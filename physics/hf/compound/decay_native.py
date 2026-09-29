"""SPEEDD: loader for the compiled decay kernels (`decay_native.c`), used by `compound.decay_fast`.

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

Task: SPEEDD (the speed wave; no physics of its own). Acceptance test: `tests/hf/test_decay_fast.py`
(every kernel against the numpy path) and the speed-wave golden.

TALYS routines the kernels compute, in decay_fast's arrangement:
    compound.f90:1 (compound)        -- a bin's feeding of its daughters

`scripts/build_decay_native.sh` builds `libdecaynative.so.1` next to the source (a build output,
not in git). Without it -- another machine, the Mac, or `HF_NATIVE=0` -- `available()` is False and
decay_fast runs its numpy code, which is the reference the kernels are tested against.
"""

from __future__ import annotations

import ctypes
import os
from functools import lru_cache
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
_P = ctypes.c_void_p
_I = ctypes.c_int64
_D = ctypes.c_double


@lru_cache(maxsize=1)
def _lib():
    if os.environ.get("HF_NATIVE", "1") == "0":
        return None
    path = Path(os.environ.get("HF_DECAY_NATIVE_LIB", _HERE / "libdecaynative.so.1"))
    if not path.is_file():
        return None
    try:
        lib = ctypes.CDLL(str(path))
        if lib.dk_version() != 1:
            return None
    except (OSError, AttributeError):
        return None
    lib.dk_contract.argtypes = ([_I, _P] + [_I] * 6 + [_P] * 5 + [_D, _I] + [_P] * 5 + [_I]
                                + [_P] * 3)
    lib.dk_contract.restype = None
    lib.dk_feed.argtypes = [_I, _P, _D, _P, _P, _P, _P, _P]
    lib.dk_feed.restype = ctypes.c_int
    lib.dk_bin_photon.argtypes = [_P, _P, _P, _I, _I, _P, _D, _P, _P, _P, _P, _P]
    lib.dk_bin_photon.restype = ctypes.c_int
    return lib


def available() -> bool:
    return _lib() is not None


def ptr(a: np.ndarray | None) -> int | None:
    return None if a is None else a.__array_interface__["data"][0]


@lru_cache(maxsize=512)
def spin_l_bounds(odd: int, parspin2: int, nj: int, jx: int) -> tuple[np.ndarray, np.ndarray]:
    """`continuum._spin_l_mask`'s lbeg/lend for mother J < nj and residual spin index i < jx,
    int64 (nj * jx,) each."""
    j2 = 2 * np.arange(nj, dtype=np.int64) + odd
    irs2 = 2 * np.arange(jx, dtype=np.int64) + (odd + parspin2) % 2
    j2min = np.abs(j2[:, None] - irs2[None, :])
    lbeg = np.abs(j2min - parspin2) // 2
    lend = (j2[:, None] + irs2[None, :] + parspin2) // 2
    return np.ascontiguousarray(lbeg.ravel()), np.ascontiguousarray(lend.ravel())


def contract(rows: np.ndarray, F: np.ndarray, e, C: int, T: np.ndarray, lbeg, lend,
             njd: int) -> tuple[np.ndarray, np.ndarray]:
    """(dp (B, n, jx, 2), mcontrib (B, n)) of exit `e` for mother rows `rows` fed by F (B, nj, 2)."""
    B, nj, _ = F.shape
    _, n, jx, np_ = e.rho_c.shape
    L = T.shape[-1]
    dp = np.empty((B, n, jx, 2))
    mc = np.empty((B, n))
    V = np.empty(jx * 2 * L)
    nd = int(e.nd)
    _lib().dk_contract(B, ptr(rows), n, jx, np_, L, nj, C, ptr(F), ptr(lbeg), ptr(lend),
                       ptr(T), ptr(e.rho_c), e.sfac, nd, ptr(e.tot0) if nd else None,
                       ptr(e.tot1) if nd else None, ptr(e.rho_d) if nd else None,
                       ptr(e.ird) if nd else None, ptr(e.pd) if nd else None, njd,
                       ptr(V), ptr(dp), ptr(mc))
    return dp, mc


def feed(pop: np.ndarray, popeps_b: float, dsum6: np.ndarray, zero6: np.ndarray,
         d6: np.ndarray | None) -> tuple[np.ndarray, np.ndarray | None, bool]:
    """(feed (nj, 2), dead (nj, 2) bool or None, trapped) of one bin; every input (nj, 2)."""
    nj = pop.shape[0]
    out = np.empty((nj, 2))
    dead = np.empty((nj, 2), dtype=np.bool_)
    flags = _lib().dk_feed(nj, ptr(pop), popeps_b, ptr(dsum6), ptr(zero6), ptr(d6), ptr(out),
                           ptr(dead))
    return out, (dead if flags & 1 else None), bool(flags & 2)


class PhotonBin:
    """The photon exit's per-bin kernel with its fixed arguments packed once per nucleus."""

    def __init__(self, nw, e):
        d6 = nw.exits[6].D
        common = [np.ascontiguousarray(nw.dsum6), np.ascontiguousarray(nw.zero6),
                  None if d6 is None else np.ascontiguousarray(d6)]
        if e.closed:  # only the feed is formed
            n = jx = np_ = L = nd = 0
            self.keep = [None] * 9 + common
            C = 1
        else:
            _, n, jx, np_ = e.rho_c.shape
            nd, L, C = int(e.nd), e.Tn.shape[-1], e.C
            self.keep = [e.lb, e.le, e.Tn, e.rho_c, e.tot0 if nd else None,
                         e.tot1 if nd else None, e.rho_d if nd else None,
                         e.ird if nd else None, e.pd if nd else None, *common]
        self.ip = np.array([n, jx, np_, L, C, nd, nw.nj, int(e.closed), int(d6 is not None)],
                           dtype=np.int64)
        self.pp = np.array([0 if a is None else ptr(a) for a in self.keep], dtype=np.uint64)
        self.dpar = np.array([e.sfac])
        self.V = np.empty(max(jx * 2 * L, 1))
        self.n, self.jx = n, jx
        self.args = (ptr(self.ip), ptr(self.pp), ptr(self.dpar))
        self.fn = _lib().dk_bin_photon

    def __call__(self, row: int, pop: np.ndarray, popeps_b: float):
        """(feed, dead or None, trapped, dp (n, jx, 2) or None, mc (n,) or None)."""
        nj = pop.shape[0]
        feed = np.empty((nj, 2))
        dead = np.empty((nj, 2), dtype=np.bool_)
        dp = np.empty((self.n, self.jx, 2))
        mc = np.empty(self.n)
        ip, pp, dpar = self.args
        flags = self.fn(ip, pp, dpar, row, nj, ptr(pop), popeps_b, ptr(feed), ptr(dead),
                        ptr(self.V), ptr(dp), ptr(mc))
        return feed, (dead if flags & 1 else None), bool(flags & 2), dp, mc
