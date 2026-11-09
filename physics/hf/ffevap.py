"""KWCOV B14 part 3 (FFEVAP): fission fragment evaporation, `massdis y` with `fymodel 4` (fragment files) or
`fymodel 5` (own fragment populations ff<ZZZ><AAA>.ex in the run directory, or INCOGNITA_FFDIR).

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning (ffevap: A.J. Koning and J.-F. Lemaitre). See physics/hf/NOTICE-TALYS.md.

OUTPUT ONLY. Reached from `fisyield` (massdis y on a fission run with fymodel >= 3); nothing else calls it. TALYS
runs, after the incident energy's own output, a full TALYS calculation for every fission fragment whose
pre-neutron cross section exceeds Rfiseps * xsfistot: the fragment is the target, `projectile 0` (an initial
excitation-energy population, ff<ZZZ><AAA>.ex), no fission, and the deck's other keywords (ffevap.f90 ->
evaptalys.f90). The fragment's residual production gives the post-neutron (fission product) yields and their
isomer split; its particle multiplicities give nubar, nu(A), nu(Z,A) per ejectile.

The port runs the same per-fragment calculation through the engine's own cascade (`engine_c.cascade`, the C walk of
multiple.f90) on a `Cascade` of the fragment with k0 = 0 (`INCOGNITA_CPINC=g` for the duration of the loop: the
photon projectile's defaults are TALYS's `projectile 0` defaults but for the lines input_*.f90 change for a
fragment run; the one that acts goes on the deck: `fission n` (input_fissionmodel.f90:80); NNLEAK goes off too (its
premise, a top bin fed by primary photons only, does not hold for an input population; decided, COVERAGE_PLAN B14c).
`epreeq = Emaxtalys` (input_preeqmodel.f90:84) and `flagdisc` (input_directmodel.f90:81) act only in the binary
reaction, which a population run never calls. What is specific to a population run:

    initial_loop.f90:54-71   the fragment is the target, ptype0 = '0', energy file ff<ZZZ><AAA>.ex
    read_energies.f90:34-90  the population file (npopE, npopJ, npopP; rows), Einc = the last energy
    energies.f90:130         eninccm = Einc, so Etotal = Einc (S(0,0,0) = 0, targetE = 0)
    exgrid.f90:250-254       maxJ from spincut(..., ipop = 1): Rspincutff instead of Rspincut (Cascade.ffruns_rspincut)
    densprepare.f90:393      lmaxhf(k0, 0) = gammax (the C walk's lmaxinc)
    excitation.f90:1         the initial population of the compound nucleus (0, 0) on its grid
    multiple.f90:247         decay of (0, 0) from that population (the cascade's type-0 seed)
    cascade.f90:76-83        xsgamdistot for a fragment run (with the conversion coefficients, incl. TALYS's
                             misaligned ones for a nucleus whose levels were read twice, levels.f90:177-183)
    totalxs.f90:100-112      multiplicity = (xsfeed summed + discrete gammas) / xsinitpop
    residual.f90:75          xspopnuc = xseps for a reachable residual (Qres > 0) with nothing in it

Files (`fisyield.build`): yieldA / yieldZA with the post-neutron columns and the isomer rows (i00 / i01, ratio),
fp<ZZZ><AAA>.tot, fp<ZZZ><AAA>.i00 / .i01 and rp<ZZZ><AAA>.i00 / .i01, nubar<x>.tot, Pnu<x><E>.fis, nu<x>A, nu<x>ZA,
EavZA / EavA (zero rows without spectra, as stock), and ff_fragments<E> (not a TALYS file: talys.out's per-fragment
summary, initial population and multiplicities).

Not ported here (refused before the run, fisyield.settings): fymodel 3 (gefsub.f); the prompt neutron / gamma spectra
(pfnsmodel 2: ffevap.f90:322-341, ffgammaspec.f90, pfnsout.f90) -- they need `outspectra y`, refused with fymodel >= 3;
P(nu) per fragment needs `channels y` (refused; with `channels n`, TALYS's default, ffevap's P(nu) is zero: the
exclusive channels it sums are not computed -- kept); `popmev y` and one-bin populations (excitation.f90:178-243).
`ffspin` acts only with fymodel 3: inert here, as stock.

TALYS routines ported here (file:line of the subroutine / function statement):
    ffevap.f90:1 (ffevap)            fragment loop, post-neutron yields, nubar / nu(A) / nu(Z,A), isomer split
    excitation.f90:1 (excitation)    initial population, npopJ = 0 and npopJ > 0
    read_energies.f90:1 (read_energies) [projectile 0 branch]
    spindis.f90:1 (spindis)
    massdis.f90:576-742              fymodel 4 fragment pairs / 5 own files (fisyield._fymodel4 / _fymodel5)
Single precision where TALYS has it (np.float32); the population file goes through its print formats (f10.5,
es12.5) as stock reads back what it wrote.
Task: T10 (physics/hf/CONTRACT.md section 7; KWCOV batch B14 part 3, output only). Acceptance test: KWCOV-B14c
(tests/hf/test_kwcov_b14c.py, scripts/kwcov/b14c_response.py, docs/hf/COVERAGE_PLAN.md).
"""

from __future__ import annotations

import math
import os
from contextlib import contextmanager
from types import SimpleNamespace

import numpy as np

F = np.float32
NUMPOP = 1000  # A0_talys_mod.f90:30
NUMJ = 40  # A0_talys_mod.f90 numJ (compound.prepare.NUMJ)
NUMIN = 8  # A0_talys_mod.f90:86
NUMNU = 50
PARDIS = F(0.5)  # constants.f90:158
SQRTTWOPI = F(math.sqrt(2.0 * math.pi))
ONETHIRD = F(1.0) / F(3.0)
FF_LINES = ("fission n", "nnleak n")  # see the module docstring


# ------------------------------------------------------------------------------------------------ population files
def fymodel4_rows(eex: float, deex: float, xs: float) -> tuple[np.ndarray, np.ndarray]:
    """ff<ZZZ><AAA>.ex of fymodel 4 as stock reads it back: a Gaussian in excitation energy (centre Excff, width
    dExcff, up to min(E + 4 dE, 80) MeV, numpop + 1 rows) times the fragment's cross section, through the file's
    f10.5 / es12.5 formats. Returns (EdistE, PdistE) of the rows read_energies reads (npopE = numpop).

    TALYS: ffevap.f90:221-244, read_energies.f90:49-52
    Test: tests/hf/test_kwcov_b14c.py
    """
    eex, deex, xs = F(eex), F(deex), F(xs)
    emaxff = min(F(eex + F(4.0) * deex), F(80.0))
    fac1 = F(F(1.0) / F(deex * SQRTTWOPI))
    fac2 = F(F(1.0) / F(F(2.0) * F(deex * deex)))
    de = F(emaxff / F(NUMPOP))
    nex = np.arange(NUMPOP + 1)
    E = (de * nex.astype(F)).astype(F)
    gau = (fac1 * np.exp((-((E - eex) * (E - eex))) * fac2)).astype(F)
    s = np.add.accumulate((de * gau).astype(F), dtype=F)[-1]
    gauss = (gau / s).astype(F)
    P = ((de * gauss).astype(F) * xs).astype(F)
    Er = np.array([float(f"{float(x):10.5f}") for x in E[:NUMPOP]], dtype=F)
    Pr = np.array([float(f"{float(x):.5e}") for x in P[:NUMPOP]], dtype=F)
    return Er, Pr


def read_population(path: str) -> dict:
    """read_energies.f90's projectile-0 branch: (npopE, npopJ, npopP) and the rows of a population file; npopP = 1
    tables are halved into both parities. Returns EdistE (0:npopE), PdistE (0:npopE), PdistJP (0:npopE, J, P) with
    P index 0 = parity -1.

    TALYS: read_energies.f90:34-90
    Test: tests/hf/test_kwcov_b14c.py
    """
    with open(path) as f:
        head = f.readline().split()
        npope, npopj, npopp = int(head[0]), int(head[1]), int(head[2])
        if not 1 <= npope <= NUMPOP:
            raise ValueError(f"TALYS-error: {path}: number of population energies {npope} outside 1..{NUMPOP}")
        if not 0 <= npopj <= NUMJ + 1:
            raise ValueError(f"TALYS-error: {path}: number of spins {npopj} outside 0..{NUMJ + 1}")
        if npopj > 0 and not 1 <= npopp <= 2:
            raise ValueError(f"TALYS-error: {path}: number of parities {npopp} outside 1..2")
        E = np.zeros(NUMPOP + 1, dtype=F)
        P = np.zeros(NUMPOP + 1, dtype=F)
        PJ = np.zeros((NUMPOP + 1, NUMJ + 1, 2), dtype=F)
        if npopj == 0:
            for nen in range(1, npope + 1):
                t = f.readline().split()
                E[nen], P[nen] = F(t[0]), F(t[1])
        else:
            pars = (1,) if npopp == 1 else (0, 1)
            for ip in pars:
                for nen in range(1, npope + 1):
                    t = f.readline().split()
                    E[nen] = F(t[0])
                    PJ[nen, :npopj, ip] = np.array(t[1:1 + npopj], dtype=F)
            for nen in range(1, npope + 1):
                if E[nen] <= E[nen - 1] and E[1] != 0.0:
                    raise ValueError("TALYS-error: excitation energies must be given in ascending order, or the number"
                                     " of population bins is not correct")
            if npopp == 1:
                PJ[:, :, 1] = (F(0.5) * PJ[:, :, 1]).astype(F)
                PJ[:, :, 0] = PJ[:, :, 1]
    return {"npopE": npope, "npopJ": npopj, "npopP": npopp, "E": E, "P": P, "PJ": PJ}


def population_of(E: np.ndarray, P: np.ndarray) -> dict:
    """A spin-independent population (npopJ = 0) given as EdistE(1:npopE), PdistE(1:npopE) (fymodel 4's rows).

    TALYS: read_energies.f90:46-52
    Test: tests/hf/test_kwcov_b14c.py
    """
    n = len(E)
    Ea = np.zeros(NUMPOP + 1, dtype=F)
    Pa = np.zeros(NUMPOP + 1, dtype=F)
    Ea[1:n + 1] = E
    Pa[1:n + 1] = P
    return {"npopE": n, "npopJ": 0, "npopP": 1, "E": Ea, "P": Pa, "PJ": np.zeros((NUMPOP + 1, NUMJ + 1, 2), F)}


def spindis(sc, rspin):
    """Wigner spin distribution (2R+1)/(2 sc) exp(-(R+1/2)^2 / (2 sc)), single precision.

    TALYS: spindis.f90:1 (spindis)
    Test: tests/hf/test_kwcov_b14c.py
    """
    sc = F(sc)
    r = np.asarray(rspin, dtype=F)
    sigma22 = F(F(2.0) * sc)
    return ((F(2.0) * r + F(1.0)) / sigma22 * np.exp(-((r + F(0.5)) * (r + F(0.5))) / sigma22)).astype(F)


def edistmax_of(pop: dict) -> float:
    """The last energy where the (spin-independent) population still rises; 10 MeV if none.

    TALYS: excitation.f90:72-77
    Test: tests/hf/test_kwcov_b14c.py
    """
    e = F(10.0)
    E, P = pop["E"], pop["P"]
    for nen in range(1, pop["npopE"] + 1):
        if P[nen] > P[nen - 1]:
            e = E[nen]
    return float(e)


def excitation(pop: dict, ex, dex, maxj, jdis, parlev, nl: int, maxex: int, A: int, sc: float | None,
               popmev: bool = False) -> dict:
    """The initial population xspop(0, 0, nex, J, parity) of a population run on the compound nucleus's grid
    (histogram overlap of the input bins with the excitation bins; Wigner spins of cutoff `sc` and equal parities
    when the input has no spins). Returns xspop (maxex+1, numJ+1, 2; P index 0 = parity -1), xspopex, xsinitpop.

    TALYS: excitation.f90:1 (excitation)
    Test: tests/hf/test_kwcov_b14c.py
    """
    if popmev:
        raise NotImplementedError("popmev y (population per MeV, excitation.f90:178-199) is not ported (KWCOV B14c)")
    npope, npopj = int(pop["npopE"]), int(pop["npopJ"])
    E = pop["E"].copy()
    P = pop["P"].copy()
    PJ = pop["PJ"].copy()
    n = maxex + 1
    xspop = np.zeros((n, NUMJ + 1, 2), dtype=F)
    xspopex = np.zeros(n, dtype=F)
    if npopj > 0:
        xsinputpop = F(0.0)
        for ip in (0, 1):
            for J in range(npopj):
                for nen in range(1, npope + 1):
                    xsinputpop = F(xsinputpop + PJ[nen, J, ip])
    else:
        xsinputpop = np.add.accumulate(P[1:npope + 1], dtype=F)[-1] if npope else F(0.0)
    if xsinputpop == 0.0:
        return {"xspop": xspop, "xspopex": xspopex, "xsinitpop": 0.0}
    if E[1] == 0.0:
        for nen in range(1, npope + 1):
            E[nen - 1] = E[nen]
            P[nen - 1] = P[nen]
            PJ[nen - 1, :npopj] = PJ[nen, :npopj]
        npope -= 1
    if npopj > 0:
        for nen in range(1, npope + 1):
            s = F(0.0)
            for ip in (0, 1):
                for J in range(npopj):
                    s = F(s + PJ[nen, J, ip])
            P[nen] = s
    k = np.arange(npope + 1)
    elow = (F(0.5) * (E[k] + E[np.maximum(k - 1, 0)])).astype(F)
    eup = (F(0.5) * (E[k] + E[np.minimum(npope, k + 1)])).astype(F)
    elow[0] = F(0.0)
    eup[npope] = E[npope]
    ex32 = np.asarray(ex, dtype=F)
    dex32 = np.asarray(dex, dtype=F)
    exlow = np.zeros(n, dtype=F)
    exup = np.zeros(n, dtype=F)
    for nex in range(n):
        if nex <= nl:
            exlow[nex] = F(F(0.5) * F(ex32[nex] + ex32[max(nex - 1, 0)]))
            exup[nex] = F(F(0.5) * F(ex32[nex] + ex32[min(nex + 1, maxex)]))
        else:
            exlow[nex] = F(ex32[nex] - F(F(0.5) * dex32[nex]))
            exup[nex] = F(ex32[nex] + F(F(0.5) * dex32[nex]))
    odd = A % 2
    pex = np.zeros(n, dtype=F)
    pexjp = np.zeros((n, NUMJ + 1, 2), dtype=F)
    sumpex = F(0.0)
    dEb = (eup[:npope] - elow[:npope]).astype(F)
    for nex in range(n):
        lo, up = exlow[nex], exup[nex]
        m = ~((elow[:npope] >= up) | (eup[:npope] <= lo))
        idx = np.flatnonzero(m)
        if idx.size:
            de = dEb[idx]
            dlo = np.maximum(lo - elow[idx], F(0.0)).astype(F)
            dup = np.maximum(eup[idx] - up, F(0.0)).astype(F)
            frac = (((de - dlo) - dup) / de).astype(F)
            pex[nex] = np.add.accumulate((frac * P[idx]).astype(F), dtype=F)[-1]
            if npopj > 0 and nex > nl:
                mj = int(maxj[nex])
                for i, nen in enumerate(idx.tolist()):
                    pexjp[nex, :mj + 1, :] = (pexjp[nex, :mj + 1, :] + frac[i] * PJ[nen, :mj + 1, :]).astype(F)
        if nex <= nl:
            J = int(jdis[nex])
            ip = 0 if int(parlev[nex]) == -1 else 1
            pexjp[nex, J, ip] = pex[nex]
        elif npopj == 0:
            mj = int(maxj[nex])
            rs = (np.arange(mj + 1, dtype=F) + F(0.5 * odd)).astype(F)
            sd = spindis(sc, rs)
            normj = np.add.accumulate(sd, dtype=F)[-1]
            for ip in (0, 1):
                pexjp[nex, :mj + 1, ip] = (((pex[nex] * PARDIS) * sd) / normj).astype(F)
        sumpex = F(sumpex + pex[nex])
    if sumpex > 0.0:
        factor = F(sumpex / xsinputpop)
        sumjp = F(0.0)
        for nex in range(n):
            mj = int(maxj[nex])
            for ip in (0, 1):
                v = (pexjp[nex, :mj + 1, ip] / factor).astype(F)
                xspop[nex, :mj + 1, ip] = v
                sumjp = F(sumjp + np.add.accumulate(v, dtype=F)[-1])
        factor2 = F(sumjp / xsinputpop)
        for nex in range(n):
            mj = int(maxj[nex])
            s = F(0.0)
            for ip in (0, 1):
                for J in range(mj + 1):
                    s = F(s + F(xspop[nex, J, ip] / factor2))
            xspopex[nex] = s
    if npope == 1:
        raise NotImplementedError("a one-bin population (npopE = 1, excitation.f90:221-243) is not ported (KWCOV B14c)")
    xsinitpop = np.add.accumulate(xspopex.astype(np.float64))[-1] if n else 0.0
    return {"xspop": xspop, "xspopex": xspopex, "xsinitpop": float(xsinitpop)}


# ------------------------------------------------------------------------------------------------ one fragment
@contextmanager
def fragment_env(restore: tuple[int, int] | None = None):
    """k0 = 0 and the deck plus FF_LINES for the duration of a fragment loop; caches dropped on both sides.

    TALYS: initial_loop.f90:54-71 (the fragment as target, ptype0 = '0'), input_fissionmodel.f90:80
    Test: tests/hf/test_kwcov_b14c.py
    """
    from physics.hf.chartrun import drop_target_caches
    from physics.hf.input import fitlib

    lines = [x for x in os.environ.get("INCOGNITA_TALYS_FIT_LINES", "").split(";") if x.strip()]
    env = {"INCOGNITA_CPINC": "g", "INCOGNITA_TALYS_FIT": "lines",
           "INCOGNITA_TALYS_FIT_LINES": ";".join(lines + list(FF_LINES))}
    old = {k: os.environ.get(k) for k in env}
    was = fitlib.active() is not None
    try:
        os.environ.update(env)
        drop_target_caches()
        yield
    finally:
        for k, v in old.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        fitlib.deactivate()
        drop_target_caches()
        if restore is not None and was:  # the main run's target is the active one again (production / thermal after)
            fitlib.activate(int(restore[0]), int(restore[1]))


def _sc_of(cas, sp0, edistmax: float) -> float:
    """excitation.f90:76-77: spincut(0, 0, ignatyuk(0, 0, Edistmax, 0), Edistmax, 0, ipop = 1)."""
    import torch

    from physics.hf.compound.dens_reference import _ld_of
    from physics.hf.density.parameters import ignatyuk, spincut

    ld = _ld_of(int(sp0.Z), int(sp0.A), int(cas.Zt), int(cas.At))[0]
    e = torch.tensor([float(F(edistmax))], dtype=torch.float64)
    ald = ignatyuk(ld, e, 0)
    sc = spincut(ld, ald.to(torch.float64), e, 0, 1, float(cas.params.at("rspincutff")))
    return float(F(float(sc.reshape(-1)[0])))


def run_fragment(Z: int, A: int, pop: dict) -> dict:
    """A population run of fragment (Z, A) (call inside `fragment_env`): multiplicities, the residual populations
    xspopnuc per (Zix, Nix) and the surviving level populations (g.s. and isomers) per (Zix, Nix).

    TALYS: evaptalys.f90:1 (evaptalys) with flagffruns, excitation.f90:1, multiple.f90:1, totalxs.f90:95-112,
    residual.f90:75
    Test: tests/hf/test_kwcov_b14c.py
    """
    import torch

    from physics.hf import engine_c
    from physics.hf.emission.feeding import Cascade

    einc = float(F(pop["E"][pop["npopE"]]))
    with torch.inference_mode():
        cas = Cascade(int(Z), int(A), einc, k0=0, energies=(einc,))
        o = cas.options
        if bool(getattr(o, "flagchannels", False)):
            raise NotImplementedError("channels y on a fragment run (ffevap.f90:292-319, P(nu) per fragment) is not "
                                      "ported (KWCOV B14c)")
        cas.ffruns_rspincut = float(cas.params.at("rspincutff"))
        st = cas.new_energy(einc, lmaxinc=int(cas.gammax), e_inc_mev=einc)
        cas.propagate_exmax(st, 0, 0)
        sp0 = cas.spec(st, 0, 0)
        sc = None
        if int(pop["npopJ"]) == 0:
            sc = _sc_of(cas, sp0, edistmax_of(pop))
        ini = excitation(pop, sp0.ex_mev, sp0.dex_mev, sp0.maxj, sp0.jdis, sp0.parlev, int(sp0.nlast),
                         int(sp0.maxex), int(sp0.A), sc, bool(getattr(o, "flagpopMeV", False)))
        xsinit = ini["xsinitpop"]
        out = {"Z": int(Z), "A": int(A), "Einc": einc, "xsinitpop": xsinit, "mult": np.zeros(7), "xspopnuc": {},
               "levels": {}, "sc": sc}
        if xsinit <= 0.0:
            return out
        maxz, maxn = int(o.maxZ), int(o.maxN)
        popeps = float(F(o.popeps_mb))
        rn = engine_c._Run(cas)
        if not rn.ok:
            raise RuntimeError(f"FFEVAP: fragment {Z}-{A}: the C cascade does not take this run")
        seed = {0: (ini["xspop"].astype(np.float64), ini["xspopex"].astype(np.float64), xsinit)}
        prq = SimpleNamespace(mulpre={}, xspopph2_mb={})
        propagated: set = set()
        while True:
            packed = engine_c.cascade(rn, st, maxz, maxn, seed, popeps, 0, xsinit, {}, None, False, None, prq,
                                      propagated)
            grown = cas.regrow(st, propagated, packed.decayed(), packed.in_set, maxz, maxn)
            if grown is None:
                break
            st = grown
        mres = packed.result()
        xseps = float(F(o.xseps_mb))
        xsparticle = np.zeros(7)
        flagelectron = bool(getattr(o, "flagelectron", True))
        etot32 = F(einc)
        for s, key in enumerate(packed.nuclei):
            feed = mres.xsfeed_mb.get(key, {})
            for t in range(7):
                xsparticle[t] += float(feed.get(t, 0.0))
            status = int(packed.si[s, 12])
            sp = packed.specs[s]
            pn = float(mres.xspopnuc_mb.get(key, 0.0))
            q0 = float(F(F(st.exmax0[key]) - etot32))
            if q0 > 0.0 and pn <= xseps:  # residual.f90:75
                pn = xseps
            out["xspopnuc"][key] = pn
            if s in packed.pops:
                XE = packed.pops[s][4]
                out["levels"][key] = (XE[: int(sp.nlast_grid) + 1].copy(), np.asarray(sp.tau_s)[: int(sp.nlast_grid) + 1])
            if status in (2, 3):
                g = _gamdis(cas, packed, s, key, sp, flagelectron)
                xsparticle[0] += g
        parskip = [not b for b in getattr(o, "parinclude", [True] * 7)]
        for t in range(7):
            if not parskip[t]:
                out["mult"][t] = xsparticle[t] / xsinit
        out["parskip"] = parskip
        out["maxz"], out["maxn"] = maxz, maxn
        for key in st.spec:  # nuclei exgrid reached but the cascade set did not hold: residual.f90:75 alone
            if key not in out["xspopnuc"] and key[0] <= maxz and key[1] <= maxn:
                q0 = float(F(F(st.exmax0[key]) - etot32))
                if q0 > 0.0:
                    out["xspopnuc"][key] = xseps
        return out


def _gamdis(cas, packed, s: int, key, sp, flagelectron: bool) -> float:
    """xsgamdistot(Zcomp, Ncomp): the discrete gamma lines of the cascade (each over 1 + its conversion coefficient),
    from the level populations at their decay (popexcl) and the branching ratios.

    TALYS: cascade.f90:76-82
    Test: tests/hf/test_kwcov_b14c.py
    """
    xrows, fo, uo, tl = packed.views[s]
    F_ = packed.F
    maxex = xrows - 1
    nl = int(sp.nlast_grid)
    ex = np.asarray(sp.ex_mev)
    tau = np.asarray(sp.tau_s)
    smin = float(sp.sep_mev[1])
    lv = None
    if flagelectron:
        # TALYS reads the levels of X again from dtheory of Y = (Zx, Nx - 1) (dtheory.f90:79-80) whenever Y's
        # structure was built, which is before X decays: the second read keeps the first branch list but takes the
        # conversion coefficients by FILE branch index (levels.f90:177-183), misaligned wherever a zero-ratio branch
        # was dropped. Kept, as stock (Zr-99 level 7: its lines are 3,000-18,000 times smaller than the cascade's).
        prior = key[1] >= 1 and (key[0], key[1] - 1) in packed.in_set
        if prior:
            from physics.hf.structure.levels import discrete_levels

            Z, A = cas.zn(*key)
            lv = discrete_levels(Z, A, cas.options, cas.m, cas.params, prior_call=True)
        else:
            lv = cas._levels(*key)
    tot = 0.0
    for nex in range(min(nl, maxex), 0, -1):
        if not (ex[nex] <= smin and tau[nex] == 0.0):
            continue
        pop = float(F_[fo + nex])
        if pop == 0.0:
            continue
        for k, ratio in sp.branch.get(nex, ()):
            cv = 0.0
            if lv is not None and nex < int(lv.branch_to.shape[0]):
                bto = lv.branch_to[nex].tolist()
                if int(k) in bto:
                    cv = float(lv.conversion[nex, bto.index(int(k))])
            tot += pop * float(ratio) / (1.0 + cv)
    return tot


# ------------------------------------------------------------------------------------------------ the fragment loop
def evaporate(r: dict, s: dict, progress=None) -> dict:
    """ffevap.f90 for one incident energy: every fragment above Rfiseps * xsfistot evaporated (fymodel 4: its
    Gaussian population), the fission product cross sections and yields (post-neutron, normalised to 2), the isomer
    split, nubar / nu(A) / nu(Z,A) per ejectile, P(nu) (zero without channels, as stock). `r` is fisyield.massdis's
    record of the energy (xsZApre, yieldZApre, yieldApre, xsfistot, ff); returns the arrays ffevap fills.

    TALYS: ffevap.f90:1 (ffevap)
    Test: tests/hf/test_kwcov_b14c.py
    """
    from physics.hf.fisyield import NUMELEM, NUMMASS, NUMNEU

    Zt, At = s["Ztarget"], s["Atarget"]
    ZCN, ACN = s["Zinit"], s["Ainit"]
    parskip = s.get("parskip", [False] * 7)
    xsZApre, yieldZApre, yieldApre = r["xsZApre"], r["yieldZApre"], r["yieldApre"]
    fiseps = F(F(s["Rfiseps"]) * F(r["xsfistot"]))
    xsZApost = np.zeros((NUMELEM + 1, NUMNEU + 1), dtype=F)
    xsApost = np.zeros(NUMMASS + 1, dtype=F)
    xsfpex = np.zeros((NUMELEM + 1, NUMNEU + 1, 2), dtype=F)
    nubar = np.zeros(7, dtype=F)
    nuA = np.zeros((7, NUMMASS + 1), dtype=F)
    nuZA: dict = {}
    eavZA: dict = {}
    eavA = np.zeros((7, NUMMASS + 1), dtype=F)
    pdisnu = np.zeros((7, NUMNU + 1), dtype=F)
    frag: dict = {}
    ff = r.get("ff", {})
    todo = []
    for ia in range(1, ACN + 1):
        for iz in range(1, ZCN + 1):
            inn = ia - iz
            if inn < 1 or inn > NUMNEU:
                continue
            if not xsZApre[iz, inn] > fiseps:
                continue
            todo.append((iz, ia, inn))
    with fragment_env(restore=(Zt, At)):
        for k, (iz, ia, inn) in enumerate(todo):
            if s["fymodel"] == 4:
                eex, deex, _tke = ff.get((iz, inn), (F(0.0), F(0.0), F(0.0)))
                E, P = fymodel4_rows(eex, deex, xsZApre[iz, inn])
                pop = population_of(E, P)
            elif s["fymodel"] == 5:  # the user's file (initial_loop.f90: energy ff<ZZZ><AAA>.ex)
                fn = ff.get((iz, inn))
                if fn is None:
                    raise FileNotFoundError(f"TALYS-error: if projectile 0, specify a range of excitation energies in a "
                                            f"file ff{iz:03d}{ia:03d}.ex (read_energies.f90:36)")
                pop = read_population(fn)
            else:
                raise NotImplementedError(f"fymodel {s['fymodel']}: no fragment populations (KWCOV B14 part 3)")
            res = run_fragment(iz, ia, pop)
            frag[(iz, ia)] = {"xsinitpop": res["xsinitpop"], "mult": res["mult"].copy(), "Einc": res["Einc"]}
            if progress is not None:
                progress(k, len(todo), iz, ia, res)
            for (zix, nix), pn in res["xspopnuc"].items():  # ffevap.f90:257-273
                if zix > res.get("maxz", 99) or nix > res.get("maxn", 99):
                    continue
                izp, inp = iz - zix, inn - nix
                if izp < 1 or inp < 1:
                    continue
                xsZApost[izp, inp] = F(xsZApost[izp, inp] + F(pn))
                xsApost[izp + inp] = F(xsApost[izp + inp] + F(pn))
            for (zix, nix), (xe, tau) in res["levels"].items():
                izp, inp = iz - zix, inn - nix
                if izp < 1 or inp < 1:
                    continue
                for nex in range(len(xe)):
                    if nex == 0 or tau[nex] != 0.0:
                        j = min(nex, 1)
                        xsfpex[izp, inp, j] = F(xsfpex[izp, inp, j] + F(xe[nex]))
            if res["xsinitpop"] > 0.0:  # ffevap.f90:278-342 (the spectra: pfnsmodel 2, not ported)
                yA, yZA = yieldApre[ia], yieldZApre[iz, inn]
                for t in range(7):
                    if parskip[t]:
                        continue
                    m = F(res["mult"][t])
                    nubar[t] = F(nubar[t] + F(yZA * m))
                    if yA > 0.0:
                        nuA[t, ia] = F(nuA[t, ia] + F(F(yZA / yA) * m))
                        nuZA[(t, iz, inn)] = F(nuZA.get((t, iz, inn), F(0.0)) + F(yZA * m))
                        eavZA[(t, iz, inn)] = F(0.0)  # Eaverage(type): spectra.f90 (outspectra) only
    # P(nu): ffevap.f90:350-394 on Pmultiff = xsexcpart / xsinitpop, zero without exclusive channels
    sumpost = F(0.0)
    for ia in range(1, ACN + 1):
        sumpost = F(sumpost + xsApost[ia])
    sumpost = F(F(0.5) * sumpost)
    yieldZApost = np.zeros_like(xsZApost)
    yieldApost = np.zeros(NUMMASS + 1, dtype=F)
    yieldfpex = np.zeros_like(xsfpex)
    fpratio = np.zeros_like(xsfpex)
    xstotpost = F(0.0)
    yieldtotpost = F(0.0)
    if sumpost > 0.0:
        for iz in range(1, ZCN + 1):
            for ia in range(iz + 1, ACN + 1):
                inn = ia - iz
                if inn > NUMNEU or xsZApost[iz, inn] == 0.0:
                    continue
                yieldZApost[iz, inn] = F(xsZApost[iz, inn] / sumpost)
                yieldApost[ia] = F(yieldApost[ia] + yieldZApost[iz, inn])
                xstotpost = F(xstotpost + xsZApost[iz, inn])
                yieldtotpost = F(yieldtotpost + yieldZApost[iz, inn])
                if xsfpex[iz, inn, 1] > 0.0:
                    for j in (0, 1):
                        yieldfpex[iz, inn, j] = F(xsfpex[iz, inn, j] / sumpost)
                        if yieldZApost[iz, inn] > 0.0:
                            fpratio[iz, inn, j] = F(yieldfpex[iz, inn, j] / yieldZApost[iz, inn])
    return {"xsZApost": xsZApost, "xsApost": xsApost, "yieldZApost": yieldZApost, "yieldApost": yieldApost,
            "xstotpost": xstotpost, "yieldtotpost": yieldtotpost, "xsfpex": xsfpex, "yieldfpex": yieldfpex,
            "fpratio": fpratio, "nubar": nubar, "nuA": nuA, "nuZA": nuZA, "eavZA": eavZA, "eavA": eavA,
            "Pdisnu": pdisnu, "Pdisnuav": np.zeros(7, dtype=F), "fragments": frag}
