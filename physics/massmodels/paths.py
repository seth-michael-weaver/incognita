"""Raw-file locations for the theoretical mass tables (all under ``raw/``; see WP-02)."""

from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
RAW = REPO / "raw"
RIPL_MASSES = RAW / "ripl4" / "RIPL-4" / "masses"
BRUSLIB = RAW / "mass_models" / "bruslib"
WS4_DIR = RAW / "mass_models" / "ws4"
DZ_DIR = RAW / "mass_models" / "dz"

# AME2020 mass excesses of the hydrogen atom and the neutron (keV); used to turn a
# binding energy into an atomic mass excess: ME = Z*ME_H + N*ME_n - B.
ME_H_KEV = 7288.971064
ME_N_KEV = 8071.31806
