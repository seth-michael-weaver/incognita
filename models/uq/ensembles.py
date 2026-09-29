"""Deep ensembles for the mass model (blueprint §5.5).

Combination rule for M heteroscedastic members with means ``mu_m`` and aleatoric
sigmas ``s_m``::

    mu      = mean_m mu_m
    var_ale = mean_m s_m^2
    var_epi = var_m mu_m          (population variance across members)
    var     = var_ale + var_epi
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import torch

from models.encoder import make_encoder
from models.encoder.chart_cnn import ChartCNN, HeadSpec


def combine(means: np.ndarray, sigmas: np.ndarray) -> dict[str, np.ndarray]:
    """``means``/``sigmas``: (M, ...). Returns mean, sigma, sigma_aleatoric, sigma_epistemic."""
    mu = means.mean(0)
    var_ale = (sigmas**2).mean(0)
    var_epi = means.var(0)
    return {
        "mean": mu,
        "sigma": np.sqrt(var_ale + var_epi),
        "sigma_aleatoric": np.sqrt(var_ale),
        "sigma_epistemic": np.sqrt(var_epi),
    }


class Ensemble:
    """A list of trained :class:`ChartCNN` members sharing one architecture."""

    def __init__(self, members: list[ChartCNN], sigma_scale: float = 1.0):
        self.members = members
        self.sigma_scale = sigma_scale

    @torch.no_grad()
    def predict(self, x: torch.Tensor, head: str = "mass") -> dict[str, np.ndarray]:
        means, sigmas, embs = [], [], []
        for m in self.members:
            m.eval()
            out = m(x)
            means.append(out[f"{head}_mean"][0, 0].float().cpu().numpy())
            sigmas.append(torch.exp(out[f"{head}_log_sigma"][0, 0]).float().cpu().numpy())
            embs.append(out["emb"][0].float().cpu().numpy())
        res = combine(np.stack(means), np.stack(sigmas))
        res["sigma_raw"] = res["sigma"].copy()
        res["sigma"] = res["sigma"] * self.sigma_scale
        res["emb"] = np.mean(np.stack(embs), 0)
        res["members_mean"] = np.stack(means)
        return res

    @torch.no_grad()
    def predict_all(self, x: torch.Tensor) -> dict[str, np.ndarray]:
        """Every head, ensemble-combined (probabilities averaged for categorical heads)."""
        acc: dict[str, list[np.ndarray]] = {}
        for m in self.members:
            m.eval()
            out = m(x)
            for h in m.heads_spec:
                if h.kind == "gaussian":
                    acc.setdefault(f"{h.name}_mean", []).append(
                        out[f"{h.name}_mean"][0, 0].float().cpu().numpy()
                    )
                    acc.setdefault(f"{h.name}_sigma", []).append(
                        torch.exp(out[f"{h.name}_log_sigma"][0, 0]).float().cpu().numpy()
                    )
                else:
                    acc.setdefault(f"{h.name}_prob", []).append(
                        torch.softmax(out[f"{h.name}_logits"][0].float(), 0).cpu().numpy()
                    )
        res: dict[str, np.ndarray] = {}
        for h in self.members[0].heads_spec:
            if h.kind == "gaussian":
                c = combine(np.stack(acc[f"{h.name}_mean"]), np.stack(acc[f"{h.name}_sigma"]))
                res[f"{h.name}_mean"] = c["mean"]
                res[f"{h.name}_sigma"] = c["sigma"] * (self.sigma_scale if h.name == "mass" else 1)
            else:
                res[f"{h.name}_prob"] = np.mean(np.stack(acc[f"{h.name}_prob"]), 0)
        return res

    # ---- persistence ------------------------------------------------------------------
    def save(self, directory: Path, arch: dict, extra: dict | None = None) -> None:
        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)
        for i, m in enumerate(self.members):
            torch.save(m.state_dict(), directory / f"member_{i}.pt")
        meta = {
            "n_members": len(self.members),
            "arch": arch,
            "heads": [h.__dict__ for h in self.members[0].heads_spec],
            "sigma_scale": self.sigma_scale,
            **(extra or {}),
        }
        with open(directory / "ensemble.json", "w", encoding="utf-8") as fh:
            json.dump(meta, fh, indent=2)

    @classmethod
    def load(cls, directory: Path, device: str | torch.device = "cpu") -> Ensemble:
        directory = Path(directory)
        with open(directory / "ensemble.json", encoding="utf-8") as fh:
            meta = json.load(fh)
        heads = [HeadSpec(**h) for h in meta["heads"]]
        members = []
        for i in range(meta["n_members"]):
            m = make_encoder(meta["arch"], heads)
            m.load_state_dict(torch.load(directory / f"member_{i}.pt", map_location=device))
            members.append(m.to(device).eval())
        ens = cls(members, sigma_scale=meta.get("sigma_scale", 1.0))
        ens.meta = meta
        return ens
