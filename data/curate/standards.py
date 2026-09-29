"""Monitor / ratio renormalization against the IAEA Neutron Data Standards 2017
(blueprint §3.1 last row, §4.2 "Ratio and monitor-relative data must be converted
to absolute using the current Standards").

What is implemented
-------------------
* The point-wise standards tables in ``raw/standards/std2017`` are parsed once
  (:class:`StandardsTable`): H(n,n), 6Li(n,t), 10B(n,a), natC(n,n), 197Au(n,g),
  235U(n,f), 238U(n,f), plus the 238U(n,g) *reference* cross section (not a
  standard, flagged as such).
* :func:`StandardsTable.evaluate` interpolates a standard at arbitrary incident
  energies (lin-lin above 30 keV, log-log below, as the tables recommend); the
  isolated thermal points (0.0253 eV) are matched only within ±2 %. Energies
  outside a standard's range give ``nan``.
* :func:`ratio_to_absolute` turns a ratio ``σ_x / σ_std`` into ``σ_x`` in barns.
* :func:`monitor_ratio` gives ``σ_std2017(E) / σ_assumed(E)`` for data that were
  normalized to a monitor whose assumed value is given in the ``MONIT`` column.

Anything else (monitors that are not standards, PAR branches, angular monitors,
missing assumed values, energies outside the standard range) is left
*unconverted*: callers get ``None`` / ``nan`` and must flag the record.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import numpy as np

from data.ingest.exfor_reactions import ParsedReaction, ReactionParseError, parse_reaction

__all__ = [
    "STANDARDS_DIR",
    "STANDARDS_VERSION",
    "Standard",
    "StandardsTable",
    "load_standards",
    "monitor_ratio",
    "ratio_to_absolute",
    "standard_for_reaction",
]

STANDARDS_VERSION = "IAEA Neutron Standards 2017"
STANDARDS_DIR = Path(__file__).resolve().parents[2] / "raw" / "standards" / "std2017"

_LOGLOG_BELOW_EV = 30e3
_GAP_FACTOR = 50.0  # consecutive energies further apart than this start a new segment
_POINT_TOL = 0.02  # ±2 % window for isolated (thermal) points


@dataclass(frozen=True)
class Standard:
    name: str  # e.g. "197Au(n,g)"
    z: int
    a: int
    sf3: str  # EXFOR process code the standard corresponds to
    energy_ev: np.ndarray
    xs_b: np.ndarray
    dxs_pct: np.ndarray
    is_standard: bool = True  # False for "reference" cross sections (rec17)
    source_file: str = ""

    @property
    def emin_ev(self) -> float:
        return float(self.energy_ev[0])

    @property
    def emax_ev(self) -> float:
        return float(self.energy_ev[-1])


def _read_table(path: Path, columns: tuple[int, int, int] = (0, 1, 2)) -> tuple[np.ndarray, ...]:
    """Read ``En CS DCS`` rows from one std17 text file; returns (E_MeV, xs, dxs%)."""
    rows: list[tuple[float, float, float]] = []
    started = False
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        s = line.strip()
        if not s:
            continue
        if s.startswith("MeV"):
            started = True
            continue
        if not started:
            continue
        toks = s.replace("*", " ").split()
        try:
            e = float(toks[columns[0]])
            xs = float(toks[columns[1]])
            d = float(toks[columns[2]])
        except (ValueError, IndexError):
            continue
        rows.append((e, xs, d))
    if not rows:
        raise ValueError(f"no numeric rows found in {path}")
    arr = np.array(rows, dtype=np.float64)
    return arr[:, 0], arr[:, 1], arr[:, 2]


def _std(name: str, z: int, a: int, sf3: str, fname: str, *, cols=(0, 1, 2), ref=False):
    path = STANDARDS_DIR / fname
    e_mev, xs, d = _read_table(path, cols)
    order = np.argsort(e_mev, kind="stable")
    return Standard(
        name=name,
        z=z,
        a=a,
        sf3=sf3,
        energy_ev=e_mev[order] * 1e6,
        xs_b=xs[order],
        dxs_pct=d[order],
        is_standard=not ref,
        source_file=fname,
    )


class StandardsTable:
    """All standards keyed by ``(Z, A, SF3)``; A == 0 means natural target."""

    def __init__(self, standards: list[Standard]):
        self.standards = standards
        self._by_key: dict[tuple[int, int, str], Standard] = {}
        for s in standards:
            self._by_key[(s.z, s.a, s.sf3)] = s

    # ----------------------------------------------------------------- lookup
    def get(self, z: int, a: int, sf3: str) -> Standard | None:
        return self._by_key.get((z, a, sf3.upper()))

    def for_reaction(self, rx: ParsedReaction | str) -> Standard | None:
        """Standard matching a *simple* reaction (no combinations, no PAR branch)."""
        if isinstance(rx, str):
            try:
                rx = parse_reaction(rx)
            except ReactionParseError:
                return None
        if rx.operator is not None:
            return None
        sf = rx.sf
        if (sf.sf2 or "").upper() != "N" or (sf.sf6 or "").upper() != "SIG":
            return None
        if sf.sf5:  # PAR, ... : partial branches are not the standard
            return None
        if sf.sf8 and sf.sf8.upper() not in ("", "A", "RAW"):
            # spectrum-averaged / Maxwellian monitors are not the point-wise standard
            return None
        z, a = rx.target.z, rx.target.a
        sf3 = (sf.sf3 or "").upper()
        # aliases: 6Li(n,a)t == 6Li(n,t)a; H/C total == elastic in the standard range
        if z == 3 and a == 6 and sf3 in ("A", "T"):
            sf3 = "T"
        if z in (1, 6) and sf3 == "TOT":
            sf3 = "EL"
        if z == 6 and a == 12:
            a = 0  # natural carbon standard is 98.9 % 12C; used interchangeably
        return self.get(z, a, sf3)

    # ----------------------------------------------------------------- evaluate
    @staticmethod
    def _segments(e: np.ndarray) -> list[tuple[int, int]]:
        segs: list[tuple[int, int]] = []
        start = 0
        for i in range(1, len(e)):
            if e[i] / e[i - 1] > _GAP_FACTOR:
                segs.append((start, i))
                start = i
        segs.append((start, len(e)))
        return segs

    def evaluate(self, std: Standard, energy_ev) -> np.ndarray:
        """Interpolate ``std`` at ``energy_ev`` (array-like, eV). ``nan`` outside coverage."""
        e_in = np.asarray(energy_ev, dtype=np.float64)
        out = np.full(e_in.shape, np.nan)
        e = std.energy_ev
        xs = std.xs_b
        for lo, hi in self._segments(e):
            se, sx = e[lo:hi], xs[lo:hi]
            if hi - lo == 1:  # isolated point (thermal)
                mask = np.abs(e_in / se[0] - 1.0) <= _POINT_TOL
                out[mask] = sx[0]
                continue
            mask = (e_in >= se[0]) & (e_in <= se[-1])
            if not mask.any():
                continue
            ei = e_in[mask]
            res = np.empty_like(ei)
            low = ei < _LOGLOG_BELOW_EV
            if low.any():
                pos = sx > 0
                if pos.all():
                    res[low] = np.exp(np.interp(np.log(ei[low]), np.log(se), np.log(sx)))
                else:
                    res[low] = np.interp(ei[low], se, sx)
            if (~low).any():
                res[~low] = np.interp(ei[~low], se, sx)
            out[mask] = res
        return out


@lru_cache(maxsize=1)
def load_standards(directory: Path | None = None) -> StandardsTable:
    global STANDARDS_DIR
    if directory is not None:
        STANDARDS_DIR = Path(directory)
    stds = [
        _std("1H(n,n)", 1, 1, "EL", "std17-001_H_001.txt"),
        _std("6Li(n,t)", 3, 6, "T", "std17-003_Li_006.txt"),
        _std("10B(n,a)", 5, 10, "A", "std17-005_B_010.txt", cols=(0, 3, 4)),
        _std("natC(n,n)", 6, 0, "EL", "std17-006_C_000.txt"),
        _std("197Au(n,g)", 79, 197, "G", "std17-079_Au_197.txt"),
        _std("235U(n,f)", 92, 235, "F", "std17-092_U_235.txt"),
        _std("238U(n,f)", 92, 238, "F", "std17-092_U_238.txt"),
        _std("238U(n,g) [reference]", 92, 238, "G", "rec17-092_U_238g.txt", ref=True),
    ]
    return StandardsTable(stds)


def standard_for_reaction(reaction: str | ParsedReaction) -> Standard | None:
    return load_standards().for_reaction(reaction)


# --------------------------------------------------------------------------- conversions


def ratio_to_absolute(
    values, energy_ev, denominator: str | ParsedReaction
) -> tuple[np.ndarray, Standard] | None:
    """``σ_x/σ_std`` (dimensionless) × ``σ_std2017(E)`` → ``σ_x`` in barns.

    Returns ``None`` when the denominator is not one of the standards. Points
    outside the standard's energy range come back as ``nan``.
    """
    table = load_standards()
    std = table.for_reaction(denominator)
    if std is None:
        return None
    sig = table.evaluate(std, energy_ev)
    return np.asarray(values, dtype=np.float64) * sig, std


def monitor_ratio(
    monitor: str | ParsedReaction, energy_ev, assumed_b
) -> tuple[np.ndarray, Standard] | None:
    """``σ_std2017(E) / σ_assumed(E)`` for a monitor-relative measurement.

    ``assumed_b`` is the monitor cross section the authors used (EXFOR ``MONIT``
    column, already in barns; a scalar is broadcast). Returns ``None`` when the
    monitor is not a standard; ``nan`` where the standard does not cover ``E``
    or the assumed value is missing / non-positive.
    """
    table = load_standards()
    std = table.for_reaction(monitor)
    if std is None:
        return None
    sig = table.evaluate(std, energy_ev)
    assumed = np.broadcast_to(np.asarray(assumed_b, dtype=np.float64), sig.shape)
    with np.errstate(divide="ignore", invalid="ignore"):
        ratio = np.where(assumed > 0, sig / assumed, np.nan)
    return ratio, std


_MONIT_RE = re.compile(r"^MONIT(\d*)$")


def is_monit_heading(heading: str) -> bool:
    return _MONIT_RE.match(heading.strip().upper()) is not None


def macs_30kev_au() -> float:
    """The 197Au MACS(30 keV) standard from the 2017 evaluation, barns."""
    return 0.620


def thermal_point(std: Standard) -> float | None:
    e = std.energy_ev
    i = np.argmin(np.abs(e - 0.0253))
    return float(std.xs_b[i]) if math.isclose(e[i], 0.0253, rel_tol=0.02) else None
