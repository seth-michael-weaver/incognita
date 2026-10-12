"""PEGQ: exciton g/gp/gn keywords reach the pre-equilibrium model (KEYAUDIT wiring carried), and the Fermi-gas isospin split
gp, gn ~ Z^(1/3), N^(1/3) at fixed g = A/Kph behind `pegq y` / INCOGNITA_PEGQ=1 (default OFF = TALYS)."""

import pytest

from physics.hf.input import fitlib
from physics.hf.input.defaults import default_options, default_params
from physics.hf.preeq.prepare import exciton_densities, pegq_split, pickup_densities, single_particle_densities


def _params(Z, A, lines):
    import os

    os.environ["INCOGNITA_TALYS_FIT"] = "lines"
    os.environ[fitlib.ENV_LINES] = ";".join(lines)
    try:
        fitlib.deactivate()
        fitlib._cards.cache_clear()
        fitlib.activate(Z, A)
        o = default_options(Z, A)
        return o, default_params(Z, A, o)
    finally:
        os.environ.pop("INCOGNITA_TALYS_FIT")
        os.environ.pop(fitlib.ENV_LINES)
        fitlib.deactivate()
        fitlib._cards.cache_clear()


def test_default_is_single_particle_densities_bit_for_bit(monkeypatch):
    monkeypatch.delenv("INCOGNITA_PEGQ", raising=False)
    o = default_options(26, 56)
    p = default_params(26, 56, o)
    for Z, N in ((26, 31), (26, 30), (25, 31), (26, 29)):
        assert exciton_densities(Z, N, 15.0, p, o) == single_particle_densities(Z, N, 15.0)
        assert pickup_densities(Z, N, 15.0, o) == (Z / 15.0, N / 15.0)


def test_talys_formula_densitypar_533_541(monkeypatch):
    monkeypatch.delenv("INCOGNITA_PEGQ", raising=False)
    o, p = _params(26, 56, ["gadjust 26 57 1.2", "gnadjust 26 57 1.1", "gp 26 57 2.5"])
    g, gp, gn = exciton_densities(26, 31, 15.0, p, o)
    assert g == pytest.approx(1.2 * 57 / 15.0, rel=1e-12)
    assert gp == pytest.approx(1.2 * 2.5, rel=1e-12)
    assert gn == pytest.approx(1.2 * 1.1 * 31 / 15.0, rel=1e-12)
    assert exciton_densities(26, 30, 15.0, p, o) == single_particle_densities(26, 30, 15.0)


def test_adjust_one_is_noop(monkeypatch):
    monkeypatch.delenv("INCOGNITA_PEGQ", raising=False)
    o, p = _params(26, 56, ["gpadjust 26 57 1", "gnadjust 26 57 1"])
    assert exciton_densities(26, 31, 15.0, p, o) == single_particle_densities(26, 31, 15.0)


def test_pegq_split(monkeypatch):
    g, gp, gn = pegq_split(20, 20, 15.0)
    assert (gp, gn) == pytest.approx((20 / 15.0, 20 / 15.0), rel=1e-14)
    g, gp, gn = pegq_split(82, 126, 15.0)
    assert gp + gn == pytest.approx(208 / 15.0, rel=1e-14)
    assert gp / (82 / 15.0) == pytest.approx(1.18, abs=0.01) and gn / (126 / 15.0) == pytest.approx(0.88, abs=0.01)
    monkeypatch.setenv("INCOGNITA_PEGQ", "1")
    o = default_options(26, 56)
    p = default_params(26, 56, o)
    assert exciton_densities(26, 31, 15.0, p, o) == pegq_split(26, 31, 15.0)
    assert pickup_densities(26, 31, 15.0, o) == pegq_split(26, 31, 15.0)[1:]
