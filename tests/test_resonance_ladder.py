"""Statistical ladder generator: GOE statistics, parameter conventions, SLBW integrals."""

import math

import numpy as np
import pytest

from physics.resonance import ladder as L

AU = L.AverageParams(awri=195.27, target_spin=1.5, d0_ev=15.5, s0=1.9e-4, gg_ev=0.128,
                     s1=0.58e-4, sigma2=6.0)


def test_goe_spacing_law():
    s = np.diff(L.goe_unit_levels(20_000, np.random.default_rng(1)))
    assert abs(s.mean() - 1) < 0.02
    # GOE nearest-neighbour variance 0.286 (Wigner surmise 0.273); Poisson would be 1
    assert 0.25 < s.var() < 0.31
    # level repulsion: P(s < 0.1) ~ pi/4 * 0.1^2 / 2 ~ 0.4% for GOE, 9.5% for Poisson
    assert (s < 0.1).mean() < 0.015


def test_spin_groups_reproduce_d0_and_s0():
    groups = AU.spin_groups()
    s_wave = [g for g in groups if g.l == 0]
    assert [g.j for g in s_wave] == [1.0, 2.0]
    assert math.isclose(1.0 / sum(1.0 / g.d_ev for g in s_wave), AU.d0_ev, rel_tol=1e-12)
    assert math.isclose(sum(g.g for g in s_wave), 1.0)
    assert math.isclose(sum(g.g * g.gn_red_mean / g.d_ev for g in s_wave), AU.s0, rel_tol=1e-12)
    p_wave = [g for g in groups if g.l == 1]
    # sum over J of g * nu = 2l + 1 = 3 for p-wave
    assert math.isclose(sum(g.g * g.nu for g in p_wave), 3.0)


def test_spin_zero_target_single_group():
    p = L.AverageParams(awri=237.0, target_spin=0.0, d0_ev=20.0, s0=1e-4, gg_ev=0.023)
    g = p.spin_groups(lmax=0)
    assert len(g) == 1 and g[0].j == 0.5 and g[0].g == 1.0 and math.isclose(g[0].d_ev, 20.0)


def test_sampled_ladder_statistics_match_inputs():
    rng = np.random.default_rng(3)
    lad = L.sample_ladder(AU, 200_000.0, rng, e_min=0.0, lmax=0)
    s = lad.l == 0
    d0 = (lad.er[s][-1] - lad.er[s][0]) / (s.sum() - 1)
    assert abs(d0 / AU.d0_ev - 1) < 0.03
    s0 = np.sum(lad.g[s] * lad.gn_red[s]) / (s.sum() * d0)
    assert abs(s0 / AU.s0 - 1) < 0.1  # Porter-Thomas: relative error ~ sqrt(2/n)
    assert abs(lad.gg.mean() / AU.gg_ev - 1) < 0.02


def test_resonance_integral_matches_brute_force():
    rng = np.random.default_rng(0)
    lad = L.sample_ladder(AU, 600.0, rng)
    ri = L.resonance_integral(lad, 0.5, 500.0)
    gam = lad.gn_at_resonance() + lad.gg
    pieces = [np.geomspace(0.5, 500.0, 200_000)]
    u = np.tan(np.linspace(-1.56, 1.56, 301))
    pieces += [r + 0.5 * gam[i] * u for i, r in enumerate(lad.er) if 0.5 < r < 500.0]
    e = np.unique(np.concatenate(pieces))
    e = e[(e >= 0.5) & (e <= 500.0)]
    brute = np.trapezoid(L.slbw(lad, e)["capture"] / e, e)
    assert abs(ri / brute - 1) < 2e-3


def test_single_resonance_peak_and_area():
    lad = L.Ladder(awri=100.0, target_spin=0.0, radius=L.channel_radius(100.0),
                   l=np.array([0]), j=np.array([0.5]), g=np.array([1.0]), er=np.array([100.0]),
                   gn_red=np.array([0.01 / 10.0]), gg=np.array([0.1]))
    xs = L.slbw(lad, [100.0])
    k2 = L.wavenumber(100.0, 100.0) ** 2
    gam = 0.11
    # peak capture = 4 pi/k^2 g Gn Gg / Gamma^2
    assert xs["capture"][0] == pytest.approx(4 * math.pi / k2 * 0.01 * 0.1 / gam**2, rel=1e-9)
    assert xs["total"][0] == pytest.approx(xs["capture"][0] + xs["elastic"][0])


def test_average_capture_limits():
    # Gn >> Gg: <Gn Gg / Gamma> -> Gg, so <sigma> -> 2 pi^2/k^2 * Gg / D0 (s-wave, I = 0)
    p = L.AverageParams(awri=100.0, target_spin=0.0, d0_ev=10.0, s0=1.0, gg_ev=1e-6)
    e = np.array([10.0])
    k2 = L.wavenumber(e, 100.0) ** 2
    assert L.average_capture(p, e, lmax=0)[0] == pytest.approx(2 * math.pi**2 / k2[0] * 1e-6 / 10,
                                                               rel=2e-3)


# --------------------------------------------------------------------------------------------
# WP-19b: D0 domain refusal and the widened ensemble (docs/results/resonance-v0b.md)
# --------------------------------------------------------------------------------------------


def test_check_domain_refuses_large_d0():
    wide = L.AverageParams(awri=16.0, target_spin=0.0, d0_ev=5e5, s0=1e-4, gg_ev=1.0)
    with pytest.raises(L.LadderDomainError, match="statistical ladder is refused"):
        L.check_domain(wide)
    with pytest.raises(L.LadderDomainError):
        L.ensemble_observables(wide, 1, np.random.default_rng(0))
    # the guard is on D0 only, and an explicit opt-out still computes (individual ensemble draws)
    o = L.ensemble_observables(wide, 1, np.random.default_rng(0), allow_out_of_domain=True)
    assert np.isfinite(o["thermal"][0])
    L.check_domain(AU)  # a measured Au-197 ladder is well inside the domain


def test_refused_thermal_would_have_been_absurd():
    """Why the refusal exists: with D0 = 0.5 MeV the ladder answers ~0 b, not a small number."""
    p = L.AverageParams(awri=207.0, target_spin=0.0, d0_ev=5e5, s0=1e-4, gg_ev=0.03)
    o = L.ensemble_observables(p, 1, np.random.default_rng(1), allow_out_of_domain=True)
    assert o["thermal"][0] < 1e-6  # Pb-208 really captures ~0.5 mb at thermal


def test_spin_cutoff_moves_the_p_wave_level_density():
    """Step 1 samples sigma^2 because it sets how D0 splits over spins, hence p-wave capture."""
    lo = L.AverageParams(awri=195.27, target_spin=1.5, d0_ev=15.5, s0=1.9e-4, gg_ev=0.128,
                         s1=0.58e-4, sigma2=3.0)
    hi = L.AverageParams(awri=195.27, target_spin=1.5, d0_ev=15.5, s0=1.9e-4, gg_ev=0.128,
                         s1=0.58e-4, sigma2=12.0)
    e = np.array([5e4])
    # a larger spin cutoff spreads the same s-wave D0 over more J, adding p-wave sequences
    assert L.average_capture(hi, e)[0] != L.average_capture(lo, e)[0]
    # s-wave D0 is preserved whatever sigma^2 is: 1/D0 = sum over the s-wave J sequences
    for p in (lo, hi):
        s_wave = [g for g in p.spin_groups() if g.l == 0]
        assert math.isclose(1.0 / sum(1.0 / g.d_ev for g in s_wave), p.d0_ev, rel_tol=1e-12)


def test_runner_refuses_and_samples_sigma2():
    from physics.resonance import ensemble_runner as ER

    job = {"target_id": "Z079N118M0", "mode": "test", "awri": 195.27, "spin": 1.5, "sigma2": 6.0,
           "d0_log10": math.log10(15.5), "s0_log10": math.log10(1.9e-4),
           "gg_log10": math.log10(0.128), "s1_log10": math.log10(0.58e-4),
           "d0_sigma": 0.02, "s0_sigma": 0.02, "gg_sigma": 0.02, "s1_sigma": 0.02}
    # 10-100 keV sits above the explicit ladder, so that column is an exact function of the drawn
    # average parameters: with every head sigma at 0 it is constant unless sigma^2 is sampled.
    flat = {**job, "d0_sigma": 0.0, "s0_sigma": 0.0, "gg_sigma": 0.0, "s1_sigma": 0.0}
    col = "mean_10000_100000"
    fixed = ER.one({**flat, "sigma2_sigma": 0.0}, 8)
    widened = ER.one({**flat, "sigma2_sigma": 0.3}, 8)
    assert fixed["refused"] is False and widened["refused"] is False
    assert np.ptp(fixed[col]) == 0.0
    assert np.ptp(widened[col]) > 0.0
    # ... but only just: a factor-2 swing in sigma^2 moves keV capture by a percent, because the
    # p-wave to s-wave level-density ratio has already saturated at 2l + 1 (see resonance-v0b.md).
    assert np.ptp(np.log10(widened[col])) < 0.05

    refused = ER.one({**job, "d0_log10": 6.0}, 12)  # D0 = 1 MeV
    assert refused["refused"] is True
    assert "refused" in refused["refusal_reason"]
    assert np.isnan(refused["thermal"]).all() and np.isnan(refused["ri"]).all()
