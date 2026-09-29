"""PARAMWIRE (ROUTE100 WP3): a fit parameter set reaches every consumer and keeps the fast paths.

`engine.ChainedFull(params=((keyword, Z, A, value), ...))` with `aadjust`, E1 `ftable` and E1
`wtable`: the numpy / NATIVEX decay stays on (`Cascade._numpy_decay_ok`, `NativeWidths`), the
level-density and photon-strength objects of the named nuclei move and no other, and a run at a
new point on a warmed Cascade gives the cold run's numbers.
"""

from __future__ import annotations

import numpy as np
import pytest
import torch

from physics.hf.core.constants import talys_structure_path

try:
    talys_structure_path()
    _HAVE = True
except FileNotFoundError:
    _HAVE = False

needs_structure = pytest.mark.skipif(not _HAVE, reason="TALYS structure database not found")

Z, A = 26, 54
DECLARED = (1.0, 14.0)


@pytest.fixture(autouse=True)
def _one_thread():
    n = torch.get_num_threads()
    torch.set_num_threads(1)
    yield
    torch.set_num_threads(n)


def test_fit_params_canonical_and_strict():
    from physics.hf.density import overrides as ov

    fit = ov.fit_params([("FTABLE", 26, 55, 0.8), ("aadjust", 26, 54, 1.1)])
    assert fit == (("aadjust", 26, 54, 1.1), ("ftable", 26, 55, 0.8))
    assert ov.ld_token(fit, 26, 54) == 1.1 and ov.ld_token(fit, 26, 55) is None
    assert ov.gamma_token(fit, 26, 55) == (None, 0.8, None)
    assert ov.gamma_token(fit, 25, 54) is None
    with pytest.raises(KeyError):
        ov.fit_params([("pshift", 26, 54, 0.1)])
    with pytest.raises(ValueError):
        ov.fit_params([("aadjust", 26, 54, 1.1), ("aadjust", 26, 54, 1.2)])


@needs_structure
def test_with_aadjust_sets_the_named_cell_only():
    from physics.hf.compound.dens_reference import _structure_of
    from physics.hf.density.overrides import with_aadjust

    o, p, _m = _structure_of(Z, A)
    q = with_aadjust(p, o, ((Z, A + 1, 1.1), (Z, A, 0.9), (10, 20, 2.0)))  # last is off the box
    assert float(q.at("aadjust", 0, 0)) == 1.1  # compound nucleus
    assert float(q.at("aadjust", 0, 1)) == 0.9  # target
    assert float(q.at("aadjust", 1, 1)) == 1.0
    assert float(p.at("aadjust", 0, 0)) == 1.0  # the shared defaults are untouched
    assert with_aadjust(p, o, ()) is p


@needs_structure
def test_psf_and_ld_consumers_move():
    """`aadjust` reaches the level density and the photon strength's `alev` of its own nucleus --
    the compound nucleus AND a residual (the target) -- and `ftable`/`wtable` the E1 table."""
    from physics.hf.compound.dens_reference import _gamma_parameters
    from physics.hf.emission.feeding import Cascade

    cas = Cascade(Z, A, max(DECLARED), energies=DECLARED)
    gp0_cn = cas.gamma_params(Z, A)
    gp0_tg = cas.gamma_params(Z, A - 1)
    ld0_cn = cas.ld_of(Z, A + 1)[0]
    cas.set_fit_params([("aadjust", Z, A + 1, 1.1), ("aadjust", Z, A, 0.9),
                        ("ftable", Z, A + 1, 0.8), ("wtable", Z, A + 1, 1.2)])
    gp_cn, gp_tg = cas.gamma_params(Z, A), cas.gamma_params(Z, A - 1)
    assert float(gp_cn.ftable[1, 1]) == 0.8 and float(gp_cn.wtable[1, 1]) == 1.2
    assert float(gp_cn.alev_per_mev) != float(gp0_cn.alev_per_mev)
    assert float(gp_tg.alev_per_mev) != float(gp0_tg.alev_per_mev)  # residual PSF
    assert float(gp_tg.ftable[1, 1]) == float(gp0_tg.ftable[1, 1])  # ftable is the CN's only
    assert float(cas.ld_of(Z, A + 1)[0].alev) != float(ld0_cn.alev)
    # a nucleus the set does not name keeps the cached default object
    assert cas.ld_of(Z - 1, A)[0] is Cascade(Z, A, max(DECLARED), energies=DECLARED).ld_of(Z - 1, A)[0]
    assert cas.gamma_params(Z, A - 2) is _gamma_parameters(Z, A - 2)[0]
    # the strength function the torch paths call carries the same parameters, on numpy
    f = cas.gamma_strength(Z, A)
    assert f.gp is gp_cn and not f.differentiable


@needs_structure
def test_params_keep_the_fast_decay_path_and_warm_equals_cold(monkeypatch):
    from physics.hf.compound import widths_native
    from physics.hf.emission.feeding import Cascade
    from physics.hf.engine import ChainedFull
    from physics.hf.engine import run as engine_run
    from physics.hf.native import nativex

    fit = (("aadjust", Z, A, 1.1), ("aadjust", Z, A + 1, 1.1), ("ftable", Z, A + 1, 0.8),
           ("wtable", Z, A + 1, 1.2))
    seen = {"ok": [], "native": 0}
    orig_ok = Cascade._numpy_decay_ok

    def spy_ok(self, pop):
        v = orig_ok(self, pop)
        seen["ok"].append(v)
        return v

    orig_nw = widths_native.NativeWidths.__init__

    def spy_nw(self, *a, **k):
        seen["native"] += 1
        return orig_nw(self, *a, **k)

    monkeypatch.setattr(Cascade, "_numpy_decay_ok", spy_ok)
    monkeypatch.setattr(widths_native.NativeWidths, "__init__", spy_nw)

    def go(params, cas=None):
        with torch.inference_mode():
            r = engine_run(injection=ChainedFull(Z=Z, A=A, declared_energies=DECLARED,
                                                 cascade=cas, params=params))
        return r.channels_mb["xs000000"].detach().numpy().copy()

    cold = go(fit)
    assert seen["ok"] and all(seen["ok"])
    if nativex.available():
        assert seen["native"] > 0
    # a warmed Cascade at defaults, then the point: the cold run's numbers, and a real move
    cas = Cascade(Z, A, max(np.float32(DECLARED)), energies=tuple(
        float(np.float32(e)) for e in DECLARED))
    base = go((), cas)
    warm = go(fit, cas)
    np.testing.assert_array_equal(warm, cold)
    assert np.max(np.abs(warm / base - 1.0)) > 0.05


@needs_structure
def test_float_gamma_overrides_keep_numpy_decay():
    from physics.hf.emission.feeding import Cascade

    cas = Cascade(Z, A, max(DECLARED), energies=DECLARED)

    class _Pop:
        xspop_mb = torch.zeros(1)

    cas.gamma_overrides = {"ftable": np.array([[0.0, 0.0, 0.0], [0.0, 0.8, 0.0]])}
    assert cas._numpy_decay_ok(_Pop())
    assert float(cas.gamma_params(Z, A).ftable[1, 1]) == 0.8
    cas.gamma_overrides = {"ftable": torch.tensor([[0.0, 0.0, 0.0], [0.0, 0.8, 0.0]],
                                                  dtype=torch.float64, requires_grad=True)}
    assert not cas._numpy_decay_ok(_Pop())
    assert cas.gamma_params(Z, A) is None
