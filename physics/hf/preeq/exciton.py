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

from dataclasses import dataclass

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
        phdens2(*sh(-1, -1, 0, 0), gsp4, gsn4, u_g, ef, False, gsp_pauli=gsp4, gsn_pauli=gsn4)
        + phdens2(*sh(0, 0, -1, -1), gsp4, gsn4, u_g, ef, False, gsp_pauli=gsp4, gsn_pauli=gsn4)
    )
    phres2 = phdens2(*sh(), gsp4, gsn4, u_g, ef, False, gsp_pauli=gsp4, gsn_pauli=gsn4)
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
    drop = (n_s.reshape(1, S, 1) > 1) & (wsum == wemission2[:, :, 0, :])
    wemission2 = torch.cat(
        [
            torch.where(
                drop, torch.zeros_like(wemission2[:, :, 0, :]), wemission2[:, :, 0, :]
            ).unsqueeze(2),
            wemission2[:, :, 1:, :],
        ],
        dim=2,
    )
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


def _integrate_plus(states, m2, u, edepth, surfwell, gsp, gsn, nexcbins, kind):
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
        lam = tph * m2[m2key] * coll
        resid = phdens2(*_shift(states, *rshift), gsp, gsn, u - uu, edepth, surfwell)
        term = lam * gfac * dex * resid
        acc = torch.zeros_like(total)
        for i in range(nexcbins):
            acc = acc + term[i]
        total = total + acc
    phtot = phdens2(*_shift(states), gsp, gsn, u, edepth, surfwell)
    ok = phtot > 0
    return torch.where(
        ok, total / torch.where(ok, phtot, torch.ones_like(phtot)), torch.zeros_like(total)
    )


def _integrate_zero(states, m2, u, edepth, surfwell, gsp, gsn, nexcbins, kind):
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
    lam = tph * m2[m2key] * phdens2(*[ct(v) for v in dens_coll], gsp, gsn, uu, edepth, surfwell)
    term = lam * phdens2(*[ct(v) for v in dens_pair], gsp, gsn, uu, edepth, surfwell) * dex
    term = term * phdens2(*_shift(states, *rshift), gsp, gsn, u - uu, edepth, surfwell)
    for i in range(nexcbins):
        acc = acc + term[i]
    phtot = phdens2(*_shift(states), gsp, gsn, u, edepth, surfwell)
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

    # NATIVEX2: off the graph, all four rates in one C call (preeq.preeq_nx2)
    out = preeq_nx2.transition_rates(inp, states, emis, m2, nex, numeric,
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
            num = integrate(states, m2, u, edepth, surfwell, gsp, gsn, nex, kind)
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


def preeq_total(spectra: dict, inp: PreeqInputs, disc: DiscreteInputs) -> dict:
    """Integrate the spectra and apply TALYS's flux normalisation (preeqtotal.f90:44-129).

    `xssteptot(type, p)` and `xspreeqtot(type)` integrate over the grid up to `nendisc`, minus
    the fraction `Etop(nendisc) - Elast` of the last bin; if the total exceeds `xsflux`
    everything is scaled down by `xsflux / (xspreeqsum + xspreeqdiscsum)`.

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
    for c in range(C):
        de = inp.deltae_mev[c]
        for t in range(7):
            b, e_end = disc.ebegin[t], disc.eend[c][t]
            nd = disc.nendisc[c][t]
            esd_all = disc.eoutdis_mev[c][t]
            elast = float(esd_all[disc.nlast[t]]) if esd_all is not None else 0.0
            frac = float(disc.etop_mev[c][nd]) - elast if elast > 0.0 else 0.0
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
    if bool(only_gamma.any()):  # preeqtotal.f90:92-102
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
    res.update(preeq_correct(res, inp, disc, res["states"]))
    res.update(preeq_total(res, inp, disc))
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
