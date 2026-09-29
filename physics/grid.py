"""The common log-spaced incident-energy grid (blueprint §4.2).

Every evaluated cross section, TALYS surrogate output and residual-model target
lives on this one grid so that tables can be stacked without interpolation.
``EvaluatedXS.grid_id`` references :data:`GRID_ID`; bump the version suffix if
the grid ever changes so stale Parquet is detectable.
"""

from __future__ import annotations

import numpy as np

__all__ = [
    "E_MAX_EV",
    "E_MIN_EV",
    "ENERGY_GRID_EV",
    "GRID_ID",
    "LOG10_ENERGY_GRID",
    "N_POINTS",
    "energy_grid",
    "interp_to_grid",
    "nearest_index",
]

E_MIN_EV: float = 1e-5
E_MAX_EV: float = 20.0e6
N_POINTS: int = 3000
GRID_ID: str = "log3000-1e-5eV-20MeV-v1"


def energy_grid(
    n_points: int = N_POINTS, e_min_ev: float = E_MIN_EV, e_max_ev: float = E_MAX_EV
) -> np.ndarray:
    """Log-spaced energies in eV, inclusive of both endpoints, as float64."""
    if n_points < 2:
        raise ValueError("need at least two grid points")
    if not (0.0 < e_min_ev < e_max_ev):
        raise ValueError("require 0 < e_min_ev < e_max_ev")
    grid = np.logspace(np.log10(e_min_ev), np.log10(e_max_ev), n_points, dtype=np.float64)
    # logspace can be off by an ulp at the ends; pin them so tests and joins are exact.
    grid[0] = e_min_ev
    grid[-1] = e_max_ev
    return grid


ENERGY_GRID_EV: np.ndarray = energy_grid()
ENERGY_GRID_EV.setflags(write=False)
LOG10_ENERGY_GRID: np.ndarray = np.log10(ENERGY_GRID_EV)
LOG10_ENERGY_GRID.setflags(write=False)


def nearest_index(energy_ev: float | np.ndarray) -> int | np.ndarray:
    """Index of the grid point closest in log-energy to ``energy_ev``."""
    x = np.log10(np.asarray(energy_ev, dtype=np.float64))
    step = (LOG10_ENERGY_GRID[-1] - LOG10_ENERGY_GRID[0]) / (N_POINTS - 1)
    idx = np.rint((x - LOG10_ENERGY_GRID[0]) / step).astype(np.int64)
    idx = np.clip(idx, 0, N_POINTS - 1)
    return int(idx) if idx.ndim == 0 else idx


def interp_to_grid(
    energy_ev: np.ndarray,
    values: np.ndarray,
    *,
    log_x: bool = True,
    log_y: bool = False,
    fill_value: float = 0.0,
    grid: np.ndarray | None = None,
) -> np.ndarray:
    """Interpolate a tabulated function onto the common grid.

    Points outside the tabulated range get ``fill_value`` (0 barns by default,
    which is the right answer for threshold reactions). ``log_y=True`` interpolates
    in log-log, which is what NJOY-style pointwise data usually wants above the
    resonance region; non-positive values fall back to linear in y.
    """
    x = np.asarray(energy_ev, dtype=np.float64)
    y = np.asarray(values, dtype=np.float64)
    if x.ndim != 1 or x.shape != y.shape:
        raise ValueError("energy_ev and values must be 1-D and the same length")
    if x.size and np.any(np.diff(x) < 0):
        order = np.argsort(x, kind="stable")
        x, y = x[order], y[order]
    target = ENERGY_GRID_EV if grid is None else np.asarray(grid, dtype=np.float64)
    xs, ts = (np.log10(x), np.log10(target)) if log_x else (x, target)
    use_log_y = log_y and y.size > 0 and bool(np.all(y > 0))
    ys = np.log10(y) if use_log_y else y
    out = np.interp(ts, xs, ys, left=np.nan, right=np.nan)
    if use_log_y:
        out = 10.0**out
    return np.where(np.isnan(out), fill_value, out)
