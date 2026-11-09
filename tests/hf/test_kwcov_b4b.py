"""KWCOV B4b: exclusive channel spectra sp<nnnnnn>.tot / .fis and `components y` (docs/hf/COVERAGE_PLAN.md, B4b).

physics/hf/exclspec.py walks channels.f90's exclusive-channel loop again with `specexcl` (binemis, the first term and
specemission.f90's smearing); physics/hf/compoobs.py gives multiple.f90's Fdir / Fpreeq / Fcomp split (xs*.tot
columns 5-7, rp*.tot columns 3-5). Stock TALYS-2.25 references: ~/kwcov/stock/b4b (scripts/kwcov/b4b_stock.sh); the
full comparison is scripts/kwcov/b4b_compare.py. The engine test runs n + Fe-56 at 14 MeV in TALYS mode
(scripts/kwcov/fidelity.py TALYS_DECK / TALYS_ENV) and pins stock's numbers.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import numpy as np
import pytest

from physics.hf import compoobs, exclspec
from physics.hf.input import defaults as D
from physics.hf.input import fitlib as F

ROOT = Path(__file__).resolve().parents[2]

# stock TALYS-2.25 n + Fe-56 14 MeV (outspectra y, channels y, components y): integral of each sp*.tot column with the
# weights np.gradient(E-out) (the same weights on both sides), mb
SP_FE56_14 = {("sp100000.tot", "n"): 6.676025e+02, ("sp100000.tot", "g"): 1.026861e+03,
              ("sp200000.tot", "n"): 9.557225e+02, ("sp010000.tot", "p"): 1.174536e+02,
              ("sp010000.tot", "g"): 1.686218e+02, ("sp000001.tot", "a"): 2.717244e+01,
              ("sp110000.tot", "n"): 4.840774e+01, ("sp110000.tot", "p"): 4.890748e+01,
              ("sp000000.tot", "g"): 1.662563e+00}
# xs*.tot columns 5-7 / rp*.tot columns 3-5 (Direct, Preequilibrium, Compound), mb
COMP_FE56_14 = {"xs100000.tot": (5.993262e+01, 2.281575e+02, 5.744858e+02),
                "xs010000.tot": (3.202283e+00, 2.264799e+01, 1.053694e+02),
                "xs200000.tot": (0.0, 0.0, 4.808369e+02),
                "rp025056.tot": (3.202575e+00, 2.265006e+01, 1.053790e+02),
                "rp026056.tot": (5.998466e+01, 2.283556e+02, 5.749846e+02),
                "rp026055.tot": (0.0, 0.0, 4.808383e+02)}


@pytest.fixture
def clean(monkeypatch):
    from physics.hf import chartrun

    for k in [k for k in os.environ if k.startswith("INCOGNITA_")]:
        monkeypatch.delenv(k, raising=False)
    F.deactivate(); F._cards.cache_clear(); chartrun.drop_target_caches()
    yield monkeypatch
    for k in [k for k in os.environ if k.startswith("INCOGNITA_")]:
        monkeypatch.delenv(k, raising=False)
    F.deactivate(); F._cards.cache_clear(); chartrun.drop_target_caches()


def _opts(**kw):
    return D.default_options(26, 56, "n", overrides=kw)


# ------------------------------------------------------------------------------------------------ switches
def test_switches():
    assert not exclspec.wanted_for(_opts())
    assert not exclspec.wanted_for(_opts(outspectra="y"))  # channels.f90 is where specexcl lives
    assert not exclspec.wanted_for(_opts(channels="y"))
    assert exclspec.wanted_for(_opts(outspectra="y", channels="y"))
    assert exclspec.wanted_for(_opts(ddxmode="1", channels="y"))  # ddxmode > 0 implies outspectra
    assert exclspec.wanted_for(_opts(endf="y"))  # endf y: outspectra and (endfdetail y) channels
    D.reject_unported(_opts(components="y"))  # B4b: no longer refused
    assert _opts(components="y").flagcompo and not _opts().flagcompo


def test_reaction_strings():
    assert exclspec._reaction(100000, 1, False) == "(n,n')"
    assert exclspec._reaction(200000, 1, False) == "(n,2n)"
    assert exclspec._reaction(0, 1, False) == "(n,g)"
    assert exclspec._reaction(110000, 1, True) == "(n,npf)"
    assert exclspec._reaction(10000, 2, False) == "(p,p')"
    assert exclspec._reaction(1, 1, False) == "(n,a)"


def test_specemission_conserves_the_bin_flux():
    """specemission.f90 normalises its weights: the spectrum integrates (deltaE) to xso00 = feedexcl x feed0."""
    eg = np.arange(0.05, 10.0, 0.1)
    de = np.full(eg.size, 0.1)
    cur = dict(egrid=eg, ebottom=eg - 0.05, etop=eg + 0.05, deltae=de, ebegin={t: 1 for t in range(7)},
               eend={t: eg.size - 1 for t in range(7)}, speceps=1e-12)
    g = exclspec._Grid(cur)
    ex = np.zeros(13); dex = np.zeros(13)
    ex[:11] = np.arange(11) * 0.5 + 0.25; dex[:11] = 0.5
    nuc_grid = {(0, 0): (ex, dex, 0, 10), (0, 1): (ex, dex, 0, 10)}
    geo = exclspec._Geom(g, nuc_grid, {(0, 0): {1: 1.0}})
    F = np.zeros((12, 11))
    F[8, 3] = 2.0; F[7, 3] = 1.0; F[9, 3] = 1.5; F[8, 2] = 0.7; F[8, 4] = 0.4
    got = exclspec._specemission(geo.of((0, 0), 1, 8, 3), F, 8, 3, 0.5, 0.4, 0.6)
    sl, v = got
    assert v.min() >= 0.0 and abs(float((v * de[sl]).sum()) - 2.0 * 0.5) < 1e-12
    # a discrete residual level (nexout <= Nlast): same normalisation
    nuc_grid[(0, 1)] = (ex, dex, 2, 10)
    geo = exclspec._Geom(g, nuc_grid, {(0, 0): {1: 1.0}})
    F2 = F.copy()
    F2[8, 1] = 0.9
    sl, v = exclspec._specemission(geo.of((0, 0), 1, 8, 1), F2, 8, 1, 0.5, 0.4, 0.6)
    assert v.min() >= 0.0 and abs(float((v * de[sl]).sum()) - 0.9 * 0.5) < 1e-12


def test_components_split_quirks():
    """multiple.f90:661-668 as TALYS writes it: preeq capped at pop - dir, comp = pop - (preeq - dir)."""
    from types import SimpleNamespace as NS

    ex = np.array([0.0, 1.0, 2.0, 3.0, 4.0, 5.0])
    nucs = {(0, 1): NS(Z=26, A=56, xspopnuc_mb=100.0, xsfeed_mb={1: 5.0, 2: 1.0}, sep_mev={1: 3.5, 2: 1.0}),
            (0, 0): NS(Z=26, A=57, xspopnuc_mb=0.0, xsfeed_mb={}, sep_mev={})}
    st = NS(spec={(0, 1): NS(ex_mev=ex, maxex=5), (0, 0): NS(ex_mev=ex, maxex=5)})
    b2 = NS(grids={1: None}, preeqpopex_mb={1: np.array([1.0, 2.0, 3.0, 4.0, 50.0, 60.0])}, xsdirdisctot_mb={1: 10.0})
    cinp = NS(nuclei=nucs, k0=2, ltarget=0)
    s = compoobs.split(cinp, st, b2, {})
    pop, d, p, c = s[(26, 56)]
    # bins 0..3 (Ex <= S_n = 3.5): 1+2+3+4 = 10; comp = 100 - (10 - 10) = 100 (TALYS adds the direct part back)
    assert (pop, d, p, c) == (100.0, 10.0, 10.0, 100.0)
    b2.preeqpopex_mb = {1: np.array([1.0, 2.0, 3.0, 400.0, 0.0, 0.0])}
    pop, d, p, c = compoobs.split(cinp, st, b2, {})[(26, 56)]
    assert p == 90.0 and c == 20.0  # capped at pop - dir


# ------------------------------------------------------------------------------------------------ engine vs stock
def _talys_mode():
    sys.path.insert(0, str(ROOT / "scripts" / "kwcov"))
    from fidelity import mode_args

    return mode_args("talys")


def _run(clean, lines: str, env: dict):
    import torch

    from physics.hf import chartrun, engine_c
    from physics.hf.engine import ChainedFull

    for k, v in env.items():
        clean.setenv(k, v)
    clean.setenv("INCOGNITA_TALYS_FIT", "lines")
    clean.setenv("INCOGNITA_TALYS_FIT_LINES", lines)
    F.deactivate(); F._cards.cache_clear(); chartrun.drop_target_caches()
    with torch.inference_mode():
        return engine_c.run(ChainedFull(Z=26, A=56, declared_energies=(14.0,)))


def test_engine_fe56_14mev_vs_stock(clean, tmp_path):
    """n + Fe-56 14 MeV, TALYS mode: every sp*.tot column TALYS writes within 0.5 % (integral) of stock, the
    components within 1 %; the spectra switches leave every other Results array bitwise unchanged; files written."""
    from physics.hf import warmrun
    from physics.hf.specobs import ENV_DIR

    deck, env = _talys_mode()
    base = _run(clean, deck, env)
    clean.setenv(ENV_DIR, str(tmp_path))
    r = _run(clean, deck + ";outspectra y;channels y;components y", env)
    sp = {k: v.numpy() for k, v in r.spectra.items()}
    for (name, x), ref in SP_FE56_14.items():
        E = sp[name + ":E"][0]
        m = np.isfinite(E)
        got = float((sp[f"{name}:{x}"][0][m] * np.gradient(E[m])).sum())
        assert abs(got / ref - 1) < 5e-3, (name, x, got, ref)
    # the channels TALYS writes and no other (stock: 9 files at 14 MeV)
    names = sorted({k.rsplit(":", 1)[0] for k in sp if k.startswith("sp") and np.isfinite(sp[k][0]).any()})
    assert names == ["sp000000.tot", "sp000001.tot", "sp000100.tot", "sp001000.tot", "sp010000.tot", "sp100000.tot",
                     "sp100001.tot", "sp110000.tot", "sp200000.tot"]
    ex = {k: float(v.numpy()[0]) for k, v in r.extras.items()}
    for stem, ref in COMP_FE56_14.items():
        for name, v in zip(compoobs.COLS, ref):  # noqa: B905
            got = ex.get(f"{stem}:{name}", 0.0)
            assert abs(got - v) <= 1e-2 * max(v, 1.0), (stem, name, got, v)
    # output only: every array of the default Results is unchanged
    a0, a1 = warmrun.result_arrays(base), warmrun.result_arrays(r)
    for k, v in a0.items():
        assert np.array_equal(np.asarray(v), np.asarray(a1[k]), equal_nan=True), k
    files = sorted(p.name for p in tmp_path.glob("sp*"))
    assert "sp200000E0014.000.tot" in files and "sp000000E0014.000.tot" in files
    txt = (tmp_path / "sp200000E0014.000.tot").read_text()
    assert "(n,2n) emission spectrum" in txt and "E-incident [MeV]" in txt
