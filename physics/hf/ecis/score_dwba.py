"""A-direct for stage b: the ported DWBA against `directE*.out`'s own `xsdirdisc` and `xsgrcoll`
on every reference target and energy that has a direct block.

Metric of contract §6: r = |ln(port/TALYS)|. The tolerance is A-mult's 5e-2, the gate T12's
`direct` family is scored at -- these numbers are the input T12 currently injects from the dump.

Task: T13 (physics/hf/CONTRACT.md §7). Acceptance test: A-direct.

Usage:
    uv run python -m physics.hf.ecis.score_dwba                 # all targets, refine 4
    uv run python -m physics.hf.ecis.score_dwba --targets Fe056,U238 --refine 8
    uv run python -m physics.hf.ecis.score_dwba --coupled     # the incident-run rows instead
"""

from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path

import numpy as np
import torch

TOL = 5.0e-2
OUT = Path(__file__).resolve().parents[3] / "docs" / "results" / "hf-ecis-dwba-gate.json"


def score_case(target: str, e_inc_mev: float, variant: str = "default", refine: int = 4) -> list[dict]:
    """Rows for one (target, incident energy)."""
    from physics.hf.direct import reference as dref
    from physics.hf.direct.dwba import GR_LABELS
    from physics.hf.ecis.dwba import dwba_case, prepare_case
    from physics.hf.ecis.reference import incident_omp

    d = dref.dump(target, e_inc_mev, variant)
    src = incident_omp(target, variant)
    sel = (src.e_inc_mev - e_inc_mev).abs() < 1.0e-6
    if int(sel.sum()) != 1:
        raise KeyError(f"{target} has no incident OMP row at {e_inc_mev} MeV")
    omp = src.select(sel)
    case = prepare_case(omp, target, e_inc_mev)
    xs, xsgr = dwba_case(omp, case, refine=refine)
    ref = {int(d.level[i]): float(d.xs_mb[i]) for i in range(len(d.level))}
    rows = []
    for i, lev in enumerate(case.level_index.tolist()):
        want, got = ref.get(lev), float(xs[i])
        if want is None or want <= 0.0 or got <= 0.0:
            continue
        rows.append({"target": target, "e_inc_mev": float(e_inc_mev), "kind": "discrete",
                     "level": lev, "port": got, "talys": want,
                     "r": abs(math.log(got / want))})
    for n, k in enumerate(case.gr_which.tolist()):
        want, got = float(d.xsgrcoll_mb[k]), float(xsgr[n])
        if want <= 0.0 or got <= 0.0:
            continue
        rows.append({"target": target, "e_inc_mev": float(e_inc_mev), "kind": "giant",
                     "level": GR_LABELS[k], "port": got, "talys": want,
                     "r": abs(math.log(got / want))})
    return rows


def summarise(rows: list[dict]) -> dict:
    r = np.array([x["r"] for x in rows])
    return {"n": int(r.size), "median": float(np.median(r)), "p95": float(np.percentile(r, 95)),
            "max": float(r.max()), "pass": bool(np.percentile(r, 95) <= TOL)}


def score_coupled_direct(target: str, variant: str = "default", refine: int = 1) -> list[dict]:
    """The other half of `directE*.out`: the rows a coupled-channels target fills from the
    INCIDENT run, not from the DWBA one.

    `incidentread.f90:381-394` copies ECIS's coupled-channels inelastic cross sections into
    `xsdirdisc(k0, indexcc(i))` for the levels in the coupled band, which is why those rows have
    `deform == 0` and are invisible to `directecis` (board note `[T12 -> T10]`). They are
    `CoupledResult.sigma_direct_mb[:, k+1]` for `struct.cc_levels[k]`, so this scores the
    OFF-diagonal of the coupled-channels S-matrix -- something A-inc, which only sees sigma_tot,
    sigma_reac, sigma_el and the strength functions, does not reach. It runs across `soswitch`:
    the deformed spin-orbit changes the off-diagonal far more than the diagonal, so this is where
    a wrong `quan-257..305` would show first.

    TALYS: incidentread.f90:1 (incidentread)
    Test: A-direct
    """
    from physics.hf.direct import reference as dref
    from physics.hf.direct.prepare import case as direct_case
    from physics.hf.ecis.incident import incident_coupled
    from physics.hf.ecis.reference import coupled_band, incident_omp
    from physics.hf.talys_reference import REFERENCE_SET

    t = next(x for x in REFERENCE_SET if x.tag == target)
    band = coupled_band(t.Z, t.A)
    if band["colltype"] not in ("R", "V"):
        return []
    cc = direct_case(target, dref.energies_with_direct(target, variant)[-1]).struct.cc_levels
    if len(cc) == 0:
        return []
    energies = [
        e for e in dref.energies_with_direct(target, variant)
        if len(dref.dump(target, e, variant).level)
    ]
    if not energies:
        return []
    src = incident_omp(target, variant)
    sel = torch.zeros(src.e_inc_mev.shape, dtype=torch.bool)
    for e in energies:
        sel |= (src.e_inc_mev - e).abs() < 1.0e-6
    e_ax = src.e_inc_mev[sel]
    _inc, res = incident_coupled(
        src.select(sel), t.Z, t.A, e_ax, band, options=band["options"], refine=refine
    )
    rows = []
    for i, e in enumerate(e_ax.tolist()):
        ref = dref.dump(target, e, variant)
        want = {int(ref.level[n]): float(ref.xs_mb[n]) for n in range(len(ref.level))}
        for k, lev in enumerate(cc.tolist()):
            got, w = float(res.sigma_direct_mb[i, k + 1]), want.get(lev)
            if w is None or w <= 0.0 or got <= 0.0:
                continue
            rows.append({"target": target, "e_inc_mev": e, "kind": "coupled", "level": lev,
                         "port": got, "talys": w, "r": abs(math.log(got / w))})
    return rows


def main(argv=None) -> int:
    from physics.hf.direct import reference as dref
    from physics.hf.talys_reference import REFERENCE_SET

    ap = argparse.ArgumentParser()
    ap.add_argument("--variant", default="default")
    ap.add_argument("--refine", type=int, default=4)
    ap.add_argument("--targets", default="")
    ap.add_argument("--emin", type=float, default=0.0)
    ap.add_argument("--out", default=str(OUT))
    ap.add_argument("--coupled", action="store_true",
                    help="score the coupled-channels rows of directE*.out instead of the DWBA "
                         "ones (incidentread.f90:381-394)")
    a = ap.parse_args(argv)
    if a.coupled and a.out == str(OUT):
        a.out = str(OUT.with_name("hf-ecis-coupled-direct.json"))
    torch.set_num_threads(2)
    tags = a.targets.split(",") if a.targets else [t.tag for t in REFERENCE_SET]
    allrows, per = [], {}
    for tag in tags:
        rows, t0 = [], time.time()
        if a.coupled:
            rows = score_coupled_direct(tag, a.variant, a.refine)
        else:
            for e in dref.energies_with_direct(tag, a.variant):
                if e < a.emin:
                    continue
                if not len(dref.dump(tag, e, a.variant).level):
                    continue
                rows += score_case(tag, e, a.variant, a.refine)
        if not rows:
            print(f"{tag:7s} no direct rows")
            continue
        allrows += rows
        per[tag] = {**summarise(rows), "seconds": time.time() - t0}
        s = per[tag]
        print(f"{tag:7s} n={s['n']:<5} med={s['median']:.2e} p95={s['p95']:.2e} "
              f"max={s['max']:.2e} {'PASS' if s['pass'] else 'FAIL'}  {s['seconds']:.0f}s")
    if not allrows:
        print("nothing scored")
        return 1
    tot = summarise(allrows)
    byk = {k: summarise([x for x in allrows if x["kind"] == k])
           for k in ("discrete", "giant", "coupled") if any(x["kind"] == k for x in allrows)}
    print(f"\nA-direct overall: n={tot['n']} median={tot['median']:.2e} p95={tot['p95']:.2e} "
          f"max={tot['max']:.2e} tol={TOL:.0e} {'PASS' if tot['pass'] else 'FAIL'}")
    for k, s in byk.items():
        print(f"  {k:9s} n={s['n']:<5} med={s['median']:.2e} p95={s['p95']:.2e} max={s['max']:.2e}")
    worst = sorted(allrows, key=lambda x: -x["r"])[:10]
    print("  worst:")
    for w in worst:
        print(f"    {w['target']:7s} E={w['e_inc_mev']:<8.4g} {w['kind']:8s} {str(w['level']):5s} "
              f"port={w['port']:.5g} talys={w['talys']:.5g} r={w['r']:.2e}")
    Path(a.out).write_text(json.dumps(
        {"tolerance": TOL, "variant": a.variant, "refine": a.refine, "overall": tot,
         "by_kind": byk, "by_target": per, "worst": worst}, indent=1) + "\n")
    print(f"\nwrote {a.out}")
    return 0 if tot["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
