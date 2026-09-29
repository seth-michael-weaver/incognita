"""Smoke test for the TALYS subprocess wrapper.

Skipped when the TALYS binary is not installed (see docs/talys-install.md).
The 56Fe + n @ 1 MeV case takes ~1 s; the whole module stays well under 60 s.
"""

from __future__ import annotations

import numpy as np
import pytest

from physics.talys import runner
from physics.talys.runner import get_channel, parse_yandf, run_talys, talys_available

pytestmark = pytest.mark.skipif(
    not talys_available(), reason=f"TALYS binary not found at {runner.talys_binary()}"
)


@pytest.fixture(scope="module")
def fe56_1mev(tmp_path_factory):
    wd = tmp_path_factory.mktemp("talys_fe56")
    return run_talys(26, 56, [1.0], workdir=wd, timeout=120)


def test_fe56_total_xs_is_about_3_barn(fe56_1mev):
    res = fe56_1mev
    assert res["returncode"] == 0
    assert res["talys_version"] and res["talys_version"].startswith("TALYS-")
    tot = get_channel(res, "total")
    assert tot["MT"] == 1
    assert tot["E"].shape == (1,)
    assert tot["E"][0] == pytest.approx(1.0)
    # 56Fe(n,tot) at 1 MeV: evaluations sit around 3-4 b; TALYS default ~3.79 b.
    assert 2500.0 < tot["xs"][0] < 4500.0  # mb


def test_fe56_channel_consistency(fe56_1mev):
    res = fe56_1mev
    ch = res["channels"]
    for name in ("total", "elastic", "nonelastic", "capture", "inelastic"):
        assert name in ch, f"missing channel {name}; have {sorted(ch)}"
        assert isinstance(ch[name]["xs"], np.ndarray)
        assert ch[name]["xs"].shape == (1,)
    tot = ch["total"]["xs"][0]
    el = ch["elastic"]["xs"][0]
    non = ch["nonelastic"]["xs"][0]
    assert tot == pytest.approx(el + non, rel=1e-3)
    assert 0.0 < ch["capture"]["xs"][0] < 50.0  # (n,g) a few mb at 1 MeV
    assert ch["inelastic"]["xs"][0] < non
    assert ch["capture"]["MT"] == 102
    assert ch["inelastic"]["MT"] == 4
    assert get_channel(res, "(n,g)") is ch["capture"]
    # Threshold channels are not written at 1 MeV; lookups must fail cleanly.
    with pytest.raises(KeyError):
        get_channel(res, "n2n")


def test_workdir_contains_inputs_and_tables(fe56_1mev):
    from pathlib import Path

    wd = Path(fe56_1mev["workdir"])
    assert (wd / "talys.inp").is_file()
    assert (wd / "talys.out").is_file()
    assert (wd / "total.tot").is_file()
    assert (wd / "xs000000.tot").is_file()
    parsed = parse_yandf(wd / "xs000000.tot")
    assert parsed["meta"]["type"] == "(n,g)"
    assert parsed["columns"][:2] == ["E", "xs"]
    assert parsed["data"].shape[1] == len(parsed["columns"])


def test_parse_yandf_handles_empty_table(tmp_path):
    p = tmp_path / "empty.tot"
    p.write_text(
        "# header:\n#   title: X(n,2n) cross section\n# reaction:\n#   type: (n,2n)\n"
        "#   ENDF_MT: 16\n##       E             xs\n##     [MeV]          [mb]\n"
    )
    parsed = parse_yandf(p)
    assert parsed["meta"]["ENDF_MT"] == "16"
    assert parsed["data"].shape == (0, 2)


def test_missing_binary_raises(monkeypatch, tmp_path):
    monkeypatch.setenv("TALYS_BIN", str(tmp_path / "nope"))
    with pytest.raises(runner.TalysError):
        run_talys(26, 56, [1.0], workdir=tmp_path)
