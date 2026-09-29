"""The dump-free `engine.ChainedFull` channel set on a (nuclide, incident energy) batch axis.

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

Task: GPUFULL (gate G-GF: the 370 spherical nuclides of `talys_sweep_broad` x the 20-point sweep
grid in <= 60 s on the laptop RTX 5050, identical to the CPU dump-free engine at <= 1e-12 relative
on every channel cell). No physics of its own: every number is produced by the statements the
CPU engine runs, rearranged so that all runs of a batch go through each statement at once.

TALYS routines computed here, in the arrangement described below:
    densprepare.f90:1 (densprepare)  -- primary and multiple emission, from set-up tables
    compprepare.f90:1 (compprepare), comptarget.f90:1 (comptarget), molprepare.f90:1,
    moldauer.f90:1                   -- the binary compound decay, Moldauer width fluctuations
    binary.f90:1 (binary)
    compound.f90:1 (compound), multiple.f90:1 (multiple), cascade.f90:1 (cascade)
    channels.f90:1 (channels), totalxs.f90:1 (totalxs)

**The split** is `gpu_full_setup`'s: set-up on CPU is structure and tables (grids, level densities,
emission-grid transmission tables, the incident channel, T8/T12's addends, photon transmissions);
this module computes everything that reads or writes a population.

**The batch axis.** A run is one (nuclide, energy). Runs are padded to the batch's largest grid,
cell list and channel list and masked. Padding enters only as exact zeros (a zero transmission,
weight or population) or behind `torch.where`, so a padded term adds 0.0.

**Rounding.** The CPU engine sums non-negative terms in the order its einsums and numpy
reductions happen to use; this module groups the same terms differently, so results agree to
rounding and not bitwise (the gate is 1e-12; every place where a subtraction amplifies that is
named in docs/results/hf-gpu-full.md).

Test: GPUFULL / tests/hf/test_gpu_full.py
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

import numpy as np
import torch
from torch import Tensor

F64 = torch.float64
NUMJ = 40
PARZ = (0, 0, 1, 1, 1, 2, 2)
PARN = (0, 1, 0, 1, 2, 1, 2)
SPIN2 = (1, 1, 1, 2, 1, 1, 1)
PARSPIN2 = (0, 1, 1, 2, 1, 1, 0)


def _pad_stack(arrs, shape, dtype=np.float64, fill=0):
    out = np.full((len(arrs),) + tuple(shape), fill, dtype=dtype)
    for i, a in enumerate(arrs):
        a = np.asarray(a)
        sl = tuple(slice(0, min(s, m)) for s, m in zip(a.shape, shape, strict=True))
        out[(i,) + sl] = a[sl]
    return out


# ================================================================================================
# packing
# ================================================================================================


@dataclass
class Batch:
    """A list of runs on the device: nuclide tables, per-run scalars, the binary residual grids."""

    runs: list  # [(setup run dict, energy index)]
    device: torch.device
    t: dict  # name -> tensor
    dims: dict
    host: dict  # per-run python structure (cells, incident channel lists)


def _nuclide_tables(nucs: list[dict], device) -> dict:
    E = max(n["maxen"] for n in nucs) + 3
    L = max(n["tjl"].shape[2] for n in nucs)
    eg = np.zeros((len(nucs), E))
    e32 = np.zeros((len(nucs), E), dtype=np.float32)
    for i, n in enumerate(nucs):
        g = n["egrid"]
        eg[i, : g.size] = g
        # the located search row: the grid to maxen, then strictly ascending past it, so that a
        # binary search sees a sorted row (the index is clipped to [ebegin - 1, eend] anyway)
        m = n["maxen"] + 1
        e32[i, :m] = g[:m].astype(np.float32)
        e32[i, m:] = np.float32(g[m - 1]) + np.float32(1.0e6) * np.arange(1, E - m + 1)
    return dict(
        egrid=torch.as_tensor(eg, device=device),
        egrid32=torch.as_tensor(e32, device=device),
        tjl=torch.as_tensor(_pad_stack([n["tjl"] for n in nucs], (6, E, L, 3)), device=device),
        tl=torch.as_tensor(_pad_stack([n["tl"] for n in nucs], (6, E, L)), device=device),
        lmax=torch.as_tensor(_pad_stack([n["lmax"] for n in nucs], (6, E), np.int64),
                             device=device),
        ebegin=torch.as_tensor(np.stack([n["ebegin"] for n in nucs]), device=device),
        eend=torch.as_tensor(np.stack([np.minimum(n["eendmax"], n["maxen"]) for n in nucs]),
                             device=device),
        maxen=torch.as_tensor(np.array([n["maxen"] for n in nucs]), device=device),
        transeps=torch.as_tensor(np.array([n["transeps"] for n in nucs]), device=device),
    )


@lru_cache(maxsize=65536)
def _incident_channel_list(j2: int, parity: int, targetspin2: int, target_parity: int,
                           lmaxinc: int, s2: int = 1, spin2: int = 1):
    """`prepare.incident_channels`' (l, updown) list for one cell, in TALYS's loop order
    (a tuple, cached)."""
    pardif = abs(target_parity - parity) // 2
    out = []
    for jj2 in range(abs(j2 - targetspin2), j2 + targetspin2 + 1, 2):
        for l2 in range(abs(jj2 - s2), min(jj2 + s2, 2 * lmaxinc) + 1, 2):
            l = l2 // 2  # noqa: E741
            if l % 2 != pardif:
                continue
            out.append((l, (jj2 - l2) // spin2))
    return tuple(out)


def pack(runs: list, device) -> Batch:
    """Pad a list of (set-up run, energy index) onto the device."""
    nucs, nuc_of = [], []
    ids = {}
    for run, _ in runs:
        k = id(run)
        if k not in ids:
            ids[k] = len(nucs)
            nucs.append(run)
        nuc_of.append(ids[k])
    tab = _nuclide_tables(nucs, device)
    B = len(runs)
    E = [run["E"][i] for run, i in runs]
    k0 = runs[0][0]["k0"]
    # the seven binary residual specs of each run
    specs = [[e["specs"][(PARZ[t], PARN[t])] for t in range(7)] for e in E]
    R = max(s["maxex"] + 1 for row in specs for s in row)
    J = NUMJ + 1
    L = tab["tjl"].shape[3]
    G = max(runs[0][0]["gammax"], 2) + 1

    def per_t(key, dtype=np.float64, fill=0):
        return torch.as_tensor(np.stack([_pad_stack([row[t][key] for row in specs], (R,), dtype,
                                                    fill) for t in range(7)], axis=1),
                               device=device)

    t = dict(tab)
    t["nuc"] = torch.as_tensor(np.array(nuc_of), device=device)
    t["ex"] = per_t("ex")
    t["dex"] = per_t("dex")
    t["maxj"] = per_t("maxj", np.int64)
    t["parlev"] = per_t("parlev", np.int64)
    t["jdis"] = per_t("jdis")
    rg = np.zeros((B, 7, R, J, 2))
    for b, row in enumerate(specs):
        for ty in range(7):
            a = row[ty]["rhogrid"]
            rg[b, ty, : a.shape[0], : a.shape[1]] = a
    t["rhogrid"] = torch.as_tensor(rg, device=device)
    for key, dt in (("maxex", np.int64), ("nlast", np.int64), ("ntop", np.int64),
                    ("discfactor", np.float64)):
        t[key] = torch.as_tensor(np.array([[row[ty][key] for ty in range(7)] for row in specs],
                                          dtype=dt), device=device)
    t["sep0"] = torch.as_tensor(np.stack([e["specs"][(0, 0)]["sep"] for e in E]), device=device)
    t["etot"] = torch.as_tensor(np.array([e["etot"] for e in E]), device=device)
    t["lmaxinc"] = torch.as_tensor(np.array([e["lmaxinc_st"] for e in E]), device=device)
    t["fiso"] = torch.as_tensor(np.stack([run["fiso"] for run, _ in runs]), device=device)
    t["tgam0"] = torch.as_tensor(_pad_stack([e["tgam0"] for e in E], (R, G, 2)), device=device)
    t["cn"] = torch.as_tensor(np.array([e["cnfactor"] for e in E]), device=device)
    t["wfc"] = torch.as_tensor(np.array([e["flagwidth"] and run["wmode"] >= 1
                                         for (run, _), e in zip(runs, E, strict=True)]),
                               device=device)
    t["wfcfactor"] = torch.as_tensor(np.array([run["wfcfactor"] for run, _ in runs]),
                                     device=device)
    # compound cells (J2, parity): parity -1 block then +1 block, each padded to nJ
    nj = [(e["j2end"] - e["j2beg"]) // 2 + 1 if e["j2end"] >= e["j2beg"] else 0 for e in E]
    nJ = max(max(nj), 1)
    K = 2 * nJ
    j2 = np.zeros((B, K), dtype=np.int64)
    cell = np.zeros((B, K), dtype=bool)
    chans = []
    A = 1
    for b, e in enumerate(E):
        sc = runs[b][0]["sc"]
        row = []
        for p, par in enumerate((-1, 1)):
            for i in range(nJ):
                k = p * nJ + i
                if i < nj[b]:
                    j2[b, k] = e["j2beg"] + 2 * i
                    cell[b, k] = True
                    ch = _incident_channel_list(int(j2[b, k]), par, sc["targetspin2"],
                                                sc["target_parity"], e["lmaxinc"])
                else:
                    j2[b, k] = j2[b, 0] if nj[b] else 0
                    ch = []
                row.append(ch)
                A = max(A, len(ch))
        chans.append(row)
    tinc = np.zeros((B, K, A))
    li = np.zeros((B, K, A), dtype=np.int64)
    ui = np.zeros((B, K, A), dtype=np.int64)
    oka = np.zeros((B, K, A), dtype=bool)
    for b, e in enumerate(E):
        tj = e["tjlinc"]
        for k in range(K):
            for a, (l, ud) in enumerate(chans[b][k]):
                tinc[b, k, a] = tj[l, ud + 1]
                li[b, k, a], ui[b, k, a], oka[b, k, a] = l, ud + 1, True
    t["j2"] = torch.as_tensor(j2, device=device)
    t["pidx"] = torch.as_tensor(np.broadcast_to((np.arange(K) >= nJ).astype(np.int64), (B, K))
                                .copy(), device=device)
    t["cell"] = torch.as_tensor(cell, device=device)
    t["tinc"] = torch.as_tensor(tinc, device=device)
    t["inc_l"] = torch.as_tensor(li, device=device)
    t["inc_u"] = torch.as_tensor(ui, device=device)
    t["inc_ok"] = torch.as_tensor(oka, device=device)
    tjlinc = _pad_stack([e["tjlinc"] for e in E], (max(e["tjlinc"].shape[0] for e in E), 3))
    t["tjlinc"] = torch.as_tensor(tjlinc, device=device)
    t["ltarget"] = torch.as_tensor(np.array([run["sc"]["ltarget"] for run, _ in runs]),
                                   device=device)
    dims = dict(B=B, R=R, J=J, L=L, G=G, K=K, A=A, k0=k0)
    bt = Batch(runs=runs, device=device, t=t, dims=dims, host=dict(E=E, specs=specs))
    bt.t_host = dict(nuc=np.array(nuc_of), lmax_max=np.stack([n["lmax"].max(1) for n in nucs]))
    return bt


# ================================================================================================
# densprepare: the transmissions and rho0 of a residual row
# ================================================================================================


def interp_nodes(tab: dict, nuc: Tensor, ptype: Tensor, eout: Tensor):
    """densprepare.f90:341-352 (and `decay_fast._particles`): `nen` located in float32 on the
    emission grid of each run's nuclide, the three pol2 nodes and weights, and `lmax(nen)`.

    `nuc`, `ptype` (particle type 1..6) and `eout` broadcast to one shape.

    TALYS: densprepare.f90:1 (densprepare), locate.f90:1 (locate)
    Test: GPUFULL
    """
    shape = eout.shape
    nuc = nuc.expand(shape).reshape(-1)
    tix = (ptype - 1).expand(shape).reshape(-1)
    e = eout.reshape(-1)
    ib = tab["ebegin"][nuc, tix + 1]
    ie = tab["eend"][nuc, tix + 1]
    maxen = tab["maxen"][nuc]
    xs = tab["egrid32"][nuc]  # (n, E)
    x = e.to(torch.float32)
    jl = torch.searchsorted(xs, x[:, None], right=True)[:, 0] - 1
    jl = torch.maximum(torch.minimum(jl, ie), ib - 1)
    xib = xs.gather(1, ib[:, None])[:, 0]
    xie = xs.gather(1, ie[:, None])[:, 0]
    jl = torch.where(x == xib, ib, torch.where(x == xie, ie - 1, jl))
    lo = tab["egrid"][nuc, ib]
    nen = torch.where(e < lo, torch.zeros_like(jl), jl)
    centred = (nen > ib + 1) | (nen >= maxen - 1)
    na = torch.where(centred, nen - 1, nen)
    nb, nc = na + 1, na + 2
    eg = tab["egrid"]
    ea, eb, ec = eg[nuc, na], eg[nuc, nb], eg[nuc, nc]
    w1 = (e - eb) * (e - ec) / ((ea - eb) * (ea - ec))
    w2 = (e - ea) * (e - ec) / ((eb - ea) * (eb - ec))
    w3 = (e - ea) * (e - eb) / ((ec - ea) * (ec - eb))
    lm = tab["lmax"][nuc, tix, torch.minimum(torch.clamp(nen, min=0), maxen)]
    rs = lambda v: v.reshape(shape)  # noqa: E731
    return dict(nen=rs(nen), na=rs(na), nb=rs(nb), nc=rs(nc), w1=rs(w1), w2=rs(w2), w3=rs(w3),
                lm=rs(lm), below=rs(e < lo), ok=rs(ib < ie), nuc=rs(nuc), tix=rs(tix))


def primary_residuals(bk: Batch) -> dict:
    """densprepare(primary = .true.) for the seven binary residuals of every run, then comptarget's
    exact incident channel (`target._exact_incident_channel`).

    Returns per type t: `rho` (B, R, J, 2), `lmaxhf` (B, R), and `tjl` (B, R, L, 3) for particles
    or `tg` (B, R, G, 2) for the photon.

    TALYS: densprepare.f90:1 (densprepare), comptarget.f90:358-362
    Test: GPUFULL
    """
    t, d = bk.t, bk.dims
    dev = bk.device
    B, R, J, L = d["B"], d["R"], d["J"], d["L"]
    rows = torch.arange(R, device=dev)
    jj = torch.arange(J, device=dev)
    out = {}
    for ty in range(7):
        nex = t["maxex"][:, ty] + 1
        inrow = rows[None, :] < nex[:, None]
        nl = t["nlast"][:, ty]
        cont = (rows[None, :] > nl[:, None]) & inrow
        keep = (jj[None, None, :] <= t["maxj"][:, ty, :, None]) & cont[:, :, None]
        rho = torch.where(keep[..., None], 1.0 * t["rhogrid"][:, ty], 0.0)
        # discrete levels: one (Ir, parity) cell each, Rboundary (times discfactor above Ntop)
        disc = (rows[None, :] <= torch.minimum(nl, nex - 1)[:, None]) & inrow
        ir = t["jdis"][:, ty].to(torch.int64)
        okir = disc & (ir >= 0) & (ir <= NUMJ)
        pix = torch.where(t["parlev"][:, ty] == -1, 0, 1)
        val = torch.where(rows[None, :] > t["ntop"][:, ty, None],
                          1.0 * t["discfactor"][:, ty, None], torch.ones((B, R), dtype=F64,
                                                                          device=dev))
        bb, rr = torch.nonzero(okir, as_tuple=True)
        rho[bb, rr, ir[bb, rr], pix[bb, rr]] = val[bb, rr]
        rec = dict(rho=rho, nex=nex)
        if ty == 0:
            lmaxhf = torch.full((B, R), bk.runs[0][0]["gammax"], dtype=torch.int64, device=dev)
            rec["tg"] = t["tgam0"]
        else:
            eout = t["etot"][:, None] - t["ex"][:, ty] - t["sep0"][:, ty, None]
            ip = interp_nodes(t, t["nuc"][:, None], torch.full((1, 1), ty, device=dev), eout)
            tj = t["tjl"]
            nuc2 = ip["nuc"]
            ti = ip["tix"]
            v = (ip["w1"][..., None, None] * tj[nuc2, ti, ip["na"]]
                 + ip["w2"][..., None, None] * tj[nuc2, ti, ip["nb"]]
                 + ip["w3"][..., None, None] * tj[nuc2, ti, ip["nc"]])  # (B, R, L, 3)
            lp = torch.arange(L, device=dev)
            kp = lp[None, None, :] <= ip["lm"][..., None]
            v = torch.where(kp[..., None], v, 0.0)
            fn = t["fiso"][:, ty + 1][:, None, None, None]
            tjl = torch.where(v < t["transeps"][t["nuc"]][:, None, None, None], 0.0, v) * fn
            live = (ip["ok"] & inrow)[..., None, None]
            rec["tjl"] = torch.where(live, tjl, 0.0)
            lmaxhf = torch.where(ip["ok"] & inrow, ip["lm"], 0)
        # lmaxhf(nexmax) = lmaxhf(nexmax - 1)
        mx = t["maxex"][:, ty]
        has = mx > 0
        bi = torch.nonzero(has).flatten()
        if bi.numel():
            lmaxhf[bi, mx[bi]] = lmaxhf[bi, mx[bi] - 1]
        lmaxhf = torch.where(inrow, lmaxhf, 0)
        rec["lmaxhf"] = lmaxhf
        out[ty] = rec
    k0 = d["k0"]
    out[k0]["lmaxhf"][:, 0] = t["lmaxinc"]
    # comptarget.f90:358-362: Tjlnex(l, updown, k0, Ltarget) = Tjlinc(updown, l)
    lt = t["ltarget"]
    n_inc = t["tjlinc"].shape[1]
    tj = out[k0]["tjl"]
    if n_inc > tj.shape[2]:
        tj = torch.cat([tj, torch.zeros(B, R, n_inc - tj.shape[2], 3, dtype=F64, device=dev)], 2)
        for ty in range(1, 7):
            if ty != k0 and out[ty]["tjl"].shape[2] < n_inc:
                p = out[ty]["tjl"]
                out[ty]["tjl"] = torch.cat(
                    [p, torch.zeros(B, R, n_inc - p.shape[2], 3, dtype=F64, device=dev)], 2)
    ninc = torch.as_tensor([e["lmaxinc"] + 1 for e in bk.host["E"]], device=dev)
    lp = torch.arange(n_inc, device=dev)
    okl = (lp[None, :] < torch.minimum(ninc, torch.full_like(ninc, n_inc))[:, None])
    okl = okl & (lt <= t["maxex"][:, k0])[:, None]
    ar = torch.arange(B, device=dev)
    row = tj[ar, lt]  # (B, L', 3)
    row[:, :n_inc] = torch.where(okl[..., None], t["tjlinc"], row[:, :n_inc])
    tj[ar, lt] = row
    out[k0]["tjl"] = tj
    return out


# ================================================================================================
# comptarget
# ================================================================================================


def _mask_for(j2: Tensor, irs2: Tensor, parspin2: int, spin2: int, L: int,
              photon: bool) -> Tensor:
    """`target_batch._mask_for` with a leading run axis: j2 (B, K), irs2 (B, K, I) -> bool
    (B, K, I, L, 3).

    TALYS: compprepare.f90:1 (compprepare)
    Test: GPUFULL
    """
    dev = j2.device
    lp = torch.arange(L, device=dev)
    lo = (j2[..., None] - irs2).abs()
    hi = j2[..., None] + irs2
    anom = (lo + parspin2) % 2
    if bool(anom.any()):
        # GPUC: OPEN3M's A2 (a discrete level of impossible 2J parity), as target_batch._mask_for
        from physics.hf.compound.prepare import anomalous_exit_mask

        return anomalous_exit_mask(lo, hi, anom, parspin2, spin2, L, photon)
    if photon:
        jjp = 2 * lp
        ok = ((jjp >= lo[..., None]) & (jjp <= hi[..., None]) & ((jjp - lo[..., None]) % 2 == 0)
              & (lp >= 1))
        out = torch.zeros(ok.shape + (3,), dtype=torch.bool, device=dev)
        out[..., 1] = ok
        return out
    ud = torch.tensor([-1, 0, 1], device=dev)
    jj2p = 2 * lp[:, None] + ud[None, :] * spin2  # (L, 3)
    dj = jj2p - 2 * lp[:, None]
    ok_s = (dj.abs() <= parspin2) & ((dj - parspin2) % 2 == 0) & (jj2p >= 0)
    ok_s = ok_s & (2 * lp[:, None] >= (jj2p - parspin2).abs())
    ok_j = ((jj2p >= lo[..., None, None]) & (jj2p <= hi[..., None, None])
            & ((jj2p - lo[..., None, None]) % 2 == 0))
    return ok_j & ok_s


def _degrees_of_freedom(tav: Tensor, st: Tensor, wfcfactor: int) -> Tensor:
    """`wfc.degrees_of_freedom` (WFCfactor 1, TALYS's default)."""
    if wfcfactor != 1:
        from physics.hf.compound import wfc

        return wfc.degrees_of_freedom(tav, st, wfcfactor)
    return torch.clamp(1.78 + (tav ** 1.212 - 0.78) * torch.exp(-0.228 * st), max=2.0)


def _prepare_type(bk: Batch, res: dict, ty: int, sel: Tensor) -> dict:
    """`target_batch._prepare` for exit type `ty` on runs `sel`.

    TALYS: compprepare.f90:1 (compprepare)
    Test: GPUFULL
    """
    t, d = bk.t, bk.dims
    dev = bk.device
    r = res[ty]
    photon = ty == 0
    Bc = sel.numel()
    R, J = d["R"], d["J"]
    rho = r["rho"][sel]
    # cut the residual spin axis after its last cell holding a rho0 comptarget reads (>= 1e-20)
    jn = torch.nonzero((rho >= 1.0e-20).flatten(0, 1).any(0).any(1)).flatten()
    J = int(jn[-1]) + 1 if jn.numel() else 1
    rho = rho[:, :, :J].contiguous()
    lmaxhf = r["lmaxhf"][sel]
    maxj = t["maxj"][sel, ty]
    nl = t["nlast"][sel, ty]
    mx = t["maxex"][sel, ty]
    rows = torch.arange(R, device=dev)
    disc = rows[None, :] <= nl[:, None]
    j2 = t["j2"][sel]
    K = j2.shape[1]
    pidx = t["pidx"][sel]
    base = (j2[:, 0] + PARSPIN2[ty]) % 2
    irs2c = 2 * torch.arange(J, device=dev)[None, :] + base[:, None]  # (Bc, J)
    if photon:
        tg = r["tg"][sel]  # (Bc, R, G, 2)
        L = tg.shape[2]
        lp = torch.arange(L, device=dev)
        Tn = torch.zeros((Bc, 2, R, L, 3), dtype=F64, device=dev)
        Tn[:, 0, :, :, 1] = tg[:, :, lp, (lp % 2 == 0).to(torch.int64)]
        Tn[:, 1, :, :, 1] = tg[:, :, lp, (lp % 2 == 1).to(torch.int64)]
        raw = None
    else:
        raw = r["tjl"][sel]
        ln = torch.nonzero((raw != 0.0).any(3).flatten(0, 1).any(0)).flatten()
        Lc = max(int(ln[-1]) + 1 if ln.numel() else 1, 1)
        raw = raw[:, :, :Lc].contiguous()
        L = raw.shape[2]
        lp = torch.arange(L, device=dev)
        Tn = torch.stack([torch.where((lp % 2 == c)[None, None, :, None], raw, 0.0)
                          for c in (0, 1)], dim=1)
    lm = lp[None, None, :] <= lmaxhf[:, :, None]  # (Bc, R, L)
    Tn = torch.where(lm[:, None, :, :, None], Tn, 0.0)
    vc = (irs2c[:, None, :] <= (2 * maxj)[:, :, None]) & ~disc[:, :, None]
    rho_c = torch.where(vc[..., None] & (rho >= 1.0e-20), rho, 0.0)  # (Bc, R, J, 2)
    M = _mask_for(j2, irs2c[:, None, :].expand(Bc, K, J), PARSPIN2[ty], SPIN2[ty], L, photon)
    Mf = M.to(F64)
    Rr = torch.einsum("bnip,bcnlu->bciplu", rho_c, Tn)
    MR = torch.einsum("bkilu,bciplu->bkcp", Mf, Rr)
    D0 = MR[:, :, 0, 0] + MR[:, :, 1, 1]
    D1 = MR[:, :, 1, 0] + MR[:, :, 0, 1]
    Dt = torch.where(pidx == 0, D0, D1)
    ND = int(torch.minimum(nl, mx).max()) + 1
    nd = torch.minimum(nl, mx) + 1
    jdis2 = torch.where(rows[None, :] <= nl[:, None],
                        (2.0 * t["jdis"][sel, ty].to(torch.float32)).to(torch.int64), -1)
    jd2 = jdis2[:, :ND]
    Md = _mask_for(j2, jd2[:, None, :].expand(Bc, K, ND), PARSPIN2[ty], SPIN2[ty], L, photon)
    Md = Md & (torch.arange(ND, device=dev)[None, None, :] < nd[:, None, None])[..., None, None]
    # GPUC: OPEN3M's cap on an anomalous level, l2' = 2 l' + 1 <= 2 lmaxhf (target_batch._prepare)
    anom_d = (j2[:, :1] + jd2 + PARSPIN2[ty]) % 2  # (Bc, ND)
    capd = (2 * lp[None, None, :] + anom_d[:, :, None]) <= 2 * lmaxhf[:, :ND, None]
    Md = Md & capd[:, None, :, :, None]
    Mdf = Md.to(F64)
    tot_d = torch.einsum("bknlu,bcnlu->bkcn", Mdf, Tn[:, :, :ND])
    ird = torch.div(jd2, 2, rounding_mode="floor")
    pd = (t["parlev"][sel, ty, :ND] > 0).to(torch.int64)
    ok = (ird >= 0) & (ird < J) & (torch.arange(ND, device=dev)[None, :] < nd[:, None])
    irc = ird.clamp(0, J - 1)
    ar = torch.arange(ND, device=dev)
    bi = torch.arange(Bc, device=dev)[:, None]
    rv = rho[bi, ar[None, :], irc, pd]
    rho_d = torch.where(ok & (rv >= 1.0e-20), rv, 0.0)
    cm = (pidx[:, :, None] != pd[:, None, :]).to(torch.int64)  # (Bc, K, ND)
    tot_dk = tot_d.gather(2, cm[:, :, None, :]).squeeze(2)  # (Bc, K, ND)
    Dt = Dt + (tot_dk * rho_d[:, None, :]).sum(2)
    parm = ((lp[None, None, None, :] % 2) == cm[..., None]).to(F64)  # (Bc, K, ND, L)
    return dict(Tn=Tn, rho_c=rho_c, M=Mf, D=Dt, raw=raw, lm=lm, L=L, nd=nd, ND=ND, ird=irc,
                pd=pd, ok=ok, rho_d=rho_d, tot_dk=tot_dk, Md=Mdf, parm=parm, pidx=pidx)


def _feed_type(pop: Tensor, ty: int, p: dict, w: Tensor) -> None:
    """`target_batch._feed_type` with a run axis: add sum_cells w * rho0 * sum T to pop[:, ty]."""
    pidx = p["pidx"]
    dev = pop.device
    same = (pidx[:, :, None] == torch.arange(2, device=dev)[None, None, :]).to(F64)
    V0 = torch.einsum("bkilu,bk,bkq->biqlu", p["M"], w, same)
    V1 = torch.einsum("bkilu,bk,bkq->biqlu", p["M"], w, 1.0 - same)
    TV = (torch.einsum("bnlu,biqlu->bniq", p["Tn"][:, 0], V0)
          + torch.einsum("bnlu,biqlu->bniq", p["Tn"][:, 1], V1))
    contrib = p["rho_c"] * TV
    fd = (p["tot_dk"] * w[:, :, None]).sum(1) * p["rho_d"]  # (Bc, ND)
    _add_discrete(contrib, fd, p)
    pop[:, ty, :, : contrib.shape[2]] += contrib


def _add_discrete(contrib: Tensor, fd: Tensor, p: dict) -> None:
    Bc, ND = fd.shape
    bi = torch.arange(Bc, device=fd.device)[:, None].expand(Bc, ND)
    ar = torch.arange(ND, device=fd.device)[None, :].expand(Bc, ND)
    contrib.index_put_((bi, ar, p["ird"], p["pd"]), torch.where(p["ok"], fd, 0.0),
                       accumulate=True)


def _chunks(cost: np.ndarray, budget: float, wfc: np.ndarray) -> list[np.ndarray]:
    """Groups of runs with the same width-fluctuation flag, in ascending cost, whose padded cost
    (runs x the group's largest cost, what the padded intermediates hold) stays under `budget`
    (a run over it is a group of its own)."""
    out, cur, top = [], [], 0.0
    for b in np.lexsort((cost, ~wfc)):
        c = float(cost[b])
        if cur and ((len(cur) + 1) * max(top, c) > budget or wfc[cur[-1]] != wfc[b]):
            out.append(np.array(cur))
            cur, top = [], 0.0
        cur.append(int(b))
        top = max(top, c)
    if cur:
        out.append(np.array(cur))
    return out


CT_BUDGET = float(__import__("os").environ.get("GPUFULL_CT_BUDGET", "3.0e7"))
# GPU3: comptarget on channel lists with spin-window sums (`gpu_full_ct`); 0 = the dense masks
CT_WINDOWS = __import__("os").environ.get("GPU3_CT", "1") != "0"


def comptarget(bk: Batch, res: dict, budget: float | None = None) -> dict:
    """comptarget.f90 for every run: `pop` (B, 7, R, J, 2), the compound elastic and xsbinary.

    `target_batch.case_moldauer` where the run has width fluctuations, `case_nowfc` where it
    has not, over groups of runs sized to `budget` elements of the largest intermediate.

    TALYS: comptarget.f90:1 (comptarget), molprepare.f90:1 (molprepare), moldauer.f90:1
    Test: GPUFULL
    """
    from physics.hf.compound import wfc

    if CT_WINDOWS:
        from physics.hf import gpu_full_ct

        return gpu_full_ct.comptarget(bk, res)
    budget = CT_BUDGET if budget is None else budget
    t, d = bk.t, bk.dims
    dev = bk.device
    B, R, J = d["B"], d["R"], d["J"]
    k0 = d["k0"]
    pop = torch.zeros((B, 7, R, J, 2), dtype=F64, device=dev)
    x, wts = wfc.gauss_laguerre(dev)
    nopen = torch.zeros(B, dtype=torch.int64, device=dev)
    for ty in range(1, 7):
        nopen += (res[ty]["tjl"] > 1.0e-30).flatten(1).sum(1)
    ncell = t["cell"].sum(1)
    Lmax = max(res[ty]["tjl"].shape[2] for ty in range(1, 7))
    host = torch.stack([nopen, ncell]).cpu().numpy()
    wfch = t["wfc"].cpu().numpy()
    K = t["j2"].shape[1]
    dense = float(K * R * Lmax * 3 * 2)
    cost = np.where(wfch, np.maximum(K * 32.0 * np.maximum(host[0], 1), dense), dense)
    import time

    for grp in _chunks(cost, budget, wfch):
        t0 = time.perf_counter()
        sel = torch.as_tensor(grp, device=dev)
        Bc = sel.numel()
        prep = {ty: _prepare_type(bk, res, ty, sel) for ty in range(7)}
        t0 = stage("ct:prepare", dev, t0)
        denom = prep[0]["D"] + prep[1]["D"]
        for ty in range(2, 7):
            denom = denom + prep[ty]["D"]
        cellm = t["cell"][sel]
        live = cellm & (denom != 0.0)
        cn = t["cn"][sel]
        j2 = t["j2"][sel].to(F64)
        sub = torch.zeros((Bc, 7, R, J, 2), dtype=F64, device=dev)
        if bool(wfch[grp[0]]):
            _moldauer(bk, sel, prep, denom, live, sub, x, wts)
        else:
            # no width fluctuations: w = CNfactor (J2 + 1) / denom * feed
            feed = torch.where(live, t["tinc"][sel].sum(2), 0.0)
            wn = torch.where(live, cn[:, None] * (j2 + 1.0) / torch.where(live, denom, 1.0)
                             * feed, 0.0)
            for ty in range(7):
                _feed_type(sub, ty, prep[ty], wn)
        pop[sel] = sub
        stage("ct:moldauer" if bool(wfch[grp[0]]) else "ct:nowfc", dev, t0)
        if STAGE_TIMES is not None:
            STAGE_TIMES["ct:groups"] = STAGE_TIMES.get("ct:groups", 0) + 1
        del prep, sub
    ar = torch.arange(B, device=dev)
    lt = t["ltarget"]
    okl = lt <= t["maxex"][:, k0]
    el = torch.where(okl, pop[ar, k0, lt].sum((1, 2)), 0.0)
    xsb = pop.sum((2, 3, 4))
    xsb[:, k0] = xsb[:, k0] - pop[ar, k0, lt].sum((1, 2))
    return dict(pop=pop, el=el, xsbinary=xsb)


def _moldauer(bk: Batch, sel: Tensor, prep: dict, denom: Tensor, live: Tensor, sub: Tensor,
              x: Tensor, wts: Tensor) -> None:
    """`target_batch.case_moldauer`'s integral and population contraction, runs `sel` x cells.

    TALYS: molprepare.f90:1 (molprepare), moldauer.f90:1 (moldauer), comptarget.f90:1
    Test: GPUFULL
    """
    t, d = bk.t, bk.dims
    dev = bk.device
    Bc = sel.numel()
    K = t["j2"].shape[1]
    k0 = d["k0"]
    wf = int(t["wfcfactor"][sel][0])
    st = torch.where(live, denom, 1.0)  # (Bc, K); dead cells are masked at the end
    pidx = prep[0]["pidx"]
    tinc = t["tinc"][sel]
    cn = t["cn"][sel]
    nu_inc = _degrees_of_freedom(tinc, st[:, :, None], wf)
    import time
    t0 = time.perf_counter()
    # open exit channels of each run, in `_case`'s block order (types 1..6, then row, l, updown)
    t_list, r_list = [], []
    for ty in range(1, 7):
        p = prep[ty]
        Bn, R_, L_ = p["raw"].shape[0], p["raw"].shape[1], p["raw"].shape[2]
        tt = torch.where(p["raw"] > 1.0e-30, p["raw"], 0.0)
        t_list.append(tt.reshape(Bn, -1))
        # weight sums: sum over (Ir, P') of rho0 * allowed
        lp = torch.arange(L_, device=dev)
        # Rw[k, n, l, u] = sum_i M[k, i, l, u] rho_c[n, i, P(k) xor (l mod 2)]
        Rw = None
        for pk in (0, 1):
            rs = p["rho_c"][..., (pk ^ (lp % 2))]  # (Bc, R, J, L)
            v = torch.einsum("bkilu,bnil->bknlu", p["M"], rs)
            Rw = v if Rw is None else torch.where((pidx == 1)[:, :, None, None, None], v, Rw)
        Rd = (p["rho_d"][:, None, :, None, None] * p["Md"] * p["parm"][..., None])
        ND = p["ND"]
        Rw[:, :, :ND] = Rw[:, :, :ND] + Rd
        Rw = Rw * p["lm"][:, None, :, :, None].to(F64)
        r_list.append(Rw.reshape(Bn, K, -1))
    t0 = stage("mol:rw", dev, t0)
    t_all = torch.cat(t_list, 1)  # (Bc, F)
    r_all = torch.cat(r_list, 2)  # (Bc, K, F)
    openm = t_all > 0.0
    nch = int(openm.sum(1).max()) if openm.any() else 0
    nch = max(nch, 1)
    order = torch.argsort((~openm).to(torch.int8), dim=1, stable=True)[:, :nch]
    t_nz = t_all.gather(1, order)
    t_nz = torch.where(openm.gather(1, order), t_nz, 0.0)  # (Bc, nch)
    r_nz = r_all.gather(2, order[:, None, :].expand(Bc, K, nch))
    gam = prep[0]["D"]
    nu_exit = _degrees_of_freedom(t_nz[:, None, :], st[:, :, None], wf)  # (Bc, K, nch)
    eps = (2.0 * t_nz[:, None, None, :] * x[None, None, :, None]
           / (st[:, :, None, None] * nu_exit[:, :, None, :]))
    livee = eps > 1.0e-30
    logterm = torch.where(livee, torch.log1p(torch.where(livee, eps, 0.0)), 0.0)
    factor = (-nu_exit * 0.5 * r_nz)[:, :, None, :] * logterm
    expo = gam[:, :, None] * x[None, None, :] / st[:, :, None]
    capt = torch.where(expo > 80.0, 0.0, torch.exp(-torch.clamp(expo, max=80.0)))
    prod = wts * wts * torch.exp(x) * torch.exp(factor.sum(3)) * capt  # (Bc, K, M)
    fa = 2.0 * tinc / (st[:, :, None] * nu_inc)
    da = 1.0 + x[None, None, :, None] * fa[:, :, None, :]  # (Bc, K, M, A)
    H = (tinc[:, :, None, :] / da).sum(3)
    PH = prod * H
    gg = PH.sum(2)  # (Bc, K)
    ea = (prod[..., None] * (2.0 / nu_inc)[:, :, None, :] / da ** 2).sum(2)  # (Bc, K, A)
    t0 = stage("mol:integral", dev, t0)
    j2 = t["j2"][sel].to(F64)
    pref = torch.where(live, cn[:, None] * (j2 + 1.0) / st, 0.0)
    _feed_type(sub, 0, prep[0], pref * gg)
    for ty in range(1, 7):
        p = prep[ty]
        raw = p["raw"]
        _, R_, L_, _ = raw.shape
        flat = raw.reshape(Bc, -1)
        opn = flat > 0.0
        Gb = gg[:, :, None].expand(Bc, K, flat.shape[1]).clone()
        no = int(opn.sum(1).max())
        if no:
            od = torch.argsort((~opn).to(torch.int8), dim=1, stable=True)[:, :no]
            om = opn.gather(1, od)
            to = torch.where(om, flat.gather(1, od), 0.0)
            nu_b = _degrees_of_freedom(to[:, None, :], st[:, :, None], wf)
            fb = 2.0 * to[:, None, :] / (st[:, :, None] * nu_b)
            val = (PH[..., None] / (1.0 + x[None, None, :, None] * fb[:, :, None, :])).sum(2)
            cur = Gb.gather(2, od[:, None, :].expand(Bc, K, no))
            Gb.scatter_(2, od[:, None, :].expand(Bc, K, no),
                        torch.where(om[:, None, :], val, cur))
        Y = (pref[:, :, None] * (flat[:, None, :] * Gb)).reshape(Bc, K, R_, L_, 3)
        Y = Y * p["lm"][:, None, :, :, None].to(F64)
        lp = torch.arange(L_, device=dev)
        parq = ((lp[None, None, None, :] % 2)
                == (pidx[:, :, None] != torch.arange(2, device=dev)[None, None, :])
                .to(torch.int64)[..., None]).to(F64)  # (Bc, K, P', L)
        MY = torch.einsum("bkilu,bkql->bkqilu", p["M"], parq)
        TV = torch.einsum("bkqilu,bknlu->bniq", MY, Y)
        contrib = p["rho_c"] * TV
        ND = p["ND"]
        fd = torch.einsum("bknlu,bknlu->bn", p["Md"] * p["parm"][..., None], Y[:, :, :ND]) \
            * p["rho_d"]
        _add_discrete(contrib, fd, p)
        if ty == k0:
            # the elastic diagonal (ielas = 1): exit (l', j') = incident (l, j) at Ltarget
            lt = t["ltarget"][sel]
            li = t["inc_l"][sel]
            ui = t["inc_u"][sel]
            oka = t["inc_ok"][sel] & (li < L_)
            lic = li.clamp(max=L_ - 1)
            bi = torch.arange(Bc, device=dev)[:, None, None]
            ki = torch.arange(K, device=dev)[None, :, None]
            ltc = lt.clamp(max=ND - 1)[:, None, None]
            wgt = (p["Md"][bi, ki, ltc, lic, ui] * p["parm"][bi, ki, ltc, lic]
                   * p["lm"][bi, lt[:, None, None], lic].to(F64))
            term = wgt * raw[bi, lt[:, None, None], lic, ui] * tinc * ea
            ex = torch.where(oka, term, 0.0).sum(2)  # (Bc, K)
            okel = (lt < p["nd"]) & p["ok"][torch.arange(Bc, device=dev), lt.clamp(max=ND - 1)]
            val = (pref * ex).sum(1) * p["rho_d"][torch.arange(Bc, device=dev),
                                                    lt.clamp(max=ND - 1)]
            bsel = torch.arange(Bc, device=dev)
            contrib.index_put_((bsel, lt, p["ird"][bsel, lt.clamp(max=ND - 1)],
                                p["pd"][bsel, lt.clamp(max=ND - 1)]),
                               torch.where(okel, val, 0.0), accumulate=True)
        sub[:, ty, :, : contrib.shape[2]] += contrib
    stage("mol:feed", dev, t0)


# ================================================================================================
# binary
# ================================================================================================


def _sfactor_levels(bk: Batch, sf_state: dict | None) -> tuple[list, list, dict]:
    """GPUC (OPEN4 D): the order `sfactor` is carried in. Each run's state comes from the run of
    the same nuclide at the next lower energy index in this batch, else from `sf_state` (an
    earlier batch), else zero. Returns per level [(runs, in-batch previous run or -1)], the
    runs whose carried energy is not the previous declared one, and each nuclide's last run."""
    by: dict = {}
    for b, (r, i) in enumerate(bk.runs):
        by.setdefault((r["Z"], r["A"]), []).append((i, b))
    levels: list = []
    gaps = []
    last = {}
    for name, lst in by.items():
        lst.sort()
        for lv, (i, b) in enumerate(lst):
            if lv:
                pi, pb = lst[lv - 1]
            else:
                pi = sf_state[name][0] if sf_state and name in sf_state else -1
                pb = -1
            if i > 0 and pi != i - 1:
                gaps.append((name, i))
            while len(levels) <= lv:
                levels.append(([], []))
            levels[lv][0].append(b)
            levels[lv][1].append(pb)
        last[name] = lst[-1]
    return levels, gaps, last


def binary(bk: Batch, ct: dict, sf_state: dict | None = None) -> dict:
    """binary.f90 with `BinaryState` carried across the energies (what `ChainedFull.cases` seeds
    the cascade from since OPEN4 D): per type t the populations `xspop` (B, R, J, 2), `xspopex`
    (B, R) and `feedbinary` (B, R), and the totals `xselastot`, `xsnonel`, `xscompel`.

    `sfactor` is run-scoped in TALYS (`strucinitial.f90:484` zeroes it once per run) and is only
    overwritten where a bin holds more than popepsA, so a bin below it takes an earlier energy's
    compound spin shape. GPUC: the batch walks its runs in energy order per nuclide
    (`_sfactor_levels`); `sf_state` carries it into a later batch. A run whose previous declared
    energy was in neither is flagged `sfactor_gaps` (it starts from the nearest one carried).

    TALYS: binary.f90:1 (binary), spindis.f90:1 (spindis)
    Test: GPUFULL
    """
    t, d = bk.t, bk.dims
    dev = bk.device
    B, R, J = d["B"], d["R"], d["J"]
    k0 = d["k0"]
    E = bk.host["E"]
    rows = torch.arange(R, device=dev)
    if "b_dd" not in t:
        dd = np.zeros((B, 7, R))
        ald = np.zeros((B, 7, R))
        spc = np.ones((B, 7, R))
        pex = np.zeros((B, 7, R))
        sc = np.zeros((B, 12))
        tots = np.zeros((B, 3, 7))
        for b, e in enumerate(E):
            bn = e["binary"]
            for ty, g in bn["grids"].items():
                n = g["maxex"] + 1
                dd[b, ty, :n] = g["xsdirdisc"][:n]
                spc[b, ty, :n] = g["spincut"][:n]
                col = e["pex"].get(ty)
                if col is not None:
                    k = min(n, len(col))
                    pex[b, ty, :k] = col[:k]
            sc[b] = (bn["popeps"], bn["xseps"], bn["xsreacinc"], bn["xselasinc"],
                     bn["flagpreeq"], bn["maxjph"], bn["pespinmodel"], bn["ltarget"],
                     bn["targetspin2"], bn["target_parity"], 0, 0)
            tots[b] = (bn["xsdirdisctot"], bn["xspreeqtot"], bn["xsgrtot"])
        t["b_dd"] = torch.as_tensor(dd, device=dev)
        t["b_spincut"] = torch.as_tensor(spc, device=dev)
        t["b_pex"] = torch.as_tensor(pex, device=dev)
        t["b_sc"] = torch.as_tensor(sc, device=dev)
        t["b_tots"] = torch.as_tensor(tots, device=dev)
    sc = t["b_sc"]
    popeps, xseps, reac, elasinc = sc[:, 0], sc[:, 1], sc[:, 2], sc[:, 3]
    flagpreeq = sc[:, 4] != 0
    maxjph = sc[:, 5].to(torch.int64)
    pespin = sc[:, 6].to(torch.int64)
    ltar = sc[:, 7].to(torch.int64)
    tspin2 = sc[:, 8].to(torch.int64)
    tpar = sc[:, 9].to(torch.int64)
    pop_all = ct["pop"]
    out = dict(xspop={}, xspopex={}, feedbinary={}, x0={}, nl={})
    sf_levels, out["sfactor_gaps"], sf_last = _sfactor_levels(bk, sf_state)
    sf_idx = []
    for bs, pbs in sf_levels:
        bt = torch.as_tensor(bs, device=dev)
        if all(p < 0 for p in pbs):
            sf_idx.append((bt, None))
        else:
            pbt = torch.as_tensor([max(p, 0) for p in pbs], device=dev)
            sf_idx.append((bt, (pbt, torch.as_tensor([p >= 0 for p in pbs], device=dev))))
    ar = torch.arange(B, device=dev)
    for ty in range(7):
        nmax = t["maxex"][:, ty]
        inrow = rows[None, :] <= nmax[:, None]
        nl = torch.minimum(t["nlast"][:, ty], nmax)
        pop = torch.where(inrow[:, :, None, None], pop_all[:, ty], 0.0)
        pex = pop.sum((-2, -1))
        dd = t["b_dd"][:, ty]
        lvm = rows[None, :] <= nl[:, None]
        jidx = t["jdis"][:, ty].to(torch.int64)
        pidx = torch.where(t["parlev"][:, ty] == -1, 0, 1)
        live = lvm & (dd != 0.0)
        bb, rr = torch.nonzero(live, as_tuple=True)
        pop.index_put_((bb, rr, jidx[bb, rr], pidx[bb, rr]), dd[bb, rr], accumulate=True)
        pex = torch.where(live, pex + dd, pex)
        x0 = torch.where(lvm, pex, 0.0)
        # pre-equilibrium spread (binary.f90:222-257), sfactor from a fresh state (zero)
        mj = int(maxjph.max()) + 1
        jj = torch.arange(mj, dtype=F64, device=dev)
        ncont = nmax - nl
        on = flagpreeq & (ncont > 0) & (pespin <= 2)
        popepsA = popeps / torch.clamp(5 * nmax, min=1).to(F64)
        sl = (rows[None, :] > nl[:, None]) & inrow & on[:, None]  # (B, R)
        jm = jj[None, :] <= maxjph[:, None].to(F64)  # (B, mj)
        has = pex > popepsA[:, None]
        ratio = pop[:, :, :mj, :] / torch.where(pex > 0, pex, 1.0)[:, :, None, None]
        hs = (has & sl)[:, :, None, None]
        wr = (sl[:, :, None] & jm[:, None, :])[..., None]
        inc = torch.zeros_like(ratio)
        for name, (_, sv) in (sf_state or {}).items():
            if name in sf_last and ty in sv:
                v = sv[ty]
                rr_, jj_ = min(R, v.shape[0]), min(mj, v.shape[1])
                bs = [b for b, (r, _) in enumerate(bk.runs) if (r["Z"], r["A"]) == name]
                inc[bs, :rr_, :jj_] = v[:rr_, :jj_].to(dev)
        if len(sf_levels) == 1:
            sf = torch.where(hs, ratio, inc)
            state = torch.where(wr, sf, inc)
        else:
            sf = torch.empty_like(ratio)
            state = torch.empty_like(ratio)
            for bs, pbs in sf_idx:
                old = inc[bs] if pbs is None else torch.where(
                    pbs[1][:, None, None, None], state[pbs[0]], inc[bs])
                new = torch.where(hs[bs], ratio[bs], old)
                sf[bs] = new
                state[bs] = torch.where(wr[bs], new, old)
        if sf_state is not None:
            for name, (i, b) in sf_last.items():
                sf_state.setdefault(name, [i, {}])[1][ty] = state[b].clone()
                sf_state[name][0] = i
        wig = _spindis(t["b_spincut"][:, ty][:, :, None], jj[None, None, :]) * 0.5
        use_sf = (pespin == 1)[:, None, None, None] & (sf > 0.0)
        spread = torch.where(use_sf, sf, wig[..., None])
        ppx = t["b_pex"][:, ty]
        add = spread * ppx[:, :, None, None]
        add = torch.where((sl[:, :, None] & jm[:, None, :])[..., None], add, 0.0)
        pop[:, :, :mj] = pop[:, :, :mj] + add
        pex = torch.where(sl, pex + ppx, pex)
        out["xspop"][ty] = pop
        out["xspopex"][ty] = pex
        out["feedbinary"][ty] = pex.clone()
        out["x0"][ty] = x0
        out["nl"][ty] = nl
    x0k = out["x0"][k0]
    ltok = ltar <= out["nl"][k0]
    xscompel = torch.where(ltok, x0k[ar, ltar.clamp(max=R - 1)], 0.0)
    out["xselastot"] = elasinc + xscompel
    out["xsnonel"] = torch.clamp(reac - xscompel, min=0.0)
    out["xscompel"] = xscompel
    bi = torch.nonzero(ltok).flatten()
    if bi.numel():
        lt = ltar[bi]
        out["feedbinary"][k0][bi, lt] = 0.0
        out["xspopex"][k0][bi, lt] = 0.0
        out["xspop"][k0][bi, lt, torch.div(tspin2[bi], 2, rounding_mode="floor"),
                         torch.where(tpar[bi] == -1, 0, 1)] = 0.0
    return out


def _spindis(sc: Tensor, rspin: Tensor) -> Tensor:
    sigma22 = 2.0 * sc
    return (2.0 * rspin + 1.0) / sigma22 * torch.exp(-((rspin + 0.5) ** 2) / sigma22)


# ================================================================================================
# a whole batch
# ================================================================================================


STAGE_TIMES: dict | None = None  # stage -> seconds, when a caller sets a dict (synchronizes)


def stage(name: str, device, t0: float) -> float:
    """Book the wall time since `t0` to `name` in `STAGE_TIMES` (a no-op when that is None)."""
    import time

    if STAGE_TIMES is None:
        return t0
    th = time.perf_counter()
    if device.type == "cuda":
        torch.cuda.synchronize()
    t1 = time.perf_counter()
    STAGE_TIMES[name] = STAGE_TIMES.get(name, 0.0) + (t1 - t0)
    # the device's backlog when the host reached the stage's end (a lower bound of its compute)
    STAGE_TIMES["wait:" + name] = STAGE_TIMES.get("wait:" + name, 0.0) + (t1 - th)
    return t1


def run_batch(runs: list, device, chan_state: dict | None = None) -> dict:
    """Every channel of every run of `runs` [(set-up run, energy index)]: `engine.run`'s
    `total`, `elastic`, `nonelastic` and `xs??????` exclusive channels, (B,) tensors, plus the
    flags of runs the batch could not reproduce.

    TALYS: talysreaction.f90:1 (talysreaction)
    Test: GPUFULL
    """
    import time

    from physics.hf.gpu_full_cascade import cascade
    from physics.hf.gpu_full_channels import ChannelWalk
    from physics.hf.gpu_full_setup import stack_run

    t0 = time.perf_counter()
    for run in {id(r): r for r, _ in runs}.values():
        stack_run(run)
    bk = pack(runs, device)
    t0 = stage("pack", device, t0)
    res = primary_residuals(bk)
    del bk.t["rhogrid"]  # GPU3: read by primary_residuals only; the cascade gathers its own
    t0 = stage("primary", device, t0)
    ct = comptarget(bk, res)
    t0 = stage("comptarget", device, t0)
    del res
    bn = binary(bk, ct, None if chan_state is None else chan_state.setdefault("_sfactor", {}))
    t0 = stage("binary", device, t0)
    del ct
    cw = ChannelWalk(bk, chan_state)
    t0 = stage("channels-init", device, t0)
    flags = cascade(bk, bn, cw)
    t0 = stage("cascade", device, t0)
    out = cw.results()
    t0 = stage("channels-results", device, t0)
    out["elastic"] = bn["xselastot"]
    out["nonelastic"] = bn["xsnonel"]
    out["total"] = bn["xselastot"] + bn["xsnonel"]
    flags["sfactor_gaps"] = bn["sfactor_gaps"]
    out["_flags"] = flags
    return out
