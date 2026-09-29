"""INGRED: the `ing_*` physics ingredients `scripts/bestfit/engine_curves.py` saves.

The reference numbers are stock TALYS-2.24's own printed values, from a run of
``~/opt/talys-src/bin/talys`` with the default keywords plus the output switches
(``filepsf y / outgamma y / outdensity y / outbasic y / outfission y``) at the engine's first
grid point, 0.001 MeV: ``ld<ZZZ><AAA>.gs`` ("theoretical D0 [eV]", "a(Sn) [MeV^-1]", ...),
``psf<ZZZ><AAA>.E1`` ("theoretical Gamma_gamma [eV]", "theoretical S-wave strength function
[e-4]", "average resonance energy [eV]"), ``spr.opt`` (S0, S1, Rprime) and
``fis<ZZZ><AAA>.txt`` (barrier heights and widths). Gate: 1e-4 relative, which is finer than
TALYS's own 7-digit print.

Nothing here runs a reaction: `ingredients` reads the level-density, photon-strength and
incident-channel objects a `Cascade` builds, and adds `dtheory` / `radwidtheory`, the two
integrals TALYS computes for output only.
"""

from __future__ import annotations

import numpy as np
import pytest
import torch

from physics.hf.emission.feeding import Cascade
from physics.hf.ingredients import eavres_mev, ingredients

TOL = 1.0e-4

# stock TALYS-2.24, n + Fe-56 at 0.001 MeV (compound nucleus Fe-57)
FE56 = {
    "ing_d0theo_ev": 2.539792e4,
    "ing_gamgam_th_ev": 1.303671e0,
    "ing_swaveth_e4": 5.132985e-1,
    "ing_s0_e4_first": 5.655801e0,
    "ing_s1_e4_first": 7.006630e-1,
    "ing_rprime_fm_first": 8.106253e0,
    "ing_sn_mev": 7.646172e0,
    "ing_alev_mev1": 7.093130e0,
    "ing_pair_mev": 1.589439e0,
    "ing_pshift_mev": 0.0,
    "ing_spincut_sn": 9.485043e0,
    "ing_eavres_mev": 1.0e4 * 1.0e-6,
    "ing_ldmodel": 1,
    "ing_tgt_sn_mev": 1.119706e1,
    "ing_tgt_alev_mev1": 6.629000e0,
}

# stock TALYS-2.24, n + U-238 at 0.001 MeV (compound nucleus U-239, ldmodel 7, 3 barriers)
U238 = {
    "ing_d0theo_ev": 2.031960e1,
    "ing_gamgam_th_ev": 1.121457e-2,
    "ing_swaveth_e4": 5.519090e0,
    "ing_sn_mev": 4.806381e0,
    "ing_ldmodel": 7,
    "ing_tgt_d0theo_ev": 3.489606e0,
    "ing_tgt_sn_mev": 6.153718e0,
}
U239_BARRIERS = ((6.008000e0, 1.331231e0), (6.731000e0, 1.612479e0), (2.898000e0, 9.311627e-1))


def _rel(port: float, talys: float) -> float:
    d = max(abs(float(port)), abs(float(talys)))
    return 0.0 if d == 0.0 else abs(float(port) - float(talys)) / d


def _scalar(ing: dict, key: str) -> float:
    return float(np.asarray(ing[key]).reshape(-1)[0])


@pytest.fixture(scope="module")
def fe56() -> dict:
    with torch.inference_mode():
        return ingredients(Cascade(26, 56, 0.001, energies=(0.001,)))


@pytest.fixture(scope="module")
def u238() -> dict:
    # no `energies`: `ingredients` then skips the per-energy S0/S1/R' block, so this fixture
    # costs no coupled-channels solve (the barriers and D0/Gamma_gamma do not need one)
    with torch.inference_mode():
        return ingredients(Cascade(92, 238, 0.001))


@pytest.mark.parametrize("key", sorted(FE56))
def test_fe56_matches_stock_talys(fe56, key):
    assert _rel(_scalar(fe56, key), FE56[key]) <= TOL, (key, _scalar(fe56, key), FE56[key])


@pytest.mark.parametrize("key", sorted(U238))
def test_u238_matches_stock_talys(u238, key):
    assert _rel(_scalar(u238, key), U238[key]) <= TOL, (key, _scalar(u238, key), U238[key])


def test_u239_fission_barriers(u238):
    assert int(_scalar(u238, "ing_fis_nfisbar")) == len(U239_BARRIERS)
    h = np.asarray(u238["ing_fis_fbarrier_mev"], float)
    w = np.asarray(u238["ing_fis_fwidth_mev"], float)
    assert h.shape == w.shape == (len(U239_BARRIERS),)
    for i, (hb, wb) in enumerate(U239_BARRIERS):
        assert _rel(h[i], hb) <= TOL, ("height", i + 1, h[i], hb)
        assert _rel(w[i], wb) <= TOL, ("width", i + 1, w[i], wb)


def test_eavres_is_talys_0p01(fe56):
    """`resonancepar.f90:74` wins over :100-102 in every normal run -- see `eavres_mev`. Fe-57's
    own value would be 0.0381 MeV (Nrr = 4, D0 = 25400 eV), and using it moves <Gamma_gamma>
    2.5 % off what TALYS prints."""
    from physics.hf.input.defaults import default_options
    from physics.hf.structure.resonances import resonance_parameters

    o = default_options(26, 56)
    assert eavres_mev(o) == pytest.approx(0.01, rel=1e-12)
    own = resonance_parameters(26, 57, o).eavres_mev
    assert own > 0.01  # the value radwidtheory would get if the reset were not reproduced
    assert _scalar(fe56, "ing_eavres_mev") == pytest.approx(0.01, rel=1e-12)


def test_every_key_is_prefixed_and_savez_safe(fe56):
    import io

    assert fe56, "no ingredients"
    assert all(k.startswith("ing_") for k in fe56)
    buf = io.BytesIO()
    np.savez(buf, **fe56)  # str / int / float / ndarray only, as `engine_curves` saves them
    buf.seek(0)
    with np.load(buf, allow_pickle=False) as z:
        assert set(z.files) == set(fe56)


def test_required_quantities_are_present(fe56):
    """The list INGRED was asked for: D0, <Gamma_gamma>, S0/S1, a(Sn), pairing/shift, spin
    cut-off, Sn, ldmodel/strength -- for the compound nucleus and for the target."""
    for key in ("ing_d0theo_ev", "ing_gamgam_th_ev", "ing_s0_e4", "ing_s1_e4", "ing_alev_mev1",
                "ing_pair_mev", "ing_pshift_mev", "ing_spincut_sn", "ing_sn_mev", "ing_ldmodel",
                "ing_strength", "ing_strengthM1", "ing_ld_cn_json", "ing_ld_tgt_json",
                "ing_psf_json", "ing_fis_json"):
        assert key in fe56, key
    for key in ("ing_tgt_d0theo_ev", "ing_tgt_alev_mev1", "ing_tgt_pair_mev",
                "ing_tgt_spincut_sn", "ing_tgt_sn_mev", "ing_tgt_ldmodel"):
        assert key in fe56, key
    assert np.asarray(fe56["ing_s0_e4"]).shape == (1,)


def test_engine_curves_saves_them_by_default():
    """`--no-ingredients` is the only way off, and the flag defaults to on."""
    import ast
    from pathlib import Path

    src = Path(__file__).resolve().parents[2] / "scripts" / "bestfit" / "engine_curves.py"
    tree = ast.parse(src.read_text())
    text = src.read_text()
    assert "--no-ingredients" in text
    assert 'dest="ingredients", action="store_false"' in text
    assert "ingredient_dump(cas, res)" in text
    fn = next(n for n in ast.walk(tree)
              if isinstance(n, ast.FunctionDef) and n.name == "_worker")
    default = fn.args.defaults[-1]
    assert isinstance(default, ast.Constant) and default.value is True
