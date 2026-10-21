"""Giant-resonance and photon-strength parameters per multipolarity and nucleus (GDR tables,
systematics, SMLO-2019 table loading).

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

Task: T7 (physics/hf/CONTRACT.md §7). Acceptance test: A-psf (§6).

TALYS routines ported here (file:line of the subroutine/function statement):
    gammapar.f90:1 (gammapar)
    input_gammapar.f90:1 (input_gammapar) -- the gamma defaults block only (upbend, wtable)
    input_gammamodel.f90:1 (input_gammamodel) -- flagupbend / flagpsfglobal / gammax defaults

Array layout. TALYS indexes egr(Zix, Nix, irad, l, igr) with irad 0 = magnetic, 1 = electric,
l = 1..gammax and igr = 1..2. Here every per-(irad, l, igr) tensor has shape (2, gammax + 1, 3)
so the Fortran indices are used unchanged (index 0 along l and igr is unused and zero).

What is injected rather than computed here (contract §5 injection rule):
    S_k0_mev, delta_mev, alev_per_mev  -- separation energy of the projectile, pairing energy
                                          and level density parameter: T6/T2 (densitypar.f90)
    beta2                              -- ground-state deformation: T2 (masses.f90:163)
    ldmodel, flagcol                   -- select the global wtable default (input_gammapar.f90:115)

Supported models: strength 1, 2, 5 (Lorentzians) and every tabulated E1 model read by
gammapar.f90 except 11 with J-pi resolution; strengthM1 1-4 and tables 8, 10, 12. `Exlfile`
(user tables) and strength/strengthM1 11 are not ported and raise.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field, replace
from functools import cache
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np
import torch
from torch import Tensor

from physics.hf import eadj as _eadj
from physics.hf.core.constants import default_talys_root, nuclide_symbol, talys_constants, talys_structure_path
from physics.hf.core.tensors import DTYPE
from physics.hf.gamma import actphys, ftglobal, ggnorm, scissors

if TYPE_CHECKING:
    from physics.hf.input.defaults import Options

# constants.f90 values as TALYS holds them (single-precision literals, core.constants "talys" mode)
_C = talys_constants()
_PI = float(_C["pi"])
ONETHIRD = float(_C["onethird"])
PI2H2C2 = float(_C["pi2h2c2"])  # constants.f90:139, mb^-1 MeV^-2
NUMGAMQRPA = 300  # A0_talys_mod.f90:50
NUMTQRPA = 31  # A0_talys_mod.f90:51
NUMZPH, NUMNPH = 4, 8  # A0_talys_mod.f90:34-35

_TABLE_DIRS_E1 = {  # gammapar.f90:147-176
    3: "hfbcs",
    4: "hfb",
    6: "hfbt",
    7: "rmf",
    8: "gogny",
    10: "bsk27_E1",
    12: "shellmodel-e1",
    13: "rqfamz",
}
_TABLE_DIRS_M1 = {8: "gognyM1", 10: "bsk27_M1", 12: "shellmodel-m1"}  # gammapar.f90:366-377

# input_gammapar.f90:115-137: global E1 wtable for (strength, ldmodel, flagcol)
#: UQ1 (Total Monte Carlo). None, or a callable `(Z, A) -> {"ftable", "wtable", "sgr_m1": factor}`
#: (or None) for the nucleus whose photon strength is being built: E1 ftable(1, 1), E1
#: wtable(1, 1) and M1 sgr(0, 1, 1), multiplied after TALYS's defaults resolve and before a
#: user override would replace them. The same three entries as `capture_gpu`'s theta.
TMC_GAMMA = None

_WTABLE_GLOBAL = {
    8: {
        (1, True): 1.052,
        (1, False): 1.076,
        (2, True): 0.942,
        (2, False): 0.943,
        (3, True): 0.905,
        (3, False): 0.911,
        4: 0.918,
        5: 1.017,
        6: 0.942,
    },
    9: {
        (1, True): 1.048,
        (1, False): 1.081,
        (2, True): 0.911,
        (2, False): 0.934,
        (3, True): 0.884,
        (3, False): 0.919,
        4: 0.921,
        5: 1.021,
        6: 0.936,
    },
}


def structure_dir() -> Path:
    """TALYS structure database (contract §4.5), via core.constants.talys_structure_path; a
    path that does not exist is returned rather than raised so callers can skip.

    TALYS: machine.f90:1 (machine)
    Test: A-psf
    """
    try:
        return talys_structure_path()
    except FileNotFoundError:
        root = os.environ.get("TALYS_DIR") or default_talys_root()
        return Path(root) / "structure"


@dataclass(frozen=True)
class PSFTable:
    """One tabulated strength function, TALYS qrpa(Zix,Nix)%e(0:300, irad, l) and
    %f(0:300, nTqrpa, irad, l). Index 0 is TALYS's zero entry (e = 0, f = 0).

    `f_raw_mev3` is onethird*pi2h2c2*f_table WITHOUT ftable (gammapar.f90:218); `e_raw_mev` is the
    tabulated energy WITHOUT etable and before the wtable stretch (gammapar.f90:216, 575-585).
    Both are applied when the table is evaluated (`table_arrays`) so ftable, etable and wtable
    stay differentiable.
    """

    e_raw_mev: Tensor  # (301,)
    f_raw_mev3: Tensor  # (301, nT)


#: LEESHELL: magic numbers of the valence rule (jj closures; arm b adds Z/N = 20)
LEESHELL_N = (28, 50, 82, 126)
LEESHELL_B = (20, 28, 50, 82, 126)


def leeshell_mode(options) -> int:
    """LEESHELL: keyword `leeshell n|nm|b`, else env INCOGNITA_LEESHELL; n / unset = 0 = OFF = TALYS.
    1 (nm): no M1 upbend in a decaying nucleus with N in LEESHELL_N; 2 (b): N or Z in LEESHELL_B.

    TALYS: (none -- Incognita extension, not a TALYS routine)
    Test: none in the public suite
    """
    v = str(getattr(options, "leeshell", "n") or "n").strip().lower()
    if v in ("", "n"):
        v = os.environ.get("INCOGNITA_LEESHELL", "n").strip().lower() or "n"
    if v in ("n", "0"):
        return 0
    if v in ("nm", "1"):
        return 1
    if v in ("b", "2"):
        return 2
    raise ValueError(f"leeshell: expected n, nm or b, got {v!r}")


def m1share_mode(options) -> int:
    """M1SHARE: keyword `m1share n|s|t`, else env INCOGNITA_M1SHARE; n / unset = 0 = OFF = TALYS.
    1 (s): spin-flip part of the tabulated M1 replaced by an independent SLO (m1share_slo), E1 table x the
    nucleus's `m1kappa` cell; 2 (t): as s, but kappa acts on the E1 table only below E_GDR - Gamma_GDR,
    linear blend to 1 at E_GDR, 1 above. 3 (p, E1M1NR): non-rotors only (|beta2| < E1M1NR_BETA): the M1 table as s,
    and the same strength taken off the E1 table at every photon energy, so f_E1 + f_M1 is held pointwise
    (e1m1nr_transfer); no kappa. Rotors are OFF. 4 (r, M1ROT): rotors only (|beta2| >= E1M1NR_BETA): as p, but the
    spin-flip SLO is split by deformation into K = 0 / K = 1 components (m1rot_slo); non-rotors OFF. 5 (b): p on
    non-rotors + r on rotors (= M1ROT arm RB, r stacked on E1M1NR's B68).

    TALYS: (none -- Incognita extension, not a TALYS routine)
    Test: none in the public suite
    """
    v = str(getattr(options, "m1share", "n") or "n").strip().lower()[:1]
    if v in ("", "n"):
        v = os.environ.get("INCOGNITA_M1SHARE", "n").strip().lower()[:1] or "n"
    if v in ("n", "0"):
        return 0
    if v in ("s", "1"):
        return 1
    if v in ("t", "2"):
        return 2
    if v in ("p", "3"):
        return 3
    if v in ("r", "4"):
        return 4
    if v in ("b", "5"):
        return 5
    raise ValueError(f"m1share: expected n, s, t, p, r or b, got {v!r}")


#: M1SHARE: (16 pi / 9) (hbar c)^-3 in MeV^-3 per (mu_N^2 / MeV): f_M1 = M1_CONV * dB(M1)up/dE
M1_CONV = 11.5473e-9
#: M1SHARE: spin-flip Sum B(M1)up = M1SF_C * A mu_N^2 (geometric mean of B/A over Ca-48, Zr-90, Sn (112-124 mean),
#: Pb-208 measured (p,p') 0 deg / (e,e') totals; development notes s2), SLO centroid 41 A^-1/3 MeV, width 4 MeV
M1SF_C = 0.0854
M1SF_G = 4.0
M1SF_SPLIT_W = 0.5


def m1share_slo(A: int, e: np.ndarray, e0: float | None = None) -> np.ndarray:
    """M1SHARE spin-flip SLO f(E) [MeV^-3], TALYS SLO shape (fstrength.f90:148-156, l = 1) with integral
    over 0..inf equal to M1_CONV * M1SF_C * A. Centroid e0 (default 41 A^-1/3 MeV).

    TALYS: (none -- Incognita extension, not a TALYS routine)
    Test: none in the public suite
    """
    e0, g = (41.0 * A ** (-1.0 / 3.0) if e0 is None else float(e0)), M1SF_G
    shape = lambda x: x * g**2 / ((x**2 - e0**2) ** 2 + x**2 * g**2)  # noqa: E731
    grid = np.linspace(0.0, 80.0, 160001)
    norm = M1_CONV * M1SF_C * A / np.trapezoid(shape(grid), grid)
    return norm * shape(np.asarray(e, float))


#: M1ROT: quadrupole radius coefficient sqrt(5 / 4 pi): R(theta) = R0 (1 + beta2 Y20), so R_par = R0 (1 + a beta2),
#: R_perp = R0 (1 - a beta2 / 2) (Bohr-Mottelson; the Danos-Okamoto axis split used for the deformed GDR)
M1ROT_A = float(np.sqrt(5.0 / (4.0 * np.pi)))


def m1rot_energies(A: int, beta2: float) -> tuple[float, float]:
    """M1ROT: K = 0 / K = 1 spin-flip centroids of a deformed nucleus. The published centroid 41 A^-1/3 MeV scales as
    1 / R (spin-orbit splitting ~ A^-1/3), applied per axis: E_K0 = E0 / (1 + a b2), E_K1 = E0 / (1 - a b2 / 2);
    splitting E_K1 - E_K0 ~ (3/2) a b2 E0 to first order (prolate: K = 0 lower). No fitted number.

    TALYS: (none -- Incognita extension, not a TALYS routine)
    Test: none in the public suite
    """
    e0, a = 41.0 * A ** (-1.0 / 3.0), M1ROT_A * float(beta2)
    return e0 / (1.0 + a), e0 / (1.0 - 0.5 * a)


def m1rot_slo(A: int, beta2: float, e: np.ndarray) -> np.ndarray:
    """M1ROT spin-flip f(E) [MeV^-3] of a rotor: two m1share_slo components at m1rot_energies, weights 1/3 (K = 0, one
    axis) and 2/3 (K = 1, two axes), each with width M1SF_G; total integral M1_CONV * M1SF_C * A as m1share_slo.

    TALYS: (none -- Incognita extension, not a TALYS routine)
    Test: none in the public suite
    """
    ek0, ek1 = m1rot_energies(A, beta2)
    return m1share_slo(A, e, ek0) / 3.0 + 2.0 * m1share_slo(A, e, ek1) / 3.0


def m1share_split(A: int, e: np.ndarray) -> np.ndarray:
    """M1SHARE: weight of the tabulated M1 kept (scissors / low-energy part): logistic step at
    E_c = 41 A^-1/3 - Gamma/2, width M1SF_SPLIT_W MeV; the part above is the table's spin-flip, replaced.

    TALYS: (none -- Incognita extension, not a TALYS routine)
    Test: none in the public suite
    """
    ec = 41.0 * A ** (-1.0 / 3.0) - M1SF_G / 2.0
    return 1.0 / (1.0 + np.exp((np.asarray(e, float) - ec) / M1SF_SPLIT_W))


#: E1M1NR: `m1share p` acts only on non-rotors, |beta2| < E1M1NR_BETA (E1TAIL's rotor class, |b2| >= 0.2)
E1M1NR_BETA = 0.2
#: E1M1NR: the E1 table never falls below this fraction of its own value (count recorded in e1m1nr_clip)
E1M1NR_FLOOR = 0.05


def _qrpa_guard(f_tab: np.ndarray) -> np.ndarray:
    """gammapar.f90:240-243 / 402-405 last-point guard on a raw table (copy)."""
    f = f_tab.copy()
    for it in range(f.shape[1]):
        if f[NUMGAMQRPA, it] > f[NUMGAMQRPA - 1, it]:
            f[NUMGAMQRPA, it] = f[NUMGAMQRPA - 1, it] * 0.9
    return f


def e1m1nr_transfer(gp: "GammaParameters", m1_off: "PSFTable") -> "GammaParameters":
    """E1M1NR (`m1share p`): gp's M1 table already carries the m1share-s substitution; `m1_off` is the unmodified
    M1 table. The M1 change dM1(E) = f_M1(on) - f_M1(off), both as TALYS evaluates them (etable/ftable/wtable,
    table_arrays), is interpolated (linear in E, 0 outside the M1 grid) to the E1 table's evaluated energies and
    taken off the E1 table there (divided by the E1 ftable, so the evaluated f_E1 falls by exactly dM1), per
    temperature column (M1 column min(c, last)). E1 floor E1M1NR_FLOOR x its own value. Upbend, E2, M2 untouched.

    TALYS: (none -- Incognita extension, not a TALYS routine)
    Test: none in the public suite
    """
    e_m, f_on = table_arrays(gp, 0, 1)
    _, f_off = table_arrays(replace(gp, tables={**gp.tables, (0, 1): m1_off}), 0, 1)
    e_m = e_m.detach().cpu().numpy()
    d = (f_on - f_off).detach().cpu().numpy()
    e_e, _ = table_arrays(gp, 1, 1)
    e_e = e_e.detach().cpu().numpy()
    tab = gp.tables[(1, 1)]
    fr = tab.f_raw_mev3.detach().cpu().numpy().copy()
    ft = float(gp.ftable[1, 1])
    clip = 0
    for c in range(fr.shape[1]):
        dc = np.interp(e_e[1:], e_m[1:], d[1:, min(c, d.shape[1] - 1)], left=0.0, right=0.0)
        new = fr[1:, c] - dc / ft
        low = new < E1M1NR_FLOOR * fr[1:, c]
        clip += int(low.sum())
        fr[1:, c] = np.where(low, E1M1NR_FLOOR * fr[1:, c], new)
    tables = {**gp.tables, (1, 1): PSFTable(tab.e_raw_mev, _t(fr).to(tab.f_raw_mev3.dtype))}
    return replace(gp, tables=tables, e1m1nr_clip=clip)


def leeshell_closed(Z: int, A: int, mode: int) -> bool:
    """True when the LEESHELL valence rule switches the M1 upbend of nucleus (Z, A) off.

    TALYS: (none -- Incognita extension, not a TALYS routine)
    Test: none in the public suite
    """
    N = int(A) - int(Z)
    if mode == 1:
        return N in LEESHELL_N
    if mode == 2:
        return N in LEESHELL_B or int(Z) in LEESHELL_B
    return False


@dataclass(frozen=True)
class GammaParameters:
    """gammapar.f90 output for one nucleus (Zix, Nix), plus the injected scalars fstrength reads."""

    Z: int
    A: int
    zix: int
    nix: int
    strength: int
    strengthM1: int
    gammax: int
    flagupbend: bool
    flagpsfglobal: bool
    egr_mev: Tensor  # (2, gammax+1, 3)
    ggr_mev: Tensor
    sgr_mb: Tensor
    epr_mev: Tensor  # pygmy / scissors, (2, gammax+1, 3)
    gpr_mev: Tensor
    tpr_mb: Tensor
    ngr: tuple[tuple[int, ...], tuple[int, ...]]  # (irad, l) -> 1 or 2
    upbend: Tensor  # (2, gammax+1, 4): [.., 1] C, [.., 2] eta, [.., 3] F
    etable_mev: Tensor  # (2, gammax+1)
    ftable: Tensor
    wtable: Tensor
    tables: dict = field(default_factory=dict)  # (irad, l) -> PSFTable
    n_tqrpa: int = 1
    tqrpa_mev: Tensor | None = None  # (n_tqrpa,)
    S_k0_mev: Tensor | float = 0.0
    delta_mev: Tensor | float = 0.0
    alev_per_mev: Tensor | float = 0.0
    beta2: Tensor | float = 0.0
    gamgam_ev: float = 0.0  # experimental <Gamma_gamma>, physical eV (ResonanceData.gamgam_ev)
    m1share: int = 0  # M1SHARE (Incognita extension): 0 OFF = TALYS, 1 s, 2 t, 3 p, 4 rotor r (tables already substituted)
    m1kappa: float = 1.0  # M1SHARE: the nucleus's E1 factor (its `m1kappa Z A k` cell), record only
    e1m1nr_clip: int = -1  # E1M1NR (m1share p): E1 table points held at the floor; -1 = transfer not applied
    e1_imax: int = 0  # M1SHARE t: wtable stretch pivot index of the UNMODIFIED E1 table (0 = find it in the table, TALYS)
    eadj_e1: tuple = ()  # ENGADJ: energy-local f_E1(Egamma) bumps of this nucleus (physics/hf/eadj.py); () = OFF
    eadj_m1: tuple = ()  # ENGADJ: the same for f_M1

    def qrpaexist(self, irad: int, l: int) -> bool:  # noqa: E741
        return (irad, l) in self.tables


def _t(x) -> Tensor:
    return torch.as_tensor(x, dtype=DTYPE)


@cache
def _read_gdr(symbol: str) -> dict[int, tuple[float, ...]]:
    """gamma/gdr/<El>.gdr, format '(4x, i4, 6f8.2)' (gammapar.f90:99)."""
    p = structure_dir() / "gamma" / "gdr" / f"{symbol}.gdr"
    out: dict[int, tuple[float, ...]] = {}
    if not p.exists():
        return out
    for line in p.read_text().splitlines():
        if len(line) < 8:
            continue
        try:
            ia = int(line[4:8])
        except ValueError:
            continue
        vals = []
        for k in range(6):
            s = line[8 + 8 * k : 16 + 8 * k].strip()
            vals.append(float(s) if s else 0.0)  # Fortran PAD: blanks read as zero
        out.setdefault(ia, tuple(vals))  # first match wins (the read loop exits)
    return out


def _fortran_fields(line: str, width: int, start: int, n: int) -> list[float]:
    try:  # COREX: `float` skips the blanks around a number itself; a blank field falls through
        return [float(line[start + width * k : start + width * (k + 1)]) for k in range(n)]
    except ValueError:
        pass
    vals = []
    for k in range(n):
        s = line[start + width * k : start + width * (k + 1)].strip()
        vals.append(float(s) if s else 0.0)
    return vals


def _psf_block_fast(lines, i: int, n_t: int) -> tuple[np.ndarray, np.ndarray] | None:
    """NATIVEX2: `_read_psf_table`'s 300 records from line `i` in one numpy text parse, or None
    when the block is not the plain case (short file, a blank or glued field, fewer than `n_t`
    columns on a line), which the per-field read then handles. On the plain case every field is
    a whitespace-separated decimal, so both reads give the float nearest to it."""
    if i + NUMGAMQRPA > len(lines):
        return None
    block = lines[i : i + NUMGAMQRPA]
    width = 9 + 12 * n_t
    rows = [ln[:width] for ln in block]
    if any(len(r) != width for r in rows):
        return None
    try:
        vals = np.array(" ".join(rows).split(), dtype=np.float64)
    except ValueError:
        return None
    if vals.size != NUMGAMQRPA * (1 + n_t):
        return None
    vals = vals.reshape(NUMGAMQRPA, 1 + n_t)
    e = np.zeros(NUMGAMQRPA + 1)
    f = np.zeros((NUMGAMQRPA + 1, n_t))
    e[1:] = vals[:, 0]
    f[1:] = vals[:, 1:]
    return e, f


@cache
def _psf_lines(path: str) -> tuple[str, ...] | None:
    """The lines of one tabulated strength file, read once (MACSPEED: every nucleus of a run asks
    `_read_psf_table` for its own mass block of the same per-element file)."""
    p = Path(path)
    if not p.exists():
        return None
    from physics.hf.structure.files import lazy_lines  # COREX: lines sliced out on demand

    return lazy_lines(path, encoding="utf-8")


@cache
def _read_psf_table(
    path: str, A: int, n_t: int, nblock: int = 1
) -> tuple[np.ndarray, np.ndarray] | None:
    """Tabulated strength block for mass A, format '(10x, i4)' header, one skipped line, 300 lines
    '(f9.3, 40es12.3)', one skipped line (gammapar.f90:180-237). Returns raw (e, f_table[mb/MeV]).
    """
    lines = _psf_lines(path)
    if lines is None:
        return None
    i = 0
    while i < len(lines):
        try:
            ia = int(lines[i][10:14])
        except (ValueError, IndexError):
            return None  # read_error(..., eor/eof = 'continue') then exit
        i += 2  # header + the column-title line
        if ia == A:
            got = _psf_block_fast(lines, i, n_t)
            if got is not None:
                return got
            e = np.zeros(NUMGAMQRPA + 1)
            f = np.zeros((NUMGAMQRPA + 1, n_t))
            for nen in range(1, NUMGAMQRPA + 1):
                if i >= len(lines):
                    break
                ln = lines[i]
                i += 1
                try:
                    e[nen] = float(ln[0:9])
                    f[nen] = _fortran_fields(ln, 12, 9, n_t)
                except ValueError:
                    break
            return e, f
        i += nblock * (NUMGAMQRPA + 1)
    return None


def gamma_parameters(
    Z: int,
    A: int,
    options: Options,
    *,
    zix: int = 0,
    nix: int = 0,
    S_k0_mev: Tensor | float = 0.0,
    delta_mev: Tensor | float = 0.0,
    alev_per_mev: Tensor | float = 0.0,
    beta2: Tensor | float = 0.0,
    gamgam_ev: float = 0.0,
    projectile_k0: int = 1,
    flagcol: bool = False,
    gammax: int | None = None,
    overrides: dict | None = None,
) -> GammaParameters:
    """egr [MeV], ggr [MeV], sgr [mb], ftable/etable/wtable per E1/M1/E2 as gammapar.f90
    (cross-check: psf* header).

    `overrides` maps a field name (egr_mev, sgr_mb, ftable, wtable, upbend, ...) to a tensor of
    the same shape; non-zero entries replace the defaults the way a TALYS keyword does (the
    `== 0.` tests in gammapar.f90 only fill what the user left at zero). Pass requires_grad
    tensors here to differentiate.

    TALYS: gammapar.f90:1 (gammapar)
    Test: A-psf
    """
    strength = int(options.strength)
    strengthM1 = int(options.strengthM1)
    # TALYS indexes ldmodel per nucleus; input_densitymodel.f90:245-252 sets ldmodel(0,0) from
    # ldmodelCN and every other nucleus from ldmodelall. Only ldmodel(Zix,Nix) reaches the
    # wtable defaults at input_gammapar.f90:117-136, so read the one for THIS nucleus -- an
    # actinide resolves ldmodelall to 7 (input_densitymodel.f90:90) and a hard-wired 1 would
    # silently pick the wrong global wtable.
    ldmodel = int(options.ldmodelCN if (zix, nix) == (0, 0) else options.ldmodelall)
    flagupbend = bool(options.flagupbend)  # input_gammamodel.f90:64-68
    flagpsfglobal = bool(options.flagpsfglobal)  # input_gammamodel.f90:69
    gmax = int(gammax if gammax is not None else options.gammax)  # input_gammapar.f90:30
    if strength == 11 or strengthM1 == 11:
        raise NotImplementedError("T7: D1M-intra (strength/strengthM1 11) not ported")
    N = A - Z
    L1 = gmax + 1
    shp = (2, L1, 3)
    egr = np.zeros(shp)
    ggr = np.zeros(shp)
    sgr = np.zeros(shp)
    epr = np.zeros(shp)
    gpr = np.zeros(shp)
    tpr = np.zeros(shp)
    upb = np.zeros((2, L1, 4))
    etable = np.zeros((2, L1))
    ftable = np.ones((2, L1))
    # ACTPHYS (Z >= 88) and GAMMAALL (Z <= 82) factors, each 1 unless its switch is on; Z ranges are disjoint
    ftable[1, 1] = actphys.e1_factor(Z, A) * ggnorm.factor(Z, A)
    wtable = np.ones((2, L1))
    ov = dict(overrides or {})
    ov = ftglobal.apply(options, Z, A, ov)  # FTGLOBAL (default ON; `ftglobal n` = deck ftable lines verbatim)
    b2 = float(beta2.detach() if isinstance(beta2, Tensor) else beta2)
    # UQ1: multiplicative Total Monte Carlo factors for THIS nucleus (`TMC_GAMMA`), or None
    tmc = TMC_GAMMA(int(Z), int(A)) if TMC_GAMMA is not None else None

    # input_gammapar.f90:112-150 (neutron-induced defaults)
    if projectile_k0 <= 1 and options.flagglobalwtable and strength in _WTABLE_GLOBAL:  # flagglobalwtable = .true.
        tbl = _WTABLE_GLOBAL[strength]
        key = (ldmodel, bool(flagcol)) if ldmodel <= 3 else ldmodel
        if key in tbl:
            from physics.hf.gamma.e1_width import constant as _e1w_constant  # INDEP_FIX: INCOGNITA_E1_WTABLE
            wtable[1, 1] = _e1w_constant(strength, tbl[key])
    if strengthM1 in (8, 10):
        if A >= 105:  # `Ainit`: the initial compound nucleus (TODO(T2): pass Ainit explicitly)
            upb[0, 1, 1], upb[0, 1, 3] = 1.0e-8, 0.0
        else:
            upb[0, 1, 1], upb[0, 1, 3] = 3.0e-8, 4.0
    if strengthM1 == 3:
        upb[0, 1, 1], upb[0, 1, 3] = 3.5e-8, 6.0
    upb[0, 1, 2] = 0.8
    if strength == 8:
        upb[1, 1, 1], upb[1, 1, 2] = 1.0e-10, 3.0

    def fill(name: str, arr: np.ndarray) -> np.ndarray:
        if name in ov:
            v = ov[name]
            v = v.detach().cpu().numpy() if isinstance(v, Tensor) else np.asarray(v, float)
            arr = np.where(v != 0.0, v, arr)
        return arr

    # user-given values are filled first, so the `== 0.` tests below leave them alone
    egr, ggr, sgr = fill("egr_mev", egr), fill("ggr_mev", ggr), fill("sgr_mb", sgr)
    epr, gpr, tpr = fill("epr_mev", epr), fill("gpr_mev", gpr), fill("tpr_mb", tpr)

    # ISOE2 (INCOGNITA_ISOE2=e, default OFF): collective quasi-continuum E2 in the E2 Lorentzian slot (irad 1, l 2, i 1);
    # user-given values win (fill above), OFF never imports the module
    # ISOHOLD: INCOGNITA_ISOE2=g = the same term only where the core E(2+) < 1.0 MeV (collective nuclei)
    _ie2 = os.environ.get("INCOGNITA_ISOE2", "").strip().lower()
    if L1 > 2 and _ie2 in ("e", "g"):
        from physics.hf.gamma import isoe2

        lz = isoe2.lorentzian(int(Z), int(A), PI2H2C2 / 5.0)
        if _ie2 == "g" and (isoe2.core_values(int(Z), int(A)) or (99.0, 0.0))[0] >= 1.0:
            lz = None
        if lz is not None and tpr[1, 2, 1] == 0.0 and epr[1, 2, 1] == 0.0 and gpr[1, 2, 1] == 0.0:
            tpr[1, 2, 1], epr[1, 2, 1], gpr[1, 2, 1] = lz

    # gammapar.f90:94-115 -- E1 GDR from the RIPL table unless flagpsfglobal
    if not flagpsfglobal:
        rec = _read_gdr(nuclide_symbol(Z)).get(A)
        if rec is not None:
            eg1, sg1, gg1, eg2, sg2, gg2 = rec
            if egr[1, 1, 1] == 0.0:
                egr[1, 1, 1] = eg1
            if sgr[1, 1, 1] == 0.0:
                sgr[1, 1, 1] = sg1
            if ggr[1, 1, 1] == 0.0:
                ggr[1, 1, 1] = gg1
            if egr[1, 1, 2] == 0.0:
                egr[1, 1, 2] = eg2
            if sgr[1, 1, 2] == 0.0:
                sgr[1, 1, 2] = sg2
            if ggr[1, 1, 2] == 0.0:
                ggr[1, 1, 2] = gg2
    onethird = ONETHIRD
    # gammapar.f90:119-127 -- E1 and E2 systematics (single-precision literals)
    if egr[1, 1, 1] == 0.0:
        egr[1, 1, 1] = 31.2 * A ** (-onethird) + 20.6 * A ** (-(1.0 / 6.0))
    if ggr[1, 1, 1] == 0.0:
        ggr[1, 1, 1] = 0.026 * egr[1, 1, 1] ** 1.91
    if sgr[1, 1, 1] == 0.0:
        sgr[1, 1, 1] = 1.2 * 120.0 * Z * N / (A * _PI * ggr[1, 1, 1])
    if gmax >= 2:
        if egr[1, 2, 1] == 0.0:
            egr[1, 2, 1] = 63.0 * A ** (-onethird)
        if ggr[1, 2, 1] == 0.0:
            ggr[1, 2, 1] = 6.11 - 0.012 * A
        if sgr[1, 2, 1] == 0.0:
            sgr[1, 2, 1] = 1.4e-4 * Z**2 * egr[1, 2, 1] / (A**onethird * ggr[1, 2, 1])
    for l in range(3, gmax + 1):  # noqa: E741 -- gammapar.f90:128-132
        if egr[1, l, 1] == 0.0:
            egr[1, l, 1] = egr[1, l - 1, 1]
        if ggr[1, l, 1] == 0.0:
            ggr[1, l, 1] = ggr[1, l - 1, 1]
        if sgr[1, l, 1] == 0.0:
            sgr[1, l, 1] = sgr[1, l - 1, 1] * 8.0e-4
    ngr = [[1] * L1 for _ in range(2)]
    for irad in (0, 1):  # gammapar.f90:136-141
        for l in range(1, gmax + 1):  # noqa: E741
            if egr[irad, l, 2] != 0.0 and sgr[irad, l, 2] != 0.0:
                ngr[irad][l] = 2

    tables: dict[tuple[int, int], PSFTable] = {}
    n_t = 1
    # gammapar.f90:145-270 -- tabulated E1
    if strength > 2 and strength != 5:
        if strength in (6, 7, 9, 10) and flagupbend:
            n_t = 11
        if strength == 9:
            sub = "smlo2019global" if flagpsfglobal else "smlo2019"
        else:
            sub = _TABLE_DIRS_E1.get(strength)
        if sub is not None:
            got = _read_psf_table(
                str(structure_dir() / "gamma" / sub / f"{nuclide_symbol(Z)}.psf"), A, n_t
            )
            if got is not None:
                e_raw, f_tab = got
                tables[(1, 1)] = (e_raw, f_tab)
    tq = None
    if n_t > 1 and (1, 1) in tables:  # gammapar.f90:250-262: Tqrpa only set on a table hit
        tq = np.arange(n_t) * 0.2

    # gammapar.f90:275-300 -- M1 systematics
    if strengthM1 <= 2 or strengthM1 == 4:
        if egr[0, 1, 1] == 0.0:
            egr[0, 1, 1] = 41.0 * A ** (-onethird)
        if ggr[0, 1, 1] == 0.0:
            ggr[0, 1, 1] = 4.0
        if sgr[0, 1, 1] == 0.0:
            sgr[0, 1, 1] = -1.0  # resolved after the E1 strength is available (needs fstrength)
    if strengthM1 == 3:
        if egr[0, 1, 1] == 0.0:
            egr[0, 1, 1] = 18.0 / A ** (1.0 / 6.0)
        if ggr[0, 1, 1] == 0.0:
            ggr[0, 1, 1] = 4.0
        if sgr[0, 1, 1] == 0.0:
            sgr[0, 1, 1] = 0.03 * A ** (5.0 / 6.0)
        s2 = scissors.s2(Z, A) if scissors.mode() == "s2" else None  # SCISSORS2, rotors only
        if scissors.mode() == "k17" or actphys.scissors_k17(Z):  # PORTLEVER / ACTPHYS (Z >= 88)
            e_sc, g_sc, t_sc = scissors.k17(A, b2)
        elif s2 is not None:
            e_sc, g_sc, t_sc = s2
        else:
            e_sc, g_sc, t_sc = 5.0 / A**0.1, 1.5, 1.0e-2 * abs(b2) * A**0.9
        if epr[0, 1, 1] == 0.0:
            epr[0, 1, 1] = e_sc
        if gpr[0, 1, 1] == 0.0:
            gpr[0, 1, 1] = g_sc
        if tpr[0, 1, 1] == 0.0:
            tpr[0, 1, 1] = t_sc
    if strengthM1 == 4:
        if epr[0, 1, 1] == 0.0:
            epr[0, 1, 1] = 80.0 * abs(b2) / A ** (1.0 / 3.0)
        if gpr[0, 1, 1] == 0.0:
            gpr[0, 1, 1] = 1.5
        if tpr[0, 1, 1] == 0.0:
            tpr[0, 1, 1] = 42.4 * b2**2 / gpr[0, 1, 1]
    # gammapar.f90:318-433 -- tabulated M1 (reads nTqrpa columns as set by the E1 branch)
    if strengthM1 in _TABLE_DIRS_M1:
        psf_name = nuclide_symbol(Z) + ".psf"
        got = _read_psf_table(
            str(structure_dir() / "gamma" / _TABLE_DIRS_M1[strengthM1] / psf_name),
            A,
            n_t,
        )
        if got is not None:
            tables[(0, 1)] = got
    if strengthM1 == 10:
        if epr[0, 1, 1] == 0.0:
            epr[0, 1, 1] = 5.0 / A**0.1
        if gpr[0, 1, 1] == 0.0:
            gpr[0, 1, 1] = 1.5
        if tpr[0, 1, 1] == 0.0:
            tpr[0, 1, 1] = 1.0e-2 * abs(b2) * A**0.9
    if tmc and strengthM1 == 3:  # UQ1: sgr(M1) scaled before M2 takes it (gammapar.f90:441-445)
        sgr[0, 1, 1] = sgr[0, 1, 1] * float(tmc.get("sgr_m1", 1.0))
    for l in range(2, gmax + 1):  # noqa: E741 -- gammapar.f90:441-445
        if egr[0, l, 1] == 0.0:
            egr[0, l, 1] = egr[0, l - 1, 1]
        if ggr[0, l, 1] == 0.0:
            ggr[0, l, 1] = ggr[0, l - 1, 1]
        if sgr[0, l, 1] == 0.0:
            sgr[0, l, 1] = sgr[0, l - 1, 1] * 8.0e-4  # propagates the -1 sentinel; fixed below

    # M1SHARE (Incognita extension, not TALYS): `m1share s|t`. The tabulated M1 (strengthM1 8: D1M+QRPA spin-flip +
    # scissors) keeps only its part below E_c = E_sf - Gamma_sf/2 (m1share_split; scissors / low energy, still x the
    # card's ftable m1); the spin-flip above is replaced by an independent SLO (m1share_slo, NOT x ftable m1). The
    # E1 table is multiplied by the nucleus's `m1kappa Z A k` cell (1 without a cell): s everywhere, t only below
    # E_GDR - Gamma_GDR (first GDR hump as loaded) with a linear blend to 1 at E_GDR. Upbend, E2, M2 untouched.
    m1mode = m1share_mode(options)
    m1rot = False
    if m1mode in (4, 5):  # M1ROT r (rotors only) / b (p on non-rotors + r on rotors)
        if not abs(b2) < E1M1NR_BETA:
            m1mode, m1rot = 3, True
        else:
            m1mode = 3 if m1mode == 5 else 0
    elif m1mode == 3 and not abs(b2) < E1M1NR_BETA:
        m1mode = 0  # E1M1NR: rotors stay TALYS
    m1kap = 1.0
    e1_imax = 0
    m1_off_raw = None
    if m1mode == 3:  # E1M1NR: keep the unmodified M1 table and the unmodified E1 stretch pivot
        if (0, 1) in tables and (1, 1) in tables:
            m1_off_raw = tables[(0, 1)]
            f0 = tables[(1, 1)][1][1:, 0]
            e1_imax = int(np.argmax(f0 == f0.max())) + 1 if f0.max() > 0 else 0
        else:
            m1mode = 0
    if m1mode:
        kv = ov.get("m1kappa_cards")
        if kv is not None and np.isfinite(np.asarray(kv, float)[1, 1, 0]):
            m1kap = float(np.asarray(kv, float)[1, 1, 0])
        if (0, 1) in tables:
            e_raw, f_tab = tables[(0, 1)]
            ftm1 = float(fill("ftable", ftable)[0, 1])
            em = e_raw + float(fill("etable_mev", etable)[0, 1])
            w = m1share_split(A, em)
            sf = m1rot_slo(A, b2, em) if m1rot else m1share_slo(A, em)  # M1ROT: deformation-split spin-flip
            add = sf / (ONETHIRD * PI2H2C2 * ftm1)
            f_new = f_tab * w[:, None] + add[:, None]
            f_new[0, :] = f_tab[0, :]
            tables[(0, 1)] = (e_raw, f_new)
        if (1, 1) in tables and m1kap != 1.0 and m1mode != 3:
            e_raw, f_tab = tables[(1, 1)]
            if m1mode == 2:  # keep TALYS's stretch pivot (first T=0 maximum) of the unmodified table: kappa(E) lowers the
                f0 = f_tab[1:, 0]  # first GDR hump of a deformed nucleus and would move the maximum to the second hump
                e1_imax = int(np.argmax(f0 == f0.max())) + 1 if f0.max() > 0 else 0
            ee = e_raw + float(fill("etable_mev", etable)[1, 1])
            if m1mode == 1:
                b = np.ones_like(ee)
            else:
                eg, gg = float(egr[1, 1, 1]), float(ggr[1, 1, 1])
                b = np.clip((eg - ee) / gg, 0.0, 1.0)
            f_new = f_tab * (1.0 + (m1kap - 1.0) * b)[:, None]
            f_new[0, :] = f_tab[0, :]
            tables[(1, 1)] = (e_raw, f_new)

    # last-point guard, gammapar.f90:240-243 and 402-405
    psf_tables: dict[tuple[int, int], PSFTable] = {}
    for key, (e_raw, f_tab) in tables.items():
        f = f_tab.copy()
        for it in range(f.shape[1]):
            if f[NUMGAMQRPA, it] > f[NUMGAMQRPA - 1, it]:
                f[NUMGAMQRPA, it] = f[NUMGAMQRPA - 1, it] * 0.9
        psf_tables[key] = PSFTable(_t(e_raw), _t(onethird * PI2H2C2 * f))

    upb = fill("upbend", upb)
    # LEESHELL (Incognita extension, default OFF): the M1 low-energy enhancement needs open valence
    # shells (recoupling of high-j proton AND neutron spins); at a closed shell the default M1 upbend
    # strength C is 0. A rule on the DEFAULT, so explicit upbendc cards below still win (as in TALYS).
    if leeshell_closed(Z, A, leeshell_mode(options)):
        upb[0, 1, 1] = 0.0
    # LEESHELL fidelity fix: per-nucleus upbendc/e/f cards replace the default (a user 0 included,
    # input_gammapar.f90:392-407), the *adjust cards multiply (fstrength.f90:489-491)
    if "upbend_cards" in ov:
        v = np.asarray(ov["upbend_cards"], float)
        upb = np.where(np.isnan(v), upb, v)
    if "upbendadjust_cards" in ov:
        v = np.asarray(ov["upbendadjust_cards"], float)
        upb = upb * np.where(np.isnan(v), 1.0, v)
    if tmc:  # UQ1: the E1 table's ftable/wtable, as TALYS's `ftable Z A f 1 E1` would set them
        if strengthM1 != 3 and float(tmc.get("sgr_m1", 1.0)) != 1.0:
            raise NotImplementedError("UQ1: sgr(M1) factor is wired for strengthM1 3 only")
        ftable[1, 1] = ftable[1, 1] * float(tmc.get("ftable", 1.0))
        wtable[1, 1] = wtable[1, 1] * float(tmc.get("wtable", 1.0))
    gp = GammaParameters(
        Z=Z,
        A=A,
        zix=zix,
        nix=nix,
        strength=strength,
        strengthM1=strengthM1,
        gammax=gmax,
        flagupbend=flagupbend,
        flagpsfglobal=flagpsfglobal,
        egr_mev=_t(egr),
        ggr_mev=_t(ggr),
        sgr_mb=_t(sgr),
        epr_mev=_t(epr),
        gpr_mev=_t(gpr),
        tpr_mb=_t(tpr),
        ngr=tuple(tuple(r) for r in ngr),
        upbend=_t(upb),
        etable_mev=_t(fill("etable_mev", etable)),
        ftable=_t(fill("ftable", ftable)),
        wtable=_t(fill("wtable", wtable)),
        tables=psf_tables,
        n_tqrpa=n_t if tq is not None else 1,
        tqrpa_mev=_t(tq) if tq is not None else None,
        S_k0_mev=S_k0_mev,
        delta_mev=delta_mev,
        alev_per_mev=alev_per_mev,
        beta2=beta2,
        gamgam_ev=gamgam_ev,
        m1share=4 if m1rot else m1mode,
        m1kappa=m1kap if m1mode else 1.0,
        e1_imax=e1_imax,
        eadj_e1=_eadj.nucleus_bumps("fe1", Z, A),
        eadj_m1=_eadj.nucleus_bumps("fm1", Z, A),
    )
    # tensors from overrides keep their autograd graph (fill() only decided which entries are set)
    for name in (
        "egr_mev",
        "ggr_mev",
        "sgr_mb",
        "epr_mev",
        "gpr_mev",
        "tpr_mb",
        "upbend",
        "etable_mev",
        "ftable",
        "wtable",
    ):
        v = ov.get(name)
        if isinstance(v, Tensor) and v.requires_grad:
            base = getattr(gp, name)
            gp = replace(gp, **{name: torch.where(v != 0.0, v, base)})
    # gammapar.f90:128-132 and 441-445 fill E(l >= 3) and M(l >= 2) from multipolarity l - 1
    # when the user left them at zero. The numpy fill above already did so with the override's
    # VALUE; redo it on the tensors so a requires_grad egr/ggr/sgr also reaches the higher
    # multipoles it defaults (SPEED0 G0.3: without this, d capture / d sgr(M1) missed the M2
    # term and disagreed with finite differences by 8e-4). Same float64 products, same values.
    if any(isinstance(ov.get(n), Tensor) and ov[n].requires_grad
           for n in ("egr_mev", "ggr_mev", "sgr_mb")):
        new = {n: getattr(gp, n).clone() for n in ("egr_mev", "ggr_mev", "sgr_mb")}
        user = {n: (np.asarray(ov[n].detach().cpu().numpy() if isinstance(ov[n], Tensor)
                               else ov[n], float) != 0.0) if n in ov else None
                for n in ("egr_mev", "ggr_mev", "sgr_mb")}
        for irad, l0 in ((1, 3), (0, 2)):
            for l in range(l0, gmax + 1):  # noqa: E741
                for n, f in (("egr_mev", 1.0), ("ggr_mev", 1.0), ("sgr_mb", 8.0e-4)):
                    if user[n] is not None and user[n][irad, l, 1]:
                        continue
                    if (irad, n) == (0, "sgr_mb") and (strengthM1 <= 2 or strengthM1 == 4):
                        continue  # the -1 sentinel chain is resolved below, from tensors
                    prev = new[n][irad, l - 1, 1]
                    new[n] = new[n].index_put(
                        (torch.tensor([irad]), torch.tensor([l]), torch.tensor([1])),
                        (prev * f if f != 1.0 else prev).reshape(1))
        gp = replace(gp, **new)

    # ETABLEFIX: the `*adjust` keywords. TALYS applies the table ones when it reads the table
    # (gammapar.f90:261-267, 437-443, 566) and the resonance ones inside fstrength
    # (fstrength.f90:158-173, 456-471), so both reach gammapar's own fstrength(E1, 7 MeV) call
    # below: the E1 factors go on before it, the M1 ones after (the M1 normalisation itself uses
    # the unadjusted egr/ggr(M1), gammapar.f90:348-349).
    gp = _apply_adjust(gp, ov, 1)

    # gammapar.f90:287-296 -- RIPL-1/2 M1 normalisation needs the E1 strength at 7 MeV
    if strengthM1 <= 2 or strengthM1 == 4:
        from physics.hf.gamma.strength import fstrength_gp

        sg = gp.sgr_mb.clone()
        if sg[0, 1, 1] < 0.0:
            egamref = 7.0
            kgr1 = PI2H2C2 / 3.0
            enum = kgr1 * egamref * gp.ggr_mev[0, 1, 1] ** 2
            denom = (egamref**2 - gp.egr_mev[0, 1, 1] ** 2) ** 2 + (
                gp.ggr_mev[0, 1, 1] * egamref
            ) ** 2
            if strengthM1 == 1:
                factor = 1.58e-9 * A**0.47
            else:
                f7 = fstrength_gp(gp, 0.0, _t([egamref]), 1, 1)[0]
                factor = f7 / (0.0588 * A**0.878)
            sg[0, 1, 1] = factor * denom / enum
            for l in range(2, gmax + 1):  # noqa: E741
                if sgr[0, l, 1] < 0.0:
                    sg[0, l, 1] = sg[0, l - 1, 1] * 8.0e-4
            gp = replace(gp, sgr_mb=sg)
    gp = _apply_adjust(gp, ov, 0)
    if m1_off_raw is not None:  # E1M1NR: hold f_E1 + f_M1 pointwise (after every etable/ftable/wtable/adjust)
        gp = e1m1nr_transfer(gp, PSFTable(_t(m1_off_raw[0]), _t(onethird * PI2H2C2 * _qrpa_guard(m1_off_raw[1]))))
    # ISOHOLD (INCOGNITA_ISOHOLD="Z,A,h", default unset = OFF): the whole dipole (l = 1, E and M) strength of nucleus (Z, A)
    # times h; every l = 1 term of fstrength is linear in sgr / tpr / ftable (tables) / upbend C, so all paths carry it
    _ih = os.environ.get("INCOGNITA_ISOHOLD", "").strip()
    if _ih:
        hz, ha, hh = _ih.split(",")
        if int(hz) == int(Z) and int(ha) == int(A):
            h = float(hh)
            sg, tp, ft, up = gp.sgr_mb.clone(), gp.tpr_mb.clone(), gp.ftable.clone(), gp.upbend.clone()
            sg[:, 1, :] = sg[:, 1, :] * h
            tp[:, 1, :] = tp[:, 1, :] * h
            ft[:, 1] = ft[:, 1] * h
            up[:, 1, 1] = up[:, 1, 1] * h
            gp = replace(gp, sgr_mb=sg, tpr_mb=tp, ftable=ft, upbend=up)
    return gp


#: `*adjust` keyword -> (field, how): TALYS `et = etable + etableadjust`, `ft = ftable *
#: ftableadjust`, `wt = wtable * wtableadjust` (gammapar.f90:261-267, 437-443, 566) and
#: `egr1 = egr * egradjust` etc. (fstrength.f90:158-173, 456-471; `spr` fills tpr)
_ADJUST = (
    ("etableadjust", "etable_mev", "add"),
    ("ftableadjust", "ftable", "mul"),
    ("wtableadjust", "wtable", "mul"),
    ("egradjust", "egr_mev", "mul"),
    ("ggradjust", "ggr_mev", "mul"),
    ("sgradjust", "sgr_mb", "mul"),
    ("epradjust", "epr_mev", "mul"),
    ("gpradjust", "gpr_mev", "mul"),
    ("spradjust", "tpr_mb", "mul"),
)


def _apply_adjust(gp: GammaParameters, ov: dict, irad: int) -> GammaParameters:
    """`gp` with the radiation type `irad`'s `*adjust` overrides applied (zero = not set).

    TALYS: gammapar.f90:261-267, 437-443, 566; fstrength.f90:158-173, 456-471
    Test: tests/hf/test_etablefix.py
    """
    new = {}
    for key, field, how in _ADJUST:
        v = ov.get(key)
        if v is None:
            continue
        a = np.asarray(v.detach().cpu().numpy() if isinstance(v, Tensor) else v, float)
        if not a[irad].any():
            continue
        base = new.get(field, getattr(gp, field))
        sel = np.zeros(a.shape, bool)
        sel[irad] = a[irad] != 0.0
        if how == "add":
            new[field] = base + _t(np.where(sel, a, 0.0)).to(base.dtype)
        else:
            new[field] = base * _t(np.where(sel, a, 1.0)).to(base.dtype)
    return replace(gp, **new) if new else gp


def table_arrays(gp: GammaParameters, irad: int, l: int) -> tuple[Tensor, Tensor]:  # noqa: E741
    """Energies [MeV] and strengths [MeV^-3] of a table exactly as TALYS holds them after
    gammapar: etable shift, ftable scale, then the wtable stretch about the T = 0 maximum
    (gammapar.f90:208-218, 564-585). Differentiable in etable, ftable, wtable.

    TALYS: gammapar.f90:1 (gammapar)
    Test: A-psf
    """
    tab: PSFTable = gp.tables[(irad, l)]
    et = gp.etable_mev[irad, l]
    ft = gp.ftable[irad, l]
    e = tab.e_raw_mev + et
    e = torch.cat([tab.e_raw_mev[:1], e[1:]])  # index 0 is never read, stays 0
    f = tab.f_raw_mev3 * ft
    if not gp.flagpsfglobal:
        wt = gp.wtable[irad, l]
        f0 = f[1:, 0]
        # first maximum wins (strict `>` in gammapar.f90:571)
        imax = int(torch.argmax((f0 == f0.max()).to(torch.int64))) + 1 if f0.max() > 0 else None
        if (irad, l) == (1, 1) and gp.e1_imax > 0:  # M1SHARE t: pivot of the unmodified table
            imax = gp.e1_imax
        if imax is not None:
            emid = e[imax]
            e = torch.cat([e[:1], emid + (e[1:] - emid) * wt])
    return e, f


__all__ = [
    "GammaParameters",
    "PSFTable",
    "PI2H2C2",
    "NUMGAMQRPA",
    "gamma_parameters",
    "table_arrays",
    "structure_dir",
]
