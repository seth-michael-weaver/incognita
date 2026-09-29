"""Tensor conventions for the TALYS port: dtype, the case axis, ragged padding, spin/parity grids.

Contract §4.2. Every per-reaction tensor leads with the case axis `C` (one target at one
incident energy). Per-nuclide structure of different lengths (discrete levels, continuum bins)
is padded to the batch maximum and carried with an explicit mask; padded entries contribute
exactly zero and must not produce NaN in the backward pass.

Spins follow TALYS's indexing exactly: the integer index `jx = 0, 1, ..., numJ` stands for
J = jx for integer-spin nuclei and J = jx + 1/2 for half-integer ones, with `J2 = 2J` where the
Fortran uses it. Parity is a length-2 axis ordered (-1, +1), matching `do parity = -1, 1, 2`.
"""

from __future__ import annotations

from dataclasses import dataclass

import torch
from torch import Tensor

DTYPE = torch.float64
PARITIES = (-1, 1)  # axis order for every parity dimension
NUMJ_DEFAULT = 40  # TALYS numJ (A0_talys_mod.f90): spins 0..40 (+1/2)


def as_tensor(x, device: torch.device | str | None = None) -> Tensor:
    """float64 tensor on `device` (no copy if already one)."""
    return torch.as_tensor(x, dtype=DTYPE, device=device)


@dataclass(frozen=True)
class CaseBatch:
    """The case axis: C (target, incident energy) pairs.

    Units: `e_inc_mev` MeV (lab-frame incident energy, as in the TALYS `energy` keyword).
    """

    Z: Tensor  # (C,) int64, target charge number
    A: Tensor  # (C,) int64, target mass number
    e_inc_mev: Tensor  # (C,) float64
    projectile: str = "n"

    def __post_init__(self):
        n = self.e_inc_mev.shape[0]
        if self.Z.shape != (n,) or self.A.shape != (n,):
            raise ValueError(
                f"CaseBatch axes disagree: Z{tuple(self.Z.shape)} A{tuple(self.A.shape)} E({n},)"
            )
        if self.e_inc_mev.dtype != DTYPE:
            raise TypeError("e_inc_mev must be float64 (contract §4.1)")

    @property
    def n(self) -> int:
        return int(self.e_inc_mev.shape[0])


@dataclass(frozen=True)
class Ragged:
    """Padded values with a validity mask of the same leading shape.

    `values[..., k]` is meaningful only where `mask[..., k]` is True. Use :meth:`masked_sum`
    and :meth:`safe` rather than summing `values` directly.
    """

    values: Tensor
    mask: Tensor  # bool, broadcastable to values

    def masked_sum(self, dim: int | tuple[int, ...]) -> Tensor:
        return torch.where(
            self.mask,
            self.values,
            torch.zeros((), dtype=self.values.dtype, device=self.values.device),
        ).sum(dim)

    def safe(self, fill: float = 1.0) -> Tensor:
        """values with padded entries replaced by `fill`, for use before log/sqrt/division."""
        return torch.where(
            self.mask,
            self.values,
            torch.full((), fill, dtype=self.values.dtype, device=self.values.device),
        )


def pad_stack(seqs: list[Tensor], fill: float = 0.0) -> Ragged:
    """Stack 1-D tensors of different lengths into (len(seqs), max_len) with a mask."""
    n = max((int(s.shape[0]) for s in seqs), default=0)
    dev = seqs[0].device if seqs else None
    vals = torch.full((len(seqs), n), fill, dtype=DTYPE, device=dev)
    mask = torch.zeros((len(seqs), n), dtype=torch.bool, device=dev)
    for i, s in enumerate(seqs):
        k = int(s.shape[0])
        vals[i, :k] = s.to(DTYPE)
        mask[i, :k] = True
    return Ragged(vals, mask)


def spin_values(numj: int = NUMJ_DEFAULT, half_integer: bool = False, device=None) -> Tensor:
    """J for each spin index jx (TALYS convention): jx or jx + 1/2."""
    j = torch.arange(numj + 1, dtype=DTYPE, device=device)
    return j + 0.5 if half_integer else j
