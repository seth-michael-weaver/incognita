"""Stage C spectral residual: a multiplicative correction r(E) on Stage B cross sections.

The correction is produced by a small Fourier neural operator over the log-energy axis, so
it is smooth in energy by construction and cheap to evaluate over the whole grid at once.
It is conditioned on the nuclide embedding, and a data-density prior (see
``density_prior_loss``) pulls r towards 1 wherever no measurement constrains it (§5.4).
"""
from __future__ import annotations

import torch
from torch import Tensor, nn


class SpectralResidual(nn.Module):
    """Multiplicative correction r(E) and its uncertainty over the log-energy grid."""

    def __init__(self, n_energy: int, embed_dim: int, n_modes: int = 16, width: int = 64,
                 n_aux: int = 1) -> None:
        super().__init__()
        self.n_energy = int(n_energy)
        self.width = int(width)
        # a mode is a frequency of the real FFT, of which there are n_energy // 2 + 1
        self.n_modes = int(min(n_modes, self.n_energy // 2 + 1))

        # two lifted channels: the Stage B cross section, and how far the energy sits above the
        # (n,2n) threshold. Measured 2026-09-09: the model is unbiased below that threshold
        # (+0.004) and underpredicts by 0.097 above it, with the damage worst just above, where
        # the competing channel turns on fastest. A smooth operator cannot find a kink it is
        # never told about.
        # `n_aux` auxiliary per-energy channels beside the cross section. One (the (n,2n)
        # threshold) until 2026-09-13, and the default keeps every existing checkpoint loadable.
        # This is the only place a feature can enter as a *function of energy*: `lift_embed`
        # below is a per-nuclide constant broadcast over the grid, so a block routed through
        # the embedding can shift a nuclide's normalisation but cannot put a kink anywhere.
        self.n_aux = int(n_aux)
        self.lift_sigma = nn.Linear(1 + self.n_aux, width)
        self.lift_embed = nn.Linear(embed_dim, width)
        scale = 1.0 / (width * width) ** 0.5
        self.weight_real = nn.Parameter(torch.randn(self.n_modes, width, width) * scale)
        self.weight_imag = nn.Parameter(torch.randn(self.n_modes, width, width) * scale)
        self.pointwise = nn.Linear(width, width)
        self.head_log_r = nn.Linear(width, 1)
        self.head_scale = nn.Linear(width, 1)

        # start close to r = 1 and a small uncertainty: an untrained Stage C must not move
        # Stage B's cross sections, only learn to where data says otherwise (§5.4).
        with torch.no_grad():
            self.head_log_r.weight.mul_(1e-2)
            self.head_log_r.bias.zero_()
            self.head_scale.weight.mul_(1e-2)
            self.head_scale.bias.fill_(-2.0)

    def _features(self, sigma_b: Tensor, embedding: Tensor,
                  threshold: Tensor | None = None) -> Tensor:
        """Lift cross sections, threshold proximity and the embedding into channel space."""
        log_sigma = torch.log10(sigma_b.clamp_min(1e-12)).unsqueeze(-1)   # (B, E, 1)
        if threshold is None:
            threshold = log_sigma.new_zeros(*log_sigma.shape[:2], self.n_aux)
        elif threshold.dim() == 2:                                        # (B, E) -> (B, E, 1)
            threshold = threshold.unsqueeze(-1)
        if threshold.shape[-1] != self.n_aux:
            raise ValueError(f"model built for {self.n_aux} auxiliary channel(s), "
                             f"got {threshold.shape[-1]}")
        x = self.lift_sigma(torch.cat([log_sigma, threshold], dim=-1))    # (B, E, width)
        return x + self.lift_embed(embedding).unsqueeze(1)                # broadcast over energy

    def _spectral_conv(self, x: Tensor) -> Tensor:
        """Convolve along the energy axis by weighting the lowest Fourier modes."""
        xf = torch.fft.rfft(x, dim=1)                                     # (B, F, width) complex
        weight = torch.complex(self.weight_real, self.weight_imag)        # (M, width, width)
        modes = min(self.n_modes, xf.shape[1])
        out = torch.zeros_like(xf)
        out[:, :modes] = torch.einsum("bmi,mio->bmo", xf[:, :modes], weight[:modes])
        return torch.fft.irfft(out, n=x.shape[1], dim=1)                  # (B, E, width)

    def forward(self, sigma_b: Tensor, embedding: Tensor,
                threshold: Tensor | None = None) -> tuple[Tensor, Tensor]:
        """Return the multiplicative correction r(E) > 0 and its standard deviation."""
        x = self._features(sigma_b, embedding, threshold)
        h = torch.nn.functional.gelu(self._spectral_conv(x) + self.pointwise(x))
        log_r = self.head_log_r(h).squeeze(-1)                            # (B, E)
        sigma_r = torch.nn.functional.softplus(self.head_scale(h).squeeze(-1)) + 1e-6
        return torch.exp(log_r), sigma_r

    def corrected(self, sigma_b: Tensor, embedding: Tensor,
                  threshold: Tensor | None = None) -> tuple[Tensor, Tensor]:
        """Apply the correction: return the corrected cross section and its uncertainty."""
        r, sigma_r = self.forward(sigma_b, embedding, threshold)
        return sigma_b * r, sigma_b * sigma_r


def density_prior_loss(log_r: Tensor, density: Tensor, weight: float = 1.0) -> Tensor:
    """Penalise log r away from zero where the measured-data density is low."""
    return weight * torch.mean((1.0 - density) * log_r.pow(2))
