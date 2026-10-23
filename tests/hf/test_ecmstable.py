"""CCNANTHERM: ECIS's relativistic c.m. energy cancels to exactly 0 at 1e-11 MeV for some target
masses (Tb-159), which made the CC grid 0/0. The cancellation-free form is used only there."""
import torch

from physics.hf.ecis import dwba_nx2, solver

M_N, M_TB = 1.00866, 158.92535  # card-rounded masses that cancel to ecm = 0 at 1e-11 MeV


def _old(e, m1, m2):
    """ECIS's expression, in the same torch operations as `channel_kinematics` (torch divides a
    tensor by a scalar through its reciprocal, so `math` can differ by one quantum here)."""
    cm = solver.ECIS_CM_MEV
    t = torch.tensor([e], dtype=torch.float64)
    return float(cm * (torch.sqrt((m1 + m2) ** 2 + 2.0 * m2 * t / cm) - m1 - m2))


def test_ecm_cancellation_replaced_only_where_it_underflows():
    e = torch.tensor([1.0e-11, 1.0e-10, 1.0e-5, 1.0, 30.0], dtype=torch.float64)
    kin = solver.channel_kinematics(e, M_N, M_TB, 0.0, torch.tensor([0.0, 0.058], dtype=torch.float64))
    assert _old(1.0e-11, M_N, M_TB) == 0.0  # the defect this guards
    exact = 1.0e-11 * M_TB / (M_N + M_TB)
    assert abs(float(kin.ecm_mev[0, 0]) / exact - 1.0) < 1e-3
    assert bool(torch.isfinite(kin.k_fm).all()) and float(kin.k_fm[0, 0]) > 0.0
    for i in range(1, 5):  # every non-underflowing row keeps ECIS's own expression bit for bit
        assert float(kin.ecm_mev[i, 0]) == _old(float(e[i]), M_N, M_TB)


def test_dwba_twin_matches_channel_kinematics():
    lev = torch.tensor([0.058], dtype=torch.float64)
    kin = solver.channel_kinematics(torch.tensor([1.0e-11], dtype=torch.float64), M_N, M_TB, 0.0,
                                    torch.cat([torch.zeros(1, dtype=torch.float64), lev]))
    *_, ecm1 = dwba_nx2._kinematics(1.0e-11, M_N, M_TB, 0.0, lev.numpy())
    assert abs(ecm1 / float(kin.ecm_mev[0, 0]) - 1.0) < 1e-12
