#!/usr/bin/env python3
"""WP-10: join RIPL-4 + ENSDF into the Tier 2 staging tables.

Outputs (all under ``staging/``):

* ``structure_params.parquet`` — one :class:`~data.schema.StructureParams` row per
  nuclide that has at least one RIPL-4 Tier 2 parameter (~9k rows). Keying convention
  is in the ``StructureParams`` docstring: resonance statistics sit on the COMPOUND
  nucleus row, everything else on the nuclide itself.
* ``levels.parquet`` — ENSDF adopted levels (one row per level; see
  :mod:`data.ingest.ensdf`), ``ensdf_datasets.parquet`` (one row per dataset with Sn/Sp),
  ``level_counts.parquet`` (N(E) summary, count below the RIPL cutoff vs RIPL ``Nmax``,
  discrete spin cutoff).
* ``ripl/*.parquet`` — every parsed RIPL-4 segment table as-is, for reuse by other work
  packages (mass models for WP-04, OMP coefficient tables, GSF inventory, ...).

Usage::

    uv run python -m data.ingest.build_structure                 # full build (~2 min)
    uv run python -m data.ingest.build_structure --skip-ensdf    # RIPL only
    uv run python -m data.ingest.build_structure --ensdf-members ensdf.056 ensdf.238
    uv run python -m data.ingest.build_structure --prefer bnl    # BNL-2018 resonance column first
"""

from __future__ import annotations

import argparse
import logging
import math
import sys
import time
from pathlib import Path

import polars as pl

from data.ingest import ensdf as E
from data.ingest import ripl as R
from data.schema import FissionBarrier, Lorentzian, Param, Source, StructureParams

log = logging.getLogger("build_structure")

REPO = Path(__file__).resolve().parents[2]
STAGING = REPO / "staging"
KD03_IREF = 2405  # Koning-Delaroche 2003 global neutron potential in the RIPL OMP library


def _param(value, sigma=None, source: Source = Source.MEASURED) -> Param | None:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return None
    if sigma is not None and (math.isnan(sigma) or sigma < 0):
        sigma = None
    return Param(value=float(value), sigma=None if sigma is None else float(sigma), source=source)


def _by_zn(df: pl.DataFrame, zcol: str = "Z", ncol: str = "N") -> dict[tuple[int, int], dict]:
    return {(int(r[zcol]), int(r[ncol])): r for r in df.iter_rows(named=True)}


# --------------------------------------------------------------------------- RIPL side


def load_ripl(root: Path, prefer: str) -> dict[str, pl.DataFrame]:
    """Parse every RIPL-4 segment once; returns a name → DataFrame dict."""
    t = time.time()
    tabs: dict[str, pl.DataFrame] = {}
    tabs["resonances_L0"] = R.read_resonances(root, 0)
    tabs["resonances_L1"] = R.read_resonances(root, 1)
    tabs["resonance_params"] = R.resonance_params(root, prefer=prefer)
    tabs["levels_param"] = R.read_levels_param(root)
    tabs["level_headers"] = R.read_level_headers(root)
    tabs["ripl_levels"] = R.read_discrete_levels(root)
    tabs["egsm"] = R.read_egsm(root)
    tabs["egsm_norm"] = R.read_egsm_norm(root)
    tabs["shell_corrections"] = R.read_shell_corrections(root)
    for m in ("bskg3", "bsk14", "thfb"):
        tabs[f"comb_ld_{m}"] = R.read_comb_ld(root, m)
    for m in ("slo", "smlo"):
        tabs[f"gdr_{m}"] = R.gdr_params(root, m)
        tabs[f"gdr_exp_{m}"] = R.read_gdr_exp(root, m)
    tabs["gsf_index"] = R.list_gsf_tables(root)
    tabs["fission_empirical"] = R.read_fission_empirical(root)
    tabs["fission_empire"] = R.read_fission_empire(root)
    tabs["fission_bskg3"] = R.read_fission_bskg3(root)
    tabs["fission_d1m"] = R.read_fission_d1m(root)
    for w in R.WMM_FILES:
        tabs[f"fission_wmm_{w}"] = R.read_fission_wmm(root, w)
    for m in R.list_mass_models(root):
        tabs[f"mass_{m}"] = R.read_mass_table(root, m)
    tabs["abundances"] = R.read_abundances(root)
    tabs["gs_deformations"] = R.read_gs_deformations(root)
    tabs["omp_index"] = R.read_optical_index(root)
    tabs["omp_references"] = R.read_optical_references(root)
    tabs["omp_entries"], tabs["omp_terms"] = R.read_optical_potentials(root)
    log.info("RIPL-4 parsed in %.1f s", time.time() - t)
    return tabs


def _gdr_components(row: dict) -> list[Lorentzian]:
    src = Source(row["source"])
    out = []
    for k in ("1", "2"):
        e = row[f"er{k}_mev"]
        if e is None or e <= 0:
            continue
        out.append(
            Lorentzian(
                energy_mev=_param(e, row.get(f"er{k}_sigma_mev"), src),
                width_mev=_param(row[f"wr{k}_mev"], row.get(f"wr{k}_sigma_mev"), src),
                sigma_mb=_param(row[f"csp{k}_mb"], row.get(f"csp{k}_sigma_mb"), src),
            )
        )
    return out


def _barriers(emp: dict | None, hfb: dict | None) -> list[FissionBarrier]:
    if emp is not None:
        out = [
            FissionBarrier(
                index=1,
                height_mev=_param(emp["Va_mev"], emp["dVa_mev"]),
                curvature_mev=_param(emp["hwa_mev"], emp["dhwa_mev"]),
            )
        ]
        if emp["Vb_mev"] is not None:
            out.append(
                FissionBarrier(
                    index=2,
                    height_mev=_param(emp["Vb_mev"], emp["dVb_mev"]),
                    curvature_mev=_param(emp["hwb_mev"], emp["dhwb_mev"]),
                )
            )
        return out
    if hfb is not None:
        out = []
        for idx, key in ((1, "inner_mev"), (2, "outer1_mev"), (3, "outer2_mev")):
            if hfb[key] and hfb[key] > 0:
                out.append(
                    FissionBarrier(
                        index=idx, height_mev=_param(hfb[key], None, Source.SYSTEMATICS)
                    )
                )
        return out
    return []


def build_structure_params(tabs: dict[str, pl.DataFrame]) -> list[StructureParams]:
    """Join the RIPL-4 tables into one ``StructureParams`` per nuclide."""
    rp = tabs["resonance_params"].with_columns((pl.col("N") + 1).alias("N_compound"))
    res = _by_zn(rp, "Z", "N_compound")
    lp = _by_zn(tabs["levels_param"])
    eg = _by_zn(tabs["egsm"])
    gdr = _by_zn(tabs["gdr_slo"])
    fe = _by_zn(tabs["fission_empirical"])
    fb = _by_zn(tabs["fission_bskg3"])
    omp = tabs["omp_entries"].filter(
        (pl.col("Zproj") == 0) & (pl.col("Aproj") == 1) & pl.col("parse_ok")
    )
    omp_rows = omp.select("iref", "Zmin", "Zmax", "Amin", "Amax").to_dicts()

    keys = set(res) | set(lp) | set(eg) | set(gdr) | set(fe) | set(fb)
    keys = {k for k in keys if k[0] > 0 and k[1] >= 0}
    records = []
    for Z, N in sorted(keys):
        A = Z + N
        key = (Z, N)
        r, p, e = res.get(key), lp.get(key), eg.get(key)
        g, f, b = gdr.get(key), fe.get(key), fb.get(key)
        kw: dict = {"Z": Z, "N": N, "source_version": R.RIPL_VERSION}
        if e is not None:
            kw["ld_model"] = "EGSM"
            kw["ld_a"] = _param(e["a_exp"], max(e["a_plus"], e["a_minus"]))
        if p is not None:
            kw["n_discrete_levels"] = int(p["Nmax"])
            kw["level_cutoff_mev"] = float(p["Umax_mev"])
            if p["ct_T_mev"] and p["ct_T_mev"] > 0:
                kw["ct_temperature_mev"] = _param(p["ct_T_mev"], p["ct_dT_mev"])
                kw["ct_e0_mev"] = _param(p["ct_U0_mev"], p["ct_dU0_mev"])
            if p["sigma_discrete"] and p["sigma_discrete"] > 0:
                kw["discrete_spin_cutoff"] = float(p["sigma_discrete"])
        if r is not None:
            kw["d0_ev"] = _param(r["d0_ev"], r["d0_sigma_ev"])
            kw["d1_ev"] = _param(r["d1_ev"], r["d1_sigma_ev"])
            kw["s0"] = _param(r["s0"], r["s0_sigma"])
            kw["s1"] = _param(r["s1"], r["s1_sigma"])
            kw["gamma_gamma_mev"] = _param(r["gg_mev"], r["gg_sigma_mev"])
            origin_keys = ("d0_origin", "s0_origin", "gg_origin", "d1_origin", "s1_origin")
            origins = {r[k] for k in origin_keys}
            origins.discard(None)
            origin = "/".join(sorted(origins))
            kw["source_version"] = f"{R.RIPL_VERSION}; resonances={origin}"
        if g is not None:
            kw["gsf_model"] = "SLO"
            kw["gdr"] = _gdr_components(g)
        kw["fission_barriers"] = _barriers(f, b)
        irefs = sorted(
            o["iref"] for o in omp_rows
            if o["Zmin"] <= Z <= o["Zmax"] and o["Amin"] <= A <= o["Amax"]
        )  # fmt: skip
        if irefs:
            kw["omp_irefs"] = irefs
            kw["omp_form"] = "KD03" if KD03_IREF in irefs else "RIPL-local"
        records.append(StructureParams(**kw))
    return records


# --------------------------------------------------------------------------- checks


def gdr_systematics_outliers(gdr: pl.DataFrame, tol: float = 0.15) -> pl.DataFrame:
    """Measured GDR rows whose centroid energy deviates > ``tol`` from
    E = 31.2 A^-1/3 + 20.6 A^-1/6 MeV (plan step 5)."""
    m = gdr.filter(pl.col("is_experimental") == 1).with_columns(
        (31.2 * pl.col("A") ** (-1 / 3) + 20.6 * pl.col("A") ** (-1 / 6)).alias("e_sys"),
        pl.when(pl.col("er2_mev") > 0)
        .then(
            (pl.col("er1_mev") * pl.col("s1_trk") + pl.col("er2_mev") * pl.col("s2_trk"))
            / (pl.col("s1_trk") + pl.col("s2_trk"))
        )
        .otherwise(pl.col("er1_mev"))
        .alias("e_centroid"),
    )
    m = m.with_columns(((pl.col("e_centroid") - pl.col("e_sys")) / pl.col("e_sys")).alias("dev"))
    return m.filter(pl.col("dev").abs() > tol).select("Z", "A", "e_centroid", "e_sys", "dev")


def resonance_evaluation_disagreements(res0: pl.DataFrame, factor: float = 1.5) -> pl.DataFrame:
    """Targets where the RIPL-3 and BNL-2018 D0 differ by more than ``factor``."""
    both = res0.filter(pl.col("d_ripl3_ev").is_not_null() & pl.col("d_bnl_ev").is_not_null())
    both = both.with_columns((pl.col("d_ripl3_ev") / pl.col("d_bnl_ev")).alias("ratio"))
    return both.filter((pl.col("ratio") > factor) | (pl.col("ratio") < 1 / factor)).select(
        "Z", "A", "symbol", "d_ripl3_ev", "d_bnl_ev", "ratio"
    )


# --------------------------------------------------------------------------- driver


def build(
    root: Path = R.RIPL4_ROOT,
    ensdf_zip: Path = E.ENSDF_ZIP,
    out_dir: Path = STAGING,
    prefer: str = "ripl3",
    skip_ensdf: bool = False,
    ensdf_members: list[str] | None = None,
    write_segments: bool = True,
) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    tabs = load_ripl(root, prefer)
    if write_segments:
        seg_dir = out_dir / "ripl"
        seg_dir.mkdir(exist_ok=True)
        for name, df in tabs.items():
            df.write_parquet(seg_dir / f"{name}.parquet")

    records = build_structure_params(tabs)
    StructureParams.write_parquet(records, out_dir / "structure_params.parquet")

    summary: dict = {
        "n_structure_rows": len(records),
        "n_measured_d0": sum(r.d0_ev is not None for r in records),
        "n_measured_s0": sum(r.s0 is not None for r in records),
        "n_measured_gg": sum(r.gamma_gamma_mev is not None for r in records),
        "n_measured_d1": sum(r.d1_ev is not None for r in records),
        "n_measured_s1": sum(r.s1 is not None for r in records),
        "n_ld_a": sum(r.ld_a is not None for r in records),
        "n_ct_fit": sum(r.ct_temperature_mev is not None for r in records),
        "n_gdr_measured": sum(
            bool(r.gdr) and r.gdr[0].energy_mev.source == Source.MEASURED for r in records
        ),
        "n_gdr_systematics": sum(
            bool(r.gdr) and r.gdr[0].energy_mev.source == Source.SYSTEMATICS for r in records
        ),
        "n_fission_empirical": sum(
            bool(r.fission_barriers)
            and r.fission_barriers[0].height_mev.source == Source.MEASURED
            for r in records
        ),
        "n_fission_hfb": sum(
            bool(r.fission_barriers)
            and r.fission_barriers[0].height_mev.source == Source.SYSTEMATICS
            for r in records
        ),
        "n_omp_kd03": sum(r.omp_form == "KD03" for r in records),
        "n_omp_local_only": sum(r.omp_form == "RIPL-local" for r in records),
        "ripl_dropped": {k: len(v) for k, v in R.DROPPED.items()},
        "gdr_outliers": gdr_systematics_outliers(tabs["gdr_slo"]).height,
        "d0_ripl3_vs_bnl_disagree": resonance_evaluation_disagreements(
            tabs["resonances_L0"]
        ).height,
    }
    nuc_path = out_dir / "nuclides.parquet"
    if nuc_path.exists():
        nuc = pl.read_parquet(nuc_path, columns=["nuclide_id"])
        ids = {r.nuclide_id for r in records}
        summary["n_matching_wp04_nuclides"] = len(ids & set(nuc["nuclide_id"].to_list()))

    if not skip_ensdf:
        t = time.time()
        levels, datasets = E.read_adopted_levels(ensdf_zip, ensdf_members)
        counts = E.level_counts(levels, tabs["levels_param"])
        levels.write_parquet(out_dir / "levels.parquet")
        datasets.write_parquet(out_dir / "ensdf_datasets.parquet")
        counts.write_parquet(out_dir / "level_counts.parquet")
        cmp = counts.filter(pl.col("ripl_nmax").is_not_null())
        summary.update(
            {
                "n_ensdf_adopted_datasets": datasets.height,
                "n_ensdf_levels": levels.height,
                "n_ensdf_levels_unknown_energy": levels.filter(
                    pl.col("energy_offset").is_not_null()
                ).height,
                "n_ensdf_unparsed_jpi_strings": len(E.UNPARSED_JPI),
                "n_nuclides_compared_to_ripl_nmax": cmp.height,
                "frac_matching_ripl_nmax": float(cmp["matches_ripl_nmax"].mean())
                if cmp.height
                else None,
                "frac_within_1_of_ripl_nmax": float(
                    ((cmp["n_below_umax"] - cmp["ripl_nmax"]).abs() <= 1).mean()
                ) if cmp.height else None,
                "frac_matching_ripl_nmax_firm": float(
                    (cmp["n_below_umax_firm"] == cmp["ripl_nmax"]).mean()
                ) if cmp.height else None,
                "ensdf_seconds": round(time.time() - t, 1),
            }
        )
    return summary


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--root", type=Path, default=R.RIPL4_ROOT)
    ap.add_argument("--ensdf", type=Path, default=E.ENSDF_ZIP)
    ap.add_argument("--out", type=Path, default=STAGING)
    ap.add_argument("--prefer", choices=["ripl3", "bnl"], default="ripl3")
    ap.add_argument("--skip-ensdf", action="store_true")
    ap.add_argument("--ensdf-members", nargs="*", default=None, help="e.g. ensdf.056 ensdf.238")
    ap.add_argument(
        "--no-segments", action="store_true", help="do not write staging/ripl/*.parquet"
    )
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args(argv)
    logging.basicConfig(
        level=logging.INFO if args.verbose else logging.WARNING,
        format="%(levelname)s %(name)s: %(message)s",
    )
    summary = build(
        args.root, args.ensdf, args.out, args.prefer, args.skip_ensdf, args.ensdf_members,
        not args.no_segments,
    )
    print("WP-10 build summary")
    for k, v in summary.items():
        print(f"  {k:36s} {v}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
