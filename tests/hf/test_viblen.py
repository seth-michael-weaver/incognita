"""VIBLEN: `dwbaimag` keyword (complex DWBA transition potential, default off) and the DWBA angular distributions.

Model only, no data."""

from __future__ import annotations

import math
import os

import numpy as np
import pytest
import torch

from physics.hf.ecis.formfactor import ALL_CENTRAL_PARTS, DWBA_PARTS, DWBAIMAG_ENV, dwba_parts


@pytest.fixture(autouse=True)
def _restore_grad_mode():
    """The tests below switch autograd off; give the next test module the mode it started with."""
    prev = torch.is_grad_enabled()
    yield
    torch.set_grad_enabled(prev)


class _Opt:
    def __init__(self, v):
        self.dwbaimag = v


def test_dwbaimag_default_off(monkeypatch):
    monkeypatch.delenv(DWBAIMAG_ENV, raising=False)
    assert dwba_parts(None) == DWBA_PARTS
    assert dwba_parts(_Opt("n")) == DWBA_PARTS


def test_dwbaimag_keyword_and_env(monkeypatch):
    monkeypatch.delenv(DWBAIMAG_ENV, raising=False)
    assert dwba_parts(_Opt("y")) == ALL_CENTRAL_PARTS
    monkeypatch.setenv(DWBAIMAG_ENV, "y")
    assert dwba_parts(None) == ALL_CENTRAL_PARTS
    assert dwba_parts(_Opt("n")) == ALL_CENTRAL_PARTS  # env used when the keyword is off
    monkeypatch.setenv(DWBAIMAG_ENV, "bogus")
    with pytest.raises(ValueError):
        dwba_parts(None)


def test_dwbaimag_is_an_input_keyword():
    from physics.hf.input.defaults import default_options
    assert hasattr(default_options(26, 56), "dwbaimag")
    assert default_options(26, 56).dwbaimag == "n"


def _fe56_case(e=14.0):
    from physics.hf.direct import chain, dwba as D, prepare as P
    from physics.hf.ecis.dwba import prepare_case
    cs = P.case("Fe056", e, (e,))
    lv = D.direct_levels(cs.struct, cs.eninccm_mev, cs.eoutdis_mev, e, cs.options.k0)
    omp = chain._omp_for(cs.Z, cs.A, e, int(cs.options.k0), (e,))
    return cs, omp, prepare_case(omp, cs.target, e, direct_case=cs, levels=lv)


def test_complex_form_factor_raises_the_2plus_and_off_is_default(monkeypatch):
    monkeypatch.delenv(DWBAIMAG_ENV, raising=False)
    from physics.hf.ecis.dwba import dwba_case
    torch.set_grad_enabled(False)
    cs, omp, case = _fe56_case()
    off, _ = dwba_case(omp, case, refine=4)
    off2, _ = dwba_case(omp, case, refine=4, parts=dwba_parts(cs.options))
    on, _ = dwba_case(omp, case, refine=4, parts=ALL_CENTRAL_PARTS)
    assert torch.equal(off, off2)
    assert float(on[0]) > 1.05 * float(off[0])


def test_angular_distribution_integral_and_plane_wave_limit():
    from scipy.special import spherical_jn
    from physics.hf.ecis import dwba_angular as DA
    from physics.hf.ecis.dwba import dwba_cross_sections
    torch.set_grad_enabled(False)
    cs, omp, case = _fe56_case()
    b = [0]
    args = (omp, cs.Z, cs.A, 14.0, case.e_mev[b], case.spin[b], case.parity[b], case.vibbeta[b], case.deformation_length)
    ri = DA.radial_integrals(*args, parts=ALL_CENTRAL_PARTS)
    port = float(dwba_cross_sections(*args, parts=ALL_CENTRAL_PARTS).xs_mb[0])
    lam, beta = int(case.spin[0]), float(case.vibbeta[0])
    _, sig, cst = DA.normalised_da(ri, 0, lam, int(case.parity[0]), beta, np.array([30.0]))
    assert abs(sig / port - 1) < 2e-3
    k0, kb, mu, d = ri["k"][0], ri["k"][1], ri["mu"], beta / math.sqrt(4 * math.pi)
    cexp = (mu / (4 * math.pi)) ** 2 * (kb / k0) * (4 * math.pi) ** 4 / (k0 * kb) ** 2 / 16.0 * d ** 2 * 10.0
    assert abs(cst / cexp / (4 * math.pi / (2 * lam + 1)) - 1) < 1e-3  # closed-form normalisation (mb = 10 fm^2)
    ri = DA.radial_integrals(*args, parts=DWBA_PARTS, free_waves=True)
    th = np.linspace(10, 170, 9)
    da, sig, _ = DA.normalised_da(ri, 0, lam, int(case.parity[0]), beta, th)
    r, w = ri["r"], ri["w"].real
    tg = np.linspace(0, 180, 721)

    def born(t):
        q = np.sqrt(ri["k"][0] ** 2 + ri["k"][1] ** 2 - 2 * ri["k"][0] * ri["k"][1] * np.cos(np.radians(t)))
        return np.array([np.trapezoid(spherical_jn(lam, x * r) * w * r ** 2, r) ** 2 for x in q])
    bg = born(tg)
    bn = born(th) * sig / (2 * math.pi * np.trapezoid(bg * np.sin(np.radians(tg)), np.radians(tg)))
    assert np.max(np.abs(np.log10(da / bn))) < 1e-3
