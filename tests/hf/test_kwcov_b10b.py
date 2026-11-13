"""KWCOV B10b: energies below eninclow, natural targets, resonance range, integral data (docs/hf/COVERAGE_PLAN.md B10b).

thermal.f90 / thermalxs.f90 (physics/hf/thermal.py, Results.thermal, output only), mass 0 / abundance (natural.py,
run_deck), integral y (integral.py, Results.integral), resonance y refused, the deck-change cache drop (fitlib). The
engine was compared with stock TALYS-2.25 by scripts/kwcov/b10b_response.py (numbers in the plan); the tests pin the
transcriptions against stock numbers, the parsing and refusals, defaults unchanged, and short engine runs.
"""
from __future__ import annotations

import math
import os

import numpy as np
import pytest

from tests._data import need_talys

from physics.hf import chartrun
from physics.hf import integral as I
from physics.hf import natural as N
from physics.hf import thermal as T
from physics.hf.input import fitlib as F

LOW = (2.53e-8, 1.0e-7, 5.0e-7, 1.0e-3, 0.1, 1.0)
DECK = "projectile n\nelement {el}\nmass {a}\nenergy energies\n"


@pytest.fixture
def clean(monkeypatch):
    for k in [k for k in os.environ if k.startswith("INCOGNITA_")]:
        monkeypatch.delenv(k, raising=False)
    F.deactivate(); F._cards.cache_clear(); chartrun.drop_target_caches()
    yield monkeypatch
    for k in [k for k in os.environ if k.startswith("INCOGNITA_")]:
        monkeypatch.delenv(k, raising=False)
    F.deactivate(); F._cards.cache_clear(); chartrun.drop_target_caches()


def _deck(tmp_path, el, a, energies, extra=""):
    (tmp_path / "energies").write_text("".join(f"{e}\n" for e in energies))
    p = tmp_path / "talys.inp"
    p.write_text(DECK.format(el=el, a=a) + extra)
    return p


# ------------------------------------------------------------------------------------------------ thermalxs / grid
def test_thermal_xs_table_overwrites_deck():
    # Fe-56: the table's isoR = -1 row overwrites a deck value (stock: `xscaptherm 5000` changes no number)
    assert T.thermal_xs(26, 56, {"cap": 5000.0})["cap"][-1] == 2590.0
    # Fe-61: no table row -> the deck value; without one, Kopecky (called only then)
    assert T.thermal_xs(26, 61, {"cap": 5000.0}, lambda: 1 / 0)["cap"][-1] == 5000.0
    assert T.thermal_xs(26, 61, {}, lambda: 123.0)["cap"][-1] == 123.0
    # Fe-55 has capture only: the deck's (n,p) / (n,a) act
    th = T.thermal_xs(26, 55, {"p": 2000.0, "alpha": 500.0})
    assert (th["cap"][-1], th["p"][-1], th["alpha"][-1]) == (13000.0, 2000.0, 500.0)
    # Ag-109: total row + ground / isomer rows (the isomer branch below E1v)
    ag = T.thermal_xs(47, 109)
    assert (ag["cap"][-1], ag["cap"][0], ag["cap"][1]) == (76900.0, 86300.0, 3950.0)


def test_low_grid():
    g = T.low_grid(LOW, 1.0e-6)  # grid.f90 inserts E1v = 0.2 eninclow and eninclow
    assert g["Ninclow"] == 4 and np.allclose(g["eninc"][:5], (2.53e-8, 1e-7, 2e-7, 5e-7, 1e-6), rtol=1e-6)
    assert g["eref"] == pytest.approx(1e-6, rel=1e-6) and g["E1v"] == pytest.approx(2e-7, rel=1e-6)
    g = T.low_grid(LOW, 1.0e-4)
    assert g["Ninclow"] == 4 and g["eref"] == pytest.approx(1e-4, rel=1e-6)
    assert T.low_grid((1.0, 5.0), 1.0e-6)["Ninclow"] == 0


def test_fill_reproduces_stock_rows():
    """thermal.fill on stock Fe-56's own 1 eV row gives stock's rows below 1 eV (float32 noise)."""
    ref = {"channels_mb/xs000000": 148099.5, "residual_production_mb/rp026057": 148099.5,
           "channels_mb/xs000001": 1e-7, "totals_mb/elastic": 2399128.0, "channels_mb/xs100000": 0.0}
    g = T.low_grid(LOW, 1.0e-6)
    out = T.fill(ref, g, T.thermal_xs(26, 56), 26, 56)
    stock = {"channels_mb/xs000000": (2590.0, 1302.747, 921.1812, 16610.85),
             "totals_mb/total": (2401718.0, 2400431.0, 2400050.0, 2415739.0)}
    for k, v in stock.items():
        assert np.allclose(out[k], v, rtol=5e-6), k
    assert out["totals_mb/elastic"] == [2399128.0] * 4 and out["channels_mb/xs000001"] == [0.0] * 4


# ------------------------------------------------------------------------------------------------ deck parsing
def test_b10b_keywords_parse_and_refuse(clean):
    from physics.hf import warmrun

    clean.setenv(F.ENV_LINES, "xsptherm 2000;xsalphatherm 7;resonance n;group y;reslib tendl.2023;tres 300")
    cas = warmrun.new_cascade(26, 55, (1e-6, 1.0))
    assert float(cas.params.at("xsptherm", -1)) == 2000.0  # was dropped ("unsupported index form")
    assert T.therm_of_run(cas)["alpha"][-1] == 7.0
    for line, exc in (("resonance y", NotImplementedError), ("tres -5", ValueError), ("elow 2", ValueError),
                      ("xscaptherm 1e11", ValueError), ("group x", ValueError)):
        clean.setenv(F.ENV_LINES, line)
        with pytest.raises(exc):
            F.cards(26, 56)


def test_resonance_refused_by_run_deck(clean, tmp_path):
    from physics.hf.input.deck import run_deck

    with pytest.raises(NotImplementedError, match="PREPRO"):
        run_deck(_deck(tmp_path, "fe", 56, (1.0,), "resonance y\n"))
    with pytest.raises(NotImplementedError, match="mass 0 with integral"):
        run_deck(_deck(tmp_path, "fe", 0, (1.0,), "integral y\n"))


# ------------------------------------------------------------------------------------------------ engine runs
def test_fe56_thermal_rows_vs_stock(clean, tmp_path):
    """Stock TALYS-2.25 n + Fe-56 at 2.53e-8 1e-7 5e-7 1e-3 0.1 1 MeV: rows below 1 eV from thermal.f90. The engine's
    own arrays at those energies are untouched (Hauser-Feshbach there); Results.thermal carries TALYS's rows."""
    from physics.hf.input.deck import run_deck

    r = run_deck(_deck(tmp_path, "fe", 56, LOW))
    th = r.thermal
    assert np.allclose(th["E"], (2.53e-8, 1e-7, 2e-7, 5e-7), rtol=1e-6)
    assert np.allclose(th["channels_mb/xs000000"], (2590.0, 1302.747, 921.1812, 16610.85), rtol=1e-5)
    assert np.allclose(th["residual_production_mb/rp026057"], th["channels_mb/xs000000"])
    # elastic: eref's (the engine's LOWEPOT elastic in default mode; stock 2399128 mb, the HF compound elastic)
    assert len(set(th["totals_mb/elastic"].tolist())) == 1
    assert np.allclose(th["totals_mb/total"], th["totals_mb/elastic"] + th["totals_mb/nonelastic"])
    # output only: the engine's 2.53e-8 MeV capture is its own Hauser-Feshbach value, not the thermal one
    assert float(r.channels_mb["xs000000"][0]) > 1e6


def test_fe55_xsptherm_thermal_point(clean, tmp_path):
    """Below E1v the (n,p) row is xsptherm sqrt(Etherm/E) whatever the engine's 1 eV (n,p) (stock: 2000 mb)."""
    from physics.hf.input.deck import run_deck

    r = run_deck(_deck(tmp_path, "fe", 55, (2.53e-8, 1.0e-6, 1.0), "xsptherm 2000\n"))
    th = r.thermal
    assert th["E"].shape == (2,)
    assert th["channels_mb/xs010000"][0] == pytest.approx(2000.0, rel=1e-5)  # xs010000 / rp025055 at eref
    assert th["xsptherm"][0] == 2000.0 and th["xscaptherm"][0] == 13000.0


def test_new_deck_drops_stale_caches(clean, tmp_path):
    """B10's observation: a second run_deck with other deck lines reused the first deck's Options (cached by
    (Z, A) in dens_reference._structure_of). Fe-56 1 MeV capture: default 3.045, `ldmodel 2` 2.176 mb."""
    from physics.hf.input.deck import run_deck

    a = run_deck(_deck(tmp_path, "fe", 56, (1.0,)))
    b = run_deck(_deck(tmp_path, "fe", 56, (1.0,), "ldmodel 2\n"))
    c = run_deck(_deck(tmp_path, "fe", 56, (1.0,)))
    ca, cb, cc = (float(x.channels_mb["xs000000"][0]) for x in (a, b, c))
    assert abs(ca - 3.0452) < 1e-3 and abs(cb - 2.1757) < 1e-3 and ca == cc
    assert a.thermal == {} and a.natural == {} and a.integral == {}  # defaults: no B10b output


def test_natural_iron(clean, tmp_path):
    """mass 0: structure/abundance/Fe.abun (54, 56, 57, 58), one run each, weighted sums. Stock natural Fe 1 MeV:
    capture 3.576751, total 3784.427 mb; stock's natural files are its isotope runs' weighted sums to 4e-7."""
    from physics.hf.input.deck import run_deck

    ab = N.abundances(26)
    assert list(ab) == [54, 56, 57, 58] and sum(ab.values()) == pytest.approx(1.0)
    assert ab[56] == pytest.approx(0.91754, rel=1e-9)
    r = run_deck(_deck(tmp_path, "fe", 0, (1.0,)))
    iso = r.natural["isotopes"]
    for fam in N.SUMMED:
        for k, v in getattr(r, fam).items():
            s = sum(ab[a] * float(getattr(iso[a], fam).get(k, np.zeros(1))[0]) for a in iso)
            assert float(v[0]) == pytest.approx(s, rel=1e-12, abs=1e-300), (fam, k)
    assert "residual_production_mb" in N.SUMMED and "rp026055" in r.residual_production_mb  # Fe-54 + n only
    assert abs(math.log(float(r.channels_mb["xs000000"][0]) / 3.576751)) < 0.05
    assert abs(math.log(float(r.totals_mb["total"][0]) / 3784.427)) < 0.01
    # abundance <file>: one isotope at 100 %
    (tmp_path / "my.abun").write_text("  26  56 100.000000\n")
    r1 = run_deck(_deck(tmp_path, "fe", 0, (1.0,), "abundance my.abun\n"))
    assert list(r1.natural["abundance"]) == [56]
    assert float(r1.channels_mb["xs000000"][0]) == float(iso[56].channels_mb["xs000000"][0])


# ------------------------------------------------------------------------------------------------ integral
def test_integral_fold_and_data():
    # xs linear on (0,0), (1, 10), (2, 30); groups at 0.5 (w 1), 1.5 (w 3), 2.5 (w 5, above the last row: left out)
    assert I.effective_b([1.0, 2.0], [10.0, 30.0], [0.5, 1.5, 2.5], [1.0, 3.0, 5.0]) == pytest.approx(
        1e-3 * (5.0 * 1 + 20.0 * 3) / 9.0)
    s = I.sacs_entries(26, 56)
    assert len(s) == 5 and s[0] == dict(reac="n,p", iso="t", flux="JAEA-FNS-pos3", exp_b=8.69e-2)
    e, phi = I.spectrum("Cf252")
    assert e[0] == pytest.approx(0.5 * (2.0e7 + 1.91e7) * 1e-6) and phi[0] == pytest.approx(2.1455e-6)
    assert I.parse_deck(["integral y"]) == {"triples": []} and I.parse_deck(["integral n"]) is None
    assert I.parse_deck(["integral xs000000.tot Cf252 0.01"]) == {"triples": [("xs000000.tot", "Cf252", 0.01)]}


def test_integral_user_triple_is_talys_bug(clean):
    """TALYS-2.25: a deck triple looks for the file '.tot' (stock: 'cross section file .tot does not exist')."""
    need_talys()  # needs the TALYS structure database (the .tot lookup reads it)
    import torch

    from physics.hf.results import Results

    r = Results(e_inc_mev=torch.tensor([1.0, 14.0], dtype=torch.float64),
                channels_mb={"xs000000": torch.tensor([3.0, 1.0], dtype=torch.float64)})
    with pytest.warns(UserWarning, match=r"\.tot does not exist"):
        t = I.integral_table(r, 26, 56, [("xs000000.tot", "Cf252", 0.01)])
    assert t["integral.dat"]["file"] == []
    with pytest.warns(UserWarning):  # Co059.sacs: (n,g) row only (no n,2n / n,a channels in this Results)
        t = I.integral_table(r, 27, 59)
    assert t["integral.dat"]["file"] == ["xs000000.tot"] and t["integral.dat"]["spectrum"] == ["FNG-eurofer"]
