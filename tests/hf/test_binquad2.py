"""BINQUAD2: in-bin knots of the Gauss sub-points (`binquadk`), the rho-tilted photon-exit quadrature
(`binquadp`), the compound nucleus's primary-photon population shape (`binquadc`) and its S edges (`snbincn`)."""
from dataclasses import replace

from physics.hf.core import grids
from physics.hf.input.defaults import Options


def test_off_by_default(monkeypatch):
    monkeypatch.delenv(grids.BINQUAD_ENV, raising=False)
    o = Options(26, 56, 1)
    assert (o.binquadk, o.binquadp, o.binquadc, o.snbincn) == (0, 0, 0, 0)
    assert grids.binquad_photon(o) == 0 and grids.binquad_knots(o) == 0


def test_only_under_binquad(monkeypatch):
    monkeypatch.delenv(grids.BINQUAD_ENV, raising=False)
    o = replace(Options(26, 56, 1), binquadp=2, binquadk=3)
    assert grids.binquad_photon(o) == 0 and grids.binquad_knots(o) == 0  # binquad n: TALYS
    o = replace(o, binquad="y")
    assert grids.binquad_photon(o) == 2 and grids.binquad_knots(o) == 3
    assert grids.binquad_photon(replace(o, binquadp=9)) == 0  # outside the GL table: off
