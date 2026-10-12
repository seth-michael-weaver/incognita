"""SPEEDFIX lever 1: a tabulated M1 (strengthM1 >= 8, the `nodata`/B55 recipe) is covered by
`psf_fast.fstrength_np` (bitwise) and by the C kernel `psf_nx2` (closeness), so the C front and
`ce_cascade` no longer fall back to Python at every energy."""
import os

import numpy as np
import pytest
import torch


@pytest.fixture
def gp_m1(monkeypatch):
    from physics.hf import chartrun, warmrun
    from physics.hf.input import fitlib

    for k in [k for k in os.environ if k.startswith("INCOGNITA_")]:
        monkeypatch.delenv(k, raising=False)
    monkeypatch.setenv("INCOGNITA_TALYS_FIT", "nodata")
    fitlib.deactivate(); fitlib._cards.cache_clear(); chartrun.drop_target_caches()
    cas = warmrun.new_cascade(28, 58, (1.0,))
    gp = cas.gamma_params(28, 59)
    if not (gp.qrpaexist(0, 1) and gp.strengthM1 >= 8):
        pytest.skip("this TALYS_DIR has no M1 table for Ni-59")
    yield gp
    fitlib.deactivate(); chartrun.drop_target_caches()


def test_numpy_m1_table_bitwise(gp_m1):
    from physics.hf.compound import psf_fast
    from physics.hf.gamma.strength import fstrength_gp

    eg = np.linspace(5e-4, 25.0, 2001)
    for efs in (0.0, 3.0, 12.0, 30.0):
        for irad in (0, 1):
            for l in range(1, gp_m1.gammax + 1):  # noqa: E741
                ref = fstrength_gp(gp_m1, efs, torch.tensor(eg, dtype=torch.float64), irad, l).numpy()
                got = psf_fast.fstrength_np(gp_m1, efs, eg, irad, l)
                assert got is not None
                assert np.array_equal(ref, got), (efs, irad, l)


def test_c_m1_table_close(gp_m1):
    from physics.hf.compound import psf_nx2
    from physics.hf.gamma.strength import fstrength_gp

    eg = np.linspace(5e-4, 25.0, 2001)
    for efs in (0.0, 3.0, 12.0):
        tg = psf_nx2.tgam_points(gp_m1, gp_m1.gammax, efs, eg, 2.0 * np.pi, 1.0)
        if tg is None:
            pytest.skip("no libnx2 build")
        for irad in (0, 1):
            for l in range(1, gp_m1.gammax + 1):  # noqa: E741
                ref = fstrength_gp(gp_m1, efs, torch.tensor(eg, dtype=torch.float64), irad, l).numpy()
                ref = ref * 2.0 * np.pi * eg ** (2 * l + 1)
                got = tg[:, l, irad]
                m = np.abs(ref) > 0
                assert not np.any(got[~m])
                if m.any():
                    assert np.max(np.abs(got - ref)[m] / np.abs(ref[m])) < 1e-12, (efs, irad, l)
