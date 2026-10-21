"""IDEA_EXACTFIS: exact per-hump fission transmission (physics/hf/fission/wkb.py)."""
import numpy as np
import pytest
import torch

from physics.hf.fission import wkb as W


def test_exact_matches_hill_wheeler_on_parabola():
    mu, w, v0, half = 0.25, 1.0, 6.0, 16.0
    x = np.linspace(-half, half, 321)
    beta = np.concatenate([[0.0], x])
    v = np.concatenate([[0.0], v0 - 0.5 * mu * w**2 * x**2])
    m = np.concatenate([[0.0], np.full_like(x, mu)])
    es = np.array([3.0, 5.5, 6.0, 6.5])
    te = W._t_exact_vec(beta, v, m, 1, len(x), es)
    hw = 1.0 / (1.0 + np.exp(2 * np.pi * (v0 - es) / w))
    assert np.all(np.abs(np.log(te / hw)) < 0.03)


@pytest.mark.parametrize("Z,A", [(92, 239), (94, 240)])
def test_off_bitwise_and_on_moves(Z, A, monkeypatch):
    monkeypatch.delenv("INCOGNITA_EXACTFIS", raising=False)
    p = W.read_hfbpath(Z, A, 6)
    if p is None:
        pytest.skip("no fm6 path")
    base = W.wkb(Z, A, p, fismodel=6, nbinswkb=40)
    off = W.wkb(Z, A, p, fismodel=6, nbinswkb=40, exactfis=False)
    assert torch.equal(base.twkb, off.twkb)
    on = W.wkb(Z, A, p, fismodel=6, nbinswkb=40, exactfis=True)
    assert not torch.equal(base.twkb, on.twkb)
    assert float(on.twkb.max()) <= 1.0
    monkeypatch.setenv("INCOGNITA_EXACTFIS", "1")
    env = W.wkb(Z, A, p, fismodel=6, nbinswkb=40)
    assert torch.equal(env.twkb, on.twkb)
