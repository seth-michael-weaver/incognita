"""CENGLD2: level-density records shared across targets by the float record of their inputs
(`ld_nx2.densitypar_key` / `shared_record`) and the spec's maxJ + rhogrid in one C call
(`ld_ceng.spec_rows`, `native/ld.c` `ceng_ld_spec`), each against the path it replaces, bitwise.
Skipped without a `libnx2` build (scripts/build_nx2_native.sh)."""

from __future__ import annotations

import numpy as np
import pytest
import torch

from physics.hf.native import nx2

pytestmark = pytest.mark.skipif(nx2.lib() is None, reason="no libnx2 build")

# (Z, A) cascade nucleus of two targets
SHARED = [(25, 55, 26, 56, 26, 57), (26, 56, 26, 56, 28, 58), (49, 119, 50, 120, 50, 119),
          (67, 166, 68, 166, 68, 167)]


@pytest.fixture(autouse=True)
def _clean():
    from physics.hf.chartrun import drop_target_caches
    from physics.hf.density import ld_nx2

    prev = torch.get_num_threads()
    torch.set_num_threads(1)
    ld_nx2._SHARED.clear()
    drop_target_caches()
    yield
    ld_nx2._SHARED.clear()
    drop_target_caches()
    torch.set_num_threads(prev)


def _ld(Z, A, Zt, At, aadjust=None):
    from physics.hf.compound.dens_reference import _ld_build

    try:
        with torch.inference_mode():
            return _ld_build(Z, A, Zt, At, None, aadjust=aadjust)
    except Exception as exc:  # noqa: BLE001  (structure database absent on this machine)
        pytest.skip(f"no level density for {Z}-{A}: {exc}")


def test_key_plan_reads_the_body():
    """The key reads what `_densitypar_floats` reads, parsed from its source."""
    from physics.hf.density.ld_nx2 import _key_plan

    pfs, pgs, opts = _key_plan()
    names = {k for k, _ in pfs}
    assert {"aadjust", "alimit", "gammald", "pair", "s2adjust", "exmatchadjust"} <= names
    assert ("s2adjust", (0,)) in pfs and ("a", ()) in pfs
    assert {"pairconstant", "gammashell2", "kph", "rspincut"} <= set(pgs)
    assert {"ldmodel_of", "flagcol_of", "flagfission", "nlow_default", "shellmodel"} <= set(opts)


@pytest.mark.parametrize("Z,A,Zt1,At1,Zt2,At2", SHARED)
def test_shared_record_is_a_fresh_build(monkeypatch, Z, A, Zt1, At1, Zt2, At2):
    """A record taken from another target equals the one built for this target, field for field."""
    from physics.hf.chartrun import drop_target_caches
    from physics.hf.density import ld_nx2

    _ld(Z, A, Zt1, At1)
    drop_target_caches()
    hits = ld_nx2.CHECK["ok"]
    monkeypatch.setenv("HF_CENGLD2_XT_CHECK", "1")
    got = _ld(Z, A, Zt2, At2)
    assert ld_nx2.CHECK["ok"] > hits
    monkeypatch.setenv("HF_CENGLD2_XT", "0")
    drop_target_caches()
    ref = _ld(Z, A, Zt2, At2)
    ld_nx2._check_same(got, ref, (Z, A))
    assert got[0].Zix == ref[0].Zix and got[0].Nix == ref[0].Nix


def test_aadjust_is_a_new_key():
    """PARAMWIRE's aadjust reaches the record: a changed value neither hits the default record nor
    matches its numbers, and equals a build with sharing off."""
    import os

    from physics.hf.density import ld_nx2

    d = _ld(26, 57, 26, 56)
    n = len(ld_nx2._SHARED)
    a = _ld(26, 57, 26, 56, aadjust=1.1)
    assert len(ld_nx2._SHARED) > n
    assert float(a[0].alev) != float(d[0].alev)
    os.environ["HF_CENGLD2_XT"] = "0"
    try:
        ref = _ld(26, 57, 26, 56, aadjust=1.1)
    finally:
        del os.environ["HF_CENGLD2_XT"]
    ld_nx2._check_same(a, ref, (26, 57))


@pytest.mark.parametrize("Z,A,Zt,At", [(26, 57, 26, 56), (25, 56, 26, 56), (82, 209, 82, 208),
                                       (68, 167, 68, 166), (7, 15, 7, 14)])
@pytest.mark.parametrize("nl_shift", [0, 3, 40])
def test_spec_rows_are_maxj_and_rhogrid(Z, A, Zt, At, nl_shift):
    """`ceng_ld_spec` against `feeding._maxj_of` + `dens_reference.rhogrid_of`, bitwise, on a
    TALYS-like grid (and one with no continuum bin)."""
    from physics.hf.compound.dens_reference import rhogrid_of
    from physics.hf.core.grids import NUMJ
    from physics.hf.density.ld_ceng import spec_rows
    from physics.hf.density.ld_nx2 import _par
    from physics.hf.emission.feeding import _maxj_of, _spincut_parts

    ld, _, nl, _ = _ld(Z, A, Zt, At)
    if _par(ld) is None:
        pytest.skip("model outside the kernel")
    n = 30
    top = float(ld.edis_mev[min(nl, ld.nlevmax2)])
    dex = np.full(n, 0.37)
    ex = top + 0.2 + 0.37 * np.arange(n)
    nlx = min(nl, n - 1) if nl_shift == 40 else min(nl_shift, n - 1)
    with torch.inference_mode():
        got = spec_rows(ld, A, ex, dex, n, nlx, _spincut_parts, NUMJ)
        maxj = np.full(n, NUMJ, np.int64)
        if n - 1 > nlx:
            maxj[nlx + 1:] = _maxj_of(ld, A / 8.0, ex[nlx + 1:])
        ref = rhogrid_of(Z, A, Zt, At, ex, dex, maxj, nlx)
    assert got is not None
    assert np.array_equal(got[0], maxj)
    assert got[1].shape == ref.shape and got[1].tobytes() == ref.tobytes()
