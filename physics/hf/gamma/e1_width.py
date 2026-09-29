"""INDEP_FIX (2026-09-23): replace TALYS's `globalwtable` constants with our own E1-width constant.

TALYS >= 2.2 turns `globalwtable y` on by default: for strength 8/9 and ldmodel 1-6 the compound's E1
`wtable` starts from a table of constants (1.076 for strength 8 / ldmodel 1 without collective
enhancement, ...), the mean of the per-nuclide fits that produced TENDL (`ng.par`). INCOGNITA's
independence rule (2026-09-23) keeps TENDL's METHOD (one chart-wide constant) but not its VALUES.
`INCOGNITA_E1_WTABLE` supplies our constant; INCOGNITA_E1 below is the shipped one, fitted on the development
folds of the capture exam against EXFOR (docs/release/indep_fix2/, `fit_e1.py`):

    unset / ""        stock TALYS behaviour (the table), bit-identical to before
    "1.02"            that value wherever the table would have supplied one (same strengths, same ld keys)
    "8=1.02,9=1.03"   per strength; a strength not named keeps the stock table

Where the table has no entry (ldmodel 7, other strengths, charged projectiles) nothing changes: 1.0.
An explicit `wtable` keyword still wins, exactly as it wins over the table.
Wired for every engine path: `defaults.py` (_wtable, the options tensor the C / fast / GPU paths read)
and `gamma/parameters.py` (the Python reference path) both call `constant`.
"""
from __future__ import annotations

import os

ENV = "INCOGNITA_E1_WTABLE"
#: the E1-width constant of the shipped v0.1 no-data recipe (INDEP_FIX, refitted on DEV EXFOR; replaces TALYS's 1.076 / 1.081).
#: scripts/bestfit/engine_curves.py applies it to `--arm nodata` runs unless `--e1 stock` is given.
INCOGNITA_E1 = 1.0425


def overrides() -> dict[int, float]:
    raw = os.environ.get(ENV, "").strip()
    if not raw:
        return {}
    if "=" not in raw:
        v = float(raw)
        return {8: v, 9: v}
    out = {}
    for tok in raw.split(","):
        k, v = tok.split("=")
        out[int(k.strip().lstrip("s"))] = float(v)
    return out


def constant(strength: int, table_value: float) -> float:
    """The E1 width to use where TALYS's global table supplies `table_value` for this strength."""
    return overrides().get(int(strength), table_value)


def resolve(arm: str, choice: str = "auto") -> str:
    """The INCOGNITA_E1_WTABLE value an engine run should use: 'auto' = the shipped constant for the no-data recipe
    (`nodata` in the arm), TALYS's table otherwise; 'incognita'; 'stock' (TALYS's table, returned as ''); or a number."""
    if choice == "auto":
        return str(INCOGNITA_E1) if "nodata" in arm.replace("+", ",").replace(" ", ",").split(",") else ""
    return {"incognita": str(INCOGNITA_E1), "stock": ""}.get(choice, choice)
