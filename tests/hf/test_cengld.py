"""CENGLD (ROUTE100 WP6): the level-density kernels of `native/ld.c` (`density/ld_ceng.py`) against
the paths they replace, `HF_NX2_CENGLD=0` against `=1`. Skipped without a `libnx2` build
(scripts/build_nx2_native.sh)."""

from __future__ import annotations

import numpy as np
import pytest
import torch

from physics.hf.native import nx2

pytestmark = pytest.mark.skipif(nx2.lib() is None, reason="no libnx2 build")

# (Z, A) residual of the target (Zt, At); 7-15 is below A = 18 (ctm.light)
CASES = [(26, 57, 26, 56), (25, 56, 26, 56), (39, 89, 40, 90), (82, 209, 82, 208),
         (50, 119, 50, 120), (61, 143, 62, 146), (68, 167, 68, 166), (7, 15, 7, 14)]


@pytest.fixture(autouse=True)
def _one_thread():
    prev = torch.get_num_threads()
    torch.set_num_threads(1)
    yield
    torch.set_num_threads(prev)


def _close(a, b, rel):
    a, b = np.asarray(a, float), np.asarray(b, float)
    assert a.shape == b.shape
    bad = np.abs(a - b) > rel * np.maximum(np.abs(a), np.abs(b)) + 1e-300
    assert not bad.any(), (np.argwhere(bad)[:5], a[bad][:5], b[bad][:5])


def _arms(monkeypatch, fn):
    out = []
    for arm in ("0", "1"):
        monkeypatch.setenv("HF_NX2_CENGLD", arm)
        out.append(fn())
    return out


def _pre_match(Z, A, Zt, At):
    from physics.hf.compound.dens_reference import structure_of
    from physics.hf.density.parameters import densitypar
    from physics.hf.density.tables import attach_tables
    from physics.hf.structure.levels import discrete_levels

    try:
        o, p, m = structure_of(Zt, At)
        return attach_tables(densitypar(Z, A, o, p, m, discrete_levels(Z, A, o, m, p)))
    except Exception as exc:  # noqa: BLE001  (structure database absent on this machine)
        pytest.skip(f"no level density for {Z}-{A}: {exc}")


@pytest.mark.parametrize("Z,A,Zt,At", CASES)
@pytest.mark.parametrize("flags", [(False, False), (True, False), (False, True)])
def test_densitymatch_is_the_torch_path(monkeypatch, Z, A, Zt, At, flags):
    """T, E0, Exmatch of `densitymatch` (flagldglobal, flagctmglob) and every other field kept."""
    from physics.hf.density.ld_ceng import densitymatch_fast
    from physics.hf.density.ld_nx2 import _par
    from physics.hf.density.matching import densitymatch

    ld = _pre_match(Z, A, Zt, At)
    if _par(ld) is None:
        pytest.skip("model outside the kernel")
    monkeypatch.setenv("HF_NX2_CENGLD", "1")
    assert densitymatch_fast(ld, *flags, 1e-4) is not None
    a, b = _arms(monkeypatch, lambda: densitymatch(ld, *flags))
    for f, x in vars(a).items():
        y = getattr(b, f)
        if isinstance(x, torch.Tensor):
            assert x.shape == y.shape and x.dtype == y.dtype, f
            _close(x.numpy(), y.numpy(), 1e-13)
        else:
            assert x == y, f


@pytest.mark.parametrize("Z,A,Zt,At", CASES[:4])
def test_densitymatch_adjust_passes(monkeypatch, Z, A, Zt, At):
    """The Tadjust / E0adjust second passes and a given Exmatchadjust."""
    from dataclasses import replace

    from physics.hf.density.ld_nx2 import _par
    from physics.hf.density.matching import densitymatch

    ld0 = _pre_match(Z, A, Zt, At)
    if _par(ld0) is None:
        pytest.skip("model outside the kernel")
    one = torch.ones(1, dtype=torch.float64)
    for adj in ({"Tadjust": 1.07 * one}, {"E0adjust": 0.93 * one},
                {"Exmatchadjust": 1.2 * one, "Exmatch_mev": 5.0 * one}):
        ld = replace(ld0, **adj)
        a, b = _arms(monkeypatch, lambda: densitymatch(ld))
        for f in ("T_mev", "E0_mev", "Exmatch_mev"):
            _close(getattr(a, f).numpy(), getattr(b, f).numpy(), 1e-13)


@pytest.mark.parametrize("Z,A,Zt,At", CASES)
def test_rhogrid_is_nx2_rhogrid_bit_for_bit(monkeypatch, Z, A, Zt, At):
    """Random bin sets, with contiguous bins (shared edges) and maxJ below and above numJ."""
    from physics.hf.compound.dens_reference import _ld_of
    from physics.hf.density import ld_ceng
    from physics.hf.density.ld_nx2 import _par
    from physics.hf.density.parameters import NUMJ

    _pre_match(Z, A, Zt, At)
    ld, _ntop, _nl, _ncum = _ld_of(Z, A, Zt, At)
    par = _par(ld)
    if par is None:
        pytest.skip("model outside the kernel")
    fn = nx2.kernel("nx2_ld_rhogrid", [nx2.P] * 5 + [nx2.I64, nx2.I64, nx2.DBL, nx2.P])
    rng = np.random.default_rng(Z * 1000 + A)
    monkeypatch.setenv("HF_NX2_CENGLD", "1")
    for n, top in ((40, 12.0), (25, 25.0), (60, 18.0)):
        dex = np.full(n, top / n) if n != 25 else rng.random(n) * top / n
        ex = np.cumsum(dex) - 0.5 * dex  # contiguous: top of k is bottom of k + 1
        maxj = rng.integers(-1, NUMJ + 3, n).astype(np.int64)
        for nlast in (0, 5):
            ref = np.zeros((n, NUMJ + 1, 2))
            sel = np.zeros(n, np.uint8)
            sel[nlast + 1:] = maxj[nlast + 1:] >= 0
            assert fn(nx2.ptr(par), nx2.ptr(ex), nx2.ptr(dex), nx2.ptr(maxj), nx2.ptr(sel), n,
                      NUMJ, 0.5 * (A % 2), nx2.ptr(ref)) == 0
            got = ld_ceng.rhogrid(par, A, ex, dex, maxj, nlast, NUMJ)
            assert np.array_equal(got, ref)


@pytest.mark.parametrize("Z,A,Zt,At", CASES)
def test_ignatyuk_spincut_arrays(monkeypatch, Z, A, Zt, At):
    from physics.hf.compound.dens_reference import _ld_of
    from physics.hf.density.parameters import ignatyuk, spincut

    _pre_match(Z, A, Zt, At)
    ld = _ld_of(Z, A, Zt, At)[0]
    ex = torch.linspace(-1.0, 30.0, 97, dtype=torch.float64)
    with torch.no_grad():
        for ibar, ipop, rs in ((0, 0, 4.0), (0, 1, 3.0)):
            a0, a1 = _arms(monkeypatch, lambda: ignatyuk(ld, ex, ibar))
            _close(a0.numpy(), a1.numpy(), 1e-14)
            for ald in (a0, float(a0[40])):
                s0, s1 = _arms(monkeypatch, lambda: spincut(ld, ald, ex, ibar, ipop, rs))
                _close(s0.numpy(), s1.numpy(), 1e-14)


def test_densitypar_shared_by_identity(monkeypatch):
    """No gradient mode: the same objects give the same record, another Params object (a fit's new
    parameter point) its own; with gradients enabled every call builds its own."""
    import copy

    from physics.hf.compound.dens_reference import structure_of
    from physics.hf.density.parameters import densitypar
    from physics.hf.structure.levels import discrete_levels

    _pre_match(26, 57, 26, 56)
    monkeypatch.setenv("HF_NX2_CENGLD", "1")
    monkeypatch.setenv("HF_CENGLD2_XT", "0")  # CENGLD2 shares equal values across objects too
    o, p, m = structure_of(26, 56)
    lv = discrete_levels(26, 57, o, m, p)
    p2 = copy.copy(p)
    with torch.no_grad():
        a = densitypar(26, 57, o, p, m, lv)
        assert densitypar(26, 57, o, p, m, lv) is a
        b = densitypar(26, 57, o, p2, m, lv)
    assert b is not a and float(b.alev) == float(a.alev)
    assert densitypar(26, 57, o, p, m, lv) is not a
