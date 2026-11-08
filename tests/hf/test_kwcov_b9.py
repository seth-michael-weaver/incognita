"""KWCOV B9: astrophysics (docs/hf/COVERAGE_PLAN.md, batch B9).

astro / astrogs / astroex / astroE / astroT / nonthermlev: TALYS's incident and temperature grids (egridastro),
the partition function (partfunc), rates and MACS (stellarrate), the files of astroout, and the thermalised
target (astrotarget / compprepare's astro feed, astro/thermal.py). The rates were compared with stock TALYS-2.25 by
scripts/kwcov/b9_response.py (numbers in the plan); the tests here pin the transcriptions against stock numbers,
the parsing and the refusals, and one engine run (Au-197 `astroE 0.03`) against stock's macs.g.
"""
from __future__ import annotations

import math
import os

import numpy as np
import pytest

from physics.hf import chartrun
from physics.hf.astro import rates as R
from physics.hf.astro import thermal as TH
from physics.hf.input import defaults as D
from physics.hf.input import fitlib as F
from physics.hf.input.deck import astro_of

STOCK_T9 = [1.0e-4, 5.0e-4, 1.0e-3, 5.0e-3, 1.0e-2, 5.0e-2, 0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9,
            1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]


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


# ------------------------------------------------------------------------------------------------ transcriptions
def test_t9_grid_is_stock():
    t9, et9 = R.t9_grid()
    assert len(t9) == 30 and np.allclose(t9, STOCK_T9, rtol=1e-6)
    assert abs(et9[-1] - 8.617333e-01) < 1e-6 and abs(et9[0] - 8.617333e-06) < 1e-11  # stock E-average column
    t1, _ = R.t9_grid(0.348136, 1)
    assert t1.tolist() == [pytest.approx(0.348136, rel=1e-6)]


def test_energy_grid_is_stock_au197():
    # stock TALYS-2.25 n + Au-197 astro y: 110 incident energies (LAB), talys.out
    from physics.hf.compound.dens_reference import structure_of

    _, _, m = structure_of(79, 197)
    e = R.energy_grid(1, float(m.specmass[0, 1, 1]), float(m.redumass_amu[0, 1, 1]),
                      {t: float(m.s_mev[0, 0, t]) for t in range(7)}, 79)
    assert e.shape == (110,)
    for i, v in ((0, 2.01024e-06), (4, 1.00512e-05), (31, 0.01005), (32, 0.01407), (54, 0.10252), (58, 0.30355),
                 (72, 1.007), (109, 50.25806)):
        assert abs(e[i] / v - 1) < (2e-4 if i != 72 else 1e-3), (i, e[i], v)


def test_maxwell_rate_constant_sigma():
    # MACS of a constant cross section = 2/sqrt(pi) sigma (centre of mass); TALYS's sgl constants make it 1.00077x
    e = np.unique(np.concatenate([np.arange(1, 100) * 1e-6, np.arange(1, 8000) * 1e-4]))
    t9 = np.array([0.348136], dtype=np.float32)
    rate, macs = R.maxwell_rate(e, np.full(e.shape, 1000.0), t9, 1.0, 1.0, None)
    assert abs(macs[0] / (2 / math.sqrt(math.pi) * 1000.0) - 1.00077) < 2e-3
    # rate = MACS x v_T x N_A (TALYS's convfac)
    assert abs(rate[0] / (macs[0] * 2.45484e5 * math.sqrt(0.348136)) - 1) < 1e-6


def test_partition_function_discrete_and_astrogs():
    lv = dict(e=[0.0, 0.1], j=[1.5, 0.5], nlast=1, nlev=1)
    grid = dict(ex=np.array([0.0, 0.1]), dex=np.zeros(2), maxex=1)
    t9 = np.array([1.0], dtype=np.float32)
    g = R.partition_function(t9, lv, grid, lambda e, j, p: np.zeros_like(e), 197)
    assert abs(g[0] - (4 + 2 * math.exp(-11.605 * 0.1)) / 4) < 1e-6
    assert R.partition_function(t9, lv, grid, None, 197, astrogs=True).tolist() == [1.0]
    # nonthermlev leaves the level out (partfunc.f90:101)
    g1 = R.partition_function(t9, lv, grid, lambda e, j, p: np.zeros_like(e), 197, nonthermlev=1)
    assert abs(g1[0] - 1.0) < 1e-9


def test_macs_experimental_file():
    m, dm = R.macs_experimental(79, 197)
    assert (m, dm) == (613.38, 6.0293)  # structure/gamma/macs/Au.macs, the number stock's macs.g prints


def test_read_stock_and_write_roundtrip(tmp_path):
    t9, et9 = R.t9_grid()
    out = {"astrorate.g": {"T": t9, "reaction_rate": np.ones(30), "MACS": np.ones(30), "G(T)": np.ones(30),
                           "E-average": et9}, "_meta": {}}
    R.write_files(out, tmp_path)
    back = R.read_stock(tmp_path / "astrorate.g")
    assert list(back) == ["T", "reaction_rate", "MACS", "G(T)", "E-average"] and np.allclose(back["T"], t9, rtol=1e-6)


# ------------------------------------------------------------------------------------------------ keywords
def test_astro_keywords_parse():
    a = astro_of(("astroe 0.03",))
    assert a["astro"] and a["astrogs"] and abs(a["astroT9"] - 0.348136) < 1e-5 and a["nTmax"] == 1
    a = astro_of(("astrot 1.",))
    assert a["astro"] and not a["astrogs"] and abs(a["astroE"] - 0.0861733) < 1e-6
    a = astro_of(("astro y", "astroex y", "nonthermlev 1"))
    assert a["astroex"] and a["nonthermlev"] == 1 and a["nTmax"] == 30 and not a["astrogs"]
    assert astro_of(("astrogs y",)) is None and astro_of(()) is None


def test_astro_keyword_refusals():
    with pytest.raises(ValueError, match="Only astroE OR astroT"):
        astro_of(("astroe 0.03", "astrot 1."))
    with pytest.raises(ValueError, match="astroT"):
        astro_of(("astrot 20",))
    with pytest.raises(ValueError, match="segment = 1"):
        astro_of(("astro y", "segment 3"))
    with pytest.raises(NotImplementedError, match="racap"):
        astro_of(("astro y", "racap y"))


def test_options_astroe_astrot(clean):
    for line, gs in (("astroe 0.03", True), ("astrot 0.5", False)):
        clean.setenv(F.ENV_LINES, line)
        F._cards.cache_clear(); F.deactivate(); chartrun.drop_target_caches()
        from physics.hf.emission.feeding import Cascade

        o = Cascade(79, 197, 1.0, energies=(1.0,)).options
        assert o.flagastro and o.flagastrogs is gs
        assert (o.transpower, o.transeps, o.xseps_mb, o.popeps_mb) == (15, 1.0e-18, 1.0e-17, 1.0e-13)


def test_deck_transeps_reaches_the_chain(clean):
    # KWCOV B9 bug fix: Options.transeps (deck `transeps`, astro y) was not the chain's Cascade.transeps
    from physics.hf.emission.feeding import Cascade

    assert Cascade(26, 56, 1.0, energies=(1.0,)).transeps == 1.0e-8
    clean.setenv(F.ENV_LINES, "transeps 1e-12")
    F._cards.cache_clear(); F.deactivate(); chartrun.drop_target_caches()
    assert Cascade(26, 56, 1.0, energies=(1.0,)).transeps == 1.0e-12


def test_thermal_switch_and_refusals():
    class O:
        flagastro, flagastrogs, flagfission, wmode = True, False, False, 1

    assert TH.active(O) and not TH.active(object())
    TH.check(O)
    O.flagfission = True
    with pytest.raises(NotImplementedError, match="fissile"):
        TH.check(O)
    O.flagfission, O.wmode = False, 2
    with pytest.raises(NotImplementedError, match="widthmode"):
        TH.check(O)
    O.flagastrogs = True
    TH.check(O)  # astrogs y: nothing thermal


def test_ewfc_default_untouched(clean):
    from physics.hf.emission.feeding import Cascade

    cas = Cascade(26, 56, 1.0, energies=(1.0,))
    assert getattr(cas, "astro_ewfc_mev", None) is None and abs(cas.ewfc_mev - 11.197) < 0.01
    cas.astro_ewfc_mev = 0.3
    assert cas.ewfc_mev == 0.3


# ------------------------------------------------------------------------------------------------ engine vs stock
def test_au197_macs30_vs_stock(clean, tmp_path):
    # stock TALYS-2.25 n + Au-197 `astroE 0.03`: macs.g 9.34376E+02 mb (Exp 6.13380E+02), astrorate.g rate 1.35100E+08
    from physics.hf.input.deck import run_deck

    (tmp_path / "talys.inp").write_text("projectile n\nelement au\nmass 197\nenergy 1.\nastroe 0.03\n")
    r = run_deck(tmp_path / "talys.inp")
    assert r.n == 75
    m = float(r.astro["macs.g"]["MACS(mb)"][0])
    assert abs(math.log(m / 934.376)) < 0.02
    assert float(r.astro["macs.g"]["Exp(mb)"][0]) == 613.38
    g = r.astro["astrorate.g"]
    assert abs(math.log(float(g["reaction_rate"][0]) / 1.35100e8)) < 0.02 and float(g["G(T)"][0]) == 1.0
    assert "(n,g)Au198" in r.astro["astrorate.tot"]
