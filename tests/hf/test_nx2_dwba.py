"""NATIVEX2 lever `dwba`: `ecis.dwba_nx2.case_cross_sections` (the compiled DWBA deck) against
`ecis.dwba.dwba_case` with the lever off, on the chained direct cases of a few targets and energies.
Skipped without a `libnx2` build (scripts/build_nx2_native.sh)."""

from __future__ import annotations

import numpy as np
import pytest
import torch

from physics.hf.native import nx2
from tests._data import BROAD_DESIGN, need_data

pytestmark = pytest.mark.skipif(nx2.lib() is None, reason="no libnx2 build")


def _close(a, b, rel=1e-10, floor=1e-14):
    a, b = np.asarray(a, float), np.asarray(b, float)
    assert a.shape == b.shape
    scale = np.maximum(np.abs(a), np.abs(b))
    bad = np.abs(a - b) > rel * scale + floor
    assert not bad.any(), (np.argwhere(bad)[:5], a[bad][:5], b[bad][:5])


def _energies():
    need_data(BROAD_DESIGN)  # the 20-point grid comes from the sweep design
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
    import hf_ccfast_bench as bench

    return tuple(bench.energies()[0])


@pytest.mark.parametrize("Z,A", [(40, 90), (82, 208), (50, 120), (71, 175)])
def test_compiled_deck_matches_dwba_case(Z, A, monkeypatch):
    from physics.hf.direct.chain import _omp_at
    from physics.hf.direct.prepare import case as direct_case
    from physics.hf.ecis import dwba_nx2
    from physics.hf.ecis.dwba import dwba_case, prepare_case
    from physics.hf.preeq.chain import target_tag

    e = _energies()
    target = target_tag(Z, A)
    solved = 0
    for ei in (e[2], e[8], e[12], e[-1]):
        try:
            cs = direct_case(target, ei, e)
        except Exception as exc:  # noqa: BLE001
            pytest.skip(f"no direct case for {target}: {exc}")
        omp = _omp_at(Z, A, float(ei), int(cs.options.k0))
        case = prepare_case(omp, target, float(ei), direct_case=cs)
        with torch.inference_mode():
            got = dwba_nx2.case_cross_sections(omp, case)
            monkeypatch.setenv("HF_NX2_DWBA", "0")
            ref = dwba_case(omp, case)
            monkeypatch.delenv("HF_NX2_DWBA")
        assert got is not None
        for a, b in zip(got, ref, strict=True):
            _close(a, b)
        solved += int((ref[0] > 0).sum()) + int((ref[1] > 0).sum())
    assert solved > 0


def test_charged_exit_waves_path_matches(monkeypatch):
    """A proton deck: the Coulomb functions come from `dwba_setb.exit_waves`, not the kernel."""
    from physics.hf.direct.chain import _omp_at
    from physics.hf.direct.prepare import case as direct_case
    from physics.hf.ecis import dwba_nx2
    from physics.hf.ecis.dwba import dwba_case, prepare_case
    from physics.hf.preeq.chain import target_tag

    e = _energies()
    Z, A = 40, 90
    target = target_tag(Z, A)
    ei = e[-1]
    cs = direct_case(target, ei, e)
    omp = _omp_at(Z, A, float(ei), int(cs.options.k0))
    case = prepare_case(omp, target, float(ei), direct_case=cs)
    with torch.inference_mode():
        got = dwba_nx2.case_cross_sections(omp, case, particle=2)
        monkeypatch.setenv("HF_NX2_DWBA", "0")
        ref = dwba_case(omp, case, particle=2)
    assert got is not None
    assert float(ref[0].sum()) > 0.0
    for a, b in zip(got, ref, strict=True):
        _close(a, b, rel=1e-9)


@pytest.mark.parametrize("Z,A", [(26, 54), (82, 208)])
def test_numpy_scalars_match_their_torch_functions(Z, A):
    """`_card_value`, `_kinematics`, `_grid` and `_potential` against `ecis_card_value`,
    `channel_kinematics`, `ecis_grid`, `optical_potential` and `derivative_form_factor`."""
    from physics.hf.direct.chain import _omp_at
    from physics.hf.ecis import dwba_nx2 as X
    from physics.hf.ecis.formfactor import DWBA_PARTS, derivative_form_factor
    from physics.hf.ecis.solver import channel_kinematics
    from physics.hf.omp import schrodinger as S

    DT = torch.float64
    vals = np.array([0.0, 1.0e-3, 0.0123456789, 3.14159265, 55.123456789, 1234.5678, -2.5e4])
    ref = S.ecis_card_value(torch.tensor(vals, dtype=DT)).numpy()
    _close(X._card_value(vals), ref, rel=1e-15, floor=0.0)
    for e in (0.00123456, 0.0999999, 14.123456789, 150.0):
        assert X._card_energy(e) == float(S.ecis_card_energy(torch.tensor([e], dtype=DT))[0])

    m1, m2 = X._masses(Z, A, 1, True)
    e_lev = np.array([0.0, 0.8467, 2.1, 9.7])
    for e_lab, z in ((1.4, 0.0), (14.0, 0.0), (60.0, float(Z))):
        kin = channel_kinematics(torch.tensor([e_lab], dtype=DT), m1, m2, z,
                                 torch.tensor(np.concatenate([[0.0], e_lev]), dtype=DT))
        k, k2, eta, mu, ecm0 = X._kinematics(e_lab, m1, m2, z, e_lev)
        _close(k, kin.k_fm[0].numpy(), rel=1e-14)
        _close(k2, kin.kappa2[0].numpy(), rel=1e-14)
        _close(eta, kin.eta[0].numpy(), rel=1e-14)
        _close(mu, float(kin.mu_coef[0]), rel=1e-14)
        omp = _omp_at(Z, A, e_lab, 1)
        gk = S.EcisKinematics(ecm_mev=kin.ecm_mev[:, 0], k_fm=kin.k_fm[0, :1],
                              eta=kin.eta[0, :1], mu_coef=kin.mu_coef)
        h_t, ism, _ = S.ecis_grid(omp, m2, gk)
        q = X._omp_row(omp)
        h, n = X._grid(q, m2, float(k[0]), ecm0)
        assert n == int(ism[0])
        _close(h, float(h_t[0]), rel=1e-14)
        r = h / 4 * np.arange(0, 4 * n + 1, dtype=np.float64)
        r[0] = h / 4
        rt = torch.from_numpy(r)
        for dl in (False, True):
            (d_re, d_im), (so_re, so_im), (w_re, w_im) = X._potential(q, m2, r, z, dl, DWBA_PARTS)
            central, so, coul = S.optical_potential(omp, m2, rt, z)
            w = derivative_form_factor(omp, m2, rt, dl, DWBA_PARTS)[0]
            _close(d_re, (central[0].real + coul[0]).numpy(), rel=1e-12, floor=1e-12)
            _close(d_im, central[0].imag.numpy(), rel=1e-12, floor=1e-12)
            _close(so_re, so[0].real.numpy(), rel=1e-12, floor=1e-12)
            _close(so_im, so[0].imag.numpy(), rel=1e-12, floor=1e-12)
            _close(w_re, w.real.numpy(), rel=1e-12, floor=1e-12)
            _close(w_im, w.imag.numpy(), rel=1e-12, floor=1e-12)
