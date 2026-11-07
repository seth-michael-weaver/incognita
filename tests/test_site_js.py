"""Site JS regressions (docs/walkthrough/js): data.js formatting, band lookup and axis range; pipeline.js pulse; nav.js."""
import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

JS = Path(__file__).resolve().parents[1] / "docs" / "walkthrough" / "js"
DATA = (JS / "data.js").read_text(encoding="utf-8")


def _node(code):
    node = shutil.which("node")
    if not node:
        pytest.skip("needs node")
    return json.loads(subprocess.run([node, "-e", code], capture_output=True, text=True, check=True).stdout)


def _defs():
    lines = DATA.splitlines()
    i = next(k for k, l in enumerate(lines) if l.startswith("  const num = "))
    j = next(k for k, l in enumerate(lines) if l.startswith("  const SUP = "))
    return "const WT = { dec: (s) => s };\n" + "\n".join(lines[i:j])


def test_fmtE_picks_the_unit_after_rounding():
    out = _node(_defs() + "\nconsole.log(JSON.stringify([999.95, 999.7, 999999, 1500, 2.5e6, 0.0253].map(fmtE)));")
    assert out == ["1 keV", "1 keV", "1 MeV", "1.5 keV", "2.5 MeV", "0.0253 eV"]


def test_band_between_its_points():
    # the (n,p) band sits at benchmark energies: a grid energy between two band points gets the log-log value
    out = _node(_defs() + "\nconst b = [[8e6, 1, 4], [1e7, 4, 16]];"
                "\nconsole.log(JSON.stringify([bandAt(b, 8e6), bandAt(b, Math.sqrt(8e7 * 1e6)), bandAt(b, 7e6), bandAt(null, 1)]));")
    assert out[0] == [8e6, 1, 4] and out[2] is None and out[3] is None
    assert abs(out[1][1] - 2) < 1e-9 and abs(out[1][2] - 8) < 1e-9


def test_y_padding_is_code_not_comment():
    for line in DATA.splitlines():
        if "y1 - y0 < 1) { y0 -= 0.5" in line:
            assert "//" not in line.split("y1 - y0 < 1")[0], line
            break
    else:
        raise AssertionError("y padding statement missing")


def test_pulse_cancels_the_running_animation_first():
    src = (JS / "pipeline.js").read_text(encoding="utf-8")
    body = src[src.index("function pulseTo"):]
    body = body[:body.index("\n  }")]
    assert body.index("cancelAnimationFrame") < body.index("= { path,")


def test_expert_menu_uses_chapter_short_names():
    nav = (JS / "nav.js").read_text(encoding="utf-8")
    for k in ("hauser", "optical", "densities", "strength", "exciton", "averages"):
        label = re.search(rf'\["{k}",3,"([^"]*)"\]', nav).group(1)
        short = re.search(r'title: "[^"]*", short: "([^"]*)"', (JS / "ch" / f"{k}.js").read_text(encoding="utf-8")).group(1)
        assert label == short, k
