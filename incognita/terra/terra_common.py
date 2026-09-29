"""TERRA-CHANNELS shared code (PREREG.md): masses and physics features, engine and library lookups.

Release port of the frozen terra_common.py (MANIFEST_TERRA_CHANNELS.sha256): only the locations changed
(environment variables instead of lab paths; the TENDL-2025 "fitted" flags come from data/tendl2025_fitted.csv,
reduced from the full keyword table with the same PREREG rule). Every computation is the frozen one.

  TERRA_DATA   frozen model files and metadata (default: this package's data/ directory)
  TERRA_CAP    engine curves (default: $INCOGNITA_WORK/terra/)
  TERRA_ROWS   channel exam rows built from EXFOR (only for the DEV / vault exam, not for the grid)
  TALYS_DIR    TALYS structure database (masses)
"""
import glob, hashlib, json, os, sys
import numpy as np, pandas as pd

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(_HERE)))
from incognita import config  # noqa: E402

T = os.environ.get('TERRA_DATA', os.path.join(_HERE, 'data')) + '/'
CAP = os.environ.get('TERRA_CAP', str(config.work_dir() / 'terra')) + '/'
ROWS = os.environ.get('TERRA_ROWS', str(config.inputs_dir() / 'channels_v0' / 'rows_A1.parquet'))


def interp(e_model, s_model, e):
    """sigma at e: log-log where the bracketing model points are positive, else linear sigma in log E."""
    le, lm = np.log(e), np.log(e_model)
    lin = np.interp(le, lm, s_model)
    pos = s_model > 0
    out = lin
    if pos.sum() >= 2:
        ll = np.exp(np.interp(le, lm[pos], np.log(s_model[pos])))
        i = np.clip(np.searchsorted(lm, le), 1, len(lm) - 1)
        ok = pos[i] & pos[i - 1]
        out = np.where(ok, ll, lin)
    return out


KEY = {'n2n': 'ch_xs200000', 'np': 'ch_xs010000'}
MT = {'n2n': 16, 'np': 103}
LIBS = (('TENDL-2025', 'tendl2025'), ('ENDF/B-VIII.1', 'endfb81'), ('JENDL-5', 'jendl5'))
G = np.logspace(-5, np.log10(2e7), 3000)
KNOBS = {'m2': ('m2_080', 'm2_125', 0.8, 1.0, 1.25), 'rvp': ('rvp_097', 'rvp_103', 0.97, 1.0, 1.03), 'pc': ('pc09', 'pc15', 9.0, 12.0, 15.0)}
ARMS = ['nodata', 'm2_080', 'm2_125', 'rvp_097', 'rvp_103', 'pc09', 'pc15', 'default', 'nd_sys']
DN, DP = 8.0713181, 7.2889711  # mass excesses of n and H-1, MeV
MAGIC = np.array([2, 8, 20, 28, 50, 82, 126, 184])


def h5(s):
    return int(hashlib.blake2b(s.encode(), digest_size=8).hexdigest(), 16) % 5


def in_vault(z):
    return h5(f'terra-2026-09-23:{int(z)}') == 0


def dev_fold(z):
    return h5(f'terra-dev:{int(z)}')


def region(z):
    return 'Fe-Sn' if z <= 50 else ('Sn-Pb' if z <= 82 else 'heavy')


# ---- masses (TALYS structure: AME2020, else HFB) and HFB beta2 ----
_M, _B = {}, {}
def _load_masses():
    if _M: return
    S = str(config.talys_dir() / 'structure' / 'masses') + '/'
    for f in glob.glob(S + 'hfb/*.mass'):
        for ln in open(f):
            p = ln.split()
            try: z, a, me, b2 = int(p[0]), int(p[1]), float(p[3]), float(p[4]); _M[(z, a)] = me; _B[(z, a)] = b2
            except Exception: pass
    for f in glob.glob(S + 'ame2020/*.mass'):
        for ln in open(f):
            p = ln.split()
            try: _M[(int(p[0]), int(p[1]))] = float(p[3])
            except Exception: pass


def mex(z, a):
    _load_masses(); return _M.get((int(z), int(a)), np.nan)


def beta2(z, a):
    _load_masses(); return _B.get((int(z), int(a)), np.nan)


def nuclide_features(z, a):
    z, a = int(z), int(a); n = a - z
    sn = mex(z, a - 1) + DN - mex(z, a); sp = mex(z - 1, a - 1) + DP - mex(z, a)
    q2n = -sn; qnp = DN + mex(z, a) - DP - mex(z - 1, a)
    dz = np.min(np.abs(MAGIC - z)); dn = np.min(np.abs(MAGIC - n))
    return dict(Z=z, A=a, N=n, I=(n - z) / a, A13=a ** (1 / 3), Sn=sn, Sp=sp, Q_n2n=q2n, Q_np=qnp,
                thr_n2n=max(0.0, -q2n) * (a + 1) / a, thr_np=max(0.0, -qnp) * (a + 1) / a, thr_nnp=max(0.0, sp) * (a + 1) / a,
                ee=int(z % 2 == 0 and n % 2 == 0), eo=int(z % 2 == 0 and n % 2 == 1), oe=int(z % 2 == 1 and n % 2 == 0), oo=int(z % 2 == 1 and n % 2 == 1),
                resZodd_np=int((z - 1) % 2 == 1), resNodd_n2n=int((n - 1) % 2 == 1), beta2=beta2(z, a),
                shZ=np.exp(-dz / 2), shN=np.exp(-dn / 2))


# ---- engine curves ----
_E, _C = {}, {}
def _compact(root, arm):
    p = f'{root}curves_{arm}.parquet'
    if (root, arm) not in _C:
        _C[(root, arm)] = {(int(r.Z), int(r.A)): r for r in pd.read_parquet(p).itertuples()} if os.path.exists(p) else None
    return _C[(root, arm)]


def curve(arm, z, a, ch, root=None):
    root = root or CAP + 'meas/'
    k = (root, arm, z, a, ch)
    if k not in _E:
        p = f'{root}{arm}/{z:03d}_{a:03d}.npz'; cc = _compact(root, arm)
        if cc is not None:
            r = cc.get((z, a)); _E[k] = None if r is None else (np.asarray(r.e_ev, float), np.asarray(getattr(r, ch), float))
        elif os.path.exists(p):
            f = np.load(p, allow_pickle=True); _E[k] = (np.asarray(f['e_ev'], float), np.asarray(f[KEY[ch]], float) if KEY[ch] in f.files else np.zeros(len(f['e_ev'])))
        else:
            _E[k] = None
    return _E[k]


def eng_at(arm, z, a, ch, e, root=None):
    c = curve(arm, int(z), int(a), ch, root)
    if c is None: return np.full(np.shape(e), np.nan)
    v = interp(c[0], c[1], np.atleast_1d(np.asarray(e, float)))
    v = np.where(np.atleast_1d(e) < c[0][0], np.nan, v)
    return v


def logslope(arm, z, a, ch, e, root=None):
    lo = eng_at(arm, z, a, ch, np.asarray(e) * 0.97, root); hi = eng_at(arm, z, a, ch, np.asarray(e) * 1.03, root)
    with np.errstate(all='ignore'):
        s = (np.log(np.maximum(hi, 1e-30)) - np.log(np.maximum(lo, 1e-30))) / np.log(1.03 / 0.97)
    return np.clip(np.nan_to_num(s, nan=0.0), -50, 50)


# ---- libraries ----
_L = {}
def lib_table(ch):
    if ch not in _L:
        # the frozen code read lib_n2n_np.parquet, a slice of the staged grids below (not redistributed)
        _L[ch] = {}
        for nm, stem in LIBS:
            dl = pd.read_parquet(config.evaluated_dir() / f'{stem}.parquet', columns=['Z', 'N', 'iso', 'mt', 'values_b'])
            dl = dl[(dl.iso == 0) & (dl.mt == MT[ch])]
            _L[ch][nm] = {(int(x.Z), int(x.Z + x.N)): np.asarray(x.values_b, float) * 1e3 for x in dl.itertuples()}
        assert all(len(v) == len(G) for t in _L[ch].values() for v in t.values())
    return _L[ch]


def lib_at(ch, nm, z, a, e):
    y = lib_table(ch)[nm].get((int(z), int(a)))
    if y is None: return np.nan
    ok = y > 0
    return float(np.exp(np.interp(np.log(e), np.log(G[ok]), np.log(y[ok])))) if ok.sum() > 2 else np.nan


# ---- TENDL-2025 fitted / unfitted (PREREG definition) ----
GAMMA_FISSION_ONLY = {'wtable', 's2adjust', 'ngfit', 'gamgam', 'egr', 'rgamma', 'fisbar', 'fishw', 'fismodel',
                      'class2', 'class2width', 'fisbaradjust'}
_TF = None
def tendl_fitted(z, a):
    """True when TENDL-2025 adjusted any parameter other than gamma / fission ones for this target (PREREG rule)."""
    global _TF
    if _TF is None:
        d = pd.read_csv(T + 'tendl2025_fitted.csv')
        _TF = {(int(r.Z), int(r.A)): bool(r.fitted) for r in d.itertuples()}
    return _TF.get((int(z), int(a)), False)


def load_rows(ch):
    d = pd.read_parquet(ROWS)
    d = d[(d.channel == ch) & (d.A > 0) & (d.data_mb > 0)].reset_index(drop=True)
    d['vault'] = d.Z.map(in_vault); d['fold'] = d.Z.map(dev_fold); d['region'] = d.Z.map(region); d['nid'] = d.Z * 1000 + d.A
    return d[['channel', 'Z', 'A', 'nid', 'series', 'e_ev', 'n_pts', 'data_mb', 'year', 'vault', 'fold', 'region']]


def build_table(ch, root=None, rows=None):
    """Rows + features + engine values for every arm (log10) + libraries."""
    d = load_rows(ch) if rows is None else rows
    F = pd.DataFrame([nuclide_features(z, a) for z, a in zip(d.Z, d.A)])
    d = pd.concat([d.reset_index(drop=True), F.drop(columns=['Z', 'A'])], axis=1)
    d['E'] = d.e_ev / 1e6
    thr = d['thr_' + ch]
    d['dE'] = d.E - thr; d['EoT'] = d.E / np.maximum(thr, 0.1)
    for arm in ARMS:
        vals = np.full(len(d), np.nan)
        for (z, a), idx in d.groupby(['Z', 'A']).groups.items():
            vals[idx] = eng_at(arm, z, a, ch, d.loc[idx, 'e_ev'].to_numpy(), root)
        with np.errstate(all='ignore'):
            d['l_' + arm] = np.where(vals > 0, np.log10(vals), np.nan)
    sl = np.zeros(len(d))
    for (z, a), idx in d.groupby(['Z', 'A']).groups.items():
        sl[idx] = logslope('nodata', z, a, ch, d.loc[idx, 'e_ev'].to_numpy(), root)
    d['slope'] = sl
    for nm, _ in LIBS:
        d[nm] = [lib_at(ch, nm, z, a, e) for z, a, e in zip(d.Z, d.A, d.e_ev)]
    d['tendl_fitted'] = [tendl_fitted(z, a) for z, a in zip(d.Z, d.A)]
    d['y'] = np.log10(d.data_mb)
    return d
