"""CENGSETUP: the libsetup kernels (native/setup.c, and nx2_omp.c compiled into libsetup) against
the libnx2 / libhfnative kernels they stand in for, to the bit; and the sliced DWBA
Clebsch-Gordan weights against their inline form. Skipped without the builds
(scripts/build_setup_native.sh, build_nx2_native.sh, build_native.sh)."""

from __future__ import annotations

import ctypes

import numpy as np
import pytest
import torch

from physics.hf import native
from physics.hf.native import nx2, setup_c

needs_libs = pytest.mark.skipif(setup_c.lib() is None or nx2.lib() is None,
                                reason="no libsetup / libnx2 build")
P, I64, DBL = ctypes.c_void_p, ctypes.c_int64, ctypes.c_double
DWBA_ARGS = [I64, I64, DBL, P, P, P, I64, P, P, P, DBL, P, I64, P, P, P]
OMP_ARGS = [I64, I64, I64, DBL, DBL, DBL, DBL, I64, P, P, P, P, I64, P, P]


def _fn(so, name, args, res=ctypes.c_int):
    f = getattr(so, name)
    f.argtypes, f.restype = args, res
    return f


def _p(a):
    return None if a is None else a.ctypes.data


def _dwba_case(rng, nlj, n, nk, charged):
    lmax = nlj // 2
    l = np.array([0] + [x for L in range(1, lmax + 1) for x in (L, L)][: nlj - 1], np.int64)
    h = 0.05
    r = h * np.arange(n + 1)
    r[0] = h
    f = np.empty((nlj, n + 1, 2))
    f[:, :, 0] = (l * (l + 1.0))[:, None] / (r * r)[None, :] - 2.0 / (1.0 + np.exp((r - 5.0) / 0.6))
    f[:, :, 1] = -0.3 / (1.0 + np.exp((r - 5.2) / 0.5)) + 1e-3 * rng.standard_normal(nlj)[:, None]
    y1 = h ** (l + 1.0)
    k2 = np.concatenate([[1.2], 1.2 - rng.uniform(0.01, 0.9, nk - 1)])
    eta = rng.uniform(0.1, 2.0, nk) if charged else np.zeros(nk)
    hp = rng.standard_normal((nk, nlj, 4)) if charged else None
    ww = rng.standard_normal((n + 1, 2)) * 1e-2
    ww[0] = 0.0
    ntab = 3
    tab = rng.uniform(0.0, 1.0, (ntab, nlj, nlj))
    tab[tab < 0.7] = 0.0
    tab[:, :, nlj - 3:] = 0.0  # a qmax below nlj
    tab_of = rng.integers(0, ntab, nk - 1).astype(np.int64)
    return (nlj, n, h, np.ascontiguousarray(f), y1, l, nk, k2, eta,
            None if hp is None else np.ascontiguousarray(hp), h * (n - 1), np.ascontiguousarray(ww),
            ntab, np.ascontiguousarray(tab), tab_of)


@needs_libs
@pytest.mark.parametrize("nlj,n,nk,charged", [(9, 40, 2, False), (57, 348, 24, False),
                                              (31, 101, 7, True), (4, 7, 3, False)])
def test_dwba_levels_bitwise(nlj, n, nk, charged):
    rng = np.random.default_rng(nlj * 1000 + n)
    c = _dwba_case(rng, nlj, n, nk, charged)
    a, b = np.zeros(nk - 1), np.zeros(nk - 1)
    ref = _fn(nx2.lib(), "nx2_dwba_levels", DWBA_ARGS)
    new = _fn(setup_c.lib(), "cs_dwba_levels", DWBA_ARGS)
    args = [x if not isinstance(x, np.ndarray) else _p(x) for x in c]
    assert ref(*args, _p(a)) == 0
    assert new(*args, _p(b)) == 0
    assert np.array_equal(a, b), (a, b)
    assert (a > 0).any()


def _omp_case(E, charged):
    e = np.linspace(0.5, 30.0, E)
    cols = np.zeros((19, E))
    cols[0], cols[1], cols[2] = 52.0 - 0.3 * e, 1.18, 0.67
    cols[3], cols[4], cols[5] = 0.1 * e, 1.18, 0.67
    cols[6], cols[7], cols[8] = 0.0, 1.27, 0.53
    cols[9], cols[10], cols[11] = 7.0 - 0.1 * e, 1.27, 0.53
    cols[12], cols[13], cols[14] = 5.9, 1.03, 0.59
    cols[15], cols[16], cols[17] = -0.05, 1.03, 0.59
    cols[18] = 1.2 if charged else 0.0
    cap = np.full(E, 25, np.int64)
    active = np.ones(E, np.int64)
    active[::7] = 0
    return (E, 36, 2, 0.5, 26.0 if charged else 0.0, 1.00727, 55.93494, 3,
            np.ascontiguousarray(e), np.ascontiguousarray(cols.reshape(-1)), cap, active, 1)


@needs_libs
@pytest.mark.skipif(not native.available(), reason="no libhfnative build")
@pytest.mark.parametrize("charged", [False, True])
def test_omp_job_bitwise(charged):
    """libsetup's nx2_omp_job with cs_numerov_inward = libnx2's with hf_numerov_inward."""
    import shutil
    import tempfile
    from pathlib import Path

    hf = ctypes.cast(native._load().hf_numerov_inward, ctypes.c_void_p).value
    with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parent) as d:
        # private copies, so the handed-over pointers do not touch the process's loaded libraries
        a_path, b_path = Path(d) / "a.so", Path(d) / "b.so"
        shutil.copy(nx2._default_path(), a_path)
        shutil.copy(Path(setup_c.lib()._name), b_path)
        A, B = ctypes.CDLL(str(a_path)), ctypes.CDLL(str(b_path))
        _fn(A, "nx2_omp_set_numerov", [P], None)(hf)
        _fn(B, "nx2_omp_set_numerov", [P], None)(
            ctypes.cast(B.cs_numerov_inward, ctypes.c_void_p).value)
        c = _omp_case(40, charged)
        outs = []
        for so in (A, B):
            tjl, sig = np.zeros(c[0] * c[1] * 3), np.zeros(3 * c[0])
            args = [x if not isinstance(x, np.ndarray) else _p(x) for x in c]
            assert _fn(so, "nx2_omp_job", OMP_ARGS)(*args, _p(tjl), _p(sig)) == 0
            outs.append(np.concatenate([tjl, sig]))
    assert np.array_equal(outs[0], outs[1], equal_nan=True)
    assert (outs[0] > 0).any()


@needs_libs
@pytest.mark.skipif(not native.available(), reason="no libhfnative build")
def test_numerov_inward_bitwise():
    """`cs_numerov_inward` (setup.c) has no arm64 NEON form matching `hf_numerov_inward`'s
    (hfnative.c's `#if HF_NEON` path); on arm64 it falls back to a plain scalar loop, batching
    the same recurrence in a different instruction order. Measured on this Mac (MACFIX2): only
    3 of 21 columns differ at all, and the worst is 3.2e-15 relative -- ordinary hardware FP
    non-associativity between two numerically-equivalent code paths, not a different algorithm.
    Reasonably close, not bit-identical (project rule, 2026-09-16: no bit-identity anywhere,
    <=1e-6 relative is the standard)."""
    rng = np.random.default_rng(7)
    m = 21
    ee = rng.uniform(0.5, 20.0, m)
    ra = rng.uniform(1.0, 10.0, m)
    rb = np.maximum(ra, 2.0 * ee + 20.0)
    gb, gb1 = rng.uniform(0.5, 2.0, m), rng.uniform(0.5, 2.0, m)
    n = np.full(m, 1500, np.int64)
    n[[3, 11, 20]] = [900, 200, 1501]  # a few columns off the call's count go scalar
    args = [I64] + [P] * 12
    ref = _fn(native._load(), "hf_numerov_inward", args, None)
    new = _fn(setup_c.lib(), "cs_numerov_inward", args, None)
    outs = []
    for fn in (ref, new):
        o = [np.zeros(m) for _ in range(6)]
        fn(m, *(_p(x) for x in (ee, ra, rb, gb, gb1, n)), *(_p(x) for x in o))
        outs.append(np.concatenate(o))
    den = np.maximum(np.abs(outs[0]), np.abs(outs[1]))
    rel = np.abs(outs[0] - outs[1]) / np.where(den > 0, den, 1.0)
    assert rel.max(initial=0.0) <= 1e-6


def test_cg_weights_sliced_bitwise():
    from physics.hf.ecis import dwba_setb as d

    for lam in (0, 2, 3, 5):
        for pb in (1, -1):
            for njmax in (20, 33, 60):
                for lmax in (njmax + lam + 1, njmax + 1):
                    a = d.cg_weights(lam, pb, lmax, njmax, 0.5)
                    b = d._cg_weights_inline(lam, pb, lmax, njmax, 0.5)
                    assert a.shape == b.shape
                    assert torch.equal(a, b)


def test_ripl_entry_walked_past_is_the_full_read():
    """`read_om_parameter` walks past other entries without converting their reals; the entry it
    returns is the one a full sequential read finds first."""
    import dataclasses
    from pathlib import Path

    from physics.hf.omp import ripl

    try:
        sdir = str(ripl._ripl_dir())
        lines = list(ripl._library_lines(str(Path(sdir) / "om-parameter-u.dat")))
    except (FileNotFoundError, OSError):
        pytest.skip("no RIPL library")
    rd = ripl._Reader(lines)
    full = []
    while rd.pos < len(rd.lines):
        full.append(ripl._read_entry(rd))
    first = {}
    for e in full:
        first.setdefault(e.iref, e)
    for iref in [2408, *list(first)[::60]]:
        ripl.read_om_parameter.cache_clear()
        got = ripl.read_om_parameter(iref, sdir)
        for f in dataclasses.fields(got):
            a, b = getattr(got, f.name), getattr(first[iref], f.name)
            assert (np.array_equal(a, b) if isinstance(a, np.ndarray) else a == b), (iref, f.name)
