"""Acceptance test for the Stage C spectral residual (WP-15 step 1).

Written by hand before the implementation: it fixes the contract the implementation must meet.
"""
import torch

from models.residual.fno import SpectralResidual, density_prior_loss

B, E, D = 4, 64, 8


def _inputs(seed: int = 0) -> tuple[torch.Tensor, torch.Tensor]:
    g = torch.Generator().manual_seed(seed)
    sigma_b = torch.rand(B, E, generator=g) + 0.1          # barns, strictly positive
    embedding = torch.randn(B, D, generator=g)
    return sigma_b, embedding


def test_forward_shapes_and_positivity() -> None:
    m = SpectralResidual(n_energy=E, embed_dim=D)
    r, sigma_r = m(*_inputs())
    assert r.shape == (B, E) and sigma_r.shape == (B, E)
    assert torch.isfinite(r).all() and torch.isfinite(sigma_r).all()
    assert (r > 0).all(), "the correction is multiplicative, so it must be positive"
    assert (sigma_r > 0).all(), "an uncertainty must be positive"


def test_corrected_is_sigma_times_r() -> None:
    m = SpectralResidual(n_energy=E, embed_dim=D)
    sigma_b, emb = _inputs()
    r, sigma_r = m(sigma_b, emb)
    corrected, unc = m.corrected(sigma_b, emb)
    assert torch.allclose(corrected, sigma_b * r, atol=1e-5)
    assert torch.allclose(unc, sigma_b * sigma_r, atol=1e-5)


def test_output_depends_on_both_inputs() -> None:
    """A constant or pass-through correction must fail here."""
    m = SpectralResidual(n_energy=E, embed_dim=D)
    s1, e1 = _inputs(0)
    s2, e2 = _inputs(1)
    r_a, _ = m(s1, e1)
    r_b, _ = m(s2, e1)
    r_c, _ = m(s1, e2)
    assert not torch.allclose(r_a, r_b, atol=1e-6), "r(E) must depend on the cross sections"
    assert not torch.allclose(r_a, r_c, atol=1e-6), "r(E) must depend on the nuclide embedding"


def test_gradients_reach_the_parameters() -> None:
    m = SpectralResidual(n_energy=E, embed_dim=D)
    r, sigma_r = m(*_inputs())
    (r.sum() + sigma_r.sum()).backward()
    grads = [p.grad for p in m.parameters() if p.grad is not None and p.grad.abs().sum() > 0]
    assert grads, "no parameter received a gradient: the layers are not in the computation graph"


def test_density_prior_pulls_r_toward_one() -> None:
    log_r = torch.full((B, E), 0.5)
    dense = torch.ones(B, E)
    sparse = torch.zeros(B, E)
    assert density_prior_loss(torch.zeros(B, E), sparse).item() == 0.0
    loss_sparse = density_prior_loss(log_r, sparse).item()
    loss_dense = density_prior_loss(log_r, dense).item()
    assert loss_sparse > loss_dense, (
        "the prior must bite where data is sparse, not where it is dense")
