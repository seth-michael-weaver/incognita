"""Frozen generalization splits (blueprint §4.4, §6.1).

Every manifest lives in ``data/splits/manifests/<name>.parquet`` as a single
:class:`~data.schema.splits.SplitManifest` row, and ``manifests_index.json`` pins
each file by sha256 (of the file bytes and of the canonical content). Consumers
load manifests **by name** through :func:`load_manifest` and never regenerate them;
regeneration is the job of ``uv run python -m data.splits.holdout --write``.

Naming: ``<split>_<role>`` where ``<split>`` is also stored in ``params["split"]``
(e.g. ``nuclide_holdout_f0_test`` ↔ split ``nuclide_holdout_f0``, role ``test``), so
the roles of one split can be gathered with :func:`load_split`.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from data.schema.splits import SplitManifest, SplitRole

__all__ = [
    "INDEX_PATH",
    "MANIFEST_DIR",
    "ManifestIntegrityError",
    "content_sha256",
    "file_sha256",
    "list_manifests",
    "load_manifest",
    "load_split",
    "manifest_path",
    "read_index",
]

MANIFEST_DIR = Path(__file__).resolve().parent / "manifests"
INDEX_PATH = MANIFEST_DIR / "manifests_index.json"
INDEX_NAME = "manifests_index.json"


class ManifestIntegrityError(RuntimeError):
    """A manifest on disk does not match the hash pinned in ``manifests_index.json``."""


def manifest_path(name: str, manifest_dir: Path = MANIFEST_DIR) -> Path:
    return manifest_dir / f"{name}.parquet"


def file_sha256(path: str | Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def content_sha256(m: SplitManifest) -> str:
    """Hash of the manifest *content* (independent of Parquet encoding details)."""
    payload = {
        "name": m.name,
        "kind": str(m.kind),
        "role": str(m.role),
        "seed": m.seed,
        "members": list(m.members),
        "params": dict(sorted(m.params.items())),
        "version": m.version,
        "description": m.description,
    }
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def read_index(manifest_dir: Path = MANIFEST_DIR) -> dict[str, Any]:
    path = manifest_dir / INDEX_NAME
    if not path.exists():
        raise FileNotFoundError(
            f"{path} not found; run `uv run python -m data.splits.holdout --write`"
        )
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def list_manifests(manifest_dir: Path = MANIFEST_DIR) -> list[str]:
    """Names of every pinned manifest, sorted."""
    return sorted(read_index(manifest_dir)["manifests"])


def load_manifest(
    name: str, *, verify: bool = True, manifest_dir: Path = MANIFEST_DIR
) -> SplitManifest:
    """Load one manifest by name, checking it against the pinned hashes."""
    index = read_index(manifest_dir)
    entry = index["manifests"].get(name)
    if entry is None:
        raise KeyError(f"unknown split manifest {name!r}; known: {sorted(index['manifests'])}")
    path = manifest_dir / entry["file"]
    if verify and file_sha256(path) != entry["sha256_file"]:
        raise ManifestIntegrityError(f"{path.name}: file sha256 differs from manifests_index.json")
    records = SplitManifest.read_parquet(path)
    if len(records) != 1:
        raise ManifestIntegrityError(f"{path.name}: expected exactly one manifest row")
    m = records[0]
    if m.name != name:
        raise ManifestIntegrityError(f"{path.name}: contains manifest {m.name!r}, not {name!r}")
    if verify and content_sha256(m) != entry["sha256_content"]:
        raise ManifestIntegrityError(f"{name}: content sha256 differs from manifests_index.json")
    return m


def load_split(
    split: str, *, verify: bool = True, manifest_dir: Path = MANIFEST_DIR
) -> dict[SplitRole, SplitManifest]:
    """All roles of one split, keyed by role (e.g. ``load_split("nuclide_holdout_f0")``)."""
    index = read_index(manifest_dir)
    out: dict[SplitRole, SplitManifest] = {}
    for name, entry in index["manifests"].items():
        if entry.get("split") == split:
            m = load_manifest(name, verify=verify, manifest_dir=manifest_dir)
            out[SplitRole(m.role)] = m
    if not out:
        raise KeyError(f"unknown split {split!r}")
    return out
