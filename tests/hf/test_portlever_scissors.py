"""PORTLEVER: `INCOGNITA_M1_SCISSORS=k17` swaps the Kopecky-2017 scissors term into `strengthM1 3`.

Off by default, the Kopecky systematics when on, zero for a spherical nucleus, a user keyword
still wins, and the switch reaches the photon-strength parameters every engine path reads.
The end-to-end check against stock TALYS on the Python, native C, fast and GPU paths is
`scripts/portlever/wiring.py` (docs/results/portlever.md, step 0).
"""

from __future__ import annotations

import subprocess
import sys

import pytest

from physics.hf.gamma import scissors


def test_the_shipped_default_is_off():
    out = subprocess.run(
        [sys.executable, "-c", "from physics.hf.gamma import scissors; print(repr(scissors.mode()))"],
        capture_output=True, text=True, check=True, env={"PATH": "/usr/bin:/bin"})
    assert out.stdout.strip() == "''", out


def test_k17_formula():
    e, g, t = scissors.k17(239, 0.28)
    assert e == pytest.approx(80.0 * 0.28 / 239 ** (1 / 3))
    assert g == 1.5
    assert t == pytest.approx(42.4 * 0.28**2 / 1.5)
    assert scissors.k17(120, 0.0)[2] == 0.0


def _cn(Z, A):
    from physics.hf.compound.dens_reference import _gamma_parameters
    return _gamma_parameters(Z, A)[0]


def test_switch_reaches_the_compound_psf():
    prev = scissors.set_mode("")
    try:
        gp0 = _cn(92, 238)
        b2 = float(gp0.beta2)
        assert float(gp0.tpr_mb[0, 1, 1]) == pytest.approx(1.0e-2 * abs(b2) * 239**0.9)
        scissors.set_mode("k17")
        gp1 = _cn(92, 238)
        e, g, t = scissors.k17(239, b2)
        assert float(gp1.epr_mev[0, 1, 1]) == pytest.approx(e)
        assert float(gp1.gpr_mev[0, 1, 1]) == pytest.approx(g)
        assert float(gp1.tpr_mb[0, 1, 1]) == pytest.approx(t)
        # the spin-flip and the upbend are SMLO-2019's either way
        assert float(gp1.sgr_mb[0, 1, 1]) == float(gp0.sgr_mb[0, 1, 1])
        assert float(gp1.upbend[0, 1, 1]) == float(gp0.upbend[0, 1, 1])
    finally:
        scissors.set_mode(prev)


def test_user_keyword_wins():
    import numpy as np
    import torch

    from physics.hf.compound.dens_reference import _build_gamma_parameters
    prev = scissors.set_mode("k17")
    try:
        t = np.zeros((2, 3, 3))
        t[0, 1, 1] = 0.123
        gp = _build_gamma_parameters(92, 238, {"tpr_mb": torch.as_tensor(t)})[0]
        assert float(gp.tpr_mb[0, 1, 1]) == pytest.approx(0.123)
    finally:
        scissors.set_mode(prev)


def test_bad_mode_refused():
    with pytest.raises(ValueError):
        scissors.set_mode("smlo")
