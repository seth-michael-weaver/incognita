"""Split manifests (blueprint §4.4): which keys belong to which held-out set."""

from __future__ import annotations

from enum import StrEnum
from typing import ClassVar

import pyarrow as pa
from pydantic import Field, model_validator

from data.schema.base import STRING_MAP, ArrowRecord

__all__ = ["SplitKind", "SplitManifest", "SplitRole"]


class SplitKind(StrEnum):
    NUCLIDE = "nuclide"  # whole nuclides held out, stratified by mass region
    REGION = "region"  # contiguous (Z, N) block held out
    TIME = "time"  # retrodiction: train before year Y, test after
    ENERGY = "energy"  # energy band masked
    INTEGRAL = "integral"  # ICSBEP/IRPhEP benchmarks, validation only


class SplitRole(StrEnum):
    TRAIN = "train"
    VAL = "val"
    TEST = "test"


class SplitManifest(ArrowRecord):
    """One (split name, role) with its member keys.

    ``members`` are canonical keys of whatever the split partitions: nuclide ids for
    ``nuclide``/``region`` splits, EXFOR ``subentry`` ids for ``time`` splits, energy
    band labels for ``energy`` splits, benchmark case ids for ``integral`` splits.
    ``params`` carries the generating parameters as strings (e.g. ``{"year": "2012"}``,
    ``{"z_min": "50", "z_max": "60"}``) so a manifest is reproducible from itself.
    """

    name: str  # e.g. "nuclide-holdout-v1", "time-2012"
    kind: SplitKind
    role: SplitRole
    seed: int = 0
    members: list[str] = Field(default_factory=list)
    params: dict[str, str] = Field(default_factory=dict)
    version: str | None = None  # dataset release the split was frozen against
    description: str | None = None

    ARROW_SCHEMA: ClassVar[pa.Schema] = pa.schema(
        [
            pa.field("name", pa.string(), nullable=False),
            pa.field("kind", pa.string(), nullable=False),
            pa.field("role", pa.string(), nullable=False),
            pa.field("seed", pa.int64(), nullable=False),
            pa.field("members", pa.list_(pa.string()), nullable=False),
            pa.field("params", STRING_MAP, nullable=False),
            pa.field("version", pa.string()),
            pa.field("description", pa.string()),
        ]
    )

    @model_validator(mode="after")
    def _unique_members(self) -> SplitManifest:
        if len(set(self.members)) != len(self.members):
            raise ValueError("duplicate member keys in split manifest")
        if self.kind == SplitKind.INTEGRAL and self.role == SplitRole.TRAIN:
            raise ValueError("integral benchmarks are never a training split (§4.4)")
        return self

    @property
    def key(self) -> tuple[str, str]:
        return (self.name, self.role)
