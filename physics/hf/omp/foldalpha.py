"""KWCOV B7b: the alpha double-folding optical potentials of Demetriou, Grama and Goriely (alphaomp 3, 4, 5): the
real part by folding the alpha and target densities with a density-dependent M3Y-type interaction (afold.f), the
imaginary part a Woods-Saxon volume (+ surface) form fixed by its volume integral, and for alphaomp 5 the
dispersive corrections (mahaux). Handed to ECIS as tabulated form factors, like JLM (`omp/jlm.py`).

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.
`afold.f` (S. Goriely) ships inside the TALYS repository under its MIT license.

Task: T5 (physics/hf/CONTRACT.md §7). Acceptance test: KWCOV-B7B (tests/hf/test_kwcov_b7b.py).

TALYS routines ported here (file:line of the subroutine/function statement):
    foldalpha.f90:1 (foldalpha)
    afold.f:1 (afold)

afold.f computes in single precision with implicit typing; the port works in double (differences of order 1e-6
relative). Two quirks are kept: the alpha density is weighted by r^2 of the PREVIOUS grid point (`dense`'s loop
restarts r at 0 for i = 2), and the target's exp(-beta rho) factor takes rho * 4 pi r^2, not rho. ftrans's Filon
branch writes the end-node weight of its last panel into bcof(npoint) and never sets bcof(npoint - 1) for an
even npoint (TALYS keeps the previous call's value; 0 here): q = 9.98 fm^-1 / r = 19.96 fm, where both integrands
vanish.
"""

from __future__ import annotations

import math
from functools import lru_cache

import numpy as np

from physics.hf.omp.jlm import NUMJLM, pvalue, radial_table

_PI_SGL = 3.1415926536  # afold.f's `pi=3.1415926536d0`
_BETA = 10.639
_ALPHA = 4.3529
_CE = 0.44073


def _ftrans(npoint: int, h: float, p: float) -> np.ndarray:
    """afold.f's ftrans for l = 0 (lm = 1) from r = 0: the weights bcof(1..npoint) of int f(x) j0(p x) dx on the grid
    x_i = (i-1) h. Filon-type quadratic panels when h p >= 0.1, Simpson otherwise.

    TALYS: afold.f:1 (afold) -- subroutine ftrans
    Test: tests/hf/test_kwcov_b7b.py
    """
    from scipy.special import sici

    d = h * p
    out = np.zeros(npoint)
    if abs(d) < 0.1:
        xfac = h / 3.0
        i = np.arange(npoint)
        x = i * d
        xs = np.where(x == 0.0, 1.0, x)
        j0 = np.where(x == 0.0, 1.0, np.sin(xs) / xs)
        out = np.where((i + 1) % 2 == 0, 4.0, 2.0) * xfac * j0
        out[0] *= 0.5
        out[-1] *= 0.5
        return out
    d2 = d + d
    dd = d * d
    xfac = 1.0 / (p * dd)
    n = (npoint + 1) // 2
    x = np.arange(n) * d2
    xs = np.where(x == 0.0, 1.0, x)
    b1 = np.where(x == 0.0, 0.0, sici(xs)[0] * xfac)
    b2 = np.where(x == 0.0, 0.0, (1.0 - np.cos(xs)) * xfac)
    b3 = np.where(x == 0.0, 0.0, (np.sin(xs) - xs * np.cos(xs)) * xfac)
    for k in range(1, n):  # Fortran in = k + 1
        xk = x[k]
        x1, x2 = xk - d, xk - d2
        bd1, bd2, bd3 = b1[k] - b1[k - 1], b2[k] - b2[k - 1], b3[k] - b3[k - 1]
        out[2 * k - 1] = -bd3 + 2.0 * x1 * bd2 - (x1 * x1 - dd) * bd1  # bcof(2 in - 2)
        if k == 1:
            out[0] = 0.5 * bd3 - (x2 + 1.5 * d) * bd2 + ((.5 * x2 + 1.5 * d) * x2 + dd) * bd1
        else:  # bcof(2 in - 3)
            out[2 * k - 2] = (.5 * (b3[k] - b3[k - 2]) - x2 * (b2[k] - b2[k - 2])
                              - 1.5 * d * (b2[k] - 2.0 * b2[k - 1] + b2[k - 2])
                              + (.5 * x2 * x2 + dd) * (b1[k] - b1[k - 2])
                              + 1.5 * x2 * d * (b1[k] - 2.0 * b1[k - 1] + b1[k - 2]))
        if k == n - 1:
            out[npoint - 1] = .5 * bd3 - (xk - 1.5 * d) * bd2 + ((.5 * xk - 1.5 * d) * xk + dd) * bd1
    return out


@lru_cache(maxsize=4)
def _ftrans_matrix(npoint: int, h: float, dp: float) -> np.ndarray:
    """(npoint, npoint): row k = ftrans weights at p = k dp."""
    return np.stack([_ftrans(npoint, h, k * dp) for k in range(npoint)])


@lru_cache(maxsize=2)
def _alpha_density(nu: int, d1: float) -> tuple[np.ndarray, np.ndarray]:
    """afold.f's `dense(1)`: the alpha's sum-of-Gaussians density times 4 pi r^2 (r of the previous point), and the
    same with exp(-beta rho)."""
    pi32 = math.sqrt(_PI_SGL) * _PI_SGL
    g = math.sqrt(2.0 / 3.0)
    ri = np.array([0.2, 0.6, 0.9, 1.4, 1.9, 2.3, 2.6, 3.1, 3.5, 4.2, 4.9, 5.2])
    sq = np.array([0.034724, 0.430761, 0.203166, 0.192986, 0.083866, 0.033007, 0.014201, 0., 0.006860, 0.,
                   0.000438, 0.])
    a = 4.0 * sq / (2.0 * pi32 * g**3 * (1.0 + 2.0 * (ri / g) ** 2))
    r = np.arange(nu) * d1
    raw = (a[None, :] * (np.exp(-((r[:, None] - ri[None, :]) / g) ** 2)
                         + np.exp(-((r[:, None] + ri[None, :]) / g) ** 2))).sum(1)
    ro = np.zeros(nu)
    roe = np.zeros(nu)
    rr = (np.arange(nu - 1) * d1) ** 2
    roe[1:] = 4.0 * _PI_SGL * rr * raw[1:] * np.exp(-raw[1:] * _BETA)
    ro[1:] = raw[1:] * rr * 4.0 * _PI_SGL
    return ro, roe


def _intu_volj(u: np.ndarray, du: float) -> float:
    """afold.f's intu: 4 pi int u r^2 dr (Simpson 3/8 over the points 1..nr, trapezoid tail)."""
    nr = u.shape[0]
    nr2 = nr - 1
    nr1 = (nr2 // 3) * 3
    s = 0.0
    a1 = 0.0
    r = 0.0
    for kr in range(3, nr1 + 1, 3):
        r1 = r + du
        r2 = r1 + du
        r3 = r2 + du
        b1 = u[kr - 2] * r1 * r1 + u[kr - 1] * r2 * r2
        c1 = u[kr] * r3 * r3
        s += a1 + 3.0 * b1 + c1
        a1 = c1
        r = r3
    if nr2 > nr1:
        c5 = du * 4.0 / 3.0
        for kr in range(nr1 + 1, nr2 + 1):
            s += c5 * du * (u[kr - 1] * (kr - 1) ** 2 + u[kr] * kr**2)
    return 0.375 * du * 12.5663706144 * s


@lru_cache(maxsize=64)
def _afold_parts(Z: int, A: int, radialmodel: int):
    """afold's energy-independent pieces: (rv, U0, U1), the folded potential being u(r) = U0 + de U1 before afold
    scales it to its volume integral (de = -276 (1 - 0.005 E / 4) is the only energy dependence of the folding)."""
    radmom, rp, rn = radial_table(Z, A, radialmodel)
    rhomom = (rn[:, 0] + rp[:, 0]).astype(float)
    radmom = radmom.astype(float)
    nu = 1000
    rb = float(radmom[NUMJLM - 1])
    d = rb / nu
    dq = 10.0 / nu
    r = np.arange(nu) * d
    rho = np.interp(r, radmom, rhomom)  # afold.f:446-466: linear, the end values outside the table
    ro2 = rho * r * r * 4.0 * _PI_SGL
    roe2 = ro2 * np.exp(-ro2 * _BETA)
    ro1, roe1 = _alpha_density(nu, d)
    Bq = _ftrans_matrix(nu, d, dq)
    sum1, sum2, s1, s2 = Bq @ ro1, Bq @ ro2, Bq @ roe1, Bq @ roe2
    qq = (np.arange(nu) * dq) ** 2
    core = (sum1 * sum2 + s1 * s2 * _ALPHA) * qq
    c0 = 25129.599 / (qq + 16.0) - 10726.653 / (qq + 6.25)  # key 5
    Br = _ftrans_matrix(nu, dq, d)
    akoff = 0.5 / (_PI_SGL * _PI_SGL)
    return r, akoff * _CE * (Br @ (core * c0)), akoff * _CE * (Br @ core)


def _mahaux(at, elab, eref, expj0, as_, es, v5, rw, aw, efermi):
    """afold.f's mahaux: the dispersive depths (dwv, dws) of alphaomp 5 (Mahaux, Ngo and Satchler 1986)."""
    pi = 4.0 * math.atan(1.0)
    a13 = at**0.3333333
    ee = 0.1 + np.arange(150.0)
    C = np.where(ee < 13.0, -0.165 * ee + 2.15, 0.005)
    v5f = v5 * np.exp(-C * np.abs(ee - efermi))
    te = 1.0 / (1.0 + np.exp(-(ee - es) / as_))
    wamp = -expj0 * te / ((1.0 - v5f) * rw**3 / 3.0 + 7.603 * v5f * aw * rw**2 / a13) / pi
    ww = wamp * (1.0 - v5f)
    wd = -wamp * v5f
    dj = ee[1:] - ee[:-1]
    with np.errstate(divide="ignore", invalid="ignore"):
        an1 = (elab - ee[:-1]) * np.log(np.abs((elab - ee[:-1]) / dj))
        an2 = (elab - ee[1:]) * np.log(np.abs((elab - ee[1:]) / dj))
    an1 = np.nan_to_num(an1)
    an2 = np.nan_to_num(an2)
    dve = ((ww[1:] - ww[:-1]) / dj) * (an1 - an2) / pi
    dved = ((wd[1:] - wd[:-1]) / dj) * (an1 - an2) / pi
    return -float(dve.sum()), -float(dved.sum())


def _mexc(Z: int, A: int, options) -> tuple[float, float]:
    """(expmexc, thmexc) of (Z, A) as masses.f90 holds them (0 when not tabulated)."""
    from physics.hf.structure.files import read_mass_file

    if Z <= 0 or A <= Z:
        return 0.0, 0.0
    exp = 0.0
    if getattr(options, "flagexpmass", True):
        row = read_mass_file(Z, "ame2020").get(A)
        exp = float(np.float32(row[1])) if row else 0.0
    mm = int(getattr(options, "massmodel", 2))
    row = read_mass_file(Z, {1: "frdm", 2: "hfb", 3: "hfbd1m"}[mm]).get(A) if mm != 0 else None
    return exp, (float(np.float32(row[1])) if row else 0.0)


def _beta2(Z: int, A: int, options) -> float:
    """beta2(Zix, Nix, 0) of (Z, A) on the run's mass grid (masses.f90), 0 outside it."""
    from physics.hf.structure.masses import masses

    ms = masses(options)
    zix, nix = int(options.Zinit) - Z, int(options.Ninit) - (A - Z)
    b = ms.beta2
    if not (0 <= zix < b.shape[0] and 0 <= nix < b.shape[1]):
        return 0.0
    v = b[zix, nix]
    return float(v.reshape(-1)[0])


def _f32(x) -> float:
    return float(np.float32(x))


def foldalpha(Z: int, A: int, e_lab, options, params=None):
    """foldalpha.f90 at the lab energies e_lab: (V (E, numjlm), W (E, numjlm), rc) in TALYS's potjlm sign (negative =
    attractive / absorptive) on radjlm, or None without a density table.

    TALYS: foldalpha.f90:1 (foldalpha), afold.f:1 (afold)
    Test: tests/hf/test_kwcov_b7b.py
    """
    from physics.hf.core.constants import talys_constants
    from physics.hf.structure.levels import discrete_levels

    radialmodel = int(getattr(options, "radialmodel", 2))
    tab = radial_table(Z, A, radialmodel)
    if tab is None:
        return None
    rr = tab[0].astype(float)
    mode = int(options.alphaomp)
    a = float(A)
    a2, a3 = a * a, a**3
    a13 = a ** (1.0 / 3.0)
    lv = discrete_levels(Z, A, options)
    e2exp = float(lv.e_mev[1]) if lv.e_mev.shape[0] > 1 else 0.0
    efermia = 0.0
    if mode == 5:
        e1, t1 = _mexc(Z - 2, A - 4, options)  # expmexc(Zix + 2, Nix + 2)
        e2, t2 = _mexc(Z + 2, A + 4, options)  # expmexc(Zix - 2, Nix - 2)
        am1, am2 = (e1, e2) if (e1 != 0.0 and e2 != 0.0) else (t1, t2)
        c = talys_constants()
        efermia = -0.5 * (am1 - am2 + 2.0 * (c["parmass"][6] - 4.0) * c["amu"])

    def adj(name: str) -> float:
        return 1.0 if params is None else _f32(float(params[name][6]))

    fac_r = _f32(pvalue(params, "aradialcor"))
    fac_d = _f32(pvalue(params, "adepthcor"))
    beta2 = _beta2(Z, A, options)
    rv_, uu0, uu1 = _afold_parts(int(Z), int(A), radialmodel)
    e_lab = np.asarray(e_lab, float).reshape(-1)
    out_v = np.zeros((e_lab.shape[0], NUMJLM))
    out_w = np.zeros((e_lab.shape[0], NUMJLM))
    for ie, ee in enumerate(e_lab):
        v5d = 0.0
        as_ = 7.65867 - 7.5669 * e2exp + 2.50486 * e2exp**2
        if mode == 3:  # OMP I: Woods-Saxon volume imaginary
            raw = 0.85281 + 0.02202 * a - 2.14551e-4 * a2 + 7.92942e-7 * a3 - 9.94658e-10 * a2 * a2
            aaw = max(-0.13526 + 0.02029 * a - 1.98441e-4 * a2 + 7.35104e-7 * a3 - 9.15272e-10 * a2 * a2, 1.0e-2)
            es = 0.1024 * a + 1.1307 * as_
            te = 1.0 / (1.0 + math.exp(-(ee - es) / as_))
            expj0 = 135.0 - 0.644 * a if a <= 90.0 else 77.0
            ww = 3.0 / math.pi / raw**3 * expj0 * te
            av5 = 0.0
        elif mode == 4:  # OMP II: volume + surface
            raw = 1.47385 - 0.00134615 * a
            aaw = 0.29
            av5 = 0.9
            es = 0.1024 * a + 1.1307 * as_
            te = 1.0 / (1.0 + math.exp(-(ee - es) / as_))
            expj0 = 135.0 - 0.644 * a if a <= 90.0 else 77.0
            ww = expj0 * te / (raw**3 / 3.0 + 7.603 * av5 * aaw * raw**2 / a13) / math.pi
        else:  # OMP III: volume + surface + dispersion
            raw = 1.47385 - 0.00134615 * a
            aaw = 0.30
            v5d = 0.35
            cc = -0.165 * ee + 2.15 if ee < 13.0 else 0.005
            av5 = v5d * math.exp(-cc * abs(ee - efermia))
            es = 0.0854 * a + 1.1307 * as_
            te = 1.0 / (1.0 + math.exp(-(ee - es) / as_))
            expj0 = 135.0 - 0.644 * a if a <= 96.0 else 75.0
            ww = expj0 * te / ((1.0 - av5) * raw**3 / 3.0 + 7.603 * av5 * aaw * raw**2 / a13) / math.pi
        rww = adj("rvadjust") * raw * a13
        aww = adj("avadjust") * aaw
        www = adj("w1adjust") * ww if mode == 4 else adj("w1adjust") * ww * (1.0 - av5)
        rws = adj("rwdadjust") * 1.09 * rww
        aws = adj("awdadjust") * 1.6 * aww
        wws = adj("d1adjust") * ww * av5
        dwv = dws = 0.0
        if mode == 5:
            dwv, dws = _mahaux(a, ee, 150.0, expj0, as_, es, v5d, raw, aaw, efermia)
        u = uu0 + (-276.0 * (1.0 - 0.005 * ee / 4.0)) * uu1
        volj = _intu_volj(u, float(rv_[1] - rv_[0])) / (4.0 * a)
        cee = (ee - 19.0) ** 2 / 19000.0
        rap = -(337.2 / math.exp(cee)) / volj if abs(cee) < 88.0 else 1.0
        va = fac_d * rap * u
        rva = fac_r * rv_ * (1.0 + abs(beta2) / 15.0 / (1.0 + math.exp((ee - 18.0) / 2.0)))
        klo = np.clip(np.searchsorted(rva, rr, side="right") - 1, 0, len(rva) - 2)
        hh = rva[klo + 1] - rva[klo]
        vopr = (rva[klo + 1] - rr) / hh * va[klo] + (rr - rva[klo]) / hh * va[klo + 1]
        xv = (rr - rww) / aww
        xs = (rr - rws) / aws
        fv = np.where(np.abs(xv) < 88.0, 1.0 / (1.0 + np.exp(np.clip(xv, -88.0, 88.0))), 0.0)
        exs = np.exp(np.clip(xs, -88.0, 88.0))
        gs = np.where(np.abs(xs) < 88.0, 4.0 * exs / (1.0 + exs) ** 2, 0.0)
        if mode == 5:
            vopr = vopr - dwv * fv - dws * gs
        out_v[ie] = vopr
        out_w[ie] = -www * fv - wws * gs
    rc = 1.123 + 2.352 * (a ** (-.666666)) - 2.07 * (a ** (-1.333333))
    return out_v.astype(np.float32).astype(float), out_w.astype(np.float32).astype(float), _f32(rc)


__all__ = ["foldalpha"]
