"""Canonical nuclide key convention used across every Incognita table.

A nuclide is identified by ``(Z, N, iso)`` where ``iso`` is the isomeric-state
index (0 = ground state, 1 = first isomer, ...). The canonical string form
produced by :func:`nuclide_id` is ``"Z026N030M0"`` (zero-padded so keys sort
by Z, then N, then isomer), which is what every Parquet table joins on.
"""

from __future__ import annotations

import re
from typing import NamedTuple

__all__ = ["NuclideKey", "nuclide_id", "nuclide_id_from_za", "parse_nuclide_id"]

_ID_RE = re.compile(r"^Z(?P<Z>\d{3})N(?P<N>\d{3})M(?P<iso>\d+)$")


class NuclideKey(NamedTuple):
    """Structured nuclide key. ``A`` is derived, never stored separately."""

    Z: int
    N: int
    iso: int = 0

    @property
    def A(self) -> int:
        return self.Z + self.N

    @property
    def id(self) -> str:
        return nuclide_id(self.Z, self.N, self.iso)


def _check(Z: int, N: int, iso: int) -> None:
    if Z < 0 or N < 0 or iso < 0:
        raise ValueError(f"Z, N, iso must be non-negative; got ({Z}, {N}, {iso})")
    if Z + N == 0:
        raise ValueError("a nuclide needs at least one nucleon")
    if Z > 999 or N > 999:
        raise ValueError(f"Z, N must be < 1000; got ({Z}, {N})")


def nuclide_id(Z: int, N: int, iso: int = 0) -> str:
    """Canonical string key for a nuclide: ``nuclide_id(26, 30) == "Z026N030M0"``."""
    Z, N, iso = int(Z), int(N), int(iso)
    _check(Z, N, iso)
    return f"Z{Z:03d}N{N:03d}M{iso}"


def nuclide_id_from_za(Z: int, A: int, iso: int = 0) -> str:
    """Same key, built from (Z, A) as EXFOR / ENDF quote it."""
    return nuclide_id(Z, int(A) - int(Z), iso)


def parse_nuclide_id(key: str) -> NuclideKey:
    """Inverse of :func:`nuclide_id`. Raises ``ValueError`` on malformed keys."""
    m = _ID_RE.match(key)
    if m is None:
        raise ValueError(f"not a canonical nuclide id: {key!r}")
    return NuclideKey(int(m["Z"]), int(m["N"]), int(m["iso"]))
