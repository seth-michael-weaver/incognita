"""FISTSC: the batched fission paths with a rotational band on the barriers (`fists2 y`).

`fists2` (TS2FREEZE) puts the even-even saddle K-band transition states on every barrier, which the
batched paths (`fission_batch_ladder`, CENGFIS, NX2 `fis2`'s ladder) used to refuse, so the C
cascade ran those compounds in Python. With FISTSC they add `barriers.band_ladder` to their
continuum sums. Held here to the per-bin torch path (`FissionChain.bin_triples` +
`continuum.fission_width`, i.e. `t1barrier`'s band branch) and to `fission_transmission`; with
`HF_NX2_FISTSC=0` the refusal is back.
"""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest
import torch

from physics.hf.native import nx2

TALYS_DIR = Path(__import__("os").environ.get("TALYS_DIR", Path.home() / "opt/talys-src"))
pytestmark = [
    pytest.mark.skipif(nx2.lib() is None, reason="no libnx2 build"),
    pytest.mark.skipif(not (TALYS_DIR / "structure").is_dir(), reason="no TALYS structure/"),
]

# (target, even-even fissioning nucleus): two- and three-humped barriers
CASES = [(92, 235, 92, 236), (92, 238, 92, 238), (90, 232, 90, 232), (94, 239, 94, 240)]


@pytest.fixture(autouse=True)
def _ts2(monkeypatch):
    monkeypatch.setenv("INCOGNITA_FIS_TS2", "1")
    monkeypatch.delenv("HF_NX2_FISTSC", raising=False)
    prev = torch.get_num_threads()
    torch.set_num_threads(1)
    yield
    torch.set_num_threads(prev)


def _rel(a, b) -> float:
    a, b = np.asarray(a, dtype=np.float64), np.asarray(b, dtype=np.float64)
    den = np.maximum(np.abs(a), np.abs(b))
    return float(np.max(np.where(den > 0, np.abs(a - b) / np.where(den > 0, den, 1.0), 0.0),
                        initial=0.0))


def _nucleus(Zt, At, Z, A, hill_wheeler=False):
    from physics.hf.fission.chain import FissionChain, _Nucleus
    from physics.hf.input.defaults import default_options

    chain = FissionChain(Zt, At, default_options(Zt, At))
    n = chain.nucleus(Z, A)
    assert n is not None
    assert all(n.fp.rotational[i].n > 0 for i in range(1, int(n.fp.nfisbar) + 1)), "fists2 not on"
    if hill_wheeler:
        n = _Nucleus(fp=replace(n.fp, fismodelx=3), ld=n.ld, odd=n.odd, grids={})
        chain._nuc[(Z, A)] = n
    return chain, n


def _per_bin(chain, n, Z, A, ex, dex, exmax, top):
    from physics.hf.compound.continuum import fission_width

    ref = np.zeros((ex.size, chain.maxj + 1, 2))
    for b in range(ex.size):
        tri = chain.bin_triples(Z, A, ex[b], dex[b], exmax, top)
        mi = SimpleNamespace(flagfission=True, nfisbar=int(n.fp.nfisbar), tfis=tri,
                             exmax_mev=exmax, ex_inc_mev=float(ex[b]), dex_inc_mev=float(dex[b]))
        for j in range(chain.maxj + 1):
            for k, par in ((0, -1), (1, 1)):
                ref[b, j, k] = float(fission_width(mi, 2 * j + n.odd, par))
    return ref


@pytest.mark.parametrize("Zt,At,Z,A", CASES)
@pytest.mark.parametrize("hill_wheeler", [False, True])
def test_ladder_widths_with_band_are_the_per_bin_triples(Zt, At, Z, A, hill_wheeler):
    from physics.hf.fission import fis_ceng
    from physics.hf.fission.fission_batch_ladder import covered, ladder_bin_widths

    chain, n = _nucleus(Zt, At, Z, A, hill_wheeler)
    assert covered(n.fp, chain.o)
    fec = float(n.fp.fecont_mev[1])
    live = 0
    for top in (fec + 3.0, 13.9):  # the band alone below fecont, band + continuum above
        exmax = top + 0.3
        ex = np.linspace(0.05, top, 41)
        dex = np.full_like(ex, ex[1] - ex[0])
        ref = _per_bin(chain, n, Z, A, ex, dex, exmax, top)
        live += int((ref > 0).sum())
        got_t = ladder_bin_widths(n.fp, chain._grid(n, top), n.ld, ex, dex, exmax, chain.o,
                                  maxj=chain.maxj, fnorm=1.0)
        got_c = fis_ceng.ladder_widths(chain, n, ex, dex, exmax, top, 1.0, chain.maxj + 1)
        assert got_c is not None
        for got in (got_t, got_c):
            assert np.array_equal(got == 0.0, ref == 0.0)
            assert _rel(got, ref) < 1e-12
    assert live > 50


@pytest.mark.parametrize("Zt,At,Z,A", CASES)
@pytest.mark.parametrize("hill_wheeler", [False, True])
def test_target_transmission_with_band(Zt, At, Z, A, hill_wheeler):
    from physics.hf.fission import fis_ceng
    from physics.hf.fission.transmission import fission_transmission

    chain, n = _nucleus(Zt, At, Z, A, hill_wheeler)
    fec = float(n.fp.fecont_mev[1])
    for e in (0.6 * fec, fec + 0.017, fec + 3.0, 6.5, 13.9, 24.3):
        ft = fission_transmission(n.fp, chain._grid(n, e), n.ld, e, 0.0, chain.o, exmax_mev=e,
                                  odd=n.odd, maxj=chain.maxj, primary=True, fnorm=1.07)
        got = fis_ceng.target_transmission(chain, n, e, 1.07)
        assert got is not None
        tf, ta, ra = got
        assert _rel(ft.tfis.numpy(), tf) < 1e-12
        assert _rel(ft.tfisA.numpy(), ta) < 1e-12
        assert _rel(ft.rhofisA.numpy(), ra) < 1e-12


def test_switch_off_restores_the_refusal(monkeypatch):
    from physics.hf.fission import fis_ceng
    from physics.hf.fission.fission_batch_ladder import covered

    chain, n = _nucleus(92, 235, 92, 236)
    monkeypatch.setenv("HF_NX2_FISTSC", "0")
    assert not covered(n.fp, chain.o)
    assert fis_ceng.target_transmission(chain, n, 6.5, 1.0) is None
    assert fis_ceng.ladder_widths(chain, n, np.array([5.0]), np.array([0.2]), 6.5, 6.5, 1.0, 12) is None
