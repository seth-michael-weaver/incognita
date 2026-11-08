"""C-12 Elastic tab of the Every nuclide page (data.html): the comparison layer of INCOGNITA's R-matrix evaluation C12RM9.

data/light_evals/cmp/C12RM9.json (scripts/export_c12_compare.py, from the frozen fit) goes into docs/walkthrough/data/n/6/12.json
as rm.cmp through scripts/add_light_evals.py: the natC curve, the held-out natC totals, their log-bin averages, the IAEA
standard 2017 points and ENDF/B-VIII.1 natC as a comparator. The page draws the comparator only with the library overlay on.
"""
import json
import shutil
import subprocess
import importlib.util
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
SITE = REPO / "docs" / "walkthrough"
DATA = (SITE / "js" / "data.js").read_text(encoding="utf-8")
EV = REPO / "data" / "light_evals"


def _nuc():
    return json.loads((SITE / "data" / "n" / "6" / "12.json").read_text(encoding="utf-8"))


def test_c12_site_file_has_the_comparison_layer():
    rm = _nuc()["rm"]
    c = rm["cmp"]
    assert [d[0] for d in c["ds"]] == ["13759/13759004/", "13761/13761002/", "13761/13761003/", "22610/22610002/"]
    assert all(d[1] and d[2] for d in c["ds"])                       # author and year for the dataset list
    assert len(c["ho"]) == 1742 and {p[3] for p in c["ho"]} == {0, 1, 2, 3}
    assert len(c["std"]) == 33 and all(p[2] > 0 for p in c["std"])    # every standard point carries its 1 sigma
    assert len(c["bins"]) >= 20 and all(b[3] >= 5 for b in c["bins"])
    assert len(c["e_ev"]) == len(c["natc_b"]) == len(c["endf_b"])
    # the frozen curve itself stays pure C-12 and identical to the evaluation file (no library content in it)
    ev = json.loads((EV / "C12RM9.json").read_text(encoding="utf-8"))
    assert rm["sigma_b"] == ev["sigma_b"] and "endf_b" not in ev
    s = c["stats"]
    assert s["std_max_z"] < 0.3 and s["std_max_dev_pct"] < 0.2 and s["heldout_chi2n"] == pytest.approx(0.96, abs=0.005)
    assert s["offsets"]["22610002"]["vs_incognita_pct"] == pytest.approx(-6.4, abs=0.1)


def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_add_light_evals_merges_and_drops_cmp(tmp_path):
    ae = _load(REPO / "scripts" / "add_light_evals.py", "add_light_evals_c12t")
    out, src = tmp_path / "data", tmp_path / "light_evals"
    (out / "n" / "6").mkdir(parents=True)
    (src / "cmp").mkdir(parents=True)
    (out / "index.json").write_text(json.dumps({"rows": []}))
    (src / "C12RM9.json").write_text(json.dumps({"id": "C12RM9", "Z": 6, "A": 12, "label": "x"}))
    (src / "cmp" / "C12RM9.json").write_text(json.dumps({"id": "C12RM9", "ho": [[1.0, 4.7, None, 0]]}))
    ae.apply(out, src)
    rm = json.loads((out / "n" / "6" / "12.json").read_text())["rm"]
    assert rm["cmp"]["ho"] == [[1.0, 4.7, None, 0]] and "id" not in rm["cmp"]
    (src / "cmp" / "C12RM9.json").unlink()
    ae.apply(out, src)
    assert "cmp" not in json.loads((out / "n" / "6" / "12.json").read_text())["rm"]


def _node(code):
    node = shutil.which("node")
    if not node:
        pytest.skip("needs node")
    lines = DATA.splitlines()
    i = next(k for k, l in enumerate(lines) if l.startswith("  const num = "))
    j = next(k for k, l in enumerate(lines) if l.startswith("  const SUP = "))
    defs = "const WT = { dec: (s) => s };\n" + "\n".join(lines[i:j])
    return json.loads(subprocess.run([node, "-e", defs + "\n" + code], capture_output=True, text=True, encoding="utf-8", check=True).stdout)


def test_endf_drawn_only_with_the_overlay():
    rm = 'JSON.parse(require("fs").readFileSync(%s, "utf8")).rm' % json.dumps(str(SITE / "data" / "n" / "6" / "12.json"))
    nm = '{ ours: "o", pure: "p", endf: "e", col: "#00f", lcol: "#f0f" }'
    out = _node(f"const rm = {rm};\nconsole.log(JSON.stringify([false, true].map((on) => elCurves(rm, on, {nm}).map((c) => [c.name, !!c.dash]))));")
    assert out[0] == [["o", False]]                 # overlay off: INCOGNITA only
    assert out[1] == [["o", False], ["e", True]]    # overlay on: ENDF/B-VIII.1 dashed, as a comparator
    # without the comparison layer the tab falls back to the pure C-12 curve and never draws a library
    out = _node(f"const rm = {rm}; delete rm.cmp;\nconsole.log(JSON.stringify(elCurves(rm, true, {nm}).map((c) => c.name)));")
    assert out == ["p"]


def test_elastic_points_and_linear_range():
    rm = 'JSON.parse(require("fs").readFileSync(%s, "utf8")).rm' % json.dumps(str(SITE / "data" / "n" / "6" / "12.json"))
    out = _node(f"const rm = {rm}; const P = elPoints(rm.cmp); const C = elCurves(rm, true, {{}});\n"
                "const k = {}; P.forEach((p) => (k[p.kind] = (k[p.kind] || 0) + 1));"
                "console.log(JSON.stringify([k, elRange(C, P), linTicks(...elRange(C, P))]));")
    k, (y0, y1), ticks = out
    assert k["ho"] == 1742 and k["std"] == 33 and k["bin"] >= 20
    assert y0 == pytest.approx(1.5) and y1 == pytest.approx(5.3)
    assert ticks[0] == pytest.approx(1.5) and ticks[-1] == pytest.approx(5.0) and len(ticks) == 8


def test_elastic_tab_uses_a_linear_y_axis():
    assert 'const lin = tab === "el"' in DATA
