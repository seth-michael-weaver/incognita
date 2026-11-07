"""scripts/build_site_data.py: a fix-unit cell is shown with its unit factor applied (it is labelled 'unit fixed')."""
import importlib.util
import math
import sys
from pathlib import Path

import pytest

pytest.importorskip("pyarrow")
_P = Path(__file__).resolve().parents[1] / "scripts" / "build_site_data.py"
_spec = importlib.util.spec_from_file_location("build_site_data", _P)
S = importlib.util.module_from_spec(_spec)
sys.path.insert(0, str(_P.parent))
_spec.loader.exec_module(S)


def test_fix_unit_cell_is_scaled():
    # Y-89(n,g)Y-90m thermal Maxwellian, EXFOR 14657002: compiled 1.02 B, a x1000 slip for mb (CAPSET-v2 D6)
    assert math.isclose(S.shown_value(1.02, "fix-unit", 0.001), 1.02e-3)


def test_other_decisions_unchanged():
    for d in ("keep", "downweight", "exclude"):
        assert S.shown_value(1.02, d, 0.001) == 1.02      # an excluded dataset with a suggested factor stays as compiled
    assert S.shown_value(1.02, "fix-unit", None) == 1.02
    assert S.shown_value(1.02, "fix-unit", float("nan")) == 1.02


def test_n_use_counts_only_kept_and_downweighted():
    pts = [[0, 0, 1, 0.1, 0, "k", ""], [0, 0, 1, 0.1, 0, "d", ""], [0, 0, 1, 0.1, 0, "x", ""], [0, 0, 1, 0.1, 0, "f", ""]]
    assert S.n_use(pts) == 2
