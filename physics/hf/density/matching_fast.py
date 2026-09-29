"""SETB: the level-density matching of `density.matching` without its per-element Python loops,
for the calls where nothing carries a gradient. Every number is the old path's to the bit.

Where the time went (Zr-88 on the Mac M2, 27 residual nuclei): `matching.match` looped over its
energies with ~8 zero-dim torch operations each, and zbrak hands it 101 energies per nucleus;
`_fermi_tables` filled `temprho` and searched `Nstart` element by element through `_fv`; and
`densitycum` built its whole bookkeeping in 0-dim tensors, of which `_ld_build` reads one entry.

Why the bits cannot move:

* `+ - * /` are exact IEEE operations whether one element or a vector is computed, in torch or
  in Python floats (`pol1`'s own fast path already evaluates on Python floats).
* `exp` and `log` stay torch's: torch's vectorised `exp`/`log` return the same bits as its 0-dim
  ones, while libm and numpy differ from them (342 of 5,000 `exp` values on the M2).
* The float32 table index `int(float32(x) / float32(0.1))` is evaluated in float32, and the
  branches (`temp > 0`, `E0save` sentinel, `clamp`) are the same per-element branches as masks.

TALYS: match.f90:1 (match), densitymatch.f90:118-160, densitycum.f90:1 (densitycum)
Test: tests/hf/test_setb.py (bitwise against the loops)
"""

from __future__ import annotations

import numpy as np
import torch
from torch import Tensor

from physics.hf.core.tensors import DTYPE

__all__ = ["match_vec", "temprho_fill", "ncum_at", "no_grad"]


def no_grad(*ts) -> bool:
    """True when none of `ts` (tensors or not) asks for a gradient."""
    return not any(isinstance(t, Tensor) and t.requires_grad for t in ts)


def match_vec(eex: Tensor, logrho: Tensor, temprho: Tensor, E0save: float, NLo: int, NP: int,
              EL: float, EP: float, sentinel: float) -> Tensor:
    """`matching.match`'s condition for every energy of `eex` at once (same shape out).

    TALYS: match.f90:1 (match)
    Test: tests/hf/test_setb.py
    """
    from physics.hf.density.matching import _DEX

    shape = eex.shape
    x = eex.reshape(-1).to(DTYPE)
    xf = x.numpy()
    idx = np.maximum((xf.astype(np.float32) / _DEX).astype(np.int64), 1)
    dEx = float(_DEX)
    it = torch.from_numpy(idx)
    x1 = torch.from_numpy(idx * dEx)
    x2 = torch.from_numpy((idx + 1) * dEx)
    den = x2 - x1
    fac = (x - x1) / den
    t1, t2 = temprho[it], temprho[it + 1]
    temp = t1 + fac * (t2 - t1)
    live = temp > 0.0
    if not bool(live.any()):
        return torch.zeros(shape, dtype=DTYPE)
    l1, l2 = logrho[it], logrho[it + 1]
    rhof = torch.exp(l1 + fac * (l2 - l1))
    safe = torch.where(live, temp, torch.ones_like(temp))
    if E0save == sentinel:
        factor1 = torch.exp(-x / safe)
        factor2 = torch.exp(EP / safe)
        if EL != 0.0:
            factor2 = factor2 - torch.exp(EL / safe)
        term = torch.clamp(safe * rhof * factor1 * factor2, max=1.0e30)
        val = term + NLo - NP
    else:
        val = x - safe * torch.log(safe * rhof) - E0save
    return torch.where(live, val, torch.zeros_like(val)).reshape(shape)


def temprho_fill(raw: Tensor, nEx: int) -> tuple[Tensor, int]:
    """`_fermi_tables`'s descending fill of `temprho` (a value <= 0.1 takes entry i+1) and its
    `Nstart` search, on Python floats.

    TALYS: densitymatch.f90:140-160
    Test: tests/hf/test_setb.py
    """
    r = raw.tolist()
    out = [0.0] * (nEx + 2)
    for k in range(nEx, 0, -1):
        v = r[k - 1]
        out[k] = out[k + 1] if v <= 0.1 else v
    nstart = 1
    for k in range(nEx - 1, 0, -1):
        if out[k] >= out[k + 1]:
            nstart = k + 1
            break
    return torch.tensor(out, dtype=DTYPE), nstart


def ncum_at(edis: Tensor, dens: Tensor, NL: int, index: int) -> float:
    """`densitycum(ld)["Ncum"][index]` on Python floats: Ncum(i) = Ncum(i-1) + dens(i-1) dEx(i-1),
    0 where the level energy is 0, NL at NL.

    TALYS: densitycum.f90:130-150
    Test: tests/hf/test_setb.py
    """
    e = edis.tolist()
    d = dens.tolist()
    ncum = [0.0] * (index + 1)
    for i in range(1, index + 1):
        if e[i] == 0.0:
            continue
        ncum[i] = ncum[i - 1] + d[i - 1] * (e[i] - e[i - 1])
        if i == NL:
            ncum[i] = float(NL)
    return ncum[index]
