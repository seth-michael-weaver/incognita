"""NATIVEX: the compiled whole-stage kernels hold the numbers of the paths they replace.

* `compound.target_native.target` (`nx_target`) against `target_batch.case_nowfc` /
  `case_moldauer`'s torch path, on every energy of a chained run, fission humps included;
* `compound.widths_native.NativeWidths` (`nx_widths`) against `decay_fast.NucleusWidths`, array by
  array;
* whole runs with the kernels (the walk `nx_walk`, multiple pre-equilibrium in C and through the
  Python callback, the trapped leftover, a fissioning cascade) against `HF_NATIVEX=0`, which is
  the numpy/torch path SETB left.

Not bit-identical (sums in loop order): held to 1e-10 relative per array element or cell.
"""

from __future__ import annotations

import os
from contextlib import contextmanager
from pathlib import Path

import numpy as np
import pytest
import torch

TALYS_DIR = Path(os.environ.get("TALYS_DIR", Path.home() / "opt/talys-src"))
needs_structure = pytest.mark.skipif(not (TALYS_DIR / "structure").is_dir(),
                                     reason="TALYS structure/ not installed")


def _lib():
    from physics.hf.native import nativex

    return nativex.lib()


needs_build = pytest.mark.skipif(_lib() is None, reason="no nativex build "
                                 "(scripts/build_nativex_native.sh)")


@pytest.fixture(autouse=True)
def _one_thread():
    prev = torch.get_num_threads()
    torch.set_num_threads(1)
    yield
    torch.set_num_threads(prev)


@contextmanager
def env(**kw):
    """Environment switches, with the kernel loader's cache reset around them."""
    from physics.hf.native import nativex

    old = {k: os.environ.get(k) for k in kw}
    os.environ.update(kw)
    nativex.lib.cache_clear()
    try:
        yield
    finally:
        for k, v in old.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        nativex.lib.cache_clear()


def _rel(a, b) -> float:
    a, b = np.asarray(a, dtype=np.float64), np.asarray(b, dtype=np.float64)
    assert a.shape == b.shape, (a.shape, b.shape)
    den = np.maximum(np.abs(a), np.abs(b))
    return float(np.max(np.where(den > 1e-300, np.abs(a - b) / np.where(den > 0, den, 1.0), 0.0),
                        initial=0.0))


def _run(Z, A, grid, energies=None):
    from physics.hf.engine import ChainedFull
    from physics.hf.engine import run as engine_run

    with torch.inference_mode():
        return engine_run(injection=ChainedFull(Z=Z, A=A, declared_energies=grid,
                                                energies=energies))


def _same_results(new, old, tol=1e-10):
    assert list(new.e_inc_mev) == list(old.e_inc_mev)
    for got, ref in ((new.channels_mb, old.channels_mb), (new.totals_mb, old.totals_mb),
                     (new.levels_mb, old.levels_mb),
                     (new.residual_production_mb, old.residual_production_mb)):
        assert set(got) == set(ref)
        for key, v in ref.items():
            assert _rel(got[key], v) < tol, key


@needs_build
@needs_structure
@pytest.mark.parametrize("Z,A,grid", [(26, 56, (0.001, 1.0, 5.0, 14.0, 20.0)),
                                      (92, 238, (0.8, 9.0)),
                                      (41, 95, (0.5, 2.0, 5.0))])  # MERGEY: OPEN3M's A2 levels
def test_target_kernel_is_the_torch_path(Z, A, grid):
    import physics.hf.compound.target_native as tn
    from physics.hf.compound import target_batch as tb

    seen = []
    orig = tn.target

    def spy(inp, wfc, max_nex):
        out = orig(inp, wfc, max_nex)
        if out is not None:
            seen.append((inp, wfc, max_nex, out))
        return out

    tn.target = spy
    try:
        _run(Z, A, grid)
    finally:
        tn.target = orig
    assert any(w for _, w, _, _ in seen) and len(seen) >= len(grid)
    with env(HF_NATIVEX="0"):
        for inp, wfc, max_nex, (pop, fis) in seen:
            ref_pop, ref_fis = (tb.case_moldauer if wfc else tb.case_nowfc)(inp, None, max_nex)
            assert _rel(pop, ref_pop) < 1e-11
            assert _rel(fis, ref_fis) < 1e-11
    if A > 215:
        assert any(float(f) > 0.0 for _, _, _, (_, f) in seen)
    if (Z, A) == (41, 95):
        # MERGEY: Nb-95's L6 (5/2:13/2)+ is J = 3.0 on odd A, a level of impossible 2J parity
        # (OPEN3M's A2): the kernel must truncate l2'/2 into it as target_batch._prepare does
        assert any(bool(((inp.j2beg + np.asarray(r.jdis2[:min(r.nlast, r.maxex) + 1])
                          + r.parspin2) % 2).any())
                   for inp, _, _, _ in seen for r in inp.residuals.values())


@needs_build
@needs_structure
@pytest.mark.parametrize("Z,A,grid", [
    (26, 56, (1.0, 14.0, 20.0)),
    # NXC: the kernels skip rows past nexmax, spins past a row's maxJ and columns past a row's
    # last transmission; a heavy target and a sub-keV odd-A one exercise those extents
    (82, 208, (0.5, 8.0, 20.0)),
    (63, 147, (0.001, 0.008044147)),
])
def test_native_widths_are_nucleus_widths(Z, A, grid):
    import physics.hf.compound.widths_native as wn
    from physics.hf.compound.decay_fast import NucleusWidths
    from physics.hf.compound.decay_native import spin_l_bounds
    from physics.hf.compound.prepare import PARSPIN2

    built = []
    init = wn.NativeWidths.__init__

    def spy(self, cas, st, sp, bins):
        init(self, cas, st, sp, bins)
        built.append((self, NucleusWidths(cas, st, sp, bins)))

    wn.NativeWidths.__init__ = spy
    try:
        _run(Z, A, grid)
    finally:
        wn.NativeWidths.__init__ = init
    assert len(built) >= (10 if (Z, A) == (26, 56) else len(grid))
    for nat, ref in built:
        assert np.array_equal(nat.zero6, ref.zero6)
        assert _rel(nat.dsum6, ref.dsum6) < 1e-12
        for a, b in zip(nat.exits, ref.exits, strict=True):
            assert a.closed == b.closed
            assert np.array_equal(a.nrows, b.nrows)
            if a.closed:
                continue
            rho = b.rho_c if b.rho_c.shape[-1] == 2 else np.repeat(b.rho_c, 2, axis=-1)
            assert _rel(a.rho_c, rho) < 1e-12
            tn = getattr(b, "Tn", None)  # set only with decay_native's build
            if tn is None:
                tn = b.T0 + b.T1 if b.t >= 1 else np.stack([b.T0, b.T1], axis=1)
            assert _rel(a.Tn, tn) < 1e-12
            assert _rel(a.D, b.D) < 1e-12
            lb, le = spin_l_bounds(ref.odd, PARSPIN2[b.t], ref.nj, b.jx)
            assert np.array_equal(a.lb, lb) and np.array_equal(a.le, le)
            assert a.nd == b.nd
            if a.nd:
                for f in ("tot0", "tot1", "rho_d"):
                    assert _rel(getattr(a, f), getattr(b, f)) < 1e-12
                assert np.array_equal(a.ird, b.ird) and np.array_equal(a.pd, b.pd)


def _count_walks():
    import physics.hf.emission.multiple_native as mn

    n = {"walk": 0}
    orig = mn.decay_nucleus

    def spy(*a, **k):
        out = orig(*a, **k)
        if out is not None:
            n["walk"] += 1
        return out

    return mn, orig, spy, n


@needs_build
@needs_structure
@pytest.mark.parametrize("Z,A,grid,energies,switches", [
    (26, 56, (0.001, 1.0, 5.0, 14.0, 20.0), None, {}),          # Moldauer, continuum, MPE in C
    (26, 56, (1.0, 20.0), (20.0,), {"HF_NATIVEX_MPE": "0"}),     # MPE through the callback
    (26, 56, (1.0, 20.0), (20.0,), {"HF_NATIVEX_WIDTHS": "0"}),  # the walk over NucleusWidths
    (63, 147, (0.001, 0.008044147), (0.008044147,), {}),         # the trapped leftover
    (69, 169, (0.001, 0.0017), (0.001,), {}),  # Tm-170: a level branching twice to one level
    (92, 238, (0.8, 9.0, 24.0), None, {}),                       # a fissioning cascade
    (82, 208, (0.5, 8.0, 20.0), None, {}),  # NXC: row, spin and l extents on a heavy cascade
])
def test_runs_are_the_numpy_path(Z, A, grid, energies, switches):
    mn, orig, spy, n = _count_walks()
    mn.decay_nucleus = spy
    try:
        with env(**switches):
            new = _run(Z, A, grid, energies)
    finally:
        mn.decay_nucleus = orig
    assert n["walk"] >= 1
    with env(HF_NATIVEX="0"):
        old = _run(Z, A, grid, energies)
    _same_results(new, old)
