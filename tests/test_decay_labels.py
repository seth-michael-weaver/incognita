"""Decay-data labels: NUBASE2016 layout, ENSDF branchings, and the measured-only rule."""

import math

import pytest

from data.ingest import decay as D
from data.ingest.ensdf import ENSDF_ZIP
from data.ingest.nubase import NUBASE2016_FILE, NUBASE_FILE, load_nubase

needs_nb16 = pytest.mark.skipif(not NUBASE2016_FILE.exists(), reason="raw/nubase2016 missing")
needs_nb20 = pytest.mark.skipif(not NUBASE_FILE.exists(), reason="raw/nubase2020 missing")


def test_ensdf_branchings():
    m = D.parse_ensdf_branchings("%B-=100 $ %B-N=13.3 62 (2022Ki23)")
    assert [(x["mode"], x["qualifier"], x["branching_pct"]) for x in m] == [
        ("B-", "=", 100.0), ("B-n", "=", 13.3)]
    m = D.parse_ensdf_branchings("%EC+%B+=100$%A<0.5$%SF=?")
    assert m[0]["mode"] == "B+" and m[0]["branching_pct"] == 100.0
    assert m[1]["mode"] == "A" and m[1]["qualifier"] == "<"
    assert m[2]["qualifier"] == "?"


def test_partials_measured_only():
    out = {}
    D._partials(0.0, [{"mode": "B-", "qualifier": "=", "branching_pct": 50.0, "extrapolated": False},
                      {"mode": "A", "qualifier": "=", "branching_pct": 50.0, "extrapolated": True},
                      {"mode": "B-n", "qualifier": "=", "branching_pct": 3.0, "extrapolated": False}], out)
    assert out["log_t_bm"] == pytest.approx(math.log10(2.0))
    assert math.isnan(out["log_t_a"])          # systematics branching is not a label
    assert out["pn"] == 3.0


@needs_nb16
def test_nubase2016_layout():
    nb = load_nubase(NUBASE2016_FILE)
    assert nb.attrs["source_version"] == "NUBASE2016"
    r = nb[(nb.Z == 56) & (nb.A == 149) & (nb.iso == 0)].iloc[0]
    assert r.half_life_s == pytest.approx(0.348)
    assert {m["mode"]: m["branching_pct"] for m in r.decay_modes}["B-n"] == 0.43
    na = nb[(nb.Z == 11) & (nb.A == 24) & (nb.iso == 1)].iloc[0]
    assert na.excitation_kev == pytest.approx(472.2074) and na.excitation_unc_kev == pytest.approx(0.0008)


@needs_nb20
def test_systematics_values_are_not_labels():
    lab = D.labels_from_nubase(2020).set_index(["Z", "N"])
    assert math.isnan(lab.loc[(36, 64), "pn"])            # 100Kr: 'B-n ?'
    assert lab.loc[(50, 84), "pn"] == 17.0                 # 134Sn: 'B-n=17 13'
    assert lab["log_t"].notna().sum() > 2500


@needs_nb16
@needs_nb20
def test_split_a_tests_are_new():
    s = D.time_split("A_2016_2020")
    old = s["train"].set_index(["Z", "N"])
    for t in D.TARGETS:
        rows = s["test_new"][s["test_new"][t].notna()]
        assert len(rows) > 0
        assert old.reindex(list(zip(rows.Z, rows.N)))[t].isna().all()


@pytest.mark.skipif(not ENSDF_ZIP.exists(), reason="raw/ensdf missing")
@needs_nb20
def test_split_b_uses_recent_ensdf():
    s = D.time_split("B_2020_2026")
    assert len(s["test_new"]) > 10
