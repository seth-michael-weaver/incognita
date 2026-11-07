#!/usr/bin/env python3
"""PERFBENCH: speed benchmark of the production engine against stock TALYS, with a bit-level correctness gate.

Runs on laptop WSL / Linux. The engine side runs exactly the calculator's production paths (scripts/talysworld):
  engine_job.py   one target, one energy, as the calculator's per-point job (it also looks up the CN separation energies
                  for the GRIDTOP pad in a second Python process)
  engine_grid.py  one target, a whole grid in one engine run (--smin given, so no separation-energy subprocess)
and, for the back-to-back test, this file's own driver (`_multi`, run under the engine venv) which imports the engine once
and calls engine_grid.run() for several targets in the same process.

Arms (each row of <out>/bench.jsonl is one timed process or one in-process target):
  smin         the separation-energy lookup alone (the extra process engine_job.py starts)            [engine]
  job1         engine_job.py, one energy (default 1 MeV)                                              [engine]
  pt1          engine_grid.py --grid [E] --smin S                                                     [engine]
  curve64      engine_grid.py on the 64-point library grid (1 keV - 20 MeV)                           [engine]
  multi        _multi driver: N targets back-to-back in one process (one energy, or --multi-grid 64)  [engine]
  talys_pt1 / talys_curve64 / talys_multi   stock TALYS, minimal input (projectile, element, mass, energy), one process per target
Cache states (engine): cold = an empty coupled-channels cache dir (TW_CC) and a fresh process; warm = a cache dir already
filled by an untimed priming run of the same target and grid. The OS page cache is not dropped (no root): "cold" here is the
engine's own disk cache, not the file system's. TALYS has no cache; its rows are tagged "cold" (first) / "warm" (repeats).
Timing: wall = perf_counter around the process; cpu = user+sys of the process and its reaped children (RUSAGE_CHILDREN delta). nice 10.

CORRECTNESS GATE: every engine result (all arms, all energies) is compared with scripts/perf/baseline.json on the channels
capture, elastic, total, np, na, n2n, fission; |x - b| > tol * max(|x|, |b|) (tol 1e-9) fails the gate (exit code 1).
  --write-baseline   store this run's results as the baseline (do that only on the reference engine).

usage (WSL):
  python3 scripts/perf/bench.py                       # everything: 4 targets, point + curve, cold + warm, multi, TALYS, gate
  python3 scripts/perf/bench.py --arms pt1,curve64 --no-talys --repeats 1
  python3 scripts/perf/bench.py --gate-only           # quickest gate: pt1 warm + curve64 warm for the 4 targets, no TALYS
  python3 scripts/perf/bench.py --write-baseline      # (re)write baseline.json from this run
  python3 scripts/perf/bench.py _multi SPEC.json      # (internal) the in-process driver; SPEC: see multi_driver()
On the shared laptop run it as one heavy job at a time (`free -g` available >= 8 GB first):
  flock /tmp/incognita_heavy.lock python3 scripts/perf/bench.py ...
The harness itself never runs more than one engine process at a time (TALYS too: one process).
Env: TW_ENG (engine repo, default ~/fastgate_data/eng/16606b356d6e), TW_INPUTS (~/libv02/inputs), TALYS_BIN
(~/opt/talys-src/bin/talys). Output: --out (default ~/perfbench_out/<time>): bench.jsonl, summary.md, gate.json.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import statistics
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
TW = os.path.join(HERE, "talysworld") if os.path.isdir(os.path.join(HERE, "talysworld")) else os.path.join(REPO, "scripts", "talysworld")
H = os.path.expanduser("~")
ENG = os.environ.get("TW_ENG", f"{H}/fastgate_data/eng/16606b356d6e")
PY = os.path.join(ENG, ".venv", "bin", "python")
TALYS = os.environ.get("TALYS_BIN", f"{H}/opt/talys-src/bin/talys")
BASELINE = os.path.join(HERE, "baseline.json")
GRID64 = os.path.join(HERE, "grid64.json")

DRIVER = os.path.abspath(__file__)


def stage_local(dst):
    """Run copies of the talysworld scripts and of this driver from dst (WSL disk) instead of the repo, which may sit on
    /mnt/c (9p): the job scripts put their own directory first on sys.path, so every import of the run stats it."""
    global TW, DRIVER
    os.makedirs(os.path.join(dst, "talysworld"), exist_ok=True)
    for f in os.listdir(TW):
        if f.endswith(".py"): shutil.copy2(os.path.join(TW, f), os.path.join(dst, "talysworld", f))
    shutil.copy2(os.path.abspath(__file__), os.path.join(dst, "bench.py"))
    TW, DRIVER = os.path.join(dst, "talysworld"), os.path.join(dst, "bench.py")


GATED = ("capture", "elastic", "total", "np", "na", "n2n", "fission")
SYM = {24: "Cr", 26: "Fe", 28: "Ni", 40: "Zr", 42: "Mo", 50: "Sn", 64: "Gd", 74: "W", 79: "Au", 92: "U"}
# (Z, A, library v0.2.1 composition: the 'composed ...' label of capture_v021.parquet, as server.resolve_comp() gives it)
NUCLIDES = {"Fe-56": (26, 56, "JS(P,A)"), "Zr-90": (40, 90, "JS(P,A)"), "Au-197": (79, 197, "JS(P,A)"),
            "U-238": (92, 238, "ACTJS A(rotor)"),
            "Cr-52": (24, 52, "JS(P,A)"), "Ni-58": (28, 58, "JS(P,A)"), "Mo-98": (42, 98, "JS(P,A)"),
            "Sn-118": (50, 118, "JS(P,A)"), "Gd-157": (64, 157, "A(rotor)"), "W-184": (74, 184, "JS(P,A)")}
MAIN4 = ["Fe-56", "Zr-90", "Au-197", "U-238"]
MULTI10 = ["Cr-52", "Fe-56", "Ni-58", "Zr-90", "Mo-98", "Sn-118", "Gd-157", "W-184", "Au-197", "U-238"]


# ----------------------------------------------------------------------------- process timing

def timed(cmd, cwd=None, env=None, nice=10):
    """Run cmd under nice; return (stdout, wall s, stderr, returncode). CPU is taken by the caller with Clock()."""
    w0 = time.perf_counter()
    p = subprocess.run(["nice", "-n", str(nice)] + cmd, cwd=cwd, env=env, capture_output=True, text=True)
    return p.stdout, time.perf_counter() - w0, p.stderr, p.returncode


class Clock:
    """children rusage delta (single-threaded harness: the only children are the ones we run)."""
    def __enter__(self):
        import resource
        self.r = resource; self.r0 = resource.getrusage(resource.RUSAGE_CHILDREN); return self

    def __exit__(self, *a):
        r1 = self.r.getrusage(self.r.RUSAGE_CHILDREN)
        self.cpu = (r1.ru_utime - self.r0.ru_utime) + (r1.ru_stime - self.r0.ru_stime)


def last_json(txt):
    ln = [x for x in txt.splitlines() if x.startswith("{")]
    return json.loads(ln[-1]) if ln else None


# ----------------------------------------------------------------------------- engine arms

def eng_env(cc):
    return dict(os.environ, TW_CC=cc, TW_ENG=ENG)


def run_smin(z, a, nice):
    code = ("import json,sys; from physics.hf.compound.dens_reference import _structure_of as S; "
            "o,p,m=S(int(sys.argv[1]),int(sys.argv[2])); print(json.dumps([float(m.s_mev[0,0,t]) for t in range(7)]))")
    with Clock() as c:
        txt, wall, err, rc = timed([PY, "-c", code, str(z), str(a)], cwd=ENG, nice=nice)
    ln = [x for x in txt.splitlines() if x.startswith("[")]
    if not ln: raise RuntimeError(f"smin {z} {a}: {err[-300:]}")
    return min(json.loads(ln[-1])), wall, c.cpu


def run_job1(z, a, comp, e, cc, work, nice):
    cmd = [PY, os.path.join(TW, "engine_job.py"), "--z", str(z), "--a", str(a), "--e", repr(e), "--comp", comp, "--work", work]
    with Clock() as c:
        txt, wall, err, rc = timed(cmd, cwd=TW, env=eng_env(cc), nice=nice)
    j = last_json(txt) or {"err": f"exit {rc}: {err[-300:]}"}
    ch = {k: [v] for k, v in (j.get("channels") or {}).items()}
    return dict(e_ev=[e], channels=ch, err=j.get("err", "")), wall, c.cpu


def run_grid(z, a, comp, grid, smin, cc, work, nice):
    gf = work.rstrip("/") + ".grid.json"; json.dump(grid, open(gf, "w"))
    cmd = [PY, os.path.join(TW, "engine_grid.py"), "--z", str(z), "--a", str(a), "--grid", gf, "--comp", comp, "--work", work,
           "--smin", repr(smin)]
    with Clock() as c:
        txt, wall, err, rc = timed(cmd, cwd=TW, env=eng_env(cc), nice=nice)
    os.remove(gf)
    j = last_json(txt) or {"err": f"exit {rc}: {err[-300:]}"}
    return dict(e_ev=j.get("e_ev", grid), channels=j.get("channels") or {}, err=j.get("err", "")), wall, c.cpu


def run_multi(names, grid, smins, cc, work, nice, profile=None, pyspy=None):
    spec = dict(targets=[[*NUCLIDES[n][:3], smins[n]] for n in names], grid=grid, work=work, cc=cc, profile=profile)
    sf = work.rstrip("/") + ".spec.json"; os.makedirs(os.path.dirname(sf), exist_ok=True); json.dump(spec, open(sf, "w"))
    cmd = [PY, DRIVER, "_multi", sf]
    if pyspy: cmd = [pyspy[0], "record", "--idle", "--native", "--rate", str(pyspy[2]), "-f", "raw", "-o", pyspy[1], "--"] + cmd
    with Clock() as c:
        txt, wall, err, rc = timed(cmd, cwd=TW, env=eng_env(cc), nice=nice)
    os.remove(sf)
    j = last_json(txt) or {"err": f"exit {rc}: {err[-500:]}", "results": []}
    return j, wall, c.cpu


def multi_driver(spec_file):
    """In-process driver: import the engine once (engine_grid.preload) and run each target's grid with engine_grid.run().
    SPEC = {targets: [[Z, A, comp, smin], ...], grid: [eV...], work: DIR, cc: DIR, profile: null|path.prof}.
    Prints one JSON line: {import_s, import_cpu_s, results: [{z, a, wall_s, cpu_s, e_ev, channels, err, stages}], total_s}."""
    spec = json.load(open(spec_file))
    os.environ["TW_CC"] = spec["cc"]
    prof = None
    if spec.get("profile"):
        import cProfile
        prof = cProfile.Profile(); prof.enable()
    w0, c0 = time.perf_counter(), time.process_time()
    sys.path.insert(0, TW)
    import engine_grid as EG
    EG.preload()
    import prodrun
    import r52pool as RP
    from physics.hf import stagetime
    # pprun.main() installs two read-only logging wrappers per call; install them once so back-to-back calls don't nest them
    hooks = {}
    for nm in ("install_dir_hook", "install_xr_hook"):
        f = getattr(RP, nm)
        def memo(f=f, nm=nm):
            if nm not in hooks: hooks[nm] = f()
            return hooks[nm]
        setattr(RP, nm, memo)
    STAGES = []
    pmain = prodrun.PP.main
    def main_snap():
        pmain()
        try: STAGES.append(stagetime.snapshot())
        except Exception as exc: STAGES.append({"err": str(exc)})
    prodrun.PP.main = main_snap
    out = dict(import_s=time.perf_counter() - w0, import_cpu_s=time.process_time() - c0, results=[])
    for z, a, comp, smin in spec["targets"]:
        STAGES.clear(); w1, c1 = time.perf_counter(), time.process_time()
        r = EG.run(z, a, spec["grid"], comp, "", os.path.join(spec["work"], f"{z}_{a}"), smin=smin)
        out["results"].append(dict(z=z, a=a, comp=comp, wall_s=time.perf_counter() - w1, cpu_s=time.process_time() - c1,
                                   e_ev=r.get("e_ev"), channels=r.get("channels") or {}, err=r.get("err", ""), stages=list(STAGES)))
    out["total_s"] = time.perf_counter() - w0
    if prof is not None:
        prof.disable(); prof.dump_stats(spec["profile"])
    sys.stdout.write(json.dumps(out) + "\n"); sys.stdout.flush()


# ----------------------------------------------------------------------------- TALYS

def run_talys(z, a, grid, work, nice):
    shutil.rmtree(work, ignore_errors=True); os.makedirs(work)
    inp = f"projectile n\nelement {SYM[z]}\nmass {a}\n"
    if len(grid) == 1:
        inp += f"energy {grid[0] / 1e6:.6e}\n"
    else:
        open(os.path.join(work, "energies"), "w").write("".join(f"{e / 1e6:.6e}\n" for e in grid)); inp += "energy energies\n"
    open(os.path.join(work, "talys.inp"), "w").write(inp)
    with Clock() as c:
        txt, wall, err, rc = timed(["sh", "-c", f"{TALYS} < talys.inp > talys.out"], cwd=work, nice=nice)
    ok = "congratulates" in open(os.path.join(work, "talys.out"), errors="replace").read()
    shutil.rmtree(work, ignore_errors=True)
    return ok, wall, c.cpu


# ----------------------------------------------------------------------------- gate

def key(arm, z, a, e_ev):
    return f"{arm.split(':')[0]}|{z}|{a}|{len(e_ev)}|{e_ev[0]:.6e}"


def compare(res, base, tol):
    """max relative difference over the gated channels; list of failures."""
    fails, worst = [], 0.0
    for ch in GATED:
        x, b = res["channels"].get(ch), base["channels"].get(ch)
        if b is None and x is None: continue
        if x is None or b is None or len(x) != len(b):
            fails.append(f"{ch}: shape {None if x is None else len(x)} vs {None if b is None else len(b)}"); continue
        for i, (u, v) in enumerate(zip(x, b)):
            d = abs(u - v); s = max(abs(u), abs(v))
            r = 0.0 if d == 0 else (d / s if s > 0 else float("inf"))
            worst = max(worst, r)
            if r > tol: fails.append(f"{ch}[{i}] E={res['e_ev'][i]:.4e}: {u!r} vs baseline {v!r} (rel {r:.3e})")
    return worst, fails


# ----------------------------------------------------------------------------- main

def main():
    if len(sys.argv) > 2 and sys.argv[1] == "_multi":
        return multi_driver(sys.argv[2])
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--nuclides", default=",".join(MAIN4))
    ap.add_argument("--multi-nuclides", default=",".join(MULTI10))
    ap.add_argument("--arms", default="smin,pt1,job1,curve64,multi")
    ap.add_argument("--energy", type=float, default=1e6, help="eV, for the one-energy arms and multi")
    ap.add_argument("--multi-grid", choices=["1", "64"], default="1")
    ap.add_argument("--states", default="cold,warm")
    ap.add_argument("--repeats", type=int, default=2, help="warm repeats (cold is always 1 per target)")
    ap.add_argument("--no-talys", action="store_true"); ap.add_argument("--talys-repeats", type=int, default=1)
    ap.add_argument("--gate-only", action="store_true", help="= --arms pt1,curve64 --states warm --repeats 1 --no-talys")
    ap.add_argument("--write-baseline", action="store_true"); ap.add_argument("--tol", type=float, default=1e-9)
    ap.add_argument("--nice", type=int, default=10)
    ap.add_argument("--local", action="store_true", help="run copies of the job scripts from <out>/code (WSL disk), not the repo")
    ap.add_argument("--out", default=os.path.join(H, "perfbench_out", time.strftime("%Y%m%d_%H%M%S")))
    a = ap.parse_args()
    if a.local: stage_local(os.path.join(a.out, "code"))
    if a.gate_only: a.arms, a.states, a.repeats, a.no_talys = "pt1,curve64", "warm", 1, True
    arms = a.arms.split(","); states = a.states.split(","); names = a.nuclides.split(","); mnames = a.multi_nuclides.split(",")
    os.makedirs(a.out, exist_ok=True); W = os.path.join(a.out, "work"); os.makedirs(W, exist_ok=True)
    cc_warm = os.path.join(a.out, "cc_warm"); os.makedirs(cc_warm, exist_ok=True)
    grid64 = json.load(open(GRID64)); g1 = [a.energy]
    log = open(os.path.join(a.out, "bench.jsonl"), "a"); rows = []; results = {}

    def rec(**k):
        k["t"] = time.strftime("%H:%M:%S"); rows.append(k); log.write(json.dumps({x: y for x, y in k.items() if x != "res"}) + "\n"); log.flush()
        print(f"{k['arm']:14s} {k.get('state',''):5s} {k.get('nuc',''):8s} wall {k.get('wall', 0):7.2f}  cpu {k.get('cpu', 0):7.2f}  {k.get('err','')[:80]}", flush=True)

    def keep(arm, z, a_, res):
        if res.get("err") or not res.get("channels"): return
        results.setdefault(key(arm, z, a_, res["e_ev"]), []).append(dict(e_ev=res["e_ev"], channels=res["channels"]))

    def fresh_cc():
        d = os.path.join(a.out, "cc_cold"); shutil.rmtree(d, ignore_errors=True); os.makedirs(d); return d

    allnames = list(dict.fromkeys(names + (mnames if "multi" in arms else [])))
    smins = {}
    for n in allnames:
        z, a_, comp = NUCLIDES[n]
        s, wall, cpu = run_smin(z, a_, a.nice); smins[n] = s
        if "smin" in arms: rec(arm="smin", state="", nuc=n, wall=wall, cpu=cpu, smin=s)

    for arm, grid in (("pt1", g1), ("job1", g1), ("curve64", grid64)):
        if arm not in arms: continue
        for n in names:
            z, a_, comp = NUCLIDES[n]
            def go(cc, w=os.path.join(W, f"{arm}_{z}_{a_}")):
                if arm == "job1": return run_job1(z, a_, comp, a.energy, cc, w, a.nice)
                return run_grid(z, a_, comp, grid, smins[n], cc, w, a.nice)
            if "cold" in states:
                res, wall, cpu = go(fresh_cc()); keep(arm, z, a_, res)
                rec(arm=arm, state="cold", nuc=n, wall=wall, cpu=cpu, err=res["err"], npts=len(grid))
            if "warm" in states:
                res, wall, cpu = go(cc_warm); keep(arm, z, a_, res)      # priming run (fills cc_warm), recorded as 'prime'
                rec(arm=arm, state="prime", nuc=n, wall=wall, cpu=cpu, err=res["err"], npts=len(grid))
                for r in range(a.repeats):
                    res, wall, cpu = go(cc_warm); keep(arm, z, a_, res)
                    rec(arm=arm, state="warm", nuc=n, wall=wall, cpu=cpu, err=res["err"], npts=len(grid), rep=r + 1)

    if "multi" in arms:
        mg = grid64 if a.multi_grid == "64" else g1
        for state in states:
            cc = fresh_cc() if state == "cold" else cc_warm
            reps = 1 if state == "cold" else a.repeats + 1      # warm: the first pass primes cc_warm for the extra targets
            for r in range(reps):
                j, wall, cpu = run_multi(mnames, mg, smins, cc, os.path.join(W, "multi"), a.nice)
                st = state if state == "cold" or r > 0 else "prime"
                for x in j.get("results", []):
                    n = f"{SYM[x['z']]}-{x['a']}"; keep("multi", x["z"], x["a"], x)
                    rec(arm="multi", state=st, nuc=n, wall=x["wall_s"], cpu=x["cpu_s"], err=x["err"], npts=len(mg), rep=r)
                rec(arm="multi_total", state=st, nuc=f"{len(mnames)}x", wall=wall, cpu=cpu, err=j.get("err", ""),
                    import_s=j.get("import_s"), npts=len(mg), rep=r)

    if not a.no_talys:
        for r in range(a.talys_repeats):
            st = "cold" if r == 0 else "warm"
            for arm, grid in (("talys_pt1", g1), ("talys_curve64", grid64)):
                tarm = arm.replace("talys_", "")
                if tarm not in arms and not (tarm == "pt1" and "job1" in arms): continue
                for n in names:
                    z, a_, comp = NUCLIDES[n]
                    ok, wall, cpu = run_talys(z, a_, grid, os.path.join(W, f"t_{z}_{a_}"), a.nice)
                    rec(arm=arm, state=st, nuc=n, wall=wall, cpu=cpu, err="" if ok else "TALYS did not finish", npts=len(grid))
            if "multi" in arms:
                mg = grid64 if a.multi_grid == "64" else g1; tw = tc = 0.0
                for n in mnames:
                    z, a_, comp = NUCLIDES[n]
                    ok, wall, cpu = run_talys(z, a_, mg, os.path.join(W, f"t_{z}_{a_}"), a.nice); tw += wall; tc += cpu
                rec(arm="talys_multi_total", state=st, nuc=f"{len(mnames)}x", wall=tw, cpu=tc, npts=len(mg))

    # ---- correctness gate
    gate = dict(tol=a.tol, checked=0, failed=0, worst_rel=0.0, failures=[], missing=[], self_consistency_worst_rel=0.0)
    for k, lst in results.items():   # every repeat of the same arm/target/grid must agree with the first
        for r in lst[1:]:
            w, _ = compare(r, lst[0], a.tol); gate["self_consistency_worst_rel"] = max(gate["self_consistency_worst_rel"], w)
    if a.write_baseline:
        old = json.load(open(BASELINE)) if os.path.exists(BASELINE) else {}
        old.update({k: v[0] for k, v in results.items()})
        meta = dict(engine=ENG, engine_commit=open(os.path.join(ENG, "ENGINE_COMMIT")).read().strip() if os.path.exists(os.path.join(ENG, "ENGINE_COMMIT")) else "",
                    written=time.strftime("%Y-%m-%d %H:%M"), channels=list(GATED), note="engine-20261022-3 production paths; see bench.py")
        old["_meta"] = meta
        json.dump(old, open(BASELINE, "w"), indent=0, sort_keys=True); print("baseline written:", BASELINE, len(old) - 1, "entries")
    base = json.load(open(BASELINE)) if os.path.exists(BASELINE) else {}
    for k, lst in results.items():
        if k not in base: gate["missing"].append(k); continue
        for r in lst:
            w, f = compare(r, base[k], a.tol); gate["checked"] += 1; gate["worst_rel"] = max(gate["worst_rel"], w)
            if f: gate["failed"] += 1; gate["failures"].append({k: f[:10]})
    for row in rows:
        if row.get("err"): gate["failures"].append({f"{row['arm']}|{row['nuc']}": [row["err"]]}); gate["failed"] += 1
    gate["pass"] = gate["failed"] == 0 and gate["checked"] > 0
    json.dump(gate, open(os.path.join(a.out, "gate.json"), "w"), indent=1)

    # ---- summary
    def med(arm, state, nuc):
        v = [r for r in rows if r["arm"] == arm and r.get("state") == state and r.get("nuc") == nuc]
        return (statistics.median(r["wall"] for r in v), statistics.median(r["cpu"] for r in v)) if v else None
    L = [f"# PERFBENCH {time.strftime('%Y-%m-%d %H:%M')}", "", f"engine {ENG}; scripts {TW}; TALYS {TALYS}; energy {a.energy:g} eV; nice {a.nice}; "
         f"load {os.getloadavg()[0]:.2f}", "", "median wall / cpu seconds", "",
         "| arm | state | " + " | ".join(names) + " |", "|---|---|" + "---|" * len(names)]
    for arm in ["smin", "pt1", "job1", "curve64", "multi", "talys_pt1", "talys_curve64"]:
        for state in ["", "cold", "warm"]:
            cells = [med(arm, state, n) for n in names]
            if any(cells): L.append(f"| {arm} | {state} | " + " | ".join(f"{c[0]:.2f} / {c[1]:.2f}" if c else "" for c in cells) + " |")
    for arm in ("multi_total", "talys_multi_total"):
        for r in rows:
            if r["arm"] == arm and r.get("state") != "prime":
                L.append(f"\n{arm} {r['state']}: {r['nuc']} targets, wall {r['wall']:.2f} s, cpu {r['cpu']:.2f} s"
                         + (f", engine import {r['import_s']:.2f} s" if r.get("import_s") else ""))
    L += ["", f"GATE: {'PASS' if gate['pass'] else 'FAIL'}  checked {gate['checked']}, failed {gate['failed']}, worst rel "
          f"{gate['worst_rel']:.3e}, repeat self-consistency worst rel {gate['self_consistency_worst_rel']:.3e}, "
          f"not in baseline {len(gate['missing'])}"]
    open(os.path.join(a.out, "summary.md"), "w").write("\n".join(L) + "\n"); print("\n".join(L))
    shutil.rmtree(W, ignore_errors=True); shutil.rmtree(os.path.join(a.out, "cc_cold"), ignore_errors=True)
    shutil.rmtree(cc_warm, ignore_errors=True); shutil.rmtree(os.path.join(a.out, "code"), ignore_errors=True)
    sys.exit(0 if gate["pass"] or a.write_baseline else 1)


if __name__ == "__main__":
    main()
