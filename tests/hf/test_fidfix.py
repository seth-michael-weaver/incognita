"""FIDELITY1 opt-in fixes (physics/hf/fidfix.py; docs/hf/FIDELITY_DEFAULTS.md): OFF changes nothing, ON restores TALYS.

The end-to-end numbers (stock TALYS-2.25 vs engine, Fe-56 `best y` and `ldmodel 2; ldmodelCN 1`) come from
scripts/kwcov/fidelity.py and are recorded in the doc; these tests pin the mechanism without running a reaction.
"""
from __future__ import annotations

import os
from pathlib import Path
from types import SimpleNamespace

import pytest

from physics.hf import fidfix
from physics.hf.input import defaults as D
from physics.hf.input import fitlib

TALYS_DIR = Path(os.environ.get("TALYS_DIR", Path.home() / "opt/talys-src"))


_FE56 = SimpleNamespace(Z=26, A=56, projectile="n")  # the run's target, as the cards fitlib.activate would hold


@pytest.fixture
def run_target(monkeypatch):
    """`ldmodel_of` reads the active run at call time; options are built with no active cards (see `_opts`)."""
    monkeypatch.setattr(fitlib, "_ACTIVE", None)
    return monkeypatch


def test_switch_parsing(monkeypatch):
    monkeypatch.delenv(fidfix.ENV, raising=False)
    assert not any(fidfix.on(f) for f in fidfix.FIXES)
    for v, want in (("0", set()), ("n", set()), ("all", set(fidfix.FIXES)), ("y", set(fidfix.FIXES)),
                    ("ldcn", {"ldcn"}), ("besttables, ldcn", {"ldcn", "besttables"})):
        monkeypatch.setenv(fidfix.ENV, v)
        assert {f for f in fidfix.FIXES if fidfix.on(f)} == want, v


class _Ld:
    """An options set built with no active cards, whose `ldmodel_of` is then asked with Fe-56 as the active run."""

    def __init__(self, Z, A, overrides=None):
        saved = fitlib._ACTIVE
        fitlib._ACTIVE = None
        try:
            self.o = D.default_options(Z, A, overrides=overrides or {"ldmodel": 2, "ldmodelcn": 1})
        finally:
            fitlib._ACTIVE = saved

    def ldmodel_of(self, zix, nix, active=_FE56):
        saved = fitlib._ACTIVE
        fitlib._ACTIVE = active
        try:
            return self.o.ldmodel_of(zix, nix)
        finally:
            fitlib._ACTIVE = saved


def _opts(Z, A):
    # `ldmodel 2` + `ldmodelCN 1`: structure/best/Fe056/n-Fe056.talys
    return _Ld(Z, A)


def test_ldcn_off_is_the_old_rule(monkeypatch, run_target):
    monkeypatch.delenv(fidfix.ENV, raising=False)
    # the run's own options and a pseudo-target's (Fe-55 + n: the chained compound nucleus Fe-56) both give (0, 0) = 1
    assert _opts(26, 56).ldmodel_of(0, 0) == 1
    assert _opts(26, 55).ldmodel_of(0, 0) == 1
    assert _opts(26, 55).ldmodel_of(0, 1) == 2


def test_ldcn_on_only_the_run_compound_takes_ldmodelcn(monkeypatch, run_target):
    monkeypatch.setenv(fidfix.ENV, "ldcn")
    assert _opts(26, 56).ldmodel_of(0, 0) == 1  # Fe-57, the run's initial compound nucleus (input_densitymodel.f90:246)
    assert _opts(26, 55).ldmodel_of(0, 0) == 2  # Fe-56 as a chain compound nucleus: ldmodelall, as in the TALYS run
    assert _opts(25, 55).ldmodel_of(0, 0) == 2  # Mn-56 likewise
    assert _opts(26, 56).ldmodel_of(1, 1) == 2


def test_ldcn_on_keeps_a_per_nucleus_card(monkeypatch, run_target):
    monkeypatch.setenv(fidfix.ENV, "ldcn")
    o = _Ld(26, 55, {"ldmodel": 2, "ldmodelcn": 1, "ldmodel 26 56": 3})
    assert o.ldmodel_of(0, 0) == 3  # TALYS: ldmodel(Zix, Nix) of Fe-56 = its own card


def test_ldcn_on_without_ldmodelcn_or_cards_is_inert(monkeypatch):
    monkeypatch.setenv(fidfix.ENV, "ldcn")
    assert _opts(26, 55).ldmodel_of(0, 0, active=None) == 1  # no active run: nothing to compare with, old rule
    assert _Ld(26, 55, {"ldmodel": 2}).ldmodel_of(0, 0) == 2  # ldmodelCN not given: equal to ldmodelall either way  # ldmodelCN not given: equal to ldmodelall either way


@pytest.mark.skipif(not (TALYS_DIR / "structure/best/Fe056/tables").is_dir(), reason="TALYS best files not installed")
def test_besttables_reads_the_best_dirs_own_table(monkeypatch, tmp_path):
    """Fe-56 `best y`: `awdadjust n 1. awdadjust-n.table`; OFF reads misc/tables (D(5 MeV) = 0.80), ON tables/ (0.81)."""
    monkeypatch.chdir(tmp_path)  # nothing in the working directory
    monkeypatch.setenv("INCOGNITA_TALYS_FIT_LINES", "best y")
    for fix, want in (("0", 0.80), ("besttables", 0.81)):
        monkeypatch.setenv(fidfix.ENV, fix)
        c = fitlib.cards(26, 56, "n", 0)
        tabs = [b for b in c.omp.bumps if b.key == "awdadjust" and b.kind == "tab"]
        assert len(tabs) == 1, (fix, c.omp)
        es, ds = tabs[0].args
        assert ds[list(es).index(5.0)] == pytest.approx(want, abs=1e-6), fix


@pytest.mark.skipif(not (TALYS_DIR / "structure/best/fits/ng.par").is_file(), reason="TALYS fit files not installed")
def test_fitrisomer_drops_the_fitted_risomer_of_the_initial_compound(monkeypatch, tmp_path):
    """Co-59 `ngfit y`: ng.par carries `risomer 27 60 ...` (Co-60 = the initial compound nucleus)."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("INCOGNITA_TALYS_FIT_LINES", "ngfit y")
    have = {}
    for fix in ("0", "fitrisomer"):
        monkeypatch.setenv(fidfix.ENV, fix)
        c = fitlib.cards(27, 59, "n", 0)
        have[fix] = {(k, z, a) for k, z, a, *_ in c.cells}
    assert ("risomer", 27, 60) in have["0"]
    assert ("risomer", 27, 60) not in have["fitrisomer"]
    assert have["0"] - {("risomer", 27, 60)} == have["fitrisomer"]  # wtable, s2adjust stay


def test_fitrisomer_keeps_a_deck_risomer(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("INCOGNITA_TALYS_FIT_LINES", "risomer 27 60 2.0")
    monkeypatch.setenv(fidfix.ENV, "fitrisomer")
    c = fitlib.cards(27, 59, "n", 0)
    assert ("risomer", 27, 60) in {(k, z, a) for k, z, a, *_ in c.cells}
