"""A cached value as a JSON skeleton plus flat arrays (CREC, ROUTE100 WP4).

The skeleton is plain JSON. Scalars (None, bool, int, float, str) are themselves -- `json` writes
a float with `repr`, which round-trips exactly, and NaN / Infinity as their tokens. Everything
else is a list whose first element is a tag:

    ["l", x...]  list          ["t", x...]  tuple        ["d", k, v, k, v...]  dict
    ["S", x...]  set           ["F", x...]  frozenset    ["c", re, im]         complex
    ["a", i]     numpy array i of the record's array table
    ["T", i]     torch tensor on the CPU, array i
    ["s", dtype, value]        numpy scalar
    ["o", "mod:Qual", name, v, name, v...]   an instance of a `physics.hf` class, fields set
                               without `__init__` (frozen dataclasses and `__slots__` included)
    ["n", "mod:Qual", x...]    a `physics.hf` NamedTuple
    ["lazy", keys, memo]       a `preeq.chain._ByEnergy`: its evaluated entries; the loader
                               rebuilds the map by calling the cached function and fills them in

An array met twice by identity is one entry of the table, so objects that shared an array still
do after loading. No class outside `physics.hf` is ever imported by the decoder.

TALYS: none (worker cache policy)
Test: scripts/hf_route100_record.py verify
"""

from __future__ import annotations

import dataclasses
import importlib
from collections.abc import Callable

import numpy as np
import torch

_PREFIX = "physics.hf."


class Unrecordable(TypeError):
    """A value the record cannot hold (a structure object, a closure, ...)."""


def _qual(obj_type: type) -> str:
    mod = obj_type.__module__
    if not mod.startswith(_PREFIX):
        raise Unrecordable(f"{mod}.{obj_type.__qualname__} is not a physics.hf class")
    return f"{mod}:{obj_type.__qualname__}"


def _resolve(q: str) -> type:
    mod, qual = q.split(":")
    if not mod.startswith(_PREFIX):
        raise ValueError(f"record names a class outside physics.hf: {q}")
    obj = importlib.import_module(mod)
    for part in qual.split("."):
        obj = getattr(obj, part)
    return obj


class Encoder:
    """Encodes values into skeletons, collecting arrays (`self.arrays`, numpy, in table order).

    `refuse` names classes that must not be recorded (structure objects the loader rebuilds).
    """

    def __init__(self, refuse: frozenset[str] = frozenset()) -> None:
        self.arrays: list[np.ndarray] = []
        self._ids: dict[int, int] = {}
        self._keep: list = []  # keeps encoded arrays alive, so their ids stay unique
        self.refuse = refuse

    def _array(self, obj, arr: np.ndarray) -> int:
        i = self._ids.get(id(obj))
        if i is None:
            i = self._ids[id(obj)] = len(self.arrays)
            self.arrays.append(arr)
            self._keep.append(obj)
        return i

    def encode(self, v, path: str = "$"):
        if v is None or isinstance(v, (bool, str)):
            return v
        if type(v) is int or type(v) is float:
            return v
        if isinstance(v, torch.Tensor):
            if v.requires_grad or v.device.type != "cpu" or v.is_sparse:
                raise Unrecordable(f"{path}: tensor on a graph / device / sparse")
            return ["T", self._array(v, np.ascontiguousarray(v.detach().numpy()))]
        if isinstance(v, np.ndarray):
            if v.dtype == object:
                raise Unrecordable(f"{path}: object array")
            return ["a", self._array(v, np.ascontiguousarray(v))]
        if isinstance(v, np.generic):
            return ["s", v.dtype.str, v.item() if not isinstance(v, np.complexfloating)
                    else [v.real.item(), v.imag.item()]]
        if type(v) is complex:
            return ["c", v.real, v.imag]
        if type(v) is list:
            return ["l", *(self.encode(x, f"{path}[{i}]") for i, x in enumerate(v))]
        if type(v) is tuple:
            return ["t", *(self.encode(x, f"{path}[{i}]") for i, x in enumerate(v))]
        if type(v) in (set, frozenset):
            return ["S" if type(v) is set else "F", *(self.encode(x, path) for x in v)]
        if type(v) is dict:
            out = ["d"]
            for k, x in v.items():
                out.append(self.encode(k, f"{path}.key"))
                out.append(self.encode(x, f"{path}[{k!r}]"))
            return out
        t = type(v)
        name = f"{t.__module__}.{t.__qualname__}"
        if name in self.refuse:
            raise Unrecordable(f"{path}: {name} is structure, not recorded")
        if name == "physics.hf.preeq.chain._ByEnergy":
            return ["lazy", self.encode(v._keys, path), self.encode(dict(v._memo), path)]
        if isinstance(v, tuple) and hasattr(t, "_fields"):
            return ["n", _qual(t), *(self.encode(x, f"{path}.{f}")
                                     for f, x in zip(t._fields, v, strict=True))]
        if isinstance(v, (Callable, type)) and not dataclasses.is_dataclass(v):
            raise Unrecordable(f"{path}: {name} is callable")
        fields = dict(getattr(v, "__dict__", {}))
        for cls in t.__mro__:
            for s in getattr(cls, "__slots__", ()):
                if s not in ("__dict__", "__weakref__") and hasattr(v, s):
                    fields[s] = getattr(v, s)
        if not fields and not dataclasses.is_dataclass(v):
            raise Unrecordable(f"{path}: {name} has no fields to record")
        out = ["o", _qual(t)]
        for f, x in fields.items():
            out.append(f)
            out.append(self.encode(x, f"{path}.{f}"))
        return out


class Decoder:
    """Rebuilds values from skeletons; `array(i)` returns the owned numpy array of table entry i
    (each entry is materialised once, so shared arrays stay shared)."""

    def __init__(self, array: Callable[[int], np.ndarray],
                 lazy: Callable[[object, dict], object] | None = None) -> None:
        self._array = array
        self._arrays: dict[int, np.ndarray] = {}
        self._tensors: dict[int, torch.Tensor] = {}
        self.lazy = lazy

    def array(self, i: int) -> np.ndarray:
        a = self._arrays.get(i)
        if a is None:
            a = self._arrays[i] = self._array(i)
        return a

    def decode(self, s):
        if not isinstance(s, list):
            return s
        tag = s[0]
        if tag == "a":
            return self.array(s[1])
        if tag == "T":
            t = self._tensors.get(s[1])
            if t is None:
                t = self._tensors[s[1]] = torch.from_numpy(self.array(s[1]))
            return t
        if tag == "t":
            return tuple(self.decode(x) for x in s[1:])
        if tag == "l":
            return [self.decode(x) for x in s[1:]]
        if tag == "d":
            it = iter(s[1:])
            return {self.decode(k): self.decode(x) for k, x in zip(it, it, strict=True)}
        if tag == "o":
            cls = _resolve(s[1])
            obj = cls.__new__(cls)
            it = iter(s[2:])
            for f, x in zip(it, it, strict=True):
                object.__setattr__(obj, f, self.decode(x))
            return obj
        if tag == "n":
            return _resolve(s[1])(*(self.decode(x) for x in s[2:]))
        if tag == "s":
            v = s[2]
            return np.dtype(s[1]).type(complex(*v) if isinstance(v, list) else v)
        if tag == "c":
            return complex(s[1], s[2])
        if tag == "S":
            return {self.decode(x) for x in s[1:]}
        if tag == "F":
            return frozenset(self.decode(x) for x in s[1:])
        if tag == "lazy":
            if self.lazy is None:
                raise ValueError("a lazy map needs the loader's rebuild hook")
            return self.lazy(self.decode(s[1]), self.decode(s[2]))
        raise ValueError(f"unknown record tag {tag!r}")
