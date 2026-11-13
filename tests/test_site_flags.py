"""Data explorer comparison files: index.json says which exist, and data.js fetches only those.

scripts/build_site_data.py records index list "lib" (Z with a data/lib/<Z>.json, scripts/build_site_overlay.py) and
column "rr" (1 when data/rr/<Z>/<A>.json exists, scripts/build_site_rr.py), read from the published files. Before this,
opening a Z 1-7 nuclide (C-12, ...) requested data/lib/6.json and data/rr/6/12.json and logged two 404s.
"""
import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

WT = Path(__file__).resolve().parents[1] / "docs" / "walkthrough"
DATA = WT / "data"
IDX = json.loads((DATA / "index.json").read_text(encoding="utf-8"))
COL = {c: i for i, c in enumerate(IDX["cols"])}


def _lib_files():
    return {int(p.stem) for p in (DATA / "lib").glob("*.json") if p.stem.isdigit()}


def _rr_files():
    return {(int(p.parent.name), int(p.stem)) for p in (DATA / "rr").glob("*/*.json")}


def _rr_flagged():
    return {(r[COL["Z"]], r[COL["A"]]) for r in IDX["rows"] if r[COL["rr"]] == 1}


def test_lib_list_is_exactly_the_files():
    assert IDX["lib"] == sorted(IDX["lib"]) and set(IDX["lib"]) == _lib_files()


def test_rr_column_is_exactly_the_files():
    assert all(r[COL["rr"]] in (0, 1) for r in IDX["rows"])
    assert _rr_flagged() == _rr_files()   # every flagged file exists, and every file is flagged (each is an index row)


def test_light_nuclides_without_files_are_unflagged():
    c12 = next(r for r in IDX["rows"] if r[COL["Z"]] == 6 and r[COL["A"]] == 12)
    assert c12[COL["rr"]] == 0 and 6 not in IDX["lib"]
    assert not (DATA / "rr" / "6" / "12.json").exists() and not (DATA / "lib" / "6.json").exists()


def test_rr_readme_count_matches_the_files():
    # data/rr/README.md is copied from the resonance-fill output by scripts/build_site_rr.py; its file count must match what is published
    m = re.search(r"`rr/<Z>/<A>\.json`, (\d+) files", (DATA / "rr" / "README.md").read_text(encoding="utf-8"))
    assert m and int(m.group(1)) == len(_rr_files())


def _block(src, start, stop):
    lines = src.splitlines()
    i = next(k for k, l in enumerate(lines) if l.startswith(start))
    j = next(k for k in range(i, len(lines)) if lines[k].startswith(stop))
    return "\n".join(lines[i:j])


def test_data_js_fetches_only_flagged_files(tmp_path):
    node = shutil.which("node")
    if not node:
        pytest.skip("needs node")
    src = (WT / "js" / "data.js").read_text(encoding="utf-8")
    nkey = next(l for l in src.splitlines() if l.startswith("  const nkey = "))
    # the index callback's first lines: IDX (with its "lib" set), the column map and the rows (with their "rr" flag)
    head = _block(src, "    IDX = idx;", "    rows.forEach(")
    code = "\n".join([
        "const fs = require('fs'); const idx = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));",
        "const got = []; const fetch = (u) => { got.push(u); return Promise.resolve({ ok: true, json: () => ({}) }); };",
        "let IDX = null, rows = []; const byKey = new Map(); const readColors = () => {};",
        nkey, _block(src, "  const lcache = ", "  let libOn"), _block(src, "  const rrcache = ", "  let TH = null"),
        head,
        "for (const Z of idx.natural) rows.push({ Z, A: 0 });",
        "rows.forEach((r) => byKey.set(r.Z + '-' + r.A, r));",
        "Promise.all(rows.flatMap((r) => [loadLib(r.Z), loadRr(r.Z, r.A)])).then(() => console.log(JSON.stringify(got)));",
    ])
    js = tmp_path / "probe.js"
    js.write_text(code, encoding="utf-8")
    got = json.loads(subprocess.run([node, str(js), str(DATA / "index.json")], capture_output=True, text=True,
                                    encoding="utf-8", check=True).stdout)
    want = {f"data/lib/{Z}.json" for Z in _lib_files()} | {f"data/rr/{Z}/{A}.json" for Z, A in _rr_files()}
    assert set(got) == want      # every existing file is still fetched, and nothing else
    assert len(got) == len(want)  # each once (cached)
