#!/usr/bin/env python3
"""Start-up correctness check: the start-up work must not move any number.

Each case is one fresh engine job (scripts/perfstart/job.py in a new interpreter, as a calculator job runs):
Fe-56, Zr-90, Au-197, U-238 at 1 MeV, at 14 MeV and on the library's 64-point grid (1 keV - 20 MeV). Every output
array of the job (all exclusive channels, totals incl. total / elastic / fission, level and residual-production
cross sections) is compared with a reference made by the engine before the change: same keys, same shapes, and
bit-identical, or at most REL relative difference (|a - b| / max(|a|, |b|)) where not.

    gate.py make REFDIR            # reference npz files with the engine as checked out (run on the old commit)
    gate.py check REFDIR [OUTDIR]  # run the cases again with this checkout, compare; exit 1 on any difference

tests/hf/test_perfstart_gate.py runs `check` when PERFSTART_REF points at a reference directory.
Extra environment for the new runs (e.g. INCOGNITA_STAGE_CACHE) is inherited, so the same check covers a cache on/off.
"""
import json, os, subprocess, sys, tempfile, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
NUCLIDES = [(26, 56), (40, 90), (79, 197), (92, 238)]
GRIDS = {"e1.0": ["--e-mev", "1.0"], "e14.0": ["--e-mev", "14.0"], "lib64": ["--lib64"]}
REL = 1e-12
# the channels the check names explicitly (they must be present in the reference and the new run)
NAMED = {"capture": "ch_xs000000", "elastic": "tot_elastic", "total": "tot_total", "np": "ch_xs010000",
         "na": "ch_xs000001", "n2n": "ch_xs200000", "fission": "tot_fission"}


def cases():
    for z, a in NUCLIDES:
        for g, args in GRIDS.items():
            yield f"{z:03d}_{a:03d}_{g}", ["--z", str(z), "--a", str(a)] + args


def run_case(args, out, env=None):
    t0 = time.time()
    p = subprocess.run([sys.executable, os.path.join(HERE, "job.py"), *args, "--out", out], capture_output=True, text=True,
                       cwd=ROOT, env=env, timeout=1800)
    if p.returncode != 0 or not os.path.exists(out):
        raise RuntimeError(f"job failed ({p.returncode}): {p.stderr.strip()[-600:]}")
    line = [ln for ln in p.stdout.splitlines() if ln.startswith("{")]
    info = json.loads(line[-1]) if line else {}
    info["proc_wall_s"] = round(time.time() - t0, 3)
    return info


def compare(ref, new):
    """{key: (n_cells_different, max_rel)} for every differing key, plus missing/extra keys and shape changes."""
    import numpy as np
    a, b = np.load(ref), np.load(new)
    ka, kb = set(a.files), set(b.files)
    bad = {}
    for k in sorted(ka - kb): bad[k] = "missing in new run"
    for k in sorted(kb - ka): bad[k] = "extra in new run"
    for k in sorted(ka & kb):
        x, y = np.asarray(a[k]), np.asarray(b[k])
        if x.shape != y.shape:
            bad[k] = f"shape {x.shape} -> {y.shape}"; continue
        same = (x == y) | (np.isnan(x) & np.isnan(y))
        if same.all(): continue
        d = np.abs(x - y)
        with np.errstate(all="ignore"):
            r = np.where(same, 0.0, d / np.maximum(np.abs(x), np.abs(y)))
        bad[k] = (int((~same).sum()), float(np.nanmax(r)))
    return bad, sorted(ka)


def make(refdir):
    os.makedirs(refdir, exist_ok=True)
    head = subprocess.run(["git", "-C", ROOT, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    dirty = subprocess.run(["git", "-C", ROOT, "status", "--porcelain", "physics"], capture_output=True, text=True).stdout.strip()
    meta = {"commit": head, "physics_dirty": bool(dirty), "cases": {}}
    for name, args in cases():
        meta["cases"][name] = run_case(args, os.path.join(refdir, name + ".npz"))
        print(name, json.dumps(meta["cases"][name]), flush=True)
    json.dump(meta, open(os.path.join(refdir, "REF.json"), "w"), indent=1)


def check(refdir, outdir=None, only=None):
    outdir = outdir or tempfile.mkdtemp(prefix="perfstart_gate_")
    os.makedirs(outdir, exist_ok=True)
    report = {}
    for name, args in cases():
        if only and not any(o in name for o in only): continue
        ref = os.path.join(refdir, name + ".npz")
        if not os.path.exists(ref):
            report[name] = {"err": "no reference"}; continue
        new = os.path.join(outdir, name + ".npz")
        info = run_case(args, new)
        bad, keys = compare(ref, new)
        # every named channel is open at 14 MeV and on the 64-point grid (fission: the actinide only)
        need = [] if name.endswith("e1.0") else [c for c in NAMED if c != "fission" or name.startswith("092")]
        missing_named = [c for c in need if NAMED[c] not in keys]
        worst = max([v[1] for v in bad.values() if isinstance(v, tuple)], default=0.0)
        ok = not missing_named and all(isinstance(v, tuple) and v[1] <= REL for v in bad.values())
        report[name] = dict(ok=ok, n_keys=len(keys), n_keys_differing=len(bad), max_rel=worst, missing_named=missing_named,
                            bad={k: v for k, v in list(bad.items())[:8]}, timing=info)
        print(name, "OK" if ok else "FAIL", "bit-identical" if not bad else f"{len(bad)} keys differ, max rel {worst:.3g}",
              json.dumps(info), flush=True)
    json.dump(report, open(os.path.join(outdir, "GATE.json"), "w"), indent=1)
    return report


if __name__ == "__main__":
    if len(sys.argv) < 3 or sys.argv[1] not in ("make", "check"):
        sys.exit(__doc__)
    if sys.argv[1] == "make":
        make(sys.argv[2])
    else:
        rep = check(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
        sys.exit(0 if all(r.get("ok") for r in rep.values()) else 1)
