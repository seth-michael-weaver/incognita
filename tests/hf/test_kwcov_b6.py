"""KWCOV B6: optical-model and direct-reaction keywords (docs/hf/COVERAGE_PLAN.md, batch B6).

`optmod`, `optmodfilen`, `optmodfilep`, the 12 `*adjustF` ranges, the energy-local forms of the 28 `ompadjust`
keywords (`v1adjust n 1. Ea Eb Em D`, `awdadjust n 1. <table>`), `incadjust`, `riplomp` now act as TALYS-2.25 reads
them; `statepot`, `rotational`, `sysreaction`, `ecisstep` and `ompenergyfile` (with endf y) refuse. The physics
response of each one was compared with stock TALYS by scripts/kwcov/b6_response.py (numbers in COVERAGE_PLAN.md B6);
these tests pin the parsing, TALYS's rules (adjust.f90 shape, ktype, incadjust) and the defaults.
"""
from __future__ import annotations

import os

import numpy as np
import pytest
import torch

from physics.hf.core.tensors import DTYPE
from physics.hf.input import defaults as D
from physics.hf.input import fitlib as F
from physics.hf.omp import ompdeck as OD
from physics.hf.omp.parameters import ejectile_params, omp_parameters

E = torch.tensor([1.0, 5.0, 6.0, 14.0, 25.0], dtype=DTYPE)


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


def _run(clean, lines: str, Z=26, A=56):
    clean.setenv(F.ENV_LINES, lines)
    F._cards.cache_clear()
    F.activate(Z, A)
    o = D.default_options(Z, A)
    return o, D.default_params(Z, A, o)


def _omp(o, p, Z=26, A=56, k=1, e=E):
    return omp_parameters(Z, A - Z, k, e, p, o)


# ------------------------------------------------------------------------------------------------ defaults

def test_defaults_unchanged(clean):
    o = D.default_options(26, 56)
    assert o.flagrot == () and o.flagsys == () and o.ompenergyfile == "" and o.flagincadj and o.ecisstep_fm == 0.0
    assert D.default_options(92, 238).riplomp[1] == 2408
    D.reject_unported(o)
    assert OD.active() is None and not OD.on()
    p = D.default_params(26, 56, o)
    assert ejectile_params(p, 1) is p                       # no copy at the defaults (every cache keeps its key)


# ------------------------------------------------------------------------------------------------ parsing

def _table(tmp_path, name="t.omp", head="  26  56 3", rows=((1.0, 40.0), (10.0, 44.0), (20.0, 48.0))):
    lines = [head] + [f"{e} {v} 1.2 0.66 1.0 1.2 0.66 0.0 1.2 0.6 7.0 1.28 0.54 6.0 1.0 0.58 -0.1 1.0 0.58 0.0"
                      for e, v in rows]
    (tmp_path / name).write_text("\n".join(lines) + "\n")
    return tmp_path / name


def test_extract_forms(tmp_path):
    t = _table(tmp_path)
    (tmp_path / "AwdAdj.Table").write_text("4.0 1.0\n6.0 0.5\n6.0 0.7\n8.0 1.0\n")
    keep, d = OD.extract([f"optmod 26 56 {t}", f"optmodfilen 26 {t}", "rvadjustf n 5 20 10 0",
                          "awdadjustf p 1 10 -5 2", "v1adjust n 1.05 3 16 10 1.03",
                          f"awdadjust n 2. {tmp_path}/awdadj.table", "rvadjust n 0.98", "ldmodel 2"], 26, 56)
    assert keep == ("v1adjust n 1.05", "awdadjust n 2.", "rvadjust n 0.98", "ldmodel 2")
    (tab,) = d.tables
    assert (tab.Z, tab.A, tab.k, len(tab.e)) == (26, 56, 1, 3) and tab.rows[1][0] == 44.0
    assert d.files == ((26, 1, str(t)),)
    assert d.ranges == ((1, 1, 5.0, 20.0, 10.0, 0.0), (2, 8, 1.0, 10.0, -5.0, 2.0))
    b1, b2 = d.bumps
    assert (b1.key, b1.k, b1.kind) == ("v1adjust", 1, "tal")
    assert b2.kind == "tab" and b2.args[0] == (4.0, 6.0, 8.0) and b2.args[1] == (2.0, 1.0, 2.0)  # value x D, dup E dropped
    cells = OD.range_cells(d)
    assert ("ompadjuste1", (2, 7, 0), 1.0) in cells and ("ompadjustd", (1, 0, 0), 10.0) in cells


def test_extract_refusals(tmp_path):
    with pytest.raises(ValueError, match="E1 E2 D s"):
        OD.extract(["rvadjustf n 5 20 10"], 26, 56)            # TALYS: read_error without s
    with pytest.raises(FileNotFoundError):
        OD.extract(["optmod 26 56 nosuch.omp"], 26, 56)
    with pytest.raises(FileNotFoundError):
        OD.extract(["awdadjust n 1. nosuch.table"], 26, 56)
    (tmp_path / "bad.table").write_text("5 1\n4 1\n")
    with pytest.raises(ValueError, match="increasing"):
        OD.extract([f"awdadjust n 1. {tmp_path}/bad.table"], 26, 56)
    keep, d = OD.extract(["v1adjust n 1.05 3 16"], 26, 56)    # incomplete range: the value only (getvalues err=10)
    assert keep == ("v1adjust n 1.05",) and d == ()


def test_adjust_shapes_are_adjust_f90():
    b = OD.TBump("v1adjust", 1, "tal", (3.0, 16.0, 10.0, 1.2))
    e = np.array([3.0, 6.5, 10.0, 13.0, 16.0, 20.0])
    f = OD._factor([b], e)
    db = 0.2 * (1 + 0.5**4)
    c = 3.0 + 3.5
    ref = 1 + db * (6.5 - 3) ** 4 / ((6.5 - 3) ** 4 + (c - 3) ** 4)
    assert f[0] == 1.0 and f[-1] == 1.0 and f[-2] == 1.0 and abs(f[2] - 1.2) < 1e-12 and abs(f[1] - ref) < 1e-12
    t = OD.TBump("awdadjust", 1, "tab", ((4.0, 6.0, 8.0), (1.0, 0.5, 1.0)))
    assert np.allclose(OD._factor([t], np.array([3.0, 4.0, 5.0, 7.0, 8.0, 9.0])), [1, 1, 0.75, 0.75, 1, 1])
    # the last line that covers E wins (adjust.f90 assigns, it does not multiply)
    assert np.allclose(OD._factor([b, t], np.array([5.0])), [0.75])


# ------------------------------------------------------------------------------------------------ the engine path

def test_energy_table_acts_on_the_incident_channel_only(clean, tmp_path):
    (tmp_path / "w.table").write_text("4.0 1.0\n6.0 0.5\n8.0 1.0\n")
    o0 = D.default_options(26, 56)
    p0 = D.default_params(26, 56, o0)
    base = _omp(o0, p0)
    o, p = _run(clean, f"awdadjust n 1. {tmp_path}/w.table")
    got = _omp(o, p)
    fac = (got.awd_fm / base.awd_fm).tolist()
    assert fac[0] == 1.0 and abs(fac[1] - 0.75) < 1e-6 and abs(fac[2] - 0.5) < 1e-6 and fac[3] == 1.0
    ej = _omp(o, ejectile_params(p, 1))                     # neutrons leaving: type 0, no table (flagompejec)
    assert torch.equal(ej.awd_fm, base.awd_fm)


def test_bump_on_an_ejectile_type_acts_on_its_channels(clean):
    o0 = D.default_options(26, 56)
    base = _omp(o0, ejectile_params(D.default_params(26, 56, o0), 1), Z=25, A=56, k=2)
    o, p = _run(clean, "d1adjust p 1.0 1 15 8 1.2")
    got = _omp(o, ejectile_params(p, 1), Z=25, A=56, k=2)
    assert float(got.wd_mev[2] / base.wd_mev[2]) > 1.1 and float(got.wd_mev[4]) == float(base.wd_mev[4])


def test_incadjust_n(clean):
    o, p = _run(clean, "incadjust n;v1adjust n 1.05;awdadjust n 1. 3 16 10 1.2")
    assert not o.flagincadj and F.active().omp == ()            # the projectile's energy-local line never acts
    assert float(p["v1adjust"][1]) == 1.0                         # nor its value (ompadjust.f90:92)
    o0 = D.default_options(26, 56)
    assert torch.equal(_omp(o, p).v_mev, _omp(o0, D.default_params(26, 56, o0)).v_mev)


def test_adjustf_ranges_reach_the_potential(clean):
    o0 = D.default_options(26, 56)
    base = _omp(o0, D.default_params(26, 56, o0))
    o, p = _run(clean, "rvadjustf n 2 20 10 0")
    assert float(p["ompadjuste2"][1, 0, 0]) == 20.0 and float(p["ompadjustd"][1, 0, 0]) == 10.0
    r = (_omp(o, p).rv_fm / base.rv_fm).tolist()
    assert r[0] < 1.05 and r[3] > 1.05 and r[4] == 1.0          # peak at 11 MeV, 1 outside (2, 20)


def test_optmod_table(clean, tmp_path):
    t = _table(tmp_path)
    o0 = D.default_options(26, 56)
    base = _omp(o0, D.default_params(26, 56, o0))
    o, p = _run(clean, f"optmod 26 56 {t}")
    got = _omp(o, p)
    assert abs(float(got.v_mev[1]) - (40.0 + 4.0 * 4.0 / 9.0)) < 1e-5 and float(got.wd_mev[0]) == pytest.approx(7.0)
    assert float(got.v_mev[4]) == float(base.v_mev[4])           # 25 MeV: outside the table, KD03
    assert torch.equal(_omp(o, p, Z=26, A=54).v_mev, _omp(o0, D.default_params(26, 56, o0), Z=26, A=54).v_mev)


def test_optmodfile_replaces_the_element_file(clean, tmp_path):
    from physics.hf.core.constants import talys_structure_path

    src = (talys_structure_path() / "optical/neutron/n-Fe.omp").read_text().replace("  56.8 ", "  59.8 ")
    (tmp_path / "my-n-fe.omp").write_text(src)
    o0 = D.default_options(26, 56)
    base = _omp(o0, D.default_params(26, 56, o0))
    o, p = _run(clean, f"optmodfilen 26 {tmp_path}/my-n-fe.omp")
    assert float(_omp(o, p).v_mev[0]) > float(base.v_mev[0]) + 2.0
    # optmodfilep for an element without a database file (Mn): its A=56 entry is read
    (tmp_path / "p-mn.omp").write_text("  25  56   1\n" + "\n".join(
        (talys_structure_path() / "optical/proton/p-Fe.omp").read_text().splitlines()[6:10]) + "\n")
    pb = _omp(o0, D.default_params(26, 56, o0), Z=25, A=56, k=2)
    o, p = _run(clean, f"optmodfilep 25 {tmp_path}/p-mn.omp")
    assert float(_omp(o, p, Z=25, A=56, k=2).rv_fm[0]) != float(pb.rv_fm[0])


def test_riplomp_forms():
    assert D.default_options(92, 238, overrides={"riplomp": "n"}).riplomp == (0,) * 7
    o = D.default_options(26, 56, overrides={"riplomp": "p 5405"})
    assert o.riplomp[2] == 5405 and o.flagriplomp
    with pytest.raises(ValueError):
        D.default_options(26, 56, overrides={"riplomp": "y"})


def test_deck_lines_with_several_words(clean):
    clean.setenv(F.ENV_LINES, "riplomp n;fileddxa n 30;rotational n p")
    c = F.cards(92, 238)
    assert dict(c.options)["riplomp"] == "n" and dict(c.options)["fileddxa"] == "n 30"
    assert D.default_options(92, 238, overrides=c.option_overrides).flagrot == ("n", "p")


@pytest.mark.parametrize("ov", [{"statepot": "y"}, {"rotational": "n"}, {"sysreaction": "p"}, {"ecisstep": 0.1},
                                {"ompenergyfile": "e.dat", "endf": "y"}])
def test_unported_are_refused(ov):
    with pytest.raises(NotImplementedError):
        D.reject_unported(D.default_options(26, 56, overrides=ov))


def test_accepted_without_effect_as_in_talys():
    for ov in ({"ompenergyfile": "e.dat"}, {"coulomb": "n"}, {"eciscompound": "y"}, {"sysreaction": ""}):
        D.reject_unported(D.default_options(26, 56, overrides=ov))
