"""STAGETIME: always-on per-stage CPU / wall timer for engine runs.

A stack of open stages; each stage books its EXCLUSIVE time (its own time minus the time of the
stages opened inside it) to its label, on `time.process_time` (CPU-s) and `time.perf_counter`
(wall-s). So lazily built set-up (level densities, inverse transmissions, the photon strength,
a coupled-channels solve) reached from inside a reaction stage is booked to the set-up label and
not to the stage that happened to ask for it first. Native C / torch / GPU work is timed at its
Python call boundary.

    from physics.hf import stagetime
    with stagetime.stage("compound"):
        ...
    @stagetime.timed("setup.ld")
    def _ld_build(...): ...

    stagetime.reset()
    with stagetime.stage("other"):      # the run itself: whatever no stage claims lands here
        run()
    rec = stagetime.snapshot()          # {"stage_cpu_s": {...}, "stage_wall_s": {...}, ...}

Timing never touches physics: it reads two clocks and updates dicts. `INCOGNITA_STAGETIME=0` (read
once, at import) turns every `stage` into a shared no-op context and every `timed` into the
undecorated function, for the on/off identity and overhead checks.

Labels (shared with SPEEDPROF): startup, setup.cascade, setup.params, setup.structure,
setup.levels, setup.ld, setup.psf, setup.omp_inverse, incident, incident.cc_cache,
incident.cc_solve, direct_dwba, direct_capture, preeq, compound, fission, multiple_emission,
multiple_emission.widths, channels, output, other.  Single-threaded engine only: the stack is
module state, not per thread.

Test: tests/hf/test_stagetime.py
"""
from __future__ import annotations

import functools
import os
import time

ENABLED = os.environ.get("INCOGNITA_STAGETIME", "1").strip().lower() not in ("0", "n", "no", "off")

_cpu = time.process_time
_wall = time.perf_counter

_STACK: list[list] = []                      # [label, cpu0, wall0, child_cpu, child_wall]
_CPU: dict[str, float] = {}
_WALL: dict[str, float] = {}
_CALLS: dict[str, int] = {}
_CPU_E: dict[tuple[str, float], float] = {}  # (label, incident energy) -> exclusive CPU-s
_COUNT: dict[str, int] = {}
_ENERGY: list = [None]


def _close(fr) -> None:
    c1 = _cpu()
    w1 = _wall()
    _STACK.pop()
    lab = fr[0]
    dc = c1 - fr[1]
    dw = w1 - fr[2]
    xc = dc - fr[3]
    _CPU[lab] = _CPU.get(lab, 0.0) + xc
    _WALL[lab] = _WALL.get(lab, 0.0) + dw - fr[4]
    _CALLS[lab] = _CALLS.get(lab, 0) + 1
    e = _ENERGY[0]
    if e is not None:
        k = (lab, e)
        _CPU_E[k] = _CPU_E.get(k, 0.0) + xc
    if _STACK:
        p = _STACK[-1]
        p[3] += dc
        p[4] += dw


class _Stage:
    __slots__ = ("label",)

    def __init__(self, label: str):
        self.label = label

    def __enter__(self):
        fr = [self.label, 0.0, 0.0, 0.0, 0.0]
        _STACK.append(fr)
        fr[2] = _wall()
        fr[1] = _cpu()
        return self

    def __exit__(self, *exc):
        _close(_STACK[-1])
        return False


class _Null:
    __slots__ = ()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


_NULL = _Null()
_STAGES: dict[str, _Stage] = {}


def stage(label: str):
    """Context manager booking the block's exclusive time to `label` (no-op when disabled)."""
    if not ENABLED:
        return _NULL
    s = _STAGES.get(label)
    if s is None:
        s = _STAGES[label] = _Stage(label)
    return s


def timed(label: str):
    """Decorator form of `stage` (returns the function itself when disabled)."""
    def deco(fn):
        if not ENABLED:
            return fn

        @functools.wraps(fn)
        def wrapped(*a, **k):
            fr = [label, 0.0, 0.0, 0.0, 0.0]
            _STACK.append(fr)
            fr[2] = _wall()
            fr[1] = _cpu()
            try:
                return fn(*a, **k)
            finally:
                _close(fr)

        return wrapped

    return deco


def count(key: str, n: int = 1) -> None:
    """Add `n` to a named counter (cache hits/misses, fallbacks)."""
    if ENABLED and n:
        _COUNT[key] = _COUNT.get(key, 0) + int(n)


def set_energy(e_inc_mev) -> None:
    """Book following stage time to this incident energy too (None = outside the energy loop)."""
    _ENERGY[0] = None if e_inc_mev is None else round(float(e_inc_mev), 6)


def reset() -> None:
    """Clear every book (start of a target). Open stages stay open."""
    _CPU.clear()
    _WALL.clear()
    _CALLS.clear()
    _CPU_E.clear()
    _COUNT.clear()
    _ENERGY[0] = None


def snapshot() -> dict:
    """JSON-ready copy of the books: per-label exclusive CPU-s / wall-s / calls, counters, and
    per-energy CPU-s (`stage_cpu_s_by_e[label][str(E)]`)."""
    by_e: dict[str, dict[str, float]] = {}
    for (lab, e), v in _CPU_E.items():
        by_e.setdefault(lab, {})[repr(e)] = v
    return {
        "enabled": ENABLED,
        "stage_cpu_s": dict(sorted(_CPU.items(), key=lambda kv: -kv[1])),
        "stage_wall_s": dict(_WALL),
        "stage_calls": dict(_CALLS),
        "stage_cpu_s_by_e": by_e,
        "counters": dict(_COUNT),
        "open": [fr[0] for fr in _STACK],
    }
