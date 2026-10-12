"""STAGECACHE: the stage disk cache returns exactly what it stored, keys on the optical-model inputs
and not on level-density ones, and is a no-op when unset.  Gates on full runs:
development notes."""

from __future__ import annotations

import numpy as np
import pytest
import torch

from physics.hf import stagedisk as S


@pytest.fixture
def cache(tmp_path, monkeypatch):
    monkeypatch.setenv(S.ENV_VAR, str(tmp_path))
    S.reset_stats()
    yield tmp_path
    S.reset_stats()


def _counter():
    n = [0]

    def compute():
        n[0] += 1
        return {"x": np.array([1.0, -0.0, 0.0]), "t": torch.tensor([[0.5, 0.0], [0.0, -0.0]]),
                "s": "R", "f": 1.25, "n": None, "tup": (1, 2.5)}
    return n, compute


def test_off_is_plain_compute(monkeypatch):
    monkeypatch.delenv(S.ENV_VAR, raising=False)
    n, compute = _counter()
    S.cached("t", (1,), compute)
    S.cached("t", (1,), compute)
    assert n[0] == 2 and S.stats() == {}


def test_round_trip_bit_exact(cache):
    n, compute = _counter()
    a = S.cached("t", (1,), compute)
    b = S.cached("t", (1,), compute)
    assert n[0] == 1 and S.stats()["t"]["hit"] == 1
    assert a["x"].tobytes() == b["x"].tobytes()
    assert a["t"].numpy().tobytes() == b["t"].numpy().tobytes() and b["t"].dtype == a["t"].dtype
    assert (b["s"], b["f"], b["n"], b["tup"]) == ("R", 1.25, None, (1, 2.5))


def test_key_follows_omp_inputs_not_ld(cache):
    from physics.hf.input.defaults import Params, default_options, default_params

    o = default_options(26, 56)
    p = default_params(26, 56, o)
    k0 = S.key("t", (1,), options=(o,), params=(p,))
    # a level-density parameter is not an input of the cached stages
    p_ld = Params({k: v.clone() for k, v in p.values.items()})
    p_ld.values["ctable"] += 0.3
    assert S.key("t", (1,), options=(o,), params=(p_ld,)) == k0
    # an optical-model one is
    p_omp = Params({k: v.clone() for k, v in p.values.items()})
    p_omp.values["rvadjust"] *= 1.02
    assert S.key("t", (1,), options=(o,), params=(p_omp,)) != k0
    # and so is an in-place change of a keyed tensor (version counter)
    t = p.values["rvadjust"]
    if not t.is_inference():
        t.mul_(1.0)
        t.mul_(1.02)
        assert S.key("t", (1,), options=(o,), params=(p,)) != k0


def test_key_follows_env(cache, monkeypatch):
    k0 = S.key("t", (1,))
    monkeypatch.setenv("HF_NX2_OMP", "0")
    assert S.key("t", (1,)) != k0
    monkeypatch.delenv("HF_NX2_OMP")
    monkeypatch.setenv("INCOGNITA_OMP_DEFORMED", "1")
    assert S.key("t", (1,)) != k0
    monkeypatch.delenv("INCOGNITA_OMP_DEFORMED")
    monkeypatch.setenv("INCOGNITA_TRAPFIX", "0")  # a cascade switch: not an input
    assert S.key("t", (1,)) == k0


def test_corrupt_file_is_a_miss(cache):
    n, compute = _counter()
    S.cached("t", (2,), compute)
    for f in cache.rglob("*.stc"):
        f.write_bytes(f.read_bytes()[:40])
    S._BYTES.clear()
    S.cached("t", (2,), compute)
    assert n[0] == 2 and S.stats()["t"]["bad"] == 1
