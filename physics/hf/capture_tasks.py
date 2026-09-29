"""The worker side of the sharded capture sweep: one capture task in, one result dict out.

`capture_task` builds a task (the capture cross section `xs000000` [mb] at each requested energy,
NaN out of domain, the domain mask, and with `grad` the Jacobian d xs_i / d theta_j over the
listed T7 `gamma_parameters` override entries); `run_task` evaluates it in a warm worker
(`_warm` is the pool initializer). The multi-host driver that ships these tasks to worker pools
is not part of this distribution; the task format
and its evaluation are, so any pool (a local `multiprocessing.Pool`, a batch scheduler) can
drive them. `capture_gpu_tasks` answers the same tasks in GPU batches.
"""

from __future__ import annotations

import os
import time
import traceback
from pathlib import Path

import numpy as np


def capture_task(Z: int, A: int, energies, overrides: dict | None = None,
                 grad: list | None = None, enincmax: float = 20.0, energy_idx=None,
                 tables: bool = True, impl: str = "lean") -> dict:
    """A capture task (see the module docstring). `overrides` maps T7 names to nested lists;
    `grad` is a list of (name, index tuple) entries of those overrides. `tables`: read the
    host's photon-strength-independent tables for this target when it has them. `impl`:
    "lean" (`capture_fast_batch.capture_xs`) or "reference" (`capture_fast.capture_xs`)."""
    t = {"fn": "capture", "Z": int(Z), "A": int(A),
         "energies": [float(e) for e in energies], "enincmax": float(enincmax),
         "tables": bool(tables), "impl": impl}
    if overrides:
        t["overrides"] = {k: np.asarray(v, dtype=np.float64).tolist() for k, v in overrides.items()}
    if grad:
        t["grad"] = [[name, list(idx)] for name, idx in grad]
    if energy_idx is not None:
        t["energy_idx"] = [int(i) for i in energy_idx]
    return t


def _warm(ready=None) -> None:
    """Worker initializer: one thread, the port imported, one capture evaluated (so module-level
    tables and the autograd engine are up before the first real task)."""
    os.environ["OMP_NUM_THREADS"] = "1"
    try:
        import torch

        torch.set_num_threads(1)
        from physics.hf import capture_fast as CF  # noqa: F401
        from physics.hf.compound import chain, target  # noqa: F401
        from physics.hf.ecis import incident  # noqa: F401
        from physics.hf.emission import feeding, multiple  # noqa: F401

        tg = CF.target(26, 56, 20.0)
        CF.capture_xs(tg, 0.001)
    except BaseException:
        if ready is not None:
            ready.abort()  # the server sees a broken barrier and exits instead of respawning
        raise
    if ready is not None:
        ready.wait()


def run_task(task: dict) -> dict:
    """Evaluate one task in a warm worker. With `task["profile"]` the result carries the
    task's cProfile stats (marshalled, base64) for aggregation by the driver."""
    if task.get("profile"):
        import base64
        import cProfile
        import marshal
        import pstats

        pr = cProfile.Profile()
        pr.enable()
        out = run_task({**task, "profile": False})
        pr.disable()
        st = pstats.Stats(pr)
        out["pstats"] = base64.b64encode(marshal.dumps(st.stats)).decode()
        return out
    import torch

    t0 = time.perf_counter()
    from physics.hf import capture_fast as CF
    from physics.hf import capture_fast_batch as CB

    if task.get("fn") == "tables":
        return _build_tables(task, t0)
    energies = task["energies"]
    idx = task.get("energy_idx") or list(range(len(energies)))
    xs = [float("nan")] * len(idx)
    dom = [False] * len(idx)
    jac = None
    err = ""
    used_tables = False
    capture = CF.capture_xs if task.get("impl") == "reference" else CB.capture_xs
    try:
        overrides, theta = None, None
        if task.get("overrides"):
            overrides = {k: torch.tensor(v, dtype=torch.float64)
                         for k, v in task["overrides"].items()}
        if task.get("grad"):
            theta = torch.tensor([float(overrides[n][tuple(i)]) for n, i in task["grad"]],
                                 dtype=torch.float64, requires_grad=True)
            for j, (n, i) in enumerate(task["grad"]):
                mask = torch.zeros_like(overrides[n])
                mask[tuple(i)] = 1.0
                overrides[n] = overrides[n] * (1.0 - mask) + theta[j] * mask
            jac = [[float("nan")] * len(task["grad"]) for _ in idx]
        tg = CF.target(task["Z"], task["A"], task.get("enincmax", 20.0),
                       gamma_overrides=overrides)
        if task.get("tables"):
            path = _table_path(task["Z"], task["A"])
            if path.exists():
                CB.install_tables(tg, torch.load(path, weights_only=False))
                used_tables = True
        for k, i in enumerate(idx):
            e = float(energies[i])
            dom[k] = CF.in_domain(tg, e)
            if not dom[k]:
                continue
            if theta is None:
                xs[k] = capture(tg, e)
            else:
                v = capture(tg, e, differentiable=True)
                xs[k] = float(v)
                (g,) = torch.autograd.grad(v, theta, retain_graph=True)
                jac[k] = g.tolist()
    except Exception as exc:  # recorded per task, never silently dropped
        err = f"{type(exc).__name__}: {exc}"[:300] + " | " + traceback.format_exc(limit=3)[-300:]
    finally:
        CB.forget_tables()
    return {"Z": task["Z"], "A": task["A"], "energy_idx": idx, "xs": xs, "domain": dom,
            "jac": jac, "seconds": time.perf_counter() - t0, "err": err,
            "tables": used_tables}


def _table_path(Z: int, A: int) -> Path:
    """This host's table file for (Z, A); the driver sets NUC_SHARD_TABLES per host."""
    return Path(os.path.expanduser(os.environ["NUC_SHARD_TABLES"])) / f"{Z}-{A}.pt"


def _build_tables(task: dict, t0: float) -> dict:
    """Worker side of `tables`: the photon-strength-independent tables of one target
    (`capture_fast_batch.tables`), written atomically to the host's table directory."""
    import torch

    from physics.hf import capture_fast as CF
    from physics.hf import capture_fast_batch as CB

    err, size = "", 0
    try:
        tg = CF.target(task["Z"], task["A"], task.get("enincmax", 20.0))
        tab = CB.tables(tg, task["energies"])
        path = _table_path(task["Z"], task["A"])
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(f".tmp{os.getpid()}")
        torch.save(tab, tmp)
        os.replace(tmp, path)
        size = path.stat().st_size
    except Exception as exc:
        err = f"{type(exc).__name__}: {exc}"[:300]
    return {"Z": task["Z"], "A": task["A"], "seconds": time.perf_counter() - t0, "err": err,
            "bytes": size}
