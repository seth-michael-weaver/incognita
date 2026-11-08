"""KWCOV B15: low-value leftovers and checks (docs/hf/COVERAGE_PLAN.md, batch B15).

* TALYS input checks the port lacked (checkvalue.f90): legacy models without `legacy y`, `transpower` 2..20;
* `transpower` / `transeps` reach the lmax cut of every transmission read (inverseread.f90 / incidentread.f90);
* `endf y`'s structure files (levels*.out and gamma*.tot of every nucleus structure builds) and endfinfo.f90's
  tefal.inf / energies.endf; `sacs y` (sacs.dat); `components y` refused; `micro`, `endfdetail` cascades;
* INCOGNITA_FIDFIX `psfsgl` (U-239 E1 at 0.4 / 0.6 MeV: the single-precision table energies of gammapar.f90).

Stock numbers: TALYS-2.25 n + Fe-56 decks under ~/kwcov/stock/b15 (endf y at 1/5/14 MeV, sacs y at 2..20 MeV, the
refused decks' TALYS-error lines), transcribed here.
"""
from __future__ import annotations

import re
import types

import numpy as np
import pytest
import torch

from physics.hf import fidfix
from physics.hf import ingout as G
from physics.hf.input import defaults as D
from physics.hf.omp import inverse as INV


def _opts(Z=26, A=56, **ov):
    return D.default_options(Z, A, "n", ov)


@pytest.fixture(autouse=True)
def _reset_eps():
    yield
    INV.set_eps(5, 1.0e-8)


# ------------------------------------------------------------------------------------------------ legacy checks
@pytest.mark.parametrize("ov, stock", [
    ({"strength": 1}, "strength = 8, 9, 10, 11, 12 or 13 are recommended. If you want to use legacy models put legacy y"),
    ({"strength": 5}, "strength = 8, 9, 10, 11, 12 or 13 are recommended"),
    ({"strengthm1": 2}, "strengthM1 = 3, 8, 10, 11 or 12 are recommended. If you want to use legacy models put legacy y"),
    ({"ldmodel": 3}, "ldmodelCN = 1, 2, 5, or 7 are recommended. If you want to use legacy models put legacy y"),
    ({"ldmodel": 4}, "= 1, 2, 5, or 7 are recommended"),
    ({"ldmodelcn": 6}, "ldmodelCN = 1, 2, 5, or 7 are recommended"),
])
def test_legacy_models_refused_without_legacy(ov, stock):
    # stock TALYS-2.25 Fe-56 `strength 1` / `strengthm1 2` / `ldmodel 3`: these TALYS-error lines, then stop
    o = _opts(**ov)
    with pytest.raises(ValueError, match=re.escape(stock.split(" are")[0])):
        D.reject_unported(o)
    D.reject_unported(_opts(legacy="y", **ov))  # legacy y: accepted, as TALYS


def test_legacy_per_nucleus_ldmodel():
    o = D.default_options(26, 56, "n", {"ldmodel 26 55": "4"})
    with pytest.raises(ValueError, match="ldmodel = 1, 2, 5, or 7"):
        D.reject_unported(o)


def test_defaults_pass_the_checks():
    for za in ((26, 56), (92, 238), (79, 197)):
        D.reject_unported(D.default_options(*za, "n", {}))
    D.reject_unported(_opts(strength=8))
    D.reject_unported(_opts(strengthm1=8))


def test_transpower_range():
    with pytest.raises(ValueError, match="transpower"):
        D.reject_unported(_opts(transpower=1))  # stock: range error, stop (checkvalue.f90:475)
    with pytest.raises(ValueError, match="transpower"):
        D.reject_unported(_opts(transpower=21))
    D.reject_unported(_opts(transpower=2))
    D.reject_unported(_opts(transpower=20))


# ------------------------------------------------------------------------------------------------ transpower / transeps
def test_transpower_reaches_the_lmax_cut():
    _opts()
    assert INV.eps() == (1.0e-5, 1.0e-8) and INV.eps_token() is None
    _opts(transpower=10)
    assert INV.eps() == (1.0e-10, 1.0e-8) and INV.eps_token() == (1.0e-10, 1.0e-8)
    _opts(massdis="y")  # input_numerics.f90:83-88
    assert INV.eps() == (1.0e-10, 1.0e-12)
    _opts(astro="y")  # :89-94
    assert INV.eps() == (1.0e-15, 1.0e-18)
    _opts(transeps=1.0e-12)
    assert INV.eps() == (1.0e-5, 1.0e-12)
    # a neutron T_lj falling by 1e-3 per l: T_0 = 1 -> lmax where T_l < max(T_0 translimit / (2l+1), transeps)
    t = torch.zeros(1, 12, 3, dtype=torch.float64)
    for ll in range(12):
        t[0, ll, :2] = 10.0 ** (-3 * ll)
    _opts()
    assert int(INV.process_tjl(t, 1)[2][0]) == 1  # l = 2: 1e-6 < 1e-5 / 5
    _opts(transpower=10)
    assert int(INV.process_tjl(t, 1)[2][0]) == 2  # l = 3: 1e-9 > 1e-8 (transeps) stops it
    _opts(transpower=10, transeps=1.0e-20)
    assert int(INV.process_tjl(t, 1)[2][0]) == 3  # l = 4: 1e-12 < 1e-10 / 9
    from physics.hf.omp.schrodinger import _lmax_talys

    assert int(_lmax_talys(t, 1)[0]) == 3


def test_stage_key_unchanged_at_defaults():
    from physics.hf import stagedisk

    _opts()
    k0 = stagedisk.key("t", (1,))
    _opts(transpower=10)
    k1 = stagedisk.key("t", (1,))
    _opts()
    assert stagedisk.key("t", (1,)) == k0 and k1 != k0


# ------------------------------------------------------------------------------------------------ keywords
def test_components_refused_sacs_accepted():
    with pytest.raises(NotImplementedError, match="components y"):
        D.reject_unported(_opts(components="y"))
    D.reject_unported(_opts(components="n"))
    o = _opts(sacs="y")
    assert o.flagsacs and G.active(o) == {"sacs": True}
    assert G.active(_opts()) == {}


def test_deck_routes_sacs_and_components():
    from physics.hf.input import fitlib as F

    opts, _c, _g, _p, skipped = F._split(["sacs y", "components y"], True)
    assert dict(opts) == {"sacs": "y", "components": "y"} and not skipped


def test_micro_cascade():
    o = _opts(micro="y")
    assert o.ldmodelall == 7 and o.flagjlm and o.flagautorot  # input_densitymodel.f90:84, ompmodel:98, directmodel:70
    with pytest.raises(NotImplementedError, match="jlmomp y"):  # JLM is unported (B7b)
        D.reject_unported(o)
    o = _opts(micro="y", jlmomp="n")
    assert o.ldmodelall == 7 and not o.flagjlm and o.flagautorot
    D.reject_unported(o)


def test_endf_and_endfdetail_cascade():
    o = _opts(endf="y")
    assert o.flagendfdet and o.flaggamdis and o.flagchannels and o.flagurr and o.eninclow_mev == 0.0
    assert {"levels", "endf"} <= set(G.active(o))
    o = _opts(endf="y", endfdetail="n")
    assert not o.flagendfdet and not o.flaggamdis and not o.flagchannels  # input_output.f90:140-143
    assert not _opts(endfdetail="n").flaggamdis


# ------------------------------------------------------------------------------------------------ files on a Cascade
@pytest.fixture(scope="module")
def fe56():
    from physics.hf.emission.feeding import Cascade

    return Cascade(26, 56, 14.0, energies=[1.0, 5.0, 14.0])


def test_gamma_decay_file_vs_stock(fe56):
    name, f = G.gamma_decay_file(fe56, 0, 1)
    assert name == "gamma026056.tot"
    b = f["blocks"][0]
    lev = {int(r[0]): r for r in b["data"]}
    # stock gamma026056.tot (endf y): level 1 / 3 / 6 rows and level 6's cascade
    assert lev[1][2] == 1 and lev[1][3] == pytest.approx(9.997041e-01, rel=2e-6)
    assert lev[3][2] == 3 and lev[3][3] == pytest.approx(1.969391, rel=2e-6)
    g6 = b["gammas"][5]
    assert [(int(x[0]), int(x[1])) for x in g6] == [(6, 0), (3, 0), (6, 1), (3, 1), (1, 0), (6, 3)]
    assert g6[:, 3] == pytest.approx([2.318738e-02, 1.520219e-04, 4.809017e-01, 4.901730e-03, 4.858034e-01,
                                      5.053752e-03], rel=2e-6)
    text = G._gammadecay_text(f)
    assert "#   entries: 273" in text.replace("     ", " ") or "entries: 273" in text


def test_endfinfo_vs_stock(fe56):
    res = types.SimpleNamespace(urr={"urr.dat": {}})
    out = G.endf_info(fe56, [1.0, 5.0, 14.0], res)
    assert out["energies.endf"]["text"] == " 1.00000E+00\n 5.00000E+00\n 1.40000E+01\n"
    stock = ("  1       : projectile type\n 26       : Z of target\n 56       : A of target\n"
             " 55.934936: mass of target in a.m.u.\n 0.0      : spin of target\n  0.000000: energy of target\n"
             "   0   0  : level and isomeric number of target\n   3      : number of incident energies\n"
             "  30      : number of discrete levels\nenergies.endf : file with incident energies\n"
             "y         : detailed ENDF-6 information per channel\ny         : keep elastic cross section in normalization\n"
             "n         : recoils\ny         : urr\ny         : block\n")
    o = fe56.options
    fe56.options = D.default_options(26, 56, "n", {"endf": "y"})
    try:
        assert G.endf_info(fe56, [1.0, 5.0, 14.0], res)["tefal.inf"]["text"] == stock
    finally:
        fe56.options = o


SACS_E = [2.0, 4.0, 6.0, 8.0, 10.0, 12.0, 14.0, 16.0, 18.0, 20.0]
SACS_XS = {  # stock xs*.tot (n + Fe-56, sacs y; channels y; filechannels y)
    "xs000000": [2.362976, 1.309066, 0.7841297, 0.778684, 0.9773583, 1.115284, 1.272394, 1.329591, 1.112683,
                 0.8575002],
    "xs100000": [987.971, 1388.14, 1520.583, 1450.468, 1383.773, 1256.001, 742.7106, 430.861, 304.3318, 250.3962],
    "xs010000": [0.0, 1.224975e-03, 9.141413, 58.65471, 94.28899, 119.2471, 124.8151, 82.99221, 52.00839, 38.93164],
    "xs200000": [0.0, 0.0, 0.0, 0.0, 0.0, 69.57549, 480.8369, 695.7523, 734.1539, 704.0347],
}
SACS_STOCK = [  # stock sacs.dat rows of those channels
    "  26  56 xs000000.tot      0.000   2.000 2.36298E+00     3.486",
    "  26  56 xs100000.tot      0.862   6.000 1.52058E+03    12.392",
    "  26  56 xs010000.tot      2.966  14.000 1.24815E+02     9.118",
    "  26  56 xs200000.tot     11.399  18.000 7.34154E+02     0.000",
]


def test_sacs_vs_stock(fe56):
    res = types.SimpleNamespace(e_inc_mev=torch.tensor(SACS_E, dtype=torch.float64),
                                channels_mb={k: torch.tensor(v, dtype=torch.float64) for k, v in SACS_XS.items()})
    o = fe56.options
    fe56.options = D.default_options(26, 56, "n", {"sacs": "y", "channels": "y"})
    try:
        text = G.sacs_table(fe56, res)["text"]
        fe56.options = D.default_options(26, 56, "n", {"sacs": "y"})
        bare = G.sacs_table(fe56, res)["text"]
    finally:
        fe56.options = o
    lines = text.splitlines()
    assert lines[0] == "# n + Fe56: Statistical analysis of cross sections"
    assert lines[2:] == SACS_STOCK
    assert len(bare.splitlines()) == 2  # stock `sacs y` without channels y: the header only (no xs files)


# ------------------------------------------------------------------------------------------------ FIDFIX psfsgl
def test_tqrpa_single_precision():
    tq = fidfix.tqrpa_sgl(11, 0.2)
    assert tq[2] == float(np.float32(0.4)) and tq[3] == float(np.float32(0.6))
    assert "psfsgl" in fidfix.FIXES


@pytest.mark.parametrize("fix, want", [("", (9.07574576e-10, 1.53618015e-09)), ("psfsgl", (2.11851e-09, 1.00962e-09))])
def test_u239_e1_at_tqrpa_points(monkeypatch, fix, want):
    """U-239 smlo2019 E1 at 0.4 / 0.6 MeV: stock 2.1185e-9 / 1.0096e-9 (psf092239.E1); the port's double-precision
    table energies gave 9.08e-10 / 1.54e-9 (B13 loss (1)); `psfsgl` restores stock."""
    from physics.hf.compound.psf_fast import _TABLES
    from physics.hf.emission.feeding import Cascade
    from physics.hf.gamma.strength import fstrength_gp

    monkeypatch.setenv(fidfix.ENV, fix)
    _TABLES.clear()
    gp = Cascade(92, 238, 1.0, energies=[1.0]).gamma_params(92, 238)
    if fix:  # the cached gamma parameters may predate the switch: rebuild the T grid as gammapar does
        gp = __import__("dataclasses").replace(gp, tqrpa_mev=torch.as_tensor(fidfix.tqrpa_sgl(11, 0.2)))
    f = fstrength_gp(gp, 0.0, torch.tensor([0.3, 0.4, 0.6], dtype=torch.float64), 1, 1).numpy()
    assert f[1:] == pytest.approx(want, rel=1e-5)
    assert f[0] == pytest.approx(1.784112e-09, rel=1e-5)  # off the T grid: both agree with stock


@pytest.mark.parametrize("line", ["rescuefile 102 rescue.102 0.9", "strucpath /tmp/structure/", "bestpath /tmp/best/"])
def test_silent_path_keywords_now_refused(line):
    """They were skipped without a word: rescuefile renormalises the returned cross sections (normalization.f90),
    strucpath / bestpath name another database than the one the port reads."""
    from physics.hf.input import fitlib as F

    _o, _c, _g, _p, skipped = F._split([line], True)
    with pytest.raises(ValueError, match="not applied by the port"):
        F._loud_skips(skipped, [line])
