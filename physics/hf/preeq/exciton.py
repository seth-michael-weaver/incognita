"""Two-component exciton model: matrix elements, emission and transition rates, lifetimes,
pre-equilibrium spectra, pairing and surface corrections.

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

Task: T8 (physics/hf/CONTRACT.md §7). Acceptance test: A-pe (§6).

TALYS routines ported here (file:line of the subroutine/function statement):
    preeqinit.f90:1 (preeqinit)
    excitoninit.f90:1 (excitoninit)
    exciton.f90:1 (exciton)
    exciton2.f90:1 (exciton2)
    exchange2.f90:1 (exchange2)
    lifetime2.f90:1 (lifetime2)
    emissionrate.f90:1 (emissionrate)
    emissionrate2.f90:1 (emissionrate2)
    matrix.f90:1 (matrix)
    surface.f90:1 (surface)
    lambdapiplus.f90:1 (lambdapiplus)
    lambdanuplus.f90:1 (lambdanuplus)
    lambdapinu.f90:1 (lambdapinu)
    lambdanupi.f90:1 (lambdanupi)
    preeqcorrect.f90:1 (preeqcorrect)
    preeqpair.f90:1 (preeqpair)
    preeqtotal.f90:1 (preeqtotal)
    preeq.f90:1 (preeq)

Batching (§4.2). The exciton states (ppi, hpi, pnu, hnu) TALYS loops over are enumerated once
into a flat axis `S`; every quantity is a tensor over (C, S), (C, S, 7) or (C, S, 7, E) with
`C` cases and `E` emission-grid points, so a whole target's energy list is one call. The only
Python loops left are over the particle number `p` (the `lifetime2` recursion, at most 6
steps), over the `nexcbins` integration points of `preeqmode 2` and over the hole index in
`finitewell` — all inherent to the physics and all tiny.

Differentiable with respect to the §4.4 continuous parameters that enter here: `M2constant`
(and `M2limit`, `M2shift`, `Rpipi`, `Rnunu`, `Rpinu`, `Rnupi`), the single-particle densities
`g`/`gp`/`gn`, and the surface well depth `esurf`.

Transmission / inverse cross sections arrive injected (`xsreac_mb`, contract §5); nothing here
reads the optical model.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

import numpy as np
import torch
from torch import Tensor

from physics.hf.core.constants import talys_constants
from physics.hf.core.tensors import DTYPE
from physics.hf.density.particle_hole import (
    EFERMI_MEV,
    NUMPARX,
    apauli2,
    finitewell,
    phdens2,
    ph_override,
    phmicro_on,
    preeqpair,
)

NEXCBINS_PRIMARY_DIV = 2  # lambdapiplus.f90:120 (primary: nbins/2)
NEXCBINS_SECONDARY_DIV = 4  # lambdapiplus.f90:122


# --------------------------------------------------------------------------- exciton states


@dataclass(frozen=True)
class ExcitonStates:
    """The (ppi, hpi, pnu, hnu) configurations TALYS's `exciton2`/`exciton2out` loop over, in
    TALYS's own order: outer loop over the particle number p = p0..maxpar, inner over ppi.

    `hpi = ppi - ppi0` and `hnu = pnu - pnu0` because the never-come-back solution only creates
    particle-hole pairs on top of the projectile's own nucleons (exciton2.f90:78-88).
    """

    ppi: Tensor  # (S,) int64
    hpi: Tensor
    pnu: Tensor
    hnu: Tensor
    ppi0: int
    hpi0: int
    pnu0: int
    hnu0: int
    p0: int
    maxpar: int

    @property
    def p(self) -> Tensor:
        return self.ppi + self.pnu

    @property
    def h(self) -> Tensor:
        return self.hpi + self.hnu

    @property
    def n(self) -> Tensor:
        return self.ppi + self.hpi + self.pnu + self.hnu

    @property
    def size(self) -> int:
        return int(self.ppi.shape[0])

    def index_of(self, ppi: int, pnu: int) -> int | None:
        m = (self.ppi == ppi) & (self.pnu == pnu)
        idx = torch.nonzero(m).flatten()
        return int(idx[0]) if idx.numel() else None


def exciton_states(
    k0: int = 1,
    maxpar: int = NUMPARX,
    device=None,
    *,
    initial: tuple[int, int, int, int] | None = None,
) -> ExcitonStates:
    """Initial exciton configuration and the state list (preeq.f90:60-77, exciton2.f90:78-100).

    `p0 = parA(k0)`, `ppi0 = parZ(k0)`, `pnu0 = parN(k0)`, all hole numbers 0; a photonuclear
    run (k0 = 0) starts from one neutron particle instead. `initial` overrides the whole
    configuration with an explicit `(ppi0, hpi0, pnu0, hnu0)`, which is what `multipreeq2`'s
    `mpreeqmode 1` restart needs (multipreeq2.f90:92-107).

    TALYS: preeq.f90:1 (preeq)
    Test: A-pe
    """
    c = talys_constants()
    if initial is not None:
        ppi0, hpi0, pnu0, hnu0 = initial
        p0 = ppi0 + pnu0
        rows = []
        for p in range(p0, maxpar + 1):
            for ppi in range(ppi0, maxpar + 1):
                hpi = hpi0 + ppi - ppi0
                for pnu in range(pnu0, maxpar + 1):
                    if ppi + pnu == p:
                        rows.append((ppi, hpi, pnu, hnu0 + pnu - pnu0))
        t = lambda i: torch.tensor([r[i] for r in rows], dtype=torch.int64, device=device)  # noqa: E731
        return ExcitonStates(t(0), t(1), t(2), t(3), ppi0, hpi0, pnu0, hnu0, p0, maxpar)
    if k0 == 0:  # preeq.f90:69-76
        p0, ppi0, pnu0 = 1, 0, 1
    else:
        p0, ppi0, pnu0 = c["parA"][k0], c["parZ"][k0], c["parN"][k0]
    hpi0 = hnu0 = 0
    rows = []
    for p in range(p0, maxpar + 1):
        for ppi in range(ppi0, maxpar + 1):
            hpi = ppi - ppi0
            for pnu in range(pnu0, maxpar + 1):
                if ppi + pnu == p:
                    rows.append((ppi, hpi, pnu, pnu - pnu0))
    t = lambda i: torch.tensor([r[i] for r in rows], dtype=torch.int64, device=device)  # noqa: E731
    return ExcitonStates(t(0), t(1), t(2), t(3), ppi0, hpi0, pnu0, hnu0, p0, maxpar)


# --------------------------------------------------------------------------- inputs


@dataclass(frozen=True)
class PreeqInputs:
    """Everything the two-component exciton model needs for `C` cases, TALYS's names kept.

    Leading axis is the case axis `C` (contract §4.2); `E` is the emission grid. Injected from
    upstream tasks: `xsreac_mb` from the inverse cross sections (T5 / dumps), `s_mev` from
    masses (T2), `pair_mev`/`alev` from the level-density parameters (T6), the grid from T1.

    Index `type` runs 0..6 = gamma, n, p, d, t, h, alpha; entry 0 of `gp_res`/`gn_res`/
    `pair_mev`/`alev_res` is the compound nucleus itself, since gamma emission leaves it.
    """

    Z: int  # target charge number
    A: int  # target mass number
    k0: int
    einc_mev: Tensor  # (C,)
    ecomp_mev: Tensor  # (C,)  Etotal, exciton2.f90:76
    esurf_mev: Tensor  # (C,)  preeq.f90:80-89
    egrid_mev: Tensor  # (C, E)
    deltae_mev: Tensor  # (C, E)
    emask: Tensor  # (C, 7, E) bool: ebegin(type) <= nen <= eend(type)
    xsreac_mb: Tensor  # (C, 7, E)
    s_mev: Tensor  # (C, 7)   S(0, 0, type)
    wfac: Tensor  # (C, 7)   excitoninit.f90:64-72
    gp_cn: Tensor  # (C,)
    gn_cn: Tensor  # (C,)
    pair_cn_mev: Tensor  # (C,)
    gp_res: Tensor  # (C, 7)
    gn_res: Tensor  # (C, 7)
    pair_res_mev: Tensor  # (C, 7)
    xsflux_mb: Tensor  # (C,)  preeq.f90:105-106
    a_init: int  # Ainit, mass number of the compound system
    nbins: int = 40
    primary: bool = True

    @property
    def C(self) -> int:
        return int(self.einc_mev.shape[0])

    @property
    def E(self) -> int:
        return int(self.egrid_mev.shape[1])


def surface_well_depth(k0: int, einc_mev: Tensor, a_init: int) -> Tensor:
    """`surface(type, elab)` [MeV], the well depth felt by the first hole (surface.f90:33-38).

    TALYS: surface.f90:1 (surface)
    Test: A-pe
    """
    onethird = talys_constants()["onethird"]
    e4 = einc_mev**4
    if k0 == 1:
        return 12.0 + 26.0 * e4 / (e4 + (245.0 / (a_init**onethird)) ** 4)
    return 22.0 + 16.0 * e4 / (e4 + (450.0 / (a_init**onethird)) ** 4)


def esurf(options, params, k0: int, einc_mev: Tensor, a_init: int) -> Tensor:
    """`Esurf` [MeV] (preeq.f90:80-89): Efermi unless `preeqsurface` is on, in which case the
    `esurf` keyword, or `surface(k0, Einc)` for its -1 sentinel.

    TALYS: preeq.f90:1 (preeq)
    Test: A-pe
    """
    ef = torch.full_like(einc_mev, EFERMI_MEV)
    if not getattr(options, "flagsurface", True):
        return ef
    e0 = torch.as_tensor(params.at("esurf"), dtype=DTYPE, device=einc_mev.device)
    if bool((e0 == -1.0).all()):
        if k0 in (1, 2):
            return surface_well_depth(k0, einc_mev, a_init)
        return ef
    return e0.expand_as(ef)


# --------------------------------------------------------------------------- matrix element


def matrix_elements(
    a_compound: int, n: Tensor, ecomp_mev: Tensor, options, params
) -> dict[str, Tensor]:
    """The two-component squared matrix elements M2pipi/M2nunu/M2pinu/M2nupi (matrix.f90:39-53).

    ``M2 = M2constant/A^3 * aproj * (M2limit*7.48 + 4.62e5/(Ecomp/(n*aproj) + M2shift*10.7)^3)``,
    multiplied by 1.20 for `preeqmode 1`; the four two-component elements are `Rpipi`, `Rnunu`,
    `Rpinu`, `Rnupi` times it. Shapes broadcast: `n` is (S,) and `ecomp_mev` (C,), so the result
    is (C, S). Differentiable in all five parameters (§4.4).

    TALYS: matrix.f90:1 (matrix)
    Test: A-pe
    """
    c = talys_constants()
    aproj = max(c["parA"][options.k0], 1)
    p = lambda k: torch.as_tensor(params.at(k), dtype=DTYPE, device=ecomp_mev.device)  # noqa: E731
    m2c, m2limit, m2shift = p("m2constant"), p("m2limit"), p("m2shift")
    ec = ecomp_mev.reshape(-1, 1)
    nf = n.reshape(1, -1).to(DTYPE)
    m2 = (
        m2c
        / (float(a_compound) ** 3)
        * aproj
        * (m2limit * 7.48 + 4.62e5 / ((ec / (nf * aproj) + m2shift * 10.7) ** 3))
    )
    if options.preeqmode == 1:
        m2 = 1.20 * m2
    if not getattr(options, "flag2comp", True):
        return {"M2": m2 * 0.50}
    return {
        "M2": m2,
        "M2pipi": p("rpipi") * m2,
        "M2nunu": p("rnunu") * m2,
        "M2pinu": p("rpinu") * m2,
        "M2nupi": p("rnupi") * m2,
    }


# --------------------------------------------------------------------------- emission rates


def phmicro_zn0(inp: "PreeqInputs", options):
    """PHMICRO: (Z0, N0) of the initial compound nucleus when `phmodel 2` / INCOGNITA_PHMODEL=2 is on, else None.

    TALYS: (none -- Incognita extension, not a TALYS routine)
    Test: none in the public suite
    """
    if not phmicro_on(options):
        return None
    z0 = int(inp.Z) + int(talys_constants()["parZ"][inp.k0])
    return (z0, int(inp.a_init) - z0)


def _shift(states: ExcitonStates, dppi=0, dhpi=0, dpnu=0, dhnu=0):
    return (
        states.ppi + dppi,
        states.hpi + dhpi,
        states.pnu + dpnu,
        states.hnu + dhnu,
    )


def emission_rates(inp: PreeqInputs, states: ExcitonStates, options, params) -> dict[str, Tensor]:
    """Two-component emission rates (emissionrate2.f90:67-172).

    Returns ``wemission2`` (C, S, 7, E) [s^-1 MeV^-1], ``wemispart2`` (C, S, 7) [s^-1] and
    ``wemistot2`` (C, S) [s^-1]. `escape width` in `exciton*.out` is ``wemispart2 * hbar``.

    TALYS: emissionrate2.f90:1 (emissionrate2)
    Test: A-pe
    """
    c = talys_constants()
    parZ, parN = c["parZ"], c["parN"]
    C, E, S = inp.C, inp.E, states.size
    dev = inp.egrid_mev.device
    pairmodel = getattr(options, "pairmodel", 2)
    rgamma = torch.as_tensor(params.at("rgamma"), dtype=DTYPE, device=dev)

    # (C, S) helpers ------------------------------------------------------
    gsp_cn = inp.gp_cn.reshape(C, 1)
    gsn_cn = inp.gn_cn.reshape(C, 1)
    gs_cn = gsp_cn + gsn_cn
    n_s = states.n.reshape(1, S)
    h_s = states.h.reshape(1, S)

    surfwell = (bool(getattr(options, "flagsurface", True)) and inp.primary) & (h_s == 1).expand(
        C, S
    )
    edepth = torch.where(
        surfwell,
        inp.esurf_mev.reshape(C, 1).expand(C, S),
        torch.full((1, 1), EFERMI_MEV, dtype=DTYPE, device=dev).expand(C, S),
    )

    ap2_cn = apauli2(*_shift(states), gsp_cn, gsn_cn)  # (C, S), TALYS's Apauli2 table
    pair_cn = preeqpair(
        inp.pair_cn_mev.reshape(C, 1), gs_cn, n_s, inp.ecomp_mev.reshape(C, 1), pairmodel
    )
    u_cn = inp.ecomp_mev.reshape(C, 1) - pair_cn
    phcomp = phdens2(*_shift(states), gsp_cn, gsn_cn, u_cn, edepth, surfwell, ap2=ap2_cn)  # (C, S)
    zn0 = phmicro_zn0(inp, options)  # PHMICRO: tabulated microscopic p-h densities (phmodel 2), None = off
    phcomp = ph_override(phcomp, *_shift(states), u_cn, 0, 0, zn0)

    # (C, S, 7, E) grids --------------------------------------------------
    eout = inp.egrid_mev.reshape(C, 1, 1, E)
    dE = inp.deltae_mev.reshape(C, 1, 1, E)
    xs = inp.xsreac_mb.reshape(C, 1, 7, E)
    wf = inp.wfac.reshape(C, 1, 7, 1)
    s_t = inp.s_mev.reshape(C, 1, 7, 1)
    mask = inp.emask.reshape(C, 1, 7, E).expand(C, S, 7, E)

    eres = inp.ecomp_mev.reshape(C, 1, 1, 1) - s_t - eout
    light = torch.tensor([True] * 3 + [False] * 4, device=dev).reshape(1, 1, 7, 1)
    eres = torch.where(light, torch.minimum(eres, inp.ecomp_mev.reshape(C, 1, 1, 1)), eres)
    open_e = mask & (eres >= 0)

    factor = wf * xs * eout  # (C, S, 7, E)

    # --- gamma (type 0): emissionrate2.f90:117-133
    # NATIVEX2: only the type-0 column of the gamma terms is kept (`is_gamma` below), so they are
    # evaluated on that column alone (element for element the same numbers)
    eres_g = eres[:, :, 0:1, :]
    pair_g = preeqpair(
        inp.pair_cn_mev.reshape(C, 1, 1, 1),
        gs_cn.reshape(C, 1, 1, 1),
        n_s.reshape(1, S, 1, 1),
        eres_g,
        pairmodel,
    )
    u_g = torch.maximum(eres_g - pair_g, pair_g)
    ef = torch.full((), EFERMI_MEV, dtype=DTYPE, device=dev)
    gsp4 = gsp_cn.reshape(C, 1, 1, 1)
    gsn4 = gsn_cn.reshape(C, 1, 1, 1)
    sh = lambda *d: tuple(x.reshape(1, S, 1, 1) for x in _shift(states, *d))  # noqa: E731
    phres1 = 0.5 * (
        ph_override(phdens2(*sh(-1, -1, 0, 0), gsp4, gsn4, u_g, ef, False, gsp_pauli=gsp4, gsn_pauli=gsn4),
                    *sh(-1, -1, 0, 0), u_g, 0, 0, zn0)
        + ph_override(phdens2(*sh(0, 0, -1, -1), gsp4, gsn4, u_g, ef, False, gsp_pauli=gsp4, gsn_pauli=gsn4),
                      *sh(0, 0, -1, -1), u_g, 0, 0, zn0)
    )
    phres2 = ph_override(phdens2(*sh(), gsp4, gsn4, u_g, ef, False, gsp_pauli=gsp4, gsn_pauli=gsn4),
                         *sh(), u_g, 0, 0, zn0)
    gs4 = gs_cn.reshape(C, 1, 1, 1)
    g2e = gs4 * gs4 * eout
    nn = n_s.reshape(1, S, 1, 1).to(DTYPE)
    branchplus = torch.where(nn >= 2, g2e / (gs4 * (nn - 2) + g2e), torch.zeros_like(g2e))
    branchzero = gs4 * nn / (gs4 * nn + g2e)
    phc4 = phcomp.reshape(C, S, 1, 1)
    ok_c = phc4 > 1.0e-10
    phratio_g = torch.where(
        ok_c,
        (branchplus * phres1 + branchzero * phres2)
        / torch.where(ok_c, phc4, torch.ones_like(phc4)),
        torch.zeros_like(phc4),
    )
    w_gamma = rgamma * factor[:, :, 0:1, :] * eout * phratio_g  # the extra Eout, :118
    ramp = pegamma_ramp(options)
    if ramp > 0.0:
        # PEGAMMA (Incognita extension, default OFF): the equidistant-spacing density of an exciton state
        # switches on as a step at its Pauli + pairing threshold (for n = 1 it IS a step, (U - A)^0),
        # so the photon emission of that state -- the semi-direct capture -- appears at full strength
        # from one incident energy to the next. Here the photon emission rate of each state rises
        # continuously from its threshold, 1 - exp(-(U - A)/ramp), U = Ecomp - P(n), A = Apauli2.
        above = (u_cn - ap2_cn).clamp(min=0.0)
        w_gamma = w_gamma * (-torch.expm1(-above / ramp)).reshape(C, S, 1, 1)
    gamma_on = (
        torch.tensor(inp.primary, device=dev)
        & (n_s.reshape(1, S, 1, 1) <= 7)
        & open_e[:, :, 0:1, :]
    )
    w_gamma = torch.where(gamma_on, w_gamma, torch.zeros_like(w_gamma))

    # --- particles (type 1..6): emissionrate2.f90:135-145
    zejec = torch.tensor(parZ, device=dev).reshape(1, 1, 7, 1)
    nejec = torch.tensor(parN, device=dev).reshape(1, 1, 7, 1)
    ppires = states.ppi.reshape(1, S, 1, 1) - zejec
    pnures = states.pnu.reshape(1, S, 1, 1) - nejec
    nres = n_s.reshape(1, S, 1, 1) - zejec - nejec
    gsp_r = inp.gp_res.reshape(C, 1, 7, 1)
    gsn_r = inp.gn_res.reshape(C, 1, 7, 1)
    pair_r = preeqpair(inp.pair_res_mev.reshape(C, 1, 7, 1), gsp_r + gsn_r, nres, eres, pairmodel)
    ures = torch.maximum(eres - pair_r, pair_r)
    ewell = torch.where(
        torch.tensor([t > 2 for t in range(7)], device=dev).reshape(1, 1, 7, 1),
        ef.expand(1, 1, 7, 1),
        edepth.reshape(C, S, 1, 1).expand(C, S, 7, 1),
    )
    sw4 = surfwell.reshape(C, S, 1, 1).expand(C, S, 7, 1)
    # Apauli2 keeps the compound-nucleus table even for the residual (phdens2.f90:44)
    ap2_res = apauli2(
        ppires, states.hpi.reshape(1, S, 1, 1), pnures, states.hnu.reshape(1, S, 1, 1), gsp4, gsn4
    )
    phres = phdens2(
        ppires,
        states.hpi.reshape(1, S, 1, 1),
        pnures,
        states.hnu.reshape(1, S, 1, 1),
        gsp_r,
        gsn_r,
        ures,
        ewell,
        sw4,
        ap2=ap2_res,
    )
    # PHMICRO: residual nucleus of ejectile type t is (Zix, Nix) = (parZ(t), parN(t)) (emissionrate2.f90:218)
    phres = ph_override(phres, ppires, states.hpi.reshape(1, S, 1, 1), pnures, states.hnu.reshape(1, S, 1, 1), ures,
                        zejec, nejec, zn0)
    w_part = torch.where(
        ok_c,
        factor * phres / torch.where(ok_c, phc4, torch.ones_like(phc4)),
        torch.zeros_like(phres),
    )
    allowed = (ppires >= 0) & (pnures >= 0) & (h_s.reshape(1, S, 1, 1) != 0)
    w_part = torch.where(allowed & open_e, w_part, torch.zeros_like(w_part))

    is_gamma = torch.arange(7, device=dev).reshape(1, 1, 7, 1) == 0
    wemission2 = torch.where(is_gamma, w_gamma, w_part)
    wemission2 = torch.where(ok_c.expand_as(wemission2), wemission2, torch.zeros_like(wemission2))

    # --- integrate over the grid, with TALYS's partial top bin (emissionrate2.f90:104-112)
    wemispart2 = (wemission2 * dE * open_e).sum(-1)  # (C, S, 7)
    idx = torch.arange(E, device=dev).reshape(1, 1, 1, E)
    last = torch.where(open_e, idx, torch.full_like(idx, -1)).amax(-1)  # (C, S, 7)
    closes = (mask & ~open_e & (idx > last.unsqueeze(-1))).any(-1) & (last >= 0)
    li = last.clamp(min=0)
    gather = lambda x: torch.gather(x.expand(C, S, 7, E), 3, li.unsqueeze(-1)).squeeze(-1)  # noqa: E731
    emax = inp.ecomp_mev.reshape(C, 1, 1) - inp.s_mev.reshape(C, 1, 7)
    dtop = emax - (gather(eout) + 0.5 * gather(dE))
    wlast = torch.gather(wemission2, 3, li.unsqueeze(-1)).squeeze(-1)
    wemispart2 = wemispart2 + torch.where(closes, wlast * dtop, torch.zeros_like(dtop))

    # --- gamma-only states are dropped (emissionrate2.f90:161-170)
    wemistot2 = wemispart2.sum(-1)
    only_g = (n_s > 1) & (wemistot2 == wemispart2[..., 0])
    wemistot2 = torch.where(only_g, torch.zeros_like(wemistot2), wemistot2)
    wemispart2 = torch.cat(
        [
            torch.where(only_g, torch.zeros_like(wemispart2[..., 0]), wemispart2[..., 0]).unsqueeze(
                -1
            ),
            wemispart2[..., 1:],
        ],
        dim=-1,
    )
    wsum = wemission2.sum(2)  # (C, S, E): wemissum2
    if ramp > 0.0:
        # PEGAMMA: TALYS keeps the photons of an n > 1 state in an outgoing bin only if a particle can
        # be emitted at the bin CENTRE, so the bin that holds the particle end point (Eout = Einc for
        # neutrons: the capture edge) flips on/off as the incident energy crosses bin centres. Here
        # each bin keeps the fraction of it that lies below the highest particle end point of the
        # state, Ecomp - S(type) over the types it emits: the same cut, continuous in the energy.
        popen = (w_part[:, :, 1:, :] > 0).any(-1)  # (C, S, 6)
        emax_t = (inp.ecomp_mev.reshape(C, 1) - inp.s_mev[:, 1:]).reshape(C, 1, 6).expand(C, S, 6)
        eopen = torch.where(popen, emax_t, torch.full_like(emax_t, -1.0e30)).amax(-1)  # (C, S)
        e0, d0 = eout[:, :, 0, :], dE[:, :, 0, :]  # (C, 1, E)
        frac = ((eopen.reshape(C, S, 1) - (e0 - 0.5 * d0)) / d0).clamp(0.0, 1.0)
        keep = torch.where(n_s.reshape(1, S, 1) > 1, frac, torch.ones_like(frac))
        gcol = wemission2[:, :, 0, :] * keep
    else:
        drop = (n_s.reshape(1, S, 1) > 1) & (wsum == wemission2[:, :, 0, :])
        gcol = torch.where(drop, torch.zeros_like(wemission2[:, :, 0, :]), wemission2[:, :, 0, :])
    wemission2 = torch.cat([gcol.unsqueeze(2), wemission2[:, :, 1:, :]], dim=2)
    return {
        "wemission2": wemission2,
        "wemispart2": wemispart2,
        "wemistot2": wemistot2,
        "phcomp": phcomp,
        "u_cn": u_cn,
        "edepth": edepth,
        "surfwell": surfwell,
        "ap2_cn": ap2_cn,
    }


# --------------------------------------------------------------------------- transition rates


def _nexcbins(inp: PreeqInputs) -> int:
    div = NEXCBINS_PRIMARY_DIV if inp.primary else NEXCBINS_SECONDARY_DIV
    return max(inp.nbins // div, 2)


def _lambda_plus_analytic(states, m2, gs_same, gs_other, u, edepth, surfwell, gsp, gsn, kind):
    """`lambdapiplus`/`lambdanuplus`, preeqmode 1/4 or n == 1 (lambdapiplus.f90:96-107)."""
    n = states.n.reshape(1, -1)
    p, h = states.p.reshape(1, -1), states.h.reshape(1, -1)
    nf = n.to(DTYPE)
    fac1 = 2.0 * nf * (nf + 1.0)
    factor1 = talys_constants()["twopihbar"] * gs_same * gs_same / fac1
    if kind == "pi":
        ap_plus = apauli2(*_shift(states, 1, 1, 0, 0), gsp, gsn)
        factor3 = (states.ppi + states.hpi).reshape(1, -1).to(DTYPE) * gsp * m2["M2pipi"] + 2.0 * (
            states.pnu + states.hnu
        ).reshape(1, -1).to(DTYPE) * gsn * m2["M2pinu"]
    else:
        ap_plus = apauli2(*_shift(states, 0, 0, 1, 1), gsp, gsn)
        factor3 = (states.pnu + states.hnu).reshape(1, -1).to(DTYPE) * gsn * m2["M2nunu"] + 2.0 * (
            states.ppi + states.hpi
        ).reshape(1, -1).to(DTYPE) * gsp * m2["M2nupi"]
    ap0 = apauli2(*_shift(states), gsp, gsn)
    term1 = u - ap_plus
    term2 = u - ap0
    ok = (term1 > 0) & (term2 > 0)
    one = torch.ones_like(term1)
    term12 = torch.where(ok, term1 / torch.where(ok, term2, one), one)
    ok = ok & (term12 >= 0.01)
    factor2 = term1**2 * (term12 ** (nf - 1.0))
    out = factor1 * factor2 * factor3 * finitewell(p + 1, h + 1, u, edepth, surfwell)
    return torch.where(ok, out, torch.zeros_like(out))


def _lambda_zero_analytic(states, m2, u, edepth, surfwell, gsp, gsn, kind):
    """`lambdapinu`/`lambdanupi`, preeqmode 1/4 or n == 1 (lambdapinu.f90:72-85)."""
    n = states.n.reshape(1, -1)
    nf = n.to(DTYPE)
    p, h = states.p.reshape(1, -1), states.h.reshape(1, -1)
    ap0 = apauli2(*_shift(states), gsp, gsn)
    if kind == "pinu":
        factor1 = (
            talys_constants()["twopihbar"]
            * (states.ppi * states.hpi).reshape(1, -1).to(DTYPE)
            * m2["M2pinu"]
            / nf
            * gsn
            * gsn
        )
        ap_x = apauli2(*_shift(states, -1, -1, 1, 1), gsp, gsn)
        has = ((states.ppi > 0) & (states.hpi > 0)).reshape(1, -1)
    else:
        factor1 = (
            talys_constants()["twopihbar"]
            * (states.pnu * states.hnu).reshape(1, -1).to(DTYPE)
            * m2["M2nupi"]
            / nf
            * gsp
            * gsp
        )
        ap_x = apauli2(*_shift(states, 1, 1, -1, -1), gsp, gsn)
        has = ((states.pnu > 0) & (states.hnu > 0)).reshape(1, -1)
    bfactor = torch.where(has, torch.maximum(ap0, ap_x), ap0)
    factor2 = u - bfactor
    factor3 = u - ap0
    ok = (factor2 > 0) & (factor3 > 0)
    one = torch.ones_like(factor2)
    factor23 = torch.where(ok, factor2 / torch.where(ok, factor3, one), one)
    ok = ok & (factor23 >= 0.01)
    factor4 = 2.0 * (u - bfactor) + torch.where(
        has, nf * torch.abs(ap0 - ap_x), torch.zeros_like(ap0)
    )
    out = factor1 * (factor23 ** (nf - 1.0)) * factor4 * finitewell(p, h, u, edepth, surfwell)
    return torch.where(ok, out, torch.zeros_like(out))


def _bin_midpoints(nexcbins: int, like: Tensor) -> Tensor:
    """`i - 0.5` for i = 1..nexcbins, as a leading axis broadcastable against `like`."""
    i = torch.arange(1, nexcbins + 1, dtype=DTYPE, device=like.device) - 0.5
    return i.reshape((nexcbins,) + (1,) * like.dim())


def _integrate_plus(states, m2, u, edepth, surfwell, gsp, gsn, nexcbins, kind, zn0=None):
    """`lambdapiplus`/`lambdanuplus`, preeqmode 2 (lambdapiplus.f90:108-186).

    Four collision channels (pi-pi particle/hole, nu-pi particle/hole for `pi`; the mirror for
    `nu`), each integrated over `nexcbins` equal bins between its own Pauli limits.
    """
    tph = talys_constants()["twopihbar"]
    if kind == "pi":
        ap_target = apauli2(*_shift(states, 1, 1, 0, 0), gsp, gsn)
        chans = (
            # (L-shift state, residual state, colliding density, M2, g)
            ((-1, 0, 0, 0), (-1, 0, 0, 0), (2, 1, 0, 0), "M2pipi", gsp),
            ((0, -1, 0, 0), (0, -1, 0, 0), (1, 2, 0, 0), "M2pipi", gsp),
            ((0, 0, -1, 0), (0, 0, -1, 0), (1, 1, 1, 0), "M2nupi", gsn),
            ((0, 0, 0, -1), (0, 0, 0, -1), (1, 1, 0, 1), "M2nupi", gsn),
        )
    else:
        ap_target = apauli2(*_shift(states, 0, 0, 1, 1), gsp, gsn)
        chans = (
            ((0, 0, -1, 0), (0, 0, -1, 0), (0, 0, 2, 1), "M2nunu", gsn),
            ((0, 0, 0, -1), (0, 0, 0, -1), (0, 0, 1, 2), "M2nunu", gsn),
            ((-1, 0, 0, 0), (-1, 0, 0, 0), (1, 0, 1, 1), "M2pinu", gsp),
            ((0, -1, 0, 0), (0, -1, 0, 0), (0, 1, 1, 1), "M2pinu", gsp),
        )
    total = torch.zeros_like(u * ap_target)
    mid = _bin_midpoints(nexcbins, u)
    for lshift, rshift, dens, m2key, gfac in chans:
        ap_l = apauli2(*_shift(states, *lshift), gsp, gsn)
        l1 = ap_target - ap_l
        l2 = u - ap_l
        dex = (l2 - l1) / nexcbins
        dppi, dhpi, dpnu, dhnu = dens
        # SPEEDP: the `nexcbins` mid-points are a leading axis, so the two state densities are
        # evaluated once per channel instead of once per bin (`nbins//2` = 20 bins on the primary
        # compound nucleus, over (C, S) arrays too small for the work to dominate the dispatch).
        # The running sum is still added bin by bin, in TALYS's order.
        uu = l1 + mid * dex
        coll = phdens2(
            torch.tensor(dppi, device=u.device),
            torch.tensor(dhpi, device=u.device),
            torch.tensor(dpnu, device=u.device),
            torch.tensor(dhnu, device=u.device),
            gsp,
            gsn,
            uu,
            edepth,
            surfwell,
        )
        coll = ph_override(coll, dppi, dhpi, dpnu, dhnu, uu, 0, 0, zn0)  # PHMICRO (lambdapiplus.f90:206-209)
        lam = tph * m2[m2key] * coll
        resid = phdens2(*_shift(states, *rshift), gsp, gsn, u - uu, edepth, surfwell)
        resid = ph_override(resid, *_shift(states, *rshift), u - uu, 0, 0, zn0)
        term = lam * gfac * dex * resid
        acc = torch.zeros_like(total)
        for i in range(nexcbins):
            acc = acc + term[i]
        total = total + acc
    phtot = phdens2(*_shift(states), gsp, gsn, u, edepth, surfwell)
    phtot = ph_override(phtot, *_shift(states), u, 0, 0, zn0)
    ok = phtot > 0
    return torch.where(
        ok, total / torch.where(ok, phtot, torch.ones_like(phtot)), torch.zeros_like(total)
    )


def _integrate_zero(states, m2, u, edepth, surfwell, gsp, gsn, nexcbins, kind, zn0=None):
    """`lambdapinu`/`lambdanupi`, preeqmode 2 (lambdapinu.f90:86-137)."""
    tph = talys_constants()["twopihbar"]
    if kind == "pinu":
        ap_l = apauli2(*_shift(states, -1, -1, 0, 0), gsp, gsn)
        dens_coll = (0, 0, 1, 1)
        dens_pair = (1, 1, 0, 0)
        rshift = (-1, -1, 0, 0)
        m2key = "M2pinu"
    else:
        ap_l = apauli2(*_shift(states, 0, 0, -1, -1), gsp, gsn)
        dens_coll = (1, 1, 0, 0)
        dens_pair = (0, 0, 1, 1)
        rshift = (0, 0, -1, -1)
        m2key = "M2nupi"
    ap0 = apauli2(*_shift(states), gsp, gsn)
    l1 = ap0 - ap_l
    l2 = u - ap_l
    dex = (l2 - l1) / nexcbins
    acc = torch.zeros_like(u * ap0)
    ct = lambda v: torch.tensor(v, device=u.device)  # noqa: E731
    uu = l1 + _bin_midpoints(nexcbins, u) * dex  # SPEEDP: all bins at once, see `_integrate_plus`
    po = lambda d, st, e: ph_override(d, *st, e, 0, 0, zn0)  # noqa: E731  PHMICRO (lambdapinu.f90:167-197)
    lam = tph * m2[m2key] * po(phdens2(*[ct(v) for v in dens_coll], gsp, gsn, uu, edepth, surfwell), dens_coll, uu)
    term = lam * po(phdens2(*[ct(v) for v in dens_pair], gsp, gsn, uu, edepth, surfwell), dens_pair, uu) * dex
    term = term * po(phdens2(*_shift(states, *rshift), gsp, gsn, u - uu, edepth, surfwell), _shift(states, *rshift),
                     u - uu)
    for i in range(nexcbins):
        acc = acc + term[i]
    phtot = po(phdens2(*_shift(states), gsp, gsn, u, edepth, surfwell), _shift(states), u)
    ok = phtot > 0
    return torch.where(
        ok, acc / torch.where(ok, phtot, torch.ones_like(phtot)), torch.zeros_like(acc)
    )


def transition_rates(
    inp: PreeqInputs, states: ExcitonStates, options, params, *, emis: dict | None = None
) -> dict[str, Tensor]:
    """The four internal transition rates [s^-1], shape (C, S).

    `preeqmode 2` (TALYS's default) integrates the collision probability over the residual
    excitation energy; `preeqmode 1`/`4`, and every n = 1 state, use the closed form. The
    `damping width` columns of `exciton*.out` are these times hbar.

    TALYS: lambdapiplus.f90:1, lambdanuplus.f90:1, lambdapinu.f90:1, lambdanupi.f90:1
    Test: A-pe
    """
    if emis is None:
        emis = emission_rates(inp, states, options, params)
    C, S = inp.C, states.size
    gsp = inp.gp_cn.reshape(C, 1)
    gsn = inp.gn_cn.reshape(C, 1)
    u = emis["u_cn"]
    edepth, surfwell = emis["edepth"], emis["surfwell"]
    m2 = matrix_elements(inp.a_init, states.n, inp.ecomp_mev, options, params)
    n1 = (states.n.reshape(1, S) == 1).expand(C, S)
    nex = _nexcbins(inp)
    numeric = options.preeqmode in (2, 3)
    if options.preeqmode == 3:
        raise NotImplementedError(
            "T8: preeqmode 3 (optical-model transition rates, bonetti.f90) is not ported"
        )
    from physics.hf.preeq import preeq_nx2

    zn0 = phmicro_zn0(inp, options)
    # NATIVEX2: off the graph, all four rates in one C call (preeq.preeq_nx2); PHMICRO takes the Python loop
    out = None if zn0 is not None else preeq_nx2.transition_rates(inp, states, emis, m2, nex, numeric,
                                                                  talys_constants()["twopihbar"])
    if out is not None:
        out.update(m2)
        return out
    out = {}
    for key, kind, analytic, integrate in (
        ("lambdapiplus", "pi", _lambda_plus_analytic, _integrate_plus),
        ("lambdanuplus", "nu", _lambda_plus_analytic, _integrate_plus),
        ("lambdapinu", "pinu", _lambda_zero_analytic, _integrate_zero),
        ("lambdanupi", "nupi", _lambda_zero_analytic, _integrate_zero),
    ):
        if analytic is _lambda_plus_analytic:
            gs_same = gsp if kind == "pi" else gsn
            ana = analytic(states, m2, gs_same, None, u, edepth, surfwell, gsp, gsn, kind)
        else:
            ana = analytic(states, m2, u, edepth, surfwell, gsp, gsn, kind)
        if numeric:
            num = integrate(states, m2, u, edepth, surfwell, gsp, gsn, nex, kind, zn0)
            val = torch.where(n1, ana, num)
        else:
            val = ana
        out[key] = torch.where(
            (states.n.reshape(1, S) == 0).expand(C, S), torch.zeros_like(val), val
        )
    out.update(m2)
    return out


# --------------------------------------------------------------------------- lifetimes


def exchange_and_lifetime(
    inp: PreeqInputs, states: ExcitonStates, rates: dict, emis: dict
) -> dict[str, Tensor]:
    """`exchange2` + `lifetime2`: the never-come-back strengths `Spre` [s] (C, S).

    `tauexc2 = 1/(lambda+ + lambda0 + wemistot2)`, `Lexc` the ratio of the creation-only
    lifetime to it, `G* = lambda* tauexc2`, and `PP2` the population recursion over the particle
    number. `Spre = PP2 * tauexc2` is the `lifetime` block of `exciton*.out`.

    TALYS: exchange2.f90:1 (exchange2), lifetime2.f90:1 (lifetime2)
    Test: A-pe
    """
    C, S = inp.C, states.size
    tpiplus, tnuplus = rates["lambdapiplus"], rates["lambdanuplus"]
    tpinu, tnupi = rates["lambdapinu"], rates["lambdanupi"]
    wemis = emis["wemistot2"]
    tplus = tpiplus + tnuplus
    texchange = tpinu + tnupi
    tauinv = tplus + texchange + wemis
    zero = torch.zeros_like(tauinv)
    one = torch.ones_like(tauinv)
    live = tplus != 0
    tauexc2 = torch.where(live & (tauinv != 0), 1.0 / torch.where(tauinv != 0, tauinv, one), zero)
    tauinvp = tplus + wemis
    tauexc2p = torch.where(tauinvp != 0, 1.0 / torch.where(tauinvp != 0, tauinvp, one), zero)
    lexc = torch.where(
        live & (tauexc2 != 0), tauexc2p / torch.where(tauexc2 != 0, tauexc2, one), zero
    )
    G = {
        "Gpiplus": tpiplus * tauexc2,
        "Gnuplus": tnuplus * tauexc2,
        "Gpinu": tpinu * tauexc2,
        "Gnupi": tnupi * tauexc2,
    }

    ppi, pnu = states.ppi, states.pnu
    ppi0, pnu0, maxpar = states.ppi0, states.pnu0, states.maxpar
    loc = {(int(ppi[s]), int(pnu[s])): s for s in range(S)}
    dev = tauinv.device
    z = torch.zeros(C, dtype=DTYPE, device=dev)
    pp2: dict[tuple[int, int], Tensor] = {}

    def Gk(name: str, key: tuple[int, int]) -> Tensor:
        return G[name][:, loc[key]] if key in loc else z

    def P(key: tuple[int, int]) -> Tensor:
        return pp2.get(key, z)

    # TALYS runs lifetime2 in order of the particle number p, so every term it reads
    # (p-1 configurations only) is already filled (exciton2.f90:82-90).
    order = sorted(range(S), key=lambda s: (int(states.p[s]), int(ppi[s])))
    for s in order:
        a, b = int(ppi[s]), int(pnu[s])
        hpi, hnu = a - ppi0, b - pnu0
        if a + b == states.p0:
            pp2[(a, b)] = torch.ones(C, dtype=DTYPE, device=dev)
            continue
        term1 = term2 = term3 = term4 = term5 = term6 = term7 = term8 = z
        if a > ppi0 and hpi > states.hpi0:
            term1 = P((a - 1, b)) * Gk("Gpiplus", (a - 1, b))
            term4 = P((a - 1, b)) * Gk("Gnuplus", (a - 1, b))
        if b > pnu0 and hnu > states.hnu0:
            term2 = P((a, b - 1)) * Gk("Gnuplus", (a, b - 1))
            term6 = P((a, b - 1)) * Gk("Gpiplus", (a, b - 1))
        if b < maxpar and hnu < maxpar:
            if a > ppi0 and hpi > states.hpi0:
                term5 = Gk("Gnupi", (a - 1, b + 1))
            if a - 1 > ppi0 and hpi - 1 > states.hpi0:
                term3 = P((a - 2, b + 1)) * Gk("Gpiplus", (a - 2, b + 1))
        if a < maxpar and hpi < maxpar:
            if b > pnu0 and hnu > states.hnu0:
                term8 = Gk("Gpinu", (a + 1, b - 1))
            if b - 1 > pnu0 and hnu - 1 >= states.hnu0:
                term7 = P((a + 1, b - 2)) * Gk("Gnuplus", (a + 1, b - 2))
        pp2[(a, b)] = (
            term1 + term2 + lexc[:, s] * ((term3 + term4) * term5 + (term6 + term7) * term8)
        )
    pp2t = torch.stack([pp2[(int(ppi[s]), int(pnu[s]))] for s in range(S)], dim=1)
    spre = pp2t * tauexc2
    return {"tauexc2": tauexc2, "Lexc": lexc, "PP2": pp2t, "Spre": spre, **G}


# --------------------------------------------------------------------------- spectra


def exciton_model(inp: PreeqInputs, options, params, states: ExcitonStates | None = None) -> dict:
    """The full two-component exciton model for a batch of cases (exciton2.f90:76-140).

    Returns every quantity `exciton*.out` and the exciton part of `preeq*.out` print:
    matrix elements, `wemispart2`/`wemistot2`, the four transition rates, `Spre`, and the
    cross sections `xsstep` (C, 7, maxpar+1, E) and `xspreeq` (C, 7, E), both mb/MeV.

    TALYS: exciton2.f90:1 (exciton2)
    Test: A-pe
    """
    if states is None:
        states = exciton_states(inp.k0, NUMPARX, inp.egrid_mev.device)
    emis = emission_rates(inp, states, options, params)
    rates = transition_rates(inp, states, options, params, emis=emis)
    life = exchange_and_lifetime(inp, states, rates, emis)
    C, E, S = inp.C, inp.E, states.size
    factor = inp.xsflux_mb.reshape(C, 1) * life["Spre"]  # (C, S)
    xs = factor.reshape(C, S, 1, 1) * emis["wemission2"]  # (C, S, 7, E), mb/MeV
    xspreeq = xs.sum(1).clone()  # (C, 7, E)
    xsstep = torch.zeros(C, 7, states.maxpar + 1, E, dtype=DTYPE, device=xs.device)
    for s in range(S):
        xsstep[:, :, int(states.p[s]), :] += xs[:, s]
    return {
        "states": states,
        "xsstep": xsstep,
        "xspreeq": xspreeq,
        "xsstep2": xs,
        **emis,
        **rates,
        **life,
    }


# --------------------------------------------------------------------------- correct + total


@dataclass(frozen=True)
class DiscreteInputs:
    """What `preeqcorrect`/`preeqtotal` need about the discrete levels of each residual.

    `eoutdis_mev[c][t]` is TALYS's `eoutdis(type, i)` for i = 0..Nlast (energies.f90:103-118),
    `nendisc[c][t]` the emission-grid bin holding the last discrete level, `nlast[t]` its NL,
    and `xsdirdisc_mb[c][t]` the direct discrete cross sections (injected: T12/T13).
    """

    eoutdis_mev: list  # [C][7] -> (NL+1,) float arrays
    nendisc: list  # [C][7] int
    nlast: tuple  # (7,) int
    xsdirdisc_mb: list  # [C][7] -> (NL+1,) float arrays
    etop_mev: Tensor  # (C, E)
    ebegin: tuple  # (7,) int
    eend: list  # [C][7] int



def c6fix_on() -> bool:
    """C6FIX (Incognita extension, ENGC10, default OFF): `INCOGNITA_C6FIX` (y/1/on).

    When the last discrete level's emission energy Elast lies ABOVE the top of the emission grid (large positive-Q
    alpha/proton channels: `nendisc` is clamped at `eend`, so Etop(nendisc) < Elast), TALYS's boundary book runs with a
    negative fraction: Rboundary = (Etop(nendisc) - Elast)/deltaE in (-1, 0) gives level NL a NEGATIVE pre-equilibrium
    cross section, scales the top continuum bin UP by (1 - Rboundary) and makes `preeq_total`'s ``- xs * frac`` ADD flux;
    once Rboundary < -1 TALYS's own |Rboundary| > 1 rule zeroes it, so the channel jumps (preeqcorrect.f90:131-132,
    preeqtotal.f90:99-104). That bin lies wholly below Elast, i.e. wholly in the continuum: no part of it belongs to NL.
    ON: Rboundary < 0 -> 0 and frac < 0 -> 0 (the |Rboundary| > 1 branch extended to the whole negative side).

    Test: tests/hf/test_c6fix.py

    TALYS: (none -- Incognita extension, not a TALYS routine)
    """
    return os.environ.get("INCOGNITA_C6FIX", "n").strip().lower() in ("y", "yes", "1", "on", "true")

def preeq_correct(
    spectra: dict, inp: PreeqInputs, disc: DiscreteInputs, states: ExcitonStates
) -> dict:
    """Collapse the pre-equilibrium continuum onto the discrete states and cut it off above the
    last discrete level (preeqcorrect.f90:47-155).

    Mutates nothing: returns new `xspreeq`, `xsstep`, `xspreeqps/ki/bu` plus `xspreeqdisc`
    (C, 7, NL+1), `xspreeqdisctot` (C, 7) and `xspreeqdiscsum` (C,), all mb.

    TALYS: preeqcorrect.f90:1 (preeqcorrect)
    Test: A-pe
    """
    from physics.hf.core.grids import locate_scalar
    from physics.hf.preeq import preeq_nx2

    fast = preeq_nx2.preeq_correct(spectra, inp, disc)  # NATIVEX2: off the graph, on numpy
    if fast is not None:
        return fast
    C, E = inp.C, inp.E
    dev = inp.egrid_mev.device
    out = {
        k: spectra[k].clone() for k in ("xspreeq", "xsstep", "xspreeqps", "xspreeqki", "xspreeqbu")
    }
    # `xsstep2` (C, S, 7, E) is corrected the same way `xsstep` is: preeqcorrect.f90:141-147
    # scales it by (1 - Rboundary) in the last discrete level's bin and :170-176 zeroes it above
    # `nendisc`. Missing that leaves the two-component spectrum running to the kinematic maximum
    # where TALYS has cut it at the last discrete level -- invisible in every A-pe column,
    # because `xsstep2` has exactly one consumer: `population.f90`'s `xspopph2` branch, which is
    # live only at `Einc >= emulpre` (EXCL3).
    if "xsstep2" in spectra:
        out["xsstep2"] = spectra["xsstep2"].clone()
    nlmax = max((len(a) for row in disc.eoutdis_mev for a in row if a is not None), default=1)
    xsdisc = torch.zeros(C, 7, nlmax, dtype=DTYPE, device=dev)
    k0 = inp.k0
    xseps = 1.0e-7  # A0_talys_mod.f90 xseps
    for c in range(C):
        eg = inp.egrid_mev[c].cpu().numpy()
        de = inp.deltae_mev[c]
        etop = disc.etop_mev[c]
        for t in range(7):
            b, e_end = disc.ebegin[t], disc.eend[c][t]
            if b >= e_end:
                continue
            nd = disc.nendisc[c][t]
            esd_all = disc.eoutdis_mev[c][t]
            NL = disc.nlast[t]
            if esd_all is not None:
                for i in range(NL + 1):
                    if disc.xsdirdisc_mb[c][t][i] != 0.0:
                        continue
                    esd = float(esd_all[i])
                    if esd < 0.0:  # preeqcorrect.f90:57 (goto 100)
                        break
                    if i == 0 or (t == k0 and i == 1):
                        esd2 = float(esd_all[0])
                    else:
                        esd2 = 0.5 * (esd + float(esd_all[i - 1]))
                    if i == NL:
                        esd1 = float(esd_all[NL])
                    elif float(esd_all[i + 1]) > 0.0:
                        esd1 = 0.5 * (esd + float(esd_all[i + 1]))
                    else:
                        esd1 = 0.0
                    if t == k0:
                        xs1 = xseps
                    else:
                        n1 = locate_scalar(eg, nd, e_end, esd1)
                        n2 = locate_scalar(eg, nd, e_end, esd2)
                        xs1 = float(
                            0.5
                            * (out["xspreeq"][c, t, n1] + out["xspreeq"][c, t, n2])
                            * (esd2 - esd1)
                        )
                    if i == NL:
                        elast = float(esd_all[NL])
                        rb = (float(etop[nd]) - elast) / float(de[nd])
                        if abs(rb) > 1.0:
                            rb = 0.0
                        if rb < 0.0 and c6fix_on():  # C6FIX: Elast above the grid's top bin
                            rb = 0.0
                        if t != k0:
                            xs1 = float(out["xspreeq"][c, t, nd] * rb)
                        for key in ("xspreeq", "xspreeqps", "xspreeqki", "xspreeqbu"):
                            out[key][c, t, nd] = out[key][c, t, nd] * (1.0 - rb)
                        out["xsstep"][c, t, 1:, nd] = out["xsstep"][c, t, 1:, nd] * (1.0 - rb)
                        if "xsstep2" in out:  # preeqcorrect.f90:141-147
                            out["xsstep2"][c, :, t, nd] = (
                                out["xsstep2"][c, :, t, nd] * (1.0 - rb))
                    xsdisc[c, t, i] = xs1
            hi = slice(nd + 1, min(e_end, E - 1) + 1)
            for key in ("xspreeq", "xspreeqps", "xspreeqki", "xspreeqbu"):
                out[key][c, t, hi] = 0.0
            out["xsstep"][c, t, 1:, hi] = 0.0
            if "xsstep2" in out:  # preeqcorrect.f90:170-176
                out["xsstep2"][c, :, t, hi] = 0.0
    out["xspreeqdisc"] = xsdisc
    out["xspreeqdisctot"] = xsdisc.sum(-1)
    out["xspreeqdiscsum"] = xsdisc.sum((-1, -2))
    return out


def preeq_total(spectra: dict, inp: PreeqInputs, disc: DiscreteInputs, ungate: bool = False, nofrac=None) -> dict:
    """Integrate the spectra and apply TALYS's flux normalisation (preeqtotal.f90:44-129).

    `xssteptot(type, p)` and `xspreeqtot(type)` integrate over the grid up to `nendisc`, minus
    the fraction `Etop(nendisc) - Elast` of the last bin; if the total exceeds `xsflux`
    everything is scaled down by `xsflux / (xspreeqsum + xspreeqdiscsum)`.

    `ungate` (PEGAMMA, default False) keeps the pre-equilibrium photons when no particle flux reaches
    the continuum instead of zeroing them (preeqtotal.f90:92-102): the discrete-level photons are
    kept in that case by TALYS too, and the zeroing turns the photon continuum on as a step where the
    first particle continuum bin opens.

    `nofrac` (PEREMOVE, default None = TALYS): (C, 7) booleans; where True the second ``- xs(nendisc) * frac`` removal is
    skipped, because `preeq_correct` already took the [Elast, Etop(nendisc)] piece out of that bin by the (1 - Rboundary)
    scaling (TALYS removes it twice, so the bin keeps (1 - Rboundary)^2 of its flux in this book).

    TALYS: preeqtotal.f90:1 (preeqtotal)
    Test: A-pe
    """
    C, E = inp.C, inp.E
    dev = inp.egrid_mev.device
    out = {k: (v.clone() if torch.is_tensor(v) else v) for k, v in spectra.items()}
    P = out["xsstep"].shape[2]
    xssteptot = torch.zeros(C, 7, P, dtype=DTYPE, device=dev)
    tot = torch.zeros(C, 7, dtype=DTYPE, device=dev)
    totps = torch.zeros(C, 7, dtype=DTYPE, device=dev)
    totki = torch.zeros(C, 7, dtype=DTYPE, device=dev)
    totbu = torch.zeros(C, 7, dtype=DTYPE, device=dev)
    c6 = c6fix_on()
    for c in range(C):
        de = inp.deltae_mev[c]
        for t in range(7):
            b, e_end = disc.ebegin[t], disc.eend[c][t]
            nd = disc.nendisc[c][t]
            esd_all = disc.eoutdis_mev[c][t]
            elast = float(esd_all[disc.nlast[t]]) if esd_all is not None else 0.0
            frac = float(disc.etop_mev[c][nd]) - elast if elast > 0.0 else 0.0
            if frac < 0.0 and c6:  # C6FIX: Elast above the grid's top bin, nothing of bin nd is discrete
                frac = 0.0
            if nofrac is not None and bool(nofrac[c][t]):  # PEREMOVE: the piece was already removed by the scaling
                frac = 0.0
            sl = slice(b, nd + 1)
            xssteptot[c, t] = (out["xsstep"][c, t, :, sl] * de[sl]).sum(-1) - out["xsstep"][
                c, t, :, nd
            ] * frac
            tot[c, t] = xssteptot[c, t].sum()
            sl2 = slice(b, min(e_end, E - 1) + 1)
            for key, acc in (("xspreeqps", totps), ("xspreeqki", totki), ("xspreeqbu", totbu)):
                acc[c, t] = (out[key][c, t, sl2] * de[sl2]).sum() - out[key][c, t, nd] * frac
    tot = tot + totps + totki + totbu
    xspreeqsum = tot.sum(-1)
    only_gamma = xspreeqsum == tot[:, 0]
    if not ungate and bool(only_gamma.any()):  # preeqtotal.f90:92-102
        tot[:, 0] = torch.where(only_gamma, torch.zeros_like(tot[:, 0]), tot[:, 0])
        xspreeqsum = torch.where(only_gamma, torch.zeros_like(xspreeqsum), xspreeqsum)
        z = only_gamma.reshape(C, 1)
        out["xsstep"][:, 0] = torch.where(
            z.unsqueeze(-1), torch.zeros_like(out["xsstep"][:, 0]), out["xsstep"][:, 0]
        )
        out["xspreeq"][:, 0] = torch.where(
            z, torch.zeros_like(out["xspreeq"][:, 0]), out["xspreeq"][:, 0]
        )
        xssteptot[:, 0] = torch.where(z, torch.zeros_like(xssteptot[:, 0]), xssteptot[:, 0])

    discsum = out.get("xspreeqdiscsum", torch.zeros(C, dtype=DTYPE, device=dev))
    flux = inp.xsflux_mb
    xseps = 1.0e-7
    need = (flux > xseps) & (xspreeqsum + discsum > flux)
    norm = torch.where(
        need,
        flux / (xspreeqsum + discsum).clamp(min=1e-300),
        torch.ones(C, dtype=DTYPE, device=dev),
    )
    for key in ("xspreeq", "xspreeqps", "xspreeqki", "xspreeqbu"):
        out[key] = out[key] * norm.reshape(C, 1, 1)
    out["xsstep"] = out["xsstep"] * norm.reshape(C, 1, 1, 1)
    out["xsstep2"] = out["xsstep2"] * norm.reshape(C, 1, 1, 1)
    if "xspreeqdisc" in out:
        out["xspreeqdisc"] = out["xspreeqdisc"] * norm.reshape(C, 1, 1)
        out["xspreeqdisctot"] = out["xspreeqdisctot"] * norm.reshape(C, 1)
        out["xspreeqdiscsum"] = discsum * norm
    out["xssteptot"] = xssteptot * norm.reshape(C, 1, 1)
    out["xspreeqtot"] = tot * norm.reshape(C, 1)
    out["xspreeqtotps"] = totps * norm.reshape(C, 1)
    out["xspreeqtotki"] = totki * norm.reshape(C, 1)
    out["xspreeqtotbu"] = totbu * norm.reshape(C, 1)
    out["xspreeqsum"] = torch.where(need, flux - discsum * norm, xspreeqsum)
    out["preeqnorm"] = torch.where(need, norm, torch.zeros_like(norm))
    return out


def pegamma_ramp(options) -> float:
    """PEGAMMA's ramp width [MeV]: the `pegammaramp` keyword (Incognita extension), else the environment
    `INCOGNITA_PEGAMMA` (a number of MeV); 0, unset or empty = OFF = TALYS.

    Test: tests/hf/test_pegamma.py

    TALYS: (none -- Incognita extension, not a TALYS routine)
    """
    r = float(getattr(options, "pegammaramp", 0.0) or 0.0)
    if r > 0.0:
        return r
    env = os.environ.get("INCOGNITA_PEGAMMA", "").strip().lower()
    return 0.0 if env in ("", "0", "off", "n", "no") else max(float(env), 0.0)


def pegamma_collapse(res: dict, spec0: Tensor, inp: PreeqInputs, disc: DiscreteInputs) -> dict:
    """PEGAMMA: the photon part of `preeq_correct`'s collapse onto the discrete states, flux-conserving.

    TALYS gives level i the photon spectrum at the grid bin that CONTAINS each of its two boundaries
    times the width (a step function of the incident energy as the levels slide across the bins), and
    the last discrete level `xspreeq(nendisc) * Rboundary`, a spectrum in mb/MeV times a fraction
    (preeqcorrect.f90:115-133), which oscillates with the grid. Here each level gets the integral of
    the linearly interpolated photon spectrum between the same boundaries (mb), so the discrete photon
    cross sections move continuously with the incident energy. Only type 0; nothing else changes.

    Test: tests/hf/test_pegamma.py

    TALYS: (none -- Incognita extension, not a TALYS routine)
    """
    disc_xs = res["xspreeqdisc"].clone()
    for c in range(inp.C):
        b, e_end = disc.ebegin[0], disc.eend[c][0]
        esd_all = disc.eoutdis_mev[c][0]
        if b >= e_end or esd_all is None:
            continue
        eg = inp.egrid_mev[c].detach().cpu().numpy().astype(float)
        y = spec0[c, 0].detach().cpu().numpy().astype(float)
        top = float(esd_all[0])  # Ecomp: the photon end point
        # knots: the bin centres at or below the end point (a bin whose centre lies above it is masked
        # to zero, which would cut the spectrum a grid-dependent distance below the end point), then
        # the last one carried flat to the end point
        jl = b + int(np.searchsorted(eg[b:e_end + 1], top, side="right")) - 1
        if jl < b:
            continue
        xk, yk = eg[b:jl + 1], y[b:jl + 1]
        if top > xk[-1]:
            xk, yk = np.append(xk, top), np.append(yk, yk[-1])
        NL = disc.nlast[0]
        for i in range(NL + 1):
            if disc.xsdirdisc_mb[c][0][i] != 0.0:
                continue
            esd = float(esd_all[i])
            if esd < 0.0:
                break
            esd2 = top if i == 0 else 0.5 * (esd + float(esd_all[i - 1]))
            if i == NL:
                esd1 = float(esd_all[NL])
            elif float(esd_all[i + 1]) > 0.0:
                esd1 = 0.5 * (esd + float(esd_all[i + 1]))
            else:
                esd1 = 0.0
            t = np.linspace(esd1, esd2, 129)
            f = np.interp(t, xk, yk, left=0.0, right=0.0)
            disc_xs[c, 0, i] = float(np.sum(0.5 * (f[1:] + f[:-1]) * np.diff(t))) if esd2 > esd1 else 0.0
    return {"xspreeqdisc": disc_xs, "xspreeqdisctot": disc_xs.sum(-1), "xspreeqdiscsum": disc_xs.sum((-1, -2))}


PCDIAG: list = []  # PECOLLAPSE: per (case, type) conservation records when INCOGNITA_PECOLLAPSE_DIAG=1 (output only)
_PC_KEYS = ("xspreeq", "xsstep", "xspreeqps", "xspreeqki", "xspreeqbu", "xsstep2")


def pecollapse_mode(options) -> str:
    """PECOLLAPSE (Incognita extension, default OFF): `pecollapse n|c|c2` keyword, else `INCOGNITA_PECOLLAPSE`.

    n = OFF = TALYS's two-point collapse (preeqcorrect.f90:115-133). c = flux-conserving collapse; c2 = c plus the
    last discrete bin's continuum removed once (see `pecollapse`).

    Test: tests/hf/test_pecollapse.py

    TALYS: (none -- Incognita extension, not a TALYS routine)
    """
    v = str(getattr(options, "pecollapse", "n") or "n").strip().lower()
    if v in ("", "n", "no", "off", "0"):
        v = os.environ.get("INCOGNITA_PECOLLAPSE", "n").strip().lower() or "n"
    if v in ("no", "off", "0"):
        v = "n"
    if v not in ("n", "c", "c2"):
        raise ValueError(f"pecollapse must be n, c or c2, not {v!r}")
    return v


def _pe_book(a: dict, c: int, t: int, b: int, hi: int, de: np.ndarray, nd: int | None, frac: float) -> float:
    """The pre-equilibrium flux of type t that `preeq_total` counts (preeqtotal.f90:44-75): sum over bins b..hi of
    (sum_p xsstep + ps + ki + bu) * deltaE, minus the last-discrete-bin fraction `frac` of bin nd when nd is given."""
    tot = 0.0
    for k in ("xspreeqps", "xspreeqki", "xspreeqbu"):
        tot += float(np.dot(a[k][c, t, b:hi + 1], de[b:hi + 1]))
    tot += float(np.dot(a["xsstep"][c, t, :, b:hi + 1].sum(0), de[b:hi + 1]))
    if nd is not None:
        tot -= (float(a["xsstep"][c, t, :, nd].sum()) + sum(float(a[k][c, t, nd]) for k in
                ("xspreeqps", "xspreeqki", "xspreeqbu"))) * frac
    return tot


def _cumlin(x: np.ndarray, y: np.ndarray, q: np.ndarray) -> np.ndarray:
    """Exact integral from x[0] to each q of the piecewise-linear interpolant through (x, y) (zero outside)."""
    q = np.clip(np.asarray(q, float), x[0], x[-1])
    cum = np.concatenate([[0.0], np.cumsum(0.5 * (y[1:] + y[:-1]) * np.diff(x))])
    j = np.clip(np.searchsorted(x, q, side="right") - 1, 0, len(x) - 2)
    h = q - x[j]
    dx = x[j + 1] - x[j]
    slope = np.where(dx > 0.0, (y[j + 1] - y[j]) / np.where(dx > 0.0, dx, 1.0), 0.0)
    return cum[j] + y[j] * h + 0.5 * slope * h * h


# --------------------------------------------------------------------------- PEPAULI (Incognita extension, default OFF)


def _case_inputs(inp: PreeqInputs, c: int, eps: np.ndarray) -> PreeqInputs:
    """Case c of `inp` with the emission grid replaced by the energies `eps` (ascending, MeV). xsreac is the linear interpolant
    of case c's inverse cross sections through the grid nodes; type t is masked on [egrid(ebegin_t), egrid(eend_t)], so at a
    grid node every field equals the original. deltaE is only used by integrated escape widths, which PEPAULI never reads."""
    from dataclasses import replace

    eg = inp.egrid_mev[c].detach().cpu().numpy().astype(float)
    xr = inp.xsreac_mb[c].detach().cpu().numpy().astype(float)
    em = inp.emask[c].detach().cpu().numpy()
    E2 = len(eps)
    xs2 = np.zeros((7, E2))
    m2 = np.zeros((7, E2), dtype=bool)
    for t in range(7):
        idx = np.nonzero(em[t])[0]
        if idx.size == 0:
            continue
        lo, hi = eg[idx[0]], eg[idx[-1]]
        m2[t] = (eps >= lo) & (eps <= hi)
        xs2[t] = np.where(m2[t], np.interp(eps, eg, xr[t]), 0.0)
    s1 = lambda x: x[c:c + 1].detach().clone()  # noqa: E731
    T = lambda a, dt=DTYPE: torch.as_tensor(a, dtype=dt).reshape((1,) + a.shape)  # noqa: E731
    return replace(inp, einc_mev=s1(inp.einc_mev), ecomp_mev=s1(inp.ecomp_mev), esurf_mev=s1(inp.esurf_mev),
                   egrid_mev=T(eps), deltae_mev=T(np.full(E2, 1.0e-3)), emask=T(m2, torch.bool), xsreac_mb=T(xs2),
                   s_mev=s1(inp.s_mev), wfac=s1(inp.wfac), gp_cn=s1(inp.gp_cn), gn_cn=s1(inp.gn_cn),
                   pair_cn_mev=s1(inp.pair_cn_mev), gp_res=s1(inp.gp_res), gn_res=s1(inp.gn_res),
                   pair_res_mev=s1(inp.pair_res_mev), xsflux_mb=s1(inp.xsflux_mb))


def _knock_shape(inp: PreeqInputs, options, c: int, t: int, eps: np.ndarray) -> np.ndarray:
    """xsreac(eps) * eps * u(eps) of `complex.knockout` for type t (u = max(Eres - ako, 0), zero where Eres < 0): the knockout
    spectrum divided by its energy-independent strength termki (knockout.f90:180-200). Only the Kalbach alpha knockout of a
    nucleon projectile exists here (k0 <= 2, t = 6)."""
    c_ = talys_constants()
    parA = c_["parA"]
    A = inp.A
    gscomp = {1: A / 13.0, 2: A / 13.0, 3: A / 52.0, 4: A / 156.0, 5: A / 156.0, 6: A / 208.0}
    k0 = inp.k0
    ako = 1.0 / (2.0 * gscomp[k0] ** 2) + 1.0 / (2.0 * gscomp[6] ** 2)
    pcn = float(preeqpair(inp.pair_res_mev[c:c + 1, t].reshape(1, 1), torch.tensor(gscomp[t], dtype=DTYPE),
                          torch.tensor(abs(parA[k0] - parA[t])), inp.ecomp_mev[c:c + 1].reshape(1, 1),
                          getattr(options, "pairmodel", 2)).reshape(-1)[0])
    sub = _case_inputs(inp, c, eps)
    eres = float(inp.ecomp_mev[c]) - float(inp.s_mev[c, t]) - eps - pcn
    ok = sub.emask[0, t].numpy() & (eres >= 0)
    return np.where(ok, sub.xsreac_mb[0, t].numpy() * eps * np.clip(eres - ako, 0.0, None), 0.0)


def pepauli_onsets(inp: PreeqInputs, options, states: ExcitonStates, c: int) -> np.ndarray:
    """Every ejectile energy (all types) at which some term of the uncorrected PE spectrum of case c switches on, switches
    off or changes form: the Pauli/pairing onsets of the two-component state densities (phdens2.f90:45, density zero unless
    U > Apauli2 + factor_p + factor_n) of every exciton state's residual configuration, of the photon terms (p-1,h-1 and p,h
    of the compound nucleus) and of the Kalbach pickup terms, mapped through U = max(Eres - P, P) (pairmodel 2: P constant)
    or U = Eres - P (pickup); the U = P floor edges Eres = 2P; the kinematic ends Eres = 0; the knockout kink Eres = ako.
    Between two consecutive onsets every term is a smooth function of the ejectile energy.
    Test: tests/hf/test_pepauli.py

    TALYS: (none -- Incognita extension, not a TALYS routine)
    """
    if getattr(options, "pairmodel", 2) == 1:
        raise ValueError("pepauli p/q needs pairmodel 2 (constant pre-equilibrium pairing)")
    cst = talys_constants()
    parZ, parN, parA = cst["parZ"], cst["parN"], cst["parA"]
    ec = float(inp.ecomp_mev[c])
    gpc, gnc = float(inp.gp_cn[c]), float(inp.gn_cn[c])
    out = []

    def thr(ppi, hpi, pnu, hnu, gsp, gsn):
        ppi, hpi, pnu, hnu = (np.asarray(v, float) for v in (ppi, hpi, pnu, hnu))
        ok = (ppi >= 0) & (hpi >= 0) & (pnu >= 0) & (hnu >= 0) & (ppi + hpi + pnu + hnu > 0)
        ap = (np.maximum(ppi, hpi) ** 2 / gpc + np.maximum(pnu, hnu) ** 2 / gnc
              - (ppi * ppi + hpi * hpi + ppi + hpi) / (4.0 * gpc) - (pnu * pnu + hnu * hnu + pnu + hnu) / (4.0 * gnc))
        ap = np.where((ppi == -1) | (hpi == -1) | (pnu == -1) | (hnu == -1), 0.0, ap)
        up = ap + (ppi * ppi + hpi * hpi + ppi + hpi) / (4.0 * gsp) + (pnu * pnu + hnu * hnu + pnu + hnu) / (4.0 * gsn)
        return up[ok]

    def floor_map(emax, P, up):  # U = max(Eres - P, P): open iff U > up
        er = np.where(up >= P, up + P, 0.0)
        return [emax - er, np.array([emax - 2.0 * P, emax])]

    ppi, hpi = states.ppi.cpu().numpy(), states.hpi.cpu().numpy()
    pnu, hnu = states.pnu.cpu().numpy(), states.hnu.cpu().numpy()
    # photons (emissionrate2.f90:117-133), compound nucleus densities, S(gamma) = s_mev[c, 0]
    pg = float(inp.pair_cn_mev[c]) if float(inp.pair_cn_mev[c]) > 0 else 0.0
    emax0 = ec - float(inp.s_mev[c, 0])
    up = np.concatenate([thr(ppi - 1, hpi - 1, pnu, hnu, gpc, gnc), thr(ppi, hpi, pnu - 1, hnu - 1, gpc, gnc),
                         thr(ppi, hpi, pnu, hnu, gpc, gnc)])
    out += floor_map(emax0, pg, up)
    pcn_t = {}
    for t in range(1, 7):
        emax = ec - float(inp.s_mev[c, t])
        P = float(inp.pair_res_mev[c, t]) if float(inp.pair_res_mev[c, t]) > 0 else 0.0
        gsp, gsn = float(inp.gp_res[c, t]), float(inp.gn_res[c, t])
        up = thr(ppi - parZ[t], hpi, pnu - parN[t], hnu, gsp, gsn)
        out += floor_map(emax, P, up)
        if inp.k0 <= 2 and t >= 3:  # Kalbach pickup (stripping.f90), the states of its two exciton sums
            k0 = inp.k0
            dpi, dnu = parZ[k0] - parZ[t], parN[k0] - parN[t]
            a_, b_, c2, d_ = max(dpi, 0), max(-dpi, 0), max(dnu, 0), max(-dnu, 0)
            terms = [(a_ + i, b_ + i, c2 + j, d_ + j) for i in range(4) for j in range(4 - i)]
            terms += [(a_ - i, b_ - j, c2 - k, d_ - ll) for i in range(a_ + 1) for j in range(b_ + 1) for k in range(c2 + 1)
                      for ll in range(d_ + 1) if i + j + k + ll]
            Ares, Zres = inp.a_init - parA[t], inp.Z - parZ[t]
            from physics.hf.preeq.prepare import pickup_densities

            gs_p, gs_n = pickup_densities(Zres, Ares - Zres, 15.0, options)
            pcn = float(preeqpair(inp.pair_res_mev[c:c + 1, t].reshape(1, 1), torch.tensor(gs_p + gs_n, dtype=DTYPE),
                                  torch.tensor(abs(parA[k0] - parA[t])), inp.ecomp_mev[c:c + 1].reshape(1, 1), 2).reshape(-1)[0])
            pcn_t[t] = pcn
            tt = np.array(terms, float).T
            up = thr(tt[0], tt[1], tt[2], tt[3], gs_p, gs_n)
            out += [emax - pcn - up, np.array([emax - pcn])]
            if t == 6:
                gscomp = {1: inp.A / 13.0, 2: inp.A / 13.0}
                ako = 1.0 / (2.0 * gscomp[k0] ** 2) + 1.0 / (2.0 * (inp.A / 208.0) ** 2)
                pck = float(preeqpair(inp.pair_res_mev[c:c + 1, t].reshape(1, 1), torch.tensor(inp.A / 208.0, dtype=DTYPE),
                                      torch.tensor(abs(parA[k0] - parA[t])), inp.ecomp_mev[c:c + 1].reshape(1, 1), 2).reshape(-1)[0])
                out += [np.array([emax - pck, emax - pck - ako])]
    if phmicro_on(options):  # PHMICRO: the tabulated densities are piecewise in U on edens: those nodes are cuts too
        from physics.hf.density.particle_hole import _PH_EDENS

        out += [emax0 - pg - _PH_EDENS]
        for t in range(1, 7):
            P = float(inp.pair_res_mev[c, t]) if float(inp.pair_res_mev[c, t]) > 0 else 0.0
            emax = ec - float(inp.s_mev[c, t])
            out += [emax - P - _PH_EDENS] + ([emax - pcn_t[t] - _PH_EDENS] if t in pcn_t else [])
    v = np.unique(np.concatenate([np.atleast_1d(np.asarray(x, float)) for x in out]))
    return v[np.isfinite(v)]


def pepauli_spectrum(res: dict, pre: dict, inp: PreeqInputs, options, params, states: ExcitonStates, c: int,
                     eps: np.ndarray) -> tuple[np.ndarray, float]:
    """The uncorrected pre-equilibrium spectrum xspreeq(type, eps) [mb/MeV] of case c, (7, len(eps)), at ANY ejectile
    energies, from the converged exciton strengths: sum_s xsflux Spre_s wemission2(s, type, eps) (exciton2.f90:76-140,
    `emission_rates` on the energies eps) + Kalbach pickup (`stripping` on eps) + alpha knockout (strength termki fitted at
    the grid nodes), the complex part carrying the run's Coulomb damping and flux cap (one per-case factor). The grid nodes
    are evaluated with the points; the returned self-check is max |eval - xspreeq| / max xspreeq over all nodes and types.
    Test: tests/hf/test_pepauli.py

    TALYS: (none -- Incognita extension, not a TALYS routine)
    """
    from physics.hf.preeq.complex import stripping

    eg = inp.egrid_mev[c].detach().cpu().numpy().astype(float)
    E = len(eg)
    allx = np.concatenate([eg, np.asarray(eps, float)])
    sub = _case_inputs(inp, c, allx)
    em = emission_rates(sub, states, options, params)
    F = (inp.xsflux_mb[c] * res["Spre"][c]).detach().cpu().numpy().astype(float)  # (S,)
    ex = np.einsum("s,ste->te", F, em["wemission2"][0].detach().cpu().numpy().astype(float))
    ps_raw = stripping(sub, options, params).detach().cpu().numpy()[0].astype(float)
    ps0 = pre["xspreeqps"][c].detach().cpu().numpy().astype(float)
    ki0 = pre["xspreeqki"][c].detach().cpu().numpy().astype(float)
    bu0 = pre["xspreeqbu"][c].detach().cpu().numpy().astype(float)
    if np.any(bu0 != 0.0):
        raise ValueError("pepauli p/q: breakup spectra (k0 > 2) are not handled")
    # one per-case factor: Coulomb damping x flux cap (preeqcomplex.f90:60-75)
    nz = ps_raw[:, :E] > 0
    scale = float(np.median(ps0[nz] / ps_raw[:, :E][nz])) if nz.any() else 0.0
    ps = ps_raw * scale
    ki = np.zeros_like(ps)
    for t in range(1, 7):
        if np.any(ki0[t] != 0.0):
            shp = _knock_shape(inp, options, c, t, allx)
            j = int(np.argmax(np.where(ki0[t] != 0.0, shp[:E], 0.0)))
            ki[t] = shp * (ki0[t, j] / shp[j])
    tot = ex + ps + ki
    ref = pre["xspreeq"][c].detach().cpu().numpy().astype(float)
    chk = float(np.max(np.abs(tot[:, :E] - ref)) / max(float(np.max(np.abs(ref))), 1e-300))
    return tot[:, E:], chk


_GL_X, _GL_W = np.polynomial.legendre.leggauss(24)


def pepauli_integral(f, lo: float, hi: float, cuts: np.ndarray) -> float:
    """Gauss-Legendre (24 points) on each piece of [lo, hi] between consecutive cuts (the analytic onsets): exact to
    rounding for the piecewise-polynomial x linear integrands of the equidistant state density.

    TALYS: (none -- Incognita extension, not a TALYS routine)
    Test: none in the public suite
    """
    if hi <= lo:
        return 0.0
    pts = np.concatenate([[lo], cuts[(cuts > lo) & (cuts < hi)], [hi]])
    a, b = pts[:-1], pts[1:]
    xs = (0.5 * (b - a)[:, None] * _GL_X[None, :] + 0.5 * (a + b)[:, None]).ravel()
    ys = f(xs).reshape(len(a), -1)
    return float(np.sum(0.5 * (b - a) * (ys @ _GL_W)))


def _pepauli_cell(res, pre, inp, ctx, c, t, x, y, egc, win, dirw, elast, u1, mode) -> dict:
    """PEPAULI for one acted (case, type) cell: corrections to WA's window integrals inside the endpoint segments only.
    Returns the updated `sh`/`union` and the endpoint book (segments, onsets used, self-check, fall-back reason)."""
    sh = list(win["sh"])
    union = float(win["union"])
    utop = max(u1, float(win.get("utop", u1)))  # pewindow g `g`: the g.s. window [u1, E0] joins the endpoint range
    lo_all = [float(v) for v in win["lo"]] + [float(p_) for _, p_, _ in dirw]
    up_all = [float(v) for v in win["up"]] + [float(q) for _, _, q in dirw]
    edges = np.unique(np.array(lo_all + up_all + [elast, u1, utop], float))
    nodes = set(np.round(egc, 12).tolist())
    segs, book = [], []
    for k in range(len(x) - 1):
        a, b = float(x[k]), float(x[k + 1])
        if (y[k] > 0.0) == (y[k + 1] > 0.0) or b <= elast or a >= utop:
            continue
        segs.append((k, a, b))
    out = dict(pp_mode=mode, pp_nseg=len(segs), pp_fallback="", pp_chk=0.0, pp_segs=book)
    if not segs:
        return out
    if any(round(a, 12) not in nodes or round(b, 12) not in nodes for _, a, b in segs):
        out["pp_fallback"] = "nongrid"
        return out
    cuts_on = pepauli_onsets(inp, ctx["options"], ctx["states"], c)
    q = []  # (seg, piece lo, piece hi) with every piece inside one window
    for k, a, b in segs:
        lo_, hi_ = max(a, elast), min(b, utop)
        inner = [lo_, hi_] + [v for v in edges if lo_ < v < hi_]
        if mode in ("p", "g"):
            inner += [v for v in cuts_on if lo_ < v < hi_]
        else:
            inner += [v for v in (a + (b - a) / 3.0, a + 2.0 * (b - a) / 3.0) if lo_ < v < hi_]
        pts = np.unique(np.array(inner, float))
        q += [(k, pa, pb) for pa, pb in zip(pts[:-1], pts[1:])]
    if mode in ("p", "g"):
        aa = np.array([p_[1] for p_ in q]); bb = np.array([p_[2] for p_ in q])
        xs = (0.5 * (bb - aa)[:, None] * _GL_X[None, :] + 0.5 * (aa + bb)[:, None]).ravel()
    else:
        xs = np.array(sorted({v for k, a, b in segs for v in (a + (b - a) / 3.0, a + 2.0 * (b - a) / 3.0)}))
    spec, chk = pepauli_spectrum(res, pre, inp, ctx["options"], ctx["params"], ctx["states"], c, xs)
    out["pp_chk"] = chk
    if not np.isfinite(chk) or chk > 1.0e-9:
        out["pp_fallback"] = "selfcheck"
        return out
    fy = spec[t]
    if mode == "q":
        qmap = dict(zip(np.round(xs, 13).tolist(), fy.tolist()))
    corr_lev = np.zeros(len(sh))
    corr_union = 0.0
    for j, (k, pa, pb) in enumerate(q):
        a, b = float(x[k]), float(x[k + 1])
        lin = lambda e: y[k] + (y[k + 1] - y[k]) * (e - a) / (b - a)  # noqa: E731
        i_lin = 0.5 * (lin(pa) + lin(pb)) * (pb - pa)
        if mode in ("p", "g"):
            i_new = float(0.5 * (pb - pa) * (fy[j * len(_GL_X):(j + 1) * len(_GL_X)] @ _GL_W))
        else:
            nx = [a, a + (b - a) / 3.0, a + 2.0 * (b - a) / 3.0, b]
            ny = [y[k], qmap[round(nx[1], 13)], qmap[round(nx[2], 13)], y[k + 1]]
            i_new = 0.5 * (np.interp(pa, nx, ny) + np.interp(pb, nx, ny)) * (pb - pa)
        d = i_new - i_lin
        mid = 0.5 * (pa + pb)
        for m, (l_, u_) in enumerate(zip(win["lo"], win["up"])):
            if l_ <= mid < u_:
                corr_lev[m] += d
                break
        if elast <= mid < u1:
            corr_union += d
        book.append(dict(k=int(k), a=a, b=b, ya=float(y[k]), yb=float(y[k + 1]), lo=float(pa), hi=float(pb),
                         lin=float(i_lin), new=float(i_new)))
    out["sh"] = [float(v + dv) for v, dv in zip(sh, corr_lev)]
    out["union"] = union + corr_union
    out["pp_onsets_in"] = int(sum(1 for k, a, b in segs for v in cuts_on if a < v < b))
    return out


def pecollapse(res: dict, pre: dict, inp: PreeqInputs, disc: DiscreteInputs, mode: str) -> dict:
    """PECOLLAPSE: flux-conserving collapse of the pre-equilibrium continuum onto the discrete states.

    TALYS (preeqcorrect.f90:96-133) zeroes every outgoing-energy bin above the last discrete level and gives level i
    ``0.5 * [xspreeq(n1) + xspreeq(n2)] * (esd2 - esd1)``, a two-point sample at the `locate`d nodes of its window,
    and the last level NL ``xspreeq(nendisc) * Rboundary`` (mb/MeV times a fraction). The sum is not the flux it
    removed; the difference goes to the compound nucleus. Here, for every ejectile type except the incident one:

    * the removed flux Z = book(un-zeroed spectrum, bins ebegin..eend) - book(continuum after the cut), both in
      `preeq_total`'s own arithmetic (sum_p xsstep + ps + ki + bu, times deltaE, less the last bin's `frac`);
    * level i's share is the exact integral of the linearly interpolated un-zeroed spectrum over its window, the
      windows tiling [Elast, Etop(eend)] (level 0's window closes at the top of the last emission bin, NL's at the
      last discrete level, the continuum boundary); xs1_i = Z * share_i / sum(shares), so sum_i xs1_i = Z exactly;
    * ``c2``: the last discrete bin nendisc is NOT also scaled by (1 - Rboundary) in xspreeq/ps/ki/bu/xsstep/xsstep2
      (TALYS removes its [Elast, Etop] part twice: the scaling, then `preeq_total`'s ``- xs * frac``), so the
      continuum keeps exactly the part of that bin below Elast and the spectra the exciton populations interpolate
      (population.f90) keep their true density at that node.

    Type k0 (xs1 = xseps, its zeroed flux returns to the compound nucleus) and levels with a direct cross section
    are untouched. Continuum spectra are untouched under ``c``.

    Test: tests/hf/test_pecollapse.py

    TALYS: (none -- Incognita extension, not a TALYS routine)
    """
    out = {k: res[k].detach().clone() for k in _PC_KEYS if k in res}
    a = {k: v.numpy() for k, v in out.items()}
    p = {k: pre[k].detach().cpu().numpy() for k in _PC_KEYS if k in pre}
    xd = res["xspreeqdisc"].detach().clone().numpy()
    C, E = inp.C, inp.E
    k0 = inp.k0
    diag = os.environ.get("INCOGNITA_PECOLLAPSE_DIAG", "") == "1"
    egall = inp.egrid_mev.detach().cpu().numpy().astype(float)
    deall = np.asarray(inp.deltae_mev.detach().cpu().numpy() if torch.is_tensor(inp.deltae_mev) else inp.deltae_mev, float)
    etopall = disc.etop_mev.detach().cpu().numpy().astype(float)
    for c in range(C):
        eg, de, etop = egall[c], deall[c], etopall[c]
        for t in range(7):
            if t == k0:
                continue
            b, e_end = disc.ebegin[t], disc.eend[c][t]
            esd_all = disc.eoutdis_mev[c][t]
            if b >= e_end or esd_all is None:
                continue
            nd, NL = disc.nendisc[c][t], disc.nlast[t]
            hi = min(e_end, E - 1)
            esd_l = [float(v) for v in esd_all[:NL + 2]]
            lev = []
            for i in range(NL + 1):  # TALYS's level loop (preeqcorrect.f90:52-57)
                if disc.xsdirdisc_mb[c][t][i] != 0.0:
                    continue
                if esd_l[i] < 0.0:
                    break
                lev.append(i)
            if not lev:
                continue
            nl_done = lev[-1] == NL
            elast = esd_l[NL] if esd_l[NL] > 0.0 else 0.0
            frac = float(etop[nd]) - elast if elast > 0.0 else 0.0
            if mode == "c2" and nl_done:  # undo the (1 - Rboundary) scaling of bin nd: removed once, by `frac`
                for k in ("xspreeq", "xspreeqps", "xspreeqki", "xspreeqbu"):
                    a[k][c, t, nd] = p[k][c, t, nd]
                a["xsstep"][c, t, 1:, nd] = p["xsstep"][c, t, 1:, nd]
                if "xsstep2" in a:
                    a["xsstep2"][c, :, t, nd] = p["xsstep2"][c, :, t, nd]
            f_before = _pe_book(p, c, t, b, hi, de, None, 0.0)
            f_after = _pe_book(a, c, t, b, hi, de, nd, frac)
            Z = f_before - f_after
            # windows: TALYS's mid-points, level 0 closed at the top of the last emission bin, NL at Elast
            ztop = float(etop[hi])
            zlo = elast if nl_done else float(etop[nd])
            lo, up = [], []
            for i in lev:
                u = ztop if i == 0 else 0.5 * (esd_l[i] + esd_l[i - 1])
                if i == NL:
                    l_ = elast
                elif esd_l[i + 1] > 0.0:
                    l_ = 0.5 * (esd_l[i] + esd_l[i + 1])
                else:
                    l_ = 0.0
                lo.append(min(max(l_, zlo), ztop))
                up.append(min(max(u, zlo), ztop))
            x = eg[b:hi + 2] if hi + 1 < len(eg) else eg[b:hi + 1]
            y = p["xspreeq"][c, t, b:b + len(x)].astype(float)
            if len(x) >= 2 and x[-1] < ztop:
                x, y = np.append(x, ztop), np.append(y, np.interp(ztop, x, y))
            if len(x) >= 2:
                sh = _cumlin(x, y, np.array(up)) - _cumlin(x, y, np.array(lo))
            else:
                sh = np.zeros(len(lev))
            old = xd[c, t, lev].copy()
            ssum = float(sh.sum())
            if mode == "n":  # diagnostics of TALYS's own collapse only (nothing written)
                pass
            elif ssum > 0.0:
                xd[c, t, lev] = Z * sh / ssum
            elif float(old.sum()) > 0.0:
                xd[c, t, lev] = Z * old / float(old.sum())
            if diag:
                PCDIAG.append(dict(c=c, einc=float(inp.einc_mev[c]), Z_t=inp.Z, A_t=inp.A, t=t, mode=mode, nd=int(nd), NL=int(NL), nlev=len(lev), nl_done=bool(nl_done),
                                   elast=elast, ztop=ztop, f_before=f_before, f_after=f_after, Z=Z, talys_disc=float(old.sum()),
                                   new_disc=float(xd[c, t, lev].sum()), win_lin=ssum, lev=list(map(int, lev)),
                                   talys_lev=old.tolist(), new_lev=xd[c, t, lev].tolist(), lin_lev=sh.tolist(),
                                   cont_before=_pe_book(p, c, t, b, nd, de, nd, frac), cont_full=_pe_book(p, c, t, b, nd, de, None, 0.0),
                                   b=int(b), e_end=int(e_end), hi=int(hi), E=int(E), x=x.tolist(), y=y.tolist(), lo=lo, up=up,
                                   xs_nd=float(p['xspreeq'][c, t, nd]), xs_after_nd=float(a['xspreeq'][c, t, nd])))
    if mode == "n":
        return {}
    for k in out:
        out[k] = torch.from_numpy(a[k]).to(res[k].dtype)
    xdt = torch.from_numpy(xd).to(res["xspreeqdisc"].dtype)
    out["xspreeqdisc"] = xdt
    out["xspreeqdisctot"] = xdt.sum(-1)
    out["xspreeqdiscsum"] = xdt.sum((-1, -2))
    return out


PUDIAG: list = []  # PEUNITS: per (case, type) records when INCOGNITA_PEUNITS_DIAG=1 (output only, also under OFF)


def peunits_on(options) -> bool:
    """PEUNITS (Incognita extension, default OFF): `peunits y|n` keyword, else `INCOGNITA_PEUNITS` (y/1/on).

    Test: tests/hf/test_peunits.py

    TALYS: (none -- Incognita extension, not a TALYS routine)
    """
    if bool(getattr(options, "peunits", False)):
        return True
    return os.environ.get("INCOGNITA_PEUNITS", "n").strip().lower() in ("y", "yes", "1", "on", "true")


def peremove_mode(options) -> str:
    """PEREMOVE (Incognita extension, default OFF): `peremove n|1|2` keyword, else `INCOGNITA_PEREMOVE`. Needs `peunits y`.

    1 = the [Elast, Etop(nendisc)] piece of the last discrete bin is removed from the continuum once (preeq_total skips its
    second ``- xs * frac``); 2 = 1 + level NL gets TALYS's own two-point window sample (see `peunits`).
    Test: tests/hf/test_peremove.py

    TALYS: (none -- Incognita extension, not a TALYS routine)
    """
    v = str(getattr(options, "peremove", "n") or "n").strip().lower()
    if v in ("", "n", "0", "no", "off"):
        v = os.environ.get("INCOGNITA_PEREMOVE", "n").strip().lower() or "n"
    if v in ("n", "0", "no", "off"):
        return "n"
    if v not in ("1", "2"):
        raise ValueError(f"peremove must be n, 1 or 2, not {v!r}")
    return v


def pewindow_mode(options) -> str:
    """PEWINDOW (Incognita extension, default OFF): `pewindow n|a|l` keyword, else `INCOGNITA_PEWINDOW`. Needs `peunits y`, implies
    `peremove 1`, refuses `peremove 2` (and, through peunits, pecollapse c/c2 / pegammaramp).

    a = every level 1 <= i <= NL takes the exact integral of the piecewise-linear interpolant of the un-zeroed PE spectrum over its
    TALYS window; l = level NL only (levels 1..NL-1 keep TALYS's two-point sample). See `peunits`.
    PEPAULI: p = a + in each ENDPOINT segment of the window range (one grid node zero, its neighbour open) the exact spectrum
    (`pepauli_spectrum`) integrated piecewise between the analytic Pauli/pairing onsets (`pepauli_onsets`) instead of the
    linear ramp through the zero node; q = a + two exactly evaluated nodes at 1/3 and 2/3 of each endpoint segment.
    pewindow g: g = p + the ground state (level 0, TALYS window [mid(E0, E1), E0]) gets the same exact integral (p leaves it on
    TALYS's two-point floor-node sample, which alternates x4 with the 0.5 MeV grid phase).
    Test: tests/hf/test_pewindow.py, tests/hf/test_pepauli.py, tests/hf/test_pewindow_gs.py

    TALYS: (none -- Incognita extension, not a TALYS routine)
    """
    v = str(getattr(options, "pewindow", "n") or "n").strip().lower()
    if v in ("", "n", "0", "no", "off"):
        v = os.environ.get("INCOGNITA_PEWINDOW", "n").strip().lower() or "n"
    if v in ("n", "0", "no", "off"):
        return "n"
    if v not in ("a", "l", "p", "q", "g"):
        raise ValueError(f"pewindow must be n, a, l, p, q or g, not {v!r}")
    return v


PRDIAG: list = []  # PEREMOVE: per (case, type) books when INCOGNITA_PEREMOVE_DIAG=1 (output only, also under OFF)


def peunits(res: dict, pre: dict, inp: PreeqInputs, disc: DiscreteInputs, on: bool, remove: str = "n", window: str = "n",
            ctx: dict | None = None) -> dict:
    """PEUNITS: the units of TALYS's pre-equilibrium cross section for the last discrete level NL.

    TALYS (preeqcorrect.f90:127-133) gives level NL ``xspreeq(nendisc) * Rboundary`` with
    Rboundary = (Etop(nendisc) - Elast) / deltaE(nendisc): a spectrum (mb/MeV) times a dimensionless fraction, i.e.
    1/deltaE(nendisc) times the flux of [Elast, Etop(nendisc)] that the (1 - Rboundary) scaling of bin nendisc removes
    from the continuum. Here level NL gets ``xspreeq(nendisc) * frac`` (mb), frac = Etop(nendisc) - Elast, the
    un-scaled spectrum of that bin (as TALYS uses it) times the same width `preeq_total` subtracts: exactly the flux
    the scaling removed. Nothing else changes: levels i < NL, level 0, the (1 - Rboundary) scaling, preeq_total's
    second removal (``- xs * frac``, a separate defect), type k0, levels with a direct cross section, the NL level when
    TALYS's level loop stops before it, and every cell with |Rboundary| > 1 (TALYS sets Rboundary = 0) or frac < 0.

    PEREMOVE (`remove`, needs `on`; default "n" = the above): in the same cells ("acts"), "1" also returns the (C, 7) mask
    `nofrac` so that `preeq_total` removes the [Elast, Etop(nendisc)] piece from the continuum once (the scaling), not twice;
    "2" = "1" + level NL gets TALYS's own two-point sample over its window [Elast, (E_NL + E_NL-1)/2] (the rule of every
    level i < NL, preeqcorrect.f90:96-122, on the un-scaled spectrum) instead of the sliver, which lies mostly inside the
    windows of levels NL-1, NL-2, ... that already receive that flux. INCOGNITA_PEREMOVE_DIAG=1 -> PRDIAG.

    PEWINDOW (`window`, needs `on` and remove "1"; default "n" = the above): in the same cells, level i takes the EXACT integral
    of the piecewise-linear interpolant (through the grid nodes, as `pecollapse` and the 4x G0 reference) of the un-zeroed,
    un-scaled spectrum over its TALYS window [esd1, esd2] (mid-points; NL's lower edge Elast), instead of the two-point sample
    0.5 [xs(n1) + xs(n2)] (esd2 - esd1) at the `locate`d floor nodes, which over-weights the node below a spectrum that falls to
    zero at the Pauli/pairing endpoint. "a": levels 1..NL; "l": NL only. Level 0, type k0, direct levels and every non-"acts"
    cell stay TALYS/PEUNITS. With remove "1" each [Elast, Etop(nendisc)] slice leaves the continuum once.

    Test: tests/hf/test_peunits.py, tests/hf/test_peremove.py, tests/hf/test_pewindow.py

    Test: tests/hf/test_peunits.py, tests/hf/test_peremove.py

    TALYS: (none -- Incognita extension, not a TALYS routine)
    """
    from physics.hf.core.grids import locate_scalar

    diag = os.environ.get("INCOGNITA_PEUNITS_DIAG", "") == "1"
    prdiag = os.environ.get("INCOGNITA_PEREMOVE_DIAG", "") == "1"
    if remove != "n" and not on:
        raise ValueError("peremove 1/2 is built on peunits y: set both")
    if window != "n" and (not on or remove != "1"):
        raise ValueError("pewindow a/l is built on peunits y + peremove 1")
    if not (on or diag or prdiag):
        return {}
    nofrac = np.zeros((inp.C, 7), dtype=bool)
    deg = np.asarray(inp.deltae_mev.detach().cpu().numpy() if torch.is_tensor(inp.deltae_mev) else inp.deltae_mev, float)
    xd = res["xspreeqdisc"].detach().clone().numpy()
    C, k0 = inp.C, inp.k0
    deall = np.asarray(inp.deltae_mev.detach().cpu().numpy() if torch.is_tensor(inp.deltae_mev) else inp.deltae_mev, float)
    etopall = disc.etop_mev.detach().cpu().numpy().astype(float)
    xpre = pre["xspreeq"].detach().cpu().numpy()
    xpost = res["xspreeq"].detach().cpu().numpy()
    for c in range(C):
        for t in range(7):
            b, e_end = disc.ebegin[t], disc.eend[c][t]
            esd_all = disc.eoutdis_mev[c][t]
            if b >= e_end or esd_all is None:
                continue
            nd, NL = disc.nendisc[c][t], disc.nlast[t]
            reached = True  # TALYS's level loop (preeqcorrect.f90:52-57) reaches NL unless a level energy is < 0
            for i in range(NL + 1):
                if disc.xsdirdisc_mb[c][t][i] == 0.0 and float(esd_all[i]) < 0.0:
                    reached = False
                    break
            direct = disc.xsdirdisc_mb[c][t][NL] != 0.0
            elast = float(esd_all[NL]) if reached else float("nan")
            frac = float(etopall[c][nd]) - elast
            de = float(deall[c][nd])
            rb = frac / de
            if t == k0:
                why = "k0"
            elif not reached:
                why = "unreached"
            elif direct:
                why = "direct"
            elif abs(rb) > 1.0:
                why = "rb>1"
            elif frac < 0.0:
                why = "frac<0"
            else:
                why = "acts"
            old = float(xd[c, t, NL]) if NL < xd.shape[2] else 0.0
            new = float(xpre[c, t, nd]) * frac if why == "acts" else old
            own = float("nan")
            if why == "acts":  # TALYS's own two-point window sample of NL (preeqcorrect.f90:96-122), un-scaled spectrum
                esd1 = elast
                esd2 = float(esd_all[0]) if NL == 0 else 0.5 * (elast + float(esd_all[NL - 1]))
                eg = inp.egrid_mev[c].detach().cpu().numpy()
                n1 = locate_scalar(eg, nd, e_end, esd1)
                n2 = locate_scalar(eg, nd, e_end, esd2)
                own = float(0.5 * (xpre[c, t, n1] + xpre[c, t, n2]) * (esd2 - esd1))
            arm = new
            lv_talys = [float(v) for v in xd[c, t, :NL + 1]]
            win = None
            if why == "acts" and (window != "n" or prdiag):  # PEWINDOW: exact window integrals (pecollapse's interpolant)
                E = xpre.shape[2]
                hi = min(e_end, E - 1)
                ztop = float(etopall[c][hi])
                egc = inp.egrid_mev[c].detach().cpu().numpy().astype(float)
                x = egc[b:hi + 2] if hi + 1 < len(egc) else egc[b:hi + 1]
                y = xpre[c, t, b:b + len(x)].astype(float)
                if len(x) >= 2 and x[-1] < ztop:
                    x, y = np.append(x, ztop), np.append(y, np.interp(ztop, x, y))
                lev, lo, up, dirw = [], [], [], []
                for i in range(1, NL + 1):
                    u_ = 0.5 * (float(esd_all[i]) + float(esd_all[i - 1]))
                    l_ = elast if i == NL else (0.5 * (float(esd_all[i]) + float(esd_all[i + 1])) if float(esd_all[i + 1]) > 0.0 else 0.0)
                    l_, u_ = min(max(l_, elast), ztop), min(max(u_, elast), ztop)
                    if disc.xsdirdisc_mb[c][t][i] != 0.0:
                        dirw.append((i, l_, u_))
                        continue
                    lev.append(i); lo.append(l_); up.append(u_)
                if len(x) >= 2 and lev:
                    sh = _cumlin(x, y, np.array(up)) - _cumlin(x, y, np.array(lo))
                    u1 = up[0] if lev[0] == 1 else 0.5 * (float(esd_all[1]) + float(esd_all[0]))
                    u1 = min(max(u1, elast), ztop)
                    union = float(_cumlin(x, y, np.array([u1]))[0] - _cumlin(x, y, np.array([elast]))[0])
                    dsum = float(sum(_cumlin(x, y, np.array([q]))[0] - _cumlin(x, y, np.array([p_]))[0] for _, p_, q in dirw))
                    if window == "g" and disc.xsdirdisc_mb[c][t][0] == 0.0 and float(esd_all[0]) > 0.0:
                        # pewindow g: the ground state's TALYS window [mid(E0, E1), E0] (preeqcorrect.f90:96-122, i = 0) takes the same
                        # exact integral as levels 1..NL; flux above the grid top (E0 > ztop) has no spectrum and is booked.
                        u0 = min(max(float(esd_all[0]), elast), ztop)
                        lev.append(0); lo.append(u1); up.append(u0)
                        sh = np.append(sh, _cumlin(x, y, np.array([u0]))[0] - _cumlin(x, y, np.array([u1]))[0])
                        utop, gs_over = u0, max(float(esd_all[0]) - ztop, 0.0)
                    else:
                        utop, gs_over = u1, 0.0
                else:
                    sh, union, dsum, utop, gs_over, u1 = np.zeros(len(lev)), 0.0, 0.0, 0.0, 0.0, 0.0
                win = dict(lev=lev, lo=lo, up=up, sh=[float(v) for v in sh], union=union, direct_win=dsum, ndirect=len(dirw),
                           utop=float(utop), gs_over=float(gs_over), gs_talys=float(xd[c, t, 0]))
                if window in ("p", "q", "g") and len(x) >= 2 and lev:
                    win.update(_pepauli_cell(res, pre, inp, ctx, c, t, x, y, egc, win, dirw, elast, u1, window))
            if on and why == "acts":
                if remove in ("1", "2"):
                    nofrac[c, t] = True
                if remove == "2":
                    arm = own
                xd[c, t, NL] = arm
                if window != "n" and win is not None:
                    for i, v in zip(win["lev"], win["sh"]):
                        if window in ("a", "p", "q", "g") or i == NL:
                            xd[c, t, i] = v
            if prdiag:
                top = min(e_end, xpre.shape[2] - 1)
                unz = float((xpre[c, t, b:top + 1] * deg[c][b:top + 1]).sum())  # un-zeroed spectrum over ebegin..eend
                f2 = 0.0 if (nofrac[c, t] or not elast > 0.0) else frac
                cont = float((xpost[c, t, b:nd + 1] * deg[c][b:nd + 1]).sum()) - float(xpost[c, t, nd]) * f2
                PRDIAG.append(dict(c=c, einc=float(inp.einc_mev[c]), Z_t=inp.Z, A_t=inp.A, t=t, nd=int(nd), NL=int(NL), why=why,
                                   on=bool(on), remove=remove, eend=int(e_end), etop_eend=float(etopall[c][min(e_end, len(etopall[c]) - 1)]),
                                   esd0=float(esd_all[0]), elast=elast, etop_nd=float(etopall[c][nd]), de_nd=de, frac=frac,
                                   rb=rb, xs_pre_nd=float(xpre[c, t, nd]), xs_post_nd=float(xpost[c, t, nd]),
                                   removed_scaling=(float(xpre[c, t, nd]) - float(xpost[c, t, nd])) * de,
                                   removed_twice=float(xpost[c, t, nd]) * frac if frac > 0.0 else 0.0,
                                   nofrac=bool(nofrac[c, t]), bin_nd_book=float(xpost[c, t, nd]) * (de - f2),
                                   nl_talys=old, nl_u=new, nl_own=own, nl_arm=float(xd[c, t, NL]) if NL < xd.shape[2] else 0.0,
                                   lv=[float(v) for v in xd[c, t, :NL + 1]], unzeroed=unz, cont_book=cont,
                                   removed_total=unz - cont, disc_sum=float(xd[c, t].sum()), window=window, lv_talys=lv_talys, win=win))
            if diag:
                PUDIAG.append(dict(c=c, einc=float(inp.einc_mev[c]), Z_t=inp.Z, A_t=inp.A, t=t, nd=int(nd), NL=int(NL), why=why,
                                   on=bool(on), elast=elast, etop_nd=float(etopall[c][nd]), de_nd=de, frac=frac, rb=rb,
                                   xs_pre_nd=float(xpre[c, t, nd]), xs_post_nd=float(xpost[c, t, nd]),
                                   removed_scaling=(float(xpre[c, t, nd]) - float(xpost[c, t, nd])) * de,
                                   removed_twice=float(xpost[c, t, nd]) * frac if frac > 0.0 else 0.0,
                                   nl_talys=old,
                                   nl_u=new, disc_sum=float(xd[c, t].sum())))
    if not on:
        return {}
    xdt = torch.from_numpy(xd).to(res["xspreeqdisc"].dtype)
    out = {"xspreeqdisc": xdt, "xspreeqdisctot": xdt.sum(-1), "xspreeqdiscsum": xdt.sum((-1, -2))}
    if remove != "n":
        out["_peremove_nofrac"] = nofrac
    return out


def preequilibrium(
    inp: PreeqInputs,
    options,
    params,
    disc: DiscreteInputs,
    *,
    coulbar_mev=None,
    xsreacinc_mb: Tensor | None = None,
    states: ExcitonStates | None = None,
) -> dict:
    """The whole of `preeq.f90` for a batch of cases: the two-component exciton model, the
    Kalbach complex-particle terms, the collapse onto discrete states, and the flux
    normalisation. Every quantity `preeq*.out` prints is in the result, all mb or mb/MeV.

    TALYS: preeq.f90:1 (preeq)
    Test: A-pe
    """
    from physics.hf.preeq.complex import complex_particle_spectra

    res = exciton_model(inp, options, params, states)
    if getattr(options, "flagpecomp", True) and coulbar_mev is not None:
        cx = complex_particle_spectra(
            inp,
            options,
            params,
            coulbar_mev=coulbar_mev,
            xsreacinc_mb=(xsreacinc_mb if xsreacinc_mb is not None else inp.xsflux_mb),
        )
    else:
        z = torch.zeros_like(res["xspreeq"])
        cx = {"xspreeqps": z, "xspreeqki": z.clone(), "xspreeqbu": z.clone()}
    res.update(cx)
    res["xspreeq"] = res["xspreeq"] + cx["xspreeqps"] + cx["xspreeqki"] + cx["xspreeqbu"]
    ramp = pegamma_ramp(options)
    spec0 = res["xspreeq"].clone() if ramp > 0.0 else None
    pcm = pecollapse_mode(options)  # PECOLLAPSE (default n = OFF = TALYS)
    if pcm != "n" and ramp > 0.0:
        raise ValueError("pecollapse c/c2 and pegammaramp both rebuild the photon collapse: use one")
    pcdiag = os.environ.get("INCOGNITA_PECOLLAPSE_DIAG", "") == "1"
    pun = peunits_on(options)  # PEUNITS (default OFF = TALYS)
    if pun and (pcm != "n" or ramp > 0.0):
        raise ValueError("peunits and pecollapse c/c2 / pegammaramp all rewrite the discrete PE collapse: use one")
    pudiag = os.environ.get("INCOGNITA_PEUNITS_DIAG", "") == "1"
    prm = peremove_mode(options)  # PEREMOVE (default n = OFF = TALYS/PEUNITS)
    if prm != "n" and not pun:
        raise ValueError("peremove 1/2 is built on peunits y: set both")
    pwm = pewindow_mode(options)  # PEWINDOW (default n = OFF = TALYS/PEUNITS/PEREMOVE)
    if pwm != "n":
        if not pun:
            raise ValueError("pewindow a/l is built on peunits y: set both")
        if prm == "2":
            raise ValueError("pewindow a/l and peremove 2 both rewrite level NL: use one")
        prm = "1"  # pewindow implies peremove 1
    pudiag = pudiag or os.environ.get("INCOGNITA_PEREMOVE_DIAG", "") == "1"
    pre = {k: res[k].detach().clone() for k in _PC_KEYS if k in res} if (pcm != "n" or pcdiag or pun or pudiag) else None
    res.update(preeq_correct(res, inp, disc, res["states"]))
    nofrac = None
    if pun or pudiag:
        res.update(peunits(res, pre, inp, disc, pun, prm, pwm,
                           ctx=dict(options=options, params=params, states=res["states"]) if pwm in ("p", "q", "g") else None))
        nofrac = res.pop("_peremove_nofrac", None)
    if ramp > 0.0:
        res.update(pegamma_collapse(res, spec0, inp, disc))
    if pcm != "n" or pcdiag:
        res.update(pecollapse(res, pre, inp, disc, pcm))
    res.update(preeq_total(res, inp, disc, ungate=ramp > 0.0, nofrac=nofrac))
    if pcdiag:
        PCDIAG.append(dict(post=True, mode=pcm, einc=inp.einc_mev.tolist(), Z_t=inp.Z, A_t=inp.A, preeqnorm=res["preeqnorm"].tolist(),
                           xspreeqtot=res["xspreeqtot"].tolist(), xspreeqdisctot=res["xspreeqdisctot"].tolist()))
    return res


def exciton_spectra(cases, grid, trans, options, params) -> dict[str, Tensor]:
    """Pre-equilibrium emission spectra [mb/MeV] per particle (exciton*.out matrix elements,
    preeq*.out spectra).

    Contract signature, kept so consumers can find it; the working entry points are
    `physics.hf.preeq.prepare.prepare` (which builds `PreeqInputs` and `DiscreteInputs` from
    structure, grids and the injected inverse cross sections) followed by `preequilibrium`.
    The `CaseBatch`/`Transmission` form lands with T5's `Transmission` adapter.

    TALYS: exciton.f90:1 (exciton), preeq.f90:1 (preeq)
    Test: A-pe
    """
    raise NotImplementedError(
        "T8: use physics.hf.preeq.prepare.prepare(...) + preequilibrium(...); the "
        "CaseBatch/Transmission signature lands with T5's Transmission adapter"
    )
