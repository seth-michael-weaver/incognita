"""Multi-block parser for TALYS YANDF output files (`# header:` ... `##` column rows ... data).

`physics/talys/runner.py::parse_yandf` reads one datablock and flattens the metadata, which is
right for the ``*.tot`` cross-section tables the sweeps use. The reference dumps the HF port is
tested against are different: ``transmission_n.out`` holds one datablock per emission energy,
``binE*.out`` one per ejectile, ``ld*.gs`` a parameter header plus several tables, and several
files carry non-numeric columns (``J/P`` = ``2.0 +``, ``def. type`` = ``B``) or ragged
continuation rows (branching lines in ``levels*.out`` and ``gamma*.tot``).

This parser keeps all of that:

* every ``datablock`` becomes a :class:`Block` carrying the metadata in scope at that point --
  the file header plus every ``# parameters:`` / ``# quantity:`` key seen since, with later keys
  overriding earlier ones, so a block knows its own ``energy [MeV]``;
* rows whose whitespace tokens are all numbers and match the column count go into ``data``
  (float64); every other row is kept verbatim in ``raw_rows`` with its row index, so nothing is
  silently dropped and a dedicated parser can reinterpret it.

Units stay exactly as TALYS writes them (``[mb]``, ``[MeV]``, ``[MeV^-1]``); the column's unit
string travels with the column. Converting is the consumer's job and must be explicit.

Stdlib + numpy only, so the harness can parse on any compute box.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

_NUM = re.compile(r"^[+-]?(\d+\.?\d*|\.\d+)([eEdD][+-]?\d+)?$")


@dataclass
class Block:
    """One YANDF datablock and the metadata in scope where it appears."""

    meta: dict[str, str]
    columns: list[str]
    units: list[str]
    data: np.ndarray  # (n_numeric_rows, n_columns) float64
    numeric_row_index: list[int]  # position of each numeric row among all rows
    raw_rows: list[tuple[int, str]] = field(default_factory=list)  # (row index, line)

    def meta_float(self, key: str) -> float | None:
        """A metadata value as float, matching ``key`` exactly or as the key without units."""
        for k, v in self.meta.items():
            if k == key or k.split(" [", 1)[0] == key:
                try:
                    return float(v.split()[0].replace("D", "E"))
                except (ValueError, IndexError):
                    return None
        return None

    def column(self, name: str) -> np.ndarray:
        return self.data[:, self.columns.index(name)]


def _is_num(tok: str) -> bool:
    return bool(_NUM.match(tok))


def parse_blocks(path: str | Path) -> list[Block]:
    """Parse every datablock in a YANDF file. Returns [] for a file with no ``##`` header.

    Metadata scoping. The file is cut into segments, one per datablock: segment b is every
    ``#`` line after datablock b-1's rows and up to datablock b's ``##`` header. A key belongs
    to block b if it is in segment b. A key from segment 0 is also inherited by every later
    block (a file-level key such as ``particle`` or ``a(Sn)``) unless its section path recurs
    with key-value lines in a later segment, in which case it was per-block data that happened
    to come first. This gets both failure modes right that a flat running dict gets wrong:

    * empty datablocks (``entries: -1``, a closed channel) have no rows, so a flush that waits
      for rows attaches the NEXT block's ``energy [MeV]`` to them (Ni-58 transmission_a.out
      started at 0.43 MeV instead of 0.32 and listed 3.4 MeV twice);
    * a block that omits a key TALYS writes only sometimes (``number of discrete levels`` is
      absent from binE blocks with no continuum) must not inherit the previous block's value.
    """
    lines = Path(path).read_text(errors="replace").splitlines()
    segments: list[list[tuple[tuple[str, ...], str, str]]] = [[]]
    parsed: list[tuple] = []  # (cols, units, rows, idx, raw) per datablock, in order
    stack: list[tuple[int, str]] = []  # (indent, section) for nested keys
    cols: list[str] | None = None
    units: list[str] | None = None
    rows: list[list[float]] = []
    idx: list[int] = []
    raw: list[tuple[int, str]] = []
    nrow = 0

    def seg_value(key: str) -> str | None:
        for _, k, v in reversed(segments[-1]):
            if k == key:
                return v
        return None

    def flush():
        nonlocal cols, units, rows, idx, raw, nrow
        if cols is not None:
            parsed.append((cols, units, rows, idx, raw))
            segments.append([])
        cols, units, rows, idx, raw, nrow = None, None, [], [], [], 0

    for ln in lines:
        if ln.startswith("##"):
            body = ln[2:]
            toks = _split_header(body, seg_value("columns"))
            if cols is not None and units is None and not rows and not raw and toks:
                if all(t.startswith("[") for t in toks):
                    units = toks
                    continue
            flush()
            cols = toks
            continue
        if ln.startswith("#"):
            if cols is not None:
                flush()  # any metadata line ends the datablock above it, rows or not
            body = ln[1:]
            indent = len(body) - len(body.lstrip(" "))
            text = body.strip()
            if not text or ":" not in text:
                continue
            k, _, v = text.partition(":")
            k, v = k.strip(), v.strip()
            while stack and stack[-1][0] >= indent:
                stack.pop()
            if not v:
                stack.append((indent, k))
                continue
            segments[-1].append((tuple(name for _, name in stack), k, v))
            continue
        if cols is None:
            continue
        toks = ln.split()
        if not toks:
            continue
        if len(toks) == len(cols) and all(_is_num(t) for t in toks):
            rows.append([float(t.replace("D", "E")) for t in toks])
            idx.append(nrow)
        else:
            raw.append((nrow, ln))
        nrow += 1
    flush()

    recurring = {path for seg in segments[1:] for path, _, _ in seg}
    file_level = {k: v for path, k, v in segments[0] if path not in recurring}
    blocks: list[Block] = []
    for b, (bcols, bunits, brows, bidx, braw) in enumerate(parsed):
        meta = dict(file_level)
        meta.update({k: v for _, k, v in segments[b]})
        n = len(bcols)
        data = np.array(brows, dtype=np.float64) if brows else np.zeros((0, n))
        blocks.append(Block(meta, list(bcols), list(bunits or [""] * n), data, bidx, braw))
    return blocks


def _split_header(body: str, ncol: str | None = None) -> list[str]:
    """Split a ``##`` row into column names.

    TALYS writes names in 15-character fields (write_block.f90), and names can contain spaces
    (``JP= 0.5-``, ``rho(J)=  0.5``) or touch their neighbour (``Compound_elast. Shape_elastic``),
    so the ``columns: N`` count declared just above the row wins whenever it is present. Without
    it, fall back to runs of >= 2 spaces.
    """
    try:
        n = int(ncol) if ncol is not None else 0
    except ValueError:
        n = 0
    if n > 0 and len(body.rstrip()) > 15 * (n - 1):
        return [body[15 * i : 15 * (i + 1)].strip() for i in range(n)]
    return [t.strip() for t in re.split(r"\s{2,}", body.strip()) if t.strip()]


def to_long(blocks: list[Block], keep_meta: tuple[str, ...] = ()) -> dict[str, list]:
    """Flatten numeric data to long-format columns (block, row, column, unit, value, + meta)."""
    out: dict[str, list] = {"block": [], "row": [], "column": [], "unit": [], "value": []}
    for k in keep_meta:
        out[k] = []
    for b, blk in enumerate(blocks):
        n, m = blk.data.shape if blk.data.ndim == 2 else (0, 0)
        for j in range(m):
            unit = blk.units[j] if j < len(blk.units) else ""
            for i in range(n):
                out["block"].append(b)
                out["row"].append(blk.numeric_row_index[i])
                out["column"].append(blk.columns[j])
                out["unit"].append(unit)
                out["value"].append(float(blk.data[i, j]))
                for k in keep_meta:
                    out[k].append(blk.meta.get(k))
    return out
