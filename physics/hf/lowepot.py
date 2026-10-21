"""LOWEPOT: no Hauser-Feshbach compound elastic below the resonance region (`INCOGNITA_LOWEPOT`, default ON since the
LOWEPOTAF gate commit; INCOGNITA_LOWEPOT=0 = previous production).

Mechanism. The HF compound elastic is an ENSEMBLE AVERAGE over many resonances in the averaging interval. Below the
first resonance there is no such interval: the elastic cross section is potential scattering, 4 pi sin^2(k R')/k^2
(R' = the OMP s-wave scattering radius), plus the tails of the nearest (unknown) resonances. The engine evaluates the HF
average anyway when a run asks for E < 1 keV. With T_n ~ sqrt(E) >> T_gamma its compound elastic grows as 1/sqrt(E), e.g.
Ti-48 at 0.0253 eV: 14 kb elastic against a measured ~4 b. The OMP shape elastic of the same run IS the potential term.

Rule (one rule for every nucleus, inputs = the run's own model quantities; LOWEPOT 2026-10-05 blend, LOWEPOTAF prereg
development notes):
  E_lo = min(D0/2, 1000/3 eV), E_hi = min(3 D0/2, 1000 eV), D0 = the engine's theoretical s-wave spacing of the compound
  (ingredients d0theo; missing or non-finite -> 1000/3 and 1000 eV); w(E) = 0 below E_lo, 1 above E_hi, linear in ln E between;
  elastic(E) -> elastic(E) - (1 - w(E)) * compound_elastic(E); total and compound_elastic lowered by the same amount.
  w(1 keV) = 1 always, so nothing at or above 1 keV changes. Capture and every other channel are untouched.
Diagnostics in totals_mb: lowepot_w, lowepot_dce_mb (the compound elastic removed, mb).
Wiring: `add_to_results(res, injection)` is called by `engine.run` and `engine_c.run` after FEWRES's hook, so the Py and C
paths apply the identical function. Test: tests/hf/test_lowepot.py
"""

from __future__ import annotations

import math
import os

import numpy as np

__all__ = ["on", "edges", "weight", "add_to_results", "EMAX_EV"]

EMAX_EV = 1000.0


def on() -> bool:
    return os.environ.get("INCOGNITA_LOWEPOT", "1").strip().lower() not in ("0", "n", "no", "off")


def edges(d0_ev: float) -> tuple[float, float]:
    if not (math.isfinite(d0_ev) and d0_ev > 0):
        return EMAX_EV / 3, EMAX_EV
    return min(d0_ev / 2, EMAX_EV / 3), min(1.5 * d0_ev, EMAX_EV)


def weight(e_ev, lo: float, hi: float) -> np.ndarray:
    e = np.asarray(e_ev, float)
    return np.clip(np.log(e / lo) / np.log(hi / lo), 0.0, 1.0)


def add_to_results(res, injection):
    """`engine.run` / `engine_c.run` Results with the LOWEPOT change in elastic/total/compound_elastic, in place; off, a
    charged or injected run, or no energy below 1 keV -> untouched."""
    if not on() or getattr(injection, "families", ()) or not hasattr(injection, "Z"):
        return res
    if os.environ.get("INCOGNITA_CPINC", ""):
        return res
    tm = getattr(res, "totals_mb", None)
    if not isinstance(tm, dict) or not all(k in tm for k in ("elastic", "total", "compound_elastic")):
        return res
    e_ev = res.e_inc_mev.detach().cpu().numpy().astype(float) * 1e6
    if not np.any(e_ev < EMAX_EV):
        return res
    import torch

    from physics.hf.fewres import run_ingredients

    Z, A = int(injection.Z), int(injection.A)
    cas = getattr(injection, "cascade", None)
    if cas is None:
        from physics.hf import warmrun
        cas = warmrun.new_cascade(Z, A, tuple(float(x) for x in res.e_inc_mev.detach().cpu().numpy()))
    d0 = float(run_ingredients(cas)["d0theo_ev"])
    lo, hi = edges(d0)
    w = weight(e_ev, lo, hi)
    ce = tm["compound_elastic"].detach().cpu().numpy().astype(float)
    dce = np.where(e_ev < EMAX_EV, (1.0 - w) * ce, 0.0)
    dt = res.e_inc_mev.dtype
    d = torch.as_tensor(dce, dtype=tm["elastic"].dtype)
    for k in ("elastic", "total", "compound_elastic"):
        tm[k] = tm[k] - d
    tm["lowepot_w"] = torch.as_tensor(w, dtype=dt)
    tm["lowepot_dce_mb"] = torch.as_tensor(dce, dtype=dt)
    return res
