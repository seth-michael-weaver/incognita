"""The `structure_scalars` family: everything `binary`, `channels` and `comptarget` read that is
neither an array of physics nor a grid -- the target's own state, the numerical cut-offs, the
reaction bookkeeping limits and the per-energy switches.

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

Task: NODUMP (physics/hf/CONTRACT.md §7). Acceptance test: A-struct / A-grid / E2E (§6).

Until this module, `engine.ChainedFull` read these off the instrumented run: `Ltarget`, the
target's spin, parity and excitation energy, `popeps`, `xseps`, `maxZ`/`maxN`, `maxchannel`,
`Ninclow`, `specmass`, `parinclude`/`parskip` and the reaction flags. None of them is a dump
quantity in any interesting sense -- they are T3's resolved input record plus one row of T2's
level scheme -- but nothing produced them, so the whole engine still needed a TALYS run per
target. That is the last of the three rows of `hf-e2e.md` §1.

Three of them are resolutions rather than reads, and getting them from `default_options`
unresolved is how a chained run goes quietly wrong:

* **`maxZ`/`maxN` are capped by the target** (nuclides.f90:140-141): the raw record has
  `numZ - 2` / `numN - 2`, and `Zinit - 3` / `Ninit - 3` is smaller for a light target.
  `resolve_structure_defaults` does it; this module only asserts it has been done.
* **`flagfission` is `A > 215`** (input_fissionmodel.f90:78-80), not the `fission n` default, and
  it decides whether `channels.f90` has a fission channel at all.
* **`flagpreeq` / `flaggiant` / `flagwidth` / `flagmulpre` are per incident energy** and come
  from the RESOLVED onsets (`energies.f90:179-210`); `epreeq` and `ewfc` are -1 sentinels in the
  raw record, and `Einc < -1.` is false at every energy, so an unresolved read turns
  pre-equilibrium ON at 1 keV and the width-fluctuation correction OFF everywhere.

`targetE` is `edis(parZ(k0), parN(k0), Ltarget)`, which is 0 for every reference target because
`Ltarget` is 0; it is carried rather than hardcoded because `channels.f90:256` adds it to every
channel's Q-value.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

import numpy as np

from physics.hf.core.constants import talys_constants
from physics.hf.preeq.spin import MAXJPH  # preeqinit.f90's maxJph = 30, a compile-time constant


@dataclass(frozen=True)
class StructureScalars:
    """One target's scalars, run-scoped. Everything here is a pure function of (Z, A, k0) and the
    run's energy grid; nothing is read from a TALYS output file."""

    Z: int
    A: int
    k0: int
    ltarget: int
    targetspin2: int
    target_parity: int
    targete_mev: float
    specmass: float
    popeps_mb: float
    xseps_mb: float
    zinit: int
    ninit: int
    maxz: int
    maxn: int
    maxchannel: int
    ninclow: int
    pespinmodel: int
    maxjph: int
    numj: int
    flagfission: bool
    flaginitpop: bool
    flagchannels: bool
    parinclude: tuple[bool, ...]  # index 0 == type -1, as the dump writes it
    parskip: tuple[bool, ...]  # index 0 == type 0
    options: object
    params: object

    def flags(self, e_inc_mev: float) -> dict[str, bool]:
        """`flagpreeq` / `flaggiant` / `flagwidth` / `flagurr` / `flagmulpre` at one energy.

        TALYS: energies.f90:1 (energies)
        Test: A-struct
        """
        from physics.hf.input.defaults import energy_flags

        return energy_flags(self.options, float(e_inc_mev))


@lru_cache(maxsize=64)
def structure_scalars(Z: int, A: int, energies: tuple[float, ...],
                      k0: int = 1) -> StructureScalars:
    """Every scalar `engine.ChainedFull` used to take from `bin_inputs.txt` / `ch_inputs.txt`.

    `energies` is the run's declared incident energy grid: `resolve_structure_defaults` needs it
    for the onsets, and `Ninclow` counts the energies below `eninclow`.

    TALYS: nuclides.f90:1 (nuclides), input_numerics.f90:1 (input_numerics), grid.f90:1 (grid)
    Test: A-struct / E2E
    """
    from physics.hf.input.defaults import (
        default_options,
        default_params,
        resolve_structure_defaults,
    )
    from physics.hf.structure.levels import discrete_levels
    from physics.hf.structure.masses import masses

    c = talys_constants()
    options = default_options(Z, A)
    params = default_params(Z, A, options)
    m = masses(options, params)
    lt = int(options.Ltarget)
    # the target is the k0 residual of the initial compound nucleus: cascade index (parZ, parN)
    lv = discrete_levels(Z, A, options, m, params)
    options = resolve_structure_defaults(
        options,
        s_projectile_mev=float(m.s_mev[c["parZ"][k0], c["parN"][k0], k0]),
        e_last_level_mev=float(lv.e_mev[int(lv.nlev)]),
        energies_mev=tuple(energies))
    params = default_params(Z, A, options)
    spin = float(lv.all_spin[lt])
    parity = int(lv.all_parity[lt])
    targete = float(lv.all_e_mev[lt])
    # grid.f90:220-233 -- the energies below `eninclow` are run separately; the reference grid
    # starts at 1 keV and `eninclow` resolves to 1e-11 MeV for an incident neutron, so Ninclow
    # is 0 on every reference target. It is counted rather than assumed.
    elow = float(getattr(options, "eninclow_mev", 0.0))
    ninclow = sum(1 for e in energies if e < elow)
    return StructureScalars(
        Z=Z, A=A, k0=k0, ltarget=lt,
        targetspin2=int(round(2.0 * spin)), target_parity=parity, targete_mev=targete,
        specmass=float(m.specmass[c["parZ"][k0], c["parN"][k0], k0]),
        # TALYS holds `popeps`, `xseps` and `Einc` in real(sgl), and both are compared against
        # cross sections in the chain, so the chained arm reads them the way TALYS stores them
        # (`capture_fast._f32` does the same for `Einc`).
        popeps_mb=float(np.float32(options.popeps_mb)),
        xseps_mb=float(np.float32(options.xseps_mb)),
        zinit=int(options.Zinit), ninit=int(options.Ninit),
        maxz=int(options.maxZ), maxn=int(options.maxN),
        maxchannel=int(options.maxchannel), ninclow=ninclow,
        pespinmodel=int(options.pespinmodel), maxjph=MAXJPH,
        numj=int(options.numJ), flagfission=bool(options.flagfission),
        flaginitpop=False,  # an incident-particle run never sets it (input_basicreac.f90)
        flagchannels=True,  # `outchannels`/`channels` is on in every reference run
        parinclude=tuple(_parinclude(options)), parskip=tuple(_parskip(options)),
        options=options, params=params)


def _parinclude(options) -> list[bool]:
    """`parinclude(-1:6)` as the dump writes it (index 0 == type -1).

    `parinclude(type)` is true for every ejectile the run emits; `parinclude(-1)` is the fission
    channel. TALYS's default `ejectiles g n p d t h a` turns all seven on, and -1 follows
    `flagfission`.

    TALYS: input_basicreac.f90:1 (input_basicreac)
    Test: A-struct
    """
    inc = list(getattr(options, "parinclude", [True] * 7))
    if len(inc) != 7:
        inc = [True] * 7
    return [bool(options.flagfission), *[bool(x) for x in inc]]


def _parskip(options) -> list[bool]:
    """`parskip(0:6)` = not `parinclude(type)`."""
    return [not x for x in _parinclude(options)[1:]]
