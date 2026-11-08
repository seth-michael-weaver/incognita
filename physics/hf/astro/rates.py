"""KWCOV B9: TALYS's astrophysical reaction rates, Maxwellian-averaged cross sections and partition function.

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

`astro y` (and `astroE` / `astroT`, which set it) makes TALYS run on its own incident grid (egridastro), fold the
residual production of every nucleus within 4 protons / 4 neutrons of the compound nucleus with a Maxwell-Boltzmann
distribution on its temperature grid (stellarrate), divide by the target's partition function unless `astrogs y`
(partfunc), and write `astrorate.g/p/a(/f)`, `astrorate.tot`, `astrorateZZZAAA.tot`, the `astroex` level files and,
for `astroE 0.03`, `macs.g` (astroout). This module is that arithmetic on an engine run (`input.deck.run_deck` calls
it; nothing here runs unless the deck asks for astro). The thermalised target itself (`astrogs n`, the default with
`astro y`) is `astro/thermal.py`, inside the run.

Definitions (stellarrate.f90): with E the centre-of-mass energy (eninc * specmass) on the run's grid, dE the half
distance to the neighbours,
    rate(T9) = 3.7335e10 / sqrt(mu T9^3) sum_E E sigma(E)[b] exp(-11.605 E / T9) dE   [/ G(T9) unless astrogs]
    MACS(T9) = rate / (2.45484e5 sqrt(T9 / mu))                                          [mb]
mu = redumass (amu); terms with 11.605 E / T9 > 80 are skipped. MACS is thus the centre-of-mass Maxwellian average
2/sqrt(pi) (kT)^-2 int sigma E exp(-E/kT) dE (to the 0.08 % of TALYS's single-precision constants).

TALYS routines ported here (file:line of the subroutine statement):
    egridastro.f90:1 (egridastro)   incident and temperature grids
    partfunc.f90:1 (partfunc)       target partition function G(T)
    stellarrate.f90:1 (stellarrate) rates and MACS
    astroout.f90:1 (astroout)       file names, columns, macs.g
Task: T10 (physics/hf/CONTRACT.md section 7; KWCOV batch B9). Acceptance test: KWCOV-B9 (tests/hf/test_kwcov_b9.py).
"""
from __future__ import annotations

import math
from pathlib import Path

import numpy as np

F32 = np.float32
KT = 0.08617333262  # constants.f90 line 122, double precision
NUMT = 30  # A0_talys_mod.f90:81
NUMZASTRO = NUMNASTRO = 4  # A0_talys_mod.f90:82-83
PARSYM = "gnpdtha"
PARZ = (0, 0, 1, 1, 1, 2, 2)
PARN = (0, 1, 0, 1, 2, 1, 2)


STATE: dict = {}  # one run: masses, the target's levels and its last-energy grid, the partition function


def record_energy(cas, st) -> None:
    """Keep what partfunc.f90 reads after the energy loop: the target's excitation grid as a residual of the
    compound nucleus (exgrid(0,0) at the LAST incident energy), its discrete levels, and the masses.

    TALYS: partfunc.f90:1 (partfunc) -- exgrid(0, 0) after the loop; stellarrate.f90 -- specmass, redumass
    Test: tests/hf/test_kwcov_b9.py
    """
    k0 = int(cas.k0)
    zix, nix = PARZ[k0], PARN[k0]
    d = cas.spec(st, zix, nix)
    STATE["grid"] = dict(ex=np.asarray(d.ex_mev, dtype=np.float64).copy(),
                         dex=np.asarray(d.dex_mev, dtype=np.float64).copy(), maxex=int(d.maxex), nlast=int(d.nlast))
    if "masses" not in STATE:
        STATE["masses"] = dict(specmass=float(cas.m.specmass[zix, nix, k0]),
                               redumass=float(cas.m.redumass_amu[zix, nix, k0]), k0=k0)


def finish_run(cas, t9: np.ndarray, astrogs: bool, nonthermlev: int) -> None:
    """partfunc.f90 on the recorded grid, the run's levels and level density (stored in STATE["partf"]).

    TALYS: partfunc.f90:1 (partfunc)
    Test: tests/hf/test_kwcov_b9.py
    """
    import torch

    from physics.hf.density.models import density

    k0 = int(cas.k0)
    lv = cas._levels(PARZ[k0], PARN[k0])
    nl = int(STATE["grid"]["nlast"])
    levels = dict(e=np.asarray(lv.all_e_mev[: int(lv.nlev) + 1], float),
                  j=np.asarray(lv.all_spin[: int(lv.nlev) + 1], float), nlast=nl, nlev=int(lv.nlev))
    ld = cas.ld_of(int(cas.Zt), int(cas.At))[0]

    def rho(e, j, p):
        d = density(ld, torch.as_tensor(e, dtype=torch.float64), torch.tensor(float(j), dtype=torch.float64), p)
        return np.asarray(d.detach(), float).reshape(-1)

    STATE["levels"] = levels
    STATE["partf"] = partition_function(t9, levels, STATE["grid"], rho, int(cas.At), nonthermlev, astrogs)


# ------------------------------------------------------------------------------------------------------------ input
def check_astro_input(astroE: float, astroT9: float, segment: int = 1, flagastro: bool = True) -> tuple[float, float]:
    """checkvalue.f90:425-495: ranges, `astroE` OR `astroT`, segment 1; returns (astroE, astroT9) completed.

    TALYS: checkvalue.f90:1 (checkvalue) lines 425-495
    Test: tests/hf/test_kwcov_b9.py
    """
    if flagastro and segment > 1:
        raise ValueError("TALYS-error: segment = 1 for astrophysical calculations")
    if astroT9 != 0.0 and not 0.0001 <= astroT9 <= 10.0:
        raise ValueError(f"TALYS-error: 0.0001 <= astroT <= 10., astroT = {astroT9}")
    if astroE != 0.0 and not 0.00001 <= astroE <= 1.0:
        raise ValueError(f"TALYS-error: 0.00001 <= astroE <= 1., astroE = {astroE}")
    if astroE != 0.0 and astroT9 != 0.0:
        raise ValueError("TALYS-error: Only astroE OR astroT can be given")
    if astroE != 0.0:
        astroT9 = float(F32(astroE / KT))
    if astroT9 != 0.0:
        astroE = float(F32(astroT9 * KT))
    return astroE, astroT9


def t9_grid(astroT9: float = 0.0, nTmax: int = NUMT) -> tuple[np.ndarray, np.ndarray]:
    """(T9, ET9) of egridastro.f90:84-121, single precision as TALYS stores them.

    TALYS: egridastro.f90:1 (egridastro)
    Test: tests/hf/test_kwcov_b9.py
    """
    if nTmax == 1:
        t9 = np.array([astroT9], dtype=F32)
    else:
        t9 = [F32(0.0001)]
        temp, dt = F32(0.0001), F32(0.0004)
        while True:
            temp = F32(temp + dt)
            teps = F32(temp + F32(1.0e-4))
            if len(t9) + 1 > nTmax:
                break
            t9.append(temp)
            for lim, step in ((0.0005, 0.0005), (0.001, 0.004), (0.005, 0.005), (0.01, 0.04), (0.05, 0.05),
                              (0.30, 0.1), (1.0, 0.50), (4.0, 1.0)):
                if teps > F32(lim):
                    dt = F32(step)
            if teps > F32(10.0):
                break
        t9 = np.array(t9, dtype=F32)
    et9 = (KT * t9.astype(np.float64)).astype(F32)
    return t9, et9


def energy_grid(k0: int, specmass: float, redumass: float, s0: dict, Ztarget: int, astroT9: float = 0.0,
                nTmax: int = NUMT, numenin: int = 600) -> np.ndarray:
    """Incident LAB energies of egridastro.f90:122-226 (double precision, the order of TALYS's operations).

    `s0` = {type: S(0, 0, type)} of the compound nucleus; `specmass` = specmass(parZ(k0), parN(k0), k0).

    TALYS: egridastro.f90:1 (egridastro)
    Test: tests/hf/test_kwcov_b9.py (stock Au-197 grid, 110 energies)
    """
    t9min = float(F32(0.0001))
    t9max = float(F32(astroT9)) if astroT9 != 0.0 else 10.0
    emin = 1.0e-12 if k0 == 1 else 1.0e-3
    emax = 50.0
    if nTmax == 1 and k0 == 1:
        emax = min(emax, 50.0 * KT * float(F32(astroT9)))
    neg, neg1, neg2 = 100, 10, 10
    acm = 1.0 / specmass
    am = redumass
    Q0, Qn, Qp, Qa = s0[k0], s0[1], s0[2], s0[6]
    qmin, qmax = min(Qn, Qp, Qa), max(Qn, Qp, Qa)
    kt = float(F32(KT))
    eg0 = 0.0
    if k0 == 0:
        eg1 = max(0.0, qmin - 4.0 * kt * t9max)
        eg2 = max(qmax + 4.0 * kt * t9max, 20.0)
        b1, b2, b3 = Qn, Qp, Qa
    elif k0 == 1:
        eg1 = max(float(F32(kt * t9min / 4.0)), 0.001)
        eg2 = kt * t9max * 4.0
        b1, b2, b3 = -999.0, Qp - Q0, Qa - Q0
    else:
        zz = Ztarget * PARZ[k0]
        eg0 = 0.122 * am ** (1.0 / 3.0) * zz ** (2.0 / 3.0)
        eg1 = 0.122 * am ** (1.0 / 3.0) * (zz * t9min) ** (2.0 / 3.0)
        deg1 = 0.237 * am ** (1.0 / 6.0) * zz ** (1.0 / 3.0) * t9min ** (5.0 / 6.0)
        eg1 = eg1 - 2.0 * deg1
        eg2 = 0.122 * am ** (1.0 / 3.0) * (zz * t9max) ** (2.0 / 3.0)
        deg2 = 0.237 * am ** (1.0 / 6.0) * zz ** (1.0 / 3.0) * t9max ** (5.0 / 6.0)
        eg2 = eg2 + 2.0 * deg2
        b1 = Qn - Q0
        b2 = Qp - Q0
        if k0 == 2:
            b2 = Qa - Q0
        b3 = -999.0
        eg2 = max(eg2, b1, b2)
    if eg1 < 0.0:
        eg1 = emin
    e = emin
    if k0 > 1:
        de1 = (math.log10(eg1) - math.log10(emin)) / neg1
        deg = (math.log10(eg2) - math.log10(eg1)) / neg
        de2 = (math.log10(emax) - math.log10(eg2)) / neg2
    else:
        de1 = (eg1 - emin) / neg1
        deg = (eg2 - eg1) / neg
        de2 = (emax - eg2) / neg2
    out = []
    while not e > emax:
        de = de1 if e < eg1 else deg if e < eg2 else de2
        if k0 == 1:
            de = 0.000002
            for lim, step in ((0.00001, 0.000010), (0.0001, 0.00010), (0.001, 0.0010), (0.010, 0.0040),
                              (0.100, 0.0500), (1.000, 0.2500), (5.000, 0.5), (10.00, 2.0), (20.00, 5.0)):
                if e >= lim:
                    de = step
        if k0 <= 1:
            if abs(e - b1) < 2.0 * de or abs(e - b2) < 2.0 * de or abs(e - b3) < 2.0 * de:
                de = de / 10.0
            e = e + de
        else:
            dl = 10.0 ** (math.log10(e) + de) - e
            if (abs(e - b1) < 2.0 * dl or abs(e - b2) < 2.0 * dl or abs(e - b3) < 2.0 * dl
                    or (eg0 < e < eg2)):
                de = de / 5.0
            e = 10.0 ** (math.log10(e) + de)
        out.append(e * acm)
        if len(out) > numenin + 2:  # 'Astro-warning: too many energy points'
            out = out[: numenin + 2]
            break
    return np.array(out, dtype=np.float64)


# ------------------------------------------------------------------------------------------------ partition function
def partition_function(t9: np.ndarray, levels: dict, grid: dict, density, Atarget: int, nonthermlev: int = -1,
                       astrogs: bool = False, ltarget: int = 0, numdiv: int = 100, numJ: int = 40) -> np.ndarray:
    """G(T9) of partfunc.f90 (normalised to 2 J_target + 1).

    `levels`: e (edis), j (jdis) of the target's levels 0..nlev, nlast (NL). `grid`: ex (Ex), dex (deltaEx), maxex
    of the target as a residual of the compound nucleus at the run's LAST incident energy (exgrid(0,0) is called
    after the energy loop). `density(E: ndarray, J: float, P: int) -> ndarray` is the target's level density
    (ground-state barrier, its ldmodel). Kept as TALYS has it: the last discrete level that passes the e^-80 cut
    is also the first point of the continuum trapezoid (sumjp(0)), bins are cut into `numdiv` points from
    Ex - deltaEx/2 + deltaEx/numdiv to Ex + deltaEx/2, `nonthermlev` is left out, nothing above max(maxex - 1, nlev).

    TALYS: partfunc.f90:1 (partfunc)
    Test: tests/hf/test_kwcov_b9.py
    """
    t9 = np.asarray(t9, dtype=F32)
    if astrogs:
        return np.ones(t9.shape[0])
    mevkt = F32(11.605)
    NL = int(levels["nlast"])
    edis = np.asarray(levels["e"], dtype=np.float64)
    jdis = np.asarray(levels["j"], dtype=np.float64)
    nlev = int(levels.get("nlev", len(edis) - 1))
    ex = np.asarray(grid["ex"], dtype=np.float64)
    dexa = np.asarray(grid["dex"], dtype=np.float64)
    maxex = int(grid["maxex"])
    # the continuum points (independent of T): (nexout, Elev) in TALYS's order, with sum_{J,P} (2J+1) rho dex
    pts_e, pts_w = [], []
    for nexout in range(0, max(maxex - 1, nlev) + 1):
        if nexout == nonthermlev or nexout <= NL:
            continue
        if nexout >= ex.shape[0] or nexout > maxex:
            continue  # TALYS reads Ex = deltaEx = 0 there (nothing: dex = 0)
        dex = F32(F32(dexa[nexout]) / F32(numdiv))
        if dex == 0.0:
            continue
        idiv = np.arange(1, numdiv + 1, dtype=F32)
        el = (F32(ex[nexout]) - F32(ex[ltarget]) + (idiv - F32(0.5) * F32(numdiv)) * dex).astype(F32)
        w = np.zeros(numdiv)
        for p in (-1, 1):
            for ir in range(numJ + 1):
                rs = ir + (Atarget % 2) / 2.0
                w += (2.0 * rs + 1.0) * np.asarray(density(el.astype(np.float64), rs, p), dtype=np.float64)
        pts_e.append(el)
        pts_w.append(w * float(dex))
    pe = np.concatenate(pts_e) if pts_e else np.zeros(0, dtype=F32)
    pw = np.concatenate(pts_w) if pts_w else np.zeros(0)
    out = np.zeros(t9.shape[0])
    for i, t in enumerate(t9):
        s = 0.0
        sj0 = 0.0
        for nexout in range(0, min(NL, len(edis) - 1) + 1):
            if nexout == nonthermlev:
                continue
            elev = F32(F32(edis[nexout]) - F32(edis[ltarget]))
            fex = float(mevkt * elev / t)
            if fex > 80.0:
                continue
            term = (2.0 * float(F32(jdis[nexout])) + 1.0) * math.exp(-fex)
            s += term
            sj0 = term
        fex = (mevkt * pe / t).astype(np.float64) if pe.size else np.zeros(0)
        keep = fex <= 80.0
        sj = np.concatenate([[sj0], (pw * np.exp(-np.where(keep, fex, 0.0)))[keep]])
        if sj.size > 1:
            s += float(np.sum(0.5 * (sj[:-1] + sj[1:])))
        out[i] = s / (2.0 * float(F32(jdis[ltarget])) + 1.0)
    return out


# ------------------------------------------------------------------------------------------------------------ rates
def maxwell_rate(e_lab: np.ndarray, xs_mb: np.ndarray, t9: np.ndarray, specmass: float, redumass: float,
                 partf: np.ndarray | None, k0: int = 1) -> tuple[np.ndarray, np.ndarray]:
    """(rate [cm3/mol/s], MACS [mb]) per T9 of stellarrate.f90:117-171 (one nucleus).

    TALYS: stellarrate.f90:1 (stellarrate)
    Test: tests/hf/test_kwcov_b9.py
    """
    e = (np.asarray(e_lab, np.float64) * specmass).astype(F32).astype(np.float64)
    n = e.shape[0]
    ee1 = np.concatenate([e[1:], e[-1:]])
    ee0 = np.concatenate([e[:1], e[:-1]])
    de = (ee1.astype(F32) - ee0.astype(F32)).astype(np.float64) / 2.0  # sgl ee1 - ee0, dE dbl
    xs = np.asarray(xs_mb, np.float64) / 1000.0
    am = F32(redumass)
    convfac = F32(F32(2.45484e5) / np.sqrt(am))
    rate = np.zeros(len(t9))
    macs = np.zeros(len(t9))
    for i, t in enumerate(np.asarray(t9, F32)):
        fact = 3.7335e10 / math.sqrt(float(am) * float(F32(t)) ** 3)  # fact is dbl, T9 sgl
        fex = (F32(11.605) * e.astype(F32) / t).astype(F32).astype(np.float64)
        keep = fex <= 80.0
        if k0 != 0:
            term = fact * e * xs * np.exp(-np.where(keep, fex, 0.0))
        else:
            term = 3.951776e17 * e ** 2 * xs / (np.exp(np.where(keep, fex, 0.0)) - 1.0)
        s = float(np.sum(np.where(keep, term * de, 0.0)))
        r = s if partf is None else s / partf[i]
        rate[i] = r
        macs[i] = r / float(F32(convfac * F32(np.sqrt(t))))
    return rate, macs


def astro_outputs(*, Z: int, A: int, k0: int, e_lab: np.ndarray, rp_mb: dict, fis_mb: np.ndarray | None,
                  specmass: float, redumass: float, t9: np.ndarray, et9: np.ndarray, partf: np.ndarray,
                  astrogs: bool, iso_mb: dict | None = None, flagastroex: bool = False, astroE: float = 0.0,
                  macs_exp: tuple | None = None, flagfission: bool = False) -> dict:
    """Every number astroout.f90 writes, as {file: {column: ndarray}} (columns in TALYS's order).

    `rp_mb[(Zcomp, Ncomp)]` = xspopnuc per incident energy (mb) for the nuclei within 4 protons / 4 neutrons of
    the compound nucleus; `iso_mb[(Zcomp, Ncomp, nex)]` = xspopex of the long-lived levels (astroex); `fis_mb`
    total fission. `macs_exp` = (MACS, dMACS) of gamma/macs/<El>.macs for macs.g (0, 0 if absent).

    TALYS: astroout.f90:1 (astroout), stellarrate.f90:1 (stellarrate)
    Test: tests/hf/test_kwcov_b9.py
    """
    from physics.hf.core.constants import nuclide_symbol as nuc

    pf = None if astrogs else partf
    Zcn, Acn = Z + PARZ[k0], A + PARZ[k0] + PARN[k0]
    rate, macs = {}, {}
    for (zc, nc), xs in rp_mb.items():
        if zc > NUMZASTRO or nc > NUMNASTRO:
            continue
        rate[(zc, nc)], macs[(zc, nc)] = maxwell_rate(e_lab, xs, t9, specmass, redumass, pf, k0)
    zero = np.zeros(len(t9))
    rfis = mfis = zero
    if fis_mb is not None and flagfission:
        rfis, mfis = maxwell_rate(e_lab, fis_mb, t9, specmass, redumass, pf, k0)
    out: dict = {}
    tag = f"({PARSYM[k0]},x)"
    gcol = partf if not astrogs else np.ones(len(t9))
    for acomp in range(0, NUMZASTRO + NUMNASTRO + 1):
        for zc in range(0, NUMZASTRO + 1):
            nc = acomp - zc
            if nc < 0 or nc > NUMNASTRO or (zc, nc) not in rate or not np.any(rate[(zc, nc)] > 0.0):
                continue
            zz, aa = Zcn - zc, Acn - zc - nc
            f = f"astrorate{zz:03d}{aa:03d}.tot"
            out[f] = {"T": t9, "reaction_rate": rate[(zc, nc)], "MACS": macs[(zc, nc)], "G(T)": gcol, "E-average": et9}
            if flagastroex and iso_mb:
                for (z2, n2, nex), xs in sorted(iso_mb.items()):
                    if (z2, n2) != (zc, nc):
                        continue
                    r, m = maxwell_rate(e_lab, xs, t9, specmass, redumass, pf, k0)
                    br = np.where(rate[(zc, nc)] > 0, r / np.where(rate[(zc, nc)] > 0, rate[(zc, nc)], 1.0), 0.0)
                    out[f"astrorate{zz:03d}{aa:03d}.L{nex:02d}"] = {"T": t9, "reaction_rate": r, "MACS": m,
                                                                     "Branching_ratio": br, "E-average": et9}
    if 0.029 <= astroE <= 0.031:
        mx, dmx = macs_exp if macs_exp else (0.0, 0.0)
        m0 = float(macs.get((0, 0), zero)[0])
        out["macs.g"] = {"Z": np.array([Z]), "A": np.array([A]), "MACS(mb)": np.array([m0]), "Exp(mb)": np.array([mx]),
                         "dEXP(mb)": np.array([dmx]), "MACS/Exp": np.array([m0 / mx if mx > 0 else 0.0])}
    for sym, (zc, nc) in (("g", (0, 0)), ("p", (1, 0)), ("a", (2, 2))):
        r = rate.get((zc, nc), zero)
        m = macs.get((zc, nc), zero)
        out[f"astrorate.{sym}"] = {"T": t9, "reaction_rate": r, "MACS": m, "G(T)": gcol, "E-average": et9}
        if flagastroex and iso_mb and any((z2, n2) == (zc, nc) and nex > 0 for (z2, n2, nex) in iso_mb):
            for (z2, n2, nex), xs in sorted(iso_mb.items()):
                if (z2, n2) != (zc, nc):
                    continue
                ri, mi = maxwell_rate(e_lab, xs, t9, specmass, redumass, pf, k0)
                br = np.where(r > 0, ri / np.where(r > 0, r, 1.0), 0.0)
                out[f"astrorate.{sym}.L{nex:02d}"] = {"T": t9, "reaction_rate": ri, "MACS": mi, "Branching_ratio": br,
                                                      "G(T)": gcol, "E-average": et9}
    if flagfission:
        out["astrorate.f"] = {"T": t9, "reaction_rate": rfis, "MACS": mfis, "G(T)": gcol, "E-average": et9}
    # astrorate.tot: G, (k0,g) (k0,n) (k0,p) (k0,a), fission, then every other product with a rate > 1e-10
    tot = {"T": t9, "G(T)": gcol}
    for (zc, nc), lab in (((0, 0), "g"), ((0, 1), "n"), ((1, 0), "p"), ((2, 2), "a")):
        tot[f"({PARSYM[k0]},{lab}){nuc(Zcn - zc)}{Acn - zc - nc}"] = rate.get((zc, nc), zero)
    tot["fission"] = rfis
    for acomp in range(0, NUMZASTRO + NUMNASTRO + 1):
        for zc in range(0, NUMZASTRO + 1):
            nc = acomp - zc
            if nc < 0 or nc > NUMNASTRO or (zc, nc) in ((0, 0), (0, 1), (1, 0), (2, 2)):
                continue
            r = rate.get((zc, nc))
            if r is not None and np.any(r > 1.0e-10):
                tot[f"{nuc(Zcn - zc)}{Acn - zc - nc}"] = r
    out["astrorate.tot"] = tot
    out["_meta"] = {"tag": tag, "astrogs": astrogs}
    return out


def macs_experimental(Z: int, A: int) -> tuple[float, float]:
    """(MACS, dMACS) [mb] at 30 keV from structure/gamma/macs/<El>.macs (astroout.f90:236-262), (0, 0) if absent.

    TALYS: astroout.f90:1 (astroout)
    Test: tests/hf/test_kwcov_b9.py
    """
    from physics.hf.core.constants import nuclide_symbol
    from physics.hf.structure.files import talys_structure_dir

    p = Path(talys_structure_dir()) / "gamma" / "macs" / f"{nuclide_symbol(Z)}.macs"
    if not p.is_file():
        return 0.0, 0.0
    for line in p.read_text(errors="replace").splitlines():
        try:
            ia, xs, dxs = int(line[4:8]), float(line[8:20]), float(line[20:32])
        except ValueError:
            break
        if ia == A:
            return xs, dxs
    return 0.0, 0.0


def write_files(out: dict, directory: str | Path) -> list[str]:
    """Write the astro files (data block only, TALYS's 15-character columns, YANDF-style '#' header lines).

    TALYS: astroout.f90:1 (astroout)
    Test: tests/hf/test_kwcov_b9.py
    """
    d = Path(directory)
    d.mkdir(parents=True, exist_ok=True)
    names = []
    for f, cols in out.items():
        if f.startswith("_"):
            continue
        keys = list(cols)
        rows = np.column_stack([np.asarray(cols[k], dtype=np.float64) for k in keys])
        with open(d / f, "w") as fo:
            fo.write(f"# {f} (INCOGNITA port of TALYS astroout)\n")
            fo.write("##" + "".join(f"{k:>15s}" for k in keys)[2:] + "\n")
            if f == "macs.g":
                fo.write("".join(f"{int(v):4d}" for v in rows[0, :2]) + "".join(f"{v:12.5E}" for v in rows[0, 2:]) + "\n")
            else:
                for r in rows:
                    fo.write("".join(f"{v:15.6E}" for v in r) + "\n")
        names.append(f)
    return names


def read_stock(path: str | Path) -> dict[str, np.ndarray]:
    """A stock TALYS astro file as {column: ndarray} (the '##' header line names the columns).

    TALYS: astroout.f90:1 (astroout) -- the format it writes
    Test: tests/hf/test_kwcov_b9.py
    """
    lines = Path(path).read_text(errors="replace").splitlines()
    cols = None
    rows = []
    for s in lines:
        if s.startswith("##") and cols is None:
            cols = s[2:].split()
            continue
        if s.startswith("#") or not s.strip():
            continue
        rows.append([float(x) for x in s.split()])
    a = np.array(rows, dtype=np.float64)
    if cols is None or len(cols) != a.shape[1]:
        cols = [f"c{i}" for i in range(a.shape[1])]
    return {c: a[:, i] for i, c in enumerate(cols)}
