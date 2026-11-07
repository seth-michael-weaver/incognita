"""Measured (n,2n), (n,p) and (n,alpha) points for the light nuclides H..Mn (Z 1-25), with the benchmark rows' rules.

The site's threshold-channel points for Z 24-92 are the benchmark rows (incognita/bench/data/exam_rows/{n2n,np,na}_rows),
cut from the research repository's channel scoreboard rows (research/scripts/channels/score_channels.py --amend, rule
set "A1", docs/release/channels_v0/rows_A1.parquet). This script applies the same rules to Z 1-25 and writes

  data/curation/inputs/exfor_threshold_Z1-25_rows.parquet      one row per EXFOR series and engine energy bin
                                                                (columns of the benchmark n2n_rows / np_rows)
  data/curation/inputs/exfor_threshold_Z1-25_provenance.json   inputs (SHA256), rule counts, checks

Steps (inside the research checkout given by --main, default ~/nucleus; nothing there is written):
  1. Stage. From the full staged EXFOR table of the 2026-10-14 entry.zip (staging/exfor_all_2026-10-14_x4fix1), the
     predicate and 20 MeV clip of `python -m data.ingest.exfor --subset n2n|np|na` (SF2 = N, SF3 = 2N | P | A,
     SF6 = SIG). The same procedure on Z 26-92 must reproduce staging/exfor_<ch>_Z26-92_2026-10-14_x4fix1 exactly,
     or the build stops.
  2. Rules of score_channels.py exfor_rows() and its A1 amendment, unchanged: quantity cross_section; EXFOR outdated flag
     not set; a single isotope (A > 0) in its ground state; SF5, SF7, SF8 empty; no isomer suffix (-G, -M, -Mn) on the
     product; no V-entry (evaluated compilation); points with sigma > 0, sigma >= 1 mb (threshold channels), energy
     <= 20 MeV and >= max(1 keV, the upper end of the resolved / unresolved resonance range of ENDF/B-VIII.1, else
     TENDL-2025, for the nucleus; a nucleus in neither library is dropped). Values: the staged renormalised block (barns).
     Plus the REACTION-code check that corrected these rules afterwards (research scripts/channels/score_channels_fixed.py
     reaction_flags, the v5b data fix registered 2026-09-23, applied to every leaf of the REACTION string): no product
     state or level suffix (-G, -M, -L, partial sums), no SF9 (DERIV, EVAL, CALC, RECOM), and no combination other than a
     sum over the states of one residual. It drops, for example, natural-target sums such as
     ((22-TI-46(N,P)21-SC-46,,SIG)+(22-TI-47(N,X)21-SC-46,,SIG,,RAB)), level-partial products such as
     13-AL-27(N,A)11-NA-24-L and DERIV series. The benchmark rows (Z 26-92) predate it; on them it would drop the rows
     counted under z26_92_check_vs_benchmark_rows.*.fixed_rule_would_drop.
  3. Bins. As score_channels.py: one row per (series = subentry.pointer, engine energy bin) with the geometric-mean
     energy and the mean cross section; bins are the 64-point production-engine grid (1 keV-20 MeV) of the chart dumps.
     The scoreboard's engine and library predictions are not computed (a row needs no engine run here).
  Check printed at the end: the same code on Z 26-92 of the same snapshot against the shipped benchmark rows (which were
  cut from the 2026-09 snapshot), as the share of benchmark rows reproduced with the same value.

Version 1.1 (2026-11-07), two corrections applied after the staging check and before the rules (--v1 reproduces 1.0):
  - Centre-of-mass energies. Series whose incident energy is compiled as EN-CM (EN-RES-CM, EN-CM-MIN/-MAX) were staged
    with that number as the lab energy. They are found by parsing their entries with this repository's
    data/ingest/exfor.py and its opt-in fix "encm"; their energies are converted, E_lab = E_cm (A+1)/A (A = target mass
    number).
  - Review lines, data/curation/inputs/review_decisions_threshold_Z1-25.jsonl (format of the capture review files plus an
    optional "points" list of the EXFOR points a line applies to): exclude drops the series (or its listed points),
    fix-unit multiplies its values by "factor". Rows of a fix-unit series carry review = "fix-unit xFACTOR".

Reaction identities stay exact: SF3 = A is (n,alpha) with the residual the target + n - alpha; Li-6(n,t)He-4 is SF3 = T
and is not taken (ENDF puts Li-6 + n -> alpha + t in MT 105, (n,t)). A Li-6 SF3 = A series (residual H-3) would be the
same final state as (n,t) and is dropped and counted (rule LI6_NT).

usage (WSL, the research checkout's environment):
  cd ~/nucleus && uv run --no-sync python <this repo>/scripts/build_light_channels.py [--main ~/nucleus] [--work DIR]
"""
import argparse, collections, glob, hashlib, json, math, os, re, sys, time
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "data" / "curation" / "inputs"
EXAM = REPO / "incognita" / "bench" / "data" / "exam_rows"
ALL = "exfor_all_2026-10-14_x4fix1.parquet"
HEAVY = "exfor_{}_Z26-92_2026-10-14_x4fix1.parquet"
SF3 = {"n2n": "2N", "np": "P", "na": "A"}
EMAX = 20e6
ISOMER = re.compile(r"-(M\d?|G)$")  # score_channels.py ISOMER (product state suffix)
ENGINE = "~/nuc-local/capture/chart_s9_npz"
VERSION = "1.1"
REVIEW = OUT / "review_decisions_threshold_Z1-25.jsonl"


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def stage(main: Path):
    """{channel: (light pyarrow table, Z 26-92 pyarrow table)}; Z 26-92 checked against the shipped staging."""
    import pyarrow as pa, pyarrow.compute as pc, pyarrow.parquet as pq
    t = pq.read_table(main / "staging" / ALL)
    sf = t["sf"]
    up = lambda f: pc.utf8_upper(pc.fill_null(pc.struct_field(sf, f), ""))
    z = t["target_z"]

    def clip(rows):  # data.ingest.exfor._clip_energy
        out = []
        for r in rows:
            e = r["energy_ev"] or []
            keep = [i for i, x in enumerate(e) if x is not None and not math.isnan(x) and x <= EMAX]
            if e and len(keep) == len(e):
                out.append(r)
                continue
            if not keep:
                continue
            tk = lambda l: None if l is None else [l[i] for i in keep]
            r = dict(r)
            for c in ("energy_ev", "energy_sigma_ev", "angle_deg", "secondary_energy_ev"):
                r[c] = tk(r[c])
            for b in ("original", "renormalized"):
                if r[b] is not None:
                    r[b] = dict(r[b], values=tk(r[b]["values"]), stat_sigma=tk(r[b]["stat_sigma"]), sys_sigma=tk(r[b]["sys_sigma"]))
            out.append(r)
        return out

    def norm(T):
        fix = lambda v: ("nan" if isinstance(v, float) and math.isnan(v) else [fix(x) for x in v] if isinstance(v, list)
                         else {k: fix(x) for k, x in v.items()} if isinstance(v, dict) else v)
        return sorted((fix(r) for r in T.to_pylist()), key=lambda r: (r["subentry"], r["pointer"] or ""))

    res = {}
    for ch, code in SF3.items():
        base = pc.and_(pc.and_(pc.equal(up("sf2"), "N"), pc.equal(up("sf3"), code)), pc.equal(up("sf6"), "SIG"))
        sub = lambda a, b: pa.Table.from_pylist(
            clip(t.filter(pc.and_(base, pc.and_(pc.greater_equal(z, a), pc.less_equal(z, b)))).to_pylist()), schema=t.schema)
        heavy = pq.read_table(main / "staging" / HEAVY.format(ch)).cast(t.schema)
        if norm(sub(26, 92)) != norm(heavy):
            sys.exit(f"staging check FAILED: the {ch} predicate + clip does not reproduce " + HEAVY.format(ch))
        res[ch] = (sub(1, 25), heavy)
        print(f"staged {ch}: {res[ch][0].num_rows} light measurements; Z 26-92 reproduces {heavy.num_rows} rows exactly", flush=True)
    return res


def encm_series(light: dict, main: Path) -> dict:
    """{"subentry/pointer": factor} of the light series whose incident energy is a centre-of-mass energy: their entries
    are parsed with this repository's ingest and its opt-in fix "encm" (V2_LOG["encm"] lists what it converted)."""
    import zipfile
    sys.path.insert(0, str(REPO))
    from data.ingest import exfor as X
    assert Path(X.__file__).resolve().is_relative_to(REPO), X.__file__
    rows = {}
    for T in light.values():
        for r in T.select(["entry", "subentry", "pointer", "target_a", "projectile"]).to_pylist():
            rows[f"{r['subentry']}/{r['pointer'] or ''}"] = r
    entries = sorted({r["entry"] for r in rows.values()})
    X.V2_FIXES, out = frozenset({"encm"}), {}
    try:
        with zipfile.ZipFile(main / "raw" / "exfor" / "entry_2026-10-14.zip") as z:
            names = {n.rsplit("/", 1)[-1][:-4]: n for n in z.namelist() if n.endswith(".txt")}
            for e in entries:
                if e not in names:
                    continue
                text = z.read(names[e]).decode("latin-1")
                if "-CM" not in text:
                    continue
                X.V2_LOG.clear()
                X.build_measurements(X.parse_entry(text), collections.Counter(), [])
                for k in X.V2_LOG.get("encm", ()):
                    if k in rows and (rows[k]["projectile"] or "").upper() == "N" and rows[k]["target_a"] > 0:
                        A = rows[k]["target_a"]
                        out[k] = (A + 1) / A
    finally:
        X.V2_FIXES = frozenset()
    return out


def read_review(path: Path) -> dict:
    """series key "subentry/pointer" -> review line (later lines override)."""
    out = {}
    for ln in path.read_text(encoding="utf-8").splitlines():
        if ln.strip() and not ln.lstrip().startswith("#"):
            d = json.loads(ln)
            assert d["decision"] in ("exclude", "fix-unit"), d
            assert d["decision"] != "fix-unit" or d.get("factor"), d
            out[f"{d['subentry']}/{d.get('pointer') or ''}"] = d
    return out


def correct(T, cm: dict, review: dict, cnt):
    """Apply the centre-of-mass conversion and the review lines to a staged pyarrow table (returns a new table)."""
    import pyarrow as pa
    rows = []
    for r in T.to_pylist():
        k = f"{r['subentry']}/{r['pointer'] or ''}"
        if k in cm:
            f = cm[k]
            r["energy_ev"] = [None if x is None else x * f for x in r["energy_ev"]]
            if r["energy_sigma_ev"] is not None:
                r["energy_sigma_ev"] = [None if x is None else x * f for x in r["energy_sigma_ev"]]
            cnt["encm_series"] += 1
            cnt["encm_points"] += len(r["energy_ev"])
        d = review.get(k)
        r["_review"] = ""
        if d is not None and d["decision"] == "exclude" and not d.get("points"):
            cnt["review_excluded_series"] += 1
            continue
        if d is not None and d["decision"] == "exclude":
            drop = [i for i, e in enumerate(r["energy_ev"]) for p in d["points"]
                    if e is not None and abs(e / p["e_ev"] - 1) < 1e-6]
            keep = [i for i in range(len(r["energy_ev"])) if i not in drop]
            assert len(drop) == len(d["points"]), (k, drop)
            cnt["review_excluded_points"] += len(drop)
            tk = lambda l: None if l is None else [l[i] for i in keep]
            for c in ("energy_ev", "energy_sigma_ev", "angle_deg", "secondary_energy_ev"):
                r[c] = tk(r[c])
            for b in ("original", "renormalized"):
                if r[b] is not None:
                    r[b] = dict(r[b], values=tk(r[b]["values"]), stat_sigma=tk(r[b]["stat_sigma"]), sys_sigma=tk(r[b]["sys_sigma"]))
        if d is not None and d["decision"] == "fix-unit":
            f = float(d["factor"])
            for b in ("original", "renormalized"):
                if r[b] is not None:
                    sc = lambda l: None if l is None else [None if x is None else x * f for x in l]
                    r[b] = dict(r[b], values=sc(r[b]["values"]), stat_sigma=sc(r[b]["stat_sigma"]), sys_sigma=sc(r[b]["sys_sigma"]))
            r["_review"] = f"fix-unit x{f:g}"
            cnt["review_fix_unit_series"] += 1
        rows.append(r)
    sch = T.schema.append(pa.field("_review", pa.string()))
    return pa.Table.from_pylist(rows, schema=sch)


def lower_bounds(main: Path, zmin, zmax):
    """score_channels.load_libs: upper end of the resonance range per (Z, A), ENDF/B-VIII.1 first, else TENDL-2025."""
    import pandas as pd
    lower = {}
    for stem in ("tendl2025", "endfb81"):  # later overrides earlier: VIII.1 wins where it has the nucleus
        d = pd.read_parquet(main / "staging" / "evaluated" / f"{stem}.parquet",
                            columns=["Z", "N", "iso", "mt", "resolved_upper_ev", "unresolved_upper_ev"])
        d = d[(d.iso == 0) & (d.mt == 1) & d.Z.between(zmin, zmax)]
        for r in d.itertuples():
            lower[(int(r.Z), int(r.Z + r.N))] = float(np.nanmax([r.resolved_upper_ev, r.unresolved_upper_ev, 0.0]))
    return lower


def load_flags(main: Path):
    import importlib.util
    spec = importlib.util.spec_from_file_location("score_channels_fixed", main / "research" / "scripts" / "channels" / "score_channels_fixed.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.reaction_flags


def rows_for(ch, T, lower, edges, cnt, flags=None):
    """score_channels.py exfor_rows() + the A1 amendment + the per-point cuts and binning of its main loop."""
    out = []
    for r in T.to_pylist():
        s_ = r["sf"]
        cnt["subentries"] += 1
        if not (r["quantity"] == "cross_section" and not r["outdated"] and r["target_a"] > 0 and r["target_iso"] == 0
                and not s_["sf5"] and not s_["sf7"] and not s_["sf8"] and not ISOMER.search(s_["sf4"] or "")):
            cnt["rule_filter"] += 1
            continue
        if str(r["entry"]).upper().startswith("V"):
            cnt["v_entry"] += 1
            continue
        if flags is not None:
            fl = flags(r["reaction"], r["entry"])
            if fl:
                cnt["reaction_code"] += 1
                for f in fl:
                    cnt["reaction_code:" + re.sub(r"[:\-].*", "", f)] += 1
                continue
        z, A = int(r["target_z"]), int(r["target_a"])
        if ch == "na" and (z, A) == (3, 6):  # Li-6 + n -> alpha + t is (n,t) (MT 105), not (n,alpha)
            cnt["li6_nt"] += 1
            continue
        lo = lower.get((z, A))
        if lo is None:
            cnt["no_lower"] += 1
            continue
        blk = r["renormalized"] if isinstance(r["renormalized"], dict) else None
        if blk is None:  # score_channels falls back to the original block; only safe when it is in barns
            if (r["original"] or {}).get("units", "").upper() != "B":
                cnt["no_barns"] += 1
                continue
            blk = r["original"]
        e = np.atleast_1d(np.asarray(r["energy_ev"], float))
        s = np.atleast_1d(np.asarray([np.nan if v is None else v for v in blk["values"]], float)) * 1e3  # b -> mb
        if e.shape != s.shape:
            cnt["shape"] += 1
            continue
        ok = np.isfinite(e) & np.isfinite(s) & (s > 0) & (e >= max(1e3, lo)) & (e <= 2e7) & (s >= 1.0)
        if not ok.any():
            cnt["no_points"] += 1
            continue
        cnt["kept"] += 1
        cnt["pts"] += int(ok.sum())
        e, s = e[ok], s[ok]
        b = np.searchsorted(edges, e)
        for bi in np.unique(b):
            m = b == bi
            out.append(dict(channel=ch, Z=z, A=A, series=f"{r['subentry']}.{r['pointer']}".replace(".None", ".nan"), bin=int(bi),
                            e_ev=float(np.exp(np.log(e[m]).mean())), n_pts=int(m.sum()), data_mb=float(s[m].mean()),
                            year=int(r["year"]) if r["year"] is not None else -1,
                            reaction=r["reaction"], first_author=r["first_author"] or "", review=r.get("_review") or ""))
    return out


def main():
    import pandas as pd
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--main", type=Path, default=Path("~/nucleus").expanduser())
    ap.add_argument("--v1", action="store_true", help="version 1.0: no centre-of-mass conversion, no review lines")
    a = ap.parse_args()
    staged = stage(a.main)
    review = {} if a.v1 else read_review(REVIEW)
    cm = {} if a.v1 else encm_series({ch: L for ch, (L, _) in staged.items()}, a.main)
    corr = collections.Counter()
    staged = {ch: (correct(L, cm, review, corr), H) for ch, (L, H) in staged.items()}
    print("v1.1 corrections:", dict(corr), "centre-of-mass series:", sorted(cm), flush=True)
    grid = np.asarray(np.load(sorted(glob.glob(os.path.expanduser(ENGINE + "/*.npz")))[0], allow_pickle=True)["e_ev"], float)
    for f in sorted(glob.glob(os.path.expanduser(ENGINE + "/*.npz")))[::500]:
        assert np.allclose(np.load(f, allow_pickle=True)["e_ev"], grid), f
    edges = np.sqrt(grid[:-1] * grid[1:])
    low_lo, heavy_lo = lower_bounds(a.main, 1, 25), lower_bounds(a.main, 26, 92)
    flags = load_flags(a.main)

    rows, counts, check = [], {}, {}
    for ch, (light, heavy) in staged.items():
        c = collections.Counter()
        rows += rows_for(ch, light, low_lo, edges, c, flags)
        counts[ch] = dict(c)
        # check: the same code on Z 26-92 (2026-10-14 staging) against the shipped benchmark rows (2026-09 staging)
        H = pd.DataFrame(rows_for(ch, heavy, heavy_lo, edges, collections.Counter()))
        E = pd.read_parquet(EXAM / f"{ch}_rows.parquet")
        if ch == "na":
            E = E[E.src == "rows_A1"]
        if "bin" not in E:  # na_rows carries no bin column: match on the bin's mean energy
            E, H = E.assign(bin=np.round(np.log(E.e_ev), 6)), H.assign(bin=np.round(np.log(H.e_ev), 6))
        k = ["Z", "A", "series", "bin"]
        m = E.merge(H[k + ["data_mb"]], on=k, how="left", suffixes=("", "_new"))
        same = int((np.abs(m.data_mb_new / m.data_mb - 1) < 1e-6).sum())
        Hf = pd.DataFrame(rows_for(ch, heavy, heavy_lo, edges, collections.Counter(), flags))
        if "bin" not in E.columns or ch == "na":
            Hf = Hf.assign(bin=np.round(np.log(Hf.e_ev), 6))
        drop = int((~E.set_index(k).index.isin(Hf.set_index(k).index)).sum())
        check[ch] = {"benchmark_rows": len(E), "reproduced_same_value": same, "share": round(same / len(E), 4),
                     "new_code_rows_z26_92": len(H), "fixed_rule_would_drop": drop}
        print(ch, counts[ch], check[ch], flush=True)

    R = pd.DataFrame(rows).sort_values(["channel", "Z", "A", "series", "bin"]).reset_index(drop=True)
    R = R.astype({"Z": "int64", "A": "int64", "bin": "int64", "n_pts": "int64", "year": "int64"})
    if a.v1:
        R = R.drop(columns=["review"])
    out = OUT / "exfor_threshold_Z1-25_rows.parquet"
    R.to_parquet(out, index=False)
    per = {ch: {"rows": int((R.channel == ch).sum()), "series": int(R[R.channel == ch].series.nunique()),
                "nuclides": sorted(f"{z}-{A}" for z, A in set(zip(R[R.channel == ch].Z, R[R.channel == ch].A)))} for ch in SF3}
    prov = {
        "version": "1.0" if a.v1 else VERSION,
        "built": time.strftime("%Y-%m-%d"),
        "script": "scripts/build_light_channels.py",
        "rules": "research scripts/channels/score_channels.py exfor_rows() + amendment A1 (the rules of the benchmark rows "
                 "incognita/bench/data/exam_rows, ch-n2n / ch-np / ch-na), applied to Z 1-25, plus the v5b REACTION-code check "
                 "(score_channels_fixed.reaction_flags); Li-6 SF3=A would be dropped as (n,t) (rule li6_nt)",
        "staging": {"source": f"staging/{ALL}", "entry_zip": "2026-10-14", "sha256": sha(a.main / "staging" / ALL),
                    "check": "same predicate + clip on Z 26-92 reproduces staging/" + HEAVY.format("<ch>") + " exactly"},
        "engine_grid": f"{len(grid)} points {grid[0]:.0f}-{grid[-1]:.0f} eV (chart_s9_npz e_ev)",
        "filter_counts": counts,
        "v1_1_corrections": None if a.v1 else {
            "centre_of_mass_energy": {"rule": "E_lab = E_cm (A+1)/A (exfor.py fix encm), applied to the staged series",
                                      "series": {k: round(f, 6) for k, f in sorted(cm.items())},
                                      "series_in_rows": sorted(set(R.series) & {(k[:-1] + ".nan") if k.endswith("/") else k.replace("/", ".") for k in cm})},
            "review_file": {"path": "data/curation/inputs/" + REVIEW.name, "sha256": sha(REVIEW), "lines": len(review)},
            "counts": dict(corr)},
        "per_channel": per,
        "z26_92_check_vs_benchmark_rows": check,
    }
    (OUT / "exfor_threshold_Z1-25_provenance.json").write_text(json.dumps(prov, indent=1) + "\n")
    print(json.dumps({k: v for k, v in prov.items() if k != "per_channel"}, indent=1))
    for ch in SF3:
        print(ch, per[ch]["rows"], "rows", per[ch]["series"], "series", len(per[ch]["nuclides"]), "nuclides:", " ".join(per[ch]["nuclides"]))


if __name__ == "__main__":
    main()
