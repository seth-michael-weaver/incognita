"""ENGADJ: energy-dependent (local) parameter adjustment inside the engine, TALYS adjust.f90 style.

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

Task: ENGADJ (2026-10-13). Acceptance test: tests/hf/test_eadj.py.

Why. Evaluators fit with energy-local PARAMETER adjustments inside the model (TALYS `v1adjust n 1. Ea Eb Em D`, adjust.f90),
so a change in one channel takes its flux from the competing ones. The port skipped those line forms (fitlib._split reads
`v1adjust n 1. Ea ...` as an "energy-dependent table form" and drops the whole line; a per-nucleus one reads Ea as a barrier
index). EMUWIDE had to fake 24 channel bumps as post-hoc output multipliers. This module gives the engine its own, explicit
keyword instead of overloading the TALYS lines (whose port behaviour existing decks may depend on).

Keyword (Incognita extension; one bump per line; deck/lines-file line, any number of them):

    eadj <target> <selector...> tal <Ea> <Eb> <Em> <D>     adjust.f90 shape: 1 outside (Ea, Eb), D at Em, npow 4 flanks
    eadj <target> <selector...> gau <E0> <W> <D>           1 + (D - 1) exp(-(E - E0)^2 / (2 W^2)), smooth everywhere

targets, selector, and the energy E the factor is evaluated at (the variable TALYS itself uses for that family):

    OMP (factor x the ompadjust F* factor):  v1adjust w1adjust d1adjust vso1adjust rvadjust avadjust rwdadjust awdadjust ...
        (every key of omp.parameters._ADJ)   selector = particle symbol n p d t h a.  E = the channel energy at which the
        potential is evaluated (incident energy for the incident channel, emission energy for the inverse channels), for
        every channel of that particle (incident AND outgoing: one energy-dependent potential, so detailed balance holds).
    LD:   a        (x level-density parameter a)             selector = Z A          E = excitation energy Eex of (Z, A)
          pshift   (+ (D-1) MeV on the pairing energy shift)  selector = Z A          E = Eex
          ctable   (+ (D-1) on the table's ln-rho shift c)    selector = Z A          E = Eex   (TALYS density.f90:92-97)
          ptable   (+ (D-1) MeV on the table's energy shift)  selector = Z A          E = Eex
    PSF:  fe1 fm1  (x photon strength f_E1 / f_M1)            selector = Z A          E = Egamma (TALYS fstrength.f90 adjust)
    fission (fismodel 6 WKB path; selector = Z A of the FISSIONING nucleus; E = its excitation energy Eex):
          vfiscor   (x path height scale, vfiscoradjust)
          rmiufiscor (x path inertia scale, rmiufiscoradjust)

Several bumps on one (target, selector) multiply (additive targets: their D-1 add). TALYS keeps only the last matching
range at an energy (adjust.f90 assigns, not multiplies); for non-overlapping windows the two agree, for overlapping ones
the product is continuous where TALYS's assignment jumps. `INCOGNITA_ENGADJ=0` ignores every eadj line (nothing parsed).

Default OFF: a run without `eadj` lines never reaches any of this (every hook first asks `on()`), bit for bit.

TALYS: adjust.f90:1 (adjust), getvalues.f90:303-365 (the Ea Eb Em D line form)
Test: tests/hf/test_eadj.py
"""

from __future__ import annotations

import os
from dataclasses import dataclass

import numpy as np

ENV = "INCOGNITA_ENGADJ"
PARSYM = ("g", "n", "p", "d", "t", "h", "a")

OMP_TARGETS = frozenset({
    "v1adjust", "v2adjust", "v3adjust", "v4adjust", "rvadjust", "avadjust",
    "w1adjust", "w2adjust", "w3adjust", "w4adjust", "rwadjust", "awadjust",
    "rvdadjust", "avdadjust", "d1adjust", "d2adjust", "d3adjust", "rwdadjust", "awdadjust",
    "vso1adjust", "vso2adjust", "rvsoadjust", "avsoadjust", "wso1adjust", "wso2adjust",
    "rwsoadjust", "awsoadjust", "rcadjust",
})  # fmt: skip
LD_TARGETS = frozenset({"a", "pshift", "ctable"})
PSF_TARGETS = frozenset({"fe1", "fm1"})
FIS_TARGETS = frozenset({"vfiscor", "rmiufiscor"})
ADDITIVE = frozenset({"pshift", "ctable"})
TARGETS = OMP_TARGETS | LD_TARGETS | PSF_TARGETS | FIS_TARGETS


@dataclass(frozen=True)
class Bump:
    target: str
    sel: tuple            # (particle type,) for OMP; (Z, A) otherwise
    shape: str            # "tal" | "gau"
    args: tuple           # tal: (Ea, Eb, Em, D); gau: (E0, W, D)

    @property
    def amp(self) -> float:
        return float(self.args[-1]) - 1.0


def parse_line(line: str) -> Bump:
    """One `eadj ...` line -> Bump (ValueError with the reason when it is malformed)."""
    w = line.split()
    if not w or w[0].lower() != "eadj":
        raise ValueError(f"not an eadj line: {line!r}")
    if len(w) < 3:
        raise ValueError(f"eadj: too short: {line!r}")
    t = w[1].lower()
    if t not in TARGETS:
        raise ValueError(f"eadj: unknown target {t!r} (known: {sorted(TARGETS)})")
    if t in OMP_TARGETS:
        p = w[2].lower()
        if p not in PARSYM[1:]:
            raise ValueError(f"eadj: particle {p!r} not one of n p d t h a")
        sel, i = (PARSYM.index(p),), 3
    else:
        sel, i = (int(w[2]), int(w[3])), 4
    if i >= len(w):
        raise ValueError(f"eadj: missing shape in {line!r}")
    shape = w[i].lower()
    vals = tuple(float(x) for x in w[i + 1:])
    if shape == "tal":
        if len(vals) != 4:
            raise ValueError(f"eadj: tal needs Ea Eb Em D: {line!r}")
        ea, eb, em, _ = vals
        if not (ea < em < eb):
            raise ValueError(f"eadj: tal needs Ea < Em < Eb: {line!r}")
    elif shape == "gau":
        if len(vals) != 3:
            raise ValueError(f"eadj: gau needs E0 W D: {line!r}")
        if not vals[1] > 0:
            raise ValueError(f"eadj: gau needs W > 0: {line!r}")
    else:
        raise ValueError(f"eadj: shape {shape!r} not tal|gau")
    return Bump(t, sel, shape, vals)


def _shape(b: Bump, e: np.ndarray) -> np.ndarray:
    """The bump's (factor - 1) / (D - 1) at energies e: 0 outside, 1 at the peak."""
    if b.shape == "gau":
        e0, wd, _ = b.args
        return np.exp(-((e - e0) ** 2) / (2.0 * wd * wd))
    ea, eb, em, _ = b.args
    npow = 4
    out = np.zeros_like(e)
    lo = (e > ea) & (e <= em)
    hi = (e > em) & (e < eb)
    c = ea + 0.5 * (em - ea)
    x = (e[lo] - ea) ** npow
    out[lo] = (1.0 + 0.5**npow) * x / (x + (c - ea) ** npow)
    c = em + 0.5 * (eb - em)
    x = (eb - e[hi]) ** npow
    out[hi] = (1.0 + 0.5**npow) * x / (x + (c - eb) ** npow)
    return out


def bump_values(bumps, e) -> np.ndarray:
    """Combined factor (multiplicative targets) at energies e of the bumps given (all of one target and selector)."""
    e = np.asarray(e, dtype=np.float64)
    f = np.ones_like(e)
    for b in bumps:
        f = f * (1.0 + b.amp * _shape(b, e))
    return f


def bump_shift(bumps, e) -> np.ndarray:
    """Combined additive shift (pshift / ctable / ptable) at energies e: sum of (D - 1) x shape."""
    e = np.asarray(e, dtype=np.float64)
    s = np.zeros_like(e)
    for b in bumps:
        s = s + b.amp * _shape(b, e)
    return s


def scalar(bumps, e: float) -> float:
    """bump_values / bump_shift at one energy, as a Python float (the right one for the target)."""
    if not bumps:
        return 1.0
    arr = np.array([float(e)])
    if bumps[0].target in ADDITIVE:
        return float(bump_shift(bumps, arr)[0])
    return float(bump_values(bumps, arr)[0])


# ------------------------------------------------------------------------------------------ the run's active set
def disabled() -> bool:
    return os.environ.get(ENV, "").strip().lower() in ("0", "off", "n", "no")


def active() -> tuple:
    """The active run's bumps (tuple of Bump), () when none (the default)."""
    if disabled():
        return ()
    from physics.hf.input import fitlib

    c = fitlib.active()
    if c is None:
        return ()
    return getattr(c, "eadj", ())


def _npw():
    from physics.hf.density import npwindow

    return npwindow


def on() -> bool:
    """Any bump this run (deck lines, or the NPWINDOW rule's target ctable bumps, physics/hf/density/npwindow.py)."""
    return bool(active()) or _npw().applies_run()


def select(target: str, sel: tuple) -> tuple:
    """The active bumps of one target and selector, in card order; () when none."""
    bs = active()
    if not bs:
        return ()
    return tuple(b for b in bs if b.target == target and b.sel == tuple(sel))


def any_target(targets) -> bool:
    bs = active()
    return bool(bs) and any(b.target in targets for b in bs)


#: NPWPROMO: the nuclei whose level density the native LD kernels are being asked about (innermost last); pushed by
#: `per_nucleus` wrappers only while the NPWINDOW rule applies to the run
_NUC: list = []


class _Nuc:
    __slots__ = ("za",)

    def __init__(self, Z, A):
        self.za = (int(Z), int(A))

    def __enter__(self):
        _NUC.append(self.za)
        return self

    def __exit__(self, *exc):
        _NUC.pop()
        return False


class _Null:
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


_NULL = _Null()


def nucleus(Z, A):
    """Context: native LD kernels called inside are about nucleus (Z, A) (no-op unless the NPWINDOW rule applies)."""
    return _Nuc(Z, A) if _npw().target() is not None else _NULL


def per_nucleus(fn):
    """Decorator for an LD function whose first argument is the nucleus's `LDNucleus`: its native kernels are asked
    for that nucleus (`ld_native_ok`). Off the NPWINDOW rule it calls `fn` directly."""
    import functools

    @functools.wraps(fn)
    def w(ld, *a, **k):
        if _npw().target() is None:
            return fn(ld, *a, **k)
        with _Nuc(ld.Z, ld.A):
            return fn(ld, *a, **k)

    return w


def ld_native_ok(Z=None, A=None) -> bool:
    """False while a deck level-density bump is active (every nucleus: the native LD kernels ld_nx2 / ld_ceng / ld2_nx2,
    which evaluate a(Eex) and rho in C, are skipped and the Python twins, which carry the bumps, run), or, under the
    NPWINDOW rule, for the rule's target nucleus ((Z, A) given, else the innermost `nucleus` context; none: False).
    True (the default) otherwise."""
    if any_target(LD_TARGETS):  # a deck LD bump: every nucleus on the Python twins (it may name any nucleus)
        return False
    t = _npw().target()
    if t is None:
        return True
    # NPWINDOW: only the rule's target needs the Python twins (its bumps live in models._adjusted); every other
    # nucleus keeps the native kernels. Unknown nucleus (no context): Python, as an ENGADJ run.
    if Z is None:
        if not _NUC:
            return False
        Z, A = _NUC[-1]
    return (int(Z), int(A)) != t


def token() -> tuple:
    """Hashable identity of the active bump set (for cache keys); () when off. NPWINDOW: + the rule's marker."""
    return tuple(active()) + _npw().token()


def omp_factor(key: str, k: int, e):
    """Multiplier of the F* factor `key` (an ompadjust keyword) for particle type k at channel energy e (float or array).

    Returns 1.0 (the float) when no bump is set for it, so callers can keep their exact arithmetic."""
    bs = select(key, (k,))
    if not bs:
        return 1.0
    if np.ndim(e) == 0:
        return float(bump_values(bs, np.array([float(e)]))[0])
    return bump_values(bs, np.asarray(e, dtype=np.float64))


def nucleus_bumps(target: str, Z: int, A: int) -> tuple:
    return select(target, (int(Z), int(A)))


def describe(bumps) -> list[str]:
    return [f"eadj {b.target} {' '.join(PARSYM[s] if b.target in OMP_TARGETS else str(s) for s in b.sel)} "
            f"{b.shape} {' '.join(repr(float(x)) for x in b.args)}" for b in bumps]


# ------------------------------------------------------------------------------- fission: node tables + interpolation
#: Excitation-energy range scanned for a fission bump's factor range (MeV)
_FIS_SCAN = np.linspace(0.0, 60.0, 6001)


def node_set(bumps) -> tuple:
    """Path-scale nodes covering the factor range of `bumps` (1.0 always among them, so energies outside every window
    reproduce the base exactly): (1.0,) when none; 4 Lobatto points with 1.0 at an end for a one-sided range; 5 points
    lo, (lo+1)/2, 1, (1+hi)/2, hi when the bumps go both ways."""
    if not bumps:
        return (1.0,)
    f = bump_values(bumps, _FIS_SCAN)
    lo, hi = min(float(f.min()), 1.0), max(float(f.max()), 1.0)
    if lo == hi:
        return (1.0,)
    if lo < 1.0 < hi:
        return (lo, 0.5 * (lo + 1.0), 1.0, 0.5 * (1.0 + hi), hi)
    return (lo, lo + 0.25 * (hi - lo), lo + 0.75 * (hi - lo), hi)


def lagrange(nodes: tuple, x: np.ndarray) -> np.ndarray:
    """Lagrange weights (len(x), len(nodes)) of `nodes` at x: exactly 1 / 0 at a node."""
    x = np.asarray(x, dtype=np.float64).reshape(-1)
    w = np.ones((x.size, len(nodes)))
    for j, xj in enumerate(nodes):
        for m, xm in enumerate(nodes):
            if m != j:
                w[:, j] *= (x - xm) / (xj - xm)
    return w


def fission_interp(values: list, weights: np.ndarray) -> np.ndarray:
    """Combine node results `values` (K arrays, leading axis = rows) with per-row node `weights` (rows, K): log-space
    Lagrange where every node value of a cell is > 0, linear (clipped at 0) elsewhere. (FissionChain.combine puts the
    base node's own values, bit for bit, on rows whose factors are exactly 1.)"""
    v = np.stack([np.asarray(x, dtype=np.float64) for x in values])  # (K, rows, ...)
    wt = weights.T.reshape((weights.shape[1], weights.shape[0]) + (1,) * (v.ndim - 2))
    pos = np.all(v > 0.0, axis=0)
    with np.errstate(divide="ignore", invalid="ignore"):
        lg = np.exp(np.sum(wt * np.log(np.where(v > 0.0, v, 1.0)), axis=0))
    lin = np.maximum(np.sum(wt * v, axis=0), 0.0)
    return np.where(pos, lg, lin)


def fission_factors(Z: int, A: int, ex) -> tuple:
    """(s_v, s_m) path-scale factors of nucleus (Z, A) at excitation energies ex (arrays)."""
    ex = np.asarray(ex, dtype=np.float64).reshape(-1)
    bv, bm = nucleus_bumps("vfiscor", Z, A), nucleus_bumps("rmiufiscor", Z, A)
    sv = bump_values(bv, ex) if bv else np.ones_like(ex)
    sm = bump_values(bm, ex) if bm else np.ones_like(ex)
    return sv, sm


def fission_weights(nv: tuple, nm: tuple, sv: np.ndarray, sm: np.ndarray, bilin: bool | None = None) -> np.ndarray:
    """Tensor-product Lagrange weights (rows, len(nv) * len(nm)), node order (iv, im) row-major.
    ENGNAN: `bilin` (default: `INCOGNITA_EADJFIS=bilin`) gives the tensor-product piecewise-linear (hat) weights instead."""
    if bilin is None:
        bilin = fis_bilin()
    f = hat if bilin else lagrange
    wv, wm = f(nv, sv), f(nm, sm)
    return (wv[:, :, None] * wm[:, None, :]).reshape(wv.shape[0], -1)


# ------------------------------------------------------------------------------- ENGNAN: well-conditioned fission combine
#: `INCOGNITA_EADJFIS=bilin`: piecewise-linear (hat) node weights everywhere (default OFF = degree-(K-1) Lagrange)
FIS_ENV = "INCOGNITA_EADJFIS"


def fis_bilin() -> bool:
    return os.environ.get(FIS_ENV, "").strip().lower() == "bilin"


def hat(nodes: tuple, x: np.ndarray) -> np.ndarray:
    """Piecewise-linear (hat) weights (len(x), len(nodes)) of `nodes` at x: exactly 1 / 0 at a node, in [0, 1], summing to 1;
    x outside the node range is clamped to it. Unlike `lagrange` they cannot amplify: node sets whose spacing differs by
    orders of magnitude (e.g. (0.981, 0.991, 1, 1.0001, 1.0002), a one-sided bump product with a tiny excursion past 1)
    give Lagrange weights ~1e5 there, and exp(sum w log v) overflowed (ENGNAN: NaN Th-232 tot_fission)."""
    x = np.asarray(x, dtype=np.float64).reshape(-1)
    nd = np.asarray(nodes, dtype=np.float64)
    w = np.zeros((x.size, nd.size))
    if nd.size == 1:
        w[:, 0] = 1.0
        return w
    o = np.argsort(nd)
    s = nd[o]
    xc = np.clip(x, s[0], s[-1])
    k = np.clip(np.searchsorted(s, xc, side="right") - 1, 0, s.size - 2)
    t = (xc - s[k]) / (s[k + 1] - s[k])
    r = np.arange(x.size)
    w[r, o[k]] = 1.0 - t
    w[r, o[k + 1]] += t
    return w

