"""CCCACHE: a DISK cache for the incident coupled-channels solve.

The coupled-channels (incident-channel) solve is 77 % of a deformed target's engine time
(Dy-163: 4.9 of 6.4 CPU-s, 87 `ccnative._keep_raw` calls; U-238: 2.4 of 5.7 s) and it depends on
NOTHING that a level-density or photon-strength variant changes.  `ecis.incident._SOLVED` already
memoises one row per (target, energy) per PROCESS -- a second run of the same nuclide in the same
process costs 0.95 s and solves zero blocks -- but every worker, every sweep point and every
rerun starts with an empty one.  This module is that memo, on disk.

    INCOGNITA_CC_CACHE=<dir>     turn it on;  unset = today's behaviour, bit for bit.

**Key.**  Not a list of keyword names, but the tuple `incident_coupled` itself hands `_SOLVED`
(`incident.py`, CCFAST2): `(Z, A, particle, band_key, lmax, allow_undeformed_spin_orbit,
soswitch, E, the 19 OMP parameters AT THAT ENERGY, refine)`.  So it is the solver's own inputs:
an `rvadjust`/`avadjust` from the PARAMWIRE/fitlib route, a different OMP file, a different
deformation (`INCOGNITA_OMP_DEFORMED=1`) or a different energy grid all change the numbers that go
in and therefore the key, and cannot hit a stale entry.  The key is hashed with sha256 over a
typed, exact encoding (float64 bytes for every float, never `repr`), together with

**the version** (`_version`): the source bytes of the modules that produce the row
(`ecis/solver.py`, `ccnative.py`, `incident.py`, `vibm.py`, `coupling.py`, `formfactor.py`,
`omp/schrodinger.py`, and the loaders they call through), the bytes of the native libraries the
solve runs on, whether those are actually loaded, the values of every `HF_*` numerics switch
those modules read, the torch version (ccfast calls torch's MKL by address), and `FORMAT` below.
Rebuild a kernel the solve runs or edit the solver and the whole cache is bypassed rather than
trusted; bump `FORMAT` for any change to the stored payload itself.

CCKEY: "the libraries the solve runs on" is what a call trace inside `solve_rotational` /
`solve_vibrational` shows (development notes): `libccfast`/`libccsplit`,
`libhfnative` (`hf_cf1`; `hf_cc_block` on the exact path) and the provider of the `omp` kernels.
`libnx2` is NOT among them in a normal build: its `nx2_omp_*` kernels are swapped for
`libsetup`'s copies of the same translation unit (`setup_c.swap`), and the rest of `libnx2` --
PSF, level densities, the cascade -- never runs inside the solve.  So the provider of each `omp`
kernel is resolved here exactly as `omp_nx2._kernel` resolves it and only that library's bytes
are hashed: a PSF edit no longer throws the whole cache away, while a build without `libsetup`
(where `libnx2` really does serve the kernels) still keys on `libnx2`.

The source / library part of the version is computed once per process; the switches part
(`env_token`: every HF_* / INCOGNITA_* switch a CC-scope source names, less stagedisk's deny-lists)
is read per call
(ENGFIX4), and so is the cache DIRECTORY, so a test can turn the cache on and off in one process.

**Storage.**  One file per key, `<dir>/<version>/<ab>/<digest>.npz`, float64 raw through
`numpy.savez` (no text, exact round-trip), written to a temporary file in the same directory and
`os.replace`d into place, because 8-16 workers share one directory and a half-written file must
never be readable.  Every read is guarded: a truncated, corrupt or key-mismatched file is a MISS
and the row is recomputed (and rewritten).  Nothing here can change a number -- a hit is only
taken when the stored key bytes equal the asked-for key bytes.

Task: CCCACHE.  Test: tests/hf/test_ccdisk.py; gates in development notes.
"""

from __future__ import annotations

import hashlib
import os
import stat
import struct
import tempfile
from functools import lru_cache
from pathlib import Path

import numpy as np
import torch

from physics.hf.core.tensors import DTYPE

FORMAT = 1  # bump when the stored payload changes shape or meaning

ENV_VAR = "INCOGNITA_CC_CACHE"

# every environment switch the CC modules read that can move a number
_NUMERICS_ENV: tuple[str, ...] = (
    "HF_CCBLOCKD", "HF_CCBLOCKD_SMALL", "HF_CCFAST_LIB", "HF_CCFAST_NATIVE", "HF_CCGLUE",
    "HF_CCSPLIT", "HF_CC_GEMM_SMALL", "HF_CC_MODNUM", "HF_INC_REFINE", "HF_INC_REFINE_EMAX",
    "HF_NX2_CCX", "HF_NX2_SWEEP", "HF_NX2_GEMM", "HF_NATIVE", "HF_NATIVEX",
    # CCKEY: the loaders the solve goes through (native/__init__, nx2, setup_c, omp_nx2); their
    # `*_LIB` path overrides are not keyed by name, the bytes of the library loaded are
    "HF_NX2", "HF_NX2_OMP", "HF_SETUP",
)

_SOURCES: tuple[str, ...] = (
    "physics/hf/ecis/solver.py", "physics/hf/ecis/ccnative.py", "physics/hf/ecis/incident.py",
    "physics/hf/ecis/vibm.py", "physics/hf/ecis/coupling.py", "physics/hf/ecis/formfactor.py",
    "physics/hf/omp/schrodinger.py",
    # CCKEY: the rest of what the call trace found running inside the solve
    "physics/hf/core/angmom.py", "physics/hf/native/__init__.py", "physics/hf/native/nx2.py",
    "physics/hf/native/setup_c.py", "physics/hf/omp/omp_nx2.py",
)

# CC-only libraries, hashed whenever present (as CCCACHE did)
_LIBS: tuple[str, ...] = ("libccfast", "libccsplit")

# the `omp` lever's kernels (omp/omp_nx2.py); their provider is resolved per kernel
_OMP_KERNELS: tuple[str, ...] = ("nx2_omp_card", "nx2_omp_coulomb", "nx2_omp_grid", "nx2_omp_job",
                                 "nx2_omp_set_numerov")

# the six arrays of `incident._row`, in order
_ARRAYS: tuple[str, ...] = ("sigma_tot_mb", "sigma_reac_mb", "sigma_abs_mb",
                            "sigma_shape_el_mb", "sigma_direct_mb", "tjl")

_stats = {"hit": 0, "miss": 0, "write": 0, "bad": 0}


def stats() -> dict[str, int]:
    """Counters since the process started: hits, misses, files written, files rejected."""
    return dict(_stats)


def reset_stats() -> None:
    for k in _stats:
        _stats[k] = 0


def directory() -> Path | None:
    """The cache directory, or None when `INCOGNITA_CC_CACHE` is unset or empty.

    Read per call, not at import: a worker sets the variable after this module is imported, and
    the tests turn the cache on and off in one process.
    """
    d = os.environ.get(ENV_VAR)
    if not d:
        return None
    return Path(d)


def enabled() -> bool:
    return directory() is not None


BATCH_ENV_VAR = "INCOGNITA_CC_BATCHCACHE"


def batch_directory() -> Path | None:
    """PERFCC2: the directory of `incident`'s whole-batch carry (`incident._CARRY` on disk), or None
    when `INCOGNITA_CC_BATCHCACHE` is unset or empty. Same file format, same version directories
    and the same guards as the row cache; only the keys differ (a whole batch's ordered row keys,
    so a hit is bit for bit the solve it replaces). Read per call."""
    d = os.environ.get(BATCH_ENV_VAR)
    return Path(d) if d else None


# ---------------------------------------------------------------------------------------------
# the key


def _encode(obj, out: bytearray) -> None:
    """A typed, exact byte encoding of the key tuple.  Floats go in as their eight IEEE bytes, so
    two keys collide only if every input really is the same double.  An unknown type raises, and
    the caller then simply does not cache (never caches under a lossy key)."""
    if obj is None:
        out += b"N"
    elif isinstance(obj, bool):  # before int: bool IS an int
        out += b"B" + (b"\x01" if obj else b"\x00")
    elif isinstance(obj, int):
        out += b"I" + str(obj).encode("ascii") + b";"
    elif isinstance(obj, float):
        out += b"F" + struct.pack("<d", obj)
    elif isinstance(obj, str):
        b = obj.encode("utf-8")
        out += b"S" + str(len(b)).encode("ascii") + b":" + b
    elif isinstance(obj, bytes):
        out += b"Y" + str(len(obj)).encode("ascii") + b":" + obj
    elif isinstance(obj, (tuple, list)):
        out += b"(" + str(len(obj)).encode("ascii") + b":"
        for x in obj:
            _encode(x, out)
        out += b")"
    else:
        raise TypeError(f"cc cache key holds a {type(obj).__name__}")


def key_bytes(key: tuple) -> bytes:
    out = bytearray()
    _encode(key, out)
    return bytes(out)


def _file_digest(path) -> bytes:
    p = Path(path) if path else None
    return hashlib.sha256(p.read_bytes()).digest() if p is not None and p.is_file() else b"missing"


def _omp_providers() -> list[tuple[str, str, str | None]]:
    """(kernel, "setup" | "nx2" | "none", library path) for each `omp` kernel, resolved as
    `omp_nx2._kernel` resolves it: `nx2.kernel(name, lever="omp")` must exist (else the Python
    path runs), then `setup_c.swap` takes libsetup's symbol when libsetup has it."""
    from physics.hf.native import nx2, setup_c

    out = []
    base = nx2.lib() if os.environ.get("HF_NX2_OMP", "1") != "0" else None
    so = setup_c.lib()
    for name in _OMP_KERNELS:
        if base is None or not hasattr(base, name):
            out.append((name, "none", None))
        elif so is not None and hasattr(so, setup_c.ALIAS.get(name, name)):
            out.append((name, "setup", so._name))
        else:
            out.append((name, "nx2", base._name))
    return out


# ENGFIX4: the switches of the CC solve are found, not listed: every HF_* / INCOGNITA_* name written
# in the CC scope's sources (the modules the solve runs, the optical-model package that builds its
# potential, and the C kernels it calls), less stagedisk's deny-lists (cache locations,
# diagnostics, derived *_EFF, LD / PSF / cascade levers). A switch only other code reads -- a
# production run's hold-rule and pre-equilibrium passes set INCOGNITA_ISOHOLD, _ISOE2, _FEWRES,
# _PEWINDOW between set-ups -- is not a CC input: keying on it would re-solve rows the run already
# holds in another batch (last-bit changes, PERFCC2's batch rule) for nothing.
_ENV_SCOPE_GLOBS: tuple[str, ...] = (
    "physics/hf/ecis/*.py", "physics/hf/omp/*.py", "physics/hf/native/__init__.py",
    "physics/hf/native/nx2.py", "physics/hf/native/setup_c.py", "physics/hf/core/angmom.py",
    "physics/hf/native/ccfast.c", "physics/hf/native/ccprop.c", "physics/hf/native/ccsplit.h",
    "physics/hf/native/hfnative.c", "physics/hf/native/nx2_omp.c",
)


@lru_cache(maxsize=1)
def env_names() -> tuple[str, ...]:
    """The environment switches the CC solve can read (see `_ENV_SCOPE_GLOBS`), sorted."""
    import re

    from physics.hf import stagedisk

    root = Path(__file__).resolve().parents[3]
    pat = re.compile(r"\b((?:HF|INCOGNITA)_[A-Z0-9_]*[A-Z0-9])\b")
    names = set(_NUMERICS_ENV)
    for g in _ENV_SCOPE_GLOBS:
        for p in sorted(root.glob(g)):
            if p.name == "ccdisk.py":  # this module: its switches are `_NUMERICS_ENV` and the cache dirs
                continue
            names |= set(pat.findall(p.read_text(encoding="utf-8", errors="replace")))
    names -= stagedisk.ENV_EXCLUDE | {ENV_VAR, BATCH_ENV_VAR}
    return tuple(sorted(names))


_ENV_TOKENS: dict = {}


def env_token() -> str:
    """ENGFIX4: the switches part of every CC cache key, read on every call -- the row cache
    (`_version`), `incident._SOLVED` and PERFCC2's batch carry (memory and INCOGNITA_CC_BATCHCACHE):
    the values of `env_names()` (INCOGNITA_ECMSTABLE, INCOGNITA_CCSOCB, the OMP region / deformed
    switches, HF_INC_REFINE(_EMAX), every HF_* numerics switch, and any switch a CC module reads
    later, without a list to keep)."""
    raw = os.environ._data  # bytes -> bytes
    vals = tuple(raw.get(k.encode()) for k in env_names())
    tok = _ENV_TOKENS.get(vals)
    if tok is None:
        if len(_ENV_TOKENS) > 64:
            _ENV_TOKENS.clear()
        h = hashlib.sha256(b"ccenv")
        for k, v in zip(env_names(), vals):
            h.update(k.encode() + b"=" + (b"\x01" if v is None else v) + b"\x00")
        tok = _ENV_TOKENS[vals] = h.hexdigest()[:24]
    return tok


_VERSIONS: dict = {}


def _version() -> str:
    """The cache's version directory: `_static_version` (source, libraries, torch) with the
    switches (`env_token`), read per call (ENGFIX4: the switches used to be read once per process,
    and only `_NUMERICS_ENV`)."""
    tok = env_token()
    v = _VERSIONS.get(tok)
    if v is None:
        v = _VERSIONS[tok] = hashlib.sha256((_static_version() + ":" + tok).encode()).hexdigest()[:24]
    return v


def _version_cache_clear() -> None:
    _static_version.cache_clear()
    _VERSIONS.clear()


_version.cache_clear = _version_cache_clear  # the former lru_cache's interface


@lru_cache(maxsize=1)
def _static_version() -> str:
    """sha256 over the CC source, the native libraries the solve runs, whether they are loaded,
    and the numerics switches -- the fingerprint of "what this process would compute"."""
    h = hashlib.sha256()
    h.update(b"cccache-format-%d cckey-v2\n" % FORMAT)
    root = Path(__file__).resolve().parents[3]
    for rel in _SOURCES:
        p = root / rel
        h.update(rel.encode() + b"=")
        h.update(hashlib.sha256(p.read_bytes()).digest() if p.is_file() else b"missing")
        h.update(b"\n")
    libdir = root / "physics/hf/native/lib"
    for stem in _LIBS:
        found = b"missing"
        for ext in (".so", ".dylib"):
            p = libdir / (stem + ext)
            if p.is_file():
                found = hashlib.sha256(p.read_bytes()).digest()
                break
        h.update(stem.encode() + b"=" + found + b"\n")
    try:
        from physics.hf.ecis import ccnative

        h.update(b"loaded=%d%d\n" % (int(ccnative.available()), int(ccnative.glue_available())))
        cc = ccnative._load()
        h.update(b"ccfast=" + (_file_digest(cc._name) if cc is not None else b"none") + b"\n")
    except Exception:  # pragma: no cover - a broken import is not a reason to poison the key
        h.update(b"loaded=??\n")
    try:
        from physics.hf import native as hfnative

        lib = hfnative._load()
        h.update(b"hfnative=%d%d%d " % (int(hfnative.available()), int(hfnative.vhypot()),
                                         int(hfnative.lapack_symbols())))
        h.update((_file_digest(lib._name) if lib is not None else b"none") + b"\n")
    except Exception:  # pragma: no cover
        h.update(b"hfnative=??\n")
    try:
        digests: dict[str, bytes] = {}
        for name, who, path in _omp_providers():
            if path is not None and path not in digests:
                digests[path] = _file_digest(path)
            h.update(name.encode() + b"=" + who.encode() + b":"
                     + (digests[path] if path is not None else b"-") + b"\n")
    except Exception:  # pragma: no cover
        h.update(b"omp=??\n")
    h.update(b"torch=" + torch.__version__.encode() + b"\n")
    for name in _NUMERICS_ENV:
        h.update(name.encode() + b"=" + (os.environ.get(name) or "").encode() + b"\n")
    return h.hexdigest()[:24]


def _path(root: Path, key: tuple) -> tuple[Path, bytes]:
    kb = key_bytes(key)
    digest = hashlib.sha256(kb).hexdigest()
    return root / _version() / digest[:2] / f"{digest}.npz", kb


# ---------------------------------------------------------------------------------------------
# read / write


def load(key: tuple, root: Path | None = None):
    """The stored `incident._row` tuple for `key`, or None (cache off, miss, or unreadable).
    `root`: another cache directory than `INCOGNITA_CC_CACHE`'s (PERFCC2's batch carry).

    Any failure at all -- a missing file, a truncated one, a key that does not match, a wrong
    shape -- returns None, so the caller recomputes.  It never raises.
    """
    root = directory() if root is None else root
    if root is None:
        return None
    try:
        path, kb = _path(root, key)
    except TypeError:
        return None
    try:
        sig = _sig(path)
    except OSError:
        sig = None
    if sig is None:
        _stats["miss"] += 1
        return None
    got = _MEMO.get(str(path))
    if got is not None and got[0] == kb and got[2] == sig:  # PERFOMP: this very file, seen before
        _stats["hit"] += 1
        return _row_of(got[1])
    try:
        with np.load(path, allow_pickle=False) as z:
            if bytes(z["key"].tobytes()) != kb:
                raise ValueError("key mismatch")
            # `np.array`, not `ascontiguousarray`: the four cross sections are 0-dim and
            # `ascontiguousarray` would promote them to shape (1,), which `_stack_rows` then
            # stacks into an (E, 1) column.
            raw = ([np.array(z[n], dtype=np.float64, copy=True) for n in _ARRAYS],
                   int(z["n_j"]), float(z["last_j_fraction"]))
    except Exception:
        _stats["bad"] += 1
        _stats["miss"] += 1
        return None
    _remember(path, kb, raw, sig)
    _stats["hit"] += 1
    return _row_of(raw)


# PERFOMP: the entries this process has read or written, so a key asked again (a worker's
# collective-E2 hold rule builds the first energy's incident channel three times before the run
# builds it once more; a warm worker meets the same keys target after target) is not unzipped
# from disk again. Keyed by the file path, checked against the full key bytes like the file and
# used only while the file on disk is the one remembered (size, mtime, inode: a file rewritten or
# replaced by anyone is read again). Each hit hands out fresh tensors made exactly as a disk read
# makes them, so it is the same bits as the read. Bounded; oldest entries go first.
_MEMO: dict[str, tuple[bytes, tuple, tuple]] = {}
_MEMO_MAX = 2048


def _sig(path: Path) -> tuple:
    st = os.stat(path)
    if not stat.S_ISREG(st.st_mode):
        raise OSError("not a file")
    return (st.st_size, st.st_mtime_ns, st.st_ino)


def _remember(path: Path, kb: bytes, raw: tuple, sig: tuple) -> None:
    _MEMO.pop(str(path), None)
    while len(_MEMO) >= _MEMO_MAX:
        _MEMO.pop(next(iter(_MEMO)))
    _MEMO[str(path)] = (kb, raw, sig)


def _row_of(raw: tuple) -> tuple:
    arrays, n_j, frac = raw
    # `np.array`, not `ascontiguousarray` (see `load`); copied, so a caller writing into a
    # returned tensor cannot reach the remembered entry
    return (*[torch.from_numpy(np.array(a, dtype=np.float64, copy=True)).to(DTYPE) for a in arrays],
            n_j, frac)


def store(key: tuple, row, root: Path | None = None) -> None:
    """Write `row` under `key`, atomically.  Silent on any failure: a cache that cannot be
    written is a slow run, not a wrong one. `root` as for `load`."""
    root = directory() if root is None else root
    if root is None:
        return
    try:
        path, kb = _path(root, key)
    except TypeError:
        return
    try:
        payload = {n: np.array(row[i].detach().cpu().to(torch.float64).numpy(), copy=True)
                   for i, n in enumerate(_ARRAYS)}
        payload["n_j"] = np.int64(int(row[6]))
        payload["last_j_fraction"] = np.float64(float(row[7]))
        payload["key"] = np.frombuffer(kb, dtype=np.uint8)
        path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=".tmp-", suffix=".npz")
        try:
            with os.fdopen(fd, "wb") as fh:
                np.savez(fh, **payload)
            # PERFOMP: no fsync (it was ~10 ms of every miss). The rename is still atomic for
            # every concurrent reader; after a power loss a file can come back empty or torn,
            # which `load` rejects (np.load or the key check fails -> recompute), never misreads.
            os.replace(tmp, path)  # atomic: a concurrent reader sees the old file or the new one
            tmp = None
        finally:
            if tmp is not None and os.path.exists(tmp):
                os.unlink(tmp)
    except Exception:
        return
    try:
        _remember(path, kb, ([payload[n] for n in _ARRAYS], int(payload["n_j"]),
                             float(payload["last_j_fraction"])), _sig(path))
    except OSError:
        pass
    _stats["write"] += 1


__all__ = ["BATCH_ENV_VAR", "ENV_VAR", "batch_directory", "directory", "enabled", "key_bytes",
           "load", "reset_stats", "stats", "store"]
