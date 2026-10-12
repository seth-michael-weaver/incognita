"""CHUNKFIX: a target's curve must not depend on which other targets share its engine run (its chunk).

Every chart freeze (B11-B18) ran `engine_curves.py --only <300 targets>` with ONE `INCOGNITA_TALYS_FIT_LINES`
string holding the recipe lines of all 300 targets (their target and compound nuclei). TALYS keywords are in
absolute nuclide coordinates and `fitlib.apply_params` writes every cell that falls in the run's box, so a
neighbour's line lands on this target's RESIDUAL nuclei: n + Fe-56 decays through Mn-56 (p), Fe-55 (2n), ...,
which are the compound nuclei of n + Mn-55 and n + Fe-54. Run alone, those residuals kept stock values; run next
to Mn-55 or Fe-54, they got the recipe. The curve moved with the chunk (B18SHRINK attempt 1: up to 0.23 dex).

The physics decision: a residual nucleus takes the SAME global recipe, evaluated for that residual, as it would
as anyone's compound. So the recipe is handed to the engine as one chart-wide table
(`INCOGNITA_TALYS_FIT_LINES_FILE` / `engine_curves.py --lines-table`), and each run takes the lines of every nucleus
in its own box from it. A chunk-shared per-nucleus `INCOGNITA_TALYS_FIT_LINES` string is refused by the driver for
more than one target (`--shared-lines` reproduces a pre-CHUNKFIX freeze in its exact chunks).

Doc: development notes. Report: development notes.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

from physics.hf.input import fitlib

REPO = Path(__file__).resolve().parents[2]
CURVES = REPO / "scripts" / "bestfit" / "engine_curves.py"
TALYS_DIR = Path(os.environ.get("TALYS_DIR", Path.home() / "opt/talys-src"))
needs_structure = pytest.mark.skipif(not (TALYS_DIR / "structure").is_dir(),
                                     reason="TALYS structure/ not installed")
GRID = [3.0e4, 1.0e6, 5.0e6, 1.4e7]  # eV: keV capture plus the MeV range where the p / 2n residuals open

X = (26, 56)                      # n + Fe-56: compound Fe-57; residuals Fe-56 (n), Mn-56 (p), Fe-55 (2n), ...
Y = (25, 55)                      # n + Mn-55: compound Mn-56 = X's (n,p) residual
W = (26, 54)                      # n + Fe-54: compound Fe-55 = X's (n,2n) residual


def recipe(z: int, a: int) -> list[str]:
    """A made-up global recipe with a large, nucleus-dependent effect (level-density and E1 strength)."""
    ct = 0.9 * np.cos(0.7 * z + 0.3 * a)
    fe = 10 ** (0.3 * np.sin(0.5 * z - 0.2 * a))
    return [f"ctable {z} {a} {ct:.5f}", f"ftable {z} {a} {fe:.5f} e1"]


def own(t) -> list[str]:
    """What the freezes put in a chunk for target t: its target and compound nucleus lines."""
    z, a = t
    return recipe(z, a) + recipe(z, a + 1)


def table(chart) -> list[str]:
    """The recipe evaluated on every nucleus of a (small) chart around X, Y and W."""
    return [l for z in range(23, 28) for a in range(50, 60) if 0 < a - z < 40 for l in recipe(z, a)]


def _run(tmp: Path, name: str, targets, *, bag=None, lines_table=None, extra=()):
    out = tmp / name
    grid = tmp / "grid.json"
    grid.write_text(json.dumps(GRID))
    env = {k: v for k, v in os.environ.items() if not k.startswith("INCOGNITA_")}
    env.update(OMP_NUM_THREADS="1", MKL_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1")
    if bag is not None:
        env[fitlib.ENV_LINES] = ";".join(bag)
    cmd = [sys.executable, str(CURVES), "--arm", "nodata", "--out", str(out), "--cpus",
           os.environ.get("CHUNKFIX_TEST_CPUS", "0-0"), "--grid", str(grid), "--no-ingredients",
           "--only", ",".join(f"{z}-{a}" for z, a in targets), *extra]
    if lines_table is not None:
        p = tmp / f"{name}.table"
        p.write_text("\n".join(lines_table) + "\n")
        cmd += ["--lines-table", str(p)]
    r = subprocess.run(cmd, env=env, cwd=REPO, capture_output=True, text=True, timeout=1800)
    return r, out


def _curve(out: Path, t) -> np.ndarray:
    return np.load(out / f"{t[0]:03d}_{t[1]:03d}.npz")["capture_mb"]


@needs_structure
def test_target_curve_is_the_same_alone_and_in_any_chunk(tmp_path):
    """The invariant: X alone == X with Y == X with W, bit for bit, and the recipe does act on X."""
    T = table(None)
    runs = {"alone": [X], "withY": [X, Y], "withW": [W, X]}
    curves = {}
    for nm, tg in runs.items():
        r, out = _run(tmp_path, nm, tg, lines_table=T)
        assert r.returncode == 0, r.stderr[-2000:]
        curves[nm] = _curve(out, X)
    r, out = _run(tmp_path, "norecipe", [X])
    assert r.returncode == 0, r.stderr[-2000:]
    assert np.max(np.abs(np.log10(curves["alone"] / _curve(out, X)))) > 1e-3, "the recipe must act"
    for nm in ("withY", "withW"):
        np.testing.assert_array_equal(curves[nm], curves["alone"], err_msg=nm)


@needs_structure
def test_chunk_shared_per_nucleus_lines_are_refused(tmp_path):
    """The freezes' protocol (one per-nucleus line string for many targets) is exactly what leaked: the driver
    refuses it, and `--shared-lines` still runs it (to reproduce a pre-CHUNKFIX freeze in its exact chunks)."""
    r, _ = _run(tmp_path, "bag", [X, Y], bag=own(X) + own(Y))
    assert r.returncode != 0 and "CHUNKFIX" in (r.stderr + r.stdout)
    r, out = _run(tmp_path, "bag_legacy", [X, Y], bag=own(X) + own(Y), extra=("--shared-lines",))
    assert r.returncode == 0, r.stderr[-2000:]
    r1, out1 = _run(tmp_path, "bag_alone", [X], bag=own(X))   # one target: a plain TALYS input, allowed
    assert r1.returncode == 0, r1.stderr[-2000:]
    # ... and it IS chunk-dependent, which is why it is refused: Y's compound line (Mn-56) lands on X's residual
    assert not np.array_equal(_curve(out, X), _curve(out1, X))


def test_table_lines_are_those_of_the_runs_box(tmp_path, monkeypatch):
    """Unit fact behind the fix: from a chart-wide table, a run takes the lines of the nuclei in its own box
    (Zix 0..14, Nix 0..34 below the compound) and nothing else; the result does not depend on other targets."""
    p = tmp_path / "t.lines"
    p.write_text("strength 8\n" + "\n".join(table(None) + recipe(60, 150)) + "\n")
    monkeypatch.delenv(fitlib.ENV_LINES, raising=False)
    monkeypatch.setenv(fitlib.ENV_LINES_FILE, str(p))
    monkeypatch.setenv(fitlib.ENV, "nodata")
    assert "lines" in fitlib.modes()
    c = fitlib.cards(*X, arms=fitlib.modes())
    zs = {(z, a) for _, z, a, *_ in c.cells}
    assert (26, 57) in zs and (25, 56) in zs and (26, 55) in zs and (24, 53) in zs
    assert (60, 150) not in zs and (27, 57) not in zs and (26, 58) not in zs   # above the compound: outside the box
    assert dict(c.options).get("strength") == "8"
    assert any(s.startswith("lines table") for s in c.source)
