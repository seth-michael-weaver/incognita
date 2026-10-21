"""ROTEXIT1CN: `sfexit` switch resolution (deck keyword > env INCOGNITA_SFEXIT > default OFF) and its SLFIRST precondition."""
import pytest

from physics.hf.omp import sfunc


class _Opt:
    def __init__(self, v=None):
        self.sfexit = v if v is not None else ""
        self._exp = v is not None

    def is_explicit(self, k):
        return self._exp and k == "sfexit"


def test_exit_mode_resolution(monkeypatch):
    monkeypatch.delenv("INCOGNITA_SFEXIT", raising=False)
    assert sfunc.exit_mode() == sfunc.EXIT_DEFAULT
    monkeypatch.setenv("INCOGNITA_SFEXIT", "cont")
    assert sfunc.exit_mode() == "cont"
    assert sfunc.exit_mode(_Opt("0")) == ""  # explicit deck keyword wins
    monkeypatch.setenv("INCOGNITA_SFEXIT", "n")
    assert sfunc.exit_mode(_Opt("cont")) == "cont"
    monkeypatch.setenv("INCOGNITA_SFEXIT", "bogus")
    with pytest.raises(ValueError):
        sfunc.exit_mode()


def test_exit_cont_needs_slfirst(monkeypatch):
    monkeypatch.setenv("INCOGNITA_SFEXIT", "cont")
    monkeypatch.delenv("INCOGNITA_SFUNC", raising=False)
    assert not sfunc.exit_cont()
    monkeypatch.setenv("INCOGNITA_SFUNC", "u1")
    monkeypatch.setenv("INCOGNITA_SFUNC_SCOPE", "all")
    assert not sfunc.exit_cont()
    monkeypatch.setenv("INCOGNITA_SFUNC_SCOPE", "first")
    assert sfunc.exit_cont()
    assert not sfunc.exit_cont(_Opt("0"))


def test_exit_contr_colltype_r_only(monkeypatch):
    """ROTEXIT1CN2: `contr` = `cont` for a colltype R target (Gd-158, U-238), OFF for S/V targets (Ni-58, As-75, Se-80, Mo-100)."""
    from physics.hf.input.defaults import Options

    monkeypatch.setenv("INCOGNITA_SFUNC", "u1")
    monkeypatch.setenv("INCOGNITA_SFUNC_SCOPE", "first")
    monkeypatch.setenv("INCOGNITA_SFEXIT", "contR")
    assert sfunc.exit_mode() == "contr"
    for Z, A, on in ((64, 158, True), (92, 238, True), (28, 58, False), (33, 75, False), (34, 80, False), (42, 100, False)):
        assert sfunc.exit_cont(Options(Z, A, 1), Z, A) is on
    with pytest.raises(ValueError):
        sfunc.exit_cont()


def test_exit_ccf_mode_and_ratio(monkeypatch):
    """ROTEXIT1CN3: `ccf` resolves, needs SLFIRST, is not `cont`; cc_ratio = max(1, inc/inv), 1 when undefined."""
    monkeypatch.setenv("INCOGNITA_SFUNC", "u1")
    monkeypatch.setenv("INCOGNITA_SFUNC_SCOPE", "first")
    monkeypatch.setenv("INCOGNITA_SFEXIT", "ccf")
    assert sfunc.exit_mode() == "ccf" and sfunc.exit_ccf() and not sfunc.exit_cont()
    monkeypatch.setenv("INCOGNITA_SFUNC_SCOPE", "all")
    assert not sfunc.exit_ccf()
    assert sfunc.cc_ratio({1: 6.0e-4}, {1: 2.0e-4}) == {1: pytest.approx(3.0)}
    assert sfunc.cc_ratio({1: 1.0e-4}, {1: 2.0e-4}) == {1: 1.0}
    assert sfunc.cc_ratio({1: 1.0e-4}, {1: float("nan")}) == {1: 1.0}
    assert sfunc.cc_ratio({1: 1.0e-4}, {}) == {1: 1.0}
