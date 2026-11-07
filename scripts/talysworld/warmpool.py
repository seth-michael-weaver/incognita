#!/usr/bin/env python3
"""Warm engine pool for the calculator / batch tools (Linux): start-up paid once, jobs in parallel, numbers unchanged.

A fresh engine job pays ~5-6 s before it computes anything (Python, numpy, torch, the engine modules, the native
library; plus ~5 s more in a second process for the GRIDTOP separation energies). This daemon pays that ONCE:

    warmpool.py serve --sock ~/talysworld_data/warm.sock --workers 3      (started by server.py under nice 10)

and then answers requests over a Unix socket. Every job runs in a child FORKED from the pristine preloaded daemon, so

* a job costs only its compute (one energy: ~1-2 s, most of it the nuclide's own set-up; a 64-point curve: the curve);
* per-run state cannot carry over: every job starts from the same memory image, whatever ran before it, in whatever
  order (the engine's run-scoped state -- sfactor across energies, fisom's first-energy latch, the grid top -- lives in
  the job's own process and dies with it). A long-lived in-process loop would have to reset each of these by hand, and
  the engine's own warm workers slow down with age (engine_pool.py: recycle after 3 items); a fork has neither problem;
* up to --workers engine processes run at once (the "N warm workers"; copy-on-write, so N jobs cost ~N x the job memory
  only). A two-arm (JS) job runs its two arms side by side in two of those slots when two are free (engine_grid.run
  parallel_arms: the second arm in a fork taken before the first arm ran), else one after the other in one slot.

The daemon exits when its socket file is removed or when the process that started it (server.py, check_warm.py, a batch)
exits; a running job finishes and still answers. SIGTERM stops the daemon; its jobs take SIGTERM as usual.
The daemon is single-threaded (fork safety: the engine's own physics.hf.pool forks under the same rule), runs at the
nice level it was started with, and calls gc.freeze() after preloading so the children's gc passes skip the preloaded
heap (the engine calls gc.collect() in drop_target_caches; this saves ~0.3-0.5 s per job, no number changes).

Requests (one JSON line per connection, one JSON line back):
    {"op": "run", "args": {z, a, grid, comp, kw, smin, gridtop, energies, skip_pad}}  -> engine_grid.run(...) result
    {"op": "smin", "z": Z, "a": A}       -> {"s": [S(0,0,type) for type 0..6]} (engine_job.cn_separation_mev, in a fork)
    {"op": "ping"}                       -> {"ok": true, "workers": N, "pid": ...}

Client side (no engine imports; usable from server.py, engine_job.py, batch scripts):
    P = Pool(sock); P.run(dict(z=26, a=56, grid=[1e6], comp="P", kw="")); P.smin(26, 56)
    P.run_grid(z, a, grid, comp, kw, smin=None, chunks=3)  # one curve, its energies split over warm workers
run_grid splits the requested energies into `chunks` slices (balanced by the engine's own energy-cost model) and runs
each slice as the SAME declared grid with an energy subset (engine_grid._energy_subset), so each slice has the full run's
grid top, GRIDTOP pad and first energy, and the merged curve equals the one-run curve (tests/talysworld/test_warmpool.py).
"""
import argparse, json, os, selectors, signal, socket, sys, threading, time, traceback
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
H = os.path.expanduser("~")
DEFAULT_SOCK = os.environ.get("TW_WARM_SOCK", f"{H}/talysworld_data/warm.sock")
MAX_WORKERS = int(os.environ.get("TW_MAX_WORKERS", "3"))   # laptop: at most 3 engine processes (the mini may set 6)


# ------------------------------------------------------------------------------------------------------------- client

def energy_cost(e_ev):
    """Relative cost of one incident energy (physics.hf.pool.energy_cost, copied so the client imports no engine):
    flat below the pre-equilibrium onset, rising linearly above it, twice its trend at >= 20 MeV."""
    e = e_ev / 1e6
    c = 0.07 + (0.045 * (e - 3.0) if e > 3.0 else 0.0)
    return c * 2.0 if e >= 20.0 else c


def split(energies, chunks):
    """At most `chunks` slices, longest-processing-time first; each slice ascending.

    A slice's job also walks every declared energy below its highest one as far as the binary step (the engine carries
    sfactor that way), which costs roughly a compound-target step per lower energy; the LPT balance on the per-energy
    cost model is good enough because that walk is cheap next to the multiple emission it skips."""
    es = sorted(float(e) for e in energies)
    chunks = max(1, min(int(chunks), len(es)))
    bins = [[0.0, []] for _ in range(chunks)]
    for e in sorted(es, key=lambda x: -energy_cost(x)):
        b = min(bins, key=lambda x: x[0]); b[0] += energy_cost(e); b[1].append(e)
    return [sorted(b[1]) for b in bins if b[1]]


def merge(grid, parts):
    """Merge slice results (engine_grid.run dicts) back onto the ascending `grid`."""
    es = sorted(float(e) for e in grid)
    out = dict(parts[0]); out.pop("computed", None)
    errs = [p.get("err") for p in parts if p.get("err")]
    out["err"] = "; ".join(errs)[:400]
    out["e_ev"] = es
    if not errs:
        by = {}
        for p in parts:
            for i, e in enumerate(p["e_ev"]):
                by[float(e)] = {c: v[i] for c, v in p["channels"].items()}
        miss = [e for e in es if e not in by]
        if miss: out["err"] = f"merge: energies missing from the slices: {miss[:5]}"
        else: out["channels"] = {c: [by[e][c] for e in es] for c in by[es[0]]}
    out["cpu_s"] = round(sum(p.get("cpu_s", 0.0) for p in parts), 2)
    out["wall_s"] = round(max(p.get("wall_s", 0.0) for p in parts), 2)
    out["chunks"] = len(parts)
    return out


class Pool:
    """Client of a warmpool daemon. Thread-safe: every call is its own connection."""

    def __init__(self, sock=DEFAULT_SOCK, timeout=7200):
        self.sock, self.timeout = sock, timeout

    def _call(self, req):
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM); s.settimeout(self.timeout)
        try:
            s.connect(self.sock)
            s.sendall((json.dumps(req) + "\n").encode())
            buf = bytearray()
            while True:
                b = s.recv(1 << 16)
                if not b: break
                buf += b
        finally:
            s.close()
        if not buf: raise RuntimeError("warm pool: empty reply (job process died)")
        return json.loads(bytes(buf))

    def alive(self):
        try: return bool(self._call(dict(op="ping")).get("ok"))
        except (OSError, ValueError, RuntimeError): return False

    def ping(self):
        return self._call(dict(op="ping"))

    def smin(self, z, a):
        r = self._call(dict(op="smin", z=int(z), a=int(a)))
        if r.get("err"): raise RuntimeError(r["err"])
        return r["s"]

    def run(self, args):
        """engine_grid.run(**args) in a warm worker; args as engine_grid.run (work defaults to a fresh dir). With the
        GRIDTOP pad on and no smin given, the separation energies come from the pool first (a fork, not a new process)."""
        args = dict(args)
        gt = args.get("gridtop")
        if gt is None: gt = os.environ.get("TW_GRIDTOP", "1").strip().lower() not in ("0", "n", "no", "off", "false")
        if gt and args.get("smin") is None: args["smin"] = min(self.smin(args["z"], args["a"]))
        return self._call(dict(op="run", args=args))

    def run_grid(self, z, a, grid, comp="P", kw="", smin=None, chunks=1, gridtop=None):
        """One curve; with chunks > 1 its energies are split over that many warm workers and merged."""
        if gridtop is None: gridtop = os.environ.get("TW_GRIDTOP", "1").strip().lower() not in ("0", "n", "no", "off", "false")
        if gridtop and smin is None: smin = min(self.smin(z, a))
        base = dict(z=z, a=a, grid=sorted(float(e) for e in grid), comp=comp, kw=kw, smin=smin, gridtop=gridtop, skip_pad=True)
        sl = split(grid, chunks)
        if len(sl) == 1: return self.run(base)
        with ThreadPoolExecutor(len(sl)) as ex:
            parts = list(ex.map(lambda s: self.run(dict(base, energies=s)), sl))
        return merge(grid, parts)


# ------------------------------------------------------------------------------------------------------------- daemon

def _child(conn, req, data):
    """In the forked child: do the request, write one JSON line, exit."""
    code = 0
    try:
        try:
            import engine_grid as EG, engine_job as EJ
            op = req.get("op")
            if op == "run":
                args = dict(req["args"])
                args.setdefault("work", os.path.join(data, "jobs", f"w{os.getpid()}_{time.time_ns()}"))
                res = EG.run(**args)
            elif op == "smin":
                res = dict(s=_smin_inproc(int(req["z"]), int(req["a"])))
            else:
                res = dict(err=f"unknown op {op!r}")
        except BaseException as ex:  # noqa: BLE001
            res = dict(err=f"warm worker: {type(ex).__name__}: {ex}"[:400], log_tail=traceback.format_exc()[-400:]); code = 1
        conn.setblocking(True)
        conn.sendall((json.dumps(res) + "\n").encode())
        conn.close()
    finally:
        os._exit(code)


def _smin_inproc(z, a):
    """engine_job.cn_separation_mev without a new interpreter: the same call, in this (forked, throw-away) process,
    with the engine repo as cwd and the job's environment, as the subprocess has it."""
    import contextlib, io
    import engine_job as EJ
    os.chdir(EJ.ENG)
    with contextlib.redirect_stdout(io.StringIO()):
        from physics.hf.compound.dens_reference import _structure_of as S
        o, p, m = S(int(z), int(a))
    return [float(m.s_mev[0, 0, t]) for t in range(7)]


def serve(sock_path, workers, data):
    sys.path.insert(0, HERE)
    t0 = time.time()
    import gc
    import engine_grid as EG, engine_job as EJ
    EG.preload(full=True)
    gc.collect(); gc.freeze()
    nthreads = len(os.listdir("/proc/self/task"))
    if nthreads != 1:
        raise SystemExit(f"warmpool: {nthreads} OS threads after preload; forking is only safe from one thread")
    os.makedirs(os.path.join(data, "jobs"), exist_ok=True)
    try: os.unlink(sock_path)
    except FileNotFoundError: pass
    srv = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM); srv.bind(sock_path); os.chmod(sock_path, 0o600); srv.listen(64)
    srv.setblocking(False)
    sel = selectors.DefaultSelector(); sel.register(srv, selectors.EVENT_READ, "accept")
    sys.stderr.write(f"warmpool: ready in {time.time() - t0:.1f} s, pid {os.getpid()}, {workers} workers, {sock_path}\n"); sys.stderr.flush()
    pending = []          # (conn, req) waiting for a free slot
    kids = {}             # pid -> t_start
    bufs = {}             # conn -> bytearray (request being read)
    stop = [False]; ppid0 = os.getppid()
    signal.signal(signal.SIGTERM, lambda *_: stop.__setitem__(0, True))
    while not stop[0]:
        # reap finished children
        while kids:
            try: pid, _st = os.waitpid(-1, os.WNOHANG)
            except ChildProcessError: kids.clear(); break
            if pid == 0: break
            kids.pop(pid, None)
        # start queued jobs; a two-arm (JS) job takes two slots and runs its arms side by side when two are free
        while pending and sum(kids.values()) < workers:
            conn, req = pending.pop(0)
            need = 1
            if req.get("op") == "run":
                args = req["args"]
                two = len(EJ.ARMS.get(str(args.get("comp", "P")).replace(" [FEW->mean]", "").strip(), [])) > 1
                if two and args.get("parallel_arms", True) and workers - sum(kids.values()) >= 2: args["parallel_arms"] = True; need = 2
                else: args["parallel_arms"] = False
            pid = os.fork()
            if pid == 0:
                signal.signal(signal.SIGTERM, signal.SIG_DFL)   # the daemon's stop handler must not shield a job from kill
                srv.close(); sel.close()
                for c, _r in pending: c.close()
                for c in bufs: c.close()
                _child(conn, req, data)
            kids[pid] = need; conn.close()
        if not os.path.exists(sock_path): break   # removed = asked to stop
        if os.getppid() != ppid0: break           # the service (or script) that started us is gone
        for key, _ in sel.select(timeout=0.05):
            if key.data == "accept":
                try:
                    c, _ = srv.accept(); c.setblocking(False); bufs[c] = bytearray()
                    sel.register(c, selectors.EVENT_READ, "read")
                except BlockingIOError:
                    pass
                continue
            c = key.fileobj
            try: b = c.recv(1 << 16)
            except BlockingIOError: continue
            except OSError: b = b""
            if b: bufs[c] += b
            if not b or b"\n" in bufs[c]:
                sel.unregister(c); raw = bytes(bufs.pop(c))
                try: req = json.loads(raw.split(b"\n")[0])
                except ValueError: c.close(); continue
                if req.get("op") == "ping":
                    c.setblocking(True)
                    c.sendall((json.dumps(dict(ok=True, workers=workers, pid=os.getpid(), running=len(kids), slots_used=sum(kids.values()), queued=len(pending))) + "\n").encode())
                    c.close()
                else:
                    pending.append((c, req))
    try: os.unlink(sock_path)
    except OSError: pass


def ensure(sock=DEFAULT_SOCK, workers=3, nice=10, data=None, python=None, log=None, wait=120):
    """A Pool on `sock`, starting the daemon (nice `nice`) if none answers there. Returns (Pool, Popen or None)."""
    import subprocess
    P = Pool(sock)
    if P.alive(): return P, None
    data = data or os.environ.get("TW_DATA", f"{H}/talysworld_data")
    python = python or os.path.join(os.environ.get("TW_ENG", f"{H}/fastgate_data/eng/16606b356d6e"), ".venv", "bin", "python")
    lf = open(log or os.path.join(data, "warmpool.log"), "a")
    p = subprocess.Popen(["nice", "-n", str(nice), python, os.path.abspath(__file__), "serve", "--sock", sock, "--workers", str(workers),
                          "--data", data], stdin=subprocess.DEVNULL, stdout=lf, stderr=lf, cwd=data, start_new_session=True)
    t0 = time.time()
    while time.time() - t0 < wait:
        if p.poll() is not None: raise RuntimeError(f"warm pool exited at start-up (rc {p.returncode}); see {lf.name}")
        if P.alive(): return P, p
        time.sleep(0.2)
    raise RuntimeError("warm pool did not start in time")


def batch(a):
    """Library-build mode: every job is one whole run (one nuclide's curve) in a warm worker, `workers` at a time, heaviest
    (highest A) first. Nuclides, not energies, are the parallel unit here: no slice repeats a run's set-up."""
    P, proc = ensure(a.sock, workers=a.workers, nice=a.nice)
    jobs = json.load(open(a.jobs)); order = sorted(range(len(jobs)), key=lambda i: -int(jobs[i]["a"]))
    lock = threading.Lock(); t0 = time.time()
    with open(a.out, "a") as f, ThreadPoolExecutor(max(1, a.workers)) as ex:
        def one(i):
            t = time.time()
            try: r = P.run(jobs[i])
            except (OSError, RuntimeError, ValueError) as e: r = dict(err=f"{type(e).__name__}: {e}"[:400])
            r["job"] = i; r["wall_total_s"] = round(time.time() - t, 2)
            with lock: f.write(json.dumps(r) + "\n"); f.flush()
            return bool(r.get("err"))
        nerr = sum(ex.map(one, order))
    print(json.dumps(dict(jobs=len(jobs), failed=nerr, wall_s=round(time.time() - t0, 1))), flush=True)
    if proc is not None:
        try: os.unlink(a.sock)
        except OSError: pass


def main():
    ap = argparse.ArgumentParser(); sp = ap.add_subparsers(dest="cmd", required=True)
    s = sp.add_parser("serve"); s.add_argument("--sock", default=DEFAULT_SOCK); s.add_argument("--workers", type=int, default=3)
    s.add_argument("--data", default=os.environ.get("TW_DATA", f"{H}/talysworld_data"))
    p = sp.add_parser("ping"); p.add_argument("--sock", default=DEFAULT_SOCK)
    b = sp.add_parser("batch", help="many jobs (e.g. a library build: one whole curve per nuclide) over the warm workers")
    b.add_argument("--jobs", required=True, help="JSON list of engine_grid.run argument dicts {z, a, grid, comp, kw, ...}")
    b.add_argument("--out", required=True, help="JSON lines, one result per job (in completion order, with 'job': index)")
    b.add_argument("--sock", default=DEFAULT_SOCK); b.add_argument("--workers", type=int, default=3); b.add_argument("--nice", type=int, default=10)
    a = ap.parse_args()
    if a.cmd == "serve": serve(a.sock, max(1, min(MAX_WORKERS, a.workers)), a.data)
    elif a.cmd == "batch": batch(a)
    else: print(json.dumps(Pool(a.sock).ping()))


if __name__ == "__main__":
    main()
