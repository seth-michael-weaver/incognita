"""Incognita extension (CTWFREEZE; not TALYS): constant-temperature level density anchored on the COMPLETE part of each
nucleus's discrete level scheme, matched with TALYS's own branch-A logic (matching.f90 + match.f90). Keyword `ctwindow y`
(densitymodel section) or env INCOGNITA_CT_WINDOW=1; default OFF, and OFF never enters this module.

Physics: below the matching energy Ex the constant-temperature density rho = exp((E-E0)/T)/T must reproduce the known,
complete discrete levels; at Ex it joins the Fermi gas with equal value and equal log-slope (T = temprho(Ex), no kink).
Without ctm tables TALYS takes densitymatch.f90's branch B (T = Tmemp, empirical), so the CT never sees the levels. Here
the window is defined in ENERGY: EL = E(Nlow); EP = the highest level of the engine's own list with E <= Umax, the upper
energy of the complete scheme in RIPL-4 levels/levels-param.data (capped at Ntop). No fitted number.

Match: int_EL^EP rho(Ex) e^{(E-Ex)/T(Ex)} e^{ctable sqrt(E-ptable)} dE = NP - Nlow (the density actually used; with
ctable = 0 this is match.f90), roots on TALYS's matching.f90 bracket [2.25/a(Exmemp)+P+0.11, 19+300/A] (100 segments,
bisection to 1e-5 MeV, of two roots the one nearest Exmemp), TALYS's guards Ex > lower limit and Ex <= 3 Exmemp; then
E0 = Ex - T ln(T rho(Ex)). Only ldmodel 1, barrier 0, no ctm table, Umax > 0 and >= 3 levels above Nlow. Otherwise, or
without a root, the nucleus keeps densitymatch's values (branch B). Numerically identical to the runner-side patch the
CTWIN job registered and ran (development notes, mode "w"; plan d7d37ed, result 8facc1d).

Everything downstream (Py / C / fast / GPU chains) reads T, E0 and Exmatch from the matched `LDNucleus` record, so the
switch acts in one place.
Test: tests/hf/test_ctwindow.py
"""

from __future__ import annotations

import math
import os
from dataclasses import replace
from pathlib import Path

import numpy as np
import torch

__all__ = ["enabled", "anchor", "ripl_umax"]

_U: dict = {}
LAST: dict = {}   # (Z, A) -> anchoring record of the last anchor() call on that nucleus (diagnostics only)
WHY: dict = {}    # (Z, A) -> reason a nucleus was not anchored


def enabled(options) -> bool:
    """`ctwindow y` on the options, or env INCOGNITA_CT_WINDOW=1."""
    return bool(getattr(options, "flagctwindow", False)) or os.environ.get("INCOGNITA_CT_WINDOW", "0") == "1"


def _levels_param() -> Path:
    env = os.environ.get("INCOGNITA_RIPL_LEVELS_PARAM")
    cands = [Path(env)] if env else []
    repo = Path(__file__).resolve().parents[3]
    cands += [repo / "raw" / "ripl4" / "RIPL-4" / "levels" / "levels-param.data"]
    for c in cands:
        if c.is_file():
            return c
    raise FileNotFoundError("ctwindow: RIPL-4 levels/levels-param.data not found (set INCOGNITA_RIPL_LEVELS_PARAM)")


def ripl_umax(Z: int, A: int) -> tuple[int, float]:
    """(Nmax, Umax [MeV]) of RIPL-4 levels-param.data, the complete level scheme's upper end; (0, 0.0) if unknown."""
    if not _U:
        for line in open(_levels_param()):
            if line.startswith("#"):
                continue
            s = line.split()
            try:
                _U[(int(s[0]), int(s[1]))] = (int(s[8]), float(s[11]))
            except (ValueError, IndexError):
                pass
    return _U.get((int(Z), int(A)), (0, 0.0))


def _window(ld):
    NL, Nt = int(ld.Nlow[0]), int(ld.Ntop[0])
    nmax, umax = ripl_umax(ld.Z, ld.A)
    if umax <= 0.0:
        return None, "no_umax"
    e = [float(x) for x in ld.edis_mev[: Nt + 1]]
    idx = [i for i in range(len(e)) if e[i] <= umax + 1e-6]
    if not idx:
        return None, "empty"
    NP = max(idx)
    if NP - NL < 3:
        return None, "lt3"
    EL, EP = e[NL], e[NP]
    if not EL < EP:
        return None, "EL>=EP"
    return (NL, NP, EL, EP, umax, nmax), None


def _interp(tab, x, dEx=0.1):
    i = max(int(x / dEx), 1)
    x0, x1 = i * dEx, (i + 1) * dEx
    return tab[i] + (tab[i + 1] - tab[i]) * (x - x0) / (x1 - x0)


def _count(r, T, EL, EP, Ex, ct, pt, n=200):
    """Levels the used density gives between EL and EP (Simpson, n intervals); closed form when ctable = 0."""
    if ct == 0.0:
        f = math.exp((EP - Ex) / T) - (math.exp((EL - Ex) / T) if EL != 0.0 else 0.0)
        return T * r * f
    E = np.linspace(EL, EP, n + 1)
    y = np.exp((E - Ex) / T + ct * np.sqrt(np.clip(E - pt, 0.0, None)))
    w = np.ones(n + 1)
    w[1:-1:2] = 4
    w[2:-1:2] = 2
    return r * float((w * y).sum()) * (EP - EL) / n / 3.0


def anchor(ld):
    """`ld` (already matched by densitymatch) with T, E0, Exmatch of barrier 0 re-solved on the complete level window,
    or `ld` unchanged where the rule does not apply."""
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
        lr, tr, _, _ = M._fermi_tables(ld, 0)
        logrho, temprho = lr.detach().double().numpy(), tr.detach().double().numpy()
        A, P = ld.A, float(ld.pair_mev)
        c2 = 2.67 if ld.flagcol else 2.33
        Exmemp = max(c2 + 253.0 / A + P, 0.1)
        ald = float(M.ignatyuk(ld, M._t(Exmemp), 0))
        x1 = max(2.25 / ald + P, 0.0) + 0.11
        x2 = 19.0 + 300.0 / A
        ntab = len(temprho) - 2

        def g(x):
            if int(x / 0.1) + 1 >= ntab:
                return float("nan")
            T = _interp(temprho, x)
            if T <= 0.0:
                return 0.0
            r = math.exp(_interp(logrho, x))
            return min(_count(r, T, EL, EP, x, ct, pt), 1e30) - (NP - NL)

        xs = np.linspace(x1, x2, 101)
        gs = [g(x) for x in xs]
        roots = []
        for a, b, ga, gb in zip(xs[:-1], xs[1:], gs[:-1], gs[1:]):
            if np.isfinite(ga) and np.isfinite(gb) and ga * gb <= 0 and not (ga == 0 and gb == 0):
                lo, hi, flo = a, b, ga
                for _ in range(60):
                    mid = 0.5 * (lo + hi)
                    fm = g(mid)
                    if flo * fm <= 0:
                        hi = mid
                    else:
                        lo, flo = mid, fm
                    if hi - lo < 1e-5:
                        break
                roots.append(0.5 * (lo + hi))
        if not roots:
            WHY[key] = "no_root"
            return ld
        Ex = min(roots[:2], key=lambda x: abs(x - Exmemp))
        ald2 = float(M.ignatyuk(ld, M._t(Ex), 0))
        if Ex <= max(2.25 / ald2 + P, 0.0) + 0.11 or Ex > 3.0 * Exmemp:
            WHY[key] = "guard"
            return ld
        T = _interp(temprho, Ex)
        r = math.exp(_interp(logrho, Ex))
        E0 = Ex - T * math.log(T * r)
        LAST[key] = dict(T0=float(ld.T_mev[0]), E00=float(ld.E0_mev[0]), Ex0=float(ld.Exmatch_mev[0]), T=T, E0=E0, Ex=Ex,
                         NL=NL, NP=NP, EL=EL, EP=EP, umax=umax, nmax_ripl=nmax, ct=ct, pt=pt, nroots=len(roots))
        WHY.pop(key, None)
        Tm, Em, Xm = ld.T_mev.clone(), ld.E0_mev.clone(), ld.Exmatch_mev.clone()
        Tm[0] = torch.as_tensor(T, dtype=Tm.dtype)
        Em[0] = torch.as_tensor(E0, dtype=Em.dtype)
        Xm[0] = torch.as_tensor(Ex, dtype=Xm.dtype)
        return replace(ld, T_mev=Tm, E0_mev=Em, Exmatch_mev=Xm)
    except FileNotFoundError:
        raise
    except Exception as e:  # noqa: BLE001 -- as the registered runner: keep branch B, record why
        WHY[key] = f"err:{type(e).__name__}:{e}"
        return ld
