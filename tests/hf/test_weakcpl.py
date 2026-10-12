"""WEAKCPL: `collrule svw|svwa` = sv + weak-coupling (core-excitation) CC for odd-A targets on STRICT-vibrator cores."""

import math

import pytest
import torch

from physics.hf.input.defaults import default_options
from physics.hf.omp import parameters as P
from physics.hf.structure import collrule as CR


@pytest.fixture(autouse=True)
def _no_env(monkeypatch):
    monkeypatch.delenv(CR.ENV, raising=False)
    monkeypatch.delenv("INCOGNITA_TALYS_FIT", raising=False)


def _dfm(Z, A, **ov):
    from physics.hf.structure.deformation import deformation
    from physics.hf.structure.levels import discrete_levels
    from physics.hf.structure.masses import masses as get_masses

    o = default_options(Z, A, overrides=ov)
    m = get_masses(o)
    lv = discrete_levels(Z, A, o, m)
    return o, lv, deformation(Z, A, o, lv, m)


def _solve(Z, A, e, spins, pars, lev_e, betas):
    from physics.hf.core.tensors import DTYPE
    from physics.hf.ecis.incident import _t4_parameters
    from physics.hf.ecis.solver import solve_vibrational
    from physics.hf.omp.schrodinger import PARMASS_AMU, nucleus_mass_amu

    o = default_options(Z, A)
    et = torch.tensor(e, dtype=DTYPE)
    omp = _t4_parameters(Z, A, 1, et, o)
    n = len(spins)
    return solve_vibrational(omp, PARMASS_AMU[1], nucleus_mass_amu(Z, A), 0.0, et, torch.tensor(lev_e, dtype=DTYPE),
                             torch.tensor(spins, dtype=DTYPE), torch.tensor(pars, dtype=torch.int64),
                             torch.tensor([0.0] + [2.0] * (n - 1), dtype=DTYPE), torch.tensor(betas, dtype=DTYPE),
                             False, lmax=30)


def test_modes_and_targets():
    for m in ("svw", "svwa"):
        assert CR.mode(default_options(29, 63, overrides={"collrule": m})) == m
    o, lv, d = _dfm(29, 63, collrule="svw")  # Cu-63 (S): weak-coupling CC
    assert d.colltype == "V" and d.weakcc and P._colltype(29, 63, o) == "V"
    o, lv, d = _dfm(45, 103, collrule="svw")  # Rh-103 (R): only in svwa
    assert d.colltype == "R" and not d.weakcc
    o, lv, d = _dfm(45, 103, collrule="svwa")
    assert d.colltype == "V" and d.weakcc and P._colltype(45, 103, o) == "V"
    for Z, A in ((27, 59), (41, 93), (51, 121)):  # no qualifying core: untouched
        o, lv, d = _dfm(Z, A, collrule="svwa")
        assert d.colltype == "S" and not d.weakcc
    o, lv, d = _dfm(30, 68, collrule="svw")  # ee: exactly the sv realisation
    o2, lv2, d2 = _dfm(30, 68, collrule="sv")
    assert d.colltype == d2.colltype == "V" and (d.defpar == d2.defpar).all() and d.leveltype == d2.leveltype


def test_multiplet_sum_rule():
    """sum_J beta_J^2 = beta_core^2 (2I+1) (ECIS t^2/(2I+1) convention) for a complete multiplet, parity kept."""
    o, lv, d = _dfm(49, 115, collrule="svw")  # In-115 9/2+: J = 5/2 .. 13/2, all found
    b = CR._wtable()[(49, 115)]["beta2"]
    I = float(lv.all_spin[0])
    rows = [i for i in range(1, d.ndef + 1) if d.leveltype[int(d.indexlevel[i])] == "V" and d.vibband[i] > 0]
    js = sorted(float(lv.all_spin[int(d.indexlevel[i])]) for i in rows)
    assert js == [2.5, 3.5, 4.5, 5.5, 6.5]
    assert all(int(lv.all_parity[int(d.indexlevel[i])]) == int(lv.all_parity[0]) for i in rows)
    s = sum(float(d.defpar[d.vibband[i]]) ** 2 for i in rows)
    assert s == pytest.approx(b * b * (2 * I + 1), rel=1e-4)


def test_no_dwba_double_count():
    """The core 2+_1 is in CC: the DWBA weak coupling must not spread it over other D levels."""
    from physics.hf.input.nuclides import weak_coupling_core
    from physics.hf.structure.deformation import deformation, weak_coupling
    from physics.hf.structure.levels import discrete_levels
    from physics.hf.structure.masses import masses as get_masses

    out = {}
    for m in ("n", "svw"):
        o = default_options(29, 63, overrides={"collrule": m})
        ms = get_masses(o)
        lv = discrete_levels(29, 63, o, ms)
        d = deformation(29, 63, o, lv, ms)
        zc, nc = weak_coupling_core(o)
        cz = o.Zinit - zc
        ca = cz + o.Ninit - nc
        cl = discrete_levels(cz, ca, o, ms)
        out[m] = weak_coupling(d, lv, deformation(cz, ca, o, cl, ms), cl, o).deform
    n_off, n_on = int((out["n"] != 0).sum()), int((out["svw"] != 0).sum())
    assert n_on < n_off  # the 2+ multiplet's DWBA assignments are gone


@pytest.mark.parametrize("I,par", [(1.5, -1), (0.5, -1), (4.5, 1)])
def test_spectator_theorem(I, par):
    """Degenerate multiplet: the odd nucleon is a spectator, so sigma_tot, sigma_reac, shape elastic and sum_J sigma_J equal the
    core problem (I = 0, one 2+ at the same energy, same beta) exactly, and sigma_J / sum = (2J+1)/(5(2I+1))."""
    e, b, ex = [0.3, 2.0, 6.0], 0.25, 0.99
    core = _solve(29, 63, e, [0.0, 2.0], [1, 1], [0.0, ex], [b])
    js = [abs(I - 2) + k for k in range(int(I + 2 - abs(I - 2)) + 1)]
    odd = _solve(29, 63, e, [I] + js, [par] * (1 + len(js)), [0.0] + [ex] * len(js),
                 [b * math.sqrt((2 * j + 1) / 5.0) for j in js])
    for f in ("sigma_tot_mb", "sigma_reac_mb", "sigma_shape_el_mb"):
        torch.testing.assert_close(getattr(odd, f), getattr(core, f), rtol=2e-6, atol=1e-6)
    dsum = odd.sigma_direct_mb[:, 1:].sum(1)
    torch.testing.assert_close(dsum, core.sigma_direct_mb[:, 1], rtol=2e-6, atol=1e-6)
    frac = odd.sigma_direct_mb[1:, 1:] / dsum[1:, None]  # above the 0.99 MeV threshold
    want = torch.tensor([(2 * j + 1) / (5 * (2 * I + 1)) for j in js], dtype=frac.dtype)
    torch.testing.assert_close(frac, want.expand_as(frac), rtol=1e-5, atol=1e-7)


def test_dwba_limit():
    """beta -> 0 at the real (split) member energies: CC sigma_J -> the TALYS weak-coupling DWBA picture, i.e. the core-spin
    0 -> 2+ cross section at that level's energy times (2J+1)/(5(2I+1))."""
    eps, e = 0.02, [1.0, 3.0, 8.0]
    o, lv, d = _dfm(29, 63, collrule="svw")
    rows = [i for i in range(1, d.ndef + 1) if d.leveltype[int(d.indexlevel[i])] == "V" and d.vibband[i] > 0]
    idx = [int(d.indexlevel[i]) for i in rows]
    I = float(lv.all_spin[0])
    js = [float(lv.all_spin[i]) for i in idx]
    ee = [float(lv.all_e_mev[i]) for i in idx]
    b = eps * CR._wtable()[(29, 63)]["beta2"]
    odd = _solve(29, 63, e, [I] + js, [-1] * (1 + len(js)), [0.0] + ee, [b * math.sqrt((2 * j + 1) / 5.0) for j in js])
    for k, (j, x) in enumerate(zip(js, ee)):
        core = _solve(29, 63, e, [0.0, 2.0], [1, 1], [0.0, x], [b])
        want = core.sigma_direct_mb[:, 1] * (2 * j + 1) / (5 * (2 * I + 1))
        torch.testing.assert_close(odd.sigma_direct_mb[:, 1 + k], want, rtol=2e-2, atol=1e-9)
