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

    def __init__(self, cas, st, sp, bins: list[int]):
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
        fnorm = cas.fisom(sp.zix, sp.nix, st)
        daughters = [cas.spec(st, sp.zix + PARZ[t], sp.nix + PARN[t]) for t in range(7)]
        nexmax = np.maximum(nxm, 0)
        ns = [int(nexmax[:, t].max()) + 1 for t in range(7)]
        tg = self._photon(cas, sp, daughters[0], exinc, nexmax[:, 0], ns[0], fnorm)
        tls = [cas.trans[t] for t in range(1, 7)]
        Ltl = tls[0][1].shape[1]
        if any(isinstance(x[1], torch.Tensor) or x[1].shape[1] != Ltl for x in tls):
            raise NotImplementedError("one numpy Tl shape for every particle")
        TL, LM, head0 = _tl_stack(cas, tls)
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

    def _photon(self, cas, sp, d0, exinc: np.ndarray, nexmax0: np.ndarray, n: int, fnorm):
        """`NucleusWidths._photon`'s Tgam[b, row, l', irad] before the l' split and cap."""
        m = exinc.size
        L = cas.gammax + 1
        tg = np.zeros((m, n, L, 2))
        efs = exinc - sp.sep_mev[1]
        fn1 = float(fnorm[1])
        ex0 = np.asarray(d0.ex_mev[:n], dtype=np.float64)
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
