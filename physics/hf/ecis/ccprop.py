"""CCPROP (ROUTE100 WP8): a log-derivative propagator for one coupled-channels (J, parity) block,
as the candidate replacement for the renormalised Numerov step of `ccfast.c::cc_block_w`.

The incumbent integrates the solution matrix u itself:

    u'' = M(r) u,   W_i = (1 - c M_i) u_i,   W_{i+1} = 12 u_i - 10 W_i - W_{i-1},
    u_{i+1} = (1 - c M_{i+1})^-1 W_{i+1},    c = h^2 / 12,

one complex linear solve per radial step, plus a QR renormalisation every `STABILISE_EVERY` steps
to keep the N columns independent. What `solver._match` then wants from the radial loop is not u
but **L = u' u^-1 at the matching radius** -- the log derivative. This module propagates that
object directly, so the QR disappears (a log derivative cannot lose linear independence: it is
already the quotient) and the step is one matrix inverse instead of one solve.

Method: Johnson's log-derivative propagator (J. Comput. Phys. 13 (1973) 445) with the half-sector
set to ECIS's own radial step, so the potential is sampled exactly where `ecis_grid` samples it
(CCPROP gate 3). Writing Y = u' u^-1, the Riccati equation Y' = M - Y^2 is split into

  * a **kick** at each node,  Y <- Y + Q_i,  Q_i = w_i Mtilde_i, with `w_i` the composite Simpson
    weight of the node (h/3, 4h/3, 2h/3, ..., 4h/3, h/3) and, at a panel midpoint, the modified
    matrix Mtilde = (1 + h^2 M / 6)^-1 M -- Johnson's reference-potential correction, which is what
    makes the rule fourth order and what keeps it stable where h^2 |M| >> 1 (the centrifugal wall
    at the first few points: l = 20 at r = 0.26 fm gives h^2 M ~ 400);
  * a **drift** over the free sector,  Y <- (1/h) 1 - (1/h^2) (Y + (1/h) 1)^-1,  which is the exact
    log-derivative propagator of u'' = 0 and which reproduces the -Y^2 term of the Riccati equation
    to all orders in h.

Panel parity: composite Simpson needs an even number of sectors between the first node and the
capture. Each energy has its own matching index, so an energy whose `nmatch` is odd starts one node
later, at r = 2h instead of r = h, where the same r^(l+1) start applies. Nothing is interpolated
and no node moves off ECIS's grid.

Start: u_c ~ r^(l_c + 1) as r -> 0, so Y = diag((l_c + 1) / r) at the first node -- the same
information the Numerov loop carries in `u_1 = diag(h^(l+1))` with `u_0 = 0`, in log-derivative
form.

**This is a research prototype, and CCPROP's verdict on it is a kill** (`docs/results/hf-ccprop.md`):
it costs more FLOPs per step than the renormalised Numerov it would replace, and at ECIS's step
size it cannot reproduce that kernel to the 1e-6 / 1e-4 per-cell bar, because the bar is twenty
times finer than the incumbent's own discretisation error at that step. Nothing in the port calls
this module; it exists so that the numbers behind the kill can be re-run.

Task: CCPROP. Test: tests/hf/test_ccprop.py
"""

from __future__ import annotations

import torch
from torch import Tensor

from physics.hf.core.tensors import DTYPE

CDTYPE = torch.complex128

__all__ = ["log_derivative", "smatrix_prop"]


def _start_node(nmatch: Tensor) -> Tensor:
    """First node of each energy: 0 when `nmatch` is even, 1 when it is odd, so that the number of
    Simpson sectors up to the matching node is even."""
    return (nmatch % 2).to(torch.int64)


def log_derivative(mm: Tensor, h_fm: Tensor, nmatch: Tensor, l_plus_1: Tensor,
                   modified: bool = True) -> Tensor:
    """Y = u' u^-1 at each energy's matching radius, (E, N, N), from M(r) on the ECIS grid.

    `mm` is (E, R, N, N) as `solver._block_operators` returns it, `h_fm` (E,), `nmatch` (E,) the
    matching index (r_match = h (nmatch + 1), the grid point `mm[:, nmatch]`), and `l_plus_1` (N,)
    the orbital angular momenta plus one.

    `modified=False` drops Johnson's (1 + h^2 M / 6)^-1 correction, which turns the rule from
    fourth order into second: it is the FLOP floor quoted in the gate, not a usable method.
    """
    n_e, n_r, n, _ = mm.shape
    eye = torch.eye(n, dtype=CDTYPE).expand(n_e, n, n)
    h = h_fm.to(CDTYPE)[:, None, None]
    hi = 1.0 / h
    c6 = (h_fm.to(CDTYPE) ** 2 / 6.0)[:, None, None]
    w3 = (h_fm.to(CDTYPE) / 3.0)[:, None, None]

    start = _start_node(nmatch)
    last = int(nmatch.max())
    r0 = h_fm[:, None] * (start.to(DTYPE) + 1.0)[:, None]  # r at each energy's first node
    y = torch.diag_embed((l_plus_1[None, :] / r0).to(CDTYPE))
    out = torch.zeros((n_e, n, n), dtype=CDTYPE)
    done = torch.zeros(n_e, dtype=torch.bool)

    for i in range(last + 1):
        live = (~done) & (i >= start)
        if not bool(live.any()):
            continue
        p = i - start                       # node index inside this energy's own quadrature
        mid = (p % 2 == 1) & live           # panel midpoint: weight 4h/3 and the modification
        end = ((p == 0) | (nmatch == i)) & live   # the two ends of the whole range: weight h/3
        shared = live & ~mid & ~end         # interior panel joint: weight 2h/3
        wt = torch.where(mid, torch.full_like(h_fm, 4.0),
                         torch.where(end, torch.ones_like(h_fm),
                                     torch.where(shared, torch.full_like(h_fm, 2.0),
                                                 torch.zeros_like(h_fm))))
        mi = mm[:, i]
        q = mi
        if modified:
            # (1 + h^2 M / 6)^-1 M at the midpoints; the endpoints take M itself
            qm = torch.linalg.solve(eye + c6 * mi, mi)
            q = torch.where(mid[:, None, None], qm, mi)
        y = y + (w3 * wt.to(CDTYPE)[:, None, None]) * q
        hit = (nmatch == i) & live
        if bool(hit.any()):
            out = torch.where(hit[:, None, None], y, out)
            done = done | hit
            if bool(done.all()):
                break
        # free drift over one sector -- only for the energies that have started and are not done,
        # so that an odd-`nmatch` energy waiting at node 1 is not carried through node 0's sector
        step = hi * eye - (hi * hi) * torch.linalg.solve(y + hi * eye, eye)
        y = torch.where((live & ~hit)[:, None, None], step, y)
    return out


def smatrix_prop(ch, ff, kin, h_fm: Tensor, nmatch: Tensor, r_fm: Tensor,
                 minus_identity: bool = False, coulomb=None, modified: bool = True):
    """`solver.smatrix(ch, ...)` with the log-derivative propagator in place of the Numerov loop:
    the same (S, open-channel mask), matched by the same algebra on the same asymptotic functions.

    Only the undeformed-spin-orbit form (`solver._block_operators`'s `nmat is None`, i.e. below
    `soswitch`, the `cc_block_w` path) is propagated here; above `soswitch` the equation carries a
    first-derivative coupling and its Riccati form picks up an N Y term, costed in
    `harness/ccprop_flops.py` but not implemented, because the gate is already decided.
    """
    from physics.hf.ecis.solver import _asymptotic, _block_operators

    mm, nm = _block_operators(ch, ff, kin, r_fm)
    if nm is not None:
        raise NotImplementedError("CCPROP prototype covers the undeformed spin-orbit block only")
    lp1 = (ch.l.to(DTYPE) + 1.0)
    L = log_derivative(mm, h_fm, nmatch, lp1, modified=modified)
    rm = h_fm * (nmatch.to(DTYPE) + 1.0)
    hp, dhp, hm, dhm, scale, op = _asymptotic(kin, ch, rm, coulomb)
    a = L * hp[:, None, :] - torch.diag_embed(dhp)
    if minus_identity:
        b = L * (hm - hp)[:, None, :] - torch.diag_embed(dhm - dhp)
    else:
        b = L * hm[:, None, :] - torch.diag_embed(dhm)
    st = torch.linalg.solve(a, b) / scale[:, :, None]
    k = kin.k_fm[:, ch.level]
    w = torch.sqrt(k[:, :, None] / k[:, None, :].clamp_min(1.0e-30))
    mask = (op[:, :, None] & op[:, None, :]).to(CDTYPE)
    return st * w.to(CDTYPE) * mask, op


# --------------------------------------------------------------- the sector form (CCPROP note 2)
# Why the cheap propagator above is only second order, and what fourth order costs.
#
# One sector [a, b] of width H propagates the log derivative by
#       Y(b) = Y4 - Y3 (Y(a) + Y1)^-1 Y2,
# and to first order in the potential, with the free reference f1 = (b-r)/H, f2 = (r-a)/H,
#       Y1 = 1/H + int f1^2 M,     Y4 = 1/H + int f2^2 M,     Y2 = Y3 = 1/H - int f1 f2 M.
# The kick-and-drift form is exactly this with `Y2 = Y3 = 1/H`, i.e. with the f1 f2 integral
# thrown away -- and that integral is H M / 6 for a constant M, an O(h^2) relative error in Y2 that
# no choice of node weight or of Johnson's (1 + h^2 M / 6)^-1 modification can put back, because a
# node kick only moves Y1 and Y4. That is the whole reason `log_derivative` converges at h^2.
#
# Keeping it makes Y2 and Y3 full matrices, so the sector costs one inverse **and two products**
# instead of one inverse: 24 N^3 against the renormalised Numerov's ~12.2 N^3 per step. The
# propagator family therefore brackets the incumbent rather than beating it -- cheaper at second
# order, twice as dear at fourth.


def log_derivative_sector(mm: Tensor, h_fm: Tensor, nmatch: Tensor, l_plus_1: Tensor) -> Tensor:
    """`log_derivative` with the f1 f2 term kept: M linear inside each sector gives

        Y1 = 1/h + h (3 M_a + M_b) / 12,  Y4 = 1/h + h (M_a + 3 M_b) / 12,
        Y2 = Y3 = 1/h - h (M_a + M_b) / 12,

    and one sector is one inverse plus the two products of Y3 (...)^-1 Y2."""
    n_e, n_r, n, _ = mm.shape
    eye = torch.eye(n, dtype=CDTYPE).expand(n_e, n, n)
    h = h_fm.to(CDTYPE)[:, None, None]
    hi = 1.0 / h
    r0 = h_fm[:, None]
    y = torch.diag_embed((l_plus_1[None, :] / r0).to(CDTYPE))
    out = torch.zeros((n_e, n, n), dtype=CDTYPE)
    done = torch.zeros(n_e, dtype=torch.bool)
    for i in range(int(nmatch.max()) + 1):
        hit = (nmatch == i) & ~done
        if bool(hit.any()):
            out = torch.where(hit[:, None, None], y, out)
            done = done | hit
            if bool(done.all()):
                break
        ma, mb = mm[:, i], mm[:, i + 1]
        y1 = hi * eye + (h / 12.0) * (3.0 * ma + mb)
        y4 = hi * eye + (h / 12.0) * (ma + 3.0 * mb)
        y2 = hi * eye - (h / 12.0) * (ma + mb)
        y = y4 - torch.matmul(y2, torch.linalg.solve(y + y1, y2))
    return out


# ------------------------------------------------------------------- the C kernel (ccprop.c)
# `log_derivative` again in C, so that the FLOP model of `harness/ccprop_flops.py` can be checked
# against a kernel's own count instead of trusted. Loaded exactly as `ccnative` loads `libccfast`.

_LIB = None
_TRIED = False


def native_available() -> bool:
    return _load_native() is not None


def _load_native():
    global _LIB, _TRIED
    if _TRIED:
        return _LIB
    _TRIED = True
    import ctypes
    import os
    import sys
    from pathlib import Path

    from physics.hf.ecis.ccnative import _torch_symbol

    lib_dir = Path(__file__).resolve().parents[1] / "native" / "lib"
    path = Path(os.environ.get("HF_CCPROP_LIB",
                               lib_dir / ("libccprop.dylib" if sys.platform == "darwin"
                                          else "libccprop.so")))
    if not path.is_file():
        return None
    try:
        lib = ctypes.CDLL(str(path))
        if lib.cc_prop_version() != 1:
            return None
    except OSError:
        return None
    addr = [_torch_symbol(n) for n in ("zgetrf_", "zgetri_", "zgetrs_")]
    if addr[0] is None or addr[2] is None:  # zgetri is optional: see ccprop.c::invert
        return None
    p, i64 = ctypes.c_void_p, ctypes.c_int64
    lib.cc_prop_set_lapack.argtypes = [p] * 3
    lib.cc_prop_set_lapack.restype = None
    lib.cc_prop_set_lapack(*addr)
    lib.cc_prop_w.argtypes = [i64] * 4 + [p] * 9 + [i64, p]
    lib.cc_prop_w.restype = ctypes.c_int
    lib.cc_prop_flops.argtypes = []
    lib.cc_prop_flops.restype = ctypes.c_double
    _LIB = lib
    return lib


def log_derivative_native(ch, ff, kin, h_fm: Tensor, nmatch: Tensor, r_fm: Tensor,
                          modified: bool = True) -> tuple[Tensor, float]:
    """`ccprop.c::cc_prop_w` for one block: (L, FLOPs the kernel issued)."""
    from physics.hf.ecis.ccnative import _common

    lib = _load_native()
    if lib is None:
        raise RuntimeError("libccprop not built (scripts/build_ccprop_native.sh)")
    n_e, n = int(h_fm.shape[0]), int(ch.level.numel())
    a = _common(ch, ff, kin, h_fm, nmatch, r_fm)
    lp1 = (ch.l.to(DTYPE) + 1.0).contiguous()
    out = torch.zeros((n_e, n, n), dtype=CDTYPE)
    rc = lib.cc_prop_w(n_e, n, int(r_fm.shape[1]), int(a["central"].shape[1]),
                       a["central"].data_ptr(), a["cpl"].data_ptr(), a["diagr"].data_ptr(),
                       a["so0"].data_ptr(), a["ls2"].data_ptr(), a["mu"].data_ptr(),
                       lp1.data_ptr(), a["h"].data_ptr(), a["nm"].data_ptr(), int(modified),
                       out.data_ptr())
    if rc != 0:
        raise RuntimeError(f"cc_prop_w returned {rc}")
    return out, float(lib.cc_prop_flops())
