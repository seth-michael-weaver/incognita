"""FIXENG F15: nonelastic != sum of exclusive channels (BASICS RC14), reproduced on our engine (stock defaults, no fit
lines) and fixed behind INCOGNITA_WFCNORM (keV: Moldauer Gauss-Laguerre leak + coupled-channels pi/k^2 at the true energy
against ECIS at the card energy) and INCOGNITA_NGNEXCL ((n,gamma X) flux of the compound's gamma-fed bins, TALYS's
`xsngn`, outside every exclusive channel). Both default OFF; OFF must be TALYS's path to the bit.

Reproducers: n + O-16 at 1-2 keV (nonelastic ~1 mb next to ~3 b compound elastic: the 2.7e-4 relative leak is 90 % of
the nonelastic), n + Cr-52 at 1.6 keV (coupled channels: E_card/E - 1 = +2.8e-4 puts the channels 3.5 % above the
nonelastic)."""
from __future__ import annotations

import numpy as np
import pytest
import torch

from physics.hf.compound import wfcnorm
from physics.hf.emission import multiple

E_KEV = tuple(float(np.float32(e)) for e in (1.0e-3, 1.6025e-3))


def _run(monkeypatch, Z, A, env):
    from physics.hf import chartrun, warmrun
    from physics.hf.engine import ChainedFull
    from physics.hf.engine_c import run as engine_run

    for k in ("INCOGNITA_WFCNORM", "INCOGNITA_NGNEXCL"):
        monkeypatch.delenv(k, raising=False)
    for k, v in env.items():
        monkeypatch.setenv(k, v)
    torch.set_num_threads(1)
    chartrun.drop_target_caches()
    cas = warmrun.new_cascade(Z, A, E_KEV)
    with torch.inference_mode():
        res = engine_run(injection=ChainedFull(Z=Z, A=A, declared_energies=E_KEV, cascade=cas))
    tot = {k: v.detach().cpu().numpy().astype(float) for k, v in res.totals_mb.items() if hasattr(v, "detach")}
    ch = sum(v.detach().cpu().numpy().astype(float) for v in res.channels_mb.values())
    chartrun.drop_target_caches()
    return tot, ch + tot.get("fission", 0.0)


def test_factor_and_flags(monkeypatch):
    assert wfcnorm.factor(0.0, 0.0, 5.0) == 1.0 and wfcnorm.factor(2.0, 0.0, 0.0) == 1.0
    assert wfcnorm.factor(999.73, 0.0, 1000.0) == pytest.approx(1000.0 / 999.73)
    monkeypatch.delenv("INCOGNITA_NGNEXCL", raising=False)
    assert not multiple._records_feedexcl(0, 0, 1) and multiple._records_feedexcl(0, 0, 0)
    monkeypatch.setenv("INCOGNITA_NGNEXCL", "1")
    assert multiple._records_feedexcl(0, 0, 1) and not multiple._records_feedexcl(7, 0, 1)


@pytest.mark.parametrize("Z,A", [(8, 16), (24, 52)])
def test_kev_channels_close_on_the_nonelastic(monkeypatch, Z, A):
    tot0, ch0 = _run(monkeypatch, Z, A, {})
    r0 = ch0 / tot0["nonelastic"]
    assert np.any(np.abs(r0 - 1.0) > 0.03)          # the defect, OFF
    tot1, ch1 = _run(monkeypatch, Z, A, {"INCOGNITA_WFCNORM": "1"})
    r1 = ch1 / tot1["nonelastic"]
    assert np.all(np.abs(r1 - 1.0) < 0.03)
    # total and the reaction cross section are not touched; only the compound elastic / nonelastic split moves
    np.testing.assert_allclose(tot1["reaction"], tot0["reaction"], rtol=1e-12)
    np.testing.assert_allclose(tot1["total"], tot0["total"], rtol=1e-12)
