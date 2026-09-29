"""WP-12 step 1: experiment-to-experiment scatter model (blueprint §1, §4.3, §15).

EXFOR is inconsistent by construction (§1): the same quantity measured by
different groups disagrees by more than the quoted uncertainties. Evaluators
handle this with GMA/GMAP-style fits in which each dataset carries its own
normalization and its uncertainties may be inflated (§15). This module is a
small, transparent version of that idea, fit **for every (nuclide, reaction,
branch, quantity kind) group at once** with vectorised scatter-adds.

Model (all in natural-log space of the cross section)::

    y_ib = mu_gb + b_i + e_ib                 i = dataset, b = coarse energy bin
    e_ib ~ N(0, (sigma_ib^2 + s_i^2) / r_ib)  r_ib ~ Gamma(nu_e/2, nu_e/2)     (t point noise)
    b_i  ~ N(0, tau^2 / lambda_i)             lambda_i ~ Gamma(nu_b/2, nu_b/2) (t bias prior)

* ``mu_gb`` is the consensus for group ``g`` in bin ``b``.
* ``b_i`` is the dataset's multiplicative bias (``exp(b_i)`` is its normalization
  relative to consensus). The heavy-tailed prior with scale ``tau`` (3 %) is what
  makes the fit identifiable *and* robust: datasets a few per cent off share the
  consensus, datasets 30 % off get a large ``b_i`` and stop pulling ``mu``.
* ``s_i^2`` is extra (unreported) variance per dataset, estimated by a
  DerSimonian–Laird moment step from the bias-corrected residuals.
* ``r_ib`` are the Gaussian scale-mixture (Student-t, nu_e = 4) point weights;
  the E-step sets ``r = (nu+1)/(nu + z^2)`` and ``lambda = (nu_b+1)/(nu_b + b^2/tau^2)``.

Cells, not points
-----------------
Each dataset is first reduced to one *cell* per coarse log-energy bin (10 bins
per decade): the linear mean of its points in the bin, with a propagated
relative uncertainty. Averaging in linear space before the log is essential for
high-resolution time-of-flight data whose background-subtracted points are often
negative, and it makes a 24 000-point resonance scan and a single activation
point comparable as bin averages.

Uncertainty rules (``data/ingest/exfor.py`` contract): ``stat_sigma`` is the
statistical or unsplit total, ``sys_sigma`` is ``ERR-SYS``; a cell's relative
sigma is ``sqrt(stat_rel^2 + sys_rel^2)``. If nothing is reported, the standard
error of the mean over >= 3 points is used, else the group's median reported
sigma x 1.5, else 15 %. Every sigma is floored at 1 % and capped at 100 %.

Which value block: ``renormalized`` whenever it exists (``standards_version`` is
``"IAEA Neutron Standards 2017"`` or ``"units-only"``) and its unit is barns;
``renormalized is None`` (unconvertible) datasets are skipped and flagged
``unconverted`` downstream. Upper limits (SF8 ``LIM``) are flagged ``limit`` and
never enter a consensus.

Renormalization sanity (WP-12 step 1): when the original unit is a cross section,
the Standards monitor factor ``median(renormalized / original_in_barns)`` must lie
within ``1/RENORM_MAX_FACTOR .. RENORM_MAX_FACTOR`` (the honest corrections sit in
-13 %..+26 % at the 5-95 % quantiles). Outside that band the monitor conversion is
an ingest artefact (wrong MONIT unit, wrong monitor energy), the authors' own
normalization (``original`` x unit factor) is used instead and the dataset is
flagged ``renorm_suspect``. Nothing is dropped.

Duplicates (plan step 6): sub-tables of one EXFOR *entry* in the same (group, bin)
cell share one dataset's worth of consensus weight, so seven re-analyses of one
measurement cannot outvote three independent ones (``cap_entry_weight``).
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
import time
from collections.abc import Iterator
from dataclasses import asdict, dataclass, field
from pathlib import Path

import numpy as np
import polars as pl
import pyarrow as pa
import pyarrow.parquet as pq

from data.curate.units import parse_unit

__all__ = [
    "BIN_OFFSET",
    "CELL_COLUMNS",
    "ScatterConfig",
    "ScatterFit",
    "bin_edges_ev",
    "bin_index",
    "cells_from_table",
    "dataset_key",
    "fit_scatter_model",
    "group_key",
    "iter_row_groups",
    "point_outlier_fraction",
    "quantity_kind",
    "residual_state",
    "run",
    "split_group_key",
]

REPO = Path(__file__).resolve().parents[2]
RENORM_MAX_FACTOR = 1.5  # a Standards monitor correction beyond x1.5 is an ingest artefact
BIN_OFFSET = 100  # bins are floor(10*log10 E) + 100 so they are non-negative ints
_RI_CUTOFF_BIN_EV = 0.5  # resonance-integral cutoffs 0.3-1 eV are the same quantity

CELL_COLUMNS = [
    "dataset_key",
    "group_key",
    "bin",
    "n_pts",
    "mean_b",
    "y",
    "stat_rel",
    "sys_rel",
    "sem_rel",
    "e_lo_ev",
    "e_hi_ev",
]

_MEAS_COLUMNS = [
    "entry",
    "subentry",
    "pointer",
    "target_z",
    "target_a",
    "target_id",
    "mt",
    "sf",
    "energy_ev",
    "original",
    "renormalized",
]


# ----------------------------------------------------------------------------- keys / bins


def dataset_key(entry: str, subentry: str, pointer: str | None) -> str:
    return f"{entry}/{subentry}/{pointer or ''}"


def quantity_kind(sf6: str | None, sf8: str | None) -> str | None:
    """Comparable-quantity kind from SF6/SF8. ``None`` means "never compare" (limits)."""
    sf6 = (sf6 or "").upper()
    sf8 = (sf8 or "").upper()
    if "LIM" in sf8.split("/"):
        return None
    if sf6 == "SIG":
        if sf8 == "":
            return "sig"
        if sf8 == "MXW":
            return "mxw"
        if sf8 == "SPA":
            return "spa"
        if sf8 in ("AV", "SPA/AV", "A/AV"):
            return "av"
        return "sig/" + sf8.lower()
    if sf6 == "RI":
        return "ri" if sf8 == "" else "ri/" + sf8.lower()
    return sf6.lower() + ("/" + sf8.lower() if sf8 else "")


_STATE_RE = re.compile(r"-(M\d*|G|L\d*)((?:[+/](?:M\d*|G|L\d*))*)$")


def residual_state(sf4: str | None) -> str:
    """Isomeric-state suffix of the SF4 residual (``"M"``, ``"G"``, ``"M1+M2"`` ...),
    ``""`` for the total. A partial to an isomer is a different quantity from the
    total capture cross section (177Hf(n,g)178Hf-M2 is 2.6 ub against 373 b), so it
    is part of the group key."""
    m = _STATE_RE.search((sf4 or "").strip().upper())
    return (m.group(1) + m.group(2)) if m else ""


def group_key(nuclide: str, mt: int, branch: str | None, kind: str, state: str = "") -> str:
    return f"{nuclide}|{mt}|{branch or ''}|{kind}|{state}"


def split_group_key(key: str) -> tuple[str, int, str, str, str]:
    nuc, mt, branch, kind, state = key.split("|")
    return nuc, int(mt), branch, kind, state


def nuclide_key(target_z: int, target_a: int, target_id: str | None) -> str:
    return target_id if target_id else f"Z{int(target_z):03d}NAT"


def bin_index(energy_ev: np.ndarray, bins_per_decade: int = 10) -> np.ndarray:
    """Coarse log-energy bin: ``floor(bins_per_decade * log10 E) + BIN_OFFSET``."""
    e = np.asarray(energy_ev, dtype=np.float64)
    with np.errstate(divide="ignore", invalid="ignore"):
        return (np.floor(bins_per_decade * np.log10(e)) + BIN_OFFSET).astype(np.int64)


def bin_edges_ev(b: np.ndarray | int, bins_per_decade: int = 10) -> tuple[np.ndarray, np.ndarray]:
    k = np.asarray(b, dtype=np.float64) - BIN_OFFSET
    return 10.0 ** (k / bins_per_decade), 10.0 ** ((k + 1) / bins_per_decade)


# ----------------------------------------------------------------------------- flattening


def _weighted_median(values: np.ndarray, weights: np.ndarray) -> float:
    o = np.argsort(values, kind="stable")
    cw = np.cumsum(weights[o])
    return float(values[o][np.searchsorted(cw, 0.5 * cw[-1])])


def _run_arange(lengths: np.ndarray) -> np.ndarray:
    """``[0..l0-1, 0..l1-1, ...]`` for a vector of run lengths."""
    total = int(lengths.sum())
    if total == 0:
        return np.zeros(0, dtype=np.int64)
    starts = np.repeat(np.cumsum(lengths) - lengths, lengths)
    return np.arange(total, dtype=np.int64) - starts


def _flatten_aligned(col: pa.Array, n_expected: np.ndarray) -> np.ndarray:
    """Flatten a list<double> column to one value per expected point; NaN for null lists."""
    if isinstance(col, pa.ChunkedArray):
        col = col.combine_chunks()
    total = int(n_expected.sum())
    out = np.full(total, np.nan)
    if total == 0 or len(col) == 0:
        return out
    lens = col.value_lengths().fill_null(0).to_numpy(zero_copy_only=False).astype(np.int64)
    ok = lens == n_expected
    flat = col.flatten().to_numpy(zero_copy_only=False).astype(np.float64)
    # positions of ok rows inside the flat (non-null) array and inside the output
    flat_starts = np.cumsum(lens) - lens
    out_starts = np.cumsum(n_expected) - n_expected
    src = np.repeat(flat_starts[ok], lens[ok]) + _run_arange(lens[ok])
    dst = np.repeat(out_starts[ok], lens[ok]) + _run_arange(lens[ok])
    out[dst] = flat[src]
    return out


def iter_row_groups(path: Path, columns: list[str] | None = None) -> Iterator[pa.Table]:
    pf = pq.ParquetFile(path)
    for i in range(pf.metadata.num_row_groups):
        yield pf.read_row_group(i, columns=columns)


# ----------------------------------------------------------------------------- cells


@dataclass
class TableIndex:
    """Per-measurement bookkeeping for one Arrow table (the part cells refer back to)."""

    dataset_key: np.ndarray  # str
    group_key: np.ndarray  # str or "" when not comparable
    usable: np.ndarray  # bool: renormalized in barns, mt set, kind comparable
    is_limit: np.ndarray  # bool: SF8 LIM
    unconverted: np.ndarray  # bool: renormalized is None or unit not barns
    renorm_factor: np.ndarray  # float: median(renormalized / original in barns), NaN if n/a
    renorm_suspect: np.ndarray  # bool: factor outside the plausible band -> original used
    unit_factor: np.ndarray  # float: original unit -> barns (NaN when not a cross section)


def _renorm_factors(tbl: pa.Table) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Per row: unit factor of the original block, median renormalized/original ratio
    (in barns), and whether that ratio is outside the plausible monitor band."""
    n = tbl.num_rows
    orig = tbl["original"]
    orig = orig.combine_chunks() if isinstance(orig, pa.ChunkedArray) else orig
    ren = tbl["renormalized"]
    ren = ren.combine_chunks() if isinstance(ren, pa.ChunkedArray) else ren
    o_units = orig.field("units").to_pylist()
    r_units = ren.field("units").to_pylist()
    r_ver = ren.field("standards_version").to_pylist()
    ren_valid = ren.is_valid().to_numpy(zero_copy_only=False)
    ufac = np.full(n, np.nan)
    for i, u in enumerate(o_units):
        info = parse_unit(u or "")
        if info.convertible and info.canonical == "b":
            ufac[i] = info.factor
    factor = np.full(n, np.nan)
    suspect = np.zeros(n, dtype=bool)
    ov = orig.field("values")
    rv = ren.field("values")
    o_len = ov.value_lengths().fill_null(0).to_numpy(zero_copy_only=False).astype(np.int64)
    r_len = rv.value_lengths().fill_null(0).to_numpy(zero_copy_only=False).astype(np.int64)
    o_flat = ov.flatten().to_numpy(zero_copy_only=False).astype(np.float64)
    r_flat = rv.flatten().to_numpy(zero_copy_only=False).astype(np.float64)
    o_off = np.cumsum(o_len) - o_len
    r_off = np.cumsum(r_len) - r_len
    for i in range(n):
        if (
            not ren_valid[i]
            or r_units[i] != "b"
            or not np.isfinite(ufac[i])
            or o_len[i] != r_len[i]
            or o_len[i] == 0
        ):
            continue
        if r_ver[i] != "IAEA Neutron Standards 2017":
            factor[i] = 1.0
            continue
        o = o_flat[o_off[i] : o_off[i] + o_len[i]] * ufac[i]
        r = r_flat[r_off[i] : r_off[i] + r_len[i]]
        ok = np.isfinite(o) & np.isfinite(r) & (o > 0) & (r > 0)
        if not ok.any():
            continue
        factor[i] = float(np.median(r[ok] / o[ok]))
        suspect[i] = abs(math.log(factor[i])) > math.log(RENORM_MAX_FACTOR)
    return ufac, factor, suspect


def index_table(tbl: pa.Table) -> TableIndex:
    n = tbl.num_rows
    entry = tbl["entry"].to_pylist()
    sub = tbl["subentry"].to_pylist()
    ptr = tbl["pointer"].to_pylist()
    tz = tbl["target_z"].to_numpy()
    ta = tbl["target_a"].to_numpy()
    tid = tbl["target_id"].to_pylist()
    mt = tbl["mt"].to_pylist()
    sf = tbl["sf"].combine_chunks() if isinstance(tbl["sf"], pa.ChunkedArray) else tbl["sf"]
    sf4 = sf.field("sf4").to_pylist()
    sf5 = sf.field("sf5").to_pylist()
    sf6 = sf.field("sf6").to_pylist()
    sf8 = sf.field("sf8").to_pylist()
    ren = tbl["renormalized"]
    ren = ren.combine_chunks() if isinstance(ren, pa.ChunkedArray) else ren
    ren_valid = ren.is_valid().to_numpy(zero_copy_only=False)
    units = ren.field("units").to_pylist()
    ufac, rfac, suspect = _renorm_factors(tbl)

    keys = np.empty(n, dtype=object)
    groups = np.empty(n, dtype=object)
    usable = np.zeros(n, dtype=bool)
    is_limit = np.zeros(n, dtype=bool)
    unconv = np.zeros(n, dtype=bool)
    for i in range(n):
        keys[i] = dataset_key(entry[i], sub[i], ptr[i])
        kind = quantity_kind(sf6[i], sf8[i])
        is_limit[i] = kind is None
        unconv[i] = (not ren_valid[i]) or units[i] != "b"
        if kind is None or mt[i] is None or unconv[i]:
            groups[i] = ""
            continue
        groups[i] = group_key(
            nuclide_key(tz[i], ta[i], tid[i]), int(mt[i]), sf5[i], kind, residual_state(sf4[i])
        )
        usable[i] = True
    return TableIndex(keys, groups, usable, is_limit, unconv, rfac, suspect, ufac)


def _values_for_fit(
    sub: pa.Table, idx_rows: TableIndex, rows: np.ndarray, n_pts: np.ndarray
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Flattened (values, stat, sys) in barns for the usable rows ``rows`` of ``sub``:
    the renormalized block, or the original block x unit factor where the
    renormalization is suspect."""
    ren = sub["renormalized"]
    ren = ren.combine_chunks() if isinstance(ren, pa.ChunkedArray) else ren
    v = _flatten_aligned(ren.field("values"), n_pts)
    st = _flatten_aligned(ren.field("stat_sigma"), n_pts)
    sy = _flatten_aligned(ren.field("sys_sigma"), n_pts)
    use_orig = idx_rows.renorm_suspect[rows]
    if use_orig.any():
        orig = sub["original"]
        orig = orig.combine_chunks() if isinstance(orig, pa.ChunkedArray) else orig
        fac = np.repeat(np.where(use_orig, idx_rows.unit_factor[rows], np.nan), n_pts)
        pick = np.isfinite(fac)
        v = np.where(pick, _flatten_aligned(orig.field("values"), n_pts) * fac, v)
        st = np.where(pick, _flatten_aligned(orig.field("stat_sigma"), n_pts) * fac, st)
        sy = np.where(pick, _flatten_aligned(orig.field("sys_sigma"), n_pts) * fac, sy)
    return v, st, sy


def cells_from_table(
    tbl: pa.Table, *, bins_per_decade: int = 10, index: TableIndex | None = None
) -> pl.DataFrame:
    """Reduce every usable measurement in ``tbl`` to one cell per coarse energy bin."""
    idx = index or index_table(tbl)
    rows = np.flatnonzero(idx.usable)
    if rows.size == 0:
        return pl.DataFrame(schema=_cell_schema())
    sub = tbl.take(pa.array(rows))
    e_col = sub["energy_ev"]
    e_col = e_col.combine_chunks() if isinstance(e_col, pa.ChunkedArray) else e_col
    n_pts = e_col.value_lengths().fill_null(0).to_numpy(zero_copy_only=False).astype(np.int64)
    e = _flatten_aligned(e_col, n_pts)
    v, st, sy = _values_for_fit(sub, idx, rows, n_pts)
    row = np.repeat(np.arange(rows.size), n_pts)

    keep = np.isfinite(e) & (e > 0) & np.isfinite(v)
    e, v, st, sy, row = e[keep], v[keep], st[keep], sy[keep], row[keep]
    if e.size == 0:
        return pl.DataFrame(schema=_cell_schema())

    gkeys = idx.group_key[rows]
    is_ri = np.array([g.split("|")[3] == "ri" for g in gkeys], dtype=bool)[row]
    b = bin_index(e, bins_per_decade)
    ri_same = is_ri & (e >= 0.3) & (e <= 1.0)
    b[ri_same] = bin_index(np.array([_RI_CUTOFF_BIN_EV]), bins_per_decade)[0]

    cell_code = row.astype(np.int64) * 1000 + b
    codes, inv = np.unique(cell_code, return_inverse=True)
    nc = codes.size
    cnt = np.bincount(inv, minlength=nc).astype(np.float64)
    sum_v = np.bincount(inv, v, minlength=nc)
    sum_v2 = np.bincount(inv, v * v, minlength=nc)
    st_ok = np.isfinite(st)
    sy_ok = np.isfinite(sy)
    n_st = np.bincount(inv, st_ok.astype(np.float64), minlength=nc)
    n_sy = np.bincount(inv, sy_ok.astype(np.float64), minlength=nc)
    sum_st2 = np.bincount(inv, np.where(st_ok, st * st, 0.0), minlength=nc)
    sum_sy = np.bincount(inv, np.where(sy_ok, sy, 0.0), minlength=nc)
    e_lo = np.full(nc, np.inf)
    e_hi = np.zeros(nc)
    np.minimum.at(e_lo, inv, e)
    np.maximum.at(e_hi, inv, e)

    mean = sum_v / cnt
    with np.errstate(divide="ignore", invalid="ignore"):
        stat_rel = np.where(n_st == cnt, np.sqrt(sum_st2) / (cnt * mean), np.nan)
        sys_rel = np.where(n_sy == cnt, (sum_sy / cnt) / mean, np.nan)
        var = (sum_v2 / cnt - mean * mean) * cnt / np.maximum(cnt - 1, 1)
        sem_rel = np.where(cnt >= 3, np.sqrt(np.maximum(var, 0.0) / cnt) / mean, np.nan)
    positive = mean > 0
    with np.errstate(divide="ignore", invalid="ignore"):
        y = np.where(positive, np.log(np.where(positive, mean, 1.0)), np.nan)

    cell_row = codes // 1000
    cell_bin = codes % 1000
    df = pl.DataFrame(
        {
            "dataset_key": pl.Series(idx.dataset_key[rows][cell_row].tolist(), dtype=pl.Utf8),
            "group_key": pl.Series(gkeys[cell_row].tolist(), dtype=pl.Utf8),
            "bin": cell_bin.astype(np.int32),
            "n_pts": cnt.astype(np.int32),
            "mean_b": mean,
            "y": y,
            "stat_rel": np.abs(stat_rel),
            "sys_rel": np.abs(sys_rel),
            "sem_rel": sem_rel,
            "e_lo_ev": e_lo,
            "e_hi_ev": e_hi,
        }
    )
    return df.filter(pl.col("y").is_finite())


def _cell_schema() -> dict[str, pl.DataType]:
    return {
        "dataset_key": pl.Utf8,
        "group_key": pl.Utf8,
        "bin": pl.Int32,
        "n_pts": pl.Int32,
        "mean_b": pl.Float64,
        "y": pl.Float64,
        "stat_rel": pl.Float64,
        "sys_rel": pl.Float64,
        "sem_rel": pl.Float64,
        "e_lo_ev": pl.Float64,
        "e_hi_ev": pl.Float64,
    }


# ----------------------------------------------------------------------------- the fit


@dataclass(frozen=True)
class ScatterConfig:
    bins_per_decade: int = 10
    nu_point: float = 4.0  # Student-t dof for point residuals
    nu_bias: float = 2.0  # Student-t dof for the bias prior
    tau_bias: float = 0.03  # prior scale of dataset normalization (log), 3 %
    sigma_floor: float = 0.01  # no cell claims better than 1 %
    sigma_cap: float = 1.0
    sigma_default: float = 0.15  # cells with no uncertainty information at all
    sigma_unreported_factor: float = 1.5  # x group median when sigma is unreported
    max_excess_sigma: float = 1.0
    excess_from_compared_only: bool = True  # lone cells (mu == own value) carry no information
    excess_prior_weight: float = 2.0  # pseudo-cells at s^2 = 0 shrinking the moment estimate
    n_iter: int = 300
    tol: float = 1e-4  # max change of any mu / b / s2 between iterations (log units)
    damping: float = 0.5  # relaxation of the mu/b/s2 updates; 0 = plain EM (see-saws)
    agree_z: float = 2.0  # "agrees with consensus": |z_loo| <= agree_z
    cap_entry_weight: bool = True  # sub-tables of one entry share one dataset's weight per cell


@dataclass
class ScatterFit:
    datasets: pl.DataFrame
    bins: pl.DataFrame
    cells: pl.DataFrame
    config: ScatterConfig
    n_iter_used: int = 0
    converged: bool = False
    info: dict = field(default_factory=dict)


def _cell_sigma(cells: pl.DataFrame, cfg: ScatterConfig) -> tuple[np.ndarray, np.ndarray]:
    """Relative sigma per cell and whether it came from reported uncertainties."""
    st = cells["stat_rel"].to_numpy()
    sy = cells["sys_rel"].to_numpy()
    sem = cells["sem_rel"].to_numpy()
    reported = np.isfinite(st) | np.isfinite(sy)
    sig = np.sqrt(np.where(np.isfinite(st), st * st, 0.0) + np.where(np.isfinite(sy), sy * sy, 0.0))
    sig = np.where(reported, sig, np.nan)
    # fallback 1: standard error of the mean when the cell has >= 3 points
    sig = np.where(np.isfinite(sig), sig, sem)
    # fallback 2: group median of reported sigmas x factor
    med = (
        cells.with_columns(pl.Series("_s", np.where(reported, sig, np.nan)))
        .group_by("group_key", maintain_order=True)
        .agg(pl.col("_s").median().alias("_m"))
    )
    gmed = (
        cells.select("group_key")
        .join(med, on="group_key", how="left", maintain_order="left")["_m"]
        .to_numpy()
    )
    sig = np.where(np.isfinite(sig), sig, cfg.sigma_unreported_factor * gmed)
    sig = np.where(np.isfinite(sig), sig, cfg.sigma_default)
    return np.clip(sig, cfg.sigma_floor, cfg.sigma_cap), reported


def fit_scatter_model(cells: pl.DataFrame, cfg: ScatterConfig | None = None) -> ScatterFit:
    """Fit the hierarchical scatter model to a cell table (all groups at once)."""
    cfg = cfg or ScatterConfig()
    cells = cells.filter(pl.col("y").is_finite()).sort(["group_key", "bin", "dataset_key"])
    n = cells.height
    if n == 0:
        raise ValueError("no cells to fit")

    ds_codes, ds = np.unique(cells["dataset_key"].to_numpy(), return_inverse=True)
    gb_str = (cells["group_key"] + "|" + cells["bin"].cast(pl.Utf8)).to_numpy()
    gb_codes, gb = np.unique(gb_str, return_inverse=True)
    n_ds, n_gb = ds_codes.size, gb_codes.size
    y = cells["y"].to_numpy()
    sig, reported = _cell_sigma(cells, cfg)
    sig2 = sig * sig
    n_cells_ds = np.bincount(ds, minlength=n_ds).astype(np.float64)
    # duplicates: cells of the same EXFOR entry in the same (group, bin) split one weight
    if cfg.cap_entry_weight:
        _, ent = np.unique([k.split("/")[0] for k in ds_codes], return_inverse=True)
        ge = np.unique(gb.astype(np.int64) * (ent.max() + 1) + ent[ds], return_inverse=True)[1]
        dup = np.bincount(ge)[ge].astype(np.float64)
    else:
        dup = np.ones(n)

    # init: consensus = per-bin median (robust, entry-weighted so that duplicate
    # tables of one entry cannot pick the starting point); no biases, no excess
    mu = np.zeros(n_gb)
    order = np.argsort(gb, kind="stable")
    bounds = np.flatnonzero(np.diff(gb[order])) + 1
    for seg in np.split(order, bounds):
        mu[gb[seg[0]]] = _weighted_median(y[seg], 1.0 / dup[seg])
    # init: each dataset's bias = median of its residuals from that consensus. Starting
    # from b = 0 would let the point-level t-weights swallow a 30 % normalization error
    # as an "outlier point" and the bias would never be attributed to the dataset.
    b = np.zeros(n_ds)
    res0 = y - mu[gb]
    order = np.argsort(ds, kind="stable")
    bounds = np.flatnonzero(np.diff(ds[order])) + 1
    for seg in np.split(order, bounds):
        b[ds[seg[0]]] = np.median(res0[seg])
    s2 = np.zeros(n_ds)
    lam = np.ones(n_ds)
    tau2 = cfg.tau_bias**2
    # cells that have at least one other dataset in their (group, bin): only those carry
    # information about a dataset's excess scatter (a lone cell sits on its own consensus)
    n_in_gb = np.bincount(gb, minlength=n_gb)
    informative = (n_in_gb[gb] > 1) if cfg.excess_from_compared_only else np.ones(n, dtype=bool)
    n_inf_ds = np.bincount(ds, informative.astype(np.float64), minlength=n_ds)
    converged = False
    it = 0
    mu_prev, b_prev = mu, b
    while it < cfg.n_iter:
        it += 1
        var = sig2 + s2[ds]
        e = y - mu[gb] - b[ds]
        r = (cfg.nu_point + 1.0) / (cfg.nu_point + e * e / var)
        w = r / var
        wm = w / dup
        mu_new = np.bincount(gb, wm * (y - b[ds]), minlength=n_gb) / np.bincount(
            gb, wm, minlength=n_gb
        )
        lam = (cfg.nu_bias + 1.0) / (cfg.nu_bias + b * b / tau2)
        num = np.bincount(ds, w * (y - mu_new[gb]), minlength=n_ds)
        den = np.bincount(ds, w, minlength=n_ds) + lam / tau2
        b_new = num / den
        e2 = (y - mu_new[gb] - b_new[ds]) ** 2
        s_num = np.bincount(ds, informative * r * (e2 - sig2), minlength=n_ds)
        s_den = np.bincount(ds, informative * r, minlength=n_ds) - 1.0 + cfg.excess_prior_weight
        s2_new = np.where(n_inf_ds >= 2, s_num / np.maximum(s_den, 0.5), 0.0)
        s2_new = np.clip(s2_new, 0.0, cfg.max_excess_sigma**2)
        mu_prev, b_prev = mu, b
        if cfg.damping > 0 and it > 1:
            a = 1.0 - cfg.damping
            mu_new = mu + a * (mu_new - mu)
            b_new = b + a * (b_new - b)
            s2_new = s2 + a * (s2_new - s2)
        delta = max(np.abs(mu_new - mu).max(), np.abs(b_new - b).max(), np.abs(s2_new - s2).max())
        mu, b, s2 = mu_new, b_new, s2_new
        if delta < cfg.tol:
            converged = True
            break
    last_delta = float(delta)
    # bulk convergence: the max-delta criterion is dominated by a handful of bistable
    # (mu, b) pairs in bins with 2-3 datasets; report how much of the solution still moves
    rms_delta = float(
        np.sqrt((np.sum((mu - mu_prev) ** 2) + np.sum((b - b_prev) ** 2)) / max(n_gb + n_ds, 1))
    )

    # ---- final quantities
    var = sig2 + s2[ds]
    e = y - mu[gb] - b[ds]
    r = (cfg.nu_point + 1.0) / (cfg.nu_point + e * e / var)
    w = r / var
    wm = w / dup
    lam = (cfg.nu_bias + 1.0) / (cfg.nu_bias + b * b / tau2)
    W = np.bincount(gb, wm, minlength=n_gb)
    S = np.bincount(gb, wm * (y - b[ds]), minlength=n_gb)
    n_ds_gb = np.bincount(gb, minlength=n_gb).astype(np.float64)
    n_pts_gb = np.bincount(gb, cells["n_pts"].to_numpy().astype(np.float64), minlength=n_gb)
    raw = y - mu[gb]
    chi2_bin = np.bincount(gb, r * raw * raw / var, minlength=n_gb)  # t-weighted (robust)
    birge = np.sqrt(np.where(n_ds_gb > 1, chi2_bin / np.maximum(n_ds_gb - 1, 1), 1.0))
    sigma_mu = np.sqrt(1.0 / W) * np.maximum(1.0, birge)
    spread = np.sqrt(np.bincount(gb, wm * raw * raw, minlength=n_gb) / W)

    # leave-one-dataset-out consensus per cell (closed form from the final weights)
    W_loo = W[gb] - wm
    with np.errstate(divide="ignore", invalid="ignore"):
        mu_loo = np.where(W_loo > 0, (S[gb] - wm * (y - b[ds])) / W_loo, np.nan)
        sig_mu_loo = np.where(W_loo > 0, np.sqrt(1.0 / W_loo) * np.maximum(1.0, birge[gb]), np.nan)
    compared = np.isfinite(mu_loo)
    res_loo = np.where(compared, y - mu_loo, np.nan)
    v_loo = var + np.where(compared, sig_mu_loo**2, 0.0)
    wl = np.where(compared, 1.0 / v_loo, 0.0)
    n_cmp = np.bincount(ds, compared.astype(np.float64), minlength=n_ds)
    sum_wl = np.bincount(ds, wl, minlength=n_ds)
    with np.errstate(divide="ignore", invalid="ignore"):
        bias_loo = np.bincount(ds, wl * np.nan_to_num(res_loo), minlength=n_ds) / sum_wl
        bias_loo_sigma = np.sqrt(1.0 / sum_wl)
        z_loo = bias_loo / np.sqrt(bias_loo_sigma**2 + tau2)
        chi2_raw = np.bincount(
            ds, np.nan_to_num(res_loo**2 / (sig2 + np.nan_to_num(sig_mu_loo) ** 2)), minlength=n_ds
        )
        chi2_ndf = np.where(n_cmp > 0, chi2_raw / np.maximum(n_cmp, 1), np.nan)
        shape_res = np.nan_to_num(res_loo - b[ds])
        shape_chi2 = np.bincount(
            ds, shape_res**2 / (sig2 + np.nan_to_num(sig_mu_loo) ** 2) * compared, minlength=n_ds
        )
        shape_chi2_ndf = np.where(n_cmp > 1, shape_chi2 / np.maximum(n_cmp - 1, 1), np.nan)
    n_other = np.zeros(n_ds)
    np.maximum.at(n_other, ds, n_ds_gb[gb] - 1)

    cells_out = cells.with_columns(
        pl.Series("sigma_rel", sig),
        pl.Series("sigma_reported", reported),
        pl.Series("mu", mu[gb]),
        pl.Series("sigma_mu", sigma_mu[gb]),
        pl.Series("bias", b[ds]),
        pl.Series("weight", w),
        pl.Series("t_weight", r),
        pl.Series("mu_loo", mu_loo),
        pl.Series("sigma_mu_loo", sig_mu_loo),
        pl.Series("z_loo", np.where(compared, res_loo / np.sqrt(v_loo), np.nan)),
    )

    gk = np.array([s.rsplit("|", 1)[0] for s in gb_codes], dtype=object)
    bins_arr = np.array([int(s.rsplit("|", 1)[1]) for s in gb_codes], dtype=np.int64)
    nuc, mt, branch, kind, state = zip(*[split_group_key(g) for g in gk], strict=True)
    e_lo, e_hi = bin_edges_ev(bins_arr, cfg.bins_per_decade)
    bins_out = pl.DataFrame(
        {
            "group_key": pl.Series(gk.tolist(), dtype=pl.Utf8),
            "nuclide": pl.Series(list(nuc), dtype=pl.Utf8),
            "mt": pl.Series(list(mt), dtype=pl.Int32),
            "branch": pl.Series(list(branch), dtype=pl.Utf8),
            "kind": pl.Series(list(kind), dtype=pl.Utf8),
            "state": pl.Series(list(state), dtype=pl.Utf8),
            "bin": bins_arr.astype(np.int32),
            "e_lo_ev": e_lo,
            "e_hi_ev": e_hi,
            "e_mid_ev": np.sqrt(e_lo * e_hi),
            "consensus_b": np.exp(mu),
            "consensus_log": mu,
            "sigma_log": sigma_mu,
            "spread_log": spread,
            "birge_ratio": birge,
            "chi2_ndf": np.where(n_ds_gb > 1, chi2_bin / np.maximum(n_ds_gb - 1, 1), np.nan),
            "n_datasets": n_ds_gb.astype(np.int32),
            "n_points": n_pts_gb.astype(np.int64),
        }
    )
    n_pts_ds = np.bincount(ds, cells["n_pts"].to_numpy().astype(np.float64), minlength=n_ds)
    ds_out = pl.DataFrame(
        {
            "dataset_key": pl.Series(ds_codes.tolist(), dtype=pl.Utf8),
            "group_key": pl.Series(
                cells.group_by("dataset_key", maintain_order=True)
                .agg(pl.col("group_key").first())
                .sort("dataset_key")["group_key"]
                .to_list(),
                dtype=pl.Utf8,
            ),
            "n_cells": n_cells_ds.astype(np.int32),
            "n_cells_compared": n_cmp.astype(np.int32),
            "n_points_used": n_pts_ds.astype(np.int64),
            "n_other_datasets": n_other.astype(np.int32),
            "bias_log": b,
            "bias_sigma": np.sqrt(1.0 / (np.bincount(ds, w, minlength=n_ds) + lam / tau2)),
            "bias_loo": np.where(n_cmp > 0, bias_loo, np.nan),
            "bias_loo_sigma": np.where(n_cmp > 0, bias_loo_sigma, np.nan),
            "z_loo": np.where(n_cmp > 0, z_loo, np.nan),
            "agree_2sigma": pl.Series(
                [
                    bool(a) if c > 0 else None
                    for a, c in zip(np.abs(z_loo) <= cfg.agree_z, n_cmp, strict=True)
                ],
                dtype=pl.Boolean,
            ),
            "excess_sigma": np.sqrt(s2),
            "chi2_ndf": chi2_ndf,
            "shape_chi2_ndf": shape_chi2_ndf,
            "lambda_bias": lam,
            "sigma_reported_frac": np.bincount(ds, reported.astype(np.float64), minlength=n_ds)
            / n_cells_ds,
        }
    )
    return ScatterFit(
        datasets=ds_out,
        bins=bins_out,
        cells=cells_out,
        config=cfg,
        n_iter_used=it,
        converged=converged,
        info={
            "n_cells": n,
            "n_datasets": n_ds,
            "n_bins": n_gb,
            "last_delta": last_delta,
            "rms_delta": rms_delta,
        },
    )


# ----------------------------------------------------------------------------- point outliers


def point_outlier_fraction(
    tbl: pa.Table, fit: ScatterFit, *, index: TableIndex | None = None, z_cut: float = 3.0
) -> pl.DataFrame:
    """Per dataset: fraction of (positive, finite) points more than ``z_cut`` sigma from
    the bin consensus, using the point's own relative sigma (floored) and the consensus sigma."""
    cfg = fit.config
    idx = index or index_table(tbl)
    rows = np.flatnonzero(idx.usable)
    empty = pl.DataFrame(
        schema={
            "dataset_key": pl.Utf8,
            "n_points_valid": pl.Int64,
            "n_nonpositive": pl.Int64,
            "frac_outlier_3sig": pl.Float64,
        }
    )
    if rows.size == 0:
        return empty
    sub = tbl.take(pa.array(rows))
    e_col = sub["energy_ev"]
    e_col = e_col.combine_chunks() if isinstance(e_col, pa.ChunkedArray) else e_col
    n_pts = e_col.value_lengths().fill_null(0).to_numpy(zero_copy_only=False).astype(np.int64)
    e = _flatten_aligned(e_col, n_pts)
    v, st, sy = _values_for_fit(sub, idx, rows, n_pts)
    row = np.repeat(np.arange(rows.size), n_pts)
    ok = np.isfinite(e) & (e > 0) & np.isfinite(v)
    nonpos = ok & (v <= 0)
    e, v, st, sy, row = (
        e[ok & ~nonpos],
        v[ok & ~nonpos],
        st[ok & ~nonpos],
        sy[ok & ~nonpos],
        row[ok & ~nonpos],
    )
    gkeys = idx.group_key[rows]
    is_ri = np.array([g.split("|")[3] == "ri" for g in gkeys], dtype=bool)[row]
    b = bin_index(e, cfg.bins_per_decade)
    ri_same = is_ri & (e >= 0.3) & (e <= 1.0)
    b[ri_same] = bin_index(np.array([_RI_CUTOFF_BIN_EV]), cfg.bins_per_decade)[0]
    gb_str = np.char.add(np.char.add(gkeys[row].astype(str), "|"), b.astype(str))
    lookup = dict(
        zip(
            (fit.bins["group_key"] + "|" + fit.bins["bin"].cast(pl.Utf8)).to_list(),
            zip(fit.bins["consensus_log"].to_list(), fit.bins["sigma_log"].to_list(), strict=True),
            strict=True,
        )
    )
    mu = np.array([lookup.get(k, (np.nan, np.nan))[0] for k in gb_str])
    smu = np.array([lookup.get(k, (np.nan, np.nan))[1] for k in gb_str])
    rel = np.sqrt(
        np.where(np.isfinite(st), (st / v) ** 2, 0.0)
        + np.where(np.isfinite(sy), (sy / v) ** 2, 0.0)
    )
    rel = np.where(np.isfinite(st) | np.isfinite(sy), rel, cfg.sigma_default)
    rel = np.clip(np.abs(rel), cfg.sigma_floor, cfg.sigma_cap)
    with np.errstate(invalid="ignore", divide="ignore"):
        z = (np.log(v) - mu) / np.sqrt(rel * rel + smu * smu)
    valid = np.isfinite(z)
    n_valid = np.bincount(row, valid.astype(np.float64), minlength=rows.size)
    n_out = np.bincount(row, (valid & (np.abs(z) > z_cut)).astype(np.float64), minlength=rows.size)
    n_np = np.bincount(np.repeat(np.arange(rows.size), n_pts)[nonpos], minlength=rows.size)
    with np.errstate(invalid="ignore", divide="ignore"):
        frac = np.where(n_valid > 0, n_out / n_valid, np.nan)
    return pl.DataFrame(
        {
            "dataset_key": pl.Series(idx.dataset_key[rows].tolist(), dtype=pl.Utf8),
            "n_points_valid": n_valid.astype(np.int64),
            "n_nonpositive": n_np.astype(np.int64),
            "frac_outlier_3sig": frac,
        }
    )


# ----------------------------------------------------------------------------- driver


def cells_from_parquet(
    path: Path, *, bins_per_decade: int = 10, verbose: bool = True
) -> pl.DataFrame:
    """Stream a Measurement parquet by row group and stack its cells (RSS stays flat)."""
    parts: list[pl.DataFrame] = []
    t0 = time.time()
    for i, tbl in enumerate(iter_row_groups(path, _MEAS_COLUMNS)):
        parts.append(cells_from_table(tbl, bins_per_decade=bins_per_decade))
        if verbose and (i + 1) % 10 == 0:
            print(
                f"  row group {i + 1}: {sum(p.height for p in parts)} cells,"
                f" {time.time() - t0:.0f}s",
                file=sys.stderr,
            )
    return (
        pl.concat([p for p in parts if p.height], how="vertical")
        if parts
        else pl.DataFrame(schema=_cell_schema())
    )


def run(
    source: Path, out_dir: Path, *, tag: str = "v0", cfg: ScatterConfig | None = None
) -> ScatterFit:
    cfg = cfg or ScatterConfig()
    cells = cells_from_parquet(source, bins_per_decade=cfg.bins_per_decade)
    fit = fit_scatter_model(cells, cfg)
    out_dir.mkdir(parents=True, exist_ok=True)
    fit.bins.write_parquet(out_dir / f"consensus_{tag}.parquet")
    fit.datasets.write_parquet(out_dir / f"discrepancy_{tag}.parquet")
    summary = {
        "config": asdict(cfg),
        "iterations": fit.n_iter_used,
        "converged": fit.converged,
        **fit.info,
    }
    print(json.dumps(summary, indent=1))
    return fit


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument(
        "--source", type=Path, default=REPO / "staging" / "exfor_capture_Z26-92.parquet"
    )
    ap.add_argument("--out", type=Path, default=REPO / "curated")
    ap.add_argument("--tag", default="v0")
    a = ap.parse_args(argv)
    run(a.source, a.out, tag=a.tag)


if __name__ == "__main__":
    main()
