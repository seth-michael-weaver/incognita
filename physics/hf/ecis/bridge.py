"""ECIS bridge: TALYS's own optical-model results, read from the reference dumps.

Contract §5 and §7 (T0 owns this file; T13 replaces it). TALYS computes every transmission
coefficient and every direct cross section with ECIS-06 -- coupled channels for actinides by
default (RIPL OMP 2408, input_omppar.f90:181-188), DWBA for collective levels everywhere. Until
the ECIS port lands, consumers that need those numbers for a deformed or actinide target take
them from here, with the same shapes `omp.schrodinger.Transmission` will have, so switching to
the port is a one-line change in the engine.

Only cases that exist in the dumps can be served; anything else raises, never extrapolates.
"""

from __future__ import annotations

import numpy as np

from physics.hf import reference as ref

PARTICLES = ("n", "p", "d", "t", "h", "a")


def emission_transmission(target: str, variant: str = "default") -> dict:
    """TALYS emission-grid T_lj for all six particles: {particle: {e_mev, tjl (E, L, 2)}}.

    Particles TALYS did not write (closed channels) are absent from the dict.
    """
    out = {}
    for p in PARTICLES:
        try:
            out[p] = ref.transmission(target, particle=p, variant=variant)
        except KeyError:  # file absent = channel not written; anything else is a bug
            continue
    if not out:
        raise KeyError(f"no transmission dumps for {target}/{variant}")
    return out


def direct_inelastic(target: str, e_inc_mev: float, variant: str = "default") -> list[str]:
    """Raw rows of directE<E>.out (level, energy, E-out, J/P, cross section [mb], def. type,
    def. par.). Returned unparsed because the J/P column holds strings; T12 owns the parser.
    """
    import pandas as pd

    name = "directE" + f"{e_inc_mev:08.3f}".replace(" ", "0") + ".out"
    p = ref.reference_dir() / "raw_rows.parquet"
    df = pd.read_parquet(p)
    rows = df[(df["target"] == target) & (df["variant"] == variant) & (df["file"] == name)]
    if rows.empty:
        raise KeyError(f"{name} not in dumps for {target}/{variant}")
    return list(rows.sort_values("row")["line"])


def check_shapes(tr: dict) -> None:
    """Contract shape check shared by the bridge and T5's solver output."""
    for p, d in tr.items():
        e, t = np.asarray(d["e_mev"]), np.asarray(d["tjl"])
        nj = {"d": 3, "a": 1}.get(p, 2)
        if t.ndim != 3 or t.shape[0] != e.shape[0] or t.shape[2] != nj:
            raise ValueError(f"{p}: tjl {t.shape} vs e {e.shape}")
        if (t < 0).any() or (t > 1 + 1e-6).any():
            raise ValueError(f"{p}: transmission outside [0, 1]")
