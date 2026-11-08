"""KWCOV B7: the exciton-model branches that were refused (docs/hf/COVERAGE_PLAN.md, batch B7).

`twocomponent n`, `gshell y` and `preeqmode 3` now run through `physics.hf.preeq.exciton_b7`, `preeqspin 3` and
`preeqspin 4` give the J-dependent pre-equilibrium population to population.f90 and binary.f90, `preeqmode 4` (MSD) is
refused (it used to run the exciton model silently) and `gnorm y` stays refused. The response of each model was
compared with stock TALYS-2.25 by scripts/kwcov/b7_response.py (numbers in COVERAGE_PLAN.md B7); the tests here pin
the transcription against the vectorised path, the transition rates and pre-equilibrium totals against stock output,
the parsing and the refusals.
"""
from __future__ import annotations

import dataclasses
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
import torch

from physics.hf.input import defaults as D

ROOT = Path(__file__).resolve().parents[2]


# ------------------------------------------------------------------------------------------- options


def test_defaults_do_not_take_the_b7_path():
    from physics.hf.preeq import exciton_b7

    o = D.default_options(26, 56)
    assert not exciton_b7.active(o)
    assert (o.flag2comp, o.flaggshell, o.preeqmode, o.pespinmodel) == (True, False, 2, 1)
    D.reject_unported(o)


@pytest.mark.parametrize("kw, want", [({"twocomponent": "n"}, ("flag2comp", False)),
                                      ({"gshell": "y"}, ("flaggshell", True)),
                                      ({"preeqmode": 3}, ("preeqmode", 3))])
def test_b7_switches_are_ported(kw, want):
    from physics.hf.preeq import exciton_b7

    o = D.default_options(26, 56, overrides=kw)
    assert getattr(o, want[0]) == want[1] and exciton_b7.active(o)
    D.reject_unported(o)


@pytest.mark.parametrize("value, want", [("y", 3), ("n", 1), ("3", 3), ("4", 4), (2, 2)])
def test_preeqspin_reads_y_n_and_numbers(value, want):
    # input_preeqmodel.f90:145-157: y = 3, n = 1, otherwise the number
    o = D.default_options(26, 56, overrides={"preeqspin": value})
    assert o.pespinmodel == want
    D.reject_unported(o)


def test_msd_is_refused_and_its_keywords_are_inert():
    o = D.default_options(26, 56, overrides={"preeqmode": 4})
    with pytest.raises(NotImplementedError, match="preeqmode 4"):
        D.reject_unported(o)
    # onestep / msdbins / emsdmin act only inside MSD (msdinit.f90, dwbaecis.f90): accepted and inert without it
    o = D.default_options(26, 56, overrides={"onestep": "y", "msdbins": 8})
    D.reject_unported(o)
    assert o.flagonestep and o.msdbins == 8


def test_gnorm_stays_refused_with_the_reason():
    with pytest.raises(NotImplementedError, match="keV number"):
        D.reject_unported(D.default_options(26, 56, overrides={"gnorm": "y"}))


def test_wigner_spin_distribution_needs_the_incident_energy():
    from physics.hf.preeq.spin import MAXJPH, newspin, preeq_spin_distribution

    o = D.default_options(26, 56, overrides={"preeqspin": 4})
    p = D.default_params(26, 56, o)
    with pytest.raises(NotImplementedError, match="multiple pre-equilibrium"):
        preeq_spin_distribution(o, p, 56)
    r = preeq_spin_distribution(o, p, 56, einc_mev=14.0)
    assert r["RnJ"].shape == (13, MAXJPH + 1) and float(r["RnJ"][0].sum()) == 0.0
    assert all(float(r["RnJsum"][n]) > 0.0 for n in range(1, 13))
    assert newspin(56, 14.0, 2) > newspin(56, 14.0, 1) > 0.0  # wider at higher exciton number


def test_giant_resonance_states_go_to_their_multipolarity():
    from physics.hf.emission.feed_reference import _spin_inputs

    E = 5
    g4 = torch.arange(20, dtype=torch.float64).reshape(4, E) + 1.0
    gres = dataclasses.make_dataclass("G", ["xsgrstate_mb", "xscollcontjp_mb"])(
        g4, torch.ones(41, 2, E, dtype=torch.float64))
    pres = {"xspreeqjp": torch.ones(1, 7, E, 31, dtype=torch.float64)}
    got = _spin_inputs(pres, 0, gres, 1, E)
    gs = got["xsgrstate_mb"][1]
    assert gs.shape == (E, 4, 2) and got["maxjph"] == 30
    assert (gs[:, 0, 0] == g4[0].numpy()).all() and (gs[:, 2, 0] == g4[1].numpy()).all()
    assert (gs[:, 3, 0] == g4[2].numpy()).all() and (gs[:, 3, 1] == g4[3].numpy()).all()
    assert gs[:, 1].sum() == 0.0 and got["xscollcontjp_mb"][1].shape == (E, 31, 2)
    assert got["xspreeqjp_mb"][3].shape == (E, 31, 2)


# --------------------------------------------------------------------------------- transcription


@pytest.fixture(scope="module")
def fe56():
    from tests._data import need_talys

    need_talys()
    from physics.hf.preeq.prepare import _structure, prepare

    es = (1.0, 5.0, 14.0)
    inp, hdr = prepare("Fe056", energies=list(es), chained=True, enincmax_mev=14.0, direct_grid=es)
    return inp, hdr, _structure("Fe056")[4]


def _rel(a, b) -> float:
    a, b = a.detach().numpy(), b.detach().numpy()
    m = abs(b).max()
    return float(abs(a - b).max() / m) if m > 0 else float(abs(a).max())


@pytest.mark.parametrize("mode", [2, 1])
def test_two_component_transcription_is_the_vectorised_model(fe56, mode):
    """With gshell n and preeqmode 1/2 exciton_b7's one-state-at-a-time transcription gives the vectorised path's
    emission and transition rates (float64 rounding): the check that it is the same physics."""
    from physics.hf.preeq import exciton as X
    from physics.hf.preeq import exciton_b7 as B

    inp, hdr, m = fe56
    o = dataclasses.replace(hdr["options"], preeqmode=mode)
    p = hdr["params"]
    st = X.exciton_states(inp.k0, X.NUMPARX)
    emis = X.emission_rates(inp, st, o, p)
    rates = X.transition_rates(inp, st, o, p, emis=emis)
    ext = B.extras(26, 56, inp.k0, o, p, m, 14.0, float(p.at("kph")))
    e2, r2 = B.two_component(inp, o, p, ext, st)
    for k in ("wemission2", "wemispart2", "wemistot2"):
        assert _rel(e2[k], emis[k]) < 1e-12, k
    for k in r2:
        assert _rel(r2[k], rates[k]) < 1e-12, k


# stock TALYS-2.25 exciton0014.000.out, n + Fe-56 at 14 MeV, preeqmode 3: lambdapiplus, lambdanuplus, lambdapinu,
# lambdanupi [s^-1] of (ppi, hpi, pnu, hnu)
STOCK_PE3_RATES = {
    (0, 0, 1, 0): (1.314111e21, 1.299077e21, 0.0, 0.0),
    (1, 1, 2, 1): (1.579255e22, 1.236454e22, 9.221151e20, 1.609589e21),
    (2, 2, 2, 1): (1.518299e22, 1.682776e22, 6.111696e21, 2.595138e21),
    (0, 0, 6, 5): (4.646919e22, 4.556418e20, 0.0, 9.708795e22),
    (5, 5, 1, 0): (2.547723e21, 2.843828e22, 8.788333e22, 0.0),
}


def test_optical_model_transition_rates_equal_stock(fe56):
    from physics.hf.preeq import exciton as X
    from physics.hf.preeq import exciton_b7 as B

    inp, hdr, m = fe56
    o = dataclasses.replace(hdr["options"], preeqmode=3)
    p = hdr["params"]
    ext = B.extras(26, 56, inp.k0, o, p, m, 14.0, float(p.at("kph")))
    i14 = 2
    one = dataclasses.replace(inp, b7=ext, **{f.name: getattr(inp, f.name)[i14:i14 + 1]
                                               for f in dataclasses.fields(inp)
                                               if isinstance(getattr(inp, f.name), torch.Tensor)})
    st = X.exciton_states(inp.k0, X.NUMPARX)
    _, rates = B.two_component(one, o, p, ext, st)
    for key, want in STOCK_PE3_RATES.items():
        s = st.index_of(key[0], key[2])
        got = [float(rates[k][0, s]) for k in ("lambdapiplus", "lambdanuplus", "lambdapinu", "lambdanupi")]
        for g, w in zip(got, want):
            assert g == pytest.approx(w, rel=2e-5, abs=1.0), (key, got, want)


# ------------------------------------------------------------------------- pre-equilibrium totals vs stock

# stock TALYS-2.25 preeq0014.000.out (outpreequilibrium y), n + Fe-56 at 14 MeV: Total of gamma, neutron, proton [mb]
STOCK_PE_TOTALS = {
    "": (0.7010832, 278.6084, 23.36152),
    "twocomponent n": (0.5712, 232.0689, 26.4932),
    "gshell y": (0.5744, 255.5670, 22.0637),
    "preeqmode 3": (0.679154, 77.02662, 5.816655),
}


@pytest.mark.parametrize("kw", list(STOCK_PE_TOTALS))
def test_binary_preequilibrium_totals_equal_stock(kw):
    """Fresh process per deck (the per-target caches must not see two decks): the engine's xspreeqtot through the
    deck-line entry, against the stock preeq file."""
    from tests._data import need_talys

    need_talys()
    env = {k: v for k, v in os.environ.items() if not k.startswith("INCOGNITA_")}
    if kw:
        env["INCOGNITA_TALYS_FIT_LINES"] = kw
    env.setdefault("OMP_NUM_THREADS", "1")
    r = subprocess.run([sys.executable, str(ROOT / "scripts/kwcov/b7_response.py"), "_pe_child", "26", "56", "14.0"],
                       env=env, cwd=ROOT, capture_output=True, text=True, timeout=900)
    line = [x for x in r.stdout.splitlines() if x.startswith("{")]
    assert r.returncode == 0 and line, r.stderr[-800:]
    got = json.loads(line[-1])["14.0"]
    for i, want in zip((0, 1, 2), STOCK_PE_TOTALS[kw]):
        assert got[i] == pytest.approx(want, rel=3e-4), (kw, i, got[i], want)
