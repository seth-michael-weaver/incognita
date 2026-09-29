"""T12: direct inelastic scattering, giant resonances and direct radiative capture.

Every test that needs TALYS output skips (not fails) when the dumps are absent, per contract §6.
The gate itself is `python -m physics.hf.direct.score`; these are the unit-level checks plus a
small A-mult slice of it so the tolerance is enforced at every commit.
"""

from __future__ import annotations

import numpy as np
import pytest
import torch

from physics.hf import reference as ref
from physics.hf.core.tensors import DTYPE
from physics.hf.direct import capture as C
from physics.hf.direct import dwba as D
from physics.hf.direct import prepare as P
from physics.hf.direct import reference as dref
from physics.hf.direct import score as S

SPHERICAL = ("Ca040", "Fe056", "Ni058", "Zr090", "Co059", "Au197")
TOL = S.TOL_AMULT  # 0.05, contract §6


def _need_dumps():
    if not ref.available("block_index"):
        pytest.skip("reference dumps not parsed")


def _need_t12(variant="t12spec"):
    if not dref.t12_available(variant):
        pytest.skip(f"{variant} reference runs absent; see physics.hf.direct.reference_runs")


# --- sum rules --------------------------------------------------------------------------------


@pytest.mark.parametrize("target", SPHERICAL)
def test_sumrules_reproduce_the_dumped_giant_resonance_parameters(target):
    _need_dumps()
    es = [e for e in dref.energies_with_direct(target) if dref.dump(target, e).has_giant]
    if not es:
        pytest.skip(f"{target}: no giant-resonance block (below the pre-equilibrium onset)")
    cs = P.case(target, es[-1])
    gr = D.giant_resonance_parameters(cs.struct, cs.params)
    d = dref.dump(target, es[-1])
    for got, want, name in (
        (gr.e_mev, d.egrcoll_mev, "Egrcoll"),
        (gr.width_mev, d.ggrcoll_mev, "Ggrcoll"),
        (gr.beta, d.betagr, "betagr"),
    ):
        g, w = got.detach().numpy(), np.asarray(want)
        live = w != 0.0
        assert (g[~live] == 0.0).all(), f"{target} {name}: non-zero where TALYS has zero"
        r = np.abs(np.log(g[live] / w[live]))
        assert r.max() < 1e-4, f"{target} {name}: {g} vs {w}"


def test_giant_resonance_parameters_are_differentiable_in_their_adjust_factors():
    _need_dumps()
    from physics.hf.input.defaults import default_options, default_params

    cs = P.case("Fe056", 14.0)
    o = default_options(26, 56)
    params = default_params(26, 56, o).requires_grad_(["GMRadjustE", "GQRadjustD"])
    gr = D.giant_resonance_parameters(cs.struct, params)
    (gr.e_mev.sum() + gr.beta.sum()).backward()
    assert torch.isfinite(params["GMRadjustE"].grad).all()
    assert params["GMRadjustE"].grad.abs() > 0
    assert params["GQRadjustD"].grad.abs() > 0


def test_a_non_positive_sum_rule_switches_its_resonance_off():
    """sumrules.f90:95-97: `if (S > 0.)`. A target whose low-lying 3- states exhaust the
    low-energy octupole sum rule gets betagr = 0 there, and then no LEOR at all."""
    _need_dumps()
    cs = P.case("Fe056", 14.0)
    st = cs.struct
    big = st.deform.copy()
    big[1:] *= 50.0  # exhaust every sum rule
    huge = type(st)(**{**st.__dict__, "deform": big})
    gr = D.giant_resonance_parameters(huge, cs.params)
    assert float(gr.beta[0]) == 0.0 and float(gr.beta[1]) == 0.0 and float(gr.beta[2]) == 0.0
    assert float(gr.beta[3]) > 0.0  # HEOR is never clipped (sumrules.f90:98)


# --- level selection and the discrete/continuum split -----------------------------------------


@pytest.mark.parametrize("target", SPHERICAL)
def test_selected_levels_match_the_directE_rows(target):
    _need_dumps()
    for e in dref.energies_with_direct(target):
        d = dref.dump(target, e)
        cs = P.case(target, e)
        lv = D.direct_levels(cs.struct, cs.eninccm_mev, cs.eoutdis_mev, e, cs.options.k0)
        xs, xscc, _ = P.injected_cross_sections(cs, lv, d)
        xsdd, _, _ = D.direct_inelastic(cs.struct, lv, xs, xscc)
        got = {int(i) for i in np.nonzero(xsdd.numpy())[0]}
        assert got == set(d.level.tolist()), f"{target} at {e} MeV"


@pytest.mark.parametrize("target", SPHERICAL)
def test_direct_totals_split_at_nlast(target):
    _need_dumps()
    worst = 0.0
    for e in dref.energies_with_direct(target):
        d = dref.dump(target, e)
        if d.xsdirdisctot_mb <= 0.0:
            continue
        cs = P.case(target, e)
        lv = D.direct_levels(cs.struct, cs.eninccm_mev, cs.eoutdis_mev, e, cs.options.k0)
        xs, xscc, _ = P.injected_cross_sections(cs, lv, d)
        _, disctot, colltot = D.direct_inelastic(cs.struct, lv, xs, xscc)
        worst = max(worst, abs(np.log(float(disctot) / d.xsdirdisctot_mb)))
        if d.xscollconttot_mb > 0:
            worst = max(worst, abs(np.log(float(colltot) / d.xscollconttot_mb)))
    assert worst < TOL, f"{target}: worst |ln(p/t)| = {worst}"


# --- giant.f90 smearing -----------------------------------------------------------------------


def test_giant_spectra_reproduce_the_dumped_spectra_block():
    _need_t12()
    worst = 0.0
    n = 0
    for target in dref.t12_available("t12spec")[:3]:
        for e in dref.t12_energies(target, "t12spec"):
            d = dref.t12_dump(target, e, "t12spec")
            if not d.has_spectra or d.spec_total_mb.max() <= 0:
                continue
            for rec in S._case_records(target, e, "t12spec", d):
                if rec["kind"] == "spectra" and rec["r"]:
                    worst = max(worst, max(rec["r"]))
                    n += len(rec["r"])
    assert n > 100, "no spectra points scored"
    assert worst < TOL, f"worst |ln(p/t)| = {worst}"


def test_giant_weights_sum_to_the_resonance_cross_section():
    """giant.f90:112-113 normalises the Gaussian over the open grid, so xsgrstate is mb per bin
    and sums back to xsgrcoll -- unlike xscollcont, which is divided by deltaE as well."""
    _need_dumps()
    cs = P.case("Ni058", 14.0)
    gr = D.giant_resonance_parameters(cs.struct, cs.params)
    xsgrcoll = torch.tensor([0.0, 0.0, 19.0, 0.0], dtype=DTYPE)
    st, tot, eoutgr = D.giant_spectra(
        gr, xsgrcoll, cs.eninccm_mev, torch.as_tensor(cs.egrid_mev, dtype=DTYPE), cs.grid_mask
    )
    assert st.dtype is DTYPE and st.shape[0] == 4
    assert abs(float(st.sum()) - 19.0) < 1e-9
    assert abs(float(eoutgr[2]) - (cs.eninccm_mev - float(gr.e_mev[2]))) < 1e-12
    assert float(tot.sum()) == pytest.approx(19.0, abs=1e-9)


def test_collective_continuum_is_resolved_by_spin_and_parity():
    _need_dumps()
    cs = P.case("Ni058", 14.0)
    d = dref.dump("Ni058", 14.0)
    lv = D.direct_levels(cs.struct, cs.eninccm_mev, cs.eoutdis_mev, 14.0, cs.options.k0)
    xs, xscc, _ = P.injected_cross_sections(cs, lv, d)
    xsdd, _, colltot = D.direct_inelastic(cs.struct, lv, xs, xscc)
    cc, ccjp = D.collective_continuum(
        cs.struct,
        xsdd,
        cs.eoutdis_mev,
        cs.eninccm_mev,
        torch.as_tensor(cs.egrid_mev, dtype=DTYPE),
        torch.as_tensor(cs.deltae_mev, dtype=DTYPE),
        cs.grid_mask,
        float(cs.params.at("elwidth")),
    )
    assert float(colltot) > 0
    assert torch.allclose(ccjp.sum((0, 1)), cc, atol=1e-12)
    assert (cc >= 0).all() and cc[~cs.grid_mask].abs().max() == 0


def test_direct_driver_totals_match_the_dump():
    """`direct.f90` composed: xsdirdisctot, xscollconttot and xsgrtot = sum(xsgrcoll) +
    xscollconttot, the three scalars binary.f90:214-272 reads."""
    _need_dumps()
    for target, e in (("Ni058", 14.0), ("Fe056", 20.0), ("Au197", 16.0)):
        cs = P.case(target, e)
        d = dref.dump(target, e)
        gr = D.giant_resonance_parameters(cs.struct, cs.params)
        lv = D.direct_levels(cs.struct, cs.eninccm_mev, cs.eoutdis_mev, e, cs.options.k0)
        xs, xscc, xsgrcoll = P.injected_cross_sections(cs, lv, d)
        r = D.direct(
            cs.struct,
            gr,
            lv,
            xs,
            xsgrcoll,
            cs.eoutdis_mev,
            cs.eninccm_mev,
            torch.as_tensor(cs.egrid_mev, dtype=DTYPE),
            torch.as_tensor(cs.deltae_mev, dtype=DTYPE),
            cs.grid_mask,
            xscc,
            flaggiant=d.has_giant,
            elwidth_mev=float(cs.params.at("elwidth")),
        )
        assert float(r.xsdirdisctot_mb) == pytest.approx(d.xsdirdisctot_mb, rel=TOL)
        assert float(r.xscollconttot_mb) == pytest.approx(d.xscollconttot_mb, rel=TOL)
        # directout.f90:211 prints xsgrtot - xscollconttot as "total GR cross section"
        assert float(r.xsgrtot_mb) == pytest.approx(d.xsgrtot_mb + d.xscollconttot_mb, rel=TOL)
        assert torch.allclose(r.xsgr_mb, r.xsgrstate_mb.sum(0) + r.xscollcont_mb)


def test_direct_driver_is_silent_below_the_preequilibrium_onset():
    """energies.f90:194-203: no flaggiant, so `giant` never runs and every spectrum is zero,
    but the discrete DWBA cross sections still stand."""
    _need_dumps()
    cs = P.case("Ni058", 3.0)
    d = dref.dump("Ni058", 3.0)
    assert not d.has_giant
    gr = D.giant_resonance_parameters(cs.struct, cs.params)
    lv = D.direct_levels(cs.struct, cs.eninccm_mev, cs.eoutdis_mev, 3.0, cs.options.k0)
    xs, xscc, xsgrcoll = P.injected_cross_sections(cs, lv, d)
    r = D.direct(
        cs.struct,
        gr,
        lv,
        xs,
        xsgrcoll,
        cs.eoutdis_mev,
        cs.eninccm_mev,
        torch.as_tensor(cs.egrid_mev, dtype=DTYPE),
        torch.as_tensor(cs.deltae_mev, dtype=DTYPE),
        cs.grid_mask,
        xscc,
        flaggiant=False,
    )
    assert float(r.xsgrtot_mb) == 0.0
    assert float(r.xsgr_mb.abs().max()) == 0.0
    assert float(r.xsdirdisctot_mb) == pytest.approx(d.xsdirdisctot_mb, rel=TOL)


@pytest.mark.parametrize("target", SPHERICAL)
def test_open_giant_resonances_match_the_dumped_non_zero_rows(target):
    """directecis.f90:230-232 / directread.f90:156-158: a resonance is calculated only when
    eninccm clears Egrcoll by more than 0.1 parA MeV."""
    _need_dumps()
    n = 0
    for e in dref.energies_with_direct(target):
        d = dref.dump(target, e)
        if not d.has_giant:
            continue
        cs = P.case(target, e)
        gr = D.giant_resonance_parameters(cs.struct, cs.params)
        got = set(D.giant_levels(gr, cs.eninccm_mev, cs.options.k0).tolist())
        want = set(np.nonzero(d.xsgrcoll_mb)[0].tolist())
        assert want <= got, f"{target} at {e} MeV: {want} not in {got}"
        assert all(d.xsgrcoll_mb[k] != 0.0 or k in want for k in got)
        n += 1
    if n == 0:
        pytest.skip(f"{target}: no giant-resonance block")


# --- coupled channels -------------------------------------------------------------------------


def test_coupled_channel_levels_are_found_for_a_vibrational_target():
    """Ca-40 is colltype 'V': its 3- at 3.74 MeV carries 43 mb of direct inelastic but has
    deform = 0, because the incident coupled-channels run owns it (incidentread.f90:381-385)."""
    _need_dumps()
    cs = P.case("Ca040", 10.0)
    assert cs.struct.colltype == "V"
    assert set(cs.struct.cc_levels.tolist()) == {2, 3, 4}
    assert all(cs.struct.deform[i] == 0.0 for i in cs.struct.cc_levels)
    sph = P.case("Ni058", 10.0)
    assert sph.struct.colltype == "S" and sph.struct.cc_levels.size == 0


# --- direct radiative capture -----------------------------------------------------------------


def test_racap_is_off_by_default():
    from physics.hf.input.defaults import default_options

    assert default_options(28, 58).flagracap is False


def test_n_experimental_levels_follows_ispect():
    assert C.ISPECT == 3  # racapinit.f90:418
    assert C.n_experimental_levels(30) == 31


def test_racap_populations_split_and_bin():
    """racap.f90:186-210 in miniature: barns to mb, the split at nlevexpracap, and the bin
    search for a continuum state."""
    xspex = torch.tensor([1.0e-3, 2.0e-3, 5.0e-3], dtype=DTYPE)
    xsp = torch.zeros(3, 31, 2, dtype=DTYPE)
    xsp[2, 4, 1] = 5.0e-3
    ex = np.array([0.0, 1.0, 2.0, 3.0])
    dex = np.array([0.0, 1.0, 1.0, 1.0])
    rp = C.racap_populations(
        xspex, xsp, np.array([0.0, 0.0, 2.2]), 3, 2, ex, dex, maxex=3, numjph=30
    )
    assert float(rp.xsracapedisc_mb) == pytest.approx(3.0)
    assert float(rp.xsracapecont_mb) == pytest.approx(5.0)
    assert float(rp.xsracape_mb) == pytest.approx(8.0)
    assert float(rp.popex_mb[0]) == pytest.approx(1.0)
    assert float(rp.popex_mb[1]) == pytest.approx(2.0)
    assert float(rp.popex_mb[2]) == pytest.approx(5.0)  # exfin 2.2 falls in bin [1.5, 2.5)
    assert float(rp.pop_mb[2, 4, 1]) == pytest.approx(5.0)


def test_racap_binary_addends_move_flux_out_of_the_compound_nucleus():
    rp = C.RacapPopulation(
        torch.tensor(8.0, dtype=DTYPE),
        torch.tensor(3.0, dtype=DTYPE),
        torch.tensor(5.0, dtype=DTYPE),
        torch.zeros(1, dtype=DTYPE),
        torch.zeros(1, 1, 2, dtype=DTYPE),
    )
    z = lambda v: torch.tensor(v, dtype=DTYPE)  # noqa: E731
    a = C.racap_binary_addends(rp, z(10.0), z(20.0), z(30.0), z(40.0))
    assert float(a["xsdisctot_mb"]) == 13.0
    assert float(a["xsdircont_mb"]) == 25.0
    assert float(a["xspopnuc_mb"]) == 38.0 and float(a["xsbinary_mb"]) == 48.0
    assert float(a["xscompall_subtract_mb"]) == 8.0


def _spectfac_for(target_z, target_a, n):
    from physics.hf.input.defaults import default_options, default_params
    from physics.hf.structure.levels import discrete_levels
    from physics.hf.structure.masses import masses

    o = default_options(target_z, target_a)
    pa = default_params(target_z, target_a, o)
    m = masses(o, pa)
    cn = discrete_levels(target_z, target_a + 1, o, m, pa)
    return (
        C.spectroscopic_factors(
            target_z,
            target_a + 1,
            o,
            pa,
            cn.all_e_mev.numpy(),
            cn.all_spin.numpy(),
            cn.all_parity.numpy(),
            int(cn.nlev),
            numex=n - 1,
        ),
        int(cn.nlev),
    )


def test_spectroscopic_factors_match_the_shipped_talys_sample():
    """`samples/n-Y089-dircap` is TALYS's own direct-capture example. Y-89 is odd-A, so
    `sfexpall` is 1 (input_gammapar.f90:164) and every factor is 1 -- the branch T12's own
    even-A reference runs never exercise."""
    try:
        ro = dref.sample_racap_out()
    except KeyError:
        pytest.skip("TALYS samples not installed")
    sf, nlev = _spectfac_for(39, 89, len(ro.spectfac))
    assert C.n_experimental_levels(nlev) == ro.nlevexpracap
    n = min(len(sf), len(ro.spectfac))
    assert np.abs(sf[:n] - ro.spectfac[:n]).max() < 5e-4


def test_the_shipped_direct_capture_sample_is_identically_zero():
    """TALYS-2.24 ships `n-Y089-dircap` with `racap y` and its own reference `racap.out` has
    `Direct radiative capture xs = 0.00000E+00` at all 41 energies -- and so do T12's own
    `racap y` runs on Fe-56, Ni-58, Zr-90 and Sn-120, with no error and no warning. `racapcalc`
    contributes nothing in this version, which is why the flag is safe and why there are no
    non-trivial numbers to gate the capture kernel against."""
    try:
        ro = dref.sample_racap_out()
    except KeyError:
        pytest.skip("TALYS samples not installed")
    assert len(ro.energies_mev) > 0
    assert float(np.abs(ro.xsracape_mb).max()) == 0.0
    assert np.allclose(ro.xspopnuc_mb, ro.xshfpreeq_mb)


def test_spectroscopic_factors_match_racap_out():
    """Every target of T12's own `racap y` runs: the two global defaults and the per-level
    `structure/levels/spectn/<Sym>.spectn` override, against what TALYS printed."""
    _need_t12("t12racap")
    worst = {}
    for target in dref.t12_available("t12racap"):
        ro = dref.t12_racap_out(target)
        z, a = P.parse_target(target)
        sf, nlev = _spectfac_for(z, a, len(ro.spectfac))
        assert C.n_experimental_levels(nlev) == ro.nlevexpracap, target
        n = min(len(sf), len(ro.spectfac))
        worst[target] = float(np.abs(sf[:n] - ro.spectfac[:n]).max())
        # the file override must actually have fired: TALYS printed values that are neither
        # default, and so must the port
        assert len(set(np.round(sf[:nlev], 6))) > 2, f"{target}: no per-level factors"
    assert max(worst.values()) < 5e-4, worst


def test_racap_addend_matches_the_capture_channel_in_racap_out():
    """racapout.f90:145-149 prints `xspopnuc(0,0)` before and after the direct-capture addend,
    which is exactly what `racap_binary_addends` does to it (binary.f90:276)."""
    _need_t12("t12racap")
    target = dref.t12_available("t12racap")[0]
    ro = dref.t12_racap_out(target)
    n = min(len(ro.xsracape_mb), len(ro.xspopnuc_mb), len(ro.xshfpreeq_mb))
    assert n > 0
    worst = 0.0
    for i in range(n):
        if ro.xspopnuc_mb[i] <= 0:
            continue
        rp = C.RacapPopulation(
            torch.tensor(float(ro.xsracape_mb[i]), dtype=DTYPE),
            torch.tensor(float(ro.xsracapedisc_mb[i]), dtype=DTYPE),
            torch.tensor(float(ro.xsracapecont_mb[i]), dtype=DTYPE),
            torch.zeros(1, dtype=DTYPE),
            torch.zeros(1, 1, 2, dtype=DTYPE),
        )
        z = torch.zeros((), dtype=DTYPE)
        a = C.racap_binary_addends(
            rp, z, z, torch.tensor(float(ro.xshfpreeq_mb[i]), dtype=DTYPE), z
        )
        worst = max(worst, abs(np.log(float(a["xspopnuc_mb"]) / ro.xspopnuc_mb[i])))
        assert float(a["xsdisctot_mb"]) == pytest.approx(ro.xsracapedisc_mb[i], rel=1e-12)
    assert worst < TOL, f"xspopnuc after racap: {worst}"


def test_racap_totals_are_the_split_of_the_per_level_table():
    _need_t12("t12racap")
    target = dref.t12_available("t12racap")[0]
    ro = dref.t12_racap_out(target)
    worst = 0.0
    for i, tot in enumerate(ro.xsracape_mb):
        if tot <= 0 or i >= len(ro.popex_mb):
            continue
        px = ro.popex_mb[i]
        got = float(px[: ro.nlevexpracap].sum())
        if ro.xsracapedisc_mb[i] > 0:
            worst = max(worst, abs(np.log(got / ro.xsracapedisc_mb[i])))
    assert worst < TOL, f"discrete sum vs header: {worst}"


# --- conventions ------------------------------------------------------------------------------


def test_every_returned_tensor_is_float64():
    _need_dumps()
    cs = P.case("Fe056", 14.0)
    gr = D.giant_resonance_parameters(cs.struct, cs.params)
    assert gr.e_mev.dtype is DTYPE and gr.beta.dtype is DTYPE
    lv = D.direct_levels(cs.struct, cs.eninccm_mev, cs.eoutdis_mev, 14.0, cs.options.k0)
    xs, xscc, xsgrcoll = P.injected_cross_sections(cs, lv, dref.dump("Fe056", 14.0))
    out = D.direct_inelastic(cs.struct, lv, xs, xscc)
    assert all(t.dtype is DTYPE for t in out)
    assert out[0].shape == (301,)  # numlev2 + 1
