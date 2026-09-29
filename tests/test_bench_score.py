"""The open benchmark reproduces the published tables from the frozen tracks, and the registry chain verifies.

Needs only files in the repository (docs/release/exam, incognita/bench/data, docs/registry). The rival-library
columns need staged library grids and are checked by `python -m incognita.bench.score leaderboard` instead.
"""
import hashlib
import json
import shutil

import numpy as np
import pytest

from incognita.bench import registry as R
from incognita.bench import score as S


def _r(track, entry, sub='all'):
    T = S.build(track)
    m = np.ones(len(T), bool) if sub == 'all' else T[f'sub:{sub}'].to_numpy(bool)
    ref = S.ref_values(T, track, {})
    return S.score_entry(T[m].reset_index(drop=True), track, T[f'entry:{entry}'].to_numpy(float)[m],
                         None if ref is None else ref[m])


def test_manifest_matches_tracks():
    man = json.loads((S.HERE / 'tracks' / 'MANIFEST.json').read_text())
    for k in S.TRACKS:
        T = S.build(k)
        assert man[k]['rows'] == len(T)
        assert man[k]['rows_sha256'] == S.rows_sha(T)
        assert hashlib.sha256((S.HERE / 'tracks' / 'rows' / f'{k}.csv').read_bytes()).hexdigest() == man[k]['rows_sha256']


def test_capture_blind_table():     # docs/release/expected/capblind/CAPTURE_BLIND.md
    r = _r('capture-heldout', 'INCOGNITA capture, D0 withheld (headline)')
    # the shipped model on DEV folds 0-5 (SHIPEXAMS exam file of f165e5a3)
    assert (r['rows'], r['nuclei']) == (1947, 122)
    assert round(r['rms'], 4) == 0.1765 and round(r['ref_rms_same_rows'], 4) == 0.1898
    assert [round(x, 4) for x in r['delta_ci']] == [-0.0229, -0.0035]
    assert round(_r('capture-heldout', 'INCOGNITA capture, measured D0 used')['rms'], 4) == 0.1569
    assert round(_r('capture-heldout', 'INCOGNITA capture, measured D0 used', 'well_measured (trust >= 1)')['rms'], 4) == 0.1202
    r = _r('capture-nostructure', 'INCOGNITA capture, no structure data (STRIP)')
    assert (r['rows'], round(r['rms'], 4), round(r['ref_rms_same_rows'], 4)) == (1966, 0.2101, 0.2042)


def test_retro_and_na_tables():     # expected/retro/RETRO.md, expected/na/NA_V1.md
    r = _r('capture-retro', 'INCOGNITA capture trained on data up to year Y')
    assert (r['rows'], round(r['rms'], 4), round(r['ref_rms_same_rows'], 4)) == (286, 0.1373, 0.1728)
    assert [round(x, 4) for x in r['delta_ci']] == [-0.0764, 0.0193]
    for track, v1, default in (('na-pickup', 0.3946, 0.5547), ('na-heprod', 0.2365, 0.3079), ('na-neverread', 0.2854, 0.4112)):
        r = _r(track, 'INCOGNITA (n,a) v1 recipe')
        assert (round(r['rms'], 4), round(r['ref_rms_same_rows'], 4)) == (v1, default)


def test_csv_submission_roundtrip(tmp_path):
    T = S.build('capture-heldout')
    p = tmp_path / 'sub.csv'
    v = 10 ** T['entry:INCOGNITA capture, D0 withheld (headline)']
    p.write_text('track,row,value_b\n' + ''.join(f'capture-heldout,{i},{x:.15g}\n' for i, x in zip(T.row, v)))
    got, h = S.csv_entry(T, 'capture-heldout', p)
    assert h is None and round(S.score_entry(T, 'capture-heldout', got)['rms'], 4) == 0.1765


def test_registry_chain(tmp_path, monkeypatch):
    assert R.verify() == 0
    bad = tmp_path / 'CHAIN.jsonl'
    lines = R.CHAIN.read_text().splitlines()
    L = json.loads(lines[1]); L['n_entries'] += 1
    bad.write_text('\n'.join([lines[0], json.dumps(L), lines[2]]) + '\n')
    monkeypatch.setattr(R, 'CHAIN', bad)
    assert R.verify() == 1


def test_endf_reader_matches_staged_grid(tmp_path):
    from incognita import config
    raw = config.main_dir() / 'raw' / 'endf' / 'endfb81' / 'n' / 'n-069_Tm_169.endf'
    njoy = shutil.which('njoy')
    if not raw.exists() or not (config.evaluated_dir() / 'endfb81.parquet').exists() or not njoy:
        pytest.skip('needs the raw ENDF/B-VIII.1 file, the staged grid and NJOY2016')
    cur = S.endf_library([raw], njoy=njoy, workdir=tmp_path)
    stg = S.staged_library('endfb81')
    T = S.build('ch-capture')
    a, b = S.predict(T, cur), S.predict(T, stg)
    m = np.isfinite(a)
    assert m.sum() > 0 and np.nanmax(np.abs(a[m] - b[m])) < 1e-9
