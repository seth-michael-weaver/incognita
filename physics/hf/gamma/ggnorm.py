"""GAMMAALL: normalise each nucleus's E1 photon strength to its measured s-wave radiative
strength <Gamma_gamma>/D0 (RIPL-3, 2009), as an engine option.

TALYS-2.24's default photon strength (SMLO-2019 tables, `strength 9`, no `gnorm`) with its
default level density gives a theoretical s-wave <Gamma_gamma> that scatters around the measured
one by ~0.24 dex (x1.7) over the chart, with a median offset near zero
(`docs/results/gammaall.md`). At keV energies, where Gamma_n >> Gamma_gamma, capture is
proportional to the radiative strength Gamma_gamma/D0 = the gamma sum over final states
(radwidtheory's `swaveth`); D0 itself cancels. So the capture-relevant anchor is
Gamma_gamma/D0, and TALYS's own `gnorm y` (which matches Gamma_gamma alone) is the same thing
only where TALYS's level density reproduces the measured D0 (C/E D0 = 1, true for most nuclei
but not all: K-42 0.17, Zr-97 0.23, Cs-136 1.40).

`INCOGNITA_GGAMMA_NORM` selects a factor g on the default E1 `ftable` of every nucleus (Z, A)
that has one in `ggnorm_ripl3.csv`:

    ""/0     off (TALYS defaults; CHART1 and the fidelity harnesses measure this)
    ripl3d0  g such that TALYS's Gamma_gamma_th / D0_th = RIPL-3 Gamma_gamma / RIPL-3 D0
    ripl3    g such that Gamma_gamma_th = RIPL-3 Gamma_gamma (TALYS `gnorm y` done in eV)

Both factors come from stock TALYS-2.24's own radwidtheory iteration (`gnorm y` with an explicit
`gamgam` in eV -- never the keV resonance-table number, GNORMFIX), run once per compound nucleus
by `scripts/gammaall/`. Only RIPL-3 values (Capote et al. 2009; per-entry references 1981-2008)
are used, never BNL-2018, so no post-2012 measurement reaches a factor. Actinides (Z > 82) are
never touched (another work package owns them). A nucleus without a measured Gamma_gamma (or,
for ripl3d0, without a RIPL-3 D0) keeps g = 1.

The factor multiplies the default before user keywords are applied, so an explicit `ftable`
override still wins, as for TALYS's own defaults. It is keyed by the nucleus, so it applies
wherever that nucleus appears in a cascade (compound nucleus, or residual after emission) --
the same as writing `ftable Z A <g x default> E1` for each such nucleus in a stock TALYS input.
"""

from __future__ import annotations

import csv
import os
from functools import cache
from pathlib import Path

MODES = ("", "ripl3d0", "ripl3")
TABLE = Path(__file__).with_name("ggnorm_ripl3.csv")
ZMAX = 82  # actinides (Z > 82) are left to ACTPHYS
_COLUMN = {"ripl3d0": "g_ripl3d0", "ripl3": "g_ripl3"}


def _parse(v: str | None) -> str:
    m = (v or "").strip().lower()
    m = "" if m == "0" else m
    if m not in MODES:
        raise ValueError(f"INCOGNITA_GGAMMA_NORM={v!r}: expected one of {MODES} (or 0)")
    return m


_MODE = _parse(os.environ.get("INCOGNITA_GGAMMA_NORM"))


def mode() -> str:
    return _MODE


@cache
def table(column: str) -> dict[tuple[int, int], float]:
    """(Z, A) of the nucleus -> E1 ftable factor, from `ggnorm_ripl3.csv` (blank = no factor)."""
    out: dict[tuple[int, int], float] = {}
    with TABLE.open() as fh:
        for r in csv.DictReader(line for line in fh if not line.startswith("#")):
            v = r.get(column, "").strip()
            if v:
                out[(int(r["Z"]), int(r["A"]))] = float(v)
    return out


def factor(Z: int, A: int) -> float:
    """The active mode's E1 ftable factor for nucleus (Z, A); 1.0 when off or not tabulated.

    TALYS: radwidtheory.f90:253 (the `gnorm` rescaling of the E1 ftable), run offline
    Test: tests/hf/test_gammaall_ggnorm.py
    """
    if not _MODE or Z > ZMAX:
        return 1.0
    return table(_COLUMN[_MODE]).get((int(Z), int(A)), 1.0)


def set_mode(m: str | None) -> str:
    """Switch in-process and drop every per-target cache (the mode is in none of their keys)."""
    global _MODE
    new = _parse(m)
    prev, _MODE = _MODE, new
    if prev != _MODE:
        from physics.hf.chartrun import drop_target_caches

        drop_target_caches(frozenset())
    return prev


__all__ = ["MODES", "TABLE", "ZMAX", "factor", "mode", "set_mode", "table"]
