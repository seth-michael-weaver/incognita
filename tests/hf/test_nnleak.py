"""NNLEAK: the Egamma^3-weighted continuum -> discrete Rboundary of the initial CN top bin."""

from __future__ import annotations

import numpy as np

from physics.hf.compound import nnleak


class _Opt:
    nnleak = True


def test_top_bin_only_for_the_initial_compound_nucleus_continuum_top(monkeypatch):
    monkeypatch.delenv("INCOGNITA_NNLEAK", raising=False)
    assert nnleak.top_bin(_Opt(), 0, 0, 40, 10) == 40
    assert nnleak.top_bin(_Opt(), 0, 1, 40, 10) == -1  # residual nucleus: TALYS
    assert nnleak.top_bin(_Opt(), 0, 0, 10, 10) == -1  # top bin is a discrete level: TALYS
    off = _Opt(); off.nnleak = False
    assert nnleak.top_bin(off, 0, 0, 40, 10) == -1
    monkeypatch.setenv("INCOGNITA_NNLEAK", "0")
    assert nnleak.top_bin(_Opt(), 0, 0, 40, 10) == -1


def test_open_fraction_is_the_quartic_and_eout_the_cubic_weighted_mean():
    dex, ex0plus = 0.2, 7.0
    exm = np.array([6.95, 6.9, 6.8])
    part = np.ones(3, bool)
    rb = (ex0plus - exm) / dex
    eo = 0.5 * (ex0plus + exm) - 6.5
    rb2, eo2 = nnleak.adjust(rb, eo, part, ex0plus, exm, dex, True)
    q = (ex0plus - exm) / dex
    np.testing.assert_allclose(rb2, q ** 4)
    # mean of u over [0, d] with weight u^3 is 0.8 d below the top (TALYS: 0.5 d)
    np.testing.assert_allclose(eo2, ex0plus - 0.8 * (ex0plus - exm) - 6.5)
    rb3, eo3 = nnleak.adjust(rb, eo, part, ex0plus, exm, dex, False)
    assert rb3 is rb and eo3 is eo  # unselected rows untouched
    s_rb, s_eo = nnleak.scalar(rb[1], eo[1], ex0plus, exm[1], dex)
    assert np.isclose(s_rb, rb2[1]) and np.isclose(s_eo, eo2[1])
