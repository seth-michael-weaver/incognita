"""A Stage B engine table must cover the whole bundle, or the bundle must opt into the fallback."""

from __future__ import annotations

import numpy as np
import pytest

from models.stage_c_data import check_engine_coverage

TABLE = {"Z026N030M0": np.ones(4), "Z079N118M0": np.ones(4)}


def test_full_coverage_passes(monkeypatch):
    monkeypatch.delenv("INCOGNITA_STAGE_B_ALLOW_FALLBACK", raising=False)
    assert check_engine_coverage(["Z026N030M0", "Z079N118M0"], TABLE, "t.parquet") == []


def test_uncovered_nuclide_raises_with_its_name(monkeypatch):
    monkeypatch.delenv("INCOGNITA_STAGE_B_ALLOW_FALLBACK", raising=False)
    monkeypatch.delenv("INCOGNITA_STAGE_B_ALLOW_FALLBACK", raising=False)
    with pytest.raises(ValueError, match="Z050N070M0"):
        check_engine_coverage(["Z026N030M0", "Z050N070M0"], TABLE, "t.parquet")


def test_fallback_is_opt_in(monkeypatch):
    monkeypatch.setenv("INCOGNITA_STAGE_B_ALLOW_FALLBACK", "1")
    assert check_engine_coverage(["Z026N030M0", "Z050N070M0"], TABLE, "t.parquet") == ["Z050N070M0"]
