"""Optical-model speed gate (scripts/perf/ompgate.py): capture, elastic, total, (n,p), (n,a), (n,2n) and fission, and a
digest of every exclusive channel and total, on Fe-56, Zr-90, Au-197 and U-238 at 14 MeV and on the 64-point library
grid, in the production configuration, must equal BIT FOR BIT the reference written by the engine before the speed work
(tests/hf/data/ompgate_ref.json); U-238 on the grid is also run from a filled coupled-channels cache.

Needs the TALYS structure database (TALYS_DIR), the library-run inputs (~/libv02/inputs or OMPGATE_INPUTS: lines_P,
sl_meas_b.csv) and the native kernels; skipped without them. About 2 CPU-minutes."""
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location("ompgate", ROOT / "scripts" / "perf" / "ompgate.py")
G = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(G)


@pytest.mark.slow
@pytest.mark.needs_data
@pytest.mark.needs_native
def test_ompgate_bit_identical():
    if not G.available():
        pytest.skip("ompgate: TALYS structure database or library-run inputs not found")
    if not G.REF.is_file():
        pytest.skip("ompgate: no reference (scripts/perf/ompgate.py write)")
    ref = json.loads(G.REF.read_text())
    bad = G.compare(ref, G.run_all(log=lambda s: None))
    assert not bad, "\n".join(bad)
