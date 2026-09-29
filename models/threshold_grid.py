"""Stage C on a threshold-relative grid: resample the operator's axis, not its features (WP-19).

The spectral residual (``models/residual/fno.py``) runs on the 64-point log-energy grid that
every nuclide shares. For (n,2n) the kink sits at a different index per nuclide (54.6 to 60.6 on
that grid) and every measured bin sits in the top nine, 55-63, directly against the edge of the
FFT's periodic domain. The idea WP-19 named as left: lay each nuclide out on u = log10(E/E_thr)
so the threshold lands on one index for all of them, run the operator there, and map r(E) back
to the physical grid, so the loss, the calibration and the scoring never see the change.

One thing this module has to respect, and its test proves: on a log grid, u = log10 E - log10
E_thr is a *translation*, and one FNO layer (lift, FFT-mode convolution, pointwise, gelu, heads)
is exactly equivariant under circular translation. Rolling each row so its threshold lands on a
common index is therefore a no-op -- it changes nothing the model computes. The layout can only
matter through what a roll cannot express: where the window's edges sit relative to the
threshold. So the aligned layout embeds the 64 physical bins in a longer, non-periodic window of
``LENGTH`` slots, edge-replicated outside the physical range, with the threshold at slot
``ANCHOR`` for every nuclide. The ``pad`` layout is its control: the same window, the same
padding, the same offset for every nuclide, so ``align`` against ``pad`` isolates the alignment
and ``pad`` against the unmodified model isolates the padding.

The shift is integer, so the forward map is a gather and the inverse is exact on every physical
bin; the threshold channel still carries the sub-bin position. Each row's shift is read off its
own threshold channel, log10(E/E_thr) = (p - k) * step in the unclipped range, so the model
needs no side table keyed on bundle row order and predicts correctly on any bundle.

    INCOGNITA_THRESHOLD_GRID = off (default) | align | pad
"""
from __future__ import annotations

import os

import torch
from torch import Tensor

from models.residual.fno import SpectralResidual

LENGTH = 80        # slots in the resampled window: the 64 physical bins plus 16 of padding
ANCHOR = 63        # slot every nuclide's threshold lands on under `align`
PAD_OFFSET = 5     # `pad`: every row shifted by the median `align` offset (target thresholds)
LAYOUTS = ("off", "align", "pad")


def layout_from_env() -> str:
    mode = os.environ.get("INCOGNITA_THRESHOLD_GRID", "off").strip().lower() or "off"
    if mode not in LAYOUTS:
        raise ValueError(f"INCOGNITA_THRESHOLD_GRID must be one of {LAYOUTS}, got {mode!r}")
    return mode


def threshold_index(channel: Tensor, lo: float = -2.0, hi: float = 1.0) -> Tensor:
    """(N,) fractional grid index of each row's threshold, read off log10(E/E_thr) per bin.

    The channel is linear in the bin index where it is not clipped, so two adjacent unclipped
    bins give the step and the intercept. The top two bins are used: an (n,2n) threshold between
    2 MeV and 2000 MeV leaves both inside (lo, hi) on a grid that ends at 20 MeV. A row where
    they are not (no threshold, or a flat channel) raises rather than aligning on nonsense.
    """
    top, below = channel[:, -1], channel[:, -2]
    step = top - below
    ok = (top > lo) & (top < hi) & (below > lo) & (below < hi) & (step > 0)
    if not bool(ok.all()):
        raise ValueError(
            f"{int((~ok).sum())} of {channel.shape[0]} rows have no unclipped threshold channel "
            "in their top two bins; the threshold grid cannot place them. INCOGNITA_THRESHOLD=off "
            "and a zero channel are not valid inputs for this layout.")
    n = channel.shape[1]
    return (n - 1) - top / step


def offsets(channel: Tensor, n_energy: int, layout: str, length: int = LENGTH,
            anchor: int = ANCHOR, pad_offset: int = PAD_OFFSET) -> Tensor:
    """(N,) integer slot of physical bin 0 for every row, clamped so all bins fit the window."""
    room = length - n_energy
    if room < 0:
        raise ValueError(f"window of {length} slots cannot hold {n_energy} bins")
    if layout == "pad":
        off = torch.full((channel.shape[0],), int(pad_offset), dtype=torch.long,
                         device=channel.device)
    elif layout == "align":
        off = anchor - torch.round(threshold_index(channel)).long()
    else:
        raise ValueError(f"offsets() needs layout 'align' or 'pad', got {layout!r}")
    return off.clamp(0, room)


def forward_index(off: Tensor, n_energy: int, length: int = LENGTH) -> Tensor:
    """(N, length) physical bin feeding each slot; edge bins repeat outside the physical range."""
    slots = torch.arange(length, device=off.device)[None, :]
    return (slots - off[:, None]).clamp(0, n_energy - 1)


def inverse_index(off: Tensor, n_energy: int) -> Tensor:
    """(N, n_energy) slot holding each physical bin."""
    return torch.arange(n_energy, device=off.device)[None, :] + off[:, None]


def to_window(x: Tensor, fwd: Tensor) -> Tensor:
    """Resample (N, E) or (N, E, C) onto the window."""
    if x.dim() == 2:
        return torch.gather(x, 1, fwd)
    return torch.gather(x, 1, fwd[..., None].expand(-1, -1, x.shape[-1]))


def from_window(x: Tensor, inv: Tensor) -> Tensor:
    """Map (N, L) window values back to the (N, E) physical grid. Exact inverse of to_window."""
    return torch.gather(x, 1, inv)


class ThresholdGridResidual(SpectralResidual):
    """SpectralResidual run on the threshold-relative window; inputs and outputs stay physical.

    Parameter shapes are those of SpectralResidual with the same arguments (the window length
    enters no weight), so construction consumes the RNG identically and a state dict moves
    between the two -- but a checkpoint trained here means something different there.
    """

    def __init__(self, *args, layout: str = "align", length: int = LENGTH, anchor: int = ANCHOR,
                 pad_offset: int = PAD_OFFSET, **kw) -> None:
        super().__init__(*args, **kw)
        if layout not in ("align", "pad"):
            raise ValueError(f"layout must be 'align' or 'pad', got {layout!r}")
        self.layout, self.length = layout, int(length)
        self.anchor, self.pad_offset = int(anchor), int(pad_offset)

    def forward(self, sigma_b: Tensor, embedding: Tensor,
                threshold: Tensor | None = None) -> tuple[Tensor, Tensor]:
        if threshold is None:
            raise ValueError("the threshold grid is placed by the threshold channel; got None")
        n_e = sigma_b.shape[1]
        chan = threshold if threshold.dim() == 2 else threshold[..., 0]
        off = offsets(chan, n_e, self.layout, self.length, self.anchor, self.pad_offset)
        fwd, inv = forward_index(off, n_e, self.length), inverse_index(off, n_e)
        r, sigma_r = super().forward(to_window(sigma_b, fwd), embedding,
                                     to_window(threshold, fwd))
        return from_window(r, inv), from_window(sigma_r, inv)


def residual_class(layout: str | None = None):
    """The residual constructor train_stage_c should use. `off` returns SpectralResidual itself."""
    layout = layout_from_env() if layout is None else layout
    if layout == "off":
        return SpectralResidual

    def build(*args, **kw) -> ThresholdGridResidual:
        return ThresholdGridResidual(*args, layout=layout, **kw)

    return build
