"""KWCOV B14 part 3: fission fragment evaporation (`massdis y; fymodel 4 | 5`, ffevap.f90) (docs/hf/COVERAGE_PLAN.md).

physics/hf/ffevap.py runs TALYS's per-fragment population calculation (`projectile 0`, excitation.f90, the multiple
emission cascade) through the engine's own C cascade on a k0 = 0 Cascade of the fragment; physics/hf/fisyield.py gains
the fymodel 4 / 5 branches of massdis.f90 and the post-neutron / isomer / per-ejectile nu files. The stock numbers
pinned here come from TALYS-2.25 n + U-235 at 1 MeV, deck `massdis y; fymodel 4` (talys.out's reaction summary of each
fragment run; ~/kwcov/stock/b14c/u235_31e7e7a528). scripts/kwcov/b14c_response.py does the full comparison.
"""
from __future__ import annotations

import math
import os

import numpy as np
import pytest

from physics.hf import ffevap as FE
from physics.hf import fisyield as Y
from physics.hf.input import defaults as D
from physics.hf.input import fitlib as FL

F = np.float32
TALYS_DIR = os.path.expanduser(os.environ.get("TALYS_DIR", "~/opt/talys-src"))
HAVE_DATA = os.path.isfile(os.path.join(TALYS_DIR, "structure", "fission", "ff", "gef", "U236", "U236_gef.E"))
needs_data = pytest.mark.skipif(not HAVE_DATA, reason="TALYS structure/fission/ff/gef/U236 not found")

ETOTAL = 7.54124212  # U-236* Etotal at 1 MeV incident (the ff*.ex header prints Einc + S + Q = 7.54552 instead)
# ff029073.ex rows (nex: E, P) as stock wrote them (fymodel 4, Cu-73: xsZApre 8.254766e-03 mb)
CU73_ROWS = {0: (0.0, 9.57232e-08), 100: (1.22957, 8.36642e-07), 454: (5.58226, 2.41359e-05),
             998: (12.27115, 8.58448e-09), 999: (12.28344, 8.33725e-09)}
CU73_XS = 8.254766e-03
# talys.out reaction summary per fragment: Einc, initial population, multiplicity (gamma, neutron), residuals
# {(Z, A): (total, {level: isomeric xs})}
STOCK = {
    "Cu73": (29, 73, 12.28344, 0.00825475, 3.94598, 0.0981082,
             {(29, 73): (0.0074449, {}), (29, 72): (0.000809859, {})}),
    "Ga75": (31, 75, 21.28955, 0.00916406, 3.61381, 0.234691,
             {(31, 75): (0.00703269, {}), (31, 74): (0.00211202, {0: 0.00155082, 2: 0.000561197}),
              (31, 73): (1.93533e-05, {}), (30, 74): (3.95458e-09, {})}),
    "Zn77": (30, 77, 16.54849, 0.228863, 2.68716, 0.390485,
             {(30, 77): (0.139789, {0: 0.0799512, 2: 0.0598375}), (30, 76): (0.0887807, {}),
              (30, 75): (0.000293435, {})}),
}
TALYS_DECK = ["fluxclose n", "npwindow n", "chancap n", "nnleak n", "exactfis n", "alphatemp 0", "sfexit n",
              "kevleak2 n", "heavymacs2 n", "ftglobal n", "ccexitnbnf n", "tfold n", "ctwcont n", "alphaentr 0"]
TALYS_ENV = {"INCOGNITA_GRIDTOP": "n", "INCOGNITA_SPECCLOSE": "0", "INCOGNITA_LOWEPOT": "0",
             "INCOGNITA_TARMASSFIX": "0", "INCOGNITA_ISOROTPASS": "0"}


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


# ------------------------------------------------------------------------------------------------ populations
def _pair(Z: int, A: int):
    files, et = Y.ff_files(92, 236, ETOTAL, ffmodel=1)
    for p in Y.ff_pairs(files, et, 236, ETOTAL)["pairs"]:
        if (p[0], p[1]) == (Z, A):
            return p[7], p[8]
        if (p[2], p[3]) == (Z, A):
            return p[9], p[10]
    raise KeyError((Z, A))


@needs_data
def test_fymodel4_population_rows_as_stock():
    """ffevap.f90:221-244: the Gaussian population file through its f10.5 / es12.5 formats, as stock wrote it."""
    eex, deex = _pair(29, 73)
    E, P = FE.fymodel4_rows(eex, deex, CU73_XS)
    assert E.shape == (1000,) and E.dtype == F
    for nex, (e, p) in CU73_ROWS.items():
        assert E[nex] == F(e), (nex, E[nex], e)
        assert abs(P[nex] / F(p) - 1.0) < 2e-5, (nex, P[nex], p)  # xsZApre itself carries ~1e-6
    pop = FE.population_of(E, P)
    assert pop["npopE"] == 1000 and float(pop["E"][1000]) == pytest.approx(12.28344, abs=1e-5)  # Einc = last row


def test_spindis_and_edistmax():
    sc = 5.0
    r = np.array([0.0, 2.5, 7.0], dtype=F)
    want = [(2 * x + 1) / (2 * sc) * math.exp(-((x + 0.5) ** 2) / (2 * sc)) for x in r]
    assert np.allclose(FE.spindis(sc, r), want, rtol=1e-6)
    pop = FE.population_of(np.array([0.0, 1.0, 2.0, 3.0], F), np.array([1.0, 3.0, 2.0, 2.0], F))
    assert FE.edistmax_of(pop) == 1.0  # the last energy where P rises (P(0) = 0 counts: E = 0 first, then 1)
    flat = FE.population_of(np.array([1.0, 2.0], F), np.array([0.0, 0.0], F))
    assert FE.edistmax_of(flat) == 10.0


def _grid():
    """A small (0, 0) grid: 3 discrete levels (0, 0.5, 1.2 MeV) and 10 continuum bins of 0.5 MeV up to 6.2 MeV."""
    ex = np.array([0.0, 0.5, 1.2] + [1.45 + 0.5 * k for k in range(10)])
    dex = np.array([0.0, 0.0, 0.0] + [0.5] * 10)
    maxj = np.array([40, 40, 40] + [9] * 10)
    jdis = np.array([0.0, 2.0, 4.0] + [0.0] * 10)
    parlev = np.array([1, 1, -1] + [0] * 10)
    return ex, dex, maxj, jdis, parlev


def test_excitation_spinless_conserves_and_places():
    """excitation.f90: histogram overlap onto the bins, discrete levels at their own (J, parity), the rest Wigner x 1/2
    per parity; the population is renormalised to the input sum."""
    ex, dex, maxj, jdis, parlev = _grid()
    E = np.linspace(0.0, 6.0, 61).astype(F)
    P = np.exp(-((E - 3.0) ** 2) / 2.0).astype(F)
    pop = FE.population_of(E, P)
    r = FE.excitation(pop, ex, dex, maxj, jdis, parlev, 2, 12, 74, 4.0)
    xin = float(np.add.accumulate(P.astype(F), dtype=F)[-1])
    assert r["xsinitpop"] == pytest.approx(xin, rel=2e-6)
    assert np.allclose(r["xspop"].sum((1, 2)), r["xspopex"], rtol=2e-6)
    # level 1 (J = 2, +) and level 2 (J = 4, -) only in their own cell
    for nex, J, ip in ((1, 2, 1), (2, 4, 0)):
        cell = r["xspop"][nex].copy()
        assert cell[J, ip] > 0
        cell[J, ip] = 0
        assert not cell.any()
    # continuum: equal parities, Wigner shape in J (A even: integer spins)
    c = r["xspop"][7]
    assert np.allclose(c[:, 0], c[:, 1])
    w = FE.spindis(4.0, np.arange(10, dtype=F))
    assert np.allclose(c[:10, 1] / c[:10, 1].sum(), w / w.sum(), rtol=1e-5) and not c[10:].any()


def test_excitation_with_spins_and_read(tmp_path):
    """npopJ > 0 (fymodel 5 / ffspin files): read_energies halves a one-parity table into both parities; the spin
    table is overlapped as given (discrete levels still take the bin total at their own J, parity)."""
    ex, dex, maxj, jdis, parlev = _grid()
    rows = []
    for e in (1.0, 2.0, 3.0, 4.0, 5.0, 6.0):
        rows.append(f"{e:10.5f}" + "".join(f"{v:12.5E}" for v in [0.1 * e, 0.2, 0.3, 0.0]))
    fn = tmp_path / "ff030074.ex"
    fn.write_text("     6   4   1\n" + "\n".join(rows) + "\n")
    pop = FE.read_population(str(fn))
    assert pop["npopJ"] == 4 and np.allclose(pop["PJ"][3, :4, 0], [0.15, 0.1, 0.15, 0.0])
    assert np.array_equal(pop["PJ"][:, :, 0], pop["PJ"][:, :, 1])
    r = FE.excitation(pop, ex, dex, maxj, jdis, parlev, 2, 12, 74, None)
    tot = float(sum(0.1 * e + 0.5 for e in (1.0, 2.0, 3.0, 4.0, 5.0, 6.0)))
    assert r["xsinitpop"] == pytest.approx(tot, rel=1e-5)
    c = r["xspop"][5]  # continuum bin 2.45 MeV: J = 0..2 only, as the table
    assert c[3:].sum() == 0 and np.allclose(c[:, 0], c[:, 1]) and c[1, 1] > 0
    fn.write_text("     6   4   3\n")
    with pytest.raises(ValueError, match="parities"):
        FE.read_population(str(fn))


def test_fymodel5_reads_run_directory(tmp_path):
    """massdis.f90:709-742: every ff<ZZZ><AAA>.ex of the run directory is a fragment, its cross section the sum of all
    its populations."""
    (tmp_path / "ff036092.ex").write_text("  2  2  2\n 1.0 1.0 2.0\n 2.0 3.0 4.0\n 1.0 0.5 0.5\n 2.0 0.0 1.0\n")
    (tmp_path / "ff056144.ex").write_text("  1  1  1\n 3.0 7.0\n")
    xa = np.zeros(415, F)
    xz = np.zeros((125, 291), F)
    got = Y._fymodel5(str(tmp_path), 92, 236, xa, xz)
    assert set(got) == {(36, 56), (56, 88)}
    assert xz[36, 56] == F(12.0) and xz[56, 88] == F(7.0) and xa[92] == F(12.0) and xa[144] == F(7.0)
    (tmp_path / "ff036092.ex").write_text("  2  0  1\n")
    with pytest.raises(ValueError, match="spins"):
        Y._fymodel5(str(tmp_path), 92, 236, xa, xz)


def test_fymodel4_pairs_to_fragments():
    xa = np.zeros(415, F)
    xz = np.zeros((125, 291), F)
    pairs = [(36, 92, 56, 144, F(0.01), F(170.0), F(20.0), F(8.0), F(1.0), F(12.0), F(2.0)),
             (38, 96, 54, 140, F(0.02), F(171.0), F(21.0), F(9.0), F(1.5), F(11.0), F(2.5))]
    ff = Y._fymodel4(pairs, F(1000.0), xa, xz)
    assert xz[36, 56] == F(10.0) and xz[54, 86] == F(20.0) and xa[92] == F(10.0) and xa[140] == F(20.0)
    assert ff[(38, 58)] == (F(9.0), F(1.5), F(171.0)) and ff[(56, 88)] == (F(12.0), F(2.0), F(170.0))


# ------------------------------------------------------------------------------------------------ settings, files
def test_settings_fymodel_3_4_5(clean):
    s = Y.settings(D.default_options(92, 235, "n", overrides={"massdis": "y", "fymodel": "4"}))
    assert s["fymodel"] == 4 and s["ffmodel"] == 1 and s["yieldfile"] == "" and s["parskip"] == [False] * 7
    clean.setenv("INCOGNITA_FFDIR", "/some/dir")
    assert Y.settings(D.default_options(92, 235, "n", overrides={"massdis": "y", "fymodel": "5"}))["ffdir"] == "/some/dir"
    with pytest.raises(NotImplementedError, match="fymodel 3"):
        Y.settings(D.default_options(92, 235, "n", overrides={"massdis": "y", "fymodel": "3"}))
    with pytest.raises(NotImplementedError, match="pfnsmodel 2"):
        Y.settings(D.default_options(92, 235, "n", overrides={"massdis": "y", "fymodel": "4", "outspectra": "y"}))
    with pytest.raises(NotImplementedError, match="channels y"):
        Y.settings(D.default_options(92, 235, "n", overrides={"massdis": "y", "fymodel": "5", "channels": "y"}))
    # ffspin acts only with fymodel 3 (massdis.f90:554): inert with 4 / 5, as stock
    assert Y.settings(D.default_options(92, 235, "n", overrides={"massdis": "y", "fymodel": "4", "ffspin": "y"}))


def test_build_ff_files():
    """fymodel >= 3 files: isomer rows and i0N files (massdisout.f90), nubar<x> / Pnu<x> / nu<x>A / nu<x>ZA per ejectile
    with nubar != 0, EavZA / EavA (nudisout.f90)."""
    At, Zt = 235, 92
    xz = np.zeros((125, 291), F)
    xz[30, 47] = F(1.0)
    post = np.zeros_like(xz)
    post[30, 47] = F(0.8)
    xf = np.zeros((125, 291, 2), F)
    xf[30, 47] = (F(0.6), F(0.2))
    nub = np.zeros(7, F)
    nub[0], nub[1] = F(7.5), F(2.4)
    nua = np.zeros((7, 415), F)
    nua[1, 77] = F(0.39)
    r = {"E": 1.0, "fpeps": 1e-6, "xsZApre": xz, "xsZApost": post, "yieldZApre": xz * F(0.01),
         "yieldZApost": post * F(0.01), "xsApre": np.zeros(415, F), "xsApost": np.zeros(415, F),
         "yieldApre": np.zeros(415, F), "yieldApost": np.zeros(415, F), "tot": np.zeros(4, F), "xsfpex": xf,
         "yieldfpex": xf * F(0.01), "fpratio": np.where(xf > 0, xf / F(0.8), F(0)).astype(F), "nubar": nub,
         "nuA": nua, "nuZA": {(1, 30, 47): F(0.004)}, "eavZA": {}, "eavA": np.zeros((7, 415), F),
         "Pdisnu": np.zeros((7, 51), F), "Pdisnuav": np.zeros(7, F),
         "fragments": {(30, 77): {"xsinitpop": 0.23, "mult": np.array([2.7, 0.39, 0, 0, 0, 0, 0]), "Einc": 16.5}}}
    out = Y.build([r], {"Ztarget": Zt, "Atarget": At, "Zinit": 92, "Ainit": 236, "fymodel": 4})
    za = out["yieldZA0001.000.fis"]
    assert list(za["isomer"]) == [-1, 0, 1] and za["Isomeric_ratio"][1] == pytest.approx(0.75)
    assert math.isnan(za["FF_yield"][1]) and math.isnan(za["Isomeric_ratio"][0])
    assert out["fp030077.i01"]["FP_xs"][0] == pytest.approx(0.2) and out["rp030077.i01"]["FP_xs"][0] == pytest.approx(0.8)
    assert set(k for k in out if k.startswith("nubar")) == {"nubarg.tot", "nubarn.tot"}
    assert list(out["Pnun0001.000.fis"]["number"]) == [0, 1, 2, 3, 4] and not out["Pnun0001.000.fis"]["nu"].any()
    assert out["nunZA0001.000.fis"]["A"].tolist() == [77] and out["nunA0001.000.fis"]["nu"][76] == F(0.39)
    assert out["EavZA0001.000.fis"]["Z"].size == 0 and out["EavA0001.000.fis"]["A"].size == At
    assert out["ff_fragments0001.000"]["mult_n"][0] == 0.39


def test_spincut_parts_default_unchanged():
    """The ipop = 1 maxJ (fragment runs) is opt-in: a Cascade without `ffruns_rspincut` keeps the cached default."""
    from physics.hf.emission import feeding

    assert feeding.Cascade.__dict__.get("ffruns_rspincut") is None


# ------------------------------------------------------------------------------------------------ fragment runs
@needs_data
def test_fragment_runs_vs_stock(clean):
    """Population runs of three U-236 fragments vs stock's talys.out (TALYS mode): initial population, neutron
    multiplicity, residual production and the isomer split (Ga-74m, Zn-77m)."""
    for k, v in TALYS_ENV.items():
        clean.setenv(k, v)
    clean.setenv("INCOGNITA_TALYS_FIT", "lines")
    clean.setenv("INCOGNITA_TALYS_FIT_LINES", ";".join(["massdis y", "fymodel 4"] + TALYS_DECK))
    for name, (Z, A, einc, initpop, mg, mn, res) in STOCK.items():
        eex, deex = _pair(Z, A)
        xs = initpop if name != "Cu73" else CU73_XS
        E, P = FE.fymodel4_rows(eex, deex, xs)
        with FE.fragment_env():
            r = FE.run_fragment(Z, A, FE.population_of(E, P))
        assert r["Einc"] == pytest.approx(einc, abs=1e-5)
        assert r["xsinitpop"] == pytest.approx(initpop, rel=2e-5), name
        assert r["mult"][1] == pytest.approx(mn, rel=1e-3), (name, r["mult"])
        assert r["mult"][0] == pytest.approx(mg, rel=6e-3), (name, r["mult"])  # see COVERAGE_PLAN B14c (gamma)
        for (z, a), (tot, iso) in res.items():
            key = (Z - z, (A - Z) - (a - z))
            assert r["xspopnuc"][key] == pytest.approx(tot, rel=2e-3), (name, z, a)
            xe, tau = r["levels"][key]
            for lev, x in iso.items():
                assert xe[lev] == pytest.approx(x, rel=2e-3), (name, z, a, lev)
                assert lev == 0 or tau[lev] > 0
