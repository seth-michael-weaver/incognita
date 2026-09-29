"""`capture_tasks.capture_task`s answered by `capture_gpu` in batches, for a GPU host of
a multi-host worker pool.

Task: SPEEDG (step 6: a `gpu` host type for the multi-host pool). A batch of capture tasks becomes one
padded point axis: each task's photon-strength-independent set-up (`capture_gpu_setup`) is built
once on the host's CPU and cached (in memory and as a pickle), its overrides become theta =
(ftable(E1), wtable(E1), sgr(M1)), and the batch runs through `capture_gpu.forward` (with the
Jacobian when a task asks for one) in chunks sized to the GPU memory the host allows. Results
have `run_task`'s shape and semantics: xs per requested energy (NaN outside the domain), the
domain flags, the Jacobian columns in the task's `grad` order, `err`.

Tasks the GPU path does not cover (another override or gradient entry, a photon-strength model
outside `setup.gamma_pack`'s family, a batch where the rho0 cut could fire) are answered by
`run_task` on the CPU, and say so in `impl`.

Test: SPEEDG / tests/hf/test_capture_gpu.py
"""

from __future__ import annotations

import hashlib
import json
import os
import pickle
import time
from pathlib import Path

import numpy as np

THETA_ENTRIES = {("ftable", (1, 1)): 0, ("wtable", (1, 1)): 1, ("sgr_mb", (0, 1, 1)): 2}
# entries whose value has no effect in the covered model family (only the E1 strength is tabulated)
INERT = ("ftable", "wtable")
BYTES_PER_POINT = {False: 0.45e6, True: 0.95e6}  # measured peaks, with margin (forward, Jacobian)


class NotCovered(ValueError):
    pass


def energies_of(task: dict) -> list[float]:
    idx = task.get("energy_idx") or list(range(len(task["energies"])))
    return [float(task["energies"][i]) for i in idx]


def setup_key(task: dict) -> str:
    h = hashlib.sha256(json.dumps([task["Z"], task["A"], energies_of(task),
                                   float(task.get("enincmax", 20.0)),
                                   bool(task.get("tables", True))]).encode()).hexdigest()[:16]
    return f"{task['Z']}-{task['A']}-{h}"


def theta_of(task: dict, gamma: dict) -> list[float]:
    """theta at the task's overrides (TALYS's defaults where it gives none)."""
    th = [gamma["ftable"], gamma["wtable"], gamma["m1"][0]]
    for name, arr in (task.get("overrides") or {}).items():
        a = np.asarray(arr, dtype=np.float64)
        for idx in np.argwhere(a != 0.0):
            key = (name, tuple(int(i) for i in idx))
            if key in THETA_ENTRIES:
                th[THETA_ENTRIES[key]] = float(a[tuple(idx)])
            elif name not in INERT:
                raise NotCovered(f"override {key}")
    return th


def grad_columns(task: dict) -> list[int]:
    cols = []
    for name, idx in task.get("grad") or []:
        key = (name, tuple(int(i) for i in idx))
        if key not in THETA_ENTRIES:
            raise NotCovered(f"gradient entry {key}")
        cols.append(THETA_ENTRIES[key])
    return cols


def build_setup(task: dict, setup_dir: str | None, tables_dir: str | None) -> dict:
    """`setup_target` for a task's energies, read from / written to `setup_dir` when given."""
    from physics.hf.capture_gpu_setup import setup_target

    path = Path(os.path.expanduser(setup_dir)) / f"{setup_key(task)}.pkl" if setup_dir else None
    if path is not None and path.exists():
        with open(path, "rb") as f:
            return pickle.load(f)
    tab = None
    if task.get("tables", True) and tables_dir:
        tab = str(Path(os.path.expanduser(tables_dir)) / f"{task['Z']}-{task['A']}.pt")
    s = setup_target(int(task["Z"]), int(task["A"]), energies_of(task),
                     float(task.get("enincmax", 20.0)), tab)
    s["tables"] = bool(tab and Path(tab).exists())
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(f".tmp{os.getpid()}")
        with open(tmp, "wb") as f:
            pickle.dump(s, f, protocol=5)
        os.replace(tmp, path)
    return s


def _result(task, setup, xs=None, jac=None, seconds=0.0, err="", impl="gpu"):
    n = len(energies_of(task))
    idx = task.get("energy_idx") or list(range(len(task["energies"])))
    out_xs = [float("nan")] * n
    ngrad = len(task.get("grad") or [])
    out_jac = [[float("nan")] * ngrad for _ in range(n)] if task.get("grad") else None
    if xs is not None:
        for k, v in xs.items():
            out_xs[k] = float(v)
        if out_jac is not None:
            for k, row in jac.items():
                out_jac[k] = [float(x) for x in row]
    dom = list(setup["domain"]) if setup is not None else [False] * n
    return {"Z": task["Z"], "A": task["A"], "energy_idx": list(idx), "xs": out_xs,
            "domain": dom, "jac": out_jac, "seconds": seconds,
            "err": err or (setup or {}).get("err", ""),
            "tables": bool((setup or {}).get("tables", False)), "impl": impl}


def run_batch(tasks: list[dict], setups: list[dict], device="cuda", compiled: bool = False,
              budget_bytes: float | None = None) -> list[dict | None]:
    """Answer `tasks` (with their `setups`) on the GPU. Returns one result per task, or None for
    a task the GPU path does not cover (the caller runs it on the CPU)."""
    import torch

    from physics.hf import capture_gpu as G

    t0 = time.perf_counter()
    out: list[dict | None] = [None] * len(tasks)
    todo = []  # (task position, theta, grad columns)
    for i, (task, s) in enumerate(zip(tasks, setups, strict=True)):
        if s["err"] or not s["points"]:
            out[i] = _result(task, s)
            continue
        try:
            todo.append((i, theta_of(task, s["gamma"]), grad_columns(task)))
        except NotCovered:
            continue
    if budget_bytes is None:
        free, _total = torch.cuda.mem_get_info(device)
        budget_bytes = 0.6 * free
    for want_grad in (False, True):
        group = [x for x in todo if bool(x[2]) == want_grad]
        per = BYTES_PER_POINT[want_grad]
        chunk, npts = [], 0
        chunks = []
        for x in group:
            n = len(setups[x[0]]["points"])
            if chunk and (npts + n) * per > budget_bytes:
                chunks.append(chunk)
                chunk, npts = [], 0
            chunk.append(x)
            npts += n
        if chunk:
            chunks.append(chunk)
        for ch in chunks:
            tg = [setups[i] for i, _th, _c in ch]
            try:
                pk = G.pack(tg, device)
                if not pk.meta["factorised"]:
                    continue  # the CPU path answers these
                theta = torch.tensor([th for _i, th, _c in ch], dtype=torch.float64, device=device)
                if want_grad:
                    xs, jac = G.forward(pk, theta, grad=True, compiled=compiled)
                    jac = jac.cpu().numpy()
                else:
                    xs, jac = G.forward(pk, theta, compiled=compiled), None
                xs = xs.cpu().numpy()
            except (ValueError, torch.OutOfMemoryError):
                continue
            per_task: dict = {i: ({}, {}) for i, _th, _c in ch}
            for p, (ti, ei) in enumerate(pk.index):
                i, _th, cols = ch[ti]
                per_task[i][0][ei] = xs[p]
                if jac is not None:
                    per_task[i][1][ei] = jac[p, cols]
            for i, _th, _c in ch:
                out[i] = _result(tasks[i], setups[i], *per_task[i])
    wall = time.perf_counter() - t0
    done = [r for r in out if r is not None]
    npts = sum(max(1, sum(r["domain"])) for r in done)
    for r in done:
        r["seconds"] = wall * max(1, sum(r["domain"])) / npts
    return out
