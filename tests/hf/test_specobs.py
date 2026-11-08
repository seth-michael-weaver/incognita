"""KWCOV B4 (SPECOBS): emission spectra, DDX, discrete gamma lines and xsngn on TALYS's keywords, output only.

* unit: keyword parsing (outspectra, ddxmode, fileddxa, fileddxe, filespectrum, outgamdis, blockspectra, endf y), the
  switch logic of output.f90:63-67 / input_output.f90:279-288, the continuum angle grid and TALYS's DDX file names, the
  fine discrete grid and Gaussian peaks of spectra.f90 on a synthetic record (flux of a peak = its level cross section);
* engine (needs a native build, TALYS structure/ and the stock TALYS-2.25 run made with scripts/kwcov/b4_compare.py's
  recipe in $KWCOV_STOCK/b4_fe56: n + Fe-56 at 1 5 14 MeV, `outspectra y`, `ddxmode 3`, `fileddxa n 30/90/150`,
  `fileddxa p ...`, `fileddxe n 3.0`, `fileddxe p 6.0`, `outgamdis y`, `filegamdis y`, `channels y`, `filechannels y`):
  every Results array is bit-identical with the keywords on and off; the espec grids equal stock's; spectra and DDX
  within 0.1 % of stock per bin at 1 and 5 MeV (where the engine's channels agree with TALYS) and within the engine's
  own channel differences at 14 MeV; the 846.8 keV Fe-56 line within 2 %; xsngn and Eaverage at 1 and 5 MeV to 1e-3.
"""

from __future__ import annotations

import math
import os
import sys
from pathlib import Path

import numpy as np
import pytest

from physics.hf import specobs

ROOT = Path(__file__).resolve().parents[2]
STOCK = Path(os.environ.get("KWCOV_STOCK", Path.home() / "kwcov/stock"))
TALYS_DIR = Path(os.environ.get("TALYS_DIR", Path.home() / "opt/talys-src"))


def test_keywords_and_defaults(monkeypatch):
    from physics.hf.input.defaults import default_options

    monkeypatch.delenv(specobs.ENV, raising=False)
    o = default_options(26, 56, "n")
    assert (o.flagspec, o.ddxmode, o.flaggamdis, o.fileddxa, o.filespectrum) == (False, 0, False, (), ())
    assert specobs.settings(o) is None and not specobs.ddx_wanted(o)
    o = default_options(26, 56, "n", {"ddxmode": 2, "fileddxa": "n 30,90 p 150", "fileddxe": "n,3.0"})
    s = specobs.settings(o)
    assert s["spec"] and s["ddx"] and not s["gamdis"]  # ddxmode > 0 implies outspectra (input_output.f90:283-285)
    assert s["fileddxa"] == (("n", 30.0), ("n", 90.0), ("p", 150.0)) and s["fileddxe"] == (("n", 3.0),)
    assert s["filespectrum"] == set("gnpdtha")
    s = specobs.settings(default_options(26, 56, "n", {"outgamdis": "y", "filespectrum": "n p"}))
    assert s["gamdis"] and not s["spec"] and s["filespectrum"] == {"n", "p"}
    e = default_options(26, 56, "n", {"endf": "y"})  # input_output.f90:125-142, input_directpar.f90:57-62
    assert e.flagspec and e.flagblockspectra and e.flagblockddx and e.flaggamdis and e.ddxmode == 0
    assert e.eadd_mev == 30.0
    d = default_options(1, 2, "d", {"endf": "y"})
    assert d.ddxmode == 2
    assert default_options(26, 56, "n", {"recoil": "y"}).flagspec
    monkeypatch.setenv(specobs.ENV, "1")
    s = specobs.settings(default_options(26, 56, "n"))
    assert s["spec"] and s["gamdis"] and s["ddxmode"] == 3


def test_anglecont_and_names():
    th = specobs.anglecont(18)
    assert th.size == 19 and th[1] == 10.0 and th[-1] == 180.0
    assert specobs._ddx_name("n", "A", 30.0) == "nddxA030.0.deg"
    assert specobs._ddx_name("p", "A", 152.5) == "pddxA152.5.deg"
    assert specobs._ddx_name("n", "E", 3.0) == "nddxE0003.0.MeV"
    assert specobs._efile(14.0) == "0014.000"


def _record(k0=1, elastic=100.0):
    """A synthetic specout energy: neutron out, flat continuum, two discrete levels."""
    eg = np.concatenate([[0.0], np.arange(1, 141) * 0.1])  # 0.1 MeV steps to 14 MeV
    from physics.hf.emission.binspec import _edges

    eb, et, de = _edges(eg, len(eg) - 1)
    E = len(eg)
    ent = dict(ebegin=1, eend=135, nendisc=125, nlast=1, xsemis=np.where(np.arange(E) <= 125, 10.0, 0.0),
               xspreeq=np.zeros(E), xsgr=np.zeros(E), lines_e=[13.0, 12.5], lines_xs=[0.0, 50.0])
    return dict(e_inc_mev=13.0, egrid=eg, ebottom=eb, etop=et, deltae=de, eninccm=12.8,
                binary={"types": {1: ent}, "xsbinary_full": [0.0] * 8}, xsemis_mul_talys=np.zeros((7, E)),
                xsmpeemis_talys=np.zeros((7, E)), per_nucleus_talys={}, walks={}), elastic


def test_fine_grid_and_peaks():
    r, el = _record()
    s = dict(k0=1, Z=26, A=56, eadd=0.0, eaddel=0.0, elwidth=0.5, segment=1, flagendf=False, echannel=False,
             ddx=False, nangle=90, nanglecont=18)
    out = specobs.energy_spectra(r, s, el)["types"][1]
    E = out["E"]
    # spectra.f90: egrid up to Elast = eoutdis(NL) - elwidth = 12 MeV, then 1 / (segment * fine) = 0.1 MeV steps
    # for int(fine * segment * (egrid(eend) - egrid(nend))) + 8 fine points
    assert np.allclose(E[:120], r["egrid"][1:121]) and E.size == 120 + 15 + 80
    assert np.allclose(np.diff(E[119:]), 0.1)
    # the elastic peak (addelastic y) carries xselastot (Gaussian of width elwidth (E/Ecm)^1.5, cut 2 sigma below)
    s["eaddel"] = 1000.0  # addelastic n
    out2 = specobs.energy_spectra(r, s, el)["types"][1]
    d = np.trapezoid(out["direct"] - out2["direct"], E)
    sel = 0.5 * (13.0 / 12.8) ** 1.5
    assert d == pytest.approx(el * 0.5 * (1 + math.erf(1.0 / (sel * math.sqrt(2)))), rel=1e-2)  # + the trapezoid at the cut
    k = int(np.argmin(np.abs(E - 12.5)))  # the inelastic peak's top: xsdisc / (sigma sqrt(2 pi))
    sig = 0.5 * (12.5 / 12.8) ** 1.5
    assert out2["direct"][k] == pytest.approx(50.0 / (sig * math.sqrt(2 * math.pi)), rel=1e-6)
    s["eadd"] = 1000.0  # adddiscrete n: no fine grid for neutrons
    out3 = specobs.energy_spectra(r, s, el)["types"][1]
    assert out3["E"].size == 135 and not np.any(out3["direct"])


def _built() -> bool:
    try:
        from physics.hf import engine_c

        return engine_c.lib() is not None
    except Exception:  # noqa: BLE001
        return False


_ENGINE = (TALYS_DIR / "structure").is_dir() and _built()


def _rd(p: Path) -> np.ndarray:
    return np.array([[float(x) for x in ln.split()] for ln in p.read_text().splitlines()
                     if ln.strip() and not ln.startswith("#")])


@pytest.mark.skipif(not _ENGINE or not (STOCK / "b4_fe56/nspec0014.000.tot").is_file(),
                    reason="needs TALYS structure/, a native build and the stock Fe-56 spectrum run")
def test_fe56_against_stock_talys(monkeypatch, tmp_path):
    sys.path.insert(0, str(ROOT / "scripts/kwcov"))
    import b4_compare as B
    import torch

    torch.set_num_threads(1)
    for k in (specobs.ENV, "INCOGNITA_SPECOUT", "INCOGNITA_ANGOUT", "INCOGNITA_ANGOUT_DIR"):
        monkeypatch.delenv(k, raising=False)
    monkeypatch.setenv(specobs.ENV_DIR, str(tmp_path))
    d = STOCK / "b4_fe56"
    E = [float(np.float32(float(x))) for x in (d / "energies").read_text().split()]
    try:
        res, on = B.engine_run(26, 56, E, B.KW_DEFAULT)
    finally:
        monkeypatch.delenv(specobs.ENV_DIR, raising=False)
    _, off = B.engine_run(26, 56, E, None)
    assert set(on) == set(off)
    for k in off:  # output only
        assert np.array_equal(off[k], on[k]), k
    sp = {k: v.numpy() for k, v in res.spectra.items()}
    assert res.angular == {}  # the DDX's discrete peaks used angout internally; no angle output was asked for
    for i, e in enumerate(E):
        for x in "np":
            f = d / f"{x}spec{B.efile(e)}.tot"
            if not f.is_file():
                continue
            st = _rd(f)
            oe = sp[f"{x}spec.tot:E"][i]
            m = np.isfinite(oe)
            assert m.sum() == st.shape[0] and np.abs(oe[m] - st[:, 0]).max() < 1e-4  # TALYS's espec grid
            ok = st[:, 1] > 1.0
            if not ok.any():
                continue
            r = sp[f"{x}spec.tot"][i][m][ok] / st[ok, 1]
            tol = 1e-3 if e < 10 else 0.16  # 14 MeV: the engine's own (n,n') (n,2n) (n,p) differences
            assert np.abs(r - 1).max() <= tol, (x, e, np.abs(r - 1).max())
            pe = st[:, 3] > 1.0  # pre-equilibrium needs no cascade: to 1e-3 at every energy
            if pe.any():
                assert np.abs(sp[f"{x}spec.tot:preeq"][i][m][pe] / st[pe, 3] - 1).max() <= 1e-3
            for g in d.glob(f"{x}ddxE{B.efile(e)}A*.deg"):
                sd = _rd(g)
                name = f"{x}ddx{g.name[len(x) + 12:]}"
                ok = sd[:, 1] > 0.1
                r = sp[name][i][m][ok] / sd[ok, 1]
                assert np.abs(r - 1).max() <= (2e-3 if e < 10 else 0.16), (name, e, np.abs(r - 1).max())
            if e < 10:
                ea = float(__import__("re").search(r"E-average \[MeV\]:\s*(\S+)", f.read_text()).group(1))
                assert sp[f"Eaverage_{x}.out"][i] == pytest.approx(ea, rel=1e-3)
    g = _rd(d / "gam026056L01L00.tot")  # the 846.8 keV line
    assert np.abs(sp["gam026056L01L00.tot"] / g[:, 1] - 1).max() <= 0.02
    assert sp["gam026056L01L00.tot:E"][0] == pytest.approx(0.846778, abs=1e-4)
    nn = _rd(d / "nn.tot")
    assert sp["nn.tot:ngn"][:2] == pytest.approx(nn[:2, 4], rel=1e-3)
    # the files: TALYS's names
    names = {p.name for p in tmp_path.iterdir()}
    assert {"nspec0014.000.tot", "nddxE0014.000A030.0.deg", "nddxE0014.000E0003.0.MeV", "gam026056L01L00.tot",
            "Eaverage_n.out"} <= names
    assert "emission spectrum" in (tmp_path / "nspec0014.000.tot").read_text()


@pytest.mark.skipif(not _ENGINE, reason="needs TALYS structure/ and a native build")
def test_port_switch_and_angle_output_together(monkeypatch):
    """INCOGNITA_SPECOBS=1 with `outangle y` + `fileangle 1`: both outputs, angout keeps its own level selection."""
    sys.path.insert(0, str(ROOT / "scripts/kwcov"))
    import b4_compare as B
    import torch

    torch.set_num_threads(1)
    for k in ("INCOGNITA_SPECOUT", "INCOGNITA_ANGOUT", specobs.ENV_DIR):
        monkeypatch.delenv(k, raising=False)
    monkeypatch.setenv(specobs.ENV, "1")
    try:
        res, _ = B.engine_run(26, 56, (float(np.float32(14.0)),), "fileelastic y;fileangle 1")
    finally:
        monkeypatch.delenv(specobs.ENV, raising=False)
    from physics.hf import specout

    assert not specout.ENERGIES and specout.RUN is None  # the recorders were cleared after the run
    sp = res.spectra
    assert sp["nddx"].shape[2] == 19 and "gam026056L01L00.tot" in sp and "nspec.tot" in sp
    assert set(res.angular) >= {"nnang.L00", "nnang.L01"} and "nnang.L02" not in res.angular
    # the DDX integrates over angle to the spectrum (Kalbach and isotropic parts are normalised)
    th = np.radians(sp["anglecont"].numpy())
    ddx = sp["nddx"][0].numpy()
    m = np.isfinite(ddx[:, 0])
    integ = 2 * math.pi * np.trapezoid(ddx[m] * np.sin(th), th, axis=1)
    spec = sp["nspec.tot"][0].numpy()[m]
    ok = (spec > 10.0) & (sp["nspec.tot:direct"][0].numpy()[m] < 0.01 * spec)  # continuum (peaks: 10-degree grid)
    assert ok.sum() > 20 and np.abs(integ[ok] / spec[ok] - 1).max() < 0.02
