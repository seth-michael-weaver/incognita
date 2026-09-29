"""A-inc for the coupled-channels incident channel: the port against TALYS's own
`incident_scalars` on every coupled-channels reference target and every incident energy -- the
eleven `colltype R` ones (stages a1 and a2-SO) and Ca-40, `colltype V` (stage a2-V).

Metric of contract §6: r = |ln(port/TALYS)| over points above the floor; the gate bounds p95 at
1e-2 and the median and max are reported.

Task: T13 (physics/hf/CONTRACT.md §7). Acceptance test: A-inc (§6).

Usage:
    uv run python -m physics.hf.ecis.score                 # injected OMP, all 23 energies
    uv run python -m physics.hf.ecis.score --chained       # T4's OMP where it exists
    uv run python -m physics.hf.ecis.score --above-soswitch          # the E > soswitch gate
    uv run python -m physics.hf.ecis.score --above-soswitch --undeformed-so
                                                # the same points with lo(13) left F: the A/B
                                                # that says what the deformed spin-orbit is worth
"""

from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path

import numpy as np
import torch

from physics.hf.core.tensors import DTYPE
from physics.hf.ecis.incident import SOSWITCH_DEFAULT_MEV, incident_coupled
from physics.hf.ecis.reference import coupled_band, incident_omp
from physics.hf.talys_reference import REFERENCE_SET

TOL = 1.0e-2  # contract §6, A-inc
REF = Path(__file__).resolve().parents[3] / "features" / "hf_reference" / "incident_scalars.parquet"
OUT = Path(__file__).resolve().parents[3] / "docs" / "results" / "hf-ecis-gate.json"
QUANTITIES = ("sigma_tot_omp_mb", "sigma_reac_omp_mb", "sigma_el_omp_mb", "s0", "s1", "r_prime_fm")
FIELDS = {
    "sigma_tot_omp_mb": "sigma_tot_mb",
    "sigma_reac_omp_mb": "sigma_reac_mb",
    "sigma_el_omp_mb": "sigma_shape_el_mb",
    "s0": "s0",
    "s1": "s1",
    "r_prime_fm": "r_prime_fm",
}


def rotational_targets() -> list:
    """Every reference target TALYS runs with the symmetric rotational coupled-channels model."""
    return [t for t in REFERENCE_SET if coupled_band(t.Z, t.A)["colltype"] == "R"]


def coupled_targets() -> list:
    """Every reference target whose incident channel is coupled channels at all: the eleven
    `colltype R` ones (stage a1) and the one `colltype V` one, Ca-40 (stage a2)."""
    return [t for t in REFERENCE_SET if coupled_band(t.Z, t.A)["colltype"] in ("R", "V")]


def score_target(target, variant: str = "default", e_max_mev: float = float("inf"),
                 refine: int = 1, chained: bool = False, e_min_mev: float = 0.0,
                 undeformed_so: bool = False) -> dict:
    """Score one target's A-inc quantities.

    `e_min_mev` cuts the energy axis from below (the `--above-soswitch` gate uses it);
    `undeformed_so` forces ECIS's `lo(13) = F` branch above the switch, which is NOT what TALYS
    does there and exists only as the A/B arm that says what the deformed spin-orbit is worth.
    """
    import pandas as pd

    ref = pd.read_parquet(REF)
    ref = ref[(ref.target == target.tag) & (ref.variant == variant)].sort_values("e_inc_mev")
    band = coupled_band(target.Z, target.A)
    ref = ref[(ref.e_inc_mev <= e_max_mev + 1.0e-9) & (ref.e_inc_mev > e_min_mev)]
    src = incident_omp(target.tag, variant)
    sel = (src.e_inc_mev <= e_max_mev + 1.0e-9) & (src.e_inc_mev > e_min_mev)
    e = src.e_inc_mev[sel]
    if chained:
        from physics.hf.input.defaults import default_params
        from physics.hf.omp.parameters import omp_parameters

        o = band["options"]
        p = omp_parameters(target.Z, target.A - target.Z, 1, e, default_params(target.Z, target.A, o), o)
    else:
        p = src.select(sel)
    t0 = time.time()
    inc, res = incident_coupled(p, target.Z, target.A, e, band, options=band["options"],
                                refine=refine,
                                allow_undeformed_spin_orbit=undeformed_so)
    dt = time.time() - t0
    rows = []
    for q in QUANTITIES:
        got = getattr(inc, FIELDS[q]).detach().numpy()
        want = ref[q].to_numpy(dtype=float)
        for i in range(len(want)):
            if not np.isfinite(got[i]) or not np.isfinite(want[i]) or want[i] <= 0 or got[i] <= 0:
                continue
            rows.append({"target": target.tag, "quantity": q, "e_inc_mev": float(e[i]),
                         "port": float(got[i]), "talys": float(want[i]),
                         "r": abs(math.log(got[i] / want[i]))})
    return {"rows": rows, "seconds": dt, "n_j": res.n_j, "ncoll": int(band["spin"].numel()),
            "kband": band["kband"], "deftype_D": bool(band["deformation_length"])}


def summarise(rows: list[dict]) -> dict:
    r = np.array([x["r"] for x in rows])
    return {"n": int(r.size), "median": float(np.median(r)), "p95": float(np.percentile(r, 95)),
            "max": float(r.max()), "pass": bool(np.percentile(r, 95) <= TOL)}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--variant", default="default")
    ap.add_argument("--emax", type=float, default=float("inf"))
    ap.add_argument("--refine", type=int, default=1)
    ap.add_argument("--chained", action="store_true")
    ap.add_argument("--targets", default="")
    ap.add_argument("--out", default=str(OUT))
    ap.add_argument(
        "--above-soswitch", action="store_true",
        help="only the eleven colltype R targets at E > soswitch, where ECIS deforms the "
             "spin-orbit potential (lo(13) = T)",
    )
    ap.add_argument(
        "--undeformed-so", action="store_true",
        help="leave the spin-orbit SPHERICAL above soswitch, which is not what TALYS does there "
             "-- the A/B arm of the deformed spin-orbit, not a gate",
    )
    a = ap.parse_args(argv)
    e_min, und = 0.0, a.undeformed_so
    if a.above_soswitch:
        e_min = SOSWITCH_DEFAULT_MEV
        if a.out == str(OUT):
            a.out = str(OUT.with_name(
                "hf-ecis-above-soswitch" + ("-undeformed" if und else "") + ".json"
            ))
    torch.set_num_threads(2)
    tgs = rotational_targets() if a.above_soswitch else coupled_targets()
    if a.targets:
        want = set(a.targets.split(","))
        tgs = [t for t in tgs if t.tag in want]
    allrows, per = [], {}
    for t in tgs:
        try:
            got = score_target(t, a.variant, a.emax, a.refine, a.chained, e_min, und)
        except NotImplementedError as exc:
            print(f"{t.tag:7s} SKIP {exc}")
            continue
        allrows += got["rows"]
        per[t.tag] = {**summarise(got["rows"]), "seconds": got["seconds"], "n_j": got["n_j"],
                      "ncoll": got["ncoll"], "kband": got["kband"], "deftype_D": got["deftype_D"]}
        s = per[t.tag]
        print(f"{t.tag:7s} ncoll={got['ncoll']} K={got['kband']:<4} nJ={got['n_j']:<3} "
              f"n={s['n']:<4} med={s['median']:.2e} p95={s['p95']:.2e} max={s['max']:.2e} "
              f"{'PASS' if s['pass'] else 'FAIL'}  {got['seconds']:.1f}s")
    if not allrows:
        print("nothing scored")
        return 1
    tot = summarise(allrows)
    byq = {q: summarise([x for x in allrows if x["quantity"] == q])
           for q in QUANTITIES if any(x["quantity"] == q for x in allrows)}
    print(f"\nA-inc overall: n={tot['n']} median={tot['median']:.2e} p95={tot['p95']:.2e} "
          f"max={tot['max']:.2e} tol={TOL:.0e} {'PASS' if tot['pass'] else 'FAIL'}")
    for q, s in byq.items():
        print(f"  {q:18s} n={s['n']:<4} med={s['median']:.2e} p95={s['p95']:.2e} max={s['max']:.2e}")
    worst = sorted(allrows, key=lambda x: -x["r"])[:8]
    print("  worst:")
    for w in worst:
        print(f"    {w['target']:7s} {w['quantity']:18s} E={w['e_inc_mev']:<8.4g} "
              f"port={w['port']:.5g} talys={w['talys']:.5g} r={w['r']:.2e}")
    Path(a.out).write_text(json.dumps(
        {"tolerance": TOL, "variant": a.variant, "e_max_mev": a.emax, "refine": a.refine,
         "chained": a.chained, "e_min_mev": e_min, "undeformed_spin_orbit": und,
         "overall": tot, "by_quantity": byq, "by_target": per,
         "worst": worst}, indent=1) + "\n")
    print(f"\nwrote {a.out}")
    return 0 if tot["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
