"""OMPDEF: the deformed-region OMP rule (`regional.DEFORMED_POINT`) and TALYS's ejectile OMP
convention (`parameters.ejectile_params`)."""

from __future__ import annotations

import pytest
import torch

from physics.hf.input.defaults import default_options, default_params
from physics.hf.omp import regional
from physics.hf.omp.parameters import ejectile_params


def _params(Z: int, A: int):
    return default_params(Z, A, default_options(Z, A))


def test_the_shipped_default_is_off():
    import subprocess
    import sys

    out = subprocess.run(
        [sys.executable, "-c",
         "from physics.hf.omp import regional; print(regional.deformed_enabled())"],
        capture_output=True, text=True, check=True, env={"PATH": "/usr/bin:/bin"})
    assert out.stdout.strip() == "False", out


@pytest.mark.parametrize("Z,A,member", [
    (74, 182, True), (64, 158, True), (76, 188, True), (79, 197, True), (60, 148, True),
    (26, 56, False), (50, 120, False), (24, 52, False),   # Cr-52 is `R` but below A = 140
    (92, 238, False), (90, 232, False),                    # actinides: Soukhovitskii CC OMP
    (76, 192, False), (78, 196, False),                    # spherical (`S`)
])
def test_region_is_colltype_R_rare_earth_side(Z, A, member):
    assert regional.deformed_member(Z, A) is member


def test_member_gets_the_point_and_talys_links_follow():
    prev = regional.set_deformed(True)
    try:
        p = _params(74, 182)
        assert float(p["rvadjust"][1]) == pytest.approx(regional.DEFORMED_POINT["rvadjust"]["n"])
        assert float(p["avadjust"][1]) == pytest.approx(regional.DEFORMED_POINT["avadjust"]["n"])
        # input_omppar.f90:632: rw/aw follow rv/av unless given
        assert float(p["awadjust"][1]) == pytest.approx(regional.DEFORMED_POINT["avadjust"]["n"])
        q = _params(26, 56)
        assert float(q["rvadjust"][1]) == 1.0 and float(q["avadjust"][1]) == 1.0
        assert regional.region_of(74, 182) == "deformed"
    finally:
        regional.set_deformed(prev)


def test_ejectile_params_is_identity_at_defaults():
    p = _params(74, 182)
    assert ejectile_params(p, 1) is p


def test_ejectile_neutron_takes_type0_factors():
    """inverseecis.f90:220 flagompejec -> opticalnp.f90:175 ktype = 0: an outgoing neutron
    never sees `rvadjust n`; the protons keep theirs."""
    prev = regional.set_deformed(True)
    try:
        p = _params(74, 182)
        e = ejectile_params(p, 1)
        assert e is not p
        for key in ("rvadjust", "avadjust", "rwadjust", "awadjust"):
            assert float(e[key][1]) == float(p[key][0]) == 1.0
            assert torch.equal(e[key][2:], p[key][2:])
        assert float(p["avadjust"][1]) != 1.0          # the incident channel keeps the rule
    finally:
        regional.set_deformed(prev)
