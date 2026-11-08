"""KWCOV B2: the run's incident energies from TALYS's `energy` and `estop` keywords.

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

Task: T3 (physics/hf/CONTRACT.md §7, the input layer). Acceptance test: KWCOV-B2, tests/hf/test_kwcov_b2.py (the
grids TALYS writes to its `energies` file).

TALYS routines ported here (file:line of the subroutine statement):
    read_energies.f90:1 (read_energies)   `energy E` (one energy), `energy E1 E2 [dE]` (a range; dE 0 or
                                          absent = 10 equal steps), `energy <file>` (one energy per line, zeros
                                          dropped, sorted, duplicates removed), and the `estop` cut
    incidentgrid.f90:1 (incidentgrid)     `energy n0-20.grid` style pre-defined grids (no `estop` cut: TALYS
                                          jumps past it)
    input_main.f90: the `energy` keyword at line 136, `estop` at 152

TALYS keeps every incident energy in `real(sgl)`; so does this module (each value is a float32 rounded
float). `estop` drops the energies above it but NOT the run's `enincmax`, which read_energies sets before the
cut: an `estop` run is the full declared grid with only the energies up to `estop` computed, i.e.
`ChainedFull(declared_energies=<all>, energies=<kept>)`, which `estop_subset` gives the engine.
"""

from __future__ import annotations

import os
from pathlib import Path

import numpy as np

PARSYM = ("g", "n", "p", "d", "t", "h", "a")  # constants.f90:89
EMAXTALYS_MEV = 1000.0  # A0_talys_mod.f90 (Emaxtalys)
NUMENIN = 600  # numenin, A0_talys_mod.f90


def _sgl(x: float) -> float:
    return float(np.float32(x))


def incident_grid(fname: str) -> tuple[float, ...] | None:
    """TALYS's pre-defined grid `<p><E1>-<E2>.grid` (e.g. `n0-20.grid`), or None when `fname` is not one.

    TALYS: incidentgrid.f90:1 (incidentgrid)
    Test: tests/hf/test_kwcov_b2.py
    """
    f = fname[:14]
    if not f or f[0] not in PARSYM or "-" not in f or ".grid" not in f:
        return None
    ktype = PARSYM.index(f[0])
    pos = f.index("-")
    k = f.find(".grid", pos + 1)
    if k < pos + 2:
        return None
    try:
        emin, emax = float(int(f[1:pos])), float(int(f[pos + 1:k]))
    except ValueError:
        return None
    e = [1.e-11, 2.53e-8, 1.e-6, 1.e-5, 1.e-4, 0.001, 0.002, 0.004, 0.007, 0.01, 0.02, 0.04, 0.07, 0.1]
    e = [np.float32(x) for x in e]
    ein, de = np.float32(0.1), np.float32(0.1)
    while True:  # incidentgrid.f90:91-108, in single precision
        ein = np.float32(ein + de)
        eeps = np.float32(ein + np.float32(1.e-4))
        if ein > EMAXTALYS_MEV or len(e) == NUMENIN:
            break
        e.append(ein)
        for lim, step in ((1., .2), (8., .5), (15., 1.), (30., 2.), (60., 5.), (80., 10.), (160., 20.),
                          (300., 50.), (600., 100.)):
            if eeps > lim:
                de = np.float32(step)
    out = []
    for ein in e:
        eeps = np.float32(ein + np.float32(1.e-4))
        if eeps < emin:
            continue
        if ktype != 1:
            if eeps < 1.:
                continue
            if np.float32(eeps - np.float32(int(eeps))) > 0.1:
                continue
        if ein <= np.float32(emax + np.float32(1.e-4)):
            out.append(float(ein))
        else:
            break
    return tuple(out) if out else None


def read_energies(value: str | list, estop_mev: float = EMAXTALYS_MEV, cwd: str | os.PathLike = ".") -> tuple[
        tuple[float, ...], tuple[float, ...]]:
    """The incident energies of an `energy` line's value(s): (the declared grid, the energies computed).

    `value` is the text after `energy` (or its words). The two tuples differ only when `estop` cuts the grid:
    TALYS keeps `enincmax` of the whole grid (read_energies.f90:180-187 run before the cut at :188-194).

    TALYS: read_energies.f90:1 (read_energies), input_main.f90:1 (input_main)
    Test: tests/hf/test_kwcov_b2.py
    """
    w = value.split() if isinstance(value, str) else [str(x) for x in value]
    if not w:
        raise ValueError("energy: no value")
    ch = w[0][:1]
    if ch.isdigit() or ch == ".":
        e1 = _sgl(float(w[0]))
        try:
            ef = _sgl(float(w[1])) if len(w) > 1 else 0.0
        except ValueError:
            ef = 0.0
        try:
            de = _sgl(float(w[2])) if len(w) > 2 else 0.0
        except ValueError:
            de = 0.0
        if ef == 0.0:
            grid = [e1]
        else:  # read_energies.f90:160-187
            if not 0.0 <= e1 <= ef:
                raise ValueError(f"energy: first energy {e1} outside 0..{ef}")
            if not 0.0 <= de <= EMAXTALYS_MEV:
                raise ValueError(f"energy: increment {de} outside 0..{EMAXTALYS_MEV}")
            if de == 0.0:
                de = _sgl(np.float32(np.float32(ef) - np.float32(e1)) / np.float32(9))
            grid = [e1]
            while True:
                if len(grid) + 1 > NUMENIN:
                    raise ValueError(f"energy: more than {NUMENIN} incident energies")
                e = _sgl(np.float32(grid[-1]) + np.float32(de))
                if e < _sgl(np.float32(ef) - np.float32(1.e-4)):
                    grid.append(e)
                else:
                    grid.append(ef)
                    break
    else:
        p = Path(cwd) / w[0]
        if not p.is_file():
            g = incident_grid(w[0])
            if g is None:
                raise ValueError(f"energy: {w[0]!r} is neither a file nor a pre-defined grid (TALYS-error)")
            return g, g  # read_energies.f90:121: `goto 300` jumps past the estop cut
        vals = []
        for line in p.read_text(errors="replace").splitlines():
            t = line.split()
            if not t:
                continue
            x = _sgl(float(t[0].replace("d", "e").replace("D", "E")))
            if x != 0.0:
                vals.append(x)
        if not vals:
            raise ValueError(f"energy: there are no incident energies in file {p}")
        if len(vals) > NUMENIN:
            raise ValueError(f"energy: more than {NUMENIN} incident energies in {p}")
        grid = sorted(set(vals))
    est = _sgl(estop_mev)
    kept = []
    for e in grid:  # read_energies.f90:188-194: stop at the first energy above estop
        if e > est:
            break
        kept.append(e)
    return tuple(grid), tuple(kept)


def estop_subset(Z: int, A: int, declared, want):
    """The engine's `want` set (rounded energies to compute; None = all) after the deck's `estop` line.

    Unchanged (the same object) unless a deck line sets `estop`; then only the declared energies up to the
    first one above `estop` are kept (read_energies.f90:188-194), and the run's grid stays `declared`.

    TALYS: read_energies.f90:1 (read_energies)
    Test: tests/hf/test_kwcov_b2.py
    """
    from physics.hf.input import fitlib

    c = fitlib.current(int(Z), int(A))
    if c is None:
        return want
    v = dict(c.options).get("estop")
    if v is None:
        return want
    est = _sgl(float(v))
    keep = set()
    for e in declared:
        if _sgl(e) > est:
            break
        keep.add(round(e, 6))
    return keep if want is None else (set(want) & keep)
