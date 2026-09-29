"""The `preequilibrium_inverse_xs` family, computed: T5's inverse channels instead of
`cross_<p>.tot`, and T12/T13's direct cross sections instead of `directE*.out` headers.

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

Task: NODUMP (physics/hf/CONTRACT.md §7). Acceptance test: A-pe / E2E (§6).

T8 ported the exciton model itself; what it injected (contract §5, and its module docstring says
so) are the five inputs `preeq.prepare.prepare` reads off a reference run:

| injected                            | computed here from                                    |
|-------------------------------------|-------------------------------------------------------|
| `xsreac(type, nen)`, `cross_<p>.tot` | T5 `omp.inverse.inverse_channels` on the emission grid |
| `xsreac(0, nen)`, `cross_g.tot`      | already T7's `gammaxs` -- only its `GammaParameters` came off the `ld*.gs` / `psf*.M1` headers |
| `pair(Zix, Nix)`, `ld*.gs` header    | T6 `density.parameters.densitypar`                     |
| `xsflux`, `talys.out` + `directE*.out` headers | T5's incident sigma_reac minus T12/T13's `direct.chain` |
| `xsdirdisc(type, i)`, `directE*.out` rows | T12/T13's `direct.chain`                          |

Two traps the dumped arm documents and this one has to reproduce exactly, because they are
properties of TALYS's arrays and not of where the numbers came from:

* **Nothing above `eendmax(type)`.** `inverse` fills `xsreac` only over `[ebegin, eendmax]`
  (inverseecis.f90:402) and TALYS reads a hard zero past it. Padding with the last value makes
  `knockout`'s `sigav = xsreac(type2, eend(type2))` finite where TALYS has 0, which inflates
  `denomki` and shrinks the alpha knockout ~25x.
* **`xsreac(0, .)` moves with the INCIDENT energy**, not only with the emission energy:
  `tgamma.f90:73` sets it from `gammaxs`, which reads `fstrength(..., Einc, Egamma, ...)`.

`enincmax` is the run's highest incident energy and fixes the emission grid, so it -- like the
declared energy grid -- is an input of the whole module rather than of one energy.
"""

from __future__ import annotations

import weakref
from collections.abc import Mapping
from functools import lru_cache

import numpy as np
import torch

from physics.hf.core.constants import NUC
from physics.hf.core.tensors import DTYPE


def target_tag(Z: int, A: int) -> str:
    """(26, 56) -> "Fe056", the inverse of `preeq.prepare.parse_target`."""
    return f"{NUC[Z - 1].strip().capitalize()}{A:03d}"


class _ByEnergy(Mapping):
    """A read-only `{rounded energy: value}` map whose values are computed on FIRST LOOKUP.

    SPEEDP. The chained arm's expensive per-energy quantities -- the DWBA/giant block of
    `chained_direct` and the incident reaction cross section -- used to be built for the whole
    declared grid the moment anything asked for one energy. A run that computes a subset of the
    grid (`engine.ChainedFull(energies=...)`, `capture_fast`, any scoring pass that walks the
    grid one energy at a time) then paid for 23 ECIS solves to read six. The value at a key is
    exactly what the eager dict held there -- the same call with the same arguments -- so this is
    a scheduling change and not a physics one.

    Iteration and `len` are over the declared key set and force nothing; only `[]`/`.get()` do.
    """

    __slots__ = ("_keys", "_fn", "_memo")

    def __init__(self, keys, fn):
        self._keys = tuple(keys)
        self._fn = fn
        self._memo: dict = {}

    def __getitem__(self, key):
        k = round(float(key), 6)
        try:
            return self._memo[k]
        except KeyError:
            pass
        if k not in self._keys:
            raise KeyError(key)
        v = self._fn(k)
        self._memo[k] = v
        return v

    def __iter__(self):
        return iter(self._keys)

    def __len__(self) -> int:
        return len(self._keys)

    def computed(self) -> int:
        """How many keys were actually evaluated (for the speed table)."""
        return len(self._memo)


# ---------------------------------------------------------------- the run's one Cascade (SPEEDP)

# `Cascade.incident` is an instance-level `lru_cache`, so two Cascades over the same target solve
# the incident channel twice. `incident_reaction_xs` used to build its own, which meant the
# engine's six solves and the chained pre-equilibrium's were never shared -- and on a `colltype
# R`/`V` target each one is a coupled-channels ECIS deck. `Cascade.incident(e)` reads only
# (Zt, At, k0, options, run grid), never `Cascade.energies` (that is `fisom`'s alone), so one
# Cascade per (Zt, At, enincmax, k0) serves every caller. The engine LENDS its own rather than
# having one handed to it: the borrower must not outlive the run that owns it, and must not
# inherit a Cascade some other run has hung DIFFPARAM overrides on.
_LENT: dict[tuple, weakref.ReferenceType] = {}


def lend_cascade(cas) -> None:
    """Offer `cas` as the Cascade `incident_reaction_xs` should solve the incident channel on.

    Held weakly and keyed by (Zt, At, enincmax, k0); a lender with parameter overrides on it is
    refused, because the chained pre-equilibrium's `xsreacinc` is not on the override graph yet
    and silently putting it there would change numbers nothing has gated.
    """
    from physics.hf.density.overrides import torch_path

    # PARAMWIRE: the incident channel reads the optical model only, so a parameter set and float
    # level-density / photon-strength overrides do not stop the lending; a graph or an optical
    # override does
    if (getattr(cas, "diff_params", False) or getattr(cas, "omp_overrides", None)
            or torch_path(getattr(cas, "gamma_overrides", None))):
        return
    _LENT[(int(cas.Zt), int(cas.At), float(cas.enincmax), int(cas.k0))] = weakref.ref(cas)


@lru_cache(maxsize=8)
def _own_cascade(Zt: int, At: int, enincmax_mev: float, energies: tuple[float, ...]):
    from physics.hf.emission.feeding import Cascade

    return Cascade(Zt, At, enincmax_mev, energies=energies)


def _incident_cascade(Zt: int, At: int, energies: tuple[float, ...]):
    enincmax = max(energies)
    ref = _LENT.get((Zt, At, float(enincmax), 1))
    cas = None if ref is None else ref()
    if cas is not None and not getattr(cas, "diff_params", False):
        return cas
    return _own_cascade(Zt, At, float(enincmax), tuple(energies))


# ------------------------------------------------------- which declared energies a run computes

# preeq.f90 runs at every declared energy above `epreeq`; a run that computes a SUBSET of the
# declared grid reads the exciton model at that subset only, and the rows in between are dead
# work (`exciton_model` is batched over a case axis, so a row costs what a row costs). The
# subset is registered here rather than threaded through `norm_reference.addends` and
# `emission.feed_reference._preeq_of`, because the second of those belongs to another branch;
# registering a DIFFERENT subset for the same (target, declared grid) drops both caches, so a
# stale narrow answer can never be served to a wider run.
_SUBSET: dict[tuple, tuple[float, ...]] = {}


def set_energy_subset(Zt: int, At: int, declared, wanted) -> None:
    """Declare which of `declared` this run actually computes (None = all of them).

    A `wanted` that covers the whole declared grid deregisters instead of registering, so the
    full-grid run E2E scores never trims and never drops a cache.
    """
    key = (int(Zt), int(At), tuple(round(float(e), 6) for e in declared))
    new = tuple(sorted({round(float(e), 6) for e in wanted})) if wanted is not None else None
    if new is not None and set(new) >= set(key[2]):
        new = None
    if _SUBSET.get(key) == new:
        return
    if new is None:
        _SUBSET.pop(key, None)
    else:
        _SUBSET[key] = new
    clear_preeq_caches()


def energy_subset(Zt: int, At: int, declared) -> tuple[float, ...] | None:
    return _SUBSET.get((int(Zt), int(At), tuple(round(float(e), 6) for e in declared)))


def clear_preeq_caches() -> None:
    """Drop every cache whose value depends on the registered subset."""
    from physics.hf.compound import pop_reference
    from physics.hf.emission import feed_reference

    pop_reference._preeq.cache_clear()
    feed_reference._preeq_of.cache_clear()


@lru_cache(maxsize=32)
def inverse_reaction_xs(Zt: int, At: int, enincmax_mev: float) -> np.ndarray:
    """`xsreac(type, nen)` [mb] for types 1..6 on the emission grid -- T5's inverse channels.

    Shape (7, maxen+1); row 0 (the photo-absorption) is left at zero, because it is per INCIDENT
    energy and `preeq.prepare` fills it from T7. Everything outside `[ebegin(type),
    eendmax(type)]` is zero, exactly as `inverse` leaves it.

    TALYS: inverse.f90:1 (inverse), inverseecis.f90:1 (inverseecis), basicxs.f90:1 (basicxs)
    Test: A-trans / A-pe
    """
    from physics.hf.compound.dens_reference import _eendmax, _transmission, run_grid

    # SPEEDP: `_transmission` runs exactly this `inverse_channels` solve -- same run grid, same
    # `CaseBatch`, same `lmax` cap -- for the emission-grid `Tjl` the cascade needs, and now
    # carries `sigma_reac_mb` out of it. Building it here a second time was the single most
    # expensive thing NODUMP added per target after the DWBA.
    rg = run_grid(Zt, At, enincmax_mev)
    E = rg.maxen + 1
    sigma = _transmission(Zt, At, enincmax_mev)["sigma_reac_mb"]
    eendmax = _eendmax(Zt, At, enincmax_mev)
    out = np.zeros((7, E))
    nen = np.arange(E)
    for t in range(1, 7):
        keep = (nen >= rg.ebegin[t]) & (nen <= int(eendmax[t]))
        out[t] = np.where(keep, sigma[t - 1].detach().numpy().astype(float)[:E], 0.0)
    return out


@lru_cache(maxsize=32)
def incident_reaction_xs(Zt: int, At: int, energies: tuple[float, ...]) -> Mapping:
    """`xsreacinc` [mb] at each declared incident energy, from T5 (T13 for a coupled target).

    The same choice `emission.feeding.Cascade.incident` makes: a `colltype R`/`V` target is
    solved coupled-channels, and reading it as spherical costs Ca-40's sigma_reac 40% at 1 keV.

    SPEEDP: solved on the run's one Cascade (`_incident_cascade`) and only at the energies that
    are read (`_ByEnergy`). `Cascade.incident` does not look at `Cascade.energies`, so which
    grid the Cascade was built on cannot move the answer -- only how many times it is solved.

    TALYS: incident.f90:1 (incident), incidentecis.f90:1 (incidentecis)
    Test: A-inc
    """
    keys = tuple(round(float(e), 6) for e in energies)
    e_of = dict(zip(keys, (float(e) for e in energies), strict=True))

    def one(k: float) -> float:
        cas = _incident_cascade(Zt, At, tuple(energies))
        return float(cas.incident(e_of[k]).sigma_reac_mb[0])

    return _ByEnergy(keys, one)


@lru_cache(maxsize=32)
def chained_direct(Zt: int, At: int, energies: tuple[float, ...]) -> Mapping:
    """`(DirectResult, flaggiant)` at every declared energy, computed by `direct.chain`.

    Cached because `preeq.prepare` needs it twice (the flux and the discrete cross sections) and
    `compound.pop_reference` a third time.

    SPEEDP: an energy's DWBA is solved on FIRST LOOKUP, not on construction. `energies` stays in
    the key and is still handed to `direct_result` whole, because `direct.chain._coupled` stitches
    `soswitch` across the axis and `direct.prepare.case` resolves the onsets on it -- what changes
    is only which rows are ever built. `engine._BuiltInputs` asks for the six energies its run
    computes out of a declared 23, and the flux asks for the pre-equilibrium ones.

    TALYS: direct.f90:1 (direct)
    Test: A-direct / A-mult
    """
    from physics.hf.direct.chain import direct_result

    tag = target_tag(Zt, At)
    keys = tuple(round(float(e), 6) for e in energies)
    e_of = dict(zip(keys, (float(e) for e in energies), strict=True))
    return _ByEnergy(keys, lambda k: direct_result(tag, e_of[k], energies))


def chained_flux(Zt: int, At: int, energies: tuple[float, ...], grid=None) -> np.ndarray:
    """`xsflux = xsreacinc - xsdirdiscsum - xsgrsum` [mb] (preeq.f90:105-106), computed.

    The three subtracted parts are the three header fields of `directE*.out` the dumped arm
    reads: the total discrete direct inelastic cross section, the collective continuum one, and
    the total giant-resonance one -- `xsdirdisctot`, `xscollconttot` and `xsgrcoll.sum()` of a
    `DirectResult`, the last taken BEFORE giant.f90:130 folds the collective continuum into
    `xsgrtot` (which would double-count it).

    `grid` is the energy axis the direct calculation belongs to. It is the pre-equilibrium
    energy list of the WHOLE declared grid even when `energies` is the subset a run computes
    (SPEEDP): `direct.chain._coupled` and `direct.prepare.case` both read that axis, so trimming
    it would move numbers rather than only save work.

    TALYS: preeq.f90:1 (preeq), giant.f90:122-131
    Test: A-pe
    """
    grid = tuple(energies) if grid is None else tuple(grid)
    reac = incident_reaction_xs(Zt, At, grid)
    dirs = chained_direct(Zt, At, grid)
    out = np.zeros(len(energies))
    for i, e in enumerate(energies):
        k = round(float(e), 6)
        d, _g = dirs[k]
        x = (reac[k] - float(d.xsdirdisctot_mb) - float(d.xscollconttot_mb)
             - float(d.xsgrcoll_mb.sum()))
        out[i] = max(x, 0.0)
    return out


def chained_direct_discrete(Zt: int, At: int, energies: tuple[float, ...], k0: int,
                            nlast: tuple[int, ...], grid=None) -> list[list[np.ndarray]]:
    """`xsdirdisc(type, i)` [mb] per energy, computed. Only the `k0` channel is non-zero for a
    neutron projectile; `preeqcorrect` skips any level that already has one
    (preeqcorrect.f90:54).

    `grid`, as in `chained_flux`, is the direct calculation's own energy axis.

    TALYS: directread.f90:1 (directread)
    Test: A-pe
    """
    dirs = chained_direct(Zt, At, tuple(energies) if grid is None else tuple(grid))
    out = []
    for e in energies:
        per = [np.zeros(nlast[t] + 1) for t in range(7)]
        d, _g = dirs[round(float(e), 6)]
        dd = np.asarray(d.xsdirdisc_mb.detach().numpy(), float)
        n = min(nlast[k0] + 1, dd.shape[0])
        per[k0][:n] = dd[:n]
        out.append(per)
    return out


def chained_pairing(Zr: int, Ar: int, options, params, m) -> float:
    """`pair(Zix, Nix)` [MeV] from T6, where the dumped arm reads the `ld*.gs` header.

    `densitypar` computes it the same way for every level-density model
    (densitypar.f90:397-405), which is why the header and this agree even for the tabulated
    models that print no pairing energy at all. `params` is the run's, with a parameter set's
    `aadjust` applied by the caller (PARAMWIRE); `pair` does not read `aadjust`, so that routing
    moves nothing today and is there for a set that carries `pair`/`pshift`.

    TALYS: densitypar.f90:1 (densitypar)
    Test: A-ld / A-pe
    """
    from physics.hf.density.parameters import densitypar
    from physics.hf.structure.levels import discrete_levels

    try:
        lv = discrete_levels(Zr, Ar, options, m, params)
        return float(densitypar(Zr, Ar, options, params, m, lv).pair_mev)
    except Exception:  # pragma: no cover - nucleus outside the structure database
        return 0.0


def chained_photoabsorption(Zt: int, At: int, egrid: np.ndarray, nmax: int,
                            energies, fit: tuple = ()) -> np.ndarray:
    """`xsreac(0, nen)` per incident energy, shape (C, nmax+1) [mb], on T7's chained parameters.

    `preeq.prepare._photoabsorption` already computes this from `gammaxs`; the only injected
    part was the `GammaParameters`, which it built from the `ld<ZZZ><AAA>.gs` and `psf*.M1`
    headers. `compound.dens_reference._gamma_parameters` builds the same object from T2, T6 and
    T7 (gate A-psf), which is what the rest of the chain already uses.

    TALYS: gammaxs.f90:1 (gammaxs), tgamma.f90:1 (tgamma)
    Test: A-psf / A-pe
    """
    from physics.hf.compound.dens_reference import _gamma_parameters
    from physics.hf.density.overrides import gamma_token
    from physics.hf.gamma.transmission import gammaxs

    # PARAMWIRE: the compound nucleus's `aadjust` (its `alev`) and E1 `ftable`/`wtable`
    tok = gamma_token(fit, Zt, At + 1)
    gp, _o = _gamma_parameters(Zt, At) if tok is None else _gamma_parameters(Zt, At, tok)
    e = torch.tensor(egrid[1 : nmax + 1], dtype=DTYPE)
    out = np.zeros((len(energies), nmax + 1))
    for i, einc in enumerate(energies):
        out[i, 1:] = gammaxs(gp, e, float(einc), Zt, At)[0].detach().numpy()
    return out


def preeq_energies(Zt: int, At: int, energies: tuple[float, ...]) -> list[float]:
    """The declared energies at which TALYS runs `preeq` at all -- `flagpreeq`, i.e. `Einc >=
    epreeq` (energies.f90:194-203). The dumped arm reads the list of `exciton*.out` files.

    TALYS: energies.f90:1 (energies)
    Test: A-pe
    """
    from physics.hf.structure.scalars import structure_scalars

    sc = structure_scalars(Zt, At, tuple(energies))
    return [float(e) for e in energies if sc.flags(e)["flagpreeq"]]


__all__ = [
    "chained_direct", "chained_direct_discrete", "chained_flux", "chained_pairing",
    "chained_photoabsorption", "clear_preeq_caches", "energy_subset", "incident_reaction_xs",
    "inverse_reaction_xs", "lend_cascade", "preeq_energies", "set_energy_subset", "target_tag",
]
