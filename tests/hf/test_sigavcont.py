"""SIGAVCONT: knockout sigav as one continuous window average (Incognita extension, default OFF).

TALYS's knockout.f90:110-126 switches sigav between the single bin eend (dE <= 2 MeV) and a whole-bin sum / dE
(dE > 2 MeV); the switch is discontinuous in the incident energy. `sigavcont y` replaces both by the exact average
of the linear interpolant of xsreac over [coulbar, emax]. OFF (no keyword, no environment) must be TALYS.
"""

from __future__ import annotations

import numpy as np
import pytest

from physics.hf.input.defaults import default_options
from physics.hf.preeq.complex import sigavcont_on, window_average


def test_off_by_default(monkeypatch):
    monkeypatch.delenv("INCOGNITA_SIGAVCONT", raising=False)
    o = default_options(75, 185)
    assert o.sigavcont is False and sigavcont_on(o) is False
    assert sigavcont_on(default_options(75, 185, overrides={"sigavcont": True})) is True


@pytest.mark.parametrize("val", ["1", "y", "yes", "on"])
def test_on_from_environment(monkeypatch, val):
    monkeypatch.setenv("INCOGNITA_SIGAVCONT", val)
    assert sigavcont_on(default_options(75, 185)) is True


def test_window_average_exact_and_continuous():
    x = np.array([1.0, 2.0, 3.0, 5.0, 8.0])
    y = 2.0 * x + 1.0
    # linear data: the average is the midpoint value, for any window inside the table
    for lo, hi in ((1.2, 1.3), (1.5, 4.5), (2.0, 8.0), (3.3, 3.300001)):
        assert window_average(x, y, lo, hi) == pytest.approx(2.0 * 0.5 * (lo + hi) + 1.0, rel=1e-9)
    # dE -> 0 and dE <= 0 give the point value at emax
    assert window_average(x, y, 4.0, 4.0) == pytest.approx(9.0)
    assert window_average(x, y, 6.0, 4.0) == pytest.approx(9.0)
    # flat beyond the last computed node (grid truncation never gives 0)
    assert window_average(x, y, 9.0, 12.0) == pytest.approx(17.0)
    # continuous in emax across the old dE = 2 switch
    vals = [window_average(x, y ** 2, 2.0, 2.0 + d) for d in np.linspace(1.9, 2.1, 201)]
    d = np.diff(vals)
    assert np.max(np.abs(np.diff(d))) < 1e-2 * np.max(np.abs(d))  # smooth slope, no jump
