"""UQ1: Total Monte Carlo priors, the sampler, and the hooks that put one sample on a whole run.

Task: UQ1 (plan WP-20 item 5, blueprint §5.5). Pre-registration: docs/results/uq1-tmc-prior.md.
Test: tests/hf/test_tmc.py.

No physics of its own. A TMC sample is a set of TALYS keyword values; this module draws them and
makes the port read them the way TALYS reads an input file: every `Params` the run builds
(`input.defaults.TMC_OVERRIDES`) and every photon-strength parameter set
(`gamma.parameters.TMC_GAMMA`) sees the sample. Both hooks are process-wide, so a sample must be
installed in a process whose caches hold nothing built without it: `scripts/uq1_tmc.py` forks a
child per sample from a worker that has only run a nuclide far from every target it serves.

**Priors: TASMAN's defaults.** Widths and distribution shapes are TASMAN's (A.J. Koning,
github.com/arjankoning1/tasman, commit 31144f44, `source/input4.f90` and `parvariation.f90`),
the code TENDL's Total Monte Carlo uses, at its default `cwidth 1`:

* a Gaussian deviate RR (`flaggauss` default y), here truncated at |RR| <= 3;
* `factor` parameters: x = 1 + RR delta for RR >= 0 and 1 / (1 + |RR| delta) for RR < 0;
  `shift` parameters: x = default + RR delta;
* delta = delta0 * Gunc, Gunc = `dripvar` (1 inside TASMAN's stable-isotope range of the
  element, rising to 3 away from it), per nucleus for `Z A` keywords and of the target
  otherwise; optical-model widths doubled for protons and alphas (class 7).

**Designs.** CPU sweep: blocks of 64 decorrelated Latin-hypercube points (`uniforms`), block b
seeded `SEED + b`. GPU capture sweep: a 3-d scrambled Sobol sequence (`sobol_uniforms`).

**Which nuclei.** Level-density keywords are drawn per nucleus for the 12 nuclei nearest the
compound nucleus (zix 0..2, nix 0..3: the compound nucleus, the target, every first-chance
residual and the (n,2n) residual), and once for all the others together. Photon strength is
varied for the compound nucleus only (as `capture_gpu`'s theta and SPEED0's G0.3). Optical
model keywords are per particle (n, p, alpha), for every nucleus, as TALYS's `v1adjust n 1.02`.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

SEED = 20260914
ZIX_MAX, NIX_MAX = 2, 3  # the per-nucleus level-density box (relative to the compound nucleus)

# TASMAN constants.f90: lightest and heaviest stable isotope per element, Z = 1..124
LIGHT = (
    1, 3, 6, 9, 10, 12, 14, 16, 19, 20, 23, 24, 27, 28,
    31, 32, 35, 36, 39, 40, 45, 46, 50, 50, 55, 54, 59, 58,
    63, 64, 69, 70, 75, 74, 79, 78, 85, 84, 89, 90, 93, 92,
    99, 96, 103, 102, 107, 106, 113, 112, 121, 120, 127, 124, 133, 130,
    138, 136, 141, 142, 139, 144, 151, 152, 159, 156, 165, 162, 169, 168,
    175, 174, 180, 180, 185, 184, 191, 190, 197, 196, 203, 204, 209, 206,
    203, 211, 212, 223, 225, 228, 229, 232, 235, 236, 239, 240, 242, 245,
    248, 252, 255, 257, 259, 261, 263, 265, 267, 269, 271, 270, 253, 254,
    256, 274, 276, 278, 280, 282, 284, 286, 287, 288, 289, 290,
)  # fmt: skip
HEAVY = (
    2, 4, 7, 9, 11, 13, 15, 18, 19, 22, 23, 26, 27, 30,
    31, 36, 37, 40, 41, 48, 45, 50, 51, 54, 55, 58, 59, 64,
    65, 70, 71, 76, 75, 82, 81, 86, 87, 88, 89, 96, 93, 100,
    99, 104, 103, 110, 109, 116, 115, 124, 123, 130, 127, 136, 133, 138,
    139, 142, 141, 150, 139, 154, 153, 160, 159, 164, 165, 170, 169, 176,
    176, 180, 181, 186, 187, 192, 193, 198, 197, 204, 205, 208, 209, 210,
    210, 213, 214, 225, 227, 233, 233, 238, 238, 242, 244, 250, 250, 253,
    256, 258, 261, 263, 265, 267, 269, 271, 273, 275, 277, 276, 381, 382,
    383, 384, 385, 386, 387, 388, 409, 410, 411, 412, 413, 414,
)  # fmt: skip


def dripvar(Z: int, A: int) -> float:
    """TASMAN dripvar.f90: the width multiplier away from the element's stable isotopes."""
    lo, hi = LIGHT[Z - 1], HEAVY[Z - 1]
    if hi - lo < 6:  # distcon = 3
        mid = (lo + hi) // 2
        lo, hi = mid - 2, mid + 3
    if lo <= A <= hi:
        return 1.0
    d, b = (float(A - hi), 5.0) if A > hi else (float(lo - A), 10.0)
    return 1.0 + 2.0 * d * d / (d * d + b * b)


@dataclass(frozen=True)
class Slot:
    """One dimension of the design."""

    name: str  # e.g. "aadjust@0,1", "v1adjust:n", "ftable"
    keyword: str
    family: str  # "psf", "omp", "ld"
    kind: str  # "factor" or "shift"
    delta0: float
    where: object = None  # (zix, nix), "rest", a particle symbol, or None


def slots() -> list[Slot]:
    """The design's dimensions, in a fixed order (the order of `p.*` columns and of the LHS)."""
    out = [
        # photon strength of the compound nucleus: TASMAN ftable 0.50, wtable 0.30, sgradjust 0.20
        Slot("ftable", "ftable", "psf", "factor", 0.50),
        Slot("wtable", "wtable", "psf", "factor", 0.30),
        Slot("sgr_m1", "sgr_m1", "psf", "factor", 0.20),
    ]
    omp = (("v1adjust", 0.02), ("w1adjust", 0.10), ("d1adjust", 0.10), ("rvadjust", 0.02),
           ("avadjust", 0.02))
    out += [Slot(f"{k}:n", k, "omp", "factor", d, "n") for k, d in omp]
    out.append(Slot("rspincut", "rspincut", "ld", "factor", 0.30))
    box = [(z, n) for z in range(ZIX_MAX + 1) for n in range(NIX_MAX + 1)]
    for zn in box:
        out.append(Slot(f"aadjust@{zn[0]},{zn[1]}", "aadjust", "ld", "factor", None, zn))
        out.append(Slot(f"pshift@{zn[0]},{zn[1]}", "pshiftadjust", "ld", "shift", 1.0, zn))
    out.append(Slot("aadjust@rest", "aadjust", "ld", "factor", None, "rest"))
    out.append(Slot("pshift@rest", "pshiftadjust", "ld", "shift", 1.0, "rest"))
    out += [Slot(f"{k}:{p}", k, "omp", "factor", d * 2.0, p) for p in ("p", "a") for k, d in omp]
    return out


def delta_of(s: Slot, Z: int, A: int) -> float:
    """TASMAN's width for slot `s` on the run of target (Z, A)."""
    Zc, Nc = Z, A + 1 - Z
    if s.keyword == "aadjust":
        d0 = 0.1125 - 3.125e-4 * A  # input4.f90: `Atarget`
    else:
        d0 = float(s.delta0)
    if isinstance(s.where, tuple):
        zn, nn = Zc - s.where[0], Nc - s.where[1]
        g = dripvar(zn, zn + nn) if zn >= 1 else dripvar(Z, A)
    else:
        g = dripvar(Z, A)
    return d0 * min(g, 3.0)


BLOCK = 64


def _decorrelated_lhs(dim: int, seed: int) -> np.ndarray:
    """One block of BLOCK Latin-hypercube points in [0, 1)^dim with near-zero rank correlation
    between every pair of columns (max |rho| ~ 0.04 at dim 45, against ~0.4 for a random LHS and
    0.77 for the first 64 Sobol points): Iman-Conover on van der Waerden scores, then greedy
    within-column swaps that lower the worst column's summed squared correlation."""
    from scipy.stats import norm

    n = BLOCK
    rng = np.random.default_rng(seed)
    u = (np.column_stack([rng.permutation(n) for _ in range(dim)]) + rng.random((n, dim))) / n
    sc = norm.ppf(np.arange(1, n + 1) / (n + 1))
    S = np.column_stack([rng.permutation(sc) for _ in range(dim)])
    for _ in range(3):
        Q, _r = np.linalg.qr(S - S.mean(0))
        R = Q.argsort(0).argsort(0)
        S = sc[R]
    X = (R - (n - 1) / 2) / np.sqrt((n * n - 1) / 12)
    C = X.T @ X / n
    eye = np.eye(dim)
    for _ in range(20000):
        j = int(np.abs(C - eye).max(axis=0).argmax())
        a, b = rng.choice(n, 2, replace=False)
        new = X[:, j].copy()
        new[[a, b]] = new[[b, a]]
        cj = X.T @ new / n
        cj[j] = 1.0
        if (cj**2).sum() < (C[:, j] ** 2).sum() - 1e-15:
            X[:, j] = new
            C[:, j] = cj
            C[j, :] = cj
    R = np.rint(X * np.sqrt((n * n - 1) / 12) + (n - 1) / 2).astype(int)
    return np.take_along_axis(np.sort(u, 0), R, 0)


def uniforms(n_lo: int, n_hi: int, dim: int, seed: int = SEED) -> np.ndarray:
    """Rows `n_lo:n_hi` of the CPU design: blocks of BLOCK decorrelated LHS points, block b drawn
    with seed `seed + b`. Growing N by whole blocks adds samples without moving earlier ones."""
    b0, b1 = n_lo // BLOCK, (n_hi - 1) // BLOCK
    u = np.concatenate([_decorrelated_lhs(dim, seed + b) for b in range(b0, b1 + 1)])
    return u[n_lo - b0 * BLOCK:n_hi - b0 * BLOCK]


def sobol_uniforms(n_lo: int, n_hi: int, dim: int, seed: int) -> np.ndarray:
    """Rows `n_lo:n_hi` of a scrambled Sobol sequence (the 3-d GPU design; extensible)."""
    import warnings

    from scipy.stats import qmc

    eng = qmc.Sobol(d=dim, scramble=True, seed=seed)
    if n_lo:
        eng.fast_forward(n_lo)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return eng.random(n_hi - n_lo)


def deviates(u: np.ndarray) -> np.ndarray:
    """Gaussian deviates at `u`, truncated at |RR| <= 3."""
    from scipy.stats import norm

    return np.clip(norm.ppf(u), -3.0, 3.0)


def transform(rr: float, kind: str, delta: float) -> float:
    """TASMAN parvariation.f90 around the default (1 for a factor, 0 for an added shift)."""
    if kind == "factor":
        return 1.0 + rr * delta if rr >= 0.0 else 1.0 / (1.0 + abs(rr) * delta)
    return rr * delta


def sample_values(Z: int, A: int, n_lo: int, n_hi: int, seed: int = SEED) -> list[dict]:
    """`{slot name: value}` for samples n_lo..n_hi-1 of target (Z, A)."""
    ss = slots()
    rr = deviates(uniforms(n_lo, n_hi, len(ss), seed))
    deltas = [delta_of(s, Z, A) for s in ss]
    return [{s.name: transform(float(r[j]), s.kind, deltas[j]) for j, s in enumerate(ss)}
            for r in rr]


def default_values() -> dict:
    return {s.name: (1.0 if s.kind == "factor" else 0.0) for s in slots()}


# ------------------------------------------------------------------------------ the hooks


def _ld_slot(vals: dict, key: str, zix: int, nix: int) -> float:
    if 0 <= zix <= ZIX_MAX and 0 <= nix <= NIX_MAX:
        return vals[f"{key}@{zix},{nix}"]
    return vals[f"{key}@rest"]


def overrides_for(vals: dict, Zc: int, Nc: int):
    """The `input.defaults.TMC_OVERRIDES` callable of one sample on the run whose compound
    nucleus is (Zc, Nc)."""
    import torch

    from physics.hf.input.defaults import DTYPE, PARAM_SPECS

    omp_keys = sorted({s.keyword for s in slots() if s.family == "omp"})
    memo: dict = {}

    def build(Z: int, A: int, options) -> dict:
        zi0, ni0 = int(options.Zinit), int(options.Ninit)
        if (zi0, ni0) in memo:
            return memo[(zi0, ni0)]
        out: dict = {}
        for kw, key in (("aadjust", "aadjust"), ("pshiftadjust", "pshift")):
            spec = PARAM_SPECS[kw]
            arr = np.zeros(spec.shape)
            for zi in range(spec.shape[0]):
                for ni in range(spec.shape[1]):
                    # this call's (zi, ni) is the nucleus (zi0 - zi, ni0 - ni); relative to the
                    # run's compound nucleus that is (Zc - zi0 + zi, Nc - ni0 + ni)
                    arr[zi, ni, ...] = _ld_slot(vals, key, Zc - zi0 + zi, Nc - ni0 + ni)
            out[kw] = torch.as_tensor(arr, dtype=DTYPE)
        out["rspincut"] = float(vals["rspincut"])
        for kw in omp_keys:
            out[kw] = {p: float(vals[f"{kw}:{p}"]) for p in ("n", "p", "a")}
        memo[(zi0, ni0)] = out
        return out

    return build


def gamma_for(vals: dict, Zc: int, Ac: int):
    """The `gamma.parameters.TMC_GAMMA` callable: factors for the compound nucleus only."""
    fac = {"ftable": float(vals["ftable"]), "wtable": float(vals["wtable"]),
           "sgr_m1": float(vals["sgr_m1"])}

    def build(Z: int, A: int):
        return fac if (Z, A) == (Zc, Ac) else None

    return build


def install(Z: int, A: int, vals: dict | None) -> None:
    """Put sample `vals` on every later run of target (Z, A) in this process (None: remove)."""
    import physics.hf.gamma.parameters as GP
    import physics.hf.input.defaults as D

    if vals is None:
        D.TMC_OVERRIDES, GP.TMC_GAMMA = None, None
        return
    Zc, Ac = int(Z), int(A) + 1
    D.TMC_OVERRIDES = overrides_for(vals, Zc, Ac - Zc)
    GP.TMC_GAMMA = gamma_for(vals, Zc, Ac)


# ------------------------------------------------------------------------------ GPU capture


GPU_SLOTS = ("ftable", "wtable", "sgr_m1")
GPU_SEED = SEED + 1


def gpu_factors(Z: int, A: int, n_lo: int, n_hi: int, seed: int = GPU_SEED) -> np.ndarray:
    """(n, 3) multiplicative factors on `capture_gpu`'s theta = (ftable, wtable, sgr(M1)): the
    same three priors as the photon-strength slots of `slots()`, on their own 3-d Sobol design."""
    ss = {s.name: s for s in slots()}
    rr = deviates(sobol_uniforms(n_lo, n_hi, 3, seed))
    out = np.empty_like(rr)
    for j, name in enumerate(GPU_SLOTS):
        d = delta_of(ss[name], Z, A)
        out[:, j] = [transform(float(r), "factor", d) for r in rr[:, j]]
    return out


def families() -> dict[str, list[str]]:
    """Slot names by sensitivity family (the ranking's groups)."""
    out: dict[str, list[str]] = {}
    for s in slots():
        if s.family == "ld":
            fam = "ld_spincut" if s.keyword == "rspincut" else f"ld_{s.keyword}"
        elif s.family == "omp":
            fam = f"omp_{s.where}"
        else:
            fam = "psf"
        out.setdefault(fam, []).append(s.name)
    return out

