"""data.ingest.endf.ladder_stats on the unresolved range, case A (LFW=0, LRF=1): every spin of the l-row counts."""
import math

import pytest

pytest.importorskip("pyarrow")
from data.ingest import endf as E  # noqa: E402


def _row(**kw):
    return dict(lru=2, lrf=1, formalism="URR", el_ev=1e4, l=0, **kw)


def test_case_a_uses_every_spin():
    # endf-parserpy case A: l_group holds {D, AJ, AMUN, GN0, GG}[m] for m = 1..NJS, no j_group (parse_mf2 j = None)
    r = _row(j=None, param_names=["D", "AJ", "AMUN", "GN0", "GG"],
             param_values=[[1000.0, 500.0], [0.0, 1.0], [1.0, 1.0], [0.1, 0.1], [0.03, 0.05]])
    s = E.ladder_stats([r], target_spin=0.5)
    assert math.isclose(s["d0_urr_ev"], 1 / (1 / 1000 + 1 / 500))
    g0, g1 = 1 / 4, 3 / 4                        # (2J+1) / (2 (2I+1)), I = 1/2
    assert math.isclose(s["s0_urr"], g0 * 0.1 / 1000 + g1 * 0.1 / 500)
    assert math.isclose(s["gamma_gamma_urr_ev"], (0.03 / 1000 + 0.05 / 500) / (1 / 1000 + 1 / 500))


def test_per_j_rows_use_the_lowest_energy():
    # cases B / C: one row per (l, J), arrays over energy: the first (lowest-energy) value
    rows = [_row(j=0.0, param_names=["D", "GN0", "GG"], param_values=[[1000.0, 900.0], [0.1, 0.2], [0.03, 0.03]]),
            _row(j=1.0, param_names=["D", "GN0", "GG"], param_values=[[500.0, 450.0], [0.1, 0.2], [0.03, 0.03]])]
    s = E.ladder_stats(rows, target_spin=0.5)
    assert math.isclose(s["d0_urr_ev"], 1 / (1 / 1000 + 1 / 500))
