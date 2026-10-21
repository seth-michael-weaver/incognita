"""FLUXCLOSE parts A + C (FLUXPROMO / FLUXPROMO2): keyword/env switch, the residual window it sets (nuclides.f90:140-141),
the run-scoped on() (KEVLEAK3 pe2 reads on("C")) and part C's placement of PE + GR flux of an exit with no continuum bin."""
from dataclasses import dataclass, field
from types import SimpleNamespace

import pytest
import torch

from physics.hf.emission import fluxclose as F
from physics.hf.input.defaults import default_options


@pytest.fixture(autouse=True)
def _restore_eff(monkeypatch):  # F.sync writes os.environ directly: register the variable so teardown restores it (unset)
    monkeypatch.setenv("INCOGNITA_FLUXCLOSE_EFF", "")
    monkeypatch.delenv("INCOGNITA_FLUXCLOSE_EFF")


def test_window_switch(monkeypatch):
    monkeypatch.delenv("INCOGNITA_FLUXCLOSE", raising=False)
    assert F.window_on(True) and not F.window_on(False)
    assert F.parts(True) == {"A", "C"} and F.parts(False) == frozenset()
    assert F.parts() == {"A", "C", "N"} and F.parts("cn") == {"A", "C", "N"}  # FLUXCN default
    assert F.parts("y") == {"A", "C"} and F.parts("n") == frozenset() and F.parts("A,C,N") == {"A", "C", "N"}
    assert F.parts(F.canon(F.parts("cn"))) == {"A", "C", "N"} and F.canon(frozenset()) == "0"
    monkeypatch.setenv("INCOGNITA_FLUXCLOSE", "cn")
    assert F.parts(False) == {"A", "C", "N"}
    for v in ("0", "n", "off"):
        monkeypatch.setenv("INCOGNITA_FLUXCLOSE", v)
        assert not F.window_on(True) and F.parts(True) == frozenset()
    for v in ("1", "all", "y"):
        monkeypatch.setenv("INCOGNITA_FLUXCLOSE", v)
        assert F.parts(False) == {"A", "C"}
    monkeypatch.setenv("INCOGNITA_FLUXCLOSE", "a")  # the FLUXPROMO candidate: window only
    assert F.parts(False) == {"A"}
    monkeypatch.setenv("INCOGNITA_FLUXCLOSE", "C")
    assert F.parts(True) == {"C"} and not F.window_on(True)
    monkeypatch.setenv("INCOGNITA_FLUXCLOSE", "A,B")  # part B is not in this engine: an error, not a no-op
    with pytest.raises(ValueError):
        F.window_on(True)


def test_window(monkeypatch):
    monkeypatch.delenv("INCOGNITA_FLUXCLOSE", raising=False)
    o = default_options(4, 9, "n")  # Be-10*: Zinit 4, Ninit 6
    assert (o.maxZ, o.maxN, o.fluxclose) == (3, 5, "A,C,N")
    o = default_options(4, 9, "n", {"fluxclose": "y"})
    assert (o.maxZ, o.maxN, o.fluxclose) == (3, 5, "A,C")
    o = default_options(4, 9, "n", {"fluxclose": "n"})
    assert (o.maxZ, o.maxN, o.fluxclose) == (1, 3, "0")
    monkeypatch.setenv("INCOGNITA_FLUXCLOSE", "0")
    assert (default_options(4, 9, "n").maxZ, default_options(26, 56, "n").maxN) == (1, 28)
    monkeypatch.delenv("INCOGNITA_FLUXCLOSE")
    assert default_options(26, 56, "n").maxN == 30  # Ninit 31: widened, nothing reachable past Ncomp 28
    o = default_options(92, 238, "n")
    assert (o.maxZ, o.maxN) == (12, 32)  # numZ-2 / numN-2 bind for heavies: unchanged


def test_on_is_run_scoped(monkeypatch):
    monkeypatch.delenv("INCOGNITA_FLUXCLOSE", raising=False)
    monkeypatch.delenv("INCOGNITA_FLUXCLOSE_EFF", raising=False)
    assert F.on("A") and F.on("C") and F.on("N") and not F.on("B")  # nothing synced: the default (keyword cn)
    default_options(4, 9, "n", {"fluxclose": "n"})  # the deck keyword reaches the option-less sites
    assert not F.on("A") and not F.on("C") and not F.on("N")
    default_options(4, 9, "n", {"fluxclose": "y"})
    assert F.on("A") and F.on("C") and not F.on("N")
    F.sync(SimpleNamespace(fluxclose=True))
    assert F.on("A") and F.on("C")
    monkeypatch.setenv("INCOGNITA_FLUXCLOSE", "A")
    F.sync(SimpleNamespace(fluxclose=True))
    assert F.on("A") and not F.on("C")
    monkeypatch.setenv("INCOGNITA_FLUXCLOSE", "C")
    F.sync(SimpleNamespace(fluxclose=False))
    assert F.on("C") and not F.on("A")


@dataclass
class _B2:
    grids: dict
    xsdirdisc_mb: dict
    xspreeqtot_mb: dict
    xsgrtot_mb: dict
    preeqpopex_mb: dict
    flagpreeq: bool = True
    k0: int = 1
    ltarget: int = 0
    extra: dict = field(default_factory=dict)


def test_place_unplaced():
    g = SimpleNamespace(maxex=3, nlast=3)  # no continuum bin: every bin is a discrete level
    gc = SimpleNamespace(maxex=5, nlast=3)  # a continuum with PE in it: left alone
    dd = {1: torch.zeros(4, dtype=torch.float64), 6: torch.zeros(1, dtype=torch.float64),
          2: torch.zeros(6, dtype=torch.float64)}
    b2 = _B2(grids={1: g, 6: SimpleNamespace(maxex=0, nlast=0), 2: gc}, xsdirdisc_mb=dd,
             xspreeqtot_mb={1: 3.0, 6: 2.0, 2: 1.0}, xsgrtot_mb={1: 1.5},
             preeqpopex_mb={1: torch.zeros(4), 2: torch.tensor([0, 0, 0, 0, 0.4, 0.6])})
    out, moved = F.place_unplaced(b2)
    assert moved == {1: 4.5, 6: 2.0}
    assert out.xsdirdisc_mb[1].tolist() == [0.0, 1.5, 1.5, 1.5]  # levels 1..NL, target g.s. excluded
    assert out.xsdirdisc_mb[6].tolist() == [2.0]  # an outgoing exit with no excited level: the ground state
    assert out.xsdirdisc_mb[2] is dd[2]
