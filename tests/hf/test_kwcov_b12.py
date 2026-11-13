"""KWCOV B12: recoils and the LAB frame (docs/hf/COVERAGE_PLAN.md, batch B12).

recoil / labddx / recoilaverage / maxenrec / anglesrec: TALYS's recoil module (recoilinit, binaryrecoil, angdisrecoil,
comprecoil, cm2lab, labsurface, binsurface, totalrecoil, recoilout and the LAB parts of spectraout / ddxout /
channelsout) on the run's specout records, physics/hf/recoil.py + physics/hf/native/recoil.c. The decks were compared
with stock TALYS-2.25 by scripts/kwcov/b12_response.py (numbers in the plan); the tests here pin the geometry, the
kinematics against stock's recoil grids, the parsing and the refusals, and one engine run against stock's n + Fe-56
1 MeV files (`recoil y`, `labddx y`, `ddxmode 3`, `fileddxa n 30`; stock TALYS-2.25, default deck otherwise).
"""
from __future__ import annotations

import math
import os

import numpy as np
import pytest

from physics.hf import recoil as R
from physics.hf.input import defaults as D
from physics.hf.input import fitlib as F

# stock TALYS-2.25 n + Fe-56, 1 MeV: rec026056spec0001.000.tot, rec026057spec0001.000.tot, nspec0001.000.lab,
# nddxE0001.000A030.0.lab (E, xs)
REC_FE56 = [(1.657511E-03, 1.149599E+05), (4.972532E-03, 1.023574E+05), (8.287553E-03, 8.164744E+04),
            (1.160257E-02, 6.607492E+04), (1.491760E-02, 5.461548E+04), (1.823262E-02, 4.649628E+04),
            (2.154764E-02, 4.106638E+04), (2.486266E-02, 3.777405E+04), (2.817768E-02, 3.617107E+04),
            (3.149270E-02, 3.591256E+04), (3.480772E-02, 3.675180E+04), (3.812275E-02, 3.853832E+04),
            (4.143777E-02, 4.121457E+04), (4.475279E-02, 4.481638E+04), (4.806781E-02, 4.947113E+04),
            (5.138283E-02, 4.860045E+04), (5.469785E-02, 3.919985E+04), (5.801287E-02, 2.861487E+04),
            (6.132789E-02, 1.672489E+04), (6.464291E-02, 3.863490E+03), (6.795793E-02, 0.000000E+00)]
REC_FE57 = [(6.065437E-04, 0.0), (1.819631E-03, 0.0), (3.032718E-03, 0.0), (4.245806E-03, 0.0), (5.458893E-03, 0.0),
            (6.671980E-03, 3.168862E-19), (7.885068E-03, 2.581429E-08), (9.098154E-03, 3.341764E-01),
            (1.031124E-02, 8.641637E+01), (1.152433E-02, 2.048493E+02), (1.273742E-02, 2.656154E+02),
            (1.395050E-02, 3.072368E+02), (1.516359E-02, 3.266801E+02), (1.637668E-02, 3.245992E+02),
            (1.758977E-02, 3.024228E+02), (1.880286E-02, 2.658594E+02), (2.001594E-02, 2.239263E+02),
            (2.122903E-02, 1.424078E+02), (2.244212E-02, 5.976614E+01), (2.365520E-02, 1.386662E-01),
            (2.486829E-02, 9.088491E-07)]
NLAB = [(0.1, 1.396781E-02), (0.2, 1.118558E-02), (0.3, 8.855272E-03), (0.4, 6.518678E-03), (0.5, 4.604909E+02),
        (0.6, 7.007595E+03), (0.7, 7.666312E+03), (0.8, 7.669153E+03), (0.9, 7.486323E+03), (1.0, 1.694337E+03),
        (1.025, 0.0)]
NDDX30 = [(0.1, 1.169268E-03), (0.2, 9.468838E-04), (0.3, 7.544014E-04), (0.4, 5.645534E-04), (0.5, 3.891987E-04),
          (0.6, 9.456589E+02), (0.7, 1.189149E+03), (0.8, 1.189959E+03), (0.9, 1.190771E+03), (1.0, 5.153220E+02),
          (1.025, 0.0)]
# first recoil energy (Erec(0) = Erecmaxmax / (2 (maxenrec + 1))) of stock's 14 MeV files: (Zix, Nix) -> MeV
EREC0_14 = {(0, 1): 2.327831E-02, (0, 2): 1.490479E-02, (2, 2): 5.191060E-02, (1, 0): 2.073565E-02,
            (0, 0): 7.610458E-03}


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


def _fe56_settings():
    from physics.hf.core.constants import talys_constants
    from physics.hf.structure.masses import masses

    o = D.default_options(26, 56, "n", overrides={"recoil": "y"})
    m = masses(o)
    c = talys_constants()
    s = R.settings(o)
    s.update(Z=26, A=56, k0=1, Zinit=26, Ninit=31, mass=np.asarray(m.mass_amu, float), sep=np.asarray(m.s_mev, float),
             parmass=tuple(float(x) for x in c["parmass"]), amu=float(c["amu"]), numenrec=D.NUMENREC, elwidth=0.5)
    return s


# ------------------------------------------------------------------------------------------------ geometry
def _clip_area(tri, xl, xu, yl, yu):
    """Reference: exact area of a triangle inside a rectangle (Sutherland-Hodgman)."""
    poly = list(tri)
    for side in range(4):
        out = []
        for i in range(len(poly)):
            (sx, sy), (ex, ey) = poly[i], poly[(i + 1) % len(poly)]
            ds, de = ((sx - xl, ex - xl), (xu - sx, xu - ex), (sy - yl, ey - yl), (yu - sy, yu - ey))[side]
            if ds >= 0:
                out.append((sx, sy))
            if (ds >= 0) != (de >= 0):
                t = ds / (ds - de)
                out.append((sx + t * (ex - sx), sy + t * (ey - sy)))
        poly = out
        if len(poly) < 3:
            return 0.0
    return abs(0.5 * sum(poly[i][0] * poly[(i + 1) % len(poly)][1] - poly[(i + 1) % len(poly)][0] * poly[i][1]
                         for i in range(len(poly))))


def test_binsurface():
    tri = ((0.1, 0.2), (1.3, 0.5), (0.4, 1.6))  # no vertical / horizontal side: the exact overlap
    for xl, xu, yl, yu in ((0.5, 1.0, 0.5, 1.0), (0.0, 2.0, 0.0, 2.0), (0.2, 0.6, 0.1, 0.4), (1.0, 1.2, 0.3, 0.9)):
        v = R.binsurface(*tri[0], *tri[1], *tri[2], xl, xu, yl, yu, 99.0)
        assert v == pytest.approx(_clip_area(tri, xl, xu, yl, yu), rel=1e-12, abs=1e-15), (xl, xu, yl, yu)
    assert R.binsurface(*tri[0], *tri[1], *tri[2], 0.4, 0.5, 0.6, 0.7, 99.0) == 99.0  # bin inside: surfbin
    # intri.f90 / sideline.f90 quirk: with a vertical or horizontal side, sideline returns a distance and intri compares
    # it for equality, so the corners of a bin inside the right triangle are not "inside": the polygon path is taken
    assert R.binsurface(0, 0, 1, 0, 0, 1, 0, 0.5, 0, 0.5, 99.0) == pytest.approx(0.25)
    assert R.binsurface(0, 0, 1, 0, 0, 1, 0.5, 1.0, 0.0, 0.5, 99.0) == pytest.approx(0.125)


def _grid(n=4, nang=3, ej=False):
    edges = np.linspace(0.0, 1.0, n + 2)
    th = np.linspace(0.0, 180.0, nang + 1)
    d = 180.0 / nang
    cmin = np.zeros(2 * nang + 2)
    cmax = np.zeros(2 * nang + 2)
    cmin[: nang + 1] = np.cos(np.radians(np.maximum(0.0, th - 0.5 * d)))
    cmax[: nang + 1] = np.cos(np.radians(np.minimum(180.0, th + 0.5 * d)))
    for i in range(nang + 1, 2 * nang + 2):
        cmin[i], cmax[i] = -cmin[i - nang - 1], -cmax[i - nang - 1]
    area = (np.diff(edges)[:, None] * np.abs(cmin - cmax)[None, :]).copy()
    return dict(ix0=1 if ej else 0, ixmax=n, nang=nang, ej=ej, xmin=edges[:-1].copy(), xmax=edges[1:].copy(),
                area=area, cmin=cmin, cmax=cmax)


def test_labsurface_conserves_area():
    g = _grid()
    scov = np.zeros((g["ixmax"] + 2, 2 * g["nang"] + 2))
    pts = ((0.1, 0.9, 0.3), (0.7, 0.2, 0.9), (0.4, -0.5, 0.8))
    ts, lx, ly = R.labsurface(g, pts, scov)
    tot = sum(scov[ix, iy % (2 * g["nang"] + 2)] for ix in range(lx[0], lx[1] + 1) for iy in range(ly[0], ly[1] + 1))
    assert tot == pytest.approx(ts, rel=1e-12)
    # the triangle in (E, unfolded cosine): |0.5 ((x1-x3)(y2-y3) - (x2-x3)(y1-y3))|
    y = [c for _, c, _ in pts]
    x = [p[0] for p in pts]
    assert ts == pytest.approx(abs(0.5 * ((x[0] - x[2]) * (y[1] - y[2]) - (x[1] - x[2]) * (y[0] - y[2]))))
    # a point beyond the last bin extends it (labsurface.f90: Erecmax(maxenrec) = x)
    g2 = _grid()
    R.labsurface(g2, ((1.5, 0.9, 0.1), (0.2, 0.8, 0.2), (0.3, 0.7, 0.3)), np.zeros_like(scov))
    assert g2["xmax"][g2["ixmax"]] == 1.5


@pytest.mark.skipif(R._lib() is None, reason="native/lib/librecoil.so not built (scripts/build_recoil_native.sh)")
def test_native_scatter_matches_python():
    rng = np.random.default_rng(12)

    def state():
        g = _grid(n=6, nang=2)
        return dict(maxenrec=6, nr=2, cmin=g["cmin"], cmax=g["cmax"], Erecmin=np.r_[g["xmin"], 0.0].copy(),
                    Erecmax=np.r_[g["xmax"], 0.0].copy(), area=np.r_[g["area"], np.zeros((1, 6))].copy(),
                    ddxrec=np.zeros((4, 7, 3)), ddxrectot=np.zeros(4))

    th = np.radians(np.linspace(0, 180, 7))
    cells = []
    for k in range(40):
        i = int(rng.integers(0, 6))
        e1 = float(rng.uniform(0.5, 3.0))
        cells.append([e1, e1 + 0.3, math.cos(th[i]), math.cos(th[i + 1]), max(math.sin(th[i]), 1e-6),
                      max(math.sin(th[i + 1]), 1e-6), 0.002, float(rng.uniform(0.1, 2.0)), 1.0 + k % 2, k % 3, k % 3 + 1])
    a, b = state(), state()
    em, rm = 939.565, 52000.0
    R.scatter_py(np.array(cells), 1, em, rm, a, True, None, False)
    R.scatter(np.array(cells), 1, em, rm, b, True, None, False)
    # the library works in single precision (TALYS's real(sgl)), the Python twin in double
    assert np.allclose(a["ddxrec"], b["ddxrec"], rtol=2e-4, atol=1e-6 * float(np.max(a["ddxrec"])))
    assert np.allclose(a["ddxrectot"], b["ddxrectot"], rtol=2e-4)
    assert a["Erecmax"][6] == pytest.approx(b["Erecmax"][6], rel=1e-6)
    # flux conservation: what went in (flux / divide on every iex row) = what ddxrectot booked
    put = sum(c[7] / c[8] * (c[10] - c[9] + 1) for c in cells)
    assert float(np.sum(b["ddxrectot"])) == pytest.approx(put, rel=1e-5)


# ------------------------------------------------------------------------------------------------ kinematics
def test_recoil_grids_equal_stock_fe56_14mev():
    s = _fe56_settings()
    from physics.hf.structure.masses import masses

    o = D.default_options(26, 56, "n")
    m = masses(o)
    tm = float(m.mass_amu[0, 1])
    etotal = 14.0 * tm / (tm + 1.00866491600) + float(s["sep"][0, 0, 1])
    _, emax = R._recoil_kinematics(s, 14.0, etotal)
    for key, e0 in EREC0_14.items():
        assert emax[key] / (2 * (s["maxenrec"] + 1)) == pytest.approx(e0, rel=5e-4), key  # etotal here is approximate (the engine run: exact)


def test_erecinit_single_precision_quirk(monkeypatch):
    """recoilinit.f90 computes the CN recoil energy as sqrt(P^2 + M^2) - M in real(sgl): it moves in steps of the float32
    spacing of M (1/256 MeV for Fe-57). The port keeps it (stock's 1 MeV Fe-57 recoil spectrum needs it);
    INCOGNITA_RECOIL_EXACT=1 gives the double-precision value."""
    s = _fe56_settings()
    e32, _ = R._recoil_kinematics(s, 1.0, 8.6)
    assert (e32 * 256.0) == pytest.approx(round(e32 * 256.0), abs=1e-6)
    monkeypatch.setenv(R.ENV_EXACT, "1")
    e64, _ = R._recoil_kinematics(s, 1.0, 8.6)
    assert e64 == pytest.approx(1.0 * 1.00866 / 56.94, rel=2e-3)
    assert abs(e32 - e64) > 1e-3


# ------------------------------------------------------------------------------------------------ input
def test_options_and_checks():
    o = D.default_options(26, 56, "n", overrides={"recoil": "y"})
    assert o.flagrecoil and o.flagspec and o.nanglerec == 1 and o.maxenrec == D.NUMENREC
    o = D.default_options(26, 56, "n", overrides={"recoil": "y", "labddx": "y", "recoilaverage": "y",
                                                  "maxenrec": "10"})
    assert o.flaglabddx and o.flagrecoilav and o.nanglerec == D.NUMANGREC and o.maxenrec == 10
    s = R.settings(o)
    assert s["labddx"] and s["recoilav"] and s["maxenrec"] == 10 and s["nanglerec"] == 9
    assert R.settings(D.default_options(26, 56, "n")) is None  # default: nothing
    with pytest.raises(ValueError, match="anglesrec 12 out of range 1-9"):
        R.check(dict(s, nanglerec=12))
    with pytest.raises(ValueError, match="maxenrec 0 out of range"):
        R.check(dict(s, maxenrec=0))


def test_deck_lines_accepted(clean):
    clean.setenv(F.ENV_LINES, "recoil y;labddx y;anglesrec 4;maxenrec 12;recoilaverage y;channelenergy y")
    F._cards.cache_clear(); F.deactivate()
    F.activate(26, 56)
    o = D.default_options(26, 56, "n")
    assert o.flagrecoil and o.flaglabddx and o.nanglerec == 4 and o.maxenrec == 12 and o.flagrecoilav
    assert o.flagEchannel


# ------------------------------------------------------------------------------------------------ engine
def _ln(a, b):
    return abs(math.log(a / b))


def test_engine_fe56_1mev_vs_stock(clean, tmp_path):
    """n + Fe-56 at 1 MeV, recoil y labddx y ddxmode 3 fileddxa n 30: the residual recoil spectra, the LAB neutron
    spectrum and the LAB DDX at 30 degrees vs stock (bins > 1 % of the maximum within 0.5 %); the defaults' arrays
    are unchanged by the switches; the files round-trip with TALYS's names."""
    import torch

    from physics.hf import engine_c, warmrun
    from physics.hf.engine import ChainedFull

    def run(lines):
        if lines:
            clean.setenv("INCOGNITA_TALYS_FIT", "lines")
            clean.setenv("INCOGNITA_TALYS_FIT_LINES", lines)
        else:
            clean.delenv("INCOGNITA_TALYS_FIT", raising=False)
            clean.delenv("INCOGNITA_TALYS_FIT_LINES", raising=False)
        F.deactivate(); F._cards.cache_clear()
        from physics.hf import chartrun

        chartrun.drop_target_caches()
        with torch.inference_mode():
            return engine_c.run(ChainedFull(Z=26, A=56, declared_energies=(1.0,)))

    clean.setenv(R.ENV_DIR, str(tmp_path))
    r = run("recoil y;labddx y;ddxmode 3;fileddxa n,30")
    rec = {k: v.numpy() for k, v in r.recoil.items()}
    for name, ref in (("rec026056spec.tot", REC_FE56), ("rec026057spec.tot", REC_FE57)):
        E, y = rec[name + ":E"][0], rec[name][0]
        ref = np.array(ref)
        assert np.allclose(E, ref[:, 0], rtol=1e-5)
        mx = ref[:, 1].max()
        for j in np.flatnonzero(ref[:, 1] > 1e-2 * mx):
            assert _ln(y[j], ref[j, 1]) < 5e-3, (name, j, y[j], ref[j, 1])
    assert float(rec["rec026056spec.tot:integral"][0]) == pytest.approx(3198.569, rel=2e-3)
    assert float(rec["rec026056spec.tot:production"][0]) == pytest.approx(2132.421, rel=2e-3)
    for name, ref in (("nspec.lab", NLAB), ("nddxA030.0.lab", NDDX30)):
        ref = np.array(ref)
        y = rec[name][0]
        assert np.sum(~np.isnan(y)) == len(ref)
        assert np.allclose(rec["nspec.lab:E"][0][: len(ref)], ref[:, 0], rtol=1e-5)
        mx = ref[:, 1].max()
        for j in np.flatnonzero(ref[:, 1] > 1e-2 * mx):
            assert _ln(y[j], ref[j, 1]) < 5e-3, (name, j, y[j], ref[j, 1])
    files = sorted(os.listdir(tmp_path))
    assert "rec026056spec0001.000.tot" in files and "nspec0001.000.lab" in files
    assert "nddxE0001.000A030.0.lab" in files and "sp100000E0001.000.rec" in files
    # `recoil y` with `outspectra n`: TALYS runs no binaryrecoil / comprecoil (flagspec n), only the discrete levels;
    # stock (same deck): Fe-57 1.823141 mb, Fe-56 3198.563 mb, no spectrum files
    clean.delenv(R.ENV_DIR, raising=False)
    r2 = run("recoil y;outspectra n")
    assert not r2.spectra
    assert float(r2.recoil["rec026057spec.tot:integral"][0]) == pytest.approx(1.823141, rel=2e-3)
    assert float(r2.recoil["rec026056spec.tot:integral"][0]) == pytest.approx(3198.563, rel=2e-3)
    # output only: every Results array of the default run is the same with the switches
    r0 = run("")
    assert not r0.recoil
    a, b = warmrun.result_arrays(r0), warmrun.result_arrays(r)
    assert set(a) == set(b)
    for k in a:
        assert np.array_equal(a[k], b[k]), k
