"""SPEEDD: T7's photon strength function `fstrength` for many Egamma at once, with numpy arithmetic
and torch's own transcendental kernels -- the same numbers to the bit, a fraction of the calls.

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

Task: SPEEDD (the speed wave; no physics of its own). Acceptance test:
`tests/hf/test_decay_fast.py::test_psf_fast_is_fstrength_to_the_bit`.

TALYS routines this evaluates, as `gamma.strength.fstrength_gp` ports them:
    fstrength.f90:1 (fstrength)  -- standard Lorentzians, the tabulated E1 with its temperature
                                    interpolation, pygmy/scissors terms and the upbend

The decay widths call the strength function four times per cascade nucleus per incident energy on
a few thousand Egamma, and `fstrength_gp` spends that time in ~150 small torch operations, not in
arithmetic. This module repeats `fstrength_gp` operation by operation: sums, products, quotients,
comparisons, `where` and gathers in numpy (IEEE, the same values in the same order), and every
transcendental function -- sqrt, log10, pow, exp -- through the very torch call the original makes,
on an array of the same values. On x86 numpy's sqrt/exp/log10 can differ from torch's in the last
bit; torch's are kept for exactly that reason. It covers the models the port's defaults use
(`strength` 3, 4 or >= 6 with an E1 table or the standard Lorentzian, pygmy terms, the upbend) and
returns None for anything else (strength 1, 2 or 5, a table for M1, parameters on a graph), in
which case the caller uses `fstrength` itself.
"""

from __future__ import annotations

import numpy as np
import torch

from physics.hf.gamma.parameters import NUMGAMQRPA, table_arrays
from physics.hf.gamma.strength import _partition, kgr

_T = torch.float64


def _t(a: np.ndarray) -> torch.Tensor:
    return torch.from_numpy(a)


def _f(x) -> float:
    return float(x.detach()) if isinstance(x, torch.Tensor) else float(x)


def _supported(gp) -> bool:
    if gp.strength in (1, 2, 5, 11) or gp.strengthM1 == 11:
        return False
    if not (gp.strength in (3, 4) or gp.strength >= 6):
        return False
    if (0, 1) in gp.tables and gp.strengthM1 >= 8:  # a tabulated M1: not covered
        return False
    for v in (gp.egr_mev, gp.ggr_mev, gp.sgr_mb, gp.epr_mev, gp.gpr_mev, gp.tpr_mb, gp.upbend,
              gp.etable_mev, gp.ftable, gp.wtable, gp.S_k0_mev, gp.delta_mev, gp.alev_per_mev,
              gp.beta2):
        if isinstance(v, torch.Tensor) and v.requires_grad:
            return False
    return True


_TABLES: dict = {}


def _table(gp, irad: int):
    """table_arrays(gp, irad, 1) as numpy, with _locate's partition, cached per parameter set."""
    key = id(gp)
    got = _TABLES.get((key, irad))
    if got is None or got[0] is not gp:
        e_tab, f_tab = table_arrays(gp, irad, 1)
        xs = e_tab.detach()
        bps, j_at, j_in, j_nan = _partition(xs)
        got = (gp, e_tab.detach().numpy().copy(), f_tab.detach().numpy().copy(),
               bps.numpy(), j_at.numpy(), j_in.numpy(), j_nan)
        if len(_TABLES) > 512:
            _TABLES.clear()
        _TABLES[(key, irad)] = got
    return got[1:]


def _locate_np(tab, x: np.ndarray) -> np.ndarray:
    """gamma.strength._locate on numpy (integers, so exact)."""
    e_tab, _, bps, j_at, j_in, j_nan = tab
    ie = e_tab.shape[0] - 1
    pos = np.searchsorted(bps, x, side="left")
    pc = np.minimum(pos, bps.shape[0] - 1)
    hit = (pos < bps.shape[0]) & (bps[pc] == x)
    jl = np.where(hit, j_at[pc], j_in[pos])
    jl = np.where(np.isnan(x), j_nan, jl)
    j = np.where(x == e_tab[0], 0, jl)
    return np.where((x != e_tab[0]) & (x == e_tab[ie]), ie - 1, j)


def _log10(a: np.ndarray) -> np.ndarray:
    return torch.log10(_t(a)).numpy()


def _interp(e, eb, ee, gamb, game):
    """gamma.strength._interp: log10-linear when both ends > 0, else linear."""
    both = (gamb > 0.0) & (game > 0.0)
    safe_b = np.where(both, gamb, 1.0)
    safe_e = np.where(both, game, 1.0)
    frac = (e - eb) / (ee - eb)
    lb = _log10(safe_b)
    logv = torch.pow(10.0, _t(lb + frac * (_log10(safe_e) - lb))).numpy()
    lin = gamb + frac * (game - gamb)
    return np.where(both, logv, lin)


def _table_strength(gp, efs, e_gamma: np.ndarray, irad: int, l: int):  # noqa: E741
    tab = _table(gp, irad)
    e_tab, f_tab = tab[0], tab[1]
    n_t0 = gp.n_tqrpa if (irad == 1 and l == 1) else 1
    eq_last = e_tab[NUMGAMQRPA]
    if n_t0 > 1:
        e = np.minimum(efs, 20.0) + _f(gp.S_k0_mev) - _f(gp.delta_mev) - e_gamma
        alev = _f(gp.alev_per_mev)
        ok = (e > 0.0) & (alev > 0.0)
        tnuc = np.where(ok, torch.sqrt(_t(np.where(ok, e, 1.0) / alev)).numpy(), 0.0)
        tq = gp.tqrpa_mev.detach().numpy()
        n_t = np.minimum((tq[None, :] <= tnuc[:, None]).sum(-1), n_t0)
        tb = tq[np.maximum(n_t, 1) - 1]
        te = np.where(n_t < n_t0, tq[np.minimum(n_t, n_t0 - 1)], tb)
        itemp = 2
    else:
        tnuc = np.zeros_like(e_gamma)
        n_t = np.ones(e_gamma.shape, dtype=np.int64)
        tb = np.zeros_like(e_gamma)
        te = np.zeros_like(e_gamma)
        itemp = 1
    inside = e_gamma <= eq_last
    nen_in = np.clip(_locate_np(tab, e_gamma), 0, NUMGAMQRPA - 1)
    nen = np.where(inside, nen_in, NUMGAMQRPA - 1)
    fvals = []
    for it in range(1, itemp + 1):
        jt = n_t if it == 1 else n_t + 1
        jt = np.minimum(jt, n_t0)
        et = tb if it == 1 else te
        eb = e_tab[nen]
        ee = e_tab[nen + 1]
        col = jt - 1
        gamb = np.where(inside & ~(eb <= et), f_tab[nen, 0], f_tab[nen, col])
        game = np.where(inside & ~(ee <= et), f_tab[nen + 1, 0], f_tab[nen + 1, col])
        fvals.append(_interp(e_gamma, eb, ee, gamb, game))
    f2 = fvals[-1]
    if n_t0 > 1:
        fb, fe = fvals
        span = te - tb
        do_t = span != 0.0
        f_t = _interp(tnuc, tb, np.where(do_t, te, tb + 1.0), fb, fe)
        f2 = np.where(do_t, f_t, f2)
    return f2


def fstrength_np(gp, efs, e_gamma: np.ndarray, irad: int, l: int):  # noqa: E741
    """`gamma.strength.fstrength_gp(gp, efs, e_gamma, irad, l)` as float64 numpy, or None when this
    parameter set is outside what the module covers. `efs` a float or an array like e_gamma.

    TALYS: fstrength.f90:1 (fstrength)
    Test: tests/hf/test_decay_fast.py::test_psf_fast_is_fstrength_to_the_bit
    """
    if not _supported(gp):
        return None
    e_gamma = np.asarray(e_gamma, dtype=np.float64)
    flag_m1 = irad == 0 and l == 1
    flag_e1 = irad == 1 and l == 1
    out = np.zeros_like(e_gamma)
    egam2 = e_gamma * e_gamma  # torch's x**2 is the product
    k = kgr(l)
    pw = None
    for i in range(1, gp.ngr[irad][l] + 1):
        sgr1 = _f(gp.sgr_mb[irad, l, i])
        egr1 = _f(gp.egr_mev[irad, l, i])
        ggr1 = _f(gp.ggr_mev[irad, l, i])
        egr2 = egr1 * egr1
        ggr2 = ggr1 * ggr1
        slo = (not gp.qrpaexist(1, 1)) or l != 1 or irad != 1
        if slo:
            pos = e_gamma > 0.001
            if pw is None:
                pw = torch.pow(_t(e_gamma), 3 - 2 * l).numpy()
            enum = ggr2 * pw
            d = egam2 - egr2
            denom = d * d + egam2 * ggr2
            out = out + np.where(pos, k * sgr1 * enum / denom, 0.0)
        if gp.qrpaexist(1, 1) and flag_e1:  # assignment, not a sum (fstrength.f90:356)
            out = _table_strength(gp, efs, e_gamma, irad, l)
    for i in (1, 2):
        tpr1 = _f(gp.tpr_mb[irad, l, i])
        if tpr1 <= 0.0:
            continue
        epr = _f(gp.epr_mev[irad, l, i])
        gpr = _f(gp.gpr_mev[irad, l, i])
        epr2, gpr2 = epr * epr, gpr * gpr
        pos = e_gamma > 0.001
        if pw is None:
            pw = torch.pow(_t(e_gamma), 3 - 2 * l).numpy()
        enum = gpr2 * pw
        d = egam2 - epr2
        denom = d * d + egam2 * gpr2
        out = out + np.where(pos, k * tpr1 * enum / denom, 0.0)
    if gp.flagupbend:
        upc = _f(gp.upbend[irad, l, 1])
        upe = _f(gp.upbend[irad, l, 2])
        upf = _f(gp.upbend[irad, l, 3])
        if gp.strengthM1 in (8, 10) and flag_m1 and gp.zix + gp.nix >= 105:
            upf = upf * 0.0
        if flag_e1:
            e = np.minimum(efs, 20.0) + _f(gp.S_k0_mev)
            ex = torch.exp(_t(e_gamma - upe)).numpy()
            if np.ndim(e) and np.size(e) > 1:
                out = out + np.where(e > 1.0, upc * e / (1.0 + ex), 0.0)
            elif float(e) > 1.0:
                out = out + upc * e / (1.0 + ex)
        if irad == 0:
            beta2 = torch.as_tensor(_f(gp.beta2), dtype=_T)
            x2 = float(torch.exp(-upf * torch.abs(beta2)))
            out = out + upc * torch.exp(_t(-upe * e_gamma)).numpy() * x2
    return out
