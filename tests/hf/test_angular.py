"""ELDA: physics/hf/ecis/angular.py (elastic / CC-level angular distributions from the incident CC S-matrix)."""

import os

import numpy as np
import pytest
import torch

from physics.hf.ecis import angular
from physics.hf.ecis.incident import _t4_parameters
from physics.hf.input.defaults import default_options

SAMPLE = os.path.expanduser("~/opt/talys-src/samples/n-Pb208-omp/org/nn0011.000ang.L00")


def _vib_band(e2, beta, spin=2.0):
    from physics.hf.ecis.reference import coupled_band

    b = dict(coupled_band(32, 74))
    b.update(e_mev=torch.tensor([0.0, e2], dtype=torch.float64), spin=torch.tensor([0.0, spin], dtype=torch.float64),
             parity=torch.tensor([1, 1]), vib_lambda=torch.tensor([0.0, 2.0], dtype=torch.float64),
             vib_beta=torch.tensor([beta], dtype=torch.float64), iphonon=torch.tensor([0, 1]), colltype="V")
    return b


def _rec(Z, A, e, band, lmax=25):
    o = default_options(Z, A)
    et = torch.tensor(e, dtype=torch.float64)
    return dict(omp=_t4_parameters(Z, A, 1, et, o), Z=Z, A=A, e=et, band=band, options=o, particle=1, lmax=lmax, refine=1)


def test_cg_racah_against_sympy():
    from sympy import Rational as R
    from sympy.physics.wigner import clebsch_gordan, racah

    assert angular.cg2(4, 2, 1, -1, 3, 1) == pytest.approx(float(clebsch_gordan(2, R(1, 2), R(3, 2), 1, R(-1, 2), R(1, 2))), abs=1e-12)
    assert angular.cg2(6, 0, 1, 1, 7, 1) == pytest.approx(float(clebsch_gordan(3, R(1, 2), R(7, 2), 0, R(1, 2), R(1, 2))), abs=1e-12)
    assert angular.racah2(5, 3, 5, 3, 4, 4) == pytest.approx(float(racah(R(5, 2), R(3, 2), R(5, 2), R(3, 2), 2, 2)), abs=1e-12)


def test_integrals_equal_cc_sums():
    """int dsigma/dOmega = the block sums sigma_shape_el / sigma_direct (Gauss-Legendre in cos theta is exact)."""
    x, w = np.polynomial.legendre.leggauss(120)
    th = np.rad2deg(np.arccos(x))
    g = angular.coupled_angular(_rec(50, 120, [4.0, 9.0], _vib_band(1.171, 0.12)), th)
    el = 2 * np.pi * (g["el_shape"] * w).sum(1)
    d1 = 2 * np.pi * (g["direct"][:, 1] * w).sum(1)
    np.testing.assert_allclose(el, g["sigma_shape_el"], rtol=1e-9)
    np.testing.assert_allclose(d1, g["sigma_direct"][:, 1], rtol=1e-9)


@pytest.mark.skipif(not os.path.exists(SAMPLE), reason="TALYS sample output not on this box")
def test_spherical_limit_matches_ecis_sample():
    """beta = 0: the shape-elastic DA of Pb-208 at 11 MeV equals ECIS's (TALYS sample n-Pb208-omp, stored output)."""
    ref = np.loadtxt(SAMPLE, comments="#")
    g = angular.coupled_angular(_rec(82, 208, [11.0], _vib_band(2.614, 0.0, 3.0), lmax=30), ref[:, 0], levels_out=[0])
    r = g["el_shape"][0] / ref[:, 2]
    assert abs(np.median(r) - 1) < 5e-4 and np.abs(r - 1).max() < 0.03


def test_record_only_when_enabled(monkeypatch):
    angular.RECORD.clear()
    monkeypatch.delenv(angular.ENV, raising=False)
    angular.record(Z=1)
    assert angular.RECORD == []
    monkeypatch.setenv(angular.ENV, "1")
    angular.record(Z=1)
    assert angular.RECORD == [{"Z": 1}]
    angular.RECORD.clear()


def test_compound_elastic_isotropic_for_s_wave_only():
    """Only l = 0 open on a 0+ target: the compound-elastic Legendre series is L = 0 only."""
    tjl = np.zeros((1, 3, 2))
    tjl[0, 0, 1] = 0.5
    c = angular.compound_elastic_legendre(tjl, 0)
    assert c[0, 0] > 0 and np.all(c[0, 1:] == 0)
