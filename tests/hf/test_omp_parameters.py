"""T4 OMP parameters and radial potentials against TALYS's omppar_<k>.out and omp.out (gates
A-omppar p95 |ln(port/TALYS)| <= 1e-5 and A-omppot <= 1e-4, docs/results/hf-engine-gates.md).

Both gates run over **all 24 reference targets** -- spherical, deformed and actinide. §3 of the
gates doc gated only the spherical ones "until the ECIS task (T13) lands"; it has, so the other
ten are in. The T14 single-precision floor is applied as written, `max(tolerance, 2 delta)` with
delta from docs/results/hf-sgl-floor.json; for these two families delta is 1.8e-7 and 0, so
neither tolerance moves.

Two things the actinides need and the spherical targets do not:

  * their default neutron OMP is RIPL 2408, retrieved by `physics.hf.omp.ripl` (T4RIPL);
  * the eleven `colltype R` targets print ECIS's **deformed** lambda = 0 form factor in omp.out,
    not the spherical Woods-Saxon, so they are scored with
    `potential.rotational_radial_potential`. `colltype V` (Ca-40) prints the spherical one,
    because the vibrational model deforms only the transition form factors.

Structure inputs other tasks own are read here until they land: the target mass on the ECIS card
comes from structure/masses/ame2020 (TODO(T2)); the collective type is read by
parameters._colltype from structure/deformation (TODO(T2)); the coupled band comes from T13's
`ecis.reference.coupled_band`.

omp.out prints the radius as `iR * step` with ECIS's step rounded to f8.5, which moves the outer
radii by up to 5e-6 fm per point and the potential there by ~1e-4. The true step is one number for
all four columns, so it is fitted once in the +/-5e-6 window against all four together and all
four are then gated with it -- one nuisance parameter, four gated columns.

Skips (does not fail) when the reference dumps are absent.
"""

from __future__ import annotations

import json
import re
from functools import cache

import numpy as np
import pytest
import torch

from physics.hf import reference as ref
from physics.hf.core.constants import PARTICLE_INDEX, nuclide_symbol, talys_structure_path
from physics.hf.input.defaults import default_options, default_params
from physics.hf.omp import parameters as P
from physics.hf.omp.potential import (
    ecis_card_value,
    radial_potential,
    rotational_radial_potential,
)

# A-omppar / A-omppot with the T14 floor rule (hf-engine-gates.md §3): tolerance = max(tol, 2*delta)
SGL_FLOOR = {"omp_parameters": 1.8e-7, "omp_potential": 0.0}  # docs/results/hf-sgl-floor.json
TOL_PAR = max(1e-5, 2 * SGL_FLOOR["omp_parameters"])
TOL_POT = max(1e-4, 2 * SGL_FLOOR["omp_potential"])
DT = torch.float64

have_par = pytest.mark.skipif(
    not (ref.available("omp_parameters") and ref.available("manifest")),
    reason="reference dumps not parsed",
)
have_pot = pytest.mark.skipif(
    not (ref.available("omp_potential") and ref.available("manifest")),
    reason="reference dumps not parsed",
)


def _structure_ok() -> bool:
    try:
        talys_structure_path()
        return True
    except FileNotFoundError:
        return False


have_structure = pytest.mark.skipif(not _structure_ok(), reason="TALYS structure database absent")


def _opts(Z, A):
    o = default_options(Z, A)
    return o, default_params(Z, A, o)


def _ame_mass(Z: int, A: int) -> float:  # TODO(T2): structure.masses
    f = talys_structure_path() / "masses" / "ame2020" / f"{nuclide_symbol(Z)}.mass"
    for line in f.read_text().splitlines():
        if int(line[4:8]) == A:
            return float(line[8:20])
    raise KeyError((Z, A))


# ---------------------------------------------------------------------------- database readers
@have_structure
def test_kd03_reads_the_global_parameter_file_in_talys_order():
    n, p = P.kd03(1), P.kd03(2)
    assert n["v1_0"] == pytest.approx(59.30, rel=1e-6) and n["rv_0"] == pytest.approx(
        1.3039, rel=1e-6
    )
    # particle-specific lines go to the particle they belong to
    assert n["v2_0"] == pytest.approx(0.007228, rel=1e-5) and p["v2_0"] == pytest.approx(
        0.007067, rel=1e-5
    )
    assert n["w1_0"] == pytest.approx(12.195, rel=1e-6) and p["w1_0"] == pytest.approx(
        14.667, rel=1e-6
    )
    assert n["ad_0"] == pytest.approx(0.5446, rel=1e-6) and p["ad_0"] == pytest.approx(
        0.5187, rel=1e-6
    )
    assert n["rc_A2"] == pytest.approx(12.994, rel=1e-6) and n["wso2_0"] == pytest.approx(160.0)


@have_structure
def test_local_file_and_colltype():
    rec, disp = P.read_local_omp(26, 56, 1)
    assert (rec["rv0"], rec["av0"], rec["v1"], rec["w2"]) == pytest.approx(
        (1.186, 0.663, 56.8, 80.0), rel=1e-6
    )
    assert rec["ef"] == pytest.approx(-9.42, rel=1e-6) and not disp
    assert P.read_local_omp(26, 99, 1) is None
    o, _ = _opts(26, 56)
    assert (
        P._colltype(20, 40, o) == "V"
        and P._colltype(25, 55, o) == "R"
        and P._colltype(26, 999, o) == "S"
    )


@have_structure
def test_d1_is_reduced_twice_for_a_deformed_nucleus_with_a_local_file():
    """omppar.f90:217 and :267 both apply 0.85; the Ca040 dump confirms 0.7225 (A-omppar)."""
    o, _ = _opts(20, 40)
    sph = P.omppar(20, 40, o, colltype="S")
    vib = P.omppar(20, 40, o, colltype="V")
    assert vib[1].d1_mev == pytest.approx(0.85**2 * sph[1].d1_mev, rel=1e-12)
    assert not vib[1].ompglobal
    # a nucleus with only global parameters is reduced once
    g_s = P.omppar(25, 56, o, colltype="S")[1]
    g_r = P.omppar(25, 56, o, colltype="R")[1]
    assert g_s.ompglobal and g_r.d1_mev == pytest.approx(0.85 * g_s.d1_mev, rel=1e-12)


@have_structure
def test_proton_coulomb_radius_is_always_kd03():
    o, _ = _opts(26, 56)
    nuc = P.omppar(26, 56, o)
    kd = P.kd03(2)
    rc = kd["rc_0"] + kd["rc_A"] * 56 ** (-2 / 3) + kd["rc_A2"] * 56 ** (-5 / 3)
    assert nuc[2].rc0_fm == pytest.approx(rc, rel=1e-12) and nuc[1].rc0_fm == 0.0


# ---------------------------------------------------------------------------- behaviour
@have_structure
def test_batched_grid_differentiable_and_scope_guards():
    o, p = _opts(26, 56)
    e = torch.logspace(-3, 1.3, 7, dtype=DT)
    g = P.omp_parameter_grid([(26, 30), (25, 31)], (1, 2, 6), e, p, o)
    assert g.v_mev.shape == (2, 3, 7) and g.stack().shape == (2, 3, 7, 19)
    assert torch.isfinite(g.stack()).all()
    # adjust factors: gradients reach the Params tensor, and V scales with v1adjust
    p.values["v1adjust"] = p.values["v1adjust"].clone().requires_grad_(True)
    v = P.omp_parameters(26, 30, 1, e, p, o).v_mev
    (gv,) = torch.autograd.grad(v.sum(), p.values["v1adjust"])
    assert gv[1] == pytest.approx(float(v.detach().sum()), rel=1e-10) and gv[2] == 0
    # the actinide default retrieves RIPL 2408 by itself, and an explicit table still wins
    oa, pa = _opts(92, 238)
    auto = P.omp_parameters(92, 146, 1, e, pa, oa)
    assert float(auto.v_mev[0]) == pytest.approx(44.721, abs=1e-9)  # the table's first row
    table = P.OMPTable(torch.tensor([0.0, 30.0], dtype=DT), torch.ones(2, 19, dtype=DT))
    t = P.omp_parameters(92, 146, 1, e, pa, oa, tables={1: table})
    assert torch.allclose(t.stack(), torch.ones(7, 19, dtype=DT))
    # ... and only on the nucleus TALYS attaches it to, (Zix, Nix) = (parZ(1), parN(1))
    assert float(P.omp_parameters(92, 145, 1, e, pa, oa).v_mev[0]) != pytest.approx(44.721)


# ---------------------------------------------------------------------------- RIPL retrieval
# Every number below is TALYS's own: `om_retrieve` was compiled standalone against the shipped
# structure/optical/ripl database and its `omp-table.dat` read off. The port reproduces the whole
# table bit for bit (130 energies x 18 columns) for all five actinides and for eight further RIPL
# potentials spanning imodel 0/1/4, idr 0/2/3, irel 0/1/2 and the Koning / Morillon-Romain /
# standard families; the rows pinned here are the ends of those tables.
RIPL_ROWS = {
    # (iref, Z, A): (Ef, row at E = 0.001 MeV, row at E = 32.0 MeV)
    (2408, 92, 238): (-5.480, [44.7210, 1.2516, 0.6360, 0.0572, 1.2530, 0.6800, 3.3502, 1.1808,
                               0.6030, 2.1158, 1.1808, 0.6030, 5.7609, 1.1214, 0.5900, -0.0036,
                               1.1214, 0.5900],
                              [36.8070, 1.2516, 0.6360, 2.2123, 1.2530, 0.6800, -1.6422, 1.1808,
                               0.6030, 6.8822, 1.1808, 0.6030, 4.3111, 1.1214, 0.5900, -0.1613,
                               1.1214, 0.5900]),
    (2405, 26, 56): (-9.800, [52.6040, 1.1979, 0.6695, 0.2041, 1.1979, 0.6695, 0.0, 0.0, 0.0,
                              5.0482, 1.2818, 0.5353, 5.8559, 1.0163, 0.5900, -0.0116, 1.0163,
                              0.5900],
                             [41.4220, 1.1979, 0.6695, 2.9293, 1.1979, 0.6695, 0.0, 0.0, 0.0,
                              5.5522, 1.2818, 0.5353, 5.1523, 1.0163, 0.5900, -0.1981, 1.0163,
                              0.5900]),
    (1469, 12, 24): (-11.931, [47.6480, 1.2990, 0.5661, 0.3801, 1.2990, 0.5661, 2.8499, 1.2990,
                               0.5661, 5.6218, 1.2990, 0.5661, 5.4979, 1.2990, 0.5661, -0.0166,
                               1.2990, 0.5661],
                              [40.4570, 1.2990, 0.5661, 3.6522, 1.2990, 0.5661, -3.3410, 1.2990,
                               0.5661, 5.0797, 1.2990, 0.5661, 4.2671, 1.2990, 0.5661, -0.2103,
                               1.2990, 0.5661]),
    (419, 13, 27): (-10.392, [49.9600, 1.2000, 0.6500, 0.0011, 1.2000, 0.6500, 3.5059, 1.1100,
                              0.6400, 9.0880, 1.1100, 0.6400, 6.0000, 1.0170, 0.6000, 0.2000,
                              1.0170, 0.6000],
                             [45.8710, 1.2000, 0.6500, 1.8004, 1.2000, 0.6500, -3.8441, 1.1100,
                              0.6400, 2.8464, 1.1100, 0.6400, 5.1129, 1.0170, 0.6000, -0.1520,
                              1.0170, 0.6000]),
}  # fmt: skip


@have_structure
def test_ripl_library_reader_and_grid():
    from physics.hf.omp import ripl

    sdir = str(ripl._ripl_dir())
    p = ripl.read_om_parameter(2408, sdir)
    assert (p.imodel, p.izproj, p.iaproj, p.irel, p.idr) == (1, 0, 1, 1, 3)
    assert p.jrange == [1, 1, 0, 1, 1, 1] and p.jcoul == 0  # no real surface, no Coulomb card
    assert (p.izmin, p.izmax, p.iamin, p.iamax) == (90, 97, 228, 249)
    assert p.author.startswith("R.Capote")
    # the RIPL exponent shorthand: `-1.36700-3` is -1.367e-3 (rv = 1.57695 - 1.367e-3 A)
    assert p.r(1, 1, 1) == pytest.approx(1.57695) and p.r(1, 1, 7) == pytest.approx(-1.367e-3)
    assert p.p(2, 1, 21) == pytest.approx(350.0)  # Ea: the non-locality is on
    # the rigid-rotor coupling scheme is read but unused: TALYS takes its own deformations
    iso = p.isotopes[0]
    assert iso["iz"] == 90 and iso["defs"] == pytest.approx([0.178, 0.114, 0.02])
    assert ripl.read_om_index(sdir)[2408][:5] == ("n", 90, 97, 228, 249)
    # omppar.f90:296-315, accumulated in real(sgl) and printed f7.3
    raw, e = ripl.ripl_energies(20.0)
    assert len(e) == 130 and e[0] == 0.001 and e[-1] == 32.0
    assert e[9] == 0.01 and e[18] == 0.1 and e[57] == 4.0 and e[87] == 10.0
    assert raw[-1] != 32.0 and abs(raw[-1] - 32.0) < 1e-5  # the single-precision drift
    assert len(ripl.ripl_energies(5.0)[1]) == 102


@have_structure
@pytest.mark.parametrize("key", sorted(RIPL_ROWS))
def test_ripl_omp_table_reproduces_om_retrieve(key):
    from physics.hf.omp import ripl

    iref, Z, A = key
    ef_ref, first, last = RIPL_ROWS[key]
    e, vals, ef = ripl.omp_table(Z, A, iref, 20.0, check_range=False)
    assert ef == pytest.approx(ef_ref, abs=1e-9)
    assert vals[0, :18].tolist() == pytest.approx(first, abs=1e-9)
    assert vals[-1, :18].tolist() == pytest.approx(last, abs=1e-9)
    assert vals[:, 18].tolist() == [0.0] * len(e)  # om_retrieve prints no Coulomb radius


@have_structure
def test_ripl_range_check_and_unported_branches():
    from physics.hf.omp import ripl

    with pytest.raises(ValueError, match="out of range"):
        ripl.omp_table(26, 56, 2408, 20.0)  # Fe-56 is outside 90 <= Z <= 97
    with pytest.raises(KeyError):
        ripl.read_om_parameter(999999, str(ripl._ripl_dir()))
    with pytest.raises(ripl.RIPLNotPorted, match="soft-rotator"):
        ripl.omp_table(26, 56, 2602, 20.0, check_range=False)


@have_structure
def test_ripl_fermi_energy_is_the_mean_neutron_separation_energy():
    from physics.hf.omp import ripl

    sdir = str(ripl._ripl_dir())
    # `masses` truncates to four decimals (om_retrieve.f:3654); the table header then prints f7.3,
    # which is the number TALYS reads back into ef(0, 1, 1).
    for (Z, A), want in {(90, 232): -5.6123, (92, 235): -5.9213, (92, 238): -5.48,
                         (94, 239): -6.0901, (95, 241): -6.0895}.items():  # fmt: skip
        assert ripl.fermi_energy(Z, A, 0, 1, sdir) == pytest.approx(want, abs=1e-9)
        assert ripl.omp_table(Z, A, 2408, 20.0)[2] == pytest.approx(round(want, 3), abs=1e-9)


def test_alpha_avrigeanu_branches_and_radius():
    F = P.ompadjust(None, 6)
    e = torch.tensor([0.5, 10.0, 24.0, 30.0, 80.0], dtype=DT)
    prev = {c: torch.full_like(e, 7.0) for c in P.COLUMNS}
    out = P.opticalalpha(26, 56, e, 6, F, prev)
    a13 = 56 ** (1 / 3)
    assert out["rv_fm"][0] == pytest.approx(1.18 + 0.012 * 0.5) and out["rv_fm"][
        -1
    ] == pytest.approx(1.48)
    assert out["w_mev"][0] == pytest.approx(max(2.73 - 2.88 * a13 + 1.11 * 0.5, 0.0))
    # opticalalpha leaves rvd/avd/rvso/avso/rwso/awso at the Watanabe values
    for c in ("rvd_fm", "avd_fm", "rvso_fm", "avso_fm", "rwso_fm", "awso_fm"):
        assert torch.equal(out[c], prev[c])
    assert P.radius(12.0) == pytest.approx((5 / 3) ** 0.5 * 2.471) and P.radius(100.0) > 4.0
    with pytest.raises(NotImplementedError):
        P.opticalalpha(26, 56, e, 4, F, prev)


def test_ecis_card_rounding_is_straight_through():
    x = torch.tensor([53.096151, -0.0107106, 1234.567], dtype=DT, requires_grad=True)
    y = ecis_card_value(x)
    assert y.tolist() == pytest.approx([53.09615, -0.01071, 1235.0], abs=1e-9)
    (g,) = torch.autograd.grad(y.sum(), x)
    assert torch.equal(g, torch.ones(3, dtype=DT))


# ---------------------------------------------------------------------------- gates
@cache
def _manifest():
    return ref.manifest()


def _target_zas(target: str, variant: str):
    m = _manifest()
    row = m[(m["target"] == target) & (m["variant"] == variant)].iloc[0]
    return int(row["Z"]), int(row["A"]), str(row.get("shape", "spherical"))


def _par_cases():
    if not (ref.available("omp_parameters") and ref.available("manifest")):
        return []
    df = ref._family("omp_parameters")
    keys = df[["target", "variant", "file"]].drop_duplicates()
    return [tuple(r) for r in keys.itertuples(index=False)]


@have_par
@have_structure
def test_a_omppar_gate():
    rows = []
    for target, variant, file in _par_cases():
        Zt, At, shape = _target_zas(target, variant)
        meta, w = ref.table("omp_parameters", target, file, variant)
        meta = json.loads(meta) if isinstance(meta, str) else meta
        Z, A = int(meta["Z"]), int(meta["A"])
        k = PARTICLE_INDEX[file.split("_")[1][0]]
        o, p = _opts(Zt, At)
        e = torch.tensor(np.asarray(w["E"], float), dtype=DT)
        port = P.omp_parameters(Z, A - Z, k, e, p, o).stack().numpy()
        for i, col in enumerate(P.TALYS_COLUMNS):
            t = np.asarray(w[col], float)
            q = port[:, i]
            big = np.abs(t) > 1e-6
            r = np.where(big, np.abs(np.log(np.where(big, q, 1.0) / np.where(big, t, 1.0))), 0.0)
            r = np.where(~big & (np.abs(q - t) > 2e-6), np.inf, r)  # printed as zero, port is not
            rows.append((target, file, col, shape, r))
    assert rows, "no omppar blocks"
    for grp in ("spherical", "deformed", "actinide", None):
        sel = [r for *_, s, r in rows if grp is None or s == grp]
        assert sel, f"no {grp} omppar blocks"
        a = np.concatenate(sel)
        worst = max((x for x in rows if grp is None or x[3] == grp),
                    key=lambda x: float(np.max(x[-1])))  # fmt: skip
        print(f"A-omppar {grp or 'ALL':9s}: {len(sel) // 19:4d} blocks, median {np.median(a):.2e},"
              f" p95 {np.percentile(a, 95):.2e}, max {np.max(a):.2e}"
              f" ({worst[0]} {worst[1]} {worst[2]})")  # fmt: skip
        assert float(np.percentile(a, 95)) <= TOL_PAR


@cache
def _band(Z: int, A: int):
    """T13's coupled band, or None for a target ECIS does not deform."""
    from physics.hf.ecis.reference import coupled_band

    o, _ = _opts(Z, A)
    if P._colltype(Z, A, o) != "R":
        return None
    b = coupled_band(Z, A)
    return (b["rotbeta"], bool(b["deformation_length"]))


def _pot_columns(par, mass, Z: int, A: int, r: torch.Tensor):
    """omp.out's four columns on radii `r` ((S, R) or (R,)) for one energy."""
    band = _band(Z, A)
    if band is None:
        return radial_potential(par, mass, r)
    return rotational_radial_potential(par, mass, r, band[0], band[1])


@have_pot
@have_structure
def test_a_omppot_gate():
    df = ref._family("omp_potential")
    rows = []
    for (target, variant), _g in df.groupby(["target", "variant"], observed=True):
        Z, A, shape = _target_zas(target, variant)
        o, p = _opts(Z, A)
        mass = torch.tensor(_ame_mass(Z, A), dtype=DT)
        for _, (meta, w) in ref.blocks("omp_potential", target, "omp.out", variant).items():
            meta = json.loads(meta) if isinstance(meta, str) else meta
            einc = float(re.search(r"at\s+([0-9.E+-]+)\s+MeV", meta["title"]).group(1))
            w = w[w["radius"] > 0]
            rad = np.asarray(w["radius"], float)
            ir = np.rint(rad / rad[0])
            par = P.omp_parameters(Z, A - Z, 1, torch.tensor([einc], dtype=DT), p, o)
            steps = np.linspace(rad[0] - 5e-6, rad[0] + 5e-6, 101)
            r_all = torch.tensor(ir[None, :] * steps[:, None], dtype=DT)  # (S, R)
            pot = _pot_columns(par, mass, Z, A, r_all)  # every column at every step
            # ECIS's step is one number for all four columns, so fit it once on all four (the
            # tightest use of the single nuisance parameter the f8.5 print leaves free) and gate
            # every column with it.
            cols = {}
            worst_of = np.zeros(len(steps))
            for c in ("V", "W", "Vso", "Wso"):
                t = np.asarray(w[c], float)
                m = np.abs(t) > 1e-6 * np.abs(t).max()
                q = pot[c].reshape(len(steps), -1).numpy()[:, m]
                cols[c] = np.abs(np.log(q / t[m]))
                worst_of = np.maximum(worst_of, cols[c].max(axis=1))
            s = int(np.argmin(worst_of))
            for c, r in cols.items():
                rows.append((target, c, shape, r[s]))
    assert rows, "no omp.out blocks"
    for grp in ("spherical", "deformed", "actinide", None):
        sel = [r for _t, _c, s, r in rows if grp is None or s == grp]
        assert sel, f"no {grp} omp.out blocks"
        a = np.concatenate(sel)
        worst = max((x for x in rows if grp is None or x[2] == grp),
                    key=lambda x: float(np.max(x[-1])))  # fmt: skip
        print(f"A-omppot {grp or 'ALL':10s}: {len(sel) // 4:4d} blocks, median {np.median(a):.2e}, "
              f"p95 {np.percentile(a, 95):.2e}, max {np.max(a):.2e} "
              f"({worst[0]} {worst[1]})")  # fmt: skip
        assert float(np.percentile(a, 95)) <= TOL_POT


# ------------------------------------------------------------- CHARTFIX: Soukhovitskii's eferm


def test_soukhovitskii_fermi_is_the_three_separation_energies():
    """soukhovitskii.f90:103-107: the Fermi energy is `-(S(0,1,1) + S(0,0,1))/2` for a neutron
    and `-(S(1,0,2) + S(0,0,2))/2` for a proton, on ABSOLUTE nucleus indices -- so it is a
    property of the run, the same for every residual the run touches."""
    from physics.hf.input.defaults import default_options
    from physics.hf.omp.parameters import soukhovitskii_fermi
    from physics.hf.structure.masses import masses, separation_energy

    o = default_options(90, 227)  # Th-227: Zinit 90, Ninit 138, so (0, 0) is Th-228
    m = masses(o)
    got = soukhovitskii_fermi(o)
    want = {
        1: -0.5 * (separation_energy(m, 90, 227, 1) + separation_energy(m, 90, 228, 1)),
        2: -0.5 * (separation_energy(m, 89, 227, 2) + separation_energy(m, 90, 228, 2)),
    }
    assert got == pytest.approx(want, rel=0, abs=0)
    # every residual of the run reads the same two numbers
    assert soukhovitskii_fermi(default_options(90, 227)) == got


def test_th227_reaches_the_soukhovitskii_potential():
    """CHART1's one crash of 482: `riplomp(1) = 2408` covers A 228-249, so Th-227 falls to the
    global potential, `flagsoukho` sends it to Soukhovitskii, and nothing supplied the Fermi
    energy. It resolves itself now, and the depths are Soukhovitskii's, not KD03's."""
    from dataclasses import replace

    from physics.hf.input.defaults import default_options, default_params
    from physics.hf.omp import parameters as P

    o = default_options(90, 227)
    p = default_params(90, 227, o)
    e = torch.tensor([1.0, 14.0], dtype=DT)
    par = P.omp_parameters(90, 137, 1, e, p, o)  # the target itself, the call that crashed
    assert torch.isfinite(par.v_mev).all() and (par.v_mev > 0).all()
    kd = P.omp_parameters(90, 137, 1, e, p, replace(o, flagsoukho=False))
    assert float((par.v_mev - kd.v_mev).abs().max()) > 0.1
    assert float((par.rv_fm - kd.rv_fm).abs().max()) > 1.0e-3
