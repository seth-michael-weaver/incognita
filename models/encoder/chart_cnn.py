"""Dilated residual CNN over the nuclide chart (blueprint §5.2, option 2).

The chart image ``(C, Zmax+1, Nmax+1)`` goes through a stem, ``n_blocks`` residual
blocks with cyclic dilations (receptive field ~60 pixels each way, i.e. the whole
chart), and out comes a per-pixel 256-d embedding. Multi-task heads are 1x1 convs on
the embedding: heteroscedastic Gaussian heads emit ``(mean, log_sigma)`` per pixel;
categorical heads emit logits. Learned Z and N embeddings are concatenated to the
input channels so the network can express shell structure that is not in the hand
features.
"""

from __future__ import annotations

from dataclasses import dataclass

import torch
from torch import nn

MIN_LOG_SIGMA = -4.6  # sigma >= 10 keV in MeV units
MAX_LOG_SIGMA = 3.0


@dataclass(frozen=True)
class HeadSpec:
    name: str
    kind: str  # "gaussian" | "categorical"
    n_out: int = 1  # classes for categorical


class ResBlock(nn.Module):
    def __init__(self, width: int, dilation: int, groups: int = 8, dropout: float = 0.0):
        super().__init__()
        self.conv1 = nn.Conv2d(width, width, 3, padding=dilation, dilation=dilation)
        self.n1 = nn.GroupNorm(groups, width)
        self.conv2 = nn.Conv2d(width, width, 3, padding=dilation, dilation=dilation)
        self.n2 = nn.GroupNorm(groups, width)
        self.act = nn.SiLU()
        self.drop = nn.Dropout2d(dropout) if dropout > 0 else nn.Identity()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        h = self.act(self.n1(self.conv1(x)))
        h = self.n2(self.conv2(self.drop(h)))
        return self.act(x + h)


class ChartCNN(nn.Module):
    def __init__(
        self,
        in_channels: int,
        H: int,
        W: int,
        heads: list[HeadSpec],
        width: int = 96,
        n_blocks: int = 8,
        emb_dim: int = 256,
        zn_emb: int = 16,
        dilations: tuple[int, ...] = (1, 2, 4, 8),
        dropout: float = 0.0,
    ):
        super().__init__()
        self.H, self.W = H, W
        self.heads_spec = list(heads)
        self.zn_emb = zn_emb
        if zn_emb > 0:  # learned lookup tables: pure position identity, easy to memorize with
            self.z_emb = nn.Embedding(H, zn_emb)
            self.n_emb = nn.Embedding(W, zn_emb)
        self.stem = nn.Sequential(
            nn.Conv2d(in_channels + 2 * zn_emb, width, 3, padding=1),
            nn.GroupNorm(8, width),
            nn.SiLU(),
        )
        self.blocks = nn.Sequential(
            *[
                ResBlock(width, dilations[i % len(dilations)], dropout=dropout)
                for i in range(n_blocks)
            ]
        )
        self.to_emb = nn.Sequential(nn.Conv2d(width, emb_dim, 1), nn.SiLU())
        self.heads = nn.ModuleDict()
        for h in heads:
            n_out = 2 if h.kind == "gaussian" else h.n_out
            self.heads[h.name] = nn.Sequential(
                nn.Conv2d(emb_dim, 128, 1), nn.SiLU(), nn.Conv2d(128, n_out, 1)
            )
        self.register_buffer("z_idx", torch.arange(H), persistent=False)
        self.register_buffer("n_idx", torch.arange(W), persistent=False)

    def positional(self, B: int) -> torch.Tensor:
        ze = self.z_emb(self.z_idx).T[:, :, None].expand(-1, self.H, self.W)
        ne = self.n_emb(self.n_idx).T[:, None, :].expand(-1, self.H, self.W)
        return torch.cat([ze, ne], 0)[None].expand(B, -1, -1, -1)

    def embed(self, x: torch.Tensor) -> torch.Tensor:
        B = x.shape[0]
        if self.zn_emb > 0:
            x = torch.cat([x, self.positional(B)], 1)
        h = self.stem(x)
        h = self.blocks(h)
        return self.to_emb(h)

    def forward(self, x: torch.Tensor) -> dict[str, torch.Tensor]:
        """``x``: (B, C, H, W). Returns ``emb`` plus per-head outputs.

        Gaussian heads: ``<name>_mean`` (B,1,H,W) and ``<name>_log_sigma``.
        Categorical heads: ``<name>_logits`` (B,K,H,W).
        """
        emb = self.embed(x)
        out: dict[str, torch.Tensor] = {"emb": emb}
        for h in self.heads_spec:
            y = self.heads[h.name](emb)
            if h.kind == "gaussian":
                out[f"{h.name}_mean"] = y[:, :1]
                out[f"{h.name}_log_sigma"] = y[:, 1:2].clamp(MIN_LOG_SIGMA, MAX_LOG_SIGMA)
            else:
                out[f"{h.name}_logits"] = y
        return out

    def n_params(self) -> int:
        return sum(p.numel() for p in self.parameters())
