"""SPEEDW: whole runs of the port -- a warm worker pool, run-scoped set-up once, energies in parallel.

Task: SPEEDW (the speed wave; no physics of its own). Acceptance test: bitwise identity with the
serial `engine.ChainedFull` run on the four harness targets x 23 energies, every output quantity
(`scripts/hf_vs_talys_bench.py wident`), and the SPEED0 golden.

Nothing here is a TALYS routine: it schedules `engine.ChainedFull` + `engine.run`
(talysreaction.f90:1, talysreaction) across processes and changes no number.

**Three pieces, each behind its own switch; the serial path is untouched and stays the default.**

1. `run_parallel(Z, A, declared, jobs)` -- one run, split over forked children:

   * The parent builds the run's `Cascade` and computes the run's FIRST declared energy on it with
     `trim_batches=False`. That one call fills every run-scoped cache the serial run fills before
     or at its first energy: the level schemes and densities of the compound nucleus, the inverse
     Tjl on the emission grid, the structure scalars, and -- because the subset registry is left
     alone -- the two set-ups that are BATCHED over the declared grid, T8's exciton model and a
     coupled target's incident deck, on the whole grid. Solving those two over a subset moves
     them in the last bits, which is why a child must never do it.
   * It then forks `jobs` children (copy-on-write: they inherit the warm Cascade and the caches)
     and gives each a slice of the remaining energies, balanced by an energy cost model. Each
     child returns its `(BinaryInputs, ChannelInputs)` pairs, pickled, over a pipe.
   * The parent merges them in the declared order and runs `engine.run` over the merged list
     itself: `binary`'s `sfactor` and `channels`' `chanopen` are carried across the ascending
     energy loop (`BinaryState`, `ExclusiveState`), so that loop must see every energy, in order,
     in one process. It costs ~0.08 s for 23 energies. The multiple emission a child runs is
     seeded from `sfactor` too, so since OPEN4 a child also walks the declared energies below its
     slice as far as `binary` (`engine.ChainedFull.cases`), which costs it their compound target.

   Why the children's numbers are the serial run's: `Cascade` state that crosses energies is
   `fisom`'s latch, which reads the DECLARED grid's first energy (`Cascade.is_first_energy`),
   and caches whose values do not depend on which energies filled them. The identity check
   compares every flattened quantity bit for bit.

   **Fork safety.** A child is forked only from a process that has one OS thread (checked in
   `/proc/self/task`; otherwise the run is solved serially in-process) and one torch/MKL thread:
   `pin_one_thread` sets OMP/MKL/OPENBLAS_NUM_THREADS=1 before torch is imported and
   `torch.set_num_threads(1)` before its first parallel region. MKL is bit-invariant only at one
   thread anyway. The engine's own import set never starts a thread; pyarrow's jemalloc
   background thread would, so the worker does not import it.

2. `serve` / `WarmPool` -- persistent 1-thread workers speaking JSON lines (SPEED3's
   multi-host sweep transport: floats as `repr`, which round-trips a float64; the payload hash
   in the hello). A worker imports the port and runs one warm-up whole run on a nuclide in no
   case set (`WARM_ZA`, three energies up to 20 MeV, so the multiple pre-equilibrium kernel and
   the coupled/DWBA code paths are loaded too) before it says hello. A task is `(Z, A, declared
   energies, jobs, fresh)`; the result is exactly what `engine.run` returns (`Results`), plus
   the CPU-s it cost (`getrusage`, the task process and every energy child it reaped).
   `fresh=True` solves the task in a process forked from the warm worker, so a task never sees
   caches another target left behind and the worker never grows; `fresh=False` solves it in the
   worker itself and keeps what it built (a sweep's residual nuclei, level schemes and parameter
   files carry over to the next target).

3. Batching energies inside one process (SPEEDD's widths, SPEEDT's coupled channels): not done.
   See docs/results/hf-speed-profile.md, "Whole runs", for why it is not bit-identical.
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
import pickle
import resource
import selectors
import subprocess
import sys
import threading
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
WARM_ZA = (50, 120)  # Sn-120: in no harness case and far in Z from every sweep neighbour of one
WARM_ENERGIES = (1.0e-3, 5.0, 20.0)
# The nucleus pre-phase of `prepare` (levels, level densities and photon strengths of the
# nuclei the run reaches, built in forked children while the parent runs T8).
NUCLEUS_PREPHASE = os.environ.get("HF_POOL_NUCLEI", "1") != "0"
THREAD_VARS = ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS")


# ------------------------------------------------------------------------------------ process


def pin_one_thread() -> None:
    """One OpenMP/MKL/torch thread, set before torch's first parallel region."""
    for k in THREAD_VARS:
        os.environ[k] = "1"
    import torch

    torch.set_num_threads(1)
    try:
        torch.set_num_interop_threads(1)
    except RuntimeError:  # already set, or the pool already started: it was never used
        pass


def os_threads() -> int:
    try:
        return len(os.listdir("/proc/self/task"))
    except OSError:
        return 1


def cpu_s() -> float:
    """User + system CPU-s of this process and of every child it has reaped."""
    s = resource.getrusage(resource.RUSAGE_SELF)
    c = resource.getrusage(resource.RUSAGE_CHILDREN)
    return s.ru_utime + s.ru_stime + c.ru_utime + c.ru_stime


def payload_hash(root: Path = REPO) -> str:
    """The code a worker runs: every `physics/**/*.py` (SPEED3's handshake)."""
    h = hashlib.sha256()
    for p in sorted(p for p in (root / "physics").rglob("*.py") if "__pycache__" not in p.parts):
        h.update(str(p.relative_to(root)).encode())
        h.update(p.read_bytes())
    return h.hexdigest()[:16]


class _Ready:
    """An injection whose cases are already built, so `engine.run` reuses them."""

    def __init__(self, families, cases):
        self.families, self._cases = tuple(families), cases

    def cases(self):
        return self._cases


def declared_grid(energies) -> tuple[float, ...]:
    """The run's declared grid as `ChainedFull` stores it (TALYS's real(sgl) `Einc`)."""
    import numpy as np

    return tuple(float(np.float32(e)) for e in energies)


# -------------------------------------------------------------------------------- scheduling


def energy_cost(e_mev: float) -> float:
    """Relative cost of one energy of a whole run, for balancing the children.

    Measured on the four harness targets after SPEEDW's multiple pre-equilibrium kernel (child
    CPU-s per energy, warm parent): ~flat below the pre-equilibrium onset, rising roughly linearly
    above it, and the `emulpre` energy (multiple pre-equilibrium, 20 MeV) about twice its trend.
    Only the ranking matters.
    """
    c = 0.07 + (0.045 * (e_mev - 3.0) if e_mev > 3.0 else 0.0)
    if e_mev >= 20.0:
        c *= 2.0
    return c


def split(energies, jobs: int) -> list[list[float]]:
    """At most `jobs` slices, longest-processing-time first; each slice ascending."""
    jobs = max(1, min(int(jobs), len(energies)))
    bins = [[0.0, []] for _ in range(jobs)]
    for e in sorted(energies, key=lambda x: -energy_cost(x)):
        b = min(bins, key=lambda x: x[0])
        b[0] += energy_cost(e)
        b[1].append(e)
    return [sorted(b[1]) for b in bins if b[1]]


# ------------------------------------------------------------------------- one run, parallel


def reached_nuclei(cas, declared, maxz: int, maxn: int) -> list[tuple[int, int]]:
    """The nuclei whose levels, level density and photon strength some declared energy builds.

    At each energy, the set `engine.ChainedFull.cases` hands `Cascade.populations` (Exmax > 0
    after its two `propagate_exmax` passes, or the compound nucleus), plus the six particle
    daughters of each: a decaying bin builds the `spec` of every exit (`decay_fast.nexmax_rows`,
    `mpe_inputs`) whether or not the cascade later populates it. A hint for the pre-phase, not a
    contract: a nucleus it misses is built where it is first used, as in the serial run. On the
    four harness targets x 23 energies it misses none and adds 7-13 that are never read.
    """
    from physics.hf.emission.feed_reference import etotal_of
    from physics.hf.emission.feeding import NUMN, NUMZ, PARN, PARZ

    zmax, nmax = min(maxz, NUMZ), min(maxn, NUMN)
    box = [(zc, nc) for zc in range(zmax + 1) for nc in range(nmax + 1)]
    out: set = set()
    for e in declared:
        st = cas.new_energy(etotal_of(cas.Zt, cas.At, cas.enincmax, e, cas.k0), e_inc_mev=e)
        cas.propagate_exmax(st, 0, 0)
        live = [k for k in box if k == (0, 0) or float(st.exmax[k]) > 0.0]
        for k in live:
            cas.propagate_exmax(st, *k)
        out.update(k for k in box if k == (0, 0) or float(st.exmax[k]) > 0.0)
    kids = {(zc + PARZ[t], nc + PARN[t]) for zc, nc in out for t in range(1, 7)}
    return sorted(out | {k for k in kids if k[0] <= zmax and k[1] <= nmax})


def _setup_items(Z: int, A: int, decl, cas, items) -> list:
    """In a pre-phase child: run-scoped values that are pure functions of their key.

    `("E", k)`: T12's DWBA/giant block and T5's incident sigma_reac at declared energy `k` --
    both `preeq.chain._ByEnergy` maps, one value per energy whichever energies were looked up
    first. `("N", (zix, nix))`: the nucleus's discrete levels (`Cascade._levels`), its matched
    level density (`dens_reference._ld_of_cached`) and the photon-strength parameters it decays
    with (`_gamma_parameters(Z, A - 1)`).
    """
    from physics.hf.compound.dens_reference import _gamma_parameters, _ld_of_cached
    from physics.hf.preeq.chain import chained_direct, incident_reaction_xs

    out = []
    for kind, key in items:
        if kind == "E":
            out.append((kind, key, (chained_direct(Z, A, decl)[key],
                                    incident_reaction_xs(Z, A, decl)[key])))
        else:
            zn = cas.zn(*key)
            out.append((kind, key, (cas._levels(*key), _ld_of_cached(zn[0], zn[1], cas.Zt, cas.At),
                                    _gamma_parameters(zn[0], zn[1] - 1))))
    return out


def _install(Z: int, A: int, decl, cas, parts) -> None:
    """Hand the pre-phase values to the caches that would have built them.

    Each cache is filled by calling it once with its builder standing in for the value, so the
    entry lands under exactly the key a later caller looks up: `_ByEnergy._memo` directly,
    `Cascade._levels` through `structure.levels._discrete_levels` (which also fills
    `discrete_levels`' own id-keyed table for this run's options/masses/params), and the two
    `dens_reference` `lru_cache`s through `_ld_build` / `_build_gamma_parameters`.
    """
    import physics.hf.compound.dens_reference as DR
    import physics.hf.structure.levels as L
    from physics.hf.preeq.chain import chained_direct, incident_reaction_xs

    cd = chained_direct(Z, A, decl)
    rx = incident_reaction_xs(Z, A, decl)
    lv_of, ld_of, gp_of = {}, {}, {}
    for part in parts:
        for kind, key, val in part:
            if kind == "E":
                cd._memo[key], rx._memo[key] = val
            else:
                zn = cas.zn(*key)
                lv_of[zn], ld_of[zn], gp_of[(zn[0], zn[1] - 1)] = val
    saved = (L._discrete_levels, DR._ld_build, DR._build_gamma_parameters)
    try:
        L._discrete_levels = lambda Zn, An, *a, **k: lv_of[(int(Zn), int(An))]
        DR._ld_build = lambda Zn, An, Zt, At, ov, matching_xacc=None: ld_of[(Zn, An)]
        DR._build_gamma_parameters = lambda Zt, At, ov: gp_of[(Zt, At)]
        for zn in lv_of:
            zix = cas.Zc - zn[0]
            cas._levels(zix, cas.Ac - zix - zn[1])
            DR._ld_of_cached(zn[0], zn[1], cas.Zt, cas.At)
            DR._gamma_parameters(zn[0], zn[1] - 1)
    finally:
        L._discrete_levels, DR._ld_build, DR._build_gamma_parameters = saved


def prepare(Z: int, A: int, declared, jobs: int = 1, timings: dict | None = None
            ) -> tuple[object, list]:
    """The run's Cascade with its run-scoped set-up built, and the first energy's case.

    See the module docstring: the first declared energy, on the run's Cascade, with
    `trim_batches=False`, is the set-up the serial run does before and at its first energy.

    With `jobs` > 1 the parts of that set-up that are pure functions of a key go first, in one
    wave of forked children (`_setup_items`): T12's DWBA / giant block and T5's incident
    sigma_reac at every declared energy (T8's flux and discrete cross sections read them for the
    whole pre-equilibrium grid before the exciton model can run), and the levels, level density
    and photon-strength parameters of every nucleus any declared energy reaches
    (`reached_nuclei`), which the energy children would otherwise each rebuild. A coupled
    target's incident deck is solved on the whole axis in the parent first: every DWBA child
    reads it, and it must not be solved on a subset.
    """
    from physics.hf.emission.feeding import Cascade
    from physics.hf.engine import ChainedFull

    tick = [time.perf_counter()]

    def mark(name):
        if timings is not None:
            now = time.perf_counter()
            timings[name] = now - tick[0]
            tick[0] = now

    decl = declared_grid(declared)
    cas = Cascade(Z, A, max(decl), energies=decl)
    nwave: list = []
    mark("setup_cascade_s")
    if jobs > 1 and len(decl) > 1 and os_threads() == 1:
        from physics.hf.direct.chain import _coupled_cached
        from physics.hf.preeq.chain import lend_cascade
        from physics.hf.structure.scalars import structure_scalars

        lend_cascade(cas)  # what `ChainedFull.cases` does first: the children solve on `cas`
        _coupled_cached(Z, A, decl, int(cas.k0), None)
        sc = structure_scalars(Z, A, decl, cas.k0)
        mark("setup_coupled_scalars_s")
        eitems = [("E", round(e, 6)) for e in decl]
        nitems = [("N", k) for k in reached_nuclei(cas, decl, sc.maxz, sc.maxn)]
        mark("setup_reached_s")
        # The nuclei do not wait for anything: their wave runs while the parent does the DWBA
        # wave and then T8. The DWBA wave must finish before T8, which reads all of it.
        nn = min(max(jobs // 2, 1), len(nitems))
        nwave = (_fork_start(_setup_items, [(Z, A, decl, cas, nitems[i::nn]) for i in range(nn)])
                 if nitems and NUCLEUS_PREPHASE else [])
        ne = min(jobs, len(eitems))
        _install(Z, A, decl, cas,
                 _fork_map(_setup_items, [(Z, A, decl, cas, eitems[i::ne]) for i in range(ne)]))
        mark("setup_wave_s")
    first = ChainedFull(Z=Z, A=A, declared_energies=decl, energies=(decl[0],),
                        trim_batches=False, cascade=cas).cases()
    mark("setup_first_energy_s")
    if jobs > 1 and len(decl) > 1 and os_threads() == 1 and nwave:
        _install(Z, A, decl, cas, _fork_collect(nwave))
        mark("setup_nucleus_wave_wait_s")
    return cas, first


def _solve(Z, A, decl, energies, cas):
    from physics.hf.engine import ChainedFull

    return ChainedFull(Z=Z, A=A, declared_energies=decl, energies=tuple(energies),
                       trim_batches=False, cascade=cas).cases()


def _fork_start(fn, jobs_args: list) -> list:
    """Fork one child per entry running `fn(*args)`; returns handles for `_fork_collect`."""
    procs = []
    for args in jobs_args:
        r, w = os.pipe()
        pid = os.fork()
        if pid == 0:  # child
            code = 0
            try:
                os.close(r)
                try:
                    out = ("ok", fn(*args))
                except BaseException as exc:  # carried to the parent, re-raised there
                    import traceback

                    out = ("err", f"{type(exc).__name__}: {exc}\n{traceback.format_exc()}")
                    code = 1
                blob = pickle.dumps(out, protocol=pickle.HIGHEST_PROTOCOL)
                with os.fdopen(w, "wb") as f:
                    f.write(blob)
            finally:
                os._exit(code)
        os.close(w)
        os.set_blocking(r, False)
        procs.append((pid, r))
    return procs


def _fork_collect(procs: list) -> list:
    """The children's results in entry order. Pipes are drained concurrently: a child's pickle
    is megabytes and a pipe holds 64 KiB."""
    bufs = {r: bytearray() for _pid, r in procs}
    sel = selectors.DefaultSelector()
    for _pid, r in procs:
        sel.register(r, selectors.EVENT_READ)
    open_fds = len(procs)
    while open_fds:
        for key, _ in sel.select():
            fd = key.fd
            try:
                chunk = os.read(fd, 1 << 20)
            except BlockingIOError:
                continue
            if chunk:
                bufs[fd] += chunk
            else:
                sel.unregister(fd)
                os.close(fd)
                open_fds -= 1
    sel.close()
    out = []
    for pid, r in procs:
        os.waitpid(pid, 0)
        status, val = pickle.loads(bytes(bufs[r]))
        if status != "ok":
            raise RuntimeError(f"forked child failed: {val}")
        out.append(val)
    return out


def _fork_map(fn, jobs_args: list) -> list:
    """`fn(*args)` in one forked child per entry; results in entry order."""
    return _fork_collect(_fork_start(fn, jobs_args))


def run_parallel(Z: int, A: int, declared, jobs: int = 12, *, timings: dict | None = None):
    """`(Results, cases)` of the whole run `ChainedFull(Z, A, declared)`, energies over `jobs`
    forked children. Bit-identical to the serial run (module docstring)."""
    from physics.hf.engine import run

    t0, c0 = time.perf_counter(), cpu_s()
    decl = declared_grid(declared)
    cas, first = prepare(Z, A, decl, jobs, timings)
    t1 = time.perf_counter()
    rest = [e for e in decl if round(e, 6) != round(decl[0], 6)]
    slices = split(rest, jobs) if rest else []
    if slices and jobs > 1 and os_threads() == 1:
        parts = _fork_map(_solve, [(Z, A, decl, s, cas) for s in slices])
        mode = "fork"
    else:
        parts = [_solve(Z, A, decl, s, cas) for s in slices]
        mode = "serial"
    t2 = time.perf_counter()
    by_e = {round(b.e_inc_mev, 6): (b, c) for b, c in first}
    for part in parts:
        for b, c in part:
            by_e[round(b.e_inc_mev, 6)] = (b, c)
    cases = [by_e[round(e, 6)] for e in decl if round(e, 6) in by_e]
    res = run(injection=_Ready((), cases))
    t3 = time.perf_counter()
    if timings is not None:
        timings.update({"setup_s": t1 - t0, "energies_s": t2 - t1, "run_loop_s": t3 - t2,
                        "wall_s": t3 - t0, "cpu_s": cpu_s() - c0, "mode": mode,
                        "slices": [list(s) for s in slices]})
    return res, cases


def run_serial(Z: int, A: int, declared, *, timings: dict | None = None):
    """The reference: `engine.run(injection=ChainedFull(Z, A, declared))`, as E2E runs it."""
    from physics.hf.engine import ChainedFull, run

    t0, c0 = time.perf_counter(), cpu_s()
    cases = ChainedFull(Z=Z, A=A, declared_energies=declared_grid(declared)).cases()
    res = run(injection=_Ready((), cases))
    if timings is not None:
        timings.update({"wall_s": time.perf_counter() - t0, "cpu_s": cpu_s() - c0,
                        "mode": "serial"})
    return res, cases


# ------------------------------------------------------------------------------ the worker


def warm(za=WARM_ZA, energies=WARM_ENERGIES, level: str = "full") -> None:
    """Import the port and, unless `level` is "imports", run one small whole run so first-call
    paths are loaded ("full": `energies`, up to 20 MeV; "light": the first of them only)."""
    from physics.hf.engine import ChainedFull, run

    if level == "imports":
        from physics.hf.compound import chain, continuum, dens_reference, target  # noqa: F401
        from physics.hf.emission import feeding, multiple  # noqa: F401
        from physics.hf.preeq import chain as _pc, mpe_fast  # noqa: F401
        return
    Z, A = za
    es = energies if level == "full" else energies[:1]
    run(injection=_Ready((), ChainedFull(Z=Z, A=A, declared_energies=declared_grid(es))
                         .cases()))


def results_json(res) -> dict:
    """`Results` as JSON-able lists (float `repr` round-trips a float64 exactly)."""
    def lst(t):
        return [float(x) for x in t.detach().reshape(-1).tolist()]

    return {"e_inc_mev": lst(res.e_inc_mev),
            **{g: {k: lst(v) for k, v in getattr(res, g).items()}
               for g in ("channels_mb", "levels_mb", "residual_production_mb", "totals_mb")},
            "injected": list(res.injected)}


def results_from_json(d: dict):
    import torch

    from physics.hf.results import Results

    f64 = torch.float64
    return Results(e_inc_mev=torch.tensor(d["e_inc_mev"], dtype=f64),
                   **{g: {k: torch.tensor(v, dtype=f64) for k, v in d[g].items()}
                      for g in ("channels_mb", "levels_mb", "residual_production_mb",
                                "totals_mb")},
                   injected=tuple(d["injected"]))


def do_task(task: dict) -> dict:
    """One whole run in this process. `jobs` > 1 forks energy children."""
    Z, A = int(task["Z"]), int(task["A"])
    tm: dict = {}
    if int(task.get("jobs", 1)) > 1:
        res, cases = run_parallel(Z, A, task["energies"], int(task["jobs"]), timings=tm)
    else:
        res, cases = run_serial(Z, A, task["energies"], timings=tm)
    out = {"Z": Z, "A": A, "timings": tm, "results": results_json(res)}
    if task.get("pickle"):  # the whole (Results, cases), for the identity check
        out["pickle"] = base64.b64encode(pickle.dumps((res, cases), protocol=5)).decode()
    return out


def _task_fresh(task: dict) -> dict:
    """`do_task` in a process forked from this warm one; its CPU-s is counted from here."""
    if os_threads() != 1:
        return do_task(task)
    return _fork_map(do_task, [(task,)])[0]


def serve(warm_level: str = "full") -> None:
    """The worker: warm up, say hello, then one JSON task per stdin line, one result per line."""
    t0 = time.perf_counter()
    pin_one_thread()
    out = sys.stdout
    sys.stdout = sys.stderr  # nothing but protocol lines on the pipe
    warm(level=warm_level)
    hello = {"op": "hello", "host": os.uname().nodename, "pid": os.getpid(),
             "hash": payload_hash(), "warm_wall_s": time.perf_counter() - t0,
             "warm_cpu_s": cpu_s(), "threads": os_threads()}
    out.write(json.dumps(hello) + "\n")
    out.flush()
    for line in sys.stdin:
        msg = json.loads(line)
        if msg.get("op") == "quit":
            break
        task = msg["task"]
        c0, w0 = cpu_s(), time.perf_counter()
        try:
            res = _task_fresh(task) if task.get("fresh", True) else do_task(task)
            res["err"] = ""
        except Exception as exc:  # recorded per task, never silently dropped
            res = {"err": f"{type(exc).__name__}: {exc}"[:2000]}
        res["task_cpu_s"] = cpu_s() - c0
        res["task_wall_s"] = time.perf_counter() - w0
        out.write(json.dumps({"op": "result", "id": msg["id"], "result": res}) + "\n")
        out.flush()


# ------------------------------------------------------------------------------ the client


class WarmPool:
    """`workers` warm 1-thread workers, each a `python -m physics.hf.pool serve` subprocess,
    pinned with `taskset` to `cpus[i]` (a CPU list string) when given.

        with WarmPool(12, cpus=[str(c) for c in range(4, 16)]) as pool:
            results = pool.map([{"Z": 26, "A": 56, "energies": grid}, ...])

    `startup` holds each worker's hello (warm-up wall and CPU-s); `startup_wall_s` is the wall
    from spawn to the last hello.
    """

    def __init__(self, workers: int = 1, cpus: list[str] | None = None, env: dict | None = None,
                 python: str = sys.executable, warm: str = "full"):
        self.env = dict(os.environ if env is None else env)
        for k in THREAD_VARS:
            self.env[k] = "1"
        self.env["PYTHONPATH"] = str(REPO)
        t0 = time.perf_counter()
        self.procs = []
        for i in range(workers):
            cmd = [python, "-m", "physics.hf.pool", "serve", warm]
            if cpus:
                cmd = ["taskset", "-c", cpus[i % len(cpus)], *cmd]
            self.procs.append(subprocess.Popen(cmd, cwd=REPO, env=self.env, text=True,
                                               stdin=subprocess.PIPE, stdout=subprocess.PIPE))
        self.startup = [json.loads(p.stdout.readline()) for p in self.procs]
        want = payload_hash()
        for h in self.startup:
            if h.get("hash") != want:
                raise RuntimeError(f"worker {h.get('pid')} runs payload {h.get('hash')} != {want}")
        self.startup_wall_s = time.perf_counter() - t0
        self._id = 0

    def startup_cpu_s(self) -> float:
        return sum(h["warm_cpu_s"] for h in self.startup)

    def map(self, tasks: list[dict], workers: list[int] | None = None) -> list[dict]:
        """Every task, each worker one at a time, results in task order.

        Tasks go to the first free worker in list order, unless `workers[i]` names the worker
        task i must run on (a sweep that keeps neighbouring targets together with
        `fresh=False`, so they share what they build)."""
        results: list = [None] * len(tasks)
        lock = threading.Lock()
        shared = list(enumerate(tasks))
        own = {w: [] for w in range(len(self.procs))}
        if workers is not None:
            shared = []
            for i, (task, w) in enumerate(zip(tasks, workers, strict=True)):
                own[w % len(self.procs)].append((i, task))

        def drive(w, p):
            queue = shared if workers is None else own[w]
            while True:
                with lock:
                    if not queue:
                        return
                    i, task = queue.pop(0)
                    self._id += 1
                    tid = self._id
                p.stdin.write(json.dumps({"op": "task", "id": tid, "task": task}) + "\n")
                p.stdin.flush()
                line = p.stdout.readline()
                if not line:
                    raise RuntimeError("pool worker died")
                results[i] = json.loads(line)["result"]

        ths = [threading.Thread(target=drive, args=(w, p)) for w, p in enumerate(self.procs)]
        for t in ths:
            t.start()
        for t in ths:
            t.join()
        return results

    def close(self) -> None:
        for p in self.procs:
            try:
                p.stdin.write(json.dumps({"op": "quit"}) + "\n")
                p.stdin.flush()
            except (BrokenPipeError, ValueError):
                pass
        for p in self.procs:
            try:
                p.wait(timeout=30)
            except subprocess.TimeoutExpired:
                p.kill()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "serve":
        serve(sys.argv[2] if len(sys.argv) > 2 else "full")
    else:
        raise SystemExit("usage: python -m physics.hf.pool serve")
