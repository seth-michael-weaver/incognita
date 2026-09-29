#!/usr/bin/env python3
"""WP-11 CLI: evaluated libraries → ``staging/evaluated/`` (grid values, ladders, covariances).

Outputs per library ``<key>`` (endfb81, jeff33, jendl5, tendl2025, cendl32):

* ``staging/evaluated/parts/<key>/xs-NNNNN.parquet``   batches of ``EvaluatedXS`` rows
* ``staging/evaluated/parts/<key>/res-NNNNN.parquet``  resonance-parameter rows
* ``staging/evaluated/<key>_cov.zarr``      ``<nuclide_id>/mt<MT>/{energy_bounds_ev, rel_cov}``
* ``staging/evaluated/<key>_done.jsonl``                per-material status (resume log)
* ``staging/evaluated/<key>.parquet``, ``<key>_resonances.parquet``   merged (finalize)
* ``staging/evaluated/summary.json``                    summary step
* ``features/library_spread.parquet``, ``features/library_tendl_like.parquet``  ``--spread`` step

Resumable: materials whose done-line covers the requested MTs and temperatures
are skipped; ``--retry-errors`` re-runs failures.

Examples::

    uv run python -m data.ingest.build_evaluated --library endfb81 --subset capture --workers 3
    uv run python -m data.ingest.build_evaluated --library all --subset all --workers 3
    uv run python -m data.ingest.build_evaluated --summary-only
    uv run python -m data.ingest.build_evaluated --summary-only --spread
    # -> features/library_spread.parquet
"""

from __future__ import annotations

import argparse
import json
import multiprocessing as mp
import re
import sys
import time
from collections import Counter, defaultdict
from collections.abc import Iterable
from pathlib import Path
from typing import Any

import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq

from data.ingest.endf import (
    ALL_MTS,
    CAPTURE_MTS,
    CAPTURE_Z_RANGE,
    COV_MTS,
    LIBRARIES,
    STAGING,
    LibrarySpec,
    MaterialResult,
    MaterialSource,
    MaterialTask,
    iter_done,
    ladder_stats,
    list_materials,
    process_material,
    read_header,
    result_summary_row,
    result_to_records,
)
from data.schema.evaluated import EvaluatedXS
from physics.grid import ENERGY_GRID_EV, GRID_ID, nearest_index

PARTS = STAGING / "parts"
LIBRARY_ORDER = ("endfb81", "jeff33", "cendl32", "tendl2025", "jendl5")

RESONANCE_SCHEMA = pa.schema(
    [
        pa.field("library", pa.string(), nullable=False),
        pa.field("nuclide_id", pa.string(), nullable=False),
        pa.field("Z", pa.int16(), nullable=False),
        pa.field("N", pa.int16(), nullable=False),
        pa.field("iso", pa.int8(), nullable=False),
        pa.field("isotope_index", pa.int16()),
        pa.field("zai", pa.float64()),
        pa.field("abundance", pa.float64()),
        pa.field("range_index", pa.int16()),
        pa.field("lru", pa.int8()),
        pa.field("lrf", pa.int8()),
        pa.field("formalism", pa.string()),
        pa.field("el_ev", pa.float64()),
        pa.field("eh_ev", pa.float64()),
        pa.field("spi", pa.float64()),
        pa.field("ap", pa.float64()),
        pa.field("lssf", pa.int8()),
        pa.field("nro", pa.int8()),
        pa.field("naps", pa.int8()),
        pa.field("group_index", pa.int16()),
        pa.field("l", pa.int16()),
        pa.field("j", pa.float64()),
        pa.field("awri", pa.float64()),
        pa.field("n_res", pa.int32()),
        pa.field("param_names", pa.list_(pa.string())),
        pa.field("param_values", pa.list_(pa.list_(pa.float64()))),
        pa.field("param_shape", pa.list_(pa.list_(pa.int32()))),
    ]
)

_Z_IN_NAME = (
    re.compile(r"^n-(\d{3})_"),  # ENDF/B: n-079_Au_197.endf
    re.compile(r"^(\d{1,3})-[A-Za-z]"),  # JEFF: 79-Au-197g.jeff33
    re.compile(r"^n_(\d{3})-"),  # TENDL: n_079-Au-197_7925.zip
)


def quick_z(src: MaterialSource) -> int | None:
    """Z from the file name if it carries one, else from the material header."""
    for pat in _Z_IN_NAME:
        m = pat.match(src.name)
        if m:
            return int(m.group(1))
    try:
        if src.zip_member is None:
            with open(src.path, "rb") as fh:
                head = fh.read(1024).decode("latin-1")
        else:
            head = src.read_text()[:1024]
        return read_header(head + "\n" * 8).Z
    except Exception:
        return None


def _covers(done: dict[str, Any], mts: Iterable[int], temps: Iterable[float]) -> bool:
    done_temps = done.get("temperatures_requested", done.get("temperatures", [0.0]))
    return (
        done.get("status") == "ok"
        and set(mts) <= set(done.get("mts_requested", done.get("mts", [])))
        and set(float(t) for t in temps) <= set(float(t) for t in done_temps)
    )


def _write_cov(zarr_path: Path, result: MaterialResult) -> None:
    if not result.covariances:
        return
    import zarr

    root = zarr.open_group(zarr_path, mode="a")
    for mt, (bounds, cov, meta) in result.covariances.items():
        g = root.require_group(f"{result.nuclide_id}/mt{mt}")
        g.create_array(
            "energy_bounds_ev", data=np.asarray(bounds, dtype=np.float64), overwrite=True
        )
        g.create_array("rel_cov", data=np.asarray(cov, dtype=np.float64), overwrite=True)
        g.attrs.update(
            {
                "library": result.library,
                "nuclide_id": result.nuclide_id,
                "mt": int(mt),
                "Z": result.Z,
                "N": result.N,
                "iso": result.iso,
                "n_bins": int(meta.get("n_bins", 0)),
                "lb_types": [int(x) for x in meta.get("lb", [])],
                "skipped": list(meta.get("skipped", [])),
                "nc_subsections": int(meta.get("nc", 0)),
                "source": "MF33 NI-type sub-subsections (relative)",
            }
        )


def _next_part_index(part_dir: Path) -> int:
    existing = sorted(part_dir.glob("xs-*.parquet"))
    return int(existing[-1].stem.split("-")[1]) + 1 if existing else 0


class BatchWriter:
    """Accumulates results and flushes them as parquet parts + done-lines + zarr blocks."""

    def __init__(
        self, spec: LibrarySpec, mts: tuple[int, ...], temps: tuple[float, ...], batch_size: int
    ):
        self.spec, self.mts, self.temps, self.batch_size = spec, mts, temps, batch_size
        self.part_dir = PARTS / spec.key
        self.part_dir.mkdir(parents=True, exist_ok=True)
        self.done_path = STAGING / f"{spec.key}_done.jsonl"
        self.zarr_path = STAGING / f"{spec.key}_cov.zarr"
        self.index = _next_part_index(self.part_dir)
        self.records: list[EvaluatedXS] = []
        self.res_rows: list[dict[str, Any]] = []
        self.done_rows: list[dict[str, Any]] = []
        self.pending: list[MaterialResult] = []

    def add(self, result: MaterialResult) -> None:
        self.records.extend(result_to_records(result, self.spec))
        self.res_rows.extend(result.resonance_rows)
        row = result_summary_row(result)
        row["mts_requested"] = list(self.mts)
        row["temperatures_requested"] = [0.0, *self.temps]
        self.done_rows.append(row)
        self.pending.append(result)
        if len(self.pending) >= self.batch_size:
            self.flush()

    def flush(self) -> None:
        if not self.pending:
            return
        if self.records:
            pq.write_table(
                EvaluatedXS.to_arrow(self.records), self.part_dir / f"xs-{self.index:05d}.parquet",
                compression="zstd", row_group_size=200,
            )  # fmt: skip
        if self.res_rows:
            pq.write_table(
                pa.Table.from_pylist(self.res_rows, schema=RESONANCE_SCHEMA),
                self.part_dir / f"res-{self.index:05d}.parquet", compression="zstd",
            )  # fmt: skip
        for r in self.pending:
            _write_cov(self.zarr_path, r)
        with open(self.done_path, "a") as fh:
            for row in self.done_rows:
                fh.write(json.dumps(row) + "\n")
        self.index += 1
        self.records, self.res_rows, self.done_rows, self.pending = [], [], [], []


def select_materials(
    spec: LibrarySpec, *, zmin: int, zmax: int, mts: tuple[int, ...], temps: tuple[float, ...],
    retry_errors: bool, limit: int | None, name_filter: str | None,
) -> tuple[list[MaterialSource], int]:  # fmt: skip
    """Materials to process (after Z filter and resume log). Returns (todo, n_skipped_done)."""
    sources = list_materials(spec.key)
    if name_filter:
        pat = re.compile(name_filter)
        sources = [s for s in sources if pat.search(s.name)]
    done = {d["name"]: d for d in iter_done(STAGING / f"{spec.key}_done.jsonl")}
    todo, n_done = [], 0
    for s in sources:
        z = quick_z(s)
        if z is not None and not (zmin <= z <= zmax):
            continue
        d = done.get(s.name)
        if d is not None:
            failed_no_retry = d["status"] == "error" and not retry_errors
            if _covers(d, mts, temps) or d["status"] == "skip" or failed_no_retry:
                n_done += 1
                continue
        todo.append(s)
    todo.sort(key=lambda s: (quick_z(s) or 0, s.name))
    if limit is not None:
        todo = todo[:limit]
    return todo, n_done


def run_library(
    spec: LibrarySpec, *, subset: str, workers: int, temperatures: tuple[float, ...], error: float,
    zmin: int | None, zmax: int | None, mts: tuple[int, ...] | None, limit: int | None,
    retry_errors: bool, batch_size: int, name_filter: str | None, log=print,
) -> dict[str, Any]:  # fmt: skip
    t0 = time.time()
    if mts is None:
        mts = CAPTURE_MTS if subset == "capture" else ALL_MTS
    if zmin is None:
        zmin = CAPTURE_Z_RANGE[0] if subset == "capture" else 0
    if zmax is None:
        zmax = CAPTURE_Z_RANGE[1] if subset == "capture" else 999
    STAGING.mkdir(parents=True, exist_ok=True)
    todo, n_done = select_materials(
        spec, zmin=zmin, zmax=zmax, mts=mts, temps=temperatures, retry_errors=retry_errors,
        limit=limit, name_filter=name_filter,
    )  # fmt: skip
    log(
        f"[{spec.key}] {len(todo)} materials to process ({n_done} already done), "
        f"Z={zmin}-{zmax}, MTs={list(mts)}, T={[0.0, *temperatures]}, workers={workers}"
    )
    writer = BatchWriter(spec, mts, temperatures, batch_size)
    tasks = [
        MaterialTask(s, mts=mts, cov_mts=COV_MTS, temperatures=temperatures, error=error)
        for s in todo
    ]
    counts: Counter[str] = Counter()
    peak = 0.0
    n = 0
    try:
        if workers <= 1:
            results = map(process_material, tasks)
        else:
            ctx = mp.get_context("fork")
            pool = ctx.Pool(processes=workers, maxtasksperchild=25)
            results = pool.imap_unordered(process_material, tasks, chunksize=1)
        for r in results:
            n += 1
            counts[r.status] += 1
            peak = max(peak, r.peak_rss_mb)
            writer.add(r)
            if r.status != "ok":
                log(f"  [{spec.key}] {r.name}: {r.status} {r.message[:160]}")
            if n % 25 == 0 or n == len(tasks):
                el = time.time() - t0
                log(
                    f"  [{spec.key}] {n}/{len(tasks)} done in {el:.0f}s "
                    f"({el / max(n, 1):.1f}s/material, peak worker RSS {peak:.0f} MB) "
                    f"{dict(counts)}"
                )
    finally:
        writer.flush()
        if workers > 1:
            pool.close()
            pool.join()
    return {
        "library": spec.key,
        "processed": n,
        "already_done": n_done,
        "counts": dict(counts),
        "seconds": round(time.time() - t0, 1),
        "peak_worker_rss_mb": round(peak, 1),
    }


# --------------------------------------------------------------------------- #
# Finalize: merge parts (latest part wins per key)
# --------------------------------------------------------------------------- #
def finalize_library(spec: LibrarySpec, log=print) -> dict[str, int]:
    part_dir = PARTS / spec.key
    out_xs = STAGING / f"{spec.key}.parquet"
    out_res = STAGING / f"{spec.key}_resonances.parquet"
    stats = {"xs_rows": 0, "resonance_rows": 0}
    xs_parts = sorted(part_dir.glob("xs-*.parquet"), reverse=True)
    if xs_parts:
        seen: set[tuple[str, int, float]] = set()
        writer = None
        tmp = out_xs.with_suffix(".parquet.tmp")
        try:
            for p in xs_parts:
                t = pq.read_table(p)
                cols = (t["nuclide_id"], t["mt"], t["temperature_k"])
                keys = list(zip(*(c.to_pylist() for c in cols), strict=True))
                keep = [i for i, k in enumerate(keys) if k not in seen]
                seen.update(keys[i] for i in keep)
                if not keep:
                    continue
                t = t.take(pa.array(keep, pa.int64()))
                if writer is None:
                    writer = pq.ParquetWriter(tmp, t.schema, compression="zstd")
                writer.write_table(t, row_group_size=200)
                stats["xs_rows"] += t.num_rows
        finally:
            if writer is not None:
                writer.close()
        if tmp.exists():
            tmp.replace(out_xs)
    res_parts = sorted(part_dir.glob("res-*.parquet"), reverse=True)
    if res_parts:
        seen_n: set[str] = set()
        writer = None
        tmp = out_res.with_suffix(".parquet.tmp")
        try:
            for p in res_parts:
                t = pq.read_table(p)
                ids = t["nuclide_id"].to_pylist()
                new = sorted(set(ids) - seen_n)
                if not new:
                    continue
                mask = pa.array([i in set(new) for i in ids])
                t = t.filter(mask)
                seen_n.update(new)
                if writer is None:
                    writer = pq.ParquetWriter(tmp, t.schema, compression="zstd")
                writer.write_table(t)
                stats["resonance_rows"] += t.num_rows
        finally:
            if writer is not None:
                writer.close()
        if tmp.exists():
            tmp.replace(out_res)
    log(f"[{spec.key}] finalized: {stats}")
    return stats


# --------------------------------------------------------------------------- #
# s-wave statistics per nuclide (plan step 2): staging/evaluated/resonance_stats.parquet
# --------------------------------------------------------------------------- #
RESONANCE_STATS_SCHEMA = pa.schema(
    [
        pa.field("library", pa.string(), nullable=False),
        pa.field("nuclide_id", pa.string(), nullable=False),
        pa.field("Z", pa.int16(), nullable=False),
        pa.field("N", pa.int16(), nullable=False),
        pa.field("iso", pa.int8(), nullable=False),
        pa.field("formalisms", pa.list_(pa.string())),
        pa.field("target_spin", pa.float64()),
        pa.field("rrr_upper_ev", pa.float64()),
        pa.field("urr_upper_ev", pa.float64()),
        pa.field("n_res_rrr_total", pa.int32()),
        pa.field("n_res_l0", pa.int32()),
        pa.field("e_first_l0_ev", pa.float64()),
        pa.field("e_last_l0_ev", pa.float64()),
        pa.field("d0_ev", pa.float64()),  # (E_last - E_first) / (n - 1), s-wave, 0 < ER <= EH
        pa.field("s0", pa.float64()),  # sum(g Gn0) / (n D0), Gn0 = Gn / sqrt(ER[eV])
        pa.field("g_gn0_mean_ev", pa.float64()),
        pa.field("gamma_gamma_ev", pa.float64()),  # mean over s-wave resonances with Gg > 0
        pa.field("gamma_gamma_median_ev", pa.float64()),
        pa.field("n_gamma_gamma", pa.int32()),
        pa.field("d0_urr_ev", pa.float64()),  # URR l=0 at the lowest tabulated energy
        pa.field("s0_urr", pa.float64()),
        pa.field("gamma_gamma_urr_ev", pa.float64()),
        pa.field("urr_lower_ev", pa.float64()),
        pa.field("rml_pair_assumed", pa.bool_()),
        pa.field("ripl_d0_ev", pa.float64()),  # RIPL-4 (keyed by the compound nucleus Z, N+1)
        pa.field("ripl_d0_sigma_ev", pa.float64()),
        pa.field("ripl_s0", pa.float64()),
        pa.field("ripl_gamma_gamma_ev", pa.float64()),
        pa.field("ripl_source", pa.string()),
    ]
)
RESONANCE_STATS_PATH = STAGING / "resonance_stats.parquet"


def _target_spins() -> dict[str, float]:
    path = STAGING.parent / "nuclides.parquet"
    if not path.exists():
        return {}
    t = pq.read_table(path, columns=["nuclide_id", "spin"])
    return {
        n: float(sp)
        for n, sp in zip(t["nuclide_id"].to_pylist(), t["spin"].to_pylist(), strict=True)
        if sp is not None
    }


def _ripl_resonance_params() -> dict[str, dict[str, Any]]:
    """RIPL-4 D0/S0/Γγ from ``staging/structure_params.parquet`` keyed by *target* nuclide_id."""
    from data.schema.keys import nuclide_id as make_nuclide_id

    path = STAGING.parent / "structure_params.parquet"
    if not path.exists():
        return {}
    t = pq.read_table(path, columns=["Z", "N", "iso", "d0_ev", "s0", "gamma_gamma_mev"])
    out: dict[str, dict[str, Any]] = {}
    for row in t.to_pylist():
        if row["iso"] or row["d0_ev"] is None or row["N"] < 1:
            continue
        d0, s0, gg = row["d0_ev"], row["s0"] or {}, row["gamma_gamma_mev"] or {}
        out[make_nuclide_id(row["Z"], row["N"] - 1, 0)] = {
            "ripl_d0_ev": d0.get("value"),
            "ripl_d0_sigma_ev": d0.get("sigma"),
            "ripl_s0": s0.get("value"),
            "ripl_gamma_gamma_ev": None if gg.get("value") is None else gg["value"] * 1e-3,
            "ripl_source": d0.get("source"),
        }
    return out


def resonance_stats(libs: list[LibrarySpec], log=print) -> dict[str, Any]:
    """One row per (library, nuclide) with the s-wave D0 / S0 / <Γγ> from the staged
    ladders (:func:`ladder_stats`) next to the RIPL-4 values → ``resonance_stats.parquet``."""
    spins = _target_spins()
    ripl = _ripl_resonance_params()
    stats: dict[str, Any] = {"rows": 0, "per_library": {}}
    tables = []
    for spec in libs:
        path = STAGING / f"{spec.key}_resonances.parquet"
        if not path.exists():
            continue
        by_nuc: dict[str, list[dict[str, Any]]] = defaultdict(list)
        pf = pq.ParquetFile(path)
        for batch in pf.iter_batches(batch_size=2000):
            for row in batch.to_pylist():
                by_nuc[row["nuclide_id"]].append(row)
        rows = []
        for nid, ladder in by_nuc.items():
            first = ladder[0]
            st = ladder_stats(ladder, spins.get(nid))
            rr = [r["eh_ev"] for r in ladder if r["lru"] == 1]
            ur = [r["eh_ev"] for r in ladder if r["lru"] == 2]
            rows.append({
                "library": spec.name, "nuclide_id": nid, "Z": first["Z"], "N": first["N"],
                "iso": first["iso"], "target_spin": spins.get(nid),
                "rrr_upper_ev": max(rr) if rr else None, "urr_upper_ev": max(ur) if ur else None,
                **st, **ripl.get(nid, {}),
            })  # fmt: skip
        if not rows:
            continue
        t = pa.Table.from_pylist(rows, schema=RESONANCE_STATS_SCHEMA)
        tables.append(t)
        d0 = np.array([r["d0_ev"] for r in rows], dtype=np.float64)
        rd0 = np.array(
            [r.get("ripl_d0_ev") or np.nan for r in rows], dtype=np.float64
        )
        both = np.isfinite(d0) & np.isfinite(rd0) & (rd0 > 0)
        ratio = np.abs(np.log10(d0[both] / rd0[both])) if both.any() else np.array([])
        stats["per_library"][spec.key] = {
            "nuclides": len(rows),
            "with_d0": int(np.isfinite(d0).sum()),
            "with_ripl_d0": int(both.sum()),
            "median_abs_log10_d0_ratio_vs_ripl": float(np.median(ratio)) if ratio.size else None,
            "within_factor2_of_ripl": float(np.mean(ratio < np.log10(2))) if ratio.size else None,
        }
        stats["rows"] += len(rows)
        log(f"[resonance-stats] {spec.key}: {stats['per_library'][spec.key]}")
    if tables:
        pq.write_table(pa.concat_tables(tables), RESONANCE_STATS_PATH, compression="zstd")
        log(f"[resonance-stats] wrote {RESONANCE_STATS_PATH} ({stats['rows']} rows)")
    (STAGING / "resonance_stats_summary.json").write_text(json.dumps(stats, indent=2))
    return stats


# --------------------------------------------------------------------------- #
# Library spread feature (plan step 4/5): features/library_spread.parquet
# --------------------------------------------------------------------------- #
FEATURES = STAGING.parents[1] / "features"
SPREAD_TMP = STAGING / "_spread_tmp"
SPREAD_MTS: tuple[int, ...] = (1, 2, 4, 16, 17, 18, 102, 103, 107)  # blueprint §2.2 Tier 3
FAST_MASK = ENERGY_GRID_EV >= 1.0e5


def _shard_library(spec: LibrarySpec, mts: tuple[int, ...], log=print) -> dict[int, Path]:
    """One streaming pass over ``<lib>.parquet``: per MT, ``log10(xs)`` (float32, NaN where
    xs <= 0) for every nuclide at 0 K → ``_spread_tmp/<lib>_mt<MT>.npz``. Never holds the
    whole library: at most one MT-set worth of one library (TENDL: ~300 MB) is in memory."""
    path = STAGING / f"{spec.key}.parquet"
    out: dict[int, Path] = {}
    if not path.exists():
        return out
    SPREAD_TMP.mkdir(parents=True, exist_ok=True)
    ids: dict[int, list[str]] = defaultdict(list)
    vals: dict[int, list[np.ndarray]] = defaultdict(list)
    meta: dict[str, tuple[int, int, int]] = {}
    pf = pq.ParquetFile(path)
    cols = ["nuclide_id", "Z", "N", "iso", "mt", "temperature_k", "values_b"]
    want = set(mts)
    for batch in pf.iter_batches(batch_size=200, columns=cols):
        mt_arr = batch["mt"].to_numpy()
        temps = batch["temperature_k"].to_numpy()
        sel = np.flatnonzero((temps == 0.0) & np.isin(mt_arr, list(want)))
        if sel.size == 0:
            continue
        nid = batch["nuclide_id"].to_pylist()
        zz, nn, ii = (batch[c].to_numpy() for c in ("Z", "N", "iso"))
        values = batch["values_b"]
        for i in sel:
            i = int(i)
            arr = np.asarray(values[i].values.to_numpy(zero_copy_only=False), dtype=np.float64)
            with np.errstate(divide="ignore"):
                lg = np.where(arr > 0, np.log10(np.where(arr > 0, arr, 1.0)), np.nan)
            ids[int(mt_arr[i])].append(nid[i])
            vals[int(mt_arr[i])].append(lg.astype(np.float32))
            meta[nid[i]] = (int(zz[i]), int(nn[i]), int(ii[i]))
    for mt in sorted(vals):
        p = SPREAD_TMP / f"{spec.key}_mt{mt}.npz"
        np.savez(p, ids=np.array(ids[mt]), log10=np.stack(vals[mt]),
                 z=np.array([meta[n][0] for n in ids[mt]], dtype=np.int16),
                 n=np.array([meta[n][1] for n in ids[mt]], dtype=np.int16),
                 iso=np.array([meta[n][2] for n in ids[mt]], dtype=np.int8))  # fmt: skip
        out[mt] = p
    n_rec = sum(len(v) for v in vals.values())
    log(f"[spread] {spec.key}: sharded {n_rec} records over {len(vals)} MTs")
    return out


SPREAD_SCHEMA = pa.schema(
    [
        pa.field("nuclide_id", pa.string(), nullable=False),
        pa.field("Z", pa.int16(), nullable=False),
        pa.field("N", pa.int16(), nullable=False),
        pa.field("iso", pa.int8(), nullable=False),
        pa.field("mt", pa.int16(), nullable=False),
        pa.field("grid_id", pa.string(), nullable=False),
        pa.field("libraries", pa.list_(pa.string())),
        pa.field("n_libraries", pa.int8()),
        pa.field("n_libraries_at_e", pa.list_(pa.int8())),  # libraries with xs>0 at each grid point
        # max-min log10(xs) over libraries; NaN where fewer than 2 libraries
        pa.field("log10_spread", pa.list_(pa.float32())),
        pa.field("mean_log10_xs_b", pa.list_(pa.float32())),  # mean log10(xs) over libraries
        pa.field("spread_thermal", pa.float32()),
        pa.field("spread_30kev", pa.float32()),
        pa.field("spread_1mev", pa.float32()),
        pa.field("median_spread_fast", pa.float32()),  # median over E >= 100 keV
        pa.field("max_spread", pa.float32()),
    ]
)
TENDL_LIKE_SCHEMA = pa.schema(
    [
        pa.field("nuclide_id", pa.string(), nullable=False),
        pa.field("mt", pa.int16(), nullable=False),
        pa.field("library", pa.string(), nullable=False),
        pa.field("median_rel_dev_vs_tendl", pa.float32()),  # median |xs/xs_TENDL - 1|, E >= 100 keV
        pa.field("n_points_compared", pa.int16()),
        pa.field("tendl_like", pa.bool_()),  # < 1 %: evaluation is TENDL systematics (§6.2)
    ]
)


def _list_col(rows: list[np.ndarray], typ: pa.DataType) -> pa.Array:
    if not rows:
        return pa.array([], pa.list_(typ))
    flat = np.concatenate(rows)
    offsets = np.zeros(len(rows) + 1, dtype=np.int32)
    offsets[1:] = np.cumsum([r.size for r in rows])
    return pa.ListArray.from_arrays(pa.array(offsets), pa.array(flat, typ))


def library_spread(
    libs: list[LibrarySpec], mts: tuple[int, ...] = SPREAD_MTS, log=print
) -> dict[str, Any]:
    """Inter-library spread per (nuclide, MT, grid energy) + TENDL-likeness per library.

    Writes ``features/library_spread.parquet`` (one row per nuclide and MT with 3000-long
    arrays) and ``features/library_tendl_like.parquet``; returns summary quantiles.
    """
    i_th, i30, i1m = (int(nearest_index(e)) for e in (0.0253, 3.0e4, 1.0e6))
    shards = {spec: _shard_library(spec, mts, log) for spec in libs}
    shards = {k: v for k, v in shards.items() if v}
    if not shards:
        return {}
    FEATURES.mkdir(parents=True, exist_ok=True)
    tmp_sp = FEATURES / "library_spread.parquet.tmp"
    tmp_tl = FEATURES / "library_tendl_like.parquet.tmp"
    w_sp = pq.ParquetWriter(tmp_sp, SPREAD_SCHEMA, compression="zstd")
    w_tl = pq.ParquetWriter(tmp_tl, TENDL_LIKE_SCHEMA, compression="zstd")
    stats: dict[str, Any] = {"rows": 0, "tendl_like_rows": 0, "per_mt": {}}
    all_s30: list[np.ndarray] = []
    all_s1m: list[np.ndarray] = []
    tl_counts: dict[str, Counter[str]] = defaultdict(Counter)
    try:
        for mt in mts:
            per_lib = {}
            for spec, paths in shards.items():
                if mt in paths:
                    z = np.load(paths[mt], allow_pickle=False)
                    per_lib[spec.name] = (list(z["ids"]), z["log10"], z["z"], z["n"], z["iso"])
            if not per_lib:
                continue
            union = sorted(set().union(*(set(v[0]) for v in per_lib.values())))
            pos = {nid: k for k, nid in enumerate(union)}
            names = sorted(per_lib)
            cube = np.full((len(names), len(union), ENERGY_GRID_EV.size), np.nan, dtype=np.float32)
            meta: dict[str, tuple[int, int, int]] = {}
            for li, name in enumerate(names):
                ids, lg, zz, nn, ii = per_lib[name]
                idx = np.array([pos[n] for n in ids])
                cube[li, idx] = lg
                for n, a, b, c in zip(ids, zz, nn, ii, strict=True):
                    meta[n] = (int(a), int(b), int(c))
            del per_lib
            finite = np.isfinite(cube)
            n_at_e = finite.sum(axis=0).astype(np.int8)
            with np.errstate(all="ignore"):
                mx, mn = np.nanmax(cube, axis=0), np.nanmin(cube, axis=0)
                mean = np.nanmean(cube, axis=0)
            spread = np.where(n_at_e >= 2, mx - mn, np.nan).astype(np.float32)
            present = finite.any(axis=2)  # [lib, nuclide]
            lib_lists = [
                [names[li] for li in np.flatnonzero(present[:, k])] for k in range(len(union))
            ]
            with np.errstate(all="ignore"):
                fast = spread[:, FAST_MASK]
                med_fast = np.nanmedian(fast, axis=1)
                mx_sp = np.nanmax(spread, axis=1)
            rows = pa.table({
                "nuclide_id": pa.array(union, pa.string()),
                "Z": pa.array([meta[n][0] for n in union], pa.int16()),
                "N": pa.array([meta[n][1] for n in union], pa.int16()),
                "iso": pa.array([meta[n][2] for n in union], pa.int8()),
                "mt": pa.array([mt] * len(union), pa.int16()),
                "grid_id": pa.array([GRID_ID] * len(union), pa.string()),
                "libraries": pa.array(lib_lists, pa.list_(pa.string())),
                "n_libraries": pa.array(present.sum(axis=0).astype(np.int8), pa.int8()),
                "n_libraries_at_e": _list_col(list(n_at_e), pa.int8()),
                "log10_spread": _list_col(list(spread), pa.float32()),
                "mean_log10_xs_b": _list_col(list(mean.astype(np.float32)), pa.float32()),
                "spread_thermal": pa.array(spread[:, i_th], pa.float32()),
                "spread_30kev": pa.array(spread[:, i30], pa.float32()),
                "spread_1mev": pa.array(spread[:, i1m], pa.float32()),
                "median_spread_fast": pa.array(med_fast.astype(np.float32), pa.float32()),
                "max_spread": pa.array(mx_sp.astype(np.float32), pa.float32()),
            }, schema=SPREAD_SCHEMA)  # fmt: skip
            w_sp.write_table(rows, row_group_size=500)
            stats["rows"] += rows.num_rows
            all_s30.append(spread[:, i30][np.isfinite(spread[:, i30])])
            all_s1m.append(spread[:, i1m][np.isfinite(spread[:, i1m])])
            multi = int((present.sum(axis=0) >= 2).sum())
            stats["per_mt"][str(mt)] = {"nuclides": len(union), "in_2plus_libraries": multi}
            # TENDL-likeness: median relative deviation vs TENDL over the fast region.
            if "TENDL-2025" in names:
                ti = names.index("TENDL-2025")
                tl_rows: dict[str, list[Any]] = defaultdict(list)
                for li, name in enumerate(names):
                    if li == ti:
                        continue
                    both = finite[li][:, FAST_MASK] & finite[ti][:, FAST_MASK]
                    with np.errstate(all="ignore"):
                        diff = cube[li][:, FAST_MASK] - cube[ti][:, FAST_MASK]
                        rel = np.abs(10.0**diff - 1.0)
                    rel = np.where(both, rel, np.nan)
                    npts = both.sum(axis=1)
                    with np.errstate(all="ignore"):
                        dev = np.nanmedian(rel, axis=1)
                    for k in np.flatnonzero(npts >= 10):
                        d = float(dev[k])
                        tl_rows["nuclide_id"].append(union[k])
                        tl_rows["mt"].append(mt)
                        tl_rows["library"].append(name)
                        tl_rows["median_rel_dev_vs_tendl"].append(d)
                        tl_rows["n_points_compared"].append(int(npts[k]))
                        tl_rows["tendl_like"].append(bool(d < 0.01))
                        tl_counts[name][str(bool(d < 0.01))] += 1
                if tl_rows:
                    t = pa.Table.from_pydict(dict(tl_rows), schema=TENDL_LIKE_SCHEMA)
                    w_tl.write_table(t)
                    stats["tendl_like_rows"] += t.num_rows
            del cube, finite
            log(f"[spread] MT{mt}: {len(union)} nuclides, {multi} in 2+ libraries")
    finally:
        w_sp.close()
        w_tl.close()
    tmp_sp.replace(FEATURES / "library_spread.parquet")
    tmp_tl.replace(FEATURES / "library_tendl_like.parquet")
    s30 = np.concatenate(all_s30) if all_s30 else np.array([])
    s1m = np.concatenate(all_s1m) if all_s1m else np.array([])
    stats["log10_spread_30kev_quantiles"] = _quantiles(s30)
    stats["log10_spread_1mev_quantiles"] = _quantiles(s1m)
    stats["tendl_like_by_library"] = {k: dict(v) for k, v in tl_counts.items()}
    stats["libraries"] = [s.name for s in shards]
    stats["mts"] = list(mts)
    stats["generated"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    (STAGING / "library_spread_summary.json").write_text(json.dumps(stats, indent=2))
    for p in SPREAD_TMP.glob("*.npz"):
        p.unlink()
    log(f"[spread] wrote {FEATURES / 'library_spread.parquet'} ({stats['rows']} rows)")
    return stats


def _quantiles(x: np.ndarray) -> dict[str, float]:
    qs = ("0.5", "0.9", "0.99")
    return {q: float(np.quantile(x, float(q))) for q in qs} if x.size else {}


def summarize(libs: list[LibrarySpec], log=print) -> dict[str, Any]:
    summary: dict[str, Any] = {"libraries": {}, "generated": time.strftime("%Y-%m-%dT%H:%M:%S")}
    for spec in libs:
        done = list(iter_done(STAGING / f"{spec.key}_done.jsonl"))
        if not done:
            continue
        ok = [d for d in done if d["status"] == "ok"]
        mt_counts: Counter[int] = Counter(mt for d in ok for mt in d["mts"])
        form: Counter[str] = Counter(f for d in ok for f in d.get("formalisms", []))
        nuclides = {d["nuclide_id"] for d in ok}
        zlo, zhi = CAPTURE_Z_RANGE
        capture_z = [d for d in ok if d["Z"] is not None and zlo <= d["Z"] <= zhi]
        lib = {
            "name": spec.name,
            "materials": {"ok": len(ok), "skip": sum(d["status"] == "skip" for d in done),
                          "error": sum(d["status"] == "error" for d in done)},
            "nuclides": len(nuclides),
            "nuclides_Z26_92": len({d["nuclide_id"] for d in capture_z}),
            "isomers": sum(1 for d in ok if d.get("iso")),
            "mts": {str(k): v for k, v in sorted(mt_counts.items())},
            "xs_records": sum(
                len(d["mts"]) * max(len(d.get("temperatures", [0.0])), 1) for d in ok
            ),
            "temperatures": sorted({t for d in ok for t in d.get("temperatures", [0.0])}),
            "mf33_any": sum(1 for d in ok if d.get("mf33_mts")),
            "mf33_capture": sum(1 for d in ok if 102 in d.get("mf33_mts", [])),
            "cov_blocks_stored": {
                str(mt): sum(1 for d in ok if mt in d.get("cov_mts", [])) for mt in COV_MTS
            },
            "mf32": sum(1 for d in ok if d.get("mf32")),
            "with_resolved_region": sum(1 for d in ok if d.get("resolved_upper_ev")),
            "with_unresolved_region": sum(1 for d in ok if d.get("unresolved_upper_ev")),
            "lssf0": sum(1 for d in ok if d.get("lssf") == 0),
            "formalisms": dict(form),
            "resonances_total": sum(d.get("n_resonances", 0) for d in ok),
            "seconds_total": round(sum(d["seconds"] for d in done), 1),
            "seconds_max": max((d["seconds"] for d in done), default=0.0),
            "peak_worker_rss_mb": max((d.get("peak_rss_mb", 0.0) for d in done), default=0.0),
            "errors": [
                {"name": d["name"], "message": d["message"][:200]}
                for d in done
                if d["status"] == "error"
            ][:50],
        }  # fmt: skip
        summary["libraries"][spec.key] = lib
        log(
            f"[{spec.key}] {spec.name}: nuclides={lib['nuclides']} "
            f"(Z26-92: {lib['nuclides_Z26_92']}), MTs={len(mt_counts)}, "
            f"xs rows={lib['xs_records']}, MF33 capture={lib['mf33_capture']}, "
            f"LSSF=0: {lib['lssf0']}, errors={lib['materials']['error']}, "
            f"{lib['seconds_total']:.0f}s cpu, peak RSS {lib['peak_worker_rss_mb']:.0f} MB"
        )
    spread_json = STAGING / "library_spread_summary.json"
    if spread_json.exists():
        summary["library_spread"] = json.loads(spread_json.read_text())
    (STAGING / "summary.json").write_text(json.dumps(summary, indent=2))
    return summary


# --------------------------------------------------------------------------- #
def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument(
        "--library", action="append", default=None,
        help="library key (endfb81, jeff33, cendl32, tendl2025, jendl5, jeff40, fendl32, "
        "brond31, irdff2, ...) or 'all'; repeatable",
    )  # fmt: skip
    ap.add_argument("--subset", choices=("capture", "all"), default="capture")
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument(
        "--temperatures", type=float, nargs="*", default=(),
        help="BROADR temperatures (K) besides 0 K",
    )  # fmt: skip
    ap.add_argument("--error", type=float, default=1e-3, help="RECONR/BROADR tolerance")
    ap.add_argument("--zmin", type=int, default=None)
    ap.add_argument("--zmax", type=int, default=None)
    ap.add_argument("--mts", type=int, nargs="*", default=None, help="override the MT list")
    ap.add_argument(
        "--limit", type=int, default=None, help="process at most N materials per library"
    )
    ap.add_argument("--materials", default=None, help="regex on material file names")
    ap.add_argument("--retry-errors", action="store_true")
    ap.add_argument("--batch-size", type=int, default=20)
    ap.add_argument("--no-finalize", action="store_true")
    ap.add_argument("--finalize-only", action="store_true")
    ap.add_argument("--summary-only", action="store_true")
    ap.add_argument(
        "--resonance-stats", action="store_true",
        help="(re)build staging/evaluated/resonance_stats.parquet from the finalized ladders",
    )  # fmt: skip
    ap.add_argument(
        "--spread", action="store_true",
        help="(re)build features/library_spread.parquet from the finalized parquet files",
    )  # fmt: skip
    args = ap.parse_args(argv)

    keys = args.library or ["all"]
    if "all" in keys:
        keys = list(LIBRARY_ORDER)
    specs = [LIBRARIES[k] for k in keys]
    t0 = time.time()

    def log(msg: str) -> None:
        print(f"[{time.time() - t0:7.0f}s] {msg}", flush=True)

    runs = []
    if not (args.summary_only or args.finalize_only):
        for spec in specs:
            if not spec.archive.exists():
                log(f"[{spec.key}] archive missing ({spec.archive}); skipping")
                continue
            runs.append(
                run_library(
                    spec, subset=args.subset, workers=args.workers,
                    temperatures=tuple(args.temperatures), error=args.error,
                    zmin=args.zmin, zmax=args.zmax, mts=tuple(args.mts) if args.mts else None,
                    limit=args.limit, retry_errors=args.retry_errors,
                    batch_size=args.batch_size, name_filter=args.materials, log=log,
                )  # fmt: skip
            )
    finalized = False
    if not args.summary_only and not args.no_finalize:
        for spec in specs:
            if (PARTS / spec.key).exists():
                finalize_library(spec, log)
                # resonance_stats/library_spread are built from LIBRARY_ORDER only: finalizing a
                # library outside it (the archived TENDL releases) must not rewrite those tables.
                finalized = finalized or spec.key in LIBRARY_ORDER
    if args.resonance_stats or finalized:
        resonance_stats([LIBRARIES[k] for k in LIBRARY_ORDER], log=log)
    if args.spread:
        library_spread([LIBRARIES[k] for k in LIBRARY_ORDER], log=log)
    summarize([s for s in LIBRARIES.values()], log)
    for r in runs:
        log(f"run: {r}")
    log(f"total wall {time.time() - t0:.0f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
