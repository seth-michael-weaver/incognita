"""TS2FREEZE: `fists2` (env INCOGNITA_FIS_TS2) = SADDLEPAIR's TS2 even-even saddle K-band transition states, default OFF.
OFF must be identical to the parent; ON touches only even-even fissioning nuclides (hbstates.ee heads, fecont = 28/sqrt(A) rounded
to 1 keV on every barrier). Stock-TALYS agreement (hbstate y + hbtransfile): development notes"""
import torch

from physics.hf.fission.parameters import fission_parameters, fists2_on
from physics.hf.input.defaults import default_options, default_params


def _fp(Z, A, monkeypatch, env=None, kw=None):
    if env is None:
        monkeypatch.delenv("INCOGNITA_FIS_TS2", raising=False)
    else:
        monkeypatch.setenv("INCOGNITA_FIS_TS2", env)
    o = default_options(92, 235, overrides=kw)
    return o, fission_parameters(Z, A, o, default_params(92, 235, o))


def test_default_off(monkeypatch):
    o, fp = _fp(92, 236, monkeypatch)
    assert not fists2_on(o)
    assert all(fp.headband[i].n == 0 for i in range(1, 4))
    assert float(fp.fecont_mev.abs().sum()) == 0.0


def test_env_and_keyword(monkeypatch):
    o, fp = _fp(92, 236, monkeypatch, env="1")
    assert fists2_on(o)
    fec = round(28.0 / 236**0.5, 3)
    for i in range(1, fp.nfisbar + 1):
        assert float(fp.fecont_mev[i]) == fec
    assert [fp.headband[i].n for i in range(1, 3)] == [8, 4]
    assert fp.rotational[1].n > fp.headband[1].n
    o, _ = _fp(92, 236, monkeypatch, env="1", kw={"fists2": "n"})
    assert not fists2_on(o)
    o, fp2 = _fp(92, 236, monkeypatch, kw={"fists2": "y"})
    assert fists2_on(o)
    assert torch.equal(fp2.fecont_mev, fp.fecont_mev)


def test_odd_untouched(monkeypatch):
    for Z, A in ((92, 235), (91, 233), (91, 234)):
        _, off = _fp(Z, A, monkeypatch)
        _, on = _fp(Z, A, monkeypatch, env="1")
        assert torch.equal(off.fecont_mev, on.fecont_mev)
        assert all(on.headband[i].n == 0 for i in range(1, 4))
        assert torch.equal(off.fbarrier_mev, on.fbarrier_mev)


def test_barriers_unchanged(monkeypatch):
    _, off = _fp(92, 234, monkeypatch)
    _, on = _fp(92, 234, monkeypatch, env="1")
    assert torch.equal(off.fbarrier_mev, on.fbarrier_mev)
    # the WKB width is not bitwise repeatable across calls in one process even with the switch OFF (OFF vs OFF differs by 9e-16,
    # pre-existing); run-level bit identity is checked against the SADDLELD S0 cache in development notes
    assert torch.allclose(off.fwidth_mev, on.fwidth_mev, rtol=1e-12, atol=0)
