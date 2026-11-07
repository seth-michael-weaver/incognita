"""scripts/talysworld/server.py: /site/ requests stay inside docs/walkthrough (not a sibling with the same prefix)."""
import importlib.util
import os
from pathlib import Path

_P = Path(__file__).resolve().parents[1] / "scripts" / "talysworld" / "server.py"
_spec = importlib.util.spec_from_file_location("tw_server", _P)
S = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(S)


def test_site_path_stays_inside():
    assert S.inside(S.SITE, "js/data.js") == os.path.join(S.SITE, "js", "data.js")
    assert S.inside(S.SITE, "../walkthrough_private/x.json") is None      # prefix sibling: was served
    assert S.inside(S.SITE, "../../README.md") is None
    assert S.inside(S.SITE, "") is None
