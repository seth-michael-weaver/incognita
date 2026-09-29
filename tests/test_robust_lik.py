"""C7's Student-t likelihood: its limits, its density, and the weight it claims to apply."""
from __future__ import annotations

import math

import torch
from scipy import stats

from models.losses import heteroscedastic_nll
from models.norm_latent import DatasetRows, norm_latent_nll
from models.robust_lik import FittedNu, student_t_nll, student_t_rows_nll, t_weight


def _cells(seed=0):
    torch.manual_seed(seed)
    pred = torch.randn(4, 6, dtype=torch.float64) * 0.3
    tgt = torch.randn(4, 6, dtype=torch.float64) * 0.3
    lv = torch.randn(4, 6, dtype=torch.float64) * 0.5 - 3.0
    trust = torch.rand(4, 6, dtype=torch.float64)
    return pred, tgt, lv, trust


def test_large_nu_is_the_shipped_gaussian():
    pred, tgt, lv, trust = _cells()
    g = heteroscedastic_nll(pred, tgt, lv, trust)
    t = student_t_nll(pred, tgt, lv, trust, 1e9)
    assert abs(float(g - t)) < 1e-6


def test_is_the_student_t_density():
    """Per point, the NLL is -log t_nu(r; 0, s) up to the Gaussian's own dropped constant."""
    pred, tgt, lv, _ = _cells(1)
    one = torch.zeros_like(pred)
    one[1, 2] = 1.0
    for nu in (2.0, 4.0, 15.0):
        got = float(student_t_nll(pred, tgt, lv, one, nu))
        s = math.exp(0.5 * float(lv[1, 2]))
        exact = -stats.t.logpdf(float(pred[1, 2] - tgt[1, 2]), nu, scale=s)
        # the shipped Gaussian NLL drops 0.5 log(2 pi) and works with log s^2, not log s
        assert abs(got - (exact - 0.5 * math.log(2 * math.pi))) < 1e-9


def test_gradient_is_the_gaussian_gradient_times_the_t_weight():
    pred, tgt, lv, trust = _cells(2)
    nu = 4.0
    pg = pred.clone().requires_grad_(True)
    heteroscedastic_nll(pg, tgt, lv, trust).backward()
    pt = pred.clone().requires_grad_(True)
    student_t_nll(pt, tgt, lv, trust, nu).backward()
    z2 = torch.exp(-lv) * (pred - tgt) ** 2
    assert torch.allclose(pt.grad, pg.grad * t_weight(z2, nu), atol=1e-12)


def test_rows_inf_is_c6_arm_b():
    torch.manual_seed(3)
    nuc = torch.tensor([0] * 5 + [1] * 3)
    bn = torch.tensor([0, 1, 2, 3, 4, 1, 2, 3])
    ds = torch.tensor([0] * 5 + [1] * 3)
    rows = DatasetRows(nuc, bn, torch.zeros(8), torch.full((8,), 0.01),
                       torch.tensor([1.0, 1.0, 0.5, 1.0, 1.0, 0.8, 0.8, 0.8]), ds,
                       torch.zeros(8), 2, ["a", "b"])
    pred, lv = torch.randn(3, 8) * 0.3, torch.full((3, 8), -4.0)
    mask = torch.tensor([1.0, 1, 1, 0, 1, 1, 1, 1])
    a = norm_latent_nll(pred, lv, rows, tau=0.0, row_mask=mask)
    b = student_t_rows_nll(pred, lv, rows, math.inf, row_mask=mask)
    assert torch.allclose(a, b, atol=1e-6)
    # and a finite nu down-weights the outlying row, so its NLL is smaller
    rows.y[0] = 3.0
    assert float(student_t_rows_nll(pred, lv, rows, 3.0)) < float(
        student_t_rows_nll(pred, lv, rows, math.inf))


def test_fitted_nu_moves_toward_heavy_tails_on_heavy_tailed_data():
    torch.manual_seed(4)
    r = torch.distributions.StudentT(3.0).sample((4000,)).double().reshape(1, -1)
    nu = FittedNu(init=30.0)
    opt = torch.optim.Adam(nu.parameters(), lr=0.05)
    for _ in range(400):
        opt.zero_grad()
        student_t_nll(r, torch.zeros_like(r), torch.zeros_like(r), torch.ones_like(r),
                      nu()).backward()
        opt.step()
    assert 2.0 < float(nu()) < 5.0
