"""comptarget.f90 without width fluctuations, with every compound (J, parity) at once.

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

Task: SPEED0 (the speed work; no physics of its own). Acceptance test: A-cn1 / SPEED0 golden.

TALYS routines this computes:
    comptarget.f90:1 (comptarget)      -- the flagwidth = .false. branch
    compprepare.f90:1 (compprepare)    -- the exit-channel selection rules it reads

Above `ewfc` (and at `widthmode 0`) comptarget's population of residual state
(nexout, Ir, P') is `sum_(J,P) CNfactor (J2+1) / denomhf(J,P) * feed(J,P) * rho0 *
sum_(l', j') T`, with `feed` the incident transmission summed over (l, j). `target._case` runs
that as a loop over (J, parity) calling `prepare.exit_channel_sums`, which materialises
(Nex, Ir, P', l', updown) weights per cell. The selection rule that depends on J is only
`|J2 - Irspin2| <= jj2' <= J2 + Irspin2` with its parity condition, a function of
(J, Ir, l', updown) and not of the bin, so the sums over cells can be taken inside the sums over
(l', updown) exactly as `continuum._compound_decay_factored` does for the cascade. All terms
are non-negative; the results differ from the per-cell loop by rounding.

FISSB: a fissioning target is covered too; fission is one more `(K,)` term of `denomhf` and of
the output, and with Moldauer's correction its Hill-Wheeler humps join the node product
(`compound.fission_batch_target`).

Two of `_residual_spin2`'s masks are J dependent and are dropped here because `ok_j` already
implies them: a continuum spin with Irspin2 > J2 + parspin2 + 2 lmaxhf has no allowed (l', j')
with l' <= lmaxhf. Not covered (the caller keeps the loop): a photon transmission that depends on
the compound J or parity.
"""

from __future__ import annotations

from functools import lru_cache

import numpy as np
import torch
from torch import Tensor

from physics.hf.compound import fission_batch_target as fbt
from physics.hf.compound.prepare import NUMJ, CompoundInputs, anomalous_exit_mask, incident_channels
from physics.hf.core.tensors import DTYPE


@lru_cache(maxsize=256)
def _exit_mask(j2par: int, nj2: tuple[int, ...], parspin2: int, spin2: int, L: int,
               photon: bool, device=None) -> Tensor:
    """`ok_j & ok_s` of `prepare.exit_channel_sums` for every compound J2 in `nj2`, continuum
    residual spin index Ir (Irspin2 = 2 Ir + (J2 + parspin2) % 2), l' and updown. Float
    (K, numJ+1, L, 3); photons use jj2' = 2 l' and only the updown = 0 slot, l' >= 1.

    TALYS: compprepare.f90:1 (compprepare)
    Test: A-cn1 / SPEED0 golden
    """
    j2 = torch.tensor(nj2, device=device)
    irs2 = 2 * torch.arange(NUMJ + 1, device=device) + (j2par + parspin2) % 2
    return _mask_for(j2, irs2[None, :].expand(len(nj2), -1), parspin2, spin2, L, photon)


def _mask_for(j2: Tensor, irs2: Tensor, parspin2: int, spin2: int, L: int,
              photon: bool) -> Tensor:
    """`ok_j & ok_s` for compound J2 (K,) against residual Irspin2 (K, R). (K, R, L, 3).

    OPEN3M: a discrete level whose 2J parity is impossible for its mass (an ENSDF spin range that
    TALYS resolved to, e.g., J = 3.0 on odd A) has `anom = (J2 + Irspin2 + parspin2) % 2 = 1`;
    see `anomalous_exit_mask`. Continuum spins have anom = 0 by construction.
    """
    dev = j2.device
    lp = torch.arange(L, device=dev)
    lo = (j2[:, None] - irs2).abs()  # (K, R)
    hi = j2[:, None] + irs2
    anom = (lo + parspin2) % 2
    if bool(anom.any()):
        return anomalous_exit_mask(lo, hi, anom, parspin2, spin2, L, photon).to(DTYPE)
    if photon:
        jj = 2 * lp
        ok = ((jj >= lo[..., None]) & (jj <= hi[..., None]) & ((jj - lo[..., None]) % 2 == 0)
              & (lp >= 1))
        out = torch.zeros(ok.shape + (3,), dtype=DTYPE, device=dev)
        out[..., 1] = ok.to(DTYPE)
        return out
    ud = torch.tensor([-1, 0, 1], device=dev)
    jj2p = 2 * lp[:, None] + ud[None, :] * spin2  # (L, 3)
    dj = jj2p - 2 * lp[:, None]
    ok_s = (dj.abs() <= parspin2) & ((dj - parspin2) % 2 == 0) & (jj2p >= 0)
    ok_s = ok_s & (2 * lp[:, None] >= (jj2p - parspin2).abs())
    ok_j = ((jj2p >= lo[..., None, None]) & (jj2p <= hi[..., None, None])
            & ((jj2p - lo[..., None, None]) % 2 == 0))
    return (ok_j & ok_s).to(DTYPE)


def _prepare(inp: CompoundInputs, cells: list[tuple[int, int]], device=None):
    """Per exit type, everything about the residual states that the (J, parity) cells share,
    plus each cell's width `sum rho0 * T` (its part of denomhf). None when a photon transmission
    depends on the compound J or parity.

    TALYS: compprepare.f90:1 (compprepare)
    Test: A-cn1 / SPEED0 golden
    """
    j2s = tuple(c[0] for c in cells)
    pidx = torch.tensor([0 if c[1] == -1 else 1 for c in cells], device=device)
    K = len(cells)
    prep = {}
    for t, r in inp.residuals.items():
        nex = r.maxex + 1
        photon = t == 0
        rho = torch.as_tensor(r.rho, dtype=DTYPE, device=device)  # (Nex, Jx, 2)
        lmaxhf = torch.as_tensor(r.lmaxhf, device=device)
        maxj = torch.as_tensor(r.maxj, device=device)
        rows = torch.arange(nex, device=device)
        disc = rows <= r.nlast
        base = (j2s[0] + r.parspin2) % 2
        irs2c = 2 * torch.arange(NUMJ + 1, device=device) + base
        if photon:
            tg = torch.as_tensor(r.tgam, dtype=DTYPE, device=device)  # (Nex, L, 2, Jx, 2)
            L = tg.shape[1]
            if not bool((tg == tg[..., :1, :1]).all()):
                return None
            tg = tg[..., 0, 0]  # (Nex, L, irad)
            lp = torch.arange(L, device=device)
            # irad = 1 (E) when mod(l', 2) == pardif2 = c, else 0 (M); photons sit at updown 0
            Tn = torch.zeros((2, nex, L, 3), dtype=DTYPE, device=device)
            Tn[0, :, :, 1] = tg[:, lp, (lp % 2 == 0).to(torch.int64)]
            Tn[1, :, :, 1] = tg[:, lp, (lp % 2 == 1).to(torch.int64)]
            raw = None
        else:
            raw = torch.as_tensor(r.tjl, dtype=DTYPE, device=device)  # (Nex, L, 3)
            L = raw.shape[1]
            lp = torch.arange(L, device=device)
            Tn = torch.stack([torch.where((lp % 2 == c)[None, :, None], raw, 0.0) for c in (0, 1)])
        lm = lp[None, :] <= lmaxhf[:, None]  # (Nex, L)
        Tn = torch.where(lm[None, :, :, None], Tn, 0.0)
        # continuum rows: the J-independent part of `_residual_spin2`'s mask
        vc = (irs2c[None, :] <= (2 * maxj)[:, None]) & ~disc[:, None]
        rho_c = torch.where(vc[:, :, None] & (rho >= 1.0e-20), rho, 0.0)
        M = _exit_mask(j2s[0] % 2, j2s, r.parspin2, r.spin2, L, photon, device)  # (K, Jx, L, 3)
        R = torch.einsum("nip,cnlu->ciplu", rho_c, Tn)  # (c, Jx, P', L, 3)
        MR = torch.einsum("kilu,ciplu->kcp", M, R)  # (K, c, P')
        # c = |P - P'| / 2: for P = -1 (index 0), P' index q gives c = q; for P = +1, c = 1 - q
        D0 = MR[:, 0, 0] + MR[:, 1, 1]
        D1 = MR[:, 1, 0] + MR[:, 0, 1]
        Dt = torch.where(pidx == 0, D0, D1)
        dprep = None
        nd = min(r.nlast, r.maxex) + 1
        if nd > 0:
            jd2 = torch.as_tensor(np.asarray(r.jdis2[:nd]), device=device)
            Md = _mask_for(torch.tensor(j2s, device=device), jd2[None, :].expand(K, -1),
                           r.parspin2, r.spin2, L, photon)  # (K, nd, L, 3)
            anom_d = (j2s[0] + jd2 + r.parspin2) % 2
            if bool(anom_d.any()):
                # OPEN3M: TALYS's cap on such a level is l2' = 2 l' + 1 <= l2maxhf
                cap = (2 * lp[None, :] + anom_d[:, None]) <= 2 * lmaxhf[:nd, None]  # (nd, L)
                Md = Md * cap[None, :, :, None].to(DTYPE)
            tot_d = torch.einsum("knlu,cnlu->kcn", Md, Tn[:, :nd])  # (K, c, nd)
            ird = torch.div(jd2, 2, rounding_mode="floor")
            pd = torch.as_tensor((np.asarray(r.parlev[:nd]) > 0).astype(np.int64), device=device)
            ok = (ird >= 0) & (ird <= NUMJ)
            ar = torch.arange(nd, device=device)
            rho_d = torch.where(ok & (rho[ar, ird.clamp(0, NUMJ), pd] >= 1.0e-20),
                                rho[ar, ird.clamp(0, NUMJ), pd], 0.0)
            # c for a level of parity index pd seen from compound parity index p: c = (p != pd)
            cm = (pidx[:, None] != pd[None, :]).to(torch.int64)  # (K, nd)
            tot_dk = tot_d[torch.arange(K, device=device)[:, None], cm, ar[None, :]]  # (K, nd)
            Dt = Dt + (tot_dk * rho_d[None, :]).sum(1)
            # the l' parity each cell reads for each level: [mod(l', 2) == c(P, P'_level)]
            parm = ((lp[None, None, :] % 2) == cm[:, :, None]).to(DTYPE)  # (K, nd, L)
            dprep = dict(ird=ird.clamp(0, NUMJ), pd=pd, rho_d=rho_d, tot_dk=tot_dk, ok=ok,
                         Md=Md, parm=parm, nd=nd)
        prep[t] = dict(Tn=Tn, rho_c=rho_c, M=M, disc=dprep, nex=nex, raw=raw, lm=lm, D=Dt,
                       L=L, photon=photon)
    return prep, pidx


def _feed_type(pop: Tensor, t: int, p: dict, w: Tensor, pidx: Tensor, device) -> None:
    """Add `sum_cells w_cell * rho0 * sum_(l', j') T` to `pop[t]` (the no-WFC shape)."""
    same = (pidx[:, None] == torch.arange(2, device=device)[None, :]).to(DTYPE)  # (K, P')
    V0 = torch.einsum("kilu,k,kq->iqlu", p["M"], w, same)
    V1 = torch.einsum("kilu,k,kq->iqlu", p["M"], w, 1.0 - same)
    TV = (torch.einsum("nlu,iqlu->niq", p["Tn"][0], V0)
          + torch.einsum("nlu,iqlu->niq", p["Tn"][1], V1))
    contrib = p["rho_c"] * TV
    d = p["disc"]
    if d is not None:
        fd = (d["tot_dk"] * w[:, None]).sum(0) * d["rho_d"]
        contrib = contrib.index_put((torch.arange(d["nd"], device=device), d["ird"], d["pd"]),
                                    torch.where(d["ok"], fd, 0.0), accumulate=True)
    n = p["nex"]
    pop[t, :n] = pop[t, :n] + contrib


def _native(inp: CompoundInputs, wfc: bool, device, max_nex: int | None):
    """NATIVEX: `compound.target_native.target` for CPU inputs off the autograd graph, else None."""
    if device not in (None, "cpu") and torch.device(device).type != "cpu":
        return None
    if isinstance(inp.cnfactor_mb, torch.Tensor) and inp.cnfactor_mb.requires_grad:
        return None
    from physics.hf.compound.target_native import target

    return target(inp, wfc, max_nex)


def _cells(inp: CompoundInputs) -> list[tuple[int, int]]:
    return [(J2, p) for p in (-1, 1) for J2 in range(inp.j2beg, inp.j2end + 1, 2)]


def case_nowfc(inp: CompoundInputs, device=None, max_nex: int | None = None
               ) -> tuple[Tensor, Tensor] | None:
    """(pop (7, Nex, numJ+1, 2), xs_fis) as `target._case` returns them when width fluctuations
    are off, or None for inputs this does not cover.

    TALYS: comptarget.f90:1 (comptarget)
    Test: A-cn1 / SPEED0 golden
    """
    got = _native(inp, False, device, max_nex)  # NATIVEX: one compiled call where it applies
    if got is not None:
        return got
    nexmax = max_nex or max(r.maxex + 1 for r in inp.residuals.values())
    pop = torch.zeros((7, nexmax, NUMJ + 1, 2), dtype=DTYPE, device=device)
    xs_fis = torch.zeros((), dtype=DTYPE, device=device)
    cells = _cells(inp)
    if not cells:
        return pop, xs_fis
    got = _prepare(inp, cells, device)
    if got is None:
        return None
    prep, pidx = got
    denom = sum(p["D"] for p in prep.values())
    fis = fbt.cell_fission_widths(inp, cells, device)  # FISSB: tfis, one more denomhf term
    if fis is not None:
        denom = denom + fis
    live = denom != 0.0
    K = len(cells)
    feed = torch.zeros(K, dtype=DTYPE, device=device)
    for k, (J2, parity) in enumerate(cells):
        if not bool(live[k]):
            continue
        _chans, tinc = incident_channels(inp, J2, parity)
        feed[k] = torch.as_tensor(tinc, dtype=DTYPE, device=device).sum()
    cn = torch.as_tensor(inp.cnfactor_mb, dtype=DTYPE, device=device)
    j2t = torch.tensor([c[0] for c in cells], dtype=DTYPE, device=device)
    w = torch.where(live, cn * (j2t + 1.0) / torch.where(live, denom, 1.0) * feed, 0.0)  # (K,)
    for t, p in prep.items():
        _feed_type(pop, t, p, w, pidx, device)
    if fis is not None:
        xs_fis = (w * fis).sum()
    return pop, xs_fis


def case_moldauer(inp: CompoundInputs, device=None, max_nex: int | None = None,
                  chunk_elements: int = 4_000_000) -> tuple[Tensor, Tensor] | None:
    """`target._case` with Moldauer width fluctuations (widthmode 1), every (J, parity) cell's
    Gauss-Laguerre integral evaluated on a leading cell axis. None for inputs not covered
    (a J/P-dependent photon transmission, a target level that is not discrete).

    Per cell, exactly `_case`'s quantities: the exit channel list (T and its level-density
    weight, summed over residual spin and parity), nu, the node products P_m, then
    G_b = sum_m P_m H_m / (1 + x_m f_b) per exit channel, G_gamma and the elastic E_a. The only
    J-dependent part of a weight is the `_exit_mask` rule, so the weight sums and the population
    contractions are einsums against it rather than materialised (Nex, Ir, P', l', j') tensors.

    TALYS: comptarget.f90:1 (comptarget), molprepare.f90:1 (molprepare), moldauer.f90:1 (moldauer)
    Test: A-cn2 / SPEED0 golden
    """
    from physics.hf.compound import wfc

    got = _native(inp, True, device, max_nex)  # NATIVEX: one compiled call where it applies
    if got is not None:
        return got
    nexmax = max_nex or max(r.maxex + 1 for r in inp.residuals.values())
    pop = torch.zeros((7, nexmax, NUMJ + 1, 2), dtype=DTYPE, device=device)
    xs_fis = torch.zeros((), dtype=DTYPE, device=device)
    cells = _cells(inp)
    if not cells:
        return pop, xs_fis
    k0 = inp.k0
    lt = inp.ltarget
    if k0 in inp.residuals and lt > inp.residuals[k0].nlast:
        return None
    got = _prepare(inp, cells, device)
    if got is None:
        return None
    prep, pidx = got
    denom = sum(p["D"] for p in prep.values())
    fis = fbt.cell_fission_widths(inp, cells, device)  # FISSB: tfis, one more denomhf term
    if fis is not None:
        denom = denom + fis
    x, wts = wfc.gauss_laguerre(device)
    cn = torch.as_tensor(inp.cnfactor_mb, dtype=DTYPE, device=device)
    parts = [t for t in prep if t != 0]
    # the J-independent exit transmissions, flat in `_case`'s block order
    t_exit_list = [torch.where(prep[t]["raw"] > 1.0e-30, prep[t]["raw"], 0.0) for t in parts]
    t_exit = torch.cat([v.reshape(-1) for v in t_exit_list])
    live_idx = [k for k in range(len(cells)) if float(denom[k].detach()) != 0.0]
    # a channel with T = 0 has eps = 0 and adds nothing to molprepare's product, and its G_b is
    # sum_m P_m H_m exactly (1 + x * 0 = 1): only the open channels need the node axis
    nz = torch.nonzero(t_exit > 0.0).flatten()
    t_nz = t_exit[nz]
    nch = max(int(nz.numel()), 1)
    step = max(1, chunk_elements // (x.numel() * nch))
    for c0 in range(0, len(live_idx), step):
        ks = live_idx[c0: c0 + step]
        kt = torch.tensor(ks, device=device)
        Kc = len(ks)
        st = denom[kt]  # (Kc,)
        pk = pidx[kt]
        # incident channels, padded with T = 0 (no term in H, never an elastic partner)
        incs = [incident_channels(inp, *cells[k]) for k in ks]
        na = max(len(ch) for ch, _ in incs)
        tinc = torch.zeros((Kc, na), dtype=DTYPE, device=device)
        for i, (_ch, tv) in enumerate(incs):
            if len(tv):
                tinc[i, : len(tv)] = torch.as_tensor(tv, dtype=DTYPE, device=device)
        nu_inc = wfc.degrees_of_freedom(tinc, st[:, None], inp.wfcfactor)
        # weight sums per exit channel: sum over (Ir, P') of rho0 * allowed
        r_list = []
        for t in parts:
            p = prep[t]
            Mk = p["M"][kt]  # (Kc, Jx, L, 3)
            A = torch.einsum("niq,kilu->kqnlu", p["rho_c"], Mk)  # (Kc, P', Nex, L, 3)
            par = ((torch.arange(p["L"], device=device) % 2)[None, None, :]
                   == (pk[:, None] != torch.arange(2, device=device)[None, :]).to(torch.int64)[..., None])
            Rw = (A * par[:, :, None, :, None].to(DTYPE)).sum(1)
            d = p["disc"]
            if d is not None:
                Rd = d["rho_d"][None, :, None, None] * d["Md"][kt] * d["parm"][kt][..., None]
                Rw = torch.cat([Rw[:, : d["nd"]] + Rd, Rw[:, d["nd"]:]], dim=1)
            Rw = Rw * p["lm"][None, :, :, None].to(DTYPE)
            r_list.append(Rw.reshape(Kc, -1))
        r_exit = torch.cat(r_list, dim=1)[:, nz]  # (Kc, open channels)
        nu_exit = wfc.degrees_of_freedom(t_nz[None, :], st[:, None], inp.wfcfactor)
        # molprepare: P_m per cell
        eps = 2.0 * t_nz[None, None, :] * x[None, :, None] / (st[:, None, None] * nu_exit[:, None, :])
        livee = eps > 1.0e-30
        logterm = torch.where(livee, torch.log1p(torch.where(livee, eps, 0.0)), 0.0)
        factor = (-nu_exit * 0.5 * r_exit)[:, None, :] * logterm
        if fis is not None:
            # FISSB: the cells' Hill-Wheeler humps, after the particle channels (target.py:163-175)
            ratio_h, t_h, rho_h, on_h = fbt.hump_channels(inp, [cells[k] for k in ks], fis[kt],
                                                          device)
            nu_h = wfc.degrees_of_freedom(t_h, st[:, None], inp.wfcfactor)
            eps_h = 2.0 * t_h[:, None, :] * x[None, :, None] / (st[:, None, None] * nu_h[:, None, :])
            live_h = eps_h > 1.0e-30
            log_h = torch.where(live_h, torch.log1p(torch.where(live_h, eps_h, 0.0)), 0.0)
            factor = torch.cat([factor, (-nu_h * 0.5 * rho_h)[:, None, :] * log_h], dim=2)
        gam = prep[0]["D"][kt] if 0 in prep else torch.zeros_like(st)
        expo = gam[:, None] * x[None, :] / st[:, None]
        capt = torch.where(expo > 80.0, 0.0, torch.exp(-torch.clamp(expo, max=80.0)))
        prod = wts * wts * torch.exp(x) * torch.exp(factor.sum(2)) * capt  # (Kc, M)
        # moldauer.f90 sums against the incident channels
        fa = 2.0 * tinc / (st[:, None] * nu_inc)  # (Kc, A)
        da = 1.0 + x[None, :, None] * fa[:, None, :]  # (Kc, M, A)
        H = (tinc[:, None, :] / da).sum(2)  # (Kc, M)
        PH = prod * H
        gg = PH.sum(1)
        ea = (prod[:, :, None] * (2.0 / nu_inc)[:, None, :] / da ** 2).sum(1)  # (Kc, A)
        j2t = torch.tensor([cells[k][0] for k in ks], dtype=DTYPE, device=device)
        pref = cn * (j2t + 1.0) / st
        if fis is not None:
            xs_fis = xs_fis + fbt.hump_fission(x, PH, st, pref, fis[kt], ratio_h, t_h, nu_h, on_h)
        wfull = torch.zeros(len(cells), dtype=DTYPE, device=device)
        if 0 in prep:
            wfull[kt] = pref * gg
            _feed_type(pop, 0, prep[0], wfull, pidx, device)
        for t, tt in zip(parts, t_exit_list, strict=True):
            p = prep[t]
            flat = tt.reshape(-1)
            open_ = torch.nonzero(flat > 0.0).flatten()
            Gb = gg[:, None].expand(Kc, flat.numel()).clone()  # sum_m P_m H_m / (1 + x * 0)
            if open_.numel():
                to = flat[open_]
                nu_b = wfc.degrees_of_freedom(to[None], st[:, None], inp.wfcfactor)
                fb = 2.0 * to[None] / (st[:, None] * nu_b)
                Gb[:, open_] = (PH[:, :, None] / (1.0 + x[None, :, None] * fb[:, None, :])).sum(1)
            Y = (pref[:, None] * (p["raw"].reshape(-1)[None, :] * Gb)).reshape((Kc,) + tt.shape)
            Y = Y * p["lm"][None, :, :, None].to(DTYPE)
            Mk = p["M"][kt]
            parq = ((torch.arange(p["L"], device=device) % 2)[None, None, :]
                    == (pk[:, None] != torch.arange(2, device=device)[None, :]).to(torch.int64)[..., None]
                    ).to(DTYPE)  # (Kc, P', L)
            contrib = p["rho_c"] * torch.einsum("kilu,kqnlu->niq", Mk,
                                                Y[:, None] * parq[:, :, None, :, None])
            d = p["disc"]
            if d is not None:
                nd = d["nd"]
                fd = torch.einsum("knlu,knlu->n", d["Md"][kt] * d["parm"][kt][..., None],
                                  Y[:, :nd]) * d["rho_d"]
                contrib = contrib.index_put((torch.arange(nd, device=device), d["ird"], d["pd"]),
                                            torch.where(d["ok"], fd, 0.0), accumulate=True)
            if t == k0 and d is not None and lt < d["nd"]:
                # the elastic diagonal (ielas = 1): exit (l', j') = incident (l, j) at Ltarget
                li = torch.zeros((Kc, na), dtype=torch.int64, device=device)
                ui = torch.zeros((Kc, na), dtype=torch.int64, device=device)
                ok_a = torch.zeros((Kc, na), dtype=torch.bool, device=device)
                for i in range(Kc):
                    for ia, (l, ud) in enumerate(incs[i][0]):
                        if l < p["L"]:
                            li[i, ia], ui[i, ia], ok_a[i, ia] = l, ud + 1, True
                kk = kt[:, None].expand(Kc, na)
                wgt = (d["Md"][kk, lt, li, ui] * d["parm"][kk, lt, li]
                       * p["lm"][lt][li].to(DTYPE))
                term = wgt * p["raw"][lt][li, ui] * tinc * ea
                ex = torch.where(ok_a, term, 0.0).sum(1)
                val = (pref * ex).sum() * d["rho_d"][lt]
                contrib = contrib.index_put(
                    (torch.tensor([lt], device=device), d["ird"][lt:lt + 1], d["pd"][lt:lt + 1]),
                    torch.where(d["ok"][lt:lt + 1], val.reshape(1), 0.0), accumulate=True)
            n = p["nex"]
            pop[t, :n] = pop[t, :n] + contrib
    return pop, xs_fis
