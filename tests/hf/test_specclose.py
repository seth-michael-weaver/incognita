"""SPECCLOSE (THEORYFIX_U7SPEC, INCOGNITA_SPECCLOSE, output only): the shipped spectra integrate to the booked flux."""

import numpy as np

from physics.hf import specout
from physics.hf.emission import binspec


def _grid():
    eg = np.array([0.0, 0.001, 0.01, 0.1, 0.2, 0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0])
    eb, et, de = binspec._edges(eg, len(eg) - 1)
    return eg, eb, et, de


def test_switch_default_off(monkeypatch):
    monkeypatch.setenv("INCOGNITA_SPECCLOSE", "0")
    assert not binspec.specclose_on()
    monkeypatch.setenv("INCOGNITA_SPECCLOSE", "1")
    assert binspec.specclose_on()


def test_close_binary_integrals():
    eg, eb, et, de = _grid()
    ib, ie, nd = 1, 12, 10
    rng = np.random.default_rng(1)
    xsemis = np.zeros(len(eg)); xsemis[ib:nd + 1] = rng.uniform(1, 5, nd + 1 - ib)
    xspre = np.zeros(len(eg)); xspre[ib:nd + 2] = rng.uniform(0.1, 1, nd + 2 - ib)
    xsgr = np.zeros(len(eg)); xsgr[5:9] = [0.1, 0.3, 0.2, 0.05]  # collective continuum, mb/MeV
    res = np.zeros(len(eg)); res[6:8] = [2.0, 1.0]  # resonance part, mb per bin
    cut = 0.3
    petot = float(np.sum(xspre[ib:nd] * de[ib:nd])) + 0.4
    e2, p2, g2 = binspec.close_binary(xsemis, xspre, xsgr + res, de, et, ib, ie, nd, cut, petot, res)
    cc = float(np.sum(xsemis[ib:nd + 1] * de[ib:nd + 1]) - xsemis[nd] * cut)  # binemission's emissum convention
    assert np.isclose(np.sum(e2 * de), cc, rtol=1e-13)
    assert np.isclose(np.sum(p2 * de), petot, rtol=1e-13) and np.all(p2[nd + 1:] == 0.0)
    assert np.isclose(np.sum(g2 * de), np.sum(xsgr * de) + res.sum(), rtol=1e-13)
    # remainder < 0: the whole PE spectrum is scaled to the booked total
    _, p3, _ = binspec.close_binary(xsemis, xspre, xsgr, de, et, ib, ie, nd, None, 0.5 * petot)
    assert np.isclose(np.sum(p3 * de), 0.5 * petot, rtol=1e-13)


def test_discrete_parent_emission_closes():
    eg, eb, et, de = _grid()
    E = len(eg)
    ex = np.array([0.0, 1.0, 3.5, 4.0, 5.0, 6.0, 7.0])  # parent: levels 0..3 (Nlast 3), bins 4..6
    dex = np.array([0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0])
    exd = np.array([0.0, 0.5, 1.5, 2.5])  # daughter: levels 0..1 (Nlast 1), bins 2..3
    dexd = np.array([0.0, 0.0, 1.0, 1.0])
    mc = np.zeros((7, 4)); mpe = np.zeros((7, 4))
    mc[2, 0], mc[3, 1], mc[3, 2] = 4.0, 2.0, 1.0  # discrete parents above S (=1.0)
    mpe[3, 0] = 0.5
    rec = dict(ex=ex, dex=dex, nlast=3, maxex=6, sep=np.array([0, 1.0, 0, 0, 0, 0, 0.0]),
               types={1: dict(mc=mc, mpe=mpe, ex=exd, dex=dexd, nlast=1, maxex=3)})
    eb_ = {t: 1 for t in range(7)}; ee_ = {t: E - 1 for t in range(7)}
    c, m = specout.discrete_parent_emission(rec, eg, eb, et, de, eb_, ee_, 1e-12)
    assert np.isclose(np.sum((c[1] + m[1]) * de), mc[1:4].sum() + mpe[1:4].sum(), rtol=1e-13)
    assert np.isclose(np.sum(m[1] * de), 0.5, rtol=1e-13)
    # continuum parents to a ground-state-only daughter (Nlast 0): the cells compemission skips
    t6 = dict(mc=np.zeros((7, 1)), mpe=np.zeros((7, 1)), ex=np.array([0.0]), dex=np.array([0.0]), nlast=0, maxex=0)
    t6["mc"][4:7, 0] = [1.0, 2.0, 3.0]
    rec2 = dict(rec, types={6: t6})
    c, m = specout.discrete_parent_emission(rec2, eg, eb, et, de, eb_, ee_, 1e-12)
    assert np.isclose(np.sum(c[6] * de), 6.0, rtol=1e-13)
