"""NATIVEX2: loader of the second wave of whole-stage kernels (`native/nx2_*.c`,
scripts/build_nx2_native.sh), one library for every `nx2_*.c` file.

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

Task: NATIVEX2 (the speed work; no physics of its own). Acceptance test: `tests/hf/test_nx2.py`
(every kernel against the torch/numpy path it replaces) and the G-NATIVEX2 closeness gate.

Selection, per call: no build, `HF_NATIVE=0`, `HF_NATIVEX=0` or `HF_NX2=0` -> the torch/numpy
path; `HF_NX2_<LEVER>=0` (read at every call) turns one lever off. Anything on the autograd graph
keeps the torch path, decided by the callers. The kernels are not bit-identical to the paths they
replace, so they are held to closeness.
"""

from __future__ import annotations

import ctypes
import os
import sys
from functools import lru_cache
from pathlib import Path

_DIR = Path(__file__).resolve().parent / "lib"
P = ctypes.c_void_p
I64 = ctypes.c_int64
DBL = ctypes.c_double
INT = ctypes.c_int


def _default_path() -> Path:
    return _DIR / ("libnx2.dylib" if sys.platform == "darwin" else "libnx2.so")


@lru_cache(maxsize=1)
def lib():
    """The loaded library, or None."""
    env = os.environ
    if env.get("HF_NATIVE", "1") == "0" or env.get("HF_NATIVEX", "1") == "0" or env.get(
            "HF_NX2", "1") == "0":
        return None
    path = Path(env.get("HF_NX2_LIB", _default_path()))
    if not path.is_file():
        return None
    try:
        return ctypes.CDLL(str(path))
    except OSError:
        return None


def kernel(name: str, argtypes: list, restype=INT, lever: str | None = None):
    """The C function `name` with its signature set, or None when the library or the symbol is
    missing, or when `HF_NX2_<lever>=0`."""
    if lever is not None and os.environ.get(f"HF_NX2_{lever.upper()}", "1") == "0":
        return None
    so = lib()
    if so is None:
        return None
    return _bound(so, name, tuple(argtypes), restype)


@lru_cache(maxsize=None)
def _bound(so, name: str, argtypes: tuple, restype):
    try:
        fn = getattr(so, name)
    except AttributeError:
        return None
    fn.argtypes = list(argtypes)
    fn.restype = restype
    return fn


def ptr(a) -> int:
    """Address of a contiguous numpy array's data (0 for None)."""
    return 0 if a is None else a.__array_interface__["data"][0]
