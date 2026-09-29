"""Chart tensor assembly for the Stage A mass model (WP-06, blueprint §5.2).

The nuclide chart is treated as an image of shape ``(C, Zmax+1, Nmax+1)``: pixel
``(Z, N)`` carries the standardized physics features of that nuclide, the theory
mass-model columns expressed as residuals to the physics baseline, and the Tier 1
targets on the same grid. Everything experimental is kept *out* of the static
feature tensor; the split-dependent "observed residual" input channel is built by
:meth:`ChartData.observed_channels` from a training mask so nothing leaks across
splits.

Target parameterization: the model predicts ``r = ME_exp - ME_baseline`` in MeV,
where the baseline is WS4 where available (RMS 295 keV on measured masses) and
nothing otherwise. Nuclides without a baseline (all have Z<8 or N<8) are kept in the
image as inputs but carry zero loss weight, which is the usual Z,N>=8 convention of
the mass-model literature.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
import polars as pl
import torch

ROOT = Path(__file__).resolve().parents[1]
# INCOGNITA_FEATURES swaps the chart feature table, which is what an ablation on a single feature
# column needs: the mass model is trained end to end, so the only honest way to attribute a
# change to the table is to run current code against both tables. Comparing a fresh run to a
# frozen result from days earlier attributes every intervening change to the feature.
FEATURES_PATH = Path(os.environ.get(
    "INCOGNITA_FEATURES", os.environ.get(
        "INCOGNITA_FEATURES", ROOT / "features" / "nuclide_features.parquet")))
STAGING_PATH = ROOT / "staging" / "nuclides.parquet"

# Atomic mass excesses (keV) used for separation energies (AME2020).
ME_NEUTRON_KEV = 8071.31806
ME_HYDROGEN_KEV = 7288.97106

PHYSICS_FEATURES = [
    "Z_even",
    "N_even",
    "isospin",
    "isospin_frac",
    "dZ_magic",
    "dN_magic",
    "Z_is_magic",
    "N_is_magic",
    "Z_particles",
    "Z_holes",
    "Z_valence",
    "N_particles",
    "N_holes",
    "N_valence",
    "casten_P",
    "A_cbrt",
    "ld_volume",
    "ld_surface",
    "ld_coulomb",
    "ld_asymmetry",
    "ld_pairing",
    "ld_binding",
]
# Theory mass models used as *inputs* (as residuals to the baseline, in MeV).
# me_ws4_rbf_kev is deliberately excluded: the RBF correction is fit to experimental
# masses and would leak the target.
THEORY_ME_COLS = [
    "me_frdm2012_kev",
    "me_hfb24_kev",
    "me_hfb27_kev",
    "me_hfb31_kev",
    "me_ws4_kev",
    "me_dz28_kev",
    "me_dz10_kev",
    "me_bskg3_kev",
    "me_d1m_kev",
]
THEORY_BETA2_COLS = [
    "beta2_frdm2012",
    "beta2_hfb24",
    "beta2_hfb27",
    "beta2_hfb31",
    "beta2_ws4",
    "beta2_bskg3",
    "beta2_d1m",
]
# Baselines reported in the results tables (raw columns of the feature table).
BASELINE_COLS = {
    "FRDM2012": "me_frdm2012_kev",
    "HFB-24": "me_hfb24_kev",
    "HFB-27": "me_hfb27_kev",
    "HFB-31": "me_hfb31_kev",
    "WS4": "me_ws4_kev",
    "WS4+RBF": "me_ws4_rbf_kev",
    "DZ28": "me_dz28_kev",
}
BASELINE_PRIORITY = ("me_ws4_kev", "me_dz28_kev", "me_frdm2012_kev")

LOG_T_MEAN, LOG_T_SCALE = 1.3, 4.4  # log10(T1/2 / s) standardization for the half-life head

DECAY_CLASSES = ["stable", "B-", "B+/EC", "alpha", "SF", "p", "n", "other"]
SPIN2_MAX = 20  # 2J classes 0..20 (J up to 10)


def decay_class(mode: str) -> int:
    """Map a NUBASE decay-mode token to one of :data:`DECAY_CLASSES`."""
    if mode == "IS":
        return 0
    if mode.startswith("B-"):
        return 1
    if mode.startswith("B+") or mode in ("EC", "e+", "2B+", "e+SF"):
        return 2
    if mode == "A":
        return 3
    if mode == "SF":
        return 4
    if mode in ("p", "2p"):
        return 5
    if mode in ("n", "2n"):
        return 6
    return 7


def dominant_decay_class(modes: list[dict[str, Any]] | None) -> int | None:
    if not modes:
        return None
    best, best_br = None, -1.0
    for i, m in enumerate(modes):
        br = m.get("branching")
        br = -0.5 + 1e-3 * (len(modes) - i) if br is None else float(br)
        if br > best_br:
            best, best_br = m, br
    if best is None or best.get("mode") is None:
        return None
    return decay_class(best["mode"])


@dataclass
class ChartData:
    """All grids are ``(H, W)`` = ``(Zmax+1, Nmax+1)`` numpy arrays indexed ``[Z, N]``."""

    H: int
    W: int
    nuc: pl.DataFrame  # one row per ground state
    x: torch.Tensor  # (C, H, W) float32 static features (standardized)
    feature_names: list[str]
    exists: np.ndarray  # bool: nuclide present in the feature table
    valid: np.ndarray  # bool: has a baseline and Z,N >= min_zn -> eligible for the mass loss
    measured: np.ndarray  # bool: AME2020 measured (non-extrapolated) mass
    me_kev: np.ndarray  # float64, NaN where not in table
    me_sigma_kev: np.ndarray
    baseline_kev: np.ndarray  # float64, NaN where no baseline
    resid_mev: np.ndarray  # (me - baseline)/1000, NaN where either missing
    year: np.ndarray  # discovery-year proxy (float, NaN unknown)
    targets: dict[str, dict[str, np.ndarray]] = field(default_factory=dict)
    baselines_kev: dict[str, np.ndarray] = field(default_factory=dict)
    meta: dict[str, Any] = field(default_factory=dict)

    # ---- helpers -----------------------------------------------------------------
    def zn_of_mask(self, mask: np.ndarray) -> np.ndarray:
        zz, nn = np.nonzero(mask)
        return np.stack([zz, nn], axis=1)

    def mask_from_ids(self, ids: list[str] | set[str]) -> np.ndarray:
        m = np.zeros((self.H, self.W), dtype=bool)
        sub = self.nuc.filter(pl.col("nuclide_id").is_in(list(ids)))
        m[sub["Z"].to_numpy(), sub["N"].to_numpy()] = True
        return m

    def observed_channels(self, train_mask: np.ndarray) -> torch.Tensor:
        """Split-dependent input: ``[has_measured_mass, observed residual (MeV)]``."""
        obs = train_mask & self.measured & np.isfinite(self.resid_mev)
        r = np.where(obs, self.resid_mev, 0.0)
        return torch.from_numpy(np.stack([obs.astype(np.float32), r.astype(np.float32)]))

    def predicted_me_kev(self, resid_mev: np.ndarray) -> np.ndarray:
        return self.baseline_kev + 1000.0 * resid_mev


def _datum(df: pl.DataFrame, col: str) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    v = df.select(pl.col(col).struct.field("value")).to_series().to_numpy().astype(np.float64)
    s = df.select(pl.col(col).struct.field("sigma")).to_series().to_numpy().astype(np.float64)
    e = df.select(pl.col(col).struct.field("extrapolated")).to_series().fill_null(False)
    return v, s, e.to_numpy().astype(bool)


def _grid(H: int, W: int, fill: float = np.nan, dtype=np.float64) -> np.ndarray:
    return np.full((H, W), fill, dtype=dtype)


def build_chart(
    features_path: Path = FEATURES_PATH,
    staging_path: Path = STAGING_PATH,
    *,
    min_zn: int = 8,
) -> ChartData:
    """Assemble the chart tensor from the feature table and staging nuclides."""
    f = pl.read_parquet(features_path).sort(["Z", "N"])
    s = pl.read_parquet(staging_path).filter(pl.col("iso") == 0)
    s = s.select(
        [
            "nuclide_id",
            "sn_kev",
            "s2n_kev",
            "sp_kev",
            "s2p_kev",
            "spin",
            "parity",
            "spin_parity_tentative",
            "is_stable",
            "log10_half_life_s",
            "decay_modes",
            "pn",
            "p2n",
            "charge_radius_fm",
            "beta2",
            "discovery_year",
            "ensdf_year",
        ]
    )
    f = f.join(s, on="nuclide_id", how="left")
    H, W = int(f["Z"].max()) + 1, int(f["N"].max()) + 1
    Z = f["Z"].to_numpy().astype(int)
    N = f["N"].to_numpy().astype(int)
    idx = (Z, N)

    # --- baseline -------------------------------------------------------------------
    base = np.full(len(f), np.nan)
    src = np.array([""] * len(f), dtype=object)
    for col in BASELINE_PRIORITY:
        v = f[col].to_numpy().astype(np.float64)
        take = np.isnan(base) & np.isfinite(v)
        base[take] = v[take]
        src[take] = col.removeprefix("me_").removesuffix("_kev")

    me = f["target_mass_excess_kev"].to_numpy().astype(np.float64)
    me_sig = f["target_mass_excess_sigma_kev"].to_numpy().astype(np.float64)
    extrap = f["target_is_extrapolated"].to_numpy().astype(bool)
    measured_v = ~extrap & np.isfinite(me)
    year_v = (
        f.select(pl.coalesce("discovery_year", "ensdf_year").cast(pl.Float64))
        .to_series()
        .to_numpy()
        .astype(np.float64)
    )

    nuc = pl.DataFrame(
        {
            "nuclide_id": f["nuclide_id"],
            "Z": Z,
            "N": N,
            "A": f["A"].to_numpy().astype(int),
            "measured": measured_v,
            "me_kev": me,
            "me_sigma_kev": me_sig,
            "baseline_kev": base,
            "baseline_source": [str(x) for x in src],
            "year": year_v,
            "valid": np.isfinite(base) & (Z >= min_zn) & (N >= min_zn),
        }
    )

    # --- static features --------------------------------------------------------------
    names: list[str] = []
    chans: list[np.ndarray] = []

    def add(name: str, values: np.ndarray) -> None:
        g = _grid(H, W, 0.0, np.float32)
        g[idx] = values.astype(np.float32)
        names.append(name)
        chans.append(g)

    add("exists", np.ones(len(f)))
    add("has_baseline", np.isfinite(base).astype(float))
    add("Z_norm", Z / (H - 1))
    add("N_norm", N / (W - 1))
    add("A_norm", f["A"].to_numpy() / f["A"].max())
    stats: dict[str, tuple[float, float]] = {}
    for col in PHYSICS_FEATURES:
        v = f[col].to_numpy().astype(np.float64)
        mu, sd = float(np.nanmean(v)), float(np.nanstd(v)) or 1.0
        stats[col] = (mu, sd)
        add(col, np.nan_to_num((v - mu) / sd))
    base_or0 = np.where(np.isfinite(base), base, 0.0)
    for col in THEORY_ME_COLS:
        v = f[col].to_numpy().astype(np.float64)
        d = np.clip((v - base_or0) / 1000.0, -20, 20)
        add(col.removeprefix("me_").removesuffix("_kev") + "_minus_base_mev", np.nan_to_num(d))
        add(col.removeprefix("me_").removesuffix("_kev") + "_avail", np.isfinite(v).astype(float))
    for col in THEORY_BETA2_COLS:
        v = f[col].to_numpy().astype(np.float64)
        v = np.where(np.abs(v) > 2, np.nan, v)
        add(col, np.nan_to_num(v))
    x = torch.from_numpy(np.stack(chans, axis=0))

    # --- grids ------------------------------------------------------------------------
    exists = np.zeros((H, W), bool)
    exists[idx] = True
    measured = np.zeros((H, W), bool)
    measured[idx] = measured_v
    valid = np.zeros((H, W), bool)
    valid[idx] = nuc["valid"].to_numpy()
    me_g, sig_g, base_g, year_g = (_grid(H, W) for _ in range(4))
    me_g[idx], sig_g[idx], base_g[idx], year_g[idx] = me, me_sig, base, year_v
    resid_g = (me_g - base_g) / 1000.0

    targets: dict[str, dict[str, np.ndarray]] = {}
    targets["mass"] = {
        "value": np.where(measured & np.isfinite(resid_g), resid_g, 0.0),
        "sigma": np.nan_to_num(sig_g / 1000.0),
        "mask": measured & valid,
    }
    # Separation energies are learned as residuals to the baseline-derived ones (MeV):
    # target = S_exp - S_baseline, so the direct heads live on the same ~0.3 MeV scale
    # as the mass residual and the consistency terms need no absolute masses.
    base_sep = separation_energies(torch.from_numpy(base_g))
    for key in ("sn", "s2n", "sp", "s2p"):
        v, sg, ex = _datum(f, f"{key}_kev")
        vg, sgg, mg = _grid(H, W), _grid(H, W, 0.0), np.zeros((H, W), bool)
        vg[idx] = v / 1000.0
        sgg[idx] = np.nan_to_num(sg / 1000.0)
        mg[idx] = np.isfinite(v) & ~ex
        sb = base_sep[key].numpy() / 1000.0
        mg &= np.isfinite(sb)
        targets[key] = {
            "value": np.nan_to_num(vg - np.nan_to_num(sb)) * mg,
            "sigma": sgg,
            "mask": mg & valid,
            "baseline_mev": np.nan_to_num(sb),
        }
    v, sg, ex = _datum(f, "log10_half_life_s")
    stable = f["is_stable"].fill_null(False).to_numpy().astype(bool)
    vg, sgg, mg = _grid(H, W), _grid(H, W, 0.0), np.zeros((H, W), bool)
    vg[idx] = (np.clip(v, -25, 35) - LOG_T_MEAN) / LOG_T_SCALE
    sgg[idx] = np.nan_to_num(sg) / LOG_T_SCALE
    mg[idx] = np.isfinite(v) & ~ex & ~stable
    targets["log_t"] = {"value": np.nan_to_num(vg), "sigma": sgg, "mask": mg & exists}
    sg_ = np.zeros((H, W), np.int64)
    sg_[idx] = stable.astype(int)
    targets["stable"] = {"value": sg_, "mask": exists.copy()}
    spin = f["spin"].to_numpy().astype(np.float64)
    par = f["parity"].to_numpy().astype(np.float64)
    cls = np.zeros((H, W), np.int64)
    mg = np.zeros((H, W), bool)
    cls[idx] = np.nan_to_num(np.clip(np.rint(2 * spin), 0, SPIN2_MAX)).astype(int)
    mg[idx] = np.isfinite(spin)
    targets["spin2"] = {"value": cls, "mask": mg & exists}
    cls = np.zeros((H, W), np.int64)
    mg = np.zeros((H, W), bool)
    cls[idx] = np.nan_to_num((par > 0).astype(int))
    mg[idx] = np.isfinite(par)
    targets["parity"] = {"value": cls, "mask": mg & exists}
    dm = [dominant_decay_class(m) for m in f["decay_modes"].to_list()]
    cls = np.zeros((H, W), np.int64)
    mg = np.zeros((H, W), bool)
    cls[idx] = np.array([-1 if d is None else d for d in dm])
    mg[idx] = np.array([d is not None for d in dm])
    cls[cls < 0] = 0
    targets["decay"] = {"value": cls, "mask": mg & exists}
    for key in ("pn", "charge_radius_fm", "beta2"):
        v, sg, ex = _datum(f, key)
        vg, sgg, mg = _grid(H, W), _grid(H, W, 0.0), np.zeros((H, W), bool)
        vg[idx] = v
        sgg[idx] = np.nan_to_num(sg)
        mg[idx] = np.isfinite(v) & ~ex
        targets[key] = {"value": np.nan_to_num(vg), "sigma": sgg, "mask": mg & exists}

    baselines = {}
    for name, col in BASELINE_COLS.items():
        g = _grid(H, W)
        g[idx] = f[col].to_numpy().astype(np.float64)
        baselines[name] = g

    meta = {
        "n_nuclides": int(len(f)),
        "n_measured": int(measured_v.sum()),
        "n_valid_measured": int((measured & valid).sum()),
        "baseline_sources": {
            k: int(v) for k, v in zip(*np.unique(src.astype(str), return_counts=True), strict=True)
        },
        "feature_stats": stats,
        "target_counts": {k: int(v["mask"].sum()) for k, v in targets.items()},
        "min_zn": min_zn,
    }
    return ChartData(
        H=H,
        W=W,
        nuc=nuc,
        x=x,
        feature_names=names,
        exists=exists,
        valid=valid,
        measured=measured,
        me_kev=me_g,
        me_sigma_kev=sig_g,
        baseline_kev=base_g,
        resid_mev=resid_g,
        year=year_g,
        targets=targets,
        baselines_kev=baselines,
        meta=meta,
    )


# ---- separation energies from a mass-excess field --------------------------------------


def shift(a: torch.Tensor, dz: int, dn: int, fill: float = float("nan")) -> torch.Tensor:
    """``out[z, n] = a[z - dz, n - dn]`` (i.e. the neighbour at (Z-dz, N-dn)), NaN-padded."""
    out = torch.full_like(a, fill)
    H, W = a.shape[-2:]
    zs = slice(max(dz, 0), H + min(dz, 0))
    zd = slice(max(-dz, 0), H + min(-dz, 0))
    ns = slice(max(dn, 0), W + min(dn, 0))
    nd = slice(max(-dn, 0), W + min(-dn, 0))
    out[..., zs, ns] = a[..., zd, nd]
    return out


def separation_energies(me_kev: torch.Tensor) -> dict[str, torch.Tensor]:
    """S_n, S_2n, S_p, S_2p (keV) from a mass-excess field ``me_kev[Z, N]``.

    NaN where a neighbour is missing. Uses atomic mass excesses (AME convention).
    """
    return {
        "sn": shift(me_kev, 0, 1) - me_kev + ME_NEUTRON_KEV,
        "s2n": shift(me_kev, 0, 2) - me_kev + 2 * ME_NEUTRON_KEV,
        "sp": shift(me_kev, 1, 0) - me_kev + ME_HYDROGEN_KEV,
        "s2p": shift(me_kev, 2, 0) - me_kev + 2 * ME_HYDROGEN_KEV,
    }


def odd_even_staggering(me_kev: torch.Tensor) -> dict[str, torch.Tensor]:
    """Three-point OES indicators along N and Z: ``0.5 * (M(N+1) - 2 M(N) + M(N-1))``."""
    return {
        "oes_n": 0.5 * (shift(me_kev, 0, -1) - 2 * me_kev + shift(me_kev, 0, 1)),
        "oes_z": 0.5 * (shift(me_kev, -1, 0) - 2 * me_kev + shift(me_kev, 1, 0)),
    }


# ---- splits -----------------------------------------------------------------------------


@dataclass
class Split:
    name: str
    kind: str
    train: np.ndarray  # (H, W) bool, subset of measured & valid
    test: np.ndarray  # (H, W) bool
    provisional: bool = False
    params: dict[str, str] = field(default_factory=dict)


def _manifests_available() -> bool:
    try:
        from data.splits import INDEX_PATH

        return INDEX_PATH.exists()
    except Exception:
        return False


def load_manifest_splits(chart: ChartData, *, verify: bool = True) -> dict[str, Split]:
    """All (train, test) pairs from ``data/splits/manifests`` mapped onto the chart."""
    from data.splits import list_manifests, load_manifest

    by_split: dict[str, dict[str, Any]] = {}
    for name in list_manifests():
        m = load_manifest(name, verify=verify)
        split = m.params.get("split", name.rsplit("_", 1)[0])
        d = by_split.setdefault(split, {"kind": str(m.kind), "params": dict(m.params)})
        d[str(m.role)] = set(m.members)
    eligible = chart.measured & chart.valid
    out: dict[str, Split] = {}
    for split, d in by_split.items():
        if "test" not in d or d["kind"] not in ("nuclide", "region", "time"):
            continue
        if split.startswith("new_masses"):
            continue  # post-AME2020 measurements: evaluated from the CSV by models.train
        # Extrapolated-eval targets are AME '#' estimates, not measurements: keep them.
        test = chart.mask_from_ids(d["test"]) & chart.exists
        if split != "ame_extrapolated_eval":
            test &= chart.measured
        if "train" in d:
            # A 'val' role is folded into training: checkpoint selection never uses a
            # random validation set (blueprint §5.6); see models.train.selection_masks.
            train_ids = set(d["train"]) | set(d.get("val", ()))
            train = chart.mask_from_ids(train_ids) & eligible
        else:
            train = eligible & ~test
        out[split] = Split(split, d["kind"], train, test, params=d["params"])
    return out


def provisional_splits(chart: ChartData, *, seed: int = 0, n_folds: int = 5) -> dict[str, Split]:
    """Fallback splits built locally when the frozen manifests are not available.

    Same population and definitions as ``data/splits`` (stratified nuclide holdout,
    discovery-year time proxy, contiguous region blocks) but *not* the frozen files;
    results on them must be labelled provisional.
    """
    rng = np.random.default_rng(seed)
    eligible = chart.measured & chart.valid
    zz, nn = np.nonzero(eligible)
    A = zz + nn
    out: dict[str, Split] = {}
    # stratified by A bins
    fold = np.zeros(len(zz), int)
    for lo in range(0, 320, 20):
        sel = np.nonzero((A >= lo) & (A < lo + 20))[0]
        rng.shuffle(sel)
        fold[sel] = np.arange(len(sel)) % n_folds
    for k in range(n_folds):
        test = np.zeros_like(eligible)
        test[zz[fold == k], nn[fold == k]] = True
        out[f"nuclide_holdout_f{k}"] = Split(
            f"nuclide_holdout_f{k}", "nuclide", eligible & ~test, test, provisional=True
        )
    for y in (2003, 2012, 2016):
        yr = chart.year
        train = eligible & np.isfinite(yr) & (yr <= y)
        test = chart.measured & np.isfinite(yr) & (yr > y)
        out[f"time_{y}"] = Split(f"time_{y}", "time", train, test, provisional=True)
    blocks = {
        "region_Z50-60_N82-90": (50, 60, 82, 90),
        "region_Z20-28_N28-40": (20, 28, 28, 40),
        "region_Z60-72_N90-104": (60, 72, 90, 104),
        "region_Z84-96_N126-140": (84, 96, 126, 140),
    }
    for name, (z0, z1, n0, n1) in blocks.items():
        blk = np.zeros_like(eligible)
        blk[z0 : z1 + 1, n0 : n1 + 1] = True
        test = blk & chart.measured
        out[name] = Split(name, "region", eligible & ~blk, test, provisional=True)
    out["ame_extrapolated_eval"] = Split(
        "ame_extrapolated_eval",
        "nuclide",
        eligible,
        chart.exists & ~chart.measured & np.isfinite(chart.baseline_kev),
        provisional=True,
    )
    return out


def get_splits(chart: ChartData, *, prefer_manifests: bool = True) -> dict[str, Split]:
    if prefer_manifests and _manifests_available():
        try:
            splits = load_manifest_splits(chart)
            if splits:
                return splits
        except Exception as e:  # pragma: no cover - defensive
            print(f"[data] manifest load failed ({e!r}); using provisional splits")
    return provisional_splits(chart)


def save_meta(chart: ChartData, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(chart.meta, fh, indent=2)
