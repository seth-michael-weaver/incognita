"""SPEEDT3: compiled kernels for the transmission-coefficient stages (inverse Tjl, incident channel,
ECIS coupled channels), bit-identical to the Python loops they replace.

The C source is `hfnative.c` next to this file; `scripts/build_native.sh` builds it into
`lib/libhfnative.so` (gitignored; `lib/` is not a package, because `pkgutil.walk_packages` reports
a .so next to an `__init__.py` as a module and `test_contract.py::test_module_imports` then tries
to import it). Each kernel repeats the elementwise operations of its Python loop
in the same order, including where torch's own kernels fuse a multiply-add, and the LAPACK/BLAS
calls of the coupled-channels loop are torch's own MKL routines, found by address in the loaded
`libtorch_cpu`. `tests/hf/test_native.py` checks every kernel against the Python path to the bit.

Selection, per call:
* the library is missing or fails to load (a machine without a build, the Mac)  -> Python;
* `HF_NATIVE=0` in the environment                                              -> Python;
* the caller is on an autograd graph (DIFFPARAM's gradients)                    -> Python, decided
  by the callers, which only reach these kernels from their `no_grad` batched paths;
* `lapack()` (the coupled-channels loop) additionally needs torch's MKL symbols and one torch
  thread: MKL's results depend on its thread count, and the Python path's batched calls run at
  whatever count torch has.

A laptop-built `.so` needs x86-64 and glibc >= 2.35 (it binds `hypot@GLIBC_2.35`); every other
machine should build its own and run `tests/hf/test_native.py` before trusting it.
"""

from __future__ import annotations

import ctypes
import os
import platform
import sys
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
_LIB: ctypes.CDLL | None = None
_TRIED = False
_LAPACK: bool | None = None

_P = ctypes.c_void_p
_I64 = ctypes.c_int64


def _load() -> ctypes.CDLL | None:
    global _LIB, _TRIED
    if _TRIED:
        return _LIB
    _TRIED = True
    path = Path(os.environ.get("HF_NATIVE_LIB", _HERE / "lib" / "libhfnative.so"))
    if not path.is_file():
        # not silent (REDTEAM minor): the pure-Python fallback gives the same numbers, ~4x slower
        print(f"INCOGNITA: native C kernels not found at {path}; run `make native`. Falling back to pure Python (~4x slower).",
              file=sys.stderr, flush=True)
        return None
    try:
        lib = ctypes.CDLL(str(path))
        if lib.hf_version() != 1:
            return None
    except OSError:
        return None
    lib.hf_numerov_inward.argtypes = [_I64] + [_P] * 12
    lib.hf_numerov_inward.restype = None
    lib.hf_cf1.argtypes = [_I64, _P, _P, _P, _I64, _P, _P]
    lib.hf_cf1.restype = None
    lib.hf_ecis_radial.argtypes = [_I64, _I64, _I64, _I64, _P, _P, _P, _P]
    lib.hf_ecis_radial.restype = ctypes.c_int
    lib.hf_ecis_job.argtypes = [_I64] * 5 + [_P] * 10
    lib.hf_ecis_job.restype = ctypes.c_int
    lib.hf_set_vhypot.argtypes = [_P]
    lib.hf_set_vhypot.restype = None
    lib.hf_cc_block.argtypes = [_I64, _I64, _I64, _P, _P, _P, _P, _P, _P, _P]
    lib.hf_cc_block.restype = ctypes.c_int
    # CCNUMEROV: ECIS's modified Numerov step; absent from a build older than the lever
    if hasattr(lib, "hf_cc_set_modnum"):
        lib.hf_cc_set_modnum.argtypes = [_I64]
        lib.hf_cc_set_modnum.restype = None
    lib.hf_set_lapack.argtypes = [_P] * 6
    lib.hf_set_lapack.restype = None
    _LIB = lib
    return lib


def available() -> bool:
    """Whether the compiled kernels are loaded and not switched off by `HF_NATIVE=0`."""
    if os.environ.get("HF_NATIVE", "1") == "0":
        return False
    return _load() is not None


def _torch_symbol(name: str) -> int | None:
    import torch

    lib = Path(torch.__file__).parent / "lib"
    so = lib / ("libtorch_cpu.dylib" if sys.platform == "darwin" else "libtorch_cpu.so")
    try:
        cpu = ctypes.CDLL(str(so))
        return ctypes.cast(getattr(cpu, name), ctypes.c_void_p).value
    except (OSError, AttributeError):
        return None


_VHYPOT: bool | None = None


def vhypot() -> bool:
    """`available()` and torch's own vector hypot (what its complex `abs` runs) found."""
    global _VHYPOT
    if not available():
        return False
    if _VHYPOT is None and platform.machine().lower() not in ("x86_64", "amd64"):
        # CCFAST2: outside x86 (the Mac's arm64) the library is built with libm's hypot in place
        # of torch's AVX2 one (hfnative.c, HF_X86 = 0): to rounding, not to torch's bits, which
        # nothing on that machine was bitwise to anyway.
        _VHYPOT = True
    if _VHYPOT is None:
        addr = _torch_symbol("Sleef_hypotd4_u05")
        if addr:
            _LIB.hf_set_vhypot(addr)
        _VHYPOT = bool(addr)
    return _VHYPOT


def lapack_symbols() -> bool:
    """`available()` and torch's six MKL complex routines found and handed to the library.

    Whether they may be USED is `lapack()`: MKL's results depend on its thread count, so the
    compiled block loop is only the Python path's answer at one torch thread.
    """
    global _LAPACK
    if not available():
        return False
    if _LAPACK is None:
        _LAPACK = False
        addr = [_torch_symbol(n) for n in ("zgemm_", "zgetrf_", "zgetrs_", "zgeqrf_", "zungqr_",
                                           "ztrsm_")]
        if all(addr):
            _LIB.hf_set_lapack(*addr)
            _LAPACK = True
    return _LAPACK


def lapack() -> bool:
    """`lapack_symbols()` and torch at one thread."""
    import torch

    return lapack_symbols() and torch.get_num_threads() == 1


def _ptr(a) -> int:
    return a.ctypes.data if isinstance(a, np.ndarray) else a.data_ptr()


def numerov_inward(ee, ra, rb, gb, gb1, n):
    """`schrodinger._numerov_inward_many` (float64 columns, int64 step counts)."""
    m = ee.shape[0]
    cols = [np.ascontiguousarray(v, dtype=np.float64) for v in (ee, ra, rb, gb, gb1)]
    nn = np.ascontiguousarray(n, dtype=np.int64)
    out = [np.empty(m) for _ in range(6)]
    _LIB.hf_numerov_inward(m, *(_ptr(v) for v in cols), _ptr(nn), *(_ptr(v) for v in out))
    return tuple(out)


def cf1(eta, rho, lmax: int, ltop):
    """`schrodinger._cf1_many(eta, rho, lmax, ltop)`: (out (m, lmax + 1), sign (m,))."""
    m = rho.shape[0]
    eta = np.ascontiguousarray(eta, dtype=np.float64)
    rho = np.ascontiguousarray(rho, dtype=np.float64)
    top = np.ascontiguousarray(ltop, dtype=np.int64)
    out = np.empty((m, lmax + 1), dtype=np.float64)
    sign = np.empty(m, dtype=np.float64)
    if m:
        _LIB.hf_cf1(m, _ptr(eta), _ptr(rho), _ptr(top), lmax + 1, _ptr(out), _ptr(sign))
    return out, sign


def ecis_radial(x, ism, nmax: int):
    """The radial loop of `schrodinger._integrate_ecis_many` for one job: x (E, L, J, R) complex
    torch tensor, ism (E,) -> u_am, u_ap (E, L, J)."""
    import torch

    x = x.contiguous()
    n_e, n_l, n_j, n_r = x.shape
    ism = np.ascontiguousarray(ism.numpy(), dtype=np.int64)
    u_am = torch.empty((n_e, n_l, n_j), dtype=torch.complex128)
    u_ap = torch.empty_like(u_am)
    if _LIB.hf_ecis_radial(n_e, n_l * n_j, n_r, int(nmax), x.data_ptr(), _ptr(ism),
                           u_am.data_ptr(), u_ap.data_ptr()):
        raise MemoryError("hf_ecis_radial")
    return u_am, u_ap


def ecis_job(pieces, ism, nmax: int):
    """`schrodinger._ecis_setup`'s x and the radial loop of `_integrate_ecis_many` in one pass for
    one job, from `pieces = (so, central, coul, ls2, L, k2 h h, mu h h)` (`_ecis_setup(...,
    native=True)`): u_am, u_ap (E, L, J)."""
    import torch

    so, central, coul, ls2, L, kh, mhh = (t.detach().contiguous() for t in pieces)
    n_e = so.shape[0]
    n_l, n_j = ls2.shape
    ism = np.ascontiguousarray(ism.numpy(), dtype=np.int64)
    u_am = torch.empty((n_e, n_l, n_j), dtype=torch.complex128)
    u_ap = torch.empty_like(u_am)
    if _LIB.hf_ecis_job(
            n_e, n_l, n_j, so.shape[1], int(nmax), so.data_ptr(), central.data_ptr(),
            coul.data_ptr(), ls2.data_ptr(), L.data_ptr(), kh.data_ptr(), mhh.data_ptr(),
            _ptr(ism), u_am.data_ptr(), u_ap.data_ptr()):
        raise MemoryError("hf_ecis_job")
    return u_am, u_ap


_KEEP = ("umm1", "um", "ump1", "mmm1", "mmp1", "sp1", "sm1")
_WTS: list | None = None      # the finite-difference weight tensors, kept alive for their pointers
_WPTR: ctypes.c_void_p | None = None


def cc_block(mmat, nmat, u1, h_fm, nmatch, weights):
    """`solver._numerov_blocks` for one block: mmat/nmat (E, R, N, N) complex (nmat may be None),
    u1 (E, N, N), h_fm (E,), nmatch (E,), `weights(npts)` the finite-difference weights.
    Returns the `keep` dict with (E, N, N) tensors."""
    import torch

    mmat = mmat.contiguous()
    nmat = nmat.contiguous() if nmat is not None else None
    u1 = u1.contiguous()
    n_e, n_r, n, _ = mmat.shape
    h = np.ascontiguousarray(h_fm.numpy(), dtype=np.float64)
    nm = np.ascontiguousarray(nmatch.numpy(), dtype=np.int64)
    global _WTS, _WPTR
    if _WPTR is None:  # the finite-difference weights are constants; hold them and their pointers
        _WTS = [weights(k).contiguous() for k in range(3, 8)]
        _WPTR = ctypes.cast((ctypes.c_void_p * 5)(*(w.data_ptr() for w in _WTS)),
                            ctypes.c_void_p)
    keep = torch.zeros((7, n_e, n, n), dtype=torch.complex128)
    if hasattr(_LIB, "hf_cc_set_modnum"):  # CCNUMEROV, read per call as the other levers are
        _LIB.hf_cc_set_modnum(int(os.environ.get("HF_CC_MODNUM", "1") != "0"))
    rc = _LIB.hf_cc_block(n_e, n, n_r, mmat.data_ptr(),
                          nmat.data_ptr() if nmat is not None else None, u1.data_ptr(), _ptr(h),
                          _ptr(nm), _WPTR, keep.data_ptr())
    if rc != 0:
        raise MemoryError(f"hf_cc_block returned {rc}")
    return {name: keep[k] for k, name in enumerate(_KEEP)}
