"""Multi-task and physics-consistency losses for the mass model (blueprint §5.2).

All continuous quantities are in MeV. Every loss is a masked mean over the pixels
where a target exists *and* that pixel belongs to the training set of the current
split, so a held-out nuclide never contributes a gradient, not even through a
neighbour-difference term.
"""

from __future__ import annotations

import torch
import torch.nn.functional as F

from models.data import shift


def masked_mean(x: torch.Tensor, mask: torch.Tensor, weight: torch.Tensor | None = None):
    m = mask.to(x.dtype)
    if weight is not None:
        m = m * weight
    denom = m.sum().clamp_min(1.0)
    x = torch.where(m > 0, x, torch.zeros_like(x))  # NaN/inf outside the mask is harmless
    return (x * m).sum() / denom


def gaussian_nll(
    mean: torch.Tensor,
    log_sigma: torch.Tensor,
    target: torch.Tensor,
    target_sigma: torch.Tensor | None,
    mask: torch.Tensor,
    weight: torch.Tensor | None = None,
) -> torch.Tensor:
    """Heteroscedastic Gaussian NLL; predicted variance is added to the measurement variance."""
    var = torch.exp(2 * log_sigma)
    if target_sigma is not None:
        var = var + target_sigma**2
    nll = 0.5 * torch.log(var) + 0.5 * (target - mean) ** 2 / var
    return masked_mean(nll, mask, weight)


def masked_ce(logits: torch.Tensor, target: torch.Tensor, mask: torch.Tensor) -> torch.Tensor:
    ce = F.cross_entropy(logits, target, reduction="none")
    return masked_mean(ce, mask)


NEIGHBOUR = {"sn": (0, 1), "s2n": (0, 2), "sp": (1, 0), "s2p": (2, 0)}


def derived_residual_separation(resid: torch.Tensor, valid: torch.Tensor):
    """``S_pred - S_baseline`` (MeV) from the residual field, plus the pair-validity mask.

    S_n(Z,N) = M(Z,N-1) - M(Z,N) + m_n, so the residual part is r(Z,N-1) - r(Z,N); the
    baseline and the nucleon mass cancel. Zero-fill shifts keep NaN out of the graph.
    """
    out, masks = {}, {}
    vf = valid.to(resid.dtype)
    for key, (dz, dn) in NEIGHBOUR.items():
        out[key] = shift(resid, dz, dn, 0.0) - resid
        masks[key] = valid & shift(vf, dz, dn, 0.0).bool()
    return out, masks


def compute_losses(
    out: dict[str, torch.Tensor],
    batch: dict[str, torch.Tensor],
    weights: dict[str, float],
    head_names: dict[str, str],
) -> dict[str, torch.Tensor]:
    """Return every loss term plus ``total``.

    ``batch`` keys (all (H, W) tensors on the model device):
      train        bool  pixels of the split's training set with measured mass
      loss_w       float weight per pixel for the mass loss (1 for dropped-from-input,
                         smaller for visible pixels), 0 outside ``train``
      aux_train    bool  pixels allowed for non-mass targets (everything except test)
      valid        bool  pixels with a baseline
      <target>_value / _sigma / _mask   from ChartData.targets
    """
    losses: dict[str, torch.Tensor] = {}
    train = batch["train"]
    valid = batch["valid"]

    # --- mass residual ------------------------------------------------------------------
    mean = out["mass_mean"][0, 0]
    ls = out["mass_log_sigma"][0, 0]
    losses["mass_nll"] = gaussian_nll(
        mean, ls, batch["mass_value"], batch["mass_sigma"], train, batch["loss_w"]
    )
    losses["mass_mse"] = masked_mean((mean - batch["mass_value"]) ** 2, train, batch["loss_w"])

    # --- direct heads for the other continuous / categorical targets -------------------
    for name, kind in head_names.items():
        if name == "mass":
            continue
        mask = batch[f"{name}_mask"] & batch["aux_train"]
        if kind == "gaussian":
            losses[f"{name}_nll"] = gaussian_nll(
                out[f"{name}_mean"][0, 0],
                out[f"{name}_log_sigma"][0, 0],
                batch[f"{name}_value"],
                batch.get(f"{name}_sigma"),
                mask,
            )
        else:
            losses[f"{name}_ce"] = masked_ce(
                out[f"{name}_logits"][:, :, :, :], batch[f"{name}_value"][None], mask[None]
            )

    # --- physics consistency ------------------------------------------------------------
    derived, pair_valid = derived_residual_separation(mean, valid)
    trf = train.to(mean.dtype)
    cons_data = mean.new_zeros(())
    cons_head = mean.new_zeros(())
    n_terms = 0
    for key, (dz, dn) in NEIGHBOUR.items():
        both_train = train & shift(trf, dz, dn, 0.0).bool()
        d = derived[key]
        if f"{key}_mask" in batch:
            m = both_train & batch[f"{key}_mask"]
            cons_data = cons_data + masked_mean((d - batch[f"{key}_value"]) ** 2, m)
            n_terms += 1
        if key in head_names:
            cons_head = cons_head + masked_mean(
                (out[f"{key}_mean"][0, 0] - d.detach()) ** 2, pair_valid[key]
            )
    losses["sep_consistency"] = cons_data / max(n_terms, 1)
    losses["head_consistency"] = cons_head / max(n_terms, 1)

    # odd-even staggering along N and Z: 3-point second difference of the predicted
    # residual field versus the measured one, on triplets fully inside the training set.
    oes = mean.new_zeros(())
    r_exp = torch.where(train, batch["mass_value"], torch.zeros_like(mean))
    for dz, dn in ((0, 1), (1, 0)):
        t = train & shift(trf, dz, dn, 0.0).bool() & shift(trf, -dz, -dn, 0.0).bool()
        d_pred = 0.5 * (shift(mean, dz, dn, 0.0) - 2 * mean + shift(mean, -dz, -dn, 0.0))
        d_exp = 0.5 * (shift(r_exp, dz, dn, 0.0) - 2 * r_exp + shift(r_exp, -dz, -dn, 0.0))
        oes = oes + masked_mean((d_pred - d_exp) ** 2, t)
    losses["oes"] = oes / 2

    # residual should vanish where there is no data (keeps extrapolation on the baseline)
    losses["offdata_l2"] = masked_mean(mean**2, valid & ~train)

    total = mean.new_zeros(())
    for k, v in losses.items():
        w = weights.get(k, None)
        if w is None:
            # per-target defaults: every direct head gets weights["aux"]
            w = weights.get("aux", 0.1)
        total = total + w * v
    losses["total"] = total
    return losses


# --- Stage C: capture cross sections (blueprint §5.6) ---------------------------------
#
# These work in log10 sigma, weighted by the WP-12 trust score of each measurement, with a
# teacher term that only speaks where no measurement exists. Everything stays differentiable:
# the training loop needs gradients through all of it.


def heteroscedastic_nll(
    pred_log: torch.Tensor,
    target_log: torch.Tensor,
    log_var: torch.Tensor,
    trust: torch.Tensor,
) -> torch.Tensor:
    """Trust-weighted Gaussian NLL in log10 sigma with a predicted per-point variance."""
    log_var = log_var.clamp(-10.0, 10.0)          # exp(-log_var) must not overflow
    nll = 0.5 * torch.exp(-log_var) * (pred_log - target_log).pow(2) + 0.5 * log_var
    return (trust * nll).sum() / trust.sum().clamp_min(1e-6)


def teacher_loss(
    pred_log: torch.Tensor,
    teacher_log: torch.Tensor,
    has_measurement: torch.Tensor,
    weight: float = 0.1,
) -> torch.Tensor:
    """Pull the prediction towards an evaluated library only where no measurement exists."""
    return weight * torch.mean((1.0 - has_measurement) * (pred_log - teacher_log).pow(2))


def capture_loss(
    pred_log: torch.Tensor,
    target_log: torch.Tensor,
    log_var: torch.Tensor,
    trust: torch.Tensor,
    teacher_log: torch.Tensor,
    has_measurement: torch.Tensor,
    teacher_weight: float = 0.1,
) -> dict[str, torch.Tensor]:
    """Combine the trust-weighted likelihood with the teacher term; returns each part."""
    nll = heteroscedastic_nll(pred_log, target_log, log_var, trust)
    teacher = teacher_loss(pred_log, teacher_log, has_measurement, weight=1.0)
    return {"nll": nll, "teacher": teacher, "total": nll + teacher_weight * teacher}
