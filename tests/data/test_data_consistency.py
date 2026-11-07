"""Consistency checks over every nuclide of INCOGNITA's data products.

Covers: library/v0.2.3 (curves, MACS, rates, below-1-keV joins, grid-dependent list, checksums), the curated capture
set v2.2 (data/curation/capture_v2: keys, units, energies, duplicates, v2.1 and v2.2 review lines), the light
threshold rows (review lines), the site data (docs/walkthrough/data: index.json
against the per-nuclide files and the library) and the C-12 R-matrix evaluation (data/light_evals/C12RM9.json).

Known open defects that need a decision outside the site build (curation review lines or a library errata) are marked
xfail(strict=True): they are listed, and the test turns red when they are fixed so the mark can be removed.

    python -m pytest tests/data/test_data_consistency.py --noconftest -q
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import re
from collections import Counter, defaultdict
from functools import lru_cache
from pathlib import Path

import numpy as np
import pytest

pq = pytest.importorskip("pyarrow.parquet")

REPO = Path(__file__).resolve().parents[2]
LIB = REPO / "library" / "v0.2.3"  # errata of v0.2.2: same values, corrected flags/factors
CAP = REPO / "data" / "curation" / "capture_v2"
INP = REPO / "data" / "curation" / "inputs"
SITE = REPO / "docs" / "walkthrough" / "data"
EVALS = REPO / "data" / "light_evals"
KT = [5, 8, 10, 15, 20, 25, 30, 40, 50, 60, 80, 100]
MN = 1.00866  # u, as library/v0.2.3/RATES.md
NA = 6.02214076e23
U_KEV = 931494.10242  # keV per u
C_CMS = 2.99792458e10
PARTIAL = {"PAR", "CN", "DI", "M-", "INC"}  # SF5 branches that are a part of capture, not the capture cross section
ONE_STATE = re.compile(r"^[GML]\d*$")       # capture into one product state (-G, -M, -M1, -L ...): partial too


def _partial(c):
    return c["branch"] in PARTIAL or bool(ONE_STATE.match(c["state"] or ""))


# ---------------------------------------------------------------- loaders
def _sig(v, n=4):
    if v is None or (isinstance(v, float) and (math.isnan(v) or math.isinf(v))):
        return None
    return 0 if v == 0 else float(f"{v:.{n}g}")


@lru_cache(None)
def cap_lib():
    return pq.read_table(LIB / "capture_v023.parquet").to_pylist()


@lru_cache(None)
def csv_rows(name):
    with open(LIB / name, newline="") as f:
        return list(csv.DictReader(f))


@lru_cache(None)
def cells():
    out = []
    for fn in ("exfor_cells_Z26-92_v2.parquet", "exfor_cells_Z1-25_v2.parquet"):
        out += pq.read_table(CAP / fn).to_pylist()
    return out


@lru_cache(None)
def trust():
    out = {}
    for fn in ("exfor_capture_Z26-92_trust_v2.parquet", "exfor_capture_Z1-25_trust_v2.parquet"):
        for r in pq.read_table(CAP / fn).to_pylist():
            assert r["dataset_key"] not in out
            out[r["dataset_key"]] = r
    return out


@lru_cache(None)
def index():
    return json.loads((SITE / "index.json").read_text())


def nfile(Z, key):
    p = SITE / "n" / str(Z) / f"{key}.json"
    return json.loads(p.read_text()) if p.exists() else None


def parse_nuc(nuc):
    m = re.match(r"Z(\d+)N(\d+)M(\d+)$", nuc)
    if m:
        return int(m[1]), int(m[1]) + int(m[2]), int(m[3])
    m = re.match(r"Z(\d+)NAT$", nuc)
    assert m, nuc
    return int(m[1]), 0, 0


# ---------------------------------------------------------------- checksums
@pytest.mark.parametrize("d", ["library/v0.2.3", "library/v0.2.2", "library/v0.2.1", "library/v0.2", "library/v0.1",
                               "data/curation/capture_v2", "data/curation/inputs"])
def test_sha256sums(d):
    base = REPO / d
    bad = []
    for line in (base / "SHA256SUMS").read_text().splitlines():
        if not line.strip():
            continue
        h, name = line.split(maxsplit=1)
        name = name.lstrip("*")
        p = base / name
        if not p.exists() or hashlib.sha256(p.read_bytes()).hexdigest() != h:
            bad.append(name)
    assert not bad, f"{d}: checksum mismatch {bad}"


# ---------------------------------------------------------------- library v0.2.3
def test_library_keys_and_curves():
    seen = set()
    for r in cap_lib():
        Z, A, M = parse_nuc(r["nuclide_id"])
        assert (Z, A, M) == (r["Z"], r["A"], 0), r["nuclide_id"]
        assert (Z, A) not in seen
        seen.add((Z, A))
        e, s = np.asarray(r["energy_ev"]), np.asarray(r["sigma_b"])
        assert len(e) == 64 and abs(e[0] - 1e3) < 1e-6 and abs(e[-1] - 2e7) < 1e-3 and np.all(np.diff(e) > 0)
        assert np.all(np.isfinite(s)) and np.all(s > 0), r["nuclide_id"]
        eb, sb = np.asarray(r["energy_below1keV_ev"]), np.asarray(r["sigma_below1keV_b"])
        assert len(eb) == 15 and np.all(np.diff(eb) > 0) and eb[-1] < 1e3 and np.all(sb > 0), r["nuclide_id"]
    for name in ("macs30_v023.csv", "macs_kt_v023.csv", "rates_v023.csv", "masses_v023.csv",
                 "compound_smin_v023.csv"):
        ids = [(int(x["Z"]), int(x["A"])) for x in csv_rows(name)]
        assert set(ids) == seen and len(ids) == len(seen), name


def test_library_macs_tables_agree():
    cap = {r["nuclide_id"]: r for r in cap_lib()}
    m30 = {x["nuclide_id"]: x for x in csv_rows("macs30_v023.csv")}
    for x in csv_rows("macs_kt_v023.csv"):
        i = x["nuclide_id"]
        assert float(x["macs30_mb"]) == pytest.approx(cap[i]["macs30_mb"], rel=1e-12), i
        assert float(x["macs30_mb"]) == pytest.approx(float(m30[i]["macs30_mb"]), rel=1e-12), i
        assert x["tier"] == cap[i]["tier"] == m30[i]["tier"], i
        assert float(x["unc68_factor_30keV"]) == pytest.approx(cap[i]["unc68_factor_30keV"], rel=1e-9), i
        sh = [float(x[f"share_below1keV_{k}keV"]) for k in KT]
        assert all(0 <= s < 1 for s in sh) and all(a >= b - 1e-12 for a, b in zip(sh, sh[1:])), i


def _joined(r):
    e = np.concatenate([r["energy_below1keV_ev"], r["energy_ev"]])
    s = np.concatenate([r["sigma_below1keV_b"], r["sigma_b"]])
    return e, s


def _macs(e, s, M, kt_kev, n=20001):
    """MACS (mb), centre-of-mass definition of library/v0.2.3/README.md, log-log curve, 1/v below the first point."""
    kt = kt_kev * 1e3
    ec = np.logspace(-4, math.log10(kt * 50), n)
    el = ec * (M + MN) / M
    ls = np.interp(np.log(np.clip(el, e[0], e[-1])), np.log(e), np.log(s))
    sig = np.exp(ls)
    lo = el < e[0]
    sig[lo] = s[0] * np.sqrt(e[0] / el[lo])
    f = sig * ec * np.exp(-ec / kt)
    return 2 / math.sqrt(math.pi) * np.trapezoid(f, ec) / kt**2 * 1e3


def test_library_macs_match_curves_all_nuclides():
    """Every MACS(kT) recomputed from its own curve (below-1-keV points + 64-point grid), all 6168 nuclides."""
    mass = {x["nuclide_id"]: float(x["mass_u"]) for x in csv_rows("masses_v023.csv")}
    mk = {x["nuclide_id"]: x for x in csv_rows("macs_kt_v023.csv")}
    bad = []
    for r in cap_lib():
        e, s = _joined(r)
        for k in (5, 30, 100):
            v = _macs(e, s, mass[r["nuclide_id"]], k)
            ref = float(mk[r["nuclide_id"]][f"macs{k}_mb"])
            if abs(v / ref - 1) > 1e-4:
                bad.append((r["nuclide_id"], k, v, ref))
    assert not bad, bad[:20]


def test_library_rates_reduced_mass():
    mk = {x["nuclide_id"]: x for x in csv_rows("macs_kt_v023.csv")}
    mass = {x["nuclide_id"]: float(x["mass_u"]) for x in csv_rows("masses_v023.csv")}
    bad = []
    for x in csv_rows("rates_v023.csv"):
        i, M = x["nuclide_id"], float(x["target_mass_u"])
        assert M == mass[i], i
        mu = 1.00866491595 * M / (1.00866491595 + M)  # RATES.md rounds m_n to 1.00866 u; the files use CODATA
        assert float(x["reduced_mass_u"]) == pytest.approx(mu, rel=1e-9), i
        # at T9 where kT is a MACS grid point: kT = 86.1733 keV * T9; T9 = 0.3482 is not on the grid, so use the
        # MACS interpolated in log-log at kT(T9 = 0.3) = 25.85 keV only as a coarse check (2 %).
        kt = 86.1733 * 0.3
        lm = np.interp(math.log(kt), np.log(KT), np.log([float(mk[i][f"macs{k}_mb"]) for k in KT]))
        vt = math.sqrt(2 * kt / (mu * U_KEV)) * C_CMS
        rate = NA * math.exp(lm) * 1e-27 * vt
        if abs(rate / float(x["rate_T9_0.3"]) - 1) > 0.02:
            bad.append((i, rate, x["rate_T9_0.3"]))
    assert not bad, bad[:10]


def test_grid_dependent_list_matches_flag():
    flag = {(r["Z"], r["A"]) for r in cap_lib() if r["engine_grid_dependent"]}
    lst = {(int(x["Z"]), int(x["A"])) for x in csv_rows("grid_dependent_v023.csv")}
    smin = {(int(x["Z"]), int(x["A"])): float(x["smin_MeV"]) for x in csv_rows("compound_smin_v023.csv")}
    assert flag == lst
    assert len(lst) == 2364
    assert lst == {k for k, v in smin.items() if v < -1.0}


# Engine's own steep rise between 0.66 keV and 1 keV (the 15 below-1-keV values are the engine's, joined exactly at
# 1 keV; the rise is in the engine run itself, all EXTRAPOLATED, mostly very exotic). Listed so a new one shows up.
JOIN_KINK_KNOWN = ["Z053N058M0", "Z054N059M0", "Z072N146M0", "Z074N148M0", "Z074N150M0", "Z076N148M0", "Z078N160M0",
                   "Z080N164M0", "Z080N170M0", "Z080N172M0", "Z091N109M0"]


def test_below1keV_join():
    """The 15 points below 1 keV meet the 64-point curve at 1 keV: the 1/v ones are exactly sigma(1 keV) sqrt(1 keV/E);
    no join changes the log-log slope by more than 2.5 except the known engine kinks."""
    kink = []
    for r in cap_lib():
        e, s = _joined(r)
        if r["below1keV_source"].startswith("1/v"):
            np.testing.assert_allclose(r["sigma_below1keV_b"],
                                       r["sigma_b"][0] * np.sqrt(1e3 / np.asarray(r["energy_below1keV_ev"])), rtol=1e-9)
        sl = np.diff(np.log(s)) / np.diff(np.log(e))
        if abs(sl[13] - sl[14]) > 2.5:
            kink.append(r["nuclide_id"])
    assert kink == JOIN_KINK_KNOWN


def test_anchored_rescale_consistent():
    cap = {r["nuclide_id"]: r for r in cap_lib()}
    rows = csv_rows("anchored_rescale_v023.csv")
    assert {x["nuclide_id"] for x in rows} == {i for i, r in cap.items() if r["tier"] == "ANCHORED"}
    for x in rows:
        assert float(x["anchor_equals_v02_macs30_mb"]) == pytest.approx(cap[x["nuclide_id"]]["macs30_mb"], rel=1e-9)
        assert float(x["v022_factor"]) == pytest.approx(float(x["v02_factor"]) * float(x["v022_extra_factor"]), rel=1e-9)


# ---------------------------------------------------------------- curated capture v2
def test_curation_keys():
    tr = trust()
    for k, r in tr.items():
        Z, A, M = parse_nuc(r["nuclide"])
        assert (Z, A) == (r["target_z"], r["target_a"]), k
        assert r["group_key"] == "" or r["group_key"].split("|")[0] == r["nuclide"], k  # "" = no cells
    for c in cells():
        t = tr[c["dataset_key"]]
        assert (c["nuclide"], c["group_key"], c["kind"], c["state"]) == (t["nuclide"], t["group_key"], t["kind"],
                                                                           t["state"] or ""), c["dataset_key"]
        assert c["decision"] == t["decision"], c["dataset_key"]


def test_curation_values_physical():
    for c in cells():
        assert c["mean_b"] > 0 and math.isfinite(c["mean_b"]), c["dataset_key"]
        assert 0 < c["e_lo_ev"] <= c["e_hi_ev"] <= 2e7, c["dataset_key"]


def _mxw_odd():
    """Maxwellian averages whose temperature is neither thermal (kT < 0.1 eV) nor stellar (kT >= 1 keV), used."""
    return sorted({c["dataset_key"] for c in cells() if c["kind"] == "mxw" and c["decision"] != "exclude"
                   and 0.1 < c["e_lo_ev"] < 1e3})


def test_curation_mxw_temperatures():
    # fixed in capture set v2.1: 14248005 W-186 (kT EV -> KEV at staging), 14165012 Te-120 (a resonance integral, excluded)
    assert _mxw_odd() == []
    w186 = sorted(c["e_lo_ev"] for c in cells() if c["dataset_key"] == "14248/14248005/")
    assert w186 and 4e3 < w186[0] and w186[-1] <= 1.0001e5, w186


def _review_lines(path):
    return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip() and not l.startswith("#")]


def test_curation_v21_lines_applied():
    """Every CAPSET-v2.1 decision line is the dataset's decision in the v2.1 tables; fix-unit factors are logged."""
    lines = [l for l in _review_lines(CAP / "review_decisions_capture_v2.jsonl") if l.get("version") == "2.1"]
    assert lines
    tr = trust()
    for l in lines:
        k = f"{l['entry']}/{l['subentry']}/{l['pointer']}"
        assert k in tr, k
        if "decision" in l:
            assert tr[k]["decision"] == l["decision"], (k, tr[k]["decision"])
            if l["decision"] == "fix-unit":
                assert tr[k]["unit_fix_factor"] == l["factor"], k
        if l.get("superseded_by"):
            assert tr[l["superseded_by"]]["decision"] != "exclude", l["superseded_by"]


def test_curation_v22_total_cross_sections_excluded():
    """CAPSET-v2.2 D11: Celenk 1991 (EXFOR 22234002-007) are total thermal cross sections of the foils compiled as
    (N,G); every subentry has an exclude line and is excluded in the v2.2 tables, and no cell of them is used."""
    lines = [l for l in _review_lines(CAP / "review_decisions_capture_v2.jsonl") if l.get("version") == "2.2"]
    keys = {f"{l['entry']}/{l['subentry']}/{l['pointer']}" for l in lines}
    assert keys == {f"22234/22234{i:03d}/" for i in range(2, 8)}, sorted(keys)
    tr = trust()
    for l in lines:
        k = f"{l['entry']}/{l['subentry']}/{l['pointer']}"
        assert l["decision"] == "exclude" and l["rule"] == "D11_TOTAL_XS" and "total" in l["reason"], k
        assert tr[k]["decision"] == "exclude", (k, tr[k]["decision"])
    assert not [c for c in cells() if c["dataset_key"] in keys and c["decision"] != "exclude"]
    assert json.loads((CAP / "provenance.json").read_text())["version"] == "2.2"


def _identical_used_pairs(min_cells=2):
    by = defaultdict(list)
    for c in cells():
        if c["decision"] != "exclude":
            by[c["dataset_key"]].append((c["bin"], round(c["mean_b"], 9)))
    sig = defaultdict(list)
    for k, v in by.items():
        if len(v) >= min_cells:
            sig[(trust()[k]["group_key"], tuple(sorted(v)))].append(k)
    return sorted(tuple(sorted(v)) for v in sig.values() if len(v) > 1)


def test_curation_no_duplicate_datasets_used():
    # Ba-132 22939040 pointer 3 (= pointer 2) excluded in v2.1. Single-cell coincidences (one thermal value equal to
    # another experiment's to the printed digits) are common and not tested here.
    assert _identical_used_pairs() == []


def test_curation_fix_unit_factor_logged():
    for k, t in trust().items():
        if t["decision"] == "fix-unit":
            assert t["unit_fix_factor"] in (1e-3, 1e3, 1e-6, 1e6), k


# ---------------------------------------------------------------- site data
def test_site_index_matches_library():
    idx = index()
    cols = idx["cols"]
    rows = {(r[0], r[1]): dict(zip(cols, r)) for r in idx["rows"]}
    assert len(rows) == len(idx["rows"]), "duplicate index rows"
    for r in cap_lib():
        x = rows.get((r["Z"], r["A"]))
        assert x is not None, f"missing nuclide {r['nuclide_id']}"
        assert idx["tiers"][x["tier"]] == r["tier"]
        assert x["macs30_mb"] == _sig(r["macs30_mb"])
        assert x["valid"] == int(bool(r["in_validated_range"]))
    assert idx["grid_ev"] == [_sig(e, 5) for e in cap_lib()[0]["energy_ev"]]


def test_site_files_match_index_and_library():
    idx = index()
    cols = idx["cols"]
    lib = {(r["Z"], r["A"]): r for r in cap_lib()}
    mk = {(int(x["Z"]), int(x["A"])): x for x in csv_rows("macs_kt_v023.csv")}
    for row in idx["rows"]:
        x = dict(zip(cols, row))
        Z, A = x["Z"], x["A"]
        d = nfile(Z, A)
        assert d is not None, (Z, A)
        m = d.get("meas", {"cap": [], "mxw": [], "ds": []})
        assert (x["n_cap"], x["n_mxw"], x["n_ds"]) == (len(m["cap"]), len(m["mxw"]), len(m["ds"])), (Z, A)
        assert x["n_use"] == sum(1 for p in m["cap"] + m["mxw"] if p[5] != "x"), (Z, A)
        t = d.get("thr", {})
        assert (x["n_n2n"], x["n_np"], x["n_na"]) == tuple(len(t.get(k, [])) for k in ("n2n", "np", "na")), (Z, A)
        L = lib.get((Z, A))
        if L is None:
            assert "cap" not in d and x["tier"] == -1
            continue
        assert d["cap"] == [_sig(v) for v in L["sigma_b"]], (Z, A)
        assert d["macs"] == [_sig(float(mk[(Z, A)][f"macs{k}_mb"])) for k in KT], (Z, A)
        assert d["macs30"] == x["macs30_mb"]


def test_site_natural_list():
    idx = index()
    nat = sorted(int(p.parent.name) for p in SITE.glob("n/*/nat.json"))
    assert idx["natural"] == nat


def test_site_light_labels():
    """Z < 26: the page's measured / not measured label is n_use > 0; n_use must equal the used capture cells
    (kept or down-weighted, cross section, average or Maxwellian; total capture of the ground-state target)."""
    idx = index()
    cols = idx["cols"]
    use = Counter()
    for c in cells():
        Z, A, M = parse_nuc(c["nuclide"])
        if Z < 26 and A and M == 0 and c["kind"] in ("sig", "av", "mxw") and c["decision"] != "exclude" \
                and not _partial(c):
            use[(Z, A)] += 1
    for row in idx["rows"]:
        x = dict(zip(cols, row))
        if x["Z"] < 26:
            assert x["n_use"] == use[(x["Z"], x["A"])], (x["Z"], x["A"])


def test_site_isomer_targets_not_merged_into_ground_state():
    """A capture cell on an isomeric target (Ta-180m, Hf-178m2, Ho-166m, ...) must not be drawn on the ground state."""
    iso = defaultdict(set)
    for c in cells():
        Z, A, M = parse_nuc(c["nuclide"])
        if M:
            iso[(Z, A)].add(c["dataset_key"])
    assert iso, "expected isomer-target datasets in capture v2"
    for (Z, A), keys in iso.items():
        d = nfile(Z, A) or {}
        shown = {ds[0] for ds in d.get("meas", {}).get("ds", [])}
        assert not (shown & keys), (Z, A, sorted(shown & keys))


def test_site_partial_branches_not_drawn_as_capture():
    part = {c["dataset_key"] for c in cells() if c["branch"] in PARTIAL}
    part |= {c["dataset_key"] for c in cells() if ONE_STATE.match(c["state"] or "")}
    for p in SITE.glob("n/*/*.json"):
        d = json.loads(p.read_text())
        m = d.get("meas")
        if not m:
            continue
        drawn = {m["ds"][q[4]][0] for q in m["cap"] + m["mxw"]}
        assert not (drawn & part), (p.name, sorted(drawn & part)[:5])


def test_site_fix_unit_points_are_fixed():
    """Points labelled 'unit fixed' (f) carry the corrected value: mean_b x unit_fix_factor."""
    tr = trust()
    want = {}
    for c in cells():
        if c["decision"] == "fix-unit" and c["kind"] in ("sig", "av", "mxw") and not _partial(c):
            Z, A, M = parse_nuc(c["nuclide"])
            want[(Z, A or "nat", c["dataset_key"], _sig(c["e_lo_ev"], 5))] = _sig(c["mean_b"] * tr[c["dataset_key"]]["unit_fix_factor"])
    assert want
    for (Z, A, key, e), v in want.items():
        d = nfile(Z, A)
        m = d["meas"]
        pts = [q for q in m["cap"] + m["mxw"] if m["ds"][q[4]][0] == key and q[0] == e]
        assert pts and all(q[5] == "f" and q[2] == v for q in pts), (Z, A, key, pts, v)


def _thr_outliers():
    """Measured (n,2n)/(n,p)/(n,alpha) points (mb) more than x200 from the library channel curve (mb), where the curve
    is above 1 mb."""
    ch = {(r["Z"], r["A"]): r for r in pq.read_table(LIB / "channels_v023.parquet").to_pylist()}
    out = []
    for p in SITE.glob("n/*/*.json"):
        if p.stem == "nat":
            continue
        Z, A = int(p.parent.name), int(p.stem)
        d = json.loads(p.read_text())
        L = ch.get((Z, A))
        for k, name in (("n2n", "sigma_n2n_mb"), ("np", "sigma_np_mb"), ("na", "sigma_na_mb")):
            if L is None or L[name] is None:
                continue
            for q in d.get("thr", {}).get(k, []):
                v = np.interp(q[0], L["energy_ev"], L[name])
                if v > 1.0 and q[1] > 0 and abs(math.log10(q[1] / v)) > 2.3:
                    out.append((Z, A, k, q[2]))
    return sorted(out)


def test_site_threshold_rows_units():
    # Cr-52/Cr-53(n,p) Chittenden 1961 (11132004/005, x1000 slips) fixed by review lines in build_light_channels.py 1.1
    assert _thr_outliers() == []


def test_threshold_review_lines_applied():
    """Light (n,2n)/(n,p)/(n,alpha) rows: excluded series (or points) are gone, fix-unit series are scaled and marked."""
    rows = pq.read_table(INP / "exfor_threshold_Z1-25_rows.parquet").to_pylist()
    by, byp = defaultdict(list), defaultdict(list)
    for r in rows:
        by[r["series"].split(".")[0]].append(r)
        byp[r["series"].replace(".nan", ".")].append(r)  # "subentry.pointer" ("subentry." without a pointer)
    for l in _review_lines(INP / "review_decisions_threshold_Z1-25.jsonl"):
        got = byp.get(f"{l['subentry']}.{l.get('pointer') or ''}", [])
        if l["decision"] == "exclude" and not l.get("points"):
            assert not got, l["subentry"]
        elif l["decision"] == "exclude":
            for p in l["points"]:
                assert not any(abs(r["e_ev"] / p["e_ev"] - 1) < 1e-6 and r["n_pts"] == 1 for r in got), (l["subentry"], p)
        else:
            assert got and all(r["review"] == f"fix-unit x{l['factor']:g}" for r in got), l["subentry"]
    cr52 = [r["data_mb"] for r in by["11132004"]]
    assert cr52 == [pytest.approx(82.7)], cr52


def test_site_threshold_points_not_below_reaction_threshold():
    """No measured (n,2n)/(n,p)/(n,alpha) point below the reaction's kinematic threshold E = -Q (A+1)/A (Q from the
    site's own q.json, the values the page draws as the threshold mark); 1 % slack for the nominal energy of a point
    whose energy spread straddles the threshold (Ti-46(n,2n) Prestwood 1961 at 13.40 +- 0.20 MeV, threshold 13.48).
    BUGLIGHT5: C-12(n,2n) Ashby 1958 (11097006, 6 +- 6 mb at 14.1 MeV, threshold 20.3 MeV) and Ca-40(n,2n) Braun 1968
    (22611002, 8 mb at 14.69 MeV, threshold 16.0 MeV) were shown."""
    q = json.loads((SITE / "q.json").read_text())["q"]
    bad = []
    for p in SITE.glob("n/*/*.json"):
        if p.stem == "nat":
            continue
        Z, A = int(p.parent.name), int(p.stem)
        for k, pts in json.loads(p.read_text()).get("thr", {}).items():
            Q = (q.get(f"{Z}-{A}") or [None] * 3)[{"np": 0, "na": 1, "n2n": 2}[k]]
            assert Q is not None, (Z, A, k)
            thr = max(0.0, -Q * (A + 1) / A * 1e6)
            bad += [(Z, A, k, x[0], x[2]) for x in pts if x[0] < 0.99 * thr]
    assert bad == []


def test_site_threshold_no_measurement_counted_twice():
    """BUGLIGHT5: light threshold series that repeat another series of the rows (the same measurement compiled twice, or
    an average shown next to the runs it averages, EXFOR STATUS DEP) are shown once (review lines, rows version 1.2)."""
    twice = [  # (Z, A, channel, energy eV, the copy that must go, the series that stays)
        (14, 28, "np", 1.41e7, "41118005", "41036002"),     # Klochkova: conference 1990 = journal 1992
        (22, 46, "np", 8.5e6, "30523004", "30733004"),      # Lu Hanlin revised set repeats Fan Peiguo 1985 at 8.5 MeV
        (22, 46, "n2n", 1.47e7, "33001007.1", "30962002"),  # Pansare 1993 HPGe = Dighe/Pansare 1991
        (24, 50, "n2n", 1.47e7, "33001006.1", "30962003"),
        (8, 16, "np", 1.47e7, "21846006", "21846035.2"),    # Schantl: average (DEP 035-037) and its runs
        (9, 19, "np", 1.47e7, "21846009", "21846040"),
        (19, 41, "np", 1.47e7, "21846026", "21846052"),
        (20, 40, "np", 1.47e7, "21846055", "21846027"),     # run relative to Al-27 shown next to the average that holds it
        (13, 27, "np", 1.47e7, "40676002", "40676003"),     # average of 003 (beta-gamma) and 004 (gamma spectrometry)
        (13, 27, "na", 1.48e7, "41051004", "41051002"),     # average of 002 and 003
    ]
    for Z, A, k, e, gone, stays in twice:
        pts = nfile(Z, A)["thr"][k]
        at = lambda s: [x for x in pts if x[2] == s and abs(x[0] / e - 1) < 0.02]
        assert at(stays), (Z, A, k, stays)
        assert not at(gone), (Z, A, k, gone)


# ---------------------------------------------------------------- C-12 R-matrix evaluation
def test_c12rm9_curve():
    ev = json.loads((EVALS / "C12RM9.json").read_text())
    e, s, mu = np.asarray(ev["energy_ev"]), np.asarray(ev["sigma_b"]), np.asarray(ev["mubar_cm"])
    assert (int(ev["Z"]), int(ev["A"])) == (6, 12)
    assert len(e) == len(s) == len(mu) and np.all(np.diff(e) > 0)
    assert e[0] == pytest.approx(float(ev["e_min_ev"])) and e[-1] == pytest.approx(float(ev["e_max_ev"]))
    assert np.all(s > 0) and np.all(np.abs(mu) <= 1)
    # low-energy limit: 0 K free-atom elastic of C-12 is 4.74 b (IAEA std2017 carbon: 4.74 b at 1e-5 eV)
    assert s[0] == pytest.approx(4.74, rel=0.002)
    # 2.08 MeV resonance is above; below 1.8 MeV the elastic is smooth and decreasing from 4.74 b to ~1.6 b
    assert 1.0 < s[-1] < 2.5
    site = nfile(6, 12)["rm"]
    for k in ("energy_ev", "sigma_b", "mubar_cm", "e_min_ev", "e_max_ev", "id"):
        assert site[k] == ev[k], k
    assert index()["light_evals"] == {"6-12": ev["id"]}
