"""Energy grids: the outgoing emission-energy grid `egrid` and its bins (grid.f90), the incident
kinematics and emission index ranges set per incident energy (energies.f90), the named incident
energy grids (incidentgrid.f90), and the excitation-energy bins of every residual nucleus
(exgrid.f90).

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

Task: T1 (physics/hf/CONTRACT.md §7). Acceptance test: A-grid (§6).

TALYS routines ported here (file:line of the subroutine/function statement):
    grid.f90:1 (grid)
    energies.f90:1 (energies)
    incidentgrid.f90:1 (incidentgrid)
    exgrid.f90:1 (exgrid)

Conventions
-----------
* **Index origin is Fortran's.** Arrays that TALYS declares ``dimension(0:numen)`` (egrid,
  deltaE, Etop, Ebottom) or ``(0:numex)`` (Ex, deltaEx) are returned with position k = Fortran
  index k, so ``egrid[1]`` is TALYS's ``egrid(1)`` = 0.001 MeV and ``egrid[0]`` = 0 is the
  unused slot (masked out). This keeps ported index arithmetic line-comparable (contract §4.2).
* **Grids are discrete structure** (contract §1.3): computed once per case, not differentiated.
  They are computed with TALYS's own kinds: ``egrid``, ``Ex``, ``deltaEx``, ``Etotal`` are
  ``real(sgl)`` and are *accumulated* in single precision (``Eout = Eout + degrid``), which is
  why TALYS prints 0.09999999 and 3.200001; separation energies, Q values and masses are
  ``real(dbl)``. Returned tensors are float64 holding exactly those float32/float64 values.
* Model-dependent upstream inputs that other tasks own (separation energies and specific masses
  from T2, Coulomb barriers from T4, level densities and spin cutoff from T6) are *arguments*
  (contract §5 injection rule); the functions here never compute them.
"""

from __future__ import annotations

from array import array
from dataclasses import dataclass
from functools import lru_cache
from typing import TYPE_CHECKING

import os

import numpy as np
import torch
from torch import Tensor

from physics.hf.core import exgrid_nx2  # MERGED2: `excitation_energies` in C
from physics.hf.core.constants import PARN, PARSYM, PARZ, talys_constants
from physics.hf.core.tensors import DTYPE

if TYPE_CHECKING:
    from physics.hf.core.tensors import CaseBatch
    from physics.hf.input.defaults import Options
    from physics.hf.structure.levels import Levels

f32 = np.float32
f64 = np.float64

# A0_talys_mod.f90 dimensions
NUMEN = int(os.environ.get("INCOGNITA_NUMEN", "260"))  # A0_talys_mod.f90:59; INCOGNITA_NUMEN (PECOLLAPSE): larger only for refined-segment reference runs
NUMENIN = 600  # A0_talys_mod.f90:31
NUMENLOW = 20  # A0_talys_mod.f90:99
NUMLEV = 40  # A0_talys_mod.f90:43
NUMBINS = 20 * (6 - 1)  # A0_talys_mod.f90:66, memorypar = 6
NUMEX = NUMLEV + NUMBINS  # A0_talys_mod.f90:67
# SNBIN: allocation cap of the residual excitation grid (and of the pre-equilibrium spin-factor rows in
# emission.binary), larger than TALYS's numex so `bins` up to NUMBINS_ALLOC works on every path. Arrays are
# returned trimmed to maxex, so at the default `bins 40` nothing downstream changes (OFF bit-identical).
# NUMEX itself is kept: `bins 0` and radwidtheory's grid depend on it.
NUMBINS_ALLOC = 300  # SNBIN3: 200 -> 300 so `bins 240` (+ window sub-bins) fits; arrays trimmed to maxex
NUMEX_ALLOC = NUMLEV + NUMBINS_ALLOC
NUMJ = 40  # A0_talys_mod.f90:68

# input_numerics.f90 / input_basicpar.f90 defaults this module needs until input.defaults lands
SEGMENT_DEFAULT = 1  # input_numerics.f90:70  TODO(T3): read from Options
NBINS0_DEFAULT = 40  # input_numerics.f90:69  TODO(T3)
FLAGEQUI_DEFAULT = True  # input_basicpar.f90:59  TODO(T3)
FLAGEQUISPEC_DEFAULT = False  # input_basicpar.f90:60  TODO(T3)
FLAGREL_DEFAULT = True  # input_basicreac.f90:85  TODO(T3)
TRANSPOWER_DEFAULT = 5  # input_numerics.f90:79  TODO(T3)
NANGLECONT_DEFAULT = 18  # input_numerics.f90:72  TODO(T3)


def _opt(options, name: str, default):
    return getattr(options, name, default) if options is not None else default


# ================================================================================================
# grid.f90: the outgoing energy grid
# ================================================================================================


@dataclass(frozen=True)
class EmissionGrid:
    e_mev: Tensor  # (C, E) outgoing energies, TALYS egrid; position k = Fortran index k
    de_mev: Tensor  # (C, E) bin widths deltaE
    mask: Tensor  # (C, E) bool, True for 1 <= k <= maxen
    etop_mev: Tensor | None = None  # (C, E) Etop
    ebottom_mev: Tensor | None = None  # (C, E) Ebottom
    maxen: Tensor | None = None  # (C,) int64


def emission_limit(enincmax_mev: float, s_k0_mev: float, target_e_mev: float = 0.0) -> float:
    """`Elimit = enincmax + S(0,0,k0) + targetE + 1.`, the energy the outgoing grid must reach
    (grid.f90:120). enincmax and targetE are real(sgl), S is real(dbl); the sum is real(sgl).

    TALYS: grid.f90:1 (grid)
    Test: A-grid
    """
    return float(
        f32(f64(f32(enincmax_mev)) + f64(s_k0_mev) + f64(f32(target_e_mev)) + f64(f32(1.0)))
    )


def egrid_values(
    elimit_mev: float,
    segment: int = SEGMENT_DEFAULT,
    numen: int = NUMEN,
    flagequispec: bool = FLAGEQUISPEC_DEFAULT,
    enincmax_mev: float | None = None,
) -> tuple[np.ndarray, int]:
    """The outgoing energy grid `egrid(0:numen)` and `maxen`, accumulated in single precision
    exactly as grid.f90:118-156 does (step 0.001 MeV rising to 10/segment MeV above 300 MeV).
    Returns (float64 array of length numen+1 holding the float32 values, egrid[0] = 0; maxen).
    With `flagequispec` (keyword `equispec y`) the equidistant grid of grid.f90:147-156 replaces
    it; that branch needs `enincmax_mev`.

    TALYS: grid.f90:1 (grid)
    Test: A-grid
    """
    eg, maxen = _egrid_values(float(elimit_mev), int(segment), int(numen), bool(flagequispec),
                              None if enincmax_mev is None else float(enincmax_mev))
    return eg.copy(), maxen


@lru_cache(maxsize=256)
def _egrid_values(elimit_mev: float, segment: int, numen: int, flagequispec: bool,
                  enincmax_mev: float | None) -> tuple[np.ndarray, int]:
    """COREX: `egrid_values`' build, a pure function of its arguments (`chartrun.KEEP`); callers
    get a copy."""
    egrid = np.zeros(numen + 1, dtype=f32)
    eout = f32(0.0)
    degrid = f32(0.001)
    seg = f32(segment)
    elimit = f32(elimit_mev)
    nen = 0
    while True:
        eout = f32(eout + degrid)
        eeps = f32(eout + f32(1.0e-4))
        if eeps > elimit:
            break
        if nen == numen:
            break
        nen += 1
        egrid[nen] = eout
        if eeps > f32(0.002):
            degrid = f32(0.003)
        if eeps > f32(0.005):
            degrid = f32(0.005)
        if eeps > f32(0.01):
            degrid = f32(0.01)
        if eeps > f32(0.02):
            degrid = f32(0.03)
        if eeps > f32(0.05):
            degrid = f32(0.05)
        if eeps > f32(0.1):
            degrid = f32(f32(0.1) / seg)
        if eeps > f32(2.0):
            degrid = f32(f32(0.2) / seg)
        if eeps > f32(4.0):
            degrid = f32(f32(0.5) / seg)
        if eeps > f32(20.0):
            degrid = f32(f32(1.0) / seg)
        if eeps > f32(40.0):
            degrid = f32(f32(2.0) / seg)
        if eeps > f32(200.0):
            degrid = f32(f32(5.0) / seg)
        if eeps > f32(300.0):
            degrid = f32(f32(10.0) / seg)
    maxen = nen
    if not 1 <= maxen <= numen:
        raise ValueError(f"number of energies {maxen} outside 1..{numen} (grid.f90:143)")
    if flagequispec:
        if enincmax_mev is None:
            raise ValueError("flagequispec needs enincmax_mev")
        maxen = numen - 2
        mhalf = numen // 2
        for k in range(1, mhalf + 1):
            egrid[k] = f32(f32(0.1) * f32(k))
        degrid_eq = f32((f32(enincmax_mev) + f32(12.0) - egrid[mhalf]) / f32(mhalf))
        for k in range(mhalf + 1, numen + 1):
            egrid[k] = f32(egrid[mhalf] + degrid_eq * f32(k - mhalf))
    return egrid.astype(f64), maxen


def emission_bins(egrid: np.ndarray, maxen: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """`deltaE`, `Etop`, `Ebottom` around each outgoing energy (grid.f90:160-172), in single
    precision, arrays of length len(egrid) with Fortran indexing (index 0: deltaE = 0).

    TALYS: grid.f90:1 (grid)
    Test: A-grid
    """
    e = egrid.astype(f32)
    n = len(e)
    de = np.zeros(n, f32)
    top = np.zeros(n, f32)
    bot = np.zeros(n, f32)
    half = f32(0.5)
    for k in range(2, maxen):
        de[k] = half * (e[k + 1] - e[k - 1])
        top[k] = half * (e[k] + e[k + 1])
        bot[k] = half * (e[k] + e[k - 1])
    de[1] = e[1] + half * (e[2] - e[1])
    top[1] = de[1]
    bot[1] = f32(0.0)
    de[0] = f32(0.0)
    de[maxen] = half * (e[maxen] - e[maxen - 1])
    top[maxen] = e[maxen]
    bot[maxen] = half * (e[maxen] + e[maxen - 1])
    return de.astype(f64), top.astype(f64), bot.astype(f64)


def emission_grid(
    cases: CaseBatch, options: Options, *, elimit_mev: Tensor | None = None
) -> EmissionGrid:
    """The outgoing-energy grid TALYS builds for these cases. Units MeV. Position k along E is
    Fortran's egrid(k); k = 0 and k > maxen are masked.

    The grid depends on the case only through `Elimit = enincmax + S(0,0,k0) + targetE + 1`
    (see `emission_limit`), which needs separation energies from structure (T2); pass it as
    `elimit_mev` (C,). Every case shares the same values up to its own maxen.

    TALYS: grid.f90:1 (grid)
    Test: A-grid
    """
    if elimit_mev is None:
        raise ValueError(
            "emission_grid needs elimit_mev (C,): enincmax + S(0,0,k0) + targetE + 1, "
            "see core.grids.emission_limit; S comes from structure (T2)"
        )
    segment = _opt(options, "segment", SEGMENT_DEFAULT)
    equispec = _opt(options, "flagequispec", FLAGEQUISPEC_DEFAULT)
    lim = torch.as_tensor(elimit_mev, dtype=DTYPE).reshape(-1)
    if lim.shape[0] != cases.n:
        raise ValueError(f"elimit_mev has {lim.shape[0]} entries for {cases.n} cases")
    rows = []
    for c in range(cases.n):
        eg, maxen = egrid_values(
            float(lim[c]),
            segment,
            NUMEN,
            equispec,
            float(cases.e_inc_mev.max()) if equispec else None,
        )
        de, top, bot = emission_bins(eg, maxen)
        rows.append((eg, de, top, bot, maxen))
    dev = cases.e_inc_mev.device
    stack = lambda i: torch.tensor(np.stack([r[i] for r in rows]), dtype=DTYPE, device=dev)  # noqa: E731
    maxen = torch.tensor([r[4] for r in rows], dtype=torch.int64, device=dev)
    k = torch.arange(NUMEN + 1, device=dev)
    mask = (k[None, :] >= 1) & (k[None, :] <= maxen[:, None])
    return EmissionGrid(stack(0), stack(1), mask, stack(2), stack(3), maxen)


def charged_particle_begin(
    egrid: np.ndarray,
    maxen: int,
    atarget: int,
    coulbar_mev: dict[int, float],
    parskip: dict[int, bool],
) -> tuple[dict[int, int], dict[int, float]]:
    """`ebegin(type)`, the first outgoing-grid point used for each particle, and `coullimit`
    (grid.f90:176-194): photons and neutrons start at 1; a charged particle starts at the first
    egrid above `0.01 * (1 + A/200) * coulbar(type)`, or 0 if none (or if skipped). Coulomb
    barriers come from the OMP task (T4) and are injected.

    TALYS: grid.f90:1 (grid)
    Test: A-grid
    """
    e = egrid.astype(f32)
    ebegin = {0: 1, 1: 1}
    coullimit: dict[int, float] = {}
    for t in range(2, 7):
        ebegin[t] = 0
        if parskip.get(t, False):
            continue
        coulfactor = f32(f32(0.01) * (f32(1.0) + f32(atarget) / f32(200.0)))
        lim = f32(coulfactor * f32(coulbar_mev[t]))
        coullimit[t] = float(lim)
        for k in range(1, maxen + 1):
            if e[k] > lim:
                ebegin[t] = k
                break
    return ebegin, coullimit


def low_incident_energies(
    eninc_mev: list[float],
    eninclow_mev: float,
    d0_ev: float,
    d0theo_ev: float,
    numenlow: int = NUMENLOW,
) -> dict[str, object]:
    """The low-energy adjustments of the incident grid (grid.f90:210-250): `eninclow` defaults to
    min(D0, 1 MeV) (measured D0, else theoretical), `E1v = 0.2 eninclow` and `eninclow` are
    inserted into the incident energies when the grid starts below them, `Ninclow` counts
    energies below eninclow. D0 in eV. Returns eninc (list), Ninc, eninclow, E1v, Ninclow.

    TALYS: grid.f90:1 (grid)
    Test: A-grid
    """
    eninc = [0.0] + [float(f32(x)) for x in eninc_mev]  # 1-based, eninc(0) unused
    ninc = len(eninc_mev)
    low = f32(eninclow_mev)
    if low == f32(0.0):
        d0 = d0theo_ev if d0_ev == 0.0 else d0_ev
        low = f32(min(f32(f32(d0) * f32(1.0e-6)), f32(1.0)))
    if ninc >= numenlow - 2:
        low = f32(min(low, f32(eninc[numenlow - 2])))
    low = f32(max(low, f32(1.0e-11)))
    e1v = f32(f32(0.2) * low)

    def _insert(val):
        nonlocal ninc, eninc
        j = int(locate_scalar(np.array(eninc, dtype=f64), 1, ninc, float(val)))
        if f32(eninc[j]) / val < f32(0.99):
            ninc += 1
            eninc = eninc[: j + 1] + [float(val)] + eninc[j + 1 :]

    if f32(eninc[1]) < e1v:
        _insert(e1v)
        _insert(low)
    ninclow = sum(1 for k in range(1, ninc + 1) if f32(eninc[k]) < low)
    return {
        "eninc": eninc[1 : ninc + 1],
        "Ninc": ninc,
        "eninclow": float(low),
        "E1v": float(e1v),
        "Ninclow": ninclow,
    }


def angle_grids(nangle: int, nanglecont: int = NANGLECONT_DEFAULT) -> tuple[np.ndarray, np.ndarray]:
    """Discrete and continuum angle grids in degrees, 0..180 (grid.f90:258-265).

    TALYS: grid.f90:1 (grid)
    Test: A-grid
    """
    a = np.array([f32(i) * f32(f32(180.0) / f32(nangle)) for i in range(nangle + 1)], f32)
    b = np.array([f32(i) * f32(f32(180.0) / f32(nanglecont)) for i in range(nanglecont + 1)], f32)
    return a.astype(f64), b.astype(f64)


def transmission_limit(transpower: int = TRANSPOWER_DEFAULT) -> float:
    """`translimit = 1 / 10**transpower` (grid.f90:254), the smallest transmission coefficient
    TALYS keeps. Integer power, single-precision result.

    TALYS: grid.f90:1 (grid)
    Test: A-trans
    """
    return float(f32(f32(1.0) / f32(10**transpower)))


# ================================================================================================
# energies.f90: per incident energy
# ================================================================================================


def incident_kinematics(
    einc_mev: float,
    k0: int,
    target_mass_amu: float,
    specmass: float,
    redumass: float,
    flagrel: bool = FLAGREL_DEFAULT,
) -> tuple[float, float]:
    """Centre-of-mass incident energy `eninccm` [MeV] and wave number `wavenum` [fm^-1]
    (energies.f90:67-77): relativistic for `flagrel` (the default, input_basicreac.f90:85) or
    photons, else non-relativistic with the specific and reduced masses of the incident channel
    (T2 supplies specmass(parZ(k0), parN(k0), k0), redumass(...), tarmass in amu). The results
    are real(sgl), as in TALYS.

    TALYS: energies.f90:1 (energies)
    Test: A-inc
    """
    c = talys_constants()
    amu = f64(c["amu"])
    hbarc = f32(c["hbarc"])
    einc = f32(einc_mev)
    if flagrel or k0 == 0:
        ma1 = f64(c["parmass"][k0])
        ma2 = f64(target_mass_amu)
        ma = ma1 + ma2
        eps = f64(2.0) * ma2 * f64(einc) / amu
        eninccm = f32(amu * eps / (np.sqrt(ma**2 + eps) + ma))
        e_over = f64(einc) / amu
        wavenum = f32(
            amu
            * ma2
            / f64(hbarc)
            * np.sqrt(
                e_over
                * (e_over + f64(2.0) * ma1)
                / ((ma1 + ma2) ** 2 + f64(2.0) * ma2 * f64(einc) / amu)
            )
        )
    else:
        eninccm = f32(f64(einc) * f64(specmass))
        wavenum = f32(np.sqrt(f32(f64(2.0) * amu * f64(redumass) * f64(eninccm))) / hbarc)
    return float(eninccm), float(wavenum)


def total_energy(eninccm_mev: float, s_k0_mev: float, target_e_mev: float = 0.0) -> float:
    """`Etotal = eninccm + S(0,0,k0) + targetE`, the compound-system energy (energies.f90:79);
    single precision.

    TALYS: energies.f90:1 (energies)
    Test: A-grid
    """
    return float(f32(f64(f32(eninccm_mev)) + f64(s_k0_mev) + f64(f32(target_e_mev))))


def emission_end(
    egrid: np.ndarray,
    maxen: int,
    etotal_mev: float,
    s_type_mev: dict[int, float],
    ebegin: dict[int, int],
    parskip: dict[int, bool],
) -> tuple[dict[int, int], int]:
    """`eend(type)`, the last outgoing-grid point energetically open for each particle, and
    `eendhigh` (energies.f90:84-96): the first egrid above Etotal - S(0,0,type), widened to at
    least ebegin + 3 points when the channel is open. `s_type_mev[type]` is S(0,0,type) of the
    compound nucleus (T2).

    TALYS: energies.f90:1 (energies)
    Test: A-grid
    """
    eend: dict[int, int] = {}
    high = 0
    etot = float(f32(etotal_mev))
    # COREX: the scan for the first egrid point above the limit as one comparison per type
    eg = np.asarray(egrid[: maxen + 1]).astype(f32).astype(f64)
    for t in range(0, 7):
        eend[t] = maxen - 1
        if parskip.get(t, False):
            continue
        above = eg > etot - float(s_type_mev[t])
        k = int(above.argmax())
        if above[k]:
            eend[t] = k
        if eend[t] > ebegin[t]:
            eend[t] = max(eend[t], ebegin[t] + 3)
        high = max(high, eend[t])
    return eend, high


def discrete_emission_begin(
    ebottom: np.ndarray,
    etotal_mev: float,
    s_type_mev: dict[int, float],
    edis_mev: dict[int, np.ndarray],
    nlast: dict[int, int],
    ebegin: dict[int, int],
    eend: dict[int, int],
    parskip: dict[int, bool],
) -> tuple[dict[int, int], dict[int, np.ndarray]]:
    """`nendisc(type)`, the emission-grid bin holding the last discrete level, and `eoutdis`, the
    outgoing energy to every discrete level of the residual (energies.f90:103-118).
    `edis_mev[type]` are the level energies of that residual (T2), `nlast[type]` its NL.

    TALYS: energies.f90:1 (energies)
    Test: A-grid
    """
    nendisc: dict[int, int] = {}
    eoutdis: dict[int, np.ndarray] = {}
    etot = f32(etotal_mev)
    for t in range(0, 7):
        nendisc[t] = 1
        if parskip.get(t, False):
            continue
        ed = np.asarray(edis_mev[t], dtype=f32).astype(f64)
        eoutdis[t] = ((float(etot) - float(s_type_mev[t])) - ed).astype(f32).astype(f64)
        if ebegin[t] >= eend[t]:
            continue
        elast = f32(eoutdis[t][nlast[t]])
        if elast > f32(0.0):
            nendisc[t] = int(locate_scalar(ebottom, 1, eend[t], float(elast)))
    return nendisc, eoutdis


def number_of_bins(einc_mev: float, nbins0: int = NBINS0_DEFAULT, numbins: int = NUMBINS) -> int:
    """`nbins`, continuum excitation bins per residual (energies.f90:173-181): the keyword
    value, default 40 (input_numerics.f90:69); with `bins 0`, 30 rising to numbins with energy.

    TALYS: energies.f90:1 (energies)
    Test: A-grid
    """
    if nbins0 != 0:
        return nbins0
    minbins, b = 30, f32(60.0)
    e = f32(einc_mev)
    return minbins + int(f32(numbins - minbins) * e * e / (e * e + b * b))


def incident_energy_flags(
    einc_mev: float,
    *,
    ewfc: float,
    eurr: float,
    epreeq: float,
    emulpre: float,
    eadd: float,
    eaddel: float,
    k0: int = 1,
    flagcpang: bool = False,
    flagang: bool = False,
    flaggiant0: bool = True,
    flagffruns: bool = False,
    flagrpruns: bool = False,
    flaginitpop: bool = False,
) -> dict[str, bool]:
    """The per-incident-energy switches of energies.f90:120-167: width fluctuations
    (Einc <= ewfc), URR output, compound angular distributions, pre-equilibrium and giant
    resonances (Einc >= epreeq), multiple pre-equilibrium, and the added direct/elastic
    contributions. Energies in MeV; thresholds come from input.defaults (T3).

    TALYS: energies.f90:1 (energies)
    Test: A-cn2
    """
    e = f32(einc_mev)
    flags = {
        "flagwidth": bool(e <= f32(ewfc)),
        "flagurr": bool(e <= f32(eurr)),
        "flagcompang": bool((k0 == 1 or flagcpang) and flagang and e <= f32(50.0)),
        "flagpreeq": bool(not e < f32(epreeq)),
        "flagmulpre": bool(not e < f32(emulpre)),
        "flagadd": bool(not e < f32(eadd)),
        "flagaddel": bool(not e < f32(eaddel)),
    }
    flags["flaggiant"] = flags["flagpreeq"] and flaggiant0
    if flagffruns or flagrpruns or flaginitpop:
        flags["flagadd"] = False
        flags["flagaddel"] = False
    return flags


# ================================================================================================
# incidentgrid.f90: named incident-energy grids ("n0-20.grid")
# ================================================================================================


def incident_grid(fname: str) -> list[float] | None:
    """The incident energies of a built-in grid named like `n0-20.grid` or `p10-200.grid`
    (incidentgrid.f90): particle symbol, lowest and highest energy in MeV. Returns None when
    the name is not such a grid (TALYS's `fexist = .false.`). Energies are single precision:
    the 14 fixed low energies, then 0.2 MeV steps widening to 100 MeV; charged particles keep
    only energies within 0.1 MeV above an integer and at least 1 MeV.

    TALYS: incidentgrid.f90:1 (incidentgrid)
    Test: A-grid
    """
    name = fname[:14]
    if not name or name[0] not in PARSYM:
        return None
    ktype = PARSYM.index(name[0])
    pos = name.find("-", 0, 14)
    if pos < 0:
        return None
    pos1 = pos + 1  # Fortran position of '-'
    lenE = None
    for k in range(pos1 + 2, 11):  # do k = pos + 2, 10
        if name[k - 1 : k + 4] == ".grid":
            lenE = k - 1
            break
    if lenE is None:
        return None
    try:
        emin = f32(int(name[1 : pos1 - 1]))
        emax = f32(int(name[pos1:lenE]))
    except ValueError:
        return None
    grid = [
        1.0e-11,
        2.53e-8,
        1.0e-6,
        1.0e-5,
        1.0e-4,
        0.001,
        0.002,
        0.004,
        0.007,
        0.01,
        0.02,
        0.04,
        0.07,
        0.1,
    ]
    e = [f32(x) for x in grid]
    ein, degrid, nen = f32(0.1), f32(0.1), 14
    emaxtalys = f32(1000.0)
    while True:
        ein = f32(ein + degrid)
        eeps = f32(ein + f32(1.0e-4))
        if ein > emaxtalys or nen == NUMENIN:
            break
        nen += 1
        e.append(ein)
        for thr, step in (
            (1.0, 0.2),
            (8.0, 0.5),
            (15.0, 1.0),
            (30.0, 2.0),
            (60.0, 5.0),
            (80.0, 10.0),
            (160.0, 20.0),
            (300.0, 50.0),
            (600.0, 100.0),
        ):
            if eeps > f32(thr):
                degrid = f32(step)
    out = []
    for ein in e:
        eeps = f32(ein + f32(1.0e-4))
        if eeps < emin:
            continue
        if ktype != 1:
            if eeps < f32(1.0):
                continue
            if f32(eeps - f32(int(eeps))) > f32(0.1):
                continue
        if ein <= f32(emax + f32(1.0e-4)):
            out.append(float(ein))
        else:
            break
    return out or None


# ================================================================================================
# exgrid.f90: excitation-energy bins of residual nuclei
# ================================================================================================


@dataclass(frozen=True)
class ExcitationBins:
    # (C, B) excitation energies: discrete levels, then continuum bins; TALYS Ex(Zix,Nix,nex),
    # position k = Fortran nex (nex = 0 is the ground state)
    ex_mev: Tensor
    dex_mev: Tensor  # (C, B) bin widths deltaEx
    nlev: Tensor  # (C,) int64 number of discrete levels in the bin list (TALYS nlevmax/maxex split)
    mask: Tensor  # (C, B) bool
    maxex: Tensor | None = None  # (C,) int64 TALYS maxex(Zix, Nix)


def residual_exmax(
    zcomp: int,
    ncomp: int,
    exmax0: np.ndarray,
    exmax: np.ndarray,
    sep_mev: np.ndarray,
    parskip: dict[int, bool],
) -> tuple[np.ndarray, np.ndarray]:
    """Maximum excitation energy of every residual reachable in one emission from compound
    (Zcomp, Ncomp) (exgrid.f90:88-111): `Exmax0(Zix,Nix) = Exmax0(mother) - S(mother, type)` and
    `Exmax = max(Exmax0, 0)`, for residuals whose Exmax is still 0. When several particles lead
    to the same residual the *last* type in 1..6 wins, as in TALYS. `exmax0`/`exmax` are
    (numZ+1, numN+1) single-precision arrays indexed (Zix, Nix) (modified copies returned);
    `sep_mev` is S (numZ+1, numN+1, 7) from structure (T2).

    TALYS: exgrid.f90:1 (exgrid)
    Test: A-grid
    """
    e0 = exmax0.astype(f32).copy()
    em = exmax.astype(f32).copy()
    zdeep, ndeep = zcomp, ncomp
    types = [t for t in range(1, 7) if not parskip.get(t, False)]
    for t in types:
        zdeep = max(zdeep, zcomp + PARZ[t])
        ndeep = max(ndeep, ncomp + PARN[t])
    # COREX: the cells as array('f') (a stored double is rounded to single precision, as
    # f32(...) is), read back as exact Python floats; the same operations in the same order
    ncol = e0.shape[1]
    e0l = array("f", e0.tobytes())
    eml = array("f", em.tobytes())
    for zix in range(zcomp, zdeep + 1):
        for nix in range(0, ndeep + 1):
            if zix == zcomp and nix == ncomp:
                continue
            k = zix * ncol + nix
            if eml[k] != 0.0:
                continue
            for t in types:
                zm, nm = zix - PARZ[t], nix - PARN[t]
                if zm < 0 or nm < 0:
                    continue
                e0l[k] = e0l[zm * ncol + nm] - float(sep_mev[zm, nm, t])
                v = e0l[k]
                eml[k] = 0.0 if 0.0 > v else v
    return (np.frombuffer(e0l, dtype=f32).reshape(e0.shape).copy(),
            np.frombuffer(eml, dtype=f32).reshape(em.shape).copy())


def residual_q_and_threshold(
    exmax0_mev: float,
    etotal_mev: float,
    s_k0_mev: float,
    target_e_mev: float,
    edis_mev: np.ndarray,
    nlast: int,
    specmass_k0: float,
    ltarget: int = 0,
    is_projectile_residual: bool = False,
    qres0_mev: float = 0.0,
) -> tuple[np.ndarray, np.ndarray]:
    """Q value and threshold incident energy for each discrete level 0..NL of a residual
    (exgrid.f90:124-137): `Qres(0) = S(0,0,k0) + targetE + Exmax0 - Etotal` unless already set,
    `Qres(nex) = Qres(0) - edis(nex)`, `Ethresh = max(-Qres / specmass(k0), 0)`. real(dbl).
    `is_projectile_residual` marks the residual (parZ(k0), parN(k0)) whose Q is targetE when
    the target is excited (`Ltarget /= 0`).

    TALYS: exgrid.f90:1 (exgrid)
    Test: A-struct
    """
    q0 = f64(qres0_mev)
    if q0 == 0.0:
        edif = f32(f32(exmax0_mev) - f32(etotal_mev))  # Edif is real(sgl)
        q0 = f64(s_k0_mev) + f64(f32(target_e_mev)) + f64(edif)
    if ltarget != 0 and is_projectile_residual:
        q0 = f64(f32(target_e_mev))
    ed = np.asarray(edis_mev, dtype=f32)
    q = np.array([q0 - f64(ed[k]) for k in range(nlast + 1)], f64)
    thr = np.maximum(-(q / f64(specmass_k0)), 0.0)
    return q, thr


def excitation_energies(
    edis_mev: np.ndarray,
    nlast: int,
    exmax_mev: float,
    nbins: int,
    aix: int,
    flagequi: bool = FLAGEQUI_DEFAULT,
    etotal_mev: float | None = None,
    thresholds_mev=None,
    snwin: int = 0,
    adapt=None,
) -> tuple[np.ndarray, np.ndarray, int]:
    """Excitation energies `Ex(0:maxex)` and bin widths `deltaEx` of one residual
    (exgrid.f90:141-181): the discrete levels 0..NL (stopping at the first level at or above
    Exmax), then `nexbins` continuum bins between Ex(NL) and Exmax, equidistant by default
    (`equidistant y`, else logarithmic). `nexbins` = nbins for Zix+Nix <= 4 (every binary
    residual), shrinking for deeper residuals. `edis_mev` holds TALYS's edis(0:numlev2) for the
    residual (at least index max(NL, 1)); `aix` = Zix + Nix. For the compound nucleus pass
    `etotal_mev`: TALYS stores Etotal in Ex(maxex + 1). Returns (Ex, deltaEx, maxex) with
    Fortran indexing, single-precision values.

    TALYS: exgrid.f90:1 (exgrid)
    Test: A-grid
    """
    if thresholds_mev:  # SNBIN (`snbin y`): the numpy body pins continuum edges at the thresholds
        return _excitation_energies(edis_mev, nlast, exmax_mev, nbins, aix, flagequi, etotal_mev,
                                    thresholds_mev, snwin, adapt)
    got = exgrid_nx2.excitation_energies(edis_mev, nlast, exmax_mev, nbins, aix, flagequi,
                                         etotal_mev, NUMEX_ALLOC)
    if got is not None:
        return got
    return _excitation_energies(edis_mev, nlast, exmax_mev, nbins, aix, flagequi, etotal_mev)


def _excitation_energies(edis_mev, nlast: int, exmax_mev: float, nbins: int, aix: int,
                         flagequi: bool = FLAGEQUI_DEFAULT, etotal_mev: float | None = None,
                         thresholds_mev=None, snwin: int = 0, adapt=None):
    """`excitation_energies`' reference body (numpy, single precision).

    TALYS: exgrid.f90:1 (exgrid)
    Test: A-grid
    """
    ed = np.zeros(max(len(edis_mev), nlast + 2, 2), f32)
    ed[: len(edis_mev)] = np.asarray(edis_mev, dtype=f32)
    ex = np.zeros(NUMEX_ALLOC + 2, f32)
    dex = np.zeros(NUMEX_ALLOC + 1, f32)
    emax = f32(exmax_mev)
    half = f32(0.5)
    # the discrete levels, elementwise (the same single-precision operations as the loop)
    k = np.arange(nlast + 1)
    stop = np.flatnonzero(ed[1 : nlast + 1] >= emax)
    top = int(stop[0]) if stop.size else nlast  # levels 0..top are on the grid
    ex[: top + 1] = ed[: top + 1]
    kk = k[1 : top + 1]
    dex[kk] = half * (ed[np.minimum(nlast, kk + 1)] - ed[kk - 1])
    dex[0] = half * ed[1]
    if stop.size:
        maxex = top
        return ex[: maxex + 2].astype(f64), dex[: maxex + 1].astype(f64), maxex
    if aix <= 4:
        nexbins = nbins
    elif aix <= 8:
        nexbins = int(f32(f32(1.0) - f32(0.1) * f32(aix - 4)) * f32(nbins))
    else:
        nexbins = nbins // 2
    nexbins = max(nexbins, 2)
    eb = ex[nlast]
    ee = max(emax, f32(eb + f32(0.001)))
    eup = np.zeros(nexbins + 1, f32)
    if flagequi or eb == f32(0.0):
        eup[:] = eb + np.arange(nexbins + 1, dtype=f32) / f32(nexbins) * (ee - eb)
    else:
        lb, le = np.log(eb), np.log(ee)
        for i in range(nexbins + 1):
            eup[i] = np.exp(f32(lb + f32(i) / f32(nexbins) * (le - lb)))
    if adapt is not None:  # BINCONV (`binconv y`): graded continuum mesh, edges at every knot
        eup = binconv_edges(eb, ee, nexbins, thresholds_mev or (), *adapt[:5], chain_mev=adapt[5], amass=adapt[6],
                            fis_mev=adapt[7])
    if thresholds_mev:
        if adapt is None:
            eup = snbin_edges(eup, thresholds_mev)
        if snwin > 0:  # SNBIN3 (`snbin w`): >= snwin bins inside every open window [S(type), Exmax]
            eup = snbin_window_edges(eup, thresholds_mev, snwin)
        nexbins = eup.size - 1
    ex[nlast + 1 : nlast + nexbins + 1] = half * (eup[:-1] + eup[1:])
    dex[nlast + 1 : nlast + nexbins + 1] = eup[1:] - eup[:-1]
    maxex = nlast + nexbins
    if etotal_mev is not None:
        ex[maxex + 1] = f32(etotal_mev)
    return ex[: maxex + 2].astype(f64), dex[: maxex + 1].astype(f64), maxex


SNBIN_ENV = "INCOGNITA_SNBIN"


SNBIN_WINDOW_MIN = 24  # SNBIN3 (`snbin w`): minimum continuum bins inside an open emission window (design study development notes: 3 leaves (n,2n) +4 %, 12-24 converge to <=0.6 %)


def snbin_mode(options=None) -> str:
    """SNBIN mode "n" | "y" | "w" from keyword `snbin` (env `INCOGNITA_SNBIN` when the keyword is off).
    `w` (SNBIN3) = `y` + at least SNBIN_WINDOW_MIN bins inside every open window [S(type), Exmax]
    (`snbin_window_edges`).

    Test: tests/hf/test_snbin.py

    TALYS: (none -- Incognita extension, not a TALYS routine)
    """
    import os

    v = str(getattr(options, "snbin", "n") or "n").strip().lower()
    if v in ("n", "0", ""):
        v = os.environ.get(SNBIN_ENV, "").strip().lower()
    if v in ("y", "1", "on"):
        return "y"
    if v in ("w", "window"):
        return "w"
    if v in ("", "n", "0", "off"):
        return "n"
    raise ValueError(f"snbin: unknown value {v!r} (n|y|w)")


def snbin_window_min(options=None) -> int:
    """SNBIN3: minimum bins per open window for `snbin w`: keyword `snbinwmin` (numerics only).

    TALYS: (none -- Incognita extension, not a TALYS routine)
    Test: none in the public suite
    """
    return int(getattr(options, "snbinwmin", SNBIN_WINDOW_MIN) or SNBIN_WINDOW_MIN)


def snbin_on(options=None) -> bool:
    """SNBIN (off by default): keyword `snbin n|y|w` (env `INCOGNITA_SNBIN`, used when the keyword is off).

    `n` = TALYS: the residual continuum is `nexbins` equidistant (or logarithmic) bins between Ex(NL)
    and Exmax (exgrid.f90:186-203) with no edge at the residual's particle separation energies, so a
    bin that straddles S(type) decays as a whole from its midpoint: densprepare.f90:213-240 weights the
    partly-open transitions by Rboundary (the open fraction of the mother bin) inside the WIDTH, so once
    Rboundary * Gamma_type >> Gamma_gamma the closed part of the bin emits the particle too.
    `y` puts a continuum edge at every S(Zix, Nix, type), type = n, p, d, t, h, a, inside the
    continuum (`snbin_edges`), so no bin straddles an emission threshold. Parameter-free.

    Test: tests/hf/test_snbin.py
    """
    return snbin_mode(options) != "n"


def snbin_edges(eup: np.ndarray, thresholds_mev) -> np.ndarray:
    """SNBIN: continuum bin edges `eup` (float32, increasing) with an edge at every threshold strictly
    inside (eup[0], eup[-1]). Each threshold moves the NEAREST free interior edge onto itself (bin count
    unchanged, neighbouring widths within [w/2, 3w/2]); if that edge is an end point or already pinned by
    another threshold, the threshold is inserted as a new edge (+1 bin). Pure bookkeeping, no parameter.

    Test: tests/hf/test_snbin.py

    TALYS: (none -- Incognita extension, not a TALYS routine)
    """
    e = [f32(x) for x in eup]
    pinned = {0, len(e) - 1}
    for s in sorted({f32(t) for t in thresholds_mev}):
        if not (e[0] < s < e[-1]):
            continue
        if s in e:
            pinned.add(e.index(s))
            continue
        i = min(range(len(e)), key=lambda k: (abs(float(e[k]) - float(s)), k))
        if i not in pinned:
            e[i] = s
            pinned.add(i)
        else:
            j = int(np.searchsorted(np.asarray(e, f32), s))
            e.insert(j, s)
            pinned = {k + 1 if k >= j else k for k in pinned} | {j}
    return np.asarray(e, f32)


def snbin_window_edges(eup: np.ndarray, thresholds_mev, nmin: int = SNBIN_WINDOW_MIN) -> np.ndarray:
    """SNBIN3: continuum edges `eup` (float32, increasing, thresholds already pinned by `snbin_edges`)
    with at least `nmin` bins inside every open emission window [S, eup[-1]], S a threshold strictly
    inside (eup[0], eup[-1]). A window holding m < nmin bins has each of its m bins split into
    ceil(nmin / m) equal parts; bins below S are untouched, so every pinned edge stays. Windows are
    processed from the highest threshold down. Quadrature only (the decay of a bin from its midpoint
    over [S, Exmax] narrower than ~2 bins), no parameter.

    Test: tests/hf/test_snbin.py

    TALYS: (none -- Incognita extension, not a TALYS routine)
    """
    e = np.asarray(eup, f32)
    for s in sorted({f32(t) for t in thresholds_mev}, reverse=True):
        if not (e[0] < s < e[-1]):
            continue
        i = int(np.searchsorted(e, s, side="left"))  # e[i] >= s; e[i] == s once pinned
        m = e.size - 1 - i if e[i] == s else e.size - i  # bins whose content lies in [S, top]
        if m >= nmin:
            continue
        k = -(-nmin // m)
        lo = i if e[i] == s else i - 1  # an unpinned S: split the bin containing it as well
        new = [e[: lo + 1]]
        for j in range(lo, e.size - 1):
            a, b = e[j], e[j + 1]
            new.append((a + np.arange(1, k + 1, dtype=f32) / f32(k) * (b - a)).astype(f32))
            new[-1][-1] = b
        e = np.concatenate(new).astype(f32)
    return e


BINCONV_ENV = "INCOGNITA_BINCONV"
BINCONV_RATIO = 8.0  # BINCONV: finest width at a knot = base width / ratio (development notes design study)
BINCONV_GROWTH = 0.3  # BINCONV: width grows by this many MeV per MeV of distance from the nearest knot
BINCONV_CAP = 1.0  # BINCONV: widest bin = cap * the TALYS base width (Exmax - Ex(NL)) / nexbins
BINCONV_KNOTS = "btscf"  # b = Ex(NL) (up), t = Exmax (down), s = each threshold S (up), S = each S (both sides),
# c = each multi-chance chain threshold S_x + S_y(daughter) [+ S_z] (up), C = chain (both sides),
# f = each fission barrier height of a fissioning nucleus (both sides); every knot is an edge
BINCONV_KAPPA = 0.35  # BINCONV: widest bin <= kappa * T(U) (Fermi-gas temperature, a = A/8)
BINCONV_CN = 1.0  # BINCONV: the compound nucleus gets the mesh only when Etotal - S_n(CN) >= this (MeV): keV capture untouched


def binconv_mode(options=None) -> bool:
    """BINCONV (off by default): keyword `binconv n|y` (env `INCOGNITA_BINCONV` when the keyword is off).
    `y` replaces TALYS's equidistant residual continuum (exgrid.f90:186-203) by the graded mesh of
    `binconv_edges` (implies the SNBIN threshold edges and the SNBIN3 `snbinwmin` windows), and gives the
    compound nucleus the same mesh (with its own S edges) once its neutron window is >= `binconvcn` MeV.

    Test: tests/hf/test_binconv.py

    TALYS: (none -- Incognita extension, not a TALYS routine)
    """
    import os

    v = str(getattr(options, "binconv", "n") or "n").strip().lower()
    if v in ("n", "0", ""):
        v = os.environ.get(BINCONV_ENV, "").strip().lower()
    if v in ("y", "1", "on"):
        return True
    if v in ("", "n", "0", "off"):
        return False
    raise ValueError(f"binconv: unknown value {v!r} (n|y)")


def binconv_params(options=None) -> tuple:
    """(ratio, growth, cap, knots, kappa) of `binconv y` from keywords binconvr/binconvg/binconvc/binconvk/binconvt.

    TALYS: (none -- Incognita extension, not a TALYS routine)
    Test: none in the public suite
    """
    g = lambda k, d: getattr(options, k, d) if getattr(options, k, None) not in (None, "", 0) else d  # noqa: E731
    return (float(g("binconvr", BINCONV_RATIO)), float(g("binconvg", BINCONV_GROWTH)),
            float(g("binconvc", BINCONV_CAP)), str(g("binconvk", BINCONV_KNOTS)), float(g("binconvt", BINCONV_KAPPA)))


def binconv_edges(eb, ee, nexbins: int, thresholds_mev, ratio: float = BINCONV_RATIO,
                  growth: float = BINCONV_GROWTH, cap: float = BINCONV_CAP, knots: str = BINCONV_KNOTS,
                  kappa: float = 0.0, chain_mev=(), amass: int = 0, fis_mev=()) -> np.ndarray:
    """BINCONV: graded continuum edges on [eb, ee] (float32). The emission integrand of every channel that
    feeds or leaves this nucleus varies fastest at its knots: just above Ex(NL) (high-energy tails of the
    emission into the residual: Coulomb-barrier penetrability and the steep low-U level density), just below
    Exmax (the low-energy end of the evaporation spectrum, epsilon ~ T) and just above each separation energy
    S (the open window of the next emission). Width w(x) = min(cap * w0, w0 / ratio + growth * d(x), kappa * T(x)),
    T(x) = sqrt(max(x, 1 MeV) / (A/8)) the Fermi-gas temperature: populations and widths vary as exp(Ex / T), so the
    midpoint rule's relative error per bin is ~ (w / T)^2 / 24 wherever the bin sits;
    w0 = (ee - eb) / nexbins, d = distance to the nearest knot on its refined side; each segment between
    knots gets n = ceil(int dx / w) bins placed at equal steps of int dx / w (equidistribution), so every
    knot is an edge and the mesh is smooth. Quadrature only, no physics parameter.

    Test: tests/hf/test_binconv.py

    TALYS: (none -- Incognita extension, not a TALYS routine)
    """
    eb, ee = float(eb), float(ee)
    w0 = (ee - eb) / max(int(nexbins), 1)
    h, wmax = w0 / ratio, cap * w0
    ths = sorted({float(f32(t)) for t in thresholds_mev if eb < float(f32(t)) < ee})
    chs = sorted({float(f32(t)) for t in chain_mev if eb < float(f32(t)) < ee} - set(ths)) if (
        "c" in knots or "C" in knots) else []
    fis = sorted({float(f32(t)) for t in fis_mev if eb < float(f32(t)) < ee} - set(ths) - set(chs)) if (
        "f" in knots) else []
    up = ([eb] if "b" in knots else []) + (ths if ("s" in knots or "S" in knots) else []) + chs + fis
    down = ([ee] if "t" in knots else []) + (ths if "S" in knots else []) + (chs if "C" in knots else []) + fis
    cuts = [eb] + sorted(ths + chs + fis) + [ee]
    out = [eb]
    for a, b in zip(cuts[:-1], cuts[1:]):
        x = np.linspace(a, b, 4001)
        d = np.full_like(x, np.inf)
        for k in up:
            d = np.where(x >= k - 1e-12, np.minimum(d, x - k), d)
        for k in down:
            d = np.where(x <= k + 1e-12, np.minimum(d, k - x), d)
        w = np.minimum(wmax, h + growth * np.where(np.isfinite(d), d, np.inf))
        if kappa > 0 and amass > 0:  # temperature bound: w <= kappa * T(U), T = sqrt(U / a), a = A/8, U >= 1 MeV
            w = np.minimum(w, kappa * np.sqrt(np.maximum(x, 1.0) / (amass / 8.0)))
        inv = 1.0 / w
        phi = np.concatenate([[0.0], np.cumsum(0.5 * (inv[1:] + inv[:-1]) * np.diff(x))])
        n = max(1, int(np.ceil(phi[-1] - 1e-9)))
        e = np.interp(np.arange(1, n) / n * phi[-1], phi, x)
        out.extend(e.tolist() + [b])
    e = np.asarray(out, f32)
    e[0], e[-1] = f32(eb), f32(ee)
    e = np.unique(e)
    if e.size - 1 > NUMBINS_ALLOC - 20:
        raise ValueError(f"binconv: {e.size - 1} continuum bins > {NUMBINS_ALLOC - 20} (lower binconvr or raise binconvg)")
    return e


BINQUAD_ENV = "INCOGNITA_BINQUAD"
BINQUAD_NODES = 3  # BINQUAD: Gauss-Legendre nodes per smooth piece of the eps distribution
BINQUAD_MTILT = 1.0  # BINQUAD: weight of the mother bin's own d ln rho / dE in its population shape (0 = uniform)
BINQUAD_RTILT = 1.0  # BINQUAD: weight of the residual bin's d ln rho / dE (0 = uniform levels)


def binquad_mode(options=None) -> bool:
    """BINQUAD (off by default): keyword `binquad n|y` (env `INCOGNITA_BINQUAD` when the keyword is off).
    `y` replaces densprepare's midpoint transmission T_l(eps_mid) and triangle Rboundary of every particle
    exit (primary and cascade, continuum and discrete rows) by a Gauss-Legendre average of T_l over the
    population-weighted eps distribution of the mother bin x residual bin (native/binquad.h): level
    densities rho(y) ~ exp(beta y), mother population ~ exp(alpha x), slopes from each nucleus's own
    rhogrid. Photon exits keep TALYS's numbers. Native engine (engine_c / nativex) only: the Python
    reference paths refuse it.

    Test: tests/hf/test_binquad.py

    TALYS: (none -- Incognita extension, not a TALYS routine)
    """
    import os

    v = str(getattr(options, "binquad", "n") or "n").strip().lower()
    if v in ("n", "0", ""):
        v = os.environ.get(BINQUAD_ENV, "").strip().lower()
    if v in ("y", "1", "on"):
        return True
    if v in ("", "n", "0", "off"):
        return False
    raise ValueError(f"binquad: unknown value {v!r} (n|y)")


def binquad_params(options=None) -> tuple:
    """(nodes, mother tilt, residual tilt, sub-points) of `binquad y` from keywords
    binquadq/binquadm/binquadr/binquads. Mother tilt -1 = the mother as a point at its centre, -2 = at its
    rho-weighted centroid; residual tilt < 0 = no transmission quadrature; sub-points S > 1 = each mother
    bin decays from S Gauss-Legendre points of the bin (uniform population, weights w_q / 2), each with
    its own branching ratios.

    TALYS: (none -- Incognita extension, not a TALYS routine)
    Test: none in the public suite
    """
    def g(k, d):
        v = getattr(options, k, None)
        return d if v is None or v == "" else v

    return (int(g("binquadq", BINQUAD_NODES)), float(g("binquadm", BINQUAD_MTILT)),
            float(g("binquadr", BINQUAD_RTILT)), int(g("binquads", 1)))


def binquad_sub(options=None) -> int:
    """BINQUAD sub-points per mother bin (1 = off).

    TALYS: (none -- Incognita extension, not a TALYS routine)
    Test: none in the public suite
    """
    return binquad_params(options)[3] if binquad_mode(options) else 1


def binquad_photon(options=None) -> int:
    """BINQUAD2: Gauss-Legendre nodes of the photon-exit quadrature over each residual continuum bin
    (keyword `binquadp`, rho-tilted like the particle exits; 0 = TALYS's bin-centre Egamma).

    TALYS: (none -- Incognita extension, not a TALYS routine)
    Test: none in the public suite
    """
    if not binquad_mode(options):
        return 0
    q = int(getattr(options, "binquadp", 0) or 0)
    return q if 0 < q <= 4 else 0


def binquad_wkb(options=None) -> int:
    """BINQUAD4: nodes of the WKB fission-penetrability table (keyword `binquadw`; 0 = TALYS).

    wkb.f90 tabulates T_WKB(U) at nbinswkb = nbins0 energies (3/4 of them up to the highest barrier,
    then 0.2 MeV steps) and twkbint interpolates it log-linearly, so the sub-barrier fission width
    of every fissioning nucleus moves with the continuum bin count `bins`: at 40 bins the nodes are
    ~0.2 MeV apart, comparable to hbar*omega/2pi, the scale on which T_WKB changes by e. `binquadw N`
    builds the table with N nodes whatever `bins` is (only under `binquad y`).

    TALYS: (none -- Incognita extension, not a TALYS routine)
    Test: none in the public suite
    """
    if not binquad_mode(options):
        return 0
    n = int(getattr(options, "binquadw", 0) or 0)
    return n if n >= 4 else 0


def binquad_knots(options=None) -> int:
    """BINQUAD2: `binquadk` bitmask of the in-bin knots that cut a mother bin into smooth pieces.

    TALYS: (none -- Incognita extension, not a TALYS routine)
    Test: none in the public suite
    """
    return int(getattr(options, "binquadk", 0) or 0) if binquad_mode(options) else 0


def binquad_sync(options=None) -> None:
    """Push `binquad` (on/off, nodes, tilts) into the native kernels' globals before a native decay call.

    TALYS: (none -- Incognita extension, not a TALYS routine)
    Test: none in the public suite
    """
    from physics.hf.native import nativex
    from physics.hf import kevleak2

    kevleak2.sync(options)  # KEVLEAK3: the run's kevleak2 value for the C kernels (INCOGNITA_KEVLEAK2_EFF)

    on = binquad_mode(options)
    q, mt, rt, sub = binquad_params(options) if on else (BINQUAD_NODES, BINQUAD_MTILT, BINQUAD_RTILT, 1)
    so = nativex.lib()
    if so is not None:
        if not hasattr(so, "nx_set_binquad"):
            if on:
                raise RuntimeError("binquad: libnativex.so has no nx_set_binquad (rebuild)")
        else:
            import ctypes

            f = so.nx_set_binquad
            f.argtypes = [ctypes.c_int64, ctypes.c_int64, ctypes.c_double, ctypes.c_double]
            f.restype = None
            f(int(on), int(q), float(mt), float(rt))
            if hasattr(so, "nx_set_binquad_sub"):
                fs = so.nx_set_binquad_sub
                fs.argtypes = [ctypes.c_int64]
                fs.restype = None
                fs(int(sub) if on else 1)
            elif on and sub > 1:
                raise RuntimeError("binquad: libnativex.so has no nx_set_binquad_sub (rebuild)")
    from physics.hf import engine_c

    ce = engine_c.lib()
    if ce is not None:
        if not hasattr(ce, "ce_set_binquad"):
            if on:
                raise RuntimeError("binquad: libengdecay.so has no ce_set_binquad (rebuild)")
        else:
            import ctypes

            f = ce.ce_set_binquad
            f.argtypes = [ctypes.c_int64, ctypes.c_int64, ctypes.c_double, ctypes.c_double]
            f.restype = None
            f(int(on), int(q), float(mt), float(rt))
    elif on:
        raise RuntimeError("binquad: native engine only (engine_c lib missing)")


def excitation_bins(
    cases: CaseBatch,
    zix: int,
    nix: int,
    levels: Levels,
    options: Options,
    *,
    exmax_mev: Tensor | None = None,
    nlast: int | None = None,
    nbins: int | None = None,
) -> ExcitationBins:
    """Discrete levels plus continuum bins of residual (Zix, Nix) for each case: `Ex` and bin size
    as written in binE*.out meta (`number of continuum bins`, `continuum bin size [MeV]`,
    `maximum excitation energy [MeV]`). Units MeV. Position k = Fortran nex.

    Exmax (C,) is energetics that needs separation energies (T2), so it is injected
    (`residual_exmax` computes it from S); `nlast` is the residual's NL (default: all levels in
    `levels`); `nbins` defaults to `number_of_bins` at each case's incident energy.

    TALYS: exgrid.f90:1 (exgrid)
    Test: A-grid
    """
    if exmax_mev is None:
        raise ValueError("excitation_bins needs exmax_mev (C,), see core.grids.residual_exmax")
    edis = levels.e_mev.detach().cpu().numpy()
    nl = int(len(edis) - 1) if nlast is None else int(nlast)
    equi = _opt(options, "flagequi", FLAGEQUI_DEFAULT)
    nb0 = _opt(options, "nbins0", NBINS0_DEFAULT)
    exm = torch.as_tensor(exmax_mev, dtype=DTYPE).reshape(-1)
    rows = []
    for c in range(cases.n):
        nb = nbins if nbins is not None else number_of_bins(float(cases.e_inc_mev[c]), nb0)
        ex, dex, maxex = excitation_energies(edis, nl, float(exm[c]), nb, zix + nix, equi)
        rows.append((ex[: maxex + 1], dex, maxex))
    width = max(r[2] for r in rows) + 1
    dev = cases.e_inc_mev.device
    ex_t = torch.zeros((cases.n, width), dtype=DTYPE, device=dev)
    dex_t = torch.zeros_like(ex_t)
    mask = torch.zeros((cases.n, width), dtype=torch.bool, device=dev)
    for c, (ex, dex, maxex) in enumerate(rows):
        ex_t[c, : maxex + 1] = torch.as_tensor(ex, dtype=DTYPE)
        dex_t[c, : maxex + 1] = torch.as_tensor(dex, dtype=DTYPE)
        mask[c, : maxex + 1] = True
    maxex_t = torch.tensor([r[2] for r in rows], dtype=torch.int64, device=dev)
    nlev = torch.clamp(maxex_t, max=nl)
    return ExcitationBins(ex_t, dex_t, nlev, mask, maxex_t)


def max_spin_index(spincut: Tensor, numj: int = NUMJ) -> Tensor:
    """`maxJ(Zix,Nix,nex) = min(int(4 + 3 sqrt(spincut)), numJ)` (exgrid.f90:199-200), the
    highest spin index carried in each continuum bin. `spincut` (spin-cutoff factor sigma^2 at
    the bin centre, a = A/8) comes from the level-density task (T6). int64.

    TALYS: exgrid.f90:1 (exgrid)
    Test: A-grid
    """
    s = spincut.to(torch.float32)
    return torch.clamp((4.0 + 3.0 * torch.sqrt(s)).to(torch.int64), max=numj)


def continuum_bin_edges(ex_mev: Tensor, dex_mev: Tensor) -> tuple[Tensor, Tensor]:
    """Lower and upper edges `Ex1min = Ex - dEx/2`, `Ex1plus = Ex + dEx/2` of a continuum bin
    (exgrid.f90:191-193), where the level density is sampled for `integrated_density`. MeV.

    TALYS: exgrid.f90:1 (exgrid)
    Test: A-ld
    """
    return ex_mev - 0.5 * dex_mev, ex_mev + 0.5 * dex_mev


def integrated_density(rho1: Tensor, rho2: Tensor, rho3: Tensor, dex_mev: Tensor) -> Tensor:
    """`rhogrid`, the level density integrated over a continuum bin (exgrid.f90:208-222), from
    rho(J, parity) [MeV^-1] at the lower edge, centre and upper edge (T6 supplies them): the
    exact integral of an exponential through each half bin,
    `0.5 dEx [(r1 - r2)/(ln r1 - ln r2) + (r2 - r3)/(ln r2 - ln r3)]`, with r1 and r3 scaled by
    (1 + 1e-10) as TALYS does to avoid 0/0; falls back to `dEx r2` when a log difference
    vanishes. Dimensionless (number of levels). Differentiable in the densities; zero densities
    are safe in the backward pass.

    TALYS: exgrid.f90:1 (exgrid)
    Test: A-ld
    """
    if (not torch.is_grad_enabled() and rho1.device.type == "cpu" and rho2.device.type == "cpu"
            and rho3.device.type == "cpu" and rho2.dtype == torch.float64):
        # COREX: off the graph, the same operations in numpy
        a1, a2, a3 = rho1.numpy(), rho2.numpy(), rho3.numpy()
        dx = dex_mev.numpy() if isinstance(dex_mev, Tensor) else np.asarray(dex_mev)
        with np.errstate(all="ignore"):
            q1 = a1 * (1.0 + 1.0e-10)
            q3 = a3 * (1.0 + 1.0e-10)
            pos = (q1 > 0) & (a2 > 0) & (q3 > 0)
            l1 = np.log(np.where(pos, q1, 1.0))
            l2 = np.log(np.where(pos, a2, 1.0))
            l3 = np.log(np.where(pos, q3, 1.0))
            ok = pos & (l2 != l1) & (l2 != l3)
            d12 = np.where(ok, l1 - l2, 1.0)
            d23 = np.where(ok, l2 - l3, 1.0)
            exact = 0.5 * dx * ((q1 - a2) / d12 + (a2 - q3) / d23)
            return torch.as_tensor(np.asarray(np.where(ok, exact, dx * a2)))
    one = torch.ones((), dtype=rho2.dtype, device=rho2.device)
    r1 = rho1 * (1.0 + 1.0e-10)
    r3 = rho3 * (1.0 + 1.0e-10)
    pos = (r1 > 0) & (rho2 > 0) & (r3 > 0)
    l1 = torch.log(torch.where(pos, r1, one))
    l2 = torch.log(torch.where(pos, rho2, one))
    l3 = torch.log(torch.where(pos, r3, one))
    ok = pos & (l2 != l1) & (l2 != l3)
    d12 = torch.where(ok, l1 - l2, one)
    d23 = torch.where(ok, l2 - l3, one)
    exact = 0.5 * dex_mev * ((r1 - rho2) / d12 + (rho2 - r3) / d23)
    return torch.where(ok, exact, dex_mev * rho2)


# ================================================================================================
# helpers shared with numerics (kept here to avoid an import cycle for scalar use)
# ================================================================================================


def locate_scalar(xx: np.ndarray, ib: int, ie: int, x: float) -> int:
    """Scalar `locate` on a Fortran-indexed array (see core.numerics.locate for the batched,
    documented version); used by the grid set-up loops.

    TALYS: locate.f90:1 (locate)
    Test: A-grid
    """
    if ib > ie:
        return 0
    x = f32(x)
    xs = np.asarray(xx[: ie + 1], dtype=f32)  # COREX: the search reads positions ib..ie only
    jl, ju = ib - 1, ie + 1
    ascend = xs[ie] >= xs[ib]
    while ju - jl > 1:
        jm = (ju + jl) // 2
        if ascend == (x >= xs[jm]):
            jl = jm
        else:
            ju = jm
    if x == xs[ib]:
        return ib
    if x == xs[ie]:
        return ie - 1
    return jl
