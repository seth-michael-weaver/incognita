"""RIGIDSPIN (ISORATIO): default OFF; R = Irigid(0) T / sigma^2_eng at S; applying the lines makes the ON cascade rigid (R -> 1)."""
import os

import pytest


@pytest.fixture(autouse=True)
def _drop_cards_after():
    """test_lines_make_box_rigid activates fitted cards; drop them so later tests see the environment they set."""
    yield
    from physics.hf import chartrun
    from physics.hf.input import fitlib
    fitlib.deactivate(); fitlib._cards.cache_clear(); chartrun.drop_target_caches()


def test_mode_default_off(monkeypatch):
    from physics.hf.density import rigidspin

    monkeypatch.delenv(rigidspin.ENV, raising=False)
    assert rigidspin.mode() == "n"
    monkeypatch.setenv(rigidspin.ENV, "y")
    assert rigidspin.mode() == "y"


@pytest.mark.slow
def test_lines_make_box_rigid(monkeypatch):
    from physics.hf import chartrun, warmrun
    from physics.hf.density import rigidspin
    from physics.hf.input import fitlib

    for k in [k for k in os.environ if k.startswith("INCOGNITA_")]:
        monkeypatch.delenv(k, raising=False)
    monkeypatch.setenv("INCOGNITA_TALYS_FIT", "nodata")   # the runners' recipe; it enables the lines arm
    fitlib.deactivate(); fitlib._cards.cache_clear(); chartrun.drop_target_caches()
    cas = warmrun.new_cascade(40, 90, (14.0,))
    lines, recs = rigidspin.chain_lines(cas)
    zr90 = [r for r in recs if (r.get("Z"), r.get("A")) == (40, 90)][0]
    # ldmodel 1: R = (1 + |beta2|/3) * alimit / a(S) exactly (scutconst = Irigid0/alimit, sigma^2 = scutconst sqrt(aU))
    assert zr90["ldmodel"] == 1 and 1.0 < zr90["R"] < 1.4
    assert len(lines) == len([r for r in recs if "R" in r and r["R"] != 1.0])
    monkeypatch.setenv("INCOGNITA_TALYS_FIT_LINES", ";".join(lines))
    fitlib.deactivate(); fitlib._cards.cache_clear(); chartrun.drop_target_caches()
    cas2 = warmrun.new_cascade(40, 90, (14.0,))
    _, after = rigidspin.chain_lines(cas2)
    for r in after:
        if "R" in r:
            assert abs(r["R"] - 1.0) < 0.02, r
