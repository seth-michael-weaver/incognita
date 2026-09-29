"""TERRA-CHANNELS arms (PREREG.md): R0 recipe, C1 global dE shape, C2 ridge, C3 shallow GBM, P1 global knob refit, P1C3."""
import numpy as np, pandas as pd
from scipy.optimize import minimize
from scipy import stats
from sklearn.linear_model import Ridge
from sklearn.preprocessing import SplineTransformer, StandardScaler
from sklearn.ensemble import HistGradientBoostingRegressor
from terra_common import KNOBS

CLIP = 1.0
LAMS = [0.1, 1, 3, 10, 30, 100]
RAW = ['I', 'A13', 'Z', 'A', 'ee', 'eo', 'oe', 'oo', 'resP', 'beta2', 'Sn', 'Sp', 'Qch', 'thr_nnp', 'shZ', 'shN', 'E', 'dE', 'EoT', 'slope']
MAIN = ['I', 'A13', 'ee', 'eo', 'oe', 'resP', 'absb2', 'Sn', 'Sp', 'Qch', 'shZ', 'shN']


def prep(d, ch):
    d = d.copy()
    d['resP'] = d['resZodd_np'] if ch == 'np' else d['resNodd_n2n']
    d['Qch'] = d['Q_' + ch]; d['absb2'] = d.beta2.abs().fillna(0.0); d['beta2'] = d.beta2.fillna(0.0)
    d['dEc'] = d.dE.clip(0, 15)
    return d


def weights(d):
    n = d.groupby('nid').nid.transform('size').to_numpy(float); return 1.0 / np.sqrt(n)


def target(d, base):
    return np.clip(d.y.to_numpy() - base, -CLIP, CLIP)


class Spl:
    def __init__(self, n_knots=5):
        self.s = SplineTransformer(n_knots=n_knots, degree=3, extrapolation='constant')
    def fit(self, x): self.s.fit(x.reshape(-1, 1)); return self
    def __call__(self, x): return self.s.transform(x.reshape(-1, 1))


# ---- C1 ----
class C1:
    def fit(self, d, base):
        self.sp = Spl(5).fit(d.dEc.to_numpy()); X = self.sp(d.dEc.to_numpy())
        self.m = Ridge(alpha=1.0).fit(X, target(d, base), sample_weight=weights(d)); return self
    def predict(self, d, base): return base + self.m.predict(self.sp(d.dEc.to_numpy()))


# ---- C2 ----
def c2_X(d, sp, sc=None):
    B = sp(d.dEc.to_numpy())[:, :4]
    M = d[MAIN].to_numpy(float)
    inter = np.concatenate([B * d[[c]].to_numpy(float) for c in ('I', 'A13', 'ee')], axis=1)
    X = np.concatenate([M, B, inter], axis=1)
    if sc is None: sc = StandardScaler().fit(X)
    return sc.transform(X), sc


class C2:
    def fit(self, d, base, inner=True):
        self.sp = Spl(4).fit(d.dEc.to_numpy())
        X, self.sc = c2_X(d, self.sp); t = target(d, base); w = weights(d)
        lam = 10.0
        if inner:
            grp = d.Z.to_numpy() % 4; best = None
            for L in LAMS:
                err = 0.0
                for g in range(4):
                    tr, te = grp != g, grp == g
                    if te.sum() == 0 or tr.sum() == 0: continue
                    m = Ridge(alpha=L).fit(X[tr], t[tr], sample_weight=w[tr]); err += np.sum(w[te] * (t[te] - m.predict(X[te])) ** 2)
                if best is None or err < best[0]: best = (err, L)
            lam = best[1]
        self.lam = lam; self.m = Ridge(alpha=lam).fit(X, t, sample_weight=w); return self
    def predict(self, d, base): return base + self.m.predict(c2_X(d, self.sp, self.sc)[0])


# ---- C3 ----
class C3:
    def fit(self, d, base):
        self.m = HistGradientBoostingRegressor(max_depth=3, learning_rate=0.05, max_iter=300, min_samples_leaf=40, l2_regularization=1.0, random_state=0)
        self.m.fit(d[RAW].to_numpy(float), target(d, base), sample_weight=weights(d)); return self
    def predict(self, d, base): return base + self.m.predict(d[RAW].to_numpy(float))


# ---- P1 ----
def p1_curve(d, th, base_col='l_nodata'):
    l0 = d.l_nodata.to_numpy(); out = d[base_col].to_numpy().copy()
    for (k, (alo, ahi, xlo, xm, xhi)), x in zip(KNOBS.items(), th):
        ylo, yhi = d['l_' + alo].to_numpy(), d['l_' + ahi].to_numpy()
        ok = np.isfinite(ylo) & np.isfinite(yhi)
        L0 = (x - xm) * (x - xhi) / ((xlo - xm) * (xlo - xhi)); L1 = (x - xlo) * (x - xhi) / ((xm - xlo) * (xm - xhi)); L2 = (x - xlo) * (x - xm) / ((xhi - xlo) * (xhi - xm))
        q = L0 * np.where(ok, ylo, l0) + L1 * l0 + L2 * np.where(ok, yhi, l0)
        out = out + (q - l0)
    return out


class P1:
    """Knob deltas are measured on the recipe runs (l_nodata vs knob arms) and added to base_col (l_nodata, or l_nd_sys for the twin)."""
    def __init__(self, base_col='l_nodata'): self.base_col = base_col
    def fit(self, d, base=None):
        w = weights(d); y = d.y.to_numpy(); bnds = [(v[2], v[4]) for v in KNOBS.values()]; x0 = [v[3] for v in KNOBS.values()]
        f = lambda th: float(np.sum(w * np.clip(y - p1_curve(d, th, self.base_col), -CLIP, CLIP) ** 2))
        r = minimize(f, x0, method='L-BFGS-B', bounds=bnds); self.th = r.x; return self
    def predict(self, d, base=None): return p1_curve(d, self.th, self.base_col)


class P1C3:
    def __init__(self, base_col='l_nodata'): self.base_col = base_col
    def fit(self, d, base=None):
        self.p = P1(self.base_col).fit(d); b = self.p.predict(d); self.c = C3().fit(d, b); return self
    def predict(self, d, base=None): return self.c.predict(d, self.p.predict(d))


ARMS = {'C1': C1, 'C2': C2, 'C3': C3, 'P1': P1, 'P1C3': P1C3}


def make(arm, base_col='l_nodata'):
    return ARMS[arm](base_col) if arm in ('P1', 'P1C3') else ARMS[arm]()


# ---- intervals ----
def sig(p, dE):
    s0, s1 = np.exp(p[0]), np.exp(p[1]); return np.sqrt(s0 ** 2 + s1 ** 2 * np.exp(-np.clip(dE, 0, None) / 2.0))


def fit_sigma(e, dE):
    def nll(p):
        nu = 2.0 + np.exp(p[2]); s = sig(p, dE); return -np.sum(stats.t.logpdf(e / s, nu) - np.log(s))
    r = minimize(nll, [np.log(0.15), np.log(0.3), np.log(3.0)], method='Nelder-Mead', options=dict(maxiter=4000, xatol=1e-6, fatol=1e-8))
    return r.x


def coverage(e, dE, p):
    nu = 2.0 + np.exp(p[2]); s = sig(p, dE)
    return float(np.mean(np.abs(e) <= stats.t.ppf(0.84134, nu) * s)), float(np.mean(np.abs(e) <= stats.t.ppf(0.975, nu) * s))


def rms(x): return float(np.sqrt(np.mean(np.square(x))))


def boot_diff(err_a, err_b, nid, n=2000, seed=20260923):
    """rms(a) - rms(b) with nucleus bootstrap 95 % CI."""
    rng = np.random.default_rng(seed); u = np.unique(nid); idx = {q: np.where(nid == q)[0] for q in u}
    sa, sb = {q: np.sum(err_a[idx[q]] ** 2) for q in u}, {q: np.sum(err_b[idx[q]] ** 2) for q in u}; cnt = {q: len(idx[q]) for q in u}
    out = []
    for _ in range(n):
        s = rng.choice(u, len(u)); N = sum(cnt[q] for q in s)
        out.append(np.sqrt(sum(sa[q] for q in s) / N) - np.sqrt(sum(sb[q] for q in s) / N))
    return rms(err_a) - rms(err_b), float(np.quantile(out, 0.025)), float(np.quantile(out, 0.975))
