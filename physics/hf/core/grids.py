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
NUMEN = 260  # A0_talys_mod.f90:59
NUMENIN = 600  # A0_talys_mod.f90:31
NUMENLOW = 20  # A0_talys_mod.f90:99
NUMLEV = 40  # A0_talys_mod.f90:43
NUMBINS = 20 * (6 - 1)  # A0_talys_mod.f90:66, memorypar = 6
NUMEX = NUMLEV + NUMBINS  # A0_talys_mod.f90:67
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
    got = exgrid_nx2.excitation_energies(edis_mev, nlast, exmax_mev, nbins, aix, flagequi,
                                         etotal_mev, NUMEX)
    if got is not None:
        return got
    return _excitation_energies(edis_mev, nlast, exmax_mev, nbins, aix, flagequi, etotal_mev)


def _excitation_energies(edis_mev, nlast: int, exmax_mev: float, nbins: int, aix: int,
                         flagequi: bool = FLAGEQUI_DEFAULT, etotal_mev: float | None = None):
    """`excitation_energies`' reference body (numpy, single precision).

    TALYS: exgrid.f90:1 (exgrid)
    Test: A-grid
    """
    ed = np.zeros(max(len(edis_mev), nlast + 2, 2), f32)
    ed[: len(edis_mev)] = np.asarray(edis_mev, dtype=f32)
    ex = np.zeros(NUMEX + 2, f32)
    dex = np.zeros(NUMEX + 1, f32)
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
    ex[nlast + 1 : nlast + nexbins + 1] = half * (eup[:-1] + eup[1:])
    dex[nlast + 1 : nlast + nexbins + 1] = eup[1:] - eup[:-1]
    maxex = nlast + nexbins
    if etotal_mev is not None:
        ex[maxex + 1] = f32(etotal_mev)
    return ex[: maxex + 2].astype(f64), dex[: maxex + 1].astype(f64), maxex


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
