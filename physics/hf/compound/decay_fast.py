"""The multiple-emission compound decay of one cascade nucleus, whole-nucleus and numpy.

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

Task: SPEEDD (the speed wave; no physics of its own). Acceptance test: the speed-wave golden
(`features/hf_speed_golden_speedwave/`, `tests/hf/test_speed_golden.py`) and
`tests/hf/test_decay_fast.py`, which holds it to `compound.decay_batch.NucleusDecay`.

TALYS routines this computes, in the arrangement described below:
    densprepare.f90:1 (densprepare)  -- primary = .false., for all mother bins at once
    compound.f90:1 (compound)        -- without width fluctuations, flagfullhf = .false.

`decay_batch.NucleusDecay` already builds a nucleus's decay widths for 24 mother bins at a time
and contracts one bin's (J, parity) population with them per call. What was left was per-call
overhead: ~60 torch operations per bin (seven exit types, most of them closed) and a width build
over (bins, rows, numJ + 1, 2, 42 l') arrays that are zero past the few spins and l' a nucleus
actually reaches. `NucleusWidths` is the same calculation with three changes, none of them
physics:

* **numpy, on axes cut to what is open.** The residual-spin axis stops after the last spin any
  row of the daughter reaches, the l' axis after the last l' any bin's `lmaxhf` admits, and a
  closed exit type (every rho0 * T zero) is recorded as closed and never contracted. Only zeros
  are dropped, so sums move by rounding only.
* **the whole nucleus in one build**, not in chunks of 24.
* **particle exits are contracted lazily, all bins at once.** Only the photon exit feeds the
  nucleus being decayed (its own lower bins, which `multiple_emission` reads while it walks
  down); every particle exit feeds a nucleus that is decayed later. So `feeding` contracts the
  photon exit now and keeps the bin's feed vector; the particle exits of every pending bin are
  contracted in one batched call the first time any of them is read. `multiple_emission`
  applies particle feeding after it has walked the nucleus, in bin order, which is the same
  sequence of additions on every daughter element.

This path takes numpy populations and returns numpy arrays; it is not on any graph. A
differentiable run (`Cascade.diff_params`, photon-strength overrides, a population that requires
grad), fission in the cascade and `flagfullhf` stay on `decay_batch`'s path (`Cascade.decay`).
"""

from __future__ import annotations

from collections.abc import Mapping
from functools import lru_cache

import numpy as np
import torch
from torch import Tensor

from physics.hf.compound import decay_native as dn
from physics.hf.compound.continuum import _spin_l_mask
from physics.hf.compound.decay_batch import PARN, PARZ, _interp_tl, _twopi
from physics.hf.compound.prepare import NUMJ, PARSPIN2
from physics.hf.core.tensors import DTYPE


@lru_cache(maxsize=256)
def _mask(odd: int, parspin2: int, nj: int, jx: int, L: int) -> np.ndarray:
    """`continuum._spin_l_mask` as float64 numpy, cut to (nj, jx, L)."""
    return _spin_l_mask(odd, parspin2, nj, max(L, 1)).to(DTYPE)[:, :jx, :L].numpy().copy()


def _tl_stack(cas, tls):
    """The six particles' Tl and lmax tables stacked, and whether Tl's first three grid nodes
    are all zero, once per Cascade (`flagompall` false: one set for the run)."""
    got = cas.__dict__.get("_decay_fast_tl")
    if got is None or got[0] is not tls[0][1]:
        TL = np.stack([np.asarray(x_[1], dtype=np.float64) for x_ in tls])
        LM = np.stack([np.asarray(x_[2]) for x_ in tls])
        head0 = ~TL[:, :3].reshape(6, -1).any(axis=1)
        got = cas.__dict__["_decay_fast_tl"] = (tls[0][1], TL, LM, head0)
    return got[1], got[2], got[3]


def _rows(idx):
    """A slice when the row indices are consecutive (a view, not a copy)."""
    idx = np.asarray(idx)
    if idx.size and int(idx[-1]) - int(idx[0]) == idx.size - 1 and \
            (idx.size == 1 or bool(np.all(np.diff(idx) == 1))):
        return slice(int(idx[0]), int(idx[-1]) + 1)
    return idx


@lru_cache(maxsize=256)
def _mask_c(odd_a: int, parspin2: int, nj: int, jx: int, L: int) -> np.ndarray:
    """(2, nj, Ir, l') spin-l' mask split by the parity of l' (c = l' mod 2 for a particle)."""
    M = _mask(odd_a, parspin2, nj, jx, L)
    odd = (np.arange(L) % 2 == 1)
    return np.stack([np.where(odd, 0.0, M), np.where(odd, M, 0.0)])


@lru_cache(maxsize=1024)
def _mask_d(odd: int, parspin2: int, nj: int, jd2: bytes, L: int) -> Tensor:
    """(nj, k, l') lbeg <= l' <= lend for mother J (J2 = 2J + odd) to discrete level spins jd2."""
    j2 = 2 * np.arange(nj) + odd
    jd = np.frombuffer(jd2, dtype=np.int64)
    lbeg = np.abs(np.abs(j2[:, None] - jd[None, :]) - parspin2) // 2
    lend = (j2[:, None] + jd[None, :] + parspin2) // 2
    lpd = np.arange(L)
    return torch.from_numpy(((lpd >= lbeg[..., None]) & (lpd <= lend[..., None])).astype(np.float64))


def nexmax_rows(cas, st, sp, bins: np.ndarray) -> np.ndarray:
    """`Cascade.nexmax` for every mother bin in `bins` at once, (m, 7) int.

    TALYS: multiple.f90:1 (multiple)
    Test: tests/hf/test_decay_fast.py
    """
    bins = np.asarray(bins, dtype=np.int64)
    exinc = np.asarray(sp.ex_mev, dtype=np.float64)[bins]
    dex = np.asarray(sp.dex_mev, dtype=np.float64)[bins]
    out = np.empty((bins.size, 7), dtype=np.int64)
    out[:, 0] = bins - 1
    for t in range(1, 7):
        d = cas.spec(st, sp.zix + PARZ[t], sp.nix + PARN[t])
        exm = exinc + 0.5 * dex - sp.sep_mev[t]
        if t > 1:
            exm = exm - float(cas.rg.egrid[cas.rg.ebegin[t]])
        bottom = (np.asarray(d.ex_mev[: d.maxex + 1], dtype=np.float64)
                  - 0.5 * np.asarray(d.dex_mev[: d.maxex + 1], dtype=np.float64))
        below = bottom[None, :] < exm[:, None]
        nb = bottom.size
        last = nb - 1 - np.argmax(below[:, ::-1], axis=1)
        out[:, t] = np.where(below.any(axis=1), last, -1)
    return out


class _Exit:
    """One exit type of one nucleus, all its mother bins (numpy, cut axes)."""

    __slots__ = ("t", "closed", "nrows", "sfac", "T0", "T1", "rho_c", "M", "Mf", "D", "jx",
                 "nd", "ird", "pd", "ar", "rho_d", "tot0", "tot1", "Tn", "C", "lb", "le")


class NucleusWidths:
    """Decay widths of mother bins `bins` of cascade nucleus `sp` at one incident energy, and the
    per-bin feeding `multiple_emission` asks for. Numbers as `decay_batch.NucleusDecay`.

    TALYS: densprepare.f90:1 (densprepare), compound.f90:1 (compound)
    Test: tests/hf/test_decay_fast.py / speed-wave golden
    """

    def __init__(self, cas, st, sp, bins: list[int]):
        from physics.hf.compound.dens_reference import _eendmax

        self.bins = list(bins)
        self.row = {b: i for i, b in enumerate(self.bins)}
        self.odd = sp.A % 2
        self.nlast_mother = sp.nlast_grid
        barr = np.asarray(self.bins, dtype=np.int64)
        exinc = np.asarray(sp.ex_mev, dtype=np.float64)[barr]
        dexinc = np.asarray(sp.dex_mev, dtype=np.float64)[barr]
        self.maxj = np.asarray(sp.maxj, dtype=np.int64)[barr]
        self.nj = int(self.maxj.max()) + 1
        nxm = nexmax_rows(cas, st, sp, barr)
        fnorm = cas.fisom(sp.zix, sp.nix, st)
        daughters = [cas.spec(st, sp.zix + PARZ[t], sp.nix + PARN[t]) for t in range(7)]
        sep = np.array([sp.sep_mev[t] for t in range(7)])
        # every exit type's residual rows on one padded (type, bin, row) axis
        g = _Geometry(exinc, dexinc, nxm, daughters, sep)
        self.exits: list[_Exit] = []
        T0, T1 = self._photon(cas, st, sp, g, exinc, fnorm)
        self.exits.append(self._finish(cas, st, g, 0, daughters[0], T0, T1))
        eendmax = _eendmax(cas.Zt, cas.At, cas.enincmax)
        TP0, TP1 = self._particles(cas, st, g, fnorm, eendmax)
        for t in range(1, 7):
            self.exits.append(self._finish(cas, st, g, t, daughters[t], TP0[t - 1], TP1[t - 1]))
        # denominators of the six exits other than alpha, and where all six are zero
        m = barr.size
        self.dsum6 = np.zeros((m, self.nj, 2))
        self.zero6 = np.ones((m, self.nj, 2), dtype=bool)
        for e in self.exits[:6]:
            if e.D is not None:
                self.dsum6 = self.dsum6 + e.D
                self.zero6 &= e.D == 0.0
        d0 = daughters[0]
        self.levels0 = (jd2_all(d0, g.n[0]), np.asarray(d0.parlev[: g.n[0]]).astype(np.int64))
        self.pending: list[tuple[int, np.ndarray, np.ndarray | None]] = []
        self.resolved: dict[int, tuple] = {}
        self._photon_bin = dn.PhotonBin(self, self.exits[0]) if dn.available() else None
        self._nrows0 = self.exits[0].nrows.tolist()
        self.last_batch = None

    def _photon(self, cas, st, sp, g: "_Geometry", exinc: np.ndarray, fnorm):
        """Tgam on the photon exit's rows, split by c = |P - P'| / 2 and lmaxhf-capped."""
        n = g.n[0]
        m = exinc.size
        L = cas.gammax + 1
        tg = np.zeros((m, n, L, 2))
        efs = exinc - sp.sep_mev[1]
        twopi = _twopi()
        fn1 = float(fnorm[1])
        inrow = g.inrow[0, :, :n]
        egam = exinc[:, None] - g.exout[0, :, :n]
        pos = (egam > 0.0) & inrow
        if pos.any():
            from physics.hf.compound.psf_fast import fstrength_np

            gstrength = cas.gamma_strength(sp.Z, sp.A - 1)
            # psf_fast's numpy form of the same fstrength, bit for bit, where it covers the model
            gp = cas.gamma_params(sp.Z, sp.A - 1)  # PARAMWIRE: the run's parameter set
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
        lp = np.arange(L)
        T0 = tg[:, :, lp, 1 - lp % 2]
        T1 = tg[:, :, lp, lp % 2]
        lmaxhf = np.full((m, n), cas.gammax, dtype=np.int64)
        return _cap_l(T0, T1, lmaxhf, g.nexmax[0], cas.k0 == 0, st.lmaxinc)

    def _particles(self, cas, st, g: "_Geometry", fnorm, eendmax):
        """Tl interpolated to every (type, bin, row) Eout, split by c and lmaxhf-capped, for
        the six particle exits in one pass (densprepare.f90's pol2, as `_interp_tl`)."""
        tls = [cas.trans[t] for t in range(1, 7)]
        L = tls[0][1].shape[1]
        if any(isinstance(x[1], torch.Tensor) or x[1].shape[1] != L for x in tls):
            raise ValueError("decay_fast needs one numpy Tl shape for every particle")
        rg = cas.rg
        m = g.eout.shape[1]
        eend = np.array([min(int(eendmax[t]), rg.maxen) for t in range(1, 7)])
        ebeg = np.array([int(rg.ebegin[t]) for t in range(1, 7)])
        # pol2 only where a residual row is in range: every other row has rho0 = 0
        inrow = g.inrow[1:] & (ebeg < eend)[:, None, None]
        tt, bb, rr = np.nonzero(inrow)
        vals = lms = None
        Lm = 0
        if tt.size:
            egrid = rg.egrid
            xs = np.asarray(egrid[: rg.maxen + 1], dtype=np.float32)
            if not bool(np.all(np.diff(xs) > 0)):  # pragma: no cover - the grid ascends
                raise ValueError("decay_fast needs an ascending emission grid")
            e_ = g.eout[1:][tt, bb, rr]
            eb_ = ebeg[tt]
            ee_ = eend[tt]
            x = e_.astype(np.float32)
            jl = np.clip(np.searchsorted(xs, x, side="right") - 1, eb_ - 1, ee_)
            jl = np.where(x == xs[eb_], eb_, np.where(x == xs[ee_], ee_ - 1, jl))
            lo = np.asarray(egrid, dtype=np.float64)[eb_]
            nen = np.where(e_ < lo, 0, jl).astype(np.int64)
            TL, LM, head0 = _tl_stack(cas, tls)
            lms = LM[tt, np.clip(nen, 0, rg.maxen)]
            # below the grid pol2 extrapolates from nodes 0..2; where those are all zero the
            # transmission is exactly zero, so the entry is not interpolated at all
            live = ~((e_ < lo) & head0[tt])
            if live.any():
                sel = np.flatnonzero(live)
                e_, nen, eb_ = e_[sel], nen[sel], eb_[sel]
                centred = (nen > eb_ + 1) | (nen >= rg.maxen - 1)
                na = np.where(centred, nen - 1, nen)
                nb, nc = na + 1, na + 2
                ea, eb, ec = egrid[na], egrid[nb], egrid[nc]
                w1 = ((e_ - eb) * (e_ - ec) / ((ea - eb) * (ea - ec)))[:, None]
                w2 = ((e_ - ea) * (e_ - ec) / ((eb - ea) * (eb - ec)))[:, None]
                w3 = ((e_ - ea) * (e_ - eb) / ((ec - ea) * (ec - eb)))[:, None]
                ts, lsel = tt[sel], lms[sel]
                Lm = min(int(lsel.max()) + 1, L)
                keep = np.arange(Lm)[None, :] <= lsel[:, None]
                u = w1 * TL[ts, na, :Lm] + w2 * TL[ts, nb, :Lm] + w3 * TL[ts, nc, :Lm]
                u = np.where(keep, u, 0.0)
                fn = np.array([float(fnorm[t + 1]) for t in range(1, 7)])[ts][:, None]
                vals = np.where(u < cas.transeps, 0.0, u) * fn
                vt, vb, vr = ts, bb[sel], rr[sel]
        out0, out1 = [], []
        if vals is None:
            for t in range(1, 7):
                out0.append(np.zeros((m, g.n[t], 0)))
                out1.append(np.zeros((m, g.n[t], 0)))
            return out0, out1
        starts = np.searchsorted(tt, np.arange(7))
        vstarts = np.searchsorted(vt, np.arange(7))
        cols = np.arange(Lm)
        for k in range(6):
            t = k + 1
            n = g.n[t]
            s0, s1 = int(vstarts[k]), int(vstarts[k + 1])
            if s1 == s0 or not vals[s0:s1].any():  # no transmission on any row
                out0.append(np.zeros((m, n, 0)))
                out1.append(np.zeros((m, n, 0)))
                continue
            b_, r_, v = vb[s0:s1], vr[s0:s1], vals[s0:s1]
            # lmaxhf on the in-range rows (0 elsewhere, where every T is 0 here anyway), with
            # lmaxhf(nexmax) = lmaxhf(nexmax - 1) and lmaxhf(0) = lmaxinc for the projectile
            a0, a1 = int(starts[k]), int(starts[k + 1])
            lmaxhf = np.zeros((m, n), dtype=np.int64)
            lmaxhf[bb[a0:a1], rr[a0:a1]] = lms[a0:a1]
            nexm = g.nexmax[t]
            ii = np.nonzero(nexm > 0)[0]
            lmaxhf[ii, nexm[ii]] = lmaxhf[ii, nexm[ii] - 1]
            if t == cas.k0:
                lmaxhf[:, 0] = st.lmaxinc
            v = np.where(cols[None, :] <= lmaxhf[b_, r_][:, None], v, 0.0)
            nzl = np.flatnonzero(v.any(axis=0))
            Lc = int(nzl[-1]) + 1 if nzl.size else 0
            T0 = np.zeros((m, n, Lc))
            T1 = np.zeros((m, n, Lc))
            T0[b_, r_, 0::2] = v[:, 0:Lc:2]
            T1[b_, r_, 1::2] = v[:, 1:Lc:2]
            out0.append(T0)
            out1.append(T1)
        return out0, out1

    def _finish(self, cas, st, g: "_Geometry", t: int, d, T0: np.ndarray, T1: np.ndarray):
        """rho0, the denominators D and the discrete-level pieces of one exit."""
        from physics.hf.compound.prepare import _discfactor

        e = _Exit()
        n = g.n[t]
        m = T0.shape[0]
        e.t, e.nrows = t, g.nexmax[t] + 1
        e.sfac = 1.0 if t == 0 else float(PARSPIN2[t] + 1)
        e.nd = 0
        Lc = T0.shape[2]
        if Lc == 0:  # every transmission is zero: every rho0 * T is zero
            e.closed, e.jx, e.D = True, 1, None
            return e
        nl = d.nlast
        rows = np.arange(n)
        inrow = g.inrow[t, :, :n]
        rb = g.rb[t, :, :n]
        maxj_d = np.asarray(d.maxj[:n], dtype=np.int64)
        base = (self.odd + PARSPIN2[t]) % 2
        irs2 = 2 * np.arange(NUMJ + 1) + base
        valid = ((irs2[None, :] <= 2 * maxj_d[:, None])
                 & (np.arange(NUMJ + 1)[None, :] <= maxj_d[:, None])
                 & (rows > nl)[:, None])  # (n, numJ+1)
        jcols = np.flatnonzero(valid.any(axis=0))
        jc = int(jcols[-1]) + 1 if jcols.size else 0
        ndd = min(nl, n - 1) + 1
        jd2 = (2.0 * np.float32(np.asarray(d.jdis[:ndd]))).astype(np.int64)
        ird = jd2 // 2
        pd = (np.asarray(d.parlev[:ndd]) > 0).astype(np.int64)
        ok = (ird >= 0) & (ird <= NUMJ)
        jx = max(jc, int(ird[ok].max()) + 1 if ok.any() else 0, 1)
        e.jx = jx
        sfac = e.sfac
        nj = self.nj
        # continuum rows: rb * rhogrid where compound.f90 reads it (_rho0_rows's masks)
        if jc:
            # masked factors first: a masked cell is 0 either way, a kept one is rb * rhogrid
            rhog = np.where(valid[:, :jx, None],
                            np.asarray(d.rhogrid[:n], dtype=np.float64)[:, :jx], 0.0)
            if np.array_equal(rhog[:, :, 0], rhog[:, :, 1]):
                # a parity-independent level density (the analytical models): one column,
                # broadcast over P' wherever it is read -- the same numbers
                rhog = rhog[:, :, :1]
            rho_c = np.where(inrow, rb, 0.0)[:, :, None, None] * rhog[None]
            rho_c = np.where(rho_c >= 1.0e-20, rho_c, 0.0)
        else:
            rho_c = np.zeros((m, n, jx, 2))
        e.rho_c = rho_c
        M = _mask(self.odd, PARSPIN2[t], nj, jx, Lc)
        e.M, e.T0, e.T1 = M, T0, T1
        e.Mf = M.reshape(nj, jx * Lc)
        native = dn.available()
        if native:
            # the compiled contraction reads a particle's two parities as one (b, n, l') array and
            # the photon's as (b, 2, n, l'); the widths' denominators stay numpy (below): in C
            # their sums move the golden's feedexcl by up to 1.3e-15, past the 1e-15 identity rule
            e.C = 1 if t >= 1 else 2
            e.Tn = T0 + T1 if t >= 1 else np.ascontiguousarray(np.stack([T0, T1], axis=1))
            e.lb, e.le = dn.spin_l_bounds(self.odd, PARSPIN2[t], nj, jx)
        if jc:
            if t >= 1:
                # a particle's T0 and T1 live on disjoint l' columns (even / odd), so one sum
                # over rows serves both, split by the parity of l' in the spin-l' mask
                Tt = torch.from_numpy(e.Tn if native else T0 + T1)
                R = torch.einsum("mnip,mnl->mipl", torch.from_numpy(rho_c), Tt)
                Mc = _mask_c(self.odd, PARSPIN2[t], nj, jx, Lc)
                MR = torch.einsum("cjil,mipl->mjcp", torch.from_numpy(Mc), R).numpy()
            else:
                Tt = torch.from_numpy(e.Tn if native else np.stack([T0, T1], axis=1))  # (m, c, n, l)
                R = torch.einsum("mnip,mcnl->mcipl", torch.from_numpy(rho_c), Tt)
                MR = torch.einsum("jil,mcipl->mjcp", torch.from_numpy(M), R).numpy()
            # parity P of the mother cell: c = 0 reaches p = P, c = 1 reaches p = 1 - P
            if MR.shape[3] == 1:
                D = np.stack([MR[:, :, 0, 0] + MR[:, :, 1, 0], MR[:, :, 1, 0] + MR[:, :, 0, 0]],
                             axis=-1) * sfac
            else:
                D = np.stack([MR[:, :, 0, 0] + MR[:, :, 1, 1], MR[:, :, 1, 0] + MR[:, :, 0, 1]],
                             axis=-1) * sfac
        else:
            D = np.zeros((m, nj, 2))
        # discrete rows: one (Ir, parity) cell each
        discfactor = _discfactor(d)
        k = np.arange(ndd)
        val = np.where(k > d.ntop, rb[:, :ndd] * discfactor, rb[:, :ndd])
        ir_w = np.asarray(d.jdis[:ndd]).astype(np.int64)  # int(jdis): where rho0 is written
        pidx = np.where(np.asarray(d.parlev[:ndd]) == -1, 0, 1)
        same = (ir_w == ird) & (pidx == pd) & (ir_w >= 0) & (ir_w <= NUMJ) & ok
        rho_d = np.where(same[None, :] & inrow[:, :ndd], val, 0.0)
        rho_d = np.where(rho_d >= 1.0e-20, rho_d, 0.0)
        if nl == 0:
            rho_d[:, 0] = 0.0
        if rho_d.any():
            Md = _mask_d(self.odd, PARSPIN2[t], nj, np.ascontiguousarray(jd2).tobytes(), Lc)
            Td = np.stack([T0[:, :ndd], T1[:, :ndd]], axis=1)  # (m, c, k, l)
            tot = torch.einsum("jnl,mcnl->mjcn", Md, torch.from_numpy(Td)).numpy()
            # a mother cell of parity P reaches level k through c = (P != pd[k])
            tot0 = np.ascontiguousarray(tot[:, :, 0])  # (m, J, k)
            tot1 = np.ascontiguousarray(tot[:, :, 1])
            r_par = rho_d * (pd == 1)
            r_npar = rho_d * (pd == 0)
            dd = np.stack([(tot0 @ r_npar[:, :, None] + tot1 @ r_par[:, :, None])[..., 0],
                           (tot0 @ r_par[:, :, None] + tot1 @ r_npar[:, :, None])[..., 0]],
                          axis=-1)
            D = D + sfac * dd
            e.nd, e.ird, e.pd, e.ar = ndd, np.clip(ird, 0, NUMJ), pd, np.arange(ndd)
            e.rho_d, e.tot0, e.tot1 = rho_d, tot0, tot1
        e.closed = not bool((D != 0.0).any())
        e.D = None if e.closed else D
        return e

    # ------------------------------------------------------------------ one bin

    def feeding(self, nex: int, pop_mother: np.ndarray, popeps_a: float,
                dmulti: float = 0.0):
        """`compound_decay` of mother bin `nex` given its current (J, parity) population, as
        `(dpop, mcontrib, fisfeed, leftover)`: the photon exit contracted now, the particle exits
        on read (`_Lazy`). A closed exit is `None` in both maps. `leftover` is compound.f90's
        iloop-1 trapped flux (:404-419), which is not part of `mcontrib`.

        `dmulti` is `Dmulti(nex)` (multipreeq2.f90:374): the fraction of the bin that multiple
        pre-equilibrium already emitted, which compound.f90:402 takes out of the compound decay
        of the same bin. It is zero everywhere below `emulpre` (20 MeV) and for every bin that
        multiple pre-equilibrium did not touch, and `(1 - 0.0) * pop` is `pop` bit for bit, so
        the arm that never sees multiple pre-equilibrium keeps its numbers exactly. The compiled
        photon kernel takes no `Dmulti`, so a depleted bin goes down the numpy path instead.

        TALYS: compound.f90:1 (compound)
        Test: tests/hf/test_decay_fast.py / speed-wave golden
        """
        i = self.row[nex]
        maxj = int(self.maxj[i])
        nj = maxj + 1
        pop = pop_mother[:nj]  # read before anything feeds this nucleus again
        popeps_b = popeps_a / (5 * max(maxj, 1)) * 0.5
        if self._photon_bin is not None and dmulti == 0.0:
            feed, dead, trapped, dp, mc = self._photon_bin(
                i, np.ascontiguousarray(pop, dtype=np.float64), popeps_b)
            if not trapped:
                dp0 = mc0 = None
                if not self.exits[0].closed:
                    r = self._nrows0[i]
                    dp0, mc0 = dp[:r], mc[:r]
                self.pending.append((nex, feed, dead))
                return (_Lazy(self, nex, dp0, mc0, "dp"), _Lazy(self, nex, dp0, mc0, "mc"),
                        0.0, 0.0)
        active = pop >= popeps_b
        ex = self.exits
        # compound.f90:222: a cell no other exit reaches does not decay by alpha either
        dead = active & self.zero6[i, :nj]
        d6 = ex[6].D
        if dead.any():
            denom = (self.dsum6[i, :nj] if d6 is None
                     else self.dsum6[i, :nj] + np.where(dead, 0.0, d6[i, :nj]))
        else:
            dead = None
            denom = self.dsum6[i, :nj] if d6 is None else self.dsum6[i, :nj] + d6[i, :nj]
        live = active & (pop != 0.0) & (denom != 0.0)
        # compound.f90:402. With Dmulti = 0 the factor is exactly 1.0 and the bits are pop's.
        feed = np.where(live, (1.0 - dmulti) * pop / np.where(live, denom, 1.0), 0.0)
        dp0 = mc0 = None
        e0 = ex[0]
        if not e0.closed:
            dp0 = self._contract_one(e0, i, feed, nj)[: int(e0.nrows[i])]
            mc0 = dp0.sum((1, 2))
        trapped = active & (pop != 0.0) & (denom == 0.0)
        leftover = 0.0
        if trapped.any():
            # compound.f90:404-419: spread over the compound nucleus's own discrete levels.
            # `mcontrib` is the width-weighted feeding of iloop 2 and this is iloop 1's, so it is
            # NOT in `mcontrib`; it is returned separately and `multiple_emission` puts it where
            # compound.f90 does (`xspopex` of the levels and `mcontrib(0, nex, nexout)`, and so
            # `feedexcl`), but not into `xsfeed`/`xspopnuc` or out of the mother's `xspopex`.
            leftover = float(pop[trapped].sum())
            nl = self.nlast_mother
            nrow0 = int(e0.nrows[i])
            jdis2, parlev = self.levels0
            big = np.zeros((nrow0, NUMJ + 1, 2))
            if dp0 is None:
                mc0 = np.zeros(nrow0)
            else:
                big[:, : dp0.shape[1]] = dp0
            mask = np.zeros_like(big)
            for nexout in range(min(nl, nrow0 - 1) + 1):
                mask[nexout, int(jdis2[nexout]) // 2, 0 if int(parlev[nexout]) == -1 else 1] = 1.0
            for J, p in zip(*np.nonzero(trapped)):  # noqa: B905
                share = pop[J, p] / (nl + 1.0)
                big = big + mask * share
            dp0 = big
        self.pending.append((nex, feed, dead))
        return (_Lazy(self, nex, dp0, mc0, "dp"), _Lazy(self, nex, dp0, mc0, "mc"),
                0.0, leftover)

    def _contract_one(self, e: _Exit, i: int, f: np.ndarray, nj: int) -> np.ndarray:
        """`_contract` for one mother row `i` (the photon exit, every bin), on views."""
        jx = e.jx
        L = e.M.shape[2]
        V0 = (f.T @ e.Mf[:nj]).reshape(2, jx, L)  # (P', Ir, l)
        W0 = V0.transpose(1, 0, 2).reshape(jx * 2, L)
        W1 = V0[::-1].transpose(1, 0, 2).reshape(jx * 2, L)
        TV = (e.T0[i] @ W0.T + e.T1[i] @ W1.T).reshape(-1, jx, 2)
        dp = e.sfac * e.rho_c[i] * TV
        if e.nd:
            A = f.T @ e.tot0[i, :nj]  # (P, k)
            B = f.T @ e.tot1[i, :nj]
            fd = A[e.pd, e.ar] + B[1 - e.pd, e.ar]
            dp[e.ar, e.ird, e.pd] += e.sfac * e.rho_d[i] * fd
        return dp

    def _contract(self, e: _Exit, idx, F: np.ndarray, nj: int) -> np.ndarray:
        """dp[b, n, Ir, P'] of exit `e` for mother rows `idx` fed by F[b, J, P] (J < nj)."""
        M = e.M[:nj]
        b_, jx, L = len(idx), e.jx, M.shape[2]
        Mf = M.reshape(nj, jx * L)
        sel = _rows(idx)
        # V_c[b, Ir, P', l] = sum_J M[J, Ir, l] f[b, J, P' xor c]
        V0 = np.matmul(F.transpose(0, 2, 1), Mf).reshape(b_, 2, jx, L).transpose(0, 2, 1, 3)
        V1 = V0[:, :, ::-1]
        # TV[b, n, Ir, P'] = sum_l T0[b, n, l] V0[b, Ir, P', l] + T1[b, n, l] V1[b, Ir, P', l]
        if e.t >= 1:  # T0 and T1 on disjoint l' columns: one product with the columns merged
            W = np.where(np.arange(L) % 2 == 0, V0, V1).reshape(b_, jx * 2, L)
            TV = np.matmul(e.T0[sel] + e.T1[sel], W.transpose(0, 2, 1)).reshape(b_, -1, jx, 2)
        else:
            W0 = np.ascontiguousarray(V0).reshape(b_, jx * 2, L)
            W1 = np.ascontiguousarray(V1).reshape(b_, jx * 2, L)
            TV = (np.matmul(e.T0[sel], W0.transpose(0, 2, 1))
                  + np.matmul(e.T1[sel], W1.transpose(0, 2, 1))).reshape(b_, -1, jx, 2)
        dp = e.sfac * e.rho_c[sel] * TV
        if e.nd:
            Ft = F.transpose(0, 2, 1)
            A = Ft @ e.tot0[sel][:, :nj]  # (b, P, k)
            B = Ft @ e.tot1[sel][:, :nj]
            fd = A[:, e.pd, e.ar] + B[:, 1 - e.pd, e.ar]
            dp[:, e.ar, e.ird, e.pd] += e.sfac * e.rho_d[sel] * fd
        return dp

    def _resolve(self) -> None:
        """Contract every particle exit for every pending bin in one call per exit."""
        if not self.pending:
            return
        nexs = [p[0] for p in self.pending]
        idx = np.array([self.row[x] for x in nexs])
        F = np.zeros((len(nexs), self.nj, 2))
        for b, (_, f, _dead) in enumerate(self.pending):
            F[b, : f.shape[0]] = f
        F6 = None
        if any(p[2] is not None for p in self.pending):
            F6 = F.copy()
            for b, (_, f, dead) in enumerate(self.pending):
                if dead is not None:
                    F6[b, : f.shape[0]] = np.where(dead, 0.0, f)
        batch = {}
        for e in self.exits[1:]:
            if e.closed:
                batch[e.t] = None
                continue
            Fe = F6 if (e.t == 6 and F6 is not None) else F
            if dn.available():
                dp, mc = dn.contract(np.ascontiguousarray(idx, dtype=np.int64), Fe, e, e.C, e.Tn,
                                     e.lb, e.le, self.nj)
            else:
                dp = self._contract(e, idx, Fe, self.nj)
                mc = dp.sum((2, 3))
            batch[e.t] = (dp, mc, e.nrows[idx])
        for b, x in enumerate(nexs):
            self.resolved[x] = (batch, b)
        self.last_batch = (nexs, batch)
        self.pending = []

    def particle_batch(self, nexs: list[int]):
        """Particle feeding of mother bins `nexs` (the pending bins, in the order they were fed)
        as one batch: type -> None (closed) or (dp (B, rows, Ir, 2), mcontrib (B, rows)). None
        when those bins are not exactly one pending batch."""
        if self.pending and [p[0] for p in self.pending] == list(nexs):
            self._resolve()
            return self.last_batch[1]
        if not self.pending and getattr(self, "last_batch", None) is not None \
                and self.last_batch[0] == list(nexs):
            return self.last_batch[1]
        return None

class _Geometry:
    """densprepare.f90's per-(bin, residual row) kinematics for all seven exit types on one
    padded (type, bin, row) axis: Eout, Rboundary, the residual excitation Exout, row masks.
    `_eout_and_rboundary_rows` with a mother axis (as `decay_batch.NucleusDecay`)."""

    def __init__(self, exinc, dexinc, nxm, daughters, sep):
        m = exinc.size
        self.nexmax = [np.maximum(nxm[:, t], 0) for t in range(7)]
        self.n = [int(x.max()) + 1 for x in self.nexmax]
        N = max(self.n)
        ex = np.zeros((7, 1, N))
        dex = np.zeros((7, 1, N))
        nl = np.zeros((7, 1, 1), dtype=np.int64)
        for t, d in enumerate(daughters):
            k = self.n[t]
            ex[t, 0, :k] = np.asarray(d.ex_mev[:k], dtype=np.float64)
            dex[t, 0, :k] = np.asarray(d.dex_mev[:k], dtype=np.float64)
            nl[t] = d.nlast
        dexhalf = 0.5 * dex
        nexmax = np.stack(self.nexmax)[:, :, None]  # (7, m, 1)
        rows = np.arange(N)[None, None, :]
        inrow = rows <= nexmax
        ss = sep[:, None, None]
        ex0plus = (exinc + 0.5 * dexinc)[None, :, None]
        ex0min = (exinc - 0.5 * dexinc)[None, :, None]
        ex1min = ex - dexhalf
        top = (rows == nexmax) & (np.arange(7) >= 1)[:, None, None]
        ex1plus = np.where(top, ex0plus - ss, ex + dexhalf)
        exout_c = np.where(top, 0.5 * (ex1plus + ex1min), ex)
        emax = (ex0plus - ss) - ex1min
        emin = (ex0min - ss) - ex1plus
        eout_mid = 0.5 * (emin + emax)
        below = emin < 0.0
        half = 0.5 * (emax - emin)
        with np.errstate(divide="ignore", invalid="ignore", over="ignore"):
            rb_c = np.where(below, np.where(eout_mid > 0.0, 1.0 - 0.5 * (emin / half) ** 2,
                                            0.5 * (emax / half) ** 2), 1.0)
        eout_c = 0.5 * (np.where(below, 0.0, emin) + emax)
        exm = ex + ss
        part = (ex0min < exm) & (exm <= ex0plus)
        with np.errstate(divide="ignore", invalid="ignore"):
            rb_d = np.where(part, (ex0plus - exm) / dexinc[None, :, None], 1.0)
        eout_d = np.where(part, 0.5 * (ex0plus + exm) - ss - ex,
                          (exinc[None, :, None] - ss) - ex)
        cont_row = rows > nl
        eout = np.where(cont_row, eout_c, eout_d)
        self.rb = np.where(cont_row, rb_c, rb_d)
        self.exout = np.where(cont_row, exout_c, np.broadcast_to(ex, (7, m, N)))
        self.eout = np.where(inrow, eout, 0.0)
        self.inrow = inrow


def _cap_l(T0, T1, lmaxhf, nexmax, is_k0: bool, lmaxinc):
    """densprepare.f90's lmaxhf cap on (bin, row, l') transmissions, and the l' axis cut after
    its last open column. lmaxhf(nexmax) = lmaxhf(nexmax - 1); lmaxhf(0) of the projectile
    type is lmaxinc."""
    ii = np.nonzero(nexmax > 0)[0]
    lmaxhf[ii, nexmax[ii]] = lmaxhf[ii, nexmax[ii] - 1]
    if is_k0:
        lmaxhf[:, 0] = lmaxinc
    L = T0.shape[2]
    lmask = np.arange(L)[None, None, :] <= lmaxhf[:, :, None]
    T0 = np.where(lmask, T0, 0.0)
    T1 = np.where(lmask, T1, 0.0)
    nzl = np.flatnonzero(T0.any(axis=(0, 1)) | T1.any(axis=(0, 1)))
    Lc = int(nzl[-1]) + 1 if nzl.size else 0
    return np.ascontiguousarray(T0[:, :, :Lc]), np.ascontiguousarray(T1[:, :, :Lc])


def rhogrid_cut(rhog: np.ndarray, jx: int) -> np.ndarray:
    if rhog.shape[1] >= jx:
        return rhog[:, :jx]
    out = np.zeros((rhog.shape[0], jx, 2))
    out[:, : rhog.shape[1]] = rhog
    return out


def jd2_all(d, n: int) -> np.ndarray:
    return (2.0 * np.float32(np.asarray(d.jdis[:n]))).astype(np.int64)


class _Lazy(Mapping):
    """type -> dpop (or mcontrib) of one bin: type 0 held, types 1..6 contracted on first read."""

    __slots__ = ("nw", "nex", "dp0", "mc0", "what")

    def __init__(self, nw: NucleusWidths, nex: int, dp0, mc0, what: str):
        self.nw, self.nex, self.dp0, self.mc0, self.what = nw, nex, dp0, mc0, what

    def __getitem__(self, t: int):
        if t == 0:
            return self.dp0 if self.what == "dp" else self.mc0
        if not 1 <= t <= 6:
            raise KeyError(t)
        r = self.nw.resolved.get(self.nex)
        if r is None:
            self.nw._resolve()
            r = self.nw.resolved[self.nex]
        batch, b = r
        v = batch[t]
        if v is None:
            return None
        k = int(v[2][b])
        return v[0][b, :k] if self.what == "dp" else v[1][b, :k]

    def __iter__(self):
        return iter(range(7))

    def __len__(self) -> int:
        return 7
