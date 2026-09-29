"""GPUFULL: the dump-free ChainedFull channel set on the (nuclide, energy) batch axis gives the CPU
engine's numbers.

`physics.hf.gpu_full_setup` extracts, per nuclide, everything a dump-free run computes that does
not read a population; `physics.hf.gpu_full` (+ `_cascade`, `_channels`) computes the rest for a
whole batch of runs at once. Summation order differs from the CPU reductions, so the check is a
relative tolerance, not bitwise. GPU3 runs the heavy contractions in float32 (gate G-GPU3,
docs/results/hf-gpu3.md: gate channels within 1e-5, every cell within 1e-4), so the checks
against the CPU engine use those bounds (`_TOL`); the float64 arrangements are checked against
each other at 1e-12. The batch path runs on CUDA when there is a device and on CPU otherwise.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
import torch

REPO = Path(__file__).resolve().parents[2]
SWEEP = tuple(float(e) for e in np.logspace(np.log10(1e-3), np.log10(20.0), 20))


def _structure_present() -> bool:
    from physics.hf.core.constants import talys_structure_path

    try:
        return Path(talys_structure_path(None)).is_dir()
    except Exception:
        return False


pytestmark = pytest.mark.skipif(not _structure_present(), reason="TALYS structure data absent")


def _device():
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


GATE = {"xs000000", "xs010000", "xs000001", "xs100000"}


def _tol(k: str) -> float:
    """G-GPU3's bound for channel `k` (GPU3: loosened from GPUFULL's 1e-10)."""
    return 1.0e-5 if k in GATE else 1.0e-4


def _rel(a: float, b: float) -> float:
    m = max(abs(a), abs(b))
    return 0.0 if m == 0.0 else abs(a - b) / m


@pytest.fixture(scope="module")
def fe56():
    from physics.hf.gpu_full_setup import setup_nuclide

    return setup_nuclide(26, 56, SWEEP)


def test_photon_transmission_packing_round_trips():
    from physics.hf.gpu_full_setup import pack_tg, unpack_tg

    rng = np.random.default_rng(0)
    bins = np.array([9, 7, 4, 1])
    tg = rng.random((4, 2, 10, 3))
    tg[..., 0] = 0.0
    tg *= (np.arange(10)[None, None, :, None] < bins[:, None, None, None])
    assert np.array_equal(unpack_tg(pack_tg(tg, bins), bins), tg)
    bad = tg.copy()
    bad[3, 0, 5, 1] = 1.0  # above the mother bin
    with pytest.raises(ValueError):
        pack_tg(bad, bins)


@pytest.mark.parametrize("eidx", [(0, 13, 17, 19)])
def test_every_channel_matches_the_cpu_engine(fe56, eidx):
    """Fe-56 at 1 keV (width fluctuations), 0.88 MeV, 7.05 MeV (width fluctuations, every binary
    channel open) and 20 MeV (multiple pre-equilibrium), as one run over those four energies."""
    from physics.hf import engine
    from physics.hf.gpu_full import run_batch

    sub = tuple(float(np.float32(SWEEP[i])) for i in eidx)
    cpu = engine.run(injection=engine.ChainedFull(
        Z=26, A=56, declared_energies=SWEEP, energies=sub, trim_batches=False))
    out = run_batch([(fe56, i) for i in eidx], _device())
    ref = {k: v.numpy() for k, v in cpu.channels_mb.items()}
    ref.update({k: cpu.totals_mb[k].numpy() for k in ("total", "elastic", "nonelastic")})
    keys = set(ref) | {k for k in out if not k.startswith("_")}
    n = 0
    for k in sorted(keys):
        g = out[k].cpu().numpy() if k in out else np.zeros(len(eidx))
        c = ref.get(k, np.zeros(len(eidx)))
        for j in range(len(eidx)):
            assert _rel(float(g[j]), float(c[j])) <= _tol(k), (k, eidx[j], g[j], c[j])
            n += int(g[j] != 0.0 or c[j] != 0.0)
    assert n >= 30
    assert float(out["xs200000"][3].cpu()) > 100.0  # (n,2n) is open at 20 MeV


def test_trapped_leftover_reaches_the_exclusive_channels():
    """GPUINT: CHARTFIX's compound.f90:404-419 on the batch axis. Eu-147 at 8 keV puts 990 of the
    3042 mb populating Eu-148 in one bin with no open exit; that flux reaches the levels' xspopex
    and feedexcl, so capture is the CPU engine's and not 0.734 of it."""
    from physics.hf import engine
    from physics.hf.gpu_full import run_batch
    from physics.hf.gpu_full_setup import setup_nuclide

    grid = (0.001, 0.008044147)
    cpu = engine.run(injection=engine.ChainedFull(Z=63, A=147, declared_energies=grid))
    out = run_batch([(setup_nuclide(63, 147, grid), i) for i in range(2)], _device())
    for k in ("xs000000", "total", "nonelastic"):
        ref = cpu.channels_mb[k] if k in cpu.channels_mb else cpu.totals_mb[k]
        for j in range(2):
            assert _rel(float(out[k][j].cpu()), float(ref[j])) <= _tol(k), (k, j)


def test_channels_carry_chanopen_across_batches(fe56):
    """channels.f90's `chanopen` crosses incident energies: two batches (low energies, then
    high ones) give the numbers of one batch over all of them."""
    from physics.hf.gpu_full import run_batch

    eidx = (15, 16, 17, 18)
    dev = _device()
    whole = run_batch([(fe56, i) for i in eidx], dev)
    state: dict = {}
    first = run_batch([(fe56, i) for i in eidx[:2]], dev, state)
    second = run_batch([(fe56, i) for i in eidx[2:]], dev, state)
    for k in whole:
        if k.startswith("_"):
            continue
        a = whole[k].cpu().numpy()
        b = np.concatenate([
            first[k].cpu().numpy() if k in first else np.zeros(2),
            second[k].cpu().numpy() if k in second else np.zeros(2)])
        for j in range(4):
            # GPU3: the two batches group comptarget's float32 Moldauer terms differently
            assert _rel(float(a[j]), float(b[j])) <= 1.0e-6, (k, j)


def test_duplicate_gamma_branches_record_the_later_one():
    """Ce-135's level 5 branches twice to level 2: the populations take both intensities and
    `feedexcl` (a dict keyed by daughter level in `gamma_cascade`) only the later one, which moves
    the capture cross section by 3% when both are recorded."""
    from physics.hf import engine
    from physics.hf.gpu_full import run_batch
    from physics.hf.gpu_full_setup import setup_nuclide

    run = setup_nuclide(58, 134, SWEEP)
    eidx = (0, 14)
    sub = tuple(float(np.float32(SWEEP[i])) for i in eidx)
    cpu = engine.run(injection=engine.ChainedFull(
        Z=58, A=134, declared_energies=SWEEP, energies=sub, trim_batches=False))
    out = run_batch([(run, i) for i in eidx], _device())
    ref = cpu.channels_mb["xs000000"].numpy()
    for j in range(2):
        assert _rel(float(out["xs000000"][j].cpu()), float(ref[j])) <= _tol("xs000000")


@pytest.mark.skipif(not torch.cuda.is_available(), reason="the CUDA-graph walk needs a device")
def test_fused_kernels_and_graph_walk_match_the_eager_path(fe56, monkeypatch):
    """GPUFULL2: the compiled kernels and the CUDA-graph bin walk give the numbers of the same
    functions run eagerly, step by step (Fe-56 at 1 keV, 7.05 MeV and 20 MeV)."""
    from physics.hf import gpu_full_cascade as C
    from physics.hf import gpu_full_kernels as K
    from physics.hf.gpu_full import run_batch

    eidx = (0, 17, 19)
    dev = torch.device("cuda")
    fast = run_batch([(fe56, i) for i in eidx], dev)
    for name in ("particle_nodes", "particle_rows", "widths_dense32", "photon_widths32",
                 "decay_step32", "gamma_step", "q_table32", "disc_tables", "populate32"):
        monkeypatch.setattr(K, name + "_c", getattr(K, name))
    monkeypatch.setattr(C, "USE_CUDAGRAPH", False)
    slow = run_batch([(fe56, i) for i in eidx], dev)
    keys = {k for k in fast if not k.startswith("_")} | {k for k in slow if not k.startswith("_")}
    assert len(keys) > 10
    for k in keys:
        a = fast[k].cpu().numpy() if k in fast else np.zeros(len(eidx))
        b = slow[k].cpu().numpy() if k in slow else np.zeros(len(eidx))
        for j in range(len(eidx)):
            # GPU3: float32 reductions fused by Inductor round differently from eager ATen
            assert _rel(float(a[j]), float(b[j])) <= 1.0e-5, (k, eidx[j], a[j], b[j])


def test_window_comptarget_matches_the_dense_masks(fe56, monkeypatch):
    """GPU3: comptarget on channel lists with spin-window prefix sums gives the dense-mask
    comptarget's populations (both float64: the Moldauer terms' float32 switched off), Fe-56 at
    1 keV and 7.05 MeV (width fluctuations) and 20 MeV (none)."""
    from physics.hf import gpu_full as G
    from physics.hf import gpu_full_ct as CT

    eidx = (0, 17, 19)
    dev = _device()
    bk = G.pack([(fe56, i) for i in eidx], dev)
    res = G.primary_residuals(bk)
    monkeypatch.setattr(CT, "LOG_F32", False)
    monkeypatch.setattr(CT, "NODE_F32", False)
    monkeypatch.setattr(G, "CT_WINDOWS", True)
    win = G.comptarget(bk, res)
    monkeypatch.setattr(G, "CT_WINDOWS", False)
    dense = G.comptarget(bk, res)
    for k in ("pop", "el", "xsbinary"):
        x, y = win[k].double(), dense[k].double()
        m = torch.maximum(x.abs(), y.abs())
        live = m > 0
        assert bool((live == ((x != 0) | (y != 0))).all())
        assert float(((x - y).abs()[live] / m[live]).max()) <= 1.0e-12, k


def test_sfactor_is_carried_across_energies():
    """GPUC (OPEN4 D): binary.f90's `sfactor` is run-scoped. Pb-208 (n,g) at 20 MeV takes the
    11.88 MeV compound spin shape in bins below popepsA: carried (one batch, or batch to batch
    through the state) it is the CPU engine's; from a fresh state it is 6% off and flagged."""
    from physics.hf import engine
    from physics.hf.gpu_full import run_batch
    from physics.hf.gpu_full_setup import setup_nuclide

    grid = (7.0, 11.875721, 20.0)
    s = setup_nuclide(82, 208, grid)
    cpu = float(engine.run(injection=engine.ChainedFull(
        Z=82, A=208, declared_energies=grid)).channels_mb["xs000000"][2])
    dev = _device()
    whole = run_batch([(s, i) for i in range(3)], dev, {})
    assert whole["_flags"]["sfactor_gaps"] == []
    assert _rel(float(whole["xs000000"][2].cpu()), cpu) <= 1.0e-5
    state: dict = {}
    run_batch([(s, 0), (s, 1)], dev, state)
    split = run_batch([(s, 2)], dev, state)
    assert split["_flags"]["sfactor_gaps"] == []
    assert _rel(float(split["xs000000"][0].cpu()), cpu) <= 1.0e-5
    fresh = run_batch([(s, 2)], dev, {})
    assert fresh["_flags"]["sfactor_gaps"] == [((82, 208), 2)]
    assert _rel(float(fresh["xs000000"][0].cpu()), cpu) > 1.0e-2


def test_anomalous_discrete_levels_follow_the_cpu_engine():
    """GPUC (OPEN3M's A2): Nb-95 has levels whose ENSDF spin range TALYS resolves to a 2J of the
    wrong parity; comptarget's l2prime/2 truncation into them moves (n,g) and the inelastic by up
    to 8% near 1 MeV. The GPU window comptarget follows the CPU engine there."""
    from physics.hf import engine
    from physics.hf.gpu_full import run_batch
    from physics.hf.gpu_full_setup import setup_nuclide

    grid = (0.8780094, 1.476318)
    cpu = engine.run(injection=engine.ChainedFull(Z=41, A=95, declared_energies=grid))
    out = run_batch([(setup_nuclide(41, 95, grid), i) for i in range(2)], _device(), {})
    for k in ("xs000000", "xs100000", "nonelastic"):
        ref = cpu.channels_mb[k] if k in cpu.channels_mb else cpu.totals_mb[k]
        for j in range(2):
            assert _rel(float(out[k][j].cpu()), float(ref[j])) <= _tol(k), (k, j)
