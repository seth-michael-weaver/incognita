"""KWCOV B14 part 1: fission fragment / product yields, `massdis y` + `fymodel 1` (Brosa) (docs/hf/COVERAGE_PLAN.md).

physics/hf/fisyield.py ports massdis.f90 (fymodel 1 branch, normalisation), brosafy.f90, neck.f90, trans/trapzd/
funcfismode, fmin/fidi and the shape helpers, and massdisout.f90's files. The decks were compared with stock TALYS-2.25
by scripts/kwcov/b14_response.py (numbers in the plan); the tests here pin the helpers, the refusals, the Brosa modes on
their own (a model level density) and one engine run against stock's n + U-235 1 MeV yieldA file (TALYS mode).
"""
from __future__ import annotations

import math
import os

import numpy as np
import pytest

from physics.hf import fisyield as Y
from physics.hf.input import defaults as D
from physics.hf.input import fitlib as FL

# stock TALYS-2.25 n + U-235, 1 MeV, `massdis y; fymodel 1` (default deck otherwise): yieldA0001.000.fis
# A: (FP_yield, FF_yield)
U235_1MEV = {90: (3.838501E-02, 2.738316E-02), 94: (6.319164E-02, 5.048932E-02), 96: (6.840242E-02, 5.877879E-02),
             98: (6.546637E-02, 6.217166E-02), 100: (5.609042E-02, 5.986270E-02), 104: (2.873210E-02, 4.173046E-02),
             132: (5.833583E-02, 4.173046E-02), 136: (6.737833E-02, 5.986270E-02), 138: (6.012813E-02, 6.217166E-02),
             140: (4.886340E-02, 5.877879E-02), 144: (2.170591E-02, 3.922953E-02)}
U235_TOT = (1.999894E+00, 2.000001E+00)


@pytest.fixture
def clean(monkeypatch):
    from physics.hf import chartrun

    for k in [k for k in os.environ if k.startswith("INCOGNITA_")]:
        monkeypatch.delenv(k, raising=False)
    FL.deactivate(); FL._cards.cache_clear(); chartrun.drop_target_caches()
    yield monkeypatch
    for k in [k for k in os.environ if k.startswith("INCOGNITA_")]:
        monkeypatch.delenv(k, raising=False)
    FL.deactivate(); FL._cards.cache_clear(); chartrun.drop_target_caches()


# ------------------------------------------------------------------------------------------------ helpers
def test_shape_factors():
    e = np.array([-0.5, -0.1, 0.0, 0.1, 0.5], dtype=np.float32)
    fs, fc = Y.fsurf(e), Y.fcoul(e)
    assert fs.dtype == np.float32 and fc.dtype == np.float32
    assert fs[2] == 1.0 and fc[2] == 1.0
    # small deformation: both factors tend to 1 from either side (Bohr-Wheeler limit)
    assert abs(fs[1] - 1.0) < 0.02 and abs(fs[3] - 1.0) < 0.02 and abs(fc[1] - 1.0) < 0.02 and abs(fc[3] - 1.0) < 0.02
    # bdef of a spherical U-236 = liquid-drop binding (negative, about -1790 MeV)
    b = float(Y.bdef(np.float32(236.0), np.float32(92.0), np.float32(0.0)))
    assert -1850.0 < b < -1700.0
    assert Y._sform(np.zeros(1, np.float32), np.zeros(1, np.float32))[0] == 1.0


def test_spline_and_rtbis():
    x = Y.TEMPS
    y = (x ** 3 - 2 * x).astype(np.float32)
    y2 = Y.spline(x, y, 9)
    for xv in (0.3, 1.2, 2.5):  # through the knots
        assert abs(float(Y.splint(x, y, y2, 9, np.float32(xv))) - (xv ** 3 - 2 * xv)) < 1e-4
    with pytest.raises(RuntimeError):
        Y.splint(x, y, y2, 1, np.float32(0.5))
    r = Y.rtbis_vec(lambda z: (z * z - 2.0).astype(np.float32), np.zeros(3, np.float32), 3.0, 1e-5)
    assert np.allclose(r, math.sqrt(2.0), atol=2e-5)


def test_estring():
    assert Y.estring(1.0) == "0001.000"
    assert Y.estring(14.0) == "0014.000"
    assert Y.estring(0.5) == "0000.500"
    assert Y.estring(2.53e-8) == "2.53E-08"


# ------------------------------------------------------------------------------------------------ switches
def test_settings_and_refusals():
    o = D.default_options(92, 235, "n")
    assert Y.settings(o) is None  # default: off
    o = D.default_options(92, 235, "n", overrides={"massdis": "y"})
    assert o.fymodel == 2 and o.pfnsmodel == 2 and o.Rfiseps == 1e-9
    assert Y.settings(o)["fymodel"] == 2  # TALYS's default with massdis: GEF (B14 part 2, test_kwcov_b14b.py)
    for fy in (3,):  # KWCOV B14c: fymodel 4 and 5 run (test_kwcov_b14c.py)
        with pytest.raises(NotImplementedError, match=f"fymodel {fy}"):
            Y.settings(D.default_options(92, 235, "n", overrides={"massdis": "y", "fymodel": str(fy)}))
    with pytest.raises(ValueError, match="outside 1..5"):
        Y.settings(D.default_options(92, 235, "n", overrides={"fymodel": "6"}))
    with pytest.raises(ValueError, match="ffmodel 5"):
        Y.settings(D.default_options(92, 235, "n", overrides={"ffmodel": "5"}))
    with pytest.raises(ValueError, match="gefran 10"):
        Y.settings(D.default_options(92, 235, "n", overrides={"gefran": "10"}))
    s = Y.settings(D.default_options(92, 235, "n", overrides={"massdis": "y", "fymodel": "1", "ffevaporation": "n",
                                                               "rfiseps": "1e-3", "yieldfile": "u.ff"}))
    assert s == {"fymodel": 1, "ffevap": False, "Rfiseps": 1e-3, "gefran": 50000}
    # no fission channel: massdis does nothing, as TALYS (flagfission .and. flagmassdis), whatever fymodel says
    assert Y.settings(D.default_options(26, 56, "n", overrides={"massdis": "y"})) is None


def test_deck_lines_parse(clean):
    clean.setenv("INCOGNITA_TALYS_FIT", "lines")
    clean.setenv("INCOGNITA_TALYS_FIT_LINES", "massdis y;fymodel 1;outfy y;gefran 1000;yieldfile u235.ff;ffspin y")
    FL._cards.cache_clear()
    c = FL.activate(92, 235, "n")
    o = D.default_options(92, 235, "n", overrides=c.option_overrides if c is not None else None)
    assert o.flagmassdis and o.fymodel == 1 and o.flagoutfy and o.gefran == 1000 and o.flagffspin
    assert o.yieldfile.lower() == "u235.ff"


# ------------------------------------------------------------------------------------------------ Brosa on its own
def _model_ld(A: int):
    def ign(e):
        return np.full(np.shape(e), np.float32(A / 10.0), dtype=np.float32) if np.ndim(e) else np.float32(A / 10.0)

    def dens(e):
        e = np.asarray(e, dtype=np.float64)
        return np.exp(2.0 * np.sqrt(A / 10.0 * e))

    return ign, dens


def test_brosafy_model_ld():
    ign, dens = _model_ld(236)
    disa, disacor, disaz, disazcor = Y.brosafy(92, 236, 7.0, True, ign, dens)
    assert abs(float(disa.sum()) - 2.0) < 1e-4 and abs(float(disacor.sum()) - 2.0) < 1e-4
    assert abs(float(disaz.sum()) - 2.0) < 1e-4
    assert np.allclose(disa, disaz.sum(axis=1), atol=1e-6)
    a = np.arange(disa.shape[0])
    light = a < 118
    assert 90 <= a[light][np.argmax(disa[light])] <= 104 and 132 <= a[~light][np.argmax(disa[~light])] <= 146
    # post-neutron masses sit below the pre-neutron ones (Brosa's estimate: about 4 for both fragments; stock U-235
    # 1 MeV yieldA gives 4.0)
    nu = float((disa * a).sum() - (disacor * a).sum())  # both fragments
    assert 2.0 < nu < 6.0
    # ffevaporation n: coarse steps, no post-neutron yields (brosafy.f90:675-688)
    d2, c2, z2, zc2 = Y.brosafy(92, 236, 7.0, False, ign, dens)
    assert float(c2.sum()) == 0.0 and float(zc2.sum()) == 0.0 and abs(float(d2.sum()) - 2.0) < 1e-4


# ------------------------------------------------------------------------------------------------ engine vs stock
TALYS_DECK = ["fluxclose n", "npwindow n", "chancap n", "nnleak n", "exactfis n", "alphatemp 0", "sfexit n",
              "kevleak2 n", "heavymacs2 n", "ftglobal n", "ccexitnbnf n", "tfold n", "ctwcont n", "alphaentr 0"]
TALYS_ENV = {"INCOGNITA_GRIDTOP": "n", "INCOGNITA_SPECCLOSE": "0", "INCOGNITA_LOWEPOT": "0",
             "INCOGNITA_TARMASSFIX": "0", "INCOGNITA_ISOROTPASS": "0"}


def _run(clean, lines, Z=92, A=235, energies=(1.0,)):
    import torch

    from physics.hf import engine_c
    from physics.hf.engine import ChainedFull

    for k, v in TALYS_ENV.items():
        clean.setenv(k, v)
    clean.setenv("INCOGNITA_TALYS_FIT", "lines")
    clean.setenv("INCOGNITA_TALYS_FIT_LINES", ";".join(lines + TALYS_DECK))
    with torch.inference_mode():
        return engine_c.run(ChainedFull(Z=Z, A=A, declared_energies=energies))


@pytest.mark.slow
def test_u235_1mev_vs_stock(clean):
    r = _run(clean, ["massdis y", "fymodel 1"])
    f = r.fission_yields["yieldA0001.000.fis"]
    assert list(f["A"][:3]) == [1, 2, 3] and len(f["A"]) == 235
    for a, (fp, ff) in U235_1MEV.items():
        assert abs(math.log(f["FF_yield"][a - 1] / ff)) < 0.02, (a, f["FF_yield"][a - 1], ff)
        assert abs(math.log(f["FP_yield"][a - 1] / fp)) < 0.02, (a, f["FP_yield"][a - 1], fp)
    assert abs(f["Tot"][0] - U235_TOT[0]) < 1e-3 and abs(f["Tot"][1] - U235_TOT[1]) < 1e-3
    za = r.fission_yields["yieldZA0001.000.fis"]
    assert abs(za["FF_yield"].sum() - 2.0) < 1e-2  # the rows with pre- and post-neutron xs >= fpeps
    assert "fp054136.tot" in r.fission_yields and "fp136.tot" in r.fission_yields and "rp054136.tot" in r.fission_yields
    # FF cross sections carry the fission cross section (every bin above fpeps)
    assert abs(f["Tot"][3] / float(r.totals_mb["fission"][0]) - 1.0) < 0.01


@pytest.mark.slow
def test_default_run_has_no_yields(clean):
    r = _run(clean, [])
    assert r.fission_yields == {}
    with pytest.raises(NotImplementedError, match="fymodel 3"):
        _run(clean, ["massdis y", "fymodel 3"])


def test_natural_target_refused(clean, tmp_path):
    from physics.hf.input.deck import run_deck

    (tmp_path / "talys.inp").write_text("projectile n\nelement u\nmass 0\nenergy 1.\nmassdis y\nfymodel 1\n")
    with pytest.raises(ValueError, match="natural targets"):  # checkvalue.f90:1075
        run_deck(tmp_path / "talys.inp")
