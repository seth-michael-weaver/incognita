"""Unit normalization for EXFOR quantities (blueprint §4.2: every energy in eV,
every cross section in barns; keep the original unit string).

EXFOR unit codes come from Dictionary 25. This module understands the ones that
matter for the Phase 1 pipeline plus a few common misspellings / long forms
("MILLI-BARNS", "BARNS", "MILLIBARN", ...). A unit is treated as a product of
*atoms* joined by ``*`` and ``/`` (``MB/SR``, ``B*EV``, ``MB/MEV/SR``); each
atom is looked up in :data:`ATOMS`, which maps it to a canonical base symbol and
a scale factor. Anything unknown is left unconverted and reported as such, never
silently passed through as a number in unknown units.

Canonical symbols: ``eV`` (energy), ``b`` (area), ``sr`` (solid angle), ``deg``
(angle), ``s`` (time), ``1`` (dimensionless), ``%`` (per cent).
"""

from __future__ import annotations

import math
import re
from collections.abc import Iterable
from dataclasses import dataclass

__all__ = [
    "ATOMS",
    "UnitInfo",
    "canonical_unit",
    "convert",
    "energy_to_ev",
    "is_energy_unit",
    "is_xs_unit",
    "parse_unit",
    "to_barn",
    "to_ev",
]

# atom code -> (canonical base, scale factor to the canonical base)
ATOMS: dict[str, tuple[str, float]] = {
    # --- energy ---
    "EV": ("eV", 1.0),
    "MILLI-EV": ("eV", 1e-3),
    "MICRO-EV": ("eV", 1e-6),
    "KEV": ("eV", 1e3),
    "MEV": ("eV", 1e6),
    "GEV": ("eV", 1e9),
    "TEV": ("eV", 1e12),
    "MILLIEV": ("eV", 1e-3),
    "NANO-EV": ("eV", 1e-9),
    "SR2": ("sr^2", 1.0),
    "MICROEV": ("eV", 1e-6),
    "MILLI-EV.": ("eV", 1e-3),
    "K": ("eV", 8.617333262e-5),  # temperature as energy (kT), Boltzmann constant in eV/K
    "K9": ("eV", 8.617333262e4),  # 10**9 K, as kT
    "DEG-K": ("eV", 8.617333262e-5),
    # --- area (cross section) ---
    "B": ("b", 1.0),
    "BARN": ("b", 1.0),
    "BARNS": ("b", 1.0),
    "MB": ("b", 1e-3),
    "MILLI-B": ("b", 1e-3),
    "MILLIBARN": ("b", 1e-3),
    "MILLIBARNS": ("b", 1e-3),
    "MILLI-BARN": ("b", 1e-3),
    "MILLI-BARNS": ("b", 1e-3),
    "MICRO-B": ("b", 1e-6),
    "MICROBARN": ("b", 1e-6),
    "MICROBARNS": ("b", 1e-6),
    "MICRO-BARN": ("b", 1e-6),
    "MICRO-BARNS": ("b", 1e-6),
    "MUB": ("b", 1e-6),
    "MU-B": ("b", 1e-6),
    "MICROB": ("b", 1e-6),
    "NB": ("b", 1e-9),
    "NANO-B": ("b", 1e-9),
    "NANOBARN": ("b", 1e-9),
    "PB": ("b", 1e-12),
    "PICO-B": ("b", 1e-12),
    "PICOBARN": ("b", 1e-12),
    "FB": ("b", 1e-15),
    "KB": ("b", 1e3),
    "KILO-B": ("b", 1e3),
    "KILOBARN": ("b", 1e3),
    "CM2": ("b", 1e24),
    "MM2": ("b", 1e22),
    "FM2": ("b", 1e-2),
    # --- solid angle, angle, misc ---
    "SR": ("sr", 1.0),
    "MSR": ("sr", 1e-3),
    "ADEG": ("deg", 1.0),
    "DEG": ("deg", 1.0),
    "MRAD": ("deg", 180.0 / math.pi * 1e-3),
    "RAD": ("deg", 180.0 / math.pi),
    "SEC": ("s", 1.0),
    "MSEC": ("s", 1e-3),
    "MICROSEC": ("s", 1e-6),
    "NSEC": ("s", 1e-9),
    "PSEC": ("s", 1e-12),
    "MIN": ("s", 60.0),
    "HR": ("s", 3600.0),
    "D": ("s", 86400.0),
    "YR": ("s", 3.15576e7),
    "NO-DIM": ("1", 1.0),
    "NODIM": ("1", 1.0),
    "DIMENSIONLESS": ("1", 1.0),
    "PER-CENT": ("%", 1.0),
    "PERCENT": ("%", 1.0),
    "%": ("%", 1.0),
    "PRD": ("1", 1.0),  # per reaction / per decay: dimensionless
    "PRT": ("1", 1.0),
    "PC/FIS": ("%", 1.0),  # per cent per fission
    "1/CM": ("1/cm", 1.0),
    "1/MEV": ("1/eV", 1e-6),
    "1/KEV": ("1/eV", 1e-3),
    "1/EV": ("1/eV", 1.0),
    "MEV-1": ("1/eV", 1e-6),
    "KEV-1": ("1/eV", 1e-3),
    "EV-1": ("1/eV", 1.0),
    "MEV**-1": ("1/eV", 1e-6),
    "COS": ("1", 1.0),
}

# EXFOR-specific compound codes that do not decompose neatly
_SPECIAL: dict[str, tuple[str, float]] = {
    "B*EV": ("b*eV", 1.0),
    "B*KEV": ("b*eV", 1e3),
    "B*MEV": ("b*eV", 1e6),
    "MB*EV": ("b*eV", 1e-3),
    "MB*KEV": ("b*eV", 1.0),
    "MB*MEV": ("b*eV", 1e3),
    "B*RT-EV": ("b*eV^0.5", 1.0),
    "MB*RT-EV": ("b*eV^0.5", 1e-3),
    "B*RT-KEV": ("b*eV^0.5", math.sqrt(1e3)),
    "MB*RT-KEV": ("b*eV^0.5", 1e-3 * math.sqrt(1e3)),
    "B/SR": ("b/sr", 1.0),
    "MB/SR": ("b/sr", 1e-3),
    "MICRO-B/SR": ("b/sr", 1e-6),
    "MU-B/SR": ("b/sr", 1e-6),
    "NB/SR": ("b/sr", 1e-9),
    "PB/SR": ("b/sr", 1e-12),
    "B/EV": ("b/eV", 1.0),
    "B/KEV": ("b/eV", 1e-3),
    "B/MEV": ("b/eV", 1e-6),
    "MB/EV": ("b/eV", 1e-3),
    "MB/KEV": ("b/eV", 1e-6),
    "MB/MEV": ("b/eV", 1e-9),
    "MICRO-B/EV": ("b/eV", 1e-6),
    "MICRO-B/KEV": ("b/eV", 1e-9),
    "MICRO-B/MEV": ("b/eV", 1e-12),
    "B/SR/EV": ("b/sr/eV", 1.0),
    "B/SR/KEV": ("b/sr/eV", 1e-3),
    "B/SR/MEV": ("b/sr/eV", 1e-6),
    "MB/SR/EV": ("b/sr/eV", 1e-3),
    "MB/SR/KEV": ("b/sr/eV", 1e-6),
    "MB/SR/MEV": ("b/sr/eV", 1e-9),
    "MICRO-B/SR/MEV": ("b/sr/eV", 1e-12),
    "MU-B/SR/MEV": ("b/sr/eV", 1e-12),
    "MB/MEV/SR": ("b/sr/eV", 1e-9),
    "B/MEV/SR": ("b/sr/eV", 1e-6),
    "ARB-UNITS": ("arb", 1.0),
    "ARB-UNIT": ("arb", 1.0),
    "AU": ("arb", 1.0),
    "RT-EV": ("eV^0.5", 1.0),
    "RT-KEV": ("eV^0.5", math.sqrt(1e3)),
    "RT-MEV": ("eV^0.5", math.sqrt(1e6)),
    "EV**0.5": ("eV^0.5", 1.0),
    "MILLI-EV**0.5": ("eV^0.5", math.sqrt(1e-3)),
    "MEV/A": ("eV/A", 1e6),
    "KEV/A": ("eV/A", 1e3),
    "EV/A": ("eV/A", 1.0),
    "1/EV**0.5": ("1/eV^0.5", 1.0),
}

_UNCONVERTIBLE = {"arb", "?"}

_TOKEN_RE = re.compile(r"([*/])")


@dataclass(frozen=True)
class UnitInfo:
    """Result of :func:`parse_unit`."""

    original: str
    canonical: str  # e.g. "b", "eV", "b/sr", "%", "1", or "?" if unknown
    factor: float  # multiply an original value by this to express it in ``canonical``
    known: bool

    @property
    def convertible(self) -> bool:
        return self.known and self.canonical not in _UNCONVERTIBLE


def _clean(code: str) -> str:
    return code.strip().upper()


def parse_unit(code: str) -> UnitInfo:
    """Parse an EXFOR unit code into a canonical unit and a scale factor.

    Unknown codes yield ``known=False`` and ``canonical="?"``, ``factor=nan``.
    """
    raw = code
    code = _clean(code)
    if not code:
        return UnitInfo(raw, "1", 1.0, True)
    if code in _SPECIAL:
        base, fac = _SPECIAL[code]
        return UnitInfo(raw, base, fac, True)
    if code in ATOMS:
        base, fac = ATOMS[code]
        return UnitInfo(raw, base, fac, True)

    # compound: tokens separated by * and /
    parts = _TOKEN_RE.split(code)
    if len(parts) < 3:
        return UnitInfo(raw, "?", math.nan, False)
    num: list[str] = []
    den: list[str] = []
    fac = 1.0
    op = "*"
    for tok in parts:
        if tok in ("*", "/"):
            op = tok
            continue
        if tok not in ATOMS:
            return UnitInfo(raw, "?", math.nan, False)
        base, f = ATOMS[tok]
        if op == "*":
            fac *= f
            if base != "1":
                num.append(base)
        else:
            fac /= f
            if base != "1":
                den.append(base)
    canon = "*".join(num) if num else "1"
    if den:
        canon += "/" + "/".join(den)
    return UnitInfo(raw, canon, fac, True)


def canonical_unit(code: str) -> str:
    return parse_unit(code).canonical


def is_energy_unit(code: str) -> bool:
    return parse_unit(code).canonical == "eV"


def is_xs_unit(code: str) -> bool:
    """True for plain cross-section units (b, mb, ...), not differential ones."""
    return parse_unit(code).canonical == "b"


def convert(values: Iterable[float], code: str) -> tuple[list[float], UnitInfo]:
    """Scale ``values`` from EXFOR unit ``code`` into its canonical unit.

    Raises ``ValueError`` for unknown or unconvertible units.
    """
    info = parse_unit(code)
    if not info.convertible:
        raise ValueError(f"unit {code!r} is not convertible")
    f = info.factor
    return [v * f if v is not None and not math.isnan(v) else math.nan for v in values], info


def to_ev(value: float, code: str) -> float:
    info = parse_unit(code)
    if info.canonical != "eV":
        raise ValueError(f"{code!r} is not an energy unit")
    return value * info.factor


def energy_to_ev(values: Iterable[float], code: str) -> list[float]:
    info = parse_unit(code)
    if info.canonical != "eV":
        raise ValueError(f"{code!r} is not an energy unit")
    f = info.factor
    return [v * f for v in values]


def to_barn(value: float, code: str) -> float:
    info = parse_unit(code)
    if info.canonical != "b":
        raise ValueError(f"{code!r} is not a cross-section unit")
    return value * info.factor


def from_ev(value_ev: float, code: str) -> float:
    """Inverse of :func:`to_ev` (used by round-trip tests)."""
    info = parse_unit(code)
    if info.canonical != "eV":
        raise ValueError(f"{code!r} is not an energy unit")
    return value_ev / info.factor


def from_barn(value_b: float, code: str) -> float:
    info = parse_unit(code)
    if info.canonical != "b":
        raise ValueError(f"{code!r} is not a cross-section unit")
    return value_b / info.factor
