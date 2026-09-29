"""DIRECTCAP: the racapcalc port (physics/hf/direct/racapcalc.py).

* sixj / clebs against the compiled Fortran (racapcalc.f:880, :1052) on a 1-in-200 sample of the
  97,748 argument sets checked when the port was written (tests/hf/data/).
* racap totals against stock TALYS-2.x `racap y optmodall y` racap.tot (Pb-208, Fe-56, Zr-90;
  TALYS returns 0 without optmodall, see the module docstring).
* INCOGNITA_DIRECT_CAPTURE off (the default) adds exactly nothing.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from physics.hf.direct import racapcalc as R

DATA = Path(__file__).parent / "data" / "racap_sixj_clebs_fortran.txt"
E = [1.0e-3, 1.0e-2, 3.0e-2, 0.1, 0.3, 1.0, 2.0, 5.0]
# racap.tot "xs(dir. cap.)" [mb], stock TALYS-2.x, `racap y optmodall y`
TALYS = {
    (82, 208): [4.692537e-02, 2.070931e-02, 1.948818e-02, 2.505150e-02, 3.727914e-02,
                6.165939e-02, 1.542773e-01, 7.615820e-02],
    (26, 56): [7.036285e01, 2.104907e01, 1.086970e01, 4.422320e00, 1.684553e00, 3.694504e00,
               7.762116e-01, 4.501220e-01],
    (40, 90): [4.546764e00, 2.102528e00, 2.143150e00, 3.437390e00, 7.205276e00, 3.534055e00,
               3.786585e00, 1.342120e00],
}


def test_sixj_clebs_match_fortran():
    n = 0
    for line in DATA.read_text().splitlines():
        a = [int(line[1 + 3 * i: 4 + 3 * i]) for i in range(6)]
        q = float(line[19:])
        v = R.sixj(*a) if line[0] == "S" else R.clebs(*a)
        assert abs(abs(v) - abs(q)) <= 1e-12 * max(1.0, abs(q)), (line, v)
        n += 1
    assert n > 400


def _talys_structure_available() -> bool:
    try:
        from physics.hf.structure.files import talys_structure_dir
        return (talys_structure_dir() / "levels").is_dir()
    except Exception:
        return False


@pytest.mark.skipif(not _talys_structure_available(), reason="TALYS structure database absent")
@pytest.mark.parametrize("ZA", sorted(TALYS))
def test_racap_matches_stock_talys(ZA):
    Z, A = ZA
    r = R.racap_xs(Z, A, E)
    d = np.log10(r["total_mb"] / np.asarray(TALYS[ZA]))
    assert np.max(np.abs(d)) < 1e-5, d
    np.testing.assert_allclose(r["disc_mb"] + r["cont_mb"], r["total_mb"], rtol=1e-5)


def test_off_by_default(monkeypatch):
    monkeypatch.delenv("INCOGNITA_DIRECT_CAPTURE", raising=False)
    monkeypatch.delenv("INCOGNITA_DIRECT_CAPTURE", raising=False)
    assert R.mode() == "off"
    assert np.all(R.direct_capture_mb(82, 208, E) == 0.0)
    monkeypatch.setenv("INCOGNITA_DIRECT_CAPTURE", "0")
    assert R.mode() == "off"
    monkeypatch.setenv("INCOGNITA_DIRECT_CAPTURE", "disc")
    assert R.mode() == "disc"
    monkeypatch.setenv("INCOGNITA_DIRECT_CAPTURE", "bogus")
    with pytest.raises(ValueError):
        R.mode()


@pytest.mark.skipif(not _talys_structure_available(), reason="TALYS structure database absent")
def test_disc_is_the_experimental_level_part(monkeypatch):
    """ispect=1 (experimental levels only) equals ispect=3's discrete part: the per-level loop does
    not depend on whether continuum bins follow."""
    r3 = R.racap_xs(82, 208, E, ispect=3)
    r1 = R.racap_xs(82, 208, E, ispect=1)
    np.testing.assert_allclose(r1["total_mb"], r3["disc_mb"], rtol=1e-6)
    monkeypatch.setenv("INCOGNITA_DIRECT_CAPTURE", "disc")
    np.testing.assert_allclose(R.direct_capture_mb(82, 208, E), r1["total_mb"], rtol=0)
