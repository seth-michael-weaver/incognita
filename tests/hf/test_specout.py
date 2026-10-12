"""SPECOUT: outgoing spectra / angular distributions / DDX recorded from the engine, OUTPUT ONLY (physics/hf/specout.py,
physics/hf/specang.py, native/specout.c, the nx_walk / nx_target / walk_nucleus sinks)."""

import math
import os

import numpy as np
import pytest
import torch

from physics.hf import specang, specout


def _record(rng, maxex=12, nl=3, drows=(14, 10, 9)):
    ex = np.linspace(0.0, 8.0, maxex + 1)
    rec = dict(zc=0, nc=1, maxex=maxex, nlast=nl, ex=ex, dex=np.full(maxex + 1, 0.6), sep=np.array([0, 7.5, 9.0, 11, 12, 13, 6.0]),
               types={}, lines_only=False)
    for t, dr in zip((0, 1, 6), drows):
        mc = rng.uniform(0, 5, (maxex + 1, dr)) * (rng.uniform(0, 1, (maxex + 1, dr)) > 0.3)
        mpe = mc * rng.uniform(0, 0.3, mc.shape) if t == 1 else np.zeros_like(mc)
        e = ex if t == 0 else np.linspace(0, 6, dr)
        rec["types"][t] = dict(mc=mc, mpe=mpe, ex=e[:dr], dex=np.full(dr, 0.6), nlast=2, maxex=dr - 1)
    return rec


def test_compemission_c_equals_python():
    rng = np.random.default_rng(3)
    eg = np.concatenate([[0.0], np.geomspace(0.001, 20.0, 80)])
    from physics.hf.emission.binspec import _edges

    eb, et, de = _edges(eg, len(eg) - 1)
    ebegin = {t: 1 for t in range(7)}
    eend = {t: len(eg) - 2 for t in range(7)}
    rec = _record(rng)
    if specout._solib() is None:
        pytest.skip("libspecout.so not built (scripts/build_specout_native.sh)")
    c = specout.compemission(rec, eg, eb, et, de, ebegin, eend, 1e-9)
    p = specout.compemission_py(rec, eg, eb, et, de, ebegin, eend, 1e-9)
    for a, b in zip(c, p):  # noqa: B905
        assert np.abs(a - b).max() <= 1e-12 * max(np.abs(b).max(), 1e-30)
    # flux closure: what a mother bin hands to bins above the daughter's Nlast lands on the grid
    assert c[0].sum() > 0 and c[1].sum() > 0 and p[1].sum() > 0


def test_kalbach_normalisation_and_smyers():
    th = np.linspace(0.0, 180.0, 3601)
    for a in (0.0, 0.3, 2.0, 12.0):
        k = specang.kalbach_shape(np.array([a]), th)[0]
        integ = 2 * math.pi * np.trapezoid(k * np.sin(np.radians(th)), np.radians(th))
        assert integ == pytest.approx(1.0, rel=1e-5)
    sm = specang.smyers(26, 57)  # n + Fe-56
    assert 7.0 < sm[1] < 13.0 and sm[6] < sm[2] + 10.0  # Myers-Swiatecki: S_n of Fe-57 ~ 7.6-10 MeV
    a = specang.kalbach_a(1, 1, 14.0, np.array([1.0, 10.0]), sm)
    assert a[1] > a[0] > 0
    assert specang.kalbach_a(1, 0, 14.0, np.array([1.0]), sm)[0] == 0.0


@pytest.mark.skipif(not os.environ.get("TALYS_DIR"), reason="needs TALYS_DIR (structure data)")
def test_switch_is_output_only_and_closes(monkeypatch):
    """Fe-56 at 14.1 MeV: every engine array bit-identical with INCOGNITA_SPECOUT on/off; the shape-elastic Legendre
    integral equals the engine's shape elastic; compound level Legendre normalisation ratio = 1."""
    from physics.hf import engine_c, warmrun
    from physics.hf.engine import ChainedFull

    torch.set_num_threads(1)
    e = (float(np.float32(14.1)),)

    def run(on):
        if on:
            monkeypatch.setenv("INCOGNITA_SPECOUT", "1")
        else:
            monkeypatch.delenv("INCOGNITA_SPECOUT", raising=False)
        monkeypatch.setenv("INCOGNITA_SPECOUT_F32", "0")
        specout.reset()
        cas = warmrun.new_cascade(26, 56, e)
        with torch.inference_mode():
            res = engine_c.run(injection=ChainedFull(Z=26, A=56, declared_energies=e, cascade=cas))
        return warmrun.result_arrays(res), specout.pack(26, 56)

    off, _ = run(False)
    on, so = run(True)
    assert set(off) == set(on)
    for k in off:
        assert np.array_equal(off[k], on[k]), k
    assert "so_n_cont" in so and so["so_n_cont"].sum() > 0
    el = so["so_elastic_xs"][0]
    shape = el[0] - el[1]
    assert 4 * math.pi * so["so_shape_leg"][0, 0] == pytest.approx(shape, rel=1e-9)
    r = so["so_comp_ratio"][0]
    assert np.allclose(r[np.isfinite(r)], 1.0, rtol=1e-9)
    assert not str(so["so_errors"])


def test_nubar_wahl_formula():
    """nubarWahl.f90 (TALYS's default-run prompt nubar, totalxs.f90:124): n + U-235 (CN U-236, Bn = 6.545 MeV) at
    thermal -> 2.435 (evaluations: 2.43); the slope 0.145 / MeV above."""
    nu0 = specang.nubar_wahl(92, 236, 2.53e-8, 6.545)
    assert nu0 == pytest.approx(2.286 + 0.145 * (6.545 - 11.47 + 0.166 * 92 * 92 / 236 + 2.53e-8), rel=1e-12)
    assert 2.40 < nu0 < 2.47
    assert specang.nubar_wahl(92, 236, 1.0, 6.545) - nu0 == pytest.approx(0.145 * (1.0 - 2.53e-8), rel=1e-9)


@pytest.mark.parametrize("ti0,tin", [(0, 4), (3, 7), (7, 1)])
def test_legendre_fast_equals_ceang(ti0, tin):
    from physics.hf.compound import ceang

    rng = np.random.default_rng(0)
    blocks = []
    for J2 in range((ti0 + 1) % 2, 30, 2):
        inn = [(l, jj) for jj in range(abs(J2 - ti0), J2 + ti0 + 1, 2) for l in range(12) if jj in (2 * l - 1, 2 * l + 1)]
        out = [(l, jj) for jj in range(abs(J2 - tin), J2 + tin + 1, 2) for l in range(12) if jj in (2 * l - 1, 2 * l + 1)]
        if inn and out:
            blocks.append({"J2": J2, "l_in": [x[0] for x in inn], "j2_in": [x[1] for x in inn],
                           "levels": {1: {"l_out": [x[0] for x in out], "j2_out": [x[1] for x in out],
                                          "M": rng.uniform(0, 1, (len(inn), len(out)))}}})
    a = ceang.legendre({"blocks": blocks}, 1, ti0, tin, 20)
    b = specang.legendre_fast({"blocks": blocks}, 1, ti0, tin, 20)
    assert np.abs(a - b).max() <= 1e-14 * np.abs(a).max()
