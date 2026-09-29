"""Statistics of a REAL resolved-resonance ladder (ENDF MF2), beyond its means.

`ladder.py` builds synthetic ladders from average parameters, and `data.ingest.endf.ladder_stats`
reduces a real MF2 ladder to its means (D0, S0, <Gg>). Everything the Hauser-Feshbach machinery
*assumes* about the ladder -- Porter-Thomas reduced neutron widths, GOE spacings, a local spacing
that follows the level density -- lives in the distributions those means throw away. This module
measures them on the s-wave part of an evaluated ladder:

* :func:`porter_thomas`   chi^2_nu fit of the reduced widths x = g Gn0 = g Gn / sqrt(E), left-
                          truncated at a detection threshold, and the fraction of the full
                          Porter-Thomas population below that threshold (the missed levels, and
                          the share of the s-wave strength they carry)
* :func:`spacing_slope`   D(E) inside the resolved region: ML fit of an exponential level
                          density exp(b E / L) to the observed staircase, reported as the change
                          of ln D across the region, against the level-density model's expectation
* :func:`spacing_ratio`   the nearest-neighbour spacing ratio <r~> (GOE 0.5307, Poisson 0.3863)
                          of the whole s-wave ladder and of each evaluator-assigned J sequence,
                          with the expectation for the number of s-wave spin sequences the target
                          spin allows (J-mixing diagnostic)

None of the three is a function of D0 and <Gg> alone.
"""
from __future__ import annotations

import math
from functools import lru_cache
from typing import Any

import numpy as np
from scipy import optimize, stats

R_GOE = 0.5307
R_POISSON = 0.3863


# --------------------------------------------------------------------------------------------
# extraction
# --------------------------------------------------------------------------------------------

def s_wave_ladder(rows: list[dict[str, Any]]) -> dict[str, Any] | None:
    """The l = 0 resolved resonances of one nuclide's MF2 rows (one library, one isotope).

    Same channel conventions as ``data.ingest.endf.ladder_stats``: LRF 1-3 take the l = 0
    groups' ER / GN / AJ; LRF 7 takes particle pair 2 with L = 0 as the neutron channel (widths
    summed over such channels, absolute values). Only 0 < ER <= EH counts. Returns energies
    (sorted), GN, AJ (NaN where unassigned), EH, the lowest EL, target spin, and AWRI.
    """
    er_all, gn_all, aj_all = [], [], []
    eh = el = spi = awri = math.nan
    for r in rows:
        if int(r.get("lru", 0)) != 1:
            continue
        names = list(r.get("param_names") or [])
        d = dict(zip(names, r.get("param_values") or [], strict=False))
        shapes = dict(zip(names, r.get("param_shape") or [], strict=False))
        e_hi = float(r.get("eh_ev") or math.nan)
        eh = e_hi if math.isnan(eh) else max(eh, e_hi)
        e_lo = float(r.get("el_ev") or 0.0)
        el = e_lo if math.isnan(el) else min(el, e_lo)
        if r.get("spi") is not None and np.isfinite(r.get("spi")):
            spi = float(r["spi"])
        if r.get("awri") is not None and np.isfinite(r.get("awri")):
            awri = float(r["awri"])
        if int(r.get("lrf", 0)) == 7:
            if not {"GAM", "PPI", "ER"} <= d.keys():
                continue
            gam = np.asarray(d["GAM"], float).reshape(shapes["GAM"])
            ppi = np.asarray(d["PPI"], np.int64)
            lch = np.asarray(d.get("L", np.zeros_like(ppi)), np.int64)
            idx = np.flatnonzero((ppi == 2) & (lch == 0))
            if idx.size == 0:
                continue
            er = np.asarray(d["ER"], float)
            gn = np.abs(gam[idx]).sum(axis=0)
            aj = np.full(er.size, abs(float(r.get("j") or math.nan)))
        else:
            if r.get("l") != 0 or "ER" not in d or "GN" not in d:
                continue
            er = np.asarray(d["ER"], float)
            gn = np.abs(np.asarray(d["GN"], float))
            aj = np.abs(np.asarray(d.get("AJ", np.full(er.size, np.nan)), float))
        n = min(er.size, gn.size, aj.size)
        er, gn, aj = er[:n], gn[:n], aj[:n]
        m = (er > 0.0) & (er <= e_hi) & (gn > 0.0)
        er_all.append(er[m])
        gn_all.append(gn[m])
        aj_all.append(aj[m])
    if not er_all or not np.isfinite(eh):
        return None
    er = np.concatenate(er_all)
    o = np.argsort(er)
    return {"er": er[o], "gn": np.concatenate(gn_all)[o], "aj": np.concatenate(aj_all)[o],
            "eh": float(eh), "el": float(el), "spi": spi, "awri": awri}


def s_wave_spins(spi: float) -> list[float]:
    """Compound spins an s-wave neutron reaches on a target of spin ``spi``."""
    if not np.isfinite(spi):
        return []
    return sorted({abs(spi - 0.5), spi + 0.5})


def g_factor(aj: np.ndarray, spi: float) -> np.ndarray:
    """g = (2J+1) / (2(2I+1)); a J that s-waves cannot reach (unassigned, 0, or a p-wave spin
    written into an l = 0 group) gets the level-density-weighted mean g of the allowed pair."""
    js = s_wave_spins(spi)
    if not js:
        return np.full(aj.shape, np.nan)
    gj = np.array([(2 * j + 1) / (2 * (2 * spi + 1)) for j in js])
    wj = np.array([2 * j + 1 for j in js])
    g_mean = float((gj * wj).sum() / wj.sum())
    ok = np.zeros(aj.shape, bool)
    for j in js:
        ok |= np.isclose(aj, j)
    return np.where(ok, (2 * aj + 1) / (2 * (2 * spi + 1)), g_mean)


# --------------------------------------------------------------------------------------------
# (i) Porter-Thomas
# --------------------------------------------------------------------------------------------

def _chi2_trunc_nll(params, x, t):
    """-log L of x ~ mu chi^2_nu / nu, left-truncated at t (x > t)."""
    lnu, lmu = params
    nu, mu = math.exp(lnu), math.exp(lmu)
    scale = mu / nu
    lp = stats.chi2.logpdf(x / scale, nu) - math.log(scale)
    tail = stats.chi2.sf(t / scale, nu) if t > 0 else 1.0
    if not tail > 0:
        return 1e12
    return float(-(lp.sum() - x.size * math.log(tail)))


def porter_thomas(x: np.ndarray, threshold_quantile: float = 0.2) -> dict[str, float]:
    """Truncated chi^2 fit of reduced widths ``x`` (any positive scale).

    The detection threshold t is the ``threshold_quantile`` of the observed x, constant in the
    reduced width (a Gn threshold growing as sqrt(E), the Doppler scaling). Above t the fit is
    unbiased whatever was missed below it, provided the true threshold is <= t.

    Returns ``nu_free`` (nu and mean fitted jointly above t), ``nu_untruncated`` (plain ML on all
    x -- biased UP by missed small widths), and with nu = 1 fixed (the Porter-Thomas assumption)
    ``mu_pt`` the fitted population mean, ``f_miss`` = 1 - n_obs / n_true where n_true =
    n_above / P(x > t), and ``strength_miss`` the fraction of the population's summed width
    carried below t (P(chi^2_3 < t / mu) for nu = 1).
    """
    x = np.asarray(x, float)
    x = x[np.isfinite(x) & (x > 0)]
    out = {k: math.nan for k in ("nu_free", "nu_untruncated", "mu_pt", "threshold", "f_miss",
                                  "strength_miss", "frac_below_threshold_obs")}
    out["n"] = int(x.size)
    if x.size < 10:
        return out
    x = x / np.mean(x)                      # scale-free; mu is reported in units of <x_obs>
    t = float(np.quantile(x, threshold_quantile))
    above = x[x > t]
    out["threshold"] = t
    out["frac_below_threshold_obs"] = float(np.mean(x <= t))
    # nu free, above threshold
    r = optimize.minimize(_chi2_trunc_nll, [0.0, math.log(np.mean(above))], args=(above, t),
                          method="Nelder-Mead", options={"xatol": 1e-5, "fatol": 1e-7,
                                                         "maxiter": 4000})
    out["nu_free"] = float(min(math.exp(r.x[0]), 100.0))
    # untruncated
    try:
        nu_u, _, _ = stats.gamma.fit(x, floc=0.0)
        out["nu_untruncated"] = float(2.0 * nu_u)
    except Exception:  # pragma: no cover - scipy edge cases
        pass
    # nu = 1 fixed: mu from the truncated likelihood
    r1 = optimize.minimize_scalar(lambda lm: _chi2_trunc_nll([0.0, lm], above, t),
                                  bounds=(math.log(1e-4), math.log(1e3)), method="bounded")
    mu = float(math.exp(r1.x))
    p_above = float(stats.chi2.sf(t / mu, 1))
    n_true = above.size / p_above
    out["mu_pt"] = mu
    out["f_miss"] = float(max(0.0, 1.0 - x.size / n_true))
    out["strength_miss"] = float(stats.chi2.cdf(t / mu, 3))
    return out


# --------------------------------------------------------------------------------------------
# (ii) local mean spacing vs energy
# --------------------------------------------------------------------------------------------

def spacing_slope(er: np.ndarray, e0: float, e1: float) -> dict[str, float]:
    """ML fit of a level density rho(E) proportional to exp(b (E - e0) / (e1 - e0)) on [e0, e1].

    ``dlnD`` = -b is the change of ln D across the region (0 = constant spacing), with its
    Poisson standard error (GOE rigidity makes the true error smaller: this is conservative).
    """
    er = np.asarray(er, float)
    er = er[(er >= e0) & (er <= e1)]
    n = er.size
    if n < 10 or not e1 > e0:
        return {"dlnD": math.nan, "dlnD_se": math.nan, "n": int(n)}
    u = (er - e0) / (e1 - e0)
    su = float(u.sum())

    def nll(b):
        if abs(b) < 1e-8:
            return -(b * su)
        return -(b * su + n * math.log(b / math.expm1(b)))

    r = optimize.minimize_scalar(nll, bounds=(-20, 20), method="bounded")
    b = float(r.x)
    h = 1e-3
    curv = (nll(b + h) - 2 * nll(b) + nll(b - h)) / h**2
    se = float(1.0 / math.sqrt(curv)) if curv > 0 else math.nan
    return {"dlnD": -b, "dlnD_se": se, "n": int(n)}


def expected_dlnD(a_mass: int, e0: float, e1: float, sn_mev: float = 6.0) -> float:
    """What the level density says ln D should do across [e0, e1] eV: -(d ln rho / dU) dE with
    the back-shifted Fermi gas slope sqrt(a / U) - 3/(2U) at U = Sn, a = A / 8 per MeV. It is
    of order -1e-3 per 10 keV: inside any resolved region the level-density drift is invisible,
    so a measurable slope is a detection effect, not a level-density one."""
    a = a_mass / 8.0
    dlnrho = math.sqrt(a / sn_mev) - 1.5 / sn_mev          # per MeV
    return -dlnrho * (e1 - e0) * 1e-6


# --------------------------------------------------------------------------------------------
# (iii) spacing distribution: J-mixing
# --------------------------------------------------------------------------------------------

def mean_ratio(er: np.ndarray) -> tuple[float, int]:
    """<r~> = mean of min(s_i, s_i+1) / max(s_i, s_i+1) over consecutive spacings."""
    s = np.diff(np.sort(np.asarray(er, float)))
    s = s[s > 0]
    if s.size < 5:
        return math.nan, int(s.size)
    r = np.minimum(s[1:], s[:-1]) / np.maximum(s[1:], s[:-1])
    return float(r.mean()), int(r.size)


@lru_cache(maxsize=64)
def expected_ratio(weights: tuple[float, ...], n_levels: int = 4000, seed: int = 7) -> float:
    """<r~> of a superposition of independent GOE sequences with relative densities ``weights``."""
    from physics.resonance.ladder import goe_unit_levels

    rng = np.random.default_rng(seed)
    w = np.asarray(weights, float) / np.sum(weights)
    lv = np.concatenate([goe_unit_levels(int(n_levels * wi) + 2, rng) / wi for wi in w])
    lim = min(n_levels * 0.9, *(int(n_levels * wi) / wi * 0.9 for wi in w))
    return mean_ratio(lv[lv < lim])[0]


def spin_sequence_weights(spi: float, sigma2: float = 10.0) -> tuple[float, ...]:
    """Relative densities of the s-wave spin sequences, (2J+1) exp(-(J+1/2)^2 / 2 sigma^2)."""
    js = s_wave_spins(spi)
    return tuple(float((2 * j + 1) * math.exp(-((j + 0.5) ** 2) / (2 * sigma2))) for j in js)


def spacing_ratio(lad: dict[str, Any]) -> dict[str, float]:
    """<r~> of the whole s-wave ladder, its expectation for the allowed spin sequences, and <r~>
    inside the evaluator-assigned J sequences (NaN when fewer than two thirds carry a J)."""
    er, aj, spi = lad["er"], lad["aj"], lad["spi"]
    r, k = mean_ratio(er)
    js = s_wave_spins(spi)
    w = spin_sequence_weights(spi)
    out = {"r_all": r, "n_ratios": k, "n_sequences": len(js),
           "r_expected": expected_ratio(w) if w else math.nan,
           # one-sigma of <r~> for k ratios: sd of r~ is ~0.26 (GOE) .. 0.29 (Poisson)
           "r_se": 0.27 / math.sqrt(k) if k else math.nan,
           "r_within_J": math.nan, "frac_J_assigned": math.nan}
    if len(js) == 2 and np.isfinite(spi):
        assigned = np.zeros(er.size, bool)
        for j in js:
            assigned |= np.isclose(aj, j)
        out["frac_J_assigned"] = float(assigned.mean())
        if assigned.mean() >= 2 / 3:
            vals, wts = [], []
            for j in js:
                rj, kj = mean_ratio(er[np.isclose(aj, j)])
                if np.isfinite(rj):
                    vals.append(rj)
                    wts.append(kj)
            if wts:
                out["r_within_J"] = float(np.average(vals, weights=wts))
    return out
