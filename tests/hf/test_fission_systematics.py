"""ACTLD5: `barsierk` must run in `real(sgl)`, as barsierk.f90 declares it.

The Sierk barrier fit sums 49 `barcof` terms of order 1e6 down to a barrier of order 1 MeV.
About six digits cancel, so single-precision rounding of the partial sums moves the answer by
0.1-0.6 MeV -- it is part of the number TALYS reports, not noise around it. Evaluating the same
sum in float64 gave Am-307 1.482 MeV against TALYS's 1.745 MeV, and on the neutron-rich
actinides whose barrier sits near the neutron separation energy that 0.26 MeV is a factor ~1e3
in the Hill-Wheeler transmission and therefore in (n,gamma).
See docs/results/actld5-sierk-precision.md.

Reference values are the "Height of fission barrier" line of TALYS-2.25's own `fis<ZZZ><AAA>.txt`
(`fismodel 6` falls through to `fismodelalt 3` = Sierk for every nucleus below).
"""

from __future__ import annotations

import pytest
import torch

from physics.hf.core.tensors import DTYPE
from physics.hf.fission.systematics import barsierk

# (Z, A) of the compound nucleus -> the "Height of fission barrier" line of TALYS-2.25's own
# fis<ZZZ><AAA>.txt, from `n + <target>` at 3.5 keV with `strength 8 / ldmodel 5 / outfission y`.
# Every entry is a nucleus for which `fismodel 6` has no barrier and TALYS falls through to
# `fismodelalt 3` = Sierk; nuclei with tabulated barriers (U-239, Cf-250, Am-247, Hs-272) never
# reach `barsierk` and are covered by gate A-fis instead.
TALYS_BARRIER = {
    (95, 307): 1.745375e00,
    (97, 219): 1.115768e00,
    (97, 315): 1.026806e00,
    (98, 316): 9.613953e-01,
    (107, 248): 1.184540e-01,
    (107, 254): 3.760223e-01,
    (108, 251): -5.949783e-01,  # Sierk goes negative out here; TALYS stores it as it comes
    (109, 257): 1.663284e-01,
    (110, 260): 1.003761e-01,
}


@pytest.mark.parametrize(("za", "ref"), sorted(TALYS_BARRIER.items()))
def test_barsierk_matches_talys_single_precision(za: tuple[int, int], ref: float) -> None:
    bfis, _egs, _lbar0 = barsierk(za[0], za[1], 0)
    assert bfis.dtype == DTYPE
    # TALYS prints seven significant digits; the port must land inside that, not merely near it.
    assert float(bfis) == pytest.approx(ref, abs=1.0e-6, rel=1.0e-6)


def test_barsierk_is_not_the_float64_value() -> None:
    """The float64 evaluation of the same sum is a different number, and a wrong one.

    Guards the regression directly: a port that "cleans up" the precision reintroduces it.
    """
    bfis, _, _ = barsierk(95, 307, 0)
    assert abs(float(bfis) - 1.482277) > 0.2  # the float64 answer
    assert float(bfis) == pytest.approx(1.745375, abs=5.0e-7)


def test_barsierk_outside_validity_returns_zero() -> None:
    """Z or A outside Sierk's fit range leaves all three at zero (barsierk.f90:68-84)."""
    for za in ((18, 40), (112, 290), (95, 100)):
        bfis, egs, lbar0 = barsierk(za[0], za[1], 0)
        assert float(bfis) == 0.0 and float(egs) == 0.0 and float(lbar0) == 0.0
        assert bfis.dtype == DTYPE


def test_barsierk_l0_ground_state_and_lbar0_are_zero() -> None:
    """`il = 0` returns early, as barsierk.f90:92 does (`if (il < 1) return`)."""
    bfis, egs, lbar0 = barsierk(95, 307, 0)
    assert float(bfis) > 0.0
    assert float(egs) == 0.0 and float(lbar0) == 0.0


def test_barsierk_float64_would_change_every_sierk_nucleus() -> None:
    """The shift is not one unlucky nucleus: it is 0.07-0.57 MeV across the Sierk region.

    Recomputing the same `barcof` sum in float64 here (the pre-fix behaviour) and checking that
    it disagrees with TALYS everywhere keeps the test honest about what is being guarded.
    """
    import numpy as np

    from physics.hf.fission.systematics import BARCOF

    cof = np.array(BARCOF, dtype=np.float64)

    def leg(n: int, x: float) -> float:
        pl = [1.0, x]
        for i in range(2, n + 1):
            pl.append((x * (2 * i - 1) * pl[i - 1] - (i - 1) * pl[i - 2]) / i)
        return pl[n]

    for (z, a), ref in TALYS_BARRIER.items():
        pz = [leg(k, z / 100.0) for k in range(7)]
        pa = [leg(k, a / 400.0) for k in range(7)]
        f64 = sum(cof[j][i] * pz[j] * pa[i] for i in range(7) for j in range(7))
        assert abs(f64 - ref) > 0.05, (z, a, f64, ref)


def test_barsierk_no_grad_and_finite() -> None:
    with torch.no_grad():
        for z, a in TALYS_BARRIER:
            bfis, _, _ = barsierk(z, a, 0)
            assert torch.isfinite(bfis)
            assert not bfis.requires_grad
