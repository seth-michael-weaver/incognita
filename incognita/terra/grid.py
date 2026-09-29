"""TERRA (n,p) blind correction: prediction grid 1-20 MeV with 68 / 95 % intervals for unmeasured targets.

Release port of `terra_grid.py grid np` (frozen, MANIFEST_TERRA_CHANNELS.sha256). The frozen model (data/frozen_np.pkl,
C3 = shallow gradient boosting on top of the TENDL no-data recipe R0) and its interval (data/frozen_np.json) ship
unchanged; the script needs, per target, the engine's R0 curve ("nodata" arm) on the energy grid data/grid_terra.json.

  # 1. the engine's R0 curves (the TALYS port, TENDL no-data recipe, ~1 CPU-minute per target):
  uv run python scripts/bestfit/engine_curves.py --arm nodata --out $INCOGNITA_WORK/terra/grid/nodata \\
      --only "$(cat incognita/terra/data/grid_targets.txt)" --grid incognita/terra/data/grid_terra.json \\
      --cpus 0-3 --cc-cache ~/.cache/incognita-cc --no-ingredients
  # 2. the corrected predictions:
  uv run python -m incognita.terra.grid --out $INCOGNITA_WORK/terra/grid_np.parquet [--only 26-61,26-62]

NPFIX (2026-09-24): `--model e1` uses data/frozen_np_e1.{pkl,json} = the SAME C3 recipe re-derived on no-data curves at OUR E1
constant (1.0425; INDEPENDENCE), which is the ship-ready (n,p) correction. Its engine curves come from step 1 WITHOUT `--e1 stock`
(`--arm nodata` applies 1.0425 by default). `--model stock` (default, unchanged) is the frozen terra model on stock-E1 curves.
The e1 grid adds `element_measured` (an isotope of the element has (n,p) data in training) as a regime flag.

Differences from the frozen script: the "measured" set and the training ranges of I and Z are read from
data/train_domain_np.json (derived from the frozen DEV and vault row files, which contain EXFOR values and are not
redistributed) instead of from those files; targets whose engine curve is missing are skipped and counted.
"""
import argparse
import json
import os
import pickle
import sys

import numpy as np
import pandas as pd
from scipy import stats

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)                      # the frozen pickle refers to the top-level module 'terra_model'
import terra_common as tc                       # noqa: E402
from terra_model import prep, sig               # noqa: E402


def targets(path):
    return [tuple(map(int, s.split('-'))) for s in open(path).read().split(',')]


def grid(ch, out, root, only=None, model='stock'):
    tag = '' if model == 'stock' else '_e1'
    F = pickle.load(open(tc.T + f'frozen_{ch}{tag}.pkl', 'rb'))
    J = json.load(open(tc.T + f'frozen_{ch}{tag}.json'))
    p = J['sigma_params']
    nu = 2 + np.exp(p[2])
    dom = json.load(open(tc.T + f'train_domain_{ch}.json'))
    Irng, Zrng = tuple(dom['I_range']), tuple(dom['Z_range'])
    meas = {tuple(x) for x in dom['measured']}
    meas_z = set(J.get('train_Z', [z for z, _ in meas]))   # elements with an isotope in the model's training rows
    tl = only or targets(tc.T + 'grid_targets.txt')
    res, missing = [], 0
    for z, a in tl:
        if (z, a) in meas:
            continue
        c = tc.curve('nodata', z, a, ch, root)
        if c is None:
            missing += 1
            continue
        e = c[0][c[0] >= 1e6]
        s = c[1][c[0] >= 1e6]
        f = tc.nuclide_features(z, a)
        d = pd.DataFrame({'e_ev': e})
        d = d.assign(**{k: v for k, v in f.items()})
        d['E'] = d.e_ev / 1e6
        d['dE'] = d.E - f['thr_' + ch]
        d['EoT'] = d.E / max(f['thr_' + ch], 0.1)
        d['nid'] = z * 1000 + a
        d['slope'] = tc.logslope('nodata', z, a, ch, e, root)
        with np.errstate(all='ignore'):
            d['l_nodata'] = np.where(s > 0, np.log10(s), np.nan)
        d = prep(d, ch)
        k = np.isfinite(d.l_nodata.to_numpy())
        pr = np.full(len(d), np.nan)
        if k.sum():
            pr[k] = F['model'].predict(d[k].reset_index(drop=True), d.l_nodata.to_numpy()[k])
        sg = sig(p, d.dE.to_numpy())
        t68, t95 = stats.t.ppf(0.84134, nu) * sg, stats.t.ppf(0.975, nu) * sg
        res.append(pd.DataFrame({'Z': z, 'A': a, 'E_MeV': d.E, 'recipe_mb': s, 'pred_mb': 10 ** pr,
                                 'lo68_mb': 10 ** (pr - t68), 'hi68_mb': 10 ** (pr + t68),
                                 'lo95_mb': 10 ** (pr - t95), 'hi95_mb': 10 ** (pr + t95), 'sigma_dex': sg,
                                 'below_engine_threshold': ~k, 'tendl_fitted_other_data': tc.tendl_fitted(z, a),
                                 'outside_training_asymmetry': not (Irng[0] <= f['I'] <= Irng[1]),
                                 'outside_training_Z': not (Zrng[0] <= z <= Zrng[1])}))
        if model == 'e1':
            res[-1]['element_measured'] = z in meas_z
            res[-1]['model'] = 'C3-e1 (frozen_np_e1.pkl; recipe = nodata at E1 1.0425)'
    if not res:
        raise SystemExit(f'no engine curves found under {root}nodata/ (missing for {missing} targets); run step 1 first')
    g = pd.concat(res, ignore_index=True)
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    g.to_parquet(out)
    print(ch, g.groupby(['Z', 'A']).ngroups, 'targets', len(g), 'points; engine curve missing for', missing,
          'targets; outside training asymmetry:', int(g.drop_duplicates(['Z', 'A']).outside_training_asymmetry.sum()))
    return g


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--channel', default='np', choices=['np'], help='only (n,p) ships; (n,2n) did not pass (BLIND_CHANNELS.md)')
    ap.add_argument('--root', default=None, help='engine-curve root holding nodata/ZZZ_AAA.npz (default $TERRA_CAP/grid/)')
    ap.add_argument('--out', default=None, help='default $INCOGNITA_WORK/terra/grid_np.parquet')
    ap.add_argument('--only', default=None, help='comma list Z-A (default: data/grid_targets.txt)')
    ap.add_argument('--model', default='stock', choices=['stock', 'e1'], help="e1 = the NPFIX re-derivation on OUR E1 constant (ships); stock = frozen terra C3 (v0.1)")
    a = ap.parse_args(argv)
    root = (a.root.rstrip('/') + '/') if a.root else tc.CAP + 'grid/'
    only = [tuple(map(int, s.split('-'))) for s in a.only.split(',')] if a.only else None
    grid(a.channel, a.out or tc.CAP + f'grid_{a.channel}.parquet', root, only, a.model)


if __name__ == '__main__':
    main()
