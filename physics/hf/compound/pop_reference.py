"""Gate driver for `population.f90`: build its inputs from the ported T8 / T12 components and
score `preeqpopex` against TALYS's own, dumped by `talys_instrument/cndump.f90` (`PEPX`).

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

Task: T9, continued by EXCL (physics/hf/CONTRACT.md §7). Acceptance test: A-cn1 (§6),
tolerance 1e-2.

What is built and what is injected, so the number below is read correctly. Built: the whole of
`population.f90` (this task), `xspreeq`/`xspreeqtot` from T8's exciton model, `xsgr`/`xsgrtot` from
T12's giant-resonance model, the emission grid and `ebegin`/`eend` from T1's grid code. Injected:
the residuals' excitation grids (`Ex`, `deltaEx`, `Nlast`, `maxex`, `S`), which come from the same
dump the reference does and are covered by gates A-grid and A-struct; T8's own `xsreac` and T12's
own DWBA cross sections, which those tasks inject and which are not this task's seam.

`flagpreeq` is false below `epreeq`, so TALYS never calls `population` at the low energies and
there is nothing to score there -- the dump carries `PEPX` at exactly the energies T8 covers.
"""

from __future__ import annotations

import argparse
import json
import tarfile
from functools import lru_cache
from pathlib import Path

import numpy as np
import torch

from physics.hf.compound.population import PopResidual, PopulationInputs, population
from physics.hf.compound.prepare import CompoundInputs, load_cn_dump
from physics.hf.core.constants import talys_constants
from physics.hf.core.grids import emission_end, incident_kinematics, total_energy
from physics.hf.preeq.multi import NUMPARX
from physics.hf.core.tensors import DTYPE
from physics.hf.emission.score import POP_FLOOR_MB, _r

ROOT = Path(__file__).resolve().parents[3]
OUT_JSON = ROOT / "docs" / "results" / "hf-population-gate.json"
TOL = 1.0e-2  # A-cn1 / A-pe: this is T8's and T12's spectrum tolerance, not a new one
# §2's pre-registered floors: 1e-3 mb for cross sections, 1e-6 mb for populations. `preeqpopex`
# is a population, so the population floor applies.
FLOOR_MB = POP_FLOOR_MB


@lru_cache(maxsize=16)
def _preeq(target: str, variant: str = "default",
           declared: tuple[float, ...] | None = None, fit: tuple = ()):
    """T8's `xspreeq(type, nen)`, `xspreeqtot(type)` and `xsstep2` at every energy it covers.

    Cached: `norm_reference.addends` and `feed_reference._preeq_of` both need it for the same
    target, and it is the most expensive run-scoped set-up of the chain. Callers only read it.

    `declared` is the run's incident energy grid. Pass it and the whole set-up is CHAINED
    (NODUMP): the energies come from `flagpreeq` rather than from the list of `exciton*.out`
    files, `xsreac` from T5, `xsreacinc` from T5's incident channel, and `xsflux`/`xsdirdisc`
    from T12/T13 -- see `preeq.chain`. `None` keeps the injected arm, which is what A-pe scores.
    """
    from physics.hf import reference as ref
    from physics.hf.input.defaults import default_options
    from physics.hf.input.nuclides import coulomb_barriers
    from physics.hf.preeq.exciton import preequilibrium
    from physics.hf.preeq.prepare import parse_target, prepare

    # PARAMWIRE: `fit` is the part of the run's parameter set this set-up reads
    # (`preeq_fit`: the compound nucleus and the binary residuals), and part of the key

    chained = declared is not None
    if chained:
        from physics.hf.preeq.chain import (
            energy_subset,
            incident_reaction_xs,
            preeq_energies,
        )

        Z, A = parse_target(target)
        # `preeq.f90` runs at every declared energy above `epreeq`; SPEEDP lets a run that
        # computes a SUBSET of the declared grid say so (`preeq.chain.set_energy_subset`), and
        # then the exciton model is batched over that subset instead of over all of them.
        #
        # `direct_grid` is the DECLARED grid, not the pre-equilibrium subset of it. That axis is
        # read by `direct.chain._coupled` (which stitches `soswitch` across it) and by
        # `direct.prepare.case` (which resolves the onsets on it), and `directecis.f90` /
        # `incidentecis.f90` run one deck per DECLARED incident energy -- the pre-equilibrium
        # list only decides where `preeq.f90` itself runs. Handing the subset here was a NODUMP
        # wiring artefact: it made `engine._BuiltInputs` and the flux ask `chained_direct` two
        # different questions about the same (target, energy), so a coupled target solved its
        # whole incident deck twice and every shared energy solved its DWBA twice. On a
        # `colltype R`/`V` target the two answers differ in the last bits of the coupled
        # stitch (Ca-40: 1.8e-14 in `xsdirdisc`); a spherical one is bit-identical.
        grid = preeq_energies(Z, A, declared)
        sub = energy_subset(Z, A, declared)
        energies = ([e for e in grid if round(float(e), 6) in sub] if sub is not None else grid)
        if not energies:
            # Every energy this run computes is below `epreeq`, so `preeq.f90` never runs: the
            # empty index map its three callers get makes each of them take the branch it already
            # has for an energy the exciton model does not cover. (`grid` may still be non-empty
            # -- the DECLARED grid reaches above the onset -- which is why this is not the same
            # as `flagpreeq` being false for the whole run.)
            return [], {}, default_options(Z, A)
        inp, hdr = prepare(target, variant, energies, chained=True,
                           enincmax_mev=max(declared), direct_grid=tuple(declared), fit=fit)
        reac = incident_reaction_xs(Z, A, declared)
    else:
        inp, hdr = prepare(target, variant)
        energies = hdr["energies"]
        inc = ref.incident_scalars(target, variant)
        reac = {round(float(r.e_inc_mev), 6): float(r.sigma_reac_omp_mb)
                for _, r in inc.iterrows()}
    o, p = hdr["options"], hdr["params"]
    xsr = torch.tensor([reac[round(e, 6)] for e in energies], dtype=DTYPE)
    res = preequilibrium(inp, o, p, hdr["discrete"], coulbar_mev=coulomb_barriers(o),
                         xsreacinc_mb=xsr)
    return energies, res, o


def preeq_fit(fit, Zt: int, At: int) -> tuple:
    """The entries of a parameter set the chained exciton set-up reads: the compound nucleus's
    (its photon strength, through `xsreac(0)`) and the seven binary residuals' (their pairing)."""
    from physics.hf.core.constants import talys_constants
    from physics.hf.density.overrides import fit_subset

    if not fit:
        return ()
    c = talys_constants()
    return fit_subset(fit, [(Zt - c["parZ"][t], At + 1 - c["parA"][t]) for t in range(7)])


def _giant(target: str, e_inc_mev: float, variant: str = "default",
           declared: tuple[float, ...] | None = None):
    """T12's `xsgr(k0, nen)` and `xsgrtot(k0)`; `giant.f90:113-174` fills type `k0` only.

    With `declared` (the run's incident energy grid) the DWBA, the coupled-channels direct cross
    sections and `flaggiant` are all computed (`direct.chain`); without it they are injected from
    `directE*.out`, which is what A-mult scores.
    """
    from physics.hf.direct import dwba as D
    from physics.hf.direct import prepare as P
    from physics.hf.direct import reference as dref

    if declared is not None:
        from physics.hf.preeq.chain import chained_direct, target_tag

        cs0 = P.case(target, e_inc_mev, declared)
        del cs0  # built for its cache; `chained_direct` keys on (Z, A, declared)
        Z, A = P.parse_target(target)
        assert target_tag(Z, A) == target
        return chained_direct(Z, A, declared)[round(float(e_inc_mev), 6)]
    cs = P.case(target, e_inc_mev)
    lv = D.direct_levels(cs.struct, cs.eninccm_mev, cs.eoutdis_mev, e_inc_mev, cs.options.k0)
    gr = D.giant_resonance_parameters(cs.struct, cs.params)
    dump = dref.dump(target, e_inc_mev, variant)
    xs, xscc, xsgrcoll = P.injected_cross_sections(cs, lv, dump)
    res = D.direct(
        cs.struct, gr, lv, xs, xsgrcoll, cs.eoutdis_mev, cs.eninccm_mev,
        torch.as_tensor(cs.egrid_mev, dtype=DTYPE),
        torch.as_tensor(cs.deltae_mev, dtype=DTYPE), cs.grid_mask, xscc,
        flaggiant=dump.has_giant, elwidth_mev=float(cs.params.at("elwidth")))
    return res, dump.has_giant


def _xsstep2_by_type(xs: np.ndarray, states, maxpar: int, E: int) -> dict[int, np.ndarray]:
    """T8's per-exciton-state spectra folded onto TALYS's `xsstep2(type, ppi, pnu, nen)` axes.

    TALYS: exciton2.f90:1 (exciton2) -- the array population.f90:210 reads
    Test: E2E
    """
    out = {t: np.zeros((maxpar + 1, maxpar + 1, E)) for t in (1, 2)}
    for s in range(xs.shape[0]):
        ppi, pnu = int(states.ppi[s]), int(states.pnu[s])
        if ppi > maxpar or pnu > maxpar:
            continue
        for t in (1, 2):
            out[t][ppi, pnu] += np.asarray(xs[s, t, :E], float)
    return out


def pop_inputs(inp: CompoundInputs, Zt: int, At: int, enincmax_mev: float, target: str,
               xspreeq: np.ndarray, xspreeqtot: np.ndarray, xsstep2: np.ndarray | None,
               options, states=None) -> PopulationInputs:
    """`PopulationInputs` for one incident energy.

    TALYS: population.f90:1 (population)
    Test: A-cn1
    """
    from physics.hf.compound.dens_reference import run_grid

    c = talys_constants()
    rg = run_grid(Zt, At, enincmax_mev)
    k0 = inp.k0
    eninccm, _ = incident_kinematics(
        inp.e_inc_mev, k0, float(rg.m.mass_amu[0, 1]),
        float(rg.m.specmass[c["parZ"][k0], c["parN"][k0], k0]),
        float(rg.m.redumass_amu[c["parZ"][k0], c["parN"][k0], k0]), rg.options.flagrel)
    ecomp = total_energy(eninccm, rg.s0[k0], 0.0)
    eend, _ = emission_end(rg.egrid, rg.maxen, ecomp, {t: rg.s0[t] for t in range(7)},
                           rg.ebegin, {t: False for t in range(7)})
    E = rg.maxen + 1
    gres, has_giant = _giant(target, inp.e_inc_mev)
    xsgr = {k0: np.asarray(gres.xsgr_mb.detach().numpy(), float)[:E]}
    xsgrtot = {k0: float(gres.xsgrtot_mb)}
    residuals = {}
    for t, r in sorted(inp.residuals.items()):
        residuals[t] = PopResidual(
            type=t, nlast=min(r.nlast, r.maxex), maxex=r.maxex, sep_mev=r.sep_mev,
            ex_mev=np.asarray(r.ex_mev, float), dex_mev=np.asarray(r.dex_mev, float))
    flagmulpre = not (inp.e_inc_mev < options.emulpre_mev)
    maxpar = int(getattr(options, "maxpar", NUMPARX))  # preeqinit.f90:64-65, numexc / 2
    return PopulationInputs(
        etotal_mev=float(ecomp), egrid_mev=rg.egrid, ebegin=dict(rg.ebegin),
        eend={t: min(eend[t], rg.maxen) for t in range(7)}, residuals=residuals,
        xspreeq_mb={t: np.asarray(xspreeq[t], float)[:E] for t in range(7)},
        xspreeqtot_mb={t: float(xspreeqtot[t]) for t in range(7)},
        flaggiant=has_giant and options.flaggiant0, xsgr_mb=xsgr, xsgrtot_mb=xsgrtot,
        pespinmodel=options.pespinmodel, flagmulpre=flagmulpre, flag2comp=options.flag2comp,
        maxpar=maxpar, ppi0=0 if c["parZ"][k0] == 0 else 1, pnu0=1 if k0 == 1 else 0,
        xsstep2_mb=(_xsstep2_by_type(xsstep2, states, maxpar, E)
                    if (flagmulpre and xsstep2 is not None and states is not None) else {}),
    )


def _stats(vals: list[np.ndarray], tol: float) -> dict:
    if not vals:
        return {"n": 0}
    r = np.concatenate([v.ravel() for v in vals])
    r = r[~np.isnan(r)]
    if r.size == 0:
        return {"n": 0}
    fin = r[np.isfinite(r)]
    return {"n": int(r.size), "n_inf": int((~np.isfinite(r)).sum()),
            "median": float(np.median(fin)) if fin.size else None,
            "p95": float(np.percentile(fin, 95)) if fin.size else None,
            "max": float(fin.max()) if fin.size else None,
            "tol": tol, "pass": bool(fin.size and np.percentile(fin, 95) <= tol
                                     and not (~np.isfinite(r)).any())}


def score_run(work: Path, Zt: int, At: int, target: str) -> dict:
    """A-cn1 on `preeqpopex` over every flagpreeq energy of one instrumented run."""
    cases = load_cn_dump(Path(work) / "cn_inputs.txt")
    enincmax = max(c.e_inc_mev for c in cases)
    energies, pres, options = _preeq(target)
    by_e = {round(e, 6): i for i, e in enumerate(energies)}
    rs, checks = [], []
    for c in cases:
        if not c.preeqpopex_mb:
            continue
        i = by_e.get(round(c.e_inc_mev, 6))
        if i is None:
            continue
        inp = pop_inputs(
            c, Zt, At, enincmax, target,
            pres["xspreeq"][i].detach().numpy(), pres["xspreeqtot"][i].detach().numpy(),
            pres["xsstep2"][i].detach().numpy() if "xsstep2" in pres else None, options,
            pres.get("states"))
        got = population(inp)
        ref = {}
        for (t, nex), v in c.preeqpopex_mb.items():
            ref.setdefault(t, {})[nex] = v
        for t, col in sorted(ref.items()):
            n = max(col) + 1
            g = np.zeros(n)
            gg = got.preeqpopex_mb.get(t)
            if gg is not None:
                g[: min(n, len(gg))] = gg[: min(n, len(gg))]
            tal = np.zeros(n)
            for nex, v in col.items():
                tal[nex] = v
            rs.append(_r(g, tal, FLOOR_MB))
        checks.append(float(sum(got.xscheck_mb.values())))
    return {"run": Path(work).name, "energies": len(rs) and len(checks),
            "preeqpopex": _stats(rs, TOL)}


def main(argv=None) -> None:
    from physics.hf.talys_reference import REFERENCE_SET

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--runs", default=str(Path.home() / "nucleus/features/hf_compound_reference"))
    ap.add_argument("--work", default=str(Path.home() / "e2e_work"))
    ap.add_argument("--out", default=str(OUT_JSON))
    ap.add_argument("--only", default="")
    a = ap.parse_args(argv)
    zt = {t.tag: (t.Z, t.A) for t in REFERENCE_SET}
    work = Path(a.work)
    work.mkdir(parents=True, exist_ok=True)
    recs = []
    for tar in sorted(Path(a.runs).glob("*.tar.gz")):
        name = tar.name[: -len(".tar.gz")]
        variant, _, tag = name.partition("__")
        if variant != "default" or (a.only and tag not in a.only.split(",")):
            continue
        d = work / name
        if not (d / "cn_inputs.txt").exists():
            with tarfile.open(tar) as tf:
                tf.extractall(d)
        Z, A = zt[tag]
        recs.append(score_run(d, Z, A, tag))
        print(json.dumps(recs[-1]), flush=True)
    p95 = [r["preeqpopex"]["p95"] for r in recs if r["preeqpopex"].get("p95") is not None]
    out = {"gate": "A-cn1 / population.f90", "tol": TOL, "runs": recs,
           "worst_p95": max(p95) if p95 else None,
           "n_inf": sum(r["preeqpopex"].get("n_inf", 0) for r in recs),
           "pass": bool(recs) and all(r["preeqpopex"].get("pass") for r in recs)}
    Path(a.out).write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps({k: v for k, v in out.items() if k != "runs"}, indent=1))


if __name__ == "__main__":
    main()
