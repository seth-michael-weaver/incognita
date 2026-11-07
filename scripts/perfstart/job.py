#!/usr/bin/env python3
"""PERFSTART job driver: one engine job (one target, one energy grid) with the library v0.2 run environment, timed by phase.

The production calculator (scripts/talysworld/engine_job.py) runs engine build 16606b356d6e with NUCLIDO_* switches; this
driver runs THIS repository's engine with the same switches under their public INCOGNITA_* names, the v0.2 P-arm deck
(lines file + PEONSET keywords + ';m1share r'), and the run_item() core of the library runner (warmrun.new_cascade ->
engine_c.run under torch.inference_mode). It is the yardstick for start-up work and the correctness gate
(tests/hf/test_perfstart_gate.py): every output array is written as float64, so two engine versions can be compared bit for bit.

usage: job.py --z 26 --a 56 (--e-mev 1.0 [--e-mev ...] | --lib64) --out OUT.npz [--lines FILE] [--repeat N] [--profile F]
Prints one JSON line with the phase timings (import_s, cascade_s, run_s per repeat; wall since interpreter start).
"""
import argparse, json, os, sys, time

T_START = time.time()
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
H = os.path.expanduser("~")
INP = os.environ.get("PS_INPUTS", f"{H}/libv02/inputs")

# library v0.2 run environment (libv02 run.sh + pprun R83/FENV + engine_job.py), public names
ENV = dict(OMP_NUM_THREADS="1", MKL_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", CJ_FLOAT="1", LC_ALL="C",
           INCOGNITA_GGDEADEND="1", INCOGNITA_NGNEXCL="1", INCOGNITA_DWBAUNIT="1", INCOGNITA_LEVCOMPLETE="tgt",
           INCOGNITA_BANDCHECK="1", INCOGNITA_TRAPFIX="1", INCOGNITA_WFCNORM="1", INCOGNITA_TALYS_FIT="nodata",
           INCOGNITA_ENGPHYS="dircap,pespin", INCOGNITA_SPECOUT_DA="0",
           INCOGNITA_TRITFID="1", INCOGNITA_RESISO="1", INCOGNITA_CCSOCB="1", INCOGNITA_MPEFIX="1", INCOGNITA_CPINC2="1",
           INCOGNITA_SPECOUT="1", INCOGNITA_LEVJ="1", INCOGNITA_C6FIX="1", INCOGNITA_TLOGIT="y",
           INCOGNITA_SFUNC="u1", INCOGNITA_SFUNC_TABLE=INP + "/sl_meas_b.csv", INCOGNITA_SFUNC_SCOPE="first",
           INCOGNITA_FEWRES="off", INCOGNITA_PEWINDOW="g")
DECK = ("preequilibrium y;multipreeq y;knockfix2 y;leeshell nm;ctwindow2 y;peunits y;fists2 y;sigavcont y")


def set_env(z, a, lines):
    for k in [k for k in os.environ if k.startswith(("INCOGNITA_", "NUCLIDO_"))]:
        if k not in ("INCOGNITA_CC_CACHE", "INCOGNITA_STAGE_CACHE", "INCOGNITA_STRUCT_CACHE"): del os.environ[k]
    os.environ.update(ENV)
    os.environ.setdefault("INCOGNITA_CC_CACHE", f"{H}/.cache/perfstart-cc")
    if os.path.isdir(f"{H}/relb61_strip/structure"): os.environ.setdefault("TALYS_DIR", f"{H}/relb61_strip")
    os.environ["INCOGNITA_TALYS_FIT_LINES_FILE"] = lines
    os.environ["INCOGNITA_TALYS_FIT_LINES"] = DECK + (";collrule svw" if a - 2 * z >= 20 else "") + ";m1share r"


def one(M, z, a, e_mev):
    np, torch, fitlib, chartrun, warmrun = M["np"], M["torch"], M["fitlib"], M["chartrun"], M["warmrun"]
    t0 = time.perf_counter()
    fitlib.deactivate(); fitlib._cards.cache_clear(); chartrun.drop_target_caches()
    cas = warmrun.new_cascade(z, a, e_mev)
    t1 = time.perf_counter()
    with torch.inference_mode():
        res = M["engine_c"].run(injection=M["ChainedFull"](Z=z, A=a, declared_energies=e_mev, cascade=cas))
    t2 = time.perf_counter()
    ex = {"ch_" + k: v.detach().cpu().numpy().astype(np.float64) for k, v in res.channels_mb.items()}
    tm = getattr(res, "totals_mb", None)
    if isinstance(tm, dict):
        ex.update({"tot_" + str(k): v.detach().cpu().numpy().astype(np.float64) for k, v in tm.items() if hasattr(v, "detach")})
    for pre, dd in (("lv_", getattr(res, "levels_mb", None)), ("rp_", getattr(res, "residual_production_mb", None))):
        if isinstance(dd, dict):
            for k, v in dd.items():
                if hasattr(v, "detach"): ex[pre + str(k)] = v.detach().cpu().numpy().astype(np.float64)
    cas = res = None; chartrun.drop_target_caches()
    return ex, t1 - t0, t2 - t1


def imports():
    import numpy as np, torch
    torch.set_num_threads(1)
    from physics.hf import chartrun, warmrun
    from physics.hf.engine import ChainedFull
    from physics.hf import engine_c
    from physics.hf.input import fitlib
    engine_c.lib()
    if os.environ.get("PS_FREEZE", "1") != "0" and hasattr(warmrun, "freeze_startup"):
        warmrun.freeze_startup()
    return dict(np=np, torch=torch, chartrun=chartrun, warmrun=warmrun, ChainedFull=ChainedFull, engine_c=engine_c, fitlib=fitlib)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--z", type=int, required=True); ap.add_argument("--a", type=int, required=True)
    ap.add_argument("--e-mev", type=float, action="append"); ap.add_argument("--lib64", action="store_true")
    ap.add_argument("--lines"); ap.add_argument("--out"); ap.add_argument("--repeat", type=int, default=1)
    ap.add_argument("--profile"); ap.add_argument("--profile-run", help="profile the job only (after the imports)")
    a = ap.parse_args()
    lines = a.lines or f"{INP}/lines_P/V32_{a.z:03d}_{a.a:03d}.lines"
    set_env(a.z, a.a, lines)
    sys.path.insert(0, ROOT); os.chdir(ROOT)
    prof = None
    if a.profile:
        import cProfile; prof = cProfile.Profile(); prof.enable()
    ti = time.perf_counter(); M = imports(); t_imp = time.perf_counter() - ti
    if a.profile_run:
        import cProfile; prof = cProfile.Profile(); prof.enable(); a.profile = a.profile_run
    np = M["np"]
    # the library's 64-point grid (geomspace(1 keV, 20 MeV, 64), as dwbaunit.TRIGGER_GRID_MEV), eV
    grid = np.geomspace(1e3, 2e7, 64) if a.lib64 else [e * 1e6 for e in a.e_mev]
    e_mev = tuple(float(np.float32(e)) for e in np.asarray(grid, float) / 1e6)
    reps = []
    for _ in range(a.repeat):
        ex, tc, tr = one(M, a.z, a.a, e_mev); reps.append(dict(cascade_s=round(tc, 4), run_s=round(tr, 4)))
    if prof is not None:
        prof.disable(); prof.dump_stats(a.profile)
    if a.out:
        np.savez(a.out, e_mev=np.asarray(e_mev), **ex)
    sd = sys.modules.get("physics.hf.stagedisk")
    stc = sd.stats() if sd is not None and sd.enabled() else None
    bc = sys.modules.get("physics.hf.structure.bincache")
    sbc = bc.stats() if bc is not None and bc.directory() is not None else None
    print(json.dumps(dict(stagecache=stc, structcache=sbc, z=a.z, a=a.a, n_e=len(e_mev), import_s=round(t_imp, 4), reps=reps,
                          wall_s=round(time.time() - T_START, 4), first_job_s=round(t_imp + reps[0]["cascade_s"] + reps[0]["run_s"], 4))))
    sys.stdout.flush(); sys.stderr.flush()
    if os.environ.get("PS_FASTEXIT", "1") != "0":
        os._exit(0)   # PERFSTART: skip interpreter teardown (~0.3 s with torch loaded); the npz is closed already


if __name__ == "__main__":
    main()
