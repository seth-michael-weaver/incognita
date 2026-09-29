"""Total fission transmission per compound state (tfission.f90).

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

Task: T11 (physics/hf/CONTRACT.md §7). Acceptance test: A-fis (§6).

TALYS routines ported here (file:line of the subroutine/function statement):
    tfission.f90:1 (tfission)
    densprepare.f90:1 (densprepare)

Only the fission block of `densprepare` (densprepare.f90:399-441) is ported here -- the rest
of that routine is T9's, which owns the interpolated `Tjlnex`/`Tlnex`/`Tgam`/`rho0`.

What this hands to the compound nucleus (contract §5). `tfission` is evaluated at three energies
per mother bin -- the bottom, the centre and the top -- because the fission transmission falls
so fast with excitation energy that `compound.f90` integrates it logarithmically across the bin.
`comptarget` uses the centre value alone, plus the Hill-Wheeler magnitude histogram `tfisA` when
width fluctuations are on. :class:`FissionTransmission` carries all of them, so
`physics.hf.compound.prepare` (`tfis`, `tfisA`, `rhofisA`) and `physics.hf.compound.continuum`
(`tfisdown`, `tfis`, `tfisup`) can both be fed from one object.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import torch
from torch import Tensor

from physics.hf.core.constants import talys_constants
from physics.hf.core.tensors import DTYPE
from physics.hf.density.models import density
from physics.hf.fission.barriers import NUMHILL, NUMJ, t1barrier, tdirbarrier
from physics.hf.fission.wkb import NUMBAR, twkbtransint

if TYPE_CHECKING:
    from physics.hf.density.models import LDNucleus
    from physics.hf.fission.parameters import FissionParameters
    from physics.hf.input.defaults import Options

NUMBINFIS = 1000  # A0_talys_mod.f90:75
DEXMIN = 0.01  # densprepare.f90:415
TRANSEPS = 1.0e-8  # input_numerics.f90:80


@dataclass(frozen=True)
class FissionLevelDensities:
    """The barrier level densities on the fission integration grid (`eintfis`, `rhofis`).

    `eintfis_mev[ibar]` is 1-based with `nbintfis[ibar]` points; odd indices are bin edges and
    even indices bin midpoints, which is what makes `t1barrier`'s ``i, i+1, i+2`` triples a
    Simpson-like pair of logarithmic integrals. `rhofis[ibar, i, J, parity]` is
    `density(Zcomp, Ncomp, eintfis, J, parity, ibar)` with the parity axis ordered `(-1, +1)`.
    """

    nbintfis: tuple[int, ...]
    eintfis_mev: Tensor  # (NUMBAR + 1, nmax + 1)
    rhofis: Tensor  # (NUMBAR + 1, nmax + 1, maxj + 1, 2)


@dataclass(frozen=True)
class FissionTransmission:
    """`Tfis` per (bin, J, parity) as the compound nucleus consumes it.

    All tensors have leading shape `(maxj+1, 2)` with the parity axis ordered `(-1, +1)`.
    `tfis` is the bin centre, `tfisdown`/`tfisup` the bin edges. `gamfis_mev` and `taufis_s`
    are the partial fission width and lifetime; TALYS labels the width column of `fis*.trans`
    `[eV]` but writes `tfis / (2 pi rho)` in MeV, and this port keeps the MeV value under a name
    that says so.
    """

    tfis: Tensor
    tfisdown: Tensor
    tfisup: Tensor
    tfisA: Tensor  # (maxj+1, 2, NUMHILL+1)
    rhofisA: Tensor
    denfis_per_mev: Tensor
    gamfis_mev: Tensor
    taufis_s: Tensor


def fission_level_densities(
    fp: FissionParameters,
    ld: LDNucleus,
    exfis_top_mev: float,
    *,
    odd: int = 0,
    maxj: int = NUMJ,
    device=None,
) -> FissionLevelDensities:
    """Build `eintfis`/`rhofis`: the barrier-level-density grid `t1barrier` integrates over.

    `exfis_top_mev` is `Exinc` for the primary compound nucleus and `Ex(maxex)` for every later
    one (densprepare.f90:408-412) -- TALYS builds the grid once per residual, at its top bin.
    The grid runs from `fecont(ibar)` to that energy in `numbinfis/2` bins, refined to at most
    10 keV, and stores the density at every edge and midpoint.

    TALYS: densprepare.f90:399-441 (densprepare)
    Test: A-fis
    """
    if device is None or torch.device(device).type == "cpu":
        from physics.hf.fission.fis2_nx2 import level_densities

        got = level_densities(fp, ld, float(exfis_top_mev), odd, maxj)  # NX2 fis2: numpy + C
        if got is not None:
            return got
    nb_out: list[int] = [0] * (NUMBAR + 1)
    grids: list[Tensor] = []
    rhos: list[Tensor] = []
    nmax = 1
    per_bar = []
    for ibar in range(NUMBAR + 1):
        if ibar == 0 or ibar > fp.nfisbar:
            per_bar.append(None)
            continue
        elowest = float(fp.fecont_mev[ibar])
        exfis = exfis_top_mev - elowest
        nbin = NUMBINFIS // 2
        if exfis <= 0.0:
            nb_out[ibar] = nbin
            per_bar.append(None)
            continue
        dex = exfis / nbin
        if dex < DEXMIN:
            nbin = max(int(exfis / DEXMIN), 1)
            dex = exfis / nbin
        edges = elowest + dex * torch.arange(nbin, dtype=DTYPE, device=device)
        e = torch.stack([edges, edges + 0.5 * dex], dim=1).reshape(-1)
        e = torch.cat([torch.zeros(1, dtype=DTYPE, device=device), e])
        e[2 * nbin] = exfis + elowest  # densprepare.f90:439
        nb_out[ibar] = 2 * nbin
        nmax = max(nmax, 2 * nbin)
        per_bar.append((ibar, e))

    jgrid = torch.arange(maxj + 1, dtype=DTYPE, device=device) + 0.5 * odd
    for ibar in range(NUMBAR + 1):
        item = per_bar[ibar]
        if item is None:
            grids.append(torch.zeros(nmax + 1, dtype=DTYPE, device=device))
            rhos.append(torch.zeros(nmax + 1, maxj + 1, 2, dtype=DTYPE, device=device))
            continue
        _, e = item
        n = nb_out[ibar]
        pad = torch.zeros(nmax + 1 - e.shape[0], dtype=DTYPE, device=device)
        grids.append(torch.cat([e, pad]))
        # rhofis is filled at the 2*nbin edge/midpoint pairs; index 2*nbin keeps the density of
        # the last midpoint even though its energy is moved to the top of the range.
        ee = e[1 : n + 1].reshape(-1, 1)
        from physics.hf.density.ld2_nx2 import fission_rhofis

        r = fission_rhofis(ld, ibar, ee, jgrid)  # NX2 ld2: both parities of a table in one C call
        if r is None:
            cols = [density(ld, ee, jgrid.reshape(1, -1), p, ibar) for p in (-1, 1)]
            r = torch.stack(cols, dim=-1)
        r = torch.cat([torch.zeros(1, maxj + 1, 2, dtype=DTYPE, device=device), r], dim=0)
        rhos.append(torch.cat([r, torch.zeros(nmax + 1 - r.shape[0], maxj + 1, 2, dtype=DTYPE, device=device)]))
    return FissionLevelDensities(tuple(nb_out), torch.stack(grids), torch.stack(rhos))


def _class2_boost(
    fp: FissionParameters,
    well: int,
    eex: Tensor,
    tf: Tensor,
    tsum: Tensor,
    odd: int,
    maxj: int,
) -> Tensor:
    """The class-II resonance enhancement of `tf` below `Emaxclass2 + widthc2/2`.

    Each class-II rotational state of matching (J, pi) adds a Lorentzian of half width
    ``0.5 widthc2`` damped towards the top of the band, normalised so that a state exactly on
    resonance lifts the transmission to ``4 / tsum``. Returns the replacement for `tf`, or `tf`
    itself when no state contributes.

    TALYS: tfission.f90:160-190 (tfission)
    Test: A-fis (ungated: `class2` is off by default)
    """
    dev = tf.device
    band = fp.class2rot[well]
    if band.n == 0:
        return tf
    e1 = band.e_mev[1]
    en = band.e_mev[band.n]
    term1 = -eex + 0.5 * (e1 + en)
    term2 = en - e1
    damper = torch.ones((), dtype=DTYPE, device=dev)
    if float(term2) > 0.0:
        expo = 24.0 * term1 / term2
        if abs(float(expo)) <= 80.0:
            damper = 1.0 / (1.0 + torch.exp(expo))
    wo2damp = 0.5 * fp.widthc2_mev[well] * damper

    ec2 = band.e_mev[1 : band.n + 1]
    boost = 1.0 / (1.0 + (torch.abs(eex - ec2) / wo2damp) ** 2)
    j2 = torch.round(2.0 * band.spin[1 : band.n + 1]).to(torch.int64)
    par = torch.as_tensor(band.parity[1 : band.n + 1], device=dev)
    jidx = (j2 - odd) // 2
    ok = (boost >= 0.25) & (2 * jidx + odd == j2) & (jidx >= 0) & (jidx <= maxj)
    flat = jidx.clamp(0, maxj) * 2 + (par > 0).to(torch.int64)
    weight = torch.zeros((maxj + 1) * 2, dtype=DTYPE, device=dev)
    weight = weight.index_add(0, flat, torch.where(ok, boost, torch.zeros_like(boost)))
    weight = weight.view(maxj + 1, 2)
    tfii = tf * (4.0 / tsum) * weight
    return torch.where(tfii > 0.0, tfii, tf)


def fission_transmission(
    fp: FissionParameters,
    grid: FissionLevelDensities,
    ld: LDNucleus,
    exinc_mev: float,
    dexinc_mev: float,
    options: Options,
    *,
    exmax_mev: float | None = None,
    odd: int = 0,
    maxj: int = NUMJ,
    primary: bool = True,
    fnorm: float = 1.0,
) -> FissionTransmission:
    """Tfis per (bin, J, parity) [dimensionless] (tfission.f90).

    Evaluated at ``Exinc - dEx/2``, ``Exinc`` and ``Exinc + dEx/2`` (clipped to `[0, Exmax]`),
    which is what lets `compound.f90` integrate the transmission logarithmically over the mother
    bin. One, two and three humped barriers combine as `Ta`, ``Ta Tb / (Ta + Tb)`` and
    ``T12 Tc / (T12 + Tc)`` respectively, with the class-II enhancement applied in between when
    `class2 y`, and with the `fispartdamp` damping when that flag is on.

    `fnorm` is TALYS's `Fnorm(-1)`, which is 1 for every default run (`fiso(-1)` is never
    changed by `isotrans`); it is an argument so the `tjadjust`/`fiso` keywords can reach it.

    TALYS: tfission.f90:1 (tfission)
    Test: A-fis
    """
    dev = fp.fbarrier_mev.device
    c = talys_constants()
    shape = (maxj + 1, 2)
    exmax = exinc_mev if exmax_mev is None else exmax_mev
    deltaw = ld.deltaW_mev
    out: list[Tensor] = []
    tfisA = torch.zeros((*shape, NUMHILL + 1), dtype=DTYPE, device=dev)
    rhofisA = torch.ones((*shape, NUMHILL + 1), dtype=DTYPE, device=dev)  # tfission.f90:147

    for iloop in (1, 2, 3):
        if iloop == 1:
            eex = max(exinc_mev - 0.5 * dexinc_mev, 0.0)
        elif iloop == 2:
            eex = exinc_mev
        else:
            eex = min(exinc_mev + 0.5 * dexinc_mev, exmax)
        e = torch.as_tensor(eex, dtype=DTYPE, device=dev)
        collect = primary and iloop == 2
        tf = torch.zeros(shape, dtype=DTYPE, device=dev)

        b1 = t1barrier(fp, grid, 1, e, deltaw, odd=odd, maxj=maxj, collect_hill=collect)
        if collect and b1.tfisA is not None:
            tfisA = tfisA + b1.tfisA
            rhofisA = rhofisA + b1.rhofisA
        tfb1 = b1.trfis

        if fp.nfisbar == 1:
            tf = tfb1
        elif fp.nfisbar == 2:
            tdir = (
                tdirbarrier(fp, grid, 1, 2, e, deltaw, odd=odd, maxj=maxj).trfis
                if options.flagfispartdamp
                else None
            )
            tfb2 = t1barrier(fp, grid, 2, e, deltaw, odd=odd, maxj=maxj).trfis
            live = (tfb1 >= TRANSEPS) & (tfb2 >= TRANSEPS)
            denom = torch.where(live, tfb1 + tfb2, torch.ones_like(tfb1))
            tf = torch.where(live, tfb1 * tfb2 / denom, torch.zeros_like(tfb1))
            if options.flagfispartdamp:
                trans = twkbtransint(fp.wkb, e, 1)
                tf = torch.where(live, tf * trans + tdir * (1.0 - trans), tf)
            ecut = float(fp.emaxclass2_mev[1] + 0.5 * fp.widthc2_mev[1])
            if options.flagclass2 and eex <= ecut:
                tf = torch.where(
                    live, _class2_boost(fp, 1, e, tf, tfb1 + tfb2, odd, maxj), tf
                )
        elif fp.nfisbar == 3:
            tfb2 = t1barrier(fp, grid, 2, e, deltaw, odd=odd, maxj=maxj).trfis
            tfb3 = t1barrier(fp, grid, 3, e, deltaw, odd=odd, maxj=maxj).trfis
            live = (tfb1 >= TRANSEPS) & (tfb2 >= TRANSEPS) & (tfb3 >= TRANSEPS)
            if options.flagfispartdamp:
                tf = _three_barrier_damped(fp, grid, e, deltaw, tfb1, tfb2, tfb3, odd, maxj)
            else:
                d12 = torch.where(live, tfb1 + tfb2, torch.ones_like(tfb1))
                tf12 = tfb1 * tfb2 / d12
                tsum = tf12 + tfb3
                tf = torch.where(
                    live, tf12 * tfb3 / torch.where(live, tsum, torch.ones_like(tsum)), tf
                )
            ecut = float(
                torch.maximum(
                    fp.emaxclass2_mev[1] + 0.5 * fp.widthc2_mev[1],
                    fp.emaxclass2_mev[2] + 0.5 * fp.widthc2_mev[2],
                )
            )
            if options.flagclass2 and eex <= ecut:
                d12 = torch.where(live, tfb1 + tfb2, torch.ones_like(tfb1))
                tf12 = _class2_boost(fp, 1, e, tfb1 * tfb2 / d12, tfb1 + tfb2, odd, maxj)
                tsum = tf12 + tfb3
                tf_new = tf12 * tfb3 / torch.where(live, tsum, torch.ones_like(tsum))
                tf = torch.where(live, _class2_boost(fp, 2, e, tf_new, tsum, odd, maxj), tf)
        out.append(tf * fnorm)

    tfisdown, tfis, tfisup = out
    jgrid = torch.arange(maxj + 1, dtype=DTYPE, device=dev) + 0.5 * odd
    e = torch.as_tensor(exinc_mev, dtype=DTYPE, device=dev)
    denfis = torch.stack(
        [density(ld, e.expand(maxj + 1), jgrid, p, 0) for p in (-1, 1)], dim=-1
    )
    gamfis = torch.where(
        denfis > 0.0, tfis / (c["twopi"] * denfis), torch.zeros_like(tfis)
    )
    taufis = torch.where(gamfis > 0.0, c["hbar"] / torch.clamp(gamfis, min=1e-300), torch.zeros_like(gamfis))
    return FissionTransmission(
        tfis=tfis,
        tfisdown=tfisdown,
        tfisup=tfisup,
        tfisA=tfisA,
        rhofisA=rhofisA,
        denfis_per_mev=denfis,
        gamfis_mev=gamfis,
        taufis_s=taufis,
    )


def _three_barrier_damped(fp, grid, e, deltaw, tfb1, tfb2, tfb3, odd, maxj):
    """Three humped barrier with partial damping of both wells (tfission.f90:200-235).

    Reached only with `fispartdamp y`; ported but ungated.
    """
    t12 = tdirbarrier(fp, grid, 1, 2, e, deltaw, odd=odd, maxj=maxj).trfis
    t23 = tdirbarrier(fp, grid, 2, 3, e, deltaw, odd=odd, maxj=maxj).trfis
    t13 = tdirbarrier(fp, grid, 1, 3, e, deltaw, odd=odd, maxj=maxj).trfis
    trans2 = twkbtransint(fp.wkb, e, 1)
    trans3 = twkbtransint(fp.wkb, e, 2)
    tdir21 = (1 - trans2) * t12
    tdir12 = (1 - trans2) * t12
    tdir23 = (1 - trans3) * t23
    tdir13 = (1 - trans2) * (1 - trans3) * t13
    ta12 = tfb1 * trans2
    ta23 = tfb2 * trans3
    ta13 = trans3 * tdir12
    ta32 = trans2 * tfb2
    sum2 = tfb1 + tdir23 + ta23
    sum3 = tdir21 + tfb3 + ta32
    ti2 = ta12 * (tdir23 / sum2 + ta23 * tfb3 / (sum2 * sum3))
    ti3 = ta13 * (tfb3 / sum3 + ta32 * tdir23 / (sum2 * sum3))
    ratio = (ta23 * ta32) / (sum2 * sum3)
    rnorm = torch.where(
        torch.abs(ratio - 1.0) <= 1.0e-8,
        sum2 * sum3 / ((tfb1 + tdir23) * sum3 + ta23 * (tdir21 + tfb3)),
        1.0 / (1.0 - ratio),
    )
    return tdir13 + rnorm * (ti2 + ti3)


__all__ = [
    "FissionLevelDensities",
    "FissionTransmission",
    "fission_level_densities",
    "fission_transmission",
]
