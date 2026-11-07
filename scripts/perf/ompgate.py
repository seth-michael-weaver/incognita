#!/usr/bin/env python3
"""Optical-model speed gate: the production-configuration engine (scripts/perf/ompbench.py) on Fe-56, Zr-90, Au-197 and
U-238, at one energy (14 MeV) and on the 64-point library grid (1 keV - 20 MeV), compared BIT FOR BIT with a reference
written by the engine before the optical-model speed work (tests/hf/data/ompgate_ref.json).

Checked per case: the gate channels (capture, elastic, total, (n,p), (n,a), (n,2n), fission) value by value, and a
SHA-256 over every ch_* / tot_* array of the run's npz (all exclusive channels and totals). Each case runs with an empty
coupled-channels cache (INCOGNITA_CC_CACHE, so the cache is written on a miss); U-238 on the 64-point grid runs a second
time on the filled cache, so a cache hit must give the same bits as the solve.

usage: ompgate.py write [--ref FILE]      # make the reference (run on the baseline engine)
       ompgate.py check [--ref FILE]      # compare; exit 1 on any difference
Environment as ompbench.py (TALYS_DIR, ~/libv02/inputs or OMPGATE_INPUTS); OMPGATE_CPUS (taskset list, e.g. "12").
"""
import argparse, hashlib, json, os, shutil, subprocess, sys, tempfile
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[2]
REF = REPO / "tests" / "hf" / "data" / "ompgate_ref.json"
INPUTS = os.environ.get("OMPGATE_INPUTS", os.path.expanduser("~/libv02/inputs"))
TARGETS = [(26, 56), (40, 90), (79, 197), (92, 238)]
GATE = {"capture": "capture_mb", "elastic": "tot_elastic", "total": "tot_total", "np": "ch_xs010000",
        "na": "ch_xs000001", "n2n": "ch_xs200000", "fission": "tot_fission"}
E1 = [14.0e6]


def grid64():
    """the library grid: 64 log-spaced energies, 1 keV - 20 MeV (library/v0.1, capture_v01_indep.parquet energy_ev)"""
    return [float(x) for x in np.geomspace(1.0e3, 2.0e7, 64)]


def cases():
    return [(z, a, name, g) for z, a in TARGETS for name, g in (("e14", E1), ("g64", grid64()))]


def available():
    td = os.environ.get("TALYS_DIR", os.path.expanduser("~/relb61_strip"))
    return (Path(td, "structure").is_dir() and all(Path(INPUTS, "lines_P", f"V32_{z:03d}_{a:03d}.lines").is_file() for z, a in TARGETS)
            and Path(INPUTS, "sl_meas_b.csv").is_file())


def summary(npz):
    q = np.load(npz, allow_pickle=True)
    keys = sorted(k for k in q.files if k.startswith(("ch_", "tot_")))
    h = hashlib.sha256()
    for k in keys:
        a = np.ascontiguousarray(np.asarray(q[k], np.float64))
        h.update(k.encode() + b"\0" + str(a.shape).encode() + b"\0" + a.tobytes())
    ch = {}
    for c, k in GATE.items():
        kk = k if k in q.files else ("ch_xs000000" if k == "capture_mb" else None)
        ch[c] = [float(x).hex() for x in np.asarray(q[kk], np.float64).ravel()] if kk in q.files else None
    return dict(channels=ch, sha256=h.hexdigest(), keys=len(keys))


def run_case(z, a, grid, work, cc):
    g = Path(work) / "grid.json"; g.write_text(json.dumps(grid))
    out = Path(work) / "out"
    if out.exists(): shutil.rmtree(out)
    cmd = [sys.executable, str(REPO / "scripts" / "perf" / "ompbench.py"), "--z", str(z), "--a", str(a), "--grid", str(g),
           "--out", str(out), "--cc", str(cc), "--inputs", INPUTS]
    cpus = os.environ.get("OMPGATE_CPUS")
    if cpus and shutil.which("taskset"): cmd = ["taskset", "-c", cpus] + cmd
    p = subprocess.run(cmd, capture_output=True, text=True, cwd=REPO)
    line = [ln for ln in p.stdout.splitlines() if ln.startswith("{")]
    if p.returncode or not line: raise RuntimeError(f"ompbench {z} {a}: exit {p.returncode}\n{p.stderr[-2000:]}")
    r = json.loads(line[-1])
    if r["status"] != "ok": raise RuntimeError(f"ompbench {z} {a}: {r['status']} {r['err']}")
    return summary(out / f"{z:03d}_{a:03d}.npz"), r


def run_all(log=print):
    res = {}
    with tempfile.TemporaryDirectory(prefix="ompgate_") as tmp:
        for z, a, name, g in cases():
            key = f"{z}_{a}_{name}"
            cc = Path(tmp) / f"cc_{key}"; cc.mkdir()
            w = Path(tmp) / key; w.mkdir()
            res[key], r = run_case(z, a, g, w, cc)
            log(f"{key}: cold cache {r['cpu_s']} cpu-s")
            if (z, a, name) == (92, 238, "g64"):
                res[key + "_warm"], r = run_case(z, a, g, w, cc)
                log(f"{key}: warm cache {r['cpu_s']} cpu-s")
    return res


def compare(ref, got):
    bad = []
    for key, r in ref.items():
        g = got.get(key)
        if g is None: bad.append(f"{key}: missing"); continue
        for c, v in r["channels"].items():
            if g["channels"].get(c) != v:
                if v is None or g["channels"].get(c) is None: bad.append(f"{key} {c}: presence differs"); continue
                x = np.array([float.fromhex(s) for s in v]); y = np.array([float.fromhex(s) for s in g["channels"][c]])
                rel = float(np.max(np.abs(y - x) / np.maximum(np.abs(x), 1e-300))) if x.shape == y.shape else float("inf")
                bad.append(f"{key} {c}: max rel diff {rel:.3e}")
        if g["sha256"] != r["sha256"]: bad.append(f"{key}: ch_/tot_ digest differs ({g['keys']} vs {r['keys']} arrays)")
    return bad


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("mode", choices=["write", "check"]); ap.add_argument("--ref", default=str(REF))
    a = ap.parse_args()
    got = run_all()
    if a.mode == "write":
        Path(a.ref).parent.mkdir(parents=True, exist_ok=True)
        json.dump(got, open(a.ref, "w"), indent=0, sort_keys=True); print("wrote", a.ref); return
    bad = compare(json.load(open(a.ref)), got)
    print("\n".join(bad) if bad else "ompgate: all cases bit-identical")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
