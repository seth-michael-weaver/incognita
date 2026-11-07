"""Spectrum-averaged cross sections (SACS) for the integral rows of the evaluation exam (track ch-sacs).

Model value = integral sigma(E) chi(E) dE / integral chi(E) dE on a fine grid, sigma log-log interpolated
(zero below the first positive point and above the last one). chi = Cf-252(sf) Maxwellian, T = 1.42 MeV, for
records labelled 'cf252'; otherwise the U-235(nth,f) Watt spectrum (a = 0.988 MeV, b = 2.249 / MeV).

Restored 2026-11-06 from the research tree (incognita/eval/spectra.py, the module the published SACS numbers used):
incognita/bench/score.py imports it, but it was missing from the public repository, so ch-sacs could not be scored.
"""
import numpy as np

EF = np.geomspace(1e5, 2e7, 4000)


def chi(kind):
    e = EF / 1e6
    return np.sqrt(e) * np.exp(-e / 1.42) if kind == "cf252" else np.exp(-e / 0.988) * np.sinh(np.sqrt(2.249 * e))


def fold(e_ev, s_mb, kind):
    ok = s_mb > 0
    if ok.sum() < 3:
        return np.nan
    ls = np.interp(np.log(EF), np.log(e_ev[ok]), np.log(s_mb[ok]), left=-np.inf)
    s = np.exp(ls)
    s[EF > e_ev[ok].max()] = 0.0
    c = chi(kind)
    _trap = getattr(np, "trapezoid", None) or np.trapz
    return float(_trap(s * c, EF) / _trap(c, EF))
