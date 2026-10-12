"""OMPROTOR `omprotor` keyword (env INCOGNITA_OMPROTOR): rotor CC diffuseness un-fold; default n = OFF (no cards, bit-identical).

The expected cards are the extra lines OMPROTOR's registered runs carried (the development notes,
built by development notes). The engine-run equality against those runs is development notes
"""

from __future__ import annotations

import pytest

from physics.hf.input import fitlib
from physics.hf.input.defaults import default_options
from physics.hf.omp import omprotor as R

UNF1 = {(60, 148): ("avadjust n 0.94089", "awdadjust n 0.89899", "avdadjust n 0.89899"),
        (68, 162): ("avadjust n 0.85986", "awdadjust n 0.75263", "avdadjust n 0.75263"),
        (79, 197): ("avadjust n 0.96895", "awdadjust n 0.94835", "avdadjust n 0.94835")}


def test_default_is_off(monkeypatch):
    monkeypatch.delenv(R.ENV_OMPROTOR, raising=False)
    o = default_options(68, 162)
    assert o.omprotor == "n" and R.mode(o) == "n" and R.lines(68, 162, "n") == ()


@pytest.mark.parametrize("za", sorted(UNF1))
def test_cards_equal_omprotor_runs(za):
    assert R.lines(*za, "unf1") == UNF1[za]
    assert R.lines(*za, "unfv") == UNF1[za][:1]


def test_non_members_get_nothing():
    for za in ((26, 56), (82, 208), (92, 238), (50, 120)):   # spherical / vibrational / actinide (RIPL 2408)
        assert R.lines(*za, "unf1") == ()


def test_env_equals_keyword(monkeypatch):
    monkeypatch.delenv(R.ENV_OMPROTOR, raising=False)
    kw = R.mode(default_options(68, 162, overrides={"omprotor": "unf1"}))
    monkeypatch.setenv(R.ENV_OMPROTOR, "unf1")
    assert R.mode(default_options(68, 162)) == kw == "unf1"
    with pytest.raises(ValueError):
        R.mode(default_options(68, 162, overrides={"omprotor": "bogus"}))


def test_cards_route(monkeypatch, tmp_path):
    """through fitlib: the keyword line puts the three neutron particle cards on a member run, after the run's own lines."""
    monkeypatch.delenv(R.ENV_OMPROTOR, raising=False)
    lf = tmp_path / "x.lines"
    lf.write_text("avadjust n 0.5\n")
    monkeypatch.setenv(fitlib.ENV, "nodata")
    monkeypatch.setenv(fitlib.ENV_LINES_FILE, str(lf))
    monkeypatch.setenv(fitlib.ENV_LINES, "omprotor unf1")
    c = fitlib.cards(68, 162)
    assert [p for p in c.particles if p[1] == 1][-3:] == [("avadjust", 1, 0.85986), ("awdadjust", 1, 0.75263),
                                                          ("avdadjust", 1, 0.75263)]
    monkeypatch.setenv(fitlib.ENV_LINES, "")
    assert fitlib.cards(68, 162).particles == (("avadjust", 1, 0.5),)
