"""CCFAST2: loader and wrapper of `physics/hf/native/ccfast.c`, the coupled-channels radial loop
held to the closeness rule instead of to the bits of `solver._numerov_blocks`.

`scripts/build_ccfast_native.sh` builds `physics/hf/native/lib/libccfast.so` (`.dylib` on macOS;
gitignored). The
kernel calls torch's own LAPACK/BLAS, found by address in `libtorch_cpu` exactly as
`physics.hf.native.lapack_symbols` finds them for SPEEDT3's kernels.

Selection: `available()` is False -- and `solver.smatrix_blocks` runs SPEEDT3's `hf_cc_block` or
Python -- when the library is missing, when `HF_CCFAST_NATIVE=0`, or when torch's symbols are not
found. Callers reach it only from `no_grad` paths that asked for `exact_bits=False`.

Task: CCFAST2. Test: tests/hf/test_ccfast.py
"""

from __future__ import annotations

import ctypes
import os
import sys
from pathlib import Path

import torch
from torch import Tensor

from physics.hf.core.tensors import DTYPE

_LIB_DIR = Path(__file__).resolve().parents[1] / "native" / "lib"
_LIB_PATH = _LIB_DIR / ("libccfast.dylib" if sys.platform == "darwin" else "libccfast.so")
# SETB: the same kernel built with `ccsplit.h` (split-storage solve and stabilisation). Default on
# arm64, where it was measured (Accelerate); `HF_CCSPLIT=1`/`0` forces it on or off elsewhere.
_SPLIT_PATH = _LIB_DIR / ("libccsplit.dylib" if sys.platform == "darwin" else "libccsplit.so")


def _split_wanted() -> bool:
    import platform

    flag = os.environ.get("HF_CCSPLIT")
    if flag is not None:
        return flag == "1"
    return platform.machine() in ("arm64", "aarch64")
_LIB: ctypes.CDLL | None = None
_TRIED = False
# steps between two renormalisations of W. `solver.STABILISE_EVERY` (the bitwise torch path) is 10;
# NATIVEX2: 15 here: a change of basis every 15 steps keeps the solutions independent on every
# checked target (15 deformed, vibrational and actinide nuclides, all channels within 3.5e-12 of
# 10) and spares a third of the stabilisations (whole deformed nuclides 0-10 % less CPU)
STABILISE_EVERY = 15

_P = ctypes.c_void_p
_I64 = ctypes.c_int64


def _load() -> ctypes.CDLL | None:
    global _LIB, _TRIED
    if _TRIED:
        return _LIB
    _TRIED = True
    default = _SPLIT_PATH if _split_wanted() and _SPLIT_PATH.is_file() else _LIB_PATH
    path = Path(os.environ.get("HF_CCFAST_LIB", default))
    if not path.is_file():
        return None
    try:
        lib = ctypes.CDLL(str(path))
        if lib.cc_version() != 1:
            return None
    except OSError:
        return None
    addr = [_torch_symbol(n) for n in ("zgemm_", "zgetrf_", "zgetrs_", "zgeqrf_", "zungqr_",
                                       "ztrsm_")]
    if not all(addr):
        return None
    lib.cc_set_lapack.argtypes = [_P] * 6
    lib.cc_set_lapack.restype = None
    lib.cc_set_lapack(*addr)
    lib.cc_block_w.argtypes = [_I64] * 4 + [_P] * 9 + [_I64, _P]
    lib.cc_block_w.restype = ctypes.c_int
    lib.cc_set_small_n.argtypes = [_I64]
    lib.cc_set_small_n.restype = None
    lib.cc_set_gemm_small.argtypes = [_I64]
    lib.cc_set_gemm_small.restype = None
    lib.cc_block_d.argtypes = [_I64] * 4 + [_P] * 15 + [_I64, _P]
    lib.cc_block_d.restype = ctypes.c_int
    # NATIVEX2 ccx: Jacobi sweeps in place of the elimination where 1 - c M is diagonal enough
    # (ccfast.c, `nm_solve_z`); absent from a build older than the lever
    if hasattr(lib, "cc_set_neumann"):
        lib.cc_set_neumann.argtypes = [_I64, ctypes.c_double]
        lib.cc_set_neumann.restype = None
        lib.cc_set_real_gemm.argtypes = [_I64]
        lib.cc_set_real_gemm.restype = None
        lib.cc_set_dgemm.argtypes = [_P]
        lib.cc_set_dgemm.restype = None
        dgemm = _torch_symbol("dgemm_")
        if dgemm:
            lib.cc_set_dgemm(dgemm)
    # CCBLOCKD: the cheaper `cc_block_d` step (real stencil products, (1 - c M) u carried);
    # absent from a build older than the lever
    if hasattr(lib, "cc_set_blockd"):
        lib.cc_set_blockd.argtypes = [_I64]
        lib.cc_set_blockd.restype = None
        lib.cc_set_rmm_small.argtypes = [_I64]
        lib.cc_set_rmm_small.restype = None
    # CCNUMEROV: ECIS's modified Numerov step; absent from a build older than the lever
    if hasattr(lib, "cc_set_modnum"):
        lib.cc_set_modnum.argtypes = [_I64]
        lib.cc_set_modnum.restype = None
    _LIB = lib
    return lib


def _torch_symbol(name: str) -> int | None:
    """The address of a LAPACK/BLAS routine in torch's CPU library (MKL on Linux x86, Accelerate
    re-exported on macOS arm64)."""
    lib = Path(torch.__file__).parent / "lib"
    for fname in ("libtorch_cpu.so", "libtorch_cpu.dylib"):
        if (lib / fname).is_file():
            try:
                cpu = ctypes.CDLL(str(lib / fname))
                return ctypes.cast(getattr(cpu, name), ctypes.c_void_p).value
            except (OSError, AttributeError):
                return None
    return None


def available() -> bool:
    if os.environ.get("HF_CCFAST_NATIVE", "1") == "0":
        return False
    return _load() is not None


_KEEP = ("umm1", "um", "ump1", "mmm1", "mmp1", "sp1", "sm1")
# NATIVEX2 ccx: a step takes the Jacobi sweeps when rho^(p+1) <= SWEEP_TOL (rho the infinity norm of
# D^-1 O of 1 - c M, p the sweeps). 1e-13 is where the solutions stop moving: against the
# elimination the matching ratios u_{m+1} u_m^-1 of every Lu-175 block differ by 7.6e-12 at 1e-13 as
# at 1e-16 or 1e-19 (that floor is the blocks' own rounding), and by 5e-10 at 1e-11.
SWEEP_TOL = 1.0e-13


def _flag(name: str, default: bool) -> bool:
    v = os.environ.get(name)
    return default if v is None else v != "0"


def _set_sweeps(lib) -> None:
    """Switch the kernel's NATIVEX2 `ccx` paths for the next call: the Jacobi sweeps and the complex
    products as real ones, both measured on arm64 (Accelerate) and off elsewhere. `HF_NX2_CCX=0`
    turns them off (the elimination on every step, zgemm). Read per call, as the other NATIVEX2
    levers read theirs."""
    if hasattr(lib, "cc_set_neumann"):
        import platform

        on = (os.environ.get("HF_NX2_CCX", "1") != "0"
              and platform.machine() in ("arm64", "aarch64"))
        # CCBLOCKD: the two ccx levers are separable, so that either can be forced on or off
        # anywhere. Unset, both follow `on` exactly as before. `HF_NX2_GEMM=1` on x86 is the
        # arithmetic-noise floor of `docs/results/hf-ccblockd.md`: the same operations in the
        # same order through four real products instead of one zgemm.
        lib.cc_set_neumann(int(_flag("HF_NX2_SWEEP", on)), SWEEP_TOL)
        lib.cc_set_real_gemm(int(_flag("HF_NX2_GEMM", on)))
        gs = os.environ.get("HF_CC_GEMM_SMALL")
        if gs is not None:  # measurement only: the N up to which `mm` is the triple loop
            lib.cc_set_gemm_small(int(gs))
    # CCBLOCKD: on by default everywhere the library has it. `HF_CCBLOCKD=0` runs the reference
    # step (`ccfast.c::cc_block_d_ref`) instead, which is how the A/B arms are taken in one
    # process; `=2` takes the real stencil products only and still forms `M_i u_i`.
    # `HF_CCBLOCKD_SMALL` sets the N below which the real product is a triple loop.
    if hasattr(lib, "cc_set_blockd"):
        lib.cc_set_blockd(int(os.environ.get("HF_CCBLOCKD", "1")))
        lib.cc_set_rmm_small(int(os.environ.get("HF_CCBLOCKD_SMALL", "0")))
    # CCNUMEROV: the same per-call read for the modified Numerov step (`solver.modified_numerov`)
    if hasattr(lib, "cc_set_modnum"):
        lib.cc_set_modnum(int(os.environ.get("HF_CC_MODNUM", "1") != "0"))


def _common(ch, ff, kin, h_fm: Tensor, nmatch: Tensor, r_fm: Tensor) -> dict:
    """The per-block arrays both kernels read: M(r) = mu sum_lambda central_lambda(r) A^lambda +
    diag(l(l+1)/r^2 - k^2 + mu V_C + mu 2 l.s V_so), exactly `solver._block_operators`'s terms."""
    lev = ch.level
    lf = ch.l.to(DTYPE)
    mu = kin.mu_coef.to(DTYPE).contiguous()
    return {
        "central": ff.central.to(torch.complex128).contiguous(),
        "cpl": ch.coupling.to(DTYPE).contiguous(),
        "diagr": ((lf * (lf + 1.0))[None, None, :] / r_fm[:, :, None] ** 2
                  - kin.kappa2[:, lev][:, None, :]
                  + (mu[:, None] * ff.coulomb)[:, :, None]).contiguous(),
        "so0": ff.spin_orbit[:, 0, :].to(torch.complex128).contiguous(),
        "ls2": ch.ls2.to(DTYPE).contiguous(),
        "mu": mu,
        "u1": torch.diag_embed(h_fm[:, None] ** (lf + 1.0)[None, :]).to(torch.complex128)
        .contiguous(),
        "h": h_fm.to(DTYPE).contiguous(),
        "nm": nmatch.to(torch.int64).contiguous(),
    }


_FDW: Tensor | None = None


def _fd_weights_flat() -> Tensor:
    """`solver._fd_weights(npts)` for npts = 3..7, real parts, (3, npts) each, concatenated."""
    global _FDW
    if _FDW is None:
        from physics.hf.ecis.solver import _fd_weights

        _FDW = torch.cat([_fd_weights(k).real.reshape(-1) for k in range(3, 8)]).to(DTYPE)
    return _FDW


def cc_block_w(ch, ff, kin, h_fm: Tensor, nmatch: Tensor, r_fm: Tensor,
               stab: int = STABILISE_EVERY) -> dict:
    """`solver._numerov_blocks`'s `keep` for one block, (E, N, N) tensors keyed as `_KEEP`:
    `ccfast.c::cc_block_w` below `soswitch`, `cc_block_d` (derivative coupling) above it."""
    keep = _keep_raw(ch, ff, kin, h_fm, nmatch, r_fm, stab)
    return {name: keep[k] for k, name in enumerate(_KEEP)}


def _keep_raw(ch, ff, kin, h_fm: Tensor, nmatch: Tensor, r_fm: Tensor,
              stab: int = STABILISE_EVERY) -> Tensor:
    """`cc_block_w`'s output as the one (7, E, N, N) tensor the kernel wrote."""
    lib = _load()
    _set_sweeps(lib)
    n_e, n_r = r_fm.shape
    n = int(ch.level.numel())
    a = _common(ch, ff, kin, h_fm, nmatch, r_fm)
    keep = torch.zeros((7, n_e, n, n), dtype=torch.complex128)
    deformed = ch.so_deriv_coef is not None and ff.so_r2 is not None
    head = (n_e, n, n_r, a["central"].shape[1], a["central"].data_ptr(), a["cpl"].data_ptr(),
            a["diagr"].data_ptr(), a["so0"].data_ptr(), a["ls2"].data_ptr(), a["mu"].data_ptr())
    if deformed:
        so_grad = ff.so_grad.real.to(DTYPE).contiguous()
        so_r2 = ff.so_r2.real.to(DTYPE).contiguous()
        so1c, so2c, sodc = (t.to(DTYPE).contiguous()
                            for t in (ch.so_grad_coef, ch.so_r2_coef, ch.so_deriv_coef))
        fdw = _fd_weights_flat()
        rc = lib.cc_block_d(*head, so_grad.data_ptr(), so_r2.data_ptr(), so1c.data_ptr(),
                            so2c.data_ptr(), sodc.data_ptr(), fdw.data_ptr(), a["u1"].data_ptr(),
                            a["h"].data_ptr(), a["nm"].data_ptr(), int(stab), keep.data_ptr())
    else:
        rc = lib.cc_block_w(*head, a["u1"].data_ptr(), a["h"].data_ptr(), a["nm"].data_ptr(),
                            int(stab), keep.data_ptr())
    if rc != 0:
        raise MemoryError(f"ccfast kernel returned {rc}")
    return keep


def glue_available() -> bool:
    """CCGLUE: `cc_match_acc` is in the loaded library and `HF_CCGLUE` is not 0."""
    if os.environ.get("HF_CCGLUE", "1") == "0" or not available():
        return False
    lib = _load()
    if not hasattr(lib, "cc_match_acc"):
        return False
    if not lib.cc_match_acc.argtypes:
        lib.cc_match_acc.argtypes = [_I64, _I64] + [_P] * 13 + [_I64, _I64] + [ctypes.c_double] * 3 \
            + [_P] * 5
        lib.cc_match_acc.restype = ctypes.c_int
    return True


def sixj(args: list[Tensor]) -> Tensor | None:
    """CCGLUE: `coupling.sixj(*args)` for flat (M,) float64 arguments by `ccfast.c::cc_sixj`, bit for
    bit, or None without the library (or with `HF_CCGLUE=0`)."""
    if os.environ.get("HF_CCGLUE", "1") == "0" or not available():
        return None
    lib = _load()
    if not hasattr(lib, "cc_sixj"):
        return None
    if not lib.cc_sixj.argtypes:
        lib.cc_sixj.argtypes = [_I64] + [_P] * 8
        lib.cc_sixj.restype = None
        from physics.hf.core.angmom import _LOGFACT_TABLE

        lib.cc_set_logfact.argtypes = [_P, _I64]
        lib.cc_set_logfact.restype = None
        lib.cc_set_logfact(_LOGFACT_TABLE.data_ptr(), int(_LOGFACT_TABLE.numel()))
    a = [t.detach().to(DTYPE).contiguous() for t in args]
    expo = torch.empty(a[0].shape, dtype=DTYPE)
    mult = torch.empty(a[0].shape, dtype=DTYPE)
    lib.cc_sixj(int(expo.numel()), *(t.data_ptr() for t in a), expo.data_ptr(), mult.data_ptr())
    return torch.exp(expo) * mult


def cc_block_acc(ch, ff, kin, h_fm: Tensor, nmatch: Tensor, r_fm: Tensor, coul, n_lev: int,
                 lmax: int, target_spin: float, proj_spin: float,
                 keep: Tensor | None = None) -> dict:
    """CCGLUE: one (J, parity) block from the radial loop to its cross-section contributions --
    `cc_block_w`, then `ccfast.c::cc_match_acc` in place of `solver._match(minus_identity=True)` and
    `solver.accumulate(minus_identity=True)`. `coul` is `_asymptotic`'s (F, dF, G, dG) of the block
    (`coulomb_functions_many`). Returns `accumulate`'s dict on the rows of `h_fm`. SPEED50: `keep`,
    when given, is the radial loop's output already computed (CCGPU) and is used in its place."""
    lib = _load()
    if keep is None:
        keep = _keep_raw(ch, ff, kin, h_fm, nmatch, r_fm)
    n_e, n = int(h_fm.shape[0]), int(ch.level.numel())
    lev = ch.level
    k = kin.k_fm[:, lev].to(DTYPE).contiguous()
    op = kin.open_[:, lev].to(torch.uint8).contiguous()
    idx = ch.l[None, :].expand(n_e, n).reshape(-1, 1)
    fv, dfv, gv, dgv = (t.gather(1, idx).reshape(n_e, n).to(DTYPE).contiguous() for t in coul)
    li = ch.l.to(torch.int64).contiguous()
    lv = lev.to(torch.int64).contiguous()
    jv = ch.j.to(DTYPE).contiguous()
    el_mask = ch.elastic.to(torch.uint8).contiguous()
    h = h_fm.to(DTYPE).contiguous()
    nm = nmatch.to(torch.int64).contiguous()
    J = 0.5 * ch.twoJ
    gw = (2.0 * J + 1.0) / ((2.0 * target_spin + 1.0) * (2.0 * proj_spin + 1.0))
    out = {"reac": torch.empty(n_e, dtype=DTYPE), "tot": torch.empty(n_e, dtype=DTYPE),
           "el": torch.empty(n_e, dtype=DTYPE), "direct": torch.empty((n_e, n_lev), dtype=DTYPE),
           "tjl": torch.empty((n_e, lmax + 1, 2), dtype=DTYPE)}
    rc = lib.cc_match_acc(
        n_e, n, keep.data_ptr(), h.data_ptr(), nm.data_ptr(), k.data_ptr(), op.data_ptr(),
        fv.data_ptr(), dfv.data_ptr(), gv.data_ptr(), dgv.data_ptr(), li.data_ptr(), lv.data_ptr(),
        jv.data_ptr(), el_mask.data_ptr(), int(n_lev), int(lmax), gw, 2.0 * J + 1.0,
        2.0 * target_spin + 1.0, out["reac"].data_ptr(), out["tot"].data_ptr(),
        out["el"].data_ptr(), out["direct"].data_ptr(), out["tjl"].data_ptr())
    if rc != 0:
        raise MemoryError(f"cc_match_acc returned {rc}")
    return out


__all__ = ["STABILISE_EVERY", "available", "cc_block_acc", "cc_block_w", "glue_available", "sixj"]
