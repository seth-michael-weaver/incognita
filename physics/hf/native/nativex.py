"""NATIVEX: loader of the whole-stage kernels (`nativex.c`, scripts/build_nativex_native.sh).

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

Task: NATIVEX (the speed work; no physics of its own). Acceptance test: `tests/hf/test_nativex.py`
(every kernel against the torch/numpy path it replaces) and the G-NATIVEX closeness gate.

TALYS routines the kernels compute:
    comptarget.f90:1 (comptarget), molprepare.f90:1 (molprepare), moldauer.f90:1 (moldauer)
        -- `compound.target_native`
    multiple.f90:1 (multiple), cascade.f90:1 (cascade), compound.f90:1 (compound)
        -- `emission.multiple_native`
    densprepare.f90:1 (densprepare), compound.f90:1 (compound)
        -- `compound.widths_native`
    finitewell.f90:1 (finitewell)
        -- `density.particle_hole._sum_terms_arr`

Selection, per call: no build, `HF_NATIVE=0` or `HF_NATIVEX=0` -> the torch/numpy path; anything
on the autograd graph (a tensor input) -> the torch path, decided by the callers. The kernels are
not bit-identical to the paths they replace (sums in loop order), so they are held to closeness.
"""

from __future__ import annotations

import ctypes
import os
import sys
from functools import lru_cache
from pathlib import Path

_DIR = Path(__file__).resolve().parent / "lib"
_P = ctypes.c_void_p
_I = ctypes.c_int64


def _default_path() -> Path:
    return _DIR / ("libnativex.dylib" if sys.platform == "darwin" else "libnativex.so")


@lru_cache(maxsize=1)
def lib():
    """The loaded library, or None."""
    if os.environ.get("HF_NATIVE", "1") == "0" or os.environ.get("HF_NATIVEX", "1") == "0":
        return None
    path = Path(os.environ.get("HF_NATIVEX_LIB", _default_path()))
    if not path.is_file():
        return None
    try:
        so = ctypes.CDLL(str(path))
        if so.nx_version() != 1:
            return None
    except (OSError, AttributeError):
        return None
    so.nx_target.argtypes = [_P, _P, _P, _P, _P]
    so.nx_target.restype = ctypes.c_int
    so.nx_walk.argtypes = [_P, _P, _P, _I, _I, _I, ctypes.c_double]
    so.nx_walk.restype = ctypes.c_int
    so.nx_widths.argtypes = [_P, _P, _P, _P, _P]
    so.nx_widths.restype = ctypes.c_int
    so.nx_sum_terms.argtypes = [_I, _P, _P, _P, _P, _I, _P, _I, _P]
    so.nx_sum_terms.restype = None
    return so


def available() -> bool:
    return lib() is not None


def ptr(a) -> int:
    return 0 if a is None else a.__array_interface__["data"][0]
