"""scripts/build_capture_v2.py: the ladder's "changed vs previous step" count (counts_v2.json, README table)."""
import importlib.util
from pathlib import Path

import pytest

pl = pytest.importorskip("polars")

_P = Path(__file__).resolve().parents[1] / "scripts" / "build_capture_v2.py"
_spec = importlib.util.spec_from_file_location("build_capture_v2", _P)
B = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(B)


def test_dataset_absent_in_both_steps_is_not_a_change():
    # a dataset staged only from S3 on (e.g. recovered by the parser fix) is null in S0, S1 and S2: S1 vs S0 is NOT a change
    prev = pl.Series([None, "keep", "keep", None, "exclude"], dtype=pl.Utf8)
    cur = pl.Series([None, "keep", "exclude", "keep", None], dtype=pl.Utf8)
    assert B.changed_count(cur, prev) == 3          # value change, appeared, disappeared


def test_identical_steps_change_nothing():
    s = pl.Series([None, None, "keep", "downweight"], dtype=pl.Utf8)
    assert B.changed_count(s, s) == 0
