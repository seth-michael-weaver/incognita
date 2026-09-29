#!/usr/bin/env python3
"""A8: the photonuclear (gamma,n) subset of EXFOR, as a measured constraint on the PSF.

Why this channel and not another. The register's rule is that information helps only when it is
a measurement of the same physical quantity the model predicts. By detailed balance the E1
gamma-ray strength function that sets neutron capture BELOW the neutron separation energy is the
same function that sets photodisintegration ABOVE it, and the (gamma,n) threshold *is* S_n --
so the lowest-energy photoneutron points sit at exactly the gamma energy that dominates keV
capture on the A-1 target. Photonuclear data on nucleus X constrains the PSF of X, which is the
compound nucleus of n + (X-1). That is the pairing this module builds.

Source. `staging/exfor_all.parquet` -- the full EXFOR parse that `data/ingest/exfor.py` already
produced from `raw/exfor/entry.zip`. Nothing is re-downloaded and nothing is re-parsed; this is
a subset filter over columns that already exist, in the same shape as the per-channel staging
parquets (`exfor_capture_Z26-92.parquet` and friends), so `data/curate/discrepancy.py` runs over
it unchanged.

The subset, and why the two reaction codes are pooled:

  * ``(G,N)`` SIG        -- the photoneutron cross section (881 datasets in EXFOR, 512 of them
                            surviving the cuts below);
  * ``(G,X)`` -> 0-NN-1  -- the photoneutron *yield* sigma(g,n) + 2 sigma(g,2n) (788 / 562),
                            which is the form nearly all of the Saclay and Livermore GDR
                            campaigns were compiled in.

Below the two-neutron separation energy those are the same number, because the (g,2n) channel is
closed. The table is therefore **cut at S_2n** (and at S_n from below), which is also the window
the anchor wants: the strength function near S_n, not at the GDR peak. Above S_2n the two codes
measure different things and pooling them would be a unit error, so they are simply not kept.

``(G,ABS)`` and ``(G,TOT)`` are written too, under ``kind = "absorption"``, as an independent
cross-check -- below S_2n they exceed (g,n) only by the Coulomb-suppressed (g,p), which for
Z >= 26 is a few percent. They are NOT pooled into the primary group.

What is deliberately not done here: the 30-year Saclay/Livermore normalisation discrepancy
(positron-annihilation photon sources at Saclay read systematically ~10-20% above Livermore for
the same nucleus) is left in the data, for `data/curate/discrepancy.py` to see as between-dataset
spread and price into `sigma_log`. Hiding it would understate the anchor's own uncertainty, which
is the one number the A/B in `scripts/photonuc_anchor.py` cannot afford to get wrong.

    uv run python data/ingest/exfor_photonuclear.py --zmin 26 --zmax 92
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import polars as pl

REPO = Path(__file__).resolve().parents[2]

# ENDF MT for (gamma,n) as TALYS's own photonuclear output labels it (xs100000.tot -> MT 4);
# the yield form is carried in `kind`, not in MT, because below S_2n it is the same quantity.
MT_GN = 4


def build(source: Path, zmin: int, zmax: int) -> tuple[pl.DataFrame, dict]:
    cols = pl.scan_parquet(source).collect_schema().names()
    d = pl.scan_parquet(source).filter(pl.col("projectile") == "g").collect()
    d = d.with_columns(
        [pl.col("sf").struct.field(f"sf{i}").alias(f"_sf{i}") for i in (3, 4, 5, 6, 8)]
    )
    d = d.filter(
        pl.col("_sf6") == "SIG",
        pl.col("target_iso") == 0,
        pl.col("target_a") > 0,
        pl.col("target_z").is_between(zmin, zmax),
        # No branch (SF5): a PAR or partial photoneutron cross section is not the total.
        pl.col("_sf5").is_null(),
        # Monoenergetic photon beams only. `BRS`/`BRA` are bremsstrahlung and are reported
        # against the *endpoint* energy of the beam, not the photon energy -- pooling them with
        # annihilation-photon data would compare two different independent variables. On Fe-54
        # that mixture put three consensus values a factor of six apart in one 10-per-decade bin.
        pl.col("_sf8").is_null() | (pl.col("_sf8") == "AV"),
        # Total (g,n), not an isomer partial: the residual must be a bare ground-state nuclide.
        pl.col("_sf4").is_null() | ~pl.col("_sf4").str.contains(r"-(M|M1|M2|G|L)$"),
    )
    is_gn = pl.col("_sf3") == "N"
    is_yield = (pl.col("_sf3") == "X") & (pl.col("_sf4") == "0-NN-1")
    is_abs = pl.col("_sf3").is_in(["ABS", "TOT"])
    d = d.filter(is_gn | is_yield | is_abs)

    nuc = pl.read_parquet(
        REPO / "staging" / "nuclides.parquet", columns=["Z", "N", "iso", "sn_kev", "s2n_kev"]
    ).filter(pl.col("iso") == 0)
    nuc = nuc.with_columns((pl.col("Z") + pl.col("N")).alias("A")).select(
        pl.col("Z").alias("target_z"), pl.col("A").cast(pl.Int16).alias("target_a"),
        pl.col("sn_kev").struct.field("value").alias("sn_kev"),
        pl.col("s2n_kev").struct.field("value").alias("s2n_kev"))
    d = d.join(nuc, on=["target_z", "target_a"], how="left")

    kind = (
        pl.when(is_abs).then(pl.lit("absorption"))
        .when(is_yield).then(pl.lit("yield"))
        .otherwise(pl.lit("gn"))
    )
    d = d.with_columns(kind.alias("_kind"), pl.lit(MT_GN, dtype=pl.Int32).alias("mt"))

    # Cut every dataset to [S_n, S_2n]: the window where (g,n), the (g,xn) yield and photo-
    # absorption are one quantity, and the window the PSF anchor is about.
    out_rows = []
    stats = {"datasets_in": d.height, "kept": 0, "dropped_no_sep": 0, "dropped_empty": 0,
             "points_in": 0, "points_kept": 0}
    for r in d.iter_rows(named=True):
        sn, s2n = r["sn_kev"], r["s2n_kev"]
        e = r["energy_ev"]
        stats["points_in"] += len(e or [])
        if sn is None or s2n is None or not e:
            stats["dropped_no_sep"] += 1
            continue
        lo, hi = float(sn) * 1e3, float(s2n) * 1e3
        blk = r["renormalized"] or r["original"]
        if blk is None or (blk["units"] or "").upper() not in ("B", "MB", "MICRO-B", "BARNS"):
            # `renormalized` is already in barns when it exists; `original` is only usable if its
            # unit is an area. Anything else (ratios, arbitrary units) is not a cross section.
            if blk is None or r["renormalized"] is None:
                stats["dropped_empty"] += 1
                continue
        blk = r["renormalized"]
        if blk is None:
            stats["dropped_empty"] += 1
            continue
        vals = blk["values"]
        idx = [i for i, ev in enumerate(e)
               if ev is not None and lo <= float(ev) <= hi
               and vals[i] is not None and float(vals[i]) > 0]
        if len(idx) < 1:
            stats["dropped_empty"] += 1
            continue

        def take(lst, idx=idx):
            return None if lst is None else [lst[i] for i in idx]

        row = {k: r[k] for k in cols if k not in ("energy_ev", "original", "renormalized",
                                                  "angle_deg", "secondary_energy_ev",
                                                  "energy_sigma_ev")}
        row["energy_ev"] = [float(e[i]) for i in idx]
        row["energy_sigma_ev"] = take(r["energy_sigma_ev"])
        row["angle_deg"] = None
        row["secondary_energy_ev"] = None
        row["mt"] = MT_GN
        for name in ("original", "renormalized"):
            b = r[name]
            row[name] = None if b is None else {
                "values": take(b["values"]), "stat_sigma": take(b["stat_sigma"]),
                "sys_sigma": take(b["sys_sigma"]), "units": b["units"],
                "standards_version": b["standards_version"]}
        row["_kind"] = r["_kind"]
        out_rows.append(row)
        stats["kept"] += 1
        stats["points_kept"] += len(idx)

    out = pl.DataFrame(out_rows, infer_schema_length=None)
    stats["nuclides"] = out.select("target_z", "target_a").unique().height if out.height else 0
    stats["by_kind"] = (out["_kind"].value_counts().to_dicts() if out.height else [])
    return out, stats


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", type=Path, default=REPO / "staging" / "exfor_all.parquet")
    ap.add_argument("--zmin", type=int, default=26)
    ap.add_argument("--zmax", type=int, default=92)
    ap.add_argument("--out", type=Path,
                    default=REPO / "staging" / "exfor_photonuclear_Z26-92.parquet")
    a = ap.parse_args(argv)

    out, stats = build(a.source, a.zmin, a.zmax)
    out.write_parquet(a.out)
    Path(str(a.out).replace(".parquet", "_summary.json")).write_text(json.dumps(stats, indent=1))
    print(json.dumps(stats, indent=1))
    print(f"[photonuc] -> {a.out}")


if __name__ == "__main__":
    main()
