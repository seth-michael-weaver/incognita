#!/usr/bin/env python3
"""BESTFIT: capture curves from the exact engine with one `INCOGNITA_TALYS_FIT` arm.

    .venv/bin/python scripts/bestfit/engine_curves.py --arm tendl --out bestfit_scratch/tendl \
        --cpus 0-5 --only 79-197,69-169 --cc-cache ~/.cache/incognita-cc

One worker per CPU, one torch thread each, one `Cascade` per target on Stage C's 64-point grid
(1 keV .. 20 MeV), `engine_c.run` (C path). Output per target: `<Z>_<A>.npz` with `capture_mb[64]`,
`e_ev[64]`, the arm and the resolved keyword cards (so a table can say what was applied).

INGRED: it also saves the physics ingredients the curves were built FROM -- `ing_*`, from
`physics.hf.ingredients` off the `Cascade` the run just used (theoretical D0 at Sn, s-wave
<Gamma_gamma>, S0/S1/R', the level-density a(Sn), pairing and shift, spin cut-off, Sn, the
ldmodel/strength actually used, and the fission barrier heights and widths per barrier of a
fissile system) -- so a chart arm can be put next to measured D0 / <Gamma_gamma> / S0 without
re-running it. On by default; `--no-ingredients` restores the previous output exactly.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import traceback
from multiprocessing import get_context
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))


def _telemetry(out_dir, **rec) -> None:
    """One JSON line per target / run in the telemetry log (ENGINE_TELEMETRY,
    else next to the output). Current RSS per target makes worker memory growth visible. Never raises."""
    try:
        import resource
        import socket
        d = os.environ.get("ENGINE_TELEMETRY") or ""
        d = d if os.path.isdir(d) else str(out_dir)
        with open("/proc/self/statm") as fh:
            rss_mb = int(fh.read().split()[1]) * os.sysconf("SC_PAGE_SIZE") / 2 ** 20
        rec = {"ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "job": "engine_curves", "host": socket.gethostname(),
               "pid": os.getpid(), "out": str(out_dir), "rss_mb": round(rss_mb, 1),
               "peak_rss_mb": round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024, 1), **rec}
        with open(os.path.join(d, "engine_curves.jsonl"), "a") as fh:
            fh.write(json.dumps(rec, default=str) + "\n")
    except Exception:
        pass
GRID_EV = np.logspace(3.0, np.log10(2e7), 64)


def _worker(cpu: int, jobs, out_dir: str, arm: str, grid_ev, cc_cache: str = "",
            ingredients: bool = True):
    if cc_cache:
        os.environ["INCOGNITA_CC_CACHE"] = cc_cache
    if arm:
        os.environ["INCOGNITA_TALYS_FIT"] = arm
    else:
        os.environ.pop("INCOGNITA_TALYS_FIT", None)
    if hasattr(os, "sched_setaffinity"):
        os.sched_setaffinity(0, {cpu})
    os.environ["OMP_NUM_THREADS"] = "1"
    import torch
    torch.set_num_threads(1)
    from physics.hf import chartrun, warmrun
    from physics.hf.engine import ChainedFull
    from physics.hf.engine_c import run as engine_run
    from physics.hf.ingredients import ingredients as ingredient_dump
    from physics.hf.input import fitlib

    e_mev = tuple(float(np.float32(e)) for e in np.asarray(grid_ev) / 1e6)
    # SPEED50: everything imported so far lives for the whole worker; freezing it takes it out of
    # every later collection (the per-target `gc.collect` in `drop_target_caches` included)
    import gc
    gc.collect()
    gc.freeze()
    # SPEED50C: fewer automatic collections (the engine allocates many short-lived containers;
    # a target's garbage is collected explicitly by `drop_target_caches` anyway)
    gc.set_threshold(50000, 20, 100)
    # SPEED50 CCGPU: with HF_CCGPU=1 the worker takes up to ENGINE_PREFETCH targets at a time, has
    # their coupled-channels radial loops integrated on the GPU first (`ccgpu.plan`), and runs the
    # targets without coupled channels while the GPU works
    from physics.hf.ecis import ccgpu
    prefetch = max(1, int(os.environ.get("ENGINE_PREFETCH", "1")))
    use_gpu = ccgpu.device() is not None
    queue: list = []
    finished = False
    while True:
        if not queue:
            while not finished and len(queue) < prefetch:
                got = jobs.get()
                if got is None:
                    finished = True
                    break
                queue.append(got)
            if not queue:
                if use_gpu:
                    ccgpu.shutdown()
                return
            queue = [t for t in queue
                     if not (Path(out_dir) / f"{t[0]:03d}_{t[1]:03d}.npz").is_file()]
            if use_gpu and queue:
                cc = []
                for t in queue:
                    try:
                        if ccgpu.plan(t[0], t[1], e_mev):
                            cc.append(t)
                    except Exception:  # noqa: BLE001 -- the target then runs the C kernel
                        traceback.print_exc()
                queue = [t for t in queue if t not in cc] + cc
            if not queue:
                continue
        Z, A = queue.pop(0)
        path = Path(out_dir) / f"{Z:03d}_{A:03d}.npz"
        if path.is_file():
            continue
        if use_gpu:
            ccgpu.restore(Z, A)
        t0, w0, status = time.process_time(), time.perf_counter(), "ok"
        try:
            cas = warmrun.new_cascade(Z, A, e_mev)
            with torch.inference_mode():
                res = engine_run(injection=ChainedFull(Z=Z, A=A, declared_energies=e_mev,
                                                       cascade=cas))
            xs = res.channels_mb["xs000000"].detach().cpu().numpy().astype(float)
            c = fitlib.active()
            cards = "" if c is None else json.dumps(
                {"options": list(c.options), "cells": [list(x[:4]) for x in c.cells],
                 "particles": [list(x) for x in c.particles],
                 "globals": [list(x) for x in c.globals_],
                 "skipped": [list(x) for x in c.skipped], "source": list(c.source)})
            # everything the run computed anyway: every exclusive channel (ch_xs<npdtha>) and the totals, for v1 and as features
            extra = {"ch_" + k: v.detach().cpu().numpy().astype(np.float32) for k, v in res.channels_mb.items()}
            tm = getattr(res, "totals_mb", None)
            if isinstance(tm, dict):
                extra.update({"tot_" + str(k): v.detach().cpu().numpy().astype(np.float32) for k, v in tm.items() if hasattr(v, "detach")})
            # discrete-level inelastic (lv_<channel>.Lnn) and residual production (rp<ZZZ><AAA>), non-zero only:
            # the observables that might still constrain 1-10 MeV capture (OFFLINE-2026-09-20, 16b warning)
            for pre, dd in (("lv_", getattr(res, "levels_mb", None)), ("", getattr(res, "residual_production_mb", None))):
                if isinstance(dd, dict):
                    for k, v in dd.items():
                        if hasattr(v, "detach"):
                            a = v.detach().cpu().numpy().astype(np.float32)
                            if np.any(a > 0):
                                extra[pre + str(k)] = a
            # INGRED: the physics ingredients behind those curves, read off the Cascade the run
            # used (cache hits: nothing about the reaction is recomputed). A failure here must not
            # cost the curves, so it is recorded next to them and the target still lands.
            if ingredients:
                t_ing = time.process_time()
                try:
                    extra.update(ingredient_dump(cas, res))
                except Exception as exc:
                    with open(Path(out_dir) / f"ingerr_{Z:03d}_{A:03d}.txt", "w") as fh:
                        fh.write(f"{type(exc).__name__}: {exc}\n{traceback.format_exc()}")
                extra["ing_cpu_s"] = time.process_time() - t_ing
            np.savez(path, capture_mb=xs, e_ev=np.asarray(grid_ev, float), arm=arm,
                     cards=cards, cpu_s=time.process_time() - t0, **extra)
        except Exception as exc:
            status = type(exc).__name__
            with open(Path(out_dir) / f"err_{Z:03d}_{A:03d}.txt", "w") as fh:
                fh.write(f"{type(exc).__name__}: {exc}\n{traceback.format_exc()}")
        cas = None
        chartrun.drop_target_caches()
        # SPEED50C: what survives the drop lives for the worker (modules imported on the way, the
        # KEEP caches): freeze it too, so the next target's collections skip it
        gc.freeze()
        if use_gpu:
            ccgpu.forget(Z, A)
        _telemetry(out_dir, kind="target", item=f"{Z}-{A}", status=status, cpu=cpu, arm=arm, n_energies=len(e_mev),
                   wall_s=round(time.perf_counter() - w0, 2), cpu_self_s=round(time.process_time() - t0, 2))


def targets() -> list[tuple[int, int]]:
    from models.stage_c_data import curated_nuclides
    return [(z, z + n) for z, n, _ in curated_nuclides(26, 92)]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", default="", help="INCOGNITA_TALYS_FIT value ('' = off)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--e1", default="auto", help="E1-width constant where TALYS's globalwtable table applies: 'auto' (default) = "
                    "INCOGNITA's shipped 1.0425 for --arm nodata (the shipped no-data recipe) and TALYS's table otherwise; "
                    "'incognita', 'stock' (TALYS's table: 1.076 / 1.081, the mean of TENDL's fits), or a number. "
                    "An already-set INCOGNITA_E1_WTABLE wins.")
    ap.add_argument("--cpus", default="0-5")
    ap.add_argument("--only", default="", help="Z-A,Z-A,...")
    ap.add_argument("--grid", default="stagec", help="stagec | a json file of eV values")
    ap.add_argument("--cc-cache", default="", help="CCCACHE: directory for the coupled-channels "
                    "disk cache (sets INCOGNITA_CC_CACHE in every worker); '' = off")
    ap.add_argument("--no-ingredients", dest="ingredients", action="store_false",
                    help="INGRED: do not save the `ing_*` physics ingredients (on by default)")
    a = ap.parse_args()
    from physics.hf.gamma.e1_width import ENV as E1_ENV, resolve as e1_resolve
    if E1_ENV not in os.environ and e1_resolve(a.arm, a.e1):
        os.environ[E1_ENV] = e1_resolve(a.arm, a.e1)
    print(f"E1 width: {os.environ.get(E1_ENV) or 'TALYS table (stock)'}", flush=True)
    lo, hi = (int(x) for x in a.cpus.split("-"))
    cpus = list(range(lo, hi + 1))
    grid = GRID_EV if a.grid == "stagec" else np.asarray(json.loads(Path(a.grid).read_text()),
                                                         float)
    tg = ([tuple(int(x) for x in s.split("-")) for s in a.only.split(",")] if a.only
          else targets())
    Path(a.out).mkdir(parents=True, exist_ok=True)
    ctx = get_context("spawn")
    q = ctx.Queue()
    for Z, A in sorted(tg, key=lambda t: -t[1]):  # heaviest (actinides) first
        q.put((Z, A))
    for _ in cpus:
        q.put(None)
    t0 = time.time()
    procs = [ctx.Process(target=_worker,
                         args=(c, q, a.out, a.arm, grid, a.cc_cache, a.ingredients))
             for c in cpus]
    for p in procs:
        p.start()
    for p in procs:
        p.join()
    done = len(list(Path(a.out).glob("*.npz")))
    print(f"{done}/{len(tg)} targets in {time.time() - t0:.0f}s -> {a.out}")
    _telemetry(a.out, kind="run", arm=a.arm, cpus=a.cpus, n_targets=len(tg), n_done=done, n_energies=len(grid),
               wall_s=round(time.time() - t0, 1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
