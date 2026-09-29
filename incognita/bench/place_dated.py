"""Fetch-and-place: build the bin-average library table the dated tracks need (DATEDEXAM2).  No library value ships with the
benchmark; this regenerates it from the official files.

    uv run python -m incognita.bench.place_dated --library endfb71 --fetch DOWNLOAD_DIR --njoy PATH --out lib_endfb71.parquet
    uv run python -m incognita.bench.place_dated --library endfb71 --endf DIR_OR_ARCHIVE --njoy PATH --out lib_endfb71.parquet
    uv run python -m incognita.bench.place_dated --merge lib_*.parquet --out dated_library.parquet
    uv run python -m incognita.bench.score leaderboard --track dated --dated-library dated_library.parquet

For every nucleus of the dated rows the library carries (ground state, LISO = 0), NJOY2016 RECONR reconstructs the 0 K
pointwise cross sections (tolerance 0.1 %), and every row gets the lethargy average of its channel over the row's own
0.1 ln E bin (`incognita/bench/binavg.py`, which states the rule).  `--endf` takes a directory (searched recursively; zip
members are read too), a .tar/.tgz/.tar.gz or a .zip.  `--fetch` downloads from the URLs below (checked 2026-09; mirrors move:
if one fails, download by hand and use --endf).  Output: one parquet per library, one row per unique dated row key
(Z, A, quantity, series, energy_ev, emin_ev) with `lib:<name>` = log10 barns, plus `src:<name>` (which MT or MT sum) and
`frac:<name>` (lethargy fraction of the bin used; < 1 only on threshold rows).
"""
from __future__ import annotations

import argparse
import io
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import zipfile
from pathlib import Path
from urllib.request import Request, urlopen

import numpy as np
import pandas as pd

from incognita.bench import binavg as BA
from incognita.bench import score as S

IAEA = 'https://www-nds.iaea.org/public/download-endf/'
# key -> (leaderboard name, kind, url): 'dir' = IAEA-NDS per-material zip directory, 'file' = one archive
SOURCES = {
    'endfb70': ('ENDF/B-VII.0', 'dir', IAEA + 'ENDF-B-VII.0/n/'),
    'jendl40': ('JENDL-4.0', 'dir', IAEA + 'JENDL-4.0/n/'),
    'endfb71': ('ENDF/B-VII.1', 'dir', IAEA + 'ENDF-B-VII.1/n/'),
    'brond31': ('BROND-3.1', 'dir', IAEA + 'BROND-3.1/n/'),
    'jeff33': ('JEFF-3.3', 'file', 'https://www.oecd-nea.org/dbdata/jeff/jeff33/downloads/JEFF33-n.tgz'),
    'cendl32': ('CENDL-3.2', 'file', IAEA + 'CENDL-3.2/backup/cendl-3-2_n.sublib.zip'),
    'irdff2': ('IRDFF-II', 'dir', IAEA + 'IRDFF-II/n/'),
    'jendl5': ('JENDL-5', 'file', 'https://wwwndc.jaea.go.jp/ftpnd/ftp/JENDL/jendl5-n.tar.gz'),
    'fendl32': ('FENDL-3.2', 'dir', IAEA + 'FENDL-3.2c/n/'),
    'endfb81': ('ENDF/B-VIII.1', 'file', 'https://www.nndc.bnl.gov/endf-releases/releases/B-VIII.1/ENDF-B-VIII.1.tar.gz'),
    'jeff40': ('JEFF-4.0', 'dir', IAEA + 'JEFF-4.0/n/'),
    'tendl2025': ('TENDL-2025', 'dir', IAEA + 'TENDL-2025/n/'),
    **{f'tendl{y}': (f'TENDL-{y}', 'file', f'https://tendl.imperial.ac.uk/tendl_{y}/tar_files/TENDL-n.tgz')
       for y in (2015, 2017, 2019, 2021, 2023)},
}
SYM = ('n H He Li Be B C N O F Ne Na Mg Al Si P S Cl Ar K Ca Sc Ti V Cr Mn Fe Co Ni Cu Zn Ga Ge As Se Br Kr Rb Sr Y Zr Nb Mo '
       'Tc Ru Rh Pd Ag Cd In Sn Sb Te I Xe Cs Ba La Ce Pr Nd Pm Sm Eu Gd Tb Dy Ho Er Tm Yb Lu Hf Ta W Re Os Ir Pt Au Hg Tl Pb '
       'Bi Po At Rn Fr Ra Ac Th Pa U Np Pu Am Cm Bk Cf Es Fm').split()
KEY = ['Z', 'A', 'quantity', 'series', 'energy_ev', 'emin_ev']


def _get(url: str, dest: Path) -> Path:
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0 (incognita.bench.place_dated)'})
    with urlopen(req, timeout=120) as r, open(dest, 'wb') as fh:
        shutil.copyfileobj(r, fh)
    return dest


def fetch(key: str, where: Path, need) -> Path:
    """Download what the dated rows need: the whole archive, or only the needed per-material zips of an IAEA directory."""
    _, kind, url = SOURCES[key]
    d = where / key; d.mkdir(parents=True, exist_ok=True)
    if kind == 'file':
        f = d / url.rsplit('/', 1)[1]
        if not f.exists():
            print(f'downloading {url}', file=sys.stderr); _get(url, f)
        return f
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0 (incognita.bench.place_dated)'})
    idx = urlopen(req, timeout=120).read().decode(errors='replace')
    names = set(re.findall(r'href="([^"/]+\.zip)"', idx))
    for z, a in need:
        for nm in names:
            if (re.fullmatch(rf'n_\d+_{z}-{SYM[z]}-{a}\.zip', nm) or re.fullmatch(rf'n_0*{z}-{SYM[z]}-{a}_\d+\.zip', nm)) \
                    and not (d / nm).exists():
                _get(url + nm, d / nm)
    return d


def _texts(src: Path):
    """Yield (name, text) of every candidate ENDF-6 file in a directory / tar / zip (zip members included)."""
    def from_zip(zb, label):
        with zipfile.ZipFile(zb) as zf:
            for n in zf.namelist():
                if not n.endswith('/'):
                    yield f'{label}:{n}', zf.read(n).decode(errors='replace')
    if src.is_dir():
        for p in sorted(src.rglob('*')):
            if p.is_file():
                if p.suffix.lower() == '.zip':
                    yield from from_zip(p, p.name)
                elif p.suffix.lower() not in ('.gz', '.tgz', '.tar', '.bz2', '.xz', '.pdf', '.html', '.htm', '.png', '.json', '.h5'):
                    yield p.name, p.read_text(errors='replace')
    elif src.suffix.lower() == '.zip':
        yield from from_zip(src, src.name)
    else:
        with tarfile.open(src) as tf:
            for m in tf:
                if m.isfile():
                    yield m.name, tf.extractfile(m).read().decode(errors='replace')


def _split_materials(text: str):
    """Yield (mat, ZA, LISO, material text) for every material of an ENDF-6 tape (one or many materials)."""
    lines = text.splitlines(keepends=True)
    cur, mat = [], None
    for L in lines:
        m = L[66:70].strip()
        if not re.fullmatch(r'-?\d+', m or 'x'):
            continue
        mi = int(m)
        if mi > 0:
            if mi != mat:
                cur, mat = [], mi
            cur.append(L)
        elif mi == 0 and cur:
            if len(cur) > 2 and cur[0][70:72].strip() == '1' and cur[0][72:75].strip() == '451':
                za = int(float(S._f(cur[0][0:11]))); liso = int(S._f(cur[1][33:44]))
                yield mat, za, liso, ''.join(cur)
            cur, mat = [], None


def read_mf3(pendf: Path, mts) -> dict:
    """{mt: (x, y)} of the requested MF3 sections of a PENDF (lin-lin, as RECONR writes it)."""
    want = set(mts); out = {}
    lines = pendf.read_text(errors='replace').splitlines()
    i = 0
    while i < len(lines):
        L = lines[i]
        if len(L) >= 75 and L[70:72].strip() == '3' and L[72:75].strip().isdigit():
            mt = int(L[72:75])
            if mt in want and mt not in out:
                t = lines[i + 1]
                nr, npt = int(S._f(t[44:55])), int(S._f(t[55:66]))
                vals, j = [], i + 2
                need = 2 * nr + 2 * npt
                while len(vals) < need:
                    row = lines[j]
                    vals += [S._f(row[k:k + 11]) for k in range(0, 66, 11) if row[k:k + 11].strip()]
                    j += 1
                xy = np.array(vals[2 * nr:need], float).reshape(-1, 2)
                out[mt] = (xy[:, 0], xy[:, 1]); i = j; continue
        i += 1
    return out


def mf3_mts(text: str) -> list[int]:
    return sorted({int(L[72:75]) for L in text.splitlines() if len(L) >= 75 and L[70:72].strip() == '3'
                   and L[72:75].strip().isdigit() and int(L[72:75]) > 0})


def place(key: str, src: Path, njoy: str) -> pd.DataFrame:
    name = SOURCES[key][0] if key in SOURCES else key
    R = S.src('dated_rows')[KEY].drop_duplicates().reset_index(drop=True)
    R = R.merge(S.src('dated_row_spans')[KEY + ['e_lo', 'e_hi']], on=KEY, how='left', validate='one_to_one')
    need = set(zip(R.Z.astype(int), R.A.astype(int)))
    out = R[KEY].copy(); v = np.full(len(R), np.nan); f = np.zeros(len(R)); s = np.array([''] * len(R), dtype=object)
    done = set()
    for nm, text in _texts(src):
        if '451' not in text[:2000]:
            continue
        for mat, za, liso, mtext in _split_materials(text):
            z, a = za // 1000, za % 1000
            if (z, a) not in need or liso != 0 or (z, a) in done:
                continue
            with tempfile.TemporaryDirectory() as w:
                w = Path(w)
                (w / 'tape20').write_text(' tape' + ' ' * 61 + '   1 0  0    0\n' + mtext + ' ' * 66 + '  -1 0  0    0\n')
                (w / 'input').write_text(f"reconr\n20 21/\n'pendf'/\n{mat} 0/\n0.001/\n0/\nstop\n")
                with open(w / 'input') as fin:
                    r = subprocess.run([njoy], stdin=fin, cwd=w, capture_output=True, timeout=1800)
                if r.returncode != 0 or not (w / 'tape21').exists():
                    print(f'  {name} {nm}: NJOY failed (rc {r.returncode})', file=sys.stderr); continue
                cur = BA.channel_curves(read_mf3(w / 'tape21', BA.WANT_MTS), mf3_mts(mtext))
            m = ((R.Z == z) & (R.A == a)).to_numpy()
            vv, _, ff, ss = BA.place_rows(cur, R.quantity[m].to_numpy(), R.energy_ev[m].to_numpy(float), R.emin_ev[m].to_numpy(float),
                                          R.e_lo[m].to_numpy(float), R.e_hi[m].to_numpy(float))
            v[m], f[m], s[m] = vv, ff, ss
            done.add((z, a))
            print(f'  {name}: {SYM[z]}-{a} ({int(m.sum())} rows)', file=sys.stderr)
    out[f'lib:{name}'] = np.where(v > 0, np.log10(np.where(v > 0, v, 1.0)), np.nan)
    out[f'src:{name}'] = s; out[f'frac:{name}'] = f
    print(f'{name}: {len(done)} of {len(need)} dated nuclei, {int(np.isfinite(out[f"lib:{name}"]).sum())} of {len(R)} rows', file=sys.stderr)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--library', help=f'one of {", ".join(SOURCES)}')
    ap.add_argument('--endf', help='directory / tar / zip of the official ENDF-6 files')
    ap.add_argument('--fetch', help='download the official files into this directory first')
    ap.add_argument('--njoy', default=shutil.which('njoy') or 'njoy', help='NJOY2016 executable')
    ap.add_argument('--merge', nargs='*', help='merge per-library tables into one')
    ap.add_argument('--out', required=True)
    a = ap.parse_args(argv)
    if a.merge:
        T = None
        for p in a.merge:
            x = pd.read_parquet(p)
            T = x if T is None else T.merge(x, on=KEY, how='outer', validate='one_to_one')
        T.to_parquet(a.out, index=False); print(f'-> {a.out}: {len(T)} rows, {sum(c.startswith("lib:") for c in T)} libraries')
        return
    src = Path(a.endf) if a.endf else None
    if a.fetch:
        R = S.src('dated_rows')
        src = fetch(a.library, Path(a.fetch), sorted(set(zip(R.Z.astype(int), R.A.astype(int)))))
    if src is None:
        raise SystemExit('give --endf or --fetch')
    place(a.library, src, a.njoy).to_parquet(a.out, index=False)
    print(f'-> {a.out}')


if __name__ == '__main__':
    main()
