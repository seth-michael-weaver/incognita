"""Shared machinery: the Pydantic base class every record inherits, the
uncertainty structs reused across records, and the Arrow/Parquet round trip.

Convention: each record class sets a ``pyarrow.Schema`` in ``ARROW_SCHEMA`` whose
column names match its Pydantic field names one-to-one. Nested models become
Arrow structs, ``list[...]`` becomes ``pa.list_``, ``dict[str, str]`` becomes a
map. ``to_arrow`` / ``from_arrow`` are generic on top of that convention, so
adding a field means touching exactly two lines: the Pydantic field and the
matching ``pa.field``.
"""

from __future__ import annotations

import math
from collections.abc import Iterable, Sequence
from enum import StrEnum
from pathlib import Path
from typing import Any, ClassVar, Self

import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq
from pydantic import BaseModel, ConfigDict, field_validator

__all__ = [
    "ArrowRecord",
    "Datum",
    "NamedParam",
    "Param",
    "Source",
    "from_arrow",
    "read_parquet",
    "to_arrow",
    "write_parquet",
]


class Source(StrEnum):
    """Where a Tier 2 structure parameter came from (§4.2 RIPL)."""

    MEASURED = "measured"
    SYSTEMATICS = "systematics"


def _as_float_list(v: Any) -> Any:
    """Accept numpy arrays / tuples for list[float] fields; leave everything else alone."""
    if isinstance(v, np.ndarray):
        return v.astype(np.float64).tolist()
    if isinstance(v, tuple):
        return list(v)
    return v


class _Model(BaseModel):
    model_config = ConfigDict(extra="forbid", use_enum_values=True)


class Datum(_Model):
    """A measured/evaluated value with its 1-σ uncertainty (Tier 1 nuclide properties).

    ``extrapolated`` marks AME/NUBASE ``#`` values, which are held out of training (§4.2).
    """

    value: float
    sigma: float | None = None
    extrapolated: bool = False

    @field_validator("sigma")
    @classmethod
    def _nonneg(cls, v: float | None) -> float | None:
        if v is not None and (v < 0 or math.isnan(v)):
            raise ValueError("sigma must be >= 0")
        return v


class Param(_Model):
    """A Tier 2 structure parameter: value, σ and whether it is measured or systematics."""

    value: float
    sigma: float | None = None
    source: Source = Source.SYSTEMATICS

    @field_validator("sigma")
    @classmethod
    def _nonneg(cls, v: float | None) -> float | None:
        if v is not None and (v < 0 or math.isnan(v)):
            raise ValueError("sigma must be >= 0")
        return v


class NamedParam(Param):
    """A ``Param`` with a name, for open-ended parameter sets such as OMP potentials."""

    name: str


# Arrow types for the structs above; imported by the record modules.
DATUM_TYPE = pa.struct(
    [
        pa.field("value", pa.float64(), nullable=False),
        pa.field("sigma", pa.float64()),
        pa.field("extrapolated", pa.bool_(), nullable=False),
    ]
)
PARAM_TYPE = pa.struct(
    [
        pa.field("value", pa.float64(), nullable=False),
        pa.field("sigma", pa.float64()),
        pa.field("source", pa.string(), nullable=False),
    ]
)
NAMED_PARAM_TYPE = pa.struct(
    [
        pa.field("value", pa.float64(), nullable=False),
        pa.field("sigma", pa.float64()),
        pa.field("source", pa.string(), nullable=False),
        pa.field("name", pa.string(), nullable=False),
    ]
)
FLOAT_LIST = pa.list_(pa.float64())
STRING_MAP = pa.map_(pa.string(), pa.string())


class ArrowRecord(_Model):
    """Base class for the five table records. Subclasses define ``ARROW_SCHEMA``."""

    ARROW_SCHEMA: ClassVar[pa.Schema]

    @classmethod
    def arrow_schema(cls) -> pa.Schema:
        return cls.ARROW_SCHEMA

    def to_row(self) -> dict[str, Any]:
        """Plain-Python row in the shape ``pyarrow`` expects (enums as str, maps as lists)."""
        row = self.model_dump(mode="python")
        for name, typ in zip(self.ARROW_SCHEMA.names, self.ARROW_SCHEMA.types, strict=True):
            if pa.types.is_map(typ) and isinstance(row.get(name), dict):
                row[name] = list(row[name].items())
        return row

    @classmethod
    def from_row(cls, row: dict[str, Any]) -> Self:
        """Inverse of :meth:`to_row`; ``pyarrow`` hands maps back as lists of pairs."""
        row = dict(row)
        for name, typ in zip(cls.ARROW_SCHEMA.names, cls.ARROW_SCHEMA.types, strict=True):
            if pa.types.is_map(typ) and isinstance(row.get(name), list):
                row[name] = dict(row[name])
        return cls.model_validate(row)

    @classmethod
    def to_arrow(cls, records: Iterable[Self]) -> pa.Table:
        """Records → ``pyarrow.Table`` with :attr:`ARROW_SCHEMA` (validated on the way in)."""
        rows = []
        for r in records:
            if not isinstance(r, cls):
                raise TypeError(f"expected {cls.__name__}, got {type(r).__name__}")
            rows.append(r.to_row())
        return pa.Table.from_pylist(rows, schema=cls.ARROW_SCHEMA)

    @classmethod
    def from_arrow(cls, table: pa.Table | pa.RecordBatch) -> list[Self]:
        """``pyarrow.Table`` → validated records. Extra columns are an error, not ignored."""
        extra = set(table.schema.names) - set(cls.ARROW_SCHEMA.names)
        if extra:
            raise ValueError(f"{cls.__name__}: unexpected columns {sorted(extra)}")
        return [cls.from_row(row) for row in table.to_pylist()]

    @classmethod
    def write_parquet(cls, records: Iterable[Self], path: str | Path, **kwargs: Any) -> Path:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        pq.write_table(cls.to_arrow(records), path, **kwargs)
        return path

    @classmethod
    def read_parquet(cls, path: str | Path, **kwargs: Any) -> list[Self]:
        return cls.from_arrow(pq.read_table(path, schema=cls.ARROW_SCHEMA, **kwargs))


def to_arrow(records: Sequence[ArrowRecord]) -> pa.Table:
    """Module-level convenience: infers the record class from the first element."""
    if not records:
        raise ValueError("cannot infer record type from an empty sequence; use Cls.to_arrow")
    return type(records[0]).to_arrow(records)


def from_arrow[T: ArrowRecord](table: pa.Table, record_type: type[T]) -> list[T]:
    return record_type.from_arrow(table)


def write_parquet(records: Sequence[ArrowRecord], path: str | Path, **kwargs: Any) -> Path:
    if not records:
        raise ValueError("cannot infer record type from an empty sequence; use Cls.write_parquet")
    return type(records[0]).write_parquet(records, path, **kwargs)


def read_parquet[T: ArrowRecord](path: str | Path, record_type: type[T], **kwargs: Any) -> list[T]:
    return record_type.read_parquet(path, **kwargs)


# Used by record modules so list[float] fields also accept numpy arrays.
as_float_list = _as_float_list
