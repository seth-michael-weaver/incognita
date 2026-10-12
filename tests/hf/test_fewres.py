"""MACSCLOSED: physics/hf/fewres.py (INCOGNITA_FEWRES few-resonance capture).

* the RTK97 window and region threshold (Delta(30 keV) = 47.76 keV, N30 = Delta / D0 < 10)
* J sequences / channel counts for even (I = 0) and odd (I = 3/2) targets
* the ensemble mean of the window sum equals the analytic (HF-type) mean: E[r] = 1
* logmean -> 1 + delta when the window is full (dense ladder), < 1 + delta when it is sparse (Jensen)
* ladders do not depend on the grid's top energy (block-seeded common random numbers)
* off (the default) leaves Results untouched
"""
from __future__ import annotations

import math

import numpy as np
import pytest

from physics.hf import fewres as F


def test_window_and_threshold():
    assert F.DELTA30_EV == pytest.approx(47756.0, rel=1e-3)
    assert F.n30(4775.6) == pytest.approx(10.0, rel=1e-3)
    assert F.n30(0.0) == float("inf")


def test_sequences_even_and_odd():
    rho = lambda J, p: 1.0                             # noqa: E731  1 level / MeV for every J, parity
    s = F._sequences(0.0, 1, rho, 0.1, 0.2, lmax=2)
    assert [(l, J, nu) for l, J, nu, *_ in s] == [(0, 0.5, 1), (1, 0.5, 1), (1, 1.5, 1), (2, 1.5, 1), (2, 2.5, 1)]
    assert [x[5] for x in s] == [0.1, 0.2, 0.2, 0.1, 0.1]
    s = F._sequences(1.5, 1, rho, 0.1, 0.1, lmax=0)
    assert [(J, nu) for _, J, nu, *_ in s] == [(1.0, 1), (2.0, 1)]
    assert s[0][4] == pytest.approx(3 / 8) and s[1][4] == pytest.approx(5 / 8)
    s = F._sequences(1.5, 1, rho, 0.1, 0.1, lmax=1)
    assert dict(((l, J), nu) for l, J, nu, *_ in s)[(1, 1.0)] == 2


def _tl(T0=0.05):
    e = np.geomspace(1e3, 2e7, 50)
    T = np.zeros((50, F.LMAX + 1)); T[:, 0] = np.minimum(T0 * np.sqrt(e / 1e4), 0.9); T[:, 1] = np.minimum(0.01 * (e / 1e4) ** 1.5, 0.9)
    return F._Tl(e, T)


@pytest.mark.parametrize("D", [2.0e3, 5.0e4])
def test_ensemble_mean_is_analytic_mean(D):
    seqs = [(0, 0.5, 1, D, 1.0, 0.5), (1, 1.5, 1, D / 2, 2.0, 0.5)]
    tl = _tl(); kT = 3.0e4
    mu, _ = F._mean_var(seqs, tl, kT)
    L = F._ladders(seqs, 7, F.XMAX * kT)
    r = F._draw_sums(seqs, L, tl, kT) / mu
    assert r.mean() == pytest.approx(1.0, abs=0.08)


def test_logmean_limits():
    tl = _tl(); e = np.array([3.0e4])
    dense = [(0, 0.5, 1, 3.0e2, 1.0, 0.5)]               # ~1200 levels in the window
    sparse = [(0, 0.5, 1, 2.0e5, 1.0, 0.5)]              # ~2 levels in the window
    d = np.array([0.1])
    gd = F.ensemble_G(dense, tl, e, d, seed=1)[0]
    gs = F.ensemble_G(sparse, tl, e, d, seed=1)[0]
    assert gd == pytest.approx(math.log1p(0.1), abs=0.01)
    assert gs < math.log1p(0.1) - 0.05


def test_ladders_independent_of_top_energy():
    seqs = [(0, 0.5, 1, 1.0e4, 1.0, 0.5)]
    a = F._ladders(seqs, 3, 1.0e5)[0][0]
    b = F._ladders(seqs, 3, 1.0e6)[0][0]
    n = a.shape[1]
    assert np.array_equal(a, b[:, :n])


def test_off_is_untouched(monkeypatch):
    monkeypatch.delenv("INCOGNITA_FEWRES", raising=False)
    sentinel = object()
    assert F.add_to_results(sentinel, object()) is sentinel
    monkeypatch.setenv("INCOGNITA_FEWRES", "bogus")
    with pytest.raises(ValueError):
        F.mode()


def test_typical_mode_no_dc_floor(monkeypatch):
    """FEWTYP: `typical` = logmean with delta = 0: G -> 1 dense, < 1 sparse, exactly 1 at E >= 1 MeV."""
    monkeypatch.setenv("INCOGNITA_FEWRES", "typical")
    assert F.mode() == "typical"
    tl = _tl(); e = np.array([3.0e4, 2.0e6]); z = np.zeros(2)
    gd = F.ensemble_G([(0, 0.5, 1, 3.0e2, 1.0, 0.5)], tl, e, z, seed=1)
    gs = F.ensemble_G([(0, 0.5, 1, 2.0e5, 1.0, 0.5)], tl, e, z, seed=1)
    assert gd[0] == pytest.approx(0.0, abs=0.01) and gs[0] < -0.05
    assert gd[1] == 0.0 and gs[1] == 0.0
