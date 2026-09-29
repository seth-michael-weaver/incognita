"""CENGDECAY (ROUTE100 WP5): `engine_c.run` holds `engine.run(injection=ChainedFull(...))`.

* chained Fe-56 on four energies (the 20 MeV one runs multiple pre-equilibrium in the C call):
  every `Results` array to the bit, with every energy taken by the C call;
* chained U-238 on three energies (fission ladder through the callback): every array to 1e-12
  relative (the fission path moves the last bits from run to run by itself);
* with `HF_ENGINE_C=0` it is `engine.run`.
"""

from __future__ import annotations

import os
from pathlib import Path

import numpy as np
import pytest
import torch

TALYS_DIR = Path(os.environ.get("TALYS_DIR", Path.home() / "opt/talys-src"))
needs_structure = pytest.mark.skipif(not (TALYS_DIR / "structure").is_dir(),
                                     reason="TALYS structure/ not installed")


def _built() -> bool:
    from physics.hf import engine_c

    return engine_c.lib() is not None


needs_build = pytest.mark.skipif(not _built(), reason="no libengdecay build "
                                 "(scripts/build_engine_c_native.sh)")

GRID = (1.0e-3, 0.5, 2.0, 5.0, 8.0, 11.0, 14.0, 20.0)


def _arrays(res) -> dict[str, np.ndarray]:
    from physics.hf import warmrun

    return warmrun.result_arrays(res)


def _pair(Z: int, A: int, energies):
    from physics.hf import engine_c
    from physics.hf.chartrun import drop_target_caches
    from physics.hf.engine import ChainedFull, run

    out = []
    stats = {}
    for use_c in (False, True):
        drop_target_caches()
        zf = ChainedFull(Z=Z, A=A, declared_energies=GRID, energies=energies)
        with torch.inference_mode():
            r = engine_c.run(zf, stats) if use_c else run(injection=zf)
        out.append(_arrays(r))
    return out[0], out[1], stats


@needs_structure
@needs_build
def test_fe56_bitwise_every_energy_in_c():
    ref, got, stats = _pair(26, 56, (2.0, 8.0, 14.0, 20.0))
    assert not any(k.endswith("fallback") for k in stats), stats
    assert stats["c"] == 4  # the energies walked only for `sfactor` stop before the cascade
    # CENGBOOK: the primary densprepare/comptarget and the channels in C at every kept energy
    assert stats.get("front_c") == 8 and stats.get("channels_c") == 4, stats  # front: all walked
    assert sorted(ref) == sorted(got)
    for k in ref:
        np.testing.assert_array_equal(got[k], ref[k], err_msg=k)


@needs_structure
@needs_build
def test_u238_close_with_fission():
    ref, got, stats = _pair(92, 238, (2.0, 8.0, 14.0))
    assert not any(k.endswith("fallback") for k in stats), stats
    assert stats.get("front_c") == 7 and stats.get("channels_c") == 3, stats
    assert sorted(ref) == sorted(got)
    for k in ref:
        np.testing.assert_allclose(got[k], ref[k], rtol=1e-12, atol=0.0, err_msg=k)


@needs_structure
def test_switch_off_is_engine_run(monkeypatch):
    from physics.hf import engine_c

    monkeypatch.setenv("HF_ENGINE_C", "0")
    engine_c.lib.cache_clear()
    try:
        assert engine_c.lib() is None
    finally:
        monkeypatch.delenv("HF_ENGINE_C")
        engine_c.lib.cache_clear()
