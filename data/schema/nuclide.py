"""Tier 1 nuclide-level record (blueprint §2.2): ground-state and decay properties."""

from __future__ import annotations

import math
from typing import ClassVar

import pyarrow as pa
from pydantic import Field, field_validator, model_validator

from data.schema.base import DATUM_TYPE, ArrowRecord, Datum, _Model
from data.schema.keys import nuclide_id

__all__ = ["DECAY_MODES", "DecayBranch", "Nuclide"]

# NUBASE-style decay mode codes; ``mode`` is validated against this set.
DECAY_MODES: frozenset[str] = frozenset(
    {
        "B-",  # beta minus
        "B+",  # beta plus (positron)
        "EC",  # electron capture
        "EC+B+",  # unresolved EC / beta plus
        "A",  # alpha
        "SF",  # spontaneous fission
        "p",  # proton emission
        "2p",
        "n",  # neutron emission
        "2n",
        "IT",  # isomeric transition
        "B-n",  # beta-delayed neutron
        "B-2n",
        "B-3n",
        "B-A",
        "B-SF",
        "B+p",
        "B+2p",
        "B+A",
        "B+SF",
        "ECp",
        "ECA",
        "ECSF",
        "14C",  # cluster decay (any heavy cluster)
        "2B-",
        "2B+",
        "2EC",
        "IS",  # stable, appears in NUBASE for naturally occurring isotopes
        # --- added for NUBASE2020 coverage (WP-04) ---
        "e+",  # positron emission quoted separately from B+ (IAS entries)
        "B",  # beta decay, direction not specified (one 126Pd level)
        "B-p",
        "B-d",
        "B-t",
        "B-4n",
        "B+pA",
        "B+3p",
        "3p",
        "3n",
        "d",  # deuteron emission
        "3H",  # triton emission
        "3He",
        # heavy-cluster radioactivity, one code per emitted cluster as NUBASE quotes it
        "12C",
        "18O",
        "20O",
        "20Ne",
        "22Ne",
        "23F",
        "24Ne",
        "25Ne",
        "28Mg",
        "30Mg",
        "32Si",
        "34Si",
        "24Ne+26Ne",
        "28Mg+30Mg",
    }
)


class DecayBranch(_Model):
    """One decay mode with its branching ratio as a fraction in [0, 1]."""

    mode: str
    branching: float | None = None
    sigma: float | None = None
    qualifier: str = "="  # "=", "<", ">", "~", "?" as NUBASE quotes them

    @field_validator("mode")
    @classmethod
    def _known_mode(cls, v: str) -> str:
        if v not in DECAY_MODES:
            raise ValueError(f"unknown decay mode {v!r}; extend DECAY_MODES if it is real")
        return v

    @field_validator("branching")
    @classmethod
    def _fraction(cls, v: float | None) -> float | None:
        if v is not None and not (0.0 <= v <= 1.0):
            raise ValueError("branching is a fraction in [0, 1], not a percent")
        return v

    @field_validator("qualifier")
    @classmethod
    def _qual(cls, v: str) -> str:
        if v not in {"=", "<", ">", "~", "?"}:
            raise ValueError(f"bad qualifier {v!r}")
        return v


DECAY_BRANCH_TYPE = pa.struct(
    [
        pa.field("mode", pa.string(), nullable=False),
        pa.field("branching", pa.float64()),
        pa.field("sigma", pa.float64()),
        pa.field("qualifier", pa.string(), nullable=False),
    ]
)


class Nuclide(ArrowRecord):
    """One row per (Z, N, iso). Units: keV for energies, fm for radii, seconds for half-life.

    ``A`` and ``nuclide_id`` are derived from ``(Z, N, iso)`` and filled in automatically;
    passing them explicitly is allowed but they must agree.
    """

    Z: int = Field(ge=0, le=999)
    N: int = Field(ge=0, le=999)
    iso: int = Field(default=0, ge=0)
    A: int | None = None
    nuclide_id: str | None = None
    symbol: str | None = None  # element symbol, e.g. "Fe"

    # Isomer bookkeeping (0 for the ground state).
    excitation_energy_kev: Datum | None = None

    # Masses (keV). ``mass_excess.extrapolated`` is the AME '#' flag.
    mass_excess_kev: Datum | None = None
    binding_energy_per_a_kev: Datum | None = None

    # Separation energies (keV).
    sn_kev: Datum | None = None
    s2n_kev: Datum | None = None
    sp_kev: Datum | None = None
    s2p_kev: Datum | None = None

    # Ground-state spin/parity. parity ∈ {+1, -1}; None = unknown.
    spin: float | None = None
    parity: int | None = None
    spin_parity_tentative: bool = False
    spin_parity_raw: str | None = None  # NUBASE string, e.g. "(2+,3-)", kept for ambiguous cases

    # Decay. ``log10_half_life_s`` is None for stable nuclides (is_stable=True) and for
    # nuclides whose half-life is unknown (is_stable=False).
    is_stable: bool = False
    log10_half_life_s: Datum | None = None
    decay_modes: list[DecayBranch] = Field(default_factory=list)

    # Beta-delayed neutron emission probabilities as fractions in [0, 1].
    pn: Datum | None = None
    p2n: Datum | None = None

    # Auxiliary physics targets.
    charge_radius_fm: Datum | None = None
    beta2: Datum | None = None

    source_version: str | None = None  # e.g. "AME2020+NUBASE2020"
    # Reference years from NUBASE (for time-based splits, §4.4): ENSDF evaluation year of the
    # entry and year the nuclide was discovered.
    ensdf_year: int | None = None
    discovery_year: int | None = None

    ARROW_SCHEMA: ClassVar[pa.Schema] = pa.schema(
        [
            pa.field("Z", pa.int16(), nullable=False),
            pa.field("N", pa.int16(), nullable=False),
            pa.field("iso", pa.int8(), nullable=False),
            pa.field("A", pa.int16(), nullable=False),
            pa.field("nuclide_id", pa.string(), nullable=False),
            pa.field("symbol", pa.string()),
            pa.field("excitation_energy_kev", DATUM_TYPE),
            pa.field("mass_excess_kev", DATUM_TYPE),
            pa.field("binding_energy_per_a_kev", DATUM_TYPE),
            pa.field("sn_kev", DATUM_TYPE),
            pa.field("s2n_kev", DATUM_TYPE),
            pa.field("sp_kev", DATUM_TYPE),
            pa.field("s2p_kev", DATUM_TYPE),
            pa.field("spin", pa.float64()),
            pa.field("parity", pa.int8()),
            pa.field("spin_parity_tentative", pa.bool_(), nullable=False),
            pa.field("spin_parity_raw", pa.string()),
            pa.field("is_stable", pa.bool_(), nullable=False),
            pa.field("log10_half_life_s", DATUM_TYPE),
            pa.field("decay_modes", pa.list_(DECAY_BRANCH_TYPE), nullable=False),
            pa.field("pn", DATUM_TYPE),
            pa.field("p2n", DATUM_TYPE),
            pa.field("charge_radius_fm", DATUM_TYPE),
            pa.field("beta2", DATUM_TYPE),
            pa.field("source_version", pa.string()),
            pa.field("ensdf_year", pa.int16()),
            pa.field("discovery_year", pa.int16()),
        ]
    )

    @field_validator("spin")
    @classmethod
    def _half_integer(cls, v: float | None) -> float | None:
        if v is not None and (v < 0 or not math.isclose(v * 2, round(v * 2))):
            raise ValueError("spin must be a non-negative multiple of 1/2")
        return v

    @field_validator("parity")
    @classmethod
    def _parity(cls, v: int | None) -> int | None:
        if v not in (None, 1, -1):
            raise ValueError("parity must be +1, -1 or None")
        return v

    @field_validator("pn", "p2n")
    @classmethod
    def _fraction(cls, v: Datum | None) -> Datum | None:
        if v is not None and not (0.0 <= v.value <= 1.0):
            raise ValueError("Pn / P2n are fractions in [0, 1]")
        return v

    @model_validator(mode="after")
    def _derive_keys(self) -> Nuclide:
        if self.Z + self.N == 0:
            raise ValueError("a nuclide needs at least one nucleon")
        a = self.Z + self.N
        if self.A is None:
            self.A = a
        elif self.A != a:
            raise ValueError(f"A={self.A} inconsistent with Z+N={a}")
        key = nuclide_id(self.Z, self.N, self.iso)
        if self.nuclide_id is None:
            self.nuclide_id = key
        elif self.nuclide_id != key:
            raise ValueError(f"nuclide_id={self.nuclide_id!r} inconsistent with {key!r}")
        if self.is_stable and self.log10_half_life_s is not None:
            raise ValueError("stable nuclides carry no half-life")
        return self

    @property
    def key(self) -> tuple[int, int, int]:
        return (self.Z, self.N, self.iso)
