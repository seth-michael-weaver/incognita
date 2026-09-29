"""NATIVEX2 lever `emit`: `binary` and `exclusive_channels` off the graph hold the numbers of the
reference bodies they replace (`HF_NX2_EMIT=0`).

* every `binary` call of chained Fe-56 and U-238 runs (both engine call sites, the run-scoped
  `sfactor` state included), replayed through the C per-type pass, through the numpy body (no
  build) and through the torch body: every field, and the state left behind;
* every `exclusive_channels` call of the same runs (the carried `chanopen` state included):
  every result field and the state, to the bit;
* whole chained runs with the lever on and off;
* anything on the autograd graph keeps the torch body.

`binary`'s C pass uses libm's exp for the Wigner spin distribution: held to 1e-12 relative (seen
~5e-16). `exclusive_channels` is bit-identical.
"""

from __future__ import annotations

import math
import os
from contextlib import contextmanager
from pathlib import Path

import numpy as np
import pytest
import torch

TALYS_DIR = Path(os.environ.get("TALYS_DIR", Path.home() / "opt/talys-src"))
needs_structure = pytest.mark.skipif(not (TALYS_DIR / "structure").is_dir(),
                                     reason="TALYS structure/ not installed")


def _built() -> bool:
    from physics.hf.emission import emit_nx2

    return emit_nx2._kernel() is not None


needs_build = pytest.mark.skipif(not _built(), reason="no libnx2 build "
                                 "(scripts/build_nx2_native.sh)")

RUNS = ((26, 56, (0.001, 1.0, 5.0, 14.0, 20.0)), (92, 238, (0.8, 9.0)))


@contextmanager
def lever(on: bool):
    old = os.environ.get("HF_NX2_EMIT")
    os.environ["HF_NX2_EMIT"] = "1" if on else "0"
    try:
        yield
    finally:
        if old is None:
            os.environ.pop("HF_NX2_EMIT", None)
        else:
            os.environ["HF_NX2_EMIT"] = old


def _bcopy(st):
    from physics.hf.emission.binary import BinaryState

    return None if st is None else BinaryState({k: v.clone() for k, v in st.sfactor.items()})


def _ccopy(st):
    from physics.hf.emission.channels import ExclusiveState

    return None if st is None else ExclusiveState(set(st.chanopen), st.idnumfull)


def _same(a, b, rel: float, where=()):
    """Structural equality with floats and arrays to `rel` (0 -> exact), types included."""
    if isinstance(a, torch.Tensor) or isinstance(b, torch.Tensor):
        assert type(a) is type(b) and a.dtype == b.dtype and a.shape == b.shape, where
        x, y = a.detach().numpy(), b.detach().numpy()
        if rel == 0.0:
            assert np.array_equal(x, y, equal_nan=True), where
        else:
            den = np.maximum(np.abs(x), np.abs(y))
            assert (np.abs(x - y) <= rel * den).all(), where
    elif isinstance(a, np.ndarray):
        assert isinstance(b, np.ndarray) and np.array_equal(a, b, equal_nan=True), where
    elif isinstance(a, dict):
        assert isinstance(b, dict) and list(a) == list(b), where
        for k in a:
            _same(a[k], b[k], rel, where + (k,))
    elif isinstance(a, (list, tuple)):
        assert len(a) == len(b), where
        for i, (x, y) in enumerate(zip(a, b)):  # noqa: B905
            _same(x, y, rel, where + (i,))
    elif hasattr(a, "__dataclass_fields__"):
        assert type(a) is type(b), where
        for f in a.__dataclass_fields__:
            _same(getattr(a, f), getattr(b, f), rel, where + (f,))
    elif isinstance(a, float):
        assert type(a) is type(b), where
        if rel == 0.0 or not math.isfinite(a):
            assert a == b or (math.isnan(a) and math.isnan(b)), where
        else:
            assert abs(a - b) <= rel * max(abs(a), abs(b)), where
    else:
        assert a == b, where


@pytest.fixture(scope="module")
def captured():
    """The `binary` / `exclusive_channels` calls of the chained runs (state copied before each),
    and the runs' results, with the lever on."""
    from physics.hf import engine as EN
    from physics.hf.engine import ChainedFull

    torch.set_num_threads(1)
    calls = {"b": [], "c": [], "res": []}
    ob, oc = EN.binary, EN.exclusive_channels

    def b(inp, state=None, device=None):
        calls["b"].append((inp, _bcopy(state)))
        return ob(inp, state, device)

    def c(inp, state=None):
        calls["c"].append((inp, _ccopy(state)))
        return oc(inp, state)

    EN.binary, EN.exclusive_channels = b, c
    try:
        with lever(True), torch.no_grad():
            for Z, A, grid in RUNS:
                calls["res"].append(EN.run(injection=ChainedFull(Z=Z, A=A,
                                                                 declared_energies=grid)))
    finally:
        EN.binary, EN.exclusive_channels = ob, oc
    return calls


@needs_build
@needs_structure
def test_binary_c_and_numpy_bodies_match_the_torch_body(captured, monkeypatch):
    from physics.hf.emission import emit_nx2
    from physics.hf.emission.binary import binary

    assert len(captured["b"]) >= 2 * sum(len(g) for _, _, g in RUNS) - 2
    n_pe = 0
    with torch.no_grad():
        for inp, st in captured["b"]:
            s0, s1, s2 = _bcopy(st), _bcopy(st), _bcopy(st)
            with lever(False):
                ref = binary(inp, s0)
            with lever(True):
                got = binary(inp, s1)
                with monkeypatch.context() as m:
                    m.setattr(emit_nx2, "_kernel", lambda: None)
                    bare = binary(inp, s2)
            _same(got, ref, 1e-12)
            _same(bare, ref, 0.0)
            if st is not None:
                _same(s1, s0, 1e-12)
                _same(s2, s0, 0.0)
            n_pe += inp.flagpreeq
    assert n_pe > 0


@needs_structure
def test_exclusive_channels_fast_body_is_the_reference_to_the_bit(captured):
    from physics.hf.emission.channels import exclusive_channels

    fissioning = 0
    for inp, st in captured["c"]:
        s0, s1 = _ccopy(st), _ccopy(st)
        with lever(False):
            ref = exclusive_channels(inp, s0)
        with lever(True):
            got = exclusive_channels(inp, s1)
        _same(got, ref, 0.0)
        _same(s1, s0, 0.0)
        fissioning += inp.flagfission
    assert fissioning > 0 and len(captured["c"]) == sum(len(g) for _, _, g in RUNS)


@needs_build
@needs_structure
def test_whole_chained_runs_match_with_the_lever_off(captured):
    from physics.hf import engine as EN
    from physics.hf.engine import ChainedFull

    with lever(False), torch.no_grad():
        for (Z, A, grid), new in zip(RUNS, captured["res"]):  # noqa: B905
            old = EN.run(injection=ChainedFull(Z=Z, A=A, declared_energies=grid))
            assert list(new.e_inc_mev) == list(old.e_inc_mev)
            for got, ref in ((new.channels_mb, old.channels_mb), (new.totals_mb, old.totals_mb),
                             (new.levels_mb, old.levels_mb),
                             (new.residual_production_mb, old.residual_production_mb)):
                _same(got, ref, 1e-12)


@needs_structure
def test_binary_keeps_the_torch_body_on_the_graph(captured):
    from dataclasses import replace

    from physics.hf.emission import emit_nx2

    inp, st = captured["b"][-1]
    t = next(iter(inp.xspop_mb))
    pop = dict(inp.xspop_mb)
    pop[t] = pop[t].clone().requires_grad_(True)
    with lever(True), torch.enable_grad():
        assert emit_nx2.binary(replace(inp, xspop_mb=pop), _bcopy(st)) is None
    with lever(False):
        assert emit_nx2.binary(inp, _bcopy(st)) is None
        assert emit_nx2.exclusive_channels(captured["c"][-1][0], None) is None
