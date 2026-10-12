"""KNOCKFIX (ALPHAHUMP): knockout sigav from the last computed inverse-xs bin (Incognita extension, default OFF).

TALYS's knockout.f90:124 reads `xsreac(type2, eend(type2))`, but `inverse` fills xsreac only up to eendmax(type2);
when the alpha end point lies in the emission grid's top bin interval that read is a hard 0 and the alpha
knockout jumps x15-25 over a 1 MeV window of incident energy. OFF (no keyword, no environment) must be TALYS.
"""

from __future__ import annotations

import pytest

from physics.hf.input.defaults import default_options
from physics.hf.preeq.complex import knockcb_on, knockfix2_on, knockfix_on


def test_off_by_default(monkeypatch):
    monkeypatch.delenv("INCOGNITA_KNOCKFIX", raising=False)
    o = default_options(75, 185)
    assert o.knockfix is False
    assert knockfix_on(o) is False
    for off in ("", "0", "off", "n"):
        monkeypatch.setenv("INCOGNITA_KNOCKFIX", off)
        assert knockfix_on(o) is False


@pytest.mark.parametrize("val", ["1", "y", "yes", "on"])
def test_on_from_environment(monkeypatch, val):
    monkeypatch.setenv("INCOGNITA_KNOCKFIX", val)
    assert knockfix_on(default_options(75, 185)) is True


def test_on_from_keyword(monkeypatch):
    monkeypatch.delenv("INCOGNITA_KNOCKFIX", raising=False)
    assert knockfix_on(default_options(75, 185, overrides={"knockfix": True})) is True


def test_knockcb_off_by_default_and_separate(monkeypatch):
    monkeypatch.delenv("INCOGNITA_KNOCKCB", raising=False)
    monkeypatch.delenv("INCOGNITA_KNOCKFIX", raising=False)
    o = default_options(75, 185)
    assert knockcb_on(o) is False
    assert knockcb_on(default_options(75, 185, overrides={"knockcb": True})) is True
    assert knockfix_on(default_options(75, 185, overrides={"knockcb": True})) is False


def test_knockfix2_off_by_default(monkeypatch):
    monkeypatch.delenv("INCOGNITA_KNOCKFIX2", raising=False)
    assert knockfix2_on(default_options(78, 183)) is False
    assert knockfix2_on(default_options(78, 183, overrides={"knockfix2": True})) is True
