"""Neural surrogate of TALYS: sigma(nuclide, Stage-B parameters, E) -> log10 xs per channel.

BLUEPRINT §5.3 option 2.  Inputs are (i) nuclide features from
:func:`physics.features.feature_matrix` plus Sn of the compound nucleus,
(ii) the coded Stage-B parameter vector of :mod:`physics.talys.params`
(categoricals one-hot, continuous scaled to [-1, 1]) and (iii) log10 of the
incident energy.  Output is one head per channel (``total, elastic, capture,
inelastic, n2n, np, na``) giving log10 sigma in mb, optionally with a
heteroscedastic log-variance per channel.

The model is a small residual MLP (pre-LayerNorm blocks) so that autograd
gives d(log sigma)/d(parameter) for the differentiable-reaction-model use
(§5.3): see :meth:`TalysSurrogate.gradient_wrt_params`.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

import numpy as np
import torch
from torch import nn

from physics import features as F
from physics.talys import params as P

CHANNELS: tuple[str, ...] = ("total", "elastic", "capture", "inelastic", "n2n", "np", "na")

LOG10_E_MIN, LOG10_E_MAX = -3.0, np.log10(20.0)


# ---------------------------------------------------------------------------
# Featurisation
# ---------------------------------------------------------------------------


@dataclass
class FeaturizerStats:
    """Standardisation constants for the nuclide block, fitted on the training set."""

    mean: list[float] = field(default_factory=list)
    std: list[float] = field(default_factory=list)


# Lattice Fourier features: sin/cos on N and Z at each period, meant to give the network the
# shell periodicity directly instead of making it learn one from (Z, N).
#
# Off by default, because they make the surrogate worse. On the synthetic fixture in
# tests/test_surrogate.py they take held-out capture RMS from 0.28 to 1.13 against a 0.35
# gate -- a factor of three, and the reason that test was red. The end-to-end run measured
# the same direction earlier. A periodic basis over a lattice with 40-odd points per axis
# aliases badly and buys nothing the network could not fit anyway; the shell information that
# does help arrives as shell_features() in Stage C, as a distance to a closed shell rather
# than as a harmonic.
#
# Set INCOGNITA_FOURIER="2,4,8,16" to put them back. Checkpoints trained with them still load:
# Featurizer infers the periods it was trained under from the length of the saved statistics.
_LEGACY_FOURIER_PERIODS: tuple[float, ...] = (2.0, 4.0, 8.0, 16.0)
_os = __import__("os")
_env = _os.environ.get("INCOGNITA_FOURIER")
FOURIER_PERIODS: tuple[float, ...] = (
    tuple(float(x) for x in _env.split(",") if x.strip()) if _env is not None else ()
)


class Featurizer:
    """Builds the surrogate input vector; pure numpy so it works for the chart at once."""

    def __init__(self, stats: FeaturizerStats | None = None):
        self.stats = stats
        # A checkpoint carries its own geometry: infer the Fourier periods from the length of
        # the saved statistics rather than trusting a global, so an old checkpoint loads under
        # new defaults instead of failing on a shape mismatch.
        self._periods = FOURIER_PERIODS
        if stats is not None:
            extra = len(stats.mean) - (len(F.FEATURE_NAMES) + 4)
            if extra >= 0 and extra % 4 == 0:
                # ... including when the default is now empty and the checkpoint was not
                trained_with = FOURIER_PERIODS or _LEGACY_FOURIER_PERIODS
                self._periods = tuple(trained_with[: extra // 4])
        # + Sn(CN) [MeV], + Sn-missing flag, + Fermi-gas exponent 2*sqrt(aU), + sqrt(U),
        # + 16 Fourier features (sin/cos on N and Z at periods 2, 4, 8, 16)
        self.n_nuclide = len(F.FEATURE_NAMES) + 4 + 4 * len(self._periods)
        self.n_cat = sum(len(p.choices) for p in P.PARAMS if p.kind == "cat")
        self.n_cont = sum(1 for p in P.PARAMS if p.kind != "cat")
        self.n_in = self.n_nuclide + self.n_cat + self.n_cont + 1

    # -- nuclide block ----------------------------------------------------
    @staticmethod
    def nuclide_raw(Z, N, sn_cn_kev, periods=None) -> np.ndarray:
        periods = FOURIER_PERIODS if periods is None else periods
        Z = np.atleast_1d(np.asarray(Z, dtype=np.int64))
        N = np.atleast_1d(np.asarray(N, dtype=np.int64))
        sn = np.atleast_1d(np.asarray(sn_cn_kev, dtype=float)) / 1000.0
        missing = ~np.isfinite(sn)
        sn = np.where(missing, 0.0, sn)
        # The Fermi-gas exponent, handed over rather than left to be learned.
        #
        # Capture scales with the level density at the compound's excitation energy, and that
        # density goes as exp(2*sqrt(aU)) with a ~ A/8 MeV^-1 and U = Sn - Delta. Sn is the
        # carrier of every pairing and shell effect into the cross section, so the network's
        # sensitivity to it decides whether the odd-even staggering and the shell dips survive.
        # Measured 2026-09-09: TALYS itself gives d log10(sigma)/d Sn = +0.268 per MeV and the
        # surrogate reproduced only +0.153, 57% of it - which is why Stage B's chains came out
        # at 0.842 roughness against nature's 1.073 and every shell dip was 1.6x too shallow.
        # An MLP asked to learn exp(2*sqrt(aU)) from Sn alone will smooth it; given the exponent
        # it only has to learn the deviations.
        A = (np.atleast_1d(np.asarray(Z, dtype=float))
             + np.atleast_1d(np.asarray(N, dtype=float)) + 1.0)      # compound mass number
        a_ld = A / 8.0                                               # MeV^-1, the usual scaling
        delta = 12.0 / np.sqrt(np.maximum(A, 1.0))                   # pairing gap, MeV
        even_z = (np.atleast_1d(np.asarray(Z, dtype=np.int64)) % 2 == 0)
        even_n = ((np.atleast_1d(np.asarray(N, dtype=np.int64)) + 1) % 2 == 0)   # compound N
        shift = np.where(even_z & even_n, delta, np.where(even_z | even_n, 0.0, -delta))
        U = np.maximum(sn - shift, 0.1)
        fermi = 2.0 * np.sqrt(a_ld * U)                              # the exponent itself

        # Fourier features on the lattice, to defeat spectral bias.
        #
        # The odd-even staggering is a period-2 oscillation in N - the Nyquist frequency of the
        # nuclide chart - and a plain MLP is documented to under-fit exactly that. Measured
        # here: TALYS gives d log10(sigma)/d Sn = +0.268 per MeV and the surrogate reproduced
        # 0.153, with chains 0.78 as rough as nature's. The network holds every structural
        # feature it needs (dN_magic, N_even, the pairing term) and still smooths, because an
        # MSE over 238k rows spends its gradient on the trend: fine structure is only 16% of
        # the variance. Sines and cosines at period 2, 4, 8 and 16 give it a basis in which the
        # sawtooth is a single coefficient rather than a high-frequency fit.
        Zf = np.atleast_1d(np.asarray(Z, dtype=float))
        Nf = np.atleast_1d(np.asarray(N, dtype=float))
        waves = []
        # period 2 is pairing, period 4 the sub-shell alternation; longer periods are not a
        # known physical structure and mostly gave the network room to overfit held-out chains
        for period in periods:
            for v in (Nf, Zf):
                waves.append(np.sin(2.0 * np.pi * v / period)[:, None])
                waves.append(np.cos(2.0 * np.pi * v / period)[:, None])
        return np.concatenate(
            [F.feature_matrix(Z, N), sn[:, None], missing.astype(float)[:, None],
             fermi[:, None], np.sqrt(U)[:, None], *waves], axis=1
        )

    def fit(self, Z, N, sn_cn_kev) -> FeaturizerStats:
        raw = self.nuclide_raw(Z, N, sn_cn_kev, self._periods)
        mean = raw.mean(axis=0)
        std = raw.std(axis=0)
        std = np.where(std > 1e-8, std, 1.0)
        self.stats = FeaturizerStats(mean.tolist(), std.tolist())
        return self.stats

    def nuclide_block(self, Z, N, sn_cn_kev) -> np.ndarray:
        if self.stats is None:
            raise RuntimeError("Featurizer.fit() first")
        raw = self.nuclide_raw(Z, N, sn_cn_kev, self._periods)
        return (raw - np.asarray(self.stats.mean)) / np.asarray(self.stats.std)

    # -- parameter block ----------------------------------------------------
    @staticmethod
    def param_block(coded: np.ndarray) -> np.ndarray:
        """(n, N_PARAMS) coded -> (n, n_cat + n_cont) one-hot + scaled continuous."""
        coded = np.atleast_2d(np.asarray(coded, dtype=float))
        cols: list[np.ndarray] = []
        for j, p in enumerate(P.PARAMS):
            x = coded[:, j]
            if p.kind == "cat":
                idx = np.clip(np.floor(x).astype(int), 0, len(p.choices) - 1)
                oh = np.zeros((len(x), len(p.choices)))
                oh[np.arange(len(x)), idx] = 1.0
                cols.append(oh)
            else:
                lo, hi = p.coded_bounds
                cols.append(((x - lo) / (hi - lo) * 2.0 - 1.0)[:, None])
        return np.concatenate(cols, axis=1)

    @staticmethod
    def energy_block(log10_e_mev: np.ndarray) -> np.ndarray:
        x = np.asarray(log10_e_mev, dtype=float)
        return ((x - LOG10_E_MIN) / (LOG10_E_MAX - LOG10_E_MIN) * 2.0 - 1.0)[:, None]

    def __call__(self, Z, N, sn_cn_kev, coded, log10_e_mev) -> np.ndarray:
        return np.concatenate(
            [
                self.nuclide_block(Z, N, sn_cn_kev),
                self.param_block(coded),
                self.energy_block(log10_e_mev),
            ],
            axis=1,
        )


# ---------------------------------------------------------------------------
# Model
# ---------------------------------------------------------------------------


class ResidualBlock(nn.Module):
    def __init__(self, width: int, dropout: float = 0.0):
        super().__init__()
        self.norm = nn.LayerNorm(width)
        self.fc1 = nn.Linear(width, width * 2)
        self.fc2 = nn.Linear(width * 2, width)
        self.act = nn.SiLU()
        self.drop = nn.Dropout(dropout) if dropout > 0 else nn.Identity()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return x + self.fc2(self.drop(self.act(self.fc1(self.norm(x)))))


@dataclass
class SurrogateConfig:
    n_in: int
    n_out: int = len(CHANNELS)
    width: int = 256
    n_blocks: int = 4
    dropout: float = 0.0
    heteroscedastic: bool = False
    channels: tuple[str, ...] = CHANNELS


class TalysSurrogate(nn.Module):
    def __init__(self, cfg: SurrogateConfig):
        super().__init__()
        self.cfg = cfg
        self.inp = nn.Linear(cfg.n_in, cfg.width)
        self.blocks = nn.ModuleList(
            [ResidualBlock(cfg.width, cfg.dropout) for _ in range(cfg.n_blocks)]
        )
        self.norm = nn.LayerNorm(cfg.width)
        n_head = cfg.n_out * (2 if cfg.heteroscedastic else 1)
        self.head = nn.Linear(cfg.width, n_head)

    def forward(self, x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor | None]:
        h = self.inp(x)
        for b in self.blocks:
            h = b(h)
        out = self.head(self.norm(h))
        if self.cfg.heteroscedastic:
            mu, logvar = out.chunk(2, dim=-1)
            return mu, logvar.clamp(-10.0, 5.0)
        return out, None

    @property
    def n_params(self) -> int:
        return sum(p.numel() for p in self.parameters())


def masked_loss(
    mu: torch.Tensor,
    logvar: torch.Tensor | None,
    y: torch.Tensor,
    channel_weights: torch.Tensor | None = None,
) -> torch.Tensor:
    """Mean squared (or Gaussian NLL) error over finite targets only."""
    mask = torch.isfinite(y)
    y0 = torch.where(mask, y, torch.zeros_like(y))
    if logvar is None:
        per = (mu - y0) ** 2
    else:
        per = 0.5 * (logvar + (mu - y0) ** 2 / torch.exp(logvar))
    if channel_weights is not None:
        per = per * channel_weights
    per = torch.where(mask, per, torch.zeros_like(per))
    return per.sum() / mask.sum().clamp(min=1)


# ---------------------------------------------------------------------------
# Bundle: model + featurizer + metadata, with save / load / predict / gradients
# ---------------------------------------------------------------------------


class SurrogateBundle:
    def __init__(self, model: TalysSurrogate, featurizer: Featurizer, meta: dict | None = None):
        self.model = model
        self.featurizer = featurizer
        self.meta = meta or {}

    @property
    def device(self) -> torch.device:
        return next(self.model.parameters()).device

    def to(self, device) -> SurrogateBundle:
        self.model.to(device)
        return self

    def save(self, path: Path | str) -> Path:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        torch.save(
            {
                "state_dict": self.model.state_dict(),
                "config": asdict(self.model.cfg),
                "featurizer": asdict(self.featurizer.stats),
                "meta": self.meta,
                "param_names": list(P.PARAM_NAMES),
                "feature_names": list(F.FEATURE_NAMES),
            },
            path,
        )
        path.with_suffix(".json").write_text(json.dumps(self.meta, indent=1, default=float))
        return path

    @classmethod
    def load(cls, path: Path | str, device: str | torch.device = "cpu") -> SurrogateBundle:
        ck = torch.load(Path(path), map_location=device, weights_only=False)
        cfg = SurrogateConfig(**{**ck["config"], "channels": tuple(ck["config"]["channels"])})
        model = TalysSurrogate(cfg)
        model.load_state_dict(ck["state_dict"])
        model.to(device).eval()
        feat = Featurizer(FeaturizerStats(**ck["featurizer"]))
        return cls(model, feat, ck.get("meta", {}))

    # -- inference ----------------------------------------------------------
    def _inputs(self, Z, N, sn_cn_kev, coded, log10_e_mev) -> torch.Tensor:
        x = self.featurizer(Z, N, sn_cn_kev, coded, log10_e_mev)
        return torch.as_tensor(x, dtype=torch.float32, device=self.device)

    #: rows per forward pass at inference; 2^18 x width 256 keeps the transient
    #: activations of a whole-chart call under ~1 GB on an 8 GB GPU.
    chunk_rows: int = 1 << 18

    #: Autocast dtype for CUDA inference (``torch.float16`` roughly halves the
    #: whole-chart wall time); ``None`` keeps full fp32.  Gradients always use fp32.
    inference_dtype: torch.dtype | None = None

    def _forward_chunked(self, x: torch.Tensor) -> torch.Tensor:
        self.model.eval()
        autocast = self.inference_dtype is not None and x.device.type == "cuda"
        with torch.autocast("cuda", dtype=self.inference_dtype or torch.float32, enabled=autocast):
            if len(x) <= self.chunk_rows:
                out = self.model(x)[0]
            else:
                out = torch.cat(
                    [
                        self.model(x[i : i + self.chunk_rows])[0]
                        for i in range(0, len(x), self.chunk_rows)
                    ]
                )
        return out.float()

    @torch.no_grad()
    def predict(self, Z, N, sn_cn_kev, coded, log10_e_mev) -> np.ndarray:
        """Row-wise prediction: arrays of equal length n -> (n, n_channels) log10 mb."""
        return (
            self._forward_chunked(self._inputs(Z, N, sn_cn_kev, coded, log10_e_mev)).cpu().numpy()
        )

    @torch.no_grad()
    def predict_curves(self, Z, N, sn_cn_kev, coded, log10_e_grid) -> np.ndarray:
        """(n_nuclides, n_E, n_channels) for one parameter vector per nuclide over a grid.

        The nuclide + parameter block is featurised once per nuclide and the
        energy block once per grid point; the outer product is formed on the
        device, so a whole-chart call (~10^3 nuclides x 10^3 energies) is a
        handful of GPU forward passes rather than 10^6 rows of numpy work.
        """
        Z = np.atleast_1d(Z)
        N = np.atleast_1d(N)
        sn = np.atleast_1d(sn_cn_kev)
        coded = np.atleast_2d(coded)
        if coded.shape[0] == 1:
            coded = np.repeat(coded, len(Z), axis=0)
        e = np.asarray(log10_e_grid, dtype=float)
        nn_, ne = len(Z), len(e)
        dev = self.device
        nuc = torch.as_tensor(
            np.concatenate(
                [self.featurizer.nuclide_block(Z, N, sn), self.featurizer.param_block(coded)],
                axis=1,
            ),
            dtype=torch.float32,
            device=dev,
        )
        eb = torch.as_tensor(self.featurizer.energy_block(e), dtype=torch.float32, device=dev)
        x = torch.cat(
            [nuc[:, None, :].expand(nn_, ne, -1), eb[None, :, :].expand(nn_, ne, -1)], dim=-1
        ).reshape(nn_ * ne, -1)
        return self._forward_chunked(x).reshape(nn_, ne, -1).cpu().numpy()

    def gradient_wrt_params(
        self, Z, N, sn_cn_kev, coded, log10_e_mev, channel: str = "capture"
    ) -> np.ndarray:
        """Autograd d(log10 sigma_channel)/d(coded parameter) -> (n, N_PARAMS).

        Only the continuous parameters have a meaningful derivative; the
        one-hot categorical columns get the derivative w.r.t. their indicator.
        """
        self.model.eval()
        x = self._inputs(Z, N, sn_cn_kev, coded, log10_e_mev).requires_grad_(True)
        mu, _ = self.model(x)
        ci = self.model.cfg.channels.index(channel)
        g = torch.autograd.grad(mu[:, ci].sum(), x)[0].cpu().numpy()
        # map input columns back to coded parameters (chain rule through the scaling)
        off = self.featurizer.n_nuclide
        out = np.zeros((g.shape[0], P.N_PARAMS))
        for j, p in enumerate(P.PARAMS):
            if p.kind == "cat":
                off += len(p.choices)  # categorical: not differentiable, leave 0
            else:
                lo, hi = p.coded_bounds
                out[:, j] = g[:, off] * 2.0 / (hi - lo)
                off += 1
        return out
