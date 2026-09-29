"""CCCACHE: the coupled-channels disk cache (`physics.hf.ecis.ccdisk`).

The physics gates (bit-identical channels off / cold / warm on 12 nuclides, the MISS and HIT
cases, concurrency) are in the development notes (CCCACHE); these are the unit-level invariants.
"""

from __future__ import annotations

import numpy as np
import pytest
import torch

from physics.hf.core.tensors import DTYPE
from physics.hf.ecis import ccdisk


def _row():
    """A payload shaped like `incident._row`: four 0-dim cross sections, sigma_direct (NLEV,),
    tjl (L+1, 2), then n_j and the convergence fraction."""
    g = torch.Generator().manual_seed(7)
    return (
        torch.tensor(1234.5678901234567, dtype=DTYPE),
        torch.tensor(2.220446049250313e-16, dtype=DTYPE),
        torch.tensor(-0.0, dtype=DTYPE),
        torch.tensor(1e-300, dtype=DTYPE),
        torch.rand(5, generator=g, dtype=DTYPE),
        torch.rand(21, 2, generator=g, dtype=DTYPE),
        23,
        3.5e-7,
    )


KEY = (66, 163, 1, (("colltype", "R"), ("e_mev", ("torch.float64", (0.0, 0.0738)))), 40,
       False, 10.0, 0.001, 1.0e-3, -0.0, 1e-300, 1)


@pytest.fixture
def cache(tmp_path, monkeypatch):
    monkeypatch.setenv(ccdisk.ENV_VAR, str(tmp_path))
    ccdisk.reset_stats()
    yield tmp_path
    ccdisk.reset_stats()


def test_off_by_default(monkeypatch):
    monkeypatch.delenv(ccdisk.ENV_VAR, raising=False)
    assert not ccdisk.enabled()
    assert ccdisk.load(KEY) is None
    ccdisk.store(KEY, _row())  # a no-op, and must not raise


def test_round_trip_is_exact(cache):
    row = _row()
    assert ccdisk.load(KEY) is None
    ccdisk.store(KEY, row)
    got = ccdisk.load(KEY)
    assert got is not None
    for a, b in zip(row[:6], got[:6], strict=True):
        assert a.shape == b.shape          # a 0-dim scalar must NOT come back as (1,)
        assert a.dtype == b.dtype
        assert torch.equal(a, b)           # bit for bit, not allclose
    assert got[6] == row[6] and isinstance(got[6], int)
    assert got[7] == row[7]
    assert ccdisk.stats()["hit"] == 1


def test_a_different_input_is_a_different_key(cache):
    ccdisk.store(KEY, _row())
    for i, bump in ((7, 0.0010000000000000002), (8, 1.0000001e-3), (0, 67), (10, True)):
        other = KEY[:i] + (bump,) + KEY[i + 1:]
        assert ccdisk.load(other) is None, f"element {i} did not change the key"


def test_ints_floats_and_bools_do_not_alias(cache):
    a, b = ccdisk.key_bytes((1,)), ccdisk.key_bytes((1.0,))
    assert a != b != ccdisk.key_bytes((True,))
    assert ccdisk.key_bytes(("1",)) not in (a, b)


def test_an_unhashable_key_simply_does_not_cache(cache):
    bad = (66, {"a": 1})
    ccdisk.store(bad, _row())
    assert ccdisk.load(bad) is None
    assert ccdisk.stats()["write"] == 0


def test_a_corrupt_file_is_a_miss_not_a_crash(cache):
    ccdisk.store(KEY, _row())
    path = next(p for p in cache.rglob("*.npz"))
    whole = path.read_bytes()
    path.write_bytes(whole[: len(whole) // 2])          # truncated mid-write
    assert ccdisk.load(KEY) is None
    assert ccdisk.stats()["bad"] == 1
    path.write_bytes(b"")                                # empty
    assert ccdisk.load(KEY) is None
    ccdisk.store(KEY, _row())                            # and it heals
    assert ccdisk.load(KEY) is not None


def test_a_sha_collision_cannot_return_another_row(cache):
    """The stored key bytes are checked against the asked-for ones, so even if two keys landed
    on one path the row would be a miss rather than the wrong answer."""
    ccdisk.store(KEY, _row())
    path = next(p for p in cache.rglob("*.npz"))
    with np.load(path) as z:
        payload = {k: z[k] for k in z.files}
    payload["key"] = np.frombuffer(ccdisk.key_bytes((1, 2, 3)), dtype=np.uint8)
    np.savez(path, **payload)
    assert ccdisk.load(KEY) is None
    assert ccdisk.stats()["bad"] == 1


def test_the_version_covers_the_numerics_switches(monkeypatch, tmp_path):
    monkeypatch.setenv(ccdisk.ENV_VAR, str(tmp_path))
    ccdisk._version.cache_clear()
    v0 = ccdisk._version()
    monkeypatch.setenv("HF_CC_MODNUM", "0")
    ccdisk._version.cache_clear()
    assert ccdisk._version() != v0
    monkeypatch.delenv("HF_CC_MODNUM")
    ccdisk._version.cache_clear()
    assert ccdisk._version() == v0


def test_no_temporary_file_survives_a_write(cache):
    ccdisk.store(KEY, _row())
    assert [p.name for p in cache.rglob(".tmp-*")] == []
    assert len(list(cache.rglob("*.npz"))) == 1


def test_incident_takes_the_disk_row(cache, monkeypatch):
    """The wiring: with the cache on, a second process-level miss is served from disk instead of
    solving, and `_stack_rows` accepts what came back (the 0-dim shapes survive)."""
    from physics.hf.ecis import incident

    row = _row()
    ccdisk.store(KEY, row)
    incident._SOLVED.clear()
    got = ccdisk.load(KEY)
    incident._SOLVED[KEY] = got
    res = incident._stack_rows([got, got])
    assert res.sigma_tot_mb.shape == (2,)
    assert res.sigma_direct_mb.shape == (2, 5)
    assert res.tjl.shape == (2, 21, 2)
    assert float(res.sigma_tot_mb[0]) == float(row[0])
    incident._SOLVED.clear()
