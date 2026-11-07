"""Site translations (docs/walkthrough/js/i18n): every key a page uses exists in each language's files that the page loads.

Added in the code bug hunt round 2 (2026-11-07) after round 1 found keys missing in every language. Pure text checks: no
browser, no node.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
SITE = REPO / "docs" / "walkthrough"
LANGS = ["ar", "da", "de", "es", "fr", "hi", "it", "ja", "ko", "nl", "pt", "ru", "zh"]

_KEY = re.compile(r'(?:^|[{,])\s*"?([A-Za-z][A-Za-z0-9_]*)"?\s*:\s*["`]', re.M)
_USE = re.compile(r'(?:\bT|WT\.ui)\(\s*"([A-Za-z0-9_]+)"\s*,')


def _defined(lang: str, files: list[str]) -> set[str]:
    keys: set[str] = set()
    for f in files:
        p = SITE / "js" / "i18n" / f"{lang}-{f}.js"
        if p.exists():
            keys |= set(_KEY.findall(p.read_text(encoding="utf-8")))
    return keys


@pytest.mark.parametrize("page", ["data.html", "pipeline.html", "instructors.html", "scoreboard.html"])
def test_every_page_key_is_translated(page):
    """Every key a page uses (data-i18n* in the page, T(...) / WT.ui(...) in its scripts, nav.js included) exists in each
    language's files that the page loads. Round 1 found the energy-band strip, the below-1-keV texts, the whole pipeline
    page, the 'More topics' link off the main pages and in_min missing."""
    html = (SITE / page).read_text(encoding="utf-8")
    files = re.findall(r'"([a-z]+)"', re.search(r"WT\.load\(\[([^\]]*)\]", html).group(1))
    used = set(re.findall(r'data-i18n(?:-aria|-ph)?="([^"]+)"', html))
    for s in re.findall(r'<script src="(js/[^"?]+)', html):
        if "/i18n" not in s:
            src = (SITE / s).read_text(encoding="utf-8")
            src = "\n".join(ln for ln in src.splitlines() if not ln.lstrip().startswith("//"))   # nav.js: the Pipeline link is commented out
            used |= set(_USE.findall(src))
    miss = {lang: sorted(used - _defined(lang, files)) for lang in LANGS}
    assert not {k: v for k, v in miss.items() if v}, miss


def test_pipeline_page_applies_its_translations():
    """pipeline.js never applied the static data-i18n text of pipeline.html (kicker, heading, 'What we have' counts) nor
    a translated title, so those stayed English in every language."""
    src = (SITE / "js" / "pipeline.js").read_text(encoding="utf-8")
    assert "[data-i18n]" in src and "pl_title" in src
