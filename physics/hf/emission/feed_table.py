"""`feedexcl(Zcomp, Ncomp, type, nex, nexout)` of one (nucleus, ejectile) as a dense table.

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

Task: SPEEDD (the speed wave; no physics of its own). Acceptance test: the speed-wave golden
and `tests/hf/test_decay_fast.py`.

TALYS routines this stores for:
    multiple.f90:1 (multiple)   -- `feedexcl`, written per mother bin
    channels.f90:1 (channels)   -- which reads it back per (nex, nexout)

`multiple_emission` used to record `feedexcl` as a dict keyed (nex, nexout), one Python entry per
non-zero cell, and `exclusive_channels` looked every cell up again; at 18 MeV that is ~50,000
entries per energy written and read one at a time. `FeedTable` is the same record as a
(mother bin, daughter bin) array plus a `present` mask, so both ends read and write whole rows.
It is a `Mapping` with the dict's keys, values and `.get`, so every reader of the dict form
(the golden record, the A-mult gate, `score.py`) sees the same entries -- including an entry that
is present with value 0.0, which a gamma cascade out of an empty level writes.
"""

from __future__ import annotations

from collections.abc import Iterator, MutableMapping

import numpy as np


class FeedTable(MutableMapping):
    """(nex, nexout) -> mb, for 0 <= nex < nrows and 0 <= nexout < ncols; any other key lives in
    a small overflow dict (a binary feed longer than the daughter's grid).

    TALYS: multiple.f90:1 (multiple)
    Test: tests/hf/test_decay_fast.py
    """

    __slots__ = ("val", "present", "extra")

    def __init__(self, nrows: int, ncols: int):
        self.val = np.zeros((nrows, ncols))
        self.present = np.zeros((nrows, ncols), dtype=bool)
        self.extra: dict[tuple[int, int], float] = {}

    def _inside(self, a: int, b: int) -> bool:
        return 0 <= a < self.val.shape[0] and 0 <= b < self.val.shape[1]

    def __getitem__(self, key):
        a, b = key
        if self._inside(a, b):
            if self.present[a, b]:
                return float(self.val[a, b])
            raise KeyError(key)
        return self.extra[key]

    def __setitem__(self, key, v) -> None:
        a, b = key
        if self._inside(a, b):
            self.val[a, b] = v
            self.present[a, b] = True
        else:
            self.extra[key] = float(v)

    def __delitem__(self, key) -> None:
        a, b = key
        if self._inside(a, b) and self.present[a, b]:
            self.val[a, b] = 0.0
            self.present[a, b] = False
        else:
            del self.extra[key]

    def __iter__(self) -> Iterator[tuple[int, int]]:
        for a, b in zip(*np.nonzero(self.present)):  # noqa: B905
            yield int(a), int(b)
        yield from self.extra

    def __len__(self) -> int:
        return int(self.present.sum()) + len(self.extra)

    def add(self, a: int, b: int, v: float) -> None:
        """`fe[(a, b)] = fe.get((a, b), 0.0) + v`."""
        if self._inside(a, b):
            self.val[a, b] = (self.val[a, b] if self.present[a, b] else 0.0) + v
            self.present[a, b] = True
        else:
            self.extra[(a, b)] = self.extra.get((a, b), 0.0) + v

    def set_row_nonzero(self, a: int, row: np.ndarray) -> None:
        """Record every non-zero cell of `row` at mother bin `a`, into cells not yet present
        (a mother bin is decayed once, so 0.0 + v == v)."""
        k = min(row.shape[0], self.val.shape[1])
        nz = row[:k] != 0.0
        np.copyto(self.val[a, :k], row[:k], where=nz)
        np.logical_or(self.present[a, :k], nz, out=self.present[a, :k])
        for b in np.flatnonzero(row[k:] != 0.0).tolist():
            self.extra[(a, k + b)] = self.extra.get((a, k + b), 0.0) + float(row[k + b])

    def dense(self, nrows: int, ncols: int) -> np.ndarray:
        """The values on (0..nrows-1, 0..ncols-1), absent cells 0."""
        out = np.zeros((nrows, ncols))
        r, c = min(nrows, self.val.shape[0]), min(ncols, self.val.shape[1])
        out[:r, :c] = self.val[:r, :c]
        for (a, b), v in self.extra.items():
            if 0 <= a < nrows and 0 <= b < ncols:
                out[a, b] = v
        return out


def dense_feed(feed, nrows: int, ncols: int) -> np.ndarray:
    """A `feedexcl` record (FeedTable or the dump's dict) as an (nrows, ncols) array."""
    if isinstance(feed, FeedTable):
        return feed.dense(nrows, ncols)
    out = np.zeros((nrows, ncols))
    for (a, b), v in feed.items():
        if 0 <= a < nrows and 0 <= b < ncols:
            out[a, b] = v
    return out
