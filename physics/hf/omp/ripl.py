"""RIPL-3 optical-model retrieval: the `om_retrieve` path TALYS takes for `riplomp`.

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

Task: T4 (physics/hf/CONTRACT.md §7), follow-up T4RIPL. Acceptance test: A-omppar (§6).

Why this file exists. TALYS's default neutron OMP for the actinides (Z 90-97, A 228-249) is not
Koning-Delaroche but RIPL potential **2408** (Capote-Soukhovitskii-Chiba-Quesada, a dispersive
coupled-channels rigid-rotor potential). `input_omppar.f90:179-186` switches `riplomp(1) = 2408`
and `flagriplomp` on for those targets, and `omppar.f90:271-376` then

1. copies `structure/optical/ripl/{om-parameter-u.dat,gs-mass-sp.dat}` to the run directory,
2. builds a fixed energy grid up to `enincmax + 12` MeV (:296-315),
3. checks the Z/A range in `om-index.txt` (:320-342),
4. calls `riplomp_mod` -> `om_retrieve::retrieve`, which writes `omp-table.dat`,
5. reads that table back into `eomp/vomp/omplines` and takes `Ef` from its header (:361-387).

`opticalnp.f90:183-215` then *linearly interpolates that table* instead of evaluating KD03, so
every number in `omppar_n.out` for an actinide comes out of the printed table, at the precision
of the print formats in `om_retrieve.f:3206-3212` (V f8.3, everything else f7.4/f8.4). This
module reproduces steps 1-5 exactly, rounding included, and returns the `OMPTable` that
`parameters.opticalnp` already knows how to interpolate.

TALYS routines ported here (file:line of the subroutine/function statement):
    om_retrieve.f:715  (omin30)          the RIPL library reader
    om_retrieve.f:872  (setup)           eta, encoul, masses
    om_retrieve.f:3615 (masses)          Fermi energy from gs-mass-sp.dat
    om_retrieve.f:3660 (energy2)         mass-excess lookup
    om_retrieve.f:2494 (optmod)          the potential itself, per energy
    om_retrieve.f:3265 (bcoget)          Koning b-coefficients
    om_retrieve.f:3892 (tableset)        the omp-table.dat header
    om_retrieve.f:3954 (Vhf)             Morillon-Romain non-local real potential
    om_retrieve.f:3987 (xkine)           lab -> cm factor
    om_retrieve.f:4041 (DOM_INT_Wv)      analytical dispersive integral, volume
    om_retrieve.f:4115      DOM_INT_Ws  analytical dispersive integral, surface (the
                                       statement is split over two records, so it carries no
                                       `file:line (routine)` anchor)
    om_retrieve.f:4203 (zfi)             exp(z) E1(z), Raynal
    om_retrieve.f:4240 (EIn)             Ei(x)
    om_retrieve.f:4317 (DOM_int_T1)      non-locality, E' << 0
    om_retrieve.f:4398 (DOM_int_T2)      non-locality, E' >> 0
    om_retrieve.f:4822 (WVf)             Wv(E)
    om_retrieve.f:4855 (WDf)             Wd(E)
    omppar.f90:271 (the riplomp block of omppar)

Not ported: the numerical dispersive integral (`idr <= -2`, `DOM_int` Gauss-Legendre), the soft
rotator (`imodel = 3`), Duflo-Zuker masses for nuclides missing from `gs-mass-sp.dat`, and the
coupling-scheme / ECIS-input side of `retrieve` (TALYS discards `ecis.inp`; it reads only
`omp-table.dat`, and takes its own deformations from `structure/deformation`). Each raises.

Everything here is plain float64 numpy: `om_retrieve` is `implicit real*8 (a-h,o-z)` throughout,
so there is no single-precision truncation inside it. The two places TALYS *is* single precision
are reproduced on purpose: the incident grid `Eripl` is accumulated in `real(sgl)`
(`omppar.f90:130-139`), and the table is read back from text, so every value is the f7.3/f8.3/
f7.4/f8.4 print of the double it came from.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
from functools import cache
from pathlib import Path

import numpy as np

from physics.hf.core.constants import talys_structure_path

NDIM2 = 13  # om_retrieve.f:274
NDIM3 = 25

AMU0C2 = 931.494013  # om_retrieve.f:3634
HBARC = 197.3269601  # om_retrieve.f:3636


def _s(x: float) -> float:
    """A Fortran default-`real` literal or expression, as it reaches a real*8 context.
    `om_retrieve` writes `atar**(1./3.)` (single) in the geometry formulas and
    `atar**(1.d0/3.d0)` (double) in the Coulomb shift; both are kept apart here."""
    return float(np.float32(x))


_T1, _T2 = _s(1.0 / 3.0), _s(2.0 / 3.0)  # the `1./3.` and `2./3.` of om_retrieve.f:2612-2640

# particle index of (izproj, iaproj), om_retrieve.f:890-896
_PARSYM = {(0, 1): "n", (1, 1): "p", (1, 2): "d", (1, 3): "t", (2, 3): "h", (2, 4): "a"}


class RIPLNotPorted(NotImplementedError):
    """A RIPL potential whose `om_retrieve` branch this module does not reproduce."""


# ------------------------------------------------------------------------------ library reader
_NUM = re.compile(r"([0-9.])([+-])([0-9]+)\s*$")


def _fnum(tok: str) -> float:
    """One list-directed real, in the RIPL exponent shorthand (`1.037-2` = 1.037e-2)."""
    try:
        return float(tok)
    except ValueError:
        return float(_NUM.sub(r"\1e\2\3", tok))


class _Reader:
    """A Fortran list-directed reader over a record (= line) stream: every `read` starts a new
    record and consumes as many records as it needs values."""

    def __init__(self, lines: list[str], pos: int = 0):
        self.lines, self.pos = lines, pos
        self.skip = False  # CENGSETUP: reals are counted, not converted (an entry being passed over)

    def line(self) -> str:
        s = self.lines[self.pos]
        self.pos += 1
        return s

    def tokens(self):
        """The token stream of one read statement, pulling further records on demand."""
        while True:
            yield from (_fnum(t) for t in self.line().split())

    def reals(self, n: int) -> list[float]:
        if self.skip:
            got = 0
            while got < n:
                got += len(self.line().split())
            if got > n:
                raise ValueError(f"list-directed read of {n} values got {got}")
            return [0.0] * n
        return self._values(n)

    def _values(self, n: int) -> list[float]:
        out: list[float] = []
        while len(out) < n:
            out.extend(_fnum(t) for t in self.line().split())
        if len(out) > n:
            raise ValueError(f"list-directed read of {n} values got {len(out)}")
        return out

    def ints(self, n: int) -> list[int]:
        return [int(x) for x in self._values(n)]


@dataclass
class RIPLPotential:
    """One entry of `om-parameter-u.dat`, as `omin30` leaves it in the module globals."""

    iref: int
    author: str
    emin: float
    emax: float
    izmin: int
    izmax: int
    iamin: int
    iamax: int
    imodel: int
    izproj: int
    iaproj: int
    irel: int
    idr: int
    jrange: list[int]  # 1-based index 1..6 in [0]..[5]
    epot: np.ndarray  # (6, nj)
    rco: np.ndarray  # (6, nj, 13)
    aco: np.ndarray  # (6, nj, 13)
    pot: np.ndarray  # (6, nj, 25)
    jcoul: int
    ecoul: np.ndarray
    rcoul0: np.ndarray
    rcoul: np.ndarray
    rcoul1: np.ndarray
    rcoul2: np.ndarray
    beta: np.ndarray
    acoul: np.ndarray
    rcoul3: np.ndarray
    # imodel 1/4 rigid-rotor coupling scheme, kept for reference (TALYS ignores it)
    isotopes: list[dict] = field(default_factory=list)

    def p(self, i: int, j: int, n: int) -> float:
        """`pot(i, j, n)`, 1-based as in the Fortran."""
        return float(self.pot[i - 1, j - 1, n - 1])

    def r(self, i: int, j: int, n: int) -> float:
        return float(self.rco[i - 1, j - 1, n - 1])

    def a(self, i: int, j: int, n: int) -> float:
        return float(self.aco[i - 1, j - 1, n - 1])


def _read_entry(rd: _Reader, want: int | None = None) -> RIPLPotential | None:
    """One potential, exactly as `omin30` reads it (om_retrieve.f:715-857).

    With `want`, an entry of another reference number is only walked past (the same records
    consumed, its reals counted instead of converted) and None is returned."""
    iref = rd.ints(1)[0]
    rd.skip = want is not None and iref != want
    try:
        return _read_entry_body(rd, iref, None if rd.skip else True)
    finally:
        rd.skip = False


def _read_entry_body(rd: _Reader, iref: int, keep: bool | None) -> RIPLPotential | None:
    author = rd.line()
    rd.line()  # refer
    for _ in range(4):  # summary(320) through format (80a1)
        rd.line()
    emin, emax = rd.reals(2)
    izmin, izmax = rd.ints(2)
    iamin, iamax = rd.ints(2)
    imodel, izproj, iaproj, irel, idr = rd.ints(5)
    jrange = [0] * 6
    nj = 1
    epot_l: list[list[float]] = [[] for _ in range(6)]
    rco_l: list[list[list[float]]] = [[] for _ in range(6)]
    aco_l: list[list[list[float]]] = [[] for _ in range(6)]
    pot_l: list[list[list[float]]] = [[] for _ in range(6)]
    for m in range(6):
        jrange[m] = rd.ints(1)[0]
        if jrange[m] == 0:
            continue
        for _ in range(abs(jrange[m])):
            epot_l[m].append(rd.reals(1)[0])
            rco_l[m].append(rd.reals(NDIM2))
            aco_l[m].append(rd.reals(NDIM2))
            pot_l[m].append(rd.reals(NDIM3))
        nj = max(nj, abs(jrange[m]))
    epot = np.zeros((6, nj))
    rco = np.zeros((6, nj, NDIM2))
    aco = np.zeros((6, nj, NDIM2))
    pot = np.zeros((6, nj, NDIM3))
    for m in range(6):
        for j, v in enumerate(epot_l[m]):
            epot[m, j] = v
            rco[m, j] = rco_l[m][j]
            aco[m, j] = aco_l[m][j]
            pot[m, j] = pot_l[m][j]
    jcoul = rd.ints(1)[0]
    nc = max(jcoul, 1)
    ecoul, rcoul0, rcoul, rcoul1 = (np.zeros(nc) for _ in range(4))
    rcoul2, beta, acoul, rcoul3 = (np.zeros(nc) for _ in range(4))
    for j in range(max(jcoul, 0)):
        vals = rd.reals(8)
        ecoul[j], rcoul0[j], rcoul[j], rcoul1[j] = vals[0], vals[1], vals[2], vals[3]
        rcoul2[j], beta[j], acoul[j], rcoul3[j] = vals[4], vals[5], vals[6], vals[7]
    isotopes: list[dict] = []
    if imodel in (1, 4):  # om_retrieve.f:779-795, :829-847
        for _ in range(rd.ints(1)[0]):
            tok = rd.tokens()
            iz, ia, ncoll, lmax, idef = (int(next(tok)) for _ in range(5))
            bandk = next(tok)
            defs = [next(tok) for _ in range(len(range(2, idef + 1, 2)))]
            levels = [rd.reals(9 if imodel == 4 else 3) for _ in range(ncoll)]
            isotopes.append(
                dict(iz=iz, ia=ia, ncoll=ncoll, lmax=lmax, idef=idef, bandk=bandk,
                     defs=defs, levels=levels)
            )  # fmt: skip
    elif imodel == 2:  # om_retrieve.f:796-807
        for _ in range(rd.ints(1)[0]):
            iz, ia, nvib = rd.ints(3)
            levels = [rd.reals(6) for _ in range(nvib)]
            isotopes.append(dict(iz=iz, ia=ia, ncoll=nvib, levels=levels))
    elif imodel == 3:  # om_retrieve.f:809-827
        for _ in range(rd.ints(1)[0]):
            iz, ia, ncoll = rd.ints(3)
            for _ in range(3):
                rd.reals(6 if _ < 2 else 5)
            levels = [rd.reals(7) for _ in range(ncoll)]
            isotopes.append(dict(iz=iz, ia=ia, ncoll=ncoll, levels=levels))
    rd.line()  # the `read(ki,1,end=999) idum` separator
    if keep is None:
        return None
    return RIPLPotential(
        iref=iref, author=author.strip(), emin=emin, emax=emax, izmin=izmin, izmax=izmax,
        iamin=iamin, iamax=iamax, imodel=imodel, izproj=izproj, iaproj=iaproj, irel=irel, idr=idr,
        jrange=jrange, epot=epot, rco=rco, aco=aco, pot=pot, jcoul=jcoul, ecoul=ecoul,
        rcoul0=rcoul0, rcoul=rcoul, rcoul1=rcoul1, rcoul2=rcoul2, beta=beta, acoul=acoul,
        rcoul3=rcoul3, isotopes=isotopes,
    )  # fmt: skip


def _ripl_dir(structure: Path | None = None) -> Path:
    base = structure if structure is not None else talys_structure_path()
    return base / "optical" / "ripl"


@cache
def _library_lines(path: str) -> tuple[str, ...]:
    return tuple(Path(path).read_text().splitlines())


@cache
def read_om_parameter(iref: int, structure_dir: str) -> RIPLPotential:
    """The `om-parameter-u.dat` entry with reference number `iref`, read the way `omin30` reads
    the library: sequentially from the top until `iref == irefget` (om_retrieve.f:465-471).

    TALYS: om_retrieve.f:715 (omin30)
    Test: A-omppar
    """
    rd = _Reader(list(_library_lines(str(Path(structure_dir) / "om-parameter-u.dat"))))
    while rd.pos < len(rd.lines):
        entry = _read_entry(rd, want=iref)
        if entry is not None:
            return entry
    raise KeyError(f"RIPL OMP {iref} not in om-parameter-u.dat")


@cache
def read_om_index(structure_dir: str) -> dict[int, tuple[str, int, int, int, int, float, float]]:
    """`om-index.txt` as `omppar` reads it: reference number -> (particle, Zbeg, Zend, Abeg,
    Aend, Ebeg, Efin), fixed-width per omppar.f90:327-328.

    TALYS: omppar.f90:322-341
    Test: A-omppar
    """
    lines = _library_lines(str(Path(structure_dir) / "om-index.txt"))
    out: dict[int, tuple[str, int, int, int, int, float, float]] = {}
    for line in lines[3:]:  # read(31,'(//)') skips three records
        if len(line) < 60:
            continue
        try:  # (i4, 3x, a1, 23x, i2, 1x, i2, 2x, i3, 1x, i3, 2x, f5.1, 1x, f5.1)
            rnum = int(line[0:4])
            part = line[7:8]
            zbeg, zend = int(line[31:33]), int(line[34:36])
            abeg, aend = int(line[38:41]), int(line[42:45])
            ebeg, efin = float(line[46:51]), float(line[52:57])
        except ValueError:
            continue
        out.setdefault(rnum, (part, zbeg, zend, abeg, aend, ebeg, efin))
    return out


# ------------------------------------------------------------------------------ masses
@cache
def _gs_mass_sp(structure_dir: str) -> dict[int, tuple[float, float]]:
    """`gs-mass-sp.dat`: za -> (mass excess MeV, spin/parity code), read as
    `(5(i7,f11.6,f7.1))` (om_retrieve.f:3693).

    TALYS: om_retrieve.f:3660 (energy2)
    Test: A-omppar
    """
    lines = _library_lines(str(Path(structure_dir) / "gs-mass-sp.dat"))
    # read(k13,'(20a4)') bcd(120) consumes six records, then read(k13,'(i7)') nmass
    nmass = int(lines[6][:7])
    out: dict[int, tuple[float, float]] = {}
    n = 0
    for line in lines[7:]:
        for c in range(5):
            f = line[c * 25 : (c + 1) * 25]
            if len(f) < 25 or not f.strip():
                break
            out[int(f[0:7])] = (float(f[7:18]), float(f[18:25]))
            n += 1
            if n == nmass:
                return out
    return out


def _excess(za: int, structure_dir: str) -> float:
    table = _gs_mass_sp(structure_dir)
    if za not in table:
        raise RIPLNotPorted(
            f"za {za} is not in gs-mass-sp.dat; om_retrieve would fall back to Duflo-Zuker "
            "(om_retrieve.f:3774), which is not ported"
        )
    return table[za][0]


def fermi_energy(Z: int, A: int, izproj: int, iaproj: int, structure_dir: str) -> float:
    """`efermi` of `masses`: -(S_n(A) + S_n(A+1))/2 for an incident neutron, from the RIPL
    mass-excess table, truncated to four decimals.

    TALYS: om_retrieve.f:3615 (masses) lines 3649-3655
    Test: A-omppar
    """
    izatar = 1000 * Z + A
    izaproj = 1000 * izproj + iaproj
    projex = _excess(izaproj, structure_dir) if izaproj != 0 else 0.0
    tarexm1 = _excess(izatar - izaproj, structure_dir)
    tarexp1 = _excess(izatar + izaproj, structure_dir)
    efermi = -0.5 * (tarexm1 - tarexp1 + 2.0 * projex)
    return float(round(efermi * 10000)) / 10000  # ":reduced to four numbers after the dot"


# ------------------------------------------------------------------------------ dispersive package
def _ein(x: float) -> float:
    """Ei(x) by its series (om_retrieve.f:4240)."""
    out = 0.57721566490153 + math.log(abs(x))
    fac = 1.0
    for n in range(1, 101):
        fac *= n
        out += x**n / (n * fac)
    return out


def _zfi(za: complex) -> complex:
    """exp(z) E1(z), J. Raynal (om_retrieve.f:4203)."""
    if za == 0:
        return 0.0 + 0.0j
    far = abs(za.real + 18.5) >= 25.0 or (
        math.sqrt(max(625.0 - (za.real + 18.5) ** 2, 0.0)) / 1.665 < abs(za.imag)
    )
    if not far:
        out = -0.57721566490153 - np.log(complex(za))
        y = 1.0 + 0.0j
        for m in range(1, 2001):
            y = -y * za / m
            if abs(y) < 1.0e-15 * abs(out):
                break
            out = out - y / m
        return complex(np.exp(complex(za)) * out)
    out = 0.0 + 0.0j
    for i in range(1, 21):
        aj = 21 - i
        out = aj / (za + out)
        out = aj / (1.0 + out)
    return 1.0 / (out + za)


def dom_int_wv(ef: float, ep: float, av: float, bv: float, einc: float, n: int):
    """Analytical dispersive integral of Wv(E) = Av (E-Ep)^n / ((E-Ep)^n + Bv^n) and its
    derivative (Quesada et al., CPC 153 (2003) 97).

    TALYS: om_retrieve.f:4041 (DOM_INT_Wv)
    Test: A-omppar
    """
    pi = math.pi
    is_ = 1
    e = einc
    if einc <= ef:
        e = 2.0 * ef - einc
        is_ = -1
    e0 = ep - ef
    ex = e - ef
    eplus = ex + e0
    emin = ex - e0
    res_emin = emin**n / (emin**n + bv**n)
    der_emin = (
        emin ** (n - 1)
        * (emin**n + bv**n * (1.0 + n * math.log(abs(emin))))
        / (emin**n + bv**n) ** 2
    )
    res_eplus = -(eplus**n) / (eplus**n + bv**n)
    der_eplus = (
        -(eplus ** (n - 1))
        * (eplus**n + bv**n * (1.0 + n * math.log(eplus)))
        / (eplus**n + bv**n) ** 2
    )
    fs = 0.0 + 0.0j
    ds = 0.0 + 0.0j
    for j in range(1, n + 1):
        pj = bv * np.exp(1j * (2 * j - 1) / n * pi)
        zj = pj * (2 * pj + eplus - emin) * ex / ((pj + e0) * (pj + eplus) * (pj - emin))
        fs = fs + zj * np.log(-pj)
        ds = ds + 2 * pj * (ex * ex + (pj + e0) ** 2) * np.log(-pj) / (
            (pj + eplus) ** 2 * (pj - emin) ** 2
        )
    rs, rds = float(fs.real), float(ds.real)
    val = -av / pi * is_ * (rs / n + (res_eplus * math.log(eplus) + res_emin * math.log(abs(emin))))
    der = -av / pi * is_ * (rds / n + (der_eplus + der_emin))
    return val, der


def dom_int_ws(ef: float, ep: float, a_s: float, bs: float, cs: float, einc: float, m: int):
    """Analytical dispersive integral of Ws(E) = As (E-Ep)^m/((E-Ep)^m + Bs^m) exp(-Cs (E-Ep))
    and its derivative.

    TALYS: om_retrieve.f:4115, DOM_INT_Ws (its `DOUBLE PRECISION FUNCTION` is split over two
    records, so it carries no `file:line (routine)` anchor)
    Test: A-omppar
    """
    pi = math.pi
    is_ = 1
    e = einc
    if einc <= ef:
        e = 2.0 * ef - einc
        is_ = -1
    e0 = ep - ef
    ex = e - ef
    eplus = ex + e0
    emin = ex - e0
    res_emin = emin**m / (emin**m + bs**m)
    der_emin = -(emin ** (m - 1)) * (
        emin**m
        + bs**m
        + (-cs * emin ** (m + 1) + bs**m * (-cs * emin + m))
        * math.exp(-cs * emin)
        * _ein(cs * emin)
    ) / (emin**m + bs**m) ** 2
    res_eplus = -(eplus**m) / (eplus**m + bs**m)
    der_eplus = (
        eplus ** (m - 1)
        * (
            eplus**m
            + bs**m
            + (cs * eplus ** (m + 1) + bs**m * (cs * eplus + m))
            * math.exp(cs * eplus)
            * _ein(-cs * eplus)
        )
        / (eplus**m + bs**m) ** 2
    )
    fs = 0.0 + 0.0j
    ds = 0.0 + 0.0j
    for j in range(1, m + 1):
        pj = bs * np.exp(1j * (2 * j - 1) / m * pi)
        zj = pj * (2 * pj + eplus - emin) * ex / (pj + e0) / (pj + eplus) / (pj - emin)
        fs = fs + zj * _zfi(-pj * cs)
        ds = ds + 2 * pj * (ex * ex + (pj + e0) ** 2) * _zfi(-pj * cs) / (
            (pj + eplus) ** 2 * (pj - emin) ** 2
        )
    rs, rds = float(fs.real), float(ds.real)
    val = (
        a_s
        / pi
        * is_
        * (
            rs / m
            - res_eplus * math.exp(cs * eplus) * _ein(-cs * eplus)
            - res_emin * math.exp(-cs * emin) * _ein(cs * emin)
        )
    )
    der = a_s / pi * is_ * (rds / m + der_eplus + der_emin)
    return val, der


def dom_int_t1(ef: float, ea: float, e: float) -> float:
    """Non-locality term T1(E' << 0), CPC eq. (20).

    TALYS: om_retrieve.f:4317 (DOM_int_T1)
    Test: A-omppar
    """
    pi = math.pi
    ex = e - ef
    ea2 = ea**2
    eax = abs(ex + ea)
    t11 = 0.5 * math.log(ea) / ex
    t12 = ((2 * ea + ex) * math.log(ea) + 0.5 * pi * ex) / (2.0 * (eax**2 + ea2))
    t13 = -(eax**2) * math.log(eax) / (ex * (eax**2 + ea2))
    return ex / pi * (t11 + t12 + t13)


def dom_int_t2(ef: float, ea: float, e: float) -> float:
    """Non-locality term T2(E' >> 0), PRC 94 (2016) 064605 eq. (24).

    TALYS: om_retrieve.f:4398 (DOM_int_T2)
    Test: A-omppar
    """
    pi = math.pi
    el = ef + ea
    out = (
        1.0
        / pi
        * (
            math.sqrt(abs(ef)) * math.atan((2 * math.sqrt(el * abs(ef))) / (el - abs(ef)))
            + el**1.5 / (2 * ef) * math.log(ea / el)
        )
    )
    if e > el:
        out += (
            1.0
            / pi
            * (
                math.sqrt(e)
                * math.log((math.sqrt(e) + math.sqrt(el)) / (math.sqrt(e) - math.sqrt(el)))
                + 1.5 * math.sqrt(el) * math.log((e - el) / ea)
                + el**1.5 / (2 * e) * math.log(el / (e - el))
            )
        )
    elif e == el:
        out += 1.0 / pi * 1.5 * math.sqrt(el) * math.log((2 ** (4.0 / 3.0) * el) / ea)
    elif e > 0.0:
        out += (
            1.0
            / pi
            * (
                math.sqrt(e)
                * math.log((math.sqrt(e) + math.sqrt(el)) / (math.sqrt(el) - math.sqrt(e)))
                + 1.5 * math.sqrt(el) * math.log((el - e) / ea)
                + el**1.5 / (2.0 * e) * math.log(el / (el - e))
            )
        )
    elif e == 0.0:
        out += 1.0 / pi * 1.5 * math.sqrt(el) * math.log(el / ea) + 0.5 * math.sqrt(el)
    else:
        out += (
            1.0
            / pi
            * (
                -math.sqrt(abs(e)) * math.atan(2 * math.sqrt(el * abs(e)) / (el - abs(e)))
                + 1.5 * math.sqrt(el) * math.log((el - e) / ea)
                + el**1.5 / (2.0 * e) * math.log(el / (el - e))
            )
        )
    return out


def _wvf(a: float, b: float, ep: float, ef: float, e: float, n: int) -> float:
    """Wv(E). TALYS: om_retrieve.f:4822 (WVf)"""  # noqa: D403
    if e <= ef:
        e = 2.0 * ef - e
    if e <= ep:
        return 0.0
    ee = (e - ep) ** n
    return a * ee / (ee + b**n)


def _vhf(einp: float, alpha_pb: float, beta_pb: float, gamma_pb: float, amu: float) -> float:
    """Morillon-Romain non-local real potential, PRC 70 (2004) 014601.

    TALYS: om_retrieve.f:3954 (Vhf)
    """
    miu = amu / HBARC**2
    coef1 = -0.5 * beta_pb**2 * miu
    coef2 = 4.0 * (gamma_pb * miu) ** 2
    v = alpha_pb
    for _ in range(10000):
        vtmp = v
        etmp = einp - vtmp
        v = alpha_pb * math.exp(coef1 * etmp + coef2 * etmp**2)
        if abs(v - vtmp) <= 0.0001:
            break
    return v


def _xkine(ei: float, tarmas: float, projmas: float, irel: int) -> tuple[float, float]:
    """(amu, xkine) of `xkine` (om_retrieve.f:3987); returns the reduced mass in MeV."""
    mtot = tarmas + projmas
    if irel == 0:
        amu = projmas * tarmas / mtot * AMU0C2
        return amu, tarmas / mtot
    p2 = (ei * (ei + 2.0 * AMU0C2 * projmas)) / (
        (1.0 + projmas / tarmas) ** 2 + 2.0 * ei / (AMU0C2 * tarmas)
    )
    etoti = math.sqrt((AMU0C2 * projmas) ** 2 + p2)
    etott = math.sqrt((AMU0C2 * tarmas) ** 2 + p2)
    return etoti * etott / (etoti + etott), etott / (etoti + etott)


# ------------------------------------------------------------------------------ optmod
def _bcoget(p: RIPLPotential, j: int, atar: float, eta: float) -> np.ndarray:
    """The Koning b-coefficients b(i, j, 1:15), 1-based in i and the last index.

    TALYS: om_retrieve.f:3265 (bcoget)
    Test: A-omppar
    """
    b = np.zeros((7, 16))
    b[1, 5] = p.p(1, j, 9)
    b[1, 1] = p.p(1, j, 1) + p.p(1, j, 2) * atar + p.p(1, j, 8) * eta
    if p.p(1, j, 24) < 3:
        soukho = p.p(1, j, 14) + p.p(1, j, 15) * atar + p.p(1, j, 16)
        if p.p(1, j, 20) != 0.0 and soukho != 0.0:
            b[1, 1] = (
                p.p(1, j, 1)
                + p.p(1, j, 2) * atar
                + p.p(1, j, 8) * eta
                + p.p(1, j, 20) * eta / soukho
            )
        b[1, 2] = p.p(1, j, 3) + p.p(1, j, 4) * atar
        b[1, 3] = p.p(1, j, 5) + p.p(1, j, 6) * atar
        b[1, 4] = p.p(1, j, 7)
        b[1, 5] = p.p(1, j, 9)
        b[1, 11] = p.p(1, j, 10) + p.p(1, j, 11) * atar
        b[1, 12] = p.p(1, j, 12)
        b[1, 13] = p.p(1, j, 16) + p.p(1, j, 2) * atar
        b[1, 14] = p.p(1, j, 17)
        b[1, 15] = p.p(1, j, 14) + p.p(1, j, 15) * atar
        if p.p(1, j, 20) == 0.0 and soukho == 0.0:
            b[1, 13] = p.p(1, j, 16)
            b[1, 15] = 1.0
    if p.p(1, j, 24) == 3:  # Li & Cai
        b[1, 15] = 1.0
        b[1, 5] = 0.0
        if b[1, 1] == 0.0:
            raise RIPLNotPorted("Li & Cai OMP with b(1,j,1) = 0")
        b[1, 2] = -(p.p(1, j, 3) + p.p(1, j, 4) * eta) / b[1, 1]
    b[2, 6] = p.p(2, j, 1) + p.p(2, j, 2) * atar + p.p(2, j, 8) * eta
    b[2, 7] = p.p(2, j, 3) + p.p(2, j, 4) * atar + p.p(2, j, 9) * eta
    b[4, 8] = (
        p.p(4, j, 1)
        + p.p(4, j, 8) * eta
        + p.p(4, j, 7) * atar
        + p.p(4, j, 9) * atar ** (-1.0 / 3.0)
    )
    if p.p(4, j, 3) != 0.0:
        b[4, 9] = (
            p.p(4, j, 2)
            + p.p(4, j, 10) * atar
            + p.p(4, j, 3) / (1.0 + math.exp((atar - p.p(4, j, 4)) / p.p(4, j, 5)))
        )
    else:
        b[4, 9] = p.p(4, j, 2) + p.p(4, j, 10) * atar
    b[4, 10] = p.p(4, j, 6) + p.p(4, j, 11) * atar
    b[4, 12] = p.p(4, j, 12)
    b[5, 11] = p.p(5, j, 10) + p.p(5, j, 11) * atar
    b[5, 12] = p.p(5, j, 12)
    if p.p(1, j, 24) == 2:
        b[5, 1] = p.p(5, j, 1) + p.p(5, j, 2) * atar + p.p(5, j, 8) * eta
        b[5, 2] = p.p(5, j, 3) + p.p(5, j, 4) * atar
        b[5, 3] = p.p(5, j, 5) + p.p(5, j, 6) * atar
    b[6, 6] = p.p(6, j, 1)
    b[6, 7] = p.p(6, j, 3)
    return b


@dataclass(frozen=True)
class _Kinematics:
    atar: float
    ztar: float
    eta: float
    encoul: float
    efermi: float
    tarmas: float
    projmas: float


def _kinematics(p: RIPLPotential, Z: int, A: int, structure_dir: str) -> _Kinematics:
    """`setup` + `masses` (om_retrieve.f:872-914, :3615)."""
    atar, ztar = float(A), float(Z)
    izatar = 1000 * Z + A
    izaproj = 1000 * p.izproj + p.iaproj
    tarmas = A + _excess(izatar, structure_dir) / AMU0C2
    projmas = p.iaproj + (_excess(izaproj, structure_dir) / AMU0C2 if izaproj else 0.0)
    return _Kinematics(
        atar=atar,
        ztar=ztar,
        eta=1.0 - (2.0 * ztar / atar),
        encoul=_s(0.4) * ztar / atar**_T1,
        efermi=fermi_energy(Z, A, p.izproj, p.iaproj, structure_dir),
        tarmas=tarmas,
        projmas=projmas,
    )


def optmod(p: RIPLPotential, kin: _Kinematics, el: float, nonegw: int = 1) -> dict[str, float]:
    """One row of `omp-table.dat`: the 6 x (depth, radius, diffuseness) ECIS reads, at lab energy
    `el`. `nonegw` is `1` when TALYS calls the retrieval (`Calc_Type = -2`, omppar.f90:356), which
    clips negative absorptive depths.

    TALYS: om_retrieve.f:2494 (optmod)
    Test: A-omppar
    """
    atar, ztar, eta, encoul = kin.atar, kin.ztar, kin.eta, kin.encoul
    rlib = np.zeros(7)
    alib = np.zeros(7)
    vlib = np.zeros(7)
    optr = np.zeros(7)
    opta = np.zeros(7)
    optv = np.zeros(7)
    b = np.zeros((7, 16))
    vhfnum = vsonum = 0.0
    ahf = a_s = aav = 0.0
    alpha = 0.0
    rc, ac = 0.0, 1.0
    ef = kin.efermi
    ep = ef
    ea = 1000.1
    if p.jcoul >= 1:  # om_retrieve.f:2556-2570
        jc = 1
        for j in range(1, p.jcoul + 1):
            if el > p.ecoul[j - 1]:
                jc = j + 1
        jc = min(jc, p.jcoul)
        rc = (
            p.rcoul0[jc - 1] * atar ** -_T1
            + p.rcoul[jc - 1]
            + p.rcoul1[jc - 1] * atar ** -_T2
            + p.rcoul2[jc - 1] * atar ** _s(-5.0 / 3.0)
            + p.rcoul3[jc - 1]
        )
        if p.beta[jc - 1] > 0.0:
            raise RIPLNotPorted("non-local potential (beta > 0): ECIS cannot use it either")
        ac = p.acoul[jc - 1]
    encoul2 = _s(1.73) * ztar / (rc * atar**_T1) if rc > 0.0 else 0.0
    vdcoul = vscoul = vvcoul = 0.0
    for i in range(1, 7):
        vcshift = 0.0
        if p.izproj == 1 and p.p(i, 1, 25) > 0.0:
            vcshift = p.p(i, 1, 25) * ztar / atar ** (1.0 / 3.0)
        vc = 0.0
        derdwv = 0.0
        alphav = 0.0
        jab = abs(p.jrange[i - 1])
        if p.jrange[i - 1] < 1:  # `go to 300`, which still runs the three assignments below
            if i == 1:
                vhfnum = vlib[1]
            if i == 2:
                alpha = alphav
            if i == 5:
                vsonum = vlib[5]
            continue
        jp = 1
        for j in range(1, jab + 1):
            if el > p.epot[i - 1, j - 1]:
                jp = j + 1
        j = min(jp, jab)
        ef = kin.efermi
        if p.p(i, j, 18) != 0.0:
            ef = p.p(i, j, 18) + p.p(i, j, 19) * atar
        elf = el - ef - vcshift
        iaref = 0
        if round(p.p(i, j, 24)) == 1 and p.p(i, j, 23) > 0.0:
            iaref = int(round(p.p(i, j, 23)))
        if p.r(i, j, 13) == 0.0:  # om_retrieve.f:2612-2626
            rlib[i] = (
                abs(p.r(i, j, 1))
                + p.r(i, j, 3) * eta
                + p.r(i, j, 4) / atar
                + p.r(i, j, 5) / math.sqrt(atar)
                + p.r(i, j, 6) * atar**_T2
                + p.r(i, j, 7) * atar
                + p.r(i, j, 8) * atar**2
                + p.r(i, j, 9) * atar**3
                + p.r(i, j, 10) * atar**_T1
                + p.r(i, j, 11) * atar ** -_T1
                + p.r(i, j, 2) * el
                + p.r(i, j, 12) * el * el
            )
        else:
            nn = int(p.r(i, j, 7))
            rlib[i] = (abs(p.r(i, j, 1)) + p.r(i, j, 2) * atar) * (
                1.0
                - (p.r(i, j, 3) + p.r(i, j, 4) * atar)
                * elf**nn
                / (elf**nn + (p.r(i, j, 5) + p.r(i, j, 6) * atar) ** nn)
            )
        alib[i] = (
            abs(p.a(i, j, 1))
            + p.a(i, j, 2) * el
            + p.a(i, j, 3) * eta
            + p.a(i, j, 4) / atar
            + p.a(i, j, 5) / math.sqrt(atar)
            + p.a(i, j, 6) * atar**_T2
            + p.a(i, j, 7) * atar
            + p.a(i, j, 8) * atar**2
            + p.a(i, j, 9) * atar**3
            + p.a(i, j, 10) * atar**_T1
            + p.a(i, j, 11) * atar ** -_T1
        )
        if iaref == 0:
            optr[i], opta[i] = rlib[i], alib[i]
        else:
            optr[i] = p.r(i, j, 1) + p.r(i, j, 7) * (atar - iaref)
            opta[i] = p.a(i, j, 1) + p.a(i, j, 7) * (atar - iaref)
        if p.p(i, j, 24) != 0.0:
            if p.p(i, j, 24) in (1.0, 3.0):  # om_retrieve.f:2655-2696, Koning-type
                elf = el - ef - vcshift
                if i == 1:
                    b = _bcoget(p, j, atar, eta)
                if i == 1 and b[1, 5] != 0.0:
                    vc = b[1, 1] * encoul2 * (
                        b[1, 2]
                        - 2.0 * b[1, 3] * elf
                        + 3.0 * b[1, 4] * elf**2
                        + b[i, 14] * b[i, 13] * math.exp(-b[i, 14] * elf)
                    )
                    vdcoul = b[i, 5] * vc
                nn = int(p.p(i, j, 13))
                ep = ef
                if i in (2, 4):
                    ep = p.p(i, j, 20)
                if ep == 0.0:
                    ep = ef
                elf = el - ep - vcshift
                iq = 1
                if i == 4 and b[4, 12] > 0.0:
                    iq = int(round(b[4, 12]))
                if i == 1:
                    ahf = b[1, 1] * b[1, 13] if b[1, 1] != 0.0 else b[1, 11]
                vlib[i] = (
                    b[i, 1]
                    * (
                        b[i, 15]
                        - b[i, 2] * elf
                        + b[i, 3] * elf**2
                        - b[i, 4] * elf**3
                        + b[i, 13] * math.exp(-b[i, 14] * elf)
                    )
                    + b[i, 5] * vc
                    + b[i, 6] * (elf**nn / (elf**nn + b[i, 7] ** nn))
                    + b[i, 8]
                    * math.exp(-b[i, 9] * elf**iq)
                    * (elf**nn / (elf**nn + b[i, 10] ** nn))
                    + b[i, 11] * math.exp(-b[i, 12] * elf)
                )
            elif p.p(i, j, 24) == 2.0:  # om_retrieve.f:2698-2745, Morillon-Romain
                elf = el - ef - vcshift
                if i == 1:
                    b = _bcoget(p, j, atar, eta)
                eee = el - vcshift
                iq = 1
                if i == 4 and b[4, 12] > 0.0:
                    iq = int(round(b[4, 12]))
                vnonl = 0.0
                if i in (1, 5):
                    amu, _ = _xkine(eee, kin.tarmas, kin.projmas, p.irel)
                    vnonl = -_vhf(eee, b[i, 1], b[i, 2], b[i, 3], amu)
                    vc = 0.0
                    if i == 1 and b[1, 5] != 0.0:
                        vc = encoul2
                        vdcoul = b[i, 5] * vc
                nn = int(p.p(i, j, 13))
                vlib[i] = (
                    vnonl
                    + b[i, 5] * vc
                    + b[i, 6] * (elf**nn / (elf**nn + b[i, 7] ** nn))
                    + b[i, 8]
                    * math.exp(-b[i, 9] * elf**iq)
                    * (elf**nn / (elf**nn + b[i, 10] ** nn))
                    + b[i, 11] * math.exp(-b[i, 12] * elf)
                )
            else:
                raise RIPLNotPorted(f"pot(i,j,24) = {p.p(i, j, 24)} is not a known OMP family")
            ea = p.p(i, j, 21)  # om_retrieve.f:2750-2763
            if ea == 0.0:
                ea = 1000.1
            if i == 2 and ea < 1000.0:
                alphav = p.p(i, j, 22)
                if alphav == 0.0:
                    alphav = 1.65
                if el > (ef + ea):
                    vlib[i] = vlib[i] + alphav * (
                        math.sqrt(el) + (ef + ea) ** 1.5 / (2.0 * el) - 1.5 * math.sqrt(ef + ea)
                    )
        elif p.p(i, j, 23) != 0.0:  # om_retrieve.f:2769-2782, Varner
            elf = el - vcshift
            vlib[i] = (p.p(i, j, 1) + p.p(i, j, 2) * eta) / (
                1.0
                + math.exp((p.p(i, j, 3) - elf + p.p(i, j, 4) * encoul2) / p.p(i, j, 5))
            )
            if p.p(i, j, 6) != 0.0:
                vlib[i] = vlib[i] + p.p(i, j, 6) * math.exp(
                    (p.p(i, j, 7) * elf - p.p(i, j, 8)) / p.p(i, j, 6)
                )
        elif p.p(i, j, 22) != 0.0:  # om_retrieve.f:2784-2796, Smith
            elf = el - vcshift
            vlib[i] = (
                p.p(i, j, 1)
                + p.p(i, j, 2) * eta
                + p.p(i, j, 6) * math.exp(p.p(i, j, 7) * elf + p.p(i, j, 8) * elf * elf)
                + p.p(i, j, 9) * elf * math.exp(p.p(i, j, 10) * elf ** p.p(i, j, 11))
            )
            if p.p(i, j, 5) != 0.0:
                vlib[i] = vlib[i] + p.p(i, j, 3) * math.cos(
                    2.0 * math.pi * (atar - p.p(i, j, 4)) / p.p(i, j, 5)
                )
        else:  # om_retrieve.f:2800-2809, standard
            elf = el - vcshift
            vlib[i] = (
                p.p(i, j, 1)
                + p.p(i, j, 7) * eta
                + p.p(i, j, 8) * encoul
                + p.p(i, j, 9) * atar
                + p.p(i, j, 10) * atar**_T1
                + p.p(i, j, 11) * atar ** -_T2
                + p.p(i, j, 12) * encoul2
            )
            if elf > 0.0:
                vlib[i] = (
                    vlib[i]
                    + (p.p(i, j, 2) + p.p(i, j, 13) * eta + p.p(i, j, 14) * atar) * elf
                    + p.p(i, j, 3) * elf**2
                    + p.p(i, j, 4) * elf**3
                    + p.p(i, j, 6) * math.sqrt(elf)
                    + p.p(i, j, 17) * encoul / elf**2
                    + (p.p(i, j, 5) + p.p(i, j, 15) * eta + p.p(i, j, 16) * elf) * math.log(elf)
                )
        if i == 1:
            vhfnum = vlib[1]
        if i == 2:
            alpha = alphav
        if i == 5:
            vsonum = vlib[5]
    dwv = dws = dwvso = 0.0
    dwvcor = dwscor = dsocor = 0.0
    if abs(p.idr) >= 2:  # om_retrieve.f:2816-2982
        if p.idr <= -2:
            raise RIPLNotPorted("numerical dispersive integral (idr <= -2) is not ported")
        vcshift = 0.0
        if p.izproj == 1 and p.p(1, 1, 25) > 0.0:
            vcshift = p.p(1, 1, 25) * ztar / atar ** (1.0 / 3.0)
        eee = el - vcshift
        if p.jrange[1] > 0 and p.p(2, 1, 24) != 0:
            aav = b[2, 6]
            bv = b[2, 7]
            n = int(round(p.p(2, 1, 13)))
            if n == 0 or n % 2 == 1:
                raise ValueError("Zero or odd exponent in Wv(E) for dispersive OMP")
            ep = p.p(2, 1, 20) or ef
            ea = p.p(2, 1, 21) or 1000.1
            dwv, derdwv = dom_int_wv(ef, ep, aav, bv, eee, n)
            if p.p(1, 1, 25) != 0:
                derdwv = 0.0
            derdwv = -b[1, 5] * encoul2 * derdwv
            t12der = 0.0
            if ea < 1000.0:
                alphav = p.p(2, 1, 22) or 1.65
                dwplus = alphav * dom_int_t2(ef, ea, eee)
                dtmp1 = _wvf(aav, bv, ep, ef, ef + ea, n)
                dwmin = dtmp1 * dom_int_t1(ef, ea, eee)
                dwv = dwv + dwplus + dwmin
                if b[1, 5] != 0.0 and p.p(1, 1, 25) == 0:
                    h = 0.05 if eee != 0.05 else 0.1
                    fac = 10.0 if eee != 0.05 else 5.0
                    d2 = dom_int_t2(ef, ea, eee + h) - dom_int_t2(ef, ea, eee - h)
                    d1 = dom_int_t1(ef, ea, eee + h) - dom_int_t1(ef, ea, eee - h)
                    t2der = alphav * d2 * fac
                    t1der = dtmp1 * d1 * fac
                    t12der = -b[1, 5] * encoul2 * (t1der + t2der)
            vvcoul = derdwv + t12der
        if p.jrange[3] > 0 and p.p(4, 1, 24) != 0:
            a_s = b[4, 8]
            bs = b[4, 10]
            cs = b[4, 9]
            m = int(round(p.p(4, 1, 13)))
            if m == 0 or m % 2 == 1:
                raise ValueError("Zero or odd exponent in Wd(E) for dispersive OMP")
            ep = p.p(4, 1, 20) or ef
            if p.idr >= 2:
                dws, derdws = dom_int_ws(ef, ep, a_s, bs, cs, eee, m)
                if p.p(1, 1, 25) != 0:
                    derdws = 0.0
                vscoul = -b[1, 5] * encoul2 * derdws
        if p.jrange[5] > 0 and p.p(6, 1, 24) != 0 and abs(p.idr) == 3:
            dwvso, _ = dom_int_wv(ef, ef, b[6, 6], b[6, 7], eee, int(round(p.p(6, 1, 13))))
        if p.idr != 0:
            dwvcor = dwv + vvcoul
            dwscor = dws + vscoul
            dsocor = dwvso
        iaref = 0
        if round(p.p(1, 1, 24)) == 1 and p.p(1, 1, 23) > 0.0:
            iaref = int(round(p.p(1, 1, 23)))
        optv[1] = vlib[1] + (p.p(1, 1, 22) * (atar - iaref) if iaref > 0 else 0.0) + dwvcor
        vlib[1] = vlib[1] + dwvcor
        optv[2] = vlib[2]
        optv[4] = vlib[4]
        vlib[3] = dwscor
        alib[3] = alib[4]
        rlib[3] = rlib[4]
        optv[3] = dwscor
        opta[3] = opta[4]
        optr[3] = optr[4]
        vlib[5] = vlib[5] + dsocor
        optv[5] = vlib[5]
        optv[6] = vlib[6]
    gamma = 1.0  # om_retrieve.f:3027-3041
    if p.irel == 2:
        emtar = kin.tarmas * AMU0C2
        emtot = (kin.tarmas + kin.projmas) * AMU0C2
        tcm = math.sqrt(2 * emtar * el + emtot**2) - emtot
        gamma = 1.0 + tcm / (tcm + 2 * kin.projmas * AMU0C2)
    v, rv, av = vlib[1] * gamma, rlib[1], alib[1]
    optv[1] *= gamma
    w, rw, aw = vlib[2] * gamma, rlib[2], alib[2]
    optv[2] *= gamma
    if w < 0.0 and nonegw == 1:
        optv[2] = 0.0
        w = 0.0
    vd, rvd, avd = vlib[3] * gamma, rlib[3], alib[3]
    optv[3] *= gamma
    wd, rwd, awd = vlib[4] * gamma, rlib[4], alib[4]
    optv[4] *= gamma
    if w < 0.0 and nonegw == 1:  # om_retrieve.f:3064 really tests w, not wd
        optv[4] = 0.0
    if wd < 0.0 and nonegw == 1:
        wd = 0.0
    vso, rvso, avso = vlib[5] * gamma, rlib[5], alib[5]
    optv[5] *= gamma
    wso, rwso, awso = vlib[6] * gamma, rlib[6], alib[6]
    optv[6] *= gamma
    # om_retrieve.f:3193-3231: the OPT* set is printed when the three dispersive amplitudes are
    # all non-zero, the plain one otherwise.
    if a_s != 0.0 and ahf != 0.0 and aav != 0.0:
        cols = [optv[1], optr[1], opta[1], dwvcor]
        for i in (2, 3, 4, 5, 6):
            cols += [optv[i], optr[i], opta[i]]
    else:
        cols = [v, rv, av, dwvcor, w, rw, aw, vd, rvd, avd, wd, rwd, awd,
                vso, rvso, avso, wso, rwso, awso]  # fmt: skip
    names = ("V", "rv", "av", "DWV", "W", "rw", "aw", "Vd", "rvd", "avd", "Wd", "rwd", "awd",
             "Vso", "rvso", "avso", "Wso", "rwso", "awso")  # fmt: skip
    out = dict(zip(names, cols, strict=True))
    out["Ef"] = ef
    out["rc"] = rc
    out["ac"] = ac
    # the common-block outputs `ecisip` reads for a modtyp >= 5 deck, and the last column of
    # omp-table.dat (om_retrieve.f:3219 prints VHFnum, the Hartree-Fock part of V before DWVcor)
    out["VHF"] = vhfnum
    out["VSO"] = vsonum
    out["VDcoul"] = vdcoul
    out["alpha"] = alpha
    return out


# ------------------------------------------------------------------------------ the table
def _f(x: float, w: int, d: int) -> float:
    """A value as Fortran prints it with `fw.d` and reads it back: round-half-away-from-zero to
    `d` decimals (om_retrieve.f:3206-3212). Overflow to `***` would make TALYS unreadable, so an
    out-of-field value raises rather than silently differing."""
    q = math.floor(abs(x) * 10**d + 0.5) / 10**d
    out = -q if x < 0 else q
    if len(f"{out:{w}.{d}f}") > w:
        raise ValueError(f"{x} overflows f{w}.{d} in omp-table.dat")
    return out


TABLE_COLUMNS = (
    "V", "rv", "av", "W", "rw", "aw", "Vd", "rvd", "avd",
    "Wd", "rwd", "awd", "Vso", "rvso", "avso", "Wso", "rwso", "awso",
)  # fmt: skip
TABLE_WIDTHS = (
    (8, 3), (7, 4), (7, 4),                  # V rv av
    (8, 4), (7, 4), (7, 4),                  # W rw aw
    (8, 4), (7, 4), (7, 4),                  # Vd rvd avd
    (8, 4), (7, 4), (7, 4),                  # Wd rwd awd
    (8, 4), (7, 4), (7, 4),                  # Vso rvso avso
    (8, 4), (7, 4), (7, 4),                  # Wso rwso awso
)  # fmt: skip


def ripl_energies(enincmax_mev: float) -> tuple[np.ndarray, np.ndarray]:
    """The incident grid TALYS sends to the retrieval. Returns (el, printed): `el` is `Eripl`
    accumulated in single precision exactly as TALYS does and promoted to double, which is the
    energy `optmod` is evaluated at; `printed` is its `f7.3` print, which is what TALYS reads
    back into `eomp` and interpolates on.

    TALYS: omppar.f90:296-315 (grid), om_retrieve.f:3206 (the f7.3 of the first column)
    Test: A-omppar
    """
    f4 = np.float32
    er = f4(0.0)
    deripl = f4(0.001)
    emax = f4(enincmax_mev) + f4(12.0)
    out: list[float] = []
    while True:
        er = f4(er + deripl)
        eeps = f4(er + f4(1.0e-4))
        if er > emax or len(out) == 260:  # numen, A0_talys_mod.f90:59
            break
        out.append(float(er))
        if eeps > f4(0.01):
            deripl = f4(0.01)
        if eeps > f4(0.1):
            deripl = f4(0.1)
        if eeps > f4(4.0):
            deripl = f4(0.2)
        if eeps > f4(10.0):
            deripl = f4(0.5)
        if eeps > f4(30.0):
            deripl = f4(1.0)
        if eeps > f4(100.0):
            deripl = f4(2.0)
    el = np.array(out, dtype=float)
    return el, np.array([_f(x, 7, 3) for x in out], dtype=float)


@cache
def _full_table(
    Z: int, A: int, iref: int, structure_dir: str
) -> tuple[np.ndarray, np.ndarray, np.ndarray, float]:
    """The retrieval evaluated on the longest grid `omppar` can ask for (the `numen` cap). The
    grid schedule does not depend on `enincmax`, so every shorter grid is a prefix of this one and
    `omp_table` just slices it."""
    p = read_om_parameter(iref, structure_dir)
    if p.imodel == 3:
        raise RIPLNotPorted("soft-rotator potentials (imodel 3) need OPTMAN")
    kin = _kinematics(p, Z, A, structure_dir)
    el_raw, e = ripl_energies(math.inf)
    vals = np.zeros((len(e), 19))
    ef = kin.efermi
    for n, el in enumerate(el_raw):
        row = optmod(p, kin, float(el))
        ef = row["Ef"]
        raw = [row[c] for c in TABLE_COLUMNS]
        vals[n, :18] = [_f(x, w, d) for x, (w, d) in zip(raw, TABLE_WIDTHS, strict=True)]
    return el_raw, e, vals, _f(ef, 7, 3)


def omp_table(
    Z: int,
    A: int,
    iref: int,
    enincmax_mev: float,
    *,
    structure: Path | None = None,
    check_range: bool = True,
) -> tuple[np.ndarray, np.ndarray, float]:
    """`omp-table.dat` for RIPL potential `iref` on target (Z, A): the energies TALYS reads back,
    the 19 `vomp` columns per energy and the Fermi energy from the table header.

    Column 19 (rc) is zero: `om_retrieve` prints no Coulomb radius, so `vomp(...,19)` stays at
    its initialised value, as it does in TALYS (omppar.f90:379-384 reads 18 numbers).

    TALYS: omppar.f90:271-376
    Test: A-omppar
    """
    sdir = str(_ripl_dir(structure))
    p = read_om_parameter(iref, sdir)
    if check_range:  # omppar.f90:322-343
        idx = read_om_index(sdir)
        if iref not in idx:
            raise KeyError(f"RIPL OMP {iref} not in om-index.txt")
        part, zbeg, zend, abeg, aend, _eb, _ef = idx[iref]
        want = _PARSYM.get((p.izproj, p.iaproj))
        if not (part == want and zbeg <= Z <= zend and abeg <= A <= aend):
            raise ValueError(f"RIPL OMP {iref} for {A} Z={Z} out of range (flagriplrisk stops)")
    _raw, e_full, vals_full, ef = _full_table(Z, A, iref, sdir)
    n = len(ripl_energies(enincmax_mev)[1])
    return e_full[:n].copy(), vals_full[:n].copy(), ef
