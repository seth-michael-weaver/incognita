"""KWCOV B13: ingredient output files (docs/hf/COVERAGE_PLAN.md, batch B13).

outlevels / outdensity / filedensity / outgamma / filepsf / outinverse / outtransenergy / outomp / blockomp / outkd /
partable / outbasic: TALYS's levels*.out, ld*.gs, nld*.tab, psf*.XL, cross_g.tot, transmission_*.out, cross_*.tot,
omppar_*.out, omp.out, spr.opt, the KD03 lines and parameters.dat from the engine's own ingredients,
physics/hf/ingout.py. The decks were compared with stock TALYS-2.25 by scripts/kwcov/b13_response.py (numbers in the
plan); the tests here pin the keyword cascade, the quirks, and one Fe-56 engine run (14 MeV, TALYS mode) against
numbers transcribed from stock TALYS-2.25 (n + Fe-56, `energy 14`, every B13 switch on), with every other Results
array bitwise equal to the same run without the switches.
"""
from __future__ import annotations

import os

import numpy as np
import pytest

from physics.hf import ingout as G
from physics.hf.input import defaults as D
from physics.hf.input import fitlib as F

SWITCHES = ["outlevels y", "outdensity y", "filedensity y", "outgamma y", "filepsf y", "outinverse y", "outomp y",
            "outkd y", "partable y"]
TALYS_DECK = ["fluxclose n", "npwindow n", "chancap n", "nnleak n", "exactfis n", "alphatemp 0", "sfexit n",
              "kevleak2 n", "heavymacs2 n", "ftglobal n", "ccexitnbnf n", "tfold n", "ctwcont n", "alphaentr 0"]
TALYS_ENV = {"INCOGNITA_GRIDTOP": "n", "INCOGNITA_SPECCLOSE": "0", "INCOGNITA_LOWEPOT": "0",
             "INCOGNITA_TARMASSFIX": "0", "INCOGNITA_ISOROTPASS": "0"}


def _opts(**ov):
    return D.default_options(26, 56, "n", ov)


# ------------------------------------------------------------------------------------------------ keywords
def test_defaults_ask_for_nothing():
    o = _opts()
    assert G.active(o) == {}
    assert (o.flagbasic, o.flaglevels, o.flagdensity, o.filedensity, o.flaggamma, o.filepsf, o.flaginverse,
            o.flagoutomp, o.flagoutkd, o.flagpartable) == (False,) * 10
    assert o.flagblockomp and o.flagtransen


def test_outbasic_cascade():
    o = _opts(outbasic="y")
    assert (o.flaglevels, o.flagdensity, o.filedensity, o.flaggamma, o.flagoutomp, o.flaginverse) == (True,) * 6
    assert not o.filepsf and not o.flagoutkd and not o.flagpartable  # input_gammamodel.f90:62, input_ompmodel:110
    o = _opts(outbasic="y", outlevels="n", filedensity="n")
    assert not o.flaglevels and o.flagdensity and not o.filedensity
    o = _opts(outdensity="y")  # input_densitypar.f90:213: filedensity follows outdensity
    assert o.filedensity
    u = D.default_options(92, 238, "n", {"outbasic": "y"})
    assert u.flagfisout  # input_fissionpar.f90:113 (outfission = outbasic for a fissile target)
    assert not D.default_options(92, 238, "n", {}).flagfisout


def test_deck_lines_reach_options(monkeypatch):
    from physics.hf import chartrun

    lines = SWITCHES + ["outtransenergy n", "blockomp n", "blocklevels y"]
    for k in [k for k in os.environ if k.startswith("INCOGNITA_")]:
        monkeypatch.delenv(k, raising=False)
    monkeypatch.setenv(F.ENV_LINES, ";".join(lines))
    F._cards.cache_clear(); F.deactivate(); F.activate(26, 56)  # noqa: E702
    try:
        o = D.default_options(26, 56, "n")
    finally:
        monkeypatch.delenv(F.ENV_LINES)
        F._cards.cache_clear(); F.deactivate(); chartrun.drop_target_caches()  # noqa: E702
    assert o.flagpartable and o.flagoutkd and o.filepsf and not o.flagtransen and not o.flagblockomp
    assert o.flagblocklevels
    assert set(G.active(o)) == {"levels", "density", "gamma", "inverse", "omp", "kd", "partable"}


def test_d0_statistics_as_densitycum():
    # stock ld026057.gs (Fe-56 + n): D0 exp 25400 +- 2200, global 23453.81, theo 25397.92 -> C/E 0.999918, C/G 1.082891
    st = G._d0_stats(25397.92, 25400.0, 2200.0, 23453.81)
    assert st["C/E D0"] == pytest.approx(9.999180e-01, rel=1e-6)
    assert st["C/G D0"] == pytest.approx(1.082891, rel=1e-6)
    assert st["Frms D0"] == pytest.approx(1.0, abs=1e-6)
    assert G._d0_stats(2617.0, 0.0, 0.0, 2626.281)["C/E D0"] == 0.0  # no experimental D0: only C/G


# ------------------------------------------------------------------------------------------------ engine run
@pytest.fixture(scope="module")
def runs(tmp_path_factory):
    from physics.hf import chartrun
    from physics.hf.input.deck import run_deck

    saved = {k: v for k, v in os.environ.items() if k.startswith("INCOGNITA_")}
    for k in saved:
        del os.environ[k]
    os.environ.update(TALYS_ENV)
    d = tmp_path_factory.mktemp("b13")
    out = {}
    try:
        for tag, extra in (("on", SWITCHES), ("off", [])):
            F.deactivate(); F._cards.cache_clear(); chartrun.drop_target_caches()  # noqa: E702
            p = d / f"{tag}.inp"
            p.write_text("\n".join(["projectile n", "element fe", "mass 56", "energy 14"] + extra + TALYS_DECK) + "\n")
            out[tag] = run_deck(str(p))
    finally:
        for k in [k for k in os.environ if k.startswith("INCOGNITA_")]:
            del os.environ[k]
        os.environ.update(saved)
        F.deactivate(); F._cards.cache_clear(); chartrun.drop_target_caches()  # noqa: E702
    out["dir"] = d
    return out


def _blk(ing, name, i=0):
    return ing[name]["blocks"][i]


def test_output_only(runs):
    from physics.hf import warmrun

    a, b = warmrun.result_arrays(runs["on"]), warmrun.result_arrays(runs["off"])
    assert set(a) == set(b)
    for k in a:
        assert np.array_equal(np.asarray(a[k]), np.asarray(b[k])), k
    assert runs["off"].ingout == {}
    want = {"levels026056.out", "levels026057.out", "ld026056.gs", "ld026057.gs", "nld026056.tab", "nld026057.tab",
            "psf026057.E1", "psf026057.M1", "psf026057.E2", "psf026057.M2", "cross_g.tot", "omp.out", "spr.opt",
            "transmission_inc.out", "parameters.dat", "kd03"}
    want |= {f"transmission_{p}.out" for p in "npdtha"} | {f"cross_{p}.tot" for p in "npdtha"}
    want |= {f"omppar_{p}.out" for p in "npdtha"}
    assert set(runs["on"].ingout) == want  # the 38 files stock writes for this deck (+ kd03 from talys.out)


def test_vs_stock_fe56(runs):
    ing = runs["on"].ingout
    lv = _blk(ing, "levels026056.out")
    assert lv["pre"]["nuclear mass [amu]"] == pytest.approx(5.593494e01, rel=1e-6)
    assert lv["pre"]["neutron separation energy [MeV]"] == pytest.approx(1.119706e01, rel=1e-6)
    assert lv["pre"]["number of excited levels"] == 30
    assert lv["data"][1, 1] == pytest.approx(8.467780e-01, rel=1e-6) and lv["data"][1, 5] == pytest.approx(6.07e-12)
    h = ing["ld026056.gs"]["header"]["pre"]
    assert h["a(Sn) [MeV^-1]"] == pytest.approx(6.629000, rel=1e-6)
    assert h["Rhotot(Sn) [MeV^-1]"] == pytest.approx(2.448640e03, rel=1e-4)
    assert h["theoretical D0 [eV]"] == pytest.approx(2.617005e03, rel=1e-4)
    assert h["Chi-2 per level"] == pytest.approx(3.670846e-01, rel=2e-4)
    tot = _blk(ing, "ld026056.gs")
    assert tot["data"].shape == (296, 7)
    assert tot["data"][0, 3] == pytest.approx(2.691466, rel=1e-4)  # Total_LD of level 1
    tn = ing["transmission_n.out"]
    assert len(tn["blocks"]) == 56
    assert tn["blocks"][0]["pre"]["energy [MeV]"] == pytest.approx(1.018033e-03, rel=1e-6)
    assert tn["blocks"][0]["data"][0, 2] == pytest.approx(1.133237e-01, rel=1e-4)  # T(L+1/2, 0)
    cx = _blk(ing, "cross_n.tot")["data"]
    assert cx[0, 1:4] == pytest.approx([8.339260e04, 8.253090e03, 7.513950e04], rel=1e-4)
    psf = _blk(ing, "psf026057.E1")["data"]
    assert psf.shape == (86, 3)
    assert psf[0, 1] == pytest.approx(9.352860e-10, rel=1e-4)
    e2 = _blk(ing, "psf026057.E2")["data"]
    assert e2[0, 1] == psf[0, 1]  # gammaout.f90 quirk: the E2 file's f column is f_E1
    pg = ing["psf026057.E1"]["header"]["pre2"]
    assert pg["theoretical Gamma_gamma [eV]"] == pytest.approx(1.303671, rel=1e-4)
    assert pg["C/E Gamma_gamma"] == pytest.approx(1.417034e03, rel=1e-4)  # TALYS's gamgam in keV, labelled eV
    sp = ing["spr.opt"]["header"]["pre"]
    assert sp["S0"] == pytest.approx(3.415099e-01, rel=1e-4) and sp["Rprime [fm]"] == pytest.approx(3.115328, rel=1e-4)
    om = _blk(ing, "omppar_n.out")["data"]
    assert om[0, :4] == pytest.approx([1.018033e-03, 5.309614e01, 1.186, 0.663], rel=1e-5)
    pot = _blk(ing, "omp.out")["data"]
    assert pot.shape == (78, 5)
    assert pot[0] == pytest.approx([2.661100e-01, 4.786560e01, 1.029590, 7.760750e-02, -9.085990e-04], rel=1e-4)
    inc = _blk(ing, "transmission_inc.out")["data"]
    assert inc[0, 2] == pytest.approx(8.028737e-01, rel=1e-4)
    rows = {(k, z, a, q.strip()): v for k, z, a, v, q in D.parse_partable(ing["parameters.dat"]["text"])}
    assert rows[("a", 26, 57, "")] == pytest.approx(7.09313, abs=1e-5)
    assert rows[("pair", 26, 57, "")] == pytest.approx(1.58944, abs=1e-5)
    assert rows[("T", 26, 57, "0")] == pytest.approx(1.36966, abs=1e-5)
    gen = dict(((k, p), v) for k, p, v in D.parse_partable_general(ing["parameters.dat"]["text"]))
    assert gen[("strength", None)] == "9" and gen[("xscaptherm", None)] == "2.59000E+03"
    assert float(gen[("Esurf", None)]) == pytest.approx(12.06067, abs=1e-5)


def test_files_round_trip(runs, tmp_path):
    from physics.hf.yandf import parse_blocks

    names = G.write_files(runs["on"].ingout, tmp_path)
    assert "kd03.out" in names and "parameters.dat" in names
    b = parse_blocks(tmp_path / "transmission_n.out")
    assert len(b) == 56 and b[0].meta_float("energy [MeV]") == pytest.approx(1.018033e-03, rel=1e-6)
    b = parse_blocks(tmp_path / "ld026057.gs")
    assert b[0].meta_float("a(Sn) [MeV^-1]") == pytest.approx(7.093130, rel=1e-5)
    assert "Positive-Parity" in (tmp_path / "nld026056.tab").read_text()
    assert "--->" in (tmp_path / "levels026056.out").read_text()


def test_filepsf_needs_outgamma():
    o = _opts(filepsf="y")
    assert "gamma" not in G.active(o)  # gamma.f90:30 calls gammaout only for outgamma
