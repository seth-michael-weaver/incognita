"""Regenerate the curation register from EXFOR + rule v2.

    python -m incognita.curation.build [--out DIR]

Writes to data/curation/ (or --out / $CURATION_OUT):
  curation_register_v2.jsonl        one record per decision (schema: incognita/curation/schema.py)
  curation_register_v2.csv          one row per (decision, cell), flat
  curation_cells_v2.parquet         EVERY capture cell with every test statistic, keep included
  curation_r11_series_v2.csv        every testable (series, nuclide) of R11 (MACS vs differential)
  curation_twins_v2.csv             every R3 twin pair
  curation_duplicate_candidates_v2.csv  R3d: cross-series copies dropped from reference sets (not twins, not decided)
  review_decisions_v2.jsonl         drop-in register in the review_decisions.jsonl format (for training code)
  curation_summary_v2.json          counts
  curation_register_v2.schema.json  JSON schema of one record
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import polars as pl

from . import inputs, paths, twins
from .rules import Engine
from .schema import (DOWNWEIGHT_FACTOR, LADDER2, PRIMARY_ORDER, RECORD_SCHEMA, RULE_DOC, RULE_VERSION, RULES)

LIBRARY_NAMES = re.compile(r"ENDF|JENDL|JEFF|TENDL|CENDL|BROND|FENDL|IRDFF|BRUSLIB|KADONIS", re.I)
DATE = "2026-09-23"


def _jsonable(v):
    if isinstance(v, (np.floating,)):
        return float(v)
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (set, frozenset)):
        return sorted(v)
    if isinstance(v, dict):
        return {k: _jsonable(x) for k, x in v.items()}
    if isinstance(v, (list, tuple)):
        return [_jsonable(x) for x in v]
    if isinstance(v, float):
        return round(v, 6)
    return v


def primary(rules: set[str], decision: str, ladder2: bool) -> str:
    if decision == "exclude" and ladder2 and not (rules & {k for k, v in RULES.items() if v[2] == "exclude"}):
        return LADDER2
    for k in PRIMARY_ORDER:
        if k in rules:
            return RULES[k][0]
    raise ValueError(rules)


def v1_index() -> dict[str, list[dict]]:
    out = defaultdict(list)
    rows = [json.loads(l) for l in paths.REGISTER_V1.read_text().splitlines() if l.startswith("{")]
    for i, r in enumerate(rows):
        k = f"{r['entry']}/{r['subentry']}/{r.get('pointer') or ''}"
        out[k].append(dict(src_line=i, decision="renorm" if "renorm" in r else r["decision"],
                           scope="points" if "points" in r else "dataset", rule=r.get("rule") or r.get("twin_rule") or ""))
    return out


def cell_summary(r: dict) -> str:
    ev, parts = r["ev"], []
    r5 = ev.get("r5") or {}
    if "d" in r5:
        parts.append(f"d={r5['d']:+.2f} dex vs {r5['n_ref']} independent series{' (bins +-1)' if r5.get('widened') else ''}")
    if "r6" in ev:
        parts.append(f"series median {ev['r6']['median']:+.2f} over {ev['r6']['n_other']} cells")
    if "d" in (ev.get("r10") or {}):
        parts.append(f"isotopic d={ev['r10']['d']:+.2f} dex vs {ev['r10']['n_nuclides']} neighbours")
    if "r9" in ev:
        parts.append(f"14 MeV d={ev['r9']['d']:+.2f} dex vs {ev['r9']['n_nuclides']} nuclides")
    return "; ".join(parts)


def build(out: Path) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    findings = inputs.record_findings()
    T = twins.find_twins()
    sid = twins.series_ids(list(zip(T["superseded"], T["kept"])))
    cells = inputs.load_cells()
    E = Engine(cells, sid, T, findings)
    E.pass_a()
    E.pass_b()
    E.ladder()
    v1 = v1_index()
    fnd = {f["id"]: f for f in findings}

    # ---------------------------------------------------------------- assemble records
    records = []
    need_pts = set()
    for key, cs in E.by_ds.items():
        nonkeep = [r for r in cs if r["decision"] != "keep"]
        rn = E.renorm.get(key)
        if not nonkeep and not rn:
            continue
        need_pts.add(key)
    pts = inputs.points_of(need_pts)
    for key in sorted(need_pts):
        cs = sorted(E.by_ds[key], key=lambda r: r["bin"])
        r0 = cs[0]
        base = dict(rule_version=RULE_VERSION, dataset_key=key, entry=r0["entry"], subentry=r0["subentry"],
                    pointer=r0["pointer"] or "", nuclide=r0["nuclide"], z=r0["target_z"], a=r0["target_a"],
                    kind=r0["kind"], first_author=r0["first_author"], year=r0["ds_year"],
                    flags=dict(sf9=r0["sf9"], derived=bool(r0["derived"]),
                               status=sorted(E.status(r0)), no_uncertainty=all(bool(r["no_unc"]) for r in cs)),
                    v1=dict(lines=v1.get(key, [])))
        groups = defaultdict(list)
        for r in cs:
            if r["decision"] != "keep":
                groups[r["decision"]].append(r)
        for dec, g in groups.items():
            scope = "dataset" if len(g) == len(cs) else "cells"
            rules = set().union(*(r["fired"] for r in g)) - {"R4"}
            ladder2 = any(r.get("ladder2") for r in g)
            dev = {}
            if "R3" in rules:
                dev["twin"] = E.twins[key]
            recf = sorted({i for r in g for i in r["ev"].get("record_findings", [])})
            if recf:
                dev["record_findings"] = [dict(id=i, rule=fnd[i]["rule"], quotes=fnd[i]["quotes"], note=fnd[i]["note"],
                                               origin=fnd[i]["origin"]) for i in recf]
            r11 = next((r["ev"]["r11"] for r in g if "r11" in r["ev"]), None)
            if r11:
                dev["r11"] = r11
            clist = []
            for r in g:
                ev = {k: v for k, v in r["ev"].items() if k not in ("r11", "record_findings", "R3")}
                p = [dict(e_ev=e, meas_b=v) for e, v in pts.get(key, [])
                     if r["e_lo_ev"] * 0.9999 <= e <= r["e_hi_ev"] * 1.0001]
                clist.append(dict(bin=r["bin"], e_lo_ev=r["e_lo_ev"], e_hi_ev=r["e_hi_ev"], mean_b=r["mean_b"],
                                  n_pts=r["n_pts"], sig_x=round(r["sig_x"], 4), rules=sorted(r["fired"]),
                                  evidence=ev, points=p))
            code = primary(rules, dec, ladder2)
            erng = f"{min(r['e_lo_ev'] for r in g):.4g}-{max(r['e_hi_ev'] for r in g):.4g} eV"
            first = next((cell_summary(r) for r in g if cell_summary(r)), "")
            summ = (f"{dec.upper()} ({code}) {r0['nuclide']} {r0['kind']} {key}, {scope} scope, {len(g)} cell(s) {erng}; "
                    f"rules {'+'.join(sorted(rules))}" + (f"; {first}" if first else "")
                    + (f"; twin of {E.twins[key]['kept']} ({E.twins[key]['how']})" if "R3" in rules else "")
                    + (f"; {r11['n_against']} of {r11['n_groups']} MACS groups against" if r11 else ""))
            h = hashlib.sha1(f"{key}|{dec}|{[c['bin'] for c in clist]}".encode()).hexdigest()[:8]
            records.append(dict(id=f"CR2-{key.replace('/', '-').rstrip('-')}-{h}", **base, decision=dec,
                                factor=DOWNWEIGHT_FACTOR if dec == "downweight" else None, scope=scope,
                                reason_code=code, rules_fired=sorted(rules), cells=clist, evidence=dev,
                                standard=None, summary=summ))
        rn = E.renorm.get(key)
        if rn:
            h = hashlib.sha1(f"{key}|renorm".encode()).hexdigest()[:8]
            records.append(dict(id=f"CR2-{key.replace('/', '-').rstrip('-')}-{h}", **base, decision="renorm",
                                factor=rn["renorm"]["factor"], scope="dataset", reason_code=RULES["R4"][0],
                                rules_fired=["R4"],
                                cells=[dict(bin=r["bin"], e_lo_ev=r["e_lo_ev"], e_hi_ev=r["e_hi_ev"], mean_b=r["mean_b"],
                                            n_pts=r["n_pts"], sig_x=round(r["sig_x"], 4), rules=["R4"], evidence={})
                                       for r in cs],
                                evidence=dict(record_findings=[dict(id=rn["id"], rule="R4", quotes=rn["quotes"],
                                                                    note=rn["note"], origin=rn["origin"])]),
                                standard=rn["renorm"],
                                summary=f"RENORM x{rn['renorm']['factor']} {key}: {rn['renorm']['standard']} "
                                        f"{rn['renorm']['documented_mb']} mb (documented) -> {rn['renorm']['reference_mb']} mb"))
    records = [_jsonable(r) for r in records]

    # ---------------------------------------------------------------- write
    reg = out / "curation_register_v2.jsonl"
    reg.write_text("".join(json.dumps(r) + "\n" for r in records))
    (out / "curation_register_v2.schema.json").write_text(json.dumps(RECORD_SCHEMA, indent=1))
    flat = ["id", "dataset_key", "nuclide", "kind", "first_author", "year", "decision", "factor", "scope",
            "reason_code", "bin", "e_lo_ev", "e_hi_ev", "mean_b", "sig_x", "cell_rules", "d_dex", "n_ref",
            "ref_offsets_dex", "r6_median", "r10_d", "r9_d", "r11_against", "record_findings", "summary"]
    with (out / "curation_register_v2.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=flat)
        w.writeheader()
        for r in records:
            for c in r["cells"]:
                ev = c["evidence"]
                w.writerow(dict(id=r["id"], dataset_key=r["dataset_key"], nuclide=r["nuclide"], kind=r["kind"],
                                first_author=r["first_author"], year=r["year"], decision=r["decision"], factor=r["factor"],
                                scope=r["scope"], reason_code=r["reason_code"], bin=c["bin"], e_lo_ev=c["e_lo_ev"],
                                e_hi_ev=c["e_hi_ev"], mean_b=c["mean_b"], sig_x=c["sig_x"], cell_rules="+".join(c["rules"]),
                                d_dex=(ev.get("r5") or {}).get("d"), n_ref=(ev.get("r5") or {}).get("n_ref"),
                                ref_offsets_dex=json.dumps((ev.get("r5") or {}).get("ref_dex")),
                                r6_median=(ev.get("r6") or {}).get("median"), r10_d=(ev.get("r10") or {}).get("d"),
                                r9_d=(ev.get("r9") or {}).get("d"),
                                r11_against=(r["evidence"].get("r11") or {}).get("n_against"),
                                record_findings=";".join(f["id"] for f in r["evidence"].get("record_findings", [])),
                                summary=r["summary"]))
    allc = pl.DataFrame([dict(dataset_key=r["dataset_key"], nuclide=r["nuclide"], kind=r["kind"], bin=r["bin"],
                              e_lo_ev=r["e_lo_ev"], e_hi_ev=r["e_hi_ev"], mean_b=r["mean_b"], x=r["x"], sig_x=r["sig_x"],
                              series=r["series"], e_stat=r["e_stat"], in_region=r["in_region"], comparable=r["cmp"],
                              pool=r["pool"], derived=r["derived"], decision=r["decision"],
                              rules="+".join(sorted(r["fired"])), evidence=json.dumps(_jsonable(r["ev"])))
                         for r in E.recs])
    allc.write_parquet(out / "curation_cells_v2.parquet")
    pl.DataFrame([dict(r, datasets=";".join(r["datasets"]), groups=json.dumps(_jsonable(r["groups"])))
                  for r in E.r11_rows]).write_csv(out / "curation_r11_series_v2.csv")
    T.write_csv(out / "curation_twins_v2.csv")
    tw = {frozenset((a, b)) for a, b in zip(T["superseded"], T["kept"])}
    dup = []
    for a, b in sorted(E.dup_pairs):
        A, B = E.ds_vals[a], E.ds_vals[b]
        com = [c for c in A if c in B]
        lr = np.array([A[c] - B[c] for c in com]) if com else np.array([np.nan])
        ra, rb = E.by_ds[a][0], E.by_ds[b][0]
        dup.append(dict(dataset_a=a, dataset_b=b, nuclide=ra["nuclide"], author_a=ra["first_author"], year_a=ra["ds_year"],
                        author_b=rb["first_author"], year_b=rb["ds_year"], n_shared_cells=len(com),
                        mean_log10_ratio=float(np.nanmean(lr)), sd_log10_ratio=float(np.nanstd(lr)),
                        known_twin=frozenset((a, b)) in tw))
    pl.DataFrame(dup).write_csv(out / "curation_duplicate_candidates_v2.csv")
    legacy = write_legacy(records, out / "review_decisions_v2.jsonl")

    # ---------------------------------------------------------------- guard: no library value in any output
    for f in ("curation_register_v2.jsonl", "curation_register_v2.csv", "review_decisions_v2.jsonl"):
        txt = (out / f).read_text()
        hits = sorted(set(m.group(0) for m in LIBRARY_NAMES.finditer(txt)))
        if hits:
            raise SystemExit(f"{f}: evaluated-library names in the output: {hits}")
    summ = dict(
        rule=RULE_DOC, cells=len(E.recs), records=len(records),
        decisions=dict(Counter(r["decision"] for r in records)),
        reason_codes=dict(Counter(r["reason_code"] for r in records)),
        scope=dict(Counter(r["scope"] for r in records)),
        cells_by_decision=dict(Counter(r["decision"] for r in E.recs)),
        cell_rules=dict(Counter(k for r in E.recs for k in r["fired"])),
        untested_cells=dict(Counter(r["ev"].get("untested", "tested").split(" (")[0] for r in E.recs
                                    if r["decision"] == "keep" or "untested" in r["ev"])),
        twins=T.height, duplicate_candidates=len(E.dup_pairs), r11_testable=len(E.r11_rows), r11_flagged=sum(r["flag"] for r in E.r11_rows),
        record_findings=len(findings), legacy_lines=legacy,
        datasets_with_record_but_no_cells=sorted({f"{f['entry']}/{f['subentry']}/{f.get('pointer') or ''}" for f in findings}
                                                 - set(E.by_ds)),
    )
    (out / "curation_summary_v2.json").write_text(json.dumps(summ, indent=1))
    return summ


def write_legacy(records: list[dict], path: Path) -> int:
    """review_decisions.jsonl format: dataset lines, point-scoped lines (EXFOR points of the cells), renorm lines."""
    lines = [f"# CURREG curation register {RULE_VERSION} ({DATE}), generated by incognita.curation.build from EXFOR + "
             f"{RULE_DOC}. Library-free. Same format as data/curate/review_decisions.jsonl: dataset lines, point-scoped "
             "lines (points = the EXFOR points of the decided cells; a point-scoped downweight carries factor 0.25 and a "
             "reader without point-scoped downweight support must skip it) and renorm lines."]
    for r in records:
        base = dict(entry=r["entry"], subentry=r["subentry"], pointer=r["pointer"])
        meta = dict(rule=f"CURREG-{RULE_VERSION}", reason_code=r["reason_code"], register_id=r["id"],
                    reason=r["summary"], reviewer="rule (incognita.curation)", date=DATE)
        if r["decision"] == "renorm":
            s = r["standard"]
            lines.append(json.dumps({**base, "renorm": dict(factor=s["factor"], monitor="79-AU-197(N,G)79-AU-198,,SIG,,SPA",
                                                                assumed=s["documented_mb"], new=s["reference_mb"],
                                                                source=s["reference_source"]), **meta}))
            continue
        line = {**base, "decision": r["decision"]}
        if r["scope"] == "cells":
            p = [q for c in r["cells"] for q in c.get("points", [])]
            if not p:
                p = [dict(e_ev=float(np.sqrt(max(c["e_lo_ev"], 1e-9) * max(c["e_hi_ev"], 1e-9))), meas_b=c["mean_b"])
                     for c in r["cells"]]
            line["points"] = p
            if r["decision"] == "downweight":
                line["factor"] = DOWNWEIGHT_FACTOR
        if "twin" in r["evidence"]:
            line["superseded_by"] = r["evidence"]["twin"]["kept"]
            line["twin_rule"] = r["evidence"]["twin"]["how"]
        lines.append(json.dumps({**line, **meta}))
    path.write_text("\n".join(lines) + "\n")
    return len(lines) - 1


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=paths.OUT)
    a = ap.parse_args()
    print(json.dumps(build(a.out), indent=1))


if __name__ == "__main__":
    main()
