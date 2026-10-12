"""SNBIN: `snbin n|y` (env INCOGNITA_SNBIN), continuum bin edges at the residual's separation energies."""
import numpy as np
import pytest

from physics.hf.core import grids
from physics.hf.input.defaults import Options

f32 = np.float32
EDIS = np.array([0.0, 0.846, 2.085, 2.658, 2.942, 3.120, 3.123, 3.370, 3.445, 3.449, 3.602], f32)


def test_off_by_default(monkeypatch):
    monkeypatch.delenv(grids.SNBIN_ENV, raising=False)
    assert Options(26, 56, 1).snbin == "n" and not grids.snbin_on(Options(26, 56, 1))


@pytest.mark.parametrize("val", ["y", "1", "on"])
def test_on_from_environment(monkeypatch, val):
    monkeypatch.setenv(grids.SNBIN_ENV, val)
    assert grids.snbin_on(Options(26, 56, 1))


def test_off_is_talys():
    """no thresholds -> the TALYS grid (C kernel or numpy body), bit for bit"""
    a = grids.excitation_energies(EDIS, 10, 14.1, 40, 1, True)
    b = grids._excitation_energies(EDIS, 10, 14.1, 40, 1, True)
    for x, y in zip(a[:2], b[:2]):
        assert np.array_equal(x, y)
    assert a[2] == b[2] == 50


def test_edges_on_thresholds():
    s = [11.197, 10.183, 7.646, 16.0, 20.4, 2.0]  # n, p, a inside; outside or below Ex(NL) ignored
    ex, dex, maxex = grids._excitation_energies(EDIS, 10, 14.1, 40, 1, True, None, s)
    lo = ex[11 : maxex + 1] - 0.5 * dex[11 : maxex + 1]
    hi = ex[11 : maxex + 1] + 0.5 * dex[11 : maxex + 1]
    for t in (11.197, 10.183, 7.646):
        assert not np.any((lo < t - 1e-5) & (hi > t + 1e-5)), t  # no bin straddles a threshold
    assert maxex == 50  # nearest-edge moves: bin count unchanged
    assert abs(dex[11:maxex + 1].sum() - (14.1 - 3.602)) < 1e-4  # continuum still exactly filled
    w = (14.1 - 3.602) / 40
    assert dex[11:maxex + 1].min() >= 0.5 * w - 1e-5 and dex[11:maxex + 1].max() <= 1.5 * w + 1e-5


def test_close_thresholds_insert():
    e = grids.snbin_edges(np.linspace(0, 1, 5, dtype=f32), [0.50, 0.51])
    assert e.size == 6 and f32(0.5) in e and f32(0.51) in e and np.all(np.diff(e) > 0)


# SNBIN3: `snbin w` = `snbin y` + >= SNBIN_WINDOW_MIN bins inside every open window [S, Exmax]
def test_mode_w(monkeypatch):
    monkeypatch.setenv(grids.SNBIN_ENV, "w")
    assert grids.snbin_mode(Options(26, 56, 1)) == "w" and grids.snbin_on(Options(26, 56, 1))
    monkeypatch.setenv(grids.SNBIN_ENV, "y")
    assert grids.snbin_mode(Options(26, 56, 1)) == "y"


def test_window_min_bins():
    """Ti-48-like: window [S_n, Exmax] = 0.13 MeV inside a 0.2 MeV-bin grid -> >= 3 bins in it, rest unchanged"""
    eup = np.linspace(3.6, 11.76, 41, dtype=f32)
    s = [11.63, 11.45, 8.1]
    e1 = grids.snbin_edges(eup, s)
    e2 = grids.snbin_window_edges(e1, s, 3)
    for t in s:
        assert f32(t) in e2 and np.sum(e2 > f32(t)) >= 3, t
    assert np.all(np.diff(e2) > 0) and e2[0] == e1[0] and e2[-1] == e1[-1]
    lo = e1[e1 <= f32(11.45)]
    assert np.array_equal(e2[: lo.size], lo)  # bins below the lowest open window untouched
    assert set(e1.tolist()) <= set(e2.tolist())  # every pinned edge kept


def test_window_noop_when_wide():
    eup = np.linspace(3.6, 14.1, 41, dtype=f32)
    e1 = grids.snbin_edges(eup, [11.197, 10.183])
    assert np.array_equal(grids.snbin_window_edges(e1, [11.197, 10.183], 3), e1)


def test_window_through_body():
    ex, dex, maxex = grids._excitation_energies(EDIS, 10, 11.30, 40, 1, True, None, [11.197], 3)
    lo = ex[11: maxex + 1] - 0.5 * dex[11: maxex + 1]
    assert np.sum(lo >= 11.197 - 1e-5) >= 3 and maxex > 50
    assert abs(dex[11:maxex + 1].sum() - (11.30 - 3.602)) < 1e-4
