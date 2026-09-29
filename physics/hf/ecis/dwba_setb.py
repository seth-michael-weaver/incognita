"""SETB: two pieces of `ecis.dwba.dwba_cross_sections` that were recomputed far more often than
their inputs change. Both return the bits the inline code returned.

* **The Clebsch-Gordan weights.** `(2 j_c + 1) / (2 s + 1) <j_c -1/2; lambda 0 | j_c' -1/2>^2`
  masked to the natural-parity, open-entrance channels depends on (lambda, parity, lmax, njmax,
  s) only, and the l/j tables are `_lj_table(lmax)`'s. The inline code rebuilt it at every
  incident energy; it is a pure function, cached for the worker (`chartrun.KEEP`), like the
  other angular-momentum tables.
* **The Coulomb functions of `_normalise`.** rho = k r_match and eta are per exit level, but the
  inline code evaluated `coulomb_functions` on the (level, channel) product -- every level's row
  once per channel, ~50 times -- and then picked each channel's own l. `coulomb_functions` is
  elementwise with two batch-level constants (the continued fraction's starting order,
  `int(rho.max()) + 60`, and the inward Numerov's step count from the largest `rb - ra`), and a
  maximum over repeated values is the maximum over the distinct ones; so one row per level, then
  the same gather, is the same numbers.

* **The levels that are solved.** The level sum skips a level whose multipole cannot reach its
  parity, whose deformation is zero or whose channel is closed, but the distorted waves were
  integrated and normalised for every level anyway, and a call with no such level at all (17 of
  Zr-88's 27) ran the whole deck to return zeros. Each row of the Numerov and of `_normalise` is
  independent; the one batch-level input, the Coulomb functions' largest rho, is the entrance
  channel's, which is always kept. So the kept rows carry the same numbers.

TALYS: directecis.f90:1 (directecis), ecist.f:5775 (fcou)
Test: tests/hf/test_setb.py (bitwise against the inline forms)
"""

from __future__ import annotations

from functools import lru_cache

import torch
from torch import Tensor

from physics.hf.core.tensors import DTYPE

__all__ = ["cg_weights", "exit_waves", "live_levels"]


@lru_cache(maxsize=512)
def cg_weights(lam: int, pb: int, lmax: int, njmax: int, spin: float) -> Tensor:
    """`dwba_cross_sections`'s `weights[(lam, pb)]`: (NLJ, NLJ), exit channel by entrance channel.

    CENGSETUP: the leading (NLJ, NLJ) block of one table per (lambda, parity, s) on the largest
    l/j table seen so far (`_cg_table`), times the open-entrance mask. `_lj_table(lmax)` lists
    its channels in l order, so a smaller table is a leading block of a larger one, and every
    factor is elementwise (`clebsch` included: its Horner loop skips an element's leading
    iterations, and its factorials are a table), so the block holds the bits of the inline form;
    multiplying by the 0/1 masks one at a time instead of by their product is the same numbers.
    A key used to miss at every (lmax, njmax) of a new target -- ~600 Clebsch-Gordan tables a
    chart.

    TALYS: directecis.f90:1 (directecis)
    Test: tests/hf/test_setb.py, tests/hf/test_cengsetup.py
    """
    from physics.hf.ecis.dwba import _lj_table

    size = max(lmax, _CG_LMAX)
    base = _cg_table(lam, pb, size, spin)
    _l, j, _ls2 = _lj_table(lmax)
    nlj = j.shape[0]
    open_j = (j[None, :] <= njmax + 0.5 + 1.0e-9).to(DTYPE)
    return base[:nlj, :nlj] * open_j


_CG_LMAX = 72  # numl 60 + the largest multipole + 1, with room


@lru_cache(maxsize=64)
def _cg_table(lam: int, pb: int, lmax: int, spin: float) -> Tensor:
    """`cg_weights` on `_lj_table(lmax)` before the open-entrance mask.

    Only the elements that can be non-zero are evaluated: natural parity for the multipole
    (`keep`) and the triangle |j_c - lambda| <= j_c' <= j_c + lambda. Everywhere else the inline
    form multiplies a zero (`keep`, or `clebsch`'s own zero outside the triangle), which is +0.
    """
    from physics.hf.core.angmom import clebsch
    from physics.hf.ecis.dwba import _lj_table

    l, j, _ls2 = _lj_table(lmax)
    jc, jp = j[None, :], j[:, None]
    par = ((-1.0) ** (l.to(DTYPE)[:, None] + l.to(DTYPE)[None, :]))
    keep = (pb * par > 0).to(DTYPE)
    tri = (jp >= (jc - lam).abs() - 1.0e-9) & (jp <= jc + lam + 1.0e-9) & (keep > 0)
    p_idx, c_idx = tri.nonzero(as_tuple=True)
    jcs, jps = j[c_idx], j[p_idx]
    lm = torch.full_like(jcs, float(lam))
    cg = clebsch(jcs, lm, jps, torch.full_like(lm, -0.5), torch.zeros_like(lm),
                 torch.full_like(lm, -0.5))
    out = torch.zeros((j.shape[0], j.shape[0]), dtype=DTYPE)
    out[p_idx, c_idx] = (2.0 * jcs + 1.0) / (2.0 * spin + 1.0) * cg * cg * keep[p_idx, c_idx]
    return out


def _cg_weights_inline(lam: int, pb: int, lmax: int, njmax: int, spin: float) -> Tensor:
    """The SETB form of `cg_weights`, kept for the bitwise test."""
    from physics.hf.core.angmom import clebsch
    from physics.hf.ecis.dwba import _lj_table

    l, j, _ls2 = _lj_table(lmax)
    jc, jp = j[None, :], j[:, None]
    par = ((-1.0) ** (l.to(DTYPE)[:, None] + l.to(DTYPE)[None, :]))
    open_j = (jc <= njmax + 0.5 + 1.0e-9).to(DTYPE)
    lm = torch.full_like(jp.expand(jp.shape[0], jc.shape[1]), float(lam))
    cg = clebsch(
        jc.expand_as(lm), lm, jp.expand_as(lm),
        torch.full_like(lm, -0.5), torch.zeros_like(lm), torch.full_like(lm, -0.5),
    )
    keep = (pb * par > 0).to(DTYPE) * open_j
    return (2.0 * jc + 1.0) / (2.0 * spin + 1.0) * cg * cg * keep


def exit_waves(kappa2: Tensor, eta: Tensor, l: Tensor, rm: float, nk: int, nlj: int):
    """`_normalise`'s `(hp, dhp)` = (G_l + i F_l, k (G_l' + i F_l')) at r_match for every
    (level, channel), from one Coulomb-function row per level.

    TALYS: ecist.f:5775 (fcou)
    Test: tests/hf/test_setb.py
    """
    from physics.hf.omp.schrodinger import coulomb_functions

    k = kappa2.abs().sqrt()
    lmax = int(l.max())
    F, dF, G, dG = coulomb_functions(eta.detach(), (k * rm).detach(), lmax)
    kk = k[:, None].expand(nk, nlj)
    hp = torch.complex(G[:, l], F[:, l])
    dhp = torch.complex(dG[:, l] * kk, dF[:, l] * kk)
    return hp, dhp


def live_levels(level_spin: Tensor, level_parity: Tensor, vibbeta: Tensor, kappa2: Tensor,
                n_lev: int) -> list[int]:
    """The levels `dwba_cross_sections`' sum reads: natural parity for the multipole, non-zero
    deformation, open channel (its `continue` test, evaluated first).

    TALYS: directecis.f90:1 (directecis)
    Test: tests/hf/test_setb.py
    """
    import math

    out = []
    for b in range(n_lev):
        lam = int(round(float(level_spin[b])))
        d = float(vibbeta[b]) / math.sqrt(4.0 * math.pi)
        if int(level_parity[b]) != (-1) ** lam or d == 0.0 or float(kappa2[b + 1]) <= 0.0:
            continue
        out.append(b)
    return out
