"""KWCOV B8: fission extras (docs/hf/COVERAGE_PLAN.md, batch B8).

Per-fissioning-nuclide fission (rpZZZAAA.fis), the Iwamoto prompt fission neutron spectrum (pfnsmodel 1, tmadjust,
fsadjust), the Wahl nubar (cnubar1, cnubar2), fisfeed, and the fission model inputs axtype, hbtransfile, class2file.
The responses and the observables were compared with stock TALYS-2.25 by scripts/kwcov/b8_response.py (numbers in
the plan); the tests here pin the transcriptions against stock numbers, the parsing, the refusals and that the
fission extras are output only.
"""
from __future__ import annotations

import os

import numpy as np
import pytest

from physics.hf import fisobs
from physics.hf.input import defaults as D
from physics.hf.input import fitlib as F


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


def _cards(clean, lines: str, Z=92, A=238):
    clean.setenv(F.ENV_LINES, lines)
    F._cards.cache_clear()
    return F.cards(Z, A)


# ------------------------------------------------------------------------------------ transcriptions vs stock

def test_pfns_grid_is_talys_strucinitial():
    e = fisobs.pfns_grid()
    assert e.shape == (293,) and e.dtype == np.float32
    assert e[0] == np.float32(0.001) and abs(e[9] - 0.01) < 1e-6 and abs(e[-1] - 49.5) < 1e-4  # stock pfns*.fis


def test_iwamoto_equals_stock_u238_14mev():
    # stock TALYS-2.25 n + U-238 at 14 MeV: Tfns.tot S(N) 4.80638 MeV; pfns0014.000.fis E-average 2.286938 MeV and
    # its first / tenth / 100th rows (E, spectrum, Maxwell ratio, CM)
    r = fisobs.iwamoto(92, 239, 4.80638, 14.0)
    assert abs(r["eav"] / 2.286938 - 1) < 2e-5
    for i, (e, p, m, c) in ((0, (1.0e-3, 1.676717e-02, 9.494773e-01, 7.364612e-02)),
                            (9, (1.0e-2, 5.306800e-02, 9.302843e-01, 1.407174e-01)),
                            (4, (5.0e-3, 3.754485e-02, 9.289030e-01, 1.025404e-01))):
        assert abs(r["E"][i] - e) < 1e-8
        assert abs(r["pfns"][i] / p - 1) < 5e-5 and abs(r["maxwell_ratio"][i] / m - 1) < 5e-5
        assert abs(r["cm"][i] / c - 1) < 5e-5
    # tmadjust / fsadjust (stock U-238 at 14 MeV: E-average 2.5275 with tmadjust 1.3, 2.2617 with fsadjust 3)
    assert abs(fisobs.iwamoto(92, 239, 4.80638, 14.0, tmadjust=1.3)["eav"] - 2.5275) < 1e-4
    assert abs(fisobs.iwamoto(92, 239, 4.80638, 14.0, fsadjust=3.0)["eav"] - 2.2617) < 1e-4


def test_nubar_wahl():
    # nubarWahl.f90 by hand for the U-239 compound nucleus (even Z, odd N), Bn = 4.80638 MeV, 14 MeV
    t1 = 2.286 + 0.054 * 3 + 0.040 * 2
    th = 11.47 - 0.166 * 92 * 92 / 239 + 0.093 * 2 - 4.80638
    t2 = (0.145 - 0.0043 * 3) * (14.0 - th)
    assert abs(fisobs.nubar_wahl(92, 239, 4.80638, 14.0) - (t1 + t2)) < 1e-5
    assert abs(fisobs.nubar_wahl(92, 239, 4.80638, 14.0, 1.1, 0.5) - (1.1 * t1 + 0.5 * t2)) < 1e-5
    assert abs(fisobs.nubar_wahl(92, 239, 4.80638, 0.0) - t1) < 1e-6  # Ein = 0: no slope term


# ------------------------------------------------------------------------------------------------ switches

def test_no_switch_no_output(clean):
    o = D.default_options(92, 238)
    assert fisobs.settings(o, D.default_params(92, 238, o)) is None
    assert fisobs.settings(D.default_options(26, 56, overrides={"fisfeed": "y"})) is None  # no fission


@pytest.mark.parametrize("ov", [{"filefission": "y"}, {"fisfeed": "y"}, {"outfission": "y"}, {"pfnsmodel": "1"}])
def test_output_keywords_switch_it_on(clean, ov):
    s = fisobs.settings(D.default_options(92, 238, overrides=ov))
    assert s is not None and s["feed"] == ("fisfeed" in ov) and s["pfnsmodel"] == 1


def test_deck_lines_of_the_output_and_adjust_keywords(clean):
    c = _cards(clean, "filefission y;outfission y;fisfeed y;pfnsmodel 2;tmadjust 1.3;fsadjust 2;cnubar1 1.1;"
                      "cnubar2 0.9;rfiseps 0.01")
    assert not c.skipped
    o = D.default_options(92, 238, overrides=dict(c.options))
    assert o.filefission and o.flagfisout and o.flagfisfeed and o.pfnsmodel == 2 and o.Rfiseps == 0.01
    assert dict(c.globals_) == {"tmadjust": 1.3, "fsadjust": 2.0, "cnubar1": 1.1, "cnubar2": 0.9}


@pytest.mark.parametrize("ov, msg", [({"pfnsmodel": "3"}, "pfnsmodel"), ({"rfiseps": "2"}, "rfiseps")])
def test_out_of_range_values_stop_as_talys(clean, ov, msg):
    with pytest.raises(ValueError, match=msg):
        fisobs.settings(D.default_options(92, 238, overrides=ov))


# ------------------------------------------------------------------------------ fission model inputs

def test_axtype_per_nucleus_and_barrier(clean):
    c = _cards(clean, "axtype 92 239 3 2;axtype 92 238 2")
    assert dict(c.options) == {"axtype 92 239 2": "3", "axtype 92 238 1": "2"}
    o = D.default_options(92, 238, overrides=dict(c.options))
    assert o.axtype_of(0, 0, 2) == 3 and o.axtype_of(0, 1, 1) == 2
    assert o.axtype_of(0, 0, 1) == 1 and o.axtype_of(0, 1, 2) == 1  # fismodel 6 defaults elsewhere
    with pytest.raises(ValueError, match="outside 1..4"):
        D.default_options(92, 238, overrides={"axtype 92 239 1": "5"})


def test_transition_state_files(clean, tmp_path):
    hb, c2 = tmp_path / "HB.eo", tmp_path / "C2.eo"
    hb.write_text("   1   1   0.500\n   1   0.000000   0.5    1\n   2   1   0.400\n   1   0.000000   0.5    1\n")
    c2.write_text("   1   1\n   1   2.000000   0.5    1\n")
    c = _cards(clean, f"hbtransfile 92 239 {hb};class2file 92 239 {c2}")
    assert dict(c.options) == {"hbtransfile 92 239": str(hb), "class2file 92 239": str(c2)}  # case kept
    o = D.default_options(92, 238, overrides=dict(c.options))
    assert o.fisstates_file_of("hbtransfile", 0, 0) == str(hb) and o.fisstates_file_of("class2file", 0, 0) == str(c2)
    assert o.fisstates_file_of("hbtransfile", 0, 1) is None
    from physics.hf.fission.parameters import read_class2_states, read_headband_states

    states, fecont = read_headband_states(92, 147, 2, o.fisstates_file_of("hbtransfile", 0, 0))
    assert abs(float(fecont[1]) - 0.5) < 1e-12 and abs(float(fecont[2]) - 0.4) < 1e-12
    assert states[1].n == 1 and abs(float(read_class2_states(92, 147, 1, str(c2))[1].e_mev[1]) - 2.0) < 1e-12
    with pytest.raises(ValueError, match="non-existent file"):
        D.default_options(92, 238, overrides={"class2file 92 239": str(tmp_path / "nope")})
    with pytest.raises(ValueError, match="expected `hbtransfile Z A <file>`"):
        _cards(clean, f"hbtransfile 92 {hb}")


# ---------------------------------------------------------------------------------------------- engine

def _run(Z, A, es):
    import torch

    from physics.hf import engine_c, warmrun
    from physics.hf.engine import ChainedFull

    with torch.inference_mode():
        r = engine_c.run(ChainedFull(Z=Z, A=A, declared_energies=es), {})
    return r, warmrun.result_arrays(r)


@pytest.mark.skipif(os.environ.get("INCOGNITA_SKIP_ENGINE") == "1", reason="engine run")
def test_fission_extras_are_output_only_and_sum_to_the_fission(clean):
    """U-238 at 5 MeV: every Results array with FISOBS on equals the run without it (extras / spectra only added);
    the per-nucleus fission sums to fission.tot, the fisfeed populations to the per-nucleus fission."""
    from physics.hf import chartrun

    r0, a0 = _run(92, 238, (5.0,))
    chartrun.drop_target_caches()
    clean.setenv(F.ENV_LINES, "fisfeed y;filefission y")
    F._cards.cache_clear()
    r1, a1 = _run(92, 238, (5.0,))
    assert set(a0) <= set(a1)
    for k, v in a0.items():
        assert np.array_equal(v, a1[k]), k
    rp = {k: float(v[0]) for k, v in r1.extras.items() if k.endswith(".fis") and k.startswith("rp")}
    assert set(rp) >= {"rp092239.fis", "rp092238.fis"}
    assert abs(sum(rp.values()) / float(r1.totals_mb["fission"][0]) - 1) < 1e-12
    for key in ("092239", "092238"):
        pop = r1.spectra[f"fis{key}.feed"][0].numpy()
        assert abs(np.nansum(pop) / rp[f"rp{key}.fis"] - 1) < 1e-9
    assert r1.spectra["pfns.fis"].shape == (1, 293)
    assert abs(float(r1.extras["pfns.fis:E-average"][0]) - 2.0784) < 2e-4  # stock pfns0005.000.fis
    assert not r0.spectra and not any(k.endswith(".fis") for k in r0.extras)
