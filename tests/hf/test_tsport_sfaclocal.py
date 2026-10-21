"""TSPORT-SFACLOCAL (`INCOGNITA_TS_SFACLOCAL=1`): upstream TALYS 57de284 resets `sfactor` per cell
(TALYS 2c5d15f: binary.f90:232 (binary)).

* ON: `binary` no longer depends on the `sfactor` carried from earlier energies -- the result
  with the carried state equals the result with a fresh (zero) state;
* ON: the C per-type pass, the numpy body and the torch body still agree;
* the switch changes at least one call of a chained Nb-93 run (the stale-shape mechanism is
  exercised) and leaves calls with a fresh state alone.
"""

from __future__ import annotations

import os
from contextlib import contextmanager
from pathlib import Path

import pytest
import torch

from tests.hf.test_nx2_emit import _bcopy, _same, lever, needs_build

TALYS_DIR = Path(os.environ.get("TALYS_DIR", Path.home() / "opt/talys-src"))
needs_structure = pytest.mark.skipif(not (TALYS_DIR / "structure").is_dir(),
                                     reason="TALYS structure/ not installed")
RUN = (41, 93, (1.0, 5.0, 14.0, 20.0))


@contextmanager
def sfaclocal(on: bool):
    old = os.environ.get("INCOGNITA_TS_SFACLOCAL")
    os.environ["INCOGNITA_TS_SFACLOCAL"] = "1" if on else "0"
    try:
        yield
    finally:
        if old is None:
            os.environ.pop("INCOGNITA_TS_SFACLOCAL", None)
        else:
            os.environ["INCOGNITA_TS_SFACLOCAL"] = old


@pytest.fixture(scope="module")
def calls():
    """Every `binary` call of a chained Nb-93 run with production behaviour (state copied)."""
    from physics.hf import chartrun, engine as EN
    from physics.hf.engine import ChainedFull
    from physics.hf.input import fitlib

    torch.set_num_threads(1)
    # ENGSYNC: the stale-sfactor effect lives at TALYS's popeps 1e-3 residual cut; the engine default
    # (POPEPS3, 1e-9) removes it, so the premise run is pinned to TALYS's value (as conftest.talys_popeps).
    mp = pytest.MonkeyPatch()
    mp.setenv(fitlib.ENV, "lines")
    mp.setenv(fitlib.ENV_LINES, "popeps 1e-3")
    fitlib.deactivate()
    chartrun.drop_target_caches()
    fitlib.activate(41, 93)
    out = []
    ob = EN.binary

    def b(inp, state=None, device=None):
        out.append((inp, _bcopy(state)))
        return ob(inp, state, device)

    EN.binary = b
    try:
        with sfaclocal(False), torch.no_grad():
            Z, A, grid = RUN
            EN.run(injection=ChainedFull(Z=Z, A=A, declared_energies=grid))
    finally:
        EN.binary = ob
        mp.undo()
        fitlib.deactivate()
        chartrun.drop_target_caches()
    return out


def _result_fields(r):
    return {f: getattr(r, f) for f in r.__dataclass_fields__ if f != "sfactor"}


@needs_structure
def test_on_ignores_the_carried_state(calls):
    from physics.hf.emission.binary import BinaryState, binary

    n_moved = 0
    with torch.no_grad(), lever(False):
        for inp, st in calls:
            if st is None:
                continue
            with sfaclocal(True):
                got = binary(inp, _bcopy(st))
                fresh = binary(inp, BinaryState())
            _same(_result_fields(got), _result_fields(fresh), 0.0)
            with sfaclocal(False):
                old = binary(inp, _bcopy(st))
            try:
                _same(_result_fields(old), _result_fields(got), 0.0)
            except AssertionError:
                n_moved += 1
    assert n_moved > 0, "the stale-sfactor mechanism was not exercised"


@needs_build
@needs_structure
def test_on_c_and_numpy_bodies_match_the_torch_body(calls, monkeypatch):
    from physics.hf.emission import emit_nx2
    from physics.hf.emission.binary import binary

    with torch.no_grad(), sfaclocal(True):
        for inp, st in calls:
            with lever(False):
                ref = binary(inp, _bcopy(st))
            with lever(True):
                got = binary(inp, _bcopy(st))
                with monkeypatch.context() as m:
                    m.setattr(emit_nx2, "_kernel", lambda: None)
                    bare = binary(inp, _bcopy(st))
            _same(got, ref, 1e-12)
            _same(bare, ref, 0.0)
