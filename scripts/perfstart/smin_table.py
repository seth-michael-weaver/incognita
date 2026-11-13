#!/usr/bin/env python3
"""Prebuilt table of the compound nucleus' separation energies for the calculator's grid-top pad.

scripts/talysworld/engine_job.py pads a job's grid when min S(CN) < 0 and gets S by starting a SECOND Python process that
imports the engine and builds the target's structure (`dens_reference._structure_of`): ~1.4 s of a ~5 s job. S depends
only on the engine's masses, so this script computes it once for every target the deck has lines for, in one process with
the job's own environment, and writes one small JSON table. A job then needs one dictionary lookup (no numpy, no torch).

    smin_table.py build [--eng ENGINE_DIR] [--out FILE] [--verify N]   # run with the engine's venv python
    smin_table.py get Z A [--table FILE]                                # prints the 7 S values (MeV) or exits 1

Key: the table records the engine commit (ENGINE_COMMIT / git HEAD) and a sha256 over the engine's mass tables
($TALYS_DIR/structure/masses, file names + sizes + mtimes); `lookup()` returns None when either no longer matches (stale)
or the nuclide is missing, and the caller falls back to the subprocess. --verify N re-computes N random entries in
separate processes exactly as engine_job.cn_separation_mev does and requires bit-identical floats.
"""
import argparse, hashlib, json, os, random, subprocess, sys, time

H = os.path.expanduser("~")
DEFAULT_ENG = os.environ.get("TW_ENG", f"{H}/fastgate_data/eng/16606b356d6e")
DEFAULT_INP = os.environ.get("TW_INPUTS", f"{H}/libv02/inputs")
HERE = os.path.dirname(os.path.abspath(__file__))


def default_table(eng=DEFAULT_ENG):
    return os.path.join(H, "talysworld_data", f"smin_{os.path.basename(os.path.normpath(eng))}.json")


def engine_commit(eng):
    p = os.path.join(eng, "ENGINE_COMMIT")
    if os.path.exists(p):
        return open(p).read().strip()
    r = subprocess.run(["git", "-C", eng, "rev-parse", "HEAD"], capture_output=True, text=True)
    return r.stdout.strip()


def masses_stamp(talys_dir=None):
    """sha256 over (relative path, size, mtime_ns) of every file under $TALYS_DIR/structure/masses: cheap (stat only)."""
    root = os.path.join(talys_dir or os.environ.get("TALYS_DIR", f"{H}/relb61_strip"), "structure", "masses")
    h = hashlib.sha256()
    for d, dirs, files in sorted(os.walk(root)):
        dirs.sort()
        for f in sorted(files):
            st = os.stat(os.path.join(d, f))
            h.update(f"{os.path.relpath(os.path.join(d, f), root)}\0{st.st_size}\0{st.st_mtime_ns}\n".encode())
    return h.hexdigest()[:32]


_TABLES = {}


def lookup(z, a, table=None, eng=DEFAULT_ENG, talys_dir=None):
    """[S_0 .. S_6] (MeV) of the compound nucleus of n + (z, a) from the prebuilt table, or None (missing / stale)."""
    table = table or default_table(eng)
    t = _TABLES.get(table)
    if t is None:
        try:
            t = json.load(open(table))
        except (OSError, ValueError):
            return None
        ok = t.get("engine_commit") == engine_commit(eng) and t.get("masses_stamp") == masses_stamp(talys_dir)
        t = _TABLES[table] = t if ok else {}
    v = t.get("s", {}).get(f"{int(z)},{int(a)}") if t else None
    return list(v) if v else None


def targets(inp):
    za = set()
    for sub in ("lines_P", "lines_A", "actjs_lines_P", "actjs_lines_A"):
        d = os.path.join(inp, sub)
        if not os.path.isdir(d): continue
        for f in os.listdir(d):
            if f.startswith("V32_") and f.endswith(".lines"):
                _, z, a = f[:-6].split("_"); za.add((int(z), int(a)))
    return sorted(za)


def build(eng, out, inp, verify):
    sys.path.insert(0, os.path.join(os.path.dirname(HERE), "talysworld"))
    import engine_job as EJ  # noqa: F401  (sets the job environment exactly as a calculator job has it)
    sys.path.insert(0, eng); os.chdir(eng)
    from physics.hf.compound.dens_reference import _structure_of as S
    za = targets(inp); t0 = time.time(); s = {}; err = {}
    for i, (z, a) in enumerate(za):
        try:
            _o, _p, m = S(z, a)
            s[f"{z},{a}"] = [float(m.s_mev[0, 0, t]) for t in range(7)]
        except Exception as ex:  # noqa: BLE001  (a nuclide the engine cannot build: left out, the job falls back)
            err[f"{z},{a}"] = f"{type(ex).__name__}: {ex}"[:200]
        if i % 200 == 0: print(i, len(za), f"{time.time() - t0:.0f}s", flush=True)
    tab = dict(engine_commit=engine_commit(eng), masses_stamp=masses_stamp(), engine=eng, n=len(s), errors=err,
               built=time.strftime("%Y-%m-%d %H:%M:%S"), s=s)
    if verify:
        rng = random.Random(1); pick = rng.sample(sorted(s), min(verify, len(s)))
        code = ("import json,sys; from physics.hf.compound.dens_reference import _structure_of as S; "
                "o,p,m=S(int(sys.argv[1]),int(sys.argv[2])); print(json.dumps([float(m.s_mev[0,0,t]) for t in range(7)]))")
        for k in pick:
            z, a = k.split(",")
            p = subprocess.run([sys.executable, "-c", code, z, a], capture_output=True, text=True, cwd=eng, timeout=600)
            ref = json.loads([ln for ln in p.stdout.splitlines() if ln.startswith("[")][-1])
            if ref != s[k]:
                raise SystemExit(f"verify: {k} table {s[k]} != fresh process {ref}")
        tab["verified"] = len(pick)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    tmp = out + ".tmp"; json.dump(tab, open(tmp, "w")); os.replace(tmp, out)
    print(f"wrote {out}: {len(s)} nuclides, {len(err)} errors, verified {tab.get('verified', 0)}, {time.time() - t0:.0f}s")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["build", "get"]); ap.add_argument("za", nargs="*", type=int)
    ap.add_argument("--eng", default=DEFAULT_ENG); ap.add_argument("--out"); ap.add_argument("--table")
    ap.add_argument("--inputs", default=DEFAULT_INP); ap.add_argument("--verify", type=int, default=0)
    a = ap.parse_args()
    if a.cmd == "build":
        build(a.eng, a.out or default_table(a.eng), a.inputs, a.verify)
    else:
        v = lookup(a.za[0], a.za[1], a.table, a.eng)
        if v is None: sys.exit(1)
        print(json.dumps(v))
