"""C6FIX (ENGC10): switch parsing; the end-to-end check (I-105 alpha NL >= 0, OFF bit-identical) is development notes."""
from physics.hf.preeq.exciton import c6fix_on


def test_c6fix_default_off(monkeypatch):
    monkeypatch.delenv("INCOGNITA_C6FIX", raising=False)
    assert not c6fix_on()


def test_c6fix_on_values(monkeypatch):
    for v in ("1", "y", "on", "true"):
        monkeypatch.setenv("INCOGNITA_C6FIX", v)
        assert c6fix_on()
    monkeypatch.setenv("INCOGNITA_C6FIX", "0")
    assert not c6fix_on()
