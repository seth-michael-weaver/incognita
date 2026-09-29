"""NODUMP: the engine runs any nuclide at any energy with no TALYS dump.

`engine.ChainedFull.families` used to be three entries long -- `preequilibrium_inverse_xs`,
`direct_dwba` and `structure_scalars` (`docs/results/hf-e2e.md` §1) -- and every one of them was
read off a per-target instrumented TALYS run. These tests gate the three replacements against the
dump values they replace, at the tolerance of the component each comes from
(`docs/results/hf-engine-gates.md` §3), and then pin the property the whole task is for: the
engine takes (Z, A) and an incident energy grid and nothing else.

The dump-backed tests skip where the reference runs are not on the box; the last two do not need
them at all, which is the point.
"""

from __future__ import annotations

import tarfile
from pathlib import Path

import numpy as np
import pytest
import torch

REPO = Path(__file__).resolve().parents[2]
RUNS = Path.home() / "hf_t10/runs"
WORK = Path.home() / "hf_t10/score_work"
DECLARED = None  # filled at import from talys_reference


def _declared():
    from physics.hf.talys_reference import ENERGIES_MEV

    return tuple(ENERGIES_MEV)


def _work(tag: str) -> Path:
    from physics.hf import reference

    if not reference.available("block_index"):  # the parsed reference tables, not in a public clone
        pytest.skip("no parsed TALYS reference tables (INCOGNITA_HF_REFERENCE)")
    d = WORK / f"default__{tag}"
    if not (d / "bin_inputs.txt").is_file():
        src = RUNS / f"default__{tag}.tar.gz"
        if not src.is_file():
            pytest.skip(f"no reference run for {tag}")
        WORK.mkdir(parents=True, exist_ok=True)
        with tarfile.open(src) as tf:
            tf.extractall(WORK, filter="data")
    return d


def _rel(a, b):
    a, b = np.asarray(a, float).reshape(-1), np.asarray(b, float).reshape(-1)
    m = np.abs(a) > 1e-12
    return np.abs(b[m] - a[m]) / np.abs(a[m]) if m.any() else np.zeros(0)


# ------------------------------------------------------------------------------------------
# structure_scalars
# ------------------------------------------------------------------------------------------


@pytest.mark.parametrize("tag,Z,A", [("Fe056", 26, 56), ("Ca040", 20, 40), ("Pb208", 82, 208)])
def test_structure_scalars_reproduce_the_dumped_record(tag, Z, A):
    """A-struct, extended to the scalars `ChainedFull` used to read: `Ltarget`, the target's spin,
    parity and excitation energy, `popeps`, `xseps`, `maxZ`/`maxN`, `maxchannel`, `Ninclow`,
    `specmass` and `parinclude`/`parskip`. Every one is exact, not approximate: they are T3's
    resolved input record and one row of T2's level scheme, not a computed quantity.

    `popeps` and `xseps` are `real(sgl)` in TALYS, so the port rounds them the same way; reading
    `1e-3` where TALYS holds `1.0000000474974513e-3` is a real difference to a `<` test."""
    from physics.hf.emission.dumps import load_binary_dump, load_channel_dump
    from physics.hf.structure.scalars import structure_scalars

    d = _work(tag)
    b = load_binary_dump(d / "bin_inputs.txt")[0]
    c = load_channel_dump(d / "ch_inputs.txt")[0]
    sc = structure_scalars(Z, A, _declared())
    assert (sc.k0, sc.ltarget, sc.targetspin2, sc.target_parity) == (
        b.k0, b.ltarget, b.targetspin2, b.target_parity)
    assert (sc.pespinmodel, sc.numj) == (b.pespinmodel, b.numj)
    # `maxJph` is `preeqinit`'s and the dump carries 0 below `epreeq`; the engine gates it on
    # `flagpreeq` for that reason (`engine._BuiltInputs.shell`).
    assert sc.maxjph == 30 and b.maxjph == 0 and not b.flagpreeq
    assert sc.popeps_mb == pytest.approx(b.popeps_mb, rel=1e-15)
    assert sc.xseps_mb == pytest.approx(b.xseps_mb, rel=1e-15)
    assert (sc.maxz, sc.maxn, sc.zinit, sc.ninit) == (c.maxz, c.maxn, c.zinit, c.ninit)
    assert (sc.maxchannel, sc.ninclow) == (c.maxchannel, c.ninclow)
    assert sc.targete_mev == pytest.approx(c.targete_mev, abs=1e-12)
    assert sc.specmass == pytest.approx(c.specmass, rel=1e-6)
    assert list(sc.parinclude) == list(c.parinclude)
    assert list(sc.parskip) == list(c.parskip)
    assert sc.flagfission == c.flagfission and sc.flaginitpop == c.flaginitpop


def test_flagpreeq_comes_from_the_resolved_onset_not_the_sentinel():
    """`epreeq` is a -1 sentinel in `default_options` and `Einc < -1.` is false at every energy,
    so an unresolved read turns pre-equilibrium ON at 1 keV. Fe-56's onset is its last discrete
    level (nuclides.f90:259), and the reference run dumps `exciton*.out` from 5 MeV up."""
    from physics.hf.preeq.chain import preeq_energies
    from physics.hf.structure.scalars import structure_scalars

    sc = structure_scalars(26, 56, _declared())
    assert sc.options.epreeq_mev > 1.0
    assert not sc.flags(0.001)["flagpreeq"]
    assert sc.flags(20.0)["flagpreeq"] and sc.flags(20.0)["flagmulpre"]
    assert preeq_energies(26, 56, _declared()) == [5.0, 6.0, 8.0, 10.0, 12.0, 14.0, 16.0, 18.0,
                                                   20.0]


def test_direct_case_resolves_the_onsets_so_flaggiant_is_per_energy():
    """`direct.prepare.case` used to call `resolve_structure_defaults` with a signature that did
    not exist, inside `except TypeError`, so `flaggiant` fell back to `flaggiant0` -- true at
    EVERY energy, where `giant.f90` writes a block only above the pre-equilibrium onset."""
    from physics.hf.direct.prepare import case

    en = _declared()
    assert not case("Fe056", 0.001, en).flaggiant
    assert case("Fe056", 14.0, en).flaggiant


# ------------------------------------------------------------------------------------------
# preequilibrium_inverse_xs
# ------------------------------------------------------------------------------------------


def test_chained_preeq_inputs_match_the_injected_ones():
    """A-pe's inputs: `xsreac` from T5's inverse channels instead of `cross_<p>.tot`, the pairing
    energies from T6 instead of the `ld*.gs` headers, `xsflux` and `xsdirdisc` from T5 + T12/T13
    instead of `talys.out` and `directE*.out`. Everything else in `PreeqInputs` is shared, so
    this isolates the five inputs."""
    _work("Fe056")  # the injected arm needs the parsed reference tables
    from physics.hf.preeq.prepare import energies_for, prepare

    en = energies_for("Fe056")
    a, _ = prepare("Fe056", energies=en)
    b, _ = prepare("Fe056", energies=en, chained=True, enincmax_mev=20.0)
    for name, tol in (("xsreac_mb", 5e-4), ("xsflux_mb", 5e-3), ("ecomp_mev", 1e-5),
                      ("pair_res_mev", 1e-5), ("pair_cn_mev", 1e-5)):
        r = _rel(getattr(a, name).numpy(), getattr(b, name).numpy())
        assert r.size and float(np.percentile(r, 95)) <= tol, (name, float(r.max()))
    # The UPPER support edge of `xsreac` is part of the physics: `knockout` reads
    # `sigav = xsreac(type2, eend(type2))`, and filling past `eendmax(type)` -- where `inverse`
    # leaves a hard zero (inverseecis.f90:402) -- inflates `denomki` and shrinks the alpha
    # knockout ~25x. The lower edge is not: TALYS's `real(sgl)` underflows the sub-barrier
    # channels to 0 one grid point before float64 does (3.9e-46 for the helion, 1.7e-53 for the
    # alpha), which is a print format, not a cut.
    A, B = a.xsreac_mb.numpy(), b.xsreac_mb.numpy()
    for t in range(1, 7):
        ia, ib = np.flatnonzero(np.abs(A[0, t]) > 0), np.flatnonzero(np.abs(B[0, t]) > 0)
        assert ia.size and ib.size and ia.max() == ib.max(), t
        assert abs(int(ib.min()) - int(ia.min())) <= 1, t
        assert float(np.abs(B[0, t][: int(ia.min())]).max(initial=0.0)) < 1e-40, t


def test_chained_preeq_output_matches_the_injected_one():
    """The same exciton model on the two input sets: T8's per-type totals and the two sums
    `compnorm` subtracts."""
    _work("Fe056")
    from physics.hf.compound.pop_reference import _preeq

    ea, ra, _ = _preeq("Fe056")
    eb, rb, _ = _preeq("Fe056", declared=_declared())
    assert ea == eb
    for key in ("xspreeqtot", "xspreeqsum", "xspreeqdiscsum"):
        r = _rel(np.asarray(ra[key], float), np.asarray(rb[key], float))
        assert float(r.max()) <= 1e-3, (key, float(r.max()))


# ------------------------------------------------------------------------------------------
# direct_dwba
# ------------------------------------------------------------------------------------------


@pytest.mark.parametrize("e_inc", [5.0, 14.0, 20.0])
def test_chained_direct_matches_the_dumped_direct(e_inc):
    """A-direct (tolerance 5e-2) on what T12 actually consumes: the discrete total, the
    collective continuum and the giant-resonance total, computed by T13's ECIS on T4's own
    optical-model parameters instead of read from `directE*.out`."""
    _work("Fe056")
    from physics.hf.compound.pop_reference import _giant

    a, ga = _giant("Fe056", e_inc)
    b, gb = _giant("Fe056", e_inc, declared=_declared())
    assert ga == gb
    for name in ("xsdirdisctot_mb", "xscollconttot_mb", "xsgrtot_mb"):
        x, y = float(getattr(a, name)), float(getattr(b, name))
        assert abs(y - x) <= 5e-2 * abs(x) + 1e-9, (name, x, y)


def test_direct_is_off_below_the_preequilibrium_onset():
    """`flaggiant` false means `direct` returns zeros for everything but the discrete DWBA, which
    is itself zero below the first excited level."""
    from physics.hf.direct.chain import direct_result

    res, giant = direct_result("Fe056", 0.001, _declared())
    assert not giant
    assert float(res.xsgrtot_mb) == 0.0 and float(res.xsdirdisctot_mb) == 0.0


# ------------------------------------------------------------------------------------------
# the built BinaryInputs / ChannelInputs shell
# ------------------------------------------------------------------------------------------


def test_built_binary_inputs_match_the_dumped_ones():
    """The shell `ChainedFull` used to take from `bin_inputs.txt`: the residual grids, the
    per-level `xsdirdisc` and the four per-type totals.

    `xsdirdisc` at binary.f90's entry is NOT only the DWBA -- preeqtotal.f90:186-192 adds
    `xspreeqdisc(type, i)` for EVERY ejectile, which is why the dump carries a non-zero
    `xsdirdisctot` for the proton, deuteron and alpha channels of a neutron-induced run. Leaving
    it out cost Fe-56's (n,alpha) 10% above 8 MeV."""
    from physics.hf.compound.norm_reference import addends
    from physics.hf.emission.dumps import load_binary_dump
    from physics.hf.emission.feeding import Cascade
    from physics.hf.engine import _BuiltInputs

    d = _work("Fe056")
    ref = {round(b.e_inc_mev, 6): b for b in load_binary_dump(d / "bin_inputs.txt")}[14.0]
    declared = _declared()
    cas = Cascade(26, 56, max(declared), energies=declared)
    built = _BuiltInputs(cas, "Fe056", declared,
                         addends("Fe056", 26, 56, list(declared), declared))
    b, _c = built.shell(1, 14.0)
    for t, g0 in ref.grids.items():
        g1 = b.grids[t]
        assert (g1.maxex, g1.nlast, g1.zix, g1.nix) == (g0.maxex, g0.nlast, g0.zix, g0.nix)
        for f, tol in (("ex_mev", 1e-6), ("dex_mev", 1e-6), ("ald", 1e-4), ("spincut", 1e-4)):
            r = _rel(getattr(g0, f).numpy(), getattr(g1, f).numpy())
            assert not r.size or float(r.max()) <= tol, (t, f, float(r.max()))
        assert (g1.maxj == g0.maxj).all() and (g1.parlev == g0.parlev).all()
        assert torch.allclose(g1.jdis, g0.jdis)
    for name, tol in (("xsdirdisctot_mb", 5e-3), ("xspreeqtot_mb", 5e-3),
                      ("xsgrtot_mb", 5e-3)):
        for t in range(7):
            x = float(getattr(ref, name).get(t, 0.0))
            y = float(getattr(b, name).get(t, 0.0))
            assert abs(y - x) <= tol * abs(x) + 1e-9, (name, t, x, y)
    assert float(b.xselasinc_mb) == pytest.approx(ref.xselasinc_mb, rel=1e-4)
    assert float(b.xsracape_mb) == ref.xsracape_mb


# ------------------------------------------------------------------------------------------
# the property the task is for
# ------------------------------------------------------------------------------------------


def test_chained_full_injects_nothing_by_default():
    from physics.hf.engine import ChainedFull

    assert ChainedFull(Z=26, A=56, declared_energies=_declared()).families == ()
    # the old arm stays reachable, and it is the A/B's other column
    assert ChainedFull(run_dir=Path("x"), Z=26, A=56,
                       inject=("direct_dwba",)).families == ("direct_dwba",)
    with pytest.raises(ValueError):
        ChainedFull(Z=26, A=56).cases()  # no grid, no dump to read one off


def test_the_engine_runs_a_nuclide_with_no_reference_run():
    """Ti-48 is not in `talys_reference.REFERENCE_SET`; nothing under `features/hf_reference/`
    or `~/hf_t10/runs` mentions it, and this opens no file that does. Two energies, so the test
    is a smoke test; `harness/nodump_predict.py` scores three such nuclides against TALYS at all
    23 (`docs/results/hf-nodump-predict.json`)."""
    from physics.hf.engine import ChainedFull, run

    torch.set_num_threads(2)
    res = run(injection=ChainedFull(Z=22, A=48, declared_energies=_declared(),
                                    energies=(0.001, 14.0)))
    assert res.injected == ()
    ng = res.channels_mb["xs000000"]
    assert float(ng[0]) > float(ng[1]) > 0.0  # capture falls with energy
    assert float(res.totals_mb["nonelastic"][1]) > float(res.totals_mb["nonelastic"][0]) > 0.0
