"""incognita.uq.calibration_report: coverage, PIT, ECE and sharpness on synthetic data with a known answer."""
import numpy as np
import pandas as pd
from scipy import stats

from incognita.uq import calibration_report as cr


def _table(n=6000, scale_true=1.0, nu=np.inf, seed=0):
    rng = np.random.default_rng(seed)
    sig = rng.uniform(0.05, 0.3, n)                            # heteroscedastic: the width should rank the errors
    z = rng.standard_normal(n) if not np.isfinite(nu) else rng.standard_t(nu, n)
    q68 = stats.norm.ppf(0.84) if not np.isfinite(nu) else stats.t.ppf(0.84, nu)
    q95 = stats.norm.ppf(0.975) if not np.isfinite(nu) else stats.t.ppf(0.975, nu)
    return pd.DataFrame(dict(nuclide_id=rng.integers(0, 120, n).astype(str), energy_ev=10 ** rng.uniform(2, 7.3, n),
                             err=z * sig * scale_true, h68=q68 * sig, h95=q95 * sig))


def test_calibrated_gaussian():
    s = cr.summarise(cr.prepare(_table()), "nuclide_id", 300)
    assert abs(s["cov68"] - 68) < 2.5 and abs(s["cov95"] - 95) < 1.5
    assert s["ece"] < 2.0
    assert s["cov68_ci"][0] < s["cov68"] < s["cov68_ci"][1]
    assert s["sharpness"] > 3                                  # widths span x6, so the top quartile's rms is several x the bottom's
    h = np.array(s["pit_hist"]); assert h.min() > 0.8 * h.mean() and h.max() < 1.2 * h.mean()


def test_too_narrow_is_detected():
    s = cr.summarise(cr.prepare(_table(scale_true=1.6)), "nuclide_id", 300)
    assert s["cov68"] < 50 and s["cov95"] < 85 and s["ece"] > 10
    h = s["pit_hist"]; assert h[0] > 1.5 * h[5] and h[-1] > 1.5 * h[5]      # U-shaped PIT


def test_student_t_from_two_quantiles():
    d = cr.prepare(_table(nu=2.5))
    assert np.allclose(d["nu"], 2.5, rtol=0.02)                 # nu recovered from h95 / h68
    s = cr.summarise(d, "nuclide_id", 200)
    assert abs(s["cov68"] - 68) < 2.5 and abs(s["cov95"] - 95) < 1.5 and s["ece"] < 2.5


def test_sigma_input_and_bands():
    t = _table(); t["sigma"] = t.h68 / stats.norm.ppf(0.84); t = t.drop(columns=["h68", "h95"])
    txt, rows = cr.report(cr.prepare(t), "t", [], "nuclide_id", 100)
    names = [r["stratum"] for r in rows]
    assert names[0] == "all" and "10-100 keV" in names and ">= 5 MeV" in names
    assert "| all |" in txt
