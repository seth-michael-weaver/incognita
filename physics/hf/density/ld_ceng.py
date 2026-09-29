"""CENGLD (ROUTE100 WP6): the level-density set-up of a cascade nucleus in one C call each
(`native/ld.c`, built into `libnx2`): `densitymatch` with its Fermi-gas tables, matching root,
passes and fallbacks, and `rhogrid` with rho(J) evaluated only up to each bin's maxJ.

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

Task: CENGLD (speed; no physics of its own). Acceptance test: `tests/hf/test_cengld.py` (each
kernel against the path it replaces) and `harness/cengld_ld.py` (every LD array of the chart path
on 200+ cascade nuclei, <= 1e-13).

Where it applies: the nuclei NATIVEX2's `ld` lever carries (`ld_nx2._par`: ldmodel 1, no collective
enhancement, no table, nothing on the autograd graph) and no fission barrier. Everything else, and
`HF_NX2_CENGLD=0`, runs the existing path. The level-density parameters come from the `LDNucleus`
`densitypar` built, so a fit's `aadjust` (PARAMWIRE's `with_aadjust` Params) reaches the kernels
through `alev`/`alimit` like every other parameter.

Where the time went (MERGEZ, Mac chart cost map, 482 x 20): the level-density stage 10.3 CPU-s,
`rhogrid_of` 5.3 of it (45,730 calls; 1.6 in the kernel), `_ld_of` 3.3 (12,677 builds:
`densitypar_floats` ~2, `densitymatch` ~0.5 of zero-dim torch operations around three C calls).

TALYS routines: densitymatch.f90:1 (densitymatch), matching.f90:1 (matching), match.f90:1,
zbrak.f90:1, rtbis.f90:1, locate.f90:1, pol1.f90:1, densitycum.f90:130-150, exgrid.f90:241-285.
"""

from __future__ import annotations

import os
from dataclasses import replace
from functools import lru_cache

import numpy as np
import torch

from physics.hf.core.tensors import DTYPE
from physics.hf.native import nx2

__all__ = ["densitymatch_fast", "ignatyuk", "rhogrid", "spec_rows", "spincut"]

_P, _D = nx2.P, nx2.DBL
_DEX = np.float32(0.1)


def _on() -> bool:
    """`HF_NX2_CENGLD=0` (or NATIVEX2's `HF_NX2_LD=0`) turns the lever off, read at every call."""
    env = os.environ
    return env.get("HF_NX2_CENGLD", "1") != "0" and env.get("HF_NX2_LD", "1") != "0"


def _kernel(name: str, args: list):
    if not _on():
        return None
    return nx2.kernel(name, args, nx2.INT, lever="ld")


@lru_cache(maxsize=64)
def _light(Z: int, A: int) -> tuple:
    from physics.hf.density.matching import _ctm_light

    d = _ctm_light(Z, A)
    return tuple((1.0, float(d[k])) if k in d else (0.0, 0.0) for k in ("T", "E0", "Exmatch"))


def densitymatch_fast(ld, flagldglobal: bool, flagctmglob: bool, xacc: float):
    """`matching.densitymatch(ld, ...)` for a nucleus the kernel carries, or None.

    TALYS: densitymatch.f90:1 (densitymatch)
    Test: tests/hf/test_cengld.py
    """
    if ld.nfisbar != 0 or ld.ldmodel in (2, 3) or ld.has_table(0):
        return None
    fn = _kernel("ceng_ld_match", [_P, _P, _P])
    if fn is None:
        return None
    from physics.hf.density.ld_nx2 import _par
    from physics.hf.density.parameters import SENTINEL, _ign_floats, _ld_memo

    par = _par(ld)
    if par is None:
        return None
    A = ld.A
    nEx = int(np.float32(20.0 + 300.0 / A) / _DEX)
    nlow, ntop = ld.Nlow[0], ld.Ntop[0]
    xadj, tadj, e0adj, t0, e00, ex0, el, ep = torch.cat([
        ld.Exmatchadjust[:1], ld.Tadjust[:1], ld.E0adjust[:1], ld.T_mev[:1], ld.E0_mev[:1],
        ld.Exmatch_mev[:1], ld.edis_mev[nlow:nlow + 1], ld.edis_mev[ntop:ntop + 1]]).tolist()
    ign = _ign_floats(ld, 0)  # delta, alimit, gammald, deltaW[0], ...
    (lt_on, lt), (le_on, le), (lx_on, lx) = _light(ld.Z, A) if A <= 18 else ((0.0, 0.0),) * 3
    m = np.array([
        A, nEx, float(bool(flagldglobal)), float(bool(flagctmglob)), float(bool(ld.ldparexist)),
        float(bool(ld.flagcol)), ign[2], ign[3], xadj, tadj, e0adj, t0, e00, ex0,
        lt_on, lt, le_on, le, lx_on, lx, nlow, ntop, el, ep, float(xacc), SENTINEL,
    ], dtype=np.float64)
    out = np.zeros(3)
    if fn(par.ctypes.data, m.ctypes.data, out.ctypes.data) != 0:
        return None
    T, E0, Ex = out.tolist()
    new = replace(ld, T_mev=torch.tensor([T], dtype=DTYPE), E0_mev=torch.tensor([E0], dtype=DTYPE),
                  Exmatch_mev=torch.tensor([Ex], dtype=DTYPE), matched=True)
    # what `ld_nx2._par` reads of the new record and did not change: its gradient check (the
    # three new tensors are fresh) and ignatyuk's scalars; the spin cutoff's read Exmatch
    memo = _ld_memo(new)
    memo["nograd"] = True
    memo[("ign", 0)] = ign
    return new


_RHOGRID = None
_IGN = None
_SC = None
_SPEC = None


def rhogrid(par: np.ndarray, A: int, ex_mev, dex_mev, maxj, nlast: int, numj: int):
    """`ld_nx2.rhogrid`'s result from `ceng_ld_rhogrid` (bit-identical), or None. The caller has
    already returned the all-zero result of a grid with no continuum bin.

    TALYS: exgrid.f90:241-285 (exgrid)
    Test: tests/hf/test_cengld.py
    """
    global _RHOGRID
    fn = _RHOGRID
    if fn is None:
        fn = _RHOGRID = _kernel("ceng_ld_rhogrid", [_P, _P, _P, _P, nx2.I64, nx2.I64, nx2.I64, _D,
                                                    _P])
        if fn is None:
            return None
    if not _on():
        return None
    n = len(ex_mev)
    ex = np.ascontiguousarray(ex_mev, dtype=np.float64)
    dex = np.ascontiguousarray(dex_mev, dtype=np.float64)
    mj = np.ascontiguousarray(maxj, dtype=np.int64)
    if dex.shape[0] < n or mj.shape[0] < n:
        return None
    out = np.zeros((n, numj + 1, 2))
    fn(par.ctypes.data, ex.ctypes.data, dex.ctypes.data, mj.ctypes.data, nlast, n, numj,
       0.5 * (A % 2), out.ctypes.data)
    return out


def spec_rows(ld, A: int, ex_mev: np.ndarray, dex_mev: np.ndarray, n: int, nlast: int,
              parts, numj: int):
    """CENGLD2: (maxJ, rhogrid) of one cascade nucleus's grid from `ceng_ld_spec` -- what
    `feeding.Cascade.spec` formed with `_maxj_of` and `dens_reference.rhogrid_of`, in one C call on
    the record's floats -- or None (the caller runs those two). `parts` makes
    `feeding._spincut_parts(ld)`, kept with the record's floats.

    TALYS: exgrid.f90:199-285 (exgrid)
    Test: tests/hf/test_cengld2.py
    """
    if not _on():
        return None
    if nlast + 1 >= n:  # no continuum bin: numJ everywhere and no rows (`rhogrid_of`'s zeros)
        return np.full(n, numj, np.int64), np.zeros((n, numj + 1, 2))
    global _SPEC, _PAR, _MEMO
    fn = _SPEC
    if fn is None:
        fn = _SPEC = _kernel("ceng_ld_spec", [_P, _P, _P, _P, nx2.I64, nx2.I64, nx2.I64, nx2.I64,
                                              _P, _P])
        if fn is None:
            return None
        from physics.hf.density.ld_nx2 import _par
        from physics.hf.density.parameters import _ld_memo

        _PAR, _MEMO = _par, _ld_memo
    par = _PAR(ld)
    if par is None:
        return None
    memo = _MEMO(ld)
    sc = memo.get("ceng_spec_sc")
    if sc is None:
        sc = memo["ceng_spec_sc"] = np.array([float(x) for x in parts(ld)], dtype=np.float64)
    ex = np.ascontiguousarray(ex_mev[:n], dtype=np.float64)
    dex = np.ascontiguousarray(dex_mev[:n], dtype=np.float64)
    maxj = np.empty(n, np.int64)
    out = np.zeros((n, numj + 1, 2))
    if fn(par.ctypes.data, sc.ctypes.data, ex.ctypes.data, dex.ctypes.data, nlast, n, numj, A,
          maxj.ctypes.data, out.ctypes.data) != 0:
        return None
    return maxj, out


_PAR = _MEMO = None


def _floats(ld, key: tuple, make) -> np.ndarray:
    from physics.hf.density.parameters import _ld_memo

    memo = _ld_memo(ld)
    got = memo.get(key)
    if got is None:
        got = memo[key] = make()
    return got


def ignatyuk(ld, eex: np.ndarray, ibar: int):
    """`parameters._ignatyuk_fast`'s array result as a tensor, from `ceng_ld_ignatyuk`, or None.

    TALYS: ignatyuk.f90:1 (ignatyuk)
    Test: tests/hf/test_cengld.py
    """
    global _IGN
    fn = _IGN
    if fn is None:
        fn = _IGN = _kernel("ceng_ld_ignatyuk", [_P, _P, nx2.I64, _P])
        if fn is None:
            return None
    if not _on():
        return None
    from physics.hf.density.parameters import _ign_floats

    f = _floats(ld, ("ceng_ign", ibar), lambda: np.array(_ign_floats(ld, ibar), dtype=np.float64))
    x = np.ascontiguousarray(eex, dtype=np.float64)
    out = np.empty(x.shape)
    fn(f.ctypes.data, x.ctypes.data, x.size, out.ctypes.data)
    return torch.from_numpy(out)


def spincut(ld, ald, eex: np.ndarray, ibar: int, ipop: int, rspincutff: float):
    """`parameters._spincut_fast`'s array result as a tensor, from `ceng_ld_spincut`, or None
    (`ald` neither a float nor an array of `eex`'s shape).

    TALYS: spincut.f90:1 (spincut)
    Test: tests/hf/test_cengld.py
    """
    global _SC
    fn = _SC
    if fn is None:
        fn = _SC = _kernel("ceng_ld_spincut", [_P, nx2.I64, nx2.I64, _P, nx2.I64, _P, nx2.I64, _P])
        if fn is None:
            return None
    if not _on():
        return None
    from physics.hf.density.parameters import _sc_floats

    x = np.ascontiguousarray(eex, dtype=np.float64)
    if isinstance(ald, float):
        a = np.array([ald])
    else:
        a = np.ascontiguousarray(ald, dtype=np.float64)
        if a.shape != x.shape:
            return None
    sc = _sc_floats(ld, ibar, ipop, rspincutff)
    f = _floats(ld, ("ceng_sc", ibar, ipop, float(rspincutff)), lambda: np.array(
        [sc[0], sc[1], sc[2], sc[3], sc[4], 0.0 if sc[5] is None else sc[5], sc[6]]))
    out = np.empty(x.shape)
    fn(f.ctypes.data, int(ld.spincutmodel == 1), int(sc[5] is not None), a.ctypes.data, a.size,
       x.ctypes.data, x.size, out.ctypes.data)
    return torch.from_numpy(out)
