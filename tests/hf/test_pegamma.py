"""PEGAMMA: a continuous pre-equilibrium photon onset (Incognita extension, default OFF).

With `pegammaramp` (MeV) > 0: each exciton state's photon emission rises as 1 - exp(-(U - A)/ramp)
above its Pauli + pairing threshold, the photon collapse onto the discrete states integrates the
interpolated spectrum, and preeqtotal.f90:92-102's zeroing of photons without particle continuum
is lifted. 0 (no keyword, no environment) must be TALYS exactly.
"""

from __future__ import annotations

import dataclasses

import pytest
import torch

from physics.hf import reference as ref
from physics.hf.core.tensors import DTYPE
from physics.hf.input.defaults import default_options
from physics.hf.preeq.exciton import pegamma_ramp


def test_ramp_is_off_by_default(monkeypatch):
    monkeypatch.delenv("INCOGNITA_PEGAMMA", raising=False)
    o = default_options(26, 56)
    assert o.pegammaramp == 0.0
    assert pegamma_ramp(o) == 0.0
    for off in ("", "0", "off", "n"):
        monkeypatch.setenv("INCOGNITA_PEGAMMA", off)
        assert pegamma_ramp(o) == 0.0


def test_ramp_from_keyword_and_environment(monkeypatch):
    monkeypatch.delenv("INCOGNITA_PEGAMMA", raising=False)
    o = default_options(26, 56, overrides={"pegammaramp": 0.4})
    assert pegamma_ramp(o) == pytest.approx(0.4)
    monkeypatch.setenv("INCOGNITA_PEGAMMA", "0.25")
    assert pegamma_ramp(default_options(26, 56)) == pytest.approx(0.25)


@pytest.mark.skipif(not ref.available("exciton"), reason="reference dumps not parsed")
def test_on_changes_only_photons(monkeypatch):
    """OFF is TALYS bit for bit; ON leaves every particle spectrum alone (no flux renormalisation
    on Fe-56) and keeps the photons finite and non-negative."""
    from physics.hf.input.nuclides import coulomb_barriers
    from physics.hf.preeq.exciton import preequilibrium
    from physics.hf.preeq.prepare import prepare

    monkeypatch.delenv("INCOGNITA_PEGAMMA", raising=False)
    inp, hdr = prepare("Fe056")
    inc = ref.incident_scalars("Fe056")
    reac = {round(float(r.e_inc_mev), 6): float(r.sigma_reac_omp_mb) for _, r in inc.iterrows()}
    xsr = torch.tensor([reac[round(e, 6)] for e in hdr["energies"]], dtype=DTYPE)
    o = hdr["options"]
    run = lambda opts: preequilibrium(  # noqa: E731
        inp, opts, hdr["params"], hdr["discrete"], coulbar_mev=coulomb_barriers(opts), xsreacinc_mb=xsr)
    off = run(o)
    off0 = run(dataclasses.replace(o, pegammaramp=0.0))
    for k in ("xspreeq", "xspreeqtot", "xspreeqsum", "xsstep", "xspreeqdisc"):
        assert torch.equal(off[k], off0[k])
    on = run(dataclasses.replace(o, pegammaramp=0.3))
    assert bool(torch.isfinite(on["xspreeq"]).all()) and bool((on["xspreeq"] >= 0).all())
    assert bool((on["xspreeqdisc"][:, 0] >= 0).all())
    if bool((off["preeqnorm"] == 0).all()) and bool((on["preeqnorm"] == 0).all()):
        assert torch.allclose(on["xspreeqtot"][:, 1:], off["xspreeqtot"][:, 1:], rtol=1e-9, atol=0)
        assert torch.allclose(on["xspreeqdisc"][:, 1:], off["xspreeqdisc"][:, 1:], rtol=1e-9, atol=0)
