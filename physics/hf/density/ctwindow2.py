"""Incognita extension (CTKINK; not TALYS): `ctwindow2`, the versioned successor of `ctwindow` (CTWFREEZE, frozen for B51).
Keyword `ctwindow2 y` (densitymodel section) or env INCOGNITA_CT_WINDOW2=1; default OFF, and OFF never enters this module.
With both switches on, `ctwindow2` is used and `ctwindow` is ignored.

Physics (same anchor as ctwindow): below the matching energy Ex the constant-temperature density
rho_CT = exp((E-E0)/T)/T must reproduce the known, complete discrete levels between E(Nlow) and EP (the highest level of the
engine's list with E <= RIPL-4 Umax); above Ex the Fermi gas applies. A physical level density is continuous in value AND in
log-slope at Ex, so (T, E0, Ex) are solved together:
    1/T         = d ln rho_FG / dE  at Ex        (slope)
    rho_CT(Ex)  = rho_FG(Ex)  ->  E0 = Ex - T ln(T rho_FG(Ex))   (value)
    N_used(Ex)  = NP - Nlow                       (the anchor: levels the USED density puts in [EL, EP])
Why ctwindow has a kink: it re-reads TALYS's FG tables (logrho, temprho on 0.1 MeV) from the record that densitymatch has
ALREADY matched. For ldmodel 1 that record's Fermi gas is not the one used above the new Ex: below the old Exmatch the spin
cutoff is TALYS's interpolation from the discrete value to the matching point (spincut.f90) and the collective enhancement
is off (colenhance.f90), so sigma, K and hence T = temprho(Ex) are those of the OLD join (T 0.3-0.8 % off, rho off). Stock
TALYS builds the tables before any Exmatch is set and has no such kink.
Here rho_FG(E) = Kcoll(E) fermi(E, delta) is evaluated exactly (float64, the port's own ignatyuk/colenhance/fermi/spincut,
the functions densitytot uses above Ex) on a copy of the record with Exmatch = 0, i.e. the pure Fermi-gas branch, which is
what the final record uses at every E > Ex. d ln rho_FG/dE by a 5-point stencil (h = 1e-3 MeV, error ~1e-11). The count
integrates the density actually used: exp(ctable sqrt(E - ptable)) x (CT below Ex, Kcoll x FG above Ex where EP > Ex).
Root search as TALYS matching.f90 / ctwindow: bracket [2.25/a(Exmemp) + P + 0.11, 19 + 300/A], 100 segments, bisection
(here to 1e-9 MeV), of the first two roots the one nearest Exmemp, TALYS's guards (Ex > lower limit, Ex <= 3 Exmemp).
Applies only to ldmodel 1, barrier 0, no ctm table, Umax > 0 and >= 3 levels above Nlow; otherwise, or without a root, the
nucleus keeps densitymatch's values. No fitted number.
Test: tests/hf/test_ctwindow2.py
"""

from __future__ import annotations

import math
import os
from dataclasses import replace

import numpy as np
import torch

from physics.hf.density.ctwindow import _window, ripl_umax  # noqa: F401  (same window as ctwindow)

__all__ = ["enabled", "mode", "anchor", "fg_log", "used_density"]

LAST: dict = {}   # (Z, A) -> anchoring record of the last anchor() call on that nucleus (diagnostics only)
WHY: dict = {}    # (Z, A) -> reason a nucleus was not anchored

_H = 1.0e-3                                                      # stencil step [MeV]
_ST = np.array([-2.0, -1.0, 1.0, 2.0]) * _H
_SW = np.array([1.0, -8.0, 8.0, -1.0]) / (12.0 * _H)
_NS = 200                                                        # Simpson intervals of the count


def enabled(options) -> bool:
    """`ctwindow2 y` on the options, or env INCOGNITA_CT_WINDOW2=1."""
    return bool(getattr(options, "flagctwindow2", False)) or os.environ.get("INCOGNITA_CT_WINDOW2", "0") == "1"


def mode(options):
    """False when ctwindow2 is off, else the no-root rule: "cont" (ARTFIX, keyword `ctwcont y`, default) or "root" (the
    pre-ARTFIX rule, `ctwcont n` or env INCOGNITA_CTW2_CONT=0)."""
    if not enabled(options):
        return False
    on = bool(getattr(options, "flagctwcont", True)) and os.environ.get("INCOGNITA_CTW2_CONT", "1") != "0"
    return "cont" if on else "root"


_GR = 0.5 * (math.sqrt(5.0) - 1.0)


def _least(gb, xs, gs):
    """ARTFIX `ctwcont`: the x of least |g| when g has no sign change on the grid (the count condition solved in the
    least-squares sense). Grid argmin of |g|, then golden section on |g| over the two adjacent segments to 1e-9 MeV, so
    at a root's birth (tangency or bracket edge) the anchor moves continuously onto the root. None if no finite g."""
    a = np.abs(np.asarray(gs, dtype=np.float64))
    if not np.isfinite(a).any():
        return None
    i = int(np.nanargmin(np.where(np.isfinite(a), a, np.nan)))
    lo, hi = float(xs[max(i - 1, 0)]), float(xs[min(i + 1, len(xs) - 1)])

    def f(z):
        v = float(np.abs(gb(np.array([z]))[0]))
        return v if np.isfinite(v) else math.inf

    c, d = hi - _GR * (hi - lo), lo + _GR * (hi - lo)
    fc, fd = f(c), f(d)
    for _ in range(200):
        if hi - lo < 1e-9:
            break
        if fc <= fd:
            hi, d, fd = d, c, fc
            c = hi - _GR * (hi - lo)
            fc = f(c)
        else:
            lo, c, fc = c, d, fd
            d = lo + _GR * (hi - lo)
            fd = f(d)
    x = 0.5 * (lo + hi)
    best = min(((f(x), x), (float(a[i]), float(xs[i]))))   # never worse than the grid point
    return best[1]


def _pure(ld):
    """`ld` with barrier-0 Exmatch = 0: spincut and colenhance on their Fermi-gas branch at every E > 0."""
    X = ld.Exmatch_mev.clone()
    X[0] = torch.as_tensor(0.0, dtype=X.dtype)
    return replace(ld, Exmatch_mev=X)


def fg_log(ld0, E) -> np.ndarray:
    """ln(Kcoll fermi) [ln MeV^-1] at energies E (MeV, array) on the pure-FG record `ld0`: densitytot's ldmodel-1 value above
    Exmatch without the ctable factor (which is common to both sides of the join). NaN where U = E - delta <= 0."""
    from physics.hf.density.models import fermi
    from physics.hf.density.parameters import colenhance, ignatyuk

    x = torch.as_tensor(np.asarray(E, dtype=np.float64).reshape(-1), dtype=torch.float64)
    ald = ignatyuk(ld0, x, 0)
    _, _, K = colenhance(ld0, x, ald, 0)
    f = fermi(ld0, ald, x, ld0.delta_mev[0], 0)
    out = torch.log(K * f).double().numpy()
    out = np.where(x.numpy() - float(ld0.delta_mev[0]) > 0.0, out, np.nan)
    return out.reshape(np.shape(E))


def _fg_point(ld0, x: float) -> tuple[float, float]:
    """(ln rho_FG(x), d ln rho_FG/dE at x)."""
    v = fg_log(ld0, np.concatenate(([x], x + _ST)))
    return float(v[0]), float(np.dot(_SW, v[1:]))


def _simpson(y, a, b):
    n = len(y) - 1
    w = np.ones(n + 1)
    w[1:-1:2] = 4.0
    w[2:-1:2] = 2.0
    return float((w * y).sum()) * (b - a) / n / 3.0


def _ctf(E, ct, pt):
    return np.exp(np.minimum(ct * np.sqrt(np.clip(E - pt, 0.0, None)), 80.0))


def _count(ld0, x, L, T, EL, EP, ct, pt):
    """Levels the USED density (CT below x joined to the FG above x with value and slope continuity) puts in [EL, EP]."""
    rho = math.exp(L)
    b = min(EP, x)
    n = 0.0
    if b > EL or EL == 0.0:
        if ct == 0.0:
            n += T * rho * (math.exp((b - x) / T) - (math.exp((EL - x) / T) if EL != 0.0 else 0.0))
        else:
            E = np.linspace(EL, b, _NS + 1)
            n += rho * _simpson(np.exp((E - x) / T) * _ctf(E, ct, pt), EL, b)
    if EP > x:
        E = np.linspace(x, EP, _NS + 1)
        n += _simpson(np.exp(fg_log(ld0, E)) * _ctf(E, ct, pt), x, EP)
    return n


def _g_batch(ld0, xs, EL, EP, ct, pt, target) -> np.ndarray:
    """SPEEDFIX: `anchor`'s g(x) = count(x) - target at many x in two `fg_log` calls (the stencil at every x, then the
    FG-side count integrands of every x with EP > x as one (n, _NS+1) array). Same arithmetic as `_fg_point` + `_count`
    per x (np.linspace with array ends = per-row linspace; row sums = 1-D sums); NaN where g is."""
    xs = np.asarray(xs, dtype=np.float64).reshape(-1)
    v = fg_log(ld0, xs[:, None] + np.concatenate(([0.0], _ST))[None, :])
    L = v[:, 0]
    d = v[:, 1:] @ _SW
    ok = np.isfinite(L) & np.isfinite(d) & (d > 0.0)
    with np.errstate(all="ignore"):
        T = np.where(ok, 1.0 / np.where(ok, d, 1.0), 1.0)
        rho = np.exp(np.where(ok, L, 0.0))
    n = np.zeros_like(xs)
    w = np.ones(_NS + 1)
    w[1:-1:2] = 4.0
    w[2:-1:2] = 2.0
    b = np.minimum(EP, xs)
    m = ok & ((b > EL) | (EL == 0.0))
    if m.any():
        with np.errstate(all="ignore"):
            if ct == 0.0:
                tail = np.exp((EL - xs[m]) / T[m]) if EL != 0.0 else 0.0
                n[m] += T[m] * rho[m] * (np.exp((b[m] - xs[m]) / T[m]) - tail)
            else:
                E = np.linspace(EL, b[m], _NS + 1, axis=1)
                y = np.exp((E - xs[m][:, None]) / T[m][:, None]) * _ctf(E, ct, pt)
                n[m] += rho[m] * ((w * y).sum(axis=1) * (b[m] - EL) / _NS / 3.0)
    m = ok & (EP > xs)
    if m.any():
        E = np.linspace(xs[m], EP, _NS + 1, axis=1)
        with np.errstate(all="ignore"):
            y = np.exp(fg_log(ld0, E)) * _ctf(E, ct, pt)
        n[m] += (w * y).sum(axis=1) * (EP - xs[m]) / _NS / 3.0
    return np.where(ok, np.minimum(n, 1e30) - target, np.nan)


_DEPTH = 4   # bisection levels evaluated per batch (2**_DEPTH - 1 speculative midpoints)


def _bisect(gb, a, b, ga):
    """`anchor`'s bisection (80 steps max, stop at a non-finite g or hi - lo < 1e-9), walked on speculative batches:
    the midpoint tree of the next `_DEPTH` levels is built with the same 0.5 * (lo + hi) arithmetic and evaluated in one
    `gb` call, then walked exactly as the serial loop would. Returns the root (0.5 * (lo + hi))."""
    lo, hi, flo = a, b, ga
    it = 0
    while True:
        tree = [(lo, hi)]
        nodes = []
        for _lev in range(_DEPTH):
            nxt = []
            for l_, h_ in tree:
                mid = 0.5 * (l_ + h_)
                nodes.append(mid)
                nxt += [(l_, mid), (mid, h_)]
            tree = nxt
        vals = dict(zip(nodes, gb(np.array(nodes))))
        for _lev in range(_DEPTH):
            if it >= 80:
                return 0.5 * (lo + hi)
            it += 1
            mid = 0.5 * (lo + hi)
            fm = vals[mid]
            if not np.isfinite(fm):
                return 0.5 * (lo + hi)
            if flo * fm <= 0:
                hi = mid
            else:
                lo, flo = mid, fm
            if hi - lo < 1e-9:
                return 0.5 * (lo + hi)


def used_density(ld, E) -> np.ndarray:
    """densitytot of barrier 0 at energies E (MeV) for a matched record, float64 (test/diagnostic helper)."""
    from physics.hf.density.models import densitytot

    x = torch.as_tensor(np.asarray(E, dtype=np.float64).reshape(-1), dtype=torch.float64)
    return densitytot(ld, x, 0).double().numpy().reshape(np.shape(E))


def anchor(ld, cont: bool = False):
    """`ld` (already matched by densitymatch) with T, E0, Exmatch of barrier 0 solved jointly on the complete level window
    (value + slope continuity at Ex, window count), or `ld` unchanged where the rule does not apply.
    `cont` (ARTFIX, `ctwcont y`): without a root, or when the root fails TALYS's guards, anchor at the least
    |count - target| on the admissible x (`_least`) instead of keeping densitymatch's values; that on/off switch made
    0.03-0.33 dex steps in knob space (ARTSCAN case 1)."""
    from physics.hf.density import matching as M

    key = (int(ld.Z), int(ld.A))
    try:
        if int(ld.ldmodel) != 1 or ld.has_table(0):
            WHY[key] = "model/table"
            return ld
        win, why = _window(ld)
        if win is None:
            WHY[key] = why
            return ld
        NL, NP, EL, EP, umax, nmax = win
        ct, pt = float(ld.ctable[0]), float(ld.ptable_mev[0])
        if abs(pt) < 1e-10:
            pt = 0.0
        ld0 = _pure(ld)
        A, P = ld.A, float(ld.pair_mev)
        c2 = 2.67 if ld.flagcol else 2.33
        Exmemp = max(c2 + 253.0 / A + P, 0.1)
        ald = float(M.ignatyuk(ld, M._t(Exmemp), 0))
        x1 = max(2.25 / ald + P, 0.0) + 0.11
        x2 = 19.0 + 300.0 / A
        target = NP - NL

        def g(x):
            L, d = _fg_point(ld0, x)
            if not (np.isfinite(L) and np.isfinite(d)) or d <= 0.0:
                return float("nan")
            return min(_count(ld0, x, L, 1.0 / d, EL, EP, ct, pt), 1e30) - target

        xs = np.linspace(x1, x2, 101)
        if os.environ.get("INCOGNITA_CTW2_SERIAL", "0") == "1":   # the pre-SPEEDFIX serial search (A/B only)
            gs = [g(x) for x in xs]
        else:
            gs = list(_g_batch(ld0, xs, EL, EP, ct, pt, target))
        roots = []
        for a, b, ga, gb in zip(xs[:-1], xs[1:], gs[:-1], gs[1:]):
            if np.isfinite(ga) and np.isfinite(gb) and ga * gb <= 0 and not (ga == 0 and gb == 0):
                if os.environ.get("INCOGNITA_CTW2_SERIAL", "0") != "1":
                    roots.append(_bisect(lambda z: _g_batch(ld0, z, EL, EP, ct, pt, target), a, b, ga))
                    continue
                lo, hi, flo = a, b, ga
                for _ in range(80):
                    mid = 0.5 * (lo + hi)
                    fm = g(mid)
                    if not np.isfinite(fm):
                        break
                    if flo * fm <= 0:
                        hi = mid
                    else:
                        lo, flo = mid, fm
                    if hi - lo < 1e-9:
                        break
                roots.append(0.5 * (lo + hi))
        if not roots and cont:
            xl = _least(lambda z: _g_batch(ld0, z, EL, EP, ct, pt, target), xs, gs)
            if xl is not None:
                roots = [xl]
        if not roots:
            WHY[key] = "no_root"
            return ld
        Ex = min(roots[:2], key=lambda x: abs(x - Exmemp))

        def bad(x):
            return x <= max(2.25 / float(M.ignatyuk(ld, M._t(x), 0)) + P, 0.0) + 0.11 or x > 3.0 * Exmemp

        guarded = bad(Ex)
        if guarded and cont:   # ARTFIX: least |g| on the admissible part of the bracket (+ its upper edge 3 Exmemp)
            hb = min(3.0 * Exmemp, x2)
            ad = sorted({float(x) for x in xs if not bad(float(x))} | ({hb} if hb > x1 and not bad(hb) else set()))
            if ad:
                gb = lambda z: _g_batch(ld0, z, EL, EP, ct, pt, target)  # noqa: E731
                xl = _least(gb, np.array(ad), gb(np.array(ad)))
                if xl is not None and not bad(xl):
                    Ex, guarded = xl, False
        if guarded:
            WHY[key] = "guard"
            return ld
        L, d = _fg_point(ld0, Ex)
        T = 1.0 / d
        E0 = Ex - T * math.log(T) - T * L
        LAST[key] = dict(T0=float(ld.T_mev[0]), E00=float(ld.E0_mev[0]), Ex0=float(ld.Exmatch_mev[0]), T=T, E0=E0, Ex=Ex,
                         lnrho=L, NL=NL, NP=NP, EL=EL, EP=EP, umax=umax, nmax_ripl=nmax, ct=ct, pt=pt, nroots=len(roots),
                         EP_above_Ex=bool(EP > Ex), count=_count(ld0, Ex, L, T, EL, EP, ct, pt),
                         least=bool(cont and abs(_count(ld0, Ex, L, T, EL, EP, ct, pt) - target) > 1e-6 * max(target, 1.0)))
        WHY.pop(key, None)
        Tm, Em, Xm = ld.T_mev.clone(), ld.E0_mev.clone(), ld.Exmatch_mev.clone()
        Tm[0] = torch.as_tensor(T, dtype=Tm.dtype)
        Em[0] = torch.as_tensor(E0, dtype=Em.dtype)
        Xm[0] = torch.as_tensor(Ex, dtype=Xm.dtype)
        return replace(ld, T_mev=Tm, E0_mev=Em, Exmatch_mev=Xm)
    except FileNotFoundError:
        raise
    except Exception as e:  # noqa: BLE001 -- keep densitymatch's values, record why
        WHY[key] = f"err:{type(e).__name__}:{e}"
        return ld
