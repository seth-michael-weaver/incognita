"""OPEN4: the two accuracy defects OPEN3M left classified.

Gate: `docs/results/hf-open4.md`.

D -- binary.f90's `sfactor` (the pre-equilibrium spin shape) is zeroed once per run
(strucinitial.f90:484) and overwritten only where a bin holds more than `popepsA`, so a bin keeps
the spin shape of an EARLIER incident energy. `engine.ChainedFull.cases` seeded the multiple
emission from a fresh `BinaryState` at every energy; actinide (n,g) above 10 MeV came out 1-6 %
low because the compound nucleus's high bins then decayed with the Wigner fallback shape.

E -- compnorm.f90:163-166: a coupled-channels target takes the compound flux from its own sum over
`Tjlinc` plus `xscoupled` and does not renormalise to `xsreacinc`. ECIS runs at the card-rounded
energy while pi/k^2 is taken at `Einc`, so TALYS's keV nonelastic (`xsreacinc - xscompel`) moves
by up to 1 % around its capture. The chained path always took the spherical branch.
"""

from __future__ import annotations

import numpy as np
import pytest
import torch

from physics.hf.compound.normalization import compound_formation
from physics.hf.core.tensors import DTYPE

# CHART1's grid (`hf_ccfast_bench.energies`) as the port declares it, and CHART1's TALYS column
CHART1_E = tuple(float(np.float32(x)) for x in (
    1.0e-3, 1.684108e-3, 2.836221e-3, 4.776502e-3, 8.044147e-3, 1.354721e-2, 2.281498e-2,
    3.842289e-2, 6.470830e-2, 1.089758e-1, 1.835270e-1, 3.090794e-1, 5.205231e-1, 8.766172e-1,
    1.476318, 2.486280, 4.187164, 7.051638, 11.87572, 20.0))


def _run(Z, A, energies, revert=None):
    import physics.hf.emission.feeding as F
    import physics.hf.engine as E
    from physics.hf.emission.binary import BinaryState

    saved = (E.binary, F.Cascade.xscoupled)
    try:
        if revert == "d":
            b = E.binary
            E.binary = lambda inp, state=None, device=None: b(inp, BinaryState(), device)
        if revert == "e":
            F.Cascade.xscoupled = lambda self, e: None
        with torch.inference_mode():
            return E.run(injection=E.ChainedFull(Z=Z, A=A, declared_energies=CHART1_E,
                                                 energies=energies))
    finally:
        E.binary, F.Cascade.xscoupled = saved


def test_coupled_branch_is_compnorm():
    """compnorm.f90:163-166 with norm = 1: flux = sum_T + xscoupled - direct - preeq - GR, and
    CNfactor * sum_T is that flux whatever `xsreacinc` says."""
    tjl = torch.tensor([[0.4, 0.4, 0.0], [0.0, 2e-3, 2.1e-3]], dtype=DTYPE)
    args = (tjl, torch.tensor(0.05, dtype=DTYPE), 0, 1, 1, 1)
    add = [torch.tensor(v, dtype=DTYPE) for v in (5.0, 2.0, 1.0)]
    cc = compound_formation(*args, torch.tensor(1.0e4, dtype=DTYPE), *add, spherical=False,
                            xscoupled_mb=torch.tensor(3.0, dtype=DTYPE))
    assert float(cc.xs_flux_mb) == pytest.approx(float(cc.xs_reacsum_mb) + 3.0 - 8.0, rel=1e-14)
    assert float(cc.cf_ratio * cc.xs_reacsum_mb) == pytest.approx(float(cc.xs_flux_mb), rel=1e-14)
    sph = compound_formation(*args, torch.tensor(1.0e4, dtype=DTYPE), *add)
    assert float(sph.xs_flux_mb) == pytest.approx(1.0e4 - 8.0, rel=1e-14)


def test_d_sfactor_reaches_the_multiple_emission():
    """U-235 (n,g) at 11.88 MeV, computed as a one-energy subset (which walks the declared prefix
    for `sfactor`): CHART1's TALYS value within 1e-3, and a fresh state per energy reproduces the
    old 1.6e-2 deficit."""
    e = (CHART1_E[-2],)
    got = float(_run(92, 235, e).channels_mb["xs000000"][0])
    talys = 1.288375  # features/hf_chart1/cells.parquet, U-235 (n,g) at 11.87572 MeV
    assert abs(np.log(got / talys)) < 1e-3
    old = float(_run(92, 235, e, revert="d").channels_mb["xs000000"][0])
    assert np.log(old / talys) < -1e-2


def test_e_coupled_nonelastic_at_kev():
    """W-184 nonelastic at 13.5 and 22.8 keV, where TALYS's sits 3-4 mb away from its capture:
    within 1e-3 of CHART1's TALYS column, and outside 1e-2 on the spherical branch."""
    e = CHART1_E[5:7]
    talys = np.array([354.8496, 282.7852])  # features/hf_chart1/cells.parquet
    got = _run(74, 184, e).totals_mb["nonelastic"].numpy()
    assert np.abs(np.log(got / talys)).max() < 1e-3
    old = _run(74, 184, e, revert="e").totals_mb["nonelastic"].numpy()
    assert np.abs(np.log(old / talys)).min() > 1e-2
