"""CREC (ROUTE100 WP4): the record codec, file format, `lru_cache` seeding and record key, without
a physics run. The chart-wide gate (warm runs from the records identical to WARM0's) is
`scripts/hf_route100_record.py verify`."""

from __future__ import annotations

import functools
from dataclasses import dataclass

import numpy as np
import pytest
import torch

from physics.hf.record import caches, codec, store


def test_codec_and_store_round_trip_bitwise(tmp_path):
    from physics.hf.direct.dwba import DirectLevels  # a physics.hf class the record rebuilds

    rng = np.random.default_rng(3)
    sparse = np.zeros((31, 2, 261))
    sparse[3, 1, 40:44] = rng.random(4)
    dense = rng.random((6, 77, 28))
    shared = torch.from_numpy(rng.random(5))
    obj = DirectLevels.__new__(DirectLevels)
    for f in getattr(DirectLevels, "__dataclass_fields__", {"x": None}):
        object.__setattr__(obj, f, dense[0, 0, :3].copy())
    value = {0.001684: (sparse, torch.from_numpy(sparse.copy()), 7, 2.5, None, "n"),
             (1, 2.0): [shared, shared, np.float32(1.1), complex(1, -2), frozenset({3})],
             "obj": obj, "dense": dense, "nan": float("nan")}
    enc = codec.Encoder()
    s = enc.encode(value)
    w = store.write(tmp_path / "x.crec", {"Z": 1}, [s], enc.arrays)
    assert w["bytes"] < w["dense_bytes"]  # the (31, 2, 261) arrays went sparse, and deduplicated
    rec = store.NuclideRecord(tmp_path / "x.crec")
    got = codec.Decoder(rec.array).decode(rec.entries[0])
    a, t, i, f, n, c = got[0.001684]
    assert np.array_equal(a, sparse) and a.flags.writeable
    assert torch.equal(t, torch.from_numpy(sparse))
    assert (i, f, n, c) == (7, 2.5, None, "n") and type(i) is int and type(f) is float
    lst = got[(1, 2.0)]
    assert lst[0] is lst[1] and torch.equal(lst[0], shared)  # shared by identity stays shared
    assert lst[2] == np.float32(1.1) and lst[2].dtype == np.float32
    assert lst[3] == complex(1, -2) and lst[4] == frozenset({3})
    assert type(got["obj"]) is DirectLevels
    assert np.array_equal(got["dense"], dense) and np.isnan(got["nan"])
    rec.close()


def test_encoder_refuses_structure_and_foreign_classes():
    @dataclass
    class Foreign:
        x: int = 1

    with pytest.raises(codec.Unrecordable):
        codec.Encoder().encode({"f": Foreign()})
    from physics.hf.input.defaults import default_options

    with pytest.raises(codec.Unrecordable):
        codec.Encoder(caches.REFUSE).encode([default_options(26, 56)])


_CALLS = []


@functools.lru_cache(maxsize=8)
def _cached(a: int, b: float, c: str = "x"):
    _CALLS.append((a, b, c))
    return {"v": a * b}


def test_seed_lru_stores_under_the_original_key():
    _cached.cache_clear()
    _CALLS.clear()
    _cached(1, 2.0)
    _cached(3, 4.0, c="y")
    items = [(caches._split_key(k), _cached(*caches._split_key(k)[0], **caches._split_key(k)[1]))
             for k in list(caches._lru_store(_cached))]
    assert len(items) == 2 and len(_CALLS) == 2
    _cached.cache_clear()
    for (args, kwargs), v in items:
        assert caches._seed_lru(_cached, args, kwargs, {"seeded": v["v"]})
    assert not caches._seed_lru(_cached, (1, 2.0), {}, None)  # already there: untouched
    assert _cached(1, 2.0) == {"seeded": 2.0} and _cached(3, 4.0, c="y") == {"seeded": 12.0}
    assert len(_CALLS) == 2  # every lookup was a hit
    assert _cached(5, 1.0)["v"] == 5.0 and len(_CALLS) == 3  # the function itself is restored


def test_recorded_caches_are_outside_the_taint_set():
    from physics.hf import warmrun

    assert not set(caches.RECORDED_LRU) & set(warmrun.DROP_LRU)
    assert not set(caches.RECORDED_DICTS) & set(warmrun.DROP_DICTS)
    assert not set(caches.RECORDED_ATTRS) & set(warmrun.DROP_ATTRS)
    assert set(caches._wrappers()) == set(caches.RECORDED_LRU)


def test_record_key_ignores_fit_parameters_and_nothing_else(monkeypatch):
    from types import SimpleNamespace

    from physics.hf import warmrun

    def cas(**kw):
        base = dict(Zt=26, At=56, k0=1, enincmax=20.0, energies=(1.0, 20.0), fit=(),
                    density_overrides=None, omp_overrides=None, diff_params=False)
        return SimpleNamespace(**{**base, **kw})

    key = caches.record_key(cas())
    caches.check_key(key, cas())
    # a PARAMWIRE parameter set reaches only the taint set, which a record never holds
    caches.check_key(key, cas(fit=(("aadjust", 26, 57, 1.1), ("ftable", 26, 57, 0.8))))
    for bad in (cas(energies=(1.0, 19.0)), cas(At=58), cas(density_overrides={"aadjust": 1.1}),
                cas(omp_overrides={"rvadjust": 1.02})):
        with pytest.raises(caches.RecordMismatch):
            caches.check_key(key, bad)
    monkeypatch.setattr(warmrun, "DROP_LRU", warmrun.DROP_LRU - {next(iter(warmrun.DROP_LRU))})
    with pytest.raises(caches.RecordMismatch):
        caches.check_key(key, cas())
