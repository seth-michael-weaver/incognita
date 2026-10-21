"""ALPHATEMP (Incognita extension, not TALYS; default ON, T* = 0.64 MeV since ALPHAADOPT):
alpha transmission that depends on the residual's excitation.

Physics. Hauser-Feshbach uses, for alpha emission to a residual state at excitation U, the inverse transmission of alpha +
(residual in that state). TALYS takes one T(eps) for every state: the ground-state absorption value. The alpha potentials
split: alphaomp 6 (Avrigeanu 2014) is fixed by alpha ABSORPTION on ground-state targets, alphaomp 8 (Avrigeanu, Hodgson &
Avrigeanu 1994) by alpha EMISSION from excited nuclei at ~14 MeV (the "alpha-emission puzzle"). Avrigeanu, von Oertzen &
Avrigeanu, NPA 764, 246 (2006) trace the difference to the finite-temperature change of the nuclear density, whose leading
term is O(T^2). Rule (one global constant T*):

    T(eps, U) = T_ao6(eps)^(1 - g) * T_ao8(eps)^g,   g = min(1, (T/T*)^2) = min(1, U / (a T*^2)),   a = A_res / 8

i.e. the cold (U = 0) residual takes the absorption potential, and the emission potential is reached at the mean residual
temperature T* of the data it was built from (development notes: 0.64 MeV). The geometric mean interpolates the WKB
barrier exponent, i.e. the potential, not the flux. Where one of the two is zero the mix is linear.

Keyword `alphatemp <T* MeV>` (0 = OFF = TALYS); a run left at the default takes INCOGNITA_ALPHATEMP if set (0 = OFF), else
DEFAULT_TSTAR. The hot table is the run's own alpha OMP
(alphaomp 8 in B46); the cold one is alphaomp 6 on the same grid. Pre-equilibrium, knockout and pickup keep the run's OMP.
Wired: C front densprepare (engine_decay.c), C widths (nativex.c nx_widths: every cascade nucleus), Python densprepare.
Paths not wired (decay_fast numpy widths, GPU, capture_fast) refuse the switch (`refuse`).

KEVCOLD domain (keyword `alphatemp_dom gd`, else INCOGNITA_ALPHATEMP_DOM; default n = the rule everywhere): the rule applies
only to first-chance compound cells (J, parity) in the isolated-resonance regime, Gamma_tot/D = denomhf / 2 pi < 1 (Ericson
condition; denomhf = sum_c T_c of the PRODUCTION transmissions, the sum comptarget already forms). Every other cell, and every
multi-step cascade nucleus, keeps the run's own alpha OMP (alphaomp 8), i.e. production. Wired: C front (engine_c.front two
densprepare passes + nativex.c nx_target per-cell table switch) and the Python comptarget (target._case cell split).
"""

from __future__ import annotations

import os

import numpy as np

A_OVER = 8.0  # a = A / 8 MeV^-1
DEFAULT_TSTAR = 0.64  # MeV, development notes; production default since ALPHAADOPT (2026-10-13)


def tstar(options) -> float:
    """T* in MeV (0 = OFF): an `alphatemp` keyword other than the default wins; else INCOGNITA_ALPHATEMP if set; else the default."""
    v = float(getattr(options, "alphatemp", DEFAULT_TSTAR))
    if v != DEFAULT_TSTAR:
        return max(v, 0.0)
    env = os.environ.get("INCOGNITA_ALPHATEMP", "")
    if env.strip():
        try:
            return max(float(env), 0.0)
        except ValueError:
            return DEFAULT_TSTAR
    return DEFAULT_TSTAR


DEFAULT_DOM = "n"  # ALPHAPROMO: the global rule everywhere; gd (KEVCOLD) is keyword-only


def domain(options) -> str:
    """KEVCOLD: 'gd' = the rule only where Gamma_tot/D < 1 (first-chance cells), 'n' = everywhere (ALPHATEMP2).
    A keyword other than the default wins; else INCOGNITA_ALPHATEMP_DOM if set; else DEFAULT_DOM."""
    v = str(getattr(options, "alphatemp_dom", DEFAULT_DOM) or DEFAULT_DOM).strip().lower()
    if v == DEFAULT_DOM:
        v = str(os.environ.get("INCOGNITA_ALPHATEMP_DOM", "") or "").strip().lower() or DEFAULT_DOM
    if v not in ("n", "gd"):
        raise ValueError(f"alphatemp_dom {v!r}: expected n or gd")
    return v


GD_MAX = 1.0  # KEVCOLD: Ericson boundary, Gamma_tot / D < 1 = isolated resonances


def dom_on(trans) -> bool:
    """KEVCOLD: the run has ALPHATEMP on AND the Gamma/D domain restriction."""
    return isinstance(trans, dict) and "alpha_cold" in trans and trans.get("alphatemp_dom") == "gd"


def cascade_cold(trans) -> bool:
    """Do the multi-step cascade widths take the cold/hot mix? (ALPHATEMP on and no KEVCOLD domain.)"""
    return isinstance(trans, dict) and "alpha_cold" in trans and trans.get("alphatemp_dom") != "gd"


def ustar(a_res: int, t_star: float) -> float:
    """U at which g reaches 1: a T*^2 with a = A_res / 8."""
    return (a_res / A_OVER) * t_star * t_star


def weight(ex_mev, u_star: float):
    """g(U) = min(1, max(U, 0) / U*)."""
    return np.clip(np.asarray(ex_mev, dtype=float) / u_star, 0.0, 1.0)


def mix(hot, cold, g):
    """T_cold^(1-g) T_hot^g (linear where either is 0); g broadcast over trailing axes."""
    hot = np.asarray(hot, dtype=float); cold = np.asarray(cold, dtype=float)
    g = np.asarray(g, dtype=float).reshape(g.shape + (1,) * (hot.ndim - np.ndim(g)))
    both = (hot > 0.0) & (cold > 0.0)
    with np.errstate(divide="ignore", invalid="ignore"):
        geo = np.exp((1.0 - g) * np.log(np.where(both, cold, 1.0)) + g * np.log(np.where(both, hot, 1.0)))
    lin = (1.0 - g) * cold + g * hot
    out = np.where(both, geo, lin)
    out = np.where(g >= 1.0, hot, out)
    return np.where(g <= 0.0, cold, out)


def refuse(trans, where: str) -> None:
    """Raise on a path that does not implement ALPHATEMP when the run has it on."""
    if isinstance(trans, dict) and "alpha_cold" in trans:
        raise NotImplementedError(f"ALPHATEMP is not wired on {where}; run the C engine or the Python densprepare path")


def arm_native(cas) -> None:
    """Hand the cold alpha tables and U* of `cas` to the C kernels (nx_widths, ce_densprepare), or switch them OFF.
    The arrays are kept alive on `cas`. Called before every native widths/front call (one target per process, but a
    stale pointer from another Cascade must never survive)."""
    import ctypes

    from physics.hf.native import nativex

    tr = getattr(cas, "trans", None)
    cold = tr.get("alpha_cold") if isinstance(tr, dict) else None
    dom = dom_on(tr)  # KEVCOLD: cascade widths keep production; the front arms ce_densprepare per pass
    keep = cas.__dict__.get("_alphatemp_native")
    if cold is not None and np.shape(cold[1]) != np.shape(tr[6][1]):  # the C kernels would silently skip the mix
        raise ValueError(f"ALPHATEMP: cold alpha Tl {np.shape(cold[1])} != hot {np.shape(tr[6][1])}")
    if cold is not None and (keep is None or keep[0] is not cold):
        tjl = np.ascontiguousarray(cold[0], dtype=np.float64); tl = np.ascontiguousarray(cold[1], dtype=np.float64)
        keep = cas.__dict__["_alphatemp_native"] = (cold, tjl, tl, float(tr["alphatemp_ustar"]))
    P, I, D = ctypes.c_void_p, ctypes.c_int64, ctypes.c_double
    nx = nativex.lib()
    if nx is not None and hasattr(nx, "nx_set_alphatemp"):
        nx.nx_set_alphatemp.argtypes = [P, I, I, D]; nx.nx_set_alphatemp.restype = None
        if cold is None or dom:
            nx.nx_set_alphatemp(None, 0, 0, 0.0)
        else:
            nx.nx_set_alphatemp(keep[2].ctypes.data, keep[2].shape[0], keep[2].shape[1], keep[3])
    elif cold is not None:
        raise NotImplementedError("ALPHATEMP: libnativex without nx_set_alphatemp (rebuild the native libraries)")
    from physics.hf import engine_c

    so = engine_c.lib()
    if so is not None and hasattr(so, "ce_set_alphatemp"):
        so.ce_set_alphatemp.argtypes = [P, I, I, D]; so.ce_set_alphatemp.restype = None
        if cold is None or dom:  # KEVCOLD: the front's first pass is production; arm_front(cas, True) arms the second
            so.ce_set_alphatemp(None, 0, 0, 0.0)
        else:
            so.ce_set_alphatemp(keep[1].ctypes.data, keep[1].shape[0], keep[1].shape[1], keep[3])
    elif cold is not None and so is not None:
        raise NotImplementedError("ALPHATEMP: libengdecay without ce_set_alphatemp (rebuild the native libraries)")


def arm_front(cas, on: bool) -> None:
    """KEVCOLD: arm (on) or disarm the cold alpha mix in ce_densprepare for the front's second (cold) pass."""
    import ctypes

    from physics.hf import engine_c

    so = engine_c.lib()
    keep = cas.__dict__.get("_alphatemp_native")
    if so is None or not hasattr(so, "ce_set_alphatemp") or keep is None:
        raise NotImplementedError("KEVCOLD: ce_set_alphatemp / armed cold tables missing")
    P, I, D = ctypes.c_void_p, ctypes.c_int64, ctypes.c_double
    so.ce_set_alphatemp.argtypes = [P, I, I, D]; so.ce_set_alphatemp.restype = None
    if on:
        so.ce_set_alphatemp(keep[1].ctypes.data, keep[1].shape[0], keep[1].shape[1], keep[3])
    else:
        so.ce_set_alphatemp(None, 0, 0, 0.0)


TWOPI = 2.0 * np.pi
STATS: dict = {"cells": 0, "gd": 0, "rows": []}  # KEVCOLD capture: per (E, J2, parity) Gamma/D and the choice


def gd_cells(cells, denom, e_inc: float | None = None, tag: str = "") -> np.ndarray:
    """KEVCOLD: True where the cell is isolated (Gamma_tot/D = denomhf / 2 pi < 1) and live (denomhf > 0)."""
    d = np.asarray(denom, dtype=float)
    gd = (d > 0.0) & (d / TWOPI < GD_MAX)
    STATS["cells"] += int((d > 0.0).sum()); STATS["gd"] += int(gd.sum())
    if os.environ.get("INCOGNITA_ALPHATEMP_DOM_LOG"):  # capture (output only)
        with open(os.environ["INCOGNITA_ALPHATEMP_DOM_LOG"], "a") as f:
            for (j2, p), v, g in zip(cells, d, gd, strict=True):
                f.write(f"{tag}\t{e_inc if e_inc is not None else float('nan'):.6g}\t{j2}\t{p}\t{v / TWOPI:.6e}\t{int(g)}\n")
    return gd
