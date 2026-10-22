"""Build the data files of the website's Data explorer (docs/walkthrough/data/).

Reads the v0.1 library (engine/library curves for every nuclide) and the curated EXFOR capture cells, plus the benchmark
rows for (n,2n), (n,p) and (n,alpha), and writes:
  data/index.json      one row per nuclide (chart of nuclides: tier, MACS at 30 keV, counts of measured data)
  data/n/<Z>/<A>.json  everything about one nuclide (<A> is "nat" for a natural element), fetched only when that
                       nuclide is opened; the chart itself needs only the index

usage:  uv run --no-project --with pyarrow python scripts/build_site_data.py
"""
import csv, json, math, os, re, shutil
from collections import defaultdict

import pyarrow.parquet as pq

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIB = os.path.join(ROOT, "library", "v0.1")
OUT = os.path.join(ROOT, "docs", "walkthrough", "data")

SYM = ("n H He Li Be B C N O F Ne Na Mg Al Si P S Cl Ar K Ca Sc Ti V Cr Mn Fe Co Ni Cu Zn Ga Ge As Se Br Kr Rb Sr Y Zr "
       "Nb Mo Tc Ru Rh Pd Ag Cd In Sn Sb Te I Xe Cs Ba La Ce Pr Nd Pm Sm Eu Gd Tb Dy Ho Er Tm Yb Lu Hf Ta W Re Os Ir Pt "
       "Au Hg Tl Pb Bi Po At Rn Fr Ra Ac Th Pa U Np Pu Am Cm Bk Cf Es Fm Md No Lr Rf Db Sg Bh Hs Mt Ds Rg Cn Nh Fl Mc Lv "
       "Ts Og").split()
TIERS = ["MEASURED", "ANCHORED", "INTERPOLATED", "EXTRAPOLATED"]
KT = [5, 8, 10, 15, 20, 25, 30, 40, 50, 60, 80, 100]
DEC = {"keep": "k", "downweight": "d", "exclude": "x", "fix-unit": "f"}


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
    """'Z028N032M0' -> (28, 60); 'Z036NAT' -> (36, 0)"""
    m = re.match(r"Z(\d+)N(\d+)", nuc)
    if m:
        return int(m.group(1)), int(m.group(1)) + int(m.group(2))
    m = re.match(r"Z(\d+)NAT", nuc)
    return (int(m.group(1)), 0) if m else (None, None)


def relerr(r):
    s, y, m = r.get("stat_rel"), r.get("sys_rel"), r.get("sem_rel")
    parts = [x for x in (s, y) if x is not None and not math.isnan(x)]
    if parts:
        return sig(math.sqrt(sum(x * x for x in parts)), 3)
    return sig(m, 3) if m is not None and not math.isnan(m) else None


def main():
    for old in ("z", "n"):  # data/z/<Z>.json was the per-element layout before per-nuclide files
        shutil.rmtree(os.path.join(OUT, old), ignore_errors=True)
    nucs = {}  # (Z, A) -> dict

    # ---- library curves ----
    cap = pq.read_table(os.path.join(LIB, "capture_v01_indep.parquet")).to_pylist()
    grid = [sig(e, 5) for e in cap[0]["energy_ev"]]
    for r in cap:
        assert [sig(e, 5) for e in r["energy_ev"]] == grid, "capture grids differ"
        nucs[(r["Z"], r["A"])] = {
            "tier": TIERS.index(r["tier"]), "valid": bool(r["in_validated_range"]),
            "cap": sigl(r["sigma_b"]), "u68": sigl(r["unc68_log10"], 3), "u95": sigl(r["unc95_log10"], 3),
            "res": sig(r["resolved_upper_ev"], 3), "macs30": sig(r["macs30_mb"]), "flag": r["macs30_flag"] or "",
            "src": r["value_source"] or "", "unc": r["unc_kind"] or "",
        }
    ch = pq.read_table(os.path.join(LIB, "channels_recipe_v01_indep.parquet")).to_pylist()
    for r in ch:
        n = nucs.get((r["Z"], r["A"]))
        if n is None:
            continue
        n["ch"] = {k: sigl(r[f"sigma_{k}_mb"]) for k in ("np", "n2n", "na") if r[f"sigma_{k}_mb"] is not None}
    npl = defaultdict(list)
    for r in pq.read_table(os.path.join(LIB, "grid_np_v01_indep.parquet")).to_pylist():
        if r["pred_mb"] is not None:
            npl[(r["Z"], r["A"])].append((r["E_MeV"] * 1e6, r["pred_mb"], r["lo68_mb"], r["hi68_mb"]))
    for k, rows in npl.items():
        if k in nucs:
            rows.sort()
            nucs[k]["npL"] = [[sig(a, 5), sig(b), sig(c), sig(d)] for a, b, c, d in rows]
    with open(os.path.join(LIB, "macs_kt_v01_indep.csv"), newline="") as f:
        for r in csv.DictReader(f):
            n = nucs.get((int(r["Z"]), int(r["A"])))
            if n is None:
                continue
            fl = lambda s: sig(float(s)) if s not in ("", None) else None
            n["macs"] = [fl(r[f"macs{t}_mb"]) for t in KT]
            n["macsU"] = [fl(r[f"unc68_factor_{t}keV"]) for t in KT]

    # ---- measured capture (curated EXFOR cells) ----
    meta = {}
    for r in pq.read_table(os.path.join(ROOT, "data", "curation", "inputs", "exfor_capture_Z26-92_trust.parquet"),
                           columns=["dataset_key", "first_author", "year", "facility"]).to_pylist():
        meta[r["dataset_key"]] = (r["first_author"] or "", r["year"], r["facility"] or "")
    meas = defaultdict(lambda: {"ds": [], "dsi": {}, "cap": [], "mxw": [], "other": defaultdict(int)})
    for r in pq.read_table(os.path.join(ROOT, "data", "curation", "inputs", "exfor_cells.parquet")).to_pylist():
        Z, A = za(r["nuclide"])
        if Z is None:
            continue
        m = meas[(Z, A)]
        key = r["dataset_key"]
        if key not in m["dsi"]:
            au, yr, fac = meta.get(key, ("", r["year"], ""))
            m["dsi"][key] = len(m["ds"])
            m["ds"].append([key, au, yr if yr is not None else r["year"], fac])
        i, kind = m["dsi"][key], r["kind"]
        pt = [sig(r["e_lo_ev"], 5), sig(r["e_hi_ev"], 5), sig(r["mean_b"]), relerr(r), i, DEC.get(r["decision"], "k"), r["state"] or ""]
        if kind in ("sig", "av"):
            m["cap"].append(pt)
        elif kind == "mxw":
            m["mxw"].append(pt)
        else:
            m["other"][kind] += 1

    # ---- measured threshold channels (benchmark rows) ----
    thr = defaultdict(lambda: defaultdict(list))
    for ch_, fn in (("n2n", "n2n_rows"), ("np", "np_rows"), ("na", "na_rows")):
        for r in pq.read_table(os.path.join(ROOT, "incognita", "bench", "data", "exam_rows", fn + ".parquet")).to_pylist():
            series = str(r.get("series") or "").replace(".nan", "")
            thr[(r["Z"], r["A"])][ch_].append([sig(r["e_ev"], 5), sig(r["data_mb"]), series, r.get("year")])

    # ---- write ----
    keys = set(nucs) | {k for k in meas if k[1] > 0} | set(thr)
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
                      len(t.get("n2n", [])), len(t.get("np", [])), len(t.get("na", [])), 1 if n.get("valid") else 0])
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
        json.dump({"cols": ["Z", "A", "tier", "macs30_mb", "unc68_30", "n_cap", "n_mxw", "n_ds", "n_n2n", "n_np", "n_na", "valid"],
                   "tiers": TIERS, "sym": SYM, "grid_ev": grid, "kT_keV": KT, "natural": nat, "rows": index},
                  f, separators=(",", ":"))
    tot = sum(os.path.getsize(os.path.join(dp, x)) for dp, _, fs in os.walk(os.path.join(OUT, "n")) for x in fs)
    print(f"{len(index)} nuclides, {nfiles} nuclide files ({tot / 1e6:.1f} MB), "
          f"index {os.path.getsize(os.path.join(OUT, 'index.json')) / 1e3:.0f} kB, "
          f"measured capture on {sum(1 for k in meas if k[1] > 0)} nuclides + {len(nat)} natural elements")


if __name__ == "__main__":
    main()
