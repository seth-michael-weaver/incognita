"""STAGETIME: the always-on stage timer (physics/hf/stagetime.py) -- exclusive accounting, nesting,
exception safety, per-energy books, counters, the OFF switch, and one engine run whose stage sum is
its CPU time (timing never touches physics: ON vs OFF bit-identity is scripts/speed/stagetime_bench.py).
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from functools import lru_cache
from pathlib import Path

import pytest

from physics.hf import stagetime

REPO = Path(__file__).resolve().parents[2]


def _spin(sec: float) -> None:
    t = time.process_time()
    while time.process_time() - t < sec:
        pass


@pytest.fixture(autouse=True)
def _fresh():
    if not stagetime.ENABLED:
        pytest.skip("INCOGNITA_STAGETIME=0 in this environment")
    stagetime.reset()
    yield
    stagetime.reset()


def test_exclusive_nesting_sums_to_outer():
    t0 = time.process_time()
    with stagetime.stage("a"):
        _spin(0.02)
        with stagetime.stage("b"):
            _spin(0.03)
            with stagetime.stage("a"):  # re-entrant label
                _spin(0.01)
        _spin(0.01)
    total = time.process_time() - t0
    s = stagetime.snapshot()
    cpu = s["stage_cpu_s"]
    assert set(cpu) == {"a", "b"}
    assert cpu["b"] == pytest.approx(0.03, abs=0.006)
    assert cpu["a"] == pytest.approx(0.04, abs=0.008)
    assert sum(cpu.values()) == pytest.approx(total, abs=0.002)
    assert s["stage_calls"] == {"a": 2, "b": 1}
    assert s["open"] == []
    assert s["stage_wall_s"]["b"] > 0


def test_decorator_wraps_and_survives_exceptions():
    @stagetime.timed("boom")
    def f(x):
        """doc"""
        _spin(0.005)
        if x:
            raise ValueError("x")
        return 7

    assert f.__wrapped__.__doc__ == "doc" and f.__name__ == "f"
    assert f(0) == 7
    with pytest.raises(ValueError):
        with stagetime.stage("outer"):
            f(1)
    s = stagetime.snapshot()
    assert s["open"] == [] and s["stage_calls"]["boom"] == 2 and s["stage_calls"]["outer"] == 1
    assert s["stage_cpu_s"]["outer"] < s["stage_cpu_s"]["boom"]


def test_lru_cache_over_timed_books_misses_only():
    calls = []

    @lru_cache(maxsize=None)
    @stagetime.timed("build")
    def g(k):
        calls.append(k)
        return k * 2

    assert [g(1), g(1), g(2)] == [2, 2, 4]
    assert stagetime.snapshot()["stage_calls"]["build"] == 2 == len(calls)


def test_energy_books_and_counters_and_reset():
    stagetime.set_energy(1.5)
    with stagetime.stage("x"):
        _spin(0.003)
    stagetime.set_energy(None)
    with stagetime.stage("x"):
        pass
    stagetime.count("hits", 3)
    stagetime.count("hits")
    stagetime.count("zero", 0)
    s = stagetime.snapshot()
    assert list(s["stage_cpu_s_by_e"]["x"]) == ["1.5"]
    assert s["stage_cpu_s_by_e"]["x"]["1.5"] <= s["stage_cpu_s"]["x"]
    assert s["counters"] == {"hits": 4}
    json.dumps(s)  # npz/JSON-ready
    stagetime.reset()
    s = stagetime.snapshot()
    assert s["stage_cpu_s"] == {} and s["counters"] == {}


def test_off_switch_is_a_noop():
    code = ("from physics.hf import stagetime as s\n"
            "def f(): return 1\n"
            "assert s.timed('a')(f) is f\n"
            "with s.stage('a'): pass\n"
            "assert s.snapshot()['stage_cpu_s'] == {} and not s.ENABLED\n")
    env = dict(os.environ, INCOGNITA_STAGETIME="0", PYTHONPATH=str(REPO))
    r = subprocess.run([sys.executable, "-c", code], env=env, cwd=REPO, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr


def test_overhead_per_stage_is_microseconds():
    n = 20000
    t = time.perf_counter()
    for _ in range(n):
        with stagetime.stage("ovh"):
            pass
    per = (time.perf_counter() - t) / n
    assert per < 2e-5, per  # sanity bound (~2-8 us on the laptop); a run books ~300-600 stages; the gate is the paired bench


def test_engine_run_stage_sum_is_run_cpu():
    """One small engine run (Ca-40, 3 energies, engine defaults): stage sum within 2 % of its CPU-s."""
    pytest.importorskip("torch")
    from physics.hf.engine_c import lib

    if lib() is None:
        pytest.skip("native engine library not built")
    code = r"""
import json, os, time, torch
torch.set_num_threads(1)
from physics.hf import stagetime, warmrun
from physics.hf.engine import ChainedFull
from physics.hf.engine_c import run
e = (0.1, 1.0, 14.0)
t0 = time.process_time(); stagetime.reset()
with stagetime.stage("other"):
    cas = warmrun.new_cascade(20, 40, e)
    with torch.inference_mode():
        res = run(injection=ChainedFull(Z=20, A=40, declared_energies=e, cascade=cas))
cpu = time.process_time() - t0
s = stagetime.snapshot()
print(json.dumps({"cpu": cpu, "sum": sum(s["stage_cpu_s"].values()), "labels": list(s["stage_cpu_s"])}))
"""
    env = {k: v for k, v in os.environ.items() if not k.startswith("INCOGNITA_")}
    env.update(PYTHONPATH=str(REPO), OMP_NUM_THREADS="1")
    r = subprocess.run([sys.executable, "-c", code], env=env, cwd=REPO, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr[-2000:]
    got = json.loads(r.stdout.strip().splitlines()[-1])
    assert abs(got["sum"] - got["cpu"]) <= 0.02 * got["cpu"]
    for lab in ("compound", "incident", "multiple_emission", "preeq", "setup.ld", "output"):
        assert lab in got["labels"], (lab, got["labels"])
