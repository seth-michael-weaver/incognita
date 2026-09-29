"""WARM0: one nuclide cold, then warm -- the same run again after only the level-density (LD),
photon-strength (PSF) and decay caches were dropped.

ROUTE100's WP1. Nothing here is a TALYS routine and no number changes: it is `chartrun`'s
`engine.run(injection=ChainedFull(...))` called twice on one `Cascade`, with a cache drop in
between.

**What a warm pass is.** A fit step that moves only LD / PSF parameters keeps everything that is
a function of structure, the optical model and the energy grid: parsed structure and masses,
incident and inverse transmissions, coupled-channels and DWBA results, grids. It rebuilds
everything that reads a level density or a photon strength: `LDNucleus`, `GammaParameters`,
rhogrid, densprepare, target decay, the cascade, the pre-equilibrium spin population, fission
barrier densities, bookkeeping -- and, with today's cache granularity, the whole exciton model,
whose one cache (`pop_reference._preeq`) also holds the CN photo-absorption cross section of its
gamma emission rate. `drop_parameter_caches` drops exactly the caches of the second kind.

**Which caches those are is measured, not assumed** (`harness/route100_warm.py trace`): every
`lru_cache` and memo of `physics.hf` is proxied, every read of an `LDNucleus`, a
`GammaParameters` or an LD/PSF `Params` keyword is charged to the caches computing at that
moment, and the taint is closed over the cache-calls-cache graph. `DROP_LRU` / `DROP_ATTRS`
below are that trace's LD+PSF closure on the traced nuclides (docs/results/hf-warm0.md §3).

Memos keyed by `id()` of an `LDNucleus` / `GammaParameters` with an identity check
(`density.parameters._LD_FLOATS`, `compound.psf_fast._TABLES`, `emission.feeding._SPINCUT_PARTS`)
invalidate themselves when the object is rebuilt, so they need no drop; they are cleared anyway
so the warm pass pays for them as a real parameter step would.

TALYS: talysreaction.f90:1 (talysreaction)
Test: harness/route100_warm.py one (warm cells identical to cold)
"""

from __future__ import annotations

import functools
import sys
from dataclasses import dataclass, field

import numpy as np

# `lru_cache`d functions (module-qualified `__wrapped__` name) whose values read a level density
# or a photon strength, directly or through another cache (the trace's closure).
DROP_LRU: frozenset[str] = frozenset({
    "physics.hf.compound.dens_reference._ld_of_cached",
    "physics.hf.compound.dens_reference._gamma_parameters",
    # T8's exciton model reads the CN photon strength (`preeq.chain.chained_photoabsorption` ->
    # `gamma.transmission.gammaxs`: `xsreac(0, nen)`) and the pairing (`chained_pairing`)
    "physics.hf.compound.pop_reference._preeq",
    "physics.hf.emission.feed_reference._preeq_of",
})

# plain-dict memos (module, name) that hold LD / PSF-derived values
DROP_DICTS: tuple[tuple[str, str], ...] = (
    ("physics.hf.density.parameters", "_LD_FLOATS"),
    ("physics.hf.compound.psf_fast", "_TABLES"),
    ("physics.hf.emission.feeding", "_SPINCUT_PARTS"),
)

# `Cascade` instance attributes that hold LD / PSF-derived values (the rest of its state --
# `_setb_incident`, `_decay_fast_tl`, the per-instance `_levels`/`_sep`/`_discrete`/`incident`
# caches -- is structure and transmission, and is kept)
DROP_ATTRS: tuple[str, ...] = ("_spec_memo", "_gamma_override_fn")


def _lru_wrappers():
    """Every `lru_cache` wrapper of `physics.hf`: {qualified name: (wrapper, owner class)}."""
    out: dict[str, tuple] = {}
    for modname, mod in list(sys.modules.items()):
        if not modname.startswith("physics.hf") or mod is None:
            continue
        for obj in list(vars(mod).values()):
            obj = getattr(obj, "__warm0_lru__", obj)  # the WARM0 tracer's proxies
            if isinstance(obj, functools._lru_cache_wrapper):
                fn = obj.__wrapped__
                out.setdefault(f"{fn.__module__}.{fn.__qualname__}", (obj, None))
            elif isinstance(obj, type) and obj.__module__ == modname:
                for v in vars(obj).values():
                    v = getattr(v, "__warm0_lru__", v)
                    if isinstance(v, functools._lru_cache_wrapper):
                        fn = v.__wrapped__
                        out.setdefault(f"{fn.__module__}.{fn.__qualname__}", (v, obj))
    return out


def drop_parameter_caches(cas, drop_lru: frozenset[str] = DROP_LRU,
                          drop_dicts=DROP_DICTS, drop_attrs=DROP_ATTRS) -> list[str]:
    """Drop the LD / PSF / decay caches of this worker and of `cas`; keep everything else.

    TALYS: none (worker cache policy)
    Test: harness/route100_warm.py one
    """
    dropped = []
    for name, (w, _owner) in _lru_wrappers().items():
        if name in drop_lru:
            w.cache_clear()
            dropped.append(name)
    for modname, attr in drop_dicts:
        memo = getattr(sys.modules.get(modname), attr, None)
        if memo is not None:
            memo.clear()
            dropped.append(f"{modname}.{attr}")
    for attr in drop_attrs:
        if attr in cas.__dict__:
            del cas.__dict__[attr]
            dropped.append(f"Cascade.{attr}")
    return dropped


def run_on(Z: int, A: int, declared_energies: tuple[float, ...], cas):
    """`chartrun.run_nuclide` with the run's `Cascade` handed in (`ChainedFull(cascade=)`).

    TALYS: talysreaction.f90:1 (talysreaction)
    Test: harness/route100_warm.py one
    """
    import torch

    from physics.hf.engine import ChainedFull
    from physics.hf.engine import run as engine_run

    with torch.inference_mode():
        return engine_run(injection=ChainedFull(Z=Z, A=A, declared_energies=declared_energies,
                                                cascade=cas))


def new_cascade(Z: int, A: int, declared_energies: tuple[float, ...]):
    """The `Cascade` `ChainedFull.cases` would build for this run (float32 grid, as TALYS)."""
    import torch

    from physics.hf.emission.feeding import Cascade

    declared = tuple(float(np.float32(e)) for e in declared_energies)
    with torch.inference_mode():
        return Cascade(Z, A, max(declared), energies=declared)


def result_arrays(res) -> dict[str, np.ndarray]:
    """Every array of an `engine.run` `Results`, flat: "channels_mb/xs000000" -> (C,)."""
    out = {"e_inc_mev": res.e_inc_mev.detach().numpy().copy()}
    for part in ("channels_mb", "levels_mb", "residual_production_mb", "totals_mb"):
        for k, v in getattr(res, part).items():
            out[f"{part}/{k}"] = np.asarray(v.detach().numpy() if hasattr(v, "detach") else v,
                                            dtype=np.float64).copy()
    return out


def compare(cold: dict[str, np.ndarray], warm: dict[str, np.ndarray]) -> dict:
    """Cell-by-cell closeness of two `result_arrays`: keys, cells, max |d|, max relative d."""
    keys = sorted(set(cold) | set(warm))
    missing = [k for k in keys if k not in cold or k not in warm]
    n = nbits = 0
    dmax = rmax = 0.0
    worst = ""
    for k in keys:
        if k in missing:
            continue
        a, b = cold[k], warm[k]
        if a.shape != b.shape:
            missing.append(k)
            continue
        n += a.size
        same = (a == b) | (np.isnan(a) & np.isnan(b))
        nbits += int((~same).sum())
        d = np.abs(a - b)
        d = np.where(same, 0.0, d)
        if d.size and float(d.max()) > dmax:
            dmax, worst = float(d.max()), k
        with np.errstate(all="ignore"):
            r = np.where(same, 0.0, d / np.maximum(np.abs(a), np.abs(b)))
        if r.size:
            rmax = max(rmax, float(np.nanmax(r)))
    return {"arrays": len(keys), "cells": n, "cells_not_bitwise": nbits, "max_abs": dmax,
            "max_rel": rmax, "worst": worst, "missing": missing}


# ------------------------------------------------------------------------------ the inventory


@dataclass
class _Sizer:
    """Deep byte count of a cached value: numpy / torch buffers (each storage once) plus the
    Python containers around them; arrays >= `min_bytes` are listed with their path."""

    min_bytes: int = 4096
    seen: set = field(default_factory=set)  # shared across `inventory` so a buffer counts once
    arrays: list = field(default_factory=list)
    buffers: int = 0
    python: int = 0

    def walk(self, obj, path: str, depth: int = 0) -> None:
        import torch

        if depth > 12:
            return
        oid = id(obj)
        if oid in self.seen:
            return
        self.seen.add(oid)
        if isinstance(obj, torch.Tensor):
            try:
                st = obj.untyped_storage()
                key = ("t", st.data_ptr(), st.nbytes())
                nb = st.nbytes()
            except Exception:  # noqa: BLE001  (inference / sparse tensors)
                key, nb = ("t", oid), obj.element_size() * obj.nelement()
            if key not in self.seen:
                self.seen.add(key)
                self.buffers += nb
                if nb >= self.min_bytes:
                    self.arrays.append((path, "torch." + str(obj.dtype).split(".")[-1],
                                        tuple(obj.shape), nb))
            return
        if isinstance(obj, np.ndarray):
            base = obj
            while isinstance(base.base, np.ndarray):
                base = base.base
            key = ("n", id(base))
            if key not in self.seen:
                self.seen.add(key)
                self.buffers += base.nbytes
                if base.nbytes >= self.min_bytes:
                    self.arrays.append((path, str(obj.dtype), tuple(obj.shape), base.nbytes))
            return
        if isinstance(obj, (int, float, complex, bool, str, bytes, type(None), np.generic)):
            self.python += sys.getsizeof(obj)
            return
        if isinstance(obj, (type, functools.partial)) or (
                callable(obj) and not hasattr(obj, "__dict__")):
            return
        if type(obj).__module__ in ("builtins",) and not isinstance(obj, (dict, list, tuple, set,
                                                                          frozenset)):
            return
        self.python += sys.getsizeof(obj)
        if isinstance(obj, dict):
            for k, v in obj.items():
                self.walk(v, f"{path}[{k!r}]" if not isinstance(k, str) else f"{path}.{k}",
                          depth + 1)
        elif isinstance(obj, (list, tuple, set, frozenset)):
            for i, v in enumerate(obj):
                self.walk(v, f"{path}[{i}]", depth + 1)
        elif hasattr(obj, "__dict__") or hasattr(obj, "__slots__"):
            if type(obj).__name__ in ("Cascade", "module", "function"):
                return
            d = dict(getattr(obj, "__dict__", {}))
            for s in getattr(type(obj), "__slots__", ()):
                if hasattr(obj, s):
                    d[s] = getattr(obj, s)
            for k, v in d.items():
                self.walk(v, f"{path}.{k}", depth + 1)


def _lru_items(w):
    """(key, value) of every entry of an `lru_cache` wrapper, read back by calling it on its key
    (a hit; `typed=False` positional keys only -- kwargs keys are skipped)."""
    import gc

    store = [r for r in gc.get_referents(w) if isinstance(r, dict) and r is not w.__dict__
             and "__wrapped__" not in r]
    out = []
    for d in store:
        for key in list(d):
            args = key if isinstance(key, tuple) else (key,)
            if any(type(a) is object for a in args):
                continue
            try:
                out.append((key, w(*args)))
            except Exception:  # noqa: BLE001
                continue
    return out


# dict memos that live across targets (not in `chartrun._DICT_MEMOS`): only the keys a nuclide
# adds are its own
PERSISTENT_MEMOS: tuple[tuple[str, str], ...] = (
    ("physics.hf.structure.levels", "_LEVELS_CACHE"),
    ("physics.hf.ecis.solver", "_FD_CACHE"),
    ("physics.hf.compound.wfc", "_GAULEG"),
    ("physics.hf.gamma.strength", "_PARTITIONS"),
)

_STRUCTURE = ("structure.", "input.defaults", "_structure", "_levels", "._sep", "_discrete",
              "prepare._base",
              "_PARAMS_CACHE", "_defaults", "_coupled_band", "run_grid", "_LEVELS_CACHE",
              "_egrid")


def _short(key, depth: int = 0) -> str:
    """A cache key for an inventory path: numbers and strings as they are, long tuples (energy
    grids) by length, objects (`Options`, `Params`) by type name."""
    if isinstance(key, (int, float, str, bool, type(None), np.generic)):
        return repr(key)
    if isinstance(key, tuple):
        if len(key) > 6 or depth > 1:
            return f"<{len(key)}-tuple>"
        return "(" + ", ".join(_short(k, depth + 1) for k in key) + ")"
    return f"<{type(key).__name__}>"


def memo_keys() -> dict[str, set]:
    """The keys of `PERSISTENT_MEMOS` now; hand it to `inventory` taken before the cold run."""
    out = {}
    for modname, attr in PERSISTENT_MEMOS:
        memo = getattr(sys.modules.get(modname), attr, None)
        out[f"{modname}.{attr}"] = set(memo) if memo is not None else set()
    return out


def inventory(cas, min_bytes: int = 4096, before: dict[str, set] | None = None,
              max_arrays: int = 30) -> dict:
    """The caches a warm worker keeps for this nuclide, with sizes.

    {cache name: {"entries", "bytes", "buffer_bytes", "python_bytes", "arrays": [(path, dtype,
    shape, bytes)], "n_arrays", "scope": "nuclide" | "chart", "group": "physics" | "structure"}}.

    * Every buffer is counted once over the whole inventory: `Params` / `Options` / masses are
      shared by several structure caches and are charged to the first one visited.
    * "chart" caches are `chartrun.KEEP`'s pure ones (file parses, spin masks, 6j tables),
      shared by every nuclide and not part of a per-nuclide record.
    * Memos that outlive a target (`PERSISTENT_MEMOS`) count only the keys added since `before`.

    TALYS: none (worker cache policy)
    Test: harness/route100_warm.py one
    """
    import torch

    from physics.hf.chartrun import _DICT_MEMOS, KEEP

    seen: set = set()
    out: dict[str, dict] = {}

    def add(name: str, values: list, scope: str) -> None:
        sz = _Sizer(min_bytes, seen)
        for path, v in values:
            sz.walk(v, path)
        if not values:
            return
        arrays = sorted(sz.arrays, key=lambda a: -a[3])
        out[name] = {"entries": len(values), "bytes": sz.buffers + sz.python,
                     "buffer_bytes": sz.buffers, "python_bytes": sz.python,
                     "n_arrays": len(arrays), "arrays": arrays[:max_arrays], "scope": scope,
                     "group": "structure" if any(t in name for t in _STRUCTURE) else "physics"}

    wrappers = sorted(_lru_wrappers().items(),
                      key=lambda kv: (not any(t in kv[0] for t in _STRUCTURE), kv[0]))
    with torch.inference_mode():
        for name, (w, owner) in wrappers:
            if name in DROP_LRU:
                continue
            items = _lru_items(w)
            if owner is not None:  # per-instance caches: this run's Cascade only
                items = [(k[1:], v) for k, v in items
                         if isinstance(k, tuple) and k and k[0] is cas]
            short = name.rsplit(".", 1)[-1]
            add(name, [(f"{short}{_short(k)}", v) for k, v in items],
                "chart" if name in KEEP else "nuclide")
        memos = [(m, n) for m, ns in _DICT_MEMOS for n in ns] + list(PERSISTENT_MEMOS)
        for modname, attr in memos:
            if (modname, attr) in DROP_DICTS:
                continue
            memo = getattr(sys.modules.get(modname), attr, None)
            if not memo:
                continue
            full = f"{modname}.{attr}"
            if isinstance(memo, dict):
                old = (before or {}).get(full, set())
                items = [(f"{attr}[{_short(k)}]", v) for k, v in list(memo.items())
                         if k not in old]
            else:
                # NATIVEX2's one-entry memos (_GR_LAST, _CORE_LAST): a plain list holding the
                # last call's [struct, params, ...], not a key -> value cache
                items = [(f"{attr}[{i}]", v) for i, v in enumerate(memo)]
            add(full, items, "chart" if attr in ("_FD_CACHE", "_GAULEG") else "nuclide")
        for attr, v in sorted(cas.__dict__.items()):
            if attr in DROP_ATTRS or not attr.startswith("_") or v is None:
                continue
            add(f"Cascade.{attr}", [(f"Cascade.{attr}", v)], "nuclide")
    return out
