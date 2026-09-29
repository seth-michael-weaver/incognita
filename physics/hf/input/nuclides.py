"""Nuclide bookkeeping: which residual nuclei (Zix, Nix) a reaction reaches, their Z/N/A, the
particle table and reaction codes.

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

Task: T2 (physics/hf/CONTRACT.md §7). Acceptance test: A-struct (§6).

TALYS routines ported here (file:line of the subroutine/function statement):
    nuclides.f90:1 (nuclides)
    multiple.f90:1 (multiple)
    structure.f90:1 (structure)
    dtheory.f90:1 (dtheory)
    mainout.f90:1 (mainout)
    weakcoupling.f90:1 (weakcoupling)

Index convention (nuclides.f90:127-137): nucleus ``(Zix, Nix)`` has Z = Zinit - Zix and
N = Ninit - Nix, counted from the initial compound nucleus; the residual reached from compound
nucleus ``(Zcomp, Ncomp)`` by emitting particle `type` is ``(Zcomp + parZ(type), Ncomp +
parN(type))``.

Which nuclei TALYS builds structure for
---------------------------------------
`structure(Zix, Nix)` runs (and writes levels<ZZZAAA>.out with `outbasic`) for

1. the binary residuals of the initial compound nucleus, particle types 0..6 in order, skipping
   excluded ejectiles (nuclides.f90:219-228) -- type 0 is the compound nucleus itself;
2. during multiple emission, for every compound nucleus ``Zcomp <= maxZ, Ncomp <= maxN`` whose
   population is at least `popeps` (1e-3 mb), each of its particle-emission residuals
   (multiple.f90:76-128).

Population is a result of the physics, so :func:`residual_nuclei` replaces item 2's population
test with an energy test -- the compound nucleus is counted as populated when the reaction has
enough energy to form it at all (Q-value path through the lightest ejectile combination) -- and
says so. The acceptance test measures how often that approximation disagrees with the dumps.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import cache
from typing import TYPE_CHECKING

import numpy as np

from physics.hf.core.constants import PARN, PARZ, talys_constants

if TYPE_CHECKING:
    from physics.hf.input.defaults import Options
    from physics.hf.structure.masses import Masses

NUMN = 34  # A0_talys_mod.f90:33, numN = 10 + 4 * memorypar

__all__ = [
    "NuclideIndex",
    "nuclide_index",
    "binary_residuals",
    "coulomb_barriers",
    "q_values",
    "residual_nuclei",
    "structure_history",
    "StructureHistory",
    "weak_coupling_core",
]


@dataclass(frozen=True)
class NuclideIndex:
    """Zindex/Nindex/ZZ/NN/AA (nuclides.f90:127-137) as functions of (Zcomp, Ncomp, type)."""

    Zinit: int
    Ninit: int

    def Zindex(self, Zcomp: int, Ncomp: int, typ: int) -> int:
        return Zcomp + PARZ[typ]

    def Nindex(self, Zcomp: int, Ncomp: int, typ: int) -> int:
        return Ncomp + PARN[typ]

    def ZZ(self, Zcomp: int, Ncomp: int, typ: int = 0) -> int:
        return self.Zinit - self.Zindex(Zcomp, Ncomp, typ)

    def NN(self, Zcomp: int, Ncomp: int, typ: int = 0) -> int:
        return self.Ninit - self.Nindex(Zcomp, Ncomp, typ)

    def AA(self, Zcomp: int, Ncomp: int, typ: int = 0) -> int:
        return self.ZZ(Zcomp, Ncomp, typ) + self.NN(Zcomp, Ncomp, typ)


def nuclide_index(options: Options) -> NuclideIndex:
    """The (Zix, Nix) <-> (Z, N, A) map for this reaction.

    TALYS: nuclides.f90:1 (nuclides)
    Test: A-struct
    """
    return NuclideIndex(options.Zinit, options.Ninit)


def _included_types(options: Options) -> tuple[int, ...]:
    from physics.hf.core.constants import particles

    inc = particles(options.k0, flagfission=options.flagfission, flagomponly=options.flagomponly)
    return tuple(t for t in range(0, 7) if inc[t])


def binary_residuals(options: Options) -> list[tuple[int, int]]:
    """(Zix, Nix) of the binary residuals, in TALYS's order: types 0..6 from the initial compound
    nucleus, skipping excluded ejectiles except the photon (nuclides.f90:219-222).

    TALYS: nuclides.f90:1 (nuclides)
    Test: A-struct
    """
    inc = set(_included_types(options))
    out = []
    for typ in range(0, 7):
        if typ != 0 and typ not in inc:
            continue
        out.append((PARZ[typ], PARN[typ]))
    return out


def coulomb_barriers(options: Options) -> tuple[float, ...]:
    """coulbar(type) [MeV] for types 0..6: Ztarget parZ e2 / (1.25 Atarget^(1/3)), single
    precision (nuclides.f90:243).

    TALYS: nuclides.f90:1 (nuclides)
    Test: A-struct
    """
    c = talys_constants()
    f = np.float32
    e2, third = f(c["e2"]), f(c["onethird"])
    out = []
    for typ in range(0, 7):
        num = f(options.Ztarget * PARZ[typ]) * e2
        out.append(float(num / (f(1.25) * f(options.Atarget) ** third)))
    return tuple(out)


def q_values(masses: Masses, options: Options) -> tuple[float, ...]:
    """Q(type) [MeV] of the binary reactions: S(0,0,k0) - S(0,0,type), stored single precision
    (nuclides.f90:240-244; talys.out "Q-values for binary reactions").

    TALYS: nuclides.f90:1 (nuclides)
    Test: A-struct
    """
    k0 = options.k0
    s = masses.s_mev
    return tuple(float(np.float32(float(s[0, 0, k0]) - float(s[0, 0, t]))) for t in range(0, 7))


def _energetic_population(options: Options, masses: Masses):
    c = talys_constants()
    amu = c["amu"]
    k0 = options.k0
    emit = [t for t in _included_types(options) if t >= 1]
    tZ, tN = PARZ[k0], PARN[k0]
    nucmass = masses.mass_amu
    parmass = c["parmass"]

    @cache
    def cheapest(zr: int, nr: int) -> float:
        """min total ejectile rest mass [amu] carrying zr protons and nr neutrons"""
        if zr == 0 and nr == 0:
            return 0.0
        best = float("inf")
        for t in emit:
            if PARZ[t] <= zr and PARN[t] <= nr:
                best = min(best, parmass[t] + cheapest(zr - PARZ[t], nr - PARN[t]))
        return best

    def populated(Zc: int, Nc: int, e_mev: float) -> bool:
        if (Zc, Nc) == (0, 0):
            return True
        if Zc >= nucmass.shape[0] or Nc >= nucmass.shape[1] or float(nucmass[Zc, Nc]) == 0.0:
            return False
        e_total = e_mev * float(masses.specmass[tZ, tN, k0]) + float(masses.s_mev[tZ, tN, k0])
        cost = (float(nucmass[Zc, Nc]) + cheapest(Zc, Nc) - float(nucmass[0, 0])) * amu
        return cost < e_total

    return populated


@dataclass(frozen=True)
class StructureHistory:
    """What TALYS's call sequence does to the structure of each nucleus.

    `order`: nuclei in the order `structure` is called for them. `prior_call`: nuclei whose
    discrete levels had been read more than once when their levels*.out was written for the last
    time (see `structure.levels.discrete_levels(prior_call=...)`); `prior_call_at_structure` the
    same at the moment `structure` ran (gamma*.tot is written only then). `compounds`: compound
    nuclei in the order multiple emission first processes them.
    """

    order: tuple[tuple[int, int], ...]
    prior_call: frozenset
    compounds: tuple[tuple[int, int], ...]
    prior_call_at_structure: frozenset = frozenset()


def structure_history(
    options: Options,
    energies_mev,
    populated=None,
    masses: Masses | None = None,
    flagpop: bool = False,
) -> StructureHistory:
    """Replay TALYS's sequence of `structure`, `levels` and `levelsout` calls.

    1. nuclides.f90:219-228: structure for the binary residuals, types 0..6. Each structure(X)
       reads levels(X), writes levels*.out (outbasic), and its densitymatch calls
       dtheory(X), which reads levels(Zix, min(numN, Nix + 1)) (dtheory.f90:79-80).
    2. mainout.f90:154-166: levelsout for the target and the compound nucleus; both are marked
       written.
    3. per incident energy, ascending, multiple.f90:76-140: every compound nucleus Zcomp <= maxZ,
       Ncomp <= maxN with population >= popeps first gets structure for its emission residuals
       not yet built, then -- with ``outpopulation y`` (`flagpop`) and not yet written --
       levelsout.
    `populated(Zcomp, Ncomp, e_mev) -> bool` is TALYS's population test; the default is the
    energy bound of :func:`residual_nuclei`.

    TALYS: nuclides.f90:1 (nuclides), multiple.f90:1 (multiple), structure.f90:1 (structure),
    dtheory.f90:1 (dtheory), mainout.f90:1 (mainout)
    Test: A-struct
    """
    if populated is None:
        if masses is None:
            from physics.hf.structure.masses import masses as _masses

            masses = _masses(options)
        populated = _energetic_population(options, masses)
    skip_density = options.flagomponly and not options.flagcomp
    inc = _included_types(options)
    reads: dict[tuple[int, int], int] = {}
    last_write: dict[tuple[int, int], int] = {}
    built: list[tuple[int, int]] = []
    exist: set[tuple[int, int]] = set()
    written: set[tuple[int, int]] = set()
    compounds: list[tuple[int, int]] = []

    def levels(zn):
        reads[zn] = reads.get(zn, 0) + 1

    def levelsout(zn):
        last_write[zn] = reads.get(zn, 0)

    at_structure: dict[tuple[int, int], int] = {}

    def structure(zn):
        levels(zn)
        levelsout(zn)
        at_structure[zn] = reads[zn]
        if not skip_density:
            levels((zn[0], min(NUMN, zn[1] + 1)))
        built.append(zn)
        exist.add(zn)

    for typ in range(0, 7):
        if typ != 0 and typ not in inc:
            continue
        zn = (PARZ[typ], PARN[typ])
        structure(zn)
        if typ == options.k0 and (options.Zinit - zn[0] + options.Ninit - zn[1]) % 2 == 1:
            core = weak_coupling_core(options)  # nuclides.f90:227, weakcoupling.f90:93
            if core not in exist:
                levels(core)
    target = (PARZ[options.k0], PARN[options.k0])
    levelsout(target)
    written.add(target)
    if 0 not in inc:
        pass
    elif options.k0 != 0:
        levelsout((0, 0))
        written.add((0, 0))
    seen_comp: set[tuple[int, int]] = set()
    for e in sorted(float(x) for x in np.atleast_1d(energies_mev)):
        for zc in range(0, options.maxZ + 1):
            for nc in range(0, options.maxN + 1):
                if not populated(zc, nc, e):
                    continue
                if (zc, nc) not in seen_comp:
                    seen_comp.add((zc, nc))
                    compounds.append((zc, nc))
                for typ in inc:
                    zn = (zc + PARZ[typ], nc + PARN[typ])
                    if zn not in exist:
                        structure(zn)
                if flagpop and (zc, nc) not in written:
                    levelsout((zc, nc))
                    written.add((zc, nc))
    prior = frozenset(zn for zn, n in last_write.items() if n >= 2)
    prior_s = frozenset(zn for zn, n in at_structure.items() if n >= 2)
    return StructureHistory(tuple(built), prior, tuple(compounds), prior_s)


def weak_coupling_core(options: Options) -> tuple[int, int]:
    """(Zix, Nix) of the even core that weakcoupling.f90 couples an odd-A target to: Z + core for
    odd Z, else N + core (`core` = -1 by default), indices taken with abs() as TALYS does.

    TALYS: weakcoupling.f90:1 (weakcoupling)
    Test: A-struct
    """
    k0 = options.k0
    Z = options.Zinit - PARZ[k0]
    N = options.Ninit - PARN[k0]
    if Z % 2 == 1:
        zc, nc = Z + options.core, N
    else:
        zc, nc = Z, N + options.core
    return abs(options.Zinit - zc), abs(options.Ninit - nc)


def residual_nuclei(
    Z: int,
    A: int,
    e_max_mev,
    options: Options,
    masses: Masses | None = None,
    populated=None,
) -> list[tuple[int, int]]:
    """The (Zix, Nix) list TALYS allocates for this target and maximum incident energy, in TALYS's
    order.

    `e_max_mev` is one energy or the list of incident energies (structure is built in the order
    new compound nuclei become populated as the energy rises). A compound nucleus other than the
    initial one counts as populated at energy E when its formation is energetically open: E in
    the centre of mass plus S(0,0,k0) covers the cheapest way to remove (Zcomp, Ncomp) nucleons
    as n, p, d, t, h, alpha (masses from the grid). TALYS's real criterion is population >=
    popeps (1e-3 mb), which the energy test can only bound from above -- see the module
    docstring. Pass `populated(Zcomp, Ncomp, e_mev) -> bool` to use a known population instead.

    TALYS: nuclides.f90:1 (nuclides), multiple.f90:1 (multiple)
    Test: A-struct
    """
    if (options.Ztarget, options.Atarget) != (Z, A):
        raise ValueError("options are for a different target")
    return list(structure_history(options, e_max_mev, populated, masses).order)
