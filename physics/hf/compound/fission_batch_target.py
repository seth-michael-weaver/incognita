"""FISSB: fission as one more exit channel of `compound.target_batch`'s every-cell target decay.

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

Task: FISSB (the speed work; no physics of its own). Acceptance test: A-cn2 / E2E through
`tests/hf/test_fission_batch.py`, which holds it to `target._case`'s per-cell loop.

TALYS routines this computes, in the arrangement described below:
    comptarget.f90:1 (comptarget)      -- the fission term of the (J, parity) sum
    compprepare.f90:1 (compprepare)    -- `denomhf` with `tfis`, and the Hill-Wheeler humps
    molprepare.f90:1 (molprepare)      -- the humps in the Gauss-Laguerre product
    moldauer.f90:1 (moldauer)          -- `W(a, fission hump)`

`target_batch.case_nowfc` and `case_moldauer` handed every fissioning target back to
`target._case`, which rebuilds `prepare.exit_channel_sums` per (J, parity) cell. In comptarget the
fission transmission of a cell is one number, `tfis(J, P)`, with no residual state, spin or l'
structure, so on a cell axis it is a `(K,)` vector:

* **without width fluctuations** it is one more term of `denomhf` and one more output,
  ``xs_fis = sum_cells CNfactor (J2 + 1) / denomhf * feed * tfis``;
* **with Moldauer's** (target.py's `ratio_h` block) the cell's `NUMHILL` Hill-Wheeler humps are
  exit channels with transmission ``tfisA(i)/tfisA(0) * tfis / max(rhofisA(i), 1)`` and
  degeneracy ``max(rhofisA(i), 1)``: they enter the node product `P_m` after the particle
  channels, and ``xs_fis = sum_cells pref * tfis * sum_i ratio_i G(hump i)``.

These are the helpers the two batched cases call; with `flagfission` off or `nfisbar = 0` they
return None and the cases run exactly as before.
"""

from __future__ import annotations

import torch
from torch import Tensor

from physics.hf.core.tensors import DTYPE

__all__ = ["NUMHILL", "cell_fission_widths", "hump_channels", "hump_fission"]

NUMHILL = 20  # A0_talys_mod.f90:77


def cell_fission_widths(inp, cells: list[tuple[int, int]], device=None) -> Tensor | None:
    """`tfis(J2, P)` of every cell, `(K,)`, as `exit_channel_sums`'s `fiswidth`; None when the
    target does not fission.

    TALYS: compprepare.f90:1 (compprepare)
    Test: tests/hf/test_fission_batch.py
    """
    if not (inp.flagfission and inp.nfisbar != 0):
        return None
    return torch.tensor([float(inp.tfis.get(c, 0.0)) for c in cells], dtype=DTYPE, device=device)


def hump_channels(inp, cells: list[tuple[int, int]], tf: Tensor, device=None):
    """The Hill-Wheeler hump channels of every cell: `(ratio, t, rho, on)` with `ratio`, `t` and
    `rho` `(K, NUMHILL)` and `on` `(K,)` where `tfisA(0) > 0` (target.py:163-175, :251).

    TALYS: compprepare.f90:1 (compprepare), molprepare.f90:1 (molprepare)
    Test: tests/hf/test_fission_batch.py
    """
    K = len(cells)
    ta = torch.zeros((K, NUMHILL + 1), dtype=DTYPE, device=device)
    ra = torch.zeros((K, NUMHILL + 1), dtype=DTYPE, device=device)
    for k, c in enumerate(cells):
        a = inp.tfisA.get(c)
        if a is not None:
            ta[k] = torch.as_tensor(a, dtype=DTYPE, device=device)
        r = inp.rhofisA.get(c)
        if r is not None:
            ra[k] = torch.as_tensor(r, dtype=DTYPE, device=device)
    t0 = ta[:, :1]
    ratio = torch.where(t0 > 0, ta[:, 1:] / torch.where(t0 > 0, t0, 1.0), 0.0)
    tfh = ratio * tf[:, None]
    rho = torch.clamp(ra[:, 1:], min=1.0)
    t = torch.where(tfh > 1.0e-30, tfh / rho, 0.0)
    return ratio, t, rho, ta[:, 0] > 0


def hump_fission(x: Tensor, PH: Tensor, st: Tensor, pref: Tensor, tf: Tensor, ratio: Tensor,
                 t: Tensor, nu: Tensor, on: Tensor) -> Tensor:
    """``sum_cells pref * tfis * sum_i ratio_i G(hump i)`` with ``G = sum_m P_m H_m / (1 + x_m f)``
    and ``f = 2 T / (st nu)``, over the cells with `tfisA(0) > 0` (target.py:248-263).

    TALYS: comptarget.f90:1 (comptarget), moldauer.f90:1 (moldauer)
    Test: tests/hf/test_fission_batch.py
    """
    fb = 2.0 * t / (st[:, None] * nu)  # (K, H)
    gh = (PH[:, :, None] / (1.0 + x[None, :, None] * fb[:, None, :])).sum(1)  # (K, H)
    per = torch.where(ratio != 0, gh * ratio, 0.0).sum(1)
    return torch.where(on, pref * tf * per, 0.0).sum()
