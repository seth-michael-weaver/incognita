"""ETABLEFIX: `etable` and the other photon-strength keywords reach gamma_parameters as TALYS
applies them (gammapar.f90:261-267, 437-443, 564-585; fstrength.f90:158-173, 456-471).

Before the fix fitlib passed `etable` under its keyword name (gamma_parameters reads
`etable_mev`), dropped every `*adjust`, and could not parse `egr Z A v E1 [igr]` at all.
"""

from __future__ import annotations

import numpy as np
import pytest
import torch

from physics.hf.input import fitlib

Z, A = 26, 56  # target Fe-56; the keywords sit on the compound nucleus Fe-57


@pytest.fixture(scope="module", autouse=True)
def _ftglobal_off():
    """FTPROMO (ftglobal default ON): this module checks behaviour against deck/golden values defined without the global ftable; pinned at ftglobal n (INCOGNITA_FTGLOBAL=0)."""
    with pytest.MonkeyPatch.context() as mp:
        mp.setenv("INCOGNITA_FTGLOBAL", "0")
        yield


def _gp(monkeypatch, lines: str):
    from physics.hf.compound.dens_reference import _gamma_parameters

    monkeypatch.setenv(fitlib.ENV, "nodata")
    if lines:
        monkeypatch.setenv(fitlib.ENV_LINES, lines)
    else:
        monkeypatch.delenv(fitlib.ENV_LINES, raising=False)
    try:
        fitlib.activate(Z, A)
        _gamma_parameters.cache_clear()
        gp, _o = _gamma_parameters(Z, A)
        gov = fitlib.gamma_overrides(Z, A + 1, int(gp.gammax))
    finally:
        fitlib.deactivate()
        _gamma_parameters.cache_clear()
    return gp, gov


def _talys_table(gp, et, ft, wt, irad=1):
    """gammapar.f90:257-270 + 564-585 written out: e = ee + et, f = f_raw * ft, then the
    stretch about the first T = 0 maximum by wt."""
    tab = gp.tables[(irad, 1)]
    e = tab.e_raw_mev.numpy().copy()
    e[1:] = e[1:] + et
    f = tab.f_raw_mev3.numpy() * ft
    f0 = f[1:, 0]
    imax = int(np.argmax(f0 == f0.max())) + 1
    emid = e[imax]
    e[1:] = emid + (e[1:] - emid) * wt
    return e, f


def test_class5_parse():
    _, cells, _, _, skipped = fitlib._split(
        ["etable 26 57 0.5 e1", "etableadjust 26 57 0.1 m1", "egr 26 57 17.0 e1 2",
         "sgradjust 26 57 1.3 m1", "ftable 26 57 1.2"], want_options=False)
    assert not skipped
    assert ("etable", 26, 57, 0.5, (1, 1)) in cells
    assert ("etableadjust", 26, 57, 0.1, (0, 1)) in cells
    assert ("egr", 26, 57, 17.0, (1, 1, 2)) in cells
    assert ("sgradjust", 26, 57, 1.3, (0, 1, 1)) in cells
    assert ("ftable", 26, 57, 1.2, (1, 1)) in cells


def test_etable_shifts_table_exactly(monkeypatch):
    from physics.hf.gamma.parameters import table_arrays

    gp0, gov0 = _gp(monkeypatch, "strength 8")
    gp1, gov1 = _gp(monkeypatch, "strength 8;etable 26 57 0.5 e1")
    assert gov0 is None
    assert set(gov1) == {"etable_mev"} and gov1["etable_mev"][1, 1] == 0.5
    assert float(gp0.etable_mev[1, 1]) == 0.0 and float(gp1.etable_mev[1, 1]) == 0.5
    wt = float(gp1.wtable[1, 1])
    assert wt == float(gp0.wtable[1, 1])
    for gp, et in ((gp0, 0.0), (gp1, 0.5)):
        e, f = table_arrays(gp, 1, 1)
        e_ref, f_ref = _talys_table(gp, et, float(gp.ftable[1, 1]), wt)
        np.testing.assert_array_equal(f.numpy(), f_ref)
        np.testing.assert_allclose(e.numpy(), e_ref, rtol=0, atol=1e-12)
    # the whole curve moves up by 0.5 MeV: f1(E + 0.5) == f0(E)
    e0, f0 = table_arrays(gp0, 1, 1)
    e1, f1 = table_arrays(gp1, 1, 1)
    np.testing.assert_allclose((e1 - e0).numpy()[1:], 0.5, rtol=0, atol=1e-12)
    np.testing.assert_array_equal(f1.numpy(), f0.numpy())


def test_etable_moves_fstrength(monkeypatch):
    """f(E1) through fstrength's table branch: the shifted table evaluated at E + et equals the
    default at E (strength 8 has one temperature, so Tnuc does not enter). The E1 upbend term
    fstrength adds on top depends on E_gamma itself and is not shifted, in TALYS too."""
    from physics.hf.gamma.strength import _table_strength, fstrength_gp

    gp0, _ = _gp(monkeypatch, "strength 8")
    gp1, _ = _gp(monkeypatch, "strength 8;etable 26 57 0.5 e1")
    assert gp0.n_tqrpa == 1
    eg = torch.tensor([2.0, 4.0, 6.0, 8.0, 12.0, 16.0], dtype=torch.float64)
    f0 = _table_strength(gp0, 0.0, eg, 1, 1)
    f1 = _table_strength(gp1, 0.0, eg + 0.5, 1, 1)
    np.testing.assert_allclose(f1.numpy(), f0.numpy(), rtol=1e-9)
    # and the full fstrength moves: at 8 MeV the table term is ~all of f(E1)
    full0 = fstrength_gp(gp0, 0.0, eg, 1, 1)
    full1 = fstrength_gp(gp1, 0.0, eg, 1, 1)
    assert bool((full1 < full0)[eg < 12.0].all())  # GDR tail moved up in energy -> lower f below it


def test_table_adjusts(monkeypatch):
    from physics.hf.gamma.parameters import table_arrays

    gp0, _ = _gp(monkeypatch, "strength 8")
    gpa, gov = _gp(monkeypatch, "strength 8;etable 26 57 0.2 e1;etableadjust 26 57 0.3 e1;"
                                "ftableadjust 26 57 1.2 e1;wtableadjust 26 57 1.1 e1")
    assert set(gov) == {"etable_mev", "etableadjust", "ftableadjust", "wtableadjust"}
    assert float(gpa.etable_mev[1, 1]) == pytest.approx(0.5, abs=1e-15)
    assert float(gpa.ftable[1, 1]) == float(gp0.ftable[1, 1]) * 1.2
    assert float(gpa.wtable[1, 1]) == float(gp0.wtable[1, 1]) * 1.1
    e, f = table_arrays(gpa, 1, 1)
    e_ref, f_ref = _talys_table(gpa, 0.5, float(gp0.ftable[1, 1]) * 1.2,
                                float(gp0.wtable[1, 1]) * 1.1)
    np.testing.assert_allclose(f.numpy(), f_ref, rtol=1e-15, atol=0)
    np.testing.assert_allclose(e.numpy(), e_ref, rtol=0, atol=1e-12)
    # M1 entries untouched by E1 keywords
    for fld in ("etable_mev", "ftable", "wtable"):
        assert torch.equal(getattr(gpa, fld)[0], getattr(gp0, fld)[0])


def test_resonance_keywords(monkeypatch):
    gp0, _ = _gp(monkeypatch, "strength 8")
    gp1, gov = _gp(monkeypatch, "strength 8;egr 26 57 17.5 e2;ggr 26 57 4.5 e2;"
                                "sgradjust 26 57 1.3 m1;egradjust 26 57 1.05 e2 1;"
                                "spr 26 57 0.7 m1;gpradjust 26 57 2.0 m1")
    assert gov["egr_mev"].shape == (2, int(gp0.gammax) + 1, 3)
    # value keywords fill, then fstrength's adjust factor multiplies
    assert float(gp1.egr_mev[1, 2, 1]) == pytest.approx(17.5 * 1.05, rel=1e-15)
    assert float(gp1.ggr_mev[1, 2, 1]) == 4.5
    assert float(gp1.tpr_mb[0, 1, 1]) == 0.7
    assert float(gp1.gpr_mev[0, 1, 1]) == float(gp0.gpr_mev[0, 1, 1]) * 2.0
    assert float(gp1.sgr_mb[0, 1, 1]) == pytest.approx(float(gp0.sgr_mb[0, 1, 1]) * 1.3,
                                                       rel=1e-15)
    # nothing else moved
    assert torch.equal(gp1.egr_mev[1, 1], gp0.egr_mev[1, 1])
    assert torch.equal(gp1.sgr_mb[1, 1], gp0.sgr_mb[1, 1])
    # the E2 sgr default is built from the user's egr/ggr, before fstrength's egradjust
    # (gammapar.f90:126: 1.4e-4 Z^2 egr / (A^1/3 ggr), compound A = 57)
    assert float(gp1.sgr_mb[1, 2, 1]) == pytest.approx(
        1.4e-4 * 26**2 * 17.5 / (57 ** (1.0 / 3.0) * 4.5), rel=1e-6)  # TALYS onethird is single precision


def test_off_is_untouched(monkeypatch):
    """No gamma keyword: no override dict, identical parameters; ftable/wtable-only lines (the
    baseline recipe's form) go through exactly the old path."""
    gp0, gov0 = _gp(monkeypatch, "strength 8")
    gpw, govw = _gp(monkeypatch, "strength 8;ftable 26 57 1.2 e1;wtable 26 57 0.9 e1")
    assert gov0 is None and set(govw) == {"ftable", "wtable"}
    assert float(gpw.ftable[1, 1]) == 1.2 and float(gpw.wtable[1, 1]) == 0.9
    assert float(gpw.etable_mev.abs().sum()) == 0.0
