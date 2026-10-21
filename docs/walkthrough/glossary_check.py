#!/usr/bin/env python3
"""Glossary coverage check: list technical-looking words in the visible prose that no glossary alias covers.

    python3 glossary_check.py          # report gaps (exit 1 if any)

Prose = chapter titles, leads and step text (controls, formulas, "In the code" asides removed), plus the hero and coda
of index.html. Candidates: words the authors emphasised (<b>, <i>, plain <em>), names introduced by "called X",
capitalised words mid-sentence, hyphenated compounds, symbols with Greek letters or subscripts, and (n,x) labels.
A candidate counts as covered when a glossary alias matches the same text (same rules as kit.js). IGNORE lists words
that are deliberately left unmarked (plain English, variables explained in place, picture vocabulary)."""
import html
import re
import sys
from pathlib import Path

D = Path(__file__).resolve().parent
ORDER = ["intro", "structure", "omp", "direct", "preeq", "compound", "decay", "gamma", "cascade", "fission", "resonance", "measure", "layers"]

IGNORE = {
    # single-letter variables and symbols the text defines on the spot
    *"a b k l r x y i n p d E J T W S K A N Z R U".split(), "J′", "xi", "Tb", "Tc", "ρb", "ρc", "Σc", "TA", "TB", "Tfis", "ΔJ", "ΔE",
    "σ", "γ", "α", "ε", "θ", "μ", "ħ", "δ", "e", "n′", "2n", "3n", "En−1", "Eγ2l+1", "E3/2", "2J+1", "(2J+1)", "x²", "β²", "Sp",
    # people and places named in passing; everyday or picture words
    "Niels Bohr", "Bohr's", "Bohr", "American", "Physicists", "Press", "Drag", "Raise", "Lower", "Add", "Set", "Pick", "Roll",
    "Collide", "Deform", "Equal widths", "Fire", "Step", "Draw", "Heat", "Watch", "Compare", "Back", "Now", "On", "Each",
    "In", "The", "This", "That", "These", "Those", "Below", "Above", "Near", "At", "From", "Here", "Higher", "Only", "With",
    "So", "Both", "Its", "It", "A", "An", "One", "Two", "Three", "Then", "Where", "When", "Why", "How", "Look", "Move",
    "Inside", "Not", "Some", "Most", "Every", "Grey", "Blue", "Orange", "Solid", "Hollow", "Wide", "Within", "Because",
    "Truly", "Real", "Neutrons", "Protons", "Photons", "Emitted", "Evaporated", "Fast", "Slow", "Capture", "Production",
    "Mixing", "Hotter", "Sharing", "Extra", "Small", "Spin", "Iron", "Uranium", "Uranium-238", "Uranium-239", "iron-56",
    "uranium-238", "uranium-239", "Chapter", "Chapters", "In the code", "INCOGNITA", "Scroll", "Fire",
    "football-shaped", "football-to-disc", "pear-shaped", "head-on", "off-centre", "short-range", "high-energy", "low-energy",
    "long-lived", "high-spin", "low-spin", "nucleon–nucleon", "one-push", "one-step", "medium-mass", "two-", "1-MeV",
    "bell-curve", "re-emits", "real part", "imaginary part", "second", "flux", "inwards",
    "free", "rung", "rungs", "door", "doors", "shelf", "shelves", "ladder", "drawers", "tray", "pile", "piles", "gates",
    "crowd", "trees", "tree", "canopy", "forest", "ghost", "plank", "terrain", "hillside", "needles", "window",
    "Fingerprints", "hump", "tail", "shelf", "rim", "well", "hill", "wave", "crests", "rings", "streams", "knocks",
    "fork", "chain", "stage", "stages", "magnification", "beam", "foil", "detectors", "petal", "disc", "discs", "bracket",
    "padlocked", "buckets", "knobs", "ledger", "marker", "squares", "tokens", "dots", "ball", "balls", "arcs", "hand",
    "meter", "mark", "neck", "Collisions", "collision", "collisions", "slope", "lit gap", "gap", "gaps", "bins",
    "Tγ", "E3", "Eγ³", "2σ²", "En", "k b", "Σy", "width", "because it", "by the", "options inside", "average of products",
    "product of averages", "forgotten how it was formed", "near-coincidences", "best-known", "swing distance", "Niels Bohr's",
    "ripple", "ripples", "phonons", "pickup", "knockout", "spin-flip", "upbend", "scissors", "sum rule",
    "measured-structure", "nucleus-by-nucleus", "R072w", "R073",
}


def strip(s):
    s = re.sub(r'<div class="(ctl|btns|formula|aside)">.*?</div>', "", s, flags=re.S)
    return s


def blocks():
    """(where, raw_html) for every prose block."""
    out = []
    for cid in ORDER:
        src = (D / "js" / "ch" / f"{cid}.js").read_text()
        for k in ("title", "lead"):
            m = re.search(k + r':\s*"((?:[^"\\]|\\.)*)"', src)
            if m and m.group(1):
                out.append((f"{cid}:{k}", m.group(1)))
        m = re.search(r"html:\s*`(.*?)`", src, re.S)
        if m:
            for i, st in enumerate(re.split(r'<div class="step">', strip(m.group(1)))[1:]):
                st = re.sub(r"<h3>.*?</h3>", "", st, flags=re.S)
                out.append((f"{cid}:step{i}", st))
    page = (D / "index.html").read_text()
    for name, a, b in (("hero", '<section class="hero', "</section>"), ("coda", '<section class="coda"', "</section>")):
        i = page.index(a)
        seg = page[i:page.index(b, i)]
        seg = re.sub(r"<(h1|h2|th|code)[^>]*>.*?</\1>", "", seg, flags=re.S)
        seg = re.sub(r'<div class="(kicker|scrollcue)">.*?</div>', "", seg, flags=re.S)
        out.append((name, seg))
    return out


def text_of(raw):
    return html.unescape(re.sub(r"<[^>]+>", "", raw))


def aliases():
    src = (D / "js" / "glossary.js").read_text()
    out = []
    for m in re.finditer(r"aliases:\s*\[(.*?)\]", src, re.S):
        out += [a.replace('\\"', '"') for a in re.findall(r'"((?:[^"\\]|\\.)*)"', m.group(1))]
    return out


def plural(a):
    if re.search(r"(s|x|ch|sh)$", a):
        return a + "es"
    if re.search(r"[^aeiou]y$", a):
        return a[:-1] + "ies"
    return a + "s"


def matcher(als):
    ci, cs = set(), set()
    for a in als:
        if re.fullmatch(r"[A-Za-z][a-z' \-–]*", a):
            ci |= {a.lower(), plural(a.lower())}
        else:
            cs.add(a)
    mk = lambda xs, fl: re.compile(r"(?<![\w\-])(?:" + "|".join(re.escape(x).replace(r"\ ", r"\s+") for x in sorted(xs, key=len, reverse=True)) + r")(?![\w\-])", fl)
    return mk(ci, re.I), mk(cs, 0)


def covered_spans(text, regs):
    spans = []
    for r in regs:
        spans += [(m.start(), m.end()) for m in r.finditer(text)]
    return spans


def candidates(raw):
    """(phrase, start offset in text_of(raw)) pairs."""
    text = text_of(raw)
    found = []
    # emphasised words: <b>, <i>, plain <em>; locate each in the text by searching forward
    pos = 0
    for m in re.finditer(r"<(b|i|em)>(.*?)</\1>", raw, re.S):
        t = text_of(m.group(2)).strip()
        j = text.find(t, pos)
        if t and j >= 0:
            found.append((t, j))
            pos = j
    for m in re.finditer(r"(?:called|known as|named)\s+(?:the\s+|a\s+|an\s+)?([\w\-–']+(?:\s+[\w\-–']+)?)", text):
        found.append((m.group(1), m.start(1)))
    for m in re.finditer(r"(?<=[a-z,;:(] )([A-Z][\w\-–']+(?:[ \-–][A-Z][\w\-–']+)*)", text):
        found.append((m.group(1), m.start(1)))
    for m in re.finditer(r"\b[A-Za-z]+(?:-[A-Za-z0-9]+)+\b", text):
        found.append((m.group(0), m.start()))
    for m in re.finditer(r"[\w⟨]*[α-ωΑ-Ω₀-₉⟩][\w⟩]*|\(n,[^)]+\)|\b[A-Z][a-z]?[0-9]\b|\b[a-z]*[A-Z]{2,}[a-z]*\b", text):
        found.append((m.group(0), m.start()))
    return text, found


def main():
    regs = matcher(aliases())
    gaps = {}
    for where, raw in blocks():
        text, cands = candidates(raw)
        spans = covered_spans(text, regs)
        for phrase, s in cands:
            p = phrase.strip(" .,;:")
            if len(p) < 2 or p in IGNORE or p.lower() in IGNORE or re.fullmatch(r"[\d.,\s]+", p):
                continue
            e = s + len(phrase)
            if any(a < e and b > s for a, b in spans):
                continue
            gaps.setdefault(p, []).append(where)
    if not gaps:
        print("glossary coverage: no gaps")
        return 0
    print(f"{len(gaps)} technical-looking phrases with no glossary entry:")
    for p, ws in sorted(gaps.items(), key=lambda kv: (-len(kv[1]), kv[0].lower())):
        print(f"  {p!r:40s} {len(ws)}x  {', '.join(sorted(set(ws))[:4])}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
