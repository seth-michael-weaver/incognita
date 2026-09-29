"""FISSC2: the incident coupled-channels radial step below `INCIDENT_REFINE_EMAX_MEV`.

The port integrates ECIS's own grid with a plain matrix Numerov where ECIS uses the modified one,
so at keV energies a deformed target's `sigma_tot` / `sigma_reac` sit ~1e-3 off TALYS
(docs/results/hf-fissc2.md).  These pin the fix's three properties: the off-switch is bitwise the
old behaviour, the policy touches only the energies it claims to, and the refined answer is the
one closer to stock TALYS.

CCNUMEROV turned the policy OFF by default (`INCIDENT_REFINE = 1`): the modified Numerov fixes
the cause at its source, so refining ECIS's own step now moves the answer away from TALYS rather
than towards it.  These still gate the lever's behaviour, and the one that claims the refined
solve is closer to TALYS is run where that is true -- with the plain Numerov, the scheme FISSC2
measured.  Its converse is `tests/hf/test_ccnumerov.py`.

Task: FISSC2. Acceptance test: G-FISSC2 (docs/results/hf-fissc2.md).
"""

from __future__ import annotations

import math

import pytest
import torch

from physics.hf.core.tensors import DTYPE
from physics.hf.ecis import incident as I
from physics.hf.ecis.reference import coupled_band

# CHART1's first three energies, and its stock-TALYS `total.tot` there for U-232 (colltype R),
# the worst of MERGEC's fissioning-29 slice (`features/hf_chart1/cells.parquet`).
E_KEV = (0.001, 0.001684, 0.002836)
U232_TALYS_TOTAL_MB = (37621.30, 31966.20, 27604.40)


@pytest.fixture(scope="module")
def u232():
    return coupled_band(92, 232)


def _solve(Z, A, band, e_mev, refine_default, emax):
    old = (I.INCIDENT_REFINE, I.INCIDENT_REFINE_EMAX_MEV)
    I.INCIDENT_REFINE, I.INCIDENT_REFINE_EMAX_MEV = refine_default, emax
    I._SOLVED.clear()
    try:
        ich, _ = I.incident_coupled(None, Z, A, torch.tensor(e_mev, dtype=DTYPE), band)
    finally:
        I.INCIDENT_REFINE, I.INCIDENT_REFINE_EMAX_MEV = old
        I._SOLVED.clear()
    return ich


def test_refine_axis_applies_only_below_the_threshold():
    e = torch.tensor([0.001, 0.05, 0.0501, 20.0], dtype=DTYPE)
    assert I._refine_axis(e, 1).tolist() == [1, 1, 1, 1], "CCNUMEROV: off by default now"
    assert I._refine_axis(e, 4).tolist() == [4, 4, 4, 4], "an explicit refine wins everywhere"
    old = I.INCIDENT_REFINE
    I.INCIDENT_REFINE = 2
    try:
        assert I._refine_axis(e, 1).tolist() == [2, 2, 1, 1], "HF_INC_REFINE=2 is the on-switch"
    finally:
        I.INCIDENT_REFINE = old


def test_the_off_switch_is_bitwise_the_unrefined_solve(u232):
    off = _solve(92, 232, u232, E_KEV, 1, 0.05)
    plain = _solve(92, 232, u232, E_KEV, 2, 0.0)  # no energy is below the threshold
    for f in ("sigma_tot_mb", "sigma_reac_mb", "sigma_shape_el_mb"):
        assert torch.equal(getattr(off, f), getattr(plain, f)), f


def test_above_the_threshold_nothing_moves(u232):
    e = (0.520523, 1.476318)
    on = _solve(92, 232, u232, e, 2, 0.05)
    off = _solve(92, 232, u232, e, 1, 0.05)
    assert torch.equal(on.sigma_tot_mb, off.sigma_tot_mb)
    assert torch.equal(on.sigma_reac_mb, off.sigma_reac_mb)


def test_the_refined_keV_solve_is_the_one_closer_to_talys(u232, monkeypatch):
    # FISSC2's property is a property OF THE PLAIN NUMEROV, which is what it measured: the
    # refinement was compensating a truncation error of the wrong sign.  CCNUMEROV removed that
    # error instead, so on the default (modified) scheme refining is no longer an improvement --
    # see `tests/hf/test_ccnumerov.py::test_the_modified_step_is_the_one_closer_to_talys`.
    monkeypatch.setenv("HF_CC_MODNUM", "0")
    off = _solve(92, 232, u232, E_KEV, 1, 0.05)
    on = _solve(92, 232, u232, E_KEV, 2, 0.05)
    for i, t in enumerate(U232_TALYS_TOTAL_MB):
        r_off = abs(math.log(float(off.sigma_tot_mb[i]) / t))
        r_on = abs(math.log(float(on.sigma_tot_mb[i]) / t))
        assert r_off > 1.0e-3, f"E={E_KEV[i]}: the defect this fixes should be there at refine 1"
        assert r_on < r_off / 2.0, f"E={E_KEV[i]}: {r_on:.2e} not well inside {r_off:.2e}"
        assert r_on < 1.0e-3


def test_the_split_batch_is_the_per_energy_solve(u232):
    """The policy splits one call into a refined and an unrefined group, as `soswitch` already
    does; `sum_blocks` converges each energy on its own, so the grouping changes no value."""
    e = (0.001, 0.008044, 0.520523)
    batched = _solve(92, 232, u232, e, 2, 0.05)
    for i, x in enumerate(e):
        one = _solve(92, 232, u232, (x,), 2, 0.05)
        for f in ("sigma_tot_mb", "sigma_reac_mb", "sigma_shape_el_mb"):
            a, b = float(getattr(one, f)[0]), float(getattr(batched, f)[i])
            assert abs(a / b - 1.0) < 1.0e-12, f"{f} at {x} MeV: {a} vs {b}"
