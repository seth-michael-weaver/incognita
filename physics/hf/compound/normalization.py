"""Normalisation of the compound cross section to the reaction cross section minus the direct and
pre-equilibrium parts, and the compound-formation bookkeeping the (J, parity) loops need.

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

Task: T9 (physics/hf/CONTRACT.md §7). Acceptance test: A-cn1 (§6).

TALYS routines ported here (file:line of the subroutine/function statement):
    compnorm.f90:1 (compnorm)

What compnorm does, and why it matters for the gates. ECIS's reaction cross section and the sum
over the incident transmission coefficients are not identical, so TALYS renormalises: it builds
`xsreacsum = sum_{J,P} CNfactor (2J+1) sum_{j,l} Tjlinc`, the compound-formation flux
`xsflux = sigma_R - sigma_direct - sigma_preeq - sigma_GR`, and folds `cfratio/norm` into
`CNfactor`. Everything downstream (`comptarget`, this module's `cn_factor_mb`) multiplies by that
one number, which is exactly the `cnfactor_mb` field `prepare.CompoundInputs` carries, so the
A-cn1/A-cn2 gates test `comptarget` with TALYS's own normalisation injected and this module
separately against the same dump.

`population.f90` is the initial-population variant for `Einc`-less runs (astrophysics and the
`population` TALYS variant); it is out of scope here and is listed in CONTRACT.md §8's spirit —
T10 needs it only for the `population` reference variant, which no gate uses.

Units: `pik2_mb` is pi/k^2 in mb (compnorm.f90:95 `pik2 = 10. * pi / (wavenum * wavenum)`, i.e.
fm^2 -> mb); every cross section in and out is mb; `wavenum_per_fm` is TALYS's `wavenum`.
"""

from __future__ import annotations

from dataclasses import dataclass

import torch
from torch import Tensor

from physics.hf.core.tensors import DTYPE
from physics.hf.core.units import MB_PER_FM2

PARSPIN2 = (0, 1, 1, 2, 1, 1, 0)  # int(2*parspin) for gamma, n, p, d, t, h, alpha
SPIN2 = (1, 1, 1, 2, 1, 1, 1)  # constants.f90 spin2; 1 for photons and alphas


@dataclass(frozen=True)
class CompoundFormation:
    """The result of compnorm: what `comptarget` needs before it starts looping."""

    cn_factor_mb: Tensor  # CNfactor after renormalisation [mb], scalar or (C,)
    cn_term_mb: Tensor  # CNterm(parity, J) [mb], (C, 2, numJ+1), parity axis (-1, +1)
    xs_reacsum_mb: Tensor  # sum over T(j,l) (B in TALYS's check output)
    xs_flux_mb: Tensor  # compound nucleus formation cross section (C)
    cf_ratio: Tensor  # C/B
    j2beg: int
    j2end: int


def reaction_transmission_sum(
    tjlinc: Tensor,
    targetspin2: int,
    target_parity: int,
    lmaxinc: int,
    k0: int,
    numj: int = 40,
) -> tuple[Tensor, int, int]:
    """`CNterm(parity, J) / CNfactor` = (2J+1) sum_{j,l} Tjlinc over the incident channels of each
    (J, parity), plus TALYS's J2beg / J2end. Factored out of compnorm so the gate can check the
    identity `CNfactor * sum = xsflux` with dumped numbers only (no wave number needed).

    TALYS: compnorm.f90:1 (compnorm)  -- the loop over incoming channels
    Test: A-cn1
    """
    parspin2 = PARSPIN2[k0]
    j2beg = (targetspin2 + parspin2) % 2
    j2end = min(2 * lmaxinc + parspin2 + targetspin2, 2 * numj)
    if (tjlinc.dtype == torch.float64 and tjlinc.device.type == "cpu"
            and not (torch.is_grad_enabled() and tjlinc.requires_grad)):
        # CENGBOOK: the same sums on Python floats (IEEE double, the same operations in the same
        # order as the 0-d tensor arithmetic below), filled into the tensor once
        return _transmission_sum_floats(tjlinc.tolist(), targetspin2, target_parity, lmaxinc,
                                        k0, numj, j2beg, j2end), j2beg, j2end
    out = torch.zeros((2, numj + 1), dtype=DTYPE, device=tjlinc.device)
    for parity in (-1, 1):
        pardif = abs(target_parity - parity) // 2
        pi_ = 0 if parity == -1 else 1
        for J2 in range(j2beg, j2end + 1, 2):
            acc = torch.zeros((), dtype=DTYPE, device=tjlinc.device)
            for jj2 in range(abs(J2 - targetspin2), J2 + targetspin2 + 1, 2):
                for l in range(abs(jj2 - parspin2) // 2, (jj2 + parspin2) // 2 + 1):
                    if k0 > 0:
                        if l > lmaxinc or l % 2 != pardif:
                            continue
                        updown = (jj2 - 2 * l) // SPIN2[k0]
                    else:
                        updown = 1
                        if (pardif == 0 and l % 2 == 1) or (pardif != 0 and l % 2 == 0):
                            updown = 0
                    if l < tjlinc.shape[0]:
                        acc = acc + (J2 + 1.0) * tjlinc[l, updown + 1]
            out[pi_, J2 // 2] = acc
    return out, j2beg, j2end


def _transmission_sum_floats(T: list, targetspin2: int, target_parity: int, lmaxinc: int, k0: int,
                            numj: int, j2beg: int, j2end: int) -> Tensor:
    """`reaction_transmission_sum`'s loop over a (l, updown) list of floats.

    TALYS: compnorm.f90:1 (compnorm)
    Test: A-cn1
    """
    parspin2 = PARSPIN2[k0]
    nrow = len(T)
    vals = [[0.0] * (numj + 1), [0.0] * (numj + 1)]
    for parity in (-1, 1):
        pardif = abs(target_parity - parity) // 2
        row = vals[0 if parity == -1 else 1]
        for J2 in range(j2beg, j2end + 1, 2):
            acc = 0.0
            for jj2 in range(abs(J2 - targetspin2), J2 + targetspin2 + 1, 2):
                for l in range(abs(jj2 - parspin2) // 2, (jj2 + parspin2) // 2 + 1):  # noqa: E741
                    if k0 > 0:
                        if l > lmaxinc or l % 2 != pardif:
                            continue
                        updown = (jj2 - 2 * l) // SPIN2[k0]
                    else:
                        updown = 1
                        if (pardif == 0 and l % 2 == 1) or (pardif != 0 and l % 2 == 0):
                            updown = 0
                    if l < nrow:
                        acc = acc + (J2 + 1.0) * T[l][updown + 1]
            row[J2 // 2] = acc
    return torch.tensor(vals, dtype=DTYPE)


def compound_formation(
    tjlinc: Tensor,
    wavenum_per_fm: Tensor,
    targetspin2: int,
    target_parity: int,
    lmaxinc: int,
    k0: int,
    xsreacinc_mb: Tensor,
    xsdirdiscsum_mb: Tensor,
    xspreeqsum_mb: Tensor,
    xsgrsum_mb: Tensor,
    numj: int = 40,
    spherical: bool = True,
    xscoupled_mb: Tensor | None = None,
) -> CompoundFormation:
    """The cross section available for compound formation [mb] and the renormalised CNfactor.

    `tjlinc` is TALYS's `Tjlinc(updown, l)` with the port's axis order `(l, updown)` and the
    updown axis ordered (-1, 0, +1), i.e. `IncidentChannel.tjl_inc` padded to 3 (CONTRACT §5);
    for photons (k0 = 0) the updown index is the multipole selection flag, not a spin projection.
    `spherical` is `colltype == 'S' .or. flagspher`: when False the coupled-channels branch is
    taken and `xscoupled_mb` is required.

    TALYS: compnorm.f90:1 (compnorm)
    Test: A-cn1
    """
    dev = tjlinc.device
    pik2_mb = MB_PER_FM2 * torch.pi / (wavenum_per_fm * wavenum_per_fm)
    parspin2 = PARSPIN2[k0]
    cn0 = pik2_mb / (parspin2 + 1.0) / (targetspin2 + 1.0)
    if k0 == 0:
        cn0 = 0.5 * cn0
    tsum, j2beg, j2end = reaction_transmission_sum(
        tjlinc, targetspin2, target_parity, lmaxinc, k0, numj
    )
    cn_term = cn0 * tsum
    xsreacsum = cn_term.sum()
    if spherical:
        norm = xsreacsum / xsreacinc_mb
        xsflux = xsreacinc_mb - xsdirdiscsum_mb - xspreeqsum_mb - xsgrsum_mb
        cfratio = torch.where(xsreacinc_mb > 0, xsflux / xsreacinc_mb, torch.zeros_like(xsflux))
    else:
        if xscoupled_mb is None:
            raise ValueError("compnorm: the coupled-channels branch needs xscoupled_mb")
        norm = torch.ones((), dtype=DTYPE, device=dev)
        xsflux = xsreacsum - xsdirdiscsum_mb + xscoupled_mb - xspreeqsum_mb - xsgrsum_mb
        cfratio = torch.where(xsreacsum > 0, xsflux / xsreacsum, torch.zeros_like(xsflux))
    cn_factor = torch.where(norm > 0, cn0 * cfratio / torch.where(norm > 0, norm, 1.0), cn0)
    return CompoundFormation(cn_factor, cn_term[None], xsreacsum, xsflux, cfratio, j2beg, j2end)
