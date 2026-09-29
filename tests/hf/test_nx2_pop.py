"""GLUEFINISH lever `pop`: `population.f90`'s bin loop in C holds the bits of the Python body it
replaces (`HF_NX2_POP=0`).

`nx2_pop_type` (native/nx2_pop.c, through `compound.pop_nx2.bin_loop`) against
`compound.population._bin_loop`, on randomised inputs that take every branch the kernel claims:

* the `_bin_nodes_many` node path (a strictly increasing egrid) and the `_bin_nodes` /
  `locate_scalar` path (a grid with a flat step, which `_bin_nodes_many` refuses);
* bins whose lower edge falls below `egrid[ib]` (`na1 = -1`, where the Python reads `egrid[-1]`
  for the abscissa and `spec[0]` for the ordinate) and bins that extrapolate past `egrid[ie]`;
* the 1e-30 cut, on a spectrum driven negative by the extrapolation;
* `flaggiant` (the giant-resonance addend) on and off;
* multiple pre-equilibrium, two-component and one-component;
* `pespinmodel >= 3`, which the wrapper must refuse.

Bitwise: the kernel does the same operations in the same order on the same doubles.
"""

from __future__ import annotations

import numpy as np
import pytest

from physics.hf.compound import pop_nx2
from physics.hf.compound.population import (
    PopResidual,
    PopulationInputs,
    PopulationResult,
    _bin_loop,
    _renormalise,
)


def _built() -> bool:
    return pop_nx2._fn() is not None


needs_build = pytest.mark.skipif(not _built(), reason="no libnx2 build "
                                 "(scripts/build_nx2_native.sh)")

MAXPAR = 6


def _residual(rng, t: int, etop: float, maxex: int, nlast: int, top=False) -> PopResidual:
    dex = np.full(maxex + 1, etop / (maxex + 1))
    ex = np.arange(maxex + 1) * dex[0]
    if top:  # the last bin sits at Etotal - S, so its lower edge falls below egrid[0]
        ex[maxex] = etop
    ex[: nlast + 1] = np.sort(rng.uniform(0.0, ex[nlast + 1], nlast + 1))
    return PopResidual(type=t, nlast=nlast, maxex=maxex, sep_mev=1.5 + 0.25 * t,
                       ex_mev=ex, dex_mev=dex)


def _inputs(rng, *, flaggiant=False, flagmulpre=False, flag2comp=True, flat=False,
            negative=False, pespinmodel=1, types=(1, 2, 3), etotal=22.0, maxen=40, ebegin=1,
            top=False):
    eg = np.concatenate([[0.0], np.linspace(0.1, 20.0, maxen)])
    if flat:  # a repeated node: `_bin_nodes_many` gives up and the scalar `locate` runs
        eg[maxen // 2] = eg[maxen // 2 - 1]
    residuals, xspreeq, tot, xsgr, gtot, step, step2 = {}, {}, {}, {}, {}, {}, {}
    for t in types:
        r = _residual(rng, t, etotal - (1.5 + 0.25 * t), 24 + t, 3 + t, top=top)
        residuals[t] = r
        s = rng.uniform(0.0, 5.0, eg.size)
        if negative:
            s[-6:] = np.linspace(2.0, -1.0, 6)
        s[0] = 0.0
        xspreeq[t] = s
        tot[t] = float(s.sum())
        xsgr[t] = rng.uniform(0.0, 0.5, eg.size)
        gtot[t] = float(xsgr[t].sum())
        step[t] = rng.uniform(0.0, 1.0, (MAXPAR + 1, eg.size))
        step2[t] = rng.uniform(0.0, 1.0, (MAXPAR + 1, MAXPAR + 1, eg.size))
    return PopulationInputs(
        etotal_mev=etotal, egrid_mev=eg,
        ebegin={t: ebegin for t in types}, eend={t: eg.size - 2 for t in types},
        residuals=residuals, xspreeq_mb=xspreeq, xspreeqtot_mb=tot,
        flaggiant=flaggiant, xsgr_mb=xsgr if flaggiant else {},
        xsgrtot_mb=gtot if flaggiant else {},
        pespinmodel=pespinmodel, maxjph=4,
        flagmulpre=flagmulpre, flag2comp=flag2comp, maxpar=MAXPAR,
        xsstep_mb=step, xsstep2_mb=step2)


def _reference(inp) -> PopulationResult:
    res = PopulationResult({}, {}, {}, {})
    eg = np.asarray(inp.egrid_mev, float)
    _bin_loop(inp, res, eg)
    return _renormalise(inp, res)


def _native(inp) -> PopulationResult | None:
    from physics.hf.compound.population import PARA, PARN, PARZ

    res = PopulationResult({}, {}, {}, {})
    eg = np.asarray(inp.egrid_mev, float)
    if not pop_nx2.bin_loop(inp, res, eg, PARA, PARZ, PARN):
        return None
    return _renormalise(inp, res)


def _same(a: PopulationResult, b: PopulationResult) -> None:
    assert sorted(a.preeqpopex_mb) == sorted(b.preeqpopex_mb)
    for t in a.preeqpopex_mb:
        np.testing.assert_array_equal(a.preeqpopex_mb[t], b.preeqpopex_mb[t])
        assert a.xscheck_mb[t] == b.xscheck_mb[t]
        assert a.norm[t] == b.norm[t]
        assert a.mulpre[t] == b.mulpre[t]
    assert sorted(a.xspopph2_mb) == sorted(b.xspopph2_mb)
    for t in a.xspopph2_mb:
        np.testing.assert_array_equal(a.xspopph2_mb[t], b.xspopph2_mb[t])
    assert sorted(a.xspopph_mb) == sorted(b.xspopph_mb)
    for t in a.xspopph_mb:
        np.testing.assert_array_equal(a.xspopph_mb[t], b.xspopph_mb[t])


@needs_build
@pytest.mark.parametrize("kw", [
    {},
    {"flaggiant": True},
    {"negative": True},
    {"flaggiant": True, "negative": True},
    {"flat": True},
    {"flat": True, "flaggiant": True},
    {"flagmulpre": True},
    {"flagmulpre": True, "flaggiant": True},
    {"flagmulpre": True, "flag2comp": False},
    {"flagmulpre": True, "flat": True},
    {"types": (0, 1, 2, 3, 4, 5, 6)},
    {"etotal": 8.0},          # residual grids that start below egrid[ib]
    {"etotal": 40.0},         # bins that extrapolate past egrid[ie]
    {"etotal": 40.0, "flagmulpre": True},
    {"ebegin": 0, "top": True},          # `na1 = ib - 1 = -1`: egrid[-1] wraps for the abscissa
    {"ebegin": 0, "top": True, "flaggiant": True},
])
def test_bitwise_against_the_python_body(kw):
    rng = np.random.default_rng(20260916)
    for _ in range(4):
        inp = _inputs(rng, **kw)
        got = _native(inp)
        assert got is not None, "the kernel refused an input it claims to take"
        _same(_reference(inp), got)


@needs_build
def test_pespinmodel_3_is_refused():
    rng = np.random.default_rng(7)
    assert _native(_inputs(rng, pespinmodel=3)) is None


@needs_build
def test_lever_off(monkeypatch):
    monkeypatch.setenv("HF_NX2_POP", "0")
    rng = np.random.default_rng(11)
    assert _native(_inputs(rng)) is None


@needs_build
def test_population_dispatches_and_agrees():
    """`population` itself: the lever on and off give the same object, bit for bit."""
    import os

    from physics.hf.compound.population import population

    rng = np.random.default_rng(3)
    inp = _inputs(rng, flaggiant=True, flagmulpre=True)
    fast = population(inp)
    os.environ["HF_NX2_POP"] = "0"
    try:
        slow = population(inp)
    finally:
        os.environ.pop("HF_NX2_POP")
    _same(slow, fast)
