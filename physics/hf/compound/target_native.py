"""NATIVEX: `target_batch.case_nowfc` and `case_moldauer` in one compiled call per incident energy.

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

Task: NATIVEX (the speed work; no physics of its own). Acceptance test: `tests/hf/test_nativex.py`,
which holds it to `target_batch`'s torch path, and the G-NATIVEX closeness gate.

TALYS routines this computes (in `native/nativex.c`, arranged as `target_batch` arranges them):
    comptarget.f90:1 (comptarget)      -- the (J, parity) sum, with and without Moldauer
    compprepare.f90:1 (compprepare)    -- denomhf and the exit-channel selection rules
    molprepare.f90:1 (molprepare)      -- the Gauss-Laguerre node product, fission humps included
    moldauer.f90:1 (moldauer)          -- G_b, G_gamma and the elastic E_a

On the Mac a spherical target's `case_moldauer` was ~20 % of the nuclide, and it was array
compute on small tensors: `_prepare`'s einsums over (cells, residual spin, parity, rows, l',
updown), then `log1p` and the node sums. The kernel takes the residual arrays as `_prepare` does
and walks only the (row, l', updown) entries with a transmission; the spin selection rule of a
(J2, l', updown) is an interval in the residual spin, so every weight sum and population scatter
is a loop over that interval. The sums run in loop order, so cells move by rounding only.

Covered: numpy inputs (no tensor on a graph), widthmode 0 or 1, any `wfcfactor`, fission
(`compound.fission_batch_target`'s `tfis` and Hill-Wheeler humps). Everything else returns None
and the torch path runs, as it did.
"""

from __future__ import annotations

import numpy as np
import torch

from physics.hf.compound import fission_batch_target as fbt
from physics.hf.compound.prepare import NUMJ
from physics.hf.core.tensors import DTYPE
from physics.hf.native import nativex

_I64 = np.int64


def _arr(a, dtype, n: int | None = None):
    if isinstance(a, torch.Tensor):
        return None
    v = np.asarray(a)
    if n is not None:
        v = v[:n]
    return np.ascontiguousarray(v, dtype=dtype)


def target(inp, wfc: bool, max_nex: int | None):
    """(pop (7, Nex, numJ+1, 2), xs_fis) as `target_batch.case_nowfc` (`wfc` False) or
    `case_moldauer` (`wfc` True) return them, or None where the kernel does not apply.

    TALYS: comptarget.f90:1 (comptarget), molprepare.f90:1 (molprepare), moldauer.f90:1 (moldauer)
    Test: tests/hf/test_nativex.py
    """
    so = nativex.lib()
    if so is None or isinstance(inp.tjlinc, torch.Tensor):
        return None
    if wfc and inp.wfcfactor not in (1, 2, 3):
        return None
    nexmax = max_nex or max(r.maxex + 1 for r in inp.residuals.values())
    cells = [(J2, p) for p in (-1, 1) for J2 in range(inp.j2beg, inp.j2end + 1, 2)]
    pop = np.zeros((7, nexmax, NUMJ + 1, 2))
    if not cells:
        return torch.from_numpy(pop), torch.zeros((), dtype=DTYPE)
    k0, lt = inp.k0, inp.ltarget
    if wfc and k0 in inp.residuals and lt > inp.residuals[k0].nlast:
        return None
    K = len(cells)
    ip = np.zeros(20 + 8 * 7, dtype=_I64)
    pp = np.zeros(10 + 6 * 7, dtype=np.uint64)
    keep = []

    def put(slot, a):
        keep.append(a)
        pp[slot] = nativex.ptr(a)

    order = list(inp.residuals)
    if len(order) > 7 or any(not 0 <= t <= 6 for t in order):
        return None
    for t, r in inp.residuals.items():
        nex = r.maxex + 1
        if nex > nexmax:
            return None
        rho = _arr(r.rho, np.float64)
        if rho is None or rho.shape[0] < nex or rho.shape[1] != NUMJ + 1:
            return None
        rho = np.ascontiguousarray(rho[:nex])
        if t == 0:
            if r.tgam is None or isinstance(r.tgam, torch.Tensor):
                return None
            tg = np.asarray(r.tgam)
            if not bool((tg == tg[..., :1, :1]).all()):
                return None  # a J/P-dependent photon transmission: the torch path's None too
            T = np.ascontiguousarray(tg[:nex, :, :, 0, 0], dtype=np.float64)
        else:
            if r.tjl is None or isinstance(r.tjl, torch.Tensor):
                return None
            T = np.ascontiguousarray(np.asarray(r.tjl)[:nex], dtype=np.float64)
        L = T.shape[1]
        arrs = [_arr(r.lmaxhf, _I64, nex), _arr(r.maxj, _I64, nex), _arr(r.jdis2, _I64, nex),
                _arr(r.parlev, _I64, nex)]
        if any(a is None or a.shape[0] < nex for a in arrs):
            return None
        ip[20 + 8 * t: 20 + 8 * t + 6] = (1, nex, r.nlast, L, r.spin2, r.parspin2)
        for j, a in enumerate([rho, *arrs, T]):
            put(10 + 6 * t + j, a)
    j2 = np.array([c[0] for c in cells], dtype=_I64)
    pidx = np.array([0 if c[1] == -1 else 1 for c in cells], dtype=_I64)
    tjlinc = np.ascontiguousarray(np.asarray(inp.tjlinc), dtype=np.float64)
    put(0, j2)
    put(1, pidx)
    put(2, tjlinc)
    fis = fbt.cell_fission_widths(inp, cells)
    has_fis = fis is not None
    if has_fis:
        put(3, np.ascontiguousarray(fis.numpy(), dtype=np.float64))
        if wfc:
            ratio, th, rho_h, on = fbt.hump_channels(inp, cells, fis)
            put(4, np.ascontiguousarray(ratio.numpy()))
            put(5, np.ascontiguousarray(th.numpy()))
            put(6, np.ascontiguousarray(rho_h.numpy()))
            put(7, np.ascontiguousarray(on.numpy().astype(_I64)))
    x, w = _nodes()
    put(8, x)
    put(9, w)
    ip[:12] = (K, int(wfc), inp.wfcfactor if wfc else 1, k0, lt, nexmax, int(has_fis),
               inp.targetspin2, inp.target_parity, inp.lmaxinc, tjlinc.shape[0], len(order))
    ip[12:12 + len(order)] = order
    dp = np.array([float(inp.cnfactor_mb)])
    out = np.zeros(2)
    rc = so.nx_target(nativex.ptr(ip), nativex.ptr(pp), nativex.ptr(dp), nativex.ptr(pop),
                      nativex.ptr(out))
    if rc != 0:
        return None
    return torch.from_numpy(pop), torch.tensor(out[0], dtype=DTYPE)


_NODES: tuple | None = None


def _nodes():
    global _NODES
    if _NODES is None:
        from physics.hf.compound import wfc

        x, w = wfc.gauss_laguerre()
        _NODES = (np.ascontiguousarray(x.numpy()), np.ascontiguousarray(w.numpy()))
    return _NODES
