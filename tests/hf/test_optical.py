"""T5 spherical optical-model solver against TALYS/ECIS (gates A-trans and A-inc, p95 of
|ln(port/TALYS)| <= 0.01, docs/results/hf-engine-gates.md).

Three layers, weakest dependency first:

1. Unit tests with no external data: Coulomb functions against Riccati-Bessel and the Wronskian,
   the ECIS card rounding and its straight-through gradient, unitarity, the j-axis padding rule
   of contract §5, `process_tjl`'s fill-in and lmax, and differentiability wrt the OMP
   parameters (§4.4).
2. An ECIS oracle checked into this file: the exact `ecisinv.inp`/`ecisinc.inp` card for
   n + 56Fe at 6 MeV, and the T_lj and cross sections ECIS itself wrote to `ecis.inctr` /
   `ecisinc.out` for it. This pins the solver to ECIS with nothing installed.
3. The gates, read straight out of the reference dump archives in `features/hf_reference/raw`
   with `physics.hf.yandf`, not through `reference.py`'s parquet: T0's `block_index.parquet`
   misattributes block metadata (2026-09-13), and the raw text is the thing the
   gate is defined against. Skips when the archives are absent.

Energy convention. `omppar_<p>.out` and `transmission_<p>.out` are both written on ECIS's
laboratory energy `e = egrid/specmass` (inverseecis.f90:403 computes it once and both the
parameter row and the ECIS card use it), so the column is handed to the solver unchanged. Only
`inverse.inverse_channels`, which starts from T1's `EmissionGrid` (egrid), divides by specmass.
"""

from __future__ import annotations

import math
import os
import tarfile
from functools import cache
from pathlib import Path

import numpy as np
import pytest
import torch

from physics.hf import yandf
from physics.hf.core.constants import nuclide_symbol, talys_structure_path
from physics.hf.core.tensors import DTYPE
from physics.hf.core.units import S0_PRINT_SCALE
from physics.hf.omp import schrodinger as sch
from physics.hf.omp.incident import strength_functions
from physics.hf.omp.inverse import process_tjl

TOL = 0.01  # A-trans and A-inc
FLOOR = 1.0e-6  # T floor of the A-trans gate (contract §6)
RAW = Path(__file__).resolve().parents[2] / "features" / "hf_reference" / "raw"
# Extraction cache. Outside the repo on purpose: the 14 archives are ~260 MB unpacked and
# nothing here belongs in git. Override with HF_RAW_CACHE.
EX = Path(os.environ.get("HF_RAW_CACHE", Path.home() / ".cache" / "incognita" / "hf_raw"))
# the files each gate reads out of an archive
WANTED = tuple(
    [f"{stem}_{p}.out" for stem in ("transmission", "omppar") for p in "npdtha"]
    + [f"cross_{p}.tot" for p in "npdtha"]
    + ["talys.out"]
)
PFILE = {1: "n", 2: "p", 3: "d", 4: "t", 5: "h", 6: "a"}
# the 14 spherical reference targets (talys_reference.py), which is what A-trans/A-inc are on
SPHERICAL = [
    ("Ca040", 20, 40), ("Fe056", 26, 56), ("Co059", 27, 59), ("Ni058", 28, 58),
    ("Zr090", 40, 90), ("Nb093", 41, 93), ("Mo098", 42, 98), ("Sn120", 50, 120),
    ("I127", 53, 127), ("Ba138", 56, 138), ("Ce140", 58, 140), ("Au197", 79, 197),
    ("Pb208", 82, 208), ("Bi209", 83, 209),
]  # fmt: skip


def _structure_ok() -> bool:
    try:
        talys_structure_path()
        return True
    except FileNotFoundError:
        return False


have_structure = pytest.mark.skipif(not _structure_ok(), reason="TALYS structure database absent")
have_raw = pytest.mark.skipif(not RAW.is_dir(), reason="reference dump archives absent")


# ------------------------------------------------------------------ 1. Coulomb / Bessel functions
def test_coulomb_functions_are_riccati_bessel_when_eta_is_zero():
    sp = pytest.importorskip("scipy.special")
    lmax = 12
    rho = torch.tensor([0.5, 5.0, 11.0, 20.0], dtype=DTYPE)
    F, dF, G, dG = sch.coulomb_functions(torch.zeros(4, dtype=DTYPE), rho, lmax)
    L = np.arange(lmax + 1)
    r = rho.numpy()[:, None]
    assert F.numpy() == pytest.approx(r * sp.spherical_jn(L, r), rel=1e-10, abs=1e-12)
    assert G.numpy() == pytest.approx(-r * sp.spherical_yn(L, r), rel=1e-10, abs=1e-12)


@pytest.mark.parametrize("eta", [0.0, 0.5, 3.0, 12.0])
def test_coulomb_functions_satisfy_the_wronskian(eta):
    """F'G - FG' = 1 for every L: the identity the matching normalisation relies on."""
    rho = torch.tensor([2.0, 8.0, 25.0], dtype=DTYPE)
    F, dF, G, dG = sch.coulomb_functions(torch.full((3,), eta, dtype=DTYPE), rho, 10)
    w = dF * G - F * dG
    assert w.numpy() == pytest.approx(np.ones_like(w.numpy()), rel=1e-9)


def test_coulomb_functions_below_the_barrier_match_the_series():
    """Charged, sub-barrier (rho well under 2 eta): G comes from an inward integration."""
    mp = pytest.importorskip("mpmath")
    eta, rho = 8.0, 3.0
    F, dF, G, dG = sch.coulomb_functions(
        torch.tensor([eta], dtype=DTYPE), torch.tensor([rho], dtype=DTYPE), 4
    )
    for L in range(5):
        f, g = mp.coulombf(L, eta, rho), mp.coulombg(L, eta, rho)
        assert float(F[0, L]) == pytest.approx(float(f), rel=1e-7)
        assert float(G[0, L]) == pytest.approx(float(g), rel=1e-7)


def test_coulomb_functions_unchanged_by_the_numpy_loops():
    """SPEED1 moved the inward Numerov and the continued fraction from per-step torch ops to
    numpy with the same floating-point operations. The fixture holds three calls captured from
    the golden speed harness (scripts/hf_speed_bench.py) BEFORE that change: the last charged
    inverse channel of Fe-56, Ca-40 and Pb-208 (eta up to 1578, deep sub-barrier, including the
    entries that overflow to inf/nan). Bit-identical on the capture machine; reasonably close
    elsewhere (project rule, 2026-09-16: no bit-identity anywhere, <=1e-6 relative is the
    standard): cross-machine libm/numpy rounding measured up to 3.6e-12 on this Mac (MACFIX2)
    and ~1.8e-12 on x86 (X86VERIFY), both far under this bound."""
    z = np.load(Path(__file__).parent / "fixtures" / "coulomb_functions_speed1.npz")
    for j in range(3):
        got = sch.coulomb_functions(
            torch.from_numpy(z[f"c{j}_eta"]), torch.from_numpy(z[f"c{j}_rho"]), int(z[f"c{j}_lmax"])
        )
        for name, g in zip(("F", "dF", "G", "dG"), got, strict=True):
            ref, g = z[f"c{j}_{name}"], g.numpy()
            assert np.array_equal(np.isfinite(ref), np.isfinite(g)), (j, name)
            fin = np.isfinite(ref)
            assert np.array_equal(np.sign(ref[~fin]), np.sign(g[~fin]), equal_nan=True), (j, name)
            den = np.maximum(np.abs(ref[fin]), np.abs(g[fin]))
            rel = np.abs(ref[fin] - g[fin]) / np.where(den > 0, den, 1.0)
            assert rel.max(initial=0.0) <= 1e-6, (j, name, rel.max())


# ---------------------------------------------------------------------- 1. ECIS card conventions
def test_ecis_card_rounding_matches_the_fortran_format():
    e = torch.tensor([6.0, 1.018033e-3, 0.0234567, 0.009999], dtype=DTYPE)
    got = sch.ecis_card_energy(e)
    # f10.5 at or above 0.01 MeV, es10.3 below (ecisinput.f90)
    assert float(got[0]) == pytest.approx(6.0)
    assert float(got[1]) == pytest.approx(1.018e-3)
    assert float(got[2]) == pytest.approx(0.02346)
    assert float(got[3]) == pytest.approx(9.999e-3)
    v = sch.ecis_card_value(torch.tensor([1.186004, 55.934937, 1234.5678], dtype=DTYPE))
    assert float(v[0]) == pytest.approx(1.186)
    assert float(v[1]) == pytest.approx(55.93494)
    assert float(v[2]) == pytest.approx(1.235e3)


def test_ecis_card_rounding_is_a_straight_through_estimator():
    """Forward value is ECIS's rounded one; the gradient is the unrounded parameter's (§4.4)."""
    x = torch.tensor([1.1860049], dtype=DTYPE, requires_grad=True)
    y = sch.ecis_card_value(x)
    assert float(y.detach()) == pytest.approx(1.186)
    y.backward()
    assert float(x.grad) == pytest.approx(1.0)


# ------------------------------------------------------------------------------ 1. the j-axis rule
def test_j_axis_padding_follows_the_contract():
    """§5: n/p/t/h use 2 columns, d 3, alpha 1, padded to 3 with zeros."""
    assert sch.NJ == {1: 2, 2: 2, 3: 3, 4: 2, 5: 2, 6: 1}
    for k, nj in sch.NJ.items():
        spin = sch.PARSPIN[k]
        _, jv, valid, _ = sch._lj_grid(4, spin)
        assert jv.shape[1] == nj
        assert bool(valid[1:].all())  # only l = 0 can lose a j value


def test_process_tjl_fills_in_the_value_ecis_omits_and_finds_lmax():
    t = torch.zeros(1, 6, 3, dtype=DTYPE)
    t[0, :, 0] = torch.tensor([0.0, 0.4, 0.2, 1e-3, 1e-7, 0.0])
    t[0, :, 1] = torch.tensor([0.8, 0.5, 0.0, 1e-3, 1e-7, 0.0])
    out, tl, lmax = process_tjl(t, 1)
    # l = 0 has no j = l-1/2, so TALYS leaves that column zero (transmission_<p>.out prints
    # 0.000000E+00 there); only l > 0 gets the missing T(l-1/2) filled from T(l+1/2).
    assert float(out[0, 0, 0]) == 0.0
    assert float(out[0, 2, 1]) == pytest.approx(0.2)  # T(l+1/2) filled from T(l-1/2)
    assert float(out[0, 0, 1]) == pytest.approx(0.8)
    # spin-averaged T_l = ((l+1) T(l+1/2) + l T(l-1/2)) / (2l+1)
    assert float(tl[0, 1]) == pytest.approx((2 * 0.5 + 1 * 0.4) / 3)
    # teps = max(T_0 translimit/(2l+1), transeps) = 8.9e-7 here, so l = 4 (T = 1e-7) is
    # already below it and lmax is the last l above: 3.
    assert int(lmax) == 3


# ------------------------------------------------------------------------- 2. the ECIS oracle
# n + 56Fe at 6.000 MeV. Card exactly as ecisinput.f90 wrote it (`ecisinc.inp`); T_lj and cross
# sections exactly as ECIS-06 wrote them back (`ecis.inctr`, `ecisinc.out`), TALYS-2.24 with the
# reference-dump input (localomp y, KD03 local parameters for Fe56).
ECIS_CARD = dict(
    v_mev=50.83657, rv_fm=1.186, av_fm=0.663, w_mev=0.46568, rw_fm=1.186, aw_fm=0.663,
    vd_mev=0.0, rvd_fm=1.282, avd_fm=0.532, wd_mev=7.36873, rwd_fm=1.282, awd_fm=0.532,
    vso_mev=5.73512, rvso_fm=1.0, avso_fm=0.58, wso_mev=-0.02853, rwso_fm=1.0, awso_fm=0.58,
    rc_fm=0.0,
)  # fmt: skip
ECIS_MASS_AMU = 55.93494
ECIS_TLJ = {  # (l, 2j) -> T
    (0, 1): 8.82143468e-01, (1, 1): 6.31721316e-01, (1, 3): 6.70267681e-01,
    (2, 3): 9.15128525e-01, (2, 5): 7.76666818e-01, (5, 11): 4.30821876e-02,
    (9, 17): 7.15477887e-07, (12, 23): 3.00424339e-10, (16, 33): 1.05893222e-14,
    (20, 39): 2.51875240e-19,
}  # fmt: skip
ECIS_XS_MB = dict(sigma_tot_mb=3571.758710, sigma_reac_mb=1565.249988, sigma_shape_el_mb=2006.508722)


class _Card:
    def __init__(self, **kw):
        for k, v in kw.items():
            setattr(self, k, torch.tensor([v], dtype=DTYPE))


def _ecis_oracle_solution():
    return sch.solve_spherical(
        _Card(**ECIS_CARD), 26, 56, 1, torch.tensor([6.0], dtype=DTYPE),
        m_targ_amu=ECIS_MASS_AMU, lmax=20,
    )


@pytest.mark.parametrize("lj", sorted(ECIS_TLJ))
def test_solver_reproduces_ecis_transmission_coefficients(lj):
    l, j2 = lj
    t = _ecis_oracle_solution().tjl[0, 0, 0]
    col = 0 if j2 < 2 * l else 1  # [T(l-1/2), T(l+1/2)]
    assert float(t[l, col]) == pytest.approx(ECIS_TLJ[lj], rel=1e-5)


@pytest.mark.parametrize("quantity", sorted(ECIS_XS_MB))
def test_solver_reproduces_ecis_cross_sections(quantity):
    tr = _ecis_oracle_solution()
    assert float(getattr(tr, quantity)[0, 0, 0]) == pytest.approx(ECIS_XS_MB[quantity], rel=1e-7)


def test_ecis_grid_reproduces_the_step_and_matching_radius_ecis_prints():
    """`lect` defaults: h = min(min(a)/2, 1/(2k)), rm = max(R + a ln(|V| k /(aconv E))), Rc."""
    # the projectile mass goes on the card as f10.5, so the kinematics uses the rounded value
    m_proj = float(sch.ecis_card_value(torch.tensor(sch.PARMASS_AMU[1], dtype=DTYPE)))
    assert m_proj == pytest.approx(1.00866)  # `ecisinc.inp` first level card
    kin = sch.ecis_kinematics(torch.tensor([6.0], dtype=DTYPE), m_proj, ECIS_MASS_AMU, 0.0)
    h, ism, rm = sch.ecis_grid(_Card(**ECIS_CARD), ECIS_MASS_AMU, kin)
    assert float(h) == pytest.approx(0.2667788092, rel=1e-9)  # ecisinc.out "step size"
    assert float(rm) == pytest.approx(20.809, abs=5e-4)  # ecis.pot "matching radius"
    assert float(kin.k_fm) == pytest.approx(0.5293572544, rel=1e-9)  # "wave number"
    # "reduced mass" of the same table, in MeV
    assert float(kin.mu_coef / sch.ECIS_CK * sch.ECIS_CM_MEV) == pytest.approx(
        928.5028958878, rel=1e-9
    )


# ---------------------------------------------------------------------------- 1. solver invariants
def test_transmission_is_bounded_and_a_real_potential_absorbs_nothing():
    card = dict(ECIS_CARD, w_mev=0.0, wd_mev=0.0, wso_mev=0.0)
    tr = sch.solve_spherical(
        _Card(**card), 26, 56, 1, torch.tensor([6.0], dtype=DTYPE),
        m_targ_amu=ECIS_MASS_AMU, lmax=12,
    )
    assert float(tr.tjl.abs().max()) < 1e-9
    assert float(tr.sigma_reac_mb.abs().max()) < 1e-6
    full = _ecis_oracle_solution().tjl
    assert bool(((full >= 0.0) & (full <= 1.0)).all())


def test_solver_is_batched_over_energy():
    e = torch.tensor([1.0, 6.0, 14.0], dtype=DTYPE)
    p = _Card(**ECIS_CARD)
    both = sch.solve_spherical(p, 26, 56, 1, e, m_targ_amu=ECIS_MASS_AMU, lmax=12)
    for i in range(3):
        one = sch.solve_spherical(
            p, 26, 56, 1, e[i : i + 1], m_targ_amu=ECIS_MASS_AMU, lmax=12
        )
        assert both.tjl[0, 0, i].numpy() == pytest.approx(one.tjl[0, 0, 0].numpy(), rel=1e-12)


def test_transmission_is_differentiable_wrt_the_potential_depths():
    """Contract §4.4: gradients flow to every continuous OMP parameter, with no NaN."""
    card = {k: torch.tensor([v], dtype=DTYPE, requires_grad=True) for k, v in ECIS_CARD.items()}
    p = _Card()
    for k, v in card.items():
        setattr(p, k, v)
    tr = sch.solve_spherical(p, 26, 56, 1, torch.tensor([6.0], dtype=DTYPE),
                             m_targ_amu=ECIS_MASS_AMU, lmax=8)
    tr.sigma_reac_mb.sum().backward()
    for name in ("v_mev", "w_mev", "wd_mev", "rv_fm", "av_fm", "rwd_fm", "awd_fm", "vso_mev"):
        g = card[name].grad
        assert g is not None and torch.isfinite(g).all(), name
        assert float(g.abs()) > 0.0, name
    # finite-difference check on the volume depth
    with torch.no_grad():
        d = 1e-4
        up = dict(ECIS_CARD, v_mev=ECIS_CARD["v_mev"] + d)
        dn = dict(ECIS_CARD, v_mev=ECIS_CARD["v_mev"] - d)
        f = [float(sch.solve_spherical(_Card(**c), 26, 56, 1, torch.tensor([6.0], dtype=DTYPE),
                                       m_targ_amu=ECIS_MASS_AMU, lmax=8).sigma_reac_mb)
             for c in (up, dn)]
    assert float(card["v_mev"].grad) == pytest.approx((f[0] - f[1]) / (2 * d), rel=2e-3)


def test_njmax_is_recomputed_per_energy_and_the_l_cap_follows_the_ejectile_spin():
    """`njmax(nen)` = max(20, int(2.4 1.25 A^1/3 0.22 sqrt(m E))), capped at numl - 2, and the
    highest l ECIS writes is njmax - 1 + ceil(parspin), not njmax - 1 for everything.

    ECIS's total-J loop is `naj = jmin + 2 ipj - 2` over `ipj = 1..njmax` (ecist.f cal1-244,
    cal1-355), so it covers njmax consecutive J and the top l is J_max + parspin. Read off ECIS's
    own `tr020041` for n + Ca-40 (`ecissave y`): a saturated nucleon block has nJ = 2 njmax = 40
    and top l 20 = njmax, a deuteron block nJ = 39 and top l 20, and an alpha block nJ = njmax
    with top l = njmax - 1 (19 where njmax = 20, 20 at the two energies where njmax = 21) --
    leaving T(l = 19) = 3.8e-5 unwritten, so it is the cap and not convergence.
    """
    e = torch.tensor([1.0e-3, 0.1, 1.0, 20.0], dtype=DTYPE)
    # A = 40, neutron: the sqrt term never reaches 20, so the floor binds at every energy
    assert sch.njmax_grid(40, sch.PARMASS_AMU[1], e).tolist() == [20, 20, 20, 20]
    assert sch.lmax_ecis_grid(40, 1, e).tolist() == [20, 20, 20, 20]
    assert sch.lmax_ecis_grid(40, 3, e).tolist() == [20, 20, 20, 20]  # deuteron, parspin 1
    assert sch.lmax_ecis_grid(40, 6, e).tolist() == [19, 19, 19, 19]  # alpha, parspin 0
    # alpha on a Pb residual at 20 MeV: 2.4 * 1.25 * 205^(1/3) * 0.22 * sqrt(4.0026 * 20) = 34.8
    assert sch.njmax_grid(205, sch.PARMASS_AMU[6], e).tolist() == [20, 20, 20, 34]
    assert int(sch.njmax_grid(205, sch.PARMASS_AMU[6], e).max()) == sch.njmax_ecis(
        205, sch.PARMASS_AMU[6], e)
    # numl - 2 is the ceiling (inverseecis.f90:411)
    hot = torch.tensor([4.0e4], dtype=DTYPE)
    assert int(sch.njmax_grid(205, sch.PARMASS_AMU[6], hot)) == 58


def test_inverse_particle_zeroes_l_above_the_ecis_cap_and_keeps_the_cap_itself():
    """TALYS's `Tjl` is a hard zero above ECIS's l cap however large the coefficient really is,
    because `inverseecis` never asks for those j values -- and it is NOT zero at the cap.

    `densprepare` interpolates three of these cells per outgoing energy, so filling the ones
    TALYS leaves empty, or emptying the one it fills, both corrupt `Tjlnex` at the top l.
    """
    from physics.hf.omp.inverse import inverse_particle

    e = torch.tensor([20.0], dtype=DTYPE)
    tr = inverse_particle(26, 56, 1, e, _Card(**ECIS_CARD), m_res_amu=ECIS_MASS_AMU, lmax=30)
    lc = int(sch.lmax_ecis_grid(56, 1, e)[0])
    t = tr.tjl[0, 0].detach()
    assert float(t[0, lc, :2].abs().max()) > 0.0, f"l = {lc} (the cap) must survive"
    assert float(t[0, lc + 1 :, :].abs().max()) == 0.0, f"l > {lc} must be zero"


def test_strength_functions_follow_spr():
    """S0 = T_0/(2 pi sqrt(E[eV])), S1 = T_1 (1+(kR)^2)/(kR)^2 /(2 pi sqrt(E[eV])), R = 1.35 A^1/3."""
    t_l = torch.tensor([[0.001, 0.002]], dtype=DTYPE)
    e = torch.tensor([1.0e-5], dtype=DTYPE)
    el = torch.tensor([5000.0], dtype=DTYPE)
    k = torch.tensor([0.0007], dtype=DTYPE)
    s0, s1, rp = strength_functions(t_l, e, el, torch.tensor([56]), k)
    efac = 1.0 / (math.sqrt(1e6 * 1e-5) * 2.0 * math.pi)
    r2k2 = (1.35 * 56 ** (1 / 3) * 0.0007) ** 2
    assert float(s0) == pytest.approx(0.001 * efac)
    assert float(s1) == pytest.approx(0.002 * efac * (1 + r2k2) / r2k2)
    assert float(rp) == pytest.approx(math.sqrt(0.1 * 5000.0 / (4 * math.pi)))


# ----------------------------------------------------------------------- 3. reading the dumps raw
@cache
def _archive(target: str, variant: str = "default") -> Path | None:
    """The files of `WANTED` from one dump archive, extracted into the cache (once per file)."""
    stem = f"{variant}__{target}"
    src = RAW / f"{stem}.tar.gz"
    if not src.is_file():
        return None
    dest = EX / stem
    missing = [n for n in WANTED if not (dest / n).is_file()]
    if missing:
        dest.mkdir(parents=True, exist_ok=True)
        with tarfile.open(src) as tf:
            for name in missing:
                try:
                    member = tf.getmember(f"{stem}/{name}")
                except KeyError:
                    continue  # not every particle channel exists for every target
                tf.extract(member, EX, filter="data")
    return dest


OMPPAR_COLUMNS = (
    "V", "rv", "av", "W", "rw", "aw", "Vd", "rvd", "avd", "Wd", "rwd", "awd",
    "Vso", "rvso", "avso", "Wso", "rwso", "awso", "rc",
)  # fmt: skip


class _DumpOMP:
    """The 19 omppar_<p>.out columns as an OMPParameters-shaped object (the injection rule, §5)."""

    def __init__(self, block):
        self.e_mev = torch.tensor(block.column("E"), dtype=DTYPE)
        for field, col in zip(sch._FIELDS, OMPPAR_COLUMNS, strict=True):
            setattr(self, field, torch.tensor(block.column(col), dtype=DTYPE))

    def at(self, idx: torch.Tensor) -> "_DumpOMP":
        out = _DumpOMP.__new__(_DumpOMP)
        out.e_mev = self.e_mev[idx]
        for field in sch._FIELDS:
            setattr(out, field, getattr(self, field)[idx])
        return out


def _read_transmission(path: Path):
    """(e_mev (E,), tjl (E, L+1, nj), open (E,)) from transmission_<p>.out."""
    blocks = yandf.parse_blocks(path)
    jcols = [c for c in blocks[0].columns if c.startswith("T(") and c != "T(L))"] or ["T(L))"]
    energies = [b.meta_float("energy") for b in blocks]
    tabs = [b if b.data.size else None for b in blocks]
    lmax = max(int(b.column("L").max()) for b in tabs if b is not None)
    tjl = np.zeros((len(tabs), lmax + 1, len(jcols)))
    for i, b in enumerate(tabs):
        if b is None:
            continue
        L = b.column("L").astype(int)
        for k, c in enumerate(jcols):
            tjl[i, L, k] = b.column(c)
    return np.array(energies), tjl, np.array([b is not None for b in tabs])


def _r(port: np.ndarray, talys: np.ndarray, floor: float) -> np.ndarray:
    m = np.isfinite(port) & np.isfinite(talys) & (talys > floor) & (port > 0)
    return np.abs(np.log(port[m] / talys[m]))


# --------------------------------------------------------------------------------- 3. A-trans
@have_raw
@have_structure
@pytest.mark.parametrize("target,Z,A", SPHERICAL, ids=[t[0] for t in SPHERICAL])
def test_a_trans_gate(target, Z, A, record_property):
    """T(l+-1/2) for n, p, d, t, h, alpha on the residual each leaves, with the OMP parameters
    injected from omppar_<p>.out: p95 |ln(port/TALYS)| <= 1% over T > 1e-6."""
    d = _archive(target)
    if d is None:
        pytest.skip(f"{target} dump absent")
    res = []
    for k in range(1, 7):
        tfile, ofile = d / f"transmission_{PFILE[k]}.out", d / f"omppar_{PFILE[k]}.out"
        if not (tfile.is_file() and ofile.is_file()):
            continue
        block = yandf.parse_blocks(ofile)[0]
        p = _DumpOMP(block)
        Zr, Ar = int(block.meta["Z"]), int(block.meta["A"])
        e_t, tjl_t, is_open = _read_transmission(tfile)
        n = min(len(p.e_mev), len(e_t))
        assert p.e_mev[:n].numpy() == pytest.approx(e_t[:n], rel=1e-6, abs=1e-9), (
            f"{target} {PFILE[k]}: omppar and transmission energy grids disagree"
        )
        idx = torch.tensor(np.nonzero(is_open[:n])[0])
        if not idx.numel():
            continue
        lmax = tjl_t.shape[1] - 1
        tr = sch.solve_spherical(
            p.at(idx), Zr, Ar, k, p.e_mev[idx],
            m_targ_amu=sch.nucleus_mass_amu(Zr, Ar), lmax=lmax,
        )
        port, _, _ = process_tjl(tr.tjl[0, 0], k)
        nj = sch.NJ[k]
        res.append(_r(port[..., :nj].detach().numpy(), tjl_t[idx.numpy()][:, :, :nj], FLOOR))
    r = np.concatenate(res)
    p95 = float(np.quantile(r, 0.95))
    record_property("A-trans", {"target": target, "n": int(r.size), "median": float(np.median(r)),
                                "p95": p95, "max": float(r.max())})
    assert p95 <= TOL, f"{target}: A-trans p95 {p95:.3e} > {TOL} (max {r.max():.3e}, n={r.size})"


# ------------------------------------------------ 3. A-trans sliced: bands, top l, zeroed cells
# `test_a_trans_gate` pools ~55k coefficients over six ejectiles, 68 emission energies and 15 l
# values into ONE p95, and `_r`'s mask silently drops any cell the port makes zero. That pooling
# is how the Ca-40 compound-elastic failure stayed invisible: it lived at Eout ~ 0.1 MeV in the
# last l TALYS prints, a few dozen cells out of 55k. Below, nothing is pooled across bands or
# cell classes, and a port zero under a live TALYS value fails outright instead of vanishing.
EOUT_BANDS: tuple[tuple[float, float], ...] = (
    (0.0, 0.1), (0.1, 0.5), (0.5, 2.0), (2.0, 8.0), (8.0, float("inf")),
)
# The five deformed reference targets. TALYS runs their INCIDENT channel as ECIS coupled channels
# (T13), but `inverseecis` takes the spherical branch for every emitted particle on every
# residual, so their emission grids are in scope for A-trans exactly like the 14 spherical ones.
DEFORMED = [("Nd150", 60, 150), ("Sm152", 62, 152), ("Gd157", 64, 157),
            ("Er166", 68, 166), ("W184", 74, 184)]  # fmt: skip


def _band_label(lo: float, hi: float) -> str:
    if lo == 0.0:
        return f"Eout<{hi:g}"
    if hi == float("inf"):
        return f"Eout>={lo:g}"
    return f"{lo:g}<=Eout<{hi:g}"


def _slice_stats(v: np.ndarray) -> dict:
    if not v.size:
        return {"n": 0}
    return {"n": int(v.size), "median": float(np.median(v)), "p95": float(np.quantile(v, 0.95)),
            "max": float(v.max())}


def a_trans_slices(target: str, Z: int, A: int) -> dict:
    """A-trans for one target, sliced instead of pooled.

    `{"bands": {label: {particle: stats}}, "top_l": stats, "zeroed": [cells]}`. `top_l` holds only
    the cells at the highest l TALYS printed at that energy -- its `lmax(type, nen)`, the last l
    before every T_lj drops under `translimit`, and the smallest coefficient in the block.
    `zeroed` lists every cell where TALYS has T > 1e-6 and the port produced 0, which is the class
    `_r`'s `port > 0` mask discards.

    TALYS: inverseecis.f90:1 (inverseecis), inverseread.f90:1 (inverseread)
    Test: A-trans
    """
    d = _archive(target)
    if d is None:
        return {}
    bands: dict = {_band_label(*b): {} for b in EOUT_BANDS}
    top: list[np.ndarray] = []
    zeroed: list[dict] = []
    for k in range(1, 7):
        tfile, ofile = d / f"transmission_{PFILE[k]}.out", d / f"omppar_{PFILE[k]}.out"
        if not (tfile.is_file() and ofile.is_file()):
            continue
        block = yandf.parse_blocks(ofile)[0]
        p = _DumpOMP(block)
        Zr, Ar = int(block.meta["Z"]), int(block.meta["A"])
        e_t, tjl_t, is_open = _read_transmission(tfile)
        n = min(len(p.e_mev), len(e_t))
        idx = torch.tensor(np.nonzero(is_open[:n])[0])
        if not idx.numel():
            continue
        tr = sch.solve_spherical(p.at(idx), Zr, Ar, k, p.e_mev[idx],
                                 m_targ_amu=sch.nucleus_mass_amu(Zr, Ar),
                                 lmax=tjl_t.shape[1] - 1)
        port, _, _ = process_tjl(tr.tjl[0, 0], k)
        nj = sch.NJ[k]
        a = port[..., :nj].detach().numpy()
        b = tjl_t[idx.numpy()][:, :, :nj]
        e = p.e_mev[idx].numpy()
        live = b > FLOOR
        # highest l TALYS printed at each energy, i.e. lmax(type, nen)
        any_l = live.any(2)
        is_top = np.zeros_like(live)
        for i in np.nonzero(any_l.any(1))[0]:
            is_top[i, live.shape[1] - 1 - any_l[i, ::-1].argmax()] = True
        is_top &= live
        for i, ll, jj in zip(*np.nonzero(live & (a <= 0.0))):  # noqa: B905
            zeroed.append({"particle": PFILE[k], "e_mev": float(e[i]), "l": int(ll),
                           "j_index": int(jj), "talys": float(b[i, ll, jj])})
        r = np.zeros_like(b)
        ok = live & (a > 0.0)
        r[ok] = np.abs(np.log(a[ok] / b[ok]))
        for lo, hi in EOUT_BANDS:
            sel = ok & ((e >= lo) & (e < hi))[:, None, None]
            if sel.any():
                bands[_band_label(lo, hi)][PFILE[k]] = _slice_stats(r[sel])
        if (ok & is_top).any():
            top.append(r[ok & is_top])
    return {"target": target, "bands": bands, "zeroed": zeroed,
            "top_l": _slice_stats(np.concatenate(top) if top else np.zeros(0))}


@have_raw
@have_structure
@pytest.mark.parametrize("target,Z,A", SPHERICAL + DEFORMED,
                         ids=[t[0] for t in SPHERICAL + DEFORMED])
def test_a_trans_by_energy_band_and_top_l(target, Z, A, record_property):
    """A-trans per Eout band -- two of them under 0.5 MeV -- and for the top-l cell on its own,
    over the 14 spherical targets AND the five deformed ones' emission channels.

    Same comparison as `test_a_trans_gate` with the pooling removed, so a defect confined to low
    Eout or to the last l cannot hide behind 55k passing cells.
    """
    s = a_trans_slices(target, Z, A)
    if not s:
        pytest.skip(f"{target} dump absent")
    record_property("A-trans-bands", s)
    assert not s["zeroed"], (
        f"{target}: port zeroed {len(s['zeroed'])} cells TALYS reports above {FLOOR:g}; "
        f"first three {s['zeroed'][:3]}")
    bad = {label: {q: st for q, st in per.items() if st["p95"] > TOL}
           for label, per in s["bands"].items()}
    bad = {label: v for label, v in bad.items() if v}
    assert not bad, f"{target}: A-trans p95 over {TOL} by band: {bad}"
    assert s["top_l"]["n"] == 0 or s["top_l"]["p95"] <= TOL, (
        f"{target}: A-trans top-l cell p95 {s['top_l']['p95']:.3e} > {TOL} "
        f"(n={s['top_l']['n']}, max {s['top_l']['max']:.3e})")


@have_raw
@have_structure
def test_inverse_reaction_cross_sections_match_cross_p_tot():
    """sigma_R on the emission grid against cross_<p>.tot, the other half of A-trans."""
    d = _archive("Fe056")
    if d is None:
        pytest.skip("Fe056 dump absent")
    worst = 0.0
    for k in (1, 2, 6):
        block = yandf.parse_blocks(d / f"omppar_{PFILE[k]}.out")[0]
        p = _DumpOMP(block)
        Zr, Ar = int(block.meta["Z"]), int(block.meta["A"])
        xs = yandf.parse_blocks(d / f"cross_{PFILE[k]}.tot")[0]
        _, _, is_open = _read_transmission(d / f"transmission_{PFILE[k]}.out")
        idx = torch.tensor(np.nonzero(is_open[: len(p.e_mev)])[0])
        tr = sch.solve_spherical(p.at(idx), Zr, Ar, k, p.e_mev[idx],
                                 m_targ_amu=sch.nucleus_mass_amu(Zr, Ar), lmax=30)
        r = _r(tr.sigma_reac_mb[0, 0].detach().numpy(), xs.column("reaction")[idx.numpy()], FLOOR)
        worst = max(worst, float(np.quantile(r, 0.95)))
    assert worst <= TOL, f"inverse sigma_R p95 {worst:.3e} > {TOL}"


# ----------------------------------------------------------------------------------- 3. A-inc
def _incident_reference(talys_out: Path):
    """The `Optical model results` block of talys.out per incident energy, with the energy taken
    from the incident-channel OMP parameter row printed above it."""
    import re

    txt = talys_out.read_text(errors="replace")
    omprow = re.compile(r"^\s{2,}(\d+\.\d+)((?:\s+-?\d+\.\d+){20})\s*$", re.M)
    block = re.compile(
        r"Optical model results\s*\n\s*\n"
        r"\s*Total cross section\s*:\s*(\S+) mb\s*\n"
        r"\s*Reaction cross section:\s*(\S+) mb\s*\n"
        r"\s*Elastic cross section\s*:\s*(\S+) mb"
        r"(?:.*?\n\s*S0:\s*\d+\s+(\S+)\s+\.e-4\s*\n\s*S1:\s*\d+\s+(\S+)\s+\.e-4"
        r"\s*\n\s*R\s*:\s*\d+\s+(\S+)\s+fm)?",
        re.S,
    )
    rows = []
    for m in block.finditer(txt):
        g = m.groups()
        head = omprow.findall(txt[: m.start()])
        if not head:
            continue
        rows.append(dict(
            e_inc_mev=float(head[-1][0]), sigma_tot_mb=float(g[0]),
            sigma_reac_mb=float(g[1]), sigma_shape_el_mb=float(g[2]),
            s0=float(g[3]) * S0_PRINT_SCALE if g[3] else np.nan,
            s1=float(g[4]) * S0_PRINT_SCALE if g[4] else np.nan,
            r_prime_fm=float(g[5]) if g[5] else np.nan,
        ))
    return rows


@have_raw
@have_structure
@pytest.mark.parametrize("target,Z,A", SPHERICAL, ids=[t[0] for t in SPHERICAL])
def test_a_inc_gate(target, Z, A, record_property):
    """Incident sigma_tot / sigma_R / sigma_shape-el and S0, S1, R' against talys.out.

    The incident channel's OMP parameters are not dumped (omppar_<p>.out is the emission grid and
    transmission_inc.out survives only for the last energy, contract §4.1), so they come from
    T4's ported `omp_parameters`, whose own gate A-omppar is p95 3.5e-7.

    Only targets TALYS itself treats as a single spherical channel are in scope: `incidentecis`
    takes the spherical branch at incidentecis.f90:203 for `colltype == 'S'` and otherwise
    couples collective levels, which is ECIS coupled channels (T13, via `ecis.bridge` for now --
    contract §5). Of the 14 spherical reference targets, Au197 is rotational ('R', 5 coupled
    levels) and Ca040 vibrational ('V', 4 phonon levels) in the incident channel, so they are
    skipped here. Their *emission* channels are spherical and are gated by A-trans.
    """
    from physics.hf.input.defaults import default_options, default_params
    from physics.hf.omp import parameters as P
    from physics.hf.omp.parameters import _colltype

    d = _archive(target)
    if d is None:
        pytest.skip(f"{target} dump absent")
    ct = _colltype(Z, A, default_options(Z, A))
    if ct != "S":
        pytest.skip(f"{target}: colltype {ct!r}, incident channel is coupled channels (T13)")
    rows = _incident_reference(d / "talys.out")
    assert rows, f"{target}: no optical model results in talys.out"
    e = torch.tensor([r["e_inc_mev"] for r in rows], dtype=DTYPE)
    o = default_options(Z, A)
    p = P.omp_parameters(Z, A - Z, 1, e, default_params(Z, A, o), o)  # T4 indexes by (Z, N)
    m_t = sch.nucleus_mass_amu(Z, A)
    lmax = sch.njmax_ecis(A, sch.PARMASS_AMU[1], e)
    tr = sch.solve_spherical(p, Z, A, 1, e, m_targ_amu=m_t, lmax=lmax)
    _, t_l, _ = process_tjl(tr.tjl[0, 0], 1)
    kin = sch.ecis_kinematics(sch.ecis_card_energy(e), sch.PARMASS_AMU[1], m_t, 0.0)
    s0, s1, rp = strength_functions(
        t_l, e, tr.sigma_shape_el_mb[0, 0], torch.full((len(rows),), A), kin.k_fm
    )
    port = {"sigma_tot_mb": tr.sigma_tot_mb[0, 0], "sigma_reac_mb": tr.sigma_reac_mb[0, 0],
            "sigma_shape_el_mb": tr.sigma_shape_el_mb[0, 0], "s0": s0, "s1": s1,
            "r_prime_fm": rp}
    worst = {}
    for q, v in port.items():
        ref = np.array([r[q] for r in rows])
        r = _r(v.detach().numpy(), ref, 0.0)
        if r.size:
            worst[q] = float(np.quantile(r, 0.95))
    record_property("A-inc", {"target": target, **worst})
    bad = {q: x for q, x in worst.items() if x > TOL}
    assert not bad, f"{target}: A-inc p95 over {TOL}: {bad}"


if __name__ == "__main__":  # pragma: no cover -- publishes the sliced A-trans table
    # PYTHONPATH=. uv run python tests/hf/test_optical.py [out.json]
    # Writes `a_trans_slices` for every target of SPHERICAL + DEFORMED, per band and per cell
    # class, so the numbers in docs/results are reproducible without parsing pytest output.
    import json as _json
    import sys as _sys

    torch.set_num_threads(2)
    _out = Path(_sys.argv[1]) if len(_sys.argv) > 1 else Path("docs/results/hf-atrans-bands.json")
    _recs = []
    for _t, _z, _a in SPHERICAL + DEFORMED:
        _s = a_trans_slices(_t, _z, _a)
        if not _s:
            continue
        _recs.append(_s)
        _worst = max((st["p95"] for per in _s["bands"].values() for st in per.values()), default=0.0)
        print(f"{_t:>6}  worst band p95 {_worst:.2e}  top-l p95 "
              f"{_s['top_l'].get('p95', 0.0):.2e} (n={_s['top_l'].get('n', 0)})  "
              f"zeroed {len(_s['zeroed'])}", flush=True)
    _out.parent.mkdir(parents=True, exist_ok=True)
    _out.write_text(_json.dumps(
        {"gate": "A-trans sliced", "tol": TOL, "floor": FLOOR,
         "bands": [_band_label(*_b) for _b in EOUT_BANDS], "targets": _recs}, indent=1) + "\n")
    print("wrote", _out)


# ================================================================================================
# DIFFPARAM (gate G0.4): the optical-model family on the autograd graph
# ================================================================================================


def test_transmission_torch_path_matches_numpy():
    """`_transmission(differentiable=True)` is the numpy path's Tjl/Tl **to the bit**.

    The torch path differs in one thing only, and it is one that cannot move a number: it hands
    `inverse_channels` an `edetach` mask that detaches the OMP parameters at the grid points
    outside `[ebegin(type), eend(type)]`, which the caller zeroes anyway. `where(keep, x,
    x.detach())` is the identity forward; it exists so that a deep-sub-barrier alpha row --
    value zero, local derivative infinite -- cannot turn the reverse pass into NaN.

    An earlier version *skipped* those points instead. That also killed the NaN, and it was
    wrong here: dropping rows from the batch changes `nmax` in the Numerov loop, hence the
    number of rescalings the surviving rows go through, and the two paths then differed by
    2e-11 on the proton Tjl. Bit-equality is the property worth having.
    """
    import numpy as np
    import torch

    from physics.hf.compound.dens_reference import _transmission

    a = _transmission(26, 56, 6.0)
    b = _transmission(26, 56, 6.0, None, True)
    for t in range(1, 7):
        for i, name in enumerate(("tjl", "tl")):
            x, y = a[t][i], b[t][i].detach().numpy()
            assert x.shape == y.shape, (t, name)
            assert np.abs(x - y).max() == 0.0, (t, name, np.abs(x - y).max())
        assert np.array_equal(a[t][2], b[t][2]), t


def test_card_rounding_switch_is_forward_only_and_small():
    """`card_rounding(False)` changes the forward value and nothing else about the port.

    ECIS reads its parameters off f10.5 cards and the port quantises them the same way, through
    a straight-through estimator whose gradient is the identity. DIFFPARAM's finite-difference
    check switches the quantisation off so that the difference measures the gradient rather than
    the card resolution; this pins how much that costs the forward value -- parts in 1e5 of a
    transmission coefficient, i.e. the card resolution itself, and never a structural change.
    """
    import torch

    from physics.hf.omp.schrodinger import CARD_ROUNDING, card_rounding, ecis_card_value

    assert CARD_ROUNDING is True, "the default must be TALYS's: cards on"
    x = torch.tensor([1.2345678, 49.876543], dtype=torch.float64, requires_grad=True)
    on = ecis_card_value(x)
    assert torch.allclose(on, torch.tensor([1.23457, 49.87654], dtype=torch.float64))
    with card_rounding(False):
        off = ecis_card_value(x)
        assert torch.equal(off, x)
    assert CARD_ROUNDING is True, "the context manager must restore the default"
    # the straight-through gradient is the identity either way, which is the whole reason the
    # gate may switch the forward quantisation off
    (g_on,) = torch.autograd.grad(on.sum(), x, retain_graph=True)
    with card_rounding(False):
        (g_off,) = torch.autograd.grad(ecis_card_value(x).sum(), x)
    assert torch.equal(g_on, g_off) and torch.equal(g_on, torch.ones_like(x))


# ================================================================================================
# SPEEDT: the non-differentiable inverse path runs all six particles in one pass
# ================================================================================================


def _same_bits(a, b, rel: float = 0.0) -> bool:
    if rel:
        return a.shape == b.shape and bool(
            torch.isclose(a, b, rtol=rel, atol=1e-300, equal_nan=True).all()
        )
    return a.shape == b.shape and bool(((a == b) | (torch.isnan(a) & torch.isnan(b))).all())


def test_coulomb_functions_many_is_each_call_to_the_bit():
    """`coulomb_functions_many` gives every column its own call's continued-fraction start and
    Numerov step count, so each call comes back reasonably close to `coulomb_functions` alone
    (project rule, 2026-09-16: no bit-identity anywhere, <=1e-6 relative is the standard) --
    including calls of different sizes, deep sub-barrier columns and an uncharged call. Batching
    the columns together reorders the floating-point sums; measured on this Mac (MACFIX2) at
    <=7.2e-15 relative, ordinary hardware FP non-associativity, not a different computation."""
    g = torch.Generator().manual_seed(7)
    etas, rhos = [], []
    for n, emax, rmax in ((5, 0.0, 30.0), (9, 40.0, 25.0), (1, 3.0, 2.0), (17, 200.0, 60.0)):
        etas.append(torch.rand(n, generator=g, dtype=DTYPE) * emax)
        rhos.append(0.5 + torch.rand(n, generator=g, dtype=DTYPE) * rmax)
    many = sch.coulomb_functions_many(etas, rhos, 12)
    for e, r, got in zip(etas, rhos, many, strict=True):
        ref = sch.coulomb_functions(e, r, 12)
        for x, y in zip(got, ref, strict=True):
            assert _same_bits(x, y, rel=1e-6)


def test_solve_spherical_many_is_each_particle_to_the_bit():
    """`solve_spherical_many` (one radial loop for all particles) against `solve_spherical`."""
    p = _Card(**ECIS_CARD)
    specs = [(p, 26, 56, k, torch.tensor([0.3, 6.0, 14.0], dtype=DTYPE)[: 3 - (k % 2)],
              ECIS_MASS_AMU, 12) for k in range(1, 7)]
    for (pp, Z, A, k, e, m, lm), got in zip(specs, sch.solve_spherical_many(specs), strict=True):
        ref = sch.solve_spherical(pp, Z, A, k, e, m_targ_amu=m, lmax=lm)
        for f in ("tjl", "sigma_reac_mb", "sigma_tot_mb"):
            assert _same_bits(getattr(got, f), getattr(ref, f)), (k, f)
