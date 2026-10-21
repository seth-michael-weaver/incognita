"""ENGADJ: energy-local parameter bumps (physics/hf/eadj.py). Parser, shapes, default-off."""

import numpy as np
import pytest

from physics.hf import eadj


def test_parse_forms():
    b = eadj.parse_line("eadj v1adjust n tal 1 6 3 1.05")
    assert (b.target, b.sel, b.shape, b.args) == ("v1adjust", (1,), "tal", (1.0, 6.0, 3.0, 1.05))
    b = eadj.parse_line("eadj ctable 92 239 gau 5.0 1.0 1.3")
    assert (b.target, b.sel, b.shape) == ("ctable", (92, 239), "gau")
    b = eadj.parse_line("eadj vfiscor 92 239 tal 5 9 6.5 0.97")
    assert b.sel == (92, 239)
    for bad in ("eadj v1adjust x tal 1 6 3 1.1", "eadj foo n tal 1 6 3 1.1", "eadj v1adjust n tal 1 6 9 1.1",
                "eadj a 92 239 gau 1 0 1.1", "eadj a 92 239 box 1 2 3"):
        with pytest.raises(ValueError):
            eadj.parse_line(bad)


def test_tal_shape_matches_adjust_f90():
    """adjust.f90 (npow 4): 1 at/outside Ea, Eb; D at Em; smooth (zero slope) at the window edges."""
    b = eadj.parse_line("eadj a 26 57 tal 2 10 4 1.2")
    e = np.array([0.0, 2.0, 4.0, 10.0, 12.0])
    np.testing.assert_allclose(eadj.bump_values([b], e), [1, 1, 1.2, 1, 1], atol=1e-15)

    def talys(E, Ea, Eb, Em, D):  # adjust.f90 statement for statement
        if E <= Ea or E >= Eb:
            return 1.0
        Db = (D - 1.0) * (1.0 + 0.5**4)
        if E <= Em:
            C = Ea + 0.5 * (Em - Ea)
            return 1.0 + Db * (E - Ea) ** 4 / ((E - Ea) ** 4 + (C - Ea) ** 4)
        C = Em + 0.5 * (Eb - Em)
        return 1.0 + Db * (Eb - E) ** 4 / ((Eb - E) ** 4 + (C - Eb) ** 4)

    es = np.linspace(0, 12, 241)
    np.testing.assert_allclose(eadj.bump_values([b], es), [talys(x, 2, 10, 4, 1.2) for x in es], rtol=0, atol=1e-14)
    d = np.diff(eadj.bump_values([b], es))
    assert np.max(np.abs(d)) < 0.02  # no jump anywhere


def test_gau_and_combination():
    g = eadj.parse_line("eadj fe1 92 239 gau 5 1 1.5")
    np.testing.assert_allclose(eadj.bump_values([g], [5.0]), [1.5])
    np.testing.assert_allclose(eadj.bump_values([g], [6.0]), [1 + 0.5 * np.exp(-0.5)])
    g2 = eadj.parse_line("eadj fe1 92 239 gau 5 1 0.8")
    np.testing.assert_allclose(eadj.bump_values([g, g2], [5.0]), [1.5 * 0.8])
    p = eadj.parse_line("eadj pshift 92 239 gau 5 1 1.3")
    np.testing.assert_allclose(eadj.bump_shift([p, p], [5.0]), [0.6])
    assert eadj.scalar([p], 5.0) == pytest.approx(0.3)


def test_default_off(monkeypatch):
    for k in ("INCOGNITA_TALYS_FIT_LINES", "INCOGNITA_TALYS_FIT_LINES_FILE", "INCOGNITA_TALYS_FIT"):
        monkeypatch.delenv(k, raising=False)
    assert eadj.active() == () and not eadj.on()
    assert eadj.omp_factor("v1adjust", 1, 3.0) == 1.0


# ------------------------------------------------------------------ the engine hooks (function level, bumps injected)
def _inject(monkeypatch, *lines):
    bs = tuple(eadj.parse_line(x) for x in lines)
    monkeypatch.setattr(eadj, "active", lambda: bs)
    return bs


def test_omp_wide_bump_is_the_flat_factor_and_window_is_local(monkeypatch):
    """A Gaussian much wider than the grid is the flat `d1adjust n D` factor; outside a narrow window nothing moves."""
    import torch

    from physics.hf.input.defaults import default_options, default_params
    from physics.hf.omp.parameters import omp_parameters

    o = default_options(26, 56)
    e = torch.tensor([0.5, 2.0, 3.0, 4.0, 12.0], dtype=torch.float64)
    p0 = default_params(26, 56, o)
    base = omp_parameters(26, 30, 1, e, p0, o)
    flat = omp_parameters(26, 30, 1, e, default_params(26, 56, o, overrides={"d1adjust": torch.tensor(
        [1.0, 1.1, 1.0, 1.0, 1.0, 1.0, 1.0], dtype=torch.float64)}), o)
    _inject(monkeypatch, "eadj d1adjust n gau 3 1e6 1.1")
    wide = omp_parameters(26, 30, 1, e, p0, o)
    np.testing.assert_allclose(wide.wd_mev.numpy(), flat.wd_mev.numpy(), rtol=1e-10)
    np.testing.assert_allclose(wide.v_mev.numpy(), base.v_mev.numpy(), rtol=1e-12)
    _inject(monkeypatch, "eadj d1adjust n tal 2.5 3.5 3 1.1")
    loc = omp_parameters(26, 30, 1, e, p0, o)
    r = loc.wd_mev.numpy() / base.wd_mev.numpy()
    np.testing.assert_allclose(r[[0, 1, 3, 4]], 1.0, rtol=1e-12)
    assert r[2] == pytest.approx(1.1, rel=1e-12)
    pr = omp_parameters(26, 30, 2, e, p0, o)  # a neutron bump leaves the proton potential alone
    _inject(monkeypatch)
    np.testing.assert_allclose(pr.wd_mev.numpy(), omp_parameters(26, 30, 2, e, p0, o).wd_mev.numpy(), rtol=1e-12)


def test_psf_bump_same_on_torch_numpy_and_c(monkeypatch):
    """f_E1 x factor(Egamma) on all three strength evaluators; f_M1 untouched by an fe1 bump."""
    from dataclasses import replace

    import torch

    import physics.hf.compound.dens_reference as dr
    from physics.hf.compound.psf_fast import fstrength_np
    from physics.hf.compound.psf_nx2 import tgam_points
    from physics.hf.gamma.strength import fstrength_gp

    gp0, _ = dr._gamma_parameters(26, 56)
    b = eadj.parse_line("eadj fe1 26 57 gau 6 1.5 1.4")
    gp = replace(gp0, eadj_e1=(b,))
    eg = np.linspace(0.05, 14.0, 281)
    fac = eadj.bump_values([b], eg)
    t0 = fstrength_gp(gp0, 5.0, torch.from_numpy(eg), 1, 1).numpy()
    t1 = fstrength_gp(gp, 5.0, torch.from_numpy(eg), 1, 1).numpy()
    np.testing.assert_allclose(t1, t0 * fac, rtol=1e-14)
    n1 = fstrength_np(gp, 5.0, eg, 1, 1)
    np.testing.assert_allclose(n1, t1, rtol=1e-12)
    np.testing.assert_array_equal(fstrength_np(gp, 5.0, eg, 0, 1), fstrength_np(gp0, 5.0, eg, 0, 1))
    c = tgam_points(gp, gp.gammax, 5.0, eg, 1.0, 1.0)
    if c is not None:
        np.testing.assert_allclose(c[:, 1, 1], eg**3 * n1, rtol=1e-12)
        c0 = tgam_points(gp0, gp0.gammax, 5.0, eg, 1.0, 1.0)
        np.testing.assert_array_equal(c[:, 1, 0], c0[:, 1, 0])


def test_ld_bumps(monkeypatch):
    """a: ignatyuk x factor; ctable: rho x exp(dc sqrt(E - pt)); pshift: rho(E) -> rho(E - dP(E)); other nuclei untouched."""
    import torch

    import physics.hf.compound.dens_reference as dr
    from physics.hf.density import models
    from physics.hf.density.parameters import ignatyuk

    ld = dr._ld_of(26, 56, 26, 56)[0]
    e = torch.linspace(0.5, 20.0, 79, dtype=torch.float64)
    a0, r0 = ignatyuk(ld, e).numpy(), models.densitytot(ld, e).numpy()
    ba = _inject(monkeypatch, "eadj a 26 56 gau 8 2 1.1")
    np.testing.assert_allclose(ignatyuk(ld, e).numpy(), a0 * eadj.bump_values(ba, e.numpy()), rtol=1e-12)
    bc = _inject(monkeypatch, "eadj ctable 26 56 gau 8 2 1.3")
    pt = float(ld.ptable_mev[0])
    want = r0 * np.exp(eadj.bump_shift(bc, e.numpy()) * np.sqrt(np.clip(e.numpy() - pt, 0, None)))
    np.testing.assert_allclose(models.densitytot(ld, e).numpy(), want, rtol=1e-12)
    bp = _inject(monkeypatch, "eadj pshift 26 56 gau 8 2 1.5")
    ee = e - torch.from_numpy(eadj.bump_shift(bp, e.numpy()))
    _inject(monkeypatch)
    want = models.densitytot(ld, ee).numpy()
    _inject(monkeypatch, "eadj pshift 26 56 gau 8 2 1.5")
    np.testing.assert_allclose(models.densitytot(ld, e).numpy(), want, rtol=1e-12)
    _inject(monkeypatch, "eadj pshift 26 57 gau 8 2 1.5")  # another nucleus
    np.testing.assert_array_equal(models.densitytot(ld, e).numpy(), r0)


def test_fission_nodes_interpolate_and_keep_base(monkeypatch):
    """vfiscor bump on U-239: node nuclei reproduce direct builds; off-node scale interpolates to < 2e-3 in T_f; energies
    outside the window are the base bit for bit."""
    from physics.hf.fission.chain import fission_chain

    _inject(monkeypatch, "eadj vfiscor 92 239 gau 7 1 0.95")
    ch = fission_chain(92, 238)
    nod = ch.nodes(92, 239)
    assert nod is not None and nod[0][-1] == 1.0 and nod[0][0] == pytest.approx(0.95, abs=1e-6)
    ex = np.array([4.0, 6.5, 7.0, 7.4, 12.0, 25.0])
    vals = [ch._target_arrays(92, 239, n, float(x), 1.0)[0] for n in nod[2] for x in ex]
    K = len(nod[2])
    per_node = [np.stack(vals[k * len(ex):(k + 1) * len(ex)]) for k in range(K)]
    got = ch.combine(92, 239, nod, per_node, ex)
    base = per_node[nod[3]]
    sv, _ = eadj.fission_factors(92, 239, ex)
    out = sv == 1.0
    np.testing.assert_array_equal(got[out], base[out])
    # off-node check at 7.4 MeV: a direct build at that exact scale
    from physics.hf.fission.chain import _scaled_params  # noqa: F401  (the node builder)

    i = 3
    direct = ch._target_arrays(92, 239, ch._build(92, 239, float(sv[i]), 1.0), float(ex[i]), 1.0)[0]
    m = direct > 1e-12
    assert np.max(np.abs(np.log(got[i][m] / direct[m]))) < 2e-3


def test_engnan_hat_weights_and_overflow_guard(monkeypatch):
    """ENGNAN: clustered node sets make Lagrange weights explode (exp overflow -> NaN tot_fission); hat weights are a
    partition of unity in [0, 1], exact at nodes, and fission_interp with them stays inside the node values."""
    nv = (0.9814160072250211, 0.9907080036125105, 1.0, 1.000100666811843, 1.0002013336236861)
    x = np.array([0.9814160072250211, 0.985, 0.997, 1.0, 1.00015, 1.0002013336236861])
    w = eadj.hat(nv, x)
    assert np.all(w >= 0) and np.all(w <= 1) and np.allclose(w.sum(1), 1.0)
    np.testing.assert_array_equal(eadj.hat(nv, np.array(nv)), np.eye(5))
    assert np.abs(eadj.lagrange(nv, np.array([0.997]))).max() > 100  # the defect
    wl = eadj.fission_weights(nv, nv, np.array([0.997]), np.array([0.986]), bilin=False)
    v = [np.array([[np.exp(30.0 * np.sign(wk)), 46.0]]) for wk in wl[0]]  # widths 1e-13 .. 1e13 where the weights alternate
    lg = eadj.fission_interp(v, wl)
    assert not np.all(np.isfinite(lg))
    hb = eadj.fission_interp(v, eadj.fission_weights(nv, nv, np.array([0.997]), np.array([0.986]), bilin=True))
    st = np.stack(v)
    assert np.all(np.isfinite(hb)) and np.all(hb >= st.min(0) * (1 - 1e-12)) and np.all(hb <= st.max(0) * (1 + 1e-12))
    monkeypatch.setenv("INCOGNITA_EADJFIS", "bilin")
    np.testing.assert_array_equal(eadj.fission_weights(nv, nv, x, x), eadj.fission_weights(nv, nv, x, x, bilin=True))
    monkeypatch.delenv("INCOGNITA_EADJFIS")
    np.testing.assert_array_equal(eadj.fission_weights(nv, nv, x, x), eadj.fission_weights(nv, nv, x, x, bilin=False))
