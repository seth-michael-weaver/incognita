"""E1PROMO: ALPHAENTR is "6" (ALPHAREOPEN E1) by default (was hw:0.77, HWA770PROMO); deck keyword `alphaentr` > env INCOGNITA_ALPHAENTR > default."""
import pytest

from physics.hf import alphaentr
from physics.hf.input.defaults import default_options


def test_default_e1(monkeypatch):
    monkeypatch.delenv("INCOGNITA_ALPHAENTR", raising=False)
    assert alphaentr.mode() == "6" and alphaentr.active(6) and not alphaentr.active(1)


@pytest.mark.parametrize("v", ["", "0", "off", "n"])
def test_env_off(monkeypatch, v):
    monkeypatch.setenv("INCOGNITA_ALPHAENTR", v)
    assert alphaentr.mode() is None and not alphaentr.active(6)


def test_deck_keyword_beats_env(monkeypatch):
    monkeypatch.setenv("INCOGNITA_ALPHAENTR", "hw:0.5")
    assert not alphaentr.active(6, default_options(50, 117, "a", {"alphaentr": "0"}))
    o = default_options(50, 117, "a", {"alphaentr": "hw:0.77"})
    assert alphaentr.mode(o) == "hw:0.77" and alphaentr.mode() == "hw:0.5" and alphaentr.mode(default_options(50, 117, "a")) == "hw:0.5"
