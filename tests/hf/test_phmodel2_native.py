"""fast-phmodel: `phmodel 2` (tabulated HFB particle-hole densities, PHMICRO) on the C cascade.

The tables reach the compiled multipreeq2 (`mpe_bin`, nativex.c) packed by `particle_hole.ph_table_packed`;
`INCOGNITA_PHFAST=0` keeps the PHMICRO reference (Python engine, torch multipreeq2 loop).

* chained Fe-56 at 14/20 MeV, PHNORM off and on: every `Results` array of the C call within 1e-9 relative of the
  reference, with every energy taken by the C call;
* the same C call with the tables withheld from `mpe_bin` (analytic densities there) moves the result, so the
  agreement above is not vacuous;
* the packed table is the one `ph_override` reads (divisor, exists mask, smoothed rows).
"""

from __future__ import annotations

import os
from pathlib import Path

import numpy as np
import pytest
import torch

from physics.hf.density import particle_hole as P

TALYS_DIR = Path(os.environ.get("TALYS_DIR", Path.home() / "opt/talys-src"))
needs_structure = pytest.mark.skipif(not (TALYS_DIR / "structure").is_dir(),
                                     reason="TALYS structure/ not installed")


def _built() -> bool:
    from physics.hf import engine_c

    return engine_c.lib() is not None


needs_build = pytest.mark.skipif(not _built(), reason="no libengdecay build (scripts/build_engine_c_native.sh)")

GRID = (1.0e-3, 0.5, 2.0, 5.0, 8.0, 11.0, 14.0, 20.0)


def _run(Z, A, energies, use_c):
    from physics.hf import engine_c, warmrun
    from physics.hf.chartrun import drop_target_caches
    from physics.hf.engine import ChainedFull, run

    drop_target_caches()
    stats = {}
    zf = ChainedFull(Z=Z, A=A, declared_energies=GRID, energies=energies)
    with torch.inference_mode():
        r = engine_c.run(zf, stats) if use_c else run(injection=zf)
    return warmrun.result_arrays(r), stats


def _close(got, ref, rtol):
    assert sorted(ref) == sorted(got)
    for k in ref:
        np.testing.assert_allclose(got[k], ref[k], rtol=rtol, atol=0.0, err_msg=k)


@needs_structure
@needs_build
@pytest.mark.parametrize("norm", ["0", "1"])
def test_fe56_phmodel2_c_matches_reference(monkeypatch, norm):
    monkeypatch.setenv("INCOGNITA_PHMODEL", "2")
    monkeypatch.setenv("INCOGNITA_PHNORM", norm)
    monkeypatch.setenv("INCOGNITA_PHFAST", "0")
    ref, _ = _run(26, 56, (14.0, 20.0), use_c=True)  # INCOGNITA_PHFAST=0: engine_c.run hands phmodel 2 to engine.run
    monkeypatch.setenv("INCOGNITA_PHFAST", "1")
    got, stats = _run(26, 56, (14.0, 20.0), use_c=True)
    assert not any(k.endswith("fallback") for k in stats), stats
    assert stats["c"] == 2, stats
    _close(got, ref, 1e-9)
    # the tables withheld from mpe_bin (mi[16] set, NULL tables = analytic): multipreeq2 moves
    real = P.phfast_tables
    monkeypatch.setattr(P, "phfast_tables", lambda *a: (real(*a)[0], [None, None, None]))
    ana, _ = _run(26, 56, (14.0, 20.0), use_c=True)
    moved = [k for k in got if got[k].shape == ana[k].shape and not np.allclose(got[k], ana[k], rtol=1e-6, atol=0.0)]
    assert moved, "phmodel-2 tables had no effect in mpe_bin"


def test_packed_table_is_the_override_table(monkeypatch):
    if P.ph_table2(81, 208) is None:
        pytest.skip("no structure/density/ph tables")
    monkeypatch.delenv("INCOGNITA_PHNORM", raising=False)
    assert P.ph_table_packed(0, 0, None) is None and P.ph_table_packed(5, 0, (82, 127)) is None
    t = P.ph_table_packed(1, 0, (82, 127))  # Tl-208 (odd-odd)
    ex, tab = P.ph_table2(81, 208)
    assert t[0] == 1.0 and np.array_equal(t[1:626], ex.reshape(-1)) and np.array_equal(t[626:], tab.reshape(-1))
    monkeypatch.setenv("INCOGNITA_PHNORM", "1")
    assert P.ph_table_packed(1, 0, (82, 127))[0] == 4.0
