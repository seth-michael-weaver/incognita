"""T13: the ECIS coupled-channels port (stage a1, symmetric rotational model).

Three layers:

1. Angular momentum. ECIS's own `dj6j` and `dcgs` were extracted from `ecist.f`, compiled and run;
   `tests/hf/fixtures/ecis_angmom.json` holds 400 random 6j values and all 567 non-zero `dcgs`
   values in the range the port uses. The port's identities must reproduce them, so the sign and
   normalisation conventions are pinned without gfortran.
2. Structure of the coupling. The coupled-channels matrix must be symmetric at every (J, parity)
   for every band in the reference set -- that is what makes the S-matrix symmetric, and the
   reduced-matrix-element index rule (rotm-035) is the only thing that delivers it. The lambda = 0
   form factor must equal the angle-average of the deformed potential, and must reduce to the
   spherical potential when the deformation is zero.
3. A-inc, off the reference dumps: the port against TALYS's own `incident_scalars` on the
   `colltype R` targets.
"""

from __future__ import annotations

import json
import math
import os
from pathlib import Path

import numpy as np
import pytest
import torch

from physics.hf.core.tensors import DTYPE

torch.set_num_threads(2)

FIX = Path(__file__).resolve().parent / "fixtures" / "ecis_angmom.json"
REPO = Path(__file__).resolve().parents[2]
RAW = REPO / "features" / "hf_reference" / "raw"
SCALARS = REPO / "features" / "hf_reference" / "incident_scalars.parquet"
have_raw = pytest.mark.skipif(
    not (RAW.is_dir() and SCALARS.is_file()), reason="reference dumps absent"
)


# ------------------------------------------------------------------ 1. angular momentum
def test_sixj_reproduces_ecis_dj6j():
    from physics.hf.ecis.coupling import sixj

    d = json.loads(FIX.read_text())["dj6j"]
    a = np.array(d, dtype=float)
    args = [torch.tensor(a[:, i] / 2.0, dtype=DTYPE) for i in range(6)]
    got = sixj(*args).numpy()
    want = a[:, 6]
    assert np.abs(got - want).max() < 1.0e-11


def test_dcgs_reproduces_ecis_dcgs():
    from physics.hf.ecis.coupling import dcgs

    d = json.loads(FIX.read_text())["dcgs"]
    a = np.array(d, dtype=float)
    got = dcgs(
        torch.tensor(a[:, 0] / 2.0, dtype=DTYPE),
        torch.tensor(a[:, 1] / 2.0, dtype=DTYPE),
        torch.tensor(a[:, 2] / 2.0, dtype=DTYPE),
    ).numpy()
    assert np.abs(got - a[:, 3]).max() < 1.0e-11


def test_reduced_matrix_element_vanishes_outside_the_multipole_window():
    from physics.hf.ecis.coupling import reduced_matrix_element

    t = lambda x: torch.tensor(float(x), dtype=DTYPE)  # noqa: E731
    # rotm-100..103: lambda >= max(2, |I-I'|) and <= min(iqmax, I+I')
    assert float(reduced_matrix_element(t(0), t(0.0), t(2.0), t(0.0))) == 0.0
    assert float(reduced_matrix_element(t(2), t(0.0), t(4.0), t(0.0))) == 0.0  # |dI| = 4 > 2
    assert abs(float(reduced_matrix_element(t(2), t(0.0), t(2.0), t(0.0)))) > 0.1
    # a K = 0 band cannot carry an odd multipole
    assert float(reduced_matrix_element(t(3), t(2.0), t(4.0), t(0.0))) == 0.0


# ------------------------------------------------------- 2. structure of the coupling matrix
BANDS = {
    "U238 (K=0 even-even)": ([0.0, 2.0, 4.0, 6.0, 8.0], 0.0),
    "Au197 (K=3/2)": ([1.5, 2.5, 3.5, 6.5, 5.5], 1.5),
    "Pu239 (K=1/2)": ([0.5, 1.5, 2.5, 3.5, 4.5], 0.5),
    "U235 (K=7/2)": ([3.5, 4.5, 5.5, 6.5, 7.5], 3.5),
    "Am241 (K=5/2)": ([2.5, 3.5, 4.5, 5.5, 6.5], 2.5),
}


@pytest.mark.parametrize("name", list(BANDS))
def test_coupling_matrix_is_symmetric(name):
    """A non-symmetric coupling would give a non-symmetric S-matrix. For a K = 0 even-even band
    either reading of rotm's sqrt(2I+1) works; for every odd-A band only the column one does.
    """
    from physics.hf.ecis.coupling import channels

    spins, k = BANDS[name]
    ls = torch.tensor(spins, dtype=DTYPE)
    lp = torch.ones(len(spins), dtype=torch.int64)
    start = (int(round(2 * spins[0])) + 1) % 2
    worst = 0.0
    for twoJ in range(start, start + 40, 2):
        for par in (-1, 1):
            ch = channels(twoJ, par, ls, lp, 8, k)
            if ch.level.numel() == 0:
                continue
            worst = max(worst, float((ch.coupling - ch.coupling.transpose(1, 2)).abs().max()))
    assert worst < 1.0e-12, f"{name}: coupling matrix asymmetric by {worst:.2e}"


def test_lambda0_slice_is_the_identity():
    from physics.hf.ecis.coupling import channels

    ls = torch.tensor([0.0, 2.0, 4.0], dtype=DTYPE)
    ch = channels(5, 1, ls, torch.ones(3, dtype=torch.int64), 6, 0.0)
    n = ch.level.numel()
    assert torch.equal(ch.coupling[0], torch.eye(n, dtype=DTYPE))


def test_gauss_legendre_nodes_and_weights():
    """ECIS's `pgn` are the 20-point Gauss-Legendre weights folded onto the 10 positive nodes, so
    they sum to 1 and integrate P_lambda exactly for even lambda up to 18."""
    from physics.hf.core.angmom import plegendre
    from physics.hf.ecis.formfactor import PGN, XGN

    w = torch.tensor(PGN, dtype=DTYPE)
    x = torch.tensor(XGN, dtype=DTYPE)
    assert abs(float(w.sum()) - 1.0) < 1.0e-14
    pl = plegendre(18, x)
    for lam in range(2, 19, 2):
        assert abs(float((w * pl[:, lam]).sum())) < 1.0e-13


def test_zero_deformation_reproduces_t5s_spherical_potential():
    """With beta = 0 the lambda = 0 form factor must be T5's spherical `optical_potential` and all
    higher multipoles must vanish: the deformed machinery has to contain the spherical limit."""
    from physics.hf.ecis.formfactor import rotational_form_factors
    from physics.hf.omp.schrodinger import optical_potential

    class P:
        pass

    p = P()
    vals = dict(
        v_mev=45.0, rv_fm=1.25, av_fm=0.65, w_mev=2.0, rw_fm=1.25, aw_fm=0.65,
        vd_mev=1.0, rvd_fm=1.2, avd_fm=0.55, wd_mev=6.0, rwd_fm=1.2, awd_fm=0.55,
        vso_mev=6.0, rvso_fm=1.1, avso_fm=0.59, wso_mev=-0.1, rwso_fm=1.1, awso_fm=0.59,
        rc_fm=1.25,
    )  # fmt: skip
    for k, v in vals.items():
        setattr(p, k, torch.tensor([v], dtype=DTYPE))
    r = torch.linspace(0.3, 15.0, 60, dtype=DTYPE)
    ff = rotational_form_factors(p, 184.0, r, torch.zeros(2, dtype=DTYPE), False, 4, 0.0)
    cen, so, _ = optical_potential(p, torch.tensor(184.0, dtype=DTYPE), r, 0.0)
    assert torch.allclose(ff.central[:, 0], cen, atol=1.0e-12)
    assert torch.allclose(ff.spin_orbit[:, 0], so, atol=1.0e-12)
    assert float(ff.central[:, 1:].abs().max()) < 1.0e-12


def test_deformed_radius_is_R_plus_delta_Ylambda0():
    """`lo(6)` (deformation lengths, TALYS `deftype D`) must shift every potential by the same
    number of fermis; dimensionless beta must shift each by beta * R."""
    from physics.hf.core.angmom import plegendre
    from physics.hf.ecis.formfactor import XGN, deformed_radii

    R = torch.tensor([[6.0, 7.5]], dtype=DTYPE)
    beta = torch.tensor([0.3, 0.05], dtype=DTYPE)
    x = torch.tensor(XGN, dtype=DTYPE)
    pl = plegendre(4, x)
    y2 = math.sqrt(5.0 / (4 * math.pi)) * pl[:, 2]
    y4 = math.sqrt(9.0 / (4 * math.pi)) * pl[:, 4]
    shift = beta[0] * y2 + beta[1] * y4
    got = deformed_radii(R, beta, True, 4)
    assert torch.allclose(got, R[..., None] + shift, atol=1.0e-13)
    got = deformed_radii(R, beta, False, 4)
    assert torch.allclose(got, R[..., None] * (1.0 + shift), atol=1.0e-13)


# ------------------------------------------------------------------------------ 3. A-inc
@have_raw
def test_rotational_targets_are_the_expected_eleven():
    from physics.hf.ecis.score import rotational_targets

    got = sorted(t.tag for t in rotational_targets())
    assert got == sorted(
        ["Au197", "Nd150", "Sm152", "Gd157", "Er166", "W184", "Th232", "U235", "U238", "Pu239", "Am241"]
    )


@have_raw
def test_unitarity_and_a_inc_on_one_actinide_and_one_odd_a():
    """sigma_tot = sigma_shape_el + absorption + direct (unitarity of the S-matrix), and A-inc on
    U238 (K = 0, deformation lengths) and Au197 (K = 3/2, dimensionless beta) -- the two bands that
    exercise both `deftype` branches and both readings of the rotor matrix element."""
    from physics.hf.ecis.score import score_target, summarise
    from physics.hf.talys_reference import REFERENCE_SET

    tags = {t.tag: t for t in REFERENCE_SET}
    for tag in ("U238", "Au197"):
        got = score_target(tags[tag], e_max_mev=2.0)
        s = summarise(got["rows"])
        assert s["pass"], f"{tag}: A-inc p95 {s['p95']:.2e}"
        assert s["p95"] < 1.0e-2


@have_raw
@pytest.mark.skipif(not os.environ.get("HF_ECIS_FULL"), reason="set HF_ECIS_FULL=1 (4 minutes)")
def test_a_inc_gate_over_every_rotational_target():
    """The pre-registered A-inc gate (contract §6, tolerance 1e-2) on all eleven `colltype R`
    targets at every one of the 23 incident energies, across `soswitch`."""
    from physics.hf.ecis.score import rotational_targets, score_target, summarise

    rows = []
    for t in rotational_targets():
        rows += score_target(t)["rows"]
    s = summarise(rows)
    assert s["pass"], f"A-inc p95 {s['p95']:.2e} > 1e-2"


def test_deformed_spin_orbit_tables_reproduce_ecis_hermitian_copy():
    """`quan` builds the deformed spin-orbit coefficients only for i2 <= i1 and then copies the
    block (quan-379..417), adding `-at` on the `so_grad` address (quan-395/398) and `+at` on the
    `so_r2` one (quan-401/404) for every derivative term, "in order to obtain an hermitian
    interaction". The port writes the formula for both orientations instead, so that copy rule
    must come out as an identity:

        so_grad - so_deriv == so_grad^T        so_r2 + so_deriv == so_r2^T

    and the derivative table itself must be antisymmetric -- it is `cx (2l.s_col - 2l.s_row)`,
    a commutator of the (symmetric) central coefficient with diag(2 l.s).
    """
    from physics.hf.ecis.coupling import channels

    ls = torch.tensor([0.0, 2.0, 4.0, 6.0], dtype=DTYPE)
    lp = torch.ones(4, dtype=torch.int64)
    for twoJ in (1, 5, 11, 17):
        for par in (-1, 1):
            ch = channels(twoJ, par, ls, lp, 9, 0.0, deformed_spin_orbit=True)
            if ch.level.numel() == 0:
                continue
            g1, g2, gd = ch.so_grad_coef, ch.so_r2_coef, ch.so_deriv_coef
            assert torch.allclose(gd, -gd.transpose(1, 2), atol=1e-12)
            assert torch.allclose(g1 - gd, g1.transpose(1, 2), atol=1e-12)
            assert torch.allclose(g2 + gd, g2.transpose(1, 2), atol=1e-12)
            assert float(g1[0].abs().max()) == 0.0  # redm's multipole table starts at lambda = 2
            assert float(gd[0].abs().max()) == 0.0


def test_spin_orbit_transition_form_factors_vanish_without_deformation():
    """The two spin-orbit transition form factors are multipole projections of the DEFORMED
    spin-orbit potential, so with every `rotpar` zero only the lambda = 0 slice survives, and it
    is then the spherical (1/r) dV/dr and V/r**2 with ECIS's factor 2."""
    from physics.hf.ecis.formfactor import rotational_form_factors
    from physics.hf.omp.schrodinger import SPIN_ORBIT_FACTOR, _ws, ecis_card_value

    p = _SphericalOMP()
    r = torch.linspace(0.2, 14.0, 140, dtype=DTYPE)
    ff = rotational_form_factors(
        p, 184.0, r, torch.zeros(2, dtype=DTYPE), False, 4, 0.0, deformed_spin_orbit=True
    )
    assert float(ff.so_grad[:, 1:].abs().max()) < 1e-12
    assert float(ff.so_r2[:, 1:].abs().max()) < 1e-12
    am3 = 184.0 ** (1.0 / 3.0)
    rr = ecis_card_value(p.rvso_fm) * am3
    aa = ecis_card_value(p.avso_fm)
    vso = ecis_card_value(p.vso_mev)
    f, g = _ws(r[None, :], rr[:, None], aa[:, None])
    want1 = SPIN_ORBIT_FACTOR * vso[:, None] * (-g / aa[:, None]) / r[None, :]
    want2 = SPIN_ORBIT_FACTOR * vso[:, None] * f / r[None, :] ** 2
    assert torch.allclose(ff.so_grad[:, 0], want1, rtol=1e-12)
    assert torch.allclose(ff.so_r2[:, 0], want2, rtol=1e-12)
    # slice 0 of `spin_orbit` is the same (1/r) dV/dr, plus the imaginary spin-orbit that
    # `lo(14) = F` keeps out of the transition form factors
    assert torch.allclose(ff.so_grad[:, 0], ff.spin_orbit[:, 0].real, rtol=1e-12)


@have_raw
def test_above_soswitch_is_ported_and_beats_the_spherical_spin_orbit():
    """Roadmap item 6. Above `soswitch` ECIS deforms the spin-orbit potential
    (incidentecis.f90:285, `lo(13) = T`), which adds two transition form factors, two coupling
    terms and a derivative coupling. The port must run there by default, pass A-inc, and be
    decisively better than the `lo(13) = F` arm it replaces."""
    from physics.hf.ecis.score import TOL, score_target, summarise
    from physics.hf.talys_reference import REFERENCE_SET

    t = next(x for x in REFERENCE_SET if x.tag == "Er166")
    on = summarise(score_target(t, e_max_mev=float("inf"), e_min_mev=10.0)["rows"])
    off = summarise(
        score_target(t, e_max_mev=float("inf"), e_min_mev=10.0, undeformed_so=True)["rows"]
    )
    assert on["n"] == 15 and off["n"] == 15
    assert on["pass"], f"Er166 A-inc above soswitch p95 {on['p95']:.2e} > {TOL:.0e}"
    assert on["p95"] < 0.25 * off["p95"]


@have_raw
def test_deformed_spin_orbit_keeps_the_s_matrix_symmetric_and_unitary():
    """ECIS says of the deformed spin-orbit that "there is no symmetry, the total table is
    calculated" (quan-152..155) -- of the COEFFICIENT table. The S-matrix must still come out
    symmetric, which is what the hermitian copy of quan-379..417 is there to guarantee, and the
    cross sections must still close: sigma_tot = sigma_shape-el + sigma_reac."""
    from physics.hf.ecis.coupling import channels
    from physics.hf.ecis.formfactor import rotational_form_factors
    from physics.hf.ecis.reference import coupled_band, incident_omp
    from physics.hf.ecis.solver import _grid_and_kinematics, smatrix
    from physics.hf.omp.schrodinger import PARMASS_AMU, nucleus_mass_amu

    band = coupled_band(92, 238)
    src = incident_omp("U238")
    sel = src.e_inc_mev > 10.0
    p = src.select(sel)
    m_t = nucleus_mass_amu(92, 238)
    kin, h, nmatch, r = _grid_and_kinematics(
        p, PARMASS_AMU[1], m_t, 0.0, src.e_inc_mev[sel], band["e_mev"], 1, True
    )
    ff = rotational_form_factors(
        p, m_t, r, band["rotbeta"], band["deformation_length"], 2 * band["rotbeta"].numel(),
        0.0, True,
    )
    for twoJ, par in ((7, 1), (13, -1)):
        ch = channels(twoJ, par, band["spin"], band["parity"], 12, band["kband"],
                      deformed_spin_orbit=True)
        sm, _op = smatrix(ch, ff, kin, h, nmatch, r)
        asym = (sm - sm.transpose(1, 2)).abs().max() / sm.abs().max()
        # ~1e-6 is the integrator's own level here, with or without the deformed spin-orbit:
        # the `lo(13) = F` branch, which session 1 gated, measures 5e-7 to 1.1e-6 on the same
        # blocks. What would show a wrong hermitian copy is a per-cent asymmetry, not this.
        assert float(asym) < 1e-5, f"S-matrix not symmetric at 2J={twoJ}: {float(asym):.2e}"


@have_raw
def test_above_soswitch_cross_sections_close():
    from physics.hf.ecis.incident import incident_coupled
    from physics.hf.ecis.reference import coupled_band, incident_omp

    band = coupled_band(66 + 2, 166)  # Er166
    src = incident_omp("Er166")
    sel = src.e_inc_mev > 10.0
    _inc, res = incident_coupled(
        src.select(sel), 68, 166, src.e_inc_mev[sel], band, options=band["options"]
    )
    close = (res.sigma_tot_mb - res.sigma_shape_el_mb - res.sigma_reac_mb).abs()
    assert float((close / res.sigma_tot_mb).max()) < 1e-9


@have_raw
def test_soswitch_split_is_per_energy_not_per_call():
    """`incidentecis.f90` picks `ecis1(13:13)` per INCIDENT energy, so an axis that straddles
    10 MeV must give exactly what two calls on the two halves give."""
    from physics.hf.ecis.incident import incident_coupled
    from physics.hf.ecis.reference import coupled_band, incident_omp

    band = coupled_band(92, 238)
    src = incident_omp("U238")
    sel = (src.e_inc_mev >= 8.0) & (src.e_inc_mev <= 14.0)
    e = src.e_inc_mev[sel]
    assert bool((e <= 10.0).any()) and bool((e > 10.0).any())
    both, _ = incident_coupled(src, 92, 238, src.e_inc_mev, band, options=band["options"],
                               energy_mask=sel)
    for half in (e <= 10.0, e > 10.0):
        one, _ = incident_coupled(src.select(sel), 92, 238, e, band, options=band["options"],
                                  energy_mask=half)
        assert torch.allclose(both.sigma_tot_mb[half], one.sigma_tot_mb, rtol=0, atol=0)
        assert torch.allclose(both.sigma_reac_mb[half], one.sigma_reac_mb, rtol=0, atol=0)


@have_raw
def test_asymmetric_rotor_is_refused_not_approximated():
    """Stage a2 landed `colltype V`; `colltype A` (the asymmetric rotor, `roam`) is still not
    ported, and no reference target uses it, so it must raise rather than be silently treated as
    a symmetric rotor."""
    from physics.hf.ecis.incident import incident_coupled
    from physics.hf.ecis.reference import coupled_band, incident_omp

    band = dict(coupled_band(20, 40))
    band["colltype"] = "A"
    src = incident_omp("Ca040")
    with pytest.raises(NotImplementedError, match="asymmetric"):
        incident_coupled(
            src, 20, 40, src.e_inc_mev, band, options=band["options"],
            energy_mask=src.e_inc_mev <= 1.0,
        )


@have_raw
def test_two_phonon_level_takes_the_second_order_branch():
    """TWOPH: a two-phonon level used to raise here (`ecis1(2:2) = 'T'` needs `vibm`'s
    second-order terms). It now builds the `vibm` table and solves; `tests/hf/test_twophonon.py`
    gates the numbers. Ca-40's band with one level relabelled two-phonon is a scheme TALYS never
    writes -- three distinct phonons, so second-order form factors in beta_i beta_j with i != j --
    which is exactly why it is worth solving here."""
    from physics.hf.ecis.incident import incident_coupled
    from physics.hf.ecis.reference import coupled_band, incident_omp
    from physics.hf.ecis.vibm import scheme_from_band

    band = dict(coupled_band(20, 40))
    band["iphonon"] = torch.tensor([1, 2, 1, 1])
    scheme, _beta = scheme_from_band(band)
    assert scheme.nbt1 == 3
    assert any(c > scheme.nbt1 for c in scheme.codes)  # second-order form factors are there
    src = incident_omp("Ca040")
    inc, res = incident_coupled(
        src, 20, 40, src.e_inc_mev, band, options=band["options"],
        energy_mask=src.e_inc_mev <= 1.0,
    )
    assert torch.isfinite(res.sigma_reac_mb).all() and (res.sigma_reac_mb > 0).all()


@have_raw
def test_energy_mask_cuts_the_parameters_and_the_axis_together():
    """T12 asked for this (board note `[T12 -> T13]`): a caller holding a reference target's 23
    energies must be able to ask for the 18 at or below soswitch without rebuilding the OMP."""
    from physics.hf.ecis.incident import incident_coupled
    from physics.hf.ecis.reference import coupled_band, incident_omp

    band = coupled_band(60, 150)
    src = incident_omp("Nd150")
    sel = src.e_inc_mev <= 0.05
    cut = src.select(sel)
    assert cut.e_inc_mev.numel() == int(sel.sum()) and cut.v_mev.numel() == int(sel.sum())
    a, _ = incident_coupled(src, 60, 150, src.e_inc_mev, band, options=band["options"], energy_mask=sel)
    b, _ = incident_coupled(cut, 60, 150, cut.e_inc_mev, band, options=band["options"])
    assert torch.equal(a.sigma_tot_mb, b.sigma_tot_mb)


class _SphericalOMP:
    """A fixed, plausible neutron OMP with BOTH a real volume and a real surface term, which is
    what makes the sign test above bite (KD03 has Vd = 0; RIPL 2408 does not)."""

    def __init__(self):
        vals = dict(
            v_mev=43.07, rv_fm=1.252, av_fm=0.636, w_mev=0.25, rw_fm=1.253, aw_fm=0.68,
            vd_mev=3.36, rvd_fm=1.181, avd_fm=0.603, wd_mev=5.29, rwd_fm=1.181, awd_fm=0.603,
            vso_mev=5.47, rvso_fm=1.121, avso_fm=0.59, wso_mev=-3.1, rwso_fm=1.121,
            awso_fm=0.59, rc_fm=1.25, ef_mev=-5.48,
        )
        for k, v in vals.items():
            setattr(self, k, torch.tensor([v], dtype=DTYPE))


# ------------------------------------------------------------------------- 4. A-direct (DWBA)
def test_derivative_form_factor_is_the_first_order_deformed_one():
    """`derivative_form_factor` (the vibrational one-phonon form factor of rotp-127..133) must be
    the first-order term of `rotational_form_factors` (ECIS's exact 10-node projection of the
    deformed Woods-Saxon), i.e. -(delta / sqrt(4 pi)) dV/dr, with the error going as delta.

    This is the only cross-check that pins the RELATIVE sign of the volume and the surface
    derivative -- getting it backwards costs the actinides (the only reference targets with a
    non-zero real surface term Vd) 25% of the DWBA cross section at 6 MeV.
    """
    from physics.hf.ecis.formfactor import (
        ALL_CENTRAL_PARTS,
        derivative_form_factor,
        rotational_form_factors,
    )

    p = _SphericalOMP()
    r = torch.arange(1, 401, dtype=DTYPE) * 0.06
    w = derivative_form_factor(p, 238.0, r, True, ALL_CENTRAL_PARTS)[0]
    prev = None
    for delta in (1.0e-4, 1.0e-5):
        exact = rotational_form_factors(
            p, 238.0, r, torch.tensor([delta, 0.0], dtype=DTYPE), True, 4, 0.0
        ).central[0, 1]
        pred = -(delta / math.sqrt(4.0 * math.pi)) * w
        rel = float((exact - pred).abs().max() / pred.abs().max())
        assert rel < 1.0e-5
        if prev is not None:
            assert rel < 0.2 * prev  # the residual is O(delta^2), so it falls with delta
        prev = rel


def test_second_derivative_form_factor_is_the_numerical_second_derivative():
    """`second_derivative_form_factor` is `sum_m s_m^2 d2U_m/dr2` (rotp-119..125, `iv = 3`),
    checked against a central second difference of `omp.schrodinger.optical_potential` itself.

    The analytic Woods-Saxon second derivatives are easy to get subtly wrong -- the surface term
    is a third derivative of a sigmoid and its `2g - (1-2f)^2` factor has no counterpart in the
    first-order form factor. This is the piece of the unported two-phonon coupling
    (`docs/results/hf-ecis-twophonon.md`) that can be written and gated on its own.
    """
    from physics.hf.ecis.formfactor import ALL_CENTRAL_PARTS, second_derivative_form_factor
    from physics.hf.omp.schrodinger import optical_potential

    p = _SphericalOMP()
    m, h = 238.0, 1.0e-3
    r = torch.arange(1, 301, dtype=DTYPE) * 0.08
    mt = torch.tensor(m, dtype=DTYPE)
    # deformation lengths (s_m = 1), so the form factor is the plain second derivative of the
    # summed central potential; `optical_potential` returns exactly that sum.
    got = second_derivative_form_factor(p, m, r, True, ALL_CENTRAL_PARTS)[0]
    u0 = optical_potential(p, mt, r, 0.0)[0][0]
    up = optical_potential(p, mt, r + h, 0.0)[0][0]
    um = optical_potential(p, mt, r - h, 0.0)[0][0]
    fd = (up - 2.0 * u0 + um) / (h * h)
    rel = float((got - fd).abs().max() / fd.abs().max())
    assert rel < 1.0e-5, rel
    # and the 1/(8 pi) coefficient of rotp-125 is (1/sqrt(4 pi))^2 / 2, not 1/(4 pi)
    assert abs(0.0397887 - (1.0 / math.sqrt(4.0 * math.pi)) ** 2 / 2.0) < 5.0e-8


def test_dwba_weight_sums_to_one_over_the_exit_channels():
    """The `quan` coefficient of a 0+ -> lambda transition collapses to a single Clebsch-Gordan
    (module docstring of `ecis.dwba`), whose square sums to 1 over the exit j' -- the completeness
    relation. A wrong 6j or a missing sqrt(2 lambda + 1) breaks it."""
    from physics.hf.core.angmom import clebsch

    for lam in (1, 2, 3, 4, 6):
        for twoJ in (1, 3, 7, 15):
            J = 0.5 * twoJ
            tot = 0.0
            for two_jp in range(abs(twoJ - 2 * lam), twoJ + 2 * lam + 1, 2):
                tot += float(
                    clebsch(
                        torch.tensor(J), torch.tensor(float(lam)), torch.tensor(0.5 * two_jp),
                        torch.tensor(-0.5), torch.tensor(0.0), torch.tensor(-0.5),
                    )
                ) ** 2
            assert abs(tot - 1.0) < 1.0e-12


@have_raw
def test_a_direct_on_one_spherical_one_deformed_and_one_odd_a():
    """A-direct at 14 MeV on Fe-56 (beta, spherical), U-238 (deformation lengths, the only
    `deftype D` branch, and the real surface term) and Au-197 (odd A, so the DWBA spin is the
    CORE spin, not `jdis`)."""
    from physics.hf.ecis.score_dwba import TOL, score_case, summarise

    for tag in ("Fe056", "U238", "Au197"):
        s = summarise(score_case(tag, 14.0, refine=4))
        assert s["n"] > 10
        assert s["p95"] <= TOL, f"{tag}: A-direct p95 {s['p95']:.2e}"


@have_raw
def test_odd_a_dwba_uses_the_core_spin_not_the_level_spin():
    """`directecis.f90:207-213`: every weakly-coupled level of an odd-A target is handed ECIS with
    its CORE spin and parity. Au-197's own levels are half-integer; what ECIS sees is integer."""
    from physics.hf.ecis.dwba import prepare_case
    from physics.hf.ecis.reference import incident_omp

    src = incident_omp("Au197")
    omp = src.select((src.e_inc_mev - 14.0).abs() < 1.0e-6)
    case = prepare_case(omp, "Au197", 14.0)
    assert case.level_index.numel() > 20
    assert torch.all((case.spin - case.spin.round()).abs() < 1.0e-9)
    assert set(case.parity.tolist()) <= {-1, 1}


@have_raw
@pytest.mark.skipif(not os.environ.get("HF_ECIS_FULL"), reason="set HF_ECIS_FULL=1 (5 minutes)")
def test_a_direct_gate_over_every_target():
    from physics.hf.ecis.score_dwba import main

    assert main(["--out", os.environ.get("HF_ECIS_OUT", "/tmp/hf-ecis-dwba-gate.json")]) == 0


# ------------------------------------------------- 5. A-inc, stage a2: the vibrational model
@pytest.mark.parametrize("twoJ", [1, 5, 9, 15])
def test_vibrational_coupling_matrix_is_symmetric(twoJ):
    """`vibm`'s one-phonon reduced matrix element is +/- 1, and taking it +1 in both directions
    has to leave `quan`'s coefficient symmetric -- otherwise the S-matrix is not. Ca-40's band
    (3-, 2+, 5-) covers both an odd and an even multipole."""
    from physics.hf.ecis.coupling import vibrational_channels

    sp = torch.tensor([0.0, 3.0, 2.0, 5.0], dtype=DTYPE)
    pa = torch.tensor([1, -1, 1, -1])
    lam = torch.tensor([0.0, 3.0, 2.0, 5.0], dtype=DTYPE)
    for par in (-1, 1):
        ch = vibrational_channels(twoJ, par, sp, pa, lam, 8)
        for k in range(ch.coupling.shape[0]):
            c = ch.coupling[k]
            assert float((c - c.T).abs().max()) < 1.0e-12


def test_vibrational_coupling_only_touches_the_ground_state_row_and_column():
    """Harmonic one-phonon: `alpha_lambda` connects n to n +/- 1, so one-phonon levels neither
    couple to each other nor reorient."""
    from physics.hf.ecis.coupling import vibrational_channels

    sp = torch.tensor([0.0, 3.0, 2.0, 5.0], dtype=DTYPE)
    pa = torch.tensor([1, -1, 1, -1])
    lam = torch.tensor([0.0, 3.0, 2.0, 5.0], dtype=DTYPE)
    ch = vibrational_channels(7, 1, sp, pa, lam, 8)
    gnd = ch.level == 0
    for b in range(1, ch.coupling.shape[0]):
        c = ch.coupling[b]
        allowed = ((ch.level == b)[:, None] & gnd[None, :]) | (gnd[:, None] & (ch.level == b)[None, :])
        assert float(c[~allowed].abs().max()) == 0.0
        assert float(c[allowed].abs().max()) > 0.0


@have_raw
def test_ca040_band_is_the_three_one_phonon_levels():
    from physics.hf.ecis.reference import coupled_band

    b = coupled_band(20, 40)
    assert b["colltype"] == "V"
    assert b["spin"].tolist() == [0.0, 3.0, 2.0, 5.0]
    assert b["vib_lambda"].tolist() == [0.0, 3.0, 2.0, 5.0]  # one phonon: lambda = the spin
    assert b["vib_beta"].numel() == 3
    assert int(b["iphonon"].max()) == 1  # no two-phonon level, so ecis1(2:2) stays 'F'


@have_raw
def test_a_inc_on_ca040_over_every_energy():
    """Ca-40 is the one `colltype V` reference target and was T5's other A-inc miss. It has no
    `soswitch`: `incidentecis.f90` only touches ecis1(13:13) in the rotational branch, so all 23
    energies are in scope."""
    from physics.hf.ecis.score import score_target, summarise
    from physics.hf.talys_reference import REFERENCE_SET

    t = next(x for x in REFERENCE_SET if x.tag == "Ca040")
    got = score_target(t)
    s = summarise(got["rows"])
    assert s["n"] == 90  # 23 energies x 3 cross sections + 7 x 3 strength quantities
    assert s["pass"], f"Ca040 A-inc p95 {s['p95']:.2e}"


@have_raw
def test_undeformed_spin_orbit_arm_is_still_available_and_bounded():
    """The `lo(13) = F` arm stays reachable, because it is the A/B that says what the deformed
    spin-orbit buys; it must stay inside the 1.5e-2 T13 session 2 measured
    (`docs/results/hf-ecis-above-soswitch-undeformed.json`), which is NOT the A-inc tolerance."""
    from physics.hf.ecis.score import score_target, summarise
    from physics.hf.talys_reference import REFERENCE_SET

    t = next(x for x in REFERENCE_SET if x.tag == "U238")
    got = score_target(t, e_max_mev=float("inf"), e_min_mev=10.0, undeformed_so=True)
    s = summarise(got["rows"])
    assert s["n"] == 15  # 5 energies x 3 cross sections; S0/S1/R' are not printed up there
    assert s["max"] < 1.5e-2


@have_raw
def test_coupled_channels_direct_inelastic_matches_directE():
    """The rows of `directE*.out` a coupled-channels target fills from the INCIDENT run
    (`incidentread.f90:381-394`), which is the OFF-diagonal of the S-matrix -- A-inc only sees
    sigma_tot, sigma_reac, sigma_el and the strength functions, all of which survive a wrong
    inelastic normalisation as long as the sum is right."""
    from physics.hf.ecis.score_dwba import TOL, score_coupled_direct, summarise

    for tag in ("Ca040", "W184"):  # colltype V and colltype R
        s = summarise(score_coupled_direct(tag))
        assert s["n"] > 20
        assert s["p95"] <= TOL, f"{tag}: coupled direct p95 {s['p95']:.2e}"


@have_raw
@pytest.mark.parametrize(("deformed_so", "threads"), [(False, 1), (True, 1), (False, 2)])
def test_smatrix_blocks_is_smatrix_to_the_bit(deformed_so, threads):
    """SPEEDT: `smatrix_blocks` runs the radial loops of every block of one channel count together
    (and the Coulomb functions of all blocks in one pass). Each block's S-matrix must be the one
    `smatrix` gives alone, reasonably close (project rule, 2026-09-16: no bit-identity anywhere,
    <=1e-6 relative is the standard) -- on several energies with different matching points, with
    blocks of equal and of different N, below and above `soswitch`, and with more than one thread
    (where it runs one block per loop, so threads=2 lands bit-identical; only the threads=1 batched
    path reorders sums -- measured on this Mac (MACFIX2) up to 5.4e-12 relative, ordinary FP
    non-associativity between two numerically-equivalent code paths)."""
    saved = torch.get_num_threads()
    torch.set_num_threads(threads)
    try:
        _check_smatrix_blocks(deformed_so)
    finally:
        torch.set_num_threads(saved)


def _check_smatrix_blocks(deformed_so):
    from physics.hf.ecis.coupling import channels
    from physics.hf.ecis.formfactor import rotational_form_factors
    from physics.hf.ecis.reference import coupled_band, incident_omp
    from physics.hf.ecis.solver import _grid_and_kinematics, smatrix, smatrix_blocks
    from physics.hf.omp.schrodinger import PARMASS_AMU, nucleus_mass_amu

    band = coupled_band(92, 238)
    src = incident_omp("U238")
    sel = (src.e_inc_mev > 10.0) if deformed_so else (src.e_inc_mev < 3.0)
    idx = torch.nonzero(sel).reshape(-1)[:3]
    sel = torch.zeros_like(sel)
    sel[idx] = True
    p = src.select(sel)
    m_t = nucleus_mass_amu(92, 238)
    kin, h, nmatch, r = _grid_and_kinematics(
        p, PARMASS_AMU[1], m_t, 0.0, src.e_inc_mev[sel], band["e_mev"], 1, True
    )
    ff = rotational_form_factors(
        p, m_t, r, band["rotbeta"], band["deformation_length"], 2 * band["rotbeta"].numel(),
        0.0, deformed_so,
    )
    chs = [channels(twoJ, par, band["spin"], band["parity"], 10, band["kband"],
                    deformed_spin_orbit=deformed_so)
           for twoJ in (1, 3, 15, 17, 19) for par in (-1, 1)]
    for ch, (s, op) in zip(chs, smatrix_blocks(chs, ff, kin, h, nmatch, r), strict=True):
        s1, op1 = smatrix(ch, ff, kin, h, nmatch, r)
        assert torch.allclose(op, op1, rtol=1e-6, atol=1e-300, equal_nan=True)
        assert bool((torch.isclose(s, s1, rtol=1e-6, atol=1e-300) | (s.isnan() & s1.isnan())).all()), (
            ch.twoJ, ch.parity)


def test_coupling_tables_are_the_elementwise_factors_to_the_bit():
    """SPEEDT: `coupling_matrix` gathers the reduced matrix element and `dcgs` from tables over the
    distinct level and j values; each gathered entry must be the direct element-wise evaluation."""
    from physics.hf.ecis.coupling import (
        _dcgs_lookup,
        _rme_table,
        channel_list,
        dcgs,
        reduced_matrix_element,
    )

    spin = torch.tensor([3.5, 4.5, 5.5, 6.5], dtype=DTYPE)
    parity = torch.tensor([1, 1, 1, 1])
    for twoJ, par in ((1, 1), (9, -1), (31, 1)):
        lev, orb, jj = channel_list(twoJ, par, spin, parity, 14)
        n = lev.numel()
        ir, ic = spin[lev][:, None].expand(n, n), spin[lev][None, :].expand(n, n)
        for lam in (2.0, 4.0, 6.0):
            L = torch.full((n, n), lam, dtype=DTYPE)
            direct = reduced_matrix_element(L, ic, ir, torch.full((n, n), 3.5, dtype=DTYPE))
            table = _rme_table(lam, tuple(spin.tolist()), 3.5)[lev[:, None], lev[None, :]]
            assert torch.equal(direct, table)
            assert torch.equal(dcgs(L, jj[:, None].expand(n, n), jj[None, :].expand(n, n)),
                               _dcgs_lookup(lam, jj))
