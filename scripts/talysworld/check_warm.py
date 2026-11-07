#!/usr/bin/env python3
"""Correctness gate + timings for the warm engine pool (warmpool.py). Linux / WSL with the production engine.

For each target (default Fe-56, Zr-90, Au-197, U-238, each with its library composition) and each grid (one energy,
the 64-point library grid), compare every reported channel of
    fresh    : a fresh engine process per job, as before (engine_job.py --cold for one energy, engine_grid.py for a curve;
               the whole padded grid computed, separation energies from their own process)
    warm     : the warm pool, one job (pad energy not computed: skip_pad)
    chunked  : the warm pool, the curve split over N workers (energy subsets of the same declared grid), merged
    reverse  : the warm pool again, targets and grids in the reverse order, all submitted at once (order independence)
    job      : engine_job.py through the pool (one energy)
to `--rtol` (default 1e-12) relative. Also checks the pool's separation energies against the fresh process's.
Writes a JSON summary (--out) with every comparison and the wall times; exit 1 if any comparison fails.

usage: check_warm.py [--targets 26,56,P 40,90,P ...] [--workers 3] [--out check_warm.json] [--e1 1e6]
"""
import argparse, json, os, subprocess, sys, tempfile, time
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import warmpool as WP  # noqa: E402

H = os.path.expanduser("~")
ENG = os.environ.get("TW_ENG", f"{H}/fastgate_data/eng/16606b356d6e")
PY = os.path.join(ENG, ".venv", "bin", "python")
LIB = os.path.join(os.path.dirname(os.path.dirname(HERE)), "library", "v0.2.1")
DEFAULT_TARGETS = [(26, 56), (40, 90), (79, 197), (92, 238)]


def library(z_a):
    """{(Z, A): composition} and the 64-point grid, from the published library (as server.py resolves 'library')."""
    import re
    import pandas as pd
    C = pd.read_parquet(os.path.join(LIB, "capture_v021.parquet"), columns=["Z", "A", "energy_ev", "value_source"])
    comp = {}
    for r in C.itertuples(index=False):
        if (int(r.Z), int(r.A)) in z_a:
            m = re.search(r"composed (.+?);", r.value_source)
            comp[(int(r.Z), int(r.A))] = m.group(1).replace(" [FEW->mean]", "").strip() if m else "P"
    return comp, [float(x) for x in C.energy_ev.iloc[0]]


def rel_diff(x, y):
    """max relative difference of two channel dicts ({name: [values]}); inf when keys or lengths differ."""
    if set(x) != set(y): return float("inf"), f"keys {sorted(set(x) ^ set(y))}"
    worst, where = 0.0, ""
    for c in x:
        a, b = list(x[c]), list(y[c])
        if len(a) != len(b): return float("inf"), f"{c}: length {len(a)} vs {len(b)}"
        for i, (u, v) in enumerate(zip(a, b)):
            d = 0.0 if u == v else abs(u - v) / max(abs(u), abs(v))
            if d > worst: worst, where = d, f"{c}[{i}] {u!r} vs {v!r}"
    return worst, where


def fresh(cmd, nice=10):
    t = time.time()
    p = subprocess.run(["nice", "-n", str(nice), PY] + cmd, capture_output=True, text=True, timeout=7200)
    line = [ln for ln in p.stdout.splitlines() if ln.startswith("{")]
    r = json.loads(line[-1]) if line else dict(err=f"exit {p.returncode}: {p.stderr[-300:]}")
    r["wall_total_s"] = round(time.time() - t, 2)
    return r


def as_lists(r):
    """engine_job.py's scalar channels -> one-element lists (engine_grid.py form)."""
    ch = r.get("channels") or {}
    return {c: (v if isinstance(v, list) else [v]) for c, v in ch.items()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--targets", nargs="*", default=[], help="Z,A[,COMP] (default: Fe-56 Zr-90 Au-197 U-238, library comps)")
    ap.add_argument("--workers", type=int, default=3); ap.add_argument("--rtol", type=float, default=1e-12)
    ap.add_argument("--e1", type=float, default=1e6, help="the one-energy job's energy (eV)")
    ap.add_argument("--out", default="check_warm.json"); ap.add_argument("--skip-fresh64", action="store_true")
    a = ap.parse_args()
    T = [tuple(int(v) for v in t.split(",")[:2]) for t in a.targets] or DEFAULT_TARGETS
    comps, G64 = library(set(T))
    for t in a.targets:
        f = t.split(",")
        if len(f) > 2: comps[(int(f[0]), int(f[1]))] = ",".join(f[2:])
    for t in T: comps.setdefault(t, "P")
    data = os.environ.get("TW_DATA", f"{H}/talysworld_data")
    work = tempfile.mkdtemp(prefix="checkwarm_", dir=data)
    sock = os.path.join(work, "pool.sock")
    S = dict(targets=[f"{z}-{aa} {comps[(z, aa)]}" for z, aa in T], rtol=a.rtol, workers=a.workers, e1_ev=a.e1, rows=[], timing={})
    fails = []

    def check(name, t, x, y):
        if x.get("err") or y.get("err"):
            d, w = float("inf"), f"err: {x.get('err')!r} / {y.get('err')!r}"
        else:
            d, w = rel_diff(x["ch"] if "ch" in x else as_lists(x), y["ch"] if "ch" in y else as_lists(y))
        ok = d <= a.rtol
        S["rows"].append(dict(check=name, target=f"{t[0]}-{t[1]}", max_rel=d if d != float("inf") else "inf", ok=ok, where=w))
        print(f"  {'ok  ' if ok else 'FAIL'} {name:28s} {t[0]}-{t[1]}: max rel {d:.3g} {w if not ok else ''}", flush=True)
        if not ok: fails.append((name, t, w))

    # 1. fresh references, one job at a time (clean timings)
    REF = {}
    print("fresh processes (one at a time, nice 10)", flush=True)
    gf = os.path.join(work, "g64.json"); json.dump(G64, open(gf, "w"))
    for t in T:
        z, aa = t; c = comps[t]
        r1 = fresh([os.path.join(HERE, "engine_job.py"), "--z", str(z), "--a", str(aa), "--e", repr(a.e1), "--comp", c, "--work",
                    os.path.join(work, f"f1_{z}_{aa}"), "--cold"])
        REF[(t, 1)] = r1; S["timing"][f"{z}-{aa} one energy, fresh engine_job.py (incl. S process)"] = r1["wall_total_s"]
        print(f"  {z}-{aa} one energy fresh: {r1['wall_total_s']} s err={r1.get('err')!r}", flush=True)
        if a.skip_fresh64: continue
        sm = r1.get("s_min_mev")
        r64 = fresh([os.path.join(HERE, "engine_grid.py"), "--z", str(z), "--a", str(aa), "--grid", gf, "--comp", c, "--work",
                     os.path.join(work, f"f64_{z}_{aa}")] + ([] if sm is None else ["--smin", repr(sm)]))
        REF[(t, 64)] = r64; S["timing"][f"{z}-{aa} 64 points, fresh engine_grid.py"] = r64["wall_total_s"]
        print(f"  {z}-{aa} 64 points fresh: {r64['wall_total_s']} s err={r64.get('err')!r}", flush=True)

    # 2. the pool
    t0 = time.time()
    P, proc = WP.ensure(sock, workers=a.workers, nice=10, data=work, python=PY, log=os.path.join(work, "pool.log"))   # empty h-rule cache
    S["timing"]["pool start-up (once)"] = round(time.time() - t0, 2)
    try:
        SM = {}
        for t in T:
            t1 = time.time(); s = P.smin(*t); SM[t] = min(s)
            sf = P._call(dict(op="smin", z=t[0], a=t[1]))["s"]   # the pool's own fork path, whatever the table says
            S["rows"].append(dict(check="smin table == pool fork", target=f"{t[0]}-{t[1]}", ok=sf == s, where=f"{sf} vs {s}"))
            if sf != s: fails.append(("smin fork", t, f"{sf} vs {s}"))
            S["timing"][f"{t[0]}-{t[1]} separation energies, pool"] = round(time.time() - t1, 2)
            ref_s = REF[(t, 1)].get("s_min_mev")
            ok = ref_s is None or round(SM[t], 4) == ref_s
            S["rows"].append(dict(check="smin pool == fresh", target=f"{t[0]}-{t[1]}", ok=ok, where=f"{SM[t]!r} vs {ref_s!r}"))
            if not ok: fails.append(("smin", t, f"{SM[t]} vs {ref_s}"))
        print("warm pool, one job at a time", flush=True)
        W = {}
        for t in T:
            z, aa = t; c = comps[t]
            for rep in (1, 2):   # the second repeat shows the steady-state latency
                t1 = time.time()
                W[(t, 1)] = P.run(dict(z=z, a=aa, grid=[a.e1], comp=c, kw="", smin=SM[t], skip_pad=True))
                S["timing"][f"{z}-{aa} one energy, warm pool (run {rep})"] = round(time.time() - t1, 2)
            t1 = time.time(); W[(t, 64)] = P.run(dict(z=z, a=aa, grid=G64, comp=c, kw="", smin=SM[t], skip_pad=True))
            S["timing"][f"{z}-{aa} 64 points, warm pool, 1 worker"] = round(time.time() - t1, 2)
            CH = {}
            for n in sorted({2, a.workers} - {1}):
                t1 = time.time(); CH[n] = P.run_grid(z, aa, G64, c, "", smin=SM[t], chunks=n)
                S["timing"][f"{z}-{aa} 64 points, warm pool, {n} workers (chunked)"] = round(time.time() - t1, 2)
            check("one energy: warm == fresh", t, {"ch": W[(t, 1)].get("channels") or {}, "err": W[(t, 1)].get("err")}, REF[(t, 1)])
            if (t, 64) in REF:
                R64 = {"ch": REF[(t, 64)].get("channels") or {}, "err": REF[(t, 64)].get("err")}
                check("64 points: warm == fresh", t, {"ch": W[(t, 64)].get("channels") or {}, "err": W[(t, 64)].get("err")}, R64)
            else:
                R64 = {"ch": W[(t, 64)].get("channels") or {}, "err": W[(t, 64)].get("err")}
            for n, r in CH.items():
                check(f"64 points: chunked x{n} == fresh", t, {"ch": r.get("channels") or {}, "err": r.get("err")}, R64)
            W[(t, "R64")] = R64

        print("warm pool, reverse order, all jobs at once", flush=True)
        jobs = [(t, g) for t in reversed(T) for g in (64, 1)]
        t1 = time.time()
        with ThreadPoolExecutor(len(jobs)) as ex:
            got = list(ex.map(lambda j: P.run(dict(z=j[0][0], a=j[0][1], grid=G64 if j[1] == 64 else [a.e1], comp=comps[j[0]], kw="",
                                                   smin=SM[j[0]], skip_pad=True)), jobs))
        S["timing"]["all 8 jobs at once, reverse order"] = round(time.time() - t1, 2)
        for (t, g), r in zip(jobs, got):
            ref = W[(t, "R64")] if g == 64 else REF[(t, 1)]
            check(f"{'64 points' if g == 64 else 'one energy'}: reverse order == fresh", t, {"ch": r.get("channels") or {}, "err": r.get("err")}, ref)

        print("deck keywords varied between jobs, interleaved, all at once", flush=True)
        KW = ["ldmodel 2", "strength 1", ""]
        kt = [t for t in T if t in ((26, 56), (92, 238))] or T[:1]
        for t in kt:
            for k in KW[:2]:
                REF[(t, 1, k)] = fresh([os.path.join(HERE, "engine_job.py"), "--z", str(t[0]), "--a", str(t[1]), "--e", repr(a.e1), "--comp", comps[t],
                                        "--kw", k, "--work", os.path.join(work, f"fk_{t[0]}_{t[1]}_{k.replace(' ', '')}"), "--cold"])
            REF[(t, 1, "")] = REF[(t, 1)]
        jobs = [(t, k) for k in KW for t in kt][::-1]
        with ThreadPoolExecutor(len(jobs)) as ex:
            got = list(ex.map(lambda j: P.run(dict(z=j[0][0], a=j[0][1], grid=[a.e1], comp=comps[j[0]], kw=j[1], smin=SM[j[0]], skip_pad=True)), jobs))
        for (t, k), r in zip(jobs, got):
            check(f"one energy kw={k or '-'!s}: interleaved == fresh", t, {"ch": r.get("channels") or {}, "err": r.get("err")}, REF[(t, 1, k)])
        for t in kt:   # the keywords really change something (else the test above proves little)
            d, _ = rel_diff(as_lists(REF[(t, 1, "ldmodel 2")]), as_lists(REF[(t, 1)]))
            S["rows"].append(dict(check="ldmodel 2 changes the result", target=f"{t[0]}-{t[1]}", ok=d > 0, where=f"max rel {d:.3g}"))

        print("engine_job.py through the pool", flush=True)
        env = dict(os.environ, TW_WARM_SOCK=sock)
        for t in T:
            z, aa = t; t1 = time.time()
            p = subprocess.run([PY, os.path.join(HERE, "engine_job.py"), "--z", str(z), "--a", str(aa), "--e", repr(a.e1), "--comp", comps[t],
                                "--work", os.path.join(work, f"j1_{z}_{aa}")], capture_output=True, text=True, env=env, timeout=3600)
            S["timing"][f"{z}-{aa} one energy, engine_job.py via pool (incl. its own python start)"] = round(time.time() - t1, 2)
            line = [ln for ln in p.stdout.splitlines() if ln.startswith("{")]
            r = json.loads(line[-1]) if line else dict(err=p.stderr[-300:])
            if not r.get("warm"): r["err"] = (r.get("err") or "") + " (did not use the pool)"
            check("engine_job.py via pool == fresh", t, r, REF[(t, 1)])
    finally:
        try: os.unlink(sock)
        except OSError: pass
        if proc is not None:
            try: proc.wait(10)
            except subprocess.TimeoutExpired: proc.terminate()
    S["n_checks"] = len(S["rows"]); S["n_failed"] = len(fails)
    json.dump(S, open(a.out, "w"), indent=1)
    print(json.dumps(S["timing"], indent=1))
    print(f"{S['n_checks']} checks, {len(fails)} failed; {a.out}", flush=True)
    import shutil; shutil.rmtree(work, ignore_errors=True)
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
