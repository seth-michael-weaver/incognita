"""The stage disk cache returns exactly what it stored, keys on the optical-model inputs
and not on level-density ones, and is a no-op when unset.  Full-run checks are not part of
the unit tests."""

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


# ENGFIX4: the key covers every input that changes the stored transmissions -- the old allow-lists
# missed tfold / alphatemp / alphatemp_dom / tlog* (options and environment) and INCOGNITA_GRIDTOP


@pytest.mark.parametrize("field,value", [("tfold", False), ("alphatemp", 0.0), ("alphatemp_dom", "gd"),
                                         ("tlog", "c"), ("tlogit", True), ("tlogref", True)])
def test_key_follows_every_omp_option(cache, field, value):
    import dataclasses

    from physics.hf.input.defaults import default_options

    o = default_options(26, 56)
    assert getattr(o, field) != value
    k0 = S.key("t", (1,), options=(o,))
    assert S.key("t", (1,), options=(dataclasses.replace(o, **{field: value}),)) != k0


@pytest.mark.parametrize("var,value", [("INCOGNITA_TFOLD", "0"), ("INCOGNITA_ALPHATEMP", "0"),
                                       ("INCOGNITA_ALPHATEMP_DOM", "gd"), ("INCOGNITA_TLOG", "c"),
                                       ("INCOGNITA_TLOGIT", "y"), ("INCOGNITA_TLOGREF", "y"),
                                       ("INCOGNITA_GRIDTOP", "n"), ("INCOGNITA_CPINC", "p"),
                                       ("INCOGNITA_SOMETHING_NEW", "1")])
def test_key_follows_every_incognita_switch(cache, monkeypatch, var, value):
    monkeypatch.delenv(var, raising=False)
    k0 = S.key("t", (1,))
    monkeypatch.setenv(var, value)
    assert S.key("t", (1,)) != k0


def test_key_ignores_ld_options_and_cache_locations(cache, monkeypatch):
    import dataclasses

    from physics.hf.input.defaults import default_options

    o = default_options(26, 56)
    k0 = S.key("t", (1,), options=(o,))
    assert S.key("t", (1,), options=(dataclasses.replace(o, ldmodelall=2, strength=8),)) == k0
    monkeypatch.setenv("INCOGNITA_CC_CACHE", "/elsewhere")
    monkeypatch.setenv("INCOGNITA_STAGETIME", "1")
    assert S.key("t", (1,), options=(o,)) == k0


def test_excluded_inputs_not_read_by_stage_code():
    """A lever on a deny-list (`ENV_LEVERS`, `OPTION_EXCLUDE`) must not be read by the modules the
    cached stages execute (`ENV_NOT_INPUTS` -- cache locations, diagnostics, derived `*_EFF` -- may be)."""
    import re
    from pathlib import Path

    root = Path(S.__file__).resolve().parents[2]
    dirs = "\n".join(p.read_text(encoding="utf-8") for d in S._SOURCE_DIRS
                     for p in (root / d).rglob("*.py") if "__pycache__" not in p.parts)
    text = dirs + "\n".join((root / f).read_text(encoding="utf-8") for f in S._SOURCE_FILES
                            if f != "physics/hf/stagedisk.py")
    env_hits = sorted(v for v in S.ENV_LEVERS if re.search(rf"\b{v}\b", text))
    opt_hits = sorted(f for f in S.OPTION_EXCLUDE
                      if re.search(rf"(options|\bo|opts|opt)\.{f}\b|\"{f}\"", dirs))
    assert (env_hits, opt_hits) == ([], [])
