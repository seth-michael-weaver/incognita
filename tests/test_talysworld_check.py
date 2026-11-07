"""scripts/talysworld/check.py: the engine's own capture is the library curve divided by the anchor factor of an ANCHORED
nuclide, in analyze() and in gridtop() alike (gridtop used the anchored curve as is)."""
import importlib.util
import math
import sys
from pathlib import Path

import pytest

pytest.importorskip("pandas")
_P = Path(__file__).resolve().parents[1] / "scripts" / "talysworld" / "check.py"
sys.path.insert(0, str(_P.parent))
_spec = importlib.util.spec_from_file_location("tw_check", _P)
S = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(S)


class _Row:
    def __init__(self, tier, src, sig):
        self.tier, self.value_source, self.sigma_b = tier, src, sig


def test_anchored_curve_divided_by_its_factor():
    r = _Row("ANCHORED", "blind curve x 1.25 (measured MACS anchor)", [0.5, 1.0])
    assert [round(v, 9) for v in S.engine_capture_mb(r)] == [400.0, 800.0]


def test_other_tiers_as_is():
    for t in ("MEASURED", "INTERPOLATED", "EXTRAPOLATED"):
        assert list(S.engine_capture_mb(_Row(t, "", [0.5]))) == [500.0]


def test_gridtop_uses_the_engine_capture():
    src = _P.read_text(encoding="utf-8")
    body = src[src.index("def gridtop("):src.index('if __name__ == "__main__"')]
    assert "engine_capture_mb(r)" in body and "np.asarray(r.sigma_b, float) * 1e3" not in body
