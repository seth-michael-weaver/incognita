"""Spectrum-averaged cross sections (SACS) for the integral rows of the evaluation exam (track ch-sacs).

Model value = integral sigma(E) chi(E) dE / integral chi(E) dE on a fine grid, sigma log-log interpolated
(zero below the first positive point and above the last one). chi = Cf-252(sf) Maxwellian, T = 1.42 MeV, for
records labelled 'cf252'; otherwise the U-235(nth,f) Watt spectrum (a = 0.988 MeV, b = 2.249 / MeV).

Restored 2026-11-06 from the research tree (incognita/eval/spectra.py, the module the published SACS numbers used):
incognita/bench/score.py imports it, but it was missing from the public repository, so ch-sacs could not be scored.

BUGSCORE2 (2026-11-07): the restored module integrated from 100 keV only, so both integrals left out the part of the
fission spectrum below 100 keV (1.3 % of the Watt U-235 spectrum and of the Cf-252 Maxwellian) and with it the 1/v-rising
low-energy capture: every model's capture SACS came out low by about the same amount. A measured SACS is an average
over the whole spectrum, so the grid now starts at the staged grid's first point (1e-5 eV), at the same point density.
OLD_EF keeps the 100 keV grid for the before/after comparison (docs/release/amendments/BUGSCORE2.md).
"""
import numpy as np

EF = np.geomspace(1e-5, 2e7, 21000)
OLD_EF = np.geomspace(1e5, 2e7, 4000)


def chi(kind, ef=None):
    e = (EF if ef is None else ef) / 1e6
    return np.sqrt(e) * np.exp(-e / 1.42) if kind == "cf252" else np.exp(-e / 0.988) * np.sinh(np.sqrt(2.249 * e))


def fold(e_ev, s_mb, kind, ef=None):
    ef = EF if ef is None else ef
    ok = s_mb > 0
    if ok.sum() < 3:
        return np.nan
    ls = np.interp(np.log(ef), np.log(e_ev[ok]), np.log(s_mb[ok]), left=-np.inf)
    s = np.exp(ls)
    s[ef > e_ev[ok].max()] = 0.0
    c = chi(kind, ef)
    _trap = getattr(np, "trapezoid", None) or np.trapz
    return float(_trap(s * c, ef) / _trap(c, ef))
