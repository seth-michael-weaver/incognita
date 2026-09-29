"""The capture fast path with only the work its answer reads: photon feeding of the compound
nucleus, and gamma-independent tables that can be computed once and shipped.

Task: SPEED3 (stretch gate G0.2s, the lab network capture sweep). No physics of its own: every
number is produced by the same statements as `capture_fast.capture_xs`, in the same order.

**What the reference path computes and throws away.** `capture_fast.capture_xs` builds the
population of ONE nucleus -- the compound nucleus, `populations(st, 0, 0, ...)` -- and hands
it to `multiple_emission`, whose `daughters` dict is therefore `{0: cn}`: every particle exit
(t = 1..6) finds no daughter and is skipped. But `Cascade.decay` -> `NucleusDecay.feeding`
still contracts the population with the width tensors of all seven exit types for every bin,
and `multiple_emission` still walks the exclusive-channel bookkeeping (a Python float per
daughter bin) that only the full chain reads. Here a bin's decay contracts the photon exit
alone; the denominators (every type's summed width, the `dead`-cell rule of compound.f90:222,
the trapped-flux rule of :404-419) are the reference's own statements, so the photon feeding
is the same arithmetic on the same operands and `xspopnuc(0, 0)` is identical to the bit.

**What does not depend on the photon strength.** The emission-grid transmission coefficients
(`dens_reference._transmission`, T5 on six particles) and the incident channel
(`Cascade.incident`, T5 or T13's coupled channels) are the same for every photon-strength
parameter a fit (FIT1) varies, and together they were ~40% of the 482-nuclide sweep.
`tables(tg, energies)` returns them as plain tensors; `install_tables(tg, tables)` makes the
target read them instead of solving. They are the reference's own outputs, stored in float64.

Identity with `capture_fast.capture_xs` (bitwise, over the harness nuclides and energies) is
`tests/hf/test_capture_fast_batch.py`.
"""

from __future__ import annotations

from types import SimpleNamespace

import numpy as np
import torch
from torch import Tensor

from physics.hf.compound.prepare import NUMJ
from physics.hf.core.tensors import DTYPE


def _photon_feeding(nd, nex: int, xspop_mother, popeps_a: float, dmulti: float = 0.0):
    """`NucleusDecay.feeding` restricted to the photon exit: returns (dpop[0], mcontrib[0]).
    Every statement that reaches the photon feeding is copied from there, unchanged.

    TALYS: compound.f90:1 (compound)
    Test: SPEED3 / tests/hf/test_capture_fast_batch.py
    """
    dev = nd.device
    i = nd.row[nex]
    maxj = int(nd.maxj[i])
    nj = maxj + 1
    pop = torch.as_tensor(xspop_mother, dtype=DTYPE, device=dev)[:nj].clone()  # (nj, 2)
    popeps_b = popeps_a / (5 * max(maxj, 1)) * 0.5
    active = pop >= popeps_b
    if getattr(nd, "dsum", None) is not None:
        # `CaptureDecay` summed the widths of every bin up front, in the same order; a dead cell
        # has every other type's width at exactly 0, so its denominator is exactly 0
        denom = torch.where(active & nd.only6[i, :nj], 0.0, nd.dsum[i, :nj])
    else:
        sums = {t: tw.D[i, :nj] for t, tw in nd.types.items()}
        dead = None
        if 6 in sums:  # compound.f90:222 (no fission in this path)
            dead = active.clone()
            for k, sv in sums.items():
                if k != 6:
                    dead = dead & (sv == 0.0)
            if bool(dead.any()):
                sums[6] = torch.where(dead, 0.0, sums[6])
            else:
                dead = None
        denom = sum(sums.values())
    live = active & (pop != 0.0) & (denom != 0.0)
    feed = torch.where(live, (1.0 - dmulti) * pop / torch.where(live, denom, 1.0), 0.0)
    tw = nd.types[0]
    if tw.closed:
        dp = torch.zeros((int(tw.nrows[i]), NUMJ + 1, 2), dtype=DTYPE, device=dev)
    else:
        f = feed
        M = tw.M[:nj]
        V0 = torch.einsum("jil,jq->iql", M, f)
        V1 = torch.einsum("jil,jq->iql", M, f.flip(1))
        T = tw.T[i]
        TV = torch.einsum("nl,iql->niq", T[0], V0) + torch.einsum("nl,iql->niq", T[1], V1)
        dp = tw.sfac * tw.rho_c[i] * TV
        if tw.rho_d is not None:
            fd = torch.einsum("jpn,jp->n", tw.tot_dp[i, :nj], f)
            n_d = fd.shape[0]
            dp = dp.index_put((torch.arange(n_d, device=dev), tw.ird, tw.pd),
                              tw.sfac * tw.rho_d[i] * fd, accumulate=True)
        dp = dp[: int(tw.nrows[i])]
    mcontrib = dp.sum((1, 2))  # before the trapped flux is added, as in the reference
    trapped = active & (pop != 0.0) & (denom == 0.0)
    if bool(trapped.any()):
        nl = nd.nlast_mother
        nrow0 = int(tw.nrows[i])
        jdis2, parlev = nd.levels0
        mask = torch.zeros_like(dp)
        for nexout in range(min(nl, nrow0 - 1) + 1):
            mask[nexout, int(jdis2[nexout]) // 2, 0 if int(parlev[nexout]) == -1 else 1] = 1.0
        for J, p in torch.nonzero(trapped).tolist():
            share = pop[J, p] / (nl + 1.0)
            dp = dp + mask * share
    return dp, mcontrib


class _Widths:
    """What the photon feeding reads of one particle exit: its summed widths `D` only."""

    __slots__ = ("D",)

    def __init__(self, D):
        self.D = D


class CaptureDecay:
    """`decay_batch.NucleusDecay` of the compound nucleus's mother bins, holding only what
    `_photon_feeding` reads: every tensor of the photon exit, and the summed widths `D` of
    each particle exit (t = 1..6), which enter only the denominators.

    The particle exits' `D` is the reference's arithmetic on an l' axis cut after the last
    column with a non-zero (lmaxhf-capped) transmission. At capture energies the emitted
    particles are slow: the axis is 42 long but nothing above l' = 8 is open (deuteron, triton
    and helion are closed outright), and the full-length contraction was ~20 % of the sweep.
    The cut columns are exact zeros, so every product is unchanged; the sums over l' see
    fewer zero terms, which can move `D` by rounding (the gate is 1e-12 on the capture).

    TALYS: densprepare.f90:1 (densprepare), compound.f90:1 (compound)
    Test: SPEED3 / tests/hf/test_capture_fast_batch.py
    """

    def __init__(self, cas, st, sp, bins: list[int], device=None, trim_l: bool = True):
        from physics.hf.compound.continuum import _spin_l_mask
        from physics.hf.compound.decay_batch import PARN, PARZ, _interp_tl, _twopi
        from physics.hf.compound.dens_reference import _eendmax
        from physics.hf.compound.prepare import PARSPIN2

        self.device = device
        self.bins = list(bins)
        self.row = {b: i for i, b in enumerate(self.bins)}
        self.odd = sp.A % 2
        self.nlast_mother = sp.nlast_grid
        m = len(self.bins)
        exinc = np.array([float(sp.ex_mev[b]) for b in self.bins])
        dexinc = np.array([float(sp.dex_mev[b]) for b in self.bins])
        self.maxj = np.array([int(sp.maxj[b]) for b in self.bins], dtype=np.int64)
        nj = int(self.maxj.max()) + 1
        self.nj = nj
        nxm = [cas.nexmax(st, sp, b) for b in self.bins]
        eendmax = _eendmax(cas.Zt, cas.At, cas.enincmax)
        fnorm = cas.fisom(sp.zix, sp.nix)
        gstrength = cas.gamma_strength(sp.Z, sp.A - 1)
        diff = bool(getattr(gstrength, "differentiable", False))
        s_n = sp.sep_mev[1]
        ex0plus = exinc + 0.5 * dexinc
        ex0min = exinc - 0.5 * dexinc
        self.types: dict = {}
        for t in range(7):
            d = cas.spec(st, sp.zix + PARZ[t], sp.nix + PARN[t])
            nexmax = np.array([max(x[t], 0) for x in nxm], dtype=np.int64)
            n = int(nexmax.max()) + 1
            nrows = nexmax + 1
            ss = sp.sep_mev[t]
            rows = np.arange(n)
            inrow = rows[None, :] <= nexmax[:, None]  # (m, n)
            ex = np.asarray(d.ex_mev[:n], dtype=np.float64)[None, :]
            dexhalf = 0.5 * np.asarray(d.dex_mev[:n], dtype=np.float64)[None, :]
            nl = d.nlast
            ex1min = ex - dexhalf
            top = (rows[None, :] == nexmax[:, None]) & (t >= 1)
            ex1plus = np.where(top, (ex0plus - ss)[:, None], ex + dexhalf)
            exout_c = np.where(top, 0.5 * (ex1plus + ex1min), ex)
            emax = (ex0plus - ss)[:, None] - ex1min
            emin = (ex0min - ss)[:, None] - ex1plus
            eout_mid = 0.5 * (emin + emax)
            below = emin < 0.0
            half = 0.5 * (emax - emin)
            with np.errstate(divide="ignore", invalid="ignore"):
                rb_c = np.where(below, np.where(eout_mid > 0.0, 1.0 - 0.5 * (emin / half) ** 2,
                                                0.5 * (emax / half) ** 2), 1.0)
            eout_c = 0.5 * (np.where(below, 0.0, emin) + emax)
            exm = ex + ss
            part = (ex0min[:, None] < exm) & (exm <= ex0plus[:, None])
            with np.errstate(divide="ignore", invalid="ignore"):
                rb_d = np.where(part, (ex0plus[:, None] - exm) / dexinc[:, None], 1.0)
            eout_d = np.where(part, 0.5 * (ex0plus[:, None] + exm) - ss - ex,
                              (exinc - ss)[:, None] - ex)
            cont_row = rows[None, :] > nl
            eout = np.where(cont_row, eout_c, eout_d)
            rb = np.where(cont_row, rb_c, rb_d)
            exout = np.where(cont_row, exout_c, np.broadcast_to(ex, (m, n)))
            eout = np.where(inrow, eout, 0.0)
            if t == 0:
                L = cas.gammax + 1
                tg = torch.zeros((m, n, L, 2), dtype=DTYPE) if diff else np.zeros((m, n, L, 2))
                efs = exinc - s_n
                twopi = _twopi()
                fn1 = float(fnorm[1])
                batch = gstrength.batch
                egam = exinc[:, None] - exout
                pos = (egam > 0.0) & inrow
                if pos.any():
                    ii_, kk_ = np.nonzero(pos)
                    eg = egam[ii_, kk_]
                    efs_t = torch.as_tensor(efs[ii_], dtype=DTYPE)
                    for l in range(1, cas.gammax + 1):  # noqa: E741
                        fac = twopi * eg ** (2 * l + 1) * fn1
                        for irad in (0, 1):
                            v = batch(efs_t, eg, irad, l)
                            if diff:
                                tg[ii_, kk_, l, irad] = torch.as_tensor(fac, dtype=DTYPE) * v
                            else:
                                tg[ii_, kk_, l, irad] = fac * v
                lp = np.arange(L)
                if diff:
                    lpt = torch.as_tensor(lp)
                    Tn = torch.stack([tg[:, :, lpt, 1 - lpt % 2], tg[:, :, lpt, lpt % 2]], dim=1)
                else:
                    Tn = np.stack([tg[:, :, lp, 1 - lp % 2], tg[:, :, lp, lp % 2]], axis=1)
                lmaxhf = np.full((m, n), cas.gammax, dtype=np.int64)
                sfac = 1.0
            else:
                tjl, tl, lmax = cas.trans[t]
                eend = min(int(eendmax[t]), cas.rg.maxen)
                tlm, lm = _interp_tl(eout, cas.rg.egrid, cas.rg.ebegin[t], eend, cas.rg.maxen,
                                     tl, lmax, float(fnorm[t + 1]), cas.transeps)
                L = tl.shape[1]
                lmaxhf = np.where(inrow, lm, 0)
                lp = np.arange(L)
                Tn = np.stack([np.where(lp % 2 == c, tlm, 0.0) for c in (0, 1)], axis=1)
                sfac = float(PARSPIN2[t] + 1)
            ii = np.nonzero(nexmax > 0)[0]
            lmaxhf[ii, nexmax[ii]] = lmaxhf[ii, nexmax[ii] - 1]
            if t == cas.k0:
                lmaxhf[:, 0] = st.lmaxinc
            lmask = np.arange(L)[None, None, None, :] <= lmaxhf[:, None, :, None]
            if isinstance(Tn, Tensor):
                Tn = torch.where(torch.as_tensor(lmask), Tn, 0.0)
            else:
                Tn = np.where(lmask, Tn, 0.0)
            if t >= 1 and trim_l:
                open_l = np.flatnonzero(Tn.any(axis=(0, 1, 2)))
                if open_l.size == 0:  # nothing open: every width of this exit is zero
                    self.types[t] = _Widths(torch.zeros((m, nj, 2), dtype=DTYPE, device=device))
                    continue
                L = int(open_l[-1]) + 1
                Tn = Tn[..., :L]
            maxj_d = np.asarray(d.maxj[:n], dtype=np.int64)
            keepj = (np.arange(NUMJ + 1)[None, :] <= maxj_d[:, None]) & (rows > nl)[:, None]
            rho = np.where(keepj[None, :, :, None],
                           rb[:, :, None, None] * np.asarray(d.rhogrid[:n], dtype=np.float64)[None],
                           0.0)
            discfactor = (min(max((d.ncum_nl - d.ntop) / (d.nlast - d.ntop), 0.5), 2.0)
                          if d.nlast > d.ntop else 1.0)
            nd = min(nl, n - 1) + 1
            for k in range(nd):
                ir = int(d.jdis[k])
                if 0 <= ir <= NUMJ:
                    pidx = 0 if int(d.parlev[k]) == -1 else 1
                    v = rb[:, k] * discfactor if k > d.ntop else rb[:, k]
                    rho[:, k, ir, pidx] = v
            rho = np.where(inrow[:, :, None, None], rho, 0.0)
            base = (self.odd + PARSPIN2[t]) % 2
            irs2 = 2 * np.arange(NUMJ + 1) + base
            valid_c = irs2[None, :] <= 2 * maxj_d[:, None]
            jdis2 = (2.0 * np.float32(np.asarray(d.jdis[:n]))).astype(np.int64)
            disc_row = rows <= nl
            rho_t = torch.as_tensor(rho, dtype=DTYPE, device=device)
            rho_t = torch.where(rho_t >= 1.0e-20, rho_t, 0.0)
            if nl == 0:
                rho_t[:, 0] = 0.0
            vc = torch.as_tensor(valid_c & ~disc_row[:, None], device=device)
            rho_c = torch.where(vc[None, :, :, None], rho_t, 0.0)
            T = torch.as_tensor(Tn, dtype=DTYPE, device=device)
            M = _spin_l_mask(self.odd, PARSPIN2[t], nj, L, device).to(DTYPE)
            R = torch.einsum("mnip,mcnl->mcipl", rho_c, T)
            MR = torch.einsum("jil,mcipl->mjcp", M, R)
            D = torch.stack([MR[..., 0, 0] + MR[..., 1, 1], MR[..., 1, 0] + MR[..., 0, 1]],
                            dim=-1) * sfac
            tw = SimpleNamespace(nrows=nrows, T=T, rho_c=rho_c, sfac=sfac, D=D, M=M,
                                 ird=None, pd=None, rho_d=None, tot_dp=None)
            ndd = min(nl, n - 1) + 1
            if ndd > 0:
                jd2 = torch.as_tensor(jdis2[:ndd], device=device)
                j2 = 2 * torch.arange(nj, device=device) + self.odd
                sp2 = PARSPIN2[t]
                lbeg = torch.div(((j2[:, None] - jd2[None, :]).abs() - sp2).abs(), 2,
                                 rounding_mode="floor")
                lend = torch.div(j2[:, None] + jd2[None, :] + sp2, 2, rounding_mode="floor")
                lpd = torch.arange(L, device=device)
                Md = ((lpd >= lbeg[..., None]) & (lpd <= lend[..., None])).to(DTYPE)
                tot_d = torch.einsum("jnl,mcnl->mjcn", Md, T[:, :, :ndd])
                ird = torch.div(jd2, 2, rounding_mode="floor")
                pd = torch.as_tensor((np.asarray(d.parlev[:ndd]) > 0).astype(np.int64),
                                     device=device)
                ok = (ird >= 0) & (ird <= NUMJ)
                irc = ird.clamp(0, NUMJ)
                ar = torch.arange(ndd, device=device)
                rho_d = torch.where(ok[None, :], rho_t[:, ar, irc, pd], 0.0)
                cmat = (torch.arange(2, device=device)[:, None] != pd[None, :]).to(torch.int64)
                tot_dp = torch.stack([tot_d[:, :, cmat[p], ar] for p in (0, 1)], dim=2)
                tw.D = tw.D + sfac * torch.einsum("mjpn,mn->mjp", tot_dp, rho_d)
                tw.ird, tw.pd, tw.rho_d, tw.tot_dp = irc, pd, rho_d, tot_dp
            if t >= 1:
                self.types[t] = _Widths(tw.D)
                continue
            tw.closed = not bool((tw.D != 0.0).any())
            self.types[t] = tw
            self.levels0 = (jdis2, np.asarray(d.parlev[:n]).astype(np.int64))
        # `_photon_feeding`'s denominators for every bin: sum over the types in order, and the
        # cells where only the alpha width can be non-zero (compound.f90:222's `dead` rule)
        self.dsum = sum(self.types[t].D for t in range(7))
        only6 = torch.ones_like(self.dsum, dtype=torch.bool)
        for t in range(6):
            only6 = only6 & (self.types[t].D == 0.0)
        self.only6 = only6


def _cascade_cn(nuc, photon_decay, popeps_mb: float, differentiable: bool):
    """`multiple_emission` for the compound nucleus alone (maxz = maxn = 0, where its only
    daughter is itself), without the exclusive-channel bookkeeping. Returns xspopnuc(0, 0):
    a float, or with `differentiable` the ground state plus isomers as a tensor.

    TALYS: multiple.f90:1 (multiple), cascade.f90:1 (cascade)
    Test: SPEED3 / tests/hf/test_capture_fast_batch.py
    """
    from physics.hf.emission.multiple import gamma_cascade

    if nuc.xspopnuc_mb < popeps_mb:
        return 0.0
    popeps_a = popeps_mb / max(5 * nuc.maxex, 1)
    smin = nuc.sep_mev.get(1, 0.0)
    for nex in range(nuc.maxex, 0, -1):
        exinc = float(nuc.ex_mev[nex])
        if nex <= nuc.nlast and exinc <= smin:
            if float(nuc.tau_s[nex]) == 0.0:
                gamma_cascade(nuc, nex)
            continue
        if float(nuc.xspopex_mb[nex]) < popeps_a:
            continue
        dp, sumip_all = photon_decay(nex)
        n = min(dp.shape[0], nuc.xspop_mb.shape[0])
        nuc.xspop_mb[:n] += dp[:n]
        sumip = sumip_all[:n]
        nuc.xspopex_mb[:n] += sumip
        tot = float(sumip.sum())
        nuc.xspopex_mb[nex] -= tot
        nuc.xspopnuc_mb += tot
    if differentiable:
        # multiple.f90:643-646 on the tensors: the ground state plus the isomers
        pop = nuc.xspopex_mb[0]
        for nex in range(1, nuc.nlast + 1):
            if float(nuc.tau_s[nex]) != 0.0:
                pop = pop + nuc.xspopex_mb[nex]
        return pop
    pop = float(nuc.xspopex_mb[0])
    for nex in range(1, nuc.nlast + 1):
        if float(nuc.tau_s[nex]) != 0.0:
            pop += float(nuc.xspopex_mb[nex])
    return pop


def capture_xs(tg, e_inc_mev: float, differentiable: bool = False, trim_l: bool = True):
    """`capture_fast.capture_xs`, with the compound nucleus's decay reduced to its photon exit
    (see the module docstring). Same domain; the same numbers to the bit with `trim_l=False`,
    to rounding with the default (`CaptureDecay`).

    TALYS: comptarget.f90:1 (comptarget), multiple.f90:1 (multiple) for (Zcomp, Ncomp) = (0, 0)
    Test: SPEED3 / tests/hf/test_capture_fast_batch.py
    """
    from physics.hf import capture_fast as CF
    from physics.hf.compound.chain import compound_inputs
    from physics.hf.compound.target import compound_target_inputs
    from physics.hf.emission.feed_reference import etotal_of

    cas = tg.cas
    if not (cas.batched and not cas.flagfullhf):
        return CF.capture_xs(tg, e_inc_mev, differentiable)  # the per-bin decay path
    if not CF.in_domain(tg, e_inc_mev):
        return float("nan")
    e = CF._f32(e_inc_mev)
    k0 = cas.k0
    etot = etotal_of(tg.Z, tg.A, tg.enincmax, e, k0)
    inc = cas.incident(e)
    st = cas.new_energy(etot, lmaxinc=int(inc.lmax[0]))
    cas.propagate_exmax(st, 0, 0)
    binp = SimpleNamespace(e_inc_mev=e, k0=k0, targetspin2=tg.targetspin2,
                           target_parity=tg.target_parity, ltarget=0, popeps_mb=tg.popeps_mb,
                           flagpreeq=False)
    ci = compound_inputs(cas, st, binp, SimpleNamespace(flagfission=False), etot,
                         CF.ZERO_ADDENDS)
    if trim_l:
        ci = _trim_tjl(ci)
    pop = compound_target_inputs(ci).pop_mb[0, 0]
    n = cas.spec(st, 0, 0).maxex + 1
    xspop = pop[:n].clone()
    xd = xspop.detach()
    seed = {0: (xd.numpy(), xd.sum((-2, -1)).numpy(), float(xd.sum()))}
    nuclei = cas.populations(st, 0, 0, seed)
    cn = nuclei[(0, 0)]
    if differentiable:
        cn.xspop_mb = xspop.clone()
        cn.xspopex_mb = xspop.sum((-2, -1))
    if cn.skipcn:
        return CF.capture_xs(tg, e_inc_mev, differentiable)
    sp = cas.spec(st, 0, 0)
    popeps_a = tg.popeps_mb / max(5 * cn.maxex, 1)  # multiple.f90:467, as Cascade.decay

    cache: dict = {}

    def photon_decay(nex: int):
        nd = cas._nucleus_decay(st, sp, nex) if not trim_l else _capture_decay(cas, st, sp, nex,
                                                                                 cache)
        return _photon_feeding(nd, nex, cn.xspop_mb[nex], popeps_a, dmulti=0.0)

    return _cascade_cn(cn, photon_decay, tg.popeps_mb, differentiable)


def _trim_tjl(ci):
    """`ci` with every particle residual's `tjl` (Nex, L, 3) cut after its last column holding a
    non-zero transmission. The columns cut are exact zeros in every row: comptarget's open
    channels, their order and every product are unchanged (the incident-channel override pads
    the axis back to lmaxinc + 1 where it needs to).

    Test: SPEED3 / tests/hf/test_capture_fast_batch.py
    """
    import copy
    from dataclasses import replace

    res = {}
    for t, r in ci.residuals.items():
        tjl = r.tjl
        if t >= 1 and isinstance(tjl, np.ndarray) and tjl.ndim == 3 and tjl.shape[1] > 1:
            open_l = np.flatnonzero((tjl != 0.0).any(axis=(0, 2)))
            L = int(open_l[-1]) + 1 if open_l.size else 1
            if L < tjl.shape[1]:
                r = replace(r, tjl=tjl[:, :L])
        res[t] = r
    out = copy.copy(ci)
    out.residuals = res
    return out


def _capture_decay(cas, st, sp, nex: int, cache: dict) -> CaptureDecay:
    """`Cascade._nucleus_decay`'s chunking, building `CaptureDecay` instead."""
    cur = cache.get("cur")
    if cur is None or nex not in cur.row:
        smin = sp.sep_mev.get(1, 0.0)
        bins = [b for b in range(nex, 0, -1)
                if not (b <= sp.nlast_grid and float(sp.ex_mev[b]) <= smin)][: cas.DECAY_CHUNK]
        cur = CaptureDecay(cas, st, sp, bins)
        cache["cur"] = cur
    return cur


# ------------------------------------------------------------------------------ tables


def tables(tg, energies) -> dict:
    """The photon-strength-independent tables of target `tg` at `energies` [MeV]: the
    emission-grid transmissions and the incident channel of every in-domain energy.

    Test: SPEED3 / tests/hf/test_capture_fast_batch.py
    """
    from physics.hf import capture_fast as CF
    from physics.hf.compound.dens_reference import _transmission

    inc = {}
    for e in energies:
        if CF.in_domain(tg, float(e)):
            e32 = CF._f32(float(e))
            inc[e32] = tg.cas.incident(e32)
    tr = _transmission(tg.cas.Zt, tg.cas.At, tg.cas.enincmax) if inc else None
    return {"key": (tg.Z, tg.A, tg.enincmax), "transmission": tr, "incident": inc}


_TABLE_TRANSMISSION: dict = {}


def install_tables(tg, tab: dict) -> None:
    """Make target `tg` read `tab` (from `tables`) instead of solving: `cas.incident` answers
    from it for the energies it holds, and the module-level `_transmission` answers for this
    target. Anything not in the table is still computed.

    Test: SPEED3 / tests/hf/test_capture_fast_batch.py
    """
    from physics.hf.compound import dens_reference

    if tuple(tab["key"]) != (tg.Z, tg.A, tg.enincmax):
        raise ValueError(f"tables for {tab['key']} installed on {(tg.Z, tg.A, tg.enincmax)}")
    cas = tg.cas
    rows = tab["incident"]
    solve_one = cas.incident

    def incident(e_inc_mev: float):
        got = rows.get(e_inc_mev)
        return got if got is not None else solve_one(e_inc_mev)

    cas.incident = incident
    if tab["transmission"] is not None:
        _TABLE_TRANSMISSION[(cas.Zt, cas.At, cas.enincmax)] = tab["transmission"]
        if not getattr(dens_reference._transmission, "_speed3_tables", False):
            dens_reference._transmission = _with_tables(dens_reference._transmission)


def _with_tables(solve):
    def _transmission(Zt: int, At: int, enincmax_mev: float, *args, **kwargs) -> dict:
        # tables hold the default (un-overridden, numpy) solve only; DIFFPARAM's optical
        # overrides and the differentiable path always solve
        if not any(a is not None and a is not False for a in args) and not any(
                v is not None and v is not False for v in kwargs.values()):
            got = _TABLE_TRANSMISSION.get((Zt, At, enincmax_mev))
            if got is not None:
                return got
        return solve(Zt, At, enincmax_mev, *args, **kwargs)

    _transmission._speed3_tables = True
    _transmission.cache_clear = getattr(solve, "cache_clear", lambda: None)
    return _transmission


def forget_tables() -> None:
    """Drop installed transmissions (a worker moving on to other targets)."""
    _TABLE_TRANSMISSION.clear()
