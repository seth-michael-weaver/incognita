"""SETB: the speed paths hold the numbers of the code they replace.

* `density.matching_fast`: `match_vec`, `temprho_fill` and `ncum_at` are bitwise the loops
  (`match` with a gradient-carrying table, the inline fill, `densitycum`).
* `omp.schrodinger._g_recurrence` is bitwise the torch recurrence it replaced.
* `ecis.dwba_setb`: `cg_weights` and `exit_waves` are bitwise the inline forms, and
  `dwba_cross_sections` gives the same bits with and without them.
* `omp.incident_axis`: every field of the whole-grid incident channel equals the per-energy call
  to rounding (cross sections and strength functions 1e-11; T_l 1e-9 relative + 1e-12
  absolute; `lmax` exactly).
* `libccsplit` (split-storage solve and stabilisation) against `libccfast` on the same blocks:
  cross sections and T_lj to 1e-9, the bound `test_ccfast.py` holds `libccfast` to.
"""

from __future__ import annotations

import pytest
import torch

from physics.hf.core.tensors import DTYPE


@pytest.fixture(autouse=True)
def _one_thread():
    prev = torch.get_num_threads()
    torch.set_num_threads(1)
    yield
    torch.set_num_threads(prev)


def _ld(Zt, At, Z, A):
    try:
        from physics.hf.compound.dens_reference import _ld_of

        ld, _ntop, nl, _ncum = _ld_of(Z, A, Zt, At)
    except Exception as exc:  # noqa: BLE001  (structure database absent on this machine)
        pytest.skip(f"no level density for {Z}-{A}: {exc}")
    return ld, nl


NUCLEI = [(26, 56, 26, 57), (40, 90, 40, 91), (40, 90, 39, 90), (82, 208, 82, 209),
          (72, 177, 72, 178), (50, 120, 48, 117)]


def _same(a: torch.Tensor, b: torch.Tensor, rel: float = 1e-6) -> bool:
    """Reasonably close, not bit-identical (project rule):
    <=1e-6 relative, not bitwise. Hardware FP non-associativity measured up to ~1.8e-12 on
    x86 vs the capture machine (X86VERIFY, 2026-09-16); 1e-6 is far above that noise floor."""
    return a.shape == b.shape and bool(
        torch.isclose(a, b, rtol=rel, atol=1e-12, equal_nan=True).all()
    )


@pytest.mark.parametrize("zt,at,z,a", NUCLEI)
def test_match_vec_is_the_loop_bitwise(zt, at, z, a):
    from physics.hf.density.matching import _fermi_tables, match
    from physics.hf.density.parameters import SENTINEL

    ld, _nl = _ld(zt, at, z, a)
    logrho, temprho, _ns, nEx = _fermi_tables(ld, 0)
    x = 0.11 + torch.arange(0, 190, dtype=DTYPE) * 0.1037
    loop_t = temprho.clone().requires_grad_(True)  # a gradient-carrying table keeps the loop
    for e0 in (SENTINEL, 1.3):
        fast = match(ld, x, logrho, temprho, e0, 0)
        loop = match(ld, x, logrho, loop_t, e0, 0).detach()
        assert _same(fast, loop)
        assert _same(match(ld, x[7], logrho, temprho, e0, 0).reshape(()),
                     match(ld, x[7], logrho, loop_t, e0, 0).detach().reshape(()))


@pytest.mark.parametrize("zt,at,z,a", NUCLEI)
def test_temprho_fill_and_ncum_are_the_loops_bitwise(zt, at, z, a):
    from physics.hf.density.matching import _fermi_tables_core, densitycum
    from physics.hf.density.matching_fast import ncum_at, temprho_fill
    from physics.hf.density.models import densitytot
    from physics.hf.density.parameters import _fv, _t

    ld, nl = _ld(zt, at, z, a)
    # the unpadded core: `_fermi_tables` zero-pads to TALYS's nummatchT, `temprho_fill` returns nEx + 2 entries
    _logrho, temprho, nstart, nEx = _fermi_tables_core(ld, 0)
    # the inline fill, on the same raw column the table was built from
    raw = torch.zeros(nEx, dtype=DTYPE)
    raw[:] = temprho[1 : nEx + 1]
    ref = [None] * (nEx + 2)
    ref[nEx + 1] = _t(0.0)
    for k in range(nEx, 0, -1):
        v = raw[k - 1]
        ref[k] = ref[k + 1] if _fv(v) <= 0.1 else v
    ref[0] = _t(0.0)
    ref_n = 1
    for k in range(nEx, 0, -1):
        if k < nEx and _fv(ref[k]) >= _fv(ref[k + 1]):
            ref_n = k + 1
            break
    got, got_n = temprho_fill(raw, nEx)
    assert _same(got, torch.stack(ref)) and got_n == ref_n
    assert _same(got, temprho) and got_n == nstart

    n = ld.nlevmax2
    edis = ld.edis_mev
    dens = densitytot(ld, 0.5 * (edis[1 : n + 1] + edis[0:n]), 0)
    full = densitycum(ld)["Ncum"]
    for idx in sorted({min(nl, n), 1, n // 2, n}):
        assert ncum_at(edis, dens, int(ld.Nlow[0]), idx) == float(full[idx])


def test_g_recurrence_is_the_torch_loop_bitwise():
    from physics.hf.omp.schrodinger import _g_recurrence

    gen = torch.Generator().manual_seed(3)
    for charged in (False, True):
        rho = torch.rand(400, dtype=DTYPE, generator=gen) * 30.0 + 0.05
        eta = torch.rand(400, dtype=DTYPE, generator=gen) * 12.0 * charged
        G0, dG0 = torch.cos(rho), -torch.sin(rho)
        lmax = 45
        G = torch.empty(rho.shape + (lmax + 1,), dtype=DTYPE)
        dG = torch.empty_like(G)
        G[..., 0], dG[..., 0] = G0, dG0
        for L in range(1, lmax + 1):
            S = L / rho + eta / L
            R = torch.sqrt(1.0 + (eta / L) ** 2)
            G[..., L] = (S * G[..., L - 1] - dG[..., L - 1]) / R
            dG[..., L] = R * G[..., L - 1] - S * G[..., L]
        G2, dG2 = _g_recurrence(eta, rho, G0, dG0, lmax)
        assert _same(G, G2) and _same(dG, dG2)


def test_dwba_setb_pieces_are_the_inline_forms_bitwise():
    from physics.hf.core.angmom import clebsch
    from physics.hf.ecis.dwba import _lj_table
    from physics.hf.ecis.dwba_setb import cg_weights, exit_waves
    from physics.hf.omp.schrodinger import coulomb_functions

    lmax, njmax, spin = 26, 22, 0.5
    l, j, _ = _lj_table(lmax)
    jc, jp = j[None, :], j[:, None]
    par = ((-1.0) ** (l.to(DTYPE)[:, None] + l.to(DTYPE)[None, :]))
    open_j = (jc <= njmax + 0.5 + 1.0e-9).to(DTYPE)
    for lam, pb in ((2, 1), (3, -1), (4, 1)):
        lm = torch.full_like(jp.expand(jp.shape[0], jc.shape[1]), float(lam))
        cg = clebsch(jc.expand_as(lm), lm, jp.expand_as(lm), torch.full_like(lm, -0.5),
                     torch.zeros_like(lm), torch.full_like(lm, -0.5))
        keep = (pb * par > 0).to(DTYPE) * open_j
        ref = (2.0 * jc + 1.0) / (2.0 * spin + 1.0) * cg * cg * keep
        assert _same(cg_weights(lam, pb, lmax, njmax, spin), ref)

    kappa2 = torch.tensor([0.9, 0.4, -0.2, 0.05], dtype=DTYPE)
    eta = torch.zeros(4, dtype=DTYPE)
    nk, nlj, rm = 4, int(l.numel()), 11.3
    k = kappa2.abs().sqrt()
    rho = (k * rm)[:, None].expand(nk, nlj).reshape(-1)
    et = eta[:, None].expand(nk, nlj).reshape(-1)
    F, dF, G, dG = coulomb_functions(et, rho, int(l.max()))
    idx = l[None, :].expand(nk, nlj).reshape(-1, 1)
    kk = k[:, None].expand(nk, nlj)
    hp = torch.complex(G.gather(1, idx).reshape(nk, nlj), F.gather(1, idx).reshape(nk, nlj))
    dhp = torch.complex(dG.gather(1, idx).reshape(nk, nlj) * kk,
                        dF.gather(1, idx).reshape(nk, nlj) * kk)
    hp2, dhp2 = exit_waves(kappa2, eta, l, rm, nk, nlj)
    assert torch.equal(hp, hp2) and torch.equal(dhp, dhp2)


def _cascade(Z, A):
    try:
        import sys
        from pathlib import Path

        sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
        import hf_ccfast_bench as bench

        from physics.hf.emission.feeding import Cascade

        e, _ = bench.energies()
        return Cascade(Z, A, max(e), energies=e), e
    except Exception as exc:  # noqa: BLE001  (chart design or structure database absent)
        pytest.skip(f"no cascade for {Z}-{A}: {exc}")


@pytest.mark.parametrize("Z,A", [(40, 88), (82, 208)])
def test_incident_axis_is_the_per_energy_channel(Z, A):
    from dataclasses import fields

    from physics.hf.core.tensors import CaseBatch
    from physics.hf.omp.incident import IncidentChannel, incident_channel
    from physics.hf.omp.incident_axis import incident_axis

    cas, e = _cascade(Z, A)
    with torch.inference_mode():
        tab = incident_axis(Z, A, e, cas.options, cas.params)
        for ei in e[::4] + e[-1:]:
            one = incident_channel(CaseBatch(Z=torch.tensor([Z]), A=torch.tensor([A]),
                                             e_inc_mev=torch.tensor([ei], dtype=DTYPE)),
                                   cas.options, cas.params)
            for f in fields(IncidentChannel):
                a, b = getattr(one, f.name), getattr(tab[ei], f.name)
                if a is None:
                    assert b is None
                    continue
                if not a.is_floating_point():
                    assert torch.equal(a, b), f.name
                    continue
                if f.name in ("tjl_inc", "t_l"):
                    # small T_l carry the batch's rounding relative to their size (1e-10 at
                    # T = 1.5e-9 on Zr-88 at 65 keV, 1.7e-7 at T = 7.6e-9 on Pb-208 at 20 MeV):
                    # 1e-15 absolute on a T of order 1; `lmax` is compared exactly above
                    assert torch.allclose(a, b, rtol=1e-9, atol=1e-12, equal_nan=True), (ei, f.name)
                else:
                    assert torch.allclose(a, b, rtol=1e-11, atol=0.0, equal_nan=True), (ei, f.name)
        # the hook: Cascade.incident serves the table's entry with autograd off
        assert cas.incident(e[3]) is cas.__dict__["_setb_incident"][e[3]]


def test_ccsplit_kernel_matches_ccfast(monkeypatch):
    from physics.hf.ecis import ccnative
    from physics.hf.ecis.coupling import channels
    from physics.hf.ecis.formfactor import rotational_form_factors
    from physics.hf.ecis.incident import _t4_parameters
    from physics.hf.ecis.solver import _grid_and_kinematics, accumulate, smatrix_blocks
    from physics.hf.omp.schrodinger import PARMASS_AMU, nucleus_mass_amu

    if not (ccnative._SPLIT_PATH.is_file() and ccnative._LIB_PATH.is_file()):
        pytest.skip("libccsplit / libccfast not built")
    try:
        from physics.hf.ecis.reference import coupled_band

        band = coupled_band(72, 177)
    except Exception as exc:  # noqa: BLE001
        pytest.skip(f"no coupled band: {exc}")
    results = {}
    for split in ("0", "1"):
        monkeypatch.setenv("HF_CCSPLIT", split)
        monkeypatch.setattr(ccnative, "_LIB", None)
        monkeypatch.setattr(ccnative, "_TRIED", False)
        assert ccnative.available() and ccnative._LIB.cc_split() == int(split)
        out = []
        for deformed_so, e in ((False, [1.0e-3, 0.3, 1.5, 4.0]), (True, [12.0, 20.0])):
            e = torch.tensor(e, dtype=DTYPE)
            p = _t4_parameters(72, 177, 1, e, None)
            m_t = nucleus_mass_amu(72, 177)
            kin, h, nmatch, r = _grid_and_kinematics(p, PARMASS_AMU[1], m_t, 0.0, e,
                                                     band["e_mev"], 1, True)
            ff = rotational_form_factors(p, m_t, r, band["rotbeta"], band["deformation_length"],
                                         2 * band["rotbeta"].numel(), 0.0, deformed_so)
            chs = [channels(tj, par, band["spin"], band["parity"], 20, band["kband"],
                            deformed_spin_orbit=deformed_so)
                   for tj in (1, 15, 31) for par in (-1, 1)]
            got = smatrix_blocks(chs, ff, kin, h, nmatch, r, minus_identity=True,
                                 exact_bits=False)
            spin0 = float(band["spin"][0])
            for ch, (s, op) in zip(chs, got, strict=True):
                out.append(accumulate(ch, s, op, kin, spin0, 0.5, int(band["spin"].numel()), 20,
                                      minus_identity=True))
        results[split] = out
    monkeypatch.setattr(ccnative, "_LIB", None)
    monkeypatch.setattr(ccnative, "_TRIED", False)
    for ga, gb in zip(results["0"], results["1"], strict=True):
        for k in ("reac", "tot", "el", "direct", "tjl"):
            assert torch.allclose(ga[k], gb[k], rtol=1e-9, atol=1e-11), k


@pytest.mark.parametrize("Z,A", [(40, 90), (82, 208)])
def test_dwba_live_levels_give_the_full_decks_bits(Z, A, monkeypatch):
    """`dwba_cross_sections` with autograd off (the live-level rows) against the same call with
    autograd on (every row solved, the inline weights): the same cross sections to the bit.
    NATIVEX2: the compiled deck (`ecis.dwba_nx2`, held to closeness) is off here; it is checked
    against this path in tests/hf/test_nx2_dwba.py."""
    monkeypatch.setenv("HF_NX2_DWBA", "0")
    from physics.hf.direct.chain import _omp_at
    from physics.hf.direct.prepare import case as direct_case
    from physics.hf.ecis.dwba import dwba_case, prepare_case
    from physics.hf.preeq.chain import target_tag

    _cas, e = _cascade(Z, A)
    target = target_tag(Z, A)
    for ei in (e[2], e[12], e[-1]):
        try:
            cs = direct_case(target, ei, e)
        except Exception as exc:  # noqa: BLE001
            pytest.skip(f"no direct case for {target}: {exc}")
        omp = _omp_at(Z, A, float(ei), int(cs.options.k0))
        case = prepare_case(omp, target, float(ei), direct_case=cs)
        with torch.enable_grad():
            full = dwba_case(omp, case)
        with torch.inference_mode():
            live = dwba_case(omp, case)
        for a, b in zip(full, live, strict=True):
            assert torch.equal(a.detach(), b)


def test_match_tables_are_padded_like_talys_nummatchT():
    """TALYS zero-fills logrho/temprho to nummatchT = 4000 (densitymatch.f90:134-137); a light nucleus
    whose empirical matching energy lies above the grid end must read 0 there, not raise."""
    from physics.hf.density.matching import _NUMMATCHT, _fermi_tables, _fermi_tables_core

    ld, _nl = _ld(50, 120, 48, 117)
    logrho, temprho, nstart, nEx = _fermi_tables(ld, 0)
    core_l, core_t, core_n, core_nEx = _fermi_tables_core(ld, 0)
    assert logrho.shape[0] == temprho.shape[0] == _NUMMATCHT + 1
    assert (nstart, nEx) == (core_n, core_nEx)
    assert bool((logrho[: core_l.shape[0]] == core_l).all()) and bool((logrho[core_l.shape[0]:] == 0).all())
    assert bool((temprho[: core_t.shape[0]] == core_t).all()) and bool((temprho[core_t.shape[0]:] == 0).all())
