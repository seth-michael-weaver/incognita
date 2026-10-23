"""HEAVYMEM (development notes): bounded per-run fission barrier grids and worker memory hygiene, no number moved."""

from __future__ import annotations

import functools

import pytest

from physics.hf import chartrun
from physics.hf.fission import chain as fch


class _Grid:
    def __init__(self, key):
        self.key = key


@pytest.fixture
def built(monkeypatch):
    calls = []

    def fake(fp, ld, key, *, odd=0, maxj=0):
        calls.append(key)
        return _Grid(key)

    import physics.hf.fission.transmission as tr

    monkeypatch.setattr(tr, "fission_level_densities", fake)
    return calls


def _chain():
    c = fch.FissionChain.__new__(fch.FissionChain)
    c.maxj = 3
    return c


def test_grids_are_bounded_and_hits_return_the_same_object(built, monkeypatch):
    monkeypatch.setenv("INCOGNITA_HEAVYMEM", "1")
    c, n = _chain(), fch._Nucleus(fp=None, ld=None, odd=0, grids={})
    g1 = c._grid(n, 10.0)
    assert c._grid(n, 10.0) is g1
    n.__dict__["_fissb_coef"] = {(id(g1), 1): (g1, "coef")}
    c._grid(n, 11.0)
    c._grid(n, 12.0)  # evicts 10.0 and its coefficient entry
    assert list(n.grids) == [11.0, 12.0] and len(n.grids) == fch.GRID_KEEP
    assert n.__dict__["_fissb_coef"] == {}
    assert built == [10.0, 11.0, 12.0]
    c._grid(n, 11.0)  # LRU: 11.0 is now the most recent
    c._grid(n, 13.0)
    assert list(n.grids) == [11.0, 13.0]


def test_off_switch_keeps_every_grid(built, monkeypatch):
    monkeypatch.setenv("INCOGNITA_HEAVYMEM", "0")
    c, n = _chain(), fch._Nucleus(fp=None, ld=None, odd=0, grids={})
    for e in (1.0, 2.0, 3.0, 4.0):
        c._grid(n, e)
    assert list(n.grids) == [1.0, 2.0, 3.0, 4.0]


def test_drop_clears_class_level_method_caches(monkeypatch):
    monkeypatch.setenv("INCOGNITA_HEAVYMEM", "1")
    from physics.hf.emission.feeding import Cascade

    import numpy as np

    w = vars(Cascade)["_sep"]
    assert isinstance(w, functools._lru_cache_wrapper)

    class _M:
        s_mev = np.zeros((1, 1, 7))

    class _Self:  # hashable stand-in for a finished target's Cascade
        m = _M()

    w.cache_clear()
    w(_Self(), 0, 0)
    assert w.cache_info().currsize == 1
    chartrun.drop_target_caches()
    assert w.cache_info().currsize == 0
