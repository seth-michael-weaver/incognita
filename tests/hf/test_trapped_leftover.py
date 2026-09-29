"""CHARTFIX: compound.f90:404-419's trapped flux reaches the exclusive channels.

A mother (J, parity) cell whose total decay width is zero does not keep its flux: `compound`
spreads it equally over the compound nucleus's OWN discrete levels and records it in
`xspopex`, `xspop` and `mcontrib(0, nex, nexout)` -- so, through `mcontrib`, in `feedexcl` and in
the exclusive channel cross sections. The port put it in `xspop` only, so every mb of it fell out
of the exclusive channels while staying in the residual production.

Eu-147 is where CHART1 saw it: 990 of the 3042 mb populating Eu-148 sit in one trapped bin, so
`(n,g)` was a flat 0.734 x TALYS from 1 keV to 1.5 MeV while `nonelastic` agreed to 1e-6. The
invariant the test asserts is TALYS's own: at an incident energy where nothing but a gamma can be
emitted, the exclusive `(n,g)` cross section IS the residual production of the compound nucleus.
"""

from __future__ import annotations

import pytest
import torch

GRID = (0.001, 0.008044147)


@pytest.fixture(scope="module")
def eu147():
    """Eu-147 at 8 keV dump-free, with every `BinFeeding.leftover_mb` the cascade produced."""
    import physics.hf.emission.feeding as fm
    from physics.hf.engine import ChainedFull
    from physics.hf.engine import run as engine_run

    seen = []
    decay0 = fm.Cascade.decay

    def decay2(self, st, nuclei, zcomp, ncomp, nex, **kw):
        out = decay0(self, st, nuclei, zcomp, ncomp, nex, **kw)
        if out is not None and out.leftover_mb:
            seen.append(((zcomp, ncomp), nex, out.leftover_mb))
        return out

    import os

    from physics.hf.native import nativex

    torch.set_num_threads(1)
    fm.Cascade.decay = decay2
    # NATIVEX: the spy watches `Cascade.decay`; the compiled walk (tests/hf/test_nativex.py holds
    # it to this path on the same Eu-147 energy) is switched off
    prev = os.environ.get("HF_NATIVEX")
    os.environ["HF_NATIVEX"] = "0"
    nativex.lib.cache_clear()
    try:
        res = engine_run(injection=ChainedFull(Z=63, A=147, declared_energies=GRID,
                                               energies=(GRID[1],)))
    finally:
        fm.Cascade.decay = decay0
        if prev is None:
            os.environ.pop("HF_NATIVEX", None)
        else:
            os.environ["HF_NATIVEX"] = prev
        nativex.lib.cache_clear()
    return res, seen


def test_the_trapped_branch_runs_here(eu147):
    _res, seen = eu147
    assert seen, "no trapped (J, parity) cell: the fixture no longer exercises compound.f90:404"
    assert max(v for _k, _n, v in seen) > 1.0  # mb, not rounding


def test_trapped_flux_stays_inside_the_exclusive_channel(eu147):
    """At 8 keV on Eu-147 only a gamma can be emitted, so TALYS's `xs000000.tot` equals its
    `rp063148.tot` (2580.67 = 2580.69 at 10 keV in TALYS's own output). Before the fix the port
    had 2263.23 against 3042.26 -- the 990 mb trapped bin, 26 % of the channel."""
    res, _seen = eu147
    ng = float(res.channels_mb["xs000000"][0])
    rp = float(res.residual_production_mb["rp063148"][0])
    assert ng == pytest.approx(rp, rel=2e-6)


def test_no_discrete_level_of_the_compound_nucleus_goes_negative(eu147):
    """The symptom that located it: `gamma_cascade` takes the level's intensity out of `xspop`
    (which had the leftover) and out of `xspopex` (which did not), so every discrete level of
    Eu-148 ended at -31.94 mb = -990 / 31."""
    res, _seen = eu147
    assert float(res.channels_mb["xs000000"][0]) > 0.0
    for k, v in res.levels_mb.items():
        if k.startswith("ng."):
            assert float(v[0]) >= -1.0e-9, k
