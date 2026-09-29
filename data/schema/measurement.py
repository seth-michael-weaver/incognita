"""One EXFOR data table (blueprint §4.2 EXFOR), i.e. one subentry/pointer.

Energies are stored in eV, cross sections in barns after unit normalization;
the ``original`` block keeps whatever the compilers gave (with its ``units``) and
``renormalized`` holds the absolute values after monitor/standards conversion,
tagged with the Standards version used.
"""

from __future__ import annotations

from enum import StrEnum
from typing import ClassVar

import pyarrow as pa
from pydantic import Field, field_validator, model_validator

from data.schema.base import FLOAT_LIST, ArrowRecord, _Model, as_float_list
from data.schema.keys import nuclide_id_from_za

__all__ = ["DataBlock", "Measurement", "QuantityType", "ReactionSF"]


class QuantityType(StrEnum):
    CROSS_SECTION = "cross_section"
    RATIO = "ratio"
    RESONANCE_PARAMETER = "resonance_parameter"
    ANGULAR_DISTRIBUTION = "angular_distribution"
    SPECTRUM = "spectrum"
    INTEGRAL = "integral"  # MACS, spectrum-averaged, resonance integrals
    OTHER = "other"


class ReactionSF(_Model):
    """EXFOR reaction-string decomposition, subfields SF1-SF9."""

    sf1: str | None = None  # target
    sf2: str | None = None  # incident projectile
    sf3: str | None = None  # process
    sf4: str | None = None  # reaction product
    sf5: str | None = None  # branch
    sf6: str | None = None  # parameter (SIG, DA, DE, ...)
    sf7: str | None = None  # particle considered
    sf8: str | None = None  # modifier (MXW, SPA, RAW, ...)
    sf9: str | None = None  # data type (EXP, EVAL, DERIV, ...)


REACTION_SF_TYPE = pa.struct([pa.field(f"sf{i}", pa.string()) for i in range(1, 10)])


class DataBlock(_Model):
    """Values with statistical and systematic 1-σ uncertainties on the record's grid."""

    values: list[float]
    stat_sigma: list[float] | None = None
    sys_sigma: list[float] | None = None
    units: str = "b"
    standards_version: str | None = None  # e.g. "IAEA Neutron Standards 2017"

    @field_validator("values", "stat_sigma", "sys_sigma", mode="before")
    @classmethod
    def _coerce(cls, v: object) -> object:
        return as_float_list(v)

    @model_validator(mode="after")
    def _lengths(self) -> DataBlock:
        n = len(self.values)
        for name in ("stat_sigma", "sys_sigma"):
            v = getattr(self, name)
            if v is not None and len(v) != n:
                raise ValueError(f"{name} has {len(v)} entries, values has {n}")
        return self


DATA_BLOCK_TYPE = pa.struct(
    [
        pa.field("values", FLOAT_LIST, nullable=False),
        pa.field("stat_sigma", FLOAT_LIST),
        pa.field("sys_sigma", FLOAT_LIST),
        pa.field("units", pa.string(), nullable=False),
        pa.field("standards_version", pa.string()),
    ]
)


class Measurement(ArrowRecord):
    """One EXFOR data table. Primary key: ``(entry, subentry, pointer)``."""

    entry: str  # EXFOR entry, e.g. "10047"
    subentry: str  # full subentry accession, e.g. "10047002"
    pointer: str | None = None  # multi-column pointer within a subentry

    # Target. ``target_a == 0`` means a natural-abundance target; ``target_id`` is then None.
    target_z: int = Field(ge=0, le=999)
    target_a: int = Field(ge=0)
    target_iso: int = Field(default=0, ge=0)
    target_id: str | None = None
    projectile: str  # "n", "p", "d", "t", "h", "a", "g"
    reaction: str  # full EXFOR reaction string, e.g. "(92-U-235(N,F),,SIG)"
    sf: ReactionSF = Field(default_factory=ReactionSF)
    mt: int | None = None  # ENDF MT when the reaction maps to one
    quantity: QuantityType = QuantityType.CROSS_SECTION

    # Independent variables. ``energy_ev`` is the incident energy; the others are
    # only set for angular distributions and spectra.
    energy_ev: list[float]
    energy_sigma_ev: list[float] | None = None
    angle_deg: list[float] | None = None
    secondary_energy_ev: list[float] | None = None

    original: DataBlock
    renormalized: DataBlock | None = None

    monitor: str | None = None  # monitor reaction string, if relative
    year: int | None = None
    facility: str | None = None
    detector: str | None = None
    first_author: str | None = None
    reference: str | None = None
    doi: str | None = None
    outdated: bool = False  # IAEA "outdated" / superseded flag
    exfor_version: str | None = None  # IAEA dump date, e.g. "2025-06-01"

    ARROW_SCHEMA: ClassVar[pa.Schema] = pa.schema(
        [
            pa.field("entry", pa.string(), nullable=False),
            pa.field("subentry", pa.string(), nullable=False),
            pa.field("pointer", pa.string()),
            pa.field("target_z", pa.int16(), nullable=False),
            pa.field("target_a", pa.int16(), nullable=False),
            pa.field("target_iso", pa.int8(), nullable=False),
            pa.field("target_id", pa.string()),
            pa.field("projectile", pa.string(), nullable=False),
            pa.field("reaction", pa.string(), nullable=False),
            pa.field("sf", REACTION_SF_TYPE, nullable=False),
            pa.field("mt", pa.int32()),
            pa.field("quantity", pa.string(), nullable=False),
            pa.field("energy_ev", FLOAT_LIST, nullable=False),
            pa.field("energy_sigma_ev", FLOAT_LIST),
            pa.field("angle_deg", FLOAT_LIST),
            pa.field("secondary_energy_ev", FLOAT_LIST),
            pa.field("original", DATA_BLOCK_TYPE, nullable=False),
            pa.field("renormalized", DATA_BLOCK_TYPE),
            pa.field("monitor", pa.string()),
            pa.field("year", pa.int16()),
            pa.field("facility", pa.string()),
            pa.field("detector", pa.string()),
            pa.field("first_author", pa.string()),
            pa.field("reference", pa.string()),
            pa.field("doi", pa.string()),
            pa.field("outdated", pa.bool_(), nullable=False),
            pa.field("exfor_version", pa.string()),
        ]
    )

    @field_validator(
        "energy_ev", "energy_sigma_ev", "angle_deg", "secondary_energy_ev", mode="before"
    )
    @classmethod
    def _coerce(cls, v: object) -> object:
        return as_float_list(v)

    @model_validator(mode="after")
    def _consistent(self) -> Measurement:
        if self.target_a == 0:
            key = None
        else:
            if self.target_a < self.target_z:
                raise ValueError("target_a must be >= target_z")
            key = nuclide_id_from_za(self.target_z, self.target_a, self.target_iso)
        if self.target_id is None:
            self.target_id = key
        elif self.target_id != key:
            raise ValueError(f"target_id={self.target_id!r} inconsistent with {key!r}")

        n = len(self.energy_ev)
        for name in ("energy_sigma_ev", "angle_deg", "secondary_energy_ev"):
            v = getattr(self, name)
            if v is not None and len(v) != n:
                raise ValueError(f"{name} has {len(v)} entries, energy_ev has {n}")
        for name in ("original", "renormalized"):
            blk = getattr(self, name)
            if blk is not None and len(blk.values) != n:
                raise ValueError(f"{name}.values has {len(blk.values)} entries, energy_ev has {n}")
        if self.renormalized is not None and self.renormalized.standards_version is None:
            raise ValueError("renormalized block must record the standards_version used")
        return self

    @property
    def key(self) -> tuple[str, str, str | None]:
        return (self.entry, self.subentry, self.pointer)

    @property
    def n_points(self) -> int:
        return len(self.energy_ev)
