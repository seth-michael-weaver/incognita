"""CCBLOCKD: the cheaper `cc_block_d` step against the reference one.

`physics/hf/native/ccfast.c` keeps `cc_block_d_ref` -- the four-complex-product step CCFAST2
shipped -- as the A arm, and `HF_CCBLOCKD` selects between them per kernel call. These tests hold
the new step to it on real coupled-channels blocks: same discretisation, same grid, same matching
point, so the only differences allowed are the ones summation order makes.

The bar is `docs/results/hf-ccblockd.md`'s: the coupled-channels observables within 1e-11 normwise
(the measured worst over the 112 CC targets is 4.8e-12, and the kernel's own product-reassociation
floor is 1.3e-12), and the raw `keep` solutions within 1e-9 -- they are defined only up to the
stabilisation's change of basis, which is why the observables and not `keep` are the real bar.

Task: CCBLOCKD. Test: tests/hf/test_ccblockd.py
"""

from __future__ import annotations

import os

import pytest
import torch

from physics.hf.core.tensors import DTYPE
from physics.hf.ecis import ccnative
from physics.hf.ecis import incident as inc_mod
from physics.hf.ecis.incident import incident_coupled
from physics.hf.ecis.reference import coupled_band

pytestmark = pytest.mark.skipif(
    not ccnative.available() or not hasattr(ccnative._load(), "cc_set_blockd"),
    reason="libccfast without CCBLOCKD; run scripts/build_ccfast_native.sh")

GRID = (1.0, 4.5, 11.0, 14.0, 18.0)  # two energies below soswitch and three above it
OBS = ("sigma_tot_mb", "sigma_reac_mb", "sigma_abs_mb", "sigma_shape_el_mb", "sigma_direct_mb")


def _arm(level: str):
    os.environ["HF_CCBLOCKD"] = level


def _run(Z: int, A: int):
    band = coupled_band(Z, A)
    inc_mod._SOLVED.clear()
    _, res = incident_coupled(None, Z, A, torch.tensor(list(GRID), dtype=DTYPE), band)
    inc_mod._SOLVED.clear()
    return res


def _normwise(new: torch.Tensor, old: torch.Tensor) -> float:
    scale = float(old.abs().max())
    return float((new - old).abs().max()) / (scale if scale > 0.0 else 1.0)


@pytest.fixture
def restore_arm():
    was = os.environ.get("HF_CCBLOCKD")
    yield
    if was is None:
        os.environ.pop("HF_CCBLOCKD", None)
    else:
        os.environ["HF_CCBLOCKD"] = was


@pytest.mark.parametrize("Z,A", [(60, 150), (92, 238)])
@pytest.mark.parametrize("level", ["1", "2"])
def test_observables_match_reference(Z, A, level, restore_arm):
    """Both levers, and the default one alone, reproduce the reference kernel's coupled-channels
    cross sections. Above `soswitch` this exercises `cc_block_d`; below it, `cc_block_w`, which
    the change does not touch and which must therefore stay bit-identical."""
    _arm(level)
    new = _run(Z, A)
    _arm("0")
    old = _run(Z, A)
    for name in OBS:
        d = _normwise(getattr(new, name), getattr(old, name))
        assert d <= 1e-11, f"{Z}-{A} {name} level {level}: {d:.3e}"


def test_deformed_block_keep_matches_reference(restore_arm):
    """The seven `keep` arrays of every deformed block of one target. They are the raw solutions,
    so the bar is 1e-9 normwise, not the observables' 1e-11."""
    seen = []
    real = ccnative._keep_raw

    def spy(ch, ff, kin, h_fm, nmatch, r_fm, stab=ccnative.STABILISE_EVERY):
        if not (ch.so_deriv_coef is not None and ff.so_r2 is not None):
            return real(ch, ff, kin, h_fm, nmatch, r_fm, stab)
        _arm("1")
        new = real(ch, ff, kin, h_fm, nmatch, r_fm, stab)
        _arm("0")
        old = real(ch, ff, kin, h_fm, nmatch, r_fm, stab)
        _arm("1")
        seen.append(max(_normwise(new[k], old[k]) for k in range(new.shape[0])))
        return new

    ccnative._keep_raw = spy
    try:
        _run(60, 150)
    finally:
        ccnative._keep_raw = real
    assert seen, "no deformed block was solved"
    assert max(seen) <= 1e-9, f"worst keep normwise {max(seen):.3e} over {len(seen)} blocks"


def test_spherical_spin_orbit_path_is_untouched(restore_arm):
    """`cc_block_w` (below `soswitch`) must be bit-identical: the change is in `cc_block_d` only."""
    _arm("1")
    new = _run(60, 150)
    _arm("0")
    old = _run(60, 150)
    lo = slice(0, 2)  # the two grid energies below soswitch
    for name in OBS:
        a, b = getattr(new, name)[lo], getattr(old, name)[lo]
        assert torch.equal(a, b), f"{name} moved below soswitch"
