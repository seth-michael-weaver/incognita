"""CENGWIRE: which compiled kernels of `physics.hf` loaded, and one warning when some did not.

Every native loader in `physics/hf` returns `None` when its `.so` is missing or fails to load, and
its callers then take the Python path. That is the right behaviour per call -- a chart run must not
die on a box without a build -- but nothing anywhere said so, so a whole chart could run at Python
cost on a box whose kernels were never built and report nothing. `report` warns **once per
process**, naming every library that did not load and the script that builds it.

Nothing here is a TALYS routine, nothing here is on a physics path, and no number changes: the
kernels select themselves exactly as they did before, this only says out loud which ones did.

TALYS: none (build hygiene)
Test: tests/hf/test_cengwire.py
"""

from __future__ import annotations

import importlib
import os
import warnings

# (key, the stage it serves, `module:accessor` returning the library or None, the build script).
# The accessor is each loader's own public predicate, so this agrees with what the callers see
# rather than second-guessing it: `available()` returns a bool, `lib()` the library or None, and
# `bool(...)` of either is "loaded and switched on".
KERNELS: tuple[tuple[str, str, str, str], ...] = (
    ("hfnative", "transmission coefficients, ECIS radial and CC blocks",
     "physics.hf.native:available", "scripts/build_native.sh"),
    ("nativex", "whole-stage kernels: widths, the cascade walk, channels",
     "physics.hf.native.nativex:available", "scripts/build_nativex_native.sh"),
    ("nx2", "second-wave kernels: level densities, OMP, PSF, pre-equilibrium, DWBA, fission",
     "physics.hf.native.nx2:lib", "scripts/build_nx2_native.sh"),
    ("speedw", "multiple-emission bins and the DWBA Numerov sweep",
     "physics.hf.native.speedw:lib", "scripts/build_speedw_native.sh"),
    ("decaynative", "the compound-decay contraction and feed",
     "physics.hf.compound.decay_native:available", "scripts/build_decay_native.sh"),
    ("ccfast", "coupled-channels blocks and matching",
     "physics.hf.ecis.ccnative:available", "scripts/build_ccfast_native.sh"),
    ("engdecay", "the whole cascade of one (nuclide, energy) in one call",
     "physics.hf.engine_c:lib", "scripts/build_engine_c_native.sh"),
)

# the env switches that turn kernels off on purpose; a warning says so rather than telling
# somebody who typed `HF_NATIVE=0` to go and build what they just switched off
_SWITCHES = ("HF_NATIVE", "HF_NATIVEX", "HF_NX2", "HF_ENGINE_C", "HF_SPEEDW_NATIVE",
             "HF_CCFAST_NATIVE", "HF_NX2_LD", "HF_NX2_LD2")

_WARNED = False


def status() -> dict[str, bool]:
    """Whether each kernel of `KERNELS` is loaded and switched on, by key.

    A loader that raises counts as absent, which is how its callers already treat it.
    """
    out: dict[str, bool] = {}
    for key, _what, spec, _script in KERNELS:
        mod, _, attr = spec.partition(":")
        try:
            out[key] = bool(getattr(importlib.import_module(mod), attr)())
        except Exception:  # noqa: BLE001  (an unloadable kernel is a fallback, not a failure)
            out[key] = False
    return out


def switched_off() -> list[str]:
    """The `HF_*` switches explicitly set to 0 in this environment."""
    return [k for k in _SWITCHES if os.environ.get(k) == "0"]


def report(path: str = "the chart's default path") -> dict[str, bool]:
    """`status()`, having warned once per process about every kernel that did not load.

    Called from `chartrun.run_nuclide` (the chart's entry point), so a box with no build says so
    once instead of quietly running the Python path at full cost for 482 nuclides.
    `HF_NATIVE_QUIET=1` silences the warning; `status()` never warns.
    """
    global _WARNED
    st = status()
    if _WARNED or os.environ.get("HF_NATIVE_QUIET") == "1":
        return st
    _WARNED = True
    missing = [(key, what, script) for key, what, _spec, script in KERNELS if not st[key]]
    if not missing:
        return st
    off = switched_off()
    why = (f"switched off by {', '.join(f'{k}=0' for k in off)}" if off
           else "not built on this machine")
    # no "build: ..." advice for kernels somebody switched off on purpose
    lines = "\n".join(f"  - {key}: {what}" + ("" if off else f"\n      build: {script}")
                      for key, what, script in missing)
    warnings.warn(
        f"physics.hf: {len(missing)} of {len(KERNELS)} compiled kernel libraries did not load "
        f"({why}), so {path} runs the slower Python path for these stages:\n{lines}\n"
        "Results are unaffected -- only speed. Set HF_NATIVE_QUIET=1 to silence this.",
        RuntimeWarning, stacklevel=2)
    return st


def _reset_for_tests() -> None:
    """Let the once-per-process warning fire again (tests/hf/test_cengwire.py only)."""
    global _WARNED
    _WARNED = False
