"""The adopted T3 echo harness reproduces the inputs of the runs T3's tests are built on."""

from __future__ import annotations

import ast
import os
from pathlib import Path

import pytest

from physics.hf import talys_defaults_echo as E
from physics.hf import talys_reference as T

ROOT = Path(__file__).resolve().parents[2]
RAW = Path(os.environ.get("INCOGNITA_T3_ECHO_RAW", ROOT / "features" / "hf_reference" / "t3_echo"))


def test_seventy_uniquely_named_cases_over_the_reference_targets():
    names = [c[0] for c in E.cases()]
    assert len(names) == 70 and len(set(names)) == 70
    assert [(s, a) for s, _, a in E.TARGETS] == [(t.symbol, t.A) for t in T.REFERENCE_SET]
    assert [z for _, z, _ in E.TARGETS] == [t.Z for t in T.REFERENCE_SET]


def test_grid_energies_ascend():
    for c in E.cases():
        if isinstance(c[4], tuple):
            assert all(b > a for a, b in zip(c[4], c[4][1:]))  # noqa: B905


def test_harness_stays_python39_stdlib():
    src = (ROOT / "physics/hf/talys_defaults_echo.py").read_text()
    tree = ast.parse(src, feature_version=(3, 9))
    mods = {n.names[0].name.split(".")[0] for n in ast.walk(tree) if isinstance(n, ast.Import)}
    mods |= {n.module.split(".")[0] for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)}
    assert mods <= {"__future__", "argparse", "json", "os", "shutil", "subprocess", "time",
                    "concurrent", "pathlib"}  # fmt: skip


@pytest.mark.skipif(not RAW.is_dir(), reason="raw echo runs not present")
def test_regenerated_inputs_match_the_raw_runs_byte_for_byte():
    checked = 0
    for c in E.cases():
        p = RAW / c[0] / "talys.inp"
        if not p.exists():
            continue
        assert E.input_files(c)[0] == p.read_text(), c[0]
        checked += 1
    assert checked >= 60
