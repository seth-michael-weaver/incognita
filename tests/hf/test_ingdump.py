"""INGDUMP: `INCOGNITA_INGDUMP=1` adds level-density tables and photon-strength curves to the
`ing_*` keys and changes nothing else.

The flag is output only: `ingredients` computes every existing key first and appends the INGDUMP
block last, read off the same `Cascade`. These tests check (1) OFF is the default and adds no key,
(2) ON leaves every existing key bitwise identical, (3) the tables are the engine's own functions
(`density`, `densitytotP`, `fstrength_gp`) on the stated grids, (4) the block fits the 2 MB budget.
The whole-run identity (channels, levels, residuals; SP2SET18 + G113, flag ON vs OFF vs the
production engine) is checked in development notes.
"""

from __future__ import annotations

import io
import json

import numpy as np
import pytest
import torch

from physics.hf.emission.feeding import Cascade
from physics.hf.ingredients import ENV_INGDUMP, INGDUMP_NUCLEI, ingdump, ingdump_enabled, ingredients


def _same(a, b) -> bool:
    if isinstance(a, np.ndarray) or isinstance(b, np.ndarray):
        a, b = np.asarray(a), np.asarray(b)
        return a.dtype == b.dtype and a.shape == b.shape and a.tobytes() == b.tobytes()
    if isinstance(a, float) and isinstance(b, float) and np.isnan(a) and np.isnan(b):
        return True
    return type(a) is type(b) and a == b


@pytest.fixture(scope="module")
def fe56_pair():
    mp = pytest.MonkeyPatch()
    try:
        cas = Cascade(26, 56, 0.001, energies=(0.001,))
        with torch.inference_mode():
            mp.delenv(ENV_INGDUMP, raising=False)
            off = ingredients(cas)
            mp.setenv(ENV_INGDUMP, "1")
            on = ingredients(cas)
            mp.setenv(ENV_INGDUMP, "0")
            off2 = ingredients(cas)
        return cas, off, on, off2
    finally:
        mp.undo()


def test_default_is_off(monkeypatch):
    monkeypatch.delenv(ENV_INGDUMP, raising=False)
    assert not ingdump_enabled()
    for v in ("0", "", "n", "no"):
        monkeypatch.setenv(ENV_INGDUMP, v)
        assert not ingdump_enabled()
    for v in ("1", "y", "yes"):
        monkeypatch.setenv(ENV_INGDUMP, v)
        assert ingdump_enabled()


def test_off_adds_nothing(fe56_pair):
    _, off, _, off2 = fe56_pair
    assert not any(k.startswith(("ing_ldtab_", "ing_psfc_", "ing_ingdump")) for k in off)
    assert list(off) == list(off2)
    assert all(_same(off[k], off2[k]) for k in off)


def test_on_is_output_only(fe56_pair):
    """every key the OFF run writes is in the ON run, bitwise, in the same order"""
    _, off, on, _ = fe56_pair
    assert list(on)[: len(off)] == list(off)
    bad = [k for k in off if not _same(off[k], on[k])]
    assert not bad, bad


def test_on_keys_and_budget(fe56_pair):
    _, off, on, _ = fe56_pair
    new = {k: v for k, v in on.items() if k not in off}
    meta = json.loads(new["ing_ingdump_json"])
    assert "error" not in meta
    for tag, _, _ in INGDUMP_NUCLEI:
        rec = meta["nuclei"][tag]
        assert "error" not in rec, (tag, rec)
        for k in ("ex_mev", "j", "rho_j", "rho_tot", "rho_obs", "ncum", "t_mev", "sig2", "sig2_eff", "lev"):
            assert f"ing_ldtab_{tag}_{k}" in new, (tag, k)
        for k in ("e1", "m1", "e2", "e1_ex"):
            assert f"ing_psfc_{tag}_{k}" in new, (tag, k)
        ex = new[f"ing_ldtab_{tag}_ex_mev"]
        assert ex[-2] <= rec["sn_mev"] + 5.0 < ex[-1]  # up to S_n + 5 MeV plus one node
        assert new[f"ing_ldtab_{tag}_rho_j"].shape == (2, ex.size, new[f"ing_ldtab_{tag}_j"].size)
    assert (meta["nuclei"]["cn"]["Z"], meta["nuclei"]["cn"]["A"]) == (26, 57)
    assert (meta["nuclei"]["n"]["Z"], meta["nuclei"]["n"]["A"]) == (26, 56)
    buf = io.BytesIO()
    np.savez_compressed(buf, **new)
    assert len(buf.getvalue()) < 2_000_000
    buf.seek(0)
    with np.load(buf, allow_pickle=False) as z:  # str / ndarray only
        assert set(z.files) == set(new)


def test_tables_are_the_engine_functions(fe56_pair):
    from physics.hf.density.models import density, densitytotP
    from physics.hf.gamma.strength import fstrength_gp

    cas, _, on, _ = fe56_pair
    ld = cas.ld_of(26, 57)[0]
    ex = torch.as_tensor(on["ing_ldtab_cn_ex_mev"], dtype=torch.float64)
    J = torch.as_tensor(on["ing_ldtab_cn_j"], dtype=torch.float64)
    for k, par in enumerate((-1, 1)):
        ref = density(ld, ex.unsqueeze(-1), J.unsqueeze(0), par, 0).numpy().astype(np.float32)
        assert np.array_equal(on["ing_ldtab_cn_rho_j"][k], ref)
        tot = densitytotP(ld, ex, par, 0).numpy().astype(np.float32)
        assert np.array_equal(on["ing_ldtab_cn_rho_obs"][k], tot)
    gp = cas.gamma_params(26, 56)
    eg = torch.as_tensor(on["ing_psfc_eg_mev"], dtype=torch.float64)
    for key, irad, l in (("e1", 1, 1), ("m1", 0, 1), ("e2", 1, 2)):  # noqa: E741
        ref = fstrength_gp(gp, 0.0, eg, irad, l).numpy()
        got = on[f"ing_psfc_cn_{key}"].astype(np.float64)
        np.testing.assert_allclose(got, ref, rtol=1e-6, atol=0.0)


def test_never_raises():
    class Broken:
        def zn(self, zix, nix):
            raise RuntimeError("boom")

    d = ingdump(Broken())
    meta = json.loads(d["ingdump_json"])
    assert all("error" in r for r in meta["nuclei"].values())
