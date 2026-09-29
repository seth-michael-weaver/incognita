"""CENGSETUP: loader of the set-up kernels (`native/setup.c` plus `native/nx2_omp.c` and
`native/nx2_preeq.c` compiled again at -O3 with the vector flags, built by
scripts/build_setup_native.sh into libsetup).

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

Task: CENGSETUP (ROUTE100 WP9; the speed work, no physics of its own). Acceptance test:
`tests/hf/test_cengsetup.py` (every kernel here against the libnx2 / libhfnative kernel it stands
in for, to the bit).

What stands in for what (same arguments, same bits):
    cs_dwba_levels      -> nx2_dwba_levels (native/nx2_dwba.c), `ecis.dwba_nx2`
    nx2_omp_*           -> the same source in libnx2, `omp.omp_nx2`
    nx2_preeq_*         -> the same source in libnx2, `preeq.preeq_nx2`
    cs_numerov_inward   -> hf_numerov_inward (native/hfnative.c), handed to libsetup's nx2_omp_job

Selection: `swap(name, fn)` returns libsetup's symbol for a kernel the libnx2 wrapper already
chose (`fn` not None, so `HF_NATIVE`, `HF_NX2`, `HF_NX2_<LEVER>` keep their meaning), or `fn` itself
when libsetup is not built or `HF_SETUP=0`.
"""

from __future__ import annotations

import ctypes
import os
import sys
from functools import lru_cache
from pathlib import Path

_DIR = Path(__file__).resolve().parent / "lib"

# libnx2 name -> libsetup name
ALIAS = {"nx2_dwba_levels": "cs_dwba_levels"}


@lru_cache(maxsize=1)
def lib():
    """The loaded library, or None."""
    if os.environ.get("HF_SETUP", "1") == "0":
        return None
    default = _DIR / ("libsetup.dylib" if sys.platform == "darwin" else "libsetup.so")
    path = Path(os.environ.get("HF_SETUP_LIB", default))
    if not path.is_file():
        return None
    try:
        return ctypes.CDLL(str(path))
    except OSError:
        return None


@lru_cache(maxsize=None)
def _bound(so, name: str, argtypes: tuple, restype):
    try:
        fn = getattr(so, name)
    except AttributeError:
        return None
    fn.argtypes = list(argtypes)
    fn.restype = restype
    return fn


def swap(name: str, fn):
    """libsetup's stand-in for the libnx2 kernel `fn` (bound as `name`), or `fn`."""
    if fn is None:
        return None
    so = lib()
    if so is None:
        return fn
    got = _bound(so, ALIAS.get(name, name), tuple(fn.argtypes), fn.restype)
    return fn if got is None else got


def numerov_inward_address() -> int | None:
    """Address of `cs_numerov_inward`, or None."""
    so = lib()
    if so is None or not hasattr(so, "cs_numerov_inward"):
        return None
    return ctypes.cast(so.cs_numerov_inward, ctypes.c_void_p).value
