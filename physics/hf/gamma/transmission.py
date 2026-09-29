"""Gamma transmission coefficients, photoabsorption cross sections and the theoretical average
radiative width with its optional normalisation of the E1 strength (tgamma.f90,
radwidtheory.f90, gammaxs.f90, quasideuteron.f90).

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

Task: T7 (physics/hf/CONTRACT.md §7). Acceptance test: A-psf (§6).

TALYS routines ported here (file:line of the subroutine/function statement):
    tgamma.f90:1 (tgamma)
    radwidtheory.f90:1 (radwidtheory)
    gammaxs.f90:1 (gammaxs)
    quasideuteron.f90:1 (quasideuteron)

Shape note (contract §5). TALYS keeps one gamma transmission per emission energy and
multipolarity, Tjl(0, nen, irad, l); the spin/parity selection happens in the compound
routines. `tgamma` returns exactly that, (E, 2, gammax + 1) with index 0 along l unused, and
`GammaTransmission` carries it. Spreading it over (bin, J, parity) is T9's job.

Normalisation. TALYS does NOT normalise the strength to the experimental <Gamma_gamma> by
default (`flaggnorm = .false.`, input_gammamodel.f90:72). `radwidtheory(..., flaggnorm=True)`
reproduces the keyword: it divides the E1 ftable by gamgamth/gamgam until they agree to 1e-4.

Injected (contract §5): level densities rho(Ex, J, parity) [MeV^-1] of the compound nucleus
(T6), its discrete levels and the target ground state (T2), D0theo/D1theo [eV] (T6).
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, replace
from typing import TYPE_CHECKING

import torch
from torch import Tensor

from physics.hf.core.tensors import DTYPE
from physics.hf.gamma.parameters import GammaParameters
from physics.hf.gamma.strength import TWOPI, fstrength_gp, kgr

if TYPE_CHECKING:
    from physics.hf.core.grids import ExcitationBins
    from physics.hf.density.models import LevelDensity
    from physics.hf.input.defaults import Options, Params

NUMLEV = 40  # A0_talys_mod.f90:43
NUMBINS = 20 * (6 - 1)  # A0_talys_mod.f90:66 with memorypar = 6
NUMEX = NUMLEV + NUMBINS  # A0_talys_mod.f90:67
NUMJ = 40  # A0_talys_mod.f90:68
PARSPIN_NEUTRON = 0.5  # parspin(1)


@dataclass(frozen=True)
class GammaTransmission:
    """Tjl(0, nen, irad, l) and the photoabsorption cross section xsreac(0, nen) [mb]."""

    e_mev: Tensor  # (E,)
    tjl: Tensor  # (E, 2, gammax + 1): [:, irad, l]
    sigma_abs_mb: Tensor  # (E,)


def quasideuteron(e_gamma_mev: Tensor, Ztarget: int, Atarget: int, levinger: float = 6.5) -> Tensor:
    """Quasi-deuteron photoabsorption [mb] (quasideuteron.f90). levinger default
    input_gammapar.f90 line 37.

    TALYS: quasideuteron.f90:1 (quasideuteron)
    Test: A-psf
    """
    e = torch.as_tensor(e_gamma_mev, dtype=DTYPE)
    above = e > 2.224
    es = torch.where(above, e, torch.full_like(e, 3.0))
    freedeut = torch.where(above, 61.2 / es**3 * (es - 2.224) ** 1.5, torch.zeros_like(e))
    ep = torch.where(e > 0.0, e, torch.ones_like(e))
    poly = 8.3714e-2 - 9.8343e-3 * ep + 4.1222e-4 * ep * ep - 3.4762e-6 * ep**3 + 9.3537e-9 * ep**4
    fpauli = torch.where(
        e <= 140.0,
        torch.where(e >= 20.0, poly, torch.exp(-73.3 / ep)),
        torch.exp(-24.2348 / ep),
    )
    Ntarget = Atarget - Ztarget
    return levinger * Ntarget * Ztarget / float(Atarget) * freedeut * fpauli


def gammaxs(
    gp: GammaParameters, e_gamma_mev: Tensor, e_inc_mev: float, Ztarget: int, Atarget: int
) -> tuple[Tensor, Tensor, Tensor]:
    """(xsgamma, xsgdr, xsqd) [mb] as gammaxs.f90: sum over irad, l of f/kgr(l)*Egamma, plus QD.

    TALYS: gammaxs.f90:1 (gammaxs)
    Test: A-psf
    """
    e = torch.as_tensor(e_gamma_mev, dtype=DTYPE)
    xsgdr = torch.zeros_like(e)
    for irad in (0, 1):
        for l in range(1, gp.gammax + 1):  # noqa: E741
            xsgdr = xsgdr + fstrength_gp(gp, e_inc_mev, e, irad, l, e_inc_mev) / kgr(l) * e
    xsqd = quasideuteron(e, Ztarget, Atarget)
    return xsgdr + xsqd, xsgdr, xsqd


def tgamma(
    gp: GammaParameters,
    e_grid_mev: Tensor,
    e_inc_mev: float,
    Ztarget: int,
    Atarget: int,
    gp_compound: GammaParameters | None = None,
) -> GammaTransmission:
    """Tjl(0, nen, irad, l) = 2 pi E^(2l+1) f(Einc, E) * xsgamma/xsgdr(compound, Einc)
    (tgamma.f90). `gp` is the emitting nucleus (Zcomp, Ncomp); the photoabsorption factor is
    always taken for the initial compound nucleus (0, 0), passed as `gp_compound` (defaults to
    `gp`).

    TALYS: tgamma.f90:1 (tgamma), gammaxs.f90:1 (gammaxs)
    Test: A-psf (T(E1), T(M1), T(E2), T(M2) columns of psf*)
    """
    g0 = gp_compound if gp_compound is not None else gp
    e = torch.as_tensor(e_grid_mev, dtype=DTYPE)
    einc_t = torch.as_tensor([e_inc_mev], dtype=DTYPE)
    xsg, xsgdr, _ = gammaxs(g0, einc_t, e_inc_mev, Ztarget, Atarget)
    factor = torch.where(
        xsgdr > 0.0,
        xsg / torch.where(xsgdr > 0.0, xsgdr, torch.ones_like(xsgdr)),
        torch.ones_like(xsgdr),
    )[0]
    tjl = torch.zeros((e.shape[0], 2, gp.gammax + 1), dtype=DTYPE)
    for l in range(1, gp.gammax + 1):  # noqa: E741
        for irad in (0, 1):
            f = fstrength_gp(gp, e_inc_mev, e, irad, l, e_inc_mev)
            tjl = tjl.index_put(
                (torch.arange(e.shape[0]), torch.tensor(irad), torch.tensor(l)),
                TWOPI * e ** (2 * l + 1) * f * factor,
            )
    xsreac, _, _ = gammaxs(gp, e, e_inc_mev, Ztarget, Atarget)
    return GammaTransmission(e_mev=e, tjl=tjl, sigma_abs_mb=xsreac)


@dataclass(frozen=True)
class RadiativeWidth:
    gamgamth0_ev: Tensor  # s-wave <Gamma_gamma>
    gamgamth1_ev: Tensor  # p-wave
    swaveth: Tensor  # s-wave sum before multiplying by D0 (TALYS prints it as 'S-wave strength')
    gp: GammaParameters  # parameters after the optional gnorm iteration


# Smallest tabulated <Gamma_gamma> in structure/resonances is 0.02 eV and the largest is 2.3 eV
# (2.3e-3 as the keV number TALYS stores), so this separates the two unit readings.
GAMGAM_MIN_EV = 5.0e-3


def radwidtheory(
    gp: GammaParameters,
    e_mev: float,
    Sn_mev: float,
    levels_e_mev: Tensor,
    levels_j: Tensor,
    levels_parity: Tensor,
    target_spin: float,
    target_parity: int,
    density: Callable[[Tensor, Tensor, int], Tensor],
    D0theo_ev: float | Tensor,
    D1theo_ev: float | Tensor = 0.0,
    *,
    nlast: int | None = None,
    flaggnorm: bool = False,
    gamgam_exp_ev: float = 0.0,
    rebuild: Callable[[GammaParameters], GammaParameters] | None = None,
) -> RadiativeWidth:
    """Theoretical <Gamma_gamma> [eV] for s- and p-wave neutron resonances (radwidtheory.f90).

    Sn_mev             S(Zcomp, Ncomp, 1): neutron separation energy of the compound nucleus
    levels_*           discrete levels 0..Nlast of the compound nucleus (edis, jdis, parlev)
    target_spin/parity ground state of the target (Zcomp, Ncomp + 1)
    density(ex, J, P)  rho [MeV^-1] for one parity P, batched over ex (X,) and J (J,),
                       returning (X, J) -- TALYS density(Zcomp, Ncomp, Ex, J, P, 0, ldmodel)
    flaggnorm          the `gnorm` keyword: rescale the E1 ftable until gamgamth == gamgam_exp
    gamgam_exp_ev      measured <Gamma_gamma> in PHYSICAL eV: `ResonanceData.gamgam_ev` or a
                       `gamgam` keyword, never `gamgam_talys`. TALYS-2.x normalises to the
                       .res keV number read as eV (resonancepar.f90:96), 1000x too small (C/E
                       Gamma_gamma 1546 for I-130); the port does not reproduce that, and
                       refuses a value below GAMGAM_MIN_EV, which only a keV number can be.
    rebuild            with flaggnorm, a function returning gamma parameters for a new ftable
                       (TALYS re-calls gammapar); defaults to replacing gp.ftable[1, 1]

    TALYS: radwidtheory.f90:1 (radwidtheory)
    Test: A-psf (theoretical Gamma_gamma header of psf*)
    """
    if flaggnorm and 0.0 < gamgam_exp_ev < GAMGAM_MIN_EV:
        raise ValueError(
            f"gamgam_exp_ev={gamgam_exp_ev:g} eV: a keV number (TALYS's resonance-table units), "
            f"not a width in eV; pass ResonanceData.gamgam_ev"
        )
    E = float(e_mev)
    Sn = float(Sn_mev) + E
    NL = int(levels_e_mev.shape[0] - 1 if nlast is None else nlast)
    edis = torch.as_tensor(levels_e_mev, dtype=DTYPE)
    jdis = torch.as_tensor(levels_j, dtype=DTYPE)
    pdis = torch.as_tensor(levels_parity)

    # excitation grid, radwidtheory.f90:74-89
    exgam = []
    continuum = True
    for nex in range(NL + 1):
        if float(edis[nex]) > Sn:
            continuum = False
            break
        exgam.append(edis[nex])
    ndis = len(exgam) - 1  # last discrete index used
    if continuum:
        nexgam = 10 * NUMEX
        dEx = (Sn - float(edis[NL])) / (nexgam - NL)
        ex_cont = float(edis[NL]) + torch.arange(1, nexgam - NL + 1, dtype=DTYPE) * dEx
    else:
        ex_cont = torch.zeros(0, dtype=DTYPE)
        dEx = 0.0

    def one_pass(g: GammaParameters) -> tuple[Tensor, Tensor, Tensor]:
        # precompute E^(2l+1) f(E) per (irad, l) on the discrete and the continuum gamma energies
        eg_dis = Sn - torch.stack(exgam) if exgam else torch.zeros(0, dtype=DTYPE)
        eg_con = Sn - ex_cont
        S_dis = {}
        S_con = {}
        for l in range(1, g.gammax + 1):  # noqa: E741
            for irad in (0, 1):
                S_dis[(irad, l)] = eg_dis ** (2 * l + 1) * fstrength_gp(g, E, eg_dis, irad, l)
                S_con[(irad, l)] = eg_con ** (2 * l + 1) * fstrength_gp(g, E, eg_con, irad, l)
        # continuum level densities integrated over each bin (the log-interpolated trapezoid)
        exmin = torch.clamp(ex_cont - 0.5 * dEx, min=0.0)
        explus = ex_cont + 0.5 * dEx
        dE1 = ex_cont - exmin
        dE2 = explus - ex_cont
        sums = []
        for ll in (0, 1):
            if ll == 0:
                tpar = target_parity
                J2b = int(abs(2.0 * (target_spin - PARSPIN_NEUTRON)))
                J2e = int(2.0 * (target_spin + PARSPIN_NEUTRON))
            else:
                tpar = -target_parity
                J2b = int(2.0 * (target_spin - 1.5))
                if J2b < 0:
                    J2b += 2
                if J2b < 0:
                    J2b += 2
                J2e = int(2.0 * (target_spin + 1.5))
            total = torch.zeros((), dtype=DTYPE)
            for J2 in range(J2b, J2e + 1, 2):
                # discrete final states, radwidtheory.f90:128-133 (rho = 1)
                for nexout in range(ndis + 1):
                    if float(eg_dis[nexout]) <= 0.0:
                        continue
                    Pprime = int(pdis[nexout])
                    Ir2 = int(2.0 * float(jdis[nexout]))
                    pardif = abs(tpar - Pprime) // 2
                    for l2 in range(max(abs(J2 - Ir2), 2), min(J2 + Ir2, 2 * g.gammax) + 1, 2):
                        l = l2 // 2  # noqa: E741
                        irad = 1 if pardif == l % 2 else 0
                        total = total + S_dis[(irad, l)][nexout]
                if ex_cont.shape[0] == 0:
                    continue
                pos = eg_con > 0.0
                Ir2s = list(range(J2 % 2, min(J2 + 2 * g.gammax, 2 * NUMJ) + 1, 2))
                rspin = torch.tensor([0.5 * i for i in Ir2s], dtype=DTYPE)
                for Pprime in (-1, 1):
                    rho1 = density(exmin, rspin, Pprime) * (1.0 + 1.0e-10)
                    rho2 = density(ex_cont, rspin, Pprime)
                    rho3 = density(explus, rspin, Pprime) * (1.0 + 1.0e-10)
                    r1, r2, r3 = torch.log(rho1), torch.log(rho2), torch.log(rho3)
                    use_log = (r2 != r1) & (r2 != r3)
                    d12 = torch.where(use_log, r1 - r2, torch.ones_like(r1))
                    d23 = torch.where(use_log, r2 - r3, torch.ones_like(r2))
                    rho = torch.where(
                        use_log,
                        (rho1 - rho2) / d12 * dE1.unsqueeze(-1)
                        + (rho2 - rho3) / d23 * dE2.unsqueeze(-1),
                        rho2 * (dE1 + dE2).unsqueeze(-1),
                    )  # (X, J)
                    pardif = abs(tpar - Pprime) // 2
                    for k, Ir2 in enumerate(Ir2s):
                        for l2 in range(max(abs(J2 - Ir2), 2), min(J2 + Ir2, 2 * g.gammax) + 1, 2):
                            l = l2 // 2  # noqa: E741
                            irad = 1 if pardif == l % 2 else 0
                            total = (
                                total
                                + torch.where(
                                    pos, rho[:, k] * S_con[(irad, l)], torch.zeros_like(eg_con)
                                ).sum()
                            )
            sums.append(total)
        return sums[0], sums[1], sums[0]

    g = gp
    for _niter in range(101):  # radwidtheory.f90:98 `do Niter = 0, 100`
        s0, s1, sw = one_pass(g)
        gg0 = s0 * torch.as_tensor(D0theo_ev, dtype=DTYPE)
        gg1 = s1 * torch.as_tensor(D1theo_ev, dtype=DTYPE)
        if flaggnorm and gamgam_exp_ev > 0.0:
            factor = gg0 / gamgam_exp_ev
            if abs(float(factor) - 1.0) >= 0.0001:
                ft = g.ftable.clone()
                ft[1, 1] = ft[1, 1] / factor
                g = rebuild(replace(g, ftable=ft)) if rebuild else replace(g, ftable=ft)
                continue
        break
    return RadiativeWidth(gamgamth0_ev=gg0, gamgamth1_ev=gg1, swaveth=sw, gp=g)


def gamma_transmission(
    Zcomp: int,
    Ncomp: int,
    bins: ExcitationBins,
    rho: LevelDensity,
    gp: GammaParameters,
    options: Options,
    params: Params,
) -> Tensor:
    """Contract stub kept for the interface; TALYS computes T_gamma per emission energy (see
    `tgamma`) and applies no Gamma_gamma normalisation unless `gnorm` is set (`radwidtheory`).

    TALYS: tgamma.f90:1 (tgamma), radwidtheory.f90:1 (radwidtheory)
    Test: A-psf
    """
    raise NotImplementedError(
        "T7: use gamma.transmission.tgamma (per emission energy, as TALYS) and radwidtheory; "
        "the (bin, J, parity) spreading belongs to compound (T9)"
    )
