"""Stage C training: fit the spectral residual on curated capture measurements (WP-15 step 3).

The curriculum of blueprint §5.6 in the order the pieces exist: the chart encoder (WP-06) and
the Stage B parameter decoder (WP-14) stay frozen, Stage B's cross sections come in as a fixed
input, and only the residual r(E) is fitted -- first above the URR boundary where the physics is
smooth, then over the full grid. Checkpoints are selected on the **time split** (measurements
published after ``year_cutoff``), never on a random validation split, because a random split
leaks: the same measurement campaign appears on both sides of it (§5.6, §12).
"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import torch
from torch import Tensor

from models.losses import capture_loss
from models.macs_constraint import KADONIS_TSV, load_macs, macs_loss
from models.norm_latent import DatasetRows, norm_latent_nll
from models.residual.fno import SpectralResidual, density_prior_loss


@dataclass
class StageCBundle:
    """Everything Stage C trains on, aligned on one shared energy grid."""

    nuclides: list[str]
    grid_ev: np.ndarray
    stage_b_b: Tensor          # (N, E) Stage B cross sections, barns
    target_log: Tensor         # (N, E) log10 measured, 0 where unmeasured (see trust)
    trust: Tensor              # (N, E) Σ trust of the datasets in that bin, 0 = no measurement
    teacher_log: Tensor        # (N, E) evaluated-library log10 cross section
    embeddings: Tensor         # (N, D) frozen nuclide embeddings
    is_test: Tensor            # (N, E) 1 where the bin belongs to the time-split test set
    teacher_ok: Tensor | None = None      # (N,) 1 where the teacher library covers the nuclide
    rrr_upper_ev: Tensor | None = None    # (N,) resolved-resonance boundary per nuclide
    threshold_ev: Tensor | None = None    # (N,) (n,2n) threshold ~ Sn of the compound
    # (N,) first excited level of the TARGET in eV. When present it becomes a second auxiliary
    # per-energy channel beside the (n,2n) one, and `threshold` is (N, E, 2) instead of (N, E).
    inelastic_ev: Tensor | None = None
    # Show `rrr_upper_ev` to the model as a per-energy channel as well, not only as the
    # `above_rrr` mask. It is the one nuclide-specific energy landmark already in the bundle.
    aux_urr: bool = False
    # the cutoff this bundle was built with, so the MACS constraint can honour it: KADoNiS
    # v1.0 was published in 2014 and cannot be used by a run that splits earlier
    year_cutoff: int | None = None
    # Per-dataset measurement rows, i.e. what `target_log` was collapsed from. Needed only by
    # the C6 normalisation latent (models/norm_latent.py); None everywhere else, and every
    # existing call site builds a bundle without it.
    ds: DatasetRows | None = None
    # STACKREG: the curve Stage C READS, when it differs from the one it MULTIPLIES. None keeps
    # every earlier run: the residual reads and corrects `stage_b_b`. See `set_prior_input`.
    input_b: Tensor | None = None
    density: Tensor = field(init=False)   # (N, E) measured-data density in [0, 1]
    above_rrr: Tensor = field(init=False)  # (N, E) 1 where Stage C is allowed to speak

    def __post_init__(self) -> None:
        t = self.trust
        self.density = (t / t.max().clamp_min(1e-6)).clamp(0.0, 1.0)
        grid_t = torch.tensor(np.asarray(self.grid_ev, float), dtype=torch.float32)
        if self.threshold_ev is None:
            self.threshold = torch.zeros_like(self.trust)
        else:
            # signed decades above the threshold, clipped: the model needs to see the kink,
            # not a number that runs away far from it
            self.threshold = torch.log10(
                grid_t[None, :] / self.threshold_ev[:, None].clamp_min(1.0)).clamp(-2.0, 1.0)
        # Extra auxiliary channels, each the signed decades of every grid energy above one
        # per-nuclide reference energy. They are the only way a feature can reach the residual
        # as a function of energy: `lift_embed` is constant over the grid. A nuclide with no
        # reference gets a flat channel rather than a fake landmark at 1 eV, which would sit
        # several decades below anything that happens.
        def _decades(ref: Tensor, lo: float, hi: float) -> Tensor:
            d = torch.log10(grid_t[None, :] / ref[:, None].clamp_min(1.0)).clamp(lo, hi)
            return torch.where((ref > 0)[:, None], d, torch.zeros_like(d))

        aux = []
        if self.inelastic_ev is not None:
            aux.append(_decades(self.inelastic_ev, -2.0, 1.0))
        if self.aux_urr and self.rrr_upper_ev is not None:
            # Wider than the threshold channels: the residual only ever speaks above this
            # boundary, so the informative side is the positive one, out to the top of the grid.
            aux.append(_decades(self.rrr_upper_ev, -1.0, 3.0))
        if aux:
            self.threshold = torch.stack([self.threshold, *aux], dim=-1)
        if self.rrr_upper_ev is None:
            self.above_rrr = torch.ones_like(self.trust)
        else:
            grid = torch.tensor(np.asarray(self.grid_ev, float), dtype=torch.float32)
            # §5.4: below the resolved resonance boundary Stage B's resonance statistics stand;
            # the residual neither trains nor is scored there.
            self.above_rrr = (grid[None, :] > self.rrr_upper_ev[:, None]).float()

    # every tensor the bundle owns, including the three built in __post_init__
    _TENSORS = ("stage_b_b", "input_b", "target_log", "trust", "teacher_log", "teacher_ok",
                "embeddings", "is_test",
                "rrr_upper_ev", "threshold_ev", "inelastic_ev", "density", "above_rrr",
                "threshold")

    def to(self, device) -> StageCBundle:  # noqa: D402
        """Move every tensor to `device`, in place, and return self.

        train_stage_c has taken a `device` argument since it was written, and passing
        anything but "cpu" raised: the model moved and the bundle did not. Nobody ever
        called it, so nobody noticed, and every experiment in this repo's history has run on
        CPU on a machine with an idle GPU. Idempotent, so the usual pattern -- one bundle,
        many train calls -- pays the transfer once.
        """
        for name in self._TENSORS:
            t = getattr(self, name, None)
            if isinstance(t, Tensor) and t.device != torch.device(device):
                setattr(self, name, t.to(device))
        if self.ds is not None:
            self.ds.to(device)
        return self

    @property
    def device(self):
        return self.stage_b_b.device

    @property
    def model_input(self) -> Tensor:
        """The curve the residual is conditioned on: `input_b` if set, else Stage B itself."""
        return self.stage_b_b if self.input_b is None else self.input_b

    def set_prior_input(self, raw_b: Tensor, correction_channel: bool = True) -> StageCBundle:
        """STACKREG: condition the residual on the uncorrected curve, correct the corrected one.

        STAGECRECAL/OSENGINE: Stage C's only physics input was Stage B's curve, so a Stage B
        row carrying a validated physics correction and one that was merely wrong in the same
        place were indistinguishable to it, and out of sample it handed back 70-74 % of the
        Os-region optical-model fix. Here the residual reads `raw_b` -- Stage B before any
        regional correction (an engine table without the fix, or the surrogate without the
        library blend) -- and still multiplies `stage_b_b`, so the prediction is
        `stage_b_b * r(raw_b, ...)`. A correction then changes what r is fitted AGAINST on the
        rows that carry it, but no longer changes the features every other row is read with.
        With `correction_channel` the correction itself, log10(stage_b_b / raw_b), is appended
        as one more per-energy auxiliary channel: zero on an uncorrected row, so the residual
        can tell "Stage B was corrected here" from "Stage B is right here".
        """
        raw = raw_b.to(self.stage_b_b.device, torch.float32)
        if raw.shape != self.stage_b_b.shape:
            raise ValueError(f"raw curve {tuple(raw.shape)} vs Stage B {tuple(self.stage_b_b.shape)}")
        self.input_b = raw
        if correction_channel:
            d = (torch.log10(self.stage_b_b.clamp_min(1e-30))
                 - torch.log10(raw.clamp_min(1e-30))).clamp(-1.0, 1.0)
            th = self.threshold if self.threshold.dim() == 3 else self.threshold.unsqueeze(-1)
            self.threshold = torch.cat([th, d.to(th.device).unsqueeze(-1)], dim=-1)
        return self

    def correction_log(self) -> Tensor:
        """(N, E) log10(stage_b_b / input_b); zero everywhere when no raw curve is set."""
        if self.input_b is None:
            return torch.zeros_like(self.stage_b_b)
        return (torch.log10(self.stage_b_b.clamp_min(1e-30))
                - torch.log10(self.input_b.clamp_min(1e-30)))

    @property
    def n_energy(self) -> int:
        """Number of points on the shared energy grid."""
        return int(self.stage_b_b.shape[1])

    @property
    def embed_dim(self) -> int:
        """Width of the frozen nuclide embedding."""
        return int(self.embeddings.shape[1])


def _split_masks(b: StageCBundle, per_nuclide: bool = True) -> tuple[Tensor, Tensor]:
    """Training weights (pre-cutoff, measured) and test weights (post-cutoff, measured).

    With ``per_nuclide`` the training weights of each nuclide are normalised to sum to one.
    Without it a handful of heavily measured nuclides own the loss: in the curated capture
    set two actinides carry more bins than the whole Fe-Sn region, and the residual fits
    them at everyone else's expense.
    """
    measured = (b.trust > 0).float() * b.above_rrr
    train = b.trust * measured * (1.0 - b.is_test)
    test = b.trust * measured * b.is_test
    if per_nuclide:
        train = train / train.sum(dim=1, keepdim=True).clamp_min(1e-9)
    return train, test



def validation_masks(early: StageCBundle, late: StageCBundle) -> tuple[Tensor, Tensor, Tensor]:
    """Train / select / report weights from two bundles that differ only in year_cutoff.

    `late` is built at the reporting cutoff (2012) and `early` at an earlier one (2003), so
    the bins between the two cutoffs are exactly those `early` calls test and `late` calls
    train. Training on pre-2003, selecting the checkpoint on 2003-2012, and reporting on
    post-2012 keeps the reported split out of every decision -- which selecting on the test
    split does not, to the tune of 2.2%.
    """
    if early.is_test.shape != late.is_test.shape:
        raise ValueError(
            f"bundles disagree in shape: {early.is_test.shape} vs {late.is_test.shape}")
    measured = (late.trust > 0).float() * late.above_rrr
    window = early.is_test * (1.0 - late.is_test)          # published in [early, late)
    train = late.trust * measured * (1.0 - early.is_test)  # strictly before the early cutoff
    val = late.trust * measured * window
    test = late.trust * measured * late.is_test
    return train, val, test

def evaluate(model: SpectralResidual, b: StageCBundle, weights: Tensor) -> dict[str, float]:
    """Weighted RMS of log10 residuals and mean |log10| on the bins the weights select."""
    model.eval()
    with torch.no_grad():
        r, sigma_r = model(b.model_input, b.embeddings, b.threshold)
        pred_log = torch.log10((b.stage_b_b * r).clamp_min(1e-12))
        d2 = (pred_log - b.target_log).pow(2)
        # callers build masks from a bundle that may since have moved to the GPU
        w = weights.to(b.stage_b_b.device).clamp_min(0.0)
        tot = w.sum().clamp_min(1e-6)
        return {
            "rms_log10": float(torch.sqrt((w * d2).sum() / tot)),
            "median_abs_log10": float((pred_log - b.target_log).abs()[w > 0].median())
            if (w > 0).any() else float("nan"),
            "mean_sigma_rel": float((sigma_r / r.clamp_min(1e-12)).mean()),
            "n_bins": int((w > 0).sum()),
        }


def train_stage_c(
    bundle: StageCBundle,
    *,
    epochs: int = 200,
    lr: float = 3e-3,
    prior_weight: float = 5.0,   # chosen on a 2003-2012 validation window, never on the test split
    teacher_weight: float = 0.0,   # v0.1: no pull toward an evaluated library (opt in with a teacher_key and a weight)
    urr_first_epochs: int = 50,
    per_nuclide_weights: bool = False,   # measured 2026-09-09: normalising per nuclide made
                                         # every region worse (overall 0.117 -> 0.140)
    init_state: dict | None = None,      # warm start, e.g. from library pre-training
    # Default changed 2026-09-10. Keeping the best epoch on the reporting split flattered
    # every number in this repo by 2.2% overall and 5.0% on the actinides (20 seeds,
    # docs/results/power/selection-bias.json). Selecting on a 2003-2012 window instead is
    # honest but worse -- it costs 13% of the training bins to buy the signal, and loses
    # 4.8% overall, 15.8% on actinides (docs/results/power/selection-protocol.json). So take
    # the last epoch: honest, and the cheapest of the honest options.
    select_on_test: bool = False,
    val_weights: Tensor | None = None,   # honest checkpoint selection: see validation_masks
    train_weights: Tensor | None = None,  # override the split, e.g. to hold out the window
    seed: int = 0,
    # Capacity, fixed at the SpectralResidual defaults until 2026-09-10. The nuclide learning
    # curve turned over -- held-out error on a fixed core *rises* past ~100 training nuclides
    # -- which is what a capacity ceiling looks like, so these are now knobs the experiments
    # can turn instead of constants nobody could measure.
    width: int = 64,
    n_modes: int = 16,
    # KADoNiS MACS as an auxiliary constraint. Zero keeps the shipped behaviour. The table
    # has scored this project since WP-16 and never trained it, which is backwards for a
    # model whose measured failure is per-nuclide normalisation: a MACS is an integral of
    # the cross section, so it constrains magnitude and little else. See models/macs_constraint.
    macs_weight: float = 0.0,
    # (N,) 0/1 over b.nuclides: 0 drops that nuclide from the MACS constraint. None keeps all
    # of them, which is right for a full training run and wrong for a held-out fold.
    macs_mask=None,
    # STACKREG anchor: >0 adds anchor_weight * mean(log r^2) over the above-RRR bins of MEASURED
    # (trust > 0) nuclides whose Stage B carries a correction (|bundle.correction_log()| > 0.01),
    # i.e. a penalty for moving a physics-corrected region. Measured rows only, so a held-out
    # fold row (trust zeroed) is never regularised by it: in deployment a chart nuclide is not
    # in the training batch, and a penalty that only acted through held-out rows would be a
    # cross-validation artefact. 0 is every earlier run.
    anchor_weight: float = 0.0,
    # C6: width of the per-dataset normalisation latent, in log10. 0 keeps the shipped
    # likelihood (one trust-weighted mean per bin, independent per point). >0 switches the
    # data term to models.norm_latent, which reads the per-dataset rows the bundle carries
    # and integrates each dataset's normalisation out instead of fitting it. 0.079 is the
    # value docs/results/noise-floor.md measured for that shift; it is not a tuned knob.
    norm_sigma: float = 0.0,
    # The A/B control: the same per-dataset likelihood with the latent switched off. Setting
    # this reruns the data term over rows rather than bins at tau=0, which is what isolates
    # "marginalising helped" from "using rows instead of bin means helped".
    norm_rows_only: bool = False,
    # C7 (ROBUSTLIK): Student-t data likelihood, models/robust_lik.py. None keeps the shipped
    # Gaussian. A float is a fixed nu -- inf routes to the shipped function itself, so that arm
    # is bit-identical to None -- and "fit" makes nu a parameter of this member's training loss.
    # With student_t_rows the t is per EXFOR row (norm_latent's per-dataset rows) instead of per
    # trust-weighted cell; its nu = inf limit is the rows Gaussian, C6's arm B.
    student_t_nu: float | str | None = None,
    student_t_rows: bool = False,
    # Training recipe. The defaults reproduce the original exactly: plain Adam, constant
    # learning rate, final weights. Each of these is standard practice now and none of them
    # had ever been tried here, which is worth measuring rather than assuming.
    optimizer: str = "adam",        # "adamw" decouples weight decay from the gradient
    weight_decay: float = 0.0,
    lr_schedule: str = "constant",  # "cosine" with warmup
    warmup_frac: float = 0.05,
    ema_decay: float = 0.0,         # >0 keeps an exponential moving average of the weights
    swa_frac: float = 0.0,          # >0 averages weights over the last fraction of training
    # C9 self-distillation: soft targets on nuclides nobody has measured, from a teacher
    # ensemble's own prediction (scripts/selfdistill.py). A dict of stage_b_b, embeddings,
    # threshold, target_log and weight, (P, E) rows that are NOT in the bundle. They are run
    # through the model in a separate forward pass, so every existing term -- the likelihood,
    # the density prior's mean over rows, the MACS constraint -- is computed on exactly the
    # rows it always was, and None is byte-identical to the shipped recipe. The term is an
    # MSE on the mean prediction in log10 with a fixed label width `pseudo_sigma`; it does not
    # touch the sigma head, and like the MACS term it only speaks after the warm-up.
    pseudo: dict | None = None,
    pseudo_weight: float = 0.0,
    pseudo_sigma: float = 0.20,
    device: str = "cpu",
) -> tuple[SpectralResidual, dict]:
    """Fit the residual, selecting the checkpoint on the time-split test set."""
    torch.manual_seed(seed)
    b = bundle.to(device)
    # WP-19 threshold-grid hook: INCOGNITA_THRESHOLD_GRID unset/off returns SpectralResidual itself
    from models.threshold_grid import residual_class
    model = residual_class()(n_energy=b.n_energy, embed_dim=b.embed_dim,
                             width=width, n_modes=n_modes,
                             n_aux=b.threshold.shape[-1] if b.threshold.dim() == 3 else 1,
                             ).to(device)
    if init_state is not None:
        model.load_state_dict(init_state)
    fitted_nu = None
    params = list(model.parameters())
    if student_t_nu == "fit":
        from models.robust_lik import FittedNu
        fitted_nu = FittedNu().to(device)
        params = params + list(fitted_nu.parameters())
    if optimizer == "adamw":
        opt = torch.optim.AdamW(params, lr=lr, weight_decay=weight_decay)
    else:
        opt = torch.optim.Adam(params, lr=lr, weight_decay=weight_decay)
    sched = None
    if lr_schedule == "cosine":
        warm = max(1, int(warmup_frac * epochs))

        def _lr(e: int) -> float:
            if e < warm:
                return (e + 1) / warm
            t = (e - warm) / max(1, epochs - warm)
            return 0.5 * (1.0 + math.cos(math.pi * min(t, 1.0)))

        sched = torch.optim.lr_scheduler.LambdaLR(opt, _lr)
    # A running average of the weights generalises better than the last point on the
    # trajectory, and costs one extra copy of a 300k-parameter model.
    avg_state = None
    avg_n = 0
    swa_start = int((1.0 - swa_frac) * epochs) if swa_frac > 0 else epochs + 1
    w_train, w_test = _split_masks(b, per_nuclide=per_nuclide_weights)
    if train_weights is not None:
        w_train = train_weights.to(device)
    if val_weights is not None:
        val_weights = val_weights.to(device)
    # The teacher pull applies where there is NO measurement, so a nuclide the teacher library
    # does not cover would be pulled toward its all-zero row -- log10 sigma = 0, i.e. 1 barn,
    # everywhere it is quiet. ENDF/B-VII.1 covers 200 of 225 nuclides where TENDL-2025 covers
    # 224, so switching teachers without this mask silently poisons 25 nuclides. Marking them
    # "measured" disables only the teacher term; the likelihood uses `trust` and is untouched.
    has_meas = (b.trust > 0).float()
    if b.teacher_ok is not None:
        has_meas = torch.maximum(has_meas, (1.0 - b.teacher_ok).reshape(-1, 1).expand_as(has_meas))
    # phase 1 fits only the smooth part of the grid: the top half in energy (§5.4 keeps the
    # resonance region out of the residual entirely).
    smooth = torch.zeros_like(w_train)
    smooth[:, b.n_energy // 2:] = 1.0

    macs_b = macs_w = macs_kt = mass_a = None
    if macs_weight > 0:
        from models.stage_c_data import _data

        macs_b, macs_w, macs_kt = load_macs(list(b.nuclides), _data(KADONIS_TSV),
                                            year_cutoff=getattr(b, 'year_cutoff', None))
        # Which nuclides the MACS constraint is allowed to see. It has to be passed in rather
        # than inferred from trust, because zero trust means two different things: a nuclide
        # deliberately held out of a fold, and a nuclide whose only capture datum IS a MACS.
        # Inferring it silenced the second along with the first.
        #
        # Why it matters that the first is silenced: scripts/holdout_calibration.py holds a
        # fold out by zeroing trust and states the contract as "a nuclide with none contributes
        # to neither loss". load_macs keys on b.nuclides alone, so every held-out nuclide kept
        # full KADoNiS weight -- 191 of the 198 leave-neighbourhood-out nuclides carry a MACS,
        # and a MACS is an integral of the capture cross section over exactly the keV decade the
        # fold is scored in. Masked, the held-out RMS goes 0.1510 -> 0.2035, almost all of it
        # per-nuclide bias. Every CV number reported before 2026-09-12 was trained with it.
        if macs_mask is not None:
            macs_w = macs_w * torch.as_tensor(
                macs_mask, dtype=torch.float32).reshape(-1, 1).cpu()
        mass_a = torch.tensor([float(int(n[1:4]) + int(n[5:8])) for n in b.nuclides],
                              dtype=torch.float32)
        macs_b, macs_w = macs_b.to(device), macs_w.to(device)
        macs_kt, mass_a = macs_kt.to(device), mass_a.to(device)
        # the bundle keeps the energy grid as numpy; the constraint integrates in torch
        macs_grid = torch.tensor(np.asarray(b.grid_ev), dtype=torch.float32, device=device)

    anchor_m = None
    if anchor_weight > 0:
        measured_nuc = ((b.trust > 0).any(dim=1, keepdim=True)).float()
        anchor_m = ((b.correction_log().abs() > 0.01).float() * b.above_rrr * measured_nuc)
        print(f"[stage-c] STACKREG anchor on {int((anchor_m.sum(1) > 0).sum())} corrected, "
              f"measured nuclides ({int(anchor_m.sum())} bins) at weight {anchor_weight}",
              flush=True)

    t_nu = None
    if student_t_nu is not None and student_t_nu != "fit":
        t_nu = float(student_t_nu)
    t_active = fitted_nu is not None or (t_nu is not None and (student_t_rows
                                                                or not math.isinf(t_nu)))
    if student_t_rows and student_t_nu is None:
        raise ValueError("student_t_rows needs student_t_nu (inf for the rows Gaussian)")
    use_rows = bool(norm_sigma > 0 or norm_rows_only or student_t_rows)
    if use_rows and (b.ds is None or len(b.ds) == 0):
        raise ValueError(
            "norm_sigma/norm_rows_only need the bundle's per-dataset rows, and this bundle "
            "has none. build_bundle attaches them; build_library_bundle does not, because a "
            "library curve is not a measurement and has no normalisation to marginalise.")
    if use_rows:
        print(f"[stage-c] likelihood over {len(b.ds)} per-dataset rows in "
              f"{b.ds.n_datasets} datasets, normalisation latent tau="
              f"{0.0 if norm_rows_only else float(norm_sigma):.3f} log10", flush=True)

    use_pseudo = pseudo is not None and pseudo_weight > 0
    if use_pseudo:
        pseudo = {k: (v.to(device) if isinstance(v, Tensor) else v) for k, v in pseudo.items()}
        pseudo_norm = pseudo["weight"].sum().clamp_min(1e-9)

    history: list[dict] = []
    best = {"epoch": -1, "rms_log10": float("inf")}
    best_state = {k: v.detach().clone() for k, v in model.state_dict().items()}

    for epoch in range(epochs):
        model.train()
        opt.zero_grad()
        r, sigma_r = model(b.model_input, b.embeddings, b.threshold)
        pred_log = torch.log10((b.stage_b_b * r).clamp_min(1e-12))
        log_var = 2.0 * torch.log((sigma_r / r.clamp_min(1e-12)).clamp_min(1e-6))
        weights = w_train * (smooth if epoch < urr_first_epochs else 1.0)
        parts = capture_loss(pred_log, b.target_log, log_var, weights,
                             b.teacher_log, has_meas, teacher_weight=teacher_weight)
        if t_active:
            from models.robust_lik import student_t_nll, student_t_rows_nll
            nu_now = fitted_nu() if fitted_nu is not None else t_nu
            if student_t_rows:
                row_w = weights[b.ds.nuc_ix, b.ds.bin_ix]
                nll = student_t_rows_nll(pred_log, log_var, b.ds, nu_now,
                                         row_mask=(row_w > 0).float())
            else:
                nll = student_t_nll(pred_log, b.target_log, log_var, weights, nu_now)
            parts = {"nll": nll, "teacher": parts["teacher"],
                     "total": nll + teacher_weight * parts["teacher"]}
        elif use_rows:
            # Gathering the row mask from `weights` rather than recomputing it is what keeps
            # the hold-out honest: every mask the rest of the loss honours -- the time split,
            # the resonance bound, the warm-up's smooth half, and a CV fold's zeroed trust --
            # is already multiplied into `weights`, so a row whose bin is excluded there is
            # excluded here. models/norm_latent.py's docstring has the rest.
            row_w = weights[b.ds.nuc_ix, b.ds.bin_ix]
            nll = norm_latent_nll(pred_log, log_var, b.ds,
                                  tau=(0.0 if norm_rows_only else float(norm_sigma)),
                                  row_mask=(row_w > 0).float())
            parts = {"nll": nll, "teacher": parts["teacher"],
                     "total": nll + teacher_weight * parts["teacher"]}
        loss = parts["total"] + density_prior_loss(torch.log(r.clamp_min(1e-12)),
                                                   b.density, weight=prior_weight)
        if anchor_m is not None and float(anchor_m.sum()) > 0:
            loss = loss + anchor_weight * (anchor_m * torch.log(r.clamp_min(1e-12)).pow(2)
                                           ).sum() / anchor_m.sum()
        if macs_weight > 0 and epoch >= urr_first_epochs:
            # after warm-up only: the Maxwellian's weight sits above the resolved region, and
            # phase 1 is deliberately fitting the smooth half of the grid
            loss = loss + macs_weight * macs_loss(b.stage_b_b * r, macs_grid,
                                                  macs_b, macs_w, macs_kt, mass_a)
        if use_pseudo and epoch >= urr_first_epochs:
            r_p, _s_p = model(pseudo["stage_b_b"], pseudo["embeddings"], pseudo["threshold"])
            pred_p = torch.log10((pseudo["stage_b_b"] * r_p).clamp_min(1e-12))
            d2_p = (pred_p - pseudo["target_log"]).pow(2)
            loss = loss + pseudo_weight * 0.5 * (pseudo["weight"] * d2_p).sum() / (
                pseudo_norm * pseudo_sigma ** 2)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 5.0)
        opt.step()
        if sched is not None:
            sched.step()
        if ema_decay > 0:
            with torch.no_grad():
                sd = model.state_dict()
                if avg_state is None:
                    avg_state = {k: v.detach().clone().float() for k, v in sd.items()}
                else:
                    for k, v in sd.items():
                        avg_state[k].mul_(ema_decay).add_(v.detach().float(), alpha=1 - ema_decay)
        elif epoch >= swa_start:
            with torch.no_grad():
                sd = model.state_dict()
                if avg_state is None:
                    avg_state = {k: v.detach().clone().float() for k, v in sd.items()}
                    avg_n = 1
                else:
                    avg_n += 1
                    for k, v in sd.items():
                        avg_state[k].add_((v.detach().float() - avg_state[k]) / avg_n)

        if epoch % 5 == 0 or epoch == epochs - 1:
            m = evaluate(model, b, w_test)
            # The checkpoint is chosen by a minimum over ~110 evaluations. Taking that
            # minimum on w_test -- the split every reported number lives on -- flatters the
            # reported accuracy by 2.2% overall and 5.0% on the actinides (measured over 20
            # seeds, docs/results/power/selection-bias.json). Prefer an earlier time window.
            score = (evaluate(model, b, val_weights)["rms_log10"]
                     if val_weights is not None else m["rms_log10"])
            history.append({"epoch": epoch, "loss": float(loss), "phase":
                            "urr" if epoch < urr_first_epochs else "full",
                            "select_score": score, **m})
            if val_weights is None and not select_on_test:
                best, best_state = {"epoch": epoch, **m}, {
                    k: v.detach().clone() for k, v in model.state_dict().items()}
            elif epoch >= urr_first_epochs and score < best.get("select_score", float("inf")):
                best = {"epoch": epoch, "select_score": score, **m}
                best_state = {k: v.detach().clone() for k, v in model.state_dict().items()}

    if avg_state is not None:
        # the averaged trajectory replaces the selected point: with EMA or SWA on, the
        # checkpoint the loop was tracking is no longer the model we want
        model.load_state_dict({k: v.to(model.state_dict()[k].dtype) for k, v in avg_state.items()})
    else:
        model.load_state_dict(best_state)
    if fitted_nu is not None:
        best["nu"] = float(fitted_nu().detach())
    return model, {"best": best, "history": history,
                   "train_bins": int((w_train > 0).sum()), "test_bins": int((w_test > 0).sum())}


def finetune_row(parent: SpectralResidual, b: StageCBundle, w_opt: Tensor, w_es: Tensor,
                 *, steps: int = 60, lr: float = 3e-4, l2: float = 1e-3,
                 patience: int = 12) -> SpectralResidual:
    """A copy of `parent` nudged toward the bins `w_opt` selects, anchored to where it began.

    The guards are the method. On ~20 training bins a 300k-parameter model can fit anything,
    so it starts at the converged global weights, pays L2 for every step away from them, and
    stops on a slice held out of the same nuclide's training bins -- never the reporting
    split. Measured over four seeds at five members: +1.77% overall, +3.19% on odd-A.
    """
    import copy

    m = copy.deepcopy(parent)
    anchor = [q.detach().clone() for q in m.parameters()]
    opt = torch.optim.Adam(m.parameters(), lr=lr)
    best, best_state, bad = float("inf"), copy.deepcopy(m.state_dict()), 0
    for _ in range(steps):
        m.train()
        opt.zero_grad()
        r, _s = m(b.model_input, b.embeddings, b.threshold)
        pred = torch.log10((b.stage_b_b * r).clamp_min(1e-12))
        loss = (w_opt * (pred - b.target_log) ** 2).sum() / w_opt.sum().clamp_min(1e-9)
        loss = loss + l2 * sum(((q - a) ** 2).sum()
                               for q, a in zip(m.parameters(), anchor, strict=True))
        loss.backward()
        opt.step()
        with torch.no_grad():
            m.eval()
            r, _s = m(b.model_input, b.embeddings, b.threshold)
            pred = torch.log10((b.stage_b_b * r).clamp_min(1e-12))
            es = float(((w_es * (pred - b.target_log) ** 2).sum()
                        / w_es.sum().clamp_min(1e-9)).sqrt())
        if es < best - 1e-6:
            best, best_state, bad = es, copy.deepcopy(m.state_dict()), 0
        else:
            bad += 1
            if bad >= patience:
                break
    m.load_state_dict(best_state)
    return m


def predict_ensemble_per_nuclide(models: list[SpectralResidual], bundle: StageCBundle,
                                 *, min_bins: int = 6, hold_frac: float = 0.25,
                                 guard: str = "none",
                                 seed: int = 20260910, log=print, **ft) -> dict[str, Tensor]:
    """predict_ensemble, but each eligible nuclide is predicted by its own fine-tuned copies.

    169 nuclides x 5 members is 845 models and about 60 GB if they are kept, so each row is
    fine-tuned, used, and discarded. Nuclides below `min_bins` keep the global prediction
    unchanged, which is most of what makes this safe: the thin ones cannot be fitted and are
    not asked to be.

    `guard="holdout"` adds the check that was missing. Measured 2026-09-10 through the WP-16
    gate, the unguarded pass is +1.77% overall and +3.19% on odd-A while turning actinide
    retrodiction from 0.078 to 0.128 -- two winning cells into losses. The bins held out for
    early stopping are already not optimised against, so they can also answer whether the
    fine-tune beat the global model for this nuclide; where it does not, keep the global one.
    Per nuclide, on data the fine-tune never fitted, and never on the time-split test set.
    """
    base = predict_ensemble(models, bundle)
    w_train, _ = _split_masks(bundle, per_nuclide=False)
    wtr = w_train.clamp_min(0.0)
    gen = torch.Generator(device="cpu").manual_seed(seed)
    hold = (torch.rand(wtr.shape, generator=gen).to(wtr.device) < hold_frac) & (wtr > 0)
    n_tr = (wtr > 0).sum(dim=1)
    rows = [i for i in range(len(bundle.nuclides)) if int(n_tr[i]) >= min_bins]
    log(f"[stage-c] per-nuclide: {len(rows)} of {len(bundle.nuclides)} nuclides eligible "
        f"(>= {min_bins} training bins)")

    out = {k: v.clone() for k, v in base.items()}
    n_rejected = 0
    for n, i in enumerate(rows):
        sel = torch.zeros_like(wtr)
        sel[i] = 1.0
        w_opt, w_es = wtr * sel * (~hold).float(), wtr * sel * hold.float()
        if float(w_opt.sum()) <= 0 or float(w_es.sum()) <= 0:
            continue
        preds, alea = [], []
        for parent in models:
            fm = finetune_row(parent, bundle, w_opt, w_es, **ft)
            fm.eval()
            with torch.no_grad():
                r, sigma_r = fm(bundle.model_input, bundle.embeddings, bundle.threshold)
            preds.append(bundle.stage_b_b[i] * r[i])
            alea.append(bundle.stage_b_b[i] * sigma_r[i])
            del fm
        p = torch.stack(preds)
        if guard == "holdout":
            m = w_es[i] > 0
            if bool(m.any()):
                tl, wt = bundle.target_log[i][m], w_es[i][m]
                # m/tl/wt bound as defaults: _err is called inside this same iteration, so
                # this is behaviour-identical, and it keeps B023 meaningful for the case where
                # a closure really does outlive its loop.
                def _err(sig, m=m, tl=tl, wt=wt):
                    lg = torch.log10(sig[m].clamp_min(1e-30))
                    return float(((lg - tl) ** 2 * wt).sum() / wt.sum())
                if _err(p.mean(0)) >= _err(base["sigma_b"][i]):
                    n_rejected += 1
                    continue          # the fine-tune did not earn the row; keep the global
        out["sigma_b"][i] = p.mean(0)
        out["aleatoric_b"][i] = torch.stack(alea).pow(2).mean(0).sqrt()
        if "epistemic_b" in out:
            out["epistemic_b"][i] = p.std(0) if len(models) > 1 else torch.zeros_like(p[0])
        if (n + 1) % 40 == 0:
            log(f"[stage-c] per-nuclide {n + 1}/{len(rows)}")
    if guard == "holdout":
        log(f"[stage-c] per-nuclide guard: {n_rejected} of {len(rows)} fine-tunes rejected "
            f"on held-out bins; those nuclides keep the global prediction")
    return out


def train_ensemble(bundle: StageCBundle, members: int = 5, seed_offset: int = 0,
                   **kw) -> tuple[list[SpectralResidual], dict]:
    """Train a deep ensemble one member at a time (8 GB of VRAM cannot hold five at once).

    ``seed_offset`` shifts every member's seed, so a second ensemble of the same recipe is an
    independent replicate (EXACTFIT's seed axis); 0 reproduces every earlier run."""
    models, reports = [], []
    for i in range(members):
        m, rep = train_stage_c(bundle, seed=seed_offset + i, **kw)
        models.append(m)
        reports.append(rep["best"])
    return models, {"members": reports}


def predict_ensemble(models: list[SpectralResidual], bundle: StageCBundle) -> dict[str, Tensor]:
    """Ensemble prediction with aleatoric and epistemic parts kept separate (§5.5)."""
    preds, alea = [], []
    for m in models:
        m.eval()
        with torch.no_grad():
            r, sigma_r = m(bundle.model_input, bundle.embeddings, bundle.threshold)
        preds.append(bundle.stage_b_b * r)
        alea.append(bundle.stage_b_b * sigma_r)
    p = torch.stack(preds)
    return {
        "sigma_b": p.mean(0),
        "aleatoric_b": torch.stack(alea).pow(2).mean(0).sqrt(),
        "epistemic_b": p.std(0, unbiased=False),
    }


def input_fingerprint(bundle: StageCBundle) -> dict:
    """A hash of the three tensors the residual actually consumes, plus the nuclide list.

    The checkpoint directory has always recorded the training CONFIG and never the inputs. On
    2026-09-11 the (n,2n) threshold channel was corrected (9a48031) four hours after
    capture_2026 was trained, and every chart built afterwards fed the old model the new
    threshold -- 0.1087 becoming 0.1708 on the 225 nuclides we know best, silently, because
    nothing compares what a checkpoint was trained on with what it is being given. The
    embedding-basis check nearby verifies the basis against itself and cannot see this.

    Hashing the tensors rather than the source catches the case the source hash would miss: a
    data file changing under unchanged code.
    """
    import hashlib

    h = hashlib.blake2b(digest_size=16)
    for name in ("stage_b_b", "embeddings", "threshold"):
        t = getattr(bundle, name)
        h.update(name.encode())
        h.update(np.ascontiguousarray(t.detach().cpu().numpy(), dtype=np.float32).tobytes())
    h.update("|".join(bundle.nuclides).encode())
    return {"digest": h.hexdigest(), "nuclides": len(bundle.nuclides),
            "n_energy": int(bundle.n_energy), "embed_dim": int(bundle.embed_dim)}


def check_fingerprint(saved: dict | None, bundle: StageCBundle, log=print) -> bool:
    """True when the bundle matches what the checkpoint was trained on. Loud when it does not."""
    if not saved or not saved.get("digest"):
        log("[stage-c] this checkpoint predates input fingerprinting; it cannot be checked "
            "against the bundle it is being given. Retrain to get the check.")
        return False
    now = input_fingerprint(bundle)
    if now["digest"] == saved["digest"]:
        return True
    log(f"[stage-c] INPUT SKEW: this checkpoint was trained on inputs whose digest is "
        f"{saved['digest']}, and it is being given {now['digest']}. The residual is being "
        f"evaluated on tensors it never saw -- retrain before trusting anything downstream.")
    return False


def save_report(report: dict, path: Path) -> None:
    """Write the training report as JSON next to the checkpoint."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=1))
