"""TALYS parameter sweep: Latin-hypercube design x nuclide set x energy grid.

One TALYS run per (nuclide, sample_id) with the full incident-energy grid in a
single ``energy`` file.  ``sample_id 0`` is the plain TALYS default for every
nuclide (the "TALYS baseline"); ``sample_id >= 1`` are LHS draws from
:mod:`physics.talys.params`.

Storage (``out_dir``, default ``features/talys_sweep/``)
-------------------------------------------------------
``shards/<host>-<pid>-<n>.parquet``   append-only shards, one row per run
``sweep.parquet``                     consolidated table (``consolidate``)
``design.json``                       nuclide list, energy grid, config, seed

Row schema: ``Z, A, N, sample_id, status, error, params (list<f64> coded
vector, see params.PARAM_NAMES), p_<name> (physical value per parameter),
keywords (TALYS input lines), sn_cn_kev, E_mev (list), log10_xs_<channel>
(list, NaN where TALYS wrote nothing or zero), talys_version, runtime_s,
hostname, timestamp``.

Resumable: on start-up every shard's ``(Z, A, sample_id)`` keys are read and
those runs are skipped.  Work is ordered sample-major (sample 0 for every
nuclide, then sample 1, ...) so a wall-clock ``max_minutes`` cut leaves a
balanced dataset.

Scaling to 10^5-10^6 runs (BLUEPRINT §9): the design is a pure function of
``(seed, nuclide list, n_samples)`` and every worker only needs the config
and its own shard directory, so a cloud fleet can run
``python -m physics.talys.sweep --config configs/talys_sweep_cloud.yaml
shard_index=k n_shards=K`` on K machines and the shards are merged by
``consolidate``.  Memory: each TALYS process peaks at ~0.75 GB RSS; the pool
size is capped by ``workers`` and backed off to ``min_workers`` when
``/proc/meminfo`` MemAvailable drops below ``mem_backoff_gb``.
"""

from __future__ import annotations

import json
import os
import re
import signal
import socket
import subprocess
import sys
import time
from collections import deque
from collections.abc import Sequence
from concurrent.futures import FIRST_COMPLETED, ProcessPoolExecutor, wait
from dataclasses import asdict
from pathlib import Path

import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq
from omegaconf import DictConfig, OmegaConf
from scipy.stats import qmc

from physics.talys import params as P
from physics.talys.nuclides import Nuclide, select_nuclides
from physics.talys.runner import TalysError, run_talys, talys_available

REPO = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG = REPO / "configs" / "talys_sweep.yaml"

CHANNELS: tuple[str, ...] = ("total", "elastic", "capture", "inelastic", "n2n", "np", "na")
# The surrogate's output width is fixed by its own CHANNELS tuple, so extending that would
# invalidate every trained checkpoint. The sweep records a superset instead: TALYS writes
# fission.tot only when `fission y` is in the input, and WP-24 has no data without it.
SWEEP_CHANNELS: tuple[str, ...] = CHANNELS + ("fission",)

# Speed/output keywords (all verified in the TALYS-2.25 source, see params.py).
DEFAULT_TALYS_KEYWORDS: dict[str, str] = {
    "outdiscrete": "n",
    "outspectra": "n",
    "outgamdis": "n",
    "bins": "20",
    "maxlevelstar": "20",
    "preequilibrium": "y",
}


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------


def default_config() -> DictConfig:
    return OmegaConf.create(
        {
            "out_dir": "features/talys_sweep",
            "seed": 20260908,
            "n_samples": 24,
            "nuclides": {
                "mode": "stratified",
                "z_min": 26,
                "z_max": 92,
                "z_step": 2,
                "n_rich": 6,
                "rich_offset": 4,
                "min_half_life_s": 3.15e7,
                "extra": [],
            },
            "energies": {"e_min_mev": 1.0e-3, "e_max_mev": 20.0, "n": 20},
            "talys_keywords": dict(DEFAULT_TALYS_KEYWORDS),
            "workers": 4,
            "min_workers": 2,
            "mem_backoff_gb": 2.0,
            "shard_size": 20,
            "max_minutes": None,
            "timeout_s": 900,
            # WP-25: the runner has always taken a projectile; the sweep never passed one, so
            # every run in this project's history has been neutron-induced.
            "projectile": "n",
            # TALYS keywords to drop from the parameter vector. `ldmodel` must be here for any
            # fission sweep: see docs/results/wp24-fission-ldmodel-trap.md.
            "omit_params": [],
            # Parameters the design is allowed to move; [] means all twelve (the historical
            # behaviour). Naming a subset samples that subspace at the same run count and
            # pins the rest at the TALYS default -- see subspace_design.
            "active_params": [],
            "shard_index": 0,
            "n_shards": 1,
            "include_default": True,
        }
    )


def load_config(path: str | Path | None = None, overrides: list[str] | None = None) -> DictConfig:
    cfg = default_config()
    if path is not None and Path(path).is_file():
        cfg = OmegaConf.merge(cfg, OmegaConf.load(Path(path)))
    if overrides:
        cfg = OmegaConf.merge(cfg, OmegaConf.from_dotlist(list(overrides)))
    return cfg


# ---------------------------------------------------------------------------
# Design
# ---------------------------------------------------------------------------


def energy_grid(e_min_mev: float = 1e-3, e_max_mev: float = 20.0, n: int = 20) -> np.ndarray:
    return np.logspace(np.log10(e_min_mev), np.log10(e_max_mev), int(n))


def lhs_design(n_nuclides: int, n_samples: int, seed: int) -> np.ndarray:
    """Coded LHS design of shape (n_nuclides * n_samples, N_PARAMS).

    A single Latin hypercube over the whole (nuclide, sample) set gives the
    surrogate more distinct parameter points than repeating one design per
    nuclide.  Row ``i * n_samples + (s - 1)`` belongs to nuclide ``i``,
    sample ``s`` (``s >= 1``).
    """
    n = n_nuclides * n_samples
    if n == 0:
        return np.zeros((0, P.N_PARAMS))
    sampler = qmc.LatinHypercube(d=P.N_PARAMS, seed=int(seed), scramble=True)
    u = sampler.random(n)
    lo, hi = P.coded_bounds()
    return qmc.scale(u, lo, hi)


def subspace_design(n_nuclides: int, n_samples: int, seed: int,
                    active: Sequence[str] | None = None) -> np.ndarray:
    """Coded LHS restricted to ``active`` parameters; the rest sit at their TALYS default.

    D1/D3 in ``docs/results/idea-register.md``: of the 12 swept parameters only three are
    recoverable from a cross section even with perfect data and all seven channels --
    ``gsf_width_factor`` (+20.3% skill over guessing), ``ld_a_factor`` (+11.0%) and
    ``gsf_norm`` (+10.8%). The other nine score 0%, so a full-dimensional Latin hypercube
    spends most of its runs moving knobs the likelihood cannot see, and the surrogate spends
    its capacity learning directions nothing will ever ask it about.

    Sampling only the identifiable dimensions puts the same run count where the likelihood
    has curvature. The inactive dimensions take ``default_coded_vector`` rather than being
    omitted, so the recorded ``p_<name>`` columns are what TALYS actually ran -- unlike
    ``omit_params``, which drops the keyword but leaves the sampled value in the design.

    ``active=None`` (or a list naming every parameter) reproduces :func:`lhs_design` exactly,
    so existing sweeps are unaffected.
    """
    if not active:
        return lhs_design(n_nuclides, n_samples, seed)
    unknown = [a for a in active if a not in P.PARAM_INDEX]
    if unknown:
        raise ValueError(f"unknown parameter(s) in active_params: {unknown}; "
                         f"known: {list(P.PARAM_NAMES)}")
    idx = [P.PARAM_INDEX[a] for a in active]
    if len(set(idx)) == P.N_PARAMS:
        return lhs_design(n_nuclides, n_samples, seed)
    n = n_nuclides * n_samples
    out = np.tile(P.default_coded_vector(), (max(n, 0), 1))
    if n == 0:
        return out.reshape(0, P.N_PARAMS)
    sampler = qmc.LatinHypercube(d=len(idx), seed=int(seed), scramble=True)
    u = sampler.random(n)
    lo, hi = P.coded_bounds()
    out[:, idx] = qmc.scale(u, lo[idx], hi[idx])
    return out


def coded_vector_for(design: np.ndarray, i_nuc: int, sample_id: int, n_samples: int) -> np.ndarray:
    if sample_id == 0:
        return P.default_coded_vector()
    return design[i_nuc * n_samples + (sample_id - 1)]


def build_tasks(cfg: DictConfig, nuclides: list[Nuclide]) -> list[tuple[int, int]]:
    """(nuclide index, sample_id) pairs, sample-major, restricted to this shard."""
    first = 0 if cfg.include_default else 1
    tasks = [(i, s) for s in range(first, int(cfg.n_samples) + 1) for i in range(len(nuclides))]
    k, K = int(cfg.shard_index), int(cfg.n_shards)
    return [t for j, t in enumerate(tasks) if j % K == k]


# ---------------------------------------------------------------------------
# One run
# ---------------------------------------------------------------------------


def _match_grid(E_req: np.ndarray, E_out: np.ndarray, xs: np.ndarray) -> np.ndarray:
    """log10 xs on the requested grid; NaN where absent or non-positive."""
    out = np.full(E_req.shape, np.nan)
    if E_out.size == 0:
        return out
    for j, e in enumerate(E_req):
        k = np.argmin(np.abs(E_out - e))
        if abs(E_out[k] - e) <= 1e-4 * e and xs[k] > 0:
            out[j] = np.log10(xs[k])
    return out


def run_one(
    nuc: Nuclide,
    sample_id: int,
    x: np.ndarray,
    energies: np.ndarray,
    base_keywords: dict[str, str],
    timeout_s: float = 900.0,
    projectile: str = "n",
    omit_params: tuple[str, ...] = (),
) -> dict:
    """Run TALYS for one (nuclide, coded parameter vector); never raises."""
    x = np.asarray(x, dtype=float)
    kw = dict(base_keywords)
    par_kw = P.to_keywords(x, nuc.Z, nuc.A)
    # Setting a keyword to what looks like its default is not the same as leaving it out.
    # `ldmodel 1` is in the parameter vector and pinning it explicitly changes the level
    # densities TALYS uses at the FISSION BARRIERS: U-238 (n,f) at 12 MeV drops from 1103 mb
    # to 66 mb, a factor of 17, while capture does not move at all. Anything sweeping fission
    # has to omit it.
    for name in omit_params:
        par_kw.pop(name, None)
    kw.update(par_kw)
    phys = P.decode(x)
    # The sampled value is still in `x`, but it was not applied. Recording it in `p_<name>`
    # would hand the surrogate an input column that looks like a knob and moves nothing --
    # it would fit zero sensitivity to a parameter TALYS never saw. NaN says "not applied".
    for name in omit_params:
        if name in phys:
            phys[name] = float("nan")
    rec: dict = {
        "Z": nuc.Z,
        "A": nuc.A,
        "N": nuc.N,
        "sample_id": int(sample_id),
        "status": "ok",
        "error": "",
        "params": x.tolist(),
        **{f"p_{k}": float(v) for k, v in phys.items()},
        "keywords": "\n".join(P.keyword_lines(kw)),
        "sn_cn_kev": float(nuc.sn_cn_kev),
        "E_mev": [float(e) for e in energies],
        **{f"log10_xs_{c}": [float("nan")] * len(energies) for c in SWEEP_CHANNELS},
        "talys_version": "",
        "runtime_s": float("nan"),
        "hostname": socket.gethostname(),
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }
    t0 = time.perf_counter()
    try:
        # WP-25 needs proton- and deuteron-induced data and the sweep only ever ran neutrons.
        # The runner has taken a projectile since it was written; the sweep never passed one.
        res = run_talys(nuc.Z, nuc.A, list(energies), extra_keywords=kw, timeout=timeout_s,
                        projectile=projectile)
    except TalysError as exc:
        rec["status"] = "error"
        # Keep the HEAD, not the tail. run_talys builds the message as
        # "TALYS failed (rc=N) in <dir>:" followed by any fatal TALYS-error lines and then up
        # to 2000 characters of output -- so [-1500:] reliably discarded the return code and
        # the extracted error lines, leaving 1500 characters of ordinary cross-section tables.
        # Six Lu/Hf/Ta failures could not be diagnosed at all until this was fixed.
        msg = str(exc)
        rec["error"] = msg if len(msg) <= 1500 else msg[:1100] + "\n...\n" + msg[-400:]
        rec["runtime_s"] = time.perf_counter() - t0
        return rec
    except Exception as exc:  # pragma: no cover - defensive
        rec["status"] = "error"
        rec["error"] = f"{type(exc).__name__}: {exc}"[-1500:]
        rec["runtime_s"] = time.perf_counter() - t0
        return rec
    rec["runtime_s"] = float(res["elapsed"])
    rec["talys_version"] = res.get("talys_version") or ""
    ch = res["channels"]
    for c in SWEEP_CHANNELS:
        if c in ch:
            rec[f"log10_xs_{c}"] = _match_grid(energies, ch[c]["E"], ch[c]["xs"]).tolist()
    # Silent-failure guard: a run with no finite total or capture is an error.
    # The acceptance test was written for neutrons. A charged projectile has no meaningful
    # total cross section -- the Coulomb amplitude diverges -- so TALYS writes none, and
    # requiring one rejects every proton run with "no finite total/capture cross section".
    if projectile == "n":
        ok_run = (np.isfinite(rec["log10_xs_total"]).any()
                  and np.isfinite(rec["log10_xs_capture"]).any())
        why = "no finite total/capture cross section written"
    else:
        ok_run = any(np.isfinite(rec[f"log10_xs_{c}"]).any()
                     for c in SWEEP_CHANNELS if f"log10_xs_{c}" in rec)
        why = f"no finite cross section written for projectile {projectile}"
    if not ok_run:
        rec["status"] = "error"
        rec["error"] = why
    return rec


def _worker(args) -> dict:
    nuc_dict, sample_id, x, energies, base_kw, timeout_s, projectile, omit = args
    return run_one(
        Nuclide(**nuc_dict), sample_id, np.asarray(x), np.asarray(energies), base_kw, timeout_s,
        projectile, tuple(omit),
    )


# ---------------------------------------------------------------------------
# Storage
# ---------------------------------------------------------------------------


def _schema(n_e: int) -> pa.Schema:
    fields = [
        ("Z", pa.int16()),
        ("A", pa.int16()),
        ("N", pa.int16()),
        ("sample_id", pa.int32()),
        ("status", pa.string()),
        ("error", pa.string()),
        ("params", pa.list_(pa.float64())),
    ]
    fields += [(f"p_{k}", pa.float64()) for k in P.PARAM_NAMES]
    fields += [
        ("keywords", pa.string()),
        ("sn_cn_kev", pa.float64()),
        ("E_mev", pa.list_(pa.float64())),
    ]
    fields += [(f"log10_xs_{c}", pa.list_(pa.float64())) for c in SWEEP_CHANNELS]
    fields += [
        ("talys_version", pa.string()),
        ("runtime_s", pa.float64()),
        ("hostname", pa.string()),
        ("timestamp", pa.string()),
    ]
    return pa.schema(fields)


def stop_pool(ex, futures=()) -> int:
    """Cancel pending work and hard-stop the pool's workers. Returns workers signalled.

    Order matters: ``shutdown()`` sets ``ProcessPoolExecutor._processes`` to None, so the
    handles have to be taken first or the terminate loop raises on the way out -- which is
    how a SIGTERM once turned a clean stop into a non-zero exit with no summary written.
    """
    for fut in futures:
        fut.cancel()
    procs = list((getattr(ex, "_processes", None) or {}).values())
    ex.shutdown(wait=False, cancel_futures=True)
    for proc in procs:
        proc.terminate()
    return len(procs)


def write_shard(records: list[dict], out_dir: Path, tag: str) -> Path:
    shards = Path(out_dir) / "shards"
    shards.mkdir(parents=True, exist_ok=True)
    n_e = len(records[0]["E_mev"])
    table = pa.Table.from_pylist(records, schema=_schema(n_e))
    path = shards / f"{tag}.parquet"
    tmp = path.with_suffix(".parquet.tmp")
    pq.write_table(table, tmp)
    os.replace(tmp, path)
    return path


def completed_keys(out_dir: Path) -> set[tuple[int, int, int]]:
    """Runs a resume may skip: the ones that succeeded.

    Errored runs are deliberately excluded. Counting them as done makes every failure
    permanent -- the resume skips them, the summary reports the shard complete, and the hole
    is only visible to whoever thinks to compare the nuclide list against the output. That is
    how a run of the medical-isotope sweep nearly shipped without O-18, whose three
    recoverable `TALYS-error` lines the runner used to treat as fatal.
    """
    shards = sorted(Path(out_dir).glob("shards/*.parquet"))
    keys: set[tuple[int, int, int]] = set()
    for s in shards:
        t = pq.read_table(s, columns=["Z", "A", "sample_id", "status"])
        for z, a, sid, st in zip(t["Z"].to_pylist(), t["A"].to_pylist(),
                                 t["sample_id"].to_pylist(), t["status"].to_pylist(),
                                 strict=True):
            if st == "error":
                continue
            keys.add((z, a, sid))
    return keys


def load_sweep(out_dir: Path | str):
    """All runs as a polars DataFrame (consolidated file if fresh, else the shards)."""
    import polars as pl

    out_dir = Path(out_dir)
    shards = sorted(out_dir.glob("shards/*.parquet"))
    cons = out_dir / "sweep.parquet"
    if cons.is_file() and (
        not shards or cons.stat().st_mtime >= max(s.stat().st_mtime for s in shards)
    ):
        return pl.read_parquet(cons)
    if not shards:
        raise FileNotFoundError(f"no sweep shards under {out_dir}")
    df = pl.concat([pl.read_parquet(s) for s in shards], how="vertical_relaxed")
    # What makes two rows the same run is the nuclide and the PARAMETER VECTOR, not the
    # sample_id. sample_id is an index into one design and is reused across designs, so
    # deduplicating on it silently deletes genuinely distinct runs whenever sweeps are merged:
    # it threw away 17,946 of talys_sweep_merged2's 45,428 rows -- 40% of the corpus -- so
    # every surrogate seed trained on 27,482 runs while the plan recorded 45,428. Resume
    # duplicates still collapse, because a re-run of the same task has the same parameters.
    #
    # A retried run also leaves both rows: the old error and the new success. Sorting
    # successes last within each key makes that choice deliberate rather than a consequence
    # of shard filenames, which are PID-ordered.
    df = df.with_columns(
        _ok=(pl.col("status") == "ok").cast(pl.Int8),
        _key=pl.col("params").cast(pl.List(pl.Float64)).cast(pl.List(pl.Utf8)).list.join(","),
    )
    df = df.sort(["Z", "A", "_key", "_ok"])
    return (
        df.unique(subset=["Z", "A", "_key"], keep="last", maintain_order=True)
        .drop(["_ok", "_key"])
        .sort(["Z", "A", "sample_id"])
    )


def consolidate(out_dir: Path | str) -> Path:
    out_dir = Path(out_dir)
    df = load_sweep(out_dir)
    path = out_dir / "sweep.parquet"
    df.write_parquet(path)
    return path


# ---------------------------------------------------------------------------
# Scheduler
# ---------------------------------------------------------------------------


def mem_available_gb() -> float:
    """Available RAM in GB, or +inf if it genuinely cannot be determined.

    macOS has no ``/proc/meminfo``, so the Linux-only probe returned +inf there and the
    memory backoff silently did nothing -- on the 8 GB MacBook, the machine least able to
    afford it. Returning +inf is the right answer for "unknown" only if nothing else can be
    asked, so ask ``vm_stat`` first.
    """
    try:
        with open("/proc/meminfo") as fh:
            for line in fh:
                if line.startswith("MemAvailable:"):
                    return int(line.split()[1]) / 1024**2
    except OSError:
        pass
    if sys.platform == "darwin":
        try:
            out = subprocess.run(["vm_stat"], capture_output=True, text=True,
                                 timeout=10, check=True).stdout
            page = 4096
            free_pages = 0
            for line in out.splitlines():
                if line.startswith("Mach Virtual Memory Statistics"):
                    m = re.search(r"page size of (\d+) bytes", line)
                    if m:
                        page = int(m.group(1))
                # "available" on macOS is free + inactive + speculative: pages the kernel can
                # hand out without swapping. Wired and active are not available.
                elif line.startswith(("Pages free:", "Pages inactive:", "Pages speculative:")):
                    free_pages += int(line.rsplit(":", 1)[1].strip().rstrip("."))
            if free_pages:
                return free_pages * page / 1024**3
        except (OSError, subprocess.SubprocessError, ValueError):
            pass
    return float("inf")


def current_workers(cfg: DictConfig) -> int:
    return (
        int(cfg.min_workers) if mem_available_gb() < float(cfg.mem_backoff_gb) else int(cfg.workers)
    )


def write_design(
    cfg: DictConfig, nuclides: list[Nuclide], energies: np.ndarray, out_dir: Path
) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    doc = {
        "config": OmegaConf.to_container(cfg, resolve=True),
        "param_names": list(P.PARAM_NAMES),
        "channels": list(CHANNELS),
        "energies_mev": energies.tolist(),
        "nuclides": [asdict(n) for n in nuclides],
        "talys_source_missing_keywords": P.verify_keywords(),
    }
    (out_dir / "design.json").write_text(json.dumps(doc, indent=1, default=float))


def _log_flush(*args) -> None:
    """``print`` that flushes: the sweep runs under ``nohup`` with stdout redirected."""
    print(*args, flush=True)


class _Interrupted(Exception):
    pass


def _raise_interrupted(signum, frame):  # pragma: no cover - signal path
    raise _Interrupted(signum)


def run_sweep(cfg: DictConfig, *, log=_log_flush) -> dict:
    """Execute the sweep described by *cfg*; returns a summary dict.

    SIGTERM/SIGINT flush the finished-but-unwritten runs to a shard before
    exiting, so a killed sweep loses at most the runs that were in flight.
    """
    if not talys_available():
        raise TalysError("TALYS binary not available")
    missing = P.verify_keywords()
    if missing:
        raise RuntimeError(f"keywords not found in TALYS source: {missing}")

    out_dir = (REPO / cfg.out_dir) if not Path(cfg.out_dir).is_absolute() else Path(cfg.out_dir)
    nuclides = select_nuclides(**OmegaConf.to_container(cfg.nuclides, resolve=True))
    energies = energy_grid(**OmegaConf.to_container(cfg.energies, resolve=True))
    design = subspace_design(len(nuclides), int(cfg.n_samples), int(cfg.seed),
                             list(cfg.get("active_params", []) or []))
    base_kw = {str(k): str(v) for k, v in OmegaConf.to_container(cfg.talys_keywords).items()}
    write_design(cfg, nuclides, energies, out_dir)

    done = completed_keys(out_dir)
    tasks = build_tasks(cfg, nuclides)
    pending = deque((i, s) for i, s in tasks if (nuclides[i].Z, nuclides[i].A, s) not in done)
    total = len(tasks)
    log(
        f"[sweep] {len(nuclides)} nuclides x {int(cfg.n_samples)} samples (+default) x "
        f"{len(energies)} energies; {total} runs in this shard, {len(pending)} pending, "
        f"{len(done)} already done"
    )

    t_start = time.time()
    deadline = t_start + 60.0 * float(cfg.max_minutes) if cfg.max_minutes else None
    tag_base = f"{socket.gethostname()}-{os.getpid()}"
    n_flushed = 0
    buffer: list[dict] = []
    n_ok = n_err = 0
    runtimes: list[float] = []
    stopped_early = False

    def flush() -> None:
        nonlocal buffer, n_flushed
        if buffer:
            write_shard(buffer, out_dir, f"{tag_base}-{n_flushed:05d}")
            n_flushed += 1
            buffer = []

    futures: dict = {}
    prev_handlers = {}
    for sig in (signal.SIGTERM, signal.SIGINT):
        try:
            prev_handlers[sig] = signal.signal(sig, _raise_interrupted)
        except ValueError:  # not in the main thread (tests)
            pass
    ex = ProcessPoolExecutor(max_workers=int(cfg.workers))
    try:
        while pending or futures:
            if deadline and time.time() > deadline and pending:
                log(f"[sweep] deadline reached with {len(pending)} runs left; finishing in-flight")
                pending.clear()
                stopped_early = True
            cap = current_workers(cfg)
            while pending and len(futures) < cap:
                i, s = pending.popleft()
                nuc = nuclides[i]
                x = coded_vector_for(design, i, s, int(cfg.n_samples))
                fut = ex.submit(
                    _worker, (asdict(nuc), s, x, energies, base_kw, float(cfg.timeout_s),
                              str(cfg.get("projectile", "n")),
                              tuple(cfg.get("omit_params", []) or []))
                )
                futures[fut] = (nuc, s)
            if not futures:
                break
            finished, _ = wait(list(futures), timeout=5.0, return_when=FIRST_COMPLETED)
            for fut in finished:
                nuc, s = futures.pop(fut)
                rec = fut.result()
                buffer.append(rec)
                if rec["status"] == "ok":
                    n_ok += 1
                    runtimes.append(rec["runtime_s"])
                else:
                    n_err += 1
                    log(f"[sweep] ERROR {nuc.key} s{s}: {rec['error'].splitlines()[-1][:120]}")
                n_done = n_ok + n_err
                if n_done % 10 == 0 or n_done == 1:
                    el = time.time() - t_start
                    log(
                        f"[sweep] {n_done}/{len(tasks) - len(done)} done, {n_err} err, "
                        f"{el / 60:.1f} min, mean "
                        f"{np.mean(runtimes) if runtimes else 0:.1f} s/run, "
                        f"workers={cap}, MemAvail={mem_available_gb():.1f} GB"
                    )
                if len(buffer) >= int(cfg.shard_size):
                    flush()
    except _Interrupted as exc:
        stopped_early = True
        log(f"[sweep] signal {exc.args[0]}: flushing {len(buffer)} finished runs and stopping")
        stop_pool(ex, futures)
    else:
        ex.shutdown(wait=True)
    finally:
        flush()
        for sig, h in prev_handlers.items():
            signal.signal(sig, h)
    summary = {
        "n_nuclides": len(nuclides),
        "n_samples": int(cfg.n_samples),
        "n_energies": int(len(energies)),
        "runs_completed_now": n_ok + n_err,
        "runs_ok": n_ok,
        "runs_error": n_err,
        "runs_previously_done": len(done),
        "wall_minutes": (time.time() - t_start) / 60.0,
        "mean_runtime_s": float(np.mean(runtimes)) if runtimes else None,
        "stopped_early": stopped_early,
        "out_dir": str(out_dir),
    }
    (out_dir / f"summary-{tag_base}.json").write_text(json.dumps(summary, indent=1))
    log(f"[sweep] finished: {json.dumps(summary)}")
    return summary


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    import argparse

    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument(
        "command", nargs="?", default="run", choices=["run", "consolidate", "status", "plan"]
    )
    ap.add_argument("--config", default=str(DEFAULT_CONFIG))
    ap.add_argument("overrides", nargs="*", help="OmegaConf dot-list overrides, e.g. n_samples=8")
    ns, extra = ap.parse_known_args(argv)
    cfg = load_config(ns.config, list(ns.overrides) + [e for e in extra if "=" in e])
    out_dir = (REPO / cfg.out_dir) if not Path(cfg.out_dir).is_absolute() else Path(cfg.out_dir)
    if ns.command == "run":
        run_sweep(cfg)
    elif ns.command == "consolidate":
        p = consolidate(out_dir)
        print(f"wrote {p}")
    elif ns.command == "status":
        keys = completed_keys(out_dir)
        print(f"{len(keys)} runs stored under {out_dir}")
    elif ns.command == "plan":
        nuclides = select_nuclides(**OmegaConf.to_container(cfg.nuclides, resolve=True))
        tasks = build_tasks(cfg, nuclides)
        print(OmegaConf.to_yaml(cfg))
        print(f"{len(nuclides)} nuclides: " + " ".join(n.key for n in nuclides))
        print(f"{len(tasks)} runs in shard {cfg.shard_index}/{cfg.n_shards}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
