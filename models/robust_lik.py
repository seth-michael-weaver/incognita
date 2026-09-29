"""Student-t data likelihood for Stage C (register C7, ROBUSTLIK).

A Gaussian likelihood's pull on the fit grows without bound in a point's residual, so a
discrepant EXFOR dataset -- wrong normalisation, understated errors, a stale monitor -- pulls
hardest exactly where it is most wrong. A Student-t with ``nu`` degrees of freedom is the
Gaussian scale mixture ``r ~ N(0, s^2 / lambda)``, ``lambda ~ Gamma(nu/2, nu/2)``; its pull is
bounded and decays past a few scale units, and the effective (IRLS / E-step) weight the fit
gives a point is

    w = (nu + 1) / (nu + r^2 / s^2)

so a point five scales out at nu = 4 counts for a sixth of a point on the model. No nuisance
parameter, no marginalisation: this is NOT C6 (``models/norm_latent.py`` integrates out a
per-dataset *normalisation*; this changes the *tail* of the per-point noise).

Two likelihood units, because the bundle has two:

* :func:`student_t_nll` -- per **cell**, on the bundle's trust-weighted bin mean. Drop-in for
  :func:`models.losses.heteroscedastic_nll`: same arguments, same variance convention, same
  trust normalisation, and the caller routes ``nu = inf`` to the shipped function so that arm
  is bit-identical to the baseline.
* :func:`student_t_rows_nll` -- per **row** (one EXFOR point) over ``DatasetRows``, the
  per-dataset structure ``models/norm_latent.py`` built for C6. This is the unit a discrepant
  dataset lives in: 55% of the trained cells mix two or more datasets, so a cell-level weight
  cannot single one out. Its ``nu = inf`` limit is ``norm_latent_nll(tau=0)``, C6's arm B, which
  is *not* the shipped likelihood (+0.57%, n.s., in C6); it carries its own Gaussian control.

``nu`` is either a float (fixed hyperparameter) or a tensor (fitted jointly; see
:class:`FittedNu`). The full normalising constant is kept because it is what makes ``nu``
identifiable when fitted; for fixed ``nu`` it is a constant and moves no gradient.
"""
from __future__ import annotations

import math

import torch
from torch import Tensor

from models.norm_latent import DatasetRows, _segment_sum


def _log_norm(nu: Tensor | float) -> Tensor | float:
    """``log Gamma(nu/2) - log Gamma((nu+1)/2) + 0.5 log(nu pi)``: -log of the t density's
    constant, less the Gaussian's ``0.5 log(2 pi)`` so both NLLs share a zero as nu -> inf."""
    if isinstance(nu, Tensor):
        return (torch.lgamma(nu / 2) - torch.lgamma((nu + 1) / 2)
                + 0.5 * torch.log(nu * math.pi) - 0.5 * math.log(2 * math.pi))
    return (math.lgamma(nu / 2) - math.lgamma((nu + 1) / 2)
            + 0.5 * math.log(nu * math.pi) - 0.5 * math.log(2 * math.pi))


def _t_terms(z2: Tensor, nu: Tensor | float) -> Tensor:
    """Per-point ``(nu+1)/2 log(1 + z^2/nu) + log-normaliser``, the part replacing ``z^2/2``."""
    return 0.5 * (nu + 1.0) * torch.log1p(z2 / nu) + _log_norm(nu)


def student_t_nll(pred_log: Tensor, target_log: Tensor, log_var: Tensor, trust: Tensor,
                  nu: Tensor | float) -> Tensor:
    """Trust-weighted Student-t NLL per cell; ``heteroscedastic_nll`` with a t tail.

    ``exp(log_var)`` is the t's squared *scale* (not its variance, which is
    ``s^2 nu / (nu - 2)``), exactly as it is the Gaussian's variance in the shipped loss.
    """
    log_var = log_var.clamp(-10.0, 10.0)
    z2 = torch.exp(-log_var) * (pred_log - target_log).pow(2)
    nll = _t_terms(z2, nu) + 0.5 * log_var
    return (trust * nll).sum() / trust.sum().clamp_min(1e-6)


def student_t_rows_nll(pred_log: Tensor, log_var: Tensor, rows: DatasetRows,
                       nu: Tensor | float, *, row_mask: Tensor | None = None) -> Tensor:
    """Per-row Student-t NLL over EXFOR points, on ``norm_latent_nll``'s conventions.

    Variance of a row is the model's predicted variance plus the point's quoted variance,
    divided by its trust weight; the result is normalised by total row weight. With
    ``nu = inf`` this is ``norm_latent_nll(..., tau=0)`` term for term.
    """
    r = pred_log[rows.nuc_ix, rows.bin_ix] - rows.y
    v = (torch.exp(log_var[rows.nuc_ix, rows.bin_ix].clamp(-10.0, 10.0))
         + rows.meas_var).clamp_min(1e-8)
    w = (rows.w if row_mask is None else rows.w * row_mask).clamp_min(0.0)
    keep = (w > 0).float()
    ve = (v / w.clamp_min(1e-12)) * keep + (1.0 - keep)
    z2 = r * r / ve
    if isinstance(nu, float) and math.isinf(nu):
        per = 0.5 * z2
    else:
        per = _t_terms(z2, nu)
    per = keep * (per + 0.5 * torch.log(ve))
    n = rows.n_datasets
    nll = _segment_sum(per, rows.ds_ix, n)
    wd = _segment_sum(w, rows.ds_ix, n)
    return nll.sum() / wd.sum().clamp_min(1e-9)


def t_weight(z2: Tensor, nu: float) -> Tensor:
    """The E-step weight ``(nu+1)/(nu+z^2)``; 1 everywhere for a Gaussian."""
    if math.isinf(nu):
        return torch.ones_like(z2)
    return (nu + 1.0) / (nu + z2)


class FittedNu(torch.nn.Module):
    """Degrees of freedom as a free parameter, ``nu = 1 + exp(theta)`` so the t keeps a mean.

    Fitted by the same optimiser as the network, inside one fold's training loss, so a fold
    never sees another fold's nu.
    """

    def __init__(self, init: float = 8.0) -> None:
        super().__init__()
        self.theta = torch.nn.Parameter(torch.tensor(math.log(init - 1.0)))

    def forward(self) -> Tensor:
        return 1.0 + torch.exp(self.theta)
