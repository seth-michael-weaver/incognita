"""The exciton-model branches the vectorised two-component path (`preeq.exciton`) does not carry:
the one-component model (`twocomponent n`), shell-damped single-particle densities (`gshell y`) and
optical-model transition rates (`preeqmode 3`).

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

Task: T8 (physics/hf/CONTRACT.md §7), KWCOV B7 (docs/hf/COVERAGE_PLAN.md). Acceptance test: A-pe (§6); the
response vs stock TALYS-2.25 is scripts/kwcov/b7_response.py, the unit checks tests/hf/test_kwcov_b7.py.

TALYS routines ported here (file:line of the subroutine/function statement):
    exciton.f90:1 (exciton)
    lifetime.f90:1 (lifetime)
    emissionrate.f90:1 (emissionrate)
    emissionrate2.f90:1 (emissionrate2)
    lambdaplus.f90:1 (lambdaplus)
    lambdapiplus.f90:1 (lambdapiplus)
    lambdanuplus.f90:1 (lambdanuplus)
    lambdapinu.f90:1 (lambdapinu)
    lambdanupi.f90:1 (lambdanupi)
    phdens.f90:1 (phdens)
    excitoninit.f90:1 (excitoninit)
    bonetti.f90:1 (bonetti)
    matrix.f90:1 (matrix)

Only runs when one of the three switches is set (`active`); a default run never reaches this module, so it
does not move a default number. It is a plain transcription: one exciton state at a time, numpy over the
emission grid and over the `nexcbins` integration points, float64, no autograd. The two-component result is
handed to `preeq.exciton.exchange_and_lifetime` (exchange2/lifetime2) unchanged; with all three switches off it
reproduces `exciton.emission_rates` / `exciton.transition_rates` (tests/hf/test_kwcov_b7.py), which is the check
that the transcription is the vectorised path's physics.

TALYS quirks kept on purpose (each one changes numbers):
  * gshell: every numerical transition rate damps all four collision densities with g(U) of its FIRST channel
    (`uupip` in lambdapiplus, `uunup` in lambdanuplus) and every residual density with g(U - that energy);
    lambdanupi damps its residual with g(uu) instead of g(U - uu) (lambdanupi.f90:185). The Pauli tables
    Apauli/Apauli2 keep the undamped compound-nucleus g (preeqinit.f90).
  * one-component photon emission uses gsg = Atarget / 13, undamped (emissionrate.f90:113), and only
    `wemispart(0)` is cleared for a photon-only state, not `wemistot` (emissionrate.f90:239).
  * preeqmode 3: the absorptive potential of the TARGET is averaged over its volume for neutrons and protons
    down to -8 MeV (bonetti.f90); the rate at `eopt = uu - S` reads bin int(10 eopt), zero above the table.
"""

from __future__ import annotations

import math

import numpy as np
import torch

from physics.hf.core.constants import talys_constants
from physics.hf.core.tensors import DTYPE
from physics.hf.density.particle_hole import (
    _NFAC_NP,
    EFERMI_MEV,
    NUMPARX,
    PHDENS_FLOOR,
    _apauli2_arr,
    _finitewell_arr,
    _phdens2_arr,
)

PARZ = (0, 0, 1, 1, 1, 2, 2)
PARN = (0, 1, 0, 1, 2, 1, 2)
PARA = (0, 1, 1, 2, 3, 3, 4)
NUMEN_TALYS = 260  # A0_talys_mod.f90:59, the wvol table bound of bonetti.f90


def active(options) -> bool:
    """True when the run sets a switch only this module implements.

    TALYS: (none -- the dispatch of preeq.f90:113-117 and the preeqmode/flaggshell branches)
    Test: tests/hf/test_kwcov_b7.py
    """
    return (not bool(getattr(options, "flag2comp", True))) or bool(getattr(options, "flaggshell", False)) \
        or int(getattr(options, "preeqmode", 2)) == 3


# ------------------------------------------------------------------------------------------- set-up


def extras(Z: int, A: int, k0: int, options, params, m, enincmax_mev: float, kph: float) -> dict:
    """What the three branches read beyond `PreeqInputs`: the one-component g of the compound nucleus and of
    the seven binary residuals, their level-density objects for the shell damping, the separation energies the
    optical-model rates use, and bonetti's `wvol` table.

    TALYS: excitoninit.f90:1 (excitoninit), bonetti.f90:1 (bonetti)
    Test: tests/hf/test_kwcov_b7.py
    """
    from physics.hf.preeq.prepare import exciton_densities
    from physics.hf.projectile import compound_of

    c = talys_constants()
    Zc, Ac = compound_of(Z, A)
    ext: dict = {"Ztarget": Z, "Atarget": A, "Zinit": Zc, "Ainit": Ac, "Ninit": Ac - Zc, "k0": k0}
    g = []
    for t in range(7):
        Zr, Ar = Zc - c["parZ"][t], Ac - c["parA"][t]
        g.append(float(exciton_densities(Zr, Ar - Zr, kph, params, options)[0]))
    ext["g"] = g  # g(Zix, Nix) of the residual of type t; t = 0 is the compound nucleus itself
    ext["s"] = {(zi, ni, k): float(m.s_mev[zi, ni, k]) for zi, ni, k in ((0, 1, 1), (1, 0, 2), (0, 0, 1), (0, 0, 2))}
    if bool(getattr(options, "flaggshell", False)):
        from physics.hf.density.parameters import densitypar
        from physics.hf.structure.levels import discrete_levels

        lds = []
        for t in range(7):
            Zr, Ar = Zc - c["parZ"][t], Ac - c["parA"][t]
            lds.append(densitypar(Zr, Ar, options, params, m, discrete_levels(Zr, Ar, options, m, params)))
        ext["ld"] = lds
    if int(getattr(options, "preeqmode", 2)) == 3:
        if bool(getattr(options, "flagjlm", False)):
            raise NotImplementedError("preeqmode 3 with jlmomp y: bonetti.f90's JLM branch is not ported")
        ext["wvol"] = wvol_table(Z, A, k0, options, params, enincmax_mev + float(m.s_mev[0, 0, k0]))
    return ext


def wvol_table(Z: int, A: int, k0: int, options, params, emax_mev: float) -> dict[int, np.ndarray]:
    """`wvol(k, nen)` [MeV], k = 1 (n), 2 (p), nen = -200 .. 10 numen as an array at offset 200: the imaginary
    potential of the target averaged over its volume, `int(W fws + 4 awd Wd dfws) fws r^2 / int fws r^2`
    (Woods-Saxon volume form factor as the weight), at e = 0.1 nen MeV; below -8 MeV the -8 MeV value; zero above
    `nenend = 10 min(numen, int(emax + 1))`.

    TALYS: bonetti.f90:1 (bonetti)
    Test: tests/hf/test_kwcov_b7.py
    """
    from physics.hf.omp.parameters import omp_parameters

    onethird = 1.0 / 3.0
    nenend = 10 * min(NUMEN_TALYS, int(emax_mev + 1.0))
    out = {}
    nrbins = 50
    dr = 20.0 / nrbins
    rr = (np.arange(1, nrbins + 1) - 0.5) * dr
    for k in (1, 2):
        tab = np.zeros(200 + 10 * NUMEN_TALYS + 1)
        nens = np.arange(-80, nenend + 1)
        e = torch.tensor(0.1 * nens, dtype=DTYPE)
        o = omp_parameters(Z, A - Z, k, e, params, options)
        g = {c: np.asarray(getattr(o, c), float).reshape(-1) for c in ("w_mev", "rw_fm", "aw_fm", "wd_mev",
                                                                        "rwd_fm", "awd_fm")}
        at = float(A) ** onethird
        for i, nen in enumerate(nens):
            radv, radd = g["rw_fm"][i] * at, g["rwd_fm"][i] * at
            aw, awd, w, wd = g["aw_fm"][i], g["awd_fm"][i], g["w_mev"][i], g["wd_mev"][i]
            sum1 = sum2 = 0.0
            for r in rr:
                expo = (r - radv) / aw
                fwsvol = 1.0 / (1.0 + math.exp(expo)) if expo <= 80.0 else 0.0
                expo = (r - radd) / awd
                fwssurf = -math.exp(expo) / (awd * (1.0 + math.exp(expo) ** 2)) if expo <= 80.0 else 0.0
                term2 = fwsvol * r * r * dr
                sum1 += term2 * (w * fwsvol - 4.0 * awd * wd * fwssurf)
                sum2 += term2
            if sum2 != 0.0:
                tab[200 + nen] = sum1 / sum2
        tab[0:120] = tab[200 - 80]  # nen = -200 .. -81
        out[k] = tab
    return out


# ------------------------------------------------------------------------------------- densities


def _arr(x) -> np.ndarray:
    return np.atleast_1d(np.asarray(x, dtype=np.float64))


def _nf(n: int) -> float:
    return float(_NFAC_NP[n])


class _Densities:
    """phdens / phdens2 with TALYS's compound-nucleus Pauli tables (preeqinit.f90:84-119)."""

    def __init__(self, g0: float, gp0: float, gn0: float):
        self.g0, self.gp0, self.gn0 = g0, gp0, gn0

    def apauli(self, p: int, h: int) -> float:
        if p == -1 or h == -1:
            return 0.0
        return max(p, h) ** 2 / self.g0 - (p * p + h * h + p + h) / (4.0 * self.g0)

    def apauli2(self, ppi: int, hpi: int, pnu: int, hnu: int) -> float:
        a = lambda v: np.array([v], dtype=np.int64)  # noqa: E731
        return float(_apauli2_arr(a(ppi), a(hpi), a(pnu), a(hnu), self.gp0, self.gn0)[0])

    def ph1(self, p: int, h: int, gs, ex, ewell: float, surf: bool) -> np.ndarray:
        """phdens.f90:59-78 (phmodel 1)."""
        ex = _arr(ex)
        gs = np.broadcast_to(_arr(gs), ex.shape)
        if p < 0 or h < 0 or p + h == 0:
            return np.zeros_like(ex)
        ap = self.apauli(p, h)
        factor = (p * p + h * h + p + h) / (4.0 * gs)
        ok = ap + factor < ex
        n1 = p + h - 1
        fac1 = _nf(p) * _nf(h) * _nf(n1)
        u = np.where(ok, ex - ap, 1.0)
        sh = ex.shape
        fw = _finitewell_arr(np.full(sh, p, np.int64), np.full(sh, h, np.int64), ex, np.full(sh, float(ewell)),
                             np.full(sh, bool(surf)), EFERMI_MEV)
        dens = gs ** (p + h) / fac1 * u ** n1 * fw
        dens = np.where(ok, dens, 0.0)
        return np.where(dens < PHDENS_FLOOR, 0.0, dens)

    def ph2(self, ppi: int, hpi: int, pnu: int, hnu: int, gsp, gsn, ex, ewell: float, surf: bool) -> np.ndarray:
        """phdens2.f90:58-79 (phmodel 1), Apauli2 from the table."""
        ex = _arr(ex)
        sh = ex.shape
        i = lambda v: np.full(sh, v, np.int64)  # noqa: E731
        f = lambda v: np.ascontiguousarray(np.broadcast_to(_arr(v), sh), dtype=np.float64)  # noqa: E731
        ap = self.apauli2(ppi, hpi, pnu, hnu)
        return np.asarray(_phdens2_arr(i(ppi), i(hpi), i(pnu), i(hnu), f(gsp), f(gsn), ex, f(ewell),
                                       np.full(sh, bool(surf)), f(ap), EFERMI_MEV), dtype=np.float64)


def _preeqpair(pair_cn: float, gs: float, n: int, e, pairmodel: int) -> np.ndarray:
    """preeqpair.f90:44-70; `gs` is gp + gn (two components) or g (one), undamped."""
    e = _arr(e)
    if pair_cn <= 0.0:
        return np.zeros_like(e)
    if pairmodel != 1:
        return np.full_like(e, pair_cn)
    pair0 = math.sqrt(pair_cn / (0.25 * gs))
    tc = 2.0 * pair0 / 3.5
    ncrit = 2.0 * gs * tc * math.log(2.0)
    ratio = e / pair_cn
    cond = ratio >= (0.716 + 2.44 * (n / ncrit) ** 2.17)
    with np.errstate(all="ignore"):
        pairex = np.where(cond, pair0 * (0.996 - 1.76 * (n / ncrit) ** 1.6 / np.abs(ratio) ** 0.68), 0.0)
    return pair_cn - 0.25 * gs * pairex ** 2


class _Damp:
    """`ignatyuk(Zix, Nix, E, 0) / alev(Zix, Nix)` of the residual of type t (gshell), or 1."""

    def __init__(self, lds):
        self.lds = lds

    def __call__(self, t: int, e) -> np.ndarray:
        e = _arr(e)
        if self.lds is None:
            return np.ones_like(e)
        from physics.hf.density.parameters import ignatyuk

        ld = self.lds[t]
        a = ignatyuk(ld, torch.as_tensor(e.copy(), dtype=DTYPE), 0).detach().numpy().astype(np.float64).reshape(e.shape)
        return a / float(ld.alev)


# ------------------------------------------------------------------------------------- the model


class _Case:
    """One incident energy: the scalars every routine of the exciton model reads."""

    def __init__(self, inp, c: int, options, params, ext: dict):
        cst = talys_constants()
        self.cst = cst
        self.inp, self.c, self.options, self.params, self.ext = inp, c, options, params, ext
        self.ecomp = float(inp.ecomp_mev[c])
        self.esurf = float(inp.esurf_mev[c])
        self.eg = inp.egrid_mev[c].detach().cpu().numpy().astype(np.float64)
        self.de = inp.deltae_mev[c].detach().cpu().numpy().astype(np.float64)
        self.mask = inp.emask[c].detach().cpu().numpy()
        self.xsreac = inp.xsreac_mb[c].detach().cpu().numpy().astype(np.float64)
        self.s = inp.s_mev[c].detach().cpu().numpy().astype(np.float64)
        self.wfac = inp.wfac[c].detach().cpu().numpy().astype(np.float64)
        self.gp_cn, self.gn_cn = float(inp.gp_cn[c]), float(inp.gn_cn[c])
        self.gp_res = inp.gp_res[c].detach().cpu().numpy().astype(np.float64)
        self.gn_res = inp.gn_res[c].detach().cpu().numpy().astype(np.float64)
        self.pair_cn = float(inp.pair_cn_mev[c])
        self.pair_res = inp.pair_res_mev[c].detach().cpu().numpy().astype(np.float64)
        self.g = ext["g"]
        self.dens = _Densities(self.g[0], self.gp_cn, self.gn_cn)
        self.gshell = bool(getattr(options, "flaggshell", False))
        self.damp = _Damp(ext.get("ld") if self.gshell else None)
        self.mode = int(getattr(options, "preeqmode", 2))
        self.pairmodel = int(getattr(options, "pairmodel", 2))
        self.surface = bool(getattr(options, "flagsurface", True))
        self.primary = bool(inp.primary)
        self.rgamma = float(params.at("rgamma"))
        self.nexcbins = max(inp.nbins // 2, 2) if inp.primary else max(inp.nbins // 4, 2)
        self.wvol = ext.get("wvol")
        # matrix.f90:64-94
        aproj = max(cst["parA"][inp.k0], 1)
        self.m2c = float(params.at("m2constant"))
        self.m2limit, self.m2shift = float(params.at("m2limit")), float(params.at("m2shift"))
        self.aproj = aproj
        r = {k: float(params.at(k)) for k in ("rpipi", "rnunu", "rpinu", "rnupi")}
        self.r = r
        self.wompfac = {1: self.m2c * 0.55 / (1.0 + 2.0 * r["rpinu"]),
                        2: self.m2c * 0.55 * 2.0 * r["rpinu"] / (1.0 + 2.0 * r["rpinu"])}
        self.wompfac[0] = 0.5 * (self.wompfac[1] + self.wompfac[2])

    # -- matrix.f90
    def m2(self, n: int) -> float:
        a = float(self.inp.a_init)
        m2 = self.m2c / a ** 3 * self.aproj * (self.m2limit * 7.48 + 4.62e5 / (
            (self.ecomp / (n * self.aproj) + self.m2shift * 10.7) ** 3))
        if self.mode == 1:
            m2 = 1.20 * m2
        return m2

    # -- the well of the first hole (preeq.f90:80-89, emissionrate2.f90:125-130)
    def well(self, h: int) -> tuple[bool, float]:
        surfwell = self.surface and h == 1 and self.primary
        return surfwell, (self.esurf if surfwell else EFERMI_MEV)

    def weff(self, k: int, uu, fac: float) -> np.ndarray:
        """`Wompfac * wvol(k, nen)`, nen = min(10 numen, int(10 max(uu - S(Zix, Nix, k), -20)))."""
        zi, ni = (0, 1) if k == 1 else (1, 0)
        eopt = np.maximum(_arr(uu) - self.ext["s"][(zi, ni, k)], -20.0)
        nen = np.minimum(10 * NUMEN_TALYS, np.trunc(eopt.astype(np.float32) * np.float32(10.0)).astype(np.int64))
        return fac * self.wvol[k][200 + nen]

    def open_grid(self, t: int):
        """(indices ebegin..eend of type t, Eres at them, the index of the first Eres < 0 or None)."""
        idx = np.nonzero(self.mask[t])[0]
        if idx.size == 0:
            return idx, idx.astype(np.float64), None
        eout = self.eg[idx]
        eres = self.ecomp - self.s[t] - eout
        if t <= 2:
            eres = np.minimum(eres, self.ecomp)
        neg = np.nonzero(eres < 0.0)[0]
        return idx, eres, (int(neg[0]) if neg.size else None)

    def integrate(self, t: int, w: np.ndarray, idx, cut) -> float:
        """`wemispart` with emissionrate2.f90:104-112's partial last bin."""
        n = idx.size if cut is None else cut
        tot = float(np.sum(w[idx[:n]] * self.de[idx[:n]])) if n else 0.0
        if cut is not None:
            nen1 = int(idx[cut]) - 1
            emax = self.ecomp - self.s[t]
            dE = emax - (self.eg[nen1] + 0.5 * self.de[nen1])
            tot += float(w[nen1]) * dE
        return tot


# ------------------------------------------------------------------------- two components


def emission2(cs: _Case, ppi: int, hpi: int, pnu: int, hnu: int):
    """emissionrate2.f90:67-172 for one state: (wemission2 (7, E), wemispart2 (7,), wemistot2, U).

    TALYS: emissionrate2.f90:1 (emissionrate2)
    Test: tests/hf/test_kwcov_b7.py
    """
    E = cs.eg.shape[0]
    n, h = ppi + hpi + pnu + hnu, hpi + hnu
    gsp, gsn = cs.gp_cn, cs.gn_cn
    if cs.gshell:
        d = float(cs.damp(0, cs.ecomp)[0])
        gsp, gsn = gsp * d, gsn * d
    surfwell, edepth = cs.well(h)
    U = cs.ecomp - float(_preeqpair(cs.pair_cn, cs.gp_cn + cs.gn_cn, n, cs.ecomp, cs.pairmodel)[0])
    phcomp = float(cs.dens.ph2(ppi, hpi, pnu, hnu, gsp, gsn, U, edepth, surfwell)[0])
    w = np.zeros((7, E))
    part = np.zeros(7)
    wsum = np.zeros(E)
    for t in range(7):
        if phcomp <= 1.0e-10:
            continue
        idx, eres, cut = cs.open_grid(t)
        if idx.size == 0:
            continue
        k = idx.size if cut is None else cut
        ii, er = idx[:k], eres[:k]
        eout = cs.eg[ii]
        factor = cs.wfac[t] * cs.xsreac[t, ii] * eout
        gsp_r = np.full(k, cs.gp_res[t])
        gsn_r = np.full(k, cs.gn_res[t])
        if cs.gshell:
            d = cs.damp(t, er)
            gsp_r, gsn_r = gsp_r * d, gsn_r * d
        if t == 0:
            if not (cs.primary and n <= 7):
                continue
            factor = factor * eout
            pp = _preeqpair(cs.pair_cn, cs.gp_cn + cs.gn_cn, n, er, cs.pairmodel)
            ug = np.maximum(er - pp, pp)
            gs = gsp_r + gsn_r
            ph1 = 0.5 * (cs.dens.ph2(ppi - 1, hpi - 1, pnu, hnu, gsp_r, gsn_r, ug, EFERMI_MEV, False)
                         + cs.dens.ph2(ppi, hpi, pnu - 1, hnu - 1, gsp_r, gsn_r, ug, EFERMI_MEV, False))
            ph2 = cs.dens.ph2(ppi, hpi, pnu, hnu, gsp_r, gsn_r, ug, EFERMI_MEV, False)
            g2e = gs * gs * eout
            bplus = g2e / (gs * (n - 2) + g2e) if n >= 2 else np.zeros_like(g2e)
            bzero = gs * n / (gs * n + g2e)
            val = cs.rgamma * factor * (bplus * ph1 + bzero * ph2) / phcomp
            w[0, ii] = val
            wsum[ii] = val
        else:
            ppires, pnures, nres = ppi - PARZ[t], pnu - PARN[t], n - PARZ[t] - PARN[t]
            if ppires < 0 or pnures < 0 or h == 0:
                continue
            ewell = EFERMI_MEV if t > 2 else edepth
            pp = _preeqpair(cs.pair_res[t], cs.gp_res[t] + cs.gn_res[t], nres, er, cs.pairmodel)
            ures = np.maximum(er - pp, pp)
            phres = cs.dens.ph2(ppires, hpi, pnures, hnu, gsp_r, gsn_r, ures, ewell, surfwell)
            val = factor * phres / phcomp
            w[t, ii] = val
            wsum[ii] += val
        part[t] = cs.integrate(t, w[t], idx, cut)
    tot = float(part.sum())
    if n > 1:
        if tot == part[0]:
            tot, part[0] = 0.0, 0.0
        w[0] = np.where(wsum == w[0], 0.0, w[0])
    return w, part, tot, U, surfwell, edepth


def _ana_plus2(cs, st, kind, U, gsp, gsn, m2, surfwell, edepth):
    """lambdapiplus/lambdanuplus closed form (lambdapiplus.f90:158-171)."""
    ppi, hpi, pnu, hnu = st
    n, p, h = sum(st), ppi + pnu, hpi + hnu
    tph = cs.cst["twopihbar"]
    D = cs.dens
    fac1 = 2.0 * n * (n + 1.0)
    if kind == "pi":
        factor1 = tph * gsp * gsp / fac1
        term1 = U - D.apauli2(ppi + 1, hpi + 1, pnu, hnu)
        factor3 = (ppi + hpi) * gsp * m2["pipi"] + 2.0 * (pnu + hnu) * gsn * m2["pinu"]
    else:
        factor1 = tph * gsn * gsn / fac1
        term1 = U - D.apauli2(ppi, hpi, pnu + 1, hnu + 1)
        factor3 = (pnu + hnu) * gsn * m2["nunu"] + 2.0 * (ppi + hpi) * gsp * m2["nupi"]
    term2 = U - D.apauli2(ppi, hpi, pnu, hnu)
    if term1 <= 0.0 or term2 <= 0.0:
        return 0.0
    term12 = term1 / term2
    if term12 < 0.01:
        return 0.0
    lplus = factor1 * term1 ** 2 * term12 ** (n - 1) * factor3
    fw = _finitewell_arr(np.array([p + 1]), np.array([h + 1]), np.array([U]), np.array([edepth]),
                         np.array([surfwell]), EFERMI_MEV)
    return float(lplus * fw[0])


def _ana_zero2(cs, st, kind, U, gsp, gsn, m2, surfwell, edepth):
    """lambdapinu/lambdanupi closed form (lambdapinu.f90:132-147)."""
    ppi, hpi, pnu, hnu = st
    n, p, h = sum(st), ppi + pnu, hpi + hnu
    tph = cs.cst["twopihbar"]
    D = cs.dens
    a0 = D.apauli2(ppi, hpi, pnu, hnu)
    if kind == "pinu":
        factor1 = tph * ppi * hpi * m2["pinu"] / n * gsn * gsn
        has = ppi > 0 and hpi > 0
        ax = D.apauli2(ppi - 1, hpi - 1, pnu + 1, hnu + 1)
    else:
        factor1 = tph * pnu * hnu * m2["nupi"] / n * gsp * gsp
        has = pnu > 0 and hnu > 0
        ax = D.apauli2(ppi + 1, hpi + 1, pnu - 1, hnu - 1)
    bfac = max(a0, ax) if has else a0
    f2, f3 = U - bfac, U - a0
    if f2 <= 0.0 or f3 <= 0.0:
        return 0.0
    f23 = f2 / f3
    if f23 < 0.01:
        return 0.0
    f4 = 2.0 * (U - bfac) + (n * abs(a0 - ax) if has else 0.0)
    fw = _finitewell_arr(np.array([p]), np.array([h]), np.array([U]), np.array([edepth]), np.array([surfwell]),
                         EFERMI_MEV)
    return float(factor1 * f23 ** (n - 1) * f4 * fw[0])


#: lambdapiplus / lambdanuplus numerical channels: (residual shift, colliding configuration, M2 key, g of
#: `gsp`/`gsn`, optical-model particle k, Wompfac index, ratio configuration (densh, densp) or None)
_PLUS = {
    "pi": (((-1, 0, 0, 0), (2, 1, 0, 0), "pipi", "p", 2, 1, None),
           ((0, -1, 0, 0), (1, 2, 0, 0), "pipi", "p", 2, 1, ((1, 2, 0, 0), (2, 1, 0, 0))),
           ((0, 0, -1, 0), (1, 1, 1, 0), "nupi", "n", 1, 2, None),
           ((0, 0, 0, -1), (1, 1, 0, 1), "nupi", "n", 1, 2, ((1, 1, 0, 1), (1, 1, 1, 0)))),
    "nu": (((0, 0, -1, 0), (0, 0, 2, 1), "nunu", "n", 1, 1, None),
           ((0, 0, 0, -1), (0, 0, 1, 2), "nunu", "n", 1, 1, ((0, 0, 1, 2), (0, 0, 2, 1))),
           ((-1, 0, 0, 0), (1, 0, 1, 1), "pinu", "p", 2, 2, None),
           ((0, -1, 0, 0), (0, 1, 1, 1), "pinu", "p", 2, 2, ((0, 1, 1, 1), (1, 0, 1, 1)))),
}


def _num_plus2(cs, st, kind, U, m2, surfwell, edepth):
    """lambdapiplus/lambdanuplus numerical form, preeqmode 2 or 3 (lambdapiplus.f90:172-283)."""
    D = cs.dens
    tph, hbar = cs.cst["twopihbar"], cs.cst["hbar"]
    tgt = D.apauli2(*(np.array(st) + (np.array([1, 1, 0, 0]) if kind == "pi" else np.array([0, 0, 1, 1]))))
    nb = cs.nexcbins
    mid = np.arange(1, nb + 1) - 0.5
    chans = _PLUS[kind]
    uus, dexs, subs = [], [], []
    for shift, *_ in chans:
        sub = tuple(int(a + b) for a, b in zip(st, shift))
        al = D.apauli2(*sub)
        l1, l2 = tgt - al, U - al
        dex = (l2 - l1) / nb
        uus.append(l1 + mid * dex)
        dexs.append(dex)
        subs.append(sub)
    if cs.gshell:  # all four channels take the first channel's damping
        dmp = cs.damp(0, uus[0])
        gsp, gsn = cs.gp_cn * dmp, cs.gn_cn * dmp
        dmp_r = cs.damp(0, U - uus[0])
        gsp_r, gsn_r = cs.gp_cn * dmp_r, cs.gn_cn * dmp_r
    else:
        gsp, gsn = np.full(nb, cs.gp_cn), np.full(nb, cs.gn_cn)
        gsp_r, gsn_r = gsp, gsn
    total = np.zeros(nb)
    for j, (shift, coll, mkey, gkey, k, wf, ratio) in enumerate(chans):
        uu = uus[j]
        if cs.mode == 2:
            lam = tph * m2[mkey] * D.ph2(*coll, gsp, gsn, uu, edepth, surfwell)
        else:
            lam = 2.0 * cs.weff(k, uu, cs.wompfac[wf]) / hbar
            if ratio is not None:
                densh = D.ph2(*ratio[0], gsp, gsn, uu, edepth, surfwell)
                densp = D.ph2(*ratio[1], gsp, gsn, uu, edepth, surfwell)
                lam = lam * np.where(densp > 1.0, densh / np.where(densp > 1.0, densp, 1.0), 1.0)
        term = lam * (gsp if gkey == "p" else gsn) * dexs[j]
        total = total + term * D.ph2(*subs[j], gsp_r, gsn_r, U - uu, edepth, surfwell)
    acc = 0.0
    for v in total:
        acc += float(v)
    gp_t, gn_t = cs.gp_cn, cs.gn_cn
    if cs.gshell:
        d = float(cs.damp(0, U)[0])
        gp_t, gn_t = gp_t * d, gn_t * d
    phtot = float(D.ph2(*st, gp_t, gn_t, U, edepth, surfwell)[0])
    return acc / phtot if phtot > 0.0 else 0.0


def _num_zero2(cs, st, kind, U, m2, surfwell, edepth):
    """lambdapinu/lambdanupi numerical form, preeqmode 2 or 3 (lambdapinu.f90:148-206)."""
    D = cs.dens
    tph, hbar = cs.cst["twopihbar"], cs.cst["hbar"]
    ppi, hpi, pnu, hnu = st
    if kind == "pinu":
        sub = (ppi - 1, hpi - 1, pnu, hnu)
        coll, pair, mkey, k, ratio = (0, 0, 1, 1), (1, 1, 0, 0), "pinu", 2, ((0, 0, 1, 1), (1, 0, 1, 1))
    else:
        sub = (ppi, hpi, pnu - 1, hnu - 1)
        coll, pair, mkey, k, ratio = (1, 1, 0, 0), (0, 0, 1, 1), "nupi", 1, ((1, 1, 0, 0), (1, 1, 1, 0))
    a0, al = D.apauli2(*st), D.apauli2(*sub)
    l1, l2 = a0 - al, U - al
    nb = cs.nexcbins
    dex = (l2 - l1) / nb
    uu = l1 + (np.arange(1, nb + 1) - 0.5) * dex
    if cs.gshell:
        d = cs.damp(0, uu)
        gsp, gsn = cs.gp_cn * d, cs.gn_cn * d
        # lambdanupi.f90:185 damps the residual with g(uu); lambdapinu.f90:185 with g(U - uu)
        dr = cs.damp(0, uu if kind == "nupi" else U - uu)
        gsp_r, gsn_r = cs.gp_cn * dr, cs.gn_cn * dr
    else:
        gsp, gsn = np.full(nb, cs.gp_cn), np.full(nb, cs.gn_cn)
        gsp_r, gsn_r = gsp, gsn
    if cs.mode == 2:
        lam = tph * m2[mkey] * D.ph2(*coll, gsp, gsn, uu, edepth, surfwell)
    else:
        lam = 2.0 * cs.weff(k, uu, cs.wompfac[0]) / hbar
        densh = D.ph2(*ratio[0], gsp, gsn, uu, edepth, surfwell)
        densp = D.ph2(*ratio[1], gsp, gsn, uu, edepth, surfwell)
        lam = lam * np.where(densp > 1.0, densh / np.where(densp > 1.0, densp, 1.0), 1.0)
    term = lam * D.ph2(*pair, gsp, gsn, uu, edepth, surfwell) * dex
    vals = term * D.ph2(*sub, gsp_r, gsn_r, U - uu, edepth, surfwell)
    acc = 0.0
    for v in vals:
        acc += float(v)
    gp_t, gn_t = cs.gp_cn, cs.gn_cn
    if cs.gshell:
        dd = float(cs.damp(0, U)[0])
        gp_t, gn_t = gp_t * dd, gn_t * dd
    phtot = float(D.ph2(*st, gp_t, gn_t, U, edepth, surfwell)[0])
    return acc / phtot if phtot > 0.0 else 0.0


def rates2(cs: _Case, st: tuple[int, int, int, int]) -> dict[str, float]:
    """The four two-component transition rates [s^-1] of one state.

    TALYS: lambdapiplus.f90:1, lambdanuplus.f90:1, lambdapinu.f90:1, lambdanupi.f90:1
    Test: tests/hf/test_kwcov_b7.py
    """
    n, h = sum(st), st[1] + st[3]
    out = {"lambdapiplus": 0.0, "lambdanuplus": 0.0, "lambdapinu": 0.0, "lambdanupi": 0.0}
    if n == 0:
        return out
    m2b = cs.m2(n)
    m2 = {k: cs.r["r" + k] * m2b for k in ("pipi", "nunu", "pinu", "nupi")}
    surfwell, edepth = cs.well(h)
    gsp, gsn = cs.gp_cn, cs.gn_cn
    if cs.gshell:
        d = float(cs.damp(0, cs.ecomp)[0])
        gsp, gsn = gsp * d, gsn * d
    U = cs.ecomp - float(_preeqpair(cs.pair_cn, cs.gp_cn + cs.gn_cn, n, cs.ecomp, cs.pairmodel)[0])
    if cs.mode not in (2, 3) or n == 1:
        out["lambdapiplus"] = _ana_plus2(cs, st, "pi", U, gsp, gsn, m2, surfwell, edepth)
        out["lambdanuplus"] = _ana_plus2(cs, st, "nu", U, gsp, gsn, m2, surfwell, edepth)
        out["lambdapinu"] = _ana_zero2(cs, st, "pinu", U, gsp, gsn, m2, surfwell, edepth)
        out["lambdanupi"] = _ana_zero2(cs, st, "nupi", U, gsp, gsn, m2, surfwell, edepth)
    else:
        out["lambdapiplus"] = _num_plus2(cs, st, "pi", U, m2, surfwell, edepth)
        out["lambdanuplus"] = _num_plus2(cs, st, "nu", U, m2, surfwell, edepth)
        out["lambdapinu"] = _num_zero2(cs, st, "pinu", U, m2, surfwell, edepth)
        out["lambdanupi"] = _num_zero2(cs, st, "nupi", U, m2, surfwell, edepth)
    return out


def two_component(inp, options, params, ext: dict, states) -> tuple[dict, dict]:
    """(emis, rates) in the shapes `exciton.exchange_and_lifetime` and `exciton.exciton_model` read:
    wemission2 (C, S, 7, E), wemispart2 (C, S, 7), wemistot2 (C, S) and the four rates (C, S).

    TALYS: exciton2.f90:1 (exciton2)
    Test: tests/hf/test_kwcov_b7.py
    """
    C, E, S = inp.C, inp.E, states.size
    w = np.zeros((C, S, 7, E))
    part = np.zeros((C, S, 7))
    tot = np.zeros((C, S))
    rates = {k: np.zeros((C, S)) for k in ("lambdapiplus", "lambdanuplus", "lambdapinu", "lambdanupi")}
    for c in range(C):
        cs = _Case(inp, c, options, params, ext)
        for s in range(S):
            st = (int(states.ppi[s]), int(states.hpi[s]), int(states.pnu[s]), int(states.hnu[s]))
            w[c, s], part[c, s], tot[c, s], *_ = emission2(cs, *st)
            for k, v in rates2(cs, st).items():
                rates[k][c, s] = v
    t = lambda a: torch.as_tensor(a, dtype=DTYPE)  # noqa: E731
    emis = {"wemission2": t(w), "wemispart2": t(part), "wemistot2": t(tot)}
    return emis, {k: t(v) for k, v in rates.items()}


# ------------------------------------------------------------------------- one component


def qfactor(ext: dict, maxpar: int) -> np.ndarray:
    """`Qfactor(type, p)` (excitoninit.f90:74-101): the charge factor of the one-component emission rates.

    TALYS: excitoninit.f90:1 (excitoninit)
    Test: tests/hf/test_kwcov_b7.py
    """
    k0 = ext["k0"]
    zoa = ext["Zinit"] / ext["Ainit"]
    noa = ext["Ninit"] / ext["Ainit"]
    zproj, nproj = PARZ[k0], PARN[k0]
    q = np.ones((7, NUMPARX + 2))
    for t in range(1, 7):
        ze, ne, ae = PARZ[t], PARN[t], PARA[t]
        for p in range(1, maxpar + 1):
            if p < ae:
                continue
            qen = qde = 0.0
            for ppi in range(zproj, p - nproj + 1):
                hpi = ppi - zproj
                npi = ppi + hpi
                pnu = p - ppi
                hnu = p - nproj - ppi
                nnu = pnu + hnu
                f4 = _nf(hpi) * _nf(hnu)
                qde += zoa ** npi * noa ** nnu * (1.0 / (_nf(ppi) * _nf(pnu))) / f4
                if ppi < ze or pnu < ne:
                    continue
                qen += zoa ** (npi - ze) * noa ** (nnu - ne) * (1.0 / (_nf(ppi - ze) * _nf(pnu - ne))) / f4
            if qde > 0.0:
                q[t, p] = (qen / qde) * _nf(p - ae) / _nf(p)
    return q


def emission1(cs: _Case, p: int, h: int, qf: np.ndarray):
    """emissionrate.f90:62-245 for one (p, h): (wemission (7, E), wemispart (7,), wemistot).

    TALYS: emissionrate.f90:1 (emissionrate)
    Test: tests/hf/test_kwcov_b7.py
    """
    E = cs.eg.shape[0]
    n = p + h
    D = cs.dens
    gs = cs.g[0]
    gsg = cs.ext["Atarget"] / 13.0
    if cs.gshell:
        gs = gs * float(cs.damp(0, cs.ecomp)[0])
    surfwell, edepth = cs.well(h)
    U = cs.ecomp - float(_preeqpair(cs.pair_cn, cs.g[0], n, cs.ecomp, cs.pairmodel)[0])
    phcomp = float(D.ph1(p, h, gs, U, edepth, surfwell)[0])
    phcompg = float(D.ph1(p, h, gsg, U, edepth, surfwell)[0])
    w = np.zeros((7, E))
    part = np.zeros(7)
    wsum = np.zeros(E)
    tot = 0.0
    for t in range(7):
        qfac = float(qf[t, p]) if (cs.primary and t > 0) else 1.0
        ewell = EFERMI_MEV if t > 2 else edepth
        if phcomp <= 1.0e-10 or (t == 0 and phcompg <= 1.0e-10):
            continue
        idx, eres, cut = cs.open_grid(t)
        if idx.size == 0:
            continue
        k = idx.size if cut is None else cut
        ii, er = idx[:k], eres[:k]
        eout = cs.eg[ii]
        factor = cs.wfac[t] * cs.xsreac[t, ii] * eout
        gsr = np.full(k, cs.g[t])
        if cs.gshell:
            gsr = gsr * cs.damp(t, er)
        if t == 0:
            if cs.primary and n <= 7:
                factor = factor * eout
                pp = _preeqpair(cs.pair_cn, cs.g[0], n, er, cs.pairmodel)
                ug = np.maximum(er - pp, pp)
                ph1 = D.ph1(p - 1, h - 1, gsg, ug, EFERMI_MEV, False)
                ph2 = D.ph1(p, h, gsg, ug, EFERMI_MEV, False)
                g2e = gsg * gsg * eout
                bplus = g2e / (gsg * (n - 2) + g2e) if n >= 2 else np.zeros_like(g2e)
                bzero = gsg * n / (gsg * n + g2e)
                val = cs.rgamma * factor * (bplus * ph1 + bzero * ph2) / phcompg
                w[0, ii] = val
                wsum[ii] = val
        else:
            pres, nres = p - PARA[t], n - PARA[t]
            if not (pres < 0 or h == 0):
                pp = _preeqpair(cs.pair_res[t], cs.g[t], nres, er, cs.pairmodel)
                ures = np.maximum(er - pp, pp)
                phres = D.ph1(pres, h, gsr, ures, ewell, surfwell)
                val = factor * phres / phcomp * qfac
                w[t, ii] = val
                wsum[ii] += val
        part[t] = cs.integrate(t, w[t], idx, cut)
        tot += part[t]
    if n > 1:
        if tot == part[0]:
            part[0] = 0.0  # emissionrate.f90:239: wemistot is NOT cleared
        w[0] = np.where(wsum == w[0], 0.0, w[0])
    return w, part, tot


def lambdaplus1(cs: _Case, p: int, h: int) -> float:
    """lambdaplus.f90:69-218: the one-component rate [s^-1] of (p, h) -> (p+1, h+1).

    TALYS: lambdaplus.f90:1 (lambdaplus)
    Test: tests/hf/test_kwcov_b7.py
    """
    n = p + h
    if n == 0:
        return 0.0
    D = cs.dens
    tph, hbar = cs.cst["twopihbar"], cs.cst["hbar"]
    m2 = cs.m2(n) * 0.50  # matrix.f90:80 (one component)
    surfwell, edepth = cs.well(h)
    g0 = cs.g[0]
    gs = g0 * float(cs.damp(0, cs.ecomp)[0]) if cs.gshell else g0
    U = cs.ecomp - float(_preeqpair(cs.pair_cn, g0, n, cs.ecomp, cs.pairmodel)[0])
    if cs.mode not in (2, 3) or n == 1:
        factor1 = tph * m2 * 0.5 / (n + 1.0) * gs ** 3
        term1 = U - D.apauli(p + 1, h + 1)
        term2 = U - D.apauli(p, h)
        if term1 <= 0.0 or term2 <= 0.0:
            return 0.0
        term12 = term1 / term2
        if term12 < 0.01:
            return 0.0
        lplus = factor1 * term1 ** 2 * term12 ** (n - 1)
        fw = _finitewell_arr(np.array([p + 1]), np.array([h + 1]), np.array([U]), np.array([edepth]),
                             np.array([surfwell]), EFERMI_MEV)
        return float(lplus * fw[0])
    l1p = D.apauli(p + 1, h + 1) - D.apauli(p - 1, h)
    l2p = U - D.apauli(p - 1, h)
    l1h = D.apauli(p + 1, h + 1) - D.apauli(p, h - 1)
    l2h = U - D.apauli(p, h - 1)
    nb = cs.nexcbins
    mid = np.arange(1, nb + 1) - 0.5
    dpp, dhh = (l2p - l1p) / nb, (l2h - l1h) / nb
    uup, uuh = l1p + mid * dpp, l1h + mid * dhh
    gsb = g0 * cs.damp(0, uup) if cs.gshell else np.full(nb, g0)
    if cs.mode == 2:
        lam1p = tph * m2 * D.ph1(2, 1, gsb, uup, edepth, surfwell)
        lam1h = tph * m2 * D.ph1(1, 2, gsb, uuh, edepth, surfwell)
    else:
        zr, nr = cs.ext["Zinit"] / cs.ext["Ainit"], cs.ext["Ninit"] / cs.ext["Ainit"]
        ww = lambda uu: zr * cs.weff(2, uu, 0.5 * cs.wompfac[0]) + nr * cs.weff(1, uu, 0.5 * cs.wompfac[0])  # noqa: E731
        lam1p = 2.0 * ww(uup) / hbar
        densh = D.ph1(1, 2, gsb, uuh, edepth, surfwell)
        densp = D.ph1(2, 1, gsb, uuh, edepth, surfwell)
        lam1h = 2.0 * ww(uuh) / hbar * np.where(densp > 1.0, densh / np.where(densp > 1.0, densp, 1.0), 1.0)
    t1p = lam1p * gsb * dpp
    t1h = lam1h * gsb * dhh
    gsr = g0 * cs.damp(0, U - uup) if cs.gshell else np.full(nb, g0)
    v = t1p * D.ph1(p - 1, h, gsr, U - uup, edepth, surfwell) + t1h * D.ph1(p, h - 1, gsr, U - uuh, edepth,
                                                                             surfwell)
    acc = 0.0
    for x in v:
        acc += float(x)
    gt = g0 * float(cs.damp(0, U)[0]) if cs.gshell else g0
    phtot = float(D.ph1(p, h, gt, U, edepth, surfwell)[0])
    return acc / phtot if phtot > 0.0 else 0.0


def one_component(inp, options, params, ext: dict) -> dict:
    """exciton.f90 + lifetime.f90: the one-component never-come-back model for every case.

    Returns `xsstep` (C, 7, maxpar+1, E), `xspreeq` (C, 7, E), and `xsstep2` (C, P, 7, E) with one row per
    particle number p (the one-component states) plus their exciton numbers `n_state` (P,), so `preeq_correct`
    and `preeq_total` treat it as they treat the two-component per-state spectrum.

    TALYS: exciton.f90:1 (exciton), lifetime.f90:1 (lifetime)
    Test: tests/hf/test_kwcov_b7.py
    """
    C, E = inp.C, inp.E
    k0 = inp.k0
    p0 = PARA[k0] if k0 > 0 else 1
    maxpar = NUMPARX
    qf = qfactor(ext, maxpar)
    ps = list(range(p0, maxpar + 1))
    xs2 = np.zeros((C, len(ps), 7, E))
    xsstep = np.zeros((C, 7, maxpar + 1, E))
    for c in range(C):
        cs = _Case(inp, c, options, params, ext)
        flux = float(inp.xsflux_mb[c])
        wem, wtot, lam = {}, {}, {}
        for p in ps:
            h = p - p0
            wem[p], _, wtot[p] = emission1(cs, p, h, qf)
            lam[p] = lambdaplus1(cs, p, h)
        dep = {}
        for i, p in enumerate(ps):
            h = p - p0
            if p == p0:
                dep[p] = 1.0
            else:
                term1 = lam[p - 1] + wtot[p - 1]
                dep[p] = dep[p - 1] * lam[p - 1] / term1 if term1 != 0.0 else 0.0
            term2 = lam[p] + wtot[p]
            tau = dep[p] / term2 if term2 != 0.0 else 0.0
            xs = flux * tau * wem[p]
            xs2[c, i] = xs
            xsstep[c, :, p, :] = xs
    t = lambda a: torch.as_tensor(a, dtype=DTYPE)  # noqa: E731
    return {"xsstep": t(xsstep), "xspreeq": t(xs2.sum(1)), "xsstep2": t(xs2),
            "n_state": torch.tensor([2 * p - p0 for p in ps], dtype=torch.int64)}


def exciton_model(inp, options, params, ext: dict, states=None) -> dict:
    """`preeq.exciton.exciton_model` for a run with one of this module's switches set.

    TALYS: preeq.f90:1 (preeq) lines 113-117
    Test: tests/hf/test_kwcov_b7.py
    """
    from physics.hf.preeq.exciton import exchange_and_lifetime, exciton_states

    if not bool(getattr(options, "flag2comp", True)):
        out = one_component(inp, options, params, ext)
        out["states"] = None
        return out
    if states is None:
        states = exciton_states(inp.k0, NUMPARX, inp.egrid_mev.device)
    emis, rates = two_component(inp, options, params, ext, states)
    life = exchange_and_lifetime(inp, states, rates, emis)
    C, E, S = inp.C, inp.E, states.size
    factor = inp.xsflux_mb.reshape(C, 1) * life["Spre"]
    xs = factor.reshape(C, S, 1, 1) * emis["wemission2"]
    xsstep = torch.zeros(C, 7, states.maxpar + 1, E, dtype=DTYPE)
    for s in range(S):
        xsstep[:, :, int(states.p[s]), :] += xs[:, s]
    return {"states": states, "xsstep": xsstep, "xspreeq": xs.sum(1).clone(), "xsstep2": xs,
            "n_state": states.n.clone(), **emis, **rates, **life}
