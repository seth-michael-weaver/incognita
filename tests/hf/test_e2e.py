"""The engine driver, the `densprepare` adapter and the end-to-end statistic
(E2E, docs/results/hf-engine-gates.md §4).

`densprepare` is the seam T10 named: it builds `compound.prepare`'s rho0 / Tjlnex / Tlnex / Tgam
from T5, T6 and T7, so `comptarget` can run without those four arrays being injected. The unit
tests below pin its arithmetic against densprepare.f90 line by line; the gate that measures it
against TALYS's own arrays is `physics.hf.compound.dens_reference`.

Two seams remain open (compnorm.f90 + population.f90, and multiple.f90's feeding chain), so §4's
"nothing injected" premise is not met yet and these tests do not assert the verdict -- they assert
the statistic is computed, that it names what it injected, and that no channel is in KILL range.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import numpy as np
import pytest
import torch

from physics.hf.results import Results, channel_code, level_key, residual_key, stack

RUNS = Path(os.environ.get("T10_RUNS", Path.home() / "hf_t10/score_work"))
E2E = Path("docs/results/hf-e2e.json")
NOT_YET = 0.15  # §4: above this the channel is a KILL candidate, once everything has landed


def _run_dirs() -> list[Path]:
    return sorted(p for p in RUNS.glob("*__*")
                  if (p / "bin_inputs.txt").is_file() and (p / "ch_inputs.txt").is_file())


def test_results_keys_match_the_talys_file_names():
    assert channel_code((1, 0, 0, 0, 0, 0)) == "xs100000"
    assert channel_code((0, 0, 0, 0, 0, 0)) == "xs000000"
    assert channel_code((2, 0, 0, 0, 0, 0)) == "xs200000"
    assert channel_code((0, 1, 0, 0, 0, 0)) == "xs010000"
    assert channel_code((0, 0, 0, 0, 0, 1)) == "xs000001"
    assert level_key(1, 1, 1) == "nn.L01"
    assert level_key(1, 6, 0) == "na.L00"
    assert residual_key(26, 56) == "rp026056"


def test_stack_zero_fills_channels_that_are_closed_at_some_energies():
    out = stack([{"a": 1.0}, {"a": 2.0, "b": 3.0}])
    assert out["a"].tolist() == [1.0, 2.0]
    assert out["b"].tolist() == [0.0, 3.0]
    assert out["a"].dtype is torch.float64


def test_run_without_injection_says_what_is_missing():
    from physics.hf.engine import run

    with pytest.raises(NotImplementedError) as e:
        run()
    msg = str(e.value)
    assert "compnorm.f90" in msg and "multiple.f90" in msg
    assert "DumpInjection" in msg and "ChainedCompound" in msg


def test_engine_returns_a_results_with_every_family_it_injected():
    from physics.hf.engine import DumpInjection, run

    dirs = _run_dirs()
    if not dirs:
        pytest.skip(f"no instrumented emission dump under {RUNS}")
    inj = DumpInjection(dirs[0])
    r = run(injection=inj)
    assert isinstance(r, Results)
    assert r.n > 0
    assert r.injected == inj.families and r.injected
    assert "xs000000" in r.channels_mb
    assert {"elastic", "nonelastic", "total", "reaction"} <= set(r.totals_mb)
    for v in r.channels_mb.values():
        assert v.shape == (r.n,) and v.dtype is torch.float64


def test_e2e_statistic_is_computed_and_flagged_provisional():
    if not E2E.is_file():
        pytest.skip("E2E not scored yet")
    g = json.loads(E2E.read_text())
    assert g["provisional"] is True, "no verdict may be declared while families are injected"
    assert g["injected"], "a provisional E2E must name what it injected"
    assert g["statistic"], "no channel was scored"
    for label, s in g["statistic"].items():
        assert s["targets"] > 0, label
        assert s["statistic"] <= NOT_YET, (label, s)


# ================================================================================================
# densprepare.f90 (compound.prepare.densprepare)
# ================================================================================================


def _resid(**kw):
    from physics.hf.compound.prepare import NUMJ, DensResidual

    n = kw.pop("n", 4)
    d = dict(
        type=1, zix=0, nix=1, A=56, nlast=1, ntop=1, nexmax=n - 1, sep_mev=7.0,
        ex_mev=np.array([0.0, 0.8, 2.0, 3.0]), dex_mev=np.array([0.4, 0.4, 1.0, 1.0]),
        maxj=np.array([NUMJ, NUMJ, 5, 5]), parlev=np.array([1, -1, 0, 0]),
        jdis=np.array([0.0, 2.0, 0.0, 0.0]),
        rhogrid=np.ones((n, NUMJ + 1, 2)),
    )
    d.update(kw)
    return DensResidual(**d)


def _inputs(**kw):
    from physics.hf.compound.prepare import DensPrepareInputs

    d = dict(
        exinc_mev=12.0, dexinc_mev=0.0, s_n_mev=11.2, gammax=2, lmaxinc=5, k0=1,
        fnorm=np.ones(8), residuals={1: _resid()}, trans={1: _trans()}, primary=True,
    )
    d.update(kw)
    return DensPrepareInputs(**d)


def _trans(L=3, n=6):
    from physics.hf.compound.prepare import DensTrans

    eg = np.array([0.0, 1.0, 2.0, 3.0, 4.0, 5.0])
    tjl = np.zeros((n, L, 3))
    tjl[:, :, 0] = np.arange(n)[:, None] * 0.01 + 0.1
    tjl[:, :, 2] = np.arange(n)[:, None] * 0.01 + 0.2
    return DensTrans(egrid_mev=eg, ebegin=1, eend=5, maxen=5, tjl=tjl,
                     tl=tjl[:, :, 2].copy(), lmax=np.array([0, 2, 2, 2, 2, 2]))


def test_densprepare_primary_eout_is_exinc_minus_exout_minus_s():
    from physics.hf.compound.prepare import _eout_and_rboundary

    inp = _inputs()
    r = inp.residuals[1]
    for nex in range(4):
        eout, rb, exout = _eout_and_rboundary(inp, r, nex)
        assert rb == 1.0  # densprepare.f90:196-203: no boundary correction for the primary CN
        assert eout == pytest.approx(12.0 - r.ex_mev[nex] - 7.0)
        assert exout == r.ex_mev[nex]


def test_densprepare_continuum_to_discrete_rboundary_is_the_reachable_fraction():
    """densprepare.f90:246-252: the lowest mother bin that can reach a level only partly can."""
    from physics.hf.compound.prepare import _eout_and_rboundary

    r = _resid(sep_mev=7.0)
    # Exm = Ex(level 1) + S = 7.8 sits inside the mother bin [7.5, 8.5]
    inp = _inputs(primary=False, exinc_mev=8.0, dexinc_mev=1.0, residuals={1: r})
    eout, rb, _ = _eout_and_rboundary(inp, r, 1)
    assert rb == pytest.approx((8.5 - 7.8) / 1.0)
    assert eout == pytest.approx(0.5 * (8.5 + 7.8) - 7.0 - 0.8)
    # a mother bin well above it reaches all of the level, with no correction
    inp2 = _inputs(primary=False, exinc_mev=12.0, dexinc_mev=1.0, residuals={1: r})
    eout2, rb2, _ = _eout_and_rboundary(inp2, r, 1)
    assert rb2 == 1.0 and eout2 == pytest.approx(12.0 - 7.0 - 0.8)


def test_densprepare_top_continuum_bin_centre_is_shifted():
    """densprepare.f90:225-227: the highest residual bin's Ex1plus is Ex0plus - S, and Exout
    moves to the middle of the bin that survives."""
    from physics.hf.compound.prepare import _eout_and_rboundary

    r = _resid(nlast=1)
    inp = _inputs(primary=False, exinc_mev=10.0, dexinc_mev=1.0, residuals={1: r})
    _, _, exout = _eout_and_rboundary(inp, r, 3)  # nexout == nexmax and type >= 1
    ex1min = r.ex_mev[3] - 0.5 * r.dex_mev[3]
    assert exout == pytest.approx(0.5 * ((10.5 - 7.0) + ex1min))
    # a bin below the top keeps its own centre
    _, _, ex2 = _eout_and_rboundary(inp, r, 2)
    assert ex2 == pytest.approx(r.ex_mev[2])


def test_densprepare_rho0_is_a_weight_for_levels_and_a_density_for_bins():
    from physics.hf.compound.prepare import densprepare

    r = _resid()
    out = densprepare(_inputs(residuals={1: r}))[1]
    # level 0: spin 0, parity +1 -> exactly one cell, weight 1 (nexout <= Ntop)
    assert out.rho[0, 0, 1] == 1.0 and out.rho[0].sum() == 1.0
    # level 1: int(jdis) = 2, parity -1
    assert out.rho[1, 2, 0] == 1.0 and out.rho[1].sum() == 1.0
    # continuum bin: rhogrid up to maxJ, zero above
    assert out.rho[2, :6].sum() == pytest.approx(12.0)
    assert out.rho[2, 6:].sum() == 0.0


def test_densprepare_discfactor_corrects_levels_above_ntop_and_is_clamped():
    from physics.hf.compound.prepare import densprepare

    # NL = 3 > Ntop = 1, Ncum(NL) = 2.0 -> (2 - 1) / (3 - 1) = 0.5
    r = _resid(nlast=3, ntop=1, ncum_nl=2.0,
               jdis=np.array([0.0, 2.0, 1.0, 3.0]), parlev=np.array([1, -1, 1, 1]))
    out = densprepare(_inputs(residuals={1: r}))[1]
    assert out.rho[2, 1, 1] == pytest.approx(0.5)
    assert out.rho[0, 0, 1] == 1.0  # nexout 0 <= Ntop, no correction
    # clamp: a huge Ncum gives 2, a tiny one gives 0.5 (densprepare.f90:173-174)
    hi = densprepare(_inputs(residuals={1: _resid(nlast=3, ntop=1, ncum_nl=1e6,
                                                  jdis=np.array([0.0, 2.0, 1.0, 3.0]),
                                                  parlev=np.array([1, -1, 1, 1]))}))[1]
    assert hi.rho[2, 1, 1] == pytest.approx(2.0)


def test_densprepare_tgam_is_twopi_egamma_pow_2l_plus_1_times_f():
    from physics.hf.core.constants import talys_constants
    from physics.hf.compound.prepare import densprepare

    calls = []

    def f(efs, egamma, irad, l):  # noqa: E741
        calls.append((efs, egamma, irad, l))
        return 1.0e-8

    g = _resid(type=0, zix=0, nix=0, sep_mev=0.0)
    out = densprepare(_inputs(residuals={0: g}, trans={}, gamma_strength=f))[0]
    twopi = float(talys_constants()["twopi"])
    egamma = 12.0 - g.ex_mev[1]
    assert out.tgam[1, 1, 0] == pytest.approx(twopi * egamma ** 3 * 1.0e-8)
    assert out.tgam[1, 2, 1] == pytest.approx(twopi * egamma ** 5 * 1.0e-8)
    assert out.tgam[:, 0].max() == 0.0, "l = 0 is never a gamma multipole"
    # Efs = Exinc - S(Zcomp, Ncomp, 1), the *compound* neutron separation energy,
    # not the residual's own S (densprepare.f90:158)
    assert {round(c[0], 9) for c in calls} == {round(12.0 - 11.2, 9)}


def test_densprepare_tgam_is_zero_when_the_gamma_energy_is_not_positive():
    from physics.hf.compound.prepare import densprepare

    g = _resid(type=0, zix=0, nix=0, sep_mev=0.0,
               ex_mev=np.array([0.0, 0.8, 2.0, 30.0]))
    out = densprepare(_inputs(residuals={0: g}, trans={},
                              gamma_strength=lambda *a: 1.0))[0]
    assert out.tgam[3].max() == 0.0  # Exinc - Exout < 0 -> densprepare.f90:301 cycles
    assert out.tgam[1].max() > 0.0


def test_densprepare_lmaxhf_copies_the_top_bin_and_lmaxinc_at_the_incident_ground_state():
    from physics.hf.compound.prepare import densprepare

    out = densprepare(_inputs(lmaxinc=7))[1]
    assert out.lmaxhf[0] == 7, "densprepare.f90:394-396 overrides lmaxhf(k0, 0) with lmaxinc"
    assert out.lmaxhf[-1] == out.lmaxhf[-2], "densprepare.f90:389"


def test_densprepare_interpolation_nodes_start_at_nen_near_the_grid_start():
    from physics.hf.compound.prepare import _interp_nodes

    tr = _trans()
    na, nb, nc = _interp_nodes(tr, np.array([0, 1, 2, 3, 4]))
    # nen <= ebegin + 1 = 2 and nen < maxen - 1 = 4 -> the triple starts at nen
    assert na.tolist()[:3] == [0, 1, 2]
    # nen = 3 > ebegin + 1 -> centred; nen = 4 >= maxen - 1 -> centred
    assert na.tolist()[3:] == [2, 3]
    assert (nb == na + 1).all() and (nc == na + 2).all()


def test_densprepare_tjlnex_drops_below_transeps_and_above_lmax():
    from physics.hf.compound.prepare import densprepare

    tr = _trans()
    tr.tjl[:, :, :] = 1.0e-12  # every value under transeps
    out = densprepare(_inputs(trans={1: tr}))[1]
    assert out.tjl.max() == 0.0
    tr2 = _trans()
    out2 = densprepare(_inputs(trans={1: tr2}))[1]
    # lmax(type, nen) is 2 on this grid, so l = 3.. is never written (L is 3 here)
    assert out2.tjl.shape[1] == 3


def test_updown_axis_is_not_the_contracts_padded_j_order():
    """A nucleon's T(l+1/2) belongs at updown = +1 (index 2), not at the contract's index 1.

    Reading one as the other zeroes half of every particle exit channel: compprepare.f90:339
    computes `updown2 = (jj2prime - l2prime) / pspin2o`, which is +-1 for a spin-1/2 ejectile and
    0 for an alpha, and indexes Tjlnex with it.
    """
    from physics.hf.compound.dens_reference import _to_updown_axis

    t = torch.tensor([[[0.1, 0.2, 0.0]]], dtype=torch.float64)
    for particle in (1, 2, 4, 5):
        out = _to_updown_axis(t, particle)
        assert out[0, 0].tolist() == [0.1, 0.0, 0.2]
    assert _to_updown_axis(t, 3)[0, 0].tolist() == [0.1, 0.2, 0.0]  # deuteron: already updown
    assert _to_updown_axis(t, 6)[0, 0].tolist() == [0.0, 0.1, 0.0]  # alpha: only updown = 0


def test_chained_compound_injects_strictly_less_than_dump_injection():
    from physics.hf.engine import ChainedCompound, DumpInjection

    dump = set(DumpInjection(Path(".")).families)
    chained = set(ChainedCompound(Path("."), Path("."), 26, 56).families)
    assert "compound" in dump and "compound" not in chained
    assert "level_density" in dump and "level_density" not in chained
    assert "gamma" in dump and "gamma" not in chained
    assert chained, "a chained run still injects compnorm and the multiple-emission feeding"


DP_GATE = Path("docs/results/hf-densprepare-gate.json")


def test_densprepare_gate_numbers_are_inside_the_component_tolerances():
    if not DP_GATE.is_file():
        pytest.skip("densprepare gate not scored yet")
    g = json.loads(DP_GATE.read_text())
    assert g["runs"], "no run scored"
    for r in g["runs"]:
        assert r["rho0"]["p95"] <= 0.02, (r["run"], "rho0 / A-ld tables")
        assert r["tjlnex"]["p95"] <= 0.01, (r["run"], "Tjlnex / A-trans")
        assert r["tgam"]["p95"] <= 0.01, (r["run"], "Tgam / A-psf")
        ok, n = r["lmaxhf_exact"]
        # lmaxhf is exact everywhere except one bin of Nb-93, where the port's `lmax(type, nen)`
        # sits one below TALYS's at the translimit boundary (hf-e2e.md §3). Anything more than
        # that single cell is a regression, so the budget is pinned, not waived.
        budget = 1 if "Nb093" in r["run"] else 0
        assert n - ok <= budget, (r["run"], f"lmaxhf off on {n - ok} of {n} cells")


# ================================================================================================
# EXCL: engine.run with nothing injected wherever a port exists
# ================================================================================================


def test_chained_full_names_only_the_families_that_have_no_port():
    """`ChainedFull.families` is the §4 premise's audit trail, and it is now EMPTY.

    EXCL3 removed "multiple_preequilibrium" (`multipreeq2.f90` is ported and driven by
    `emission.feeding.Cascade.mpe`); NODUMP removed the last three. `inject=` keeps the old arm
    reachable, because it is the other column of the A/B that gates each family."""
    from physics.hf.engine import ChainedFull, DumpInjection

    assert ChainedFull(Z=26, A=56, declared_energies=(1.0,)).families == ()
    fam = set(ChainedFull(run_dir=Path("."), Z=0, A=0,
                          inject=("preequilibrium_inverse_xs", "direct_dwba",
                                  "structure_scalars")).families)
    assert fam == {"preequilibrium_inverse_xs", "direct_dwba", "structure_scalars"}
    # every compound/emission family DumpInjection carries is built, not injected
    gone = {"compound", "multiple_emission", "level_density", "gamma", "optical"}
    assert gone.isdisjoint(fam)
    assert gone <= set(DumpInjection(Path(".")).families)


def test_chained_full_runs_the_whole_engine_on_one_energy():
    """One low incident energy of Fe-56, end to end: compnorm -> densprepare -> comptarget ->
    population -> binary -> the feeding chain -> channels.

    NODUMP: this no longer needs the instrumented run at all, and no longer monkeypatches
    `DumpInjection.cases` to cut the energy axis down -- `ChainedFull` takes (Z, A) and the run's
    declared grid, and `energies=` is the subset to compute."""
    from physics.hf.engine import ChainedFull
    from physics.hf.engine import run as engine_run
    from physics.hf.talys_reference import ENERGIES_MEV

    res = engine_run(injection=ChainedFull(Z=26, A=56, declared_energies=ENERGIES_MEV,
                                           energies=(1.0,)))
    assert res.injected == ()
    assert res.e_inc_mev.tolist() == [1.0]
    for k in ("elastic", "nonelastic", "total", "reaction"):
        v = float(res.totals_mb[k][0])
        assert np.isfinite(v) and v > 0.0, (k, v)
    # sigma_el + sigma_nonel = sigma_tot is an identity binary.py forms, not a fitted number
    assert float(res.totals_mb["total"][0]) == pytest.approx(
        float(res.totals_mb["elastic"][0]) + float(res.totals_mb["nonelastic"][0]), rel=1e-12)
    # radiative capture is the only channel open at 1 MeV that has to be non-zero
    assert float(res.channels_mb["xs000000"][0]) > 0.0


def test_excl_chained_arm_verdict_matches_the_preregistered_thresholds():
    """§4's outcome is defined purely on the statistic: PASS at or under 0.05, KILL above 0.15,
    NOT YET between. This pins the chained arm's recorded outcome against its own numbers, so a
    rescoring that moves a channel across a threshold cannot leave the verdict behind."""
    p = Path("docs/results/hf-e2e.json")
    if not p.exists():
        pytest.skip("hf-e2e.json not built on this tree")
    g = json.loads(p.read_text())["groups"].get("spherical_chained")
    if g is None:
        pytest.skip("chained arm not scored on this tree")
    assert len(g["targets_scored"]) == 14, g["targets_scored"]
    for ch, v in g["statistic"].items():
        want = ("PASS-level" if v["statistic"] <= 0.05
                else "KILL-level" if v["statistic"] > 0.15 else "NOT YET")
        assert v["outcome"] == want, (ch, v)
        assert v["targets"] == 14, (ch, v)
    # the KILL clause of §4 names five channels; none of them may exceed 0.15
    for ch in ("(n,g)", "elastic", "total inelastic", "(n,2n)", "(n,p)"):
        assert g["statistic"][ch]["statistic"] <= 0.15, (ch, g["statistic"][ch])
    # EXCL2: the recorded verdict word is derived from the statistics rather than hardcoded, so
    # this keeps pinning the doc against its own numbers through a change of outcome. EXCL's
    # version asserted "NOT YET", which is exactly the staleness it was written to prevent.
    outcomes = {v["outcome"] for v in g["statistic"].values()}
    want = ("KILL" if "KILL-level" in outcomes
            else "PASS" if outcomes == {"PASS-level"} else "NOT YET")
    assert g["verdict"].startswith(want), (want, g["verdict"])


# ---------------------------------------------------------------------------------------------
# EXCL2: the two per-run switches the chained arm was reading from the wrong place (hf-e2e.md §4.2)
# ---------------------------------------------------------------------------------------------


def test_cascade_resolves_ewfc_instead_of_leaving_the_minus_one_sentinel():
    """`ewfc` is TALYS's width-fluctuation off-set energy and its default is a SENTINEL, not a
    number: input_compoundmodel.f90:84 sets -1 and nuclides.f90:251 replaces it with
    `S(parZ(k0), parN(k0), k0)` once the masses are known. `default_options` stops at the sentinel,
    and `Einc <= -1.` is false at every incident energy -- so reading it raw silently runs the
    whole chain at W = 1. This pins the resolution, and pins that the raw record still holds the
    sentinel, because that is what makes the mistake easy to make again."""
    from physics.hf.emission.feeding import Cascade

    cas = Cascade(26, 56, 20.0)
    assert cas.options.ewfc_mev == -1.0  # the trap is still there; ewfc_mev is the way past it
    # S_n of Fe-56 (the projectile's separation energy from the TARGET, not from Fe-57)
    assert cas.ewfc_mev == pytest.approx(11.197, abs=5.0e-3)
    assert cas.ewfc_mev == pytest.approx(cas.sep_mev(0, 1)[1])


def test_chained_flagwidth_is_on_below_ewfc_and_off_above_it():
    """energies.f90:179-183 on the resolved onset. Fe-56's reference energies straddle it, so the
    chained arm must switch Moldauer on at 1 keV and off at 14 MeV exactly as TALYS does."""
    from physics.hf.emission.feeding import Cascade

    cas = Cascade(26, 56, 20.0)
    assert bool(0.001 <= cas.ewfc_mev)
    assert bool(1.0 <= cas.ewfc_mev)
    assert not bool(14.0 <= cas.ewfc_mev)


def test_primary_fnorm_is_one_over_fiso_of_the_initial_compound_nucleus():
    """comptarget.f90:281 calls `isotrans(Zinit, Ninit)` and :338 sets `Fnorm = factor / fiso`,
    so the primary decay's `Fnorm` is a property of the COMPOUND nucleus. n + Ca-40 makes Ca-41,
    `Z = N - 1`, so gamma emission is isospin-suppressed by 1.5 (isotrans.f90:52-62) and
    densprepare.f90:310 divides every primary `Tgam` by it. Fe-57 is not isospin-forbidden, which
    is why only Ca-40 of the 14 spherical reference targets ever showed this."""
    from physics.hf.emission.feeding import Cascade

    ca = Cascade(20, 40, 20.0).fiso()
    assert ca[0 + 1] == pytest.approx(1.0 / 1.5)  # type 0, the photon channel
    assert list(ca[[0, 2, 3, 4, 5, 6, 7]]) == [1.0] * 7
    assert list(Cascade(26, 56, 20.0).fiso()) == [1.0] * 8


def test_fiso_does_not_latch_fisom():
    """isotrans keeps two independent latches (isotrans.f90:63-81): `fiso` for the primary decay
    and `fisom` for multiple emission. Reading one must not fix the other."""
    from physics.hf.emission.feeding import Cascade

    cas = Cascade(20, 40, 20.0)
    assert cas.fiso()[1] == pytest.approx(1.0 / 1.5)
    # `fisom` is unaffected by that read -- it is a pure function of (zix, nix) and the energy
    assert cas.fisom(0, 0)[1] == pytest.approx(1.0 / 1.5)
    assert list(cas.fisom(0, 1)) == [1.0] * 8


@pytest.mark.parametrize(
    "tag,Z,A,tol_ng,tol_nonel",
    [("Fe056", 26, 56, 1.0e-3, 1.0e-3),
     # Ca-40's residual nonelastic is ECIS2's coupled-channels seam (`colltype V`): its sigma_reac
     # and Tjlinc are ~2e-3 off, and elastic and total carry the same 2e-3.
     ("Ca040", 20, 40, 2.0e-3, 1.0e-2)])
def test_chained_capture_at_one_kev_matches_talys(tag, Z, A, tol_ng, tol_nonel):
    """The gate on both fixes, at the energy where they bite hardest. At 1 keV the only open
    channels are capture and compound elastic, so `(n,gamma)` and `nonelastic` are a direct read of
    the primary compound decay. Before the fixes: Fe-56 7.7e-2 / 1.8e-2 and Ca-40 2.9e-1 / 2.1e-1.
    """
    from physics.hf.emission.score import XS_FLOOR_MB, _column
    from physics.hf.engine import ChainedFull
    from physics.hf.engine import run as engine_run

    from physics.hf.talys_reference import ENERGIES_MEV

    d = RUNS / f"default__{tag}"
    if not (d / "xs000000.tot").is_file():
        pytest.skip(f"no TALYS reference column for {tag} on this box")
    # NODUMP: the port side of this comparison opens no file belonging to `tag`; `d` is only the
    # reference column.
    res = engine_run(injection=ChainedFull(Z=Z, A=A, declared_energies=ENERGIES_MEV,
                                           energies=(0.001,)))
    assert res.injected == ()
    assert len(res.e_inc_mev) == 1
    e = round(float(res.e_inc_mev[0]), 6)
    for key, port, tol in (("xs000000.tot", float(res.channels_mb["xs000000"][0]), tol_ng),
                           ("nonelastic.tot", float(res.totals_mb["nonelastic"][0]), tol_nonel)):
        talys = _column(d / key, "xs").get(e)
        assert talys is not None and talys > XS_FLOOR_MB, (tag, key, talys)
        assert abs(np.log(port / talys)) <= tol, (tag, key, port, talys)


# ================================================================================================
# EXCL3: multipreeq2.f90 (gate A-mpe) and the `fisom` reset
# ================================================================================================


def test_fisom_is_reset_to_fisominit_after_the_first_cascade_nucleus():
    """`fisom` is NOT a run-scoped latch the way `fiso` is. multiple.f90:458-460 writes
    `fisom(0:6) = fisominit(type) = 1` immediately after `Fnorm` has been formed from it, so the
    `-1` sentinel `isotrans` tests is live exactly once per run -- for the nucleus that clears
    multiple.f90:262-265 first, which for an incident particle is the initial compound nucleus at
    the run's first energy. Every other nucleus, at every energy, decays with `Fnorm = 1`.

    Latching it instead divides the gamma transmission of Ca-40's whole cascade by Ca-41's
    `ff(0) = 1.5`, which is |ln(1.5)| = 0.405 -- A-mult's only failing row before EXCL3.
    `Fnorm` is formed ABOVE multiple.f90:488's `do nex` loop, so it is that nucleus's whole
    decay and not its first bin: NODUMP's half of the fix."""
    from physics.hf.emission.feeding import Cascade

    grid = (0.001, 14.0)
    cas = Cascade(20, 40, 20.0, energies=grid)
    st0 = cas.new_energy(25.0, e_inc_mev=0.001)
    first = cas.fisom(0, 0, st0)  # Ca-41, Z = N - 1
    assert first[0 + 1] == pytest.approx(1.0 / 1.5)
    for zn in ((0, 1), (1, 0), (0, 2)):  # Ca-40 (Z == N), K-40, Ca-39 -- all unsuppressed
        assert list(cas.fisom(*zn, st0)) == [1.0] * 8, zn
    st1 = cas.new_energy(38.0, e_inc_mev=14.0)
    assert list(cas.fisom(0, 0, st1)) == [1.0] * 8  # the sentinel was spent at 1 keV


def test_multipreeq2_moves_unemitted_flux_to_the_next_stage_of_the_same_bin():
    """multipreeq2.f90:297-305 splits `feedph - sumph` equally between `(ipp+1, ihp+1, ipn, ihn)`
    and `(ipp, ihp, ipn+1, ihn+1)` -- both LATER in TALYS's own loop order, so the pair loop is
    sequential and reads the array it is writing. With every daughter closed nothing is emitted,
    so the whole population must walk up the ladder and be conserved."""
    import torch

    from physics.hf.core.tensors import DTYPE
    from physics.hf.preeq.multi import (
        MpeDaughter,
        MultiPreeqInputs,
        multiple_preequilibrium,
    )

    P, B = 6, 4
    pop = torch.zeros(P + 1, P + 1, P + 1, P + 1, dtype=DTYPE)
    pop[0, 0, 1, 1] = 1.0
    z = torch.zeros(B, dtype=DTYPE)
    dead = [MpeDaughter(type=t, zix=t - 1, nix=2 - t, nlast=0, nexmax=-1, parskip=False,
                        s_mev=8.0, gp=torch.tensor(1.7, dtype=DTYPE),
                        gn=torch.tensor(2.0, dtype=DTYPE), ex_mev=z, dex_mev=z, tswave=z,
                        maxj=(0,) * B) for t in (1, 2)]
    one = lambda v: torch.tensor(float(v), dtype=DTYPE)  # noqa: E731
    r = multiple_preequilibrium(MultiPreeqInputs(
        zcomp=0, ncomp=1, nex=1, exinc_mev=one(15.0), dexinc_mev=one(0.4),
        xspopex_mother_mb=one(10.0), xspopph2_mb=pop, gp_comp=one(1.7), gn_comp=one(2.0),
        gp_cn0=one(1.7), gn_cn0=one(2.0), daughters=tuple(dead),
        rnj=torch.zeros(41, dtype=DTYPE), rnjsum=one(1.0), maxpar=P), numj=40)
    assert float(r.summpe_mb) == 0.0  # nexmax = -1: no bin is open, so nothing is emitted
    assert float(r.dmulti) == 0.0
    out = r.xspopph2_mother_mb
    assert float(out[0, 0, 1, 1]) == pytest.approx(1.0)  # the source row is not consumed
    # 0.5 each into (1, 1, 1, 1) and (0, 0, 2, 2), and those two then feed on in turn
    assert float(out[1, 1, 1, 1]) > 0.0 and float(out[0, 0, 2, 2]) > 0.0
    assert float(out[0, 0, 2, 2]) == pytest.approx(0.5)
    assert float(out.sum()) > 2.0  # the ladder, not a single transfer


def test_multipreeq2_is_dormant_below_emulpre():
    """`flagmulpre = not (Einc < emulpre)` with `emulpre = 20 MeV` (input_preeqmodel.f90:83), so
    `population.f90:136` sets `mulpreZN` -- and therefore anything at all happens -- only at the
    last reference energy. The engine must not pay for it at the other 22."""
    from physics.hf.emission.feeding import Cascade

    cas = Cascade(26, 56, 20.0)
    assert cas.options.emulpre_mev == 20.0
    assert not (20.0 < cas.options.emulpre_mev)  # 20.0 MeV exactly is ON
    assert 19.999 < cas.options.emulpre_mev  # everything below is OFF


def test_mpe_gate_numbers_are_inside_the_tolerance():
    """A-mpe: every output of `multipreeq2` against the instrumented TALYS dump, on 14 spherical
    targets at 20 MeV. The two particle-hole rows are differences of `real(sgl)` array entries,
    so they carry a 1e-7 mb floor and are reported unscaled as well (`abs_max_mb`)."""
    p = Path("docs/results/hf-mpe-gate.json")
    if not p.exists():
        pytest.skip("hf-mpe-gate.json not built on this tree")
    g = json.loads(p.read_text())
    assert g["verdict"] == "PASS", g["worst"]
    assert g["calls"] > 1000, g["calls"]
    for q, v in g["worst"].items():
        assert v["n_inf"] == 0, (q, v)
        assert v["p95"] <= g["tolerance"], (q, v)
    # the three that are pure float64-vs-float32: nothing there may exceed single-precision noise
    for q in ("dmulti", "summpe", "xsmpe", "term"):
        assert g["worst"][q]["max"] < 1.0e-5, (q, g["worst"][q])
    assert g["worst"]["daughter_ph"]["abs_max_mb"] < 1.0e-6
    assert g["worst"]["daughter_ph"]["total_flux_rel"] < 1.0e-6
