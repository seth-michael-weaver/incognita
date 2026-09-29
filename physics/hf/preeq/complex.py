"""Pickup, stripping and knockout contributions for complex particles (Kalbach).

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

Task: T8 (physics/hf/CONTRACT.md §7). Acceptance test: A-pe (§6).

TALYS routines ported here (file:line of the subroutine/function statement):
    preeqcomplex.f90:1 (preeqcomplex)
    knockout.f90:1 (knockout)
    stripping.f90:1 (stripping)
    bonetti.f90:1 (bonetti)

`bonetti` is only read for `preeqmode 3` (optical-model transition rates) and is not ported;
`breakup` (`k0 > 2`) is out of scope for a neutron-induced port and raises.

These are the `Pickup/strip` and `Knockout` columns of `preeq*.out`. Batched over
(case, energy, particle); the only loops are Kalbach's four small exciton sums.
"""

from __future__ import annotations

import torch
from torch import Tensor

from physics.hf.core.constants import talys_constants
from physics.hf.core.tensors import DTYPE
from physics.hf.density.particle_hole import apauli2, phdens2, preeqpair
from physics.hf.preeq import preeq_nx2
from physics.hf.preeq.exciton import PreeqInputs, surface_well_depth


def stripping(inp: PreeqInputs, options, params, *, kph: float = 15.0) -> Tensor:
    """Kalbach pickup/stripping spectra `xspreeqps(type, nen)` [mb/MeV], shape (C, 7, E).

    TALYS: stripping.f90:1 (stripping)
    Test: A-pe
    """
    c = talys_constants()
    parZ, parN, parA = c["parZ"], c["parN"], c["parA"]
    parmass, parspin = c["parmass"], c["parspin"]
    k0 = inp.k0
    C, E = inp.C, inp.E
    dev = inp.egrid_mev.device
    pairmodel = getattr(options, "pairmodel", 2)
    Z, A = inp.Z, inp.A
    Ainit = inp.a_init
    out = torch.zeros(C, 7, E, dtype=DTYPE, device=dev)
    einc = inp.einc_mev.reshape(C, 1)
    # eninccm is not dumped separately; Etotal - S(0,0,k0) is exactly it (energies.f90:79)
    eninccm = inp.ecomp_mev.reshape(C, 1) - inp.s_mev[:, k0].reshape(C, 1)
    projmass = parmass[k0]
    proj2sp1 = 2.0 * parspin[k0] + 1.0
    gsp_cn = inp.gp_cn.reshape(C, 1)
    gsn_cn = inp.gn_cn.reshape(C, 1)

    for t in range(1, 7):
        if k0 <= 2 and t <= 2:  # stripping.f90:83
            continue
        ejecmass, ejec2sp1 = parmass[t], 2.0 * parspin[t] + 1.0
        term1 = ejec2sp1 * ejecmass / (proj2sp1 * projmass)
        kap = torch.ones(C, 1, dtype=DTYPE, device=dev)
        if k0 in (1, 2):  # stripping.f90:88-92
            if t == 6:
                kap = kap * 12.0
            if t == 3:
                kap = torch.where(einc > 80.0, 80.0 / einc, kap)
            if t == 5:
                kap = kap * 5.0
        ndelta = abs(parA[k0] - parA[t])
        ndeltapi = parZ[k0] - parZ[t]
        ndeltanu = parN[k0] - parN[t]
        va = 12.5 * projmass
        term2 = (kap / projmass) * (projmass / (einc + va)) ** (2 * ndelta)
        ppi, hpi = max(ndeltapi, 0), max(-ndeltapi, 0)
        pnu, hnu = max(ndeltanu, 0), max(-ndeltanu, 0)
        Ares, Zres = Ainit - parA[t], Z - parZ[t]
        Nres = Ares - Zres
        term3 = ((5500.0 if k0 == 1 else 3800.0) / float(Ares)) ** ndelta
        if parA[k0] < parA[t]:
            term4 = 1.0 / (80.0 * eninccm)
        elif parA[k0] > parA[t]:
            term4 = 1.0 / (580.0 * torch.sqrt(eninccm))
        else:
            term4 = 1.0 / (1160.0 * torch.sqrt(eninccm))
        base = 2.0 * Z / A
        term5 = base ** (2 * (parZ[k0] + 2) * hpi + 2 * pnu)
        cstrip = torch.as_tensor(params.at("cstrip", t), dtype=DTYPE, device=dev)
        termps = cstrip * term1 * term2 * term3 * term4 * term5

        if k0 == 1:
            v1well = surface_well_depth(1, inp.einc_mev, Ainit).reshape(C, 1)
        elif k0 == 2:
            v1well = surface_well_depth(2, inp.einc_mev, Ainit).reshape(C, 1)
        elif k0 in (5, 6):
            v1well = torch.full((C, 1), 25.0, dtype=DTYPE, device=dev)
        else:
            v1well = torch.full((C, 1), 17.0, dtype=DTYPE, device=dev)
        xnt = (
            torch.sqrt(torch.clamp(einc, max=100.0) / projmass)
            * 7.0
            / (v1well * A * A)
            * (pnu**2 + ppi**2 + hnu**2 + 1.5 * hpi**2)
        )
        gsn = Nres / kph
        gsp = Zres / kph
        ewell = v1well * base if ndeltapi == 0 else v1well

        eout = inp.egrid_mev  # (C, E)
        factor1 = inp.xsreac_mb[:, t] * eout
        nt = torch.tensor(ndelta, device=dev)
        pcn = preeqpair(
            inp.pair_res_mev[:, t].reshape(C, 1),
            torch.tensor(gsp + gsn, dtype=DTYPE, device=dev),
            nt,
            inp.ecomp_mev.reshape(C, 1),
            pairmodel,
        )
        eres = inp.ecomp_mev.reshape(C, 1) - inp.s_mev[:, t].reshape(C, 1) - eout - pcn
        ok = inp.emask[:, t] & (eres >= 0)
        eres_s = torch.where(ok, eres, torch.zeros_like(eres))
        gspt = torch.full((1, 1), gsp, dtype=DTYPE, device=dev)
        gsnt = torch.full((1, 1), gsn, dtype=DTYPE, device=dev)
        ew = ewell.expand(C, E) if ewell.shape[1] == 1 else ewell

        def omega(dppi, dhpi, dpnu, dhnu, _g=(gspt, gsnt, eres_s, ew)):
            idx = [torch.tensor(v, device=dev) for v in (dppi, dhpi, dpnu, dhnu)]
            ap = apauli2(*idx, gsp_cn, gsn_cn)  # the compound-nucleus Apauli2 table
            return phdens2(*idx, _g[0], _g[1], _g[2], _g[3], False, ap2=ap)

        # the two exciton sums' terms in TALYS's order: (power of xnt, or None, and the state)
        terms = [(i + j, ppi + i, hpi + i, pnu + j, hnu + j)  # stripping.f90:158-163
                 for i in range(4) for j in range(4 - i)]
        terms += [(None, ppi - i, hpi - j, pnu - k, hnu - ll)  # stripping.f90:164-172
                  for i in range(ppi + 1) for j in range(hpi + 1) for k in range(pnu + 1)
                  for ll in range(hnu + 1) if i + j + k + ll]
        # NATIVEX2: off the graph, every term's density in one call (preeq.preeq_nx2)
        acc = preeq_nx2.stripping_sum(terms, xnt, gspt, gsnt, eres_s, ew, gsp_cn, gsn_cn)
        if acc is None:
            acc = torch.zeros_like(eres)
            for pw, *state in terms:
                om = omega(*state)
                acc = acc + (om if pw is None else xnt**pw * om)
        out[:, t] = torch.where(ok, termps * acc * factor1, torch.zeros_like(acc))
    return out


def knockout(inp: PreeqInputs, options, params, coulbar_mev, xsreacinc_mb: Tensor) -> Tensor:
    """Kalbach knockout / inelastic spectra `xspreeqki(type, nen)` [mb/MeV], shape (C, 7, E).

    For a nucleon projectile only the alpha knockout survives `knockout.f90:83-85`
    (`k0 <= 2 .and. type <= 2` is skipped, and `flaginel` needs `k0 == type`).

    TALYS: knockout.f90:1 (knockout)
    Test: A-pe
    """
    c = talys_constants()
    parA, parmass, parspin = c["parA"], c["parmass"], c["parspin"]
    k0 = inp.k0
    C, E = inp.C, inp.E
    dev = inp.egrid_mev.device
    pairmodel = getattr(options, "pairmodel", 2)
    Z, A = inp.Z, inp.A
    N = A - Z
    out = torch.zeros(C, 7, E, dtype=DTYPE, device=dev)
    eninccm = inp.ecomp_mev.reshape(C, 1) - inp.s_mev[:, k0].reshape(C, 1)
    projmass = parmass[k0]
    proj2sp1 = 2.0 * parspin[k0] + 1.0

    phi = 0.08  # knockout.f90:99-101
    if 116 < N < 126:
        phi = 0.02 + 0.06 * (126 - N) / 10.0
    elif 126 <= N < 129:
        phi = 0.02 + 0.06 * (N - 126) / 3.0
    denom = A - 2.0 * phi * Z + 0.5 * phi * Z
    Pn = {1: (N - phi * Z) / denom, 2: (Z - phi * Z) / denom, 6: 0.5 * phi * Z / denom}
    gscomp = {1: A / 13.0, 2: A / 13.0, 3: A / 52.0, 4: A / 156.0, 5: A / 156.0, 6: A / 208.0}

    # denomki(type2) (knockout.f90:110-126), per case
    denomki = torch.zeros(C, 7, dtype=DTYPE, device=dev)
    for t2 in range(1, 7):
        emax = eninccm.reshape(C) + (inp.s_mev[:, k0] - inp.s_mev[:, t2])  # Q(type2)
        cb = coulbar_mev[t2]
        dE = emax - cb
        above = inp.emask[:, t2] & (inp.egrid_mev >= cb)
        total = (inp.xsreac_mb[:, t2] * inp.deltae_mev * above).sum(-1)
        # xsreac(type2, eend(type2)); the mask is empty for a closed channel
        last = torch.zeros(C, dtype=DTYPE, device=dev)
        for i in range(C):
            nz = inp.emask[i, t2].nonzero()
            if nz.numel():
                last[i] = inp.xsreac_mb[i, t2, int(nz.max())]
        sigav = torch.where(dE > 2.0, total / torch.where(dE > 2.0, dE, torch.ones_like(dE)), last)
        denomki[:, t2] = (
            (2.0 * parspin[t2] + 1.0) * sigav * (emax + 2.0 * cb) * torch.clamp(dE**2, min=100.0)
        )

    for t in range(1, 7):
        if k0 <= 2 and t <= 2:
            continue
        flagknock = k0 in (1, 2) and t == 6
        flaginel = k0 == t
        if not (flagknock or flaginel):
            continue
        ejecmass, ejec2sp1 = parmass[t], 2.0 * parspin[t] + 1.0
        ndelta = abs(parA[k0] - parA[t])
        ccl = 1.0 / 14.0
        ako = 0.0
        termki = torch.zeros(C, dtype=DTYPE, device=dev)
        ckn = torch.as_tensor(params.at("cknock", t), dtype=DTYPE, device=dev)
        if flagknock:
            ako = 1.0 / (2.0 * gscomp[k0] ** 2) + 1.0 / (2.0 * gscomp[6] ** 2)
            termk0 = projmass * denomki[:, k0] * gscomp[k0] * gscomp[6] ** 2 / (
                6.0 * gscomp[k0]
            ) + ejecmass * denomki[:, 6] * gscomp[k0] * gscomp[6] ** 2 / (6.0 * gscomp[6])
            term1 = ccl * xsreacinc_mb * ejec2sp1 * ejecmass
            termki = torch.where(
                termk0 != 0,
                ckn
                * term1
                * Pn[6]
                * gscomp[k0]
                * gscomp[6]
                / torch.where(termk0 != 0, termk0, torch.ones_like(termk0)),
                termki,
            )
        else:
            for t2 in (1, 2, 6):
                termin0 = projmass * denomki[:, k0] * gscomp[k0] * gscomp[t2] ** 2 / (
                    6.0 * gscomp[k0]
                ) + projmass * denomki[:, t2] * gscomp[k0] * gscomp[t2] ** 2 / (6.0 * gscomp[t2])
                term1 = ccl * xsreacinc_mb * proj2sp1 * projmass
                termki = termki + torch.where(
                    termin0 != 0,
                    ckn
                    * term1
                    * Pn[t2]
                    * gscomp[t2]
                    * gscomp[t2]
                    / torch.where(termin0 != 0, termin0, torch.ones_like(termin0)),
                    torch.zeros_like(termin0),
                )
        eout = inp.egrid_mev
        factor1 = inp.xsreac_mb[:, t] * eout
        pcn = preeqpair(
            inp.pair_res_mev[:, t].reshape(C, 1),
            torch.tensor(gscomp[t], dtype=DTYPE, device=dev),
            torch.tensor(ndelta, device=dev),
            inp.ecomp_mev.reshape(C, 1),
            pairmodel,
        )
        eres = inp.ecomp_mev.reshape(C, 1) - inp.s_mev[:, t].reshape(C, 1) - eout - pcn
        ok = inp.emask[:, t] & (eres >= 0)
        u = torch.clamp(eres - ako, min=0.0)
        out[:, t] = torch.where(ok, termki.reshape(C, 1) * factor1 * u, torch.zeros_like(u))
    return out


def complex_particle_spectra(
    inp: PreeqInputs,
    options,
    params,
    *,
    coulbar_mev,
    xsreacinc_mb: Tensor,
    kph: float = 15.0,
) -> dict[str, Tensor]:
    """Complex-particle pre-equilibrium spectra [mb/MeV]: `xspreeqps`, `xspreeqki`, `xspreeqbu`,
    each (C, 7, E), damped below the projectile's Coulomb barrier and capped at `xsflux`.

    TALYS: preeqcomplex.f90:1 (preeqcomplex)
    Test: A-pe
    """
    C, E = inp.C, inp.E
    dev = inp.egrid_mev.device
    if not getattr(options, "flagpecomp", True):
        z = torch.zeros(C, 7, E, dtype=DTYPE, device=dev)
        return {"xspreeqps": z, "xspreeqki": z.clone(), "xspreeqbu": z.clone()}
    ps = stripping(inp, options, params, kph=kph)
    ki = knockout(inp, options, params, coulbar_mev, xsreacinc_mb)
    bu = torch.zeros_like(ps)
    if inp.k0 > 2:
        raise NotImplementedError("T8: breakup (k0 > 2, breakup.f90/breakupAVR.f90) is not ported")
    # Coulomb damping of the whole complex-particle part (preeqcomplex.f90:60-64)
    cb = coulbar_mev[inp.k0]
    damper = torch.ones(C, dtype=DTYPE, device=dev)
    if cb > 0:
        expo = (inp.einc_mev - 0.5 * cb) / (0.1 * cb)
        damper = torch.where(expo <= 80.0, 1.0 - 1.0 / (1.0 + torch.exp(expo)), damper)
    d = damper.reshape(C, 1, 1)
    ps, ki, bu = ps * d, ki * d, bu * d
    pecompsum = ((ps + ki + bu) * inp.deltae_mev.reshape(C, 1, E) * inp.emask).sum((1, 2))
    over = pecompsum > inp.xsflux_mb
    f = torch.where(over, inp.xsflux_mb / pecompsum.clamp(min=1e-300), torch.ones_like(pecompsum))
    f = f.reshape(C, 1, 1)
    return {"xspreeqps": ps * f, "xspreeqki": ki * f, "xspreeqbu": bu * f}
