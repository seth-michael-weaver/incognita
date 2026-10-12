"""STAGECACHE: a DISK cache for the optical-model / direct stages a level-density, photon-strength or
cascade variant cannot change.

On the C route with a warm coupled-channels cache (CCCACHE), four stages still run on every engine
run although their inputs are the optical model, the deformations and the discrete levels only:
the incident channel (`Cascade.incident`: the SETB spherical axis, or the coupled-channels wrapper
around the CC disk cache), the DWBA direct cross sections (`direct.chain.direct_result`, per
energy) and the inverse-channel transmissions (`compound.dens_reference._transmission_cached`).
SPEEDPROF2 measured them at 16-20 % of a warm product run.  This module is their memo, on disk.

    INCOGNITA_STAGE_CACHE=<dir>     turn it on;  unset = today's behaviour, bit for bit.

**Key** (development notes, from a run-time trace of what the four stages read
plus a static scan of every module they execute):  stage + its call arguments +

* the values of the Options fields in `OPTION_FIELDS`, for every Options object the stage uses;
* the full bytes of the Params tensors in `PARAM_KEYS` (the optical-model `*adjust` family,
  `ompadjust*`, `ejoin`, `vinfadjust`, `beta2`, `elwidth`, `risomer`, the masses and the
  giant-resonance adjusts), for every Params object the stage uses;
* the structure the stage consumes, BY VALUE: the `Masses`, `direct.prepare._base`'s collective
  structure (levels, spins, parities, deformations, coupled levels), the coupled band.  A level,
  deformation or mass change from any source changes the key, however it was produced;
* every `HF_*` variable, the INCOGNITA_ switches in `ENV_KEYS`, the evaluated `engphys.on()` of the
  switches the executed code asks for, TALYS_DIR and HOME;
* the version: source bytes of the modules the stages execute (`_SOURCE_DIRS`, `_SOURCE_FILES`),
  bytes of the native libraries they can call (`_LIBS`), torch / numpy versions, `FORMAT`.

What is deliberately NOT in it is what LD / PSF / cascade levers change: their parameters
(`a`, `ctable`, `ptable`, `etable`, `ftable`, ...), their options and their INCOGNITA_ switches.  The
key is hashed with sha256 over the typed exact encoding of `ecis.ccdisk` (float64 bytes, never
`repr`).  Per-object digests are memoised on (object id, tensor ids, tensor `_version`) like
`omp.omp_nx2._factors`; an inference tensor (no version counter) is re-hashed on every call.
Options and the collective structure are frozen dataclasses treated read-only, as the lru caches
of `direct.prepare` and `omp.omp_nx2._omppar` already treat them.

**Storage.**  `<dir>/<version16>/<stage>/<ab>/<digest>.stc`: the value as `record.codec`'s JSON
skeleton plus its arrays (exact round trip, one read per file), with the key bytes stored and
compared on read.
Written to a temporary file and `os.replace`d.  A corrupt, truncated or key-mismatched file is a
miss.  A value the codec refuses is computed and not stored.

Task: STAGECACHE.  Test: tests/hf/test_stagedisk.py; gates in development notes.
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
import os
import struct
import tempfile
from functools import lru_cache
from pathlib import Path

import numpy as np
import torch

FORMAT = 2  # 2: trailing zeros of each array not stored
ENV_VAR = "INCOGNITA_STAGE_CACHE"

OPTION_FIELDS: tuple[str, ...] = (
    "Atarget", "Ltarget", "Ztarget", "alphaomp", "altomp", "collrule", "disctable", "dwbaimag",
    "emulpre_mev", "eninclow_mev", "epreeq_mev", "eurr_mev", "ewfc_mev", "flagautorot", "flagdisp",
    "flagequispec", "flagexpmass", "flaggiant0", "flagglobalfermi", "flagjlm", "flaglocalomp",
    "flagpseudores", "flagrel", "flagriplomp", "flagsoukho", "flagsoukhoinp", "flagspher", "flagurr",
    "isomer_s", "k0", "massmodel", "maxN", "maxZ", "maxband", "maxrot", "nlevbin", "nlevmax",
    "nlevmaxres", "pruitt", "pruittset", "riplomp", "segment", "soswitch_mev", "wddecay",
    # static scan of the OMP / grid modules
    "deuteronomp", "flagglobaldisp", "jlmmode", "flagequi", "nbins0",
    "binconv", "binconvc", "binconvcn", "binconvg", "binconvk", "binconvr", "binconvt",
    "binquad", "binquadc", "binquadg", "binquadk", "binquadm", "binquadp", "binquadq", "binquadr",
    "binquads", "binquadw", "snbin", "snbincn", "snbinwmin",
)  # fmt: skip

PARAM_KEYS: tuple[str, ...] = (
    "v1adjust", "v2adjust", "v3adjust", "v4adjust", "rvadjust", "avadjust", "w1adjust",
    "w2adjust", "w3adjust", "w4adjust", "rwadjust", "awadjust", "rvdadjust", "avdadjust",
    "d1adjust", "d2adjust", "d3adjust", "rwdadjust", "awdadjust", "vso1adjust", "vso2adjust",
    "rvsoadjust", "avsoadjust", "wso1adjust", "wso2adjust", "rwsoadjust", "awsoadjust", "rcadjust",
    "ompadjustd", "ompadjuste1", "ompadjuste2", "ompadjusts", "ejoin", "vinfadjust",
    "beta2", "elwidth", "risomer", "massexcess", "massnucleus",
    "gmradjustd", "gmradjuste", "gmradjustg", "gqradjustd", "gqradjuste", "gqradjustg",
    "leoradjustd", "leoradjuste", "leoradjustg", "heoradjustd", "heoradjuste", "heoradjustg",
    # JLM / Lane (static scan)
    "lv1adjust", "lvadjust", "lvsoadjust", "lw1adjust", "lwadjust", "lwsoadjust",
)  # fmt: skip

ENV_KEYS: tuple[str, ...] = (
    "INCOGNITA_BANDCHECK", "INCOGNITA_BINCONV", "INCOGNITA_BINQUAD", "INCOGNITA_SNBIN", "INCOGNITA_COLLRULE",
    "INCOGNITA_DWBAUNIT", "INCOGNITA_DWBAIMAG", "INCOGNITA_GGDEADEND", "INCOGNITA_LEVCOMPLETE",
    "INCOGNITA_NUMEN", "INCOGNITA_OMP_DEFORMED", "INCOGNITA_OMP_REGION", "INCOGNITA_OMPROTOR",
    "INCOGNITA_RIPL_LEVELS_PARAM", "INCOGNITA_WDDECAY", "INCOGNITA_HF_REFERENCE",
    "INCOGNITA_HF_DIRECT_REFERENCE", "INCOGNITA_TALYS_FIT", "INCOGNITA_DIRCAP", "INCOGNITA_DEF_EVENEVEN",
    "INCOGNITA_SOUKHO_EFCLAMP", "TALYS_DIR", "HOME",
)  # fmt: skip

ENGPHYS_KEYS: tuple[str, ...] = ("dircap", "oddodd", "efermi")

_SOURCE_DIRS: tuple[str, ...] = (
    "physics/hf/omp", "physics/hf/ecis", "physics/hf/direct", "physics/hf/structure",
    "physics/hf/core", "physics/hf/native",
)
_SOURCE_FILES: tuple[str, ...] = (
    "physics/hf/compound/dens_reference.py", "physics/hf/emission/feeding.py",
    "physics/hf/input/defaults.py", "physics/hf/input/fitlib.py", "physics/hf/input/nuclides.py",
    "physics/hf/density/ctwindow.py", "physics/hf/preeq/chain.py", "physics/hf/preeq/exciton.py",
    "physics/hf/preeq/prepare.py", "physics/hf/reference.py", "physics/hf/engphys.py",
    "physics/hf/chartrun.py", "physics/hf/stagedisk.py", "physics/hf/record/codec.py",
)
_LIBS: tuple[str, ...] = ("libsetup", "libnx2", "libhfnative", "libnativex", "libccfast",
                          "libccsplit")

# structure objects a stored value must not hold (as `record.caches.REFUSE`): a copy would break
# the identity-keyed caches downstream, so such a value is computed and not stored
_REFUSE: frozenset[str] = frozenset({
    "physics.hf.input.defaults.Options", "physics.hf.input.defaults.Params",
    "physics.hf.structure.masses.Masses", "physics.hf.structure.levels.Levels",
    "physics.hf.emission.feeding.Cascade",
})

_stats: dict[str, dict[str, int]] = {}


def stats() -> dict[str, dict[str, int]]:
    """Per stage: hit / miss / write / bad / skip counts since the process started."""
    return {k: dict(v) for k, v in _stats.items()}


def reset_stats() -> None:
    _stats.clear()


def _count(stage: str, what: str) -> None:
    s = _stats.setdefault(stage, {"hit": 0, "miss": 0, "write": 0, "bad": 0, "skip": 0})
    s[what] += 1


def directory() -> Path | None:
    """The cache directory, or None when INCOGNITA_STAGE_CACHE is unset or empty (read per call)."""
    d = os.environ.get(ENV_VAR)
    return Path(d) if d else None


def enabled() -> bool:
    return directory() is not None


# ---------------------------------------------------------------------------------------------
# exact value encoding


_DEFAULTS_MOD = "physics.hf.input.defaults"


class Unkeyable(TypeError):
    """A key input this module cannot encode exactly: the call is then not cached."""


def _enc(obj, out: bytearray) -> None:
    if obj is None:
        out += b"N"
    elif isinstance(obj, (bool, np.bool_)):
        out += b"B" + (b"\x01" if obj else b"\x00")
    elif isinstance(obj, (int, np.integer)):
        out += b"I" + str(int(obj)).encode("ascii") + b";"
    elif isinstance(obj, (float, np.floating)):
        out += b"F" + struct.pack("<d", float(obj))
    elif isinstance(obj, str):
        b = obj.encode("utf-8")
        out += b"S" + str(len(b)).encode("ascii") + b":" + b
    elif isinstance(obj, bytes):
        out += b"Y" + str(len(obj)).encode("ascii") + b":" + obj
    elif isinstance(obj, torch.Tensor):
        if obj.device.type != "cpu" or obj.is_sparse:
            raise Unkeyable("tensor off the CPU / sparse")
        _enc(obj.detach().contiguous().numpy(), out)
    elif isinstance(obj, np.ndarray):
        if obj.dtype == object:
            raise Unkeyable("object array")
        a = np.ascontiguousarray(obj)
        out += (b"A" + a.dtype.str.encode() + b"|" + repr(a.shape).encode() + b":"
                + hashlib.sha256(a.tobytes()).digest())
    elif isinstance(obj, tuple) and obj and all(type(x) is float for x in obj):
        out += b"f" + str(len(obj)).encode() + b":" + struct.pack(f"<{len(obj)}d", *obj)
    elif isinstance(obj, (tuple, list)):
        out += (b"(" if isinstance(obj, tuple) else b"[") + str(len(obj)).encode() + b":"
        for x in obj:
            _enc(x, out)
        out += b")"
    elif isinstance(obj, (set, frozenset)):
        items = sorted(_key_bytes(x) for x in obj)
        out += b"{" + str(len(items)).encode() + b":" + b"".join(items) + b"}"
    elif isinstance(obj, dict):
        items = sorted((_key_bytes(k), _key_bytes(v)) for k, v in obj.items())
        out += b"D" + str(len(items)).encode() + b":"
        for k, v in items:
            out += k + v
    elif type(obj).__qualname__ == "Options" and type(obj).__module__ == _DEFAULTS_MOD:
        out += b"Oo" + _options_digest(obj)  # nested (a band's `options`): the keyed subset only
    elif type(obj).__qualname__ == "Params" and type(obj).__module__ == _DEFAULTS_MOD:
        out += b"Op" + _params_digest(obj)
    elif dataclasses.is_dataclass(obj) and not isinstance(obj, type):
        t = type(obj)
        out += b"O" + f"{t.__module__}.{t.__qualname__}".encode() + b":"
        for f in dataclasses.fields(obj):
            _enc(f.name, out)
            _enc(getattr(obj, f.name), out)
        out += b")"
    else:
        raise Unkeyable(f"cannot key a {type(obj).__name__}")


def _key_bytes(obj) -> bytes:
    out = bytearray()
    _enc(obj, out)
    return bytes(out)


def _tver(t) -> int:
    return -2 if t.is_inference() else t._version


# per-object digests: id -> (obj, stamp, digest); the object is held so its id is not reused
_MEMO: dict[int, tuple] = {}


def _memo(obj, stamp, build) -> bytes:
    hit = _MEMO.get(id(obj))
    if hit is not None and hit[0] is obj and hit[1] == stamp and stamp is not None:
        return hit[2]
    d = hashlib.sha256(build()).digest()
    if len(_MEMO) > 512:
        _MEMO.clear()
    _MEMO[id(obj)] = (obj, stamp, d)
    return d


def _options_digest(o) -> bytes:
    """The OPTION_FIELDS values of an Options object (frozen: memoised by identity)."""
    return _memo(o, (), lambda: _key_bytes(tuple((f, getattr(o, f, "<absent>"))
                                                 for f in OPTION_FIELDS)))


def _raw(h, name: str, t) -> None:
    """Feed one tensor / array to `h`: name, dtype, shape and its bytes (no Python per element)."""
    h.update(b"<" + name.encode() + b">")
    if t is None:
        h.update(b"N")
        return
    a = t.detach().numpy() if isinstance(t, torch.Tensor) else t
    a = np.ascontiguousarray(a)
    h.update(a.dtype.str.encode() + repr(a.shape).encode())
    h.update(memoryview(a).cast("B"))


def _params_digest(p) -> bytes:
    """The PARAM_KEYS tensors of a Params object, full bytes.  Memoised on the tensors' ids and
    version counters; an inference tensor keeps no counter and is checked by identity only, the
    convention `omp.omp_nx2._factors` (the optical-model code cached here) already relies on."""
    vals = p.values
    tens = [vals.get(k) for k in PARAM_KEYS]
    stamp = tuple((id(t), _tver(t)) if t is not None else None for t in tens)

    def build():
        h = hashlib.sha256(b"params")
        for k, t in zip(PARAM_KEYS, tens):
            if t is not None and (t.device.type != "cpu" or t.is_sparse):
                raise Unkeyable(f"{k}: tensor off the CPU / sparse")
            _raw(h, k, t)
        return h.digest()

    return _memo(p, stamp, build)


def _value_digest(obj) -> bytes:
    """A structure object (Masses, CollectiveStructure, a band dict) by value; a dataclass is
    memoised on its tensor fields' ids and version counters (identity for inference tensors)."""
    if isinstance(obj, Digest):
        return bytes(obj)
    if obj is None or isinstance(obj, (dict, tuple, list, str, int, float)):
        return hashlib.sha256(_key_bytes(obj)).digest()
    if not dataclasses.is_dataclass(obj):
        raise Unkeyable(f"cannot key a {type(obj).__name__}")
    fields = [(f.name, getattr(obj, f.name)) for f in dataclasses.fields(obj)]
    stamp = tuple((id(x), _tver(x)) for _, x in fields if isinstance(x, torch.Tensor))

    def build():
        h = hashlib.sha256(f"{type(obj).__module__}.{type(obj).__qualname__}".encode())
        for n, x in fields:
            if isinstance(x, (torch.Tensor, np.ndarray)) and (
                    not isinstance(x, torch.Tensor) or x.device.type == "cpu") and (
                    getattr(x, "dtype", None) is not object):
                _raw(h, n, x)
            else:
                h.update(b"<" + n.encode() + b">" + _key_bytes(x))
        return h.digest()

    return _memo(obj, stamp, build)


class Digest(bytes):
    """A precomputed digest handed to `key(values=...)` as is."""


_ENGPHYS_MEMO: dict = {}


def _env_part() -> bytes:
    """Every `HF_*` variable, the `ENV_KEYS` and the evaluated `engphys.on()` of `ENGPHYS_KEYS`,
    read from the raw (bytes) environment on every call -- a worker or a test may change it."""
    raw = os.environ._data  # bytes -> bytes; iterating it skips decoding ~100 variables
    hf = sorted(kv for kv in raw.items() if kv[0][:3] == b"HF_")
    named = [raw.get(k.encode()) for k in ENV_KEYS]
    # `engphys.on` reads INCOGNITA_ENGPHYS and one switch variable per name; evaluate it once per
    # distinct raw value of those variables
    from physics.hf import engphys

    ek = tuple(raw.get(v.encode()) for v in ("INCOGNITA_ENGPHYS",
                                              *(engphys.SWITCHES[k] for k in ENGPHYS_KEYS)))
    eng = _ENGPHYS_MEMO.get(ek)
    if eng is None:
        vals = []
        for k in ENGPHYS_KEYS:
            try:
                vals.append(b"1" if engphys.on(k) else b"0")
            except (KeyError, ValueError) as e:
                vals.append(f"error:{e}".encode())
        eng = _ENGPHYS_MEMO[ek] = b",".join(vals)
    out = [b"hf"]
    for k, v in hf:
        out += [k, b"=", v, b"\x00"]
    out.append(b"named")
    for k, v in zip(ENV_KEYS, named):
        out += [k.encode(), b"=", b"\x01" if v is None else v, b"\x00"]
    out += [b"engphys=", eng]
    return b"".join(out)


def _file_digest(p: Path, memo: dict) -> bytes:
    """sha256 of a file's bytes, memoised on (size, mtime_ns, inode) in `memo`."""
    try:
        st = p.stat()
    except OSError:
        return b"missing"
    tag = [st.st_size, st.st_mtime_ns, st.st_ino]
    hit = memo.get(str(p))
    if hit is not None and hit[0] == tag:
        return bytes.fromhex(hit[1])
    d = hashlib.sha256(p.read_bytes()).digest()
    memo[str(p)] = [tag, d.hex()]
    return d


@lru_cache(maxsize=1)
def _version() -> str:
    """sha256 over the sources the stages execute, the native libraries, torch / numpy, FORMAT.

    The per-file sha256 is memoised in `<cache dir>/filehash.json` on (size, mtime_ns, inode), so
    a worker does not re-read ~10 MB of libraries at start-up; any rebuild or edit changes the
    mtime and is re-hashed."""
    h = hashlib.sha256()
    h.update(b"stagecache-format-%d\n" % FORMAT)
    root = Path(__file__).resolve().parents[2]
    d = directory()
    side = d / "filehash.json" if d is not None else None
    try:
        memo = json.loads(side.read_text()) if side is not None and side.is_file() else {}
    except (OSError, ValueError):
        memo = {}
    n0 = json.dumps(memo, sort_keys=True)
    files = set(_SOURCE_FILES)
    for sd in _SOURCE_DIRS:
        files |= {str(p.relative_to(root)) for p in (root / sd).rglob("*.py")
                  if "__pycache__" not in p.parts}
    for rel in sorted(files):
        h.update(rel.encode() + b"=" + _file_digest(root / rel, memo) + b"\n")
    libdir = root / "physics" / "hf" / "native" / "lib"
    for name in _LIBS:
        h.update(name.encode() + b"=" + _file_digest(libdir / f"{name}.so", memo) + b"\n")
    h.update(f"torch={torch.__version__} numpy={np.__version__}\n".encode())
    if side is not None and json.dumps(memo, sort_keys=True) != n0:
        try:
            side.parent.mkdir(parents=True, exist_ok=True)
            fd, tmp = tempfile.mkstemp(dir=side.parent, suffix=".tmp")
            with os.fdopen(fd, "w") as fh:
                json.dump(memo, fh)
            os.replace(tmp, side)
        except OSError:
            pass
    return h.hexdigest()


def version() -> str:
    return _version()


def value_digest(obj) -> Digest:
    """`obj` by value, as `key(values=[obj])` would hash it (for a caller memoising it)."""
    return Digest(_value_digest(obj))


def key(stage: str, args: tuple, *, options=(), params=(), values=()) -> bytes:
    """The key bytes of one stage call (raises `Unkeyable` when an input cannot be encoded)."""
    out = bytearray()
    _enc((FORMAT, stage), out)
    _enc(args, out)
    out += b"|o" + b"".join(_options_digest(o) for o in options)
    out += b"|p" + b"".join(_params_digest(p) for p in params)
    out += b"|v" + b"".join(_value_digest(v) for v in values)
    out += b"|e" + hashlib.sha256(_env_part()).digest()
    out += b"|V" + _version().encode()
    return bytes(out)


# ---------------------------------------------------------------------------------------------
# storage


_MAGIC = b"STC2"
# file bytes read in this process (an entry asked for again, e.g. by a second Cascade, is decoded
# afresh -- new arrays -- without a second read); dropped if a read fails its checks
_BYTES: dict = {}


def _path(stage: str, digest: str) -> Path:
    return directory() / _version()[:16] / stage / digest[:2] / f"{digest}.stc"


def _load(path: Path, kb: bytes):
    """One file, one read: magic, header length, JSON header (skeleton + array table), then the
    key bytes and every array back to back.  The arrays are copied out (owned, writable)."""
    from physics.hf.record import codec

    buf = _BYTES.get(path)
    if buf is None:
        buf = path.read_bytes()
        if len(_BYTES) > 4096:
            _BYTES.clear()
        _BYTES[path] = buf
    if buf[:4] != _MAGIC:
        raise ValueError("bad magic")
    hl = int.from_bytes(buf[4:12], "little")
    head = json.loads(buf[12:12 + hl].decode("utf-8"))
    blob = memoryview(buf)[12 + hl:]
    if bytes(blob[:head["klen"]]) != kb:
        raise ValueError("key mismatch")
    arrays = []
    for dt, shape, off, nb, used in head["arrays"]:
        a = np.zeros(int(np.prod(shape, dtype=np.int64)), dtype=np.dtype(dt))
        a[:used] = np.frombuffer(blob[off:off + nb], dtype=np.dtype(dt))
        arrays.append(a.reshape(shape))
    if len(blob) != head["size"]:
        raise ValueError("truncated")
    return codec.Decoder(lambda i: arrays[i]).decode(head["skel"])


def _store(path: Path, kb: bytes, value) -> bool:
    from physics.hf.record import codec

    enc = codec.Encoder(_REFUSE)
    try:
        skel = enc.encode(value)
    except codec.Unrecordable:
        return False
    table, parts, off = [], [kb], len(kb)
    for a in enc.arrays:
        a = np.ascontiguousarray(a)
        flat = a.reshape(-1)
        # trailing all-zero-BYTES elements (padding to NUMLEV2 / the grid) are not stored; a -0.0
        # has a sign bit and is kept, so the round trip stays bit-exact for every dtype
        nz = np.flatnonzero(flat.view(np.uint8).reshape(flat.size, -1).any(axis=1)) \
            if flat.size and flat.dtype.itemsize else np.zeros(0, dtype=np.int64)
        used = int(nz[-1]) + 1 if nz.size else 0
        b = flat[:used].tobytes()
        table.append([a.dtype.str, list(a.shape), off, len(b), used])
        parts.append(b)
        off += len(b)
    head = json.dumps({"klen": len(kb), "arrays": table, "size": off, "skel": skel}).encode()
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(_MAGIC + len(head).to_bytes(8, "little") + head)
            for b in parts:
                fh.write(b)
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise
    return True


def cached(stage: str, args: tuple, compute, *, options=(), params=(), values=()):
    """`compute()`, or its stored value when a call with the same key was stored before.

    Not enabled: `compute()`, nothing else.  The key inputs are described in the module docstring.
    """
    if not enabled():
        return compute()
    from physics.hf import stagetime

    with stagetime.stage("stagecache"):
        try:
            kb = key(stage, args, options=options, params=params, values=values)
        except Unkeyable:
            kb = None
        if kb is None:
            _count(stage, "skip")
        else:
            digest = hashlib.sha256(kb).hexdigest()
            path = _path(stage, digest)
            if path.is_file():
                try:
                    value = _load(path, kb)
                    _count(stage, "hit")
                    return value
                except Exception:  # noqa: BLE001  (any unreadable file is a miss)
                    _BYTES.pop(path, None)
                    _count(stage, "bad")
            _count(stage, "miss")
    value = compute()
    if kb is not None:
        with stagetime.stage("stagecache"):
            try:
                if _store(path, kb, value):
                    _count(stage, "write")
                else:
                    _count(stage, "skip")
            except OSError:
                _count(stage, "skip")
    return value


__all__ = ["cached", "enabled", "directory", "key", "stats", "reset_stats", "version", "Unkeyable"]
