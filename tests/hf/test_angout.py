"""KWCOV B3 (ANGOUT): discrete angular distributions and Legendre coefficients on TALYS's keywords, output only.

* unit: keyword parsing (outangle, fileelastic, fileangle, blockangle, angles), the switch logic of angleout.f90 /
  output.f90:65, TALYS's angle grid and file names, the YANDF column header, the generalised Blatt-Biedenharn side
  (ceang_types) against ceang's spin-1/2 one, and the cleg sum against ceang.legendre;
* engine (needs a native build, TALYS structure/ and stock TALYS-2.25 runs made with scripts/kwcov/b3_compare.py's
  recipe in $KWCOV_STOCK/b3_fe56 (n + Fe-56, 1 5 14 MeV) and $KWCOV_STOCK/b3_nb93p (p + Nb-93, 5 14 MeV), each with
  `outangle y` and `outlegendre y`): every Results array is bit-identical with the switch on and off; elastic and the
  first two inelastic levels within 2 % of stock per angle where stock > 1 mb/sr; the (p,p) ratio to Rutherford within
  2 %; the deck-line route (`outangle y`, `angles 36` through INCOGNITA_TALYS_FIT_LINES) gives the 37-angle grid.
"""

from __future__ import annotations

import math
import os
import sys
from pathlib import Path

import numpy as np
import pytest

from physics.hf import angout

ROOT = Path(__file__).resolve().parents[2]
STOCK = Path(os.environ.get("KWCOV_STOCK", Path.home() / "kwcov/stock"))
TALYS_DIR = Path(os.environ.get("TALYS_DIR", Path.home() / "opt/talys-src"))


def test_keywords_and_defaults(monkeypatch):
    from physics.hf.input.defaults import default_options

    monkeypatch.delenv(angout.ENV, raising=False)
    o = default_options(26, 56, "n")
    assert (o.flagang, o.fileelastic, o.flagblockangle, o.fileangle, o.flaglegendre) == (False, False, False, (), False)
    assert angout.settings(o) is None  # angleout.f90 does not run: nothing is recorded
    o = default_options(26, 56, "n", {"fileangle": "1,2", "fileelastic": "y", "angles": 36})
    s = angout.settings(o)
    assert s["fileangle"] == {1, 2} and not s["fileangle_all"] and s["nangle"] == 36 and not s["flagang"]
    assert not angout.flagcompang(1.0, s)  # compound angular distributions need outangle (energies.f90)
    s = angout.settings(default_options(26, 56, "n", {"outangle": "y", "outlegendre": "y", "blockangle": "y"}))
    assert s["fileangle_all"] and s["legendre"] and s["block"] and angout.flagcompang(14.0, s)
    assert not angout.flagcompang(60.0, s)
    e = default_options(26, 56, "n", {"endf": "y"})  # input_output.f90:128-133, input_outfiles.f90:105
    assert e.flagang and e.fileelastic and e.flagblockangle and e.flaglegendre
    monkeypatch.setenv(angout.ENV, "1")
    s = angout.settings(default_options(26, 56, "n"))
    assert s["flagang"] and s["legendre"]


def test_cpang_and_charged_compang():
    from physics.hf.input.defaults import default_options

    s = angout.settings(default_options(41, 93, "p", {"outangle": "y"}))
    assert not angout.flagcompang(14.0, s)
    s = angout.settings(default_options(41, 93, "p", {"outangle": "y", "cpang": "y"}))
    assert angout.flagcompang(14.0, s)


def test_angle_grid_and_file_names():
    th = angout.angles(90)
    assert th.size == 91 and th[1] == 2.0 and th[-1] == 180.0
    th = angout.angles(36)
    assert th[1] == 5.0
    assert angout._fname("nn", "ang", 1, 14.0, False) == "nn0014.000ang.L01"
    assert angout._fname("np", "leg", 12, 0.5, False) == "np0000.500leg.L12"
    assert angout._fname("pp", "ang", 0, 123.456, False) == "pp0123.456ang.L00"
    assert angout._fname("nn", "ang", 1, 14.0, True) == "nnang.L01"


def test_yandf_column_header(tmp_path):
    p = tmp_path / "x"
    with open(p, "w") as f:
        angout._datablock(f, 2, ["Angle", "xs", "Direct", "Compound"], ["deg", "mb/sr", "mb/sr", "mb/sr"], 91)
        angout._datablock(f, 2, ["L", "Total", "Direct", "Compound", "Normalized", "ENDF-6"], [""] * 6, 26)
    got = p.read_text().splitlines()
    # TALYS-2.25 write_block.f90 output, copied from nn0014.000ang.L00 / nn0014.000leg.L01
    assert got[3] == "##     Angle           xs           Direct        Compound"
    assert got[4] == "##     [deg]         [mb/sr]        [mb/sr]        [mb/sr]"
    assert got[8] == "##       L            Total         Direct        Compound      Normalized       ENDF-6"
    assert got[9] == "##      []             []             []             []             []             []"


@pytest.mark.parametrize("J2,l,j2,ti,L", [(3, 1, 3, 0, 2), (5, 2, 5, 1, 2), (7, 3, 5, 3, 4), (9, 4, 9, 4, 6)])
def test_side_spin_half_is_ceang(J2, l, j2, ti, L):
    from physics.hf.compound import ceang, ceang_types

    assert ceang_types.side(J2, l, j2, ti, L, 1) == pytest.approx(ceang._side(J2, l, j2, ti, L), abs=1e-14)


def test_legendre_matches_ceang_for_nucleons():
    from physics.hf.compound import ceang, ceang_types

    rng = np.random.default_rng(1)
    ti0, tin = 0, 4
    blocks = []
    for J2 in range(1, 25, 2):
        inn = [(l, jj) for jj in range(abs(J2 - ti0), J2 + ti0 + 1, 2) for l in range(10) if jj in (2 * l - 1, 2 * l + 1)]
        out = [(l, jj) for jj in range(abs(J2 - tin), J2 + tin + 1, 2) for l in range(10) if jj in (2 * l - 1, 2 * l + 1)]
        if inn and out:
            blocks.append({"J2": J2, "l_in": [x[0] for x in inn], "j2_in": [x[1] for x in inn],
                           "levels": {1: {"l_out": [x[0] for x in out], "j2_out": [x[1] for x in out],
                                          "M": rng.uniform(0, 1, (len(inn), len(out)))}}})
    a = ceang.legendre({"blocks": blocks}, 1, ti0, tin, 16)
    b = ceang_types.legendre({"blocks": blocks}, 1, ti0, 1, tin, 1, 16)
    assert np.abs(a - b).max() <= 1e-13 * np.abs(a).max()


def test_spin0_exit_is_isotropic_for_spin0_states():
    """An alpha (s = 0) leaving a J = 1/2 compound state by l' = 0 for a 1/2 level after a single incident s-wave
    (l = 0, j = 1/2): every L > 0 term vanishes (isotropic), and cleg_0 = M / (4 pi)."""
    from physics.hf.compound import ceang_types

    rec = {"blocks": [{"J2": 1, "l_in": [0], "j2_in": [1], "levels": {0: {"l_out": [0], "j2_out": [0], "M": np.ones((1, 1))}}}]}
    c = ceang_types.legendre(rec, 0, 0, 1, 1, 0, 8)
    assert c[0] == pytest.approx(1 / (4 * math.pi)) and np.allclose(c[1:], 0.0)


def _built() -> bool:
    try:
        from physics.hf import engine_c

        return engine_c.lib() is not None
    except Exception:  # noqa: BLE001
        return False


_ENGINE = (TALYS_DIR / "structure").is_dir() and _built()


@pytest.mark.skipif(not _ENGINE or not (STOCK / "b3_fe56/nn0014.000ang.L01").is_file(),
                    reason="needs TALYS structure/, a native build and the stock Fe-56 angular run")
def test_fe56_against_stock_talys(monkeypatch):
    sys.path.insert(0, str(ROOT / "scripts/kwcov"))
    import b3_compare as B

    monkeypatch.setenv(angout.ENV, "0")  # b3_compare sets os.environ directly: teardown restores the state before it
    monkeypatch.setenv("INCOGNITA_ANGOUT_DIR", "")
    monkeypatch.delenv("INCOGNITA_ANGOUT_DIR")
    import torch

    torch.set_num_threads(1)
    monkeypatch.delenv("INCOGNITA_SPECOUT", raising=False)
    monkeypatch.delenv(angout.ENV_DIR, raising=False)
    d = STOCK / "b3_fe56"
    E = [float(np.float32(float(x))) for x in (d / "energies").read_text().split()]
    res, on = B.engine_run(26, 56, E, True)
    _, off = B.engine_run(26, 56, E, False)
    monkeypatch.delenv(angout.ENV, raising=False)
    assert set(on) == set(off)
    for k in off:  # output only
        assert np.array_equal(off[k], on[k]), k
    ang = {k: v.numpy() for k, v in res.angular.items()}
    th = ang["angle"]
    st = B.stock_files(d, "n")
    scored = 0
    for (stem, kind, n, e), s in st.items():
        if kind != "ang" or stem != "nn" or n > 2:
            continue
        i = int(np.argmin(np.abs(np.asarray(E) - e)))
        name = f"nnang.L{n:02d}"
        m = (s[:, 1] > 1.0) & (th > 0)
        if not m.any():
            continue
        r = ang[name][i][m] / s[m, 1]
        assert np.abs(r - 1).max() <= 0.02, (name, e, np.abs(r - 1).max())
        scored += int(m.sum())
    assert scored >= 400
    # integrals: compound elastic and the level cross section
    x = np.cos(np.radians(th))
    w = 2 * math.pi * np.abs(np.trapezoid(ang["nnang.L01"][2], x))
    assert w == pytest.approx(float(res.levels_mb["nn.L01"][2]), rel=5e-3)
    # a Legendre file's L = 0 total is sigma / (4 pi)
    assert 4 * math.pi * ang["nnleg.L01"][2, 0] == pytest.approx(float(res.levels_mb["nn.L01"][2]), rel=1e-6)


@pytest.mark.skipif(not _ENGINE or not (STOCK / "b3_nb93p/pp0014.000ang.L00").is_file(),
                    reason="needs TALYS structure/, a native build and the stock p + Nb-93 angular run")
def test_nb93_proton_rutherford(monkeypatch):
    sys.path.insert(0, str(ROOT / "scripts/kwcov"))
    import b3_compare as B

    monkeypatch.setenv(angout.ENV, "0")  # b3_compare sets os.environ directly: teardown restores the state before it
    monkeypatch.setenv("INCOGNITA_ANGOUT_DIR", "")
    monkeypatch.delenv("INCOGNITA_ANGOUT_DIR")
    import torch

    from physics.hf.chartrun import drop_target_caches

    torch.set_num_threads(1)
    monkeypatch.setenv("INCOGNITA_CPINC", "p")
    monkeypatch.delenv("INCOGNITA_SPECOUT", raising=False)
    d = STOCK / "b3_nb93p"
    E = [float(np.float32(float(x))) for x in (d / "energies").read_text().split()]
    try:
        res, _ = B.engine_run(41, 93, E, True)
    finally:
        monkeypatch.delenv(angout.ENV, raising=False)
        monkeypatch.delenv("INCOGNITA_CPINC", raising=False)
        drop_target_caches()
    ang = {k: v.numpy() for k, v in res.angular.items()}
    th = ang["angle"]
    for i, e in enumerate(E):
        s = B.read_cols(d / f"pp{int(e):04d}{f'{e:8.3f}'[4:]}ang.L00")
        m = th > 0
        assert np.abs(ang["ppang.L00:ruth"][i][m] / s[m, 4] - 1).max() <= 0.02
        assert np.abs(ang["ppang.L00"][i][m] / s[m, 1] - 1).max() <= 0.02


@pytest.mark.skipif(not _ENGINE, reason="needs TALYS structure/ and a native build")
def test_deck_lines_route(monkeypatch, tmp_path):
    """`outangle y`, `angles 36`, `blockangle y` as deck lines (fitlib's lines arm): the angle grid follows `angles`,
    the files are written under their blockangle names, and nothing else changes."""
    import torch

    from physics.hf import engine_c, warmrun
    from physics.hf.chartrun import drop_target_caches
    from physics.hf.engine import ChainedFull

    torch.set_num_threads(1)
    for k in (angout.ENV, "INCOGNITA_SPECOUT", "INCOGNITA_TALYS_FIT", "INCOGNITA_TALYS_FIT_LINES"):
        monkeypatch.delenv(k, raising=False)
    e = (float(np.float32(5.0)),)

    def run():
        drop_target_caches()
        with torch.inference_mode():
            r = engine_c.run(ChainedFull(Z=26, A=56, declared_energies=e))
        return r, warmrun.result_arrays(r)

    _, off = run()
    monkeypatch.setenv("INCOGNITA_TALYS_FIT", "lines")
    monkeypatch.setenv("INCOGNITA_TALYS_FIT_LINES", "outangle y;angles 36;blockangle y;outlegendre y")
    monkeypatch.setenv(angout.ENV_DIR, str(tmp_path))
    try:
        res, on = run()
    finally:
        for k in ("INCOGNITA_TALYS_FIT", "INCOGNITA_TALYS_FIT_LINES", angout.ENV_DIR):
            monkeypatch.delenv(k, raising=False)
        from physics.hf.input import fitlib

        fitlib.deactivate()  # the deck's fitted keyword lines stay active until the next Cascade otherwise
        drop_target_caches()
    for k in off:
        assert np.array_equal(off[k], on[k]), k
    assert res.angular["angle"].numel() == 37 and res.angular["nnang.L00"].shape == (1, 37)
    assert (tmp_path / "nnang.L00").is_file() and (tmp_path / "nnleg.L01").is_file()
    assert "angular distribution" in (tmp_path / "nnang.L01").read_text()
