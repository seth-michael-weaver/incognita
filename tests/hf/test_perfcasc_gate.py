"""Cascade speed check: the speed work on the gamma cascade / multiple emission, the level densities and the
pre-equilibrium stage must not change a single bit of the library job's cross sections.

For Fe-56, Zr-90, Au-197 and U-238 (the library compositions: JS(P,A) = arms P and A, actinide A(rotor) = arm AJ)
at one incident energy (1 MeV) and on the 64-point library grid (1 keV - 20 MeV, `data/perfcasc_grid64.json`), the
engine's total, elastic, nonelastic, capture, (n,p), (n,a), (n,2n), inelastic and fission cross sections of every arm
must equal, bit for bit, the reference made with the engine before the change
(`data/perfcasc_gate_ref.json`). `INCOGNITA_PERFCASC_RTOL` (default 0 = bit-identical) loosens that to a relative
tolerance for a change that cannot be bit-identical (it must then be stated with the change, at most 1e-10).

The job is the library v0.2 deck and runner (lines, SL table and the library runner and engine-pool code), which
is not part of this repository: the test is skipped without it (directory `INCOGNITA_PERFCASC_INPUTS`) or without the RIPL-4 level parameters the deck's `ctwindow2` reads. Runner: `perfcasc_gate_run.py`.
Regenerate the reference (only from an engine known to be right): INCOGNITA_PERFCASC_WRITE=1.
"""

from __future__ import annotations

import json
import math
import os
import subprocess
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
REF = HERE / "data" / "perfcasc_gate_ref.json"
GRID64 = HERE / "data" / "perfcasc_grid64.json"
INPUTS = Path(os.environ.get("INCOGNITA_PERFCASC_INPUTS", str(Path.home() / "libv02" / "inputs"))).expanduser()
NUCLIDES = {"fe56": (26, 56, "JS(P,A)"), "zr90": (40, 90, "JS(P,A)"), "au197": (79, 197, "JS(P,A)"),
            "u238": (92, 238, "ACTJS A(rotor)")}
GRIDS = ("e1mev", "grid64")

pytestmark = [pytest.mark.slow, pytest.mark.needs_data]


def _have_inputs() -> bool:
    return (INPUTS / "code" / "prodrun.py").is_file() and (INPUTS / "lines_P").is_dir() and (
        bool(os.environ.get("INCOGNITA_RIPL_LEVELS_PARAM"))
        or (REPO / "raw" / "ripl4" / "RIPL-4" / "levels" / "levels-param.data").is_file())


def _close(a: float, b: float, rtol: float) -> bool:
    if rtol == 0.0:
        return a == b or (math.isnan(a) and math.isnan(b))
    return abs(a - b) <= rtol * max(abs(a), abs(b))


@pytest.mark.parametrize("grid", GRIDS)
@pytest.mark.parametrize("nuc", sorted(NUCLIDES))
def test_perfcasc_gate(nuc, grid, tmp_path):
    if not _have_inputs():
        pytest.skip(f"library v0.2 deck inputs not found ({INPUTS}) or RIPL-4 levels-param missing")
    z, a, comp = NUCLIDES[nuc]
    gfile = tmp_path / "grid.json"
    gfile.write_text(json.dumps([1.0e6]) if grid == "e1mev" else GRID64.read_text())
    out = tmp_path / "out.json"
    cmd = [sys.executable, str(HERE / "perfcasc_gate_run.py"), "--repo", str(REPO), "--inputs", str(INPUTS),
           "--z", str(z), "--a", str(a), "--comp", comp, "--grid", str(gfile), "--cc", str(tmp_path / "cc"),
           "--out", str(out)]
    p = subprocess.run(cmd, capture_output=True, text=True, cwd=str(REPO), timeout=3600)
    assert p.returncode == 0 and out.is_file(), p.stdout[-2000:] + p.stderr[-4000:]
    got = json.loads(out.read_text())
    key = f"{nuc}/{grid}"
    if os.environ.get("INCOGNITA_PERFCASC_WRITE") == "1":
        ref = json.loads(REF.read_text()) if REF.is_file() else {}
        ref[key] = got
        REF.write_text(json.dumps(ref, indent=0, sort_keys=True) + "\n")
        pytest.skip("reference written")
    ref = json.loads(REF.read_text())[key]
    rtol = float(os.environ.get("INCOGNITA_PERFCASC_RTOL", "0"))
    assert rtol <= 1.0e-10
    assert sorted(got) == sorted(ref)
    bad = []
    for arm, chans in ref.items():
        assert sorted(got[arm]) == sorted(chans), (arm, sorted(got[arm]), sorted(chans))
        for ch, vals in chans.items():
            g = [float.fromhex(v) for v in got[arm][ch]]
            r = [float.fromhex(v) for v in vals]
            assert len(g) == len(r), (arm, ch)
            bad += [(arm, ch, i, r[i], g[i]) for i in range(len(r)) if not _close(r[i], g[i], rtol)]
    assert not bad, f"{len(bad)} values differ (rtol {rtol}); first: {bad[:5]}"
