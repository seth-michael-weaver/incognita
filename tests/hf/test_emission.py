"""T10: binary emission, the multi-chance cascade and exclusive channels (A-mult).

The gate runs on instrumented TALYS runs (`physics/hf/emission/em_reference.py`), which are not
in git; every test that needs one skips when it is absent, as CONTRACT §6 requires. The unit
tests below need no dump.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import numpy as np
import pytest
import torch

from physics.hf.core.tensors import DTYPE
from physics.hf.emission import binary as B
from physics.hf.emission import multiple as M
from physics.hf.emission.channels import ExclusiveState, _limits, exclusive_channels
from physics.hf.emission.dumps import load_binary_dump, load_channel_dump

RUNS = Path(os.environ.get("T10_RUNS", Path.home() / "hf_t10/score_work"))
GATE = Path("docs/results/hf-emission-gate.json")
TOL = 0.05  # A-mult, docs/results/hf-engine-gates.md §3


def _run_dirs() -> list[Path]:
    return sorted(p for p in RUNS.glob("*__*")
                  if (p / "bin_inputs.txt").is_file() and (p / "ch_inputs.txt").is_file())


def _one() -> Path:
    d = _run_dirs()
    if not d:
        pytest.skip(f"no instrumented emission dump under {RUNS}")
    return d[0]


# --- unit tests (no dump) ----------------------------------------------------------------------


def test_spindis_is_normalised_over_spin():
    """The Wigner form integrates to 1 in J; the sum over TALYS's integer J grid is the midpoint
    rule for that integral, so it approaches 1 as the spin cutoff grows (4.6% out at sigma^2 = 1,
    which is a property of the distribution, not of this port)."""
    J = torch.arange(0, 400, dtype=DTYPE)
    errs = []
    for sc in (1.0, 25.0, 100.0):
        s = B.spindis(torch.tensor(sc, dtype=DTYPE), J).sum()
        errs.append(abs(float(s) - 1.0))
    assert errs[0] < 5e-2 and errs[1] < 2e-3 and errs[2] < 5e-4
    assert errs[0] > errs[1] > errs[2]  # the midpoint error falls like 1/sigma^2
    x = torch.linspace(0, 60, 600001, dtype=DTYPE)  # J on a fine grid: the integral IS 1
    sc = torch.tensor(9.0, dtype=DTYPE)
    integral = torch.trapz(B.spindis(sc, x - 0.5), x)
    assert abs(float(integral) - 1.0) < 1e-6


def test_spindis_matches_the_fortran_expression():
    sc, J = 7.5, 3.0
    want = (2 * J + 1) / (2 * sc) * np.exp(-((J + 0.5) ** 2) / (2 * sc))
    got = float(B.spindis(torch.tensor(sc, dtype=DTYPE), torch.tensor(J, dtype=DTYPE)))
    assert abs(got - want) < 1e-14


def test_spindis_is_differentiable_in_the_spin_cutoff():
    sc = torch.tensor(5.0, dtype=DTYPE, requires_grad=True)
    B.spindis(sc, torch.arange(0, 10, dtype=DTYPE)).sum().backward()
    assert torch.isfinite(sc.grad)


def test_channel_particle_limits_follow_the_fortran_formulae():
    """channels.f90:210-218 -- Zix=1, Nix=2 admits 2 n, 1 p, 1 d, 1 t, 1 h, 0 alpha."""
    inc = [True] * 8
    assert _limits(1, 2, inc, 4) == (2, 1, 1, 1, 1, 0)
    assert _limits(0, 0, inc, 4) == (0, 0, 0, 0, 0, 0)
    # an ejectile that is not included contributes nothing
    off = [True, True, True, False, True, True, True, True]  # protons off (index 2 == type 1? no)
    assert _limits(1, 2, off, 4)[1] == 0


def test_gamma_cascade_conserves_flux_and_empties_the_level():
    """cascade.f90: the intensity leaves nex and arrives at the branch levels, exactly."""
    n = 4
    nuc = M.NucleusPopulation(
        zcomp=0, ncomp=0, Z=26, A=56, maxex=n - 1, nlast=n - 1,
        ex_mev=torch.linspace(0, 3, n, dtype=DTYPE), dex_mev=torch.ones(n, dtype=DTYPE),
        maxj=torch.zeros(n, dtype=torch.int64), jdis=torch.tensor([0.0, 2.0, 2.0, 4.0], dtype=DTYPE),
        parlev=torch.tensor([1, 1, -1, 1]), tau_s=torch.zeros(n, dtype=DTYPE),
        sep_mev={1: 11.2}, branch={3: [(1, 0.75), (0, 0.25)]},
        xspop_mb=torch.zeros((n, 41, 2), dtype=DTYPE), xspopex_mb=torch.zeros(n, dtype=DTYPE),
    )
    nuc.xspop_mb[3, 4, 1] = 100.0
    nuc.xspopex_mb[3] = 100.0
    out = M.gamma_cascade(nuc, 3)
    assert out == pytest.approx({1: 75.0, 0: 25.0})
    assert float(nuc.xspopex_mb[3]) == pytest.approx(0.0)
    assert float(nuc.xspop_mb[1, 2, 1]) == pytest.approx(75.0)
    assert float(nuc.xspop_mb[0, 0, 1]) == pytest.approx(25.0)
    assert float(nuc.xspopex_mb.sum()) == pytest.approx(100.0)


def test_exclusive_state_tracks_opennum_as_the_size_of_chanopen():
    st = ExclusiveState()
    assert st.opennum == 0
    st.chanopen.add((1, 0, 0, 0, 0, 0))
    st.chanopen.add((1, 0, 0, 0, 0, 0))
    assert st.opennum == 1


# --- injected gate (needs an instrumented dump) -------------------------------------------------


def test_binary_reproduces_the_discrete_level_partials():
    """A-mult, the `.Lnn` files: xsdisc = xspopex0 after the direct addend (binary.f90:266)."""
    from physics.hf.emission.score import PARSYM, _column

    d = _one()
    cases = load_binary_dump(d / "bin_inputs.txt")
    rs = []
    for case in cases:
        res = B.binary(case)
        for t, arr in res.xsdisc_mb.items():
            for nex in range(arr.shape[0]):
                f = d / f"{PARSYM[case.k0]}{PARSYM[t]}.L{nex:02d}"
                if not f.is_file():
                    continue
                ref = _column(f, "xs").get(round(case.e_inc_mev, 6))
                if ref is None or ref <= 1e-3:
                    continue
                rs.append(abs(np.log(max(float(arr[nex]), 1e-300) / ref)))
    assert rs, "no discrete-level partials above the floor in the dump"
    assert float(np.percentile(rs, 95)) <= TOL


def test_binary_reproduces_the_first_chance_population():
    """A-mult on binE*.out, including the ~14% of cells where `sfactor == 0` and binary.f90:236
    spreads pre-equilibrium with `spindis(sc, J) * pardis` instead (T9's `ungated_cells`)."""
    from physics.hf.emission.score import _read_binE

    d = _one()
    rs, n_fallback = [], 0
    for case in load_binary_dump(d / "bin_inputs.txt"):
        f = d / f"binE{case.e_inc_mev:08.3f}.out"
        if not f.is_file():
            continue
        res = B.binary(case)
        for t, tab in _read_binE(f).items():
            if t not in res.xspop_bine_mb:
                continue
            got = res.xspop_bine_mb[t].numpy()
            n = min(got.shape[0], tab["pop"].shape[0])
            live = tab["pop"][:n] > 1e-6
            assert not (live & (got[:n] <= 0)).any(), "port lost a populated cell"
            rs.append(np.abs(np.log(got[:n][live] / tab["pop"][:n][live])))
            g = case.grids[t]
            nl = min(g.nlast, g.maxex)
            if g.maxex > nl and case.flagpreeq:
                sf = res.sfactor[t].numpy()[nl + 1:n, : case.maxjph + 1, :]
                ppx = case.preeqpopex_mb[t].numpy()[nl + 1:n]
                n_fallback += int(((sf == 0.0) & (ppx[:, None, None] > 0)
                                   & live[nl + 1:, : case.maxjph + 1, :]).sum())
    assert rs
    assert float(np.percentile(np.concatenate(rs), 95)) <= TOL
    assert n_fallback > 0, "the spindis fallback branch was never exercised"


def test_exclusive_channels_reproduce_the_xs_files():
    """A-mult on xs*.tot and rp*.tot, with feedexcl/popexcl injected."""
    from physics.hf.emission.score import _column

    d = _one()
    cases = load_channel_dump(d / "ch_inputs.txt")
    chan = {int(f.name[2:8]): _column(f, "xs") for f in sorted(d.glob("xs[0-9]*.tot"))}
    rp = {(int(f.name[2:5]), int(f.name[5:8])): _column(f, "xs")
          for f in sorted(d.glob("rp[0-9]*.tot"))}
    rs = []
    for case in cases:
        out = exclusive_channels(case)
        e = round(case.e_inc_mev, 6)
        for code, table in chan.items():
            ref = table.get(e)
            if ref is None or ref <= 1e-3:
                continue
            rs.append(abs(np.log(max(out.xschannel_mb.get(code, 0.0), 1e-300) / ref)))
        for za, table in rp.items():
            ref = table.get(e)
            if ref is None or ref <= 1e-3:
                continue
            rs.append(abs(np.log(max(out.residual_mb.get(za, 0.0), 1e-300) / ref)))
    assert rs
    assert float(np.percentile(rs, 95)) <= TOL


def test_gamma_cascade_branching_matches_talys_feedexcl():
    """A-mult, cascade.f90: the share of a discrete level's flux going to each branch level is
    T2's branching ratio, which is what TALYS's own feedexcl(.,.,0,nex,k) carries."""
    from physics.hf.emission.score import score_cascade
    from physics.hf.talys_reference import REFERENCE_SET

    d = _one()
    tag = d.name.split("__")[-1]
    t = next((x for x in REFERENCE_SET if x.tag == tag), None)
    if t is None:
        pytest.skip(f"{tag} is not in the reference set")
    st = score_cascade(d, t.Z, t.A)
    if not st["n"]:
        pytest.skip("no discrete gamma feeding in this dump")
    assert st["n_inf"] == 0
    assert st["p95"] <= TOL


def test_the_published_gate_passes():
    if not GATE.is_file():
        pytest.skip("gate not scored yet")
    g = json.loads(GATE.read_text())
    # The only permitted infinity is a point where TALYS itself printed a negative cross section
    # (Bi-209 (n,alpha) to level 30 at 18 MeV): the metric calls a sub-floor reference `inf` even
    # when the port reproduces it exactly. §2's rule is not changed; the cause is counted.
    neg = g["summary"].get("negative_reference_points", 0)
    for key in ("levels", "cascade", "channels", "residual", "a_mult"):
        s = g["summary"][key]
        assert s["n"] > 0, key
        assert s["n_inf"] <= neg, (key, s, neg)
        assert s["worst_p95"] <= TOL, (key, s)
    assert g["summary"]["a_mult"]["runs"] == 14, "A-mult is gated on the 14 spherical targets"


# ================================================================================================
# EXCL: the multiple-emission feeding chain (emission/feeding.py)
# ================================================================================================


@pytest.fixture(scope="module")
def cascade():
    """A Cascade for Ca-40 + n. Ca-41 has |Z - N| = 1, which is what makes it the interesting
    target for the isotrans latch; nothing here touches the optical model, so it is cheap."""
    from physics.hf.emission.feeding import Cascade

    return Cascade(20, 40, 20.0)


def test_isotrans_is_spent_on_the_initial_compound_nucleus_of_the_first_energy(cascade):
    """`fisom` is read once per RUN and is then 1, which is NOT what `fiso` does.

    isotrans.f90:63-82 only overwrites an `fisom` entry still at -1, and input_gammapar.f90:103
    sets that -1 at input parsing -- but **multiple.f90:458-460 writes
    `fisom(0:6) = fisominit(type) = 1` immediately after multiple.f90:437 has formed `Fnorm` from
    it**. So the sentinel is live for the initial compound nucleus at the run's first incident
    energy and for nothing else: that nucleus decays with `Fnorm = 1 / ff` over ALL of its bins,
    every other nucleus at every other energy with `Fnorm = 1`.

    This test used to assert that the first nucleus's value was inherited by every later one,
    which is what EXCL documented and what made Ca-40 the only failing row of A-mult at
    `feedexcl` p95 0.405 = |ln(1.5)|. `fisom(-1)` is outside the reset loop and does latch, but
    isotrans never gives it anything but 1."""
    first = cascade.fisom(0, 0)  # Ca-41: Z = 20, N = 21, so ff(0) = 1.5
    assert first[0 + 1] == pytest.approx(1.0 / 1.5)
    assert list(cascade.fisom(0, 0)) == list(first)  # reading it does not spend it
    for zn in ((1, 0), (0, 1), (0, 2)):  # K-40, Ca-40 (Z == N, ff(0) = 2), Ca-39 (ff(0) = 1.5)
        assert np.allclose(cascade.fisom(*zn), 1.0), zn


def test_fisom_is_the_declared_first_energy_not_the_first_call():
    """The sentinel belongs to (initial CN, the FIRST energy of the run's declared grid). A
    Cascade handed that grid must give `Fnorm = 1 / ff` there and 1 at every other energy, in
    whatever order the energies are computed -- otherwise an energy subset, an on-demand batched
    width build and a sharded run each latch a different energy and disagree."""
    from physics.hf.emission.feeding import Cascade

    grid = (0.001, 0.1, 1.0, 14.0)
    cas = Cascade(20, 40, 20.0, energies=grid)
    seen = {}
    for e in reversed(grid):  # deliberately the wrong way round
        st = cas.new_energy(25.0, e_inc_mev=e)
        seen[e] = float(cas.fisom(0, 0, st)[1])
    assert seen == {0.001: pytest.approx(1.0 / 1.5), 0.1: 1.0, 1.0: 1.0, 14.0: 1.0}
    # a subset that does not contain the run's first energy latches nowhere
    sub = Cascade(20, 40, 20.0, energies=grid)
    st = sub.new_energy(25.0, e_inc_mev=14.0)
    assert float(sub.fisom(0, 0, st)[1]) == 1.0
    # a Cascade with no declared grid is a one-energy run
    assert float(Cascade(20, 40, 20.0).fisom(0, 0)[1]) == pytest.approx(1.0 / 1.5)


def test_exgrid_latches_are_cleared_per_incident_energy(cascade):
    """reacinitial.f90:503-508 zeroes Exmax and maxex once per energy and re-seeds Exmax(0, 0)."""
    a = cascade.new_energy(30.0)
    cascade.propagate_exmax(a, 0, 0)
    assert float(a.exmax[0, 0]) == pytest.approx(30.0, rel=1e-6)
    assert float(a.exmax[0, 1]) > 0.0
    b = cascade.new_energy(12.0)
    assert float(b.exmax[0, 0]) == pytest.approx(12.0, rel=1e-6)
    assert float(b.exmax[0, 1]) == 0.0  # not propagated yet: a fresh latch
    assert b.spec == {} and b.maxex == {}


def test_exmax_propagation_is_the_separation_energy_chain(cascade):
    st = cascade.new_energy(25.0)
    cascade.propagate_exmax(st, 0, 0)
    s_n = float(cascade.m.s_mev[0, 0, 1])
    assert float(st.exmax[0, 1]) == pytest.approx(25.0 - s_n, rel=1e-5)


def test_nlast_is_unclamped_and_nlast_grid_is_not(cascade):
    """`discfactor` divides by NL - Ntop with TALYS's raw Nlast (densprepare.f90:170), while the
    grid only holds levels up to maxex. A nucleus whose Exmax stops below its last discrete level
    is exactly where the two differ."""
    st = cascade.new_energy(25.0)
    cascade.propagate_exmax(st, 0, 0)
    for zc in range(3):
        for nc in range(4):
            cascade.propagate_exmax(st, zc, nc)
    seen = False
    for zc in range(3):
        for nc in range(4):
            if float(st.exmax[zc, nc]) <= 0.0 and (zc, nc) != (0, 0):
                continue
            sp = cascade.spec(st, zc, nc)
            assert sp.nlast_grid == min(sp.nlast, sp.maxex)
            assert sp.nlast_grid <= sp.nlast
            seen = seen or sp.nlast_grid < sp.nlast
            # exgrid leaves maxJ at numJ wherever it never wrote (reacinitial.f90:509)
            if sp.maxex <= sp.nlast:
                assert (sp.maxj == 40).all()
    assert seen, "no nucleus in this tree has a grid shorter than its level scheme"


def test_nexmax_of_a_mother_bin_drops_one_grid_point_for_composite_ejectiles(cascade):
    """multiple.f90:519-521: the reference energy is the TOP of the mother bin, and for a
    composite ejectile TALYS additionally removes egrid(ebegin(type))."""
    st = cascade.new_energy(25.0)
    cascade.propagate_exmax(st, 0, 0)
    sp = cascade.spec(st, 0, 0)
    nxm = cascade.nexmax(st, sp, sp.maxex)
    assert nxm[0] == sp.maxex - 1  # gamma: the bin below, always
    assert nxm[1] >= 0
    assert set(nxm) == set(range(7))
    lo = cascade.nexmax(st, sp, max(sp.nlast_grid + 1, 1))
    assert lo[1] <= nxm[1]  # a lower mother bin cannot reach higher
    assert lo[0] == max(sp.nlast_grid + 1, 1) - 1


def test_feeding_gate_numbers_are_inside_the_amult_tolerance():
    p = Path("docs/results/hf-feeding-gate.json")
    if not p.exists():
        pytest.skip("hf-feeding-gate.json not built on this tree")
    g = json.loads(p.read_text())
    assert g["tol"] == TOL
    for r in g["runs"]:
        assert r["popexcl"]["p95"] is not None
        assert r["popexcl"]["p95"] <= TOL, (r["run"], r["popexcl"])
