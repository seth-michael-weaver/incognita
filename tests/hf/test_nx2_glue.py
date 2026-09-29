"""NATIVEX2 lever `glue`: the per-energy glue rewrites give the numbers of the code they replace
(`HF_NX2_GLUE=0`), to the bit.

* `compound.prepare.densprepare` (the Tjl/Tl interpolation in C, `_rho0_rows`' discrete levels
  as one scatter) on every call of chained Fe-56 and U-238 runs, and `_rho0_rows` on synthetic
  residuals that take its edge cases (spins out of range, levels above Ntop with a missing-level
  factor, no continuum);
* `engine._BuiltInputs.channels` (the nucleus records, unreached nuclei shared across energies)
  on every call of the same runs;
* the whole chained runs with the lever on and off.
"""

from __future__ import annotations

import math
import os
from contextlib import contextmanager
from pathlib import Path

import numpy as np
import pytest
import torch

TALYS_DIR = Path(os.environ.get("TALYS_DIR", Path.home() / "opt/talys-src"))
needs_structure = pytest.mark.skipif(not (TALYS_DIR / "structure").is_dir(),
                                     reason="TALYS structure/ not installed")

RUNS = ((26, 56, (0.001, 1.0, 5.0, 14.0, 20.0)), (92, 238, (0.8, 9.0)))


def _built() -> bool:
    from physics.hf.native import nx2

    so = nx2.lib()
    return so is not None and hasattr(so, "nx2_glue_interp")


needs_build = pytest.mark.skipif(not _built(), reason="no libnx2 build "
                                 "(scripts/build_nx2_native.sh)")


@contextmanager
def lever(on: bool):
    old = os.environ.get("HF_NX2_GLUE")
    os.environ["HF_NX2_GLUE"] = "1" if on else "0"
    try:
        yield
    finally:
        if old is None:
            os.environ.pop("HF_NX2_GLUE", None)
        else:
            os.environ["HF_NX2_GLUE"] = old


def _same(a, b, where=()):
    """Structural equality, bit for bit (NaN equal to NaN), types included."""
    if isinstance(a, (torch.Tensor, np.ndarray)) or isinstance(b, (torch.Tensor, np.ndarray)):
        assert type(a) is type(b) and a.dtype == b.dtype and a.shape == b.shape, where
        x = a.detach().numpy() if isinstance(a, torch.Tensor) else a
        y = b.detach().numpy() if isinstance(b, torch.Tensor) else b
        assert np.array_equal(x, y, equal_nan=x.dtype.kind in "fc"), where
    elif isinstance(a, dict):
        assert isinstance(b, dict) and list(a) == list(b), where
        for k in a:
            _same(a[k], b[k], where + (k,))
    elif isinstance(a, (list, tuple)):
        assert type(a) is type(b) and len(a) == len(b), where
        for i, (x, y) in enumerate(zip(a, b)):  # noqa: B905
            _same(x, y, where + (i,))
    elif hasattr(a, "__dataclass_fields__"):
        assert type(a) is type(b), where
        for f in a.__dataclass_fields__:
            _same(getattr(a, f), getattr(b, f), where + (f,))
    elif isinstance(a, float):
        assert type(a) is type(b), where
        assert a == b or (math.isnan(a) and math.isnan(b)), where
    else:
        assert a == b, where


@pytest.fixture(scope="module")
def captured():
    """Every `densprepare` input and `_BuiltInputs.channels` call (with its result under each
    arm) of the chained runs, and the runs' results, with the lever on."""
    from physics.hf import engine as EN
    from physics.hf.compound import chain as CC
    from physics.hf.compound.prepare import densprepare

    torch.set_num_threads(1)
    calls = {"dens": [], "chan": [], "res": []}
    od, oc = CC.densprepare, EN._BuiltInputs.channels

    def dens(inp):
        calls["dens"].append(inp)
        return od(inp)

    def chan(self, *a):
        with lever(False):
            ref = oc(self, *a)
        with lever(True):
            got = oc(self, *a)
        calls["chan"].append((ref, got))
        return got

    CC.densprepare, EN._BuiltInputs.channels = dens, chan
    try:
        with lever(True), torch.no_grad():
            for Z, A, grid in RUNS:
                calls["res"].append(EN.run(injection=EN.ChainedFull(Z=Z, A=A,
                                                                    declared_energies=grid)))
    finally:
        CC.densprepare, EN._BuiltInputs.channels = od, oc
    assert densprepare is od
    return calls


@needs_build
@needs_structure
def test_densprepare_glue_is_the_numpy_body_to_the_bit(captured):
    from physics.hf.compound.prepare import densprepare

    n = sum(len(g) for _, _, g in RUNS)
    assert len(captured["dens"]) == n
    for inp in captured["dens"]:
        with lever(False):
            ref = densprepare(inp)
        with lever(True):
            got = densprepare(inp)
        _same(got, ref)
        assert any(ch.tjl is not None and ch.tjl.any() for ch in got.values())


@needs_structure
def test_channel_records_are_the_reference_records(captured):
    assert len(captured["chan"]) == sum(len(g) for _, _, g in RUNS)
    for ref, got in captured["chan"]:
        _same(got, ref)
        assert any(n.maxex == 0 for n in got.nuclei.values())
        assert any(n.edis_mev for n in got.nuclei.values())


@needs_build
@needs_structure
def test_whole_chained_runs_match_with_the_lever_off(captured):
    from physics.hf import engine as EN

    with lever(False), torch.no_grad():
        for (Z, A, grid), new in zip(RUNS, captured["res"]):  # noqa: B905
            old = EN.run(injection=EN.ChainedFull(Z=Z, A=A, declared_energies=grid))
            _same(new.e_inc_mev, old.e_inc_mev)
            for got, ref in ((new.channels_mb, old.channels_mb), (new.totals_mb, old.totals_mb),
                             (new.levels_mb, old.levels_mb),
                             (new.residual_production_mb, old.residual_production_mb)):
                _same(got, ref)


@pytest.mark.parametrize("nlast,ntop,nexmax", [(6, 3, 12), (6, 6, 12), (9, 2, 9), (0, 0, 5)])
def test_rho0_rows_scatter_is_the_level_loop(nlast, ntop, nexmax):
    from physics.hf.compound.prepare import DensResidual, _discfactor, _rho0_rows

    rng = np.random.default_rng(nlast * 100 + ntop)
    nex = nexmax + 1
    jdis = rng.uniform(-1.5, 44.0, size=nex)
    jdis[0], jdis[1 % nex] = 41.2, 3.5  # one spin above numJ, one half-integer
    r = DensResidual(
        type=1, zix=0, nix=1, A=56, nlast=nlast, ntop=ntop, nexmax=nexmax, sep_mev=7.6,
        ex_mev=np.linspace(0.0, 9.0, nex), dex_mev=np.full(nex, 0.3),
        maxj=rng.integers(3, 40, size=nex), parlev=rng.choice([-1, 1], size=nex),
        jdis=jdis, rhogrid=rng.random((nex, 41, 2)), ncum_nl=nlast + 1.7)
    rb = rng.uniform(0.2, 1.0, size=nex)
    df = _discfactor(r)
    _same(_rho0_rows(r, nex, rb, df, glue=True), _rho0_rows(r, nex, rb, df, glue=False))
