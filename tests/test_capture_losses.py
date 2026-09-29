"""Acceptance tests for the Stage C capture losses (WP-15 step 2)."""
import torch

from models.losses import capture_loss, heteroscedastic_nll, teacher_loss

B, E = 3, 16


def test_nll_rewards_confidence_only_when_right() -> None:
    pred, target = torch.zeros(B, E), torch.zeros(B, E)
    trust = torch.ones(B, E)
    sure = heteroscedastic_nll(pred, target, torch.full((B, E), -2.0), trust)
    unsure = heteroscedastic_nll(pred, target, torch.full((B, E), 2.0), trust)
    assert sure < unsure, "a correct, confident prediction must score better than a vague one"
    wrong_sure = heteroscedastic_nll(pred + 1.0, target, torch.full((B, E), -2.0), trust)
    assert wrong_sure > unsure, "confident and wrong must be punished"


def test_trust_weighting_changes_the_answer() -> None:
    pred, target = torch.zeros(B, E), torch.ones(B, E)
    log_var = torch.zeros(B, E)
    full = heteroscedastic_nll(pred, target, log_var, torch.ones(B, E))
    half = heteroscedastic_nll(pred, target, log_var, torch.full((B, E), 0.5))
    assert torch.isclose(full, half, atol=1e-6), "uniform trust is a scale, not a shift"
    mixed = torch.ones(B, E)
    mixed[:, :E // 2] = 0.0
    assert heteroscedastic_nll(pred, target, log_var, mixed) <= full + 1e-6


def test_teacher_term_is_silent_where_measured() -> None:
    pred, teacher = torch.zeros(B, E), torch.ones(B, E)
    assert teacher_loss(pred, teacher, torch.ones(B, E)).item() == 0.0
    assert teacher_loss(pred, teacher, torch.zeros(B, E)).item() > 0.0


def test_capture_loss_parts_and_gradients() -> None:
    pred = torch.zeros(B, E, requires_grad=True)
    log_var = torch.zeros(B, E, requires_grad=True)
    # target 2.0, not 1.0: at squared error 1 and log_var 0 the variance gradient is
    # analytically zero (that point is the NLL's optimum), which would test nothing.
    out = capture_loss(pred, torch.full((B, E), 2.0), log_var, torch.ones(B, E),
                       torch.full((B, E), 0.5), torch.zeros(B, E))
    assert set(out) == {"nll", "teacher", "total"}
    assert torch.isclose(out["total"], out["nll"] + 0.1 * out["teacher"], atol=1e-6)
    out["total"].backward()
    assert pred.grad.abs().sum() > 0 and log_var.grad.abs().sum() > 0
