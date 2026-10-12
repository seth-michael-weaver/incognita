"""ACTPHYS: `INCOGNITA_ACTPHYS=gg|sc|both` changes the photon strength of Z >= 88 nuclei only.

Off by default; `gg` sets the E1 ftable default to the RIPL-3 <Gamma_gamma> factor, `sc` swaps in
the Kopecky-2017 scissors, `both` does both with the factors re-derived under the scissors; a
non-actinide is untouched in every mode. The end-to-end check against stock TALYS on every engine
path is `scripts/actphys/wiring.py` (docs/results/actphys-prereg.md, step 0).
"""

from __future__ import annotations

import subprocess
import sys

import pytest

from physics.hf.gamma import actphys, scissors


def _cn(Z, A):
    from physics.hf.compound.dens_reference import _gamma_parameters
    return _gamma_parameters(Z, A)[0]


def test_the_shipped_default_is_off():
    out = subprocess.run(
        [sys.executable, "-c", "from physics.hf.gamma import actphys; print(repr(actphys.mode()))"],
        capture_output=True, text=True, check=True, env={"PATH": "/usr/bin:/bin"})
    assert out.stdout.strip() == "''", out


def test_factors_are_actinide_only():
    assert all(z >= actphys.ZMIN for z, _ in actphys.GG_FACTOR)
    prev = actphys.set_mode("gg")
    try:
        assert actphys.e1_factor(92, 239) == actphys.GG_FACTOR[(92, 239)][0]
        assert actphys.e1_factor(92, 238) == 1.0  # no RIPL-3 width for U-237 + n
        assert actphys.e1_factor(65, 160) == 1.0
        assert not actphys.scissors_k17(92)
        actphys.set_mode("both")
        assert actphys.e1_factor(92, 239) == actphys.GG_FACTOR[(92, 239)][1]
        assert actphys.scissors_k17(92) and actphys.scissors_k17(88)
        assert not actphys.scissors_k17(87)
    finally:
        actphys.set_mode(prev)


@pytest.mark.parametrize("mode", ["gg", "sc", "both"])
def test_switch_reaches_the_actinide_psf_and_not_tb159(mode):
    prev = actphys.set_mode("")
    try:
        u0, tb0 = _cn(92, 238), _cn(65, 159)
        actphys.set_mode(mode)
        u1, tb1 = _cn(92, 238), _cn(65, 159)
        for name in ("ftable", "epr_mev", "gpr_mev", "tpr_mb", "sgr_mb", "egr_mev"):
            assert getattr(tb1, name).equal(getattr(tb0, name)), name
        if mode in ("gg", "both"):
            f = actphys.GG_FACTOR[(92, 239)][1 if mode == "both" else 0]
            assert float(u1.ftable[1, 1]) == f
        else:
            assert float(u1.ftable[1, 1]) == float(u0.ftable[1, 1])
        if mode in ("sc", "both"):
            e, g, t = scissors.k17(239, float(u0.beta2))
            assert float(u1.tpr_mb[0, 1, 1]) == pytest.approx(t)
            assert float(u1.epr_mev[0, 1, 1]) == pytest.approx(e)
        else:
            assert float(u1.tpr_mb[0, 1, 1]) == float(u0.tpr_mb[0, 1, 1])
    finally:
        actphys.set_mode(prev)


def test_bad_mode_refused():
    with pytest.raises(ValueError):
        actphys.set_mode("k17")
