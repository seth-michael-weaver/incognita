"""Gate driver for the multiple-emission feeding chain: compute `feedexcl`/`popexcl` from the
ported components and score them against TALYS's own, dumped by
`emission/talys_instrument/chdump.f90`.

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

Task: T10, continued by EXCL (physics/hf/CONTRACT.md §7). Acceptance test: A-mult (§6),
tolerance 0.05.

`feedexcl(Zcomp, Ncomp, type, nex, nexout)` is the only quantity `channels.f90` reads that no TALYS
output file carries, which is why T10 instrumented it. Until this task it was also the only one the
port could not compute: `multiple_emission` (T10) had the bookkeeping and `compound_decay` (T9) had
the physics, and nothing built the per-nucleus grids that join them. `emission.feeding.Cascade`
does; this module scores the result.

Injected here and named, so the number is read for what it is: the mother populations of the
binary residuals come from `binary` (T10) on `comptarget` (T9) or on the dump, depending on
`--chained`; `multipreeq2.f90` is unported so `Einc >= emulpre` (20 MeV) is reported separately;
the fission transmission is T11's, injected per (J, parity) where `flagfission`.
"""

from __future__ import annotations

import argparse
import json
import tarfile
import time
from functools import lru_cache
from pathlib import Path

import numpy as np

from physics.hf.core.constants import talys_constants
from physics.hf.core.grids import incident_kinematics, total_energy
from physics.hf.emission.binary import BinaryState, binary
from physics.hf.emission.dumps import ChannelInputs, load_binary_dump, load_channel_dump
from physics.hf.emission.feeding import PARN as PARN_
from physics.hf.emission.feeding import PARZ as PARZ_
from physics.hf.emission.feeding import Cascade
from physics.hf.emission.multiple import multiple_emission
from physics.hf.emission.score import POP_FLOOR_MB, _r
from physics.hf.preeq.multi import NUMPARX

PARSYM_ = "gnpdtha"  # constants.f90: parsym, types 0..6

ROOT = Path(__file__).resolve().parents[3]
OUT_JSON = ROOT / "docs" / "results" / "hf-feeding-gate.json"
TOL = 0.05  # A-mult, contract §6
# §2's pre-registered floors: 1e-3 mb for cross sections, 1e-6 mb for populations. `feedexcl` and
# `popexcl` are flux per bin, i.e. population-class, so the population floor applies.
FLOOR_MB = POP_FLOOR_MB


def etotal_of(Zt: int, At: int, enincmax_mev: float, e_inc_mev: float, k0: int) -> float:
    """`Etotal`, the compound system's total energy at one incident energy (energies.f90)."""
    from physics.hf.compound.dens_reference import run_grid

    c = talys_constants()
    rg = run_grid(Zt, At, enincmax_mev)
    eninccm, _ = incident_kinematics(
        e_inc_mev, k0, float(rg.m.mass_amu[0, 1]),
        float(rg.m.specmass[c["parZ"][k0], c["parN"][k0], k0]),
        float(rg.m.redumass_amu[c["parZ"][k0], c["parN"][k0], k0]), rg.options.flagrel)
    return float(total_energy(eninccm, rg.s0[k0], 0.0))


@lru_cache(maxsize=16)
def _preeq_of(target: str, declared: tuple[float, ...] | None = None, fit: tuple = ()):
    """T8's spectra for one target, cached: `prepare` + `preequilibrium` is the expensive part.

    `declared` (the run's incident energy grid) switches the whole set-up to the chained arm --
    no `cross_<p>.tot`, no `directE*.out`, no `exciton*.out` file list (NODUMP)."""
    from physics.hf.compound.pop_reference import _preeq

    # `declared` only when given: HEAD's `pop_reference._preeq` predates NODUMP's keyword
    kw = {} if declared is None else {"declared": declared}
    if fit:  # PARAMWIRE: `pop_reference.preeq_fit` of the run's parameter set
        kw["fit"] = fit
    energies, res, options = _preeq(target, **kw)
    return {round(e, 6): i for i, e in enumerate(energies)}, res, options


@lru_cache(maxsize=512)
def _giant_of(target: str, e_inc_mev: float, declared: tuple[float, ...] | None = None):
    from physics.hf.compound.pop_reference import _giant

    kw = {} if declared is None else {"declared": declared}
    return _giant(target, e_inc_mev, **kw)


def pop_inputs_of(cas: Cascade, binp, target: str, etotal_mev: float, add: dict,
                  declared: tuple[float, ...] | None = None):
    """`PopulationInputs` for one incident energy, built off the Cascade's own grids.

    The dump-driven twin is `compound.pop_reference.pop_inputs`, which is what the A-cn1 gate
    scores; this one takes the same physics from the same modules but reads `Ex`/`deltaEx`/`Nlast`
    off `Cascade.spec`, so the full chain needs no compound-nucleus dump.

    TALYS: population.f90:1 (population)
    Test: A-cn1 / E2E
    """
    from physics.hf.compound.pop_reference import _xsstep2_by_type
    from physics.hf.compound.population import PopResidual, PopulationInputs
    from physics.hf.core.grids import emission_end

    from physics.hf.compound.pop_reference import preeq_fit

    del add  # the addends are compnorm's; population needs the spectra themselves
    pfit = preeq_fit(cas.fit, cas.Zt, cas.At) if declared is not None else ()
    pe, pres, options = (_preeq_of(target, declared, pfit) if pfit
                         else _preeq_of(target, declared))
    i = pe.get(round(binp.e_inc_mev, 6))
    E = cas.rg.maxen + 1
    eend, _ = emission_end(cas.rg.egrid, cas.rg.maxen, etotal_mev,
                           {t: cas.rg.s0[t] for t in range(7)}, cas.rg.ebegin,
                           {t: False for t in range(7)})
    st0 = cas.new_energy(etotal_mev)
    cas.propagate_exmax(st0, 0, 0)
    sp = cas.spec(st0, 0, 0)
    residuals = {}
    for t in range(7):
        d = cas.spec(st0, PARZ_[t], PARN_[t])
        residuals[t] = PopResidual(
            type=t, nlast=d.nlast_grid, maxex=d.maxex, sep_mev=sp.sep_mev[t],
            ex_mev=d.ex_mev, dex_mev=d.dex_mev)
    if i is None:  # below epreeq TALYS never calls population at all
        zero = np.zeros(E)
        return PopulationInputs(
            etotal_mev=etotal_mev, egrid_mev=cas.rg.egrid, ebegin=dict(cas.rg.ebegin),
            eend={t: min(int(eend[t]), cas.rg.maxen) for t in range(7)}, residuals=residuals,
            xspreeq_mb={t: zero for t in range(7)}, xspreeqtot_mb={t: 0.0 for t in range(7)},
            flaggiant=False)
    gres, has_giant = _giant_of(target, binp.e_inc_mev, declared)
    xspreeq = pres["xspreeq"][i].detach().numpy()
    xstep2 = pres["xsstep2"][i].detach().numpy() if "xsstep2" in pres else None
    flagmulpre = not (binp.e_inc_mev < options.emulpre_mev)
    # preeqinit.f90:64-65: maxpar = maxexc / 2 = numexc / 2 = 6, NOT 5 -- with 5 the
    # (6, .) and (., 6) particle-hole columns `multipreeq2` reads are simply missing.
    maxpar = int(getattr(options, "maxpar", NUMPARX))
    return PopulationInputs(
        etotal_mev=etotal_mev, egrid_mev=cas.rg.egrid, ebegin=dict(cas.rg.ebegin),
        eend={t: min(int(eend[t]), cas.rg.maxen) for t in range(7)}, residuals=residuals,
        xspreeq_mb={t: np.asarray(xspreeq[t], float)[:E] for t in range(7)},
        xspreeqtot_mb={t: float(pres["xspreeqtot"][i][t]) for t in range(7)},
        flaggiant=has_giant and options.flaggiant0,
        xsgr_mb={cas.k0: np.asarray(gres.xsgr_mb.detach().numpy(), float)[:E]},
        xsgrtot_mb={cas.k0: float(gres.xsgrtot_mb)},
        pespinmodel=options.pespinmodel, flagmulpre=flagmulpre, flag2comp=options.flag2comp,
        maxpar=maxpar,
        xsstep2_mb=(_xsstep2_by_type(xstep2, pres.get("states"), maxpar, E)
                    if (flagmulpre and xstep2 is not None and pres.get("states") is not None)
                    else {}),
    )


def chain_case(cas: Cascade, binp, cinp: ChannelInputs, *, bstate=None) -> tuple[dict, dict]:
    """Run `binary` then the feeding chain for one incident energy.

    Returns (`MultipleResult`-as-dict of feedexcl, popexcl) keyed the way the dump is.

    TALYS: multiple.f90:1 (multiple)
    Test: A-mult
    """
    b = binary(binp, bstate)
    inc = cas.incident(binp.e_inc_mev)
    st = cas.new_energy(etotal_of(cas.Zt, cas.At, cas.enincmax, binp.e_inc_mev, binp.k0),
                        lmaxinc=int(inc.lmax[0]), e_inc_mev=binp.e_inc_mev)
    # exgrid(0, 0) runs before the multiple loop (talysreaction.f90:116)
    cas.propagate_exmax(st, 0, 0)
    seed = {}
    for t in sorted(binp.grids):
        if t == 0:
            continue
        seed[t] = (b.xspop_mb[t].detach().numpy(), b.xspopex_mb[t].detach().numpy(),
                   float(b.xspopnuc_mb[t].sum()) if b.xspopnuc_mb[t].dim() else
                   float(b.xspopnuc_mb[t]))
    seed[0] = (b.xspop_mb[0].detach().numpy(), b.xspopex_mb[0].detach().numpy(),
               float(np.asarray(b.xspopex_mb[0].detach().numpy()).sum()))
    nuclei = cas.populations(st, cinp.maxz, cinp.maxn, seed)
    # every nucleus the loop reaches propagates Exmax to its own daughters first
    for zc in range(cinp.maxz + 1):
        for nc in range(cinp.maxn + 1):
            if (zc, nc) in nuclei:
                cas.propagate_exmax(st, zc, nc)
    nuclei = cas.populations(st, cinp.maxz, cinp.maxn, seed)
    # multiple pre-equilibrium is live at `Einc >= emulpre` only, and it needs `population.f90`'s
    # `xspopph2` for the two binary residuals to start from (multiple.f90:549).
    mpe = None
    if not (binp.e_inc_mev < cas.options.emulpre_mev):
        from physics.hf.compound.population import population
        from physics.hf.engine import _seed_mulpre

        etot = etotal_of(cas.Zt, cas.At, cas.enincmax, binp.e_inc_mev, binp.k0)
        _seed_mulpre(nuclei, population(pop_inputs_of(cas, binp, _tag_of(cas), etot, None)))
        if any(n.mulpre for n in nuclei.values()):
            mpe = lambda zc, nc, nex: cas.mpe(  # noqa: E731
                st, nuclei, zc, nc, nex, etotal_mev=etot)
    xsb = {t - 1: float(v) for t, v in enumerate(binp.xsbinary_mb)} if (
        binp.xsbinary_mb is not None) else {}
    res = multiple_emission(
        nuclei, lambda zc, nc, nex, *, dmulti=0.0: cas.decay(
            st, nuclei, zc, nc, nex, popeps_mb=binp.popeps_mb, flagfission=False,
            dmulti=dmulti),
        popeps_mb=binp.popeps_mb, maxz=cinp.maxz, maxn=cinp.maxn, k0=binp.k0,
        xsreacinc_mb=cinp.xsreacinc_mb, xsbinary_mb=xsb,
        feedbinary_mb=b.feedbinary_mb, flagfission=cinp.flagfission, mpe=mpe)
    return res.feedexcl_mb, res.popexcl_mb


def _tag_of(cas: Cascade) -> str:
    """The reference-set tag of a cascade's target, which `pop_inputs_of` needs to find T8's
    pre-equilibrium run and T12's giant-resonance addend."""
    from physics.hf.talys_reference import REFERENCE_SET

    for t in REFERENCE_SET:
        if (t.Z, t.A) == (cas.Zt, cas.At):
            return t.tag
    raise KeyError(f"no reference-set tag for Z={cas.Zt} A={cas.At}")


def _tally_inf(inf: dict, cas: Cascade, e_inc_mev: float, k, ns, t: int,
               keys: list, port: np.ndarray, talys: np.ndarray) -> None:
    """Break the `n_inf` cells of `feedexcl` down by (residual nucleus, ejectile).

    `_r` calls a cell infinite in two opposite situations and lumping them hides which one it is:
    TALYS above the 1e-6 mb population floor where the port returns zero (**missing** flux), and
    TALYS below the floor where the port is above it (**spurious** flux). Both are counted here,
    with the mother/daughter bin indices of the first few so a cell can be reproduced directly.

    TALYS: multiple.f90:1 (multiple)
    Test: A-mult
    """
    live = talys > FLOOR_MB
    missing = live & ~(port > 0)
    spurious = (~live) & (np.abs(port) > FLOOR_MB)
    if not (missing.any() or spurious.any()):
        return
    Z, A = cas.zn(*k)
    key = f"Z{Z}A{A}_{PARSYM_[t]}"
    rec = inf.setdefault(key, {"zcomp": k[0], "ncomp": k[1], "Z": Z, "A": A, "type": t,
                               "n_inf": 0, "n_missing": 0, "n_spurious": 0,
                               "energies_mev": [], "cells": []})
    rec["n_missing"] += int(missing.sum())
    rec["n_spurious"] += int(spurious.sum())
    rec["n_inf"] = rec["n_missing"] + rec["n_spurious"]
    e = round(float(e_inc_mev), 6)
    if e not in rec["energies_mev"]:
        rec["energies_mev"].append(e)
    for i in np.flatnonzero(missing | spurious):
        if len(rec["cells"]) >= 8:
            break
        nex, nexout = keys[i]
        rec["cells"].append({"e_inc_mev": e, "nex": int(nex), "nexout": int(nexout),
                             "nlast": int(ns.nlast), "maxex": int(ns.maxex),
                             "talys_mb": float(talys[i]), "port_mb": float(port[i]),
                             "kind": "missing" if missing[i] else "spurious"})


def _stats(vals: list[np.ndarray], tol: float) -> dict:
    if not vals:
        return {"n": 0}
    r = np.concatenate([np.atleast_1d(v).ravel() for v in vals])
    r = r[~np.isnan(r)]
    if r.size == 0:
        return {"n": 0}
    fin = r[np.isfinite(r)]
    p95 = float(np.percentile(fin, 95)) if fin.size else None
    return {"n": int(r.size), "n_inf": int((~np.isfinite(r)).sum()),
            "median": float(np.median(fin)) if fin.size else None, "p95": p95,
            "max": float(fin.max()) if fin.size else None, "tol": tol,
            "pass": bool(p95 is not None and p95 <= tol)}


def score_run(work: Path, Zt: int, At: int, energies: list[float] | None = None) -> dict:
    """A-mult on `feedexcl` and `popexcl` over one instrumented run."""
    bs = load_binary_dump(Path(work) / "bin_inputs.txt")
    cs = load_channel_dump(Path(work) / "ch_inputs.txt")
    by_e = {round(c.e_inc_mev, 6): c for c in cs}
    enincmax = max(b.e_inc_mev for b in bs)
    cas = Cascade(Zt, At, enincmax, energies=tuple(b.e_inc_mev for b in bs))
    fe, pe, times, done = [], [], [], []
    inf: dict[str, dict] = {}
    bstate = BinaryState()  # sfactor is run-scoped (strucinitial.f90:484): walk every energy
    for binp in bs:
        key = round(binp.e_inc_mev, 6)
        if key not in by_e or (
                energies is not None and not any(abs(binp.e_inc_mev - e) < 1e-9 for e in energies)):
            binary(binp, bstate)
            continue
        cinp = by_e[key]
        t0 = time.time()
        feed, pop = chain_case(cas, binp, cinp, bstate=bstate)
        times.append(time.time() - t0)
        done.append(binp.e_inc_mev)
        for k, ns in cinp.nuclei.items():
            got_f = feed.get(k, {})
            for t, ref in ns.feedexcl_mb.items():
                g = got_f.get(t, {})
                keys = sorted(ref)
                port = np.array([g.get(kk, 0.0) for kk in keys])
                talys = np.array([ref[kk] for kk in keys])
                fe.append(_r(port, talys, FLOOR_MB))
                _tally_inf(inf, cas, binp.e_inc_mev, k, ns, t, keys, port, talys)
            got_p = pop.get(k, {})
            keys = sorted(ns.popexcl_mb)
            if keys:
                pe.append(_r(np.array([got_p.get(kk, 0.0) for kk in keys]),
                             np.array([ns.popexcl_mb[kk] for kk in keys]), FLOOR_MB))
    for v in inf.values():
        v["cells"] = v["cells"][:8]
    return {"run": Path(work).name, "energies": done, "densprepare_calls": cas.ndens,
            "s_per_energy": round(float(np.median(times)), 2) if times else None,
            "feedexcl": _stats(fe, TOL), "popexcl": _stats(pe, TOL),
            "feedexcl_inf_by_nucleus_type": dict(
                sorted(inf.items(), key=lambda kv: -kv[1]["n_inf"]))}


def main(argv=None) -> None:
    from physics.hf.talys_reference import REFERENCE_SET

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--runs", default=str(Path.home() / "hf_t10/runs"))
    ap.add_argument("--work", default=str(Path.home() / "hf_t10/score_work"))
    ap.add_argument("--out", default=str(OUT_JSON))
    ap.add_argument("--only", default="")
    ap.add_argument("--energies", default="")
    a = ap.parse_args(argv)
    zt = {t.tag: (t.Z, t.A) for t in REFERENCE_SET}
    en = [float(x) for x in a.energies.split(",")] if a.energies else None
    recs = []
    for tar in sorted(Path(a.runs).glob("default__*.tar.gz")):
        tag = tar.name[len("default__"): -len(".tar.gz")]
        if a.only and tag not in a.only.split(","):
            continue
        d = Path(a.work) / f"default__{tag}"
        if not (d / "ch_inputs.txt").exists():
            d.mkdir(parents=True, exist_ok=True)
            with tarfile.open(tar) as tf:
                tf.extractall(d)
        Z, A = zt[tag]
        recs.append(score_run(d, Z, A, en))
        print(json.dumps(recs[-1]), flush=True)
    p95 = [r["feedexcl"]["p95"] for r in recs if r["feedexcl"].get("p95") is not None]
    roll: dict[str, dict] = {}
    for r in recs:
        for key, v in r.get("feedexcl_inf_by_nucleus_type", {}).items():
            d = roll.setdefault(f"{r['run']}/{key}", {"run": r["run"], **v})
            d.update(v)
    out = {"gate": "A-mult / multiple.f90 feeding chain", "tol": TOL, "runs": recs,
           "worst_p95": max(p95) if p95 else None,
           "n_inf": sum(r["feedexcl"].get("n_inf", 0) for r in recs),
           "n_inf_by_nucleus_type": dict(sorted(roll.items(), key=lambda kv: -kv[1]["n_inf"])),
           "n_missing": sum(v["n_missing"] for v in roll.values()),
           "n_spurious": sum(v["n_spurious"] for v in roll.values()),
           "pass": bool(recs) and all(r["feedexcl"].get("pass") for r in recs)}
    Path(a.out).write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps({k: v for k, v in out.items() if k != "runs"}, indent=1))


if __name__ == "__main__":
    main()
