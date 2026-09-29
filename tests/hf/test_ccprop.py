"""CCPROP (ROUTE100 WP8): the log-derivative propagator, and the two facts that killed it.

`docs/results/hf-ccprop.md` is the verdict. These tests hold the evidence behind it:

* the propagator solves the same coupled-channels problem as `cc_block_w` -- its cross sections
  converge on the kernel's as the radial step shrinks (so the kill is not a bug);
* `ccprop.c` and the torch prototype are the same method on the same numbers;
* gate 1 fails on arithmetic: even the propagator's unreachable FLOP floor -- one complex inverse
  per ECIS step and nothing else -- is more than half of what the renormalised Numerov kernel
  costs on real blocks.
"""

from __future__ import annotations

import pytest
import torch

from physics.hf.core.tensors import DTYPE
from physics.hf.ecis import ccnative, ccprop


@pytest.fixture(autouse=True)
def _two_threads():
    prev = torch.get_num_threads()
    torch.set_num_threads(2)
    yield
    torch.set_num_threads(prev)


def _blocks(refine: int, twoj=(1, 9, 25, 41)):
    from physics.hf.ecis.coupling import channels
    from physics.hf.ecis.formfactor import rotational_form_factors
    from physics.hf.ecis.incident import _t4_parameters
    from physics.hf.ecis.reference import coupled_band
    from physics.hf.ecis.solver import _grid_and_kinematics
    from physics.hf.omp.schrodinger import PARMASS_AMU, nucleus_mass_amu

    try:
        band = coupled_band(92, 238)
    except Exception as exc:  # noqa: BLE001  (structure database absent on this machine)
        pytest.skip(f"no coupled band for U-238: {exc}")
    e = torch.tensor([1.5, 9.0], dtype=DTYPE)  # below soswitch: the `cc_block_w` path
    p = _t4_parameters(92, 238, 1, e, None)
    m_t = nucleus_mass_amu(92, 238)
    kin, h, nmatch, r = _grid_and_kinematics(p, PARMASS_AMU[1], m_t, 0.0, e, band["e_mev"],
                                             refine, True)
    ff = rotational_form_factors(p, m_t, r, band["rotbeta"], band["deformation_length"],
                                 2 * band["rotbeta"].numel(), 0.0, False)
    chs = [channels(tj, par, band["spin"], band["parity"], 20, band["kband"],
                    deformed_spin_orbit=False) for tj in twoj for par in (-1, 1)]
    return band, [c for c in chs if int(c.level.numel()) > 0], ff, kin, h, nmatch, r


def _reac(band, chs, ff, kin, h, nmatch, r, prop: bool) -> torch.Tensor:
    from physics.hf.ecis.solver import accumulate, smatrix_blocks

    if prop:
        pairs = [ccprop.smatrix_prop(c, ff, kin, h, nmatch, r, minus_identity=True) for c in chs]
    else:
        pairs = smatrix_blocks(chs, ff, kin, h, nmatch, r, minus_identity=True, exact_bits=False)
    tot = None
    for ch, (s, op) in zip(chs, pairs, strict=True):
        g = accumulate(ch, s, op, kin, float(band["spin"][0]), 0.5,
                       int(band["spin"].numel()), 20, minus_identity=True)
        tot = g["reac"].clone() if tot is None else tot + g["reac"]
    return tot


def test_propagator_converges_on_the_numerov_kernel_as_the_step_shrinks():
    """The log derivative solves the same equation: refining the grid closes the gap. It does NOT
    close it at ECIS's own step -- that is CCPROP's gate-2 kill, measured in
    docs/results/hf-ccprop.md, not asserted here."""
    gaps = []
    for refine in (1, 4, 16):
        band, chs, ff, kin, h, nmatch, r = _blocks(refine)
        a = _reac(band, chs, ff, kin, h, nmatch, r, prop=False)
        b = _reac(band, chs, ff, kin, h, nmatch, r, prop=True)
        gaps.append(float(((b - a).abs() / a.abs()).max()))
    assert gaps[0] > 1.0e-3, gaps       # nowhere near the 1e-6 / 1e-4 bar at ECIS's step
    assert gaps[1] < gaps[0] / 4.0, gaps  # and it is a discretisation gap, not a wrong equation
    assert gaps[2] < gaps[1] / 4.0, gaps


@pytest.mark.skipif(not ccprop.native_available(), reason="libccprop.so not built")
def test_c_kernel_is_the_torch_prototype():
    from physics.hf.ecis.solver import _block_operators

    _band, chs, ff, kin, h, nmatch, r = _blocks(1)
    for ch in chs:
        mm, nm = _block_operators(ch, ff, kin, r)
        assert nm is None
        py = ccprop.log_derivative(mm, h, nmatch, ch.l.to(DTYPE) + 1.0)
        c, flops = ccprop.log_derivative_native(ch, ff, kin, h, nmatch, r)
        rel = (c - py).abs() / py.abs().clamp_min(1.0e-300)
        assert float(rel.max()) < 1.0e-10, (ch.twoJ, ch.parity, float(rel.max()))
        assert flops > 0.0


def test_gate_1_fails_even_at_the_propagators_floor():
    """The FLOP model of `harness/ccprop_flops.py` on real U-238 blocks: one complex inverse per
    ECIS step -- no Simpson correction, no product, which is second order and so not a usable
    method -- still costs more than half of `cc_block_w`."""
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "harness"))
    import ccprop_flops as fl

    _band, chs, _ff, _kin, _h, nmatch, _r = _blocks(1)
    cur = prop = floor = 0.0
    for ch in chs:
        n3 = float(int(ch.level.numel())) ** 3
        for v in nmatch.tolist():
            cur += fl.cur_w(int(v), ccnative.STABILISE_EVERY) * n3
            prop += fl.prop_w(int(v), "neumann") * n3
            floor += fl.prop_w(int(v), "floor") * n3
    assert prop / cur > 0.5, prop / cur     # the fourth-order attempt: no win at all
    assert floor / cur > 0.5, floor / cur   # and the unreachable floor does not reach 2x either
