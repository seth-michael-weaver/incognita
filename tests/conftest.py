"""Suite-wide hooks (see tests/_data.py).

* `needs_data(*paths)` / `needs_main(*paths)` markers: skip unless the lab files exist.
* A test that fails only because the TALYS structure database is not installed (the locators
  raise FileNotFoundError "TALYS structure database not found") is reported as skipped, with
  the fix; with TALYS installed the hook never fires.
* The nx2 kernels are (re)loaded before each test, so switch-off arms cannot leak (`_prime_nx2`).
"""

from __future__ import annotations

import pytest

from tests._data import TALYS_MISSING, need_data, need_main

_TALYS_SKIP = "TALYS structure database not installed: set TALYS_DIR (docs/talys-install.md)"


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line(
        "markers", "needs_data(*paths): skip unless these repo-relative lab data paths exist "
        "(they are not shipped in the public tree)")
    config.addinivalue_line(
        "markers", "needs_main(*paths): skip unless these main-checkout data files exist in the "
        "repo or under $INCOGNITA_MAIN (not shipped in the public tree)")


def _prime_nx2() -> None:
    """Keep the nx2 kernels loaded between tests. `nx2.lib()` caches its first answer for the
    process, switches included, and several tests drop every `physics.hf` lru cache
    (`chartrun.drop_target_caches`). In a full run with TALYS some later test reloads it with the
    switches on before test_native's HF_NATIVE=0 reference arm runs, and that arm's bitwise
    comparison relies on it. Without TALYS those tests skip, the reload can land inside an
    HF_NATIVE/HF_NATIVEX=0 arm, and every nx2 test after it finds the kernels off. Loading it
    before each test (switches as the environment has them) keeps the suite order-independent."""
    import sys

    nx2 = sys.modules.get("physics.hf.native.nx2")
    if nx2 is not None and nx2.lib.cache_info().currsize == 0:
        nx2.lib()


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_setup(item: pytest.Item) -> None:
    _prime_nx2()
    for m in item.iter_markers("needs_data"):
        need_data(*m.args)
    for m in item.iter_markers("needs_main"):
        need_main(*m.args)


def _talys_missing(excinfo) -> bool:
    return (excinfo is not None and excinfo.errisinstance(FileNotFoundError)
            and TALYS_MISSING in str(excinfo.value))


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo):
    outcome = yield
    rep = outcome.get_result()
    if rep.failed and _talys_missing(call.excinfo):
        rep.outcome = "skipped"
        rep.longrepr = (str(item.path), item.location[1] or 0, f"Skipped: {_TALYS_SKIP}")

