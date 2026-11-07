"""SWNAMES6: the launchers' engine switch names (scripts/talysworld/engine_env.py) cannot drift from the engine.

* every INCOGNITA_* name of engine_env.SWITCHES is read by this repository's engine (a string constant in physics/hf
  Python code outside docstrings, or a getenv("...") in its C sources);
* every NUCLIDO_* name a launcher of this repository mentions (scripts/, harness/, incognita/, tests/hf/*_run.py), and
  every one the library's runner bundle sets when it is present (~/libv02/inputs/code), is in engine_env.SWITCHES;
* flavour detection, and the os.environ mirror (set, delete, clear/update as the bundle does per item, subprocess
  inheritance), in a child process.
"""
from __future__ import annotations

import ast
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
TW = ROOT / "scripts" / "talysworld"
sys.path.insert(0, str(TW))
import engine_env as EE  # noqa: E402

NAME = re.compile(r"\bNUCLIDO_[A-Z0-9_]*[A-Z0-9]\b")
BUNDLE = Path(os.environ.get("TW_INPUTS", Path.home() / "libv02" / "inputs")) / "code"


def _docstring_ids(tree):
    ids = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and node.body:
            first = node.body[0]
            if isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant):
                ids.add(id(first.value))
    return ids


def engine_reads() -> set[str]:
    """Every INCOGNITA_* string constant of physics/hf code (not docstrings) and every getenv'd name of its C code."""
    names = set()
    for p in (ROOT / "physics" / "hf").rglob("*.py"):
        tree = ast.parse(p.read_text(encoding="utf-8", errors="replace"))
        skip = _docstring_ids(tree)
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str) and id(node) not in skip:
                names.update(re.findall(r"\bINCOGNITA_[A-Z0-9_]+", node.value))
    for p in (ROOT / "physics" / "hf").rglob("*.[ch]"):
        names.update(re.findall(r'getenv\("(INCOGNITA_[A-Z0-9_]+)"\)', p.read_text(encoding="utf-8", errors="replace")))
    return names


def launcher_names(paths) -> dict[str, set[str]]:
    out: dict[str, set[str]] = {}
    for base in paths:
        files = [base] if base.is_file() else [*base.rglob("*.py"), *base.rglob("*.sh"), *base.rglob("*.ps1")]
        for p in files:
            if p.name == "engine_env.py" or "__pycache__" in p.parts:
                continue
            for n in NAME.findall(p.read_text(encoding="utf-8", errors="replace")):
                out.setdefault(n, set()).add(str(p))
    return out


def test_every_mapped_name_is_read_by_the_engine():
    reads = engine_reads()
    missing = sorted(v for v in EE.SWITCHES.values() if v not in reads)
    assert not missing, f"engine_env.SWITCHES maps to names physics/hf does not read: {missing}"


def test_table_is_one_to_one_and_prefixed():
    assert len(set(EE.SWITCHES.values())) == len(EE.SWITCHES)
    for k, v in EE.SWITCHES.items():
        assert k.startswith(EE.PROD_PREFIX) and v.startswith(EE.REPO_PREFIX), (k, v)
        assert k[len(EE.PROD_PREFIX):] == v[len(EE.REPO_PREFIX):], (k, v)   # renamed prefix only, today


def test_every_launcher_name_is_mapped():
    found = launcher_names([ROOT / "scripts", ROOT / "harness", ROOT / "incognita", *sorted((ROOT / "tests").rglob("*_run.py"))])
    unmapped = {n: sorted(f) for n, f in found.items() if n not in EE.SWITCHES}
    assert not unmapped, f"NUCLIDO_* names used by launchers but missing from engine_env.SWITCHES: {unmapped}"


@pytest.mark.skipif(not BUNDLE.is_dir(), reason="library runner bundle (~/libv02/inputs/code) not present")
def test_every_bundle_name_is_mapped():
    found = launcher_names([BUNDLE])
    unmapped = sorted(n for n in found if n not in EE.SWITCHES)
    assert not unmapped, f"the runner bundle sets NUCLIDO_* names missing from engine_env.SWITCHES: {unmapped}"


def test_flavour(tmp_path, monkeypatch):
    monkeypatch.delenv("TW_ENG_FLAVOUR", raising=False)
    assert EE.flavour(str(ROOT)) == "repo"
    prod = tmp_path / "prod"
    (prod / "physics/hf/structure").mkdir(parents=True)
    (prod / "physics/hf/structure/ggdeadend.py").write_text('import os\nX = os.environ.get("NUCLIDO_GGDEADEND")\n')
    assert EE.flavour(str(prod)) == "production"
    with pytest.raises(RuntimeError):
        EE.flavour(str(tmp_path / "nothing"))
    monkeypatch.setenv("TW_ENG_FLAVOUR", "production")
    assert EE.flavour(str(ROOT)) == "production"


_CHILD = r"""
import json, os, subprocess, sys
sys.path.insert(0, sys.argv[1]); import engine_env as EE
out = {}
os.environ["NUCLIDO_GGDEADEND"] = "1"                       # set before install: mirrored by install
EE.install(sys.argv[2], skip=("NUCLIDO_CC_CACHE",))
os.environ.update(NUCLIDO_DWBAUNIT="1", NUCLIDO_CC_CACHE="/x", NUCLIDO_ISOE2="e")
out["after_set"] = {k: os.environ.get(k) for k in ("INCOGNITA_GGDEADEND", "INCOGNITA_DWBAUNIT", "INCOGNITA_CC_CACHE", "INCOGNITA_ISOE2")}
base = dict(os.environ)
os.environ.pop("NUCLIDO_ISOE2")
out["after_pop"] = os.environ.get("INCOGNITA_ISOE2")
os.environ.clear(); os.environ.update(base)                 # the bundle's per-item reset
out["after_reset"] = os.environ.get("INCOGNITA_ISOE2")
out["child"] = subprocess.run([sys.executable, "-c", "import os; print(os.environ.get('INCOGNITA_DWBAUNIT'))"],
                              capture_output=True, text=True).stdout.strip()
EE.install(sys.argv[2])                                     # idempotent; re-install without skip
os.environ["NUCLIDO_CC_CACHE"] = "/y"
out["cc_noskip"] = os.environ.get("INCOGNITA_CC_CACHE")
print(json.dumps(out))
"""


def test_mirror_in_child_process():
    env = {k: v for k, v in os.environ.items() if not k.startswith(("NUCLIDO_", "INCOGNITA_", "TW_ENG_FLAVOUR"))}
    p = subprocess.run([sys.executable, "-c", _CHILD, str(TW), str(ROOT)], capture_output=True, text=True, env=env, timeout=120)
    assert p.returncode == 0, p.stderr
    out = json.loads(p.stdout.strip().splitlines()[-1])
    assert out["after_set"] == {"INCOGNITA_GGDEADEND": "1", "INCOGNITA_DWBAUNIT": "1", "INCOGNITA_CC_CACHE": None,
                                "INCOGNITA_ISOE2": "e"}
    assert out["after_pop"] is None and out["after_reset"] == "e"
    assert out["child"] == "1"
    assert out["cc_noskip"] == "/y"


def test_production_flavour_leaves_environ_alone(tmp_path):
    prod = tmp_path / "prod"
    (prod / "physics/hf/structure").mkdir(parents=True)
    (prod / "physics/hf/structure/ggdeadend.py").write_text('X = "NUCLIDO_GGDEADEND"\n')
    code = ("import os, sys; sys.path.insert(0, sys.argv[1]); import engine_env as EE; t = type(os.environ); "
            "f = EE.install(sys.argv[2]); os.environ['NUCLIDO_DWBAUNIT'] = '1'; "
            "print(f, type(os.environ) is t, os.environ.get('INCOGNITA_DWBAUNIT'))")
    env = {k: v for k, v in os.environ.items() if not k.startswith(("NUCLIDO_", "INCOGNITA_", "TW_ENG_FLAVOUR"))}
    p = subprocess.run([sys.executable, "-c", code, str(TW), str(prod)], capture_output=True, text=True, env=env, timeout=120)
    assert p.stdout.split() == ["production", "True", "None"], p.stderr
