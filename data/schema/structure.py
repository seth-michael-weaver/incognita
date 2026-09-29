"""Tier 2 record (blueprint §2.2 items 7-12, §4.2 RIPL): statistical structure
parameters per nuclide that feed the Hauser-Feshbach layer. Every parameter is a
:class:`Param` carrying σ and a ``source`` of ``measured`` or ``systematics``.

Units: MeV for energies and widths except ``gamma_gamma_mev`` (meV) and the
resonance spacings ``d0_ev`` / ``d1_ev`` (eV); strength functions ``s0``/``s1``
are dimensionless (the raw value, not the ×1e-4 RIPL convention); GDR peak
cross sections in mb.
"""

from __future__ import annotations

from typing import ClassVar

import pyarrow as pa
from pydantic import Field, model_validator

from data.schema.base import NAMED_PARAM_TYPE, PARAM_TYPE, ArrowRecord, NamedParam, Param, _Model
from data.schema.keys import nuclide_id

__all__ = ["FissionBarrier", "Lorentzian", "StructureParams"]


class Lorentzian(_Model):
    """One Lorentzian component of the E1 strength: GDR (or a pygmy resonance)."""

    energy_mev: Param
    width_mev: Param
    sigma_mb: Param


LORENTZIAN_TYPE = pa.struct(
    [
        pa.field("energy_mev", PARAM_TYPE, nullable=False),
        pa.field("width_mev", PARAM_TYPE, nullable=False),
        pa.field("sigma_mb", PARAM_TYPE, nullable=False),
    ]
)


class FissionBarrier(_Model):
    """One barrier hump (index 1 = inner, 2 = outer, 3 = third) with height and curvature."""

    index: int = Field(ge=1, le=3)
    height_mev: Param
    curvature_mev: Param | None = None  # ħω


FISSION_BARRIER_TYPE = pa.struct(
    [
        pa.field("index", pa.int8(), nullable=False),
        pa.field("height_mev", PARAM_TYPE, nullable=False),
        pa.field("curvature_mev", PARAM_TYPE),
    ]
)


class StructureParams(ArrowRecord):
    """Tier 2 parameters for one nuclide (the compound nucleus for reaction use).

    Keying convention (WP-10): level density, discrete levels, GDR and fission barriers
    describe this nuclide itself. Resonance statistics (``d0_ev``, ``s0``, ``gamma_gamma_mev``,
    ``d1_ev``, ``s1``) describe the levels of this nuclide at its own S_n, i.e. they are the
    parameters RIPL quotes for the TARGET one neutron lighter (238U's D0 = 20.3 eV lives on
    the 239U row). ``omp_form`` / ``omp_irefs`` describe neutrons incident on this nuclide.
    """

    Z: int = Field(ge=0, le=999)
    N: int = Field(ge=0, le=999)
    iso: int = Field(default=0, ge=0)
    nuclide_id: str | None = None

    # Level density (item 7). ``ld_model`` names the parametrization the values belong to.
    ld_model: str | None = None  # "CTM", "BSFG", "GSM", "EGSM", "HFB", ...
    ld_a: Param | None = None  # level-density parameter a (MeV^-1)
    ld_delta_mev: Param | None = None  # pairing / energy shift Δ
    ld_spin_cutoff: Param | None = None  # σ² spin-cutoff parameter at the matching energy
    n_discrete_levels: int | None = None  # RIPL count up to the completeness cutoff
    level_cutoff_mev: float | None = None  # completeness cutoff energy (RIPL Umax)
    # WP-10 additions: RIPL-4 ships a constant-temperature fit to the discrete levels
    # (T, E0) and a spin cutoff extracted from the discrete-level spins for ~3.5k
    # nuclides; these are the only level-density labels available beyond the ~300 with
    # a measured D0, so they are stored explicitly rather than squeezed into ``ld_*``.
    ct_temperature_mev: Param | None = None  # CT-model nuclear temperature T
    ct_e0_mev: Param | None = None  # CT-model energy shift E0 (RIPL "U0")
    discrete_spin_cutoff: float | None = None  # σ (not σ²) from discrete-level spins

    # Resonance statistics (items 8, 9) at the neutron separation energy.
    d0_ev: Param | None = None
    d1_ev: Param | None = None
    s0: Param | None = None
    s1: Param | None = None
    gamma_gamma_mev: Param | None = None  # average radiative width, meV

    # Gamma strength function (item 10).
    gsf_model: str | None = None  # "SLO", "GLO", "SMLO", "HFB-QRPA", ...
    gdr: list[Lorentzian] = Field(default_factory=list)  # one or two components
    pygmy: list[Lorentzian] = Field(default_factory=list)
    upbend_c: Param | None = None  # low-energy upbend amplitude (MeV^-3)
    upbend_eta: Param | None = None  # upbend slope (MeV^-1)

    # Optical model (item 11). ``omp_irefs`` lists the RIPL OMP library entries (by
    # ``iref``) valid for neutrons on THIS nuclide as target; the coefficient tables
    # live in ``staging/ripl/omp_terms.parquet``.
    omp_form: str | None = None  # "KD03", "dispersive", ...
    omp: list[NamedParam] = Field(default_factory=list)
    omp_irefs: list[int] = Field(default_factory=list)

    # Fission barriers (item 12).
    fission_barriers: list[FissionBarrier] = Field(default_factory=list)

    source_version: str | None = None  # e.g. "RIPL-3 (2023)"

    ARROW_SCHEMA: ClassVar[pa.Schema] = pa.schema(
        [
            pa.field("Z", pa.int16(), nullable=False),
            pa.field("N", pa.int16(), nullable=False),
            pa.field("iso", pa.int8(), nullable=False),
            pa.field("nuclide_id", pa.string(), nullable=False),
            pa.field("ld_model", pa.string()),
            pa.field("ld_a", PARAM_TYPE),
            pa.field("ld_delta_mev", PARAM_TYPE),
            pa.field("ld_spin_cutoff", PARAM_TYPE),
            pa.field("n_discrete_levels", pa.int32()),
            pa.field("level_cutoff_mev", pa.float64()),
            pa.field("ct_temperature_mev", PARAM_TYPE),
            pa.field("ct_e0_mev", PARAM_TYPE),
            pa.field("discrete_spin_cutoff", pa.float64()),
            pa.field("d0_ev", PARAM_TYPE),
            pa.field("d1_ev", PARAM_TYPE),
            pa.field("s0", PARAM_TYPE),
            pa.field("s1", PARAM_TYPE),
            pa.field("gamma_gamma_mev", PARAM_TYPE),
            pa.field("gsf_model", pa.string()),
            pa.field("gdr", pa.list_(LORENTZIAN_TYPE), nullable=False),
            pa.field("pygmy", pa.list_(LORENTZIAN_TYPE), nullable=False),
            pa.field("upbend_c", PARAM_TYPE),
            pa.field("upbend_eta", PARAM_TYPE),
            pa.field("omp_form", pa.string()),
            pa.field("omp", pa.list_(NAMED_PARAM_TYPE), nullable=False),
            pa.field("omp_irefs", pa.list_(pa.int32()), nullable=False),
            pa.field("fission_barriers", pa.list_(FISSION_BARRIER_TYPE), nullable=False),
            pa.field("source_version", pa.string()),
        ]
    )

    @model_validator(mode="after")
    def _derive_keys(self) -> StructureParams:
        key = nuclide_id(self.Z, self.N, self.iso)
        if self.nuclide_id is None:
            self.nuclide_id = key
        elif self.nuclide_id != key:
            raise ValueError(f"nuclide_id={self.nuclide_id!r} inconsistent with {key!r}")
        if len(self.gdr) > 2:
            raise ValueError("at most two GDR Lorentzians (spherical / deformed split)")
        idx = [b.index for b in self.fission_barriers]
        if len(idx) != len(set(idx)):
            raise ValueError("duplicate fission barrier index")
        return self

    @property
    def key(self) -> tuple[int, int, int]:
        return (self.Z, self.N, self.iso)
