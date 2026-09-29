"""OSENGINE: Incognita's own regional optical-model defaults, layered on the TALYS port's defaults.

Everything else under `physics/hf` answers one question -- *what does TALYS do?* -- and CHART1
measures the answer. This module is the one place that deliberately answers a different one:
*what does the evidence say TALYS should have done?* It holds corrections that OSREGION-style
pre-registered regional experiments have established against measured data, expressed in exactly
the form TALYS itself takes them (`rvadjust n 0.96`), and `input.defaults.default_params` applies
them to every run whose **target** is a region member. Because they go in as `default_params`
overrides rather than as resolved potential values, TALYS's own post-resolution links still run
(`rwadjust`/`awadjust` follow `rvadjust`/`avadjust`, input_omppar.f90:632), so an engine run of a
region member reproduces the TALYS run OSREGION actually measured -- keyword for keyword.

That makes it a *prior*, not a correction Stage C has to relearn: Stage B is already fixed when
Stage C first sees it. STAGECRECAL raised the question this module exists to answer
(`docs/results/hf-stagecrecal.md`); `docs/results/hf-osengine.md` reports the answer, and the
answer is **no**: out of sample the fix keeps 26 % of its Stage B gain as an engine prior against
STAGECRECAL's 30 % as a Stage C retrofit -- the same number, because Stage C's only physics input
*is* Stage B's curve, so there is no earlier place for a fix to enter and no difference for Stage C
to see. Wired a priori it still loses three quarters of itself to the measured neighbours of the
nuclides it corrects, and on the >2012 window it is +0.0077 (p = 0.024).

**So the regional defaults are OFF unless asked for** (`INCOGNITA_OMP_REGION=1`, or
`regional.set_enabled(True)`), and OSREGION's "a positive Stage B with a negative Stage C does not
ship" stands. What is wired is the mechanism and the region: one switch turns it on for a future
Stage B regeneration if the Stage C interaction is ever solved, and the switch is verified on every
live path (Python, the native `engine_c` chain, the chart path, the GPU capture kernel).

### The Os region (OSREGION, `docs/results/hf-osregion.md`)

Sixteen deformed nuclides Hf-174..180 / Ta-181 / W-180..186 / Re-185,187 / Os-186..188, whose
p-wave strength functions TALYS's default neutron OMP over-predicts as a block. The point is the
pre-registered regional minimiser of sum-over-region chi2(S0, S1) against the measured anchors
TALYS tabulates -- chosen with **no capture data** -- and it takes the regional chi2 from 5441 to
619 with 15 of the 16 improving, halves the region's capture RMS (0.1910 -> 0.0949, p = 0.0000)
and moves the whole chart's Stage B validation window by -0.0201 (p = 0.0006).

Two caveats, both from OSREGION's own pre-registered checks and both deliberately not patched
here, because trimming a pre-registered region by its results is how a lever stops being evidence:

* **Hf-174 fails S3** (chi2 23.0 -> 36.2): it is the one member admitted on its S1 defect while
  its S0 runs the other way, so lowering both helps one and hurts the other. It is kept.
* The (rv, av) minimum is a **degenerate diagonal valley**, not a point: rv0.98/av0.55 reaches
  chi2 229 and every point along the valley is worth the same -0.019..-0.020 at Stage B. The
  pre-registered point is used because it is the pre-registered one, not because 2-D argmin on
  this grid means anything.

### The deformed rotational region (OMPDEF, `docs/results/ompdef.md`)

OSREGION's 16 rows were a symptom. The cause is a regime: a target TALYS couples as a rigid rotor
(`colltype R`) gets the *global spherical* KD03 potential inside its coupled-channels solve, and
that potential's geometry was never constrained on deformed nuclei in CC. Measured against the
resonance-parameter anchors TALYS tabulates (S0, S1, R'), the whole region Nd..Os over-predicts the
p-wave strength function (median x2.2) and, toward Re/Os, S0 and R' too; the actinides, which TALYS
gives a dedicated dispersive CC potential (Soukhovitskii, RIPL 2408), and the vibrational/spherical
targets do not. So the rule is keyed to the regime, not to a list: **every `colltype R` target with
A >= 140 and Z < 90** gets one (`rvadjust n`, `avadjust n`) point, fitted to the S0/S1/R' of the
region's members with every blind-set nuclide left out of the fit (`scripts/ompdef/fit_rule.py`).
Nothing capture-related chose it. `INCOGNITA_OMP_DEFORMED=1` (or `set_deformed(True)`); off by
default, for the same CHART1 reason as below -- and because on blind capture it is a **genuine null**
(`docs/results/ompdef.md`: +0.0009 [-0.0066, +0.0115] with Stage C's S2 input, Stage B alone +0.0009;
Ta/Au/Tb/Os improve, Re-185/187 -- right before for the wrong reason -- get worse by 0.1-0.2 dex). When both switches are on, a nuclide in both regions
takes the deformed rule.

### Turning it on and off

`INCOGNITA_OMP_REGION=1` in the environment, or `regional.set_enabled(True)` / `disabled()` in
process. Note that even were the default flipped, the port's own fidelity measurements -- CHART1's
port-vs-TALYS cell comparison, `talys_reference`, the echo and A-* reference tests -- would have to
run with it off, since a deliberate departure from TALYS's defaults reads there as a port defect;
`hf_macspeed_chart.py run` sets the variable itself for that reason, and measures the departure
under `--engine-defaults` (0.99750 -> 0.96611 on CHART1's 482 nuclides, all of it the 16 members).
"""

from __future__ import annotations

import os
from collections.abc import Mapping
from contextlib import contextmanager
from functools import lru_cache

#: OSREGION's pre-registered 16 deformed members, as (Z, A) of the **target**.
OS_REGION: frozenset[tuple[int, int]] = frozenset({
    (72, 174), (72, 176), (72, 177), (72, 178), (72, 179), (72, 180),  # Hf
    (73, 181),                                                          # Ta
    (74, 180), (74, 182), (74, 183), (74, 186),                         # W
    (75, 185), (75, 187),                                               # Re
    (76, 186), (76, 187), (76, 188),                                    # Os
})

#: OSREGION's common anchored point, in TALYS's per-particle keyword form (`rvadjust n 0.96`).
OS_POINT: dict[str, dict[str, float]] = {"rvadjust": {"n": 0.96}, "avadjust": {"n": 0.75}}

#: OMPDEF's regional point for the deformed rotational region (`fit_rule.py`, fit set = the
#: region's S0/S1/R'-anchored members minus the blind set). Set once, before any scoring.
DEFORMED_POINT: dict[str, dict[str, float]] = {"rvadjust": {"n": 0.995}, "avadjust": {"n": 0.69}}

#: The region's definition: TALYS's own coupled-channels flag, on the rare-earth side of the chart.
DEFORMED_AMIN, DEFORMED_ZMAX = 140, 89

#: (Z, A) -> the run's OMP keyword defaults. One region today; a second one adds a second block.
_REGIONS: tuple[tuple[str, frozenset[tuple[int, int]], dict[str, dict[str, float]]], ...] = (
    ("osregion", OS_REGION, OS_POINT),
)

#: Off by default -- OSENGINE measured the fix as an engine prior and it did not survive Stage C
#: any better than as a retrofit (26 % vs 30 %), so nothing ships. See the module docstring.
_ENABLED = os.environ.get("INCOGNITA_OMP_REGION", "0") == "1"
#: Off by default too (CHART1 measures TALYS fidelity); see "The deformed rotational region".
_DEFORMED = os.environ.get("INCOGNITA_OMP_DEFORMED", "0") == "1"


@lru_cache(maxsize=4096)
def colltype(Z: int, A: int) -> str:
    """TALYS's collective model for target (Z, A): the `deformation/<Sym>.def` header letter,
    'S' when the nucleus has no block (deformpar.f90:128)."""
    from physics.hf.structure.files import read_deformation_file

    got = read_deformation_file(int(Z), int(A))
    return "S" if got is None else str(got[0]).strip() or "S"


def deformed_member(Z: int, A: int) -> bool:
    """In the deformed rotational region: `colltype R`, A >= 140, Z < 90. Ignores the switch."""
    return (int(A) >= DEFORMED_AMIN and int(Z) <= DEFORMED_ZMAX
            and colltype(int(Z), int(A)) == "R")


def deformed_enabled() -> bool:
    """Whether the deformed-region rule is applied to new runs."""
    return _DEFORMED


def enabled() -> bool:
    """Whether the regional defaults are applied to new runs."""
    return _ENABLED


def region_of(Z: int, A: int) -> str | None:
    """The name of the region (Z, A) belongs to, or None. Ignores the switches; the deformed
    region is reported only when its switch is on (it contains most of OSREGION's rows)."""
    if _DEFORMED and deformed_member(Z, A):
        return "deformed"
    for name, members, _ in _REGIONS:
        if (int(Z), int(A)) in members:
            return name
    return None


def overrides_for(Z: int, A: int) -> dict[str, dict[str, float]] | None:
    """`default_params` overrides for a run on target (Z, A), or None.

    TALYS: input_omppar.f90:1 (input_omppar), as the keywords `rvadjust n` / `avadjust n`
    Test: tests/hf/test_osengine.py
    """
    if _DEFORMED and deformed_member(Z, A):
        return {k: dict(v) for k, v in DEFORMED_POINT.items()}
    if not _ENABLED:
        return None
    for _name, members, point in _REGIONS:
        if (int(Z), int(A)) in members:
            return {k: dict(v) for k, v in point.items()}
    return None


def merged(Z: int, A: int, overrides: Mapping[str, object] | None) -> dict[str, object] | None:
    """`overrides` with the regional defaults underneath it: an explicit value for a keyword the
    region also sets **wins**, whole, because a caller sweeping `rvadjust` is measuring that
    keyword and must not silently get the region's value folded in."""
    region = overrides_for(Z, A)
    if region is None:
        return dict(overrides) if overrides else None
    if not overrides:
        return region
    region.update({str(k).lower(): v for k, v in overrides.items()})
    return region


def set_enabled(flag: bool) -> bool:
    """Switch the regional defaults on or off and drop every cache that holds a `Params` or
    anything built from one. Returns the previous setting.

    Processes that only read the environment (`INCOGNITA_OMP_REGION`) never need this; it exists
    for the port-fidelity harnesses and tests that toggle inside one process.
    """
    global _ENABLED
    prev, _ENABLED = _ENABLED, bool(flag)
    if prev != _ENABLED:
        _clear_caches()
    return prev


def set_deformed(flag: bool) -> bool:
    """Switch the deformed-region rule on or off (dropping the same caches as `set_enabled`).
    Returns the previous setting."""
    global _DEFORMED
    prev, _DEFORMED = _DEFORMED, bool(flag)
    if prev != _DEFORMED:
        _clear_caches()
    return prev


@contextmanager
def disabled():
    """`with regional.disabled():` -- the TALYS port's own defaults, nothing added."""
    prev, prev_d = set_enabled(False), set_deformed(False)
    try:
        yield
    finally:
        set_enabled(prev)
        set_deformed(prev_d)


def _clear_caches() -> None:
    """Drop every cache that holds a `Params` or anything built from one. The flag is in none of
    their keys, so a toggle inside a process has to empty them -- and that is the chart worker's
    own between-nuclides hygiene call, with nothing kept: `_default_params_values`'s templates are
    the unperturbed build either way, but `_structure_of`, `_transmission_cached`,
    `ecis.incident._PARAMS_CACHE` and the level-density memos all hold a resolved run."""
    from physics.hf.chartrun import drop_target_caches

    drop_target_caches(frozenset())


__all__ = ["DEFORMED_POINT", "OS_POINT", "OS_REGION", "colltype", "deformed_enabled",
           "deformed_member", "disabled", "enabled", "merged", "overrides_for", "region_of",
           "set_deformed", "set_enabled"]
