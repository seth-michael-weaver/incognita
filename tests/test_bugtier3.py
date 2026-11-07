"""Bug hunt round 3, scoring: library v0.2.2 tiers, bands and MACS flags, and how the site shows them (2026-11-07).

Each test pins one finding of BUGTIER3 (docs/release/amendments/BUGTIER3.md).
- Site display bugs (fixed): the tier the Data explorer shows and the "How far to trust this" panel.
- Library findings that would change a shipped value or a published number are not fixed here. Their tests are marked
  xfail(strict=True) and name the amendment item, so they turn into failures (and must be unmarked) once it is applied.
"""
from __future__ import annotations

import csv
import json
import math
import re
import shutil
import subprocess
from functools import lru_cache
from pathlib import Path

import numpy as np
import pytest

pq = pytest.importorskip("pyarrow.parquet")

REPO = Path(__file__).resolve().parents[1]
LIB = REPO / "library" / "v0.2.2"
SITE = REPO / "docs" / "walkthrough"
DATA_JS = (SITE / "js" / "data.js").read_text(encoding="utf-8")
LANGS = ["ar", "da", "de", "es", "fr", "hi", "it", "ja", "ko", "nl", "pt", "ru", "zh"]


@lru_cache(None)
def cap():
    return {r["nuclide_id"]: r for r in pq.read_table(LIB / "capture_v022.parquet").to_pylist()}


@lru_cache(None)
def below():
    return {r["nuclide_id"]: r for r in pq.read_table(LIB / "below1keV_engine_v022.parquet").to_pylist()}


@lru_cache(None)
def index_rows():
    idx = json.loads((SITE / "data" / "index.json").read_text())
    return [dict(zip(idx["cols"], r)) for r in idx["rows"]]


def nfile(Z, A):
    return json.loads((SITE / "data" / "n" / str(Z) / f"{A}.json").read_text())


def _node(code):
    node = shutil.which("node")
    if not node:
        pytest.skip("needs node")
    return json.loads(subprocess.run([node, "-e", code], capture_output=True, text=True, check=True).stdout)


def _line(prefix):
    return next(l for l in DATA_JS.splitlines() if l.startswith(prefix))


def _en(key):
    """The English default of a ui key in data.js: T("key", "text")."""
    return re.search(rf'T\("{key}", "((?:[^"\\]|\\.)*)"\)', DATA_JS).group(1)


def _lang(lang, key):
    return re.search(rf'^\s*{key}: "((?:[^"\\]|\\.)*)",?$', (SITE / "js" / "i18n" / f"{lang}-data.js").read_text(encoding="utf-8"), re.M).group(1)


# ------------------------------------------------------------------------------------------------ site: shown tier
def test_shown_tier_marks_interpolated_nuclides_with_curated_data_as_measured():
    """33 INTERPOLATED nuclides (Z 26-83) have curated capture cells the curation kept, yet the page called them
    "Interpolated. Not measured" and drew the measurements beside that text. EXTRAPOLATED ones already got tier 5."""
    out = _node(_line("  const shownTier = ") + "\nconsole.log(JSON.stringify(["
                "shownTier(30, 2, 3, 1), shownTier(30, 2, 0, 0), shownTier(30, 2, 2, 0), shownTier(30, 3, 1, 1),"
                "shownTier(30, 0, 9, 9), shownTier(30, 1, 5, 5), shownTier(20, 3, 1, 1), shownTier(20, 3, 0, 0)]));")
    assert out == [5, 2, 2, 5, 0, 1, 6, 4]


def test_interpolated_with_curated_data_exist_and_are_shown_as_measured():
    rows = [r for r in index_rows() if r["Z"] >= 26 and r["tier"] == 2 and r["n_use"] > 0]
    assert len(rows) == 33  # the case above is real (capture set v2)
    assert any((r["Z"], r["A"]) == (27, 57) for r in rows)  # Co-57


def test_tier5_text_does_not_say_extrapolated_only():
    """Tier 5 now also holds INTERPOLATED nuclides: its text must not say the library lists them as extrapolated."""
    en = _en("dx_tr_t5")
    assert "interpolated or extrapolated" in en
    for lang in LANGS:
        assert _lang(lang, "dx_tr_t5") != "", lang


# ------------------------------------------------------------------------------------------------ site: trust panel
def _band(tier):
    lines = DATA_JS.splitlines()
    i = next(k for k, l in enumerate(lines) if l.lstrip().startswith('const band = k === "cap"'))
    j = next(k for k in range(i, len(lines)) if 'T("dx_tr_b_none"' in lines[k])
    code = "const T = (k, en) => k;\n" + "\n".join(lines[i:j + 1])
    return _node(f"const k = 'cap', d = {{ u68: [0.1], tier: {tier} }};\n{code}\nconsole.log(JSON.stringify(band));")


def test_capture_band_claim_only_for_measured_tier():
    """The panel said "bands cover as stated" for ANCHORED nuclides too (tier 1); the coverage check behind that claim
    scored measured nuclei only (library/v0.2/BUILD.md: the ANCHORED row has 32 points, 'too few to read')."""
    assert _band(0) == "dx_tr_b_ok"
    assert _band(1) == "dx_tr_b_unm"
    assert _band(2) == "dx_tr_b_unm"
    assert _band(3) == "dx_tr_b_unm"


def test_anchored_text_does_not_deny_curated_measurements():
    """14 of the 21 ANCHORED nuclides have kept curated capture cross-section cells (3 of them at keV energies: Zn-70,
    Ge-76, Te-120). The panel said "No measured cross sections" above those points."""
    n = 0
    for r in cap().values():
        if r["tier"] == "ANCHORED":
            m = nfile(r["Z"], r["A"]).get("meas", {"cap": []})
            n += any(p[5] != "x" for p in m["cap"])
    assert n == 14
    assert not _en("dx_tr_t1").startswith("Anchored. No measured cross sections")
    for lang in LANGS:
        assert "v0.1" in _lang(lang, "dx_tr_t1"), lang


def _l1_to_measured():
    meas = [(r["Z"], r["A"] - r["Z"]) for r in cap().values() if r["tier"] == "MEASURED"]
    out = {}
    for i, r in cap().items():
        z, n = r["Z"], r["A"] - r["Z"]
        out[i] = min(abs(a - z) + abs(b - n) for a, b in meas if (a, b) != (z, n))
    return out


def test_extrapolated_text_does_not_say_far_from_measured():
    """chart_distance is |dZ| + |dN| to the nearest MEASURED nucleus. 205 EXTRAPOLATED nuclides in Z 26-83 with structure
    data lie within 2 of one (Co-60 is next to Co-59), so "not close to measured nuclei" was wrong for them."""
    d = _l1_to_measured()
    for r in cap().values():
        if r["tier"] in ("INTERPOLATED", "ANCHORED"):
            assert d[r["nuclide_id"]] == r["chart_distance"], r["nuclide_id"]
    near = [i for i, r in cap().items() if r["tier"] == "EXTRAPOLATED" and r["structure_data"]
            and r["in_validated_range"] and d[i] <= 2]
    assert len(near) == 205 and "Z027N033M0" in near
    assert "not close to measured nuclei" not in _en("dx_tr_t3")


# ------------------------------------------------------------------------------------------------ library: checks that hold
def test_bands_finite_ordered_and_flags_consistent():
    """All 6,168 rows: 0 < u68 <= u95, finite; unc68_factor_30keV is the band at 30 keV; in_validated_range is exactly
    Z 26-83; macs30_flag is set exactly where the measured resolved range reaches above 3 keV."""
    e = np.log10(np.asarray(next(iter(cap().values()))["energy_ev"], float))
    for r in cap().values():
        u68, u95 = np.asarray(r["unc68_log10"], float), np.asarray(r["unc95_log10"], float)
        assert np.all(np.isfinite(u68)) and np.all(np.isfinite(u95)) and np.all(u68 > 0) and np.all(u68 <= u95)
        assert math.log10(r["unc68_factor_30keV"]) == pytest.approx(np.interp(math.log10(3e4), e, u68), abs=1e-12)
        assert r["in_validated_range"] == (26 <= r["Z"] <= 83)
        ru = r["resolved_upper_ev"]
        assert bool(r["macs30_flag"]) == (ru is not None and not math.isnan(ru) and ru > 3e3), r["nuclide_id"]


def test_anchored_factor_applied_once():
    """The v0.2.2 ANCHORED curve is v0.2's times the extra factor at every point, and below 1 keV the engine's own shape
    times the same total factor: no factor applied twice or skipped."""
    v02 = {r["nuclide_id"]: r for r in pq.read_table(REPO / "library" / "v0.2" / "capture_v02.parquet").to_pylist()}
    with open(LIB / "anchored_rescale_v022.csv", newline="") as f:
        rows = list(csv.DictReader(f))
    for x in rows:
        i = x["nuclide_id"]
        s, s2 = np.asarray(cap()[i]["sigma_b"]), np.asarray(v02[i]["sigma_b"])
        np.testing.assert_allclose(s / s2, float(x["v022_extra_factor"]), rtol=1e-12)
        b = below()[i]
        tot = s[0] / (b["engine_1keV_mb"] / 1e3)
        np.testing.assert_allclose(cap()[i]["sigma_below1keV_b"], np.asarray(b["engine_mb"]) / 1e3 * tot, rtol=1e-9)


# ------------------------------------------------------------------------------------------------ library: amendment items
@pytest.mark.xfail(strict=True, reason="BUGTIER3 item A: v02_factor parsed from the 3-decimal value_source text")
def test_anchored_rescale_total_factor_is_the_curves_own():
    """anchored_rescale_v022.csv v022_factor (and v02_factor) should be the factor the curve carries: sigma(1 keV) over
    the unscaled engine value at 1 keV. build_library_v022.py parses the v0.2 factor from value_source, where it is
    rounded to 3 decimals, so the listed total is off by up to 6.7e-4 (Ge-76); the curve itself is right."""
    with open(LIB / "anchored_rescale_v022.csv", newline="") as f:
        for x in csv.DictReader(f):
            i = x["nuclide_id"]
            true = cap()[i]["sigma_b"][0] / (below()[i]["engine_1keV_mb"] / 1e3)
            assert float(x["v022_factor"]) == pytest.approx(true, rel=1e-6), i


@pytest.mark.xfail(strict=True, reason="BUGTIER3 item A: value_source 'blind curve x f' rounds the wrong total")
def test_anchored_value_source_factor_rounds_the_true_factor():
    for i, r in cap().items():
        if r["tier"] == "ANCHORED":
            f = float(re.search(r"blind curve x ([0-9.]+) \(measured", r["value_source"]).group(1))
            assert f == round(r["sigma_b"][0] / (below()[i]["engine_1keV_mb"] / 1e3), 3), i


@pytest.mark.xfail(strict=True, reason="BUGTIER3 item B: model_form_max_dex_sub1MeV is 0 for the 3 gg_deadend rows")
def test_model_form_max_dex_covers_the_alternative():
    e = np.asarray(next(iter(cap().values()))["energy_ev"], float)
    k = int(np.argmin(abs(np.log(e / 3e4))))
    for r in cap().values():
        if r["model_form_flag"] != "none":
            dex = abs(math.log10(r["alt_value_30keV_b"] / r["sigma_b"][k]))
            assert r["model_form_max_dex_sub1MeV"] >= dex - 1e-9, r["nuclide_id"]


def _kept_cells_by_nuclide(kev_only):
    cells = []
    for fn in ("exfor_cells_Z26-92_v2.parquet",):
        cells += pq.read_table(REPO / "data" / "curation" / "capture_v2" / fn).to_pylist()
    out = {}
    for c in cells:
        if not c["nuclide"].endswith("M0") or c["decision"] == "exclude" or (c["branch"] or "") in {"PAR", "CN", "DI", "M-", "INC"}:
            continue
        if c["kind"] not in ("sig", "av", "mxw"):
            continue
        if kev_only and not (c["kind"] == "mxw" or (c["e_hi_ev"] or 0) >= 1e3):
            continue
        out.setdefault(c["nuclide"], []).append(c)
    return out


@pytest.mark.xfail(strict=True, reason="BUGTIER3 item C: 57 INTERPOLATED/EXTRAPOLATED nuclides have kept keV capture data")
def test_unmeasured_tiers_have_no_kept_kev_capture_data():
    kept = _kept_cells_by_nuclide(kev_only=True)
    bad = [i for i, r in cap().items() if r["Z"] >= 26 and r["tier"] in ("INTERPOLATED", "EXTRAPOLATED") and i in kept]
    assert bad == []


@pytest.mark.xfail(strict=True, reason="BUGTIER3 item C: Zn-70, Ge-76, Te-120 are ANCHORED with kept keV cross sections")
def test_anchored_have_no_kept_kev_cross_sections():
    kept = _kept_cells_by_nuclide(kev_only=True)
    bad = [i for i, r in cap().items() if r["tier"] == "ANCHORED" and any(c["kind"] != "mxw" for c in kept.get(i, []))]
    assert bad == []


@pytest.mark.xfail(strict=True, reason="BUGTIER3 item E: TERRA coverage cells with 5-6 nuclei marked 'N/A (<5 nuclei)'")
def test_terra_na_label_matches_its_nucleus_count():
    with open(SITE / "data" / "board" / "cells.csv", newline="") as f:
        rows = [r for r in csv.DictReader(f) if r["section"] == "terra"]
    bad = [(r["view"], r["rival"], r["n_nuclei"]) for r in rows
           if r["verdict"] == "N/A (<5 nuclei)" and int(r["n_nuclei"]) >= 5]
    assert bad == []
