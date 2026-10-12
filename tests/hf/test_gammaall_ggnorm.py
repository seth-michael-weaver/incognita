"""GAMMAALL: `INCOGNITA_GGAMMA_NORM` scales a nucleus's default E1 ftable by its RIPL-3 Gamma_gamma
(or Gamma_gamma/D0) factor.

Off by default; the tabulated factor when on; 1 for actinides and untabulated nuclei; an explicit
ftable override still wins; the factors are anchored to physical-eV widths (never the keV
resonance-table number GNORMFIX found TALYS's `gnorm y` reading as eV). The end-to-end check
against stock TALYS on the Python, native C, fast and GPU paths is `scripts/gammaall/wiring.py`.
"""

from __future__ import annotations

import subprocess
import sys

import numpy as np
import pytest

from physics.hf.gamma import ggnorm
from physics.hf.gamma.transmission import GAMGAM_MIN_EV


def test_the_shipped_default_is_off():
    out = subprocess.run(
        [sys.executable, "-c", "from physics.hf.gamma import ggnorm; print(repr(ggnorm.mode()), ggnorm.factor(79, 198))"],
        capture_output=True, text=True, check=True, env={"PATH": "/usr/bin:/bin"})
    assert out.stdout.strip() == "'' 1.0", out


@pytest.mark.parametrize("m", ["ripl3", "ripl3d0"])
def test_table_is_physical_ev_and_non_actinide(m):
    tab = ggnorm.table(ggnorm._COLUMN[m])
    assert len(tab) > 150
    assert max(z for z, _ in tab) <= ggnorm.ZMAX
    assert all(0.0 < g < 100.0 for g in tab.values())
    import csv
    with ggnorm.TABLE.open() as fh:
        rows = list(csv.DictReader(line for line in fh if not line.startswith("#")))
    assert all(float(r["gg_ripl3_ev"]) > GAMGAM_MIN_EV for r in rows)  # eV, not TALYS's keV number


def _cn(Z, A):
    from physics.hf.compound.dens_reference import _gamma_parameters
    return _gamma_parameters(Z, A)[0]


def test_switch_reaches_the_compound_psf():
    prev = ggnorm.set_mode("")
    try:
        assert float(_cn(79, 197).ftable[1, 1]) == 1.0
        ggnorm.set_mode("ripl3d0")
        g = ggnorm.table("g_ripl3d0")[(79, 198)]
        gp = _cn(79, 197)
        assert float(gp.ftable[1, 1]) == pytest.approx(g, rel=0, abs=0)
        assert float(gp.ftable[0, 1]) == 1.0  # M1 untouched
        assert float(_cn(92, 238).ftable[1, 1]) == 1.0  # actinides are not this lever's
        assert ggnorm.factor(92, 239) == 1.0
    finally:
        ggnorm.set_mode(prev)


def test_user_ftable_wins():
    import torch

    from physics.hf.compound.dens_reference import _build_gamma_parameters
    prev = ggnorm.set_mode("ripl3d0")
    try:
        t = np.zeros((2, 3))
        t[1, 1] = 0.777
        gp = _build_gamma_parameters(79, 197, {"ftable": torch.as_tensor(t)})[0]
        assert float(gp.ftable[1, 1]) == pytest.approx(0.777)
    finally:
        ggnorm.set_mode(prev)


def test_bad_mode_refused():
    with pytest.raises(ValueError):
        ggnorm.set_mode("bnl")
