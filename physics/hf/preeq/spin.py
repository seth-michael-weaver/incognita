"""Spin distribution of the pre-equilibrium residual population.

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

Task: T8 (physics/hf/CONTRACT.md §7). Acceptance test: A-pe (§6).

TALYS routines ported here (file:line of the subroutine/function statement):
    preeqspindis.f90:1 (preeqspindis)
    newspin.f90:1 (newspin, spin_wigner)

`pespinmodel 4` (the Wigner `spin_wigner`/`newspin` distribution) depends on the incident
energy, so it needs `einc_mev` (KWCOV B7); TALYS's default is 1 for a neutron projectile and 2
for a charged one. `pespinmodel >= 3` is what makes `exciton2` build a J-dependent
pre-equilibrium cross section from `RnJ`.
"""

from __future__ import annotations

import math

import torch
from torch import Tensor

from physics.hf.core.constants import talys_constants
from physics.hf.core.tensors import DTYPE
from physics.hf.density.particle_hole import NUMEXC

MAXJPH = 30  # preeqspindis.f90:44


def newspin(a: int, e_mev: float, n: int) -> float:
    """The width of the Wigner pre-equilibrium spin distribution, global parameters (newspin.f90, iglob 1).

    TALYS: newspin.f90:1 (newspin)
    Test: tests/hf/test_kwcov_b7.py
    """
    a13 = float(a) ** (1.0 / 3.0)
    fa = -0.680858 * a13 + 6.37643
    fb = 0.0818127 * a13 - 0.557189
    fc = 1.14442 * a13 - 7.1285
    return 0.7 * (fa * e_mev ** 0.25 + fb * e_mev ** 0.75 + fc + 0.5) * float(n) ** 0.44


def preeq_spin_distribution(
    options, params, atarget: int, *, maxexc: int = NUMEXC, device=None, einc_mev: float | None = None
) -> dict[str, Tensor]:
    """`RnJ(n, J)` and `RnJsum(n)` (preeqspindis.f90:45-56), dimensionless.

    ``sigma2ph = Rspincutpreeq * 0.24 * n * Atarget^(2/3)`` and
    ``RnJ = (2J+1) / (2 sqrt(2 pi) sigma2ph^1.5) exp(-(J+1/2)^2 / (2 sigma2ph))``;
    `RnJsum` is the (2J+1)-weighted sum `exciton2` normalises with.

    Returns ``{"RnJ": (maxexc+1, maxJph+1), "RnJsum": (maxexc+1,)}``, index 0 unused as in
    TALYS. Differentiable in `Rspincutpreeq` (§4.4).

    TALYS: preeqspindis.f90:1 (preeqspindis)
    Test: A-pe
    """
    c = talys_constants()
    if int(getattr(options, "pespinmodel", 1)) == 4:
        # KWCOV B7: preeqspindis.f90:58-66, RnJ = spin_wigner(J, eta) / (2J+1), eta = sqrt(Rspincutpreeq) newspin
        if einc_mev is None:
            raise NotImplementedError("not ported: preeqspin 4 with multiple pre-equilibrium (the Wigner spin "
                                      "distribution depends on the incident energy; only the binary exciton model "
                                      "has it)")
        rs = float(params.at("rspincutpreeq"))
        sq = math.sqrt(4.0 * math.atan(1.0))
        rnj = torch.zeros(maxexc + 1, MAXJPH + 1, dtype=DTYPE, device=device)
        for n in range(1, maxexc + 1):
            eta = math.sqrt(rs) * newspin(atarget, float(einc_mev), n)
            for J in range(MAXJPH + 1):
                rnj[n, J] = (2.0 * J + 1.0) ** 2 / (eta ** 3 * sq) * math.exp(-((J + 0.5) ** 2) / eta ** 2) / (
                    2.0 * J + 1.0)
        J = torch.arange(0, MAXJPH + 1, dtype=DTYPE, device=device).reshape(1, -1)
        return {"RnJ": rnj, "RnJsum": ((2.0 * J + 1.0) * rnj).sum(-1)}
    twothird, sqrttwopi = c["twothird"], c["sqrttwopi"]
    rs = torch.as_tensor(params.at("rspincutpreeq"), dtype=DTYPE, device=device)
    n = torch.arange(0, maxexc + 1, dtype=DTYPE, device=device).reshape(-1, 1)
    J = torch.arange(0, MAXJPH + 1, dtype=DTYPE, device=device).reshape(1, -1)
    sigma2ph = rs * 0.24 * n * float(atarget) ** twothird
    ok = sigma2ph > 0
    s = torch.where(ok, sigma2ph, torch.ones_like(sigma2ph))
    denom = 2.0 * sqrttwopi * s**1.5
    rnj = torch.where(
        ok,
        (2.0 * J + 1.0) / denom * torch.exp(-((J + 0.5) ** 2) / (2.0 * s)),
        torch.zeros_like(s + J),
    )
    return {"RnJ": rnj, "RnJsum": ((2.0 * J + 1.0) * rnj).sum(-1)}


def spin_weighted_spectra(
    xs_mb: Tensor, n: Tensor, rnj: dict[str, Tensor], maxjph: int = MAXJPH
) -> Tensor:
    """`xspreeqJP(type, nen, J, parity)` from a per-state spectrum (exciton2.f90:121-128).

    ``xs * 0.5 * (2J+1) * RnJ(n, J) / RnJsum(n)``, the same for both parities. `xs_mb` is
    (..., S, ...) over exciton states with exciton number `n` (S,); the result gains a trailing
    (J, parity) pair of axes with parity ordered (-1, +1) as in TALYS (contract §4.2).

    TALYS: exciton2.f90:1 (exciton2)
    Test: A-pe
    """
    w = rnj["RnJ"][n] / rnj["RnJsum"][n].unsqueeze(-1)  # (S, J+1)
    J = torch.arange(0, maxjph + 1, dtype=DTYPE, device=xs_mb.device)
    w = 0.5 * (2.0 * J + 1.0) * w
    out = xs_mb.unsqueeze(-1) * w.reshape(*([1] * (xs_mb.dim() - 1)), -1)
    return torch.stack([out, out], dim=-1)
