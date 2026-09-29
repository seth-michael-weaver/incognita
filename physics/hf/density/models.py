"""Total and spin/parity-dependent level densities for every ldmodel: constant temperature + Fermi
gas (Gilbert-Cameron, ldmodel 1), back-shifted Fermi gas (2), generalised superfluid (3), and the
microscopic tables (4-7) with the ctable/ptable adjustment; the theoretical s-wave spacing D0 and
the level-density output tables TALYS writes to ld*.gs.

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

Task: T6 (physics/hf/CONTRACT.md §7). Acceptance test: A-ld (§6).

TALYS routines ported here (file:line of the subroutine/function statement):
    density.f90:1 (density)
    densitytot.f90:1 (densitytot)
    densitytotP.f90:1 (densitytotP)
    gilcam.f90:1 (gilcam)
    fermi.f90:1 (fermi)
    bsfgmodel.f90:1 (bsfgmodel)
    superfluid.f90:1 (superfluid)
    dtheory.f90:1 (dtheory)
    densityout.f90:1 (densityout)

Definitions pinned from densityout.f90 (the question T0 left open in `reference.py`)
------------------------------------------------------------------------------------
In the per-parity blocks of ld*.gs, ``rho(J)`` is ``density(Ex, J, parity)`` -- the level density
of ONE parity and ONE spin J, levels not states; ``rho_observed`` is ``densitytotP``, the total
level density of that parity; ``rho_total`` is ``sum_J (2J+1) rho(J)`` for that parity, i.e. a
state density, which is why it exceeds the sum of the rho(J) columns. For ldmodel <= 3,
``T = sqrt(Ex/a(Sn))`` and ``N_cumulative`` integrates `densitytotP` with the rectangle rule on
edens; for tables both come from the file. The first block (per discrete level) holds
``densitytot`` at each level energy, not a per-parity quantity.
"""

from __future__ import annotations

import math
from collections.abc import Callable
from dataclasses import dataclass

import torch
from torch import Tensor

from physics.hf.core.constants import talys_constants
from physics.hf.core.numerics import locate
from physics.hf.core.tensors import DTYPE
from physics.hf.density.parameters import (
    NUMJ,
    PARDIS,
    LDNucleus,
    _safe,
    _fv,
    _t,
    colenhance,
    ignatyuk,
    spincut,
    spindis,
)
from physics.hf.density.tables import edens_grid

__all__ = [
    "LevelDensity",
    "density",
    "densitytot",
    "densitytotP",
    "gilcam",
    "fermi",
    "bsfgmodel",
    "superfluid",
    "dtheory",
    "density_callable",
    "level_density_on_grid",
    "densityout",
]


@dataclass(frozen=True)
class LevelDensity:
    """rho(Ex, J, parity) [MeV^-1] on the excitation bins of one residual (and barrier ibar)."""

    rho_per_mev: Tensor  # (C, B, Jx, 2)
    ld_parameters: dict  # the ld*.gs header quantities, names as TALYS prints them


def fermi(ld: LDNucleus, ald: Tensor, eex_mev: Tensor, P_mev: Tensor, ibar: int = 0) -> Tensor:
    """Fermi-gas total level density [MeV^-1], exp(2 sqrt(aU)) / (12 sqrt2 sigma a^1/4 U^5/4),
    with U = Eex - P; 1 for U <= 0.

    TALYS: fermi.f90:1 (fermi)
    Test: A-ld
    """
    eex, ald, P = _t(eex_mev), _t(ald), _t(P_mev)
    U = eex - P
    ok = U > 0.0
    Us = _safe(U, ok)
    factor = torch.clamp(2.0 * torch.sqrt(ald * Us), max=700.0)
    sigma = torch.sqrt(spincut(ld, ald, eex, ibar))
    denom = 12.0 * math.sqrt(2.0) * sigma * ald**0.25 * Us**1.25
    return torch.where(ok, torch.exp(factor) / denom, torch.ones_like(eex))


def gilcam(ld: LDNucleus, ald: Tensor, eex_mev: Tensor, P_mev: Tensor, ibar: int = 0) -> Tensor:
    """Gilbert-Cameron total level density [MeV^-1]: Fermi gas above Exmatch, constant temperature
    exp((Eex - E0)/T)/T below.

    TALYS: gilcam.f90:1 (gilcam)
    Test: A-ld
    """
    eex = _t(eex_mev)
    T = ld.T_mev[ibar]
    Ts = T if _fv(T) != 0.0 else _t(1.0)
    ct = torch.exp(torch.clamp((eex - ld.E0_mev[ibar]) / Ts, max=300.0)) / Ts
    return torch.where(eex > ld.Exmatch_mev[ibar], fermi(ld, ald, eex, P_mev, ibar), ct)


def bsfgmodel(ld: LDNucleus, ald: Tensor, eex_mev: Tensor, P_mev: Tensor, ibar: int = 0) -> Tensor:
    """Back-shifted Fermi gas [MeV^-1] with the Grossjean-Feldmeier low-energy regularisation.

    TALYS: bsfgmodel.f90:1 (bsfgmodel)
    Test: A-ld
    """
    eex, ald, P = _t(eex_mev), _t(ald), _t(P_mev)
    sigma = torch.sqrt(spincut(ld, ald, eex, ibar))
    an = 0.5 * ald
    ap = 0.5 * ald
    term = math.exp(1.0) / 24.0 * (an + ap) ** 2 / torch.sqrt(an * ap) / sigma
    U = eex - P
    ok = U > 0.0
    Us = _safe(U, ok)
    invfermi = 1.0 / fermi(ld, ald, eex, P, ibar)
    T2 = Us / ald
    expo = 4.0 * an * ap * T2
    small = expo < 80.0
    deninv = torch.where(small, invfermi + 1.0 / (term * torch.exp(_safe(expo, small, 0.0))), invfermi)
    return torch.where(ok, 1.0 / deninv, term)


def superfluid(ld: LDNucleus, ald: Tensor, eex_mev: Tensor, P_mev: Tensor, ibar: int = 0) -> Tensor:
    """Generalised superfluid model [MeV^-1]: the superfluid phase below Ucrit, Fermi gas above.

    TALYS: superfluid.f90:1 (superfluid)
    Test: A-ld
    """
    eex, ald = _t(eex_mev), _t(ald)
    sqrttwopi = talys_constants()["sqrttwopi"]
    U = eex + ld.pair_mev + ld.Pshift_mev[ibar]
    Ucrit = ld.Ucrit_mev[ibar]
    sub = (U > 0.0) & (U <= Ucrit)
    Uc = Ucrit if _fv(Ucrit) != 0.0 else _t(1.0)
    phi2 = torch.where(sub, 1.0 - U / Uc, torch.full_like(eex, 0.5))
    Df = ld.Dcrit[ibar] * (1.0 - phi2) * (1.0 + phi2) * (1.0 + phi2)
    phi1 = torch.sqrt(phi2)
    Tf = 2.0 * ld.Tcrit_mev * phi1 / torch.log((phi1 + 1.0) / (1.0 - phi1))
    Sf = ld.Scrit[ibar] * ld.Tcrit_mev / Tf * (1.0 - phi2)
    sigma = torch.sqrt(spincut(ld, ald, eex, ibar))
    sf = torch.exp(Sf) / torch.sqrt(Df) / sqrttwopi / sigma
    return torch.where(
        U > 0.0,
        torch.where(U > Ucrit, fermi(ld, ald, eex, P_mev, ibar), sf),
        torch.ones_like(eex),
    )


def _table_interp(edens: Tensor, nendens: int, edensmax: float, eshift: Tensor, lo_hi) -> Tensor:
    """TALYS's table lookup: locate on edens(0..nendens) below Edensmax, else the last interval;
    log-linear when both ends exceed 1, linear otherwise. `lo_hi(nex)` gives the tabulated values."""
    idx = locate(edens[: nendens + 1], eshift.reshape(-1), 0, nendens).reshape(eshift.shape)
    idx = torch.where(eshift <= edensmax, idx, torch.full_like(idx, nendens - 1))
    idx = torch.clamp(idx, 0, nendens - 1)
    eb, ee = edens[idx], edens[idx + 1]
    ldb, lde = lo_hi(idx), lo_hi(idx + 1)
    frac = (eshift - eb) / (ee - eb)
    big = (ldb > 1.0) & (lde > 1.0)
    lb = torch.log(torch.where(big, ldb, torch.ones_like(ldb)))
    le = torch.log(torch.where(big, lde, torch.ones_like(lde)))
    return torch.where(big, torch.exp(lb + frac * (le - lb)), ldb + frac * (lde - ldb))


def _ct_pt(ld: LDNucleus, ibar: int) -> tuple[Tensor, Tensor]:
    return ld.ctable[ibar], ld.ptable_mev[ibar]


def densitytot(ld: LDNucleus, eex_mev: Tensor, ibar: int = 0, ldmodel: int | None = None) -> Tensor:
    """Total level density [MeV^-1] (both parities, levels): the analytical model times the
    collective enhancement for ldmodel <= 3 (or a missing table), the table otherwise, times
    exp(ctable sqrt(Eex - ptable)); 1e-30 below zero.

    TALYS: densitytot.f90:1 (densitytot)
    Test: A-ld
    """
    eex = _t(eex_mev)
    ldmod = ld.ldmodel if ldmodel is None else ldmodel
    ct, pt = _ct_pt(ld, ibar)
    eshift = eex - pt
    valid = (eex >= 0.0) & (eshift > 0.0)
    if ldmod <= 3 or not ld.has_table(ibar):
        ald = ignatyuk(ld, eex, ibar)
        _, _, Kcoll = colenhance(ld, eex, ald, ibar)
        P = ld.delta_mev[ibar]
        if ldmod == 1 or ldmod >= 4:
            dens = gilcam(ld, ald, eex, P, ibar)
        elif ldmod == 2:
            dens = bsfgmodel(ld, ald, eex, P, ibar)
        else:
            dens = superfluid(ld, ald, eex, P, ibar)
        dens = Kcoll * dens
    else:
        tab = ld.tables[ibar]
        dens = _table_interp(
            edens_grid(), tab.nendens, tab.Edensmax_mev, _safe(eshift, valid, 1.0),
            lambda i: tab.ldtottable_per_mev[i],
        )
    expo = torch.clamp(ct * torch.sqrt(_safe(eshift, valid, 0.0)), max=80.0)
    out = torch.exp(expo) * dens
    out = torch.where(valid, out, torch.zeros_like(out))
    return torch.clamp(out, min=1.0e-30)


def densitytotP(
    ld: LDNucleus, eex_mev: Tensor, parity: int, ibar: int = 0, ldmodel: int | None = None
) -> Tensor:
    """Total level density of one parity [MeV^-1]: pardis x densitytot for the analytical models,
    the per-parity table otherwise, times exp(ctable sqrt(Eex - ptable)).

    TALYS: densitytotP.f90:1 (densitytotP)
    Test: A-ld
    """
    eex = _t(eex_mev)
    ldmod = ld.ldmodel if ldmodel is None else ldmodel
    ct, pt = _ct_pt(ld, ibar)
    eshift = eex - pt
    valid = (eex >= 0.0) & (eshift > 0.0)
    if ldmod <= 3 or not ld.has_table(ibar):
        dens = densitytot(ld, eex, ibar, ldmod) * PARDIS
    else:
        tab = ld.tables[ibar]
        pi = 0 if parity == -1 else 1
        dens = _table_interp(
            edens_grid(), tab.nendens, tab.Edensmax_mev, _safe(eshift, valid, 1.0),
            lambda i: tab.ldtottableP_per_mev[i, pi],
        )
    expo = torch.clamp(ct * torch.sqrt(_safe(eshift, valid, 0.0)), max=80.0)
    out = torch.where(valid, torch.exp(expo) * dens, torch.zeros_like(dens))
    return torch.clamp(out, min=1.0e-30)


def density(
    ld: LDNucleus,
    eex_mev: Tensor,
    J: Tensor,
    parity: int,
    ibar: int = 0,
    ldmodel: int | None = None,
) -> Tensor:
    """rho(Ex, J, parity) [MeV^-1], the level density of one spin and parity, exactly as
    density.f90: densitytot x 1/2 x Wigner(J) for the analytical models, the table
    rho(J, parity) otherwise (spin index min(numJ-1, int(J))). `eex_mev` and `J` broadcast;
    1e-30 below zero.

    TALYS: density.f90:1 (density)
    Test: A-ld
    """
    eex = _t(eex_mev)
    J = _t(J)
    ldmod = ld.ldmodel if ldmodel is None else ldmodel
    if ldmod <= 3 or not ld.has_table(ibar):
        # COREX: nothing but spindis reads J, so the energy-only factors are evaluated on eex as
        # given ((X, 1) from the grid callers) and broadcast against J once, in spindis
        ald = ignatyuk(ld, eex, ibar)
        sc = spincut(ld, ald, eex, ibar)
        out = densitytot(ld, eex, ibar, ldmod) * PARDIS * spindis(sc, J)
        out = torch.where(eex < 0.0, torch.zeros_like(out), out)
        return torch.clamp(out, min=1.0e-30)
    eex, J = torch.broadcast_tensors(eex, J)
    tab = ld.tables[ibar]
    ct, pt = _ct_pt(ld, ibar)
    from physics.hf.density.ld2_nx2 import table_density

    got = table_density(tab, ct, pt, eex, J, parity, NUMJ - 1)  # NX2 ld2: C, off the graph
    if got is not None:
        return got
    eshift = eex - pt
    valid = (eex >= 0.0) & (eshift > 0.0)
    jj = torch.clamp(J.floor().to(torch.int64), max=NUMJ - 1)
    pi = 0 if parity == -1 else 1
    ldtab = _table_interp(
        edens_grid(), tab.nendens, tab.Edensmax_mev, _safe(eshift, valid, 1.0),
        lambda i: tab.ldtable_per_mev[i, jj, pi],
    )
    expo = torch.clamp(ct * torch.sqrt(_safe(eshift, valid, 0.0)), max=80.0)
    out = torch.where(valid, torch.exp(expo) * ldtab, torch.zeros_like(ldtab))
    return torch.clamp(out, min=1.0e-30)


def density_callable(ld: LDNucleus, ibar: int = 0) -> Callable[[Tensor, Tensor, int], Tensor]:
    """`density(ex, J, P) -> (X, J)` for one nucleus, the form `gamma.transmission.radwidtheory`
    takes: ex (X,), J (J,), parity +-1.

    TALYS: density.f90:1 (density)
    Test: A-ld
    """

    def f(ex: Tensor, J: Tensor, P: int) -> Tensor:
        return density(ld, _t(ex).reshape(-1, 1), _t(J).reshape(1, -1), int(P), ibar)

    return f


def level_density_on_grid(
    ld: LDNucleus, ex_mev: Tensor, ibar: int = 0, numJ: int = NUMJ
) -> LevelDensity:
    """rho(Ex, J, parity) [MeV^-1] on an excitation grid ex_mev (..., B) for J = j + A-parity/2,
    j = 0..numJ, parity axis (-1, +1), as `LevelDensity` (contract §5).

    TALYS: density.f90:1 (density)
    Test: A-ld
    """
    ex = _t(ex_mev)
    rodd = 0.5 * (ld.A % 2)
    J = torch.arange(numJ + 1, dtype=DTYPE) + rodd
    rho = torch.stack(
        [density(ld, ex.unsqueeze(-1), J, p, ibar) for p in (-1, 1)], dim=-1
    )
    return LevelDensity(rho_per_mev=rho, ld_parameters=ld_header(ld, ibar))


def dtheory(
    ld: LDNucleus, target_spin: float, target_parity: int, E_mev: float = 0.0, lmaxinc: int = 0,
    numl: int = 60,
) -> Tensor:
    """Theoretical average resonance spacings D_l [eV] for l = 0..numl of the compound nucleus
    `ld` formed by a neutron on the nucleus with ground-state spin `target_spin` and parity
    `target_parity` (levels of (Zix, Nix+1), level Ltarget for the initial compound): D_l =
    1e6 / sum_J rho(S_n + E, J, parity with (-1)^l). The last (l, J) pair written wins in rho(l, J),
    exactly as the Fortran overwrites it.

    TALYS: dtheory.f90:1 (dtheory)
    Test: A-ld
    """
    tspin = _fv(target_spin)
    tspin2 = int(2.0 * tspin)
    lmaxdth = max(int(lmaxinc), 5)
    J2b = int(2.0 * (tspin + 0.5)) % 2
    J2e = min(int(2 * (lmaxdth + 0.5 + tspin)), 2 * NUMJ)
    eex = torch.clamp(ld.S_mev + E_mev, min=0.0)
    rho = {}
    for parity in (-1, 1):
        pardif = abs(int(target_parity) - parity) // 2
        for J2 in range(J2b, J2e + 1, 2):
            J = J2 // 2
            for jj2 in range(abs(J2 - tspin2), J2 + tspin2 + 1, 2):
                l2end = min(jj2 + 1, 2 * lmaxdth)
                for l2 in range(abs(jj2 - 1), l2end + 1, 2):
                    l = l2 // 2
                    if l % 2 != pardif:
                        continue
                    rho[(l, J)] = (0.5 * J2, parity)
    D = torch.zeros(numl + 1, dtype=DTYPE)
    cache: dict[tuple[float, int], Tensor] = {}
    for l in range(numl + 1):
        rsum = _t(0.0)
        for J in range(NUMJ + 1):
            if (l, J) in rho:
                key = rho[(l, J)]
                if key not in cache:
                    cache[key] = density(ld, eex, _t(key[0]), key[1], 0)
                rsum = rsum + cache[key]
        if _fv(rsum) >= 1.0e-10:
            D[l] = 1.0e6 / rsum
    return D


def ld_header(ld: LDNucleus, ibar: int = 0) -> dict:
    """The ld*.gs `parameters` block as TALYS prints it (names and units as in the file).

    TALYS: densityout.f90:1 (densityout)
    Test: A-ld
    """
    SS = ld.S_mev
    h: dict = {
        "fission barrier": ibar,
        "ldmodel keyword": ld.ldmodel,
    }
    if ld.ldmodel <= 3:
        h["collective enhancement"] = "y" if (ld.flagcol and not ld.has_table(ibar)) else "n"
        h["a(Sn) [MeV^-1]"] = _fv(ld.alev)
        h["asymptotic a [MeV^-1]"] = _fv(ld.alimit)
        h["shell correction [MeV]"] = _fv(ld.deltaW_mev[ibar])
        h["damping gamma"] = _fv(ld.gammald)
        h["pairing energy [MeV]"] = _fv(ld.pair_mev)
        h["adjusted pairing shift [MeV]"] = _fv(ld.Pshift_mev[ibar])
        h["discrete spin cutoff parameter"] = _fv(ld.scutoffdisc[ibar])
        h["spin cutoff parameter(Sn)"] = _fv(spincut(ld, ignatyuk(ld, SS, ibar), SS, ibar))
        if ld.ldmodel == 1:
            h["matching energy [MeV]"] = _fv(ld.Exmatch_mev[ibar])
            h["temperature [MeV]"] = _fv(ld.T_mev[ibar])
            h["E0 [MeV]"] = _fv(ld.E0_mev[ibar])
        # densityout.f90:224 tests ldexist at barrier 1 literally, whatever `ibar` is
        if ld.flagcol and not ld.has_table(1):
            h["beta2"] = _fv(ld.beta2[0])
            h["Krotconstant"] = _fv(ld.Krotconstant[ibar])
            h["Ufermi"] = _fv(ld.Ufermi_mev[ibar])
            h["cfermi"] = _fv(ld.cfermi_mev[ibar])
        if ibar > 0:  # densityout.f90:230
            from physics.hf.density.matching import aldmatch

            h["a-effective [MeV^-1]"] = _fv(aldmatch(ld, SS, ibar))
        if ld.ldmodel == 3:
            h["Delta0"] = _fv(ld.delta0_mev)
            h["critical a [MeV^-1]"] = _fv(ld.aldcrit[ibar])
            h["critical energy [MeV]"] = _fv(ld.Ucrit_mev[ibar])
            h["condensation energy [MeV]"] = _fv(ld.Econd_mev[ibar])
            h["critical temperature [MeV]"] = _fv(ld.Tcrit_mev)
    h["separation energy [MeV]"] = _fv(SS)
    h["Rhotot(Sn) [MeV^-1]"] = _fv(densitytot(ld, SS, ibar))
    h["number of excited levels"] = ld.nlevmax2
    h["Nlow"] = ld.Nlow[ibar]
    h["Ntop"] = ld.Ntop[ibar]
    h["ctable"] = _fv(ld.ctable[ibar])
    h["ptable"] = _fv(ld.ptable_mev[ibar])
    h["s2adjust"] = _fv(ld.s2adjust[ibar])
    return h


def densityout(
    ld: LDNucleus,
    ncum: Tensor | None = None,
    ibar: int = 0,
    rhoexp: Tensor | None = None,
) -> dict:
    """The numbers of ld*.gs for one nucleus and barrier: the header (:func:`ld_header`), the
    per-level total level density block (ibar 0; needs `ncum` and `rhoexp` from densitycum),
    and the
    per-parity blocks on edens: T, N_cumulative, rho_observed (densitytotP), rho_total
    (sum_J (2J+1) rho(J)) and rho(J) for J = j + A-parity/2, j = 0..numJ.

    TALYS: densityout.f90:1 (densityout)
    Test: A-ld
    """
    out: dict = {"parameters": ld_header(ld, ibar)}
    A = ld.A
    odd = A % 2
    if ibar == 0:
        # densityout.f90:275-307 walks the levels one at a time; here the whole column is one
        # batched evaluation (contract §1.2) -- 300 scalar densitytot calls per nucleus was the
        # dominant cost of the A-ld gate.
        keep = [i for i in range(1, ld.nlevmax2 + 1) if _fv(ld.edis_mev[i]) != 0.0]
        idx = torch.tensor(keep, dtype=torch.int64)
        eex = ld.edis_mev[idx]
        nan = torch.full_like(eex, float("nan"))
        # Trap: densityout.f90:285 evaluates densitytot at the level MIDPOINT
        # 0.5*(edis(i) + edis(i-1)), and only the ldmod <= 3 branch (:291) overwrites it with
        # the value at the level energy. So the `Total_LD` column of ld*.gs -- and of
        # physics.hf.reference.level_density -- is the level density at the midpoint whenever
        # ldmodel >= 4, which is the default for A > 215. Reading it as rho(E_level) makes
        # every actinide look wrong by a factor that decays as the levels crowd together
        # (Pu-238: 1.79x at level 9, and TALYS's 1e-30 at level 7, whose midpoint falls below
        # ptable). edis(i-1) is the raw previous index, zero-energy levels included, as in the
        # Fortran.
        e_tot = eex if ld.ldmodel <= 3 else 0.5 * (eex + ld.edis_mev[idx - 1])
        lev = {
            "E": eex.tolist(),
            "Level": keep,
            "N_cumulative": (ncum[idx] if ncum is not None else nan).tolist(),
            "Total_LD": densitytot(ld, e_tot, ibar).tolist(),
            "Exp_LD": (rhoexp[idx] if rhoexp is not None else nan).tolist(),
        }
        if ld.ldmodel <= 3:
            ald = ignatyuk(ld, eex, ibar)
            if ld.ldmodel == 3:  # densityout.f90:290
                below = eex < ld.Ucrit_mev[ibar] - ld.pair_mev - ld.Pshift_mev[ibar]
                ald = torch.where(below, ld.aldcrit[ibar].expand_as(ald), ald)
            lev["a"] = ald.tolist()
            lev["Sigma"] = torch.sqrt(spincut(ld, ald, eex, ibar)).tolist()
        out["levels"] = lev
    edens = edens_grid()
    from physics.hf.density.tables import nendens_of

    nend = nendens_of(ld.ldmodel)[0]
    E = edens[1 : nend + 1]
    J = torch.arange(NUMJ + 1, dtype=DTYPE) + 0.5 * odd
    blocks = {}
    for parity in (1, -1):
        dP = densitytotP(ld, E, parity, ibar)
        if ld.ldmodel > 3:  # densityout.f90:350-352, zeros when the table is missing
            pi = 0 if parity == -1 else 1
            tab = ld.tables[ibar] if ld.has_table(ibar) else None
            T = tab.ldtableT_mev[1 : nend + 1, pi] if tab else torch.zeros_like(E)
            Nc = tab.ldtableN[1 : nend + 1, pi] if tab else torch.zeros_like(E)
        else:
            T = torch.sqrt(E / ld.alev)
            dEx = torch.cat([E[:1], E[1:] - E[:-1]])
            Nc = torch.cumsum(dP * dEx, dim=0)
        rhoJ = density(ld, E.unsqueeze(-1), J.unsqueeze(0), parity, ibar)
        ldtot = ((2.0 * J + 1.0) * rhoJ).sum(-1)
        blocks[parity] = {
            "E": E, "T": T, "N_cumulative": Nc, "rho_observed": dP, "rho_total": ldtot,
            "rho_J": rhoJ,
        }
    out["parity_blocks"] = blocks
    return out
