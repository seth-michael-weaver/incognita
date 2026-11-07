"""scripts/build_site_overlay.py: comparator MACS in the centre-of-mass frame, as library v0.2.1+ (CHANGELOG v0.2.1)."""
import importlib.util
import math
from pathlib import Path

import numpy as np

_P = Path(__file__).resolve().parents[1] / "scripts" / "build_site_overlay.py"
_spec = importlib.util.spec_from_file_location("build_site_overlay", _P)
O = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(O)


def test_one_over_v_macs_is_sigma_at_lab_energy_kT_over_r():
    # sigma = 1/v: MACS(kT) (centre-of-mass definition, E = r E_lab) = sigma(E_lab = kT / r)
    e = np.geomspace(1e-5, 2e7, 40001); s = 1.0 / np.sqrt(e)
    awr = 15.8575                                     # O-16
    r = awr / (awr + 1)
    m = O.macs(e, s, [3e4], awr=awr)[0]
    assert math.isclose(m, 1 / math.sqrt(3e4 / r), rel_tol=2e-4)


def test_lab_frame_only_when_asked():
    e = np.geomspace(1e-5, 2e7, 40001); s = 1.0 / np.sqrt(e)
    assert math.isclose(O.macs(e, s, [3e4], awr=None)[0], 1 / math.sqrt(3e4), rel_tol=2e-4)


def test_stable_against_kT_round_off():
    # the antiderivative form gave 0.9996 at 31892 eV but 1.0088 at 31892.4 eV (round-off of F(x1) - F(x0))
    e = np.geomspace(1e-5, 2e7, 40001); s = 1.0 / np.sqrt(e)
    for kt in (5e3, 3e4, 31892.0, 31892.4, 1e5):
        assert math.isclose(O.macs(e, s, [kt], awr=None)[0] * math.sqrt(kt), 1.0, rel_tol=2e-4), kt


def test_constant_cross_section():
    # sigma = 1 b everywhere from 0: MACS = 2/sqrt(pi) (exactly, as the upper limit -> inf)
    e = np.r_[0.0, np.geomspace(1e-5, 2e7, 200)]; s = np.ones_like(e)
    assert math.isclose(O.macs(e, s, [3e4], awr=None)[0], 2 / math.sqrt(math.pi), rel_tol=1e-9)
