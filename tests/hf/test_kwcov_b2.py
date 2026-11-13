"""KWCOV B2: deck lines for what the engine already has (docs/hf/COVERAGE_PLAN.md, batch B2).

Each keyword below used to be accepted and ignored (or not read at all). It now acts the way TALYS-2.25 reads
it, or the run refuses it. The physics response of each one was compared with stock TALYS by
scripts/kwcov/b2_response.py (|ln(R/S)| per channel and energy; the numbers are in docs/hf/COVERAGE_PLAN.md
B2); the tests here pin the parsing, the precedence rules and the default (nothing set = bit-identical).
"""
from __future__ import annotations

import os
import subprocess
import sys

import pytest

from physics.hf.input import defaults as D
from physics.hf.input import fitlib as F
from physics.hf.input.energies import estop_subset, incident_grid, read_energies
from tests._data import need_talys


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


# ------------------------------------------------------------------------------------ defaults unchanged

def test_defaults_carry_no_deck_forms():
    o = D.default_options(26, 56)
    assert o.pernuc == () and o.parinclude == (True,) * 7
    assert o.ldmodel_of(0, 0) == o.ldmodelCN == 1 and o.ldmodel_of(1, 1) == o.ldmodelall
    assert o.flagcol_of(2, 3) == o.flagcolall and o.nlev_of(2, 3) == o.nlevmaxres == 30
    assert o.branches_of(0, 1) == ()
    u = D.default_options(92, 238)
    assert u.ldmodel_of(0, 0) == 7 and u.flagcol_of(0, 0) is True
    D.reject_unported(o)


def test_no_lines_no_arm(clean):
    assert F.modes() == frozenset() and F.current(26, 56) is None


# ------------------------------------------------------------------------------ per-nucleus / particle forms

def test_per_nucleus_forms_resolve_to_zix_nix():
    # n + Fe-56: compound Fe-57 (Zinit 26, Ninit 31)
    o = D.default_options(26, 56, overrides={"ldmodel 26 57": 2, "colenhance 25 56": "y", "nlevels 25 56": 5,
                                             "maxlevelsbin p": 7})
    assert o.ldmodel_of(0, 0) == 2 and o.ldmodel_of(0, 1) == 1          # card on the CN only
    assert o.flagcol_of(1, 0) is True and o.flagcol_of(0, 0) is False
    assert o.nlev_of(1, 0) == 5 and o.nlev_of(0, 1) == o.nlevmax       # the target keeps nlevmax (nuclides.f90:169)
    assert o.nlevbin[2] == 7
    D.reject_unported(o)


def test_ldmodelcn_beats_a_card_on_the_compound():
    o = D.default_options(26, 56, overrides={"ldmodelcn": 3, "ldmodel 26 57": 2})
    assert o.ldmodel_of(0, 0) == 3                     # input_densitymodel.f90:245-247


def test_out_of_box_card_is_ignored_with_talys_warning():
    with pytest.warns(UserWarning, match="out of range"):
        o = D.default_options(26, 56, overrides={"ldmodel 10 20": 2})
    assert o.pernuc == ()


def test_maxlevelstar_after_maxlevelsbin_wins_for_the_projectile():
    o = D.default_options(26, 56, overrides={"maxlevelsbin n": 7, "maxlevelstar": 12})
    assert o.nlevbin[1] == 12
    o = D.default_options(26, 56, overrides={"maxlevelstar": 12, "maxlevelsbin n": 7})
    assert o.nlevbin[1] == 7


def test_bestbranch_reads_the_branch_file_and_input_lines_win():
    need_talys()  # needs the TALYS structure database; without it the best-file reads come back empty
    o = D.default_options(27, 59, overrides={"bestbranch": "y"})
    got = dict(o.branches_of(0, 2))                         # Co-58 = (Zix 0, Nix 2) of n + Co-59
    assert set(got) == {2, 12, 17, 20} and dict(got[2]) == pytest.approx({1: 0.7, 0: 0.3})
    D.reject_unported(o)


def test_branch_lines_are_dropped_as_talys_drops_them():
    """TALYS-2.25 wipes `branch` input (strucinitial.f90:325); stock Co-59 `branch 27 58 2 1 0 1.0` changes
    nothing. The port does the same, with a warning; a malformed line is still an error."""
    need_talys()  # needs the TALYS structure database; without it the best-file reads come back empty
    with pytest.warns(UserWarning, match="drops `branch` lines"):
        o = D.default_options(27, 59, overrides={"branch 27 58 2": "1 0 1.0"})
    assert o.branches_of(0, 2) == ()
    with pytest.warns(UserWarning):
        o = D.default_options(27, 59, overrides={"bestbranch": "y", "branch 27 58 2": "1 0 1.0"})
    assert dict(dict(o.branches_of(0, 2))[2]) == pytest.approx({1: 0.7, 0: 0.3})   # the file's
    with pytest.raises(ValueError):
        D.default_options(27, 59, overrides={"branch 27 58 2": "1 0 1.5"})


def test_bad_forms_are_refused_not_dropped(clean):
    with pytest.raises(ValueError):
        D.default_options(26, 56, overrides={"nlevels": 5})
    with pytest.raises(ValueError):
        D.default_options(26, 56, overrides={"strength 26 57": 8})
    clean.setenv(F.ENV_LINES, "strength 8 26 57")       # was: skipped silently
    with pytest.raises(ValueError, match="no per-nucleus"):
        F.cards(26, 56)


def test_unapplied_deck_line_is_refused_best_file_line_warns(clean):
    need_talys()  # needs the TALYS structure database; without it the best-file reads come back empty
    clean.setenv(F.ENV_LINES, "cknock a 1. cknock-a.table")          # energy-dependent table of a non-OMP keyword
    with pytest.raises(ValueError, match="not applied by the port"):
        F.cards(26, 56)
    # KWCOV B6: OMP adjustment tables are read now; Fe-56's best file finds its table in best/Fe056/misc/tables
    clean.setenv(F.ENV_LINES, "best y")
    assert F.cards(26, 56).omp.bumps[0].key == "awdadjust"


def test_deck_lines_reach_the_options(clean):
    clean.setenv(F.ENV_LINES, "ldmodel 2 26 57;colenhance y 25 56;nlevels 25 56 5;maxlevelsbin p 7")
    assert F.modes() == frozenset({"lines"})           # lines alone are the deck (was: dropped without an arm)
    F.activate(26, 56)
    o = D.default_options(26, 56)
    assert o.ldmodel_of(0, 0) == 2 and o.flagcol_of(1, 0) and o.nlev_of(1, 0) == 5 and o.nlevbin[2] == 7


def test_ejectiles_subset_is_refused():
    o = D.default_options(26, 56, overrides={"ejectiles": "g n p"})
    assert o.parinclude == (True, True, True, False, False, False, False)
    with pytest.raises(NotImplementedError, match="ejectiles"):
        D.reject_unported(o)
    D.reject_unported(D.default_options(26, 56, overrides={"ejectiles": "g n p d t h a"}))
    assert D.default_options(26, 56, overrides={"ejectiles": "p"}).parinclude[1] is True   # projectile always


# ------------------------------------------------------------------------------------------- best and fits

def _same(a, b):
    return (a.options, a.cells, a.globals_, a.particles) == (b.options, b.cells, b.globals_, b.particles)


@pytest.mark.parametrize("za", [(26, 56), (92, 238), (27, 59)])
def test_deck_best_equals_the_best_arm(clean, za):
    need_talys()  # needs the TALYS structure database; without it the best-file reads come back empty
    clean.setenv(F.ENV, "best")
    a = F.cards(*za)
    clean.delenv(F.ENV)
    clean.setenv(F.ENV_LINES, "best y")
    b = F.cards(*za)
    assert a.source and _same(a, b)


def test_bestend_puts_the_best_file_last(clean):
    need_talys()  # needs the TALYS structure database; without it the best-file reads come back empty
    clean.setenv(F.ENV_LINES, "best y;ldmodel 3")
    assert dict(F.cards(26, 56).options)["ldmodel"] == "3"     # the deck wins
    clean.setenv(F.ENV_LINES, "best y;bestend y;ldmodel 3")
    assert dict(F.cards(26, 56).options)["ldmodel"] == "2"     # the best file (Fe-56: ldmodel 2) wins


def test_bestfile_and_missing_file(clean, tmp_path):
    p = tmp_path / "My.talys"
    p.write_text("# mine\nldmodel 4\n")
    clean.setenv(F.ENV_LINES, f"best y;bestfile {p}")
    assert dict(F.cards(26, 56).options)["ldmodel"] == "4"
    clean.setenv(F.ENV_LINES, f"best y;bestfile {tmp_path / 'none.talys'}")
    with pytest.warns(UserWarning, match="best file does not exist"):
        assert "ldmodel" not in dict(F.cards(26, 56).options)


def test_fit_flags(clean):
    need_talys()  # needs the TALYS structure database; without it the best-file reads come back empty
    o = D.default_options(26, 56, overrides={"macsfit": "y"})
    assert o.flagfit and o.flagmacsfit and not o.flagngfit       # input_fit.f90:175-183
    o = D.default_options(26, 56, overrides={"gamgamfit": "y"})
    assert o.flagfit and o.flaggamgamfit and not o.flagngfit
    o = D.default_options(26, 56, overrides={"pnfit": "y"})
    assert o.flagfit and o.flagpnfit and not o.flagngfit
    clean.setenv(F.ENV_LINES, "ngfit y")
    assert any(s.startswith("ng.par") for s in F.cards(26, 56).source)
    clean.setenv(F.ENV_LINES, "macsfit y")
    src = F.cards(26, 56).source
    assert any(s.startswith("macs.par") for s in src) and not any(s.startswith("ng.par") for s in src)


def test_other_projectile_libraries_apply_on_a_neutron_run(clean):
    need_talys()  # needs the TALYS structure database; without it the best-file reads come back empty
    # pn.par's first entry: Ag-109, ldmodel 1, colenhance n, strength 8 (xsfit.f90 does not match the projectile)
    clean.setenv(F.ENV_LINES, "strength 8;pnfit y")
    c = F.cards(47, 109)
    assert any(s.startswith("pn.par") for s in c.source)
    assert any(k == "rwdadjust" for k, _, _ in c.particles)


# ---------------------------------------------------------------------------------------- energies, estop

def test_energy_forms():
    assert read_energies("14") == ((14.0,), (14.0,))
    g, k = read_energies("1 2 0.25")
    assert g == (1.0, 1.25, 1.5, 1.75, 2.0) and k == g
    g, _ = read_energies("1 10")                          # dE absent: 10 points
    assert len(g) == 10 and g[0] == 1.0 and g[-1] == 10.0
    g, k = read_energies("1 10 1", estop_mev=4.5)
    assert len(g) == 10 and k == (1.0, 2.0, 3.0, 4.0)       # enincmax stays 10 (read_energies.f90:180-194)
    # TALYS-2.25's own `energies` files with `estop 2.6` (the single-precision sum 0.5 + 3 x 0.7 is above 2.6)
    assert read_energies("1 10", estop_mev=2.6)[1] == (1.0, 2.0)
    assert read_energies("0.5 3.1 0.7", estop_mev=2.6)[1] == pytest.approx((0.5, 1.2, 1.9), rel=1e-6)


def test_energy_file(tmp_path):
    (tmp_path / "en").write_text("14\n0\n1\n5.\n1\n")
    assert read_energies("en", cwd=tmp_path) == ((1.0, 5.0, 14.0), (1.0, 5.0, 14.0))
    assert read_energies("en", estop_mev=5.0, cwd=tmp_path)[1] == (1.0, 5.0)


def test_predefined_grid_matches_talys():
    g = incident_grid("n0-20.grid")
    assert g[:3] == pytest.approx((1e-11, 2.53e-8, 1e-6), rel=1e-6) and g[-1] == pytest.approx(20.0)
    assert g == pytest.approx(TALYS_N0_20, rel=1e-6)
    p = incident_grid("p1-30.grid")                      # charged: integer MeV values only, >= 1 MeV
    assert p == pytest.approx(TALYS_P1_30, rel=1e-6)
    assert incident_grid("energies") is None


def test_estop_subset(clean):
    decl = (1.0, 5.0, 14.0)
    assert estop_subset(26, 56, decl, None) is None
    clean.setenv(F.ENV_LINES, "estop 6")
    assert estop_subset(26, 56, decl, None) == {1.0, 5.0}
    assert estop_subset(26, 56, decl, {5.0, 14.0}) == {5.0}


def test_read_deck(tmp_path):
    from physics.hf.input.deck import read_deck

    (tmp_path / "talys.inp").write_text("# c\nprojectile n\nelement Fe\nmass 56\nenergy 1 3 1\nestop 2.5\n"
                                        "LDMODEL 2 26 57\n")
    d = read_deck((tmp_path / "talys.inp").read_text(), tmp_path)
    assert (d.projectile, d.Z, d.A) == ("n", 26, 56)
    assert d.declared_mev == (1.0, 2.0, 3.0) and d.energies_mev == (1.0, 2.0)
    assert d.lines == ("estop 2.5", "ldmodel 2 26 57")


# ------------------------------------------------------------------------------- the engine, end to end

def test_engine_deck_best_is_the_best_arm_bitwise():
    """`best y` as a deck line runs the same numbers as INCOGNITA_TALYS_FIT=best (Fe-56, 14 MeV), each in a
    fresh process (the cards are cached per process)."""
    from tests._data import need_talys

    need_talys()
    code = ("import json, numpy as np, torch; from physics.hf import engine_c, warmrun; "
            "from physics.hf.engine import ChainedFull\n"
            "with torch.inference_mode(): r = engine_c.run(ChainedFull(Z=26, A=56, declared_energies=(14.0,)), {})\n"
            "a = warmrun.result_arrays(r); print(json.dumps({k: np.asarray(v).tolist() for k, v in a.items()}))")
    out = []
    for extra in ({"INCOGNITA_TALYS_FIT": "best"}, {"INCOGNITA_TALYS_FIT_LINES": "best y"}):
        env = {k: v for k, v in os.environ.items() if not k.startswith("INCOGNITA_")}
        env.update(extra)
        r = subprocess.run([sys.executable, "-c", code], env=env, capture_output=True, text=True, timeout=900)
        assert r.returncode == 0, r.stderr[-800:]
        out.append(r.stdout.strip().splitlines()[-1])
    assert out[0] == out[1]


# TALYS-2.25's own `energies` file for `energy n0-20.grid` / `energy p1-30.grid` (read_energies.f90:300)
TALYS_N0_20 = (
    1.0000E-11, 2.5300E-08, 1.0000E-06, 1.0000E-05, 1.0000E-04, 1.0000E-03, 2.0000E-03, 4.0000E-03,
    7.0000E-03, 1.0000E-02, 2.0000E-02, 4.0000E-02, 7.0000E-02, 0.1000, 0.2000, 0.3000, 0.4000, 0.5000,
    0.6000, 0.7000, 0.8000, 0.9000, 1.000, 1.200, 1.400, 1.600, 1.800, 2.000, 2.200, 2.400, 2.600, 2.800,
    3.000, 3.200, 3.400, 3.600, 3.800, 4.000, 4.200, 4.400, 4.600, 4.800, 5.000, 5.200, 5.400, 5.600, 5.800,
    6.000, 6.200, 6.400, 6.600, 6.800, 7.000, 7.200, 7.400, 7.600, 7.800, 8.000, 8.500, 9.000, 9.500, 10.00,
    10.50, 11.00, 11.50, 12.00, 12.50, 13.00, 13.50, 14.00, 14.50, 15.00, 16.00, 17.00, 18.00, 19.00, 20.00,
)
TALYS_P1_30 = tuple(float(e) for e in range(1, 31))
