"""Warm engine pool (scripts/talysworld/warmpool.py).

Unit tests (always): the energy split and the merge of slice results.
Engine check (Linux with the production engine, opt-in: TW_ENGINE_TESTS=1, several minutes, 2 engine processes at
nice 10): scripts/talysworld/check_warm.py on Fe-56, Zr-90, Au-197, U-238 (library compositions), one energy and the
64-point library grid: warm-pool (two-arm compositions with their arms side by side), chunked (2 workers), reverse-order/concurrent and engine_job.py-via-pool outputs
must equal a fresh process per job to 1e-12 relative (also with deck keywords varied between interleaved jobs and with
the pool's cached h rule), and the pool's separation energies (table and fork) must equal the fresh ones.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

TW = Path(__file__).resolve().parents[2] / "scripts" / "talysworld"
sys.path.insert(0, str(TW))
import warmpool as WP  # noqa: E402

G64 = [10 ** (3 + i * (7.30103 - 3) / 63) for i in range(64)]


def test_split_covers_grid_once_and_ascending():
    for n in (1, 2, 3, 5, 64, 100):
        sl = WP.split(G64, n)
        assert len(sl) == min(n, 64)
        flat = [e for s in sl for e in s]
        assert sorted(flat) == sorted(G64) and len(flat) == len(set(flat))
        assert all(s == sorted(s) for s in sl)


def test_split_balances_cost():
    sl = WP.split(G64, 3)
    cost = [sum(WP.energy_cost(e) for e in s) for s in sl]
    assert max(cost) - min(cost) <= max(WP.energy_cost(e) for e in G64)


def test_merge_restores_grid_order():
    full = {c: [float(i) * k for i in range(64)] for k, c in ((1, "capture"), (2, "total"))}
    parts = []
    for s in WP.split(G64, 3):
        idx = [G64.index(e) for e in s]
        parts.append(dict(e_ev=s, channels={c: [v[i] for i in idx] for c, v in full.items()}, err="", cpu_s=1.0, wall_s=2.0, computed=len(s)))
    m = WP.merge(G64, parts)
    assert m["err"] == "" and m["e_ev"] == sorted(G64) and m["channels"] == full and m["chunks"] == 3
    assert "computed" not in m


def test_merge_reports_errors_and_missing():
    s = WP.split(G64, 2)
    ok = dict(e_ev=s[0], channels={"capture": [0.0] * len(s[0])}, err="")
    assert WP.merge(G64, [ok, dict(ok, err="boom")])["err"] == "boom"
    assert "missing" in WP.merge(G64, [ok])["err"]


ENGINE = Path(os.environ.get("TW_ENG", str(Path.home() / "fastgate_data/eng/16606b356d6e")))


@pytest.mark.skipif(os.environ.get("TW_ENGINE_TESTS") != "1" or not (ENGINE / ".venv/bin/python").exists(),
                    reason="engine check: set TW_ENGINE_TESTS=1 on a machine with the production engine (Linux)")
def test_engine_gate_warm_chunked_order_equal_fresh(tmp_path):
    out = tmp_path / "check_warm.json"
    p = subprocess.run([str(ENGINE / ".venv/bin/python"), str(TW / "check_warm.py"), "--workers", "2", "--out", str(out)],
                       capture_output=True, text=True, timeout=7200)
    S = json.loads(out.read_text())
    bad = [r for r in S["rows"] if not r["ok"]]
    assert not bad, bad
    assert S["n_checks"] >= 40 and p.returncode == 0
