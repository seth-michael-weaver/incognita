"""NATIVEX2 lever `ld`: the level-density kernels (`density/ld_nx2.py`, `native/nx2_ld.c`) against
the torch/numpy paths they replace, `HF_NX2_LD=0` against `=1` (closeness, not bits). Skipped
without a `libnx2` build (scripts/build_nx2_native.sh)."""

from __future__ import annotations

import numpy as np
import pytest
import torch

from physics.hf.native import nx2

pytestmark = pytest.mark.skipif(nx2.lib() is None, reason="no libnx2 build")

# (Z, A) residual of the target (Zt, At): binary residuals and the compound nucleus
CASES = [(26, 57, 26, 56), (25, 56, 26, 56), (39, 89, 40, 90), (82, 209, 82, 208),
         (50, 119, 50, 120), (61, 143, 62, 146)]


@pytest.fixture(autouse=True)
def _one_thread():
    prev = torch.get_num_threads()
    torch.set_num_threads(1)
    yield
    torch.set_num_threads(prev)


def _close(a, b, rel=1e-12):
    a, b = np.asarray(a, float), np.asarray(b, float)
    assert a.shape == b.shape
    scale = np.maximum(np.abs(a), np.abs(b))
    bad = np.abs(a - b) > rel * scale + 1e-300
    assert not bad.any(), (np.argwhere(bad)[:5], a[bad][:5], b[bad][:5])


def _arms(monkeypatch, fn):
    out = []
    for arm in ("0", "1"):
        monkeypatch.setenv("HF_NX2_LD", arm)
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
def test_fermi_tables_and_matching_roots(monkeypatch, Z, A, Zt, At):
    from physics.hf.density.ld_nx2 import _par
    from physics.hf.density.matching import _fermi_tables, matching
    from physics.hf.density.parameters import SENTINEL

    ld = _pre_match(Z, A, Zt, At)
    if _par(ld) is None:
        pytest.skip("model outside the kernel")
    (l0, t0, n0, e0), (l1, t1, n1, e1) = _arms(monkeypatch, lambda: _fermi_tables(ld, 0))
    assert (n0, e0) == (n1, e1)
    _close(l0.numpy(), l1.numpy())
    _close(t0.numpy(), t1.numpy(), 1e-10)  # temprho: dEx over a difference of two logs
    exmemp = 2.33 + 253.0 / A + float(ld.pair_mev)
    for xacc in (1.0e-4, 1.0e-10):
        for e0save in (SENTINEL, 1.3):
            r0, r1 = _arms(monkeypatch, lambda: matching(ld, l0, t0, exmemp, e0save, 0, xacc))
            assert abs(r0 - r1) <= 1e-12 * max(abs(r0), 1.0), (r0, r1)


@pytest.mark.parametrize("Z,A,Zt,At", CASES)
def test_ld_build_matched_quantities_and_ncum(monkeypatch, Z, A, Zt, At):
    from physics.hf.compound.dens_reference import _ld_build

    _pre_match(Z, A, Zt, At)
    (ld0, nt0, nl0, nc0), (ld1, nt1, nl1, nc1) = _arms(
        monkeypatch, lambda: _ld_build(Z, A, Zt, At, None))
    assert (nt0, nl0) == (nt1, nl1)
    for f in ("T_mev", "E0_mev", "Exmatch_mev"):
        _close(getattr(ld0, f).numpy(), getattr(ld1, f).numpy())
    _close(nc0, nc1)


@pytest.mark.parametrize("Z,A,Zt,At", CASES)
def test_rhogrid_of_bin_sets(monkeypatch, Z, A, Zt, At):
    from physics.hf.compound.dens_reference import _ld_of, rhogrid_of
    from physics.hf.density.ld_nx2 import _par
    from physics.hf.density.parameters import NUMJ

    _pre_match(Z, A, Zt, At)
    ld, _ntop, nl, _ncum = _ld_of(Z, A, Zt, At)
    if _par(ld) is None:
        pytest.skip("model outside the kernel")
    rng = np.random.default_rng(Z * 1000 + A)
    for n, top in ((40, 12.0), (25, 25.0)):
        ex = np.sort(rng.random(n)) * top
        dex = np.full(n, top / n)
        maxj = rng.integers(-1, NUMJ + 1, n).astype(np.int64)
        for nlast in (0, 5):
            a, b = _arms(monkeypatch, lambda: rhogrid_of(Z, A, Zt, At, ex, dex, maxj, nlast))
            assert isinstance(b, np.ndarray)
            _close(a, b, 1e-11)


@pytest.mark.parametrize("Z,A,Zt,At", CASES)
def test_rigid_moments_are_deformations(Z, A, Zt, At):
    """`densitypar`'s shortcut to Irigid0/Irigid gives `deformation`'s numbers, bit for bit."""
    from physics.hf.compound.dens_reference import structure_of
    from physics.hf.structure.deformation import deformation, rigid_moments
    from physics.hf.structure.levels import discrete_levels

    _pre_match(Z, A, Zt, At)
    o, p, m = structure_of(Zt, At)
    d = deformation(Z, A, o, discrete_levels(Z, A, o, m, p), m, p)
    assert rigid_moments(Z, A, o, m, p) == (d.irigid0, d.irigid)


@pytest.mark.parametrize("Z,A,Zt,At", CASES + [(92, 238, 92, 238), (90, 233, 90, 232)])
def test_densitypar_floats_is_densitypar(monkeypatch, Z, A, Zt, At):
    """Every field of `densitypar`'s LDNucleus on the float path against the tensor path."""
    from physics.hf.compound.dens_reference import structure_of
    from physics.hf.density.parameters import densitypar
    from physics.hf.structure.levels import discrete_levels

    _pre_match(Z, A, Zt, At)
    o, p, m = structure_of(Zt, At)
    lv = discrete_levels(Z, A, o, m, p)
    a, b = _arms(monkeypatch, lambda: densitypar(Z, A, o, p, m, lv))
    for f, x in vars(a).items():
        y = getattr(b, f)
        if isinstance(x, torch.Tensor):
            assert x.shape == y.shape and x.dtype == y.dtype, f
            _close(x.numpy(), y.numpy(), 1e-14)
        else:
            assert x == y, f


def test_densitypar_keeps_the_tensor_path_for_a_gradient():
    from physics.hf.compound.dens_reference import structure_of
    from physics.hf.density.ld_nx2 import densitypar_floats
    from physics.hf.density.parameters import densitypar
    from physics.hf.structure.levels import discrete_levels

    _pre_match(26, 57, 26, 56)
    th = torch.tensor(1.0, dtype=torch.float64, requires_grad=True)
    o, p, m = structure_of(26, 56, {"aadjust": th})
    lv = discrete_levels(26, 57, o, m, p)
    assert densitypar_floats(26, 57, o, p, m, lv) is None
    assert densitypar(26, 57, o, p, m, lv).alev.requires_grad
