"""NUBASE2020 parser: half-life units, spin-parity, decay modes, reference years."""

import math

import numpy as np
import pytest

from data.ingest.nubase import (
    HALF_LIFE_UNIT_S,
    NUBASE_FILE,
    SECONDS_PER_YEAR,
    load_nubase,
    parse_decay_modes,
    parse_half_life,
    parse_spin_parity,
)
from data.schema.nuclide import DECAY_MODES

needs_file = pytest.mark.skipif(not NUBASE_FILE.exists(), reason="raw/nubase2020 not downloaded")


@pytest.fixture(scope="module")
def nb():
    return load_nubase()


def gs(nb, Z, A, iso=0):
    r = nb[(nb["Z"] == Z) & (nb["A"] == A) & (nb["iso"] == iso)]
    assert len(r) == 1
    return r.iloc[0]


# ---- pure parsing helpers -------------------------------------------------------------


def test_units_cover_nubase_vocabulary():
    for u in "ys zs as fs ps ns us ms s m h d y ky My Gy Ty Py Ey Zy Yy".split():
        assert u in HALF_LIFE_UNIT_S
    assert HALF_LIFE_UNIT_S["y"] == SECONDS_PER_YEAR
    assert HALF_LIFE_UNIT_S["Gy"] == pytest.approx(1e9 * SECONDS_PER_YEAR)


def test_parse_half_life_number():
    r = parse_half_life("  4.463  ", "Gy", "0.003")
    assert r["half_life_s"] == pytest.approx(4.463e9 * SECONDS_PER_YEAR)
    assert r["log10_half_life_s"] == pytest.approx(math.log10(4.463e9 * SECONDS_PER_YEAR))
    assert r["log10_half_life_unc"] == pytest.approx(0.003 / 4.463 / math.log(10))
    assert not r["is_stable"] and not r["half_life_extrapolated"]


def test_parse_half_life_stable_and_flags():
    s = parse_half_life("stbl", "", ">2.6Zy")
    assert s["is_stable"] and math.isnan(s["half_life_s"]) and math.isnan(s["log10_half_life_s"])
    assert s["half_life_limit_kind"] == ">" and s["half_life_limit_s"] == pytest.approx(
        2.6e21 * SECONDS_PER_YEAR
    )
    p = parse_half_life("p-unst", "", "")
    assert p["is_particle_unstable"] and not p["is_stable"]
    e = parse_half_life("1#", "s", "")
    assert e["half_life_extrapolated"] and e["half_life_s"] == 1.0
    lim = parse_half_life(">100#", "ns", "")
    assert lim["half_life_limit_kind"] == ">" and lim["half_life_limit_s"] == pytest.approx(1e-7)
    assert math.isnan(lim["half_life_s"])
    with pytest.raises(ValueError):
        parse_half_life("1", "furlongs", "")


@pytest.mark.parametrize(
    "raw, spin, parity, tentative",
    [
        ("5/2+*", 2.5, 1, False),
        ("5/2+#", 2.5, 1, True),
        ("(1/2+)", 0.5, 1, True),
        ("0+", 0.0, 1, False),
        ("0+      T=2", 0.0, 1, False),
        ("3/2-    T=3/2", 1.5, -1, False),
        ("(2+,3-)", None, None, True),
        ("(1/2+,3/2+)", None, 1, True),
        ("(3/2,5/2)+", None, 1, True),
        ("9,10+", None, 1, True),
        ("7/2", 3.5, None, False),
        ("", None, None, False),
        ("am", None, None, False),
        ("2+  frg T=1", 2.0, 1, False),
    ],
)
def test_parse_spin_parity(raw, spin, parity, tentative):
    r = parse_spin_parity(raw)
    assert r["spin"] == spin
    assert r["parity"] == parity
    assert r["spin_parity_tentative"] == tentative
    assert r["spin_parity_raw"] == (raw.strip() or None)


def test_parse_spin_parity_isospin_and_measured():
    r = parse_spin_parity("0+      T=2")
    assert r["isospin"] == "2"
    assert parse_spin_parity("1/2+*")["spin_parity_measured"]
    assert not parse_spin_parity("1/2+")["spin_parity_measured"]


def test_parse_decay_modes_styles():
    m = parse_decay_modes("B-=100;B-n=2.3 5")
    assert [(x["mode"], x["qualifier"], x["branching_pct"]) for x in m] == [
        ("B-", "=", 100.0),
        ("B-n", "=", 2.3),
    ]
    assert m[1]["sigma_pct"] == pytest.approx(0.5)
    m = parse_decay_modes("IS=99.9855 78")
    assert m[0]["sigma_pct"] == pytest.approx(0.0078)
    m = parse_decay_modes("SF=5.44e-5 7")
    assert m[0]["branching_pct"] == pytest.approx(5.44e-5) and m[0]["sigma_pct"] == pytest.approx(
        7e-7
    )
    assert parse_decay_modes("IT ?")[0]["qualifier"] == "?"
    assert parse_decay_modes("IT=?")[0]["qualifier"] == "?"
    lt = parse_decay_modes("SF<4.7e-9")[0]
    assert lt["qualifier"] == "<" and lt["branching_pct"] == pytest.approx(4.7e-9)
    assert parse_decay_modes("A~100")[0]["qualifier"] == "~"
    ann = parse_decay_modes("IT=100[gs=0,m=100]")[0]
    assert ann["mode"] == "IT" and ann["branching_pct"] == 100.0
    sy = parse_decay_modes("B-=100#")[0]
    assert sy["extrapolated"] and sy["branching_pct"] == 100.0
    two = parse_decay_modes("B+p ? 2p ?")
    assert [x["mode"] for x in two] == ["B+p", "2p"]
    assert parse_decay_modes("") == []


# ---- the real file -------------------------------------------------------------------


@needs_file
def test_u238_half_life(nb):
    r = gs(nb, 92, 238)
    years = r["half_life_s"] / SECONDS_PER_YEAR
    assert years == pytest.approx(4.468e9, rel=0.01)  # NUBASE2020 quotes 4.463(3) Gy
    assert r["log10_half_life_s"] == pytest.approx(math.log10(4.463e9 * SECONDS_PER_YEAR), abs=1e-6)
    assert r["spin"] == 0 and r["parity"] == 1
    modes = {m["mode"]: m for m in r["decay_modes"]}
    assert modes["A"]["branching_pct"] == 100.0
    assert modes["SF"]["branching_pct"] == pytest.approx(5.44e-5)
    assert modes["IS"]["branching_pct"] == pytest.approx(99.2742)
    assert r["discovery_year"] == 1896 and r["ensdf_year"] == 2015


@needs_file
def test_co60_half_life(nb):
    r = gs(nb, 27, 60)
    assert r["half_life_s"] / SECONDS_PER_YEAR == pytest.approx(5.27, rel=0.001)
    assert r["spin"] == 5 and r["parity"] == 1 and r["spin_parity_measured"]
    assert r["decay_modes"][0]["mode"] == "B-" and r["decay_modes"][0]["branching_pct"] == 100
    m = gs(nb, 27, 60, iso=1)
    assert m["excitation_kev"] == pytest.approx(58.59) and m["half_life_s"] == pytest.approx(
        10.467 * 60
    )


@needs_file
def test_pb208_stable(nb):
    r = gs(nb, 82, 208)
    assert r["is_stable"] and math.isnan(r["log10_half_life_s"])
    assert r["half_life_limit_kind"] == ">"
    assert r["mass_excess_kev"] == pytest.approx(-21748.5, abs=0.1)


@needs_file
def test_u235_isomer(nb):
    m = gs(nb, 92, 235, iso=1)
    assert m["excitation_kev"] == pytest.approx(0.076737, abs=1e-6)
    assert m["half_life_s"] == pytest.approx(25.7 * 60)
    assert m["spin"] == 0.5 and m["parity"] == 1


@needs_file
def test_counts(nb):
    n_gs = int((nb["iso"] == 0).sum())
    assert 3400 <= n_gs <= 3700  # 3558 in NUBASE2020
    assert 5500 <= len(nb) <= 6200
    assert 240 <= int((nb["is_stable"] & (nb["iso"] == 0)).sum()) <= 300
    assert not nb.duplicated(["Z", "N", "iso"]).any()
    assert int(nb["non_existent"].sum()) < 30


@needs_file
def test_all_decay_modes_known(nb):
    modes = {m["mode"] for ms in nb["decay_modes"] for m in ms}
    assert modes <= DECAY_MODES, sorted(modes - DECAY_MODES)
    quals = {m["qualifier"] for ms in nb["decay_modes"] for m in ms}
    assert quals <= {"=", "<", ">", "~", "?"}
    pct = np.array([m["branching_pct"] for ms in nb["decay_modes"] for m in ms], dtype=float)
    assert np.nanmax(pct) <= 100.0 and np.nanmin(pct) >= 0.0


@needs_file
def test_years_and_half_life_coverage(nb):
    assert nb["ensdf_year"].dropna().between(1990, 2030).all()
    assert nb["discovery_year"].dropna().between(1800, 2030).all()
    has_t = nb["half_life_s"].notna()
    assert has_t.sum() > 4500
    assert (nb.loc[has_t, "half_life_s"] > 0).all()
    assert not (nb["is_stable"] & has_t).any()
