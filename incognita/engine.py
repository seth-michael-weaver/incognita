"""One call from Python to the engine: every reaction channel of one neutron-induced target.

    >>> from incognita.engine import run
    >>> res = run(26, 56)                      # Fe-56, 30 energies 1 keV - 20 MeV
    >>> res.channels                           # pandas DataFrame, mb, one column per channel
    >>> res.channels["(n,2n)"]

The engine is a port of TALYS-2 (MIT, A.J. Koning, S. Hilaire, S. Goriely; see NOTICE). It reads
the TALYS nuclear-structure database from ``$TALYS_DIR/structure`` (``scripts/fetch_structure.sh``
fetches the part the engine reads). The default arm is the shipped no-data recipe
(``INCOGNITA_TALYS_FIT=nodata``: TALYS defaults with INCOGNITA's own E1-width constant).

The engine returns central values only. Calibrated intervals exist for capture in the shipped
library: :func:`incognita.library.capture`.
"""

from __future__ import annotations

import os
import time
from dataclasses import dataclass, field

import numpy as np

_PARTICLES = ("n", "p", "d", "t", "h", "a")


def channel_label(key: str) -> str:
    """TALYS's exclusive-channel key ``xsNPDTHA`` (counts of n, p, d, t, 3He, alpha in the exit
    channel) as a reaction label: ``xs000000`` -> ``(n,g)``, ``xs200000`` -> ``(n,2n)``,
    ``xs010000`` -> ``(n,p)``. Keys that are not of that form are returned unchanged."""
    code = key[2:] if key.startswith("xs") else ""
    if len(code) != 6 or not code.isdigit():
        return key
    parts = [(f"{int(c)}{p}" if int(c) > 1 else p) for c, p in zip(code, _PARTICLES, strict=True)
             if int(c) > 0]
    return "(n,g)" if not parts else "(n," + "".join(parts) + ")"


@dataclass
class Result:
    Z: int
    A: int
    energies_mev: np.ndarray
    channels: object          # pandas.DataFrame, index energy_mev, columns channel labels, mb
    totals: object            # pandas.DataFrame of the run's total/reaction/elastic sums, mb
    wall_s: float
    raw: dict = field(default_factory=dict, repr=False)

    def to_csv(self, path: str) -> None:
        self.channels.join(self.totals).to_csv(path)


def run(Z: int, A: int, energies_mev=None, *, arm: str = "nodata", cc_cache: str | None = None,
        keep_zero: bool = False, keep_raw: bool = False) -> Result:
    """Run the engine for neutrons on (Z, A) and return every exclusive channel in mb.

    ``energies_mev``: incident energies (default: 30 log-spaced points, 1 keV - 20 MeV).
    ``arm``: ``INCOGNITA_TALYS_FIT`` arm (``nodata`` = shipped recipe; ``""`` = stock TALYS defaults).
    ``cc_cache``: directory for the coupled-channels cache (bit-identical, ~3x faster on reruns;
    default ``~/.cache/incognita-cc``).
    ``keep_raw``: keep the engine's own result object in ``Result.raw`` (tensors; costs memory).

    Per-target caches are dropped after the run, so a loop over many targets keeps a flat memory
    footprint (without this, ~20 targets in one process can exceed several GB).
    """
    import pandas as pd

    if energies_mev is None:
        energies_mev = np.geomspace(1e-3, 20.0, 30)
    e = tuple(float(np.float32(x)) for x in np.asarray(energies_mev, float))
    if arm:
        os.environ["INCOGNITA_TALYS_FIT"] = arm
    else:
        os.environ.pop("INCOGNITA_TALYS_FIT", None)
    default_cache = os.path.join(os.path.expanduser("~"), ".cache", "incognita-cc")
    os.environ.setdefault("INCOGNITA_CC_CACHE", cc_cache or default_cache)

    import torch

    from physics.hf import chartrun, warmrun
    from physics.hf.engine import ChainedFull
    from physics.hf.engine_c import run as engine_run

    t0 = time.perf_counter()
    cas = warmrun.new_cascade(Z, A, e)
    with torch.inference_mode():
        res = engine_run(injection=ChainedFull(Z=Z, A=A, declared_energies=e, cascade=cas))
    wall = time.perf_counter() - t0

    idx = pd.Index(np.asarray(e), name="energy_mev")
    cols = {}
    for k, v in res.channels_mb.items():
        a = v.detach().cpu().numpy().astype(float)
        if keep_zero or np.any(a > 0):
            cols[channel_label(k)] = a
    tot = {}
    tm = getattr(res, "totals_mb", None)
    if isinstance(tm, dict):
        for k, v in tm.items():
            if hasattr(v, "detach"):
                tot[str(k)] = v.detach().cpu().numpy().astype(float)
    out = Result(Z=Z, A=A, energies_mev=np.asarray(e), channels=pd.DataFrame(cols, index=idx),
                 totals=pd.DataFrame(tot, index=idx), wall_s=wall,
                 raw={"result": res} if keep_raw else {})
    del cas, res
    chartrun.drop_target_caches()
    return out
