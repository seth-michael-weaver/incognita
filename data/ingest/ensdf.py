"""WP-10: ENSDF "ADOPTED LEVELS" parser (blueprint §3.1, §4.2 "ENSDF").

Streams the NNDC archive ``raw/ensdf/ensdf_<yymmdd>.zip`` (one member per mass number,
``ensdf.001`` … ``ensdf.300``) without extracting it, keeps only the adopted-levels
datasets, and returns one row per level with:

* ``energy_kev`` (+ σ from the ENSDF "digits" convention, e.g. ``846.7778 19`` → σ =
  0.0019 keV), the unknown-offset tag (``X``, ``Y``, ``SN``, …) when the energy is
  only known relative to an unplaced band head, and the qualifier (``AP``, ``SY``, …);
* the raw Jπ string plus a parsed candidate distribution (``j_values``/``parities``),
  a ``j_tentative`` flag (parentheses anywhere) and ``j_unique`` (exactly one J and a
  firm parity) — never a single forced value;
* half-life in seconds (widths in eV/keV/MeV converted through ħ ln 2 / Γ and kept as
  ``width_ev``), the ``STABLE`` flag, metastable (``MS``) and questionable (``?``) marks;
* the number of gamma records that follow the level.

Record classification follows the ENSDF manual: column 6 blank = primary record,
otherwise a continuation record; column 7 in ``cCdDtT`` = comment; column 8 = record
type (``L`` level, ``G`` gamma, ``Q`` Q-value, ``H`` history, ``N`` normalization …).
Decay datasets (``DSID`` containing ``DECAY``) and reaction datasets are skipped.

Level-count helpers (:func:`level_counts`) give N(E) per nuclide, the count below the
RIPL completeness cutoff ``Umax`` (for the comparison with RIPL's ``Nmax``) and the
spin cutoff extracted from the uniquely assigned spins below the cutoff (WP-14).
"""

from __future__ import annotations

import logging
import re
import zipfile
from collections import Counter
from collections.abc import Iterable, Iterator
from decimal import Decimal, InvalidOperation
from pathlib import Path

import polars as pl

from data.ingest.ripl import symbol_to_z
from data.schema.keys import nuclide_id

log = logging.getLogger(__name__)

REPO = Path(__file__).resolve().parents[2]
ENSDF_ZIP = REPO / "raw" / "ensdf" / "ensdf_260901.zip"
ENSDF_VERSION = "ENSDF 2026-09-01"

__all__ = [
    "ENSDF_VERSION",
    "ENSDF_ZIP",
    "LEVEL_SCHEMA",
    "UNPARSED_JPI",
    "cumulative_levels",
    "iter_adopted_datasets",
    "level_counts",
    "parse_adopted_levels",
    "parse_energy",
    "parse_half_life",
    "parse_jpi",
    "read_adopted_levels",
]

HBAR_LN2_EV_S = 6.582119569e-16 * 0.6931471805599453  # ħ ln2 in eV·s
_SECONDS = {
    "Y": 365.25 * 86400.0, "D": 86400.0, "H": 3600.0, "M": 60.0, "MIN": 60.0, "S": 1.0,
    "MS": 1e-3, "US": 1e-6, "NS": 1e-9, "PS": 1e-12, "FS": 1e-15, "AS": 1e-18,
}  # fmt: skip
_WIDTH_EV = {"EV": 1.0, "KEV": 1e3, "MEV": 1e6}
_QUALIFIERS = {"AP", "SY", "CA", "GE", "GT", "LE", "LT", "?"}

UNPARSED_JPI: Counter[str] = Counter()
"""Jπ strings the grammar could not decompose (kept raw in the table); for review."""


# --------------------------------------------------------------------------- field parsers


def _digits_sigma(value_str: str, unc_str: str) -> float | None:
    """ENSDF uncertainty convention: ``unc`` counts units of the last digit of ``value``."""
    try:
        exp = Decimal(value_str.strip()).as_tuple().exponent
        return float(int(unc_str)) * float(10) ** int(exp)
    except (InvalidOperation, ValueError):
        return None


_E_RE = re.compile(r"^(?:([A-Z]{1,2})\+)?([0-9.]+(?:E[+-]?\d+)?)?(?:\+([A-Z]{1,2}))?$", re.I)


def parse_energy(
    e_field: str, de_field: str
) -> tuple[float | None, float | None, str | None, str | None]:
    """``(energy_kev, sigma_kev, offset, qualifier)``.

    ``"846.7778", "19"`` → (846.7778, 0.0019, None, None); ``"1234+X", ""`` → (1234.0,
    None, "X", None); ``"X", ""`` → (None, None, "X", None); ``"2500", "AP"`` →
    (2500.0, None, None, "AP").
    """
    s = re.sub(r"\s+", "", e_field.upper())  # "881.6 +X" occurs once in the archive
    if re.fullmatch(r"[A-Z]{1,2}", s):  # bare "X" / "Y" / "SN": offset only
        return None, None, s, None
    m = _E_RE.match(s)
    if not m or (m[2] is None and m[1] is None and m[3] is None):
        if s:
            log.warning("ENSDF: unparsed level energy %r", e_field)
        return None, None, None, None
    offset = m[1] or m[3]
    energy = float(m[2]) if m[2] else None
    de = de_field.strip().upper()
    sigma = qual = None
    if de:
        if de in _QUALIFIERS:
            qual = de
        elif m[2]:
            sigma = _digits_sigma(m[2], de)
    return energy, sigma, offset, qual


_T_RE = re.compile(r"^([0-9.]+(?:E[+-]?\d+)?)\s*([A-Z]+)\s*(\?)?$", re.I)
_DT_ASYM = re.compile(r"^\+(\d+)\s*-(\d+)$|^-(\d+)\s*\+(\d+)$")


def parse_half_life(t_field: str, dt_field: str) -> dict:
    """Half-life field → ``half_life_s``, ``half_life_sigma_s``, ``half_life_qualifier``,
    ``width_ev``, ``is_stable``. Widths (eV/keV/MeV) are converted via ħ ln2 / Γ."""
    out = {
        "half_life_s": None, "half_life_sigma_s": None, "half_life_qualifier": None,
        "width_ev": None, "is_stable": False,
    }  # fmt: skip
    s = t_field.strip().upper()
    if not s:
        return out
    if s == "STABLE":
        out["is_stable"] = True
        return out
    m = _T_RE.match(s)
    if not m:
        return out
    val_str, unit = m[1], m[2].upper()
    if m[3]:
        out["half_life_qualifier"] = "?"
    dt = dt_field.strip().upper()
    sig = None
    if dt:
        if dt in _QUALIFIERS:
            out["half_life_qualifier"] = dt
        else:
            ma = _DT_ASYM.match(dt)
            if ma:
                digs = [int(x) for x in ma.groups() if x is not None]
                sig = _digits_sigma(val_str, str(max(digs)))
            elif dt.isdigit():
                sig = _digits_sigma(val_str, dt)
    val = float(val_str)
    if unit in _WIDTH_EV:
        width = val * _WIDTH_EV[unit]
        out["width_ev"] = width
        if width > 0:
            out["half_life_s"] = HBAR_LN2_EV_S / width
            if sig:
                out["half_life_sigma_s"] = HBAR_LN2_EV_S / width * (sig * _WIDTH_EV[unit] / width)
    elif unit in _SECONDS:
        out["half_life_s"] = val * _SECONDS[unit]
        if sig is not None:
            out["half_life_sigma_s"] = sig * _SECONDS[unit]
    return out


_J_ITEM = re.compile(r"^(\d+(?:/2)?)$")
_J_RANGE = re.compile(r"^(\d+(?:/2)?)([+-]?)(?::|TO)(\d+(?:/2)?)([+-]?)$", re.I)
_J_PAR = re.compile(r"^(.*?)\s*(\(?[+-]\)?)$")
_J_LIMIT = re.compile(r"^(GE|GT|LE|LT|AP|NOT|>|<|>=|<=)")


def _jval(s: str) -> float:
    return float(s[:-2]) / 2 if s.endswith("/2") else float(s)


def _strip_parens(s: str) -> tuple[str, bool]:
    s = s.strip()
    if s.startswith("(") and s.endswith(")"):
        depth = 0
        for i, ch in enumerate(s):
            depth += ch == "("
            depth -= ch == ")"
            if depth == 0 and i < len(s) - 1:
                return s, False  # e.g. "(1)+" or "(1,2)+(3)" — not fully enclosed
        return s[1:-1].strip(), True
    return s, False


def parse_jpi(raw: str) -> tuple[list[float], list[int], bool, bool]:
    """Jπ string → ``(j_values, parities, tentative, unique)``.

    Handles ``3/2+``, ``(2+)``, ``1/2-,3/2-``, ``(1,2)+``, ``3/2(+)``, ``1:4``,
    ``1 TO 3``, ``+`` (parity only), ``GE 2`` / ``LE 3`` (kept as unknown J), ``J``.
    ``parities`` is aligned with ``j_values`` (0 = unknown). Unparsed strings are
    counted in :data:`UNPARSED_JPI` and return empty lists.
    """
    s = raw.strip().upper()
    if not s:
        return [], [], False, False
    tentative = "(" in s or "[" in s
    s = s.replace(" ", "").replace("[", "(").replace("]", ")").replace("&", ",")
    # Rotational-band bookkeeping ("J", "J1+2", "J+4", "J1 AP (18)"): symbolic, no
    # numeric spin to extract; treat as unknown J without flagging it unparsed.
    if re.match(r"^\(?J\d*(\+\d+)?\)?(AP\(.*\))?$", s):
        return [], [], tentative, False
    inner, _ = _strip_parens(s)
    global_par = 0
    # "(1,2)+" / "(1,2)-" / "(0:4)(+)": group parity applies to every member
    m = re.match(r"^\((.*)\)\(?([+-])\)?$", s)
    if m and "(" not in m[1]:
        inner, global_par = m[1], (1 if m[2] == "+" else -1)
    js: list[float] = []
    ps: list[int] = []
    ok = True
    for item in inner.split(","):
        item, _ = _strip_parens(item)
        if not item:
            continue
        par = global_par
        mr = _J_RANGE.match(item)
        if mr:  # "1:4", "1TO3", "1-TO4-", "0+TO4+"
            if mr[2] or mr[4]:
                par = 1 if "+" in (mr[2] + mr[4]) else -1
            lo, hi = _jval(mr[1]), _jval(mr[3])
            j = lo
            while j <= hi + 1e-9:
                js.append(j)
                ps.append(par)
                j += 1.0
            continue
        mp = _J_PAR.match(item)
        if mp and mp[2]:
            par = 1 if "+" in mp[2] else -1
            item, _ = _strip_parens(mp[1])  # "(3)+" → "3"
        if not item:  # parity only, J unknown
            if not js:
                ps.append(par)
            continue
        if _J_LIMIT.match(item) or item in {"J", "NATURAL", "UNNATURAL"}:
            continue  # a bound or an unknown J: no candidates, raw string kept
        mi = _J_ITEM.match(item)
        if mi:
            js.append(_jval(mi[1]))
            ps.append(par)
            continue
        ok = False
    if not ok:
        UNPARSED_JPI[raw.strip()] += 1
        return [], [], tentative, False
    if not js:
        ps = ps[:1]
    unique = len(js) == 1 and ps[0] != 0 and not tentative
    return js, ps, tentative, unique


# --------------------------------------------------------------------------- datasets

_NUCID_RE = re.compile(r"^\s*(\d{1,3})([A-Za-z]{1,2}|\d{2,3})\s*$")


def _nucid(nucid: str) -> tuple[int, int] | None:
    m = _NUCID_RE.match(nucid)
    if not m:
        return None
    A = int(m[1])
    try:
        Z = symbol_to_z(m[2])
    except ValueError:
        return None
    if m[2].upper() == "NN":
        Z = 0
    return Z, A


def iter_adopted_datasets(
    zip_path: Path = ENSDF_ZIP, members: Iterable[str] | None = None
) -> Iterator[tuple[str, str, list[str]]]:
    """Yield ``(nucid, dsid, lines)`` for every ADOPTED LEVELS dataset, streaming the zip
    one member at a time and buffering only the dataset being read."""
    with zipfile.ZipFile(zip_path) as zf:
        names = list(members) if members is not None else zf.namelist()
        for name in names:
            buf: list[str] = []
            keep = False
            nucid = dsid = ""
            with zf.open(name) as fh:
                for raw in fh:
                    line = raw.decode("latin-1").rstrip("\r\n")
                    if not line.strip():
                        if keep and buf:
                            yield nucid, dsid, buf
                        buf, keep = [], False
                        continue
                    if not buf:  # identification record
                        nucid, dsid = line[:5], line[9:39].strip()
                        keep = dsid.startswith("ADOPTED LEVELS")
                    if keep:
                        buf.append(line)
            if keep and buf:
                yield nucid, dsid, buf


LEVEL_SCHEMA: dict[str, pl.DataType | type] = {
    "nuclide_id": pl.String, "Z": pl.Int16, "N": pl.Int16, "A": pl.Int16,
    "level_index": pl.Int32, "energy_kev": pl.Float64, "energy_sigma_kev": pl.Float64,
    "energy_offset": pl.String, "energy_qualifier": pl.String, "jpi_raw": pl.String,
    "j_values": pl.List(pl.Float64), "parities": pl.List(pl.Int8), "j_tentative": pl.Boolean,
    "j_unique": pl.Boolean, "half_life_raw": pl.String, "half_life_s": pl.Float64,
    "half_life_sigma_s": pl.Float64, "half_life_qualifier": pl.String, "width_ev": pl.Float64,
    "is_stable": pl.Boolean, "metastable": pl.String, "questionable": pl.Boolean,
    "comment_flag": pl.String, "n_gammas": pl.Int16, "n_continuation": pl.Int8,
}  # fmt: skip

DATASET_SCHEMA: dict[str, pl.DataType | type] = {
    "nuclide_id": pl.String, "Z": pl.Int16, "N": pl.Int16, "A": pl.Int16, "dsid": pl.String,
    "date": pl.String, "sn_kev": pl.Float64, "sp_kev": pl.Float64, "n_levels": pl.Int32,
}  # fmt: skip


def _q_record(line: str) -> tuple[float | None, float | None]:
    """Q record: Q(β-) 10-19, DQ 20-21, SN 22-29, DSN 30-31, SP 32-39, DSP 40-41, QA 42-49."""
    def f(a: int, b: int) -> float | None:
        try:
            return float(line[a:b].strip())
        except ValueError:
            return None

    return f(21, 29), f(31, 39)


def parse_adopted_levels(nucid: str, dsid: str, lines: list[str]) -> tuple[dict | None, list[dict]]:
    """One adopted-levels dataset → ``(dataset_row, level_rows)``."""
    key = _nucid(nucid)
    if key is None:
        log.warning("ENSDF: cannot decode NUCID %r (%s)", nucid, dsid)
        return None, []
    Z, A = key
    N = A - Z
    if N < 0 or (Z == 0 and A != 1):
        log.warning("ENSDF: dropped %r — N=%d", nucid, N)
        return None, []
    nid = nuclide_id(Z, N)
    ds = {
        "nuclide_id": nid, "Z": Z, "N": N, "A": A, "dsid": dsid, "date": lines[0][74:80].strip(),
        "sn_kev": None, "sp_kev": None, "n_levels": 0,
    }  # fmt: skip
    levels: list[dict] = []
    cur: dict | None = None
    for line in lines[1:]:
        c6, c7, c8 = line[5:6], line[6:7], line[7:8]
        if c7 in "cCdDtT" and c7 != " ":
            continue  # comment record
        if c8 == "Q" and c6 == " ":
            ds["sn_kev"], ds["sp_kev"] = _q_record(line)
            continue
        if c8 == "L":
            # A continuation record whose column 6 was left blank shows up with "$" or
            # "=" in the energy field ("$B(E1)=0.8"); attach it instead of making a level.
            if c6 == " " and not any(ch in line[9:21] for ch in "$="):
                e, es, off, eq = parse_energy(line[9:19], line[19:21])
                jraw = line[21:39].strip()
                js, ps, tent, uniq = parse_jpi(jraw)
                hl = parse_half_life(line[39:49], line[49:55])
                cur = {
                    "nuclide_id": nid, "Z": Z, "N": N, "A": A, "level_index": len(levels) + 1,
                    "energy_kev": e, "energy_sigma_kev": es, "energy_offset": off,
                    "energy_qualifier": eq, "jpi_raw": jraw, "j_values": js, "parities": ps,
                    "j_tentative": tent, "j_unique": uniq, "half_life_raw": line[39:49].strip(),
                    **hl, "metastable": line[77:79].strip() or None,
                    "questionable": line[79:80] == "?", "comment_flag": line[76:77].strip() or None,
                    "n_gammas": 0, "n_continuation": 0,
                }  # fmt: skip
                levels.append(cur)
            elif cur is not None:
                cur["n_continuation"] += 1
            continue
        if c8 == "G" and c6 == " " and cur is not None:
            cur["n_gammas"] += 1
    ds["n_levels"] = len(levels)
    return ds, levels


def read_adopted_levels(
    zip_path: Path = ENSDF_ZIP, members: Iterable[str] | None = None
) -> tuple[pl.DataFrame, pl.DataFrame]:
    """Parse every ADOPTED LEVELS dataset → ``(levels, datasets)`` DataFrames."""
    lrows: list[dict] = []
    drows: list[dict] = []
    for nucid, dsid, lines in iter_adopted_datasets(zip_path, members):
        ds, lv = parse_adopted_levels(nucid, dsid, lines)
        if ds is None:
            continue
        drows.append(ds)
        lrows.extend(lv)
    levels = pl.DataFrame(lrows, schema=LEVEL_SCHEMA)
    datasets = pl.DataFrame(drows, schema=DATASET_SCHEMA)
    return levels.sort("Z", "N", "level_index"), datasets.sort("Z", "N")


# --------------------------------------------------------------------------- level counts


MIN_SPINS_FOR_CUTOFF = 10
"""RIPL quotes a discrete-level spin cutoff only when >= 10 levels have assigned spins."""

_KNOWN_E = pl.col("energy_kev").is_not_null() & pl.col("energy_offset").is_null()


def cumulative_levels(levels: pl.DataFrame) -> pl.DataFrame:
    """Per nuclide: sorted known level energies (keV) — the N(E) staircase is
    ``n_cumulative[i] = i + 1`` at ``energies_kev[i]``. Levels whose energy is only
    known relative to an unplaced band head (``energy_offset``) are excluded."""
    known = levels.filter(_KNOWN_E).sort("nuclide_id", "energy_kev")
    return known.group_by("nuclide_id", "Z", "N", maintain_order=True).agg(
        pl.col("energy_kev").alias("energies_kev"),
        pl.len().alias("n_known_energy"),
    )


def level_counts(levels: pl.DataFrame, cutoffs: pl.DataFrame | None = None) -> pl.DataFrame:
    """Per-nuclide summary: total levels, levels with a known absolute energy, unique-Jπ
    count, highest level energy, and — when ``cutoffs`` (columns ``Z, N, Umax_mev, Nmax``)
    is given — the number of known-energy levels at or below ``Umax`` (``n_below_umax``;
    ``n_below_umax_firm`` additionally drops ``?``-flagged levels), RIPL's ``Nmax``, and
    the spin cutoff σ from the uniquely assigned spins below the cutoff
    (⟨(J+½)²⟩ = 2σ² + ¼, the RIPL recipe, null below :data:`MIN_SPINS_FOR_CUTOFF`)."""
    base = levels.group_by("nuclide_id", "Z", "N", "A").agg(
        pl.len().alias("n_levels"),
        _KNOWN_E.sum().alias("n_known_energy"),
        pl.col("j_unique").sum().alias("n_unique_jpi"),
        pl.col("energy_kev").filter(_KNOWN_E).max().alias("e_max_kev"),
    )
    if cutoffs is None:
        return base.sort("Z", "N")
    cut = cutoffs.select(
        pl.col("Z").cast(pl.Int16), pl.col("N").cast(pl.Int16),
        pl.col("Umax_mev").alias("ripl_umax_mev"), pl.col("Nmax").alias("ripl_nmax"),
    )  # fmt: skip
    lv = levels.join(cut, on=["Z", "N"], how="inner").filter(
        _KNOWN_E & (pl.col("energy_kev") <= pl.col("ripl_umax_mev") * 1000.0 + 1e-3)
    )
    below = lv.group_by("nuclide_id").agg(
        pl.len().alias("n_below_umax"),
        (~pl.col("questionable")).sum().alias("n_below_umax_firm"),
        pl.col("j_unique").sum().alias("n_spin_assigned_below_umax"),
        (
            ((pl.col("j_values").list.first() + 0.5) ** 2).filter(pl.col("j_unique")).mean()
        ).alias("_jsq"),
    ).with_columns(
        pl.when(
            (pl.col("_jsq") > 0.25)
            & (pl.col("n_spin_assigned_below_umax") >= MIN_SPINS_FOR_CUTOFF)
        )
        .then(((pl.col("_jsq") - 0.25) / 2.0).sqrt())
        .otherwise(None)
        .alias("spin_cutoff_discrete")
    ).drop("_jsq")
    out = base.join(cut, on=["Z", "N"], how="left").join(below, on="nuclide_id", how="left")
    return out.with_columns(
        pl.col("n_below_umax").fill_null(0),
        pl.col("n_below_umax_firm").fill_null(0),
        (pl.col("n_below_umax").fill_null(0) == pl.col("ripl_nmax")).alias("matches_ripl_nmax"),
    ).sort("Z", "N")
