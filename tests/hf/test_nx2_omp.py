"""NATIVEX2 lever `omp`: `omp.omp_nx2` (the compiled optical-model solve, the float OMP parameters)
against the torch paths with the lever off. Skipped without a `libnx2` build
(scripts/build_nx2_native.sh)."""

from __future__ import annotations

import numpy as np
import pytest
import torch

from physics.hf.native import nx2
from tests._data import BROAD_DESIGN

pytestmark = pytest.mark.skipif(nx2.lib() is None, reason="no libnx2 build")

DT = torch.float64


def _close(a, b, rel=1e-12, floor=1e-300):
    a, b = np.asarray(a, float), np.asarray(b, float)
    assert a.shape == b.shape, (a.shape, b.shape)
    scale = np.maximum(np.abs(a), np.abs(b))
    bad = ~((np.abs(a - b) <= rel * scale + floor) | (np.isnan(a) & np.isnan(b)))
    assert not bad.any(), (np.argwhere(bad)[:5], a[bad][:5], b[bad][:5])


@pytest.fixture
def off(monkeypatch):
    """Run a block with the lever off: `with off(): ...`."""
    from contextlib import contextmanager

    @contextmanager
    def ctx():
        monkeypatch.setenv("HF_NX2_OMP", "0")
        try:
            yield
        finally:
            monkeypatch.delenv("HF_NX2_OMP")

    return ctx


def test_card_rounding_matches(off):
    from physics.hf.omp import omp_nx2
    from physics.hf.omp import schrodinger as S

    x = torch.tensor([0.0, 1.0e-3, 0.00999999, 0.0123456789, 3.14159265, -55.123456789, 999.99999,
                      1234.5678, -2.5e4, 7.0e-9], dtype=DT)
    with off():
        rv, re = S.ecis_card_value(x), S.ecis_card_energy(x.abs())
    _close(omp_nx2.card(x, False), rv, rel=4e-16, floor=0.0)
    _close(omp_nx2.card(x.abs(), True), re, rel=4e-16, floor=0.0)
    assert omp_nx2.card(torch.tensor(56.93539, dtype=DT), False).shape == ()


@pytest.mark.parametrize("lmax", [0, 30])
def test_coulomb_functions_match(off, lmax):
    from physics.hf.omp import omp_nx2
    from physics.hf.omp.schrodinger import coulomb_functions

    eta = torch.tensor([0.0, 0.0, 0.3, 2.5, 12.0, 25.0, 40.0, 3.0], dtype=DT)
    rho = torch.tensor([0.5, 30.0, 4.0, 3.0, 9.0, 20.0, 35.0, 60.0], dtype=DT)
    with off():
        ref = coulomb_functions(eta, rho, lmax)
    got = omp_nx2.coulomb(eta, rho, lmax)
    for a, b in zip(got, ref, strict=True):
        _close(a, b, rel=1e-11)


def _omp(Z, A, particle, e):
    from physics.hf.input.defaults import default_options, default_params
    from physics.hf.omp.parameters import omp_parameters

    o = default_options(Z, A)
    return omp_parameters(Z, A - Z, particle, e, default_params(Z, A, o), o), o


@pytest.mark.parametrize("Z,A,particle", [(26, 55, 1), (50, 120, 2), (82, 208, 6), (40, 90, 3),
                                          (62, 146, 4), (28, 58, 5)])
def test_omp_parameters_match(off, Z, A, particle):
    from physics.hf.input.defaults import default_options, default_params
    from physics.hf.omp import omp_nx2
    from physics.hf.omp.parameters import COLUMNS, omp_parameters

    e = torch.tensor([1.0e-3, 0.3, 2.5, 9.0, 14.7, 27.0, 90.0, 250.0], dtype=DT)
    o = default_options(Z, A)
    p = default_params(Z, A, o)
    for zr, ar in ((Z, A), (Z - 1, A - 3), (Z, A - 1)):
        with off():
            ref = omp_parameters(zr, ar - zr, particle, e, p, o)
        got = omp_nx2.omp_parameters(zr, ar - zr, particle, e, p, o)
        assert got is not None
        for c in COLUMNS:
            _close(getattr(got, c), getattr(ref, c), rel=1e-13, floor=1e-14)
        one = omp_nx2.omp_parameters(zr, ar - zr, particle, e[3:4], p, o)
        for c in COLUMNS:
            _close(getattr(one, c), getattr(ref, c)[3:4], rel=1e-13, floor=1e-14)


def test_omp_parameters_actinide_soukhovitskii(off):
    from physics.hf.input.defaults import default_options, default_params
    from physics.hf.omp import omp_nx2
    from physics.hf.omp.parameters import COLUMNS, omp_parameters

    Z, A = 90, 227
    o = default_options(Z, A)
    p = default_params(Z, A, o)
    e = torch.tensor([0.01, 1.0, 12.0, 25.0], dtype=DT)
    for k in (1, 2, 6):
        with off():
            ref = omp_parameters(Z, A - Z, k, e, p, o)
        got = omp_nx2.omp_parameters(Z, A - Z, k, e, p, o)
        if got is None:
            continue
        for c in COLUMNS:
            _close(getattr(got, c), getattr(ref, c), rel=1e-13, floor=1e-14)


def test_omp_parameters_keep_the_gradient_path():
    from physics.hf.input.defaults import default_options, default_params
    from physics.hf.omp import omp_nx2

    o = default_options(26, 56)
    p = default_params(26, 56, o)
    p.values["v1adjust"] = p.values["v1adjust"].clone().requires_grad_(True)
    assert omp_nx2.omp_parameters(26, 30, 1, torch.tensor([1.0, 2.0], dtype=DT), p, o) is None


@pytest.mark.parametrize("Z,A,particle", [(26, 54, 1), (82, 207, 2), (50, 117, 6), (40, 88, 3)])
def test_solve_spherical_matches(off, Z, A, particle):
    from physics.hf.omp import omp_nx2
    from physics.hf.omp.schrodinger import solve_spherical

    e = torch.tensor([0.001, 0.05, 0.8, 3.0, 7.5, 12.0, 19.0, 26.0], dtype=DT)
    omp, _ = _omp(Z, A, particle, e)
    with off():
        ref = solve_spherical(omp, Z, A, particle, e, lmax=30)
    got = omp_nx2.solve(omp, Z, A, particle, e, None, 30)
    # T = 4 (Im C - |C|^2) carries the torch path's own rounding, ~1e-15 absolute (libm against
    # torch elementary functions moves it): rel 1e-9 plus that floor
    _close(got.tjl, ref.tjl, rel=1e-9, floor=1e-13)
    _close(got.sigma_reac_mb, ref.sigma_reac_mb, rel=1e-9, floor=1e-7)
    if particle == 1:
        _close(got.sigma_tot_mb, ref.sigma_tot_mb, rel=1e-10)
        _close(got.sigma_shape_el_mb, ref.sigma_shape_el_mb, rel=1e-10)
    assert torch.equal(got.lmax, ref.lmax)


@pytest.mark.needs_data(BROAD_DESIGN)  # emax comes from the sweep design
@pytest.mark.parametrize("Z,A", [(26, 54), (82, 208)])
def test_transmission_build_matches(off, Z, A):
    import sys
    from pathlib import Path

    from physics.hf.compound.dens_reference import _transmission_build

    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
    import hf_ccfast_bench as bench

    emax = max(bench.energies()[0])
    with off():
        ref = _transmission_build(Z, A, emax, None, False)
    got = _transmission_build(Z, A, emax, None, False)
    for t in range(1, 7):
        ud, tl, lm = got[t]
        ud0, tl0, lm0 = ref[t]
        _close(ud, ud0, rel=1e-9, floor=1e-13)
        _close(tl, tl0, rel=1e-9, floor=1e-13)
        assert np.array_equal(lm, lm0)
    from physics.hf.compound.dens_reference import _eendmax, run_grid

    rg = run_grid(Z, A, emax)
    ee = _eendmax(Z, A, emax)
    nen = np.arange(rg.maxen + 1)
    for t in range(1, 7):
        keep = (nen >= rg.ebegin[t]) & (nen <= int(ee[t]))
        _close(got["sigma_reac_mb"][t - 1].numpy()[keep], ref["sigma_reac_mb"][t - 1].numpy()[keep],
               rel=1e-9, floor=1e-7)


def test_own_numerov_matches_the_handed_over_kernel():
    """Without `native.numerov_inward`'s kernel the job runs its own copy of the recurrence."""
    import ctypes

    from physics.hf.omp import omp_nx2

    e = torch.tensor([0.05, 0.8, 3.0, 7.5, 12.0, 19.0, 3.3, 4.4, 5.5, 6.6], dtype=DT)
    omp, _ = _omp(50, 117, 6, e)
    handed = omp_nx2.solve(omp, 50, 117, 6, e, None, 30)
    setter = nx2.kernel("nx2_omp_set_numerov", [nx2.P], None, lever="omp")
    setter(None)
    try:
        own = omp_nx2.solve(omp, 50, 117, 6, e, None, 30)
    finally:
        omp_nx2._HANDED[0] = False
        omp_nx2.enabled()
    _close(own.tjl, handed.tjl, rel=1e-9, floor=1e-13)
    _close(own.sigma_reac_mb, handed.sigma_reac_mb, rel=1e-9, floor=1e-7)
