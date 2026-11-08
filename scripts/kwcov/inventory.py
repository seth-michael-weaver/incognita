#!/usr/bin/env python3
"""KWCOV: TALYS-2.25 keyword inventory -> docs/hf/keyword_coverage.csv.

Not a TALYS routine. Reads the stock TALYS source (master keyword list in checkkeyword.f90, the keyword
loops of input_*.f90, getvalues.f90 classes) and a `USER INPUT FILE + DEFAULTS` echo (talys.out of a
`reaction n` run), then classifies each keyword against this repository's engine:

  * Options keyword (`defaults._OPTION_KEYWORDS`) or Params keyword (`defaults.PARAM_SPECS`): READ.
    Honoured when the Fortran variable it sets is read by engine code outside the input layer.
  * `defaults.UNPORTED` (refused at run time when set): READ_ONLY_DEFAULT.
  * `fitlib._SKIP` (parsed, dropped): IGNORED.
  * output / path / plumbing keywords: NA (the observables they gate are in OBSERVABLE_COVERAGE).
  * hand-checked entries in MANUAL (kwcov_manual.py) override the automatic class.

The automatic SUPPORTED means "read and reaches physics code" -- `evidence` says whether a test in
tests/hf names the keyword (`test:<file>`) or only the grep found it (`grep`). Batches upgrade rows
to `verified` as they add stock-TALYS comparisons.

usage (WSL, engine venv for torch):
    python scripts/kwcov/inventory.py --talys ~/opt/talys-src --echo ~/kwcov/echo/talys.out
"""
from __future__ import annotations

import argparse
import csv
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from kwcov_manual import MANUAL, NA_PREFIXES, NA_WORDS  # noqa: E402

CLASS_TYPE = {
    0: "per-nucleus", 1: "per-nucleus", 2: "per-nucleus", 3: "per-nucleus-barrier", 4: "per-nucleus-barrier",
    5: "per-nucleus-radiation", 6: "per-particle", 7: "per-particle", 8: "per-particle", 9: "value",
    10: "per-element-file", 11: "per-nucleus-file", 12: "per-nucleus-particle-file", 13: "value+nucleus",
    14: "value+nucleus", 15: "value+nucleus", 16: "per-particle-nucleus",
}
EXCLUDE = {"input/defaults.py", "input/fitlib.py", "talys_defaults_echo.py"}
#: files that carry a keyword without computing with it (cache keys, override plumbing, legacy toy, output dumps)
PLUMBING = {"stagedisk.py", "density/overrides.py", "eadj.py", "tmc.py", "capture.py", "ingredients.py",
            "record/caches.py", "record/codec.py", "record/store.py"}


def master_list(src: Path) -> list[str]:
    t = (src / "source/checkkeyword.f90").read_text()
    m = re.search(r"data \(keyword\(i\), i = 1, numkey\) /(.*?)/\s*\n", t, re.S)
    kws = re.findall(r"'([^']*)'", m.group(1))
    return [k for k in kws if k.strip()]


def keyword_blocks(src: Path) -> dict[str, tuple[str, int, str]]:
    """keyword -> (input file, line, block text) from `if (key == '...')` in input_*.f90."""
    out: dict[str, tuple[str, int, str]] = {}
    for f in sorted((src / "source").glob("input_*.f90")):
        lines = f.read_text(errors="replace").splitlines()
        starts = [i for i, s in enumerate(lines) if re.search(r"key\s*==\s*'", s)]
        for j, i in enumerate(starts):
            end = starts[j + 1] if j + 1 < len(starts) else min(len(lines), i + 40)
            block = "\n".join(lines[i:end])
            for k in re.findall(r"key\s*==\s*'([^']+)'", lines[i]):
                out.setdefault(k, (f.name, i + 1, block))
    return out


def ktype(kw: str, block: str) -> str:
    m = re.search(r"getvalues\((\d+)", block) or re.search(r"class\s*=\s*(\d+)", block)
    if m:
        t = CLASS_TYPE.get(int(m.group(1)), f"class{m.group(1)}")
        if re.search(r"word\(3\)\s*==\s*' '", block):  # `key value` global form, else the per-nucleus form
            t = ("flag" if re.search(r"ch\s*==\s*'[yn]'", block) else "value") + " | " + t
        return t
    if re.search(r"ch\s*==\s*'[yn]'", block):
        return "flag"
    return "value"


def parse_echo(path: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    if not path or not path.is_file():
        return out
    on = False
    for line in path.read_text(errors="replace").splitlines():
        if "USER INPUT FILE + DEFAULTS" in line:
            on = True
            continue
        if on and "BASIC REACTION PARAMETERS" in line:
            break
        if not on or not line.strip() or line.strip().startswith("#") or line.startswith(" Keyword"):
            continue
        w = line.split()
        k = w[0].lower()
        if k in ("maxlevelsbin", "ejectiles"):
            val = " ".join(w[1:3]) if k == "maxlevelsbin" else " ".join(w[1:8])
            out.setdefault(k, val if k == "ejectiles" else w[2])
            continue
        if len(w) >= 3:
            out.setdefault(k, w[1])
        elif len(w) == 2:
            out.setdefault(k, "")
    return out


def code_index() -> list[tuple[str, str]]:
    files = []
    base = ROOT / "physics/hf"
    for p in base.rglob("*"):
        if p.suffix not in (".py", ".c", ".h") or not p.is_file():
            continue
        rel = p.relative_to(base).as_posix()
        if rel in EXCLUDE:
            continue
        files.append((rel, p.read_text(errors="replace")))
    return files


def test_index() -> list[tuple[str, str]]:
    return [(p.name, p.read_text(errors="replace")) for p in (ROOT / "tests/hf").glob("*.py")]


def users(var: str, files) -> list[str]:
    pat = re.compile(r"(?<![A-Za-z0-9_])" + re.escape(var) + r"(?![A-Za-z0-9_])")
    return sorted({rel for rel, txt in files if pat.search(txt)})


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--talys", default=os.path.expanduser("~/opt/talys-src"))
    ap.add_argument("--echo", default=os.path.expanduser("~/kwcov/echo/talys.out"))
    ap.add_argument("--out", default=str(ROOT / "docs/hf/keyword_coverage.csv"))
    a = ap.parse_args()
    src = Path(a.talys)

    from physics.hf.input import defaults as D
    from physics.hf.input import fitlib as F

    kws = master_list(src)
    blocks = keyword_blocks(src)
    echo = parse_echo(Path(a.echo))
    code, tests = code_index(), test_index()
    unported = {key: msg.split(":")[0] for key, _f, msg in D.UNPORTED}
    rows = []
    for kw in kws:
        f, ln, block = blocks.get(kw, ("", 0, ""))
        typ = ktype(kw, block) if block else "value"
        default = echo.get(kw, "")
        spec = D.PARAM_SPECS.get(kw)
        if not default and spec is not None:
            default = str(spec.default)
        opt = D._OPTION_KEYWORDS.get(kw)
        status, where, note, evidence = "MISSING", "", "", ""
        var = opt[1] if opt else (spec.variable if spec else "")
        if opt or spec:
            where = "input/defaults.py " + ("Options." + opt[1] if opt else "Params." + spec.variable)
            u = [x for x in users(var, code) if x not in PLUMBING]
            if var in unported:
                status, note = "READ_ONLY_DEFAULT", "refused when set (defaults.UNPORTED): " + unported[var]
            elif u:
                status = "SUPPORTED"
                where += " -> " + ", ".join(u[:4]) + (f" (+{len(u) - 4})" if len(u) > 4 else "")
            else:
                status, note = "IGNORED", "parsed into Options/Params but no engine code reads " + var
            t = [n for n, txt in tests if re.search(r"['\"\s]" + re.escape(kw) + r"['\"\s]", txt)]
            if status == "SUPPORTED" and opt and ("per-" in typ or "nucleus" in typ):
                note = "global form only: the per-nucleus/per-particle form is refused (defaults.default_options)"
            evidence = ("test:" + ",".join(t[:3])) if (t and status == "SUPPORTED") else ("grep" if status == "SUPPORTED" else "")
        if kw in F._SKIP:
            status, note = "IGNORED", "fitlib skips the line: " + F._SKIP[kw]
        if kw in NA_WORDS or kw.startswith(NA_PREFIXES):
            if status in ("MISSING", "IGNORED"):
                status, note = "NA", "output/path/plumbing switch; observable tracked in OBSERVABLE_COVERAGE"
        if kw in MANUAL:
            m = MANUAL[kw]
            status = m[0]
            where = m[1] or where
            note = m[2]
            evidence = m[3] if len(m) > 3 else (evidence or "manual")
        rows.append(dict(keyword=kw, group=f.replace(".f90", "") if f else "", talys_line=f"{f}:{ln}" if f else "",
                         type=typ, default=default, status=status, where=where, evidence=evidence, notes=note))
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    with open(a.out, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    from collections import Counter
    c = Counter(r["status"] for r in rows)
    print(len(rows), dict(sorted(c.items())))


if __name__ == "__main__":
    main()
