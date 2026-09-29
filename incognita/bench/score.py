"""INCOGNITA open benchmark: score any evaluation on frozen EXFOR-derived tracks, the same way for everyone.

    uv run python -m incognita.bench.score tracks                          # list tracks, verify source hashes
    uv run python -m incognita.bench.score export  --track capture-heldout --out rows.csv
    uv run python -m incognita.bench.score score   --track capture-heldout --csv my.csv --name "my model"
    uv run python -m incognita.bench.score score   --track all --library tendl2025             # a staged 3000-point grid
    uv run python -m incognita.bench.score score   --track all --endf DIR --name "my lib"      # ENDF-6 / PENDF files
    uv run python -m incognita.bench.score leaderboard --out docs/release/bench                # frozen entries + staged libraries

Track definitions, sources and their sha256 live in `TRACKS` below and `tracks/<id>.md` (the data cards). Every
track is a fixed list of measured points (row = 0..n-1 in the exported order). The label is log10 of the measured
cross section in barns (spectrum-averaged for the SACS track).

Submissions
- CSV: columns `track,row,value_b` (or `log10_b`); optional `h68,h95` = half-widths of the 68 / 95 % intervals in
  log10 units, which adds coverage columns. Rows you do not give are "not covered" (see scoring rule).
- a staged library grid (`<key>.parquet` from data/ingest/build_evaluated.py, INPUTS.md section 2), or
- ENDF-6 files: MF3 is read directly. Files whose MF2 still holds resonance parameters (LRP = 1) need their
  resonance region reconstructed first; with `--njoy PATH` the scorer runs NJOY2016 RECONR (tolerance 0.1 %) itself,
  otherwise pass PENDF files (RECONR output). Library values are log-log interpolated at the row energy on a 3000-point
  grid (1e-5 eV - 20 MeV), which is how our lab scored the libraries (incognita/eval/hydrate.py).
- dated-Y tracks (0.1 ln E bin means of EXFOR series, down to 1 keV) score libraries ONLY as bin averages of their RECONR
  curve over each row's own bin (incognita/bench/binavg.py): grid samples inside resolved resonances are not bin means.
  Build the table with `uv run python -m incognita.bench.place_dated` (no library value ships) and pass `--dated-library`.

Scoring rule (same for every entry)
- error e = log10(prediction / measurement) per row; primary = rms(e), point-weighted, or nucleus-weighted where the
  track says so (each nucleus counts once).
- A row is covered if the prediction is finite and > 0. rms is over covered rows; coverage is reported. On tracks
  with `miss_dex` (NA-FRESH) an uncovered row counts as an error of that size instead.
- 95 % CI: nucleus bootstrap (resample nuclei with replacement), paired against the track's reference entry on the
  rows both cover. Seed and draws per track (the values our published tables used).
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
EXAM = REPO / 'docs' / 'release' / 'exam'
DATA = HERE / 'data'
G = np.logspace(-5, np.log10(2e7), 3000)          # the staged library grid (eV), = incognita.eval.incognita_eval.G
HEMT = (107, 22, 24, 45, 112, 117)                 # He-4 production = sum of alpha-emitting channels (hydrate.py)
QMT = {'capture': (102,), 'na': (107,), 'he_prod': HEMT, 'n2n': (16,), 'np': (103,),
       'total': (1,), 'elastic': (2,), 'inelastic': (4,)}   # MT 1/2/4: the dated tracks' total/elastic/inelastic rows

# staged grids from the official distributions (docs/release/INPUTS.md section 2) with their release years
LIBRARIES = [('ENDF/B-VIII.1', 'endfb81', 2024), ('JENDL-5', 'jendl5', 2021), ('TENDL-2025', 'tendl2025', 2025),
             ('JEFF-4.0', 'jeff40', 2025), ('JEFF-3.3', 'jeff33', 2017), ('BROND-3.1', 'brond31', 2016),
             ('FENDL-3.2', 'fendl32', 2022), ('CENDL-3.2', 'cendl32', 2020), ('IRDFF-II', 'irdff2', 2020),
             ('ENDF/B-VII.1', 'endfb71', 2011), ('JENDL-4.0', 'jendl40', 2010), ('ENDF/B-VII.0', 'endfb70', 2006)]
# TENDL releases for the dated (retrodiction) entry: per row, the newest release no later than the row's cutoff year
TENDL_DATED = [(2015, 'tendl2015'), (2017, 'tendl2017'), (2019, 'tendl2019'), (2021, 'tendl2021'), (2023, 'tendl2023')]
# dated tracks (DATEDEXAM): freeze year Y of every scored library = calendar year of the release of the files we score (no
# library documents a data-freeze date; sources in docs/release/DATED.md). A library is blind to a dated-Y track iff its Y <= track Y.
DATED_Y = {'ENDF/B-VII.0': 2006, 'JENDL-4.0': 2010, 'ENDF/B-VII.1': 2011, 'TENDL-2015': 2016, 'BROND-3.1': 2016,
           'JEFF-3.3': 2017, 'TENDL-2017': 2017, 'TENDL-2019': 2019, 'CENDL-3.2': 2020, 'IRDFF-II': 2020, 'JENDL-5': 2021,
           'TENDL-2021': 2021, 'FENDL-3.2': 2022, 'TENDL-2023': 2024, 'ENDF/B-VIII.1': 2024, 'JEFF-4.0': 2025,
           'TENDL-2025': 2025}
DATED_TRACK_YEARS = (2006, 2010, 2011, 2016, 2017, 2019, 2020, 2021, 2024)

SRC = {  # sha256 of every frozen source file a track reads (capture_blind_cells / retro_rows: the SHIPEXAMS files of f165e5a3,
       # = docs/release/exam/SHA256SUMS; re-pinned by DATEDEXAM2)
    'capture_blind_cells': (EXAM / 'capture_blind_cells.parquet', '5617e404c08455976a7e3c5552f58b2d01474b25ebc041f950985f0a244b7af6'),
    'dated_rows': (EXAM / 'dated_rows.parquet', 'c102bee1a5922d63d9007f7ede879a11fd75ba9f5d5de53101a0ef1505edc55e'),
    # DATEDEXAM2: [E_lo, E_hi] of each dated row's own EXFOR points (energies only), the bin-average window above 100 keV
    'dated_row_spans': (EXAM / 'dated_row_spans.parquet', 'f55093143c230bb096273168a5ee556757d6081589287b9c7338782f9ea987f2'),
    'retro_rows': (EXAM / 'retro_rows.parquet', '78a6e30080200b5e8aa41062aee55f95e19ebe364fda267bd0e6663bc856a9ab'),
    'na_v1_rows': (EXAM / 'na_v1_rows.parquet', 'a94267abd85f83c0959725f17a503373e7b03f19f4655de25833dd20a6bd7467'),
    'na_fresh': (DATA / 'na_fresh.parquet', '0e08a83a4ac57910553937b267dc80f974df56a4821e81027f3eb384f5a741cf'),
    'na_rows': (DATA / 'exam_rows' / 'na_rows.parquet', None),
    'n2n_rows': (DATA / 'exam_rows' / 'n2n_rows.parquet', None),
    'np_rows': (DATA / 'exam_rows' / 'np_rows.parquet', None),
    'capture_rows': (DATA / 'exam_rows' / 'capture_rows.parquet', None),
    'sacs_rows': (DATA / 'exam_rows' / 'sacs_rows.parquet', None),
}
for _k in ('na_rows', 'n2n_rows', 'np_rows', 'capture_rows', 'sacs_rows'):  # hashes from the shipped SHA256SUMS
    _s = dict(reversed(l.split()) for l in (DATA / 'exam_rows' / 'SHA256SUMS').read_text().splitlines() if l.strip())
    SRC[_k] = (SRC[_k][0], _s[f'{_k}.parquet'])


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def src(key: str) -> pd.DataFrame:
    p, h = SRC[key]
    if not p.exists():
        raise SystemExit(f'missing track source {p}')
    if sha256(p) != h:
        raise SystemExit(f'{p} does not match its frozen sha256 {h[:12]}...: the track would not be the published one')
    return pd.read_parquet(p)


def nid(z, a):
    return np.asarray(z, int) * 1000 + np.asarray(a, int)


# ---------------------------------------------------------------------------------------------------- track builders
# Each returns a frame with: Z, A, energy_ev, quantity, spectrum ('' unless SACS), label (log10 barns), optional subset
# columns 'sub:<name>' (bool) and frozen entries 'entry:<name>' (log10 barns).

def t_capture_heldout():
    X = src('capture_blind_cells')
    pred = ['pred_ours_d0free', 'pred_ours_d0assisted', 'pred_recipe_d0free', 'pred_recipe_d0assisted']
    X = X[(X.Z <= 82) & np.all([np.isfinite(X[c] - X.target_log10_P) for c in pred], 0)].reset_index(drop=True)
    return pd.DataFrame({
        'Z': X.Z, 'A': X.A, 'energy_ev': X.energy_ev, 'quantity': 'capture', 'spectrum': '', 'label': X.target_log10_P,
        'fold': X.fold,
        'sub:well_measured (trust >= 1)': X.trust_P >= 1,
        'sub:precision cut (>= 3 datasets within x1.3, E < 10 MeV, NON-SMOKER covers)':
            (X.energy_ev < 1e7) & X.nonsmoker_covers & X.precision_P,
        'entry:INCOGNITA capture, D0 withheld (headline)': X.pred_ours_d0free,
        'entry:INCOGNITA capture, measured D0 used': X.pred_ours_d0assisted,
        'entry:default TALYS = TENDL no-data recipe (our engine), D0 withheld': X.pred_recipe_d0free,
        'entry:default TALYS = TENDL no-data recipe (our engine), measured D0': X.pred_recipe_d0assisted})


def t_capture_nostructure():
    X = src('capture_blind_cells')
    X = X[(X.Z <= 82) & X.fold.isin(range(6)) & np.isfinite(X.pred_ours_strip - X.target_log10)
          & np.isfinite(X.pred_recipe_strip)].reset_index(drop=True)
    return pd.DataFrame({
        'Z': X.Z, 'A': X.A, 'energy_ev': X.energy_ev, 'quantity': 'capture', 'spectrum': '', 'label': X.target_log10,
        'entry:INCOGNITA capture, no structure data (STRIP)': X.pred_ours_strip,
        'entry:default TALYS = TENDL no-data recipe (our engine), no structure data': X.pred_recipe_strip})


def t_capture_retro():
    R = src('retro_rows')
    R = R[~R.P & np.isfinite(R.err_ours) & R.tendlY_available].reset_index(drop=True)
    lab = np.log10(R.meas_b)
    return pd.DataFrame({
        'Z': R.nuclide_id.str[1:4].astype(int), 'A': R.nuclide_id.str[1:4].astype(int) + R.nuclide_id.str[5:8].astype(int),
        'energy_ev': R.e_mid_ev, 'quantity': 'capture', 'spectrum': '', 'label': lab, 'cutoff_year': R.retro_y,
        'measured_year': R.year,
        'entry:INCOGNITA capture trained on data up to year Y': lab + R.err_ours,
        'entry:default TALYS = TENDL no-data recipe (our engine)': lab + R.err_recipe})


def _dated(y):
    def f():
        R = src('dated_rows')
        R = R[R.freeze_year == y].reset_index(drop=True)
        out = pd.DataFrame({'Z': R.Z, 'A': R.A, 'energy_ev': R.energy_ev, 'quantity': R.quantity, 'spectrum': '',
                            'label': R.label, 'freeze_year': R.freeze_year, 'pub_year': R.pub_year,
                            'compiled_year': R.compiled_year, 'entry': R.entry})
        for q in ('capture', 'n2n', 'np', 'na', 'total', 'elastic', 'inelastic'):
            if (R.quantity == q).any():
                out[f'sub:{q}'] = (R.quantity == q).to_numpy()
        # energy regions (DATEDEXAM2): libraries are placed as bin averages (binavg.py), so every region is scored,
        # including below 100 keV; 'E >= 100 keV' is DATEDEXAM's post-hoc subset, kept for continuity
        for b, lo, hi in (('< 10 keV', 0, 1e4), ('10-100 keV', 1e4, 1e5), ('0.1-1 MeV', 1e5, 1e6), ('1-10 MeV', 1e6, 1e7),
                          ('> 10 MeV', 1e7, np.inf)):
            out[f'sub:{b}'] = ((R.energy_ev >= lo) & (R.energy_ev < hi)).to_numpy()
        out['sub:E >= 100 keV (DATEDEXAM post-hoc subset)'] = (R.energy_ev >= 1e5).to_numpy()
        out['entry:INCOGNITA DEFD (default TALYS port + defect GP from pre-Y EXFOR series)'] = R.pred_defd
        out['entry:INCOGNITA capture chart trained on data up to Y (capture only)'] = R.pred_chart
        out['entry:default TALYS (our engine; the blind rival)'] = R.pred_def
        return out
    return f


def _na_v1(setname):
    def f():
        R = src('na_v1_rows')
        R = R[R.set == setname].reset_index(drop=True)
        q = np.where(R.state == 'He', 'he_prod', np.where(R.state == 'T', 'na', 'na_' + R.state.astype(str)))
        return pd.DataFrame({
            'Z': R.Z, 'A': R.A, 'energy_ev': R.e_ev, 'quantity': q, 'spectrum': '', 'label': np.log10(R.data_mb / 1e3),
            **({'sub:A > 70 (natural targets: Z > 30)': (R.A > 70) | ((R.A == 0) & (R.Z > 30))}
               if setname == 'helium production' else {}),
            **({'sub:(n,a) total only (the rows a library file can be scored on)': R.state == 'T'}
               if setname == 'isomer/ground/total' else {}),
            'entry:INCOGNITA (n,a) v1 recipe': np.log10(R.v1_mb / 1e3),
            'entry:default TALYS = TENDL no-data recipe (our engine)': np.log10(R.default_mb / 1e3)})
    return f


def t_na_post2021():
    R = src('na_fresh')
    out = pd.DataFrame({'Z': R.Z, 'A': R.A, 'energy_ev': R.E_MeV * 1e6, 'quantity': 'na', 'spectrum': '',
                        'label': np.log10(R.sigma_mb / 1e3), 'year': R.year})
    e = HERE / 'entries' / 'na-post2021' / 'incognita_na_v2.csv'
    if e.exists():
        v = pd.read_csv(e).set_index('row').value_b.reindex(range(len(out)))
        out['entry:INCOGNITA (n,a) v2 (frozen 2026-09-23 before this set was read)'] = np.log10(v.where(v > 0)).values
    return out


def _channel(ch):
    def f():
        R = src(f'{ch}_rows')
        if ch == 'na':
            q, lab = np.where(R.kind == 'nxa', 'he_prod', 'na'), np.log10(R.data_mb / 1e3)
        elif ch == 'capture':
            q, lab = 'capture', np.log10(R.data_b)
        else:
            q, lab = ch, np.log10(R.data_mb / 1e3)
        return pd.DataFrame({'Z': R.Z, 'A': R.A, 'energy_ev': R.e_ev, 'quantity': q, 'spectrum': '', 'label': lab,
                             'year': R.year})
    return f


def t_sacs():
    R = src('sacs_rows')
    R = R[~R.suspect.astype(bool)].reset_index(drop=True)
    out = pd.DataFrame({'Z': R.Z, 'A': R.A, 'energy_ev': np.nan, 'quantity': R.channel, 'spectrum': R.spectrum,
                        'label': np.log10(R.data_mb / 1e3), 'year': R.year})
    for ch in ('capture', 'na', 'n2n', 'np'):
        out[f'sub:{ch}'] = (R.channel == ch).to_numpy()
    return out


# id -> (builder, reference entry, weighting, miss_dex, bootstrap (seed, draws), one-line description)
TRACKS = {
    'capture-heldout': (t_capture_heldout, 'entry:default TALYS = TENDL no-data recipe (our engine), D0 withheld', 'point', None,
                        (20260923, 10000), 'capture sigma(E), 122 nuclei held out of our fit (DEV folds 0-5, Z <= 82; shipped library-free model), audited targets'),
    'capture-nostructure': (t_capture_nostructure, 'entry:default TALYS = TENDL no-data recipe (our engine), no structure data', 'point', None,
                            (20260923, 10000), 'capture sigma(E), held-out nuclei, DEV folds 0-5, model given no structure data'),
    'capture-retro': (t_capture_retro, 'entry:default TALYS = TENDL no-data recipe (our engine)', 'point', None,
                      (20260910, 5000), 'capture sigma(E) measured after year Y, predicted from data up to Y (Y = 2015-2023)'),
    **{f'dated-{y}': (_dated(y), 'entry:default TALYS (our engine; the blind rival)', 'point', None, (20260923, 5000),
                      f'all 7 channels, EXFOR entries published AND compiled after {y}; our arms trained on data up to {y}; '
                      f'libraries released <= {y} are blind to these rows') for y in DATED_TRACK_YEARS},
    'na-pickup': (_na_v1('isomer/ground/total'), 'entry:default TALYS = TENDL no-data recipe (our engine)', 'point', None,
                  (20260923, 10000), '(n,a) isomer / ground-state / total production, 57 targets, registered before read'),
    'na-heprod': (_na_v1('helium production'), 'entry:default TALYS = TENDL no-data recipe (our engine)', 'point', None,
                  (20260923, 10000), 'He-4 production (n,xa), 52 targets incl. natural, registered before read'),
    'na-neverread': (_na_v1('never-read (M)/M+'), 'entry:default TALYS = TENDL no-data recipe (our engine)', 'point', None,
                     (20260923, 10000), '(n,a) to isomers on 8 targets never read before the recipe froze'),
    'na-post2021': (t_na_post2021, 'lib:JENDL-5', 'nucleus', 1.0, (0, 10000),
                    '(n,a) measured 2021+ (after JENDL-5), 116 points / 12 nuclei; misses = 1 dex'),
    'ch-na': (_channel('na'), 'lib:TENDL-2025', 'point', None, (20260922, 1000), '(n,a) and He production, EXFOR, all years (in-sample for every library)'),
    'ch-n2n': (_channel('n2n'), 'lib:TENDL-2025', 'point', None, (20260922, 1000), '(n,2n), EXFOR binned, all years (in-sample)'),
    'ch-np': (_channel('np'), 'lib:TENDL-2025', 'point', None, (20260922, 1000), '(n,p), EXFOR binned, all years (in-sample)'),
    'ch-capture': (_channel('capture'), 'lib:TENDL-2025', 'point', None, (20260922, 1000), 'capture above the resolved region, EXFOR, all years (in-sample)'),
    'ch-sacs': (t_sacs, 'lib:TENDL-2025', 'point', None, (20260922, 1000), 'spectrum-averaged (U-235 / Cf-252) capture, (n,a), (n,2n), (n,p), non-suspect'),
}
# tracks that publication spends: retired from our internal model selection from the release on
RETIRED = {k: True for k in TRACKS}


def build(track: str) -> pd.DataFrame:
    T = TRACKS[track][0]()
    T.insert(0, 'row', np.arange(len(T)))
    return T.reset_index(drop=True)


DATED_LIBRARY_ENV = 'INCOGNITA_DATED_LIBRARY'


def dated_library_values(y: int, path=None) -> dict:
    """{library name: log10 barns on the rows of track dated-y}: every library as the lethargy average of its 0 K RECONR
    curve over the row's own 0.1 ln E bin (incognita/bench/binavg.py).  No library value ships with the benchmark: the
    table is built from the official files by `uv run python -m incognita.bench.place_dated` and passed as `--dated-library PATH`
    (or $INCOGNITA_DATED_LIBRARY).  Without it the dated tracks score no library: grid SAMPLES of resolved resonances
    against 0.1 ln E bin means are wrong below ~100 keV (DATEDEXAM), so there is no fallback.  NaN = no curve."""
    p = path or os.environ.get(DATED_LIBRARY_ENV)
    if not p:
        print(f'dated-{y}: no --dated-library table (build it with uv run python -m incognita.bench.place_dated); libraries not scored',
              file=sys.stderr)
        return {}
    R = src('dated_rows')
    R = R[R.freeze_year == y].reset_index(drop=True)
    L = pd.read_parquet(p)
    K = ['Z', 'A', 'quantity', 'series', 'energy_ev', 'emin_ev']
    M = R[K].merge(L, on=K, how='left', validate='many_to_one')
    assert len(M) == len(R) and (M.Z.to_numpy() == R.Z.to_numpy()).all()
    return {c[4:]: M[c].to_numpy(float) for c in L.columns if c.startswith('lib:')}


def public_rows(T: pd.DataFrame) -> pd.DataFrame:
    return T[[c for c in T.columns if not c.startswith('entry:')]]


def rows_sha(T: pd.DataFrame) -> str:
    b = public_rows(T).to_csv(index=False, float_format='%.10g', lineterminator='\n').encode()
    return hashlib.sha256(b).hexdigest()


# ---------------------------------------------------------------------------------------------------- predictions
def interp_loglog(x, y, e):
    ok = y > 0
    if ok.sum() <= 2:
        return np.nan
    return float(np.exp(np.interp(np.log(e), np.log(x[ok]), np.log(y[ok]))))


def spectrum_fold(x, y, kind):
    from incognita.eval.spectra import fold
    return fold(x, y, kind)


class Curves:
    """(Z, A, mt) -> pointwise barns on an energy grid; value() applies the benchmark's sampling rule."""

    def __init__(self, tab: dict, grid=None):
        self.tab, self.grid = tab, grid          # tab[(z, a, mt)] = (x, y) or y on self.grid

    def xy(self, z, a, mt):
        v = self.tab.get((z, a, mt))
        if v is None:
            return None
        return (self.grid, v) if self.grid is not None else v

    def value(self, z, a, q, e, spectrum=''):
        mts = QMT.get(q)
        if mts is None or self.xy(z, a, mts[0]) is None:
            return np.nan
        if len(mts) == 1:
            x, y = self.xy(z, a, mts[0])
        else:                                     # sum on the first curve's grid
            x, y0 = self.xy(z, a, mts[0]); y = np.array(y0, float)
            for m in mts[1:]:
                c = self.xy(z, a, m)
                if c is not None:
                    y = y + (c[1] if c[0] is x else np.interp(x, c[0], c[1], left=0, right=0))
        if spectrum:
            return spectrum_fold(np.asarray(x), np.asarray(y) * 1e3, spectrum) / 1e3
        return interp_loglog(np.asarray(x), np.asarray(y), e)


def staged_library(key: str, evaluated: Path | None = None) -> Curves:
    from incognita import config
    p = (evaluated or config.evaluated_dir()) / f'{key}.parquet'
    mts = sorted({m for v in QMT.values() for m in v})
    x = pd.read_parquet(p, columns=['Z', 'N', 'iso', 'mt', 'values_b'], filters=[('iso', '==', 0), ('mt', 'in', mts)])
    return Curves({(int(r.Z), int(r.Z + r.N), int(r.mt)): np.asarray(r.values_b, float) for r in x.itertuples()}, G)


# --- ENDF-6 ---------------------------------------------------------------------------------------------------------
def _f(s):
    s = s.strip()
    if not s:
        return 0.0
    m = re.match(r'^([+-]?[\d.]+)([+-]\d+)$', s)
    return float(f'{m.group(1)}e{m.group(2)}') if m else float(s)


def _interp_law(x, y, nbt, law, e):
    """ENDF TAB1 interpolation (laws 1-5) of (x, y) at e."""
    out = np.empty_like(e)
    lo = 0
    for hi, L in zip(nbt, law):
        seg = slice(lo, hi)
        xs, ys = x[seg], y[seg]
        m = (e >= xs[0]) & (e <= xs[-1])
        if m.any():
            if L == 1:
                out[m] = ys[np.clip(np.searchsorted(xs, e[m], 'right') - 1, 0, len(xs) - 1)]
            elif L == 2:
                out[m] = np.interp(e[m], xs, ys)
            elif L == 3:
                out[m] = np.interp(np.log(e[m]), np.log(xs), ys)
            elif L == 4:
                out[m] = np.exp(np.interp(e[m], xs, np.log(np.maximum(ys, 1e-300))))
            else:
                out[m] = np.exp(np.interp(np.log(e[m]), np.log(xs), np.log(np.maximum(ys, 1e-300))))
        lo = hi - 1
    out[(e < x[0]) | (e > x[-1])] = 0.0
    return out


def read_endf(path: Path):
    """-> (Z, A, LRP, {mt: (x, y)}) from MF1/MF3 of one ENDF-6 or PENDF material."""
    lines = path.read_text(errors='replace').splitlines()
    za = lrp = None
    sec = {}
    want = {m for v in QMT.values() for m in v}
    i = 0
    while i < len(lines):
        L = lines[i]
        if len(L) < 75:
            i += 1; continue
        mf, mt = int(L[70:72] or 0), int(L[72:75] or 0)
        if mf == 1 and mt == 451 and za is None:
            za, lrp = _f(L[0:11]), int(_f(L[22:33]))
        if mf == 3 and mt in want and mt not in sec:
            # HEAD, then TAB1: C1 C2 L1 L2 NR NP, NR (NBT, INT) pairs, NP (x, y) pairs
            t = lines[i + 1]
            nr, npt = int(_f(t[44:55])), int(_f(t[55:66]))
            vals, j = [], i + 2
            need = 2 * nr + 2 * npt
            while len(vals) < need:
                row = lines[j]
                vals += [_f(row[k:k + 11]) for k in range(0, 66, 11) if row[k:k + 11].strip()]
                j += 1
            ints = np.array(vals[:2 * nr], int).reshape(-1, 2)
            xy = np.array(vals[2 * nr:need], float).reshape(-1, 2)
            sec[mt] = (xy[:, 0], xy[:, 1], ints[:, 0], ints[:, 1])
            i = j
            continue
        i += 1
    if za is None:
        raise ValueError(f'{path}: no MF1/MT451')
    z, a = int(za) // 1000, int(za) % 1000
    tab = {}
    for mt, (x, y, nbt, law) in sec.items():
        # the staging rule (data/ingest/endf.py:to_grid): sample on the 3000-point grid, 0 outside the table;
        # lin-lin for linearised sections, the section's own laws otherwise
        y = np.interp(G, x, y, left=0.0, right=0.0) if set(law) == {2} else _interp_law(x, y, nbt, law, G.copy())
        tab[mt] = np.clip(y, 0.0, None)
    return z, a, lrp, tab


def reconr(path: Path, njoy: str, workdir: Path | None = None) -> Path:
    mat = int(path.read_text(errors='replace').splitlines()[1][66:70])
    d = Path(tempfile.mkdtemp(dir=workdir))
    (d / 'tape20').symlink_to(path.resolve())
    (d / 'input').write_text(f"reconr\n20 21/\n'benchmark pendf'/\n{mat} 0/\n0.001/\n0/\nstop\n")
    subprocess.run([njoy], stdin=open(d / 'input'), cwd=d, check=True, capture_output=True)
    return d / 'tape21'


def endf_library(paths, njoy: str | None = None, workdir: Path | None = None) -> Curves:
    tab, warned = {}, []
    for p in paths:
        try:
            z, a, lrp, t = read_endf(p)
        except Exception as ex:                    # noqa: BLE001 - one bad file must not stop the library
            print(f'  skip {p.name}: {ex}', file=sys.stderr); continue
        if lrp == 1:
            if njoy:
                pendf = reconr(p, njoy, workdir)
                z, a, _, t = read_endf(pendf)
                shutil.rmtree(pendf.parent, ignore_errors=True)
            else:
                warned.append(p.name)
        for mt, y in t.items():
            tab[(z, a, mt)] = y
    if warned:
        print(f'  WARNING: {len(warned)} files carry resonance parameters (LRP=1) and were read without reconstruction; '
              'values inside the resolved/unresolved range are the MF3 background only. Pass --njoy or PENDF files.',
              file=sys.stderr)
    return Curves(tab, G)


def predict(T: pd.DataFrame, cur: Curves) -> np.ndarray:
    out = np.full(len(T), np.nan)
    for i, r in enumerate(T[['Z', 'A', 'quantity', 'energy_ev', 'spectrum']].itertuples(index=False)):
        v = cur.value(int(r.Z), int(r.A), r.quantity, r.energy_ev, r.spectrum)
        out[i] = np.log10(v) if np.isfinite(v) and v > 0 else np.nan
    return out


def csv_entry(T: pd.DataFrame, track: str, path: Path):
    s = pd.read_csv(path)
    if 'track' in s:
        s = s[s.track == track]
    bad_rows = int((~s.row.isin(range(len(T)))).sum()) if 'row' in s else 0
    s = s[s.row.isin(range(len(T)))] if 'row' in s else s
    s = s.set_index('row').reindex(range(len(T)))
    if 'log10_b' in s:
        v = s.log10_b.to_numpy(float)
    else:
        vb = s.value_b.to_numpy(float)
        v = np.where(vb > 0, np.log10(np.where(vb > 0, vb, 1)), np.nan)
    n_bad = int((~np.isfinite(v)).sum())
    if bad_rows or n_bad:   # never drop submission rows silently
        print(f'WARNING {track}: {bad_rows} submitted row numbers are not on this track (ignored); {n_bad} of {len(T)} rows have no '
              f'usable value (missing, NaN or <= 0) and count as not covered', file=sys.stderr)
    h = (s.h68.to_numpy(float), s.h95.to_numpy(float)) if {'h68', 'h95'} <= set(s.columns) else None
    return v, h


# ---------------------------------------------------------------------------------------------------- scoring
def _boot_counts(n_nuc, seed, draws):
    return np.random.default_rng(seed).multinomial(n_nuc, np.full(n_nuc, 1 / n_nuc), size=draws).astype(float)


def score_entry(T, track, pred, ref=None, h=None):
    _, _, weighting, miss, (seed, draws), _ = TRACKS[track]
    lab = T.label.to_numpy(float)
    e = pred - lab
    cov = np.isfinite(e)
    if miss is not None:
        e = np.where(cov, e, miss); use = np.ones(len(e), bool)
    else:
        use = cov
    nu = nid(T.Z, T.A)
    res = {'rows': int(use.sum()), 'rows_total': len(T), 'covered': int(cov.sum()),
           'nuclei': int(len(np.unique(nu[use])))}
    if not use.any():
        return res

    def agg(mask, err):
        u, inv = np.unique(nu[mask], return_inverse=True)
        k = np.bincount(inv).astype(float)
        w = 1 / k[inv] if weighting == 'nucleus' else np.ones(mask.sum())
        return u, np.bincount(inv, w * err[mask] ** 2), np.bincount(inv, w)

    u, S, W = agg(use, e)
    res['rms'] = float(np.sqrt(S.sum() / W.sum()))
    res['bias'] = float(np.mean(e[use]))
    c = _boot_counts(len(u), seed, draws)
    lo, hi = np.percentile(np.sqrt(c @ S / (c @ W)), [2.5, 97.5])
    res['rms_ci'] = [float(lo), float(hi)]
    if h is not None:
        m = use & np.isfinite(h[0]) & np.isfinite(h[1])
        if m.any():
            res['cover68'] = float(np.mean(np.abs(e[m]) <= h[0][m]))
            res['cover95'] = float(np.mean(np.abs(e[m]) <= h[1][m]))
            res['median_h68'] = float(np.median(h[0][m]))
            res['interval_rows'] = int(m.sum())
    if ref is not None:
        er = ref - lab
        if miss is not None:
            er = np.where(np.isfinite(er), er, miss); both = use.copy()
        else:
            both = use & np.isfinite(er)
        if both.any():
            u2, Sa, Wa = agg(both, e)
            _, Sb, _ = agg(both, er)
            c = _boot_counts(len(u2), seed, draws)
            d = np.sqrt(c @ Sa / (c @ Wa)) - np.sqrt(c @ Sb / (c @ Wa))
            lo, hi = np.percentile(d, [2.5, 97.5])
            res['paired_rows'] = int(both.sum())
            res['ref_rms_same_rows'] = float(np.sqrt(Sb.sum() / Wa.sum()))
            res['delta_vs_ref'] = float(np.sqrt(Sa.sum() / Wa.sum()) - np.sqrt(Sb.sum() / Wa.sum()))
            res['delta_ci'] = [float(lo), float(hi)]
    return res


def subsets(T):
    yield 'all', np.ones(len(T), bool)
    for c in T.columns:
        if c.startswith('sub:'):
            yield c[4:], T[c].to_numpy(bool)


def ref_values(T, track, libs):
    r = TRACKS[track][1]
    if r.startswith('entry:'):
        return T[r].to_numpy(float)
    return libs[r[4:]] if r[4:] in libs else None


# ---------------------------------------------------------------------------------------------------- CLI
def track_list(sel):
    """'all', one id, a comma list, or 'dated' (every dated-Y track)."""
    if sel in (None, 'all'):
        return list(TRACKS)
    out = []
    for t in sel.split(','):
        out += [k for k in TRACKS if k.startswith('dated-')] if t == 'dated' else [t]
    return out


def cmd_tracks(a):
    sel = track_list(getattr(a, 'track', 'all'))
    old = json.loads((HERE / 'tracks' / 'MANIFEST.json').read_text()) if sel != list(TRACKS) else {}
    man = {k: v for k, v in old.items() if k not in sel and k != '_sources'}
    for k in sel:
        (f, ref, wt, miss, bs, desc) = TRACKS[k]
        T = build(k)
        man[k] = {'description': desc, 'rows': len(T), 'nuclei': int(len(np.unique(nid(T.Z, T.A)))),
                  'rows_sha256': rows_sha(T), 'reference': ref, 'weighting': wt, 'miss_dex': miss,
                  'bootstrap': {'seed': bs[0], 'draws': bs[1]}, 'retired_from_internal_selection': RETIRED[k],
                  'frozen_entries': [c[6:] for c in T.columns if c.startswith('entry:')],
                  'subsets': [c[4:] for c in T.columns if c.startswith('sub:')]}
        print(f'{k:20s} {len(T):6d} rows {man[k]["nuclei"]:4d} nuclei  sha256 OK  {desc}')
    man = {k: man[k] for k in TRACKS if k in man}      # manifest in TRACKS order
    man['_sources'] = {k: {'path': str(p.relative_to(REPO)), 'sha256': h} for k, (p, h) in SRC.items()}
    if a.write:
        (HERE / 'tracks' / 'MANIFEST.json').write_text(json.dumps(man, indent=1) + '\n')
        print(f'-> {HERE / "tracks" / "MANIFEST.json"}')


def cmd_export(a):
    ks = track_list(a.track)
    for k in ks:
        T = public_rows(build(k))
        out = Path(a.out) / f'{k}.csv' if len(ks) > 1 or a.track == 'all' else Path(a.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        T.to_csv(out, index=False, float_format='%.10g', lineterminator='\n')
        print(f'{k}: {len(T)} rows -> {out}')


def _entries_for(a, T, k, libs):
    E = []
    if a.csv:
        v, h = csv_entry(T, k, Path(a.csv)); E.append((a.name or Path(a.csv).stem, v, h, 'submission'))
    dl = dated_library_values(int(k[6:]), a.dated_library) if k.startswith('dated-') else {}
    for nm, cur in libs.items():
        if k.startswith('dated-'):                 # dated tracks: bin averages only (see dated_library_values)
            if nm in dl:
                E.append((nm, dl[nm], None, 'library'))
            continue
        E.append((nm, predict(T, cur), None, 'library'))
    return E


def load_libs(a):
    libs = {}
    for key in (a.library or []):
        nm = next((n for n, s, _ in LIBRARIES if s == key), key)
        libs[nm] = staged_library(key, Path(a.evaluated) if a.evaluated else None)
    if getattr(a, 'njoy', None) and not Path(a.njoy).exists():
        raise SystemExit(f'--njoy {a.njoy}: no such file')
    if a.endf:
        files = sorted(p for p in Path(a.endf).rglob('*') if p.is_file())
        if not files:
            raise SystemExit(f'--endf {a.endf}: no files found')
        libs[a.name or Path(a.endf).name] = endf_library(files, a.njoy)
    return libs


def cmd_score(a):
    libs = load_libs(a)
    for k in track_list(a.track):
        T = build(k)
        refv = ref_values(T, k, {n: predict(T, c) for n, c in libs.items()} if TRACKS[k][1].startswith('lib:') else {})
        for nm, v, h, _ in _entries_for(a, T, k, libs):
            for sn, m in subsets(T):
                r = score_entry(T[m].reset_index(drop=True), k, v[m], None if refv is None else refv[m],
                                None if h is None else (h[0][m], h[1][m]))
                print(k, '|', sn, '|', nm, f'| reference entry: {TRACKS[k][1]} |', json.dumps(r))


def fmt_ci(r):
    if 'rms' not in r:
        return '—'
    return f"{r['rms']:.4f} [{r['rms_ci'][0]:.3f}, {r['rms_ci'][1]:.3f}]"


def cmd_leaderboard(a):
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    from incognita import config
    ev = Path(a.evaluated) if a.evaluated else config.evaluated_dir()
    tracks = track_list(a.track)
    TT = {k: build(k) for k in tracks}
    LP = {k: {} for k in tracks}                 # track -> library name -> log10 predictions
    dated = [k for k in tracks if k.startswith('dated-')]
    grid_tracks = [k for k in tracks if k not in dated]
    for nm, key, yr in LIBRARIES:
        if grid_tracks and (ev / f'{key}.parquet').exists():
            print(f'loading {nm}', file=sys.stderr)
            cur = staged_library(key, ev)
            for k in grid_tracks:
                LP[k][nm] = predict(TT[k], cur)
            del cur
    for k in dated:     # DATEDEXAM2: libraries as bin averages on the rows' own bins (frozen table), not grid samples
        LP[k].update(dated_library_values(int(k[6:]), a.dated_library))
    if 'capture-retro' in tracks and all((ev / f'{key}.parquet').exists() for _, key in TENDL_DATED):
        T = TT['capture-retro']; v = np.full(len(T), np.nan); cy = T.cutoff_year.to_numpy()
        for yr, key in TENDL_DATED:
            print(f'loading TENDL-{yr} (dated entry)', file=sys.stderr)
            p = predict(T, staged_library(key, ev))
            v = np.where(cy >= yr, p, v)
        LP['capture-retro']['TENDL-Y (newest release <= cutoff year Y; a true retrodiction)'] = v
    rows, md = [], ['# INCOGNITA benchmark leaderboard (generated by `python -m incognita.bench.score leaderboard`)', '',
                    'rms of log10(prediction / measurement); 95 % nucleus-bootstrap CI; Δ = paired difference vs the '
                    "track's reference entry on the rows both cover (negative = better). Rows = covered / total.", '']
    for k in tracks:
        T = TT[k]
        _, ref, wt, miss, _, desc = TRACKS[k]
        P = {c[6:]: (T[c].to_numpy(float), 'frozen entry') for c in T.columns if c.startswith('entry:')}
        for nm, v in LP[k].items():
            if k.startswith('dated-') and nm in DATED_Y:
                P[nm] = (v, ('library, blind (released <= Y)' if DATED_Y[nm] <= int(k[6:]) else 'library, released after Y')
                         + ', bin average')
            else:
                P[nm] = (v, 'library')
        refv = P[ref.split(':', 1)[1]][0] if ref.split(':', 1)[1] in P else None
        md += [f'## {k}: {desc}', '', f'{len(T)} rows, {len(np.unique(nid(T.Z, T.A)))} nuclei; weighting: {wt}'
               + (f'; uncovered rows count as {miss} dex' if miss else '') + f"; reference: {ref.split(':', 1)[1]}", '']
        for sn, m in subsets(T):
            Tm = T[m].reset_index(drop=True)
            res = []
            for nm, (v, kind) in P.items():
                r = score_entry(Tm, k, v[m], None if refv is None else refv[m])
                if r['covered'] == 0:
                    continue
                r.update(track=k, subset=sn, entry=nm, kind=kind); res.append(r); rows.append(r)
            res.sort(key=lambda r: (r['covered'] < r['rows_total'] * 0.5, r.get('rms', 9)))
            md += [f'### {sn}' if sn != 'all' else '### all rows', '',
                   '| # | entry | kind | rows | rms [95 % CI] | bias | Δ vs reference [95 % CI] (rows) |', '|---|---|---|---|---|---|---|']
            for i, r in enumerate(res, 1):
                d = (f"{r['delta_vs_ref']:+.4f} [{r['delta_ci'][0]:+.4f}, {r['delta_ci'][1]:+.4f}] ({r['paired_rows']})"
                     if 'delta_vs_ref' in r else '—')
                md.append(f"| {i} | {r['entry']} | {r['kind']} | {r['covered']}/{r['rows_total']} | {fmt_ci(r)} | "
                          f"{r.get('bias', float('nan')):+.3f} | {d} |")
            md.append('')
    pd.DataFrame(rows).to_csv(out / 'leaderboard.csv', index=False)
    (out / 'leaderboard.json').write_text(json.dumps(rows, indent=1) + '\n')
    (out / 'LEADERBOARD.md').write_text('\n'.join(md) + '\n')
    print(f'-> {out}/LEADERBOARD.md, leaderboard.csv, leaderboard.json')


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest='cmd', required=True)
    p = sp.add_parser('tracks'); p.add_argument('--write', action='store_true', help='write tracks/MANIFEST.json')
    p.add_argument('--track', default='all', help="'all', an id, a comma list, or 'dated'")
    p = sp.add_parser('export'); p.add_argument('--track', required=True); p.add_argument('--out', required=True)
    for nm in ('score', 'leaderboard'):
        p = sp.add_parser(nm)
        p.add_argument('--track', default='all')
        p.add_argument('--evaluated', help='directory of staged library grids (default INCOGNITA_EVALUATED)')
        p.add_argument('--dated-library', help='bin-average library table for the dated tracks (uv run python -m incognita.bench.place_dated; '
                                               f'default ${DATED_LIBRARY_ENV})')
        if nm == 'score':
            p.add_argument('--csv'); p.add_argument('--name')
            p.add_argument('--library', nargs='*', help='staged grid keys, e.g. tendl2025 endfb81')
            p.add_argument('--endf', help='directory of ENDF-6 or PENDF files')
            p.add_argument('--njoy', default=os.environ.get('INCOGNITA_NJOY'), help='NJOY2016 executable for RECONR')
        else:
            p.add_argument('--out', default='docs/release/bench')
    a = ap.parse_args(argv)
    {'tracks': cmd_tracks, 'export': cmd_export, 'score': cmd_score, 'leaderboard': cmd_leaderboard}[a.cmd](a)


if __name__ == '__main__':
    main()
