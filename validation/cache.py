"""Snapshot the inputs of the differential harness under ``features/validation_cache/``.

The WP-11 merged parquets (``staging/evaluated/<lib>.parquet``) are rewritten whenever the
evaluated build finalizes, and each is 50-350 MB because every MT of every material is
stored. The harness only needs one MT at a time (capture by default), the RRR/URR bounds,
the MF33 blocks of that MT and the WP-12 per-dataset cells, so those are copied once into
small parquet files that a run can re-read cheaply:

    features/validation_cache/<lib>_mt<MT>.parquet      grid values + bounds, one row per nuclide
    features/validation_cache/<lib>_cov_mt<MT>.parquet  MF33 relative covariance blocks (flattened)
    features/validation_cache/exfor_cells.parquet       WP-12 cells x trust / year per dataset

    uv run python -u -m validation.cache            # capture (MT 102), all five libraries
    uv run python -u -m validation.cache --mt 102 16 --library tendl2025 jeff33
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import polars as pl

REPO = Path(__file__).resolve().parents[1]
STAGING = REPO / "staging" / "evaluated"
CURATED = REPO / "curated"
CACHE = REPO / "features" / "validation_cache"
EXFOR_SOURCE = REPO / "staging" / "exfor_capture_Z26-92.parquet"

# WP-19: the curation machinery is channel-agnostic -- quality_model takes --source and --tag
# -- but everything downstream of it named the capture files directly. A channel is the tag
# its curated tables were written under; "capture" stays the default so nothing that exists
# has to change.
CHANNEL_TAGS: dict[str, str] = {
    "capture": "exfor_capture_Z26-92",
    "n2n": "exfor_n2n_Z26-92",
    # WP-24: total (n,f), sf4/sf5 empty -- see scripts/wp24_fission_subset.py
    "fission": "exfor_fission_Z88-96",
    "fission_noratio": "exfor_fission_noratio_Z88-96",
    # WP-19: the other neutron channels, SIG only; state/branch are scored "" -- see
    # data/ingest/exfor.py CHANNEL_SF3
    "np": "exfor_np_Z26-92",
    "na": "exfor_na_Z26-92",
    "inelastic": "exfor_inelastic_Z26-92",
    "elastic": "exfor_elastic_Z26-92",
    "total": "exfor_total_Z26-92",
}

# WP-19: threshold channels are scored in log10, and a cell measured at 1e-12 b a few hundred
# keV above threshold (EXFOR 14862007, Zn-68(n,p), 2025) is a factor 10^6 from every library
# and model -- one such dataset set the (n,p) and (n,a) RMS of all seven predictions. Cells
# below this value (in barns) are excluded from training and scoring: 23 of 2,311 usable (n,p)
# cells, 45 of 1,407 (n,a), 20 of 2,458 (n,2n). Capture and the non-threshold channels have
# none, so they get no floor.
CHANNEL_FLOOR_B: dict[str, float] = {"n2n": 1e-5, "np": 1e-5, "na": 1e-5}

# ENDF MT of each WP-19 curated channel (stage_c_data and the surrogate use the same numbers).
CHANNEL_MT: dict[str, int] = {
    "capture": 102,
    "n2n": 16,
    "np": 103,
    "na": 107,
    "inelastic": 4,
    "elastic": 2,
    "total": 1,
}


def channel_source(channel: str = "capture") -> Path:
    return REPO / "staging" / f"{CHANNEL_TAGS[channel]}.parquet"


def channel_trust(channel: str = "capture") -> Path:
    return CURATED / f"{CHANNEL_TAGS[channel]}_trust.parquet"


def channel_consensus(channel: str = "capture") -> Path:
    return CURATED / f"{CHANNEL_TAGS[channel]}_consensus.parquet"

LIBRARIES: dict[str, str] = {
    "endfb81": "ENDF/B-VIII.1",
    "jeff33": "JEFF-3.3",
    "jendl5": "JENDL-5",
    "tendl2025": "TENDL-2025",
    "cendl32": "CENDL-3.2",
    # released December 2011: the only library here that predates the time-split cutoff, so
    # the only one that can be compared with a 2012-cutoff model on equal information
    "endfb71": "ENDF/B-VII.1",
    # also pre-cutoff, for the prior ensemble
    "jendl40": "JENDL-4.0",
    "endfb70": "ENDF/B-VII.0",
    # RETRO: the archived TENDL releases. A TENDL of year Y has not seen a measurement
    # published after Y, which makes it the only rival that is blind where we are blind.
    "tendl2015": "TENDL-2015",
    "tendl2017": "TENDL-2017",
    "tendl2019": "TENDL-2019",
    "tendl2021": "TENDL-2021",
    "tendl2023": "TENDL-2023",
}
# What `build()` caches when it is not told: the archived releases are only needed by the
# retrodiction exam, and adding them to the registry must not lengthen every routine rebuild.
CACHE_DEFAULT: tuple[str, ...] = ("endfb81", "jeff33", "jendl5", "tendl2025", "cendl32",
                                  "endfb71", "jendl40", "endfb70")

XS_COLUMNS = [
    "library",
    "library_version",
    "nuclide_id",
    "Z",
    "N",
    "iso",
    "mt",
    "grid_id",
    "values_b",
    "threshold_ev",
    "resolved_upper_ev",
    "unresolved_upper_ev",
]


def xs_cache_path(lib: str, mt: int) -> Path:
    return CACHE / f"{lib}_mt{mt}.parquet"


def cov_cache_path(lib: str, mt: int) -> Path:
    return CACHE / f"{lib}_cov_mt{mt}.parquet"


def cells_cache_path(channel: str = "capture") -> Path:
    # the capture cache keeps its original name so existing files stay valid
    return CACHE / ("exfor_cells.parquet" if channel == "capture"
                    else f"exfor_cells_{channel}.parquet")



def _fresh(out: Path, *sources: Path) -> bool:
    """True if ``out`` exists and is newer than every source it was built from.

    Without this the caches were keyed on existence alone: once written they were returned
    for ever, and re-ingesting EXFOR or a library left every score reading the previous
    build. Nothing failed and nothing warned -- the new measurements simply did not reach
    the metric. That is the same class of defect as a parameter TALYS accepts and ignores,
    and it is worse here because the affected number is the one the project publishes.
    """
    if not out.is_file():
        return False
    t = out.stat().st_mtime
    return all((not s.is_file()) or s.stat().st_mtime <= t for s in sources)


def cache_library_xs(lib: str, mt: int, *, force: bool = False) -> Path:
    """One MT of one library: grid values and RRR/URR bounds, ground states and isomers."""
    out = xs_cache_path(lib, mt)
    src = STAGING / f"{lib}.parquet"
    if _fresh(out, src) and not force:
        return out
    if not src.is_file():
        raise FileNotFoundError(src)
    CACHE.mkdir(parents=True, exist_ok=True)
    df = (
        pl.scan_parquet(src)
        .filter((pl.col("mt") == mt) & (pl.col("projectile") == "n"))
        .select(XS_COLUMNS)
        .collect()
    )
    tmp = out.with_suffix(".tmp.parquet")
    df.write_parquet(tmp)
    tmp.replace(out)
    return out


def cache_library_cov(lib: str, mt: int, *, force: bool = False) -> Path:
    """MF33 relative covariance blocks of one MT, flattened row-major, one row per nuclide."""
    out = cov_cache_path(lib, mt)
    src = STAGING / f"{lib}_cov.zarr"
    if _fresh(out, src) and not force:
        return out
    import zarr

    rows: list[dict] = []
    if src.is_dir():
        root = zarr.open(str(src), mode="r")
        key = f"mt{mt}"
        for nuc in root.keys():
            grp = root[nuc]
            if key not in grp:
                continue
            blk = grp[key]
            bounds = np.asarray(blk["energy_bounds_ev"][:], dtype=np.float64)
            cov = np.asarray(blk["rel_cov"][:], dtype=np.float64)
            rows.append(
                {
                    "nuclide_id": nuc,
                    "mt": mt,
                    "n_bins": int(cov.shape[0]),
                    "energy_bounds_ev": bounds.tolist(),
                    "rel_cov": cov.reshape(-1).tolist(),
                    "lb_types": [int(x) for x in blk.attrs.get("lb_types", [])],
                }
            )
    CACHE.mkdir(parents=True, exist_ok=True)
    schema = {
        "nuclide_id": pl.Utf8,
        "mt": pl.Int16,
        "n_bins": pl.Int32,
        "energy_bounds_ev": pl.List(pl.Float64),
        "rel_cov": pl.List(pl.Float64),
        "lb_types": pl.List(pl.Int16),
    }
    df = pl.DataFrame(rows, schema=schema) if rows else pl.DataFrame(schema=schema)
    tmp = out.with_suffix(".tmp.parquet")
    df.write_parquet(tmp)
    tmp.replace(out)
    return out


def cache_exfor_cells(*, force: bool = False, source: Path | None = None,
                      channel: str = "capture") -> Path:
    """WP-12 per-(dataset, group, bin) cells joined to the trust table.

    Columns: dataset_key, group_key, nuclide, mt, kind, state, branch, bin, n_pts, mean_b,
    ln_mean, stat_rel, sys_rel, sem_rel, e_lo_ev, e_hi_ev, trust, inflation, year, decision,
    usable. ``ln_mean`` is the natural log of ``mean_b`` (the curation layer's ``y``).
    """
    source = source if source is not None else channel_source(channel)
    out = cells_cache_path(channel)
    trust_src = channel_trust(channel)
    if _fresh(out, source, trust_src) and not force:
        return out
    from data.curate.discrepancy import cells_from_parquet, split_group_key

    cells = cells_from_parquet(source, verbose=False)
    trust = pl.read_parquet(
        trust_src,
        columns=["dataset_key", "trust", "inflation", "year", "decision", "usable"],
    )
    keys = cells["group_key"].to_list()
    parts = [split_group_key(k) for k in keys]
    cells = cells.with_columns(
        nuclide=pl.Series([p[0] for p in parts], dtype=pl.Utf8),
        mt=pl.Series([p[1] for p in parts], dtype=pl.Int32),
        branch=pl.Series([p[2] for p in parts], dtype=pl.Utf8),
        kind=pl.Series([p[3] for p in parts], dtype=pl.Utf8),
        state=pl.Series([p[4] for p in parts], dtype=pl.Utf8),
    ).rename({"y": "ln_mean"})
    df = cells.join(trust, on="dataset_key", how="left")
    floor = CHANNEL_FLOOR_B.get(channel)
    if floor is not None:
        # WP-19: see CHANNEL_FLOOR_B. Marked excluded rather than dropped, so the curation
        # filter in load_exfor_points removes them and its drop tally counts them.
        df = df.with_columns(
            decision=pl.when(pl.col("mean_b") < floor).then(pl.lit("exclude"))
            .otherwise(pl.col("decision"))
        )
    CACHE.mkdir(parents=True, exist_ok=True)
    tmp = out.with_suffix(".tmp.parquet")
    df.write_parquet(tmp)
    tmp.replace(out)
    return out


def build(
    libraries: list[str] | None = None, mts: list[int] | None = None, *, force: bool = False
) -> dict:
    libraries = libraries or list(CACHE_DEFAULT)
    mts = mts or [102]
    info: dict[str, dict] = {}
    t0 = time.time()
    for lib in libraries:
        for mt in mts:
            p = cache_library_xs(lib, mt, force=force)
            c = cache_library_cov(lib, mt, force=force)
            n = pl.scan_parquet(p).select(pl.len()).collect().item()
            nc = pl.scan_parquet(c).select(pl.len()).collect().item()
            info[f"{lib}_mt{mt}"] = {"xs_rows": n, "cov_rows": nc}
            print(f"  {lib} MT{mt}: {n} xs rows, {nc} cov blocks ({time.time() - t0:.0f}s)")
    p = cache_exfor_cells(force=force)
    n = pl.scan_parquet(p).select(pl.len()).collect().item()
    info["exfor_cells"] = {"rows": n}
    print(f"  exfor cells: {n} rows ({time.time() - t0:.0f}s)")
    (CACHE / "cache_info.json").write_text(json.dumps(info, indent=1))
    return info


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--library", nargs="*", default=None, choices=list(LIBRARIES))
    ap.add_argument("--mt", nargs="*", type=int, default=None)
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args(argv)
    build(a.library, a.mt, force=a.force)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)
