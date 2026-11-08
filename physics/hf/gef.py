"""KWCOV B14 part 2 (GEF): the GEF Monte Carlo fission model of TALYS, `massdis y` + `fymodel 2` (TALYS's default).

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning (GEF: K.-H. Schmidt and B. Jurado; FORTRAN version V. Simutkin and M. Onegin).
See physics/hf/NOTICE-TALYS.md.

`geftalys(Z, A, Exfis, xsfis, nevt, stream)` is geftalys.f: per fissioning nucleus, for every excitation bin
(Exfis, xsfis), `nevt` (= gefran) Monte Carlo fission events: fission mode, fragment mass and charge, excitation
energies, spins, TKE, then neutron (and gamma) evaporation from both fragments. It returns what massdis.f90 reads from
the /outgef/ commons: ysum / ysump (pre / post-neutron mass yields x xs), yAZ / yAZp (isotopic), anpre_sum (nu per
pre-neutron mass), ann_sum (P(nu)), anMean_sum (nubar), each summed over the bins with weight xsfis.

Random numbers. GEF draws from the MCNP 48-bit generator of geftalys.f (`ran2`, X <- 0x1158C4D60917D X mod 2^48 as
gb * 2^24 + gs, seeded 5^19 at every geftalys call; `rndm` = sngl(X / 2^48)); Gaussians from PGauss (polar Box-Muller
with a cached second value, whose cache is a DATA-initialised SAVE variable: ISet = 1, GSet = 0.5 at program start, and
it carries across geftalys calls, nuclides and incident energies). The port has the same generator in two layouts:
    * stream="talys": one lane, events one after the other: the exact stock stream. The caller keeps a `GefStream` for
      the whole run so the PGauss cache carries as in TALYS. Slow (python-speed per event); for checks.
    * stream="lanes" (the engine's default): the events of a bin run in lockstep, one lane each; lane i draws from its
      own substream (odd 48-bit start from splitmix64 of the lane index, lane_seeds), PGauss cache per lane starting
      empty. Every lane follows exactly the stock per-event sequence of draws; only the streams differ, so results agree
      with stock statistically (and are deterministic: same deck, same numbers).
Arithmetic is single precision as geftalys.f (implicit REAL*4): numpy float32 for + - * / sqrt (IEEE, as gfortran -O3
-ffp-contract=off); exp / log / pow / sin / log10 / erf are evaluated in double and rounded once (glibc's float
versions are correctly rounded in nearly all cases); integer powers expand as gfortran's powi table (x**3 = x*(x*x),
x**4 = (x*x)*(x*x), x**5 = (x*x)*(x*(x*x))); NINT rounds half away from zero.

Kept TALYS/GEF quirks: the heavy-fragment spin and the Fermi-gas energy split use the stale `A1` of the last mode-3
deformation loop (A1 = (Z_CN - 10 + 0.5) / Z_CN * A_CN); mode 2 draws a discarded PGauss before PBox; mode 4's light
fragment deformation width uses beta(2,2,Z) (copy of mode 5); the even-odd tables of modes 4/5 are rewritten in loop
order; Ivenodd clamps the table entry to <= 1 in place; P(nu) counts only events with >= 1 neutron (aNN(0) is never
filled) and nu(A) averages over fragments that emitted 1..20 neutrons; PEgammahigh never fills sigma(N) (its Eg runs
one step behind M). Diagnostic-only GEF arrays (Edefo2d, Eintr2d, Eexc2d, Ecoll2d, AEkin, JFRAGpre, ZISO*, ANZ*,
Egamma, ArrayEn/Tn) are not kept; some of them index out of bounds in stock (Eintr2d(A, nint(10 E + 0.5)) with E < 0),
which in a static layout lands in the neighbouring diagnostic array.

TALYS routines ported here (file:line of the subroutine / function statement):
    geftalys.f:1 (geftalys)                       setup, modes, energy sorting, spins, event loop, bin sums
    geftalys.f:2347 (AyPair), 2368 (BetaEquiA), 2409 (Eva), 2584 (ALDMas), 2602 (Ushell), 2617 (UMass),
    2623 (Zequi), 2674 (betalight), 2685 (betaheavy), 2695 (AMasscurv), 2716 (DeSaddleScission), 2727 (TRusanovf),
    2737 (IVENODD), 2797 (Erf), 2811 (Erfc), 2826 (fTanh), 2832 (PBox), 2849 (PGauss), 2873 (PLinGauss),
    2886 (Ualev), 2894 (UTemp), 2936 (PEN1), 2983 (PEgammahigh), 3034 (E0GDR), 3057 (WidthGDR), 3063 (IMATENDF),
    3075 (rndm), 3108 (random: setijk / setran), 3135 (ran2)
    geffunctions.f:74 (Getyield), 112 (F1), 120 (F2), 225 (TEgidy), 268 (LyMass), 303 (LyPair), 412 (LDMass),
    440 (AME2012), 512 (U_SHELL_EO_exp), 549 (ECOUL), 1093 (BFTF), 1221 (BFTFB), 1254 (Gaussintegral)
    massdis.f90:263-292 (GEF data: beldm.dat, ushell.dat, nucprop.dat)
Not ported: geffunctions.f:728 (Beta_Equi; geftalys overwrites its result with BetaEquiA, BSUB = .true.), gefsub.f
(fymodel 3, KWCOV B14 part 3).
Task: T10 (physics/hf/CONTRACT.md section 7; KWCOV batch B14 part 2, output only). Acceptance test: KWCOV-B14b
(tests/hf/test_kwcov_b14b.py, scripts/kwcov/b14b_response.py, docs/hf/COVERAGE_PLAN.md).
"""

from __future__ import annotations

import math
import os
from dataclasses import dataclass, field
from functools import lru_cache

import numpy as np

F = np.float32
D = np.float64
M48 = (1 << 48) - 1
#: ran2's multiplier gb * 2^24 + gs (geftalys.f:3138-3139)
GMUL = 1136868 * (1 << 24) + 6328637
#: setijk(5^19), setran (geftalys.f:73-75)
SEED = 5 ** 19
NUMNU = 50


# ------------------------------------------------------------------------------------------------ float32 helpers
def _a(x):
    return np.asarray(x, dtype=F)


def _o(r):
    return r if np.ndim(r) else r[()]


def expf(x):
    """expf: float32 helper.

    TALYS: geftalys.f / geffunctions.f EXP (single precision, rounded once)
    Test: tests/hf/test_kwcov_b14b.py
    """
    with np.errstate(all="ignore"):
        return _o(np.exp(_a(x).astype(D)).astype(F))


def logf(x):
    """logf: float32 helper.

    TALYS: geftalys.f ALOG / LOG (single precision)
    Test: tests/hf/test_kwcov_b14b.py
    """
    with np.errstate(all="ignore"):
        return _o(np.log(_a(x).astype(D)).astype(F))


def log10f(x):
    """log10f: float32 helper.

    TALYS: geftalys.f:2972 ALOG10 (PEN1)
    Test: tests/hf/test_kwcov_b14b.py
    """
    with np.errstate(all="ignore"):
        return _o(np.log10(_a(x).astype(D)).astype(F))


def sinf(x):
    """sinf: float32 helper.

    TALYS: geftalys.f:2970 SIN (PEN1)
    Test: tests/hf/test_kwcov_b14b.py
    """
    return _o(np.sin(_a(x).astype(D)).astype(F))


def powf(x, y):
    """x**y with a REAL exponent: powf, y the float32 value of the Fortran literal.

    TALYS: geftalys.f / geffunctions.f x**y with a REAL exponent
    Test: tests/hf/test_kwcov_b14b.py
    """
    with np.errstate(all="ignore"):
        return _o(np.power(_a(x).astype(D), D(F(y))).astype(F))


def sqrtf(x):
    """sqrtf: float32 helper.

    TALYS: geftalys.f SQRT
    Test: tests/hf/test_kwcov_b14b.py
    """
    with np.errstate(all="ignore"):
        return _o(np.sqrt(_a(x)))


def p2(x):
    """p2: float32 helper.

    TALYS: gfortran x**2 (powi expansion)
    Test: tests/hf/test_kwcov_b14b.py
    """
    x = _a(x)
    return _o(x * x)


def p3(x):
    """p3: float32 helper.

    TALYS: gfortran x**3 = x*(x*x) (powi expansion)
    Test: tests/hf/test_kwcov_b14b.py
    """
    x = _a(x)
    return _o(x * (x * x))


def p4(x):
    """p4: float32 helper.

    TALYS: gfortran x**4 = (x*x)*(x*x) (powi expansion)
    Test: tests/hf/test_kwcov_b14b.py
    """
    x = _a(x)
    t = x * x
    return _o(t * t)


def p5(x):
    """p5: float32 helper.

    TALYS: gfortran x**5 = (x*x)*(x*(x*x)) (powi expansion; Eva Tm**5)
    Test: tests/hf/test_kwcov_b14b.py
    """
    x = _a(x)
    t = x * x
    return _o(t * (x * t))


def nint(x):
    """NINT / lroundf: round half away from zero (float32 input is exact in double).

    TALYS: geftalys.f NINT
    Test: tests/hf/test_kwcov_b14b.py
    """
    x = np.asarray(x, dtype=F).astype(D)
    with np.errstate(all="ignore"):
        r = np.where(x >= 0, np.floor(x + 0.5), -np.floor(-x + 0.5))
    r = np.nan_to_num(r, nan=0.0, posinf=1e9, neginf=-1e9)
    return _o(r.astype(np.int64))


def fint(x):
    """INT(real): truncation toward zero.

    TALYS: geftalys.f INT
    Test: tests/hf/test_kwcov_b14b.py
    """
    x = np.asarray(x, dtype=F).astype(D)
    return _o(np.nan_to_num(np.trunc(x), nan=0.0, posinf=1e9, neginf=-1e9).astype(np.int64))


def erff(x):
    """The ERF intrinsic (gfortran -> glibc erff), used by Gaussintegral (geffunctions.f declares ERF without EXTERNAL).

    TALYS: geffunctions.f:1263 (ERF intrinsic in Gaussintegral)
    Test: tests/hf/test_kwcov_b14b.py
    """
    x = np.asarray(x, dtype=D)
    v = np.vectorize(math.erf, otypes=[D])(x) if x.ndim else D(math.erf(float(x)))
    return _o(np.asarray(v).astype(F))


# ------------------------------------------------------------------------------------------------ data
@dataclass(frozen=True)
class GefData:
    """massdis.f90:263-292: beldm(203,136), ushel(203,136) indexed [N, Z] (1-based, row 0 / col 0 unused), RNucTab."""
    beldm: np.ndarray
    ushel: np.ndarray
    rnuctab: np.ndarray


@lru_cache(maxsize=2)
def load_data(talys_dir: str | None = None) -> GefData:
    """Read structure/fission/gef/{beldm,ushell,nucprop}.dat as massdis.f90 does (list-directed, transposed).

    TALYS: massdis.f90:263-292
    Test: tests/hf/test_kwcov_b14b.py
    """
    root = talys_dir or os.environ.get("TALYS_DIR") or os.path.expanduser("~/opt/talys-src")
    d = os.path.join(root, "structure", "fission", "gef")

    def grid(name):
        v = np.array(open(os.path.join(d, name)).read().split(), dtype=F)
        if v.size != 136 * 203:
            raise RuntimeError(f"GEF {name}: {v.size} values, expected {136 * 203}")
        out = np.zeros((204, 137), dtype=F)
        out[1:, 1:] = v.reshape(203, 136)  # beldm1(136,203) read column-major, beldm(i,j) = beldm1(j,i)
        return out

    rows = []
    with open(os.path.join(d, "nucprop.dat")) as fh:
        for ln in fh:
            t = ln.split()
            if len(t) < 8:
                raise RuntimeError(f"GEF nucprop.dat: short row {ln!r}")
            rows.append([float(x) for x in t[:8]])
    if len(rows) != 3885:
        raise RuntimeError(f"GEF nucprop.dat: {len(rows)} rows, expected 3885")
    return GefData(grid("beldm.dat"), grid("ushell.dat"), np.array(rows, dtype=F))


# ------------------------------------------------------------------------------------------------ GEF functions
PI_LY = F(3.14159)  # LyMass PARAMETER
SQ54PI = sqrtf(F(5.0) / (F(4.0) * PI_LY))
PI_G = F(3.14159265)  # geftalys DATA pi


def lymass(Z, A, beta):
    """Liquid-drop binding (Myers-Swiatecki Lysekil 1967), single precision.

    TALYS: geffunctions.f:268 (LyMass)
    Test: tests/hf/test_kwcov_b14b.py
    """
    Z, A, beta = _a(Z), _a(A), _a(beta)
    alpha = SQ54PI * beta
    t = (A - F(2.0) * Z) / A
    xcom = F(1.0) - F(1.7826) * (t * t)
    a2 = alpha * alpha
    with np.errstate(all="ignore"):
        xvs = -(xcom * (F(15.4941) * A - F(17.9439) * powf(A, F(2.0) / F(3.0)) * (F(1.0) + F(0.4) * a2)))
        xe = (Z * Z) * (F(0.7053) / powf(A, F(1.0) / F(3.0)) * (F(1.0) - F(0.2) * a2) - F(1.1529) / A)
    return _o(xvs + xe)


def ecoul(Z1, A1, b1, Z2, A2, b2, d):
    """Coulomb energy of two tip-to-tip deformed nuclei.

    TALYS: geffunctions.f:549 (ECOUL)
    Test: tests/hf/test_kwcov_b14b.py
    """
    Z1, A1, b1, Z2, A2, b2, d = (_a(x) for x in (Z1, A1, b1, Z2, A2, b2, d))
    n1 = A1 - Z1
    n2 = A2 - Z2
    c = F(0.6666667)
    dtot = F(1.16) * (powf(Z1 + n1, 0.3333333) * (F(1.0) + c * b1) + powf(Z2 + n2, 0.3333333) * (F(1.0) + c * b2)) + d
    return _o(Z1 * Z2 * F(1.44) / dtot)


def aypair(Z, A):
    """Pairing staggering -12/sqrt(A) x (even Z) + (even A).

    TALYS: geftalys.f:2347 (AyPair)
    Test: tests/hf/test_kwcov_b14b.py
    """
    Z, A = _a(Z), _a(A)
    with np.errstate(all="ignore"):
        ep = F(-12.0) / np.sqrt(A)
    m = (nint(Z) % 2 == 0).astype(np.int64) + (nint(A) % 2 == 0).astype(np.int64)
    return _o(ep * m.astype(F))


def _tab(t, i, j):
    i = np.clip(np.asarray(i), 0, t.shape[0] - 1)
    j = np.clip(np.asarray(j), 0, t.shape[1] - 1)
    return t[i, j]


def ushell_g(Z, A, data: GefData):
    """Shell correction (positive values x 0.3).

    TALYS: geftalys.f:2602 (Ushell)
    Test: tests/hf/test_kwcov_b14b.py
    """
    Z, A = _a(Z), _a(A)
    an = np.maximum(A - Z, F(1.0))
    res = _a(_tab(data.ushel, nint(an), nint(Z)))
    return _o(np.where(res > 0, F(0.3) * res, res).astype(F))


def aldmas0(Z, A, data: GefData):
    """BEldm table + 24/sqrt(A) - 1.433e-5 Z^2.39 (LyMass where the table is 0); beta = 0 (FEDEFOLys = 0).

    TALYS: geftalys.f:2584 (ALDMas)
    Test: tests/hf/test_kwcov_b14b.py
    """
    Z, A = _a(Z), _a(A)
    an = np.maximum(A - Z, F(1.0))
    with np.errstate(all="ignore"):
        be = (_a(_tab(data.beldm, nint(an), nint(Z))) + F(24.0) / np.sqrt(A)) - F(0.00001433) * powf(Z, 2.39)
    be = np.where(be == 0, lymass(Z, A, F(0.0)), be).astype(F)
    return _o(be)


def umass(Z, A, data: GefData):
    """Liquid drop (table) + shell.

    TALYS: geftalys.f:2617 (UMass)
    Test: tests/hf/test_kwcov_b14b.py
    """
    return _o(_a(aldmas0(Z, A, data)) + _a(ushell_g(Z, A, data)))


def tegidy(A, DU, Fred):
    """Constant-temperature T (von Egidy / Bucurescu) with shell DU, scaled by Fred.

    TALYS: geffunctions.f:225 (TEgidy)
    Test: tests/hf/test_kwcov_b14b.py
    """
    A, DU = _a(A), _a(DU)
    return _o(F(1.0) / ((F(0.0570) + F(0.00193) * DU) * powf(A, 0.6666667)) * F(Fred))


def ualev(A):
    """Level-density parameter (Ignatyuk, Bologna 2000).

    TALYS: geftalys.f:2886 (Ualev)
    Test: tests/hf/test_kwcov_b14b.py
    """
    A = _a(A)
    return _o(F(0.078) * A + F(0.115) * powf(A, 0.6666667))


class Tables:
    """Per (Z, A) float32 tables of the mass and temperature functions GEF calls with integer arguments."""

    def __init__(self, data: GefData, zmax: int = 150, amax: int = 351):
        self.data = data
        Z = np.arange(zmax + 1, dtype=F)[:, None] * np.ones((1, amax + 1), dtype=F)
        A = np.ones((zmax + 1, 1), dtype=F) * np.arange(amax + 1, dtype=F)[None, :]
        A = np.where(A == 0, F(1.0), A).astype(F)
        with np.errstate(all="ignore"):
            self.um = _a(umass(Z, A, data))
            self.ap = _a(aypair(Z, A))
            self.alev = _a(ualev(A)) * F(0.86)
            self.rshell = _a(ushell_g(Z, A, data))
            self.tct = _a(tegidy(A, self.rshell, 0.85))

    def utemp(self, iz, ia, E):
        """Temperature of the modified Gilbert-Cameron level density (KHS 2012).

        TALYS: geftalys.f:2894 (UTemp)
        Test: tests/hf/test_kwcov_b14b.py
        """
        iz = np.clip(np.asarray(iz), 0, self.um.shape[0] - 1)
        ia = np.clip(np.asarray(ia), 0, self.um.shape[1] - 1)
        E = _a(E)
        alev, rsh, tct, ap = self.alev[iz, ia], self.rshell[iz, ia], self.tct[iz, ia], self.ap[iz, ia]
        expo = np.minimum(-(F(0.055) * E), F(80.0))
        eeff0 = ((E - F(2.0)) + ap) + rsh * (F(1.0) - _a(expf(expo)))
        res = _a(tct).copy() if np.ndim(tct) else np.array(tct, dtype=F)
        m = eeff0 > F(0.5)
        if np.any(m):
            with np.errstate(all="ignore"):
                e0 = np.where(m, eeff0, F(1.0)).astype(F)
                al = np.broadcast_to(alev, e0.shape)
                e1 = e0 + F(0.1)
                ex = F(2.0) * np.sqrt(al * e0)
                ok = m & (ex < F(80.0))
                rho0 = F(1.0) / _a(powf(e0, 1.25)) * _a(expf(ex))
                rho1 = F(1.0) / _a(powf(e1, 1.25)) * _a(expf(F(2.0) * np.sqrt(al * e1)))
                tfg = F(0.1) / (_a(logf(rho1)) - _a(logf(rho0)))
            tfg = np.where(ok, tfg, F(0.0)).astype(F)
            res = np.where(tfg > res, tfg, res).astype(F)
        return _o(res)


def getyield(E_rel, E_ref, T_low, T_high):
    """Relative yield of a fission channel above / below its barrier.

    TALYS: geffunctions.f:74 (Getyield)
    Test: tests/hf/test_kwcov_b14b.py
    """
    E_rel, E_ref, T_low, T_high = F(E_rel), F(E_ref), F(T_low), F(T_high)
    exp1 = E_rel / T_low - E_ref / F(0.4)
    expo1 = E_rel / T_high - E_ref / F(0.4)
    expo2 = -E_rel / (T_high * T_low / (T_high - T_low))
    if exp1 < -50.0 or expo1 > 80.0 or expo2 > 80.0:
        y = F(0.0)
    else:
        y = F(expf(expo1) * F(1.0) / (F(1.0) + expf(expo2)))
    return F(max(y, F(0.0)))


def f1(x):
    """TALYS: geffunctions.f:112 (F1)
    Test: tests/hf/test_kwcov_b14b.py"""
    return expf(F(-9.05) + F(4.58) * logf(F(x) / F(2.3)))


def f2(x):
    """TALYS: geffunctions.f:120 (F2)
    Test: tests/hf/test_kwcov_b14b.py"""
    return expf(F(12.08) - F(3.27) * logf(F(x) / F(2.3)))


def amasscurv(Z, A, RI):
    """Curvature of the mass-asymmetric potential (Mulgin et al. 1998), kappa = 0 (INTEGER by implicit typing).

    TALYS: geftalys.f:2695 (AMasscurv)
    Test: tests/hf/test_kwcov_b14b.py
    """
    Z, A = F(Z), F(A)
    x = Z * Z / A * F(1.0) / F(1.0)
    return F(min(f1(x), f2(x)))


def desaddlescission(x):
    """Energy release saddle to scission (Asghar and Hasse), ESHIFTSASCI = -30.

    TALYS: geftalys.f:2716 (DeSaddleScission)
    Test: tests/hf/test_kwcov_b14b.py
    """
    r = F(20.0) / F(250.0) * ((F(x) - F(1300.0)) + F(-30.0)) + F(11.0)
    return F(max(r, F(0.0)))


def trusanovf(E, A):
    """TALYS: geftalys.f:2727 (TRusanovf)
    Test: tests/hf/test_kwcov_b14b.py"""
    E, A = F(E), F(A)
    return F(np.sqrt(E / (F(0.094) * A))) if E > 0 else F(0.0)


def erfc_nr(x):
    """Complementary error function (Numerical Recipes), single precision.

    TALYS: geftalys.f:2811 (Erfc)
    Test: tests/hf/test_kwcov_b14b.py
    """
    x = _a(x)
    z = np.abs(x)
    t = F(1.0) / (F(1.0) + F(0.5) * z)
    poly = F(1.48851587) + t * (F(-0.82215223) + t * F(0.17087277))
    poly = F(-1.13520398) + t * poly
    poly = F(0.27886807) + t * poly
    poly = F(-0.18628806) + t * poly
    poly = F(0.09678418) + t * poly
    poly = F(0.37409196) + t * poly
    poly = F(1.00002368) + t * poly
    r = t * _a(expf((-(z * z) - F(1.26551223)) + t * poly))
    return _o(np.where(x < 0, F(2.0) - r, r).astype(F))


def erf_nr(x):
    """TALYS: geftalys.f:2797 (Erf = 1 - Erfc)
    Test: tests/hf/test_kwcov_b14b.py"""
    return _o(F(1.0) - _a(erfc_nr(x)))


def gaussintegral(x, s):
    """0.5 + 0.5 erf(x / s) with the intrinsic ERF.

    TALYS: geffunctions.f:1254 (Gaussintegral)
    Test: tests/hf/test_kwcov_b14b.py
    """
    with np.errstate(all="ignore"):
        q = _a(x) / _a(s)
    return _o(F(0.5) + F(0.5) * _a(erff(q)))


def ftanh(x):
    """TALYS: geftalys.f:2826 (fTanh)
    Test: tests/hf/test_kwcov_b14b.py"""
    x = F(x)
    return F((expf(x) - expf(-x)) / (expf(x) + expf(-x)))


def lypair_i(Z: int, A: int):
    """TALYS: geffunctions.f:303 (LyPair, INTEGER arguments)
    Test: tests/hf/test_kwcov_b14b.py"""
    return F(-(F(12.0) / np.sqrt(F(A))) * F((Z + 1) % 2 + (A - Z + 1) % 2))


def bftfb(RZ, RA, data: GefData):
    """Outer fission barrier, Thomas-Fermi (Myers-Swiatecki) with I_Switch = 1.

    TALYS: geffunctions.f:1221 (BFTFB), 1093 (BFTF), 512 (U_SHELL_EO_exp), 440 (AME2012), 412 (LDMass)
    Test: tests/hf/test_kwcov_b14b.py
    """
    RZ, RA = F(RZ), F(RA)
    IZ, IA = int(nint(RZ)), int(nint(RA))
    RN = RA - RZ
    RI = (RN - RZ) / RA
    rk = F(1.9) + (RZ - F(80.0)) / F(75.0)
    RS = powf(RA, 0.666667) * (F(1.0) - rk * (RI * RI))
    RX = RZ * RZ / (RA * (F(1.0) - rk * (RI * RI)))
    RX0, RX1 = F(48.5428), F(34.15)
    RF = F(0.0)
    if RX < 30:
        RF = F(1.0e10)
    if RX > RX0:
        RF = F(0.0)
    if RX < RX1 and RX > 30:
        RF = F(0.595553) - F(0.124136) * (RX - RX1)
    if RX >= RX1 and RX <= RX0:
        RF = F(0.000199749) * p3(RX0 - RX)
    RB = F(RF * RS)
    if RZ > 86.5:
        RB = F(RB - F(0.15) * (RZ - F(86.5)))
    if RZ > 90:
        RB = F(RB + F(0.35) * (RZ - F(90.0)))
    if RZ > 93:
        RB = F(RB + F(0.15) * (RZ - F(93.0)))
    if RZ > 95:
        RB = F(RB - F(0.25) * (RZ - F(95.0)))
    ineu = IA - IZ
    ame = data.beldm[ineu, IZ]
    fz, fa = F(IZ), F(IA)
    ld = F((data.beldm[int(nint(fa - fz)), IZ] + F(2.0) * F(12.0) / np.sqrt(fa)) - F(0.00001433) * powf(fz, 2.39))
    if ld == 0:
        ld = lymass(fz, fa, F(0.0))
    eo = F(ame - ld)
    bf0 = F((RB - eo) + lypair_i(IZ, IA) * F(14.0) / F(12.0))
    z3a = p3(RZ) / RA
    db = F(-((F(5.40101) - F(0.00666175) * z3a) + F(1.52531e-6) * (z3a * z3a)))
    return F(bf0 + db) if db < 0 else bf0


def betaequia(A1, A2, Z1, Z2):
    """Analytical optimum deformation of the light fragment at scission (beta2opt = beta1opt, as GEF).

    TALYS: geftalys.f:2368 (BetaEquiA)
    Test: tests/hf/test_kwcov_b14b.py
    """
    A1, A2, Z1, Z2 = _a(A1), _a(A2), _a(Z1), _a(Z2)
    zsq = p2(Z1 + Z2) / _a(powf(A1 + A2, 0.333333))
    x = zsq * F(0.001) - F(1.26)
    P0 = F(0.1339)
    P1 = np.where(x < F(1.26), F(1.452), F(1.452) + F(1.8387) * (x * x)).astype(F)
    P2 = -(F(2.13) * P1)
    P3 = F(2.935) * P1
    P4 = -(F(1.753) * P1)
    zr = Z1 / (Z1 + Z2)
    return _o((((P0 + P1 * zr) + P2 * p2(zr)) + P3 * p3(zr)) + P4 * p4(zr))


def zequi(ZCN, A1, A2, beta1, beta2, d, imode: int, zucd):
    """Charge of the light fragment at the minimum of the scission-point potential (ZUCD + polarisation).

    TALYS: geftalys.f:2623 (Zequi)
    Test: tests/hf/test_kwcov_b14b.py
    """
    ZCN, A1, A2, beta1, beta2, d, zucd = (_a(x) for x in (ZCN, A1, A2, beta1, beta2, d, zucd))
    z1 = A1 / (A1 + A2) * ZCN
    z2 = ZCN - z1
    one = F(1.0)
    re1 = (_a(lymass(z1 - one, A1, beta1)) + lymass(z2 + one, A2, beta2)) + ecoul(z1 - one, A1, beta1, z2 + one, A2, beta2, d)
    re2 = (_a(lymass(z1, A1, beta1)) + lymass(z2, A2, beta2)) + ecoul(z1, A1, beta1, z2, A2, beta2, d)
    re3 = (_a(lymass(z1 + one, A1, beta1)) + lymass(z2 - one, A2, beta2)) + ecoul(z1 + one, A1, beta1, z2 - one, A2, beta2, d)
    eps2 = ((re1 - F(2.0) * re2) + re3) / F(2.0)
    eps1 = (re3 - re1) / F(2.0)
    dz = -eps1 / (F(2.0) * eps2)
    if imode > 0:
        dz = dz * F(1.0) + F(0.3)
    return _o(zucd + dz)


def ivenodd(rorigin, revenodd):
    """Integer charge / neutron number from a real one with an even-odd effect REVENODD (clamped to <= 1).

    TALYS: geftalys.f:2737 (IVENODD)
    Test: tests/hf/test_kwcov_b14b.py
    """
    ro = _a(rorigin)
    re = np.minimum(_a(revenodd), F(1.0))
    rin = ro + F(0.5)
    rfloor = fint(rin)
    rrest = rin - _a(rfloor).astype(F)
    rmid = _a(rfloor).astype(F) + F(0.5)
    even = (np.asarray(rfloor) % 2) == 0
    den = np.where(even, np.maximum(F(0.01), F(1.0) + re), np.maximum(F(0.01), F(1.0) - re)).astype(F)
    rh = rmid + (rrest - F(0.5)) * F(1.0) / den
    rh = np.minimum(rh, rmid + F(1.0))
    rh = np.maximum(rh, rmid - F(1.0))
    out = np.where(np.abs(re) < F(1.0e-3), rfloor, fint(rh))
    return _o(np.asarray(out, dtype=np.int64))


# ------------------------------------------------------------------------------------------------ random numbers
def _splitmix64(z: np.ndarray) -> np.ndarray:
    z = (z + np.uint64(0x9E3779B97F4A7C15))
    z = (z ^ (z >> np.uint64(30))) * np.uint64(0xBF58476D1CE4E5B9)
    z = (z ^ (z >> np.uint64(27))) * np.uint64(0x94D049BB133111EB)
    return z ^ (z >> np.uint64(31))


def lane_seeds(nlanes: int, offset: int = 0) -> np.ndarray:
    """Odd 48-bit starting states of the lanes: splitmix64(offset 2^32 + i), lane 0 = the stock seed 5^19 at offset 0.

    Not jump-ahead by a power of two: G^(2^k) = 1 mod 2^(k+2), so lanes 2^k draws apart are shifted copies of one
    another in their top bits (a lattice across lanes); that biased the mode / Box-Muller joint draws by 3-5 % at the
    yield peaks in a first version. Hashed seeds put the lanes at unrelated places of the 2^46 cycle.

    TALYS: (none -- the port's lane layout of geftalys.f:3108 setijk)
    Test: tests/hf/test_kwcov_b14b.py
    """
    with np.errstate(over="ignore"):
        idx = np.arange(nlanes, dtype=np.uint64) + np.uint64((int(offset) & 0xFFFFFFFF) << 32)
        x = (_splitmix64(idx) & np.uint64(M48)) | np.uint64(1)
    if offset == 0 and nlanes:
        x[0] = SEED
    return x


class GefStream:
    """The MCNP 48-bit generator of geftalys.f per lane, with PGauss's cached Gaussian per lane.

    TALYS: geftalys.f:3075 (rndm), 3108 (setijk, setran), 3135 (ran2), 2849 (PGauss DATA Iset/1/, GSet/0.5/)
    Test: tests/hf/test_kwcov_b14b.py
    """

    def __init__(self, mode: str = "lanes", seed_offset: int = 0):
        if mode not in ("lanes", "talys"):
            raise ValueError(f"GEF stream mode {mode!r}: 'lanes' or 'talys'")
        self.mode = mode
        self.seed_offset = int(seed_offset)
        self.x = np.zeros(1, dtype=np.uint64)
        # the PGauss SAVE state of the program (talys mode carries it across calls)
        self.iset = np.ones(1, dtype=bool)
        self.gset = np.full(1, F(0.5), dtype=F)
        self.ndraw = 0

    def reset(self, nlanes: int) -> None:
        """geftalys.f:72-75 at every call: nrand = 0, setijk(5^19), setran. Lanes: lane_seeds."""
        if self.mode == "talys":
            self.x = np.array([SEED], dtype=np.uint64)
            return
        self.x = lane_seeds(nlanes, self.seed_offset)
        self.iset = np.zeros(nlanes, dtype=bool)
        self.gset = np.zeros(nlanes, dtype=F)

    def rndm(self, lid: np.ndarray) -> np.ndarray:
        """rndm = sngl(ran2()); ran2 advances X <- G X mod 2^48 and returns X / 2^48."""
        x = (self.x[lid] * np.uint64(GMUL)) & np.uint64(M48)
        self.x[lid] = x
        self.ndraw += lid.size
        return (x.astype(D) * D(2.0 ** -48)).astype(F)

    def pgauss(self, lid: np.ndarray, mean, sigma) -> np.ndarray:
        """PGauss(AMean, Sigma): polar Box-Muller, second value cached per lane (SAVE).

        TALYS: geftalys.f:2849 (PGauss)
        """
        gas = np.empty(lid.size, dtype=F)
        cached = self.iset[lid]
        if np.any(cached):
            c = lid[cached]
            gas[cached] = self.gset[c]
            self.iset[c] = False
        new = ~cached
        if np.any(new):
            pos = np.nonzero(new)[0]
            v1 = np.empty(pos.size, dtype=F)
            v2 = np.empty(pos.size, dtype=F)
            r = np.empty(pos.size, dtype=F)
            todo = np.arange(pos.size)
            while todo.size:
                ll = lid[pos[todo]]
                a = F(2.0) * self.rndm(ll) - F(1.0)
                b = F(2.0) * self.rndm(ll) - F(1.0)
                rr = a * a + b * b
                v1[todo], v2[todo], r[todo] = a, b, rr
                todo = todo[rr >= F(1.0)]
            with np.errstate(all="ignore"):
                fac = np.sqrt(F(-2.0) * _a(logf(r)) / r)
            ln = lid[pos]
            self.gset[ln] = v1 * fac
            self.iset[ln] = True
            gas[pos] = v2 * fac
        return (_a(mean) + _a(sigma) * gas).astype(F)

    def plingauss(self, lid: np.ndarray, rsigma) -> np.ndarray:
        """PLinGauss: |PGauss(0, Brms)| + |PGauss(0, Brms)| + shape correction.

        TALYS: geftalys.f:2873 (PLinGauss)
        """
        rsigma = _a(rsigma)
        brms = rsigma / np.sqrt(F(2.0))
        rres = np.abs(self.pgauss(lid, F(0.0), brms))
        rres = rres + np.abs(self.pgauss(lid, F(0.0), brms))
        with np.errstate(all="ignore"):
            corr = brms / F(4.0) * (F(1.0) - _a(expf(-rres / rsigma)))
        return np.where(rsigma > F(0.0), rres + corr, rres).astype(F)


# ------------------------------------------------------------------------------------------------ setup
@dataclass
class CallSetup:
    """Energy-independent part of geftalys.f (lines 160-650)."""
    ZCN: np.float32
    ACN: np.float32
    nZ: int
    nA: int
    RNCN: np.float32
    DeltaS0: np.float32
    beta: np.ndarray  # (6, 3, 151)
    edefo: np.ndarray  # (4, 3, 151)
    zshift: np.ndarray  # (4, 3, 351)
    A1s: np.float32  # the stale A1 of the last deformation loop
    ZCMode: list
    ACMode: list
    RZCurvS0: np.float32
    RACurvS0: np.float32
    RPolCurvS0: np.float32
    SpinCN: np.float32
    um_cn: np.float32
    ap_cn: np.float32
    dss: np.float32


_DELTAS0 = {(95, 242): -0.1, (95, 244): -0.1, (96, 244): 0.1, (93, 238): 0.2, (94, 240): -0.1, (94, 241): -0.35,
            (94, 243): -0.3, (90, 228): 0.65, (90, 230): 0.65, (90, 233): -0.2, (92, 233): 0.65, (92, 234): 0.5,
            (92, 235): 0.35, (92, 236): 0.3}


def call_setup(ZCN, ACN, data: GefData, tab: Tables) -> CallSetup:
    """Deformations, deformation energies, charge polarisation, fission-channel positions and curvatures.

    TALYS: geftalys.f:160-650 (energy-independent part of geftalys)
    Test: tests/hf/test_kwcov_b14b.py
    """
    ZCN, ACN = F(ZCN), F(ACN)
    nZ, nA = int(nint(ZCN)), int(nint(ACN))
    RNCN = F(ACN - ZCN)
    DeltaS0 = F(_DELTAS0.get((nZ, nA), 0.0))
    dneck = F(3.0)
    beta = np.zeros((6, 3, 151), dtype=F)
    edefo = np.zeros((4, 3, 151), dtype=F)
    I = np.arange(10, nZ - 10 + 1)
    Z1 = I.astype(F)
    # mode 0: liquid drop (BetaEquiA)
    A1 = Z1 / ZCN * ACN
    A2 = ACN - A1
    Z2 = ZCN - Z1
    b = _a(betaequia(A1, A2, Z1, Z2))
    beta[0, 1, I] = b
    beta[0, 2, I] = b
    e1 = _a(lymass(Z1, A1, b)) - _a(lymass(Z1, A1, F(0.0)))
    edefo[0, 1, I] = e1
    edefo[0, 2, I] = e1
    # mode 1: deformed light, spherical heavy
    A1 = (Z1 - F(0.0)) / ZCN * ACN
    rb = (Z1 - F(26.6)) * F(0.80) / F(20.0)
    beta[1, 1, I] = rb
    edefo[1, 1, I] = _a(lymass(Z1, A1, rb)) - _a(lymass(Z1, A1, F(0.0)))
    beta[1, 2, I] = F(0.0)
    edefo[1, 2, I] = F(0.0)
    # modes 2 and 3: deformed shells in both
    for m in (2, 3):
        A1 = (Z1 - F(0.5)) / ZCN * ACN
        rb = (Z1 - F(26.6)) * F(0.80) / F(20.0)
        beta[m, 1, I] = rb
        edefo[m, 1, I] = _a(lymass(Z1, A1, rb)) - _a(lymass(Z1, A1, F(0.0)))
        rb = (Z1 - F(48.0)) * F(0.70) / F(20.0)
        beta[m, 2, I] = rb
        A1 = (Z1 + F(0.5)) / ZCN * ACN
        edefo[m, 2, I] = _a(lymass(Z1, A1, rb)) - _a(lymass(Z1, A1, F(0.0)))
    A1s = F((F(nZ - 10) + F(0.5)) / ZCN * ACN)
    beta[4, 1, I] = np.maximum(beta[1, 2, I], F(0.0))
    beta[4, 2, I] = beta[4, 1, I]
    beta[5, 1, I] = np.maximum(beta[2, 2, I], F(0.0))
    beta[5, 2, I] = beta[5, 1, I]
    # mean Z as a function of mass (modes 0-3)
    zshift = np.zeros((4, 3, 351), dtype=F)
    IA = np.arange(10, nA - 10 + 1)
    fI = IA.astype(F)
    zucd = fI / ACN * ZCN
    for m in range(4):
        if m == 1:
            beta1 = beta[1, 1, np.clip(nint(zucd + F(0.0)), 0, 150)]
            beta2 = beta[1, 2, np.clip(nint(ZCN - (zucd - F(0.0))), 0, 150)]
        else:
            beta1 = beta[m, 1, np.clip(nint(zucd), 0, 150)]
            beta2 = beta[m, 2, np.clip(nint(ZCN - zucd), 0, 150)]
        z1 = _a(zequi(ZCN, fI, ACN - fI, beta1, beta2, dneck, m, zucd))
        if m == 1:
            z1 = z1 + F(0.0)
            z1 = np.where(ZCN - z1 < F(50.0), ZCN - F(50.0), z1).astype(F)
        k = nint(ACN - fI)
        zshift[m, 1, IA] = z1 - zucd
        zshift[m, 2, k] = zucd - z1
    # central Z of the fission channels (Boeckstiegel et al. 2008)
    zc13 = powf(ZCN, 1.3) / ACN - F(1.50)
    ZC1 = F((F(52.9) - F(51.5)) / (F(1.56) - F(1.50)) * zc13 + F(51.5) + F(-0.1))
    ZC2 = F((F(55.8) - F(54.5)) / (F(1.56) - F(1.50)) * zc13 + F(54.5) + F(-0.45))
    ZC3 = F(ZC2 + F(4.5) + F(0.0))
    ZC0 = F(ZCN * F(0.5))
    ZCMode = [ZC0, ZC1, ZC2, ZC3]
    ACMode = []
    for m, zc in enumerate(ZCMode):  # geftalys.f:1012-1044 (second iteration; mode 3 truncates with INT)
        rzpol = F(0.0)
        for _ in range(3):
            ra = F((zc - rzpol) * ACN / ZCN)
            rzpol = zshift[m, 2, int(fint(ra)) if m == 3 else int(nint(ra))]
        ACMode.append(F((zc - rzpol) * ACN / ZCN))
    RI = F((RNCN - ZCN) / ACN)
    am = amasscurv(ZCN, ACN, RI)
    RZCurvS0 = F(F(8.0) / p2(ZCN) * am)
    RACurvS0 = F(F(8.0) / p2(ACN) * am)
    # stiffness in polarisation (geftalys.f:907-921)
    RZ, RA = F(ZCN * F(0.5)), F(ACN * F(0.5))
    b1 = beta[0, 1, int(nint(RZ + F(0.5)))]
    b2 = beta[0, 2, int(nint(RZ + F(0.5)))]
    one = F(1.0)
    s = F(lymass(RZ - one, RA, b1))
    s = F(s + lymass(RZ + one, RA, b2))
    s = F(s + lymass(RZ + one, RA, b1))
    s = F(s + lymass(RZ - one, RA, b2))
    s = F(s + ecoul(RZ - one, RA, b1, RZ + one, RA, b2, dneck))
    s = F(s + ecoul(RZ + one, RA, b1, RZ - one, RA, b2, dneck))
    s = F(s - F(2.0) * ecoul(RZ, RA, b1, RZ, RA, b2, dneck))
    s = F(s - F(2.0) * lymass(RZ, RA, b1))
    s = F(s - F(2.0) * lymass(RZ, RA, b2))
    RPolCurvS0 = F(s * F(0.5))
    # CN spin (IMATENDF: first row with Z, A; the last row if none)
    zt, at = int(fint(ZCN)), int(fint(ACN))
    rows = np.nonzero((nint(data.rnuctab[:, 1]) == zt) & (nint(data.rnuctab[:, 2]) == at))[0]
    imat = int(rows[0]) if rows.size else data.rnuctab.shape[0] - 1
    SpinCN = F(data.rnuctab[imat, 4])
    dss = desaddlescission(F(p2(ZCN) / powf(ACN, 0.33333)))
    return CallSetup(ZCN, ACN, nZ, nA, RNCN, DeltaS0, beta, edefo, zshift, A1s, ZCMode, ACMode, RZCurvS0, RACurvS0,
                     RPolCurvS0, SpinCN, F(umass(ZCN, ACN, data)), F(aypair(ZCN, ACN)), dss)


@dataclass
class BinSetup:
    """Energy-dependent part of geftalys.f (lines 730-1516) for one excitation energy."""
    Eex: np.float32
    yields: np.ndarray  # (6,) normalised: 0, 1, 2, 3, 11, 22
    sigA: np.ndarray  # (6,)
    sigZ2: np.float32
    sigpol: np.ndarray  # (4,)
    epart: np.ndarray  # (6, 3, 351)
    peoz: np.ndarray
    peon: np.ndarray
    spin: np.ndarray  # (6, 3, 201, 151) SpinRMSNZ[mode, k, N, Z]
    ecollsaddle: np.ndarray  # (6,)
    etunn: np.float32
    rexc_gs: np.float32 = np.float32(0.0)


def bin_setup(cs: CallSetup, excit, tab: Tables, data: GefData, epart_prev=None, peo_prev=None,
              spin_prev=None) -> BinSetup:
    """Barriers and yields of the fission channels, widths, even-odd effects, energy sorting, fragment spins.

    TALYS: geftalys.f:730-1516
    Test: tests/hf/test_kwcov_b14b.py
    """
    ZCN, ACN, RNCN, nZ, nA = cs.ZCN, cs.ACN, cs.RNCN, cs.nZ, cs.nA
    ZC0, ZC1, ZC2, ZC3 = cs.ZCMode
    REexcGS = F(excit)
    Eex = F(REexcGS - bftfb(ZCN, ACN, data))
    S0p = Eex
    dnpol = F(F(82.0) - F(50.0) / ZCN * RNCN)
    rs1 = F(F(-2.8) * (F(1.0) - F(0.055) * abs(dnpol)))
    s1e = F(F(-0.5) + p2(ZCN - F(50.0) - F(44.85)) * F(0.1))
    if s1e > 0:
        s1e = F(0.0)
    rs1 = F(rs1 + s1e)
    rs3 = F(F(-5.8) * (F(1.0) - F(0.005) * p2(ZCN - F(60.5) - F(37.0))))
    rs3 = F(min(rs3, F(0.0)))
    q = ACN / ZCN
    eld1 = F(cs.RACurvS0 * p2(q * (ZC1 - ZC0)))
    bs1 = F(eld1 + rs1)
    eld2 = F(cs.RACurvS0 * p2(q * (ZC2 - ZC0)))
    bs2 = F(eld2 + F(-4.0))
    eld3 = F(cs.RACurvS0 * p2(q * (ZC3 - ZC0)))
    bs3 = F(eld3 + rs3)
    bs11 = F(F(2.0) * (rs1 + F(0.75) * p2(ZC1 - ZC0)))
    if bs11 > rs1 and bs11 < rs1 + F(7.0):
        bs11 = F(min(bs11, rs1))
    des11 = F(min(F(0.0), -(F(0.2) * (F(2.0) * abs(ZC1 - ZC0)))))
    bs11 = F(bs11 + des11)
    bs22 = F(F(2.0) * (eld2 + F(-4.0)) + F(2.0) * F(0.5) * p2(ZC2 - ZC0))
    emin = F(0.0)
    for v in (bs1, bs2, bs3, bs11, bs22):
        emin = F(min(emin, v))
    E0 = F(F(S0p + emin) - cs.DeltaS0)
    E1 = F(F(S0p - bs1) + emin)
    E2 = F(F(S0p - bs2) + emin)
    E3 = F(F(S0p - bs3) + emin)
    E11 = F(F(S0p - bs11) + emin)
    E22 = F(F(S0p - bs22) + emin)
    etunn = F(-E0) if E0 < 0 else F(0.0)
    reff = F(max(F(0.1), E0))
    dss = cs.dss
    tc0 = F(max(F(F(0.13) * F(dss - etunn)), F(0.0)))
    tc0 = F(max(tc0, trusanovf(reff, ACN)))
    tpol0 = F(F(0.01) * tc0)
    tas0 = F(np.sqrt(p2(tc0) + p2(F(0.12))))
    epot = F(dss - etunn)
    eeffs2 = F(F(F(max(E2, F(0.0))) + F(0.3) * epot) - F(2.3))
    eeffs2 = F(max(F(0.0), eeffs2))
    if eeffs2 < F(0.5) + F(2.0) * F(0.3):
        E1 = F(E1 - F(F(F(0.5) * F(4.0)) * F(12.0)) / np.sqrt(F(132.0)) * gaussintegral(F(0.5) - eeffs2, F(0.3)))
    tcm, tpol, tas = [tc0], [tpol0], [tas0]
    for e in (E1, E2, E3):
        tc = F(max(F(F(0.1) * e + F(0.13) * F(dss - etunn)), F(0.0)))
        tcm.append(tc)
        tpol.append(F(F(0.01) * tc))
        tas.append(F(np.sqrt(p2(tc) + p2(F(0.12)))))
    rpol = cs.RPolCurvS0
    hom = F(2.0)

    def sigpol(m):
        expo = F(hom / (F(2.0) * tpol[m]))
        if tcm[m] > F(1.0e-2) and abs(expo) < 80.0:
            return F(np.sqrt(F(F(F(0.25) * hom) / rpol) / ftanh(expo)))
        return F(np.sqrt(F(F(0.25) * hom) / rpol))

    ap_cn = cs.ap_cn
    sigz = [F(np.sqrt(F(F(0.5) * tas0) / cs.RZCurvS0))]
    for m, (e, pz) in enumerate(((E1, F(0.75)), (E2, F(0.5)), (E3, F(0.22))), start=1):
        rei = F(max(F(F(e + ap_cn) + F(-3.0)), F(0.0)))
        att = expf(-rei / F(18.5))
        sigz.append(F(np.sqrt(F(F(0.5) * tas[m]) / F(pz * att))))
    sp = np.array([sigpol(m) for m in range(4)], dtype=F)
    teg = lambda du: tegidy(ACN, du, 0.8)  # noqa: E731
    y0 = F(max(getyield(E0, E0, F(0.31), teg(F(0.0))), F(0.0)))
    y1 = F(max(getyield(E1, E0, F(0.30), teg(F(rs1 + F(-3.0)))), F(0.0)))
    y2 = F(max(getyield(E2, E0, F(0.31), teg(F(F(-4.0) + F(0.0)))), F(0.0)))
    y3 = F(max(getyield(E3, E0, F(0.32), teg(F(F(-5.8) + F(0.0)))), F(0.0)))  # PShellS3, not RShellS3eff
    y11 = F(0.0) if bs11 > 0 else getyield(E11, E0, F(0.36), teg(F(rs1 + F(2.0) * F(-3.0))))
    y22 = F(0.0) if bs22 > 0 else getyield(E22, E0, F(0.31), teg(F(-4.0)))
    yn = F(F(F(F(F(y0 + y1) + y2) + y3) + y11) + y22)
    yields = np.array([y0, y1, y2, y3, y11, y22], dtype=F) / yn
    sigA = np.array([sigz[0] * ACN / ZCN, sigz[1] * ACN / ZCN, sigz[2] * ACN / ZCN, sigz[3] * ACN / ZCN,
                     F(sigz[1] * np.sqrt(F(2.0))) * ACN / ZCN, F(sigz[2] * np.sqrt(F(2.0))) * ACN / ZCN], dtype=F)
    # shells and fragment temperatures at scission (Temp(mode, k, A))
    ias = np.arange(1, nA).astype(F)
    temp = np.zeros((4, 3, 351), dtype=F)
    t00 = _a(tegidy(ias, F(0.0), 0.8))
    for m in range(4):
        temp[m, 1, 1:nA] = t00
        temp[m, 2, 1:nA] = t00
    du1 = F(min(F(rs1 + F(-3.0)), F(0.0)))
    temp[1, 2, 1:nA] = _a(tegidy(ias, du1, 0.8))
    # even-odd effects and energy sorting per mode (geftalys.f:1235-1385, sequential: modes 4/5 rewrite in loop order)
    epart = np.zeros((6, 3, 351), dtype=F) if epart_prev is None else epart_prev
    peoz, peon = (np.zeros((6, 3, 351), dtype=F), np.zeros((6, 3, 351), dtype=F)) if peo_prev is None else peo_prev
    ecs = np.zeros(6, dtype=F)
    zeven = nZ % 2 == 0
    neven = int(nint(RNCN)) % 2 == 0
    for m, et in enumerate((E0, E1, E2, E3, E11, E22)):
        et = F(et)
        if (nZ % 2 + int(nint(RNCN)) % 2) == 0 and et > 0 and et < F(F(2.0) * F(12.0)) / np.sqrt(ACN):
            ecs[m] = et
            et = F(0.0)
        et = F(max(et, F(0.0)))
        et = F(et + F(0.3) * epot)
        expo = F(et / F(2.25))
        r1p = expf(-expo) if (zeven and abs(expo) < 80.0) else F(0.0)
        expo = F(et / F(0.5))
        r1n = expf(-expo) if (neven and abs(expo) < 80.0) else F(0.0)
        ia1 = np.arange(40, nA - 40 + 1)
        ia2 = nA - ia1
        if m <= 3:
            t1, t2 = temp[m, 1, ia1], temp[m, 2, ia2]
        else:
            k = 1 if m == 4 else 2
            t1, t2 = temp[k, 2, ia1], temp[k, 2, ia2]
        dt = np.abs(t2 - t1)
        r2 = _a(gaussintegral(dt / et - F(0.04), F(0.35) * (dt + F(0.0001))))
        r2p = (F(0.40) - r1p) * r2
        r2n = (F(0.40) - r1n) * r2
        with np.errstate(all="ignore"):
            e1es = np.minimum(F(0.1) * t1 * t2 / np.abs(t1 - t2), F(0.5) * et)
        e1fg = F(et * cs.A1s / ACN)
        if et < 13:
            e1 = e1es
        elif et <= 20:
            e1 = e1es + (et - F(13.0)) / F(7.0) * (e1fg - e1es)
        else:
            e1 = np.full_like(e1es, e1fg)
        e1 = np.where(np.abs(t1 - t2) < F(1.0e-6), F(0.5) * et, e1).astype(F)
        e2 = et - e1
        for j in range(ia1.size):
            a1, a2 = int(ia1[j]), int(ia2[j])
            if m <= 3:
                peoz[m, 1, a1] = r1p
                peoz[m, 2, a2] = r1p
                peon[m, 1, a1] = r1n
                peon[m, 2, a2] = r1n
            else:
                peoz[m, 2, a1] = r1p
                peoz[m, 2, a2] = r1p
                peon[m, 2, a1] = r1n
                peon[m, 2, a2] = r1n
            peoz[m, 1, a1] = F(peoz[m, 1, a1] + r2p[j])
            peoz[m, 2, a2] = F(peoz[m, 2, a2] + r2p[j]) if zeven else F(peoz[m, 2, a2] - r2p[j])
            peon[m, 1, a1] = F(peon[m, 1, a1] + r2n[j])
            peon[m, 2, a2] = F(peon[m, 2, a2] + r2n[j]) if neven else F(peon[m, 2, a2] - r2n[j])
            epart[m, 1, a1] = e1[j]
            epart[m, 2, a2] = e2[j]
    # RMS spins of the fragments (geftalys.f:1422-1516)
    spin = np.zeros((6, 3, 201, 151), dtype=F) if spin_prev is None else spin_prev
    iz1 = np.arange(20, nZ - 20 + 1)
    aucd = nint(iz1.astype(F) * ACN / ZCN)
    IZ = np.repeat(iz1, 31)
    IA = (np.repeat(aucd, 31) + np.tile(np.arange(-15, 16), iz1.size)).astype(np.int64)
    fA = IA.astype(F)
    irs = F(F(1.16) * F(1.16)) * _a(powf(fA, 1.6667)) / F(103.8415)
    sq = np.sqrt(F(4.0) * PI_G / F(5.0))
    odd = (IZ % 2) == 1
    third = F(1.0) / F(3.0)
    for m in range(6):
        for k in (1, 2):
            alph = cs.beta[m, k, IZ] / sq
            irig = irs * ((F(1.0) + F(0.5) * alph) + F(9.0) / F(7.0) * (alph * alph))
            ee = epart[m, k, IA]
            ee = np.where(ee < 0, F(0.0), ee).astype(F)
            t = _a(tab.utemp(IZ, IA, ee))
            t = np.sqrt(t * t + F(0.8) * F(0.8))
            ieff = irig * (F(1.0) - F(0.8) * _a(expf(-(F(0.693) * ee) / F(5.0))))
            j = np.sqrt(F(2.0) * ieff * t)
            j = np.sqrt(j * j + third * (cs.SpinCN * cs.SpinCN))
            if k == 1:
                add = F(0.4) * _a(powf(fA / F(140.0), 0.66667))
            else:
                add = np.full(IA.shape, F(0.4) * powf(cs.A1s / F(140.0), 0.66667), dtype=F)
            j = np.where(odd, j + add, j).astype(F)
            spin[m, k, IA - IZ, IZ] = j * F(1.0)
    return BinSetup(Eex, yields, sigA, sigz[2], sp, epart, peoz, peon, spin, ecs, etunn)


# ------------------------------------------------------------------------------------------------ event loop
@dataclass
class BinTally:
    apre: np.ndarray
    apost: np.ndarray
    cnt_pre: np.ndarray  # yAZ_temp counts (351, 151)
    cnt_post: np.ndarray
    an2pre: np.ndarray  # (351, 21)
    an2post: np.ndarray
    ann: np.ndarray  # (51,)
    anpre: np.ndarray  # ANPRE by N (Racc), detail output only
    anpost: np.ndarray
    tke_fix: int = 0


def _pen1(st: GefStream, lid, td, tct, ed, ad):
    """PEN1: neutron energy from a Maxwellian with FG correction and optical-model inverse cross section (rejection).

    TALYS: geftalys.f:2936 (PEN1)
    """
    out = np.empty(lid.size, dtype=F)
    todo = np.arange(lid.size)
    pw_ad = _a(powf(ad, 0.6666667))
    while todo.size:
        ll = lid[todo]
        r1 = st.rndm(ll)
        r2 = st.rndm(ll)
        T, Ed = td[todo], ed[todo]
        e = -T * (_a(logf(r1)) + _a(logf(r2)))
        need = (e < Ed) & (Ed > F(6.0))
        keep = np.ones(todo.size, dtype=bool)
        if np.any(need):
            ni = np.nonzero(need)[0]
            en, edn, tn, tctn = e[ni], Ed[ni], T[ni], tct[todo][ni]
            efin = edn - en
            with np.errstate(all="ignore"):
                fa = _a(expf(F(2.0) / tn * np.sqrt(edn * efin) + (en - F(2.0) * edn) / tn))
                fb = _a(expf(F(2.0) * np.sqrt(edn * F(6.0)) / tn - (F(6.0) - efin) / tctn + (en - F(2.0) * edn) / tn))
            fred = np.where(efin > F(6.0), fa, fb).astype(F)
            r3 = st.rndm(lid[todo[ni]])
            keep[ni[r3 > fred]] = False
        ki = np.nonzero(keep)[0]
        if ki.size:
            x = e[ki] / pw_ad[todo[ki]]
            with np.errstate(all="ignore"):
                xp = _a(powf(x, -0.14))
                y_lo = F(155.0) * xp + F(15.0) * xp * _a(sinf((F(3.0) * _a(powf(x, 0.14)) + F(0.06)) / F(0.115) - F(4.3)))
                y_hi = F(290.0) * _a(expf(-_a(log10f(x)) / log10f(F(6.0))))
            y = np.where(x < F(4.5), y_lo, y_hi).astype(F)
            r4 = F(400.0) * st.rndm(lid[todo[ki]])
            acc = ~(r4 > y)
            out[todo[ki[acc]]] = e[ki[acc]]
            keep[ki[~acc]] = False
        todo = todo[~keep]
    return out


def _pegammahigh(st: GefStream, lid, zi, ai, ei, tab: Tables):
    """PEgammahigh: gamma energy from a GDR-tail x level-density distribution on a 100 keV grid (rejection).

    TALYS: geftalys.f:2983 (PEgammahigh), 3034 (E0GDR), 3057 (WidthGDR)
    """
    n = np.minimum(nint(ei * F(10.0)), 5000)
    n = np.where(n <= 0, 1, n)
    e0 = F(18.0) / _a(powf(ai, 0.333333)) + F(25.0) / _a(powf(ai, 0.1666667))
    g0 = F(1.99) * _a(powf(e0 / F(10.0), 1.6))
    tm = _a(tab.utemp(nint(zi), nint(ai), ei))
    mmax = int(max(int(n.max()) - 1, 1))
    M = np.arange(1, mmax + 1)
    eg = (F(0.1) * M.astype(F))[None, :]

    def sig(eg, tm, e0, g0):
        with np.errstate(all="ignore"):
            return (p3(eg) / p2(tm) * _a(expf(-(eg / tm))) * (g0 * eg)
                    / (p2(eg * eg - e0 * e0) + (g0 * g0) * (e0 * e0))).astype(F)

    s = _a(sig(eg, tm[:, None], e0[:, None], g0[:, None]))
    valid = (M[None, :] <= np.maximum(n - 1, 1)[:, None])
    smax = np.where(valid, s, F(0.0)).max(axis=1).astype(F)
    out = np.empty(lid.size, dtype=F)
    todo = np.arange(lid.size)
    while todo.size:
        ll = lid[todo]
        xr = np.maximum(st.rndm(ll) * ei[todo] * F(10.0), F(1.0)).astype(F)
        m = np.minimum(nint(xr), n[todo])
        yr = st.rndm(ll) * smax[todo]
        inside = (m <= np.maximum(n[todo] - 1, 1))
        sm = np.where(inside, s[todo, np.clip(m - 1, 0, mmax - 1)], F(0.0)).astype(F)
        acc = ~(yr > sm)
        out[todo[acc]] = xr[acc] / F(10.0)
        todo = todo[~acc]
    return out


def _eva(st: GefStream, lid, iz0, ia0, einit, tab: Tables):
    """Eva: neutron evaporation with gamma competition from one fragment; returns (Z, A) after the cascade.

    TALYS: geftalys.f:2409 (Eva)
    """
    um, ap = tab.um, tab.ap
    n = lid.size
    zi = iz0.astype(F)
    ai = ia0.astype(F)
    ei = einit.astype(F).copy()

    def sep(z, a):
        iz, ia = nint(z), nint(a)
        return ((um[iz, ia - 1] + ap[iz, ia - 1]) - (um[iz, ia] + ap[iz, ia])).astype(F)

    sneff = sep(zi, ai)
    act = np.arange(n)
    while act.size:
        L = lid[act]
        Z, A, E, S = zi[act], ai[act], ei[act], sneff[act]
        izn, ian = nint(Z), nint(A)
        tm = _a(tab.utemp(izn, ian, E))
        td = _a(tab.utemp(izn, ian, E - S))
        with np.errstate(all="ignore"):
            gg = F(0.624) * _a(powf(A, 1.6)) / _a(p5(tm))
            gg = gg * F(1.0e-9)
            tmean = (tm + td) / F(2.0)
            gn = _a(powf(A - F(1.0), 0.66667)) * F(0.13) * (td * td) / _a(expf(S / tmean))
        low = (E - S) < np.abs(ap[izn, nint(A - F(1.0))])
        zev = (nint(Z) % 2) == 0
        nev = (nint(A - Z - F(1.0)) % 2) == 0
        gn = np.where(low & (zev | nev), F(0.1) * gn, gn).astype(F)
        gn = np.where(low & zev & nev, F(0.1) * gn, gn).astype(F)
        with np.errstate(all="ignore"):
            pg = gg / (gg + gn)
        pg = F(0.3) * pg
        rg = st.rndm(L)
        gam = rg < pg
        if np.any(gam):
            gi = np.nonzero(gam)[0]
            eg = _pegammahigh(st, L[gi], Z[gi], A[gi], E[gi], tab)
            E[gi] = E[gi] - eg
            ei[act[gi]] = E[gi]
        stop = (E - S) <= F(0.0)
        cont = np.nonzero(~stop)[0]
        # neutron: up to 99 tries of PEN1 with Ekin <= E - Sn
        ekin = np.full(cont.size, F(np.nan), dtype=F)
        tries = np.arange(cont.size)
        itry = 0
        while tries.size:
            itry += 1
            if itry >= 100:
                break
            c = cont[tries]
            zc, ac, ec, sc = Z[c], A[c], E[c], S[c]
            tdc = _a(tab.utemp(nint(zc), nint(ac - F(1.0)), ec - sc))
            tct = _a(tegidy(ac - F(1.0), F(0.0), 0.85))
            ek = _pen1(st, L[c], tdc, tct, ec - sc, ac - F(1.0))
            ok = ~(ek > ec - sc)
            ekin[tries[ok]] = ek[ok]
            tries = tries[~ok]
        emitted = ~np.isnan(ekin)
        ce = cont[emitted]
        if ce.size:
            g = act[ce]
            af = A[ce] - F(1.0)
            ef = E[ce] - ekin[emitted] - S[ce]
            ai[g] = af
            ei[g] = ef
            sneff[g] = sep(Z[ce], af)
        nxt = act[ce]
        nxt = nxt[(ei[nxt] - sneff[nxt]) > F(0.0)]
        act = nxt
    return zi, ai


def run_events(cs: CallSetup, bs: BinSetup, nevt: int, st: GefStream, tab: Tables, lanes: np.ndarray,
               tally: BinTally) -> None:
    """One batch of events (one per lane, in lane order), accumulated into `tally` (geftalys.f:1608-2193).

    TALYS: geftalys.f:1608-2193 (event loop)
    Test: tests/hf/test_kwcov_b14b.py
    """
    ZCN, ACN, RNCN = cs.ZCN, cs.ACN, cs.RNCN
    racc = F(F(1.0) / F(nevt))
    n = lanes.size
    lid = lanes
    y = bs.yields
    rs = np.cumsum(y.astype(F), dtype=F)
    rch = st.rndm(lid)
    imode = np.full(n, 5, dtype=np.int64)
    imode[rch < rs[0]] = 0
    for m in range(1, 6):
        imode[(rch >= rs[m - 1]) & (rch < rs[m])] = m
    ra = np.zeros(n, dtype=F)
    rz = np.zeros(n, dtype=F)
    half = F(0.5) * ACN
    for m in (0, 1, 2, 3, 4, 5):
        sel = np.nonzero(imode == m)[0]
        if not sel.size:
            continue
        ll = lid[sel]
        if m in (0, 4, 5):
            sa = bs.sigA[0] if m == 0 else bs.sigA[m]
            rah = st.pgauss(ll, cs.ACMode[0], sa)
            rah_ = np.where(rah > half, rah, ACN - rah).astype(F)
            if m == 0:
                rzpol = cs.zshift[0, 2, np.clip(nint(rah_), 0, 350)]
                rzc = rah_ * ZCN / ACN + rzpol
            else:
                rzc = rah_ * ZCN / ACN
            ra[sel] = rah_
            rz[sel] = st.pgauss(ll, rzc, bs.sigpol[0])
        elif m in (1, 3):
            rah = st.pgauss(ll, cs.ACMode[m], bs.sigA[m])
            rzpol = cs.zshift[m, 2, np.clip(nint(rah), 0, 350)]
            ra[sel] = rah
            rz[sel] = st.pgauss(ll, rah * ZCN / ACN + rzpol, bs.sigpol[m])
        else:
            todo = np.arange(sel.size)
            while todo.size:
                l2 = ll[todo]
                st.pgauss(l2, cs.ACMode[2], bs.sigA[2])
                rah = st.pgauss(l2, cs.ACMode[2], bs.sigA[2])
                rah = rah + (st.rndm(l2) - F(0.5)) * F(14.0)
                rah = np.maximum(rah, F(1.0)).astype(F)
                rzpol = cs.zshift[2, 2, np.clip(nint(rah), 0, 350)]
                rzc = rah * ZCN / ACN + rzpol
                rt = st.rndm(l2)
                g1 = F(0.5) * _a(erf_nr((rzc - F(50.0)) / (F(1.0) * bs.sigZ2))) + F(0.5)
                g2 = F(0.5) * _a(erf_nr((ZCN - rzc - F(30.5)) / (F(0.56) * bs.sigZ2))) + F(0.5)
                rej = (rt > g1) | (rt > g2)
                acc = np.nonzero(~rej)[0]
                if acc.size:
                    ra[sel[todo[acc]]] = rah[acc]
                    rz[sel[todo[acc]]] = st.pgauss(l2[acc], rzc[acc], bs.sigpol[2])
                todo = todo[rej]
    rz = np.minimum(np.maximum(rz, F(1.0)), ZCN - F(1.0)).astype(F)
    ra = np.minimum(np.maximum(ra, F(1.0)), ACN - F(1.0)).astype(F)
    rn = ra - rz
    nra = np.minimum(nint(ra), 350)
    nra = np.clip(nra, 0, 350)
    peon = np.minimum(bs.peon[imode, 2, nra], F(1.0))
    peoz = np.minimum(bs.peoz[imode, 2, nra], F(1.0))
    bs.peon[imode, 2, nra] = peon  # Ivenodd writes the clamp back (idempotent)
    bs.peoz[imode, 2, nra] = peoz
    inh = np.asarray(ivenodd(rn, peon))
    izh = np.asarray(ivenodd(rz, peoz))
    iah = inh + izh
    inl = fint(RNCN - inh.astype(F))
    izl = fint(ZCN - izh.astype(F))
    ial = fint(ACN - iah.astype(F))
    inl, izl, ial = np.maximum(inl, 1), np.maximum(izl, 1), np.maximum(ial, 1)
    inh, iah, izh = np.minimum(inh, 200), np.minimum(iah, 350), np.minimum(izh, 150)
    inh, iah, izh = np.maximum(inh, 0), np.maximum(iah, 0), np.maximum(izh, 0)
    # pre-neutron tallies (heavy, then light, per event)
    np.add.at(tally.apre, np.stack([iah, ial], 1).ravel(), racc)
    np.add.at(tally.anpre, np.stack([np.minimum(inh, 200), np.minimum(inl, 200)], 1).ravel(), racc)
    np.add.at(tally.cnt_pre, (iah, izh), 1)
    np.add.at(tally.cnt_pre, (np.minimum(ial, 350), np.minimum(izl, 150)), 1)
    # deformation energies
    beta = cs.beta
    b_h = np.where(imode <= 3, beta[np.minimum(imode, 3), 2, izh],
                   np.where(imode == 4, beta[1, 2, izh], beta[2, 2, izh])).astype(F)
    b_l = np.where(imode <= 3, beta[np.minimum(imode, 3), 1, np.minimum(izl, 150)],
                   beta[2, 2, np.minimum(izl, 150)]).astype(F)
    ed = cs.edefo
    mh = np.where(imode <= 3, ed[np.minimum(imode, 3), 2, izh],
                  np.where(imode == 4, ed[1, 2, izh], ed[2, 2, izh])).astype(F)
    izl_c = np.minimum(izl, 150)
    ml = np.where(imode <= 3, ed[np.minimum(imode, 3), 1, izl_c],
                  np.where(imode == 4, ed[1, 2, izl_c], ed[2, 2, izl_c])).astype(F)
    fzh, fah, fzl, fal = izh.astype(F), iah.astype(F), izl.astype(F), ial.astype(F)
    sgh = _a(lymass(fzh, fah, b_h + F(0.165))) - _a(lymass(fzh, fah, b_h))
    sgl = _a(lymass(fzl, fal, b_l + F(0.165))) - _a(lymass(fzl, fal, b_l))
    mh = np.maximum(mh, F(0.0))
    ml = np.maximum(ml, F(0.0))
    eh = _rej_pos(st, lid, mh, sgh)
    el = _rej_pos(st, lid, ml, sgl)
    # intrinsic excitation energies (light first)
    eil_m = np.maximum(bs.epart[imode, 1, np.minimum(ial, 350)], F(0.0))
    eih_m = np.maximum(bs.epart[imode, 2, iah], F(0.0))
    eil = _rej_pos(st, lid, eil_m, F(0.5) * eil_m + F(0.5))
    eih = _rej_pos(st, lid, eih_m, F(0.5) * eih_m + F(0.5))
    eil = eil - tab.ap[np.minimum(izl, 150), np.minimum(ial, 351)]
    eih = eih - tab.ap[izh, iah]
    eh = eh + eih
    el = el + eil
    # collective energy (ECOLLFRAC = 0; + 1.6 MeV for odd-Z CN)
    ecm = F(max(F(F(0.0) * F(cs.dss - bs.etunn)), F(0.0)))
    if cs.nZ % 2 == 1:
        ecm = F(ecm + F(1.6))
    ecoll = _rej_pos(st, lid, np.full(n, ecm, dtype=F), np.full(n, F(0.5) * ecm, dtype=F))
    ecoll = ecoll + bs.ecollsaddle[imode]
    ech = F(0.5) * ecoll
    eh = eh + ech
    el = el + ech
    # fragment angular momenta (light first)
    sp = bs.spin
    inl_c = np.minimum(inl, 200)
    s_l = np.where(imode <= 3, sp[np.minimum(imode, 3), 1, inl_c, izl_c],
                   np.where(imode == 4, sp[1, 2, inl_c, izl_c], sp[2, 2, inl_c, izl_c])).astype(F)
    s_h = np.where(imode <= 3, sp[np.minimum(imode, 3), 2, inh, izh],
                   np.where(imode == 4, sp[1, 2, inh, izh], sp[2, 2, inh, izh])).astype(F)
    sq2 = np.sqrt(F(2.0))
    jl = st.plingauss(lid, s_l / sq2) - F(0.5)
    jh = st.plingauss(lid, s_h / sq2) - F(0.5)
    jl = np.maximum(jl, F(0.0))
    jh = np.maximum(jh, F(0.0))
    c116 = F(F(1.16) * F(1.16))
    irl = c116 * _a(powf(fal, 1.6667)) / F(103.8415)
    erl = jl * (jl + F(1.0)) / (F(2.0) * (F(0.45) * irl))
    irh = c116 * _a(powf(fah, 1.6667)) / F(103.8415)
    erh = jh * (jh + F(1.0)) / (F(2.0) * (F(0.45) * irh))
    # TKE (geftalys.f:2021-2041)
    um, ap = tab.um, tab.ap
    ialc = np.minimum(ial, 351)
    qv = (cs.um_cn + cs.ap_cn) - (((um[izh, iah] + ap[izh, iah]) + um[izl_c, ialc]) + ap[izl_c, ialc])
    txe = ((el + eh) + erl) + erh
    tke = (qv + bs.rexc_gs) - txe
    bad = tke < F(0.0)
    if np.any(bad):
        tally.tke_fix += int(bad.sum())
        corr = txe[bad] + tke[bad] - F(1.0)
        el[bad] = el[bad] * corr / txe[bad]
        eh[bad] = eh[bad] * corr / txe[bad]
    # evaporation: heavy then light
    zhp, ahp = _eva(st, lid, izh, iah, eh, tab)
    rnhp = ahp - zhp
    izhp = np.minimum(nint(zhp), 150)
    inhp = np.minimum(nint(rnhp), 200)
    iahp = np.minimum(nint(zhp) + nint(rnhp), 350)
    zlp, alp = _eva(st, lid, izl, ial, el, tab)
    rnlp = alp - zlp
    izlp = np.maximum(nint(zlp), 1)
    inlp = np.maximum(nint(rnlp), 1)
    ialp = np.maximum(nint(zlp) + nint(rnlp), 1)
    np.add.at(tally.apost, np.stack([iahp, np.minimum(ialp, 350)], 1).ravel(), racc)
    np.add.at(tally.anpost, np.stack([inhp, np.minimum(inlp, 200)], 1).ravel(), racc)
    np.add.at(tally.cnt_post, (iahp, izhp), 1)
    np.add.at(tally.cnt_post, (np.minimum(ialp, 350), np.minimum(izlp, 150)), 1)
    irn_h = iah - iahp
    ok = (irn_h > 0) & (irn_h <= 20)
    np.add.at(tally.an2post, (iahp[ok], irn_h[ok]), 1)
    np.add.at(tally.an2pre, (iah[ok], irn_h[ok]), 1)
    irn_l = ial - ialp
    tot = irn_h + irn_l
    ok = (tot > 0) & (tot <= 50)
    np.add.at(tally.ann, tot[ok], 1)
    ok = (irn_l > 0) & (irn_l <= 20)
    np.add.at(tally.an2post, (np.minimum(ialp[ok], 350), irn_l[ok]), 1)
    np.add.at(tally.an2pre, (np.minimum(ial[ok], 350), irn_l[ok]), 1)


def _rej_pos(st: GefStream, lid, mean, sig):
    """`10 x = PGauss(mean, sig); if (x < 0) goto 10` per lane."""
    out = np.empty(lid.size, dtype=F)
    todo = np.arange(lid.size)
    while todo.size:
        v = st.pgauss(lid[todo], mean[todo], np.broadcast_to(sig, mean.shape)[todo])
        ok = ~(v < F(0.0))
        out[todo[ok]] = v[ok]
        todo = todo[~ok]
    return out


# ------------------------------------------------------------------------------------------------ geftalys
@dataclass
class GefResult:
    """The /outgef/ commons after one geftalys call (massdis.f90:427-452 reads them)."""
    ysum: np.ndarray  # (351,) index A
    ysump: np.ndarray
    yAZ: np.ndarray  # (351, 151) [A, Z]
    yAZp: np.ndarray
    anpre_sum: np.ndarray  # (351,)
    anpost_sum: np.ndarray
    ann_sum: np.ndarray  # (51,)
    anMean_sum: np.float32
    detail: list = field(default_factory=list)


def geftalys(ZCN: float, ACN: float, excit, fsig, nevt: int, st: GefStream, data: GefData | None = None,
             detail: bool = False, max_lanes: int = 65536) -> GefResult:
    """GEF fission yields and prompt neutrons of one fissioning nucleus over its excitation bins.

    TALYS: geftalys.f:1 (geftalys)
    Test: tests/hf/test_kwcov_b14b.py
    """
    data = data or load_data()
    tab = _tables(id(data), data)
    res = GefResult(np.zeros(351, F), np.zeros(351, F), np.zeros((351, 151), F), np.zeros((351, 151), F),
                    np.zeros(351, F), np.zeros(351, F), np.zeros(51, F), F(0.0))
    if ZCN > 136.0 or ACN > 350.0 or ACN - ZCN > 203.0:
        return res
    talys = st.mode == "talys"
    nl = 1 if talys else int(min(nevt, max_lanes))
    st.reset(nl)
    cs = call_setup(ZCN, ACN, data, tab)
    epart = peo = spin = None
    for nex in range(len(excit)):
        bs = bin_setup(cs, excit[nex], tab, data, epart, peo, spin)
        bs.rexc_gs = F(excit[nex])
        epart, peo, spin = bs.epart, (bs.peoz, bs.peon), bs.spin
        t = BinTally(np.zeros(351, F), np.zeros(351, F), np.zeros((351, 151), np.int64), np.zeros((351, 151), np.int64),
                     np.zeros((351, 21), np.int64), np.zeros((351, 21), np.int64), np.zeros(51, np.int64),
                     np.zeros(201, F), np.zeros(201, F))
        done = 0
        while done < nevt:
            k = min(nl, nevt - done)
            run_events(cs, bs, nevt, st, tab, np.arange(k), t)
            done += k
        _bin_sums(res, t, F(fsig[nex]), detail, bs)
    return res


def _bin_sums(res: GefResult, t: BinTally, fs, detail: bool, bs: BinSetup) -> None:
    """geftalys.f:2195-2335: normalisations and the sums over bins weighted by fsig."""
    cpre = t.cnt_pre[1:201, 1:151].astype(F)
    cpost = t.cnt_post[1:201, 1:151].astype(F)
    norm = F(cpre.sum(dtype=D))
    yazt = np.zeros((351, 151), F)
    yazpt = np.zeros((351, 151), F)
    yazt[1:201, 1:151] = cpre * F(2.0) / norm
    yazpt[1:201, 1:151] = cpost * F(2.0) / norm
    j = np.arange(21, dtype=D)
    z = (t.an2pre * j[None, :]).sum(axis=1).astype(F)
    nn = t.an2pre.sum(axis=1).astype(F)
    with np.errstate(all="ignore"):
        anapre = np.where(nn != 0, z / nn, F(0.0)).astype(F)
    z = (t.an2post * j[None, :]).sum(axis=1).astype(F)
    nn = t.an2post.sum(axis=1).astype(F)
    with np.errstate(all="ignore"):
        anapost = np.where(nn != 0, z / nn, F(0.0)).astype(F)
    asum = F(t.ann.sum())
    ann = (t.ann.astype(F) / asum).astype(F) if asum > 0 else np.zeros(51, F)
    mean = F(0.0)
    for i in range(51):
        mean = F(mean + F(i) * ann[i])
    res.yAZ += (yazt * fs).astype(F)
    res.yAZp += (yazpt * fs).astype(F)
    res.ysum += (t.apre * fs).astype(F)
    res.ysump += (t.apost * fs).astype(F)
    res.anpre_sum += (anapre * fs).astype(F)
    res.anpost_sum += (anapost * fs).astype(F)
    res.ann_sum[1:] += (ann[1:] * fs).astype(F)
    res.anMean_sum = F(res.anMean_sum + mean * fs)
    if detail:
        res.detail.append({"Eex": float(bs.Eex), "yields": bs.yields.copy(), "anpre": t.anpre.copy(),
                           "anpost": t.anpost.copy(), "apre": t.apre.copy(), "apost": t.apost.copy(),
                           "anapre": anapre, "anapost": anapost, "ann": ann, "mean": mean, "tke_fix": t.tke_fix})


_TABLES: dict = {}


def _tables(key, data):
    if key not in _TABLES:
        _TABLES.clear()
        _TABLES[key] = Tables(data)
    return _TABLES[key]
