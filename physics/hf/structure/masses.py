"""Nuclear masses (AME2020, FRDM/HFB fallbacks, Duflo-Zuker), mass excesses and separation
energies.

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

Task: T2 (physics/hf/CONTRACT.md §7). Acceptance test: A-struct (§6).

TALYS routines ported here (file:line of the subroutine/function statement):
    masses.f90:1 (masses)
    separation.f90:1 (separation)
    duflo.f90:1 (duflo)
    duflo.f90:20 (mass10)
    mliquid1.f90:1 (mliquid1)
    mliquid2.f90:1 (mliquid2)

What TALYS does, and what this reproduces
-----------------------------------------
Masses live on TALYS's nucleus grid ``[Zix, Nix]`` (protons/neutrons removed from the initial
compound nucleus), for ``Zix <= maxZ + 4`` and ``Nix <= maxN + 4`` (masses.f90:105-110; separation
energies need the neighbours). Precedence per nucleus (masses.f90:176-201): a user
``massnucleus``/``massexcess`` wins; else the AME2020 mass if ``expmass y`` (default) and tabulated;
else the theoretical table of ``massmodel`` (default 2 = HFB-Skyrme, masses/hfb). If any grid
nucleus is still massless -- which happens on almost every run, because the grid reaches
N <= 0 or beyond the tables -- the Duflo-Zuker formula is evaluated for the WHOLE grid
(`dumexc`) and fills the massless ones (masses.f90:208-231).

Separation energies (separation.f90) are always built from two masses of the same kind: both
experimental mass excesses if both exist, else both theoretical, else both Duflo-Zuker -- even
when that means the Duflo-Zuker difference of two nuclei whose table masses exist. Their grid is
``Zix <= maxZ + 2``, ``Nix <= maxN + 2`` and particle types 1..6; ``S(.,.,0) = 0``.

Precision: masses and mass excesses are real(dbl) read from the tables; Duflo-Zuker is computed
in single precision (duflo.f90 declares nothing, so every variable is implicit REAL) and is
reproduced here in float32. `amu` and `excmass` are TALYS's in-memory values (T1,
`talys_constants()`).
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from functools import cache, lru_cache
from typing import TYPE_CHECKING

import numpy as np
import torch
from torch import Tensor

from physics.hf.core.constants import PARN, PARZ, talys_constants
from physics.hf.core.tensors import DTYPE
from physics.hf.structure.files import read_mass_file, talys_structure_dir

if TYPE_CHECKING:
    from physics.hf.input.defaults import Options, Params

__all__ = ["Masses", "masses", "duflo", "mliquid1", "mliquid2", "separation_energy"]

_F = np.float32


@dataclass(frozen=True)
class Masses:
    """TALYS's mass arrays on the nucleus grid, indexed ``[Zix, Nix]`` (contract §4.2).

    Shapes: per-nucleus arrays ``(maxZ+5, maxN+5)``; separation energies, specific and reduced
    masses ``(maxZ+3, maxN+3, 7)`` over particle type 0..6 (g n p d t h a).
    Units in the names; `beta2`, `beta4`, spins and parities are dimensionless.
    """

    Zinit: int
    Ninit: int
    maxZ: int
    maxN: int
    mass_amu: Tensor  # nucmass
    expmass_amu: Tensor  # expmass (0 = not tabulated)
    expmexc_mev: Tensor  # expmexc
    thmass_amu: Tensor  # thmass
    thmexc_mev: Tensor  # thmexc
    dumexc_mev: Tensor  # dumexc (Duflo-Zuker, 0 unless flagduflo)
    beta2: Tensor  # beta2(Zix, Nix, 0) as read from the theoretical table
    beta4: Tensor
    gsspin: Tensor
    gsparity: Tensor
    s_mev: Tensor  # S(Zix, Nix, type)
    specmass: Tensor  # specmass(Zix, Nix, type)
    redumass_amu: Tensor  # redumass(Zix, Nix, type)
    flagduflo: bool

    @property
    def s_n_mev(self) -> Tensor:
        return self.s_mev[..., 1]

    @property
    def s_p_mev(self) -> Tensor:
        return self.s_mev[..., 2]

    @property
    def s_a_mev(self) -> Tensor:
        return self.s_mev[..., 6]

    def index(self, Z: int, A: int) -> tuple[int, int]:
        """(Zix, Nix) of nucleus (Z, A)."""
        return self.Zinit - Z, self.Ninit - (A - Z)


# ----------------------------------------------------------------------------------------------
# Duflo-Zuker (duflo.f90), single precision
# ----------------------------------------------------------------------------------------------

_B = np.array(
    [0.7043, 17.7418, 16.2562, 37.5562, 53.9017, 0.4711, 2.1307, 0.0210, 40.5356, 6.0632],
    dtype=_F,
)


@cache
def _shell(n: int, ndef: int) -> tuple:
    """The per-nucleon-kind block of mass10 (duflo.f90's ``do j = 1, 2`` body) for ``n``
    nucleons and deformation branch ``ndef``: (n2, pp, qx, dx, op, os). It depends on nothing
    else, so it is memoised; the float32 operations are the Fortran's, in its order."""
    one, half = _F(1.0), _F(0.5)
    ju = 4 if ndef == 2 else 0
    noc = np.zeros(30, dtype=np.int64)
    onp = np.zeros((21, 3), dtype=_F)
    n2 = 2 * (n // 2)
    ncum = 0
    i = 0
    while True:
        i += 1
        i2 = (i // 2) * 2
        idd = i + 1 if i2 != i else i * (i - 2) // 4
        ncum += idd
        if ncum < n:
            noc[i] = idd
            continue
        break
    imax = i + 1
    ip = (i - 1) // 2
    ipm = i // 2
    pp = _F(ip)
    moc = n - ncum + idd
    noc[i] = moc - ju
    noc[i + 1] = ju
    if i2 != i:
        oei = _F(moc + ip * (ip - 1))
        dei = _F(ip * (ip + 1) + 2)
    else:
        oei = _F(moc - ju)
        dei = _F((ip + 1) * (ip + 2) + 2)
    qx = oei * (dei - oei - _F(ju)) / dei
    dx = qx * (_F(2.0) * oei - dei)
    if ndef == 2:
        qx = qx / np.sqrt(dei)
    for ii in range(1, imax + 1):
        ipp = (ii - 1) // 2
        fact = np.sqrt((_F(ipp) + one) * (_F(ipp) + _F(2.0)))
        onp[ipp, 1] = onp[ipp, 1] + _F(noc[ii]) / fact
        vm = _F(-1.0)
        if 2 * (ii // 2) != ii:
            vm = half * _F(ipp)
        onp[ipp, 2] = onp[ipp, 2] + _F(noc[ii]) * vm
    op = _F(0.0)
    os_ = _F(0.0)
    for ipp in range(0, ipm + 1):
        pi = _F(ipp)
        den = ((pi + one) * (pi + _F(2.0))) ** (_F(3.0) / _F(2.0))
        op = op + onp[ipp, 1]
        os_ = (
            os_
            + onp[ipp, 2] * (one + onp[ipp, 1]) * (pi * pi / den)
            + onp[ipp, 2] * (one - onp[ipp, 1]) * ((_F(4.0) * pi - _F(5.0)) / den)
        )
    op = op * op
    return n2, pp, qx, dx, op, os_


@cache
def _mass10(nx: int, nz: int) -> np.float32:
    """mass10 of duflo.f90; a pure function of (N, Z), memoised (masses() evaluates it on every
    grid, many times per run)."""
    one, quarter = _F(1.0), _F(0.25)
    nn = (nx, nz)
    a = _F(nx + nz)
    t = _F(abs(nx - nz))
    r = a ** (one / _F(3.0))
    rc = r * (one - quarter * (t / a) * (t / a))
    ra = (rc * rc) / r
    z2 = _F(nz * (nz - 1))
    dyda = np.zeros(11, dtype=_F)  # 1-based
    dyda[1] = (-z2 + _F(0.76) * z2 ** (_F(2.0) / _F(3.0))) / rc
    y = np.zeros(3, dtype=_F)
    for ndef in (1, 2):
        y[ndef] = _F(0.0)
        dyda[2:11] = _F(0.0)
        pp = np.zeros(3, dtype=_F)
        qx = np.zeros(3, dtype=_F)
        dx = np.zeros(3, dtype=_F)
        op = np.zeros(3, dtype=_F)
        os_ = np.zeros(3, dtype=_F)
        n2 = [0, 0, 0]
        for j in (1, 2):
            n2[j], pp[j], qx[j], dx[j], op[j], os_[j] = _shell(nn[j - 1], ndef)
        dyda[2] = op[1] + op[2]
        dyda[3] = -dyda[2] / ra
        dyda[2] = dyda[2] + os_[1] + os_[2]
        dyda[4] = -(t * (t + _F(2.0)) / (r * r))
        dyda[5] = -dyda[4] / ra
        if ndef == 1:
            dyda[6] = dx[1] + dx[2]
            dyda[7] = -dyda[6] / ra
            px = np.sqrt(pp[1]) + np.sqrt(pp[2])
            dyda[8] = qx[1] * qx[2] * (_F(2.0) ** px)
        else:
            dyda[9] = qx[1] * qx[2]
        dyda[5] = t * (one - t) / (a * (ra * ra * ra)) + dyda[5]
        nx_even, nz_even = n2[1] == nn[0], n2[2] == nn[1]
        if not nx_even and not nz_even:
            dyda[10] = t / a
        if nx > nz:
            if nx_even and not nz_even:
                dyda[10] = one - t / a
            if not nx_even and nz_even:
                dyda[10] = one
        else:
            if nx_even and not nz_even:
                dyda[10] = one
            if not nx_even and nz_even:
                dyda[10] = one - t / a
        if nz_even and nx_even:
            dyda[10] = _F(2.0) - t / a
        for mss in range(2, 11):
            dyda[mss] = dyda[mss] / ra
        for mss in range(1, 11):
            y[ndef] = y[ndef] + dyda[mss] * _B[mss - 1]
    de = y[2] - y[1]
    e = y[2]
    if de <= 0.0 or nz <= 50:
        e = y[1]
    return _F(e)


def duflo(N: int, Z: int) -> float:
    """Duflo-Zuker mass excess [MeV] in TALYS's single precision.

    TALYS: duflo.f90:1 (duflo), duflo.f90:20 (mass10)
    Test: A-struct
    """
    e = _mass10(int(N), int(Z))
    exc = _F(Z) * _F(7.28903) + _F(N) * _F(8.07138) - e
    return float(exc)


def _mass10_many(nx: np.ndarray, nz: np.ndarray) -> np.ndarray:
    """COREX: `_mass10` elementwise over int arrays (N, Z >= 1): the same float32 operations in
    the same order, as array operations, so every element is bit-identical to the scalar call
    (tests/hf/test_corex.py checks each cell of a masses() grid)."""
    one, quarter = _F(1.0), _F(0.25)
    a = (nx + nz).astype(_F)
    t = np.abs(nx - nz).astype(_F)
    r = a ** (one / _F(3.0))
    rc = r * (one - quarter * (t / a) * (t / a))
    ra = (rc * rc) / r
    z2 = (nz * (nz - 1)).astype(_F)
    d1 = (-z2 + _F(0.76) * z2 ** (_F(2.0) / _F(3.0))) / rc
    zero = np.zeros_like(a)
    y = {}
    for ndef in (1, 2):
        sh = {}
        for j, nn_ in ((1, nx), (2, nz)):
            uniq, inv = np.unique(nn_, return_inverse=True)
            rows = [_shell(int(v), ndef) for v in uniq]
            cols = [np.array([row[c] for row in rows])[inv].reshape(nn_.shape) for c in range(6)]
            sh[j] = (cols[0].astype(np.int64),) + tuple(c.astype(_F) for c in cols[1:])
        n2_1, pp1, qx1, dx1, op1, os1 = sh[1]
        n2_2, pp2, qx2, dx2, op2, os2 = sh[2]
        d = [None, d1] + [zero] * 9
        d[2] = op1 + op2
        d[3] = -d[2] / ra
        d[2] = d[2] + os1 + os2
        d[4] = -(t * (t + _F(2.0)) / (r * r))
        d[5] = -d[4] / ra
        if ndef == 1:
            d[6] = dx1 + dx2
            d[7] = -d[6] / ra
            px = np.sqrt(pp1) + np.sqrt(pp2)
            d[8] = qx1 * qx2 * (_F(2.0) ** px)
        else:
            d[9] = qx1 * qx2
        d[5] = t * (one - t) / (a * (ra * ra * ra)) + d[5]
        xe, ze = n2_1 == nx, n2_2 == nz
        ta = t / a
        d10 = np.where(~xe & ~ze, ta, zero)
        gt = nx > nz
        d10 = np.where(gt & xe & ~ze, one - ta, d10)
        d10 = np.where(gt & ~xe & ze, one, d10)
        d10 = np.where(~gt & xe & ~ze, one, d10)
        d10 = np.where(~gt & ~xe & ze, one - ta, d10)
        d10 = np.where(ze & xe, _F(2.0) - ta, d10)
        d[10] = d10
        for mss in range(2, 11):
            d[mss] = d[mss] / ra
        acc = zero
        for mss in range(1, 11):
            acc = acc + d[mss] * _B[mss - 1]
        y[ndef] = acc
    de = y[2] - y[1]
    return np.where((de <= 0.0) | (nz <= 50), y[1], y[2]).astype(_F)


# NATIVEX2 `struct`: duflo(N, Z) by cell (float64 of the float32 value) and which cells are filled;
# pure, no target in it, kept for the worker.
_DUFLO_CELLS = np.zeros((130, 260))
_DUFLO_HAVE = np.zeros((130, 260), dtype=bool)


@cache
def _duflo_grid(Zinit: int, Ninit: int, nz: int, nn: int) -> tuple[np.ndarray, np.ndarray]:
    """COREX: `duflo(Ninit - Nix, Zinit - Zix)` on masses()'s (nz, nn) grid and the mask of the
    cells with Z > 0 and N > 0 (a pure function of the four integers; `chartrun.KEEP`), computed
    over the grid at once (`_mass10_many`). Read-only: masses() only reads it."""
    Z = Zinit - np.arange(nz)[:, None] + np.zeros((1, nn), dtype=np.int64)
    N = Ninit - np.arange(nn)[None, :] + np.zeros((nz, 1), dtype=np.int64)
    live = (Z > 0) & (N > 0)
    exc = np.zeros((nz, nn))
    if live.any():
        nx, zz = N[live], Z[live]
        # NATIVEX2 `struct`: cells already computed for an earlier grid (the cascade nuclei's
        # grids overlap) are taken from `_DUFLO_CELLS`; `_mass10_many` is elementwise, so a cell
        # is the same float32 arithmetic whichever grid first asked for it
        global _DUFLO_CELLS, _DUFLO_HAVE
        if int(zz.max()) >= _DUFLO_HAVE.shape[0] or int(nx.max()) >= _DUFLO_HAVE.shape[1]:
            shp = (max(int(zz.max()) + 1, _DUFLO_HAVE.shape[0]),
                   max(int(nx.max()) + 1, _DUFLO_HAVE.shape[1]))
            h2, c2 = np.zeros(shp, dtype=bool), np.zeros(shp)
            h2[: _DUFLO_HAVE.shape[0], : _DUFLO_HAVE.shape[1]] = _DUFLO_HAVE
            c2[: _DUFLO_CELLS.shape[0], : _DUFLO_CELLS.shape[1]] = _DUFLO_CELLS
            _DUFLO_HAVE, _DUFLO_CELLS = h2, c2
        miss = ~_DUFLO_HAVE[zz, nx]
        if miss.any():
            zm, nm = zz[miss], nx[miss]
            e = _mass10_many(nm, zm)
            _DUFLO_CELLS[zm, nm] = (zm.astype(_F) * _F(7.28903) + nm.astype(_F) * _F(8.07138)
                                    - e).astype(np.float64)
            _DUFLO_HAVE[zm, nm] = True
        exc[live] = _DUFLO_CELLS[zz, nx]
    exc.flags.writeable = False
    live.flags.writeable = False
    return exc, live


def _lit(x: float) -> float:
    """A single-precision Fortran literal as TALYS holds it in a real(dbl) variable."""
    return float(_F(x))


def mliquid1(Z: int, A: int) -> float:
    """Myers-Swiatecki liquid-drop mass [amu] (used by the level-density systematics, T6).
    Variables are real(dbl), literals single precision (as in the TALYS build).

    TALYS: mliquid1.f90:1 (mliquid1)
    Test: A-ld
    """
    c = talys_constants()
    a1, a2, kappa, c3, c4 = _lit(15.677), _lit(18.56), _lit(1.79), _lit(0.717), _lit(1.21129)
    mn, mh = _lit(8.07144), _lit(7.28899)
    N = A - Z
    rA, rZ, rN = float(A), float(Z), float(N)
    factor = 1.0 - kappa * ((rN - rZ) / rA) ** 2
    ev = -a1 * factor * rA
    esur = a2 * factor * rA ** c["twothird"]
    ecoul = c3 * rZ**2 / (rA ** c["onethird"]) - c4 * rZ**2 / rA
    odd_z, odd_n = Z % 2, N % 2
    delta_p = 0.0
    if odd_z == 0 and odd_n == 0:
        delta_p = -11.0 / math.sqrt(rA)
    if odd_z == 1 and odd_n == 1:
        delta_p = 11.0 / math.sqrt(rA)
    eldm = Z * mh + N * mn + ev + esur + ecoul + delta_p
    return A + eldm / c["amu"]


def mliquid2(Z: int, A: int) -> float:
    """Goriely liquid-drop mass [amu] (used by the level-density systematics, T6).

    TALYS: mliquid2.f90:1 (mliquid2)
    Test: A-ld
    """
    c = talys_constants()
    avol, as_, asym, ass, ac = (
        _lit(-15.6428),
        _lit(17.5418),
        _lit(27.9418),
        _lit(-25.3440),
        _lit(0.70),
    )
    mn, mh = _lit(8.07132281), _lit(7.2889694)
    N = A - Z
    rA, rZ, rN = float(A), float(Z), float(N)
    factor = (rN - rZ) / rA
    ev = avol * rA
    esur = as_ * (rA ** c["twothird"])
    esym = (asym + ass * (rA ** (-c["onethird"]))) * rA * factor**2
    ecoul = ac * rZ**2 / (rA ** c["onethird"])
    eldm = Z * mh + N * mn + ev + esur + esym + ecoul - _lit(1.4333e-5) * rZ ** _lit(2.39)
    return A + eldm / c["amu"]


# ----------------------------------------------------------------------------------------------
# masses.f90 + separation.f90 on the grid
# ----------------------------------------------------------------------------------------------


@cache
def _mass_table(structure_dir: str, Z: int, table: str) -> tuple[np.ndarray, np.ndarray]:
    """One element's mass table as (A ascending, float64 columns (n, 6)): mass, excess, beta2,
    beta4, gs spin, gs parity (the last four zero for `ame2020`). Parsed once per run."""
    rows = sorted(read_mass_file(Z, table).items())
    ia = np.array([a for a, _ in rows], dtype=np.int64)
    cols = np.zeros((len(rows), 6))
    for i, (_, vals) in enumerate(rows):
        cols[i, : len(vals)] = vals
    return ia, cols


# NATIVEX2 `struct`: the element tables of `_mass_table` copied into one dense (Z, A) array per
# (structure dir, table), an element's row filled the first time a grid reaches it. Pure file data
# like `_mass_table` itself (kept for the worker), read-only once filled.
_DENSE: dict[tuple[str, str], tuple[np.ndarray, np.ndarray, set]] = {}


def _table_cells(sdir: str, table: str, zs: list[int], Zc: np.ndarray, Ac: np.ndarray):
    """(have, values) on a (Z, A) cell grid: whether element Z's `table` file lists mass A, and
    that row's six columns (`_mass_table`'s), for the elements `zs` the grid holds (Z > 0).

    TALYS: masses.f90:1 (masses)
    Test: tests/hf/test_nx2_struct.py
    """
    ent = _DENSE.get((sdir, table))
    if ent is None:
        ent = (np.zeros((1, 1), dtype=bool), np.zeros((1, 1, 6)), set())
    have, vals, done = ent
    need = [z for z in zs if z not in done]
    if need:
        rows = {z: _mass_table(sdir, z, table) for z in need}
        zmax = max(need)
        amax = max([int(ia.max()) for ia, _ in rows.values() if ia.size], default=0)
        if zmax >= have.shape[0] or amax >= have.shape[1]:
            shp = (max(zmax + 1, have.shape[0]), max(amax + 1, have.shape[1], 360))
            h2, v2 = np.zeros(shp, dtype=bool), np.zeros(shp + (6,))
            h2[: have.shape[0], : have.shape[1]] = have
            v2[: vals.shape[0], : vals.shape[1]] = vals
            have, vals = h2, v2
        for z, (ia, cols) in rows.items():
            have[z, ia] = True
            vals[z, ia] = cols
            done.add(z)
        _DENSE[(sdir, table)] = (have, vals, done)
    ok = (Zc > 0) & (Zc < have.shape[0]) & (Ac >= 0) & (Ac < have.shape[1])
    zi, ai = np.where(ok, Zc, 0), np.where(ok, Ac, 0)
    return ok & have[zi, ai], vals[zi, ai]


def _param_grid(params: Params | None, name: str, nz: int, nn: int, *extra: int) -> np.ndarray:
    """``float(params.at(name, Zix, Nix, *extra))`` on the whole ``(nz, nn)`` grid, 0 if absent."""
    out = np.zeros((nz, nn))
    if params is None or name not in params:
        return out
    from physics.hf.input.defaults import PARAM_SPECS

    spec = PARAM_SPECS[name.lower()]
    index_hi = (nz - 1, nn - 1, *extra)
    index_lo = (0, 0, *extra)
    if len(spec.dims) != len(index_hi) or any(
        not (lo <= i <= hi and lo <= j <= hi)
        for i, j, (lo, hi) in zip(index_lo, index_hi, spec.dims, strict=True)
    ):  # out of Fortran bounds: let `at` raise exactly as the cell-by-cell lookup does
        for Zix in range(nz):
            for Nix in range(nn):
                out[Zix, Nix] = float(params.at(name, Zix, Nix, *extra))
        return out
    o = spec.offsets
    rest = (e + oe for e, oe in zip(extra, o[2:], strict=True))
    sl = (slice(o[0], o[0] + nz), slice(o[1], o[1] + nn), *rest)
    out[:] = params[name].detach()[sl].to("cpu").numpy()
    return out


def masses(
    options: Options,
    params: Params | None = None,
    specmass_types: tuple[int, ...] = (0, 1, 2, 3, 4, 5, 6),
) -> Masses:
    """Masses, mass excesses, ground-state spins/parities/deformations and separation energies
    on TALYS's nucleus grid for the target and projectile in `options` (maxZ/maxN already capped
    as in nuclides.f90:140-141). `params` supplies `massnucleus`, `massexcess`, `beta2`
    (defaults if None). `specmass_types` are the particle types not skipped (parskip).

    The grid loops of masses.f90/separation.f90 are numpy array operations on the whole grid
    (the same float64 operations in the same order per cell), the mass tables are parsed once
    per run and Duflo-Zuker is memoised per (N, Z).

    TALYS: masses.f90:1 (masses), separation.f90:1 (separation)
    Test: A-struct
    """
    # COREX: `params` enters only through these three grids, so the build is memoised on them
    # and the options' values (a chain asks ~18 times per energy grid for the same target)
    nz, nn = options.maxZ + 5, options.maxN + 5
    grids = (_param_grid(params, "beta2", nz, nn, 0), _param_grid(params, "massnucleus", nz, nn),
             _param_grid(params, "massexcess", nz, nn))
    return _masses_of(options, tuple(specmass_types), tuple(g.tobytes() for g in grids))


@lru_cache(maxsize=64)
def _masses_of(options: Options, specmass_types: tuple[int, ...],
               grid_bytes: tuple[bytes, bytes, bytes]) -> Masses:
    """COREX: `masses`' build from the options and the beta2/massnucleus/massexcess grids (as
    bytes). `Masses` is frozen and nothing writes into its tensors."""
    c = talys_constants()
    amu = c["amu"]
    excmass = c["excmass"]
    parmass = c["parmass"]
    Zinit, Ninit = options.Zinit, options.Ninit
    Ainit = Zinit + Ninit
    maxZ, maxN = options.maxZ, options.maxN
    nz, nn = maxZ + 5, maxN + 5
    Zix_g = np.arange(nz)[:, None]
    Nix_g = np.arange(nn)[None, :]
    A_g = Ainit - Zix_g - Nix_g  # (nz, nn) int

    expmass = np.zeros((nz, nn))
    expmexc = np.zeros((nz, nn))
    thmass = np.zeros((nz, nn))
    thmexc = np.zeros((nz, nn))
    dumexc = np.zeros((nz, nn))
    beta4 = np.zeros((nz, nn))
    gsparity = np.ones((nz, nn))
    # strucinitial.f90: gsspin 0 for even A, 0.5 for odd
    gsspin = np.where(A_g % 2 == 0, 0.0, 0.5)
    beta2, mnuc, mexc = (np.frombuffer(b).reshape(nz, nn).copy() for b in grid_bytes)

    massmodel = options.massmodel
    theo_table = {1: "frdm", 0: "hfb", 2: "hfb", 3: "hfbd1m"}[massmodel]
    sdir = str(talys_structure_dir())
    # NATIVEX2 `struct`: the per-element loop as one gather per table from a dense (Z, A) copy of
    # the element tables (`_table_cells`, filled per element on first use): a cell takes the
    # table's row exactly when the loop's `sel` held it (the element's file has that A), the same
    # stores otherwise; float32 rounding as before.
    Zc = Zinit - Zix_g + np.zeros((1, nn), dtype=np.int64)
    zs = [Zinit - Zix for Zix in range(maxZ + 5) if Zinit - Zix > 0]
    if options.flagexpmass:
        have, vals = _table_cells(sdir, "ame2020", zs, Zc, A_g)
        expmass = np.where(have, vals[..., 0], expmass)
        expmexc = np.where(have, vals[..., 1], expmexc)
    have, vals = _table_cells(sdir, theo_table, zs, Zc, A_g)
    if massmodel != 0:
        thmass = np.where(have, vals[..., 0], thmass)
        thmexc = np.where(have, vals[..., 1], thmexc)
    beta2 = np.where(have & (beta2 == 0.0), vals[..., 2].astype(_F).astype(np.float64), beta2)
    beta4 = np.where(have, vals[..., 3].astype(_F).astype(np.float64), beta4)
    gsspin = np.where(have, vals[..., 4].astype(_F).astype(np.float64), gsspin)
    gsparity = np.where(have, vals[..., 5], gsparity)

    # user massnucleus wins, then massexcess, then the experimental/theoretical table mass
    by_mnuc = mnuc != 0.0
    by_mexc = ~by_mnuc & (mexc != 0.0)
    by_table = ~by_mnuc & ~by_mexc
    table_mass = np.where(options.flagexpmass & (expmass != 0.0), expmass, thmass)
    nucmass = np.where(by_mnuc, mnuc, np.where(by_mexc, A_g + mexc / amu, table_mass))
    exc_user = np.where(by_mnuc, (mnuc - A_g) * amu, mexc)
    expmexc = np.where(by_table, expmexc, exc_user)
    thmexc = np.where(by_table, thmexc, exc_user)
    flagduflo = massmodel == 0 or bool((by_table & (nucmass == 0.0)).any())

    k0 = options.k0
    if nucmass[PARZ[k0], PARN[k0]] == 0.0 and not flagduflo:
        raise ValueError("TALYS-error: Target nucleus not in masstable")

    if flagduflo:
        # COREX: the cell loop as whole-grid operations; `_duflo_grid` holds duflo(N, Z) per cell
        # (0 where Z <= 0 or N <= 0, the cells the loop skips) and `live` marks the cells it visits
        exc_g, live = _duflo_grid(Zinit, Ninit, nz, nn)
        dumexc = np.where(live, exc_g, dumexc)
        thmass1 = A_g + dumexc / amu
        take = live & ((nucmass == 0.0) | ((expmass == 0.0) & (massmodel == 0)))
        nucmass = np.where(take, thmass1, nucmass)
        if massmodel == 0:
            thmexc = np.where(live, dumexc, thmexc)

    sz, sn = maxZ + 3, maxN + 3
    specmass = np.zeros((sz, sn, 7))
    redumass = np.zeros((sz, sn, 7))
    m0 = nucmass[:sz, :sn]
    for typ in specmass_types:
        specmass[:, :, typ] = m0 / (m0 + parmass[typ])
        redumass[:, :, typ] = specmass[:, :, typ] * parmass[typ]

    S = np.zeros((sz, sn, 7))
    for typ in range(1, 7):
        zr, nr = PARZ[typ], PARN[typ]
        q = excmass[typ] * amu

        def pair(x, zr=zr, nr=nr):
            return x[:sz, :sn], x[zr : zr + sz, nr : nr + sn]

        e0, er = pair(expmexc)
        t0, tr = pair(thmexc)
        d0, dr = pair(dumexc)
        S[:, :, typ] = np.where(
            (e0 != 0.0) & (er != 0.0),
            er - e0 + q,
            np.where((t0 != 0.0) & (tr != 0.0), tr - t0 + q, dr - d0 + q),
        )

    def t(x):
        return torch.as_tensor(x, dtype=DTYPE)

    return Masses(
        Zinit=Zinit,
        Ninit=Ninit,
        maxZ=maxZ,
        maxN=maxN,
        mass_amu=t(nucmass),
        expmass_amu=t(expmass),
        expmexc_mev=t(expmexc),
        thmass_amu=t(thmass),
        thmexc_mev=t(thmexc),
        dumexc_mev=t(dumexc),
        beta2=t(beta2),
        beta4=t(beta4),
        gsspin=t(gsspin),
        gsparity=t(gsparity),
        s_mev=t(S),
        specmass=t(specmass),
        redumass_amu=t(redumass),
        flagduflo=flagduflo,
    )


def separation_energy(m: Masses, Z: int, A: int, particle: int) -> float:
    """S [MeV] for removing `particle` (type 1..6) from nucleus (Z, A), from the grid.

    TALYS: separation.f90:1 (separation)
    Test: A-struct
    """
    Zix, Nix = m.index(Z, A)
    return float(m.s_mev[Zix, Nix, particle])
