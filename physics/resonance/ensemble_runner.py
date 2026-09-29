"""Compute ladder ensembles from a job table (``scripts/resonance_v0.py ensembles --jobs-only``).

Needs only numpy, scipy, pandas and `physics.resonance.ladder`, so a shard can run on any box:

    python -m physics.resonance.ensemble_runner JOBS.parquet OUT.parquet --n-ladders 100 \
        --shard 0 --of 2

Each job draws its average parameters log-normally (mean, sigma per head) for every ladder, so the
spread of an observable carries both the Porter-Thomas/GOE randomness and the parameter
uncertainty. The generator is seeded from crc32("target:mode"): shards and machines give the
same numbers for the same job.

Two job columns added for WP-19b step 1 (resonance-v0.md said the v0 ensembles were "too narrow
above 1 keV and for A >= 190"):

``sigma2_sigma``   log10 width of a log-normal draw on the spin-cutoff parameter sigma^2, which
                   v0 held fixed at its Ignatyuk/RIPL central value. sigma^2 sets how D0 is split
                   among compound spins and therefore the p-wave level density, which controls
                   capture once individual resonances have averaged out.
``d0_max_ev``      the refusal threshold (step 2). A job whose *central* D0 exceeds it is refused:
                   observables come back NaN with ``refused = True`` and a reason string, instead
                   of a 1e-30 b answer the statistical model has no business giving. Individual
                   draws inside an accepted ensemble are allowed past the threshold, so the
                   interval is not truncated.
"""
from __future__ import annotations

import argparse
import time
import zlib
from pathlib import Path

import numpy as np
import pandas as pd

from physics.resonance import ladder as L

WINDOWS = ((0.5, 10.0), (10.0, 100.0), (100.0, 1e3), (1e3, 1e4), (1e4, 1e5))
HEADS = ("d0", "s0", "gg", "s1")


def _f(job: dict, key: str, default: float) -> float:
    """Job column as a float, tolerating a missing column or a NaN (older job tables)."""
    v = job.get(key, default)
    try:
        v = float(v)
    except (TypeError, ValueError):
        return default
    return default if not np.isfinite(v) else v


def one(job: dict, n_ladders: int) -> dict:
    rng = np.random.default_rng(zlib.crc32(f"{job['target_id']}:{job['mode']}".encode()))
    cols: dict[str, list] = {"thermal": [], "ri": [], "ri_tail": []}
    cols.update({f"mean_{lo:g}_{hi:g}": [] for lo, hi in WINDOWS})
    d0_max = _f(job, "d0_max_ev", L.D0_MAX_EV)
    s2_sigma = _f(job, "sigma2_sigma", 0.0)
    central = L.AverageParams(awri=job["awri"], target_spin=job["spin"],
                              d0_ev=10 ** job["d0_log10"], s0=10 ** job["s0_log10"],
                              gg_ev=10 ** job["gg_log10"], s1=10 ** job["s1_log10"],
                              sigma2=job["sigma2"])
    try:
        L.check_domain(central, d0_max=d0_max)
    except L.LadderDomainError as exc:
        nan = np.full(n_ladders, np.nan)
        return {**job, "refused": True, "refusal_reason": str(exc),
                **{k: nan.copy() for k in cols}}
    for _ in range(n_ladders):
        draw = {h: 10 ** (job[f"{h}_log10"] + job[f"{h}_sigma"] * rng.standard_normal()) for h in HEADS}
        s2 = job["sigma2"]
        sigma2 = s2 * 10 ** (s2_sigma * rng.standard_normal()) if s2_sigma else s2
        p = L.AverageParams(awri=job["awri"], target_spin=job["spin"], d0_ev=draw["d0"],
                            s0=draw["s0"], gg_ev=draw["gg"], s1=draw["s1"], sigma2=sigma2)
        o = L.ensemble_observables(p, 1, rng, windows=WINDOWS, allow_out_of_domain=True)
        for k in cols:
            cols[k].append(float(o[k][0]))
    return {**job, "refused": False, "refusal_reason": None,
            **{k: np.asarray(v) for k, v in cols.items()}}


def run(jobs_path: Path, out_path: Path, n_ladders: int, shard: int, of: int) -> None:
    jobs = pd.read_parquet(jobs_path)
    jobs = jobs.iloc[[i for i in range(len(jobs)) if i % of == shard]]
    rows, done = [], set()
    if out_path.is_file():
        prev = pd.read_parquet(out_path)
        rows = prev.to_dict("records")
        done = set(zip(prev.target_id, prev["mode"]))
    t0 = time.time()
    for job in jobs.to_dict("records"):
        if (job["target_id"], job["mode"]) in done:
            continue
        rows.append(one(job, n_ladders))
        if len(rows) % 10 == 0:
            pd.DataFrame(rows).to_parquet(out_path)
            print(f"[ens] {len(rows)}/{len(jobs)} {time.time() - t0:.0f}s", flush=True)
    df = pd.DataFrame(rows)
    df.to_parquet(out_path)
    n_ref = int(df.refused.sum()) if "refused" in df else 0
    print(f"[ens] wrote {len(rows)} ensembles ({n_ref} refused) to {out_path}", flush=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("jobs", type=Path)
    ap.add_argument("out", type=Path)
    ap.add_argument("--n-ladders", type=int, default=100)
    ap.add_argument("--shard", type=int, default=0)
    ap.add_argument("--of", type=int, default=1)
    a = ap.parse_args()
    run(a.jobs, a.out, a.n_ladders, a.shard, a.of)


if __name__ == "__main__":
    main()
