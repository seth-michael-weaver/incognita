"""KWCOV B5: compound, gamma, level and level-density keywords (docs/hf/COVERAGE_PLAN.md, batch B5).

Each keyword below used to be read and ignored, or not read at all (a deck line with it was skipped without a
word). It now acts the way TALYS-2.25 reads it, or the run refuses it. The physics response of each one was
compared with stock TALYS by scripts/kwcov/b5_response.py (|ln(R/S)| per channel and energy; the numbers are in
docs/hf/COVERAGE_PLAN.md B5); the tests here pin the parsing, the refusals and the default (nothing set = the
old objects and numbers).
"""
from __future__ import annotations

import os
import warnings

import pytest

from physics.hf.input import defaults as D
from physics.hf.input import fitlib as F


@pytest.fixture
def clean(monkeypatch):
    from physics.hf import chartrun

    for k in [k for k in os.environ if k.startswith("INCOGNITA_")]:
        monkeypatch.delenv(k, raising=False)
    F.deactivate(); F._cards.cache_clear(); chartrun.drop_target_caches()
    yield monkeypatch
    for k in [k for k in os.environ if k.startswith("INCOGNITA_")]:
        monkeypatch.delenv(k, raising=False)
    F.deactivate(); F._cards.cache_clear(); chartrun.drop_target_caches()


def _cards(clean, lines: str):
    clean.setenv(F.ENV_LINES, lines)
    F._cards.cache_clear()
    return F.cards(26, 56)


# ------------------------------------------------------------------------------------ defaults unchanged

def test_defaults_carry_no_b5_forms():
    o = D.default_options(26, 56)
    assert o.nlow_of(0, 1) == o.nlow_default == -1 and o.ntop_of(0, 1, 1) == o.ntop_default == -1
    assert not o.skipcn_of(0, 1) and o.levelfile_of(0) is None and o.deformfile_of(0) is None
    D.reject_unported(o)


def test_no_deck_no_direct_capture(clean):
    from physics.hf.direct import racapcalc as R

    assert R.mode() == "off" and R.mode(26, 56) == "off"
    assert R._deck_key(26, 56) == ()


# ------------------------------------------------------------------------------ per-nucleus / element forms

def test_nlow_ntop_skipcn_resolve_to_zix_nix():
    # n + Fe-56: compound Fe-57 (Zinit 26, Ninit 31); Fe-56 = (0, 1)
    o = D.default_options(26, 56, overrides={"nlow 26 56 0": 3, "ntop 26 56 1": 8, "skipcn 26 56": "y",
                                             "ntop 0 1 0": 6})                 # (Zix, Nix) given directly
    assert o.nlow_of(0, 1) == 3 and o.nlow_of(0, 0) == -1
    assert o.ntop_of(0, 1, 1) == 8 and o.ntop_of(0, 1) == 6
    assert o.skipcn_of(0, 1) and not o.skipcn_of(0, 0)
    D.reject_unported(o)


def test_deck_forms_of_nlow_ntop_skipcn(clean):
    o = dict(_cards(clean, "nlow 26 56 3;ntop 26 56 8 1;skipcn 26 57").options)
    assert o == {"nlow 26 56 0": "3", "ntop 26 56 1": "8", "skipcn 26 57": "y"}
    with pytest.raises(ValueError, match="expected `skipcn Z A`"):
        _cards(clean, "skipcn 26 57 1")


def test_level_and_deformation_files_keep_their_case(clean, tmp_path):
    lev, dfm = tmp_path / "MyFe.lev", tmp_path / "MyFe.def"
    o = dict(_cards(clean, f"LEVELFILE 26 {lev};deformfile 26 {dfm}").options)
    assert o == {"levelfile 26": str(lev), "deformfile 26": str(dfm)}
    opts = D.default_options(26, 56, overrides=o)
    assert opts.levelfile_of(0) == str(lev) and opts.deformfile_of(0) == str(dfm) and opts.levelfile_of(1) is None


def test_best_file_level_files_are_not_applied():
    # Mo-95's best file says `levelfile 42 Mo.lev` (a file of its own directory): left out with a warning
    _, _, _, _, skipped = F._split(["levelfile 42 mo.lev"], want_options=True)
    assert skipped == [("levelfile 42 mo.lev", "external level file")]


def test_read_deck_resolves_a_level_file_in_the_deck_directory(tmp_path):
    from physics.hf.input.deck import read_deck

    d = read_deck("projectile n\nelement fe\nmass 56\nenergy 14\nlevelfile 26 MyFe.lev\n", cwd=tmp_path)
    assert d.lines == (f"levelfile 26 {tmp_path / 'MyFe.lev'}",)


def test_levelfile_replaces_the_structure_file(tmp_path):
    from physics.hf.gamma.parameters import structure_dir
    from physics.hf.structure.levels import discrete_levels

    src = structure_dir() / "levels" / "final" / "Fe.lev"
    if not src.is_file():
        pytest.skip("TALYS structure database not present")
    text = src.read_text()
    assert "   1   0.846778   2.0" in text
    p = tmp_path / "Fe.lev"
    p.write_text(text.replace("   1   0.846778   2.0", "   1   0.950000   2.0", 1))
    o = D.default_options(26, 56, overrides={"levelfile 26": str(p)})
    lv = discrete_levels(26, 56, o)
    assert float(lv.e_mev[1]) == pytest.approx(0.95)
    assert float(discrete_levels(26, 56, D.default_options(26, 56)).e_mev[1]) == pytest.approx(0.846778)
    o = D.default_options(26, 56, overrides={"levelfile 26": str(tmp_path / "none.lev")})
    with pytest.raises(FileNotFoundError, match="levelfile"):
        discrete_levels(26, 56, o)


# ------------------------------------------------------------------------------------- Params deck forms

def test_tjadjust_constant_is_read_and_warned_as_talys_never_applies_it(clean):
    with pytest.warns(UserWarning, match="never applies a constant `tjadjust`"):
        c = _cards(clean, "tjadjust 26 57 p 1.5")
    assert c.cells == (("tjadjust", 26, 57, 1.5, (2,)),)
    with pytest.warns(UserWarning):
        assert _cards(clean, "tjadjust 26 57 f 0.9").cells[0][4] == (-1,)    # parsym(-1) = f
    with pytest.raises(ValueError, match="energy-local adjustment"):
        _cards(clean, "tjadjust 26 57 p 1.5 4. 20. 10. 1.5")


def test_global_and_per_nucleus_forms_of_sfth_sfexp_pshiftconstant(clean):
    c = _cards(clean, "sfth 0.5;sfexp 0.4;pshiftconstant 1.5;sfexp 0.6 26 57 2;sfth 0.7 26 57")
    assert set(c.globals_) == {("sfth", 0.5), ("sfexp", 0.4), ("pshiftconstant", 1.5)}
    assert set(c.cells) == {("sfexp", 26, 57, 0.6, (2,)), ("sfth", 26, 57, 0.7, ())}
    F.activate(26, 56)
    o = D.default_options(26, 56)
    p = F.apply_params(26, 56, o, D.default_params(26, 56, o))
    assert float(p.at("sfth", 0, 0)) == pytest.approx(0.7)      # the per-nucleus line wins over sfthall (input_gammapar:487)
    assert float(p.at("sfth", 0, 1)) == pytest.approx(0.5)
    assert float(p.at("sfexp", 0, 0, 2)) == pytest.approx(0.6) and float(p.at("sfexp", 0, 0, 1)) == pytest.approx(0.4)
    assert float(p.at("pshiftconstant", 1, 1)) == pytest.approx(1.5)


@pytest.mark.parametrize("line", ["densfile 26 my.ld", "e1file 26 56 my.e1", "m1file 26 56 my.m1",
                                  "massdir mymasses", "nosuchkeyword 1"])
def test_unread_files_and_unknown_keywords_are_refused(clean, line):
    with pytest.raises(ValueError, match="not applied by the port"):
        _cards(clean, line)


def test_output_only_keywords_stay_accepted(clean):
    c = _cards(clean, "filechannels y;fileresidual y;outdiscrete y;outspectra y;blockangle y;partable y")
    assert all(why == "output-only keyword (NA)" for _, why in c.skipped)   # read as options, or accepted as NA


# ---------------------------------------------------------------------------------------------- refusals

def test_rpevap_and_optmodall_are_refused_their_dependants_are_inert():
    for ov, key in (({"rpevap": "y"}, "rpevap"),):  # KWCOV B6 ports optmodall (tests/hf/test_kwcov_b6.py)
        with pytest.raises(NotImplementedError, match=key):
            D.reject_unported(D.default_options(26, 56, overrides=ov))
    # maxZrp/maxNrp act only with rpevap y (multiple.f90:270), popmev only on a population input (projectile 0),
    # the pseudo-resonance values only with `pseudoresonances y` (refused in structure/levels.py)
    o = D.default_options(26, 56, overrides={"maxzrp": 3, "maxnrp": 4, "popmev": "y"})
    assert (o.maxZrp, o.maxNrp, o.flagpopMeV) == (3, 4, True)
    D.reject_unported(o)


def test_racap_deck_line(clean):
    from physics.hf.direct import racapcalc as R

    clean.setenv(F.ENV_LINES, "racap y")
    with pytest.warns(UserWarning, match="without optmodall y"):
        assert R.mode(26, 56) == "off"                         # stock TALYS-2.25: 0 mb without optmodall
    clean.setenv("INCOGNITA_DIRECT_CAPTURE", "all")
    clean.setenv(F.ENV_LINES, "racap n")
    assert R.mode(26, 56) == "off"                              # the deck wins over the variable
    clean.setenv(F.ENV_LINES, "sfth 0.5")
    assert R.mode(26, 56) == "all" and R._deck_key(26, 56) != ()
    clean.setenv(F.ENV_LINES, "ldmodelracap 2")
    with pytest.raises(NotImplementedError, match="ldmodelracap 2"):
        R.mode(26, 56)
    clean.delenv("INCOGNITA_DIRECT_CAPTURE")
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        assert R.mode(26, 56) == "off"                          # ldmodelracap alone: inert, as in TALYS
