"""Build the data files of the website's Data explorer (docs/walkthrough/data/).

Reads library v0.2.3 (production-engine curves for every nuclide; v0.2.2 errata: same values, corrected flags and factors) and the curated EXFOR capture cells of
capture set v2 (data/curation/capture_v2: exfor_capture_Z26-92_trust_v2 + exfor_cells_Z26-92_v2 and the Z 1-25 pair, the WP-12
curation re-run on the corrected 2026-10-14 staging by scripts/build_capture_v2.py; display only: the library, its tiers
and every score stay as they are; --curation v1 reads the earlier data/curation/inputs tables), plus measured (n,2n), (n,p) and (n,alpha) points: the benchmark rows (Z 24-92,
incognita/bench/data/exam_rows) and, for Z 1-25, EXFOR rows cut with the same rules by scripts/build_light_channels.py
(data/curation/inputs/exfor_threshold_Z1-25_rows.parquet), and writes:
  data/index.json      one row per nuclide (chart of nuclides: tier, MACS at 30 keV, counts of measured data), plus
                       which comparison files exist (index list "lib", column "rr"; see below)
  data/n/<Z>/<A>.json  everything about one nuclide (<A> is "nat" for a natural element), fetched only when that
                       nuclide is opened; the chart itself needs only the index

Index column n_use: curated capture cells (cross sections and Maxwellian averages) of the nuclide that the curation did
NOT exclude. The page uses it for the tier it shows below Z 26. Library v0.2 (and v0.2.1 - v0.2.3) defines its tiers only from Z 26 up (every
Z < 26 row is EXTRAPOLATED there, because the library's curated capture set started at Z 26); the page does not change
the library's tier (field "tier" stays the library's), it shows "measured (Z < 26)" when n_use > 0 and "not measured
(Z < 26)" otherwise. Measured means: at least one curated EXFOR capture cell that the curation kept or down-weighted.

Only the capture cross section of the ground-state (or natural) target is drawn and counted: cells on an isomeric target
(Ta-180m, Hf-178m2, Ho-166m, ...) are not put on the ground state's file, and partial branches (EXFOR SF5 PAR, CN, DI,
M-, INC: gamma-line, level or component cross sections) and capture into one product state (-G, -M, -M1, -L ...) are
listed with the datasets but only counted under "other". A
fix-unit cell is drawn with its logged unit factor applied (the curation tables keep the value as compiled).
Index list "lib" (Z with a data/lib/<Z>.json) and column "rr" (1 when data/rr/<Z>/<A>.json exists) are read from the
files already published there, so run scripts/build_site_overlay.py and scripts/build_site_rr.py first; the page fetches
only the files they flag (tests/test_site_flags.py).
Checked by tests/data/test_data_consistency.py.

usage:  uv run --no-project --with pyarrow python scripts/build_site_data.py [--curation v1]
"""
import csv, json, math, os, re, shutil
from collections import defaultdict

import pyarrow.parquet as pq
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIB = os.path.join(ROOT, "library", "v0.2.3")
OUT = os.path.join(ROOT, "docs", "walkthrough", "data")

SYM = ("n H He Li Be B C N O F Ne Na Mg Al Si P S Cl Ar K Ca Sc Ti V Cr Mn Fe Co Ni Cu Zn Ga Ge As Se Br Kr Rb Sr Y Zr "
       "Nb Mo Tc Ru Rh Pd Ag Cd In Sn Sb Te I Xe Cs Ba La Ce Pr Nd Pm Sm Eu Gd Tb Dy Ho Er Tm Yb Lu Hf Ta W Re Os Ir Pt "
       "Au Hg Tl Pb Bi Po At Rn Fr Ra Ac Th Pa U Np Pu Am Cm Bk Cf Es Fm Md No Lr Rf Db Sg Bh Hs Mt Ds Rg Cn Nh Fl Mc Lv "
       "Ts Og").split()
TIERS = ["MEASURED", "ANCHORED", "INTERPOLATED", "EXTRAPOLATED"]
KT = [5, 8, 10, 15, 20, 25, 30, 40, 50, 60, 80, 100]
DEC = {"keep": "k", "downweight": "d", "exclude": "x", "fix-unit": "f"}
# EXFOR SF5 branches that are a part of capture (partial gamma-line or level cross sections, compound / direct components,
# "metastable excluded"), not the capture cross section: listed with the nuclide's datasets, counted under "other", not
# drawn as capture and not counted as a capture measurement (n_use)
PARTIAL = {"PAR", "CN", "DI", "M-", "INC"}
# Capture into ONE product state (EXFOR SF4 -G, -M, -M1, -M2, -L ...; the cell's "state") is a partial cross section of
# the same class (Seth, 2026-11-07): listed with the datasets, counted under "other" as "<state>:<kind>", not drawn as
# total capture and not in n_use. Sums over states (M1+M2, G+M1, G+M2) are not single states and are left as they were.
ONE_STATE = re.compile(r"^[GML]\d*$")


def partial_kind(branch, state):
    """The "other" label of a partial cell (lower-case SF5 branch or single product state), or None for total capture."""
    if (branch or "") in PARTIAL:
        return branch.lower()
    if ONE_STATE.match(state or ""):
        return state.lower()
    return None


def sig(v, n=4):
    """round to n significant digits; None/NaN -> None"""
    if v is None or (isinstance(v, float) and (math.isnan(v) or math.isinf(v))):
        return None
    if v == 0:
        return 0
    return float(f"{v:.{n}g}")


def sigl(xs, n=4):
    return None if xs is None else [sig(x, n) for x in xs]


def za(nuc):
    """'Z028N032M0' -> (28, 60); 'Z036NAT' -> (36, 0); an isomeric target ('Z073N107M1', Ta-180m) -> (None, None):
    the site has one file per ground-state nuclide, and capture on an isomer is a different reaction"""
    m = re.match(r"Z(\d+)N(\d+)(?:M(\d+))?$", nuc)
    if m:
        if m.group(3) not in (None, "0"):
            return None, None
        return int(m.group(1)), int(m.group(1)) + int(m.group(2))
    m = re.match(r"Z(\d+)NAT", nuc)
    return (int(m.group(1)), 0) if m else (None, None)


def relerr(r):
    s, y, m = r.get("stat_rel"), r.get("sys_rel"), r.get("sem_rel")
    parts = [x for x in (s, y) if x is not None and not math.isnan(x)]
    if parts:
        return sig(math.sqrt(sum(x * x for x in parts)), 3)
    return sig(m, 3) if m is not None and not math.isnan(m) else None


def shown_value(mean_b, decision, factor):
    """The value the page shows for a cell. A fix-unit dataset (a compiled unit slip, e.g. B for mb) is labelled
    "unit fixed" on the page, so it is shown with the curation's factor applied (the cell keeps the compiled value)."""
    if decision == "fix-unit" and factor is not None and not math.isnan(factor) and mean_b is not None:
        return mean_b * factor
    return mean_b


def n_use(points):
    """Measured points the curation did not exclude (index column n_use): kept, down-weighted, and unit-fixed cells
    (a fix-unit cell is used with the curation's factor applied, so it counts as a measurement)."""
    return sum(1 for p in points if p[5] != "x")


def main():
    for old in ("z", "n"):  # data/z/<Z>.json was the per-element layout before per-nuclide files
        shutil.rmtree(os.path.join(OUT, old), ignore_errors=True)
    nucs = {}  # (Z, A) -> dict

    # ---- library curves ----
    cap = pq.read_table(os.path.join(LIB, "capture_v023.parquet")).to_pylist()
    grid = [sig(e, 5) for e in cap[0]["energy_ev"]]
    for r in cap:
        assert [sig(e, 5) for e in r["energy_ev"]] == grid, "capture grids differ"
        nucs[(r["Z"], r["A"])] = {
            "tier": TIERS.index(r["tier"]), "valid": bool(r["in_validated_range"]),
            "cap": sigl(r["sigma_b"]), "u68": sigl(r["unc68_log10"], 3), "u95": sigl(r["unc95_log10"], 3),
            "res": sig(r["resolved_upper_ev"], 3), "macs30": sig(r["macs30_mb"]), "flag": r["macs30_flag"] or "",
            "src": r["value_source"] or "", "unc": r["unc_kind"] or "",
        }
        mf = r.get("model_form_flag") or "none"
        if mf != "none":  # model-form note (v0.2): alternate deck choice at 30 keV; keys only, the page writes the text
            v30 = r["sigma_b"][min(range(len(r["energy_ev"])), key=lambda i: abs(math.log(r["energy_ev"][i] / 3e4)))]
            a30 = r.get("alt_value_30keV_b")
            ok = a30 is not None and not (isinstance(a30, float) and math.isnan(a30)) and v30 > 0
            nucs[(r["Z"], r["A"])]["mform"] = {"kind": mf, "alt30": sig(a30) if ok else None, "ratio": sig(a30 / v30, 3) if ok else None}
    ch = pq.read_table(os.path.join(LIB, "channels_v023.parquet")).to_pylist()
    for r in ch:
        n = nucs.get((r["Z"], r["A"]))
        if n is None:
            continue
        n["ch"] = {k: sigl(r[f"sigma_{k}_mb"]) for k in ("np", "n2n", "na") if r[f"sigma_{k}_mb"] is not None}
    npl = defaultdict(list)
    for r in pq.read_table(os.path.join(LIB, "grid_np_v023.parquet")).to_pylist():
        if r["pred_mb"] is not None:
            npl[(r["Z"], r["A"])].append((r["E_MeV"] * 1e6, r["pred_mb"], r["lo68_mb"], r["hi68_mb"]))
    for k, rows in npl.items():
        if k in nucs:
            rows.sort()
            nucs[k]["npL"] = [[sig(a, 5), sig(b), sig(c), sig(d)] for a, b, c, d in rows]
    with open(os.path.join(LIB, "macs_kt_v023.csv"), newline="") as f:
        for r in csv.DictReader(f):
            n = nucs.get((int(r["Z"]), int(r["A"])))
            if n is None:
                continue
            fl = lambda s: sig(float(s)) if s not in ("", None) else None
            n["macs"] = [fl(r[f"macs{t}_mb"]) for t in KT]
            n["macsU"] = [fl(r[f"unc68_factor_{t}keV"]) for t in KT]

    # ---- measured capture (curated EXFOR cells) ----
    # capture set v2 (default) or v1 (--curation v1); Z 26-92 and Z 1-25 files never share a dataset key (asserted)
    INP = os.path.join(ROOT, "data", "curation", "inputs")
    v1 = "--curation" in sys.argv and sys.argv[sys.argv.index("--curation") + 1] == "v1"
    CAP = INP if v1 else os.path.join(ROOT, "data", "curation", "capture_v2")
    TRUST = (("exfor_capture_Z26-92_trust.parquet", "exfor_capture_Z1-25_trust.parquet") if v1
             else ("exfor_capture_Z26-92_trust_v2.parquet", "exfor_capture_Z1-25_trust_v2.parquet"))
    CELLS = (("exfor_cells.parquet", "exfor_cells_Z1-25.parquet") if v1
             else ("exfor_cells_Z26-92_v2.parquet", "exfor_cells_Z1-25_v2.parquet"))
    meta, ufix = {}, {}
    for fn in TRUST:
        for r in pq.read_table(os.path.join(CAP, fn), columns=["dataset_key", "first_author", "year", "facility", "unit_fix_factor"]).to_pylist():
            assert r["dataset_key"] not in meta, r["dataset_key"]
            meta[r["dataset_key"]] = (r["first_author"] or "", r["year"], r["facility"] or "", r["unit_fix_factor"])
    meas = defaultdict(lambda: {"ds": [], "dsi": {}, "cap": [], "mxw": [], "other": defaultdict(int)})
    cells = [r for fn in CELLS for r in pq.read_table(os.path.join(CAP, fn)).to_pylist()]
    n_iso = 0
    for r in cells:
        Z, A = za(r["nuclide"])
        if Z is None:
            n_iso += 1
            continue
        m = meas[(Z, A)]
        key = r["dataset_key"]
        if key not in m["dsi"]:
            au, yr, fac, _ = meta.get(key, ("", r["year"], "", None))
            m["dsi"][key] = len(m["ds"])
            m["ds"].append([key, au, yr if yr is not None else r["year"], fac])
        i, kind = m["dsi"][key], r["kind"]
        y = r["mean_b"]
        if r["decision"] == "fix-unit":  # the curation logs the factor and leaves the value as compiled; the page says "unit fixed"
            f = meta[key][3]
            assert f is not None and f > 0 and not math.isnan(f), key
            y *= f
        pt = [sig(r["e_lo_ev"], 5), sig(r["e_hi_ev"], 5), sig(y), relerr(r), i, DEC.get(r["decision"], "k"), r["state"] or ""]
        pk = partial_kind(r["branch"], r["state"])
        if pk:
            m["other"][f"{pk}:{kind}"] += 1
        elif kind in ("sig", "av"):
            m["cap"].append(pt)
        elif kind == "mxw":
            m["mxw"].append(pt)
        else:
            m["other"][kind] += 1

    # ---- measured threshold channels ----
    # Z >= 26: the benchmark rows. Their (n,alpha) file also holds He-4 production rows (kind "nxa", (n,x)He-4, the
    # benchmark's separate he_prod quantity): a different reaction, so they are not shown as (n,alpha).
    # Z 1-25: the same rules on the 2026-10-14 EXFOR snapshot (scripts/build_light_channels.py); for Z 24-25 the benchmark
    # has only He-production rows, so the two sources never meet on one nuclide (asserted).
    thr = defaultdict(lambda: defaultdict(list))
    for ch_, fn in (("n2n", "n2n_rows"), ("np", "np_rows"), ("na", "na_rows")):
        for r in pq.read_table(os.path.join(ROOT, "incognita", "bench", "data", "exam_rows", fn + ".parquet")).to_pylist():
            if r.get("kind") == "nxa":
                continue
            series = str(r.get("series") or "").replace(".nan", "")
            thr[(r["Z"], r["A"])][ch_].append([sig(r["e_ev"], 5), sig(r["data_mb"]), series, r.get("year")])
    assert all(Z >= 26 for Z, _ in thr), "benchmark (n,2n)/(n,p)/(n,alpha) rows below Z 26"
    for r in pq.read_table(os.path.join(INP, "exfor_threshold_Z1-25_rows.parquet")).to_pylist():
        assert r["Z"] <= 25
        series = str(r["series"]).replace(".nan", "")
        thr[(r["Z"], r["A"])][r["channel"]].append([sig(r["e_ev"], 5), sig(r["data_mb"]), series, r["year"]])

    # ---- write ----
    keys = set(nucs) | {k for k in meas if k[1] > 0} | set(thr)
    # which comparison files exist, read from the published tree so the page never requests an absent one:
    # data/lib/<Z>.json (scripts/build_site_overlay.py) -> index list "lib" of Z; data/rr/<Z>/<A>.json
    # (scripts/build_site_rr.py) -> index column "rr" (1 = the file exists). Run those two first.
    lib_z = sorted(int(f[:-5]) for f in os.listdir(os.path.join(OUT, "lib")) if re.fullmatch(r"\d+\.json", f))
    has_rr = lambda Z, A: 1 if A > 0 and os.path.isfile(os.path.join(OUT, "rr", str(Z), f"{A}.json")) else 0
    index, byz = [], defaultdict(dict)
    for (Z, A) in sorted(keys):
        n = nucs.get((Z, A), {})
        m = meas.get((Z, A))
        t = thr.get((Z, A), {})
        rec = dict(n)
        if m:
            rec["meas"] = {"ds": m["ds"], "cap": m["cap"], "mxw": m["mxw"], "other": dict(m["other"])}
        if t:
            rec["thr"] = {k: sorted(v) for k, v in t.items()}
        byz[Z][str(A)] = rec
        index.append([Z, A, n.get("tier", -1), n.get("macs30"), (n.get("macs") and n.get("macsU") and n["macsU"][KT.index(30)]),
                      len(m["cap"]) if m else 0, len(m["mxw"]) if m else 0, len(m["ds"]) if m else 0,
                      len(t.get("n2n", [])), len(t.get("np", [])), len(t.get("na", [])), 1 if n.get("valid") else 0,
                      n_use(m["cap"] + m["mxw"]) if m else 0, has_rr(Z, A)])
    for (Z, A), m in meas.items():
        if A == 0:  # natural element
            byz[Z]["nat"] = {"meas": {"ds": m["ds"], "cap": m["cap"], "mxw": m["mxw"], "other": dict(m["other"])}}
    nat = sorted(Z for Z in byz if "nat" in byz[Z])
    nfiles = 0
    for Z, d in byz.items():
        os.makedirs(os.path.join(OUT, "n", str(Z)), exist_ok=True)
        for key, rec in d.items():
            with open(os.path.join(OUT, "n", str(Z), f"{key}.json"), "w") as f:
                json.dump(rec, f, separators=(",", ":"))
            nfiles += 1
    with open(os.path.join(OUT, "index.json"), "w") as f:
        json.dump({"cols": ["Z", "A", "tier", "macs30_mb", "unc68_30", "n_cap", "n_mxw", "n_ds", "n_n2n", "n_np", "n_na", "valid", "n_use", "rr"],
                   "tiers": TIERS, "sym": SYM, "grid_ev": grid, "kT_keV": KT, "natural": nat, "lib": lib_z, "rows": index},
                  f, separators=(",", ":"))
    tot = sum(os.path.getsize(os.path.join(dp, x)) for dp, _, fs in os.walk(os.path.join(OUT, "n")) for x in fs)
    print(f"{len(index)} nuclides, {nfiles} nuclide files ({tot / 1e6:.1f} MB), "
          f"index {os.path.getsize(os.path.join(OUT, 'index.json')) / 1e3:.0f} kB, "
          f"measured capture on {sum(1 for k in meas if k[1] > 0)} nuclides + {len(nat)} natural elements "
          f"({n_iso} cells on isomeric targets not shown); comparison files: lib for {len(lib_z)} elements, "
          f"rr for {sum(r[13] for r in index)} nuclides")
    light = [r for r in index if r[0] < 26]
    print(f"Z 1-25: {len(light)} nuclides, {sum(1 for r in light if r[12] > 0)} measured (n_use > 0), "
          f"{sum(1 for r in light if r[5] + r[6] > 0 and r[12] == 0)} with only excluded cells; "
          f"(n,2n) / (n,p) / (n,alpha) measured on {sum(1 for r in light if r[8])} / {sum(1 for r in light if r[9])} / "
          f"{sum(1 for r in light if r[10])} nuclides ({sum(r[8] for r in light)} / {sum(r[9] for r in light)} / {sum(r[10] for r in light)} points)")
    # light-nuclide R-matrix evaluations that passed their gates (data/light_evals; scripts/add_light_evals.py)
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import add_light_evals
    add_light_evals.apply(OUT)


if __name__ == "__main__":
    main()
