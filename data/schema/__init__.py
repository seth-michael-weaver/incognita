"""Typed records every ingest writes and every model reads (blueprint §4.1, §9).

Each record is a Pydantic model with a paired ``pyarrow.Schema`` and generic
``to_arrow`` / ``from_arrow`` / ``write_parquet`` / ``read_parquet`` classmethods.
"""

from data.schema.base import (
    ArrowRecord,
    Datum,
    NamedParam,
    Param,
    Source,
    from_arrow,
    read_parquet,
    to_arrow,
    write_parquet,
)
from data.schema.evaluated import EvaluatedXS
from data.schema.keys import NuclideKey, nuclide_id, nuclide_id_from_za, parse_nuclide_id
from data.schema.measurement import DataBlock, Measurement, QuantityType, ReactionSF
from data.schema.nuclide import DECAY_MODES, DecayBranch, Nuclide
from data.schema.splits import SplitKind, SplitManifest, SplitRole
from data.schema.structure import FissionBarrier, Lorentzian, StructureParams

RECORD_TYPES: tuple[type[ArrowRecord], ...] = (
    Nuclide,
    StructureParams,
    Measurement,
    EvaluatedXS,
    SplitManifest,
)

__all__ = [
    "DECAY_MODES",
    "RECORD_TYPES",
    "ArrowRecord",
    "DataBlock",
    "Datum",
    "DecayBranch",
    "EvaluatedXS",
    "FissionBarrier",
    "Lorentzian",
    "Measurement",
    "NamedParam",
    "NuclideKey",
    "Nuclide",
    "Param",
    "QuantityType",
    "ReactionSF",
    "Source",
    "SplitKind",
    "SplitManifest",
    "SplitRole",
    "StructureParams",
    "from_arrow",
    "nuclide_id",
    "nuclide_id_from_za",
    "parse_nuclide_id",
    "read_parquet",
    "to_arrow",
    "write_parquet",
]
