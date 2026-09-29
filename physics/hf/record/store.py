"""The record files: one flat, mmap-able file per nuclide and one chart index (CREC, WP4).

A nuclide file is

    b"CREC0002" | u64 key length | u64 entries length | u64 arrays
    | key JSON | entries JSON | array table (packed `TABLE` rows) | array blobs

little-endian, with the table and every blob at an offset that is a multiple of 64, so the table
and any dense array are viewed in place from an `mmap` of the file. Opening a record parses the
key (a few hundred bytes) and views the table; the entries JSON is parsed on first use.

* A table row is (dtype, ndim, shape, offset, nnz, offset of values). `nnz = -1` is a dense blob
  at `offset`; otherwise the array is stored sparse, `nnz` int32 flat indices at `offset` and
  `nnz` values at the second offset (used when that is under half the dense bytes -- the direct
  and giant-resonance arrays are 99 % zeros). Two arrays with the same dtype, shape and bytes
  share one blob.
* `entries` are the recorded cache entries, each a skeleton of `codec` (see `caches`).

The chart index `index.json` lists every nuclide file with its size and key, and carries the
key fields every file shares, so a worker checks them once.

TALYS: none (worker cache policy)
Test: scripts/hf_route100_record.py verify
"""

from __future__ import annotations

import functools
import hashlib
import json
import mmap
import os
import struct
from pathlib import Path

import numpy as np

MAGIC = b"CREC0002"
ALIGN = 64
INDEX = "index.json"
MAX_NDIM = 6
TABLE = np.dtype([("dtype", "S4"), ("ndim", "<i4"), ("shape", "<i8", (MAX_NDIM,)),
                  ("offset", "<i8"), ("nnz", "<i8"), ("voffset", "<i8")])


def _pad(n: int) -> int:
    return (-n) % ALIGN


def nuclide_file(Z: int, A: int) -> str:
    return f"{Z:03d}_{A:03d}.crec"


def write(path: Path, key: dict, entries: list, arrays: list[np.ndarray],
          sparse_below: float = 0.5) -> dict:
    """Write one nuclide record atomically; returns {"bytes", "dense_bytes", "arrays", "blobs"}.

    TALYS: none (worker cache policy)
    Test: scripts/hf_route100_record.py verify
    """
    table: list = []
    blobs: list[bytes] = []
    offset = 0
    by_content: dict[tuple, list] = {}
    dense_total = 0

    def put(b: bytes) -> int:
        nonlocal offset
        at = offset
        blobs.append(b)
        blobs.append(b"\0" * _pad(len(b)))
        offset += len(b) + _pad(len(b))
        return at

    for a in arrays:
        a = np.ascontiguousarray(a)
        raw = a.tobytes()
        dense_total += len(raw)
        ck = (a.dtype.str, a.shape, hashlib.blake2b(raw, digest_size=16).digest())
        hit = by_content.get(ck)
        if hit is not None:
            table.append(hit)
            continue
        flat = a.reshape(-1)
        nz = np.flatnonzero(flat) if a.dtype.kind in "fcib" and flat.size < 2**31 else None
        if nz is not None and nz.size * (4 + a.itemsize) < sparse_below * len(raw):
            idx = put(nz.astype("<i4").tobytes())
            vals = put(np.ascontiguousarray(flat[nz]).tobytes())
            row = [a.dtype.str, list(a.shape), idx, int(nz.size), vals]
        else:
            row = [a.dtype.str, list(a.shape), put(raw), -1, 0]
        by_content[ck] = row
        table.append(row)
    rows = np.zeros(len(table), TABLE)
    for i, (dt, shape, off, nnz, voff) in enumerate(table):
        if len(shape) > MAX_NDIM:
            raise ValueError(f"array {i}: {len(shape)} dimensions")
        rows[i] = (dt.encode(), len(shape), (*shape, *[0] * (MAX_NDIM - len(shape))), off, nnz,
                   voff)
    kb = json.dumps(key, separators=(",", ":")).encode()
    eb = json.dumps(entries, separators=(",", ":")).encode()
    head = MAGIC + struct.pack("<QQQ", len(kb), len(eb), len(table)) + kb + eb
    head += b"\0" * _pad(len(head)) + rows.tobytes()
    head += b"\0" * _pad(len(head))
    path = Path(path)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "wb") as f:
        f.write(head)
        for b in blobs:
            f.write(b)
    os.replace(tmp, path)
    return {"bytes": len(head) + offset, "dense_bytes": dense_total, "arrays": len(arrays),
            "blobs": len(by_content)}


class NuclideRecord:
    """One nuclide file, mapped: `key`, `entries`, and `array(i)` (an owned copy of table entry
    i, rebuilt from its sparse form where stored so). Nothing is read until asked for.

    TALYS: none (worker cache policy)
    Test: scripts/hf_route100_record.py verify
    """

    def __init__(self, path: Path) -> None:
        self.path = Path(path)
        with open(self.path, "rb") as f:
            self._mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
        if self._mm[:8] != MAGIC:
            raise ValueError(f"{path}: not a CREC record of format {MAGIC.decode()}")
        nk, ne, na = struct.unpack("<QQQ", self._mm[8:32])
        self._entries_at = (32 + nk, 32 + nk + ne)
        at = 32 + nk + ne
        at += _pad(at)
        self.key: dict = json.loads(self._mm[32:32 + nk])
        self.table = np.frombuffer(self._mm, TABLE, na, at)
        self._base = at + na * TABLE.itemsize
        self._base += _pad(self._base)

    @functools.cached_property
    def entries(self) -> list:
        lo, hi = self._entries_at
        return json.loads(self._mm[lo:hi])

    def view(self, i: int) -> np.ndarray:
        """Table entry i in place on the mapping (read-only) when dense; rebuilt when sparse."""
        dt, ndim, shape, off, nnz, voff = self.table[i].item()
        dt, shape = np.dtype(dt.decode()), shape[:ndim]
        count = int(np.prod(shape, dtype=np.int64))
        if nnz < 0:
            return np.frombuffer(self._mm, dt, count, self._base + off).reshape(shape)
        out = np.zeros(count, dt)
        out[np.frombuffer(self._mm, "<i4", nnz, self._base + off)] = np.frombuffer(
            self._mm, dt, nnz, self._base + voff)
        return out.reshape(shape)

    def array(self, i: int) -> np.ndarray:
        v = self.view(i)
        return v.copy() if self.table["nnz"][i] < 0 else v

    def close(self) -> None:
        self.table = None  # the table is a view on the mapping; arrays handed out are copies
        self._mm.close()


def write_index(root: Path, shared: dict, nuclides: dict) -> Path:
    """`index.json`: {"format", "shared": key fields common to all, "nuclides": {"Z-A": {...}}}.

    TALYS: none (worker cache policy)
    Test: scripts/hf_route100_record.py verify
    """
    p = Path(root) / INDEX
    tmp = p.with_suffix(".tmp")
    tmp.write_text(json.dumps({"format": MAGIC.decode(), "shared": shared,
                               "nuclides": nuclides}, indent=0, sort_keys=True))
    os.replace(tmp, p)
    return p


class ChartRecord:
    """The chart index and its nuclide files, opened lazily (`nuclide(Z, A)` maps one file).

    TALYS: none (worker cache policy)
    Test: scripts/hf_route100_record.py load
    """

    def __init__(self, root: Path) -> None:
        self.root = Path(root)
        idx = json.loads((self.root / INDEX).read_text())
        if idx["format"] != MAGIC.decode():
            raise ValueError(f"{root}: record format {idx['format']}, loader {MAGIC.decode()}")
        self.shared: dict = idx["shared"]
        self.nuclides: dict = idx["nuclides"]
        self._open: dict[tuple[int, int], NuclideRecord] = {}

    def __contains__(self, za) -> bool:
        return f"{za[0]}-{za[1]}" in self.nuclides

    def nuclide(self, Z: int, A: int) -> NuclideRecord:
        rec = self._open.get((Z, A))
        if rec is None:
            meta = self.nuclides[f"{Z}-{A}"]
            rec = self._open[(Z, A)] = NuclideRecord(self.root / meta["file"])
        return rec

    def close(self) -> None:
        for r in self._open.values():
            r.close()
        self._open.clear()
