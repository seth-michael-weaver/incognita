"""T1 core: constants, numerics, angular-momentum algebra and grids (physics/hf/CONTRACT.md §7).

Special functions are checked against independent references (numpy/scipy/sympy), never against
the port itself. Grids are checked against the TALYS reference dumps (gate A-grid); those tests
skip when the dumps are absent.
"""

from __future__ import annotations

import itertools
import json
import math
from functools import cache

import numpy as np
import pytest
import torch

from physics.hf import reference as ref
from physics.hf.core import angmom, grids, numerics
from physics.hf.core.constants import (
    PARSYM,
    machine_limits,
    nuclide_symbol,
    particles,
    sgn_table,
    talys_constants,
)

D = torch.float64


# ----------------------------------------------------------------------------------------------
# constants
# ----------------------------------------------------------------------------------------------


def test_constants_carry_single_precision_literals():
    c = talys_constants()
    x = talys_constants("exact")
    # amu is real(dbl) but assigned from a single-precision literal in the TALYS build
    assert c["amu"] == float(np.float32(931.49410242)) != 931.49410242
    assert x["amu"] == 931.49410242
    assert c["parmass"][1] == float(np.float32(1.00866491574))
    # hbar c = 197.3269804 MeV fm (CODATA 2018); both modes within their precision
    assert abs(x["hbarc"] - 197.3269804) < 1e-6
    assert abs(c["hbarc"] - 197.3269804) / 197.3269804 < 2e-7
    for k in ("pi2h2c2", "pi2h3c2", "amupi2h3c2", "amu4pi2h2c2", "twopihbar", "sqrttwopi"):
        assert c[k] == float(np.float32(c[k])), f"{k} not a float32 value"
        assert abs(c[k] - x[k]) / abs(x[k]) < 1e-6
    assert x["pi2h2c2"] == pytest.approx(0.1 / (math.pi**2 * x["hbarc"] ** 2), rel=1e-14)
    assert c["spin2"] == (1, 1, 1, 2, 1, 1, 1)
    assert c["parA"] == (0, 1, 1, 2, 3, 3, 4)
    with pytest.raises(ValueError):
        talys_constants("double")


def test_sign_symbols_particles_limits():
    s = sgn_table()
    assert len(s) == 121 and s[0] == 1.0 and s[1] == -1.0 and s[120] == 1.0
    assert nuclide_symbol(26) == "Fe" and nuclide_symbol(92) == "U" and nuclide_symbol(124) == "C4"
    inc = particles()
    assert inc[-1] is False and all(inc[t] for t in range(0, 7))
    only = particles(k0=1, outtype=("p",))
    assert only[1] and only[2] and not only[0] and not only[6]
    assert particles(flagomponly=True)[1] is True  # incident always included
    assert machine_limits()["sgl_eps"] == pytest.approx(1.1920929e-07)


# ----------------------------------------------------------------------------------------------
# numerics
# ----------------------------------------------------------------------------------------------


def test_gauleg_matches_numpy_and_talys_order():
    x, w = numerics.gauleg(50, single=False)
    xr, wr = np.polynomial.legendre.leggauss(50)
    assert np.allclose(np.sort(x.numpy()), np.sort(xr), atol=1e-14)
    order = np.argsort(x.numpy())
    # TALYS's weights are half the textbook ones: they sum to 1 on [-1, 1]
    assert np.allclose(w.numpy()[order], 0.5 * wr[np.argsort(xr)], atol=1e-14)
    assert float(w.sum()) == pytest.approx(1.0, abs=1e-14)
    # TALYS order: first half positive descending, second half their negatives
    assert (x[:25] > 0).all() and (x[:25].diff() < 0).all()
    assert torch.equal(x[25:], -x[:25])
    # mapped interval integrates exactly
    xm, wm = numerics.gauleg(10, 0.0, 2.0, single=False)
    assert float((wm * xm**5).sum()) == pytest.approx(0.5 * 2.0**6 / 6, rel=1e-13)


def test_gauleg_default_is_talys_single_precision_not_the_exact_table():
    """`single=False` above is the mathematics; the DEFAULT is what TALYS integrates with, and
    the two are not the same table. gauleg.f90:50 builds each weight from `P_{n-1}` computed by a
    49-term real(sgl) recurrence, whose roundoff is worst where `P_{n-1}` is smallest -- at the
    outermost node. Asserting the default against numpy at 1e-14, as this file used to, asserts
    that the port is NOT TALYS; the GOE triple integral is dominated by that node and moves 9e-4
    on it (docs/results/hf-compound-port.md, the GOE section)."""
    x, w = numerics.gauleg(50)
    xe, we = numerics.gauleg(50, single=False)
    assert np.abs(x.numpy() - xe.numpy()).max() < 1e-7  # nodes: float32, still the right roots
    rel = (w / we - 1.0).numpy()
    outer = int(np.argmax(np.abs(x.numpy())))
    assert rel[outer] == pytest.approx(9.755e-4, rel=1e-3)
    assert np.abs(rel[np.abs(x.numpy()) < 0.98]).max() < 1e-4


def test_gauleg_odd_n_reproduces_the_fortran_quirk():
    x, _ = numerics.gauleg(5)
    # ns2 = 2: tgl(3) = -tgl(1), tgl(4) = -tgl(2), tgl(5) = -tgl(3) = tgl(1); no middle root
    assert x[2] == -x[0] and x[3] == -x[1] and x[4] == x[0]
    assert not torch.isclose(x, torch.zeros((), dtype=D)).any()


def test_gaulag_is_the_32_point_rule():
    x, w = numerics.gaulag(32)
    xr, wr = np.polynomial.laguerre.laggauss(32)
    assert np.allclose(x.numpy(), xr, rtol=1e-13)
    # TALYS tabulates sqrt(weight): molprepare.f90 squares wmo * exp(x/2)
    assert np.allclose(w.numpy() ** 2, wr, rtol=1e-10, atol=1e-60)
    with pytest.raises(ValueError):
        numerics.gaulag(16)


def _locate_brute(xx, x, ib, ie):
    xx = np.asarray(xx, float)
    if ib > ie:
        return 0
    ascend = xx[ie] >= xx[ib]
    idx = range(ib, ie + 1)
    if ascend:
        jl = max([k for k in idx if xx[k] <= x], default=ib - 1)
    else:
        jl = max([k for k in idx if xx[k] > x], default=ib - 1)
    if x == xx[ib]:
        return ib
    if x == xx[ie]:
        return ie - 1
    return jl


def test_locate_conventions():
    rng = np.random.default_rng(1)
    for descending in (False, True):
        xx = np.concatenate([[0.0], np.sort(rng.uniform(0, 10, 30))])
        if descending:
            xx = np.concatenate([[0.0], xx[1:][::-1]])
        probes = np.concatenate([rng.uniform(-1, 11, 200), xx[1:], [xx[1], xx[-1]]])
        got = numerics.locate(torch.tensor(xx, dtype=D), torch.tensor(probes, dtype=D), 1, 30)
        want = [_locate_brute(xx, p, 1, 30) for p in probes]
        assert got.tolist() == want
    assert int(numerics.locate(torch.tensor([0.0, 1.0], dtype=D), torch.tensor(0.5), 2, 1)) == 0


def test_pol1_pol2_are_exact_and_differentiable():
    x1, x2, x3 = (torch.tensor(v, dtype=D) for v in (0.3, 1.1, 2.6))
    f = lambda t: 2.0 - 3.0 * t + 0.7 * t * t  # noqa: E731
    x = torch.linspace(-1, 4, 11, dtype=D)
    assert torch.allclose(numerics.pol2(x1, x2, x3, f(x1), f(x2), f(x3), x), f(x), atol=1e-12)
    g = lambda t: 1.5 - 0.25 * t  # noqa: E731
    assert torch.allclose(numerics.pol1(x1, x2, g(x1), g(x2), x), g(x), atol=1e-14)
    y1 = torch.tensor(1.0, dtype=D, requires_grad=True)
    numerics.pol1(x1, x2, y1, torch.tensor(3.0, dtype=D), torch.tensor(0.7, dtype=D)).backward()
    assert float(y1.grad) == pytest.approx((1.1 - 0.7) / 0.8)


def test_spline_splint_match_scipy():
    from scipy.interpolate import CubicSpline

    rng = np.random.default_rng(2)
    xa = np.sort(rng.uniform(0, 5, 12))
    ya = np.sin(xa) + 0.1 * xa
    xs = np.linspace(xa[0], xa[-1], 57)
    y2 = numerics.spline(torch.tensor(xa), torch.tensor(ya))
    got = numerics.splint(torch.tensor(xa), torch.tensor(ya), y2, torch.tensor(xs)).numpy()
    assert np.allclose(got, CubicSpline(xa, ya, bc_type="natural")(xs), atol=1e-12)
    y2c = numerics.spline(torch.tensor(xa), torch.tensor(ya), 0.3, -1.2)
    gotc = numerics.splint(torch.tensor(xa), torch.tensor(ya), y2c, torch.tensor(xs)).numpy()
    assert np.allclose(gotc, CubicSpline(xa, ya, bc_type=((1, 0.3), (1, -1.2)))(xs), atol=1e-12)
    # batched tables
    yb = torch.tensor(np.stack([ya, 2 * ya]))
    y2b = numerics.spline(torch.tensor(xa).expand(2, -1), yb)
    assert torch.allclose(y2b[1], 2 * y2b[0], atol=1e-12)
    # outside the table: the end cubic, as TALYS's clamped bisection
    out = numerics.splint(torch.tensor(xa), torch.tensor(ya), y2, torch.tensor([xa[-1] + 0.5]))
    assert np.isfinite(out.numpy()).all()
    with pytest.raises(ValueError):
        numerics.splint(
            torch.tensor([0.0, 1.0, 1.0]),
            torch.zeros(3, dtype=D),
            torch.zeros(3, dtype=D),
            torch.tensor([1.0], dtype=D),
        )
    yg = torch.tensor(ya, requires_grad=True)
    numerics.splint(
        torch.tensor(xa), yg, numerics.spline(torch.tensor(xa), yg), torch.tensor(xs)
    ).sum().backward()
    assert torch.isfinite(yg.grad).all()


def test_trapzd_stages_and_quirk():
    f = lambda x: x**3 + 1.0  # noqa: E731
    a, b = 0.0, 2.0
    assert float(numerics.trapzd(f, a, b, 1)) == pytest.approx(0.5 * 2 * (1 + 9))
    for n in (2, 3, 5):
        it = 2 ** (n - 2)
        dl = (b - a) / it
        mids = a + dl * (np.arange(it) + 0.5)
        midpoint = dl * np.sum(mids**3 + 1)
        # TALYS resets snew: half the midpoint rule, not the refined trapezoid
        assert float(numerics.trapzd(f, a, b, n)) == pytest.approx(0.5 * midpoint, rel=1e-13)


def test_fcoul_matches_closed_form():
    e = torch.tensor([-0.6, -0.1, 0.0, 0.2, 0.7], dtype=D)
    got = numerics.fcoul(e).numpy()
    ev = e.numpy()
    want = [
        (1 + v * v) ** (1 / 3) / v * math.atan(v)
        if v < 0
        else 1.0
        if v == 0
        else (1 - v * v) ** (1 / 3) / (2 * v) * math.log((1 + v) / (1 - v))
        for v in ev
    ]
    assert np.allclose(got, want, rtol=1e-14)
    assert got[2] == 1.0 and abs(got[1] - 1) < 0.01 and abs(got[3] - 1) < 0.02


def test_rtbis_and_zbrak():
    f = torch.cos
    lo, hi = numerics.zbrak(f, 0.0, 10.0, 100, 5)
    assert lo.numel() == 3
    roots = numerics.rtbis(f, lo, hi, 1e-10)
    assert np.allclose(roots.numpy(), [math.pi / 2, 3 * math.pi / 2, 5 * math.pi / 2], atol=1e-9)
    lo2, _ = numerics.zbrak(f, 0.0, 10.0, 100, 1)
    assert lo2.numel() == 1
    # sign orientation: f(x1) > 0 starts from x2
    r = numerics.rtbis(
        lambda x: 1.0 - x, torch.tensor([0.0], dtype=D), torch.tensor([3.0], dtype=D), 1e-9
    )
    assert float(r) == pytest.approx(1.0, abs=1e-8)


# ----------------------------------------------------------------------------------------------
# angular momentum
# ----------------------------------------------------------------------------------------------


def test_clebsch_matches_sympy():
    from sympy import Rational
    from sympy.physics.wigner import clebsch_gordan

    half = lambda v: Rational(int(round(2 * v)), 2)  # noqa: E731
    js = [0, 0.5, 1, 1.5, 2, 2.5, 3]
    rows, want = [], []
    for j1, j2, j3 in itertools.product(js, js, js):
        for m1 in np.arange(-j1, j1 + 0.1, 1):
            for m2 in np.arange(-j2, j2 + 0.1, 1):
                rows.append((j1, j2, j3, m1, m2))
                want.append(
                    float(
                        clebsch_gordan(
                            half(j1), half(j2), half(j3), half(m1), half(m2), half(m1 + m2)
                        )
                    )
                )
    a = torch.tensor(rows, dtype=D)
    got = angmom.clebsch(a[:, 0], a[:, 1], a[:, 2], a[:, 3], a[:, 4])
    w = torch.tensor(want, dtype=D)
    assert float((got - w).abs().max()) < 1e-13
    assert int(((w != 0) & (got == 0)).sum()) == 0
    # explicit m3 != m1 + m2 gives zero
    z = angmom.clebsch(
        torch.tensor(1.0),
        torch.tensor(1.0),
        torch.tensor(1.0),
        torch.tensor(0.0),
        torch.tensor(0.0),
        torch.tensor(1.0),
    )
    assert float(z) == 0.0


def test_racah_matches_sympy():
    from sympy import Rational
    from sympy.physics.wigner import racah

    vals = [0, 0.5, 1, 1.5, 2]
    rows = list(itertools.product(vals, repeat=6))
    want = []
    for t in rows:
        try:
            want.append(float(racah(*[Rational(int(2 * v), 2) for v in t])))
        except ValueError:  # sympy refuses couplings that violate a triangle rule: W = 0
            want.append(0.0)
    a = torch.tensor(rows, dtype=D)
    got = angmom.racah(*[a[:, i] for i in range(6)])
    w = torch.tensor(want, dtype=D)
    assert float((got - w).abs().max()) < 1e-13
    assert int((w != 0).sum()) > 400


def test_plegendre_matches_scipy_and_grads():
    from scipy.special import eval_legendre

    x = torch.linspace(-1, 1, 23, dtype=D, requires_grad=True)
    p = angmom.plegendre(12, x)
    want = np.stack([eval_legendre(ell, x.detach().numpy()) for ell in range(13)], axis=-1)
    assert np.allclose(p.detach().numpy(), want, atol=1e-13)
    assert float(angmom.plegendre_l(3, torch.tensor(0.4, dtype=D))) == pytest.approx(
        eval_legendre(3, 0.4)
    )
    p[:, 5].sum().backward()
    assert torch.isfinite(x.grad).all()
    assert float(angmom.logfact(torch.tensor(6.0))) == pytest.approx(math.log(120.0))


# ----------------------------------------------------------------------------------------------
# grids: algorithm-level tests
# ----------------------------------------------------------------------------------------------


def test_egrid_is_single_precision_accumulation():
    eg, maxen = grids.egrid_values(28.5)
    assert eg[0] == 0.0 and eg[1] == float(np.float32(0.001))
    printed = [
        "1.000000E-03",
        "2.000000E-03",
        "5.000000E-03",
        "1.000000E-02",
        "2.000000E-02",
        "5.000000E-02",
        "9.999999E-02",
        "2.000000E-01",
    ]
    assert [f"{float(np.float32(v)):.6E}" for v in eg[1:9]] == printed
    # 0.02 + 0.03 accumulated in float32 is 0.049999997, not float32(0.05)
    assert eg[6] == float(np.float32(np.float32(0.02) + np.float32(0.03)))
    assert np.all(np.diff(eg[1 : maxen + 1]) > 0) and eg[maxen] + 1e-4 <= 28.5
    de, top, bot = grids.emission_bins(eg, maxen)
    assert de[1] == pytest.approx(eg[1] + 0.5 * (eg[2] - eg[1]))
    assert top[maxen] == eg[maxen] and bot[1] == 0.0
    inner = slice(2, maxen)
    assert np.allclose(de[inner], 0.5 * (eg[3 : maxen + 1] - eg[1 : maxen - 1]), atol=1e-6)
    eg2, maxen2 = grids.egrid_values(28.5, segment=2)
    assert maxen2 > maxen


def test_emission_grid_batch_and_indices():
    from physics.hf.core.tensors import CaseBatch

    cb = CaseBatch(
        torch.tensor([26, 82]), torch.tensor([56, 208]), torch.tensor([1.0, 20.0], dtype=D)
    )
    g = grids.emission_grid(cb, None, elimit_mev=torch.tensor([10.0, 30.0], dtype=D))
    assert g.e_mev.shape == (2, grids.NUMEN + 1)
    assert not g.mask[:, 0].any() and int(g.maxen[0]) < int(g.maxen[1])
    assert torch.equal(g.e_mev[0, : int(g.maxen[0]) + 1], g.e_mev[1, : int(g.maxen[0]) + 1])
    with pytest.raises(ValueError):
        grids.emission_grid(cb, None)
    ebegin, lim = grids.charged_particle_begin(
        g.e_mev[1].numpy(), int(g.maxen[1]), 208, {t: 10.0 for t in range(2, 7)}, {}
    )
    assert ebegin[1] == 1 and g.e_mev[1, ebegin[2]] > lim[2] >= g.e_mev[1, ebegin[2] - 1]
    eend, high = grids.emission_end(
        g.e_mev[1].numpy(), int(g.maxen[1]), 25.0, {t: 5.0 for t in range(7)}, ebegin, {}
    )
    assert g.e_mev[1, eend[1]] > 20.0 >= g.e_mev[1, eend[1] - 1] and high >= eend[1]


def test_number_of_bins_incident_grid_and_flags():
    assert grids.number_of_bins(5.0) == 40
    assert grids.number_of_bins(20.0, nbins0=0) == 30 + int(70 * 400 / (400 + 3600))
    g = grids.incident_grid("n0-20.grid")
    assert g[0] == float(np.float32(1e-11)) and g[1] == float(np.float32(2.53e-8))
    assert abs(g[-1] - 20.0) < 1e-4 and all(b > a for a, b in zip(g, g[1:], strict=False))
    assert grids.incident_grid("n0-20.xyz") is None and grids.incident_grid("x0-20.grid") is None
    pg = grids.incident_grid("p10-30.grid")
    assert all(abs(e - round(e)) < 1e-4 for e in pg) and pg[0] >= 9.9
    fl = grids.incident_energy_flags(
        2.0, ewfc=5.0, eurr=0.0, epreeq=3.0, emulpre=20.0, eadd=0.0, eaddel=0.0
    )
    assert fl["flagwidth"] and not fl["flagpreeq"] and fl["flagadd"]


def test_kinematics_nonrelativistic_and_relativistic_agree_at_low_energy():
    c = talys_constants("exact")
    A = 59.0
    tar = 58.9332
    mn = c["parmass"][1]
    spec = tar / (tar + mn)
    red = tar * mn / (tar + mn)
    cm_nr, k_nr = grids.incident_kinematics(1.0, 1, tar, spec, red, flagrel=False)
    cm_r, k_r = grids.incident_kinematics(1.0, 1, tar, spec, red, flagrel=True)
    assert cm_nr == pytest.approx(A / (A + 1), rel=2e-3)
    # relativistic: invariant-mass kinetic energy and centre-of-mass momentum
    ma = mn + tar
    sq = math.sqrt(ma**2 + 2 * tar * 1.0 / c["amu"])
    assert cm_r == pytest.approx(c["amu"] * (sq - ma), rel=1e-6)
    t = 1.0 / c["amu"]
    k_ref = c["amu"] * tar * math.sqrt(t * (t + 2 * mn)) / sq / c["hbarc"]
    assert k_r == pytest.approx(k_ref, rel=1e-6)
    assert cm_r == pytest.approx(cm_nr, rel=1e-4) and k_r == pytest.approx(k_nr, rel=1e-3)
    assert k_nr == pytest.approx(math.sqrt(2 * c["amu"] * red * cm_nr) / c["hbarc"], rel=1e-6)


def test_excitation_energies_and_integrated_density():
    edis = np.array([0.0, 0.5, 1.2, 2.0, 2.4])
    ex, dex, maxex = grids.excitation_energies(edis, 4, 10.0, 40, 1)
    assert maxex == 44 and ex[4] == np.float32(2.4)
    assert np.allclose(dex[5:45], (10.0 - 2.4) / 40, rtol=1e-5)
    assert dex[0] == pytest.approx(0.25) and dex[2] == pytest.approx(0.5 * (2.0 - 0.5))
    assert np.allclose(np.cumsum(dex[5:45])[-1], 10.0 - 2.4, rtol=1e-6)
    ex_c, _, mx = grids.excitation_energies(edis, 4, 10.0, 40, 0, etotal_mev=10.0)
    assert ex_c[mx + 1] == pytest.approx(10.0)
    # levels at or above Exmax end the list with no continuum
    ex2, _, maxex2 = grids.excitation_energies(edis, 4, 1.5, 40, 1)
    assert maxex2 == 2 and len(ex2) == 4
    # deeper residuals get fewer bins; logarithmic spacing when requested
    assert grids.excitation_energies(edis, 4, 10.0, 40, 6)[2] == 4 + int(np.float32(0.8) * 40)
    assert grids.excitation_energies(edis, 4, 10.0, 40, 9)[2] == 4 + 20
    exl, dexl, _ = grids.excitation_energies(edis, 4, 10.0, 40, 1, flagequi=False)
    assert dexl[44] > dexl[5]
    # rhogrid: exact integral of an exponential density over the bin
    a, T = 3.0, 0.8
    lo, hi = torch.tensor(4.0, dtype=D), torch.tensor(4.5, dtype=D)
    mid = 0.5 * (lo + hi)
    rho = lambda e: a * torch.exp(e / T)  # noqa: E731
    got = grids.integrated_density(rho(lo), rho(mid), rho(hi), hi - lo)
    exact = a * T * (math.exp(4.5 / T) - math.exp(4.0 / T))
    assert float(got) == pytest.approx(exact, rel=1e-8)
    zero = torch.zeros(3, dtype=D, requires_grad=True)
    out = grids.integrated_density(zero, zero, zero, torch.ones(3, dtype=D))
    out.sum().backward()
    assert torch.isfinite(zero.grad).all() and float(out.sum()) == 0.0
    sp = torch.tensor([0.0, 4.0, 400.0])
    assert grids.max_spin_index(sp).tolist() == [4, 10, 40]


def test_residual_exmax_last_particle_wins():
    exmax0 = np.zeros((3, 4), np.float32)
    exmax = np.zeros((3, 4), np.float32)
    exmax0[0, 0] = exmax[0, 0] = 10.0
    S = np.zeros((3, 4, 7))
    S[0, 0, 1], S[0, 0, 2] = 7.0, 8.5
    e0, em = grids.residual_exmax(0, 0, exmax0, exmax, S, {t: t not in (1, 2) for t in range(7)})
    assert e0[0, 1] == np.float32(3.0) and e0[1, 0] == np.float32(1.5)
    q, thr = grids.residual_q_and_threshold(
        float(e0[1, 0]), 10.0, 7.0, 0.0, np.array([0.0, 0.3, 1.0]), 2, 0.98
    )
    assert q[0] == pytest.approx(7.0 + 1.5 - 10.0) and q[2] == pytest.approx(q[0] - 1.0)
    assert thr[2] == pytest.approx(-q[2] / 0.98) and thr.min() >= 0


# ----------------------------------------------------------------------------------------------
# gate A-grid against the TALYS dumps
# ----------------------------------------------------------------------------------------------

needs_dumps = pytest.mark.skipif(
    not (
        ref.available("preequilibrium")
        and ref.available("binary_population")
        and ref.available("raw_rows")
    ),
    reason="TALYS reference dumps not parsed (features/hf_reference)",
)

EJECTILE = {
    "gamma": 0,
    "neutron": 1,
    "proton": 2,
    "deuteron": 3,
    "triton": 4,
    "helium-3": 5,
    "alpha": 6,
}
PARZ_ = (0, 0, 1, 1, 1, 2, 2)
PARA_ = (0, 1, 1, 2, 3, 3, 4)


def _fmt(x) -> str:
    return f"{float(x):.6E}"


def _r(p, t):
    p, t = np.asarray(p, float), np.asarray(t, float)
    m = np.abs(t) > 0
    return np.abs(np.log(p[m] / t[m]))


@cache
def _levels(target: str, variant: str, z: int, a: int) -> np.ndarray:
    import polars as pl

    rows = (
        pl.read_parquet(ref.reference_dir() / "raw_rows.parquet")
        .filter(
            (pl.col("target") == target)
            & (pl.col("variant") == variant)
            & (pl.col("file") == f"levels{z:03d}{a:03d}.out")
        )
        .sort("row")
    )
    e = []
    for line in rows["line"].to_list():
        tok = line.split()
        if len(tok) >= 2 and tok[0].isdigit():
            e.append(float(tok[1]))
    return np.array(e)


def _float32_candidates(printed: float, reach: int = 16):
    c = np.float32(printed)
    out = {c}
    lo = hi = c
    for _ in range(reach):
        lo = np.nextafter(lo, np.float32(-np.inf))
        hi = np.nextafter(hi, np.float32(np.inf))
        out |= {lo, hi}
    return sorted(x for x in out if _fmt(x) == _fmt(printed))


@needs_dumps
def test_gate_a_grid_egrid_against_preequilibrium_spectra():
    """egrid as printed in preeq*.out (E-out column): exact string equality at TALYS's es15.6."""
    import polars as pl

    pe = pl.read_parquet(
        ref.reference_dir() / "preequilibrium.parquet",
        columns=["row", "column", "value", "variant", "target", "file", "block"],
    )
    pe = pe.filter(pl.col("column") == "E-out")
    eg, _ = grids.egrid_values(1000.0)
    n = mism = 0
    diffs = []
    for _, g in pe.group_by(["variant", "target", "file", "block"]):
        vals = g.sort("row")["value"].to_numpy()
        k0 = int(np.argmin(np.abs(eg[1:] - vals[0]))) + 1
        port = eg[k0 : k0 + len(vals)]
        assert len(port) == len(vals)
        diffs.append(np.abs(port - vals))
        mism += sum(_fmt(np.float32(p)) != _fmt(v) for p, v in zip(port, vals, strict=True))
        n += len(vals)
    d = np.concatenate(diffs)
    print(f"A-grid egrid: {n} points, string mismatches {mism}, max |dE| {d.max():.3e} MeV")
    assert n > 1000 and mism == 0
    assert d.max() <= 1e-6


@needs_dumps
def test_gate_a_grid_excitation_bins_against_binary_population():
    """Ex(nex) of every continuum bin and the printed bin size, per ejectile block of binE*.out.

    Injected: discrete level energies (levels*.out of the residual) and Exmax, which binE prints
    to 7 significant digits. TALYS holds Exmax as a float32 that the print rounds; the test
    injects each float32 consistent with the printed value and requires that one of them
    reproduces every printed Ex and the bin size exactly. The naive injection (printed value as
    is) is reported alongside: its error is the input's print rounding, not the port's.
    """
    import polars as pl

    bp = pl.read_parquet(
        ref.reference_dir() / "binary_population.parquet",
        columns=["row", "column", "value", "variant", "target", "file", "block"],
    )
    bp = bp.filter(pl.col("column") == "Ex")
    idx = pl.read_parquet(ref.reference_dir() / "block_index.parquet").filter(
        pl.col("family") == "binary_population"
    )
    man = ref.manifest()
    za = {(r.variant, r.target): (int(r.Z), int(r.A)) for r in man.itertuples()}
    ex_by = {
        k: g.sort("row")["value"].to_numpy()
        for k, g in bp.group_by(["variant", "target", "file", "block"])
    }
    blocks = exact = early = 0
    naive_r, scan_r = [], []
    for row in idx.iter_rows(named=True):
        key = (row["variant"], row["target"], row["file"], row["block"])
        if key not in ex_by:
            continue
        meta = json.loads(row["meta"])
        t = EJECTILE[meta["ejectile"]]
        z, a = za[(row["variant"], row["target"])]
        zr, ar = z - PARZ_[t], a + 1 - PARA_[t]
        edis = _levels(row["target"], row["variant"], zr, ar)
        if len(edis) == 0:
            continue
        nl = len(edis) - 1
        ex = ex_by[key]
        einc = float(meta["E-incident [MeV]"])
        nbins = grids.number_of_bins(einc)
        exmax_p = float(meta["maximum excitation energy [MeV]"])
        blocks += 1

        def run(e, edis=edis, nl=nl, nbins=nbins, aix=PARA_[t]):
            return grids.excitation_energies(edis, nl, e, nbins, aix)

        pex, pdex, maxex = run(exmax_p)
        if maxex <= nl:  # levels reach Exmax: no continuum, the list ends early
            early += 1
            assert len(ex) == maxex + 1, (key, len(ex), maxex)
            pairs = zip(pex[: maxex + 1], ex, strict=True)
            assert all(_fmt(np.float32(p)) == _fmt(v) for p, v in pairs)
            exact += 1
            continue
        assert maxex - nl == len(ex) - nl - 1, (key, maxex, len(ex))
        size = meta.get("continuum bin size [MeV]")
        naive_r.append(_r(pex[nl + 1 : maxex + 1], ex[nl + 1 :]))
        want = [_fmt(v) for v in ex[nl + 1 :]]
        hit = None
        for cand in _float32_candidates(exmax_p):
            cex, cdex, cmax = run(float(cand))
            if (
                cmax == maxex
                and [_fmt(np.float32(p)) for p in cex[nl + 1 : cmax + 1]] == want
                and (size is None or _fmt(np.float32(cdex[cmax])) == _fmt(float(size)))
            ):
                hit = cex
                break
        if hit is not None:
            exact += 1
            scan_r.append(_r(hit[nl + 1 : maxex + 1], ex[nl + 1 :]))
    nr = np.concatenate(naive_r)
    sr = np.concatenate(scan_r) if scan_r else np.array([np.inf])
    print(
        f"A-grid Ex: {blocks} blocks ({early} without continuum), exact as printed {exact}; "
        f"naive-Exmax r median {np.median(nr):.2e} p95 {np.percentile(nr, 95):.2e} "
        f"max {nr.max():.2e}; float32-consistent r median {np.median(sr):.2e} "
        f"p95 {np.percentile(sr, 95):.2e} max {sr.max():.2e}"
    )
    assert blocks > 100 and exact == blocks


@needs_dumps
def test_gate_a_grid_emission_ranges_against_transmission_files():
    """transmission_<p>.out lists egrid(ebegin..eend)/specmass at enincmax (inverseout.f90:116-118).
    eend must equal the port's emission_end from Etotal - S(0,0,type) = Exmax of that residual at
    the highest incident energy (binE meta), and every listed energy must be one egrid point
    scaled by a single constant (1/specmass) to print precision.

    The energies are read from the raw TALYS files in features/hf_reference/raw, not from
    block_index.parquet: the parsed per-block meta is misaligned for files with closed-channel
    blocks (reported to T0; e.g. Ni058 transmission_a.out parses 3.4 MeV twice and drops 0.3).
    """
    import re
    import tarfile

    import polars as pl

    raw = ref.reference_dir() / "raw"
    if not raw.is_dir():
        pytest.skip("raw TALYS outputs not present")
    binidx = pl.read_parquet(ref.reference_dir() / "block_index.parquet").filter(
        pl.col("family") == "binary_population"
    )
    energy_re = re.compile(r"energy \[MeV\]:\s*(\S+)")
    count_re = re.compile(r"number of energies:\s*(\d+)")
    checked, worst = 0, 0.0
    for tgz in sorted(raw.glob("*.tar.gz")):
        variant, target = tgz.name[: -len(".tar.gz")].split("__")
        b = binidx.filter((pl.col("variant") == variant) & (pl.col("target") == target))
        exmax_top: dict[int, tuple[float, float]] = {}
        for m in (json.loads(x) for x in b["meta"].to_list()):
            t = EJECTILE[m["ejectile"]]
            e = float(m["E-incident [MeV]"])
            if t not in exmax_top or e > exmax_top[t][0]:
                exmax_top[t] = (e, float(m["maximum excitation energy [MeV]"]))
        if not {0, 1} <= set(exmax_top):
            continue
        # The grid has to be the one TALYS actually built for this run, not an arbitrarily long
        # one: grid.f90:123 stops it at `Elimit = enincmax + S(0,0,k0) + targetE + 1.`, and
        # energies.f90:137 leaves `eend(type) = maxen - 1` whenever `Etotal - S(0,0,type)`
        # reaches past that top. That clip is dead weight for every channel but alpha on an
        # actinide, where S(0,0,alpha) is negative -- Am241 wants 31.04 MeV of outgoing alpha
        # off a grid that stops at 26 -- so a 1000 MeV grid used to sail past the clip and put
        # eend 7 points too high. Etotal is the gamma Exmax (S(0,0,gamma) = 0), so
        # S(0,0,k0) + targetE is gamma Exmax - neutron Exmax for these neutron-induced runs.
        enincmax = exmax_top[0][0]
        eg, maxen = grids.egrid_values(enincmax + (exmax_top[0][1] - exmax_top[1][1]) + 1.0)
        with tarfile.open(tgz) as tf:
            for member in tf.getmembers():
                name = member.name.rsplit("/", 1)[-1]
                if (
                    not (name.startswith("transmission_") and name.endswith(".out"))
                    or "inc" in name
                ):
                    continue
                t = PARSYM.index(name.split("_")[1][0])
                if t not in exmax_top:
                    continue
                text = tf.extractfile(member).read().decode(errors="replace")
                energies = np.array([float(x) for x in energy_re.findall(text)])
                nen = int(count_re.search(text).group(1))
                assert nen == len(energies), (target, name)
                eend, _ = grids.emission_end(
                    eg,
                    maxen,
                    exmax_top[t][1],
                    {k: 0.0 for k in range(7)},
                    {k: 1 for k in range(7)},
                    {},
                )
                ebegin = eend[t] - nen + 1
                assert ebegin >= 1, (variant, target, name)
                ratio = energies / eg[ebegin : eend[t] + 1]
                spread = float(np.abs(ratio / np.median(ratio) - 1).max())
                worst = max(worst, spread)
                assert spread < 2e-6, (variant, target, name, spread)
                checked += 1
    print(
        f"A-grid emission ranges: {checked} transmission files, max 1/specmass spread {worst:.2e}"
    )
    assert checked >= 20
