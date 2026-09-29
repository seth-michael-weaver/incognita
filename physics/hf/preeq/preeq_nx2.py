"""NATIVEX2 lever `preeq`: the exciton-model set-up off the autograd graph.

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

Task: NATIVEX2 (the speed work; no physics of its own). Acceptance test:
`tests/hf/test_nx2_preeq.py` (every path here against the numpy/torch path it replaces) and the
G-NATIVEX2 closeness gate.

TALYS routines computed here:
    phdens2.f90:1 (phdens2), finitewell.f90:1 (finitewell)
        -- `density.particle_hole._phdens2_arr` (`nx2_preeq_phdens2`, native/nx2_preeq.c)
    stripping.f90:1 (stripping)
        -- the exciton sums of `preeq.complex.stripping`, one density call per ejectile
    preeqcorrect.f90:1 (preeqcorrect)
        -- `preeq.exciton.preeq_correct` on numpy arrays, the bin searches batched

Selection, per call: `HF_NATIVE=0`, `HF_NATIVEX=0`, `HF_NX2=0` or `HF_NX2_PREEQ=0` -> the
numpy/torch paths; no `libnx2` build -> the C density is skipped (the numpy rewrites still run).
The callers only come here off the autograd graph (grad mode off, or no input requiring grad).
"""

from __future__ import annotations

import os

import numpy as np
import torch

_NDIM = 4
_DTYPES = (np.int64, np.int64, np.int64, np.int64, np.float64, np.float64, np.float64,
           np.float64, np.uint8, np.float64)


def enabled() -> bool:
    """The lever's switch (read at every call): off with `HF_NATIVE`, `HF_NATIVEX`, `HF_NX2` or
    `HF_NX2_PREEQ` set to 0.

    TALYS: none (selection only)
    Test: tests/hf/test_nx2_preeq.py
    """
    env = os.environ
    return not any(env.get(k, "1") == "0" for k in ("HF_NATIVE", "HF_NATIVEX", "HF_NX2",
                                                    "HF_NX2_PREEQ"))


def off_graph(*xs) -> bool:
    """The lever is on and no tensor among `xs` is on the autograd graph or off the CPU.

    TALYS: none (selection only)
    Test: tests/hf/test_nx2_preeq.py
    """
    if not enabled():
        return False
    grad = torch.is_grad_enabled()
    for x in xs:
        if isinstance(x, torch.Tensor) and (x.device.type != "cpu" or (grad and x.requires_grad)):
            return False
    return True


def _kernel():
    from physics.hf.native import nx2, setup_c

    # CENGSETUP: the same source compiled into libsetup (-O3, vector flags) when built
    return setup_c.swap("nx2_preeq_phdens2", nx2.kernel(
        "nx2_preeq_phdens2", [nx2.P] * 12 + [nx2.DBL, nx2.DBL, nx2.P, nx2.I64, nx2.P, nx2.I64,
                                             nx2.I64, nx2.P], nx2.INT, lever="preeq"))


def phdens2_arr(ppi, hpi, pnu, hnu, gsp, gsn, ex, ewell, surfwell, ap2, efermi_mev):
    """`density.particle_hole._phdens2_arr` in C, or None when the kernel is not available (or
    the arrays have more than four axes). Arguments as `_phdens2_arr` takes them (numpy arrays or
    scalars, any broadcastable shapes); returns the float64 array of the broadcast shape. Nothing
    is broadcast in memory: the kernel steps through each input with its own strides.

    TALYS: phdens2.f90:1 (phdens2), finitewell.f90:1 (finitewell)
    Test: tests/hf/test_nx2_preeq.py
    """
    fn = _kernel()
    if fn is None:
        return None
    from physics.hf.density.particle_hole import _NFAC_NP, NUMEXC, PHDENS_FLOOR

    args = [np.asarray(a, dtype=d) for a, d in zip(
        (ppi, hpi, pnu, hnu, gsp, gsn, ex, ewell, surfwell, ap2), _DTYPES)]
    try:
        shape = np.broadcast_shapes(*(a.shape for a in args))
    except ValueError:
        return None
    nd = len(shape)
    if nd > _NDIM:
        return None
    pad = _NDIM - nd
    full = (1,) * pad + tuple(shape)
    strides = np.zeros((10, _NDIM), dtype=np.int64)
    for i, a in enumerate(args):
        if any(s < 0 for s in a.strides):
            a = args[i] = np.ascontiguousarray(a)
        off = _NDIM - a.ndim
        for d in range(a.ndim):
            if a.shape[d] != 1:
                strides[i, off + d] = a.strides[d] // a.itemsize
    hmax = max(int(args[1].max()) + int(args[3].max()), 1)
    tab = _tab(hmax)
    out = np.empty(shape)
    fn(_ptr(np.asarray(full, dtype=np.int64)), _ptr(strides), *(_ptr(a) for a in args),
       float(efermi_mev), PHDENS_FLOOR, _ptr(_NFAC_NP),
       len(_NFAC_NP) - 1, _ptr(tab), 2 * NUMEXC + 2, hmax, _ptr(out))
    return out


def _ptr(a: np.ndarray) -> int:
    return a.__array_interface__["data"][0]


_TABS: dict = {}


def _tab(hmax: int) -> np.ndarray:
    """``(-1)^k ncomb(h, k)`` for k = 1..hmax, h = 0..2 numexc + 1 (pure constants)."""
    t = _TABS.get(hmax)
    if t is None:
        from physics.hf.density.particle_hole import _signed_ncomb_table

        t = _TABS[hmax] = np.ascontiguousarray(_signed_ncomb_table(hmax, "cpu").numpy(),
                                               dtype=np.float64)
    return t


def stripping_sum(terms, xnt, gsp, gsn, eres, ewell, gsp_cn, gsn_cn):
    """The two exciton sums of `stripping` (stripping.f90:158-172) in one density call, or None
    off the lever / on the graph / without the kernel. `terms` lists `(power, ppi, hpi, pnu, hnu)`
    in TALYS's order, `power` None for the second sum's unweighted terms; `xnt` (C, 1), `gsp`,
    `gsn` (1, 1), `eres`, `ewell` (C, E), `gsp_cn`, `gsn_cn` (C, 1) as `stripping` has them.
    Returns the (C, E) tensor `acc`, added term by term in TALYS's order.

    TALYS: stripping.f90:1 (stripping)
    Test: tests/hf/test_nx2_preeq.py
    """
    if not off_graph(xnt, gsp, gsn, eres, ewell, gsp_cn, gsn_cn) or _kernel() is None:
        return None
    from physics.hf.density.particle_hole import EFERMI_MEV, _apauli2_arr

    k = len(terms)
    idx = [np.array([t[j] for t in terms], dtype=np.int64).reshape(k, 1, 1) for j in (1, 2, 3, 4)]
    ap = _apauli2_arr(*idx, gsp_cn.numpy(), gsn_cn.numpy())  # (K, C, 1), the CN Apauli2 table
    om = phdens2_arr(*idx, gsp.numpy(), gsn.numpy(), eres.numpy(), ewell.numpy(), False, ap,
                     EFERMI_MEV)
    if om is None:
        return None
    x = xnt.numpy()
    acc = np.zeros(np.broadcast_shapes(eres.shape, x.shape))
    for kk, t in enumerate(terms):
        acc = acc + (om[kk] if t[0] is None else x ** t[0] * om[kk])
    return torch.from_numpy(acc)


def _locate_many(xs32: np.ndarray, ib: int, ie: int, x: np.ndarray, xx: np.ndarray) -> np.ndarray:
    """`core.grids.locate_scalar(xx, ib, ie, x_i)` for every x_i, by one sorted search (the
    bisection's result on a non-decreasing float32 grid); any other grid, or a NaN, takes the
    scalar search."""
    from physics.hf.core.grids import locate_scalar

    if ib > ie:
        return np.zeros(len(x), dtype=np.int64)
    x32 = x.astype(np.float32)
    seg = xs32[ib:ie + 1]
    if np.isnan(x32).any() or (len(seg) > 1 and not (np.diff(seg) >= 0).all()):
        return np.array([locate_scalar(xx, ib, ie, float(v)) for v in x], dtype=np.int64)
    jl = np.searchsorted(seg, x32, side="right").astype(np.int64) + (ib - 1)
    jl = np.where(x32 == xs32[ie], ie - 1, jl)
    return np.where(x32 == xs32[ib], ib, jl)


def preeq_correct(spectra: dict, inp, disc) -> dict | None:
    """`preeq.exciton.preeq_correct` on numpy views of the cloned spectra, or None off the lever
    or on the graph. The level loop is TALYS's; the `locate` calls of each (case, ejectile) are
    one sorted search and the `xs1` products one array expression (the same float64 operations
    per level).

    TALYS: preeqcorrect.f90:1 (preeqcorrect)
    Test: tests/hf/test_nx2_preeq.py
    """
    keys = ("xspreeq", "xsstep", "xspreeqps", "xspreeqki", "xspreeqbu") + (
        ("xsstep2",) if "xsstep2" in spectra else ())
    if not off_graph(*(spectra[k] for k in keys), inp.egrid_mev, inp.deltae_mev, disc.etop_mev):
        return None
    C, E = inp.C, inp.E
    out = {k: spectra[k].detach().clone() for k in keys}
    a = {k: v.numpy() for k, v in out.items()}
    xp, xst = a["xspreeq"], a["xsstep"]
    xst2 = a.get("xsstep2")
    nlmax = max((len(r) for row in disc.eoutdis_mev for r in row if r is not None), default=1)
    xsdisc = np.zeros((C, 7, nlmax))
    k0 = inp.k0
    xseps = 1.0e-7  # A0_talys_mod.f90 xseps
    egall = inp.egrid_mev.detach().cpu().numpy()
    deall = inp.deltae_mev.detach().numpy()
    etopall = disc.etop_mev.detach().numpy()
    for c in range(C):
        eg = egall[c]
        eg32 = eg.astype(np.float32)
        for t in range(7):
            b, e_end = disc.ebegin[t], disc.eend[c][t]
            if b >= e_end:
                continue
            nd = disc.nendisc[c][t]
            esd_all = disc.eoutdis_mev[c][t]
            NL = disc.nlast[t]
            if esd_all is not None:
                esd_l = [float(v) for v in esd_all[:NL + 2]]
                dd = disc.xsdirdisc_mb[c][t]
                lev, e1, e2 = [], [], []
                for i in range(NL + 1):
                    if dd[i] != 0.0:
                        continue
                    esd = esd_l[i]
                    if esd < 0.0:  # preeqcorrect.f90:57 (goto 100)
                        break
                    if i == 0 or (t == k0 and i == 1):
                        esd2 = esd_l[0]
                    else:
                        esd2 = 0.5 * (esd + esd_l[i - 1])
                    if i == NL:
                        esd1 = esd_l[NL]
                    elif esd_l[i + 1] > 0.0:
                        esd1 = 0.5 * (esd + esd_l[i + 1])
                    else:
                        esd1 = 0.0
                    lev.append(i)
                    e1.append(esd1)
                    e2.append(esd2)
                if lev:
                    li = np.array(lev)
                    if t == k0:
                        xsdisc[c, t, li] = xseps
                    else:
                        a1, a2 = np.array(e1), np.array(e2)
                        n1 = _locate_many(eg32, nd, e_end, a1, eg)
                        n2 = _locate_many(eg32, nd, e_end, a2, eg)
                        row = xp[c, t]
                        xsdisc[c, t, li] = 0.5 * (row[n1] + row[n2]) * (a2 - a1)
                    if lev[-1] == NL:
                        elast = esd_l[NL]
                        rb = (float(etopall[c, nd]) - elast) / float(deall[c, nd])
                        if abs(rb) > 1.0:
                            rb = 0.0
                        if t != k0:
                            xsdisc[c, t, NL] = xp[c, t, nd] * rb
                        for key in ("xspreeq", "xspreeqps", "xspreeqki", "xspreeqbu"):
                            a[key][c, t, nd] = a[key][c, t, nd] * (1.0 - rb)
                        xst[c, t, 1:, nd] = xst[c, t, 1:, nd] * (1.0 - rb)
                        if xst2 is not None:  # preeqcorrect.f90:141-147
                            xst2[c, :, t, nd] = xst2[c, :, t, nd] * (1.0 - rb)
            hi = slice(nd + 1, min(e_end, E - 1) + 1)
            for key in ("xspreeq", "xspreeqps", "xspreeqki", "xspreeqbu"):
                a[key][c, t, hi] = 0.0
            xst[c, t, 1:, hi] = 0.0
            if xst2 is not None:  # preeqcorrect.f90:170-176
                xst2[c, :, t, hi] = 0.0
    xd = torch.from_numpy(xsdisc)
    out["xspreeqdisc"] = xd
    out["xspreeqdisctot"] = xd.sum(-1)
    out["xspreeqdiscsum"] = xd.sum((-1, -2))
    return out


def transition_rates(inp, states, emis: dict, m2: dict, nexcbins: int, numeric: bool,
                     tph: float) -> dict | None:
    """The four transition rates of `preeq.exciton.transition_rates` (C, S) in one C call
    (`nx2_preeq_transition`), or None off the lever, on the graph, without the kernel or without
    the two-component matrix elements. `numeric` is preeqmode 2 (bin integrals, the closed form
    at n = 1); otherwise the closed form everywhere.

    TALYS: lambdapiplus.f90:1, lambdanuplus.f90:1, lambdapinu.f90:1, lambdanupi.f90:1
    Test: tests/hf/test_nx2_preeq.py
    """
    keys = ("M2pipi", "M2nunu", "M2pinu", "M2nupi")
    if not all(k in m2 for k in keys):
        return None
    u, edepth, surf = emis["u_cn"], emis["edepth"], emis["surfwell"]
    if not off_graph(u, edepth, inp.gp_cn, inp.gn_cn, *(m2[k] for k in keys)):
        return None
    from physics.hf.native import nx2, setup_c

    fn = setup_c.swap("nx2_preeq_transition", nx2.kernel(
        "nx2_preeq_transition", [nx2.I64, nx2.I64] + [nx2.P] * 13 + [
            nx2.I64, nx2.I64, nx2.DBL, nx2.DBL, nx2.DBL, nx2.P, nx2.I64, nx2.P, nx2.I64, nx2.I64,
            nx2.P], nx2.INT, lever="preeq"))
    if fn is None:
        return None
    from physics.hf.density.particle_hole import _NFAC_NP, EFERMI_MEV, NUMEXC, PHDENS_FLOOR

    C, S = int(u.shape[0]), states.size
    cs = (C, S)
    st = [np.ascontiguousarray(x.numpy(), dtype=np.int64)
          for x in (states.ppi, states.hpi, states.pnu, states.hnu)]
    d = lambda x, shape: np.ascontiguousarray(  # noqa: E731
        np.broadcast_to(np.asarray(x.detach().numpy(), dtype=np.float64), shape))
    gp, gn = d(inp.gp_cn.reshape(-1), (C,)), d(inp.gn_cn.reshape(-1), (C,))
    arrs = [d(u, cs), d(edepth, cs),
            np.ascontiguousarray(np.broadcast_to(surf.numpy(), cs), dtype=np.uint8)]
    m2a = [d(m2[k], cs) for k in keys]
    hmax = max(int(st[1].max()) + int(st[3].max()) + 3, 3)
    tab = _tab(hmax)
    out = np.empty((4, C, S))
    fn(C, S, *(_ptr(a) for a in st), _ptr(gp), _ptr(gn), *(_ptr(a) for a in arrs),
       *(_ptr(a) for a in m2a), int(bool(numeric)), int(nexcbins), float(tph), EFERMI_MEV,
       PHDENS_FLOOR, _ptr(_NFAC_NP), len(_NFAC_NP) - 1, _ptr(tab), 2 * NUMEXC + 2, hmax,
       _ptr(out))
    t = torch.from_numpy(out)
    return {"lambdapiplus": t[0], "lambdanuplus": t[1], "lambdapinu": t[2], "lambdanupi": t[3]}
