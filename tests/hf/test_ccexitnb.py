"""CCEXITNB: `ccexitnb y` / INCOGNITA_CCEXITNB=1 (default off; its no-fission-channel class rule `ccexitnbnf` is default ON) gives a colltype-R target's first-compound neutron exit to
its discrete NON-band levels the g.s. coupled-channels Tjlinc at Eout. Off / spherical targets / band levels: unchanged."""
import dataclasses

import numpy as np
import pytest

from physics.hf.compound import ccexitnb
from physics.hf.compound.chain import PARN, PARZ, primary_dens_inputs
from physics.hf.compound.prepare import densprepare
from physics.hf.emission.feed_reference import etotal_of
from physics.hf.emission.feeding import Cascade


def _primary(Z, A, e):
    cas = Cascade(Z, A, 20.0, energies=[e])
    inc = cas.incident(e)
    etot = etotal_of(Z, A, 20.0, e, 1)
    st = cas.new_energy(etot, lmaxinc=int(inc.lmax[0]), e_inc_mev=e)
    cas.propagate_exmax(st, 0, 0)
    for t in range(7):
        cas.spec(st, PARZ[t], PARN[t])
    res = densprepare(primary_dens_inputs(cas, st, etot, gammax=cas.options.gammax))
    return cas, etot, res[1], float(cas.spec(st, 0, 0).sep_mev[1])


def test_mode_parsing(monkeypatch):
    for v in ("", "0", "n", "off"):
        monkeypatch.setenv(ccexitnb.ENV, v)
        assert not ccexitnb.enabled()
    monkeypatch.setenv(ccexitnb.ENV, "1")
    assert ccexitnb.enabled()
    monkeypatch.setenv(ccexitnb.ENV, "cc")
    with pytest.raises(ValueError):
        ccexitnb.enabled()


def test_off_and_spherical_give_no_rows(monkeypatch):
    monkeypatch.delenv(ccexitnb.ENV, raising=False)
    monkeypatch.delenv(ccexitnb.ENV2, raising=False)
    cas, etot, r, sn = _primary(76, 187, 0.04)
    assert cas.options.ccexitnbnf and ccexitnb.enabled(cas.options)  # CCEXITNB2 default ON (no fission channel)
    cas.options = dataclasses.replace(cas.options, ccexitnbnf=False)  # deck `ccexitnbnf n` = OFF = previous production
    assert ccexitnb.rows(cas, 0, r.ex_mev, r.nlast, r.maxex, etot, sn, r.tjl.shape[1], 1.0) == {}
    monkeypatch.setenv(ccexitnb.ENV, "1")
    cas2, etot2, r2, sn2 = _primary(50, 120, 2.0)  # spherical target
    assert ccexitnb.rows(cas2, 0, r2.ex_mev, r2.nlast, r2.maxex, etot2, sn2, r2.tjl.shape[1], 1.0) == {}


@pytest.mark.parametrize("e", [0.0106, 0.04, 1.5])
def test_spherical_nodes_reproduce_densprepare(monkeypatch, e):
    """The builder's locate + Lagrange rule fed with the spherical table returns densprepare's own rows."""
    monkeypatch.setenv(ccexitnb.ENV, "1")
    cas, etot, r, sn = _primary(76, 187, e)
    sph = np.asarray(cas.trans_of(0, 0)[1][0], dtype=np.float64)
    rw = ccexitnb.rows(cas, 0, r.ex_mev, r.nlast, r.maxex, etot, sn, r.tjl.shape[1], ccexitnb.fnorm_n(cas),
                       node=lambda n: sph[n])
    assert rw
    for i, (row, _lm) in rw.items():
        ref = np.asarray(r.tjl[i])
        k = min(ref.shape[0], row.shape[0])
        lm = int(r.lmaxhf[i])
        np.testing.assert_allclose(row[: lm + 1], ref[: lm + 1], rtol=2e-6, atol=1e-12)
        assert not np.any(ref[lm + 1: k])  # densprepare zeroes l > lmaxhf


def test_os187_rows_nonband_only_and_cc(monkeypatch):
    monkeypatch.setenv(ccexitnb.ENV, "1")
    cas, etot, r, sn = _primary(76, 187, 0.04)
    band = np.asarray(cas._coupled_band()["e_mev"])
    rw = ccexitnb.rows(cas, 0, r.ex_mev, r.nlast, r.maxex, etot, sn, r.tjl.shape[1], ccexitnb.fnorm_n(cas))
    assert 1 in rw  # 9.756 keV 3/2- (not in the 1/2-[510] band)
    for i in rw:
        assert np.min(np.abs(band - r.ex_mev[i])) > 1e-6 and i != 0
    # the CC s-wave exceeds the spherical one for n + Os-187 at ~30 keV (CC/sph ~3, STEP0)
    assert rw[1][0][0, 2] > 1.5 * float(np.asarray(r.tjl[1])[0, 2])
    new = ccexitnb.apply_residual(cas, r, 0, etot, sn)
    assert new is not r and np.array_equal(np.asarray(new.tjl[0]), np.asarray(r.tjl[0]))


def test_ccexitnb2_class_rule_no_fission_channel_only(monkeypatch):
    """CCEXITNB2 (`ccexitnbnf y` / INCOGNITA_CCEXITNB2=1): the CCEXITNB rows on a target without a fission channel
    (Os-187: identical to CCEXITNB), none on a target whose engine opens fission (U-235, A > 215)."""
    monkeypatch.delenv(ccexitnb.ENV, raising=False)
    for v in ("", "0", "n"):
        monkeypatch.setenv(ccexitnb.ENV2, v)
        assert not ccexitnb.enabled()
    monkeypatch.setenv(ccexitnb.ENV2, "1")
    assert not ccexitnb.enabled()  # no options: the class cannot be decided -> off
    cas, etot, r, sn = _primary(76, 187, 0.04)
    assert not cas.options.flagfission and ccexitnb.enabled(cas.options)
    rw2 = ccexitnb.rows(cas, 0, r.ex_mev, r.nlast, r.maxex, etot, sn, r.tjl.shape[1], ccexitnb.fnorm_n(cas))
    monkeypatch.delenv(ccexitnb.ENV2)
    monkeypatch.setenv(ccexitnb.ENV, "1")
    cas1, etot1, r1, sn1 = _primary(76, 187, 0.04)
    rw1 = ccexitnb.rows(cas1, 0, r1.ex_mev, r1.nlast, r1.maxex, etot1, sn1, r1.tjl.shape[1], ccexitnb.fnorm_n(cas1))
    assert rw2 and sorted(rw2) == sorted(rw1)
    for i in rw1:
        assert np.array_equal(rw1[i][0], rw2[i][0]) and rw1[i][1] == rw2[i][1]
    cu, etu, ru, snu = _primary(92, 235, 0.04)
    assert cu.options.flagfission
    assert ccexitnb.rows(cu, 0, ru.ex_mev, ru.nlast, ru.maxex, etu, snu, ru.tjl.shape[1], ccexitnb.fnorm_n(cu))  # CCEXITNB: rows
    monkeypatch.delenv(ccexitnb.ENV)
    monkeypatch.setenv(ccexitnb.ENV2, "1")
    assert not ccexitnb.enabled(cu.options)
    assert ccexitnb.rows(cu, 0, ru.ex_mev, ru.nlast, ru.maxex, etu, snu, ru.tjl.shape[1], ccexitnb.fnorm_n(cu)) == {}


def test_ccexitnbnf_deck_keyword(monkeypatch):
    monkeypatch.delenv(ccexitnb.ENV, raising=False)
    monkeypatch.delenv(ccexitnb.ENV2, raising=False)
    from types import SimpleNamespace as N
    assert ccexitnb.enabled(N(ccexitnb=False, ccexitnbnf=True, flagfission=False))
    assert not ccexitnb.enabled(N(ccexitnb=False, ccexitnbnf=True, flagfission=True))
    assert not ccexitnb.enabled(N(ccexitnb=False, ccexitnbnf=False, flagfission=False))
