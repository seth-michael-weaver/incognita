"""validation.cache._fresh: a directory source (the <lib>_cov.zarr store) counts by its newest file."""
import os

from validation import cache as C


def test_directory_source_newer_than_cache_is_stale(tmp_path):
    out = tmp_path / "cov.parquet"; out.write_text("x")
    z = tmp_path / "lib_cov.zarr"; (z / "a").mkdir(parents=True); f = z / "a" / "0.0"; f.write_text("y")
    t = out.stat().st_mtime
    os.utime(out, (t - 100, t - 100))            # the cache was written before the zarr was rewritten
    assert not C._fresh(out, z)
    os.utime(out, (t + 100, t + 100))
    assert C._fresh(out, z)


def test_missing_source_does_not_force_rebuild(tmp_path):
    out = tmp_path / "c.parquet"; out.write_text("x")
    assert C._fresh(out, tmp_path / "absent.parquet")
