"""NATIVEX2 lever `fis2`: the continuum fission transmission through one barrier in C
(`native/nx2_fis2.c`), for the calls where nothing carries a gradient and the barrier has no
rotational band (`hbstate n`, TALYS's default).

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

Task: NATIVEX2 (the speed work; no physics of its own). Acceptance test: `tests/hf/test_nx2_fis2.py`
(each kernel against the torch path it replaces) and the G-NATIVEX2 closeness gate.

Where the time went (cProfile, second runs of U-238 and Th-232, 6.15 s): the bin-ladder fission
widths 0.65 s (`fission_batch_ladder._barrier`: the WKB interpolation of an (energy, triple)
matrix with a `locate` and two table logarithms per call, 0.33 s, and the barrier-density slopes
0.16 s) and the primary compound nucleus's `fission_transmission` 0.32 s (300 `t1barrier` calls,
of which `_log_integrate` 0.22 s). Both are the same sum -- the level density integrated over each
`eintfis` triple, clipped at the energy, times the penetrability at the triple's centre -- so one
kernel serves both: `ladder` for every energy of a bin ladder, `t1` for one energy with the
Hill-Wheeler histograms. The slopes are taken once per barrier grid and kept with it.
`level_densities` builds the barrier grid itself on numpy with the `ld2` table kernel (0.15 s of
small torch operations around it).

The kernel repeats the torch expressions' +, -, *, / in order; libm's exp/log and the order of the
sums over triples may move last bits, so it is held to closeness. Each function returns None when
the kernel is not built, `HF_NX2_FIS2=0`, a barrier carries a rotational band, the grids do not
match, or an input asks for a gradient; the caller then runs its own path.

TALYS routines the kernel computes:
    t1barrier.f90:1 (t1barrier), twkbint.f90:1 (twkbint), thill.f90:1 (thill)
"""

from __future__ import annotations

import weakref

import numpy as np
import torch
from torch import Tensor

from physics.hf.core.constants import talys_constants
from physics.hf.native import nx2

__all__ = ["ladder", "level_densities", "t1"]

_LEVER = "fis2"
_P, _I, _D = nx2.P, nx2.I64, nx2.DBL


def _grad(*ts) -> bool:
    return any(isinstance(t, Tensor) and t.requires_grad for t in ts)


def _kernels():
    coef = nx2.kernel("nx2_fis2_coef", [_P, _P, _I, _I, _P, _P, _P, _P, _P], _I, lever=_LEVER)
    bar = nx2.kernel("nx2_fis2_barrier",
                     [_P, _P, _P, _P, _P, _I, _I, _D, _P, _I, _I, _D, _D, _D, _P, _P, _I, _P, _P,
                      _P, _P, _I], nx2.INT, lever=_LEVER)
    return (coef, bar) if coef is not None and bar is not None else None


#: per barrier grid (keyed by the id of its `rhofis` tensor, with a weak reference that must still
#: resolve to it): {ibar: (elow, emid, eup, A, B)} -- `fission_batch_ladder._coefficients`
_COEF: dict[int, tuple] = {}
#: per WKB result (by the id of its `twkb` tensor): (uwkb, {ibar: contiguous column}) or None when
#: the energy table is not ascending
_WKB: dict[int, tuple] = {}


def _memo(store: dict, t: Tensor, build):
    ent = store.get(id(t))
    if ent is not None and ent[0]() is t:
        return ent[1]
    val = build()
    key = id(t)
    store[key] = (weakref.ref(t, lambda _r, k=key: store.pop(k, None)), val)
    return val


def _coefficients(coef_fn, grid, ibar: int):
    per = _memo(_COEF, grid.rhofis, dict)
    got = per.get(ibar)
    if got is None:
        nb = int(grid.nbintfis[ibar])
        e = np.ascontiguousarray(grid.eintfis_mev[ibar].numpy(), dtype=np.float64)
        r = grid.rhofis[ibar].numpy()
        nj2 = r.shape[1] * r.shape[2]
        r = np.ascontiguousarray(r.reshape(r.shape[0], nj2), dtype=np.float64)
        S = max(len(range(1, nb - 1, 2)), 0)
        elow, emid, eup = np.zeros(S), np.zeros(S), np.zeros(S)
        A, B = np.zeros((S, nj2)), np.zeros((S, nj2))
        if S > 0 and coef_fn(nx2.ptr(e), nx2.ptr(r), nb, nj2, nx2.ptr(elow), nx2.ptr(emid),
                             nx2.ptr(eup), nx2.ptr(A), nx2.ptr(B)) != S:
            return None
        got = per[ibar] = (elow, emid, eup, A, B)
    return got


def _penetrability(fp, ibar: int, deltaw):
    """(mode, bfis, wfis, uwkb, column, nbins) of `barriers._penetrability`, or None."""
    from physics.hf.fission.barriers import barrier_height

    if fp.fismodelx >= 5 and fp.wkb is not None:
        w = fp.wkb
        if _grad(w.uwkb_mev, w.twkb):
            return None

        def build():
            u = np.ascontiguousarray(w.uwkb_mev.numpy(), dtype=np.float64)
            if u.shape[0] < 2 or not bool(np.all(np.diff(u) >= 0.0)):
                return None
            return (u, {})

        tab = _memo(_WKB, w.twkb, build)
        if tab is None:
            return None
        u, cols = tab
        col = cols.get(ibar)
        if col is None:
            t = np.asarray(w.twkb[:, ibar].numpy(), dtype=np.float64)
            with np.errstate(divide="ignore", invalid="ignore"):
                # the column and its logarithms as `_wkb_interp` takes them (clamped at 1e-300)
                col = cols[ibar] = np.ascontiguousarray(
                    np.concatenate([t, np.log(np.maximum(t, 1e-300))]))
        return 1, 0.0, 1.0, u, col, u.shape[0] - 1
    bfis, wfis = barrier_height(fp, ibar, deltaw)
    if _grad(bfis, wfis):
        return None
    return 0, float(bfis), float(wfis), None, None, 0


def _run(fp, grid, ibar: int, eex: np.ndarray, deltaw, maxj: int, collect: bool):
    ks = _kernels()
    if ks is None or not _covered(fp, grid, ibar, deltaw, maxj):
        return None
    pen = _penetrability(fp, ibar, deltaw)
    if pen is None:
        return None
    from physics.hf.fission.barriers import NUMHILL

    coef_fn, bar_fn = ks
    n = eex.shape[0]
    nj2 = (maxj + 1) * 2
    trfis = np.zeros((n, nj2))
    rhof = np.zeros((n, nj2))
    hill = ((np.zeros((nj2, NUMHILL + 1)), np.zeros((nj2, NUMHILL + 1))) if collect
            else (None, None))
    if int(grid.nbintfis[ibar]) < 3:
        return trfis, rhof, hill
    coef = _coefficients(coef_fn, grid, ibar)
    if coef is None:
        return None
    elow, emid, eup, A, B = coef
    mode, bfis, wfis, u, col, nbins = pen
    twopi = float(talys_constants()["twopi"])
    if bar_fn(nx2.ptr(elow), nx2.ptr(emid), nx2.ptr(eup), nx2.ptr(A), nx2.ptr(B), elow.shape[0],
              nj2, float(fp.fecont_mev[ibar]), nx2.ptr(eex), n, mode, bfis, wfis, twopi,
              nx2.ptr(u), nx2.ptr(col), nbins, nx2.ptr(trfis), nx2.ptr(rhof), nx2.ptr(hill[0]),
              nx2.ptr(hill[1]), NUMHILL) != 0:
        return None
    return trfis, rhof, hill


def ladder(fp, grid, ibar: int, eex: Tensor, deltaw, shape) -> Tensor | None:
    """`fission_batch_ladder._barrier`: `t1barrier(...).trfis` at every energy of `eex`,
    `(E, maxj+1, 2)`, or None. The (energy, triple) weights come from C and the two contractions
    with the slopes stay the matrix products the torch code takes (a scalar loop over
    energy x triple x (J, parity) is slower than them).

    TALYS: t1barrier.f90:1 (t1barrier)
    Test: tests/hf/test_nx2_fis2.py
    """
    if _grad(eex):
        return None
    wfn = nx2.kernel("nx2_fis2_ladder_weights",
                     [_P, _P, _P, _I, _D, _P, _I, _I, _D, _D, _D, _P, _P, _I, _P, _P], nx2.INT,
                     lever=_LEVER)
    ks = _kernels()
    maxj = int(shape[0]) - 1
    if wfn is None or ks is None or not _covered(fp, grid, ibar, deltaw, maxj):
        return None
    pen = _penetrability(fp, ibar, deltaw)
    if pen is None:
        return None
    e = np.ascontiguousarray(eex.detach().numpy().reshape(-1), dtype=np.float64)
    E = e.shape[0]
    if int(grid.nbintfis[ibar]) < 3:
        return torch.zeros((E, *shape), dtype=torch.float64)
    coef = _coefficients(ks[0], grid, ibar)
    if coef is None:
        return None
    elow, emid, eup, A, B = coef
    S = elow.shape[0]
    mode, bfis, wfis, u, col, nbins = pen
    W1, W2 = np.zeros((E, S)), np.zeros((E, S))
    if wfn(nx2.ptr(elow), nx2.ptr(emid), nx2.ptr(eup), S, float(fp.fecont_mev[ibar]),
           nx2.ptr(e), E, mode, bfis, wfis, float(talys_constants()["twopi"]), nx2.ptr(u),
           nx2.ptr(col), nbins, nx2.ptr(W1), nx2.ptr(W2)) != 0:
        return None
    tr = torch.from_numpy(W1) @ torch.from_numpy(A) + torch.from_numpy(W2) @ torch.from_numpy(B)
    return tr.reshape(E, *shape)


def _covered(fp, grid, ibar: int, deltaw, maxj: int) -> bool:
    return (not _grad(grid.rhofis, grid.eintfis_mev, deltaw, fp.fbarrier_mev, fp.fwidth_mev,
                      fp.fecont_mev)
            and fp.rotational[ibar].n == 0 and grid.rhofis.shape[2] == maxj + 1)


def t1(fp, grid, ibar: int, eex, deltaw, maxj: int, collect_hill: bool):
    """`barriers.t1barrier` at one energy as a `BarrierTransmission`, or None.

    TALYS: t1barrier.f90:1 (t1barrier)
    Test: tests/hf/test_nx2_fis2.py
    """
    from physics.hf.fission.barriers import NUMHILL, BarrierTransmission

    if _grad(eex):
        return None
    e = np.array([float(eex)], dtype=np.float64)
    got = _run(fp, grid, ibar, e, deltaw, maxj, collect_hill)
    if got is None:
        return None
    trfis, rhof, (ta, ra) = got
    shape = (maxj + 1, 2)
    return BarrierTransmission(torch.from_numpy(trfis.reshape(shape)),
                              torch.from_numpy(rhof.reshape(shape)),
                              None if ta is None else torch.from_numpy(
                                  ta.reshape(*shape, NUMHILL + 1)),
                              None if ra is None else torch.from_numpy(
                                  ra.reshape(*shape, NUMHILL + 1)))


def level_densities(fp, ld, exfis_top_mev: float, odd: int, maxj: int):
    """`transmission.fission_level_densities` on numpy with every barrier's densities from its
    table in one C call (the energy grid is the same arithmetic, to the bit), or None when a
    barrier has no table or anything asks for a gradient.

    TALYS: densprepare.f90:399-441 (densprepare)
    Test: tests/hf/test_nx2_fis2.py
    """
    from physics.hf.density.ld2_nx2 import table_grid
    from physics.hf.density.parameters import NUMJ
    from physics.hf.fission.transmission import DEXMIN, NUMBINFIS, FissionLevelDensities
    from physics.hf.fission.wkb import NUMBAR

    # CENGFIS: the full signature; a one-argument binding of the same ctypes function object reset
    # its argtypes for `_coefficients` whenever it was bound after it (a bus error in the test)
    if _kernels() is None or ld.ldmodel <= 3:
        return None
    if _grad(fp.fecont_mev, ld.ctable, ld.ptable_mev):
        return None
    nb_out = [0] * (NUMBAR + 1)
    per_bar: list = [None] * (NUMBAR + 1)
    nmax = 1
    for ibar in range(1, int(fp.nfisbar) + 1):
        if ibar > NUMBAR:
            return None
        elowest = float(fp.fecont_mev[ibar])
        exfis = exfis_top_mev - elowest
        nbin = NUMBINFIS // 2
        if exfis <= 0.0:
            nb_out[ibar] = nbin
            continue
        if not ld.has_table(ibar) or _grad(ld.tables[ibar].ldtable_per_mev):
            return None
        dex = exfis / nbin
        if dex < DEXMIN:
            nbin = max(int(exfis / DEXMIN), 1)
            dex = exfis / nbin
        edges = elowest + dex * np.arange(nbin, dtype=np.float64)
        e = np.zeros(2 * nbin + 1)
        e[1::2] = edges
        e[2::2] = edges + 0.5 * dex
        e[2 * nbin] = exfis + elowest  # densprepare.f90:439
        nb_out[ibar] = 2 * nbin
        nmax = max(nmax, 2 * nbin)
        per_bar[ibar] = e
    grids = np.zeros((NUMBAR + 1, nmax + 1))
    rhos = np.zeros((NUMBAR + 1, nmax + 1, maxj + 1, 2))
    jidx = np.minimum(np.floor(np.arange(maxj + 1, dtype=np.float64) + 0.5 * odd).astype(np.int64),
                      NUMJ - 1)
    for ibar, e in enumerate(per_bar):
        if e is None:
            continue
        n = nb_out[ibar]
        grids[ibar, : e.shape[0]] = e
        got = table_grid(ld.tables[ibar], ld.ctable[ibar], ld.ptable_mev[ibar], e[1 : n + 1], jidx,
                         (0, 1))
        if got is None:
            return None
        rhos[ibar, 1 : n + 1] = got
    return FissionLevelDensities(tuple(nb_out), torch.from_numpy(grids), torch.from_numpy(rhos))
