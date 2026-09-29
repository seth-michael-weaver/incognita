"""Frozen WP-06 embeddings for Stage B, one full-chart field per split.

For a mass-model split (``nuclide_holdout_f0`` … ``region_*``) the embedding comes from
the ensemble trained *for that split* (``models/checkpoints/mass_v0/<split>/``), run with
the split's training masses as the observed-residual input channel — exactly what
``models.train.predict_split`` does — so a nuclide held out from the decoder was also
held out from the encoder. ``production`` uses ``full_chart_prediction.npz`` (every
measured mass observed). Fields are cached as ``models/checkpoints/stage_b/emb/<split>.npz``
(``emb`` float32 (256, H, W), ``exists`` bool (H, W), ``train`` bool (H, W)).

Extraction runs on the CPU on purpose: five forward passes of the chart-CNN take a few
seconds and no CUDA context is created (RSS budget of the shared box).
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import torch

from models.data import ROOT, ChartData, build_chart, get_splits
from models.uq.ensembles import Ensemble

MASS_CKPT = ROOT / "models" / "checkpoints" / "mass_v0"
EMB_DIR = ROOT / "models" / "checkpoints" / "stage_b" / "emb"


def _chart_masks(chart: ChartData, split: str) -> tuple[np.ndarray, np.ndarray]:
    if split == "production":
        train = chart.measured & chart.valid
        return train, np.zeros_like(train)
    splits = get_splits(chart)
    if split not in splits:
        raise KeyError(f"unknown split {split!r}; known: {sorted(splits)}")
    return splits[split].train, splits[split].test


@torch.no_grad()
def extract(split: str, chart: ChartData | None = None, *, force: bool = False) -> Path:
    """Compute (or reuse) the cached embedding field for ``split``; returns the npz path."""
    EMB_DIR.mkdir(parents=True, exist_ok=True)
    path = EMB_DIR / f"{split}.npz"
    if path.exists() and not force:
        return path
    chart = chart or build_chart()
    train, test = _chart_masks(chart, split)
    if split == "production":
        src = MASS_CKPT / "full_chart_prediction.npz"
        if src.exists():
            emb = np.load(src)["emb"].astype(np.float32)
        else:
            emb = _run_ensemble(MASS_CKPT, chart, train)
    else:
        ck = MASS_CKPT / split
        if not (ck / "ensemble.json").exists():
            raise FileNotFoundError(f"no WP-06 ensemble for split {split!r} under {ck}")
        emb = _run_ensemble(ck, chart, train)
    np.savez_compressed(path, emb=emb, exists=chart.exists, train=train, test=test)
    return path


def _run_ensemble(ck: Path, chart: ChartData, obs_mask: np.ndarray) -> np.ndarray:
    ens = Ensemble.load(ck, torch.device("cpu"))
    meta = ens.meta
    x = chart.x
    uses_obs = meta["arch"]["in_channels"] > chart.x.shape[0]
    if uses_obs:
        x = torch.cat([x, chart.observed_channels(obs_mask)], 0)
    out = ens.predict(x[None])
    return out["emb"].astype(np.float32)


def load(split: str) -> dict[str, np.ndarray]:
    d = np.load(extract(split))
    return {k: d[k] for k in d.files}


def gather(field: np.ndarray, Z: np.ndarray, N: np.ndarray, exists: np.ndarray):
    """Compound and target embeddings for rows (Z, N).

    ``has_target`` flags rows whose target (Z, N-1) exists in the chart."""
    H, W = exists.shape
    inside = (Z >= 0) & (Z < H) & (N >= 0) & (N < W)
    emb_cn = np.zeros((len(Z), field.shape[0]), np.float32)
    emb_cn[inside] = field[:, Z[inside], N[inside]].T
    Nt = N - 1
    has_t = inside & (Nt >= 0)
    has_t[has_t] &= exists[Z[has_t], Nt[has_t]]
    emb_tg = np.zeros_like(emb_cn)
    emb_tg[has_t] = field[:, Z[has_t], Nt[has_t]].T
    in_chart = inside.copy()
    in_chart[inside] &= exists[Z[inside], N[inside]]
    return emb_cn, emb_tg, has_t, in_chart
