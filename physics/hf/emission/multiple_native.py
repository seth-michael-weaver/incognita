"""NATIVEX: `multiple_emission`'s walk down one cascade nucleus in one compiled call.

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

Task: NATIVEX (the speed work; no physics of its own). Acceptance test: `tests/hf/test_nativex.py`
(the walk against `multiple._decay_nucleus_numpy` and the tensor loop) and the G-NATIVEX closeness
gate.

TALYS routines this computes (in `native/nativex.c`'s `nx_walk`):
    multiple.f90:1 (multiple)     -- the loop over mother bins, popexcl, feedexcl, xsfeed
    cascade.f90:1 (cascade)       -- the gamma cascade of a discrete level under S_n
    compound.f90:1 (compound)     -- a bin's feeding of its daughters, the trapped leftover and
                                     fisfeed, over `compound.decay_fast.NucleusWidths`

`_decay_nucleus_numpy` walks a nucleus bin by bin in Python: one `decay` callback per bin (the
compiled photon kernel through `decay_fast.PhotonBin`), the lazy particle contraction, and the
records written through dicts and `FeedTable` rows. On the Mac that bookkeeping was about a third
of `multiple_emission`. Here the whole walk is one C call over the widths `NucleusWidths` has
already built: every array update of the numpy walk, per array element in its order (a particle
exit feeds another nucleus, so it is applied right after its bin rather than after the walk), with
the records written into the same `FeedTable`s and dicts.

Multiple pre-equilibrium (`Einc >= emulpre`, the 20 MeV energy, which ran the tensor loop) is in
the walk too: `Cascade.mpe_inputs`' per-nucleus constants are packed once (`_Walk.attach_mpe`) and
`nx_walk` runs `preeq.mpe_fast`'s kernel loop (`speedw.c`'s `sw_mpe_bin`) and `multiple._apply_mpe`
for every bin with a particle-hole population, after its `popexcl` snapshot and before its decay,
as the tensor loop does. The daughters' particle-hole additions are summed per daughter bin before
they are added to the dict entries, which moves them by rounding. Without that packing
(`flaggshell`, a tensor on a graph, `HF_NATIVEX_MPE=0`) the walk stops before each such bin, runs
the Python `mpe` callback and `_apply_mpe`, and resumes with its `Dmulti`.

Returns None (and touches nothing) when a nucleus has no `NucleusWidths` (a graph, `flagfullhf`,
an uncovered fission ladder, a `decay` callback without `.widths`).
"""

from __future__ import annotations

import os

import numpy as np
import torch

from physics.hf.compound import decay_native as dn
from physics.hf.compound.decay_batch import PARN, PARZ
from physics.hf.compound.prepare import NUMJ, PARSPIN2
from physics.hf.core.tensors import DTYPE
from physics.hf.emission.feed_table import FeedTable
from physics.hf.native import nativex

_I64 = np.int64
_U8 = np.uint8


def _c(a, dtype=np.float64):
    return np.ascontiguousarray(a, dtype=dtype)


class _Walk:
    """The packed arguments of `nx_walk` for one nucleus."""

    def __init__(self, nuc, daughters: dict, nw, zc: int, nc: int, popepsA: float, smin: float,
                 feedexcl: dict, records):
        so = nativex.lib()
        self.fn = so.nx_walk
        self.keep = []
        X = nuc.xspop_mb.numpy()
        XE = nuc.xspopex_mb.numpy()
        self.X, self.XE = X, XE
        xrows = X.shape[0]
        maxex = nuc.maxex
        ip = np.zeros(16 + 16 * 7, dtype=_I64)
        pp = np.zeros(160, dtype=np.uint64)
        dpar = np.zeros(10)
        self.ip, self.pp, self.dpar = ip, pp, dpar

        def put(slot, a):
            self.keep.append(a)
            pp[slot] = nativex.ptr(a)
            return a

        lvl = nuc.parlev.numpy() if hasattr(nuc.parlev, "numpy") else np.asarray(nuc.parlev)
        put(0, _c(nuc.ex_mev.numpy()))
        put(1, _c(nuc.tau_s.numpy()))
        put(2, _c(nuc.jdis.numpy().astype(_I64), _I64))
        put(3, _c(np.where(lvl == -1, 0, 1), _I64))
        off = np.zeros(xrows + 1, dtype=_I64)
        bk, br = [], []
        for nex in range(xrows):
            got = nuc.branch.get(nex, [])
            for k, ratio in got:
                bk.append(int(k))
                br.append(float(ratio))
            off[nex + 1] = len(bk)
        put(4, off)
        put(5, _c(np.asarray(bk, dtype=_I64).reshape(-1), _I64))
        put(6, _c(np.asarray(br, dtype=np.float64).reshape(-1)))
        m = len(nw.bins)
        nj = nw.nj
        rowmap = np.full(xrows, -1, dtype=_I64)
        rowmap[np.asarray(nw.bins, dtype=_I64)] = np.arange(m, dtype=_I64)
        put(7, rowmap)
        put(8, _c(nw.maxj, _I64))
        put(9, _c(nw.dsum6))
        put(10, _c(nw.zero6, _U8))
        d6 = nw.exits[6].D
        if d6 is not None:
            put(11, _c(d6))
        fis = getattr(nw, "fis", None)
        if fis is not None:
            put(12, _c(fis))
        put(13, _c(nw.levels0[0], _I64))
        put(14, _c(np.where(np.asarray(nw.levels0[1]) == -1, 0, 1), _I64))
        put(15, X)
        put(16, XE)
        put(17, _c(nuc.dex_mev.numpy()))
        ip[:7] = (xrows, maxex, nuc.nlast, m, nj, int(d6 is not None), int(fis is not None))
        vmax, dpmax, nmax = 1, 1, 1
        self.tables = {}
        for t in range(7):
            d = daughters.get(t)
            if d is None:
                continue
            e = nw.exits[t]
            DX = X if t == 0 else d.xspop_mb.numpy()
            drows = DX.shape[0]
            s = 16 + 16 * t
            q = 20 + 16 * t
            rec = bool(records[t])
            ip[s: s + 4] = (1, drows, int(rec), int(e.closed))
            if t > 0:
                put(q, DX)
                put(q + 1, d.xspopex_mb.numpy())
            dpar[3 + t] = e.sfac
            put(q + 6, _c(e.nrows, _I64))
            if rec:
                fe = FeedTable(maxex + 2, drows)
                self.tables[t] = fe
                put(q + 12, fe.val)
                put(q + 13, fe.present.view(_U8))
                ip[s + 10: s + 12] = (maxex + 2, drows)
            if e.closed:
                continue
            _, n, jx, np_ = e.rho_c.shape
            tn = getattr(e, "Tn", None)
            if tn is None:
                tn = e.T0 + e.T1 if t >= 1 else np.stack([e.T0, e.T1], axis=1)
            tn = _c(tn)
            L = tn.shape[-1]
            lb = getattr(e, "lb", None)
            if lb is None:
                lb, le = dn.spin_l_bounds(nw.odd, PARSPIN2[t], nj, jx)
            else:
                le = e.le
            nd = int(e.nd)
            ip[s + 4: s + 10] = (n, jx, np_, L, 1 if t >= 1 else 2, nd)
            put(q + 2, _c(e.rho_c))
            put(q + 3, tn)
            put(q + 4, _c(lb, _I64))
            put(q + 5, _c(le, _I64))
            if nd:
                put(q + 7, _c(e.tot0))
                put(q + 8, _c(e.tot1))
                put(q + 9, _c(e.rho_d))
                put(q + 10, _c(e.ird, _I64))
                put(q + 11, _c(e.pd, _I64))
            vmax = max(vmax, jx * 2 * L)
            dpmax = max(dpmax, n * jx * 2)
            nmax = max(nmax, n)
        nmax = max(nmax, xrows)
        dpmax = max(dpmax, xrows * (NUMJ + 1) * 2)
        self.popexcl = put(136, np.zeros(xrows))
        self.part = put(137, np.zeros((7, xrows)))
        self.partf = put(138, np.zeros((7, xrows), dtype=_U8))
        self.fisfeed = put(139, np.zeros(xrows))
        self.fisf = put(140, np.zeros(xrows, dtype=_U8))
        self.xsfeed = put(141, np.zeros(8))
        self.xsfeedf = put(142, np.zeros(8, dtype=_U8))
        self.xspopnuc = put(143, np.zeros(7))
        self.created = put(144, np.zeros(7, dtype=_U8))
        work = [np.zeros(vmax), np.zeros(dpmax), np.zeros(nmax), np.zeros(nj * 2),
                np.zeros(nj * 2), np.zeros(nj * 2, dtype=_U8)]
        self.keep.extend(work)
        put(145, np.array([nativex.ptr(w) for w in work], dtype=np.uint64))
        dpar[0], dpar[1] = smin, popepsA
        self.args = (nativex.ptr(ip), nativex.ptr(pp), nativex.ptr(dpar))

    def attach_mpe(self, nuc, daughters: dict, context, zc: int, nc: int) -> bool:
        """Pack multiple pre-equilibrium for the walk (`mpe_bin` in nativex.c): everything
        `Cascade.mpe_inputs` builds per bin that does not depend on the bin, once per nucleus.
        False (nothing packed) where the compiled bin does not apply."""
        from physics.hf.compound.decay_fast import nexmax_rows
        from physics.hf.core.grids import emission_end
        from physics.hf.density.particle_hole import EFERMI_MEV
        from physics.hf.preeq.prepare import single_particle_densities
        from physics.hf.preeq.spin import preeq_spin_distribution

        cas, st, _nuclei, etot = context
        if bool(cas.options.flaggshell) or (zc, nc) == (0, 0):
            return False
        ph = {k: v for k, v in nuc.xspopph2_mb.items() if 1 <= k <= nuc.maxex}
        if not ph:
            return False
        if any(not isinstance(v, torch.Tensor) or v.requires_grad or v.dim() != 4
               for v in ph.values()):
            return False
        P1 = next(iter(ph.values())).shape[0]
        P4 = P1 ** 4
        tj = [cas.trans[t][0] for t in (1, 2)]
        if any(isinstance(x, torch.Tensor) for x in tj):
            return False
        xrows = self.X.shape[0]
        sp = cas.spec(st, zc, nc)
        dsp = [cas.spec(st, sp.zix + PARZ[t], sp.nix + PARN[t]) for t in (1, 2)]
        nb = max(d.maxex for d in dsp) + 1
        mother = np.zeros((xrows, P4))
        flags = np.zeros(xrows, dtype=_U8)
        for k, v in ph.items():
            mother[k] = v.detach().numpy().reshape(-1)
            flags[k] = 1
        bins = np.flatnonzero(flags)
        nxm = np.zeros((xrows, 7), dtype=_I64)
        nxm[bins] = nexmax_rows(cas, st, sp, bins)
        key = ("_nativex_eend", round(float(etot), 9))
        eend = st.__dict__.get(key)
        if eend is None:
            eend, _ = emission_end(cas.rg.egrid, cas.rg.maxen, etot,
                                   {t: cas.rg.s0[t] for t in range(7)}, cas.rg.ebegin,
                                   {t: False for t in range(7)})
            st.__dict__[key] = eend
        kph = float(cas.params.at("kph"))
        rnj = cas.__dict__.get("_nativex_rnj")
        nj1 = NUMJ + 1
        if rnj is None:
            r = preeq_spin_distribution(cas.options, cas.params, cas.At)
            v = np.zeros(nj1)
            row = r["RnJ"][2].detach().numpy()
            v[: min(nj1, row.shape[0])] = row[:nj1]
            jj = np.arange(nj1, dtype=np.float64)
            rnj = cas.__dict__["_nativex_rnj"] = 0.5 * (2.0 * jj + 1.0) * v / float(r["RnJsum"][2])
        jw = np.zeros((2, nb, nj1))
        dex = np.zeros((2, nb))
        dx = np.zeros((2, nb))
        for di, d in enumerate(dsp):
            k = min(nb, d.maxex + 1, len(d.ex_mev))
            dx[di, :k] = np.asarray(d.ex_mev[:k], dtype=np.float64)
            dex[di, :k] = np.asarray(d.dex_mev[:k], dtype=np.float64)
            for nexout in range(nb):
                mj = int(d.maxj[nexout]) if nexout <= d.maxex else 0
                jw[di, nexout, : min(mj, NUMJ) + 1] = rnj[: min(mj, NUMJ) + 1]
        _, gpc, gnc = single_particle_densities(sp.Z, sp.A - sp.Z, kph)
        c0 = cas.spec(st, 0, 0)
        _, gp0, gn0 = single_particle_densities(c0.Z, c0.A - c0.Z, kph)
        dg = [single_particle_densities(d.Z, d.A - d.Z, kph) for d in dsp]
        rg = cas.rg
        mi = np.array([P1 - 1, nb, dsp[0].nlast_grid, dsp[1].nlast_grid, dsp[0].zix, dsp[1].zix,
                       dsp[0].nix, dsp[1].nix, dsp[0].maxex, dsp[1].maxex, rg.ebegin[1],
                       rg.ebegin[2], eend[1], eend[2], rg.maxen, xrows], dtype=_I64)
        md = np.array([gpc, gnc, gp0, gn0, EFERMI_MEV, sp.sep_mev[1], sp.sep_mev[2], dg[0][1],
                       dg[1][1], dg[0][2], dg[1][2]], dtype=np.float64)
        acc, accf = [], []
        for t in (1, 2):
            d = daughters.get(t)
            rows = d.xspop_mb.shape[0] if d is not None else 0
            acc.append(np.zeros((rows, P4)) if d is not None else None)
            accf.append(np.zeros(rows, dtype=_U8) if d is not None else None)
        mul = np.zeros(2, dtype=_U8)
        arrs = [mother, flags, nxm, jw, dx, dex,
                np.ascontiguousarray(np.asarray(rg.egrid, dtype=np.float64)[: rg.maxen + 1],
                                     dtype=np.float32),
                np.ascontiguousarray(np.asarray(tj[0])[:, 0, 2], dtype=np.float64),
                np.ascontiguousarray(np.asarray(tj[1])[:, 0, 2], dtype=np.float64),
                acc[0], acc[1], accf[0], accf[1], mul, np.zeros(2 * nb), np.zeros(2 * nb),
                np.zeros(2 * nb * nj1), np.zeros(2 * nb)]
        mp = np.array([0 if a is None else nativex.ptr(a) for a in arrs], dtype=np.uint64)
        block = np.array([nativex.ptr(mi), nativex.ptr(md), nativex.ptr(mp)], dtype=np.uint64)
        self.keep.extend([mi, md, mp, block, *[a for a in arrs if a is not None]])
        self.pp[146] = nativex.ptr(block)
        self.mpe = (P1, mother, flags, acc, accf, mul)
        return True

    def detach_mpe(self, nuc, daughters: dict) -> None:
        """The particle-hole populations and `mulpre` flags `mpe_bin` produced, back into the
        nuclei (as `multiple._apply_mpe` writes them)."""
        P1, mother, flags, acc, accf, mul = self.mpe
        shape = (P1,) * 4
        for k in np.flatnonzero(flags == 2).tolist():
            nuc.xspopph2_mb[k] = torch.from_numpy(mother[k].reshape(shape).copy())
        for di, t in enumerate((1, 2)):
            d = daughters.get(t)
            if d is None:
                continue
            for j in np.flatnonzero(accf[di]).tolist():
                cur = d.xspopph2_mb.get(j)
                if cur is None:
                    cur = d.xspopph2_mb[j] = torch.zeros(shape, dtype=DTYPE)
                if cur.requires_grad:  # pragma: no cover - the walk runs off the graph
                    d.xspopph2_mb[j] = cur + torch.from_numpy(acc[di][j].reshape(shape))
                else:
                    a = cur.numpy()
                    a += acc[di][j].reshape(shape)
            if mul[di]:
                d.mulpre = True

    def load(self, daughters: dict, xsfeed: dict) -> None:
        for t, d in daughters.items():
            self.xspopnuc[t] = d.xspopnuc_mb
        for t in range(-1, 7):
            self.xsfeed[t + 1] = xsfeed.get(t, 0.0)

    def unload(self, daughters: dict, xsfeed: dict) -> None:
        for t, d in daughters.items():
            d.xspopnuc_mb = float(self.xspopnuc[t])
        for t in range(-1, 7):
            if self.xsfeedf[t + 1] or t in xsfeed:
                xsfeed[t] = float(self.xsfeed[t + 1])

    def run(self, hi: int, lo: int, resume: bool = False, dmulti: float = 0.0) -> None:
        if hi < lo:
            return
        rc = self.fn(*self.args, hi, lo, int(resume), float(dmulti))
        if rc != 0:  # pragma: no cover - every decaying bin is a row of the widths
            raise RuntimeError(f"nx_walk: bin without a width row (rc {rc})")


def decay_nucleus(nuc, daughters: dict, decay, zc: int, nc: int, popepsA: float, smin: float,
                  popexcl: dict, feedexcl: dict, xsfeed: dict, xspartial: dict, fisfeed: dict,
                  mpe=None, records=None):
    """`multiple_emission`'s loop over the mother bins of one nucleus, compiled; returns
    `xsgamdistot`, or None (with nothing touched) where the walk does not apply.

    TALYS: multiple.f90:1 (multiple), cascade.f90:1 (cascade), compound.f90:1 (compound)
    Test: tests/hf/test_nativex.py
    """
    from physics.hf.emission import multiple as M

    widths = getattr(decay, "widths", None)
    if widths is None or not nativex.available():
        return None
    maxex = nuc.maxex
    XE = nuc.xspopex_mb.numpy()
    ex = nuc.ex_mev.numpy()
    nl = nuc.nlast
    first = None
    for nex in range(maxex, 0, -1):
        if nex <= nl and ex[nex] <= smin:
            continue
        if XE[nex] >= popepsA:
            first = nex
            break
    nw = None
    if first is not None:
        nw = widths(zc, nc, first)
        if nw is None:
            return None
    records = [M._records_feedexcl(zc, nc, t) for t in range(7)]
    if nw is None:
        return _cascade_only(nuc, zc, nc, popepsA, smin, popexcl, feedexcl, xspartial, records)
    w = _Walk(nuc, daughters, nw, zc, nc, popepsA, smin, feedexcl, records)
    for t, fe in w.tables.items():
        feedexcl[t] = fe
    w.load(daughters, xsfeed)
    mpe_bins = []
    native_mpe = False
    if mpe is not None and nuc.mulpre:
        context = getattr(mpe, "context", None) if os.environ.get("HF_NATIVEX_MPE", "1") != "0" \
            else None
        native_mpe = context is not None and w.attach_mpe(nuc, daughters, context, zc, nc)
        if not native_mpe:
            mpe_bins = sorted((k for k in nuc.xspopph2_mb if 1 <= k <= maxex), reverse=True)
    cur = maxex
    for b in mpe_bins:
        w.run(cur, b + 1)
        cur = b - 1
        if (b <= nl and ex[b] <= smin) or XE[b] < popepsA:
            w.run(b, b)
            continue
        w.popexcl[b] = XE[b]
        m = mpe(zc, nc, b)
        dmulti = 0.0
        if m is not None:
            dmulti = m.dmulti
            w.unload(daughters, xsfeed)
            M._apply_mpe(nuc, daughters, b, m, feedexcl, xspartial, xsfeed, zc, nc)
            w.load(daughters, xsfeed)
        w.run(b, b, resume=True, dmulti=dmulti)
    w.run(cur, 1)
    w.unload(daughters, xsfeed)
    if native_mpe:
        w.detach_mpe(nuc, daughters)
    for nex in range(maxex, 0, -1):
        popexcl[nex] = float(w.popexcl[nex])
    for t in range(7):
        fl = np.flatnonzero(w.partf[t])
        if fl.size:
            part = xspartial.setdefault(t, {})
            vals = w.part[t]
            for nex in fl[::-1].tolist():
                part[nex] = part.get(nex, 0.0) + float(vals[nex])
    for nex in np.flatnonzero(w.fisf)[::-1].tolist():
        fisfeed[nex] = fisfeed.get(nex, 0.0) + float(w.fisfeed[nex])
    for t, fe in w.tables.items():
        if not w.created[t] and not len(fe):
            del feedexcl[t]
    return float(w.dpar[2])


def _cascade_only(nuc, zc, nc, popepsA, smin, popexcl, feedexcl, xspartial, records) -> float:
    """A nucleus with no bin to decay: the snapshots and the gamma cascade (the numpy walk's)."""
    from physics.hf.emission import multiple as M

    X = nuc.xspop_mb.numpy()
    XE = nuc.xspopex_mb.numpy()
    ex = nuc.ex_mev.tolist()
    tau = nuc.tau_s.tolist()
    jdis = nuc.jdis.tolist()
    parlev = nuc.parlev.tolist()
    gamdis = 0.0
    for nex in range(nuc.maxex, 0, -1):
        popexcl[nex] = float(XE[nex])
        if nex <= nuc.nlast and ex[nex] <= smin and tau[nex] == 0.0:
            xsjp = float(X[nex, int(jdis[nex]), M._pi(int(parlev[nex]))])
            contrib = {}
            for k, ratio in nuc.branch.get(nex, []):
                intens = xsjp * ratio
                X[k, int(jdis[k]), M._pi(int(parlev[k]))] += intens
                XE[k] += intens
                XE[nex] -= intens
                contrib[k] = intens
            if contrib and records[0]:
                fe = M._table(feedexcl, 0, nuc.maxex + 2, X.shape[0])
                part = xspartial.setdefault(0, {})
                for k, v in contrib.items():
                    fe.add(nex, k, v)
                    part[nex] = part.get(nex, 0.0) + v
                    gamdis += v
    return gamdis
