"""Shared fixtures for tests/hf."""

from __future__ import annotations

import pytest

#: TALYS's residual-population cut (input_numerics.f90:82). Ours defaults to 1e-9 mb (POPEPS3 2026-10-12,
#: `input.defaults.Options.popeps_mb`); tests that compare with TALYS output, or with golden records made
#: at TALYS's value, pin this one.
TALYS_POPEPS = "1e-3"


@pytest.fixture
def talys_popeps(monkeypatch):
    """Run the test at TALYS's `popeps 1e-3`, as a deck line (`INCOGNITA_TALYS_FIT_LINES`, the path a run's
    extra deck lines take), with every per-target cache dropped on the way in and out so no option set
    leaks across tests.

    POPEPS3: `fitlib.modes()` reads the lines only when `INCOGNITA_TALYS_FIT` names an arm, and tests run
    with INCOGNITA_* unset, so the pin also sets the lines-only arm (`lines`); without it the deck line was
    silently dropped (POPEPS2 (a)). The pin is checked: a run built under it must carry popeps 1e-3."""
    from physics.hf import chartrun
    from physics.hf.input import fitlib

    fitlib.deactivate()
    chartrun.drop_target_caches()
    monkeypatch.setenv(fitlib.ENV, "lines")
    monkeypatch.setenv(fitlib.ENV_LINES, f"popeps {TALYS_POPEPS}")
    from physics.hf.input import defaults

    assert fitlib.activate(26, 56) is not None
    assert defaults.default_options(26, 56).popeps_mb == float(TALYS_POPEPS), "popeps pin is inert"
    fitlib.deactivate()
    chartrun.drop_target_caches()
    yield TALYS_POPEPS
    monkeypatch.delenv(fitlib.ENV_LINES, raising=False)
    monkeypatch.delenv(fitlib.ENV, raising=False)
    fitlib.deactivate()
    chartrun.drop_target_caches()


@pytest.fixture(autouse=True)
def _talys_point_geometry_triton(monkeypatch):
    """TFOLD (default ON; omp/tfold.py) folds the t / 3He diffuseness and scales cstrip t/h by 0.99; the tests that compare with
    TALYS output or golden records made before TFOLD run with the fold off. tests/hf/test_tfold.py removes the pin."""
    monkeypatch.setenv("INCOGNITA_TFOLD", "0")
