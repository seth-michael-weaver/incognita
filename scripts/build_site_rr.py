"""INCOGNITA's own capture (and elastic/total) below the 1 keV join, from the resonance-region fill, for the explorer (data.html).

Copies the resonance-region site files (rr/<Z>/<A>.json, rr_index.json, README.md; schema in README.md) into
docs/walkthrough/data/rr/ and checks every copied file against their SHA256SUMS.txt.
Exits non-zero on any missing file or mismatch.
The published README.md has one line corrected after the copy (the file count: one per rr_index.json row, not per
explorer row; tests/test_site_flags.py checks it), so a re-copy must re-apply that. Re-run scripts/build_site_data.py
afterwards: its index.json column "rr" flags which rr files exist.

usage: python3 scripts/build_site_rr.py [SRC_DIR] [SHA256SUMS]
  SRC_DIR    the resonance-region site files (default: see SRC below)
  SHA256SUMS their checksum file (default: see SUMS below)
"""
import hashlib, os, shutil, sys
from pathlib import Path

SRC = Path(os.path.expanduser(sys.argv[1] if len(sys.argv) > 1 else "~/resfill_data/site"))
SUMS = Path(os.path.expanduser(sys.argv[2] if len(sys.argv) > 2 else "~/nucleus/research/rl/resfill/out/site/SHA256SUMS.txt"))
DST = Path(__file__).resolve().parent.parent / "docs" / "walkthrough" / "data" / "rr"


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def main():
    want = {}
    for ln in SUMS.read_text().splitlines():
        if ln.strip():
            h, rel = ln.split(None, 1)
            rel = rel.strip().lstrip("*")
            want[rel[2:] if rel.startswith("./") else rel] = h
    want.pop("SHA256SUMS.txt", None)
    # published layout: rr/<Z>/<A>.json -> data/rr/<Z>/<A>.json; rr_index.json, README.md -> data/rr/
    dst_of = lambda rel: DST / (rel[3:] if rel.startswith("rr/") else rel)
    if DST.exists():
        shutil.rmtree(DST)
    n = 0
    for rel in sorted(want):
        s, d = SRC / rel, dst_of(rel)
        if not s.is_file():
            sys.exit(f"missing in source: {rel}")
        d.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(s, d)
        n += 1
    bad = [rel for rel in sorted(want) if sha(dst_of(rel)) != want[rel]]
    if bad:
        sys.exit(f"sha256 mismatch in {len(bad)} files, e.g. {bad[:5]}")
    size = sum(p.stat().st_size for p in DST.rglob("*") if p.is_file())
    print(f"copied {n} files to {DST}, all sha256 match; {size / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
