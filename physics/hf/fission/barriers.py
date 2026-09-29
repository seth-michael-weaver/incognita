"""Barrier penetrabilities: Hill-Wheeler, transition states on rotational bands, class-II
resonances, direct barrier transmission.

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

Task: T11 (physics/hf/CONTRACT.md §7). Acceptance test: A-fis (§6).

TALYS routines ported here (file:line of the subroutine/function statement):
    thill.f90:1 (thill)
    t1barrier.f90:1 (t1barrier)
    tdirbarrier.f90:1 (tdirbarrier)

`rotband` and `rotclass2` build the transition-state bands themselves and live with the rest
of `fissionpar` in :mod:`physics.hf.fission.parameters`.

Batching. TALYS calls `t1barrier` once per (J, parity); this port evaluates every spin and
both parities at once, so the continuum quadrature over the barrier level density is a single
``(segment, J, parity)`` contraction. The penetrability depends only on the effective energy,
so it stays a ``(segment,)`` vector shared by all spins. The parity axis is ordered
``(-1, +1)`` (contract §4.2).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import torch
from torch import Tensor

from physics.hf.core.constants import talys_constants
from physics.hf.core.tensors import DTYPE
from physics.hf.fission.wkb import twkbint, twkbphaseint

if TYPE_CHECKING:
    from physics.hf.fission.parameters import FissionParameters
    from physics.hf.fission.transmission import FissionLevelDensities

NUMHILL = 20  # A0_talys_mod.f90:77
NUMJ = 40  # A0_talys_mod.f90:68
_EPS = 1.0e-10  # t1barrier.f90:158-160


def thill(e_hw_mev: Tensor, b_hw_mev: Tensor, w_hw_mev: Tensor) -> Tensor:
    """Hill-Wheeler transmission through one barrier (thill.f90). Dimensionless.

    ``T = [1 + exp(-2 pi (E - B) / hw)]^-1``, and exactly zero where the exponent falls to -80
    or below.

    TALYS: thill.f90:1 (thill)
    Test: A-fis
    """
    twopi = talys_constants()["twopi"]
    expo = twopi * (e_hw_mev - b_hw_mev) / w_hw_mev
    safe = torch.clamp(expo, min=-80.0)
    return torch.where(expo > -80.0, 1.0 / (1.0 + torch.exp(-safe)), torch.zeros_like(expo))


@dataclass(frozen=True)
class BarrierTransmission:
    """One barrier's contribution at one excitation energy, over all (J, parity).

    `trfis` and `rhof` are `(maxj+1, 2)`. `tfisA`/`rhofisA` are the Hill-Wheeler magnitude
    histograms the width-fluctuation correction needs, `(maxj+1, 2, NUMHILL+1)`; TALYS fills
    them only for the inner barrier of the primary compound nucleus at the bin centre.
    """

    trfis: Tensor
    rhof: Tensor
    tfisA: Tensor | None = None
    rhofisA: Tensor | None = None


def barrier_height(fp: FissionParameters, ibar: int, deltaw_mev: Tensor) -> tuple[Tensor, Tensor]:
    """Effective barrier height and curvature of barrier `ibar` [MeV].

    For `fismodel >= 3`, and for a single-humped tabulated barrier, the liquid-drop height is
    corrected with the ground-state shell correction ``deltaW(0) - deltaW(1)``. `deltaw_mev` is
    T6's `LDNucleus.deltaW_mev`, indexed by barrier. `fisbaradjust`/`fishwadjust` multiply the
    height (before the shell correction) and the curvature (FISBARWIRE); TALYS applies them only
    when `fisadjust` is set, i.e. when a fission keyword was given, and they are 1 otherwise.
    The energy-dependent `adjust` factors of a keyword given with an energy range are not ported
    (they are 1 without one). Every live path -- this torch code, `fission_batch_ladder`, NATIVEX2's
    `fis2` C kernels and CENGFIS's `fission.c` -- takes its Hill-Wheeler height and curvature from
    here; under `fismodel >= 5` the WKB table is read instead and neither is used.

    TALYS: t1barrier.f90:99-121 (t1barrier)
    Test: A-fis
    """
    fbar = fp.fbarrier_mev[ibar]
    wfis = fp.fwidth_mev[ibar]
    if fp.fbaradjust is not None:
        fbar = fbar * fp.fbaradjust[ibar]
    if fp.fwidthadjust is not None:
        wfis = wfis * fp.fwidthadjust[ibar]
    if fp.fismodelx >= 3 or fp.nfisbar == 1:
        return fbar - (deltaw_mev[0] - deltaw_mev[1]), wfis
    return fbar, wfis


def _penetrability(fp: FissionParameters, eeff: Tensor, ibar: int, bfis: Tensor, wfis: Tensor):
    """`twkbint` for `fismodel >= 5`, Hill-Wheeler otherwise (t1barrier.f90:132-136, :170-174)."""
    if fp.fismodelx >= 5 and fp.wkb is not None:
        return twkbint(fp.wkb, eeff, ibar)
    return thill(eeff, bfis, wfis)


def _band_index(band, eex: Tensor, odd: int, maxj: int, dev):
    """(mask, flat (J,parity) index, transition energies) of a rotational band at `eex`."""
    etrans = band.e_mev[1 : band.n + 1].to(dev)
    j2 = torch.round(2.0 * band.spin[1 : band.n + 1].to(dev)).to(torch.int64)
    par = torch.as_tensor(band.parity[1 : band.n + 1], device=dev)
    jidx = (j2 - odd) // 2
    ok = (eex >= etrans) & (2 * jidx + odd == j2) & (jidx >= 0) & (jidx <= maxj)
    flat = jidx.clamp(0, maxj) * 2 + (par > 0).to(torch.int64)
    return ok, flat, etrans


def _log_integrate(rho1: Tensor, rho2: Tensor, rho3: Tensor, de1: Tensor, de2: Tensor) -> Tensor:
    """TALYS's logarithmic integration of the level density over one `eintfis` triple.

    ``(rho1-rho2)/ln(rho1/rho2) dE1 + (rho2-rho3)/ln(rho2/rho3) dE2``, falling back to the
    midpoint rectangle when either logarithm difference vanishes (t1barrier.f90:161-168).
    """
    r1, r2, r3 = torch.log(rho1), torch.log(rho2), torch.log(rho3)
    ok = (r2 != r1) & (r2 != r3)
    s12 = torch.where(ok, r1 - r2, torch.ones_like(r1))
    s23 = torch.where(ok, r2 - r3, torch.ones_like(r1))
    return torch.where(
        ok, (rho1 - rho2) / s12 * de1 + (rho2 - rho3) / s23 * de2, rho2 * (de1 + de2)
    )


def _segments(grid: FissionLevelDensities, ibar: int, eex: Tensor, dev):
    """The `do i = 1, nbintfis-2, 2` triples, clipped at `eex` (t1barrier.f90:151-157)."""
    nb = grid.nbintfis[ibar]
    idx = torch.arange(1, nb - 1, 2, device=dev)
    e = grid.eintfis_mev[ibar]
    elow = e[idx]
    emid = torch.minimum(e[idx + 1], eex)
    eup = torch.minimum(e[idx + 2], eex)
    return idx, elow, emid, (emid - elow), (eup - emid), (elow <= eex)


def t1barrier(
    fp: FissionParameters,
    grid: FissionLevelDensities,
    ibar: int,
    eex_mev: Tensor,
    deltaw_mev: Tensor,
    *,
    odd: int = 0,
    maxj: int = NUMJ,
    collect_hill: bool = False,
) -> BarrierTransmission:
    """Fission transmission coefficient through one barrier, for every (J, parity).

    Two contributions, exactly as TALYS: the discrete transition states of the rotational band
    on the barrier, each adding one penetrability at ``Eex - Etrans`` to its own (J, pi); and
    the continuum above `fecont`, a logarithmic integration of the barrier level density
    against the penetrability over the `eintfis` triples.

    With the TALYS defaults (`hbstate n`) the band is empty and only the continuum contributes.

    TALYS: t1barrier.f90:1 (t1barrier)
    Test: A-fis
    """
    dev = fp.fbarrier_mev.device
    eex = torch.as_tensor(eex_mev, dtype=DTYPE, device=dev)
    if dev.type == "cpu" and eex.ndim == 0:
        from physics.hf.fission.fis2_nx2 import t1

        got = t1(fp, grid, ibar, eex, deltaw_mev, maxj, collect_hill)  # NX2 fis2: C, no band
        if got is not None:
            return got
    bfis, wfis = barrier_height(fp, ibar, deltaw_mev)
    shape = (maxj + 1, 2)
    zeros = torch.zeros(shape, dtype=DTYPE, device=dev)
    trfis, rhof = zeros, zeros.clone()
    tfisA = torch.zeros((*shape, NUMHILL + 1), dtype=DTYPE, device=dev) if collect_hill else None
    rhofisA = torch.zeros_like(tfisA) if collect_hill else None

    band = fp.rotational[ibar]
    if band.n > 0:
        ok, flat, etrans = _band_index(band, eex, odd, maxj, dev)
        t1 = _penetrability(fp, eex - etrans, ibar, bfis, wfis) * ok.to(DTYPE)
        one = ok.to(DTYPE)
        trfis = trfis + zeros.view(-1).index_add(0, flat, t1).view(shape)
        rhof = rhof + zeros.view(-1).index_add(0, flat, one).view(shape)
        if collect_hill:
            ihill = torch.clamp((NUMHILL * t1).to(torch.int64) + 1, max=NUMHILL)
            lin = flat * (NUMHILL + 1) + ihill
            tfisA = tfisA.view(-1).index_add(0, lin, t1).view(*shape, NUMHILL + 1)
            rhofisA = rhofisA.view(-1).index_add(0, lin, one).view(*shape, NUMHILL + 1)
            tfisA[..., 0] = tfisA[..., 0] + zeros.view(-1).index_add(0, flat, t1).view(shape)

    if grid.nbintfis[ibar] >= 3 and bool(eex >= fp.fecont_mev[ibar]):
        idx, _elow, emid, de1, de2, keep = _segments(grid, ibar, eex, dev)
        r = grid.rhofis[ibar]
        rho = _log_integrate(
            r[idx] * (1.0 + _EPS) + _EPS,
            r[idx + 1] + _EPS,
            r[idx + 2] * (1.0 + _EPS) + _EPS,
            de1.view(-1, 1, 1),
            de2.view(-1, 1, 1),
        ) * keep.to(DTYPE).view(-1, 1, 1)
        t1 = _penetrability(fp, eex - emid, ibar, bfis, wfis)
        rhotr = rho * t1.view(-1, 1, 1)
        trfis = trfis + rhotr.sum(0)
        rhof = rhof + rho.sum(0)
        if collect_hill:
            ihill = torch.clamp((NUMHILL * t1).to(torch.int64) + 1, max=NUMHILL)
            tfisA = tfisA.index_add(2, ihill, rhotr.permute(1, 2, 0))
            rhofisA = rhofisA.index_add(2, ihill, rho.permute(1, 2, 0))
            tfisA[..., 0] = torch.clamp(tfisA[..., 0] + rhotr.sum(0), min=1.0e-30)
    return BarrierTransmission(trfis, rhof, tfisA, rhofisA)


def tdirbarrier(
    fp: FissionParameters,
    grid: FissionLevelDensities,
    ibar: int,
    ibar2: int,
    eex_mev: Tensor,
    deltaw_mev: Tensor,
    *,
    odd: int = 0,
    maxj: int = NUMJ,
) -> BarrierTransmission:
    """Direct (undamped) transmission through barriers `ibar` and `ibar2` together.

    Reached only with `fispartdamp y`, which the reference dumps do not exercise, so this
    branch is ported but ungated. Adjacent barriers couple as ``Ta Tb / (1 + (1-Ta)(1-Tb))``
    when the intervening well carries a non-zero phase integral and as ``Ta Tb`` otherwise;
    barriers two apart go through the middle one the same way. In the continuum, barriers two
    apart use the pointwise *minimum* of the two level densities (tdirbarrier.f90:152-155), and
    TALYS carries `rho` into the intermediate `trfisonetwo` as well as the outer product
    (tdirbarrier.f90:176-186) -- reproduced here as written.

    TALYS: tdirbarrier.f90:1 (tdirbarrier)
    Test: A-fis (ungated: `fispartdamp` is off by default)
    """
    dev = fp.fbarrier_mev.device
    eex = torch.as_tensor(eex_mev, dtype=DTYPE, device=dev)
    shape = (maxj + 1, 2)
    zeros = torch.zeros(shape, dtype=DTYPE, device=dev)
    trfis, rhof = zeros, zeros.clone()
    gap = abs(ibar - ibar2)
    ibar3 = (ibar + ibar2) // 2 if gap == 2 else ibar

    def pair(eeff: Tensor, base: Tensor) -> Tensor:
        """`base` scaled by the coupled two- or three-barrier transmission at `eeff`."""
        t1 = twkbint(fp.wkb, eeff, ibar)
        t2 = twkbint(fp.wkb, eeff, ibar2)
        p1 = twkbphaseint(fp.wkb, eeff, ibar)
        if gap == 1:
            return base * torch.where(p1 > 0, t1 * t2 / (1 + (1 - t1) * (1 - t2)), t1 * t2)
        t3 = twkbint(fp.wkb, eeff, ibar3)
        p3 = twkbphaseint(fp.wkb, eeff, ibar3)
        t12 = base * torch.where(p1 > 0, t1 * t3 / (1 + (1 - t1) * (1 - t3)), t1 * t3)
        return base * torch.where(p3 > 0, t12 * t2 / (1 + (1 - t12) * (1 - t2)), t12 * t2)

    band = fp.rotational[ibar3]
    if band.n > 0:
        ok, flat, etrans = _band_index(band, eex, odd, maxj, dev)
        val = pair(eex - etrans, torch.ones_like(etrans)) * ok.to(DTYPE)
        trfis = trfis + zeros.view(-1).index_add(0, flat, val).view(shape)
        rhof = rhof + zeros.view(-1).index_add(0, flat, ok.to(DTYPE)).view(shape)

    if grid.nbintfis[ibar3] >= 3 and bool(eex >= fp.fecont_mev[ibar3]):
        idx, _elow, emid, de1, de2, keep = _segments(grid, ibar3, eex, dev)
        if gap == 1:
            r = grid.rhofis[ibar3]
            rho1, rho2, rho3 = r[idx] * (1 + _EPS), r[idx + 1], r[idx + 2] * (1 + _EPS)
        else:
            ra, rb = grid.rhofis[ibar], grid.rhofis[ibar2]
            rho1 = torch.minimum(ra[idx], rb[idx]) * (1 + _EPS)
            rho2 = torch.minimum(ra[idx + 1], rb[idx + 1])
            rho3 = torch.minimum(ra[idx + 2], rb[idx + 2]) * (1 + _EPS)
        rho = _log_integrate(rho1, rho2, rho3, de1.view(-1, 1, 1), de2.view(-1, 1, 1))
        rho = rho * keep.to(DTYPE).view(-1, 1, 1)
        eeff = (eex - emid).view(-1, 1, 1).expand_as(rho)
        trfis = trfis + pair(eeff, rho).sum(0)
        rhof = rhof + rho.sum(0)
    return BarrierTransmission(trfis, rhof)


__all__ = [
    "NUMHILL",
    "BarrierTransmission",
    "barrier_height",
    "t1barrier",
    "tdirbarrier",
    "thill",
]
