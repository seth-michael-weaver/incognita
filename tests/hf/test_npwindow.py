"""NPWINDOW / NPWPROMO: windowed target-rho rule on D0-unanchored targets (physics/hf/density/npwindow.py)."""

import hashlib
from types import SimpleNamespace

import pytest

from physics.hf import eadj
from physics.hf.density import npwindow as N


@pytest.fixture(autouse=True)
def _clean(monkeypatch):
    monkeypatch.delenv(N.ENV, raising=False)
    monkeypatch.setenv(N.EFF, "0")   # registered, so the run state this module writes is undone afterwards
    monkeypatch.delenv(N.EFF)
    yield


def test_class_flag_is_input_availability():
    # As-75: no measured D0 of As-75 itself (As-74 + n not in the table) -> class U; As-76 (As-75 + n) anchored
    assert N.in_class(33, 75) and not N.in_class(33, 76)
    assert len(N.anchored()) == 374


def test_no_run_state_is_production():
    assert N.target() is None and not N.applies_run() and N.token() == ()
    assert not eadj.on() and eadj.ld_native_ok() and eadj.token() == ()
    assert N.bumps(SimpleNamespace(Z=33, A=75)) == ()


def test_switch_env_and_keyword(monkeypatch):
    assert N.flag("y") and not N.flag("n") and N.flag(True) and not N.flag(False)
    monkeypatch.setenv(N.ENV, "0")
    assert not N.flag("y")
    monkeypatch.setenv(N.ENV, "1")
    assert N.flag("n")
    with pytest.raises(ValueError):
        N._yn("maybe", "x")


def test_state_neutron_unanchored_only(monkeypatch):
    monkeypatch.setenv(N.ENV, "1")
    N.begin(33, 75, 1)
    assert N.target() == (33, 75) and eadj.on() and not eadj.ld_native_ok()
    assert eadj.token()[-1] == ("npwindow", "MX1", 33, 75)
    N.sync(SimpleNamespace(npwindow="y", Ztarget=33, Atarget=75, k0=1))
    N.begin(33, 76, 1)   # anchored target: off
    assert N.target() is None
    N.begin(33, 75, 2)   # proton-induced: off
    assert N.target() is None
    with pytest.raises(RuntimeError):
        N.sync(SimpleNamespace(npwindow="y", Ztarget=33, Atarget=75, k0=1))


def test_lines_reproduce_npwindow_record():
    # the NPWINDOW record's MX/033_075.eadj (development notes; dc = target_dctable.csv, Ecut/S_n = INGDUMP chart P)
    txt = "".join(x + "\n" for x in N.lines(33, 75, 0.2079, 1.420199990272522, 10.245456337641983))
    assert len(txt.splitlines()) == 116
    assert hashlib.sha256(txt.encode()).hexdigest() == "89cf37dcca02bdbf0d16cfc099c6c31ea1c37c1f6ddcd3101cf152653fb57c4d"


def test_bumps_only_on_the_target_ground_state(monkeypatch):
    import torch

    monkeypatch.setenv(N.ENV, "1")
    N.begin(33, 75, 1)
    ld = SimpleNamespace(Z=33, A=75, Nlast=(30,), edis_mev=torch.tensor([0.0] * 30 + [1.420199990272522]),
                         S_mev=torch.tensor(10.245456337641983), ctable=torch.tensor([-0.2402]),
                         deltaW_mev=torch.tensor([0.0]), beta2=torch.tensor([0.0]))
    b = N.bumps(ld)
    assert len(b) > 0 and all(x.target == "ctable" and x.sel == (33, 75) for x in b)
    assert N.bumps(ld, ibar=1) == ()
    assert N.bumps(SimpleNamespace(Z=33, A=74)) == ()
    s = eadj.bump_shift(b, [1.0, 2.0, 12.0])
    assert s[0] == 0.0 and abs(s[2] * 12.0 ** 0.5 - N.dc_rule(33, 75, -0.2402, 0.0, 0.0) * 10.245456337641983 ** 0.5) < 0.05
