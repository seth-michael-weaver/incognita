"""Path resolution and fixed-format readers for TALYS's structure/ database. Each reader is
anchored to the Fortran `read` statement whose column positions it reproduces. No other data
source is allowed (contract §4.5).

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

Task: T2 (physics/hf/CONTRACT.md §7). Acceptance test: A-struct (§6).

TALYS routines ported here (file:line of the subroutine/function statement):
    structure.f90:1 (structure)
    levels.f90:1 (levels)
    masses.f90:1 (masses)
    deformpar.f90:1 (deformpar)
    resonancepar.f90:1 (resonancepar)

How Fortran formatted input is reproduced
-----------------------------------------
TALYS opens every structure file with the default ``BLANK='NULL'``: blanks inside a numeric
field are ignored and an all-blank field reads as zero. A real field without a decimal point
takes the implied decimal of its edit descriptor (``f11.6`` reads ``1454210`` as 1.454210).
:func:`fortran_read` implements exactly that for the descriptors these files use (``nx``,
``iw``, ``fw.d``, ``ew.d``, ``esw.d``, ``aw``). Lines shorter than the format are blank-padded,
which is what a formatted sequential read does at end of record.

Precision. Fields TALYS declares ``real(sgl)`` are returned rounded to float32 (as float64
numbers) by the callers, fields declared ``real(dbl)`` are returned as the float64 nearest to
the decimal string. Rounding a decimal first to float64 and then to float32 differs from
rounding it directly to float32 only when the decimal lies within one double ulp of a float32
midpoint, which the 7-significant-digit literals in structure/ never do.

Units traps in structure/ (see also CONTRACT.md §4.1):
  * ``resonances/*.res``: the header says ``gamgam[keV]`` and the values ARE keV (Au198
    1.28e-4 = 0.128 eV; Ni059 2.03e-3 = 2.03 eV), but TALYS stores them unconverted in `gamgam`,
    declared "total radiative width in eV", and prints them as ``experimental Gamma_gamma [eV]``
    (psf*.E1). The port keeps TALYS's number (faithful) as ``ResonanceData.gamgam_talys`` and
    exposes the physical width as ``gamgam_ev``.
  * ``resonances/*.res``: ``S[e-4]`` is in units of 1e-4 (Ni059 3.2 = 3.2e-4).
  * ``resonances/*.res``: ``D[eV]`` is eV.
"""

from __future__ import annotations

import os
import re
from functools import cache
from pathlib import Path

__all__ = [
    "talys_structure_dir",
    "fortran_read",
    "read_mass_file",
    "read_level_file",
    "level_records",
    "read_deformation_file",
    "read_resonance_file",
    "read_d0global",
]

_TOKEN = re.compile(r"(\d*)([a-zA-Z]+)(\d*)(?:\.(\d+))?")
_EXP_NO_LETTER = re.compile(r"(?<=[\d.])([+-]\d+)$")


def talys_structure_dir() -> Path:
    """`$TALYS_DIR/structure`, default `~/opt/talys-src/structure`; raises if missing.

    TALYS: structure.f90:1 (structure)
    Test: A-struct
    """
    return _structure_dir(os.environ.get("TALYS_DIR") or "")


_STRUCTURE_DIRS: dict[str, Path] = {}


def _structure_dir(env: str) -> Path:
    """COREX: the resolved directory per $TALYS_DIR value, remembered once it exists."""
    path = _STRUCTURE_DIRS.get(env)
    if path is None:
        base = env or str(Path.home() / "opt" / "talys-src")
        path = Path(base) / "structure"
        if not path.is_dir():
            raise FileNotFoundError(f"TALYS structure database not found at {path}; set TALYS_DIR")
        _STRUCTURE_DIRS[env] = path
    return path


@cache
def _parse_format(fmt: str) -> tuple[tuple[str, int, int], ...]:
    """'(4x, i4, 2f12.6)' -> (('x',4,0), ('i',4,0), ('f',12,6), ('f',12,6))"""
    body = fmt.strip()
    if body.startswith("(") and body.endswith(")"):
        body = body[1:-1]
    # expand non-nested repeated groups: 2(3x, a1) -> 3x, a1, 3x, a1
    group = re.compile(r"(\d+)\(([^()]*)\)")
    while True:
        new = group.sub(lambda m: ", ".join([m.group(2)] * int(m.group(1))), body)
        if new == body:
            break
        body = new
    out: list[tuple[str, int, int]] = []
    for item in body.split(","):
        item = item.strip().lower()
        if not item:
            continue
        m = _TOKEN.fullmatch(item)
        if m is None:
            raise ValueError(f"unsupported edit descriptor {item!r} in {fmt!r}")
        rep, kind, width, dec = m.groups()
        if kind == "x":  # nX: the count precedes the letter
            out.append(("x", int(rep or 1), 0))
            continue
        n = int(rep or 1)
        w = int(width) if width else 1
        d = int(dec) if dec else 0
        if kind not in ("i", "f", "e", "es", "a"):
            raise ValueError(f"unsupported edit descriptor {item!r} in {fmt!r}")
        out.extend([(kind, w, d)] * n)
    return tuple(out)


def _real(field: str, d: int) -> float:
    s = field.replace(" ", "")
    if not s:
        return 0.0
    s = s.replace("D", "E").replace("d", "E")
    if "E" not in s.upper():
        s = _EXP_NO_LETTER.sub(r"E\1", s)
    mant, _, exp = s.upper().partition("E")
    if "." not in mant:
        sign = ""
        if mant[:1] in "+-":
            sign, mant = mant[0], mant[1:]
        mant = sign + (mant[:-d] if d else mant) + "." + (mant[-d:] if d else "")
        if mant in ("+.", "-.", "."):
            mant = "0"
    return float(mant + ("E" + exp if exp else ""))


def fortran_read(line: str, fmt: str) -> list:
    """Values of one formatted record, reproducing gfortran's defaults for these files.

    TALYS: levels.f90:1 (levels)
    Test: A-struct
    """
    parse = _PARSERS.get(fmt)
    if parse is None:
        parse = _PARSERS[fmt] = _make_parser(fmt)
    return parse(line)


def fortran_reader(fmt: str):
    """`functools.partial(fortran_read, fmt=fmt)` without the extra call per record (COREX).

    TALYS: levels.f90:1 (levels)
    Test: A-struct
    """
    parse = _PARSERS.get(fmt)
    if parse is None:
        parse = _PARSERS[fmt] = _make_parser(fmt)
    return parse


_PARSERS: dict = {}
_NOT_PLAIN = ("_", "n", "N", "i", "I")


def _make_parser(fmt: str):
    """COREX: `fortran_read` for one format as generated code, one conversion per field.

    A real field containing '.' and none of '_', 'n', 'N', 'i', 'I' is read by Python's `float`,
    which then agrees with gfortran's BLANK='NULL' read: it skips the blanks around the number,
    rejects inner blanks, D exponents and signed exponents without a letter (those raise and go to
    `_real`, as does a field without '.', whose decimals are implied), and underscores, nan and inf
    are excluded beforehand. An integer field without '_' is read by `int`, falling back to the
    blank-dropping read when that raises. tests/hf/test_corex.py fuzzes it against c8035ee2."""
    width, plan = _read_plan(fmt)
    src = ["def parse(line):", f"    rec = line.rstrip('\\n').ljust({width})", "    out = []"]
    for k, (kind, a, b, d) in enumerate(plan):
        f = f"f{k}"
        src.append(f"    {f} = rec[{a}:{b}]")
        if kind == "a":
            src.append(f"    out.append({f})")
        elif kind == "i":
            src += ["    try:",
                    f"        if '_' in {f}:",
                    "            raise ValueError",
                    f"        out.append(int({f}))",
                    "    except ValueError:",
                    f"        out.append(_int_blank({f}))"]
        else:
            cond = " and ".join([f"'.' in {f}"] + [f"{c!r} not in {f}" for c in _NOT_PLAIN])
            src += ["    try:",
                    f"        if not ({cond}):",
                    "            raise ValueError",
                    f"        out.append(float({f}))",
                    "    except ValueError:",
                    f"        out.append(_real({f}, {d}))"]
    src.append("    return out")
    ns: dict = {"_real": _real, "_int_blank": _int_blank}
    # compiled under this file's name, so profiles charge the generated code to this module
    exec(compile("\n".join(src), __file__, "exec"), ns)  # noqa: S102
    return ns["parse"]


def _int_blank(field: str) -> int:
    s = field.replace(" ", "")
    return int(s) if s not in ("", "+", "-") else 0


@cache
def _read_plan(fmt: str) -> tuple[int, tuple[tuple[str, int, int, int], ...]]:
    """`_parse_format` as record slices: (record width, ((kind, start, stop, decimals), ...)),
    with the `x` skips folded into the offsets."""
    spec = _parse_format(fmt)
    pos, plan = 0, []
    for kind, w, d in spec:
        if kind != "x":
            plan.append((kind, pos, pos + w, d))
        pos += w
    return pos, tuple(plan)


@cache
def _lines(path: str) -> tuple[str, ...]:
    with open(path, encoding="latin-1") as f:
        return tuple(f.read().splitlines())


class LazyLines:
    """COREX: `tuple(text.splitlines())` of a file whose only line break is '\\n', without building
    the tuple: the text is kept whole with the offsets of its line starts and ends, and a line is
    sliced out when it is indexed (a reader that walks block headers touches a few hundred of an
    element file's ~40,000 lines). Indexing and len as a tuple; slices return tuples."""

    __slots__ = ("_text", "_starts", "_ends")

    def __init__(self, text: str, starts, ends):
        self._text, self._starts, self._ends = text, starts, ends

    def __len__(self) -> int:
        return len(self._starts)

    def __getitem__(self, i):
        if isinstance(i, slice):
            text = self._text
            return tuple([text[a:b] for a, b in zip(self._starts[i].tolist(),
                                                    self._ends[i].tolist(), strict=True)])
        return self._text[self._starts[i]:self._ends[i]]


def lazy_lines(path: str, encoding: str = "latin-1") -> LazyLines | tuple[str, ...]:
    """`LazyLines` of a file, or the plain split lines when it holds any other line break
    `str.splitlines` would split at (or, for another encoding than latin-1, any non-ASCII byte).

    TALYS: levels.f90:1 (levels)
    Test: A-struct
    """
    import numpy as np

    with open(path, "rb") as f:
        data = f.read()
    if encoding != "latin-1" and not data.isascii():
        return tuple(data.decode(encoding).splitlines())
    # NATIVEX2 `struct`: one pass for every control byte instead of seven substring scans and a
    # newline pass: the file takes the plain split exactly when a control byte other than '\n'
    # is one of str.splitlines' breaks (\r \x0b \x0c \x1c \x1d \x1e) or it holds \x85
    arr = np.frombuffer(data, dtype=np.uint8)
    ctrl = np.flatnonzero(arr < 32)
    kinds = arr[ctrl]
    if (b"\x85" in data or bool((((kinds >= 11) & (kinds <= 13)) | (kinds >= 28)).any())):
        return tuple(data.decode(encoding).splitlines())
    nl = ctrl[kinds == 10]
    starts = np.concatenate(([0], nl + 1))
    ends = np.concatenate((nl, [len(data)]))
    if starts[-1] == len(data):  # a final newline ends the last line; no empty line follows
        starts, ends = starts[:-1], ends[:-1]
    return LazyLines(data.decode("latin-1"), starts, ends)


@cache
def _lazy_lines(path: str) -> LazyLines | tuple[str, ...]:
    return lazy_lines(path)


def read_mass_file(Z: int, table: str) -> dict[int, tuple]:
    """One element's mass table, keyed by A.

    ``table="ame2020"``: {A: (mass_amu, mass_excess_mev)}, read with '(4x, i4, 2f12.6)'
    (masses.f90:119). Theoretical tables ``hfb``, ``frdm``, ``hfbd1m``: {A: (mass_amu,
    mass_excess_mev, beta2, beta4, gs_spin, gs_parity)}, read with
    '(4x, i4, 2f12.6, 2f8.4, 20x, f4.1, i2)' (masses.f90:155). Missing file -> {}.

    TALYS: masses.f90:1 (masses)
    Test: A-struct
    """
    from physics.hf.core.constants import nuclide_symbol

    path = talys_structure_dir() / "masses" / table / f"{nuclide_symbol(Z)}.mass"
    if not path.is_file():
        return {}
    out: dict[int, tuple] = {}
    if table == "ame2020":
        read = fortran_reader("(4x, i4, 2f12.6)")
        for line in _lines(str(path)):
            ia, m, exc = read(line)
            out[ia] = (m, exc)
    else:
        read = fortran_reader("(4x, i4, 2f12.6, 2f8.4, 20x, f4.1, i2)")
        for line in _lines(str(path)):
            ia, m, exc, b2, b4, gs, p = read(line)
            out[ia] = (m, exc, b2, b4, gs, p)
    return out


def read_level_file(Z: int, A: int, disctable: int = 1, levelfile: str | None = None):
    """The block of `levels/<final|exp|hfb>/<Sym>.lev` for mass A, as raw records.

    Returns None when the file does not exist (levels.f90:139-140 returns early) and
    ``(nnn, records)`` otherwise, where `records` is the list of level lines each followed by
    its branch lines, exactly as they appear, and nnn = 0 with no records if A is absent.
    Header '(4x, i4, 2i5)' (levels.f90:161).

    TALYS: levels.f90:1 (levels)
    Test: A-struct
    """
    got = level_records(Z, A, disctable, levelfile)
    if got is None:
        return None
    nnn, recs = got
    return nnn, recs.materialise()


class LevelRecords:
    """NATIVEX2 `struct`: a block's records as `read_level_file` returns them -- the slice
    `lines[start:stop]` -- without building the tuple (`levels._level_block` reads the level
    lines up to numlev2 and skips the rest of a block that may hold thousands). Length and
    non-negative integer indexing as that tuple."""

    __slots__ = ("_lines", "_start", "_n")

    def __init__(self, lines, start: int, stop: int):
        total = len(lines)
        start, stop = min(start, total), min(stop, total)
        self._lines, self._start, self._n = lines, start, max(stop - start, 0)

    def __len__(self) -> int:
        return self._n

    def __getitem__(self, k: int) -> str:
        if not 0 <= k < self._n:
            raise IndexError("level record index out of range")
        return self._lines[self._start + k]

    def materialise(self) -> tuple[str, ...]:
        return tuple(self._lines[self._start : self._start + self._n])

    def buffer(self):
        """(latin-1 bytes of the records' span, line starts, line ends within it) when the file is
        held as a `LazyLines` text, else None."""
        import numpy as np

        lines = self._lines
        if not isinstance(lines, LazyLines) or self._n == 0:
            return None
        a, b = self._start, self._start + self._n
        st, en = lines._starts[a:b], lines._ends[a:b]
        s0 = int(st[0])
        data = lines._text[s0:int(en[-1])].encode("latin-1")
        return (data, np.ascontiguousarray(st - s0, dtype=np.int64),
                np.ascontiguousarray(en - s0, dtype=np.int64))


def level_records(Z: int, A: int, disctable: int = 1, levelfile: str | None = None):
    """`read_level_file` with the records as a `LevelRecords` view (NATIVEX2 `struct`).

    TALYS: levels.f90:1 (levels)
    Test: tests/hf/test_nx2_struct.py
    """
    from physics.hf.core.constants import nuclide_symbol

    if levelfile:
        path = Path(levelfile)
    else:
        sub = {1: "final", 2: "exp", 3: "hfb"}[disctable]
        path = talys_structure_dir() / "levels" / sub / f"{nuclide_symbol(Z)}.lev"
    if not path.is_file():
        return None
    lines = _lazy_lines(str(path))
    got = _level_headers(str(path)).get(A)  # NATIVEX2: the walk below, done once per file
    if got is not None:
        i, nlevlines, nnn = got
        return nnn, LevelRecords(lines, i + 1, i + 1 + nlevlines)
    i = 0
    while i < len(lines):
        ia, nlevlines, nnn = fortran_read(lines[i], "(4x, i4, 2i5)")
        if ia == A:
            return nnn, LevelRecords(lines, i + 1, i + 1 + nlevlines)
        i += 1 + nlevlines
    return 0, LevelRecords((), 0, 0)


@cache
def _level_headers(path: str) -> dict[int, tuple[int, int, int]]:
    """NATIVEX2: `read_level_file`'s header walk over one file, once: {A: (header line, nlevlines,
    nnn)} for the first block of each mass, up to the first header the walk could not read (a mass
    not in the dict takes the walk itself, which then raises or returns as before)."""
    lines = _lazy_lines(path)
    out: dict[int, tuple[int, int, int]] = {}
    i = 0
    try:
        while i < len(lines):
            ia, nlevlines, nnn = fortran_read(lines[i], "(4x, i4, 2i5)")
            out.setdefault(ia, (i, nlevlines, nnn))
            i += 1 + nlevlines
    except (ValueError, IndexError):
        pass
    return out


def read_deformation_file(Z: int, A: int, deformfile: str | None = None):
    """The `deformation/<Sym>.def` block for mass A: (colltype, deftype, rows) or None.

    Header '(4x, 2i4, 2(3x, a1))' (deformpar.f90:128); rows '(i4, 3x, a1, 4i4, 4f9.5)'
    (deformpar.f90:147) as (nex, leveltype, vibband, lband, Kmag, iphonon, deform[4]).

    TALYS: deformpar.f90:1 (deformpar)
    Test: A-struct
    """
    from physics.hf.core.constants import nuclide_symbol

    path = (
        Path(deformfile)
        if deformfile
        else (talys_structure_dir() / "deformation" / f"{nuclide_symbol(Z)}.def")
    )
    if not path.is_file():
        return None
    lines = _lines(str(path))
    i = 0
    while i < len(lines):
        ia, ndisc, colltype1, deftype1 = fortran_read(lines[i], "(4x, 2i4, 2(3x, a1))")
        if ia == A:
            rows = []
            for line in lines[i + 1 : i + 1 + ndisc]:
                v = fortran_read(line, "(i4, 3x, a1, 4i4, 4f9.5)")
                rows.append((v[0], v[1], v[2], v[3], v[4], v[5], tuple(v[6:10])))
            return colltype1, deftype1, rows
        i += 1 + ndisc
    return None


def read_resonance_file(Z: int) -> list[tuple]:
    """Every record of `resonances/<Sym>.res`: (A, L, D, dD, S, dS, gamgam, dgamgam, R, dR,
    Nrr), read with '(4x, 2i4, 8es15.6, i4)' (resonancepar.f90:79). Units as in the file:
    D eV, S in 1e-4, gamgam keV (see module docstring), R fm.

    TALYS: resonancepar.f90:1 (resonancepar)
    Test: A-struct
    """
    from physics.hf.core.constants import nuclide_symbol

    path = talys_structure_dir() / "resonances" / f"{nuclide_symbol(Z)}.res"
    if not path.is_file():
        return []
    out = []
    for line in _lines(str(path)):
        if line.lstrip().startswith("#"):
            # a Fortran formatted read of the comment header yields blanks -> A = 0, never matched
            continue
        out.append(tuple(fortran_read(line, "(4x, 2i4, 8es15.6, i4)")))
    return out


def read_d0global(ext: str, Z: int, A: int) -> float | None:
    """Global D0 [eV] for (Z, A) from `resonances/D0global.<ext>` (list-directed read,
    resonancepar.f90:129), or None.

    TALYS: resonancepar.f90:1 (resonancepar)
    Test: A-struct
    """
    table = _d0global_table(ext)
    return table.get((Z, A))


@cache
def _d0global_table(ext: str) -> dict[tuple[int, int], float]:
    path = talys_structure_dir() / "resonances" / f"D0global.{ext}"
    out: dict[tuple[int, int], float] = {}
    if not path.is_file():
        return out
    for line in _lines(str(path)):
        parts = line.split()
        if len(parts) < 3:
            continue
        try:
            key = (int(parts[0]), int(parts[1]))
        except ValueError:
            continue
        # resonancepar exits at the FIRST match (resonancepar.f90:133-137)
        out.setdefault(key, float(parts[2]))
    return out
