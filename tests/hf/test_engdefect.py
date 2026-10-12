"""ENGDEFECT: nonelastic > reaction (up to x100) in 565 far-from-stability chart nuclei.

n + Am-308 (Z=95, N=213; its own Sn is -0.24 MeV in TALYS's mass table, i.e. the target is past the neutron
drip line) at 0.2-2.6 MeV: first-order DWBA to the default 2+ vibrational level (beta 0.128, deformpar.f90:310)
on an almost real optical potential (Wd = 0.04 MeV) gives sigma_direct = 3.1e5 mb against sigma_R = 1.4e3 mb.
compnorm.f90 then makes xsflux = sigma_R - sigma_direct - ... = -3.1e5 mb, and comptarget.f90:256 returns at once
(`if (xsflux <= xseps) return`): no compound decay at that energy, so TALYS's compound elastic and fission are 0 and
its nonelastic (binary.f90:318, max(xsreacinc - xscompel, 0)) equals sigma_R.

The port had no such return: it ran comptarget with CNfactor * cfratio < 0, i.e. NEGATIVE populations. Compound
elastic came out at -3e5 mb, so nonelastic = sigma_R - xscompel was x100 sigma_R, and fission went negative.
Stock TALYS-2.25 on the same input (strength 8, same structure) has none of that. This file pins the fix.

The x100 (n,2n) / residual production itself is TALYS's (direct > reaction is not bounded in TALYS either) and is
NOT changed here; see development notes.
"""
from __future__ import annotations

import numpy as np
import pytest
import torch

Z, A = 95, 308
# MeV, float32-rounded Stage C grid points: 0.287 (xsflux > 0), then 0.336 / 0.393 / 0.538 (xsflux < 0 in TALYS)
E_MEV = tuple(float(np.float32(e)) for e in (0.2869006, 0.3357390, 0.3928910, 0.5380377))


@pytest.fixture(scope="module")
def run():
    from physics.hf import chartrun, warmrun
    from physics.hf.engine import ChainedFull
    from physics.hf.engine_c import run as engine_run

    torch.set_num_threads(1)
    cas = warmrun.new_cascade(Z, A, E_MEV)
    with torch.inference_mode():
        res = engine_run(injection=ChainedFull(Z=Z, A=A, declared_energies=E_MEV, cascade=cas))
    out = {k: v.detach().cpu().numpy().astype(float) for k, v in res.totals_mb.items() if hasattr(v, "detach")}
    out["xs200000"] = res.channels_mb["xs200000"].detach().cpu().numpy().astype(float)
    chartrun.drop_target_caches()
    return out


def test_far_target_really_has_negative_flux(run):
    """The case is the one the chart flagged: sigma_direct >> sigma_R at 0.336 MeV (via (n,2n), TALYS's own)."""
    assert run["xs200000"][1] > 10 * run["reaction"][1]


def test_nonelastic_never_exceeds_reaction(run):
    assert np.all(run["nonelastic"] <= run["reaction"] * (1 + 1e-6) + 1e-9)


def test_no_negative_compound_cross_sections(run):
    assert np.all(run["fission"] >= -1e-9)
    assert np.all(run["compound_elastic"] >= -1e-9)


def test_nonelastic_is_reaction_minus_compound_elastic(run):
    """binary.f90:318; where xsflux <= xseps there is no compound elastic, so nonelastic == sigma_R (stock: 1411.16 mb
    at 0.336 MeV)."""
    ne = np.maximum(run["reaction"] - run["compound_elastic"], 0.0)
    np.testing.assert_allclose(run["nonelastic"], ne, rtol=1e-6, atol=1e-9)
    np.testing.assert_allclose(run["nonelastic"][1:], run["reaction"][1:], rtol=1e-6)


def test_gpu_batch_path_has_no_compound_where_xsflux_is_negative(run):
    """The batch path (`gpu_full_setup` -> `gpu_full.run_batch`, CPU device here) builds its own CNfactor and now
    takes the same guard. Unlike the CPU/C paths it did NOT show the defect before (with CNfactor < 0 its nonelastic
    was already sigma_R), so this is a parity check, not a failing-first test: it pins batch == fixed CPU engine."""
    from physics.hf.gpu_full import run_batch
    from physics.hf.gpu_full_setup import setup_nuclide

    torch.set_num_threads(1)
    out = run_batch([(setup_nuclide(Z, A, E_MEV), i) for i in range(len(E_MEV))], torch.device("cpu"))
    np.testing.assert_allclose(out["nonelastic"].cpu().numpy()[1:], run["reaction"][1:], rtol=1e-4)
    for k, v in out.items():
        if not k.startswith("_") and hasattr(v, "cpu"):
            assert float(v.cpu().min()) >= -1e-9, k
