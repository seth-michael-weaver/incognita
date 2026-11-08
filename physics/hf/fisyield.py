"""KWCOV B14 part 1 (FISYIELD): fission fragment and fission product yields, `massdis y` + `fymodel 1` (Brosa).

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning (Brosa model: M. Duijvestijn). See physics/hf/NOTICE-TALYS.md.

OUTPUT ONLY. The switch is the deck's `massdis y` on a run with fission; nothing else turns it on and, off, nothing is
recorded (every Results array is unchanged). `massdis y` already set its cascade defaults before this batch (transeps,
popeps, Rfiseps 1e-9, pfnsmodel 2: input/defaults.py); this module adds the yields.

What it gives: `Results.fission_yields`, {TALYS file name: {column: ndarray}} (massdisout.f90):
    yieldA<E>.fis       A, FP_yield, FF_yield, FP_xs, FF_xs over A = 1..Atarget at one incident energy, plus
                        "Tot" = [yieldtotpost, yieldtotpre, xstotpost, xstotpre]
    yieldZA<E>.fis      Z, A, isomer (-1), FP_yield, FF_yield, FP_xs, FF_xs: the rows TALYS writes (pre- and post-neutron
                        cross section both >= fpeps)
    fpZZZAAA.tot        E, FP_yield, FF_yield, FP_xs, FF_xs over the run's energies (isotopic)
    rpZZZAAA.tot        E, FP_xs (TALYS's file name for the fission product cross section; it lives in this dict, not in
                        Results.residual_production_mb)
    fpAAA.tot           E, FP_yield, FF_yield, FP_xs, FF_xs over the run's energies (per mass)
FF = fission fragment (pre-neutron), FP = fission product (post-neutron emission, Brosa's evaporation estimate).
<E> is TALYS's energy string (`0001.000`, or `2.53E-08` below 1 keV).

Models: fymodel 1 (Brosa) is ported. fymodel 2 (GEF, the TALYS default once massdis is on), 3 (GEF + TALYS
evaporation), 4 (fragment files: ffmodel, yieldfile) and 5 (own population files) are refused with an error (B14
parts 2 and 3). The isomer split of the fission products (yieldfpex / fpratio) is only filled by ffevap.f90 (fymodel
>= 3): with fymodel 1 TALYS writes none, and neither does the port.

TALYS routines ported here (file:line of the subroutine / function statement):
    massdis.f90:1 (massdis) [fymodel 1 branch, normalisation]   per-bin loop, fpeps, sums
    massdisout.f90:1 (massdisout)                                the yield files
    brosafy.f90:1 (brosafy)                                      the three Brosa modes (SL, ST I, ST II)
    neck.f90:1 (neck)                                            mass / charge / evaporation per mode
    trans.f90:1, trapzd.f90:1, funcfismode.f90:1                 mode transmission (TALYS's trapzd keeps no running
                                                                 sum: snew is reset at entry; ported as is)
    fmin.f90:1, fidi.f90:1, rpoint.f90:1, rhodi.f90:1, vr1/2/3.f90:1, sform.f90:1, evap.f90:1,
    bdef.f90:1, fsurf.f90:1, fcoul.f90:1, spline.f90:1, splint.f90:1, rtbis.f90:1
Single precision where TALYS has it (np.float32), double where TALYS has dbl (transmissions, level density).
Task: T10 (physics/hf/CONTRACT.md section 7; KWCOV batch B14 part 1, output only). Acceptance test: KWCOV-B14
(tests/hf/test_kwcov_b14.py, scripts/kwcov/b14_response.py, docs/hf/COVERAGE_PLAN.md).
"""

from __future__ import annotations

import math
from functools import lru_cache

import numpy as np

F = np.float32
NUMMASS = 414  # A0_talys_mod.f90:93
NUMELEM = 124  # A0_talys_mod.f90:26
NUMNEU = NUMMASS - NUMELEM
PI = F(3.14159265358979323)
TEMPS = np.array([0.0, 0.3, 0.6, 0.9, 1.2, 1.6, 2.0, 2.5, 3.0], dtype=F)
HBAR = F(6.582119569e-22)  # constants.f90:120
CLIGHT = F(2.99792458e8)
AMU = 931.49410242
PARMASS_N, PARMASS_P = 1.00866491574, 1.00782495281

_SET: dict | None = None
_REC: list = []


# ------------------------------------------------------------------------------------------------ switches
def settings(options) -> dict | None:
    """The run's yield switches, or None (no `massdis y`, or no fission). Refuses what part 1 does not port.

    TALYS: talysreaction.f90:189-196 (flagfission .and. flagmassdis), checkvalue.f90:1085-1088
    Test: tests/hf/test_kwcov_b14.py
    """
    if options is None:
        return None
    fy = int(getattr(options, "fymodel", 2))
    if not 1 <= fy <= 5:
        raise ValueError(f"fymodel {fy}: outside 1..5 (TALYS-error, checkvalue.f90:1085)")
    ff = int(getattr(options, "ffmodel", 1))
    if not 0 <= ff <= 4:
        raise ValueError(f"ffmodel {ff}: outside 0..4 (TALYS-error, checkvalue.f90:1086)")
    gr = int(getattr(options, "gefran", 50000))
    if not 1000 <= gr <= 1000000:
        raise ValueError(f"gefran {gr}: outside 1000..1000000 (TALYS-error, checkvalue.f90:1088)")
    if not (bool(getattr(options, "flagmassdis", False)) and bool(getattr(options, "flagfission", False))):
        return None
    if fy != 1:
        what = {2: "GEF (geftalys.f, 7,264 lines)", 3: "GEF + TALYS fragment evaporation (ffevap.f90)",
                4: "fission fragment files (ffmodel / yieldfile) + ffevap.f90", 5: "own fragment populations + ffevap.f90"}
        raise NotImplementedError(
            f"massdis y with fymodel {fy} ({what[fy]}) is not ported (KWCOV B14 parts 2/3); TALYS's default once massdis "
            f"is on is fymodel 2. Add `fymodel 1` (Brosa) to the deck for fission yields.")
    return {"fymodel": fy, "ffevap": bool(getattr(options, "flagffevap", True)),
            "Rfiseps": float(getattr(options, "Rfiseps", 1e-9))}


def begin_run(cas) -> bool:
    """Fix the run's switches (engine_c.cases, before the energy loop).

    TALYS: (none -- a port switch)
    Test: tests/hf/test_kwcov_b14.py
    """
    global _SET
    _REC.clear()
    s = settings(cas.options)
    if s is not None:
        s.update(Zinit=int(cas.Zc), Ainit=int(cas.Ac), Ztarget=int(cas.Zt), Atarget=int(cas.At))
    _SET = s
    return s is not None


def active() -> bool:
    """Whether this run computes fission yields.

    TALYS: (none -- a port switch)
    Test: tests/hf/test_kwcov_b14.py
    """
    return _SET is not None


# ------------------------------------------------------------------------------------------------ small numerics
def spline(x, y, n: int) -> np.ndarray:
    """Natural cubic spline second derivatives (yp1 = ypn = 2e30), single precision; y2 has len(x) entries.

    TALYS: spline.f90:1 (spline)
    Test: tests/hf/test_kwcov_b14.py
    """
    y2 = np.zeros(len(x), dtype=F)
    u = np.zeros(len(x), dtype=F)
    for i in range(1, n - 1):
        sig = F((x[i] - x[i - 1]) / (x[i + 1] - x[i - 1]))
        p = F(sig * y2[i - 1] + F(2.0))
        y2[i] = F((sig - F(1.0)) / p)
        u[i] = F((F(6.0) * ((y[i + 1] - y[i]) / (x[i + 1] - x[i]) - (y[i] - y[i - 1]) / (x[i] - x[i - 1]))
                  / (x[i + 1] - x[i - 1]) - sig * u[i - 1]) / p)
    y2[n - 1] = F(0.0)
    for k in range(n - 2, -1, -1):
        y2[k] = F(y2[k] * y2[k + 1] + u[k])
    return y2


def splint(xa, ya, y2a, n: int, x):
    """Cubic spline value at x (scalar or array), single precision, bisection bracket as splint.f90.

    TALYS: splint.f90:1 (splint)
    Test: tests/hf/test_kwcov_b14.py
    """
    xa = np.asarray(xa[:n], dtype=F)
    xv = np.asarray(x, dtype=F)
    if n < 2:
        raise RuntimeError("bad xa input in splint (TALYS stops)")
    klo = np.clip(np.searchsorted(xa, xv, side="right") - 1, 0, n - 2)
    khi = klo + 1
    h = (xa[khi] - xa[klo]).astype(F)
    a = ((xa[khi] - xv) / h).astype(F)
    b = ((xv - xa[klo]) / h).astype(F)
    ya, y2a = np.asarray(ya, dtype=F), np.asarray(y2a, dtype=F)
    y = (a * ya[klo] + b * ya[khi] + ((a ** 3 - a) * y2a[klo] + (b ** 3 - b) * y2a[khi]) * (h * h) / F(6.0)).astype(F)
    return y if y.ndim else F(y)


def fsurf(e):
    """Surface-energy shape factor of a spheroid (arithmetic IF on the sign of e), single precision, elementwise.

    TALYS: fsurf.f90:1 (fsurf)
    Test: tests/hf/test_kwcov_b14.py
    """
    e = np.asarray(e, dtype=F)
    out = np.ones_like(e)
    with np.errstate(all="ignore"):
        neg = e < 0
        if neg.any():
            en = e[neg]
            dum = np.sqrt(F(1.0) + en * en)
            out[neg] = (np.log(-en + dum) - en * dum) / (F(-2.0) * en * dum ** F(1.0 / 3.0))
        pos = e > 0
        if pos.any():
            ep = e[pos]
            dum = np.sqrt(F(1.0) - ep * ep)
            out[pos] = (np.arcsin(ep) + ep * dum) / (F(2.0) * ep * dum ** F(1.0 / 3.0))
    return out


def fcoul(e):
    """Coulomb self-energy shape factor (fcoul.f90), single precision, elementwise.

    TALYS: fcoul.f90:1 (fcoul)
    Test: tests/hf/test_kwcov_b14.py
    """
    e = np.asarray(e, dtype=F)
    out = np.ones_like(e)
    with np.errstate(all="ignore"):
        neg = e < 0
        if neg.any():
            en = e[neg]
            out[neg] = (F(1.0) + en * en) ** F(1.0 / 3.0) / en * np.arctan(en)
        pos = e > 0
        if pos.any():
            ep = e[pos]
            out[pos] = (F(1.0) - ep * ep) ** F(1.0 / 3.0) / (F(2.0) * ep) * np.log((F(1.0) + ep) / (F(1.0) - ep))
    return out


def bdef(amass, zchar, eps):
    """Liquid-drop energy of a deformed fragment, the `b` output of bdef.f90 (cou and sym are not used), float32.

    TALYS: bdef.f90:1 (bdef)
    Test: tests/hf/test_kwcov_b14.py
    """
    amass = np.asarray(amass, dtype=F)
    zchar = np.asarray(zchar, dtype=F)
    with np.errstate(all="ignore"):
        a3w = amass ** F(1.0 / 3.0)
        cou = F(0.7053) / a3w * fcoul(np.broadcast_to(np.asarray(eps, dtype=F), amass.shape)) - F(1.153) / amass
        hsc = F(15.4941) * amass - F(17.9439) * a3w ** 2 * fsurf(np.broadcast_to(np.asarray(eps, dtype=F), amass.shape))
        sym = F(1.7826) / amass ** 2 * hsc
        b = -hsc + sym * (amass - zchar - zchar) ** 2 + cou * zchar ** 2
    return b.astype(F)


def rtbis_vec(func, x1, x2, xacc: float, jmax: int = 40):
    """Bisection as rtbis.f90 (orientation on the sign of f(x1), at most 40 halvings, stop at |dx| < xacc or f = 0),
    batched over the arrays x1 / x2, float32; `func` maps an array to an array.

    TALYS: rtbis.f90:1 (rtbis)
    Test: tests/hf/test_kwcov_b14.py
    """
    x1 = np.asarray(x1, dtype=F)
    x2 = np.broadcast_to(np.asarray(x2, dtype=F), x1.shape).astype(F)
    f = func(x1)
    neg = f < 0
    root = np.where(neg, x1, x2).astype(F)
    dx = np.where(neg, x2 - x1, x1 - x2).astype(F)
    act = np.ones(x1.shape, dtype=bool)
    for _ in range(jmax):
        dx = np.where(act, (dx * F(0.5)).astype(F), dx)
        xmid = (root + dx).astype(F)
        fmid = func(xmid)
        root = np.where(act & (fmid <= 0), xmid, root).astype(F)
        act = act & ~((np.abs(dx) < F(xacc)) | (fmid == 0))
        if not act.any():
            break
    return root


# ------------------------------------------------------------------------------------------------ neck geometry
class _Neck:
    """The neck-rupture globals of A0_talys_mod (r1, r2, r3, z1, z2, z3, aaa, cur, totl, di, rest, vtot, rp, rt, rpt,
    c0) as one object; fidi.f90 changes r1, r3, z1, z2, z3, aaa and cur as a side effect, as in TALYS."""

    __slots__ = ("r1", "r2", "r3", "z1", "z2", "z3", "aaa", "cur", "totl", "di", "rest", "vtot", "rp", "rt", "rpt",
                 "c0")

    def vr1(self, z):
        return F(PI * ((F(2.0) * self.r1 ** 3 - z ** 3) / F(3.0) + self.r1 ** 2 * z))

    def vr2(self, zz1, zz2, zz3):
        z21 = (zz2 - zz1) / self.aaa
        z32 = (zz3 - zz2) / self.aaa
        z21 = np.minimum(z21, F(30.0))
        z32 = np.minimum(z32, F(30.0))
        b = self.aaa * self.aaa * self.cur
        return (PI * (((self.r2 - b) ** 2 + F(0.5) * b ** 2) * (zz3 - zz1) + self.aaa * b * (
            F(2.0) * (self.r2 - b) * (np.sinh(z32) + np.sinh(z21)) + F(0.25) * b * (np.sinh(F(2.0) * z32)
                                                                                    + np.sinh(F(2.0) * z21))))).astype(F)

    def vr3(self, z):
        d = F(self.totl - self.r1 - self.r3)
        return F(PI * ((F(2.0) * self.r3 ** 3 - (d - z) ** 3) / F(3.0) + self.r3 ** 2 * (d - z)))

    def rhodi(self, z):
        d = F(self.totl - self.r1 - self.r3)
        if z < -self.r1 or z > d + self.r3:
            return F(0.0)
        if z <= self.z1:
            return F(math.sqrt(F(self.r1 ** 2 - z ** 2))) if self.r1 ** 2 - z ** 2 >= 0 else F(np.nan)
        if z <= self.z3:
            return F(self.r2 + self.aaa * self.aaa * self.cur * (F(np.cosh(F((z - self.z2) / self.aaa))) - F(1.0)))
        v = F(self.r3 ** 2 - (z - d) ** 2)
        return F(math.sqrt(v)) if v >= 0 else F(np.nan)

    def fidi(self, x) -> np.float32:
        """fidi.f90: the shape functional; sets the globals from the trial point x(1..7) first."""
        d = F(self.totl - self.r1 - self.r3)
        self.aaa = F(F(0.8) + x[0] * F(2.0))
        self.z2 = F(d * (F(0.5) - x[1]))
        self.z1 = F(self.r1 * x[2])
        self.z3 = F(d - self.r3 * x[3])
        self.r1 = F(self.rp * x[4])
        self.r3 = F(self.rt * x[5])
        self.cur = F(self.c0 * abs(x[6]))
        wu1 = F(self.r1 ** 2 - self.z1 ** 2)
        if wu1 < 1.0e-8:
            wu1 = F(1.0e-8)
        wu3 = F(self.r3 ** 2 - (d - self.z3) ** 2)
        if wu3 < 1.0e-8:
            wu3 = F(1.0e-8)
        sq1, sq3 = F(math.sqrt(wu1)), F(math.sqrt(wu3))
        z21 = F((self.z2 - self.z1) / self.aaa)
        z32 = F((self.z3 - self.z2) / self.aaa)
        z21 = min(z21, F(30.0))
        z32 = min(z32, F(30.0))
        aac = F(self.aaa * self.aaa * self.cur)
        al = F((self.vtot - self.vr1(self.z1) - self.vr2(self.z1, self.z2, self.z3) - self.vr3(self.z3)) ** 2)
        be = F(((self.rp ** 3 - self.r1 ** 3) - self.rpt * (self.rt ** 3 - self.r3 ** 3)) ** 2 * F(10.0))
        ga = F((sq1 - self.r2 - aac * (F(np.cosh(z21)) - F(1.0))) ** 2 * F(1.0e5))
        de = F((sq3 - self.r2 - aac * (F(np.cosh(z32)) - F(1.0))) ** 2 * F(1.0e5))
        eq = F((self.z1 / sq1 - self.aaa * self.cur * F(np.sinh(z21))) ** 2 * F(1.0e5))
        epsc = F(((d - self.z3) / sq3 - self.aaa * self.cur * F(np.sinh(z32))) ** 2 * F(1.0e5))
        ds = F(x[6] ** 2 * F(1.0e-4))
        return F(al + be + ga + de + eq + epsc + ds)


def fmin(extern, k: int, psh, pd, pa, pe, ncall: int, eps: float):
    """Bounded simplex minimisation of fmin.f90 (TALYS's goto structure kept as a state loop); psh (in/out) ends at the
    best vertex; returns the function value of the last ranking (label 17), as the Fortran's `fmin`.

    TALYS: fmin.f90:1 (fmin)
    Test: tests/hf/test_kwcov_b14.py
    """
    alpha, betap, gam = F(1.0), F(0.5), F(2.0)
    for i in range(k):
        if psh[i] < pa[i]:
            psh[i] = pa[i]
        if psh[i] > pe[i]:
            psh[i] = pe[i]
    fn = F(k)
    n1 = k + 1
    ssh = np.zeros((k, n1), dtype=F)
    for jk in range(n1):
        ssh[:, jk] = psh[:k]
    for i in range(k):
        ssh[i, i + 1] = F(ssh[i, i + 1] + pd[i])
    f = np.zeros(n1, dtype=F)
    icall = 0
    fmin_v = F(0.0)
    std = F(0.0)
    state = "17"
    for jk in range(n1):
        if jk != 0:
            psh[:k] = ssh[:, jk]
        icall += 1
        if icall > ncall:
            state = "80"
            break
        f[jk] = extern(psh)
    maxf = minf = 0
    fmax = fmax2 = F(0.0)
    pc = np.zeros(k, dtype=F)
    pr = np.zeros(k, dtype=F)
    pex = np.zeros(k, dtype=F)
    fr = fex = F(0.0)
    while True:
        if state == "17":
            fmax, maxf = f[0], 0
            for i in range(1, n1):
                if f[i] < fmax:
                    continue
                maxf, fmax = i, f[i]
            fmin_v, minf = f[0], 0
            for i in range(1, n1):
                if f[i] > fmin_v:
                    continue
                minf, fmin_v = i, f[i]
            fmax2 = f[minf]
            for i in range(n1):
                if i == maxf or f[i] < fmax2:
                    continue
                fmax2 = f[i]
            pc[:] = 0.0
            for jk in range(n1):
                if jk == maxf:
                    continue
                for i in range(k):
                    pc[i] = F(pc[i] + ssh[i, jk])
            pc[:] = (pc / fn).astype(F)
            if eps < 0.0:  # label 74
                s = F(0.0)
                for jk in range(n1):
                    s = F(s + f[jk])
                s = F(s / F(n1))
                s2 = F(0.0)
                for jk in range(n1):
                    s2 = F(s2 + (f[jk] - s) ** 2)
                std = F(math.sqrt(F(s2 / fn)))
            else:
                std = F(0.0)
                pmax = F(abs(pc[k - 1] - ssh[k - 1, maxf]))
                if pmax > std:
                    std = pmax
            state = "80"
        if state == "80":
            if icall < ncall and std > abs(eps):
                state = "27"
            else:
                psh[:k] = ssh[:, minf]
                return fmin_v
        if state == "27":
            for i in range(k):
                pr[i] = F((F(1.0) + alpha) * pc[i] - alpha * ssh[i, maxf])
            bad = next((i for i in range(k) if pr[i] < pa[i] or pr[i] > pe[i]), None)
            icall += 1
            if icall > ncall:
                state = "80"
                continue
            if bad is None:
                fr = extern(pr.copy())
            else:
                fr = F(abs(fmax) * (F(1.0) + abs((pr[bad] - pc[bad]) / pd[bad])))
            if fr < fmin_v:  # label 40
                for i in range(k):
                    pex[i] = F(gam * pr[i] + (F(1.0) - gam) * pc[i])
                bad = next((i for i in range(k) if pex[i] < pa[i] or pex[i] > pe[i]), None)
                icall += 1
                if icall > ncall:
                    state = "80"
                    continue
                if bad is None:
                    fex = extern(pex.copy())
                else:
                    fex = F(abs(fmax) * (F(1.0) + abs((pex[bad] - pc[bad]) / pd[bad])))
                if fex > fmin_v:
                    state = "44"
                else:
                    state = "45"
            elif fr > fmax2:
                state = "50"
            else:
                state = "44"
        if state == "45":
            ssh[:, maxf] = pex
            f[maxf] = fex
            state = "17"
            continue
        if state == "44":
            ssh[:, maxf] = pr
            f[maxf] = fr
            state = "17"
            continue
        if state == "50":
            if not fr > fmax:
                ssh[:, maxf] = pr
                f[maxf] = fr
            for i in range(k):
                pex[i] = F(betap * ssh[i, maxf] + (F(1.0) - betap) * pc[i])
            icall += 1
            if icall > ncall:
                state = "80"
                continue
            fex = extern(pex.copy())
            if fex < fmax:
                ssh[:, maxf] = pex
                f[maxf] = fex
                state = "17"
                continue
            stop = False
            for jk in range(n1):
                if jk == minf:
                    continue
                for i in range(k):
                    ssh[i, jk] = F(F(0.5) * (ssh[i, jk] + ssh[i, minf]))
                    psh[i] = ssh[i, jk]
                icall += 1
                if icall > ncall:
                    stop = True
                    break
                f[jk] = extern(psh.copy())
            state = "80" if stop else "17"


def neck(Z: int, A: int, ap, edefo, elt, crel, ffevap: bool, ign):
    """Mass, charge and (with ffevaporation) post-neutron yields of one Brosa mode at one deformation energy:
    (fmass, fmasscor, fmz, fmzcor), arrays over A (0..NUMMASS) and (A, Z) (0..NUMELEM), float32.
    `ign(E)` is the fissioning nucleus' Ignatyuk a(E).

    TALYS: neck.f90:1 (neck)
    Test: tests/hf/test_kwcov_b14.py
    """
    s = _Neck()
    r0, xnu = F(1.15), F(1.0)
    atot, ztot = F(A), F(Z)
    ap, edefo, elt, crel = F(ap), F(edefo), F(elt), F(crel)
    if ffevap:
        astepnum, astepsize, izstepnum, zstepsize = F(10.0), F(0.1), 30, F(0.1)
    else:
        astepnum, astepsize, izstepnum, zstepsize = F(1.0), F(1.0), 3, F(1.0)
    s.totl = F(F(F(1.15) / F(1.2249)) * F(2.0) * elt)
    rayl = F(F(11.0) * elt / (F(2.4) * F(1.2249) * atot ** F(0.333333)))
    s.di = F(F(3.0) / (F(4.0) * PI * r0 ** 3))
    s.vtot = F(atot / s.di)
    zda = F(ztot / atot)
    gam = F(F(0.9517) * (F(1.0) - F(1.7826) * ((atot - F(2.0) * ztot) / atot) ** 2))
    at = F(atot - ap)
    s.rt = F(r0 * at ** F(1.0 / 3.0))
    s.rp = F(r0 * ap ** F(1.0 / 3.0))
    d = F(s.totl - s.rt - s.rp)
    s.r2 = F(s.totl / rayl)
    s.c0 = F(crel * F(2.0) * (s.rt + s.rp + F(2.0) * (F(math.sqrt(F((s.rt - s.r2) * (s.rp - s.r2)))) - s.r2)) / d ** 2)
    s.rpt = F((s.rp / s.rt) ** xnu)
    ald = F(ign(edefo))
    tmp = F(math.sqrt(F(edefo / ald)))
    psh = np.array([0.5, 0.0, 0.65, 0.65, 0.8, 0.8, 1.0], dtype=F)
    pa = np.array([0.0, -0.2, 0.3, 0.3, 0.6, 0.6, 0.5], dtype=F)
    pe = np.array([1.0, 0.2, 1.0, 1.0, 1.0, 1.0, 10.0], dtype=F)
    pd = np.array([0.1, 0.05, 0.35, 0.35, 0.2, 0.2, 0.5], dtype=F)
    s.r1, s.r3 = s.rp, s.rt
    s.z1 = F(s.r1 * psh[2])
    s.z3 = F(s.r3 * psh[3])
    s.z2, s.aaa, s.cur, s.rest = F(0.0), F(1.0), F(0.0), F(0.0)
    for k in range(1, 16):
        if k >= 2:
            delt = F(F(0.2) ** ((k + 1) // 2))
            pa = (psh - delt).astype(F)
            pe = (psh + delt).astype(F)
            pd = np.full(7, delt, dtype=F)
        fimin = fmin(s.fidi, 7, psh, pd, pa, pe, 200, -1.0e-4)
        if fimin < 1.0e-3:
            break
    d = F(s.totl - s.r1 - s.r3)
    amin = F(s.di * s.vr1(s.z1))
    imax = int(F(s.di * s.vr2(s.z1, s.z2, s.z3) * astepnum))
    n = imax + 1
    if n <= 0:
        z = np.zeros(NUMMASS + 1, dtype=F)
        return z, z.copy(), np.zeros((NUMMASS + 1, NUMELEM + 1), dtype=F), np.zeros((NUMMASS + 1, NUMELEM + 1), dtype=F)
    ii = np.arange(n)
    aloop = (amin + (ii * astepsize).astype(F)).astype(F)
    rest = (amin - aloop).astype(F)
    z1, z2, z3 = s.z1, s.z2, s.z3
    zriss = rtbis_vec(lambda z: (s.di * s.vr2(z1, z2, z) + rest).astype(F), np.full(n, z1, dtype=F), z3, 2.0e-4)
    a1 = (F(0.5) * (zriss + s.r1)).astype(F)
    a2 = (F(0.5) * (d + s.r3 - zriss)).astype(F)
    ve1 = (s.vr1(z1) + s.vr2(z1, z2, zriss)).astype(F)
    ve2 = (s.vr3(z3) + s.vr2(zriss, z2, z3)).astype(F)
    with np.errstate(all="ignore"):
        b1 = np.sqrt(F(3.0) * ve1 / (F(4.0) * PI * a1)).astype(F)
        b2 = np.sqrt(F(3.0) * ve2 / (F(4.0) * PI * a2)).astype(F)
        de = (a1 + a2).astype(F)
        x1 = (a1 ** 2 - b1 ** 2).astype(F)
        x1 = np.where(x1 >= 0, np.sqrt(np.abs(x1)) / de, -np.sqrt(np.abs(x1)) / de).astype(F)
        x2 = (a2 ** 2 - b2 ** 2).astype(F)
        x2 = np.where(x2 >= 0, np.sqrt(np.abs(x2)) / de, -np.sqrt(np.abs(x2)) / de).astype(F)
    s12 = _sform(x1, x2)
    coul12 = (F(1.44) * s12 / de).astype(F)
    x1 = (x1 * de / a1).astype(F)
    x2 = (x2 * de / a2).astype(F)
    am1 = aloop
    am2 = (atot - am1).astype(F)
    nz = 2 * izstepnum + 1
    off = ((np.arange(1, nz + 1) - izstepnum - 1) * zstepsize).astype(F)
    ze1 = (zda * am1[:, None] + off[None, :]).astype(F)
    ze2 = (ztot - ze1).astype(F)
    ok = (ze1 >= 0) & (ze2 >= 0)
    A1 = np.broadcast_to(am1[:, None], ze1.shape).astype(F)
    A2 = np.broadcast_to(am2[:, None], ze1.shape).astype(F)
    X1 = np.broadcast_to(x1[:, None], ze1.shape).astype(F)
    X2 = np.broadcast_to(x2[:, None], ze1.shape).astype(F)
    bind1 = bdef(A1, ze1, X1)
    bind2 = bdef(A2, ze2, X2)
    bind01 = bdef(A1, ze1, F(0.0))
    bind02 = bdef(A2, ze2, F(0.0))
    es1 = (edefo / atot * A1).astype(F)
    es2 = (edefo - es1).astype(F)
    es1 = (bind1 - bind01 + es1).astype(F)
    es2 = (bind2 - bind02 + es2).astype(F)
    wlog = (es1 + es2).astype(F)
    rnma = (wlog * F(0.167)).astype(F)
    rn1 = np.zeros(ze1.shape, dtype=F)
    rn2 = np.zeros(ze1.shape, dtype=F)
    if ffevap:  # the evaporation estimate only feeds fmzcor (neck.f90:375-381)
        for amm, zee, ess, out in ((A1, ze1, es1, rn1), (A2, ze2, es2, rn2)):
            m = ok & (rnma > F(0.7))
            if m.any():
                am_, ze_, es_ = amm[m], zee[m], ess[m]
                bb = bdef(am_, ze_, F(0.0))

                def evap(rn, am_=am_, ze_=ze_, es_=es_, bb=bb):
                    an = (am_ - rn).astype(F)
                    bn = bdef(an, ze_, F(0.0))
                    bn1 = bdef((an - F(1.0)).astype(F), ze_, F(0.0))
                    with np.errstate(invalid="ignore"):
                        return (es_ - F(0.5) * (bn + bn1) + bb - F(0.621) * rn * np.sqrt(rn + F(1.0))).astype(F)

                r = rtbis_vec(evap, np.full(am_.shape, -1.0, dtype=F), rnma[m], 1.0e-2)
                out[m] = np.maximum(r, F(0.0))
    with np.errstate(all="ignore"):
        vnel = (F(4.0) * PI * gam * (b1 * b2) ** 2 / (a1 * b2 * b2 + a2 * b1 * b1) * F(-1.7817)).astype(F)
        coulel = (coul12[:, None] * ze1 * ze2).astype(F)
        ezdis = ((bind1 + bind2 + coulel + vnel[:, None]) / tmp).astype(F)
    first = np.argmax(ok, axis=1)
    norm = ezdis[np.arange(n), first]
    ezdis = (ezdis - norm[:, None]).astype(F)
    zdis = np.where(ok & (np.abs(ezdis) <= 80.0), np.exp(-np.where(np.abs(ezdis) <= 80.0, ezdis, F(0.0))), F(0.0)).astype(F)
    rz2 = s.rhodi(z2)
    eob = np.array([F(F(2.0) * PI * gam * (s.rhodi(F(zr)) ** 2 - rz2 ** 2)) for zr in zriss], dtype=F)
    expo = (eob / tmp).astype(F)
    wgt = np.where(expo < 80.0, np.exp(-np.minimum(expo, F(80.0))), F(0.0)).astype(F)
    wgt[~ok.any(axis=1)] = F(0.0)
    sumw = F(np.cumsum(wgt, dtype=F)[-1]) if n else F(0.0)
    sumtmp = np.cumsum(zdis, axis=1, dtype=F)[:, -1]
    with np.errstate(all="ignore"):
        wgt = (wgt / sumw).astype(F)
        zdis = (zdis / sumtmp[:, None]).astype(F)
    w = (wgt[:, None] * zdis).astype(F)
    iaf1 = np.maximum((am1 + F(0.5)).astype(np.int64), 1)
    iaf2 = np.maximum((am2 + F(0.5)).astype(np.int64), 1)
    izf1 = np.maximum((ze1 + F(0.5)).astype(np.int64), 1)
    izf2 = np.maximum((ze2 + F(0.5)).astype(np.int64), 1)
    fmz = np.zeros((NUMMASS + 1, NUMELEM + 1), dtype=F)
    fmzcor = np.zeros((NUMMASS + 1, NUMELEM + 1), dtype=F)
    fmass = np.zeros(NUMMASS + 1, dtype=F)
    IA1 = np.broadcast_to(iaf1[:, None], ze1.shape)
    IA2 = np.broadcast_to(iaf2[:, None], ze1.shape)
    for k in range(n):  # the Fortran's order: per mass step, light then heavy per charge step
        np.add.at(fmz, (IA1[k], izf1[k]), w[k])
        np.add.at(fmz, (IA2[k], izf2[k]), w[k])
        if ffevap:
            irn1 = np.maximum((A1[k] - rn1[k] + F(0.5)).astype(np.int64), 1)
            irn2 = np.maximum((A2[k] - rn2[k] + F(0.5)).astype(np.int64), 1)
            np.add.at(fmzcor, (irn1, izf1[k]), w[k])
            np.add.at(fmzcor, (irn2, izf2[k]), w[k])
        fmass[iaf1[k]] = F(fmass[iaf1[k]] + wgt[k])
        fmass[iaf2[k]] = F(fmass[iaf2[k]] + wgt[k])
    fmasscor = fmzcor.sum(axis=1, dtype=F)
    return fmass, fmasscor, fmz, fmzcor


def _sform(x, y):
    """sform.f90: Coulomb interaction form factor of two spheroids (double series, 21 x 15 terms), float32,
    elementwise over the arrays x, y."""
    x = np.asarray(x, dtype=F)
    y = np.asarray(y, dtype=F)
    big = np.abs(x) > np.abs(y)
    z1 = np.where(big, x, y).astype(F)
    z2 = np.where(big, y, x).astype(F)
    zero = z1 == 0.0
    z1 = np.where(zero, F(1.0), z1).astype(F)
    z1 = np.copysign(z1 * z1, z1).astype(F)
    z2 = np.copysign(z2 * z2, z2).astype(F)
    out = np.zeros(x.shape, dtype=F)
    zn = (F(1.0) / z1).astype(F)
    for k in range(21):
        zn = (zn * z1).astype(F)
        sn = (F(0.75) / F(F(k + 0.5) * F(k + 1.5)) * zn).astype(F)
        zm = np.ones(x.shape, dtype=F)
        cnm = F(1.0)
        for m in range(1, 16):
            zm = (zm * z2).astype(F)
            cnm = F(cnm * F(k + m) * F(k + m - 0.5) / F(F(m) * F(m - 0.5)))
            sm = (F(F(0.5625) / F(F(k + 0.5) * F(k + 1.5) * F(m + 0.5) * F(m + 1.5)) * cnm) * zn * zm).astype(F)
            sn = (sn + sm).astype(F)
        out = (out + sn).astype(F)
    return np.where(zero, F(1.0), out).astype(F)


# ------------------------------------------------------------------------------------------------ Brosa modes
@lru_cache(maxsize=64)
def _table(kind: str, sym: str, ext: str):
    """Rows (A, values...) of structure/fission/brosa/<kind>/<sym><ext>, or None when the file is absent."""
    from physics.hf.structure.files import talys_structure_dir

    p = talys_structure_dir() / "fission" / "brosa" / kind / f"{sym}{ext}"
    if not p.is_file():
        return None
    rows = []
    for ln in p.read_text().splitlines():
        w = ln.split()
        if len(w) >= 4:
            rows.append((int(w[1]), tuple(F(float(v)) for v in w[3:])))
    return tuple(rows)


def _index(Z: int, A: int, amassmax: int):
    """brosafy.f90's noff / index1 / index2 (the literal loop, `cycle` and all)."""
    noff = [0, 0, 2, 4, 6, 8, 11, 14, 0] if Z < 94 else [0, 0, 2, 4, 6, 8, 10, 0, 0]  # 1-based, noff(8) = 0
    numoff = 7 if Z < 94 else 6
    amassar = [0] + [amassmax - noff[k] for k in range(1, numoff + 1)]
    massdif = amassmax - A
    index1 = index2 = None
    for k in range(1, numoff + 1):
        if noff[k] <= massdif <= noff[k + 1]:
            if massdif == noff[k]:
                index1, index2 = k, -1
            elif massdif == noff[k + 1]:
                index1, index2 = k + 1, -1
            else:
                index1, index2 = k, k + 1
            continue
        if massdif > noff[numoff]:
            index1, index2 = numoff, -1
        elif massdif < noff[1]:
            index1, index2 = 1, -1
    if index1 is None:
        raise RuntimeError(f"brosafy: no Brosa mass index for Z={Z} A={A} (TALYS leaves it undefined)")
    return noff, amassar, index1, index2


def brosafy(Z: int, A: int, excfis, ffevap: bool, ign, dens):
    """Fission fragment yields of the three Brosa modes at excitation `excfis` of nucleus (Z, A): (disa, disacor, disaz,
    disazcor) over A (0..NUMMASS) and (A, Z). `ign(E)` is Ignatyuk's a(E) of the nucleus (array in, array out),
    `dens(E)` its density(E, J=0, parity +, ibar 0, ldmodel 1) in double precision.

    TALYS: brosafy.f90:1 (brosafy)
    Test: tests/hf/test_kwcov_b14.py
    """
    from physics.hf.core.constants import NUC

    excfis = F(excfis)
    zb = max(72, min(Z, 96))
    sym = NUC[zb - 1]
    mn = F(PARMASS_N * AMU)
    mp = F(PARMASS_P * AMU)
    gs = _table("groundstate", sym, ".fis")
    if gs is None:
        raise FileNotFoundError(f"brosa/groundstate/{sym}.fis (TALYS stops)")
    amassmax = gs[0][0]
    noff, amassar, index1, index2 = _index(Z, A, amassmax)
    bindgs = np.zeros((10, 3), dtype=F)
    i = k = 1
    for am, v in gs:
        if am == amassar[index1]:
            if i <= 9:
                bindgs[i, 1] = abs(v[0])
            i += 1
        elif index2 != -1 and am == amassar[index2]:
            if k <= 9:
                bindgs[k, 2] = abs(v[0])
            k += 1
    modes = []
    store = {}
    for iloop, ext in ((1, ".sl"), (2, ".st"), (3, ".st2")):
        bf = np.zeros(11, dtype=F)
        hw = np.zeros(11, dtype=F)
        bfi = np.zeros((10, 3), dtype=F)
        hwi = np.zeros((10, 3), dtype=F)
        bar_rows = _table("barrier", sym, ext)
        if bar_rows is not None:
            i = k = 1
            for am, v in bar_rows:
                bar, width = v[0], v[1]
                if am == amassar[index1]:
                    rmass = F(F(F(1.0) / F(CLIGHT * CLIGHT)) * F(F(Z) * mp + F(A - Z) * mn - bindgs[1, 1]))
                    if i <= 9:
                        bfi[i, 1] = bar
                        hwi[i, 1] = F(HBAR * math.sqrt(float(width) * 1.0e30 / float(rmass)))
                    i += 1
                if index2 != -1 and am == amassar[index2]:
                    rmass = F(F(F(1.0) / F(CLIGHT * CLIGHT)) * F(F(Z) * mp + F(A - Z) * mn - bindgs[1, 2]))
                    if k <= 9:
                        bfi[k, 2] = bar
                        hwi[k, 2] = F(HBAR * math.sqrt(float(width) * 1.0e30 / float(rmass)))
                    k += 1
        numtemp = 1
        if index2 == -1:
            for k in range(1, 10):
                if bfi[k, 1] != 0:
                    bf[k], hw[k], numtemp = bfi[k, 1], hwi[k, 1], k
        elif abs(noff[index1] - noff[index2]) == 3:
            md = F(abs(amassar[index1] - A))
            for k in range(1, 10):
                if bfi[k, 1] != 0 and bfi[k, 2] != 0:
                    bf[k] = F(bfi[k, 1] + F(md / F(3.0)) * (bfi[k, 2] - bfi[k, 1]))
                    hw[k] = F(hwi[k, 1] + F(md / F(3.0)) * (hwi[k, 2] - hwi[k, 1]))
                    numtemp = k
        else:
            for k in range(1, 10):
                if bfi[k, 1] != 0 and bfi[k, 2] != 0:
                    bf[k] = F(F(0.5) * (bfi[k, 1] + bfi[k, 2]))
                    hw[k] = F(F(0.5) * (hwi[k, 1] + hwi[k, 2]))
                    numtemp = k
        if iloop == 2:
            bf[numtemp + 1], hw[numtemp + 1] = store["bf_sl"][numtemp + 1], store["hw_sl"][numtemp + 1]
            numtemp += 1
        if iloop == 3:
            bf[numtemp + 1], hw[numtemp + 1] = store["bf_st"][numtemp + 1], store["hw_st"][numtemp + 1]
            numtemp += 1
        tmpmax = TEMPS[numtemp - 1]
        if bf[1] == 0:
            numtemp = 9
        bfs = spline(TEMPS, bf[1:10], numtemp)
        hws = spline(TEMPS, hw[1:10], numtemp)
        ald = F(ign(excfis))
        tmp = F(math.sqrt(F(excfis / ald)))
        if tmp < tmpmax and bf[1] != 0.0:
            trcof = _trans(excfis, bf[1:10], bfs, hw[1:10], hws, numtemp, ign, dens)
        else:
            trcof = 0.0
        key = {1: "sl", 2: "st", 3: "st2"}[iloop]
        sbf = np.zeros(11, dtype=F)
        shw = np.zeros(11, dtype=F)
        sbf[1:numtemp + 1] = bf[1:numtemp + 1]
        shw[1:numtemp + 1] = hw[1:numtemp + 1]
        store[f"bf_{key}"], store[f"hw_{key}"] = sbf, shw
        modes.append(dict(t=trcof, numtemp=numtemp, bf=bf[1:10].copy(), bfs=bfs))
    stot = modes[0]["t"] + modes[1]["t"] + modes[2]["t"]
    if stot == 0.0:
        w = [1.0, 0.0, 0.0]
    else:
        w = [m["t"] / stot for m in modes]
    disa = np.zeros(NUMMASS + 1, dtype=F)
    disacor = np.zeros(NUMMASS + 1, dtype=F)
    disaz = np.zeros((NUMMASS + 1, NUMELEM + 1), dtype=F)
    disazcor = np.zeros((NUMMASS + 1, NUMELEM + 1), dtype=F)
    neckprev = {}
    pres = {}
    for iloop, ext, crel in ((1, ".sl", F(0.1)), (2, ".st", F(0.3)), (3, ".st2", F(0.3))):
        m = modes[iloop - 1]
        numtemp, bf, bfs = m["numtemp"], m["bf"], m["bfs"]
        dont = w[iloop - 1] == 0.0
        hmneck = np.zeros(10, dtype=F)
        elneck = np.zeros(10, dtype=F)
        eneck = np.zeros(10, dtype=F)
        if iloop >= 2:  # the extension point takes the previous mode's values (brosafy.f90 neck loop)
            prev = neckprev[iloop - 1]
            hmneck[numtemp], elneck[numtemp], eneck[numtemp] = (prev[0][numtemp], prev[1][numtemp],
                                                                 prev[2][numtemp])
        fm = fmc = fz = fzc = None
        if not dont:
            rows = _table("prescission", sym, ext)
            if rows is None:
                raise FileNotFoundError(f"brosa/prescission/{sym}{ext} (TALYS stops)")
            hi = np.zeros((10, 3), dtype=F)
            eli = np.zeros((10, 3), dtype=F)
            Ei = np.zeros((10, 3), dtype=F)
            i = k = 1
            for am, v in rows:
                hm, elsc, bindsc = v[0], v[1], v[2]
                if am == amassar[index1]:
                    if i <= 9:
                        hi[i, 1], eli[i, 1], Ei[i, 1] = hm, elsc, F(abs(bindsc) - bindgs[i, 1])
                    i += 1
                if index2 != -1 and am == amassar[index2]:
                    if k <= 9:
                        hi[k, 2], eli[k, 2], Ei[k, 2] = hm, elsc, F(abs(bindsc) - bindgs[k, 2])
                    k += 1
            if index2 == -1:
                for k in range(1, 10):
                    if hi[k, 1] != 0:
                        hmneck[k] = F(F(hi[k, 1] * F(A)) / F(amassar[index1]))
                        elneck[k], eneck[k] = eli[k, 1], Ei[k, 1]
            elif abs(noff[index1] - noff[index2]) == 3:
                md = F(abs(amassar[index1] - A))
                for k in range(1, 10):
                    if hi[k, 1] != 0 and hi[k, 2] != 0:
                        f3 = F(md / F(3.0))
                        hmneck[k] = F(hi[k, 1] + f3 * (hi[k, 2] - hi[k, 1]))
                        elneck[k] = F(eli[k, 1] + f3 * (eli[k, 2] - eli[k, 1]))
                        eneck[k] = F(Ei[k, 1] + f3 * (Ei[k, 2] - Ei[k, 1]))
            else:
                for k in range(1, 10):
                    if hi[k, 1] != 0 and hi[k, 2] != 0:
                        hmneck[k] = F(F(0.5) * (hi[k, 1] + hi[k, 2]))
                        elneck[k] = F(F(0.5) * (eli[k, 1] + eli[k, 2]))
                        eneck[k] = F(F(0.5) * (Ei[k, 1] + Ei[k, 2]))
            hms = spline(TEMPS, hmneck[1:10], numtemp)
            els = spline(TEMPS, elneck[1:10], numtemp)
            Es = spline(TEMPS, eneck[1:10], numtemp)
            ald = F(ign(excfis))
            tmp = F(math.sqrt(F(excfis / ald)))
            ET = splint(TEMPS, eneck[1:10], Es, numtemp, tmp)
            BFT = splint(TEMPS, bf, bfs, numtemp, tmp)
            if excfis > BFT:
                edefo = F(F(ET + BFT) + excfis - BFT)
                if ET <= 0.0:
                    edefo = excfis
                tmp = F(math.sqrt(F(edefo / F(ign(edefo)))))
                ET = splint(TEMPS, eneck[1:10], Es, numtemp, tmp)
                edefo = F(F(ET + BFT) + excfis - BFT)
                if ET <= 0.0:
                    edefo = excfis
            else:
                edefo = F(ET + excfis)
                if ET <= 0.0:
                    edefo = excfis
                tmp = F(math.sqrt(F(edefo / F(ign(edefo)))))
                ET = splint(TEMPS, eneck[1:10], Es, numtemp, tmp)
                edefo = F(ET + excfis)
                if ET <= 0.0:
                    edefo = excfis
            tmp = F(math.sqrt(F(edefo / F(ign(edefo)))))
            call = False
            if tmp > TEMPS[numtemp - 1]:
                tmp = F(math.sqrt(F(excfis / F(ign(excfis)))))
                call = tmp < TEMPS[numtemp - 1]
            else:
                call = True
            if call:
                hmt = splint(TEMPS, hmneck[1:10], hms, numtemp, tmp)
                elt = splint(TEMPS, elneck[1:10], els, numtemp, tmp)
                fm, fmc, fz, fzc = neck(Z, A, hmt, edefo, elt, crel, ffevap, ign)
        neckprev[iloop] = (hmneck, elneck, eneck)
        pres[iloop] = (fm, fmc, fz, fzc)
    for iloop in (1, 2, 3):
        fm, fmc, fz, fzc = pres[iloop]
        if fm is None:
            continue
        wt = F(w[iloop - 1])
        disa += (fm * wt).astype(F)
        disaz += (fz * wt).astype(F)
        if ffevap:
            disacor += (fmc * wt).astype(F)
            disazcor += (fzc * wt).astype(F)
    return disa, disacor, disaz, disazcor


def _trans(excfis, bf, bfs, hw, hws, numtemp: int, ign, dens) -> float:
    """Transmission of one Brosa mode, trans.f90 + trapzd.f90 (snew reset at entry, as TALYS) + funcfismode.f90.

    TALYS: trans.f90:1 (trans), trapzd.f90:1 (trapzd), funcfismode.f90:1 (funcfismode)
    Test: tests/hf/test_kwcov_b14.py
    """

    def funcfismode(ep: np.ndarray) -> np.ndarray:
        ep = np.asarray(ep, dtype=F)
        ald = np.asarray(ign(ep), dtype=F)
        with np.errstate(all="ignore"):
            tmp = np.sqrt(ep / ald).astype(F)
            bft = splint(TEMPS, bf, bfs, numtemp, tmp)
            hwt = splint(TEMPS, hw, hws, numtemp, tmp)
            expo = (F(2.0) * PI * (bft + ep - excfis) / hwt).astype(F).astype(np.float64)
            out = np.where(expo <= 80.0, 1.0 / (1.0 + np.exp(np.minimum(expo, 80.0))),
                           math.exp(-80.0) / (math.exp(-80.0) + np.exp(np.minimum(expo - 80.0, 700.0))))
        pos = ep > 0
        if pos.any():
            out = out.copy()
            out[pos] = out[pos] * np.asarray(dens(ep[pos]), dtype=np.float64)
        return out

    xa, xb = F(0.0), F(excfis)
    if excfis == 0:
        return float(funcfismode(np.array([0.0], dtype=F))[0])

    def trapzd(nk: int) -> float:
        if nk == 1:
            v = funcfismode(np.array([xa, xb], dtype=F))
            return 0.5 * float(F(xb - xa)) * (v[0] + v[1])
        it = 2 ** (nk - 2)
        tnm = float(it)
        dl = F((float(xb) - float(xa)) / tnm)
        xs = np.empty(it, dtype=F)
        x = F(xa + F(0.5) * dl)
        for j in range(it):
            xs[j] = x
            x = F(x + dl)
        vals = funcfismode(xs)
        sm = 0.0
        for v in vals:
            sm += float(v)
        return 0.5 * (0.0 + float(F(xb - xa)) * sm / tnm)

    snew, sold = 10.0, 1.0
    icount = i = 0
    while True:
        with np.errstate(all="ignore"):
            r = abs(np.float64(snew) / np.float64(sold))
        if r <= 0.99 or r >= 1.01:
            sold = snew
            i += 1
            if i > 10:
                break
            snew = trapzd(i)
        else:
            icount += 1
            if icount == 2:
                break
            sold = snew
            i += 1
            if i > 10:
                break
            snew = trapzd(i)
    return snew


# ------------------------------------------------------------------------------------------------ massdis
def _ld_funcs(cas, Z: int, A: int):
    """(ign, dens) of nucleus (Z, A) on this run: Ignatyuk a(E) (ibar 0) and density(E, J=0, +, ibar 0, ldmodel 1)."""
    import torch

    from physics.hf.density.models import density
    from physics.hf.density.parameters import ignatyuk

    ld = cas.ld_of(Z, A)
    if isinstance(ld, tuple):
        ld = ld[0]

    def ign(e):
        e64 = np.atleast_1d(np.asarray(e, dtype=np.float64))
        v = ignatyuk(ld, torch.as_tensor(e64, dtype=torch.float64)).detach().numpy().astype(F)
        return v if np.ndim(e) else F(v[0])

    def dens(e):
        e64 = torch.as_tensor(np.asarray(e, dtype=np.float64), dtype=torch.float64)
        j = torch.zeros_like(e64)
        return density(ld, e64, j, 1, 0, 1).detach().numpy().astype(np.float64)

    return ign, dens


def massdis(cas, st, etot_mev: float, mres, s: dict) -> dict:
    """Fission fragment / product cross sections and yields of one incident energy (fymodel 1).

    TALYS: massdis.f90:1 (massdis) lines 230-327 (loop, Brosa branch), 731-776 (normalisation to 2)
    Test: tests/hf/test_kwcov_b14.py
    """
    Zt, At = s["Ztarget"], s["Atarget"]
    xsApre = np.zeros(NUMMASS + 1, dtype=F)
    xsApost = np.zeros(NUMMASS + 1, dtype=F)
    xsZApre = np.zeros((NUMELEM + 1, NUMNEU + 1), dtype=F)
    xsZApost = np.zeros((NUMELEM + 1, NUMNEU + 1), dtype=F)
    feeds = {} if mres is None else mres.xsfeed_mb
    xsfistot = F(sum(float(x.get(-1, 0.0)) for x in feeds.values()))
    fpeps = F(F(s["Rfiseps"]) * xsfistot)
    out = {"fpeps": float(fpeps), "xsfistot": float(xsfistot)}
    if fpeps == 0.0 or mres is None:
        out.update(_normalise(xsApre, xsApost, xsZApre, xsZApost, Zt, At))
        return out
    for key in sorted(feeds, key=lambda k: (k[0], k[1])):
        if not float(feeds[key].get(-1, 0.0)) > fpeps:
            continue
        if key != (0, 0) and key not in mres.decayed:
            continue
        sp = st.spec.get(key)
        if sp is None:
            continue
        Z, A = cas.zn(*key)
        ign, dens = _ld_funcs(cas, Z, A)
        maxex = int(sp.maxex)
        ex = np.asarray(sp.ex_mev[: maxex + 1], dtype=np.float64).astype(F)
        ff = mres.fisfeedex_mb.get(key, {})
        nexend = maxex + 1 if key == (0, 0) else maxex
        fisepsA = F(fpeps / F(max(3 * maxex, 1)))
        iskip, istep = 0, 4
        excfis = F(0.0)
        for nex in range(nexend, -1, -1):
            if key == (0, 0) and nex == maxex + 1:
                excfis = F(etot_mev)
                partfisxs = F(ff.get(maxex + 1, 0.0))
            else:
                if iskip % istep != 0:
                    iskip += 1
                    continue
                if nex - istep + 1 < 0:
                    continue
                if ex[nex - istep + 1] >= 30.0:
                    partfisxs = F(0.0)
                    for i in range(istep):
                        partfisxs = F(partfisxs + F(ff.get(nex - i, 0.0)))
                    if partfisxs != 0:
                        excfis = F(0.0)
                        for i in range(istep):
                            excfis = F(excfis + F(ff.get(nex - i, 0.0)) * ex[nex - i])
                        excfis = F(excfis / partfisxs)
                    iskip = 1
                else:
                    excfis = ex[nex]
                    partfisxs = F(ff.get(nex, 0.0))
            if partfisxs > fisepsA:
                disa, disacor, disaz, disazcor = brosafy(Z, A, excfis, s["ffevap"], ign, dens)
                term = F(F(0.5) * partfisxs)
                xsApre[1:A + 1] += (term * disa[1:A + 1]).astype(F)
                xsApost[1:A + 1] += (term * disacor[1:A + 1]).astype(F)
                for iz in range(1, Z + 1):
                    ias = np.arange(max(iz + 1, 1), A + 1)
                    ins = ias - iz
                    m = (ins >= 1) & (ins <= NUMNEU)
                    ias, ins = ias[m], ins[m]
                    xsZApre[iz, ins] += (term * disaz[ias, iz]).astype(F)
                    xsZApost[iz, ins] += (term * disazcor[ias, iz]).astype(F)
    out.update(_normalise(xsApre, xsApost, xsZApre, xsZApost, Zt, At))
    return out


def _normalise(xsApre, xsApost, xsZApre, xsZApost, Zt: int, At: int) -> dict:
    """massdis.f90:731-776: yields per (Z, A) normalised to 2, summed per A; totals."""
    sumpre = F(np.cumsum(xsApre[1:At + 1], dtype=F)[-1]) if At else F(0.0)
    sumpost = F(np.cumsum(xsApost[1:At + 1], dtype=F)[-1]) if At else F(0.0)
    yieldZApre = np.zeros_like(xsZApre)
    yieldZApost = np.zeros_like(xsZApost)
    yieldApre = np.zeros(NUMMASS + 1, dtype=F)
    yieldApost = np.zeros(NUMMASS + 1, dtype=F)
    tot = np.zeros(4, dtype=F)  # yieldtotpost, yieldtotpre, xstotpost, xstotpre
    for iz in range(1, Zt + 1):
        for ia in range(iz + 1, At + 1):
            inn = ia - iz
            if iz > NUMELEM or inn > NUMNEU:
                continue
            if xsZApre[iz, inn] == 0.0:
                continue
            if sumpre > 0:
                yieldZApre[iz, inn] = F(F(2.0) * xsZApre[iz, inn] / sumpre)
            yieldApre[ia] = F(yieldApre[ia] + yieldZApre[iz, inn])
            tot[1] = F(tot[1] + yieldZApre[iz, inn])
            tot[3] = F(tot[3] + xsZApre[iz, inn])
            if sumpost > 0:
                yieldZApost[iz, inn] = F(F(2.0) * xsZApost[iz, inn] / sumpost)
            yieldApost[ia] = F(yieldApost[ia] + yieldZApost[iz, inn])
            tot[0] = F(tot[0] + yieldZApost[iz, inn])
            tot[2] = F(tot[2] + xsZApost[iz, inn])
    return {"xsApre": xsApre, "xsApost": xsApost, "xsZApre": xsZApre, "xsZApost": xsZApost, "yieldApre": yieldApre,
            "yieldApost": yieldApost, "yieldZApre": yieldZApre, "yieldZApost": yieldZApost, "tot": tot}


def record(cas, st, e_inc_mev: float, etot_mev: float, mres) -> None:
    """One kept energy: massdis on the cascade result (engine_c.cases, next to fisobs.record).

    TALYS: talysreaction.f90:189-191 (massdis, massdisout per incident energy)
    Test: tests/hf/test_kwcov_b14.py
    """
    if _SET is None:
        return
    r = massdis(cas, st, etot_mev, mres, _SET)
    r["E"] = float(e_inc_mev)
    _REC.append(r)


# ------------------------------------------------------------------------------------------------ output
def estring(e: float) -> str:
    """TALYS's energy part of yieldA<E>.fis: f8.3 with the integer part as i4.4, es8.2 below 1 keV.

    TALYS: massdisout.f90:94-100
    Test: tests/hf/test_kwcov_b14.py
    """
    if e < 0.001:
        return f"{e:.2E}"
    s = f"{e:8.3f}"
    return f"{int(e):04d}" + s[4:]


def build(rec: list, s: dict) -> dict:
    """massdisout.f90's files of the recorded run, {file name: {column: ndarray}}.

    TALYS: massdisout.f90:1 (massdisout)
    Test: tests/hf/test_kwcov_b14.py
    """
    Zt, At = s["Ztarget"], s["Atarget"]
    Ninit = s["Ainit"] - s["Zinit"]
    out: dict = {}
    E = np.array([r["E"] for r in rec])
    C = len(rec)
    fpz: dict = {}
    fpa: dict = {}
    for c, r in enumerate(rec):
        es = estring(r["E"])
        A = np.arange(1, At + 1)
        out[f"yieldA{es}.fis"] = {"A": A, "FP_yield": r["yieldApost"][1:At + 1].astype(float),
                                  "FF_yield": r["yieldApre"][1:At + 1].astype(float),
                                  "FP_xs": r["xsApost"][1:At + 1].astype(float),
                                  "FF_xs": r["xsApre"][1:At + 1].astype(float), "Tot": r["tot"].astype(float)}
        fpeps = F(r["fpeps"])
        rows = []
        for ia in range(1, At + 1):
            for iz in range(1, Zt + 1):
                inn = ia - iz
                if inn < 1 or inn > Ninit:
                    continue
                pre, post = r["xsZApre"][iz, inn], r["xsZApost"][iz, inn]
                if (pre <= fpeps and post <= fpeps) and (iz, ia) not in fpz:
                    continue
                fpz.setdefault((iz, ia), np.zeros((C, 4)))
                fpz[(iz, ia)][c] = (r["yieldZApost"][iz, inn], r["yieldZApre"][iz, inn], post, pre)
                if pre >= fpeps and post >= fpeps:
                    rows.append((iz, ia, -1, r["yieldZApost"][iz, inn], r["yieldZApre"][iz, inn], post, pre))
            if r["xsApre"][ia] < fpeps and r["xsApost"][ia] < fpeps and ia not in fpa:
                continue
            fpa.setdefault(ia, np.zeros((C, 4)))
            fpa[ia][c] = (r["yieldApost"][ia], r["yieldApre"][ia], r["xsApost"][ia], r["xsApre"][ia])
        rows.sort(key=lambda x: (x[1], x[0]))
        arr = np.array(rows, dtype=float).reshape(-1, 7)
        out[f"yieldZA{es}.fis"] = {k: arr[:, j] for j, k in enumerate(
            ("Z", "A", "isomer", "FP_yield", "FF_yield", "FP_xs", "FF_xs"))}
    for (iz, ia), v in sorted(fpz.items(), key=lambda x: (x[0][1], x[0][0])):
        out[f"fp{iz:03d}{ia:03d}.tot"] = {"E": E, "FP_yield": v[:, 0], "FF_yield": v[:, 1], "FP_xs": v[:, 2],
                                          "FF_xs": v[:, 3]}
        out[f"rp{iz:03d}{ia:03d}.tot"] = {"E": E, "FP_xs": v[:, 2]}
    for ia, v in sorted(fpa.items()):
        out[f"fp{ia:03d}.tot"] = {"E": E, "FP_yield": v[:, 0], "FF_yield": v[:, 1], "FP_xs": v[:, 2],
                                  "FF_xs": v[:, 3]}
    return out


def add_to_results(res, injection=None):
    """End of engine_c.run: the yield files into Results.fission_yields. Unchanged without `massdis y`.

    TALYS: massdisout.f90:1 (massdisout)
    Test: tests/hf/test_kwcov_b14.py
    """
    global _SET
    if _SET is None:
        return res
    from dataclasses import replace

    try:
        if len(_REC) != res.n:
            raise RuntimeError(f"FISYIELD: {len(_REC)} recorded energies for {res.n} results")
        res = replace(res, fission_yields=build(_REC, _SET))
    finally:
        _SET = None
        _REC.clear()
    return res
