"""The multiple-emission compound decay of every mother bin of one cascade nucleus, batched.

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

Task: SPEED0 (the speed work; no physics of its own). Acceptance test: SPEED0 golden
(`tests/hf/test_speed_golden.py`), A-mult through `engine.ChainedFull`.

TALYS routines this computes, in the arrangement described below:
    densprepare.f90:1 (densprepare)  -- primary = .false., for all mother bins at once
    compound.f90:1 (compound)        -- without width fluctuations, flagfullhf = .false.

`emission.feeding.Cascade.decay` used to run `densprepare` and `compound_decay` once per mother
bin, each a few hundred small tensor/array operations; at 18 MeV a target has several hundred
populated bins and that per-operation overhead was most of the wall. Nothing in a bin's decay
*widths* depends on its population, so this module builds them for all bins of a nucleus in one
call (`NucleusDecay`), and a bin's decay then only divides its (J, parity) population by the
denominators and contracts it with the width tensors (`NucleusDecay.feeding`). The order in
which `multiple_emission` decays bins, and everything it does between bins, is untouched.

The contraction is the one `continuum._compound_decay_factored` documents: for a mother cell
(J, P), residual state (nexout, Ir, P') is reached through
`sum_l' [lbeg(J, Ir) <= l' <= lend(J, Ir)] [l' <= lmaxhf(nexout)] T_c(nexout, l')` with
c = |P - P'| / 2, and the first bracket depends only on (J, Ir, l'). Sums are reordered (all
terms non-negative), so results move by rounding only.

Not covered, and routed to the per-bin path by the caller: `flagfullhf`, fission in the cascade,
and a photon transmission that depends on the mother's J or parity (never built by densprepare).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import torch
from torch import Tensor

from physics.hf.compound.continuum import _spin_l_mask
from physics.hf.compound.prepare import NUMJ, PARSPIN2
from physics.hf.core.tensors import DTYPE

PARZ = (0, 0, 1, 1, 1, 2, 2)
PARN = (0, 1, 0, 1, 2, 1, 2)


@dataclass
class _TypeWidths:
    """One exit type, all mother bins: what `feeding` contracts with a population."""

    nrows: np.ndarray  # (m,) nexmax(type) + 1 per mother bin
    T: Tensor  # (m, 2, n, L): lmaxhf-capped transmission split by c = |P - P'| / 2
    rho_c: Tensor  # (m, n, Jx, 2): continuum rho0, masked as compound.f90 reads it
    sfac: float  # (2s + 1) for particles, 1 for photons
    D: Tensor  # (m, nj, 2): sum over residual states of rho0 * transmission per mother cell
    ird: Tensor | None = None  # (nd,) discrete levels: Ir
    pd: Tensor | None = None  # (nd,) discrete levels: parity index
    rho_d: Tensor | None = None  # (m, nd)
    tot_dp: Tensor | None = None  # (m, nj, 2, nd)
    M: Tensor | None = None  # (nj, Jx, L) float `_spin_l_mask`
    closed: bool = False  # every rho0 * T is zero: no width, no feeding, for every bin and cell


def _interp_tl(eout: np.ndarray, egrid: np.ndarray, ebegin: int, eend: int, maxen: int,
               tl: np.ndarray, lmax: np.ndarray, fn: float, transeps: float,
               ) -> tuple[np.ndarray, np.ndarray]:
    """densprepare.f90's pol2 interpolation of `Tl` to every (bin, row) Eout, and `lmax` there.
    (m, n, L) and (m, n); the same arithmetic as `prepare.densprepare`, over two axes.

    TALYS: densprepare.f90:1 (densprepare)
    Test: A-trans / SPEED0 golden
    """
    m, n = eout.shape
    L = tl.shape[1]
    if not ebegin < eend:
        zeros = (torch.zeros((m, n, L), dtype=DTYPE) if isinstance(tl, Tensor)
                 else np.zeros((m, n, L)))
        return zeros, np.zeros((m, n), dtype=np.int64)
    lo = float(egrid[ebegin])
    xs = np.asarray(egrid, dtype=np.float32)
    seg = xs[ebegin : eend + 1]
    x = eout.astype(np.float32)
    if bool(np.all(np.diff(seg) > 0)):
        jl = np.searchsorted(seg, x, side="right") - 1 + ebegin
        jl = np.where(x == xs[ebegin], ebegin, np.where(x == xs[eend], eend - 1, jl))
    else:  # pragma: no cover - the emission grid ascends strictly
        from physics.hf.core.grids import locate_scalar

        jl = np.array([[locate_scalar(egrid, ebegin, eend, float(e)) for e in row]
                       for row in eout], dtype=np.int64)
    nen = np.where(eout < lo, 0, jl).astype(np.int64)
    centred = (nen > ebegin + 1) | (nen >= maxen - 1)
    na = np.where(centred, nen - 1, nen)
    nb, nc = na + 1, na + 2
    ea, eb, ec = egrid[na], egrid[nb], egrid[nc]
    w1 = ((eout - eb) * (eout - ec) / ((ea - eb) * (ea - ec)))[..., None]
    w2 = ((eout - ea) * (eout - ec) / ((eb - ea) * (eb - ec)))[..., None]
    w3 = ((eout - ea) * (eout - eb) / ((ec - ea) * (ec - eb)))[..., None]
    lm = lmax[np.clip(nen, 0, maxen)]
    keep = np.arange(L)[None, None, :] <= lm[..., None]
    if isinstance(tl, Tensor):  # DIFFPARAM: the same pol2, on the optical parameters' graph
        w1, w2, w3 = (torch.as_tensor(w, dtype=DTYPE) for w in (w1, w2, w3))
        z = torch.zeros((), dtype=DTYPE)
        u = w1 * tl[na] + w2 * tl[nb] + w3 * tl[nc]
        u = torch.where(torch.as_tensor(keep), u, z)
        return torch.where(u < transeps, z, u) * fn, lm
    u = w1 * tl[na] + w2 * tl[nb] + w3 * tl[nc]
    u = np.where(keep, u, 0.0)
    return np.where(u < transeps, 0.0, u) * fn, lm


class NucleusDecay:
    """Decay widths of mother bins `bins` of cascade nucleus `sp`, for one incident energy.

    TALYS: densprepare.f90:1 (densprepare), compound.f90:1 (compound)
    Test: SPEED0 golden / E2E
    """

    def __init__(self, cas, st, sp, bins: list[int], device=None):
        from physics.hf.compound.dens_reference import _eendmax
        from physics.hf.compound.prepare import _discfactor

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
        fnorm = cas.fisom(sp.zix, sp.nix, st)
        gstrength = cas.gamma_strength(sp.Z, sp.A - 1)
        diff = bool(getattr(gstrength, "differentiable", False))
        s_n = sp.sep_mev[1]
        ex0plus = exinc + 0.5 * dexinc
        ex0min = exinc - 0.5 * dexinc
        self.types: dict[int, _TypeWidths] = {}
        self.daughter_rows: dict[int, tuple] = {}
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
            nl = d.nlast  # Nlast(Zix, Nix, 0), unclamped, as DensResidual carries it
            # _eout_and_rboundary_rows with a mother axis
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
            # rho0 (_rho0_rows), with the mother axis
            discfactor = _discfactor(d)  # a tensor under a DIFFPARAM level-density override
            maxj_d = np.asarray(d.maxj[:n], dtype=np.int64)
            keepj = (np.arange(NUMJ + 1)[None, :] <= maxj_d[:, None]) & (rows > nl)[:, None]
            df_t = discfactor if isinstance(discfactor, Tensor) else None
            grad_rho = isinstance(d.rhogrid, Tensor) or df_t is not None
            if grad_rho:
                # continuum rows on the graph, discrete cells (a level's Rboundary weight, a
                # grid quantity) as the constants they are -- `prepare._rho0_rows`'s split.
                cont = torch.where(
                    torch.as_tensor(keepj)[None, :, :, None],
                    torch.as_tensor(rb, dtype=DTYPE)[:, :, None, None]
                    * d.rhogrid[:n].to(DTYPE)[None],
                    torch.zeros((), dtype=DTYPE))
                rho = np.zeros(cont.shape, dtype=np.float64)
            elif df_t is not None:  # rhogrid plain but Ncum on the graph
                cont = torch.as_tensor(
                    np.where(keepj[None, :, :, None],
                             rb[:, :, None, None]
                             * np.asarray(d.rhogrid[:n], dtype=np.float64)[None], 0.0),
                    dtype=DTYPE)
                rho = np.zeros(cont.shape, dtype=np.float64)
            else:
                rho = np.where(keepj[None, :, :, None],
                               rb[:, :, None, None]
                               * np.asarray(d.rhogrid[:n], dtype=np.float64)[None],
                               0.0)
            nd = min(nl, n - 1) + 1
            scaled = np.zeros_like(rho) if df_t is not None else None
            for k in range(nd):
                ir = int(d.jdis[k])
                if 0 <= ir <= NUMJ:
                    pidx = 0 if int(d.parlev[k]) == -1 else 1
                    if k > d.ntop and df_t is not None:
                        scaled[:, k, ir, pidx] = rb[:, k]
                    else:
                        rho[:, k, ir, pidx] = (rb[:, k] * discfactor if k > d.ntop else rb[:, k])
            if grad_rho:
                rho = cont + torch.as_tensor(rho, dtype=DTYPE)
                if df_t is not None:
                    rho = rho + df_t * torch.as_tensor(scaled, dtype=DTYPE)
                rho = torch.where(torch.as_tensor(inrow)[:, :, None, None], rho,
                                  torch.zeros((), dtype=DTYPE))
            else:
                rho = np.where(inrow[:, :, None, None], rho, 0.0)
            # transmission and lmaxhf
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
                    # fstrength once per (l, irad) over every (bin, row); Efs is per bin
                    ii_, kk_ = np.nonzero(pos)
                    eg = egam[ii_, kk_]
                    efs_t = torch.as_tensor(efs[ii_], dtype=DTYPE)
                    for l in range(1, cas.gammax + 1):  # noqa: E741
                        fac = twopi * eg ** (2 * l + 1) * fn1  # numpy pow == Python's pow here
                        for irad in (0, 1):
                            v = batch(efs_t, eg, irad, l)
                            if diff:  # G0.3: keep the photon strength on the graph
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
                if isinstance(tlm, Tensor):
                    zt = torch.zeros((), dtype=DTYPE)
                    lpt = torch.as_tensor(lp)
                    Tn = torch.stack([torch.where(lpt % 2 == c, tlm, zt) for c in (0, 1)], dim=1)
                else:
                    Tn = np.stack([np.where(lp % 2 == c, tlm, 0.0) for c in (0, 1)], axis=1)
                sfac = float(PARSPIN2[t] + 1)
            # lmaxhf(nexmax) = lmaxhf(nexmax - 1); lmaxhf(0) of the projectile type = lmaxinc
            ii = np.nonzero(nexmax > 0)[0]
            lmaxhf[ii, nexmax[ii]] = lmaxhf[ii, nexmax[ii] - 1]
            if t == cas.k0:
                lmaxhf[:, 0] = st.lmaxinc
            lmask = np.arange(L)[None, None, None, :] <= lmaxhf[:, None, :, None]
            if isinstance(Tn, Tensor):
                Tn = torch.where(torch.as_tensor(lmask), Tn, 0.0)
            else:
                Tn = np.where(lmask, Tn, 0.0)
            # continuum's masks (_residual_spins, rho >= 1e-20, NL == 0)
            base = (self.odd + PARSPIN2[t]) % 2
            irs2 = 2 * np.arange(NUMJ + 1) + base
            valid_c = irs2[None, :] <= 2 * maxj_d[:, None]  # (n, Jx)
            jdis2 = (2.0 * np.float32(np.asarray(d.jdis[:n]))).astype(np.int64)
            disc_row = rows <= nl
            rho_t = torch.as_tensor(rho, dtype=DTYPE, device=device)
            rho_t = torch.where(rho_t >= 1.0e-20, rho_t, torch.zeros((), dtype=DTYPE,
                                                                    device=device))
            if nl == 0:
                # not in place: `rho_t` may be a graph tensor (DIFFPARAM)
                m0 = torch.ones(rho_t.shape[1], dtype=DTYPE, device=device)
                m0[0] = 0.0
                rho_t = rho_t * m0[None, :, None, None]
            vc = torch.as_tensor(valid_c & ~disc_row[:, None], device=device)
            rho_c = torch.where(vc[None, :, :, None], rho_t, 0.0)
            T = torch.as_tensor(Tn, dtype=DTYPE, device=device)
            M = _spin_l_mask(self.odd, PARSPIN2[t], nj, L, device).to(DTYPE)
            R = torch.einsum("mnip,mcnl->mcipl", rho_c, T)
            MR = torch.einsum("jil,mcipl->mjcp", M, R)
            D = torch.stack([MR[..., 0, 0] + MR[..., 1, 1], MR[..., 1, 0] + MR[..., 0, 1]],
                            dim=-1) * sfac
            tw = _TypeWidths(nrows=nrows, T=T, rho_c=rho_c, sfac=sfac, D=D, M=M)
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
                rho_d = torch.where(ok[None, :], rho_t[:, ar, irc, pd], 0.0)  # (m, nd)
                cmat = (torch.arange(2, device=device)[:, None] != pd[None, :]).to(torch.int64)
                tot_dp = torch.stack([tot_d[:, :, cmat[p], ar] for p in (0, 1)], dim=2)
                tw.D = tw.D + sfac * torch.einsum("mjpn,mn->mjp", tot_dp, rho_d)
                tw.ird, tw.pd, tw.rho_d, tw.tot_dp = irc, pd, rho_d, tot_dp
            # D is a sum of non-negative rho0 * T terms over exactly the (state, l') cells the
            # feeding reads, so D == 0 everywhere means every feeding term is zero too
            tw.closed = not bool((tw.D != 0.0).any())
            self.types[t] = tw
            if t == 0:
                self.levels0 = (jdis2, np.asarray(d.parlev[:n]).astype(np.int64))

    def feeding(self, nex: int, xspop_mother: Tensor, popeps_a: float, dmulti: float = 0.0):
        """`compound_decay` of mother bin `nex` given its current (J, parity) population.
        Returns (dpop, mcontrib, fisfeed, leftover) exactly as `continuum.ContinuumFeeding`
        carries them; `leftover` is compound.f90's iloop-1 trapped flux (:404-419).

        TALYS: compound.f90:1 (compound)
        Test: SPEED0 golden / E2E
        """
        dev = self.device
        i = self.row[nex]
        maxj = int(self.maxj[i])
        nj = maxj + 1
        # a copy: multiple_emission adds to this nucleus's populations in place while the
        # graph still needs this bin's (G0.3)
        pop = torch.as_tensor(xspop_mother, dtype=DTYPE, device=dev)[:nj].clone()  # (nj, 2)
        popeps_b = popeps_a / (5 * max(maxj, 1)) * 0.5
        active = pop >= popeps_b
        sums = {t: tw.D[i, :nj] for t, tw in self.types.items()}
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
        dpop, mcontrib = {}, {}
        for t, tw in self.types.items():
            if tw.closed:
                dp = torch.zeros((int(tw.nrows[i]), NUMJ + 1, 2), dtype=DTYPE, device=dev)
                dpop[t] = dp
                mcontrib[t] = torch.zeros(int(tw.nrows[i]), dtype=DTYPE, device=dev)
                continue
            f = feed if (t != 6 or dead is None) else torch.where(dead, 0.0, feed)
            M = tw.M[:nj]
            V0 = torch.einsum("jil,jq->iql", M, f)
            V1 = torch.einsum("jil,jq->iql", M, f.flip(1))
            T = tw.T[i]
            TV = torch.einsum("nl,iql->niq", T[0], V0) + torch.einsum("nl,iql->niq", T[1], V1)
            dp = tw.sfac * tw.rho_c[i] * TV
            if tw.rho_d is not None:
                fd = torch.einsum("jpn,jp->n", tw.tot_dp[i, :nj], f)
                nd = fd.shape[0]
                dp = dp.index_put((torch.arange(nd, device=dev), tw.ird, tw.pd),
                                  tw.sfac * tw.rho_d[i] * fd, accumulate=True)
            dp = dp[: int(tw.nrows[i])]
            dpop[t] = dp
            mcontrib[t] = dp.sum((1, 2))
        trapped = active & (pop != 0.0) & (denom == 0.0)
        leftover = 0.0
        if bool(trapped.any()):
            # compound.f90:404-419: spread over the compound nucleus's own discrete levels.
            # iloop 1's, so not part of `mcontrib` (iloop 2's): returned separately and applied by
            # `multiple_emission` where compound.f90 applies it.
            leftover = float(pop[trapped].sum())
            nl = self.nlast_mother
            r0 = self.types[0]
            nrow0 = int(r0.nrows[i])
            jdis2, parlev = self.levels0
            mask = torch.zeros_like(dpop[0])
            for nexout in range(min(nl, nrow0 - 1) + 1):
                mask[nexout, int(jdis2[nexout]) // 2, 0 if int(parlev[nexout]) == -1 else 1] = 1.0
            for J, p in torch.nonzero(trapped).tolist():
                share = pop[J, p] / (nl + 1.0)
                dpop[0] = dpop[0] + mask * share
        return dpop, mcontrib, 0.0, leftover


def _twopi() -> float:
    from physics.hf.core.constants import talys_constants

    return float(talys_constants()["twopi"])
