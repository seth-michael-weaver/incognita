"""RESISO: residual isomer files from the cascade's surviving populations (residual.f90:67)."""

from physics.hf.emission import multiple as M
from physics.hf.engine import resiso_keys


def test_off_writes_nothing(monkeypatch):
    monkeypatch.delenv("INCOGNITA_RESISO", raising=False)
    assert resiso_keys({(82, 199): 798.0}, {(82, 199): {0: 0.2, 1: 0.8}}) == {}


def test_isomer_files_levnum_and_unreached(monkeypatch):
    monkeypatch.setenv("INCOGNITA_RESISO", "1")
    monkeypatch.setitem(M.LEVNUM, (79, 196), {3: 3, 30: 54})  # a continuum isomer moved into slot 30 keeps file number 54
    out = resiso_keys({(79, 196): 100.0}, {(79, 196): {0: 0.25, 3: 0.75}})  # slot 30 not reached by the cascade
    assert out == {"rp079196.L00": 25.0, "rp079196.L03": 75.0, "rp079196.L54": 0.0}


def test_no_isomer_no_files(monkeypatch):
    monkeypatch.setenv("INCOGNITA_RESISO", "1")
    monkeypatch.setitem(M.LEVNUM, (26, 56), {})
    assert resiso_keys({(26, 56): 10.0}, {(26, 56): {0: 1.0}}) == {}


def test_isomer_from_level_scheme_when_cascade_stops_short(monkeypatch):
    monkeypatch.setenv("INCOGNITA_RESISO", "1")
    monkeypatch.setitem(M.LEVNUM, (82, 202), {14: 14})  # Pb-202m above this energy's Nlast: L00 = total, L14 = 0
    assert resiso_keys({(82, 202): 34.7}, {(82, 202): {0: 1.0}}) == {"rp082202.L00": 34.7, "rp082202.L14": 0.0}
