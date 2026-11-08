"""KWCOV B6: `optmodall y` -- a new optical-model (inverse channel) calculation for every compound nucleus.

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

Task: T5 (physics/hf/CONTRACT.md §7). Acceptance test: KWCOV-B6 (tests/hf/test_kwcov_b6.py).

TALYS routines ported here (file:line of the subroutine statement):
    talysreaction.f90:1 (talysreaction)   lines 88, 102: `basicxs(0, 0)` once (optmodall n) or at the top of every
                                          incident energy (optmodall y), BEFORE `energies`
    multiple.f90:1 (multiple)             line 323: `basicxs(Zcomp, Ncomp)` for every compound nucleus of the cascade
    inverseread.f90:1 (inverseread)       Tl and lmax are filled over ebegin..eend(type) only

What TALYS does with `optmodall y`, and so the port:

1. Every compound nucleus (Zcomp, Ncomp) of the multiple-emission loop -- the initial one (0, 0) included -- decays
   through transmission coefficients computed on ITS OWN residuals (`inverse(Zcomp, Ncomp)`), not through the set of
   the initial compound nucleus's residuals that every nucleus shares by default (`cascade_set`).
2. The initial compound nucleus's PRIMARY decay (comptarget, the binary emission) at the second and later incident
   energies uses the set `basicxs(0, 0)` reads at the top of the energy loop -- before `energies` has set eend(type)
   for the new energy. `inverseread` fills Tl and lmax only up to eend(type), so above the PREVIOUS energy's eend the
   set has Tl = 0 and lmax = 0 (Tjl itself is read to eendmax). That is TALYS-2.25's behaviour, reproduced on purpose
   (`front_set`): stock n + Au-197 at 0.01/0.1/1/5 MeV moves capture at 1 MeV from 144 to 277 mb with it, and a run at
   1 MeV alone does not move at all. The first energy's set is read with grid.f90's eend (= eendmax), i.e. it is the
   default set.

Every set here is the default set's computation (`dens_reference._transmission_build`) with `cn` = the compound
nucleus, then Tl and lmax cut above the eend of the energy TALYS computes it at. The C cascade has one stack plus a
first-nucleus stack, so with `optmodall y` the engine takes the Python cascade (`engine_c._Run.ok` is false).

Default OFF (`optmodall n`): `on()` is false and nothing here is reached.
"""

from __future__ import annotations

from functools import lru_cache

import numpy as np


def on(cas) -> bool:
    """`optmodall y` for this run.

    TALYS: talysreaction.f90:1 (talysreaction)
    Test: tests/hf/test_kwcov_b6.py
    """
    return bool(getattr(cas.options, "flagompall", False))


def eend_at(Zt: int, At: int, enincmax_mev: float, e_inc_mev: float | None) -> dict:
    """eend(type) of energies.f90 at incident energy `e_inc_mev` on the run's grid; eendmax for None (grid.f90:208).

    TALYS: energies.f90:1 (energies)
    Test: tests/hf/test_kwcov_b6.py
    """
    from physics.hf.compound.dens_reference import _eendmax

    if e_inc_mev is None:
        return _eendmax(Zt, At, enincmax_mev)
    return _eend_at(int(Zt), int(At), float(enincmax_mev), float(e_inc_mev))


@lru_cache(maxsize=256)
def _eend_at(Zt: int, At: int, enincmax_mev: float, e_inc_mev: float) -> dict:
    from physics.hf.compound.dens_reference import run_grid, total_energy
    from physics.hf.core.constants import talys_constants
    from physics.hf.core.grids import emission_end
    from physics.hf.projectile import target_mass_index
    from physics.hf.compound.dens_reference import incident_kinematics

    c = talys_constants()
    rg = run_grid(Zt, At, enincmax_mev)
    k0 = rg.options.k0
    eninccm, _ = incident_kinematics(
        e_inc_mev, k0, float(rg.m.mass_amu[target_mass_index()]),
        float(rg.m.specmass[c["parZ"][k0], c["parN"][k0], k0]),
        float(rg.m.redumass_amu[c["parZ"][k0], c["parN"][k0], k0]), rg.options.flagrel)
    ecomp = total_energy(eninccm, rg.s0[k0], rg.target_e)
    eend, _ = emission_end(rg.egrid, rg.maxen, ecomp, {t: rg.s0[t] for t in range(7)}, rg.ebegin,
                           {t: False for t in range(7)})
    return eend


@lru_cache(maxsize=64)
def _base(Zt: int, At: int, enincmax_mev: float, zix: int, nix: int, _key) -> dict:
    from physics.hf.compound.dens_reference import _transmission, _transmission_build

    if (zix, nix) == (0, 0):
        return _transmission(Zt, At, enincmax_mev)
    return _transmission_build(Zt, At, enincmax_mev, None, False, cn=(zix, nix))


def _cut(base: dict, eend: dict) -> dict:
    """inverseread.f90:158-215: Tl and lmax only over ebegin..eend(type); above it they keep basicinitial's 0."""
    out = dict(base)
    for t in range(1, 7):
        tjl, tl, lm = base[t]
        e = int(eend[t])
        if e + 1 >= np.shape(tl)[0]:
            continue
        tl = np.array(tl, copy=True)
        lm = np.array(lm, copy=True)
        tl[e + 1:] = 0.0
        lm[e + 1:] = 0
        out[t] = (tjl, tl, lm)
    return out


@lru_cache(maxsize=256)
def _cached_set(Zt: int, At: int, enincmax_mev: float, zix: int, nix: int, e_key, _key) -> dict:
    base = _base(Zt, At, enincmax_mev, zix, nix, _key)
    if e_key is None:  # grid.f90's eend = eendmax: the set as `basicxs` reads it before the energy loop
        return base
    eend = eend_at(Zt, At, enincmax_mev, e_key)
    return _cut(base, eend)


def _deck_key():
    from physics.hf.input import fitlib
    from physics.hf.omp import ompdeck

    return (fitlib._lines_key(), ompdeck.token())


def cascade_set(cas, zix: int, nix: int) -> dict:
    """The set compound nucleus (zix, nix) decays through in the multiple-emission loop at the cascade's current
    incident energy (multiple.f90:323, after `energies`).

    TALYS: multiple.f90:1 (multiple), inverse.f90:1 (inverse)
    Test: tests/hf/test_kwcov_b6.py
    """
    e = getattr(cas, "_ompall_e", None)
    return _cached_set(int(cas.Zt), int(cas.At), float(cas.enincmax), int(zix), int(nix),
                       None if e is None else float(e), _deck_key())


def front_set(cas) -> dict:
    """The set of the initial compound nucleus's PRIMARY decay at the cascade's current incident energy: read at the
    top of the energy loop, with the previous energy's eend (talysreaction.f90:102 before :105 `energies`).

    TALYS: talysreaction.f90:1 (talysreaction), inverseread.f90:1 (inverseread)
    Test: tests/hf/test_kwcov_b6.py
    """
    e = getattr(cas, "_ompall_e", None)
    prev = None
    if e is not None:
        axis = [float(x) for x in cas.energies]
        i = min(range(len(axis)), key=lambda j: abs(axis[j] - float(e)))
        prev = axis[i - 1] if i > 0 else None
    return _cached_set(int(cas.Zt), int(cas.At), float(cas.enincmax), 0, 0, prev, _deck_key())


def clear() -> None:
    """Drop the per-run sets (a deck or target change).

    TALYS: (none -- cache control)
    Test: tests/hf/test_kwcov_b6.py
    """
    _base.cache_clear()
    _cached_set.cache_clear()
    _eend_at.cache_clear()


__all__ = ["cascade_set", "clear", "eend_at", "front_set", "on"]
