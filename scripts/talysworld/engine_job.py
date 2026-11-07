#!/usr/bin/env python3
"""TALYSWORLD-style calculator, one engine job: ONE target, ONE incident energy, the production engine.

Runs on laptop WSL / Linux with the production engine engine-20261022-3 (nucleus 16606b356d6e), the same environment,
runner (FASTGATE worker -> prodrun -> pprun, `fewres off`, `pewindow g`), deck and inputs as the library v0.2 runs
(nucleus research/rl/libv02/code/run.sh + worker.py; the v0.2.2 copy is ~/libv022/code/worker.py on the mini). The only
difference is the energy grid: [E], padded by default with one dummy top energy (GRIDTOP pad, below). Extra deck
keywords (TALYS spelling, ';'-joined) are appended to the arm deck the way worker.py --repro does.

GRIDTOP pad (default on; TW_GRIDTOP=0 or --no-gridtop for the bare one-point grid [E]). This engine sets the outgoing grid
top from the run's highest incident energy as TALYS does (grid.f90:120: enincmax + S_n(CN) + 1 MeV), i.e. 1 MeV above the
photon exit only. When the compound nucleus is unbound to an ejectile (S < 0: alpha for nearly every CN above A ~ 140,
proton on the proton-rich side) that exit's top energy E + S_n - S lies above the grid top and the transitions to the
residual's lowest states are cut, so a one-energy job [E] is wrong for these nuclei (I-109 capture at 19.8 keV x62 too
high). The fix of the later engines (NUCLIDO_GRIDTOP, default ON since engine-20261029-2; public INCOGNITA_GRIDTOP) is not
in engine-20261022-3, so the job runs the grid [E, E + |min S| + 1 MeV] instead (S = the CN's separation energies,
S(0,0,type) from the engine's own masses) and reports only E. Nothing changes when every S >= 0 (no pad is added).

usage: engine_job.py --z Z --a A --e E_EV --comp COMP [--kw "ldmodel 2;strength 9"] --work DIR [--cold]
Warm pool: when a warmpool.py daemon answers on TW_WARM_SOCK (default ~/talysworld_data/warm.sock) the job is sent there
(no ~5-6 s start-up, no separate separation-energy process; same numbers, same output line plus "warm": true). --cold
(or TW_WARM=0) always runs here in this process, as before.
COMP: library composition label (P | A(rotor) | ACTJS A(rotor) | JS(P,A) | ACTJS JS(P,A)) or a single arm P | A | AJ.
Prints one JSON line: {"e_ev":..., "channels": {total, elastic, nonelastic, capture, np, na, n2n, inelastic, fission} in mb,
"arms": [...], "cpu_s": ..., "err": ...}. Leaves nothing but that line (the work dir is removed).
"""
import argparse, json, os, shutil, sys, time

H = os.path.expanduser("~")
ENG = os.environ.get("TW_ENG", f"{H}/fastgate_data/eng/16606b356d6e")
INP = os.environ.get("TW_INPUTS", f"{H}/libv02/inputs")      # = the v0.2 runs' inputs (lines_P, lines_A, actjs_lines_*, code)
CC = os.environ.get("TW_CC", f"{H}/talysworld_data/cc")       # private copy of ~/fastgate_data/cc (as libv022/run.sh did)

# the library run environment, verbatim from libv02/libv022 run.sh
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import engine_env  # noqa: E402  (the one production-name -> repository-name switch table)

engine_env.clear_switches()   # NUCLIDO_* and INCOGNITA_*: nothing from the caller's shell reaches the engine
os.environ.update(OMP_NUM_THREADS="1", MKL_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", CJ_FLOAT="1", LC_ALL="C", UV_NO_SYNC="1",
                  TALYS_DIR=f"{H}/relb61_strip", RL_CC=CC, RL_BOX="laptop", RL_ENGINES="/dev/null",
                  NUCLIDO_GGDEADEND="1", NUCLIDO_NGNEXCL="1", NUCLIDO_DWBAUNIT="1", NUCLIDO_LEVCOMPLETE="tgt",
                  ENGAUDIT_PATH="c", NUCLIDO_BANDCHECK="1", NUCLIDO_TRAPFIX="1", NUCLIDO_WFCNORM="1",
                  NUCLIDO_CC_CACHE=CC, NUCLIDO_TALYS_FIT="nodata", NUCLIDO_ENGPHYS="dircap,pespin", NUCLIDO_SPECOUT_DA="0")
# SWNAMES6: the switches above (and the ones the bundle's pprun / r52pool / engine_pool set per job) are the production
# engine's NUCLIDO_* names. A TW_ENG that is this repository's engine reads INCOGNITA_*: engine_env.install mirrors every
# switch of engine_env.SWITCHES to it (on every set and delete), so both engines run the library configuration.
# Coupled-channels cache: for this repository's engine the job uses the BATCH cache (PERFCC2, physics/hf/ecis/incident.py
# `_CARRY`): whole solves keyed by every row they solve, so a hit is bit for bit the solve it replaces and the run's
# numbers are those of a run without any cache. The row cache NUCLIDO_CC_CACHE maps to (INCOGNITA_CC_CACHE) would serve
# a row solved in another batch: same values to ~1e-15, not the same bits; it is therefore not mirrored unless
# TW_CC_BATCH=0 (then the row cache, as production uses it). The production engine has no batch cache.
_BATCH = os.environ.get("TW_CC_BATCH", "1") != "0"
FLAVOUR = engine_env.install(ENG, skip=("NUCLIDO_CC_CACHE",) if _BATCH else ())
if FLAVOUR == "repo" and _BATCH: os.environ["INCOGNITA_CC_BATCHCACHE"] = CC
# worker.py
os.environ.update(PP_PLINES=INP + "/lines_P", PP_ALINES=INP + "/lines_A", PP_SLTABLE=INP + "/sl_meas_b.csv", R52CODE=INP + "/code")

ARMS = {"P": ["P"], "A": ["A"], "AJ": ["AJ"], "A(rotor)": ["A"], "ACTJS A(rotor)": ["AJ"], "JS(P,A)": ["P", "A"], "ACTJS JS(P,A)": ["P", "AJ"]}
CH = {"total": "tot_total", "elastic": "tot_elastic", "nonelastic": "tot_nonelastic", "capture": "capture_mb", "np": "ch_xs010000",
      "na": "ch_xs000001", "n2n": "ch_xs200000", "inelastic": "ch_xs100000", "fission": "tot_fission"}


def val(q, k):
    import numpy as np
    if k == "capture_mb" and k not in q: k = "ch_xs000000"
    return float(np.asarray(q[k], float)[0]) if k in q else 0.0


def cn_separation_mev(z, a):
    """S(0,0,type), type 0..6, of the compound nucleus of n + (z, a), from the engine's own masses (default options), in a
    separate process so nothing the engine caches at import leaks into the job. First the prebuilt table
    (scripts/perfstart/smin_table.py: same values, keyed to this engine's commit and mass tables; ~10 ms), else that process."""
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "perfstart"))
        import smin_table
        v = smin_table.lookup(z, a, eng=ENG)
        if v is not None: return [float(x) for x in v]
    except Exception:  # noqa: BLE001  (no table / unreadable: compute it)
        pass
    import subprocess
    code = ("import json,sys; from physics.hf.compound.dens_reference import _structure_of as S; "
            "o,p,m=S(int(sys.argv[1]),int(sys.argv[2])); print(json.dumps([float(m.s_mev[0,0,t]) for t in range(7)]))")
    p = subprocess.run([sys.executable, "-c", code, str(z), str(a)], capture_output=True, text=True, cwd=ENG, timeout=600)
    line = [ln for ln in p.stdout.splitlines() if ln.startswith("[")]
    if not line: raise RuntimeError(p.stderr.strip()[-300:] or f"exit {p.returncode}")
    return json.loads(line[-1])


def warm_job(a):
    """The job through a running warm pool (warmpool.py), in this script's output format; None if no pool answers."""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import warmpool as WP
    P = WP.Pool()
    if not P.alive(): return None
    w0 = time.time(); comp = a.comp.replace(" [FEW->mean]", "").strip()
    gridtop = not a.no_gridtop and os.environ.get("TW_GRIDTOP", "1").strip().lower() not in ("0", "n", "no", "off", "false")
    out = dict(z=a.z, a=a.a, e_ev=a.e, comp=comp, kw=a.kw, arms=ARMS[comp], err="")
    try:
        sm = round(float(min(P.smin(a.z, a.a))), 4) if gridtop else None   # engine_grid.run pads with the rounded value
        r = P.run(dict(z=a.z, a=a.a, grid=[a.e], comp=comp, kw=a.kw, work=os.path.abspath(a.work), smin=sm, gridtop=gridtop,
                       skip_pad=True, keep=a.keep))
    except (OSError, RuntimeError, ValueError) as ex:
        return None if isinstance(ex, OSError) else dict(out, err=f"warm pool: {type(ex).__name__}: {ex}"[:400])
    if sm is not None:
        out["s_min_mev"] = round(sm, 4)
    out["grid_ev"] = [a.e, a.e + (-sm + 1.0) * 1e6] if (sm is not None and sm < 0) else [a.e]
    out["gridtop"] = gridtop; out["err"] = r.get("err", "")
    if r.get("channels"): out["channels"] = {c: v[0] for c, v in r["channels"].items()}
    if r.get("log_tail"): out["log_tail"] = r["log_tail"]
    out["cpu_s"] = r.get("cpu_s"); out["wall_s"] = round(time.time() - w0, 2); out["warm"] = True
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--z", type=int, required=True); ap.add_argument("--a", type=int, required=True)
    ap.add_argument("--e", type=float, required=True); ap.add_argument("--comp", default="P"); ap.add_argument("--kw", default="")
    ap.add_argument("--work", required=True); ap.add_argument("--keep", action="store_true")
    ap.add_argument("--no-gridtop", action="store_true", help="bare one-point grid [E] (TALYS grid top; wrong when some S < 0)")
    ap.add_argument("--cold", action="store_true", help="never use the warm pool")
    a = ap.parse_args(); t0 = time.process_time(); w0 = time.time()
    if not a.cold and os.environ.get("TW_WARM", "1") != "0":
        res = warm_job(a)
        if res is not None:
            if not a.keep: shutil.rmtree(a.work, ignore_errors=True)
            sys.stdout.write(json.dumps(res) + "\n"); sys.stdout.flush(); return
    comp = a.comp.replace(" [FEW->mean]", "").strip()
    os.makedirs(a.work, exist_ok=True); grid = os.path.join(a.work, "grid.json")
    out = dict(z=a.z, a=a.a, e_ev=a.e, comp=comp, kw=a.kw, arms=ARMS[comp], err="")
    gridtop = not a.no_gridtop and os.environ.get("TW_GRIDTOP", "1").strip().lower() not in ("0", "n", "no", "off", "false")
    g = [a.e]
    if gridtop:
        try:
            # rounded as engine_grid.run pads (and as the warm pool's one-energy jobs pad): one grid for this nucleus everywhere
            smin = round(float(min(cn_separation_mev(a.z, a.a))), 4)
        except Exception as ex:  # noqa: BLE001  (a job without S cannot be padded safely: report it)
            out["err"] = f"GRIDTOP pad: separation energies unavailable: {type(ex).__name__}: {ex}"[:400]
            out["cpu_s"] = round(time.process_time() - t0, 2); out["wall_s"] = round(time.time() - w0, 2)
            if not a.keep: shutil.rmtree(a.work, ignore_errors=True)
            sys.stdout.write(json.dumps(out) + "\n"); sys.stdout.flush(); return
        out["s_min_mev"] = round(smin, 4)
        if smin < 0: g = [a.e, a.e + (-smin + 1.0) * 1e6]
    out["grid_ev"] = g; out["gridtop"] = gridtop
    json.dump(g, open(grid, "w"))
    sys.path.insert(0, INP + "/code")
    import io, contextlib
    log = io.StringIO()
    try:
        with contextlib.redirect_stdout(log):
            import numpy as np
            import prodrun
            PP = prodrun.PP
            X = a.kw.strip().strip(";")
            base = dict(PP.DECK)
            Q = {}
            for arm in ARMS[comp]:
                L = INP + ("/actjs_lines" if arm == "AJ" else "/lines")
                PP.ALINES = L + "_A/V32_{:03d}_{:03d}.lines"; prodrun._PL = L + "_P"
                pa = "A" if arm == "AJ" else arm
                PP.DECK = {k: v + (";" + X if X else "") for k, v in base.items()}
                od = os.path.join(a.work, arm)
                sys.argv = ["pprun", "--repo", ENG, "--out", od, "--grid", grid, "--arm", pa, "--fewres", "off", "--pewindow", "g",
                            "--za", f"{a.z},{a.a}"]
                PP.main()
                f = os.path.join(od, f"{a.z:03d}_{a.a:03d}.npz")
                if not os.path.exists(f):
                    e = os.path.join(od, f"{a.z:03d}_{a.a:03d}.err")
                    raise RuntimeError(f"arm {arm}: " + (open(e).read().strip()[-300:] if os.path.exists(e) else "no output"))
                q = np.load(f, allow_pickle=True); Q[arm] = {k: q[k] for k in q.files}
            first = Q[ARMS[comp][0]] if comp not in ("A(rotor)", "ACTJS A(rotor)") else Q[ARMS[comp][-1]]
            ch = {c: val(first, k) for c, k in CH.items()}
            if comp in ("JS(P,A)", "ACTJS JS(P,A)"):
                from physics.hf import jointcap as J
                class _Q(dict):
                    files = property(lambda s: list(s.keys()))
                c = J.combine(_Q(Q["P"]), _Q(Q[ARMS[comp][1]]))
                ch["capture"] = float(np.asarray(c["capture_mb"], float)[0])
                ch["capture_P"] = val(Q["P"], "capture_mb"); ch["capture_A"] = val(Q[ARMS[comp][1]], "capture_mb")
            out["channels"] = ch
    except Exception as ex:  # noqa: BLE001  (record and return)
        out["err"] = f"{type(ex).__name__}: {ex}"[:400]
        out["log_tail"] = log.getvalue()[-400:]
    out["cpu_s"] = round(time.process_time() - t0, 2); out["wall_s"] = round(time.time() - w0, 2)
    if not a.keep: shutil.rmtree(a.work, ignore_errors=True)
    sys.stdout.write(json.dumps(out) + "\n"); sys.stdout.flush()


if __name__ == "__main__":
    main()
