"""XDHARD: binary emission spectra (physics/hf/emission/binspec.py) -- output only."""
from types import SimpleNamespace

import numpy as np
import torch

from physics.hf.emission import binspec


def test_full_xsbinary_adds_direct_and_preeq():
    b2 = SimpleNamespace(xsbinary_mb=torch.tensor([0.5, 1.0, 10.0, 5.0, 0.2, 0.0, 0.0, 2.0], dtype=torch.float64),
                         grids={0: None, 1: None, 2: None, 3: None, 6: None}, flagpreeq=True,
                         xsdirdisctot_mb={1: 3.0, 3: 0.1}, xspreeqtot_mb={1: 7.0, 2: 1.5, 3: 0.4, 6: 0.3},
                         xsgrtot_mb={1: 0.25})
    out = binspec.full_xsbinary(b2)
    assert out == [0.5, 1.0, 10.0 + 3.0 + 7.0 + 0.25, 5.0 + 1.5, 0.2 + 0.1 + 0.4, 0.0, 0.0, 2.0 + 0.3]
    b2.flagpreeq = False
    assert binspec.full_xsbinary(b2)[2] == 13.0


def test_edges_match_grid_f90():
    eg = np.array([0.0, 0.1, 0.2, 0.4, 0.8, 1.6])
    eb, et, de = binspec._edges(eg, 5)
    assert np.isclose(de[1], 0.15) and et[1] == de[1] and eb[1] == 0.0
    assert np.isclose(de[3], 0.3) and np.isclose(et[3], 0.6) and np.isclose(eb[3], 0.3)
    assert np.isclose(de[5], 0.4) and et[5] == 1.6


def test_binemission_interpolates_bin_density():
    r = SimpleNamespace(nlast=0, maxex=3, sep_mev=1.0, ex_mev=np.array([0.0, 1.0, 2.0, 3.0]), dex_mev=np.array([0.0, 1.0, 1.0, 1.0]))
    pinp = SimpleNamespace(egrid_mev=np.arange(0.0, 10.0, 0.5), ebegin={3: 1}, eend={3: 18}, residuals={3: r}, etotal_mev=6.0)
    xs, _ = binspec.binemission(pinp, 3, np.array([0.0, 2.0, 2.0, 2.0, 0.0]), 6.0)
    # Eo(nex) = 6 - 1 - Ex = 4, 3, 2 for nex 1..3: a flat 2 mb/MeV density between 2 and 4 MeV, zero at/above Eo(NL) = 5
    assert np.allclose(xs[(pinp.egrid_mev >= 2.0) & (pinp.egrid_mev <= 4.0)], 2.0)
    assert np.all(xs[pinp.egrid_mev >= 5.0] == 0.0)


def test_disabled_by_default(monkeypatch):
    monkeypatch.delenv("INCOGNITA_BINSPEC", raising=False)
    assert not binspec.enabled()
    monkeypatch.setenv("INCOGNITA_BINSPEC", "1")
    assert binspec.enabled()
