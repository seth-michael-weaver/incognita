"""KWCOV B1 (CHANOBS): channel observables TALYS writes by default, named as its files.

* unit: names, residual mapping, isomer level numbers, the particle-production completion (`binary_adds`) and that
  `full_xsbinary` (TRITFID) still adds in the same order;
* engine (needs the native build, TALYS structure/ and a stock TALYS-2.25 run of Co-59 at 1, 5, 14 MeV in
  $KWCOV_STOCK/co59, made by scripts/kwcov/b1_compare.py's recipe): the switch is output only (every other array
  bit-identical), isomer files sum to their channel, and every name agrees with stock TALYS: <= 0.5 % at 1 and
  5 MeV, <= 12 % at 14 MeV where the engine's channels themselves differ from TALYS by up to 7 %.
"""

from __future__ import annotations

import math
import os
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
import torch

from physics.hf.emission import chanobs

ROOT = Path(__file__).resolve().parents[2]
STOCK = Path(os.environ.get("KWCOV_STOCK", Path.home() / "kwcov/stock"))
TALYS_DIR = Path(os.environ.get("TALYS_DIR", Path.home() / "opt/talys-src"))


def test_off_by_default(monkeypatch):
    monkeypatch.delenv(chanobs.ENV, raising=False)
    assert not chanobs.enabled()
    monkeypatch.setenv(chanobs.ENV, "1")
    assert chanobs.enabled()


def test_residual_of():
    assert chanobs.residual_of(200000, 27, 60) == (27, 58)  # Co-59(n,2n)Co-58
    assert chanobs.residual_of(1, 27, 60) == (25, 56)  # (n,a)
    assert chanobs.residual_of(10000, 26, 57) == (25, 56)  # (n,p)
    assert chanobs.residual_of(110000, 26, 57) == (25, 55)  # (n,np)


def _ch():
    return SimpleNamespace(
        xsparticle_mb={0: 10.0, 1: 100.0, 2: 5.0}, multiplicity={0: 0.1, 1: 1.0, 2: 0.05},
        xsexclusive_mb={0: 2.0, 1: 50.0, 2: 4.0},
        xsgamchannel_mb={0: 3.0, 200000: 7.0, 100000: 40.0}, xsfischannel_mb={100000: 1.5},
        xschaniso_mb={200000: {0: 2.0, 1: 3.0}, 0: {0: 2.0}}, exclbranch={200000: {0: 0.4, 1: 0.6}},
    )


def _b():
    return SimpleNamespace(xsbinary_mb=torch.arange(8, dtype=torch.float64), xsdisctot_mb=torch.full((7,), 1.0),
                           xsnonel_mb=100.0)


def test_extras_names(monkeypatch):
    monkeypatch.setenv("INCOGNITA_TRITFID", "1")  # completion off: values as the channels gave them
    x = chanobs.extras(_ch(), _b(), 1, 27, 59, levnum=lambda z, a: {1: 2} if (z, a) == (27, 58) else None)
    assert x["nprod.tot"] == 100.0 and x["nprod.tot:multiplicity"] == 1.0
    assert x["binary.tot:g"] == 1.0 and x["binary.tot:a"] == 7.0  # xsbinary is indexed -1..6
    assert x["np.tot:discrete"] == 1.0 and x["np.tot:continuum"] == 3.0
    assert x["xs200000.tot:gamma"] == 7.0 and x["xs100000.fis"] == 1.5
    assert x["xs200000.L00"] == 2.0 and x["xs200000.L02"] == 3.0  # level number 2, not nex 1
    assert x["xs200000.L02:branch"] == 0.6
    assert "xs000000.L00" not in x  # no isomer in the residual: no isomer file


def test_particle_production_completion(monkeypatch):
    monkeypatch.setenv("INCOGNITA_TRITFID", "0")
    binp = SimpleNamespace(grids={0: 0, 1: 0, 2: 0}, xsdirdisctot_mb={1: 20.0, 2: 1.0}, flagpreeq=True,
                           xspreeqtot_mb={1: 30.0, 2: 2.0}, xsgrtot_mb={1: 5.0}, xsracape_mb=0.5)
    x = chanobs.extras(_ch(), _b(), 1, 27, 59, binp=binp)
    assert x["nprod.tot"] == pytest.approx(155.0)
    assert x["pprod.tot"] == pytest.approx(8.0)
    assert x["gprod.tot"] == pytest.approx(10.5)
    assert x["nprod.tot:multiplicity"] == pytest.approx(1.55)  # same xsnonel (100) the channels used


def test_full_xsbinary_order_unchanged(monkeypatch):
    """TRITFID adds per type in grid order, then direct capture to gamma: the same float order as before KWCOV."""
    from physics.hf.emission.multiple import full_xsbinary

    monkeypatch.setenv("INCOGNITA_TRITFID", "1")
    binp = SimpleNamespace(grids={0: 0, 1: 0}, xsdirdisctot_mb={0: 0.1, 1: 0.2}, flagpreeq=True,
                           xspreeqtot_mb={0: 0.3, 1: 0.7}, xsgrtot_mb={0: 1e-17}, xsracape_mb=0.3)
    xb = torch.tensor([0.0, 0.1, 0.2, 0, 0, 0, 0, 0], dtype=torch.float64)
    got = full_xsbinary(binp, xb)
    ref = xb.clone()
    ref[1] = ref[1] + (0.1 + (0.3 + 1e-17))
    ref[2] = ref[2] + (0.2 + (0.7 + 0.0))
    ref[1] = ref[1] + 0.3
    assert torch.equal(got, ref)


def _built() -> bool:
    try:
        from physics.hf import engine_c

        return engine_c.lib() is not None
    except Exception:  # noqa: BLE001
        return False


@pytest.mark.skipif(not (TALYS_DIR / "structure").is_dir() or not (STOCK / "co59/xs200000.L01").is_file()
                    or not _built(), reason="needs TALYS structure/, a native build and the stock Co-59 run")
def test_co59_against_stock_talys(monkeypatch):
    sys.path.insert(0, str(ROOT / "scripts/kwcov"))
    import b1_compare as B
    import numpy as np

    st = B.stock_values(STOCK / "co59")
    E = st.pop("E")
    off, _, _ = B.engine_values(27, 59, E, False)
    on, ex, _ = B.engine_values(27, 59, E, True)
    monkeypatch.delenv(chanobs.ENV, raising=False)
    for k, v in off.items():  # output only
        assert np.array_equal(v, on[k]), k
    iso = ex["xs200000.L00"] + ex["xs200000.L01"]
    assert np.allclose(iso, ex["xs200000.tot"], rtol=1e-9)
    scored = 0
    for k, t in st.items():
        e = ex.get(k)
        assert e is not None or not np.any(t > 1.0), k
        if e is None:
            continue
        ratio_like = k.endswith((":multiplicity", ":branch"))
        for i, (ev, tv) in enumerate(zip(E, t)):
            if tv <= (1e-3 if ratio_like else 1.0):
                continue
            r = abs(math.log(e[i] / tv))
            assert r <= (0.005 if ev <= 5.0 else 0.12), (k, ev, e[i], tv)
            scored += 1
    assert scored > 60
