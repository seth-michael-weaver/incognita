"""LEESHELL: (a) per-nucleus `upbendc/e/f` and `upbendc/e/fadjust` cards reach gamma_parameters with
TALYS semantics (input_gammapar.f90:392-425 assign after the defaults; fstrength.f90:489-491 multiply
by the adjusts) -- before, they were skipped as unknown keywords; (b) `leeshell n|nm|b`
(env INCOGNITA_LEESHELL): M1 upbend strength C = 0 by default in closed-shell decaying nuclei.
"""

from __future__ import annotations

import pytest

from physics.hf.input import fitlib


def _gp(monkeypatch, Z, A, lines: str = "", mode: str | None = None):
    from physics.hf.compound.dens_reference import _gamma_parameters

    monkeypatch.setenv(fitlib.ENV, "nodata")
    if lines:
        monkeypatch.setenv(fitlib.ENV_LINES, lines)
    else:
        monkeypatch.delenv(fitlib.ENV_LINES, raising=False)
    if mode is None:
        monkeypatch.delenv("INCOGNITA_LEESHELL", raising=False)
    else:
        monkeypatch.setenv("INCOGNITA_LEESHELL", mode)
    try:
        fitlib.activate(Z, A)
        _gamma_parameters.cache_clear()
        gp, _o = _gamma_parameters(Z, A)
        skipped = list(fitlib.active().skipped) if fitlib.active() is not None else []
    finally:
        fitlib.deactivate()
        _gamma_parameters.cache_clear()
    return gp, skipped


def test_parse():
    _, cells, _, _, skipped = fitlib._split(
        ["upbendc 50 121 0. m1", "upbende 50 121 0.9 m1", "upbendfadjust 26 57 2.0 m1", "upbendc 26 57 2e-10 e1"],
        want_options=False)
    assert not skipped
    assert ("upbendc", 50, 121, 0.0, (0, 1)) in cells
    assert ("upbende", 50, 121, 0.9, (0, 1)) in cells
    assert ("upbendfadjust", 26, 57, 2.0, (0, 1)) in cells
    assert ("upbendc", 26, 57, 2e-10, (1, 1)) in cells


def test_cards_apply(monkeypatch):
    base, _ = _gp(monkeypatch, 50, 120)  # compound Sn-121
    assert float(base.upbend[0, 1, 1]) > 0.0
    gp, sk = _gp(monkeypatch, 50, 120, "upbendc 50 121 0. m1")
    assert not [s for s in sk if "upbend" in s[0]]
    assert float(gp.upbend[0, 1, 1]) == 0.0  # a user 0 is kept (TALYS assigns after its defaults)
    assert float(gp.upbend[1, 1, 1]) == float(base.upbend[1, 1, 1])  # E1 low-E term untouched
    gp, _ = _gp(monkeypatch, 50, 120, "upbendcadjust 50 121 2.0 m1;upbende 50 121 0.5 m1")
    assert float(gp.upbend[0, 1, 1]) == pytest.approx(2.0 * float(base.upbend[0, 1, 1]), rel=0, abs=0)
    assert float(gp.upbend[0, 1, 2]) == 0.5
    gp, _ = _gp(monkeypatch, 50, 120, "upbendc 26 57 0. m1")  # other nucleus: no effect
    assert float(gp.upbend[0, 1, 1]) == float(base.upbend[0, 1, 1])


@pytest.mark.parametrize("Z,A,nm,b", [(40, 89, True, True),    # Zr-90  N=50
                                       (50, 120, False, True),  # Sn-121 Z=50
                                       (26, 56, False, False),  # Fe-57
                                       (28, 59, False, True),   # Ni-60 Z=28
                                       (82, 207, True, True)])  # Pb-208
def test_leeshell(monkeypatch, Z, A, nm, b):
    base, _ = _gp(monkeypatch, Z, A)
    for mode, closed in (("n", False), ("nm", nm), ("b", b)):
        gp, _ = _gp(monkeypatch, Z, A, mode=mode)
        assert float(gp.upbend[0, 1, 1]) == (0.0 if closed else float(base.upbend[0, 1, 1]))
        assert float(gp.upbend[1, 1, 1]) == float(base.upbend[1, 1, 1])
        assert float(gp.upbend[1, 1, 2]) == float(base.upbend[1, 1, 2])


def test_leeshell_card_wins(monkeypatch):
    base, _ = _gp(monkeypatch, 40, 89)
    gp, _ = _gp(monkeypatch, 40, 89, "upbendc 40 90 2e-8 m1", mode="nm")
    assert float(gp.upbend[0, 1, 1]) == 2e-8
