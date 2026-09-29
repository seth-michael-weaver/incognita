"""Prospective registry: one append-only hash chain over every frozen prediction set.

    python -m incognita.bench.registry verify            # re-hash every registry, every entry and every chain link
    python -m incognita.bench.registry append DIR --witness "..."   # add a new frozen registry as the next link

Each registry directory is frozen on its own: a MANIFEST (sha256 of each file) and MANIFEST.sha256 (the hash that is
timestamped). The chain (`docs/registry/CHAIN.jsonl`) adds ordering: link n stores the hash of link n-1, the registry's
manifest hash, the root of its per-row entry hashes and the evidence of when it existed (OpenTimestamps proofs, signed
tags, public posts). Changing any frozen byte, or reordering or dropping a link, breaks `verify`.

What the chain does NOT prove by itself: time. A link is only as early as the oldest independent witness of its hash
(an OpenTimestamps Bitcoin attestation, or a public post). The chain head must itself be witnessed after every append.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parent.parent.parent
REG = REPO / 'docs' / 'registry'
CHAIN = REG / 'CHAIN.jsonl'


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def canon(d: dict) -> bytes:
    return json.dumps(d, sort_keys=True, separators=(',', ':')).encode()


def manifest_check(d: Path) -> tuple[str, str, list[str]]:
    """-> (manifest file name, sha256 of that file = the timestamped hash, [files that fail])."""
    if (d / 'MANIFEST').exists():                  # v1 layout: MANIFEST lists files, MANIFEST.sha256 = sha256(MANIFEST)
        man = d / 'MANIFEST'
    else:                                           # v0 layout: MANIFEST.sha256 lists files and is itself stamped
        man = d / 'MANIFEST.sha256'
    bad = []
    for line in man.read_text().splitlines():
        if not line.strip():
            continue
        h, name = line.split(None, 1)
        p = d / name.strip()
        if not p.exists() or sha(p.read_bytes()) != h:
            bad.append(name.strip())
    return man.name, sha(man.read_bytes()), bad


def entries_root(d: Path):
    """sha256 over the per-row entry hashes (file order), after re-deriving each one from its row."""
    p = d / 'predictions.csv'
    if not p.exists():
        return None, 0, 0
    df = pd.read_csv(p, keep_default_na=False)
    wrong = 0
    for r in df.to_dict('records'):
        h = r.pop('entry_hash')
        if not any(hashlib.sha256(json.dumps(v, sort_keys=True).encode()).hexdigest() == h for v in _variants(r)):
            wrong += 1
    return sha('\n'.join(df.entry_hash).encode()), len(df), wrong


def _variants(r):
    """The row as read, then with integral floats written as ints: a builder may have hashed 5 where the CSV
    column (float because another row holds 14.5) now reads 5.0. Same number, two JSON spellings."""
    yield r
    keys = [k for k, v in r.items() if isinstance(v, float) and v.is_integer()]
    for m in range(1, 2 ** len(keys)):
        yield {**r, **{k: int(r[k]) for i, k in enumerate(keys) if m >> i & 1}}


def link_hash(link: dict) -> str:
    return sha(canon({k: v for k, v in link.items() if k != 'link_sha256'}))


def read_chain():
    return [json.loads(l) for l in CHAIN.read_text().splitlines() if l.strip()] if CHAIN.exists() else []


def verify(argv=None) -> int:
    chain, prev, fail = read_chain(), None, 0
    for L in chain:
        d = REG / L['registry_id']
        if not d.is_dir():  # a registry withheld from this distribution: its link still has to chain
            ok = {'prev link': L['prev_link_sha256'] == prev, 'link hash': link_hash(L) == L['link_sha256']}
            fail += not all(ok.values())
            print(f"link {L['seq']} {L['registry_id']}: " + ', '.join(f"{k} {'OK' if v else 'FAIL'}" for k, v in ok.items())
                  + '  (registry files not distributed here: manifest not checked)')
            prev = L['link_sha256']
            continue
        mname, mh, bad = manifest_check(d)
        root, n, wrong = entries_root(d)
        known = set(L.get('known_manifest_exceptions', {}))
        ok = {
            'prev link': L['prev_link_sha256'] == prev,
            'link hash': link_hash(L) == L['link_sha256'],
            'manifest hash': mh == L['manifest_sha256'],
            'files vs manifest': set(bad) <= known,
            'entries root': root == L['entries_root_sha256'] and n == L['n_entries'] and wrong == 0,
        }
        fail += not all(ok.values())
        print(f"link {L['seq']} {L['registry_id']}: " + ', '.join(f"{k} {'OK' if v else 'FAIL'}" for k, v in ok.items())
              + (f"  (documented exceptions: {sorted(set(bad) & known)})" if set(bad) & known else ''))
        prev = L['link_sha256']
    print(f'chain head {prev}' if chain else 'empty chain')
    return 1 if fail else 0


def append(a) -> int:
    chain = read_chain()
    d = (REG / a.dir) if not Path(a.dir).is_absolute() else Path(a.dir)
    mname, mh, bad = manifest_check(d)
    exc = json.loads(a.exceptions) if a.exceptions else {}
    if set(bad) - set(exc):
        print(f'{d}: files do not match the manifest: {sorted(set(bad) - set(exc))}', file=sys.stderr); return 1
    root, n, wrong = entries_root(d)
    if wrong:
        print(f'{d}: {wrong} rows do not match their entry_hash', file=sys.stderr); return 1
    L = {'seq': len(chain) + 1, 'registry_id': d.name, 'freeze_date': a.freeze_date, 'manifest_file': mname,
         'manifest_sha256': mh, 'n_entries': n, 'entries_root_sha256': root,
         'witnesses': a.witness or [], 'notes': a.note or [], 'known_manifest_exceptions': exc,
         'appended': a.appended, 'prev_link_sha256': chain[-1]['link_sha256'] if chain else None}
    L['link_sha256'] = link_hash(L)
    with CHAIN.open('a') as f:
        f.write(json.dumps(L, sort_keys=True) + '\n')
    print(f"link {L['seq']} {d.name} -> head {L['link_sha256']}")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest='cmd', required=True)
    sp.add_parser('verify')
    p = sp.add_parser('append')
    p.add_argument('dir'); p.add_argument('--freeze-date', required=True); p.add_argument('--appended', required=True)
    p.add_argument('--witness', action='append', help='evidence of existence time (repeatable)')
    p.add_argument('--note', action='append', help='caveat recorded in the link (repeatable)')
    p.add_argument('--exceptions', help='JSON {file: reason} for files documented as changed after hashing')
    a = ap.parse_args(argv)
    sys.exit(verify() if a.cmd == 'verify' else append(a))


if __name__ == '__main__':
    main()
