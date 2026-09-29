"""TWOPH: ECIS's second-order vibrational branch (`ecis1(2:2) = 'T'`), the 37 `colltype V`
sweep nuclides that raised `NotImplementedError` in `ecis.incident` until now.

Gate: G-2PH, `docs/results/hf-ecis-twophonon.md`. The scoring against TALYS lives in
`physics.hf.ecis.score_twophonon`; what is here is the part that needs no TALYS run.

`fixtures/ecis_vibm.json` was produced by ECIS-06's OWN `vibm`, extracted from `ecist.f`
together with `djcg` and `dj6j` and compiled (`gfortran -O0 -std=legacy -ffp-contract=off`),
driven on seven coupling schemes: the three gate targets, the two of the 37 that differ (Pd-106's
3+ member and Ce-136's negative-parity one), Ca-40 (one phonon, three bands, `lo(2) = F`) and a
synthetic two-band scheme that reaches the branches TALYS never writes.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import pytest
import torch

from physics.hf.core.tensors import DTYPE
from physics.hf.ecis.coupling import (
    anharmonic_vibrational_channels,
    vibrational_channels,
)
from physics.hf.ecis.reference import coupled_band
from physics.hf.ecis.vibm import Phonons, VibLevel, reduced_matrix_elements, scheme_from_band

FIXTURE = Path(__file__).parent / "fixtures" / "ecis_vibm.json"
# Zn-64 ... Ce-136: the 37 `colltype V` nuclides of features/talys_sweep_broad with a
# two-phonon level, from docs/results/hf-ecis-twophonon.md §1.
THIRTY_SEVEN: tuple[tuple[int, int], ...] = (
    (30, 64), (30, 66), (32, 70), (32, 72), (32, 74), (32, 76), (34, 74), (34, 76), (34, 78),
    (34, 80), (34, 82), (36, 78), (36, 80), (36, 82), (36, 84), (36, 86), (42, 100), (44, 96),
    (44, 98), (44, 100), (44, 102), (44, 104), (46, 102), (46, 104), (46, 106), (46, 108),
    (46, 110), (48, 106), (48, 108), (48, 110), (48, 112), (48, 114), (48, 116), (52, 120),
    (52, 122), (52, 124), (58, 136),
)  # fmt: skip


def _cases() -> dict:
    return json.loads(FIXTURE.read_text())


def _scheme(cfg) -> object:
    levels = [
        VibLevel(
            n_phonon=n,
            bands=() if n == 0 else ((b,) if n == 1 else tuple(cfg["npa"][b - 1])),
            two_spin=s - 1,
            parity_index=p,
        )
        for n, b, p, s in cfg["levels"]
    ]
    phonons = Phonons(
        lam=(0, *(l for l, _k in cfg["phonons"])), kmag=(0, *(k for _l, k in cfg["phonons"]))
    )
    return reduced_matrix_elements(levels, phonons, bool(cfg["lo2"]))


@pytest.mark.parametrize("name", sorted(_cases()))
def test_vibm_matches_ecis_own_routine(name):
    """Every `(iq(1), lambda, t)` of `vibm`, against ECIS-06's compiled `vibm`."""
    case = _cases()[name]
    got = _scheme(case["config"]).as_dict()
    want: dict = {}
    for i1, i2, code, mult, t in case["elements"]:
        want.setdefault((i1, i2), []).append((code, mult, t))
    assert {k: [(c, m) for c, m, _ in v] for k, v in got.items()} == {
        k: [(c, m) for c, m, _ in v] for k, v in want.items()
    }, "form-factor code / multipole table differs (the `vibm` merge is order-sensitive)"
    worst = 0.0
    for key, items in want.items():
        for (c, m, t), (gc, gm, gt) in zip(items, got[key], strict=True):
            assert (c, m) == (gc, gm)
            worst = max(worst, abs(gt - t) / max(abs(t), 1.0e-30))
    assert worst < 1.0e-12, worst


def test_the_37_are_one_configuration_with_two_form_factors():
    """All 37 sweep nuclides build a scheme, and every one has `nbt1 = 1` -- a single phonon,
    so exactly two transition form factors: first order in beta and second order in beta^2."""
    seen = set()
    for Z, A in THIRTY_SEVEN:
        band = coupled_band(Z, A)
        assert band["colltype"] == "V"
        assert int(band["iphonon"].max()) == 2
        scheme, beta = scheme_from_band(band)
        assert scheme.nbt1 == 1, (Z, A, scheme.nbt1)
        assert scheme.codes == (1, 3), (Z, A, scheme.codes)
        assert beta.numel() == 2 and float(beta[1]) > 0.0
        seen.add(tuple(band["spin"].tolist()) + tuple(band["parity"].tolist()))
    assert len(THIRTY_SEVEN) == 37
    assert len(seen) == 8, seen  # eight orderings of the same five levels


def test_second_order_monopole_is_the_angle_average_of_the_deformed_potential():
    """`vibm`'s lambda = 0 elements times `quan`'s lambda = 0 coefficient must put exactly ONE
    unit of the second-order form factor on EVERY level's diagonal, because that form factor
    already IS `<U(r - delta)> - U(r) = (1/2) <delta^2> U''` with
    `<delta^2> = s^2 beta^2 / (4 pi)`, and the monopole shift cannot depend on the state. `vibm`
    writes `t = 1`, `sqrt(2I+1)` and `sqrt(2I+1)` for the three cases that produce it
    (vibm-147/180/291) and `quan`'s lambda = 0 coefficient divides the `sqrt(2I+1)` out again.

    The full beta^2 diagonal is NOT that: the same slice also carries the lambda = 2 and 4
    reorientation of vibm-188..197 and vibm-296..313, which is l- and j-dependent. This isolates
    the lambda = 0 part, and what comes out is

        1 + 2 n / (2 lambda + 1)

    for a level of n phonons -- 1, 1.4, 1.8 for lambda = 2 -- which is the harmonic oscillator's
    `<n| sum_mu alpha_mu alpha*_mu |n>`: the ground state gets the bare `<delta^2>` and each
    phonon adds `2/(2 lambda + 1)` of it. The `1` is `vibm`'s case-1/3/5 monopole proper
    (vibm-147/180/291, `t = 1` or `sqrt(2I+1)`, which `quan` divides out); the rest is the
    `j = 0` member of the reorientation series, which is a monopole too."""
    band = coupled_band(30, 64)
    scheme, _ = scheme_from_band(band)
    mono = _keep_lambda_zero(scheme)
    ch = anharmonic_vibrational_channels(
        5, 1, band["spin"], band["parity"], mono, mono.codes, lmax=6
    )
    beta2 = ch.coupling[1 + mono.codes.index(3)]
    diag = torch.diagonal(beta2)
    lam = float(band["jband"][1])
    nph = torch.tensor([0] + [1] + [2] * (int(band["spin"].numel()) - 2))
    want = 1.0 + 2.0 * nph[ch.level].to(DTYPE) / (2.0 * lam + 1.0)
    assert torch.allclose(diag, want, atol=1.0e-12), (diag, want)
    # the only lambda = 0 element off the diagonal is case 6's ground state -> two-phonon 0+
    # (vibm-316..327 with k3 = I = 0), which needs both levels to be 0+
    off = (beta2 - torch.diag_embed(diag)).abs() > 1.0e-12
    spin0 = band["spin"][ch.level] == 0.0
    assert bool((off <= (spin0[:, None] & spin0[None, :])).all())
    assert bool(off.any())


def _keep_lambda_zero(scheme):
    from physics.hf.ecis.vibm import VibmScheme

    pairs = tuple((a, b, tuple(x for x in it if x[1] == 0))
                  for a, b, it in scheme.pairs)
    pairs = tuple(x for x in pairs if x[2])
    codes = tuple(sorted({c for _a, _b, it in pairs for c, _m, _t in it}))
    return VibmScheme(pairs=pairs, codes=codes, nbt1=scheme.nbt1)


def test_anharmonic_coupling_is_symmetric():
    """ECIS fills one triangle of `nat/at` and copies it; the matrix must come out symmetric or
    the S-matrix is not."""
    band = coupled_band(52, 124)
    scheme, _ = scheme_from_band(band)
    for twoJ in (1, 5, 11):
        for par in (-1, 1):
            ch = anharmonic_vibrational_channels(
                twoJ, par, band["spin"], band["parity"], scheme, scheme.codes, lmax=8
            )
            if ch.level.numel() == 0:
                continue
            for k in range(ch.coupling.shape[0]):
                m = ch.coupling[k]
                # symmetric to rounding: the geometrical factor is evaluated once over the whole
                # (N, N) block and its own row/column asymmetry is at the last bits
                assert torch.allclose(m, m.T, atol=1.0e-13), (twoJ, par, k,
                                                              float((m - m.T).abs().max()))


def test_harmonic_target_is_untouched_by_the_new_branch():
    """Ca-40 has no two-phonon level, so `scheme_from_band` leaves `lo(2)` off and the only
    elements are the one-phonon couplings of vibm-152..162 -- one per band, `t = +/- 1`."""
    band = coupled_band(20, 40)
    scheme, _ = scheme_from_band(band)
    assert scheme.nbt1 == 3
    assert scheme.codes == (1, 2, 3)
    got = scheme.as_dict()
    assert set(got) == {(0, 1), (0, 2), (0, 3)}
    for (_a, b), items in got.items():
        (code, mult, t) = items[0]
        assert code == b and abs(abs(t) - 1.0) < 1.0e-15


def test_harmonic_and_anharmonic_couplings_differ_only_by_a_band_sign():
    """On a one-phonon target the two paths give the same coupling up to one sign PER BAND.

    The harmonic path takes `t = +1` and a `+(beta/sqrt(4 pi)) dU/dr` form factor; this one
    takes `vibm`'s `t` (vibm-161, `-1` unless `lambda + ipi(1,j1) - ipi(1,j2)` is a multiple of
    4) against a NEGATED form factor, so the coupling matrices differ by `t` and the PRODUCTS
    coupling x form factor differ by `-t`. That is +1 for every band whose `t` is `-1` and -1
    for the rest -- Ca-40's lambda = 5 band, whose level is negative-parity, is one. The flip is
    the exact gauge `A_0b -> -A_0b` of the harmonic model, which no observable sees, because
    with no level-to-level coupling every path uses `A_0b` an even number of times
    (`test_harmonic_and_anharmonic_cross_sections_agree` is the statement that matters)."""
    band = coupled_band(20, 40)
    scheme, _ = scheme_from_band(band)
    signs = {b: t for (_a, b, items) in scheme.pairs for (_c, _m, t) in items}
    assert sorted(signs.values()) == [-1.0, -1.0, 1.0]
    for twoJ in (1, 7):
        for par in (-1, 1):
            a = anharmonic_vibrational_channels(
                twoJ, par, band["spin"], band["parity"], scheme, scheme.codes, lmax=8
            )
            h = vibrational_channels(
                twoJ, par, band["spin"], band["parity"], band["vib_lambda"], lmax=8
            )
            if a.level.numel() == 0:
                continue
            assert torch.allclose(a.coupling[0], h.coupling[0])
            for q, code in enumerate(scheme.codes):
                assert torch.allclose(a.coupling[q + 1], signs[code] * h.coupling[code],
                                      atol=1.0e-13)


def test_harmonic_and_anharmonic_cross_sections_agree():
    """Ca-40 through the second-order machinery with `lo(2)` off, against the harmonic path it
    normally takes: same sigma_tot, sigma_reac, sigma_shape-el, direct cross sections and Tjl.

    This is the end-to-end statement that the new branch's sign conventions -- `vibm`'s `t`
    against a negated first-order form factor -- are the same physics as the path that already
    passes A-inc, and it exercises the whole anharmonic set-up (form-factor stack, code map,
    coupling, channel cache) on a target whose answer is already gated."""
    from physics.hf.ecis.incident import _t4_parameters, njmax_incident
    from physics.hf.ecis.solver import solve_vibrational
    from physics.hf.omp.schrodinger import PARMASS_AMU, nucleus_mass_amu

    Z, A = 20, 40
    band = coupled_band(Z, A)
    scheme, beta = scheme_from_band(band)
    assert scheme.codes == (1, 2, 3)
    e = torch.tensor([1.0, 8.0, 14.0], dtype=DTYPE)
    omp = _t4_parameters(Z, A, 1, e, band["options"])
    common = (omp, PARMASS_AMU[1], nucleus_mass_amu(Z, A), 0.0, e,
              band["e_mev"], band["spin"], band["parity"], band["vib_lambda"],
              band["vib_beta"], band["deformation_length"])
    nj = njmax_incident(A, PARMASS_AMU[1], float(e.max()))
    harm = solve_vibrational(*common, lmax=nj)
    anh = solve_vibrational(*common, lmax=nj, scheme=scheme, band_beta=beta)
    for field in ("sigma_tot_mb", "sigma_reac_mb", "sigma_shape_el_mb"):
        g, w = getattr(anh, field), getattr(harm, field)
        assert torch.allclose(g, w, rtol=2.0e-11), (field, (g - w).abs().max())
    assert torch.allclose(anh.sigma_direct_mb, harm.sigma_direct_mb, rtol=2.0e-11, atol=1e-12)
    assert torch.allclose(anh.tjl, harm.tjl, rtol=2.0e-11, atol=1e-14)


@pytest.mark.parametrize("Z,A", [(30, 64), (52, 124)])
def test_two_phonon_target_solves_and_conserves_flux(Z, A):
    """The coupled solve runs and its S-matrix is unitary-bounded: the direct cross sections are
    positive, and sigma_reac = sigma_tot - sigma_shape_el holds to rounding."""
    from physics.hf.ecis.incident import incident_coupled

    band = coupled_band(Z, A)
    e = torch.tensor([1.0, 14.0], dtype=DTYPE)
    inc, res = incident_coupled(None, Z, A, e, band, options=band["options"])
    assert torch.isfinite(res.sigma_reac_mb).all()
    assert (res.sigma_reac_mb > 0).all()
    assert (res.sigma_direct_mb[:, 1:] >= 0).all()
    lhs = res.sigma_tot_mb - res.sigma_shape_el_mb
    assert torch.allclose(lhs, res.sigma_reac_mb, rtol=1.0e-10)
    assert (inc.tjl_inc >= 0).all() and (inc.tjl_inc <= 1.0 + 1.0e-9).all()


def test_second_derivative_form_factor_is_the_derivative_of_the_first():
    """`second_derivative_form_factor` against a central difference of
    `derivative_form_factor` on the same parameters -- the two form factors the second-order
    branch multiplies together."""
    from physics.hf.ecis.formfactor import (
        ALL_CENTRAL_PARTS,
        derivative_form_factor,
        second_derivative_form_factor,
    )

    class P:
        v_mev = torch.tensor([50.0], dtype=DTYPE)
        rv_fm = torch.tensor([1.2], dtype=DTYPE)
        av_fm = torch.tensor([0.66], dtype=DTYPE)
        w_mev = torch.tensor([3.0], dtype=DTYPE)
        rw_fm = torch.tensor([1.2], dtype=DTYPE)
        aw_fm = torch.tensor([0.66], dtype=DTYPE)
        vd_mev = torch.tensor([1.5], dtype=DTYPE)
        rvd_fm = torch.tensor([1.3], dtype=DTYPE)
        avd_fm = torch.tensor([0.55], dtype=DTYPE)
        wd_mev = torch.tensor([7.0], dtype=DTYPE)
        rwd_fm = torch.tensor([1.3], dtype=DTYPE)
        awd_fm = torch.tensor([0.55], dtype=DTYPE)
        vso_mev = torch.tensor([6.0], dtype=DTYPE)
        rvso_fm = torch.tensor([1.0], dtype=DTYPE)
        avso_fm = torch.tensor([0.58], dtype=DTYPE)
        wso_mev = torch.tensor([0.1], dtype=DTYPE)
        rwso_fm = torch.tensor([1.0], dtype=DTYPE)
        awso_fm = torch.tensor([0.58], dtype=DTYPE)
        rc_fm = torch.tensor([1.25], dtype=DTYPE)

    h = 1.0e-4
    r = torch.arange(1.0, 12.0, 0.25, dtype=DTYPE)
    args = (P(), 64.0)
    # `deformation_length=True` is ECIS's `lo(6)`, where rotp's `sr` is 1 for every potential
    # (rotp-116/124); with `sr = R_m` the two form factors carry sr and sr**2, so they are not
    # derivatives of each other by construction.
    fd = (
        derivative_form_factor(*args, r + h, True, ALL_CENTRAL_PARTS)
        - derivative_form_factor(*args, r - h, True, ALL_CENTRAL_PARTS)
    ) / (2 * h)
    got = second_derivative_form_factor(*args, r, True, ALL_CENTRAL_PARTS)
    scale = fd.abs().max()
    assert (got - fd).abs().max() < 1.0e-6 * scale, (got - fd).abs().max() / scale
    assert math.isfinite(float(scale))


# ---------------------------------------------------------------------------------------------
# TWOPH part 2: T11's fission transmission wired into the dump-free chain
# ---------------------------------------------------------------------------------------------


def test_fission_chain_is_none_for_a_non_fissile_target():
    """`input_fissionmodel.f90:78-80` sets `flagfission` from `A > 215`, so nothing in the
    fission chain is built -- and no residual leaves `decay_fast`'s batched path -- for a
    spherical target."""
    from physics.hf.fission.chain import fission_chain

    assert fission_chain(26, 56) is None
    assert fission_chain(82, 208) is None
    assert fission_chain(92, 238) is not None


def test_fission_chain_keys_are_the_compound_side_s_j2_and_parity():
    """`fission.transmission` indexes `(J, parity)` with physical spin `J + odd/2`; the compound
    side keys `(J2, parity)` with `J2 = 2 * spin`. U-239 is odd, so every key must be odd."""
    from physics.hf.fission.chain import fission_chain

    fc = fission_chain(92, 238)
    assert fc.nfisbar(92, 239) == 3
    got = fc.compound_target(92, 239, 12.0)
    assert got["nfisbar"] == 3
    assert got["tfis"] and all(j2 % 2 == 1 for j2, _p in got["tfis"])
    assert set(p for _j, p in got["tfis"]) == {-1, 1}
    assert set(got["tfisA"]) == set(got["tfis"]) == set(got["rhofisA"])
    # U-238 is even: even J2
    tri = fc.bin_triples(92, 238, 5.0, 0.25, 11.0, 11.0)
    assert tri and all(j2 % 2 == 0 for j2, _p in tri)
    for down, mid, up in tri.values():
        assert down <= mid <= up or up == 0.0  # tfission evaluates Ex-dEx/2, Ex, Ex+dEx/2


def test_binary_feed_adds_the_binary_cross_section_once_per_type():
    """`multiple.f90:936-961` adds `xsbinary(type)` to `xsfeed(0,0,type)` once. `_binary_feed`
    built its type list as `list(xsfeed) + [-1]`, which counts `-1` twice as soon as the
    compound nucleus's own bins have fissioned -- i.e. on every actinide the moment the chain
    supplies a fission transmission. That was +10% on U-238's (n,f)."""
    from physics.hf.emission.multiple import MultipleResult, _binary_feed

    class _Nuc:
        maxex = 3

    res = MultipleResult(popexcl_mb={}, feedexcl_mb={})
    key = (0, 0)
    res.popexcl_mb[key] = {}
    res.feedexcl_mb[key] = {}
    res.fisfeedex_mb[key] = {}
    res.xsfeed_mb[key] = {-1: 7.0, 1: 2.0}
    _binary_feed(res, key, 0, 0, 1, 100.0, {-1: 5.0, 1: 3.0}, None, _Nuc(), True)
    assert res.xsfeed_mb[key][-1] == 12.0
    assert res.xsfeed_mb[key][1] == 5.0
    assert res.fisfeedex_mb[key][4] == 5.0


def test_chained_u238_fission_matches_talys():
    """(n,f) of the dump-free chain against TALYS's own `fission.tot`, three energies that span
    first, second and third chance. Before TWOPH this was 0 at every energy:
    `engine.ChainedFull` passed `tfis=None` and `flagfission=False`.

    The full 5-actinide, 23-energy gate is `harness/nodump_e2e.py --shape actinide`
    (`docs/results/hf-twoph-actinide-e2e.json`); this is the cheap sentinel.
    """
    import math

    from physics.hf.engine import ChainedFull
    from physics.hf.engine import run as engine_run
    from physics.hf.talys_reference import ENERGIES_MEV

    want = {2.0: 429.3058, 14.0: 1270.645, 20.0: 1764.395}  # default__U238/fission.tot
    res = engine_run(injection=ChainedFull(Z=92, A=238, declared_energies=ENERGIES_MEV,
                                           energies=tuple(want)))
    got = {round(float(e), 6): float(v)
           for e, v in zip(res.e_inc_mev, res.totals_mb["fission"], strict=True)}
    for e, ref in want.items():
        r = abs(math.log(got[round(e, 6)] / ref))
        assert r < 1.0e-3, (e, got[round(e, 6)], ref, r)
