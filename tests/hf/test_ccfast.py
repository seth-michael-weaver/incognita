"""CCFAST2: the coupled-channels incident channel without bit-identity.

The project rule (2026-09-14) for speed work that moves bits: per cell <= 1e-6 median and <= 1e-4 worst
against the port before the change. These tests hold the pieces to much tighter bounds than that,
so a failure here means an algebra slip, not rounding:

* `accumulate` in the S - 1 form gives the S form's cross sections, and keeps a nearly-unitary
  block's absorption where the S form has none left;
* per-energy total-J convergence: an energy alone and inside a batch sum the same blocks;
* the incident memo serves a second caller, and misses when a parameter changes;
* `ccfast.c`'s radial loops (W-form below soswitch, derivative coupling above) match SPEEDT3's
  bitwise kernel to rounding.
"""

from __future__ import annotations

import pytest
import torch

from physics.hf.core.tensors import DTYPE
from physics.hf.ecis import ccnative

CD = torch.complex128


@pytest.fixture(autouse=True)
def _one_thread():
    prev = torch.get_num_threads()
    torch.set_num_threads(1)
    yield
    torch.set_num_threads(prev)


def _band(Z, A):
    from physics.hf.ecis.reference import coupled_band

    try:
        return coupled_band(Z, A)
    except Exception as exc:  # noqa: BLE001  (structure database absent on this machine)
        pytest.skip(f"no coupled band for {Z}-{A}: {exc}")


def _grid(n=None):
    e = torch.tensor([1.0e-3, 0.3, 1.5, 4.0, 9.0, 12.0, 20.0], dtype=DTYPE)
    return e if n is None else e[:n]


def _fake_channel(n_ent: int, n: int):
    from types import SimpleNamespace

    level = torch.tensor([0] * n_ent + [1] * (n - n_ent))
    return SimpleNamespace(
        twoJ=3, level=level, l=torch.arange(n), j=torch.arange(n, dtype=DTYPE) + 0.5,
        elastic=level == 0,
    )


def test_minus_identity_accumulate_is_the_s_form_and_keeps_small_absorption():
    from physics.hf.ecis.solver import accumulate

    g = torch.Generator().manual_seed(7)
    n, n_ent = 6, 2
    ch = _fake_channel(n_ent, n)
    op = torch.ones((1, n), dtype=torch.bool)
    # an S with O(1) off-diagonal flux: both forms must give the same cross sections
    d = 0.2 * torch.complex(torch.randn(1, n, n, generator=g, dtype=DTYPE),
                            torch.randn(1, n, n, generator=g, dtype=DTYPE))
    d = 0.5 * (d + d.transpose(1, 2))
    s = torch.eye(n, dtype=CD)[None] + d
    a = accumulate(ch, s, op, None, 0.0, 0.5, 2, n)
    b = accumulate(ch, d, op, None, 0.0, 0.5, 2, n, minus_identity=True)
    for k in ("tot", "el", "direct"):
        assert torch.allclose(a[k], b[k], rtol=1e-13, atol=0), k
    # a nearly unitary block, as at high l: S_00 = exp(2i delta) (1 - T/2) with a small phase
    # delta = 1e-6 and T = 1e-15, so 1 - |S_00|^2 = T - T^2/4. From S the leading 1 cancels and
    # nothing of T is left; from D = S - 1 only 4 delta^2 ~ 4e-12 cancels (ECIS's own form, scam).
    t_true, delta = 1.0e-15, 1.0e-6
    two = torch.tensor(2j * delta, dtype=CD)
    phase = torch.exp(two)
    s00 = phase * (1.0 - t_true / 2.0)
    d00 = torch.expm1(two) - phase * (t_true / 2.0)
    s1 = torch.zeros((1, n, n), dtype=CD)
    d1 = torch.zeros((1, n, n), dtype=CD)
    s1[0, 0, 0], d1[0, 0, 0] = s00, d00
    fac = 2.0  # (2J + 1) / ((2j + 1)(2 I_0 + 1)) for 2J = 3, j = 1/2, I_0 = 0
    want = fac * (t_true - t_true**2 / 4.0)
    got_s = float(accumulate(ch, s1, op, None, 0.0, 0.5, 2, n)["tjl"][0, 0, 1])
    got_d = float(accumulate(ch, d1, op, None, 0.0, 0.5, 2, n, minus_identity=True)
                  ["tjl"][0, 0, 1])
    err_s, err_d = abs(got_s - want) / want, abs(got_d - want) / want
    assert err_d < 1e-9
    assert err_s > 1e-4 and err_s > 1e4 * err_d


def test_one_energy_alone_sums_the_blocks_it_sums_in_a_batch():
    from physics.hf.ecis import incident as inc_mod
    from physics.hf.ecis.incident import incident_coupled

    band = _band(60, 150)
    e = _grid()
    inc_mod._SOLVED.clear()
    batch, rb = incident_coupled(None, 60, 150, e, band, lmax=20)
    for i in (0, 3, 6):
        inc_mod._SOLVED.clear()
        one, r1 = incident_coupled(None, 60, 150, e[i : i + 1], band, lmax=20)
        for k in ("sigma_tot_mb", "sigma_reac_mb", "sigma_shape_el_mb", "sigma_direct_mb"):
            x, y = getattr(rb, k)[i], getattr(r1, k)[0]
            # 1e-10, not 0: the batch's per-energy solves (`_match`) are batched LAPACK calls,
            # and Accelerate on arm64 does not give a lone matrix the batch's last bits (x86 MKL
            # at one thread does). A block missing from either sum would be >= 1e-10 here.
            assert torch.allclose(x, y, rtol=1e-10, atol=1e-12), (k, i, float(x), float(y))
        # T_lj: 1e-9 where it matters, 1e-5 down to 1e-8, which is the sub-barrier blocks' own
        # conditioning (docs/results/hf-speed-profile.md, "Coupled channels without bit-identity")
        for lo, hi, rtol in ((1e-3, 2.0, 1e-9), (1e-8, 1e-3, 1e-5)):
            sel = (batch.tjl_inc[i] > lo) & (batch.tjl_inc[i] <= hi)
            assert torch.allclose(batch.tjl_inc[i][sel], one.tjl_inc[0][sel], rtol=rtol, atol=0)


def test_incident_memo_serves_the_second_caller_and_misses_on_a_changed_potential():
    from physics.hf.ecis import incident as inc_mod
    from physics.hf.ecis.incident import _t4_parameters, incident_coupled

    band = _band(60, 150)
    e = _grid(3)
    inc_mod._SOLVED.clear()
    first, _ = incident_coupled(None, 60, 150, e, band, lmax=20)
    assert len(inc_mod._SOLVED) == 3
    calls = []
    real = inc_mod.solve_rotational
    try:
        inc_mod.solve_rotational = lambda *a, **k: calls.append(1) or real(*a, **k)
        again, _ = incident_coupled(None, 60, 150, e[1:2], band, lmax=20)
        assert not calls
        assert torch.equal(again.sigma_reac_mb[0], first.sigma_reac_mb[1])
        p = _t4_parameters(60, 150, 1, e[1:2], None)
        p.v_mev.mul_(1.001)
        moved, _ = incident_coupled(p, 60, 150, e[1:2], band, lmax=20)
        assert calls
        assert float((moved.sigma_reac_mb[0] - first.sigma_reac_mb[1]).abs()) > 0
    finally:
        inc_mod.solve_rotational = real
        inc_mod._SOLVED.clear()


@pytest.mark.skipif(not ccnative.available(), reason="libccfast.so not built")
@pytest.mark.parametrize("deformed_so", [False, True])
def test_ccfast_kernels_match_speedt3s_loop(deformed_so):
    from physics.hf.ecis.coupling import channels
    from physics.hf.ecis.formfactor import rotational_form_factors
    from physics.hf.ecis.incident import _t4_parameters
    from physics.hf.ecis.solver import _grid_and_kinematics, accumulate, smatrix_blocks
    from physics.hf.omp.schrodinger import PARMASS_AMU, nucleus_mass_amu

    band = _band(92, 238)
    e = _grid()[5:] if deformed_so else _grid(5)  # above / below soswitch
    p = _t4_parameters(92, 238, 1, e, None)
    m_t = nucleus_mass_amu(92, 238)
    kin, h, nmatch, r = _grid_and_kinematics(p, PARMASS_AMU[1], m_t, 0.0, e, band["e_mev"], 1,
                                             True)
    ff = rotational_form_factors(p, m_t, r, band["rotbeta"], band["deformation_length"],
                                 2 * band["rotbeta"].numel(), 0.0, deformed_so)
    chs = [channels(tj, par, band["spin"], band["parity"], 20, band["kband"],
                    deformed_spin_orbit=deformed_so)
           for tj in (1, 9, 25, 41) for par in (-1, 1)]
    exact = smatrix_blocks(chs, ff, kin, h, nmatch, r, minus_identity=True)
    fast = smatrix_blocks(chs, ff, kin, h, nmatch, r, minus_identity=True, exact_bits=False)
    spin0 = float(band["spin"][0])
    for ch, (a, op), (b, _) in zip(chs, exact, fast, strict=True):
        # what a block is FOR: its cross sections and T_lj. Elements of D far below the block's
        # largest (1e-59 in a 1e-53 block at 1 keV) differ in their leading digits and matter to
        # nothing, so the S-matrix is not compared element by element, and a sub-barrier block adds
        # 1e-5 of pi/k^2 to a sum of order 1-10 and carries its own conditioning: at 9 MeV the
        # 2J = 25 block (1.4e-5) differs by 7e-8 relative between the two loops, 1e-12 absolute.
        ga = accumulate(ch, a, op, kin, spin0, 0.5, int(band["spin"].numel()), 20,
                        minus_identity=True)
        gb = accumulate(ch, b, op, kin, spin0, 0.5, int(band["spin"].numel()), 20,
                        minus_identity=True)
        for k in ("reac", "tot", "el", "direct", "tjl"):
            assert torch.allclose(ga[k], gb[k], rtol=1e-9, atol=1e-11), (ch.twoJ, ch.parity, k)


@pytest.mark.skipif(not ccnative.available(), reason="libccfast.so not built")
@pytest.mark.parametrize("deformed_so", [False, True])
def test_ccx_sweeps_and_real_products_match_the_elimination(deformed_so, monkeypatch):
    """NATIVEX2 ccx: the Jacobi sweeps in place of the elimination, the complex products as real
    ones and the split-storage derivative-coupling loop (`HF_NX2_CCX`, on by default on arm64)
    against the same kernel with them off, on U-238's blocks below and above soswitch. Off
    arm64 the switch is a no-op and the two runs are the same."""
    from physics.hf.ecis.coupling import channels
    from physics.hf.ecis.formfactor import rotational_form_factors
    from physics.hf.ecis.incident import _t4_parameters
    from physics.hf.ecis.solver import _grid_and_kinematics, accumulate, smatrix_blocks
    from physics.hf.omp.schrodinger import PARMASS_AMU, nucleus_mass_amu

    band = _band(92, 238)
    e = _grid()[5:] if deformed_so else _grid(5)
    p = _t4_parameters(92, 238, 1, e, None)
    m_t = nucleus_mass_amu(92, 238)
    kin, h, nmatch, r = _grid_and_kinematics(p, PARMASS_AMU[1], m_t, 0.0, e, band["e_mev"], 1,
                                             True)
    ff = rotational_form_factors(p, m_t, r, band["rotbeta"], band["deformation_length"],
                                 2 * band["rotbeta"].numel(), 0.0, deformed_so)
    chs = [channels(tj, par, band["spin"], band["parity"], 20, band["kband"],
                    deformed_spin_orbit=deformed_so)
           for tj in (1, 9, 25, 33, 41) for par in (-1, 1)]
    assert max(int(ch.level.numel()) for ch in chs) >= 32  # blocks the switch acts on
    monkeypatch.setenv("HF_NX2_CCX", "0")
    ref = smatrix_blocks(chs, ff, kin, h, nmatch, r, minus_identity=True, exact_bits=False)
    monkeypatch.setenv("HF_NX2_CCX", "1")
    got = smatrix_blocks(chs, ff, kin, h, nmatch, r, minus_identity=True, exact_bits=False)
    spin0 = float(band["spin"][0])
    nspin = int(band["spin"].numel())
    for ch, (a, op), (b, _) in zip(chs, ref, got, strict=True):
        ga = accumulate(ch, a, op, kin, spin0, 0.5, nspin, 20, minus_identity=True)
        gb = accumulate(ch, b, op, kin, spin0, 0.5, nspin, 20, minus_identity=True)
        for k in ("reac", "tot", "el", "direct", "tjl"):
            assert torch.allclose(ga[k], gb[k], rtol=1e-10, atol=1e-12), (ch.twoJ, ch.parity, k)
