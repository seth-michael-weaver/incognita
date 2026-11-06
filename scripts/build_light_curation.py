"""Curated EXFOR capture for the light nuclides H..Mn (Z 1-25): the same WP-12 curation as the shipped Z 26-92 set.

The shipped Z 26-92 tables (data/curation/inputs/exfor_capture_Z26-92_trust.parquet, exfor_cells.parquet) were made by
the research repository's WP-12 curation (`python -m data.curate.quality_model`: leave-one-out discrepancy against the
other experiments, a metadata prior, Bayesian trust, automatic decisions keep / downweight / exclude / fix-unit). This
script runs that same code, unchanged, for Z 1-25 and writes tables with the same schemas:

  data/curation/inputs/exfor_capture_Z1-25_trust.parquet   one row per dataset   (schema of exfor_capture_Z26-92_trust)
  data/curation/inputs/exfor_cells_Z1-25.parquet           one row per dataset x 0.1-dex energy bin (schema of exfor_cells)
  data/curation/inputs/exfor_capture_Z1-25_provenance.json inputs (SHA256), gates, decision counts

Steps (all inside the research checkout given by --main, default ~/nucleus; nothing there is written):
  1. Stage. EXFOR capture for Z 1-25 is taken from the full staged EXFOR table (staging/exfor_all_2026-10-14_x4fix1,
     the 2026-10-14 entry.zip) with the predicate and energy clip of `python -m data.ingest.exfor --subset capture`
     (SF2 = N, SF3 = G, SF6 in SIG/RI; points above 20 MeV dropped, a measurement with no point left dropped). The
     same procedure applied to Z 26-92 is checked to reproduce staging/exfor_capture_Z26-92_2026-10-14_x4fix1 exactly;
     the build stops if it does not.
  2. Curate. quality_model runs ONCE on Z 1-92 together (light + the Z 26-92 staging), so the metadata prior and the
     global scatter model are learned from the whole chart, as for Z 26-92, and the IAEA-standards and 238U spot-list
     gates can run (a light-only run has no capture standard). Only the Z 1-25 rows are kept. The human review
     decisions in data/curate/review_decisions.jsonl are applied as usual; none of them names a light dataset, so
     every light decision is the automatic layer (reviewer "auto:quality_model_v0.2").
  3. Cells. As validation/cache.py cache_exfor_cells: discrepancy.cells_from_parquet on the staged light data, joined to
     the trust table (trust, inflation, year, decision, usable). Capture has no value floor.

The Z 26-92 files are NOT rebuilt (they stay the shipped 2026-09-12 curation). The Z 26-92 rows of the joint run are
used only for the check printed at the end (agreement of the joint run's decisions with the shipped ones).

usage (WSL, the research checkout's environment):
  cd ~/nucleus && uv run --no-sync python <this repo>/scripts/build_light_curation.py [--main ~/nucleus] [--work DIR]
"""
import argparse, collections, hashlib, json, math, os, subprocess, sys, time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "data" / "curation" / "inputs"
ALL = "exfor_all_2026-10-14_x4fix1.parquet"
HEAVY = "exfor_capture_Z26-92_2026-10-14_x4fix1.parquet"
EMAX = 20e6
TAG = "exfor_capture_Z1-92"


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def stage(main: Path, work: Path):
    import pyarrow as pa, pyarrow.compute as pc, pyarrow.parquet as pq
    t = pq.read_table(main / "staging" / ALL)
    sf = t["sf"]
    up = lambda f: pc.utf8_upper(pc.fill_null(pc.struct_field(sf, f), ""))
    base = pc.and_(pc.and_(pc.equal(up("sf2"), "N"), pc.equal(up("sf3"), "G")),
                   pc.is_in(up("sf6"), value_set=pa.array(["SIG", "RI"])))
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

    def sub(a, b):
        rows = t.filter(pc.and_(base, pc.and_(pc.greater_equal(z, a), pc.less_equal(z, b)))).to_pylist()
        return pa.Table.from_pylist(clip(rows), schema=t.schema)

    def norm(T):
        fix = lambda v: ("nan" if isinstance(v, float) and math.isnan(v) else [fix(x) for x in v] if isinstance(v, list)
                         else {k: fix(x) for k, x in v.items()} if isinstance(v, dict) else v)
        return sorted((fix(r) for r in T.to_pylist()), key=lambda r: (r["subentry"], r["pointer"] or ""))

    heavy = pq.read_table(main / "staging" / HEAVY).cast(t.schema)
    if norm(sub(26, 92)) != norm(heavy):
        sys.exit("staging check FAILED: the capture predicate + clip does not reproduce " + HEAVY)
    light = sub(1, 25)
    pq.write_table(light, work / "exfor_capture_Z1-25.parquet")
    pq.write_table(pa.concat_tables([light, heavy]), work / "exfor_capture_Z1-92.parquet")
    print(f"staged: {light.num_rows} light measurements; Z 26-92 check reproduces {heavy.num_rows} rows exactly")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--main", type=Path, default=Path("~/nucleus").expanduser())
    ap.add_argument("--work", type=Path, default=Path("~/lightdata_work").expanduser())
    a = ap.parse_args()
    a.work.mkdir(parents=True, exist_ok=True)
    sys.path.insert(0, str(a.main))
    stage(a.main, a.work)

    import polars as pl
    from data.curate import quality_model as qm
    from data.curate.discrepancy import cells_from_parquet, split_group_key
    qdir = a.work / "q92"
    res = qm.run(a.work / "exfor_capture_Z1-92.parquet", qdir, tag=TAG, verbose=False)
    q = pl.read_parquet(qdir / f"{TAG}_trust.parquet")
    light = q.filter(pl.col("target_z") <= 25)
    assert light.filter(pl.col("reviewer") != "auto:quality_model_v0.2").height == 0, "a human decision names a light dataset"
    ship = pl.read_parquet(OUT / "exfor_capture_Z26-92_trust.parquet")
    assert light.columns == ship.columns, "trust schema differs from the shipped Z 26-92 table"
    light.write_parquet(OUT / "exfor_capture_Z1-25_trust.parquet")

    cells = cells_from_parquet(a.work / "exfor_capture_Z1-25.parquet", verbose=False)
    parts = [split_group_key(k) for k in cells["group_key"].to_list()]
    cells = cells.with_columns(
        nuclide=pl.Series([p[0] for p in parts], dtype=pl.Utf8), mt=pl.Series([p[1] for p in parts], dtype=pl.Int32),
        branch=pl.Series([p[2] for p in parts], dtype=pl.Utf8), kind=pl.Series([p[3] for p in parts], dtype=pl.Utf8),
        state=pl.Series([p[4] for p in parts], dtype=pl.Utf8)).rename({"y": "ln_mean"})
    cells = cells.join(light.select("dataset_key", "trust", "inflation", "year", "decision", "usable"), on="dataset_key", how="left")
    shipc = pl.read_parquet(OUT / "exfor_cells.parquet")
    cells = cells.select(shipc.columns).cast(shipc.schema)
    cells.write_parquet(OUT / "exfor_cells_Z1-25.parquet")

    # check: joint-run decisions on Z 26-92 against the shipped 2026-09-12 curation (newer staging, more human lines)
    m = ship.select("dataset_key", pl.col("decision").alias("a")).join(
        q.filter(pl.col("target_z") >= 26).select("dataset_key", pl.col("decision").alias("b")), on="dataset_key", how="inner")
    agree = (m["a"] == m["b"]).mean()
    dec = collections.Counter(light["decision"].to_list())
    prov = {
        "built": time.strftime("%Y-%m-%d"),
        "script": "scripts/build_light_curation.py",
        "curation": "WP-12 quality_model (research repository data/curate/quality_model.py), unchanged, run on Z 1-92 jointly; Z 1-25 rows kept",
        "research_commit": subprocess.run(["git", "-C", str(a.main), "log", "-1", "--format=%h"], capture_output=True, text=True).stdout.strip(),
        "staging": {"source": f"staging/{ALL}", "entry_zip": "2026-10-14", "sha256": sha(a.main / "staging" / ALL),
                    "check": f"same predicate + clip on Z 26-92 reproduces staging/{HEAVY} exactly"},
        "light_datasets": light.height, "light_cells": cells.height,
        "decisions": dict(dec), "human_decisions_on_light": 0,
        "gates_joint_run": {k: v.get("pass") for k, v in res.gates.items()},
        "z26_92_joint_vs_shipped_decision_agreement": round(float(agree), 4),
        "note": "resampling_stability also fails for a Z 26-92-only run with the same staging and review file, so it is not caused by the light data",
    }
    (OUT / "exfor_capture_Z1-25_provenance.json").write_text(json.dumps(prov, indent=1) + "\n")
    print(json.dumps(prov, indent=1))


if __name__ == "__main__":
    main()
