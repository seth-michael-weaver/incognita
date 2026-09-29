"""Direct inelastic scattering to collective levels (DWBA through ECIS) and giant resonances.

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

Task: T12 (physics/hf/CONTRACT.md §7). Acceptance test: A-mult (§6).

TALYS routines ported here (file:line of the subroutine/function statement):
    direct.f90:1 (direct)
    directecis.f90:1 (directecis)   -- the level selection and the deformation ECIS receives
    directread.f90:1 (directread)   -- the bookkeeping around the ECIS cross sections
    incidentread.f90:1 (incidentread) -- only :368-394, the coupled-channels discrete levels
    giant.f90:1 (giant)
    sumrules.f90:1 (sumrules)

What is ported and what is injected
-----------------------------------
TALYS gets every direct cross section from ECIS-06: `directecis.f90` writes one two-state
DWBA problem per collective level, `ecist` solves them all, and `directread.f90` reads the
answers back. The solver is T13's task (contract §7, 26,315 lines). Everything *around* it is
here:

* which levels get a DWBA calculation at this energy, and with which deformation
  (`directecis.f90:197-245`) -- this is what decides the rows of `directE*.out`;
* the strength, energy and width of the four giant resonances from the energy-weighted sum
  rules, minus the low-lying collective states (`sumrules.f90`);
* for a non-spherical target, which levels the *incident* coupled-channels run already
  covered, so their cross sections are not sought from the DWBA run and are not lost from the
  totals (`incidentread.f90:368-394`);
* the split of the ECIS cross sections into the discrete part (`xsdirdisctot`, which binary.f90
  adds to `xspop` level by level) and the collective-continuum part (`xscollconttot`)
  (`directread.f90:189-201`);
* the Gaussian smearing of the giant resonances and of the above-`NL` collective levels onto
  the emission grid (`giant.f90`), which is what feeds `binemission.f90:188` and
  `population.f90:164-198`.

The per-level DWBA cross sections themselves are an argument (`xs_level_mb`), taken from
`physics.hf.ecis.bridge` / the `directE*.out` dumps until T13 lands; the interface does not
change when it does.

A quirk worth naming, because it looks like a bug and is reproduced on purpose: `giant.f90:113`
builds `xsgrstate` from a weight that sums to one over the grid (so it is in mb per *bin*),
while `giant.f90:158` divides the collective-continuum weight by `deltaE` as well (mb/MeV), and
`giant.f90:174` adds the two into the same `xsgr`. TALYS's own spectra carry that mix.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np
import torch
from torch import Tensor

from physics.hf.core.constants import talys_constants
from physics.hf.core.tensors import DTYPE
from physics.hf.structure.levels import NUMLEV2

__all__ = [
    "CollectiveStructure",
    "GiantResonances",
    "DirectLevels",
    "DirectResult",
    "giant_resonance_parameters",
    "giant_resonance_parameters_of",
    "direct_levels",
    "coupled_levels",
    "giant_levels",
    "direct",
    "direct_inelastic",
    "giant_spectra",
    "collective_continuum",
    "WSCALE",
    "GR_LABELS",
]

# giant.f90:94 -- giant resonances are smeared with 0.42 of their Lorentzian width.
WSCALE = 0.42
# The four (l, i) pairs sumrules.f90 fills, in the order `do l = 0, 3 / do i = 1, 2` visits them
# (directread.f90:154-155), which is also the print order of directout.f90:212-215.
GR_LI: tuple[tuple[int, int], ...] = ((0, 1), (2, 1), (3, 1), (3, 2))
GR_LABELS: tuple[str, ...] = ("GMR", "GQR", "LEOR", "HEOR")


@dataclass(frozen=True)
class CollectiveStructure:
    """Discrete structure of the residual nucleus the direct channel populates.

    For an incident neutron this is `Zindex(0, 0, k0), Nindex(0, 0, k0)` = the target itself.
    Arrays are indexed by TALYS's level number 0..numlev2 and are prepared once (§4.2: discrete
    structure is not differentiated). `nlast` is `Nlast(Zix, Nix, 0)` = `nlev` (densitypar.f90:304).
    """

    Atarget: int
    nlast: int
    deftype: str  # 'B' (beta) or 'D' (deformation length)
    edis_mev: np.ndarray  # (numlev2+1,) edis
    jdis: np.ndarray  # (numlev2+1,) spin
    parlev: np.ndarray  # (numlev2+1,) +-1
    deform: np.ndarray  # (numlev2+1,) deform
    colltype: str = "S"  # 'S', 'V', 'R' or 'A' (deformpar.f90)
    cc_levels: np.ndarray = field(default_factory=lambda: np.zeros(0, np.int64))


@dataclass(frozen=True)
class GiantResonances:
    """`Egrcoll`, `Ggrcoll`, `betagr` for GMR/GQR/LEOR/HEOR, shape (4,), MeV and dimensionless."""

    e_mev: Tensor
    width_mev: Tensor
    beta: Tensor

    @property
    def labels(self) -> tuple[str, ...]:
        return GR_LABELS


@dataclass(frozen=True)
class DirectLevels:
    """The levels `directecis.f90` hands to ECIS at one incident energy, in file order.

    `index` is TALYS's level number, `discrete` is `index <= Nlast` (the split directread.f90
    uses), `vibbeta` is the deformation ECIS is given (T13 consumes it; `deform * vibfactor`).
    """

    index: np.ndarray  # (n,) int
    e_mev: np.ndarray  # (n,) edis
    eout_mev: np.ndarray  # (n,) eoutdis
    spin: np.ndarray  # (n,)
    parity: np.ndarray  # (n,) +-1
    deform: np.ndarray  # (n,)
    vibbeta: np.ndarray  # (n,)
    discrete: np.ndarray  # (n,) bool

    def __len__(self) -> int:
        return int(self.index.shape[0])


@dataclass(frozen=True)
class DirectResult:
    """Everything binary.f90 and binemission.f90 take from the direct/giant subsystem, in mb.

    Scalars are 0-d tensors so they stay differentiable. `xsdirdisc_mb` is indexed by level
    number 0..numlev2 (zero where TALYS did no DWBA); `xsgr_mb`, `xscollcont_mb` and
    `xsgrstate_mb` live on the emission grid (index = TALYS's `nen`); `xscollcontjp_mb` is
    (J, parity, nen) with parity ordered (-1, +1) as in contract §4.2.
    """

    xsdirdisc_mb: Tensor  # (numlev2+1,)
    xsdirdisctot_mb: Tensor  # scalar, binary.f90:214-216
    xscollconttot_mb: Tensor  # scalar, directread.f90:196
    xsgrcoll_mb: Tensor  # (4,)
    xsgrtot_mb: Tensor  # scalar, giant.f90:122/130 -- includes xscollconttot
    xsgrsum_mb: Tensor  # scalar, giant.f90:125/131 (equal to xsgrtot for a single ejectile)
    eoutgr_mev: Tensor  # (4,)
    xsgrstate_mb: Tensor  # (4, E)
    xscollcont_mb: Tensor  # (E,)
    xscollcontjp_mb: Tensor  # (Jmax+1, 2, E)
    xsgr_mb: Tensor  # (E,)
    levels: DirectLevels


def _t(x, device=None) -> Tensor:
    return torch.as_tensor(x, dtype=DTYPE, device=device)


def giant_resonance_parameters(
    struct: CollectiveStructure,
    params=None,
    device=None,
) -> GiantResonances:
    """Giant-resonance energy, width and deformation from the energy-weighted sum rules.

    The collective strength of the continuum is the sum rule minus what the low-lying collective
    states already carry: a J=0 level is subtracted from the monopole strength, J=2 from the
    quadrupole and J=3 from the low-energy octupole (sumrules.f90:80-91). When the target's
    deformation is a *length* the level's value is converted back to a beta with
    `1.24 A^(1/3)` -- with the TARGET's A, not the residual's. The high-energy octupole keeps
    the full 0.7 of the octupole sum rule and is the only one that is never clipped at zero.

    `params` supplies the twelve `GMRadjustE`/`...D` factors of input_preeqpar.f90:112-123
    (all 1 by default); the result is differentiable in them.

    TALYS: sumrules.f90:1 (sumrules)
    Test: A-mult (the `Exc. energy`, `Width` and `Deform. par.` columns of directE*.out)
    """
    c = talys_constants()
    A = _t(float(struct.Atarget), device)
    one3, two3 = _t(c["onethird"], device), _t(c["twothird"], device)

    def adj(name: str) -> Tensor:
        if params is None or name.lower() not in params:
            return _t(1.0, device)
        return params[name.lower()].to(dtype=DTYPE)

    a53 = A ** (-_t(5.0, device) / _t(3.0, device))
    sgmr = _t(23.0, device) * a53
    sgqr = _t(575.0, device) * a53
    sgor = _t(1208.0, device) * a53
    sleor = _t(0.3, device) * sgor
    sheor = _t(0.7, device) * sgor

    e = [
        adj("GMRadjustE") * (_t(18.7, device) - _t(0.025, device) * A),
        adj("GQRadjustE") * (_t(65.0, device) * A ** (-one3)),
        adj("LEORadjustE") * (_t(31.0, device) * A ** (-one3)),
        adj("HEORadjustE") * (_t(115.0, device) * A ** (-one3)),
    ]
    g = [
        adj("GMRadjustG") * _t(3.0, device),
        adj("GQRadjustG") * (_t(85.0, device) * A ** (-two3)),
        adj("LEORadjustG") * _t(5.0, device),
        adj("HEORadjustG") * (_t(9.3, device) - A / _t(48.0, device)),
    ]

    # sumrules.f90:80-91: subtract the low-lying collective states. Level 0 is excluded.
    dfm = _t(struct.deform[1 : NUMLEV2 + 1], device)
    edis = _t(struct.edis_mev[1 : NUMLEV2 + 1], device)
    jint = np.asarray(struct.jdis[1 : NUMLEV2 + 1]).astype(np.int64)
    if struct.deftype == "D":
        dfm = dfm / (_t(1.24, device) * A**one3)
    betasq = torch.where(
        _t(struct.deform[1 : NUMLEV2 + 1], device) != 0.0, dfm * dfm, _t(0.0, device)
    )
    take = lambda j: (betasq * edis * _t((jint == j).astype(np.float64), device)).sum()  # noqa: E731
    sgmr = sgmr - take(0)
    sgqr = sgqr - take(2)
    sleor = sleor - take(3)

    zero = _t(0.0, device)
    beta = [
        adj("GMRadjustD") * torch.sqrt(torch.clamp(sgmr, min=0.0) / e[0]),
        adj("GQRadjustD") * torch.sqrt(torch.clamp(sgqr, min=0.0) / e[1]),
        adj("LEORadjustD") * torch.sqrt(torch.clamp(sleor, min=0.0) / e[2]),
        adj("HEORadjustD") * torch.sqrt(sheor / e[3]),
    ]
    # `if (S > 0.)` (sumrules.f90:95-97): a non-positive sum rule leaves betagr at zero, which
    # switches the resonance off entirely in directecis/directread/giant.
    beta[0] = torch.where(sgmr > 0.0, beta[0], zero)
    beta[1] = torch.where(sgqr > 0.0, beta[1], zero)
    beta[2] = torch.where(sleor > 0.0, beta[2], zero)
    return GiantResonances(torch.stack(e), torch.stack(g), torch.stack(beta))


_GR_ADJUST = tuple(f"{g}adjust{x}".lower() for g in ("GMR", "GQR", "LEOR", "HEOR")
                   for x in ("E", "G", "D"))
_GR_LAST: list = []  # [struct, params, adjust values, GiantResonances]


def giant_resonance_parameters_of(
    struct: CollectiveStructure, params=None
) -> GiantResonances:
    """NATIVEX2: `giant_resonance_parameters(struct, params)`, remembered for the last structure.

    The chained direct stage asks for it twice at every incident energy of a target (the DWBA
    deck and `direct`) with the same `DirectCase.struct` and `params` objects. The memo holds
    one entry, matched on the identity of both objects and on the values of the twelve adjust
    factors it reads, so a new target (a new `struct`) or an edited factor recomputes. Autograd
    on, or no `params`: always recomputed (the result then carries the factors' graph).

    TALYS: sumrules.f90:1 (sumrules)
    Test: A-mult
    """
    if torch.is_grad_enabled() or params is None:
        return giant_resonance_parameters(struct, params)
    adj = tuple(tuple(params[n].reshape(-1).tolist()) if n in params else None
                for n in _GR_ADJUST)
    if _GR_LAST and _GR_LAST[0] is struct and _GR_LAST[1] is params and _GR_LAST[2] == adj:
        return _GR_LAST[3]
    gr = giant_resonance_parameters(struct, params)
    _GR_LAST[:] = [struct, params, adj, gr]
    return gr


def direct_levels(
    struct: CollectiveStructure,
    eninccm_mev: float,
    eoutdis_mev: np.ndarray,
    einc_mev: float,
    k0: int = 1,
    ltarget: int = 0,
) -> DirectLevels:
    """The collective levels ECIS is asked about at this incident energy, in TALYS's order.

    A level is included when it has a non-zero deformation, its outgoing energy is positive and
    the centre-of-mass energy clears it by more than `0.1 parA` MeV; the target's own level is
    skipped. `vibbeta` carries the `vibfactor` damping that stops the DWBA diverging above
    200 MeV (directecis.f90:196). The resulting list is exactly the rows `directread.f90:101-103`
    then fills, so its length and order are what a DWBA solver must return.

    TALYS: directecis.f90:1 (directecis)
    Test: A-mult (the `level` column of directE*.out)
    """
    c = talys_constants()
    para = float(c["parA"][k0])
    vibfactor = 1.0 - max((float(einc_mev) - 200.0) / 1600.0, 0.0)  # directecis.f90:196
    # NATIVEX2: the `do i = 0, numlev2` loop's four `cycle` tests as one numpy mask per level
    # (the same comparisons element by element; NaN fails each test the way it failed the loop's)
    i = np.arange(NUMLEV2 + 1)
    dfm = np.asarray(struct.deform)[: NUMLEV2 + 1]
    eout = np.asarray(eoutdis_mev)[: NUMLEV2 + 1]
    edis = np.asarray(struct.edis_mev)[: NUMLEV2 + 1]
    keep = ((i != ltarget)  # `i == Ltarget .and. type == k0`; direct only runs for type = k0
            & ~(dfm == 0.0) & ~(eout <= 0.0) & ~(float(eninccm_mev) <= edis + 0.1 * para))
    a = np.flatnonzero(keep).astype(np.int64)
    return DirectLevels(
        index=a,
        e_mev=struct.edis_mev[a],
        eout_mev=np.asarray(eoutdis_mev)[a],
        spin=struct.jdis[a],
        parity=struct.parlev[a].astype(np.int64),
        deform=struct.deform[a],
        vibbeta=struct.deform[a] * vibfactor,
        discrete=a <= struct.nlast,
    )


def giant_levels(gr: GiantResonances, eninccm_mev: float, k0: int = 1) -> np.ndarray:
    """Indices into `GR_LABELS` of the giant resonances ECIS is asked about at this energy.

    Same open-channel test as the discrete levels, on `Egrcoll` (directecis.f90:230-232 and
    directread.f90:156-158). A resonance with `betagr == 0` is never calculated.

    TALYS: directecis.f90:1 (directecis)
    Test: A-mult (the non-zero rows of the giant-resonance block of directE*.out)
    """
    c = talys_constants()
    para = float(c["parA"][k0])
    beta = gr.beta.detach().cpu().numpy()
    e = gr.e_mev.detach().cpu().numpy()
    return np.array(
        [k for k in range(4) if beta[k] != 0.0 and eninccm_mev > e[k] + 0.1 * para], np.int64
    )


def coupled_levels(deformation, flagspher: bool = False) -> np.ndarray:
    """Levels whose direct cross section comes from the *incident* coupled-channels ECIS run.

    For `colltype /= 'S'` (and without `spherical y`) TALYS couples the ground state and up to
    `ndef - 1` excited states in the incident calculation and reads their inelastic cross
    sections from `ecis.incin`, mapping ECIS's state number back with `indexcc`
    (incidentread.f90:381-385). Those levels carry `deform == 0`, so `directecis` skips them --
    which is why Ca-40's strongest inelastic level, the 3- at 3.74 MeV, never appears in the
    DWBA list and yet has 43 mb in `directE*.out`.

    TALYS: incidentread.f90:1 (incidentread)
    Test: A-mult (the `level` column of directE*.out for a 'V' or 'R' target)
    """
    if flagspher or getattr(deformation, "colltype", "S") == "S":
        return np.zeros(0, np.int64)
    idx = np.asarray(deformation.indexcc)
    n = min(int(getattr(deformation, "ndef", 0)), idx.shape[0] - 1)
    return np.array([int(idx[k]) for k in range(2, n + 1) if idx[k] != 0], np.int64)


def direct_inelastic(
    struct: CollectiveStructure,
    levels: DirectLevels,
    xs_level_mb: Tensor,
    xs_coupled_mb: Tensor | None = None,
) -> tuple[Tensor, Tensor, Tensor]:
    """Scatter the ECIS cross sections onto the level axis and split them at `Nlast`.

    Returns `(xsdirdisc, xsdirdisctot, xscollconttot)` in mb: the per-level array binary.f90:199
    adds to `xspop`, the discrete total binary.f90:214 adds to `xspopnuc`, and the part that
    lives above the last discrete level and is smeared into the continuum by `giant`. TALYS
    accumulates the split over `i = 0, numlev2` guarded by `deform /= 0`, which is the same set
    the DWBA was run for, so a level ECIS did not see contributes zero either way.

    `xs_level_mb` is the DWBA cross section per entry of `levels`, from `ecis.bridge` (or T13).
    `xs_coupled_mb` is the same for `struct.cc_levels`, from the incident coupled-channels run;
    incidentread.f90:386-390 splits it at `Nlast` the same way, so the two sources add.

    TALYS: directread.f90:1 (directread)
    Test: A-mult
    """
    xs = torch.as_tensor(xs_level_mb, dtype=DTYPE).reshape(-1)
    if xs.shape[0] != len(levels):
        raise ValueError(f"{xs.shape[0]} cross sections for {len(levels)} levels")
    out = torch.zeros(NUMLEV2 + 1, dtype=DTYPE, device=xs.device)
    zero = torch.zeros((), dtype=DTYPE, device=xs.device)
    idx = struct.cc_levels
    cc = (
        torch.as_tensor(xs_coupled_mb, dtype=DTYPE, device=xs.device).reshape(-1)
        if xs_coupled_mb is not None
        else torch.zeros(idx.shape[0], dtype=DTYPE, device=xs.device)
    )
    if cc.shape[0] != idx.shape[0]:
        raise ValueError(f"{cc.shape[0]} coupled cross sections for {idx.shape[0]} levels")
    if idx.shape[0]:
        out = out.index_put((torch.as_tensor(idx, device=xs.device),), cc)
    if len(levels):
        out = out.index_put((torch.as_tensor(levels.index, device=xs.device),), xs, accumulate=True)
    disc = torch.as_tensor(levels.discrete, device=xs.device)
    ccdisc = torch.as_tensor(idx <= struct.nlast, device=xs.device)
    # directread.f90:190-191 skips level 0 of the elastic channel; direct_levels already did.
    xsdirdisctot = ((xs * disc).sum() if len(levels) else zero) + (
        (cc * ccdisc).sum() if idx.shape[0] else zero
    )
    xscollconttot = ((xs * ~disc).sum() if len(levels) else zero) + (
        (cc * ~ccdisc).sum() if idx.shape[0] else zero
    )
    return out, xsdirdisctot, xscollconttot


def _gauss_weights(centre: Tensor, egrid: Tensor, width: Tensor, mask: Tensor) -> Tensor:
    """Normalised Gaussian weights on the emission grid, zero beyond 5 sigma.

    giant.f90:100-112: the Gaussian is evaluated with `fac1 = 1/(w sqrt(2 pi))` and then divided
    by its own sum over the open part of the grid, so `fac1` cancels; it is kept because a
    resonance whose whole 5-sigma window falls outside the grid must give `sumgauss == 0` and
    therefore no spectrum at all, not a uniform one.
    """
    sqrttwopi = math.sqrt(2.0 * math.pi)
    w = width.unsqueeze(-1)
    edist = (centre.unsqueeze(-1) - egrid).abs()
    inside = mask & (edist <= 5.0 * w)
    g = torch.where(inside, torch.exp(-(edist**2) / (2.0 * w**2)) / (w * sqrttwopi), 0.0)
    s = g.sum(-1, keepdim=True)
    return torch.where(s > 0.0, g / torch.where(s > 0.0, s, torch.ones_like(s)), 0.0)


def giant_spectra(
    gr: GiantResonances,
    xsgrcoll_mb: Tensor,
    eninccm_mev: float,
    egrid_mev: Tensor,
    grid_mask: Tensor,
) -> tuple[Tensor, Tensor, Tensor]:
    """Smear the four giant resonances onto the emission grid.

    Returns `(xsgrstate, xsgr_partial, eoutgr)`: the per-resonance spectrum (4, E), its sum over
    resonances (E,), and the emission energy of each resonance (4,). The width is `WSCALE` times
    the Lorentzian width, and the weights sum to one over the open grid, so `xsgrstate` sums back
    to `xsgrcoll` -- it is mb per bin, not mb/MeV (see the module docstring).

    `grid_mask` selects `ebegin(k0) .. eend(k0)`.

    TALYS: giant.f90:1 (giant)
    Test: A-mult (the `GMR`/`GQR`/`LEOR`/`HEOR` columns of the giant-resonance spectra block)
    """
    eg = torch.as_tensor(egrid_mev, dtype=DTYPE)
    xs = torch.as_tensor(xsgrcoll_mb, dtype=DTYPE).reshape(4)
    eoutgr = _t(eninccm_mev, eg.device) - gr.e_mev
    live = (gr.beta != 0.0).unsqueeze(-1)
    w = _gauss_weights(eoutgr, eg, gr.width_mev * WSCALE, grid_mask.unsqueeze(0) & live)
    xsgrstate = w * xs.unsqueeze(-1)
    return xsgrstate, xsgrstate.sum(0), eoutgr


def collective_continuum(
    struct: CollectiveStructure,
    xsdirdisc_mb: Tensor,
    eoutdis_mev: np.ndarray,
    eninccm_mev: float,
    egrid_mev: Tensor,
    deltae_mev: Tensor,
    grid_mask: Tensor,
    elwidth_mev: float = 0.5,
    numj: int = 30,
) -> tuple[Tensor, Tensor]:
    """Smear the collective levels above `Nlast` into the continuum.

    Returns `(xscollcont, xscollcontJP)`, shapes (E,) and (J, 2, E), in mb/MeV: each level above
    the last discrete one is spread over a Gaussian whose width shrinks with the outgoing energy
    as `elwidth (Eout/Ecm)^1.5` (giant.f90:143), and -- unlike the giant resonances -- the weight
    is divided by the bin width. The parity axis is ordered (-1, +1) (§4.2).

    TALYS: giant.f90:1 (giant)
    Test: A-mult (the `Collective` column of the giant-resonance spectra block)
    """
    eg = torch.as_tensor(egrid_mev, dtype=DTYPE)
    de = torch.as_tensor(deltae_mev, dtype=DTYPE)
    xsd = torch.as_tensor(xsdirdisc_mb, dtype=DTYPE)
    idx = [
        i
        for i in range(struct.nlast + 1, NUMLEV2 + 1)
        if struct.deform[i] != 0.0 and eoutdis_mev[i] > 0.0
    ]
    E = eg.shape[0]
    jmax = numj + 1
    cont = torch.zeros(E, dtype=DTYPE, device=eg.device)
    contjp = torch.zeros(jmax, 2, E, dtype=DTYPE, device=eg.device)
    if not idx:
        return cont, contjp
    a = np.asarray(idx, np.int64)
    eout = _t(np.asarray(eoutdis_mev)[a], eg.device)
    diswidth = _t(elwidth_mev, eg.device) * (eout / _t(eninccm_mev, eg.device)) ** 1.5
    w = _gauss_weights(eout, eg, diswidth, grid_mask.unsqueeze(0).expand(len(a), -1))
    safe_de = torch.where(de > 0.0, de, torch.ones_like(de))
    term = torch.where(de > 0.0, w / safe_de, 0.0) * xsd[a].unsqueeze(-1)
    cont = term.sum(0)
    jl = np.clip(struct.jdis[a].astype(np.int64), 0, numj)
    pl = (struct.parlev[a].astype(np.int64) > 0).astype(np.int64)
    flat = torch.as_tensor(jl * 2 + pl, device=eg.device)
    contjp = contjp.reshape(jmax * 2, E).index_add(0, flat, term).reshape(jmax, 2, E)
    return cont, contjp


def direct(
    struct: CollectiveStructure,
    gr: GiantResonances,
    levels: DirectLevels,
    xs_level_mb: Tensor,
    xsgrcoll_mb: Tensor,
    eoutdis_mev: np.ndarray,
    eninccm_mev: float,
    egrid_mev: Tensor,
    deltae_mev: Tensor,
    grid_mask: Tensor,
    xs_coupled_mb: Tensor | None = None,
    flaggiant: bool = True,
    elwidth_mev: float = 0.5,
    numj: int = 30,
) -> DirectResult:
    """`direct.f90`'s four calls, composed: read, smear, and total up.

    Everything a `DirectResult` holds is what `binary.f90:199-272`, `binemission.f90:188` and
    `population.f90:164-198` read out of the direct subsystem. `flaggiant` is
    `energy_flags(options, e)["flaggiant"]` -- false below the pre-equilibrium onset, where TALYS
    writes no giant-resonance block at all (energies.f90:194-203); the collective-continuum
    smearing lives inside `giant` too, so it is off there as well.

    TALYS: direct.f90:1 (direct)
    Test: A-mult
    """
    xsdirdisc, disctot, collconttot = direct_inelastic(struct, levels, xs_level_mb, xs_coupled_mb)
    eg = torch.as_tensor(egrid_mev, dtype=DTYPE)
    zero_e = torch.zeros_like(eg)
    if not flaggiant:
        z4 = torch.zeros(4, dtype=DTYPE, device=eg.device)
        return DirectResult(
            xsdirdisc_mb=xsdirdisc,
            xsdirdisctot_mb=disctot,
            xscollconttot_mb=collconttot,
            xsgrcoll_mb=z4,
            xsgrtot_mb=torch.zeros((), dtype=DTYPE, device=eg.device),
            xsgrsum_mb=torch.zeros((), dtype=DTYPE, device=eg.device),
            eoutgr_mev=z4.clone(),
            xsgrstate_mb=torch.zeros(4, eg.shape[0], dtype=DTYPE, device=eg.device),
            xscollcont_mb=zero_e,
            xscollcontjp_mb=torch.zeros(numj + 1, 2, eg.shape[0], dtype=DTYPE, device=eg.device),
            xsgr_mb=zero_e.clone(),
            levels=levels,
        )
    xsgrcoll = torch.as_tensor(xsgrcoll_mb, dtype=DTYPE).reshape(4)
    xsgrstate, xsgrpart, eoutgr = giant_spectra(gr, xsgrcoll, eninccm_mev, eg, grid_mask)
    cc, ccjp = collective_continuum(
        struct,
        xsdirdisc,
        eoutdis_mev,
        eninccm_mev,
        eg,
        deltae_mev,
        grid_mask,
        elwidth_mev,
        numj,
    )
    # giant.f90:122-131: xsgrtot is the resonances plus the collective continuum, and xsgrsum
    # follows it; binary.f90:258 adds the sum to xspopnuc, compnorm.f90:169 removes it from flux.
    xsgrtot = xsgrcoll.sum() + collconttot
    return DirectResult(
        xsdirdisc_mb=xsdirdisc,
        xsdirdisctot_mb=disctot,
        xscollconttot_mb=collconttot,
        xsgrcoll_mb=xsgrcoll,
        xsgrtot_mb=xsgrtot,
        xsgrsum_mb=xsgrtot,
        eoutgr_mev=eoutgr,
        xsgrstate_mb=xsgrstate,
        xscollcont_mb=cc,
        xscollcontjp_mb=ccjp,
        xsgr_mb=xsgrpart + cc,
        levels=levels,
    )
