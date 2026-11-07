"""GRIDTOP (`INCOGNITA_GRIDTOP`, default ON): the outgoing grid reaches 1 MeV above the top energy of every exit.

TALYS's `Elimit = enincmax + S(0,0,k0) + targetE + 1` (grid.f90:120) covers the photon exit only. For a compound
nucleus unbound to some ejectile (I-110: S(alpha) = -3.58 MeV) the fastest alphas are above the grid top, get T = 0,
and how many are lost depends on the run's highest incident energy. So the same (nucleus, energy) differed by grid:
I-109 capture at 20 keV was 6.67 mb as a one-energy run and 6.34 mb with a 20 MeV point (stock TALYS-2.25: 6.664 /
6.338), and with forced pre-equilibrium (the production deck's `preequilibrium y`) 4.95 vs 0.106 mb.

* `emission_limit`: TALYS's value to the bit when no S is negative or the switch is off; raised by -min S otherwise;
* I-109 at 19.82 keV gives the same capture, (n,p) and (n,alpha) on a one-point grid, after a 1 keV point, and with
  a 5 or 20 MeV top, to 1e-6 relative, with the default deck and with `preequilibrium y`;
* with the switch off the one-point run differs from the 20 MeV run (the test bites).
"""

from __future__ import annotations

import os
from pathlib import Path

import numpy as np
import pytest
import torch

TALYS_DIR = Path(os.environ.get("TALYS_DIR", Path.home() / "opt/talys-src"))
needs_structure = pytest.mark.skipif(not (TALYS_DIR / "structure").is_dir(),
                                     reason="TALYS structure/ not installed")

Z, A = 53, 109  # I-109: compound I-110 has S(alpha) = -3.58 MeV, S(p) = 0.04 MeV
E = 0.0198214778  # MeV, a library grid point (19.82 keV)
GRIDS = ((E,), (1.0e-3, E), (E, 5.0), (E, 20.0))
CHANNELS = ("xs000000", "xs010000", "xs000001")  # (n,g), (n,p), (n,a)


@pytest.fixture
def gridtop(monkeypatch):
    """Undo conftest's TALYS-grid pin; yields a setter for the switch."""
    from physics.hf import chartrun

    monkeypatch.delenv("INCOGNITA_GRIDTOP", raising=False)
    chartrun.drop_target_caches()

    def set_on(on: bool):
        if on:
            monkeypatch.delenv("INCOGNITA_GRIDTOP", raising=False)
        else:
            monkeypatch.setenv("INCOGNITA_GRIDTOP", "0")
        chartrun.drop_target_caches()

    yield set_on
    chartrun.drop_target_caches()


def test_emission_limit_rule(gridtop):
    from physics.hf.core.grids import emission_limit

    base = emission_limit(20.0, 7.5, 0.0)
    assert emission_limit(20.0, 7.5, 0.0, s_exits_mev=[0.0, 7.5, 6.0, 9.0, 10.0, 8.0, 3.2]) == base
    raised = emission_limit(20.0, 7.5, 0.0, s_exits_mev=[0.0, 7.5, 6.0, 9.0, 10.0, 8.0, -3.58])
    assert raised == pytest.approx(base + 3.58, abs=1e-5)
    gridtop(False)
    assert emission_limit(20.0, 7.5, 0.0, s_exits_mev=[0.0, 7.5, 6.0, 9.0, 10.0, 8.0, -3.58]) == base


def _at_e(grid, lines: str, monkeypatch) -> np.ndarray:
    from physics.hf import chartrun, engine_c
    from physics.hf.engine import ChainedFull
    from physics.hf.input import fitlib

    if lines:
        monkeypatch.setenv(fitlib.ENV, "lines")
        monkeypatch.setenv(fitlib.ENV_LINES, lines)
    else:
        monkeypatch.delenv(fitlib.ENV, raising=False)
        monkeypatch.delenv(fitlib.ENV_LINES, raising=False)
    fitlib.deactivate()
    chartrun.drop_target_caches()
    try:
        with torch.inference_mode():
            r = engine_c.run(ChainedFull(Z=Z, A=A, declared_energies=grid))
        i = grid.index(E)
        return np.array([float(r.channels_mb[k][i]) for k in CHANNELS])
    finally:
        fitlib.deactivate()
        chartrun.drop_target_caches()


@needs_structure
@pytest.mark.parametrize("lines", ["", "preequilibrium y"])
def test_same_energy_same_answer_on_every_grid(gridtop, monkeypatch, lines):
    torch.set_num_threads(1)
    gridtop(True)
    ref = _at_e(GRIDS[-1], lines, monkeypatch)
    assert np.all(ref > 0), ref
    for g in GRIDS[:-1]:
        got = _at_e(g, lines, monkeypatch)
        np.testing.assert_allclose(got, ref, rtol=1e-6, atol=0.0, err_msg=f"grid {g}, deck {lines!r}")
    gridtop(False)
    talys_one = _at_e((E,), lines, monkeypatch)
    assert abs(talys_one[0] / ref[0] - 1.0) > 0.01, (talys_one, ref)  # the TALYS grid cuts alphas here
