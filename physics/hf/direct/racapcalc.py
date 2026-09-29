"""Direct radiative capture: the `racapcalc` kernel. OFF by default (`INCOGNITA_DIRECT_CAPTURE`).

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning (racapcalc.f: S. Goriely, Xu Yi). See physics/hf/NOTICE-TALYS.md.

Task: T12 (DIRECTCAP job). Acceptance test: DIRECTCAP (`tests/hf/test_directcap.py` and
`scripts/directcap/talys_agree.py` (engine vs stock TALYS `racap y optmodall y`, racap.tot)).

TALYS routines ported here (file:line of the subroutine statement):
    racapcalc.f:1 (racapcalc), racapcalc.f:880 (sixj), racapcalc.f:1052 (clebs),
    racapcalc.f:1152 (calmagelc), racapcalc.f:1275 (num1l), racapcalc.f:1439 (dephase),
    racapcalc.f:1504 (coufra)
    racap.f90:1 (racap), racapinit.f90:1 (racapinit) -- the inputs they hand to racapcalc

The model: the incident neutron radiates (E1, E2, M1) straight into a bound single-particle state
of the compound nucleus. Final states are the experimental levels below S_n (the ground state
weighted by its spectroscopic factor, excited levels by 0.1 + 0.33 exp(-0.8 E)) and, above the
last one, 0.25 MeV bins of the compound level density ("continuum", Xu & Goriely PRC 86 045801,
2012). The bound state is a Woods-Saxon well (KD03 real volume on the compound nucleus at 1 eV)
rescaled until its eigenvalue sits at the level; the scattering state is the KD03 real volume on
the target at the incident energy.

**Upstream defect this port does not reproduce.** `racapinit.f90` takes the final-state well from
`optical(0, 0, k0, 1e-6)`, but `structure.f90:85` only fills the compound nucleus's OMP arrays
(`omppar(0, 0)`) under `optmodall y`. With TALYS defaults the well depth is 0, no bound state is
found, and `racap y` returns exactly 0 mb for every target at every energy (measured: 10 targets
x 8 energies, DIRECTCAP). The port always uses the KD03 compound-nucleus well, which is what
TALYS computes under `optmodall y`; the agreement test runs stock TALYS that way and compares the
direct-capture column of racap.tot only (optmodall also changes other channels).

**What is energy independent.** Everything up to the bound state (levels, weights, selection
rules, the well-depth search, `wff`) depends only on the target, so `_BoundPass` runs it once per
target in TALYS's own loop order (the search carries `facv1` from one search to the next, and a
second valid spin coupling reuses whatever bound state is current -- both kept). Per energy only
the scattering wave (`dephase`, one per li) and the overlaps are computed.

Precision: TALYS passes and accumulates several single-precision reals (energies, well
parameters, `pi`, `hbarc`, `e2`, the cross-section sums, some literals); those are rounded to
float32 at the same points so the discrete well-depth search takes the same path.
"""

from __future__ import annotations

import math
import os
from dataclasses import dataclass, field
from functools import cache, lru_cache

import numpy as np

__all__ = [
    "mode",
    "RacapStructure",
    "racap_structure",
    "racap_xs",
    "direct_capture_mb",
    "sixj",
    "clebs",
]

F32 = np.float32


def f32(x: float) -> float:
    """Numeric helper.
    TALYS: racapcalc.f:1 (racapcalc; float32 rounding of the Fortran literals)
    Test: tests/hf/test_directcap.py
    """
    return float(F32(x))


def mode() -> str:
    """`INCOGNITA_DIRECT_CAPTURE`: `0`/unset (off, TALYS default), `all` (discrete + continuum,
    TALYS's ispect=3) or `disc` (experimental levels only, TALYS's ispect=1).
    TALYS: racap.f90:1 (racap; keyword racap, ispect)
    Test: tests/hf/test_directcap.py
    """
    v = os.environ.get("INCOGNITA_DIRECT_CAPTURE", "0")
    v = v.strip().lower()
    if v in ("", "0", "n", "no", "off", "false"):
        return "off"
    if v in ("all", "1", "y", "yes", "on", "true", "3"):
        return "all"
    if v in ("disc", "discrete", "exp"):
        return "disc"
    raise ValueError(f"INCOGNITA_DIRECT_CAPTURE={v!r}: expected 0, all or disc")


# ---------------------------------------------------------------------------------------------
# Angular-momentum algebra (racapcalc.f:880 sixj, :1052 clebs). Arguments are doubled (2j, 2m).
# TALYS only ever uses squares of these, so the Racah closed forms stand in for the Fortran's
# goto ladder; tests/hf/test_directcap.py checks them against the compiled Fortran on 97,748
# argument sets. Invalid couplings return 0, as the Fortran does (with an "erreur" print).
# ---------------------------------------------------------------------------------------------

_FACT = [math.factorial(i) for i in range(200)]


def _tri(a: int, b: int, c: int) -> bool:
    return (a + b + c) % 2 == 0 and abs(a - b) <= c <= a + b and min(a, b, c) >= 0


def _delta(a: int, b: int, c: int) -> float:
    return math.sqrt(_FACT[(a + b - c) // 2] * _FACT[(a - b + c) // 2] * _FACT[(-a + b + c) // 2]
                     / _FACT[(a + b + c) // 2 + 1])


@cache
def sixj(j1: int, j2: int, j3: int, l1: int, l2: int, l3: int) -> float:
    """{j1 j2 j3; l1 l2 l3}, doubled arguments. TALYS: racapcalc.f:880 (sixj)
    Test: tests/hf/test_directcap.py
    """
    if not (_tri(j1, j2, j3) and _tri(j1, l2, l3) and _tri(l1, j2, l3) and _tri(l1, l2, j3)):
        return 0.0
    a1, a2 = (j1 + j2 + j3) // 2, (j1 + l2 + l3) // 2
    a3, a4 = (l1 + j2 + l3) // 2, (l1 + l2 + j3) // 2
    b1, b2 = (j1 + j2 + l1 + l2) // 2, (j2 + j3 + l2 + l3) // 2
    b3 = (j3 + j1 + l3 + l1) // 2
    s = 0.0
    for t in range(max(a1, a2, a3, a4), min(b1, b2, b3) + 1):
        s += (-1) ** t * _FACT[t + 1] / (
            _FACT[t - a1] * _FACT[t - a2] * _FACT[t - a3] * _FACT[t - a4]
            * _FACT[b1 - t] * _FACT[b2 - t] * _FACT[b3 - t])
    return (_delta(j1, j2, j3) * _delta(j1, l2, l3) * _delta(l1, j2, l3) * _delta(l1, l2, j3)
            * s)


@cache
def clebs(j1: int, j2: int, j3: int, m1: int, m2: int, m3: int) -> float:
    """<j1 m1 j2 m2 | j3 m3>, doubled arguments. TALYS: racapcalc.f:1052 (clebs)
    Test: tests/hf/test_directcap.py
    """
    if m1 + m2 != m3 or not _tri(j1, j2, j3):
        return 0.0
    if abs(m1) > j1 or abs(m2) > j2 or abs(m3) > j3:
        return 0.0
    if (j1 + m1) % 2 or (j2 + m2) % 2 or (j3 + m3) % 2:
        return 0.0
    pre = math.sqrt((j3 + 1) * _FACT[(j1 + j2 - j3) // 2] * _FACT[(j1 - j2 + j3) // 2]
                    * _FACT[(-j1 + j2 + j3) // 2] / _FACT[(j1 + j2 + j3) // 2 + 1])
    pre *= math.sqrt(_FACT[(j1 + m1) // 2] * _FACT[(j1 - m1) // 2] * _FACT[(j2 + m2) // 2]
                     * _FACT[(j2 - m2) // 2] * _FACT[(j3 + m3) // 2] * _FACT[(j3 - m3) // 2])
    s = 0.0
    kmin = max(0, (j2 - j3 - m1) // 2, (j1 - j3 + m2) // 2)
    kmax = min((j1 + j2 - j3) // 2, (j1 - m1) // 2, (j2 + m2) // 2)
    for k in range(kmin, kmax + 1):
        s += (-1) ** k / (_FACT[k] * _FACT[(j1 + j2 - j3) // 2 - k] * _FACT[(j1 - m1) // 2 - k]
                          * _FACT[(j2 + m2) // 2 - k] * _FACT[(j3 - j2 + m1) // 2 + k]
                          * _FACT[(j3 - j1 - m2) // 2 + k])
    return pre * s


# ---------------------------------------------------------------------------------------------
# racapcalc.f:1152 calmagelc -- single-particle magnetic moment and intrinsic quadrupole
# ---------------------------------------------------------------------------------------------

_LNMAG = (0, 1, 1, 2, 2, 0, 3, 3, 1, 1, 4, 4, 2, 2, 5, 0, 5, 3, 6, 3, 1, 1, 6, 4, 7, 4, 2, 2, 0, 7,
          5, 8, 5)
_SNMAG = tuple(f32(x) for x in (
    0.5, 1.5, 0.5, 2.5, 1.5, 0.5, 3.5, 2.5, 1.5, 0.5, 4.5, 3.5, 2.5, 1.5, 5.5, 0.5, 4.5, 3.5, 6.5,
    2.5, 1.5, 0.5, 5.5, 4.5, 7.5, 3.5, 2.5, 1.5, 0.5, 6.5, 5.5, 8.5, 4.5))
_NNCOM = (2, 6, 8, 14, 18, 20, 28, 34, 38, 40, 50, 58, 64, 68, 80, 82, 92, 100, 114, 120, 124,
          126, 138, 148, 164, 172, 178, 182, 184, 198, 210, 228, 238)
_LPMAG = (0, 1, 1, 2, 2, 0, 3, 3, 1, 4, 1, 4, 5, 2, 2, 0, 5, 6, 3, 3, 1, 1, 6, 7, 4, 4, 2, 2, 7, 0,
          8, 5, 5)
_SPMAG = tuple(f32(x) for x in (
    0.5, 1.5, 0.5, 2.5, 1.5, 0.5, 3.5, 2.5, 1.5, 4.5, 0.5, 3.5, 5.5, 2.5, 1.5, 0.5, 4.5, 6.5, 3.5,
    2.5, 1.5, 0.5, 5.5, 7.5, 4.5, 3.5, 2.5, 1.5, 6.5, 0.5, 8.5, 5.5, 4.5))
_NPCOM = (2, 6, 8, 14, 18, 20, 28, 34, 38, 48, 50, 58, 70, 76, 80, 82, 92, 106, 114, 120, 124,
          126, 138, 154, 164, 172, 178, 182, 196, 198, 216, 228, 238)
_GP, _GN = f32(5.5856), f32(-3.8263)


def _mu_proton(z: int) -> float:
    for i in range(33):
        if z < _NPCOM[i]:
            if _SPMAG[i] - _LPMAG[i] == 0.5:
                return (_SPMAG[i] - 0.5) + 0.5 * _GP
            if _SPMAG[i] - _LPMAG[i] == -0.5:
                return _SPMAG[i] / (_SPMAG[i] + 1.0) * (_SPMAG[i] + 1.5 - 0.5 * _GP)
    return 0.0


def _mu_neutron(n: int) -> float:
    for i in range(33):
        if n < _NNCOM[i]:
            if _SNMAG[i] - _LNMAG[i] == 0.5:
                return 0.5 * _GN
            if _SNMAG[i] - _LNMAG[i] == -0.5:
                return _SNMAG[i] / (_SNMAG[i] + 1.0) * (0.0 - 0.5 * _GN)
    return 0.0


def calmagelc(kz: int, ka: int, b2: float) -> tuple[float, float]:
    """(dmag, qelc). TALYS: racapcalc.f:1152 (calmagelc)
    Test: tests/hf/test_directcap.py
    """
    kn = ka - kz
    if kz % 2 and not kn % 2:
        dmag = _mu_proton(kz)
    elif not kz % 2 and kn % 2:
        dmag = _mu_neutron(kn)
    elif kz % 2 and kn % 2:
        dmag = _mu_proton(kz) + _mu_neutron(kn)
    else:
        dmag = 0.0
    qelc = float(b2) * float(ka) ** f32(5.0 / 3.0) / 0.9174368
    return dmag, qelc


# ---------------------------------------------------------------------------------------------
# racapcalc.f:1275 num1l -- Numerov bound state, Newton on the eigenvalue, node count
# ---------------------------------------------------------------------------------------------

def num1l(n: int, h: float, e: float, s2: float, u: list, no: int, eps: float):
    """Returns (e, s, no); `u` (0..n) is modified in place as in the Fortran. no = -1: the
    requested state is not bound. TALYS: racapcalc.f:1275 (num1l)
    Test: tests/hf/test_directcap.py
    """
    s = [0.0] * (n + 2)
    h12 = h * h / 12
    if e > 0:
        e = 0.0
    dei = 0.0
    epss = 0.1e-10
    if not (u[n - 1] > epss):
        dei = u[n - 1] - epss
        for k in range(1, n + 1):
            u[k] = u[k] - dei
    u[n] = u[n - 1]
    # number of bound states: integration at zero energy
    s[0] = 1.0e-10
    s[1] = 1.0e-10
    b0 = 0.0
    aa = h12 * u[1]
    if s2 != 0:
        b0 = -s[1] * aa
    b1 = s[1] * (1 - aa)
    for k in range(2, n + 1):
        b2 = 12 * s[k - 1] - 10 * b1 - b0
        if not (abs(b2) < 1.0e10):
            b2 = b2 * 1.0e-20
            b1 = b1 * 1.0e-20
        aa = h12 * u[k]
        s[k] = b2 / (1 - aa)
        b0 = b1
        b1 = b2
    n0 = n
    for k in range(5, n + 1):
        n0 = k
        if u[k] < 0:
            break
    nel = 0
    for k in range(n0, n + 1):
        p = s[k - 1] * s[k]
        if p < 0:
            nel += 2
        elif p == 0:
            nel += 1
    nel //= 2
    if nel <= no:
        if nel != no:
            return e, s, -1
        rap1 = s[n - 1] / s[n]
        rap2 = math.exp(h * math.sqrt(u[n - 1] - e))
        if rap1 < rap2:
            return e, s, -1
    # 64: bracket the eigenvalue
    umin = u[1]
    for k in range(2, n + 1):
        if u[k] < umin:
            umin = u[k]
    emin = umin
    emax = 0.0
    te = emax - emin
    if e < emin or e > emax:
        e = emin + te / 2
    e1 = emin
    e2 = emax
    j = 2
    i = 1
    goto = 102
    som = 0.0
    while True:
        if goto == 90:
            emin = e1
            emax = e2
            te = emax - emin
            j = 2
            goto = 98
        if goto == 98:
            i = 1
            goto = 100
        if goto == 100:
            e = emin + te * i / j
            goto = 102
        if goto == 102:
            de = 0.0
            goto = 104
        if goto == 104:
            e = e + de
            if e > 0:
                goto = 204
            else:
                s[n] = 1.0e-10
                n1 = n - 1
                expo = min(h * math.sqrt((u[n - 1] + u[n]) / 2 - e), 80.0)
                rap2 = math.exp(expo)
                s[n1] = s[n] * rap2
                aa = h12 * (u[n1] - e)
                b0 = s[n] * (1 - aa)
                b1 = s[n1] * (1 - aa)
                n1 = n - 2
                k = 1
                for kaux in range(1, n1 + 1):
                    k = n1 - kaux + 1
                    b2 = 12 * s[k + 1] - 10 * b1 - b0
                    aa = h12 * (u[k] - e)
                    s[k] = b2 / (1 - aa)
                    b0 = b1
                    b1 = b2
                    if u[k] < e:
                        break
                n1 = k
                sn1 = s[n1]
                for kk in range(n1, n + 1):
                    s[kk] = s[kk] / sn1
                s[1] = 1.0e-10
                b0 = 0.0
                aa = h12 * (u[1] - e)
                if s2 != 0:
                    b0 = -s[1] * aa
                b1 = s[1] * (1 - aa)
                for k in range(2, n1 + 1):
                    b2 = 12 * s[k - 1] - 10 * b1 - b0
                    aa = h12 * (u[k] - e)
                    s[k] = b2 / (1 - aa)
                    b0 = b1
                    b1 = b2
                sn1 = s[n1]
                for k in range(1, n1 + 1):
                    s[k] = s[k] / sn1
                som = 0.0
                for k in range(1, n + 1):
                    som += s[k] * s[k]
                de = ((-s[n1 - 1] + 2 - s[n1 + 1]) / (h * h) + u[n1] - e) / som
                if abs(de) > eps:
                    goto = 104
                    continue
                # nodes of the eigenstate found
                n0 = n + 1
                for k in range(5, n + 1):
                    if u[k] < e:
                        n0 = k
                        break
                nel = 0
                for k in range(n0, n1 + 1):
                    p = s[k - 1] * s[k]
                    if p < 0:
                        nel += 2
                    elif p == 0:
                        nel += 1
                nel //= 2
                if nel == no:
                    som = 1 / math.sqrt(som * h)
                    for k in range(1, n + 1):
                        s[k] = s[k] * som
                    e = e + dei
                    return e, s, no
                if nel < no:
                    if e > e1:
                        e1 = e
                else:
                    if e < e2:
                        e2 = e
                goto = 204
        if goto == 204:
            i = i + 2
            if i <= j:
                goto = 100
                continue
            j = 2 * j
            if abs(e1 - emin) > eps or abs(emax - e2) > eps:
                goto = 90
            else:
                goto = 98


# ---------------------------------------------------------------------------------------------
# racapcalc.f:1504 coufra -- Coulomb functions F_l, G_l at one l (minl = maxl in racapcalc)
# ---------------------------------------------------------------------------------------------

def coufra(rho: float, eta: float, ll: int) -> tuple[float, float]:
    """(F_l(eta, rho), G_l(eta, rho)) with minl = maxl = l. TALYS: racapcalc.f:1504 (coufra)
    Test: tests/hf/test_directcap.py
    """
    acc = 1.0e-7
    pace = 100.0
    r = rho
    ktr = 1
    minl = ll
    lmax = ll
    xll1 = float(minl * (minl + 1))
    eta2 = eta ** 2
    turn = eta + math.sqrt(eta2 + xll1)
    if r < turn and abs(eta) >= 1.0e-6:
        ktr = -1
    ktrp = ktr
    tf = tfp = 0.0
    while True:  # label 2
        etar = eta * r
        rho2 = r * r
        pl = float(lmax + 1)
        pmx = pl + 0.5
        fp = eta / pl + pl / r
        dk = etar + etar
        dl = 0.0
        d = 0.0
        f = 1.0
        k = (pl * pl - pl + etar) * (pl + pl - 1)
        if pl * pl + pl + etar == 0.0:
            r = r * 1.0000001
            continue
        overflow = False
        while True:  # label 3
            hh = (pl * pl + eta2) * (1 - pl * pl) * rho2
            k = k + dk + pl * pl * 6
            d = 1 / (d * hh + k)
            dl = dl * (d * k - 1)
            if pl < pmx:
                dl = -r * (pl * pl + eta2) * (pl + 1) * d / pl
            pl = pl + 1
            fp = fp + dl
            if d < 0:
                f = -f
            if pl > 20000.0:
                overflow = True
                break
            if not (abs(dl / fp) >= acc):
                break
        if overflow:
            return 0.0, 0.0
        fp = f * fp
        if ktrp == -1:  # label 1: redo at the turning point
            r = turn
            tf = f
            tfp = fp
            lmax = minl
            ktrp = 1
            continue
        break
    # label 5: p + i q at minl
    p = 0.0
    q = r - eta
    pl = 0.0
    ar = -(eta2 + xll1)
    ai = eta
    br = q + q
    bi = 2.0
    wi = eta + eta
    dr = br / (br * br + bi * bi)
    di = -bi / (br * br + bi * bi)
    dp = -(ar * di + ai * dr)
    dq = ar * dr - ai * di
    while True:  # label 6
        p = p + dp
        q = q + dq
        pl = pl + 2.0
        ar = ar + pl
        ai = ai + wi
        bi = bi + 2.0
        d = ar * dr - ai * di + br
        di = ai * dr + ar * di + bi
        t = 1.0 / (d * d + di * di)
        dr = t * d
        di = -t * di
        hh = br * dr - bi * di - 1.0
        k = bi * dr + br * di
        t = dp * hh - dq * k
        dq = dp * k + dq * hh
        dp = t
        if pl > 46000.0:
            return 0.0, 0.0
        if not (abs(dp) + abs(dq) >= (abs(p) + abs(q)) * acc):
            break
    p = p / r
    q = q / r
    g = (fp - p * f) / q
    gp = p * g - q * f
    w = 1.0 / math.sqrt(abs(fp * g - f * gp))
    g = w * g
    gp = w * gp
    if ktr != 1:  # Runge-Kutta from the turning point in to rho (charged particles only)
        f = tf
        fp = tfp
        if rho < 0.2 * turn:
            pace = 999.0
        r3 = 1.0 / 3.0
        hs = (rho - turn) / (pace + 1.0)
        h2 = hs / 2.0
        i2 = int(pace + 0.001)
        etah = eta * hs
        h2ll = h2 * xll1
        s = (etah + h2ll / r) / r - h2
        while True:
            rh2 = r + h2
            t = (etah + h2ll / rh2) / rh2 - h2
            k1 = h2 * gp
            m1 = s * g
            k2 = h2 * (gp + m1)
            m2 = t * (g + k1)
            k3 = hs * (gp + m2)
            m3 = t * (g + k2)
            m3 = m3 + m3
            k4 = h2 * (gp + m3)
            rh = r + hs
            s = (etah + h2ll / rh) / rh - h2
            m4 = s * (g + k3)
            g = g + (k1 + k2 + k2 + k3 + k4) * r3
            gp = gp + (m1 + m2 + m2 + m3 + m4) * r3
            r = rh
            i2 = i2 - 1
            if abs(gp) > 1.0e300:
                return 0.0, 0.0
            if i2 < 0:
                break
        w = 1.0 / (fp * g - f * gp)
    return w * f, g


# ---------------------------------------------------------------------------------------------
# racapcalc.f:1439 dephase -- scattering wave, matched to F/G, normalised
# ---------------------------------------------------------------------------------------------

def dephase(maxv: int, h: float, w: list, eps: float, l: int, eta: float, qk: float):  # noqa: E741 (Fortran name)
    """Returns (y, ifail); y is 1-based (index 0 unused). TALYS: racapcalc.f:1439 (dephase)
    Test: tests/hf/test_directcap.py
    """
    y = [0.0] * (maxv + 1)
    dd = 0.0
    pas = h * eps
    qq = qk * qk
    ll = l + 1
    l1 = l * ll
    r = 2.0 * eta * qk
    rmax = maxv * h
    done = False
    for k in range(2, maxv + 1):
        rmax = rmax - h
        if abs(w[maxv - k + 1] - (l1 / rmax + r) / rmax) < eps:
            continue
        if k > 3:
            done = True
            break
        return y, 1
    if not done:
        rmax = h * (maxv - 2)
    h2 = h ** 2
    h212 = h2 / 12.0
    aa = h212 * (qq - w[1])
    y[1] = h ** ll
    b0 = 0.0
    b1 = y[1] * (1.0 + aa)
    for k in range(2, maxv + 1):
        aa = h212 * (qq - w[k])
        b2 = 12.0 * y[k - 1] - 10.0 * b1 - b0
        y[k] = b2 / (1.0 + aa)
        b0 = b1
        b1 = b2
    r = rmax
    n1 = int((rmax + 1.0e-5) / h) + 1
    fc, gc = coufra(qk * r, eta, l)
    fg1, fg2 = fc, gc
    ifail = 1
    n = maxv + 1
    c = d = dl = 0.0
    for nn in range(n1, maxv + 1):
        r = r + h
        fc, gc = coufra(qk * r, eta, l)
        c = fg2 * y[nn] - gc * y[nn - 1]
        d = fc * y[nn - 1] - fg1 * y[nn]
        z = fg1 * gc - fg2 * fc
        dl = abs(z) / math.sqrt(c * c + d * d)
        if abs(1 - dd / dl) < pas:
            ifail = 0
            n = nn
            break
        dd = dl
        fg1 = fc
        fg2 = gc
    if c == 0.0:
        return y, 1
    d = d / c
    if y[min(n, 200, maxv)] * (fc + gc * d) < 0.0:
        dl = -dl
    for k in range(1, maxv + 1):
        y[k] = y[k] * dl
    return y, ifail


# ---------------------------------------------------------------------------------------------
# inputs (racap.f90 / racapinit.f90)
# ---------------------------------------------------------------------------------------------

_N0N = (0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 2, 0, 1, 0, 1, 2, 2, 0, 1, 0, 1, 2, 2, 3, 0, 1,
        0, 1)
_LN = _LNMAG
_NN = _NNCOM
NUMJPH = 30
NUMDENSRACAP = 200
NUMJLM = 200
NUMLEV2 = 300


@dataclass(frozen=True)
class RacapStructure:
    """Everything racapcalc reads that does not depend on the incident energy."""

    Z: int
    A: int  # target
    a1: float  # target mass, amu (expmass, else thmass)
    af: float  # compound-nucleus mass, amu
    a2: float  # neutron mass, amu (parmass)
    beta2: float  # target beta2 (single)
    spin1: float  # target g.s. spin
    ipa1: int  # target g.s. parity
    spinf_gs: float  # compound g.s. spin
    ipaf_gs: int  # compound g.s. parity
    sn: float  # S_n of the compound nucleus (single)
    lev_e: tuple[float, ...]  # compound levels 1..Nlast (single)
    lev_j: tuple[float, ...]
    lev_p: tuple[int, ...]
    sf_gs: float  # spectfac(0,0,0)
    rhopos: np.ndarray  # (200, 31) chglposj, compound level density, parity +
    rhoneg: np.ndarray  # (200, 31) chglnegj
    vfin: tuple[float, float, float]  # (V, rv, av) KD03 on the compound nucleus at 1e-6 MeV
    omp_target: object = field(default=None, compare=False, repr=False)  # E -> (V, rv, av)


def _kd03_real(Zn: int, Nn: int, e_mev: list[float], options, params) -> list[tuple]:
    import torch

    from physics.hf.omp.parameters import omp_parameters

    e = torch.as_tensor([float(F32(x)) for x in e_mev], dtype=torch.float64)
    o = omp_parameters(Zn, Nn, 1, e, params, options)
    return [(f32(o.v_mev[i]), f32(o.rv_fm[i]), f32(o.av_fm[i])) for i in range(len(e_mev))]


@lru_cache(maxsize=64)
def racap_structure(Z: int, A: int) -> RacapStructure:
    """racapinit + the structure half of racap for a neutron on (Z, A).

    TALYS: racapinit.f90:1 (racapinit), racap.f90:1 (racap)
    Test: tests/hf/test_directcap.py
    """
    import torch

    from physics.hf.compound.dens_reference import _ld_of, _structure_of
    from physics.hf.density.models import density
    from physics.hf.direct.capture import spectroscopic_factors
    from physics.hf.structure.levels import discrete_levels

    options, params, m = _structure_of(Z, A)
    Zc, Ac = Z, A + 1
    cix = m.index(Zc, Ac)
    tix = m.index(Z, A)

    def mass(ix):
        e = float(m.expmass_amu[ix])
        return e if e != 0.0 else float(m.thmass_amu[ix])

    lv_c = discrete_levels(Zc, Ac, options, m, params)
    lv_t = discrete_levels(Z, A, options, m, params)
    ld, _ntop, nlast, _ncum = _ld_of(Zc, Ac, Z, A)
    nlast = int(nlast)
    nexp = nlast + 1  # nlevexpracap (ispect = 3)
    ne = lv_c.e_mev.numpy()
    nj = lv_c.spin.numpy()
    npar = lv_c.parity.numpy()
    nl = min(nexp - 1, len(ne) - 1)  # racapcalc reads levels 1..iexplvnum-1 = 1..Nlast
    lev_e = tuple(f32(ne[i]) for i in range(1, nl + 1))
    lev_j = tuple(f32(nj[i]) for i in range(1, nl + 1))
    lev_p = tuple(int(npar[i]) for i in range(1, nl + 1))
    sf = spectroscopic_factors(Zc, Ac, options, params, ne, nj, npar, nlast, 0)
    # chglposj/negj: density(0, 0, Eldpd, Sldpd, parity, 0, ldmodel=5) (racapinit.f90, ldmodel 3)
    eld = torch.tensor([f32(0.125 + (i - 1) * 0.25) for i in range(1, NUMDENSRACAP + 1)],
                       dtype=torch.float64)[:, None]
    half = 0.5 if Ac % 2 == 1 else 0.0
    sj = torch.tensor([f32(j + half) for j in range(NUMJPH + 1)], dtype=torch.float64)[None, :]
    with torch.inference_mode():
        rp = density(ld, eld, sj, 1, 0, ldmodel=5).double().numpy().copy()
        rn = density(ld, eld, sj, -1, 0, ldmodel=5).double().numpy().copy()
    vfin = _kd03_real(Zc, Ac - Zc, [1.0e-6], options, params)[0]
    b2 = f32(m.beta2[tix])
    return RacapStructure(
        Z=Z, A=A, a1=mass(tix), af=mass(cix), a2=float(_parmass_n()), beta2=b2,
        spin1=f32(lv_t.spin[0]), ipa1=int(lv_t.parity[0]),
        spinf_gs=f32(lv_c.spin[0]), ipaf_gs=int(lv_c.parity[0]),
        sn=f32(m.s_mev[cix][1]), lev_e=lev_e, lev_j=lev_j, lev_p=lev_p, sf_gs=f32(sf[0]),
        rhopos=rp, rhoneg=rn, vfin=vfin,
        omp_target=lambda es, _o=options, _p=params: _kd03_real(Z, A - Z, es, _o, _p))


def _parmass_n() -> float:
    from physics.hf.core.constants import talys_constants

    return float(talys_constants()["parmass"][1])


def _consts() -> tuple[float, float, float, float]:
    from physics.hf.core.constants import talys_constants

    c = talys_constants()
    return f32(c["pi"]), f32(c["e2"]), float(c["amu"]), f32(c["hbarc"])


# ---------------------------------------------------------------------------------------------
# racapcalc.f:1 -- phase A (energy independent) and phase B (per energy)
# ---------------------------------------------------------------------------------------------

@dataclass
class _Term:
    jlev: int
    jspin: int
    jpar: int
    lam: int
    li: int
    fac1: float  # lam 1, 3
    fac1in: float  # lam 2
    fac1re: float  # lam 2
    bound: int  # index into _BoundPass.states


@dataclass
class _BoundPass:
    """Everything racapcalc does before `570` (and the search between), in TALYS's loop order."""

    nlevf: int  # experimental final states below S_n, incl. the g.s. (after racapcalc)
    nlevfmax: int
    exf: list
    terms: list
    states: list  # (ebound, wff)
    early_return: bool  # `E* > Q-value` return inside the level loop


def _bound_pass(st: RacapStructure, ispect: int, ncall: int) -> _BoundPass:
    pi, e2, amu, hc = _consts()
    n = NUMJLM
    rlim = 20.0
    h = rlim / float(n)
    rr = np.array([F32(rlim * float(i) / float(n)) for i in range(1, n + 1)], dtype=F32)
    ka1, kz1, ka2, kz2 = st.A, st.Z, 1, 0
    kaf, kzf = ka1 + ka2, kz1 + kz2
    nnf = kaf - kzf
    a1, a2 = st.a1, st.a2
    sn = st.sn
    n1m = int(a1 + 0.5)
    n2m = int(a2 + 0.5)
    lz = 2 - (n1m + n2m) % 2
    lz1 = 2 - n1m % 2
    lz2 = 2 - n2m % 2
    amn = amu * a2
    hm = hc * hc / (2.0 * amn)
    ama = a1 + a2
    rmu = a1 * a2 / ama
    rm = rmu / hm
    ze = kz1 * kz2 * e2
    rc = f32(1.2) * (float(ka1) ** f32(1.0 / 3.0) + float(ka2) ** f32(1.0 / 3.0))
    spin1 = float(st.spin1)
    ipa1 = st.ipa1
    spin2 = 0.5
    i1 = _nint(spin1 * (ka1 % 2 + 1))
    i2 = _nint(spin2 * (ka2 % 2 + 1))
    i1i2 = (lz1 * i1 + 1) * (lz2 * i2 + 1)
    # final potential (Woods-Saxon, iopt = 1)
    vfn, rfn, afn = st.vfin
    radf = rfn * float(kaf) ** f32(1.0 / 3.0)
    vf = [0.0] * (n + 1)
    for j in range(1, n + 1):
        vf[j] = -vfn / (1.0 + math.exp((float(rr[j - 1]) - radf) / afn))
    # levels
    levmax = NUMLEV2
    exf = [0.0] * (levmax + 2)
    spinff = [0.0] * (levmax + 2)
    ipaff = [0] * (levmax + 2)
    spinff[1] = st.spinf_gs
    ipaff[1] = st.ipaf_gs
    nlevf = 1
    exf[1] = 0.0
    for i in range(len(st.lev_e)):
        if st.lev_e[i] < sn:
            exf[i + 2] = st.lev_e[i]
            spinff[i + 2] = st.lev_j[i]
            ipaff[i + 2] = st.lev_p[i]
            nlevf += 1
            if nlevf >= levmax:
                break
    if ispect == 2:
        nlevf = 1
    emaxex = exf[nlevf]
    nlevf = min(nlevf, levmax)
    rhobin = np.zeros((levmax + 2, NUMJPH + 1, 3))
    for jlev in range(1, nlevf + 1):
        jspin = _nint(spinff[jlev] - float(kaf % 2) / 2.0)
        jspin = max(min(jspin, NUMJPH), 0)
        jparity = min(_nint(ipaff[jlev] / 2.0 + 1.5), 2)
        rhobin[jlev, jspin, jparity] = 1.0
    nlevfmax = nlevf
    if ispect != 1 and nlevfmax < levmax:
        binw = 0.25
        kethmin = _nint(emaxex / binw + 0.499) + 1
        ethmin = float(kethmin - 1) * binw
        kethmax = min(int(sn / binw), NUMDENSRACAP)
        nlevfmax = min(nlevf + kethmax - kethmin + 1, levmax)
        rp = st.rhopos.copy()
        rn = st.rhoneg.copy()
        for _ in range(ncall):  # racapcalc.f: the g.s. is taken out of bin 1 IN PLACE, each call
            for j in range(NUMJPH + 1):
                if rp[0, j] >= 1.0:
                    rp[0, j] -= 1.0
                if rn[0, j] >= 1.0:
                    rn[0, j] -= 1.0
        for keth in range(kethmin, kethmax + 1):
            jlev = nlevf + (keth - kethmin + 1)
            if jlev > levmax:
                continue
            exf[jlev] = f32(ethmin + binw * (keth - kethmin + 0.5))
            for j in range(NUMJPH + 1):
                rhobin[jlev, j, 1] = max(rp[keth - 1, j] * binw, 0.0)
                rhobin[jlev, j, 2] = max(rn[keth - 1, j] * binw, 0.0)
    iexplvnum = nlevf
    if sn <= 0.0:
        return _BoundPass(nlevf=nlevf, nlevfmax=0, exf=exf, terms=[], states=[], early_return=True)
    terms: list[_Term] = []
    states: list[tuple] = [(0.0, [0.0] * (n + 2))]
    cur = 0
    ebound = 0.0
    facv1 = 0.0
    wff = states[0][1]
    early = False
    for jlev in range(1, nlevfmax + 1):
        ef = float(exf[jlev])
        if ef > sn:
            early = True
            break
        for jspin in range(NUMJPH + 1):
            for jparity in (1, 2):
                spinf = float(jspin + float(kaf % 2) / 2.0)
                ipaf = int((float(jparity) - 1.5) * 2.0)
                if jlev > 1:
                    weight = rhobin[jlev, jspin, jparity] * (0.1 + 0.33 * math.exp(f32(-0.8) * ef))
                else:
                    weight = rhobin[jlev, jspin, jparity] * float(st.sf_gs)
                if weight <= 1.0e-20:
                    continue
                if ispect != 2:
                    if jlev <= iexplvnum:
                        if spinff[jlev] != spinf or ipaff[jlev] != ipaf:
                            continue
                else:
                    if jlev == 1 and (spinff[1] != spinf or ipaff[1] != ipaf):
                        continue
                jf = int(spinf * (kaf % 2 + 1)) * lz
                ipasslam = 0
                for lam in (1, 2, 3):
                    if lam == 1:
                        fac0 = f32(f32(f32(8.0) * pi) * 2) / float(3) ** 2.0 / (lam * 100 * i1i2)
                    elif lam == 2:
                        fac0 = f32(f32(f32(8.0) * pi) * 3) / float(15) ** 2.0 / (lam * 100 * i1i2)
                    else:
                        fac0 = (f32(f32(f32(f32(0.011) * f32(8.0)) * pi) * 2) / float(3) ** 2.0
                                / (1 * 100 * i1i2))
                    icont = 1
                    lfmin = int(abs(spinf - spin1) - 0.5)
                    ipalf = int((-1) ** lfmin)
                    if ipa1 * ipaf != ipalf:
                        lfmin += 1
                    if lfmin < 0:
                        lfmin += 2
                    limin = lfmin - lam if lam in (1, 2) else lfmin
                    if limin < 0:
                        limin += 2
                    if lfmin != int(abs(spinf - spin1) - 0.5):
                        icont = 2
                    if i1 == 0 or jf == 0:
                        icont = 1
                    li = limin
                    lf = lfmin
                    licut = 6 - 2 * lam if lam in (1, 2) else 4
                    if li > licut or lf < 0 or li < 0:
                        continue
                    n0 = 0
                    for j in range(33):
                        if _LN[j] == lfmin and _NN[j] <= nnf:
                            n0 = _N0N[j] + 1
                        if _LN[j] == lfmin and _NN[j] > nnf:
                            n0 = _N0N[j]
                            break
                    n0init = n0
                    ipass = 0
                    jjmax = 2 * li + 1
                    for ipos in range(1, icont + 1):
                        ipassf = -1
                        spii = spin1 + spin2
                        if ipos == 2:
                            spii = spin1 - spin2
                        if icont == 1 and (spii < abs(spinf - lf) or spii > spinf + lf):
                            spii = spin1 - spin2
                        ii = int(spii * (kaf % 2 + 1)) * lz
                        ifv = ii
                        for jj in range(1, jjmax + 1):
                            spini = spii + float(li - jj + 1)
                            if spini < 0:
                                continue
                            lt = lam if lam in (1, 2) else 1
                            if spini > spinf + lt or spini < abs(spinf - lt):
                                continue
                            ipassf += 1
                            ji = int(spini * (kaf % 2 + 1)) * lz
                            if ji > ifv + 2 * li or ji < abs(ifv - 2 * li) or n0 < 0:
                                continue
                            if jf < abs(2 * lf - ifv) or jf > 2 * lf + ifv or n0 < 0:
                                continue
                            if ji < abs(2 * li - ii) or ji > 2 * li + ii or n0 < 0:
                                continue
                            if lam in (1, 2):
                                if lam * 2 < abs(ji - jf) or lam * 2 > ji + jf:
                                    continue
                            else:
                                if 2 < abs(ji - jf) or 2 > ji + jf:
                                    continue
                            fac1 = fac1in = fac1re = 0.0
                            if lam == 1:
                                c1 = clebs(2 * li, 2, 2 * lf, 0, 0, 0)
                                s1 = sixj(jf, ji, 2, 2 * li, 2 * lf, ii)
                                facree1 = ((kz1 * (a2 / ama) ** 1.0 + kz2 * (-a1 / ama) ** 1.0)
                                           ** 2.0 * 3.0 * (jf + 1) * (ji + 1) * (2 * li + 1)
                                           * (c1 * s1) ** 2.0)
                                fac1 = fac0 * facree1 * weight
                            elif lam == 2:
                                c2 = clebs(2 * li, 4, 2 * lf, 0, 0, 0)
                                s2 = sixj(jf, ji, 4, 2 * li, 2 * lf, ii)
                                facree2 = ((kz1 * (a2 / ama) ** 2.0 + kz2 * (-a1 / ama) ** 2.0)
                                           ** 2.0 * 5.0 * (jf + 1) * (ji + 1) * (2 * li + 1)
                                           * (c2 * s2) ** 2.0)
                                fac1re = fac0 * facree2 * weight
                                if lz1 * i1 >= 2 and li == lf:
                                    estar1 = sixj(lz1 * i1, lz2 * i2, ifv, ii, 4, lz1 * i1)
                                    estar2 = sixj(ji, jf, 4, ifv, ii, 2 * lf)
                                    ectar = clebs(lz1 * i1, 4, lz1 * i1, lz1 * i1, 0, lz1 * i1)
                                    _dm, qelc1 = calmagelc(kz1, ka1, st.beta2)
                                    pre = f32(f32(f32(float((ji + 1) * (lz1 * i1 + 1) * (ii + 1)
                                                            * (ifv + 1)) * f32(5.0)) / f32(16.0))
                                              / pi)
                                    facine2 = (pre * qelc1 * qelc1 * estar1 ** 2.0
                                               * estar2 ** 2.0 / ectar ** 2.0)
                                else:
                                    facine2 = 0.0
                                fac1in = fac0 * facine2 * weight
                            else:
                                if lf == li:
                                    srem = sixj(ji, jf, 2, 2 * li, 2 * lf, ii)
                                    facrem1 = ((kz1 / a1 * (a2 / ama) ** 1.0
                                                - kz2 / a2 * (-a1 / ama) ** 1.0) ** 2.0
                                               * (jf + 1) * 3.0 * li * (li + 1) * (2 * li + 1)
                                               * (ji + 1) * srem ** 2.0)
                                    if lz1 * i1 == 0:
                                        factarm1 = 0.0
                                    else:
                                        starm = sixj(lz1 * i1, lz2 * i2, ifv, ii, 2, lz1 * i1)
                                        ctarm = clebs(lz1 * i1, 2, lz1 * i1, lz1 * i1, 0, lz1 * i1)
                                        sinallm = sixj(ji, jf, 2, ifv, ii, 2 * lf)
                                        dmag1, _q = calmagelc(kz1, ka1, st.beta2)
                                        pre = f32(f32(f32(float((ji + 1) * (lz1 * i1 + 1)
                                                                * (ii + 1) * (ifv + 1))
                                                          * f32(3.0)) / f32(4.0)) / f32(3.14159))
                                        factarm1 = (pre * dmag1 * dmag1 * starm ** 2.0
                                                    * sinallm ** 2.0 / ctarm ** 2.0)
                                    if lz2 * i2 == 0:
                                        facprojm1 = 0.0
                                    else:
                                        sprojm = sixj(lz2 * i2, lz1 * i1, ifv, ii, 2, lz2 * i2)
                                        cprojm = clebs(lz2 * i2, 2, lz2 * i2, lz2 * i2, 0,
                                                       lz2 * i2)
                                        sinallm = sixj(ji, jf, 2, ifv, ii, 2 * lf)
                                        dmag2, _q = calmagelc(kz2, ka2, st.beta2)
                                        pre = f32(f32(f32(float((ji + 1) * (lz2 * i2 + 1)
                                                                * (ii + 1) * (ifv + 1))
                                                          * f32(3.0)) / f32(4.0)) / f32(3.14159))
                                        facprojm1 = (pre * dmag2 * dmag2 * sprojm ** 2.0
                                                     * sinallm ** 2.0 / cprojm ** 2.0)
                                    fac1 = fac0 * (facrem1 + factarm1 + facprojm1) * weight
                                else:
                                    fac1 = 0.0
                            searched_ok = True
                            if not (ipass != 0 or ipassf != 0 or ipasslam != 0):
                                # the well-depth search (racapcalc.f:430-490)
                                s2 = 0.0
                                e = 0.0
                                umax = 0.0
                                ee0 = 0.0
                                facv = 1.0
                                xfac = f32(0.05)
                                fvmax = f32(1.3)
                                jtestmax = int((fvmax - 1.0) / xfac)
                                itest = 0
                                itestmax = 20
                                jtest = 0
                                itrue = 1
                                eps = 1.0e-4
                                found = False
                                while True:
                                    itest += 1
                                    ee1 = ee0
                                    potf = [0.0] * (n + 1)
                                    for j in range(1, n + 1):
                                        x = j * h
                                        vn = facv * vf[j]
                                        vc = ze / x
                                        if x <= rc:
                                            vc = ze * (3 - (x / rc) ** 2.0) / 2.0 / rc
                                        vce = lf * (lf + 1) / x / x
                                        potf[j] = (vn + vc) * rm + vce
                                    e, s, n0 = num1l(n, h, e, s2, potf, n0, eps)
                                    wff_try = s
                                    ebound = (e + umax) / rm
                                    ee0 = sn + ebound
                                    if abs(ee0 - ef) < 100.0 * eps and n0 != -1:
                                        found = True
                                        break
                                    if itest > itestmax:
                                        break
                                    if n0 == -1:
                                        jtest += 1
                                        n0 = n0init
                                        ee0 = float(sn)
                                        facv = facv + xfac * 2.0
                                        if jtest > jtestmax:
                                            break
                                        continue
                                    facv0 = facv
                                    if itest == 1:
                                        ee1 = ee0
                                    if itrue == 1:
                                        if ee0 > ef and ee1 > ef:
                                            facv = facv + xfac
                                        if ee0 < ef and ee1 < ef:
                                            facv = facv - xfac
                                        if (ee0 - ef) * (ee1 - ef) < 0.0 and ee1 != ee0:
                                            itrue = 0
                                    if itrue != 1:
                                        if ee0 == ee1:
                                            xfac = xfac / 2.0
                                            if ee0 < ef:
                                                facv = facv - xfac
                                            if ee0 > ef:
                                                facv = facv + xfac
                                        else:
                                            facv = (facv0 + (facv1 - facv0) / (ee1 - ee0)
                                                    * (ef - ee0))
                                    facv1 = facv0
                                # the bound state is whatever num1l left, found or not
                                wff = wff_try
                                states.append((ebound, wff))
                                cur = len(states) - 1
                                if not found:
                                    searched_ok = False
                                elif facv > fvmax or facv < f32(f32(1.0) / fvmax):
                                    searched_ok = False
                                else:
                                    ipass += 1
                                    ipasslam = 1
                            if not searched_ok:
                                break  # goto 500: next ipos
                            terms.append(_Term(jlev, jspin, jparity, lam, li, fac1, fac1in,
                                               fac1re, cur))
    return _BoundPass(nlevf=iexplvnum, nlevfmax=nlevfmax, exf=exf, terms=terms, states=states,
                      early_return=early)


def _nint(x: float) -> int:
    """Fortran NINT/IDNINT: round half away from zero."""
    return int(math.floor(x + 0.5)) if x >= 0 else -int(math.floor(-x + 0.5))


def _energy_pass(st: RacapStructure, bp: _BoundPass, ein: float, vtarget: tuple) -> dict:
    """racapcalc.f:570-530 for one incident energy: sums in barns, as TALYS (single)."""
    pi, e2, amu, hc = _consts()
    n = NUMJLM
    h = 20.0 / float(n)
    rr = np.array([F32(20.0 * float(i) / float(n)) for i in range(1, n + 1)], dtype=F32)
    a1, a2 = st.a1, st.a2
    ama = a1 + a2
    rmu = a1 * a2 / ama
    amn = amu * a2
    hm = hc * hc / (2.0 * amn)
    rm = rmu / hm
    fsc = hc / e2
    ein = f32(ein)
    ecm = f32(ein * a1 / (a2 + a1))
    e0 = float(ecm)
    eta = 0.0  # neutron: eta0 = 0
    qk = math.sqrt(e0 * rm)
    vn0, rn0, an0 = vtarget
    rad1 = F32(rn0 * float(st.A) ** f32(1.0 / 3.0))
    with np.errstate(over="ignore"):
        vi = (-F32(vn0) / (F32(1.0) + np.exp((rr - rad1) / F32(an0)))).astype(np.float64)
    eps = 1.0e-4
    waves: dict[int, tuple] = {}
    xsall = [F32(0.0)] * 3
    esig = F32(0.0)
    per_lev = {}
    for t in bp.terms:
        if t.li not in waves:
            li = t.li
            poti = [0.0] * (n + 1)
            for j in range(1, n + 1):
                x = j * h
                poti[j] = (1.0 * vi[j - 1]) * rm + li * (li + 1) / x / x
            waves[li] = dephase(n, h, poti, eps, li, eta, qk)
        wfi, ifail = waves[t.li]
        if ifail == 1:
            continue
        ebound, wff = bp.states[t.bound]
        if t.lam == 2:
            fac2in = t.fac1in * ((e0 - ebound) / hc) ** 5.0 / (qk * qk * fsc) * math.sqrt(
                rmu * amn / e0 / 2.0)
            fac2re = t.fac1re * ((e0 - ebound) / hc) ** 5.0 / (qk * qk * fsc) * math.sqrt(
                rmu * amn / e0 / 2.0)
            zin = zre = 0.0
            for j in range(1, n + 1):
                p = wff[j] * wfi[j]
                zin += p
                zre += p * (j * h) ** 2.0
            val = (zin * h) ** 2.0 * fac2in + (zre * h) ** 2.0 * fac2re
        else:
            fac2 = t.fac1 * ((e0 - ebound) / hc) ** 3.0 / (qk * qk * fsc) * math.sqrt(
                rmu * amn / e0 / 2.0)
            z = 0.0
            if t.lam == 1:
                for j in range(1, n + 1):
                    z += wff[j] * wfi[j] * (j * h) ** 1.0
            else:
                for j in range(1, n + 1):
                    z += wff[j] * wfi[j]
            val = (z * h) ** 2.0 * fac2
        k = {1: 0, 2: 1, 3: 2}[t.lam]
        if t.lam == 2:  # xsall(2) = xsall(2) + elmatin + elmatre, left to right in double
            vin = (zin * h) ** 2.0 * fac2in
            vre = (zre * h) ** 2.0 * fac2re
            xsall[k] = F32(float(xsall[k]) + vin + vre)
            esig = F32(float(esig) + 0.0 + vin + vre)
        else:
            xsall[k] = F32(float(xsall[k]) + val)
            esig = F32(float(esig) + val + 0.0 + 0.0)
        per_lev[t.jlev] = per_lev.get(t.jlev, 0.0) + val
    disc = sum(v for j, v in per_lev.items() if j <= bp.nlevf)
    cont = sum(v for j, v in per_lev.items() if j > bp.nlevf)
    mb = F32(1000.0)
    return {
        "total_mb": float(F32(esig * mb)),
        "e1_mb": float(F32(xsall[0] * mb)),
        "e2_mb": float(F32(xsall[1] * mb)),
        "m1_mb": float(F32(xsall[2] * mb)),
        "disc_mb": float(F32(F32(disc) * mb)),
        "cont_mb": float(F32(F32(cont) * mb)),
    }


@lru_cache(maxsize=512)
def _bound_cached(Z: int, A: int, ispect: int, ncall: int) -> _BoundPass:
    return _bound_pass(racap_structure(Z, A), ispect, ncall)


def racap_xs(Z: int, A: int, energies, ispect: int = 3) -> dict[str, np.ndarray]:
    """Direct radiative capture of a neutron on (Z, A) at incident energies (MeV, lab), in mb:
    total, E1/E2/M1 and the discrete / continuum split, as TALYS's racap.tot / racap.f90 give them
    (with the compound-nucleus well TALYS only builds under `optmodall y`; see module docstring).
    `ispect` 3 = discrete + continuum (TALYS), 1 = experimental levels only.

    The g.s. is taken out of level-density bin 1 once per call in TALYS (`ncall` below), which
    only matters when no excited level lies below S_n; energies are treated as one TALYS run in
    the order given.

    TALYS: racap.f90:1 (racap), racapcalc.f:1 (racapcalc)
    Test: tests/hf/test_directcap.py
    """
    es = [float(x) for x in np.atleast_1d(np.asarray(energies, dtype=float))]
    st = racap_structure(Z, A)
    vt = st.omp_target(es)
    out = {k: np.zeros(len(es)) for k in ("total_mb", "e1_mb", "e2_mb", "m1_mb", "disc_mb",
                                           "cont_mb")}
    st_needs_calls = _needs_call_index(st)
    for i, (e, v) in enumerate(zip(es, vt, strict=True)):
        bp = _bound_cached(Z, A, ispect, (i + 1) if st_needs_calls else 1)
        r = _energy_pass(st, bp, e, v)
        for k in out:
            out[k][i] = r[k]
    return out


def _needs_call_index(st: RacapStructure) -> bool:
    emaxex = 0.0
    for e in st.lev_e:
        if e < st.sn:
            emaxex = e
    return _nint(emaxex / 0.25 + 0.499) + 1 == 1


def direct_capture_mb(Z: int, A: int, energies, which: str | None = None) -> np.ndarray:
    """The capture addend of `INCOGNITA_DIRECT_CAPTURE` (mb, one per energy): zeros when off, the
    racap total for `all`, the experimental-level part only for `disc`. Every engine path adds
    this to its (n,g) cross section: the direct-capture populations sit below S_n, so TALYS's own
    capture channel grows by exactly xsracape (binary.f90:273-277; checked on stock TALYS).
    TALYS: binary.f90:273-277 (xsracape)
    Test: tests/hf/test_directcap.py
    """
    w = mode() if which is None else which
    es = np.atleast_1d(np.asarray(energies, dtype=float))
    if w == "off" or A < 1:
        return np.zeros(len(es))
    return _cached_addend(Z, A, tuple(float(x) for x in es), w)


@lru_cache(maxsize=4096)
def _cached_addend(Z: int, A: int, es: tuple, w: str) -> np.ndarray:
    if w == "disc":
        r = racap_xs(Z, A, es, ispect=1)
    else:
        r = racap_xs(Z, A, es, ispect=3)
    return np.asarray(r["total_mb"], float)


def add_to_results(res, injection):
    """`engine.run` / `engine_c.run` Results with the `INCOGNITA_DIRECT_CAPTURE` addend in the
    capture channel (xs000000) and in the compound nucleus's residual production, in place.
    Only for a dump-free chained run (`injection` carries Z and A); off -> untouched.

    TALYS: binary.f90:273-277 (xspopnuc(0,0) and xsbinary(0) grow by xsracape)
    Test: tests/hf/test_directcap.py
    """
    if mode() == "off" or getattr(injection, "families", ()) or not hasattr(injection, "Z"):
        return res
    import torch

    Z, A = int(injection.Z), int(injection.A)
    e = res.e_inc_mev.detach().cpu().numpy()
    dc = torch.as_tensor(direct_capture_mb(Z, A, e), dtype=res.e_inc_mev.dtype)
    if "xs000000" in res.channels_mb:
        res.channels_mb["xs000000"] = res.channels_mb["xs000000"] + dc
    from physics.hf.results import residual_key

    k = residual_key(Z, A + 1)
    if k in res.residual_production_mb:
        res.residual_production_mb[k] = res.residual_production_mb[k] + dc
    return res
