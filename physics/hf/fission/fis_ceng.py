"""CENGFIS (ROUTE100 WP7): the chart's fission transmissions from one C pass per barrier grid
(`native/fission.c`), for nuclei whose barriers all have density tables and no rotational band
(TALYS's defaults for every fissioning chart nucleus).

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

Task: CENGFIS (the speed work; no physics of its own). Acceptance test: `tests/hf/test_cengfis.py`
(each entry against the path it replaces) and the CENGFIS gates (`docs/results/hf-cengfis.md`).

NATIVEX2's `fis2`/`ld2` levers already ran the arithmetic in C, but as five calls per grid with
their arrays passed through Python: `level_densities` built the `rhofis` tensor (41 x 2 densities
at ~1000 points, the table's logarithms taken again per call), `nx2_fis2_coef` took a log() of
every one of them, `ladder` searched the WKB table for every (energy, triple), and the hump
combination and the bin integration ran as ~40 numpy/torch operations. Here:

* `ceng_fis_grid` walks the grid once and emits the triple slopes directly, bit-identical to
  `level_densities` + `nx2_fis2_coef`. A parity column the table holds equal to the other is
  copied (up to all of a barrier's second parity), and the 1e-30 floor's logarithm is taken once.
  (Logarithms taken from the exponent the density was built from instead of a log() were tried:
  2e-8 on Ra-223 (n,f), because a slope divides by the difference of two neighbouring logs.)
* `ceng_fis_weights` walks the WKB index down the triples instead of searching for it (the same
  index); the two contractions with the slopes stay torch's matrix products, as in `fis2`.
* `ceng_fis_bins` combines the humps and integrates each mother bin's triple in one call.
* The primary compound nucleus's `tfission` at `Exinc` with `dExinc = 0` evaluates the same
  barrier sums three times; it is taken once, and `denfis`/`gamfis`/`taufis`, which
  `compound_target` never reads, are not built.

The table logarithms are taken once per table. Each function returns None when the kernels are not
built, `HF_NX2_CENGFIS=0` (or NATIVEX2's `HF_NX2_FIS2=0`), a barrier has no table or a rotational
band, `class2`/`fispartdamp` is on, or anything carries a gradient; the caller then runs its own
path.

TALYS routines the kernels compute:
    densprepare.f90:399-441 (densprepare), density.f90:1 (density), t1barrier.f90:1 (t1barrier),
    twkbint.f90:1 (twkbint), thill.f90:1 (thill), tfission.f90:1 (tfission),
    compound.f90:120-147 (compound)
"""

from __future__ import annotations

import os
import weakref

import numpy as np
import torch

from physics.hf.native import nx2

__all__ = ["grid_coefficients", "ladder_widths", "target_transmission"]

_P, _I, _D = nx2.P, nx2.I64, nx2.DBL
#: grids kept per nucleus: the ladder and the primary compound nucleus each read their grid once
_KEEP = 2


def _on() -> bool:
    env = os.environ
    return env.get("HF_NX2_CENGFIS", "1") != "0" and env.get("HF_NX2_FIS2", "1") != "0"


def _kernels():
    if not _on():
        return None
    ks = (nx2.kernel("ceng_fis_grid", [_P, _I, _D, _P, _P, _I, _D, _D, _D, _D, _P, _I, _D, _I, _P,
                                       _P, _P, _P, _P, _I], _I),
          nx2.kernel("ceng_fis_weights", [_P, _P, _P, _I, _D, _P, _I, _I, _D, _D, _D, _P, _P, _I,
                                          _P, _P], nx2.INT),
          nx2.kernel("ceng_fis_bins", [_P, _P, _P, _P, _I, _I, _D, _P, _P, _D, _P], nx2.INT),
          nx2.kernel("ceng_fis_log_table", [_P, _I, _P], None))
    return None if any(k is None for k in ks) else ks


def _grad(*ts) -> bool:
    return any(isinstance(t, torch.Tensor) and t.requires_grad for t in ts)


_LG: dict[int, tuple] = {}


def _log_table(fn, tab) -> tuple[np.ndarray, np.ndarray]:
    from physics.hf.density.ld2_nx2 import _table_array

    t = tab.ldtable_per_mev
    ent = _LG.get(id(t))
    if ent is not None and ent[0]() is t:
        return ent[1]
    a = _table_array(tab)
    lg = np.empty_like(a)
    fn(nx2.ptr(a), a.size, nx2.ptr(lg))
    key = id(t)
    _LG[key] = (weakref.ref(t, lambda _r, k=key: _LG.pop(k, None)), (a, lg))
    return a, lg


def _covered(fp, ld, options) -> bool:
    nb = int(fp.nfisbar)
    if nb not in (1, 2, 3) or options.flagclass2 or options.flagfispartdamp or ld.ldmodel <= 3:
        return False
    if _grad(fp.fecont_mev, fp.fbarrier_mev, fp.fwidth_mev, ld.ctable, ld.ptable_mev,
             ld.deltaW_mev):
        return False
    return all(fp.rotational[ibar].n == 0 for ibar in range(1, nb + 1))


def grid_coefficients(chain, n, exfis_top_mev: float, nJ: int | None = None):
    """`{ibar: (elow, emid, eup, A, B) or None}` of the nucleus's barrier grid at `exfis_top_mev`
    (`fis2_nx2._coefficients` of `fis2_nx2.level_densities`' grid; None: no triples) for the
    first `nJ` spins (default all `maxj + 1`), or None when not covered.

    TALYS: densprepare.f90:399-441 (densprepare), t1barrier.f90:151-168 (t1barrier)
    Test: tests/hf/test_cengfis.py
    """
    ks = _kernels()
    if ks is None or not _covered(n.fp, n.ld, chain.o):
        return None
    top = round(float(exfis_top_mev), 9)
    nJ = chain.maxj + 1 if nJ is None else min(int(nJ), chain.maxj + 1)
    key = (top, nJ)
    store = n.__dict__.setdefault("_ceng_coef", {})
    got = store.get(key)
    if got is not None:
        return got
    from physics.hf.density.ld2_nx2 import _edens
    from physics.hf.density.parameters import NUMJ
    from physics.hf.density.tables import edens_grid
    from physics.hf.fission.transmission import DEXMIN, NUMBINFIS

    grid_fn, _, _, log_fn = ks
    fp, ld = n.fp, n.ld
    jidx = np.minimum(np.floor(np.arange(nJ, dtype=np.float64) + 0.5 * n.odd).astype(np.int64),
                      NUMJ - 1)
    edens = _edens(edens_grid)
    got = {}
    for ibar in range(1, int(fp.nfisbar) + 1):
        elowest = float(fp.fecont_mev[ibar])
        exfis = top - elowest
        if exfis > 0.0 and (not ld.has_table(ibar) or _grad(ld.tables[ibar].ldtable_per_mev)):
            return None
        smax = NUMBINFIS // 2  # nbin <= numbinfis/2, so at most numbinfis/2 - 1 triples
        elow, emid, eup = np.empty(smax), np.empty(smax), np.empty(smax)
        A, B = np.empty((smax, 2 * nJ)), np.empty((smax, 2 * nJ))
        if exfis > 0.0:
            tab = ld.tables[ibar]
            tbl, lg = _log_table(log_fn, tab)
            ct, pt = float(ld.ctable[ibar]), float(ld.ptable_mev[ibar])
            nendens, emax, nj = int(tab.nendens), float(tab.Edensmax_mev), tbl.shape[1]
        else:
            tbl = lg = None
            ct = pt = emax = 0.0
            nendens = nj = 0
        S = grid_fn(nx2.ptr(edens), nendens, emax, nx2.ptr(tbl), nx2.ptr(lg), nj, ct, pt, elowest,
                    top, nx2.ptr(jidx), nJ, DEXMIN, NUMBINFIS, nx2.ptr(elow), nx2.ptr(emid),
                    nx2.ptr(eup), nx2.ptr(A), nx2.ptr(B), smax)
        if S < 0:
            return None
        got[ibar] = None if S == 0 else (elow[:S], emid[:S], eup[:S], np.ascontiguousarray(A[:S]),
                                         np.ascontiguousarray(B[:S]))
    while len(store) >= _KEEP:
        store.pop(next(iter(store)))
    store[key] = got
    return got


def _pen(fp, ld, ibar: int):
    from physics.hf.fission.fis2_nx2 import _penetrability

    return _penetrability(fp, ibar, ld.deltaW_mev)


def ladder_widths(chain, n, ex_mev: np.ndarray, dex_mev: np.ndarray, exmax_mev: float,
                  exfis_top_mev: float, fnorm: float, nJ: int) -> np.ndarray | None:
    """`fission_batch_ladder.ladder_bin_widths` of the nucleus's grid at `exfis_top_mev` for the
    first `nJ` spins, `(bins, nJ, 2)`, or None when not covered. The cascade reads only the spins
    up to its mother bins' `maxj` (`NucleusWidths.nj`), and every (J, parity) column is computed
    on its own, so the columns above are not computed rather than cut off afterwards.

    TALYS: tfission.f90:1 (tfission), compound.f90:120-147 (compound)
    Test: tests/hf/test_cengfis.py
    """
    co = grid_coefficients(chain, n, exfis_top_mev, nJ)
    if co is None:
        return None
    from physics.hf.core.constants import talys_constants

    _, w_fn, bins_fn, _ = _kernels()
    fp = n.fp
    nJ = min(int(nJ), chain.maxj + 1)
    nj2 = 2 * nJ
    ex = np.ascontiguousarray(ex_mev, dtype=np.float64)
    dex = np.ascontiguousarray(dex_mev, dtype=np.float64)
    m = ex.size
    lo = np.maximum(ex - 0.5 * dex, 0.0)
    hi = np.minimum(ex + 0.5 * dex, exmax_mev)
    eex = np.ascontiguousarray(np.concatenate([lo, ex, hi]))
    E = eex.size
    twopi = float(talys_constants()["twopi"])
    ts = [None, None, None]
    for ibar in range(1, int(fp.nfisbar) + 1):
        c = co[ibar]
        if c is None:
            ts[ibar - 1] = np.zeros((E, nj2))
            continue
        pen = _pen(fp, n.ld, ibar)
        if pen is None:
            return None
        elow, emid, eup, A, B = c
        S = elow.shape[0]
        mode, bfis, wfis, u, col, nbins = pen
        W1, W2 = np.empty((E, S)), np.empty((E, S))
        if w_fn(nx2.ptr(elow), nx2.ptr(emid), nx2.ptr(eup), S, float(fp.fecont_mev[ibar]),
                nx2.ptr(eex), E, mode, bfis, wfis, twopi, nx2.ptr(u), nx2.ptr(col), nbins,
                nx2.ptr(W1), nx2.ptr(W2)) != 0:
            return None
        tr = torch.from_numpy(W1) @ torch.from_numpy(A) + torch.from_numpy(W2) @ torch.from_numpy(B)
        ts[ibar - 1] = tr.numpy()
    fis = np.empty((m, nj2))
    if bins_fn(int(fp.nfisbar), nx2.ptr(ts[0]), nx2.ptr(ts[1]), nx2.ptr(ts[2]), m, nj2,
               float(fnorm), nx2.ptr(ex), nx2.ptr(dex), float(exmax_mev), nx2.ptr(fis)) != 0:
        return None
    return fis.reshape(m, nJ, 2)


def target_transmission(chain, n, exinc_mev: float, fnorm: float):
    """`(tfis, tfisA, rhofisA)` of `fission_transmission(..., dexinc=0, primary=True)` at
    `exinc_mev`: `(maxj+1, 2)` and `(maxj+1, 2, NUMHILL+1)` arrays, or None when not covered.

    TALYS: tfission.f90:1 (tfission)
    Test: tests/hf/test_cengfis.py
    """
    co = grid_coefficients(chain, n, exinc_mev)
    if co is None:
        return None
    from physics.hf.core.constants import talys_constants
    from physics.hf.fission.barriers import NUMHILL
    from physics.hf.fission.fis2_nx2 import _kernels as fis2_kernels

    ks2 = fis2_kernels()
    if ks2 is None:
        return None
    bar_fn = ks2[1]
    fp, maxj = n.fp, chain.maxj
    nJ = maxj + 1
    nj2 = 2 * nJ
    nh = NUMHILL + 1
    e = np.array([float(exinc_mev)])
    twopi = float(talys_constants()["twopi"])
    tfisA = np.zeros((nj2, nh))
    rhofisA = np.zeros((nj2, nh))
    ts = [None, None, None]
    for ibar in range(1, int(fp.nfisbar) + 1):
        tr = np.zeros(nj2)
        ts[ibar - 1] = tr
        c = co[ibar]
        if c is None:
            continue
        pen = _pen(fp, n.ld, ibar)
        if pen is None:
            return None
        elow, emid, eup, A, B = c
        mode, bfis, wfis, u, col, nbins = pen
        collect = ibar == 1
        if bar_fn(nx2.ptr(elow), nx2.ptr(emid), nx2.ptr(eup), nx2.ptr(A), nx2.ptr(B),
                  elow.shape[0], nj2, float(fp.fecont_mev[ibar]), nx2.ptr(e), 1, mode, bfis, wfis,
                  twopi, nx2.ptr(u), nx2.ptr(col), nbins, nx2.ptr(tr), 0,
                  nx2.ptr(tfisA) if collect else 0, nx2.ptr(rhofisA) if collect else 0,
                  NUMHILL) != 0:
            return None
    tf = np.empty(nj2)
    comb = nx2.kernel("ceng_fis_combine", [_I, _P, _P, _P, _I, _D, _P], nx2.INT)
    if comb is None or comb(int(fp.nfisbar), nx2.ptr(ts[0]), nx2.ptr(ts[1]), nx2.ptr(ts[2]), nj2,
                            float(fnorm), nx2.ptr(tf)) != 0:
        return None
    return (tf.reshape(nJ, 2), tfisA.reshape(nJ, 2, nh), (1.0 + rhofisA).reshape(nJ, 2, nh))
