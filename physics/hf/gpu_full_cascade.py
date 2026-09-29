"""multiple.f90's cascade on the (nuclide, energy) batch axis.

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

Task: GPUFULL. No physics of its own: `emission.multiple.multiple_emission` with
`compound.decay_fast.NucleusWidths` as its decay callback (the CPU engine's path), rearranged.

TALYS routines computed here:
    densprepare.f90:1 (densprepare)  -- primary = .false., every mother bin of a nucleus at once
    compound.f90:1 (compound)        -- without width fluctuations (flagfullhf = .false.)
    multiple.f90:1 (multiple), cascade.f90:1 (cascade)
    multipreeq2.f90:246-296          -- the flux side; the particle-hole side is set-up's

**Rows and levels.** A row is one cascade nucleus of one run. multiple.f90 decays nuclei in the
order Zcomp = 0.., Ncomp = 0..; a nucleus is fed only by nuclei with fewer nucleons removed, so
every nucleus with the same Zcomp + Ncomp (a LEVEL) can be decayed at once, and the rows of a
level are decayed together, cut into chunks of equal A parity (the spin-l' selection mask then
is one array per chunk). Summing a daughter's feeding from two mothers of one level in another
order is the only change, and it moves the last bits.

**Inside a row, the CPU engine's order.** Mother bins from the top down: the gamma cascade
through a discrete level under S_n, the popeps gates, multiple pre-equilibrium, the photon exit
into the row's own lower bins (it is read by the next bin); every particle exit is contracted
for all decayed bins after the walk, as `emission.multiple._decay_nucleus_numpy` does.

**Widths.** `NucleusWidths`: the residual rows' Eout and Rboundary, the particle transmissions
interpolated from the run's emission-grid table, rho0 from rhogrid, the spin-l' masks, the
denominators D and the discrete levels, per exit type, over chunks of mother bins with the row,
spin and l' axes cut to what the chunk reaches.

Test: GPUFULL / tests/hf/test_gpu_full.py
"""

from __future__ import annotations

import os
import time
from functools import lru_cache

import numpy as np
import torch
from torch import Tensor

from physics.hf import gpu_full_kernels as K
from physics.hf.gpu_full import (
    F64,
    NUMJ,
    PARN,
    PARSPIN2,
    PARZ,
    Batch,
    _pad_stack,
    interp_nodes,
    stage,
)

J_ALL = NUMJ + 1


def records_feedexcl(zc: int, nc: int, ty: int) -> bool:
    """`emission.multiple._records_feedexcl`."""
    if zc > 6 or nc > 10:
        return False
    return not (zc == 0 and nc == 0 and ty > 0)


@lru_cache(maxsize=512)
def _spin_l_mask(odd: int, parspin2: int, nj: int, J: int, L: int, device: str) -> Tensor:
    """`continuum._spin_l_mask` (nj, J, L) as float64."""
    j2 = 2 * torch.arange(nj) + odd
    irs2 = 2 * torch.arange(J) + (odd + parspin2) % 2
    j2min = (j2[:, None] - irs2[None, :]).abs()
    lbeg = torch.div((j2min - parspin2).abs(), 2, rounding_mode="floor")
    lend = torch.div(j2[:, None] + irs2[None, :] + parspin2, 2, rounding_mode="floor")
    lp = torch.arange(L)
    return ((lp >= lbeg[..., None]) & (lp <= lend[..., None])).to(F64).to(device)


@lru_cache(maxsize=512)
def _spin_parity_mask32(odd: int, parspin2: int, nj: int, J: int, L: int, particle: bool,
                        device: str) -> Tensor:
    """The spin-l' mask with the residual parity folded in, as a float32 matrix (J*2, L*nj*2):
    [i*2 + P_in, (l*nj + j)*2 + P_out] = M(j, i, l) where P_in = P_out xor (l odd) for
    particles and P_in = P_out for the photon (`exit_Q`'s flip), so that the Q table is
    rho0 (rows x J*2) times it and `populate` is Z times its transpose."""
    M = _spin_l_mask(odd, parspin2, nj, J, L, device)  # (nj, J, L)
    lp = torch.arange(L, device=M.device)
    flip = (lp % 2 == 1) if particle else torch.zeros(L, dtype=torch.bool, device=M.device)
    p = torch.arange(2, device=M.device)
    same = (p[:, None, None] == (p[None, None, :] ^ flip[None, :, None].to(torch.int64)))
    # (p_in, l, p_out) x M(j, i, l) -> (i, p_in, l, j, p_out)
    Mp = (M.permute(1, 2, 0)[:, None, :, :, None] * same[None, :, :, None, :].to(M.dtype))
    return Mp.reshape(J * 2, L * nj * 2).to(torch.float32).contiguous()


@lru_cache(maxsize=512)
def _spin_l_mask32(odd: int, parspin2: int, nj: int, J: int, L: int, device: str) -> Tensor:
    return _spin_l_mask(odd, parspin2, nj, J, L, device).to(torch.float32)


def _row_nj(sp: dict, bins) -> int:
    """The mother spin axis a row's decay reads: `maxJ + 1` of a continuum bin, the level's own
    spin + 1 of a discrete one (its population holds that one cell; `NucleusWidths.feeding`
    reads `pop[:maxJ + 1]`, which is zero past it)."""
    bins = np.asarray(bins, dtype=np.int64)
    if bins.size == 0:
        return 1
    disc = bins <= sp["nlast_grid"]
    nj = np.where(disc, sp["jdis"][bins].astype(np.int64) + 1, sp["maxj"][bins] + 1)
    return int(min(nj.max(), J_ALL))


def _rho_columns(s_: dict, Rt: int) -> int:
    """The residual spins a daughter's rho0 can reach: rhogrid columns holding a value >= 1e-20
    (rho0 = Rboundary * rhogrid with Rboundary <= 1 is cut below that) and not past maxJ."""
    rg = s_["rhogrid"][:Rt]
    if rg.size == 0:
        return 1
    cols = np.flatnonzero((rg >= 1.0e-20).any(axis=(0, 2)))
    jx = int(cols[-1]) + 1 if cols.size else 1
    nl = s_["nlast"]
    cont = np.arange(min(Rt, rg.shape[0])) > nl
    if cont.any():
        jx = min(jx, int(s_["maxj"][: rg.shape[0]][cont].max()) + 1)
    return max(jx, 1)


class Bucket:
    """Every (nucleus, run) row of a batch as concatenated tables (`gpu_full_setup.stack_run`),
    rows sorted by level, A parity, mother spins and bins; specs and rows on the device, the
    ragged rhogrid and photon tables on the host until a chunk needs them."""

    def __init__(self, bk: Batch):
        dev = bk.device
        E = bk.host["E"]
        R = bk.dims["R"]
        sts = [e["st"] for e in E]
        B = len(sts)
        S_off = np.concatenate([[0], np.cumsum([st["S"] for st in sts])]).astype(np.int64)
        N_off = np.concatenate([[0], np.cumsum([st["Nn"] for st in sts])]).astype(np.int64)
        rho_base = np.concatenate([[0], np.cumsum([st["rho"].size for st in sts])])
        tg_base = np.concatenate([[0], np.cumsum([st["tg"].size for st in sts])])
        cat = np.concatenate
        self.s_int = cat([st["s_int"] for st in sts])
        self.s_f = cat([st["s_f"] for st in sts])
        self.s_sep = cat([st["s_sep"] for st in sts])
        self.s_row = cat([st["s_row"] for st in sts])
        self.s_rowi = cat([st["s_rowi"] for st in sts])
        self.s_run = cat([np.full(st["S"], b) for b, st in enumerate(sts)]).astype(np.int64)
        self.rho = cat([st["rho"] for st in sts])
        self.rho_off = cat([st["rho_off"] + rho_base[b] for b, st in enumerate(sts)])
        self.skey = {}
        for b, st in enumerate(sts):
            for i, k in enumerate(st["skeys"]):
                self.skey[(tuple(k), b)] = int(S_off[b] + i)
        self.static = cat([st["static"] + S_off[b] for b, st in enumerate(sts)])
        n_int = cat([st["n_int"] for st in sts])
        n_run = cat([np.full(st["Nn"], b) for b, st in enumerate(sts)]).astype(np.int64)
        n_int[:, 0] += S_off[n_run]
        bins = cat([st["bins"] for st in sts])
        nxm = cat([st["nxm"] for st in sts])
        fnorm = cat([st["fnorm"] for st in sts])
        dspec = cat([st["dspec"] + S_off[b] for b, st in enumerate(sts)])
        drow = cat([np.where(st["drow"] >= 0, st["drow"] + N_off[b], -1)
                    for b, st in enumerate(sts)])
        nlb = max(st["br_k"].shape[1] for st in sts)
        nb = max(st["br_k"].shape[2] for st in sts)
        br_k = cat([_pad_stack(list(st["br_k"]), (nlb, nb), np.int64, -1) for st in sts])
        br_r = cat([_pad_stack(list(st["br_r"]), (nlb, nb)) for st in sts])
        tg_off = cat([st["tg_off"] + tg_base[b] for b, st in enumerate(sts)])
        tg_shape = cat([st["tg_shape"] for st in sts])
        self.tg = cat([st["tg"] for st in sts])
        m_int = cat([st["m_int"] + np.array([N_off[b], 0]) for b, st in enumerate(sts)])
        self.m_term = cat([st["m_term"] for st in sts])
        self.m_sum = cat([st["m_sum"] for st in sts])
        self.m_has = cat([st["m_has"] for st in sts])
        self.m_w = cat([np.broadcast_to(st["mpe_w"], (st["M"], NUMJ + 1)) for st in sts])
        # processing order: level, A parity, mother spins, bins, then TALYS's nucleus order
        # GPU3: the top bin (descending) after the A parity, so that the rows a walk step
        # can decay are a prefix of the chunk
        top = s_int_all = None
        s_int_all = np.concatenate([st["s_int"] for st in sts])
        top = s_int_all[n_int[:, 0], 0]
        order = np.lexsort((n_run, n_int[:, 6], n_int[:, 5], n_int[:, 1], n_int[:, 2], -top,
                            n_int[:, 4], n_int[:, 3]))
        inv = np.empty_like(order)
        inv[order] = np.arange(order.size)
        self.NS = int(order.size)
        self.n_int = n_int[order]
        self.n_run = n_run[order]
        self.bins = bins[order]
        self.nxm = nxm[order]
        self.fnorm = fnorm[order]
        self.dspec = dspec[order]
        d0 = drow[order]
        self.drow = np.where(d0 >= 0, inv[np.clip(d0, 0, None)], -1)
        self.br_k = br_k[order]
        self.br_r = br_r[order]
        self.tg_off = tg_off[order]
        self.tg_shape = tg_shape[order]
        self.m_row = inv[m_int[:, 0]] if m_int.size else np.zeros(0, dtype=np.int64)
        self.m_nex = m_int[:, 1] if m_int.size else np.zeros(0, dtype=np.int64)
        self.row_of = {}
        for b, e in enumerate(E):
            for j, k in enumerate(e["nuclei"]):
                self.row_of[(tuple(k), b)] = int(inv[N_off[b] + j])
        d = lambda a: torch.as_tensor(a, device=dev)  # noqa: E731
        self.dev_s_f, self.dev_s_sep = d(self.s_f), d(self.s_sep)
        self.dev_s_row, self.dev_s_rowi, self.dev_s_int = d(self.s_row), d(self.s_rowi), \
            d(self.s_int)
        # the ragged rhogrid and photon tables once per batch on the device (a chunk gathers them)
        self.dev_rho = d(self.rho)
        self.dev_rho_off = d(self.rho_off)
        self.dev_tg = d(self.tg)
        self.levels = self.n_int[:, 3]
        self.odds = self.n_int[:, 4]
        self.njs = self.n_int[:, 2]
        self.ms = self.n_int[:, 1]
        # GPU3: per-row tables every chunk reads, formed and uploaded once per batch (the chunks
        # slice them on the device)
        pe_run = np.array([r[0]["sc"]["popeps"] for r in bk.runs])
        self.popeps_row = pe_run[self.n_run]
        zc, nc = self.n_int[:, 5], self.n_int[:, 6]
        tt = np.arange(7)
        self.rec_row = (((zc <= 6) & (nc <= 10))[:, None]
                        & ~(((zc == 0) & (nc == 0))[:, None] & (tt > 0)[None, :]))
        brk = self.br_k
        later = np.zeros(brk.shape, dtype=bool)
        for q in range(brk.shape[2] - 1):
            later[:, :, q] = ((brk[:, :, q + 1:] == brk[:, :, q:q + 1])
                              & (brk[:, :, q:q + 1] >= 0)).any(2)
        i16 = lambda a: torch.as_tensor(a.astype(np.int16), device=dev)  # noqa: E731
        self.dev_n_run = d(self.n_run)
        self.dev_sm = d(self.n_int[:, 0].copy())
        self.dev_nb = d(self.n_int[:, 1].copy())
        self.dev_bins16 = i16(self.bins)
        self.dev_nxm16 = i16(self.nxm)
        self.dev_fnorm = d(self.fnorm)
        self.dev_drow = d(self.drow)
        self.dev_dspec = d(self.dspec)
        self.dev_brk = d(brk)
        self.dev_brr = d(self.br_r)
        self.dev_brrec = d(~later)
        self.dev_rec = d(self.rec_row)
        self.dev_popeps = d(self.popeps_row)
        self.dev_tg_off = d(self.tg_off.astype(np.int64))
        self.dev_tg_shape = d(self.tg_shape)

    def chunks(self, budget: float, max_rows: int) -> list[tuple[int, int]]:
        """Contiguous rows of one level and one A parity, cut to `budget` elements of the
        chunk's largest per-row array."""
        out, start, acc = [], 0, 0.0
        # per row: the bins' (NJ, 2) width tables and the exits' (71 rows x l' x NJ x 2) Q/Z
        cost = np.maximum(self.ms, 1) * np.maximum(self.njs, 1) * 8.0 + \
            71.0 * 42 * np.maximum(self.njs, 1) * 2 * 3
        for i in range(self.NS + 1):
            new = (i == self.NS or (i > start and (
                self.levels[i] != self.levels[start] or self.odds[i] != self.odds[start]
                or acc + cost[i] > budget or i - start >= max_rows)))
            if new and i > start:
                out.append((start, i))
                start, acc = i, 0.0
            if i < self.NS:
                acc += cost[i]
        return out


class Chunk:
    """Rows r0..r1 of a `Bucket` gathered onto the device."""

    def __init__(self, bk: Batch, bu: Bucket, r0: int, r1: int):
        dev = bk.device
        R = bk.dims["R"]
        n = r1 - r0
        self.n, self.r0, self.r1 = n, r0, r1
        self.level = int(bu.levels[r0])
        self.odd = int(bu.odds[r0])
        ni = bu.n_int[r0:r1]
        self.zc, self.nc = ni[:, 5], ni[:, 6]
        self.keys = list(zip(self.zc.tolist(), self.nc.tolist()))
        runs_h = bu.n_run[r0:r1]
        self.runs_h = runs_h
        self.runs = bu.dev_n_run[r0:r1]
        sm_h = ni[:, 0]
        sm = bu.dev_sm[r0:r1]
        self.m = m = max(int(ni[:, 1].max()), 1)
        self.NJ = int(max(ni[:, 2].max(), 1))
        self.maxex_h = bu.s_int[sm_h, 0]
        self.maxex = bu.dev_s_int[sm, 0]
        self.nlg = bu.dev_s_int[sm, 2]
        self.ex, self.dex = bu.dev_s_row[sm, 0], bu.dev_s_row[sm, 1]
        self.jdis, self.tau = bu.dev_s_row[sm, 2], bu.dev_s_row[sm, 3]
        self.maxj, self.parlev = bu.dev_s_rowi[sm, 0], bu.dev_s_rowi[sm, 1]
        self.sep = bu.dev_s_sep[sm]
        self.popeps = bu.dev_popeps[r0:r1]
        self.popepsA = self.popeps / torch.clamp(5 * self.maxex, min=1).to(F64)
        bins_h = bu.bins[r0:r1, :m]
        nb_h = ni[:, 1]
        binm_h = np.arange(m)[None, :] < nb_h[:, None]
        nxm_h = bu.nxm[r0:r1, :m]
        self.bins = bu.dev_bins16[r0:r1, :m].to(torch.int64)
        self.binm = torch.arange(m, device=dev)[None, :] < bu.dev_nb[r0:r1, None]
        rowidx = torch.full((n, R + 1), -1, dtype=torch.int64, device=dev)
        rowidx.scatter_(1, torch.where(self.binm, self.bins, R),
                        torch.arange(m, device=dev).expand(n, m))
        self.rowidx = rowidx[:, :R].contiguous()
        self.nxm = bu.dev_nxm16[r0:r1, :m].to(torch.int64)
        self.Rt = [int(max(v, 0)) + 1 for v in nxm_h.reshape(-1, 7).max(0)]
        self.fnorm = bu.dev_fnorm[r0:r1]
        self.nuc = bk.t["nuc"][self.runs]
        self.lmaxinc = bk.t["lmaxinc"][self.runs]
        nucs = np.unique(bk.t_host["nuc"][runs_h])
        lmx = bk.t_host["lmax_max"][nucs].max(0)
        self.Lp = [0] + [int(min(lmx[t - 1] + 1, bk.dims["Lp"][t])) for t in range(1, 7)]
        # photon transmissions: this chunk's flat segments, and per (row, bin) row offsets
        shp = bu.tg_shape[r0:r1]
        self.G = int(max(shp[:, 2].max(), 1))
        self.tgf = bu.dev_tg
        self.tg_base = bu.dev_tg_off[r0:r1]  # offsets into the batch's device table
        self.tg_n0 = bu.dev_tg_shape[r0:r1, 1].contiguous()
        self.tg_lc = bu.dev_tg_shape[r0:r1, 2].contiguous()
        cnt = torch.where(self.binm, torch.minimum(self.bins, self.tg_n0[:, None]), 0)
        self.tg_boff = torch.cat([torch.zeros((n, 1), dtype=torch.int64, device=dev),
                                  torch.cumsum(cnt, 1)[:, :-1]], 1)
        # daughters
        ds_h = bu.dspec[r0:r1]
        dr_h = bu.drow[r0:r1]
        self.drow = bu.dev_drow[r0:r1]
        self.dkeys = None
        self.d = []
        for t in range(7):
            Rt = self.Rt[t]
            st = ds_h[:, t]
            sti = bu.dev_dspec[r0:r1, t].contiguous()
            nl_h = bu.s_int[st, 1]
            jx_h = bu.s_int[st, 5]
            nd_h = np.minimum(nl_h, Rt - 1) + 1
            ND = int(nd_h.max())
            jd = (2.0 * bu.s_row[st, 2, :ND].astype(np.float32)).astype(np.int64) // 2
            jd = np.where(np.arange(ND)[None, :] < nd_h[:, None], jd, 0)
            Jt = int(min(max(jx_h.max(), jd.max() + 1, 1), J_ALL))
            self.d.append(dict(
                Rt=Rt, Jt=Jt, ND=ND,
                ex=bu.dev_s_row[sti, 0, :Rt], dex=bu.dev_s_row[sti, 1, :Rt],
                jdis=bu.dev_s_row[sti, 2, :Rt], maxj=bu.dev_s_rowi[sti, 0, :Rt],
                parlev=bu.dev_s_rowi[sti, 1, :Rt], nlast=bu.dev_s_int[sti, 1],
                ntop=bu.dev_s_int[sti, 3], discfactor=bu.dev_s_f[sti, 0],
                rhogrid=_gather_rho_dev(bu, sti, Rt, Jt),
                spec_h=st))
        self.rec = bu.rec_row[r0:r1]
        self.rec_d = bu.dev_rec[r0:r1]
        # multiple pre-equilibrium records of these rows (row, mother bin), and multipreeq2's
        # summpe by (row, mother bin): the walk's Dmulti (compound.f90:402)
        self.mpe = None
        self.summpe = torch.zeros((n, R), dtype=F64, device=dev)
        if bu.m_row.size:
            sel = np.flatnonzero((bu.m_row >= r0) & (bu.m_row < r1))
            if sel.size:
                rows_l = bu.m_row[sel] - r0
                nexs = bu.m_nex[sel]
                self.mpe = dict(rows=torch.as_tensor(rows_l, device=dev), rows_h=rows_l,
                                nex=torch.as_tensor(nexs, device=dev), nex_h=nexs,
                                term=torch.as_tensor(bu.m_term[sel], device=dev),
                                sums=torch.as_tensor(bu.m_sum[sel], device=dev),
                                has=torch.as_tensor(bu.m_has[sel], device=dev),
                                w=torch.as_tensor(bu.m_w[sel], device=dev),
                                empty=torch.as_tensor((bu.m_sum[sel] == 0.0).all(1), device=dev))
                self.summpe[self.mpe["rows"], self.mpe["nex"]] = self.mpe["sums"][:, 2]
        # host structure of the walk
        mx = self.maxex_h
        self.walk_top = int(mx.max())
        nlg = bu.s_int[sm_h, 2]
        smin = bu.s_sep[sm_h, 1]
        exh = bu.s_row[sm_h, 0]
        tauh = bu.s_row[sm_h, 3]
        brk_h = bu.br_k[r0:r1]
        nexs = np.arange(R)
        dunder = (nexs[None, :] <= nlg[:, None]) & (exh <= smin[:, None]) & \
            (nexs[None, :] <= mx[:, None])
        nlb = brk_h.shape[1]
        brany = np.zeros((n, R), dtype=bool)
        brany[:, :nlb] = (brk_h >= 0).any(2)
        self.gc_any = (dunder & (tauh == 0.0) & brany).any(0)
        self.dec_any = np.zeros(R, dtype=bool)
        self.dec_any[bins_h[binm_h]] = True
        # `gamma_cascade`'s record is a dict keyed by daughter level: of two branches to one
        # level the populations get both and `feedexcl` only the later one (`Bucket.dev_brrec`)
        self.br_rec = bu.dev_brrec[r0:r1]
        self.brk = bu.dev_brk[r0:r1]
        self.brr = bu.dev_brr[r0:r1]
        self.nlb = nlb
        self.bu_s_int, self.bu_s_rowi = bu.dev_s_int, bu.dev_s_rowi
        self.trk_any = (dr_h >= 0).any(0)
        self.e_last = {}

    def tg_bins(self, ic: Tensor, R0: int) -> Tensor:
        """Photon transmissions (n, mc, 2, R0, G) of mother-bin rows `ic` (n, mc)."""
        n, mc = ic.shape
        G = self.G
        dev = ic.device
        if G <= 1 or self.tgf.numel() == 0:
            return torch.zeros((n, mc, 2, R0, G), dtype=F64, device=dev)
        bi = torch.arange(n, device=dev)[:, None]
        binr = self.bins[bi, ic]  # (n, mc)
        lc = self.tg_lc[:, None]  # (n, 1)
        stride = 2 * torch.clamp(lc - 1, min=1)
        r = torch.arange(R0, device=dev)
        c = torch.arange(2, device=dev)
        lq = torch.arange(1, G, device=dev)
        start = self.tg_base[:, None] + self.tg_boff[bi, ic] * stride  # (n, mc)
        idx = (start[:, :, None, None, None] + r[None, None, None, :, None] * stride[:, :, None,
               None, None] + c[None, None, :, None, None] * (lc - 1)[:, :, None, None, None]
               + (lq - 1)[None, None, None, None, :])
        ok = ((r[None, None, None, :, None] < torch.minimum(binr, self.tg_n0[:, None])[:, :, None,
               None, None]) & (lq[None, None, None, None, :] < lc[:, :, None, None, None])
              & self.binm[bi, ic][:, :, None, None, None])
        vals = self.tgf[torch.where(ok, idx, 0)]
        out = torch.zeros((n, mc, 2, R0, G), dtype=F64, device=dev)
        out[..., 1:] = torch.where(ok, vals, 0.0)
        return out


def _gather_rho_dev(bu: Bucket, spec: Tensor, Rt: int, Jt: int) -> Tensor:
    """`_gather_rho` on the device, from the batch's uploaded table."""
    dev = spec.device
    jx = bu.dev_s_int[spec, 5]
    nr = bu.dev_s_int[spec, 0] + 1
    off = bu.dev_rho_off[spec]
    r = torch.arange(Rt, device=dev)[None, :, None, None]
    j = torch.arange(Jt, device=dev)[None, None, :, None]
    p = torch.arange(2, device=dev)[None, None, None, :]
    idx = off[:, None, None, None] + (r * jx[:, None, None, None] + j) * 2 + p
    ok = (r < nr[:, None, None, None]) & (j < jx[:, None, None, None])
    if bu.dev_rho.numel() == 0:
        return torch.zeros(ok.shape, dtype=F64, device=dev)
    return torch.where(ok, bu.dev_rho[torch.where(ok, idx, 0)], 0.0)


def _gather_rho(bu: Bucket, spec: np.ndarray, Rt: int, Jt: int) -> np.ndarray:
    """rhogrid (n, Rt, Jt, 2) of specs `spec` from the bucket's ragged table."""
    n = spec.size
    jx = bu.s_int[spec, 5]
    nr = bu.s_int[spec, 0] + 1
    off = bu.rho_off[spec]
    r = np.arange(Rt)[None, :, None, None]
    j = np.arange(Jt)[None, None, :, None]
    p = np.arange(2)[None, None, None, :]
    idx = off[:, None, None, None] + (r * jx[:, None, None, None] + j) * 2 + p
    ok = (r < nr[:, None, None, None]) & (j < jx[:, None, None, None])
    out = np.zeros((n, Rt, Jt, 2))
    if bu.rho.size:
        out = np.where(ok, bu.rho[np.where(ok, idx, 0)], 0.0)
    return out


def exit_arrays(bk: Batch, ch: Chunk, ty: int, ic: Tensor) -> dict:
    """`NucleusWidths`' exit `ty` for the mother-bin rows `ic` (n, mc) of chunk `ch`, without rho0:
    `rb` (n, mc, Rt) the Rboundary of each residual row (0 outside the bin's reach), the
    transmissions `T` (n, mc, Rt, L) (the photon's `(T0, T1)` pair: (n, mc, 2, Rt, G)), and the
    discrete levels' `rho_d` (n, mc, ND), parity index `pd`, spin index `ird` and l' window
    `Md` (n, NJ, ND, L). rho0 of the continuum rows enters through `exit_Q`.

    TALYS: densprepare.f90:1 (densprepare), compound.f90:1 (compound)
    Test: GPUFULL
    """
    t = bk.t
    dev = bk.device
    d = ch.d[ty]
    Rt, Jt, ND = d["Rt"], d["Jt"], d["ND"]
    n, mc = ic.shape
    NJ = ch.NJ
    bi = torch.arange(n, device=dev)[:, None]
    binr = ch.bins[bi, ic]
    live_bin = ch.binm[bi, ic]
    exinc = ch.ex[bi, binr]
    dexinc = ch.dex[bi, binr]
    rows = torch.arange(Rt, device=dev)
    nexm = torch.clamp(ch.nxm[bi, ic, ty], min=0)
    inrow = (rows[None, None, :] <= nexm[..., None]) & live_bin[..., None]
    ex = d["ex"][:, None, :]
    dexhalf = 0.5 * d["dex"][:, None, :]
    ss = ch.sep[:, ty][:, None, None]
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
    nl = d["nlast"]
    cont_row = rows[None, None, :] > nl[:, None, None]
    exm = ex + ss
    part = (ex0min < exm) & (exm <= ex0plus)
    dexs = torch.where(part, dexinc[..., None], 1.0)
    rb_d = torch.where(part, (ex0plus - exm) / dexs, 1.0)
    rb = torch.where(cont_row, rb_c, rb_d)
    e = dict(ty=ty, sfac=1.0 if ty == 0 else float(PARSPIN2[ty] + 1), Rt=Rt, Jt=Jt, ND=ND)
    if ty == 0:
        T = torch.where(inrow[:, :, None, :, None], ch.tg_bins(ic, Rt), 0.0)  # (n,mc,2,Rt,G)
        L = T.shape[-1]
    else:
        eout_c = 0.5 * (torch.where(below, 0.0, emin) + emax)
        eout_d = torch.where(part, 0.5 * (ex0plus + exm) - ss - ex,
                             (exinc[..., None] - ss) - ex)
        eout = torch.where(inrow, torch.where(cont_row, eout_c, eout_d), 0.0)
        ip = interp_nodes(t, ch.nuc[:, None, None], torch.full((1, 1, 1), ty, device=dev), eout)
        nuc3 = ip["nuc"]
        L = ch.Lp[ty]
        TL = t["tl_cut"][ty][..., :L]  # (Nn, E, L) for this type
        head0 = t["tl_head0"][:, ty - 1][nuc3]
        inr = inrow & ip["ok"]
        lmaxhf = torch.where(inr, ip["lm"], 0)
        has = nexm > 0
        prev = lmaxhf.gather(2, torch.clamp(nexm - 1, min=0)[..., None])[..., 0]
        cur = lmaxhf.gather(2, nexm.clamp(max=Rt - 1)[..., None])[..., 0]
        lmaxhf = lmaxhf.scatter(2, nexm.clamp(max=Rt - 1)[..., None],
                                torch.where(has, prev, cur)[..., None])
        if ty == bk.dims["k0"]:
            lmaxhf[:, :, 0] = ch.lmaxinc[:, None]
        lcap = torch.minimum(ip["lm"], lmaxhf)
        lcap = torch.where(inr & ~(ip["below"] & head0), lcap, -1)
        u = (ip["w1"][..., None] * TL[nuc3, ip["na"]] + ip["w2"][..., None] * TL[nuc3, ip["nb"]]
             + ip["w3"][..., None] * TL[nuc3, ip["nc"]])
        lp = torch.arange(L, device=dev)
        fn = ch.fnorm[:, ty + 1][:, None, None, None]
        eps = t["transeps"][nuc3][..., None]
        T = torch.where((lp <= lcap[..., None]) & (u >= eps), u * fn, 0.0)  # (n, mc, Rt, L)
    e["T"] = T
    e["L"] = L
    e["rb"] = torch.where(inrow, rb, 0.0)
    # discrete rows: one (Ir, parity) cell each
    ndd = torch.minimum(nl, torch.full_like(nl, Rt - 1)) + 1
    kk = torch.arange(ND, device=dev)
    rbd = rb[:, :, :ND]
    val = torch.where(kk[None, None, :] > d["ntop"][:, None, None],
                      rbd * d["discfactor"][:, None, None], rbd)
    jdis_d = d["jdis"][:, :ND]
    jd2 = (2.0 * jdis_d.to(torch.float32)).to(torch.int64)
    ird = torch.div(jd2, 2, rounding_mode="floor")
    pd = (d["parlev"][:, :ND] > 0).to(torch.int64)
    okd = (ird >= 0) & (ird <= NUMJ) & (kk[None, :] < ndd[:, None])
    ir_w = jdis_d.to(torch.int64)
    pidx_w = torch.where(d["parlev"][:, :ND] == -1, 0, 1)
    same = (ir_w == ird) & (pidx_w == pd) & (ir_w >= 0) & (ir_w <= NUMJ) & okd
    rho_d = torch.where(same[:, None, :] & inrow[:, :, :ND], val, 0.0)
    rho_d = torch.where(rho_d >= 1.0e-20, rho_d, 0.0)
    rho_d[:, :, 0] = torch.where((nl == 0)[:, None], 0.0, rho_d[:, :, 0])
    j2 = 2 * torch.arange(NJ, device=dev)[None, :] + ch.odd
    lbeg = torch.div(((j2[:, :, None] - jd2[:, None, :]).abs() - PARSPIN2[ty]).abs(), 2,
                     rounding_mode="floor")
    lend = torch.div(j2[:, :, None] + jd2[:, None, :] + PARSPIN2[ty], 2, rounding_mode="floor")
    lpd = torch.arange(L, device=dev)
    e["Md"] = ((lpd >= lbeg[..., None]) & (lpd <= lend[..., None])).to(F64)  # (n, NJ, ND, L)
    e.update(rho_d=rho_d, ird=ird.clamp(0, NUMJ), pd=pd)
    return e


def exit_Q(bk: Batch, ch: Chunk, ty: int, L: int) -> dict:
    """rho0 of exit `ty`'s continuum rows contracted with the spin-l' selection rule, once per
    chunk: `Qm[b, r*L + l, J*2 + P] = sum_i rhog(b, r, i, P') M(J, i, l)`, with P' the residual
    parity a mother parity P reaches through l' (particles: P' = P for even l', 1 - P for odd;
    the photon's two radiation types are its T0/T1 pair, so P' = P there).

    rho0 = Rboundary * rhogrid is cut at 1e-20 in densprepare; here the cut is taken on rhogrid,
    which differs only in rows with Rboundary < 1 and there by less than 1e-20 * T per cell.

    TALYS: compound.f90:1 (compound)
    Test: GPUFULL
    """
    dev = bk.device
    d = ch.d[ty]
    Rt, Jt = d["Rt"], d["Jt"]
    NJ = ch.NJ
    rows = torch.arange(Rt, device=dev)
    base = (ch.odd + PARSPIN2[ty]) % 2
    jj = torch.arange(Jt, device=dev)
    maxj_d = d["maxj"]
    valid = ((2 * jj[None, None, :] + base <= 2 * maxj_d[:, :, None])
             & (jj[None, None, :] <= maxj_d[:, :, None])
             & (rows[None, :] > d["nlast"][:, None])[:, :, None])  # (n, Rt, Jt)
    rhog = torch.where(valid[..., None] & (d["rhogrid"] >= 1.0e-20), d["rhogrid"], 0.0)
    M = _spin_l_mask(ch.odd, PARSPIN2[ty], NJ, Jt, L, str(dev))  # (NJ, Jt, L)
    Qe = torch.einsum("brip,jil->brljp", rhog, M)  # (n, Rt, L, NJ, 2)
    if ty >= 1:
        lp = torch.arange(L, device=dev)
        Qe = torch.where((lp % 2 == 1)[None, None, :, None, None], Qe.flip(4), Qe)
    n = Qe.shape[0]
    return dict(Qm=Qe.reshape(n, Rt * L, NJ * 2), rhog=rhog, M=M)


def widths_of(e: dict, Q: dict, NJ: int) -> Tensor:
    """D (n, mc, NJ, 2) of an exit: `sum rho0 T` over its residual rows, spins, l' and j'."""
    n, mc = e["rb"].shape[:2]
    Rt, L = e["Rt"], e["L"]
    if e["ty"] >= 1:
        W = (e["rb"][..., None] * e["T"]).reshape(n, mc, Rt * L)
        D = torch.bmm(W, Q["Qm"]).reshape(n, mc, NJ, 2)
        T0 = e["T"][:, :, : e["ND"]] * (torch.arange(L, device=W.device) % 2 == 0)
        T1 = e["T"][:, :, : e["ND"]] - T0
    else:
        W0 = (e["rb"][..., None] * e["T"][:, :, 0]).reshape(n, mc, Rt * L)
        W1 = (e["rb"][..., None] * e["T"][:, :, 1]).reshape(n, mc, Rt * L)
        D = (torch.bmm(W0, Q["Qm"]).reshape(n, mc, NJ, 2)
             + torch.bmm(W1, Q["Qm"]).reshape(n, mc, NJ, 2).flip(3))
        T0, T1 = e["T"][:, :, 0, : e["ND"]], e["T"][:, :, 1, : e["ND"]]
    pd = e["pd"][:, None, :, None]
    rd = e["rho_d"][..., None]
    r_par = rd * (pd == 1)
    r_npar = rd * (pd == 0)
    dd0 = torch.einsum("bjkl,bmkl->bmj", e["Md"], T0 * r_npar + T1 * r_par)
    dd1 = torch.einsum("bjkl,bmkl->bmj", e["Md"], T0 * r_par + T1 * r_npar)
    return e["sfac"] * (D + torch.stack([dd0, dd1], -1))


def feed_of(e: dict, Q: dict, F: Tensor, NJ: int) -> tuple[Tensor, Tensor, Tensor]:
    """A particle exit fed by F (n, mc, NJ, 2): `(Z, mcont, fd)` with Z (n, Rt*L, NJ*2) the
    continuum feeding summed over the bins (`populate`), mcont (n, mc, Rt) the per-bin row sums
    and fd (n, mc, ND) the discrete cells' feeding (`NucleusWidths._contract`)."""
    n, mc = e["rb"].shape[:2]
    Rt, L, ND = e["Rt"], e["L"], e["ND"]
    W = (e["rb"][..., None] * e["T"]).reshape(n, mc, Rt * L)
    Fm = F.reshape(n, mc, NJ * 2)
    Z = torch.bmm(W.transpose(1, 2), Fm)
    H = torch.bmm(Fm, Q["Qm"].transpose(1, 2))  # (n, mc, Rt*L)
    mcont = (H * W).reshape(n, mc, Rt, L).sum(3) * e["sfac"]
    T0 = e["T"][:, :, :ND] * (torch.arange(L, device=F.device) % 2 == 0)
    T1 = e["T"][:, :, :ND] - T0
    tot0 = torch.einsum("bjkl,bmkl->bmjk", e["Md"], T0)
    tot1 = torch.einsum("bjkl,bmkl->bmjk", e["Md"], T1)
    A = torch.einsum("bmjp,bmjk->bmpk", F, tot0)
    Bq = torch.einsum("bmjp,bmjk->bmpk", F, tot1)
    pd = e["pd"]
    fd = (A.gather(2, pd[:, None, None, :].expand(n, mc, 1, ND))[:, :, 0]
          + Bq.gather(2, (1 - pd)[:, None, None, :].expand(n, mc, 1, ND))[:, :, 0])
    fd = e["sfac"] * e["rho_d"] * fd
    return Z, mcont, fd


def populate(e: dict, Q: dict, Z: Tensor, NJ: int) -> Tensor:
    """The continuum feeding (n, Rt, Jt, 2) of a daughter from the bin-summed Z."""
    n = Z.shape[0]
    Rt, L = e["Rt"], e["L"]
    Zs = Z.reshape(n, Rt, L, NJ, 2)
    lp = torch.arange(L, device=Z.device)
    Zs = torch.where((lp % 2 == 1)[None, None, :, None, None], Zs.flip(4), Zs)
    Y = torch.einsum("brljp,jil->brip", Zs, Q["M"])
    return e["sfac"] * Q["rhog"] * Y


def prepare_tables(bk: Batch) -> None:
    """Per-type cuts of the emission-grid Tl table and its all-zero head (`decay_fast._tl_stack`)."""
    t = bk.t
    if "tl_cut" in t:
        return
    TL = t["tl"]  # (Nn, 6, E, L)
    Lp = [0] * 7
    cut = [None] * 7
    for ty in range(1, 7):
        nz = (TL[:, ty - 1] != 0.0).any(0).any(0)
        idx = torch.nonzero(nz).flatten()
        L = int(idx[-1]) + 1 if idx.numel() else 1
        Lp[ty] = L
        cut[ty] = TL[:, ty - 1, :, :L].contiguous()
    t["tl_cut"] = cut
    bk.dims["Lp"] = Lp
    t["tl_head0"] = ~(TL[:, :, :3] != 0.0).flatten(2).any(2)  # (Nn, 6)


CHUNK_BUDGET = float(os.environ.get("GPUFULL_CHUNK_BUDGET", "1.2e8"))
BIN_BUDGET = float(os.environ.get("GPUFULL_BIN_BUDGET", "1.0e9"))
BIN_PER = int(os.environ.get("GPUFULL_BIN_PER", "3"))


def cascade(bk: Batch, bn: dict, cw=None, budget: float | None = None, max_rows: int = 4096,
            bin_budget: float | None = None) -> dict:
    """multiple.f90 over every run's cascade tree (module docstring), feeding `cw`
    (a `gpu_full_channels.ChannelWalk`) as it goes.

    Returns the flags of what the batch could not reproduce: `mpe_gate` (B,), a multiple
    pre-equilibrium record on a bin whose popeps gates closed.

    TALYS: multiple.f90:1 (multiple), compound.f90:1 (compound), cascade.f90:1 (cascade)
    Test: GPUFULL
    """
    dims = bk.dims
    dev = bk.device
    budget = CHUNK_BUDGET if budget is None else budget
    bin_budget = BIN_BUDGET if bin_budget is None else bin_budget
    B, R, J = dims["B"], dims["R"], dims["J"]
    prepare_tables(bk)
    bu = Bucket(bk)
    bk.host["bucket"] = bu
    NS = bu.NS
    X = torch.zeros((NS, R, J, 2), dtype=F64, device=dev)
    XE = torch.zeros((NS, R), dtype=F64, device=dev)
    NUC = torch.zeros(NS, dtype=F64, device=dev)
    for ty in range(7):
        k = (PARZ[ty], PARN[ty])
        pairs = [(bu.row_of[(k, b)], b) for b in range(B) if (k, b) in bu.row_of]
        if not pairs:
            continue
        ri = torch.as_tensor([p[0] for p in pairs], device=dev)
        bi = torch.as_tensor([p[1] for p in pairs], device=dev)
        Xs = bn["xspop"][ty][bi]
        X.index_add_(0, ri, Xs)
        XE.index_add_(0, ri, bn["xspopex"][ty][bi])
        NUC.index_add_(0, ri, Xs.sum((1, 2, 3)))
    bn.pop("xspop")  # GPU3: copied into X; freed for the chunks
    flags = dict(mpe_gate=torch.zeros(B, dtype=torch.bool, device=dev), mpe_gate_bins=[])
    done = 0  # channel levels whose validity is formed

    def finish_levels(below: int) -> None:
        nonlocal done
        while cw is not None and done < below:
            cw.level_done(done)
            done += 1

    for (r0, r1) in bu.chunks(budget, max_rows):
        t0 = time.perf_counter()
        finish_levels(int(bu.levels[r0]))
        t0 = stage("c:level_done", dev, t0)
        ch = Chunk(bk, bu, r0, r1)
        stage("c:chunk", dev, t0)
        _decay_chunk(bk, bn, ch, X[r0:r1], XE[r0:r1], NUC, X, XE, cw, flags, bin_budget)
        del ch
    if cw is not None:
        finish_levels(max(list(cw.by_level) + [int(bu.levels.max()) if NS else 0]) + 1)
    return flags


def _bin_chunks(ch: Chunk, bin_budget: float) -> list[tuple[int, int]]:
    per = 0
    for t, d in enumerate(ch.d):
        L = ch.G if t == 0 else ch.Lp[t]
        per = max(per, d["Rt"] * d["Jt"] * 2, d["Rt"] * L * 2, d["Jt"] * 2 * L * 2,
                  ch.NJ * d["ND"] * L)
        per = max(per, d["Rt"] * L * 4)
    per = ch.n * max(per, 1) * BIN_PER
    step = max(1, int(bin_budget // max(per, 1)))
    return [(c0, min(ch.m, c0 + step)) for c0 in range(0, ch.m, step)]


def _exit_ctx(bk: Batch, ch: Chunk, ty: int) -> dict:
    """The bin-independent arguments of exit `ty`'s fused kernels for chunk `ch`: the daughter's
    discrete-level masks, spin windows `Md` and (particles) the rows' emission-grid tables.

    TALYS: densprepare.f90:1 (densprepare)
    Test: GPUFULL2
    """
    t = bk.t
    dev = bk.device
    d = ch.d[ty]
    Rt, ND = d["Rt"], d["ND"]
    L = ch.G if ty == 0 else ch.Lp[ty]
    dmask, dfac, pd, ird, lbeg, lend, Md = K.disc_tables_c(
        d["nlast"], d["jdis"][:, :ND].contiguous(), d["parlev"][:, :ND].contiguous(), d["ntop"],
        d["discfactor"], Rt, ch.NJ, ch.odd, PARSPIN2[ty], L, ty == 0 or not DENSE32)
    c = dict(L=L, Rt=Rt, ND=ND, Jt=d["Jt"], dmask=dmask, dfac=dfac, Md=Md, pd=pd, lb=lbeg,
             le=lend,
             ird=ird, sep=ch.sep[:, ty].contiguous(), d_ex=d["ex"].contiguous(),
             d_dex=d["dex"].contiguous(), d_nlast=d["nlast"],
             sfac=1.0 if ty == 0 else float(PARSPIN2[ty] + 1))
    if ty >= 1:
        nuc = ch.nuc
        c.update(egrid_r=t["egrid"][nuc], egrid32_r=t["egrid32"][nuc], ib=t["ebegin"][nuc, ty],
                 ie=t["eend"][nuc, ty], maxen=t["maxen"][nuc], lmax_r=t["lmax"][nuc, ty - 1],
                 TL_r=t["tl_cut"][ty][nuc, :, :L].contiguous(), head0=t["tl_head0"][nuc, ty - 1],
                 eps=t["transeps"][nuc], fn=ch.fnorm[:, ty + 1].contiguous())
    return c


def _bin_args(ch: Chunk, c: dict, ty: int, c0: int, c1: int) -> tuple:
    sl = slice(c0, c1)
    return (ch.bins[:, sl].contiguous(), ch.binm[:, sl].contiguous(),
            ch.nxm[:, sl, ty].contiguous(), ch.ex, ch.dex, c["sep"], c["d_ex"], c["d_dex"],
            c["d_nlast"])


def _particle_args(ch: Chunk, c: dict, bk: Batch, ty: int) -> tuple:
    return (c["egrid_r"], c["egrid32_r"], c["ib"], c["ie"], c["maxen"], c["lmax_r"], c["TL_r"],
            c["head0"], c["eps"], c["fn"], ch.lmaxinc, c["dmask"], c["dfac"])


USE_CUDAGRAPH = os.environ.get("GPUFULL_CUDAGRAPH", "1") != "0"
# GPU3: stages whose contractions run in float32 (`wf`: particle widths and feeding, `photon`:
# the photon widths); everything accumulated stays float64
_CF = os.environ.get("GPU3_CASCADE_F32", "dense")
DENSE32 = "dense" in _CF  # particle widths and feeding as dense float32 bmms, Q not cached
F32_WF, F32_PHOTON = "wf" in _CF and not DENSE32, "photon" in _CF or DENSE32
F32_WALK = "nowalk" not in _CF  # the walk's photon exit in float32 (bmm form)
WALK_CAPS = int(os.environ.get("GPU3_WALK_CAPS", "3"))  # halving steps of the walk's row caps
WALK_CAPS_ON = WALK_CAPS > 1
WALK_WARM_ALL = os.environ.get("GPU3_WALK_WARM_ALL", "0") == "1"
WALK_SYNC = os.environ.get("GPU3_WALK_SYNC", "0") == "1"  # host syncs around captures


WALK_STATS: dict = {}  # capture seconds and count (diagnostics)
STAGE_PROBE = os.environ.get("GPU3_WALK_PROBE", "0") == "1"
_TLS = __import__("threading").local()  # capture stream and graph pool, per thread


def _capture_stream():
    if getattr(_TLS, "stream", None) is None:
        _TLS.stream = torch.cuda.Stream()
    return _TLS.stream


def _graph_pool():
    """One private pool for every chunk's walk graph (per thread), kept alive by an anchor graph
    (a pool whose last graph is deleted cannot be captured into again)."""
    if getattr(_TLS, "pool", None) is None:
        pool = torch.cuda.graph_pool_handle()
        anchor = torch.cuda.CUDAGraph()
        torch.cuda.synchronize()
        with torch.cuda.stream(_capture_stream()):
            anchor.capture_begin(pool)
            try:
                torch.zeros(1, device="cuda").add_(1.0)
            finally:
                anchor.capture_end()
        torch.cuda.synchronize()
        _TLS.pool = (pool, anchor)
    return _TLS.pool[0]


_WARM_SIGS: set = set()  # walk step shape classes that have run outside a capture


def _shape_sig(*dims: int) -> tuple:
    """The sizes torch.compile specialises on (0, 1, other)."""
    return tuple(min(int(v), 2) for v in dims)


Z_SLICE = 2.5e7  # elements of one slice of Z's (triples x l' x 2 NJ) addends


def exit_Q_live(bk: Batch, ch: Chunk, ty: int, L: int, br_idx: Tensor) -> dict:
    """`exit_Q` on the (row, residual row) pairs `br_idx` (flat over (n, Rt)) that a live triple
    reads: `Qr` (nbr, L, NJ*2), with the pairs' rhog (nbr, Jt, 2) and the spin-l' mask.

    TALYS: compound.f90:1 (compound)
    Test: GPUFULL2
    """
    dev = bk.device
    d = ch.d[ty]
    Rt, Jt = d["Rt"], d["Jt"]
    NJ = ch.NJ
    rows = torch.arange(Rt, device=dev)
    base = (ch.odd + PARSPIN2[ty]) % 2
    jj = torch.arange(Jt, device=dev)
    maxj_d = d["maxj"]
    valid = ((2 * jj[None, None, :] + base <= 2 * maxj_d[:, :, None])
             & (jj[None, None, :] <= maxj_d[:, :, None])
             & (rows[None, :] > d["nlast"][:, None])[:, :, None])
    rhog = torch.where(valid[..., None] & (d["rhogrid"] >= 1.0e-20), d["rhogrid"], 0.0)
    rhog_c = rhog.reshape(-1, Jt, 2)[br_idx]
    M = _spin_l_mask(ch.odd, PARSPIN2[ty], NJ, Jt, L, str(dev))  # (NJ, Jt, L)
    Qe = torch.einsum("rip,jil->rljp", rhog_c, M)  # (nbr, L, NJ, 2)
    lp = torch.arange(L, device=dev)
    Qe = torch.where((lp % 2 == 1)[None, :, None, None], Qe.flip(3), Qe)
    Qr = Qe.reshape(-1, L, NJ * 2)
    if F32_WF:
        qs = Qr.amax(1)
        qs = torch.where(qs > 0.0, qs, 1.0)
        return dict(Qs=(Qr / qs[:, None, :]).to(torch.float32), qs=qs, rhog_c=rhog_c, M=M,
                    br_idx=br_idx)
    return dict(Qr=Qr, rhog_c=rhog_c, M=M, br_idx=br_idx)


def exit_Q32(bk: Batch, ch: Chunk, ty: int, L: int) -> dict:
    """`exit_Q` in float32 (GPU3): `Qs` (n, Rt*L, NJ*2) with each (J, parity) column divided by
    its largest value `qs` (float64 (n, NJ*2)), and the cut `rhog` and mask for `populate32`.

    TALYS: compound.f90:1 (compound)
    Test: GPU3
    """
    dev = bk.device
    d = ch.d[ty]
    Rt, Jt = d["Rt"], d["Jt"]
    NJ = ch.NJ
    base = (ch.odd + PARSPIN2[ty]) % 2
    M = _spin_l_mask(ch.odd, PARSPIN2[ty], NJ, Jt, L, str(dev))  # (NJ, Jt, L)
    Mp = _spin_parity_mask32(ch.odd, PARSPIN2[ty], NJ, Jt, L, ty >= 1, str(dev))
    Qs, qs, rhog = K.q_table32_c(d["rhogrid"], d["maxj"], d["nlast"], base, Mp, NJ)
    return dict(Qs=Qs, qs=qs, rhog=rhog, M=M, Mp=Mp)


def populate32(Q: dict, Z32: Tensor, fr: Tensor, NJ: int, sfac: float, n: int, Rt: int,
               L: int) -> Tensor:
    """`populate` from the float32 bin-summed Z (units of the row scale `fr`)."""
    return K.populate32_c(Z32, Q["Mp"], Q["rhog"], fr, sfac, n, Rt, L, NJ)


def populate_live(Qd: dict, Zr: Tensor, NJ: int, sfac: float, n: int, Rt: int) -> Tensor:
    """`populate` on the compact pairs: the continuum feeding (n, Rt, Jt, 2)."""
    nbr, L = Zr.shape[0], Zr.shape[1]
    Jt = Qd["rhog_c"].shape[1]
    Zs = Zr.reshape(nbr, L, NJ, 2)
    lp = torch.arange(L, device=Zr.device)
    Zs = torch.where((lp % 2 == 1)[None, :, None, None], Zs.flip(3), Zs)
    Y = torch.einsum("rljp,jil->rip", Zs, Qd["M"])
    out = torch.zeros((n * Rt, Jt, 2), dtype=F64, device=Zr.device)
    out[Qd["br_idx"]] = sfac * Qd["rhog_c"] * Y
    return out.reshape(n, Rt, Jt, 2)


def _widths_particles(bk: Batch, ch: Chunk, c: dict, ty: int, bchunks: list) -> tuple:
    """A particle exit's widths over every bin chunk on the live triples: [D per bin chunk],
    [triples per bin chunk] and the compact Q table the feeding reuses after the walk."""
    n, NJ, Rt = ch.n, ch.NJ, c["Rt"]
    dev = bk.device
    nodes, brl = [], None
    for c0, c1 in bchunks:
        nd = K.particle_nodes_c(*_bin_args(ch, c, ty, c0, c1), c["egrid_r"], c["egrid32_r"],
                                c["ib"], c["ie"], c["maxen"], c["lmax_r"], c["head0"],
                                ch.lmaxinc, ty, ty == bk.dims["k0"])
        nodes.append(nd)
        a_ = nd[7].any(1)
        brl = a_ if brl is None else brl | a_
    br_idx = torch.nonzero(brl.reshape(-1)).flatten()
    if br_idx.numel() == 0:
        return ([torch.zeros((n, c1 - c0, NJ, 2), dtype=F64, device=dev) for c0, c1 in bchunks],
                [None] * len(bchunks), None)
    Qd = exit_Q_live(bk, ch, ty, c["L"], br_idx)
    br_map = torch.full((n * Rt,), -1, dtype=torch.int64, device=dev)
    br_map[br_idx] = torch.arange(br_idx.numel(), device=dev)
    Ds, gots = [], []
    for (c0, c1), nd in zip(bchunks, nodes, strict=True):
        mc = c1 - c0
        rb, lcap, na, w1, w2, w3, _inrow, live = nd
        idx = torch.nonzero(live.reshape(-1)).flatten()
        if idx.numel() == 0:
            Ds.append(torch.zeros((n, mc, NJ, 2), dtype=F64, device=dev))
            gots.append(None)
            continue
        got = K.particle_rows_c(rb, lcap, na, w1, w2, w3, idx, c["TL_r"], c["eps"], c["fn"],
                                br_map, mc, Rt)
        b, m, r, qrow, rb_r, T = got
        if F32_WF:
            Ds.append(K.widths_rows32_c(b, m, r, qrow, rb_r, T, Qd["Qs"], Qd["qs"], c["Md"],
                                        c["pd"], c["dmask"], c["dfac"], c["sfac"], n, mc, NJ))
        else:
            Ds.append(K.widths_rows_c(b, m, r, qrow, rb_r, T, Qd["Qr"], c["Md"], c["pd"],
                                      c["dmask"], c["dfac"], c["sfac"], n, mc, NJ))
        gots.append(got)
    return Ds, gots, Qd


def _widths_dense(bk: Batch, ch: Chunk, c: dict, ty: int, bchunks: list) -> tuple:
    """A particle exit's widths over every bin chunk: the live triples (`particle_nodes`,
    `particle_rows`) contracted as dense float32 bmms with the row Q table (`exit_Q32`, not kept):
    [D per bin chunk], [triples per bin chunk].

    TALYS: compound.f90:1 (compound)
    Test: GPU3
    """
    n, NJ, Rt = ch.n, ch.NJ, c["Rt"]
    dev = bk.device
    Q = None
    Ds, gots = [], []
    dummy = torch.zeros((n * Rt,), dtype=torch.int64, device=dev)
    for c0, c1 in bchunks:
        mc = c1 - c0
        _t = time.perf_counter()
        nd = K.particle_nodes_c(*_bin_args(ch, c, ty, c0, c1), c["egrid_r"], c["egrid32_r"],
                                c["ib"], c["ie"], c["maxen"], c["lmax_r"], c["head0"],
                                ch.lmaxinc, ty, ty == bk.dims["k0"])
        rb, lcap, na, w1, w2, w3, _inrow, live = nd
        idx = torch.nonzero(live.reshape(-1)).flatten()
        if idx.numel() == 0:
            Ds.append(torch.zeros((n, mc, NJ, 2), dtype=F64, device=dev))
            gots.append(None)
            continue
        _t = stage("w:nodes", dev, _t)
        got = K.particle_rows_c(rb, lcap, na, w1, w2, w3, idx, c["TL_r"], c["eps"], c["fn"],
                                dummy, mc, Rt)
        del nd, rb, lcap, na, w1, w2, w3, _inrow, live
        _t = stage("w:rows", dev, _t)
        if Q is None:
            Q = exit_Q32(bk, ch, ty, c["L"])
            _t = stage("w:Q", dev, _t)
        b, m, r, _q, rb_r, T = got
        Ds.append(K.widths_dense32_c(b, m, r, rb_r, T, Q["Qs"], Q["qs"], c["lb"], c["le"],
                                     c["pd"], c["dmask"], c["dfac"], c["sfac"], n, mc, Rt, NJ))
        gots.append((b, m, r, rb_r, T))
        stage("w:kernel", dev, _t)
    return Ds, gots


def _feed_ragged(c: dict, got, Qd: dict, F: Tensor, Zr: Tensor, n: int, mc: int):
    """A particle exit fed by F (n, mc, NJ, 2) on the live triples `got`: (mcont, fd), with the
    continuum feeding added to the compact `Zr`."""
    Rt, ND = c["Rt"], c["ND"]
    if got is None:
        z = torch.zeros((n, mc, Rt), dtype=F64, device=F.device)
        return z, torch.zeros((n, mc, ND), dtype=F64, device=F.device)
    b, m, r, qrow, rb_r, T = got
    if F32_WF:
        mcont, fd = K.feed_rows32_c(b, m, r, qrow, rb_r, T, Qd["Qs"], Qd["qs"], c["Md"], c["pd"],
                                    c["dmask"], c["dfac"], F, c["sfac"], n, mc, Rt)
    else:
        mcont, fd = K.feed_rows_c(b, m, r, qrow, rb_r, T, Qd["Qr"], c["Md"], c["pd"],
                                  c["dmask"], c["dfac"], F, c["sfac"], n, mc, Rt)
    nr = b.numel()
    step = max(1, int(Z_SLICE // (T.shape[1] * F.shape[2] * 2)))
    for s0 in range(0, nr, step):
        sl = slice(s0, min(nr, s0 + step))
        K.z_rows(b[sl], m[sl], qrow[sl], rb_r[sl], T[sl], F, Zr, mc)
    return mcont, fd


def _decay_chunk(bk, bn, ch: Chunk, X: Tensor, XE: Tensor, NUC: Tensor, Xall: Tensor,
                 XEall: Tensor, cw, flags: dict, bin_budget: float) -> None:
    """Every row of one chunk: widths, the walk down the mother bins, the particle exits
    (`gpu_full_kernels` holds the fused arithmetic; this is the bookkeeping around it)."""
    dev = bk.device
    R, J = bk.dims["R"], bk.dims["J"]
    n, m, NJ = ch.n, ch.m, ch.NJ
    ar = torch.arange(n, device=dev)
    NUCc = NUC[ch.r0: ch.r1]
    act = NUCc >= ch.popeps  # multiple.f90:262
    popexcl = torch.zeros((n, R + 2), dtype=F64, device=dev)
    rec_d = ch.rec_d
    rec0 = rec_d[:, 0]
    chan0 = cw is not None and any(cw.is_channel_nucleus(k) for k in set(ch.keys))
    f0 = torch.zeros((n, R + 1, R), dtype=F64, device=dev) if chan0 else None
    bchunks = _bin_chunks(ch, bin_budget)
    t0 = time.perf_counter()
    ctx = [_exit_ctx(bk, ch, ty) for ty in range(7)]
    # ---- widths of every decayable bin, and the photon exit's per-bin pieces
    dsum6 = torch.zeros((n, m, NJ, 2), dtype=F64, device=dev)
    zero6 = torch.ones((n, m, NJ, 2), dtype=torch.bool, device=dev)
    D6 = torch.zeros((n, m, NJ, 2), dtype=F64, device=dev)
    c0x = ctx[0]
    R0, J0, ND0 = c0x["Rt"], c0x["Jt"], c0x["ND"]
    rb0 = torch.zeros((n, m, R0), dtype=F64, device=dev)
    rhod0 = torch.zeros((n, m, ND0), dtype=F64, device=dev)
    G = ch.G
    M0 = None
    rows_cache = [[] for _ in range(7)]
    q_cache = [None] * 7
    for ty in range(7):
        c = ctx[ty]
        if ty == 0:
            Q = exit_Q32(bk, ch, ty, c["L"]) if F32_PHOTON else exit_Q(bk, ch, ty, c["L"])
        elif DENSE32:
            Ds, rows_cache[ty] = _widths_dense(bk, ch, c, ty, bchunks)
            Q = None
        else:
            Ds, rows_cache[ty], Q = _widths_particles(bk, ch, c, ty, bchunks)
            q_cache[ty] = Q
        for q_, (c0, c1) in enumerate(bchunks):
            if ty == 0:
                ba = _bin_args(ch, c, ty, c0, c1)
                if F32_PHOTON:
                    D, rb, rho_d = K.photon_widths32_c(
                        *ba, ch.tgf, ch.tg_base, ch.tg_boff[:, c0:c1].contiguous(), ch.tg_n0,
                        ch.tg_lc, c["dmask"], c["dfac"], Q["Qs"], Q["qs"], c["Md"], c["pd"], G,
                        NJ)
                else:
                    D, rb, rho_d = K.photon_widths_c(
                        *ba, ch.tgf, ch.tg_base, ch.tg_boff[:, c0:c1].contiguous(), ch.tg_n0,
                        ch.tg_lc, c["dmask"], c["dfac"], Q["Qm"], c["Md"], c["pd"], G, NJ)
                rb0[:, c0:c1] = rb
                rhod0[:, c0:c1] = rho_d
            else:
                D = Ds[q_]
            if ty < 6:
                dsum6[:, c0:c1] += D
                zero6[:, c0:c1] &= D == 0.0
            else:
                D6[:, c0:c1] = D
            del D
        if ty == 0:
            M0 = Q["M"]
        Ds = None
        del Q
    # the photon exit's bin-independent pieces
    jj = torch.arange(J0, device=dev)
    rows0 = torch.arange(R0, device=dev)
    valid0 = ((2 * jj[None, None, :] + ch.odd <= 2 * ch.d[0]["maxj"][:, :, None])
              & (jj[None, None, :] <= ch.d[0]["maxj"][:, :, None])
              & (rows0[None, :] > ch.d[0]["nlast"][:, None])[:, :, None])
    rhog0 = torch.where(valid0[..., None], ch.d[0]["rhogrid"], 0.0)  # (n, R0, J0, 2)
    Md0, pd0, ird0 = c0x["Md"], c0x["pd"], c0x["ird"]
    t0 = stage("c:widths", dev, t0)
    Fst = torch.zeros((n, m, NJ, 2), dtype=F64, device=dev)
    deadst = torch.zeros((n, m, NJ, 2), dtype=torch.bool, device=dev)
    decayed = torch.zeros((n, m), dtype=torch.bool, device=dev)
    jd_int = ch.jdis.to(torch.int64).clamp(0, J - 1)
    pd_lev = torch.where(ch.parlev == -1, 0, 1)
    jdt = ((2.0 * ch.jdis.to(torch.float32)).to(torch.int64) // 2).clamp(0, J - 1)
    smin = ch.sep[:, 1]
    rowsR = torch.arange(R, device=dev)
    ex_le_smin = ch.ex <= smin[:, None]  # (n, R)
    maxj_c = ch.maxj.contiguous()
    rowidx = ch.rowidx
    share_ix = (ar[:, None].expand(n, R), rowsR[None, :].expand(n, R), jdt, pd_lev)
    nlb = ch.nlb
    nex_d = torch.zeros(1, dtype=torch.int64, device=dev)  # the mother bin, on the device
    nex0 = nex_d[0]
    brk_c, brr_c, brrec_c = ch.brk, ch.brr, ch.br_rec
    tau0 = ch.tau == 0.0
    NB = brk_c.shape[2]
    bix = ar[:, None].expand(n, NB)
    ar_nex = ar  # (n,) row index for the (row, nex) reads
    Xf, XEf = X.view(-1), XE.view(-1)
    f0f = f0.view(-1) if f0 is not None else None
    share_flat = (((ar[:, None] * R + rowsR[None, :]) * J + jdt) * 2 + pd_lev).reshape(-1)
    summpe = ch.summpe

    on_t = torch.zeros((), dtype=torch.bool, device=dev)  # False: every write of a step is a no-op
    rhog0_32 = rhog0.to(torch.float32) if F32_WALK else None
    M0_32 = M0.to(torch.float32) if F32_WALK else None
    ND0 = rhod0.shape[2]

    def make_step(kc: int, rc: int):
        """One mother bin of the walk for the first `kc` rows (the rows are sorted by their top
        bin, so every row that can decay at this bin is among them) and the first `rc` residual
        rows (the photon exit feeds rows below the bin), with `nex_d` as the bin: every read and
        write indexes the device scalar, a bin with no gamma cascade or no decaying row adds
        exact zeros, so the kernel sequence is the same for every bin of a (kc, rc) and replays
        as one CUDA graph. With `on_t` False no row decays and the state is left as it was."""
        Xk, XEk, pk = X[:kc], XE[:kc], popexcl[:kc]
        Xfk, XEfk = Xk.view(-1), XEk.view(-1)
        f0k = f0[:kc] if f0 is not None else None  # noqa: F821 (closure over names deleted after the last step is built)
        f0fk = f0k.view(-1) if f0k is not None else None
        Fk, dk_, dck = Fst[:kc], deadst[:kc], decayed[:kc]
        # compiled kernels guard on strides and on the base of a view: slices are copied
        cc = lambda v: v[:kc].clone()  # noqa: E731
        actk, maxexk, nlgk = cc(act), cc(ch.maxex), cc(ch.nlg)
        exsk, tauk, jdk, pdk = cc(ex_le_smin), cc(tau0), cc(jd_int), cc(pd_lev)
        brkk, brrk, brreck, rec0k = cc(brk_c), cc(brr_c), cc(brrec_c), cc(rec0)
        summk, popAk, rowidxk, maxjk = cc(summpe), cc(ch.popepsA), cc(rowidx), cc(maxj_c)
        ds6k, z6k, D6k = cc(dsum6), cc(zero6), cc(D6)  # noqa: F821 (same)
        ndc = min(ND0, rc)
        rb0k = rb0[:kc, :, :rc].clone()
        rhod0k = rhod0[:kc, :, :ndc].clone()
        pd0k, ird0k = pd0[:kc, :ndc].clone(), ird0[:kc, :ndc].clone()
        Md0k = Md0[:kc, :, :ndc].clone()
        rhogk = (rhog0_32 if F32_WALK else rhog0)[:kc, :rc].clone()
        binsk, binmk = cc(ch.bins), cc(ch.binm)
        tgbk, tgbok, tgn0k, tglck = cc(ch.tg_base), cc(ch.tg_boff), cc(ch.tg_n0), cc(ch.tg_lc)
        ark = ar[:kc]
        bixk = bix[:kc]
        nexk = nex0.expand(kc)
        share_flatk = (((ark[:, None] * R + rowsR[None, :]) * J + jdt[:kc]) * 2
                       + pd_lev[:kc]).reshape(-1)
        drk, rmk = decrec[:kc], rmrec[:kc]
        kernel = K.decay_step32_c if F32_WALK else K.decay_step_c
        M0k = M0_32 if F32_WALK else M0

        def probe():
            """The step's two compiled kernels on arguments of the step's shapes, with no
            write: compiles what a capture of the step would otherwise compile."""
            rmask = actk & (nex0 <= maxexk) & on_t
            xe_col = XEk.index_select(1, nex_d)[:, 0]
            dunder = (nex0 <= nlgk) & exsk.index_select(1, nex_d)[:, 0]
            nb_d = torch.clamp(nex_d, max=nlb - 1)
            gc = (rmask & dunder & tauk.index_select(1, nex_d)[:, 0] & (nex0 < nlb))
            xsjp = Xk[ark, nexk, jdk.index_select(1, nex_d)[:, 0], pdk.index_select(1, nex_d)[:, 0]]
            kb = brkk.index_select(1, nb_d)[:, 0]
            K.gamma_step_c(xsjp, gc, kb.clone(), brrk.index_select(1, nb_d)[:, 0].clone(),
                           brreck.index_select(1, nb_d)[:, 0].clone(), rec0k)
            kernel(nex0, Xk.index_select(1, nex_d)[:, 0, :NJ].clone(), xe_col.clone(),
                   summk.index_select(1, nex_d)[:, 0].clone(), rmask.clone(), dunder.clone(),
                   popAk, rowidxk.index_select(1, nex_d)[:, 0].clone(),
                   maxjk.index_select(1, nex_d)[:, 0].clone(), ds6k,
                   z6k, D6k, rb0k, rhogk, rhod0k, pd0k, ird0k, M0k, Md0k,
                   binsk, binmk, ch.tgf, tgbk, tgbok, tgn0k, tglck, nlgk, rowsR, Fst, deadst,
                   decayed, G)

        def step():
            rmask = actk & (nex0 <= maxexk) & on_t
            xe_col = XEk.index_select(1, nex_d)[:, 0]
            pk.index_copy_(1, nex_d, torch.where(rmask, xe_col, 0.0)[:, None])
            dunder = (nex0 <= nlgk) & exsk.index_select(1, nex_d)[:, 0]
            # the gamma cascade through the discrete levels (gc_any / nlb masks are exact zeros)
            nb_d = torch.clamp(nex_d, max=nlb - 1)
            gc = (rmask & dunder & tauk.index_select(1, nex_d)[:, 0] & (nex0 < nlb))
            xsjp = Xk[ark, nexk, jdk.index_select(1, nex_d)[:, 0], pdk.index_select(1, nex_d)[:, 0]]
            kb = brkk.index_select(1, nb_d)[:, 0]
            intens, intens_rec = K.gamma_step_c(xsjp, gc, kb.clone(),
                                                brrk.index_select(1, nb_d)[:, 0].clone(),
                                                brreck.index_select(1, nb_d)[:, 0].clone(), rec0k)
            kcl = kb.clamp(min=0)
            # flat index_add_ (index_put_'s accumulate path sorts its indices, which a CUDA graph
            # does not replay faithfully)
            Xfk.index_add_(0, (((bixk * R + kcl) * J + jdk[bixk, kcl]) * 2
                               + pdk[bixk, kcl]).reshape(-1), intens.reshape(-1))
            XEfk.index_add_(0, (bixk * R + kcl).reshape(-1), intens.reshape(-1))
            xe_col = xe_col - intens.sum(1)
            if f0k is not None:
                f0fk.index_add_(0, ((bixk * (R + 1) + nex0) * R + kcl).reshape(-1),
                                intens_rec.reshape(-1))
            (dec, i, dp0, mc0, mc0s, share_v, share_e, newF, newdead, newdec) = kernel(
                nex0, Xk.index_select(1, nex_d)[:, 0, :NJ].clone(), xe_col.clone(),
                summk.index_select(1, nex_d)[:, 0].clone(), rmask.clone(), dunder.clone(), popAk,
                rowidxk.index_select(1, nex_d)[:, 0].clone(),
                maxjk.index_select(1, nex_d)[:, 0].clone(), ds6k,
                z6k, D6k, rb0k, rhogk, rhod0k, pd0k, ird0k, M0k, Md0k,
                binsk, binmk, ch.tgf, tgbk, tgbok, tgn0k, tglck, nlgk, rowsR, Fst, deadst,
                decayed, G)
            Xk[:, :rc, :J0] += dp0
            Xfk.index_add_(0, share_flatk, share_v.reshape(-1))
            XEk[:, :R] += share_e  # `_apply_leftover` runs before the photon exit's updates
            XEk[:, :rc] += mc0
            XEk.index_copy_(1, nex_d, (xe_col + share_e.index_select(1, nex_d)[:, 0]
                                       - mc0s)[:, None])
            if f0k is not None:
                row = f0k.index_select(1, nex_d)[:, 0, :rc]
                f0k[:, :, :rc].index_copy_(1, nex_d, torch.where((dec & rec0k)[:, None], mc0,
                                                                 row)[:, None])
                f0k.index_add_(1, nex_d, torch.where(rec0k[:, None], share_e, 0.0)[:, None])
            Fk.index_put_((ark, i), newF)
            dk_.index_put_((ark, i), newdead)
            dck.index_put_((ark, i), newdec)
            drk.index_copy_(1, nex_d, dec[:, None])
            rmk.index_copy_(1, nex_d, rmask[:, None])
            return dec, rmask

        step.probe = probe
        return step

    # the decay flag and popeps mask of every (row, mother bin), for the multiple
    # pre-equilibrium records applied after the walk
    decrec = torch.zeros((n, R), dtype=torch.bool, device=dev)
    rmrec = torch.zeros((n, R), dtype=torch.bool, device=dev)

    # rows are sorted by their top bin (descending) inside a chunk: the rows that can decay at
    # bin nex are the first k(nex); both caps step down a halving ladder as nex goes down
    mx_desc = -ch.maxex_h
    k_ladder = sorted({min(n, max(2, -(-n // (1 << t)))) for t in range(WALK_CAPS)})
    r_ladder = sorted({min(R0, max(2, -(-R0 // (1 << t)))) for t in range(WALK_CAPS)})
    graph = None
    key = None
    steps: dict = {}
    first = True
    if STAGE_PROBE:
        torch.cuda.synchronize()
        _tw = time.perf_counter()
    for nex in range(ch.walk_top, 0, -1):
        k_need = int(np.searchsorted(mx_desc, -nex, side="right"))
        kc = next(c for c in k_ladder if c >= k_need)
        rc = next(c for c in r_ladder if c >= min(nex, R0))
        if not WALK_CAPS_ON:
            kc, rc = n, R0
        nex_d.fill_(nex)
        if USE_CUDAGRAPH and dev.type == "cuda":
            if (kc, rc) != key:
                key = (kc, rc)
                step = make_step(kc, rc)
                graph = None
                on_t.fill_(False)
                sig = _shape_sig(kc, rc, min(ND0, rc), NJ, J0) + (G,)
                warmed = first or sig not in _WARM_SIGS or WALK_WARM_ALL
                if warmed:
                    # a no-op step on a side stream: compiles any new shape specialisation
                    # outside the capture
                    side = torch.cuda.Stream()
                    side.wait_stream(torch.cuda.current_stream())
                    with torch.cuda.stream(side):
                        step()
                    torch.cuda.current_stream().wait_stream(side)
                    _WARM_SIGS.add(sig)
                    first = False
                # `torch.cuda.graph` without its `empty_cache()`s; the capture pass runs with
                # `on_t` False, so it leaves the state as it was
                tc = time.perf_counter()
                cs = _capture_stream()
                if WALK_SYNC:
                    torch.cuda.synchronize()
                else:
                    cs.wait_stream(torch.cuda.current_stream())
                # a compilation must not run inside a capture: probe the kernels' guards with a
                # no-op step first when they would recompile (the probe itself compiles)
                if not warmed:
                    try:
                        with torch.compiler.set_stance("fail_on_recompile"):
                            step.probe()
                    except Exception:  # noqa: BLE001 (a recompile would be needed)
                        step.probe()
                        WALK_STATS["recompiles"] = WALK_STATS.get("recompiles", 0) + 1
                    cs.wait_stream(torch.cuda.current_stream())
                graph = torch.cuda.CUDAGraph()
                with torch.cuda.stream(cs):
                    graph.capture_begin(_graph_pool())
                    try:
                        outs = step()
                    finally:
                        graph.capture_end()
                if WALK_SYNC:
                    torch.cuda.synchronize()
                else:
                    torch.cuda.current_stream().wait_stream(cs)
                on_t.fill_(True)
                WALK_STATS["capture_s"] = (WALK_STATS.get("capture_s", 0.0)
                                           + time.perf_counter() - tc)
                WALK_STATS["captures"] = WALK_STATS.get("captures", 0) + 1
            graph.replay()
            dec, rmask = outs
        else:
            on_t.fill_(True)
            if (kc, rc) not in steps:
                steps[(kc, rc)] = make_step(kc, rc)
            dec, rmask = steps[(kc, rc)]()
    if STAGE_PROBE:
        _tl = time.perf_counter()
        torch.cuda.synchronize()
        WALK_STATS["loop_s"] = WALK_STATS.get("loop_s", 0.0) + _tl - _tw
        WALK_STATS["sync_s"] = WALK_STATS.get("sync_s", 0.0) + time.perf_counter() - _tl
        WALK_STATS["bins"] = WALK_STATS.get("bins", 0) + ch.walk_top
    del graph
    del dsum6, zero6, D6
    t0 = stage("c:walk", dev, t0)
    mpe_rec = None
    if ch.mpe is not None:
        # multipreeq2.f90:246-296 after the walk: what it writes (the daughters' populations
        # and this row's xspopex at the bin, after that bin decayed) is not read by the walk
        E = ch.mpe
        keep = np.flatnonzero(ch.dec_any[E["nex_h"]])
        if keep.size:
            kt = torch.as_tensor(keep, device=dev)
            ent = {k: (v[keep] if isinstance(v, np.ndarray) else v[kt]) for k, v in E.items()}
            d_e = decrec[ent["rows"], ent["nex"]]
            bad = _apply_mpe(ch, ent, d_e, rmrec[ent["rows"], ent["nex"]], XE, Xall, XEall, NUC)
            mpe_rec = (ent, d_e)
            for q in np.flatnonzero(bad.cpu().numpy()).tolist():
                b = int(ch.runs_h[ent["rows_h"][q]])
                flags["mpe_gate"][b] = True
                flags["mpe_gate_bins"].append((b, ch.keys[ent["rows_h"][q]], int(ent["nex_h"][q])))
    dbg = bk.host.get("debug")
    if dbg is not None:
        for j, k in enumerate(ch.keys):
            b = int(ch.runs_h[j])
            dbg.setdefault((k, b), {})["popexcl"] = popexcl[j].cpu().numpy()
            if f0 is not None:
                dbg[(k, b)]["f0"] = f0[j].cpu().numpy()
    # ---- channels at this chunk's nuclei (they need this walk's photon rows)
    keys_arr = ch.zc * 1000 + ch.nc
    if cw is not None:
        _channels_of_chunk(bk, bn, ch, cw, popexcl, f0, keys_arr)
        decayed_any = decayed.any(1) & act
        for ty in range(7):
            dk_arr = (ch.zc + PARZ[ty]) * 1000 + ch.nc + PARN[ty]
            for code in np.unique(dk_arr).tolist():
                sel = torch.as_tensor(np.flatnonzero(dk_arr == code), device=dev)
                keep = sel[decayed_any[sel]]
                cw.mark_reached((code // 1000, code % 1000), ch.runs[keep])
    del f0
    t0 = stage("c:channels", dev, t0)
    # ---- the particle exits of every decayed bin, after the walk
    drow = ch.drow
    for ty in range(1, 7):
        if not bool(ch.trk_any[ty]):
            continue
        c = ctx[ty]
        trk = drow[:, ty] >= 0
        q = drow[:, ty].clamp(min=0)
        Rt, Jt, ND, L = c["Rt"], c["Jt"], c["ND"], c["L"]
        if DENSE32:
            _feed_dense(bk, ch, c, ty, bchunks, rows_cache[ty], decayed, deadst, Fst, trk, q,
                        rec_d, popexcl, keys_arr, XE, Xall, XEall, NUC, cw)
            rows_cache[ty] = None
            continue
        Q = q_cache[ty]
        Zr = (torch.zeros((Q["br_idx"].numel(), L, NJ * 2), dtype=F64, device=dev)
              if Q is not None else None)
        kk = torch.arange(ND, device=dev)[None, :].expand(n, ND)
        pix = (q[:, None].expand(n, ND), kk, c["ird"].clamp(max=J - 1), c["pd"])
        for (c0, c1), got in zip(bchunks, rows_cache[ty], strict=True):
            dcy = decayed[:, c0:c1]
            binr = ch.bins[:, c0:c1]
            Fc = Fst[:, c0:c1]
            if ty == 6:
                Fc = torch.where(deadst[:, c0:c1], 0.0, Fc)
            ok = dcy & trk[:, None]
            Fc = torch.where(ok[:, :, None, None], Fc, 0.0)
            mcont, fd = _feed_ragged(c, got, Q, Fc, Zr, n, c1 - c0)
            tots = mcont.sum(2)
            XEall.index_add_(0, q, torch.nn.functional.pad(mcont.sum(1), (0, R - Rt))
                             * trk[:, None])
            NUC.index_add_(0, q, tots.sum(1) * trk)
            XE.scatter_add_(1, binr, -tots)
            Xall.index_put_(pix, fd.sum(1) * trk[:, None], accumulate=True)
            if cw is not None:
                _channel_contributions(ch, cw, ty, binr, ok & rec_d[:, ty, None], popexcl, mcont,
                                       keys_arr)
            del mcont, fd
        rows_cache[ty] = None
        q_cache[ty] = None
        if Q is not None:
            pop = populate_live(Q, Zr, NJ, c["sfac"], n, Rt)  # (n, Rt, Jt, 2)
            Jt = pop.shape[2]
            Xall.index_add_(0, q, torch.nn.functional.pad(pop, (0, 0, 0, J - Jt, 0, R - Rt))
                            * trk[:, None, None, None])
            del pop
        del Q, Zr
    t0 = stage("c:particles", dev, t0)
    if cw is not None:
        if mpe_rec is not None:
            # every multiple pre-equilibrium record of the chunk in one contraction per
            # (ejectile, nucleus): a row decayed at several bins appears once per bin
            ent, dec_e = mpe_rec
            rows_h, rows_e, nex_e = ent["rows_h"], ent["rows"], ent["nex"]
            has_e, term_e = ent["has"], ent["term"]
            rec_e = torch.as_tensor(ch.rec[rows_h], device=dev)
            sub_keys = keys_arr[rows_h]
            pe = popexcl[rows_e]
            for t in (1, 2):
                okm = dec_e & has_e[:, t - 1] & rec_e[:, t]
                for code in np.unique(sub_keys).tolist():
                    key = (code // 1000, code % 1000)
                    if not cw.is_channel_nucleus(key):
                        continue
                    kt = torch.as_tensor(np.flatnonzero(sub_keys == code), device=dev)
                    cw.contribute(key, ch.runs[rows_e[kt]], t, nex_e[kt][:, None],
                                  okm[kt][:, None], pe[kt], term_e[kt, t - 1][:, None, :])
        cn = np.flatnonzero(keys_arr == 0)
        if cn.size:
            sel = torch.as_tensor(cn, device=dev)
            for ty in range(1, 7):
                cw.contribute_top(ch.runs[sel], ty, bn["feedbinary"][ty][ch.runs[sel]])
    stage("c:mpe-channels", dev, t0)


def _feed_dense(bk, ch: Chunk, c: dict, ty: int, bchunks: list, gots: list, decayed: Tensor,
                deadst: Tensor, Fst: Tensor, trk: Tensor, q: Tensor, rec_d: Tensor,
                popexcl: Tensor, keys_arr, XE: Tensor, Xall: Tensor, XEall: Tensor, NUC: Tensor,
                cw) -> None:
    """A particle exit of every decayed bin of chunk `ch` after the walk, on the live triples of
    the widths contracted as dense float32 bmms (`gpu_full_kernels.feed_dense32`): the daughters'
    populations, the rows' bin sums and the channel contributions.

    TALYS: multiple.f90:1 (multiple), compound.f90:1 (compound)
    Test: GPU3
    """
    dev = bk.device
    R, J = bk.dims["R"], bk.dims["J"]
    n, NJ = ch.n, ch.NJ
    Rt, ND, L = c["Rt"], c["ND"], c["L"]
    if all(g is None for g in gots):
        return
    Fall = torch.where((decayed & trk[:, None])[:, :, None, None], Fst, 0.0)
    if ty == 6:
        Fall = torch.where(deadst, 0.0, Fall)
    fr = Fall.amax((1, 2, 3))
    fr = torch.where(fr > 0.0, fr, 1.0)
    _t = time.perf_counter()
    Q = exit_Q32(bk, ch, ty, L)
    _t = stage("f:Q", dev, _t)
    Z32 = torch.zeros((n, Rt * L, NJ * 2), dtype=torch.float32, device=dev)
    kk = torch.arange(ND, device=dev)[None, :].expand(n, ND)
    pix = (q[:, None].expand(n, ND), kk, c["ird"].clamp(max=J - 1), c["pd"])
    for (c0, c1), got in zip(bchunks, gots, strict=True):
        if got is None:
            continue
        b, m, r, rb_r, T = got
        mc = c1 - c0
        binr = ch.bins[:, c0:c1]
        ok = decayed[:, c0:c1] & trk[:, None]
        Zs, mcont, fd = K.feed_dense32_c(b, m, r, rb_r, T, Q["Qs"], Q["qs"], c["lb"], c["le"],
                                         c["pd"], c["dmask"], c["dfac"],
                                         Fall[:, c0:c1].contiguous(), fr, c["sfac"], n, mc, Rt,
                                         NJ)
        Z32 += Zs
        _t = stage("f:kernel", dev, _t)
        tots = mcont.sum(2)
        XEall.index_add_(0, q, torch.nn.functional.pad(mcont.sum(1), (0, R - Rt))
                         * trk[:, None])
        NUC.index_add_(0, q, tots.sum(1) * trk)
        XE.scatter_add_(1, binr, -tots)
        Xall.index_put_(pix, fd.sum(1) * trk[:, None], accumulate=True)
        _t = stage("f:book", dev, _t)
        if cw is not None:
            _channel_contributions(ch, cw, ty, binr, ok & rec_d[:, ty, None], popexcl, mcont,
                                   keys_arr)
        del Zs, mcont, fd
        _t = stage("f:chan", dev, _t)
    pop = populate32(Q, Z32, fr, NJ, c["sfac"], n, Rt, L)  # (n, Rt, Jt, 2)
    Jt = pop.shape[2]
    Xall.index_add_(0, q, torch.nn.functional.pad(pop, (0, 0, 0, J - Jt, 0, R - Rt))
                    * trk[:, None, None, None])
    stage("f:populate", dev, _t)


def _apply_mpe(ch: Chunk, ent: dict, d: Tensor, rm: Tensor, XE: Tensor, Xall: Tensor,
               XEall: Tensor, NUC: Tensor) -> Tensor:
    """multipreeq2.f90:246-296 / `emission.multiple._apply_mpe` for the records `ent` (E) of a
    chunk, `d`/`rm` the decay flag and popeps mask of each record's (row, bin). A record whose
    bin the popeps gates closed is not applied; returns the records to flag (closed and carrying
    flux, or its nucleus not decayed at that bin).

    Test: GPUFULL, GPU3
    """
    dev = XE.device
    R, J = XE.shape[1], Xall.shape[2]
    rows = ent["rows"]
    for t in (1, 2):
        q = ch.drow[rows, t]
        use = d & ent["has"][:, t - 1] & (q >= 0)
        qc = q.clamp(min=0)
        term = torch.where(use[:, None], ent["term"][:, t - 1], 0.0)  # (E, R)
        spec = torch.as_tensor(ch.d[t]["spec_h"][ent["rows_h"]], device=dev)
        bu_int = ch.bu_s_int[spec]
        mjd = ch.bu_s_rowi[spec, 0]  # (E, R) maxJ of the daughter
        kmax = torch.where(torch.arange(R, device=dev)[None, :] <= bu_int[:, 0][:, None],
                           torch.clamp(mjd, max=NUMJ), 0)
        wj = torch.where(torch.arange(J, device=dev)[None, None, :] <= kmax[:, :, None],
                         ent["w"][:, None, :J], 0.0)
        add = term[:, :, None] * wj  # (E, R, J)
        XEall.index_add_(0, qc, term)
        Xall.index_add_(0, qc, torch.stack([add, add], -1))
        NUC.index_add_(0, qc, torch.where(use, ent["sums"][:, t - 1], 0.0))
    XE.index_put_((rows, ent["nex"]), torch.where(d, -ent["sums"][:, 2], 0.0), accumulate=True)
    return (~d) & (~rm | ~ent["empty"])


def _channels_of_chunk(bk, bn, ch: Chunk, cw, popexcl: Tensor, f0, keys_arr) -> None:
    dev = bk.device
    for code in np.unique(keys_arr).tolist():
        key = (code // 1000, code % 1000)
        if not cw.is_channel_nucleus(key):
            continue
        sel_h = np.flatnonzero(keys_arr == code)
        sel = torch.as_tensor(sel_h, device=dev)
        top0 = bn["feedbinary"][0][ch.runs[sel]] if key == (0, 0) else None
        cw.nucleus(key, ch.runs[sel], popexcl[sel], f0[sel] if f0 is not None else None, top0,
                   runs_h=ch.runs_h[sel_h])


def _channel_contributions(ch: Chunk, cw, ty: int, binr: Tensor, ok: Tensor, popexcl: Tensor,
                           mcont: Tensor, keys_arr) -> None:
    dev = binr.device
    for code in np.unique(keys_arr).tolist():
        key = (code // 1000, code % 1000)
        if not cw.is_channel_nucleus(key) or not records_feedexcl(key[0], key[1], ty):
            continue
        sel = torch.as_tensor(np.flatnonzero(keys_arr == code), device=dev)
        cw.contribute(key, ch.runs[sel], ty, binr[sel], ok[sel], popexcl[sel], mcont[sel])
