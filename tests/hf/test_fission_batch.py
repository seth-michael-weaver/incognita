"""FISSB: fissioning nuclei on the batched target and cascade paths give the per-cell/per-bin numbers.

Three pieces, none of them physics, each held to what it replaces:

* `fission.fission_batch_ladder.ladder_bin_widths` against `FissionChain.bin_triples` +
  `continuum.fission_width`, bin by bin, on the barrier grids of a real chained U-238 residual;
* `target_batch.case_nowfc` / `case_moldauer` with fission against `target._case`'s per-cell loop;
* `compound.fission_batch_decay.FissionNucleusWidths` (the fissioning nucleus on `decay_fast`) against
  the per-bin `continuum.compound_decay`;

the last two through a whole chained U-238 at energies below `ewfc` (Moldauer), in the continuum and
above `emulpre` (the tensor loop of `multiple_emission`), with the old paths restored by patching
the three hooks back. The whole-chart check is `scripts/hf_macspeed_chart.py close` (hf-fissb.md).
"""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest
import torch

TALYS_DIR = Path(__import__("os").environ.get("TALYS_DIR", Path.home() / "opt/talys-src"))
needs_structure = pytest.mark.skipif(not (TALYS_DIR / "structure").is_dir(),
                                     reason="TALYS structure/ not installed")


def _rel(a, b) -> float:
    a, b = np.asarray(a, dtype=np.float64), np.asarray(b, dtype=np.float64)
    den = np.maximum(np.abs(a), np.abs(b))
    return float(np.max(np.where(den > 0, np.abs(a - b) / np.where(den > 0, den, 1.0), 0.0),
                        initial=0.0))


@needs_structure
@pytest.mark.parametrize("Z,A", [(92, 239), (92, 238), (92, 237)])
def test_ladder_widths_are_the_per_bin_triples(Z, A):
    from physics.hf.compound.continuum import fission_width
    from physics.hf.fission.chain import FissionChain
    from physics.hf.fission.fission_batch_ladder import covered, ladder_bin_widths
    from physics.hf.input.defaults import default_options

    torch.set_num_threads(1)
    chain = FissionChain(92, 238, default_options(92, 238))
    n = chain.nucleus(Z, A)
    assert n is not None and covered(n.fp, chain.o)
    exmax, top = 14.2, 13.9
    ex = np.linspace(0.05, top, 57)
    dex = np.full_like(ex, ex[1] - ex[0])
    got = ladder_bin_widths(n.fp, chain._grid(n, top), n.ld, ex, dex, exmax, chain.o,
                            maxj=chain.maxj, fnorm=1.0)
    ref = np.zeros_like(got)
    odd = A % 2
    for b in range(ex.size):
        tri = chain.bin_triples(Z, A, ex[b], dex[b], exmax, top)
        mi = SimpleNamespace(flagfission=True, nfisbar=int(n.fp.nfisbar), tfis=tri,
                             exmax_mev=exmax, ex_inc_mev=float(ex[b]), dex_inc_mev=float(dex[b]))
        for j in range(chain.maxj + 1):
            for k, par in ((0, -1), (1, 1)):
                ref[b, j, k] = float(fission_width(mi, 2 * j + odd, par))
    assert (ref > 0).sum() > 100
    assert np.array_equal(got == 0.0, ref == 0.0)
    assert _rel(got, ref) < 1e-12


def _legacy(monkeypatch):
    """Put `target._case`'s loop and the per-bin cascade back for fissioning nuclei."""
    import physics.hf.compound.target_batch as tb
    from physics.hf.compound.fission_batch_decay import FissionLadder

    for name in ("case_nowfc", "case_moldauer"):
        fn = getattr(tb, name)

        def wrapped(inp, *a, _fn=fn, **k):
            return None if (inp.flagfission and inp.nfisbar != 0) else _fn(inp, *a, **k)

        monkeypatch.setattr(tb, name, wrapped)
    monkeypatch.setattr(FissionLadder, "covered", lambda self: False)


@needs_structure
def test_chained_u238_is_the_per_cell_and_per_bin_paths(monkeypatch, request):
    from physics.hf.chartrun import run_nuclide
    from physics.hf.compound import fission_batch_decay as fbd
    from physics.hf.compound import target_batch as tb

    torch.set_num_threads(1)
    energies = (0.8, 9.0, 24.0)
    calls = {"nw": 0, "mold": 0, "nowfc": 0}
    init = fbd.FissionNucleusWidths.__init__
    mold, nowfc = tb.case_moldauer, tb.case_nowfc

    def init2(self, *a, **k):
        calls["nw"] += 1
        return init(self, *a, **k)

    def count(key, fn):
        def inner(inp, *a, **k):
            out = fn(inp, *a, **k)
            if inp.flagfission and inp.nfisbar != 0 and out is not None:
                calls[key] += 1
            return out
        return inner

    from physics.hf.native import nativex

    # NATIVEX: this counts FISSB's numpy path; the compiled kernels are held to it by
    # tests/hf/test_nativex.py
    monkeypatch.setenv("HF_NATIVEX", "0")
    nativex.lib.cache_clear()
    request.addfinalizer(nativex.lib.cache_clear)
    with monkeypatch.context() as m:
        m.setattr(fbd.FissionNucleusWidths, "__init__", init2)
        m.setattr(tb, "case_moldauer", count("mold", mold))
        m.setattr(tb, "case_nowfc", count("nowfc", nowfc))
        new = run_nuclide(92, 238, energies)
    assert calls["nw"] > 10 and calls["mold"] >= 1 and calls["nowfc"] >= 1
    with monkeypatch.context() as m:
        _legacy(m)
        old = run_nuclide(92, 238, energies)
    assert list(new.e_inc_mev) == list(old.e_inc_mev)
    fis = np.asarray(new.totals_mb["fission"], dtype=np.float64)
    assert (fis > 1.0).all()
    for got, ref in ((new.channels_mb, old.channels_mb), (new.totals_mb, old.totals_mb),
                     (new.levels_mb, old.levels_mb),
                     (new.residual_production_mb, old.residual_production_mb)):
        assert set(got) == set(ref)
        for key, v in ref.items():
            assert _rel(got[key], v) < 1e-10, key
