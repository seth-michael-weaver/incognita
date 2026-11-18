#!/usr/bin/env python3
"""Regenerate the "More Nuclear Topics" drop-down list in docs/walkthrough/js/nav.js
from docs/walkthrough/topics.html (parts + chapter order) and js/topics/*.js (level + short title).
Run after adding a part or chapter to topics.html:  python3 tools/sync_topics_menu.py [--check]"""
import re, sys, pathlib, json
W = pathlib.Path(__file__).resolve().parent.parent / "docs" / "walkthrough"
html = (W / "topics.html").read_text()
meta = {}
for f in sorted((W / "js" / "topics").glob("*.js")):
    s = f.read_text()
    for m in re.finditer(r'WT\.chapter\("([a-z0-9]+)",\s*\{\s*level:\s*(\d)[^}]*?short:\s*"([^"]+)"', s, re.S):
        meta[m[1]] = (int(m[2]), m[3])
    for m in re.finditer(r'typeLesson\("([a-z0-9]+)",\s*(\d),\s*"[^"]*",\s*"([^"]+)"', s):
        meta[m[1]] = (int(m[2]), m[3])
# chapters defined without a level field (js/ch/*.js): keep the level/short already in nav.js
old = re.search(r'"topics\.html": (\[\[.*?\]\]) \};', (W / "js" / "nav.js").read_text(), re.S)
for it in (json.loads(old[1]) if old else []):
    if not it[0].startswith("#") and it[0] not in meta: meta[it[0]] = (it[1], it[2])
for f in sorted((W / "js" / "ch").glob("*.js")):
    for m in re.finditer(r'WT\.chapter\("([a-z0-9]+)",\s*\{[^}]*?short:\s*"([^"]+)"', f.read_text(), re.S):
        if m[1] not in meta: meta[m[1]] = (1, m[2])
items, missing = [], []
tok = re.compile(r'<section class="part-head" id="([a-z0-9-]+)".*?data-i18n="([a-z0-9_]+)">([^<]+)</div><h2[^>]*data-i18n="([a-z0-9_]+)">([^<]+)</h2>'
                 r'|<section class="chapter" data-ch="([a-z0-9]+)">', re.S)
for m in tok.finditer(html):
    if m[1]:
        items.append(["#" + m[1], m[2], m[3].strip(), m[4], m[5].strip()])
    else:
        ch = m[6]
        if ch not in meta: missing.append(ch); continue
        items.append([ch, meta[ch][0], meta[ch][1]])
if missing: sys.exit(f"no level/short found for chapters: {missing}")
new = '"topics.html": ' + json.dumps(items, ensure_ascii=False, separators=(",", ":")) + " };"
nav = W / "js" / "nav.js"; s = nav.read_text()
out, n = re.subn(r'"topics\.html": \[\[.*?\]\] \};', lambda _: new, s, count=1, flags=re.S)
if n != 1: sys.exit("MENUS['topics.html'] line not found in nav.js")
if "--check" in sys.argv:
    sys.exit(0 if out == s else "nav.js topics menu is out of date: run tools/sync_topics_menu.py")
nav.write_text(out); print(f"topics menu: {sum(1 for i in items if i[0].startswith('#'))} parts, {sum(1 for i in items if not i[0].startswith('#'))} chapters")
