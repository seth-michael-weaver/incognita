"""T7 gamma: photon strength functions, gamma transmission and the theoretical <Gamma_gamma>
against TALYS's own psf* files (gate A-psf, docs/results/hf-engine-gates.md: p95 of
|ln(port/TALYS)| <= 1%).

Inputs other components own are injected from the same TALYS run (contract §5):
  S_n, pairing energy, a(Sn), D0theo, rho(Ex, J, parity)  <- ld<ZZZ><AAA>.gs of the compound nucleus
  discrete levels                                         <- levels<ZZZ><AAA>.out (raw rows)
  |beta2|                                                 <- backed out of the psf M1 header
                                                             ("pygmy tpr" = 0.01 |beta2| A^0.9),
                                                             until T2 reads the mass table
Skips when the reference dumps are absent.
"""

from __future__ import annotations

import json
from functools import cache

import numpy as np
import pytest
import torch
from scipy.interpolate import CubicSpline

from physics.hf import reference as ref
from physics.hf.gamma.parameters import gamma_parameters, structure_dir
from physics.hf.gamma.score import has_temperature_inputs
from physics.hf.gamma.strength import _locate, fstrength_gp
from physics.hf.gamma.transmission import quasideuteron, radwidtheory, tgamma
from physics.hf.input.defaults import default_options

TOL_P95 = 0.01  # A-psf
FLOOR = 1e-30

have_dumps = pytest.mark.skipif(
    not (ref.available("psf") and ref.available("level_density") and ref.available("raw_rows")),
    reason="reference dumps not parsed",
)
have_structure = pytest.mark.skipif(
    not (structure_dir() / "gamma" / "smlo2019").exists(), reason="TALYS structure database absent"
)


@cache
def _frames():
    import pandas as pd

    d = ref.reference_dir()
    return (
        pd.read_parquet(d / "psf.parquet"),
        pd.read_parquet(d / "level_density.parquet"),
        pd.read_parquet(d / "raw_rows.parquet"),
    )


def _cases():
    if not ref.available("psf"):
        return []
    psf = _frames()[0]
    out = []
    for (target, variant, file), _ in psf.groupby(["target", "variant", "file"], observed=True):
        if file.endswith(".E1"):
            tag = file[3:9]
            out.append((target, variant, int(tag[:3]), int(tag[3:])))
    return sorted(set(out))


def _wide(df):
    return df.pivot_table(index="row", columns="column", values="value", observed=True)


def _meta(df):
    return json.loads(df["meta"].iloc[0])


@cache
def _setup(target: str, variant: str, Z: int, A: int):
    psf, ld, _raw = _frames()
    tag = f"{Z:03d}{A:03d}"
    sub = psf[(psf.target == target) & (psf.variant == variant)]
    g = ld[(ld.target == target) & (ld.variant == variant) & (ld.file == f"ld{tag}.gs")]
    m = _meta(g)
    hdr = {rad: _meta(sub[sub.file == f"psf{tag}.{rad}"]) for rad in ("E1", "M1", "E2", "M2")}
    tpr = float(hdr["M1"].get("pygmy tpr [mb]", 0.0))
    beta2 = tpr / (1.0e-2 * A**0.9)
    gp = gamma_parameters(
        Z,
        A,
        default_options(Z, A - 1),  # psf<Z><A> is the compound nucleus of the (Z, A-1) target
        S_k0_mev=float(m["separation energy [MeV]"]),
        delta_mev=float(m.get("pairing energy [MeV]", 0.0)),
        alev_per_mev=float(m.get("a(Sn) [MeV^-1]", 0.0)),
        beta2=beta2,
        flagcol=m.get("collective enhancement", "n") == "y",
    )
    tables = {rad: _wide(sub[sub.file == f"psf{tag}.{rad}"]) for rad in ("E1", "M1", "E2", "M2")}
    return gp, tables, hdr, m, g


def _skip_without_temperature(m: dict, quantity: str):
    """fstrength's tabulated-E1 branch needs a(Sn) and the pairing energy (the nuclear
    temperature), and both are INJECTED from ld*.gs (contract §5). densityout.f90 prints them
    only for the analytical level density models, so an ldmodel 7 nucleus -- every actinide,
    input_densitymodel.f90:90 -- has no reference value and the quantity cannot be gated.
    Measured with a one-off `ldmodel 1` TALYS run on U-238, where TALYS does print them:
    f(E1) p95 1.2e-6, T(E1) 2.0e-6 over all 88 points, so the gap is the missing input, not the
    port. physics/hf/gamma/score.py reports these cases as ungated."""
    if not has_temperature_inputs(m):
        pytest.skip(
            f"{quantity}: ld*.gs prints no a(Sn)/pairing for ldmodel {m.get('ldmodel keyword')}"
        )


def _r(port: np.ndarray, talys: np.ndarray) -> np.ndarray:
    msk = talys > FLOOR
    return np.abs(np.log(port[msk] / talys[msk]))


CASES = _cases()
IDS = [f"{t}-{v}" for t, v, _, _ in CASES]


@have_dumps
@have_structure
@pytest.mark.parametrize("case", CASES, ids=IDS)
def test_strength_functions_E1_M1_match_talys(case):
    gp, tables, hdr, m, _ = _setup(*case)
    assert hdr["E1"]["strength keyword"].strip() == str(gp.strength)
    assert hdr["M1"]["strength keyword"].strip() == str(gp.strengthM1)
    assert float(hdr["E1"]["wtable"]) == pytest.approx(float(gp.wtable[1, 1]), abs=1e-6)
    for rad, irad in (("M1", 0), ("E1", 1)):  # M1 first: E1 may skip on a tabulated-ld nucleus
        if rad == "E1":
            _skip_without_temperature(m, "f(E1)")
        w = tables[rad]
        e = torch.tensor(w["E"].to_numpy(), dtype=torch.float64)
        port = fstrength_gp(gp, 0.0, e, irad, 1).numpy()  # gammaout.f90 passes Efs = 0
        r = _r(port, w[f"f({rad})"].to_numpy())
        assert np.percentile(r, 95) <= TOL_P95, (
            f"{case} f({rad}): p95 {np.percentile(r, 95):.3g}, max {r.max():.3g}"
        )


@have_dumps
@have_structure
@pytest.mark.parametrize("case", CASES, ids=IDS)
def test_gamma_transmission_all_multipolarities_match_talys(case):
    """T(XL) columns = Tjl(0, nen, irad, l) from tgamma at the FIRST incident energy (gamma.f90:30
    writes psf* only for nin == 1), so they test E2 and M2 too."""
    gp, tables, _, m, _ = _setup(*case)
    target_Z, target_A = case[2], case[3] - 1
    w = tables["E1"]
    n = int((w["T(E1)"] > 0).sum())  # beyond egrid TALYS pads the table with T = 0
    e = torch.tensor(w["E"].to_numpy()[:n], dtype=torch.float64)
    from physics.hf.talys_reference import ENERGIES_MEV

    tr = tgamma(gp, e, ENERGIES_MEV[0], target_Z, target_A)
    for rad, irad, l in (("M1", 0, 1), ("E2", 1, 2), ("M2", 0, 2), ("E1", 1, 1)):  # noqa: E741
        if rad == "E1":
            _skip_without_temperature(m, "T(E1)")
        talys = tables[rad][f"T({rad})"].to_numpy()[:n]
        r = _r(tr.tjl[:, irad, l].numpy(), talys)
        assert r.size > 0 and np.percentile(r, 95) <= TOL_P95, (
            f"{case} T({rad}): p95 {np.percentile(r, 95):.3g}"
        )


def _levels(raw, target, variant, Z, A):
    s = raw[
        (raw.target == target)
        & (raw.variant == variant)
        & (raw.file == f"levels{Z:03d}{A:03d}.out")
    ]
    out = []
    for line in s.sort_values(["block", "row"])["line"]:
        if "--->" in line:
            continue
        f = line.split()
        if len(f) < 4 or f[3] not in "+-":
            continue
        out.append((float(f[1]), float(f[2]), 1 if f[3] == "+" else -1))
    return out


def _density_from_dump(g):
    """rho(Ex, J, parity) [MeV^-1] from the ld*.gs per-parity tables, cubic in ln(rho).

    The interpolation is part of the injection, not the port; see
    physics.hf.gamma.score._density_from_dump for why cubic.
    """
    tabs = {}
    for _, gb in g.groupby("block", observed=True):
        m = _meta(gb)
        if "Parity" not in m or int(m["Parity"]) in tabs:
            continue
        w = _wide(gb)
        if "E" not in w:
            continue
        jc = [c for c in w.columns if str(c).startswith("rho(J)=")]
        tabs[int(m["Parity"])] = (
            w["E"].to_numpy(),
            np.array([float(str(c).split("=")[1]) for c in jc]),
            np.log(np.maximum(w[jc].to_numpy(), 1e-300)),
        )

    def density(ex, J, parity):
        E, js, lr = tabs[parity]
        idx = [int(np.argmin(np.abs(js - j))) for j in J.numpy()]
        x = ex.numpy()
        cols = [np.exp(CubicSpline(E, lr[:, k])(x)) for k in idx]
        return torch.tensor(np.stack(cols, -1), dtype=torch.float64)

    return density


@have_dumps
@have_structure
@pytest.mark.parametrize("case", CASES, ids=IDS)
def test_theoretical_gamma_gamma_matches_talys(case):
    target, variant, Z, A = case
    gp, _, hdr, m, g = _setup(*case)
    _skip_without_temperature(m, "theoretical Gamma_gamma")
    raw = _frames()[2]
    lv = _levels(raw, target, variant, Z, A)
    tg = _levels(raw, target, variant, Z, A - 1)
    assert lv and tg, "levels files missing from raw_rows"
    rw = radwidtheory(
        gp,
        float(hdr["E1"]["average resonance energy [eV]"]) * 1.0e-6,
        float(m["separation energy [MeV]"]),
        torch.tensor([x[0] for x in lv]),
        torch.tensor([x[1] for x in lv]),
        torch.tensor([x[2] for x in lv]),
        tg[0][1],
        tg[0][2],
        _density_from_dump(g),
        float(m["theoretical D0 [eV]"]),
    )
    th = float(hdr["E1"]["theoretical Gamma_gamma [eV]"])
    sw = float(hdr["E1"]["theoretical S-wave strength function [e-4]"]) * 1.0e-4
    assert abs(np.log(float(rw.gamgamth0_ev) / th)) <= TOL_P95, (float(rw.gamgamth0_ev), th)
    assert abs(np.log(float(rw.swaveth) / sw)) <= TOL_P95


@have_dumps
@pytest.mark.parametrize("case", CASES, ids=IDS)
def test_talys_psf_E2_M2_files_carry_the_l1_strength(case):
    """TALYS output trap (gammaout.f90: `fstrength(Zcomp, Ncomp, 0., e, irad, 1, 0, 0)` with l
    hard-wired to 1): the f() column of psf*.E2 / *.M2 is f(E1) / f(M1). Only their T() columns
    carry the l = 2 physics. If a TALYS update fixes this, the E2/M2 f gates become testable."""
    _, tables, _, _, _ = _setup(*case)
    assert np.array_equal(tables["E2"]["f(E2)"].to_numpy(), tables["E1"]["f(E1)"].to_numpy())
    assert np.array_equal(tables["M2"]["f(M2)"].to_numpy(), tables["M1"]["f(M1)"].to_numpy())


@have_dumps
@have_structure
@pytest.mark.parametrize("case", CASES, ids=IDS)
def test_no_strength_reads_silently_empty_where_talys_has_it(case):
    """Commit 2dd8065's failure mode (tables parsed to all zeros): wherever TALYS has a non-zero
    E1/M1 strength, the port must too, point by point, and the SMLO table must have been read."""
    gp, tables, hdr, _, _ = _setup(*case)
    if "Tables" in hdr["E1"]["PSF model"]:
        assert gp.qrpaexist(1, 1) and float(gp.tables[(1, 1)].f_raw_mev3.max()) > 0.0
    for rad, irad in (("E1", 1), ("M1", 0)):
        w = tables[rad]
        talys = w[f"f({rad})"].to_numpy()
        port = fstrength_gp(
            gp, 0.0, torch.tensor(w["E"].to_numpy(), dtype=torch.float64), irad, 1
        ).numpy()
        assert not np.any((talys > 0.0) & ~(port > 0.0)), f"{case} {rad}: zero where TALYS is not"


@have_structure
@pytest.mark.parametrize(
    "strength,strengthM1,Z,A,irad",
    [
        (9, 3, 40, 91, 1),
        (8, 8, 40, 91, 0),
        (10, 10, 40, 91, 0),
        (3, 3, 26, 57, 1),
        (4, 3, 26, 57, 1),
        (12, 12, 20, 41, 0),
    ],
)
def test_tabulated_models_read_non_empty(strength, strengthM1, Z, A, irad):
    o = default_options(Z, A - 1, overrides={"strength": strength, "strengthM1": strengthM1})
    gp = gamma_parameters(Z, A, o, S_k0_mev=7.0, delta_mev=1.0, alev_per_mev=10.0, beta2=0.1)
    if not gp.qrpaexist(irad, 1):
        pytest.skip(f"no table for Z={Z} A={A} in this model (TALYS falls back, so does the port)")
    tab = gp.tables[(irad, 1)]
    assert float(tab.f_raw_mev3[1:, 0].min()) >= 0.0
    assert int((tab.f_raw_mev3[1:, 0] > 0).sum()) > 250, "table parsed mostly empty"
    assert float(tab.e_raw_mev[1]) > 0.0 and float(tab.e_raw_mev[-1]) > float(tab.e_raw_mev[1])


@have_structure
def test_gradients_flow_to_the_adjustable_parameters():
    ft = torch.ones((2, 3), dtype=torch.float64, requires_grad=True)
    wt = torch.ones((2, 3), dtype=torch.float64)
    wt[1, 1] = 1.081
    wt.requires_grad_(True)
    sgr = torch.zeros((2, 3, 3), dtype=torch.float64)
    sgr[0, 1, 1] = 0.03 * 91 ** (5 / 6)
    sgr.requires_grad_(True)
    gp = gamma_parameters(
        40,
        91,
        default_options(40, 90),
        S_k0_mev=7.19,
        delta_mev=1.26,
        alev_per_mev=10.5,
        beta2=0.11,
        overrides={"ftable": ft, "wtable": wt, "sgr_mb": sgr},
    )
    e = torch.linspace(0.5, 12.0, 40, dtype=torch.float64)
    loss = fstrength_gp(gp, 0.0, e, 1, 1).log().sum() + fstrength_gp(gp, 0.0, e, 0, 1).log().sum()
    loss.backward()
    for name, t, idx in (("ftable", ft, (1, 1)), ("wtable", wt, (1, 1)), ("sgr", sgr, (0, 1, 1))):
        g = t.grad[idx]
        assert torch.isfinite(t.grad).all() and float(g) != 0.0, f"no gradient to {name}"
    # ftable is a pure scale on the table: d(sum log f)/d ftable = N / ftable at ftable = 1
    assert float(ft.grad[1, 1]) == pytest.approx(40.0, rel=1e-9)


def test_locate_reproduces_fortran_bisection_on_a_non_monotonic_table():
    """After the wtable stretch e(1) can drop below e(0) = 0; TALYS's bisection still returns a
    definite interval there, and searchsorted would not."""
    xx = torch.tensor([0.0, -1.2, -1.0, 0.5, 2.0, 3.0], dtype=torch.float64)

    def fortran(xx, x):
        ib, ie = 0, len(xx) - 1
        jl, ju = ib - 1, ie + 1
        asc = xx[ie] >= xx[ib]
        while ju - jl > 1:
            jm = (ju + jl) // 2
            if asc == (x >= xx[jm]):
                jl = jm
            else:
                ju = jm
        if x == xx[ib]:
            return ib
        if x == xx[ie]:
            return ie - 1
        return jl

    xs = torch.tensor([-1.1, -0.5, 0.0, 0.2, 0.5, 1.0, 2.5, 3.0, 4.0], dtype=torch.float64)
    got = _locate(xx, xs).tolist()
    assert got == [fortran(xx.tolist(), float(x)) for x in xs]


def test_quasideuteron_zero_below_deuteron_binding():
    e = torch.tensor([1.0, 2.224, 2.3, 30.0, 150.0], dtype=torch.float64)
    q = quasideuteron(e, 40, 90)
    assert (
        float(q[0]) == 0.0 and float(q[1]) == 0.0 and float(q[2]) > 0.0 and torch.isfinite(q).all()
    )
