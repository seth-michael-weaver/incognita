"""`globalwtable n` must drop the global E1 wtable default (input_gammapar.f90:112-150)."""

from __future__ import annotations

import dataclasses

from physics.hf.compound.dens_reference import _structure_of
from physics.hf.gamma.parameters import gamma_parameters


def _wtable(flag: bool) -> float:
    o, _p, m = _structure_of(26, 56)
    o = dataclasses.replace(o, flagglobalwtable=flag)
    gp = gamma_parameters(26, 57, o, S_k0_mev=float(m.s_mev[0, 0, 1]), projectile_k0=o.k0)
    return float(gp.wtable[1, 1])


def test_globalwtable_flag_is_honoured():
    assert _wtable(False) == 1.0
    assert _wtable(True) != 1.0
