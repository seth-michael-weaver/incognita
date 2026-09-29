"""Evaluated-library cross section on the common energy grid (blueprint §4.2).

One record per (library, nuclide, MT, temperature). Values are in barns on
:data:`physics.grid.ENERGY_GRID_EV`; the grid itself is not stored, only its
``grid_id``. Resonance parameters and covariance blocks are separate artifacts
referenced by key so this table stays dense and stackable.
"""

from __future__ import annotations

from typing import ClassVar

import numpy as np
import pyarrow as pa
from pydantic import Field, field_validator, model_validator

from data.schema.base import FLOAT_LIST, ArrowRecord, as_float_list
from data.schema.keys import nuclide_id
from physics.grid import ENERGY_GRID_EV, GRID_ID, N_POINTS

__all__ = ["EvaluatedXS"]


class EvaluatedXS(ArrowRecord):
    library: str  # "ENDF/B-VIII.1", "JEFF-3.3", "JENDL-5", "TENDL-2023", "CENDL-3.2"
    library_version: str | None = None  # release/date if the name is not enough
    Z: int = Field(ge=0, le=999)
    N: int = Field(ge=0, le=999)
    iso: int = Field(default=0, ge=0)
    nuclide_id: str | None = None
    projectile: str = "n"
    mt: int = Field(ge=1, le=999)
    temperature_k: float = Field(default=0.0, ge=0.0)  # 0 K = training target (§4.2)

    grid_id: str = GRID_ID
    values_b: list[float]  # cross section in barns, len == N_POINTS for the common grid

    # Threshold (eV) for threshold reactions; None otherwise.
    threshold_ev: float | None = None
    # Resolved / unresolved resonance-region upper bounds (eV) as declared in MF2.
    resolved_upper_ev: float | None = None
    unresolved_upper_ev: float | None = None
    # Keys into the separate resonance-parameter and covariance stores.
    resonance_ref: str | None = None  # e.g. "staging/resonances.parquet#ENDF/B-VIII.1/Z092N143M0"
    covariance_ref: str | None = None  # e.g. Zarr group path for the MF33 block

    ARROW_SCHEMA: ClassVar[pa.Schema] = pa.schema(
        [
            pa.field("library", pa.string(), nullable=False),
            pa.field("library_version", pa.string()),
            pa.field("Z", pa.int16(), nullable=False),
            pa.field("N", pa.int16(), nullable=False),
            pa.field("iso", pa.int8(), nullable=False),
            pa.field("nuclide_id", pa.string(), nullable=False),
            pa.field("projectile", pa.string(), nullable=False),
            pa.field("mt", pa.int16(), nullable=False),
            pa.field("temperature_k", pa.float64(), nullable=False),
            pa.field("grid_id", pa.string(), nullable=False),
            pa.field("values_b", FLOAT_LIST, nullable=False),
            pa.field("threshold_ev", pa.float64()),
            pa.field("resolved_upper_ev", pa.float64()),
            pa.field("unresolved_upper_ev", pa.float64()),
            pa.field("resonance_ref", pa.string()),
            pa.field("covariance_ref", pa.string()),
        ]
    )

    @field_validator("values_b", mode="before")
    @classmethod
    def _coerce(cls, v: object) -> object:
        return as_float_list(v)

    @model_validator(mode="after")
    def _consistent(self) -> EvaluatedXS:
        key = nuclide_id(self.Z, self.N, self.iso)
        if self.nuclide_id is None:
            self.nuclide_id = key
        elif self.nuclide_id != key:
            raise ValueError(f"nuclide_id={self.nuclide_id!r} inconsistent with {key!r}")
        if self.grid_id == GRID_ID and len(self.values_b) != N_POINTS:
            raise ValueError(f"grid {GRID_ID} has {N_POINTS} points, got {len(self.values_b)}")
        if any(v < 0 for v in self.values_b):
            raise ValueError("negative cross section")
        return self

    @property
    def key(self) -> tuple[str, int, int, int, int, float]:
        return (self.library, self.Z, self.N, self.iso, self.mt, self.temperature_k)

    @property
    def energy_ev(self) -> np.ndarray:
        """The energy grid this record lives on (only the common grid is known here)."""
        if self.grid_id != GRID_ID:
            raise ValueError(f"unknown grid_id {self.grid_id!r}; look it up yourself")
        return ENERGY_GRID_EV

    def values(self) -> np.ndarray:
        return np.asarray(self.values_b, dtype=np.float64)
