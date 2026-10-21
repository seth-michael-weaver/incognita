"""KEVLEAK3 (`pe2`, `dup2` parts of INCOGNITA_KEVLEAK2). pe2: the projectile's sentinel PE is zeroed only where it is booked nowhere
(Elast(k0) <= 0 and level 1 closed, or FLUXCLOSE C off); where FLUXCLOSE C books it on open levels, pe2 == off bitwise.
dup2 = dup + the C engine's cascade_only (engine_decay.c); its C side is covered by the KEVLEAK3 Step 0 smoke (Sb-109 15.25 MeV
== the merged-branch oracle), the parts parsing here."""
import numpy as np
import pytest
import torch

from physics.hf.preeq import exciton as X
from tests.hf import test_kevleak2 as T2


@pytest.fixture(autouse=True)
def _no_eff(monkeypatch):  # KEVLEAK3 gate candidate: a run's kevleak2.sync value must not leak into these unit tests
    monkeypatch.delenv("INCOGNITA_KEVLEAK2_EFF", raising=False)
    monkeypatch.delenv("INCOGNITA_FLUXCLOSE_EFF", raising=False)  # FLUXPROMO2: nor a run's fluxclose.sync value (on("C"))


def _run(monkeypatch, flag, e1, fc="1"):
    monkeypatch.setenv("INCOGNITA_KEVLEAK2", flag) if flag else monkeypatch.setenv("INCOGNITA_KEVLEAK2", "0")
    monkeypatch.setenv("INCOGNITA_FLUXCLOSE", fc)
    monkeypatch.delenv("INCOGNITA_C6FIX", raising=False)
    sp, inp, disc = T2._case(-0.3)
    disc.eoutdis_mev[0][1] = np.array([0.004, e1, -0.3])  # k0: ground, level 1, last level (closed)
    return X.preeq_total(sp, inp, disc)


KEYS = ("xspreeqtot", "xssteptot", "xspreeq", "xsstep", "xsstep2", "xspreeqsum")


def _has_fluxclose() -> bool:
    import importlib.util

    return importlib.util.find_spec("physics.hf.emission.fluxclose") is not None


@pytest.mark.skipif(not _has_fluxclose(), reason="engine without FLUXCLOSE (production): see test_pe2_without_fluxclose_is_pe")
def test_pe2_booked_by_fluxclose_is_bitwise(monkeypatch):
    off, on = _run(monkeypatch, None, 0.003), _run(monkeypatch, "pe2", 0.003)
    assert float(off["xspreeqtot"][0, 1]) > 0.0
    for k in KEYS:
        assert torch.equal(off[k], on[k]), k


def test_pe2_sink_zeroes_like_pe(monkeypatch):
    for fc, e1 in (("1", -0.1), ("0", 0.003)):  # no open level above the ground state; or FLUXCLOSE C off
        pe, pe2 = _run(monkeypatch, "pe", e1, fc), _run(monkeypatch, "pe2", e1, fc)
        assert float(pe2["xspreeqtot"][0, 1]) == 0.0
        for k in KEYS:
            assert torch.equal(pe[k], pe2[k]), (fc, k)


@pytest.mark.skipif(not _has_fluxclose(), reason="engine without FLUXCLOSE")
def test_pe2_capture_neutral_is_pe(monkeypatch):
    """FLUXCN part N (`fluxclose cn`, default): with C on the sentinel is still zeroed as in production (pe2 == pe with level
    1 open), so the compound flux and the PE-photon gate are production's."""
    for fc in ("cn", "A,C,N", "C,N"):
        pe, pe2 = _run(monkeypatch, "pe", 0.003, fc), _run(monkeypatch, "pe2", 0.003, fc)
        assert float(pe2["xspreeqtot"][0, 1]) == 0.0
        for k in KEYS:
            assert torch.equal(pe[k], pe2[k]), (fc, k)


@pytest.mark.skipif(_has_fluxclose(), reason="engine with FLUXCLOSE")
def test_pe2_without_fluxclose_is_pe(monkeypatch):
    """KEVLEAK3 gate candidate on production (no FLUXCLOSE module = C off): nothing books the sentinel PE, so pe2 == pe even
    with level 1 open."""
    pe, pe2 = _run(monkeypatch, "pe", 0.003), _run(monkeypatch, "pe2", 0.003)
    assert float(pe2["xspreeqtot"][0, 1]) == 0.0
    for k in KEYS:
        assert torch.equal(pe[k], pe2[k]), k


def test_parts(monkeypatch):
    from physics.hf import kevleak2 as K
    for v, want in (("1", {"dup", "pe"}), ("y", {"dup", "pe"}), ("2", {"dup", "dup2", "pe2"}), ("dup2", {"dup", "dup2"}),
                    ("pe2", {"pe2"}), ("dup", {"dup"}), ("pe", {"pe"}), ("dup2,pe2", {"dup", "dup2", "pe2"}), ("0", set()), ("n", set()),
                    ("", {"dup", "dup2", "pe2"})):
        monkeypatch.setenv("INCOGNITA_KEVLEAK2", v)
        assert {p for p in ("dup", "dup2", "pe", "pe2") if K.on(p)} == want, v


def test_dup2_python_record(monkeypatch):
    rec, nuc = T2._gc(monkeypatch, "2")
    assert rec == {1: 5.0, 0: 5.0}


def test_resolve_deck_env_default(monkeypatch):
    """Gate candidate: explicit deck keyword `kevleak2` > env INCOGNITA_KEVLEAK2 > default 2; sync() publishes it to _EFF."""
    from physics.hf import kevleak2 as K
    from physics.hf.input.defaults import default_options
    monkeypatch.delenv("INCOGNITA_KEVLEAK2", raising=False)
    o = default_options(26, 56)
    assert o.kevleak2 == "y" and K.resolve(o) == "2"
    monkeypatch.setenv("INCOGNITA_KEVLEAK2", "pe2")
    assert K.resolve(o) == "pe2" and K.resolve(None) == "pe2"
    on_n = default_options(26, 56, overrides={"kevleak2": "n"})
    assert K.resolve(on_n) == "0"
    K.sync(on_n)
    assert not any(K.on(p) for p in ("dup", "dup2", "pe", "pe2"))
    K.sync(default_options(26, 56, overrides={"kevleak2": "y"}))
    assert K.on("dup2") and K.on("pe2") and not K.on("pe")
