"""Units for the TALYS port: the only place a unit conversion factor may be written.

Contract §4.1. Public names carry a unit suffix (`_mev`, `_ev`, `_kev`, `_mb`, `_b`, `_fm`,
`_per_mev`, `_mev3`, `_amu`); dimensionless quantities carry none. Internally, and in every
`Results` table, cross sections are millibarns because every TALYS output file is.

The type aliases below are documentation that static checkers and readers can see; they do not
convert anything. Conversions are explicit multiplications by the named constants.
"""

from __future__ import annotations

from typing import Annotated

from torch import Tensor

# --- type aliases (documentation only) ---------------------------------------------------------
MeV = Annotated[Tensor, "MeV"]
eV = Annotated[Tensor, "eV"]
fm = Annotated[Tensor, "fm"]
mb = Annotated[Tensor, "mb"]
barn = Annotated[Tensor, "b"]
per_MeV = Annotated[Tensor, "MeV^-1"]  # level densities
MeV_minus3 = Annotated[Tensor, "MeV^-3"]  # photon strength functions
amu = Annotated[Tensor, "amu"]
Dimensionless = Annotated[Tensor, "1"]  # transmission coefficients, spins, ratios

# --- conversions -------------------------------------------------------------------------------
MB_PER_B = 1.0e3
B_PER_MB = 1.0e-3
EV_PER_MEV = 1.0e6
MEV_PER_EV = 1.0e-6
KEV_PER_MEV = 1.0e3
MEV_PER_KEV = 1.0e-3
MEV_PER_MILLI_EV = 1.0e-9  # RIPL/structure_params `gamma_gamma_mev` holds meV (WP-26 trap)
FM2_PER_MB = 0.1  # 1 mb = 0.1 fm^2
MB_PER_FM2 = 10.0
S0_PRINT_SCALE = 1.0e-4  # talys.out prints "S0: 5.6558 .e-4" meaning 5.6558e-4

UNIT_SUFFIXES = ("_mev", "_ev", "_kev", "_mb", "_b", "_fm", "_per_mev", "_mev3", "_amu")
