"""Load the EXFOR-derived inputs of the curation rule: cells, per-dataset BIB flags, RIPL D0, record findings."""
from __future__ import annotations

import json
import re
from collections import defaultdict

import numpy as np
import polars as pl

from . import exfor_text, paths

DERIVED = ("DERIV", "CALC", "EVAL", "RECOM")
MAGIC_N = (28, 50, 82, 126)


def load_cells() -> pl.DataFrame:
    """Capture cells (dataset x 0.1-dex bin), usable, value > 0, with BIB flags joined. ``gs`` marks ground-state
    total capture (state '' and branch ''), the only cells the data rules test or use as references; record and
    identity rules (R1-R4, R8) also reach partial / isomeric-state datasets."""
    c = pl.read_parquet(paths.CELLS).filter((pl.col("mt") == 102) & pl.col("usable") & (pl.col("mean_b") > 0))
    t = pl.read_parquet(paths.TRUST, columns=[
        "dataset_key", "entry", "subentry", "pointer", "target_z", "target_a", "sf9", "is_calc_eval",
        "is_compilation", "first_author", "facility", "detector", "year", "trust"]).rename({"year": "ds_year"})
    c = c.drop("trust", "year").join(t, on="dataset_key", how="left")
    stat = np.nan_to_num(c["stat_rel"].to_numpy(), nan=0.0)
    sys_ = np.nan_to_num(c["sys_rel"].to_numpy(), nan=0.0)
    sem = np.nan_to_num(c["sem_rel"].to_numpy(), nan=0.0)
    rel = np.sqrt(stat ** 2 + sys_ ** 2)
    no_unc = (rel <= 0) & (sem <= 0)
    rel = np.where(rel > 0, rel, np.where(sem > 0, sem, 0.10))
    derived = (c["sf9"].fill_null("").str.contains("|".join(DERIVED)) | c["is_calc_eval"].fill_null(False))
    return c.with_columns(
        x=pl.col("mean_b").log10(), sig_x=pl.Series(np.log10(1 + rel)), no_unc=pl.Series(no_unc),
        derived=derived, gs=(pl.col("state") == "") & (pl.col("branch") == ""), n_neut=(pl.col("target_a") - pl.col("target_z")).cast(pl.Int32))


def ripl_d0() -> dict[tuple[int, int], float]:
    """(Z, A) of the TARGET -> RIPL s-wave spacing D0 in eV (RIPL-3 column, else the BNL column)."""
    pat = re.compile(r"^\s*(\d+)\s+(\d+)\s+(\d+)\s+(\S+)\s+(\d+)\s+(\S+)\s+([+-])")
    out = {}
    for ln in paths.RIPL_D0.read_text().splitlines():
        if ln.startswith("#"):
            continue
        m = pat.match(ln)
        if not m:
            continue
        rest = ln[m.end():]
        f = [rest[10 + 12 * i:22 + 12 * i].strip() for i in range(4)]
        d = f[0] or f[2]
        if d:
            out[(int(m.group(1)), int(m.group(3)))] = float(d)
    return out


def e_stat(z: int, a: int, d0: dict[tuple[int, int], float]) -> tuple[float, str]:
    """Lower edge of the statistical region, max(1 keV, 40 D0), and where D0 came from (rule v2 §1)."""
    if (z, a) in d0:
        return max(1e3, 40 * d0[(z, a)]), "ripl"
    n = a - z
    near = [v for (zz, aa), v in d0.items() if zz % 2 == z % 2 and (aa - zz) % 2 == n % 2 and abs(aa - a) <= 10]
    if near:
        return max(1e3, 40 * float(np.median(near))), f"parity-median of {len(near)}"
    return 1e5, "default 100 keV"


def near_magic(n: int) -> bool:
    return any(abs(n - m) <= 2 for m in MAGIC_N)


def record_findings() -> list[dict]:
    """The RECORD family; every quote is re-checked against entry.zip (the build refuses to run otherwise)."""
    F = [json.loads(l) for l in paths.RECORD_FINDINGS.read_text().splitlines() if l.strip()]
    bad = [(f["id"], q["text"]) for f in F for q in f["quotes"]
           if not exfor_text.quote_found(f["entry"], q["subentry"], q["text"])]
    if bad:
        raise SystemExit(f"record findings whose quote is not in the EXFOR record: {bad}")
    return F


def points_of(keys: set[str]) -> dict[str, list[tuple[float, float]]]:
    """dataset_key -> EXFOR points (e_ev, value_b) from the staged capture table (renormalised values if staged)."""
    lf = pl.scan_parquet(paths.POINTS).with_columns(
        dataset_key=pl.col("entry") + "/" + pl.col("subentry") + "/" + pl.col("pointer").fill_null(""))
    df = lf.filter(pl.col("dataset_key").is_in(sorted(keys))).select(
        "dataset_key", "energy_ev", pl.col("original").struct.field("values").alias("orig"),
        pl.col("renormalized").struct.field("values").alias("ren")).collect()
    out = defaultdict(list)
    for r in df.iter_rows(named=True):
        vals = r["ren"] if r["ren"] else r["orig"]
        for e, v in zip(r["energy_ev"] or [], vals or []):
            if e is not None and v is not None:
                out[r["dataset_key"]].append((float(e), float(v)))
    return out
