"""KWCOV GAP: isomeric (excited) targets, TALYS `ltarget` (docs/hf/ISOMERIC_TARGETS.md).

* the checks TALYS makes (checkvalue.f90:429, :467; levels.f90:252) and the refusals of what is not ported
  (`ltarget` with `liso`, the outputs of `defaults.LTARGET_UNPORTED`, projectiles other than n);
* the target state: spin, parity and excitation energy of level `Ltarget` (nuclides.f90:231-234);
* direct.f90:33 (no DWBA level, no giant resonance for an excited target) and preeqcorrect.f90:90 (no collapse of
  the pre-equilibrium continuum onto the discrete levels);
* n + Fe-56 `ltarget 1` (0.847 MeV 2+) at 1 and 14 MeV in TALYS mode (scripts/kwcov/fidelity.py TALYS_DECK /
  TALYS_ENV) against stock TALYS-2.25 (~/kwcov/stock/biso, scripts/kwcov/biso_stock.sh), numbers transcribed here.
  The full comparison (Fe-56 levels 1 and 2, Am-242m) is scripts/kwcov/biso_compare.py.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import numpy as np
import pytest

from physics.hf.input import defaults as D
from physics.hf.input import fitlib as F

ROOT = Path(__file__).resolve().parents[2]

# stock TALYS-2.25 n + Fe-56, `ltarget 1`, channels y, filechannels y, fileresidual y, outdiscrete y (mb)
STOCK_FE56_L1 = {
    1.0: {"total": 3.785750e+03, "elastic": 3.437702e+03, "nonelastic": 3.480476e+02, "xs000000": 4.297545e+00,
          "xs100000": 3.436889e+02, "nn.L00": 3.436889e+02},
    14.0: {"total": 2.657760e+03, "elastic": 1.219731e+03, "nonelastic": 1.438029e+03, "xs000000": 9.104453e-01,
           "xs100000": 5.595993e+02, "xs200000": 6.217520e+02, "xs010000": 1.129738e+02, "xs000001": 4.071546e+01},
}
# stock TALYS-2.25 n + Am-242m (`ltarget 2`, 48.6 keV 5-), 1 MeV, same deck (mb). nn.L03 / nn.L04 are the ground band's
# coupled-channels inelastic TALYS keeps for the excited target (incidentread.f90:381-394); nn.L00 is superelastic.
STOCK_AM242M_1 = {"total": 6.987590e+03, "elastic": 3.742045e+03, "nonelastic": 3.245544e+03, "fission": 2.376450e+03,
                  "xs000000": 5.061145e+01, "xs100000": 8.182926e+02, "nn.L00": 1.831799e+00, "nn.L03": 1.192089e+02,
                  "nn.L04": 2.447946e+02}
KEYS = {"total": "totals_mb/total", "elastic": "totals_mb/elastic", "nonelastic": "totals_mb/nonelastic",
        "fission": "totals_mb/fission"}


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


def _drop():
    from physics.hf import chartrun

    F.deactivate(); F._cards.cache_clear(); chartrun.drop_target_caches()


def _opts(Z=26, A=56, **kw):
    return D.default_options(Z, A, "n", overrides=kw)


# ------------------------------------------------------------------------------------------------ checks, refusals
def test_ltarget_parses_and_sets_the_target_level_count():
    o = _opts(ltarget="2")
    assert o.Ltarget == 2 and o.nlevmax == 30
    assert _opts(ltarget="35").nlevmax == 35  # input_levels.f90:106 max(30, Ltarget)
    D.reject_unported(o)  # a plain excited-target run is ported


def test_talys_range_and_liso_checks():
    with pytest.raises(ValueError, match="0 <= Ltarget <= 40"):  # checkvalue.f90:467 (Hf-178m2 = level 109)
        D.reject_unported(_opts(72, 178, ltarget="109"))
    with pytest.raises(NotImplementedError, match="ltarget with liso"):
        D.reject_unported(_opts(ltarget="1", liso="1"))
    D.reject_unported(_opts(liso="1"))  # liso alone: the output label, as before


@pytest.mark.parametrize("kw", ["outangle", "outspectra", "recoil", "astro", "endf", "components", "racap",
                                "production", "channelenergy"])
def test_unported_outputs_refused_with_ltarget(kw):
    D.reject_unported(_opts(**{kw: "y"}))  # a ground-state run with the same keyword is not refused here
    with pytest.raises(NotImplementedError, match=rf"ltarget > 0 with [a-z, ]*\b{kw}\b"):
        D.reject_unported(_opts(ltarget="1", **{kw: "y"}))


def test_excited_level_must_exist(clean):
    from physics.hf.input.defaults import default_params
    from physics.hf.structure.levels import discrete_levels
    from physics.hf.structure.masses import masses

    o = _opts(ltarget="3", maxlevelstar="2")  # maxlevelstar = max(2, Ltarget) = 3 -> fine
    m = masses(o, default_params(26, 56, o))
    assert int(discrete_levels(26, 56, o, m, default_params(26, 56, o)).nlev) >= 3
    o = _opts(1, 2, ltarget="5")  # H-2: no excited level in the file, nlev = max(0, 1) (levels.f90:242, :252-257)
    with pytest.raises(ValueError, match="excited level of target does not exist"):
        discrete_levels(1, 2, o, masses(o, default_params(1, 2, o)), default_params(1, 2, o))


def test_natural_target_refused(clean, tmp_path):
    from physics.hf.input.deck import run_deck

    (tmp_path / "talys.inp").write_text("projectile n\nelement fe\nmass 0\nenergy 14\nltarget 1\n")
    with pytest.raises(ValueError, match="not possible for natural targets"):
        run_deck(tmp_path / "talys.inp")


# ------------------------------------------------------------------------------------------------ target state
@pytest.mark.parametrize("Z, A, lt, spin2, par, e_mev", [
    (26, 56, 1, 4, 1, 0.846778),   # Fe-56 2+
    (26, 56, 2, 8, 1, 2.085105),   # Fe-56 4+
    (95, 242, 2, 10, -1, 0.048600),  # Am-242m 5-
])
def test_target_state_of_level(clean, Z, A, lt, spin2, par, e_mev):
    from physics.hf.structure.scalars import structure_scalars

    clean.setenv("INCOGNITA_TALYS_FIT", "lines")
    clean.setenv("INCOGNITA_TALYS_FIT_LINES", f"ltarget {lt}")
    _drop()
    assert F.activate(Z, A) is not None  # the deck lines reach default_options through fitlib (as in a run)
    sc = structure_scalars(Z, A, (1.0, 14.0))
    assert (sc.ltarget, sc.targetspin2, sc.target_parity) == (lt, spin2, par)
    assert sc.targete_mev == pytest.approx(e_mev, abs=2e-6)


# ------------------------------------------------------------------------------------------------ direct, preeq gates
def test_direct_off_for_excited_target(clean):
    """direct.f90:33: no DWBA level and no giant resonance (Fe-56 is spherical: no coupled-channels inelastic)."""
    from physics.hf.direct.chain import direct_result

    clean.setenv("INCOGNITA_TALYS_FIT", "lines")
    clean.setenv("INCOGNITA_TALYS_FIT_LINES", "ltarget 1")
    _drop()
    assert F.activate(26, 56) is not None
    d, flaggiant = direct_result("Fe056", 14.0, (1.0, 14.0))
    assert not flaggiant
    assert float(d.xsdirdisctot_mb) == 0.0 and float(d.xsgrtot_mb) == 0.0
    assert float(np.abs(np.asarray(d.xsdirdisc_mb)).sum()) == 0.0


def test_preeq_correct_skips_levels_for_excited_target():
    """preeqcorrect.f90:90: Ltarget /= 0 -> goto 100: no xspreeqdisc, the spectrum above nendisc still zeroed."""
    import dataclasses

    import torch

    from physics.hf.preeq import exciton as X

    C, E = 1, 12
    eg = torch.linspace(0.5, 11.5, E, dtype=torch.float64).reshape(1, E)
    sp = {k: torch.ones(1, 7, E, dtype=torch.float64) for k in ("xspreeq", "xspreeqps", "xspreeqki", "xspreeqbu")}
    sp["xsstep"] = torch.ones(1, 7, 4, E, dtype=torch.float64)
    inp = type("I", (), dict(C=C, E=E, k0=1, egrid_mev=eg, deltae_mev=torch.ones(1, E, dtype=torch.float64)))()
    eo = [None] * 7
    eo[1] = np.array([10.0, 9.0, 8.0])
    disc = X.DiscreteInputs(eoutdis_mev=[eo], nendisc=[[0, 7, 0, 0, 0, 0, 0]], nlast=(0, 2, 0, 0, 0, 0, 0),
                            xsdirdisc_mb=[[np.zeros(3)] * 7], etop_mev=eg + 0.5,
                            ebegin=(0, 0, 1, 1, 1, 1, 1), eend=[[0, 11, 0, 0, 0, 0, 0]])
    gs = X.preeq_correct(sp, inp, disc, None)
    ex = X.preeq_correct(sp, inp, dataclasses.replace(disc, ltarget=1), None)
    assert float(gs["xspreeqdisctot"][0, 1]) > 0.0 and float(ex["xspreeqdisctot"][0, 1]) == 0.0
    for r in (gs, ex):  # above nendisc: zero either way
        assert float(r["xspreeq"][0, 1, 8:].abs().sum()) == 0.0
    assert float(ex["xspreeq"][0, 1, 7]) == 1.0  # no Rboundary depletion of the last discrete bin


# ------------------------------------------------------------------------------------------------ engine vs stock
def _talys_mode():
    sys.path.insert(0, str(ROOT / "scripts" / "kwcov"))
    from fidelity import mode_args

    return mode_args("talys")


def _engine(clean, Z: int, A: int, lines: str, energies):
    import torch

    from physics.hf import chartrun, engine_c, warmrun
    from physics.hf.engine import ChainedFull

    deck, env = _talys_mode()
    for k, v in env.items():
        clean.setenv(k, v)
    clean.setenv("INCOGNITA_TALYS_FIT", "lines")
    clean.setenv("INCOGNITA_TALYS_FIT_LINES", lines + ";" + deck)
    F.deactivate(); F._cards.cache_clear(); chartrun.drop_target_caches()
    with torch.inference_mode():
        r = engine_c.run(ChainedFull(Z=Z, A=A, declared_energies=tuple(energies)))
    return warmrun.result_arrays(r)


def _get(a, ch, i):
    k = KEYS.get(ch) or (f"levels_mb/{ch}" if ch.startswith("nn.") else f"channels_mb/{ch}")
    return float(np.asarray(a[k])[i])


def test_engine_fe56_ltarget1_vs_stock(clean):
    """n + Fe-56 (2+, 0.847 MeV), TALYS mode: the main channels within 2 % of stock at 1 and 14 MeV (measured
    <= 0.01 %); at 1 MeV the whole inelastic is the superelastic exit to the ground state (nn.L00), and nn.L01 (the
    target level) is empty. 14 MeV (n,a) is the complex-particle pre-equilibrium's eninccm (was -1.6 %)."""
    a = _engine(clean, 26, 56, "ltarget 1", (1.0, 14.0))
    for i, e in enumerate((1.0, 14.0)):
        for ch, ref in STOCK_FE56_L1[e].items():
            got = _get(a, ch, i)
            if ref > 1.0:
                assert abs(got / ref - 1) < 0.02, (e, ch, got, ref)
    assert abs(_get(a, "xs000001", 1) / STOCK_FE56_L1[14.0]["xs000001"] - 1) < 2e-3
    assert float(np.abs(np.asarray(a.get("levels_mb/nn.L01", np.zeros(2)))).sum()) == 0.0


def test_engine_am242m_vs_stock(clean):
    """n + Am-242m 1 MeV, TALYS mode: deformed (incident coupled channels on the 0/3/4 band) and fissile; main
    channels and the levels within 2 % of stock (measured <= 0.03 %)."""
    a = _engine(clean, 95, 242, "ltarget 2", (1.0,))
    for ch, ref in STOCK_AM242M_1.items():
        got = _get(a, ch, 0)
        assert abs(got / ref - 1) < 0.02, (ch, got, ref)
