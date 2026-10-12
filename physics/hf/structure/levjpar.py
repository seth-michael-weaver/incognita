"""Incognita extension (LEVJPAR; not TALYS): a discrete level whose spin has the wrong half-integrality is treated as a level of
unknown spin.

Env INCOGNITA_LEVJ=1 (y/yes). Default OFF, and OFF never changes a `Levels` object.

Defect: odd-A nuclei need half-integer J, even-A integer J. The TALYS/RIPL level files give 145 levels in 57 odd-A nuclides an
integer J (levels/final; e.g. Pd-105 level 15, J = 4.0 for ENSDF (1/2+:9/2+); Te-123 level 30, J = 2.0 for (3/2-:9/2-)): almost all
carry the file's 'J' (spin assigned) flag, so the assignment drew from the ENSDF range in integer steps. levels.f90 passes them
through, and every angular-momentum sum then couples target J + s + l to the wrong integrality (STELLARSEF: the reciprocity
sigma(0->mu)/c_0 = sigma(mu->0)/c_mu fails by up to 0.53 on such a level).

Rule (no fitted number, the same for every nucleus): the level's J is unknown, so it is re-assigned the way an unknown spin is,
from the spin distribution, among the values the nucleus allows next to the file value:
  C = {J - 1/2, J + 1/2} (>= 0); S = the spins of the right integrality named in the level's own ENSDF J^pi string (file columns
  61-78, ranges 'a:b' / 'a TO b' expanded in unit steps); C' = C & S, else the members of S nearest J when S is non-empty, else C;
  J* = argmax over C' of (2J+1) exp(-(J+1/2)^2 / (2 sigma^2)), sigma^2 = (0.83 A^0.26)^2 (densitypar.f90 scutoffsys); ties -> smaller.
Energy, parity, half-life and branches are kept. Applied in `levels._levels_of_values` to every level read (0..min(nnn, 300)) of
every nucleus, so the Py / C / fast / GPU chains all read the corrected `Levels`.
Test: tests/hf/test_levjpar.py
"""

from __future__ import annotations

import math
import os
import re
from functools import lru_cache

__all__ = ["ENV", "enabled", "corrections", "new_spin", "ensdf_spins", "LAST"]

ENV = "INCOGNITA_LEVJ"
LAST: dict = {}  # (Z, A) -> {rank: (J_file, J_new, ensdf)} of the last corrected block (diagnostics only)

_FRAC = r"(\d+(?:/2)?)"


def enabled() -> bool:
    return os.environ.get(ENV, "0").strip().lower() in ("1", "y", "yes", "on")


def _val(x: str) -> float:
    return float(x[:-2]) / 2.0 if x.endswith("/2") else float(x)


def ensdf_spins(s: str) -> set[float]:
    """Spin values named in an ENSDF J^pi string ('' -> empty); ranges 'a:b' and 'a TO b' expanded in unit steps."""
    s = s.strip()
    out: set[float] = set()
    if not s:
        return out
    for m in re.finditer(_FRAC + r"\s*[+-]?\)?\s*(?::|\bTO\b)\s*\(?" + _FRAC, s):
        a, b = _val(m.group(1)), _val(m.group(2))
        v = a
        while v <= b + 1e-9:
            out.add(v)
            v += 1.0
    for x in re.findall(_FRAC, s):
        out.add(_val(x))
    return out


def new_spin(A: int, j: float, ensdf: str) -> float:
    """The re-assigned spin of a level with the wrong integrality (see the module rule)."""
    cand = [v for v in (j - 0.5, j + 0.5) if v >= 0.0]
    allowed = sorted(v for v in ensdf_spins(ensdf) if int(round(2 * v)) % 2 == A % 2)
    if allowed:
        both = [v for v in cand if v in allowed]
        if both:
            cand = both
        else:
            d = min(abs(v - j) for v in allowed)
            cand = [v for v in allowed if abs(abs(v - j) - d) < 1e-9]
    s2 = (0.83 * A ** 0.26) ** 2
    w = [(2 * v + 1) * math.exp(-((v + 0.5) ** 2) / (2 * s2)) for v in cand]
    best = max(w)
    return min(v for v, x in zip(cand, w) if x >= best * (1 - 1e-12))


@lru_cache(maxsize=4096)
def corrections(Z: int, A: int, disctable: int) -> tuple[tuple[int, float], ...]:
    """((rank, J*), ...) for the levels 0..min(nnn, 300) of (Z, A) whose file J has the wrong integrality; () when none."""
    from physics.hf.structure.files import level_records

    block = level_records(int(Z), int(A), int(disctable))
    if block is None:
        return ()
    nnn, recs = block
    nmax = min(int(nnn), 300)
    out, info = [], {}
    k = 0
    for i in range(nmax + 1):
        if k >= len(recs):
            break
        r = recs[k]
        j = float(r[15:21])
        nb = int(r[26:29])
        k += 1 + nb
        if int(round(2 * j)) % 2 != int(A) % 2:
            ens = r[60:78] if len(r) > 60 else ""
            jn = new_spin(int(A), j, ens)
            out.append((i, jn))
            info[i] = (j, jn, ens.strip())
    if info:
        LAST[(int(Z), int(A))] = info
    return tuple(out)
