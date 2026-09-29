"""OSENGINE: the regional OMP defaults of `physics.hf.omp.regional`, on every path.

The point of the module is that a region member's run is the TALYS run OSREGION measured --
`rvadjust n 0.96` / `avadjust n 0.75` with TALYS's own links following -- and that nothing else
on the chart moves. These check exactly that, at the two places it can go wrong: the `Params`
the keywords land in, and the cross section the chart path (`chartrun.run_nuclide`, the native
`engine_c` chain, MACSPEED_FAST's call) actually returns.
"""

from __future__ import annotations

import pytest
import torch

from physics.hf.input.defaults import default_options, default_params, default_params_shared
from physics.hf.omp import regional

IN_REGION = [(76, 187), (74, 186), (72, 174), (75, 185)]
OUT_REGION = [(26, 56), (74, 184), (79, 197), (92, 238)]  # W-184 is deliberately NOT a member


@pytest.fixture(autouse=True)
def _on():
    """The defaults ship OFF (OSENGINE: they did not survive Stage C), so every test below has to
    ask for them. `test_the_shipped_default_is_off` is the one that checks that it is off."""
    prev = regional.set_enabled(True)
    yield
    regional.set_enabled(prev)


def _params(Z: int, A: int):
    return default_params(Z, A, default_options(Z, A))


def test_the_shipped_default_is_off():
    """Nothing in the engine departs from TALYS unless a caller asks: the module's own default,
    read before any fixture touches it, is off (`docs/results/hf-osengine.md`)."""
    import subprocess
    import sys

    out = subprocess.run(
        [sys.executable, "-c",
         "from physics.hf.omp import regional; print(regional.enabled())"],
        capture_output=True, text=True, check=True, env={"PATH": "/usr/bin:/bin"})
    assert out.stdout.strip() == "False", out


@pytest.mark.parametrize("Z,A", IN_REGION)
def test_region_member_carries_the_osregion_point(Z, A):
    p = _params(Z, A)
    assert regional.region_of(Z, A) == "osregion"
    assert float(p["rvadjust"][1]) == pytest.approx(0.96)
    assert float(p["avadjust"][1]) == pytest.approx(0.75)


@pytest.mark.parametrize("Z,A", OUT_REGION)
def test_everything_else_keeps_talys_defaults(Z, A):
    p = _params(Z, A)
    assert regional.region_of(Z, A) is None
    assert float(p["rvadjust"][1]) == 1.0
    assert float(p["avadjust"][1]) == 1.0


@pytest.mark.parametrize("Z,A", IN_REGION)
def test_talys_links_follow_the_regional_default(Z, A):
    """input_omppar.f90:632 -- `rwadjust`/`awadjust` take `rvadjust`/`avadjust` unless given.
    Going in as keywords rather than as resolved values is what makes this hold, and it is what
    makes an engine run of a member the same run TALYS did for OSREGION's grid."""
    p = _params(Z, A)
    assert float(p["rwadjust"][1]) == pytest.approx(0.96)
    assert float(p["awadjust"][1]) == pytest.approx(0.75)


@pytest.mark.parametrize("Z,A", IN_REGION)
def test_only_the_neutron_channel_moves(Z, A):
    """`rvadjust n`: particle type 1. The protons and alphas of the same run are untouched."""
    p = _params(Z, A)
    for k in (0, 2, 3, 4, 5, 6):
        assert float(p["rvadjust"][k]) == 1.0
        assert float(p["avadjust"][k]) == 1.0


def test_shared_and_copied_builds_agree():
    """`default_params_shared` takes a different route (the cached tensors themselves); a region
    member must not get TALYS's defaults down one and the region's down the other."""
    for Z, A in IN_REGION + OUT_REGION:
        o = default_options(Z, A)
        a, b = default_params(Z, A, o), default_params_shared(Z, A, o)
        for k in ("rvadjust", "avadjust", "rwadjust", "awadjust"):
            assert torch.equal(a[k], b[k]), (Z, A, k)


def test_caller_overrides_win_whole():
    """A fit sweeping `rvadjust` must measure `rvadjust`, not the region's value folded into it.
    The keyword the caller gives is taken entire; the one it does not give still gets the
    region's -- which is what `overrides` means everywhere else in `default_params`."""
    Z, A = 76, 187
    p = default_params(Z, A, default_options(Z, A), overrides={"rvadjust": {"n": 1.10}})
    assert float(p["rvadjust"][1]) == pytest.approx(1.10)
    assert float(p["avadjust"][1]) == pytest.approx(0.75)


def test_disabled_gives_the_ports_own_defaults():
    """`regional.disabled()` is what CHART1's port arm runs under: port vs stock TALYS, with no
    deliberate departure in it. It has to drop the caches, or the previous run's `Params` leaks."""
    Z, A = 76, 187
    with regional.disabled():
        p = _params(Z, A)
        assert float(p["rvadjust"][1]) == 1.0
        assert float(p["avadjust"][1]) == 1.0
    assert float(_params(Z, A)["rvadjust"][1]) == pytest.approx(0.96)


def test_the_chart_path_returns_the_corrected_cross_section():
    """The native fast path rule: the default has to reach the call the chart actually makes
    (`chartrun.run_nuclide` -> `engine_c.run`), not just the Python reference path. Os-187's
    capture drops ~40 % in the keV region under the OSREGION point, and a control nuclide is
    bit-identical with the default on and off.

    Test: this is the in-suite form of what `docs/results/hf-osengine.md` measures over the
    whole region against TALYS's own response to the same two keywords.
    """
    from physics.hf import chartrun

    e_mev = tuple(float(torch.tensor(e, dtype=torch.float32)) for e in (1.0e-3, 1.0e-2, 1.0e-1))

    def curve(Z, A):
        chartrun.drop_target_caches(frozenset())
        return chartrun.run_nuclide(Z, A, e_mev).channels_mb["xs000000"].double().clone()

    on = curve(76, 187)
    ctl_on = curve(74, 184)
    with regional.disabled():
        off = curve(76, 187)
        ctl_off = curve(74, 184)
    assert torch.equal(ctl_on, ctl_off), "a non-member moved"
    r = (on / off).tolist()
    assert all(0.4 < x < 0.9 for x in r), r
