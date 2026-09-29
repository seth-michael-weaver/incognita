"""Physical constants and particle properties exactly as TALYS sets them (constants.f90), the
structure-database location TALYS resolves (machine.f90), and the default set of competing
outgoing particles (particles.f90).

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

Task: T1 (physics/hf/CONTRACT.md §7). Acceptance test: A-grid (§6).

TALYS routines ported here (file:line of the subroutine/function statement):
    constants.f90:1 (constants)
    machine.f90:1 (machine)
    particles.f90:1 (particles)

Precision, and why there are two sets of values
-----------------------------------------------
TALYS is built without ``-fdefault-real-8`` (source/Makefile: ``-w -O3 -ffp-contract=off``), so
every literal in constants.f90 such as ``amu = 931.49410242`` is a *single-precision* literal.
That holds even where the variable is declared ``real(dbl)`` (amu, parmass, excmass in
A0_talys_mod.f90:123-140): the value is rounded to float32 first and only then widened, so the
``amu`` TALYS computes with is 931.4940795898438, not 931.49410242. The derived constants (hbarc,
pi2h2c2, ...) are evaluated in single precision, left to right, as written.

``talys_constants()`` (default ``precision="talys"``) returns exactly those in-memory values, as
float64 numbers, so a port that uses them reproduces TALYS's arithmetic inputs bit for bit.
``precision="exact"`` returns the float64 value of every literal and float64 derived constants:
what the constants would be in the double-precision TALYS build of T14. Differences between the
two are ~1e-7 relative and sit inside every §6 tolerance, but a disagreement at that level
should be checked against this switch before it is called a port bug.
"""

from __future__ import annotations

import math
import os
from functools import lru_cache
from pathlib import Path

import numpy as np

# --- particle indices (constants.f90:78-86) -----------------------------------------------------
# fission = -1, photon = 0, neutron = 1, proton = 2, deuteron = 3, triton = 4, helium-3 = 5,
# alpha = 6
PARTICLE_INDEX = {"f": -1, "g": 0, "n": 1, "p": 2, "d": 3, "t": 4, "h": 5, "a": 6}
PARNAME = ("gamma", "neutron", "proton", "deuteron", "triton", "helium-3", "alpha")  # 0..6
PARSYM = ("g", "n", "p", "d", "t", "h", "a")  # 0..6
PARZ = (0, 0, 1, 1, 1, 2, 2)
PARN = (0, 1, 0, 1, 2, 1, 2)
PARA = (0, 1, 1, 2, 3, 3, 4)

# the literals as written in constants.f90:88-91 (single-precision literals in the TALYS build)
_PARMASS_LIT = (
    0.0,
    1.00866491574,
    1.00782495281,
    2.01410195518,
    3.01604916211,
    3.01602879487,
    4.00260293529,
)
_EXCMASS_LIT = (
    0.0,
    8.66491574e-3,
    7.82495281e-3,
    1.410195518e-2,
    1.604916211e-2,
    1.602879487e-2,
    2.60293529e-3,
)
_PARSPIN_LIT = (0.0, 0.5, 0.5, 1.0, 0.5, 0.5, 0.0)

# constants.f90:95-104
NUC = (
    "H",
    "He",
    "Li",
    "Be",
    "B",
    "C",
    "N",
    "O",
    "F",
    "Ne",
    "Na",
    "Mg",
    "Al",
    "Si",
    "P",
    "S",
    "Cl",
    "Ar",
    "K",
    "Ca",
    "Sc",
    "Ti",
    "V",
    "Cr",
    "Mn",
    "Fe",
    "Co",
    "Ni",
    "Cu",
    "Zn",
    "Ga",
    "Ge",
    "As",
    "Se",
    "Br",
    "Kr",
    "Rb",
    "Sr",
    "Y",
    "Zr",
    "Nb",
    "Mo",
    "Tc",
    "Ru",
    "Rh",
    "Pd",
    "Ag",
    "Cd",
    "In",
    "Sn",
    "Sb",
    "Te",
    "I",
    "Xe",
    "Cs",
    "Ba",
    "La",
    "Ce",
    "Pr",
    "Nd",
    "Pm",
    "Sm",
    "Eu",
    "Gd",
    "Tb",
    "Dy",
    "Ho",
    "Er",
    "Tm",
    "Yb",
    "Lu",
    "Hf",
    "Ta",
    "W",
    "Re",
    "Os",
    "Ir",
    "Pt",
    "Au",
    "Hg",
    "Tl",
    "Pb",
    "Bi",
    "Po",
    "At",
    "Rn",
    "Fr",
    "Ra",
    "Ac",
    "Th",
    "Pa",
    "U",
    "Np",
    "Pu",
    "Am",
    "Cm",
    "Bk",
    "Cf",
    "Es",
    "Fm",
    "Md",
    "No",
    "Lr",
    "Rf",
    "Db",
    "Sg",
    "Bh",
    "Hs",
    "Mt",
    "Ds",
    "Rg",
    "Cn",
    "Nh",
    "Fl",
    "Mc",
    "Lv",
    "Ts",
    "Og",
    "B9",
    "C0",
    "C1",
    "C2",
    "C3",
    "C4",
)  # nuc(Z) for Z = 1..124: NUC[Z - 1]
MAGIC = (2, 8, 20, 28, 50, 82, 126, 184)
ISOCHAR = (" ", "g", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v")
CPARITY = {-1: "-", 0: " ", 1: "+"}

# numl, A0_talys_mod.f90 line 28
NUML = 60

# fundamental constants, CODATA 2018 literals (constants.f90:114-122)
_FUNDAMENTAL_LIT = {
    "pi": 3.14159265358979323,
    "amu": 931.49410242,  # MeV
    "e2": 1.4399645,  # MeV fm
    "hbar": 6.582119569e-22,  # MeV s
    "clight": 2.99792458e8,  # m / s
    "kT": 0.08617333262,  # MeV for T9 = 1
    "emass": 0.510998950,  # MeV / c^2
    "avogadro": 6.02214076e23,
    "qelem": 1.602176634e-19,  # C
}

# default outgoing-particle symbols in `outtype` order 0..6 (particles.f90:62-66)
DEFAULT_OUTTYPE = PARSYM


def _f32(x: float) -> np.float32:
    return np.float32(x)


def talys_constants(precision: str = "talys") -> dict[str, object]:
    """SETB: `_talys_constants(precision)`, built once per worker (it is ~800 calls per nuclide);
    each caller gets its own shallow copy of the dict, whose values are immutable.

    TALYS: constants.f90:1 (constants)
    Test: A-grid
    """
    return dict(_talys_constants_memo(precision))


@lru_cache(maxsize=4)
def _talys_constants_memo(precision: str) -> dict[str, object]:
    return _talys_constants(precision)


def _talys_constants(precision: str = "talys") -> dict[str, object]:
    """Every constant TALYS defines in constants.f90, keyed by the Fortran variable name.

    Scalars are Python floats (float64). Particle arrays (parmass, excmass, parspin, spin2, parZ,
    parN, parA) are tuples indexed 0..6 = gamma..alpha, as in TALYS's ``dimension(0:numpar)``.
    Units follow constants.f90: amu, emass, e2*fm, hbarc in MeV (fm); hbar in MeV s; clight in
    m/s; parmass/excmass in amu; pi2h2c2 in mb^-1 MeV^-2; pi2h3c2 in mb^-1 MeV^-3 s^-1;
    amupi2h3c2 in mb^-1 MeV^-2 s^-1; amu4pi2h2c2 in mb^-1 MeV^-1.

    precision="talys": the values TALYS holds in memory (single-precision literals, derived
    constants in single-precision arithmetic, dbl-declared variables widened from float32).
    precision="exact": float64 literals and float64 arithmetic (the T14 double build).

    TALYS: constants.f90:1 (constants)
    Test: A-grid
    """
    if precision not in ("talys", "exact"):
        raise ValueError("precision must be 'talys' or 'exact'")
    talys = precision == "talys"
    lit = _f32 if talys else np.float64

    c = {k: lit(v) for k, v in _FUNDAMENTAL_LIT.items()}
    pi, amu, hbar, clight = c["pi"], c["amu"], c["hbar"], c["clight"]
    two = lit(2.0)

    # derived constants, evaluated in the declared kind, left to right (constants.f90:126-139)
    twopi = two * pi
    pi2 = pi * pi
    sqrttwopi = np.sqrt(two * pi)
    fourpi = lit(4.0) * pi
    deg2rad = pi / lit(180.0)
    rad2deg = lit(180.0) / pi
    onethird = lit(1.0) / lit(3.0)
    twothird = two * onethird
    twopihbar = twopi / hbar
    hbarc = hbar * clight * lit(1.0e15)
    pi2h2c2 = lit(0.1) / (pi2 * hbarc * hbarc)
    pi2h3c2 = pi2h2c2 / hbar
    # amu is real(dbl); `real(amu)` converts it back to the default (single) kind
    amu_sgl = _f32(amu) if talys else amu
    amupi2h3c2 = amu_sgl * pi2h3c2
    amu4pi2h2c2 = amu_sgl * lit(0.25) * pi2h2c2

    parspin = tuple(float(lit(s)) for s in _PARSPIN_LIT)
    # spin2 = int(2. * parspin); spin2(0) = spin2(6) = 1 (constants.f90:161-163)
    spin2 = [int(2.0 * s) for s in parspin]
    spin2[0] = 1
    spin2[6] = 1

    out: dict[str, object] = {k: float(v) for k, v in c.items()}
    out.update(
        twopi=float(twopi),
        pi2=float(pi2),
        sqrttwopi=float(sqrttwopi),
        fourpi=float(fourpi),
        deg2rad=float(deg2rad),
        rad2deg=float(rad2deg),
        onethird=float(onethird),
        twothird=float(twothird),
        twopihbar=float(twopihbar),
        hbarc=float(hbarc),
        pi2h2c2=float(pi2h2c2),
        pi2h3c2=float(pi2h3c2),
        amupi2h3c2=float(amupi2h3c2),
        amu4pi2h2c2=float(amu4pi2h2c2),
        # dbl-declared, but assigned from single-precision literals in the TALYS build
        parmass=tuple(float(lit(m)) for m in _PARMASS_LIT),
        excmass=tuple(float(lit(m)) for m in _EXCMASS_LIT),
        parspin=parspin,
        spin2=tuple(spin2),
        parZ=PARZ,
        parN=PARN,
        parA=PARA,
        pardis=0.5,  # constants.f90:153
        fislim=215,  # constants.f90:167
        Emaxtalys=1000.0,  # constants.f90:171, MeV
        numl=NUML,
    )
    return out


def sgn_table(numl: int = NUML) -> tuple[float, ...]:
    """TALYS's `sgn` array, index 0..2*numl: sgn(0) = 1, sgn(even) = 1, sgn(odd) = -1.

    TALYS: constants.f90:1 (constants)
    Test: A-cn2
    """
    return tuple(1.0 if i % 2 == 0 else -1.0 for i in range(2 * numl + 1))


def nuclide_symbol(Z: int) -> str:
    """Element symbol TALYS uses for charge number Z (1..124), `nuc(Z)` without padding.

    TALYS: constants.f90:1 (constants)
    Test: A-struct
    """
    if not 1 <= Z <= len(NUC):
        raise ValueError(f"Z = {Z} outside TALYS's nuc table (1..{len(NUC)})")
    return NUC[Z - 1]


def talys_structure_path(code_dir: str | os.PathLike | None = None) -> Path:
    """The structure-database directory TALYS reads: $TALYS_DIR/structure/, falling back to the
    compiled-in code_dir (machine.f90:50-66). Raises FileNotFoundError with TALYS's own check
    (structure/abundance/H.abun must exist, machine.f90:81-91).

    TALYS: machine.f90:1 (machine)
    Test: A-struct
    """
    if code_dir is None:
        code_dir = os.environ.get("TALYS_DIR") or str(Path.home() / "opt" / "talys-src")
    path = Path(code_dir) / "structure"
    if not (path / "abundance" / "H.abun").is_file():
        raise FileNotFoundError(
            f"TALYS structure database not found: expected {path / 'abundance' / 'H.abun'}; "
            "set TALYS_DIR"
        )
    return path


def particles(
    k0: int = 1,
    outtype: tuple[str, ...] | None = None,
    flagfission: bool = False,
    flagomponly: bool = False,
) -> dict[int, bool]:
    """Which outgoing particles TALYS includes as competing channels: {type: parinclude} for
    type = -1 (fission) .. 6 (alpha). `outtype` is the `outgoing` keyword's particle symbols
    (blank or None = the default, all of gamma..alpha); the incident particle `k0` is always
    included. `parskip` is the negation. The URR side effect (eurr = 0 when photons are
    skipped, particles.f90:98-101) belongs to input.defaults and is not reproduced here.

    TALYS: particles.f90:1 (particles)
    Test: A-grid
    """
    parinclude = {t: True for t in range(-1, 7)}
    if not flagfission:
        parinclude[-1] = False
    if flagomponly:
        parinclude = {t: False for t in range(-1, 7)}
    requested = [s for s in (outtype or ()) if s and s != " "]
    if requested:
        for t in range(0, 7):
            parinclude[t] = False
        for t in range(0, 7):
            if PARSYM[t] in requested:
                parinclude[t] = True
    parinclude[k0] = True
    return parinclude


def machine_limits() -> dict[str, float]:
    """The IEEE limits TALYS's arithmetic lives in (single precision by default): float32 tiny,
    max and epsilon, and the float64 ones the port computes in. Used by tests that decide
    whether a disagreement is below TALYS's own resolution.

    TALYS: machine.f90:1 (machine)
    Test: A-grid
    """
    f32, f64 = np.finfo(np.float32), np.finfo(np.float64)
    return {
        "sgl_eps": float(f32.eps),
        "sgl_tiny": float(f32.tiny),
        "sgl_max": float(f32.max),
        "dbl_eps": float(f64.eps),
        "dbl_tiny": float(f64.tiny),
        "dbl_max": float(f64.max),
        "ln_sgl_max": math.log(float(f32.max)),
    }
