"""Binary disk cache for parsed TALYS structure-database tables.

The engine parses the TALYS text files lazily, per nucleus, once per process. Most families cost
little; a few cost a fresh process noticeable time, mostly on heavy and fissile targets: the
level-density tables (`density.tables._table_blocks`, one Fortran-formatted record per line, 33
numbers each) and the HFB fission paths (`fission.wkb._parsed_blocks`, a whole element file).
This module stores what those parsers return as float64/int64 arrays in a `.npz`, so the next
process reads the numbers instead of parsing the text.

    INCOGNITA_STRUCT_CACHE=<dir>     turn it on;  unset or empty = parse the text, as before.

Key: the family, the parser's arguments and the source file's absolute path. Staleness: the
entry stores the source file's (size, mtime_ns) and FORMAT and is used only when all three still
match; anything else (missing, stale, unreadable, truncated) is a miss and the text is parsed
(and the entry rewritten). Entries are written to a temporary file and `os.replace`d. The arrays
hold exactly the float64 / int values the parser produced, so a hit returns the same numbers
to the bit (tests/hf/test_perfstart_gate.py, run with the cache cold and warm).

TALYS: none (I/O cache)
Test: tests/hf/test_structbin.py
"""

from __future__ import annotations

import hashlib
import os
import tempfile
from pathlib import Path

ENV_VAR = "INCOGNITA_STRUCT_CACHE"
FORMAT = 1

_stats: dict[str, int] = {"hit": 0, "miss": 0, "write": 0, "bad": 0}


def directory() -> Path | None:
    d = os.environ.get(ENV_VAR)
    return Path(d) if d else None


def stats() -> dict[str, int]:
    return dict(_stats)


def _entry(d: Path, family: str, source: str, args: tuple) -> tuple[Path, str]:
    key = f"{FORMAT}\0{family}\0{os.path.abspath(source)}\0{args!r}"
    h = hashlib.sha1(key.encode()).hexdigest()
    return d / f"v{FORMAT}" / family / h[:2] / f"{h}.npz", key


def _stamp(source: str):
    st = os.stat(source)
    return st.st_size, st.st_mtime_ns


def load(family: str, source: str, args: tuple) -> dict | None:
    """The arrays stored for (family, source, args), or None (cache off, missing or stale)."""
    d = directory()
    if d is None:
        return None
    import numpy as np

    path, key = _entry(d, family, source, args)
    try:
        with np.load(path, allow_pickle=False) as z:
            meta = z["__meta__"]
            if (str(z["__key__"]) != key or int(meta[0]) != FORMAT
                    or (int(meta[1]), int(meta[2])) != _stamp(source)):
                _stats["bad"] += 1
                return None
            out = {k: z[k] for k in z.files if not k.startswith("__")}
    except FileNotFoundError:
        _stats["miss"] += 1
        return None
    except Exception:  # noqa: BLE001  (unreadable / truncated entry: a miss)
        _stats["bad"] += 1
        return None
    _stats["hit"] += 1
    return out


def store(family: str, source: str, args: tuple, arrays: dict) -> None:
    """Write the arrays for (family, source, args); any failure is silent (the cache is optional)."""
    d = directory()
    if d is None:
        return
    import numpy as np

    path, key = _entry(d, family, source, args)
    try:
        size, mtime = _stamp(source)
        path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
        with os.fdopen(fd, "wb") as f:
            np.savez(f, __key__=np.array(key), __meta__=np.array([FORMAT, size, mtime], dtype=np.int64),
                     **arrays)
        os.replace(tmp, path)
        _stats["write"] += 1
    except Exception:  # noqa: BLE001
        try:
            os.unlink(tmp)  # type: ignore[possibly-undefined]
        except Exception:  # noqa: BLE001
            pass
