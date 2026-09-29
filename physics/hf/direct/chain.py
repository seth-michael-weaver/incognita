"""The `direct_dwba` family, computed: T13's ECIS instead of `directE*.out`.

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.
ECIS-06 (`ecist.f`) is by J. Raynal and ships inside the TALYS repository under its MIT license.

Task: NODUMP (physics/hf/CONTRACT.md §7). Acceptance test: A-direct / A-mult / E2E (§6).

`direct.prepare.injected_cross_sections` is T12's declared injection seam: the per-level DWBA
cross sections, the coupled-channels ones and the four giant resonances, all read off
`directE*.out`. T13 ported the DWBA (`ecis.dwba`, gate A-direct: n = 13,716, p95 6.0e-3 against
a 5e-2 tolerance) and the coupled-channels off-diagonal (`ecis.incident`, n = 668, p95 7.5e-3),
and ECIS2 made both run on T4's own optical-model parameters instead of the `f6.2` ones
`talys.out` prints. Nothing was left but the wiring, and this module is it:

    xs, xscc, xsgrcoll = computed_cross_sections(case, levels)     # was (case, levels, dump)

Two things the dump supplied besides numbers, and where they come from now:

* **`dump.has_giant`** -- whether TALYS wrote a giant-resonance block at all. It is
  `energy_flags(options, Einc)["flaggiant"]`, which is `flagpreeq and flaggiant0`, i.e. false
  below the pre-equilibrium onset (energies.f90:194-203). `DirectCase.flaggiant` carries it,
  and `direct.prepare.case` now resolves the onsets instead of falling back to `flaggiant0`.
* **which energies have a direct block** -- `dref.energies_with_direct` reads the dump's file
  list. A chained caller declares its own energy grid; `case(target, e, energies)` already
  takes it, and everything here requires it.

**The two halves of `xsdirdisc`.** For a spherical target every direct discrete cross section is
DWBA (`directecis.f90`). For a `colltype R` or `V` target the levels of the coupled band are
solved in the INCIDENT run and copied into `xsdirdisc(k0, indexcc(i))` by
`incidentread.f90:381-394`; those levels have `deform == 0` and `directecis` never sees them.
So the two calls here are not alternatives -- a rotational target needs both, and
`direct_inelastic` scatters them onto the same level axis.
"""

from __future__ import annotations

from functools import lru_cache

import numpy as np
import torch

from physics.hf.core.tensors import DTYPE


@lru_cache(maxsize=64)
def _omp_at(Z: int, A: int, e_inc_mev: float, k0: int = 1):
    """T4's optical-model parameters for the incident channel at one energy, shaped the way
    `ecis.solver` wants them (one row on the energy axis).

    TALYS: optical.f90:1 (optical), omppar.f90:1 (omppar)
    Test: A-omppar
    """
    from physics.hf.omp.parameters import omp_parameters

    # SPEEDP: one `Options`/`Params` pair per target rather than one per energy. Besides the
    # build itself, a fresh pair defeats every downstream cache keyed on their identity
    # (`structure.levels.discrete_levels`, `structure.deformation.deformation`).
    o, p = _defaults(Z, A)
    return omp_parameters(Z, A - Z, k0, torch.tensor([float(e_inc_mev)], dtype=DTYPE), p, o)


@lru_cache(maxsize=8)
def _omp_grid(Z: int, A: int, energies: tuple[float, ...], k0: int = 1):
    """NATIVEX2: `_omp_at` for every energy of the declared grid in one `omp_parameters` call,
    as a dict energy -> single-row `OMPParameters`. The parameters are elementwise in the energy
    (checked bit for bit on the bench 15 and an 11-target sample, actinides with RIPL tables
    included: the table's nodes do not move with the largest energy asked), so a row equals the
    one-energy call.

    TALYS: optical.f90:1 (optical), omppar.f90:1 (omppar)
    Test: A-omppar
    """
    from physics.hf.omp.parameters import COLUMNS, OMPParameters, omp_parameters

    o, p = _defaults(Z, A)
    g = omp_parameters(Z, A - Z, k0, torch.tensor(list(energies), dtype=DTYPE), p, o)
    cols = {c: getattr(g, c).reshape(-1) for c in COLUMNS}
    return {float(e): OMPParameters(**{c: v[i:i + 1] for c, v in cols.items()})
            for i, e in enumerate(energies)}


def _omp_for(Z: int, A: int, e_inc_mev: float, k0: int, energies):
    """The single-row OMP at `e_inc_mev`: a row of `_omp_grid` when the energy is on the declared
    grid and autograd is off, else `_omp_at`."""
    if energies is not None and not torch.is_grad_enabled():
        ax = tuple(float(e) for e in energies)
        row = _omp_grid(Z, A, ax, k0).get(float(e_inc_mev))
        if row is not None:
            return row
    return _omp_at(Z, A, e_inc_mev, k0)


@lru_cache(maxsize=16)
def _defaults(Z: int, A: int):
    from physics.hf.input.defaults import default_options, default_params

    o = default_options(Z, A)
    return o, default_params(Z, A, o)


def _coupled(Z: int, A: int, energies: tuple[float, ...], k0: int = 1):
    """`incident_coupled` over the declared grid for a `colltype R`/`V` target, or None.

    Solved once per target: `incidentecis.f90` runs one ECIS deck per incident energy, and the
    `soswitch` split inside `incident_coupled` needs the whole axis to stitch.

    SPEEDP: a run that computes a subset of the declared grid solves the deck on that subset
    (`preeq.chain.set_energy_subset`), with `lmax` still taken from the WHOLE axis -- `njmax` is
    `incident_coupled`'s only genuinely cross-energy quantity, and letting it follow a subset's
    `e.max()` would be a different calculation rather than the same one scheduled differently.
    The rows are then solved in a smaller batch, which moves them in the last bits (Ca-40: the
    golden's `xsdirdisc`/`xscollcont` by 8e-16, `linalg_solve` over a shorter batch axis).

    TALYS: incidentecis.f90:1 (incidentecis), incidentread.f90:1 (incidentread)
    Test: A-inc / A-direct
    """
    from physics.hf.preeq.chain import energy_subset

    sub = energy_subset(Z, A, energies)
    table = _coupled_cached(Z, A, energies, k0, sub)
    return table


@lru_cache(maxsize=32)
def _coupled_cached(Z: int, A: int, energies: tuple[float, ...], k0: int,
                    wanted: tuple[float, ...] | None):
    from physics.hf.ecis.incident import incident_coupled, njmax_incident
    from physics.hf.ecis.reference import coupled_band
    from physics.hf.input.defaults import default_options
    from physics.hf.omp.schrodinger import PARMASS_AMU

    try:
        band = coupled_band(Z, A)
    except Exception:
        return None
    if band is None or band.get("colltype") not in ("R", "V"):
        return None
    e_ax = torch.tensor(list(energies), dtype=DTYPE)
    nj = njmax_incident(A, PARMASS_AMU[k0], float(e_ax.max()))
    keep = None
    if wanted is not None:
        w = set(wanted)
        keep = torch.tensor([round(float(e), 6) in w for e in energies])
        if bool(keep.all()):
            keep = None
    _inc, res = incident_coupled(
        None, Z, A, e_ax, band, particle=k0, lmax=nj, energy_mask=keep,
        options=band.get("options") or default_options(Z, A))
    idx = range(len(energies)) if keep is None else [i for i, b in enumerate(keep) if b]
    return {round(float(energies[i]), 6): res.sigma_direct_mb[j] for j, i in enumerate(idx)}


def computed_cross_sections(cs, levels, *, refine: int = 4, energies=None,
                            levels_are_dwba: bool = False):
    """`injected_cross_sections`'s three tensors, computed: DWBA per level, coupled-channels per
    `cc_level`, and the four giant resonances.

    Same contract as the injected arm -- a level the port selected but ECIS was not asked about
    gets zero, which is what `directread` would leave it at.

    `levels_are_dwba=True` says `levels` IS `direct_levels` of this case at this energy (as in
    `direct_result`), so the DWBA question reuses it instead of selecting the levels again.

    TALYS: directecis.f90:1 (directecis), directread.f90:1 (directread),
           incidentread.f90:381-394
    Test: A-direct / E2E
    """
    from physics.hf.ecis.dwba import dwba_case, prepare_case

    omp = _omp_for(cs.Z, cs.A, float(cs.e_inc_mev), int(cs.options.k0), energies)
    case = prepare_case(omp, cs.target, float(cs.e_inc_mev), direct_case=cs,
                        levels=levels if levels_are_dwba else None)
    xs_by_level, xsgr = dwba_case(omp, case, refine=refine)
    by = {int(i): float(v) for i, v in zip(case.level_index.tolist(),
                                           xs_by_level.tolist(), strict=True)}
    xs = torch.tensor([by.get(int(i), 0.0) for i in levels.index], dtype=DTYPE)
    grc = torch.zeros(4, dtype=DTYPE)
    if case.gr_which.numel():
        grc[np.asarray(case.gr_which)] = xsgr.to(DTYPE)

    cc_levels = np.asarray(cs.struct.cc_levels).reshape(-1)
    cc = torch.zeros(len(cc_levels), dtype=DTYPE)
    if len(cc_levels) and energies is not None:
        ax = tuple(float(e) for e in energies)
        table = _coupled(cs.Z, cs.A, ax, int(cs.options.k0))
        key = round(float(cs.e_inc_mev), 6)
        if table is not None and key not in table:
            # An energy outside the run's registered subset: fall back to the whole axis rather
            # than let `directread`'s "no ECIS row" zero stand in for one that was never asked.
            table = _coupled_cached(cs.Z, cs.A, ax, int(cs.options.k0), None)
        row = None if table is None else table.get(key)
        if row is not None:
            for k in range(len(cc_levels)):
                if k + 1 < row.shape[0]:
                    cc[k] = row[k + 1]
    return xs, cc, grc


def direct_result(target: str, e_inc_mev: float, energies, *, refine: int = 4):
    """`(DirectResult, has_giant)` for one (target, incident energy), with nothing injected.

    The chained replacement for `compound.pop_reference._giant`, which reads `directE*.out`.

    TALYS: direct.f90:1 (direct), giant.f90:1 (giant)
    Test: A-mult / E2E
    """
    from physics.hf.direct import dwba as D
    from physics.hf.direct import prepare as P

    energies = tuple(float(e) for e in energies)
    cs = P.case(target, e_inc_mev, energies)
    lv = D.direct_levels(cs.struct, cs.eninccm_mev, cs.eoutdis_mev, e_inc_mev, cs.options.k0)
    gr = D.giant_resonance_parameters_of(cs.struct, cs.params)
    xs, xscc, xsgrcoll = computed_cross_sections(cs, lv, refine=refine, energies=energies,
                                                 levels_are_dwba=True)
    res = D.direct(
        cs.struct, gr, lv, xs, xsgrcoll, cs.eoutdis_mev, cs.eninccm_mev,
        torch.as_tensor(cs.egrid_mev, dtype=DTYPE),
        torch.as_tensor(cs.deltae_mev, dtype=DTYPE), cs.grid_mask, xscc,
        flaggiant=cs.flaggiant, elwidth_mev=float(cs.params.at("elwidth")))
    return res, cs.flaggiant


__all__ = ["computed_cross_sections", "direct_result"]
