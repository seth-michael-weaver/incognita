"""NATIVEX: `compound.decay_fast.NucleusWidths`' arrays for the compiled walk, built in C.

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

Task: NATIVEX (the speed work; no physics of its own). Acceptance test: `tests/hf/test_nativex.py`
(every array against `NucleusWidths`) and the G-NATIVEX closeness gate.

TALYS routines this computes (`native/nativex.c`'s `nx_widths`, arranged as `decay_fast` arranges
them):
    densprepare.f90:1 (densprepare)  -- primary = .false.: Eout, Rboundary, rho0, the Tl pol2
                                        interpolation and the lmaxhf cap, for all mother bins
    compound.f90:1 (compound)        -- the spin-l' selection, the denominators, the discrete rows

`NucleusWidths.__init__` was a quarter of a spherical target's `multiple_emission` on the Mac:
~80 numpy and torch calls per exit type per cascade nucleus per energy on small arrays. The photon
strength functions stay where they were (`psf_fast` / `fstrength`, the model code); everything after
them is one C call. The arrays are the ones `emission.multiple_native`'s walk reads, with the same
values to rounding (sums in loop order). `NativeWidths` carries no `feeding`: it serves the
compiled walk only, so `Cascade.fast_widths` keeps it apart from `decay`'s own cache.
"""

from __future__ import annotations

import numpy as np
import torch

from physics.hf.compound.decay_batch import PARN, PARZ, _twopi
from physics.hf.compound.decay_fast import _tl_stack, jd2_all, nexmax_rows
from physics.hf.compound.prepare import NUMJ, PARSPIN2
from physics.hf.core.tensors import DTYPE
from physics.hf.native import nativex

_I64 = np.int64


class _Exit:
    __slots__ = ("t", "closed", "nrows", "sfac", "rho_c", "Tn", "lb", "le", "nd", "tot0", "tot1",
                 "rho_d", "ird", "pd", "D", "jx")


class NativeWidths:
    """The decay widths of mother bins `bins` of cascade nucleus `sp` at one incident energy, as
    `NucleusWidths` holds them, for `emission.multiple_native`. Raises `NotImplementedError` for
    inputs the kernel does not take (a tensor on the way, a Tl shape per particle).

    TALYS: densprepare.f90:1 (densprepare), compound.f90:1 (compound)
    Test: tests/hf/test_nativex.py
    """

    def __init__(self, cas, st, sp, bins: list[int], fissions: bool = True):
        from physics.hf.compound.dens_reference import _eendmax
        from physics.hf.compound.prepare import _discfactor

        so = nativex.lib()
        if so is None:
            raise NotImplementedError("no nativex build")
        self.bins = list(bins)
        self.row = {b: i for i, b in enumerate(self.bins)}
        self.odd = sp.A % 2
        self.nlast_mother = sp.nlast_grid
        barr = np.asarray(self.bins, dtype=_I64)
        m = barr.size
        exinc = np.ascontiguousarray(np.asarray(sp.ex_mev, dtype=np.float64)[barr])
        dexinc = np.ascontiguousarray(np.asarray(sp.dex_mev, dtype=np.float64)[barr])
        self.maxj = np.asarray(sp.maxj, dtype=_I64)[barr]
        nj = self.nj = int(self.maxj.max()) + 1
        nxm = np.ascontiguousarray(nexmax_rows(cas, st, sp, barr), dtype=_I64)
        from physics.hf.core.grids import binquad_mode, binquad_params, binquad_sub

        self.sub = binquad_sub(cas.options)
        if self.sub > 1:
            # BINQUAD sub-points: S widths rows per mother bin at its Gauss-Legendre nodes, each a
            # sub-bin of width dEx / S (nx_walk decays the bin's population on each with weight w_q / 2)
            from physics.hf.compound.prepare import _BQ_X

            from physics.hf.compound.prepare import _BQ_W

            S = self.sub
            xi = np.asarray(_BQ_X[S], dtype=np.float64)
            # each node's box (TALYS's partial-overlap geometry) is its weight's share of the bin, clipped
            # so it never reaches past the bin edges (a box over S_n would emit from below threshold)
            half = np.minimum(0.25 * np.asarray(_BQ_W[S]), 0.5 * (1.0 - np.abs(xi)))
            # one point where the branching cannot vary inside the bin: a discrete level, or a bin wholly
            # below every particle separation energy of a nucleus that does not fission (photons only)
            smin_all = min(float(sp.sep_mev[t]) for t in range(1, 7))
            cnt = np.where((barr <= int(sp.nlast_grid)) | ((exinc + 0.5 * dexinc <= smin_all) & (not fissions)), 1, S)
            # BINQUAD2 (`binquadk` bitmask): the bin's widths jump/kink at knots (own S: an exit opens; chain
            # S_x + S_y': the daughter's own exit opens; fission barrier tops), so S Gauss points per smooth
            # piece [knot, knot], each piece's points sharing its fraction of the (uniform) population
            from physics.hf.core.grids import binquad_knots

            kmask = binquad_knots(cas.options)
            knots = []
            if kmask & 1:
                knots += [float(sp.sep_mev[t]) for t in range(1, 7)]
            if kmask & 2:
                knots += list(cas._chain_knots(sp.zix, sp.nix))
            if kmask & 4 and fissions:
                knots += list(cas._fis_knots(sp.zix, sp.nix))
            knots = np.unique(np.asarray([k for k in knots if np.isfinite(k) and k > 0.0], dtype=np.float64))
            ex_r, dx_r, w_r = [], [], []
            for b in range(m):
                if cnt[b] == 1:
                    ex_r.append([exinc[b]]); dx_r.append([dexinc[b]]); w_r.append([1.0])
                    continue
                x0, x1 = exinc[b] - 0.5 * dexinc[b], exinc[b] + 0.5 * dexinc[b]
                cut = knots[(knots > x0 + 1e-6 * dexinc[b]) & (knots < x1 - 1e-6 * dexinc[b])] if knots.size else knots
                if cut.size == 0:
                    ex_r.append(exinc[b] + 0.5 * dexinc[b] * xi); dx_r.append(2.0 * dexinc[b] * half)
                    w_r.append(0.5 * np.asarray(_BQ_W[S]))
                    continue
                e = np.concatenate([[x0], cut, [x1]])
                ee, dd, ww = [], [], []
                for a, c in zip(e[:-1], e[1:]):
                    ee.append(0.5 * (a + c) + 0.5 * (c - a) * xi); dd.append(2.0 * (c - a) * half)
                    ww.append((c - a) / dexinc[b] * 0.5 * np.asarray(_BQ_W[S]))
                ex_r.append(np.concatenate(ee)); dx_r.append(np.concatenate(dd)); w_r.append(np.concatenate(ww))
                cnt[b] = len(ex_r[-1])
            off = np.concatenate([[0], np.cumsum(cnt)[:-1]]).astype(_I64)
            self.sub_w = np.ascontiguousarray(np.concatenate(w_r), dtype=np.float64)
            exinc = np.ascontiguousarray(np.concatenate(ex_r))
            dexinc = np.ascontiguousarray(np.concatenate(dx_r))
            nxm = np.ascontiguousarray(np.repeat(nxm, cnt, axis=0))
            self.maxj = np.repeat(self.maxj, cnt)
            m = int(cnt.sum())
            self.sub_ex, self.sub_dex = exinc, dexinc
            self.sub_cnt, self.sub_off = np.ascontiguousarray(cnt, dtype=_I64), off

        if binquad_mode(cas.options) and binquad_params(cas.options)[1] <= -2.0:
            # BINQUAD centroid: each mother bin decays at its population centroid (as engine_decay.c)
            from physics.hf.compound.prepare import binquad_centroid, binquad_slope

            rh = np.asarray(sp.rhogrid, dtype=np.float64)
            exa, dxa = np.asarray(sp.ex_mev, dtype=np.float64), np.asarray(sp.dex_mev, dtype=np.float64)
            nr = min(int(sp.maxex) + 1, rh.shape[0])
            for i, k in enumerate(self.bins):
                if k > int(sp.nlast):
                    exinc[i] = exa[k] + binquad_centroid(binquad_slope(rh, exa, dxa, int(sp.nlast), nr, k), dxa[k])
        fnorm = cas.fisom(sp.zix, sp.nix, st)
        if self.sub > 1 and (sp.zix, sp.nix) == (0, 0) and int(getattr(cas.options, "binquadc", 0) or 0) == 1:
            self._cn_population_weights(cas, sp, fnorm, float(st.exmax0[0, 0]))
        daughters = [cas.spec(st, sp.zix + PARZ[t], sp.nix + PARN[t]) for t in range(7)]
        nexmax = np.maximum(nxm, 0)
        ns = [int(nexmax[:, t].max()) + 1 for t in range(7)]
        if self.sub > 1 and int(getattr(cas.options, "binquadg", 0) or 0) == 1:
            # BINQUAD binquadg 1: the photon exit at the bin centre for every sub-point (Gamma_gamma is smooth)
            exb = np.asarray(sp.ex_mev, dtype=np.float64)[barr]
            tgb = self._photon_q(cas, sp, daughters[0], exb, nexmax[self.sub_off, 0], ns[0], fnorm)
            tg = np.ascontiguousarray(np.repeat(tgb, self.sub_cnt, axis=0))
        else:
            tg = self._photon_q(cas, sp, daughters[0], exinc, nexmax[:, 0], ns[0], fnorm)
        tls = [cas.trans_of(sp.zix, sp.nix)[t] for t in range(1, 7)]  # SLFIRST: per emitting nucleus
        Ltl = tls[0][1].shape[1]
        if any(isinstance(x[1], torch.Tensor) or x[1].shape[1] != Ltl for x in tls):
            raise NotImplementedError("one numpy Tl shape for every particle")
        TL, LM, head0 = _tl_stack(cas, tls)
        from physics.hf.compound import tlog

        if isinstance(cas.trans, dict) and "tlogref" in cas.trans:
            raise NotImplementedError("TLOGREF (G0 reference) is numpy-only")  # -> decay_fast numpy widths
        tlog.native_arm(cas.trans)  # LOGTINT (default OFF): log-T Lagrange of charged T in nx_widths
        rg = cas.rg
        eendmax = _eendmax(cas.Zt, cas.At, cas.enincmax)
        egrid = np.ascontiguousarray(np.asarray(rg.egrid, dtype=np.float64))
        keep = []
        ip = np.zeros(16 + 8 * 7, dtype=_I64)
        pp = np.zeros(20 + 8 * 7, dtype=np.uint64)
        dp = np.zeros(8)
        L0 = cas.gammax + 1

        def put(slot, a):
            keep.append(a)
            pp[slot] = nativex.ptr(a)
            return a

        put(0, exinc)
        put(1, dexinc)
        put(2, nxm)
        put(3, np.array([sp.sep_mev[t] for t in range(7)], dtype=np.float64))
        put(4, np.ascontiguousarray(TL, dtype=np.float64))
        put(5, np.ascontiguousarray(LM, dtype=_I64))
        put(6, np.ascontiguousarray(head0, dtype=_I64))
        put(7, egrid)
        put(8, np.ascontiguousarray(egrid[: rg.maxen + 1], dtype=np.float32))
        put(9, np.array([int(rg.ebegin[t]) for t in range(1, 7)], dtype=_I64))
        put(10, np.array([min(int(eendmax[t]), rg.maxen) for t in range(1, 7)], dtype=_I64))
        put(11, np.array([float(fnorm[t + 1]) for t in range(1, 7)], dtype=np.float64))
        put(12, tg)
        ip[:10] = (m, nj, self.odd, cas.k0, st.lmaxinc, rg.maxen, Ltl, TL.shape[1], egrid.size, L0)
        dp[0] = cas.transeps
        outp = np.zeros(12 * 7, dtype=np.uint64)
        bufs = []
        for t, d in enumerate(daughters):
            n = ns[t]
            nl = int(d.nlast)
            ndd = max(min(nl, n - 1) + 1, 0)
            disc = _discfactor(d)
            if isinstance(disc, torch.Tensor):
                raise NotImplementedError("a level-density parameter on a graph")
            rhog = np.asarray(d.rhogrid, dtype=np.float64)
            if rhog.shape[1] != NUMJ + 1 or rhog.shape[0] < n:
                raise NotImplementedError("rhogrid shape")
            jd = np.asarray(d.jdis[:ndd])
            ip[16 + 8 * t: 16 + 8 * t + 6] = (n, nl, int(d.ntop), rhog.shape[0], ndd, PARSPIN2[t])
            q = 20 + 8 * t
            put(q, np.ascontiguousarray(np.asarray(d.ex_mev[:n], dtype=np.float64)))
            put(q + 1, np.ascontiguousarray(np.asarray(d.dex_mev[:n], dtype=np.float64)))
            put(q + 2, np.ascontiguousarray(np.asarray(d.maxj[:n], dtype=_I64)))
            put(q + 3, np.ascontiguousarray((2.0 * np.float32(jd)).astype(_I64)))
            put(q + 4, np.ascontiguousarray(jd.astype(_I64)))
            put(q + 5, np.ascontiguousarray(np.asarray(d.parlev[:ndd]).astype(_I64)))
            put(q + 6, np.ascontiguousarray(rhog))
            dp[1 + t] = float(disc)
            Lb = L0 if t == 0 else Ltl
            b = dict(rho_c=np.empty(m * n * (NUMJ + 1) * 2), T=np.empty(m * 2 * n * Lb),
                     tot0=np.empty(m * nj * max(ndd, 1)), tot1=np.empty(m * nj * max(ndd, 1)),
                     rho_d=np.empty(m * max(ndd, 1)), ird=np.empty(max(ndd, 1), dtype=_I64),
                     pd=np.empty(max(ndd, 1), dtype=_I64), D=np.empty(m * nj * 2),
                     nrows=np.empty(m, dtype=_I64), lb=np.empty(nj * (NUMJ + 1), dtype=_I64),
                     le=np.empty(nj * (NUMJ + 1), dtype=_I64))
            bufs.append(b)
            for k, name in enumerate(("rho_c", "T", "tot0", "tot1", "rho_d", "ird", "pd", "D",
                                      "nrows", "lb", "le")):
                outp[12 * t + k] = nativex.ptr(b[name])
        meta = np.zeros(8 * 7, dtype=_I64)
        from physics.hf.core.grids import binquad_sync

        binquad_sync(cas.options)
        so.nx_widths(nativex.ptr(ip), nativex.ptr(pp), nativex.ptr(dp), nativex.ptr(outp),
                     nativex.ptr(meta))
        self.exits: list[_Exit] = []
        for t in range(7):
            b, n = bufs[t], ns[t]
            e = _Exit()
            e.t = t
            e.sfac = 1.0 if t == 0 else float(PARSPIN2[t] + 1)
            e.nrows = b["nrows"]
            closed, jx, Lc, nd = (int(v) for v in meta[8 * t: 8 * t + 4])
            e.closed, e.jx, e.nd = bool(closed), jx, nd
            if closed:
                e.D = None
                self.exits.append(e)
                continue
            e.rho_c = b["rho_c"][: m * n * jx * 2].reshape(m, n, jx, 2)
            e.Tn = (b["T"][: m * n * Lc].reshape(m, n, Lc) if t >= 1
                    else b["T"][: m * 2 * n * Lc].reshape(m, 2, n, Lc))
            e.lb = b["lb"][: nj * jx]
            e.le = b["le"][: nj * jx]
            e.D = b["D"].reshape(m, nj, 2)
            if nd:
                e.tot0 = b["tot0"][: m * nj * nd].reshape(m, nj, nd)
                e.tot1 = b["tot1"][: m * nj * nd].reshape(m, nj, nd)
                e.rho_d = b["rho_d"][: m * nd].reshape(m, nd)
                e.ird = b["ird"][:nd]
                e.pd = b["pd"][:nd]
            self.exits.append(e)
        self.dsum6 = np.zeros((m, nj, 2))
        self.zero6 = np.ones((m, nj, 2), dtype=bool)
        for e in self.exits[:6]:
            if e.D is not None:
                self.dsum6 = self.dsum6 + e.D
                self.zero6 &= e.D == 0.0
        d0 = daughters[0]
        self.levels0 = (jd2_all(d0, ns[0]), np.asarray(d0.parlev[: ns[0]]).astype(_I64))

    def _cn_population_weights(self, cas, sp, fnorm, etot: float) -> None:
        """BINQUAD2 (`binquadc 1`): the compound nucleus's continuum is fed only by primary photons from
        Etotal, so inside a bin its population goes as rho(y) Tgamma(Etotal - y) (steep near Etotal, where
        Egamma -> 0), not flat: each sub-point's share = geometric weight x rho tilt x the summed primary
        photon transmission at its energy, renormalised per bin (bin totals unchanged)."""
        from physics.hf.compound.prepare import binquad_slope

        ex = np.asarray(sp.ex_mev, dtype=np.float64)  # etot: Etotal (exgrid's Ex(maxex + 1) of the CN)
        if not etot > 0.0:
            return
        y = np.asarray(self.sub_ex, dtype=np.float64)
        N = y.size
        tg = self._photon(cas, sp, sp, np.array([etot]), np.array([N - 1], dtype=_I64), N, fnorm, ex0=y)
        tsum = tg[0].sum(axis=(1, 2))
        rhog = np.asarray(sp.rhogrid, dtype=np.float64)
        dexf = np.asarray(sp.dex_mev, dtype=np.float64)
        nr = min(int(sp.maxex) + 1, rhog.shape[0], ex.size, dexf.size)
        w = np.asarray(self.sub_w, dtype=np.float64).copy()
        for i, b in enumerate(self.bins):
            c, o = int(self.sub_cnt[i]), int(self.sub_off[i])
            if c <= 1:
                continue
            beta = binquad_slope(rhog, ex, dexf, int(sp.nlast), nr, int(b))
            sh = w[o:o + c] * np.exp(beta * (y[o:o + c] - ex[b])) * tsum[o:o + c]
            tot = sh.sum()
            if tot > 0.0 and np.isfinite(tot):
                w[o:o + c] = sh / tot
        self.sub_w = np.ascontiguousarray(w)

    def _photon_q(self, cas, sp, d0, exinc: np.ndarray, nexmax0: np.ndarray, n: int, fnorm):
        """`_photon`, or under BINQUAD2 (`binquadp Q`) its average over each continuum row's bin
        [Ex - dEx/2, Ex + dEx/2] at Q Gauss-Legendre nodes weighted by the row's level-density tilt
        (engine_decay.c's primary photon twin); discrete rows keep their point."""
        from physics.hf.core.grids import binquad_photon

        pq = binquad_photon(cas.options)
        if pq <= 0:
            return self._photon(cas, sp, d0, exinc, nexmax0, n, fnorm)
        from physics.hf.compound.prepare import _BQ_W, _BQ_X, binquad_slope

        ex0 = np.asarray(d0.ex_mev[:n], dtype=np.float64)
        dex0 = np.asarray(d0.dex_mev[:n], dtype=np.float64)
        nl = int(d0.nlast)
        rhog = np.asarray(d0.rhogrid, dtype=np.float64)
        exf = np.asarray(d0.ex_mev, dtype=np.float64)
        dexf = np.asarray(d0.dex_mev, dtype=np.float64)
        nr = min(int(d0.maxex) + 1, rhog.shape[0], exf.size, dexf.size)
        rows = np.arange(max(nl + 1, 0), n)
        rows = rows[dex0[rows] > 0.0]
        if rows.size == 0:
            return self._photon(cas, sp, d0, exinc, nexmax0, n, fnorm)
        beta = np.array([binquad_slope(rhog, exf, dexf, nl, nr, int(k)) for k in rows])
        acc, wsum = None, np.zeros(rows.size)
        for x, w in zip(_BQ_X[pq], _BQ_W[pq]):
            exq = ex0.copy()
            exq[rows] = ex0[rows] + 0.5 * dex0[rows] * x
            wk = w * np.exp(beta * 0.5 * dex0[rows] * x)
            wsum += wk
            tq = self._photon(cas, sp, d0, exinc, nexmax0, n, fnorm, exq)
            if acc is None:
                acc = tq.copy()  # discrete rows: the point (identical at every node)
                acc[:, rows] = 0.0
            acc[:, rows] += wk[None, :, None, None] * tq[:, rows]
        acc[:, rows] /= wsum[None, :, None, None]
        return np.ascontiguousarray(acc)

    def _photon(self, cas, sp, d0, exinc: np.ndarray, nexmax0: np.ndarray, n: int, fnorm, ex0=None):
        """`NucleusWidths._photon`'s Tgam[b, row, l', irad] before the l' split and cap (`ex0`: the
        rows' energies, default the bin centres)."""
        m = exinc.size
        L = cas.gammax + 1
        tg = np.zeros((m, n, L, 2))
        efs = exinc - sp.sep_mev[1]
        fn1 = float(fnorm[1])
        ex0 = np.asarray(d0.ex_mev[:n], dtype=np.float64) if ex0 is None else np.asarray(ex0, dtype=np.float64)
        inrow = np.arange(n)[None, :] <= nexmax0[:, None]
        egam = exinc[:, None] - ex0[None, :]
        pos = (egam > 0.0) & inrow
        if pos.any():
            from physics.hf.compound.psf_fast import fstrength_np

            twopi = _twopi()
            gstrength = cas.gamma_strength(sp.Z, sp.A - 1)
            gp = cas.gamma_params(sp.Z, sp.A - 1)  # PARAMWIRE: the run's parameter set
            if gp is not None:
                # NATIVEX2: the strength function and the rows in C (compound/psf_nx2.py)
                from physics.hf.compound.psf_nx2 import photon_rows

                got = photon_rows(gp, cas.gammax, exinc, ex0, nexmax0, n, float(sp.sep_mev[1]),
                                  twopi, fn1)
                if got is not None:
                    return got
            ii_, kk_ = np.nonzero(pos)
            eg = egam[ii_, kk_]
            efs_p = efs[ii_]
            efs_t = None
            for l in range(1, cas.gammax + 1):  # noqa: E741
                fac = twopi * eg ** (2 * l + 1) * fn1
                for irad in (0, 1):
                    v = None if gp is None else fstrength_np(gp, efs_p, eg, irad, l)
                    if v is None:
                        if efs_t is None:
                            efs_t = torch.as_tensor(efs_p, dtype=DTYPE)
                        v = gstrength.batch(efs_t, eg, irad, l)
                    tg[ii_, kk_, l, irad] = fac * v
        return np.ascontiguousarray(tg)
