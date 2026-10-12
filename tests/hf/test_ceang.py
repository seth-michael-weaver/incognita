"""CEANG: physics/hf/compound/ceang.py -- TALYS's compound Blatt-Biedenharn Legendre coefficients from per-pair HF weights,
checked against an independent m-substate sum (sympy Clebsch-Gordan, no Racah algebra), on a spin-0 and an odd-A target."""

import math

import numpy as np
import pytest
from scipy.special import sph_harm_y
from sympy import Rational as R
from sympy.physics.wigner import clebsch_gordan

from physics.hf.compound import ceang


def _cg(j1, m1, j2, m2, j, m):  # doubled arguments
    return float(clebsch_gordan(R(j1, 2), R(j2, 2), R(j, 2), R(m1, 2), R(m2, 2), R(m, 2)))


def _mstate(J2, l, j2, two_i, lp, jp2, two_ip, th):
    """d sigma / d Omega for one compound channel pair a=(l,j) -> b=(l',j') through (J, M), incoherent over everything
    except the single M each initial substate feeds: beam along z (m_l = 0), unpolarised, random target M_I."""
    out = np.zeros_like(th)
    for mi in range(-two_i, two_i + 1, 2):
        for nu in (-1, 1):
            M = mi + nu
            if abs(M) > J2:
                continue
            w_in = _cg(2 * l, 0, 1, nu, j2, nu) ** 2 * _cg(j2, nu, two_i, mi, J2, M) ** 2
            if w_in == 0:
                continue
            for mf in range(-two_ip, two_ip + 1, 2):
                mp = M - mf
                if abs(mp) > jp2:
                    continue
                for nup in (-1, 1):
                    ml2 = mp - nup
                    if abs(ml2) > 2 * lp:
                        continue
                    w = _cg(jp2, mp, two_ip, mf, J2, M) ** 2 * _cg(2 * lp, ml2, 1, nup, jp2, mp) ** 2
                    out += w_in * w * np.abs(sph_harm_y(lp, ml2 // 2, th, 0.0)) ** 2
    return out


@pytest.mark.parametrize("two_i0,two_in,J2,pairs", [
    (0, 0, 3, [((1, 3), (1, 3))]),                    # spin-0 elastic, J=3/2-, p3/2 -> p3/2
    (0, 4, 5, [((2, 5), (0, 1)), ((2, 5), (2, 3))]),  # spin-0 -> 2+ level
    (7, 7, 6, [((1, 3), (3, 5)), ((3, 5), (1, 1)), ((3, 7), (3, 7))]),  # odd-A (7/2-) elastic, J=3
    (3, 1, 2, [((1, 1), (1, 3)), ((0, 1), (2, 3))]),  # odd-A 3/2 -> 1/2 level
])
def test_blatt_biedenharn_vs_mstate_sum(two_i0, two_in, J2, pairs):
    th = np.linspace(0.0, math.pi, 37)
    x = np.cos(th)
    for (l, j2), (lp, jp2) in pairs:
        M = np.array([[1.0]])
        rec = {"blocks": [{"J2": J2, "l_in": [l], "j2_in": [j2], "levels": {1: {"l_out": [lp], "j2_out": [jp2], "M": M}}}]}
        c = ceang.legendre(rec, 1, two_i0, two_in, 12)
        f = np.polynomial.legendre.legval(x, c * (2 * np.arange(13) + 1))
        ref = _mstate(J2, l, j2, two_i0, lp, jp2, two_in, th)
        # same shape, and 4 pi cleg_0 = M (the flux of the pair)
        assert 4 * math.pi * c[0] == pytest.approx(1.0, rel=1e-10)
        assert np.allclose(f / f.mean(), ref / ref.mean(), rtol=1e-9, atol=1e-12)


def test_matches_covang_when_denominator_constant():
    """With M = (2J+1) T_a T_b the exact builder reproduces angular.compound_elastic_legendre (COVANG) term for term."""
    from physics.hf.ecis import angular

    rng = np.random.default_rng(1)
    tjl = rng.uniform(0.05, 0.9, size=(1, 5, 2))
    tjl[0, 0, 0] = 0.0
    for two_i in (0, 3):
        ref = angular.compound_elastic_legendre(tjl, two_i)[0]
        blocks = []
        for two_j in range((two_i + 1) % 2, 2 * 4 + 1 + two_i + 1, 2):
            for par in (-1, 1):
                ch = [(l, jj, tjl[0, l, col]) for l in range(5) if (-1) ** l == par
                      for col, jj in ((0, 2 * l - 1), (1, 2 * l + 1)) if jj >= 0 and abs(two_j - two_i) <= jj <= two_j + two_i]
                if not ch:
                    continue
                t = np.array([c[2] for c in ch])
                blocks.append({"J2": two_j, "l_in": [c[0] for c in ch], "j2_in": [c[1] for c in ch],
                               "levels": {0: {"l_out": [c[0] for c in ch], "j2_out": [c[1] for c in ch],
                                              "M": (two_j + 1) * np.outer(t, t)}}})
        got = ceang.legendre({"blocks": blocks}, 0, two_i, two_i, ref.size - 1)
        assert np.allclose(got / got[0], ref / ref[0], rtol=1e-10, atol=1e-13)
