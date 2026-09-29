"""The port refuses keyword settings it does not implement (physics/hf/input/defaults.py: UNPORTED).

Before 2026-09-22 three of them returned numbers that were not the model asked for (jlmomp y, alphaomp
3-5, gnorm y) and four crashed deep inside a calculation. Option resolution stays faithful to TALYS (the echo tests replay such inputs); starting a CALCULATION
with one of them must now fail, loudly.
"""
import pytest

from physics.hf.input.defaults import UNPORTED, default_options, reject_unported

REFUSED = [
    {"jlmomp": "y"},
    {"alphaomp": 3}, {"alphaomp": 4}, {"alphaomp": 5},
    {"preeqmode": 3},
    {"preeqspin": 3},
    {"twocomponent": "n"},
    {"gshell": "y"},
    {"gnorm": "y"},
]


@pytest.mark.parametrize("kw", REFUSED, ids=lambda d: " ".join(f"{k} {v}" for k, v in d.items()))
def test_unported_keyword_is_refused(kw):
    o = default_options(50, 120, "n", kw)          # resolving the options stays faithful to TALYS
    with pytest.raises(NotImplementedError, match="not ported"):
        reject_unported(o)                          # computing with them is refused


@pytest.mark.parametrize("kw", [{}, {"alphaomp": 6}, {"alphaomp": 7}, {"alphaomp": 1}, {"preeqmode": 2},
                                {"preeqspin": 2}, {"twocomponent": "y"}, {"jlmomp": "n"}, {"gnorm": "n"}, {"ldmodel": 2}])
def test_ported_settings_still_resolve(kw):
    reject_unported(default_options(50, 120, "n", kw))


def test_default_options_do_not_trip_the_guard_for_other_projectiles():
    for proj in ("n", "p", "d", "t", "h", "a", "g"):
        reject_unported(default_options(50, 120, proj, {}))


def test_every_guard_names_its_reason():
    assert all(len(msg) > 20 for _, _, msg in UNPORTED)


def test_a_cascade_refuses_an_unported_keyword():
    """End to end through the engine's own entry point (the keyword-lines path the screens use). Run in a
    subprocess: the fitted-library cards are cached per process, so setting them here would leak into
    every later test in the session."""
    import os, subprocess, sys

    from tests._data import need_talys

    need_talys()  # the cascade is built in a subprocess
    env = dict(os.environ, INCOGNITA_TALYS_FIT="lines", INCOGNITA_TALYS_FIT_LINES="jlmomp y")
    code = "import numpy as np; from physics.hf import warmrun; warmrun.new_cascade(50, 120, (float(np.float32(1.0)),))"
    r = subprocess.run([sys.executable, "-c", code], env=env, capture_output=True, text=True, timeout=600)
    assert r.returncode != 0 and "not ported: jlmomp y" in r.stderr, r.stderr[-400:]


def test_an_unapplied_gamma_resonance_cell_is_refused():
    """`sgradjust Z A f` (and the other giant/pygmy resonance cells) used to be parsed and ignored."""
    import os, subprocess, sys
    env = dict(os.environ, INCOGNITA_TALYS_FIT="lines", INCOGNITA_TALYS_FIT_LINES="strength 2;sgradjust 50 121 0.5")
    code = "import numpy as np; from physics.hf import warmrun; warmrun.new_cascade(50, 120, (float(np.float32(1.0)),))"
    r = subprocess.run([sys.executable, "-c", code], env=env, capture_output=True, text=True, timeout=600)
    assert r.returncode != 0 and "not ported: `sgradjust 50 121" in r.stderr, r.stderr[-400:]
