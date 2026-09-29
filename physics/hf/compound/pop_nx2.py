"""GLUEFINISH lever `pop`: `population.f90`'s bin loop in C.

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

Task: GLUEFINISH (the speed work; no physics of its own). Acceptance test:
`tests/hf/test_nx2_pop.py` (this path against `compound.population`'s reference body, bitwise) and
docs/results/hf-gluefinish.md.

TALYS routines computed here:
    population.f90:1 (population), lines 129-244 -- the per-residual, per-bin loop of
    `compound.population.population`, one `nx2_pop_type` call per ejectile type
    (`native/nx2_pop.c`), including `_bin_nodes_many` / `_bin_nodes`, `pol1`, the 1e-30 cut and
    multiple pre-equilibrium's particle-hole ladders.

What stays in Python: the result's array allocation, and population.f90:246-268's renormalisation
(one numpy `sum` and one in-place multiply per type -- numpy's pairwise summation is not
reproduced in C, so the sum stays where its bits are defined).

Selection, per call: `HF_NATIVE=0`, `HF_NATIVEX=0`, `HF_NX2=0` or `HF_NX2_POP=0`, no `libnx2`
build, `pespinmodel >= 3` (the (J, parity)-resolved population, which an incident-neutron run
never asks for), or any input the kernel does not take -> `population`'s reference body, which is
what this is measured against.
"""

from __future__ import annotations

import ctypes

import numpy as np

from physics.hf.native.nx2 import DBL, I64, P, kernel

_ARGS = [P, I64, I64, I64, DBL, DBL, P, P, I64, I64, P, P, I64, P,
         I64, I64, I64, I64, I64, I64, I64, I64, I64, P, P, I64, P, P]


def _fn():
    """`nx2_pop_type`, or None (no build, or the lever is off)."""
    return kernel("nx2_pop_type", _ARGS, restype=ctypes.c_int64, lever="POP")


def _ptr(a) -> int:
    return 0 if a is None else a.ctypes.data


def bin_loop(inp, res, eg: np.ndarray, para, parz, parn) -> bool:
    """`population`'s first loop (population.f90:129-244) for every residual, in C.

    Fills `res` and returns True, or leaves `res` untouched and returns False for the caller to
    run its own body. Everything is written into `res` only once every type has succeeded.

    TALYS: population.f90:1 (population)
    Test: tests/hf/test_nx2_pop.py
    """
    fn = _fn()
    if fn is None or inp.pespinmodel >= 3:
        return False
    eg = np.ascontiguousarray(eg, float)
    mp1 = inp.maxpar + 1
    neg = eg.size
    popex_by, popph_by, popph2_by, mulpre_by = {}, {}, {}, {}
    hold = []  # the arrays the C call reads, kept alive until it returns
    for t, r in sorted(inp.residuals.items()):
        n = r.maxex + 1
        popex = np.zeros(n)
        popex_by[t] = popex
        mulpre_by[t] = False
        ib, ie = inp.ebegin.get(t, 0), inp.eend.get(t, -1)
        if ib >= ie:
            continue
        # population.f90:129 -- multiple pre-equilibrium is neutrons and protons only
        mulpre = bool(inp.flagmulpre and t in (1, 2))
        mulpre_by[t] = mulpre
        xspreeq = np.ascontiguousarray(inp.xspreeq_mb[t], float)
        # the spectrum is eend(type)-long, which is shorter than egrid; the kernel gives up on any
        # bin whose node falls off it, as the Python body would raise there
        if xspreeq.ndim != 1 or neg < ie + 1:
            return False
        xsgr = None
        if inp.flaggiant:
            g = inp.xsgr_mb.get(t)
            xsgr = (np.zeros_like(xspreeq) if g is None
                    else np.ascontiguousarray(g, float))
            if xsgr.shape != xspreeq.shape:
                return False
        ex = np.ascontiguousarray(r.ex_mev, float)
        dex = np.ascontiguousarray(r.dex_mev, float)
        if ex.ndim != 1 or ex.size < n or dex.size < n:
            return False
        step = step2 = popph = popph2 = None
        nstep = 0
        if mulpre:
            if inp.flag2comp:
                step2 = np.ascontiguousarray(inp.xsstep2_mb[t], float)
                if step2.ndim != 3 or step2.shape[0] < mp1 or step2.shape[1] < mp1:
                    return False
                nstep = step2.shape[2]
                popph2 = np.zeros((n, mp1, mp1, mp1, mp1))
                popph2_by[t] = popph2
            else:
                step = np.ascontiguousarray(inp.xsstep_mb[t], float)
                if step.ndim != 2 or step.shape[0] < mp1:
                    return False
                nstep = step.shape[1]
                popph = np.zeros((n, mp1, mp1))
                popph_by[t] = popph
        hold += [xspreeq, xsgr, ex, dex, step, step2]
        ok = fn(_ptr(eg), neg, ib, ie, float(inp.etotal_mev), float(r.sep_mev), _ptr(ex),
                _ptr(dex), int(r.nlast), int(r.maxex), _ptr(xspreeq), _ptr(xsgr),
                int(xspreeq.size), _ptr(popex),
                int(mulpre), int(inp.flag2comp), int(inp.maxpar), int(inp.p0), int(inp.ppi0),
                int(inp.pnu0), int(para[t]), int(parz[t]), int(parn[t]), _ptr(step), _ptr(step2),
                nstep, _ptr(popph), _ptr(popph2))
        if not ok:
            return False
    del hold
    for t in popex_by:
        res.preeqpopex_mb[t] = popex_by[t]
        res.mulpre[t] = mulpre_by[t]
        res.norm[t] = 1.0
        res.xscheck_mb[t] = 0.0
    res.xspopph_mb.update(popph_by)
    res.xspopph2_mb.update(popph2_by)
    return True
