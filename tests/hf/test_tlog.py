"""LOGTINT: log-T Lagrange is exact for a pure exponential, falls back to TALYS's linear pol2 on a zero node, and the
fine reference grid keeps the coarse nodes."""
import numpy as np

from physics.hf.compound import tlog


def _w(xa, xb, xc, x):
    return ((x - xb) * (x - xc) / ((xa - xb) * (xa - xc)), (x - xa) * (x - xc) / ((xb - xa) * (xb - xc)),
            (x - xa) * (x - xb) / ((xc - xa) * (xc - xb)))


def test_exponential_exact_and_linear_overshoots():
    xa, xb, xc, x = 1.0, 1.4, 1.8, 1.63  # densprepare centres the triple: Eout lies in [Eb, Ec], where pol2 overshoots
    f = lambda e: np.exp(-12.0 * (2.0 - e) ** 1.0)  # x ~e^(4.8) over the triple
    w1, w2, w3 = _w(xa, xb, xc, x)
    lg = tlog.lagr_log(w1, w2, w3, f(xa), f(xb), f(xc))
    lin = w1 * f(xa) + w2 * f(xb) + w3 * f(xc)
    assert abs(lg / f(x) - 1) < 1e-12
    assert lin > f(x)


def test_zero_node_keeps_linear():
    w1, w2, w3 = _w(0.0, 0.5, 1.0, 0.7)
    a, b, c = np.array([0.0, 1e-3]), np.array([1e-4, 1e-2]), np.array([1e-3, 1e-1])
    out = tlog.lagr_log(w1, w2, w3, a, b, c)
    assert out[0] == w1 * a[0] + w2 * b[0] + w3 * c[0]
    assert out[1] != w1 * a[1] + w2 * b[1] + w3 * c[1]


def test_fine_grid_contains_nodes():
    eg = np.array([0.0, 0.1, 0.3, 0.7, 1.5])
    ef, left = tlog.fine_grid(eg, 4)
    assert np.allclose(ef[:: tlog.REFINE], eg)
    assert left[-1] == 4


def test_logit_exact_both_limits_and_fallback():
    """TLOGIT: logit-Lagrange is exact for the WKB form T = 1/(1+exp(2K)) with K linear in E, below AND above the barrier."""
    xa, xb, xc, x = 1.0, 1.4, 1.8, 1.63
    w1, w2, w3 = _w(xa, xb, xc, x)
    for k0 in (-9.0, -0.5, 0.0, 3.0, 25.0):  # deep sub-barrier .. saturated
        f = lambda e: 1.0 / (1.0 + np.exp(-(k0 + 6.0 * (e - 1.4))))
        v = tlog.lagr_logit(w1, w2, w3, f(xa), f(xb), f(xc))
        assert abs(v / f(x) - 1) < 1e-12, k0
        assert tlog.lagr_log(w1, w2, w3, f(xa), f(xb), f(xc), "l") == v
    one = tlog.lagr_logit(w1, w2, w3, np.array([1.0, 0.0]), np.array([0.9, 0.1]), np.array([0.8, 0.2]))
    assert one[0] == w1 * 1.0 + w2 * 0.9 + w3 * 0.8 and one[1] == w1 * 0.0 + w2 * 0.1 + w3 * 0.2


def test_logit_torch_matches_numpy():
    import torch

    w1, w2, w3 = _w(1.0, 1.4, 1.8, 1.55)
    a, b, c = np.array([1e-30, 0.3, 0.97, 0.0]), np.array([1e-25, 0.6, 0.99, 0.2]), np.array([1e-20, 0.8, 0.999, 0.4])
    n = tlog.lagr_logit(w1, w2, w3, a, b, c)
    t = tlog.lagr_log_torch(*(torch.tensor(v, dtype=torch.float64) for v in (w1, w2, w3, a, b, c)), kind="l").numpy()
    assert np.allclose(n, t, rtol=1e-12, atol=0)
