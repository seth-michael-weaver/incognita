#!/usr/bin/env python3
"""PERFCASC gate runner (used by tests/hf/test_perfcasc_gate.py; not a test module itself).

Runs ONE nuclide of the TALYSWORLD library job against an engine checkout: the library v0.2 deck and runner (the
`libv02/inputs` bundle: lines_P / lines_A / actjs_lines_*, sl_meas_b.csv and its code/ prodrun -> pprun -> r52pool ->
engine_pool, `fewres off`, `pewindow g`), the arms of the library composition (JS(P,A): P and A; ACTJS A(rotor): AJ), on
an energy grid given as a JSON list of eV. The bundle sets the engine's switches under their pre-release NUCLIDO_* names;
they are mirrored here to the INCOGNITA_* names this repository reads (scripts/talysworld/engine_env.py).

Writes a JSON file {arm: {key: [float.hex(), ...]}} with the gate channels of every arm (total, elastic, nonelastic,
capture, (n,p), (n,a), (n,2n), inelastic, fission), exact to the bit.

usage: perfcasc_gate_run.py --repo REPO --inputs LIBV02_INPUTS --z Z --a A --comp COMP --grid GRID.json --cc CCDIR --out OUT.json
"""
import argparse
import json
import os
import shutil
import sys


sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                                "scripts", "talysworld"))
import engine_env  # noqa: E402  (the one NUCLIDO_* -> INCOGNITA_* switch table)


ARMS = {"P": ["P"], "A": ["A"], "AJ": ["AJ"], "JS(P,A)": ["P", "A"], "ACTJS A(rotor)": ["AJ"]}
#: npz key of each gate channel (engine_pool's names)
KEYS = {"total": "tot_total", "elastic": "tot_elastic", "nonelastic": "tot_nonelastic", "capture": "capture_mb",
        "np": "ch_xs010000", "na": "ch_xs000001", "n2n": "ch_xs200000", "inelastic": "ch_xs100000",
        "fission": "tot_fission"}


def main():
    ap = argparse.ArgumentParser()
    for k in ("--repo", "--inputs", "--comp", "--grid", "--cc", "--out"):
        ap.add_argument(k, required=True)
    ap.add_argument("--z", type=int, required=True)
    ap.add_argument("--a", type=int, required=True)
    a = ap.parse_args()
    engine_env.clear_switches()
    engine_env.install(a.repo)
    H, INP = os.path.expanduser("~"), a.inputs
    os.makedirs(a.cc, exist_ok=True)
    # the library run environment (libv02 run.sh + worker.py), as scripts/talysworld/engine_job.py sets it
    os.environ.update(OMP_NUM_THREADS="1", MKL_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", CJ_FLOAT="1", LC_ALL="C",
                      UV_NO_SYNC="1", TALYS_DIR=os.environ.get("TALYS_DIR", f"{H}/relb61_strip"), RL_CC=a.cc,
                      RL_BOX="laptop", RL_ENGINES="/dev/null",
                      NUCLIDO_GGDEADEND="1", NUCLIDO_NGNEXCL="1", NUCLIDO_DWBAUNIT="1", NUCLIDO_LEVCOMPLETE="tgt",
                      ENGAUDIT_PATH="c", NUCLIDO_BANDCHECK="1", NUCLIDO_TRAPFIX="1", NUCLIDO_WFCNORM="1",
                      NUCLIDO_CC_CACHE=a.cc, NUCLIDO_TALYS_FIT="nodata", NUCLIDO_ENGPHYS="dircap,pespin",
                      NUCLIDO_SPECOUT_DA="0")
    os.environ.update(PP_PLINES=INP + "/lines_P", PP_ALINES=INP + "/lines_A", PP_SLTABLE=INP + "/sl_meas_b.csv",
                      R52CODE=INP + "/code")
    work = a.out + ".work"
    shutil.rmtree(work, ignore_errors=True)
    os.makedirs(work)
    sys.path.insert(0, INP + "/code")
    import numpy as np
    import prodrun

    PP = prodrun.PP
    base = dict(PP.DECK)
    out = {}
    for arm in ARMS[a.comp]:
        lines = INP + ("/actjs_lines" if arm == "AJ" else "/lines")
        PP.ALINES = lines + "_A/V32_{:03d}_{:03d}.lines"
        prodrun._PL = lines + "_P"
        PP.DECK = dict(base)
        od = os.path.join(work, arm)
        sys.argv = ["pprun", "--repo", a.repo, "--out", od, "--grid", os.path.abspath(a.grid), "--arm",
                    "A" if arm == "AJ" else arm, "--fewres", "off", "--pewindow", "g", "--za", f"{a.z},{a.a}"]
        PP.main()
        f = os.path.join(od, f"{a.z:03d}_{a.a:03d}.npz")
        if not os.path.exists(f):
            import glob

            raise SystemExit(f"arm {arm} failed: " + "".join(open(e).read()[-2000:] for e in glob.glob(od + "/*err*")))
        q = np.load(f, allow_pickle=True)
        out[arm] = {c: [float(x).hex() for x in np.asarray(q[k], dtype=np.float64).reshape(-1)]
                    for c, k in KEYS.items() if k in q.files}
    with open(a.out, "w") as fh:
        json.dump(out, fh, indent=0, sort_keys=True)
    shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    main()
