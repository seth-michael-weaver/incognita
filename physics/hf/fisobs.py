"""KWCOV B8 (FISOBS): fission extras on TALYS's keywords, OUTPUT ONLY.

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

What it gives (TALYS's file names without the incident energy; arrays on the run's energies):

    Results.extras
      rpZZZAAA.fis              fission cross section per fissioning nuclide, xsfeed(Zcomp, Ncomp, -1) (C,) mb
                                (fissionout.f90:1, the `4b` table / filefission files; 0 where TALYS writes 0)
      pfns.fis:E-average        average energy of the Iwamoto total fission neutron spectrum (C,) MeV (Eavpfns)
      nubarn.tot:wahl           prompt nubar of the Wahl systematics, nubarWahl(Einc) (C,) (totalxs.f90:124). TALYS-2.25
                                computes it and never writes it (massdis.f90:252 resets nubar before nubarout), so
                                this is the port's only reader of cnubar1 / cnubar2
    Results.spectra
      pfns.fis                  prompt fission neutron spectrum (C, NEpfns) 1/MeV, column 2 of pfnsEEEE.EEE.fis
      pfns.fis:E                the PFNS grid Epfns (C, NEpfns) MeV (strucinitial.f90:631-655)
      pfns.fis:Maxwell_ratio    column 3, total (prompt + scission) spectrum / Maxwellian of the same mean energy
      pfns.fis:CM               column 4, the centre-of-mass spectrum
      fisZZZAAA.feed            fisfeed y: fisfeedex(Zcomp, Ncomp, nex), fission per excitation bin (C, M) mb
                                (column `Population` of fisZZZAAAEeeee.eee.feed, multiple.f90:884); NaN padded
      fisZZZAAA.feed:Ex         its Ex column (C, M) MeV

Switches: the deck keywords `filefission y`, `fisfeed y`, `outfission y`, an explicit `pfnsmodel`, `cnubar1`, `cnubar2`,
`tmadjust`, `fsadjust` (values != 1), or the port switch `INCOGNITA_FISOBS=1`, on a run with fission. Default: none of
them, nothing is computed and every Results array is unchanged. `pfnsmodel 2` (PFNS from fission-fragment decay, needs
massdis y, B14) writes no Iwamoto spectrum, as TALYS (fissionout.f90:135).

Not given: the J-parity columns of the fisfeed files (fisfeedJP, compound.f90: the engine's decay kernels sum the
fission feed over J and parity); the per-fragment / scission columns of Tfns.tot and phiTav.tot (iwamoto's
scratch files).

TALYS routines ported here (file:line of the subroutine statement):
    iwamoto.f90:1 (iwamoto) + inverse_xs, cmfns, labfns   the Iwamoto PFNS, single precision as TALYS
    nubarWahl.f90:1 (nubarWahl)                           Wahl nubar systematics
    fissionout.f90:1 (fissionout)                         per-fissioning-nuclide table, the PFNS call
    pfnsout.f90:1 (pfnsout)                               columns
    strucinitial.f90:631-655                              the PFNS energy grid
Task: T10 (physics/hf/CONTRACT.md section 7; KWCOV batch B8, output only). Acceptance test: KWCOV-B8
(tests/hf/test_kwcov_b8.py, scripts/kwcov/b8_response.py, docs/hf/COVERAGE_PLAN.md).
"""

from __future__ import annotations

import math
import os

import numpy as np

ENV = "INCOGNITA_FISOBS"
NUMPFNS = 600  # A0_talys_mod.f90:102
NGRID = 20000  # iwamoto.f90: Ngrid
NT = 100  # cmfns: nT
F = np.float32

_SET: dict | None = None
_REC: list = []  # per kept energy: {"E": Einc, "rp": {(Z, A): mb}, "feed": {(Z, A): (Ex, pop)}}


def _on(v) -> bool:
    v = str(v).strip().lower()
    return v[:1] in ("1", "y", "t") or v == "on"


def _param(params, name: str) -> float:
    try:
        return float(params.at(name))
    except Exception:  # noqa: BLE001 -- Params without the key: TALYS's default
        return 1.0


def settings(options, params=None) -> dict | None:
    """The run's fission-output switches, or None when none is set (or the run has no fission).

    TALYS: fissionout.f90:1 (fissionout) [filefission, pfnsmodel]; multiple.f90 line 884 [fisfeed];
    input_fissionpar.f90:128-131
    Test: tests/hf/test_kwcov_b8.py
    """
    if options is None:
        return None
    adj = {k: _param(params, k) if params is not None else 1.0 for k in ("cnubar1", "cnubar2", "tmadjust", "fsadjust")}
    for k, v in adj.items():  # checkvalue.f90:1089-1092 (TALYS stops)
        if not 0.1 <= v <= 10.0:
            raise ValueError(f"{k} {v}: outside 0.1..10 (TALYS-error, checkvalue.f90:1089-1092)")
    if int(getattr(options, "pfnsmodel", 1)) not in (1, 2):
        raise ValueError(f"pfnsmodel {options.pfnsmodel}: outside 1..2 (TALYS-error, checkvalue.f90:1087)")
    if not 0.0 <= float(getattr(options, "Rfiseps", 1e-3)) <= 1.0:
        raise ValueError(f"rfiseps {options.Rfiseps}: outside 0..1 (TALYS-error, checkvalue.f90:479)")
    if not bool(getattr(options, "flagfission", False)):
        return None
    expl = getattr(options, "is_explicit", lambda k: False)
    on = (_on(os.environ.get(ENV, "0")) or bool(getattr(options, "filefission", False))
          or bool(options.flagfisfeed) or bool(getattr(options, "flagfisout", False)) or expl("pfnsmodel")
          or any(v != 1.0 for v in adj.values()))
    if not on:
        return None
    return {"feed": bool(options.flagfisfeed) or _on(os.environ.get(ENV, "0")), "pfnsmodel": int(options.pfnsmodel),
            **adj}


def begin_run(cas) -> bool:
    """Fix the run's switches from its Options / Params (engine_c.cases, before the energy loop).

    TALYS: (none -- a port switch)
    Test: tests/hf/test_kwcov_b8.py
    """
    global _SET
    _REC.clear()
    s = settings(cas.options, cas.params)
    if s is not None:
        k0 = int(cas.k0)
        zc, ac = int(cas.Zc), int(cas.Ac)
        s.update(Zinit=zc, Ainit=ac, Ninit=ac - zc, Sn=float(np.float32(float(cas.m.s_mev[0, 0, 1]))), k0=k0)
    _SET = s
    return s is not None


def active() -> bool:
    """Whether this run records the fission extras.

    TALYS: (none -- a port switch)
    Test: tests/hf/test_kwcov_b8.py
    """
    return _SET is not None


def record(cas, st, e_inc_mev: float, etot_mev: float, mres) -> None:
    """One kept energy: the per-nucleus fission and, with fisfeed, the per-bin fission off `mres` (MultipleResult).

    TALYS: fissionout.f90:28-37 (xsfeed(Zcomp, Ncomp, -1) /= 0), multiple.f90:884-930 (fisfeedex rows 0..nen,
    nen = maxex + 1 for the initial compound nucleus, whose top row is the binary fission)
    Test: tests/hf/test_kwcov_b8.py
    """
    if _SET is None:
        return
    rp, feed = {}, {}
    if mres is not None:
        for key, xf in mres.xsfeed_mb.items():
            v = float(xf.get(-1, 0.0))
            if v != 0.0:
                rp[cas.zn(*key)] = v
        if _SET["feed"]:
            for key, ff in mres.fisfeedex_mb.items():
                if key != (0, 0) and key not in mres.decayed:
                    continue
                sp = st.spec.get(key)
                if sp is None:
                    continue
                nen = sp.maxex + 1 if key == (0, 0) else sp.maxex
                ex = np.zeros(nen + 1)
                ex[: sp.maxex + 1] = np.asarray(sp.ex_mev[: sp.maxex + 1], dtype=float)
                if nen > sp.maxex:
                    ex[nen] = etot_mev
                pop = np.array([float(ff.get(n, 0.0)) for n in range(nen + 1)])
                feed[cas.zn(*key)] = (ex, pop)
    _REC.append({"E": float(e_inc_mev), "rp": rp, "feed": feed, "missing": mres is None})


# ------------------------------------------------------------------------------------------------ TALYS formulas
def pfns_grid() -> np.ndarray:
    """Epfns, the PFNS outgoing-energy grid, single precision.

    TALYS: strucinitial.f90:631-655
    Test: tests/hf/test_kwcov_b8.py
    """
    out = []
    eout, degrid = F(0.0), F(0.001)
    while True:
        eout = F(eout + degrid)
        eeps = F(eout + F(1.0e-4))
        if eeps > 50.0 or len(out) == NUMPFNS:
            break
        out.append(eout)
        if eeps > 0.01:
            degrid = F(0.01)
        if eeps > 0.2:
            degrid = F(0.02)
        if eeps > 0.5:
            degrid = F(0.025)
        if eeps > 3.0:
            degrid = F(0.1)
        if eeps > 10.0:
            degrid = F(0.5)
    return np.array(out, dtype=F)


def _inverse_xs(emax: np.float32):
    """iwamoto.f90 inverse_xs: Egrid(0:Ngrid) and sigma(1:Ngrid) [mb]."""
    pi = F(3.14159265358979323)
    hbar, clight = F(6.5821220e-22), F(2.99792458e8)
    hbarc = F(F(hbar * clight) * F(1.0e15))
    amu = F(931.49386)
    parmass = F(F(1.008664904) * amu)
    a100, r0 = F(100.0), F(1.2)
    r = F(r0 * F(a100 ** F(1.0 / 3.0)))
    sigma0 = F(pi * r * r)
    s0, sqrt1ev = F(1.0e-4), F(1.0e-3)
    alpha = F(F(F(F(pi * hbarc) * hbarc) * s0) / F(F(F(parmass * r0) * r0) * F(a100 ** F(2.0 / 3.0)) * sqrt1ev))
    degrid = F(emax / F(NGRID))
    egrid = np.zeros(NGRID + 1, dtype=F)
    egrid[1:] = (degrid * np.arange(1, NGRID + 1, dtype=F)).astype(F)
    e = egrid[1:]
    sigma = (sigma0 * (F(1.0) + alpha / np.sqrt(e)) * F(10.0)).astype(F)
    return egrid, sigma


def _cmfns(egrid, sigma, tm: np.float32, emax: np.float32) -> np.ndarray:
    """iwamoto.f90 cmfns: the temperature-averaged CM spectrum phiTav(1:Ngrid)."""
    dt = F(tm / F(NT))
    degrid = F(emax / F(NGRID))
    e = egrid[1:]
    phi = np.zeros(NGRID, dtype=F)
    for it in range(1, NT + 1):
        t = F(F(it - 0.5) * dt)
        pt = F(F(F(2.0) * t) / F(tm * tm))
        w = (sigma * e * np.exp(-e / t)).astype(F)
        kt = F(F(w.sum(dtype=np.float64)) * degrid)
        if kt > 0.0:
            phi += (w / kt).astype(F) * pt
    return (phi * dt).astype(F)


def _labfns(e: np.float32, ef: np.float32, phi, egrid) -> np.float32:
    """iwamoto.f90 labfns: the CM spectrum boosted to the lab for a fragment of energy Ef per nucleon."""
    emin = F((math.sqrt(e) - math.sqrt(ef)) ** 2)
    eplus = F((math.sqrt(e) + math.sqrt(ef)) ** 2)
    factor = F(1.0 / (4.0 * math.sqrt(ef)))
    eg = egrid[1:]
    m = (eg > emin) & (eg <= eplus)
    if not m.any():
        return F(0.0)
    de = (eg[m] - np.maximum(egrid[:-1][m], emin)).astype(F)
    return F(factor * F((phi[m] / np.sqrt(eg[m]) * de).sum(dtype=np.float64)))


def iwamoto(Z: int, A: int, sn: float, ein: float, tmadjust: float = 1.0, fsadjust: float = 1.0,
            etfns: np.ndarray | None = None) -> dict:
    """The Iwamoto prompt fission neutron spectrum: {E, pfns, maxwell_ratio, cm, tfns, eav}.

    TALYS: iwamoto.f90:1 (iwamoto)
    Test: tests/hf/test_kwcov_b8.py
    """
    et = pfns_grid() if etfns is None else np.asarray(etfns, dtype=F)
    n = et.shape[0]
    za13 = F(F(Z) / F(F(A) ** F(1.0 / 3.0)))
    tke = F(F(F(0.1189) * F(Z)) * za13 + F(7.3))
    ah = 145
    al = A - ah
    efh = F(F(F(al) / F(ah)) * tke / F(A))
    efl = F(F(F(ah) / F(al)) * tke / F(A))
    tm0 = F(F(tmadjust) * F(F(0.45) * za13 - F(5.82)))
    ex = F(max(F(F(ein) + F(sn)), F(0.0)))
    ald = F(F(A) / F(10.0))
    tm = F(math.sqrt(F(F(tm0 * tm0) + F(ex / ald))))
    emax = et[-1]
    fs = F(F(fsadjust) * F(F(0.11) / F(F(1.0) + F(math.exp(F(F(15.0) - za13) / F(0.1))))))
    egrid, sigma = _inverse_xs(emax)
    phi = _cmfns(egrid, sigma, tm, emax)
    det = np.zeros(n, dtype=F)
    det[1:-1] = F(0.5) * (et[2:] - et[:-2])
    det[0] = et[0]
    det[-1] = F(0.5) * (et[-1] - et[-2])
    pf, cm, tf = np.zeros(n, dtype=F), np.zeros(n, dtype=F), np.zeros(n, dtype=F)
    esum = ssum = 0.0
    for i in range(n):
        e = et[i]
        nen2 = max(int(F(F(e * F(NGRID)) / emax)), 1)
        sfns0 = phi[nen2 - 1]
        scission = F(fs * sfns0)
        for ef in (efl, efh):
            prompt = F(F(F(1.0) - fs) * _labfns(e, ef, phi, egrid))
            promptcm = F(F(F(1.0) - fs) * sfns0)
            pf[i] = F(pf[i] + F(F(0.5) * prompt))
            cm[i] = F(cm[i] + F(F(0.5) * promptcm))
        tf[i] = F(pf[i] + scission)
        esum = F(esum + F(F(tf[i] * e) * det[i]))
        ssum = F(ssum + F(tf[i] * det[i]))
    eav = F(esum / ssum)
    ratio = np.zeros(n, dtype=F)
    if eav > 0.0:
        maxfactor = F(F(2.0) / F(math.sqrt(F(F(3.14159265358979323) * F(eav ** 3)))))
        mw = (maxfactor * np.sqrt(et) * np.exp(-et / F(F(2.0 / 3.0) * eav))).astype(F)
        summax = F((mw * det).sum(dtype=np.float64))
        if summax > 0.0:
            mw = (mw / summax).astype(F)
            ok = mw > 0.0
            ratio[ok] = tf[ok] / mw[ok]
    return {"E": et.astype(float), "pfns": pf.astype(float), "maxwell_ratio": ratio.astype(float),
            "cm": cm.astype(float), "tfns": tf.astype(float), "eav": float(eav)}


def nubar_wahl(Zinit: int, Ainit: int, bn: float, ein: float, cnubar1: float = 1.0, cnubar2: float = 1.0) -> float:
    """Prompt nubar of the Wahl systematics for the compound nucleus (Zinit, Ainit), Bn = S(0, 0, 1).

    TALYS: nubarWahl.f90:1 (nubarWahl)
    Test: tests/hf/test_kwcov_b8.py
    """
    ninit = Ainit - Zinit
    fz = 1.0 if Zinit % 2 == 0 else -1.0
    fn = 1.0 if ninit % 2 == 0 else -1.0
    term1 = F(F(2.286) + F(0.147) * F(Zinit - 92) + F(0.054) * F(Ainit - 236) + F(0.040) * F(2.0 - fz - fn))
    term2 = F(0.0)
    if ein > 0.0:
        th = F(F(11.47) - F(F(F(0.166) * F(Zinit) * F(Zinit)) / F(Ainit)) + F(0.093) * F(2.0 - fz - fn) - F(bn))
        term2 = F(F(F(0.145) - F(0.0043) * F(Ainit - 236)) * F(F(ein) - th))
    return float(F(F(cnubar1) * term1 + F(cnubar2) * term2))


# ------------------------------------------------------------------------------------------------ Results
def build() -> tuple[dict, dict]:
    """(extras, spectra) of the recorded run.

    TALYS: fissionout.f90:1 (fissionout), pfnsout.f90:1 (pfnsout)
    Test: tests/hf/test_kwcov_b8.py
    """
    s = _SET
    rec = _REC
    C = len(rec)
    extras: dict[str, np.ndarray] = {}
    spectra: dict[str, np.ndarray] = {}
    if C == 0:
        return extras, spectra
    nuclei = sorted({k for r in rec for k in r["rp"]}, key=lambda x: (-x[1], -x[0]))
    for Z, A in nuclei:
        extras[f"rp{Z:03d}{A:03d}.fis"] = np.array([r["rp"].get((Z, A), 0.0) for r in rec])
    extras["nubarn.tot:wahl"] = np.array([nubar_wahl(s["Zinit"], s["Ainit"], s["Sn"], r["E"], s["cnubar1"],
                                                     s["cnubar2"]) for r in rec])
    if s["pfnsmodel"] == 1:  # fissionout.f90:135
        rows = [iwamoto(s["Zinit"], s["Ainit"], s["Sn"], r["E"], s["tmadjust"], s["fsadjust"]) for r in rec]
        extras["pfns.fis:E-average"] = np.array([x["eav"] for x in rows])
        spectra["pfns.fis"] = np.stack([x["pfns"] for x in rows])
        spectra["pfns.fis:E"] = np.stack([x["E"] for x in rows])
        spectra["pfns.fis:Maxwell_ratio"] = np.stack([x["maxwell_ratio"] for x in rows])
        spectra["pfns.fis:CM"] = np.stack([x["cm"] for x in rows])
    if s["feed"]:
        for Z, A in sorted({k for r in rec for k in r["feed"]}, key=lambda x: (-x[1], -x[0])):
            m = max(r["feed"][(Z, A)][0].shape[0] for r in rec if (Z, A) in r["feed"])
            ex, pop = np.full((C, m), np.nan), np.full((C, m), np.nan)
            for i, r in enumerate(rec):
                if (Z, A) in r["feed"]:
                    e, p = r["feed"][(Z, A)]
                    ex[i, : e.shape[0]], pop[i, : p.shape[0]] = e, p
            spectra[f"fis{Z:03d}{A:03d}.feed"] = pop
            spectra[f"fis{Z:03d}{A:03d}.feed:Ex"] = ex
    return extras, spectra


def add_to_results(res, injection=None):
    """End of engine_c.run (after specobs): the fission extras into Results.extras / Results.spectra. Unchanged when
    no switch is on.

    TALYS: fissionout.f90:1, pfnsout.f90:1, multiple.f90:884
    Test: tests/hf/test_kwcov_b8.py
    """
    global _SET
    if _SET is None:
        return res
    import warnings
    from dataclasses import replace

    import torch

    try:
        if any(r["missing"] for r in _REC):
            warnings.warn("FISOBS: the per-nucleus fission of some energies was not recorded (no cascade result)",
                          stacklevel=2)
        extras, spectra = build()
        if len(_REC) != res.n:
            raise RuntimeError(f"FISOBS: {len(_REC)} recorded energies for {res.n} results")
        ex = dict(res.extras)
        ex.update({k: torch.as_tensor(v, dtype=torch.float64) for k, v in extras.items()})
        sp = dict(res.spectra)
        sp.update({k: torch.as_tensor(v, dtype=torch.float64) for k, v in spectra.items()})
        res = replace(res, extras=ex, spectra=sp)
    finally:
        _SET = None
        _REC.clear()
    return res
