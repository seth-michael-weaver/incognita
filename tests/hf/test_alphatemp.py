"""ALPHATEMP: residual-excitation-dependent alpha transmission (physics/hf/omp/alphatemp.py), default ON (0.64)."""
import numpy as np

import dataclasses

from physics.hf.input.defaults import Options
from physics.hf.omp import alphatemp


def test_default_on_and_overrides(monkeypatch):
    monkeypatch.delenv("INCOGNITA_ALPHATEMP", raising=False)
    f = {x.name: x for x in dataclasses.fields(Options)}["alphatemp"]
    assert f.default == 0.64 == alphatemp.DEFAULT_TSTAR
    assert alphatemp.tstar(type("O", (), {"alphatemp": 0.64})()) == 0.64
    assert alphatemp.tstar(type("O", (), {"alphatemp": 0.0})()) == 0.0  # keyword alphatemp 0 = OFF = TALYS
    assert alphatemp.tstar(type("O", (), {"alphatemp": 0.5})()) == 0.5
    monkeypatch.setenv("INCOGNITA_ALPHATEMP", "0")
    assert alphatemp.tstar(type("O", (), {"alphatemp": 0.64})()) == 0.0
    assert alphatemp.tstar(type("O", (), {"alphatemp": 0.5})()) == 0.5


def test_mix_limits_and_geometric_mean():
    hot, cold = np.array([4.0, 0.0, 1e-3]), np.array([1.0, 2.0, 1e-5])
    assert np.allclose(alphatemp.mix(hot, cold, np.array(1.0)), hot)
    assert np.allclose(alphatemp.mix(hot, cold, np.array(0.0)), cold)
    m = alphatemp.mix(hot, cold, np.array(0.5))
    assert np.isclose(m[0], 2.0) and np.isclose(m[1], 1.0) and np.isclose(m[2], 1e-4)


def test_weight_scale():
    u = alphatemp.ustar(56, 0.64)
    assert np.isclose(u, 7.0 * 0.64 ** 2)
    assert np.allclose(alphatemp.weight([-1.0, 0.0, u / 2, u, 3 * u], u), [0, 0, 0.5, 1, 1])


def test_kevcold_domain_default_n(monkeypatch):
    """ALPHAPROMO: the global rule (n) is the default; gd stays a keyword."""
    monkeypatch.delenv("INCOGNITA_ALPHATEMP_DOM", raising=False)
    f = {x.name: x for x in dataclasses.fields(Options)}["alphatemp_dom"]
    assert f.default == "n" == alphatemp.DEFAULT_DOM
    assert alphatemp.domain(type("O", (), {"alphatemp_dom": "n"})()) == "n"
    assert alphatemp.domain(type("O", (), {"alphatemp_dom": "gd"})()) == "gd"
    monkeypatch.setenv("INCOGNITA_ALPHATEMP_DOM", "gd")
    assert alphatemp.domain(type("O", (), {"alphatemp_dom": "n"})()) == "gd"
    assert not alphatemp.dom_on({"alphatemp_dom": "gd"})
    assert alphatemp.dom_on({"alpha_cold": (0, 0), "alphatemp_dom": "gd"})
    assert not alphatemp.cascade_cold({"alpha_cold": (0, 0), "alphatemp_dom": "gd"})
    assert alphatemp.cascade_cold({"alpha_cold": (0, 0), "alphatemp_dom": "n"})


def test_kevcold_ericson_boundary(monkeypatch):
    """Gamma/D = denomhf / 2 pi; isolated (< 1) and live cells only."""
    monkeypatch.delenv("INCOGNITA_ALPHATEMP_DOM_LOG", raising=False)
    tp = 2.0 * np.pi
    cells = [(1, -1), (3, -1), (5, 1), (7, 1)]
    gd = alphatemp.gd_cells(cells, [0.0, 0.5 * tp, 0.999 * tp, 1.0 * tp])
    assert gd.tolist() == [False, True, True, False]
