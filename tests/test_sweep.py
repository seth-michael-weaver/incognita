"""Sweep design + a tiny end-to-end TALYS sweep (skipped without the binary; < 60 s)."""

from __future__ import annotations

import time

import numpy as np
import pytest

from physics.talys import params as P
from physics.talys import sweep as S
from physics.talys.nuclides import select_nuclides
from physics.talys.runner import talys_available


def test_lhs_design_is_deterministic_and_in_bounds():
    d1 = S.lhs_design(5, 7, seed=3)
    d2 = S.lhs_design(5, 7, seed=3)
    assert d1.shape == (35, P.N_PARAMS)
    assert np.array_equal(d1, d2)
    lo, hi = P.coded_bounds()
    assert (d1 >= lo).all() and (d1 <= hi).all()
    # Latin property: each 1-d marginal has one point per stratum
    u = (d1[:, 1] - lo[1]) / (hi[1] - lo[1])
    assert len(np.unique(np.floor(u * 35).astype(int))) == 35
    assert not np.array_equal(d1, S.lhs_design(5, 7, seed=4))


def test_task_sharding_partitions_work():
    cfg = S.load_config(None, ["n_samples=3", "n_shards=3"])
    nucs = select_nuclides(z_min=26, z_max=30, z_step=2, n_rich=0)
    all_tasks = set()
    for k in range(3):
        cfg.shard_index = k
        t = S.build_tasks(cfg, nucs)
        assert not (all_tasks & set(t))
        all_tasks |= set(t)
    assert len(all_tasks) == len(nucs) * 4  # default + 3 samples


@pytest.mark.needs_data("staging/nuclides.parquet")  # the fallback has no Sn, fewer stables
def test_nuclide_selection_stratified_and_sn():
    nucs = select_nuclides(z_min=26, z_max=92, z_step=2, n_rich=6)
    zs = [n.Z for n in nucs[:34]]
    assert zs == list(range(26, 93, 2))
    keys = {n.key for n in nucs}
    assert "Z026A056" in keys and "Z082A206" in keys and "Z092A238" in keys
    assert len(nucs) == 40
    fe = next(n for n in nucs if n.key == "Z026A056")
    assert 7600 < fe.sn_cn_kev < 7700  # Sn(57Fe) = 7646 keV


@pytest.mark.skipif(not talys_available(), reason="TALYS binary not installed")
def test_end_to_end_sweep_two_nuclides_three_samples(tmp_path):
    cfg = S.load_config(
        None,
        [
            f"out_dir={tmp_path}",
            "n_samples=3",
            "nuclides.z_min=26",
            "nuclides.z_max=40",
            "nuclides.z_step=14",
            "nuclides.n_rich=0",
            "energies.n=3",
            "shard_size=4",
            "timeout_s=120",
        ],
    )
    summary = S.run_sweep(cfg, log=lambda *_: None)
    assert summary["runs_completed_now"] == 8
    assert summary["runs_error"] == 0, summary
    df = S.load_sweep(tmp_path)
    assert df.height == 8
    assert set(df["sample_id"].to_list()) == {0, 1, 2, 3}
    assert (df["status"] == "ok").all()
    assert df["talys_version"][0].startswith("TALYS-")
    cap = np.array(df.filter(df["sample_id"] == 0)["log10_xs_capture"].to_list())
    assert np.isfinite(cap).all() and cap.shape == (2, 3)
    # capture falls with energy for the default run
    assert (np.diff(cap, axis=1) < 0).all()
    # resume: nothing left to do
    again = S.run_sweep(cfg, log=lambda *_: None)
    assert again["runs_completed_now"] == 0 and again["runs_previously_done"] == 8
    p = S.consolidate(tmp_path)
    assert p.is_file()


def test_stop_pool_terminates_workers_and_survives_shutdown_clearing_processes():
    # A SIGTERM mid-sweep used to raise here instead of stopping cleanly: shutdown() sets
    # ProcessPoolExecutor._processes to None, so reading the handles afterwards blew up and
    # the run exited non-zero with no summary written and the workers left to die on their own.
    from concurrent.futures import ProcessPoolExecutor

    ex = ProcessPoolExecutor(max_workers=2)
    futures = [ex.submit(abs, -1) for _ in range(4)]
    for f in futures:
        f.result()
    procs = list(ex._processes.values())
    assert len(procs) == 2

    n = S.stop_pool(ex, futures)

    assert n == 2, "the worker handles have to be read before shutdown() clears them"
    assert ex._processes is None
    # Poll rather than assert straight after a single join. The executor's own management
    # thread joins these same Process objects concurrently, and Process.join() is not
    # thread-safe: whichever thread loses the race to _popen.wait() can return with
    # returncode still unwritten, so exitcode reads None for a moment on a worker that has
    # in fact been signalled and is already dead. Asserting on that instant failed 7 runs in
    # 20 while stop_pool was behaving correctly every time -- the workers always reached
    # exitcode -15 within a fraction of a second.
    deadline = time.monotonic() + 30
    for p in procs:
        while p.exitcode is None and time.monotonic() < deadline:
            p.join(timeout=0.2)
        assert p.exitcode is not None, "worker was never signalled"


def test_write_input_rejects_non_ascending_energies(tmp_path):
    # TALYS truncates the run at the first descent in the energy file and still exits zero with
    # its success banner, so a short result looks like a clean one. write_input refuses instead.
    # Sorting would be worse than raising: callers index the returned arrays by the order they
    # passed in, so a quiet reorder trades a silent truncation for a silent misalignment.
    from physics.talys.runner import write_input

    ok = write_input(tmp_path, 26, 56, [1.0, 2.0, 3.0])
    assert ok.is_file()
    assert (tmp_path / "energies").read_text().split() == ["1.000000E+00", "2.000000E+00",
                                                           "3.000000E+00"]
    for bad in ([3.0, 2.0, 1.0], [1.0, 3.0, 2.0], [1.0, 1.0, 2.0]):
        with pytest.raises(ValueError, match="strictly ascend"):
            write_input(tmp_path, 26, 56, bad)


def test_sweep_channels_satisfy_the_total_cross_section_sum_rule():
    """The extracted partials must add up to the extracted total.

    Every channel in the corpus comes from parsing a different TALYS output file, keyed by
    filename (`xs*.tot`). Nothing downstream would notice if one of those keys picked up the
    wrong file: a surrogate trained on capture that is really inelastic converges perfectly
    well and is wrong everywhere, and no shape or range check would flag it because both are
    cross sections of similar magnitude over the same grid.

    The sum rule catches exactly that, because it is a relation BETWEEN the channels. Neutron
    total is the sum of elastic and every non-elastic channel, so the six partials we extract
    must account for essentially all of it and never exceed it. Measured here: median ratio
    0.9999, p99 1.0009, with 0.045% of cells above 1.01 and a maximum of 1.0275 -- consistent
    with the precision TALYS prints, not with a mis-mapped channel, which would show as a ratio
    off by a factor rather than by a rounding.
    """
    import pathlib

    import polars as pl

    from physics.talys.sweep import load_sweep

    corpus = (pathlib.Path(__file__).resolve().parents[1]
              / "features" / "talys_sweep_merged2")
    if not (corpus / "shards").exists():
        pytest.skip("merged TALYS corpus not present in this checkout")
    d = load_sweep(corpus).filter(pl.col("status") == "ok").head(2000)

    total = 10 ** np.array(d["log10_xs_total"].to_list(), dtype=float)
    partials = np.zeros_like(total)
    for c in ("log10_xs_elastic", "log10_xs_capture", "log10_xs_inelastic",
              "log10_xs_n2n", "log10_xs_np", "log10_xs_na"):
        partials += np.nan_to_num(10 ** np.array(d[c].to_list(), dtype=float), nan=0.0)

    ok = np.isfinite(total) & (total > 0)
    assert ok.sum() > 1000, "not enough finite cells to test the sum rule"
    ratio = partials[ok] / total[ok]
    assert 0.98 < np.median(ratio) < 1.01, (
        f"partials account for {np.median(ratio):.4f} of the total; a channel is mis-mapped"
    )
    over = float((ratio > 1.01).mean())
    assert over < 0.01, f"{over:.2%} of cells have partials exceeding the total by over 1%"


def test_write_input_gnorm_gets_gamgam_in_ev(tmp_path):
    # GNORMFIX: stock TALYS normalises `gnorm y` to the resonance table's keV number read as eV
    # (C/E Gamma_gamma 1546 for I-130). write_input supplies the compound nucleus's width in eV.
    from physics.talys.runner import resonance_gamgam_ev, talys_dir, write_input

    if not (talys_dir() / "structure" / "resonances" / "Au.res").is_file():
        pytest.skip("TALYS structure database not available")
    assert resonance_gamgam_ev(79, 198) == pytest.approx(0.128)  # Au198 1.28e-4 keV
    assert resonance_gamgam_ev(53, 130) == pytest.approx(0.087)

    def kw(extra):
        text = write_input(tmp_path, 53, 129, [0.001, 0.01], extra).read_text()
        return [ln for ln in text.splitlines() if ln.startswith(("gnorm", "gamgam"))]

    assert kw({"gnorm": "y"}) == ["gnorm y", "gamgam 53 130 0.087"]
    assert kw({"gnorm": "y", "gamgam": "53 130 0.05"}) == ["gnorm y", "gamgam 53 130 0.05"]
    assert kw({"gnorm": "y", "gamgamadjust": "53 130 0.5"}) == [  # TALYS multiplies it on
        "gnorm y", "gamgamadjust 53 130 0.5", "gamgam 53 130 0.087"]
    assert kw({"gnorm": "n"}) == ["gnorm n"]
    assert kw({}) == []


def test_radwidtheory_refuses_kev_gamgam():
    import torch

    from physics.hf.gamma.transmission import radwidtheory

    with pytest.raises(ValueError, match="keV"):
        radwidtheory(None, 0.0, 6.5, torch.zeros(1), torch.zeros(1), torch.ones(1), 0.5, 1,
                     lambda ex, j, p: None, 20.0, flaggnorm=True, gamgam_exp_ev=8.7e-5)
