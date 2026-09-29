import hashlib

import numpy as np
import pytest

from incognita import library as L


def test_nuclide_id_parsing():
    assert L.nuclide_id("Fe-56") == "Z026N030M0"
    assert L.nuclide_id("fe56") == "Z026N030M0"
    assert L.nuclide_id("197Au") == "Z079N118M0"
    assert L.nuclide_id("Z026N030M0") == "Z026N030M0"
    with pytest.raises(ValueError):
        L.nuclide_id("Xx-12")


def test_library_checksums():
    sums = (L.LIBRARY / "SHA256SUMS").read_text().split("\n")
    for line in filter(None, sums):
        digest, name = line.split(maxsplit=1)
        assert hashlib.sha256((L.LIBRARY / name.strip()).read_bytes()).hexdigest() == digest, name


def test_capture_table_shape_and_tiers():
    t = L.load_capture()
    assert t.nuclide_id.is_unique
    assert set(t.tier) <= set(L.TIERS)
    e = np.asarray(t.energy_ev.iloc[0], float)
    assert e.min() == pytest.approx(1e3) and e.max() == pytest.approx(2e7)
    assert "anchor_macs30_mb" not in t.columns  # third-party compilation values are not redistributed


def test_capture_curve_bands_are_ordered():
    c = L.capture_curve("Fe-56")
    ok = np.isfinite(c.sigma_b) & (c.sigma_b > 0)
    assert ok.any()
    c = c[ok]
    assert (c.lo95_b <= c.lo68_b).all() and (c.lo68_b <= c.sigma_b).all()
    assert (c.sigma_b <= c.hi68_b).all() and (c.hi68_b <= c.hi95_b).all()
