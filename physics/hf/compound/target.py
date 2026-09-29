"""First-chance (binary) compound decay of the target system: sum over compound J, parity, incident
(l, j) and exit channels, with WFC (comptarget.f90). Produces the population per ejectile,
level/bin, J and parity.

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

Task: T9 (physics/hf/CONTRACT.md §7). Acceptance test: A-cn2 (§6).

TALYS routines ported here (file:line of the subroutine/function statement):
    comptarget.f90:1 (comptarget)
    widthfluc.f90:1 (widthfluc)  -- dispatch on wmode (1 Moldauer, 2 HRTW, 3 GOE)

The loops over (J, parity) stay Python loops (at most 2 x 41 blocks); inside a block every sum
over residual level/bin, spin, parity, l', j' and incident (l, j) is a tensor expression. Summing
the population over incident channels before multiplying by the exit transmission is exact
because all three width-fluctuation factors factorise over the incident channel
(wfc.moldauer_sums, wfc.hrtw_sums, wfc.goe_sums).

What TALYS does and this port reproduces, including quirks:
* flagwidth (Einc <= ewfc, default ewfc = S_n of the target) selects the full (j, l) loops; above
  it the lumped `feed * enumhf / denomhf` path is taken. Both equal the W = 1 expression, so one
  code path serves both, and W != 1 only when flagwidth and wmode >= 1.
* compound elastic is populated here (pop of the incident particle at nexout = Ltarget) and
  removed later by binary.f90:505; `xs_comp_el_mb` carries it.
* photons read Tgam(l, nexout, irad, J, P) with the COMPOUND J and P, as the Fortran does.
"""

from __future__ import annotations

import copy
from dataclasses import dataclass, replace

import numpy as np
import torch
from torch import Tensor

from physics.hf.compound import wfc
from physics.hf.compound.prepare import NUMJ, CompoundInputs, exit_channel_sums, incident_channels
from physics.hf.core.tensors import DTYPE

NUMHILL = 20


@dataclass(frozen=True)
class BinaryPopulation:
    pop_mb: Tensor  # (C, particle(0..6), Lv+B, Jx, 2) population of each residual state
    xs_comp_el_mb: Tensor  # (C,) compound elastic
    xs_fission_mb: Tensor  # (C,)


def _exact_incident_channel(inp: CompoundInputs) -> CompoundInputs:
    """comptarget.f90:358-362: replace the incident channel's interpolated `Tjlnex(l, updown, k0,
    Ltarget)` by the exactly calculated `Tjlinc(updown, l)`.

    densprepare gets every other residual state by a second-order interpolation of `Tjl` over the
    emission grid; for the target's own ground state TALYS has the exact incident-channel value
    and uses it. How far apart those two are is a property of the target, not of the grid:
    measured over Einc = 0.002 .. 0.5 MeV, the interpolant is within 2.4% of `Tjlinc` on the eight
    spherical targets with a spherical incident channel, and **38-54% off on Ca-40 at every one of
    those energies**, because Ca-40's incident channel is ECIS coupled channels (colltype 'V', 4
    one-phonon levels) and no interpolation of a spherical emission grid reproduces it. Skipping
    this loop is what put the chained A-cn on Ca-40 at p95 3.7e-2 (max inf); with it, 1.6e-5.

    Idempotent on injected inputs: the instrumented dump is taken after this loop runs, so
    `Tjlnex(., ., k0, Ltarget)` already equals `Tjlinc` there.

    TALYS: comptarget.f90:1 (comptarget)
    Test: A-cn1
    """
    r = inp.residuals.get(inp.k0)
    if r is None or r.tjl is None or not (0 <= inp.ltarget <= r.maxex):
        return inp
    n = min(inp.lmaxinc + 1, inp.tjlinc.shape[0])
    tjl = r.tjl
    # `tjl` is numpy from the dump loader and a Tensor when the caller is differentiating
    # through it (contract §4.4), so stay in whichever it is; the clone keeps the untouched
    # rows on the autograd graph.
    if isinstance(tjl, Tensor):
        inc = torch.as_tensor(inp.tjlinc[:n], dtype=tjl.dtype, device=tjl.device)
        if bool(torch.equal(tjl[inp.ltarget, :n].detach(), inc)):
            return inp
        if n > tjl.shape[1]:
            pad = torch.zeros(tjl.shape[0], n - tjl.shape[1], 3, dtype=tjl.dtype, device=tjl.device)
            tjl = torch.cat([tjl, pad], dim=1)
        else:
            tjl = tjl.clone()
    else:
        if np.array_equal(tjl[inp.ltarget, :n], inp.tjlinc[:n]):
            return inp
        inc = inp.tjlinc[:n]
        tjl = (np.concatenate([tjl, np.zeros((tjl.shape[0], n - tjl.shape[1], 3))], axis=1)
               if n > tjl.shape[1] else tjl.copy())
    tjl[inp.ltarget, :n] = inc
    out = copy.copy(inp)
    out.residuals = dict(inp.residuals)
    out.residuals[inp.k0] = replace(r, tjl=tjl)
    return out


def _elastic_channel(t: Tensor, jl: Tensor, chans, ltarget: int, device):
    """The exit channel `comptarget.f90:630-632` pairs with each incident (l, j): same l, same j,
    at the target's own level. Returns its transmission and `transjl` rows, one per incident
    channel, zeroed where the exit l is outside the residual's own l range.

    TALYS: comptarget.f90:1 (comptarget), goe.f90:1 (goe); `dab` is set at goe.f90 line 98
    Test: A-cn2
    """
    lmax = t.shape[1]
    ok = [lp < lmax for lp, _ in chans]
    ls = torch.tensor([lp if o else 0 for (lp, _), o in zip(chans, ok, strict=True)],
                      dtype=torch.long, device=device)
    us = torch.tensor([ud + 1 for _, ud in chans], dtype=torch.long, device=device)
    live = torch.tensor(ok, dtype=torch.bool, device=device)
    zero6 = torch.zeros(1, 6, dtype=DTYPE, device=device)
    return (torch.where(live, t[ltarget][ls, us], torch.zeros_like(live, dtype=DTYPE)),
            torch.where(live[:, None], jl[ltarget][ls, us], zero6))


def _case(inp: CompoundInputs, device=None, max_nex: int | None = None):
    inp = _exact_incident_channel(inp)
    types = sorted(inp.residuals)
    nexmax = max_nex or max(r.maxex + 1 for r in inp.residuals.values())
    pop = torch.zeros((7, nexmax, NUMJ + 1, 2), dtype=DTYPE, device=device)
    xs_fis = torch.zeros((), dtype=DTYPE, device=device)
    use_wfc = inp.flagwidth and inp.wmode >= 1
    if use_wfc and inp.wmode not in (1, 2, 3):
        raise NotImplementedError(f"widthmode {inp.wmode} is not a TALYS option")
    if not use_wfc or inp.wmode == 1:
        # SPEED0: without width fluctuations, or with Moldauer's, every (J, parity) at once
        from physics.hf.compound.target_batch import case_moldauer, case_nowfc

        got = (case_nowfc if not use_wfc else case_moldauer)(inp, device, nexmax)
        if got is not None:
            return got
    x, wts = wfc.gauss_laguerre(device)
    cn = torch.as_tensor(inp.cnfactor_mb, dtype=DTYPE, device=device)
    for parity in (-1, 1):
        for J2 in range(inp.j2beg, inp.j2end + 1, 2):
            s = exit_channel_sums(inp, J2, parity, device)
            st = s["denom"]
            if float(st.detach()) == 0.0:
                continue
            chans, tinc_np = incident_channels(inp, J2, parity)
            tinc = torch.as_tensor(tinc_np, dtype=DTYPE, device=device)
            feed = tinc.sum()
            blocks = s["blocks"]
            ratio_h = None
            offs: dict[int, tuple[int, int]] = {}
            fis_off = (0, 0)
            if use_wfc:
                nu_inc = wfc.degrees_of_freedom(tinc, st, inp.wfcfactor)
                t_list, r_list, g_list, pos = [], [], [], 0
                for t, b in blocks.items():
                    if t == 0:
                        continue
                    tt = torch.where(b.t > 1.0e-30, b.t, 0.0)
                    offs[t] = (pos, pos + tt.numel())
                    pos += tt.numel()
                    t_list.append(tt.reshape(-1))
                    r_list.append(b.weight.sum((1, 2)).reshape(-1))
                    g_list.append(tt.reshape(-1))
                fis_off = (pos, pos + NUMHILL)
                if inp.flagfission and inp.nfisbar != 0:
                    ta = torch.as_tensor(inp.tfisA.get((J2, parity), [0.0] * (NUMHILL + 1)), dtype=DTYPE, device=device)
                    ra = torch.as_tensor(inp.rhofisA.get((J2, parity), [0.0] * (NUMHILL + 1)), dtype=DTYPE, device=device)
                    ratio_h = torch.where(ta[0] > 0, ta[1:] / torch.where(ta[0] > 0, ta[0], 1.0), 0.0)
                    tfh = ratio_h * s["fiswidth"]
                    rho_h = torch.clamp(ra[1:], min=1.0)
                    t_list.append(torch.where(tfh > 1.0e-30, tfh / rho_h, 0.0))
                    r_list.append(rho_h)
                    # compprepare.f90:407 tests the HILL width, not T = tfishill / rho
                    g_list.append(tfh)
                t_exit, r_exit = torch.cat(t_list), torch.cat(r_list)
                g_exit = torch.cat(g_list)
                if inp.wmode == 1:
                    nu_exit = wfc.degrees_of_freedom(t_exit, st, inp.wfcfactor)
                    prod = wfc.moldauer_product(x, wts, st, t_exit, r_exit, nu_exit, s["gamwidth"])
                elif inp.wmode == 3:
                    # widthprepare.f90:76 -- one goeprepare per (J, parity), then every pair.
                    goe_prep = wfc.goe_prepare(t_exit, r_exit, st, s["gamwidth"], device,
                                               guard=g_exit)
                    goe_inc = wfc.goe_incident(goe_prep, tinc)
                    gam1 = torch.ones(1, dtype=DTYPE, device=device)
                    jl_gam = wfc.transjl_powers(s["gamwidth"].reshape(1), gam1,
                                                guard=s["gamwidth"].reshape(1), gamma=True)
                else:
                    # HRTW: the 60-iteration fixed point runs over the whole channel list at once
                    # (incident, every exit channel, the lumped capture channel last), so each
                    # block's v is SLICED out of it, never recomputed (hrtwprepare.f90:72-81).
                    n_a = tinc.numel()
                    t_all = torch.cat([tinc, t_exit, s["gamwidth"].reshape(1)])
                    r_all = torch.cat([
                        torch.ones(n_a, dtype=DTYPE, device=device), r_exit,
                        torch.ones(1, dtype=DTYPE, device=device)])
                    hv, hw, hsv = wfc.hrtw_prepare(t_all, r_all, st, n_a, inp.wfcfactor)
                    hv_inc, hw_inc, hv_exit = hv[:n_a], hw[:n_a], hv[n_a:-1]
            pref = cn * (J2 + 1.0) / st
            for t, b in blocks.items():
                if t == 0:
                    if use_wfc and inp.wmode == 1:
                        _, gg, _ = wfc.moldauer_sums(x, prod, st, tinc, nu_inc, b.t[:1, :1, :1], torch.ones(1, dtype=DTYPE))
                    elif use_wfc and inp.wmode == 3:
                        gg = wfc.goe_sums(goe_prep, goe_inc, s["gamwidth"].reshape(1), jl_gam,
                                          capture=True).reshape(())
                    elif use_wfc:
                        gg, _ = wfc.hrtw_sums(hv, hw_inc, hsv, st, tinc, hv_inc,
                                              s["gamwidth"].reshape(1), hv[-1:].reshape(1))
                        gg = gg.reshape(())
                    else:
                        gg = feed
                    contrib = (b.weight * b.t[:, None, None, :, :]).sum((3, 4)) * gg
                else:
                    if use_wfc and inp.wmode == 1:
                        tt = torch.where(b.t > 1.0e-30, b.t, 0.0)
                        nu_b = wfc.degrees_of_freedom(tt, st, inp.wfcfactor)
                        gb, _, ea = wfc.moldauer_sums(x, prod, st, tinc, nu_inc, tt, nu_b)
                    elif use_wfc and inp.wmode == 3:
                        tt = torch.where(b.t > 1.0e-30, b.t, 0.0)
                        # goe.f90:157's tb6 is the one term that is not linear in rho, so the
                        # (Ir, P') cells lumped into one channel need sum(rho) AND sum(kappa).
                        wt5 = b.weight
                        kap = torch.where(wt5 >= 1.0, wt5, wt5 * wt5).sum((1, 2))
                        jl = wfc.transjl_powers(tt, wt5.sum((1, 2)), kappa=kap)
                        gb = wfc.goe_sums(goe_prep, goe_inc, tt, jl)
                        ea = None
                        if t == inp.k0:
                            el = _elastic_channel(tt, jl, chans, inp.ltarget, device)
                            ea = wfc.goe_elastic(goe_prep, goe_inc, *el)
                    elif use_wfc:
                        tt = torch.where(b.t > 1.0e-30, b.t, 0.0)
                        o0, o1 = offs[t]
                        gb, ea = wfc.hrtw_sums(hv, hw_inc, hsv, st, tinc, hv_inc, tt,
                                               hv_exit[o0:o1].reshape(tt.shape))
                    else:
                        gb = feed
                    contrib = (b.weight * (b.t * gb)[:, None, None, :, :]).sum((3, 4))
                    if use_wfc and t == inp.k0:
                        # elastic diagonal (ielas = 1): exit (l', j') identical to incident (l, j)
                        lt = inp.ltarget
                        extra = torch.zeros_like(contrib[lt])
                        for ia, (l, ud) in enumerate(chans):
                            if l < b.t.shape[1]:
                                extra = extra + b.weight[lt, :, :, l, ud + 1] * b.t[lt, l, ud + 1] * tinc[ia] * ea[ia]
                        contrib = contrib.index_add(0, torch.tensor([lt], device=device), extra[None])
                n = contrib.shape[0]
                pop[t, :n] = pop[t, :n] + pref * contrib
            if inp.flagfission and inp.nfisbar != 0:
                tf = s["fiswidth"]
                if use_wfc:
                    if ratio_h is not None and float(torch.as_tensor(inp.tfisA.get((J2, parity), [0.0])[0])) > 0:
                        th = torch.where(ratio_h * tf > 1.0e-30, ratio_h * tf / torch.clamp(ra[1:], min=1.0), 0.0)
                        if inp.wmode == 1:
                            nu_h = wfc.degrees_of_freedom(th, st, inp.wfcfactor)
                            gh, _, _ = wfc.moldauer_sums(x, prod, st, tinc, nu_inc, th, nu_h)
                        elif inp.wmode == 3:
                            gh = wfc.goe_sums(goe_prep, goe_inc, th, wfc.transjl_powers(
                                th, torch.clamp(ra[1:], min=1.0), guard=ratio_h * tf))
                        else:
                            gh, _ = wfc.hrtw_sums(hv, hw_inc, hsv, st, tinc, hv_inc, th,
                                                  hv_exit[fis_off[0]:fis_off[1]])
                        live = ratio_h != 0
                        xs_fis = xs_fis + pref * tf * (torch.where(live, gh * ratio_h, 0.0)).sum()
                else:
                    xs_fis = xs_fis + pref * feed * tf
    return pop, xs_fis


def compound_target_inputs(inp: CompoundInputs, device=None) -> BinaryPopulation:
    """comptarget.f90 for one case from injected inputs; C = 1.

    TALYS: comptarget.f90:1 (comptarget)
    Test: A-cn2
    """
    pop, xs_fis = _case(inp, device)
    r = inp.residuals[inp.k0]
    el = pop[inp.k0, inp.ltarget].sum() if inp.ltarget <= r.maxex else torch.zeros((), dtype=DTYPE)
    return BinaryPopulation(pop[None], el.reshape(1), xs_fis.reshape(1))


def compound_target(cases, inc=None, sums=None, options=None) -> BinaryPopulation:
    """The comptarget.f90 calculation; A-cn1 (wfc_off) and A-cn2 (default) compare pop_mb with
    binE*.out.

    `cases` is a list of CompoundInputs (the injected upstream arrays, see prepare.py); the
    contract's (CaseBatch, IncidentChannel, sums) form is served once T5/T6/T7 exist, by an adapter
    that builds CompoundInputs from their objects. Cases are padded to a common Lv+B axis.

    TALYS: comptarget.f90:1 (comptarget)
    Test: A-cn2
    """
    if isinstance(cases, CompoundInputs):
        cases = [cases]
    nexmax = max(max(r.maxex + 1 for r in c.residuals.values()) for c in cases)
    out = [_case(c, None, nexmax) for c in cases]
    pops = torch.stack([p for p, _ in out])
    el = torch.stack([pops[i, c.k0, c.ltarget].sum() for i, c in enumerate(cases)])
    fis = torch.stack([f for _, f in out])
    return BinaryPopulation(pops, el, fis)


def binary_cross_sections(pop: BinaryPopulation, cases: list[CompoundInputs]) -> Tensor:
    """xsbinary per type (0..6) [mb]: population summed over states, compound elastic excluded
    (comptarget.f90: `if (.not. elastic) sumIPE = sumIPE + sumIP`).

    TALYS: comptarget.f90:1 (comptarget)
    Test: A-cn1
    """
    out = pop.pop_mb.sum((2, 3, 4)).clone()
    for i, c in enumerate(cases):
        out[i, c.k0] = out[i, c.k0] - pop.pop_mb[i, c.k0, c.ltarget].sum()
    return out
