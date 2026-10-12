"""STELLARSEF (INCOGNITA_STELLAR): switch default OFF; the Maxwellian integrator on a 1/v cross section.
Engine-level checks (bit-identity OFF/ON, reciprocity <= 1e-6, factorised W = 1 capture == _case) are run by
development notes (Step 0) on real targets."""
import math

import numpy as np

from physics.hf.astro import stellar


def test_default_off(monkeypatch):
    monkeypatch.delenv("INCOGNITA_STELLAR", raising=False)
    assert not stellar.enabled()
    monkeypatch.setenv("INCOGNITA_STELLAR", "y")
    assert stellar.enabled()


def test_maxwellian_one_over_v():
    # sigma = c / sqrt(E): int_0^inf E sigma e^{-E/kT} dE = c Gamma(3/2) kT^{3/2}
    kt, c = 0.03, 2.0
    e = np.logspace(-3, np.log10(3.0), 25)
    got = stellar._maxw(e, c / np.sqrt(e), kt)
    want = c * math.gamma(1.5) * kt ** 1.5
    assert abs(got / want - 1) < 2e-4
