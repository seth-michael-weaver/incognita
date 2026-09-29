"""T8: pre-equilibrium (two-component exciton model, complex particles, spin, multiple preeq).

Gate A-pe (physics/hf/CONTRACT.md §6, docs/results/hf-engine-gates.md): p95 |ln(port/TALYS)|
<= 0.02 against the `exciton` and `preequilibrium` dump families. Tests that need the dumps
skip when they are absent.
"""

from __future__ import annotations

import math

import numpy as np
import pytest
import torch

from physics.hf import reference as ref
from physics.hf.core.constants import talys_constants
from physics.hf.core.tensors import DTYPE
from physics.hf.density.particle_hole import (
    EFERMI_MEV,
    apauli,
    apauli2,
    factorial,
    finitewell,
    ncomb,
    phdens,
    phdens2,
    preeqpair,
)
from physics.hf.input.defaults import default_options, default_params
from physics.hf.preeq.exciton import (
    exciton_states,
    matrix_elements,
    surface_well_depth,
)
from physics.hf.preeq.score import TOLERANCE, score_target
from physics.hf.preeq.spin import MAXJPH, preeq_spin_distribution

pytestmark = pytest.mark.filterwarnings("ignore::DeprecationWarning")

GATE_TARGETS = ("Fe056", "Ni058", "Zr090", "Nb093", "Sn120", "Pb208")


def _t(x):
    return torch.tensor(x, dtype=DTYPE)


def _i(x):
    return torch.tensor(x, dtype=torch.int64)


# ----------------------------------------------------------------- particle-hole densities


def test_factorial_and_ncomb_match_talys_tables():
    assert float(factorial(_i(6))) == 720.0
    assert ncomb(5, 2) == 10.0
    assert ncomb(4, 0) == 1.0
    assert ncomb(3, 5) == 0.0


def test_apauli_matches_the_closed_form():
    gs = _t(57.0 / 15.0)
    for p, h in ((1, 0), (2, 1), (3, 3)):
        want = max(p, h) ** 2 / float(gs) - (p * p + h * h + p + h) / (4.0 * float(gs))
        assert float(apauli(_i(p), _i(h), gs)) == pytest.approx(want, rel=1e-12)
    assert float(apauli(_i(-1), _i(2), gs)) == 0.0


def test_apauli2_is_the_sum_of_the_two_components():
    gsp, gsn = _t(26.0 / 15.0), _t(31.0 / 15.0)
    ppi, hpi, pnu, hnu = 2, 2, 1, 0
    want = (
        max(ppi, hpi) ** 2 / float(gsp)
        + max(pnu, hnu) ** 2 / float(gsn)
        - (ppi**2 + hpi**2 + ppi + hpi) / (4.0 * float(gsp))
        - (pnu**2 + hnu**2 + pnu + hnu) / (4.0 * float(gsn))
    )
    got = apauli2(_i(ppi), _i(hpi), _i(pnu), _i(hnu), gsp, gsn)
    assert float(got) == pytest.approx(want, rel=1e-12)
    assert float(apauli2(_i(-1), _i(0), _i(1), _i(0), gsp, gsn)) == 0.0


def test_finitewell_is_one_below_the_well_and_for_a_single_hole():
    p, h = _i(1), _i(1)
    assert float(finitewell(p, h, _t(10.0), _t(38.0))) == 1.0
    assert float(finitewell(_i(1), _i(0), _t(50.0), _t(38.0))) == 1.0  # h = 1, n = 1


def test_finitewell_reduces_the_density_above_the_well():
    f = float(finitewell(_i(2), _i(2), _t(90.0), _t(38.0)))
    assert 0.0 < f < 1.0


def test_finitewell_surface_hole_vanishes_above_116_percent_of_efermi():
    got = finitewell(_i(0), _i(1), _t(1.17 * EFERMI_MEV), _t(12.0), True)
    assert float(got) == 0.0


def test_finitewell_matches_the_pre_vectorisation_capture():
    """SPEED2 evaluates finitewell's sums over k and over the nine well depths as array axes.
    The fixture holds 56 calls captured from the golden speed harness (scripts/hf_speed_bench.py,
    one per argument signature, surface branch on and off) and 24 synthetic ones (scalar and
    broadcast exciton numbers, masked `surfwell`), all computed BEFORE that change.
    Bit-identical on the capture machine; rel <= 1e-12 here (pow/exp are libm-dependent)."""
    from pathlib import Path

    z = np.load(Path(__file__).parent / "fixtures" / "finitewell_speed2.npz")
    for j in range(int(z["n"])):
        surf = z[f"c{j}_surf"]
        surf = bool(surf) if bool(z[f"c{j}_surf_is_bool"]) else torch.from_numpy(surf)
        got = finitewell(
            torch.from_numpy(z[f"c{j}_p"]),
            torch.from_numpy(z[f"c{j}_h"]),
            torch.from_numpy(z[f"c{j}_eex"]),
            torch.from_numpy(z[f"c{j}_ewell"]),
            surf,
        ).numpy()
        ref = z[f"c{j}_out"]
        assert got.shape == ref.shape, j
        den = np.maximum(np.abs(ref), np.abs(got))
        # COREX: off the graph the k-sum runs in numpy (particle_hole._sum_terms_np); where the
        # alternating sum cancels to ~1e-16 only an absolute tolerance is meaningful
        rel = np.abs(ref - got) / np.where(den > 1e-12, den, 1.0)
        assert rel.max(initial=0.0) <= 1e-12, (j, rel.max())


def test_phdens2_is_the_two_component_closed_form():
    gsp, gsn = _t(26.0 / 15.0), _t(31.0 / 15.0)
    ppi, hpi, pnu, hnu, ex = 1, 1, 2, 1, 20.0
    ap = apauli2(_i(ppi), _i(hpi), _i(pnu), _i(hnu), gsp, gsn)
    n1 = ppi + hpi + pnu + hnu - 1
    want = (
        float(gsp) ** (ppi + hpi)
        * float(gsn) ** (pnu + hnu)
        / (
            math.factorial(ppi)
            * math.factorial(hpi)
            * math.factorial(pnu)
            * math.factorial(hnu)
            * math.factorial(n1)
        )
        * (ex - float(ap)) ** n1
    )
    got = phdens2(_i(ppi), _i(hpi), _i(pnu), _i(hnu), gsp, gsn, _t(ex), _t(EFERMI_MEV))
    assert float(got) == pytest.approx(want, rel=1e-12)


def test_phdens2_vanishes_below_the_pauli_limit_and_for_negative_indices():
    gsp, gsn = _t(1.7), _t(2.1)
    assert float(phdens2(_i(2), _i(2), _i(2), _i(2), gsp, gsn, _t(0.5), _t(EFERMI_MEV))) == 0.0
    assert float(phdens2(_i(-1), _i(0), _i(1), _i(0), gsp, gsn, _t(20.0), _t(EFERMI_MEV))) == 0.0


def test_phdens_one_component_matches_its_closed_form():
    gs = _t(57.0 / 15.0)
    p, h, ex = 2, 1, 15.0
    ap = apauli(_i(p), _i(h), gs)
    want = float(gs) ** 3 / (2 * 1 * 2) * (ex - float(ap)) ** 2
    got = phdens(_i(p), _i(h), gs, _t(ex), _t(EFERMI_MEV), ap)
    assert float(got) == pytest.approx(want, rel=1e-12)


def test_phdens2_rejects_the_unported_table_model():
    with pytest.raises(NotImplementedError):
        phdens2(_i(1), _i(1), _i(1), _i(1), _t(1.7), _t(2.1), _t(10.0), _t(38.0), phmodel=2)


def test_preeqpair_default_model_returns_the_ground_state_pairing():
    pair = _t(1.5894)
    got = preeqpair(pair, _t(3.8), _i(3), _t(20.0), pairmodel=2)
    assert float(got) == pytest.approx(1.5894)
    assert float(preeqpair(_t(0.0), _t(3.8), _i(3), _t(20.0), pairmodel=2)) == 0.0


def test_preeqpair_fu_model_reduces_the_gap_at_high_energy():
    pair = _t(1.5894)
    low = float(preeqpair(pair, _t(3.8), _i(3), _t(1.0), pairmodel=1))
    high = float(preeqpair(pair, _t(3.8), _i(3), _t(30.0), pairmodel=1))
    assert low == pytest.approx(1.5894)  # below the Fu threshold the gap is untouched
    assert high < low


# ----------------------------------------------------------------- exciton bookkeeping


def test_exciton_states_follow_talys_order_for_a_neutron_projectile():
    st = exciton_states(1, 6)
    assert st.size == 21
    assert (st.ppi0, st.hpi0, st.pnu0, st.hnu0, st.p0) == (0, 0, 1, 0, 1)
    first = [(int(st.ppi[i]), int(st.hpi[i]), int(st.pnu[i]), int(st.hnu[i])) for i in range(6)]
    assert first == [
        (0, 0, 1, 0),
        (0, 0, 2, 1),
        (1, 1, 1, 0),
        (0, 0, 3, 2),
        (1, 1, 2, 1),
        (2, 2, 1, 0),
    ]
    assert (st.h == st.hpi + st.hnu).all()
    assert (st.n == st.p + st.h).all()


def test_surface_well_depth_matches_the_kalbach_parameterisation():
    a = 57
    e = _t([1.0, 14.0])
    got = surface_well_depth(1, e, a).numpy()
    third = talys_constants()["onethird"]
    want = [12.0 + 26.0 * x**4 / (x**4 + (245.0 / a**third) ** 4) for x in (1.0, 14.0)]
    assert got == pytest.approx(want, rel=1e-12)
    assert surface_well_depth(2, e, a)[0] > 22.0  # protons start from 22 MeV


def test_matrix_element_ratios_follow_the_r_keywords():
    o = default_options(26, 56)
    p = default_params(26, 56, o)
    m2 = matrix_elements(57, _i([1, 3]), _t([21.4]), o, p)
    assert float(m2["M2nunu"][0, 0] / m2["M2pipi"][0, 0]) == pytest.approx(1.5)
    assert float(m2["M2pinu"][0, 0] / m2["M2pipi"][0, 0]) == pytest.approx(1.0)
    # M2 falls with the exciton number through Ecomp/(n*aproj)
    assert float(m2["M2pipi"][0, 1]) > float(m2["M2pipi"][0, 0])


def test_matrix_element_is_differentiable_in_m2constant():
    o = default_options(26, 56)
    p = default_params(26, 56, o).requires_grad_(["m2constant"])
    m2 = matrix_elements(57, _i([1]), _t([21.4]), o, p)
    m2["M2pipi"].sum().backward()
    g = p.values["m2constant"].grad
    assert g is not None and float(g) > 0.0


def test_spin_distribution_normalises_and_shrinks_with_a():
    o = default_options(26, 56)
    p = default_params(26, 56, o)
    r = preeq_spin_distribution(o, p, 56)
    assert r["RnJ"].shape[1] == MAXJPH + 1
    assert float(r["RnJ"][0].sum()) == 0.0  # n = 0 is unused, as in TALYS
    for n in (1, 4, 8):
        assert float(r["RnJsum"][n]) > 0.0
    # a wider spin cutoff at larger n pushes the distribution to higher J
    mean = lambda n: float((torch.arange(MAXJPH + 1) * r["RnJ"][n]).sum() / r["RnJ"][n].sum())  # noqa: E731
    assert mean(8) > mean(1)


def test_spin_distribution_rejects_the_unported_wigner_model():
    o = default_options(26, 56, overrides={"preeqspin": 4})
    p = default_params(26, 56, o)
    with pytest.raises(NotImplementedError):
        preeq_spin_distribution(o, p, 56)


# ----------------------------------------------------------------- A-pe gate


@pytest.mark.skipif(not ref.available("exciton"), reason="reference dumps not parsed")
@pytest.mark.parametrize("target", GATE_TARGETS)
def test_a_pe_gate(target):
    rec = score_target(target)
    assert rec["quantities"], f"{target}: nothing scored"
    bad = {k: v for k, v in rec["quantities"].items() if v.get("n") and v["p95"] > TOLERANCE}
    assert not bad, f"{target} A-pe p95 above {TOLERANCE}: {bad}"


@pytest.mark.skipif(not ref.available("exciton"), reason="reference dumps not parsed")
def test_a_pe_reports_every_dumped_quantity():
    rec = score_target("Fe056")
    for q in (
        "matrix element",
        "emission rate",
        "escape width",
        "internal transition rate",
        "damping width",
        "total width",
        "lifetime",
        "spectrum Total",
        "spectrum Exciton model",
        "spectrum per stage",
        "total cross section",
    ):
        assert rec["quantities"].get(q, {}).get("n"), f"{q} not scored"


@pytest.mark.skipif(not ref.available("exciton"), reason="reference dumps not parsed")
def test_preequilibrium_conserves_flux():
    """`preeqtotal` never lets the pre-equilibrium sum exceed the available flux."""
    import torch as _torch

    from physics.hf.input.nuclides import coulomb_barriers
    from physics.hf.preeq.exciton import preequilibrium
    from physics.hf.preeq.prepare import prepare

    inp, hdr = prepare("Fe056")
    inc = ref.incident_scalars("Fe056")
    reac = {round(float(r.e_inc_mev), 6): float(r.sigma_reac_omp_mb) for _, r in inc.iterrows()}
    xsr = _torch.tensor([reac[round(e, 6)] for e in hdr["energies"]], dtype=DTYPE)
    res = preequilibrium(
        inp,
        hdr["options"],
        hdr["params"],
        hdr["discrete"],
        coulbar_mev=coulomb_barriers(hdr["options"]),
        xsreacinc_mb=xsr,
    )
    total = res["xspreeqsum"] + res["xspreeqdiscsum"]
    assert bool((total <= inp.xsflux_mb * (1.0 + 1e-9)).all())
    assert bool((res["xspreeq"] >= 0).all())
    assert np.isfinite(res["xspreeq"].numpy()).all()
