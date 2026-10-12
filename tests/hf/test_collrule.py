"""COLLRULE: keyword `collrule` (env alias INCOGNITA_COLLRULE) = target coupling scheme from measured structure. Default n = TALYS."""

import pytest

from physics.hf.input.defaults import default_options
from physics.hf.omp import parameters as P
from physics.hf.structure import collrule as CR


@pytest.fixture(autouse=True)
def _no_env(monkeypatch):
    monkeypatch.delenv(CR.ENV, raising=False)
    monkeypatch.delenv("INCOGNITA_TALYS_FIT", raising=False)


def _dfm(Z, A, **ov):
    from physics.hf.structure.deformation import deformation
    from physics.hf.structure.levels import discrete_levels
    from physics.hf.structure.masses import masses as get_masses

    o = default_options(Z, A, overrides=ov)
    m = get_masses(o)
    return o, deformation(Z, A, o, discrete_levels(Z, A, o, m), m)


def test_default_off():
    o = default_options(25, 55)
    assert o.collrule == "n" and CR.mode(o) == "" and CR.target_letter(25, 55, o) is None


def test_keyword_env_and_bad_value(monkeypatch):
    assert CR.mode(default_options(25, 55, overrides={"collrule": "y"})) == "strict"
    monkeypatch.setenv(CR.ENV, "trans")
    assert CR.mode(default_options(25, 55)) == "trans"
    with pytest.raises(ValueError):
        CR.mode(default_options(25, 55, overrides={"collrule": "rotor"}))


def test_schemes():
    o, d = _dfm(25, 55)
    assert d.colltype == "R" and P._colltype(25, 55, o) == "R"
    o, d = _dfm(25, 55, collrule="strict")  # Mn-55: vibrator core (R4/2 2.32) -> S
    assert d.colltype == "S" and P._colltype(25, 55, o) == "S"
    o, d = _dfm(30, 68, collrule="strict")  # Zn-68: vibrator (2.24) -> V, measured beta2 on the 2+_1
    assert d.colltype == "V" and P._colltype(30, 68, o) == "V" and d.defpar[1] == pytest.approx(0.2025, abs=1e-3)
    o, d = _dfm(41, 103, collrule="strict")  # Nb-103: rotor core + ENSDF g.s. band -> R (autorot band)
    assert d.colltype == "R" and P._colltype(41, 103, o) == "R"
    o, d = _dfm(60, 148, collrule="strict")  # transitional: letter kept
    assert d.colltype == "R"
    o, d = _dfm(60, 148, collrule="trans")
    assert d.colltype == "V"


def test_not_target_untouched():
    from physics.hf.structure.deformation import deformation
    from physics.hf.structure.levels import discrete_levels
    from physics.hf.structure.masses import masses as get_masses

    o = default_options(25, 56, overrides={"collrule": "strict"})  # Mn-55 is a residual here, not the target
    m = get_masses(o)
    assert deformation(25, 55, o, discrete_levels(25, 55, o, m), m).colltype == "R"
    assert P._colltype(25, 55, o) == "R"


def test_autorot_ported():
    o, d = _dfm(71, 176, autorot="y")  # Lu-176: no block, A > 150, >= 8 from magic -> autorot rotor
    assert d.colltype == "R" and P._colltype(71, 176, o) == "R"


def test_sv_component():
    o, d = _dfm(30, 68, collrule="sv")  # S -> V: switched
    assert d.colltype == "V" and P._colltype(30, 68, o) == "V"
    o, d = _dfm(25, 55, collrule="sv")  # R -> S under strict: NOT part of the sv component
    assert d.colltype == "R" and P._colltype(25, 55, o) == "R"
    o, d = _dfm(41, 103, collrule="sv")  # S -> R under strict: not part of it either
    assert d.colltype == "S"
    o, d = _dfm(78, 194, collrule="sv")  # transitional S -> V exists only in trans
    assert d.colltype == "S"
