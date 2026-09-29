"""SPEEDW: loader of the whole-run speed kernels (`speedw.c`, built by scripts/build_speedw_native.sh).

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

Task: SPEEDW (the speed wave; no physics of its own). Acceptance test:
`tests/hf/test_speedw_native.py` (the DWBA Numerov kernel against the torch loop, to the bit) and
`tests/hf/test_mpe_fast.py` (the multiple pre-equilibrium kernel against the torch loop).

TALYS routines the kernels compute:
    ecist.f:18285 (inri)              -- `ecis.dwba.distorted_waves`
    multipreeq2.f90:1 (multipreeq2)   -- `preeq.mpe_fast`

Selection, per call: no build, `HF_NATIVE=0` or `HF_SPEEDW_NATIVE=0` -> the Python loop; anything
on the autograd graph or off the CPU -> the Python loop, decided by the callers. The DWBA kernel
repeats torch's own complex kernels at one torch thread (their SIMD/scalar split is what makes it
bit-identical), so its caller also requires `torch.get_num_threads() == 1`.
"""

from __future__ import annotations

import ctypes
import os
from functools import lru_cache
from pathlib import Path

_LIB = Path(__file__).resolve().parent / "lib" / "libspeedw.so"
_P = ctypes.c_void_p
_I = ctypes.c_int64
_D = ctypes.c_double


@lru_cache(maxsize=1)
def lib():
    """The loaded library, or None."""
    if os.environ.get("HF_NATIVE", "1") == "0" or os.environ.get("HF_SPEEDW_NATIVE", "1") == "0":
        return None
    path = Path(os.environ.get("HF_SPEEDW_NATIVE_LIB", _LIB))
    if not path.is_file():
        return None
    try:
        so = ctypes.CDLL(str(path))
        if so.sw_version() != 1:
            return None
    except (OSError, AttributeError):
        return None
    so.sw_mpe_bin.argtypes = [_I, _I, _I, _P] + [_D] * 7 + [_P] * 19 + [_I, _P]
    so.sw_mpe_bin.restype = _I
    so.sw_dwba_numerov.argtypes = [_I, _I, _I, _P, _P, _D, _P, _P]
    so.sw_dwba_numerov.restype = None
    return so


def available() -> bool:
    return lib() is not None


def dwba_numerov(f_lj, kappa2, l, h: float, n: int):
    """`ecis.dwba.distorted_waves`, compiled: (NK, NLJ, n+1) complex128, bit-identical.

    TALYS: ecist.f:18285 (inri)
    Test: tests/hf/test_speedw_native.py
    """
    import torch

    from physics.hf.core.tensors import DTYPE

    nk, nlj = int(kappa2.shape[0]), int(l.shape[0])
    f = torch.view_as_real(f_lj.detach().to(torch.complex128).contiguous()).contiguous()
    k2 = torch.view_as_real(kappa2.detach().to(torch.complex128).reshape(-1).contiguous())
    k2 = k2.contiguous()
    y1 = (torch.as_tensor(h, dtype=DTYPE) ** (l.to(DTYPE) + 1.0)).contiguous()
    y = torch.empty((nk, nlj, n + 1, 2), dtype=torch.float64)
    lib().sw_dwba_numerov(nk, nlj, int(n), f.data_ptr(), k2.data_ptr(), h * h / 12.0,
                          y1.data_ptr(), y.data_ptr())
    return torch.view_as_complex(y)
