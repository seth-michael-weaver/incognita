"""comptarget.f90 on the (nuclide, energy) batch axis over per-type channel lists, with the spin
coupling taken as window sums (GPU3).

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

Task: GPU3 (gate G-GPU3, docs/results/hf-gpu3.md). No physics of its own: `gpu_full.comptarget`
(`target_batch.case_moldauer` / `case_nowfc` with a run axis) with the same numbers, arranged so
that nothing of shape (runs, cells, residual spins, l', j') or (runs, cells, nodes, channels) is
formed.

**Channels.** An exit channel of type t is a (parity class c, residual row n, l', j') cell with
T > 0 inside lmaxhf and allowed by the ejectile's spin (`_mask_for`'s `ok_s`); c is l' mod 2 for
particles and the radiation class for the photon, and the residual parity is the cell's parity
xor c. Channels are packed per run (`_channel_list`); padding carries T = 0 and weight 0.

**Spin windows.** `_mask_for` allows compound spin j2, residual spin irs2 and channel spin jj
(jj = 2l' + (j' - 1) spin2) iff |j2 - irs2| <= jj <= j2 + irs2 (the parity condition follows
from `ok_s`). For fixed (j2, jj) the allowed residual spins are a contiguous range, and for
fixed (irs2, jj) the allowed cells of one parity block are a contiguous range. So every
contraction with the mask is a window sum:

* a channel's weight in a cell, sum over residual spins of rho0 (`Rw`), and the denominators
  D = sum_channels T * weight;
* the population a residual (row, spin, parity) receives, sum over cells of the cell's feeding
  of the channel (`TV`).

A window sum is a difference of prefix sums, and of the two differences (prefix below, suffix
above) the one that subtracts the smaller part is taken, so the cancellation is at most
eps * min(below, above) / window. Discrete levels use the level's own 2J in place of irs2.

**Moldauer.** The integrand's product over channels and the feeding's sum over nodes are
reductions over the channel axis or the node axis; they are formed without the
(runs, cells, nodes, channels) intermediate, so groups of runs are sized by channels and cells.

Test: GPU3 / tests/hf/test_gpu_full.py
"""

from __future__ import annotations

import os
import time

import numpy as np
import torch
from torch import Tensor

from physics.hf import gpu_full as _G
from physics.hf.gpu_full import (
    F64,
    PARSPIN2,
    SPIN2,
    Batch,
    _chunks,
    _degrees_of_freedom,
    stage,
)
from physics.hf.gpu_full_kernels import _compiled

CT_BUDGET = float(os.environ.get("GPU3_CT_BUDGET", "6.0e7"))


def _spin_tables(ty: int, L: int, dev) -> tuple[Tensor, Tensor]:
    """jj (L, 3) and `_mask_for`'s ok_s (L, 3) of exit type `ty` (photon: jj = 2l', l' >= 1,
    only the middle j' column)."""
    lp = torch.arange(L, device=dev)
    if ty == 0:
        jj = (2 * lp)[:, None].expand(L, 3).contiguous()
        ok = torch.zeros((L, 3), dtype=torch.bool, device=dev)
        ok[:, 1] = lp >= 1
        return jj, ok
    s, ps = SPIN2[ty], PARSPIN2[ty]
    ud = torch.tensor([-1, 0, 1], device=dev)
    jj = 2 * lp[:, None] + ud[None, :] * s
    dj = jj - 2 * lp[:, None]
    ok = ((dj.abs() <= ps) & ((dj - ps) % 2 == 0) & (jj >= 0)
          & (2 * lp[:, None] >= (jj - ps).abs()))
    return jj.clamp(min=0), ok


def _spin_tables_anom(ty: int, L: int, dev) -> tuple[Tensor, Tensor]:
    """GPUC: `_spin_tables` for a discrete level of impossible 2J parity (OPEN3M's A2,
    `prepare.anomalous_exit_mask`): l2' = 2 l' + 1, jj = l2' + (j' - 1) spin2."""
    lp = torch.arange(L, device=dev)
    l2 = 2 * lp + 1
    if ty == 0:
        jj = l2[:, None].expand(L, 3).contiguous()
        ok = torch.zeros((L, 3), dtype=torch.bool, device=dev)
        ok[:, 1] = l2 >= 2
        return jj, ok
    s, ps = SPIN2[ty], PARSPIN2[ty]
    dj = torch.tensor([-1, 0, 1], device=dev)[None, :] * s
    jj = l2[:, None] + dj
    ok = ((dj.abs() <= ps) & ((dj - ps) % 2 == 0) & (jj >= 0)
          & (l2[:, None] >= (jj - ps).abs()))
    return jj.clamp(min=0), ok


def _cum(v: Tensor, dim: int) -> tuple[Tensor, Tensor]:
    """Prefix P[x] = sum_{x' < x} v and suffix S[x] = sum_{x' >= x} v along `dim`, length X + 1."""
    pad = [0, 0] * (v.dim() - 1 - (dim % v.dim()))
    P = torch.nn.functional.pad(torch.cumsum(v, dim), pad + [1, 0])
    S = torch.nn.functional.pad(torch.cumsum(v.flip(dim), dim).flip(dim), pad + [0, 1])
    return P, S


def _window(Pa: Tensor, Pb: Tensor, Sa: Tensor, Sb: Tensor, empty: Tensor) -> Tensor:
    """sum over [a, b] from P[a], P[b + 1], S[a], S[b + 1]: the difference subtracting less."""
    v = torch.where(Pa <= Sb, Pb - Pa, Sa - Sb)
    return torch.where(empty, 0.0, torch.clamp(v, min=0.0))


def _gather_window(P: Tensor, S: Tensor, lin: Tensor, lo: Tensor, hi: Tensor, X: int,
                   stride: int) -> Tensor:
    """Window [lo, hi] (clamped to [0, X - 1]) of the prefix/suffix tables P, S (flat, last axis
    of length X + 1 at `stride` = X + 1), at the leading flat offsets `lin`."""
    a = lo.clamp(0, X)
    b1 = (hi + 1).clamp(0, X)
    empty = (lo > hi) | (lo >= X) | (hi < 0)
    Pf, Sf = P.reshape(-1), S.reshape(-1)
    base = lin * stride
    return _window(Pf[base + a], Pf[base + b1], Sf[base + a], Sf[base + b1], empty | (b1 <= a))


def _channel_list(Tn: Tensor, okS: Tensor, R: int, L: int) -> dict:
    """The channels (T > 0, allowed j') of `Tn` (Bc, 2, R, L, 3), packed per run: (Bc, nch)
    tables of T, parity class c, row n, l', j' and the valid mask."""
    Bc = Tn.shape[0]
    dev = Tn.device
    m = (Tn > 0.0) & okS[None, None, None]
    F = 2 * R * L * 3
    m = m.reshape(Bc, F)
    cnt = m.sum(1)
    nch = max(int(cnt.max()) if Bc else 0, 1)
    pos = torch.where(m, torch.cumsum(m, 1) - 1, nch)
    fidx = torch.zeros((Bc, nch + 1), dtype=torch.int64, device=dev)
    fidx.scatter_(1, pos, torch.arange(F, device=dev).expand(Bc, F))
    fidx = fidx[:, :nch]
    ok = torch.arange(nch, device=dev)[None, :] < cnt[:, None]
    T = torch.where(ok, Tn.reshape(Bc, F).gather(1, fidx), 0.0)
    u = fidx % 3
    l = (fidx // 3) % L  # noqa: E741
    n = (fidx // (3 * L)) % R
    c = fidx // (3 * L * R)
    return dict(T=T, u=u, l=l, n=n, c=c, ok=ok, nch=nch)


def _prep(bk: Batch, res: dict, ty: int, sel: Tensor) -> dict:
    """`gpu_full._prepare_type` on the channel list: rho0 and its prefix tables over residual
    spin, the discrete levels, the channels and their weights `r` (Bc, K, nch) per cell, D.

    TALYS: compprepare.f90:1 (compprepare)
    Test: GPU3
    """
    t, d = bk.t, bk.dims
    dev = bk.device
    _t0 = time.perf_counter()
    r_ = res[ty]
    photon = ty == 0
    Bc = sel.numel()
    R = d["R"]
    rho = r_["rho"][sel]
    jn = torch.nonzero((rho >= 1.0e-20).flatten(0, 1).any(0).any(1)).flatten()
    J = int(jn[-1]) + 1 if jn.numel() else 1
    rho = rho[:, :, :J].contiguous()
    lmaxhf = r_["lmaxhf"][sel]
    maxj = t["maxj"][sel, ty]
    nl = t["nlast"][sel, ty]
    mx = t["maxex"][sel, ty]
    rows = torch.arange(R, device=dev)
    disc = rows[None, :] <= nl[:, None]
    j2 = t["j2"][sel]
    K = j2.shape[1]
    pidx = t["pidx"][sel]
    base = (j2[:, 0] + PARSPIN2[ty]) % 2
    irs2c = 2 * torch.arange(J, device=dev)[None, :] + base[:, None]  # (Bc, J)
    if photon:
        tg = r_["tg"][sel]  # (Bc, R, G, 2)
        L = tg.shape[2]
        lp = torch.arange(L, device=dev)
        Tn = torch.zeros((Bc, 2, R, L, 3), dtype=F64, device=dev)
        Tn[:, 0, :, :, 1] = tg[:, :, lp, (lp % 2 == 0).to(torch.int64)]
        Tn[:, 1, :, :, 1] = tg[:, :, lp, (lp % 2 == 1).to(torch.int64)]
        raw = None
    else:
        raw = r_["tjl"][sel]
        ln = torch.nonzero((raw != 0.0).any(3).flatten(0, 1).any(0)).flatten()
        Lc = max(int(ln[-1]) + 1 if ln.numel() else 1, 1)
        raw = raw[:, :, :Lc].contiguous()
        L = raw.shape[2]
        lp = torch.arange(L, device=dev)
        Tn = torch.stack([torch.where((lp % 2 == c)[None, None, :, None], raw, 0.0)
                          for c in (0, 1)], dim=1)
    lm = lp[None, None, :] <= lmaxhf[:, :, None]  # (Bc, R, L)
    Tn = torch.where(lm[:, None, :, :, None], Tn, 0.0)
    vc = (irs2c[:, None, :] <= (2 * maxj)[:, :, None]) & ~disc[:, :, None]
    rho_c = torch.where(vc[..., None] & (rho >= 1.0e-20), rho, 0.0)  # (Bc, R, J, 2)
    ND = int(torch.minimum(nl, mx).max()) + 1
    nd = torch.minimum(nl, mx) + 1
    jdis2 = torch.where(rows[None, :] <= nl[:, None],
                        (2.0 * t["jdis"][sel, ty].to(torch.float32)).to(torch.int64), -1)
    jd2 = jdis2[:, :ND]
    ird = torch.div(jd2, 2, rounding_mode="floor")
    pd = (t["parlev"][sel, ty, :ND] > 0).to(torch.int64)
    okd = (ird >= 0) & (ird < J) & (torch.arange(ND, device=dev)[None, :] < nd[:, None])
    irc = ird.clamp(0, J - 1)
    ar = torch.arange(ND, device=dev)
    bi = torch.arange(Bc, device=dev)[:, None]
    rv = rho[bi, ar[None, :], irc, pd]
    rho_d = torch.where(okd & (rv >= 1.0e-20), rv, 0.0)
    _t0 = stage("ct:tables", dev, _t0)
    jjt, okt = _spin_tables(ty, L, dev)
    ch = _channel_list(Tn, okt, R, L)
    _t0 = stage("ct:list", dev, _t0)
    nch = ch["nch"]
    jj = jjt[ch["l"], ch["u"]]  # (Bc, nch)
    # GPUC: OPEN3M's A2 on a channel into a discrete level of impossible 2J parity: its own jj and
    # rule, capped at 2 l' + 1 <= 2 lmaxhf (every live such channel is in the regular list: the
    # extra (l' = 0, j' = 0) of a spin-1/2 ejectile has T = 0)
    jjta, okta = _spin_tables_anom(ty, L, dev)
    an_d = ((j2[:, :1] + jd2 + PARSPIN2[ty]) % 2 == 1) & (jd2 >= 0)  # (Bc, ND)
    an_ch = an_d.gather(1, ch["n"].clamp(max=ND - 1)) & (ch["n"] < ND)
    capa = (2 * ch["l"] + 1) <= 2 * lmaxhf.gather(1, ch["n"])
    jjd = torch.where(an_ch, jjta[ch["l"], ch["u"]], jj)
    okdc = torch.where(an_ch, okta[ch["l"], ch["u"]] & capa & ch["ok"], ch["ok"])
    P, S = _cum(rho_c.permute(0, 1, 3, 2), 3)  # (Bc, R, 2, J + 1)
    r = _weights_c(P, S, rho_d, jd2, pd, nd, j2, pidx, base, ch["n"], ch["c"], jj, ch["ok"],
                   jjd, okdc, R, J, ND)
    D = (r * ch["T"][:, None, :]).sum(2)
    stage("ct:weights", dev, _t0)
    return dict(rho_c=rho_c, rho_d=rho_d, jd2=jd2, pd=pd, ird=irc, ok=okd, nd=nd, ND=ND, J=J,
                L=L, raw=raw, lm=lm, ch=ch, jj=jj, r=r, D=D, pidx=pidx, j2=j2, base=base,
                irs2=irs2c, okt=okt, jjt=jjt, K=K, nch=nch, jjd=jjd, okdc=okdc, jjta=jjta,
                okta=okta, lmaxhf=lmaxhf)


def _weights(P, S, rho_d, jd2, pd, nd, j2, pidx, base, n, c, jj, ok, jjd, okd, R: int, J: int,
             ND: int):
    """A channel's weight in each cell (Bc, K, nch): rho0 over the residual spins its window
    allows at the residual parity (cell parity xor c), plus the discrete level of its row.

    TALYS: molprepare.f90:1 (molprepare), compprepare.f90:1 (compprepare)
    Test: GPU3
    """
    Bc, K = j2.shape
    dev = j2.device
    j2k = j2[:, :, None]
    jjc = jj[:, None, :]
    lo = (j2k - jjc).abs()
    hi = j2k + jjc
    b0 = base[:, None, None]
    ilo = torch.div(lo - b0, 2, rounding_mode="floor")
    ihi = torch.div(hi - b0, 2, rounding_mode="floor")
    par = pidx[:, :, None] ^ c[:, None, :]
    bidx = torch.arange(Bc, device=dev)[:, None, None]
    lin = (bidx * R + n[:, None, :]) * 2 + par
    rc = _gather_window(P, S, lin, ilo, ihi, J, J + 1)
    # discrete levels of the channel's row
    isd = n < ND
    nc = n.clamp(max=ND - 1)
    jdn = jd2.gather(1, nc)[:, None, :]
    pdn = pd.gather(1, nc)[:, None, :]
    lod = (j2k - jdn).abs()
    jjdc = jjd[:, None, :]
    md = ((lod <= jjdc) & (jjdc <= j2k + jdn) & ((jjdc - lod) % 2 == 0)
          & (isd & (n < nd[:, None]))[:, None, :])
    parm = c[:, None, :] == (pidx[:, :, None] != pdn).to(torch.int64)
    rd = torch.where(md & parm, rho_d.gather(1, nc)[:, None, :], 0.0)
    return torch.where(ok[:, None, :], rc, 0.0) + torch.where(okd[:, None, :], rd, 0.0)


def _cell_window(Wp: Tensor, Ws: Tensor, blk: Tensor, irs2: Tensor, jj: Tensor, j2beg: Tensor,
                 nJ: int, lead: Tensor, lead_n: int) -> Tensor:
    """sum over the cells of parity block `blk` whose 2J lies in [|irs2 - jj|, irs2 + jj], from
    the prefix/suffix tables Wp, Ws (lead_n x 2 x (nJ + 1), flat) at leading index `lead`."""
    lo = torch.div((irs2 - jj).abs() - j2beg, 2, rounding_mode="floor")
    hi = torch.div(irs2 + jj - j2beg, 2, rounding_mode="floor")
    lin = lead * 2 + blk
    return _gather_window(Wp, Ws, lin, lo.clamp(min=0), torch.minimum(hi, torch.full_like(
        hi, nJ - 1)), nJ, nJ + 1) * (hi >= 0)


def _cont_window(Wp, Ws, c, irs2, jjc, j2beg, nJ: int, lead, Tfac, ok, q: int):
    blk = (q ^ c)[:, :, None]
    win = _cell_window(Wp, Ws, blk, irs2, jjc, j2beg[:, None, None], nJ, lead, 0)
    if Tfac is not None:
        win = Tfac[:, :, None] * win
    return torch.where(ok[:, :, None], win, 0.0)


def _feed(sub: Tensor, ty: int, p: dict, Y: Tensor, sep: bool, nJ: int) -> None:
    """Add the populations of exit `ty` to sub[:, ty]: Y is the cells' feeding of each channel,
    (Bc, K) when it factorises as w_k * T (`sep`), else (Bc, K, nch) with T in it.

    TALYS: comptarget.f90:1 (comptarget)
    Test: GPU3
    """
    _t0 = time.perf_counter()
    ch = p["ch"]
    Bc = sub.shape[0]
    dev = sub.device
    R = sub.shape[2]
    J, ND, nch = p["J"], p["ND"], p["nch"]
    j2beg = p["j2"][:, 0]
    if sep:
        V = Y.reshape(Bc, 2, nJ)  # (Bc, blocks, cells)
        lead = torch.arange(Bc, device=dev)[:, None, None]
        lead_n = Bc
        Tfac = ch["T"]
    else:
        V = Y.reshape(Bc, 2, nJ, nch).permute(0, 3, 1, 2)  # (Bc, nch, blocks, cells)
        lead = (torch.arange(Bc, device=dev)[:, None] * nch
                + torch.arange(nch, device=dev)[None, :])[:, :, None]
        lead_n = Bc * nch
        Tfac = None
    Wp, Ws = _cum(V.contiguous(), -1)
    irs2 = p["irs2"][:, None, :]  # (Bc, 1, J)
    jjc = p["jj"][:, :, None]  # (Bc, nch, 1)
    idx = (torch.arange(Bc, device=dev)[:, None] * R + ch["n"]).reshape(-1)  # (Bc * nch)
    outs = []
    for q in (0, 1):
        v = _cont_window_c(Wp, Ws, ch["c"], irs2, jjc, j2beg, nJ, lead, Tfac, ch["ok"], q)
        o = torch.zeros((Bc * R, J), dtype=F64, device=dev)
        outs.append(o.index_add_(0, idx, v.reshape(-1, J)).reshape(Bc, R, J))
    contrib = p["rho_c"] * torch.stack(outs, -1)
    _t0 = stage("ct:feed-cont", sub.device, _t0)
    # discrete levels: the level's 2J in place of irs2
    isd = (ch["n"] < ND) & p["okdc"]
    nc = ch["n"].clamp(max=ND - 1)
    jdn = p["jd2"].gather(1, nc)
    pdn = p["pd"].gather(1, nc)
    blk = pdn ^ ch["c"]
    win = _cell_window(Wp, Ws, blk, jdn, p["jjd"], j2beg[:, None], nJ, lead[:, :, 0], lead_n)
    parity_ok = ((jdn + p["jjd"] + j2beg[:, None]) % 2 == 0) & (ch["n"] < p["nd"][:, None])
    if Tfac is not None:
        win = Tfac * win
    fd = torch.zeros((Bc, ND), dtype=F64, device=dev)
    fd.scatter_add_(1, nc, torch.where(isd & parity_ok, win, 0.0))
    fd = fd * p["rho_d"]
    _G._add_discrete(contrib, fd, p)
    sub[:, ty, :, :J] += contrib
    stage("ct:feed-disc", sub.device, _t0)


def _moldauer(bk: Batch, sel: Tensor, prep: dict, denom: Tensor, live: Tensor, sub: Tensor,
              x: Tensor, wts: Tensor, nJ: int, f32: bool = True) -> None:
    """`gpu_full._moldauer` on the channel lists.

    TALYS: molprepare.f90:1 (molprepare), moldauer.f90:1 (moldauer), comptarget.f90:1
    Test: GPU3
    """
    t, d = bk.t, bk.dims
    dev = bk.device
    Bc = sel.numel()
    K = t["j2"].shape[1]
    k0 = d["k0"]
    wf = int(t["wfcfactor"][sel][0])
    st = torch.where(live, denom, 1.0)
    tinc = t["tinc"][sel]
    cn = t["cn"][sel]
    nu_inc = _degrees_of_freedom(tinc, st[:, :, None], wf)
    t0 = time.perf_counter()
    t_all = torch.cat([torch.where(prep[ty]["ch"]["T"] > 1.0e-30, prep[ty]["ch"]["T"], 0.0)
                       for ty in range(1, 7)], 1)  # (Bc, F)
    r_all = torch.cat([prep[ty]["r"] for ty in range(1, 7)], 2)  # (Bc, K, F)
    t0 = stage("mol:rw", dev, t0)
    gam = prep[0]["D"]
    factor = _log_product(t_all, r_all, st, x, wf, f32 and LOG_F32)  # (Bc, K, M)
    expo = gam[:, :, None] * x[None, None, :] / st[:, :, None]
    capt = torch.where(expo > 80.0, 0.0, torch.exp(-torch.clamp(expo, max=80.0)))
    prod = wts * wts * torch.exp(x) * torch.exp(factor) * capt  # (Bc, K, M)
    fa = 2.0 * tinc / (st[:, :, None] * nu_inc)
    da = 1.0 + x[None, None, :, None] * fa[:, :, None, :]  # (Bc, K, M, A)
    H = (tinc[:, :, None, :] / da).sum(3)
    PH = prod * H
    gg = PH.sum(2)  # (Bc, K)
    ea = (prod[..., None] * (2.0 / nu_inc)[:, :, None, :] / da ** 2).sum(2)  # (Bc, K, A)
    t0 = stage("mol:integral", dev, t0)
    j2 = t["j2"][sel].to(F64)
    pref = torch.where(live, cn[:, None] * (j2 + 1.0) / st, 0.0)
    _feed(sub, 0, prep[0], pref * gg, True, nJ)
    for ty in range(1, 7):
        p = prep[ty]
        T = p["ch"]["T"]
        _t1 = time.perf_counter()
        Gb = _node_sum(PH, T, st, x, wf, f32 and NODE_F32)  # (Bc, K, nch)
        stage("mol:nodes", dev, _t1)
        Y = pref[:, :, None] * (T[:, None, :] * Gb)
        Y = torch.where(p["ch"]["ok"][:, None, :], Y, 0.0)
        _feed(sub, ty, p, Y, False, nJ)
        if ty == k0:
            _elastic(bk, sel, p, pref, tinc, ea, sub, ty)
    stage("mol:feed", dev, t0)


_MF = os.environ.get("GPU3_MOL_F32", "log,node")
LOG_F32, NODE_F32 = "log" in _MF, "node" in _MF
# runs whose compound elastic is this many times their nonelastic are redone in float64 (54 of
# the 7,120 at 1000; the largest ratio on the sweep is 2,129):
# xsnonel = xsreacinc - xscompel (binary.f90:320) multiplies the float32 rounding of the
# Moldauer terms (~2e-8 in xscompel) by that ratio
F64_AMP = float(os.environ.get("GPU3_MOL_F64_AMP", "1000"))


def _log_terms(t_all: Tensor, r_all: Tensor, st: Tensor, x: Tensor, f32: bool) -> Tensor:
    """sum over open channels of -nu/2 r log1p(2 T x / (st nu)) (Bc, K, M); with `f32` each term
    is formed in float32 and the sum over channels is float64 (WFCfactor 1)."""
    dt = torch.float32 if f32 else F64
    t, r, s, xx = t_all.to(dt), r_all.to(dt), st.to(dt), x.to(dt)
    nu = torch.clamp(1.78 + (t[:, None, :] ** 1.212 - 0.78) * torch.exp(-0.228 * s[:, :, None]),
                     max=2.0)
    eps = 2.0 * t[:, None, None, :] * xx[None, None, :, None] / (s[:, :, None, None]
                                                                 * nu[:, :, None, :])
    livee = eps > 1.0e-30
    logterm = torch.where(livee, torch.log1p(torch.where(livee, eps, 0.0)), 0.0)
    return ((-nu * 0.5 * r)[:, :, None, :] * logterm).to(F64).sum(3)


def _node_terms(PH: Tensor, T: Tensor, st: Tensor, x: Tensor, f32: bool) -> Tensor:
    """sum over nodes of PH / (1 + x 2T/(st nu)) (Bc, K, nch); with `f32` the terms are float32
    and the sum over nodes float64 (WFCfactor 1)."""
    dt = torch.float32 if f32 else F64
    t, s, xx = T.to(dt), st.to(dt), x.to(dt)
    nu = torch.clamp(1.78 + (t[:, None, :] ** 1.212 - 0.78) * torch.exp(-0.228 * s[:, :, None]),
                     max=2.0)
    fb = 2.0 * t[:, None, :] / (s[:, :, None] * nu)
    return (PH.to(dt)[..., None] / (1.0 + xx[None, None, :, None] * fb[:, :, None, :])).to(
        F64).sum(2)




def _log_product(t_all: Tensor, r_all: Tensor, st: Tensor, x: Tensor, wf: int,
                 f32: bool) -> Tensor:
    """sum over open channels of -nu/2 r log1p(2 T x / (st nu)) (Bc, K, M).

    TALYS: moldauer.f90:1 (moldauer)
    Test: GPU3
    """
    if wf == 1 and f32:
        return _log_terms_c(t_all, r_all, st, x, True)
    Bc, K, F = r_all.shape
    M = x.numel()
    out = torch.empty((Bc, K, M), dtype=F64, device=x.device)
    nu = _degrees_of_freedom(t_all[:, None, :], st[:, :, None], wf)  # (Bc, K, F)
    a = (-nu * 0.5 * r_all)
    step = max(1, int(4.0e7 // max(Bc * K * F, 1)))
    for m0 in range(0, M, step):
        xs = x[m0: m0 + step]
        eps = (2.0 * t_all[:, None, None, :] * xs[None, None, :, None]
               / (st[:, :, None, None] * nu[:, :, None, :]))
        livee = eps > 1.0e-30
        logterm = torch.where(livee, torch.log1p(torch.where(livee, eps, 0.0)), 0.0)
        out[:, :, m0: m0 + step] = (a[:, :, None, :] * logterm).sum(3)
    return out


def _node_sum(PH: Tensor, T: Tensor, st: Tensor, x: Tensor, wf: int, f32: bool) -> Tensor:
    """sum over nodes of PH / (1 + x 2T/(st nu)) (Bc, K, nch).

    TALYS: moldauer.f90:1 (moldauer)
    Test: GPU3
    """
    if wf == 1 and f32:
        return _node_terms_c(PH, T, st, x, True)
    Bc, K, M = PH.shape
    nch = T.shape[1]
    nu_b = _degrees_of_freedom(T[:, None, :], st[:, :, None], wf)
    fb = 2.0 * T[:, None, :] / (st[:, :, None] * nu_b)  # (Bc, K, nch)
    out = torch.empty((Bc, K, nch), dtype=F64, device=T.device)
    step = max(1, int(4.0e7 // max(Bc * K * M, 1)))
    for c0 in range(0, nch, step):
        f = fb[:, :, c0: c0 + step]
        out[:, :, c0: c0 + step] = (PH[..., None] / (1.0 + x[None, None, :, None]
                                                      * f[:, :, None, :])).sum(2)
    return out


def _elastic(bk: Batch, sel: Tensor, p: dict, pref: Tensor, tinc: Tensor, ea: Tensor,
             sub: Tensor, ty: int) -> None:
    """The elastic diagonal (ielas = 1) of `gpu_full._moldauer`: exit (l', j') = incident (l, j)
    at Ltarget, with `_mask_for` evaluated at those cells.

    TALYS: comptarget.f90:1 (comptarget)
    Test: GPU3
    """
    t = bk.t
    dev = bk.device
    Bc = sel.numel()
    K = p["K"]
    ND, L = p["ND"], p["L"]
    raw = p["raw"]
    lt = t["ltarget"][sel]
    li = t["inc_l"][sel]
    ui = t["inc_u"][sel]
    oka = t["inc_ok"][sel] & (li < L)
    lic = li.clamp(max=L - 1)
    bi = torch.arange(Bc, device=dev)[:, None, None]
    ltc = lt.clamp(max=ND - 1)
    jdl = p["jd2"][torch.arange(Bc, device=dev), ltc][:, None, None]
    pdl = p["pd"][torch.arange(Bc, device=dev), ltc][:, None, None]
    j2k = p["j2"][:, :, None]
    # GPUC: OPEN3M's A2 when the target level itself has an impossible 2J parity
    an = ((j2k + jdl + PARSPIN2[ty]) % 2 == 1) & (jdl >= 0)
    lmx = p["lmaxhf"][torch.arange(Bc, device=dev), ltc][:, None, None]
    jj = torch.where(an, p["jjta"][lic, ui], p["jjt"][lic, ui])  # (Bc, K, A)
    okx = torch.where(an, p["okta"][lic, ui] & (2 * lic + 1 <= 2 * lmx), p["okt"][lic, ui])
    lo = (j2k - jdl).abs()
    md = ((lo <= jj) & (jj <= j2k + jdl) & ((jj - lo) % 2 == 0) & okx
          & (ltc < p["nd"])[:, None, None])
    parm = (lic % 2) == (p["pidx"][:, :, None] != pdl).to(torch.int64)
    wgt = (md & parm).to(F64) * p["lm"][bi, lt[:, None, None], lic].to(F64)
    term = wgt * raw[bi, lt[:, None, None], lic, ui] * tinc * ea
    ex = torch.where(oka, term, 0.0).sum(2)  # (Bc, K)
    ar = torch.arange(Bc, device=dev)
    okel = (lt < p["nd"]) & p["ok"][ar, ltc]
    val = (pref * ex).sum(1) * p["rho_d"][ar, ltc]
    contrib = torch.zeros_like(sub[:, ty])
    contrib.index_put_((ar, lt, p["ird"][ar, ltc], p["pd"][ar, ltc]),
                       torch.where(okel, val, 0.0), accumulate=True)
    sub[:, ty] += contrib


def comptarget(bk: Batch, res: dict, budget: float | None = None) -> dict:
    """comptarget.f90 for every run: `pop` (B, 7, R, J, 2), the compound elastic and xsbinary
    (`gpu_full.comptarget`'s numbers).

    TALYS: comptarget.f90:1 (comptarget), molprepare.f90:1 (molprepare), moldauer.f90:1
    Test: GPU3
    """
    from physics.hf.compound import wfc

    budget = CT_BUDGET if budget is None else budget
    t, d = bk.t, bk.dims
    dev = bk.device
    B, R, J = d["B"], d["R"], d["J"]
    k0 = d["k0"]
    pop = torch.zeros((B, 7, R, J, 2), dtype=F64, device=dev)
    x, wts = wfc.gauss_laguerre(dev)
    nchan = torch.zeros(B, dtype=torch.int64, device=dev)
    for ty in range(1, 7):
        nchan += (res[ty]["tjl"] > 0.0).flatten(1).sum(1)
    wfch = t["wfc"].cpu().numpy()
    K = t["j2"].shape[1]
    nJ = K // 2
    host = nchan.cpu().numpy()
    # the largest per-run intermediates: weights (K x channels, twice) and the Moldauer
    # feeding's cell prefix tables (channels x cells x 2, pre and suf)
    cost = (K * 3.0 + 64.0) * np.maximum(host, 1) + 7 * R * J * 2 * 4.0
    _groups(bk, res, pop, x, wts, _chunks(cost, budget, wfch), wfch, nJ, True)
    ar = torch.arange(B, device=dev)
    lt = t["ltarget"]
    okl = lt <= t["maxex"][:, k0]
    if LOG_F32 or NODE_F32:
        el = torch.where(okl, pop[ar, k0, lt].sum((1, 2)), 0.0).cpu().numpy()
        reac = np.array([e["binary"]["xsreacinc"] for e in bk.host["E"]])
        redo = wfch & (el > F64_AMP * np.maximum(reac - el, 0.0))
        if redo.any():
            grps = [g for g in _chunks(cost[redo], budget, wfch[redo])]
            ix = np.flatnonzero(redo)
            _groups(bk, res, pop, x, wts, [ix[g] for g in grps], wfch, nJ, False)
        if _G.STAGE_TIMES is not None:
            _G.STAGE_TIMES["ct:f64-runs"] = _G.STAGE_TIMES.get("ct:f64-runs", 0) + int(redo.sum())
    el = torch.where(okl, pop[ar, k0, lt].sum((1, 2)), 0.0)
    xsb = pop.sum((2, 3, 4))
    xsb[:, k0] = xsb[:, k0] - pop[ar, k0, lt].sum((1, 2))
    return dict(pop=pop, el=el, xsbinary=xsb)


def _groups(bk: Batch, res: dict, pop: Tensor, x: Tensor, wts: Tensor, groups: list,
            wfch: np.ndarray, nJ: int, f32: bool) -> None:
    """comptarget for `groups` of runs into `pop`: Moldauer (`f32`: float32 terms) or no width
    fluctuations."""
    t, d = bk.t, bk.dims
    dev = bk.device
    R, J = d["R"], d["J"]
    for grp in groups:
        t0 = time.perf_counter()
        sel = torch.as_tensor(grp, device=dev)
        Bc = sel.numel()
        prep = {ty: _prep(bk, res, ty, sel) for ty in range(7)}
        t0 = stage("ct:prepare", dev, t0)
        denom = prep[0]["D"] + prep[1]["D"]
        for ty in range(2, 7):
            denom = denom + prep[ty]["D"]
        cellm = t["cell"][sel]
        live = cellm & (denom != 0.0)
        cn = t["cn"][sel]
        j2 = t["j2"][sel].to(F64)
        sub = torch.zeros((Bc, 7, R, J, 2), dtype=F64, device=dev)
        if bool(wfch[grp[0]]):
            _moldauer(bk, sel, prep, denom, live, sub, x, wts, nJ, f32)
        else:
            feed = torch.where(live, t["tinc"][sel].sum(2), 0.0)
            wn = torch.where(live, cn[:, None] * (j2 + 1.0) / torch.where(live, denom, 1.0)
                             * feed, 0.0)
            for ty in range(7):
                _feed(sub, ty, prep[ty], wn, True, nJ)
        pop[sel] = sub
        stage("ct:moldauer" if bool(wfch[grp[0]]) else "ct:nowfc", dev, t0)
        if _G.STAGE_TIMES is not None:
            _G.STAGE_TIMES["ct:groups"] = _G.STAGE_TIMES.get("ct:groups", 0) + 1
        del prep, sub


_log_terms_c = _compiled(_log_terms)
_node_terms_c = _compiled(_node_terms)
_weights_c = _compiled(_weights)
_cont_window_c = _compiled(_cont_window)
