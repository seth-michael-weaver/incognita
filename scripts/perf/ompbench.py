#!/usr/bin/env python3
"""One production-configuration engine run of one target on a given energy grid, for timing, profiling and the
optical-model speed gate (tests/hf/test_ompgate.py).

The configuration is the library/calculator one (scripts/talysworld/engine_job.py: lines_P deck, the PEON keyword deck
+ ';m1share r' (+ ';collrule svw' for N - Z >= 20), the R83 switches, the S-function input, FEWRES off, PEWINDOW g, the
collective-E2 hold rule), with the public INCOGNITA_ switch names, run through the emulator's port of the production
runner (emu/incognita_emu/runner/prod: h_rule -> run_item) so the C path is exactly the production one.

usage: ompbench.py --z 26 --a 56 --grid GRID.json --out DIR [--cc CCDIR] [--prof FILE.prof] [--inputs ~/libv02/inputs]
Writes DIR/ZZZ_AAA.npz (run_item's npz) and prints one JSON line {z, a, n, h_cpu_s, run_cpu_s, cpu_s, wall_s, err}.
Environment: TALYS_DIR (structure database), INCOGNITA_EMU_SLTABLE (S-function table; default INPUTS/sl_meas_b.csv)."""
import argparse, json, os, sys, time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
H = os.path.expanduser("~")

# library run switches (engine_job.py), INCOGNITA_ spelling; set before the engine is imported
SW = dict(GGDEADEND="1", NGNEXCL="1", DWBAUNIT="1", LEVCOMPLETE="tgt", BANDCHECK="1", TRAPFIX="1", WFCNORM="1",
          TALYS_FIT="nodata", ENGPHYS="dircap,pespin", SPECOUT_DA="0")


def configure(inputs, cc):
    for v in [k for k in os.environ if k.startswith(("INCOGNITA_", "NUCLIDO_", "HF_"))]: del os.environ[v]
    os.environ.update(OMP_NUM_THREADS="1", MKL_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", LC_ALL="C")
    os.environ.setdefault("TALYS_DIR", f"{H}/relb61_strip")
    os.environ.update({"INCOGNITA_" + k: v for k, v in SW.items()})
    if cc: os.environ["INCOGNITA_CC_CACHE"] = cc
    os.environ.setdefault("INCOGNITA_EMU_SLTABLE", f"{inputs}/sl_meas_b.csv")


def run(z, a, grid_file, out, inputs, prof=None):
    sys.path.insert(0, str(REPO / "emu" / "incognita_emu" / "runner" / "prod"))
    import settings as PP  # noqa: E402  (engine_pool + hrule, INCOGNITA_ prefix)
    EP, RP = PP.EP, PP.RP
    c0 = time.process_time(); w0 = time.time()
    M, base = EP._setup(str(REPO), [], "dircap,pespin")
    setup_cpu = time.process_time() - c0
    Path(out).mkdir(parents=True, exist_ok=True)
    lines = f"{inputs}/lines_P/V32_{z:03d}_{a:03d}.lines"
    extra = PP.DECK["P"] + (";collrule svw" if a - 2 * z >= 20 else "")
    it = [str(out), z, a, lines, str(grid_file), extra, "ompbench", {**PP.FLAGS, **PP.FENV}]
    c1 = time.process_time()
    row, env = RP.h_rule(M, base, it)
    h_cpu = time.process_time() - c1
    env = {**it[7], **env, EP.ev("FEWRES"): "off", EP.ev("PEWINDOW"): "g"}
    it2 = list(it[:5]) + [it[5] + ";m1share r", it[6], env]
    c2 = time.process_time()
    if prof:
        import cProfile
        pr = cProfile.Profile(); pr.enable()
    st = EP.run_item(M, base, it2, str(REPO), "dircap,pespin", 0, {"cpu": 0.0, "wall": 0.0})
    if prof:
        pr.disable(); pr.dump_stats(prof)
    run_cpu = time.process_time() - c2
    err = "" if st in ("ok", "skip") else (Path(out) / f"err_{z:03d}_{a:03d}.txt").read_text()[-600:]
    return dict(z=z, a=a, n=len(json.load(open(grid_file))), setup_cpu_s=round(setup_cpu, 3), h_cpu_s=round(h_cpu, 3),
                run_cpu_s=round(run_cpu, 3), cpu_s=round(time.process_time() - c0, 3), wall_s=round(time.time() - w0, 3),
                status=st, err=err)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--z", type=int, required=True); ap.add_argument("--a", type=int, required=True)
    ap.add_argument("--grid", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--cc", default=""); ap.add_argument("--prof", default="")
    ap.add_argument("--inputs", default=f"{H}/libv02/inputs")
    a = ap.parse_args()
    configure(a.inputs, a.cc)
    r = run(a.z, a.a, a.grid, a.out, a.inputs, a.prof or None)
    sys.stdout.write(json.dumps(r) + "\n"); sys.stdout.flush()


if __name__ == "__main__":
    main()
