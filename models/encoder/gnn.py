"""Relational message-passing GNN over the nuclide chart (blueprint §5.2, option 1).

Nodes are the pixels where a nuclide exists; the edge set is the physics one —
(Z±1, N), (Z, N±1), (Z±1, N∓1) (beta direction), (Z±2, N±2) (alpha direction) — with one
linear message map per directed edge type (a relational GCN). Because the chart is a
regular grid, "gather neighbour j" is a shift of the node-feature image, so the whole
thing is torch-only (no PyG) and runs on the same ``(B, C, H, W)`` tensors as the CNN.
Messages from non-existent nuclides are masked out, so the irregular boundary of the
chart is respected rather than zero-padded.
"""

from __future__ import annotations

import torch
from torch import nn

from models.data import shift
from models.encoder.chart_cnn import MAX_LOG_SIGMA, MIN_LOG_SIGMA, HeadSpec

EDGES: tuple[tuple[int, int], ...] = (
    (1, 0),
    (-1, 0),
    (0, 1),
    (0, -1),
    (1, -1),
    (-1, 1),
    (2, 2),
    (-2, -2),
)


class NodeNorm(nn.Module):
    """LayerNorm over the channel axis of a ``(B, C, H, W)`` tensor, per pixel.

    GroupNorm/BatchNorm pool statistics over the whole image, which makes every node's
    embedding depend on every other node (a non-local leak that defeats the masked edge
    set); a per-node norm is the graph-correct choice.
    """

    def __init__(self, width: int):
        super().__init__()
        self.ln = nn.LayerNorm(width)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.ln(x.permute(0, 2, 3, 1)).permute(0, 3, 1, 2)


class MPLayer(nn.Module):
    def __init__(self, width: int, dropout: float = 0.0):
        super().__init__()
        self.msg = nn.ModuleList([nn.Conv2d(width, width, 1, bias=False) for _ in EDGES])
        self.self_map = nn.Conv2d(width, width, 1)
        self.update = nn.Sequential(
            NodeNorm(width),
            nn.SiLU(),
            nn.Conv2d(width, width, 1),
            nn.SiLU(),
            nn.Dropout2d(dropout) if dropout > 0 else nn.Identity(),
            nn.Conv2d(width, width, 1),
        )
        self.norm = NodeNorm(width)

    def forward(self, h: torch.Tensor, exists: torch.Tensor) -> torch.Tensor:
        agg = self.self_map(h)
        for (dz, dn), lin in zip(EDGES, self.msg, strict=True):
            nb = shift(h, dz, dn, 0.0) * shift(exists, dz, dn, 0.0)
            agg = agg + lin(nb)
        return h + self.update(self.norm(agg))


class ChartGNN(nn.Module):
    """Same interface as :class:`ChartCNN` (``embed``, ``forward``, ``heads_spec``)."""

    def __init__(
        self,
        in_channels: int,
        H: int,
        W: int,
        heads: list[HeadSpec],
        width: int = 96,
        n_blocks: int = 8,
        emb_dim: int = 256,
        zn_emb: int = 0,
        dilations: tuple[int, ...] = (),
        dropout: float = 0.0,
    ):
        super().__init__()
        self.H, self.W = H, W
        self.heads_spec = list(heads)
        self.zn_emb = zn_emb
        if zn_emb > 0:
            self.z_emb = nn.Embedding(H, zn_emb)
            self.n_emb = nn.Embedding(W, zn_emb)
        self.stem = nn.Sequential(
            nn.Conv2d(in_channels + 2 * zn_emb, width, 1), NodeNorm(width), nn.SiLU()
        )
        self.layers = nn.ModuleList([MPLayer(width, dropout) for _ in range(n_blocks)])
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
        exists = x[:, :1]  # channel 0 of the static features is the "nuclide exists" mask
        if self.zn_emb > 0:
            x = torch.cat([x, self.positional(x.shape[0])], 1)
        h = self.stem(x)
        for layer in self.layers:
            h = layer(h, exists)
        return self.to_emb(h)

    def forward(self, x: torch.Tensor) -> dict[str, torch.Tensor]:
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
