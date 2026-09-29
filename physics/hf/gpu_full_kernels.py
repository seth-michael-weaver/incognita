"""Fused kernels of `gpu_full_cascade`: the per-bin exit arrays, widths and particle feeding, and
one step of the mother-bin walk, as pure tensor functions that `torch.compile` fuses.

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

Task: GPUFULL2 (gate G-GF2, docs/results/hf-gpu-full.md). No physics of its own: every function
here is a statement-for-statement copy of `gpu_full_cascade.exit_arrays`, `widths_of`, `feed_of`
and the body of `_decay_chunk`'s walk, with the object and dict lookups moved out so that a
function sees tensors and a few static ints only. The eager path measured 3.6 M aten launches per
480 heavy runs (~14 us each on the laptop), which is the whole of its wall time; a compiled
function is one launch of a handful of fused kernels, and its intermediates of shape
(rows, bins, residual rows, l') are not materialised, so the bin chunks can be larger too.

**Rounding.** Inductor emits the same float64 operations in the same order within an expression;
reductions (sums, einsums lowered to bmm) may group terms differently, which moves last bits
(<= 1e-15 relative), the same class of change the batch axis already makes.

`COMPILE` (env `GPUFULL_COMPILE`, default on when a C compiler and Python.h are found) switches
`torch.compile` off; the eager functions compute the same numbers.

Test: GPUFULL2 / tests/hf/test_gpu_full.py
"""

from __future__ import annotations

import os

import torch
from torch import Tensor

F64 = torch.float64
F32 = torch.float32
NUMJ = 40


def _can_compile() -> bool:
    """Triton builds its launcher with a C compiler against Python.h: without both, eager.
    (On a micromamba install both come from the micromamba env: CC=.../incognita-phys/bin/gcc and
    CPATH=.../incognita-phys/include/python3.12.)"""
    import shutil
    import sysconfig

    cc = os.environ.get("CC") or shutil.which("cc") or shutil.which("gcc") or shutil.which("clang")
    inc = [sysconfig.get_paths()["include"]] + os.environ.get("CPATH", "").split(os.pathsep)
    return bool(cc) and any(p and os.path.exists(os.path.join(p, "Python.h")) for p in inc)


COMPILE = os.environ.get("GPUFULL_COMPILE", "1") != "0" and _can_compile()


def _compiled(fn):
    if not COMPILE:
        return fn
    import torch._dynamo

    torch._dynamo.config.cache_size_limit = max(torch._dynamo.config.cache_size_limit, 256)
    # GPU3: sizes that happen to be equal are not one symbol (duck sizing), or a later call
    # with them unequal recompiles, possibly inside a CUDA-graph capture
    import torch.fx.experimental._config as fx_config

    fx_config.use_duck_shape = False
    if hasattr(torch._dynamo.config, "recompile_limit"):
        torch._dynamo.config.recompile_limit = max(torch._dynamo.config.recompile_limit, 256)
    return torch.compile(fn, dynamic=True, fullgraph=True)


# ------------------------------------------------------------------------------------ geometry


def _geometry(bins: Tensor, binm: Tensor, nexm_raw: Tensor, ex_m: Tensor, dex_m: Tensor,
              sep_t: Tensor, d_ex: Tensor, d_dex: Tensor, d_nlast: Tensor, ty: int):
    """`exit_arrays`' residual-row geometry: (inrow, rb, below, part, emin, emax, exinc, ex0plus,
    exm) for mother bins `bins` (n, mc) into the daughter rows (n, Rt).

    TALYS: densprepare.f90:1 (densprepare)
    Test: GPUFULL2
    """
    Rt = d_ex.shape[1]
    exinc = ex_m.gather(1, bins)
    dexinc = dex_m.gather(1, bins)
    rows = torch.arange(Rt, device=bins.device)
    nexm = torch.clamp(nexm_raw, min=0)
    inrow = (rows[None, None, :] <= nexm[..., None]) & binm[..., None]
    ex = d_ex[:, None, :]
    dexhalf = 0.5 * d_dex[:, None, :]
    ss = sep_t[:, None, None]
    ex0plus = (exinc + 0.5 * dexinc)[..., None]
    ex0min = (exinc - 0.5 * dexinc)[..., None]
    ex1min = ex - dexhalf
    top = (rows[None, None, :] == nexm[..., None]) & (ty >= 1)
    ex1plus = torch.where(top, ex0plus - ss, ex + dexhalf)
    emax = (ex0plus - ss) - ex1min
    emin = (ex0min - ss) - ex1plus
    eout_mid = 0.5 * (emin + emax)
    below = emin < 0.0
    half = 0.5 * (emax - emin)
    halfs = torch.where(below, half, 1.0)
    rb_c = torch.where(below, torch.where(eout_mid > 0.0, 1.0 - 0.5 * (emin / halfs) ** 2,
                                          0.5 * (emax / halfs) ** 2), 1.0)
    cont_row = rows[None, None, :] > d_nlast[:, None, None]
    exm = ex + ss
    part = (ex0min < exm) & (exm <= ex0plus)
    dexs = torch.where(part, dexinc[..., None], 1.0)
    rb_d = torch.where(part, (ex0plus - exm) / dexs, 1.0)
    rb = torch.where(cont_row, rb_c, rb_d)
    return inrow, rb, below, part, emin, emax, exinc, ex0plus, exm, ss, ex, cont_row, nexm


def _rho_discrete(rb: Tensor, inrow: Tensor, dmask: Tensor, dfac: Tensor) -> Tensor:
    """`exit_arrays`' discrete rows: rho_d (n, mc, ND); `dmask` (n, ND) holds `same`, the row
    range and the nlast = 0 cut, `dfac` (n, ND) discfactor above Ntop and 1 below."""
    ND = dmask.shape[1]
    rbd = rb[:, :, :ND]
    val = rbd * dfac[:, None, :]
    rho_d = torch.where(dmask[:, None, :] & inrow[:, :, :ND], val, 0.0)
    return torch.where(rho_d >= 1.0e-20, rho_d, 0.0)


def particle_nodes(bins, binm, nexm_raw, ex_m, dex_m, sep_t, d_ex, d_dex, d_nlast, egrid_r,
                   egrid32_r, ib, ie, maxen, lmax_r, head0, lmaxinc, ty: int, is_k0: bool):
    """`exit_arrays` for a particle exit up to the transmissions, dense over (row, bin, residual
    row): Rboundary `rb` (0 outside the bin's reach), the pol2 node `na` and weights `w1..w3` of
    the emission energy, the l' cap `lcap` (-1: no transmission), and `live`, the cells where
    `rb * T` can be non-zero.

    TALYS: densprepare.f90:1 (densprepare), locate.f90:1 (locate)
    Test: GPUFULL2
    """
    n, mc = bins.shape
    Rt = d_ex.shape[1]
    (inrow, rb, below, part, emin, emax, exinc, ex0plus, exm, ss, ex, cont_row,
     nexm) = _geometry(bins, binm, nexm_raw, ex_m, dex_m, sep_t, d_ex, d_dex, d_nlast, ty)
    eout_c = 0.5 * (torch.where(below, 0.0, emin) + emax)
    eout_d = torch.where(part, 0.5 * (ex0plus + exm) - ss - ex, (exinc[..., None] - ss) - ex)
    e = torch.where(inrow, torch.where(cont_row, eout_c, eout_d), 0.0).reshape(n, mc * Rt)
    # interp_nodes with the nuclide's grid per row
    x = e.to(torch.float32)
    jl = torch.searchsorted(egrid32_r, x, right=True) - 1
    jl = torch.maximum(torch.minimum(jl, ie[:, None]), ib[:, None] - 1)
    xib = egrid32_r.gather(1, ib[:, None])
    xie = egrid32_r.gather(1, ie[:, None])
    jl = torch.where(x == xib, ib[:, None], torch.where(x == xie, ie[:, None] - 1, jl))
    lo = egrid_r.gather(1, ib[:, None])
    nen = torch.where(e < lo, torch.zeros_like(jl), jl)
    centred = (nen > ib[:, None] + 1) | (nen >= maxen[:, None] - 1)
    na = torch.where(centred, nen - 1, nen)
    nb, nc = na + 1, na + 2
    ea, eb, ec = egrid_r.gather(1, na), egrid_r.gather(1, nb), egrid_r.gather(1, nc)
    w1 = (e - eb) * (e - ec) / ((ea - eb) * (ea - ec))
    w2 = (e - ea) * (e - ec) / ((eb - ea) * (eb - ec))
    w3 = (e - ea) * (e - eb) / ((ec - ea) * (ec - eb))
    lm = lmax_r.gather(1, torch.minimum(torch.clamp(nen, min=0), maxen[:, None]))
    below_e = (e < lo).reshape(n, mc, Rt)
    ok = (ib < ie)[:, None, None]
    lm = lm.reshape(n, mc, Rt)
    inr = inrow & ok
    base = torch.where(inr, lm, 0)
    rows = torch.arange(Rt, device=bins.device)
    prev = base.gather(2, torch.clamp(nexm - 1, min=0)[..., None])
    at = (rows[None, None, :] == nexm[..., None]) & (nexm > 0)[..., None]
    lmaxhf = torch.where(at, prev, base)
    if is_k0:
        lmaxhf = torch.where((rows == 0)[None, None, :], lmaxinc[:, None, None], lmaxhf)
    lcap = torch.minimum(lm, lmaxhf)
    lcap = torch.where(inr & ~(below_e & head0[:, None, None]), lcap, -1)
    rb = torch.where(inrow, rb, 0.0)
    rs = lambda v: v.reshape(n, mc, Rt)  # noqa: E731
    return rb, lcap, rs(na), rs(w1), rs(w2), rs(w3), inrow, (lcap >= 0) & (rb != 0.0)


def _particle_T(bins, binm, nexm_raw, ex_m, dex_m, sep_t, d_ex, d_dex, d_nlast, egrid_r,
                egrid32_r, ib, ie, maxen, lmax_r, TL_r, head0, eps, fn, lmaxinc, dmask, dfac,
                ty: int, is_k0: bool):
    """`exit_arrays` for a particle exit: (rb, T (n, mc, Rt, L), rho_d), dense.

    TALYS: densprepare.f90:1 (densprepare), locate.f90:1 (locate)
    Test: GPUFULL2
    """
    n, mc = bins.shape
    Rt = d_ex.shape[1]
    L = TL_r.shape[2]
    rb, lcap, na, w1, w2, w3, inrow, _live = particle_nodes(
        bins, binm, nexm_raw, ex_m, dex_m, sep_t, d_ex, d_dex, d_nlast, egrid_r, egrid32_r, ib, ie,
        maxen, lmax_r, head0, lmaxinc, ty, is_k0)
    bi = torch.arange(n, device=bins.device)[:, None]
    na, w1, w2, w3 = (v.reshape(n, mc * Rt) for v in (na, w1, w2, w3))
    u = (w1[..., None] * TL_r[bi, na] + w2[..., None] * TL_r[bi, na + 1]
         + w3[..., None] * TL_r[bi, na + 2]).reshape(n, mc, Rt, L)
    lp = torch.arange(L, device=bins.device)
    T = torch.where((lp <= lcap[..., None]) & (u >= eps[:, None, None, None]),
                    u * fn[:, None, None, None], 0.0)
    return rb, T, _rho_discrete(rb, inrow, dmask, dfac)


# ------------------------------------------------------------------------------ ragged rows
#
# `rb * T` of a particle exit is non-zero on ~3% of the dense (row, bin, residual row, l') cells
# of a heavy chunk (a bin reaches only the residual rows under its nexmax, and T only the l' under
# its cap), and FP64 bmm on the laptop GPU runs at ~50 GFLOP/s. So the contractions run on the
# list of live (row, bin, residual row) triples, `particle_nodes`' `live`, as fused reductions:
# the same products, summed per triple and then per (row, bin), which moves the last bits only.


def particle_rows(rb, lcap, na, w1, w2, w3, idx, TL_r, eps, fn, br_map, mc: int, Rt: int):
    """The live triples `idx` (flat over (n, mc, Rt)): their row/bin/residual-row indices, their
    row in the compact Q table (`br_map` over (n, Rt)), `rb` and transmissions T (nr, L).

    TALYS: densprepare.f90:1 (densprepare)
    Test: GPUFULL2
    """
    b = torch.div(idx, mc * Rt, rounding_mode="floor")
    m = torch.div(idx, Rt, rounding_mode="floor") % mc
    r = idx % Rt
    L = TL_r.shape[2]
    rb_r = rb.reshape(-1)[idx]
    na_r = na.reshape(-1)[idx]
    u = (w1.reshape(-1)[idx][:, None] * TL_r[b, na_r] + w2.reshape(-1)[idx][:, None]
         * TL_r[b, na_r + 1] + w3.reshape(-1)[idx][:, None] * TL_r[b, na_r + 2])
    lp = torch.arange(L, device=idx.device)
    T = torch.where((lp[None, :] <= lcap.reshape(-1)[idx][:, None]) & (u >= eps[b][:, None]),
                    u * fn[b][:, None], 0.0)
    return b, m, r, br_map[b * Rt + r], rb_r, T


def _rows_discrete(b, r, rb_r, T, Md, pd, dmask, dfac):
    ND = dmask.shape[1]
    rc = r.clamp(max=ND - 1)
    rd = torch.where((r < ND) & dmask[b, rc], rb_r * dfac[b, rc], 0.0)
    rd = torch.where(rd >= 1.0e-20, rd, 0.0)
    pdv = pd[b, rc]
    L = T.shape[1]
    T0 = T * (torch.arange(L, device=T.device) % 2 == 0)
    T1 = T - T0
    return rc, rd, pdv, T0, T1


def widths_rows(b, m, r, qrow, rb_r, T, Qr, Md, pd, dmask, dfac, sfac: float, n: int, mc: int,
                NJ: int):
    """`widths_of` on the live triples: D (n, mc, NJ, 2).

    TALYS: compound.f90:1 (compound)
    Test: GPUFULL2
    """
    L = T.shape[1]
    Wr = rb_r[:, None] * T  # (nr, L)
    cont = (Wr[:, :, None] * Qr[qrow]).sum(1)  # (nr, NJ*2)
    rc, rd, pdv, T0, T1 = _rows_discrete(b, r, rb_r, T, Md, pd, dmask, dfac)
    md = Md[b, :, rc]  # (nr, NJ, L)
    r_par = (rd * (pdv == 1))[:, None, None]
    r_npar = (rd * (pdv == 0))[:, None, None]
    dd0 = (md * (T0[:, None, :] * r_npar + T1[:, None, :] * r_par)).sum(2)
    dd1 = (md * (T0[:, None, :] * r_par + T1[:, None, :] * r_npar)).sum(2)
    tot = cont.reshape(-1, NJ, 2) + torch.stack([dd0, dd1], -1)
    D = torch.zeros((n * mc, NJ, 2), dtype=F64, device=T.device)
    D = D.index_add(0, b * mc + m, tot)
    return sfac * D.reshape(n, mc, NJ, 2)


def feed_rows(b, m, r, qrow, rb_r, T, Qr, Md, pd, dmask, dfac, F, sfac: float, n: int, mc: int,
              Rt: int):
    """`feed_of` on the live triples, without Z: mcont (n, mc, Rt) with the discrete cells
    added and fd (n, mc, ND).

    TALYS: compound.f90:1 (compound)
    Test: GPUFULL2
    """
    NJ2 = F.shape[2] * 2
    ND = dmask.shape[1]
    L = T.shape[1]
    Fr = F.reshape(n * mc, NJ2)[b * mc + m]  # (nr, NJ*2)
    Wr = rb_r[:, None] * T
    H = (Fr[:, None, :] * Qr[qrow]).sum(2)  # (nr, L)
    mc_r = (H * Wr).sum(1) * sfac
    rc, rd, pdv, T0, T1 = _rows_discrete(b, r, rb_r, T, Md, pd, dmask, dfac)
    md = Md[b, :, rc]  # (nr, NJ, L)
    tot0 = (md * T0[:, None, :]).sum(2)  # (nr, NJ)
    tot1 = (md * T1[:, None, :]).sum(2)
    Fj = Fr.reshape(-1, NJ2 // 2, 2)
    A = (Fj * tot0[:, :, None]).sum(1)  # (nr, 2)
    Bq = (Fj * tot1[:, :, None]).sum(1)
    fd_r = (A.gather(1, pdv[:, None])[:, 0] + Bq.gather(1, (1 - pdv)[:, None])[:, 0])
    fd_r = torch.where(r < ND, sfac * rd * fd_r, 0.0)
    mcont = torch.zeros((n * mc * Rt,), dtype=F64, device=T.device)
    mcont = mcont.index_put(((b * mc + m) * Rt + r,), mc_r + fd_r)
    fd = torch.zeros((n * mc * ND + 1,), dtype=F64, device=T.device)
    fd = fd.index_put((torch.where(r < ND, (b * mc + m) * ND + rc, n * mc * ND),), fd_r)
    return mcont.reshape(n, mc, Rt), fd[: n * mc * ND].reshape(n, mc, ND)


def widths_rows32(b, m, r, qrow, rb_r, T, Qs, qs, Md, pd, dmask, dfac, sfac: float, n: int,
                  mc: int, NJ: int):
    """`widths_rows` with the contractions in float32 (GPU3): the compact Q table is carried as
    `Qs` (float32, each (pair, J, parity) column divided by its largest value `qs`), the
    per-triple sums are formed in float32 and scaled back and accumulated in float64.

    TALYS: compound.f90:1 (compound)
    Test: GPU3
    """
    Wr = (rb_r[:, None] * T).to(F32)  # (nr, L)
    cont = (Wr[:, :, None] * Qs[qrow]).sum(1).to(F64) * qs[qrow]  # (nr, NJ*2)
    rc, rd, pdv, T0, T1 = _rows_discrete(b, r, rb_r, T, Md, pd, dmask, dfac)
    md = Md[b, :, rc]  # (nr, NJ, L) bool
    S0 = (md * T0.to(F32)[:, None, :]).sum(2).to(F64)
    S1 = (md * T1.to(F32)[:, None, :]).sum(2).to(F64)
    r_par = (rd * (pdv == 1))[:, None]
    r_npar = (rd * (pdv == 0))[:, None]
    dd0 = S0 * r_npar + S1 * r_par
    dd1 = S0 * r_par + S1 * r_npar
    tot = cont.reshape(-1, NJ, 2) + torch.stack([dd0, dd1], -1)
    D = torch.zeros((n * mc, NJ, 2), dtype=F64, device=T.device)
    D = D.index_add(0, b * mc + m, tot)
    return sfac * D.reshape(n, mc, NJ, 2)


def feed_rows32(b, m, r, qrow, rb_r, T, Qs, qs, Md, pd, dmask, dfac, F, sfac: float, n: int,
                mc: int, Rt: int):
    """`feed_rows` with the (J, parity) x l' contraction in float32 (GPU3): the feeding times
    the column scales is divided by its largest value per triple, contracted with `Qs` and `W`
    in float32, and scaled back in float64.

    TALYS: compound.f90:1 (compound)
    Test: GPU3
    """
    NJ2 = F.shape[2] * 2
    ND = dmask.shape[1]
    Fr = F.reshape(n * mc, NJ2)[b * mc + m]  # (nr, NJ*2)
    G = Fr * qs[qrow]
    gs = G.amax(1)
    gs = torch.where(gs > 0.0, gs, 1.0)
    Gs = (G / gs[:, None]).to(F32)
    Wr = (rb_r[:, None] * T).to(F32)
    H = (Gs[:, None, :] * Qs[qrow]).sum(2)  # (nr, L)
    mc_r = (H * Wr).sum(1).to(F64) * gs * sfac
    rc, rd, pdv, T0, T1 = _rows_discrete(b, r, rb_r, T, Md, pd, dmask, dfac)
    md = Md[b, :, rc]  # (nr, NJ, L) bool
    tot0 = (md * T0.to(F32)[:, None, :]).sum(2).to(F64)  # (nr, NJ)
    tot1 = (md * T1.to(F32)[:, None, :]).sum(2).to(F64)
    Fj = Fr.reshape(-1, NJ2 // 2, 2)
    A = (Fj * tot0[:, :, None]).sum(1)  # (nr, 2)
    Bq = (Fj * tot1[:, :, None]).sum(1)
    fd_r = (A.gather(1, pdv[:, None])[:, 0] + Bq.gather(1, (1 - pdv)[:, None])[:, 0])
    fd_r = torch.where(r < ND, sfac * rd * fd_r, 0.0)
    mcont = torch.zeros((n * mc * Rt,), dtype=F64, device=T.device)
    mcont = mcont.index_put(((b * mc + m) * Rt + r,), mc_r + fd_r)
    fd = torch.zeros((n * mc * ND + 1,), dtype=F64, device=T.device)
    fd = fd.index_put((torch.where(r < ND, (b * mc + m) * ND + rc, n * mc * ND),), fd_r)
    return mcont.reshape(n, mc, Rt), fd[: n * mc * ND].reshape(n, mc, ND)


def _dense32(b, m, r, v, n: int, mc: int, Rt: int):
    """Scatter per-triple rows `v` (nr, L) into a dense float32 (n, mc, Rt, L) (flat (n mc Rt, L))."""
    L = v.shape[1]
    out = torch.zeros((n * mc * Rt, L), dtype=F32, device=v.device)
    return out.index_put_(((b * mc + m) * Rt + r,), v.to(F32))


def _lwin(T, lb, le, b, rc):
    """sum of T (nr, L) over l' in [lb, le] of the triple's discrete level (tables (n, NJ, ND)),
    even and odd l' apart: (nr, NJ) each. `_mask_for`'s l' window as prefix/suffix differences,
    each taking the difference that subtracts the smaller part."""
    nr, L = T.shape
    TE = T * (torch.arange(L, device=T.device) % 2 == 0)
    TO = T - TE
    lo = lb[b, :, rc]
    hi = le[b, :, rc]
    a = lo.clamp(0, L)
    b1 = (hi + 1).clamp(0, L)
    empty = (lo > hi) | (b1 <= a)
    out = []
    for X in (TE, TO):
        P = torch.nn.functional.pad(torch.cumsum(X, 1), (1, 0))
        S = torch.nn.functional.pad(torch.cumsum(X.flip(1), 1).flip(1), (0, 1))
        Pa, Pb, Sa, Sb = P.gather(1, a), P.gather(1, b1), S.gather(1, a), S.gather(1, b1)
        v = torch.where(Pa <= Sb, Pb - Pa, Sa - Sb)
        out.append(torch.where(empty, 0.0, torch.clamp(v, min=0.0)))
    return out[0], out[1]


def widths_dense32(b, m, r, rb_r, T, Qs, qs, lb, le, pd, dmask, dfac, sfac: float, n: int,
                   mc: int, Rt: int, NJ: int):
    """`widths_rows` with the live triples scattered into a dense float32 (n, mc, Rt*L) and the
    continuum contraction as a float32 bmm (GPU3): `Qs` (n, Rt*L, NJ*2) is the rows' Q table
    with each (J, parity) column divided by its largest value `qs` (n, NJ*2). The discrete levels
    take the l' window of `lb`/`le` as prefix differences (float64).

    TALYS: compound.f90:1 (compound)
    Test: GPU3
    """
    L = T.shape[1]
    W = _dense32(b, m, r, rb_r[:, None] * T, n, mc, Rt).view(n, mc, Rt * L)
    D = (torch.bmm(W, Qs).to(F64) * qs[:, None, :]).reshape(n, mc, NJ, 2)
    rc, rd, pdv, _T0, _T1 = _rows_discrete(b, r, rb_r, T, None, pd, dmask, dfac)
    SE, SO = _lwin(T, lb, le, b, rc)
    r_par = (rd * (pdv == 1))[:, None]
    r_npar = (rd * (pdv == 0))[:, None]
    dd = torch.stack([SE * r_npar + SO * r_par, SE * r_par + SO * r_npar], -1)
    Dd = torch.zeros((n * mc, NJ, 2), dtype=F64, device=T.device).index_add(0, b * mc + m, dd)
    return sfac * (D + Dd.reshape(n, mc, NJ, 2))


def feed_dense32(b, m, r, rb_r, T, Qs, qs, lb, le, pd, dmask, dfac, F, fr, sfac: float, n: int,
                 mc: int, Rt: int, NJ: int):
    """`feed_rows` and `z_rows` as float32 bmms on the dense triples (GPU3): Z (n, Rt*L, NJ*2)
    in units of the row scale `fr`, mcont (n, mc, Rt) with the discrete cells added, and fd.

    TALYS: compound.f90:1 (compound), multiple.f90:1 (multiple)
    Test: GPU3
    """
    ND = dmask.shape[1]
    L = T.shape[1]
    NJ2 = NJ * 2
    W = _dense32(b, m, r, rb_r[:, None] * T, n, mc, Rt).view(n, mc, Rt * L)
    Fm = F.reshape(n, mc, NJ2)
    Zs = torch.bmm(W.transpose(1, 2), (Fm / fr[:, None, None]).to(F32))
    G = Fm * qs[:, None, :]
    gs = G.amax(2)
    gs = torch.where(gs > 0.0, gs, 1.0)
    H = torch.bmm((G / gs[..., None]).to(F32), Qs.transpose(1, 2))  # (n, mc, Rt*L)
    mcont = ((H * W).reshape(n, mc, Rt, L).sum(3).to(F64) * (gs * sfac)[..., None]).reshape(-1)
    rc, rd, pdv, _T0, _T1 = _rows_discrete(b, r, rb_r, T, None, pd, dmask, dfac)
    SE, SO = _lwin(T, lb, le, b, rc)
    Fj = F.reshape(n * mc, NJ, 2)[b * mc + m]  # (nr, NJ, 2)
    A = (Fj * SE[:, :, None]).sum(1)
    Bq = (Fj * SO[:, :, None]).sum(1)
    fd_r = (A.gather(1, pdv[:, None])[:, 0] + Bq.gather(1, (1 - pdv)[:, None])[:, 0])
    fd_r = torch.where(r < ND, sfac * rd * fd_r, 0.0)
    mcont = mcont.index_add(0, (b * mc + m) * Rt + r, fd_r)
    fd = torch.zeros((n * mc * ND + 1,), dtype=F64, device=T.device)
    fd = fd.index_put((torch.where(r < ND, (b * mc + m) * ND + rc, n * mc * ND),), fd_r)
    return Zs, mcont.reshape(n, mc, Rt), fd[: n * mc * ND].reshape(n, mc, ND)


def q_table32(rhogrid, maxj, nlast, base: int, Mp, NJ: int):
    """`exit_Q`'s table in float32 as one matrix product: rho0 (rhogrid on the valid continuum
    spins, cut at 1e-20; float64, returned) times `Mp` (Jt*2, L*NJ*2), the spin-l' mask with the
    residual parity folded in (`gpu_full_cascade._spin_parity_mask32`): (n, Rt*L, NJ*2), unit
    column scales (float64, the kernels' interface) and rhog. Float32 holds the table's range
    (rho0 <= ~1e15, >= 1e-20), so no scaling is needed."""
    n, Rt, Jt, _ = rhogrid.shape
    dev = rhogrid.device
    rows = torch.arange(Rt, device=dev)
    jj = torch.arange(Jt, device=dev)
    valid = ((2 * jj[None, None, :] + base <= 2 * maxj[:, :, None])
             & (jj[None, None, :] <= maxj[:, :, None])
             & (rows[None, :] > nlast[:, None])[:, :, None])
    rhog = torch.where(valid[..., None] & (rhogrid >= 1.0e-20), rhogrid, 0.0)
    L = Mp.shape[1] // (2 * NJ)
    Q = (rhog.to(F32).reshape(n * Rt, Jt * 2) @ Mp).reshape(n, Rt * L, NJ * 2)
    return Q, torch.ones((n, NJ * 2), dtype=F64, device=dev), rhog


def disc_tables(nl, jdis, parlev, ntop, discfactor, Rt: int, NJ: int, odd: int, ps: int, L: int,
                with_md: bool):
    """`_exit_ctx`'s discrete-level tables of a daughter (n, ND): the `same` mask, discfactor
    above Ntop, parity and spin index, and the l' window (lbeg, lend) (n, NJ, ND) of each
    (mother spin, level), with its bool mask (n, NJ, ND, L) when asked."""
    n, ND = jdis.shape
    dev = jdis.device
    ndd = torch.clamp(nl, max=Rt - 1) + 1
    kk = torch.arange(ND, device=dev)
    jd2 = (2.0 * jdis.to(F32)).to(torch.int64)
    ird = torch.div(jd2, 2, rounding_mode="floor")
    pd = (parlev > 0).to(torch.int64)
    okd = (ird >= 0) & (ird <= NUMJ) & (kk[None, :] < ndd[:, None])
    ir_w = jdis.to(torch.int64)
    pidx_w = torch.where(parlev == -1, 0, 1)
    same = (ir_w == ird) & (pidx_w == pd) & (ir_w >= 0) & (ir_w <= NUMJ) & okd
    dmask = same & ~((kk == 0)[None, :] & (nl == 0)[:, None])
    dfac = torch.where(kk[None, :] > ntop[:, None], discfactor[:, None],
                       torch.ones((n, ND), dtype=F64, device=dev))
    j2 = 2 * torch.arange(NJ, device=dev)[None, :] + odd
    lbeg = torch.div(((j2[:, :, None] - jd2[:, None, :]).abs() - ps).abs(), 2,
                     rounding_mode="floor")
    lend = torch.div(j2[:, :, None] + jd2[:, None, :] + ps, 2, rounding_mode="floor")
    Md = None
    if with_md:
        lpd = torch.arange(L, device=dev)
        Md = (lpd >= lbeg[..., None]) & (lpd <= lend[..., None])
    return dmask, dfac, pd, ird.clamp(0, NUMJ), lbeg, lend, Md


def populate32(Z32, Mp, rhog, fr, sfac: float, n: int, Rt: int, L: int, NJ: int):
    """`populate` from the float32 bin-summed Z (n, Rt*L, NJ*2) (units of the row scale `fr`) as
    one matrix product with the parity-folded spin mask: (n, Rt, Jt, 2) float64."""
    Jt = rhog.shape[2]
    Y = (Z32.reshape(n * Rt, L * NJ * 2) @ Mp.t()).reshape(n, Rt, Jt, 2)
    return sfac * rhog * Y.to(F64) * fr[:, None, None, None]


def z_rows(b, m, qrow, rb_r, T, F, Z, mc: int):
    """Z (nbr, L, NJ*2), over the compact (row, residual row) pairs, += the continuum feeding of
    the live triples (a slice of them)."""
    n, NJ = F.shape[0], F.shape[2]
    L = T.shape[1]
    Fr = F.reshape(n * mc, NJ * 2)[b * mc + m]
    vals = (rb_r[:, None] * T)[:, :, None] * Fr[:, None, :]
    flat = (qrow[:, None] * L + torch.arange(L, device=T.device)[None, :]).reshape(-1)
    Z.reshape(-1, NJ * 2).index_add_(0, flat, vals.reshape(-1, NJ * 2))


def _photon_T(bins, binm, nexm_raw, ex_m, dex_m, sep_t, d_ex, d_dex, d_nlast, tgf, tg_base,
              tg_boff, tg_n0, tg_lc, ic0: int, dmask, dfac, G: int):
    """`exit_arrays` for the photon: (rb, T (n, mc, 2, Rt, G), rho_d); `Chunk.tg_bins` inlined.

    Test: GPUFULL2
    """
    n, mc = bins.shape
    Rt = d_ex.shape[1]
    (inrow, rb, *_rest) = _geometry(bins, binm, nexm_raw, ex_m, dex_m, sep_t, d_ex, d_dex,
                                    d_nlast, 0)
    T = _tg_gather(bins, binm, tgf, tg_base, tg_boff, tg_n0, tg_lc, Rt, G)
    T = torch.where(inrow[:, :, None, :, None], T, 0.0)
    rb = torch.where(inrow, rb, 0.0)
    return rb, T, _rho_discrete(rb, inrow, dmask, dfac)


def _tg_gather(binr, binm, tgf, tg_base, tg_boff, tg_n0, tg_lc, R0: int, G: int):
    """`Chunk.tg_bins` for mother bins `binr` (n, mc) with their row offsets `tg_boff` (n, mc)."""
    dev = binr.device
    lc = tg_lc[:, None]
    stride = 2 * torch.clamp(lc - 1, min=1)
    r = torch.arange(R0, device=dev)
    c = torch.arange(2, device=dev)
    lq = torch.arange(1, G, device=dev)
    start = tg_base[:, None] + tg_boff * stride
    idx = (start[:, :, None, None, None] + r[None, None, None, :, None] * stride[:, :, None, None,
           None] + c[None, None, :, None, None] * (lc - 1)[:, :, None, None, None]
           + (lq - 1)[None, None, None, None, :])
    ok = ((r[None, None, None, :, None] < torch.minimum(binr, tg_n0[:, None])[:, :, None, None,
           None]) & (lq[None, None, None, None, :] < lc[:, :, None, None, None])
          & binm[:, :, None, None, None])
    vals = torch.where(ok, tgf[torch.where(ok, idx, 0)], 0.0)
    return torch.nn.functional.pad(vals, (1, 0))


def _discrete_widths(T0, T1, Md, rho_d, pd):
    Md = Md.to(T0.dtype)
    rd = rho_d[..., None]
    pdl = pd[:, None, :, None]
    r_par = rd * (pdl == 1)
    r_npar = rd * (pdl == 0)
    dd0 = torch.einsum("bjkl,bmkl->bmj", Md, T0 * r_npar + T1 * r_par)
    dd1 = torch.einsum("bjkl,bmkl->bmj", Md, T0 * r_par + T1 * r_npar)
    return torch.stack([dd0, dd1], -1)


def particle_widths(bins, binm, nexm_raw, ex_m, dex_m, sep_t, d_ex, d_dex, d_nlast, egrid_r,
                    egrid32_r, ib, ie, maxen, lmax_r, TL_r, head0, eps, fn, lmaxinc, dmask, dfac,
                    Qm, Md, pd, sfac: float, ty: int, is_k0: bool, NJ: int):
    """`widths_of(exit_arrays(...))` for a particle exit: D (n, mc, NJ, 2).

    TALYS: compound.f90:1 (compound)
    Test: GPUFULL2
    """
    rb, T, rho_d = _particle_T(bins, binm, nexm_raw, ex_m, dex_m, sep_t, d_ex, d_dex, d_nlast,
                               egrid_r, egrid32_r, ib, ie, maxen, lmax_r, TL_r, head0, eps, fn,
                               lmaxinc, dmask, dfac, ty, is_k0)
    n, mc, Rt, L = T.shape
    ND = dmask.shape[1]
    W = (rb[..., None] * T).reshape(n, mc, Rt * L)
    D = torch.bmm(W, Qm).reshape(n, mc, NJ, 2)
    T0 = T[:, :, :ND] * (torch.arange(L, device=T.device) % 2 == 0)
    T1 = T[:, :, :ND] - T0
    return sfac * (D + _discrete_widths(T0, T1, Md, rho_d, pd))


def photon_widths(bins, binm, nexm_raw, ex_m, dex_m, sep_t, d_ex, d_dex, d_nlast, tgf, tg_base,
                  tg_boff, tg_n0, tg_lc, dmask, dfac, Qm, Md, pd, G: int, NJ: int):
    """`widths_of(exit_arrays(...))` for the photon: (D (n, mc, NJ, 2), rb, rho_d).

    TALYS: compound.f90:1 (compound)
    Test: GPUFULL2
    """
    rb, T, rho_d = _photon_T(bins, binm, nexm_raw, ex_m, dex_m, sep_t, d_ex, d_dex, d_nlast, tgf,
                             tg_base, tg_boff, tg_n0, tg_lc, 0, dmask, dfac, G)
    n, mc = bins.shape
    Rt = d_ex.shape[1]
    ND = dmask.shape[1]
    W0 = (rb[..., None] * T[:, :, 0]).reshape(n, mc, Rt * G)
    W1 = (rb[..., None] * T[:, :, 1]).reshape(n, mc, Rt * G)
    D = (torch.bmm(W0, Qm).reshape(n, mc, NJ, 2) + torch.bmm(W1, Qm).reshape(n, mc, NJ, 2)
         .flip(3))
    T0, T1 = T[:, :, 0, :ND], T[:, :, 1, :ND]
    return D + _discrete_widths(T0, T1, Md, rho_d, pd), rb, rho_d


def photon_widths32(bins, binm, nexm_raw, ex_m, dex_m, sep_t, d_ex, d_dex, d_nlast, tgf,
                    tg_base, tg_boff, tg_n0, tg_lc, dmask, dfac, Qs, qs, Md, pd, G: int, NJ: int):
    """`photon_widths` with the matrix products in float32 (GPU3): `Qs` is the dense Q table
    (float32, each (J, parity) column divided by its largest value `qs` (n, NJ*2)).

    TALYS: compound.f90:1 (compound)
    Test: GPU3
    """
    rb, T, rho_d = _photon_T(bins, binm, nexm_raw, ex_m, dex_m, sep_t, d_ex, d_dex, d_nlast, tgf,
                             tg_base, tg_boff, tg_n0, tg_lc, 0, dmask, dfac, G)
    n, mc = bins.shape
    Rt = d_ex.shape[1]
    ND = dmask.shape[1]
    W0 = (rb[..., None] * T[:, :, 0]).reshape(n, mc, Rt * G).to(F32)
    W1 = (rb[..., None] * T[:, :, 1]).reshape(n, mc, Rt * G).to(F32)
    sc = qs[:, None, :]
    D = ((torch.bmm(W0, Qs).to(F64) * sc).reshape(n, mc, NJ, 2)
         + (torch.bmm(W1, Qs).to(F64) * sc).reshape(n, mc, NJ, 2).flip(3))
    T0, T1 = T[:, :, 0, :ND].to(F32), T[:, :, 1, :ND].to(F32)
    Mf = Md.to(F32)
    S0 = torch.einsum("bjkl,bmkl->bmjk", Mf, T0).to(F64)  # (n, mc, NJ, ND)
    S1 = torch.einsum("bjkl,bmkl->bmjk", Mf, T1).to(F64)
    rd = rho_d[:, :, None, :]
    pdl = pd[:, None, None, :]
    r_par = rd * (pdl == 1)
    r_npar = rd * (pdl == 0)
    dd0 = (S0 * r_npar + S1 * r_par).sum(3)
    dd1 = (S0 * r_par + S1 * r_npar).sum(3)
    return D + torch.stack([dd0, dd1], -1), rb, rho_d


def _discrete32(T0, T1, Md, rho_d, pd):
    """`_discrete_widths` with the l' sums in float32: (n, mc, NJ, 2)."""
    Mf = Md.to(F32)
    S0 = torch.einsum("bjkl,bmkl->bmjk", Mf, T0.to(F32)).to(F64)  # (n, mc, NJ, ND)
    S1 = torch.einsum("bjkl,bmkl->bmjk", Mf, T1.to(F32)).to(F64)
    rd = rho_d[:, :, None, :]
    pdl = pd[:, None, None, :]
    r_par = rd * (pdl == 1)
    r_npar = rd * (pdl == 0)
    return torch.stack([(S0 * r_npar + S1 * r_par).sum(3), (S0 * r_par + S1 * r_npar).sum(3)],
                       -1)


def particle_widths32(bins, binm, nexm_raw, ex_m, dex_m, sep_t, d_ex, d_dex, d_nlast, egrid_r,
                      egrid32_r, ib, ie, maxen, lmax_r, TL_r, head0, eps, fn, lmaxinc, dmask,
                      dfac, Qs, qs, Md, pd, sfac: float, ty: int, is_k0: bool, NJ: int):
    """`particle_widths` with the (bin, residual row x l') x (J, parity) product as a float32
    bmm (GPU3): `Qs` (n, Rt*L, NJ*2) is the Q table with each column divided by `qs`.

    TALYS: compound.f90:1 (compound)
    Test: GPU3
    """
    rb, T, rho_d = _particle_T(bins, binm, nexm_raw, ex_m, dex_m, sep_t, d_ex, d_dex, d_nlast,
                               egrid_r, egrid32_r, ib, ie, maxen, lmax_r, TL_r, head0, eps, fn,
                               lmaxinc, dmask, dfac, ty, is_k0)
    n, mc, Rt, L = T.shape
    ND = dmask.shape[1]
    W = (rb[..., None] * T).reshape(n, mc, Rt * L).to(F32)
    D = (torch.bmm(W, Qs).to(F64) * qs[:, None, :]).reshape(n, mc, NJ, 2)
    T0 = T[:, :, :ND] * (torch.arange(L, device=T.device) % 2 == 0)
    T1 = T[:, :, :ND] - T0
    return sfac * (D + _discrete32(T0, T1, Md, rho_d, pd))


def particle_W32(bins, binm, nexm_raw, ex_m, dex_m, sep_t, d_ex, d_dex, d_nlast, egrid_r,
                 egrid32_r, ib, ie, maxen, lmax_r, TL_r, head0, eps, fn, lmaxinc, dmask, dfac,
                 ty: int, is_k0: bool):
    """`_particle_T` as the float32 products' inputs: W = Rboundary T (n, mc, Rt*L), the
    discrete rows' even and odd l' transmissions (n, mc, ND, L) and rho_d (float64)."""
    rb, T, rho_d = _particle_T(bins, binm, nexm_raw, ex_m, dex_m, sep_t, d_ex, d_dex, d_nlast,
                               egrid_r, egrid32_r, ib, ie, maxen, lmax_r, TL_r, head0, eps, fn,
                               lmaxinc, dmask, dfac, ty, is_k0)
    n, mc, Rt, L = T.shape
    ND = dmask.shape[1]
    W = (rb[..., None] * T).reshape(n, mc, Rt * L).to(F32)
    T0 = T[:, :, :ND] * (torch.arange(L, device=T.device) % 2 == 0)
    T1 = T[:, :, :ND] - T0
    return W, T0.to(F32), T1.to(F32), rho_d


def particle_feed32(bins, binm, nexm_raw, ex_m, dex_m, sep_t, d_ex, d_dex, d_nlast, egrid_r,
                    egrid32_r, ib, ie, maxen, lmax_r, TL_r, head0, eps, fn, lmaxinc, dmask, dfac,
                    Qs, qs, Md, pd, F, fr, sfac: float, ty: int, is_k0: bool, NJ: int):
    """`particle_feed` with the products as float32 bmms (GPU3): Z in units of the row scale
    `fr` (float32, summed over the bins), and the row sums mcont (float64, the feeding times the
    column scales divided by its largest value per bin before the product).

    TALYS: compound.f90:1 (compound), multiple.f90:1 (multiple)
    Test: GPU3
    """
    W, T0, T1, rho_d = particle_W32_c(bins, binm, nexm_raw, ex_m, dex_m, sep_t, d_ex, d_dex,
                                      d_nlast, egrid_r, egrid32_r, ib, ie, maxen, lmax_r, TL_r,
                                      head0, eps, fn, lmaxinc, dmask, dfac, ty, is_k0)
    n, mc, ND, L = T0.shape
    Rt = W.shape[2] // L
    Fm = F.reshape(n, mc, NJ * 2)
    Zs = torch.bmm(W.transpose(1, 2), (Fm / fr[:, None, None]).to(F32))
    G = Fm * qs[:, None, :]
    gs = G.amax(2)
    gs = torch.where(gs > 0.0, gs, 1.0)
    H = torch.bmm((G / gs[..., None]).to(F32), Qs.transpose(1, 2))  # (n, mc, Rt*L)
    mcont = (H * W).reshape(n, mc, Rt, L).sum(3).to(F64) * (gs * sfac)[..., None]
    Mf = Md.to(F32)
    tot0 = torch.einsum("bjkl,bmkl->bmjk", Mf, T0).to(F64)
    tot1 = torch.einsum("bjkl,bmkl->bmjk", Mf, T1).to(F64)
    A = torch.einsum("bmjp,bmjk->bmpk", F, tot0)
    Bq = torch.einsum("bmjp,bmjk->bmpk", F, tot1)
    fd = (A.gather(2, pd[:, None, None, :].expand(n, mc, 1, ND))[:, :, 0]
          + Bq.gather(2, (1 - pd)[:, None, None, :].expand(n, mc, 1, ND))[:, :, 0])
    fd = sfac * rho_d * fd
    head = mcont[:, :, :ND] + fd
    mcont = torch.cat([head, mcont[:, :, ND:]], 2)
    return Zs, mcont, fd


def particle_feed(bins, binm, nexm_raw, ex_m, dex_m, sep_t, d_ex, d_dex, d_nlast, egrid_r,
                  egrid32_r, ib, ie, maxen, lmax_r, TL_r, head0, eps, fn, lmaxinc, dmask, dfac,
                  Qm, Md, pd, F, sfac: float, ty: int, is_k0: bool, NJ: int):
    """`feed_of(exit_arrays(...), F)` and `_decay_chunk`'s row sums: (Z (n, Rt*L, NJ*2), mcont
    (n, mc, Rt) with the discrete cells added, fd (n, mc, ND)).

    TALYS: compound.f90:1 (compound), multiple.f90:1 (multiple)
    Test: GPUFULL2
    """
    rb, T, rho_d = _particle_T(bins, binm, nexm_raw, ex_m, dex_m, sep_t, d_ex, d_dex, d_nlast,
                               egrid_r, egrid32_r, ib, ie, maxen, lmax_r, TL_r, head0, eps, fn,
                               lmaxinc, dmask, dfac, ty, is_k0)
    n, mc, Rt, L = T.shape
    ND = dmask.shape[1]
    W = (rb[..., None] * T).reshape(n, mc, Rt * L)
    Fm = F.reshape(n, mc, NJ * 2)
    Z = torch.bmm(W.transpose(1, 2), Fm)
    H = torch.bmm(Fm, Qm.transpose(1, 2))
    mcont = (H * W).reshape(n, mc, Rt, L).sum(3) * sfac
    T0 = T[:, :, :ND] * (torch.arange(L, device=F.device) % 2 == 0)
    T1 = T[:, :, :ND] - T0
    tot0 = torch.einsum("bjkl,bmkl->bmjk", Md, T0)
    tot1 = torch.einsum("bjkl,bmkl->bmjk", Md, T1)
    A = torch.einsum("bmjp,bmjk->bmpk", F, tot0)
    Bq = torch.einsum("bmjp,bmjk->bmpk", F, tot1)
    fd = (A.gather(2, pd[:, None, None, :].expand(n, mc, 1, ND))[:, :, 0]
          + Bq.gather(2, (1 - pd)[:, None, None, :].expand(n, mc, 1, ND))[:, :, 0])
    fd = sfac * rho_d * fd
    head = mcont[:, :, :ND] + fd
    mcont = torch.cat([head, mcont[:, :, ND:]], 2)
    return Z, mcont, fd


# ----------------------------------------------------------------------------------- the walk


def gamma_step(xsjp: Tensor, gc: Tensor, brk: Tensor, brr: Tensor, br_rec: Tensor, rec0: Tensor):
    """The gamma cascade of one mother bin (`_decay_chunk`): the intensities (n, NB) to add at
    the branch levels, masked, and those recorded in `feedexcl` (the later of duplicates)."""
    ok = gc[:, None] & (brk >= 0)
    intens = torch.where(ok, xsjp[:, None] * brr, 0.0)
    return intens, torch.where(rec0[:, None] & br_rec, intens, 0.0)


def decay_step(nex: Tensor, pop: Tensor, xe_nex: Tensor, summpe_nex: Tensor, rmask: Tensor,
               dunder: Tensor,
               popepsA: Tensor, rowidx_nex: Tensor, maxj_nex: Tensor, dsum6: Tensor,
               zero6: Tensor, D6: Tensor, rb0: Tensor, rhog0: Tensor, rhod0: Tensor, pd0: Tensor,
               ird0: Tensor, M0: Tensor, Md0: Tensor, bins: Tensor, binm: Tensor, tgf: Tensor,
               tg_base: Tensor, tg_boff: Tensor, tg_n0: Tensor, tg_lc: Tensor, nlg: Tensor,
               rowsR: Tensor, Fst: Tensor, deadst: Tensor, decayed: Tensor, G: int):
    """`_decay_chunk`'s walk at mother bin `nex` (a 0-d device tensor) after the gamma cascade: the decay flag of each
    row, the photon exit into the row's lower bins `dp0` (n, R0, J0, 2) and its row sums `mc0`,
    the trapped population's share per level into the levels' populations (n, R, rows below the
    mother bin) and into `xspopex`/`feedexcl` (n, R), and the bin's stored feeding, dead cells and
    decayed flag after this bin.

    `summpe_nex` is multipreeq2's `summpe` of each row at this bin (zero without a record), so
    `Dmulti = summpe / xspopex` (multipreeq2.f90:374) takes the multiple pre-equilibrium share out
    of the compound feeding (compound.f90:402); with no record the factor is exactly 1.0.

    TALYS: multiple.f90:1 (multiple), compound.f90:1 (compound)
    Test: GPUFULL2
    """
    dev = pop.device
    n, NJ = pop.shape[0], pop.shape[1]
    R0, J0 = rhog0.shape[1], rhog0.shape[2]
    ND0 = rhod0.shape[2]
    ar = torch.arange(n, device=dev)
    jjn = torch.arange(NJ, device=dev)
    dec = rmask & ~dunder & (xe_nex >= popepsA) & (rowidx_nex >= 0)
    i = rowidx_nex.clamp(min=0)
    jm = jjn[None, :] <= maxj_nex[:, None]
    popeps_b = popepsA / (5 * torch.clamp(maxj_nex, min=1)).to(F64) * 0.5
    active = jm[..., None] & (pop >= popeps_b[:, None, None]) & dec[:, None, None]
    dead = active & zero6[ar, i]
    denom = dsum6[ar, i] + torch.where(dead, 0.0, D6[ar, i])
    live = active & (pop != 0.0) & (denom != 0.0)
    has_mpe = summpe_nex != 0.0
    dmulti = torch.where(has_mpe, summpe_nex / torch.where(has_mpe, xe_nex, 1.0), 0.0)
    f = torch.where(live, (1.0 - dmulti)[:, None, None] * pop / torch.where(live, denom, 1.0), 0.0)
    trapped = active & (pop != 0.0) & (denom == 0.0)
    rb = rb0[ar, i]
    rho_c = rb[:, :, None, None] * rhog0
    rho_c = torch.where(rho_c >= 1.0e-20, rho_c, 0.0)
    tg = _tg_gather(bins.gather(1, i[:, None]), binm.gather(1, i[:, None]), tgf, tg_base,
                    tg_boff.gather(1, i[:, None]), tg_n0, tg_lc, R0, G)[:, 0]
    # the einsums as explicit fused reductions: their inner dimensions (G <= 3 multipolarities,
    # 2 parities) make FP64 bmm the slowest kernel the card has
    V0 = (f[:, :, None, :, None] * M0[None, :, :, None, :]).sum(1)  # (n, J0, 2, G)
    V1 = V0.flip(2)
    TV = ((tg[:, 0, :, None, None, :] * V0[:, None]).sum(-1)
          + (tg[:, 1, :, None, None, :] * V1[:, None]).sum(-1))  # (n, R0, J0, 2)
    dp0 = rho_c * TV
    tot0 = (Md0 * tg[:, 0, None, :ND0]).sum(-1)  # (n, NJ, ND0)
    tot1 = (Md0 * tg[:, 1, None, :ND0]).sum(-1)
    A0 = (f[:, None, :, :] * tot0.transpose(1, 2)[:, :, :, None]).sum(2).transpose(1, 2)
    A1 = (f[:, None, :, :] * tot1.transpose(1, 2)[:, :, :, None]).sum(2).transpose(1, 2)
    fd = A0.gather(1, pd0[:, None, :])[:, 0] + A1.gather(1, (1 - pd0)[:, None, :])[:, 0]
    kk0 = torch.arange(ND0, device=dev)[None, :].expand(n, ND0)
    flat = (((ar[:, None] * R0 + kk0) * J0 + ird0.clamp(max=J0 - 1)) * 2 + pd0).reshape(-1)
    dp0 = dp0.reshape(-1).index_add(0, flat, (rhod0[ar, i] * fd).reshape(-1)).reshape(dp0.shape)
    rows0 = torch.arange(R0, device=dev)
    dp0 = torch.where(((rows0 < nex)[None, :, None, None] & dec[:, None, None, None]), dp0, 0.0)
    mc0 = dp0.sum((2, 3))
    tr = trapped.flatten(1).any(1)
    share = torch.where(trapped, pop, 0.0).sum((1, 2)) / (nlg + 1.0)
    R = rowsR.shape[0]
    rr = torch.arange(R, device=dev)
    lev = (rr[None, :] <= torch.minimum(nlg, nex - 1)[:, None]) & tr[:, None]
    share_v = torch.where(lev, share[:, None], 0.0)
    # compound.f90:404-419 / `multiple._apply_leftover`: the levels' xspopex and feedexcl get the
    # share on every level 0..Nlast, not only the rows below the mother bin
    share_e = torch.where((rr[None, :] <= nlg[:, None]) & tr[:, None], share[:, None], 0.0)
    newF = torch.where(dec[:, None, None], f, Fst[ar, i])
    newdead = torch.where(dec[:, None, None], dead, deadst[ar, i])
    newdec = decayed[ar, i] | dec
    return dec, i, dp0, mc0, mc0.sum(1), share_v, share_e, newF, newdead, newdec


def decay_step32(nex: Tensor, pop: Tensor, xe_nex: Tensor, summpe_nex: Tensor, rmask: Tensor,
                 dunder: Tensor, popepsA: Tensor, rowidx_nex: Tensor, maxj_nex: Tensor,
                 dsum6: Tensor, zero6: Tensor, D6: Tensor, rb0: Tensor, rhog0_32: Tensor,
                 rhod0: Tensor, pd0: Tensor, ird0: Tensor, M0_32: Tensor, Md0: Tensor,
                 bins: Tensor, binm: Tensor, tgf: Tensor, tg_base: Tensor, tg_boff: Tensor,
                 tg_n0: Tensor, tg_lc: Tensor, nlg: Tensor, rowsR: Tensor, Fst: Tensor,
                 deadst: Tensor, decayed: Tensor, G: int):
    """`decay_step` with the photon exit's contractions in float32 (GPU3): the compound feeding
    `f` is divided by its largest value per row, contracted with the photon transmissions and
    rho0 (`rhog0_32`, `M0_32` float32) in float32, and scaled back to float64 for the
    populations it is added to. Same returns as `decay_step`.

    TALYS: multiple.f90:1 (multiple), compound.f90:1 (compound)
    Test: GPU3
    """
    dev = pop.device
    n, NJ = pop.shape[0], pop.shape[1]
    R0, J0 = rhog0_32.shape[1], rhog0_32.shape[2]
    ND0 = rhod0.shape[2]
    ar = torch.arange(n, device=dev)
    jjn = torch.arange(NJ, device=dev)
    dec = rmask & ~dunder & (xe_nex >= popepsA) & (rowidx_nex >= 0)
    i = rowidx_nex.clamp(min=0)
    jm = jjn[None, :] <= maxj_nex[:, None]
    popeps_b = popepsA / (5 * torch.clamp(maxj_nex, min=1)).to(F64) * 0.5
    active = jm[..., None] & (pop >= popeps_b[:, None, None]) & dec[:, None, None]
    dead = active & zero6[ar, i]
    denom = dsum6[ar, i] + torch.where(dead, 0.0, D6[ar, i])
    live = active & (pop != 0.0) & (denom != 0.0)
    has_mpe = summpe_nex != 0.0
    dmulti = torch.where(has_mpe, summpe_nex / torch.where(has_mpe, xe_nex, 1.0), 0.0)
    f = torch.where(live, (1.0 - dmulti)[:, None, None] * pop / torch.where(live, denom, 1.0), 0.0)
    trapped = active & (pop != 0.0) & (denom == 0.0)
    fs = f.amax((1, 2))
    fs = torch.where(fs > 0.0, fs, 1.0)
    f32 = (f / fs[:, None, None]).to(F32)
    rb32 = rb0[ar, i].to(F32)
    rho_c = rb32[:, :, None, None] * rhog0_32
    rho_c = torch.where(rho_c >= 1.0e-20, rho_c, 0.0)
    tg = _tg_gather(bins.gather(1, i[:, None]), binm.gather(1, i[:, None]), tgf, tg_base,
                    tg_boff.gather(1, i[:, None]), tg_n0, tg_lc, R0, G)[:, 0].to(F32)
    # (n, NJ*2) x (NJ, J0, G) -> V (n, J0, 2, G) and the photon exit TV as two float32 bmms:
    # TV[r, J, p] = sum_g tg[0, r, g] V[J, p, g] + tg[1, r, g] V[J, 1 - p, g]
    V0 = torch.einsum("bjp,jkg->bkpg", f32, M0_32)  # (n, J0, 2, G)
    Vc = torch.cat([V0.permute(0, 3, 1, 2), V0.flip(2).permute(0, 3, 1, 2)], 1)  # (n, 2G, J0, 2)
    TV = torch.bmm(tg.permute(0, 2, 1, 3).reshape(n, R0, -1),
                   Vc.reshape(n, Vc.shape[1], J0 * 2)).reshape(n, R0, J0, 2)
    rows0 = torch.arange(R0, device=dev)
    on = (rows0 < nex)[None, :, None, None] & dec[:, None, None, None]
    dp32 = torch.where(on, rho_c * TV, 0.0)
    dp0 = dp32.to(F64) * fs[:, None, None, None]
    mc0 = dp32.sum((2, 3)).to(F64) * fs[:, None]
    tot0 = (Md0 * tg[:, 0, None, :ND0]).sum(-1)  # (n, NJ, ND0)
    tot1 = (Md0 * tg[:, 1, None, :ND0]).sum(-1)
    A0 = (f32[:, None, :, :] * tot0.transpose(1, 2)[:, :, :, None]).sum(2).transpose(1, 2)
    A1 = (f32[:, None, :, :] * tot1.transpose(1, 2)[:, :, :, None]).sum(2).transpose(1, 2)
    fd = (A0.gather(1, pd0[:, None, :])[:, 0] + A1.gather(1, (1 - pd0)[:, None, :])[:, 0]).to(F64)
    kk0 = torch.arange(ND0, device=dev)[None, :].expand(n, ND0)
    vd = torch.where((kk0 < nex) & dec[:, None], rhod0[ar, i] * fd * fs[:, None], 0.0)
    flat = (((ar[:, None] * R0 + kk0) * J0 + ird0.clamp(max=J0 - 1)) * 2 + pd0).reshape(-1)
    dp0 = dp0.reshape(-1).index_add(0, flat, vd.reshape(-1)).reshape(dp0.shape)
    mc0 = mc0.scatter_add(1, kk0, vd)
    tr = trapped.flatten(1).any(1)
    share = torch.where(trapped, pop, 0.0).sum((1, 2)) / (nlg + 1.0)
    R = rowsR.shape[0]
    rr = torch.arange(R, device=dev)
    lev = (rr[None, :] <= torch.minimum(nlg, nex - 1)[:, None]) & tr[:, None]
    share_v = torch.where(lev, share[:, None], 0.0)
    share_e = torch.where((rr[None, :] <= nlg[:, None]) & tr[:, None], share[:, None], 0.0)
    newF = torch.where(dec[:, None, None], f, Fst[ar, i])
    newdead = torch.where(dec[:, None, None], dead, deadst[ar, i])
    newdec = decayed[ar, i] | dec
    return dec, i, dp0, mc0, mc0.sum(1), share_v, share_e, newF, newdead, newdec


decay_step32_c = _compiled(decay_step32)
particle_widths_c = _compiled(particle_widths)
photon_widths_c = _compiled(photon_widths)
particle_feed_c = _compiled(particle_feed)
decay_step_c = _compiled(decay_step)
particle_nodes_c = _compiled(particle_nodes)
particle_rows_c = _compiled(particle_rows)
widths_rows_c = _compiled(widths_rows)
feed_rows_c = _compiled(feed_rows)
gamma_step_c = _compiled(gamma_step)
widths_rows32_c = _compiled(widths_rows32)
feed_rows32_c = _compiled(feed_rows32)
photon_widths32_c = _compiled(photon_widths32)
particle_widths32_c = _compiled(particle_widths32)
particle_W32_c = _compiled(particle_W32)
widths_dense32_c = _compiled(widths_dense32)
q_table32_c = _compiled(q_table32)
disc_tables_c = _compiled(disc_tables)
populate32_c = _compiled(populate32)
feed_dense32_c = _compiled(feed_dense32)
particle_feed32_c = particle_feed32  # eager around the compiled W (Inductor cannot split its ranges)

