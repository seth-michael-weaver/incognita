"""WP-10: RIPL-4 segment parsers (blueprint §3.1, §4.2 "RIPL").

One reader per RIPL-4 segment, each returning a :class:`polars.DataFrame` keyed by
``(Z, A)`` (with ``N`` added so tables join on the project ``(Z, N)`` convention).
Nothing here writes to ``staging/`` or ``features/``; :mod:`data.ingest.build_structure`
does the joining and the Parquet output.

Layout of the RIPL-4 GitHub release (``raw/ripl4/RIPL-4/``), May 2026 — see
``docs/ripl4-notes.md`` for the full inventory:

* ``resonances/resonances_L0.dat``, ``resonances_L1.dat`` — s-/p-wave average
  resonance parameters, RIPL-3 and BNL (Mughabghab 2018) columns side by side.
* ``levels/z###.dat`` (discrete level schemes, one file per element) and
  ``levels/levels-param.data`` (constant-temperature fits, completeness cutoff
  ``Nmax``/``Umax``, discrete-level spin cutoff).
* ``densities/total/level-densities-egsm.dat`` (EGSM ``a`` fitted to D0),
  ``level-densities-egsm-norm.dat``, ``shellcor-ms.dat`` and the microscopic
  combinatorial tables ``bskg3-comb/``, ``bsk14-comb/``, ``thfb-comb/``, ``qrpabe/``.
  The RIPL-3 BSFG / GC / HFB parameter files are *not* in RIPL-4.
* ``gamma/gdr-parameters_exp&systematics_{slo,smlo}.dat`` (8980 nuclides, flag
  ``In``: 1 = experimental, 0 = systematics), ``gdr_parameters&errors_exp_*.dat``
  (uncertainties), and zipped GSF tables (``smlo_E1.zip``, ``smlo_M1.zip``, ``d1m.zip``).
* ``fission/empirical-barriers-ripl4.dat`` (empirical double-humped barriers with
  uncertainties), ``barriers-bskg3.dat``, ``barriers-d1m_lep.dat``, ``WMM/``.
* ``masses/mass-{ame20,bskg3,d1m,frdm12,hfb27,ws4}.dat`` plus abundances and
  experimental β2.
* ``optical/om-summary-2026/om-parameter-u-latest.dat`` — 589 OMP entries in the
  free-format RIPL OMP layout, with ``omp-index.txt`` and ``references``.

Measured vs systematics: every reader emits a ``source`` column (``"measured"`` /
``"systematics"``) where the segment distinguishes them (GDR ``In`` flag, empirical
vs HFB barriers, EGSM ``a_exp`` vs ``a_sys``). Resonance parameters are all
evaluated from measured resonances, so they are ``measured``.

Dropped rows are never silent: they are logged at WARNING level and collected in
:data:`DROPPED` so the build script can print a summary.
"""

from __future__ import annotations

import logging
import re
import zipfile
from collections import defaultdict
from collections.abc import Iterable, Iterator
from pathlib import Path

import polars as pl

from data.schema.base import Source

log = logging.getLogger(__name__)

REPO = Path(__file__).resolve().parents[2]
RIPL4_ROOT = REPO / "raw" / "ripl4" / "RIPL-4"
RIPL_VERSION = "RIPL-4 (2026)"

__all__ = [
    "DROPPED",
    "ELEMENTS",
    "MASS_MODELS",
    "RIPL4_ROOT",
    "RIPL_VERSION",
    "fortran_slices",
    "gdr_params",
    "list_gsf_tables",
    "list_mass_models",
    "omp_irefs_for",
    "parse_fixed",
    "read_abundances",
    "read_comb_ld",
    "read_comb_table",
    "read_discrete_levels",
    "read_egsm",
    "read_egsm_norm",
    "read_fission_bskg3",
    "read_fission_d1m",
    "read_fission_empirical",
    "read_fission_empire",
    "read_fission_wmm",
    "read_gdr",
    "read_gdr_exp",
    "read_gdr_recommended",
    "read_gs_deformations",
    "read_gsf_table",
    "read_level_headers",
    "read_levels_param",
    "read_mass_table",
    "read_optical_index",
    "read_optical_potentials",
    "read_optical_references",
    "read_resonances",
    "read_shell_corrections",
    "resonance_params",
    "symbol_to_z",
]

# --------------------------------------------------------------------------- elements

ELEMENTS: tuple[str, ...] = (
    "n", "H", "He", "Li", "Be", "B", "C", "N", "O", "F", "Ne",
    "Na", "Mg", "Al", "Si", "P", "S", "Cl", "Ar", "K", "Ca",
    "Sc", "Ti", "V", "Cr", "Mn", "Fe", "Co", "Ni", "Cu", "Zn",
    "Ga", "Ge", "As", "Se", "Br", "Kr", "Rb", "Sr", "Y", "Zr",
    "Nb", "Mo", "Tc", "Ru", "Rh", "Pd", "Ag", "Cd", "In", "Sn",
    "Sb", "Te", "I", "Xe", "Cs", "Ba", "La", "Ce", "Pr", "Nd",
    "Pm", "Sm", "Eu", "Gd", "Tb", "Dy", "Ho", "Er", "Tm", "Yb",
    "Lu", "Hf", "Ta", "W", "Re", "Os", "Ir", "Pt", "Au", "Hg",
    "Tl", "Pb", "Bi", "Po", "At", "Rn", "Fr", "Ra", "Ac", "Th",
    "Pa", "U", "Np", "Pu", "Am", "Cm", "Bk", "Cf", "Es", "Fm",
    "Md", "No", "Lr", "Rf", "Db", "Sg", "Bh", "Hs", "Mt", "Ds",
    "Rg", "Cn", "Nh", "Fl", "Mc", "Lv", "Ts", "Og",
)  # fmt: skip
_SYMBOL_TO_Z = {s.upper(): z for z, s in enumerate(ELEMENTS)}


def symbol_to_z(symbol: str) -> int:
    """Element symbol → Z (case-insensitive; ``"NN"``/``"n"`` → 0; digits → int)."""
    s = symbol.strip()
    if s.isdigit():
        return int(s)
    if s == "n" or s.upper() == "NN":  # lowercase "n" (RIPL) / "NN" (ENSDF) = neutron
        return 0
    try:
        return _SYMBOL_TO_Z[s.upper()]
    except KeyError:
        raise ValueError(f"unknown element symbol {symbol!r}") from None


# --------------------------------------------------------------------------- drop log

DROPPED: dict[str, list[str]] = defaultdict(list)
"""segment → list of ``"<reason>: <line>"`` for every row a reader could not use."""


def _drop(segment: str, line: str, reason: str) -> None:
    msg = f"{reason}: {line.rstrip()[:120]}"
    DROPPED[segment].append(msg)
    log.warning("%s dropped row — %s", segment, msg)


def _data_lines(path: Path, comment: str = "#") -> Iterator[str]:
    with path.open(encoding="latin-1") as fh:
        for line in fh:
            line = line.rstrip("\r\n")
            if not line.strip() or line.lstrip().startswith(comment):
                continue
            yield line


# --------------------------------------------------------------------------- fixed width

_TOKEN = re.compile(r"^(\d*)([aAiIfFeEgGxX])(\d*)(?:\.(\d+))?$")


def _split_top(s: str) -> list[str]:
    out, depth, cur = [], 0, []
    for ch in s:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == "," and depth == 0:
            out.append("".join(cur))
            cur = []
        else:
            cur.append(ch)
    if cur:
        out.append("".join(cur))
    return out


def _expand(fmt: str) -> list[tuple[str, int]]:
    s = fmt.strip()
    if s.startswith("(") and s.endswith(")"):
        s = s[1:-1]
    items: list[tuple[str, int]] = []
    for tok in _split_top(s):
        tok = tok.strip()
        if not tok:
            continue
        m = re.match(r"^(\d*)\((.*)\)$", tok)
        if m:
            items += _expand(m[2]) * int(m[1] or 1)
            continue
        tok = re.sub(r"^\d*[pP]", "", tok)  # scale factors (1p, 0p) do not affect columns
        if not tok:
            continue
        m = _TOKEN.match(tok)
        if not m:
            raise ValueError(f"unsupported Fortran edit descriptor {tok!r} in {fmt!r}")
        rep, kind, width = int(m[1] or 1), m[2].lower(), m[3]
        w = int(width) if width else 1
        items += [(kind, w)] * rep
    return items


def fortran_slices(fmt: str) -> list[tuple[str, int, int]]:
    """Column slices ``(kind, start, stop)`` for a Fortran FORMAT string.

    Supports ``i``, ``f``, ``e``, ``g``, ``a``, ``x``, repeat counts, groups and scale
    factors — enough for every RIPL-4 readme. ``x`` fields are skipped.
    """
    out, pos = [], 0
    for kind, w in _expand(fmt):
        if kind != "x":
            out.append((kind, pos, pos + w))
        pos += w
    return out


def parse_fixed(line: str, slices: list[tuple[str, int, int]]) -> list:
    """Slice ``line`` per :func:`fortran_slices`; blank numeric fields → ``None``."""
    vals: list = []
    for kind, a, b in slices:
        field = line[a:b]
        if kind == "a":
            vals.append(field.strip())
            continue
        f = field.strip()
        if not f or set(f) == {"*"}:  # blank, or Fortran field overflow ("******")
            vals.append(None)
        elif kind == "i":
            vals.append(int(f))
        else:
            vals.append(float(f))
    return vals


def _read_fixed(
    path: Path, fmt: str, names: list[str], segment: str, min_len: int = 0
) -> pl.DataFrame:
    slices = fortran_slices(fmt)
    rows = []
    for line in _data_lines(path):
        if len(line) < min_len:
            _drop(segment, line, "short line")
            continue
        try:
            rows.append(parse_fixed(line, slices))
        except ValueError as e:
            _drop(segment, line, f"parse error ({e})")
    return pl.DataFrame(rows, schema=names, orient="row")


# --------------------------------------------------------------------------- RESONANCES

_RES_FMT = "(3i4,2x,a2,2x,i2,f5.1,1x,a1,f10.3,1p,12e12.3)"
_RES_NAMES = [
    "Z", "N", "A", "symbol", "L", "J_target", "parity_target", "Sn_mev",
    "d_ripl3_ev", "d_ripl3_sigma_ev", "d_bnl_ev", "d_bnl_sigma_ev",
    "gg_ripl3_ev", "gg_ripl3_sigma_ev", "gg_bnl_ev", "gg_bnl_sigma_ev",
    "s_ripl3_1e4", "s_ripl3_sigma_1e4", "s_bnl_1e4", "s_bnl_sigma_1e4",
]  # fmt: skip


def read_resonances(root: Path = RIPL4_ROOT, wave: int = 0) -> pl.DataFrame:
    """``resonances/resonances_L{wave}.dat``: average s- (0) or p-wave (1) parameters.

    Keys ``(Z, N, A)`` are the TARGET nucleus. ``D`` in eV, ``Gg`` in eV, ``S`` in units
    of 1e-4 (as in the file; :func:`resonance_params` converts). Two evaluations are
    given side by side: the RIPL-3 (Capote 2009) column and BNL (Mughabghab 2018).
    """
    path = root / "resonances" / f"resonances_L{wave}.dat"
    df = _read_fixed(path, _RES_FMT, _RES_NAMES, f"resonances_L{wave}", min_len=40)
    df = df.with_columns(
        pl.col("parity_target").replace_strict({"+": 1, "-": -1, "": 0}, default=0),
        pl.lit(Source.MEASURED.value).alias("source"),
    )
    bad = df.filter(pl.col("A") != pl.col("Z") + pl.col("N"))
    for row in bad.iter_rows(named=True):
        _drop(f"resonances_L{wave}", str(row), "A != Z + N")
    return df.filter(pl.col("A") == pl.col("Z") + pl.col("N"))


def _pick(df: pl.DataFrame, base: str, prefer: str, scale: float = 1.0) -> pl.DataFrame:
    """Add ``<base>``, ``<base>_sigma``, ``<base>_origin`` choosing the preferred column."""
    first, second = ("ripl3", "bnl") if prefer == "ripl3" else ("bnl", "ripl3")
    stem = {"d0": "d", "d1": "d", "s0": "s", "s1": "s", "gg": "gg"}[base]
    unit = {"d": "_ev", "s": "_1e4", "gg": "_ev"}[stem]
    v1, v2 = f"{stem}_{first}{unit}", f"{stem}_{second}{unit}"
    e1, e2 = f"{stem}_{first}_sigma{unit}", f"{stem}_{second}_sigma{unit}"
    use_first = pl.col(v1).is_not_null()
    return df.with_columns(
        (pl.when(use_first).then(pl.col(v1)).otherwise(pl.col(v2)) * scale).alias(base),
        (pl.when(use_first).then(pl.col(e1)).otherwise(pl.col(e2)) * scale).alias(f"{base}_sigma"),
        pl.when(use_first)
        .then(pl.lit("RIPL-3" if first == "ripl3" else "BNL2018"))
        .when(pl.col(v2).is_not_null())
        .then(pl.lit("RIPL-3" if second == "ripl3" else "BNL2018"))
        .otherwise(pl.lit(None, dtype=pl.String))
        .alias(f"{base}_origin"),
    )


def resonance_params(root: Path = RIPL4_ROOT, prefer: str = "ripl3") -> pl.DataFrame:
    """One row per TARGET nucleus with ``d0_ev``, ``s0``, ``gg_mev``, ``d1_ev``, ``s1``
    (+ ``_sigma``/``_origin``) chosen from the preferred evaluation with fallback.

    ``prefer="ripl3"`` is the default because RIPL-4's own EGSM level-density fit
    (``level-densities-egsm.dat``, "RIPL-4 Do") uses the RIPL-3 column. Units follow
    :class:`data.schema.StructureParams`: eV, dimensionless S (×1e-4 applied), meV.
    """
    if prefer not in {"ripl3", "bnl"}:
        raise ValueError("prefer must be 'ripl3' or 'bnl'")
    s = read_resonances(root, 0)
    s = _pick(s, "d0", prefer)
    s = _pick(s, "s0", prefer, scale=1e-4)
    s = _pick(s, "gg", prefer, scale=1e3)  # eV → meV
    s = s.rename({"gg": "gg_mev", "gg_sigma": "gg_sigma_mev"})
    p = read_resonances(root, 1)
    p = _pick(p, "d1", prefer)
    p = _pick(p, "s1", prefer, scale=1e-4)
    p = p.select(
        "Z", "N", "d1", "d1_sigma", "d1_origin", "s1", "s1_sigma", "s1_origin"
    ).rename({"d1": "d1_ev", "d1_sigma": "d1_sigma_ev"})
    keep = [
        "Z", "N", "A", "symbol", "J_target", "parity_target", "Sn_mev",
        "d0", "d0_sigma", "d0_origin", "s0", "s0_sigma", "s0_origin",
        "gg_mev", "gg_sigma_mev", "gg_origin",
    ]  # fmt: skip
    out = s.select(keep).rename({"d0": "d0_ev", "d0_sigma": "d0_sigma_ev"})
    return out.join(p, on=["Z", "N"], how="full", coalesce=True).sort("Z", "N")


# --------------------------------------------------------------------------- LEVELS

_LP_FMT = "(2i4,1x,a2,4(1x,f9.5),4i4,1x,f8.5,1x,f8.5,1x,e10.3,1x,a1,1x,a1,2i4,f7.4,1x,f6.3)"
_LP_NAMES = [
    "Z", "A", "symbol", "ct_T_mev", "ct_dT_mev", "ct_U0_mev", "ct_dU0_mev",
    "Nlev", "Nmax", "N0", "Nc", "Umax_mev", "Uc_mev", "chi", "fit", "flag",
    "NoX", "Xm", "Ex_mev", "sigma_discrete",
]  # fmt: skip


def read_levels_param(root: Path = RIPL4_ROOT) -> pl.DataFrame:
    """``levels/levels-param.data``: constant-temperature fit (T, U0) per nuclide, the
    completeness cutoff (``Nmax`` levels up to ``Umax_mev``), the unique-spin cutoff
    (``Nc``/``Uc_mev``), and the spin cutoff ``sigma_discrete`` from discrete-level spins.
    """
    df = _read_fixed(root / "levels" / "levels-param.data", _LP_FMT, _LP_NAMES, "levels_param")
    return df.with_columns((pl.col("A") - pl.col("Z")).alias("N"))


_ID_RE = re.compile(r"^\s*(\d{1,3})([A-Za-z]{1,2})\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)")
_ID_FMT = "(a5,6i5,2f12.6)"
_LEVEL_FMT = (
    "(i3,1x,f10.6,1x,f5.1,i3,1x,e10.3,i3,1x,a1,1x,a4,1x,a18,i3,"
    "10(1x,a2,1x,e10.4,1x,a7),f10.6,1x,3(i2))"
)
_GAMMA_FMT = "(39x,i4,1x,f10.4,3(1x,e10.3))"
_ID_SL, _LEVEL_SL, _GAMMA_SL = (fortran_slices(f) for f in (_ID_FMT, _LEVEL_FMT, _GAMMA_FMT))


def _level_files(root: Path, Z: Iterable[int] | None) -> list[Path]:
    if Z is None:
        return sorted((root / "levels").glob("z[0-9][0-9][0-9].dat"))
    return [root / "levels" / f"z{z:03d}.dat" for z in Z]


def _iter_level_file(path: Path) -> Iterator[tuple[list, list[list], list[list]]]:
    """Yield ``(ident, levels, gammas)`` per isotope, using the record counts in the
    identification record to consume exactly ``Nol`` levels and their gammas."""
    seg = f"levels/{path.name}"
    with path.open(encoding="latin-1") as fh:
        lines = fh.read().splitlines()
    i, n = 0, len(lines)
    while i < n:
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        if not _ID_RE.match(line):
            _drop(seg, line, "expected identification record")
            i += 1
            continue
        ident = parse_fixed(line, _ID_SL)
        nol = ident[3]
        i += 1
        levels: list[list] = []
        gammas: list[list] = []
        ok = True
        for _ in range(nol):
            if i >= n or _ID_RE.match(lines[i]):
                ok = False
                break
            try:
                lv = parse_fixed(lines[i], _LEVEL_SL)
            except ValueError as e:
                _drop(seg, lines[i], f"level parse error ({e})")
                ok = False
                break
            levels.append(lv)
            i += 1
            for _g in range(lv[5] or 0):
                if i >= n or not lines[i].startswith(" " * 30):
                    ok = False
                    break
                try:
                    gammas.append([lv[0], *parse_fixed(lines[i], _GAMMA_SL)])
                except ValueError as e:
                    _drop(seg, lines[i], f"gamma parse error ({e})")
                i += 1
            if not ok:
                break
        if not ok or len(levels) != nol:
            _drop(seg, line, f"isotope truncated: expected {nol} levels, got {len(levels)}")
            # resync at the next identification record
            while i < n and not _ID_RE.match(lines[i]):
                i += 1
            continue
        yield ident, levels, gammas


_HDR_NAMES = ["nucid", "A", "Z", "Nol", "Nog", "Nmax", "Nc", "Sn_mev", "Sp_mev"]


def read_level_headers(root: Path = RIPL4_ROOT, Z: Iterable[int] | None = None) -> pl.DataFrame:
    """Identification records of ``levels/z###.dat``: level/gamma counts, completeness
    cutoff ``Nmax``, unique-spin cutoff ``Nc``, and Sn/Sp (MeV)."""
    rows = [ident for p in _level_files(root, Z) for ident, _, _ in _iter_level_file(p)]
    df = pl.DataFrame(rows, schema=_HDR_NAMES, orient="row")
    return df.with_columns((pl.col("A") - pl.col("Z")).alias("N"))


def read_discrete_levels(
    root: Path = RIPL4_ROOT, Z: Iterable[int] | None = None, include_gammas: bool = False
) -> pl.DataFrame | tuple[pl.DataFrame, pl.DataFrame]:
    """Discrete levels from ``levels/z###.dat`` (RIPL-4: ENSDF Oct 2025 + NUBASE2020).

    Columns: ``Z, N, A, level_index (1-based), energy_mev, spin (-1 = unknown),
    parity (0 unknown), half_life_s (-1 = stable), n_gammas, spin_flag, energy_flag,
    jpi_raw, n_decay_modes, decay_modes (list of "mod percent mode"), shift_mev, bands``.
    With ``include_gammas`` also returns ``(Z, A, level_index, final_index, e_gamma_mev,
    p_gamma, p_em, icc)``.
    """
    lrows, grows = [], []
    for path in _level_files(root, Z):
        for ident, levels, gammas in _iter_level_file(path):
            A, Zc = ident[1], ident[2]
            for lv in levels:
                modes = []
                for k in range(lv[9] or 0):
                    mod, pct, mode = lv[10 + 3 * k], lv[11 + 3 * k], lv[12 + 3 * k]
                    modes.append(f"{mod} {pct if pct is not None else ''} {mode}".strip())
                lrows.append(
                    (
                        Zc, A - Zc, A, lv[0], lv[1], lv[2], lv[3], lv[4], lv[5] or 0,
                        lv[6], lv[7], lv[8], lv[9] or 0, modes, lv[40],
                        [b for b in lv[41:44] if b is not None],
                    )
                )  # fmt: skip
            if include_gammas:
                grows += [(Zc, A, *g) for g in gammas]
    schema = {
        "Z": pl.Int16, "N": pl.Int16, "A": pl.Int16, "level_index": pl.Int32,
        "energy_mev": pl.Float64, "spin": pl.Float64, "parity": pl.Int8,
        "half_life_s": pl.Float64, "n_gammas": pl.Int16, "spin_flag": pl.String,
        "energy_flag": pl.String, "jpi_raw": pl.String, "n_decay_modes": pl.Int8,
        "decay_modes": pl.List(pl.String), "shift_mev": pl.Float64, "bands": pl.List(pl.Int8),
    }  # fmt: skip
    levels_df = pl.DataFrame(lrows, schema=schema, orient="row")
    if not include_gammas:
        return levels_df
    gschema = {
        "Z": pl.Int16, "A": pl.Int16, "level_index": pl.Int32, "final_index": pl.Int32,
        "e_gamma_mev": pl.Float64, "p_gamma": pl.Float64, "p_em": pl.Float64, "icc": pl.Float64,
    }  # fmt: skip
    return levels_df, pl.DataFrame(grows, schema=gschema, orient="row")


# --------------------------------------------------------------------------- DENSITIES

_EGSM_NAMES = [
    "Z", "A", "symbol", "J_target", "Bn_mev", "D0_kev", "D0_sigma_kev", "shell_mev",
    "beta2", "D0_calc_kev", "a_plus", "a_exp", "a_minus", "a_sys", "a_ratio",
]  # fmt: skip


def read_egsm(root: Path = RIPL4_ROOT) -> pl.DataFrame:
    """``densities/total/level-densities-egsm.dat``: EGSM level-density parameter ``a``
    at Bn for the 291 COMPOUND nuclei with a measured D0 (``a_exp`` with asymmetric
    errors ``a_plus``/``a_minus``, and the systematics value ``a_sys``)."""
    path = root / "densities" / "total" / "level-densities-egsm.dat"
    rows = []
    for line in _data_lines(path):
        t = line.split()
        if len(t) != 15:
            _drop("egsm", line, f"expected 15 fields, got {len(t)}")
            continue
        try:
            rows.append([int(t[0]), int(t[1]), t[2], *map(float, t[3:])])
        except ValueError as e:
            _drop("egsm", line, f"parse error ({e})")
    df = pl.DataFrame(rows, schema=_EGSM_NAMES, orient="row")
    return df.with_columns(
        (pl.col("A") - pl.col("Z")).alias("N"),
        pl.lit(Source.MEASURED.value).alias("source"),
        pl.lit("EGSM").alias("ld_model"),
    )


def read_egsm_norm(root: Path = RIPL4_ROOT) -> pl.DataFrame:
    """Per-element normalisation factor ``a_exp/a_sys`` for the EGSM systematics."""
    path = root / "densities" / "total" / "level-densities-egsm-norm.dat"
    return _read_fixed(path, "(i5,f8.4)", ["Z", "factor"], "egsm_norm")


def read_shell_corrections(root: Path = RIPL4_ROOT) -> pl.DataFrame:
    """Myers-Swiatecki shell corrections (MeV) with deformation correction and β2/β4."""
    path = root / "densities" / "shellcor-ms.dat"
    names = ["Z", "A", "symbol", "shell_mev", "deform_corr_mev", "beta2", "beta4"]
    df = _read_fixed(path, "(2i4,1x,a2,2(1x,f8.3),2(f6.3))", names, "shellcor_ms")
    return df.with_columns((pl.col("A") - pl.col("Z")).alias("N"))


COMB_MODELS = {
    "bskg3": "bskg3-comb", "bsk14": "bsk14-comb", "thfb": "thfb-comb", "qrpabe": "qrpabe"
}  # fmt: skip


def read_comb_ld(root: Path = RIPL4_ROOT, model: str = "bskg3") -> pl.DataFrame:
    """``densities/total/<model>-comb/z###.ld``: normalisation ``alpha`` (to D0) and energy
    shift ``delta_mev`` of the microscopic combinatorial level densities, with the level
    window ``Nlow..Ntop`` used in the fit. Only nuclides with a measured D0 appear."""
    d = root / "densities" / "total" / COMB_MODELS[model]
    rows = []
    for path in sorted(d.glob("z[0-9][0-9][0-9].ld")):
        for line in _data_lines(path):
            t = line.split()
            try:
                rows.append([int(t[0]), int(t[1]), int(t[2]), int(t[3]), float(t[4]), float(t[5])])
            except (ValueError, IndexError) as e:
                _drop(f"{model}-comb.ld", line, f"parse error ({e})")
    names = ["Z", "A", "Nlow", "Ntop", "alpha", "delta_mev"]
    df = pl.DataFrame(rows, schema=names, orient="row")
    return df.with_columns(
        (pl.col("A") - pl.col("Z")).alias("N"), pl.lit(f"{model}-comb").alias("ld_model")
    )


_TAB_TITLE = re.compile(r"Z=\s*(\d+)\s+A=\s*(\d+):\s*(Positive|Negative)-Parity")


def read_comb_table(root: Path, model: str, Z: int, with_spins: bool = False) -> pl.DataFrame:
    """One ``z###.tab`` of a combinatorial level-density model → long table
    ``(Z, A, parity, U_mev, T_mev, n_cumul, rho_obs, rho_tot[, rho_J])``.

    Files are 5-40 MB each; read one element at a time."""
    path = root / "densities" / "total" / COMB_MODELS[model] / f"z{Z:03d}.tab"
    rows = []
    cur = None
    for line in path.open(encoding="latin-1"):
        m = _TAB_TITLE.search(line)
        if m:
            cur = (int(m[1]), int(m[2]), 1 if m[3] == "Positive" else -1)
            continue
        if cur is None or line.startswith("*") or line.lstrip().startswith("U[MeV]"):
            continue
        t = line.split()
        if len(t) < 5:
            continue
        try:
            vals = [float(x) for x in t]
        except ValueError:
            continue
        row = [*cur, *vals[:5]]
        if with_spins:
            row.append(vals[5:])
        rows.append(row)
    schema: dict[str, pl.DataType | type] = {
        "Z": pl.Int16, "A": pl.Int16, "parity": pl.Int8, "U_mev": pl.Float64, "T_mev": pl.Float64,
        "n_cumul": pl.Float64, "rho_obs": pl.Float64, "rho_tot": pl.Float64,
    }  # fmt: skip
    if with_spins:
        schema["rho_J"] = pl.List(pl.Float64)
    return pl.DataFrame(rows, schema=schema, orient="row")


# --------------------------------------------------------------------------- GAMMA

_GDR_FMT = "(2i4,9f9.3,i5)"
_GDR_NAMES = [
    "Z", "A", "er1_mev", "wr1_mev", "s1_trk", "er2_mev", "wr2_mev", "s2_trk", "s_trk",
    "csp1_mb", "csp2_mb", "is_experimental",
]  # fmt: skip


def read_gdr(root: Path = RIPL4_ROOT, model: str = "slo") -> pl.DataFrame:
    """``gamma/gdr-parameters_exp&systematics_<model>.dat`` (8980 nuclides): one- or
    two-component GDR Lorentzian parameters. ``source`` = measured where the file's
    ``In`` flag is 1 (from the experimental compilation), systematics otherwise."""
    path = root / "gamma" / f"gdr-parameters_exp&systematics_{model}.dat"
    df = _read_fixed(path, _GDR_FMT, _GDR_NAMES, f"gdr_{model}", min_len=40)
    return df.with_columns(
        (pl.col("A") - pl.col("Z")).alias("N"),
        pl.when(pl.col("is_experimental") == 1)
        .then(pl.lit(Source.MEASURED.value))
        .otherwise(pl.lit(Source.SYSTEMATICS.value))
        .alias("source"),
        pl.lit(model.upper()).alias("gsf_model"),
    )


_GDR_EXP_FMT = "(2i4,1x,a2,a3,1x,9f8.3,a22)"
_GDR_EXP_NAMES = [
    "Z", "A", "symbol", "data_id", "er1_mev", "wr1_mev", "s1_trk", "csp1_mb",
    "er2_mev", "wr2_mev", "s2_trk", "csp2_mb", "s_trk", "e_range_ref",
]  # fmt: skip
_GDR_ERR_FMT = "(15x,9f8.3)"
_GDR_ERR_NAMES = [
    "er1_sigma_mev", "wr1_sigma_mev", "s1_sigma_trk", "csp1_sigma_mb", "er2_sigma_mev",
    "wr2_sigma_mev", "s2_sigma_trk", "csp2_sigma_mb", "s_sigma_trk",
]  # fmt: skip


def read_gdr_exp(root: Path = RIPL4_ROOT, model: str = "slo") -> pl.DataFrame:
    """``gamma/gdr_parameters&errors_exp_<model>.dat``: every experimental GDR fit (478
    entries, 144 isotopes + 19 natural elements with ``A == 0``) with 1-σ uncertainties.
    The first entry per (Z, A) is the recommended one (``is_recommended``)."""
    path = root / "gamma" / f"gdr_parameters&errors_exp_{model}.dat"
    sl_v, sl_e = fortran_slices(_GDR_EXP_FMT), fortran_slices(_GDR_ERR_FMT)
    rows, pending = [], None
    for line in _data_lines(path):
        if pending is None:
            try:
                pending = parse_fixed(line, sl_v)
            except ValueError as e:
                _drop(f"gdr_exp_{model}", line, f"parse error ({e})")
            continue
        try:
            errs = parse_fixed(line, sl_e)
        except ValueError as e:
            _drop(f"gdr_exp_{model}", line, f"error-line parse error ({e})")
            pending = None
            continue
        rows.append(pending + errs)
        pending = None
    df = pl.DataFrame(rows, schema=_GDR_EXP_NAMES + _GDR_ERR_NAMES, orient="row")
    return df.with_columns(
        (pl.int_range(pl.len()).over("Z", "A") == 0).alias("is_recommended"),
        pl.col("e_range_ref").str.strip_chars(),
    )


def read_gdr_recommended(root: Path = RIPL4_ROOT, model: str = "slo") -> pl.DataFrame:
    """``gamma/gdr_parameters_recommended_exp_<model>.dat`` (one entry per nuclide)."""
    path = root / "gamma" / f"gdr_parameters_recommended_exp_{model}.dat"
    names = [n for n in _GDR_EXP_NAMES if n != "data_id"]
    return _read_fixed(path, "(2i4,1x,a2,2x,9f8.3,a22)", names, f"gdr_rec_{model}")


def gdr_params(root: Path = RIPL4_ROOT, model: str = "slo") -> pl.DataFrame:
    """GDR table for all 8980 nuclides with 1-σ uncertainties attached to the measured
    rows (from the recommended experimental entry). Systematics rows have null σ."""
    base = read_gdr(root, model)
    exp = read_gdr_exp(root, model).filter(pl.col("is_recommended") & (pl.col("A") > 0))
    sig = exp.select("Z", "A", *_GDR_ERR_NAMES, "e_range_ref")
    out = base.join(sig, on=["Z", "A"], how="left")
    # Only measured rows may carry σ; guard against a nuclide listed in the errors file
    # but flagged systematics in the master table.
    return out.with_columns(
        [
            pl.when(pl.col("is_experimental") == 1).then(pl.col(c)).otherwise(None).alias(c)
            for c in _GDR_ERR_NAMES
        ]
    )


_GSF_MEMBER = re.compile(r"(?:fe1_the_(\d{3})_(\d{3})_|z(\d{3})_(e1|m1))")


def list_gsf_tables(root: Path = RIPL4_ROOT) -> pl.DataFrame:
    """Inventory of the zipped photon-strength-function tables (not extracted):
    ``smlo_E1.zip`` (one file per nuclide, T = 0-2 MeV), ``smlo_M1.zip`` and ``d1m.zip``
    (D1M+QRPA E1/M1, one file per element)."""
    rows = []
    for zname in ("smlo_E1", "smlo_M1", "d1m"):
        zpath = root / "gamma" / f"{zname}.zip"
        if not zpath.exists():
            continue
        with zipfile.ZipFile(zpath) as zf:
            for info in zf.infolist():
                if info.is_dir():
                    continue
                m = _GSF_MEMBER.search(info.filename)
                Z = A = None
                kind = zname
                if m:
                    if m[1]:
                        Z, A = int(m[1]), int(m[2])
                    else:
                        Z, kind = int(m[3]), f"{zname}:{m[4]}"
                rows.append((zname, info.filename, kind, Z, A, info.file_size))
    names = ["archive", "member", "kind", "Z", "A", "bytes"]
    return pl.DataFrame(rows, schema=names, orient="row")


def read_gsf_table(root: Path, archive: str, member: str) -> pl.DataFrame:
    """Read one GSF table from a gamma zip archive as numeric columns (first column is
    the photon energy in MeV; header names are kept when present)."""
    with zipfile.ZipFile(root / "gamma" / f"{archive}.zip") as zf:
        text = zf.read(member).decode("latin-1").splitlines()
    header, rows = None, []
    for line in text:
        if line.startswith("#"):
            if "E " in line and "T=" in line:
                header = ["E_mev", *[t for t in line[1:].split()[1:]]]
            continue
        t = line.split()
        try:
            rows.append([float(x) for x in t])
        except ValueError:
            continue
    ncol = max(len(r) for r in rows) if rows else 0
    names = header if header and len(header) == ncol else [f"c{i}" for i in range(ncol)]
    return pl.DataFrame([r for r in rows if len(r) == ncol], schema=names, orient="row")


# --------------------------------------------------------------------------- FISSION

_FISS_EMP_NAMES = [
    "Z", "A", "symbol", "sym_a", "Va_mev", "dVa_mev", "hwa_mev", "dhwa_mev",
    "sym_b", "Vb_mev", "dVb_mev", "hwb_mev", "dhwb_mev",
]  # fmt: skip


def read_fission_empirical(root: Path = RIPL4_ROOT) -> pl.DataFrame:
    """``fission/empirical-barriers-ripl4.dat``: empirical inner/outer barrier heights
    and curvatures (ħω) with estimated uncertainties (Capote & Sin, 2025). Pre-actinides
    carry only the inner height. Token-based because the columns drift by one relative
    to the readme's FORMAT."""
    path = root / "fission" / "empirical-barriers-ripl4.dat"
    rows = []
    for line in _data_lines(path):
        t = line.split()
        try:
            Z, A, sym = int(t[0]), int(t[1]), t[2]
            if len(t) == 6:
                row = [Z, A, sym, t[3], float(t[4]), float(t[5])] + [None] * 7
            elif len(t) == 8:
                row = [Z, A, sym, t[3], *map(float, t[4:8]), None, None, None, None, None]
            elif len(t) == 13:
                row = [Z, A, sym, t[3], *map(float, t[4:8]), t[8], *map(float, t[9:13])]
            else:
                _drop("fission_empirical", line, f"unexpected token count {len(t)}")
                continue
        except (ValueError, IndexError) as e:
            _drop("fission_empirical", line, f"parse error ({e})")
            continue
        rows.append(row)
    df = pl.DataFrame(rows, schema=_FISS_EMP_NAMES, orient="row")
    return df.with_columns(
        (pl.col("A") - pl.col("Z")).alias("N"), pl.lit(Source.MEASURED.value).alias("source")
    )


def read_fission_empire(root: Path = RIPL4_ROOT) -> pl.DataFrame:
    """``fission/empirical-barriers-new-EMPIRE.dat``: EMPIRE barrier set (heights,
    curvatures, optional third hump ``Vc`` and pairing shift ``delta_f``); ``*`` marks
    triple-humped cases."""
    path = root / "fission" / "empirical-barriers-new-EMPIRE.dat"
    names = ["Z", "A", "symbol", "triple", "sym_a", "Va_mev", "hwa_mev", "sym_b", "Vb_mev",
             "hwb_mev", "Vc_mev", "delta_f_mev"]  # fmt: skip
    rows = []
    for line in _data_lines(path):
        if not re.match(r"^\s*\*?\s*\d", line):
            continue
        triple = line.lstrip().startswith("*")
        t = line.replace("*", " ").split()
        try:
            Z, A, sym = int(t[0]), int(t[1]), t[2]
            rest = t[3:]
            row = [Z, A, sym, triple, rest[0], float(rest[1]), None, None, None, None, None, None]
            if len(rest) >= 5:
                row[6] = float(rest[2])
                row[7] = rest[3]
                row[8] = float(rest[4])
            if len(rest) >= 6:
                row[9] = float(rest[5])
            if len(rest) == 7:
                row[11] = float(rest[6])
            elif len(rest) == 8:
                row[10], row[11] = float(rest[6]), float(rest[7])
            elif len(rest) > 8 or len(rest) in (3, 4):
                _drop("fission_empire", line, f"unexpected token count {len(t)}")
                continue
        except (ValueError, IndexError) as e:
            _drop("fission_empire", line, f"parse error ({e})")
            continue
        rows.append(row)
    return pl.DataFrame(rows, schema=names, orient="row").with_columns(
        (pl.col("A") - pl.col("Z")).alias("N")
    )


def _read_numeric_table(path: Path, ncol: int, names: list[str], segment: str) -> pl.DataFrame:
    rows = []
    for line in _data_lines(path):
        t = line.split()
        if not t[0].lstrip("-").isdigit():
            continue  # un-commented header line ("Z N A | Binner ...")
        if len(t) != ncol:
            _drop(segment, line, f"expected {ncol} fields, got {len(t)}")
            continue
        try:
            rows.append([int(t[0]), int(t[1]), int(t[2]), *map(float, t[3:])])
        except ValueError as e:
            _drop(segment, line, f"parse error ({e})")
    return pl.DataFrame(rows, schema=names, orient="row")


def read_fission_bskg3(root: Path = RIPL4_ROOT) -> pl.DataFrame:
    """``fission/barriers-bskg3.dat``: HFB-BSkG3 barriers (inner, outer 1, outer 2) and
    two shape isomers with (β20, β22, β30) — 2449 nuclei with Z ≥ 90. 0.0 = absent."""
    names = ["Z", "N", "A"]
    for hump in ("inner", "outer1", "outer2", "isomer1", "isomer2"):
        names += [f"{hump}_mev", f"{hump}_b20", f"{hump}_b22", f"{hump}_b30"]
    df = _read_numeric_table(root / "fission" / "barriers-bskg3.dat", 23, names, "fission_bskg3")
    return df.with_columns(pl.lit(Source.SYSTEMATICS.value).alias("source"))


def read_fission_d1m(root: Path = RIPL4_ROOT) -> pl.DataFrame:
    """``fission/barriers-d1m_lep.dat``: Gogny-D1M least-energy-path barriers (45 nuclei)."""
    names = ["Z", "N", "A"]
    for hump in ("inner", "outer"):
        names += [f"{hump}_mev", f"{hump}_b20", f"{hump}_b22", f"{hump}_b30"]
    df = _read_numeric_table(root / "fission" / "barriers-d1m_lep.dat", 11, names, "fission_d1m")
    return df.with_columns(pl.lit(Source.SYSTEMATICS.value).alias("source"))


WMM_FILES = {
    "actinides_gs": "actinides_gs_WMM.dat",
    "actinides_inner": "actinides_inner_saddles_Bf1_WMM.dat",
    "actinides_outer": "actinides_outer_saddles_Bf2_WMM.dat",
    "actinides_secmin": "actinides_secmin_WMM.dat",
    "superheavy_gs": "superheavy_gs_WMM.dat",
    "superheavy_saddles": "superheavy_saddles_Bf_WMM.dat",
}


def read_fission_wmm(root: Path = RIPL4_ROOT, which: str = "actinides_inner") -> pl.DataFrame:
    """Warsaw macroscopic-microscopic (WMM) saddle/ground-state tables; columns are taken
    from the file's own ``#`` header."""
    path = root / "fission" / "WMM" / WMM_FILES[which]
    header = None
    with path.open(encoding="latin-1") as fh:
        for line in fh:
            if line.startswith("#"):
                header = line[1:].split()
                break
    if header is None:
        raise ValueError(f"no header in {path}")
    names = [h.replace("*", "star") for h in header]
    df = _read_numeric_table(path, len(names), names, f"wmm_{which}")
    return df.with_columns(pl.lit(Source.SYSTEMATICS.value).alias("source"))


# --------------------------------------------------------------------------- MASSES

MASS_MODELS: dict[str, tuple[str, list[str]]] = {
    "ame20": (
        "(2i4,1x,a2,1x,i1,2f10.3)",
        ["Z", "A", "symbol", "flag", "mexp_mev", "mexp_sigma_mev"],
    ),
    "bskg3": (
        "(2i4,1x,a2,1x,i1,3f10.3,7f8.3)",
        ["Z", "A", "symbol", "flag", "mexp_mev", "mexp_sigma_mev", "mth_mev", "beta20",
         "beta22", "gamma_deg", "beta30", "beta32", "beta4", "rch_fm"],
    ),
    "d1m": (
        "(2i4,1x,a2,1x,i1,3f10.3,2f8.3)",
        ["Z", "A", "symbol", "flag", "mexp_mev", "mexp_sigma_mev", "mth_mev", "beta20", "rch_fm"],
    ),
    "frdm12": (
        "(2i4,1x,a2,1x,i1,4f10.3,4f8.3)",
        ["Z", "A", "symbol", "flag", "mexp_mev", "mexp_sigma_mev", "mth_mev", "emic_mev",
         "beta2", "beta3", "beta4", "beta6"],
    ),
    "hfb27": (
        "(2i4,1x,a2,1x,i1,3f10.3,3f8.3)",
        ["Z", "A", "symbol", "flag", "mexp_mev", "mexp_sigma_mev", "mth_mev", "beta20",
         "beta40", "rch_fm"],
    ),
    "ws4": (
        "(2i4,1x,a2,1x,i1,4f10.3,3f8.3)",
        ["Z", "A", "symbol", "flag", "mexp_mev", "mexp_sigma_mev", "mth_mev", "esh_mev",
         "beta2", "beta4", "beta6"],
    ),
}  # fmt: skip
"""Mass tables in ``masses/``: ``flag`` 2 = AME2020 measured, 1 = AME2020 recommended
(extrapolated ``#``), 0 = no experimental mass. ``mth_mev`` is the model mass excess.
Models: AME2020 (experimental), BSkG3 and HFB-27 (Skyrme-HFB), D1M (Gogny-HFB),
FRDM(2012) and WS4 (macroscopic-microscopic)."""


def list_mass_models(root: Path = RIPL4_ROOT) -> list[str]:
    return [m for m in MASS_MODELS if (root / "masses" / f"mass-{m}.dat").exists()]


def read_mass_table(root: Path = RIPL4_ROOT, model: str = "frdm12") -> pl.DataFrame:
    """One ``masses/mass-<model>.dat`` table (fixed width; blank fields → null)."""
    fmt, names = MASS_MODELS[model]
    df = _read_fixed(root / "masses" / f"mass-{model}.dat", fmt, names, f"mass_{model}")
    return df.with_columns(
        (pl.col("A") - pl.col("Z")).alias("N"),
        pl.lit(model).alias("model"),
        (pl.col("flag") == 1).alias("mexp_extrapolated"),
    )


def read_abundances(root: Path = RIPL4_ROOT) -> pl.DataFrame:
    names = ["Z", "A", "symbol", "abundance_pct", "abundance_sigma_pct"]
    df = _read_fixed(root / "masses" / "abundance.dat", "(2i4,1x,a2,1x,2f10.6)", names, "abundance")
    return df.with_columns((pl.col("A") - pl.col("Z")).alias("N"))


def read_gs_deformations(root: Path = RIPL4_ROOT) -> pl.DataFrame:
    """Experimental β2 from B(E2) (Raman 2001), 328 nuclides."""
    names = ["Z", "A", "symbol", "beta2", "beta2_sigma"]
    df = _read_fixed(
        root / "masses" / "gs-deformations-exp.dat", "(2i4,1x,a2,1x,2f8.4)", names, "gs_deform"
    )
    return df.with_columns(
        (pl.col("A") - pl.col("Z")).alias("N"), pl.lit(Source.MEASURED.value).alias("source")
    )


# --------------------------------------------------------------------------- OPTICAL

_OMP_INDEX_RE = re.compile(
    r"^\s*(\d+)\s+(\S+)\s+(spher\.|CC rig\.|CC vib\.|CC softR|CC softD|CC soft|CC r/vi)"
    r"\s+(yes|no)\s+(yes|no)"
    r"\s+(\d+)-\s*(\d+)\s+(\d+)-\s*(\d+)\s+([\d.]+)-\s*([\d.]+)\s+(\d+)\s+(.*?)\s*$"
)
# RIPL-4 adds "CC softR"/"CC softD" (rigid / soft multiband, imodel 4 / 5) to the RIPL-3 labels.
_OMP_MODEL = {
    "spher.": "spherical", "CC rig.": "cc_rigid_rotor", "CC vib.": "cc_vibrational",
    "CC soft": "cc_soft_rotor", "CC r/vi": "cc_rigid_soft", "CC softR": "cc_rigid_multiband",
    "CC softD": "cc_soft_multiband",
}  # fmt: skip


def _optical_dir(root: Path) -> Path:
    d = root / "optical" / "om-summary-2026"
    return d if d.exists() else root / "optical" / "om-data"


def read_optical_index(root: Path = RIPL4_ROOT) -> pl.DataFrame:
    """``optical/om-summary-2026/omp-index.txt``: one row per OMP library entry —
    ``iref``, projectile, model type, dispersive/relativistic flags, Z/A/E validity
    ranges, reference number and first author."""
    d = _optical_dir(root)
    path = d / "omp-index.txt" if (d / "omp-index.txt").exists() else d / "om-index.txt"
    rows = []
    for line in _data_lines(path):
        m = _OMP_INDEX_RE.match(line)
        if not m:
            if "Lib." in line or "No." in line:
                continue
            _drop("optical_index", line, "unrecognised index line")
            continue
        rows.append(
            (
                int(m[1]), m[2], _OMP_MODEL[m[3]], m[4] == "yes", m[5] == "yes",
                int(m[6]), int(m[7]), int(m[8]), int(m[9]), float(m[10]), float(m[11]),
                int(m[12]), m[13],
            )
        )  # fmt: skip
    names = ["iref", "projectile", "model", "dispersive", "relativistic", "Zmin", "Zmax",
             "Amin", "Amax", "Emin_mev", "Emax_mev", "ref_no", "first_author"]  # fmt: skip
    return pl.DataFrame(rows, schema=names, orient="row")


def read_optical_references(root: Path = RIPL4_ROOT) -> pl.DataFrame:
    """Reference list keyed by ``ref_no`` (multi-line entries joined)."""
    d = _optical_dir(root)
    path = d / "references" if (d / "references").exists() else d / "om-references.txt"
    refs: dict[int, list[str]] = {}
    cur = None
    for line in path.open(encoding="latin-1"):
        m = re.match(r"^\s*(\d+)\.\s+(.*)$", line.rstrip())
        if m:
            cur = int(m[1])
            refs[cur] = [m[2]]
        elif cur is not None and line.strip():
            refs[cur].append(line.strip())
    rows = [(k, "".join(v)) for k, v in refs.items()]
    return pl.DataFrame(rows, schema=["ref_no", "reference"], orient="row")


_FORTRAN_FLOAT = re.compile(r"^([+-]?(?:\d+\.?\d*|\.\d+))([+-]\d+)$")


def _ftok(tok: str) -> float:
    """Fortran-style float without the E (``.00000+0``, ``-3.00000-1``)."""
    m = _FORTRAN_FLOAT.match(tok)
    return float(f"{m[1]}E{m[2]}") if m else float(tok)


class _Tokens:
    """Free-format numeric token cursor over consecutive lines."""

    def __init__(self, lines: list[str], start: int):
        self.lines, self.i, self.buf = lines, start, []

    def next(self) -> float:
        while not self.buf:
            if self.i >= len(self.lines):
                raise ValueError("unexpected end of entry")
            self.buf = self.lines[self.i].split()
            self.i += 1
        return _ftok(self.buf.pop(0))

    def take(self, n: int) -> list[float]:
        return [self.next() for _ in range(n)]

    def peek_line(self) -> list[str]:
        """Tokens of the next unread line (without consuming); [] at end."""
        if self.buf:
            return list(self.buf)
        return self.lines[self.i].split() if self.i < len(self.lines) else []

    def next_line(self) -> list[float]:
        """Discard any partial line and return the next line's tokens as floats."""
        self.buf = []
        if self.i >= len(self.lines):
            raise ValueError("unexpected end of entry")
        toks = self.lines[self.i].split()
        self.i += 1
        return [_ftok(t) for t in toks]

    def exhausted(self) -> bool:
        """True if no numeric token remains (only blank / ``+++`` separator lines)."""
        if self.buf:
            return False
        for line in self.lines[self.i :]:
            s = line.strip()
            if s and not set(s) <= {"+", "-", "="}:
                return False
        return True


def _parse_coupling(tk: _Tokens, imodel: int) -> dict:
    """Consume the coupled-channel section. Isotope headers and Hamiltonian parameters
    are read token-wise per the readme; coupled levels are ONE LINE EACH, because the
    RIPL-4 file carries 9 (imodel 4) / 10 (imodel 5) tokens per level where the readme
    documents 8 / 12."""
    out: dict = {"n_isotopes": 0, "isotopes": []}
    if imodel == 0:
        return out
    niso = int(tk.next())
    out["n_isotopes"] = niso
    for _ in range(niso):
        defs: list[float] = []
        if imodel in (1, 4, 5):
            iz, ia, ncoll, _lmax, idef, _bandk = tk.take(6)
            defs = tk.take(int(idef) // 2)
            if imodel == 5:
                tk.take(17)
        elif imodel == 2:
            iz, ia, ncoll = tk.take(3)
        elif imodel == 3:
            iz, ia, ncoll = tk.take(3)
            tk.take(17)
        else:
            raise ValueError(f"unknown imodel {imodel}")
        levels = [tk.next_line() for _ in range(int(ncoll))]
        out["isotopes"].append(
            {"Z": int(iz), "A": int(ia), "n_coupled": int(ncoll), "beta": defs, "levels": levels}
        )
    return out


_POT_TERMS = ["real_volume", "imag_volume", "real_surface", "imag_surface", "real_so", "imag_so"]


def read_optical_potentials(
    root: Path = RIPL4_ROOT, parse_body: bool = True
) -> tuple[pl.DataFrame, pl.DataFrame]:
    """``om-parameter-u-latest.dat`` → ``(entries, terms)``.

    ``entries``: one row per potential (``iref``, author, reference, summary, validity
    ranges, ``imodel``, projectile Z/A, ``irel``, ``idr``, ``parse_ok``, coupled
    isotopes as a list of (Z, A)). ``terms``: one row per (iref, term, energy range)
    with the 13 radius, 13 diffuseness and 25 strength coefficients of the RIPL
    functional form (see ``om-parameter-u.readme``). Entries whose numeric body fails
    to parse are kept with ``parse_ok = False`` and logged.
    """
    d = _optical_dir(root)
    path = d / "om-parameter-u-latest.dat"
    if not path.exists():
        path = d / "om-parameter-u.dat"
    lines = path.read_text(encoding="latin-1").splitlines()
    n = len(lines)

    def is_int_line(s: str) -> bool:
        return bool(re.match(r"^\s*\d+\s*$", s))

    def is_text(s: str) -> bool:
        return bool(re.search(r"[A-Za-z]", s)) and not re.match(r"^[\s\d.+\-Ee]+$", s)

    starts = [i for i in range(n - 1) if is_int_line(lines[i]) and is_text(lines[i + 1])]
    entries, terms = [], []
    for k, s in enumerate(starts):
        end = starts[k + 1] if k + 1 < len(starts) else n
        iref = int(lines[s])
        author, reference = lines[s + 1].strip(), lines[s + 2].strip()
        summary = " ".join(x.strip() for x in lines[s + 3 : s + 7]).strip()
        rec: dict = {
            "iref": iref, "author": author, "reference": reference, "summary": summary,
            "Emin_mev": None, "Emax_mev": None, "Zmin": None, "Zmax": None, "Amin": None,
            "Amax": None, "imodel": None, "Zproj": None, "Aproj": None, "irel": None,
            "idr": None, "n_coupled_isotopes": 0, "coupled_isotopes": [], "parse_ok": False,
        }  # fmt: skip
        try:
            tk = _Tokens(lines[:end], s + 7)
            rec["Emin_mev"], rec["Emax_mev"] = tk.take(2)
            rec["Zmin"], rec["Zmax"] = (int(x) for x in tk.take(2))
            rec["Amin"], rec["Amax"] = (int(x) for x in tk.take(2))
            imodel, zp, ap, irel, idr = (int(x) for x in tk.take(5))
            rec.update(imodel=imodel, Zproj=zp, Aproj=ap, irel=irel, idr=idr)
            if parse_body:
                for i, term in enumerate(_POT_TERMS, start=1):
                    jrange = int(tk.next())
                    for j in range(1, abs(jrange) + 1):
                        epot = tk.next()
                        rco, aco, pot = tk.take(13), tk.take(13), tk.take(25)
                        terms.append((iref, i, term, j, jrange < 0, epot, rco, aco, pot))
                # Coulomb block: "jcoul" then jcoul rows of 8. Some proton entries omit
                # the count line and give the 8-value row directly.
                if len(tk.peek_line()) >= 8:
                    while len(tk.peek_line()) >= 8:
                        tk.next_line()
                else:
                    jcoul = int(tk.next())
                    for _ in range(jcoul):
                        tk.take(8)
                coup = _parse_coupling(tk, imodel)
                rec["n_coupled_isotopes"] = coup["n_isotopes"]
                rec["coupled_isotopes"] = [(iso["Z"], iso["A"]) for iso in coup["isotopes"]]
                if not tk.exhausted():
                    raise ValueError("numeric lines left over after the coupling section")
                rec["parse_ok"] = True
            else:
                rec["parse_ok"] = True
        except (ValueError, IndexError) as e:
            _drop("optical_potentials", lines[s], f"iref {iref}: body parse failed ({e})")
        entries.append(rec)
    eschema = {
        "iref": pl.Int32, "author": pl.String, "reference": pl.String, "summary": pl.String,
        "Emin_mev": pl.Float64, "Emax_mev": pl.Float64, "Zmin": pl.Int16, "Zmax": pl.Int16,
        "Amin": pl.Int16, "Amax": pl.Int16, "imodel": pl.Int8, "Zproj": pl.Int8,
        "Aproj": pl.Int8, "irel": pl.Int8, "idr": pl.Int8, "n_coupled_isotopes": pl.Int16,
        "coupled_isotopes": pl.List(pl.List(pl.Int16)), "parse_ok": pl.Boolean,
    }  # fmt: skip
    entries_df = pl.DataFrame(entries, schema=eschema)
    tschema = {
        "iref": pl.Int32, "term_index": pl.Int8, "term": pl.String, "range_index": pl.Int8,
        "volume_integral": pl.Boolean, "epot_max_mev": pl.Float64,
        "rco": pl.List(pl.Float64), "aco": pl.List(pl.Float64), "pot": pl.List(pl.Float64),
    }  # fmt: skip
    terms_df = pl.DataFrame(terms, schema=tschema, orient="row")
    return entries_df, terms_df


def omp_irefs_for(
    entries: pl.DataFrame, Z: int, A: int, Zproj: int = 0, Aproj: int = 1
) -> list[int]:
    """OMP entries (by ``iref``) valid for projectile (Zproj, Aproj) on target (Z, A)."""
    hit = entries.filter(
        (pl.col("Zproj") == Zproj) & (pl.col("Aproj") == Aproj)
        & (pl.col("Zmin") <= Z) & (pl.col("Zmax") >= Z)
        & (pl.col("Amin") <= A) & (pl.col("Amax") >= A)
    )  # fmt: skip
    return sorted(hit["iref"].to_list())
