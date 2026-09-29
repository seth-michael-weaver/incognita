"""Per-dataset normalisation as a latent variable, marginalised in the likelihood (C6).

The measurement noise floor (``docs/results/noise-floor.md``) decomposed the 0.162 log10
disagreement between independent experiments measuring the same cross section: **38% of it is a
whole-dataset normalisation shift** (sigma = 0.079 log10), and 62% is point-to-point scatter.
A normalisation error moves an entire measured curve together. That is a rank-1 correlated
term per dataset, and it is precisely the long-range correlation an evaluator encodes in an
ENDF MF33 covariance.

Stage C's likelihood has never had a term that can represent it. Two consequences, both
measured:

* **Fitting chases it.** Per-nuclide parameter fitting reaches TENDL-level error on the bins it
  fits and transfers nothing forward in time (Stage C -128% / -12.7% / -5.7%), because it is
  fitting each dataset's normalisation and the next decade's experiments do not share this
  decade's normalisations.
* **The intervals are too tight along energy.** G3 fails on exactly one clause: our energy
  correlation length is 3-6x shorter than ENDF MF33. A likelihood whose only randomness is
  independent per point cannot produce a long correlation length no matter how it is
  calibrated.

``stage_c_data`` already has a *harmonisation* path (``NORM_HARMONISE``): estimate each
dataset's shift against the consensus of the others and subtract it. It was measured and it
lost -- validation 0.1565 -> 0.1656, walking back to neutral as the overlap guard tightens.
That is the expected failure of a point estimate: a shift estimated from two overlapping cells
is mostly noise, and subtracting it injects that noise into every point of the dataset.

Marginalising is the other way to do the same thing, and it is the standard one. Let dataset
``d`` carry rows with residuals ``r_j = pred_j - y_j`` and per-point variances ``v_j``, and let
its unknown normalisation be ``n_d ~ N(0, tau^2)`` shared by every row:

    r_d | n_d ~ N(n_d * 1, diag(v))        =>        r_d ~ N(0, diag(v) + tau^2 * 1 1^T)

Integrating ``n_d`` out is closed-form (Sherman-Morrison), so there is no extra parameter to
fit and nothing to estimate from thin overlap:

    -2 log L_d = sum_j r_j^2/v_j  -  tau^2 (sum_j r_j/v_j)^2 / (1 + tau^2 sum_j 1/v_j)
                 + sum_j log v_j  +  log(1 + tau^2 sum_j 1/v_j)

The middle term is what makes this different from harmonisation: it *forgives* whatever common
offset a dataset has, in proportion to how well that offset is determined, without ever
committing to a value for it. A dataset with one point is forgiven almost nothing (its offset
is unidentifiable and stays in the residual); a dataset with forty points is forgiven almost
all of its mean offset and is left contributing only its shape. The model is then fitted to
the *shape* of each experiment and the *consensus* of their levels, which is what the model is
supposed to predict and what survives into the next decade.

``tau = 0`` reduces the expression exactly to the independent Gaussian NLL, so the whole path
is off by default and the shipped model is bit-identical with it off.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import torch
from torch import Tensor


@dataclass
class DatasetRows:
    """Per-dataset measurement rows, aligned to a :class:`StageCBundle`'s grid.

    One row is one (dataset, energy bin) measurement. ``ds_ix`` groups rows into datasets --
    an EXFOR dataset is a single experiment's single measurement campaign, which is the unit a
    normalisation error applies to. The bundle's ``target_log`` collapses all of this into one
    trust-weighted mean per (nuclide, bin); these arrays are what it was collapsed from.
    """

    nuc_ix: Tensor    # (M,) index into bundle.nuclides
    bin_ix: Tensor    # (M,) index into bundle.grid_ev
    y: Tensor         # (M,) log10 measured cross section, barns
    meas_var: Tensor  # (M,) quoted variance of that point, log10^2
    w: Tensor         # (M,) trust weight
    ds_ix: Tensor     # (M,) dataset group index, 0..n_datasets-1
    is_test: Tensor   # (M,) 1 where the row is post-cutoff (never trained on)
    n_datasets: int
    keys: list[str]

    _TENSORS = ("nuc_ix", "bin_ix", "y", "meas_var", "w", "ds_ix", "is_test")

    def to(self, device) -> DatasetRows:
        for name in self._TENSORS:
            t = getattr(self, name)
            if isinstance(t, Tensor) and t.device != torch.device(device):
                setattr(self, name, t.to(device))
        return self

    def __len__(self) -> int:
        return int(self.nuc_ix.shape[0])

    @property
    def device(self):
        return self.nuc_ix.device


def build_rows(records: list[dict], ids: list[str], n_energy: int) -> DatasetRows:
    """Assemble :class:`DatasetRows` from the flat records collected while building a bundle.

    Each record needs ``nuc_ix``, ``bin``, ``log10``, ``sigma_log10``, ``weight``,
    ``dataset_key`` and ``is_test``. Rows whose nuclide did not survive the bundle's own
    selection are dropped by the caller, which passes the surviving ``ids``.
    """
    if not records:
        empty_i = torch.zeros(0, dtype=torch.long)
        empty_f = torch.zeros(0, dtype=torch.float32)
        return DatasetRows(empty_i, empty_i, empty_f, empty_f, empty_f, empty_i, empty_f, 0, [])
    keys: dict[str, int] = {}
    nuc_ix, bin_ix, y, mv, w, ds_ix, te = [], [], [], [], [], [], []
    for r in records:
        k = str(r["dataset_key"])
        if k not in keys:
            keys[k] = len(keys)
        nuc_ix.append(int(r["nuc_ix"]))
        bin_ix.append(int(r["bin"]))
        y.append(float(r["log10"]))
        # A quoted uncertainty of zero or nothing is not a perfect measurement. 0.1 log10 (26%)
        # is the point-to-point half of the measured floor, which is the right thing to assume
        # about a point whose author did not say.
        s = float(r.get("sigma_log10") or 0.0)
        mv.append((s if np.isfinite(s) and s > 1e-3 else 0.1) ** 2)
        w.append(float(r.get("weight") or 1.0))
        ds_ix.append(keys[k])
        te.append(float(r.get("is_test") or 0.0))
    assert max(bin_ix) < n_energy and max(nuc_ix) < len(ids)
    L, F = torch.long, torch.float32
    return DatasetRows(
        nuc_ix=torch.tensor(nuc_ix, dtype=L), bin_ix=torch.tensor(bin_ix, dtype=L),
        y=torch.tensor(y, dtype=F), meas_var=torch.tensor(mv, dtype=F),
        w=torch.tensor(w, dtype=F), ds_ix=torch.tensor(ds_ix, dtype=L),
        is_test=torch.tensor(te, dtype=F), n_datasets=len(keys),
        keys=[k for k, _ in sorted(keys.items(), key=lambda kv: kv[1])],
    )


def _segment_sum(vals: Tensor, ix: Tensor, n: int) -> Tensor:
    out = torch.zeros(n, dtype=vals.dtype, device=vals.device)
    return out.index_add_(0, ix, vals)


def norm_latent_nll(pred_log: Tensor, log_var: Tensor, rows: DatasetRows, *,
                    tau: float = 0.079, row_mask: Tensor | None = None,
                    reduce: bool = True) -> Tensor | tuple[Tensor, Tensor]:
    """Negative log likelihood with each dataset's normalisation integrated out.

    ``pred_log`` and ``log_var`` are the model's (N, E) prediction and predicted log-variance;
    rows index into them. ``tau`` is the prior width of a dataset's normalisation in log10 --
    0.079 is the value ``docs/results/noise-floor.md`` measured, not a tuned one.

    Trust enters as a precision multiplier, i.e. the covariance of dataset ``d`` is
    ``diag(v/w) + tau^2 11^T``: a distrusted dataset is one whose points are noisier, so it
    pulls the fit less *and* its own normalisation is less determined, which is the behaviour
    WP-12's trust score is supposed to buy. The result is normalised by the total row weight,
    so the number is a per-row NLL on the same scale as
    :func:`models.losses.heteroscedastic_nll` and ``prior_weight`` / ``teacher_weight`` keep
    the meanings they were tuned with.

    ``tau = 0`` is the same likelihood without the latent -- the honest A/B for what
    marginalising buys, holding the per-dataset row representation fixed.

    Returns the scalar NLL, or ``(per_dataset_nll, per_dataset_weight)`` when ``reduce`` is
    False.
    """
    r = pred_log[rows.nuc_ix, rows.bin_ix] - rows.y
    v = (torch.exp(log_var[rows.nuc_ix, rows.bin_ix].clamp(-10.0, 10.0))
         + rows.meas_var).clamp_min(1e-8)
    w = rows.w if row_mask is None else rows.w * row_mask
    # A masked-out row must not contribute to its dataset's shared offset either, so the mask
    # is applied to the sufficient statistics rather than to the finished per-row terms. Zero
    # weight is exactly "this row is not in this likelihood" -- which is what makes the
    # hold-out honest: `row_mask` is gathered from the same training weights the rest of the
    # loss uses, so a nuclide zeroed out of a CV fold is zeroed out here too.
    w = w.clamp_min(0.0)
    keep = (w > 0).float()
    ve = (v / w.clamp_min(1e-12)) * keep + (1.0 - keep)   # masked rows get variance 1, weight 0
    p = keep / ve
    n = rows.n_datasets
    S_p = _segment_sum(p, rows.ds_ix, n)                  # sum 1/v_eff
    S_pr = _segment_sum(p * r, rows.ds_ix, n)             # sum r/v_eff
    S_prr = _segment_sum(p * r * r, rows.ds_ix, n)        # sum r^2/v_eff
    S_ld = _segment_sum(keep * torch.log(ve), rows.ds_ix, n)
    t2 = float(tau) ** 2
    denom = 1.0 + t2 * S_p
    quad = S_prr - t2 * S_pr.pow(2) / denom
    logdet = S_ld + torch.log(denom)
    nll = 0.5 * (quad + logdet)
    wd = _segment_sum(w, rows.ds_ix, n)
    if not reduce:
        return nll, wd
    return nll.sum() / wd.sum().clamp_min(1e-9)


def posterior_shift(pred_log: Tensor, log_var: Tensor, rows: DatasetRows, *,
                    tau: float = 0.079, row_mask: Tensor | None = None) -> Tensor:
    """Posterior mean of each dataset's normalisation latent, ``E[n_d | data]``.

    Never used in training -- marginalising means never committing to this number. It is the
    diagnostic that says whether the latent is doing anything: its spread should come out near
    the 0.079 log10 the noise floor measured, and if it comes out near zero the term is inert.
    It is also, exactly, the shift ``NORM_HARMONISE`` subtracts from the data, so comparing the
    two is comparing a point estimate against the distribution it came from.
    """
    r = pred_log[rows.nuc_ix, rows.bin_ix] - rows.y
    v = (torch.exp(log_var[rows.nuc_ix, rows.bin_ix].clamp(-10.0, 10.0))
         + rows.meas_var).clamp_min(1e-8)
    w = (rows.w if row_mask is None else rows.w * row_mask).clamp_min(0.0)
    keep = (w > 0).float()
    p = keep / ((v / w.clamp_min(1e-12)) * keep + (1.0 - keep))
    t2 = float(tau) ** 2
    S_p = _segment_sum(p, rows.ds_ix, rows.n_datasets)
    S_pr = _segment_sum(p * r, rows.ds_ix, rows.n_datasets)
    return t2 * S_pr / (1.0 + t2 * S_p)
