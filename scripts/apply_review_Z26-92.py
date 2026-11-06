"""Apply data/curation/inputs/review_decisions_Z26-92.jsonl to the shipped Z 26-92 capture curation (2026-11-06).

The Z 26-92 tables (exfor_capture_Z26-92_trust.parquet, exfor_cells.parquet) are the research repository's WP-12 curation
as run on 2026-09-12; they are not re-run here (a re-run on today's snapshot would move about 6 % of the decisions, see
data/curation/inputs/README.md). Review lines are applied on top, the way quality_model applies its human-decision file:

  - "decision": "exclude" (or keep / downweight): trust table columns review_decision, review_note, reviewer, decision and
    reason are set; the dataset's cells get the same decision. Nothing is removed from either table.
  - "rekey": {"state": ..., "group_key": ...}: the dataset is re-keyed in both tables (state, group_key); its decision,
    trust and values are unchanged; review_note records why.

Idempotent: applying the same file twice changes nothing. Then update data/curation/inputs/SHA256SUMS.

usage:  python scripts/apply_review_Z26-92.py      (needs pandas + pyarrow)
"""
import json
from pathlib import Path

import pandas as pd

INP = Path(__file__).resolve().parents[1] / "data" / "curation" / "inputs"
TRUST, CELLS, REVIEW = INP / "exfor_capture_Z26-92_trust.parquet", INP / "exfor_cells.parquet", INP / "review_decisions_Z26-92.jsonl"


def key(d):
    return f"{d['entry']}/{d['subentry']}/{d.get('pointer') or ''}"


def main():
    import pyarrow as pa, pyarrow.parquet as pq
    sT, sC = pq.read_schema(TRUST), pq.read_schema(CELLS)       # written back with the same schema (int columns with nulls)
    T, C = pd.read_parquet(TRUST), pd.read_parquet(CELLS)
    lines = [json.loads(l) for l in REVIEW.read_text().splitlines() if l.strip() and not l.startswith("#")]
    for d in lines:
        k = key(d)
        t, c = T.dataset_key == k, C.dataset_key == k
        if t.sum() != 1:
            raise SystemExit(f"{k}: {int(t.sum())} rows in the trust table (expected 1)")
        if "rekey" in d:
            for col, v in d["rekey"].items():
                T.loc[t, col] = v
                if col in C:
                    C.loc[c, col] = v
            T.loc[t, "review_note"] = d["reason"]
            T.loc[t, "reviewer"] = d["reviewer"]
            print(f"{k}: re-keyed {d['rekey']} ({int(c.sum())} cells)")
            continue
        dec = d["decision"]
        T.loc[t, ["review_decision", "review_note", "reviewer", "decision", "reason"]] = [dec, d["reason"], d["reviewer"], dec, d["reason"]]
        C.loc[c, "decision"] = dec
        print(f"{k}: {dec} ({int(c.sum())} cells)")
    pq.write_table(pa.Table.from_pandas(T, schema=sT, preserve_index=False), TRUST, compression="zstd")
    pq.write_table(pa.Table.from_pandas(C, schema=sC, preserve_index=False), CELLS, compression="zstd")


if __name__ == "__main__":
    main()
