#!/usr/bin/env python3
"""PERFBENCH profiler: where an engine job's time goes (feeds scripts/perf/PROFILE.md).

For each target and grid it runs bench.py's in-process driver (one target per fresh process, so start-up is included), warm
coupled-channels cache (primed by an untimed run first), three ways:
  plain     no profiler: wall/CPU, and the engine's own always-on stage timer (physics/hf/stagetime.py: exclusive CPU-s per
            stage, setup.structure, setup.ld, incident.cc_solve, compound, ...; it only covers engine_c.run's insides)
  pyspy     py-spy record --idle --native (wall clock, includes I/O waits and C frames). The report gives
              (a) inclusive wall seconds of named pipeline blocks (share of samples whose stack contains the block's frame)
              (b) a partition of all samples by the innermost physics/hf/<area> frame (structure, density, ecis, ...)
              (c) the top leaf frames (where samples land: libc stat/open, gc, C kernels, torch ops)
  cprofile  own-time top list (cProfile's cumulative times of the outer pipeline frames are unreliable in this process:
            entries such as engine_pool._setup and r52pool.h_rule come back empty, so blocks are taken from py-spy)
Seconds from py-spy = share x the plain run's wall time is NOT used: the py-spy run's own sample count / rate is the wall.

usage (WSL): python3 scripts/perf/profile_engine.py [--nuclides Fe-56,Au-197,U-238] [--grids 1,64] [--out DIR]
             [--no-pyspy] [--no-cprofile] [--local] [--report-only]
--local runs copies of the scripts from WSL disk (DIR/code) instead of the repo (which may be on /mnt/c, 9p).
Writes DIR/<nuc>_<grid>.{plain.json,prof,pyspy.txt} and DIR/report.md.
"""
from __future__ import annotations

import argparse
import collections
import json
import os
import re
import shutil
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bench as B  # noqa: E402

# inclusive pipeline blocks, matched against py-spy frames 'function (file:line)'
BLOCKS = [
    ("startup  engine_grid.preload: numpy, prodrun/pprun/r52pool/engine_pool, jointcap", r"^preload \(engine_grid\.py"),
    ("startup  engine_pool._setup: import torch + physics.hf engine modules + C kernels", r"^_setup \(engine_pool\.py"),
    ("startup    import torch (whole)", r"^<module> \(torch/__init__\.py"),
    ("startup      torch _load_global_deps / CUDA lib glob", r"^(_load_global_deps|_get_cuda_dep_paths|_preload_cuda_deps) \(torch/__init__"),
    ("startup    engine_c.lib (dlopen C kernels)", r"^lib \(physics/hf/engine_c\.py"),
    ("any import (importlib._find_and_load, outermost)", r"^_find_and_load \(<frozen importlib\._bootstrap>"),
    ("per arm  r52pool.h_rule: ISOHOLD h = 3 x (new_cascade + ingredients)", r"^h_rule \(r52pool\.py"),
    ("per arm  engine_pool.run_item: the production run", r"^run_item \(engine_pool\.py"),
    ("           warmrun.new_cascade (any caller)", r"^new_cascade \(physics/hf/warmrun\.py"),
    ("           engine_c.run (reaction calculation)", r"^run \(physics/hf/engine_c\.py"),
    ("           ingredients() (h_rule x3 + npz dump x1 per arm)", r"^ingredients \(physics/hf/ingredients\.py"),
    ("           np.savez_compressed", r"^savez_compressed \("),
    ("per arm  write_dir_log (re-solves spherical sigma_R)", r"^write_dir_log \(r52pool\.py"),
    ("per arm  write_xr", r"^write_xr \(r52pool\.py"),
    ("chartrun.drop_target_caches (incl. gc.collect)", r"^drop_target_caches \(physics/hf/chartrun\.py"),
    ("fitlib deck (cards/activate/table_lines)", r"^(_cards|activate|table_lines|_lines_key) \(physics/hf/input/fitlib\.py"),
    ("direct/chain.direct_result (DWBA + direct capture)", r"^direct_result \(physics/hf/direct/chain\.py"),
    ("dwbaunit._evaluate (autorot decision)", r"^_evaluate \(physics/hf/direct/dwbaunit\.py"),
    ("ecis/reference.coupled_band (coupled channels)", r"^coupled_band \(physics/hf/ecis/reference\.py"),
    ("structure/deformation.deformation", r"^deformation \(physics/hf/structure/deformation\.py"),
]
FS_LEAF = re.compile(r"^(fstatat64|__open_nocancel|open64|getdents64|fstat64|read|__xstat|lstat64|newfstatat|statx) \(libc")


def area_of(frame):
    m = re.search(r"\((physics/hf/(?:[a-z_0-9]+/)?)[a-zA-Z_0-9]+\.py:", frame)
    if not m: return None
    p = m.group(1)
    return p if p != "physics/hf/" else "physics/hf/" + re.search(r"\(physics/hf/([a-zA-Z_0-9]+)\.py", frame).group(1) + ".py"


def pyspy_report(path, top=15):
    blocks = collections.Counter(); areas = collections.Counter(); leaf = collections.Counter(); tot = 0; fs_import = fs_all = 0
    rx = [(lab, re.compile(r)) for lab, r in BLOCKS]
    for ln in open(path):
        ln = ln.rstrip()
        if not ln: continue
        st, _, n = ln.rpartition(" "); n = int(n); tot += n
        fr = st.split(";")
        for lab, r in rx:
            if any(r.search(f) for f in fr): blocks[lab] += n
        a = None
        for f in fr:
            a = area_of(f) or a
        if a is None:
            if any("importlib" in f for f in fr): a = "(imports outside physics.hf)"
            elif any(re.search(r"\((pprun|prodrun|r52pool|engine_pool|engine_grid|bench)\.py", f) for f in fr): a = "(runner scripts, not in physics.hf)"
            else: a = "(interpreter / other)"
        areas[a] += n
        leaf[fr[-1]] += n
        if FS_LEAF.search(fr[-1]):
            fs_all += n
            if any("importlib" in f for f in fr): fs_import += n
    return tot, blocks, areas, leaf.most_common(top), fs_all, fs_import


def cprofile_own(path, top=20):
    import pstats
    st = pstats.Stats(path)
    own = sorted(((tt, f"{os.path.relpath(fn, B.ENG) if fn.startswith(B.ENG) else fn}:{ln}({nm})", nc)
                  for (fn, ln, nm), (cc, nc, tt, ct, callers) in st.stats.items()), reverse=True)[:top]
    return st.total_tt, own


def report(a, n, g, tag, rate):
    z, A, comp = B.NUCLIDES[n]
    R = []
    pj = os.path.join(a.out, tag + ".plain.json")
    if os.path.exists(pj):
        j = json.load(open(pj)); r0 = (j.get("results") or [{}])[0]
        R += [f"## {n}, {g} energies ({comp})", "",
              f"plain: process wall {j.get('_wall', 0):.2f} s, cpu {j.get('_cpu', 0):.2f} s; driver pre-run imports {j.get('import_s', 0):.2f} s; "
              f"target run wall {r0.get('wall_s', 0):.2f} s, cpu {r0.get('cpu_s', 0):.2f} s; err {r0.get('err', '')!r}", ""]
        agg = collections.Counter(); calls = collections.Counter()
        for snap in r0.get("stages", []):
            for k, v in (snap.get("stage_cpu_s") or {}).items(): agg[k] += v
        if agg:
            R += [f"stagetime (exclusive CPU s inside engine_c.run, summed over arms; total {sum(agg.values()):.2f} s):", "",
                  "| stage | CPU s |", "|---|---|"] + [f"| {k} | {v:.3f} |" for k, v in agg.most_common() if v >= 0.001] + [""]
    sf = os.path.join(a.out, tag + ".pyspy.txt")
    if os.path.exists(sf):
        tot, blocks, areas, leaf, fs_all, fs_imp = pyspy_report(sf)
        s = lambda c: f"{c / rate:.2f}"
        R += [f"py-spy --idle --native: {tot} samples at {rate} Hz = {tot / rate:.2f} s wall (py-spy run). File-system leaf "
              f"(stat/open/getdents/read in libc): {s(fs_all)} s, of it inside imports {s(fs_imp)} s.", "",
              "| block (inclusive) | wall s | share |", "|---|---|---|"]
        R += [f"| {lab.strip()} | {s(blocks[lab])} | {blocks[lab] / tot:.0%} |" for lab, _ in BLOCKS] + [""]
        R += ["| innermost area (partition) | wall s | share |", "|---|---|---|"]
        R += [f"| {k} | {s(c)} | {c / tot:.0%} |" for k, c in areas.most_common(18)] + [""]
        R += ["| leaf frame | wall s | share |", "|---|---|---|"]
        R += [f"| `{k[:110]}` | {s(c)} | {c / tot:.0%} |" for k, c in leaf] + [""]
    pf = os.path.join(a.out, tag + ".prof")
    if os.path.exists(pf):
        total, own = cprofile_own(pf)
        R += [f"cProfile own time (total {total:.2f} s, profiler-inflated):", "", "| own s | function | calls |", "|---|---|---|"]
        R += [f"| {tt:.3f} | `{k}` | {nc} |" for tt, k, nc in own] + [""]
    return R


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nuclides", default="Fe-56,Au-197,U-238")
    ap.add_argument("--grids", default="1,64"); ap.add_argument("--energy", type=float, default=1e6)
    ap.add_argument("--out", default=os.path.join(B.H, "perfbench_out", "prof"))
    ap.add_argument("--no-pyspy", action="store_true"); ap.add_argument("--no-cprofile", action="store_true")
    ap.add_argument("--local", action="store_true"); ap.add_argument("--report-only", action="store_true")
    ap.add_argument("--rate", type=int, default=100)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True); cc = os.path.join(a.out, "cc"); os.makedirs(cc, exist_ok=True)
    if a.local: B.stage_local(os.path.join(a.out, "code"))
    grid64 = json.load(open(B.GRID64)); pyspy = shutil.which("py-spy") or os.path.join(os.path.dirname(B.PY), "py-spy")
    R = [f"# engine profile {time.strftime('%Y-%m-%d %H:%M')}", "",
         f"engine {B.ENG}; scripts {B.TW}; warm CC cache; one target per fresh process; nice 10", ""]
    for n in a.nuclides.split(","):
        z, A, comp = B.NUCLIDES[n]
        smin = None if a.report_only else B.run_smin(z, A, 10)[0]
        for g in a.grids.split(","):
            grid = [a.energy] if g == "1" else grid64; tag = f"{n}_{g}"; w = os.path.join(a.out, "w_" + tag)
            if not a.report_only:
                B.run_multi([n], grid, {n: smin}, cc, w, 10)        # prime the CC cache (untimed)
                j, wall, cpu = B.run_multi([n], grid, {n: smin}, cc, w, 10)
                j["_wall"], j["_cpu"] = wall, cpu
                json.dump(j, open(os.path.join(a.out, tag + ".plain.json"), "w"))
                if not a.no_cprofile:
                    B.run_multi([n], grid, {n: smin}, cc, w, 10, profile=os.path.join(a.out, tag + ".prof"))
                if not a.no_pyspy:
                    sf = os.path.join(a.out, tag + ".pyspy.txt")
                    B.run_multi([n], grid, {n: smin}, cc, w, 10, pyspy=(pyspy, sf, a.rate))
            R += report(a, n, len(grid), tag, a.rate)
            print(f"{tag} done", flush=True)
    open(os.path.join(a.out, "report.md"), "w").write("\n".join(R) + "\n")
    print(f"report: {os.path.join(a.out, 'report.md')}")


if __name__ == "__main__":
    main()
