"""KWCOV B11: medical isotope production (docs/hf/COVERAGE_PLAN.md, batch B11).

production / Ebeam / Eback / Ibeam / Area / rho / Tirrad / Tcool / radiounit / yieldunit: TALYS's isoprod
(prodinitial, decaydata, prodres, stoppingpower, prodrates, prodyield, prodout) on the run's residual production,
physics/hf/production.py. The decks were compared with stock TALYS-2.25 by scripts/kwcov/b11_response.py (numbers
in the plan); the tests here pin the port on stock's own p + Zn-68 cross sections (stock TALYS-2.25, `energy 8 20 1`,
`production y`, `Ebeam 18`, `Eback 10`, the rest TALYS's defaults) against stock's Y files and talys.out, the
parsing and the refusals, and one engine run.
"""
from __future__ import annotations

import os

import numpy as np
import pytest

from physics.hf import production as P
from physics.hf.input import defaults as D
from physics.hf.input import fitlib as F

E = [8.0 + i for i in range(13)]
# stock TALYS-2.25 p + Zn-68 (Zinit 31, Ninit 38): nonelastic.tot and four rp files
NONEL = [6.593632E+02, 7.713344E+02, 8.619274E+02, 9.282433E+02, 9.766588E+02, 1.014439E+03, 1.046136E+03,
         1.073708E+03, 1.097759E+03, 1.118650E+03, 1.136940E+03, 1.153290E+03, 1.168060E+03]
RP = {
    (30, 68): [4.633225E+01, 6.237594E+01, 7.729902E+01, 9.054463E+01, 1.037153E+02, 1.173663E+02, 1.288477E+02,
               1.351417E+02, 1.392679E+02, 1.425073E+02, 1.436201E+02, 1.438896E+02, 1.437436E+02],
    (31, 68): [6.058098E+02, 6.990686E+02, 7.718910E+02, 8.226604E+02, 8.550156E+02, 7.398970E+02, 5.125500E+02,
               3.370284E+02, 2.276355E+02, 1.590162E+02, 1.191895E+02, 9.543001E+01, 8.217965E+01],
    (31, 67): [0.0] * 5 + [1.278147E+02, 3.568514E+02, 5.227716E+02, 6.150036E+02, 6.624422E+02, 6.801651E+02,
                           6.829096E+02, 6.754653E+02],
    (29, 64): [0.0] * 5 + [1.522837E-02, 1.017652E-01, 6.229946E-01, 3.035559E+00, 9.466422E+00, 1.951981E+01,
                           3.049510E+01, 4.004861E+01],
}
DEFAULT_M = dict(Area=1.0, Eback=10.0, Ebeam=18.0, Ibeam=1.0, radiounit="gbq", yieldunit="num", rhotarget=-1.0,
                 Tirrad=(1, 0, 0, 0, 0), unitTirrad=("d", " ", " ", " ", " "), Tcool=(1, 0, 0, 0, 0),
                 unitTcool=("d", " ", " ", " ", " "))


def _run(**kw):
    m = dict(DEFAULT_M, **kw)
    rp = {(31 - z, 38 - (a - z), None): (E, v) for (z, a), v in RP.items()}
    return P.production(rp=rp, nonel=(E, NONEL), m=m, k0=2, Ztarget=30, Atarget=68, maxZ=12, maxN=32,
                        eninc=tuple(E))


@pytest.fixture
def clean(monkeypatch):
    from physics.hf import chartrun

    for k in [k for k in os.environ if k.startswith("INCOGNITA_")]:
        monkeypatch.delenv(k, raising=False)
    F.deactivate(); F._cards.cache_clear(); chartrun.drop_target_caches()
    yield monkeypatch
    for k in [k for k in os.environ if k.startswith("INCOGNITA_")]:
        monkeypatch.delenv(k, raising=False)
    F.deactivate(); F._cards.cache_clear(); chartrun.drop_target_caches()


# ------------------------------------------------------------------------------------------------ transcriptions
def test_parse_time():
    assert P.parse_time("2 d 6 h") == ((2, 6, 0, 0, 0), ("d", "h", " ", " ", " "))
    assert P.parse_time("30 minutes") == ((30, 0, 0, 0, 0), ("m", " ", " ", " ", " "))
    assert P.parse_time("1.5 d 3 h") == ((0, 3, 0, 0, 0), (" ", "h", " ", " ", " "))  # TALYS skips a non-integer
    assert P.parse_time("2") == ((2, 0, 0, 0, 0), (" ", " ", " ", " ", " "))  # no unit: 0 seconds in prodinitial


def test_prodinitial_and_time_grid():
    init = P.prodinitial(DEFAULT_M, 30)
    assert init["rho"] == pytest.approx(7.13, rel=1e-7) and init["Tir"] == 86400.0 and init["Tco"] == 86400.0
    assert init["Tirrad"] == (0, 1, 0, 0, 0)
    assert P.prodinitial(dict(DEFAULT_M, Tirrad=(90, 0, 0, 0, 0), unitTirrad=("m",) + (" ",) * 4), 30)["Tirrad"] \
        == (0, 0, 1, 30, 0)
    tg, nt = P.time_grid(86400.0, 86400.0)
    assert nt == 48 and tg[1] == 0.5 and tg[48] == 24.0
    for i, v in ((49, 2.406386E+01), (50, 2.413179E+01), (75, 2.831929E+01), (100, 4.8E+01)):  # stock Y031068.tot
        assert abs(tg[i] / v - 1) < 1e-6, (i, tg[i], v)


def test_decay_data_jeff():
    d = P.decay_data(31, 38, 12, 32)
    th, lam, rt = d[(0, 1, -1)]  # Ga-68
    assert lam == pytest.approx(1.707680E-04, rel=1e-6) and rt == 2 and d[(0, 1, 0)] == d[(0, 1, -1)]
    assert d[(0, 2, -1)][1] == pytest.approx(2.459993E-06, rel=1e-6)  # Ga-67
    assert d[(2, 3, -1)][1] == pytest.approx(1.515950E-05, rel=1e-6)  # Cu-64
    assert d[(1, 0, -1)][1] == 0.0  # Zn-68 stable
    tc = P.decay_data(43, 58, 12, 32)  # p + Mo-100 (Tc-101): Tc-99m (Zix 0, Nix 2, is 1)
    assert tc[(0, 2, 1)][1] == pytest.approx(3.203675E-05, rel=1e-6)
    assert tc[(0, 2, -1)][1] == pytest.approx(1.026401E-13, rel=1e-6)


def test_port_on_stock_cross_sections_zn68():
    out = _run()
    p = {v["nuclide"]: v["Initial production rate [s^-1]"] for v in out["params"].values()}
    for nuc, v in (("Ga68", 2.992189E-09), ("Ga67", 2.254957E-09), ("Cu64", 2.092811E-11), ("Zn68", 7.707816E-10)):
        assert abs(p[nuc] / v - 1) < 2e-6, (nuc, p[nuc], v)
    assert out["meta"]["Ntar0"] == pytest.approx(3.366285E+21, rel=2e-6)
    ga = out["files"]["Y031068.tot"]
    for i, act, iso in ((0, 2.665494E+03, 1.560886E+16), (47, 1.006791E+04, 5.895668E+16),
                        (99, 3.937366E-03, 2.305682E+10)):  # stock Y031068.tot rows 1, 48, 100
        assert abs(ga["Activity"][i] / act - 1) < 2e-6 and abs(ga["Isotopes"][i] / iso - 1) < 2e-6, i
    assert ga["Yield"][0] == pytest.approx(1.480830, rel=2e-6)
    g67 = out["files"]["Y031067.tot"]
    assert g67["Activity"][47] == pytest.approx(1.453080E+03, rel=2e-6)
    assert g67["Isotopes"][99] == pytest.approx(4.775834E+17, rel=2e-6)
    assert out["files"]["Y029064.tot"]["Activity"][99] == pytest.approx(1.387761E+01, rel=2e-6)
    s = {r["nuclide"]: r for r in out["summary"]}
    assert s["Ga68"]["Activity"] == pytest.approx(1.006908E+04, rel=2e-6)  # talys.out: at the activity maximum
    assert out["params"]["Y031068.tot"]["Maximum production at"].split() == \
        "0 years 0 days 16 hours 45 minutes 33 seconds".split()


def test_units_and_beam_scale():
    base = _run()
    mbq = _run(radiounit="mbq", yieldunit="mg", Ibeam=0.5)
    a0, a1 = base["files"]["Y031068.tot"], mbq["files"]["Y031068.tot"]
    # Ibeam halves the projectiles: rates (and early activity) halve; GBq -> MBq x 1000
    assert a1["Activity"][0] / a0["Activity"][0] == pytest.approx(0.5 * 1000, rel=1e-5)
    assert a1["Isotopes"][0] / a0["Isotopes"][0] == pytest.approx(0.5 * 68 / P.AVOGADRO * 1e3, rel=1e-5)
    assert mbq["units"] == {"activity": "MBq", "isotopes": "mg"}
    wide = _run(Area=2.5)  # rate per atom ~ 1/Area, atoms ~ Area: a thick target stops the same beam (stock 1.00015)
    assert wide["files"]["Y031068.tot"]["Activity"][0] / a0["Activity"][0] == pytest.approx(1.0, abs=1e-4)


def test_write_and_read_back(tmp_path):
    out = _run()
    names = P.write_files(out, tmp_path)
    assert "Y031068.tot" in names
    par, cols = P.read_yfile(tmp_path / "Y031068.tot")
    assert np.allclose(cols["Activity"], out["files"]["Y031068.tot"]["Activity"], rtol=1e-6)
    assert float(par["Initial production rate [s^-1]"]) == pytest.approx(2.992189E-09, rel=2e-6)
    assert P.write_files(out, tmp_path / "b", block=True) == ["Y.tot"]


# ------------------------------------------------------------------------------------------------ input, refusals
def test_options_medical_keywords():
    o = D.default_options(30, 68, "p", overrides={"production": "y", "ebeam": "18", "eback": "10", "ibeam": "0.5",
                                                    "area": "2", "rho": "7", "radiounit": "MBq", "yieldunit": "mug",
                                                    "tirrad": "2 d 6 h", "tcool": "30 m"})
    assert o.flagprod and (o.Ebeam, o.Eback, o.Ibeam, o.Area, o.rhotarget) == (18.0, 10.0, 0.5, 2.0, 7.0)
    assert (o.radiounit, o.yieldunit) == ("mbq", "mug")
    assert o.Tirrad == (2, 6, 0, 0, 0) and o.unitTirrad[:2] == ("d", "h") and o.Tcool[0] == 30
    d = D.default_options(30, 68, "p")
    assert not d.flagprod and d.Ebeam == -1.0 and d.Tirrad == (1, 0, 0, 0, 0) and d.radiounit == "gbq"


def test_deck_lines_accepted(clean):
    # before B11 `ebeam 18` etc. were refused on a deck line ("not a TALYS keyword the port knows")
    clean.setenv("INCOGNITA_CPINC", "p")
    clean.setenv(F.ENV_LINES, "production y;ebeam 18;eback 10;tirrad 2 d 6 h;tcool 1 d;radiounit kbq")
    F._cards.cache_clear(); F.deactivate()
    F.activate(30, 68)
    o = D.default_options(30, 68, "p")
    assert o.flagprod and o.Ebeam == 18.0 and o.Tirrad == (2, 6, 0, 0, 0) and o.radiounit == "kbq"


def test_checks_refuse():
    m = dict(DEFAULT_M)
    with pytest.raises(NotImplementedError, match="incident photons or neutrons"):
        P.check(m, 1, tuple(E))
    with pytest.raises(ValueError, match="Ebeam must be given"):
        P.check(dict(m, Ebeam=-1.0), 2, tuple(E))
    with pytest.raises(ValueError, match="Ebeam is not in the energy range"):
        P.check(dict(m, Ebeam=25.0), 2, tuple(E))
    with pytest.raises(ValueError, match="Eback is not in the energy range"):
        P.check(dict(m, Eback=5.0), 2, tuple(E))
    with pytest.raises(ValueError, match="radiounit"):
        P.check(dict(m, radiounit="xx"), 2, tuple(E))
    with pytest.raises(ValueError, match="yieldunit"):
        P.check(dict(m, yieldunit="lb"), 2, tuple(E))
    with pytest.raises(ValueError, match="wrong unit for Tirrad"):
        P.check(dict(m, unitTirrad=("w",) + (" ",) * 4), 2, tuple(E))
    assert P.check(dict(m, Eback=-1.0), 2, tuple(E))["Eback"] == 13.0  # max(Ebeam - 5, 0.1)


# ------------------------------------------------------------------------------------------------ engine
def test_engine_zn68_production(clean, tmp_path):
    """p + Zn-68 at 10 and 18 MeV, production y Ebeam 18 Eback 10: the run's Results.production vs the port on
    stock's cross sections at the same two energies (the engine's rp031068 is stock's to 0.004 %)."""
    from physics.hf.input.deck import run_deck

    clean.setenv("INCOGNITA_CPINC", "p")
    (tmp_path / "talys.inp").write_text("projectile p\nelement zn\nmass 68\nenergy 10 18 8\nproduction y\nEbeam 18\n"
                                        "Eback 10\n")
    r = run_deck(tmp_path / "talys.inp")
    pr = r.production
    two = [2, 10]
    rp = {(31 - z, 38 - (a - z), None): ([E[i] for i in two], [v[i] for i in two]) for (z, a), v in RP.items()}
    ref = P.production(rp=rp, nonel=([E[i] for i in two], [NONEL[i] for i in two]), m=DEFAULT_M, k0=2, Ztarget=30,
                       Atarget=68, maxZ=12, maxN=32, eninc=(10.0, 18.0))
    for n in ("Y031068.tot", "Y031067.tot"):
        a, b = pr["files"][n]["Activity"][47], ref["files"][n]["Activity"][47]
        assert abs(a / b - 1) < 2e-3, (n, a, b)
    assert pr["meta"]["Ntime"] == 48


def test_engine_neutron_production_refused(clean, tmp_path):
    from physics.hf.input.deck import run_deck

    (tmp_path / "talys.inp").write_text("projectile n\nelement fe\nmass 56\nenergy 14\nproduction y\nEbeam 14\n")
    with pytest.raises(NotImplementedError, match="incident photons or neutrons"):
        run_deck(tmp_path / "talys.inp")
