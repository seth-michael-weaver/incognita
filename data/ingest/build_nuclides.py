"""WP-04 step 3: join AME2020 + NUBASE2020 into ``staging/nuclides.parquet`` (validated
:class:`data.schema.Nuclide` rows) and build ``features/nuclide_features.parquet`` (the chart
encoder input: :mod:`physics.features` columns + mass-model predictions + AME targets).

    uv run python -m data.ingest.build_nuclides            # writes both tables, prints summary
    uv run python -m data.ingest.build_nuclides --no-write  # dry run

Join rule: every NUBASE entry (Z, N, iso) is a row. For ground states the mass excess,
binding energy and separation energies come from AME (unrounded); for isomers the mass
excess comes from NUBASE. NUBASE "non-exist" isomers are dropped.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from data.ingest.ame import load_ame
from data.ingest.nubase import load_nubase
from data.schema.nuclide import DECAY_MODES, Datum, DecayBranch, Nuclide
from physics.features import FEATURE_NAMES, feature_table
from physics.massmodels import baseline_rms, format_baseline_table, load_all, mass_model_table

__all__ = [
    "FEATURES_PATH",
    "STAGING_PATH",
    "build_feature_table",
    "build_nuclide_records",
    "main",
    "summary",
]

REPO = Path(__file__).resolve().parents[2]
STAGING_PATH = REPO / "staging" / "nuclides.parquet"
FEATURES_PATH = REPO / "features" / "nuclide_features.parquet"
SOURCE_VERSION = "AME2020+NUBASE2020"


def _datum(value: float, sigma: float | None = None, extrapolated: bool = False) -> Datum | None:
    if value is None or (isinstance(value, float) and math.isnan(value)) or pd.isna(value):
        return None
    if sigma is not None and (pd.isna(sigma) or sigma < 0):
        sigma = None
    return Datum(
        value=float(value),
        sigma=None if sigma is None else float(sigma),
        extrapolated=bool(extrapolated),
    )


def _opt(v: Any) -> Any:
    """pandas NA/NaN -> None."""
    if v is None:
        return None
    try:
        if pd.isna(v):
            return None
    except (TypeError, ValueError):
        pass
    return v


def _branches(modes: list[dict[str, Any]]) -> tuple[list[DecayBranch], dict[str, Datum]]:
    """NUBASE decay dicts -> DecayBranch list (fractions) and Pn/P2n data where quoted."""
    out: list[DecayBranch] = []
    pn: dict[str, Datum] = {}
    for m in modes:
        mode = m["mode"]
        if mode not in DECAY_MODES:
            raise ValueError(
                f"decay mode {mode!r} not in DECAY_MODES; extend data/schema/nuclide.py"
            )
        br = m["branching_pct"]
        frac = None if br is None or math.isnan(br) else min(br / 100.0, 1.0)
        sig = m["sigma_pct"]
        sig = None if sig is None or math.isnan(sig) else sig / 100.0
        out.append(DecayBranch(mode=mode, branching=frac, sigma=sig, qualifier=m["qualifier"]))
        if mode in ("B-n", "B-2n") and frac is not None and m["qualifier"] in ("=", "~"):
            key = "pn" if mode == "B-n" else "p2n"
            pn[key] = Datum(value=frac, sigma=sig, extrapolated=bool(m.get("extrapolated", False)))
    return out, pn


def build_nuclide_records(
    ame: pd.DataFrame | None = None, nubase: pd.DataFrame | None = None
) -> list[Nuclide]:
    """Join and validate. Raises with the offending rows if any record fails the schema."""
    ame = load_ame() if ame is None else ame
    nubase = load_nubase() if nubase is None else nubase
    ame_idx = ame.set_index(["Z", "N"])
    ame_keys = set(ame_idx.index)
    nb = nubase[~nubase["non_existent"]]
    seen: set[tuple[int, int, int]] = set()
    records: list[Nuclide] = []
    errors: list[str] = []
    for r in nb.itertuples(index=False):
        key = (int(r.Z), int(r.N), int(r.iso))
        seen.add(key)
        row: dict[str, Any] = {
            "Z": key[0],
            "N": key[1],
            "iso": key[2],
            "symbol": r.symbol or None,
            "source_version": SOURCE_VERSION,
            "spin": _opt(r.spin),
            "parity": None if _opt(r.parity) is None else int(r.parity),
            "spin_parity_tentative": bool(r.spin_parity_tentative),
            "spin_parity_raw": _opt(r.spin_parity_raw),
            "is_stable": bool(r.is_stable),
            "ensdf_year": None if _opt(r.ensdf_year) is None else int(r.ensdf_year),
            "discovery_year": None if _opt(r.discovery_year) is None else int(r.discovery_year),
        }
        if key[2] != 0:
            row["excitation_energy_kev"] = _datum(
                r.excitation_kev, r.excitation_unc_kev, r.excitation_extrapolated
            )
        if key[2] == 0 and (key[0], key[1]) in ame_keys:
            a = ame_idx.loc[(key[0], key[1])]
            row["mass_excess_kev"] = _datum(
                a["mass_excess_kev"], a["mass_excess_unc_kev"], a["mass_excess_extrapolated"]
            )
            row["binding_energy_per_a_kev"] = _datum(
                a["binding_per_a_kev"], a["binding_per_a_unc_kev"], a["binding_per_a_extrapolated"]
            )
            for q in ("sn", "s2n", "sp", "s2p"):
                row[f"{q}_kev"] = _datum(a[f"{q}_kev"], a[f"{q}_unc_kev"], a[f"{q}_extrapolated"])
            if not row["symbol"]:
                row["symbol"] = a["symbol"]
        else:
            row["mass_excess_kev"] = _datum(
                r.mass_excess_kev, r.mass_excess_unc_kev, r.mass_excess_extrapolated
            )
        if not r.is_stable and not math.isnan(r.log10_half_life_s):
            row["log10_half_life_s"] = _datum(
                r.log10_half_life_s, r.log10_half_life_unc, r.half_life_extrapolated
            )
        try:
            branches, pn = _branches(r.decay_modes)
            row["decay_modes"] = branches
            row.update(pn)
            records.append(Nuclide(**row))
        except Exception as e:  # noqa: BLE001 - collect everything, then fail once
            errors.append(f"Z={key[0]} N={key[1]} iso={key[2]}: {e}")
    # AME ground states missing from NUBASE (none in 2020, but keep the join honest)
    for (z, n), a in ame_idx.iterrows():
        if (z, n, 0) in seen:
            continue
        try:
            records.append(
                Nuclide(
                    Z=int(z),
                    N=int(n),
                    iso=0,
                    symbol=a["symbol"],
                    source_version=SOURCE_VERSION,
                    mass_excess_kev=_datum(
                        a["mass_excess_kev"],
                        a["mass_excess_unc_kev"],
                        a["mass_excess_extrapolated"],
                    ),
                    binding_energy_per_a_kev=_datum(
                        a["binding_per_a_kev"],
                        a["binding_per_a_unc_kev"],
                        a["binding_per_a_extrapolated"],
                    ),
                )
            )
        except Exception as e:  # noqa: BLE001
            errors.append(f"Z={z} N={n} iso=0 (AME only): {e}")
    if errors:
        head = "\n".join(errors[:20])
        raise ValueError(f"{len(errors)} rows failed Nuclide validation, e.g.:\n{head}")
    records.sort(key=lambda x: x.key)
    return records


TARGET_COLUMNS = (
    "target_mass_excess_kev",
    "target_mass_excess_sigma_kev",
    "target_is_extrapolated",
    "target_binding_per_a_kev",
    "target_binding_per_a_sigma_kev",
)


def build_feature_table(
    records: list[Nuclide], model_tables: dict[str, pd.DataFrame] | None = None
) -> pa.Table:
    """Ground-state rows -> Arrow table: key, physics features, mass-model columns, targets.

    Column provenance is stored in the Parquet schema metadata under ``column_sources``.
    """
    gs = [r for r in records if r.iso == 0 and r.mass_excess_kev is not None]
    Z = np.array([r.Z for r in gs], dtype=np.int64)
    N = np.array([r.N for r in gs], dtype=np.int64)
    feats = feature_table(Z, N)
    cols: dict[str, Any] = {"nuclide_id": [r.nuclide_id for r in gs]}
    sources: dict[str, str] = {"nuclide_id": "data/schema/keys.py"}
    for name in FEATURE_NAMES:
        cols[name] = feats[name]
        sources[name] = "physics/features.py"
    mm = mass_model_table(Z, N, tables=model_tables)
    for c in mm.columns:
        if c in ("Z", "N"):
            continue
        cols[c] = mm[c].to_numpy(dtype=np.float64)
        sources[c] = mm.attrs["column_sources"][c]
    cols["target_mass_excess_kev"] = np.array([r.mass_excess_kev.value for r in gs])
    cols["target_mass_excess_sigma_kev"] = np.array(
        [np.nan if r.mass_excess_kev.sigma is None else r.mass_excess_kev.sigma for r in gs]
    )
    cols["target_is_extrapolated"] = np.array(
        [r.mass_excess_kev.extrapolated for r in gs], dtype=bool
    )
    cols["target_binding_per_a_kev"] = np.array(
        [
            np.nan if r.binding_energy_per_a_kev is None else r.binding_energy_per_a_kev.value
            for r in gs
        ]
    )
    cols["target_binding_per_a_sigma_kev"] = np.array(
        [
            np.nan
            if r.binding_energy_per_a_kev is None or r.binding_energy_per_a_kev.sigma is None
            else r.binding_energy_per_a_kev.sigma
            for r in gs
        ]
    )
    for c in TARGET_COLUMNS:
        sources[c] = "raw/ame2020/mass_1.mas20.txt"
    table = pa.table(cols)
    meta = {
        b"column_sources": json.dumps(sources).encode(),
        b"feature_names": json.dumps(FEATURE_NAMES).encode(),
        b"source_version": SOURCE_VERSION.encode(),
    }
    return table.replace_schema_metadata({**(table.schema.metadata or {}), **meta})


def summary(records: list[Nuclide], features: pa.Table, rms: pd.DataFrame) -> str:
    gs = [r for r in records if r.iso == 0]
    me = [r for r in gs if r.mass_excess_kev is not None]
    meas = [r for r in me if not r.mass_excess_kev.extrapolated]
    rows = [
        ("NUBASE entries (all states)", len(records)),
        ("  ground states", len(gs)),
        ("  isomers / levels / IAS", len(records) - len(gs)),
        ("ground states with an AME mass", len(me)),
        ("  measured (training set)", len(meas)),
        ("  extrapolated '#' (evaluation set)", len(me) - len(meas)),
        ("stable ground states", sum(r.is_stable for r in gs)),
        ("ground states with half-life", sum(r.log10_half_life_s is not None for r in gs)),
        ("ground states with definite J", sum(r.spin is not None for r in gs)),
        ("ground states with parity", sum(r.parity is not None for r in gs)),
        ("ground states with Pn", sum(r.pn is not None for r in gs)),
        ("feature rows x columns", f"{features.num_rows} x {features.num_columns}"),
    ]
    w = max(len(k) for k, _ in rows)
    out = ["nuclide tables", *[f"  {k:<{w}}  {v:>10}" for k, v in rows]]
    out.append("")
    out.append("mass-model baseline RMS vs AME2020 measured masses (Z, N >= 8)")
    out.append(format_baseline_table(rms))
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--staging", type=Path, default=STAGING_PATH)
    ap.add_argument("--features", type=Path, default=FEATURES_PATH)
    ap.add_argument("--no-write", action="store_true", help="build and validate only")
    args = ap.parse_args(argv)

    ame = load_ame()
    nubase = load_nubase()
    records = build_nuclide_records(ame, nubase)
    tables = load_all()
    features = build_feature_table(records, tables)
    rms = baseline_rms(ame, tables)
    if not args.no_write:
        Nuclide.write_parquet(records, args.staging)
        args.features.parent.mkdir(parents=True, exist_ok=True)
        pq.write_table(features, args.features)
        print(f"wrote {args.staging} ({len(records)} rows)")
        print(f"wrote {args.features} ({features.num_rows} rows, {features.num_columns} cols)")
    print(summary(records, features, rms))
    return 0


if __name__ == "__main__":
    sys.exit(main())
