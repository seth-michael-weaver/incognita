"""Microscopic tabulated level densities (ldmodel 4-7: Goriely-Skyrme HFB, Hilaire-Goriely Skyrme
and Gogny, BSkG3 combinatorial), with the spin-cutoff rescaling and the triaxial enhancement of
barrier tables.

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

Task: T6 (physics/hf/CONTRACT.md §7). Acceptance test: A-ld (§6).

TALYS routines ported here (file:line of the subroutine/function statement):
    densitytable.f90:1 (densitytable)

File layout, as the Fortran reads it: each nucleus block is a 3-line banner whose second line
carries A in columns 32-34, a column-label line, `nendens` data records
``(7x, f7.3, e10.2, e9.2, 9x, 30e9.2)`` = U, T, N_cumulative, rho (the RHOOBS column; RHOTOT is
skipped), rho(J=0..29), then one blank line. ldmodel 4 files (55 energies, 150 MeV) hold both
parities summed; ldmodel >= 5 files hold a positive- and a negative-parity block per nucleus and
TALYS reads them in that order from one file position.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from functools import cache
from pathlib import Path
from typing import TYPE_CHECKING

import torch
from torch import Tensor

from physics.hf.core.constants import nuclide_symbol, talys_constants
from physics.hf.core.tensors import DTYPE
from physics.hf.structure.files import fortran_read, fortran_reader, talys_structure_dir

if TYPE_CHECKING:
    from physics.hf.density.parameters import LDNucleus

__all__ = ["DensityTable", "edens_grid", "nendens_of", "density_table", "attach_tables"]

NUMJ = 40  # A0_talys_mod.f90:68
_DATA_FMT = "(7x, f7.3, e10.2, e9.2, 9x, 30e9.2)"  # densitytable.f90:143

_GROUND = {4: "goriely", 5: "hilaire", 6: "hilaireD1M", 7: "bskg3"}  # densitytable.f90:88-92
_BARRIER = {  # densitytable.f90:95-110
    1: {4: "goriely/inner", 5: "hilaire/Max1", 6: "hilaire/Max1", 7: "bskg3/Max1"},
    2: {4: "goriely/outer", 5: "hilaire/Max2", 6: "hilaire/Max2", 7: "bskg3/Max2"},
    3: {5: "hilaire/Max3", 6: "hilaire/Max3", 7: "bskg3/Max3"},
}


def edens_grid() -> Tensor:
    """TALYS's tabulated-density energy grid edens(0..60) [MeV] (strucinitial.f90:446-460).

    TALYS: densitytable.f90:1 (densitytable)
    Test: A-ld
    """
    e = [0.0] * 61
    for nex in range(1, 21):
        e[nex] = 0.25 * nex
    for nex in range(21, 31):
        e[nex] = 5.0 + 0.5 * (nex - 20)
    for nex in range(31, 41):
        e[nex] = 10.0 + nex - 30
    e[41], e[42], e[43] = 22.5, 25.0, 30.0
    for nex in range(44, 61):
        e[nex] = 30.0 + 10.0 * (nex - 43)
    return torch.tensor(e, dtype=DTYPE)


def nendens_of(ldmodel: int) -> tuple[int, float]:
    """(nendens, Edensmax [MeV]) for a nucleus with this ldmodel (strucinitial.f90:461-468).

    TALYS: densitytable.f90:1 (densitytable)
    Test: A-ld
    """
    return (55, 150.0) if ldmodel == 4 else (60, 200.0)


@dataclass(frozen=True)
class DensityTable:
    """One nucleus/barrier table as TALYS stores it; parity axis ordered (-1, +1) (contract §4.2),
    energy axis indexed 0..nendens like `edens` (row 0 unused, zero)."""

    ldmodel: int
    ibar: int
    nendens: int
    Edensmax_mev: float
    ldtable_per_mev: Tensor  # (nendens+1, numJ+1, 2)
    ldtottable_per_mev: Tensor  # (nendens+1,)
    ldtottableP_per_mev: Tensor  # (nendens+1, 2)
    ldtableT_mev: Tensor  # (nendens+1, 2)
    ldtableN: Tensor  # (nendens+1, 2)


@cache
def _file_lines(path: str) -> tuple[str, ...]:
    p = Path(path)
    if not p.is_file():
        return ()
    return tuple(p.read_text(encoding="latin-1").splitlines())


def _table_path(Z: int, ldmodel: int, ibar: int) -> Path | None:
    base = talys_structure_dir() / "density"
    sym = nuclide_symbol(Z)
    if ibar == 0:
        d = _GROUND.get(ldmodel)
        return base / "ground" / d / f"{sym}.tab" if d else None
    d = _BARRIER.get(ibar, {}).get(ldmodel)
    return base / "fission" / d / f"{sym}.ld" if d else None


def density_table(
    Z: int,
    A: int,
    ldmodel: int,
    ibar: int = 0,
    *,
    rspincut: float = 1.0,
    s2adjust: float = 1.0,
    flagparity: bool = True,
    ld: LDNucleus | None = None,
    path: str | Path | None = None,
) -> DensityTable | None:
    """The tabulated rho(E, J, parity) [MeV^-1] TALYS reads from structure/density for (Z, A), or
    None when the nucleus is not in the file (ldexist false). `rspincut`/`s2adjust` reshape the
    spin distribution as densitytable.f90:160-195 when not 1; `ld` is needed only for barrier
    tables with axtype >= 3 (the triaxial factor uses ignatyuk/spincut).

    TALYS: densitytable.f90:1 (densitytable)
    Test: A-ld
    """
    p = Path(path) if path is not None else _table_path(Z, ldmodel, ibar)
    lines = _file_lines(str(p)) if p is not None else ()
    if not lines:
        return None
    nendens, edensmax = nendens_of(ldmodel)
    if rspincut == 1.0 and s2adjust == 1.0:
        from physics.hf.density.ld2_nx2 import enabled

        if enabled():  # NX2 ld2: the same arithmetic on whole columns (bit for bit)
            return _density_table_np(str(p), A, ldmodel, ibar, nendens, edensmax, flagparity, ld)
    ploop = (1, -1) if ldmodel >= 5 else (1,)
    pardisloc = 1.0 if ldmodel >= 5 else 0.5
    edens = edens_grid()
    ldtable = torch.zeros(nendens + 1, NUMJ + 1, 2, dtype=DTYPE)
    ldtot_t = torch.zeros(nendens + 1, dtype=DTYPE)
    ldtotP = torch.zeros(nendens + 1, 2, dtype=DTYPE)
    ldT = torch.zeros(nendens + 1, 2, dtype=DTYPE)
    ldN = torch.zeros(nendens + 1, 2, dtype=DTYPE)
    exist = False
    pos = 0
    nl = len(lines)
    for parity in ploop:
        pi = 0 if parity == -1 else 1
        found = False
        while pos + 1 < nl:
            ia = fortran_read(lines[pos + 1], "(31x, i3)")[0]  # '(/31x, i3//)'
            pos += 4
            if ia != A:
                pos += nendens + 1
                continue
            found = exist = True
            read = fortran_reader(_DATA_FMT)
            for nex in range(1, nendens + 1):
                vals = read(lines[pos] if pos < nl else "")
                pos += 1
                Tn, Nc, ldtot = vals[0], vals[1], vals[2]
                ld2j1 = [0.0] * (NUMJ + 1)
                ld2j1[:30] = [float(v) for v in vals[3:33]]
                ldT[nex, pi] = Tn
                ldN[nex, pi] = Nc
                ldsum = ldtot
                for J in range(30, NUMJ + 1):  # densitytable.f90:150-154
                    factor = 1.0 - (J - 29.0) / (NUMJ - 29.0)
                    ld2j1[J] = ld2j1[29] * factor
                    ldsum += ld2j1[J]
                if ldsum > 0.0:
                    ld2j1 = [v * ldtot / ldsum for v in ld2j1]
                if (rspincut != 1.0 or s2adjust != 1.0) and ldtot > 0.0:  # :160-195
                    jt = rspincut * s2adjust
                    Rdis = [v / ldtot for v in ld2j1]
                    Rsum = sum(Rdis)
                    if Rsum > 0.0:
                        Rdis = [v / Rsum for v in Rdis]
                        Jtop = 0
                        for J in range(1, NUMJ + 1):
                            if Rdis[J] > Rdis[Jtop]:
                                Jtop = J
                        Rnew = [0.0] * (NUMJ + 1)
                        for J in range(NUMJ):
                            Rnew[J] = Rdis[Jtop] * (Rdis[J] / Rdis[Jtop]) ** (1.0 / jt)
                        sumJ = sum(Rnew)
                        if sumJ > 0.0:
                            ld2j1 = [ldtot * v / sumJ for v in Rnew]
                Ktriax = 1.0
                if ibar > 0 and ld is not None:  # :196-208
                    ax = ld.axtype[ibar]
                    if ax == 2:
                        Ktriax = 2.0
                    elif ax >= 3:
                        from physics.hf.density.parameters import ignatyuk, spincut

                        twopi = talys_constants()["twopi"]
                        eex = edens[nex]
                        ald = ignatyuk(ld, eex, ibar)
                        term = math.sqrt(float(spincut(ld, ald, eex, ibar)))
                        Ktriax = {3: 0.5, 4: 1.0, 5: 2.0}[ax] * math.sqrt(twopi) * term
                ldtotP[nex, pi] = pardisloc * ldtot * Ktriax
                if len(ploop) == 1:
                    ldtotP[nex, 0] = pardisloc * ldtot * Ktriax
                ldtot_t[nex] += ldtot
                row = torch.tensor(ld2j1, dtype=DTYPE) * (pardisloc * Ktriax)
                ldtable[nex, :, pi] = row
                if len(ploop) == 1:
                    ldtable[nex, :, 0] = row
            pos += 1  # read(2, '()')
            break
        if not found:
            break
    if not exist:
        return None
    if ldmodel >= 5 and not flagparity:  # densitytable.f90:236-243
        ldtotP[:, 1] = 0.5 * (ldtotP[:, 0] + ldtotP[:, 1])
        ldtable[:, :, 1] = 0.5 * (ldtable[:, :, 0] + ldtable[:, :, 1])
    return DensityTable(
        ldmodel=ldmodel,
        ibar=ibar,
        nendens=nendens,
        Edensmax_mev=edensmax,
        ldtable_per_mev=ldtable,
        ldtottable_per_mev=ldtot_t,
        ldtottableP_per_mev=ldtotP,
        ldtableT_mev=ldT,
        ldtableN=ldN,
    )


@cache
def _table_blocks(path: str, A: int, nendens: int, nparity: int) -> tuple:
    """NX2 ld2: the `nendens` records (T, N_cumulative, rho, rho(J=0..29)) of mass `A` in one table
    file, one float64 array (nendens, 33) per parity block found, in file order, scanned exactly as
    `density_table` scans (a missing second block ends the search). A pure function of the file,
    as `_file_lines` is.

    TALYS: densitytable.f90:1 (densitytable)
    Test: tests/hf/test_nx2_ld2.py
    """
    import numpy as np

    lines = _file_lines(path)
    nl = len(lines)
    read = fortran_reader(_DATA_FMT)
    pos = 0
    out = []
    for _ in range(nparity):
        found = False
        while pos + 1 < nl:
            ia = fortran_read(lines[pos + 1], "(31x, i3)")[0]  # '(/31x, i3//)'
            pos += 4
            if ia != A:
                pos += nendens + 1
                continue
            found = True
            rows = [read(lines[pos + k] if pos + k < nl else "") for k in range(nendens)]
            pos += nendens + 1  # the records and read(2, '()')
            block = np.array([[float(v) for v in r[:33]] for r in rows], dtype=np.float64)
            block.setflags(write=False)
            out.append(block)
            break
        if not found:
            break
    return tuple(out)


def _density_table_np(path: str, A: int, ldmodel: int, ibar: int, nendens: int, edensmax: float,
                      flagparity: bool, ld) -> DensityTable | None:
    """NX2 ld2: `density_table` without the spin-cutoff reshaping (`rspincut` = `s2adjust` = 1), on
    whole columns of the records: every element sees the loop's operations in the loop's order,
    so the table is the same to the bit.

    TALYS: densitytable.f90:1 (densitytable)
    Test: tests/hf/test_nx2_ld2.py
    """
    import numpy as np

    nparity = 2 if ldmodel >= 5 else 1
    blocks = _table_blocks(path, int(A), nendens, nparity)
    if not blocks:
        return None
    pardisloc = 1.0 if ldmodel >= 5 else 0.5
    n1 = nendens + 1
    ldtable = np.zeros((n1, NUMJ + 1, 2))
    ldtot_t = np.zeros(n1)
    ldtotP = np.zeros((n1, 2))
    ldT = np.zeros((n1, 2))
    ldN = np.zeros((n1, 2))
    Ktriax = np.ones(nendens)
    if ibar > 0 and ld is not None:  # :196-208
        ax = ld.axtype[ibar]
        if ax == 2:
            Ktriax[:] = 2.0
        elif ax >= 3:
            from physics.hf.density.parameters import ignatyuk, spincut

            twopi = talys_constants()["twopi"]
            edens = edens_grid()
            for nex in range(1, nendens + 1):
                eex = edens[nex]
                ald = ignatyuk(ld, eex, ibar)
                term = math.sqrt(float(spincut(ld, ald, eex, ibar)))
                Ktriax[nex - 1] = {3: 0.5, 4: 1.0, 5: 2.0}[ax] * math.sqrt(twopi) * term
    for k, V in enumerate(blocks):
        pi = 1 if k == 0 else 0  # the positive-parity block comes first
        ldtot = V[:, 2]
        ld2j1 = np.zeros((nendens, NUMJ + 1))
        ld2j1[:, :30] = V[:, 3:33]
        ldT[1:, pi] = V[:, 0]
        ldN[1:, pi] = V[:, 1]
        ldsum = ldtot.copy()
        for J in range(30, NUMJ + 1):  # densitytable.f90:150-154
            factor = 1.0 - (J - 29.0) / (NUMJ - 29.0)
            ld2j1[:, J] = ld2j1[:, 29] * factor
            ldsum = ldsum + ld2j1[:, J]
        pos = ldsum > 0.0
        with np.errstate(all="ignore"):
            scaled = ld2j1 * ldtot[:, None] / np.where(pos, ldsum, 1.0)[:, None]
        ld2j1 = np.where(pos[:, None], scaled, ld2j1)
        totP = pardisloc * ldtot * Ktriax
        ldtotP[1:, pi] = totP
        if nparity == 1:
            ldtotP[1:, 0] = totP
        ldtot_t[1:] += ldtot
        row = ld2j1 * (pardisloc * Ktriax)[:, None]
        ldtable[1:, :, pi] = row
        if nparity == 1:
            ldtable[1:, :, 0] = row
    if ldmodel >= 5 and not flagparity:  # densitytable.f90:236-243
        ldtotP[:, 1] = 0.5 * (ldtotP[:, 0] + ldtotP[:, 1])
        ldtable[:, :, 1] = 0.5 * (ldtable[:, :, 0] + ldtable[:, :, 1])
    return DensityTable(
        ldmodel=ldmodel,
        ibar=ibar,
        nendens=nendens,
        Edensmax_mev=edensmax,
        ldtable_per_mev=torch.from_numpy(ldtable),
        ldtottable_per_mev=torch.from_numpy(ldtot_t),
        ldtottableP_per_mev=torch.from_numpy(ldtotP),
        ldtableT_mev=torch.from_numpy(ldT),
        ldtableN=torch.from_numpy(ldN),
    )


def attach_tables(ld: LDNucleus) -> LDNucleus:
    """`ld` with `ldexist`/`tables` filled for every barrier when ldmodel >= 4 (the
    ``if (ldmodel >= 4) call densitytable`` step of structure.f90). Barrier tables are read only
    with fission on, as TALYS does (nloop = nfisbar).

    TALYS: densitytable.f90:1 (densitytable)
    Test: A-ld
    """
    from dataclasses import replace

    if ld.ldmodel < 4:
        return ld
    tabs = []
    for ib in range(ld.nfisbar + 1):
        tabs.append(
            density_table(
                ld.Z,
                ld.A,
                ld.ldmodel,
                ib,
                rspincut=float(ld.Rspincut),
                s2adjust=float(ld.s2adjust[ib]),
                flagparity=ld.flagparity,
                ld=ld,
            )
        )
    return replace(ld, ldexist=tuple(t is not None for t in tabs), tables=tuple(tabs))
