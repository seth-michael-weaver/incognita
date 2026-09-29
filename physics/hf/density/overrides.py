"""Parameter overrides that put a TALYS keyword family on the autograd graph (DIFFPARAM).

Task: DIFFPARAM (gate G0.4). Acceptance test: tests/hf/test_capture_fast.py, A-ld / A-trans
unmoved.

G0.3 (SPEED0) put the **photon-strength** family on the graph by handing
`capture_fast.target(..., gamma_overrides=...)` a dict of T7 `gamma_parameters` fields as
`requires_grad` tensors. This module is the same idea for the other two families TALYS users
tune, and it is deliberately *narrower*: instead of overriding a resolved physics object it
overrides the **TALYS input keyword**, i.e. an entry of `input.defaults.Params`.

Why the keyword and not the resolved value
------------------------------------------
`default_params(Z, A, options, overrides=...)` already accepts overrides, already returns
float64 tensors, and already runs TALYS's *post*-resolution links afterwards (`rwadjust` takes
`rvadjust` unless given, `ctable`/`ptable` take `cglobal`/`pglobal`, `alphald` takes the global
value). `density.parameters.densitypar` reads those tensors straight through -- its docstring
says so: "`aadjust`, `pshift`, `ctable`, `ptable`, `s2adjust`, `krotconstant` carry gradients" --
and `omp.parameters` applies the `F*` adjustment factors on every path, always, precisely so
that they are differentiable. So the whole differentiability of both families was already built;
what was missing was that **every consumer reached those tensors through an `lru_cache` keyed on
(Z, A) and then dropped to numpy**. That is what this module and its call sites fix.

The two families are separate arguments rather than one dict because they have different costs:
a density override rebuilds `LDNucleus` per cascade nucleus, an optical override rebuilds the
whole emission-grid transmission (`inverse_channels`, the expensive one). A fit that only moves
level densities should not pay for the second, and vice versa.

What is *not* supported, and why it raises rather than being ignored
--------------------------------------------------------------------
Keywords outside the two families below. Masses (`massexcess`, `massnucleus`, `beta2`) are
resolved once per run by `structure.masses` and cached across both families here on the grounds
that no key in either set can move them; overriding a mass keyword through this path would
silently use the unperturbed masses, so it is rejected instead. Photon strength keeps its own
`gamma_overrides` argument (G0.3) and is rejected here for the same reason -- two mechanisms
for one family is how a fit ends up differentiating something it is not evaluating.
"""

from __future__ import annotations

from collections.abc import Mapping

import torch

# ------------------------------------------------------------------------------------------------
# the two families
# ------------------------------------------------------------------------------------------------

#: Level-density keywords (input_densitypar.f90). Everything `densitypar`/`densitymatch`/
#: `attach_tables` reads out of `Params` and nothing else.
DENSITY_KEYS: frozenset[str] = frozenset({
    # the level density parameter a and its Ignatyuk ingredients
    "a", "aadjust", "alimit", "gammald", "deltaw", "alphald", "betald",
    "gammashell1", "gammashell2",
    # pairing
    "pair", "pairconstant", "pshift", "pshiftadjust", "pshiftconstant",
    # spin cutoff and the moment of inertia
    "s2adjust", "rspincut", "rspincutff", "krotconstant", "ufermi", "cfermi",
    # the tabulated models' c/p shifts (ldmodel 4-6)
    "ctable", "ptable", "ctableadjust", "ptableadjust", "cglobal", "pglobal",
    # the constant-temperature branch
    "t", "tadjust", "e0", "e0adjust", "exmatch", "exmatchadjust", "d0",
})

#: Optical-model keywords (input_omppar.f90 / ompadjust.f90). The `F*` multiplicative factors of
#: `omp.parameters.ompadjust` plus `vinfadjust`; the energy-dependent `ompadjustE1/E2/D/s` ranges
#: are *not* here because `omp.parameters` does not port adjust.f90's energy ranges (its §5 note).
OPTICAL_KEYS: frozenset[str] = frozenset({
    "v1adjust", "v2adjust", "v3adjust", "v4adjust", "rvadjust", "avadjust",
    "w1adjust", "w2adjust", "w3adjust", "w4adjust", "rwadjust", "awadjust",
    "d1adjust", "d2adjust", "d3adjust", "rvdadjust", "avdadjust", "rwdadjust", "awdadjust",
    "vso1adjust", "vso2adjust", "rvsoadjust", "avsoadjust",
    "wso1adjust", "wso2adjust", "rwsoadjust", "awsoadjust",
    "rcadjust", "vinfadjust",
    # JLM (radialmodel/jlmomp); harmless to allow, they reach the same `_final_adjust`
    "lvadjust", "lwadjust", "lv1adjust", "lw1adjust", "lvsoadjust", "lwsoadjust",
})


def check(overrides: Mapping[str, object] | None, family: str) -> Mapping[str, object] | None:
    """Reject a keyword that is not in `family` ("density" or "optical").

    A typo, or a keyword whose consumer this plumbing does not rebuild, must not be silently
    dropped: the gradient would be a clean-looking zero and the finite difference would not
    match it.
    """
    if not overrides:
        return None
    keys = DENSITY_KEYS if family == "density" else OPTICAL_KEYS
    bad = sorted(k for k in overrides if k.lower() not in keys)
    if bad:
        raise KeyError(
            f"{family} overrides: {bad} is not a {family} keyword. Level density: "
            f"{sorted(DENSITY_KEYS)}; optical: {sorted(OPTICAL_KEYS)}. Photon strength keeps "
            "capture_fast.target(gamma_overrides=...) (G0.3)."
        )
    return {k.lower(): v for k, v in overrides.items()}


def merge(density: Mapping | None, optical: Mapping | None) -> dict | None:
    """The two families as the one `overrides` mapping `default_params` takes, or None."""
    d = check(density, "density")
    o = check(optical, "optical")
    if not d and not o:
        return None
    return {**(d or {}), **(o or {})}


def token(overrides: Mapping[str, object] | None) -> tuple | None:
    """A hashable identity for one override mapping, for the per-`Cascade` caches.

    Tensors are keyed by `id`, not by value: a fit hands a *new* tensor every step, and two
    different tensors with equal values must not share a cached `LDNucleus` (they are different
    graph nodes). `id` reuse after garbage collection can only alias a mapping that no longer
    exists, and the caches this keys are per-`CaptureTarget`, which holds its overrides alive.
    """
    if not overrides:
        return None
    return tuple(sorted(
        (k, id(v) if isinstance(v, torch.Tensor) else repr(v)) for k, v in overrides.items()
    ))


def torch_path(overrides: Mapping[str, object] | None) -> bool:
    """True when any override entry is a **tensor**, which is what selects the torch path.

    Not `requires_grad`: a central finite difference of the gradient has to walk the same code
    as the gradient, and it perturbs plain (grad-free) tensors. Keying on the type instead means
    autograd and its own finite-difference check share one path, and the numpy fast path is
    reached by a float override -- which is the pair
    `tests/hf/test_capture_fast.py::test_override_paths_agree` compares at 1e-12.
    """
    if not overrides:
        return False
    for v in overrides.values():
        if isinstance(v, torch.Tensor):
            return True
        if isinstance(v, Mapping) and any(isinstance(x, torch.Tensor) for x in v.values()):
            return True
    return False


# ------------------------------------------------------------------------------------------------
# PARAMWIRE: a fit's parameter set, keyed by value, on the numpy / NATIVEX path
# ------------------------------------------------------------------------------------------------
#
# The DIFFPARAM hooks above exist for autograd: a tensor switches the run onto the graph and every
# cache is bypassed, because an `lru_cache` would hand the next step the previous step's tensors.
# A fit that re-evaluates the chart at a new parameter point wants the opposite: plain floats, the
# numpy and C kernels on, and every level-density / photon-strength cache KEYED by the parameter it
# reads, so a warm step recomputes only what that parameter reaches (ROUTE100 WP3,
# docs/results/hf-warm0.md §4.3).
#
# A parameter set is a sorted tuple of `(keyword, Z, A, value)` in absolute nuclide coordinates,
# TALYS's own `keyword Z A value` form. Absolute coordinates matter: the chain builds a residual's
# level density on the TARGET's `Params` (`_ld_of(Z, A, Zt, At)`) but its photon strength on the
# pseudo-target (Z, A - 1)'s (`_gamma_parameters(Z, A - 1)`), two runs whose (Zix, Nix) of the
# same nucleus differ. Each consumer asks for the entries of ITS nucleus (`ld_token`,
# `gamma_token`), so a change at the compound nucleus rebuilds the compound nucleus's objects and
# leaves the other ~50 nuclei of the cascade on their cached defaults.

#: What a parameter set may carry, and the TALYS routine each one reaches.
#: `aadjust` (input_densitypar.f90:252): the level density parameter `a` of (Z, A) -- its level
#: density, `alev` in its photon strength (gammapar/fstrength), fission barrier level densities.
#: `ftable` / `wtable` (input_gammapar.f90:313-326): the E1 tabulated strength of (Z, A), its
#: normalisation and its width about the maximum; `wtable` REPLACES the global default
#: (input_gammapar.f90:115-137), it does not multiply it.
#: FISBARWIRE: `fisbaradjust` / `fishwadjust` of (Z, A) (input_fissionpar.f90:210-229) multiply the
#: height and curvature of EVERY barrier of (Z, A) in `t1barrier` (t1barrier.f90:99-121) -- TALYS's
#: per-barrier keywords with the barriers tied. `fismodel` is global in TALYS and is given at
#: Z = A = 0. These three reach only `fission.chain.FissionChain`; `Cascade.set_fit_params` keeps
#: them out of `Cascade.fit`, so the level-density / photon-strength / pre-equilibrium caches see
#: the same key with or without them.
FISSION_KEYS: frozenset[str] = frozenset({"fismodel", "fisbaradjust", "fishwadjust"})
FIT_KEYS: frozenset[str] = frozenset({"aadjust", "ftable", "wtable"}) | FISSION_KEYS


def fit_params(items) -> tuple[tuple[str, int, int, float], ...]:
    """A parameter set in canonical form: lowercase keyword, int Z and A, float value, sorted.

    Rejects keywords outside `FIT_KEYS` (a consumer this plumbing does not route would be a clean
    silent no-op) and a (keyword, Z, A) given twice.
    """
    out = {}
    for it in items or ():
        k, z, a, v = it
        k = str(k).lower()
        if k not in FIT_KEYS:
            raise KeyError(f"parameter set: {k!r} is not one of {sorted(FIT_KEYS)}")
        if isinstance(v, torch.Tensor):
            raise TypeError(f"parameter set: {k} {z} {a} is a tensor; use set_param_overrides / "
                            "gamma_overrides for autograd")
        key = (k, int(z), int(a))
        if k == "fismodel" and (key[1:] != (0, 0) or float(v) not in (1.0, 2.0, 3.0, 4.0, 5.0, 6.0)):
            raise ValueError(f"parameter set: fismodel is global (Z = A = 0) and 1-6, got {it}")
        if key in out:
            raise ValueError(f"parameter set: {key} given twice")
        out[key] = float(v)
    return tuple(sorted((k, z, a, v) for (k, z, a), v in out.items()))


def fit_value(fit, keyword: str, Z: int, A: int) -> float | None:
    for k, z, a, v in fit or ():
        if k == keyword and z == Z and a == A:
            return v
    return None


def ld_token(fit, Z: int, A: int) -> float | None:
    """What of `fit` the level density of (Z, A) reads: its `aadjust`, or None (defaults)."""
    return fit_value(fit, "aadjust", Z, A) if fit else None


def gamma_token(fit, Z: int, A: int) -> tuple | None:
    """What of `fit` the photon strength of (Z, A) reads -- `aadjust` through `alev`, and the E1
    `ftable`/`wtable` -- or None when it reads none of them."""
    if not fit:
        return None
    tok = tuple(fit_value(fit, k, Z, A) for k in ("aadjust", "ftable", "wtable"))
    return None if tok == (None, None, None) else tok


def fit_subset(fit, nuclei) -> tuple:
    """The entries of `fit` at the nuclei `nuclei` ((Z, A) pairs), as a cache key."""
    want = {(int(z), int(a)) for z, a in nuclei}
    return tuple(e for e in fit or () if (e[1], e[2]) in want)


def with_aadjust(params, options, entries) -> object:
    """`params` with `aadjust` set at `entries` ((Z, A, value), absolute), for the run `options`
    belongs to. Nuclei outside the run's (Zix, Nix) box are skipped. Returns `params` itself when
    nothing lands, so the default path keeps its object; otherwise a shallow copy that shares every
    other keyword's tensor (nothing writes into `Params` tensors in place; `_structure_of` already
    shares one `Params` among all its callers).
    """
    from physics.hf.input.defaults import PARAM_SPECS, Params

    spec = PARAM_SPECS["aadjust"]
    cells = []
    for z, a, v in entries:
        zix, nix = options.Zinit - int(z), options.Ninit - (int(a) - int(z))
        (zlo, zhi), (nlo, nhi) = spec.dims
        if zlo <= zix <= zhi and nlo <= nix <= nhi:
            cells.append((zix + spec.offsets[0], nix + spec.offsets[1], float(v)))
    if not cells:
        return params
    t = params.values["aadjust"].clone()
    for i, j, v in cells:
        t[i, j] = v
    return Params({**params.values, "aadjust": t})


def fission_entries(fit) -> tuple:
    """The `FISSION_KEYS` entries of a canonical parameter set."""
    return tuple(e for e in fit or () if e[0] in FISSION_KEYS)


def without_fission(fit) -> tuple:
    """A canonical parameter set without its `FISSION_KEYS` entries."""
    return tuple(e for e in fit or () if e[0] not in FISSION_KEYS)


def with_fission_adjust(params, options, fit) -> object:
    """`params` with `fisbaradjust` / `fishwadjust` set on every barrier of each (Z, A) the parameter
    set names, for the run `options` belongs to (`with_aadjust`'s conventions: nuclei outside the
    run's (Zix, Nix) box are skipped, and `params` itself comes back when nothing lands).

    TALYS: input_fissionpar.f90:210-229 (input_fissionpar)
    Test: tests/hf/test_fisbarwire.py
    """
    from physics.hf.input.defaults import PARAM_SPECS, Params

    new = {}
    for k, z, a, v in fit or ():
        if k not in ("fisbaradjust", "fishwadjust"):
            continue
        spec = PARAM_SPECS[k]
        zix, nix = options.Zinit - int(z), options.Ninit - (int(a) - int(z))
        (zlo, zhi), (nlo, nhi), _bar = spec.dims
        if not (zlo <= zix <= zhi and nlo <= nix <= nhi):
            continue
        t = new.get(k)
        if t is None:
            t = new[k] = params.values[k].clone()
        t[zix + spec.offsets[0], nix + spec.offsets[1], 1 + spec.offsets[2]:] = float(v)
    return Params({**params.values, **new}) if new else params


def aadjust_entries(fit) -> tuple[tuple[int, int, float], ...]:
    return tuple((z, a, v) for k, z, a, v in fit or () if k == "aadjust")


def gamma_fit_overrides(tok: tuple | None, gammax: int) -> dict | None:
    """`gamma.parameters.gamma_parameters` overrides for a `gamma_token`: E1 (irad 1, l 1) entries
    of (2, gammax + 1) arrays, zero elsewhere -- `fill` keeps the default wherever the override is
    zero, exactly as TALYS keeps what the user left unset."""
    if tok is None:
        return None
    import numpy as np

    out = {}
    for name, v in (("ftable", tok[1]), ("wtable", tok[2])):
        if v is not None:
            arr = np.zeros((2, int(gammax) + 1))
            arr[1, 1] = v
            out[name] = arr
    return out or None


__all__ = ["DENSITY_KEYS", "FISSION_KEYS", "FIT_KEYS", "OPTICAL_KEYS", "aadjust_entries", "check",
           "fission_entries", "fit_params", "fit_subset", "fit_value", "gamma_fit_overrides",
           "gamma_token", "ld_token", "merge", "token", "torch_path", "with_aadjust",
           "with_fission_adjust", "without_fission"]
