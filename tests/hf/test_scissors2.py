"""SCISSORS2: `INCOGNITA_M1_SCISSORS=s2` puts a deformation-scaled scissors on rotational nuclei
only (R4/2 >= 2.91) and leaves every other nucleus on TALYS's own term, bit for bit.
"""

from __future__ import annotations

import pytest

from physics.hf.gamma import scissors


def _cn(Z, A):
    from physics.hf.compound.dens_reference import _gamma_parameters
    return _gamma_parameters(Z, A)[0]


def test_rotor_classification():
    assert scissors.is_rotor(92, 239) and scissors.is_rotor(66, 164) and scissors.is_rotor(72, 180)
    # spherical / vibrational / soft: FRDM2012 alone would call Zr-96 (beta2 0.24) deformed
    for z, a in ((50, 120), (40, 96), (42, 98), (79, 197), (82, 208), (26, 57), (48, 114)):
        assert not scissors.is_rotor(z, a), (z, a)
        assert scissors.s2(z, a) is None


def test_s2_strength_is_the_oslo_scaling():
    e, g, t = scissors.s2(92, 239)
    d = 0.946 * 0.237
    assert e == pytest.approx(66.0 * d / 239 ** (1 / 3))
    assert g == scissors.GAMMA_MEV
    assert scissors.b_m1(e, t, g) == pytest.approx(scissors.KAPPA * 239 ** (4 / 3) * d * d)
    # inside the Oslo actinide band (Guttormsen 2014: 6-11 mu_N^2), well below Kopecky 2017
    assert 8.0 < scissors.b_m1(e, t, g) < 13.0


def test_switch_moves_rotors_only():
    prev = scissors.set_mode("")
    try:
        d_u, d_sn = _cn(92, 238), _cn(50, 119)
        scissors.set_mode("s2")
        s_u, s_sn = _cn(92, 238), _cn(50, 119)
        assert float(s_u.tpr_mb[0, 1, 1]) == pytest.approx(scissors.s2(92, 239)[2])
        assert float(s_u.tpr_mb[0, 1, 1]) != float(d_u.tpr_mb[0, 1, 1])
        assert float(s_u.sgr_mb[0, 1, 1]) == float(d_u.sgr_mb[0, 1, 1])
        for f in ("epr_mev", "gpr_mev", "tpr_mb", "sgr_mb", "upbend"):
            assert (getattr(s_sn, f) == getattr(d_sn, f)).all(), f
    finally:
        scissors.set_mode(prev)
