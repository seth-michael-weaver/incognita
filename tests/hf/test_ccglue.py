"""CCGLUE: the coupled-channels stage's Python moved into `ccfast.c`, and the J loop as a task list.

* `ccnative.sixj` (C) gives `coupling.sixj`'s bits on every sextet a coupled-channels target asks for;
* `ccnative.cc_block_acc` (kernel + `cc_match_acc`) gives `_match` + `accumulate`'s contributions;
* `sum_blocks` on the task list equals the `smatrix_blocks` loop (`HF_CCGLUE=0`) to <= 1e-12;
* the tasks are schedulable: one kernel call per (block, energy) gives the grouped call's numbers.
"""

from __future__ import annotations

import pytest
import torch

from physics.hf.core.tensors import DTYPE
from physics.hf.ecis import ccnative

pytestmark = pytest.mark.skipif(not ccnative.glue_available(), reason="libccfast.so not built")


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


def _setup(Z, A, e, lmax=20, deformed_so=False):
    from physics.hf.ecis.formfactor import rotational_form_factors
    from physics.hf.ecis.incident import _t4_parameters
    from physics.hf.ecis.solver import _ChannelMaker, _grid_and_kinematics
    from physics.hf.omp.schrodinger import PARMASS_AMU, nucleus_mass_amu

    band = _band(Z, A)
    p = _t4_parameters(Z, A, 1, e, None)
    m_t = nucleus_mass_amu(Z, A)
    kin, h, nmatch, r = _grid_and_kinematics(p, PARMASS_AMU[1], m_t, 0.0, e, band["e_mev"], 1,
                                             True)
    ff = rotational_form_factors(p, m_t, r, band["rotbeta"], band["deformation_length"],
                                 2 * band["rotbeta"].numel(), 0.0, deformed_so)
    sp, par = band["spin"], band["parity"]
    maker = _ChannelMaker("rot", tuple(sp.tolist()), sp.dtype, tuple(par.tolist()), par.dtype,
                          (float(band["kband"]), bool(deformed_so)), lmax, 0.5)
    return band, maker, ff, kin, h, nmatch, r


def test_c_sixj_is_torch_sixj_to_the_bit():
    from physics.hf.ecis.coupling import sixj

    # every triangle-allowed sextet of small spins, half-integers included, plus violators
    g = torch.Generator().manual_seed(3)
    args = [torch.randint(0, 50, (100_000,), generator=g).to(DTYPE) * 0.5 for _ in range(6)]
    ref = sixj(*args)
    got = ccnative.sixj(args)
    assert int((ref != 0).sum()) > 1000
    assert torch.equal(ref, got)


@pytest.mark.parametrize("deformed_so", [False, True])
def test_task_loop_is_the_smatrix_blocks_loop(deformed_so, monkeypatch):
    from physics.hf.ecis.solver import sum_blocks

    e = torch.tensor([1.0e-3, 1.5, 9.0, 20.0], dtype=DTYPE)
    e = e[2:] if deformed_so else e[:2]
    band, maker, ff, kin, h, nmatch, r = _setup(92, 238, e, deformed_so=deformed_so)
    args = (maker, ff, kin, h, nmatch, r, int(band["spin"].numel()), 20, float(band["spin"][0]),
            0.5)
    with torch.inference_mode():
        monkeypatch.setenv("HF_CCGLUE", "0")
        old = sum_blocks(*args)
        monkeypatch.setenv("HF_CCGLUE", "1")
        new = sum_blocks(*args)
    assert new.n_j == old.n_j
    for k in ("sigma_tot_mb", "sigma_reac_mb", "sigma_abs_mb", "sigma_shape_el_mb",
              "sigma_direct_mb"):
        a, b = getattr(old, k), getattr(new, k)
        assert torch.allclose(a, b, rtol=1e-12, atol=1e-14), k
    # T_lj: relative where it is O(1e-3) or more; below, 1 - sum |S|^2 carries the block's own
    # rounding (a 1.7e-8 T_lj of U-238 at 9 MeV moves by 5e-17 absolute between the two matchings)
    big = old.tjl > 1e-3
    assert torch.allclose(old.tjl[big], new.tjl[big], rtol=1e-11, atol=0)
    assert float((old.tjl - new.tjl)[~big].abs().max()) < 1e-15


def test_tasks_split_per_energy_give_the_grouped_numbers():
    from physics.hf.ecis.solver import cc_tasks, run_cc_tasks

    e = torch.tensor([0.3, 4.0, 12.0], dtype=DTYPE)
    band, maker, ff, kin, h, nmatch, r = _setup(60, 150, e)
    rest = (maker, ff, kin, h, nmatch, r, int(band["spin"].numel()), 20, float(band["spin"][0]),
            0.5)
    with torch.inference_mode():
        tasks = cc_tasks(9, [0, 1, 2])
        grouped = run_cc_tasks(tasks, *rest)
        assert [(tj, par) for tj, par, _r, _g in grouped] == [(9, -1), (9, 1)]
        for tj, par, rows, got in grouped:
            assert rows.tolist() == [0, 1, 2]
            for t in [t for t in tasks if (t.two_j, t.parity) == (tj, par)]:
                ((_tj, _par, one_rows, one),) = run_cc_tasks([t], *rest)
                assert one_rows.tolist() == [t.energy]
                for k in ("reac", "tot", "el", "direct", "tjl"):
                    assert torch.equal(one[k][0], got[k][t.energy]), (tj, par, t.energy, k)
