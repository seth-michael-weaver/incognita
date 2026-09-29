"""Theoretical mass models as features and baselines (BLUEPRINT §3.3, §5.2).

Every model is exposed through :data:`MODELS` as a loader returning a frame with at least
``Z, N, A, mass_excess_kev`` (atomic mass excess, keV) and optionally ``beta2``.
:func:`mass_model_table` aligns all of them to a list of nuclides for the feature table,
and :func:`baseline_rms` reports each model's RMS deviation from AME2020 measured masses.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

import numpy as np
import pandas as pd

from physics.massmodels import bruslib, dz, ripl_tables, ws4
from physics.massmodels.paths import BRUSLIB, DZ_DIR, RIPL_MASSES, WS4_DIR

__all__ = [
    "MODELS",
    "ModelSpec",
    "baseline_rms",
    "format_baseline_table",
    "load_all",
    "load_model",
    "mass_model_table",
]


@dataclass(frozen=True)
class ModelSpec:
    name: str
    loader: Callable[[], pd.DataFrame]
    source: str  # file the numbers came from, relative to raw/ (or "computed")
    citation: str
    has_beta2: bool = False
    literature_rms_kev: float | None = None  # on AME2020 (or nearest published), for sanity


def _rel(p) -> str:
    from physics.massmodels.paths import RAW

    return str(p.relative_to(RAW))


MODELS: dict[str, ModelSpec] = {
    "frdm2012": ModelSpec(
        "frdm2012",
        lambda: ripl_tables.load_ripl_mass_table("frdm2012"),
        _rel(RIPL_MASSES / "mass-frdm12.dat"),
        ripl_tables.RIPL_TABLES["frdm2012"][2],
        has_beta2=True,
        literature_rms_kev=606.0,
    ),
    "hfb24": ModelSpec(
        "hfb24",
        lambda: bruslib.load_bruslib_table("hfb24"),
        _rel(BRUSLIB / "hfb24-dat"),
        bruslib.BRUSLIB_TABLES["hfb24"][1],
        has_beta2=True,
        literature_rms_kev=549.0,
    ),
    "hfb27": ModelSpec(
        "hfb27",
        lambda: ripl_tables.load_ripl_mass_table("hfb27"),
        _rel(RIPL_MASSES / "mass-hfb27.dat"),
        ripl_tables.RIPL_TABLES["hfb27"][2],
        has_beta2=True,
        literature_rms_kev=518.0,
    ),
    "hfb31": ModelSpec(
        "hfb31",
        lambda: bruslib.load_bruslib_table("hfb31"),
        _rel(BRUSLIB / "hfb31-dat"),
        bruslib.BRUSLIB_TABLES["hfb31"][1],
        has_beta2=True,
        literature_rms_kev=561.0,
    ),
    "ws4": ModelSpec(
        "ws4",
        ws4.load_ws4,
        _rel(WS4_DIR / "WS4.txt"),
        ws4.WS4_CITATION,
        has_beta2=True,
        literature_rms_kev=295.0,
    ),
    "ws4_rbf": ModelSpec(
        "ws4_rbf",
        ws4.load_ws4_rbf,
        _rel(WS4_DIR / "WS4_RBF.txt"),
        ws4.WS4_RBF_CITATION,
        literature_rms_kev=170.0,
    ),
    "dz28": ModelSpec(
        "dz28",
        dz.load_dz28_table,
        _rel(DZ_DIR / "DZ28_RBF.txt"),
        dz.DZ28_CITATION,
        literature_rms_kev=400.0,
    ),
    "dz10": ModelSpec(
        "dz10",
        dz.dz10_table,
        "computed: physics/massmodels/dz.py port of " + _rel(DZ_DIR / "du_zu_10.feb96fort"),
        dz.DZ10_CITATION,
        literature_rms_kev=506.0,
    ),
    "bskg3": ModelSpec(
        "bskg3",
        lambda: ripl_tables.load_ripl_mass_table("bskg3"),
        _rel(RIPL_MASSES / "mass-bskg3.dat"),
        ripl_tables.RIPL_TABLES["bskg3"][2],
        has_beta2=True,
        literature_rms_kev=631.0,
    ),
    "d1m": ModelSpec(
        "d1m",
        lambda: ripl_tables.load_ripl_mass_table("d1m"),
        _rel(RIPL_MASSES / "mass-d1m.dat"),
        ripl_tables.RIPL_TABLES["d1m"][2],
        has_beta2=True,
        literature_rms_kev=798.0,
    ),
}

# Order the feature table and baseline report use.
FEATURE_MODELS: tuple[str, ...] = tuple(MODELS)


def load_model(name: str) -> pd.DataFrame:
    df = MODELS[name].loader()
    dup = df.duplicated(["Z", "N"])
    if dup.any():
        raise ValueError(f"{name}: {int(dup.sum())} duplicate (Z, N) rows")
    return df


def load_all(names: tuple[str, ...] = FEATURE_MODELS) -> dict[str, pd.DataFrame]:
    return {n: load_model(n) for n in names}


def mass_model_table(Z, N, tables: dict[str, pd.DataFrame] | None = None) -> pd.DataFrame:
    """Per-nuclide mass-model columns aligned to (Z, N): ``me_<model>_kev`` and, where the
    model provides it, ``beta2_<model>``. NaN where a model has no entry.

    Column provenance is in ``df.attrs["column_sources"]``.
    """
    Z = np.atleast_1d(np.asarray(Z, dtype=np.int64))
    N = np.atleast_1d(np.asarray(N, dtype=np.int64))
    tables = load_all() if tables is None else tables
    key = pd.DataFrame({"Z": Z, "N": N})
    out = key.copy()
    sources: dict[str, str] = {}
    for name, df in tables.items():
        spec = MODELS[name]
        cols = ["Z", "N", "mass_excess_kev"] + (["beta2"] if spec.has_beta2 else [])
        m = key.merge(df[cols], on=["Z", "N"], how="left")
        out[f"me_{name}_kev"] = m["mass_excess_kev"].to_numpy()
        sources[f"me_{name}_kev"] = spec.source
        if spec.has_beta2:
            # A quadrupole deformation is bounded: the tables run about -0.4 to +0.7 and |b2| > 1
            # is not a shape, it is a fill value. HFB-27 carries -99.999 for Ir-180 (Z=77, N=103),
            # and because it is a NUMBER rather than NaN it survived every missing-data check --
            # models/data.py standardises with nanmean/nanstd, which ignores NaN and not this.
            # One cell inflated that column's std 8.8x (0.194 -> 1.713), compressing the
            # standardised feature for all 3,557 other nuclides from a +-2.4 range to +-0.29, so
            # the encoder saw about a ninth of the signal the column was meant to carry.
            b2 = m["beta2"].to_numpy(dtype=float)
            out[f"beta2_{name}"] = np.where(np.abs(b2) > 1.0, np.nan, b2)
            sources[f"beta2_{name}"] = spec.source
    out.attrs["column_sources"] = sources
    return out


def baseline_rms(
    ame: pd.DataFrame | None = None,
    tables: dict[str, pd.DataFrame] | None = None,
    zmin: int = 8,
    nmin: int = 8,
) -> pd.DataFrame:
    """RMS deviation (keV) of each model from AME2020 *measured* masses.

    ``ame`` is the frame from :func:`data.ingest.ame.load_ame`; rows with the ``#`` flag are
    excluded. The overlap set is restricted to Z >= zmin and N >= nmin (the tables start at
    16O). Returns one row per model: n, rms_kev, mean_kev, max_abs_kev, literature_rms_kev.
    """
    if ame is None:
        from data.ingest.ame import load_ame

        ame = load_ame()
    meas = ame[
        (~ame["mass_excess_extrapolated"])
        & ame["mass_excess_kev"].notna()
        & (ame["Z"] >= zmin)
        & (ame["N"] >= nmin)
    ][["Z", "N", "mass_excess_kev"]]
    tables = load_all() if tables is None else tables
    rows = []
    for name, df in tables.items():
        spec = MODELS[name]
        m = meas.merge(
            df[["Z", "N", "mass_excess_kev"]].rename(columns={"mass_excess_kev": "model"}),
            on=["Z", "N"],
            how="inner",
        )
        m = m[m["model"].notna()]
        d = (m["model"] - m["mass_excess_kev"]).to_numpy()
        rows.append(
            {
                "model": name,
                "n": int(len(d)),
                "rms_kev": float(np.sqrt(np.mean(d**2))) if len(d) else np.nan,
                "mean_kev": float(np.mean(d)) if len(d) else np.nan,
                "max_abs_kev": float(np.max(np.abs(d))) if len(d) else np.nan,
                "literature_rms_kev": spec.literature_rms_kev,
                "source": spec.source,
            }
        )
    return pd.DataFrame(rows)


def format_baseline_table(rms: pd.DataFrame) -> str:
    lines = [
        f"{'model':<10}{'n':>6}{'rms keV':>10}{'mean keV':>10}{'max|d| keV':>12}"
        f"{'lit. rms':>10}  source"
    ]
    for r in rms.itertuples(index=False):
        lit_v = r.literature_rms_kev
        lit = "" if lit_v is None or np.isnan(lit_v) else f"{lit_v:.0f}"
        lines.append(
            f"{r.model:<10}{r.n:>6}{r.rms_kev:>10.1f}{r.mean_kev:>10.1f}{r.max_abs_kev:>12.1f}"
            f"{lit:>10}  {r.source}"
        )
    return "\n".join(lines)


if __name__ == "__main__":
    print(format_baseline_table(baseline_rms()))
