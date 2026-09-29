"""T9 compound: Hauser-Feshbach core and Moldauer WFC (physics/hf/compound).

Synthetic tests run everywhere. The acceptance gates A-cn1 / A-cn2 need the instrumented reference
(`physics/hf/compound/cn_reference.py`, parsed into features/hf_compound_reference/) and skip, not
fail, when it is absent (contract §6).
"""

from __future__ import annotations

import json
import math
import os
import tarfile
from pathlib import Path

import numpy as np
import pytest
import torch

from physics.hf.compound import wfc
from physics.hf.compound.prepare import (
    NUMJ,
    CompoundInputs,
    ResidualChannels,
    exit_channel_sums,
    incident_channels,
)
from physics.hf.compound.target import (
    binary_cross_sections,
    compound_target,
    compound_target_inputs,
)
from physics.hf.core.tensors import DTYPE

ROOT = Path(__file__).resolve().parents[2]
REF = Path(
    os.environ.get("INCOGNITA_HF_COMPOUND_REFERENCE", ROOT / "features" / "hf_compound_reference")
)


def _toy(wmode: int = 0, flagwidth: bool = True) -> CompoundInputs:
    """Even-even target (0+), neutron in; one discrete level + 3 continuum bins in the residual,
    one gamma level + 2 bins in the compound nucleus. Small but exercises every selection rule."""
    nex_n, nex_g = 4, 3
    rho_n = np.zeros((nex_n, NUMJ + 1, 2))
    rho_n[0, 0, 1] = 1.0  # ground state 0+
    rho_n[1:, :6, :] = (
        np.linspace(1, 3, 6)[None, :, None] * np.array([1.0, 2.0, 4.0])[:, None, None]
    )
    rho_g = np.zeros((nex_g, NUMJ + 1, 2))
    rho_g[0, 0, 0] = 1.0  # 1/2- level stored at Ir = 0 (odd A)
    rho_g[1:, :6, :] = 5.0
    tjl = np.zeros((nex_n, 4, 3))
    for n in range(nex_n):
        for l in range(4):
            tjl[n, l, 0] = tjl[n, l, 2] = 0.3 * np.exp(-0.7 * l) * (1.0 - 0.15 * n)
    tjl[0, 0, 0] = 0.0
    tg = np.zeros((nex_g, 3, 2, NUMJ + 1, 2))
    tg[:, 1, 1] = 2e-3
    tg[:, 1, 0] = 4e-4
    tg[:, 2, 1] = 5e-5
    residuals = {
        0: ResidualChannels(
            0,
            0,
            0,
            nex_g - 1,
            0,
            1,
            0,
            np.array([2] * nex_g),
            np.array([5] * nex_g),
            np.zeros(nex_g),
            np.array([-1, 0, 0]),
            np.array([1, -1, -1]),
            rho_g,
            tgam=tg,
        ),
        1: ResidualChannels(
            1,
            0,
            1,
            nex_n - 1,
            0,
            1,
            1,
            np.array([3] * nex_n),
            np.array([5] * nex_n),
            np.zeros(nex_n),
            np.array([1, 0, 0, 0]),
            np.array([0, -1, -1, -1]),
            rho_n,
            tjl=tjl,
        ),
    }
    return CompoundInputs(
        e_inc_mev=1.0,
        cnfactor_mb=100.0,
        xsflux_mb=0.0,
        xsreacinc_mb=0.0,
        j2beg=1,
        j2end=7,
        targetspin2=0,
        target_parity=1,
        lmaxinc=3,
        k0=1,
        ltarget=0,
        wmode=wmode,
        wfcfactor=1,
        gammax=2,
        nfisbar=0,
        flagwidth=flagwidth,
        flagfission=False,
        tjlinc=tjl[0, :4].copy(),
        residuals=residuals,
    )


def test_gauss_laguerre_weights_are_stored_as_square_roots():
    x, w = wfc.gauss_laguerre()
    # squared weights integrate exp(-x) x^k exactly: sum w^2 x^k = k!
    for k in range(6):
        assert float((w**2 * x**k).sum()) == pytest.approx(float(math.factorial(k)), rel=1e-5)


def test_hauser_feshbach_conserves_flux_without_wfc():
    """With W = 1, each (J, P) block distributes CN (2J+1) * sum_a T_a over all exit channels
    exactly once: total population = sum over blocks of CNterm."""
    inp = _toy(wmode=0)
    pop = compound_target_inputs(inp).pop_mb[0]
    cnterm = 0.0
    for parity in (-1, 1):
        for J2 in range(inp.j2beg, inp.j2end + 1, 2):
            if float(exit_channel_sums(inp, J2, parity)["denom"]) > 0:
                cnterm += inp.cnfactor_mb * (J2 + 1) * incident_channels(inp, J2, parity)[1].sum()
    assert float(pop.sum()) == pytest.approx(cnterm, rel=1e-12)


def test_moldauer_conserves_flux_and_enhances_elastic():
    """Moldauer's W is normalised so that sum_b T_b W(a,b) = T_a st-weighted (flux check printed by
    comptarget); the defining physics is that compound elastic grows relative to no-WFC."""
    p0 = compound_target_inputs(_toy(wmode=0)).pop_mb[0]
    p1 = compound_target_inputs(_toy(wmode=1)).pop_mb[0]
    assert float(p1.sum()) == pytest.approx(float(p0.sum()), rel=0.02)
    assert float(p1[1, 0].sum()) > float(p0[1, 0].sum()) * 1.01


def test_scalar_moldauer_matches_the_factorised_sums():
    torch.manual_seed(0)
    x, w = wfc.gauss_laguerre()
    tinc = torch.rand(3, dtype=DTYPE) * 0.5
    tex = torch.rand(20, dtype=DTYPE) * 0.5
    rho = torch.rand(20, dtype=DTYPE) * 3 + 0.5
    st = (rho * tex).sum() + 0.2
    tall = torch.cat([tinc, tex])
    deg = torch.cat([torch.ones(3, dtype=DTYPE), rho])
    opts = {"ninc": 3, "st": st, "tgamma": torch.tensor(0.2, dtype=DTYPE)}
    a = torch.arange(3).repeat_interleave(20)
    b = (torch.arange(20) + 3).repeat(3)
    W = wfc.moldauer(tall, deg, x, w, a, b, opts).reshape(3, 20)
    nu = wfc.degrees_of_freedom(tall, st)
    prod = wfc.moldauer_product(x, w, st, tex, rho, nu[3:], torch.tensor(0.2, dtype=DTYPE))
    gb, gg, _ = wfc.moldauer_sums(x, prod, st, tinc, nu[:3], tex, nu[3:])
    assert torch.allclose((tinc[:, None] * W).sum(0), gb, rtol=1e-12)


def test_population_is_differentiable_in_transmission_and_level_density():
    inp = _toy(wmode=1)
    r = inp.residuals[1]
    rho = torch.as_tensor(r.rho, dtype=DTYPE).requires_grad_(True)
    tjl = torch.as_tensor(r.tjl, dtype=DTYPE).requires_grad_(True)
    r.rho, r.tjl = rho, tjl  # tensors pass straight through torch.as_tensor
    out = compound_target_inputs(inp).pop_mb[0, 0].sum()  # capture
    out.backward()
    assert torch.isfinite(rho.grad).all() and torch.isfinite(tjl.grad).all()
    assert float(tjl.grad.abs().sum()) > 0


def test_batched_entry_point_pads_cases():
    a, b = _toy(0), _toy(1)
    bp = compound_target([a, b])
    assert bp.pop_mb.shape[0] == 2
    xs = binary_cross_sections(bp, [a, b])
    assert xs.shape == (2, 7) and torch.isfinite(xs).all()


# ------------------------------------------------------------------------------------------------
# acceptance gates against the instrumented TALYS reference
# ------------------------------------------------------------------------------------------------


def _runs(variant: str):
    return sorted(REF.glob(f"{variant}__*.tar.gz"))


def _cases(tar: Path, tmp: Path):
    from physics.hf.compound.prepare import load_cn_dump

    with tarfile.open(tar) as tf:
        m = next(x for x in tf.getmembers() if x.name.endswith("cn_inputs.txt"))
        tf.extract(m, tmp, filter="data")
    return load_cn_dump(tmp / m.name)


@pytest.mark.parametrize("variant,tol", [("wfc_off", 0.01), ("default", 0.02)])
def test_gate_compound_population_matches_talys_xspop(variant, tol, tmp_path):
    runs = _runs(variant)
    if not runs:
        pytest.skip(f"no instrumented {variant} reference in {REF}")
    rs = []
    for tar in runs:
        for c in _cases(tar, tmp_path):
            pop = compound_target_inputs(c).pop_mb[0].numpy()
            for t, ref in c.ref_pop_mb.items():
                p = pop[t, : ref.shape[0]]
                live = ref >= 1e-6
                rs.append(np.abs(np.log(np.maximum(p[live], 1e-300) / ref[live])))
                assert not ((ref < 1e-6) & (p >= 1e-6)).any()
    r = np.concatenate(rs)
    assert np.percentile(r, 95) <= tol, (np.percentile(r, 95), r.max())


# ------------------------------------------------------------------------------------------------
# continuum decay (compound.f90) and normalisation (compnorm.f90)
# ------------------------------------------------------------------------------------------------


def _toy_multi(fullhf: bool = False, fission: bool = False) -> "MultiInputs":  # noqa: F821 (imported in the body)
    """Even-A compound nucleus decaying from bin nex = 5 into a neutron and a gamma daughter."""
    from physics.hf.compound.continuum import MultiInputs

    nex_n, nex_g = 4, 3
    rho_n = np.zeros((nex_n, NUMJ + 1, 2))
    rho_n[0, 1, 1] = 1.0  # ground state 1+ (stored at Ir = 1)
    rho_n[1:, :6, :] = np.linspace(1.0, 3.0, 6)[None, :, None]
    rho_g = np.zeros((nex_g, NUMJ + 1, 2))
    rho_g[0, 0, 1] = 1.0
    rho_g[1:, :6, :] = 4.0
    tjl = np.zeros((nex_n, 5, 3))
    tl = np.zeros((nex_n, 5))
    for n in range(nex_n):
        for l in range(5):
            t = 0.25 * np.exp(-0.6 * l) * (1.0 - 0.1 * n)
            tjl[n, l, 0] = tjl[n, l, 2] = t
            tl[n, l] = t  # (2s+1) Tl == sum over j of Tjl for equal spin-orbit halves
    tg = np.zeros((nex_g, 3, 2, NUMJ + 1, 2))
    tg[:, 1, 1] = 3e-3
    tg[:, 1, 0] = 6e-4
    tg[:, 2, 1] = 7e-5
    res = {
        0: ResidualChannels(0, 0, 0, nex_g - 1, 0, 1, 0, np.array([2] * nex_g),
                            np.array([5] * nex_g), np.zeros(nex_g), np.array([1, 0, 0]),
                            np.array([0, -1, -1]), rho_g, tgam=tg),
        1: ResidualChannels(1, 0, 1, nex_n - 1, 0, 1, 1, np.array([4] * nex_n),
                            np.array([5] * nex_n), np.zeros(nex_n), np.array([1, 0, 0, 0]),
                            np.array([2, -1, -1, -1]), rho_n, tjl=tjl),
    }
    res[1].tl = tl
    pop = np.zeros((NUMJ + 1, 2))
    pop[:5, :] = 10.0
    mi = MultiInputs(
        zcomp=0, ncomp=0, nex=5, odd=0, e_inc_mev=8.0, ex_inc_mev=6.0, dex_inc_mev=0.5,
        exmax_mev=8.0, popeps_mb=1e-6, dmulti=0.1, flagfullhf=fullhf, maxj_mother=4, gammax=2,
        nlast_mother=3, nfisbar=1 if fission else 0, numj=NUMJ, flagfission=fission,
        xspop_mother_mb=pop, residuals=res,
    )
    if fission:
        for parity in (-1, 1):
            for J in range(5):
                mi.tfis[(2 * J, parity)] = (0.02, 0.03, 0.045)
    return mi


def test_discrete_levels_ignore_a_stale_opposite_parity_rho0():
    """compound.f90:243-246 pins a discrete level to ONE parity, `parlev`.

    `rho0` is a scratch array TALYS refills per residual without clearing, so a level's own `Ir`
    row can still hold a non-zero value at the opposite parity left over from an earlier nucleus
    or mother bin. TALYS never reads it. A mask on `Ir` alone does, and adds a phantom exit
    channel -- in the Fe-56 multi dump that inflated denomhf by up to 55%.
    """
    from physics.hf.compound.continuum import compound_decay

    clean = compound_decay(_toy_multi())
    mi = _toy_multi()
    # neutron ground state: 1+, so Ir = 1 at parity index 1. Plant scratch at (Ir = 1, parity -1).
    assert mi.residuals[1].parlev[0] == 1 and mi.residuals[1].jdis2[0] // 2 == 1
    mi.residuals[1].rho[0, 1, 0] = 0.7
    dirty = compound_decay(mi)
    for t in clean.dpop_mb:
        assert torch.allclose(dirty.dpop_mb[t], clean.dpop_mb[t], rtol=0, atol=0)
    for k in clean.denom:
        assert float(dirty.denom[k]) == float(clean.denom[k])


def test_dump_fields_survive_a_negative_value_abutting_its_neighbour():
    """`es17.9e3` fills all 17 columns when the value is negative, so it runs into the previous
    field. Pb-208's TYPE line does exactly this (S(0,0,type) = -2.2485 MeV for one ejectile) and
    a plain `.split()` silently drops a column."""
    from physics.hf.compound.prepare import _split_dump_fields

    assert _split_dump_fields(" 0.000000000E+000-2.248526176E+000") == [
        "0.000000000E+000", "-2.248526176E+000"]
    # an exponent's own sign must NOT be treated as a separator
    assert _split_dump_fields(" 5.000000000E-001 1.119705834E+001") == [
        "5.000000000E-001", "1.119705834E+001"]
    assert _split_dump_fields("     82   126    -1     0") == ["82", "126", "-1", "0"]


def test_multi_dump_drops_channels_with_no_open_bin(tmp_path):
    """multiple.f90 dumps a TYPE line for every non-skipped particle, but `nexmax = -1` means the
    channel has no open bin at this mother excitation (compound.f90:235 never enters the loop).
    The loader must drop it rather than allocate a zero-row residual."""
    from physics.hf.compound.continuum import load_cn_multi_dump

    txt = tmp_path / "cn_multi.txt"
    txt.write_text(
        "MBIN      0     1     5     0 8.0E+000 6.0E+000 5.0E-001 8.0E+000 1.0E-006 1.0E-001 F\n"
        "MINT      4     2     3     0    40 F\n"
        "MPOP      0     1 1.0000000000000000E+001\n"
        "TYPE      0     0     0     2     0     0 0.0E+000 0.0E+000\n"
        "NEX       0     0     2     5 0.0E+000 0.0E+000 0.0E+000\n"
        "LEV       0     0     1\n"
        "RHO       0     0     0     1 1.0000000000000000E+000\n"
        "TYPE      1     0     1    -1     0     1 5.0E-001 0.0E+000\n"
        "MJP       0     1 1.0000000000000000E+000\n"
        "MEND      0     1     5\n"
    )
    cases = load_cn_multi_dump(txt)
    assert len(cases) == 1
    assert sorted(cases[0].residuals) == [0], "the closed neutron channel must not be kept"


def test_continuum_decay_conserves_the_mother_flux():
    """compound.f90 hands every daughter feed * enumhf and the widths sum to denomhf, so the total
    handed down is exactly (1 - Dmulti) * population of the mother bin."""
    from physics.hf.compound.continuum import compound_decay

    mi = _toy_multi()
    f = compound_decay(mi)
    handed = sum(float(v.sum()) for v in f.dpop_mb.values()) + float(f.fisfeed_mb)
    decayed = 10.0 * 2 * (mi.maxj_mother + 1)  # every (J, P) block is above popepsB here
    assert handed == pytest.approx((1.0 - mi.dmulti) * decayed, rel=1e-12)


def test_continuum_decay_with_fission_splits_the_same_flux():
    from physics.hf.compound.continuum import compound_decay, fission_width

    f = compound_decay(_toy_multi(fission=True))
    mi = _toy_multi(fission=True)
    handed = sum(float(v.sum()) for v in f.dpop_mb.values()) + float(f.fisfeed_mb)
    assert handed == pytest.approx(0.9 * 10.0 * 2 * (mi.maxj_mother + 1), rel=1e-12)
    assert float(f.fisfeed_mb) > 0
    # the logarithmic integration lies between the bin's lowest and highest transmission
    w = float(fission_width(mi, 4, 1))
    assert 0.02 < w < 0.045


def test_continuum_averaged_and_full_spin_paths_both_run_and_differ_only_in_j_coupling():
    from physics.hf.compound.continuum import compound_decay

    a = compound_decay(_toy_multi(fullhf=False))
    b = compound_decay(_toy_multi(fullhf=True))
    ta, tb = sum(float(v.sum()) for v in a.dpop_mb.values()), sum(
        float(v.sum()) for v in b.dpop_mb.values())
    assert ta == pytest.approx(tb, rel=1e-12)  # both normalise to the same mother flux
    assert not torch.allclose(a.dpop_mb[1], b.dpop_mb[1])  # but share it out differently


def test_continuum_decay_is_differentiable_in_transmission_and_level_density():
    from physics.hf.compound.continuum import compound_decay

    mi = _toy_multi()
    r = mi.residuals[1]
    rho = torch.as_tensor(r.rho, dtype=DTYPE).requires_grad_(True)
    tl = torch.as_tensor(r.tl, dtype=DTYPE).requires_grad_(True)
    r.rho, r.tl = rho, tl
    compound_decay(mi).dpop_mb[0].sum().backward()
    assert torch.isfinite(rho.grad).all() and torch.isfinite(tl.grad).all()
    assert float(tl.grad.abs().sum()) > 0


def test_compnorm_identity_cnfactor_times_transmission_sum_is_the_compound_flux():
    """compnorm folds cfratio/norm into CNfactor, which reduces to CNfactor = xsflux / sum_{J,P,j,l}
    (2J+1) Tjlinc. Every term is in the dump, so this is a gate that needs no wave number."""
    from physics.hf.compound.normalization import compound_formation, reaction_transmission_sum

    torch.manual_seed(3)
    t = torch.rand(6, 3, dtype=DTYPE) * 0.4
    cf = compound_formation(
        t, torch.tensor(0.21, dtype=DTYPE), 0, 1, 5, 1,
        torch.tensor(1234.0, dtype=DTYPE), torch.tensor(56.0, dtype=DTYPE),
        torch.tensor(78.0, dtype=DTYPE), torch.tensor(0.0, dtype=DTYPE),
    )
    s, j2beg, j2end = reaction_transmission_sum(t, 0, 1, 5, 1)
    assert (j2beg, j2end) == (cf.j2beg, cf.j2end) == (1, 11)
    assert float(cf.cn_factor_mb * s.sum()) == pytest.approx(float(cf.xs_flux_mb), rel=1e-12)


def test_compnorm_matches_the_instrumented_dump(tmp_path):
    """The same identity against TALYS's own CNfactor, xsflux and Tjlinc."""
    runs = _runs("wfc_off") + _runs("default")
    if not runs:
        pytest.skip(f"no instrumented reference in {REF}")
    from physics.hf.compound.normalization import reaction_transmission_sum

    worst = 0.0
    for tar in runs:
        for c in _cases(tar, tmp_path):
            if c.xsflux_mb == 0.0:
                continue
            s, j2beg, j2end = reaction_transmission_sum(
                torch.as_tensor(c.tjlinc, dtype=DTYPE), c.targetspin2, c.target_parity,
                c.lmaxinc, c.k0,
            )
            assert (j2beg, j2end) == (c.j2beg, c.j2end)
            got = float(torch.as_tensor(c.cnfactor_mb, dtype=DTYPE) * s.sum())
            worst = max(worst, abs(got - c.xsflux_mb) / max(c.xsflux_mb, 1e-30))
    assert worst < 1e-5, worst


def test_hrtw_runs_conserves_flux_to_its_own_accuracy_and_enhances_elastic():
    """widthmode 2. HRTW is an approximation to the same integral, so it does not conserve flux
    exactly the way Moldauer's normalisation does; it must stay close and still enhance elastic."""
    p0 = compound_target_inputs(_toy(wmode=0)).pop_mb[0]
    p2 = compound_target_inputs(_toy(wmode=2)).pop_mb[0]
    assert float(p2.sum()) == pytest.approx(float(p0.sum()), rel=0.02)
    assert float(p2[1, 0].sum()) > float(p0[1, 0].sum()) * 1.01


def test_scalar_hrtw_matches_the_factorised_sums():
    torch.manual_seed(1)
    tinc = torch.rand(3, dtype=DTYPE) * 0.5 + 0.05
    tex = torch.rand(12, dtype=DTYPE) * 0.5 + 0.05
    rho = torch.rand(12, dtype=DTYPE) * 3 + 0.5
    tg = torch.tensor(0.2, dtype=DTYPE)
    st = (rho * tex).sum() + tg
    tall = torch.cat([tinc, tex])
    deg = torch.cat([torch.ones(3, dtype=DTYPE), rho])
    opts = {"ninc": 3, "st": st, "tgamma": tg}
    a = torch.arange(3).repeat_interleave(12)
    b = (torch.arange(12) + 3).repeat(3)
    W = wfc.hrtw(tall, deg, a, b, opts).reshape(3, 12)
    t_all = torch.cat([tinc, tex, tg.reshape(1)])
    r_all = torch.cat([torch.ones(3, dtype=DTYPE), rho, torch.ones(1, dtype=DTYPE)])
    v, w, sv = wfc.hrtw_prepare(t_all, r_all, st, 3)
    gb, ea = wfc.hrtw_sums(v, w[:3], sv, st, tinc, v[:3], tex, v[3:-1])
    assert torch.allclose((tinc[:, None] * W).sum(0), gb, rtol=1e-12)
    # The elastic diagonal is the (w_a - 1) term of hrtw.f90:22. `ea` is that term of W(a,a)
    # ITSELF, in the same convention as moldauer_sums: comptarget.f90:635 weights every width
    # fluctuation factor by Tinc * Tout, so the caller -- and this assertion -- supplies both
    # factors of T_a. Returning T_a * (Wel - W00) instead costs a factor w_a (up to 3) on
    # compound elastic wherever T_a is small.
    Wel = wfc.hrtw(tall, deg, torch.arange(3), torch.arange(3),
                   {**opts, "elastic": torch.ones(3)})
    W00 = wfc.hrtw(tall, deg, torch.arange(3), torch.arange(3), opts)
    assert torch.allclose(Wel - W00, ea, rtol=1e-12)
    assert torch.allclose(tinc * tinc * (Wel - W00), tinc * tinc * ea, rtol=1e-12)


def test_gate_continuum_decay_matches_talys_dpop(tmp_path):
    """A-mult component diagnostic: the daughter increments and denomhf of compound.f90, inputs
    injected from the instrumented multi dump. Tolerance 5% (contract §6); the port sits at the
    single-precision floor, so a regression of any real size trips this."""
    from physics.hf.compound.continuum import compound_decay, load_cn_multi_dump

    runs = sorted(REF.glob("multi*__*.tar.gz"))
    if not runs:
        pytest.skip(f"no instrumented continuum-decay dump in {REF}")
    rs, rd = [], []
    for tar in runs:
        with tarfile.open(tar) as tf:
            m = next(x for x in tf.getmembers() if x.name.endswith("cn_multi.txt"))
            tf.extract(m, tmp_path, filter="data")
        for mi in load_cn_multi_dump(tmp_path / m.name):
            f = compound_decay(mi)
            for t, got in f.dpop_mb.items():
                ref = mi.ref_dpop_mb.get(t)
                if ref is None:
                    continue
                g, live = got.numpy(), ref >= 1e-6
                rs.append(np.abs(np.log(np.maximum(g[live], 1e-300) / ref[live])))
            ks = sorted(mi.denomhf)
            ref_d = np.array([mi.denomhf[k] for k in ks])
            got_d = np.array([float(f.denom[k]) for k in ks])
            live = ref_d > 0
            rd.append(np.abs(np.log(np.maximum(got_d[live], 1e-300) / ref_d[live])))
    r, d = np.concatenate(rs), np.concatenate(rd)
    assert np.percentile(r, 95) <= 0.05, (np.percentile(r, 95), r.max())
    assert np.percentile(d, 95) <= 0.05, (np.percentile(d, 95), d.max())


# ------------------------------------------------------------------------------------------------
# GOE (widthmode 3)
# ------------------------------------------------------------------------------------------------


def test_gauss_legendre_is_talys_half_weight_table_in_single_precision():
    """Two properties of gauleg.f90 a textbook Gauss-Legendre routine does not have, both of which
    the GOE integral depends on."""
    x, w = wfc.gauss_legendre(50)
    xn, wn = np.polynomial.legendre.leggauss(50)
    assert np.abs(np.sort(x.numpy()) - xn).max() < 1e-7  # the nodes ARE the Legendre roots
    # gauleg.f90:50 omits the factor 2: the weights sum to 1, and goeprepare puts it back by hand.
    assert float(w.sum()) == pytest.approx(1.0, rel=1e-5)
    # ... and the outermost weight is 9.8e-4 high, because P_49 comes out of a 49-term recurrence
    # in real(sgl) and is smallest exactly there. Recomputing the table in float64 moves W on the
    # capture channel by that much -- thirty times the rest of the port's error budget.
    xs, ws = x.numpy(), w.numpy()
    ref = np.empty_like(ws)
    for i, xi in enumerate(xs):                       # pair each node with its exact weight
        ref[i] = wn[int(np.argmin(np.abs(xn - xi)))] / 2.0
    rel = ws / ref - 1.0
    outer = int(np.argmax(np.abs(xs)))
    assert rel[outer] == pytest.approx(9.755e-4, rel=1e-3)
    assert np.abs(rel[np.abs(xs) < 0.98]).max() < 1e-4


def test_goe_runs_conserves_flux_to_its_own_accuracy_and_enhances_elastic():
    """widthmode 3. Like HRTW, GOE is not normalised to conserve flux exactly, but its 50-point
    triple integral must stay close and still enhance compound elastic."""
    p0 = compound_target_inputs(_toy(wmode=0)).pop_mb[0]
    p3 = compound_target_inputs(_toy(wmode=3)).pop_mb[0]
    assert float(p3.sum()) == pytest.approx(float(p0.sum()), rel=0.05)
    assert float(p3[1, 0].sum()) > float(p0[1, 0].sum()) * 1.01


def test_scalar_goe_matches_the_factorised_sums():
    """The production path sums over incident channels BEFORE the exit channel, which is only
    legal because func1.f90:31-32 separates in (ta, tb) once `dab` is zero. Checked pair by pair
    against `wfc.goe`, which evaluates goe.f90 as the Fortran writes it."""
    torch.manual_seed(2)
    tinc = torch.rand(3, dtype=DTYPE) * 0.5 + 0.05
    tex = torch.rand(6, dtype=DTYPE) * 0.5 + 0.05
    rho = torch.rand(6, dtype=DTYPE) * 3 + 0.5
    tg = torch.tensor(0.2, dtype=DTYPE)
    st = (rho * tex).sum() + tg
    assert float(st) < wfc.GOE_STSWITCH  # the triple-integral branch
    tall = torch.cat([tinc, tex])
    deg = torch.cat([torch.ones(3, dtype=DTYPE), rho])
    opts = {"ninc": 3, "st": st, "tgamma": tg}
    a = torch.arange(3).repeat_interleave(6)
    b = (torch.arange(6) + 3).repeat(3)
    W = wfc.goe(tall, deg, a, b, opts).reshape(3, 6)
    prep = wfc.goe_prepare(tex, rho, st, tg)
    inc = wfc.goe_incident(prep, tinc)
    gb = wfc.goe_sums(prep, inc, tex, wfc.transjl_powers(tex, rho))
    assert torch.allclose((tinc[:, None] * W).sum(0), gb, rtol=1e-11)
    # the lumped capture channel: goe.f90:106 zeroes tav but keeps tjl(1,.) = gamwidth
    ac = torch.arange(3)
    Wg = wfc.goe(tall, deg, ac, torch.full((3,), tall.shape[0]), opts)
    one = torch.ones(1, dtype=DTYPE)
    gg = wfc.goe_sums(prep, inc, tg.reshape(1),
                      wfc.transjl_powers(tg.reshape(1), one, guard=tg.reshape(1), gamma=True),
                      capture=True)
    assert float((tinc * Wg).sum()) == pytest.approx(float(gg), rel=1e-11)
    # and the ielas = 1 diagonal, in moldauer_sums' convention: E_a = W(a,a|1) - W(a,a|0)
    jl_el = wfc.transjl_powers(tex[:3], rho[:3])
    Wel = wfc.goe(tall, deg, ac, ac + 3, {**opts, "elastic": torch.ones(3)})
    W00 = wfc.goe(tall, deg, ac, ac + 3, opts)
    ea = wfc.goe_elastic(prep, inc, tex[:3], jl_el)
    assert torch.allclose(Wel - W00, ea, rtol=1e-11)


def test_scalar_goe_matches_the_factorised_sums_in_the_moment_branch():
    """The same three quantities above `st = 20`, where goe.f90:143-178 replaces the grid. The
    capture channel is the interesting one: goe.f90:106's `tb = 0` is a GRID-branch statement, so
    here the photon channel keeps `tjl(1,.) = gamwidth`."""
    torch.manual_seed(5)
    tinc = torch.rand(4, dtype=DTYPE) * 0.5 + 0.05
    tex = torch.rand(60, dtype=DTYPE) * 0.6 + 0.2
    rho = torch.rand(60, dtype=DTYPE) * 2 + 0.6
    tg = torch.tensor(0.3, dtype=DTYPE)
    st = (rho * tex).sum() + tg
    assert float(st) > wfc.GOE_STSWITCH
    tall = torch.cat([tinc, tex])
    deg = torch.cat([torch.ones(4, dtype=DTYPE), rho])
    opts = {"ninc": 4, "st": st, "tgamma": tg}
    prep = wfc.goe_prepare(tex, rho, st, tg)
    assert prep["mode"] == "moments"
    inc = wfc.goe_incident(prep, tinc)
    a = torch.arange(4).repeat_interleave(60)
    b = (torch.arange(60) + 4).repeat(4)
    W = wfc.goe(tall, deg, a, b, opts).reshape(4, 60)
    gb = wfc.goe_sums(prep, inc, tex, wfc.transjl_powers(tex, rho))
    assert torch.allclose((tinc[:, None] * W).sum(0), gb, rtol=1e-11)
    ac = torch.arange(4)
    one = torch.ones(1, dtype=DTYPE)
    Wg = wfc.goe(tall, deg, ac, torch.full((4,), tall.shape[0]), opts)
    gg = wfc.goe_sums(prep, inc, tg.reshape(1),
                      wfc.transjl_powers(tg.reshape(1), one, guard=tg.reshape(1), gamma=True),
                      capture=True)
    assert float((tinc * Wg).sum()) == pytest.approx(float(gg), rel=1e-11)
    Wel = wfc.goe(tall, deg, ac, ac + 4, {**opts, "elastic": torch.ones(4)})
    W00 = wfc.goe(tall, deg, ac, ac + 4, opts)
    ea = wfc.goe_elastic(prep, inc, tex[:4], wfc.transjl_powers(tex[:4], rho[:4]))
    assert torch.allclose(Wel - W00, ea, rtol=1e-11)


def test_goe_moment_branch_takes_over_above_st_20_and_is_continuous():
    """goeprepare.f90:111 / goe.f90:102 swap the triple integral for an asymptotic expansion at
    st = 20. Both are approximations to the same quantity, so they must agree to O(1) there --
    and the moment branch, unlike the grid, must not depend on how the (Ir, P') cells are lumped."""
    torch.manual_seed(3)
    tex = torch.rand(40, dtype=DTYPE) * 0.6 + 0.2
    rho = torch.full((40,), 1.2, dtype=DTYPE)
    tg = torch.tensor(0.3, dtype=DTYPE)
    tinc = torch.rand(3, dtype=DTYPE) * 0.5 + 0.05
    lo = (rho * tex).sum() * 0.7 + tg
    hi = (rho * tex).sum() * 1.4 + tg
    assert float(lo) < wfc.GOE_STSWITCH < float(hi)
    out = []
    for st in (lo, hi):
        prep = wfc.goe_prepare(tex, rho, st, tg)
        inc = wfc.goe_incident(prep, tinc)
        g = wfc.goe_sums(prep, inc, tex, wfc.transjl_powers(tex, rho))
        out.append((prep["mode"], (g / st).mean()))
    assert out[0][0] == "grid" and out[1][0] == "moments"
    assert float(out[1][1]) == pytest.approx(float(out[0][1]), rel=0.5)
    # tb6 = tjl(1) tjl(5) / max(tjl(0), 1) is the one term that is not linear in rho, so lumping
    # n cells of weight rho needs sum(rho^2 / max(rho,1)), not (n rho)^2 / max(n rho, 1).
    small = torch.full((40,), 0.3, dtype=DTYPE)
    split = wfc.transjl_powers(tex, small).repeat(1, 1) * 4.0
    lumped = wfc.transjl_powers(tex, 4.0 * small, kappa=4.0 * small * small)
    assert torch.allclose(lumped, torch.stack([split[:, i] for i in range(6)], -1), rtol=1e-12)
    naive = wfc.transjl_powers(tex, 4.0 * small)
    assert not torch.allclose(naive[:, 5], lumped[:, 5])


def test_goe_grid_channel_list_is_collapsed_without_changing_the_answer():
    """goe_prepare drops dead channels and merges equal transmissions: prodm/prodp see each
    distinct T once with sum(rho) as its exponent. comptarget hands over ~2e4 (nexout, l', j')
    cells above a few MeV against ~1e3 distinct live values, so this is what makes it run."""
    torch.manual_seed(4)
    tex = torch.rand(5, dtype=DTYPE) * 0.4 + 0.05
    rho = torch.rand(5, dtype=DTYPE) * 2 + 0.5
    tg = torch.tensor(0.15, dtype=DTYPE)
    st = (rho * tex).sum() + tg
    tinc = torch.rand(2, dtype=DTYPE) * 0.4 + 0.05
    padded_t = torch.cat([tex, tex, torch.zeros(30, dtype=DTYPE)])
    padded_r = torch.cat([rho / 2, rho / 2, torch.rand(30, dtype=DTYPE)])
    got = []
    for t, r in ((tex, rho), (padded_t, padded_r)):
        prep = wfc.goe_prepare(t, r, st, tg)
        inc = wfc.goe_incident(prep, tinc)
        got.append(wfc.goe_sums(prep, inc, tex, wfc.transjl_powers(tex, rho)))
    assert torch.allclose(got[0], got[1], rtol=1e-12)


@pytest.mark.parametrize("wmode", [1, 2, 3])
def test_every_width_fluctuation_model_is_reachable_from_comptarget(wmode):
    """widthfluc.f90:73-76 dispatches on wmode; none of the three may raise."""
    pop = compound_target_inputs(_toy(wmode=wmode)).pop_mb[0]
    assert torch.isfinite(pop).all() and float(pop.sum()) > 0


def test_goe_gate_numbers_are_inside_the_component_tolerance():
    """A-cn2 on the widthmode 3 reference set, if it has been scored on this tree."""
    p = Path("docs/results/hf-compound-gates-goe.json")
    if not p.exists():
        pytest.skip("hf-compound-gates-goe.json not built on this tree")
    g = json.loads(p.read_text())
    for kind in ("binE", "xspop"):
        k = f"A-cn2-goe:{kind}"
        assert k in g, sorted(g)
        assert g[k]["all"]["n_inf"] == 0, (k, g[k]["all"])
        assert g[k]["all"]["p95"] <= g[k]["tolerance_p95"], (k, g[k]["all"])
        assert g[k]["pass"], k


# ================================================================================================
# EXCL: population.f90 and the chained compnorm
# ================================================================================================


def _pop_inputs(**kw):
    """A two-bin residual on a six-point emission grid; the spectrum is 1 mb/MeV flat, so the
    exact bin integral is deltaEx and the normalisation factor is xspreeqtot / sum(deltaEx).

    `etotal` is deliberately NOT on a grid point: `Eb = min(egrid(nb), Etotal - S)`
    (population.f90:146) collapses to `Ea` when it is, and TALYS's `pol1` divides by zero there
    exactly as this port does.
    """
    from physics.hf.compound.population import PopResidual, PopulationInputs

    r = PopResidual(type=1, nlast=0, maxex=2, sep_mev=0.0,
                    ex_mev=np.array([0.0, 1.0, 3.0]), dex_mev=np.array([0.0, 2.0, 2.0]))
    base = dict(
        etotal_mev=5.5, egrid_mev=np.array([0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0]),
        ebegin={1: 1}, eend={1: 6}, residuals={1: r},
        xspreeq_mb={1: np.ones(7)}, xspreeqtot_mb={1: 4.0},
    )
    base.update(kw)
    return PopulationInputs(**base)


def test_population_integrates_a_flat_spectrum_to_the_bin_width():
    from physics.hf.compound.population import population

    # with xspreeqtot equal to the raw integral the normalisation is exactly 1
    res = population(_pop_inputs(xspreeqtot_mb={1: 4.0}))
    col = res.preeqpopex_mb[1]
    assert col[0] == 0.0  # discrete levels are never filled: the loop starts at NL + 1
    assert res.norm[1] == pytest.approx(1.0, abs=1e-12)
    assert col[1] == pytest.approx(2.0, rel=1e-12)
    assert col[2] == pytest.approx(2.0, rel=1e-12)


def test_population_renormalises_the_whole_column_to_the_preequilibrium_total():
    """population.f90:246-268: interpolation does not conserve flux, so the column is rescaled to
    xspreeqtot + xsgrtot -- and the check value is reported before the rescaling."""
    from physics.hf.compound.population import population

    res = population(_pop_inputs(xspreeqtot_mb={1: 10.0}))
    assert res.xscheck_mb[1] == pytest.approx(4.0, rel=1e-12)
    assert res.norm[1] == pytest.approx(2.5, rel=1e-12)
    assert float(res.preeqpopex_mb[1].sum()) == pytest.approx(10.0, rel=1e-12)


def test_population_adds_the_giant_resonance_only_when_flaggiant():
    from physics.hf.compound.population import population

    gr = {1: np.ones(7)}
    off = population(_pop_inputs(xsgr_mb=gr, xsgrtot_mb={1: 4.0}, flaggiant=False))
    on = population(_pop_inputs(xsgr_mb=gr, xsgrtot_mb={1: 4.0}, flaggiant=True))
    assert off.xscheck_mb[1] == pytest.approx(4.0, rel=1e-12)
    assert on.xscheck_mb[1] == pytest.approx(8.0, rel=1e-12)  # spectrum doubled
    assert on.norm[1] == pytest.approx(1.0, rel=1e-12)  # and so is the total it normalises to


def test_population_skips_the_spin_resolved_and_multipreeq_branches_at_the_defaults():
    """pespinmodel is 1 for an incident neutron (input_preeqmodel.f90:76-80) and flagmulpre is
    false below emulpre = 20 MeV, so neither array is even allocated."""
    from physics.hf.compound.population import population

    res = population(_pop_inputs())
    assert res.preeqpop_mb == {}
    assert res.xspopph_mb == {} and res.xspopph2_mb == {}
    assert res.mulpre == {1: False}


def test_population_sets_mulpre_for_nucleons_only():
    from physics.hf.compound.population import PopResidual, population

    r6 = PopResidual(type=6, nlast=0, maxex=2, sep_mev=0.0,
                     ex_mev=np.array([0.0, 1.0, 3.0]), dex_mev=np.array([0.0, 2.0, 2.0]))
    # (maxpar + 1)**2 x E with maxpar = numexc / 2 = 6 (preeqinit.f90:64-65). It used to be
    # sized 6 x 6 here and `PopulationInputs.maxpar` used to default to 5, which silently
    # dropped the (6, .) and (., 6) particle-hole columns `multipreeq2` reads.
    inp = _pop_inputs(flagmulpre=True, xsstep2_mb={1: np.zeros((7, 7, 7))})
    assert inp.maxpar == 6
    inp.residuals[6] = r6
    inp.xspreeq_mb[6] = np.ones(7)
    inp.xspreeqtot_mb[6] = 4.0
    inp.ebegin[6] = 1
    inp.eend[6] = 6
    res = population(inp)
    assert res.mulpre == {1: True, 6: False}  # population.f90:129


def test_population_returns_nothing_for_an_optical_model_only_run():
    from physics.hf.compound.population import population

    assert population(_pop_inputs(flagomponly=True)).preeqpopex_mb == {}


def test_compnorm_gate_numbers_are_inside_the_component_tolerance():
    """The chained compnorm gate, if it has been run on this tree."""
    p = Path("docs/results/hf-compnorm-gate.json")
    if not p.exists():
        pytest.skip("hf-compnorm-gate.json not built on this tree")
    g = json.loads(p.read_text())
    # `norm` is in worst_p95 as a diagnostic and is NOT supposed to be 1 for a coupled-channels
    # target, so only the gated quantities are asserted (gated_quantities in the JSON says which).
    for k in ("cnfactor", "xsflux"):
        v = g["worst_p95"][k]
        assert v is not None and v <= g["tol"], (k, v)
    assert g["j2_exact_all"] and g["lmaxinc_exact_all"]
    for r in g["runs"]:
        b, n = r["j2_exact"].split("/")
        assert b == n, (r["run"], r["j2_exact"])
        b, n = r["lmaxinc_exact"].split("/")
        assert b == n, (r["run"], r["lmaxinc_exact"])
    assert g["pass"]


def test_population_gate_numbers_are_inside_the_component_tolerance():
    p = Path("docs/results/hf-population-gate.json")
    if not p.exists():
        pytest.skip("hf-population-gate.json not built on this tree")
    g = json.loads(p.read_text())
    assert g["worst_p95"] is not None and g["worst_p95"] <= g["tol"], g["worst_p95"]
    assert g["n_inf"] == 0
    assert g["pass"]
