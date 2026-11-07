"""PERFCC2: the coupled-channels blocks on two threads, and the rows carried across target drops.

* `HF_CC_THREADS=2` (the default) runs the (J, parity) blocks of a solve on a helper thread as well
  as the caller's; every number must be the one-thread number, bit for bit, on both sides of
  `soswitch` (the W-form / modified Numerov kernel below, the derivative-coupling one above), for a
  batch and for a lone energy;
* `_BlockWorkers` returns results in item order, re-raises a helper's exception on the caller, and
  leaves no thread behind (the warm pool and `physics.hf.pool` fork only from one-thread processes);
* `incident._CARRY` serves a row again after `chartrun.drop_target_caches` emptied `_SOLVED`,
  the same tensor values, and misses when a numerics switch changed.

Task: PERFCC2. Test: tests/hf/test_ccthreads.py
"""

from __future__ import annotations

import threading

import pytest
import torch

from physics.hf.core.tensors import DTYPE
from physics.hf.ecis import ccnative
from physics.hf.ecis import incident as inc_mod
from physics.hf.ecis import solver

needs_kernel = pytest.mark.skipif(not ccnative.glue_available(),
                                  reason="libccfast.so not built (scripts/build_ccfast_native.sh)")

OBS = ("sigma_tot_mb", "sigma_reac_mb", "sigma_abs_mb", "sigma_shape_el_mb", "sigma_direct_mb",
       "tjl")


def _band(Z, A):
    from physics.hf.ecis.reference import coupled_band

    try:
        return coupled_band(Z, A)
    except Exception as exc:  # noqa: BLE001  (structure database absent on this machine)
        pytest.skip(f"no coupled band for {Z}-{A}: {exc}")


def _forget():
    inc_mod._SOLVED.clear()
    inc_mod._CARRY.clear()


def _solve(monkeypatch, threads: str, Z: int, A: int, e: torch.Tensor):
    monkeypatch.setenv("HF_CC_THREADS", threads)
    _forget()
    try:
        with torch.inference_mode():
            return inc_mod.incident_coupled(None, Z, A, e, _band(Z, A))[1]
    finally:
        _forget()


@needs_kernel
@pytest.mark.parametrize("energies", [(1.0e-3, 0.3, 4.0, 12.0, 20.0), (9.0,), (14.0,)])
def test_two_threads_give_the_one_thread_bits(monkeypatch, energies):
    e = torch.tensor(energies, dtype=DTYPE)
    one = _solve(monkeypatch, "1", 92, 238, e)
    two = _solve(monkeypatch, "2", 92, 238, e)
    for k in OBS:
        assert torch.equal(getattr(one, k), getattr(two, k)), k
    assert one.n_j == two.n_j


@needs_kernel
def test_no_helper_thread_outlives_a_solve(monkeypatch):
    before = threading.active_count()
    _solve(monkeypatch, "2", 92, 238, torch.tensor([1.5], dtype=DTYPE))
    assert threading.active_count() == before
    assert not [t for t in threading.enumerate() if t.name.startswith("cc-block-")]


def test_block_workers_keep_item_order_and_reraise():
    with solver._BlockWorkers(3) as w:
        assert w.map(lambda x: x * x, list(range(10))) == [x * x for x in range(10)]
        assert w.map(lambda x: -x, [7]) == [-7]

        def boom(x):
            if x == 4:
                raise ValueError("block 4")
            return x

        with pytest.raises(ValueError, match="block 4"):
            w.map(boom, list(range(6)))
        assert w.map(lambda x: x + 1, [1, 2, 3]) == [2, 3, 4]  # still usable after an error
    assert not [t for t in threading.enumerate() if t.name.startswith("cc-block-")]


def test_cc_threads_reads_the_switch(monkeypatch):
    monkeypatch.delenv("HF_CC_THREADS", raising=False)
    assert solver.cc_threads() == 2
    monkeypatch.setenv("HF_CC_THREADS", "1")
    assert solver.cc_threads() == 1
    monkeypatch.setenv("HF_CC_THREADS", "0")
    assert solver.cc_threads() == 1
    monkeypatch.setenv("HF_CC_THREADS", "x")
    assert solver.cc_threads() == 1


@needs_kernel
def test_carried_rows_survive_a_target_drop_and_miss_on_a_switch(monkeypatch):
    from physics.hf import chartrun

    monkeypatch.delenv("HF_CC_CARRY", raising=False)
    Z, A = 92, 238
    band = _band(Z, A)
    e = torch.tensor([1.5, 4.0], dtype=DTYPE)
    _forget()
    calls = []
    real = inc_mod.solve_rotational
    monkeypatch.setattr(inc_mod, "solve_rotational", lambda *a, **k: calls.append(1) or real(*a, **k))
    try:
        with torch.inference_mode():
            _, first = inc_mod.incident_coupled(None, Z, A, e, band)
            assert calls and len(inc_mod._CARRY) == 1
            chartrun.drop_target_caches()
            assert not inc_mod._SOLVED
            calls.clear()
            _, again = inc_mod.incident_coupled(None, Z, A, e, band)
            assert not calls
            for k in OBS:
                assert torch.equal(getattr(first, k), getattr(again, k)), k
            inc_mod._SOLVED.clear()
            monkeypatch.setenv("HF_CC_MODNUM", "0")  # another discretisation: must not be served
            inc_mod.incident_coupled(None, Z, A, e[:1], band)
            assert calls
            monkeypatch.delenv("HF_CC_MODNUM")
            inc_mod._SOLVED.clear()
            calls.clear()
            monkeypatch.setenv("HF_CC_CARRY", "0")
            inc_mod.incident_coupled(None, Z, A, e[:1], band)
            assert calls
    finally:
        _forget()
