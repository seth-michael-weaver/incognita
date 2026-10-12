"""FISSBAR2: INCOGNITA_FISBAR_LD per-barrier keys. OFF = rejected (default runs cannot carry them); ON = fission-only,
set/multiply exactly one barrier's Params cell. Stock-TALYS agreement: development notes"""
import pytest

from physics.hf.density import overrides as ov


def test_off_rejects(monkeypatch):
    monkeypatch.delenv("INCOGNITA_FISBAR_LD", raising=False)
    with pytest.raises(KeyError):
        ov.fit_params([("ctable@1", 94, 240, 0.5)])


def test_on_is_fission_only(monkeypatch):
    monkeypatch.setenv("INCOGNITA_FISBAR_LD", "1")
    fit = ov.fit_params([("ctable@1", 94, 240, 0.5), ("aadjust", 94, 240, 1.1), ("fisbaradjust@2", 94, 240, 1.05)])
    assert {e[0] for e in ov.fission_entries(fit)} == {"ctable@1", "fisbaradjust@2"}
    assert [e[0] for e in ov.without_fission(fit)] == ["aadjust"]


def test_on_sets_one_cell(monkeypatch):
    monkeypatch.setenv("INCOGNITA_FISBAR_LD", "1")
    from physics.hf.input.defaults import PARAM_SPECS, default_options, default_params
    o = default_options(94, 239)
    p = default_params(94, 239, o)
    assert ov.with_fission_adjust(p, o, ()) is p
    q = ov.with_fission_adjust(p, o, (("ctable@2", 94, 240, 0.7), ("fisbaradjust@1", 94, 240, 1.1)))
    zix, nix = o.Zinit - 94, o.Ninit - 146
    sp = PARAM_SPECS["ctable"]
    t0, t1 = p.values["ctable"], q.values["ctable"]
    i = (zix + sp.offsets[0], nix + sp.offsets[1], 2 + sp.offsets[2])
    assert float(t1[i]) == 0.7
    d = (t0 != t1).nonzero()
    assert len(d) == 1
    fb0, fb1 = p.values["fisbaradjust"], q.values["fisbaradjust"]
    assert ((fb0 != fb1).sum()) == 1
