"""LOWEPOT (INCOGNITA_LOWEPOT, default OFF): rule arithmetic + engine wiring on a light target (Ti-48 sub-keV)."""
import numpy as np
import pytest

from physics.hf import lowepot


def test_edges_weight():
    lo, hi = lowepot.edges(17138.9)
    assert (lo, hi) == (1000.0 / 3, 1000.0)
    lo, hi = lowepot.edges(10.0)
    assert (lo, hi) == (5.0, 15.0)
    assert lowepot.edges(float("nan")) == (1000.0 / 3, 1000.0)
    w = lowepot.weight([1.0, 5.0, np.sqrt(75.0), 15.0, 1000.0], 5.0, 15.0)
    assert w[0] == 0 and w[1] == 0 and abs(w[2] - 0.5) < 1e-12 and w[3] == 1 and w[4] == 1


def test_on_is_default(monkeypatch):
    monkeypatch.delenv("INCOGNITA_LOWEPOT", raising=False)
    assert lowepot.on()
    monkeypatch.setenv("INCOGNITA_LOWEPOT", "0")
    assert not lowepot.on()
    monkeypatch.setenv("INCOGNITA_LOWEPOT", "1")
    assert lowepot.on()


def test_engine_ti48(monkeypatch):
    from physics.hf import engine_c, warmrun
    from physics.hf.engine import ChainedFull

    e = (float(np.float32(2.53e-8)), float(np.float32(1e-4)), 1e-3, 1.0)

    def run(flag):
        monkeypatch.setenv("INCOGNITA_LOWEPOT", flag)
        cas = warmrun.new_cascade(22, 48, e)
        return engine_c.run(injection=ChainedFull(Z=22, A=48, declared_energies=e, cascade=cas))

    off, on = run("0"), run("1")
    el0, el1 = off.totals_mb["elastic"].numpy(), on.totals_mb["elastic"].numpy()
    ce0 = off.totals_mb["compound_elastic"].numpy()
    shape = el0 - ce0
    assert np.allclose(el1[:2], shape[:2], rtol=1e-12)               # D0(Ti-49) >> 1 keV: w = 0 below 333 eV
    assert el1[2] == el0[2] and el1[3] == el0[3]                     # >= 1 keV untouched, bitwise
    assert 2.0 < el1[0] / 1e3 < 6.0                                  # ~ 4 pi R'^2 ~ 4 b (measured ~4 b)
    t0, t1 = off.totals_mb["total"].numpy(), on.totals_mb["total"].numpy()
    assert np.allclose(t0 - t1, el0 - el1, rtol=1e-12, atol=1e-9)
    for k, v in off.channels_mb.items():
        assert np.array_equal(v.numpy(), on.channels_mb[k].numpy()), k
