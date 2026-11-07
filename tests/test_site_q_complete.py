"""docs/walkthrough/data/q.json (scripts/build_site_q.py) covers every nuclide of data/index.json (build_site_data.py)."""
import json
from pathlib import Path

D = Path(__file__).resolve().parents[1] / "docs" / "walkthrough" / "data"


def test_every_index_nuclide_has_q_values():
    idx = json.loads((D / "index.json").read_text())
    q = json.loads((D / "q.json").read_text())["q"]
    want = {f"{r[0]}-{r[1]}" for r in idx["rows"] if r[1] > 0}
    assert not sorted(want - set(q)), "q.json is stale: rerun scripts/build_site_q.py after build_site_data.py"
