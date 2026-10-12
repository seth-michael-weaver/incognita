"""BINQUAD4: the WKB fission-penetrability table size (`binquadw`), decoupled from `bins` under `binquad y`."""
from dataclasses import replace

from physics.hf.core import grids
from physics.hf.fission.parameters import _nbinswkb
from physics.hf.input.defaults import Options


def test_off_by_default(monkeypatch):
    monkeypatch.delenv(grids.BINQUAD_ENV, raising=False)
    o = Options(92, 238, 1)
    assert o.binquadw == 0 and grids.binquad_wkb(o) == 0
    assert _nbinswkb(o) == o.nbins0 == 40  # TALYS: nbinswkb = nbins0
    assert _nbinswkb(replace(o, nbins0=0)) == 30


def test_only_under_binquad(monkeypatch):
    monkeypatch.delenv(grids.BINQUAD_ENV, raising=False)
    o = replace(Options(92, 238, 1), binquadw=240)
    assert _nbinswkb(o) == 40  # binquad n: TALYS
    o = replace(o, binquad="y")
    assert _nbinswkb(o) == 240 and _nbinswkb(replace(o, nbins0=240)) == 240
    assert _nbinswkb(replace(o, binquadw=0)) == 40
