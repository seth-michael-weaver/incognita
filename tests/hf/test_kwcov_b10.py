"""KWCOV B10: unresolved resonance range (docs/hf/COVERAGE_PLAN.md, batch B10).

urr / lurr / urrnjoy / rprime: comptarget's (l, J) URR blocks, dtheory's D(l, J), strengthfunc, the widths, the NJOY
formalism (csunr2, unfac, gnrl) and urrout's files, output only (physics/hf/urr.py). The engine was compared with stock
TALYS-2.25 by scripts/kwcov/b10_response.py (numbers in the plan); the tests here pin the transcriptions, the parsing
and the refusals, defaults unchanged, and one Fe-56 run against stock numbers.
"""
from __future__ import annotations

import math
import os

import numpy as np
import pytest

from physics.hf import chartrun
from physics.hf import urr as U
from physics.hf.input import defaults as D
from physics.hf.input import fitlib as F


@pytest.fixture
def clean(monkeypatch):
    for k in [k for k in os.environ if k.startswith("INCOGNITA_")]:
        monkeypatch.delenv(k, raising=False)
    F.deactivate(); F._cards.cache_clear(); chartrun.drop_target_caches()
    yield monkeypatch
    for k in [k for k in os.environ if k.startswith("INCOGNITA_")]:
        monkeypatch.delenv(k, raising=False)
    F.deactivate(); F._cards.cache_clear(); chartrun.drop_target_caches()


# ------------------------------------------------------------------------------------------------ transcriptions
def test_gnrl_by_hand():
    qp, qw = U._QP.astype(float), U._QW.astype(float)
    # no fission, no competition: sum_j w_j x_j^2 / (a x_j + g) (id 1), sum_j w_j x_j / (a x_j + g) (id 2)
    for mu in (1, 2, 4):
        x, w = qp[:, mu - 1], qw[:, mu - 1]
        assert U.gnrl(0.3, 0.0, 0.05, mu, 1, 1, 0.0, 1) == pytest.approx((w * x * x / (0.3 * x + 0.05)).sum())
        assert U.gnrl(0.3, 0.0, 0.05, mu, 1, 1, 0.0, 2) == pytest.approx((w * x / (0.3 * x + 0.05)).sum())
        assert U.gnrl(0.3, 0.0, 0.05, mu, 1, 1, 0.0, 3) == 0.0
    # fission + competition: triple sum, symmetric check against an explicit loop
    s = sum(qw[j, 0] * qw[k, 1] * qw[m, 2] * qp[j, 0] * qp[k, 1] / (0.2 * qp[j, 0] + 0.1 * qp[k, 1] + 0.05
                                                                        + 0.4 * qp[m, 2])
            for j in range(10) for k in range(10) for m in range(10))
    assert U.gnrl(0.2, 0.1, 0.05, 1, 2, 3, 0.4, 3) == pytest.approx(s)
    assert U.gnrl(0.0, 0.1, 0.05, 1, 2, 3, 0.4, 3) == 0.0 and U.gnrl(0.2, 0.1, 0.0, 1, 2, 3, 0.4, 1) == 0.0
    # chi-squared quadrature of one degree of freedom: weights sum to 1
    assert qw.sum(0) == pytest.approx(np.ones(4), abs=3e-4)  # NJOY table precision


def test_unfac_and_strengthfunc():
    assert U.unfac(0, 0.3, 0.2, 2.0) == (2.0, 0.2)
    v, p = U.unfac(1, 0.3, 0.2, 1.0)
    assert v == pytest.approx(0.09 / 1.09) and p == pytest.approx(0.2 - math.atan(0.2))
    v, p = U.unfac(2, 0.3, 0.2, 1.0)
    assert v == pytest.approx(0.0081 / (9 + 0.27 + 0.0081)) and p == pytest.approx(0.2 - math.atan(0.6 / 2.96))
    assert U.unfac(3, 0.3, 0.2, 1.0) == (1.0, 1.0)
    # l = 0: v_l = 1/10, S = T / (2 pi 0.1 sqrt(E))
    assert U.strengthfunc(0.01, 0, 0.01, 0.02, 56.0) == pytest.approx(0.01 / (2 * math.pi * 0.1 * 0.1))


def test_urr_keywords_parse(clean):
    o = D.default_options(26, 56)
    assert not o.flagurr and o.lurr == 2 and not o.flagurrnjoy and not U.active(o)
    for lines, (flag, eurr, lurr, njoy) in (
            ("urr y", (True, -1.0, 2, False)), ("urr 0.5; lurr 1; urrnjoy y", (True, 0.5, 1, True)),
            ("urr n", (False, -1.0, 2, False))):
        clean.setenv(F.ENV_LINES, lines)
        F._cards.cache_clear(); F.deactivate(); chartrun.drop_target_caches()
        from physics.hf.emission.feeding import Cascade

        o = Cascade(26, 56, 1.0, energies=(1.0,)).options
        assert (o.flagurr, o.eurr_mev, o.lurr, o.flagurrnjoy) == (flag, eurr, lurr, njoy), lines


def test_urr_refusals():
    class O:
        flagurr, lurr, k0, flagcomp = True, 2, 1, True

    U.check(O)
    O.lurr = 61
    with pytest.raises(ValueError, match="lurr"):
        U.check(O)
    O.lurr, O.k0 = 2, 2
    with pytest.raises(ValueError, match="incident neutrons"):
        U.check(O)
    O.k0, O.flagcomp = 1, False
    with pytest.raises(ValueError, match="compound nucleus model"):
        U.check(O)

    class CI:
        alphadom = cellsel = ew = None
        flagwidth, wmode = True, 2

    with pytest.raises(NotImplementedError, match="widthmode 2"):
        U.comptarget_lj(CI, 2)
    CI.ew = object()
    with pytest.raises(NotImplementedError, match="EWFC"):
        U.comptarget_lj(CI, 2)


def test_defaults_record_nothing(clean):
    from physics.hf.emission.feeding import Cascade

    cas = Cascade(26, 56, 1.0, energies=(1.0,))
    U.begin_run(cas)
    assert U.STATE == {} and not U.wanted(cas, 0.01)


def test_thermal_capture_table_and_systematics(clean):
    from physics.hf.emission.feeding import Cascade

    assert U.thermal_capture_mb(Cascade(26, 56, 1.0, energies=(1.0,))) == 2590.0  # structure/thermal/Fe.ther
    assert U.thermal_capture_mb(Cascade(92, 238, 1.0, energies=(1.0,))) == 2670.0  # stock urr.dat (U.ther)


# ------------------------------------------------------------------------------------------------ engine vs stock
def test_fe56_urr_vs_stock(clean, tmp_path):
    """Stock TALYS-2.25 n + Fe-56 at 0.01 0.1 1 5 MeV with `urr y; urrnjoy y` (urr.dat, urrtalys.tot, urrnjoy.tot,
    urrcomwidth.l00, urrgamwidth.l01). The engine runs 0.01 and 1 MeV; R' of the first energy is the same."""
    from physics.hf.input.deck import run_deck

    (tmp_path / "energies").write_text("0.01\n1.\n")
    deck = "projectile n\nelement fe\nmass 56\nenergy energies\n"
    (tmp_path / "talys.inp").write_text(deck)
    r0 = run_deck(tmp_path / "talys.inp")
    assert r0.urr == {}
    (tmp_path / "talys.inp").write_text(deck + "urr y\nurrnjoy y\n")
    F.deactivate(); F._cards.cache_clear(); chartrun.drop_target_caches()  # a new deck in the same process
    r = run_deck(tmp_path / "talys.inp")
    # output only: every cross section bit for bit
    for fam in ("channels_mb", "levels_mb", "residual_production_mb", "totals_mb"):
        a, b = getattr(r0, fam), getattr(r, fam)
        assert a.keys() == b.keys()
        for k in a:
            assert bool((a[k] == b[k]).all()), (fam, k)
    u = r.urr
    d = u["urr.dat"]
    row = (d["E"] == np.float32(0.01)) & (d["l"] == 0)
    for c, v in (("D(l,J)", 2.523266e4), ("S(l,J)", 4.998054), ("Gn(l,J)", 1.261142e1), ("Gg(l,J)", 1.251195)):
        assert abs(math.log(float(d[c][row][0]) / v)) < 1e-4, c
    assert float(d["xscaptherm"][0]) == 2590.0 and abs(float(d["S_n"][0]) - 7.646171) < 1e-4
    assert abs(float(d["rprime"][0]) - 7.5928) < 1e-3
    t = u["urrtalys.tot"]
    for c, v in (("xs", (2.853946e4, 3.737462e3)), ("elastic", (2.849768e4, 3.198740e3)),
                 ("capture", (4.177991e1, 2.290062))):
        assert np.allclose(t[c], v, rtol=1e-4), c
    n = u["urrnjoy.tot"]
    assert np.allclose(n["xs"], (2.735259e4, 6.240286e3), rtol=1e-4)
    assert np.allclose(n["capture"], (4.196498e1, 2.299519), rtol=1e-4)
    assert np.allclose(u["urrratio.tot"]["xs"], (1.043392, 0.5989249), rtol=1e-4)
    assert np.allclose(u["urrcomwidth.l00"]["J=0.5:width"], (0.0, 36.72449), rtol=1e-4)
    assert np.allclose(u["urrcomwidth.l00"]["J=0.5:nu"], (1.0, 1.0))
    assert np.allclose(u["urrgamwidth.l01"]["J=1.5:width"], (5.221708e-1, 6.824679e-1), rtol=1e-4)
    assert "urrfiswidth.l00" not in u and "urrprowidth.l00" not in u and "urralpwidth.l00" in u
