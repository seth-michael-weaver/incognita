"""Fetch-and-place for the NON-dated tracks (2026-11-06): bin averages for the capture tracks, and the MT 5 alpha parts.

    uv run python -m incognita.bench.place_tracks --library endfb81 --endf DIR_OR_ARCHIVE --njoy PATH --out place_endfb81.parquet \
        [--grid-out DIR]
    uv run python -m incognita.bench.place_tracks --merge place_*.parquet --out track_library.parquet
    uv run python -m incognita.bench.score leaderboard --track-library track_library.parquet

Why. The staged grids (score.G) SAMPLE the 0 K RECONR curve at the row energy. Below ~100 keV that is one point inside a
resonance ladder, while a capture row is a mean: of the EXFOR datasets in a bin (capture-heldout, -nostructure, -retro) or
of a measurement with its own energy resolution (ch-capture). The dated tracks were moved to bin averages in DATEDEXAM2
(binavg.py); this does the same for capture-heldout, capture-nostructure, capture-retro and ch-capture, for every library.

Rule (binavg.py's, with the window of each track):
  - pointwise curve = NJOY2016 RECONR at 0 K, tolerance 0.1 %, lin-lin; channel capture = MT 102;
  - value = lethargy (1/E-weighted) average of the curve over the row's window, integrated exactly segment by segment;
  - window: capture-heldout / capture-nostructure: the engine energy bin of the cell (64-point log grid 1 keV - 20 MeV,
    edges at the geometric midpoints; the cell's label is the trust-weighted mean of the datasets in that bin);
    capture-retro: the cell's 0.1-decade bin [10^((b-100)/10), 10^((b-99)/10)] eV; ch-capture (single EXFOR points):
    binavg.row_window (the 0.1 ln E bin below 100 keV, a 2 % window around the point from 100 keV up).
  Frozen INCOGNITA / default-TALYS entries are smooth model curves stored at the bin energy; they are not re-placed
  (no curve ships with the frozen exam files); for a smooth curve the bin average equals the bin-centre value to well
  under 1 %.
With --grid-out the same RECONR run also writes the library's staged grid for these nuclei (score.G, the staging rule,
every MT the scorer reads, plus the MT 5 alpha pseudo-MTs 905/906 of alpha.py), so a library that was staged before the
alpha fix can be re-scored without rebuilding everything.
"""
from __future__ import annotations

import argparse
import sys
import tempfile
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd

from incognita.bench import alpha as AL
from incognita.bench import binavg as BA
from incognita.bench import score as S
from incognita.bench.place_dated import SOURCES, SYM, _split_materials, _texts, read_mf3, mf3_mts

CAPTURE_TRACKS = ('capture-heldout', 'capture-nostructure', 'capture-retro', 'ch-capture')
ENGINE_GRID = np.logspace(3, np.log10(2e7), 64)          # chart dumps' e_ev (checked equal to chart_s9_npz)
_EDGES = np.concatenate([[ENGINE_GRID[0]], np.sqrt(ENGINE_GRID[:-1] * ENGINE_GRID[1:]), [ENGINE_GRID[-1]]])
KEY = ['track', 'row']


def capture_windows() -> pd.DataFrame:
    """(track, row, Z, A, energy_ev, lo, hi) of every row of the four capture tracks."""
    out = []
    X = S.src('capture_blind_cells')
    for k in ('capture-heldout', 'capture-nostructure'):
        T = S.build(k)
        b = np.searchsorted(ENGINE_GRID, T.energy_ev.to_numpy() * (1 - 1e-9))     # the cell's engine bin
        assert np.allclose(ENGINE_GRID[b], T.energy_ev), k
        out.append(pd.DataFrame({'track': k, 'row': T.row, 'Z': T.Z, 'A': T.A, 'energy_ev': T.energy_ev,
                                 'lo': _EDGES[b], 'hi': _EDGES[b + 1]}))
    del X
    R = S.src('retro_rows')
    R = R[~R.P & np.isfinite(R.err_ours) & R.tendlY_available].reset_index(drop=True)
    T = S.build('capture-retro')
    out.append(pd.DataFrame({'track': 'capture-retro', 'row': T.row, 'Z': T.Z, 'A': T.A, 'energy_ev': T.energy_ev,
                             'lo': 10.0 ** ((R.bin.to_numpy() - 100) / 10), 'hi': 10.0 ** ((R.bin.to_numpy() - 99) / 10)}))
    T = S.build('ch-capture')
    w = np.array([BA.row_window(e, None, e, e) for e in T.energy_ev.to_numpy(float)])
    out.append(pd.DataFrame({'track': 'ch-capture', 'row': T.row, 'Z': T.Z, 'A': T.A, 'energy_ev': T.energy_ev,
                             'lo': w[:, 0], 'hi': w[:, 1]}))
    W = pd.concat(out, ignore_index=True)
    assert (W.lo < W.hi).all() and ((W.energy_ev >= W.lo * 0.999) & (W.energy_ev <= W.hi * 1.001)).all()
    return W


def needed_nuclei() -> set:
    """Every (Z, A > 0) of the non-dated tracks."""
    s = set()
    for k in S.TRACKS:
        if not k.startswith('dated-'):
            T = S.build(k)
            s |= {(int(z), int(a)) for z, a in zip(T.Z, T.A) if a > 0}
    return s


def run_reconr(mat: int, mtext: str, njoy: str):
    w = Path(tempfile.mkdtemp())
    (w / 'tape20').write_text(' tape' + ' ' * 61 + '   1 0  0    0\n' + mtext + ' ' * 66 + '  -1 0  0    0\n')
    (w / 'input').write_text(f"reconr\n20 21/\n'pendf'/\n{mat} 0/\n0.001/\n0/\nstop\n")
    with open(w / 'input') as fin:
        r = subprocess.run([njoy], stdin=fin, cwd=w, capture_output=True, timeout=3600)
    return w, (r.returncode == 0 and (w / 'tape21').exists())


def place(key: str, src: Path, njoy: str, grid_out: Path | None = None, only=None) -> pd.DataFrame:
    name = SOURCES[key][0] if key in SOURCES else key
    W = capture_windows()
    need = needed_nuclei() if only is None else set(only)
    v = np.full(len(W), np.nan)
    grid_rows, done = [], set()
    want = sorted(set(S.LOAD_MTS) | set(range(600, 650)))
    for nm, text in _texts(src):
        if '451' not in text[:2000]:
            continue
        for mat, za, liso, mtext in _split_materials(text):
            z, a = za // 1000, za % 1000
            if (z, a) not in need or liso != 0 or (z, a) in done:
                continue
            w, ok = run_reconr(mat, mtext, njoy)
            if not ok:
                print(f'  {name} {nm}: NJOY failed', file=sys.stderr)
                continue
            pend = read_mf3(w / 'tape21', want)
            orig = set(mf3_mts(mtext))
            for f in w.iterdir():
                f.unlink()
            w.rmdir()
            m = ((W.Z == z) & (W.A == a)).to_numpy()
            if m.any() and 102 in pend and 102 in orig:
                x, y = map(np.asarray, pend[102])
                v[m] = [BA.lethargy_average(x, y, lo, hi)[0] for lo, hi in zip(W.lo[m], W.hi[m])]
            if grid_out is not None:
                tab = {mt: np.clip(np.interp(S.G, np.asarray(xx), np.asarray(yy), left=0.0, right=0.0), 0, None)
                       for mt, (xx, yy) in pend.items() if mt in S.LOAD_MTS}
                tab = {mt: y for mt, y in tab.items() if np.any(y > 0)}
                tab.update(AL.mt5_alpha_parts(mtext, z, a, tab.get(5, np.zeros(len(S.G))), S.G))
                grid_rows += [dict(Z=z, N=a - z, iso=0, mt=int(mt), values_b=yy.tolist()) for mt, yy in sorted(tab.items())]
            done.add((z, a))
            print(f'  {name}: {SYM[z]}-{a} ({int(m.sum())} capture rows)', file=sys.stderr, flush=True)
    out = W[KEY].copy()
    out[f'lib:{name}'] = np.where(v > 0, np.log10(np.where(v > 0, v, 1.0)), np.nan)
    print(f'{name}: {len(done)} of {len(need)} nuclei, {int(np.isfinite(out[f"lib:{name}"]).sum())} of {len(W)} capture rows',
          file=sys.stderr)
    if grid_out is not None:
        grid_out.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(grid_rows).to_parquet(grid_out / f'{key}.parquet', index=False)
    return out


def track_library_values(track: str, path) -> dict:
    """{library name: log10 barns on the rows of a capture track} from a merged place_tracks table."""
    if not path or track not in CAPTURE_TRACKS:
        return {}
    L = pd.read_parquet(path)
    L = L[L.track == track].set_index('row')
    n = len(S.build(track))
    return {c[4:]: L[c].reindex(range(n)).to_numpy(float) for c in L.columns if c.startswith('lib:')}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--library')
    ap.add_argument('--endf', help='directory / tar / zip of the official ENDF-6 files')
    ap.add_argument('--njoy', default='njoy')
    ap.add_argument('--grid-out', help='also write <DIR>/<library>.parquet: the staged grid of these nuclei')
    ap.add_argument('--merge', nargs='*')
    ap.add_argument('--out', required=True)
    a = ap.parse_args(argv)
    if a.merge:
        T = None
        for p in a.merge:
            x = pd.read_parquet(p)
            T = x if T is None else T.merge(x, on=KEY, how='outer', validate='one_to_one')
        T.to_parquet(a.out, index=False)
        print(f'-> {a.out}: {len(T)} rows, {sum(c.startswith("lib:") for c in T)} libraries')
        return
    place(a.library, Path(a.endf), a.njoy, Path(a.grid_out) if a.grid_out else None).to_parquet(a.out, index=False)
    print(f'-> {a.out}')


if __name__ == '__main__':
    main()
