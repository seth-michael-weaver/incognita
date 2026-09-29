"""FISSB: the fission transmission of a whole bin ladder in one evaluation per barrier.

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

Task: FISSB (the speed work; no physics of its own). Acceptance test: A-fis / E2E through
`tests/hf/test_fission_batch.py`, which holds it to `fission.chain.FissionChain.bin_triples` and
`compound.continuum.fission_width`.

TALYS routines this computes, in the arrangement described below:
    t1barrier.f90:1 (t1barrier)   -- the continuum above `fecont`, no rotational band
    tfission.f90:1 (tfission)     -- one, two and three humps, no class II, no `fispartdamp`
    compound.f90:120-147          -- the logarithmic integration of the triple over each bin

`multiple_emission` asks `FissionChain.bin_triples` for one mother bin at a time, and each call
runs `t1barrier` at three energies per barrier. Every call takes the logarithms of the same
`(segment, J, parity)` barrier level densities again, which made `_log_integrate` the biggest
single function of a fissioning nuclide (MERGEX §3). Two rearrangements, neither physics:

* **The logarithms once per grid.** `_log_integrate(rho1, rho2, rho3, dE1, dE2)` is
  ``A dE1 + B dE2`` with ``A = (rho1 - rho2) / ln(rho1 / rho2)`` and ``B`` the same for
  ``(rho2, rho3)``, or ``A = B = rho2`` where a logarithm difference vanishes. Only `dE1`/`dE2`
  depend on the excitation energy (the top triple is clipped at it), so `A` and `B` are built
  once per `densprepare` grid.
* **Every energy of the ladder at once.** With the energies on a leading axis, the clipped
  `dE1`/`dE2`, the `keep` mask and the penetrability are `(energy, segment)` arrays, and the
  transmission is ``A . (dE1 keep T) + B . (dE2 keep T)``, two matrix products.

The hump combination is elementwise and unchanged. All terms of the sums are non-negative, so the
numbers move by rounding only. Not covered (the caller keeps the per-bin path): a rotational band
on a barrier (`hbstate y`), `class2 y`, `fispartdamp y`, and more than three barriers.
"""

from __future__ import annotations

import numpy as np
import torch
from torch import Tensor

from physics.hf.core.tensors import DTYPE
from physics.hf.fission.barriers import _EPS, _penetrability, barrier_height
from physics.hf.fission.transmission import TRANSEPS

__all__ = ["covered", "ladder_bin_widths", "ladder_transmission"]


def covered(fp, options) -> bool:
    """Whether `ladder_transmission` reproduces `fission_transmission` for this nucleus.

    TALYS: tfission.f90:1 (tfission)
    Test: tests/hf/test_fission_batch.py
    """
    nb = int(fp.nfisbar)
    if nb not in (1, 2, 3) or options.flagclass2 or options.flagfispartdamp:
        return False
    return all(fp.rotational[ibar].n == 0 for ibar in range(1, nb + 1))


def _coefficients(grid, ibar: int, dev) -> tuple[Tensor, ...]:
    """`(elow, e_mid, e_up, A, B)` of barrier `ibar`'s `eintfis` triples: `A`/`B` are
    `(segment, (maxj+1) * 2)`, `_log_integrate`'s two slopes (t1barrier.f90:151-168)."""
    nb = grid.nbintfis[ibar]
    idx = torch.arange(1, nb - 1, 2, device=dev)
    e = grid.eintfis_mev[ibar]
    r = grid.rhofis[ibar]
    rho1 = r[idx] * (1.0 + _EPS) + _EPS
    rho2 = r[idx + 1] + _EPS
    rho3 = r[idx + 2] * (1.0 + _EPS) + _EPS
    r1, r2, r3 = torch.log(rho1), torch.log(rho2), torch.log(rho3)
    ok = (r2 != r1) & (r2 != r3)
    s12 = torch.where(ok, r1 - r2, torch.ones_like(r1))
    s23 = torch.where(ok, r2 - r3, torch.ones_like(r1))
    A = torch.where(ok, (rho1 - rho2) / s12, rho2)
    B = torch.where(ok, (rho2 - rho3) / s23, rho2)
    n = A.shape[0]
    return e[idx], e[idx + 1], e[idx + 2], A.reshape(n, -1), B.reshape(n, -1)


def _barrier(fp, grid, ibar: int, eex: Tensor, deltaw: Tensor, shape, cache: dict) -> Tensor:
    """`t1barrier(...).trfis` at every energy of `eex`, `(E, maxj+1, 2)`.

    TALYS: t1barrier.f90:1 (t1barrier)
    Test: tests/hf/test_fission_batch.py
    """
    dev = eex.device
    E = eex.shape[0]
    if dev.type == "cpu":
        from physics.hf.fission.fis2_nx2 import ladder

        got = ladder(fp, grid, ibar, eex, deltaw, shape)  # NX2 fis2: every energy in one C call
        if got is not None:
            return got
    out = torch.zeros((E, *shape), dtype=DTYPE, device=dev)
    if grid.nbintfis[ibar] < 3:
        return out
    key = (id(grid), ibar)
    coef = cache.get(key)
    if coef is None or coef[0] is not grid:
        coef = cache[key] = (grid, _coefficients(grid, ibar, dev))
    elow, e1, e2, A, B = coef[1]
    on = eex >= fp.fecont_mev[ibar]
    if not bool(on.any()):
        return out
    x = eex[:, None]
    emid = torch.minimum(e1[None, :], x)
    eup = torch.minimum(e2[None, :], x)
    keep = (elow[None, :] <= x).to(DTYPE)
    bfis, wfis = barrier_height(fp, ibar, deltaw)
    t1 = _penetrability(fp, x - emid, ibar, bfis, wfis) * keep  # (E, segment)
    tr = ((emid - elow[None, :]) * t1) @ A + ((eup - emid) * t1) @ B
    return torch.where(on[:, None, None], tr.reshape(E, *shape), out)


def ladder_transmission(fp, grid, ld, eex_mev, options, *, maxj: int, fnorm: float = 1.0,
                        cache: dict | None = None) -> Tensor:
    """`tf * fnorm` of `fission_transmission` at every energy of `eex_mev`, `(E, maxj+1, 2)`,
    parity axis `(-1, +1)`. Only for nuclei `covered` accepts.

    TALYS: tfission.f90:1 (tfission)
    Test: tests/hf/test_fission_batch.py
    """
    dev = fp.fbarrier_mev.device
    cache = {} if cache is None else cache
    eex = torch.as_tensor(np.asarray(eex_mev, dtype=np.float64), dtype=DTYPE, device=dev)
    shape = (maxj + 1, 2)
    deltaw = ld.deltaW_mev
    tfb1 = _barrier(fp, grid, 1, eex, deltaw, shape, cache)
    nb = int(fp.nfisbar)
    if nb == 1:
        tf = tfb1
    elif nb == 2:
        tfb2 = _barrier(fp, grid, 2, eex, deltaw, shape, cache)
        live = (tfb1 >= TRANSEPS) & (tfb2 >= TRANSEPS)
        denom = torch.where(live, tfb1 + tfb2, torch.ones_like(tfb1))
        tf = torch.where(live, tfb1 * tfb2 / denom, torch.zeros_like(tfb1))
    else:
        tfb2 = _barrier(fp, grid, 2, eex, deltaw, shape, cache)
        tfb3 = _barrier(fp, grid, 3, eex, deltaw, shape, cache)
        live = (tfb1 >= TRANSEPS) & (tfb2 >= TRANSEPS) & (tfb3 >= TRANSEPS)
        d12 = torch.where(live, tfb1 + tfb2, torch.ones_like(tfb1))
        tf12 = tfb1 * tfb2 / d12
        tsum = tf12 + tfb3
        tf = torch.where(live, tf12 * tfb3 / torch.where(live, tsum, torch.ones_like(tsum)),
                         torch.zeros_like(tfb1))
    return tf * fnorm


def ladder_bin_widths(fp, grid, ld, ex_mev: np.ndarray, dex_mev: np.ndarray, exmax_mev: float,
                      options, *, maxj: int, fnorm: float = 1.0,
                      cache: dict | None = None) -> np.ndarray:
    """`continuum.fission_width` of every mother bin `(ex_mev[b], dex_mev[b])` and every
    (J, parity), `(bins, maxj+1, 2)` float64: the triple at ``Ex - dEx/2``, ``Ex`` and
    ``Ex + dEx/2`` (clipped to `[0, Exmax]`) integrated logarithmically over the bin.

    TALYS: compound.f90:120-147 (compound), tfission.f90:1 (tfission)
    Test: tests/hf/test_fission_batch.py
    """
    ex = np.asarray(ex_mev, dtype=np.float64)
    dex = np.asarray(dex_mev, dtype=np.float64)
    m = ex.size
    lo = np.maximum(ex - 0.5 * dex, 0.0)
    hi = np.minimum(ex + 0.5 * dex, exmax_mev)
    tf3 = ladder_transmission(fp, grid, ld, np.concatenate([lo, ex, hi]), options, maxj=maxj,
                              fnorm=fnorm, cache=cache).numpy()
    tfd, tf, tfu = (np.maximum(tf3[k * m:(k + 1) * m], TRANSEPS) for k in range(3))
    explus = np.minimum(exmax_mev, ex + 0.5 * dex)[:, None, None]
    exmin = np.maximum(ex - 0.5 * dex, 0.0)[:, None, None]
    de1 = ex[:, None, None] - exmin
    de2 = explus - ex[:, None, None]
    logd = np.log(tf) - np.log(tfd)
    logu = np.log(tfu) - np.log(tf)
    with np.errstate(divide="ignore", invalid="ignore"):
        c1 = np.where(logd == 0, tf * de1, (tf - tfd) / np.where(logd == 0, 1.0, logd) * de1)
        c2 = np.where(logu == 0, tf * de2, (tfu - tf) / np.where(logu == 0, 1.0, logu) * de2)
        fis = (c1 + c2) / (explus - exmin)
    fis = np.where((explus <= exmin) | (fis <= 10.0 * TRANSEPS), 0.0, fis)
    return np.ascontiguousarray(fis)
