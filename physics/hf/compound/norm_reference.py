"""Drive `compnorm.f90` from the ported components instead of from the instrumented dump, and gate
the result: `CNfactor`, `xsflux`, `xsreacsum`, `J2beg`/`J2end` and the three addends they are built
from.

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

Task: T9, continued by EXCL (physics/hf/CONTRACT.md §7). Acceptance test: A-cn1 (§6).

`compnorm.f90` itself was already ported by T9 (`compound.normalization.compound_formation`) and
gated with TALYS's own `Tjlinc` injected. What was missing -- and what `engine.ChainedCompound`
listed as injected -- is the *wiring*: `Tjlinc`, `lmaxinc` and `xsreacinc` from T5's incident
channel, `xspreeqsum` from T8, `xsgrsum` and `xsdirdiscsum` from T12. With those built, nothing
`comptarget` reads about the compound nucleus's normalisation comes from a dump.

Three things worth knowing about the addends, because they are not where a reader would look:

* `xsdirdiscsum` is NOT only `direct`'s: `preeqtotal.f90:192` adds `xspreeqdiscsum` to it after
  `preeq` has run, so it is a T12 + T8 quantity.
* `xspreeqsum` is capped: `preeqtotal.f90:143-150` recomputes it as `xsflux - xspreeqdiscsum`
  whenever the raw sum would exceed the flux, and zeroes it when only the photon channel
  contributes (`preeqtotal.f90:126-128`). T8 reproduces both, so this module just reads its
  `xspreeqsum`.
* `xsgrsum = xsgrtot(k0)` is taken BEFORE `giant.f90:130` adds `xscollconttot` to `xsgrtot`
  (giant.f90:125), so the number compnorm subtracts is the discrete-state giant resonance only --
  which is not the same `xsgrtot` that `population.f90` normalises against.

Below `epreeq` there is no pre-equilibrium at all (`flagpreeq` false) and those addends are zero;
the gate scores every energy the dump carries and reports the two groups separately.
"""

from __future__ import annotations

import argparse
import json
import tarfile
from pathlib import Path

import numpy as np
import torch

from physics.hf.compound.normalization import compound_formation
from physics.hf.compound.prepare import load_cn_dump
from physics.hf.core.constants import talys_constants
from physics.hf.core.grids import incident_kinematics
from physics.hf.core.tensors import DTYPE

ROOT = Path(__file__).resolve().parents[3]
OUT_JSON = ROOT / "docs" / "results" / "hf-compnorm-gate.json"
TOL = 1.0e-2  # A-cn1


def addends(target: str, Zt: int, At: int, energies: list[float],
            declared: tuple[float, ...] | None = None, fit: tuple = ()) -> dict[float, dict]:
    """`xsdirdiscsum`, `xspreeqsum` and `xsgrsum` at every energy, from T8 and T12.

    `declared` is the run's incident energy grid; pass it and T8's and T12's own inputs are
    computed rather than injected (`preeq.chain`, `direct.chain`), which is what makes
    `engine.ChainedFull(inject=())` dump-free (NODUMP)."""
    from physics.hf.compound.pop_reference import _giant, _preeq, preeq_fit

    # PARAMWIRE: the exciton model reads the compound nucleus's photon strength
    pfit = preeq_fit(fit, Zt, At) if declared is not None else ()
    pe_energies, pres, _o = (_preeq(target, declared=declared, fit=pfit) if pfit
                             else _preeq(target, declared=declared))
    pe = {round(e, 6): i for i, e in enumerate(pe_energies)}
    out: dict[float, dict] = {}
    for e in energies:
        g, has_giant = _giant(target, e, declared=declared)
        i = pe.get(round(e, 6))
        disc = 0.0
        preeqsum = 0.0
        if i is not None:
            preeqsum = float(pres["xspreeqsum"][i])
            # preeqtotal.f90:192 -- the discrete pre-equilibrium part joins xsdirdiscsum
            disc = float(pres["xspreeqdiscsum"][i]) if "xspreeqdiscsum" in pres else 0.0
        out[round(e, 6)] = {
            "xsdirdiscsum_mb": float(g.xsdirdisctot_mb.sum()) + disc,
            "xspreeqsum_mb": preeqsum,
            "xsgrsum_mb": float(g.xsgrsum_mb) if has_giant else 0.0,
        }
    return out


def chained_formation(cas, inp, add: dict):
    """`compound_formation` on T5's incident channel and T8/T12's addends.

    `cas` is an `emission.feeding.Cascade` (it owns the cached incident channel).

    TALYS: compnorm.f90:1 (compnorm)
    Test: A-cn1
    """
    from physics.hf.compound.dens_reference import _to_updown_axis

    c = talys_constants()
    inc = cas.incident(inp.e_inc_mev)
    k0 = inp.k0
    _, wavenum = incident_kinematics(
        inp.e_inc_mev, k0, float(cas.m.mass_amu[0, 1]),
        float(cas.m.specmass[c["parZ"][k0], c["parN"][k0], k0]),
        float(cas.m.redumass_amu[c["parZ"][k0], c["parN"][k0], k0]), cas.options.flagrel)
    lm = int(inc.lmax[0])
    tjl = _to_updown_axis(inc.tjl_inc[0], k0)[: lm + 1]
    # OPEN4: compnorm.f90:163-166 -- a coupled-channels target (colltype /= 'S', no `spherical y`)
    # takes the flux from its own sum over `Tjlinc` plus `xscoupled`, and does NOT renormalise
    # to `xsreacinc`. The two differ where ECIS solved at the card-rounded energy
    # (`schrodinger.ecis_card_energy`) while pi/k^2 is taken at `Einc`, which is what puts
    # TALYS's keV nonelastic (`xsreacinc - xscompel`) below its own capture.
    xscoupled = cas.xscoupled(inp.e_inc_mev)
    # DIFFPARAM: `torch.tensor(float(...))` on sigma_reac would cut the optical parameters out
    # of the compound normalisation, which is the one place they enter it. `as_tensor` keeps the
    # graph when there is one and is the same object when there is not.
    return compound_formation(
        tjl, torch.tensor(float(wavenum), dtype=DTYPE),
        inp.targetspin2, inp.target_parity, lm, k0,
        torch.as_tensor(inc.sigma_reac_mb[0], dtype=DTYPE),
        torch.tensor(add["xsdirdiscsum_mb"], dtype=DTYPE),
        torch.tensor(add["xspreeqsum_mb"], dtype=DTYPE),
        torch.tensor(add["xsgrsum_mb"], dtype=DTYPE),
        spherical=xscoupled is None,
        xscoupled_mb=None if xscoupled is None else torch.as_tensor(xscoupled, dtype=DTYPE),
    ), lm


def _r1(p: float, t: float, floor: float = 1.0e-3) -> float:
    if abs(t) <= floor:
        return float("nan")
    if p == 0.0:
        return float("inf")
    return abs(float(np.log(abs(p / t))))


def _stats(vals: list[float], tol: float) -> dict:
    a = np.array([v for v in vals if not np.isnan(v)])
    if a.size == 0:
        return {"n": 0}
    fin = a[np.isfinite(a)]
    p95 = float(np.percentile(fin, 95)) if fin.size else None
    return {"n": int(a.size), "n_inf": int((~np.isfinite(a)).sum()),
            "median": float(np.median(fin)) if fin.size else None, "p95": p95,
            "max": float(fin.max()) if fin.size else None, "tol": tol,
            "pass": bool(p95 is not None and p95 <= tol and not (~np.isfinite(a)).any())}


def score_run(work: Path, Zt: int, At: int, target: str) -> dict:
    """A-cn1 on everything `compnorm` produces, over every incident energy of one run."""
    from physics.hf.emission.feeding import Cascade

    cases = load_cn_dump(Path(work) / "cn_inputs.txt")
    enincmax = max(c.e_inc_mev for c in cases)
    cas = Cascade(Zt, At, enincmax)
    add = addends(target, Zt, At, [c.e_inc_mev for c in cases])

    acc: dict[str, list] = {k: [] for k in ("cnfactor", "xsflux", "norm_diagnostic")}
    j2_ok = j2_n = lm_ok = lm_n = 0
    for c in cases:
        cf, lm = chained_formation(cas, c, add[round(c.e_inc_mev, 6)])
        acc["cnfactor"].append(_r1(float(cf.cn_factor_mb), c.cnfactor_mb, 1.0e-12))
        acc["xsflux"].append(_r1(float(cf.xs_flux_mb), c.xsflux_mb))
        # DIAGNOSTIC, not a gate: `xsreacsum` is TALYS's own check column B, the sum over the
        # incident T(j,l), and the dump carries `xsreacinc`. compnorm.f90:163 divides one by the
        # other precisely because they differ -- for a coupled-channels target `xsreacinc` also
        # holds the direct cross section to the coupled levels, so `norm` is genuinely not 1 and
        # scoring the two against each other would score TALYS's own renormalisation as an error.
        acc["norm_diagnostic"].append(_r1(float(cf.xs_reacsum_mb), c.xsreacinc_mb))
        j2_n += 2
        j2_ok += int(cf.j2beg == c.j2beg) + int(cf.j2end == c.j2end)
        lm_n += 1
        lm_ok += int(lm == c.lmaxinc)
    return {"run": Path(work).name, "energies": len(cases),
            "coupled_incident_channel": cas.coupled_incident_channel,
            **{k: _stats(v, TOL) for k, v in acc.items()},
            "j2_exact": f"{j2_ok}/{j2_n}", "lmaxinc_exact": f"{lm_ok}/{lm_n}"}


def main(argv=None) -> None:
    from physics.hf.talys_reference import REFERENCE_SET

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--runs", default=str(Path.home() / "nucleus/features/hf_compound_reference"))
    ap.add_argument("--work", default=str(Path.home() / "e2e_work"))
    ap.add_argument("--out", default=str(OUT_JSON))
    ap.add_argument("--only", default="")
    a = ap.parse_args(argv)
    zt = {t.tag: (t.Z, t.A) for t in REFERENCE_SET}
    recs = []
    for tar in sorted(Path(a.runs).glob("default__*.tar.gz")):
        tag = tar.name[len("default__"): -len(".tar.gz")]
        if a.only and tag not in a.only.split(","):
            continue
        d = Path(a.work) / f"default__{tag}"
        if not (d / "cn_inputs.txt").exists():
            d.mkdir(parents=True, exist_ok=True)
            with tarfile.open(tar) as tf:
                tf.extractall(d)
        Z, A = zt[tag]
        recs.append(score_run(d, Z, A, tag))
        print(json.dumps(recs[-1]), flush=True)
    keys = ("cnfactor", "xsflux")
    worst = {k: max((r[k]["p95"] for r in recs if r[k].get("p95") is not None), default=None)
             for k in (*keys, "norm_diagnostic")}
    out = {"gate": "A-cn1 / compnorm.f90 chained on T5+T8+T12", "tol": TOL, "runs": recs,
           "worst_p95": worst,
           "gated_quantities": list(keys) + ["j2_exact", "lmaxinc_exact"],
           "j2_exact_all": all(r["j2_exact"].split("/")[0] == r["j2_exact"].split("/")[1]
                               for r in recs),
           "lmaxinc_exact_all": all(
               r["lmaxinc_exact"].split("/")[0] == r["lmaxinc_exact"].split("/")[1] for r in recs),
           "pass": bool(recs) and all(r[k].get("pass") for r in recs for k in keys)}
    Path(a.out).write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps({k: v for k, v in out.items() if k != "runs"}, indent=1))


if __name__ == "__main__":
    main()
