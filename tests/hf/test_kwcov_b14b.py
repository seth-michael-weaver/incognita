"""KWCOV B14 part 2: GEF (`massdis y`, fymodel 2 = TALYS's default), yields and prompt neutrons (docs/hf/COVERAGE_PLAN.md).

physics/hf/gef.py ports geftalys.f (+ the geffunctions.f functions it calls) with geftalys's own random-number generator;
physics/hf/fisyield.py adds massdis.f90's GEF branch and nubarout.f90 / nudisout.f90's files. The stock numbers pinned
here come from TALYS-2.25 n + U-235 at 1 MeV with `massdis y; outfy y; gefran 1000` (the first excitation bin of U-236,
Excit = 7.54124212 MeV, as printed by geftalys with outfy y). scripts/kwcov/b14b_response.py does the full comparison.
"""
from __future__ import annotations

import math
import os

import numpy as np
import pytest

from physics.hf import fisyield as Y
from physics.hf import gef as G
from physics.hf.input import defaults as D
from physics.hf.input import fitlib as FL

F = np.float32
TALYS_DIR = os.path.expanduser(os.environ.get("TALYS_DIR", "~/opt/talys-src"))
HAVE_DATA = os.path.isfile(os.path.join(TALYS_DIR, "structure", "fission", "gef", "beldm.dat"))
needs_data = pytest.mark.skipif(not HAVE_DATA, reason="TALYS structure/fission/gef not found")

# stock geftalys output, U-236 first bin (gefran 1000, outfy y)
BIN1_E = F(7.54124212)
BIN1_EEX = F(4.15038919)
BIN1_YIELDS = (1.22833846e-03, 5.92378192e-02, 0.897600651, 4.19331379e-02, 0.0, 0.0)
BIN1_A = {90: (0.05300, 0.06700), 95: (0.06100, 0.05300), 96: (0.06300, 0.08000), 100: (0.04800, 0.03900),
          134: (0.04200, 0.05900), 136: (0.04800, 0.08100), 140: (0.06300, 0.06600), 142: (0.05800, 0.07300)}
BIN1_N = {60: (0.10300, 0.05100), 62: (0.05700, 0.02400), 64: (0.01100, 0.00200), 90: (0.09100, 0.04000)}
BIN1_NUA = {90: (1.28571, 1.30612), 95: (1.57143, 1.58537), 96: (1.59574, 1.68750), 100: (1.79070, 1.67647),
            134: (1.46875, 1.77551), 136: (1.70455, 2.05195), 140: (2.41667, 2.11111), 142: (2.10714, 1.90141)}
BIN1_PNU = {1: 9.49494913e-02, 2: 0.251515150, 3: 0.337373734, 4: 0.215151519, 5: 8.48484859e-02,
            6: 1.41414143e-02, 7: 2.02020211e-03}
BIN1_MEAN = 2.99393916


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


# ------------------------------------------------------------------------------------------------ generator
def test_generator_is_geftalys_ran2():
    st = G.GefStream("talys")
    st.reset(1)
    lid = np.zeros(1, dtype=np.int64)
    x = G.SEED
    for _ in range(5):  # ran2 with integers: (ranb, rans) 24-bit halves, gb/gs multipliers
        ranb, rans = x >> 24, x & 0xFFFFFF
        a = 6328637 * rans
        b = 1136868 * rans + 6328637 * ranb + (a >> 24)
        rans, ranb = a & 0xFFFFFF, b & 0xFFFFFF
        x = (ranb << 24) | rans
        assert st.rndm(lid)[0] == F(x / 2.0 ** 48)
    # lanes: lane 0 = the stock seed, the others hashed odd 48-bit states (no power-of-two lattice), offset shifts them
    ln = G.GefStream("lanes")
    ln.reset(1000)
    assert int(ln.x[0]) == G.SEED and (ln.x % 2 == 1).all() and (ln.x < 2 ** 48).all()
    assert len(set(ln.x.tolist())) == 1000 and not ln.iset.any()  # lanes start with an empty PGauss cache
    u = ln.rndm(np.arange(1000)).astype(np.float64)
    assert abs(u.mean() - 0.5) < 0.03 and abs(np.corrcoef(u[:-1], u[1:])[0, 1]) < 0.1
    assert not np.array_equal(G.lane_seeds(10, 1), G.lane_seeds(10, 0))


def test_pgauss_save_state():
    st = G.GefStream("talys")
    st.reset(1)
    lid = np.zeros(1, dtype=np.int64)
    # DATA Iset/1/, GSet/0.5/: the program's first PGauss returns mean + 0.5 sigma without drawing
    assert st.pgauss(lid, F(10.0), F(2.0))[0] == F(11.0) and st.ndraw == 0
    v = st.pgauss(lid, F(0.0), F(1.0))[0]
    assert st.ndraw >= 2 and st.iset[0]
    assert st.pgauss(lid, F(0.0), F(1.0))[0] == st.gset[0] or not st.iset[0]
    st.reset(1)  # a new geftalys call reseeds but keeps the cache (SAVE)
    assert not st.iset[0] and np.isfinite(v)


# ------------------------------------------------------------------------------------------------ functions
def test_small_functions():
    assert G.nint(F(2.5)) == 3 and G.nint(F(-2.5)) == -3 and G.nint(F(2.4999998)) == 2
    assert G.fint(F(-1.7)) == -1
    assert G.p5(F(1.1)) == F(F(1.1) * F(1.1)) * F(F(1.1) * F(F(1.1) * F(1.1)))
    assert abs(float(G.erf_nr(F(0.5))) - math.erf(0.5)) < 2e-7
    assert float(G.gaussintegral(F(0.0), F(1.0))) == 0.5
    # Ivenodd: no even-odd effect = floor(x + 0.5); full effect pushes to even
    assert G.ivenodd(F(52.3), F(0.0)) == 52
    out = np.array([G.ivenodd(F(x), F(1.0)) for x in np.linspace(50.0, 54.0, 41, dtype=F)])
    assert (out % 2 == 0).mean() > 0.7
    # PEgammahigh's grid assumption: nint(10 * (0.1 * M)) == M in single precision
    m = np.arange(1, 5001)
    assert (G.nint((F(0.1) * m.astype(F)) * F(10.0)) == m).all()


@needs_data
def test_barrier_and_setup_u236():
    data = G.load_data()
    assert data.beldm.shape == (204, 137) and data.rnuctab.shape == (3885, 8)
    assert F(BIN1_E - G.bftfb(F(92.0), F(236.0), data)) == BIN1_EEX  # "After: Eex" of the stock printout
    tab = G.Tables(data)
    cs = G.call_setup(F(92.0), F(236.0), data, tab)
    assert cs.SpinCN == 0.0 and cs.DeltaS0 == F(0.3)
    bs = G.bin_setup(cs, BIN1_E, tab, data)
    assert np.allclose(bs.yields, BIN1_YIELDS, rtol=1e-6, atol=1e-9)


# ------------------------------------------------------------------------------------------------ exact stream
@needs_data
def test_bin1_exact_stock_stream():
    """The stock generator stream event by event: stock's sampled tables to the printed digits."""
    st = G.GefStream("talys")
    r = G.geftalys(92.0, 236.0, np.array([BIN1_E]), np.array([1.0], F), 1000, st, detail=True)
    d = r.detail[0]
    for a, (pre, post) in BIN1_A.items():
        assert abs(d["apre"][a] - pre) < 6e-6 and abs(d["apost"][a] - post) < 6e-6, a
    for n, (pre, post) in BIN1_N.items():
        assert abs(d["anpre"][n] - pre) < 6e-6 and abs(d["anpost"][n] - post) < 6e-6, n
    for a, (pre, post) in BIN1_NUA.items():
        assert abs(d["anapre"][a] - pre) < 6e-6 and abs(d["anapost"][a] - post) < 6e-6, a
    for k, v in BIN1_PNU.items():
        assert abs(d["ann"][k] / v - 1.0) < 1e-6, k
    assert abs(float(d["mean"]) / BIN1_MEAN - 1.0) < 1e-7
    # the /outgef/ sums massdis reads (fsig = 1): pre / post yields sum to 2, nubar = the bin mean
    assert abs(float(r.ysum.sum()) - 2.0) < 1e-4 and abs(float(r.ysump.sum()) - 2.0) < 1e-4
    assert abs(float(r.yAZ.sum()) - 2.0) < 1e-4 and float(r.anMean_sum) == float(d["mean"])


@needs_data
def test_lanes_statistics():
    """Lanes (the engine's default): own substream per event; the same distribution as stock within noise."""
    st = G.GefStream("lanes")
    r = G.geftalys(92.0, 236.0, np.array([BIN1_E]), np.array([1.0], F), 20000, st, detail=True)
    d = r.detail[0]
    assert abs(float(d["mean"]) - BIN1_MEAN) < 0.06  # stock at 1000 events: +-0.04 (1 sigma)
    assert np.allclose(d["yields"], BIN1_YIELDS, rtol=1e-6)
    light = d["apre"][1:118].sum() + 0.5 * d["apre"][118]
    assert abs(light - 1.0) < 0.005  # one light, one heavy fragment per event (A_CN = 236)
    st2 = G.GefStream("lanes")
    r2 = G.geftalys(92.0, 236.0, np.array([BIN1_E]), np.array([1.0], F), 20000, st2)
    assert np.array_equal(r.ysum, r2.ysum)  # deterministic


# ------------------------------------------------------------------------------------------------ massdis / output
def test_settings_fymodel2(clean):
    o = D.default_options(92, 235, "n", overrides={"massdis": "y"})
    s = Y.settings(o)
    assert s["fymodel"] == 2 and s["gefran"] == 50000 and s["gef_stream"].mode == "lanes"
    clean.setenv("INCOGNITA_GEF_STREAM", "talys")
    assert Y.settings(o)["gef_stream"].mode == "talys"
    clean.setenv("INCOGNITA_GEF_STREAM", "fast")
    with pytest.raises(ValueError, match="lanes"):
        Y.settings(o)
    clean.delenv("INCOGNITA_GEF_STREAM")
    for fy in (3, 4, 5):
        with pytest.raises(NotImplementedError, match="part 3"):
            Y.settings(D.default_options(92, 235, "n", overrides={"massdis": "y", "fymodel": str(fy)}))
    assert Y.settings(D.default_options(92, 235, "n", overrides={"massdis": "y", "gefran": "1000"}))["gefran"] == 1000


def test_pdisnu_numin_quirk():
    pd = np.zeros(51, F)
    pd[1:11] = F(1.0)
    Y._pdisnu_norm(pd)
    assert np.allclose(pd[1:9], 1.0 / 8.0) and pd[9] == 1.0 and pd[10] == 1.0  # massdis.f90:457 sums 1..numin only


def test_build_nu_files():
    def g(nub):
        pd = np.zeros(51, F)
        pd[2], pd[3] = 0.4, 0.6
        nua = np.zeros(415, F)
        nua[100] = 1.5
        return {"nubar": F(nub), "Pdisnu": pd, "nuA": nua}

    rec = [{"E": 1.0, "gef": g(0.0)}, {"E": 2.0, "gef": g(2.5)}, {"E": 3.0, "gef": g(0.0)}, {"E": 4.0, "gef": g(2.7)}]
    out = Y.build_nu(rec, {"Atarget": 235})
    # nubarout: zero rows for the energies before the file exists, energies with nubar = 0 afterwards skipped
    assert list(out["nubarn.tot"]["E"]) == [1.0, 2.0, 4.0] and list(out["nubarn.tot"]["nubar"])[0] == 0.0
    p = out["Pnun0002.000.fis"]
    assert list(p["number"]) == [0, 1, 2, 3, 4] and abs(p["nu"][3] - 0.6) < 1e-7
    assert len(out["nunA0004.000.fis"]["A"]) == 235 and out["nunA0004.000.fis"]["nu"][99] == F(1.5)
    assert out["nunZA0002.000.fis"]["Z"].size == 0 and "Pnun0001.000.fis" not in out


@needs_data
def test_fymodel4_fragment_files():
    """fymodel 4 reader (engine use refused until ffevap, part 3): file choice and energy interpolation."""
    files, et = Y.ff_files(92, 236, 7.54124212, ffmodel=1)
    assert [os.path.basename(f) for f in files] == ["U236_7.00e+00MeV_gef.ff", "U236_8.00e+00MeV_gef.ff"]
    assert et == [7.0, 8.0]
    r = Y.ff_pairs(files, et, 236, 7.54124212)
    assert abs(r["efac"] - 0.54124212) < 1e-6 and len(r["pairs"]) > 100
    ysum = sum(float(p[4]) for p in r["pairs"])
    assert 0.9 < ysum < 1.1  # pair yields sum to 1
    assert all(p[1] + p[3] == 236 for p in r["pairs"])
    files, et = Y.ff_files(92, 236, 0.0, ffmodel=1)  # below the first table: one file
    assert len(files) == 1 and "2.53e-08" in files[0]
    assert Y.ff_files(92, 236, 7.0, yieldfile="my.ff") == (["my.ff"], [])
    with pytest.raises(FileNotFoundError, match="Non-existent FF file"):
        Y.ff_files(92, 236, 7.0, ffmodel=0)  # no structure/fission/ff/user database


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


# stock TALYS-2.25 n + U-235 1 MeV, deck `massdis y` (GEF, gefran 50000), ~/kwcov/stock/b14b/u235_8577f5297a:
# yieldA0001.000.fis summed over the light (A 90-100) and heavy (134-144) peaks, nubarn.tot, Pnun0001.000.fis
U235_PEAKS = {"FF": (0.632564, 0.613507), "FP": (0.661072, 0.664954)}
U235_NUBAR = 3.010442
U235_PNU = {2: 2.609862e-01, 3: 3.303828e-01, 4: 2.345572e-01}


@pytest.mark.slow
@needs_data
def test_u235_1mev_gef_vs_stock(clean):
    """Engine (lanes, default gefran) vs stock: statistical; the sums over 11 peak masses carry ~0.6 % noise each side."""
    r = _run(clean, ["massdis y"])
    fy = r.fission_yields
    f = fy["yieldA0001.000.fis"]
    assert len(f["A"]) == 235 and abs(f["Tot"][1] - 2.0) < 1e-3
    assert {"nubarn.tot", "Pnun0001.000.fis", "nunA0001.000.fis", "nunZA0001.000.fis"} <= set(fy)
    for col, key in (("FF_yield", "FF"), ("FP_yield", "FP")):
        light, heavy = f[col][89:100].sum(), f[col][133:144].sum()
        assert abs(math.log(light / U235_PEAKS[key][0])) < 0.02, (col, light)
        assert abs(math.log(heavy / U235_PEAKS[key][1])) < 0.02, (col, heavy)
    assert abs(float(fy["nubarn.tot"]["nubar"][0]) / U235_NUBAR - 1.0) < 0.005
    p = fy["Pnun0001.000.fis"]
    pd = dict(zip(p["number"].tolist(), p["nu"]))
    for k, v in U235_PNU.items():
        assert abs(pd[k] / v - 1.0) < 0.03, (k, pd[k], v)
