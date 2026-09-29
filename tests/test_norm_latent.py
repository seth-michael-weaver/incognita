"""The C6 marginal likelihood has a closed form, so it can be checked against the exact thing.

These are not smoke tests. `norm_latent_nll` claims to be the log-density of
``N(0, diag(v/w) + tau^2 11^T)``, and that density can be computed directly with a matrix
solve; if the Sherman-Morrison algebra is wrong the two disagree. Everything else in the module
(the mask, the tau=0 limit, the shrinkage) follows from that identity holding.
"""
from __future__ import annotations

import torch

from models.norm_latent import DatasetRows, build_rows, norm_latent_nll, posterior_shift


def _rows(w=None):
    nuc = torch.tensor([0] * 5 + [1] * 3)
    bn = torch.tensor([0, 1, 2, 3, 4, 1, 2, 3])
    ds = torch.tensor([0] * 5 + [1] * 3)
    y = torch.zeros(8)
    mv = torch.full((8,), 0.01)
    if w is None:
        w = torch.ones(8)
    return DatasetRows(nuc, bn, y, mv, w, ds, torch.zeros(8), 2, ["a", "b"])


def _pred(seed=0):
    torch.manual_seed(seed)
    return torch.randn(3, 8) * 0.3, torch.full((3, 8), -4.0)


def test_matches_exact_multivariate_normal():
    pred, lv = _pred()
    rows = _rows(torch.tensor([1.0, 1.0, 0.5, 1.0, 1.0, 0.8, 0.8, 0.8]))
    tau = 0.079
    r = pred[rows.nuc_ix, rows.bin_ix] - rows.y
    v = torch.exp(lv[rows.nuc_ix, rows.bin_ix]) + rows.meas_var
    nll, _ = norm_latent_nll(pred, lv, rows, tau=tau, reduce=False)
    for d in range(2):
        m = rows.ds_ix == d
        rd, vd = r[m].double(), (v[m] / rows.w[m]).double()
        cov = torch.diag(vd) + tau**2 * torch.ones(len(rd), len(rd), dtype=torch.float64)
        exact = 0.5 * (rd @ torch.linalg.solve(cov, rd) + torch.logdet(cov))
        assert torch.allclose(nll[d].double(), exact, atol=1e-5), f"dataset {d}"


def test_tau_zero_is_the_independent_likelihood():
    """With no latent the covariance is diagonal, so the marginal must factorise."""
    pred, lv = _pred(1)
    rows = _rows()
    nll, _ = norm_latent_nll(pred, lv, rows, tau=0.0, reduce=False)
    r = pred[rows.nuc_ix, rows.bin_ix] - rows.y
    v = torch.exp(lv[rows.nuc_ix, rows.bin_ix]) + rows.meas_var
    per_row = 0.5 * (r**2 / v + torch.log(v))
    indep = torch.zeros(2).index_add_(0, rows.ds_ix, per_row)
    assert torch.allclose(nll, indep, atol=1e-5)


def test_mask_removes_a_dataset_entirely():
    """A masked row must not reach its dataset's shared offset either.

    This is what keeps a cross-validation fold honest: the row mask is gathered from the same
    training weights the rest of the loss uses, and a held-out nuclide must contribute to
    neither the residual nor the latent. The MACS constraint failed exactly this test and cost
    0.1510 against 0.2035 in held-out RMS.
    """
    pred, lv = _pred(2)
    rows = _rows()
    mask = torch.tensor([1.0] * 5 + [0.0] * 3)
    masked = norm_latent_nll(pred, lv, rows, tau=0.079, row_mask=mask)
    alone = norm_latent_nll(pred, lv, DatasetRows(
        rows.nuc_ix[:5], rows.bin_ix[:5], rows.y[:5], rows.meas_var[:5], rows.w[:5],
        rows.ds_ix[:5], torch.zeros(5), 1, ["a"]), tau=0.079)
    assert torch.allclose(masked, alone, atol=1e-6)


def test_shrinkage_grows_with_evidence():
    """A one-point dataset keeps its offset; a many-point dataset has it forgiven.

    That asymmetry is the whole reason to marginalise rather than subtract a point estimate:
    harmonisation applies a shift estimated from thin overlap to every point of the dataset.
    """
    tau = 0.079
    offset = 0.4
    shifts = []
    for n in (1, 4, 20):
        nuc = torch.zeros(n, dtype=torch.long)
        bn = torch.arange(n) % 8
        rows = DatasetRows(nuc, bn, torch.full((n,), -offset), torch.full((n,), 0.01),
                           torch.ones(n), torch.zeros(n, dtype=torch.long),
                           torch.zeros(n), 1, ["a"])
        pred = torch.zeros(1, 8)
        lv = torch.full((1, 8), -4.0)
        shifts.append(float(posterior_shift(pred, lv, rows, tau=tau)[0]))
    assert shifts[0] < shifts[1] < shifts[2], shifts
    # One point forgives 18% of the offset and leaves 82% in the residual; twenty points
    # forgive 82%. That ratio is the behaviour harmonisation cannot have -- it applies the
    # same estimated shift whether it rests on one overlapping cell or forty.
    assert shifts[0] < 0.25 * offset
    assert shifts[2] > 0.80 * offset


def test_build_rows_defaults_a_missing_uncertainty():
    """A point whose author quoted nothing is not a perfect measurement."""
    rows = build_rows([
        {"nuc_ix": 0, "bin": 1, "log10": -1.0, "sigma_log10": 0.0, "weight": 1.0,
         "dataset_key": "x", "is_test": 0.0},
        {"nuc_ix": 0, "bin": 2, "log10": -1.1, "sigma_log10": 0.05, "weight": 1.0,
         "dataset_key": "x", "is_test": 1.0},
    ], ["Z050N078M0"], 8)
    assert rows.n_datasets == 1 and len(rows) == 2
    assert abs(float(rows.meas_var[0]) - 0.1**2) < 1e-9
    assert abs(float(rows.meas_var[1]) - 0.05**2) < 1e-9
    assert float(rows.is_test.sum()) == 1.0


def test_empty_rows_are_safe():
    rows = build_rows([], [], 8)
    assert len(rows) == 0 and rows.n_datasets == 0
