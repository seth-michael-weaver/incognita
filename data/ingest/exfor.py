#!/usr/bin/env python3
"""WP-09: EXFOR (X4 format) → ``Measurement`` records → Parquet, streamed.

Input: ``raw/exfor/entry.zip`` (IAEA EXFOR Entry File, one X4 text file per
entry; the 2026-08-27 snapshot is a superset of the 2025 Master File in
``raw/exfor/exfor-2025.zip``, so the per-entry archive is what we parse).

The stdlib parser here handles the X4 record structure (ENTRY / SUBENT / BIB /
COMMON / DATA, 11-column fields, pointers) and the BIB keywords the schema
needs. Entries are read one at a time from the zip, parsed by a small worker
pool, and appended to a single Parquet file through ``pyarrow.ParquetWriter``
in row-group batches, so resident memory stays flat (a few hundred MB).

Contract for the two value blocks (blueprint §4.2, ``data/schema/measurement.py``):

* ``energy_ev`` (and the other independent variables) are always converted.
* ``original`` keeps the compilers' numbers **untouched** with the EXFOR unit
  code (``"MB"``, ``"NO-DIM"``, ...).
* ``renormalized`` holds the same points in canonical units (barns, b/sr, ...)
  whenever the unit is convertible; ``standards_version`` says what was done:
  ``"IAEA Neutron Standards 2017"`` when a ratio-to-standard or MONIT-column
  monitor renormalization was applied, ``"units-only"`` when only the unit
  conversion was possible (absolute data, or a monitor that is not a standard).
  ``renormalized is None`` means the values could not be expressed in barns
  (arbitrary units, raw yields, dimensionless ratios to non-standards, ...).
* ``stat_sigma`` is ``ERR-S`` when the compilers split the uncertainty,
  otherwise the unsplit total (``ERR-T`` / ``DATA-ERR``); ``sys_sigma`` is
  ``ERR-SYS`` only. Missing uncertainties stay ``None`` (never defaulted).

Monitor (MONIT) renormalization — rules added 2026-09-09 after the WP-12 curation
pass found factors of x4 (entry 40520) and x1000 (entry 31790); every rule is a
reason string in the ``renorm_reason`` column and a ``renorm:*`` stats key:

* The MONIT column is matched to *one* MONITOR reaction: the item carrying the
  same ``(MONITn)`` flag when flags are used, else the only unflagged item. A
  flag that lives only in MONIT-REF (the assumed value comes from another
  measurement) or several unflagged monitors for one column is
  ``monitor_reaction_ambiguous``: not applied. The reaction must be one of the
  six Standards: a *reference* cross section such as 238U(n,g) (20264) or the
  authors' own reaction measured elsewhere (40691: ``((MONIT)75-RE-0(N,G),,SIG)``
  next to a 235U(n,f) shape monitor) is ``monitor_not_standard``.
* The energy at which the assumed value holds is ``EN-NRM`` when present (the
  constant belongs to the normalization point, not to every data energy: 40520,
  32105, 40691), else the data energy when MONIT is a DATA column or the table
  has a single incident energy, else — a constant MONIT under a multi-energy
  table — only when the Standard is flat (< 10 %) over the table; otherwise
  ``monitor_energy_ambiguous``. Spectrum-averaged data (MXW/SPA/FIS/...) take a
  point-wise monitor value only at thermal or through ``EN-NRM``.
* The Standard must cover every point (``monitor_energy_partial_coverage``
  otherwise: a dataset is never half-renormalized) and the MONIT unit must be
  an area unit.
* Every per-point factor must lie inside ``RENORM_BAND`` (default [0.5, 2.0],
  ``--renorm-band``); outside it nothing is applied, the median factor is kept
  in ``renorm_factor_rejected`` and the reason is ``factor_out_of_band``
  (``:unit_slip_1000^k`` appended when it is a power of 1000, as in 31790 whose
  MONIT of 98.66 "MB" is really barns).

The four extra columns (``renorm_factor``, ``renorm_monitor``, ``renorm_reason``,
``renorm_factor_rejected``, see :class:`ExforMeasurement`) are appended after the
WP-03 ``Measurement`` schema; readers that select columns by name are unaffected.
Nothing is ever dropped: a rejected renormalization still yields the
``units-only`` block.

Usage::

    uv run python -m data.ingest.exfor --subset capture --zmin 26 --zmax 92
    uv run python -m data.ingest.exfor --subset all
"""

from __future__ import annotations

import argparse
import json
import math
import multiprocessing as mp
import os
import re
import sys
import time
import zipfile
from collections import Counter
from collections.abc import Iterable, Iterator
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, ClassVar

import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq

from data.curate import standards as std_mod
from data.curate.units import parse_unit
from data.ingest.exfor_reactions import ParsedReaction, ReactionParseError, parse_reaction
from data.schema.measurement import DataBlock, Measurement, QuantityType, ReactionSF

REPO = Path(__file__).resolve().parents[2]
_MAIN = Path(os.environ.get("INCOGNITA_MAIN", REPO)).expanduser()   # one data directory for every tool (default: the repository root)
RAW_ENTRY_ZIP = _MAIN / "raw" / "exfor" / "entry.zip"
STAGING = _MAIN / "staging"
EXFOR_VERSION = "2026-08-27"  # entry.zip snapshot date (raw/MANIFEST.json)

RSS_LIMIT_MB = 2500
WORKER_RSS_LIMIT_MB = 900
FIELD = 11
NFIELD_PER_LINE = 6

# Plausible band for a Standards monitor factor sigma_std2017 / sigma_assumed. The
# honest corrections in EXFOR sit within -15 %..+30 % (WP-12 curation pass); a
# factor outside this band is an ingest/compilation artefact and is recorded, not
# applied. Overridable per run (``--renorm-band``).
RENORM_BAND: tuple[float, float] = (0.5, 2.0)
# A constant MONIT under a multi-energy table is accepted only when the Standard
# varies less than this over the table's energies (then the energy is immaterial).
RENORM_FLAT_STANDARD_TOL = 0.10
_MONIT_HEADINGS = ("MONIT", "MONIT1", "MONIT2", "MONIT3", "MONIT4")
_MONIT_FLAG_RE = re.compile(r"^\(\((MONIT\d*)\)(.*)\)$", re.DOTALL)
# SF8 modifiers meaning "averaged over a spectrum": a point-wise Standard is not the
# monitor value the authors used unless the monitor energy is thermal (2200 m/s
# values of 1/v monitors equal the Standard's thermal point) or given by EN-NRM.
_SPECTRUM_SF8 = {"MXW", "SPA", "FIS", "FST", "EPI", "BRA", "BRS", "MSC", "TTA", "TT"}
_THERMAL_EV = 0.0253

__all__ = [
    "RENORM_BAND",
    "Entry",
    "ExforMeasurement",
    "RenormInfo",
    "Subentry",
    "Table",
    "build_measurements",
    "iter_entry_texts",
    "parse_entry",
    "run",
]


class ExforMeasurement(Measurement):
    """WP-03 ``Measurement`` plus the per-dataset renormalization audit trail.

    ``renorm_reason`` is always set (``monitor_to_standard``, ``ratio_to_standard``,
    ``units_only``, or the rejection reason). ``renorm_factor`` is the median
    factor actually applied to the ``original`` values in barns (monitor case), or
    the median Standard cross section multiplied into a ratio (ratio case); it is
    ``None`` when nothing beyond a unit conversion was done. ``renorm_monitor`` is
    the reaction the MONIT column / ratio denominator was matched to.
    ``renorm_factor_rejected`` keeps the factor that was computed but *not*
    applied, so nothing is lost and WP-12 can audit it.
    """

    renorm_factor: float | None = None
    renorm_monitor: str | None = None
    renorm_reason: str = "units_only"
    renorm_factor_rejected: float | None = None

    ARROW_SCHEMA: ClassVar[pa.Schema] = pa.schema(
        list(Measurement.ARROW_SCHEMA)
        + [
            pa.field("renorm_factor", pa.float64()),
            pa.field("renorm_monitor", pa.string()),
            pa.field("renorm_reason", pa.string(), nullable=False),
            pa.field("renorm_factor_rejected", pa.float64()),
        ]
    )


@dataclass
class RenormInfo:
    """Outcome of :func:`_renormalize` for one dataset (mirrors the four columns)."""

    reason: str = "units_only"
    monitor: str | None = None
    factor: float | None = None
    factor_rejected: float | None = None


# =========================================================================== X4 structure


@dataclass
class Table:
    """A COMMON or DATA block: headings (name, pointer), units, and a column-major matrix."""

    headings: list[tuple[str, str]] = field(default_factory=list)  # (name, pointer)
    units: list[str] = field(default_factory=list)
    columns: list[list[float]] = field(default_factory=list)

    @property
    def nrows(self) -> int:
        return len(self.columns[0]) if self.columns else 0


@dataclass
class BibItem:
    pointer: str  # "" when unpointered
    code: str  # leading parenthesised code, "" if none
    text: str  # free text (everything after the code)


@dataclass
class Subentry:
    accession: str  # e.g. "10001002"
    bib: dict[str, list[BibItem]] = field(default_factory=dict)
    common: Table | None = None
    data: Table | None = None
    nodata: bool = False


@dataclass
class Entry:
    entry: str
    subentries: list[Subentry] = field(default_factory=list)


_NUM_FIX = re.compile(r"^([+-]?\d*\.?\d+)([+-]\d+)$")


def _num(s: str) -> float:
    """EXFOR numeric field → float. Handles Fortran forms like ``4.75   +00`` / ``1.5-3``."""
    s = s.strip()
    if not s:
        return math.nan
    try:
        return float(s)
    except ValueError:
        s = s.replace(" ", "")
        try:
            return float(s)
        except ValueError:
            m = _NUM_FIX.match(s)
            if m:
                return float(f"{m[1]}e{m[2]}")
            return math.nan


def _fields(line: str, n: int) -> list[str]:
    body = line[: FIELD * NFIELD_PER_LINE]
    return [body[i * FIELD : (i + 1) * FIELD] for i in range(n)]


def _parse_table(lines: list[str], i: int, nfields: int) -> tuple[Table, int]:
    """Parse a COMMON/DATA block starting at ``lines[i]`` (the line after the keyword).

    Returns the table and the index of the ENDCOMMON/ENDDATA line.
    """
    nl = (nfields + NFIELD_PER_LINE - 1) // NFIELD_PER_LINE
    heads: list[tuple[str, str]] = []
    units: list[str] = []
    for k in range(nl):
        for f in _fields(lines[i + k], NFIELD_PER_LINE):
            if len(heads) < nfields:
                heads.append((f[:10].strip(), f[10:11].strip()))
    i += nl
    for k in range(nl):
        for f in _fields(lines[i + k], NFIELD_PER_LINE):
            if len(units) < nfields:
                units.append(f.strip())
    i += nl
    cols: list[list[float]] = [[] for _ in range(nfields)]
    while i < len(lines):
        key = lines[i][:10].rstrip()
        if key in ("ENDCOMMON", "ENDDATA"):
            break
        vals: list[str] = []
        for k in range(nl):
            if i + k >= len(lines):
                break
            vals.extend(_fields(lines[i + k], NFIELD_PER_LINE))
        for c in range(nfields):
            cols[c].append(_num(vals[c]) if c < len(vals) else math.nan)
        i += nl
    return Table(heads, units, cols), i


def _paren_balance(s: str) -> int:
    return s.count("(") - s.count(")")


def _parse_bib(lines: list[str], i: int) -> tuple[dict[str, list[BibItem]], int]:
    """Parse BIB lines until ENDBIB; returns keyword → items and the ENDBIB index."""
    bib: dict[str, list[BibItem]] = {}
    keyword = None
    cur_lines: list[tuple[str, str]] = []  # (pointer, content)

    def flush() -> None:
        if keyword is None or not cur_lines:
            return
        items = bib.setdefault(keyword, [])
        # split into items: a new item starts on a line that carries a pointer or
        # whose content starts with "(" while the previous code is balanced.
        groups: list[list[tuple[str, str]]] = []
        for ptr, content in cur_lines:
            starts_new = False
            if not groups:
                starts_new = True
            elif ptr:
                starts_new = True
            elif content.startswith("(") and _paren_balance("".join(c for _, c in groups[-1])) == 0:
                starts_new = True
            if starts_new:
                groups.append([(ptr, content)])
            else:
                groups[-1].append((ptr, content))
        for g in groups:
            ptr = g[0][0]
            joined = ""
            code = ""
            text_parts: list[str] = []
            if g[0][1].startswith("("):
                depth = 0
                done = False
                for _, content in g:
                    if done:
                        text_parts.append(content.strip())
                        continue
                    for j, ch in enumerate(content):
                        if ch == "(":
                            depth += 1
                        elif ch == ")":
                            depth -= 1
                            if depth == 0:
                                joined += content[: j + 1]
                                text_parts.append(content[j + 1 :].strip())
                                done = True
                                break
                    if not done:
                        joined += content.rstrip()
                code = joined if done else ""
                if not done:
                    text_parts = [c.strip() for _, c in g]
            else:
                text_parts = [c.strip() for _, c in g]
            items.append(BibItem(ptr, code, " ".join(t for t in text_parts if t)))

    while i < len(lines):
        line = lines[i]
        key = line[:10].rstrip()
        if key == "ENDBIB":
            flush()
            return bib, i
        ptr = line[10:11].strip()
        content = line[11:66].rstrip()
        if key:
            flush()
            keyword = key
            cur_lines = [(ptr, content)]
        else:
            cur_lines.append((ptr, content))
        i += 1
    flush()
    return bib, i


def parse_entry(text: str) -> Entry:
    """Parse one X4 entry file (all its subentries)."""
    lines = text.splitlines()
    entry_id = ""
    entry = None
    sub: Subentry | None = None
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        key = line[:10].rstrip()
        if key == "ENTRY":
            entry_id = line[11:22].strip()
            entry = Entry(entry_id)
        elif key == "SUBENT":
            sub = Subentry(line[11:22].strip())
            if entry is None:
                entry = Entry(sub.accession[:5])
            entry.subentries.append(sub)
        elif key == "BIB" and sub is not None:
            sub.bib, i = _parse_bib(lines, i + 1)
        elif key in ("COMMON", "DATA") and sub is not None:
            nfields = int(line[11:22])
            table, i = _parse_table(lines, i + 1, nfields)
            if key == "COMMON":
                sub.common = table
            else:
                sub.data = table
        elif key == "NODATA" and sub is not None:
            sub.nodata = True
        i += 1
    if entry is None:
        entry = Entry(entry_id)
    return entry


# =========================================================================== zip streaming


def iter_entry_texts(
    zip_path: Path, names: Iterable[str] | None = None
) -> Iterator[tuple[str, str]]:
    with zipfile.ZipFile(zip_path) as z:
        for name in names if names is not None else z.namelist():
            if not name.endswith(".txt"):
                continue
            yield name, z.read(name).decode("latin-1")


def _rss_mb() -> float:
    try:
        with open("/proc/self/status") as f:
            for line in f:
                if line.startswith("VmRSS:"):
                    return int(line.split()[1]) / 1024.0
    except OSError:
        pass
    import resource

    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0


def _peak_rss_mb() -> float:
    try:
        with open("/proc/self/status") as f:
            for line in f:
                if line.startswith("VmHWM:"):
                    return int(line.split()[1]) / 1024.0
    except OSError:
        pass
    return _rss_mb()


# =========================================================================== BIB helpers

_YEAR_RE = re.compile(r"(19|20)\d{2}")
_DOI_RE = re.compile(r"#doi:\s*(\S+)", re.IGNORECASE)


def _first_code(items: list[BibItem] | None, pointer: str = "") -> str | None:
    if not items:
        return None
    for it in items:
        if it.pointer == pointer and it.code:
            return it.code
    for it in items:
        if not it.pointer and it.code:
            return it.code
    return None


def _year_from_reference(items: list[BibItem] | None) -> int | None:
    if not items:
        return None
    for it in items:
        if not it.code:
            continue
        last = it.code.strip("()").split(",")[-1].strip()
        y = _year_from_field(last)
        if y is not None:
            return y
        m2 = _YEAR_RE.search(it.code)
        if m2:
            return int(m2[0])
    return None


def _year_from_field(field_: str) -> int | None:
    """EXFOR reference dates: YYYYMMDD, YYYYMM, YYYY, YYMM or YY (two-digit = 19xx/20xx)."""
    if not field_.isdigit():
        return None
    n = len(field_)
    if n == 8 or (n in (4, 6) and field_[:2] in ("19", "20")):
        return int(field_[:4])
    if n in (2, 4, 6):  # YY, YYMM or YYMMDD
        yy = int(field_[:2])
        return 1900 + yy if yy >= 30 else 2000 + yy
    return None


def _doi(items: list[BibItem] | None) -> str | None:
    if not items:
        return None
    for it in items:
        m = _DOI_RE.search(it.text) or _DOI_RE.search(it.code)
        if m:
            return m[1].rstrip(".,;")
    return None


def _first_author(items: list[BibItem] | None) -> str | None:
    code = _first_code(items)
    if not code:
        return None
    return code.strip("()").split(",")[0].strip() or None


def _facility(items: list[BibItem] | None) -> str | None:
    code = _first_code(items)
    if not code:
        return None
    return code.strip("()").split(",")[0].strip() or None


def _status_flags(*item_lists: list[BibItem] | None) -> set[str]:
    flags: set[str] = set()
    for items in item_lists:
        if not items:
            continue
        for it in items:
            for m in re.findall(r"\(([A-Z]+)[,)]", it.code + " " + it.text):
                flags.add(m)
    return flags


_OUTDATED_FLAGS = {"SPSDD", "OUTDT"}


# =========================================================================== columns


@dataclass
class Column:
    name: str
    pointer: str
    unit: str
    values: np.ndarray
    origin: str = "DATA"  # "DATA" (per point) or "COMMON" (a constant broadcast to nrows)

    def sliced(self, sel: np.ndarray) -> Column:
        return Column(self.name, self.pointer, self.unit, self.values[sel], self.origin)


def _merged_columns(sub: Subentry, common001: Table | None) -> list[Column] | None:
    """DATA columns plus COMMON (subentry and entry-level) constants broadcast to nrows."""
    if sub.data is None or sub.data.nrows == 0:
        return None
    nrows = sub.data.nrows
    cols: list[Column] = []
    for (name, ptr), unit, vals in zip(
        sub.data.headings, sub.data.units, sub.data.columns, strict=True
    ):
        cols.append(Column(name, ptr, unit, np.asarray(vals, dtype=np.float64)))
    present = {(c.name, c.pointer) for c in cols}
    for tbl in (sub.common, common001):
        if tbl is None or tbl.nrows == 0:
            continue
        for (name, ptr), unit, vals in zip(tbl.headings, tbl.units, tbl.columns, strict=True):
            if (name, ptr) in present:
                continue
            present.add((name, ptr))
            cols.append(
                Column(name, ptr, unit, np.full(nrows, vals[0], dtype=np.float64), "COMMON")
            )
    return cols


def _pick(cols: list[Column], names: Iterable[str], pointer: str) -> Column | None:
    by = {(c.name, c.pointer): c for c in cols}
    for nm in names:
        c = by.get((nm, pointer)) if pointer else None
        if c is None:
            c = by.get((nm, ""))
        if c is not None:
            return c
    return None


def _to_abs_sigma(err: Column | None, ref_values: np.ndarray, ref_unit: str) -> np.ndarray | None:
    """Uncertainty column → absolute σ in the *reference* (original) unit, or None."""
    if err is None:
        return None
    info = parse_unit(err.unit)
    if info.canonical == "%":
        return np.abs(err.values) / 100.0 * np.abs(ref_values)
    ref = parse_unit(ref_unit)
    if info.known and ref.known and info.canonical == ref.canonical and ref.factor:
        return np.abs(err.values) * (info.factor / ref.factor)
    if err.unit.strip().upper() == ref_unit.strip().upper():
        return np.abs(err.values)
    return None


_ENERGY_PRIMARY = (
    "EN",
    "EN-RES",
    "KT",
    "KT-K",
    "EN-MEAN",
    "EN-APRX",
    "EN-DUMMY",
    "KT-DUMMY",
    "EN-CM",
    "EN-RES-CM",
    "EN-NM",  # numerator energy of a ratio at two energies
    "EN-MEAN-NM",
)
_PROJECTILE_A = {"N": 1, "P": 1, "D": 2, "T": 3, "HE3": 3, "A": 4, "G": 0, "E": 0}
_MASS_MEV = {"N": 939.565, "P": 938.272}


def _projectile_a(rx: ParsedReaction) -> int | None:
    sf2 = (rx.sf.sf2 or "").upper()
    if sf2 in _PROJECTILE_A:
        return _PROJECTILE_A[sf2] or None
    m = re.match(r"^\d{1,3}-[A-Z]{1,2}-(\d{1,3})", sf2)
    return int(m[1]) if m and int(m[1]) > 0 else None


def _col_to_ev(c: Column, rx: ParsedReaction) -> np.ndarray | None:
    """Energy column → eV; handles MeV/nucleon by multiplying with the projectile A."""
    info = parse_unit(c.unit)
    if info.canonical == "eV":
        return c.values * info.factor
    if info.canonical == "eV/A":
        a = _projectile_a(rx)
        if a:
            return c.values * info.factor * a
    return None


_ENERGY_SIGMA = ("EN-ERR", "EN-RSL", "EN-RSL-HW", "EN-RES-ERR", "EN-ERR-DIG", "KT-ERR")
_DATA_NAMES = ("DATA", "DATA-CM", "DATA-APRX")
_ANGLE = ("ANG", "ANG-CM", "ANG-MEAN")
_COS = ("COS", "COS-CM")
_SECONDARY = ("E", "E-CM", "E-LVL", "E-EXC", "E-MEAN")


def _energy(
    cols: list[Column],
    ptr: str,
    rx: ParsedReaction,
    resonance_energy: np.ndarray | None = None,
) -> tuple[np.ndarray, np.ndarray | None, str] | None:
    c = _pick(cols, _ENERGY_PRIMARY, ptr)
    sig: np.ndarray | None = None
    if c is None:
        if resonance_energy is not None:
            # sibling pointer carries the resonance energy: (N,0),,EN in DATA 1
            return resonance_energy, None, "DATA(EN pointer)"
        lo = _pick(cols, ("EN-MIN", "EN-RES-MIN", "EN-CM-MIN", "EN-MIN-NM"), ptr)
        hi = _pick(cols, ("EN-MAX", "EN-RES-MAX", "EN-CM-MAX", "EN-MAX-NM"), ptr)
        lo_ev = _col_to_ev(lo, rx) if lo is not None else None
        hi_ev = _col_to_ev(hi, rx) if hi is not None else None
        if lo_ev is not None and hi_ev is not None:
            return 0.5 * (lo_ev + hi_ev), 0.5 * np.abs(hi_ev - lo_ev), "EN-MIN/EN-MAX"
        if hi_ev is not None:
            return hi_ev, None, "EN-MAX"
        if (rx.sf.sf6 or "").upper() == "EN":  # resonance energies: DATA is the energy
            d = _pick(cols, _DATA_NAMES, ptr)
            if d is not None and parse_unit(d.unit).canonical == "eV":
                return d.values * parse_unit(d.unit).factor, None, "DATA"
        if lo_ev is not None and (rx.sf.sf6 or "").upper() in ("RI", "SIG"):
            # resonance integral / epithermal data with only a lower cutoff: energy = cutoff
            return lo_ev, None, "EN-MIN"
        mom = _pick(cols, ("MOM",), ptr)
        mass = _MASS_MEV.get((rx.sf.sf2 or "").upper())
        if mom is None:
            mlo = _pick(cols, ("MOM-MIN",), ptr)
            mhi = _pick(cols, ("MOM-MAX",), ptr)
            if mlo is not None and mhi is not None and mlo.unit == mhi.unit:
                mom = Column("MOM", ptr, mlo.unit, 0.5 * (mlo.values + mhi.values))
        if mom is not None and mass is not None:
            munit = mom.unit.strip().upper()
            pc_mev = {"MEV/C": 1.0, "GEV/C": 1e3, "KEV/C": 1e-3}.get(munit)
            if pc_mev is not None:  # relativistic kinetic energy from momentum
                pc = mom.values * pc_mev
                return (np.sqrt(pc**2 + mass**2) - mass) * 1e6, None, "MOM"
        if (rx.sf.sf8 or "").upper().startswith("MXW") and rx.quantity == QuantityType.INTEGRAL:
            return np.full(len(cols[0].values), 0.0253), None, "thermal-implicit"
        if (rx.sf.sf3 or "").upper() == "THS":  # thermal scattering lengths / cross sections
            return np.full(len(cols[0].values), 0.0253), None, "thermal-implicit"
        if (rx.sf.sf2 or "") == "0":
            # target property / spontaneous fission: no incident energy
            return np.zeros(len(cols[0].values)), None, "none"
        return None
    e = _col_to_ev(c, rx)
    if e is None:
        return None
    s = _pick(cols, _ENERGY_SIGMA, ptr)
    if s is None:
        fw = _pick(cols, ("EN-RSL-FW",), ptr)
        if fw is not None:
            s = Column(fw.name, fw.pointer, fw.unit, fw.values / 2.0)
    if s is not None:
        sinfo = parse_unit(s.unit)
        if sinfo.canonical == "%":
            sig = np.abs(s.values) / 100.0 * np.abs(e)
        else:
            sev = _col_to_ev(s, rx)
            sig = np.abs(sev) if sev is not None else None
    return e, sig, c.name


def _angle(cols: list[Column], ptr: str) -> np.ndarray | None:
    c = _pick(cols, _ANGLE, ptr)
    if c is not None:
        info = parse_unit(c.unit)
        if info.canonical == "deg":
            return c.values * info.factor
        return None
    c = _pick(cols, _COS, ptr)
    if c is not None:
        with np.errstate(invalid="ignore"):
            return np.degrees(np.arccos(np.clip(c.values, -1.0, 1.0)))
    return None


def _secondary(cols: list[Column], ptr: str) -> np.ndarray | None:
    c = _pick(cols, _SECONDARY, ptr)
    if c is None:
        lo = _pick(cols, ("E-MIN",), ptr)
        hi = _pick(cols, ("E-MAX",), ptr)
        if lo is None or hi is None:
            return None
        li, hi_ = parse_unit(lo.unit), parse_unit(hi.unit)
        if li.canonical != "eV" or hi_.canonical != "eV":
            return None
        return 0.5 * (lo.values * li.factor + hi.values * hi_.factor)
    info = parse_unit(c.unit)
    if info.canonical != "eV":
        return None
    return c.values * info.factor


# =========================================================================== measurements


class SkipSubentry(Exception):
    """Subentry produced no measurement; ``reason`` is a short category string."""

    def __init__(self, reason: str, detail: str = ""):
        super().__init__(reason)
        self.reason = reason
        self.detail = detail


def _reaction_items(sub: Subentry) -> list[BibItem]:
    items = [it for it in sub.bib.get("REACTION", []) if it.code]
    return items


def _monitor_flag(code: str) -> tuple[str | None, str]:
    """``"((MONIT1)79-AU-197(N,G)79-AU-198,,SIG)"`` → ``("MONIT1", "(79-AU-197(N,G)...,,SIG)")``;
    an unflagged code comes back as ``(None, code)``."""
    m = _MONIT_FLAG_RE.match(code.strip())
    if m is None:
        return None, code.strip()
    return m[1].upper(), "(" + m[2].strip() + ")"


def _items_for_pointer(items: list[BibItem] | None, ptr: str) -> list[BibItem]:
    """Same precedence as :func:`_first_code`: the pointer's own items, else unpointered."""
    if not items:
        return []
    own = [it for it in items if it.code and it.pointer == ptr] if ptr else []
    if own:
        return own
    return [it for it in items if it.code and not it.pointer]


class _Reject(Exception):
    def __init__(self, reason: str, factor: float | None = None):
        super().__init__(reason)
        self.reason = reason
        self.factor = factor


def _match_monitor(
    monitor_items: list[BibItem],
    monit_ref_items: list[BibItem],
    cols: list[Column],
    ptr: str,
) -> tuple[Column, str]:
    """The MONIT column and the *one* MONITOR reaction it belongs to.

    Raises :class:`_Reject` with ``monitor_no_assumed_value`` when there is no MONIT
    column and ``monitor_reaction_ambiguous`` when the column cannot be tied to a
    single reaction.
    """
    flagged: dict[str, str] = {}
    unflagged: list[str] = []
    for it in monitor_items:
        flag, code = _monitor_flag(it.code)
        if flag is not None:
            flagged[flag] = code
        else:
            unflagged.append(code)
    ref_flags = {_monitor_flag(it.code)[0] for it in monit_ref_items if it.code}
    ref_flags.discard(None)
    found = False
    for heading in _MONIT_HEADINGS:
        col = _pick(cols, (heading,), ptr)
        if col is None:
            continue
        found = True
        if heading in flagged:
            return col, flagged[heading]
        if flagged:
            raise _Reject(f"monitor_reaction_ambiguous:{heading} has no ({heading}) flag")
        if heading in ref_flags:
            # the assumed value comes from a MONIT-REF measurement (e.g. the same
            # reaction measured elsewhere), not from the MONITOR reaction
            raise _Reject(f"monitor_reaction_ambiguous:({heading}) flag only in MONIT-REF")
        if len(unflagged) == 1:
            return col, unflagged[0]
        if not unflagged:
            raise _Reject("monitor_reaction_ambiguous:no MONITOR reaction")
        stds = {
            s.name for s in (std_mod.standard_for_reaction(c) for c in unflagged) if s is not None
        }
        if len(stds) == 1 and all(std_mod.standard_for_reaction(c) is not None for c in unflagged):
            return col, unflagged[0]
        raise _Reject(f"monitor_reaction_ambiguous:{len(unflagged)} unflagged MONITOR items")
    if not found:
        raise _Reject("monitor_no_assumed_value")
    raise _Reject("monitor_reaction_ambiguous")  # pragma: no cover - defensive


def _monitor_energy(
    rx: ParsedReaction,
    mon_col: Column,
    cols: list[Column],
    ptr: str,
    energy_ev: np.ndarray,
    std: std_mod.Standard,
) -> tuple[np.ndarray, str]:
    """Energies at which the MONIT values hold, and where that knowledge comes from."""
    en_nrm = _pick(cols, ("EN-NRM",), ptr)
    if en_nrm is not None:
        e = _col_to_ev(en_nrm, rx)
        if e is None:
            raise _Reject("monitor_energy_ambiguous:EN-NRM unit")
        return e, "EN-NRM"
    finite = energy_ev[np.isfinite(energy_ev)]
    single = finite.size > 0 and np.allclose(finite, finite[0], rtol=1e-9, atol=0.0)
    if mon_col.origin == "DATA" or single:
        source = "DATA" if mon_col.origin == "DATA" else "single-energy"
    else:
        # a constant assumed value under a multi-energy table: fine only when the
        # Standard is flat over the table, i.e. the normalization energy is immaterial
        sig = std_mod.load_standards().evaluate(std, energy_ev)
        ok = np.isfinite(sig) & (sig > 0)
        if not ok.any():
            raise _Reject("monitor_energy_out_of_range")
        spread = float(sig[ok].max() / sig[ok].min()) - 1.0
        if not ok.all() or spread > RENORM_FLAT_STANDARD_TOL:
            raise _Reject(f"monitor_energy_ambiguous:constant MONIT, standard varies {spread:.0%}")
        source = "flat-standard"
    sf8 = {m for m in (rx.sf.sf8 or "").upper().split("/") if m}
    if sf8 & _SPECTRUM_SF8:
        thermal = np.abs(energy_ev / _THERMAL_EV - 1.0) <= 0.02
        if not thermal.all():
            raise _Reject(f"monitor_spectrum_averaged:{'/'.join(sorted(sf8 & _SPECTRUM_SF8))}")
    return energy_ev, source


def _renormalize(
    rx: ParsedReaction,
    monitor_items: list[BibItem],
    monit_ref_items: list[BibItem],
    energy_ev: np.ndarray,
    values_orig: np.ndarray,
    stat_orig: np.ndarray | None,
    sys_orig: np.ndarray | None,
    unit: str,
    cols: list[Column],
    ptr: str,
    stats: Counter,
    band: tuple[float, float] = RENORM_BAND,
) -> tuple[DataBlock | None, RenormInfo]:
    """Canonical-unit block, with a Standards-2017 conversion where it is unambiguous.

    Returns the block (``None`` when the values cannot be expressed in canonical
    units) and the :class:`RenormInfo` audit record. The MONIT rules are spelled
    out in the module docstring; every outcome increments ``stats["renorm:<reason>"]``.
    """
    info = parse_unit(unit)
    canon_vals: np.ndarray | None = None
    canon_unit = ""
    if info.convertible and info.canonical not in ("1", "%"):
        canon_vals = values_orig * info.factor
        canon_unit = info.canonical
        f = info.factor
    elif info.canonical == "1":
        canon_vals = values_orig.copy()
        canon_unit = "1"
        f = 1.0
    else:
        stats["renorm:unit_unconvertible"] += 1
        return None, RenormInfo(reason="unit_unconvertible")
    stat = stat_orig * f if stat_orig is not None else None
    sys_ = sys_orig * f if sys_orig is not None else None
    version = "units-only"
    ri = RenormInfo()

    # (a) ratio to a standard → absolute cross section in barns
    if rx.is_ratio and rx.operator == "/" and canon_unit == "1":
        den = rx.denominator
        res = std_mod.ratio_to_absolute(canon_vals, energy_ev, den) if den is not None else None
        if res is None:
            stats["renorm:ratio_denominator_not_standard"] += 1
            return None, RenormInfo(reason="ratio_denominator_not_standard")
        abs_vals, std = res
        if np.isnan(abs_vals).all():
            stats["renorm:ratio_energy_out_of_range"] += 1
            return None, RenormInfo(reason="ratio_energy_out_of_range", monitor=den.raw)
        sig = std_mod.load_standards().evaluate(std, energy_ev)
        stat = stat * sig if stat is not None else None
        sys_ = sys_ * sig if sys_ is not None else None
        canon_vals, canon_unit, version = abs_vals, "b", std_mod.STANDARDS_VERSION
        stats["renorm:ratio_to_standard"] += 1
        ri = RenormInfo(
            reason="ratio_to_standard",
            monitor=den.raw,
            factor=float(np.nanmedian(sig)) if np.isfinite(sig).any() else None,
        )
    elif canon_unit == "1":
        stats["renorm:dimensionless_unconverted"] += 1
        return None, RenormInfo(reason="dimensionless_unconverted")
    # (b) monitor-relative with the assumed monitor value in a MONIT column
    elif monitor_items and canon_unit == "b":
        try:
            ratio, ri = _monitor_factor(
                rx, monitor_items, monit_ref_items, energy_ev, cols, ptr, band
            )
        except _Reject as rej:
            ri = RenormInfo(reason=rej.reason, factor_rejected=rej.factor)
            ri.monitor = getattr(rej, "monitor", None)
            stats["renorm:" + rej.reason.split(":")[0]] += 1
        else:
            canon_vals = canon_vals * ratio
            stat = stat * ratio if stat is not None else None
            sys_ = sys_ * ratio if sys_ is not None else None
            version = std_mod.STANDARDS_VERSION
            stats["renorm:monitor_to_standard"] += 1
    if version == "units-only":
        stats["renorm:units_only"] += 1
    return (
        DataBlock(
            values=_clean(canon_vals),
            stat_sigma=_clean(stat) if stat is not None else None,
            sys_sigma=_clean(sys_) if sys_ is not None else None,
            units=canon_unit,
            standards_version=version,
        ),
        ri,
    )


def _monitor_factor(
    rx: ParsedReaction,
    monitor_items: list[BibItem],
    monit_ref_items: list[BibItem],
    energy_ev: np.ndarray,
    cols: list[Column],
    ptr: str,
    band: tuple[float, float],
) -> tuple[np.ndarray, RenormInfo]:
    """Per-point factor ``sigma_std2017 / sigma_assumed`` for a MONIT-normalized table,
    or :class:`_Reject` (carrying ``.monitor`` and the would-be ``.factor``)."""
    mon_col, monitor = _match_monitor(monitor_items, monit_ref_items, cols, ptr)
    try:
        try:
            mrx = parse_reaction(monitor)
        except ReactionParseError as e:
            raise _Reject("monitor_not_standard:unparseable") from e
        std = std_mod.standard_for_reaction(mrx)
        if std is None or not std.is_standard:
            raise _Reject("monitor_not_standard")
        if re.search(r"-(M\d?|L\d?)$", (mrx.sf.sf4 or "").upper()):
            # production of a metastable product is not the Standard's total; a "-G"
            # product is (198Au-M is populated at the microbarn level)
            raise _Reject("monitor_not_standard:isomer product")
        minfo = parse_unit(mon_col.unit)
        if minfo.canonical != "b":
            raise _Reject("monitor_unit_not_barn")
        e_mon, _source = _monitor_energy(rx, mon_col, cols, ptr, energy_ev, std)
        assumed = mon_col.values * minfo.factor
        sig = std_mod.load_standards().evaluate(std, e_mon)
        with np.errstate(divide="ignore", invalid="ignore"):
            ratio = np.where(assumed > 0, sig / assumed, np.nan)
        ok = np.isfinite(ratio)
        if not ok.any():
            raise _Reject("monitor_energy_out_of_range")
        med = float(np.median(ratio[ok]))
        if not ok.all():
            raise _Reject(f"monitor_energy_partial_coverage:{int(ok.sum())}/{ok.size} points", med)
        lo, hi = band
        if not (lo <= ratio.min() and ratio.max() <= hi):
            reason = (
                f"factor_out_of_band:median {med:.3g}, range {ratio.min():.3g}-{ratio.max():.3g}"
            )
            k = round(math.log10(med) / 3.0) if med > 0 else 0
            if k != 0 and abs(math.log10(med) - 3 * k) < math.log10(1.03):
                reason += f":unit_slip_1000^{k}"
            raise _Reject(reason, med)
    except _Reject as rej:
        rej.monitor = monitor  # type: ignore[attr-defined]
        raise
    return ratio, RenormInfo(reason="monitor_to_standard", monitor=monitor, factor=med)


def _clean(a: np.ndarray) -> list[float]:
    return [float(x) if math.isfinite(x) else math.nan for x in a.tolist()]


def build_measurements(
    entry: Entry,
    stats: Counter | None = None,
    errors: list[dict[str, Any]] | None = None,
    *,
    renorm_band: tuple[float, float] = RENORM_BAND,
) -> list[ExforMeasurement]:
    """All ``ExforMeasurement`` records of one entry (one per subentry × reaction pointer)."""
    stats = stats if stats is not None else Counter()
    out: list[ExforMeasurement] = []
    if not entry.subentries:
        return out
    first = entry.subentries[0]
    common001 = first.common if first.accession.endswith("001") else None
    ebib = first.bib if first.accession.endswith("001") else {}

    for sub in entry.subentries:
        if sub.accession.endswith("001"):
            continue
        stats["subentries"] += 1
        try:
            recs = _build_sub(entry, sub, ebib, common001, stats, renorm_band)
        except SkipSubentry as e:
            stats[f"skip:{e.reason}"] += 1
            if errors is not None:
                errors.append(
                    {"subentry": sub.accession, "reason": e.reason, "detail": e.detail[:200]}
                )
            continue
        except Exception as e:  # noqa: BLE001 - one bad subentry must not kill the run
            stats["skip:exception"] += 1
            if errors is not None:
                errors.append(
                    {
                        "subentry": sub.accession,
                        "reason": "exception",
                        "detail": f"{type(e).__name__}: {e}"[:200],
                    }
                )
            continue
        if recs:
            stats["subentries_parsed"] += 1
            out.extend(recs)
    return out


def _build_sub(
    entry: Entry,
    sub: Subentry,
    ebib: dict[str, list[BibItem]],
    common001: Table | None,
    stats: Counter,
    renorm_band: tuple[float, float] = RENORM_BAND,
) -> list[ExforMeasurement]:
    if sub.nodata or sub.data is None:
        stats["subentries_nodata"] += 1
        stats["subentries_parsed"] += 1  # counted as handled, not as a failure
        return []
    rx_items = _reaction_items(sub)
    if not rx_items:
        raise SkipSubentry("no_reaction")
    cols = _merged_columns(sub, common001)
    if cols is None:
        stats["subentries_nodata"] += 1
        stats["subentries_parsed"] += 1
        return []

    bib = sub.bib
    year = _year_from_reference(bib.get("REFERENCE") or ebib.get("REFERENCE"))
    doi = _doi(bib.get("REFERENCE")) or _doi(ebib.get("REFERENCE"))
    reference = _first_code(bib.get("REFERENCE") or ebib.get("REFERENCE"))
    first_author = _first_author(bib.get("AUTHOR") or ebib.get("AUTHOR"))
    facility = _facility(bib.get("FACILITY") or ebib.get("FACILITY"))
    detector = _facility(bib.get("DETECTOR") or ebib.get("DETECTOR"))
    flags = _status_flags(bib.get("STATUS"), ebib.get("STATUS"))
    outdated = bool(flags & _OUTDATED_FLAGS)
    monitors = bib.get("MONITOR") or ebib.get("MONITOR")
    monit_refs = bib.get("MONIT-REF") or ebib.get("MONIT-REF") or []

    data_ptrs = {c.pointer for c in cols if c.name in _DATA_NAMES}
    parsed: list[tuple[BibItem, ParsedReaction | None, str]] = []
    for it in rx_items:
        try:
            parsed.append((it, parse_reaction(it.code), ""))
        except ReactionParseError as e:
            parsed.append((it, None, str(e)))
    # resonance tables: pointer whose reaction is ",,EN" holds the energy for its siblings
    res_energy: np.ndarray | None = None
    for it, rx, _ in parsed:
        if (
            rx is not None
            and (rx.sf.sf6 or "").upper() == "EN"
            and _pick(cols, _ENERGY_PRIMARY, it.pointer) is None
        ):
            d = _pick(cols, _DATA_NAMES, it.pointer)
            if d is not None and parse_unit(d.unit).canonical == "eV":
                res_energy = d.values * parse_unit(d.unit).factor
                break
    recs: list[ExforMeasurement] = []
    reasons: list[str] = []
    for it, rx, perr in parsed:
        ptr = it.pointer
        if rx is None:
            reasons.append(f"reaction_parse:{perr}")
            stats["pointer:reaction_parse"] += 1
            continue
        dcol = _pick(cols, _DATA_NAMES, ptr)
        if dcol is None or (ptr and dcol.pointer != ptr and len(rx_items) > 1 and data_ptrs - {""}):
            if _pick(cols, ("DATA-MAX", "DATA-MIN"), ptr) is not None:
                reasons.append(f"limit_only:{ptr or '-'}")  # upper/lower limits only
                stats["pointer:limit_only"] += 1
            else:
                reasons.append(f"no_data_column:{ptr or '-'}")
                stats["pointer:no_data_column"] += 1
            continue
        en = _energy(cols, ptr, rx, res_energy)
        if en is None:
            reasons.append("no_energy_column")
            stats["pointer:no_energy_column"] += 1
            continue
        energy_ev, energy_sig, _src = en
        values = dcol.values
        keep = np.isfinite(values) & np.isfinite(energy_ev)
        if not keep.any():
            reasons.append("no_valid_points")
            stats["pointer:no_valid_points"] += 1
            continue

        err_s = _pick(cols, ("ERR-S",), ptr)
        err_t = _pick(cols, ("ERR-T", "DATA-ERR"), ptr)
        if err_t is None:
            plus = _pick(cols, ("+DATA-ERR", "+ERR-T"), ptr)
            minus = _pick(cols, ("-DATA-ERR", "-ERR-T"), ptr)
            if plus is not None and minus is not None:
                err_t = Column(
                    "DATA-ERR", ptr, plus.unit, 0.5 * (np.abs(plus.values) + np.abs(minus.values))
                )
        err_sys = _pick(cols, ("ERR-SYS",), ptr)
        stat = _to_abs_sigma(err_s, values, dcol.unit)
        if stat is None:
            stat = _to_abs_sigma(err_t, values, dcol.unit)
        sysg = _to_abs_sigma(err_sys, values, dcol.unit)

        angle = _angle(cols, ptr)
        secondary = _secondary(cols, ptr)

        sel = np.flatnonzero(keep)
        e_k = energy_ev[sel]
        v_k = values[sel]
        st_k = stat[sel] if stat is not None else None
        sy_k = sysg[sel] if sysg is not None else None
        st_k = None if st_k is not None and not np.isfinite(st_k).any() else st_k
        sy_k = None if sy_k is not None and not np.isfinite(sy_k).any() else sy_k

        monitor = _first_code(monitors, ptr) if monitors else None
        original = DataBlock(
            values=_clean(v_k),
            stat_sigma=_clean(st_k) if st_k is not None else None,
            sys_sigma=_clean(sy_k) if sy_k is not None else None,
            units=dcol.unit.strip() or "NO-DIM",
        )
        renorm, rinfo = _renormalize(
            rx,
            _items_for_pointer(monitors, ptr),
            _items_for_pointer(monit_refs, ptr),
            e_k,
            v_k,
            st_k,
            sy_k,
            dcol.unit,
            [c.sliced(sel) for c in cols],
            ptr,
            stats,
            renorm_band,
        )

        recs.append(
            ExforMeasurement(
                entry=entry.entry,
                subentry=sub.accession,
                pointer=ptr or None,
                target_z=rx.target.z,
                target_a=rx.target.a,
                target_iso=rx.target.iso,
                projectile=rx.projectile,
                reaction=it.code,
                sf=ReactionSF(**rx.sf.model_dump()),
                mt=rx.mt,
                quantity=rx.quantity,
                energy_ev=_clean(e_k),
                energy_sigma_ev=_clean(energy_sig[sel]) if energy_sig is not None else None,
                angle_deg=_clean(angle[sel]) if angle is not None else None,
                secondary_energy_ev=_clean(secondary[sel]) if secondary is not None else None,
                original=original,
                renormalized=renorm,
                monitor=monitor,
                year=year,
                facility=facility,
                detector=detector,
                first_author=first_author,
                reference=reference,
                doi=doi,
                outdated=outdated,
                exfor_version=EXFOR_VERSION,
                renorm_factor=rinfo.factor,
                renorm_monitor=rinfo.monitor,
                renorm_reason=rinfo.reason,
                renorm_factor_rejected=rinfo.factor_rejected,
            )
        )
    if not recs:
        raise SkipSubentry(
            reasons[0].split(":")[0] if reasons else "no_measurement", "; ".join(reasons)
        )
    return recs


# =========================================================================== subsets

# WP-19: EXFOR SF3 code of each non-capture channel subset (n2n keeps its own filter above).
CHANNEL_SF3: dict[str, str] = {
    "np": "P",
    "na": "A",
    "inelastic": "INL",
    "elastic": "EL",
    "total": "TOT",
}


def _subset_filter(subset: str, zmin: int, zmax: int):
    def capture(m: Measurement) -> bool:
        sf = m.sf
        return (
            (sf.sf2 or "").upper() == "N"
            and (sf.sf3 or "").upper() == "G"
            and (sf.sf6 or "").upper() in ("SIG", "RI")
            and zmin <= m.target_z <= zmax
        )

    def n2n(m: Measurement) -> bool:
        # WP-19. sf3 "2N" is (n,2n); the capture subset's "G" has no equivalent here, and the
        # threshold means RI (resonance integral) is meaningless, so only SIG is taken.
        sf = m.sf
        return (
            (sf.sf2 or "").upper() == "N"
            and (sf.sf3 or "").upper() == "2N"
            and (sf.sf6 or "").upper() == "SIG"
            and zmin <= m.target_z <= zmax
        )

    def everything(m: Measurement) -> bool:
        return zmin <= m.target_z <= zmax

    def reaction(sf3: str):
        # WP-19 channels. Same shape as n2n: SIG only, because RI is a capture quantity. The
        # residual state (sf4) and branch (sf5) are kept, not filtered: WP-12 curation carries
        # them into the comparable-quantity key and the scorer selects state "" / branch "",
        # so an isomer partial or a PAR level-inelastic is recorded and never scored as a total.
        def keep(m: Measurement) -> bool:
            sf = m.sf
            return (
                (sf.sf2 or "").upper() == "N"
                and (sf.sf3 or "").upper() == sf3
                and (sf.sf6 or "").upper() == "SIG"
                and zmin <= m.target_z <= zmax
            )

        return keep

    if subset in CHANNEL_SF3:
        return reaction(CHANNEL_SF3[subset])

    if subset == "capture":
        return capture
    if subset == "n2n":
        return n2n
    if subset == "all":
        return everything
    raise ValueError(f"unknown subset {subset!r}")


def _clip_energy(m: Measurement, emax_ev: float) -> Measurement | None:
    """Drop points above ``emax_ev`` (capture subset: thermal → 20 MeV)."""
    e = np.asarray(m.energy_ev)
    keep = e <= emax_ev
    if keep.all():
        return m
    if not keep.any():
        return None
    idx = np.flatnonzero(keep)

    def take(lst):
        return None if lst is None else [lst[i] for i in idx]

    def take_block(b: DataBlock | None):
        if b is None:
            return None
        return DataBlock(
            values=take(b.values),
            stat_sigma=take(b.stat_sigma),
            sys_sigma=take(b.sys_sigma),
            units=b.units,
            standards_version=b.standards_version,
        )

    return m.model_copy(
        update={
            "energy_ev": take(m.energy_ev),
            "energy_sigma_ev": take(m.energy_sigma_ev),
            "angle_deg": take(m.angle_deg),
            "secondary_energy_ev": take(m.secondary_energy_ev),
            "original": take_block(m.original),
            "renormalized": take_block(m.renormalized),
        }
    )


# =========================================================================== workers

_WORKER_ZIP: zipfile.ZipFile | None = None


def _worker_init(zip_path: str) -> None:
    global _WORKER_ZIP
    _WORKER_ZIP = zipfile.ZipFile(zip_path)


def _worker(
    args: tuple[list[str], str, int, int, float, tuple[float, float]],
) -> tuple[list[dict], dict, list[dict]]:
    names, subset, zmin, zmax, emax, band = args
    assert _WORKER_ZIP is not None
    keep = _subset_filter(subset, zmin, zmax)
    stats: Counter = Counter()
    errors: list[dict] = []
    rows: list[dict] = []
    for name in names:
        text = _WORKER_ZIP.read(name).decode("latin-1")
        if text.startswith("DICTION"):  # area 9 holds the EXFOR dictionaries, not data
            stats["dictionary_files"] += 1
            continue
        stats["entries"] += 1
        try:
            entry = parse_entry(text)
        except Exception as e:  # noqa: BLE001
            stats["entry_parse_failed"] += 1
            errors.append({"subentry": name, "reason": "entry_parse", "detail": str(e)[:200]})
            continue
        for m in build_measurements(entry, stats, errors, renorm_band=band):
            stats["measurements_total"] += 1
            if not keep(m):
                continue
            if emax > 0:
                m2 = _clip_energy(m, emax)
                if m2 is None:
                    stats["measurements_clipped_out"] += 1
                    continue
                m = m2
            rows.append(m.to_row())
        del entry
    if _rss_mb() > WORKER_RSS_LIMIT_MB:
        stats["worker_rss_exceeded"] += 1
    return rows, dict(stats), errors


def _chunks(seq: list[str], size: int) -> Iterator[list[str]]:
    for i in range(0, len(seq), size):
        yield seq[i : i + size]


def run(
    subset: str,
    zmin: int,
    zmax: int,
    out_path: Path,
    *,
    zip_path: Path = RAW_ENTRY_ZIP,
    workers: int = 3,
    chunk_entries: int = 40,
    rowgroup_rows: int = 4000,
    emax_ev: float = 0.0,
    limit: int | None = None,
    errors_path: Path | None = None,
    renorm_band: tuple[float, float] = RENORM_BAND,
) -> dict[str, Any]:
    t0 = time.time()
    with zipfile.ZipFile(zip_path) as z:
        names = [n for n in z.namelist() if n.endswith(".txt")]
    names.sort()
    if limit:
        names = names[:limit]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = out_path.with_suffix(".parquet.tmp")
    errors_path = errors_path or out_path.parent / "exfor_parse_errors.jsonl"
    schema = ExforMeasurement.ARROW_SCHEMA
    writer = pq.ParquetWriter(tmp_path, schema, compression="zstd")
    stats: Counter = Counter()
    buf: list[dict] = []
    n_rows = 0
    n_points = 0
    peak = 0.0
    n_done = 0
    total = len(names)
    band = (float(renorm_band[0]), float(renorm_band[1]))
    tasks = [(c, subset, zmin, zmax, emax_ev, band) for c in _chunks(names, chunk_entries)]

    def flush() -> None:
        nonlocal buf, n_rows
        if not buf:
            return
        table = pa.Table.from_pylist(buf, schema=schema)
        writer.write_table(table)
        n_rows += len(buf)
        buf = []

    try:
        with open(errors_path, "w") as ef:
            ctx = mp.get_context("fork")
            with ctx.Pool(workers, initializer=_worker_init, initargs=(str(zip_path),)) as pool:
                for rows, wstats, errs in pool.imap_unordered(_worker, tasks, chunksize=1):
                    stats.update(wstats)
                    for e in errs:
                        ef.write(json.dumps(e) + "\n")
                    for r in rows:
                        n_points += len(r["energy_ev"])
                    buf.extend(rows)
                    n_done += wstats.get("entries", 0)
                    if len(buf) >= rowgroup_rows:
                        flush()
                    rss = _rss_mb()
                    peak = max(peak, rss)
                    if rss > RSS_LIMIT_MB:
                        raise MemoryError(
                            f"main process RSS {rss:.0f} MB exceeded the {RSS_LIMIT_MB} MB limit "
                            f"after {n_done}/{total} entries; aborting (partial output removed)"
                        )
                    if n_done % 2000 < chunk_entries:
                        el = time.time() - t0
                        print(
                            f"  {n_done}/{total} entries  rows={n_rows + len(buf)}  "
                            f"points={n_points}  rss={rss:.0f}MB  {el:.0f}s",
                            file=sys.stderr,
                            flush=True,
                        )
        flush()
    except BaseException:
        writer.close()
        tmp_path.unlink(missing_ok=True)
        raise
    writer.close()
    os.replace(tmp_path, out_path)
    wall = time.time() - t0
    summary = {
        "subset": subset,
        "zmin": zmin,
        "zmax": zmax,
        "output": str(out_path),
        "exfor_version": EXFOR_VERSION,
        "standards_version": std_mod.STANDARDS_VERSION,
        "renorm_band": list(band),
        "entries": total,
        "measurements_written": n_rows,
        "points_written": n_points,
        "wall_seconds": round(wall, 1),
        "peak_rss_main_mb": round(max(peak, _peak_rss_mb()), 1),
        "stats": dict(sorted(stats.items())),
    }
    sub_total = stats.get("subentries", 0)
    parsed = stats.get("subentries_parsed", 0)
    summary["parse_coverage_pct"] = round(100.0 * parsed / sub_total, 2) if sub_total else None
    (out_path.parent / f"{out_path.stem}_summary.json").write_text(json.dumps(summary, indent=1))
    return summary


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument(
        "--subset", choices=["capture", "n2n", *CHANNEL_SF3, "all"], default="capture"
    )
    ap.add_argument("--zmin", type=int, default=0)
    ap.add_argument("--zmax", type=int, default=999)
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--zip", type=Path, default=RAW_ENTRY_ZIP)
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--limit", type=int, default=None, help="only the first N entries (smoke test)")
    ap.add_argument("--emax-mev", type=float, default=None, help="drop points above this energy")
    ap.add_argument(
        "--renorm-band",
        type=float,
        nargs=2,
        default=list(RENORM_BAND),
        metavar=("LO", "HI"),
        help="MONIT factors outside [LO, HI] are recorded but not applied (default 0.5 2.0)",
    )
    args = ap.parse_args(argv)
    if not (0 < args.renorm_band[0] < 1 <= args.renorm_band[1]):
        ap.error("--renorm-band must satisfy 0 < LO < 1 <= HI")
    if args.out is None:
        if args.subset == "capture":
            args.out = STAGING / f"exfor_capture_Z{args.zmin}-{args.zmax}.parquet"
        elif args.subset == "n2n" or args.subset in CHANNEL_SF3:
            args.out = STAGING / f"exfor_{args.subset}_Z{args.zmin}-{args.zmax}.parquet"
        else:
            suffix = "" if (args.zmin == 0 and args.zmax == 999) else f"_Z{args.zmin}-{args.zmax}"
            args.out = STAGING / f"exfor_all{suffix}.parquet"
    emax = (
        args.emax_mev * 1e6
        if args.emax_mev is not None
        else (20e6 if args.subset in ("capture", "n2n", *CHANNEL_SF3) else 0.0)
    )
    summary = run(
        args.subset,
        args.zmin,
        args.zmax,
        args.out,
        zip_path=args.zip,
        workers=args.workers,
        emax_ev=emax,
        limit=args.limit,
        errors_path=STAGING / "exfor_parse_errors.jsonl",
        renorm_band=(args.renorm_band[0], args.renorm_band[1]),
    )
    print(json.dumps(summary, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
