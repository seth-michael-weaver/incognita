"""the JLM microscopic optical model (`jlmomp y`, `micro y`) for neutrons and protons: radial matter
densities from the structure database, the JLMB folding of Bauge et al. (PRC 63, 024607 (2001)), and the
single-channel solve on the tabulated potential ECIS is handed (ecisinput.f90's "JLM OMP" branch).

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.
`momjlmecis.f` (E. Bauge) ships inside the TALYS repository under its MIT license.

Task: T5 (physics/hf/CONTRACT.md §7). Acceptance test: KWCOV-B7B (tests/hf/test_kwcov_b7b.py).

TALYS routines ported here (file:line of the subroutine/function statement):
    radialtable.f90:1 (radialtable)
    mom.f90:1 (mom)
    momjlmecis.f:1 (momjlmecis)

What TALYS does with `jlmomp y` (and what this module reproduces):
  * structure.f90:86 reads `structure/optical/jlm/<d1m|bskg3>/<Sym>.rad` (radialmodel 2 / 1) or `radialfile Z file`
    for every nucleus; a nucleus whose mass is in the file gets jlmexist(n) = jlmexist(p) = true.
  * flagspher = true (input_omppar.f90:173): every incident channel is spherical, and `rotational` is off by default,
    so the incident channel and every outgoing n / p channel on such a nucleus run ECIS on the JLM potential
    (incidentecis.f90:215, inverseecis.f90:312): hint = 0.1 fm, rmatch = 18 fm, njmax = 1600 (no l cap).
  * mom.f90: the energy-dependent normalisations lv, lw, lv1, lw1, lvso, lwso (jlmmode, the l*adjust keywords) and
    momjlmecis's potentials on r = 0.1 .. 18.2 fm, written to ECIS as tabulated form factors (es20.6 values, f10.5
    strengths): U = lv V_c + i lw W_c + 2 (2 l.s) 0.5 (lvso + i lwso) (1/r) d/dr rho_so + V_Coulomb(rc_Elton).
Not here (refused in input.defaults): the alpha folding potentials (alphaomp 3-5), JLM with preeqmode 3 (bonetti.f90)
and with racap y (racap.f90's JLMB initial state).
"""

from __future__ import annotations

import math
import os
from functools import lru_cache
from pathlib import Path

import numpy as np
import torch

from physics.hf.core.constants import nuclide_symbol, talys_structure_path
from physics.hf.core.tensors import DTYPE

NUMJLM = 200  # A0_talys_mod.f90:54
NPTS = 182  # momjlmecis block data `npts`
H = 0.1  # momjlmecis block data `h` [fm]
NRAD = 182  # incidentecis.f90:222 / inverseecis.f90:319
HINT = 0.1  # ECIS step for JLM (ecisstep 0)
RMATCH = 18.0  # ECIS matching radius for JLM
NJMAX_JLM = 1600


# ------------------------------------------------------------------------------------------------- densities
@lru_cache(maxsize=256)
def _read_rad(path: str, A: int):
    """radialtable.f90:94-121 on one file: (radjlm, rhop, rhon) as float32 (numjlm,) / (numjlm, 5) or None."""
    radjlm = np.zeros(NUMJLM, np.float32)
    rp = np.zeros((NUMJLM, 6), np.float32)
    rn = np.zeros((NUMJLM, 6), np.float32)
    lines = Path(path).read_text(errors="replace").splitlines()
    i = 0
    found = False
    while i < len(lines):
        hdr = lines[i]
        i += 1
        if not hdr.strip():
            continue
        try:  # '(4x, i4, i5, f7.3)'
            ia, nrad, h = int(hdr[4:8]), int(hdr[8:13]), float(hdr[13:20])
        except ValueError as exc:
            raise ValueError(f"TALYS-error: reading {path}: {hdr!r}") from exc
        if ia == A:
            i += 1  # read(2, *): the r = 0 line
            nrad -= 1
            for k in range(min(nrad, NUMJLM)):
                w = [float(x.replace("D", "E").replace("d", "e")) for x in lines[i + k].split()]
                radjlm[k] = w[0]
                rp[k, :5] = w[1:6]
                rn[k, :5] = w[6:11]
            found = True
            break
        i += nrad
    if not found:
        return None
    if nrad < NUMJLM:  # extrapolate (radialtable.f90:126-144), single precision
        h32 = np.float32(h)
        for j in range(5):
            rp0, rp1 = rp[nrad - 1, j], rp[nrad - 2, j]
            rn0, rn1 = rn[nrad - 1, j], rn[nrad - 2, j]
            ap = np.float32(-math.log(rp0 / rp1) / h32) if rp0 * rp1 > 0 else np.float32(0)
            an = np.float32(-math.log(rn0 / rn1) / h32) if rn0 * rn1 > 0 else np.float32(0)
            for ii in range(nrad + 1, NUMJLM + 1):
                dr = np.float32(h32 * (ii - nrad))
                if j == 0:
                    radjlm[ii - 1] = np.float32(radjlm[nrad - 1] + dr)
                expo = np.float32(ap * dr)
                if abs(expo) <= 80.0 and expo > 0.0:
                    rp[ii - 1, j] = np.float32(rp0 * np.exp(-expo, dtype=np.float32))
                expo = np.float32(an * dr)
                if abs(expo) <= 80.0 and expo > 0.0:
                    rn[ii - 1, j] = np.float32(rn0 * np.exp(-expo, dtype=np.float32))
    for a in (radjlm, rp, rn):
        a.setflags(write=False)
    return radjlm, rp, rn


def radial_file(Z: int, radialmodel: int = 2) -> str | None:
    """The density file radialtable.f90:82-93 reads for element Z: `radialfile Z file`, else the database's.

    TALYS: radialtable.f90:1 (radialtable)
    Test: tests/hf/test_kwcov_b7b.py
    """
    from physics.hf.omp import ompdeck

    user = ompdeck.local_file(Z, RADIALFILE_K)
    if user is not None:
        return user
    sub = "bskg3" if int(radialmodel) == 1 else "d1m"
    p = talys_structure_path() / "optical" / "jlm" / sub / f"{nuclide_symbol(Z)}.rad"
    return str(p) if p.is_file() else None


#: `ompdeck.OMPDeck.files` holds (Z, k, path); the `radialfile Z file` lines go there with this k
RADIALFILE_K = -1


def radial_table(Z: int, A: int, radialmodel: int = 2):
    """(radjlm, rhojlmp, rhojlmn) of nucleus (Z, A), or None when TALYS has none (jlmexist false).

    TALYS: radialtable.f90:1 (radialtable)
    Test: tests/hf/test_kwcov_b7b.py
    """
    f = radial_file(int(Z), int(radialmodel))
    if f is None:
        return None
    return _read_rad(f, int(A))


# ------------------------------------------------------------------------------------------------- momjlmecis
# block data of momjlmecis.f (Fortran column order: (rho power, energy power))
_AC = np.array([-974.0, 7097.0, -19530.0, 11.26, -125.7, 418.0, -.0425, .5853, -2.054]).reshape(3, 3, order="F")
_BC = np.array([360.1, -2691.0, 7733.0, -5.224, 51.3, -171.7, .02051, -.247, .8846]).reshape(3, 3, order="F")
_CC = np.array([4.557, -2.051, -65.09, -.005291, -.4906, 3.095, .6108e-5, .001812, -.0119]).reshape(3, 3, order="F")
_DHC = np.array([-.65986e3, .11437e5, -.74505e5, .17609e6, .10768e2, -.29076e3, .22068e4, -.54579e4,
                 -.78863e-1, .24430e1, -.19926e2, .51127e2, .18755e-3, -.62028e-2, .51754e-1,
                 -.13386e0]).reshape(4, 4, order="F")
_FHC = np.array([.45959e3, -.76929e4, .55250e5, -.14373e6, -.64399e1, .14639e3, -.11121e4, .30382e4,
                 .40403e-1, -.10244e1, .79667e1, -.22202e2, -.90086e-4, .23367e-2, -.18008e-1,
                 .50258e-1]).reshape(4, 4, order="F")
_PI = 3.141592653589793


def _pll() -> np.ndarray:
    """prepgl's Y_l0 at cos(theta) = 0 (npgl = 1), l = 0, 2, 4 (the three xform uses, lamax = 3)."""
    s4 = math.sqrt(4.0 * _PI)
    return np.array([1.0, 0.63078310 * (-0.50) * s4, 0.846284367 * 0.375 * s4])


@lru_cache(maxsize=4)
def _kernel(t: float) -> np.ndarray:
    """convolbesl0's folding matrix K (npts, npo-1): out(j) = sum_k K(j, k) in(k), k = 2..npo (Gaussian range t)."""
    nblk8 = NPTS // 8
    npo = 8 * nblk8
    dx = 0.1
    mu = t * t
    bag = np.array([0., 460., -954., 2196., -2459., 2196., -954., 460.])
    k = np.arange(2, npo + 1)
    big = bag[(k - 1) % 8]
    r = (k - 0.1) * dx
    j = np.arange(1, NPTS + 1)
    rprim = j * H
    zz = 2.0 * r[None, :] * rprim[:, None] / mu
    with np.errstate(over="ignore"):
        ser = 1.0 + zz**2 / 6.0 + zz**4 / 120.0 + zz**6 / 5040.0  # the three-term series (zz <= 0.1)
        # sinh(zz)/zz times exp(-r2 - rprim2): exp(zz - r2 - rprim2) - exp(-zz - r2 - rprim2), all over 2 zz
        r2 = (r**2 / mu)[None, :]
        p2 = (rprim**2 / mu)[:, None]
        big_br = 0.5 * (np.exp(zz - r2 - p2) - np.exp(-zz - r2 - p2)) / np.where(zz > 0, zz, 1.0)
        small_br = ser * np.exp(-r2 - p2)
    bes_g = np.where(zz <= 0.1, small_br, big_br)
    newtfac = 8.0 * dx / 945.0
    fnorm = 4.0 * _PI / math.sqrt(mu * _PI) ** 3
    return bes_g * (r**2 / mu * big)[None, :] * newtfac * fnorm * mu


def _prelim(e_lab: np.ndarray, emp: float, em: float, z: float, zp: float):
    """prelim (irel = 1): ecm, emu, zzp."""
    amen = 931.47
    aamu = emp * em / (emp + em)
    emu = 0.047846 * aamu
    xemp, xem = amen * emp, amen * em
    xemt = xemp + xem
    aux = 2.0 * xem * e_lab
    wcm = np.sqrt(xemt * xemt + aux)
    x = aux / (xemt * xemt)
    ecm = np.where(x > 1.0e-3, wcm - xemt, (.0625 * x**3 - .125 * x * x + .5 * x) * xemt)
    wm = xem * (e_lab + xemt) / wcm
    wmp = wcm - wm
    grel = wmp * wm / ((wmp + wm) * amen * aamu)
    aamu = grel * aamu
    emu = grel * emu
    zzp = .034447 * aamu * z * zp
    return ecm, emu, zzp


def _vcoul(rhop: np.ndarray, zzp: np.ndarray, emu: np.ndarray) -> np.ndarray:
    """coul: (E, npts) Coulomb potential from the proton density (l = 0)."""
    h = H
    rmax = NPTS * h
    q = np.zeros(NPTS)
    q[0] = rhop[0] * h * h * h / 3.0
    r = 2.0 * h
    for i in range(1, NPTS):
        q[i] = q[i - 1] + (r * r * rhop[i] + (r - h) * (r - h) * rhop[i - 1]) * h / 2.0
        r = r + h
    v = np.zeros(NPTS)
    v[NPTS - 1] = q[NPTS - 1] / rmax
    r = rmax - h
    for jj in range(2, NPTS + 1):
        i = NPTS - jj  # 0-based of Fortran npts - j + 1
        v[i] = v[i + 1] + (q[i] / (r * r) + q[i + 1] / ((r + h) * (r + h))) * h / 2.0
        r = r - h
    xnorm = (2.0 * zzp) / (rmax * emu * v[NPTS - 1])
    return xnorm[:, None] * v[None, :]


def momjlmecis(Z: int, N: int, zpi: float, e_lab: np.ndarray, lv1: np.ndarray, lw1: np.ndarray,
               rhop5: np.ndarray, rhon5: np.ndarray):
    """momjlmecis.f: (vpot (E, numjlm, 6), rcjlm) for lab energies e_lab (E,).

    TALYS: momjlmecis.f:1 (momjlmecis)
    Test: tests/hf/test_kwcov_b7b.py (vs stock omp.out)
    """
    e = np.asarray(e_lab, dtype=float)
    n_e = e.shape[0]
    emp, zp = (1.0087, 0.0) if zpi == 0.0 else (1.0073, 1.0)
    z, a = float(Z), float(N + Z)
    ecm, emu, zzp = _prelim(e, emp, a, z, zp)
    rc = 1.123 + 2.352 * a ** (-.666666) - 2.07 * a ** (-1.333333)
    rhopi = rhop5[:NPTS, :3].astype(float)
    rhoni = rhon5[:NPTS, :3].astype(float)
    pll = _pll()
    vang = (rhopi + rhoni) @ pll
    valf = ((rhoni - rhopi) @ pll) / vang
    rhop = rhopi[:, 0]
    rhon = rhoni[:, 0]
    # vcorr(r) at the accumulated radius r = h, 2h, ... (jlmcen's `r = r + h`)
    rr = np.cumsum(np.full(NPTS, H))
    if zp != 0.0:
        vc = _vcoul(rhop, zzp, emu)
        xr = 10.0 * rr
        idx = np.floor(xr).astype(int)
        fracp = np.where(idx > 0, xr - idx, 0.0)
        idx = np.where(idx > 0, idx, 1)
        fracm = 1.0 - fracp
        hi = np.minimum(idx, NPTS - 1)  # vcoul(id+1), 1-based id -> 0-based id
        vcorr = fracm[None, :] * vc[:, idx - 1] + fracp[None, :] * vc[:, hi]
    else:
        vcorr = np.zeros((n_e, NPTS))
    tau3 = 2.0 * (0.5 - zp)
    rho = vang[None, :]
    alf = valf[None, :]
    xfr1 = 1.0 / (1.0 + np.exp((ecm - 9.0) / 2.0))[:, None]
    xfr2 = 1.0 - xfr1
    eps1 = -22.0 - rho * (298.52 - 3760.23 * rho + 12435.82 * rho**2)
    eps2 = rho * (-510.8 + 3222.0 * rho - 6250.0 * rho**2)
    eps = eps1 * xfr1 + eps2 * xfr2
    ee = ecm[:, None] - vcorr
    f = ee
    vzero = np.zeros_like(ee)
    redms = np.ones_like(ee)
    ren = np.zeros_like(ee)
    akmass = np.ones_like(ee)
    for ii in range(1, 4):
        for jj in range(1, 4):
            rp_ = rho**ii
            vzero = vzero + _AC[ii - 1, jj - 1] * rp_ * ee ** (jj - 1)
            redms = redms - (jj - 1) * _AC[ii - 1, jj - 1] * rp_ * ee ** (jj - 2)
            ren = ren + _BC[ii - 1, jj - 1] * rp_ * ee ** (jj - 1)
            akmass = akmass - _CC[ii - 1, jj - 1] * rp_ * ee ** (jj - 1)
    emass = redms / akmass
    wzero = np.zeros_like(ee)
    cen = np.zeros_like(ee)
    for i in range(1, 5):
        for j in range(1, 5):
            rp_ = rho**i * f ** (j - 1)
            wzero = wzero + _DHC[i - 1, j - 1] * rp_ / (1.0 + 126.25 / ((f - eps) ** 2))
            cen = cen + _FHC[i - 1, j - 1] * rp_ / (1.0 + 1.0 / (f - eps))
    lv1 = np.asarray(lv1, float)[:, None]
    lw1 = np.asarray(lw1, float)[:, None]
    fr = vzero
    fi = wzero * akmass
    gr = lv1 * akmass * ren
    gi = lw1 * cen / emass * akmass
    vcentr = fr + tau3 * alf * gr
    vcenti = fi + tau3 * alf * gi
    npo = 8 * (NPTS // 8)
    vcr = vcentr[:, 1:npo] @ _kernel(1.25).T
    vci = vcenti[:, 1:npo] @ _kernel(1.35).T
    # simpls: Scheerbaum spin-orbit form factor
    vlt = (2.0 * rhop + rhon) / 3.0 if zp == 0.0 else (2.0 * rhon + rhop) / 3.0
    vls = np.zeros(NPTS)
    vls[NPTS - 1] = (vlt[NPTS - 1] - vlt[NPTS - 2]) / H / (NPTS * H)
    vls[0] = (vlt[1] - vlt[0]) / H / H
    i = np.arange(2, NPTS)
    vls[1:NPTS - 1] = (vlt[i] - vlt[i - 2]) / (2 * H) / (i * H)
    vpot = np.zeros((n_e, NUMJLM, 6))
    vpot[:, :NPTS, 0] = vcr
    vpot[:, :NPTS, 1] = vci
    vpot[:, :NPTS, 4] = vls[None, :]
    vpot[:, :NPTS, 5] = vls[None, :]
    vpot = np.clip(vpot.astype(np.float32), -1.0e30, 1.0e30)  # real vpot(numjlm, 6); potjlm min/max
    return vpot, float(np.float32(rc))


def normalisations(e_lab: np.ndarray, jlmmode: int = 0, params=None) -> np.ndarray:
    """mom.f90's lv, lw, lv1, lw1, lvso, lwso, (6, E) in double, with jlmmode and the l*adjust keywords.

    TALYS: mom.f90:1 (mom)
    Test: tests/hf/test_kwcov_b7b.py
    """
    e = np.asarray(e_lab, dtype=float)
    le = np.log(e * 1000.0)
    lv = .0008 * le + .00018 * le**2.0 + .951
    lw = (1.24 - (1.0 / (1.0 + np.exp((e - 4.5) / 2.9)))) * (1.0 + .06 * np.exp(-((e - 14.0) / 3.7) ** 2)) \
        * (1.0 - 0.09 * np.exp(-((e - 80.0) / 78.0) ** 2))
    lw = np.where(e > 80.0, lw * (1 + (e - 80.0) / 400.0), lw)
    lv1 = 1.5 - (0.65 / (1.0 + np.exp((e - 1.3) / 3.0)))
    alam = np.full_like(e, 0.44)
    if jlmmode == 1:
        alam = 1.10 * np.exp(-0.4 * e**0.25)
    if jlmmode >= 2:
        alam = 1.375 * np.exp(-0.2 * e**0.5)
    if jlmmode == 3:
        lw = lw * 2.0
    lw1 = (1.1 + (alam / (1.0 + (np.exp((e - 40.0) / 50.9)) ** 4))) * (1.0 - .065 * np.exp(-((40.0 - e) / 13.0) ** 2)) \
        * (1.0 - .083 * np.exp(-((200.0 - e) / 80.0) ** 2))
    lvso = 40.0 + np.exp(-e * 0.013) * 130.0
    lwso = -0.2 * (e - 20)
    out = np.stack([lv, lw, lv1, lw1, lvso, lwso])
    if params is not None:  # ompadjustp(1): factor (energy-local: 1) * l*adjust, real(sgl) (mom.f90:94-112)
        for i, name in enumerate(("lvadjust", "lwadjust", "lv1adjust", "lw1adjust", "lvsoadjust", "lwsoadjust")):
            out[i] = float(np.float32(pvalue(params, name))) * out[i]
    return out


def pvalue(params, name: str, default: float = 1.0) -> float:
    """A scalar Params entry (`params["lvadjust"]`), or the default when absent.

    TALYS: mom.f90:1 (mom) -- the l*adjust / aradialcor / adepthcor values
    Test: tests/hf/test_kwcov_b7b.py
    """
    if params is None or name not in params:
        return default
    return float(torch.as_tensor(params[name]).reshape(-1)[0])


def _card7(x: np.ndarray) -> np.ndarray:
    """es20.6: 7 significant digits."""
    x = np.asarray(x, float)
    ax = np.where(x == 0, 1.0, np.abs(x))
    ex = np.floor(np.log10(ax))
    return np.where(x == 0, 0.0, np.round(x / 10.0**ex, 6) * 10.0**ex)


def _f10_5(x):
    return np.round(np.asarray(x, float) * 1.0e5) / 1.0e5


def potential(Z: int, A: int, particle: int, e_lab: np.ndarray, *, jlmmode: int = 0, params=None,
              radialmodel: int = 2, alpha_options=None):
    """The ECIS form factors TALYS writes for the JLM channel (ecisinput.f90:173-226), on r = 0.1 n fm, n = 1..nrad:
    (central (E, nrad) complex, spin-orbit radial factor (E, nrad) complex, rc) in the convention of
    `schrodinger.optical_potential` (central = -(V + iW); the spin-orbit factor multiplies SPIN_ORBIT_FACTOR * 2 l.s),
    or None when the nucleus has no tabulated density.

    TALYS: mom.f90:1 (mom), ecisinput.f90:1 (ecisinput)
    Test: tests/hf/test_kwcov_b7b.py (vs stock omp.out)
    """
    tab = radial_table(Z, A, radialmodel)
    if tab is None:
        return None
    _rad, rp, rn = tab
    e = np.asarray(e_lab, float)
    if particle == 6:  # alphaomp 3-5 (foldalpha.f90): central only, strengths normjlm = 1 (strucinitial.f90:502)
        from physics.hf.omp.foldalpha import foldalpha

        vv, ww, rc = foldalpha(Z, A, e, alpha_options, params)
        central = -_card7(-vv[:, :NRAD]) - 1j * _card7(-ww[:, :NRAD])
        return central, np.zeros_like(central), rc
    norm = normalisations(e, jlmmode, params)
    zpi = 0.0 if particle == 1 else float(Z)
    vpot, rc = momjlmecis(Z, A - Z, zpi, e, norm[2], norm[3], rp, rn)
    pot = _card7(-vpot[:, :NRAD, :].astype(float))  # fext = -potjlm (es20.6)
    pso = _card7(-0.5 * vpot[:, :NRAD, :].astype(float))
    s = _f10_5(norm)  # strengths, f10.5 (column 1 is ECIS's extrapolation flag: blank)
    # ECIS: U = -(strength * fext) for every type (the sign of the value is that of a Woods-Saxon depth)
    central = -(s[0][:, None] * pot[..., 0]) - 1j * (s[1][:, None] * pot[..., 1])
    so = -(s[4][:, None] * pso[..., 4]) - 1j * (s[5][:, None] * pso[..., 5])
    return central, so, rc


# ------------------------------------------------------------------------------------------------- solve
def active(options, Z: int, A: int, particle: int) -> bool:
    """jlmexist(Zix, Nix, particle) under the run's options (radialtable.f90:146-149).

    TALYS: radialtable.f90:1 (radialtable)
    Test: tests/hf/test_kwcov_b7b.py
    """
    if options is None:
        return False
    if particle == 6:  # radialtable.f90:149: alphaomp 3-5 -> jlmexist(., ., 6)
        if not 3 <= int(getattr(options, "alphaomp", 6)) <= 5:
            return False
    elif not getattr(options, "flagjlm", False) or particle not in (1, 2):
        return False
    if particle in getattr(options, "flagrot", ()) or str(particle) in getattr(options, "flagrot", ()):
        return False
    return radial_table(int(Z), int(A), int(getattr(options, "radialmodel", 2))) is not None


def solve(Z: int, A: int, particle: int, e_lab_mev, m_targ_amu: float, lmax: int, options, params):
    """T_lj, reaction / total / shape-elastic cross sections of `particle` on (Z, A) with ECIS on the JLM potential:
    a raw `schrodinger.Transmission` (no njmax clip: njmax = 1600), as `solve_spherical` returns.

    TALYS: incidentecis.f90:1 (incidentecis), inverseecis.f90:1 (inverseecis), ecist.f:14445 (tlnc)
    Test: tests/hf/test_kwcov_b7b.py
    """
    from physics.hf.omp import schrodinger as S

    e = torch.as_tensor(e_lab_mev, dtype=DTYPE).reshape(-1)
    m_proj = S.PARMASS_AMU[particle]
    spin = S.PARSPIN[particle]
    zp = float(Z * S.PARZ[particle])
    e_card = S.ecis_card_energy(e)
    m_proj_r = float(S.ecis_card_value(torch.tensor(m_proj, dtype=DTYPE)))
    m_targ_r = float(S.ecis_card_value(torch.tensor(m_targ_amu, dtype=DTYPE)))
    kin = S.ecis_kinematics(e_card, m_proj_r, m_targ_r, zp)
    # mom gets ecisinput's real(sgl) e (not the input-record value)
    e32 = e.numpy().astype(np.float32).astype(float)
    central, so, rc = potential(Z, A, particle, e32, jlmmode=int(getattr(options, "jlmmode", 0)), params=params,
                                radialmodel=int(getattr(options, "radialmodel", 2)), alpha_options=options)
    n_e = e.shape[0]
    ism = int(round(RMATCH / HINT))
    nmax = ism + 1
    h = torch.full((n_e,), HINT, dtype=DTYPE)
    ism_t = torch.full((n_e,), ism, dtype=torch.int64)
    rm = h * ism
    r = HINT * torch.arange(1, nmax + 1, dtype=DTYPE)
    cen = torch.as_tensor(central[:, :nmax], dtype=torch.complex128)
    sof = torch.as_tensor(so[:, :nmax], dtype=torch.complex128) * S.SPIN_ORBIT_FACTOR
    # Coulomb: input record 7 (itypx -1, reduced radius): homogeneous sphere of radius rc M^(1/3)
    rc_c = float(_f10_5(rc)) * m_targ_r ** (1.0 / 3.0)
    e2z = S.ECIS_CCZ_MEV_FM * zp
    coul = torch.where(r < rc_c, e2z / (2.0 * rc_c) * (3.0 - (r / rc_c) ** 2), e2z / r)[None, :].expand(n_e, nmax)
    if zp == 0:
        coul = torch.zeros_like(coul)
    L, jv, valid, ls2 = S._lj_grid(lmax, spin)
    k2 = kin.k_fm**2
    mu = kin.mu_coef
    g = sof[:, None, None, :] * ls2[None, :, :, None].to(sof.dtype) + cen[:, None, None, :] + coul[:, None, None, :]
    g = g * (mu * h * h)[:, None, None, None]
    ab = (k2 * h * h)[:, None, None, None] - (L * (L + 1))[None, :, None, None] / (
        torch.arange(1, nmax + 1, dtype=DTYPE)[None, None, None, :] ** 2)
    g = ab - g
    x = g - g * g / 12.0
    shape = (n_e, lmax + 1, jv.shape[1])
    u_prev = torch.zeros(shape, dtype=torch.complex128)
    u_cur = torch.ones(shape, dtype=torch.complex128)
    u_am = u_ap = None
    for n in range(1, nmax + 1):
        u_next = 2.0 * u_cur - u_prev - x[..., n - 1] * u_cur
        if n == ism - 1:
            u_am = u_cur
        if n + 1 == ism + 1:
            u_ap = u_next
        u_prev, u_cur = u_cur, u_next
        if n % 25 == 0:
            s = u_cur.abs().clamp_min(1.0e-300)
            u_prev, u_cur = u_prev / s, u_cur / s
            if u_am is not None:
                u_am = u_am / s
            if u_ap is not None and n + 1 > ism:
                u_ap = u_ap / s
    F, dF, G, dG = S.coulomb_functions(kin.eta, kin.k_fm * rm, lmax)
    smat, tlj, valid, jv, rmf, hf = S._match_ecis(u_am, u_ap, F, dF, G, dG, L, jv, valid, h, ism_t, rm, kin)
    sol = S.RadialSolution(smat=smat, tlj=tlj, valid=valid, jvalues=jv, kin=kin, rmatch_fm=rmf, step_fm=hf)
    return S._transmission_of(sol, particle, spin)


def processed(tr, particle: int):
    """inverseread's processing of a JLM solve (fill-in, lmax), without `_clip_to_njmax` (njmax = 1600).

    TALYS: inverseread.f90:1 (inverseread)
    Test: tests/hf/test_kwcov_b7b.py
    """
    from physics.hf.omp.inverse import process_tjl
    from physics.hf.omp.schrodinger import Transmission

    tjl, _, lm = process_tjl(tr.tjl, particle)
    return Transmission(tjl=tjl, nj=tr.nj, sigma_reac_mb=tr.sigma_reac_mb, sigma_tot_mb=tr.sigma_tot_mb,
                        sigma_shape_el_mb=tr.sigma_shape_el_mb, lmax=lm)


def token(options) -> tuple:
    """Cache-key part of a JLM run (the density files it reads).

    TALYS: (none -- cache keys)
    Test: tests/hf/test_kwcov_b7b.py
    """
    if options is None or not (getattr(options, "flagjlm", False) or 3 <= int(getattr(options, "alphaomp", 6)) <= 5):
        return ()
    return ("jlm", int(getattr(options, "jlmmode", 0)), int(getattr(options, "radialmodel", 2)),
            os.environ.get("TALYS_DIR", ""))


__all__ = ["NJMAX_JLM", "RADIALFILE_K", "active", "momjlmecis", "normalisations", "potential", "processed",
           "radial_file", "radial_table", "solve", "token"]
