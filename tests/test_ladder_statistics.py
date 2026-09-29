"""Ladder statistics beyond the means: Porter-Thomas missed fraction, D(E) slope, spacing ratio."""
import numpy as np

from physics.resonance import ladder_statistics as L
from physics.resonance.ladder import goe_unit_levels


def test_porter_thomas_recovers_missed_fraction():
    rng = np.random.default_rng(3)
    full = np.sort(rng.chisquare(1, 2000))
    complete = L.porter_thomas(full)
    assert complete["f_miss"] < 0.03
    assert 0.8 < complete["nu_free"] < 1.25
    cut = L.porter_thomas(full[600:])          # the 30% smallest widths missed
    assert 0.24 < cut["f_miss"] < 0.36
    assert cut["nu_untruncated"] > 1.5          # the upward bias the truncated fit removes


def test_spacing_slope_and_ratio_on_goe():
    rng = np.random.default_rng(4)
    e = goe_unit_levels(1500, rng)
    s = L.spacing_slope(e, 0.0, float(e[-1]))
    assert abs(s["dlnD"]) < 3 * s["dlnD_se"]
    assert abs(L.mean_ratio(e)[0] - L.R_GOE) < 0.03
    two = L.expected_ratio(L.spin_sequence_weights(1.5))
    assert L.R_POISSON < two < L.R_GOE


def test_g_factor_unassigned_spin_gets_mean():
    g = L.g_factor(np.array([1.0, 2.0, 0.0]), 1.5)
    assert np.isclose(g[0], 3 / 8) and np.isclose(g[1], 5 / 8)
    assert np.isclose(g[2], (3 / 8 * 3 + 5 / 8 * 5) / 8)
