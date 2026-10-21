"""FTGLOBAL / FTPROMO: the E1/M1 ftable override becomes the global f(beta2) form; `ftglobal n` restores the deck line."""
import numpy as np
import pytest
import torch

from physics.hf.gamma import ftglobal as FG
from types import SimpleNamespace


def Options(**kw):
    return SimpleNamespace(**kw)


def _ov(e1=0.0, m1=0.0, e2=0.0):
    a = np.zeros((2, 4))
    a[1, 1], a[0, 1], a[1, 2] = e1, m1, e2
    return {"ftable": a}


def test_replaces_nonzero_e1_m1_only(monkeypatch):
    monkeypatch.delenv("INCOGNITA_FTGLOBAL", raising=False)
    monkeypatch.delenv("INCOGNITA_HEAVYMACS2", raising=False)
    g = FG.table()[(26, 56)]
    out = FG.apply(Options(), 26, 56, _ov(e1=1.7, m1=0.0, e2=2.0))["ftable"]
    assert out[1, 1] == g and out[0, 1] == 0.0 and out[1, 2] == 2.0


def test_off_and_untabulated_and_grad_untouched(monkeypatch):
    monkeypatch.delenv("INCOGNITA_FTGLOBAL", raising=False)
    ov = _ov(e1=1.7)
    assert FG.apply(Options(ftglobal="n"), 26, 56, ov) is ov
    monkeypatch.setenv("INCOGNITA_FTGLOBAL", "0")
    assert FG.apply(Options(), 26, 56, ov) is ov
    monkeypatch.delenv("INCOGNITA_FTGLOBAL")
    assert FG.apply(Options(), 8, 29, ov) is ov  # no beta2 in the feature table: deck line kept
    t = torch.tensor(ov["ftable"], requires_grad=True)
    assert FG.apply(Options(), 26, 56, {"ftable": t})["ftable"] is t
    assert FG.apply(Options(), 26, 56, {}) == {}


def test_table_is_global_form():
    t = FG.table()
    assert len(t) > 6000 and all(v > 0 for v in t.values())


def test_heavymacs2_default_on_and_domain(monkeypatch):
    """HEAVYMACS2 (default ON): `heavymacs2 n` = previous production; ON sets the global value to 1 only for 60<=Z<=83, |beta2|>=0.2."""
    monkeypatch.delenv("INCOGNITA_FTGLOBAL", raising=False)
    monkeypatch.delenv("INCOGNITA_HEAVYMACS2", raising=False)
    dom = FG.hm2_domain()
    assert (70, 174) in dom and (82, 208) not in dom and (26, 56) not in dom
    g = FG.table()[(70, 174)]
    assert FG.apply(Options(heavymacs2="n"), 70, 174, _ov(e1=1.7, m1=0.9))["ftable"][1, 1] == g
    assert FG.apply(Options(), 70, 174, _ov(e1=1.7, m1=0.9))["ftable"][1, 1] == 1.0
    out = FG.apply(Options(heavymacs2="y"), 70, 174, _ov(e1=1.7, m1=0.9))["ftable"]
    assert out[1, 1] == 1.0 and out[0, 1] == 1.0
    monkeypatch.setenv("INCOGNITA_HEAVYMACS2", "1")
    assert FG.apply(Options(), 70, 174, _ov(e1=1.7))["ftable"][1, 1] == 1.0
    assert FG.apply(Options(), 26, 56, _ov(e1=1.7))["ftable"][1, 1] == FG.table()[(26, 56)]
    assert FG.apply(Options(ftglobal="n"), 70, 174, _ov(e1=1.7))["ftable"][1, 1] == 1.7  # only acts where FTGLOBAL acts
