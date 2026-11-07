"""Curated EXFOR capture set v2 (CAPSET-v2): the WP-12 curation re-run on a corrected staging, Z 1-92.

The shipped capture tables (data/curation/inputs/: Z 26-92 run on 2026-09-12, Z 1-25 run on 2026-11-06) carry ingestion
defects found by a read-only hunt on 2026-11-06. This script fixes them and writes a NEW versioned product to
data/curation/capture_v2/ (the old files are not touched). Every decision it adds is a review-decision line with a reason
and the EXFOR id (review_decisions_capture_v2.jsonl); nothing is deleted silently. README.md there lists every fix with
its counts before and after; ADOPTION.md says what would change downstream.

Fixes (numbers = the defect list of the 2026-11-06 hunt):
  D1 numfix    Fortran numbers "5.     -07" read as NaN (data/ingest/exfor.py _NUM_FIX).
  D2 parser    RATIO heading; EN-MIN-APX; KT-K in DEG-C; "(N,ABS)=(N,G)" equivalences filed under (N,G).
  D3 sums      REACTION combinations that are not one capture cross section (sums over targets / processes, weighted
               state sums such as G + 1.006 M x FCT) are excluded with the REACTION-code rule of
               research/scripts/channels/score_channels_fixed.reaction_flags (flags COMBO_SUM / COMBO_DIFF / COMBO_PROD).
  D4 unc       stat = ERR-S, sys = ERR-SYS or sqrt(ERR-T^2 - ERR-S^2); stat = sqrt(ERR-T^2 - ERR-SYS^2); an unsplit
               total stays stat_sigma (as v1). Peelle: absolute-unit uncertainties are re-based on the expected value of a
               first fit (sigma / exp(mu + bias) instead of sigma / observed mean) before the final fit.
  D5 dupes     a dataset whose EXFOR STATUS says (SPSDD,X) or (DEP,X), where X is in the set with the same comparable
               quantity, is excluded (also across entries) and left out of the consensus fit; STATUS PRELM -> downweight.
  D6 slips     three x1000-type slips reviewed by hand (lines with reasons).
  D7 version   exfor_version is the snapshot actually read (2026-10-14), not the hard-coded 2026-08-27.

Steps (inside the research checkout --main, default ~/nucleus; nothing there is written):
  1. Stage three times from raw/exfor/entry_2026-10-14.zip with this repository's data/ingest/exfor.py: v1 behaviour
     (no fix), numfix only, all fixes. Capture predicate and 20 MeV clip of `python -m data.ingest.exfor --subset
     capture`, Z 1-92. Checks: the numfix-only Z 26-92 staging against the research staging
     staging/exfor_capture_Z26-92_2026-10-14_x4fix1 (the 2026-10-22 X4NUMFIX output).
  2. Rule lines (D3, D5 SPSDD/DEP) and the hand lines (D6), then quality_model.run (research data/curate, unchanged,
     with this repository's data/curate/discrepancy.py) on Z 1-92 with the human-decision file = research
     review_decisions.jsonl + data/curation/inputs/review_decisions_Z1-25.jsonl + the CAPSET-v2 lines. The consensus fit
     leaves out the cells of datasets excluded by a CAPSET-v2 rule line (as it already leaves out compilations).
  3. PRELM lines (only where pass 1 kept or down-weighted the dataset and no earlier human line names it), pass 2.
  4. Cells (discrepancy.cells_from_parquet on the v2 staging) joined to the trust table; split Z 1-25 / Z 26-92 into
     files with the shipped schemas; counts, provenance, SHA256SUMS.

usage (WSL, the research checkout's environment):
  cd ~/nucleus && INCOGNITA_MAIN=~/nucleus .venv/bin/python <this repo>/scripts/build_capture_v2.py [--main ~/nucleus] [--work DIR]
"""
from __future__ import annotations

import argparse, collections, hashlib, json, math, os, re, subprocess, sys, time, zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "data" / "curation" / "capture_v2"
INP = REPO / "data" / "curation" / "inputs"
ZIPNAME = "entry_2026-10-14.zip"
RESEARCH_STAGING = "exfor_capture_Z26-92_2026-10-14_x4fix1.parquet"
EMAX = 20e6
TAG = "exfor_capture_Z1-92_v2"
DATE = "2026-11-06"
REVIEWER_RULE = "rule:capset-v2"
REVIEWER_HAND = "agent:claude-opus-5.5"
COMBO_EXCLUDE = ("COMBO_SUM", "COMBO_DIFF", "COMBO_PROD")
PEELLE_CLIP = 3.0  # the re-basing factor mean/consensus is clipped to [1/3, 3]

# D6: hand-reviewed x1000-type slips (checked against the EXFOR record of the 2026-10-14 entry.zip)
HAND = [
    {"entry": "14657", "subentry": "14657002", "pointer": "", "decision": "fix-unit", "factor": 0.001,
     "reason": "Y-89(n,g)Y-90m thermal Maxwellian (SIG,,MXW), Krane 2020, EXFOR 14657002: DATA 1.02 / 0.98 / 1.06 B with "
               "ERR-T 0.01-0.03 B for three irradiation positions. The other EXFOR measurements of the same isomeric thermal "
               "cross section are 1 mb: Heath 1961 11870002 (0.001 B, MXW), De Corte 1988 23488032 (0.00104 B), Farina "
               "Arbocco 2013 23266090/91 (0.00107 B). The compiled unit B is a x1000 slip for MB. fix-unit, factor 0.001 "
               "(trust 0 until the correction is applied at ingest)."},
    {"entry": "13947", "subentry": "13947004", "pointer": "", "decision": "fix-unit", "factor": 0.001,
     "reason": "Ni-60(n,g)Ni-61 partial gamma-ray cross sections (PAR,SIG,,MXW), Raman et al. 2004, EXFOR 13947004 (Table 10): "
               "240 gamma lines compiled in B that sum to 3693 B (e.g. 812 B at E-gamma 283 keV), while the same quantity "
               "from Gippner 1971 (30150003, 31 lines compiled in MB) sums to 2744 MB; a thermal capture cross section of a "
               "few barns times a gamma multiplicity of a few cannot give thousands of barns of gamma lines. The values are "
               "millibarns. fix-unit, factor 0.001."},
    {"entry": "41639", "subentry": "41639002", "pointer": "", "decision": "exclude",
     "reason": "Sb-124(n,g)Sb-125 spectrum average (SIG,,SPA), Murin 1957 (At. Energy 2, 552), EXFOR 41639002: one DATA-APRX "
               "value 2000 B with no uncertainty, at an incident energy the compiler supposed (COMMENT: 'Incident neutron "
               "energy is not given in the article, supposed by compiler as 0.0253 eV'; HISTORY 2021 changed EN-DUMMY from "
               "1 MeV). Excluded on the record: an approximate value of a quantity whose energy is not defined. It is NOT "
               "proven to be a unit slip: Courtemanche 1966 (11990002, SPA) gives 6.5 B, x300 lower, but Elgart 1971 "
               "(10728004, MXW) gives 2990 B, the same magnitude as this value, so EXFOR alone does not settle Sb-124; "
               "10728004 and 11990002 are left to the automatic layer and listed for a person to read."},
]


def sha(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def setup(main: Path):
    """This repository's data package first (patched exfor.py, discrepancy.py); the research data/curate modules that
    are not here (quality_model, review_log) are found by extending the package path."""
    sys.path.insert(0, str(REPO))
    import data.curate, data.ingest  # noqa: F401
    data.curate.__path__.append(str(main / "data" / "curate"))
    from data.curate import standards as std, discrepancy as disc
    std.STANDARDS_DIR = main / "raw" / "standards" / "std2017"
    disc.REPO = main  # quality_model takes REPO from discrepancy: research review file, spot list (read-only)
    from data.curate import quality_model as qm
    assert qm.HUMAN_DECISIONS == main / "data" / "curate" / "review_decisions.jsonl", qm.HUMAN_DECISIONS
    sys.path.append(str(main / "research" / "scripts" / "channels"))


# ----------------------------------------------------------------------------------------------------- 1. staging

_REF = re.compile(r"\((SPSDD|DEP)\s*,([^)]*)\)")


def _refs(items) -> list[tuple[str, str]]:
    out = []
    for it in items or []:
        for flag, body in _REF.findall((it.code or "") + " " + (it.text or "")):
            for r in body.split(","):
                r = r.strip()
                if re.fullmatch(r"[0-9A-Z]{5}|[0-9A-Z]{8}", r):
                    out.append((flag, r))
    return out


def stage(main: Path, work: Path, tag: str, fixes: frozenset[str]) -> dict:
    """Parse every entry holding '(N,G)', keep capture (SF2 N, SF3 G, SF6 SIG/RI, Z 1-92), clip at 20 MeV."""
    import pyarrow as pa, pyarrow.parquet as pq
    from data.ingest import exfor as X
    out, logp = work / f"stage_{tag}.parquet", work / f"stage_{tag}.json"
    if out.exists() and logp.exists():
        return json.loads(logp.read_text())
    zp = main / "raw" / "exfor" / ZIPNAME
    X.V2_FIXES = frozenset(fixes)
    X.V2_LOG.clear()
    X.EXFOR_VERSION = X.exfor_version_of(zp) if fixes else "2026-08-27"
    keep = X._subset_filter("capture", 1, 92)
    writer = pq.ParquetWriter(out.with_suffix(".tmp"), X.ExforMeasurement.ARROW_SCHEMA, compression="zstd")
    stats, errs, buf, status = collections.Counter(), [], [], {}
    t0 = time.time()
    with zipfile.ZipFile(zp) as z:
        names = sorted(n for n in z.namelist() if n.endswith(".txt"))
        for name in names:
            text = z.read(name).decode("latin-1")
            if text.startswith("DICTION") or "(N,G)" not in text:
                continue
            stats["entries"] += 1
            e = X.parse_entry(text)
            first = e.subentries[0] if e.subentries and e.subentries[0].accession.endswith("001") else None
            ebib = first.bib if first else {}
            subs = {s.accession: s for s in e.subentries}
            for m in X.build_measurements(e, stats, errs):
                if not keep(m):
                    continue
                m2 = X._clip_energy(m, EMAX)
                if m2 is None:
                    stats["clipped_out"] += 1
                    continue
                buf.append(m2.to_row())
                s = subs[m.subentry]
                st = X._status_flags(s.bib.get("STATUS"), ebib.get("STATUS"))
                status[m.subentry] = {"refs": _refs(s.bib.get("STATUS")) + _refs(ebib.get("STATUS")),
                                      "prelm": "PRELM" in st}
            if len(buf) >= 2000:
                writer.write_table(pa.Table.from_pylist(buf, schema=X.ExforMeasurement.ARROW_SCHEMA))
                buf = []
    if buf:
        writer.write_table(pa.Table.from_pylist(buf, schema=X.ExforMeasurement.ARROW_SCHEMA))
    writer.close()
    out.with_suffix(".tmp").rename(out)
    info = {"tag": tag, "fixes": sorted(fixes), "exfor_version": X.EXFOR_VERSION, "seconds": round(time.time() - t0),
            "stats": {k: v for k, v in stats.items() if k in ("entries", "clipped_out", "subentries", "subentries_parsed")},
            "v2_log": {k: sorted(v) for k, v in X.V2_LOG.items()}, "status": status}
    logp.write_text(json.dumps(info))
    print(f"staged {tag}: {pq.read_metadata(out).num_rows} capture measurements, {info['seconds']} s", flush=True)
    return info


def summarize(path: Path):
    """dataset_key -> (z, n_points, n_finite_stat, n_finite_sys, reaction)."""
    import pyarrow.parquet as pq
    t = pq.read_table(path, columns=["entry", "subentry", "pointer", "target_z", "reaction", "energy_ev", "original"]).to_pylist()
    fin = lambda l: sum(1 for x in (l or []) if x is not None and x == x)
    return {f"{r['entry']}/{r['subentry']}/{r['pointer'] or ''}":
            (r["target_z"], len(r["energy_ev"] or []), fin(r["original"]["stat_sigma"]), fin(r["original"]["sys_sigma"]),
             r["reaction"]) for r in t}


def check_research_staging(main: Path, path: Path) -> dict:
    """numfix-only Z 26-92 staging vs the research X4NUMFIX staging (exfor_version aside)."""
    import pyarrow.parquet as pq
    import pyarrow.compute as pc
    ours = pq.read_table(path)
    ours = ours.filter(pc.greater_equal(ours["target_z"], 26))
    theirs = pq.read_table(main / "staging" / RESEARCH_STAGING)
    fix = lambda v: ("nan" if isinstance(v, float) and math.isnan(v) else [fix(x) for x in v] if isinstance(v, list)
                     else {k: fix(x) for k, x in v.items() if k != "exfor_version"} if isinstance(v, dict) else v)
    norm = lambda T: {f"{r['subentry']}/{r['pointer'] or ''}": fix(r) for r in T.to_pylist()}
    a, b = norm(ours), norm(theirs)
    diff = sorted(k for k in set(a) & set(b) if a[k] != b[k])
    return {"ours": len(a), "research": len(b), "only_ours": sorted(set(a) - set(b))[:50], "n_only_ours": len(set(a) - set(b)),
            "only_research": sorted(set(b) - set(a))[:50], "n_only_research": len(set(b) - set(a)),
            "n_differ": len(diff), "differ": diff[:50]}


# ----------------------------------------------------------------------------------------------- 2. rule lines


def line(key: str, decision: str, reason: str, rule: str, reviewer: str = REVIEWER_RULE, **extra) -> dict:
    entry, sub, ptr = key.split("/")
    return {"entry": entry, "subentry": sub, "pointer": ptr, "decision": decision, "rule": rule, "reason": reason,
            "reviewer": reviewer, "date": DATE, **extra}


def rule_lines(stg: Path, info: dict, prior: dict) -> tuple[list[dict], list[dict], dict]:
    """D3 sums + D6 hand lines, D5 SPSDD/DEP lines, and a per-dataset audit table. ``prior``: key -> earlier human
    Decision (research file + light file); a dataset an earlier line decides keeps that decision, and a dataset an
    earlier line excludes is not a valid 'original' for D5."""
    prior_keys = set(prior)
    gone = {k for k, d in prior.items() if d.decision in ("exclude", "fix-unit")}
    import pyarrow.parquet as pq
    from data.curate import discrepancy as disc
    from score_channels_fixed import reaction_flags
    t = pq.read_table(stg, columns=["entry", "subentry", "pointer", "target_z", "target_a", "target_id", "mt", "sf",
                                     "reaction", "energy_ev", "original", "renormalized"])
    idx = disc.index_table(t)
    keys = idx.dataset_key.tolist()
    groups = dict(zip(keys, idx.group_key.tolist()))
    rx = dict(zip(keys, t["reaction"].to_pylist()))
    sf9 = dict(zip(keys, [(x or "").upper() for x in t["sf"].combine_chunks().field("sf9").to_pylist()]))
    # a valid original for D5 is a measurement: not a V-entry compilation, not SF9 CALC / EVAL (auto-excluded anyway)
    not_meas = {k for k in keys if k.startswith("V") or sf9[k] in ("CALC", "EVAL")}
    lines, audit = [], {}
    hand = {f"{h['entry']}/{h['subentry']}/{h['pointer']}": h for h in HAND}
    for k in keys:
        fl = reaction_flags(rx[k], k.split("/")[0])
        combo = [f for f in fl if f in COMBO_EXCLUDE]
        audit[k] = {"reaction_flags": fl}
        if combo and k not in hand:
            lines.append(line(k, "exclude", f"CAPSET-v2 D3: REACTION {rx[k]!r} is a combination ({', '.join(combo)}) of "
                              "different targets, processes or weighted states, not one capture cross section; it was filed "
                              "under its first component. Flags of score_channels_fixed.reaction_flags: " + ", ".join(fl),
                              "D3_SUM_REACTION"))
    for k, h in hand.items():
        if k in groups:
            lines.append(line(k, h["decision"], "CAPSET-v2 D6: " + h["reason"], "D6_HAND_SLIP", REVIEWER_HAND,
                              **({"factor": h["factor"]} if "factor" in h else {})))
    excluded = {l["entry"] + "/" + l["subentry"] + "/" + l["pointer"] for l in lines} | gone
    lines36, lines = lines, []
    # D5: SPSDD / DEP references to a dataset of the same comparable quantity
    by_sub = collections.defaultdict(list)
    for k in keys:
        by_sub[k.split("/")[1]].append(k)
    by_entry = collections.defaultdict(list)
    for k in keys:
        by_entry[k.split("/")[0]].append(k)
    cand = {}
    for k in keys:
        sub = k.split("/")[1]
        if k in not_meas:  # a compilation / calculated dataset is excluded by the automatic layer already
            continue
        for flag, ref in info["status"].get(sub, {}).get("refs", []):
            targets = by_sub.get(ref, []) if len(ref) == 8 else by_entry.get(ref, [])
            same = [q for q in targets if q != k and groups[q] and groups[q] == groups[k] and q not in excluded
                    and q not in not_meas]
            if same:
                cand.setdefault(k, (flag, ref, same))
    dropped = set()
    for k in sorted(cand):
        flag, ref, same = cand[k]
        if all(q in dropped for q in same):  # mutual reference: never drop both members
            audit[k]["d5_skipped"] = "every referenced dataset is itself dropped (mutual reference)"
            continue
        if k in prior_keys:
            audit[k]["d5_skipped"] = "an earlier human review line decides this dataset"
            continue
        if k in hand:
            continue
        dropped.add(k)
        cross = ref[:5] != k.split("/")[0]
        what = ("superseded by" if flag == "SPSDD" else "dependent on (derived from)")
        lines.append(line(k, "exclude", f"CAPSET-v2 D5: EXFOR STATUS ({flag},{ref}): this dataset is {what} "
                          f"{', '.join(same)}, which is in the set with the same comparable quantity ({groups[k]}); counting "
                          f"both counts one measurement twice{' (cross-entry pair)' if cross else ''}. The referenced "
                          "dataset carries the measurement.", "D5_SPSDD" if flag == "SPSDD" else "D5_DEP",
                          superseded_by=same[0], cross_entry=cross))
    for k in keys:
        audit[k]["group_key"] = groups[k]
    return lines36, lines, audit


def prelm_lines(info: dict, q1, prior_keys: set[str], decided: set[str]) -> list[dict]:
    out = []
    for r in q1.select("dataset_key", "subentry", "decision").iter_rows(named=True):
        k = r["dataset_key"]
        if k.startswith("STD2017") or k in prior_keys or k in decided:
            continue
        if info["status"].get(r["subentry"], {}).get("prelm") and r["decision"] in ("keep", "downweight"):
            out.append(line(k, "downweight", "CAPSET-v2 D5: EXFOR STATUS PRELM (preliminary data, not the final published "
                            "result). Rule: preliminary data are down-weighted (trust x0.25) wherever the automatic layer "
                            f"kept or down-weighted them (pass-1 decision: {r['decision']}).", "D5_PRELM"))
    return out


def write_jsonl(path: Path, lines: list[dict], header: str):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(header)
        for l in lines:
            f.write(json.dumps(l, ensure_ascii=False) + "\n")


# ------------------------------------------------------------------------------------------------- 3. curation


def run_qm(stg: Path, work: Path, hd: Path, fit_excluded: set[str], peelle: set[str], name: str):
    """quality_model.run with the consensus fit (i) leaving out fit_excluded datasets and (ii) re-basing the uncertainty
    of absolute-unit datasets (peelle) on the expected value exp(mu + bias) of a first fit."""
    import numpy as np, polars as pl
    from data.curate import discrepancy as disc
    from data.curate import quality_model as qm
    orig = disc.fit_scatter_model
    pstat = collections.Counter()

    def fit(cells, cfg=None):
        cells = cells.filter(~pl.col("dataset_key").is_in(sorted(fit_excluded)))
        f1 = orig(cells, cfg)
        if not peelle:
            return f1
        # expected value of the cell = consensus x the dataset's own normalisation, exp(mu + bias) (d'Agostini / Peelle)
        b = f1.cells.select("dataset_key", "bin", (pl.col("mu") + pl.col("bias")).alias("_mu")).unique(["dataset_key", "bin"])
        c = cells.join(b, on=["dataset_key", "bin"], how="left", maintain_order="left")
        absu = c["dataset_key"].is_in(sorted(peelle)).to_numpy()
        mu = c["_mu"].to_numpy()
        ok = absu & np.isfinite(mu) & (c["mean_b"].to_numpy() > 0)
        fac = np.where(ok, np.clip(c["mean_b"].to_numpy() / np.exp(np.where(ok, mu, 0.0)), 1 / PEELLE_CLIP, PEELLE_CLIP), 1.0)
        pstat["cells_rebased"] = int(ok.sum())
        pstat["cells_abs_units"] = int(absu.sum())
        pstat["median_abs_log_factor_x1000"] = int(1000 * float(np.median(np.abs(np.log(fac[ok]))))) if ok.any() else 0
        c = c.with_columns((pl.col("stat_rel") * pl.Series(fac)).alias("stat_rel"),
                           (pl.col("sys_rel") * pl.Series(fac)).alias("sys_rel")).drop("_mu")
        return orig(c, cfg)

    disc.fit_scatter_model = fit
    try:
        res = qm.run(stg, work / name, tag=TAG, verbose=True, human_decisions=hd)
    finally:
        disc.fit_scatter_model = orig
    print(f"{name}: peelle {dict(pstat)}", flush=True)
    return res, dict(pstat)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--main", type=Path, default=Path("~/nucleus").expanduser())
    ap.add_argument("--work", type=Path, default=Path("~/capv2_work").expanduser())
    ap.add_argument("--stage-only", action="store_true")
    a = ap.parse_args()
    a.work.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    setup(a.main)
    import numpy as np, polars as pl
    from data.ingest import exfor as X

    # 1. staging
    i_v1 = stage(a.main, a.work, "v1", frozenset())
    i_nf = stage(a.main, a.work, "numfix", frozenset({"numfix"}))
    i_v2 = stage(a.main, a.work, "v2", X.V2_ALL)
    stg = a.work / "stage_v2.parquet"
    chk = check_research_staging(a.main, a.work / "stage_numfix.parquet")
    print("research staging check:", {k: v for k, v in chk.items() if not isinstance(v, list)}, flush=True)
    if a.stage_only:
        return

    # 2. lines
    from data.curate import quality_model as qm
    from data.curate import review_log as rl
    light_review = INP / "review_decisions_Z1-25.jsonl"
    prior_text = qm.HUMAN_DECISIONS.read_text(encoding="utf-8").rstrip("\n") + "\n" + light_review.read_text(encoding="utf-8")
    pf = a.work / "prior_human.jsonl"
    pf.write_text(prior_text, encoding="utf-8")
    prior = rl.parse_decisions_jsonl(pf)
    lines36, lines5, audit = rule_lines(stg, i_v2, prior)
    kk = lambda ls: {f"{l['entry']}/{l['subentry']}/{l['pointer']}" for l in ls if l["decision"] in ("exclude", "fix-unit")}
    peelle = set(i_v2["v2_log"].get("unc_abs_units", []))
    peelle = {k for k in summarize(stg) if k.split("/", 1)[1] in peelle}
    hdr = ("# CAPSET-v2 review decisions (data/curation/capture_v2/README.md), format of the research repository's\n"
           "# data/curate/review_decisions.jsonl: entry, subentry, pointer, decision, reason (EXFOR id), reviewer, date; plus\n"
           "# rule (D3/D5/D6 code of the README) and, for D5, superseded_by / cross_entry. Applied AFTER the research file and\n"
           "# data/curation/inputs/review_decisions_Z1-25.jsonl (a later line overrides). reviewer 'rule:capset-v2' = written by\n"
           "# scripts/build_capture_v2.py from the EXFOR record; 'agent:claude-opus-5.5' = checked by hand against the entry.\n")

    def hfile(name, ls):
        write_jsonl(a.work / f"{name}_lines.jsonl", ls, hdr)
        p = a.work / f"{name}_human.jsonl"
        p.write_text(prior_text + (a.work / f"{name}_lines.jsonl").read_text(encoding="utf-8"), encoding="utf-8")
        return p

    # ladder: one fix at a time, so every decision change is attributed to the step that made it
    stage(a.main, a.work, "v2parse", X.V2_ALL - {"unc"})
    steps = [("S1_baseline", "v1", [], False), ("S2_numfix", "numfix", [], False), ("S3_parser", "v2parse", [], False),
             ("S4_uncertainty", "v2", [], False), ("S5_peelle", "v2", [], True), ("S6_sums_slips", "v2", lines36, True),
             ("S7_spsdd_dep", "v2", lines36 + lines5, True)]
    lad, pstats = {}, {}
    for name, st, ls, pe in steps:
        r, pst = run_qm(a.work / f"stage_{st}.parquet", a.work, hfile(name, ls), kk(ls), peelle if pe else set(), "q_" + name)
        lad[name] = r.quality.select("dataset_key", "target_z", "decision", "trust")
        pstats[name] = pst
    q1 = lad["S7_spsdd_dep"]
    decided = kk(lines36 + lines5) | {f"{l['entry']}/{l['subentry']}/{l['pointer']}" for l in lines36 + lines5}
    lines8 = prelm_lines(i_v2, r.quality, set(prior), decided)
    lines = lines36 + lines5 + lines8
    write_jsonl(OUT / "review_decisions_capture_v2.jsonl", lines, hdr)
    hd = a.work / "final_human.jsonl"
    hd.write_text(prior_text + (OUT / "review_decisions_capture_v2.jsonl").read_text(encoding="utf-8"), encoding="utf-8")
    r2, p2 = run_qm(stg, a.work, hd, kk(lines), peelle, "q_final")
    q = r2.quality
    lad["S8_prelm_final"] = q.select("dataset_key", "target_z", "decision", "trust")
    mine = {f"{l['entry']}/{l['subentry']}/{l['pointer']}" for l in lines}
    got = set(q.filter(pl.col("dataset_key").is_in(sorted(mine)))["dataset_key"].to_list())
    assert got == mine, f"CAPSET-v2 lines without a dataset: {sorted(mine - got)[:10]}"

    # 3. tables with the shipped schemas
    from data.curate.discrepancy import cells_from_parquet, split_group_key
    ship_t = pl.read_parquet(INP / "exfor_capture_Z26-92_trust.parquet")
    ship_c = pl.read_parquet(INP / "exfor_cells.parquet")
    q = q.select(ship_t.columns).cast(ship_t.schema)
    cells = cells_from_parquet(stg, verbose=False)
    parts = [split_group_key(k) for k in cells["group_key"].to_list()]
    cells = cells.with_columns(
        nuclide=pl.Series([p[0] for p in parts], dtype=pl.Utf8), mt=pl.Series([p[1] for p in parts], dtype=pl.Int32),
        branch=pl.Series([p[2] for p in parts], dtype=pl.Utf8), kind=pl.Series([p[3] for p in parts], dtype=pl.Utf8),
        state=pl.Series([p[4] for p in parts], dtype=pl.Utf8)).rename({"y": "ln_mean"})
    cells = cells.join(q.select("dataset_key", "trust", "inflation", "year", "decision", "usable"), on="dataset_key", how="left")
    cells = cells.select(ship_c.columns).cast(ship_c.schema)
    cells = cells.join(q.select("dataset_key", "target_z"), on="dataset_key", how="left")
    for lab, lo, hi in (("Z26-92", 26, 200), ("Z1-25", 1, 25)):
        q.filter(pl.col("target_z").is_between(lo, hi)).write_parquet(OUT / f"exfor_capture_{lab}_trust_v2.parquet")
        cells.filter(pl.col("target_z").is_between(lo, hi)).drop("target_z").write_parquet(OUT / f"exfor_cells_{lab}_v2.parquet")

    # 4. counts and audit
    counts = report(a, i_v1, i_nf, i_v2, chk, lines, audit, q, cells.drop("target_z"), lad, pstats, p2, r2)
    (OUT / "counts_v2.json").write_text(json.dumps(counts, indent=1, default=str) + "\n")
    prov = {
        "product": "CAPSET-v2 curated EXFOR capture set, Z 1-92 (data/curation/capture_v2)",
        "built": time.strftime("%Y-%m-%d %H:%M"),
        "script": "scripts/build_capture_v2.py",
        "public_commit_base": (subprocess.run(["git", "-C", str(REPO), "log", "-1", "--format=%H"], capture_output=True, text=True).stdout.strip()
                               or os.environ.get("CAPSET_BASE", "")),  # a Windows worktree is not readable by WSL git
        "research_commit": subprocess.run(["git", "-C", str(a.main), "log", "-1", "--format=%H"], capture_output=True, text=True).stdout.strip(),
        "curation_code": "research data/curate/quality_model.py + review_log.py (unchanged) with this repository's "
                         "data/curate/discrepancy.py (unchanged) and data/ingest/exfor.py (V2_FIXES = all six)",
        "entry_zip": {"path": f"raw/exfor/{ZIPNAME}", "sha256": sha(a.main / "raw" / "exfor" / ZIPNAME), "exfor_version": i_v2["exfor_version"]},
        "staging_v2": {"sha256": sha(stg), "rows": counts["staging"]["v2"], "where": "work directory, not shipped (rebuilt by this script)"},
        "human_decision_files": {"research data/curate/review_decisions.jsonl": sha(qm.HUMAN_DECISIONS),
                                 "data/curation/inputs/review_decisions_Z1-25.jsonl": sha(light_review),
                                 "data/curation/capture_v2/review_decisions_capture_v2.jsonl": sha(OUT / "review_decisions_capture_v2.jsonl")},
        "fit": {"left_out_of_consensus_fit": len(kk(lines)), "peelle_rebased_datasets": len(peelle),
                "peelle_final": p2, "peelle_clip": PEELLE_CLIP, "summary": {k: r2.summary.get(k) for k in ("fit", "n_cells", "n_datasets")}},
        "gates": {k: v.get("pass") for k, v in r2.gates.items()},
        "research_staging_check": {k: v for k, v in chk.items() if not isinstance(v, list)},
        "shipped_v1": {n: sha(INP / n) for n in ("exfor_capture_Z26-92_trust.parquet", "exfor_cells.parquet",
                                                  "exfor_capture_Z1-25_trust.parquet", "exfor_cells_Z1-25.parquet")},
    }
    (OUT / "provenance.json").write_text(json.dumps(prov, indent=1, default=str) + "\n")
    names = sorted(p.name for p in OUT.iterdir() if p.is_file() and p.name != "SHA256SUMS" and not p.name.endswith(".md"))
    (OUT / "SHA256SUMS").write_text("".join(f"{sha(OUT / n)}  {n}\n" for n in names))
    print(json.dumps({k: counts[k] for k in ("summary", "ladder")}, indent=1, default=str))


def report(a, i_v1, i_nf, i_v2, chk, lines, audit, q, cells, lad, pstats, p2, r2) -> dict:
    """Before/after counts per defect, the decision ladder (ladder_v2.csv) and the change table (changes_v1_v2.csv)."""
    import polars as pl
    w = a.work
    s1, sn, s2 = summarize(w / "stage_v1.parquet"), summarize(w / "stage_numfix.parquet"), summarize(w / "stage_v2.parquet")
    pts = lambda d, ks: sum(d[k][1] for k in ks if k in d)
    zsplit = lambda ks, d: {"Z26-92": sum(1 for k in ks if d[k][0] >= 26), "Z1-25": sum(1 for k in ks if d[k][0] <= 25)}
    # D1 numfix: v1-mode staging vs numfix-only staging
    new_nf = set(sn) - set(s1)
    more_nf = {k for k in set(sn) & set(s1) if sn[k][1:4] != s1[k][1:4]}

    def d1(sel):
        n = {k for k in new_nf if sel(sn[k][0])}
        m = {k for k in more_nf if sel(sn[k][0])}
        return {"datasets_recovered": len(n), "datasets_with_more_points_or_uncertainties": len(m),
                "points_recovered": pts(sn, n) + sum(sn[k][1] - s1[k][1] for k in m),
                "uncertainty_values_recovered": sum(sn[k][2] + sn[k][3] for k in n) + sum((sn[k][2] + sn[k][3]) - (s1[k][2] + s1[k][3]) for k in m)}
    D1 = {"Z26-92": d1(lambda z: z >= 26), "Z1-25": d1(lambda z: z <= 25), "examples": sorted(new_nf)[:15],
          "in_shipped_v1_Z26-92_trust": None}
    log = i_v2["v2_log"]
    lg = lambda f: {k for k in s2 if k.split("/", 1)[1] in set(log.get(f, []))}
    D2 = {f: {"datasets": len(lg(f)), "by_Z": zsplit(lg(f), s2), "new_in_capture_set": len(lg(f) - set(sn)),
              "points": pts(s2, lg(f)), "keys": sorted(lg(f))} for f in ("ratio", "enminapx", "ktdegc", "eqroute")}
    D4 = {"datasets_by_uncertainty_mode": {m[4:]: len(lg(m)) for m in sorted(log) if m.startswith("unc:")},
          "abs_unit_datasets_peelle": len(lg("unc_abs_units")), "peelle_final": p2}
    byrule = collections.Counter(l["rule"] for l in lines)
    d5x = [l for l in lines if l["rule"] in ("D5_SPSDD", "D5_DEP")]
    final = dict(zip(q["dataset_key"].to_list(), q["decision"].to_list()))
    orphan = [f"{l['entry']}/{l['subentry']}/{l['pointer']}" for l in d5x if final.get(l["superseded_by"]) in ("exclude", "fix-unit")]
    D5 = {"SPSDD_excluded": byrule["D5_SPSDD"], "DEP_excluded": byrule["D5_DEP"],
          "cross_entry": sum(1 for l in d5x if l.get("cross_entry")), "PRELM_downweighted": byrule["D5_PRELM"],
          "already_excluded_by_an_earlier_human_line": sum(1 for v in audit.values() if v.get("d5_skipped", "").startswith("an earlier")),
          "mutual_references_kept": sum(1 for v in audit.values() if v.get("d5_skipped", "").startswith("every")),
          "referenced_dataset_excluded_in_final": orphan}
    D3 = {"excluded": byrule["D3_SUM_REACTION"],
          "keys": sorted(f"{l['entry']}/{l['subentry']}/{l['pointer']}" for l in lines if l["rule"] == "D3_SUM_REACTION")}
    D6 = {l["subentry"]: {"line": l["decision"], "final": final.get(f"{l['entry']}/{l['subentry']}/{l['pointer']}")}
          for l in lines if l["rule"] == "D6_HAND_SLIP"}
    # v1 shipped vs v2
    real = lambda t: t.filter(~pl.col("dataset_key").str.starts_with("STD2017"))
    v1t = pl.concat([pl.read_parquet(INP / "exfor_capture_Z26-92_trust.parquet"), pl.read_parquet(INP / "exfor_capture_Z1-25_trust.parquet")])
    v1c = pl.concat([pl.read_parquet(INP / "exfor_cells.parquet"), pl.read_parquet(INP / "exfor_cells_Z1-25.parquet")])
    D1["in_shipped_v1_Z26-92_trust"] = len(new_nf & set(v1t["dataset_key"].to_list()))
    # ladder
    lt = real(v1t).select("dataset_key", "target_z", pl.col("decision").alias("S0_shipped_v1"))
    for name, t in lad.items():
        lt = lt.join(real(t).select("dataset_key", pl.col("target_z").alias("_z"), pl.col("decision").alias(name)),
                     on="dataset_key", how="full", coalesce=True).with_columns(pl.coalesce("target_z", "_z").alias("target_z")).drop("_z")
    rule_of = {f"{l['entry']}/{l['subentry']}/{l['pointer']}": l["rule"] for l in lines}
    lt = lt.with_columns(pl.col("dataset_key").replace_strict(rule_of, default=None).alias("capset_v2_rule")).sort("dataset_key")
    lt.write_csv(OUT / "ladder_v2.csv")
    cols = ["S0_shipped_v1"] + list(lad)
    ladder = {}
    for lab, lo, hi in (("Z26-92", 26, 200), ("Z1-25", 1, 25)):
        x = lt.filter(pl.col("target_z").is_between(lo, hi))
        ladder[lab] = []
        for i, c in enumerate(cols):
            row = {"step": c, **{d: int((x[c] == d).sum()) for d in ("keep", "downweight", "exclude", "fix-unit")},
                   "datasets": int(x[c].is_not_null().sum())}
            if i:
                p = cols[i - 1]
                row["changed_vs_previous"] = int(((x[c] != x[p]) | (x[c].is_null() != x[p].is_null())).fill_null(True).sum())
            ladder[lab].append(row)
    trans = {}
    for lab, lo, hi in (("Z26-92", 26, 200), ("Z1-25", 1, 25)):
        x = lt.filter(pl.col("target_z").is_between(lo, hi))
        trans[lab] = {f"{r['S0_shipped_v1']}->{r['S8_prelm_final']}": r["len"]
                      for r in x.group_by("S0_shipped_v1", "S8_prelm_final").len().sort("len", descending=True).iter_rows(named=True)}

    def side(t, c, lo, hi):
        t = real(t).filter(pl.col("target_z").is_between(lo, hi))
        c = c.filter(pl.col("dataset_key").is_in(t["dataset_key"].to_list()))
        return {"datasets": t.height, "points": int(t["n_points"].sum()), "cells": c.height,
                "decisions": dict(sorted(collections.Counter(t["decision"].to_list()).items())),
                "cells_by_decision": dict(sorted(collections.Counter(c["decision"].to_list()).items()))}
    summ = {lab: {"v1": side(v1t, v1c, lo, hi), "v2": side(q, cells, lo, hi)} for lab, lo, hi in (("Z26-92", 26, 200), ("Z1-25", 1, 25))}
    return {"summary": summ, "ladder": ladder, "transitions_v1_to_v2": trans, "D1_numfix": D1, "D2_parser": D2, "D3_sums": D3,
            "D4_uncertainty": D4, "D5_duplicates": D5, "D6_slips": D6,
            "D7_version": {"v1_parser_staged": i_v1["exfor_version"], "v2_staged": i_v2["exfor_version"]},
            "staging": {"v1_mode": len(s1), "numfix_only": len(sn), "v2": len(s2)}, "research_staging_check": chk,
            "gates_final": {k: v.get("pass") for k, v in r2.gates.items()}, "peelle_by_step": pstats,
            "d5_skips": {k: v["d5_skipped"] for k, v in audit.items() if "d5_skipped" in v}}


if __name__ == "__main__":
    main()
