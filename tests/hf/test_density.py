"""T6 level densities against TALYS's own ld*.gs files (gate A-ld, docs/results/hf-engine-gates.md:
p95 of |ln(port/TALYS)| <= 1e-4 for the header parameters, <= 0.02 for the tables).

Inputs come from the ported upstream tasks, not from the dumps: T3 defaults, T2 masses and
discrete levels, T2 deformation (Irigid). Nothing TALYS computed for the level density is
injected; the compound nucleus and every residual that TALYS wrote an ld*.gs for are scored.
Reference-dump tests skip when the dumps are absent; the analytic tests always run.

Run `python -m tests.hf.test_density` for the gate table.
"""

from __future__ import annotations

import math
import pathlib
from functools import cache

import numpy as np
import pytest
import torch

from physics.hf import reference as ref
from physics.hf.core.tensors import DTYPE
from physics.hf.density.matching import (
    _fermi_tables,
    degenerate_window,
    densitycum,
    densitymatch,
    match,
)
from physics.hf.density.models import densityout, densitytot, dtheory, ld_header
from physics.hf.density.parameters import (
    SENTINEL,
    _fv,
    densitypar,
    ignatyuk,
    spincut,
    spindis,
)
from physics.hf.density.tables import attach_tables, density_table, edens_grid
from tests._data import talys_structure_dir_or_missing

TOL_PARAMS = 1e-4
TOL_TABLES = 0.02
TOL_DIAG = 0.01  # densitycum goodness-of-fit numbers; see DIAG_KEYS
FLOOR = 1e-10  # level densities [MeV^-1]
ZERO_ATOL = 1e-12  # |port| at or below this counts as agreeing with a TALYS zero

PARAM_KEYS = (
    "a(Sn) [MeV^-1]",
    "asymptotic a [MeV^-1]",
    "shell correction [MeV]",
    "damping gamma",
    "pairing energy [MeV]",
    "adjusted pairing shift [MeV]",
    "discrete spin cutoff parameter",
    "spin cutoff parameter(Sn)",
    "matching energy [MeV]",
    "temperature [MeV]",
    "separation energy [MeV]",
    "Rhotot(Sn) [MeV^-1]",
    "theoretical D0 [eV]",
    "theoretical D1 [eV]",
)
# The four goodness-of-fit numbers densitycum.f90 prints beside the parameters. They are not
# level-density parameters and they do not belong under A-ld's 1e-4: each is built from
# Ncum(i) - i, a difference of nearly equal numbers, so the ~1e-5 at which the port reproduces
# Ncum comes out amplified by one to two orders of magnitude. Scored at 1% instead, which still
# catches a wrong Nlow/Ntop window or a wrong matching energy.
DIAG_KEYS = (
    "Chi-2 per level",
    "Frms per level",
    "Erms per level",
    "average deviation per level",
)
EXACT_KEYS = ("Nlow", "Ntop", "number of excited levels", "ldmodel keyword")

have_dumps = pytest.mark.skipif(
    not ref.available("level_density"), reason="reference dumps not parsed"
)
have_structure = pytest.mark.skipif(
    not (talys_structure_dir_or_missing() / "density" / "ground" / "ctm").exists(),
    reason="TALYS structure database absent",
)


@cache
def _target_inputs(Zt: int, At: int, overrides: tuple = ()):
    """T3 Options/Params and T2 masses for a neutron run on (Zt, At). `overrides` is a tuple of
    (keyword, value) pairs passed to `default_options`, so pinning `ldmodel` carries its
    dependent defaults (flagparity, the ld parameter file) with it."""
    from physics.hf.input.defaults import default_options, default_params
    from physics.hf.structure.masses import masses

    o = default_options(Zt, At, "n", dict(overrides) if overrides else None)
    p = default_params(Zt, At, o)
    return o, p, masses(o, p)


@cache
def _target_ZA(target: str) -> tuple[int, int]:
    man = ref.manifest()
    row = man[man["target"] == target].iloc[0]
    return int(row["Z"]), int(row["A"])


def build_ld(Zt: int, At: int, Z: int, A: int, overrides: tuple = ()):
    """The ported level-density state of nucleus (Z, A) in a neutron run on (Zt, At), through the
    structure.f90 order densitypar -> densitytable -> densitymatch -> densitycum."""
    from physics.hf.structure.levels import discrete_levels

    o, p, m = _target_inputs(Zt, At, overrides)
    lev = discrete_levels(Z, A, o, m, p)
    ld = densitypar(Z, A, o, p, m, lev)
    ld = attach_tables(ld)
    ld = densitymatch(ld, o.flagldglobal, o.flagctmglob)
    return ld, densitycum(ld), o, p, m


def _r(port, talys, floor=0.0):
    """|ln(port/TALYS)| over the points where TALYS is above `floor`. A point TALYS puts at or
    below the floor is dropped when the port agrees (both effectively zero) and scored `inf`
    when it does not -- silently passing "TALYS says 0, we say 7" is how a gate lies."""
    port = np.asarray(port, dtype=float).ravel()
    talys = np.asarray(talys, dtype=float).ravel()
    out = np.zeros_like(talys)
    above = np.abs(talys) > floor
    agree = np.abs(port) <= max(floor, ZERO_ATOL)
    with np.errstate(divide="ignore", invalid="ignore"):
        ratio = port[above] / talys[above]
        # E0 and the shell correction are signed, so a sign disagreement gives log of a negative
        # number. Score it inf, not nan: nan would poison np.percentile and turn a real failure
        # into a gate that silently reports nothing.
        out[above] = np.where(ratio > 0.0, np.abs(np.log(np.abs(ratio))), np.inf)
    bad = (~above) & (~agree)
    out[bad] = np.inf
    assert not np.isnan(out).any(), "the A-ld metric must never produce nan"
    return out[above | bad]


def ld_files():
    if not ref.available("level_density"):
        return []
    d = ref._family("level_density")
    pairs = d[["variant", "target", "file"]].drop_duplicates()
    return [tuple(x) for x in pairs.itertuples(index=False) if not x[2].endswith(("b01.gs", "b02.gs", "b03.gs"))]


def score_file(variant: str, target: str, file: str) -> dict[str, np.ndarray]:
    """|ln(port/TALYS)| per quantity for one ld*.gs file of the reference dumps (ibar 0)."""
    Zt, At = _target_ZA(target)
    return score_blocks(ref.level_density(file, target, variant), Zt, At,
                        int(file[2:5]), int(file[5:8]))


def score_blocks(bl: dict, Zt: int, At: int, Z: int, A: int, overrides: tuple = ()) -> dict:
    """|ln(port/TALYS)| per quantity for one parsed ld*.gs file: `bl` is {block: (meta, table)}
    as `physics.hf.reference.level_density` returns it, for nucleus (Z, A) in a neutron run on
    target (Zt, At). `overrides` pins keywords (``(("ldmodel", 2),)``) so the same scorer serves
    the reference dumps and the pinned-ldmodel runs of ~/t6_ldmodel/run.py."""
    from physics.hf.structure.levels import discrete_levels

    meta0, levtab = bl[0]
    tp = ref._float_meta(meta0)
    ld, cum, o, p, m = build_ld(Zt, At, Z, A, overrides)
    out = densityout(ld, cum["Ncum"], 0, cum["rhoexp"])
    h = out["parameters"]
    h["Chi-2 per level"] = _fv(cum["chi2lev"])
    h["Frms per level"] = _fv(cum["Frmslev"])
    h["Erms per level"] = _fv(cum["Ermslev"])
    h["average deviation per level"] = _fv(cum["avdevlev"])
    # dtheory: s-wave spacing for a neutron on (Z, A-1) (densitymatch.f90:292, E = 0)
    tl = discrete_levels(Z, A - 1, o, m, p)
    D = dtheory(ld, float(tl.spin[0]), int(tl.parity[0]))
    h["theoretical D0 [eV]"] = float(D[0])
    h["theoretical D1 [eV]"] = float(D[1])
    res: dict[str, np.ndarray] = {}
    exact = []
    for k in EXACT_KEYS:
        if k in tp and k in h:
            exact.append(float(tp[k]) == float(h[k]))
    res["exact"] = np.array(exact, dtype=float)
    for k in PARAM_KEYS:
        if k in tp and k in h:
            res[f"param:{k}"] = _r([h[k]], [tp[k]])
    # E0 is signed and passes through zero (Gd-154: E0 = 0.0435 MeV), so |ln(port/TALYS)| is
    # unbounded there however well the two agree -- and E0 only ever enters the physics through
    # gilcam's exp((Eex - E0)/T), so the error that means anything is |dE0| measured in units of
    # the temperature. Scored at the same 1e-4 as the other parameters, just on the right scale.
    if "E0 [MeV]" in tp and "E0 [MeV]" in h:
        res["param:E0/T"] = np.array([abs(h["E0 [MeV]"] - tp["E0 [MeV]"]) / h["temperature [MeV]"]])
    for k in DIAG_KEYS:
        if k in tp and k in h:
            res[f"diag:{k}"] = _r([h[k]], [tp[k]])
    if levtab is not None and "Total_LD" in levtab.columns and "levels" in out:
        L = out["levels"]
        t = levtab.set_index("Level")
        lvl = np.array(L["Level"])
        common = [i for i in lvl if i in t.index]
        sel = np.isin(lvl, common)
        for col in ("Total_LD", "Exp_LD", "N_cumulative", "a", "Sigma"):
            if col in t.columns and len(L.get(col, [])):
                res[f"levels:{col}"] = _r(
                    np.array(L[col])[sel], t.loc[common, col].to_numpy(), FLOOR if col == "Total_LD" else 0.0
                )
    for b, (mt, w) in bl.items():
        if mt.get("type") != "level density" or str(mt.get("fission barrier", "0")) != "0":
            continue
        par = int(mt["Parity"])
        pb = out["parity_blocks"][par]
        n = min(len(w), len(pb["E"]))
        res.setdefault("table:E", [])
        res["table:E"] = np.concatenate([np.atleast_1d(res["table:E"]), _r(pb["E"][:n].numpy(), w["E"].to_numpy()[:n])])
        for col, key in (("rho_observed", "rho_observed"), ("rho_total", "rho_total"), ("T", "T"), ("N_cumulative", "N_cumulative")):
            prev = res.get(f"table:{col}", np.array([]))
            fl = FLOOR if col.startswith("rho") else 0.0
            res[f"table:{col}"] = np.concatenate([prev, _r(pb[key][:n].detach().numpy(), w[col].to_numpy()[:n], fl)])
        jcols = [c for c in w.columns if c.startswith("rho(J)=")]
        port = pb["rho_J"][:n, : len(jcols)].detach().numpy()
        prev = res.get("table:rho(J)", np.array([]))
        res["table:rho(J)"] = np.concatenate([prev, _r(port, w[jcols].to_numpy()[:n], FLOOR)])
    return res


def gate_table(files=None) -> dict:
    files = ld_files() if files is None else files
    pooled: dict[str, list] = {}
    per_file = {}
    for f in files:
        s = score_file(*f)
        per_file[f] = s
        for k, v in s.items():
            pooled.setdefault(k, []).append(np.asarray(v, dtype=float))
    summary = {}
    for k, vs in pooled.items():
        v = np.concatenate([np.atleast_1d(x) for x in vs]) if vs else np.array([])
        if k == "exact":
            summary[k] = {"n": int(v.size), "fraction_equal": float(v.mean()) if v.size else 1.0}
            continue
        finite = v[np.isfinite(v)]
        # v empty = TALYS printed only zeros for this quantity and the port matched them; there
        # is nothing to score, and the gate must read that as 0, not nan (nan <= tol is False).
        summary[k] = {
            "n": int(v.size),
            "median": float(np.median(finite)) if finite.size else 0.0,
            "p95": float(np.percentile(v, 95)) if v.size else 0.0,
            "max": float(v.max()) if v.size else 0.0,
        }
    return {"summary": summary, "per_file": per_file}


# ------------------------------------------------------------------------------ analytic tests


def test_spindis_normalises_over_spins():
    """sum_J spindis is the midpoint rule for int_0^inf (u/s2) exp(-u^2/2s2) du with u = J+1/2:
    nodes at u = 1/2, 3/2, ... (integer J) cover [0, inf) and give 1; nodes at u = 1, 2, ...
    (half-integer J) cover [1/2, inf) and give exp(-1/(8 s2)). Both to the quadrature error,
    which shrinks as the distribution widens."""
    prev_int = prev_half = 1.0
    for sc in (4.0, 9.0, 25.0):
        s = torch.tensor(sc, dtype=DTYPE)
        Jint = torch.arange(0, 80, dtype=DTYPE)
        d_int = abs(float(spindis(s, Jint).sum()) - 1.0)
        d_half = abs(float(spindis(s, Jint + 0.5).sum()) - math.exp(-0.125 / sc))
        assert d_int < 1.5e-2 and d_half < 1.5e-2, (sc, d_int, d_half)
        assert d_int < prev_int and d_half < prev_half
        prev_int, prev_half = d_int, d_half


def test_edens_grid_matches_strucinitial():
    e = edens_grid()
    assert float(e[20]) == 5.0 and float(e[30]) == 10.0 and float(e[40]) == 20.0
    assert float(e[43]) == 30.0 and float(e[60]) == 200.0


@have_structure
def test_zr91_header_without_dumps():
    """Values printed in ld040091.gs of a TALYS-2.24 Zr-90 + n run (hand-copied, 7 digits)."""
    try:
        ld, cum, *_ = build_ld(40, 90, 40, 91)
    except Exception as exc:  # pragma: no cover - database layout
        pytest.skip(f"structure inputs unavailable: {exc}")
    h = ld_header(ld)
    expect = {
        "a(Sn) [MeV^-1]": 10.4817,
        "asymptotic a [MeV^-1]": 11.5233,
        "shell correction [MeV]": -1.232496,
        "damping gamma": 0.09628627,
        "pairing energy [MeV]": 1.257942,
        "discrete spin cutoff parameter": 9.368644,
        "spin cutoff parameter(Sn)": 17.51648,
        "matching energy [MeV]": 6.424624,
        "temperature [MeV]": 0.8600038,
        "E0 [MeV]": -0.1761203,
        "Rhotot(Sn) [MeV^-1]": 6000.32,
    }
    for k, v in expect.items():
        assert abs(math.log(h[k] / v)) < TOL_PARAMS, (k, h[k], v)
    assert (h["Nlow"], h["Ntop"]) == (7, 39)




@have_structure
def test_y89_reproduces_talys_locate_temprho_offset():
    """densitymatch.f90 hands the 1-based `temprho` to locate.f90, whose dummy is `xx(0:ie)`, so
    the bracket that comes back is one interval low and the pol1 after it extrapolates. Y-89 in
    a Zr-90 run is where that becomes visible: TALYS-2.24 prints Exmatch 3.204383, T 0.6350462,
    E0 1.41367 in ld039089.gs (reproduced here with `t 39 89 <T>` probes of the same table).
    "Repairing" the off-by-one gives Exmatch 2.9624 and puts rho(J) 35% out -- the port keeps
    TALYS's arithmetic (contract §1)."""
    try:
        ld, _cum, *_ = build_ld(40, 90, 39, 89)
    except Exception as exc:  # pragma: no cover - database layout
        pytest.skip(f"structure inputs unavailable: {exc}")
    h = ld_header(ld)
    for k, v, tol in (("matching energy [MeV]", 3.204383, 1e-4),
                      ("temperature [MeV]", 0.6350462, 1e-5),
                      ("E0 [MeV]", 1.41367, 1e-5)):
        assert abs(math.log(h[k] / v)) < tol, (k, h[k], v)


@have_structure
def test_nb91_degenerate_matching_window():
    """Nb-91 in an Nb-93 run has Nlow == Ntop == 3, so the CTM has no level window: EL == EP and
    match.f90's condition is identically zero, which makes every energy in zbrak's bracket a
    root. TALYS still returns one particular energy (1.871067), because its factor2 subtracts a
    single-precision `exp` from a double-precision one and it brackets the float32 residue.

    The port returns a definite root of its own -- the first point of zbrak's scan -- rather
    than falling back to the empirical temperature, which put Exmatch at 8.4992 and cost 23 of
    CHART1's Nb-91 cells. Pinned here: the condition is still exactly zero, the two answers are
    inside one zbrak segment of each other, and the fallback is not taken."""
    try:
        ld, _cum, *_ = build_ld(41, 93, 41, 91)
    except Exception as exc:  # pragma: no cover - structure database layout
        pytest.skip(f"structure inputs unavailable: {exc}")
    assert ld.Nlow[0] == ld.Ntop[0] == 3
    assert float(ld.edis_mev[ld.Nlow[0]]) == float(ld.edis_mev[ld.Ntop[0]])
    assert degenerate_window(ld, 0)
    logrho, temprho, _nstart, _nex = _fermi_tables(ld, 0)
    cond = match(ld, torch.linspace(2.0, 19.0, 40, dtype=DTYPE), logrho, temprho, SENTINEL, 0)
    assert float(cond.abs().max()) == 0.0, "EL == EP must give an identically zero condition"
    exm = ld_header(ld)["matching energy [MeV]"]
    assert abs(exm - 1.78675) < 1e-4, exm                   # x1 + dx, not the 8.4992 fallback
    assert abs(exm - 1.871067) < (19.0 + 300.0 / 91 - 1.5796) / 100 + 1e-3  # within one segment


@have_structure
def test_degenerate_window_needs_a_non_zero_level_energy():
    """Ntop == Nlow == 0 is not the degenerate case: match.f90:57 guards `if (EL /= 0.)`, so
    factor2 is 1 and the condition is a real function with a real root. Eu-148 is that case and
    must still go through zbrak -- TALYS gives it Exmatch = 3.88811."""
    try:
        ld, _cum, *_ = build_ld(63, 147, 63, 148)
    except Exception as exc:  # pragma: no cover - structure database layout
        pytest.skip(f"structure inputs unavailable: {exc}")
    assert int(ld.Nlow[0]) == int(ld.Ntop[0]) == 0
    assert not degenerate_window(ld, 0)
    assert abs(ld_header(ld)["matching energy [MeV]"] - 3.88811) < 1e-3


@have_structure
def test_degenerate_window_lands_ir188_on_the_talys_level_density():
    """Ir-188 is the case CHART1 named. Its degenerate root has to come out below the top of its
    discrete level scheme (1.7538 MeV): everything the cells care about is the residual's level
    density where its continuum opens, and below that energy the CTM is never evaluated. TALYS's
    own noise root (0.4469783) is in the same interval, which is why the two agree on the cross
    sections to 1.5e-4 without agreeing on Exmatch."""
    try:
        ld, _cum, *_ = build_ld(77, 188, 77, 188)
    except Exception as exc:  # pragma: no cover - structure database layout
        pytest.skip(f"structure inputs unavailable: {exc}")
    assert degenerate_window(ld, 0)
    exm = ld_header(ld)["matching energy [MeV]"]
    assert 0.0 < exm <= float(ld.edis_mev[int(ld.Nlast[0])])
    assert 0.0 < 0.4469783 <= float(ld.edis_mev[int(ld.Nlast[0])])


@have_structure
def test_gradients_flow_to_aadjust_and_pshift():
    from physics.hf.input.defaults import default_options, default_params
    from physics.hf.structure.levels import discrete_levels
    from physics.hf.structure.masses import masses

    o = default_options(26, 56, "n")
    p = default_params(26, 56, o)
    p.requires_grad_(["aadjust", "pshiftadjust"])
    m = masses(o, p)
    lev = discrete_levels(26, 57, o, m, p)
    ld = densitypar(26, 57, o, p, m, lev)
    rho = densitytot(ld, torch.tensor([12.0], dtype=DTYPE))
    rho.sum().backward()
    ga = p["aadjust"].grad
    assert ga is not None and float(ga.abs().sum()) > 0.0
    assert torch.isfinite(ga).all()


@have_structure
def test_bskg3_table_reads_both_parities_for_u238():
    tab = density_table(92, 238, 7, 0)
    if tab is None:
        pytest.skip("bskg3 U table absent")
    assert tab.nendens == 60
    assert float(tab.ldtottableP_per_mev[10, 0]) > 0.0 and float(tab.ldtottableP_per_mev[10, 1]) > 0.0
    assert float(tab.ldtottable_per_mev[10]) == pytest.approx(
        float(tab.ldtottableP_per_mev[10, 0] + tab.ldtottableP_per_mev[10, 1]), rel=1e-12
    )


# ------------------------------------------------------------------------------ gate A-ld


@cache
def _gate() -> dict:
    """The A-ld gate, computed once per session: it rebuilds the level-density state of every
    residual in the dumps, which takes minutes."""
    return gate_table()


def _gate_summary() -> dict:
    return _gate()["summary"]


@have_dumps
@have_structure
def test_a_ld_parameters():
    g = _gate_summary()
    assert g["exact"]["fraction_equal"] == 1.0
    for k, s in g.items():
        if k.startswith("param:"):
            assert s["p95"] <= TOL_PARAMS, (k, s)
        if k.startswith("diag:"):
            assert s["p95"] <= TOL_DIAG, (k, s)


@have_dumps
@have_structure
def test_a_ld_only_known_divergence_is_nb91():
    """Every quantity the port cannot put a finite |ln| on must come from the one nucleus whose
    disagreement is understood and written down: Nb-91 of the Nb-93 run, where TALYS roots its
    own float32 rounding (see test_nb91_degenerate_matching_window). A new name appearing here
    is a new divergence, not a known one."""
    res = _gate()
    offenders = {
        f[2]
        for f, sc in res["per_file"].items()
        for v in sc.values()
        if np.size(v) and not np.all(np.isfinite(np.atleast_1d(np.asarray(v, dtype=float))))
    }
    assert offenders <= {"ld041091.gs"}, sorted(offenders)


@have_dumps
@have_structure
def test_a_ld_tables():
    g = _gate_summary()
    for k, s in g.items():
        if k.startswith(("table:rho", "levels:Total_LD")):
            assert s["p95"] <= TOL_TABLES, (k, s)


if __name__ == "__main__":  # pragma: no cover
    import json
    import sys

    res = gate_table()
    print(json.dumps(res["summary"], indent=1))
    # Rank nan-safe: np.max of an array holding nan is nan, and nan sorts below everything, so a
    # plain sort hides exactly the files worth looking at. nan (a sign flip in a signed quantity
    # such as E0) and inf (TALYS at zero, the port not) both go to the top.
    worst = []
    for f, sc in res["per_file"].items():
        for k, v in sc.items():
            v = np.atleast_1d(np.asarray(v, dtype=float))
            if k == "exact" or not v.size:
                continue
            m = float(np.max(v))
            worst.append((0 if np.isnan(m) else 1, m, k, f))
    worst.sort(key=lambda w: (w[0], w[1]))
    for rank, m, k, f in worst[:25]:
        print(f"{'nan' if rank == 0 else f'{m:.6g}':>12s}  {k:32s} {f}")
    if len(sys.argv) > 1:
        pathlib.Path(sys.argv[1]).write_text(
            json.dumps([{"max": None if np.isnan(m) else m, "quantity": k, "file": list(f)}
                        for _r, m, k, f in worst], indent=1)
        )


# ================================================================================================
# DIFFPARAM (gate G0.4): the level-density family on the autograd graph
# ================================================================================================


def test_rhogrid_torch_path_matches_numpy(monkeypatch):
    """`rhogrid_of(differentiable=True)` is the numpy path's numbers, not an approximation.

    The torch path replaces a row scatter and a per-row `out[k, maxJ+1:] = 0` loop with an
    `index_copy` and a mask; both must be the same array to the bit, because the fast path is
    what every non-gradient call (the whole chart sweep) keeps using.
    """
    from physics.hf.compound.dens_reference import rhogrid_of

    # the numpy path to the bit; NX2's C rhogrid is held to closeness in tests/hf/test_nx2_ld.py
    monkeypatch.setenv("HF_NX2_LD", "0")
    ex = np.linspace(0.0, 12.0, 40)
    dex = np.full(40, 12.0 / 39.0)
    maxj = np.full(40, 20, dtype=np.int64)
    maxj[30:] = 8
    a = rhogrid_of(26, 57, 26, 56, ex, dex, maxj, 5)
    b = rhogrid_of(26, 57, 26, 56, ex, dex, maxj, 5, None, True)
    assert isinstance(b, torch.Tensor)
    d = np.abs(b.detach().numpy() - a).max()
    assert d == 0.0, d


def test_a_float_override_at_the_talys_default_reproduces_the_unoverridden_level_density():
    """A `density_overrides` of the TALYS defaults must be the un-overridden `LDNucleus`.

    This is the test that the override plumbing does not quietly take a different branch: the
    same numbers have to come out of the cached arm and out of the rebuilt one.
    """
    from physics.hf.compound.dens_reference import _ld_of

    ld0, ntop0, nl0, ncum0 = _ld_of(26, 57, 26, 56)
    ld1, ntop1, nl1, ncum1 = _ld_of(26, 57, 26, 56, {"aadjust": 1.0, "pshift": 0.0})
    assert (ntop1, nl1) == (ntop0, nl0) and float(ncum1) == float(ncum0)
    for f in ("alev", "alimit", "pair_mev", "T_mev", "E0_mev", "Exmatch_mev", "delta_mev"):
        x, y = getattr(ld0, f), getattr(ld1, f)
        assert torch.equal(torch.as_tensor(x), torch.as_tensor(y)), f


def test_the_matching_energy_carries_the_implicit_derivative_of_its_own_root():
    """`Exmatch` solves `match(E, theta) = 0`; its gradient is -(dg/dtheta)/(dg/dE).

    Checked against a finite difference of the *bisection itself*, with the root refined to
    1e-12 so that TALYS's own 1e-4 staircase is not what is being measured. Without this term
    every level-density gradient through capture was wrong by 30-140%.
    """
    from physics.hf.compound.dens_reference import _ld_of

    def exm(a: float, xacc: float = 1.0e-12) -> float:
        ld, *_ = _ld_of(26, 57, 26, 56, {"aadjust": a}, xacc)
        return float(ld.Exmatch_mev[0])

    th = torch.tensor(1.0, dtype=torch.float64, requires_grad=True)
    ld, *_ = _ld_of(26, 57, 26, 56, {"aadjust": th}, 1.0e-12)
    E = ld.Exmatch_mev[0]
    assert E.requires_grad, "Exmatch is a leaf: the implicit derivative is not attached"
    E.backward()
    h = 1.0e-4
    fd = (exm(1.0 + h) - exm(1.0 - h)) / (2.0 * h)
    assert abs(fd) > 1.0  # Fe-57: about -16.5 MeV per unit aadjust
    assert abs(float(th.grad) - fd) <= 1e-4 * abs(fd), (float(th.grad), fd)
