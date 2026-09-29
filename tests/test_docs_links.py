"""Every relative link in the docs resolves.

A release ships these files. A dead link in a data card or a model card is the kind of thing
nobody sees until someone else follows it, and the four this caught on its first run were all
introduced the same afternoon by writing `results/x.md` in PLAN.md, which lives at the repo
root, where the correct form is `docs/results/x.md`. mkdocs --strict does not cover PLAN.md or
README.md, and it does not run in the default test suite.
"""
from __future__ import annotations

import pathlib
import re

REPO = pathlib.Path(__file__).resolve().parents[1]
LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")


def _targets():
    files = sorted(REPO.glob("docs/**/*.md")) + [REPO / "README.md", REPO / "PLAN.md"]
    for md in files:
        if not md.exists():
            continue
        for m in LINK.finditer(md.read_text(errors="ignore")):
            target = m.group(1).split("#")[0]          # strip anchors; we check the file only
            if not target or target.startswith(("http://", "https://", "mailto:", "<")):
                continue
            yield md, target


def test_relative_doc_links_resolve():
    broken = [
        f"{md.relative_to(REPO)} -> {target}"
        for md, target in _targets()
        if not (md.parent / target).exists() and not (REPO / target).exists()
    ]
    assert not broken, "broken relative links:\n  " + "\n  ".join(broken)


def test_the_check_sees_a_useful_number_of_links():
    """Guard against the glob quietly matching nothing and the test passing on an empty set.
    The public tree ships the data and model cards but not docs/results/, so far fewer links."""
    lab = any((REPO / "docs" / "results").glob("*.md"))
    assert sum(1 for _ in _targets()) > (100 if lab else 0)
