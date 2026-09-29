"""Validate register v2 against the v1 register (rule v2 §4).

    python -m incognita.curation.validate [--reg DIR]

Writes to <DIR>/validation/:
  v1_lines_vs_v2.csv     each of the 524 v1 lines: old decision, v2 decision on the line's own scope, agree, codes
  flips.csv              the lines whose decision changed, with the v2 evidence
  new_decisions.csv      v2 decisions (cells) that no v1 line covers
  audit_sample.csv       the pre-registered 30-decision spot-audit sample (seed 20260923, strata of 10)
  validation_summary.json
"""
from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import polars as pl

from . import paths

LIBPAT = re.compile(r"ENDF|JENDL|JEFF|TENDL|CENDL|BROND|FENDL|IRDFF|BRUSLIB|evaluat|librar|VIII\.|VII\.1", re.I)
L2_LINES = set(range(0, 5)) | set(range(398, 470))   # INDEP_CURATE's reading: a library VALUE was evidence
ORDER = {"keep": 0, "downweight": 1, "exclude": 2}
SEED = 20260923


def v1_class(i: int, row: dict) -> str:
    if not LIBPAT.search(json.dumps(row)):
        return "none"
    if i in L2_LINES:
        return "L2"
    return "L1" if row.get("rule") == "MACSCHECK" else "L0"


def validate(reg: Path) -> dict:
    out = reg / "validation"
    out.mkdir(parents=True, exist_ok=True)
    cells = pl.read_parquet(reg / "curation_cells_v2.parquet")
    recs = [json.loads(l) for l in (reg / "curation_register_v2.jsonl").read_text().splitlines()]
    renorm = {r["dataset_key"] for r in recs if r["decision"] == "renorm"}
    by_ds = defaultdict(list)
    for r in cells.iter_rows(named=True):
        by_ds[r["dataset_key"]].append(r)
    v1 = [json.loads(l) for l in paths.REGISTER_V1.read_text().splitlines() if l.startswith("{")]
    rows, covered = [], set()
    for i, r in enumerate(v1):
        key = f"{r['entry']}/{r['subentry']}/{r.get('pointer') or ''}"
        old = "renorm" if "renorm" in r else r["decision"]
        cs = by_ds.get(key, [])
        if "points" in r:
            sel = []
            for p in r["points"]:
                hit = [c for c in cs if c["e_lo_ev"] * 0.9999 <= p["e_ev"] <= c["e_hi_ev"] * 1.0001]
                if hit and p.get("meas_b"):
                    hit = [min(hit, key=lambda c: abs(np.log10(c["mean_b"] / p["meas_b"])))]
                sel += hit
        else:
            sel = cs
        sel = list({(c["dataset_key"], c["bin"], c["kind"]): c for c in sel}.values())
        covered |= {(c["dataset_key"], c["bin"]) for c in sel}
        if old == "renorm":
            new = "renorm" if key in renorm else "keep"
        elif not sel:
            new = "no-cell"
        else:
            new = max((c["decision"] for c in sel), key=ORDER.get)
        rules = sorted({x for c in sel for x in (c["rules"] or "").split("+") if x})
        ev = [json.loads(c["evidence"]) for c in sel]
        note = "; ".join(sorted({e.get("untested", "") for e in ev} - {""}))
        rows.append(dict(src_line=i, dataset_key=key, nuclide=cs[0]["nuclide"] if cs else "",
                         v1_rule=r.get("rule") or ("TWIN " + r["twin_rule"] if "twin_rule" in r else ""),
                         v1_rules=r.get("rules", ""), v1_scope="points" if "points" in r else "dataset",
                         v1_class=v1_class(i, r), old=old, new=new, agree=old == new, n_cells=len(sel),
                         v2_rules="+".join(rules), untested=note,
                         d_dex=";".join(str((e.get("r5") or {}).get("d", "")) for e in ev[:6]),
                         n_ref=";".join(str((e.get("r5") or {}).get("n_ref", "")) for e in ev[:6])))
    with (out / "v1_lines_vs_v2.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    flips = [r for r in rows if not r["agree"]]
    with (out / "flips.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(flips)
    new = cells.filter(pl.col("decision") != "keep").with_columns(
        v1=pl.struct("dataset_key", "bin").map_elements(lambda s: (s["dataset_key"], s["bin"]) in covered,
                                                          return_dtype=pl.Boolean)).filter(~pl.col("v1"))
    new.drop("v1").write_csv(out / "new_decisions.csv")

    # pre-registered audit sample: (a) R3 records, (b) other non-keep records, (c) flips
    rng = np.random.default_rng(SEED)
    a = sorted([r["id"] for r in recs if r["reason_code"] == "R3_TWIN_SUPERSEDED"])
    b = sorted([r["id"] for r in recs if r["reason_code"] != "R3_TWIN_SUPERSEDED" and r["decision"] != "renorm"])
    c = sorted([r["src_line"] for r in flips])
    pick = lambda xs: [xs[i] for i in sorted(rng.choice(len(xs), size=min(10, len(xs)), replace=False))]  # noqa: E731
    rid = {r["id"]: r for r in recs}
    sample = [dict(stratum="a_twin", item=x, dataset_key=rid[x]["dataset_key"], decision=rid[x]["decision"],
                   reason_code=rid[x]["reason_code"], summary=rid[x]["summary"]) for x in pick(a)]
    sample += [dict(stratum="b_other", item=x, dataset_key=rid[x]["dataset_key"], decision=rid[x]["decision"],
                    reason_code=rid[x]["reason_code"], summary=rid[x]["summary"]) for x in pick(b)]
    fl = {r["src_line"]: r for r in flips}
    sample += [dict(stratum="c_flip", item=f"v1 line {x}", dataset_key=fl[x]["dataset_key"],
                    decision=f"{fl[x]['old']}->{fl[x]['new']}", reason_code=fl[x]["v2_rules"],
                    summary=f"v1 {fl[x]['v1_rule']} {fl[x]['v1_rules']}; {fl[x]['untested']}") for x in pick(c)]
    with (out / "audit_sample.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(sample[0]) + ["verdict", "exfor_quote", "auditor_note"])
        w.writeheader()
        w.writerows(sample)
    tr = Counter((r["old"], r["new"]) for r in rows)
    summ = dict(
        v1_lines=len(rows), agree=sum(r["agree"] for r in rows), flips=len(flips),
        transitions={f"{a}->{b}": n for (a, b), n in sorted(tr.items())},
        by_v1_class={k: dict(n=sum(r["v1_class"] == k for r in rows), flips=sum(r["v1_class"] == k and not r["agree"] for r in rows))
                     for k in ("L2", "L1", "L0", "none")},
        by_v1_rule={k: dict(n=n, flips=sum(1 for r in flips if (r["v1_rule"] or "?") == k))
                    for k, n in Counter(r["v1_rule"] or "?" for r in rows).items()},
        new_decision_cells=new.height, new_decision_datasets=new["dataset_key"].n_unique(),
        new_by_decision=dict(Counter(new["decision"].to_list())),
        audit_pools=dict(a=len(a), b=len(b), c=len(c)),
    )
    (out / "validation_summary.json").write_text(json.dumps(summ, indent=1))
    return summ


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--reg", type=Path, default=paths.OUT)
    print(json.dumps(validate(ap.parse_args().reg), indent=1))


if __name__ == "__main__":
    main()
