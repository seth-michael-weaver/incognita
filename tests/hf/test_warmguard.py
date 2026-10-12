"""SPEEDFIX (warmrun trap): a Cascade is refused when the fitlib cards changed since it was built.

SPEEDPROF found that a kept Cascade + `warmrun.drop_parameter_caches` after a lines change returned
capture frozen at the first sweep point (up to 5.4x off). The engine now refuses that run.
"""
import os

import pytest


def _clean(monkeypatch):
    from physics.hf import chartrun
    from physics.hf.input import fitlib

    for k in [k for k in os.environ if k.startswith("INCOGNITA_")]:
        monkeypatch.delenv(k, raising=False)
    monkeypatch.setenv("INCOGNITA_TALYS_FIT", "nodata")
    fitlib.deactivate(); fitlib._cards.cache_clear(); chartrun.drop_target_caches()


def test_same_cards_pass_changed_cards_refused(monkeypatch):
    from physics.hf import warmrun
    from physics.hf.input import fitlib

    _clean(monkeypatch)
    monkeypatch.setenv("INCOGNITA_TALYS_FIT_LINES", "ctable 20 41 0.10000")
    cas = warmrun.new_cascade(20, 40, (1.0,))
    cas.check_cards()                              # unchanged: allowed
    warmrun.drop_parameter_caches(cas)            # the no-change cold/warm check stays allowed
    monkeypatch.setenv("INCOGNITA_TALYS_FIT_LINES", "ctable 20 41 0.20000")
    with pytest.raises(RuntimeError, match="changed fitlib cards"):
        cas.check_cards()
    with pytest.raises(RuntimeError, match="changed fitlib cards"):
        warmrun.drop_parameter_caches(cas)
    # SPEEDPROF's "warm" sweep: deactivate (drops target caches) + drop_parameter_caches
    fitlib.deactivate()
    with pytest.raises(RuntimeError):
        warmrun.drop_parameter_caches(cas)
    # SPEEDPROF's "warm2" sweep: new cards forced active without deactivate
    fitlib._ACTIVE = fitlib.cards(20, 40)
    with pytest.raises(RuntimeError):
        cas.check_cards()
    # a fresh Cascade under the new cards is fine
    cas2 = warmrun.new_cascade(20, 40, (1.0,))
    cas2.check_cards()


def test_activate_replaces_stale_cards(monkeypatch):
    """A lines change WITHOUT deactivate used to keep the old cards for the same target."""
    from physics.hf.input import fitlib

    _clean(monkeypatch)
    monkeypatch.setenv("INCOGNITA_TALYS_FIT_LINES", "ctable 20 41 0.10000")
    c1 = fitlib.activate(20, 40)
    monkeypatch.setenv("INCOGNITA_TALYS_FIT_LINES", "ctable 20 41 0.20000")
    c2 = fitlib.activate(20, 40)
    assert c1 != c2 and fitlib.active() is c2
    assert any(abs(v - 0.2) < 1e-12 for k, _z, _a, v, _i in c2.cells if k == "ctable")


def test_lever_off_never_refuses(monkeypatch):
    from physics.hf import chartrun, warmrun
    from physics.hf.input import fitlib

    for k in [k for k in os.environ if k.startswith("INCOGNITA_")]:
        monkeypatch.delenv(k, raising=False)
    fitlib.deactivate(); chartrun.drop_target_caches()
    cas = warmrun.new_cascade(20, 40, (1.0,))
    warmrun.drop_parameter_caches(cas)
    cas.check_cards()
