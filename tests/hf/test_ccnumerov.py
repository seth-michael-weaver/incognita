"""CCNUMEROV: ECIS's modified Numerov in the coupled-channels radial step.

`ecist.f::inch` steps the coupled equations explicitly,

    u_{i+1} = 2 u_i - u_{i-1} + (T_i + T_i**2 / 12) u_i,   T = h**2 M,

which is 2(cosh kh - 1) truncated after two terms; the port used the plain implicit Numerov,
whose h**6 truncation has the opposite sign (-v**3/240 against +v**3/360, ecis-113/ecis-114) and
therefore does not land on ECIS's answer at ECIS's own step.  These pin the recurrence itself,
the agreement of the compiled kernels with the torch loop, that both schemes still converge to
the same solution, and that the modified one is the one closer to stock TALYS at `refine = 1`.

Task: CCNUMEROV. Acceptance test: G-CCNUMEROV (docs/results/hf-ccnumerov.md).
"""

from __future__ import annotations

import math

import pytest
import torch

from physics.hf.core.tensors import DTYPE
from physics.hf.ecis import ccnative

CD = torch.complex128

# CHART1's first three energies and its stock-TALYS `total.tot` for U-232, as tests/hf/test_fissc2
# quotes them: `total.tot` of a CC target is exactly the optical sigma_tot.
E_KEV = (0.001, 0.001684, 0.002836)
U232_TALYS_TOTAL_MB = (37621.30, 31966.20, 27604.40)


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


def _solve(Z, A, band, e_mev, modnum, monkeypatch, refine=1):
    from physics.hf.ecis import incident as I

    monkeypatch.setenv("HF_CC_MODNUM", "1" if modnum else "0")
    monkeypatch.setattr(I, "INCIDENT_REFINE", 1)  # FISSC2's halving off: this is the bare step
    I._SOLVED.clear()
    try:
        ich, _ = I.incident_coupled(None, Z, A, torch.tensor(e_mev, dtype=DTYPE), band,
                                    refine=refine)
    finally:
        I._SOLVED.clear()
    return ich


def test_the_step_is_ecis_inch_and_not_the_plain_numerov(monkeypatch):
    """`_numerov_blocks` on a constant M must reproduce `inch-155..162` to the last bit, and the
    plain scheme must not: for a constant potential the two differ at h**6 by T**3/144."""
    from physics.hf.ecis import solver

    monkeypatch.setenv("HF_CC_MODNUM", "1")
    n, n_e, n_r = 3, 1, 40
    torch.manual_seed(0)
    a = torch.randn(n, n, dtype=torch.float64)
    m0 = (a + a.T).to(CD) * 0.05 + 1j * torch.eye(n, dtype=CD) * 0.01  # symmetric, as ECIS's is
    mm = m0.expand(n_r, n_e, n, n).contiguous()
    h = torch.tensor([0.27], dtype=DTYPE)
    u1 = torch.eye(n, dtype=CD).expand(n_e, n, n).contiguous().clone()
    nmatch = torch.tensor([n_r - 3])
    keep = solver._numerov_blocks(mm, None, u1.clone(), h, nmatch)

    c = float(h[0]) ** 2 / 12.0
    t = 12.0 * c * m0                                  # T = h**2 M
    step = t + torch.matmul(t, t) / 12.0               # inch-133..147: V - V*V/12, V = -T
    up, uc = torch.zeros(n, n, dtype=CD), u1[0].clone()
    for _ in range(int(nmatch[0]) + 1):                # inch-155..162
        up, uc = uc, 2.0 * uc - up + torch.matmul(step, uc)

    # The loop stabilises the solution matrix every 10 steps (U -> U C, `solver._stabilise`), so
    # U itself is basis-dependent and U_{i+1} U_i^-1 -- what the matching radius actually reads --
    # is not.  That is what is compared.
    def ratio(a, b):
        return torch.linalg.solve(b.transpose(0, 1), a.transpose(0, 1)).transpose(0, 1)

    want = ratio(uc, up)
    got = ratio(keep["ump1"][0, 0], keep["um"][0, 0])
    assert torch.allclose(got, want, rtol=1e-8, atol=1e-10), "not ECIS's inch recurrence"

    monkeypatch.setenv("HF_CC_MODNUM", "0")
    kp = solver._numerov_blocks(mm, None, u1.clone(), h, nmatch)
    plain = ratio(kp["ump1"][0, 0], kp["um"][0, 0])
    assert not torch.allclose(plain, want, rtol=1e-6), "the plain step is a different scheme"


@pytest.mark.skipif(not ccnative.available(), reason="libccfast.so not built")
def test_the_compiled_kernels_step_what_the_torch_loop_steps(monkeypatch):
    """`ccfast.c::cc_block_mn` (and its split twin) against `solver._numerov_blocks`, below
    `soswitch` where the modified step applies.  CCFAST2 is not bit-identical by design, so this
    is the cross-section-level closeness its own gate uses."""
    from physics.hf.ecis.coupling import channels
    from physics.hf.ecis.formfactor import rotational_form_factors
    from physics.hf.ecis.incident import _t4_parameters
    from physics.hf.ecis.solver import _grid_and_kinematics, accumulate, smatrix_blocks
    from physics.hf.omp.schrodinger import PARMASS_AMU, nucleus_mass_amu

    monkeypatch.setenv("HF_CC_MODNUM", "1")
    band = _band(92, 238)
    e = torch.tensor([1.0e-3, 0.3, 1.5, 4.0], dtype=DTYPE)
    p = _t4_parameters(92, 238, 1, e, None)
    m_t = nucleus_mass_amu(92, 238)
    kin, h, nmatch, r = _grid_and_kinematics(p, PARMASS_AMU[1], m_t, 0.0, e, band["e_mev"], 1, True)
    ff = rotational_form_factors(p, m_t, r, band["rotbeta"], band["deformation_length"],
                                 2 * band["rotbeta"].numel(), 0.0, False)
    chs = [channels(tj, par, band["spin"], band["parity"], 20, band["kband"],
                    deformed_spin_orbit=False)
           for tj in (1, 9, 25) for par in (-1, 1)]
    exact = smatrix_blocks(chs, ff, kin, h, nmatch, r, minus_identity=True)
    fast = smatrix_blocks(chs, ff, kin, h, nmatch, r, minus_identity=True, exact_bits=False)
    spin0 = float(band["spin"][0])
    for ch, (a, op), (b, _) in zip(chs, exact, fast, strict=True):
        ga = accumulate(ch, a, op, kin, spin0, 0.5, int(band["spin"].numel()), 20,
                        minus_identity=True)
        gb = accumulate(ch, b, op, kin, spin0, 0.5, int(band["spin"].numel()), 20,
                        minus_identity=True)
        for k in ("reac", "tot", "el", "direct", "tjl"):
            assert torch.allclose(ga[k], gb[k], rtol=1e-9, atol=1e-11), (ch.twoJ, ch.parity, k)


def test_both_schemes_converge_to_the_same_solution(monkeypatch):
    """They are two truncations of the same series, so refining the step must close the gap: the
    change is a discretisation, not a different set of equations."""
    band = _band(92, 232)
    e = (0.001, 0.008044)
    coarse = [abs(float(_solve(92, 232, band, e, mn, monkeypatch).sigma_tot_mb[i]))
              for mn in (0, 1) for i in range(len(e))]
    fine = [abs(float(_solve(92, 232, band, e, mn, monkeypatch, refine=4).sigma_tot_mb[i]))
            for mn in (0, 1) for i in range(len(e))]
    for i in range(len(e)):
        d_coarse = abs(coarse[i] / coarse[i + len(e)] - 1.0)
        d_fine = abs(fine[i] / fine[i + len(e)] - 1.0)
        assert d_fine < d_coarse / 10.0, f"E={e[i]}: {d_fine:.2e} not well inside {d_coarse:.2e}"
        assert d_fine < 1.0e-5


def test_the_modified_step_is_the_one_closer_to_talys(monkeypatch):
    """The inverse of FISSC2's own property, and the reason its step-halving is off by default:
    on ECIS's own grid the modified scheme, not the plain one, sits near stock TALYS."""
    band = _band(92, 232)
    off = _solve(92, 232, band, E_KEV, False, monkeypatch)
    on = _solve(92, 232, band, E_KEV, True, monkeypatch)
    for i, t in enumerate(U232_TALYS_TOTAL_MB):
        r_off = abs(math.log(float(off.sigma_tot_mb[i]) / t))
        r_on = abs(math.log(float(on.sigma_tot_mb[i]) / t))
        assert r_off > 1.0e-3, f"E={E_KEV[i]}: the plain Numerov's defect should be there"
        assert r_on < r_off / 2.0, f"E={E_KEV[i]}: {r_on:.2e} not well inside {r_off:.2e}"
        assert r_on < 1.0e-3
