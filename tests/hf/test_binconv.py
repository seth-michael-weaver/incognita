"""BINCONV: `binconv n|y` (env INCOGNITA_BINCONV), graded residual continuum mesh (core/grids.binconv_edges)."""
import numpy as np
import pytest

from physics.hf.core import grids
from physics.hf.input.defaults import Options

f32 = np.float32
EDIS = np.array([0.0, 0.846, 2.085, 2.658, 2.942, 3.120, 3.123, 3.370, 3.445, 3.449, 3.602], f32)


def test_off_by_default(monkeypatch):
    monkeypatch.delenv(grids.BINCONV_ENV, raising=False)
    assert Options(26, 56, 1).binconv == "n" and not grids.binconv_mode(Options(26, 56, 1))


def test_on_from_environment(monkeypatch):
    monkeypatch.setenv(grids.BINCONV_ENV, "y")
    assert grids.binconv_mode(Options(26, 56, 1))


def test_bad_value():
    from dataclasses import replace

    o = replace(Options(26, 56, 1), binconv="maybe")
    with pytest.raises(ValueError):
        grids.binconv_mode(o)


def test_knots_are_edges_and_widths_bounded():
    ths, ch, fis = [7.646, 10.183, 11.197], [12.5], [13.0]
    e = grids.binconv_edges(3.602, 14.1, 40, ths, 8.0, 0.3, 1.0, "btscf", 0.35, ch, 56, fis)
    assert e.dtype == f32 and np.all(np.diff(e) > 0)
    for k in ths + ch + fis + [3.602, 14.1]:
        assert f32(k) in e, k
    w0 = (14.1 - 3.602) / 40
    assert np.diff(e).max() <= w0 * (1 + 1e-5)
    assert np.diff(e).min() >= w0 / 8.0 * (1 - 1e-3)
    assert np.diff(e)[0] < 0.2 * w0 and np.diff(e)[-1] < 0.2 * w0  # graded at Ex(NL) and Exmax


def test_temperature_bound():
    """width <= kappa * sqrt(max(Ex, 1) / (A/8)) everywhere (heavy nucleus, wide continuum)"""
    e = grids.binconv_edges(0.5, 14.0, 40, [], 8.0, 0.3, 1.0, "bt", 0.35, (), 237)
    mid = 0.5 * (e[1:] + e[:-1])
    bound = 0.35 * np.sqrt(np.maximum(e[1:], 1.0) / (237 / 8.0))  # bound at the bin's upper end (monotone)
    assert np.all(np.diff(e) <= bound * 1.01 + 1e-6)
    assert e.size - 1 > 40 and mid.size == e.size - 1


def test_body_fills_continuum():
    adapt = (8.0, 0.3, 1.0, "btscf", 0.35, (12.5,), 56, ())
    ex, dex, maxex = grids._excitation_energies(EDIS, 10, 14.1, 40, 1, True, None, [7.646, 10.183, 11.197], 24, adapt)
    assert abs(dex[11:maxex + 1].sum() - (14.1 - 3.602)) < 1e-4
    assert np.all(ex[11:maxex + 1] > 3.602) and maxex - 10 <= grids.NUMBINS_ALLOC


def test_off_is_talys():
    a = grids._excitation_energies(EDIS, 10, 14.1, 40, 1, True)
    b = grids.excitation_energies(EDIS, 10, 14.1, 40, 1, True)
    for x, y in zip(a[:2], b[:2]):
        assert np.array_equal(x, y)
