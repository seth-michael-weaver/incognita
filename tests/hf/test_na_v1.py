"""INCOGNITA_NA_V1: the v1 (n,a) recipe (emission alpha OMP + parity-dependent alpha pickup)."""
import pytest

from physics.hf.input import fitlib


@pytest.fixture(autouse=True)
def _clean_env(monkeypatch):
    for k in (fitlib.ENV, fitlib.ENV_LINES, fitlib.ENV_MF1, fitlib.ENV_NA_V1):
        monkeypatch.delenv(k, raising=False)
    fitlib.deactivate()
    yield
    fitlib.deactivate()


def test_off_by_default():
    assert fitlib.modes() == frozenset()
    assert not fitlib.enabled()


def test_lines_follow_target_parity():
    assert fitlib.na_v1_lines(82, 208) == ("alphaomp 8", "cstrip a 1.85")   # even-even
    assert fitlib.na_v1_lines(83, 209) == ("alphaomp 8", "cstrip a 0.52")   # odd Z
    assert fitlib.na_v1_lines(82, 207) == ("alphaomp 8", "cstrip a 0.52")   # odd N


def test_env_switch_applies_the_recipe(monkeypatch):
    monkeypatch.setenv(fitlib.ENV_NA_V1, "1")
    assert "nav1" in fitlib.modes()
    c = fitlib.cards(82, 208, "n", 0, fitlib.modes())
    assert ("alphaomp", 8) in [(k, int(v)) for k, v in c.options]
    assert [tuple(p) for p in c.particles] == [("cstrip", 6, 1.85)]


def test_explicit_line_still_wins(monkeypatch):
    monkeypatch.setenv(fitlib.ENV_NA_V1, "1")
    monkeypatch.setenv(fitlib.ENV_LINES, "cstrip a 1.0")
    c = fitlib.cards(82, 208, "n", 0, fitlib.modes())
    assert [tuple(p) for p in c.particles][-1] == ("cstrip", 6, 1.0)
