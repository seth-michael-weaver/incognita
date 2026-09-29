"""NATIVEX2 lever `ld2`: the tabulated level densities (ldmodel >= 4, the default above A = 215,
and every fission-barrier table) in C (`native/nx2_ld2.c`), for the calls where nothing carries a
gradient.

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

Task: NATIVEX2 (the speed work; no physics of its own). Acceptance test: `tests/hf/test_nx2_ld2.py`
(each kernel against the torch path it replaces) and the G-NATIVEX2 closeness gate.

Where the time went (cProfile, second runs of Er-166, Lu-175, U-238, Th-232, 15.9 s): `density`'s
table branch 1.10 s over 1,272 calls -- `_table_interp`'s locate (a `searchsorted` and four
`where`s), two gathers, two logs and an exp per call -- of which 1.01 s under
`fission.transmission.fission_level_densities` and 0.16 s under `rhogrid_of`; and
`tables.density_table` 0.48 s over 141 calls (the per-row Python arithmetic of the rows it
reads). The deformed rare earths (ldmodel 1, no collective enhancement by default below A = 216)
already run on the `ld` kernels.

The kernels do the torch expressions' +, -, *, / in their order (contraction off); libm's exp/log
may differ from torch's in a last bit, so they are held to closeness. Each function returns None
when the kernel is not built, `HF_NX2_LD2=0`, or an input asks for a gradient; the caller then
runs its own path.

TALYS routines the kernels compute:
    density.f90:1 (density), locate.f90:1 (locate), exgrid.f90:241-285 (exgrid),
    densprepare.f90:399-441 (densprepare, the fission-barrier grid)

`tables.density_table` (no C) does its per-row arithmetic on whole columns of records parsed once
per file and mass (`tables._table_blocks`), to the bit.
"""

from __future__ import annotations

import numpy as np
import torch
from torch import Tensor

from physics.hf.native import nx2

__all__ = ["table_density", "table_grid", "fission_rhofis", "table_rhogrid", "enabled"]

_LEVER = "ld2"
_P, _I, _D = nx2.P, nx2.I64, nx2.DBL


def enabled() -> bool:
    """`HF_NX2_LD2` is not 0 (the numpy-only parts of the lever read this; the kernels read it
    through `nx2.kernel`)."""
    import os

    return os.environ.get("HF_NX2_LD2", "1") != "0"


def _k(name: str, args: list, res=nx2.INT):
    return nx2.kernel(name, args, res, lever=_LEVER)


def _grad(*ts) -> bool:
    return any(isinstance(t, Tensor) and t.requires_grad for t in ts)


def _np(t) -> np.ndarray:
    a = t.detach().numpy() if isinstance(t, Tensor) else np.asarray(t)
    return np.ascontiguousarray(a, dtype=np.float64)


def table_density(tab, ct, pt, eex: Tensor, J: Tensor, parity: int,
                  numj_cap: int) -> Tensor | None:
    """`density.models.density`'s table branch for `eex` and `J` already broadcast to one shape:
    rho(Ex, J, parity) [MeV^-1] with the table spin index min(int(J), numj_cap), or None.

    TALYS: density.f90:1 (density)
    Test: tests/hf/test_nx2_ld2.py
    """
    if _grad(ct, pt, eex, J, tab.ldtable_per_mev):
        return None
    fn = _k("nx2_ld2_table_density", [_P, _I, _D, _P, _I, _D, _D, _P, _P, _I, _I, _P])
    if fn is None or eex.dtype != torch.float64 or eex.device.type != "cpu":
        return None
    from physics.hf.density.tables import edens_grid

    edens = _edens(edens_grid)
    tbl = _table_array(tab)
    e = np.ascontiguousarray(eex.numpy().reshape(-1))
    jj = np.minimum(np.floor(J.detach().numpy().reshape(-1)).astype(np.int64), numj_cap)
    jj = np.ascontiguousarray(jj)
    out = np.empty(e.shape[0])
    if fn(nx2.ptr(edens), int(tab.nendens), float(tab.Edensmax_mev), nx2.ptr(tbl), tbl.shape[1],
          float(ct), float(pt), nx2.ptr(e), nx2.ptr(jj), e.shape[0], 0 if parity == -1 else 1,
          nx2.ptr(out)) != 0:
        return None
    return torch.from_numpy(out.reshape(eex.shape))


def table_grid(tab, ct, pt, e, jidx: np.ndarray, pcols: tuple[int, ...]) -> np.ndarray | None:
    """rho(e[a], J with table spin index jidx[b], parity column pcols[c]) as (len(e), len(jidx),
    len(pcols)): `density`'s table branch on the outer product of an energy column and a spin row
    for one or two parities, or None. `e` is a float64 array or tensor (no gradient).

    TALYS: density.f90:1 (density)
    Test: tests/hf/test_nx2_ld2.py
    """
    if _grad(ct, pt, e, tab.ldtable_per_mev):
        return None
    fn = _k("nx2_ld2_table_grid", [_P, _I, _D, _P, _I, _D, _D, _P, _I, _P, _I, _P, _I, _P])
    if fn is None:
        return None
    from physics.hf.density.tables import edens_grid

    ee = np.ascontiguousarray(e.numpy() if isinstance(e, Tensor) else e, dtype=np.float64)
    ee = ee.reshape(-1)
    jj = np.ascontiguousarray(jidx, dtype=np.int64)
    pc = np.ascontiguousarray(pcols, dtype=np.int64)
    tbl = _table_array(tab)
    out = np.empty((ee.shape[0], jj.shape[0], pc.shape[0]))
    if fn(nx2.ptr(_edens(edens_grid)), int(tab.nendens), float(tab.Edensmax_mev), nx2.ptr(tbl),
          tbl.shape[1], float(ct), float(pt), nx2.ptr(ee), ee.shape[0], nx2.ptr(jj), jj.shape[0],
          nx2.ptr(pc), pc.shape[0], nx2.ptr(out)) != 0:
        return None
    return out


def fission_rhofis(ld, ibar: int, ee: Tensor, jgrid: Tensor) -> Tensor | None:
    """`fission_level_densities`' two `density(ld, ee, jgrid, parity, ibar)` columns stacked on
    the parity axis (-1, +1), (len(ee), len(jgrid), 2), in one call; None when the barrier has no
    table or a gradient is present (the caller keeps its loop).

    TALYS: densprepare.f90:399-441 (densprepare), density.f90:1 (density)
    Test: tests/hf/test_nx2_ld2.py
    """
    if ld.ldmodel <= 3 or not ld.has_table(ibar) or _grad(ee, jgrid):
        return None
    from physics.hf.density.parameters import NUMJ

    jidx = np.minimum(np.floor(jgrid.detach().numpy().reshape(-1)).astype(np.int64), NUMJ - 1)
    got = table_grid(ld.tables[ibar], ld.ctable[ibar], ld.ptable_mev[ibar], ee, jidx, (0, 1))
    return None if got is None else torch.from_numpy(got)


def table_rhogrid(ld, ex_mev, dex_mev, maxj, nlast: int, numj: int) -> np.ndarray | None:
    """`dens_reference.rhogrid_of`'s numpy result for a nucleus with a ground-state table, both
    parity columns from the table, or None.

    TALYS: exgrid.f90:241-285 (exgrid), density.f90:1 (density)
    Test: tests/hf/test_nx2_ld2.py
    """
    if not ld.has_table(0) or ld.ldmodel <= 3:
        return None
    tab = ld.tables[0]
    ct, pt = ld.ctable[0], ld.ptable_mev[0]
    if _grad(ct, pt, tab.ldtable_per_mev):
        return None
    fn = _k("nx2_ld2_table_rhogrid",
            [_P, _I, _D, _P, _I, _I, _D, _D, _P, _P, _P, _P, _I, _I, _P])
    if fn is None:
        return None
    from physics.hf.density.parameters import NUMJ
    from physics.hf.density.tables import edens_grid

    n = len(ex_mev)
    out = np.zeros((n, numj + 1, 2))
    if nlast + 1 >= n:
        return out
    ex = np.ascontiguousarray(ex_mev, dtype=np.float64)
    dex = np.ascontiguousarray(dex_mev, dtype=np.float64)
    mj = np.ascontiguousarray(maxj, dtype=np.int64)
    if dex.shape[0] < n or mj.shape[0] < n:
        return None
    sel = np.zeros(n, np.uint8)
    sel[nlast + 1:] = mj[nlast + 1: n] >= 0
    edens = _edens(edens_grid)
    tbl = _table_array(tab)
    if fn(nx2.ptr(edens), int(tab.nendens), float(tab.Edensmax_mev), nx2.ptr(tbl), tbl.shape[1],
          NUMJ - 1, float(ct), float(pt), nx2.ptr(ex), nx2.ptr(dex), nx2.ptr(mj), nx2.ptr(sel),
          n, numj, nx2.ptr(out)) != 0:
        return None
    return out


_EDENS: list = []


def _edens(edens_grid) -> np.ndarray:
    if not _EDENS:
        _EDENS.append(np.ascontiguousarray(edens_grid().numpy(), dtype=np.float64))
    return _EDENS[0]


#: the contiguous float64 ldtable of a DensityTable by id, with a weak reference to the table's
#: tensor that must still resolve (a recycled id never hits)
_TBL: dict[int, tuple] = {}


def _table_array(tab) -> np.ndarray:
    import weakref

    t = tab.ldtable_per_mev
    ent = _TBL.get(id(t))
    if ent is not None and ent[0]() is t:
        return ent[1]
    a = _np(t)
    key = id(t)
    _TBL[key] = (weakref.ref(t, lambda _r, k=key: _TBL.pop(k, None)), a)
    return a
