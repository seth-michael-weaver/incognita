"""NATIVEX2 lever `emit`: the per-energy bookkeeping after the cascade off the autograd graph.

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

Task: NATIVEX2 (the speed work; no physics of its own). Acceptance test:
`tests/hf/test_nx2_emit.py` (every path here against the torch/numpy path it replaces) and the
G-NATIVEX2 closeness gate.

TALYS routines computed here:
    binary.f90:1 (binary), spindis.f90:1 (spindis)
        -- `emission.binary.binary` on numpy views of its tensors, each ejectile's array work in
           C (`nx2_emit_binary_type`, native/nx2_emit.c)
    channels.f90:1 (channels), totalxs.f90:1 (totalxs), residual.f90:1 (residual)
        -- `emission.channels.exclusive_channels` with its per-channel re-reading taken out

`binary` works over seven ejectile types on arrays of a few hundred cells, where torch's
per-operation dispatch (~70 clones, ~100 `where`/`as_tensor` per call) is most of the cost. Here
each type is one C pass over copies of its arrays (the numpy body, the torch body operation for
operation, runs without a build); the run-scoped `BinaryState.sfactor` tensors are written through
their numpy views, so the state persists as on the torch path, and the result holds tensors of the
same shapes, dtypes and aliasing. The Wigner spin distribution uses libm's exp, so the pre-
equilibrium spin spread is held to closeness (~5e-16); everything else is the same to the bit.

`exclusive_channels` is the reference body statement for statement, bit for bit; see its
docstring for what is evaluated less often.

Selection, per call: `HF_NATIVE=0`, `HF_NATIVEX=0`, `HF_NX2=0` or `HF_NX2_EMIT=0` -> the
reference paths; `binary` also keeps its torch body for any input on the autograd graph or off
the CPU.
"""

from __future__ import annotations

import os

import numpy as np
import torch

from physics.hf.core.tensors import DTYPE


def enabled() -> bool:
    """The lever's switch (read at every call): off with `HF_NATIVE`, `HF_NATIVEX`, `HF_NX2` or
    `HF_NX2_EMIT` set to 0.

    TALYS: none (selection only)
    Test: tests/hf/test_nx2_emit.py
    """
    env = os.environ
    return not any(env.get(k, "1") == "0" for k in ("HF_NATIVE", "HF_NATIVEX", "HF_NX2",
                                                    "HF_NX2_EMIT"))


def glue_enabled() -> bool:
    """The `glue` lever's switch (read at every call): off with `HF_NATIVE`, `HF_NATIVEX`,
    `HF_NX2` or `HF_NX2_GLUE` set to 0. It selects the per-energy glue rewrites in `engine`,
    `emission.feeding`, `compound.prepare`, `compound.widths_native` and
    `emission.multiple_native`, each the same numbers as the code it replaces.

    TALYS: none (selection only)
    Test: tests/hf/test_nx2_glue.py
    """
    env = os.environ
    return not any(env.get(k, "1") == "0" for k in ("HF_NATIVE", "HF_NATIVEX", "HF_NX2",
                                                    "HF_NX2_GLUE"))


def _off_graph(tensors) -> bool:
    grad = torch.is_grad_enabled()
    for x in tensors:
        if isinstance(x, torch.Tensor) and (x.device.type != "cpu" or (grad and x.requires_grad)):
            return False
    return True


def _np(x: torch.Tensor) -> np.ndarray:
    return x.detach().numpy()


def _ptr(a: np.ndarray) -> int:
    return a.__array_interface__["data"][0]


def _kernel():
    from physics.hf.native import nx2

    I, D, P = nx2.I64, nx2.DBL, nx2.P
    return nx2.kernel("nx2_emit_binary_type", [I, I, I, I, I, I, I, D, D] + [P] * 9, nx2.INT,
                      lever="emit")


def _binary_type_c(kern, pop, pex, dd, g, ppx, sfglobal, sfac, nl, nmax, mj, do_pe, pespinmodel,
                   popeps_a, pardis) -> bool:
    """`nx2_emit_binary_type` on one type's arrays (pop, pex, ppx, sfac: contiguous copies;
    sfglobal: the state's view), or False where the shapes are not the ones it assumes or a level
    spin index is out of range (the numpy body then runs, and raises as the torch body would)."""
    N, J = pop.shape[0], pop.shape[1]
    jdis = np.ascontiguousarray(_np(g.jdis), dtype=np.float64)
    parlev = np.ascontiguousarray(_np(g.parlev), dtype=np.int64)
    spincut = np.ascontiguousarray(_np(g.spincut), dtype=np.float64)
    ddc = np.ascontiguousarray(dd, dtype=np.float64)
    if (pop.ndim != 3 or pop.shape[2] != 2 or sfglobal.shape[1:] != pop.shape[1:]
            or not sfglobal.flags.c_contiguous or sfglobal.shape[0] < nmax + 1
            or min(N, len(pex), len(ppx), len(spincut)) < nmax + 1
            or min(len(ddc), len(jdis), len(parlev)) < nl + 1):
        return False
    rc = kern(N, J, nl, nmax, mj, int(bool(do_pe)), int(pespinmodel), float(popeps_a),
              float(pardis), _ptr(pop), _ptr(pex), _ptr(ddc), _ptr(jdis), _ptr(parlev),
              _ptr(spincut), _ptr(ppx), _ptr(sfglobal), _ptr(sfac))
    return rc == 0


def binary(inp, state=None, device=None):
    """`emission.binary.binary` on numpy, or None off the lever, on the graph or off the CPU.

    TALYS: binary.f90:1 (binary)
    Test: tests/hf/test_nx2_emit.py
    """
    from physics.hf.emission.binary import (
        PARDIS,
        BinaryResult,
        BinaryState,
        _pi,
        spindis,
    )

    if not enabled() or (device is not None and torch.device(device).type != "cpu"):
        return None
    types = sorted(inp.grids)
    st = state if state is not None else BinaryState()
    ins = [inp.xsbinary_mb]
    for t in types:
        g = inp.grids[t]
        ins += [inp.xspop_mb[t], inp.xspopex_mb[t], inp.xsdirdisc_mb[t], inp.preeqpopex_mb[t],
                g.jdis, g.parlev, g.spincut]
    ins += list(st.sfactor.values())
    for d in (inp.xspopnuc_mb, inp.xsdirdisctot_mb, inp.xspreeqtot_mb, inp.xsgrtot_mb,
              inp.xscompcont_mb):
        ins += list(d.values())
    ins += [inp.xsreacinc_mb, inp.xselasinc_mb, inp.xsdirdiscsum_mb, inp.xspreeqsum_mb,
            inp.xsgrsum_mb, inp.xsracape_mb, inp.popeps_mb, inp.xseps_mb]
    if not _off_graph(ins):
        return None
    tn = torch.from_numpy
    nj = inp.numj
    xspop, xspopex, xspopex0 = {}, {}, {}
    xspopnuc, xspopdir, sfac_out, preeqpopex = {}, {}, {}, {}
    xsdisc, xsdirdisc, xscompdisc, feedbinary = {}, {}, {}, {}
    z = torch.zeros((), dtype=DTYPE)
    xsdisctot = np.zeros(7)
    xscompdisctot = np.zeros(7)
    xsdircont = np.zeros(7)
    xsdirect = np.zeros(7)
    xsconttot = np.zeros(7)
    xscompound = np.zeros(7)
    xsbin = (_np(inp.xsbinary_mb).astype(np.float64, copy=True) if inp.xsbinary_mb is not None
             else np.zeros(8))
    f64 = np.float64
    kern = _kernel()

    for t in types:
        g = inp.grids[t]
        nmax = g.maxex
        nl = min(g.nlast, nmax)
        pop = _np(inp.xspop_mb[t]).copy()
        pex = _np(inp.xspopex_mb[t]).copy()
        dd_t = inp.xsdirdisc_mb[t]
        dd = _np(dd_t)
        nuc = f64(inp.xspopnuc_mb.get(t, 0.0))

        sfglobal = _np(st.get(g.zix, g.nix, nj, device))  # written through: run-scoped
        sfac = sfglobal[: nmax + 1].copy()
        ppx = _np(inp.preeqpopex_mb[t]).copy()
        do_pe = inp.flagpreeq and nmax - nl > 0 and inp.pespinmodel <= 2
        popepsA = inp.popeps_mb / max(5 * nmax, 1)
        done = kern is not None and _binary_type_c(
            kern, pop, pex, dd, g, ppx, sfglobal, sfac, nl, nmax, inp.maxjph + 1, do_pe,
            inp.pespinmodel, popepsA, PARDIS)
        if not done:
            # --- direct discrete addend (binary.f90:194-216): one (J, parity) cell per level
            jidx = _np(g.jdis[: nl + 1]).astype(np.int64)  # int(jdis): truncation
            pidx = np.where(_np(g.parlev[: nl + 1]) == -1, 0, 1)
            term = dd[: nl + 1]
            live = term != 0.0
            lv = np.flatnonzero(live)
            pop[lv, jidx[live], pidx[live]] += term[live]  # one cell per level: no repeat
            pex[: nl + 1] = pex[: nl + 1] + np.where(live, term, 0.0)
        x0 = pex[: nl + 1].copy()  # the pre-equilibrium addend below starts at nl + 1

        ddtot = f64(inp.xsdirdisctot_mb.get(t, 0.0))
        xspopdir[t] = tn(np.array(ddtot))
        xsbin[t + 1] = xsbin[t + 1] + ddtot
        nuc = nuc + ddtot

        # --- pre-equilibrium addend (binary.f90:222-257)
        if inp.flagpreeq:
            if do_pe and not done:
                sl = slice(nl + 1, nmax + 1)
                mj = inp.maxjph + 1
                jj = torch.arange(mj, dtype=DTYPE)
                pexs = pex[sl]
                has = (pexs > popepsA)[:, None, None]
                new = np.where(has, pop[sl, :mj, :]
                               / np.where(pexs > 0, pexs, 1.0)[:, None, None], sfac[sl, :mj, :])
                sfac[sl, :mj, :] = new
                sfglobal[nl + 1: nmax + 1, :mj, :] = new
                wig = _np(spindis(g.spincut[sl][:, None], jj[None, :]) * PARDIS)
                use_sf = (inp.pespinmodel == 1) & (new > 0.0)
                spread = np.where(use_sf, new, wig[:, :, None])
                add = spread * ppx[sl][:, None, None]
                pop[sl, :mj, :] = pop[sl, :mj, :] + add
                pex[sl] = pex[sl] + ppx[sl]
            pt = f64(inp.xspreeqtot_mb.get(t, 0.0))
            gt = f64(inp.xsgrtot_mb.get(t, 0.0))
            nuc = nuc + pt + gt
            xsbin[t + 1] = xsbin[t + 1] + pt + gt

        # --- other total binary cross sections (binary.f90:263-313)
        disc = x0.copy()
        if t == inp.k0 and inp.ltarget <= nl:
            disc[inp.ltarget] = 0.0
        cdisc = disc - dd[: nl + 1]
        if t == inp.k0 and inp.ltarget <= nl:
            cdisc[inp.ltarget] = 0.0
        xscompdisctot[t] = float(tn(cdisc).sum())  # torch's reduction order
        xsdisctot[t] = ddtot + xscompdisctot[t]
        pt = f64(inp.xspreeqtot_mb.get(t, 0.0))
        gt = f64(inp.xsgrtot_mb.get(t, 0.0))
        cc = f64(inp.xscompcont_mb.get(t, 0.0))
        cc = f64(0.0) if cc < inp.xseps_mb else cc  # binary.f90:311
        xsdircont[t] = pt + gt
        xsdirect[t] = ddtot + xsdircont[t]
        xsconttot[t] = cc + xsdircont[t]
        xscompound[t] = xscompdisctot[t] + cc

        # --- binary feeding channels (binary.f90:329-340)
        feed = pex.copy()
        xspop[t], xspopex[t], xspopex0[t] = tn(pop), tn(pex), tn(x0)
        xspopnuc[t], preeqpopex[t], sfac_out[t] = tn(np.array(nuc)), tn(ppx), tn(sfac)
        xsdisc[t], xsdirdisc[t], xscompdisc[t] = tn(disc), dd_t[: nl + 1], tn(cdisc)
        feedbinary[t] = tn(feed)

    # --- totals over the initial compound nucleus (binary.f90:317-326): torch, as the torch path
    k0, lt = inp.k0, inp.ltarget
    ltok = k0 in xspopex0 and lt < xspopex0[k0].shape[0]
    xscompel = xspopex0[k0][lt] if ltok else z.clone()
    xselastot = inp.xselasinc_mb + xscompel
    xsnonel = torch.clamp(inp.xsreacinc_mb - xscompel, min=0.0)
    xscompall = torch.clamp(
        torch.as_tensor(
            inp.xsreacinc_mb - inp.xsdirdiscsum_mb - inp.xspreeqsum_mb - inp.xsgrsum_mb
            - inp.xsracape_mb, dtype=DTYPE),
        min=0.0,
    )
    xscompnonel = torch.clamp(xscompall - xscompel, min=0.0)

    xspop_bine = {t: tn(v.numpy().copy()) for t, v in xspop.items()}
    xspopex_bine = {t: tn(v.numpy().copy()) for t, v in xspopex.items()}
    if ltok:
        a = feedbinary[k0].numpy().copy()
        a[lt] = 0.0
        feedbinary[k0] = tn(a)
        a = xspopex[k0].numpy().copy()
        a[lt] = 0.0
        xspopex[k0] = tn(a)
        a = xspop[k0].numpy().copy()
        a[lt, inp.targetspin2 // 2, _pi(inp.target_parity)] = 0.0
        xspop[k0] = tn(a)
        a = preeqpopex[k0].numpy().copy()
        a[lt] = 0.0
        preeqpopex[k0] = tn(a)

    return BinaryResult(
        xspop_mb=xspop, xspopex_mb=xspopex, xspop_bine_mb=xspop_bine,
        xspopex_bine_mb=xspopex_bine, xspopex0_mb=xspopex0, xspopnuc_mb=xspopnuc,
        xspopdir_mb=xspopdir, preeqpopex_mb=preeqpopex, xsdisc_mb=xsdisc,
        xsdirdisc_mb=xsdirdisc, xscompdisc_mb=xscompdisc, feedbinary_mb=feedbinary,
        sfactor=sfac_out, xsdisctot_mb=tn(xsdisctot), xscompdisctot_mb=tn(xscompdisctot),
        xsdircont_mb=tn(xsdircont), xsdirect_mb=tn(xsdirect), xsconttot_mb=tn(xsconttot),
        xscompound_mb=tn(xscompound), xsbinary_mb=tn(xsbin), xscompel_mb=xscompel,
        xselastot_mb=xselastot, xsnonel_mb=xsnonel, xscompnonel_mb=xscompnonel,
    )


_ZEROS: dict = {}


def _zeros(n: int) -> np.ndarray:
    """A shared read-only zero vector of length n (a channel with nothing feeding it)."""
    z = _ZEROS.get(n)
    if z is None:
        z = _ZEROS[n] = np.zeros(n)
        z.flags.writeable = False
    return z


def _trtrs():
    from scipy.linalg.lapack import dtrtrs

    return dtrtrs


def exclusive_channels(inp, state=None):
    """`emission.channels.exclusive_channels` with its per-channel work cut down, or None off the
    lever. The same statements in the same order; what changes is how often they are evaluated:

    * the isomer list, the floor's isomers and the fission terms of each residual nucleus are
      read out of its dicts once per nucleus, not once per channel;
    * a channel no source table feeds keeps a shared zero vector instead of two new ones (they are
      only ever read);
    * the source tables are looked up once per (nucleus, ejectile);
    * a channel code fixes (Zix, Nix), so it is formed at most once per call: the source search
      is one dict lookup (the index it was formed at, if that index still holds it), and
      `Qexcl(idnum, 0)`, the only entry ever read, is a float per index (`Qexcl(0, 0)` still
      re-assigned at every index, channels.f90:256);
    * the photon recurrence calls LAPACK's `dtrtrs` on the transposed system directly, which is
      exactly what `scipy.linalg.solve_triangular` calls for a C-ordered matrix.

    Every number is the one the reference body computes, to the bit.

    TALYS: channels.f90:1 (channels), totalxs.f90:1 (totalxs), residual.f90:1 (residual)
    Test: tests/hf/test_nx2_emit.py
    """
    if not enabled():
        return None
    from physics.hf.emission import channels as CH

    PARZ, PARN = CH.PARZ, CH.PARN
    st = state if state is not None else CH.ExclusiveState(set(inp.chanopen), inp.idnumfull)
    chanopen = st.chanopen
    nuc = inp.nuclei
    xseps = inp.xseps_mb
    root = nuc[(0, 0)]
    trtrs = _trtrs()

    xsexcl: dict[int, np.ndarray] = {}
    gamexcl: dict[int, np.ndarray] = {}
    idchannel: dict[int, int] = {}
    xschannel: dict[int, float] = {}
    xsgamchannel: dict[int, float] = {}
    xsfischannel: dict[int, float] = {}
    xschaniso: dict[int, dict[int, float]] = {}
    qx: dict[int, float] = {}  # Qexcl(idnum, 0), the only entry ever read
    top0 = root.maxex + 1
    slot: dict[int, int] = {}  # channel code -> the idnum it was formed at
    tables = CH._SourceTables(nuc, top0)
    parskip = inp.parskip
    live_t = [t for t in range(7) if not parskip[t]]
    q00 = root.sep_mev.get(inp.k0, 0.0) + inp.targete_mev
    fis_root = root.fisfeedex_mb.get(top0, 0.0)
    flagfission = inp.flagfission
    numchantot = CH.NUMCHANTOT

    channelsum = 0.0
    xsabs = 0.0
    idnum = -1
    zend = min(CH.NUMZCHAN, inp.maxz, inp.zinit)
    nend = min(CH.NUMNCHAN, inp.maxn, inp.ninit)
    for zix in range(zend + 1):
        for nix in range(nend + 1):
            if (zix, nix) not in nuc:
                continue
            res = nuc[(zix, nix)]
            lim = CH._limits_of(zix, nix, tuple(inp.parinclude), inp.maxchannel)
            keys = CH._channel_keys(zix, nix, lim, inp.maxchannel)
            if not keys:
                continue
            # --- per residual nucleus, once
            nr = res.maxex + 1
            tau = res.tau_s
            # the levels with a lifetime (keys of tau_s holding a non-zero value), as the reference
            # body's `nexout = min(maxex, nlast)..0` and `i = 1..nlast` loops meet them
            taus = [int(k) for k, v in tau.items() if v != 0.0]  # int keys (engine, dumps)
            top_iso = min(res.maxex, res.nlast)
            iso = sorted({k for k in taus if 0 < k <= top_iso} | ({0} if top_iso >= 0 else set()),
                         reverse=True)
            floor_iso = sorted(k for k in taus if 1 <= k <= res.nlast)
            iso_idx = np.array(iso, dtype=np.int64)
            has_edis0 = min(res.nlast, len(res.edis_mev) - 1) >= 0
            edis0 = res.edis_mev.get(0, 0.0)
            # (source ejectile, mother nucleus present, its separation energy)
            srcs = []
            for t in live_t:
                zc, nc = zix - PARZ[t], nix - PARN[t]
                there = (zc, nc) in nuc
                sep = nuc[(zc, nc)].sep_mev.get(t, 0.0) if there else 0.0
                srcs.append((t, _POW[t], there, sep))
            tabs: dict[int, tuple] = {}
            fis_terms = None
            if flagfission:
                fis_terms = []
                for nex in range(res.maxex, 0, -1):
                    pop = res.popexcl_mb.get(nex, 0.0)
                    if pop != 0.0:
                        fis_terms.append((nex, res.fisfeedex_mb.get(nex, 0.0) / pop))
            zero_nr = _zeros(nr)
            root_nuc = zix == 0 and nix == 0

            for key in keys:
                if st.idnumfull and key not in chanopen:
                    continue
                if idnum == numchantot:
                    continue
                i_n, ip, idd_, it, ih, ia = key
                npart = i_n + ip + idd_ + it + ih + ia
                ident = (100000 * i_n + 10000 * ip + 1000 * idd_ + 100 * it + 10 * ih + ia)
                idnum += 1
                idchannel[idnum] = ident
                slot[ident] = idnum  # a code is formed once per call (it fixes Zix, Nix)
                xsfis = 0.0
                # Qexcl(idnum, 0) starts at 0; Qexcl(0, 0) is re-assigned at every idnum
                # (channels.f90:256), which at idnum 0 is this channel's own start value
                qx[idnum] = 0.0
                qx[0] = q00
                qv = qx[idnum]

                # --- source paths (channels.f90:283-318)
                identorg = []  # (t, idorg) for the sources with a mother nucleus
                for t, p10, there, sep in srcs:
                    if t == 0:
                        idorg = idnum  # the photon source is the channel itself
                    else:
                        idd = ident - p10
                        if idd < 0:
                            continue
                        # the idnum formed with code idd, if it still holds it
                        idorg = slot.get(idd)
                        if idorg is None or idorg > idnum or idchannel[idorg] != idd:
                            continue
                    if qv == 0.0 and there:
                        qv = (qv if idorg == idnum else qx[idorg]) - sep
                    if has_edis0:
                        qv = qv - edis0
                    if there:
                        identorg.append((t, idorg))
                qx[idnum] = qv

                if flagfission and root_nuc:
                    xsfis += fis_root

                # --- exclusive cross section per excitation energy (channels.f90:330-391)
                xe = ge = None
                ug = None
                for t, idorg in identorg:
                    got = tabs.get(t)
                    if got is None:
                        got = tabs[t] = tables.of(zix - PARZ[t], nix - PARN[t], t, nr)
                    top, ratio = got
                    if top is not None:
                        if xe is None:
                            xe, ge = np.zeros(nr), np.zeros(nr)
                        xe += top
                        if t == 0:
                            ge += top
                    if ratio is None:
                        continue
                    if t == 0:
                        ug = ratio
                        continue
                    if xe is None:
                        xe, ge = np.zeros(nr), np.zeros(nr)
                    xe += xsexcl[idorg][1 : ratio.shape[0] + 1] @ ratio
                    ge += gamexcl[idorg][1 : ratio.shape[0] + 1] @ ratio
                if ug is not None:
                    if xe is None:
                        xe, ge = np.zeros(nr), np.zeros(nr)
                    A, U = tables.gamma_system(zix, nix, ug, nr)
                    At = A.T  # solve_triangular's call for a C-ordered matrix
                    xe, info = trtrs(At, xe, lower=1, trans=1, unitdiag=1)
                    if info != 0:
                        raise np.linalg.LinAlgError(f"trtrs info {info}")
                    ge, info = trtrs(At, ge + U @ xe, lower=1, trans=1, unitdiag=1)
                    if info != 0:
                        raise np.linalg.LinAlgError(f"trtrs info {info}")
                if xe is None:
                    xe = ge = zero_nr
                xsexcl[idnum], gamexcl[idnum] = xe, ge

                # --- total and per isomer (channels.f90:398-425)
                xsc = 0.0
                xsg = 0.0
                if xe is zero_nr:  # every term is +0.0, and so is every sum
                    chaniso = dict.fromkeys(iso, 0.0)
                else:
                    chaniso = {}
                    for nexout, v, w in zip(iso, xe[iso_idx].tolist(), ge[iso_idx].tolist()):
                        chaniso[nexout] = v
                        xsc += v
                        xsg += w
                xschaniso[idnum] = chaniso

                channelsum += xsc
                if i_n == 0:
                    xsabs += xsc

                # non-threshold floor (channels.f90:435-445)
                if qv > 0.0 and xsc <= xseps:
                    xsc = xseps
                    xsg = xseps
                    chaniso[0] = xseps
                    for i in floor_iso:
                        chaniso[0] = 0.5 * xseps
                        chaniso[i] = 0.5 * xseps

                # exclusive fission (channels.f90:459-475)
                if flagfission:
                    for nex, term in fis_terms:
                        xsfis += term * float(xe[nex])
                    channelsum += xsfis
                    xsabs += xsfis
                xschannel[idnum] = xsc
                xsgamchannel[idnum] = xsg
                xsfischannel[idnum] = xsfis

                # --- idnum give-back (channels.f90:630-637)
                if (xsc >= xseps and not st.idnumfull) or npart == 0:
                    chanopen.add(key)
                if xsc < xseps and npart > 1 and key not in chanopen:
                    idnum -= 1
                if len(chanopen) == numchantot - 10:
                    st.idnumfull = True
                if idnum < 0:
                    continue
                if xschannel[idnum] < 0.0:
                    xschannel[idnum] = xseps

    return CH._channel_result(inp, nuc, xseps, idnum, idchannel, xschannel, xsgamchannel,
                              xsfischannel, xschaniso, {i: {0: qx[i]} for i in range(idnum + 1)},
                              channelsum, xsabs)


_POW = (0,) + tuple(10 ** (6 - t) for t in range(1, 7))
