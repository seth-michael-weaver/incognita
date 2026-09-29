"""BESTFIT: `physics.hf.input.fitlib` reads TALYS's best tree the way xsfit.f90 does.

The engine-level gates (engine vs stock TALYS with the same keywords, the four paths, the TENDL
file comparison) are in `docs/results/bestfit.md`; these are the unit facts behind them.
"""
from __future__ import annotations

import pytest

from physics.hf.input import fitlib

pytestmark = pytest.mark.skipif(not fitlib.structure_best().is_dir(),
                                reason="TALYS structure/best not installed")
ARMS = frozenset({"best", "s8"})  # = INCOGNITA_TALYS_FIT=tendl


def test_modes_parses_the_env(monkeypatch):
    monkeypatch.delenv(fitlib.ENV, raising=False)
    assert fitlib.modes() == frozenset() and not fitlib.enabled()
    monkeypatch.setenv(fitlib.ENV, "off")
    assert fitlib.modes() == frozenset()
    monkeypatch.setenv(fitlib.ENV, "tendl")
    assert fitlib.modes() == frozenset({"best", "s8"}) and fitlib.enabled()
    monkeypatch.setenv(fitlib.ENV, "nodata")
    assert fitlib.modes() == frozenset({"nodata", "s8"})
    monkeypatch.setenv(fitlib.ENV, "bogus")
    with pytest.raises(ValueError):
        fitlib.modes()


def test_best_file_lines():
    assert fitlib.best_lines(79, 197) == ("ldmodel 7", "fit y")
    assert "ldmodelcn 1" in fitlib.best_lines(26, 56)
    assert fitlib.best_lines(69, 171) == ()  # no best file: TENDL never fitted Tm-171


def test_par_entry_is_keyed_on_ldmodel_and_strength():
    """xsfit.f90:145-152. Fe-56's best file says `ldmodel 2` and `ldmodelCN 1`, and TENDL's own
    MF1 block carries the ldmodel-1 strength-8 value, 0.81361."""
    ld1 = fitlib.par_lines("ng", 26, 56, ldmodel=1, flagcol=False, strength=8)
    assert [l.split()[3] for l in ld1 if l.startswith("wtable")] == ["0.81361"]
    ld2 = fitlib.par_lines("ng", 26, 56, ldmodel=2, flagcol=False, strength=8)
    assert [l.split()[3] for l in ld2 if l.startswith("wtable")] == ["0.80043"]
    s9 = fitlib.par_lines("ng", 26, 56, ldmodel=1, flagcol=False, strength=9)
    assert s9 and s9 != ld1
    assert fitlib.par_lines("ng", 26, 56, ldmodel=1, flagcol=False, strength=8, Ltarget=1) == ()


def test_cards_reproduce_the_adjust_dat_of_stock_talys():
    """`fit y` reads every (n,x) fitted library, not only ng.par: this is exactly what stock
    TALYS-2.2 writes to adjust.dat for n + Au-197 with `best y` and `strength 8`."""
    c = fitlib.cards(79, 197, arms=ARMS)
    assert dict(c.options) == {"strength": 8, "ldmodel": "7", "fit": "y"}
    assert ("wtable", 79, 198, 0.86175, (1, 1)) in c.cells
    assert ("gadjust", 79, 198, 1.08794, ()) in c.cells
    assert ("s2adjust", 79, 198, 1.11126, (0,)) in c.cells
    assert ("rvadjust", 2, 1.00319) in c.particles
    assert sum(1 for k, *_ in c.cells if k == "wtable") == 1


def test_ngfit_alone_does_not_pull_the_other_libraries():
    """input_fit.f90:53-63: the sub-flag defaults are read before the keyword loop, so `ngfit y`
    on its own leaves flagnnfit/flagnafit off."""
    c = fitlib.cards(26, 56, arms=ARMS)          # Fe-56's best file says `ngfit y`, not `fit y`
    fits = [s for s in c.source if s.endswith("]")]
    assert len(fits) == 1 and fits[0].startswith("ng.par[ldmodel 1 colenhance n strength 8]")
    assert ("wtable", 26, 57, 0.81361, (1, 1)) in c.cells
    au = fitlib.cards(79, 197, arms=ARMS)        # Au-197's says `fit y`: every library is read
    assert sorted(s.split("[")[0] for s in au.source if s.endswith("]")) == [
        "na.par", "ng.par", "nn.par"]


def test_lever_off_changes_nothing(monkeypatch):
    from physics.hf.input.defaults import default_options, default_params

    monkeypatch.delenv(fitlib.ENV, raising=False)
    fitlib.deactivate()
    o = default_options(79, 197)
    p = default_params(79, 197, o)
    assert o.strength == 9 and o.ldmodelall == 1
    assert float(p.values["wtable"][0, 0, 1, 1]) == pytest.approx(1.081)  # globalwtable, ld 1
    assert fitlib.apply_params(79, 197, o, p) is p


def test_cards_reach_options_and_params(monkeypatch):
    from physics.hf.input.defaults import default_options, default_params

    monkeypatch.setenv(fitlib.ENV, "tendl")
    try:
        fitlib.activate(79, 197)
        o = default_options(79, 197)
        assert (o.strength, o.ldmodelall, o.ldmodelCN, o.flagngfit, o.flagnnfit) == (
            8, 7, 7, True, True)
        p = default_params(79, 197, o)
        assert float(p.values["s2adjust"][0, 0, 0]) == pytest.approx(1.11126)
        assert float(p.values["gadjust"][0, 0]) == pytest.approx(1.08794)
        assert float(p.values["rvadjust"][2]) == pytest.approx(1.00319)
        # E1 wtable is owned by gamma_parameters, so it travels as a gamma override
        gov = fitlib.gamma_overrides(79, 198, 2)
        assert gov["wtable"][1, 1] == pytest.approx(0.86175)
        assert fitlib.gamma_overrides(79, 197, 2) is None
    finally:
        fitlib.deactivate()
        monkeypatch.delenv(fitlib.ENV, raising=False)
