"""CAPSET-v2 parser fixes in data/ingest/exfor.py (opt-in V2_FIXES): default behaviour unchanged, each fix on."""

from __future__ import annotations

import numpy as np
import pytest

from data.ingest import exfor as X
from data.ingest.exfor_reactions import parse_reaction


@pytest.fixture
def v2():
    old = X.V2_FIXES
    X.V2_FIXES = X.V2_ALL
    X.V2_LOG.clear()
    yield
    X.V2_FIXES = old
    X.V2_LOG.clear()


def test_default_is_off() -> None:
    old = X.V2_FIXES  # INCOGNITA_X4_V2 may switch it on; test the default path explicitly
    X.V2_FIXES = frozenset()
    try:
        assert np.isnan(X._num("5.     -07"))
        assert X._num("4.75   +00") == 4.75
        assert X._dn() == X._DATA_NAMES
    finally:
        X.V2_FIXES = old


def test_numfix(v2) -> None:
    assert X._num("5.     -07") == pytest.approx(5e-7)
    assert X._num("7.     -03") == pytest.approx(7e-3)
    assert X._num(".5-3") == pytest.approx(5e-4)
    assert X._num("1.5-3") == pytest.approx(1.5e-3)


def test_uncertainty_split(v2) -> None:
    s, t, y = np.array([3.0]), np.array([5.0]), np.array([2.0])
    st, sy, m = X._split_uncertainty(s, t, None)
    assert m == "split_sys_derived" and st[0] == 3.0 and sy[0] == pytest.approx(4.0)
    st, sy, m = X._split_uncertainty(None, t, None)
    assert m == "total_unsplit" and sy is None and st[0] == 5.0
    st, sy, m = X._split_uncertainty(None, t, y)
    assert m == "total_minus_sys" and st[0] == pytest.approx(np.sqrt(21.0))
    st, sy, m = X._split_uncertainty(s, t, y)
    assert m == "split" and sy[0] == 2.0


def test_equivalence_routed_to_capture(v2) -> None:
    rx = parse_reaction("((71-LU-175(N,ABS),,SIG)=(71-LU-175(N,G)71-LU-176,,SIG))")
    assert rx.sf.sf3 == "ABS"
    r2 = X._route_equivalence(rx, "21322007", "")
    assert r2.sf.sf3 == "G" and r2.target.a == 175 and r2.raw == rx.raw
    assert "21322007/" in X.V2_LOG["eqroute"]


def test_kt_in_celsius(v2) -> None:
    rx = parse_reaction("(92-U-234(N,G)92-U-235,,SIG,,MXW)")
    c = X.Column("KT-K", "", "DEG-C", np.array([37.5]))
    assert X._col_to_ev(c, rx)[0] == pytest.approx(8.617333262e-5 * 310.65)
    e = X.Column("KT-K-ERR", "", "DEG-C", np.array([7.0]))
    assert X._col_to_ev(e, rx)[0] == pytest.approx(8.617333262e-5 * 7.0)


def test_version_from_zip_name() -> None:
    from pathlib import Path
    assert X.exfor_version_of(Path("raw/exfor/entry_2026-10-14.zip")) == "2026-10-14"
