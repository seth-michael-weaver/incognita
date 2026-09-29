"""NATIVEX2 lever `fis2`: the continuum fission transmission through one barrier in C
(`fission/fis2_nx2.py`, `native/nx2_fis2.c`) against the torch paths it replaces, `HF_NX2_FIS2=0`
against `=1` (closeness, not bits). Skipped without a `libnx2` build or TALYS's structure data.
"""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import numpy as np
import pytest
import torch

from physics.hf.native import nx2

TALYS_DIR = Path(__import__("os").environ.get("TALYS_DIR", Path.home() / "opt/talys-src"))
pytestmark = [
    pytest.mark.skipif(nx2.lib() is None, reason="no libnx2 build"),
    pytest.mark.skipif(not (TALYS_DIR / "structure").is_dir(), reason="no TALYS structure/"),
]

# (target, residual) pairs: two- and three-humped barriers, even and odd A
CASES = [(92, 238, 92, 239), (92, 238, 92, 238), (92, 238, 92, 237), (90, 232, 90, 233),
         (94, 239, 94, 240)]


@pytest.fixture(autouse=True)
def _one_thread():
    prev = torch.get_num_threads()
    torch.set_num_threads(1)
    yield
    torch.set_num_threads(prev)


def _close(a, b, rel=1e-12, tiny=1e-300):
    a, b = np.asarray(a, float), np.asarray(b, float)
    assert a.shape == b.shape
    scale = np.maximum(np.abs(a), np.abs(b))
    bad = np.abs(a - b) > rel * scale + tiny
    assert not bad.any(), (np.argwhere(bad)[:5], a[bad][:5], b[bad][:5])


def _arms(monkeypatch, fn):
    out = []
    for arm in ("0", "1"):
        monkeypatch.setenv("HF_NX2_FIS2", arm)
        out.append(fn())
    return out


def _nucleus(Zt, At, Z, A):
    from physics.hf.fission.chain import FissionChain
    from physics.hf.input.defaults import default_options

    chain = FissionChain(Zt, At, default_options(Zt, At))
    n = chain.nucleus(Z, A)
    if n is None:
        pytest.skip("does not fission")
    return chain, n


def _energies(n):
    lo = float(n.fp.fecont_mev[1:int(n.fp.nfisbar) + 1].min())
    # below every fecont, on fecont, inside the grid, on and past its top
    return [0.0, lo - 0.3, lo, lo + 0.017, 2.5, 5.1, 7.77, 11.0, 13.9, 14.2, 25.0]


@pytest.mark.parametrize("Zt,At,Z,A", CASES)
@pytest.mark.parametrize("hill_wheeler", [False, True])
def test_t1barrier_matches_the_torch_loop(monkeypatch, Zt, At, Z, A, hill_wheeler):
    from physics.hf.fission.barriers import t1barrier

    chain, n = _nucleus(Zt, At, Z, A)
    fp = replace(n.fp, fismodelx=3) if hill_wheeler else n.fp
    for top in (6.0, 13.9):
        grid = chain._grid(n, top)
        for ibar in range(1, int(fp.nfisbar) + 1):
            for e in _energies(n):
                for collect in (False, True):
                    a, b = _arms(monkeypatch, lambda: t1barrier(
                        fp, grid, ibar, torch.tensor(e, dtype=torch.float64), n.ld.deltaW_mev,
                        odd=n.odd, maxj=chain.maxj, collect_hill=collect))
                    _close(a.trfis.numpy(), b.trfis.numpy())
                    _close(a.rhof.numpy(), b.rhof.numpy())
                    if collect:
                        _close(a.tfisA.numpy(), b.tfisA.numpy())
                        _close(a.rhofisA.numpy(), b.rhofisA.numpy())


@pytest.mark.parametrize("Zt,At,Z,A", CASES)
def test_ladder_transmission_matches_the_torch_matrix(monkeypatch, Zt, At, Z, A):
    from physics.hf.fission.fission_batch_ladder import covered, ladder_transmission

    chain, n = _nucleus(Zt, At, Z, A)
    if not covered(n.fp, chain.o):
        pytest.skip("not on the ladder path")
    grid = chain._grid(n, 13.9)
    e = np.array(_energies(n) + list(np.linspace(0.05, 14.2, 60)))
    a, b = _arms(monkeypatch, lambda: ladder_transmission(n.fp, grid, n.ld, e, chain.o,
                                                         maxj=chain.maxj))
    _close(a.numpy(), b.numpy())


@pytest.mark.parametrize("Zt,At,Z,A", CASES[:2])
def test_fission_transmission_and_compound_target(monkeypatch, Zt, At, Z, A):
    chain, n = _nucleus(Zt, At, Z, A)
    for ex in (4.0, 6.2, 11.3):
        a, b = _arms(monkeypatch, lambda: chain.transmission(Z, A, ex, 0.4, 13.0, exmax_mev=13.0))
        for f in ("tfis", "tfisdown", "tfisup", "denfis_per_mev", "gamfis_mev"):
            _close(getattr(a, f).numpy(), getattr(b, f).numpy())
        a, b = _arms(monkeypatch, lambda: chain.compound_target(Z, A, ex))
        assert a["tfis"].keys() == b["tfis"].keys()
        for k in a["tfis"]:
            _close(a["tfis"][k], b["tfis"][k])
            _close(a["tfisA"][k], b["tfisA"][k])
            _close(a["rhofisA"][k], b["rhofisA"][k])


@pytest.mark.parametrize("Zt,At,Z,A", CASES)
def test_fission_level_densities_match_the_torch_grid(monkeypatch, Zt, At, Z, A):
    from physics.hf.fission.transmission import fission_level_densities

    chain, n = _nucleus(Zt, At, Z, A)
    lo = float(n.fp.fecont_mev[1:int(n.fp.nfisbar) + 1].min())
    for top in (lo - 0.5, lo + 0.004, lo + 0.3, 6.0, 13.9, 30.0):
        a, b = _arms(monkeypatch, lambda: fission_level_densities(n.fp, n.ld, top, odd=n.odd,
                                                                  maxj=chain.maxj))
        assert a.nbintfis == b.nbintfis
        assert a.eintfis_mev.shape == b.eintfis_mev.shape
        assert torch.equal(a.eintfis_mev, b.eintfis_mev)
        _close(a.rhofis.numpy(), b.rhofis.numpy())
