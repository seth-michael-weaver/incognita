"""Alpha production that an evaluation lumps into MT 5, so that (n,alpha) and He-4 production are derived the same way
for every evaluated file (2026-11-06).

Why: an ENDF-6 evaluation may give the (n,alpha) cross section explicitly (MT 107, or its levels MT 800-849) or leave part
of it inside MT 5 ("anything else"), whose products are listed in MF6 (or MF9 / MF10) of MT 5. ENDF/B-VIII.1 does this for
Fe-54/56/57/58 and others: its Fe-54 MT 107 is 4 mb at 14 MeV against about 100 mb measured, the rest of the alpha channel
sits in MT 5. Scoring MT 107 alone then compares a partial channel with the measured total and misranks the library.

The rule, applied identically to every library (ours included):
  (n,alpha)   = MT 107 (else the sum of MT 800-849) + sigma_5(E) * Y5(residual Z-2, A-3; E)
  He-4 prod.  = sum over explicit MTs of (alpha multiplicity x sigma_MT)        (HE_MULT below)
                + sigma_5(E) * Y5(He-4; E)
where Y5(ZAP; E) is the MT 5 product yield of ZAP: MF6 MT 5 (the yield TAB1 of every subsection with that ZAP, all
isomer levels LIP summed), else MF10 MT 5 (production cross sections of that ZAP divided by sigma_5), else MF9 MT 5
(multiplicities). If sigma_5 > 0 but the file gives no MT 5 product data, the derived value is UNDEFINED and that
library's row is "comparator incomplete" (not covered) instead of silently taking MT 107 alone, unless sigma_5 itself (an
upper bound of the unread alpha part) is below 1 % of the derived value at the row (for a spectrum average: of the folded
values).

The derived MT 5 parts are stored as two pseudo-MTs on the library grid (values in barns, 0 where nothing is produced):
  MT5_NA = 905   sigma_5 * Y5(Z-2, A-3)     (the (n,alpha) residual made inside MT 5)
  MT5_HE = 906   sigma_5 * Y5(He-4)         (alphas emitted inside MT 5)
Present (possibly all zero) = the file's MT 5 products were read; absent with sigma_5 > 0 somewhere = incomplete.
"""
from __future__ import annotations

import re

import numpy as np

MT5_NA, MT5_HE = 905, 906
# alpha multiplicity of every ENDF-6 neutron reaction MT that emits alphas (ENDF-102, appendix B); MT 800-849 are levels of 107
HE_MULT = {22: 1, 23: 3, 24: 1, 25: 1, 29: 2, 30: 2, 35: 2, 36: 2, 45: 1, 107: 1, 108: 2, 109: 3, 112: 1, 113: 2, 114: 2,
           117: 1, 155: 1, 158: 1, 159: 1, 165: 1, 166: 1, 167: 1, 168: 1, 180: 2, 181: 1, 189: 1, 193: 1, 195: 2, 196: 1,
           199: 1}
NA_LEVELS = range(800, 850)
WANT_MTS = sorted({5, 107, *HE_MULT, *NA_LEVELS})


def _f(s: str) -> float:
    s = s.replace(' ', '')     # also "2.50550+ 4" (a blank inside the exponent; data/ingest/endf.endf_float)
    if not s:
        return 0.0
    m = re.match(r'^([+-]?[\d.]+)([+-]\d+)$', s)
    return float(f'{m.group(1)}e{m.group(2)}') if m else float(s)


def _i(s: str) -> int:
    s = s.strip()
    return int(float(s)) if s else 0


def section_lines(text: str, mf: int, mt: int) -> list[str]:
    """The data lines (HEAD first, SEND excluded) of one section of one ENDF-6 material text."""
    tag = f'{mf:2d}{mt:3d}'
    return [L for L in text.splitlines() if len(L) >= 75 and L[70:75] == tag]


class _Reader:
    def __init__(self, lines):
        self.L, self.i = lines, 0

    def cont(self):
        L = self.L[self.i]; self.i += 1
        return _f(L[0:11]), _f(L[11:22]), _i(L[22:33]), _i(L[33:44]), _i(L[44:55]), _i(L[55:66])

    def values(self, n):
        out = []
        while len(out) < n:
            L = self.L[self.i]; self.i += 1
            out += [_f(L[k:k + 11]) for k in range(0, 66, 11)]
        return out[:n]

    def tab1(self):
        c1, c2, l1, l2, nr, npt = self.cont()
        ints = np.array(self.values(2 * nr), int).reshape(-1, 2)
        xy = np.array(self.values(2 * npt), float).reshape(-1, 2)
        return (c1, c2, l1, l2), xy[:, 0], xy[:, 1], ints[:, 0], ints[:, 1]

    def tab2(self):
        c1, c2, l1, l2, nr, nz = self.cont()
        self.values(2 * nr)
        return nz

    def list_(self):
        c1, c2, l1, l2, npl, n2 = self.cont()
        self.values(npl)


def _skip_law(r: _Reader, law: int):
    """Skip the distribution block of one MF6 subsection (ENDF-6 formats manual, chapter 6)."""
    if law in (0, 3, 4):
        return
    if law in (1, 2, 5):
        for _ in range(r.tab2()):
            r.list_()
    elif law == 6:
        r.cont()
    elif law == 7:
        for _ in range(r.tab2()):
            for _ in range(r.tab2()):
                r.tab1()
    elif law == 8:
        r.tab1()
    else:
        raise ValueError(f'MF6 LAW {law} not handled')


def interp_tab(x, y, nbt, law, e):
    """ENDF TAB1 interpolation (laws 1-5) at e; 0 outside the table."""
    e = np.asarray(e, float); out = np.zeros_like(e)
    lo = 0
    for hi, L in zip(nbt, law):
        xs, ys = x[lo:hi], y[lo:hi]
        if len(xs) >= 2:
            m = (e >= xs[0]) & (e <= xs[-1])
            if m.any():
                if L == 1:
                    out[m] = ys[np.clip(np.searchsorted(xs, e[m], 'right') - 1, 0, len(xs) - 1)]
                elif L == 3:
                    out[m] = np.interp(np.log(e[m]), np.log(np.maximum(xs, 1e-300)), ys)
                elif L == 4:
                    out[m] = np.exp(np.interp(e[m], xs, np.log(np.maximum(ys, 1e-300))))
                elif L == 5:
                    out[m] = np.exp(np.interp(np.log(e[m]), np.log(np.maximum(xs, 1e-300)), np.log(np.maximum(ys, 1e-300))))
                else:
                    out[m] = np.interp(e[m], xs, ys)
        lo = hi - 1
    return out


def mt5_yields(text: str, zaps, grid) -> dict | None:
    """{ZAP: yield of ZAP inside MT 5 on `grid`} from MF6 (else MF9) of MT 5; None if the file has neither.
    MF10 (production cross sections) is returned separately by mt5_production."""
    zaps = {int(z) for z in zaps}
    out = {z: np.zeros(len(grid)) for z in zaps}
    lines = section_lines(text, 6, 5)
    if lines:
        r = _Reader(lines)
        za, awr, _, lct, nk, _ = r.cont()
        for _ in range(nk):
            (zap, awp, lip, law), x, y, nbt, ilaw = r.tab1()
            if int(round(zap)) in zaps:
                out[int(round(zap))] += interp_tab(x, y, nbt, ilaw, grid)
            _skip_law(r, law)
        return out
    lines = section_lines(text, 9, 5)
    if lines:
        r = _Reader(lines)
        za, awr, lis, _, ns, _ = r.cont()
        for _ in range(ns):
            (qm, qi, izap, lfs), x, y, nbt, ilaw = r.tab1()
            if izap in zaps:
                out[izap] += interp_tab(x, y, nbt, ilaw, grid)
        return out
    return None


def mt5_production(text: str, zaps, grid) -> dict | None:
    """{ZAP: production cross section (b) inside MT 5 on `grid`} from MF10 MT 5; None if absent."""
    lines = section_lines(text, 10, 5)
    if not lines:
        return None
    zaps = {int(z) for z in zaps}
    out = {z: np.zeros(len(grid)) for z in zaps}
    r = _Reader(lines)
    za, awr, lis, _, ns, _ = r.cont()
    for _ in range(ns):
        (qm, qi, izap, lfs), x, y, nbt, ilaw = r.tab1()
        if izap in zaps:
            out[izap] += interp_tab(x, y, nbt, ilaw, grid)
    return out


def mt5_alpha_parts(text: str, z: int, a: int, sigma5, grid) -> dict:
    """{MT5_NA: sigma_5 * Y(Z-2, A-3), MT5_HE: sigma_5 * Y(He-4)} on `grid` (barns), given sigma_5 on the same grid
    (from the file's MF3, or its RECONR / PENDF curve). {} if sigma_5 is zero everywhere (nothing lumped) AND the file has
    no MT 5 products; if sigma_5 > 0 and the file gives no MT 5 products, also {} (the caller marks rows incomplete)."""
    s5 = np.asarray(sigma5, float)
    res = 1000 * (z - 2) + (a - 3)
    y = mt5_yields(text, (res, 2004), grid)
    if y is not None:
        return {MT5_NA: s5 * y[res], MT5_HE: s5 * y[2004]}
    p = mt5_production(text, (res, 2004), grid)
    if p is not None:
        return {MT5_NA: p[res], MT5_HE: p[2004]}
    if not np.any(s5 > 0):
        z0 = np.zeros(len(grid))
        return {MT5_NA: z0, MT5_HE: z0.copy()}
    return {}


TOL = 0.01   # sigma_5 is an upper bound of the alpha part that could not be read; below 1 % of the value it cannot matter
# A file with no explicit (n,alpha) section (MT 107 / 800-849) evaluates the channel only through MT 5; that counts when
# the MT 5 part reaches 1 mb somewhere. A vanishing MT 5 yield (TENDL-2025 U-238: 1e-9 b at 14.5 MeV against 1.5 mb
# measured) means the channel is not evaluated, and the row stays not covered, as it was before the fix.
NA_MIN_MT5_ONLY_B = 1e-3


def na_total(curves: dict):
    """(n,alpha) total on the grid from {mt: values}: MT 107 (else sum of MT 800-849) + MT5_NA.
    Returns (values or None, missing): missing = sigma_5 on the grid (an upper bound of the unread part) when sigma_5 > 0
    somewhere and MT5_NA is absent, else None."""
    base = curves.get(107)
    if base is None:
        lv = [curves[m] for m in NA_LEVELS if m in curves]
        base = np.sum(lv, axis=0) if lv else None
    s5 = curves.get(5)
    part = curves.get(MT5_NA)
    if part is None and s5 is not None and np.any(np.asarray(s5) > 0):
        return base, np.asarray(s5, float)
    if base is None and (part is None or np.max(part) < NA_MIN_MT5_ONLY_B):
        return None, None             # the file does not evaluate (n,alpha) for this nucleus: not covered (as before)
    v = (np.zeros_like(part) if base is None else np.asarray(base, float)) + (0 if part is None else part)
    return v, None


def he_total(curves: dict):
    """He-4 production on the grid: sum of multiplicity x sigma_MT over HE_MULT (MT 107, else its levels MT 800-849)
    + MT5_HE. Same `missing` rule."""
    have = [m for m in HE_MULT if m in curves]
    lv = [m for m in NA_LEVELS if m in curves] if 107 not in curves else []   # (n,a) given only as its levels (as na_total)
    s5 = curves.get(5)
    part = curves.get(MT5_HE)
    if not have and not lv and part is None:
        return None, None
    n = len(next(iter(curves.values())))
    v = np.zeros(n)
    for m in have:
        v = v + HE_MULT[m] * np.asarray(curves[m], float)
    for m in lv:
        v = v + np.asarray(curves[m], float)
    if part is not None:
        return v + part, None
    if s5 is not None and np.any(np.asarray(s5) > 0):
        return v, np.asarray(s5, float)
    return v, None


def is_incomplete(value: float, missing_bound: float, tol: float = TOL) -> bool:
    """Comparator incomplete: the unread MT 5 part (bounded by sigma_5) may exceed tol x the derived value."""
    if not (missing_bound > 0):
        return False
    return not (np.isfinite(value) and value > 0 and missing_bound <= tol * value)


__all__ = ['MT5_NA', 'MT5_HE', 'HE_MULT', 'WANT_MTS', 'mt5_alpha_parts', 'mt5_yields', 'mt5_production', 'na_total',
           'he_total', 'is_incomplete', 'TOL', 'section_lines', 'interp_tab']
