"""BINQUAD: `binquad n|y` (env INCOGNITA_BINQUAD), population-weighted in-bin quadrature of the emission
(native/binquad.h, compound/prepare.binquad_nodes, Gauss sub-points of the mother bins in nx_walk)."""
from dataclasses import replace

import numpy as np
import pytest

from physics.hf.compound.prepare import binquad_centroid, binquad_nodes, binquad_slope
from physics.hf.core import grids
from physics.hf.input.defaults import Options


def test_off_by_default(monkeypatch):
    monkeypatch.delenv(grids.BINQUAD_ENV, raising=False)
    o = Options(26, 56, 1)
    assert o.binquad == "n" and not grids.binquad_mode(o) and grids.binquad_sub(o) == 1


def test_on_from_environment(monkeypatch):
    monkeypatch.setenv(grids.BINQUAD_ENV, "y")
    assert grids.binquad_mode(Options(26, 56, 1))


def test_bad_value():
    with pytest.raises(ValueError):
        grids.binquad_mode(replace(Options(26, 56, 1), binquad="maybe"))


def test_params():
    o = replace(Options(26, 56, 1), binquad="y", binquads=3, binquadm=-1.0, binquadq=2)
    assert grids.binquad_params(o) == (2, -1.0, 1.0, 3) and grids.binquad_sub(o) == 3


def _brute(u0, u1, y0, y1, alpha, beta, f, n=1501):
    """mass(eps > 0) / mass and the g-weighted mean of f on eps > 0, on a fine (u, y) grid."""
    u = np.linspace(u0, u1, n) if u1 > u0 else np.array([u0])
    y = np.linspace(y0, y1, n) if y1 > y0 else np.array([y0])
    U, Y = np.meshgrid(u, y, indexing="ij")
    w = np.exp(alpha * (U - 0.5 * (u0 + u1)) + beta * (Y - 0.5 * (y0 + y1)))
    e = U - Y
    acc = e > 0
    return w[acc].sum() / w.sum(), (w[acc] * f(e[acc])).sum() / w[acc].sum()


@pytest.mark.parametrize("u0,u1,y0,y1,alpha,beta", [
    (10.0, 10.0, 9.2, 9.6, 0.0, 2.0),    # point mother (primary, binquadm -1, sub-points)
    (10.0, 10.0, 9.8, 10.3, 0.0, 1.5),   # point mother, residual bin straddling eps = 0
    (9.8, 10.2, 9.0, 9.3, 0.0, 0.0),     # two bins, uniform: the exact trapezoid
    (9.8, 10.2, 9.7, 10.0, 0.7, 2.0),    # two bins, tilted, straddling eps = 0
    (9.8, 10.2, 9.9, 9.9, 1.0, 0.0),     # a discrete level from a bin
])
def test_nodes_match_brute_force(u0, u1, y0, y1, alpha, beta):
    f = lambda e: np.sqrt(e) * e  # noqa: E731  a T_l(eps)-like convex rise
    es, ws, rb = binquad_nodes(u0, u1, y0, y1, alpha, beta, 4)
    rb_b, fb = _brute(u0, u1, y0, y1, alpha, beta, f)
    assert abs(rb - rb_b) < 2e-3
    assert np.all(es > 0) and abs(ws.sum() - 1.0) < 1e-12
    assert abs((ws * f(es)).sum() / fb - 1.0) < 3e-3


def test_both_points_keep_talys():
    assert binquad_nodes(10.0, 10.0, 9.0, 9.0, 0.0, 0.0, 3) is None


def test_inaccessible_bin():
    es, ws, rb = binquad_nodes(10.0, 10.0, 10.2, 10.5, 0.0, 1.0, 2)
    assert rb == 0.0 and es.size == 0


def test_slope_of_an_exponential_density():
    ex = np.linspace(1.0, 9.0, 17)
    dex = np.full_like(ex, 0.5)
    rho = np.zeros((17, 41, 2))
    rho[:, 3, 1] = np.exp(1.7 * ex) * dex
    assert abs(binquad_slope(rho, ex, dex, 2, 17, 8) - 1.7) < 1e-9
    assert binquad_slope(rho, ex, dex, 8, 17, 5) == 0.0  # a discrete row


def test_centroid():
    assert binquad_centroid(0.0, 0.5) == 0.0
    a, w = 2.0, 0.6
    x = np.linspace(-w / 2, w / 2, 200001)
    assert abs(binquad_centroid(a, w) - (x * np.exp(a * x)).sum() / np.exp(a * x).sum()) < 1e-6


def test_native_setters_exist():
    from physics.hf import engine_c
    from physics.hf.native import nativex

    so, ce = nativex.lib(), engine_c.lib()
    if so is None or ce is None:
        pytest.skip("no native build")
    assert hasattr(so, "nx_set_binquad") and hasattr(so, "nx_set_binquad_sub") and hasattr(ce, "ce_set_binquad")
    grids.binquad_sync(Options(26, 56, 1))  # OFF pushes zeros


def test_numpy_widths_refuse():
    from physics.hf.compound.decay_fast import NucleusWidths

    class _C:
        options = replace(Options(26, 56, 1), binquad="y")

    with pytest.raises(RuntimeError, match="binquad"):
        NucleusWidths(_C(), None, None, [1])
