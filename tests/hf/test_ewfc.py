"""EWCC: the Engelbrecht-Weidenmueller transform of Moldauer's WFC (physics/hf/compound/ewfc.py).

1. P diagonal -> the transform is Moldauer exactly (<= 1e-12).
2. Sum rule: summed over every exit the EW population of incident a is sum_alpha |U_alpha a|^2 F_alpha, F_alpha the
   Moldauer outflow of eigen-channel alpha (so it is sigma_CN whenever Moldauer's own outflow is p_alpha).
3. Reciprocity: sigma_ab = sigma_ba on the transformed channels.
4. GOE Monte Carlo (3 channels, correlated couplings, Kawano et al. PRC 94 (2016) 014612): EW + Moldauer reproduces the
   ensemble fluctuation cross sections; Moldauer on the diagonal P alone does not.
"""

import numpy as np
import pytest
import torch

from physics.hf.compound import ewfc, wfc
from physics.hf.core.tensors import DTYPE


def _nodes():
    return wfc.gauss_laguerre()


def _moldauer_matrix(t, rest_log, st, gamw):
    """sigma_ab * st = T_a T_b W_ab for every pair (plain Moldauer, the diagonal reference)."""
    x, w = _nodes()
    t = torch.as_tensor(t, dtype=DTYPE)
    nu = wfc.degrees_of_freedom(t, st, 1)
    f = 2 * t / (st * nu)
    den = 1 + x[:, None] * f[None, :]
    lg = torch.log1p(x[:, None] * f[None, :])
    expo = gamw * x / st
    pm = w * w * torch.exp(x) * torch.exp(rest_log + (-nu * 0.5 * lg).sum(1)) * torch.exp(-expo)
    wm = torch.einsum("m,ma,mb->ab", pm, 1 / den, 1 / den) + torch.diag((pm[:, None] * (2 / nu)[None, :] / den**2).sum(0))
    return (t[:, None] * t[None, :] * wm).numpy(), pm, f


def _random_case(n=4, seed=1):
    rng = np.random.default_rng(seed)
    a = rng.normal(size=(n, n)) + 1j * rng.normal(size=(n, n))
    q, _ = np.linalg.qr(a)
    p = rng.uniform(0.05, 0.9, n)
    pmat = q @ np.diag(p) @ q.conj().T
    return pmat, p


def _ew_full(pmat, rest_log, st, gamw, n_cc=None):
    x, w = _nodes()
    n = pmat.shape[0]
    p, v = ewfc.eigen(pmat, n if n_cc is None else n_cc)
    out = np.zeros((n, n))
    for a in range(n):
        _, _, sig = ewfc.ew_populations(x, w, st, rest_log, gamw, p, v, [a], None, 1)
        out[a] = sig.numpy()
    return out, p, v


def test_diagonal_is_moldauer():
    st = torch.tensor(3.7, dtype=DTYPE)
    gamw = torch.tensor(0.05, dtype=DTYPE)
    t = np.array([0.6, 0.3, 0.1, 0.02])
    rest = torch.zeros(32, dtype=DTYPE) - 0.1 * _nodes()[0]
    ref, _, _ = _moldauer_matrix(t, rest, st, gamw)
    got, _, _ = _ew_full(np.diag(t).astype(complex), rest, st, gamw)
    assert np.max(np.abs(got - ref) / ref) <= 1e-12


def test_sum_rule_and_reciprocity():
    pmat, p = _random_case()
    st = torch.tensor(float(p.sum()) + 1.3, dtype=DTYPE)  # 1.3 = other channels outside the transform
    gamw = torch.tensor(0.2, dtype=DTYPE)
    x, w = _nodes()
    t_out = torch.tensor([0.4, 0.5, 0.4], dtype=DTYPE)  # the non-transformed exits (sum 1.3, gamma separate: st is a total)
    nu_o = wfc.degrees_of_freedom(t_out, st, 1)
    rest = (-nu_o * 0.5 * torch.log1p(x[:, None] * (2 * t_out / (st * nu_o))[None, :])).sum(1)
    full, pe, v = _ew_full(pmat, rest, st, gamw)
    assert np.max(np.abs(full - full.T)) <= 1e-12 * np.abs(full).max()
    # outflow of each eigen-channel alpha (Moldauer in the eigen space)
    ref, pm, f = _moldauer_matrix(pe, rest, st, gamw)
    fo = 2 * t_out / (st * nu_o)
    for a in range(pmat.shape[0]):
        pm_, hm, sig = ewfc.ew_populations(x, w, st, rest, gamw, pe, v, [a], None, 1)
        out_other = float((pm_ * hm)[:, None].mul(t_out[None, :] / (1 + x[:, None] * fo[None, :])).sum()) \
            + float((pm_ * hm).sum()) * float(gamw)
        total = float(sig.sum()) + out_other
        a2 = np.abs(v[a]) ** 2
        f_alpha = ref.sum(1) + np.array([
            float((pm * pe[k] / (1 + x * f[k]))[:, None].mul(t_out[None, :] / (1 + x[:, None] * fo[None, :])).sum())
            + float((pm * pe[k] / (1 + x * f[k])).sum()) * float(gamw) for k in range(len(pe))])
        assert abs(total - float(a2 @ f_alpha)) <= 1e-12 * total


def test_identity_cells_outside_block_untouched():
    pmat, p = _random_case(3, seed=5)
    big = np.zeros((4, 4), dtype=complex)
    big[:3, :3] = pmat
    big[3, 3] = 0.25
    st = torch.tensor(2.0, dtype=DTYPE)
    gamw = torch.tensor(0.0, dtype=DTYPE)
    rest = torch.zeros(32, dtype=DTYPE)
    full, _, v = _ew_full(big, rest, st, gamw, n_cc=3)
    assert np.allclose(np.abs(v[3]), [0, 0, 0, 1])
    assert np.max(np.abs(full - full.T)) <= 1e-12 * np.abs(full).max()


def _goe_mc(n_lev=160, lam=3, n_real=300, n_e=120, seed=7, mix=None):
    """<S>, and <|S_ab - <S_ab>|^2> from the Mahaux-Weidenmueller S-matrix of GOE resonances with correlated couplings."""
    rng = np.random.default_rng(seed)
    mix = np.array([[1.0, 0.0, 0.0], [0.9, 0.44, 0.0], [0.6, 0.5, 0.62]]) if mix is None else mix
    strength = np.array([0.9, 0.5, 0.25])
    s_acc = np.zeros((lam, lam), complex)
    s2_acc = np.zeros((lam, lam))
    cnt = 0
    for _ in range(n_real):
        a = rng.normal(size=(n_lev, n_lev))
        h = (a + a.T) / np.sqrt(2 * n_lev)  # semicircle radius ~ 2, mean spacing at E=0: d = pi/n_lev
        d = np.pi / n_lev
        w = rng.normal(size=(n_lev, lam)) @ (mix * np.sqrt(strength)[:, None]).T * np.sqrt(d) / np.pi
        heff = h - 1j * np.pi * w @ w.T
        lamv, phi = np.linalg.eig(heff)
        phiinv = np.linalg.inv(phi)
        left = w.T @ phi
        right = phiinv @ w
        es = np.linspace(-0.25, 0.25, n_e)
        for e in es:
            s = np.eye(lam) - 2j * np.pi * (left / (e - lamv)[None, :]) @ right
            s_acc += s
            s2_acc += np.abs(s) ** 2
            cnt += 1
    sm = s_acc / cnt
    fl = s2_acc / cnt - np.abs(sm) ** 2
    return sm, fl


def test_goe_monte_carlo():
    """Channel correlations |P_ab|/sqrt(P_aa P_bb) 0.58/0.11/0.48: EW + Moldauer rms 2.6 % (max 3.9 %) from the GOE ensemble,
    Moldauer on diag(P) rms 16 % (max 30 %) -- the size and ordering Kawano et al. 2016 report."""
    sm, fl = _goe_mc(n_real=400)
    pmat = np.eye(3) - sm @ sm.conj().T
    pmat = 0.5 * (pmat + pmat.conj().T)
    st = torch.tensor(float(np.real(np.trace(pmat))), dtype=DTYPE)
    gamw = torch.tensor(0.0, dtype=DTYPE)
    rest = torch.zeros(32, dtype=DTYPE)
    ew, _, _ = _ew_full(pmat, rest, st, gamw)
    ew = ew / float(st)
    diag, _, _ = _moldauer_matrix(np.real(np.diag(pmat)).copy(), rest, st, gamw)
    diag = diag / float(st)
    err_ew = ew / fl - 1
    err_d = diag / fl - 1
    assert np.abs(err_ew).max() < 0.05, (ew, fl)
    assert np.sqrt(np.mean(err_d**2)) > 3 * np.sqrt(np.mean(err_ew**2)), (diag, ew, fl)


def test_switch(monkeypatch):
    from types import SimpleNamespace

    monkeypatch.delenv(ewfc.ENV, raising=False)
    assert not ewfc.enabled() and not ewfc.enabled(SimpleNamespace(ewtransform="n"))
    assert ewfc.enabled(SimpleNamespace(ewtransform="y"))
    monkeypatch.setenv(ewfc.ENV, "y")
    assert ewfc.enabled() and ewfc.enabled(SimpleNamespace(ewtransform="n"))
    from physics.hf.input.defaults import default_options

    assert default_options(74, 184).ewtransform == "n"
