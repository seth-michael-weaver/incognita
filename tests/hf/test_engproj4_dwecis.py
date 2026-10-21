"""ENGPROJ4 DWECIS: ECIS's DWBA numerics (insh modified Numerov + tlnc matching) give correctly normalised waves,
converge to the plain-Numerov port on a fine grid, and are scoped to d/t/h."""
import torch

from physics.hf.core.tensors import DTYPE
from physics.hf.ecis.dwba import _normalise, distorted_waves, ecis_distorted_waves
from physics.hf.ecis.solver import CDTYPE
from physics.hf.omp.schrodinger import coulomb_functions


def _case(h, n, k=1.2, eta=0.6, depth=40.0):
    """A Woods-Saxon + Coulomb-like well in the u'' = (f - k^2) u convention, l = 0..8, nodes 0..n+1."""
    l = torch.arange(9, dtype=torch.int64)
    r = h * torch.arange(0, n + 2, dtype=DTYPE)
    r[0] = h
    ws = -(depth + 8.0j) / (1.0 + torch.exp((r - 5.0) / 0.65))
    coul = 2.0 * k * eta / r  # point-Coulomb tail in units of k^2
    f = (l * (l + 1)).to(DTYPE)[:, None] / r[None, :] ** 2 + (0.05 * ws + coul)[None, :]
    return f.to(CDTYPE), l


def test_free_waves_are_minus_2i_F():
    """No nuclear potential: S = 1, so H^- - S H^+ = -2i F_l(eta, kr) at every node."""
    k, eta, h, n = 1.2, 0.6, 0.02, 1000
    l = torch.arange(9, dtype=torch.int64)
    r = h * torch.arange(0, n + 2, dtype=DTYPE)
    r[0] = h
    f = ((l * (l + 1)).to(DTYPE)[:, None] / r[None, :] ** 2 + (2.0 * k * eta / r)[None, :]).to(CDTYPE)
    u = ecis_distorted_waves(f, torch.tensor([k * k], dtype=DTYPE), torch.tensor([k], dtype=DTYPE),
                             torch.tensor([eta], dtype=DTYPE), l, h, n)[0]
    for i in (300, 600, 1000):
        F = coulomb_functions(torch.tensor([eta], dtype=DTYPE), torch.tensor([k * i * h], dtype=DTYPE), 8)[0][0]
        assert torch.allclose(u[:, i], -2.0j * F.to(CDTYPE), rtol=0, atol=2e-5 * float(F.abs().max()) + 1e-12)


def test_fine_grid_matches_plain_numerov_port():
    """On a fine grid both integrators converge to the same normalised solution (ECIS's error is O(h^4))."""
    k, eta, h, n = 1.2, 0.6, 0.0125, 1600
    f, l = _case(h, n, k, eta)
    k2 = torch.tensor([k * k], dtype=DTYPE)
    ue = ecis_distorted_waves(f, k2, torch.tensor([k], dtype=DTYPE), torch.tensor([eta], dtype=DTYPE), l, h, n)
    up = _normalise(distorted_waves(f[:, :n + 1], k2, l, h, n), f[:, :n + 1], k2, torch.tensor([eta], dtype=DTYPE),
                    l, h)
    scale = float(up.abs().max())
    assert float((ue - up).abs().max()) < 1e-5 * scale


def test_scope():
    import os

    from physics.hf.projectile import dwba_ecis_numerics

    old = os.environ.pop("INCOGNITA_DWECIS", None)
    try:
        assert [dwba_ecis_numerics(p) for p in range(7)] == [False, False, False, True, True, True, False]
        os.environ["INCOGNITA_DWECIS"] = "1"
        assert all(dwba_ecis_numerics(p) for p in range(1, 7))
    finally:
        os.environ.pop("INCOGNITA_DWECIS", None)
        if old is not None:
            os.environ["INCOGNITA_DWECIS"] = old
