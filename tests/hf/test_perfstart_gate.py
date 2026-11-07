"""PERFSTART gate: the start-up work (lazy scipy, gc.freeze after the imports, fast exit, stage cache) moves no number.

Fe-56, Zr-90, Au-197, U-238 at 1 MeV, 14 MeV and on the library's 64-point grid, each a fresh engine job
(scripts/perfstart/job.py), against reference outputs made by the engine before the change
(`python scripts/perfstart/gate.py make REFDIR` on that commit). Every output array must be bit-identical, or within
1e-12 relative. Set PERFSTART_REF=REFDIR to run it (several minutes, needs TALYS structure data and the v0.2 deck
inputs); without it the test is skipped. INCOGNITA_STAGE_CACHE / INCOGNITA_CC_CACHE in the environment are passed on,
so the same gate covers the disk caches on and off.
"""

import importlib.util
import os
from pathlib import Path

import pytest

REF = os.environ.get("PERFSTART_REF", "")
GATE = Path(__file__).resolve().parents[2] / "scripts" / "perfstart" / "gate.py"


def _gate():
    spec = importlib.util.spec_from_file_location("perfstart_gate", GATE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_compare_detects_difference(tmp_path):
    np = pytest.importorskip("numpy")
    g = _gate()
    a, b = tmp_path / "a.npz", tmp_path / "b.npz"
    x = np.array([1.0, 2.0, 0.0])
    np.savez(a, ch_xs000000=x, tot_total=x)
    np.savez(b, ch_xs000000=x, tot_total=x)
    assert g.compare(str(a), str(b))[0] == {}
    np.savez(b, ch_xs000000=x * (1 + 1e-9), tot_total=x)
    bad, _ = g.compare(str(a), str(b))
    assert set(bad) == {"ch_xs000000"} and bad["ch_xs000000"][1] > g.REL


@pytest.mark.slow
@pytest.mark.skipif(not REF or not os.path.isdir(REF), reason="set PERFSTART_REF to a gate.py reference directory")
def test_perfstart_gate(tmp_path):
    rep = _gate().check(REF, str(tmp_path))
    bad = {k: v for k, v in rep.items() if not v.get("ok")}
    assert not bad, bad
