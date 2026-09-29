"""T11 fission: the WKB path, the barrier parameters, the transition-state bands and the
fission transmission, against TALYS's own `fis*.txt` / `fis*.trans` dumps (gate A-fis).

Tests that need the TALYS `structure/` database or the reference archives skip when those are
absent, as CONTRACT.md §6 requires.
"""

from __future__ import annotations

import math
from pathlib import Path

import pytest
import torch

from physics.hf.core.constants import talys_constants
from physics.hf.core.tensors import DTYPE
from physics.hf.fission import reference as R
from physics.hf.fission import wkb as W
from physics.hf.fission.barriers import NUMHILL, t1barrier, thill
from physics.hf.fission.parameters import (
    NUMBAR,
    TransitionStates,
    barrier_levels,
    fission_parameters,
    rotband,
)
from physics.hf.fission.transmission import (
    FissionLevelDensities,
    fission_level_densities,
    fission_transmission,
)
from tests._data import talys_structure_dir_or_missing

torch.set_num_threads(2)

WORKDIR = Path.home() / "hf_t11" / "ref"
HAS_STRUCTURE = (talys_structure_dir_or_missing() / "fission" / "hfbpath_bskg3").is_dir()
HAS_U238 = R.available("U238")
needs_structure = pytest.mark.skipif(not HAS_STRUCTURE, reason="TALYS structure/ not installed")
needs_u238 = pytest.mark.skipif(not HAS_U238, reason="U238 reference archive absent")

# TALYS's own printed values for the U-239 compound nucleus, default run
# (features/hf_reference/raw/default__U238.tar.gz, fis092239.txt).
U239_BARRIERS = ((6.008, 1.331231, 92.10976), (6.731, 1.612479, 162.0449), (2.898, 0.9311627, 170.5736))


def _target(Z: int, A: int):
    from physics.hf.input.defaults import default_options, default_params

    o = default_options(Z, A)
    return o, default_params(Z, A, o)


# --------------------------------------------------------------------------- Hill-Wheeler


def test_thill_matches_the_closed_form_and_saturates():
    xs = (-20.0, -1.0, 0.0, 1.0, 10.0)
    e = torch.tensor(xs, dtype=DTYPE)
    b = torch.tensor(0.0, dtype=DTYPE)
    w = torch.tensor(1.0, dtype=DTYPE)
    t = thill(e, b, w)
    # TALYS's `twopi` is a real(sgl) constant, so the closed form must use T1's value, not
    # math.tau, or the comparison is 1e-8 off for that reason alone.
    twopi = talys_constants()["twopi"]
    expect = [1.0 / (1.0 + math.exp(-twopi * x)) for x in xs]
    # thill.f90:33 cuts the tail to exactly zero once 2 pi (E - B) / hw falls to -80
    assert twopi * xs[0] < -80.0 and float(t[0]) == 0.0
    assert all(abs(float(t[i]) - expect[i]) < 1e-12 for i in (1, 2, 3, 4))
    assert float(t[2]) == pytest.approx(0.5)
    assert torch.all(t[1:].diff() > 0)


def test_thill_is_differentiable_in_the_barrier_height():
    b = torch.tensor(6.0, dtype=DTYPE, requires_grad=True)
    t = thill(torch.tensor(6.5, dtype=DTYPE), b, torch.tensor(1.0, dtype=DTYPE))
    t.backward()
    assert torch.isfinite(b.grad) and float(b.grad) < 0.0  # a higher barrier transmits less


# --------------------------------------------------------------------------- WKB numerics


def test_gauss_kronrod_41_integrates_a_polynomial_exactly():
    a = torch.tensor(0.0, dtype=DTYPE)
    b = torch.tensor(2.0, dtype=DTYPE)
    val, err = W._gauss_legendre41(lambda x: x**5 - 3 * x**2 + 1, a, b)
    assert float(val) == pytest.approx(2.0**6 / 6 - 2.0**3 + 2.0, abs=1e-10)
    assert float(err) < 1e-10


def test_parab_fit_recovers_a_known_parabola():
    n = 21
    beta = torch.arange(n + 1, dtype=DTYPE)
    # V = 5 - 0.25 (i - 10)^2 around a maximum at i = 10
    v = 5.0 - 0.25 * (beta - 10.0) ** 2
    path = W.FissionPath(
        Z=92, A=239, nbeta=n, betafis=beta, vfis_mev=v, rmiufis=torch.ones(n + 1, dtype=DTYPE),
        nextr=1, iiextr=(1, 10, n, 0, 0, 0, 0, 0),
    )
    height, width = W.parab_fit(10, 3, 2.0, path)
    assert float(height) == pytest.approx(5.0, abs=1e-9)
    assert float(width) == pytest.approx(math.sqrt(2 * 0.25 / 2.0), abs=1e-9)


@needs_structure
def test_wkb_reproduces_the_printed_u239_barriers():
    path = W.read_hfbpath(92, 239, 6)
    assert path is not None and path.nextr == 5
    res = W.wkb(92, 239, path)
    assert res.nbar == 3
    for i, (b, w, _mi) in enumerate(U239_BARRIERS, start=1):
        assert float(res.fbarrier_mev[i]) == pytest.approx(b, rel=1e-6)
        assert float(res.fwidth_mev[i]) == pytest.approx(w, rel=1e-6)


@needs_structure
def test_twkbint_is_monotone_and_saturates_above_the_table():
    path = W.read_hfbpath(92, 239, 6)
    res = W.wkb(92, 239, path)
    e = torch.linspace(0.5, float(res.uwkb_mev[-1]), 40, dtype=DTYPE)
    t = W.twkbint(res, e, 1)
    assert torch.all(t.diff() > 0)
    assert 0.0 < float(t[0]) < 1.0
    above = W.twkbint(res, torch.tensor(1.0e3, dtype=DTYPE), 1)
    assert float(above) == 1.0


# --------------------------------------------------------------------------- rotational bands


def test_rotband_builds_the_k0_minus_band_with_the_erk10_shift():
    head = TransitionStates(
        n=2,
        e_mev=torch.tensor([0.0, 0.0, 0.4], dtype=DTYPE),
        spin=torch.tensor([0.0, 0.0, 0.0], dtype=DTYPE),
        parity=(0, 1, -1),
    )
    inertia = torch.tensor([0.0, 10.0, 0.0, 0.0], dtype=DTYPE)
    fecont = torch.tensor([0.0, 1.0, 0.0, 0.0], dtype=DTYPE)
    band = rotband((TransitionStates(), head), inertia, fecont, 1)[1]
    e = [float(x) for x in band.e_mev[1 : band.n + 1]]
    j = [float(x) for x in band.spin[1 : band.n + 1]]
    assert e == sorted(e)
    # a K = 0 head steps in 2 units of J; a 0- head additionally starts at J = 1 and is
    # shifted by 1/I, the k=0- to k=1- splitting (rotband.f90:64-68)
    plus = [(jj, ee) for jj, ee, p in zip(j, e, band.parity[1:], strict=True) if p == 1]
    minus = [(jj, ee) for jj, ee, p in zip(j, e, band.parity[1:], strict=True) if p == -1]
    assert [jj for jj, _ in plus] == [0.0, 2.0, 4.0]
    assert [jj for jj, _ in minus][:2] == [1.0, 3.0]
    assert plus[1][1] == pytest.approx(2 * 3 / 20.0)
    assert minus[0][1] == pytest.approx(0.4 + 1 / 10.0)
    assert minus[1][1] == pytest.approx(0.4 + 1 / 10.0 + (3 * 4 - 1 * 2) / 20.0)
    assert all(x <= 1.0 for x in e)  # everything above fecont is dropped


@needs_structure
def test_default_run_has_no_transition_states_and_zero_fecont():
    """`hbstate`/`class2` default to false, so the default barrier is pure continuum."""
    o, p = _target(92, 238)
    fp = fission_parameters(92, 239, o, p)
    assert o.fismodel == 6 and not o.flaghbstate and not o.flagclass2
    assert fp.nfisbar == 3
    for i in range(1, fp.nfisbar + 1):
        assert fp.headband[i].n == 0 and fp.rotational[i].n == 0
        assert float(fp.fecont_mev[i]) == 0.0
    assert fp.nclass2 == 0


# --------------------------------------------------------------------------- parameters


@needs_structure
@pytest.mark.parametrize(
    ("Z", "A", "nbar"), [(92, 239, 3), (92, 236, 2), (94, 240, 2), (90, 233, 2), (95, 242, 2)]
)
def test_fission_parameters_barrier_count_matches_the_dumps(Z, A, nbar):
    o, p = _target(Z, A - 1)
    assert fission_parameters(Z, A, o, p).nfisbar == nbar


@needs_structure
def test_fismodel_1_reads_the_maslov_table_and_keeps_user_barriers():
    from physics.hf.fission.parameters import read_barrier_file

    tab = read_barrier_file(92, 239)
    assert tab is not None
    o, p = _target(92, 238)
    o1 = type(o)(**{**o.__dict__, "fismodel": 1})
    fp = fission_parameters(92, 239, o1, p)
    assert fp.nfisbar == 2
    assert float(fp.fbarrier_mev[1]) == pytest.approx(tab[0])
    assert float(fp.fwidth_mev[1]) == pytest.approx(tab[1])


@needs_structure
def test_barrier_levels_feeds_t6_density_for_ibar_above_zero():
    from physics.hf.density.matching import densitymatch
    from physics.hf.density.models import density
    from physics.hf.density.parameters import densitypar
    from physics.hf.density.tables import attach_tables
    from physics.hf.structure.levels import discrete_levels
    from physics.hf.structure.masses import masses

    o, p = _target(92, 238)
    fp = fission_parameters(92, 239, o, p)
    bl = barrier_levels(fp)
    assert bl.nfisbar == 3 and bl.axtype[1:4] == (1, 1, 1)
    ms = masses(o, p)
    ld = densitymatch(
        attach_tables(densitypar(92, 239, o, p, ms, discrete_levels(92, 239, o, ms, p), barriers=bl))
    )
    assert ld.nfisbar == 3 and ld.ldmodel == 7
    e = torch.tensor(4.0, dtype=DTYPE)
    j = torch.tensor(2.5, dtype=DTYPE)
    rho = [float(density(ld, e, j, 1, ib)) for ib in range(4)]
    assert all(x > 0 for x in rho)
    # a barrier level density is far above the ground-state one at the same excitation energy
    assert min(rho[1:]) > rho[0]


# --------------------------------------------------------------------------- transmission


@needs_structure
def test_fission_level_density_grid_follows_densprepare():
    o, p = _target(92, 238)
    fp = fission_parameters(92, 239, o, p)
    ld = _ld(92, 239, o, p, fp)
    grid = fission_level_densities(fp, ld, 4.8, odd=1, maxj=5)
    assert isinstance(grid, FissionLevelDensities)
    for ib in range(1, fp.nfisbar + 1):
        n = grid.nbintfis[ib]
        assert n % 2 == 0 and n >= 2
        e = grid.eintfis_mev[ib]
        assert float(e[1]) == pytest.approx(0.0)  # fecont = 0 in the default run
        assert float(e[n]) == pytest.approx(4.8)  # densprepare.f90:439 moves the last point
        odd_idx = torch.arange(1, n - 1, 2)
        assert torch.all(e[odd_idx + 1] > e[odd_idx])  # midpoints sit above their edges


def _ld(Z, A, o, p, fp):
    from physics.hf.density.matching import densitymatch
    from physics.hf.density.parameters import densitypar
    from physics.hf.density.tables import attach_tables
    from physics.hf.structure.levels import discrete_levels
    from physics.hf.structure.masses import masses

    ms = masses(o, p)
    lv = discrete_levels(Z, A, o, ms, p)
    return densitymatch(
        attach_tables(densitypar(Z, A, o, p, ms, lv, barriers=barrier_levels(fp)))
    )


@needs_structure
@needs_u238
def test_tfission_reproduces_the_u239_transmission_dump():
    """A-fis on the U-239 compound nucleus: T, Gamma, tau and rho at every incident energy."""
    d = R.extract("U238", "default", WORKDIR)
    blocks = R.read_transmission(d / "fis092239.trans")
    groups = R.transmission_groups(blocks)
    assert len(groups) == 23  # one per incident energy
    o, p = _target(92, 238)
    fp = fission_parameters(92, 239, o, p)
    ld = _ld(92, 239, o, p, fp)
    worst = 0.0
    n = 0
    for g in groups[::5]:
        b = g[0]
        maxj = len(b.spin) - 1
        grid = fission_level_densities(fp, ld, b.exinc_mev, odd=1, maxj=maxj)
        ft = fission_transmission(fp, grid, ld, b.exinc_mev, 0.0, o, odd=1, maxj=maxj)
        for port, ref in ((ft.tfis, b.tfis), (ft.denfis_per_mev, b.density_per_mev)):
            pv = port.detach().numpy()
            live = (ref > 0) & (pv > 0)
            assert live.any()
            r = abs(torch.log(torch.as_tensor(pv[live] / ref[live])))
            worst = max(worst, float(r.max()))
            n += int(live.sum())
    assert n > 150
    assert worst < 5.0e-2, f"A-fis: worst |ln(port/talys)| = {worst:.3e}"
    assert worst < 1.0e-4, "regression: the port used to agree to 1e-5"


@needs_structure
@needs_u238
def test_tfisA_histogram_sums_to_the_transmission():
    """`tfisA(J,P,0)` is the total the width-fluctuation correction re-weights (t1barrier.f90:140)."""
    d = R.extract("U238", "default", WORKDIR)
    b = R.transmission_groups(R.read_transmission(d / "fis092239.trans"))[10][0]
    o, p = _target(92, 238)
    fp = fission_parameters(92, 239, o, p)
    ld = _ld(92, 239, o, p, fp)
    maxj = len(b.spin) - 1
    grid = fission_level_densities(fp, ld, b.exinc_mev, odd=1, maxj=maxj)
    ft = fission_transmission(fp, grid, ld, b.exinc_mev, 0.0, o, odd=1, maxj=maxj, primary=True)
    assert ft.tfisA.shape == (maxj + 1, 2, NUMHILL + 1)
    inner = t1barrier(fp, grid, 1, torch.tensor(b.exinc_mev, dtype=DTYPE), ld.deltaW_mev,
                      odd=1, maxj=maxj, collect_hill=True)
    total = ft.tfisA[..., 0]
    binned = ft.tfisA[..., 1:].sum(-1)
    assert torch.allclose(total, binned, rtol=1e-10)
    assert torch.allclose(total, inner.trfis.clamp(min=1e-30), rtol=1e-10)
    assert torch.all(ft.rhofisA >= 1.0)  # tfission.f90:147 seeds it at 1, not 0


@needs_structure
def test_tfission_brackets_the_bin_and_falls_with_energy():
    o, p = _target(92, 238)
    fp = fission_parameters(92, 239, o, p)
    ld = _ld(92, 239, o, p, fp)
    grid = fission_level_densities(fp, ld, 6.0, odd=1, maxj=10)
    ft = fission_transmission(fp, grid, ld, 6.0, 0.5, o, odd=1, maxj=10, exmax_mev=6.5)
    live = ft.tfis > 0
    assert live.any()
    assert torch.all(ft.tfisdown[live] < ft.tfis[live])
    assert torch.all(ft.tfis[live] < ft.tfisup[live])


@needs_structure
def test_fission_transmission_is_differentiable_in_fisbar_and_fishw():
    """Contract §4.4: `fisbar` and `fishw` are adjustable, so gradients must reach `tfis`."""
    from physics.hf.input.defaults import default_options, default_params

    o = default_options(92, 238, overrides={"fismodel": 1})
    p = default_params(92, 238, o)
    zix, nix = o.Zinit - 92, o.Ninit - 147
    for key, val in (("fisbar", 6.0), ("fishw", 0.8)):
        t = p.values[key].clone()
        t[zix, nix, 1] = val
        p.values[key] = t
    p.requires_grad_(["fisbar", "fishw"])
    fp = fission_parameters(92, 239, o, p)
    ld = _ld(92, 239, o, p, fp)
    grid = fission_level_densities(fp, ld, 6.0, odd=1, maxj=6)
    ft = fission_transmission(fp, grid, ld, 6.0, 0.0, o, odd=1, maxj=6)
    ft.tfis.sum().backward()
    gb = p.values["fisbar"].grad[zix, nix, 1]
    gw = p.values["fishw"].grad[zix, nix, 1]
    assert torch.isfinite(gb) and float(gb) < 0.0  # a higher barrier transmits less
    assert torch.isfinite(gw) and float(gw) != 0.0


# --------------------------------------------------------------------------- systematics


def test_fisdata_tables_have_the_shapes_talys_declares():
    from physics.hf.fission import systematics as S

    for name, shape in (
        ("BARCOF", (7, 7)), ("L20COF", (5, 4)), ("L80COF", (5, 4)), ("LMXCOF", (6, 4)),
        ("X1B", (6, 11)), ("X2B", (6, 11)), ("X3B", (10, 20)),
        ("X1H", (6, 11)), ("X2H", (6, 11)), ("X3H", (10, 20)),
    ):
        t = getattr(S, name)
        assert (len(t), len(t[0])) == shape, name
    assert (len(S.EGSCOF), len(S.EGSCOF[0]), len(S.EGSCOF[0][0])) == (5, 6, 4)


def test_sierk_and_rldm_give_physical_barriers():
    from physics.hf.fission.systematics import barsierk, rldm

    bfis, egs, lbar0 = barsierk(92, 239, 0)
    assert 2.0 < float(bfis) < 8.0  # Sierk RFRM for uranium
    assert float(egs) == 0.0 and float(lbar0) == 0.0  # l = 0 returns early
    assert 8.0 < float(barsierk(83, 209, 0)[0]) < 16.0  # Bi-209 near 11.9 MeV
    assert float(barsierk(10, 20, 0)[0]) == 0.0  # outside Sierk's Z range
    egs, esp = rldm(92, 239, 0)
    assert 0.0 < float(esp - egs) < 20.0


# --------------------------------------------------------------------------- gate


@needs_structure
@needs_u238
def test_a_fis_gate_on_u238():
    """The published A-fis row for one target, so a regression fails the suite, not just the CLI."""
    from physics.hf.fission.score import TOLERANCE, score_target

    res = score_target("U238", workdir=WORKDIR)
    rows = {r["name"]: r for r in res["rows"] if r["n"]}
    assert set(rows) >= {"tfis", "height_of_fission_barrier", "nfisbar_exact"}
    for name, row in rows.items():
        assert row["p95"] <= TOLERANCE, f"A-fis {name}: p95 {row['p95']:.3e}"
        assert row["n_zero_in_port"] == 0, name
    assert rows["nfisbar_exact"]["max"] == 0.0
    assert rows["tfis"]["p95"] < 1e-4


def test_numbar_matches_talys():
    assert NUMBAR == 3 and W.NUMBAR == 3
