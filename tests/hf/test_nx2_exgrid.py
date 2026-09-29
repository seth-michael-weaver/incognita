"""MERGED2: `core.exgrid_nx2` (exgrid.f90's excitation bins in C) against
`core.grids._excitation_energies`, the reference body, bitwise.

TALYS: exgrid.f90:1 (exgrid)
"""

from __future__ import annotations

import numpy as np
import pytest

from physics.hf.core import exgrid_nx2
from physics.hf.core.grids import NUMEX, _excitation_energies, excitation_energies

needs_build = pytest.mark.skipif(exgrid_nx2._fn() is None,
                                 reason="no libnx2 build (scripts/build_nx2_native.sh)")


def _same(got, ref) -> None:
    assert got is not None
    assert got[2] == ref[2]
    for a, b in zip(got[:2], ref[:2]):
        assert a.dtype == b.dtype and a.shape == b.shape
        assert np.array_equal(a.view(np.uint64), b.view(np.uint64))


def _levels(rng, n: int, top: float, f32: bool = False) -> np.ndarray:
    e = np.concatenate([[0.0], np.sort(rng.uniform(0.0, top, n))])
    return e.astype(np.float32) if f32 else e


@needs_build
@pytest.mark.parametrize("seed", range(6))
def test_random_grids_bitwise(seed) -> None:
    rng = np.random.default_rng(seed)
    for _ in range(400):
        n = int(rng.integers(0, 40))
        edis = _levels(rng, n, float(rng.uniform(0.01, 6.0)), f32=bool(rng.integers(2)))
        nlast = int(rng.integers(0, n + 3))  # past len(edis): the zero padding
        exmax = float(rng.choice([rng.uniform(0.0, 25.0), edis[min(nlast, len(edis) - 1)],
                                  -1.0, 0.0]))
        nbins = int(rng.integers(0, 60))
        aix = int(rng.integers(0, 14))
        etot = None if rng.integers(2) else float(rng.uniform(0.0, 30.0))
        args = (edis, nlast, exmax, nbins, aix, True, etot)
        _same(exgrid_nx2.excitation_energies(*args, NUMEX), _excitation_energies(*args))
        _same(excitation_energies(*args), _excitation_energies(*args))


@needs_build
def test_every_aix_branch_and_stop() -> None:
    edis = np.array([0.0, 0.3, 0.7, 1.1, 1.9])
    for aix in range(0, 12):
        for exmax in (0.2, 0.3, 1.0, 1.9, 2.5, 17.3):
            for nlast in range(0, 6):
                args = (edis, nlast, exmax, 37, aix, True, 12.5)
                _same(exgrid_nx2.excitation_energies(*args, NUMEX), _excitation_energies(*args))


@needs_build
def test_log_bins_fall_back_unless_eb_zero() -> None:
    edis = np.array([0.0, 0.3, 0.7])
    assert exgrid_nx2.excitation_energies(edis, 2, 9.0, 30, 3, False, None, NUMEX) is None
    _same(excitation_energies(edis, 2, 9.0, 30, 3, False, None),
          _excitation_energies(edis, 2, 9.0, 30, 3, False, None))
    # Ex(NL) = 0: the equidistant formula, in C
    args = (np.array([0.0]), 0, 9.0, 30, 3, False, None)
    _same(exgrid_nx2.excitation_energies(*args, NUMEX), _excitation_energies(*args))


@needs_build
def test_past_numex_falls_back() -> None:
    edis = np.linspace(0.0, 1.0, 120)
    assert exgrid_nx2.excitation_energies(edis, 119, 5.0, 40, 2, True, None, NUMEX) is None
    with pytest.raises(ValueError):
        _excitation_energies(edis, 119, 5.0, 40, 2, True, None)


def test_lever_off(monkeypatch) -> None:
    monkeypatch.setenv("HF_NX2_EXGRID", "0")
    assert exgrid_nx2.excitation_energies(np.array([0.0, 1.0]), 1, 5.0, 10, 2, True, None,
                                          NUMEX) is None
    _same(excitation_energies(np.array([0.0, 1.0]), 1, 5.0, 10, 2, True, None),
          _excitation_energies(np.array([0.0, 1.0]), 1, 5.0, 10, 2, True, None))
