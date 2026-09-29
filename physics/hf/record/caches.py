"""Which caches a record holds, captured after a run and seeded into a new one (CREC, WP4).

**What is recorded.** WARM0's inventory (docs/results/hf-warm0.md §5) of what a warm worker keeps,
less two groups:

* structure (`Options`, `Params`, `Masses`, `Levels`, parsed files): ~108 MB of tensors per
  nuclide rebuilt from TALYS's own database, and what a record would store is their source rows,
  which are already on disk. They are rebuilt on first use (`REFUSE` makes the encoder fail on
  any recorded value that holds one, so a record never carries a stale copy);
* WARM0's taint set (`warmrun.DROP_LRU`, `DROP_DICTS`, `DROP_ATTRS`): everything a level density
  or photon strength reaches. `RECORDED` is checked disjoint from it, so a PARAMWIRE parameter
  set never needs a record rebuilt -- its caches are keyed by the entries they read and computed
  in the run.

What is left is the optical model and direct-reaction physics: incident channels (spherical
axis tables and coupled-channels solves), inverse transmissions, reaction cross sections, the
DWBA / giant-resonance blocks and the OMP parameters per energy.

**How an `lru_cache` entry is seeded.** An `lru_cache` wrapper has no insert. `seed` calls the
wrapper on the recorded arguments with the wrapped function's code object temporarily swapped for
one that returns the recorded value, so the entry is stored under exactly the key the run will
look up (argument types, `typed`, keyword order all as the original call). Only functions
without closure cells can be seeded this way; the recorded ones are module-level functions and
one method.

TALYS: none (worker cache policy)
Test: scripts/hf_route100_record.py verify
"""

from __future__ import annotations

import functools
import hashlib
import importlib
import json
import sys
from pathlib import Path

from physics.hf import warmrun
from physics.hf.record import codec

FORMAT = 1

# `lru_cache`d functions (qualified `__wrapped__` name); `Cascade.incident` is per instance, keyed
# on the run's Cascade
RECORDED_LRU: tuple[str, ...] = (
    "physics.hf.emission.feeding.Cascade.incident",
    "physics.hf.compound.dens_reference._transmission_cached",
    "physics.hf.compound.dens_reference._eendmax",
    "physics.hf.preeq.chain.inverse_reaction_xs",
    "physics.hf.preeq.chain.incident_reaction_xs",
    "physics.hf.preeq.chain.chained_direct",
    "physics.hf.emission.feed_reference._giant_of",
    "physics.hf.direct.chain._omp_grid",
    "physics.hf.direct.chain._omp_at",
    "physics.hf.direct.chain._coupled_cached",
)

# plain-dict memos (module, name): entries this run added
RECORDED_DICTS: tuple[tuple[str, str], ...] = (
    ("physics.hf.ecis.incident", "_SOLVED"),
)

# `Cascade` instance attributes: SETB's incident axis table, the NATIVEX decay transmissions and
# RnJ, and the coupled-channels `xscoupled` that `Cascade.incident` records as it solves
RECORDED_ATTRS: tuple[str, ...] = ("_setb_incident", "_decay_fast_tl", "_nativex_rnj",
                                   "_xscoupled")

# structure classes a recorded value must not hold
REFUSE: frozenset[str] = frozenset({
    "physics.hf.input.defaults.Options",
    "physics.hf.input.defaults.Params",
    "physics.hf.structure.masses.Masses",
    "physics.hf.structure.levels.Levels",
    "physics.hf.emission.feeding.Cascade",
})


def _check_disjoint() -> None:
    lru = set(RECORDED_LRU) & set(warmrun.DROP_LRU)
    dicts = set(RECORDED_DICTS) & set(warmrun.DROP_DICTS)
    attrs = set(RECORDED_ATTRS) & set(warmrun.DROP_ATTRS)
    if lru or dicts or attrs:
        raise AssertionError(f"recorded caches in WARM0's taint set: {lru | dicts | attrs}")


_check_disjoint()


# ------------------------------------------------------------------------------ the record key


def _sha(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True).encode()).hexdigest()[:16]


def taint_signature() -> str:
    """WARM0's taint set and PARAMWIRE's parameter keywords: a change to either changes what a
    record may hold."""
    from physics.hf.density.overrides import FIT_KEYS

    return _sha([sorted(warmrun.DROP_LRU), sorted(map(list, warmrun.DROP_DICTS)),
                 sorted(warmrun.DROP_ATTRS), sorted(FIT_KEYS)])


def recorded_signature() -> str:
    return _sha([FORMAT, list(RECORDED_LRU), [list(x) for x in RECORDED_DICTS],
                 list(RECORDED_ATTRS), sorted(REFUSE)])


@functools.lru_cache(maxsize=1)
def code_signature() -> str:
    """The port's source: every `.py`, `.c` and `.h` under `physics/hf` outside this package."""
    root = Path(__file__).resolve().parents[1]
    h = hashlib.sha256()
    for p in sorted(root.rglob("*")):
        if p.suffix not in (".py", ".c", ".h") or "__pycache__" in p.parts:
            continue
        rel = p.relative_to(root)
        if rel.parts[0] == "record":
            continue
        h.update(str(rel).encode())
        h.update(p.read_bytes())
    return h.hexdigest()[:16]


def record_key(cas, code: bool = True) -> dict:
    """What a record is valid for: the nuclide, its run (maximum and declared energies,
    projectile) and the three signatures (`code=False` leaves out the source hash).

    TALYS: none (worker cache policy)
    Test: scripts/hf_route100_record.py verify
    """
    key = {"format": FORMAT, "Z": int(cas.Zt), "A": int(cas.At), "k0": int(cas.k0),
           "enincmax": float(cas.enincmax), "energies": [float(e) for e in cas.energies],
           "taint": taint_signature(), "recorded": recorded_signature()}
    if code:
        key["code"] = code_signature()
    return key


def _overridden(cas) -> bool:
    return bool(getattr(cas, "density_overrides", None) or getattr(cas, "omp_overrides", None)
                or getattr(cas, "diff_params", False))


# ------------------------------------------------------------------------------ capture


def _wrappers() -> dict[str, functools._lru_cache_wrapper]:
    """The recorded wrappers by name, importing their modules (a fresh worker has not yet)."""
    out = {}
    for name in RECORDED_LRU:
        parts = name.split(".")
        for cut in range(len(parts) - 1, 0, -1):
            try:
                obj = importlib.import_module(".".join(parts[:cut]))
            except ModuleNotFoundError:
                continue
            for p in parts[cut:]:
                obj = getattr(obj, p)
            break
        if not isinstance(obj, functools._lru_cache_wrapper):
            raise TypeError(f"{name} is not an lru_cache")
        out[name] = obj
    return out


def _split_key(key) -> tuple[tuple, dict]:
    """An `lru_cache` key (typed=False) back into (args, kwargs)."""
    if not isinstance(key, tuple):
        return (key,), {}
    for i, x in enumerate(key):
        if type(x) is object:  # the C implementation's keyword marker
            rest = key[i + 1:]
            return key[:i], dict(zip(rest[::2], rest[1::2], strict=True))
    return key, {}


def _lru_store(w) -> dict:
    import gc

    # a bounded cache's referents are its linked entries (key, result -- which may itself be a
    # dict) and then the key -> entry dict, whose values are `functools._lru_list_elem`
    if w.cache_info().maxsize is None:
        raise TypeError(f"{w.__wrapped__.__qualname__}: unbounded caches are not recorded")
    for r in gc.get_referents(w):
        if (isinstance(r, dict) and r
                and all(type(x).__name__ == "_lru_list_elem" for x in r.values())):
            return r
    return {}


def capture(cas, before: dict[str, set] | None = None) -> tuple[list, list, list[str]]:
    """The recorded caches after a run on `cas`: (entries, arrays, skipped).

    `entries` are `["lru", name, self?, args, kwargs, value]`, `["dict", module, name, key,
    value]` and `["attr", name, value]` skeletons; `before` (from `dict_keys()`, taken before the
    run) limits the dict memos to the keys this run added. `skipped` names what could not be
    encoded, with the reason.

    TALYS: none (worker cache policy)
    Test: scripts/hf_route100_record.py build
    """
    import torch

    enc = codec.Encoder(REFUSE)
    entries: list = []
    skipped: list[str] = []
    with torch.inference_mode():
        for name, w in _wrappers().items():
            method = name == "physics.hf.emission.feeding.Cascade.incident"
            for key in list(_lru_store(w)):
                args, kwargs = _split_key(key)
                if method:
                    if not args or args[0] is not cas:
                        continue
                    args = args[1:]
                try:
                    value = (w(cas, *args, **kwargs) if method else w(*args, **kwargs))
                    entries.append(["lru", name, method, enc.encode(list(args)),
                                    enc.encode(kwargs), enc.encode(value, name)])
                except codec.Unrecordable as e:
                    skipped.append(f"{name}{args!r}: {e}")
        for modname, attr in RECORDED_DICTS:
            memo = getattr(sys.modules.get(modname), attr, None) or {}
            old = (before or {}).get(f"{modname}.{attr}", set())
            for k, v in list(memo.items()):
                if k in old:
                    continue
                try:
                    entries.append(["dict", modname, attr, enc.encode(k), enc.encode(v)])
                except codec.Unrecordable as e:
                    skipped.append(f"{modname}.{attr}[{k!r}]: {e}")
        for attr in RECORDED_ATTRS:
            if attr in cas.__dict__:
                try:
                    entries.append(["attr", attr, enc.encode(cas.__dict__[attr], attr)])
                except codec.Unrecordable as e:
                    skipped.append(f"Cascade.{attr}: {e}")
    return entries, enc.arrays, skipped


def dict_keys() -> dict[str, set]:
    """The keys of `RECORDED_DICTS` now (hand to `capture` taken before the run)."""
    out = {}
    for modname, attr in RECORDED_DICTS:
        memo = getattr(sys.modules.get(modname), attr, None)
        out[f"{modname}.{attr}"] = set(memo) if memo is not None else set()
    return out


# ------------------------------------------------------------------------------ seed


def _returns_seed(*args, **kwargs):
    return __crec_seed__  # noqa: F821  (looked up in the seeded function's own globals)


def _seed_lru(w, args: tuple, kwargs: dict, value) -> bool:
    """Store `value` in `w` under the key of `w(*args, **kwargs)`; False if already there."""
    fn = w.__wrapped__
    code, g = fn.__code__, fn.__globals__
    if code.co_freevars:
        raise TypeError(f"{fn.__qualname__}: a closure cannot be seeded")
    misses = w.cache_info().misses
    fn.__code__ = _returns_seed.__code__
    g["__crec_seed__"] = value
    try:
        w(*args, **kwargs)
    finally:
        fn.__code__ = code
        del g["__crec_seed__"]
    return w.cache_info().misses > misses


class RecordMismatch(ValueError):
    """The record was written for another run, taint set, cache list or source."""


def check_key(key: dict, cas, check_code: bool = True) -> None:
    """Raise `RecordMismatch` unless `key` is valid for a run on `cas`.

    TALYS: none (worker cache policy)
    Test: scripts/hf_route100_record.py verify
    """
    if _overridden(cas):
        raise RecordMismatch("the Cascade carries density / optical overrides")
    want = record_key(cas, check_code)
    bad = [k for k in want if key.get(k) != want[k]]
    if bad:
        raise RecordMismatch(f"record key differs in {bad}")


def seed(rec, cas, check_code: bool = True) -> dict:
    """Seed a `store.NuclideRecord` into this worker's caches and `cas`, before the run.

    Returns {"lru": entries stored, "lru_present": already cached, "dict", "attr"}.

    TALYS: none (worker cache policy)
    Test: scripts/hf_route100_record.py verify
    """
    import torch

    check_key(rec.key, cas, check_code)
    wrappers = _wrappers()
    counts = {"lru": 0, "lru_present": 0, "dict": 0, "attr": 0}
    dec = codec.Decoder(rec.array)  # one per record: arrays shared across entries stay shared
    with torch.inference_mode():
        for e in rec.entries:
            kind = e[0]
            if kind == "lru":
                _k, name, method, s_args, s_kwargs, s_value = e
                w = wrappers[name]
                args = tuple(dec.decode(s_args))
                kwargs = dec.decode(s_kwargs)

                def lazy(keys, memo, w=w, args=args, kwargs=kwargs, name=name):
                    # `preeq.chain._ByEnergy`: the map as the cached function builds it (no
                    # energy is evaluated by building it), with the recorded energies filled in
                    m = w.__wrapped__(*args, **kwargs)
                    if tuple(m._keys) != tuple(keys):
                        raise RecordMismatch(f"{name}: lazy map keys differ")
                    m._memo.update(memo)
                    return m

                dec.lazy = lazy
                value = dec.decode(s_value)
                call = (cas, *args) if method else args
                counts["lru" if _seed_lru(w, call, kwargs, value) else "lru_present"] += 1
            elif kind == "dict":
                _k, modname, attr, s_key, s_value = e
                memo = getattr(importlib.import_module(modname), attr)
                k = dec.decode(s_key)
                if k not in memo:
                    memo[k] = dec.decode(s_value)
                    counts["dict"] += 1
            else:
                _k, attr, s_value = e
                if attr not in cas.__dict__:
                    cas.__dict__[attr] = dec.decode(s_value)
                    counts["attr"] += 1
    return counts
