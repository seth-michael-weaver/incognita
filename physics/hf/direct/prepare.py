"""Assemble the structure, grids and injected DWBA cross sections one direct calculation needs.

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

Task: T12 (physics/hf/CONTRACT.md §7). Acceptance test: A-mult (§6).

TALYS routines ported here (file:line of the subroutine/function statement):
    direct.f90:1 (direct)

`direct.f90` itself is four guards and four calls; this module is the guards plus the wiring
the driver would otherwise do. Everything upstream is the landed ports -- T2's levels and
deformation, T3's options and params, T1's energy grid and `eoutdis` -- except the per-level
DWBA cross sections, which are injected from `directE*.out` until T13's ECIS lands
(contract §5).
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

import numpy as np
import torch

from physics.hf.core.constants import talys_constants
from physics.hf.core.grids import (
    NUMEN,
    charged_particle_begin,
    discrete_emission_begin,
    egrid_values,
    emission_bins,
    emission_end,
    emission_limit,
    incident_kinematics,
    total_energy,
)
from physics.hf.core.tensors import DTYPE
from physics.hf.direct import reference as dref
from physics.hf.direct.dwba import CollectiveStructure
from physics.hf.input.defaults import (
    default_options,
    default_params,
    energy_flags,
    resolve_structure_defaults,
)
from physics.hf.input.nuclides import coulomb_barriers, weak_coupling_core
from physics.hf.structure.deformation import deformation, weak_coupling
from physics.hf.structure.levels import NUMLEV2, discrete_levels
from physics.hf.structure.masses import masses


@dataclass(frozen=True)
class DirectCase:
    """One (target, incident energy): structure, grid and the flags `energies.f90` derives."""

    target: str
    Z: int
    A: int
    e_inc_mev: float
    eninccm_mev: float
    etotal_mev: float
    struct: CollectiveStructure
    eoutdis_mev: np.ndarray  # (numlev2+1,) for the k0 channel
    egrid_mev: np.ndarray  # (numen+1,)
    deltae_mev: np.ndarray  # (numen+1,)
    ebegin: int
    eend: int
    maxen: int
    flaggiant: bool
    options: object
    params: object

    @property
    def grid_mask(self) -> torch.Tensor:
        k = torch.arange(len(self.egrid_mev))
        return (k >= self.ebegin) & (k <= min(self.eend, self.maxen))


def parse_target(target: str) -> tuple[int, int]:
    """ "Ni058" -> (28, 58).

    TALYS: constants.f90:1 (constants)
    Test: A-mult
    """
    from physics.hf.preeq.prepare import parse_target as _pt

    return _pt(target)


@lru_cache(maxsize=32)
def _base(target: str, energies: tuple[float, ...]):
    Z, A = parse_target(target)
    options = default_options(Z, A)
    params = default_params(Z, A, options)
    m = masses(options, params)
    c = talys_constants()
    k0 = options.k0
    Zr, Ar = Z - c["parZ"][k0], A + 1 - c["parA"][k0]  # residual of the k0 channel = the target
    lev = discrete_levels(Zr, Ar, options, m, params)
    dfm = deformation(Zr, Ar, options, lev, m, params)
    if Ar % 2 == 1:  # nuclides.f90:227 -- an odd-A target gets its deformations by weak coupling
        zc, nc = weak_coupling_core(options)
        cz = options.Zinit - zc
        ca = cz + options.Ninit - nc
        clev = discrete_levels(cz, ca, options, m, params)
        dfm = weak_coupling(dfm, lev, deformation(cz, ca, options, clev, m, params), clev, options)
    # nuclides.f90:251-259 -- `ewfc`, `eurr` and `epreeq` are -1 sentinels in the raw record and
    # `energy_flags` raises on them, so `case` would fall back to `flaggiant0` (true at EVERY
    # energy) and put a giant-resonance block below the pre-equilibrium onset, where TALYS
    # writes none. This call used to be guarded by `except TypeError` on a signature that never
    # matched, so the fallback was the only path taken (NODUMP).
    options = resolve_structure_defaults(
        options,
        s_projectile_mev=float(m.s_mev[c["parZ"][k0], c["parN"][k0], k0]),
        e_last_level_mev=float(lev.e_mev[int(lev.nlev)]),
        energies_mev=tuple(energies))
    edis = np.zeros(NUMLEV2 + 1)
    jdis = np.zeros(NUMLEV2 + 1)
    parlev = np.ones(NUMLEV2 + 1)
    n = lev.nlevmax2
    edis[: n + 1] = lev.all_e_mev.numpy()
    jdis[: n + 1] = lev.all_spin.numpy()
    parlev[: n + 1] = lev.all_parity.numpy()
    from physics.hf.direct.dwba import coupled_levels

    struct = CollectiveStructure(
        Atarget=A,
        nlast=int(lev.nlev),
        deftype=dfm.deftype,
        edis_mev=edis,
        jdis=jdis,
        parlev=parlev,
        deform=dfm.deform.copy(),
        colltype=dfm.colltype,
        cc_levels=coupled_levels(dfm, options.flagspher),
    )
    return Z, A, options, params, m, struct


@lru_cache(maxsize=32)
def _grid(target: str, energies: tuple[float, ...]):
    """NATIVEX2: the part of `case` that does not depend on the incident energy -- the emission
    grid up to the run's largest energy, its bins and the charged-particle begin -- built once per
    (target, declared grid) instead of at every energy; the same calls on the same arguments.
    Dropped between targets with every other `lru_cache` (`chartrun.drop_target_caches`).

    TALYS: grid.f90:1 (grid), energies.f90:1 (energies)
    Test: A-mult
    """
    Z, A, options, params, m, struct = _base(target, energies)
    k0 = options.k0
    parskip = {t: False for t in range(7)}
    s0 = {t: float(m.s_mev[0, 0, t]) for t in range(7)}
    eg, maxen = egrid_values(
        emission_limit(max(energies), s0[k0], 0.0),
        options.segment,
        NUMEN,
        options.flagequispec,
        None,
    )
    de, _etop, ebot = emission_bins(eg, maxen)
    coulbar = coulomb_barriers(options)
    ebegin, _ = charged_particle_begin(eg, maxen, A, {t: coulbar[t] for t in range(7)}, parskip)
    return s0, eg, maxen, de, ebot, ebegin, parskip


@lru_cache(maxsize=256)
def case(target: str, e_inc_mev: float, energies: tuple[float, ...] | None = None) -> DirectCase:
    """Build the `DirectCase` for one incident energy, on ported inputs only.

    NATIVEX2: cached per (target, energy, declared grid) like `_base` -- a chained run asks for
    the same case from `compound.pop_reference._giant` and `direct.chain.direct_result`. The
    returned case is shared; treat it as read-only. Dropped between targets with every other
    `lru_cache` (`chartrun.drop_target_caches`).

    TALYS: direct.f90:1 (direct)
    Test: A-mult
    """
    energies = tuple(energies or dref.energies_with_direct(target))
    Z, A, options, params, m, struct = _base(target, energies)
    c = talys_constants()
    k0 = options.k0
    s0, eg, maxen, de, ebot, ebegin, parskip = _grid(target, energies)
    eninccm, _ = incident_kinematics(
        e_inc_mev,
        k0,
        float(m.mass_amu[0, 1]),
        float(m.specmass[c["parZ"][k0], c["parN"][k0], k0]),
        float(m.redumass_amu[c["parZ"][k0], c["parN"][k0], k0]),
        options.flagrel,
    )
    etotal = total_energy(eninccm, s0[k0], 0.0)
    eend, _ = emission_end(eg, maxen, etotal, s0, ebegin, parskip)
    # eoutdis runs over 0..numlev2 (energies.f90:166-168), past the discrete levels the
    # residual actually uses, because the collective continuum lives up there.
    _nd, eout = discrete_emission_begin(
        ebot,
        etotal,
        s0,
        {t: struct.edis_mev if t == k0 else struct.edis_mev[: struct.nlast + 1] for t in range(7)},
        {t: struct.nlast for t in range(7)},
        ebegin,
        eend,
        parskip,
    )
    try:
        flaggiant = energy_flags(options, e_inc_mev)["flaggiant"]
    except ValueError:
        flaggiant = bool(options.flaggiant0)
    return DirectCase(
        target=target,
        Z=Z,
        A=A,
        e_inc_mev=float(e_inc_mev),
        eninccm_mev=eninccm,
        etotal_mev=etotal,
        struct=struct,
        eoutdis_mev=np.asarray(eout[k0]),
        egrid_mev=eg,
        deltae_mev=de,
        ebegin=int(ebegin[k0]),
        eend=int(eend[k0]),
        maxen=int(maxen),
        flaggiant=flaggiant,
        options=options,
        params=params,
    )


def injected_cross_sections(
    cs: DirectCase, levels, dump: dref.DirectDump
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    """DWBA cross sections for `levels`, coupled-channels ones for `struct.cc_levels`, and the
    four giant resonances -- all from the dump.

    This is the injection seam (contract §5): T13's ECIS will produce these two tensors and
    nothing else in `direct` changes. A level the port selected but TALYS did not write gets
    zero, which is also what `directread` would leave it at.

    TALYS: directread.f90:1 (directread)
    Test: A-mult
    """
    by = dict(zip(dump.level.tolist(), dump.xs_mb.tolist(), strict=True))
    xs = torch.tensor([by.get(int(i), 0.0) for i in levels.index], dtype=DTYPE)
    cc = torch.tensor([by.get(int(i), 0.0) for i in cs.struct.cc_levels], dtype=DTYPE)
    return xs, cc, torch.tensor(dump.xsgrcoll_mb, dtype=DTYPE)
