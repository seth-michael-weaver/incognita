"""The capture fast path on a (nuclide, incident energy) batch axis, for one GPU.

Task: SPEEDG (gate G-GPU: the 482 x 64 capture sweep on the laptop RTX 5050 in <= 10 s,
identical to the CPU sweep at <= 1e-12). No physics of its own: every number is produced by the
statements of `capture_fast_batch.capture_xs` (itself identical to `capture_fast.capture_xs`),
rearranged so that all points of a sweep go through each statement at once.

**The split.** `capture_gpu_setup.setup_point` runs, on CPU and once per point, everything that
does not read the photon strength function: the grids, level densities, particle transmissions
and widths, the incident channels and the Moldauer weight sums of the particle exits. This module
evaluates what does: the photon strength (`psf`, the SMLO E1 tables with their temperature axis,
M1 with scissors and upbend, E2 and M2 Lorentzians), the primary photon transmissions and widths,
Moldauer's integral (whose total width contains the photon width), the photon population of the
compound nucleus (`target_batch._feed_type`), and the decay of the compound nucleus's bins
(`capture_fast_batch._photon_feeding` and `_cascade_cn`, with `emission.multiple.gamma_cascade`
for the discrete levels). A fit (FIT1) changes only the photon strength, so the set-up is paid
once per design, not once per call.

**The batch axis.** Every point of the sweep has its own excitation grid, cells and channels;
they are padded to the batch's largest and masked. Padding enters only as exact zeros (a zero
transmission, weight or population) or behind `torch.where`, so a padded term adds 0.0. The
cascade runs mother bin by mother bin (`nex` from the top down, as `multiple.f90`), every point
at once; a point whose bin `nex` is a discrete level cascades, is skipped, or decays according to
its own mask, exactly as the reference's branch would.

**Rounding.** The reference sums over residual states, cells, l' and nodes in the order its
einsums and CPU reductions happen to use; the GPU groups the same non-negative terms differently.
Results therefore agree to rounding (SPEED2: summation order moves the last bits), not bitwise;
the gate is 1e-12 relative. Where the reference's order is cheap to keep it is kept (the widths
of the seven exit types are added in the reference's order, the isomers are added one by one).

Identity with the CPU sweep is `tests/hf/test_capture_gpu.py`.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
import torch
from torch import Tensor

from physics.hf.compound.prepare import NUMJ

F64 = torch.float64
NUMGAMQRPA = 300
L = 3  # gammax + 1


def _twopi() -> float:
    from physics.hf.core.constants import talys_constants

    return float(talys_constants()["twopi"])


def _pi2h2c2() -> float:
    from physics.hf.gamma.parameters import PI2H2C2

    return float(PI2H2C2)


# ------------------------------------------------------------------------------ packing


@dataclass
class Packed:
    """Every point of a batch on the device, padded (see the module docstring)."""

    n: int  # points
    index: list  # point -> (target position, energy index)
    nuc: Tensor  # (P,) target position, for the photon-strength parameters
    t: dict  # name -> tensor (P, ...)
    g: dict  # name -> tensor (Nn, ...) photon-strength parameters per target
    dims: dict
    device: torch.device
    meta: dict


def _pad(arrs, shape, dtype, fill=0):
    out = np.full((len(arrs),) + tuple(shape), fill, dtype=dtype)
    for i, a in enumerate(arrs):
        a = np.asarray(a)
        sl = (i,) + tuple(slice(0, min(s, m)) for s, m in zip(a.shape, shape, strict=True))
        out[sl] = a[tuple(slice(0, min(s, m)) for s, m in zip(a.shape, shape, strict=True))]
    return out


def jcut_of(pt: dict) -> int:
    """The residual/mother spin axis length a point needs: every J with a non-zero population.

    A continuum bin's population lives at J <= maxJ (its rho0 is masked there), a discrete level's
    at its own spin; the compound cells of the primary decay are a separate axis."""
    ct, cs = pt["ct"], pt["cs"]
    need = 1
    nz = np.nonzero(ct["rho_c0"].any(axis=(0, 2)))[0]
    if nz.size:
        need = max(need, int(nz[-1]) + 1)
    rg = cs["rhogrid"]
    cont = np.arange(cs["R"]) > cs["nl"]
    mj = np.where(cont, cs["maxj"], 0)
    need = max(need, int(mj.max()) + 1)
    lev = np.arange(cs["R"]) <= cs["ng"]
    need = max(need, int(np.where(lev, cs["jdis_int"], 0).max()) + 1)
    ok = ct["okd0"]
    if ok.any():
        need = max(need, int(ct["ird0"][ok].max()) + 1)
    del rg
    return min(need, NUMJ + 1)


def _rb_min(tt: dict, R: int) -> float:
    """The smallest photon-exit Rboundary of any (continuum mother bin, continuum residual row)."""
    ex, dex, nl = tt["ex"], tt["dex"], tt["nl"]
    out = math.inf
    for nex in range(1, R):
        exr, dh = ex[:, :nex], 0.5 * dex[:, :nex]
        ex0plus = (ex[:, nex] + 0.5 * dex[:, nex])[:, None]
        ex0min = (ex[:, nex] - 0.5 * dex[:, nex])[:, None]
        emax = ex0plus - (exr - dh)
        emin = ex0min - (exr + dh)
        half = 0.5 * (emax - emin)
        half = torch.where(half != 0.0, half, torch.ones_like(half))
        rb = torch.where(emin < 0.0, torch.where(0.5 * (emin + emax) > 0.0,
                                                 1.0 - 0.5 * (emin / half) ** 2,
                                                 0.5 * (emax / half) ** 2), torch.ones_like(half))
        use = ((torch.arange(nex, device=ex.device)[None, :] > nl[:, None])
               & (tt["mode"][:, nex, None] == 2))
        if bool(use.any()):
            out = min(out, float(torch.where(use, rb, torch.inf).min()))
    return out


def _channel_buckets(cts: list[dict], K: int, device, max_elements: int = 16_000_000) -> list:
    """Moldauer's open particle exit channels, as (cell rows, channels) blocks.

    Most points have a handful of open channels and a few have hundreds, so one (P, K, channels)
    tensor would be almost all padding. Rows are the (point, cell) pairs; points are grouped by
    their channel count (padded to the next power of two, padding T = 0 adds an exact -0.0 to
    the node sum), and each block stays under `max_elements` row x node x channel entries."""
    nch = np.array([c["t_nz"].shape[0] for c in cts])
    edges = 2 ** np.ceil(np.log2(np.maximum(nch, 1))).astype(np.int64)
    out = []
    for w in sorted(set(edges.tolist())):
        pts = np.flatnonzero(edges == w)
        rows = [(p, k) for p in pts for k in range(len(cts[p]["J2"]))]
        step = max(1, max_elements // (32 * w))
        for r0 in range(0, len(rows), step):
            blk = rows[r0: r0 + step]
            rp = np.array([b[0] for b in blk], dtype=np.int64)
            rk = np.array([b[1] for b in blk], dtype=np.int64)
            tb = np.zeros((len(blk), w))
            rb = np.zeros((len(blk), w))
            for i, (p, k) in enumerate(blk):
                n = nch[p]
                tb[i, :n] = cts[p]["t_nz"]
                rb[i, :n] = cts[p]["r_exit"][k]
            out.append(dict(p=torch.as_tensor(rp, device=device),
                            k=torch.as_tensor(rk, device=device),
                            t=torch.as_tensor(tb, device=device),
                            r=torch.as_tensor(rb, device=device)))
    return out


def pack(targets: list[dict], device="cuda", jcut: int | None = None) -> Packed:
    """Pad and move every in-domain point of `targets` (from `setup_target`) to `device`."""
    pts, index, nuc = [], [], []
    gam = []
    for ti, tgt in enumerate(targets):
        gam.append(tgt["gamma"])
        for ei, pt in sorted(tgt["points"].items()):
            pts.append(pt)
            index.append((ti, ei))
            nuc.append(ti)
    P = len(pts)
    if P == 0:
        raise ValueError("no points")
    cts = [p["ct"] for p in pts]
    css = [p["cs"] for p in pts]
    J = jcut or max(jcut_of(p) for p in pts)
    R = max(c["R"] for c in css)
    K = max(len(c["J2"]) for c in cts)
    NA = max(c["tinc"].shape[1] for c in cts)
    NCH = max(1, max(c["t_nz"].shape[0] for c in cts))
    ND0 = max(c["rho_d0"].shape[0] for c in cts)
    NB = max(1, max(len(c["bins"]) for c in css))
    NT = max(1, max(len(c["widths"]) for c in css))
    NBR = max(c["br_k"].shape[1] for c in css)
    for c in cts:
        if c["wfcfactor"] != 1:
            raise ValueError("WFCfactor != 1")
    for c in css:
        lev = np.arange(c["R"]) <= c["ng"]
        if not np.all(np.isin(c["parlev"][lev][1:], (-1, 1))) and c["ng"] > 0:
            raise ValueError("a discrete level without parity")
        if np.any((c["jdis2"] // 2 != c["jdis_int"]) & lev):
            raise ValueError("level spin index mismatch")
    t = {}
    # primary decay
    t["eg0"] = _pad([c["eg0"] for c in cts], (R,), np.float64)
    t["row0"] = _pad([np.ones(c["nrow0"], bool) for c in cts], (R,), bool)
    t["efs0"] = np.array([c["efs0"] for c in cts])
    t["fn1_0"] = np.array([c["fn1_0"] for c in cts])
    t["rho_c0"] = _pad([c["rho_c0"] for c in cts], (R, J, 2), np.float64)
    t["rho_d0"] = _pad([c["rho_d0"] for c in cts], (ND0,), np.float64)
    t["ird0"] = _pad([np.clip(c["ird0"], 0, J - 1) for c in cts], (ND0,), np.int64)
    t["pd0"] = _pad([c["pd0"] for c in cts], (ND0,), np.int64)
    t["okd0"] = _pad([c["okd0"] & (c["ird0"] < J) for c in cts], (ND0,), bool)
    for c in cts:
        if np.any(c["okd0"] & (c["ird0"] >= J) & (c["rho_d0"] != 0.0)):
            raise ValueError("J cut drops a populated discrete level")
    t["jd2_0"] = _pad([c["jd2_0"] for c in cts], (ND0,), np.int64)
    t["J2"] = _pad([c["J2"] for c in cts], (K,), np.int64)
    t["cell"] = _pad([np.ones(len(c["J2"]), bool) for c in cts], (K,), bool)
    t["pidx"] = _pad([c["pidx"] for c in cts], (K,), np.int64)
    t["dpart"] = _pad([c["dpart"] for c in cts], (K, 6), np.float64)
    t["tinc"] = _pad([c["tinc"] for c in cts], (K, NA), np.float64)
    t["feedsum"] = _pad([c["feedsum"] for c in cts], (K,), np.float64)
    t["cn"] = np.array([c["cn"] for c in cts])
    t["wfc"] = np.array([c["wfc"] for c in cts])
    # the compound nucleus's decay
    for k in ("nl", "ng", "ntop", "odd"):
        t[k] = np.array([c[k] for c in css], dtype=np.int64)
    for k in ("discfactor", "sep0", "sn", "fn1", "popeps_a", "popeps_mb"):
        t[k] = np.array([c[k] for c in css], dtype=np.float64)
    t["ex"] = _pad([c["ex"] for c in css], (R,), np.float64)
    t["dex"] = _pad([c["dex"] for c in css], (R,), np.float64)
    t["maxj"] = _pad([c["maxj"] for c in css], (R,), np.int64)
    t["jdis2"] = _pad([c["jdis2"] for c in css], (R,), np.int64)
    t["jdis_int"] = _pad([np.clip(c["jdis_int"], 0, J - 1) for c in css], (R,), np.int64)
    t["parlev"] = _pad([c["parlev"] for c in css], (R,), np.int64)
    t["iso"] = _pad([c["iso"] for c in css], (R,), bool)
    t["rhogrid"] = _pad([c["rhogrid"] for c in css], (R, J, 2), np.float64)
    t["mode"] = _pad([c["mode"] for c in css], (R,), np.int64)
    t["br_k"] = _pad([c["br_k"] for c in css], (R, NBR), np.int64)
    t["br_r"] = _pad([c["br_r"] for c in css], (R, NBR), np.float64)
    bidx = np.zeros((P, R), dtype=np.int64)
    W = np.zeros((P, NB, J, 2, NT))
    p5 = np.ones((P, NB, J, 2), dtype=bool)
    peb = np.ones((P, NB))
    for p, c in enumerate(css):
        bidx[p, c["bins"]] = np.arange(len(c["bins"]))
        peb[p, : len(c["bins"])] = c["popeps_b"]
        for j, (ty, w) in enumerate(c["widths"]):
            jj = min(J, w.shape[1])
            W[p, : w.shape[0], :jj, :, j] = w[:, :jj]
            if ty <= 5:
                p5[p, : w.shape[0], :jj] &= w[:, :jj] == 0.0
    t["bidx"], t["W"], t["part5zero"], t["popeps_b"] = bidx, W, p5, peb
    tt = {}
    for k, v in t.items():
        tt[k] = torch.as_tensor(v).to(device)
    tt["channels"] = _channel_buckets(cts, K, device)
    # rhogrid where compound.f90 reads it for a continuum residual row (maxJ and the Irspin2 rule)
    rows = torch.arange(R, device=device)
    cont = rows[None, :] > tt["nl"][:, None]
    Jr = torch.arange(J, device=device)
    irs2 = 2 * Jr[None, :] + (tt["odd"][:, None] % 2)
    mj = tt["maxj"][:, :, None]
    keep = (Jr[None, None, :] <= mj) & (irs2[:, None, :] <= 2 * mj) & cont[:, :, None]
    tt["rhogrid_c"] = torch.where(keep[..., None], tt["rhogrid"], 0.0)
    del tt["rhogrid"]
    # compound.f90's rho0 >= 1e-20 cut on Rboundary * rhogrid: if the smallest non-zero rhogrid
    # times the smallest continuum Rboundary of any mother bin clears it, the cut never fires and
    # rho0 factorises (see `_forward`)
    rg = tt["rhogrid_c"]
    rgm_min = float(torch.where(rg > 0.0, rg, torch.inf).min())
    rb_min = _rb_min(tt, R)
    meta = dict(nl_min=int(t["nl"].min()), nl_max=int(min(t["nl"].max(), R - 1)),
                factorised=bool(rgm_min * rb_min >= 1.0e-20), rgm_min=rgm_min, rb_min=rb_min,
                mode_any1=[bool((t["mode"][:, n] == 1).any()) for n in range(R)],
                mode_any2=[bool((t["mode"][:, n] == 2).any()) for n in range(R)])
    # photon-strength parameters per target
    g = {}
    ok = [x for x in gam if x is not None]
    if len(ok) != len(gam):
        raise ValueError("a target with points has no photon-strength pack")
    tq = ok[0]["tq"]
    for x in ok:
        if not np.array_equal(x["tq"], tq):
            raise ValueError("temperature grids differ")
        if x["m2"][0] != x["m1"][0] * 8.0e-4:
            raise ValueError("M2 strength is not the M1 default chain")
    g["tq"] = torch.as_tensor(tq, dtype=F64, device=device)
    g["e_raw"] = torch.as_tensor(np.stack([x["e_raw"] for x in ok]), dtype=F64, device=device)
    g["f_raw"] = torch.as_tensor(np.stack([x["f_raw"] for x in ok]), dtype=F64, device=device)
    for k in ("ftable", "wtable", "S", "delta", "alev", "beta2"):
        g[k] = torch.as_tensor([x[k] for x in ok], dtype=F64, device=device)
    for k in ("m1", "e2", "m2", "scissors", "upbend"):
        g[k] = torch.as_tensor([x[k] for x in ok], dtype=F64, device=device)  # (Nn, 3)
    dims = dict(P=P, R=R, J=J, K=K, NA=NA, NCH=NCH, blocks=len(tt["channels"]), ND0=ND0, NB=NB,
                NT=NT, NBR=NBR,
                Nn=len(targets))
    # DIRECTCAP: direct radiative capture (racap) per point, 0 unless INCOGNITA_DIRECT_CAPTURE
    from physics.hf.direct.racapcalc import direct_capture_mb, mode

    dc = np.zeros(P)
    if mode() != "off":
        for p_i, (ti, ei) in enumerate(index):
            tg = targets[ti]
            dc[p_i] = direct_capture_mb(tg["Z"], tg["A"], tg["energies"])[ei]
    tt["dc_mb"] = torch.as_tensor(dc, dtype=F64, device=device)
    return Packed(n=P, index=index, nuc=torch.as_tensor(nuc, device=device), t=tt, g=g,
                  dims=dims, device=torch.device(device), meta=meta)


def theta_default(pk: Packed) -> Tensor:
    """(Nn, 3): ftable(E1), wtable(E1), sgr(M1) at their TALYS defaults."""
    return torch.stack([pk.g["ftable"], pk.g["wtable"], pk.g["m1"][:, 0]], dim=1)


# ------------------------------------------------------------------------------ photon strength


def _interp(e, eb, ee, gamb, game):
    """`gamma.strength._interp`."""
    both = (gamb > 0.0) & (game > 0.0)
    safe_b = torch.where(both, gamb, torch.ones_like(gamb))
    safe_e = torch.where(both, game, torch.ones_like(game))
    frac = (e - eb) / (ee - eb)
    logv = torch.pow(10.0, torch.log10(safe_b) + frac * (torch.log10(safe_e) - torch.log10(safe_b)))
    lin = gamb + frac * (game - gamb)
    return torch.where(both, logv, lin)


def _interp_de(e, eb, ee, gamb, game, deb, dee):
    """`_interp` and its derivative when the interval ends eb, ee move by deb, dee."""
    both = (gamb > 0.0) & (game > 0.0)
    safe_b = torch.where(both, gamb, torch.ones_like(gamb))
    safe_e = torch.where(both, game, torch.ones_like(game))
    span = ee - eb
    frac = (e - eb) / span
    lb, le = torch.log10(safe_b), torch.log10(safe_e)
    logv = torch.pow(10.0, lb + frac * (le - lb))
    lin = gamb + frac * (game - gamb)
    dfrac = (-deb - frac * (dee - deb)) / span
    dv = torch.where(both, logv * math.log(10.0) * (le - lb) * dfrac, (game - gamb) * dfrac)
    return torch.where(both, logv, lin), dv


def psf_params(pk: Packed, theta: Tensor, want_d: bool = False) -> dict:
    """Every point's photon-strength parameters at theta = (ftable(E1), wtable(E1), sgr(M1)),
    per target as gammapar.f90 holds them, gathered onto the point axis.

    TALYS: gammapar.f90:1 (gammapar)
    Test: SPEEDG / tests/hf/test_capture_gpu.py
    """
    g, nuc = pk.g, pk.nuc
    theta = theta.detach()
    ft, wt, sgr = theta[:, 0], theta[:, 1], theta[:, 2]
    # gammapar.table_arrays: etable (0 here), ftable, then the wtable stretch about the T = 0
    # maximum (first maximum wins)
    e = g["e_raw"]
    f = g["f_raw"] * ft[:, None, None]
    f0 = f[:, 1:, 0]
    fmax = f0.max(dim=1).values
    imax = torch.argmax((f0 == fmax[:, None]).to(torch.int64), dim=1) + 1
    emid = torch.gather(e, 1, imax[:, None])
    stretched = torch.cat([e[:, :1], emid + (e[:, 1:] - emid) * wt[:, None]], dim=1)
    stretch = (fmax > 0.0)[:, None]
    e_tab = torch.where(stretch, stretched, e)

    def pt(x):
        return x[nuc][:, None]

    p = dict(nuc=nuc[:, None], e_tab=e_tab[nuc], f_flat=f.reshape(-1), tq=g["tq"],
             S=pt(g["S"]), delta=pt(g["delta"]), alev=pt(g["alev"]), beta2=pt(g["beta2"]),
             ft=pt(ft), sgr1=pt(sgr), sgr2=pt(sgr * 8.0e-4),  # gammapar.f90:441-445
             m1e=pt(g["m1"][:, 1]), m1g=pt(g["m1"][:, 2]),
             e2s=pt(g["e2"][:, 0]), e2e=pt(g["e2"][:, 1]), e2g=pt(g["e2"][:, 2]),
             m2e=pt(g["m2"][:, 1]), m2g=pt(g["m2"][:, 2]),
             tpr=pt(g["scissors"][:, 0]), epr=pt(g["scissors"][:, 1]),
             gpr=pt(g["scissors"][:, 2]), tpr_on=pt(g["scissors"][:, 0] > 0.0),
             upc=pt(g["upbend"][:, 0]), upe=pt(g["upbend"][:, 1]), upf=pt(g["upbend"][:, 2]))
    if want_d:
        # d e_tab / d wtable: (e_raw - emid) at points 1..300 of a stretched table
        de = torch.cat([torch.zeros_like(e[:, :1]), e[:, 1:] - emid], dim=1)
        p["de_tab"] = torch.where(stretch, de, torch.zeros_like(de))[nuc]
    return p


def _e1(p: dict, efs: Tensor, eg: Tensor, want_d: bool):
    """fstrength.f90's tabulated E1 (strength 9, n_t0 = 11 temperatures), (P, n); with `want_d`
    also its derivative in wtable (ftable scales it and is the caller's)."""
    e_tab = p["e_tab"]
    nT = p["tq"].shape[0]
    e = torch.clamp(efs, max=20.0) + p["S"] - p["delta"] - eg
    ok = (e > 0.0) & (p["alev"] > 0.0)
    tnuc = torch.where(ok, torch.sqrt(torch.where(ok, e, torch.ones_like(e)) / p["alev"]),
                       torch.zeros_like(e))
    tq = p["tq"]
    n_t = torch.searchsorted(tq, tnuc.contiguous(), right=True).clamp(max=nT)  # #(tq <= Tnuc)
    tb = tq[n_t.clamp(min=1) - 1]
    te = torch.where(n_t < nT, tq[n_t.clamp(max=nT - 1)], tb)
    inside = eg <= e_tab[:, NUMGAMQRPA, None]
    # locate.f90 on a table whose points 1..300 ascend (point 0 = 0 may sit above point 1 after
    # the stretch): for Egamma > 0 the bisection lands on the count of points 1..300 <= Egamma
    nen_in = torch.searchsorted(e_tab[:, 1:].contiguous(), eg.contiguous(),
                                right=True).clamp(0, NUMGAMQRPA - 1)
    nen = torch.where(inside, nen_in, torch.full_like(nen_in, NUMGAMQRPA - 1))
    eb = torch.gather(e_tab, -1, nen)
    ee = torch.gather(e_tab, -1, nen + 1)
    if want_d:
        deb = torch.gather(p["de_tab"], -1, nen)
        dee = torch.gather(p["de_tab"], -1, nen + 1)
    flat = p["f_flat"]
    ib = (p["nuc"] * (NUMGAMQRPA + 1) + nen) * nT
    ie = ib + nT
    fvals, dvals = [], []
    for it in (1, 2):
        jt = (n_t if it == 1 else n_t + 1).clamp(max=nT)
        et = tb if it == 1 else te
        col = jt - 1
        gamb = torch.where(inside & ~(eb <= et), flat[ib], flat[ib + col])
        game = torch.where(inside & ~(ee <= et), flat[ie], flat[ie + col])
        if want_d:
            v, dv = _interp_de(eg, eb, ee, gamb, game, deb, dee)
            fvals.append(v)
            dvals.append(dv)
        else:
            fvals.append(_interp(eg, eb, ee, gamb, game))
    fb, fe = fvals
    do_t = (te - tb) != 0.0
    te_s = torch.where(do_t, te, tb + 1.0)
    f_t = _interp(tnuc, tb, te_s, fb, fe)
    out = torch.where(do_t, f_t, fe)
    if not want_d:
        return out, None
    dfb, dfe = dvals
    both = (fb > 0.0) & (fe > 0.0)
    frac = (tnuc - tb) / (te_s - tb)
    sb = torch.where(both, fb, torch.ones_like(fb))
    se = torch.where(both, fe, torch.ones_like(fe))
    df_t = torch.where(both, f_t * ((1.0 - frac) * dfb / sb + frac * dfe / se),
                       dfb + frac * (dfe - dfb))
    return out, torch.where(do_t, df_t, dfe)


def _slo(k: float, sgr, egr, ggr, eg, enum_pow):
    """fstrength.f90's standard Lorentzian (Egamma > 1 keV)."""
    egam2 = eg ** 2
    enum = ggr ** 2 * enum_pow
    denom = (egam2 - egr ** 2) ** 2 + egam2 * ggr ** 2
    return torch.where(eg > 0.001, k * sgr * enum / denom, torch.zeros_like(eg))


def tcl_kernel(p: dict, efs: Tensor, eg: Tensor, pos: Tensor, fn1: Tensor, want_d: bool):
    """densprepare's Tgam = 2 pi Egamma^(2l+1) f_XL(Egamma) Fnorm, split by c = |P - P'| / 2
    and l' and without the l' = 0 column (always zero for photons): (P, n, 4) in the order
    (c, l') = (0, 1) M1, (0, 2) E2, (1, 1) E1, (1, 2) M2. With `want_d`, also the derivatives
    of the M1, E1 and M2 columns in theta: (dM1/dsgr, dE1/dftable, dE1/dwtable, dM2/dsgr).

    TALYS: fstrength.f90:1 (fstrength), densprepare.f90:288-322
    Test: SPEEDG / tests/hf/test_capture_gpu.py
    """
    twopi, k0 = _twopi(), _pi2h2c2()
    k1, k2 = k0 / 3.0, k0 / 5.0
    eg_s = torch.where(pos, eg, torch.ones_like(eg))
    fac1 = twopi * eg_s ** 3 * fn1
    fac2 = twopi * eg_s ** 5 * fn1
    z = torch.zeros_like(eg)
    # M1: Lorentzian + scissors + upbend
    slo1 = _slo(k1, p["sgr1"], p["m1e"], p["m1g"], eg_s, eg_s)
    egam2 = eg_s ** 2
    enum = p["gpr"] ** 2 * eg_s
    denom = (egam2 - p["epr"] ** 2) ** 2 + egam2 * p["gpr"] ** 2
    m1 = torch.where(p["tpr_on"] & (eg_s > 0.001), slo1 + k1 * p["tpr"] * enum / denom, slo1)
    m1 = m1 + p["upc"] * torch.exp(-p["upe"] * eg_s) * torch.exp(-p["upf"] * torch.abs(p["beta2"]))
    e2 = _slo(k2, p["e2s"], p["e2e"], p["e2g"], eg_s, eg_s ** -1)
    m2 = _slo(k2, p["sgr2"], p["m2e"], p["m2g"], eg_s, eg_s ** -1)
    e1, de1 = _e1(p, efs, eg_s, want_d)
    tm1 = torch.where(pos, fac1 * m1, z)
    te2 = torch.where(pos, fac2 * e2, z)
    te1 = torch.where(pos, fac1 * e1, z)
    tm2 = torch.where(pos, fac2 * m2, z)
    out = torch.stack([tm1, te2, te1, tm2], dim=-1)
    if not want_d:
        return out, None
    d = (torch.where(pos, fac1 * slo1, z) / p["sgr1"], te1 / p["ft"],
         torch.where(pos, fac1 * de1, z), tm2 / p["sgr1"])
    return out, d


def _linearise(Tc: Tensor, d, dth: Tensor) -> Tensor:
    """Tc carrying the graph to theta: Tc + (dT/dtheta) * dth with dth = theta_p - theta_p
    (exactly zero, so the value is Tc to the bit, and the gradient is the analytic derivative)."""
    dm1, de1f, de1w, dm2 = d
    z = torch.zeros_like(dm1)
    lin = torch.stack([dm1 * dth[:, None, 2], z, de1f * dth[:, None, 0] + de1w * dth[:, None, 1],
                       dm2 * dth[:, None, 2]], dim=-1)
    return Tc + lin


# ------------------------------------------------------------------------------ masks


def _photon_exit_mask(j2: Tensor, irs2: Tensor) -> Tensor:
    """`target_batch._mask_for` for photons at l' = 1, 2 (slot updown = 0): (..., 2) float.

    OPEN3M: a discrete level with an impossible 2J parity reads `l2' = jj2' = 2 l' + 1`, capped
    at l2maxhf = 2 gammax (`prepare.anomalous_exit_mask`); for every other spin this is 2 l'.
    """
    lp = torch.arange(1, L, device=j2.device)
    lo = (j2 - irs2).abs()[..., None]
    hi = (j2 + irs2)[..., None]
    jj = 2 * lp + lo % 2
    return ((jj >= lo) & (jj <= hi) & ((jj - lo) % 2 == 0) & (jj <= 2 * (L - 1))).to(F64)


def _dof(tav: Tensor, st: Tensor) -> Tensor:
    """`wfc.degrees_of_freedom`, WFCfactor 1."""
    return torch.clamp(1.78 + (tav ** 1.212 - 0.78) * torch.exp(-0.228 * st), max=2.0)


def _band_masks(odd: Tensor, J: int) -> dict:
    """`continuum._spin_l_mask(odd, 0, J, L)` for photons, as bands: the mask of mother J = m and
    residual Ir = i at l' is `|m - i| <= l' <= m + i + odd`, symmetric in (m, i). Returns
    {"l{l'}d{d}": (P, J, 1, 1) float} with d = i - m, for l' = 1, 2 and |d| <= l'."""
    m = torch.arange(J, device=odd.device)
    out = {}
    for lp in (1, 2):
        for d in range(-lp, lp + 1):
            i = m + d
            ok = (i >= 0) & (i < J)
            out[f"l{lp}d{d}"] = (ok[None, :] & ((m + i)[None, :] + odd[:, None] >= lp)
                                 ).to(F64)[:, :, None, None]
    return out


def _band_sum(X: Tensor, lp: int, masks: dict) -> Tensor:
    """sum_i mask(m, i, l') X[:, i] for X (P, J, a, b): the spin-l' contraction as a band sum."""
    J = X.shape[1]
    Xp = torch.nn.functional.pad(X, (0, 0, 0, 0, 2, 2))
    out = None
    for d in range(-lp, lp + 1):
        term = Xp[:, 2 + d: 2 + d + J] * masks[f"l{lp}d{d}"]
        out = term if out is None else out + term
    return out


class _Band(torch.autograd.Function):
    """`_band_sum` with its own adjoint (the mask is symmetric), for eager autograd."""

    @staticmethod
    def forward(ctx, X, lp, masks):
        ctx.lp, ctx.masks = lp, masks
        return _band_sum(X, lp, masks)

    @staticmethod
    def backward(ctx, g):
        return _band_sum(g, ctx.lp, ctx.masks), None, None


def _band(X: Tensor, lp: int, masks: dict, fused: bool) -> Tensor:
    if not fused and X.requires_grad and torch.is_grad_enabled():
        return _Band.apply(X, lp, masks)
    return _band_sum(X, lp, masks)


# ------------------------------------------------------------------------------ the decay step


def rows_kernel(exinc, dexinc, exr, dexr, sep0, sn, cont, rn, ntop, discfactor, nl, okd):
    """One mother bin's residual rows for the photon exit: Rboundary (P, n), Egamma, Efs, and
    the discrete levels' rho0 weights (P, nd).

    TALYS: densprepare.f90:196-281
    Test: SPEEDG / tests/hf/test_capture_gpu.py
    """
    ex0plus = exinc + 0.5 * dexinc
    ex0min = exinc - 0.5 * dexinc
    dexhalf = 0.5 * dexr
    ex1min = exr - dexhalf
    ex1plus = exr + dexhalf
    emax = (ex0plus - sep0)[:, None] - ex1min
    emin = (ex0min - sep0)[:, None] - ex1plus
    eout_mid = 0.5 * (emin + emax)
    half = 0.5 * (emax - emin)
    half_s = torch.where(half != 0.0, half, torch.ones_like(half))
    rb_c = torch.where(emin < 0.0, torch.where(eout_mid > 0.0, 1.0 - 0.5 * (emin / half_s) ** 2,
                                               0.5 * (emax / half_s) ** 2), torch.ones_like(half))
    exm = exr + sep0[:, None]
    part = (ex0min[:, None] < exm) & (exm <= ex0plus[:, None])
    rb_d = torch.where(part, (ex0plus[:, None] - exm) / dexinc[:, None], torch.ones_like(exm))
    rb = torch.where(cont, rb_c, rb_d)
    nd = rn.shape[1]
    rbd = rb[:, :nd]
    v = torch.where(rn > ntop[:, None], rbd * discfactor[:, None], rbd)
    v = torch.where(rn <= nl[:, None], v, torch.zeros_like(v))
    v = torch.where(v >= 1.0e-20, v, torch.zeros_like(v))
    v = torch.where((nl[:, None] == 0) & (rn == 0), torch.zeros_like(v), v)
    rho_d = torch.where(okd, v, torch.zeros_like(v))
    return rb, exinc[:, None] - exr, exinc - sn, rho_d


def decay_kernel(Tcc, Tcd, rbc, rgc, rho_d, pdn, Mdn, bands, Wb, p5b, popm, peb, jm, dec,
                 ng1, tr, fused: bool):
    """`capture_fast_batch._photon_feeding` of one mother bin for every point: the photon widths
    (continuum rows through rhogrid, discrete levels through their one cell), the denominators,
    the feeding, and what it adds to every residual row. Returns (dpc (P, nc, J, 2) continuum
    rows, their sums (P, nc), vd (P, nd) discrete levels, trapped flux per level (P, nd)).

    `fused` selects the formulation for `torch.compile` (broadcast products under a sum, which
    inductor fuses without building them) over the eager one (einsum / bmm).

    TALYS: compound.f90:1 (compound), densprepare.f90:1 (densprepare)
    Test: SPEEDG / tests/hf/test_capture_gpu.py
    """
    P = Tcc.shape[0]
    nd = Tcd.shape[1]
    u = rbc[..., None] * Tcc  # rho0 = Rboundary * rhogrid (no cut: `pack` checked it)
    if fused:
        Rr = (rgc[..., None] * u[:, :, None, None, :]).sum(1)
    else:
        Rr = torch.einsum("pnjq,pnk->pjqk", rgc, u)  # (P, J, P', 4)
    B1 = _band(Rr[..., 0::2], 1, bands, fused)  # l' = 1: (M1, E1)
    B2 = _band(Rr[..., 1::2], 2, bands, fused)  # l' = 2: (E2, M2)
    # c = 0 is (M1, E2), c = 1 is (E1, M2): D(P) = sum over P' with c = |P - P'|
    D0 = torch.stack([(B1[..., 0, 0] + B2[..., 0, 0]) + (B1[..., 1, 1] + B2[..., 1, 1]),
                      (B1[..., 0, 1] + B2[..., 0, 1]) + (B1[..., 1, 0] + B2[..., 1, 0])], dim=-1)
    T4 = Tcd.reshape(P, nd, 2, 2)  # (P, n, c, l')
    Tq0 = torch.where(pdn == 0, T4[:, :, 0], T4[:, :, 1])  # parity index 0 reads c = pd
    Tq1 = torch.where(pdn == 1, T4[:, :, 0], T4[:, :, 1])
    Y = torch.stack([Tq0 * rho_d[..., None], Tq1 * rho_d[..., None]], dim=-1)  # (P, n, l', P')
    if fused:
        Dd = (Mdn[..., None] * Y[:, None]).sum((2, 3))
    else:
        Dd = torch.bmm(Mdn, Y.reshape(P, 2 * nd, 2))
    D0 = D0 + 1.0 * Dd
    dsum = D0
    for k in range(Wb.shape[-1]):
        dsum = dsum + Wb[..., k]
    only6 = (D0 == 0.0) & p5b
    active = (popm >= peb[:, None, None]) & jm[:, :, None] & dec[:, None, None]
    denom = torch.where(active & only6, torch.zeros_like(dsum), dsum)
    live = active & (popm != 0.0) & (denom != 0.0)
    feed = torch.where(live, popm / torch.where(live, denom, torch.ones_like(denom)),
                       torch.zeros_like(popm))
    Vb1 = _band(feed[..., None], 1, bands, fused)[..., 0]
    Vb2 = _band(feed[..., None], 2, bands, fused)[..., 0]
    V = torch.stack([Vb1, Vb2, Vb1.flip(-1), Vb2.flip(-1)], dim=-1)  # (P, J, P', 4)
    if fused:
        dpc = rgc * (u[:, :, None, None, :] * V[:, None]).sum(-1)
    else:
        dpc = rgc * torch.einsum("pnk,pjqk->pnjq", u, V)
    mc_c = dpc.sum((-2, -1))
    if fused:
        Gq = (Mdn[..., None] * feed[:, :, None, None, :]).sum(1)  # (P, n, l', P')
    else:
        Gq = torch.bmm(Mdn.transpose(1, 2), feed).reshape(P, nd, 2, 2)
    fd = (Tq0 * Gq[..., 0]).sum(-1) + (Tq1 * Gq[..., 1]).sum(-1)
    vd = rho_d * fd
    trapped = active & (popm != 0.0) & (denom == 0.0)
    share = torch.where(trapped, popm, torch.zeros_like(popm)).sum((1, 2)) / ng1
    return dpc, mc_c, vd, torch.where(tr, share[:, None], torch.zeros_like(vd))


# ------------------------------------------------------------------------------ forward


_COMPILED: dict = {}


def _k(fn, compiled: bool):
    """`fn`, or its `torch.compile`d version (dynamic shapes, compiled once per process)."""
    if not compiled:
        return fn
    key = (fn.__name__, torch.is_grad_enabled())  # separate caches: no guard checks across modes
    got = _COMPILED.get(key)
    if got is None:
        import torch._dynamo.config as dcfg
        import torch.fx.experimental._config as fcfg

        # one graph per kernel and grad mode: no equalities between unrelated sizes that
        # happen to coincide (duck shapes), and room for the few 0/1 specialisations
        fcfg.use_duck_shape = False
        dcfg.recompile_limit = max(dcfg.recompile_limit, 64)
        dcfg.accumulated_recompile_limit = max(dcfg.accumulated_recompile_limit, 1024)
        got = _COMPILED[key] = torch.compile(fn, dynamic=True)
    return got


def _primary(pk: Packed, p: dict, dth: Tensor | None, compiled: bool) -> Tensor:
    """comptarget's photon population of the compound nucleus, (P, R, J, 2).

    TALYS: comptarget.f90:1 (comptarget), densprepare.f90:1 (densprepare), moldauer.f90:1
    Test: SPEEDG / tests/hf/test_capture_gpu.py
    """
    from physics.hf.compound import wfc

    t, dev = pk.t, pk.device
    P, J, K = pk.n, pk.dims["J"], pk.dims["K"]
    eg = t["eg0"]
    pos = (eg > 0.0) & t["row0"]
    Tc, d = _k(tcl_kernel, compiled)(p, t["efs0"][:, None], eg, pos, t["fn1_0"][:, None],
                                     dth is not None)
    if dth is not None:
        Tc = _linearise(Tc, d, dth)
    J2 = t["J2"]  # (P, K)
    pidx = t["pidx"]
    Ir = torch.arange(J, device=dev)
    irs2 = 2 * Ir[None, None, :] + (J2[:, :, None] % 2)  # (P, K, J)
    M = _photon_exit_mask(J2[:, :, None], irs2) * t["cell"][:, :, None, None]  # (P, K, J, 2)
    rho_c = t["rho_c0"]
    Rr = torch.einsum("pnjq,pnk->pjqk", rho_c, Tc).reshape(P, J, 2, 2, 2)  # (P, J, q, c, l')
    MR = torch.einsum("pkjl,pjqcl->pkcq", M, Rr)
    D0 = MR[:, :, 0, 0] + MR[:, :, 1, 1]
    D1 = MR[:, :, 1, 0] + MR[:, :, 0, 1]
    Dg = torch.where(pidx == 0, D0, D1)
    ND0 = pk.dims["ND0"]
    Md = _photon_exit_mask(J2[:, :, None], t["jd2_0"][:, None, :])  # (P, K, ND0, 2)
    T4 = Tc[:, :ND0].reshape(P, ND0, 2, 2)  # (P, n, c, l')
    cm = pidx[:, :, None] != t["pd0"][:, None, :]  # (P, K, ND0): c of each (cell, level)
    tot_dk = (torch.where(cm, T4[:, None, :, 1, 0], T4[:, None, :, 0, 0]) * Md[..., 0]
              + torch.where(cm, T4[:, None, :, 1, 1], T4[:, None, :, 0, 1]) * Md[..., 1])
    rho_d = t["rho_d0"]
    Dg = Dg + (tot_dk * rho_d[:, None, :]).sum(-1)
    denom = Dg
    for k in range(6):
        denom = denom + t["dpart"][:, :, k]
    live = (denom != 0.0) & t["cell"]
    st = torch.where(live, denom, torch.ones_like(denom))
    # Moldauer (widthmode 1) or no width fluctuations
    x, wts = wfc.gauss_laguerre(dev)
    tinc = t["tinc"]  # (P, K, NA)
    nu_inc = _dof(tinc, st[..., None])
    fsum = torch.zeros((P, K, x.numel()), dtype=F64, device=dev)
    for b in t["channels"]:
        st_r = st[b["p"], b["k"]]  # (rows,)
        fsum = fsum.index_put((b["p"], b["k"]), _MolFactor.apply(st_r, b["t"], b["r"], x))
    expo = Dg[..., None] * x / st[..., None]
    capt = torch.where(expo > 80.0, 0.0, torch.exp(-torch.clamp(expo, max=80.0)))
    prod = wts * wts * torch.exp(x) * torch.exp(fsum) * capt  # (P, K, M)
    fa = 2.0 * tinc / (st[..., None] * nu_inc)
    da = 1.0 + x[None, None, :, None] * fa[:, :, None, :]
    H = (tinc[:, :, None, :] / da).sum(-1)
    gg = (prod * H).sum(-1)
    G = torch.where(t["wfc"][:, None], gg, t["feedsum"])
    pref = t["cn"][:, None] * (J2.to(F64) + 1.0) / st
    w = torch.where(live, pref * G, torch.zeros_like(G))
    # _feed_type
    same = (pidx[..., None] == torch.arange(2, device=dev)).to(F64)  # (P, K, 2)
    V0 = torch.einsum("pkjl,pkq->pjql", M, w[..., None] * same)
    V1 = torch.einsum("pkjl,pkq->pjql", M, w[..., None] * (1.0 - same))
    V = torch.stack([V0[..., 0], V0[..., 1], V1[..., 0], V1[..., 1]], dim=1)  # (P, 4, J, 2)
    TV = torch.einsum("pnk,pkjq->pnjq", Tc, V)
    pop = rho_c * TV
    fd = (tot_dk * w[..., None]).sum(1) * rho_d  # (P, ND0)
    fd = torch.where(t["okd0"], fd, torch.zeros_like(fd))
    ar = torch.arange(P, device=dev)[:, None].expand(P, ND0)
    rows = torch.arange(ND0, device=dev)[None, :].expand(P, ND0)
    pop = pop.index_put((ar, rows, t["ird0"], t["pd0"]), fd, accumulate=True)
    return pop * t["row0"][:, :, None, None]


def forward(pk: Packed, theta: Tensor | None = None, grad: bool = False,
            compiled: bool = False):
    """`xs000000` [mb] of every point of `pk`, (P,); with `grad`, also the Jacobian (P, 3) of each
    point's cross section in its target's theta = (ftable(E1), wtable(E1), sgr(M1)).

    The Jacobian takes one reverse pass: every point gets its own copy of theta, so the gradient
    of the sum of all cross sections with respect to the copies is every point's own row.
    `compiled` runs the photon strength and the decay step through `torch.compile` (needs a C
    compiler for triton; the first call compiles).

    TALYS: comptarget.f90:1 (comptarget), multiple.f90:1 (multiple), cascade.f90:1 (cascade)
    Test: SPEEDG / tests/hf/test_capture_gpu.py
    """
    if theta is None:
        theta = theta_default(pk)
    if not pk.meta["factorised"]:
        raise ValueError("rho0's 1e-20 cut can fire in this batch; not covered")
    if grad:
        theta_p = theta.detach()[pk.nuc].clone().requires_grad_(True)
        with torch.enable_grad():
            xs = _forward(pk, theta, theta_p - theta_p.detach(), compiled)
            (jac,) = torch.autograd.grad(xs.sum(), theta_p)
        return xs.detach() + _dc(pk), jac
    with torch.no_grad():
        return _forward(pk, theta, None, compiled) + _dc(pk)


def _dc(pk: Packed):
    """DIRECTCAP's per-point direct-capture addend (0 when off or packed before it existed)."""
    return pk.t.get("dc_mb", 0.0)


def _forward(pk: Packed, theta: Tensor, dth: Tensor | None, compiled: bool) -> Tensor:
    """The populations of the compound nucleus are one (P, J, 2) tensor per continuum row and a
    (P, NL + 1) tensor of discrete-level populations: a level is populated in its own (J, parity)
    cell only (comptarget, the feeding and the gamma cascade all write there)."""
    t, dev = pk.t, pk.device
    P, R, J = pk.n, pk.dims["R"], pk.dims["J"]
    want_d = dth is not None
    p = psf_params(pk, theta, want_d)
    pop = _primary(pk, p, dth, compiled)  # (P, R, J, 2)
    xspopex = pop.sum((-2, -1))
    xspopnuc = pop.sum((1, 2, 3))
    go = xspopnuc >= t["popeps_mb"]
    ar = torch.arange(P, device=dev)
    Jr = torch.arange(J, device=dev)
    odd = t["odd"]
    bands = _band_masks(odd, J)
    rows = torch.arange(R, device=dev)
    nl, ng = t["nl"], t["ng"]
    cont_row = rows[None, :] > nl[:, None]  # (P, R)
    ND = int(pk.meta["nl_max"]) + 1  # rows < ND can be a discrete level for some point
    lo = int(pk.meta["nl_min"]) + 1  # rows >= lo can be continuum for some point
    jd2 = t["jdis2"][:, :ND]
    ird = torch.div(jd2, 2, rounding_mode="floor")
    pd = (t["parlev"][:, :ND] > 0).to(torch.int64)
    okd = (ird >= 0) & (ird <= NUMJ) & (ird < J)
    irc = ird.clamp(0, J - 1)
    j2m = 2 * Jr[None, :] + odd[:, None]  # (P, J)
    lbeg = torch.div((j2m[:, :, None] - jd2[:, None, :]).abs(), 2, rounding_mode="floor")
    lend = torch.div(j2m[:, :, None] + jd2[:, None, :], 2, rounding_mode="floor")
    lp = torch.arange(1, L, device=dev)
    Md = ((lp >= lbeg[..., None]) & (lp <= lend[..., None])).to(F64)  # (P, J, ND, 2)
    Mdf = Md.reshape(P, J, 2 * ND).contiguous()  # prefix slices of the flat axis stay views
    rowsND = torch.arange(ND, device=dev)[None, :].expand(P, ND)
    levrow = rowsND <= ng[:, None]
    ng1 = ng.to(F64) + 1.0
    rgm = t["rhogrid_c"]  # (P, R, J, 2), zero outside keepj & valid_c
    crow = {r: pop[:, r] * cont_row[:, r, None, None] for r in range(lo, R)}
    popd = torch.where(okd & (rowsND <= nl[:, None]), pop[ar[:, None], rowsND, irc, pd],
                       torch.zeros((P, ND), dtype=F64, device=dev))
    del pop
    NBR = pk.dims["NBR"]
    arBR = ar[:, None].expand(P, NBR)
    any1, any2 = pk.meta["mode_any1"], pk.meta["mode_any2"]
    kt, kr, kd = (_k(tcl_kernel, compiled), _k(rows_kernel, compiled),
                  _k(decay_kernel, compiled))
    for nex in range(R - 1, 0, -1):
        mode = t["mode"][:, nex]
        if any1[nex]:
            # -- gamma cascade of a discrete level (cascade.f90)
            casc = (mode == 1) & go
            xsjp = popd[:, nex] if nex < ND else torch.zeros(P, dtype=F64, device=dev)
            kk = t["br_k"][:, nex]  # (P, NBR)
            intens = xsjp[:, None] * t["br_r"][:, nex] * casc[:, None]
            popd = popd.index_put((arBR, kk), intens, accumulate=True)
            xspopex = xspopex.index_put((arBR, kk), intens, accumulate=True)
            xspopex = xspopex.index_put((ar, torch.full_like(ar, nex)), -intens.sum(1),
                                        accumulate=True)
        if not any2[nex]:
            continue
        # -- decay by emission (compound.f90 through `_photon_feeding`)
        dec = (mode == 2) & go & ~(xspopex[:, nex] < t["popeps_a"])
        hi = nex  # residual rows 0..nex-1
        # rows c0..nex-1 may be continuum (at least two: a discrete row has rhogrid_c = 0 and
        # adds nothing, and the compiled kernel keeps one graph), rows 0..nd-1 may be discrete
        c0 = max(0, min(lo, hi - 2))
        nd = min(ND, hi)
        bi = t["bidx"][:, nex]
        rb, eg, efs, rho_d = kr(t["ex"][:, nex], t["dex"][:, nex], t["ex"][:, :hi],
                                t["dex"][:, :hi], t["sep0"], t["sn"], cont_row[:, :hi],
                                rowsND[:, :nd], t["ntop"], t["discfactor"], nl, okd[:, :nd])
        Tc, d = kt(p, efs[:, None], eg, eg > 0.0, t["fn1"][:, None], want_d)  # (P, hi, 4)
        if want_d:
            Tc = _linearise(Tc, d, dth)
        # the mother bin's (J, parity) population
        popm = torch.zeros((P, J, 2), dtype=F64, device=dev)
        if nex >= lo:
            popm = popm + crow[nex] * cont_row[:, nex, None, None]
        if nex < ND:
            popm = popm + torch.zeros((P, J, 2), dtype=F64, device=dev).index_put(
                (ar, irc[:, nex], pd[:, nex]), torch.where(cont_row[:, nex], 0.0, popd[:, nex]))
        jm = Jr[None, :] <= t["maxj"][:, nex][:, None]
        tr = levrow[:, :nd] & (rowsND[:, :nd] <= hi - 1)
        Mdn = Md[:, :, :nd] if compiled else Mdf[:, :, : 2 * nd]
        dpc, mc_c, vd, trap = kd(Tc[:, c0:hi], Tc[:, :nd], rb[:, c0:hi], rgm[:, c0:hi], rho_d,
                                 pd[:, :nd, None], Mdn, bands, t["W"][ar, bi],
                                 t["part5zero"][ar, bi], popm, t["popeps_b"][ar, bi], jm, dec,
                                 ng1, tr, compiled)
        for r, dr in zip(range(c0, hi), dpc.unbind(1), strict=True):
            if r >= lo:
                crow[r] = crow[r] + dr
        popd = torch.cat([popd[:, :nd] + vd + trap, popd[:, nd:]], dim=1)
        add = torch.cat([vd, torch.zeros((P, R - nd), dtype=F64, device=dev)], dim=1)
        add = torch.cat([add[:, :c0], add[:, c0:hi] + mc_c, add[:, hi:]], dim=1)
        tot = add[:, :hi].sum(1)
        add = add.index_put((ar, torch.full_like(ar, nex)), -tot, accumulate=True)
        xspopex = xspopex + add
    out = xspopex[:, 0]
    for k in range(1, R):
        out = torch.where(t["iso"][:, k] & (k <= ng), out + xspopex[:, k], out)
    return torch.where(go, out, torch.zeros_like(out))


class _MolFactor(torch.autograd.Function):
    """molprepare's sum over open exit channels of -nu/2 * rho * log(1 + 2 T x / (nu S)) for
    rows (point, cell) of total width S: (rows, nodes), with the derivative in S analytic."""

    @staticmethod
    def forward(ctx, st, tt, rr, x):
        nu = _dof(tt, st[:, None])
        eps = 2.0 * tt[:, None, :] * x[None, :, None] / (st[:, None, None] * nu[:, None, :])
        livee = eps > 1.0e-30
        logterm = torch.where(livee, torch.log1p(torch.where(livee, eps, 0.0)), 0.0)
        ctx.save_for_backward(st, tt, rr, x)
        return ((-nu * 0.5 * rr)[:, None, :] * logterm).sum(2)

    @staticmethod
    def backward(ctx, g):
        st, tt, rr, x = ctx.saved_tensors
        ex = torch.exp(-0.228 * st)[:, None]
        base = tt ** 1.212 - 0.78
        raw = 1.78 + base * ex
        nu = torch.clamp(raw, max=2.0)
        dnu = torch.where(raw <= 2.0, base * (-0.228) * ex, 0.0)
        eps = 2.0 * tt[:, None, :] * x[None, :, None] / (st[:, None, None] * nu[:, None, :])
        livee = eps > 1.0e-30
        e0 = torch.where(livee, eps, 0.0)
        logterm = torch.where(livee, torch.log1p(e0), 0.0)
        deps = -eps * (1.0 / st[:, None, None] + (dnu / nu)[:, None, :])
        dlog = torch.where(livee, deps / (1.0 + e0), 0.0)
        dfac = (-0.5 * rr * dnu)[:, None, :] * logterm + (-nu * 0.5 * rr)[:, None, :] * dlog
        return (g * dfac.sum(2)).sum(1), None, None, None


# ------------------------------------------------------------------------------ driver


def sweep_arrays(targets: list[dict], xs: Tensor, pk: Packed, n_energies: int):
    """(xs [mb], domain) arrays (Nn, nE) with `run_task`'s NaN semantics."""
    out = np.full((len(targets), n_energies), np.nan)
    dom = np.zeros((len(targets), n_energies), dtype=bool)
    for i, tgt in enumerate(targets):
        dom[i] = tgt["domain"]
    v = xs.detach().cpu().numpy()
    for p, (ti, ei) in enumerate(pk.index):
        if not targets[ti]["err"]:
            out[ti, ei] = v[p]
    return out, dom


__all__ = ["Packed", "pack", "forward", "theta_default", "psf_params", "tcl_kernel", "sweep_arrays"]
