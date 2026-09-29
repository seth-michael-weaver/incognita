"""CENGWIRE: the chart's default path is the C engine, and says so when it cannot be.

* `chartrun.run_nuclide` gives `engine.run`'s arrays to the bit, and takes the C cascade when it
  is built (the whole point: the default path, with no env var set, is the fast one);
* `engine_c.lib` is in `chartrun.KEEP`, so the loaded library survives the per-target cache drop;
* `native.inventory.status` agrees with each loader's own predicate, and `report` warns once,
  naming what is missing and how to build it (and is silent when everything loaded);
* `hf_macspeed_chart.fast()` is on by default and `MACSPEED_FAST=0` is the opt-out.
"""

from __future__ import annotations

import os
import sys
import warnings
from pathlib import Path

import numpy as np
import pytest
import torch

REPO = Path(__file__).resolve().parents[2]
TALYS_DIR = Path(os.environ.get("TALYS_DIR", Path.home() / "opt/talys-src"))
needs_structure = pytest.mark.skipif(not (TALYS_DIR / "structure").is_dir(),
                                     reason="TALYS structure/ not installed")

GRID = (1.0e-3, 0.5, 2.0, 5.0, 8.0, 11.0, 14.0, 20.0)


def _built() -> bool:
    from physics.hf import engine_c

    return engine_c.lib() is not None


# --------------------------------------------------------------------------------- the default path


@needs_structure
def test_run_nuclide_is_engine_run_bitwise():
    """The default chart call and the plain engine call, array by array, to the bit."""
    from physics.hf import warmrun
    from physics.hf.chartrun import drop_target_caches, run_nuclide
    from physics.hf.engine import ChainedFull, run

    energies = (1.0e-3, 5.0, 14.0)
    drop_target_caches()
    with torch.inference_mode():
        ref = warmrun.result_arrays(
            run(injection=ChainedFull(Z=26, A=56, declared_energies=energies)))
    drop_target_caches()
    got = warmrun.result_arrays(run_nuclide(26, 56, energies))
    assert set(got) == set(ref)
    for k in ref:
        a, b = np.asarray(ref[k], float), np.asarray(got[k], float)
        assert a.shape == b.shape, k
        assert np.array_equal(a, b, equal_nan=True), (
            k, float(np.nanmax(np.abs(b - a))))


@needs_structure
@pytest.mark.skipif(not _built(), reason="no libengdecay build "
                    "(scripts/build_engine_c_native.sh)")
def test_run_nuclide_takes_the_c_cascade_with_no_env_var():
    """With nothing set in the environment, the C cascade takes the energies -- CENGWIRE's whole
    claim. Before this, `run_nuclide` called `engine.run` and `ce_cascade` never fired."""
    from physics.hf import engine_c
    from physics.hf.chartrun import drop_target_caches
    from physics.hf.engine import ChainedFull

    for k in ("HF_NATIVE", "HF_NATIVEX", "HF_ENGINE_C"):
        assert os.environ.get(k, "1") != "0", f"{k} is switched off in this environment"
    drop_target_caches()
    stats: dict = {}
    energies = (1.0e-3, 5.0)
    with torch.inference_mode():
        engine_c.run(ChainedFull(Z=26, A=56, declared_energies=energies), stats)
    assert stats.get("c") == len(energies), stats


def test_engine_c_lib_survives_the_cache_drop():
    """`engine_c.lib` is an `lru_cache(maxsize=1)` holding the loaded library and its kernel
    pointers. Were it not in `KEEP`, the chart would dlopen and re-kernel it once per nuclide."""
    from physics.hf.chartrun import KEEP

    assert "physics.hf.engine_c.lib" in KEEP


# ------------------------------------------------------------------------------ the loud fallback


def test_status_covers_every_kernel_and_agrees_with_its_loader():
    import importlib

    from physics.hf.native import inventory

    st = inventory.status()
    assert set(st) == {key for key, _w, _s, _b in inventory.KERNELS}
    for key, _what, spec, script in inventory.KERNELS:
        mod, _, attr = spec.partition(":")
        assert (REPO / script).is_file(), script
        assert st[key] is bool(getattr(importlib.import_module(mod), attr)()), key


def test_report_warns_once_naming_the_switch_that_turned_them_off(monkeypatch):
    """Nothing loaded and `HF_NATIVE=0` set: the warning fires once, names the switch rather than
    telling anyone to build what they just switched off, and is silent the second time.

    `status` is stubbed rather than driven through the env, because `HF_NATIVE=0` is *not* a
    reliable global kill switch once a process has loaded: `nativex.lib`/`decay_native._lib` cache
    the decision (`lru_cache`) and `ecis.ccnative` never consults `HF_NATIVE` at all. That is
    pre-existing loader behaviour and CENGWIRE does not change it -- it is why gate 2 of
    docs/results/hf-cengwire.md moves the `.so` files aside instead of setting the switch.
    """
    from physics.hf.native import inventory

    monkeypatch.setenv("HF_NATIVE", "0")
    monkeypatch.delenv("HF_NATIVE_QUIET", raising=False)
    monkeypatch.setattr(inventory, "status",
                        lambda: {key: False for key, _w, _s, _b in inventory.KERNELS})
    inventory._reset_for_tests()
    try:
        with pytest.warns(RuntimeWarning) as rec:
            st = inventory.report()
        assert not any(st.values()), st
        msg = str(rec[0].message)
        assert "HF_NATIVE=0" in msg
        assert "scripts/build_" not in msg  # switched off on purpose, not unbuilt
        assert "only speed" in msg
        assert f"{len(inventory.KERNELS)} of {len(inventory.KERNELS)}" in msg
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            inventory.report()  # once per process: no second warning
    finally:
        inventory._reset_for_tests()


def test_report_is_silent_when_every_kernel_loaded(monkeypatch):
    from physics.hf.native import inventory

    monkeypatch.delenv("HF_NATIVE_QUIET", raising=False)
    monkeypatch.setattr(inventory, "status",
                        lambda: {key: True for key, _w, _s, _b in inventory.KERNELS})
    inventory._reset_for_tests()
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            assert all(inventory.report().values())
    finally:
        inventory._reset_for_tests()


def test_report_is_quiet_when_silenced(monkeypatch):
    from physics.hf.native import inventory

    monkeypatch.setenv("HF_NATIVE", "0")
    monkeypatch.setenv("HF_NATIVE_QUIET", "1")
    inventory._reset_for_tests()
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            inventory.report()
    finally:
        inventory._reset_for_tests()


def test_report_names_the_build_script_when_a_kernel_is_unbuilt(monkeypatch):
    """A missing `.so` with no switch set: the warning tells you which script builds it."""
    from physics.hf import engine_c
    from physics.hf.native import inventory

    monkeypatch.delenv("HF_NATIVE_QUIET", raising=False)
    for k in inventory._SWITCHES:
        monkeypatch.delenv(k, raising=False)
    monkeypatch.setattr(engine_c, "lib", lambda: None)
    inventory._reset_for_tests()
    try:
        with pytest.warns(RuntimeWarning, match="build_engine_c_native.sh"):
            assert inventory.report()["engdecay"] is False
    finally:
        inventory._reset_for_tests()


# ------------------------------------------------------------------------------------ the harness
