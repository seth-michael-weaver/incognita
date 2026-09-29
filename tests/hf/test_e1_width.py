"""The shipped E1-width constant (REDTEAM B4): the public engine applies INCOGNITA's 1.0425, not TALYS's table
(1.076 / 1.081, the mean of TENDL's fits), to the no-data recipe."""
from physics.hf.gamma import e1_width as w


def test_shipped_constant():
    assert w.INCOGNITA_E1 == 1.0425


def test_resolve_defaults():
    assert w.resolve("nodata") == "1.0425"
    assert w.resolve("nodata+s8") == "1.0425"
    assert w.resolve("lines") == ""          # other arms keep TALYS's table unless asked
    assert w.resolve("") == ""
    assert w.resolve("nodata", "stock") == ""
    assert w.resolve("lines", "incognita") == "1.0425"
    assert w.resolve("", "1.02") == "1.02"


def test_override_replaces_table(monkeypatch):
    monkeypatch.delenv(w.ENV, raising=False)
    assert w.constant(8, 1.076) == 1.076
    monkeypatch.setenv(w.ENV, "1.0425")
    assert w.constant(8, 1.076) == 1.0425 and w.constant(9, 1.081) == 1.0425
    monkeypatch.setenv(w.ENV, "8=1.02")
    assert w.constant(8, 1.076) == 1.02 and w.constant(9, 1.081) == 1.081
