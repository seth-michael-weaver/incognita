"""MERGED2 lever `exgrid`: `exgrid.f90`'s excitation-energy bins of one residual in C.

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

Task: MERGED2 (the speed work; no physics of its own). Acceptance test:
`tests/hf/test_nx2_exgrid.py` (this path against `core.grids.excitation_energies`' reference body,
bitwise) and docs/results/hf-merged2.md.

TALYS routines computed here:
    exgrid.f90:1 (exgrid), lines 141-181 -- `Ex(0:maxex)` and `deltaEx` of one residual
    (`native/nx2_exgrid.c`).

Selection, per call: `HF_NATIVE=0`, `HF_NATIVEX=0`, `HF_NX2=0` or `HF_NX2_EXGRID=0`, no `libnx2`
build, logarithmic bins (`equidistant n`), or a grid past (0:numex) -> the reference body, which
is what this is measured against.
"""

from __future__ import annotations

import ctypes

import numpy as np

from physics.hf.native.nx2 import DBL, I64, P, kernel

_ARGS = [P, I64, I64, DBL, I64, I64, I64, I64, DBL, I64, P, I64, P, I64]


def _fn():
    """`nx2_exgrid`, or None (no build, or the lever is off)."""
    return kernel("nx2_exgrid", _ARGS, restype=ctypes.c_int64, lever="EXGRID")


def excitation_energies(edis_mev, nlast: int, exmax_mev: float, nbins: int, aix: int,
                        flagequi: bool, etotal_mev: float | None, numex: int):
    """`core.grids.excitation_energies` in C: (Ex, deltaEx, maxex), or None for the caller to
    run its own body.

    TALYS: exgrid.f90:1 (exgrid)
    Test: tests/hf/test_nx2_exgrid.py
    """
    fn = _fn()
    if fn is None:
        return None
    ed = np.ascontiguousarray(edis_mev, np.float64)
    if ed.ndim != 1:
        return None
    nlast = int(nlast)
    # maxex + 2 <= NL + max(nbins, 2) + 2 on every branch, and never past (0:numex+1)
    cap = min(nlast + max(int(nbins), 2) + 2, numex + 2)
    if cap < 2:
        return None
    ex = np.empty(cap)
    dex = np.empty(cap - 1)
    maxex = fn(ed.ctypes.data, ed.size, nlast, float(exmax_mev), int(nbins), int(aix),
               int(bool(flagequi)), int(etotal_mev is not None),
               0.0 if etotal_mev is None else float(etotal_mev), numex, ex.ctypes.data, cap,
               dex.ctypes.data, cap - 1)
    if maxex < 0:
        return None
    return ex[: maxex + 2], dex[: maxex + 1], int(maxex)
