"""PERFSTART structure binary cache (physics/hf/structure/bincache.py): exact round trip, stale and
corrupt entries are misses, cache off does nothing."""

import os

import numpy as np

from physics.hf.structure import bincache


def test_roundtrip_stale_corrupt(tmp_path, monkeypatch):
    src = tmp_path / "X.ld"
    src.write_text("table\n")
    arrays = {"n": np.array(2), "b0": np.array([[0.1, 1e-300, 7.0 / 3.0]])}
    monkeypatch.delenv(bincache.ENV_VAR, raising=False)
    bincache.store("t", str(src), (1,), arrays)
    assert bincache.load("t", str(src), (1,)) is None  # off: nothing stored, nothing read
    monkeypatch.setenv(bincache.ENV_VAR, str(tmp_path / "cache"))
    assert bincache.load("t", str(src), (1,)) is None  # miss
    bincache.store("t", str(src), (1,), arrays)
    got = bincache.load("t", str(src), (1,))
    assert got is not None and got["b0"].tobytes() == arrays["b0"].tobytes() and int(got["n"]) == 2
    assert bincache.load("t", str(src), (2,)) is None  # other arguments: other entry
    os.utime(src, ns=(1, 1))  # source changed: stale
    assert bincache.load("t", str(src), (1,)) is None
    bincache.store("t", str(src), (1,), arrays)
    path, _ = bincache._entry(bincache.directory(), "t", str(src), (1,))
    path.write_bytes(path.read_bytes()[:40])  # truncated: a miss, not an error
    assert bincache.load("t", str(src), (1,)) is None
