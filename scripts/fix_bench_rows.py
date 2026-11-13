"""Apply the REACTION-code check (incognita/bench/reaction_check.py) to the benchmark's EXFOR rows (2026-11-06).

The rows of ch-n2n / ch-np / ch-na / ch-sacs (incognita/bench/data/exam_rows/{n2n,np,na,sacs}_rows.parquet) were cut by
the research repository's channel comparison (scripts/channels/score_channels.py --amend, rule set A1), which checked only
the first SF block of a REACTION string and only the isomer suffixes -M / -Mn / -G. The light (Z 1-25) rows already pass
the full check. This script applies the same check to every benchmark row, so both sides follow one rule:

  - the REACTION code of each row's series is read from the staged EXFOR table of the 2026-10-14 entry.zip
    (research checkout, staging/exfor_all_2026-10-14_x4fix1.parquet); a series is subentry.pointer, or a subentry
    (rows without a pointer: the na_rows He-production / confirm / pristine sets and the SACS rows), in which case the
    subentry's reactions for the row's channel are used and the row is dropped only if every one of them is flagged;
  - flagged rows are removed from the parquet and listed, with their flags and REACTION code, in
    exam_rows/reaction_check_dropped.csv (nothing is deleted silently);
  - -G+M1 (ground + first isomer) is the total only when the residual has no further isomer (NUBASE2020); it is kept
    then and dropped otherwise (on these rows every G+M1 residual, Ir-190, Ir-192, Au-196, has a second isomer);
  - SF9 = DERIV rows are dropped by the rule (d); the script also reports, for information, whether each DERIV row
    duplicates a kept row (same channel and nucleus, energy within 3 %, value within 5 %).

usage (the research checkout's environment; writes into this repository only):
  cd MAIN && uv run --no-sync python <this repo>/scripts/fix_bench_rows.py [--main MAIN] [--dry-run]
then update incognita/bench/data/exam_rows/SHA256SUMS and `python -m incognita.bench.score tracks --write`.
"""
import argparse, collections, hashlib, json, sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
from incognita.bench.reaction_check import nubase_isomers, reaction_flags  # noqa: E402

EXAM = REPO / "incognita" / "bench" / "data" / "exam_rows"
ALL = "exfor_all_2026-10-14_x4fix1.parquet"
SF3 = {"n2n": {"2N"}, "np": {"P"}, "na": {"A"}, "nxa": {"X", "A"}, "capture": {"G"}}
FILES = ("n2n_rows", "np_rows", "na_rows", "sacs_rows", "capture_rows")


def channel_of(f, r):
    if f == "capture_rows":
        return "capture"
    if f == "na_rows":
        return "nxa" if r.kind == "nxa" else "na"
    return r.channel


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--main", type=Path, default=Path("~/nucleus").expanduser())
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    from data.ingest.nubase import load_nubase
    other = nubase_isomers(load_nubase(a.main / "raw" / "nubase2020" / "nubase_4.mas20.txt"))
    S = pd.read_parquet(a.main / "staging" / ALL, columns=["entry", "subentry", "pointer", "reaction", "sf"])
    S["sf3"] = [(s or {}).get("sf3") or "" for s in S.sf]
    S["series"] = S.subentry + "." + S.pointer.fillna("nan").astype(str)
    by_series = S.drop_duplicates("series").set_index("series")
    by_sub = S.groupby("subentry")

    dropped, report = [], {}
    for f in FILES:
        D = pd.read_parquet(EXAM / f"{f}.parquet")
        sacs = f == "sacs_rows"
        flags, rx, how = [], [], []
        for r in D.itertuples(index=False):
            ch = channel_of(f, r)
            s = str(r.series)
            if s.count("/") == 2:                      # capture_rows: entry/subentry/pointer
                s = s.split("/")[1] + "." + (s.split("/")[2] or "nan")
            if s in by_series.index:
                x = by_series.loc[s]
                fl = reaction_flags(x.reaction, x.entry, sacs, other)
                flags.append(",".join(fl)); rx.append(x.reaction); how.append("series")
                continue
            sub = s.split(".")[0]
            if sub not in by_sub.groups:
                flags.append(""); rx.append(""); how.append("NOT_FOUND")
                continue
            g = by_sub.get_group(sub)
            g = g[g.sf3.str.upper().isin(SF3[ch])] if g.sf3.str.upper().isin(SF3[ch]).any() else g
            fls = [reaction_flags(x.reaction, x.entry, sacs, other) for x in g.itertuples()]
            allflagged = all(fls)
            flags.append(",".join(sorted(set(sum(fls, [])))) if allflagged else "")
            rx.append(" | ".join(sorted(set(g.reaction)))); how.append(f"subentry ({len(g)} pointer(s))")
        D = D.assign(rc_flags=flags, rc_reaction=rx, rc_match=how)
        bad = D.rc_flags != ""
        c = collections.Counter(fl.split(",")[0] if "," not in fl else fl for fl in D.rc_flags[bad])
        rep = {"rows": len(D), "dropped": int(bad.sum()), "kept": int((~bad).sum()),
               "not_found_in_staging": int((D.rc_match == "NOT_FOUND").sum()), "by_flag": dict(c.most_common())}
        # DERIV: duplicate of a kept row? (information only; the rule drops DERIV)
        e_col = "e_ev" if "e_ev" in D else None
        if e_col and "data_mb" in D:
            keep = D[~bad]
            der = D[D.rc_flags.str.contains("SF9:DERIV")]
            dup = 0
            for r in der.itertuples(index=False):
                k = keep[(keep.Z == r.Z) & (keep.A == r.A)]
                if "channel" in D:
                    k = k[k.channel == r.channel]
                m = (np.abs(np.log(k[e_col] / getattr(r, e_col))) < 0.03) & (np.abs(np.log(k.data_mb / r.data_mb)) < 0.05)
                dup += bool(m.any())
            rep["deriv_rows"] = len(der); rep["deriv_duplicating_a_kept_row"] = dup
        report[f] = rep
        print(f, json.dumps(rep), flush=True)
        out = D[bad].copy(); out.insert(0, "file", f)
        dropped.append(out)
        if not a.dry_run:
            D[~bad].drop(columns=["rc_flags", "rc_reaction", "rc_match"]).reset_index(drop=True).to_parquet(EXAM / f"{f}.parquet", index=False)

    X = pd.concat(dropped, ignore_index=True).rename(columns={"rc_flags": "flags", "rc_reaction": "reaction", "rc_match": "matched_by"})
    cols = ["file", "channel", "kind", "src", "Z", "A", "series", "e_ev", "spectrum", "data_mb", "data_b", "year", "flags", "reaction", "matched_by"]
    X = X[[c for c in cols if c in X.columns]]
    p = EXAM / "reaction_check_dropped.csv"
    if not a.dry_run:
        if p.exists():   # idempotent: a second run finds nothing new; keep the first run's list
            X = pd.concat([pd.read_csv(p), X], ignore_index=True).drop_duplicates()
        X.to_csv(p, index=False, float_format="%.10g", lineterminator="\n")
        (EXAM / "reaction_check_report.json").write_text(json.dumps(report, indent=1) + "\n") if any(
            r["dropped"] for r in report.values()) else None
        print("->", p)
    else:
        X.to_csv("reaction_check_dropped_dryrun.csv", index=False)


if __name__ == "__main__":
    main()
