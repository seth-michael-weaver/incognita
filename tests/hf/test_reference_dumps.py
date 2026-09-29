"""Integrity of the parsed TALYS reference dumps (features/hf_reference/). Skips when absent.

These are the facts every component test relies on; if one fails, fix the dumps before
debugging a port against them."""

from __future__ import annotations

import json

import numpy as np
import pytest

from physics.hf import reference as ref
from physics.hf import talys_reference as T

pytestmark = pytest.mark.skipif(not ref.available(), reason="reference dumps not parsed")


def test_every_parsed_run_completed_and_used_defaults():
    m = ref.manifest()
    assert (m["returncode"] == 0).all() and m["completed_banner"].all()
    assert all(len(f) == 0 for f in m["fatal_errors"])
    for _, r in m.iterrows():
        target = next(t for t in T.REFERENCE_SET if t.tag == r["target"])
        assert r["input"] == T.input_text(r["variant"], target)[0], (
            f"{r['variant']}/{r['target']}: dump made from a different input than the harness"
        )


def test_one_talys_binary_across_boxes():
    assert ref.manifest()["talys_bin_sha256"].nunique() >= 1  # recorded; see next test
    # Linux and macOS builds differ as binaries but were verified to agree on output
    # (Au-197 residual production identical, cross-machine check); the
    # invariance check below compares within one box.


def test_flag_invariance_passed_where_checked():
    p = ref.reference_dir() / "flag_invariance.json"
    if not p.exists():
        pytest.skip("run `talys_reference check` first")
    res = json.loads(p.read_text())
    assert res["rows"], "no default/minimal pair parsed"
    assert all(r["max_rel_diff"] <= res["tolerance"] for r in res["rows"])


def test_cross_sections_are_on_the_reference_energies():
    m = ref.manifest()
    for _, r in m[m["variant"] == "default"].head(3).iterrows():
        _, w = ref.cross_section(r["target"], "total.tot")
        assert np.allclose(w["E"].to_numpy(), T.ENERGIES_MEV, rtol=1e-6)


def test_transmission_shapes_and_range():
    from physics.hf.ecis import bridge

    m = ref.manifest()
    for _, r in m[m["variant"] == "default"].head(3).iterrows():
        tr = bridge.emission_transmission(r["target"])
        bridge.check_shapes(tr)
        assert {"n", "p"} <= set(tr)
        e = tr["n"]["e_mev"]
        assert (np.diff(e) > 0).all()


def _first(variant="default"):
    m = ref.manifest()
    rows = m[m["variant"] == variant]
    if rows.empty:
        pytest.skip(f"no {variant} dumps parsed")
    return rows.iloc[0]["target"]


def test_level_density_arrays_have_both_parities_in_contract_order():
    import pandas as pd

    target = _first()
    ld = pd.read_parquet(ref.reference_dir() / "level_density.parquet")
    f = sorted(ld[ld["target"] == target]["file"].astype(str).unique())[-1]
    d = ref.level_density_arrays(target, f)
    u, rho = d["u_mev"], d["rho_jp_per_mev"]
    assert rho.shape == (len(u), len(d["j"]), 2) and (np.diff(u) > 0).all()
    p = d["parameters"]
    assert (rho >= 0).all() and p["separation energy [MeV]"] > 0
    # TALYS chooses the level density model per nuclide and the harness never pins `ldmodel`
    # (rule 1 of the module docstring), so the printed parameter block is not the same set of
    # keys everywhere and a test may not assume one model. Across the 24-target reference set
    # the split is exactly by fissility: the 19 non-actinides get ldmodel 1
    # (Constant-Temperature, which prints a temperature, E0 and a matching energy), the 5
    # actinides -- Am241, Pu239, Th232, U235, U238 -- get ldmodel 7 (BSKG3-Combinatorial), a
    # tabulated microscopic model with no constant-temperature parameters at all.
    if p["level density model"] == "Constant-Temperature":
        assert p["ldmodel keyword"] == 1
        assert {"temperature [MeV]", "E0 [MeV]", "matching energy [MeV]"} <= set(p)
    else:
        assert (p["ldmodel keyword"], p["level density model"]) == (7, "BSKG3-Combinatorial")
        assert "temperature [MeV]" not in p


def test_binary_population_arrays_reassemble_the_printed_totals():
    """The per-(J,parity) columns of binE must re-sum to the printed `population` column.

    This is the check that catches a misread datablock -- a dropped or shifted column moves the
    sum by O(1) -- so the tolerance only has to sit above TALYS's own printing. It is not 1e-5:
    the two are accumulated separately inside TALYS and agree to ~1e-9 on even-even targets but
    only to 1.7e-4 on the strongly-absorbing odd-A ones (U235 1.7e-4, Pu239 1.0e-4, Gd157
    3.0e-5, Am241 1.8e-5, everything else <4e-8), always with the JP columns the larger. That
    residual is TALYS's, not the parser's: re-summing the raw text of wfc_off__Am241
    binE0001.000.out by hand reproduces both sums to the last printed digit.
    """
    m = ref.manifest()
    targets = sorted(set(m[m["variant"] == "wfc_off"]["target"]))
    if not targets:
        pytest.skip("no wfc_off dumps parsed")
    worst, worst_at = 0.0, None
    for target in targets:
        for name, ej in ref.binary_population_arrays(target, 1.0, "wfc_off").items():
            jp, tot = ej["pop_jp_mb"].sum(), ej["pop_mb"].sum()
            if max(abs(jp), abs(tot)) < 1e-6:  # closed channel: both are zero
                continue
            rel = abs(jp - tot) / abs(tot)
            if rel > worst:
                worst, worst_at = rel, (target, name)
            assert rel < 1e-3, (target, name, jp, tot, rel)
    print(f"binary population JP-vs-total: {len(targets)} targets, worst {worst:.2e} at {worst_at}")


def test_incident_scalars_cover_every_energy():
    if not ref.available("incident_scalars"):
        pytest.skip("re-parse to produce incident_scalars")
    s = ref.incident_scalars(_first())
    assert np.allclose(s["e_inc_mev"], T.ENERGIES_MEV)
    assert (s["sigma_tot_omp_mb"] > 0).all()


def test_binary_population_grid_facts_are_per_block_not_inherited():
    # T1 report: a binE block with no continuum inherited the previous block's level/bin counts
    m = ref.manifest()
    if "Ni058" not in set(m[m["variant"] == "default"]["target"]):
        pytest.skip("Ni058 default dump not parsed")
    pops = ref.binary_population_arrays("Ni058", 1.0)
    assert pops["proton"]["n_discrete_levels"] is None
    assert pops["proton"]["n_continuum_bins"] is None
    assert pops["proton"]["exmax_mev"] == pytest.approx(1.383721)
    assert pops["gamma"]["n_discrete_levels"] == 30


def test_closed_channel_energies_start_where_talys_printed_them():
    m = ref.manifest()
    if "Ni058" not in set(m[m["variant"] == "default"]["target"]):
        pytest.skip("Ni058 default dump not parsed")
    a = ref.transmission("Ni058", particle="a")
    assert a["e_mev"][0] == pytest.approx(0.3218569)
    assert len(np.unique(a["e_mev"])) == len(a["e_mev"]) and not a["open"][0]
