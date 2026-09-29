#!/usr/bin/env python3
"""Speed benchmark: stock TALYS vs the INCOGNITA TALYS port, whole-process CPU seconds, same nuclides, same energies, one pinned core.

This is the protocol of SPEED50C (expected result: SPEED50C.md, raw data results/speed50c_raw.jsonl):
each timed run is a fresh child (`taskset -c CPU`), reaped with os.wait4 -> user+sys CPU of that child
(imports included for the port). 20 fixed nuclides x 20 energies (1 keV - 20 MeV), ABAB order across repeats.

Arms (--arms, comma-separated):
  talys            stock TALYS, one process per nuclide (default keywords, same energy file)
  <R>_cold         the port in repo <R>, one process per nuclide, empty coupled-channels (CC) cache
  <R>_cold_fused   same, with the opt-in fused GPU kernel (HF_CCGPU=1 HF_CCGPU_FUSED=1)
  <R>_warm         the port, one process per nuclide, CC cache filled by an untimed cold run first
  <R>_batch        all nuclides in ONE port process, empty CC cache, CPU only
  <R>_batch_gpu    same, HF_CCGPU=1 (torch GPU radial loops)
  <R>_batch_fused  same, fused GPU kernel
  <R>_batch_warm   all nuclides in one process, CC cache filled by an earlier run
<R> is a repo label: `new` = this repository (default); more with --repo LABEL=PATH (for example an older
commit checked out with `git worktree add`, to measure a before/after in the same session; SPEED50C used
`base` = c423b78d and `b50b` = 1260ac1c). Each repo needs its own .venv (uv sync) and `make native`.

    python incognita/bench/speed/bench.py --cpu 15 --repeats 2 --out /abs/path/out
    python incognita/bench/speed/bench.py --out /abs/out --arms talys,new_cold,new_batch,new_batch_warm --only fe56,au197
    python incognita/bench/speed/bench.py report DIR          # re-make DIR/REPORT.md from DIR/raw.jsonl

The stock TALYS binary: --talys-bin, else $TALYS_BIN, else $TALYS_DIR/bin/talys (default ~/opt/talys-src).
A clean result needs an idle machine (load < 2) and the native kernels built (`make native`): without them the
port runs ~4x slower, silently. Only same-session ratios are claims; this hardware drifted 15-50 % between runs.
Wall seconds are recorded next to CPU seconds: a GPU arm's device time shows in wall, not in CPU.
--out is always resolved to an absolute path: the engine runs with cwd = the repo, and a relative --out once
put every cold arm's cache inside the repo, where later "cold" runs found it warm.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[3]
FUSED = {"HF_CCGPU": "1", "HF_CCGPU_FUSED": "1"}
NUC = [('fe', 26, 56), ('ni', 28, 58), ('cu', 29, 63), ('zr', 40, 90), ('mo', 42, 98), ('sn', 50, 120), ('i', 53, 127),
       ('ba', 56, 138), ('nd', 60, 148), ('sm', 62, 154), ('gd', 64, 158), ('er', 68, 166), ('hf', 72, 178), ('w', 74, 184),
       ('au', 79, 197), ('pb', 82, 208), ('th', 90, 232), ('u', 92, 235), ('u', 92, 238), ('pu', 94, 239)]
E_MEV = [float(x) for x in np.round(np.geomspace(0.001, 20.0, 20), 6)]
SINGLE_KINDS = ("cold", "cold_fused", "warm")


def talys_dir() -> Path:
    return Path(os.environ.get("TALYS_DIR", str(Path.home() / "opt" / "talys-src"))).expanduser()


def timed(cmd, cwd, env=None, stdin=None):
    t0 = time.time()
    p = subprocess.Popen(cmd, cwd=cwd, env=env, stdin=stdin, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    _, status, ru = os.wait4(p.pid, 0)
    err = p.stderr.read().decode(errors='replace')[-400:]
    return dict(cpu_s=ru.ru_utime + ru.ru_stime, wall_s=time.time() - t0, rc=os.waitstatus_to_exitcode(status),
                maxrss_mb=ru.ru_maxrss / 1024, err=err if status else '')


def run_talys(talys_bin: Path, cpu, sym, z, a, work):
    d = Path(tempfile.mkdtemp(dir=work))
    (d / 'energies').write_text('\n'.join(str(e) for e in E_MEV) + '\n')
    (d / 'talys.inp').write_text(f'projectile n\nelement {sym}\nmass {a}\nenergy energies\n')
    with open(d / 'talys.inp') as f:
        r = timed(['taskset', '-c', str(cpu), str(talys_bin)], d, stdin=f)
    shutil.rmtree(d, ignore_errors=True)
    return r


def run_engine(repo: Path, cpu: int, only: str, work: Path, cc_cache: Path, extra_env: dict):
    out = Path(tempfile.mkdtemp(dir=work))
    grid = out / "grid.json"
    grid.write_text(json.dumps([e * 1e6 for e in E_MEV]))
    env = dict(os.environ, TALYS_DIR=str(talys_dir()), OMP_NUM_THREADS="1", **extra_env)
    cmd = ["taskset", "-c", str(cpu), str(repo / ".venv/bin/python"), "scripts/bestfit/engine_curves.py",
           "--out", str(out / "o"), "--only", only, "--cpus", f"{cpu}-{cpu}", "--grid", str(grid),
           "--cc-cache", str(cc_cache), "--no-ingredients"]
    r = timed(cmd, repo, env=env)
    r["n_done"] = len(list((out / "o").glob("*.npz")))
    return r, out


def split_arm(arm):
    """'new_cold_fused' -> ('new', 'cold_fused'); 'talys' -> ('talys', '')."""
    if arm == "talys":
        return "talys", ""
    label, _, kind = arm.partition("_")
    return label, kind


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cpu", type=int, default=15, help="the one core every timed child is pinned to")
    ap.add_argument("--repeats", type=int, default=2)
    ap.add_argument("--out", required=True, help="output directory (resolved to an absolute path)")
    ap.add_argument("--only", default="", help="subset of the 20 nuclides, e.g. fe56,au197")
    ap.add_argument("--arms", default="talys,new_cold,new_cold_fused,new_warm,new_batch,new_batch_gpu,"
                    "new_batch_fused,new_batch_warm")
    ap.add_argument("--repo", action="append", default=[], metavar="LABEL=PATH",
                    help="another checkout to time as arms LABEL_*; `new` is this repository")
    ap.add_argument("--talys-bin", default=os.environ.get("TALYS_BIN", ""),
                    help="stock TALYS executable (default $TALYS_BIN, else $TALYS_DIR/bin/talys)")
    a = ap.parse_args()
    repos = {"new": REPO}
    for s in a.repo:
        k, _, v = s.partition("=")
        repos[k] = Path(v).expanduser().resolve()
    arms = a.arms.split(",")
    talys_bin = Path(a.talys_bin).expanduser() if a.talys_bin else talys_dir() / "bin" / "talys"
    for arm in arms:
        label, kind = split_arm(arm)
        if label == "talys":
            if not talys_bin.exists():
                raise SystemExit(f"arm talys: no TALYS executable at {talys_bin} (build it per docs/talys-install.md "
                                 "or pass --talys-bin)")
        elif label not in repos:
            raise SystemExit(f"arm {arm}: unknown repo label {label!r}; add --repo {label}=PATH")
        elif not (repos[label] / ".venv/bin/python").exists():
            raise SystemExit(f"arm {arm}: {repos[label]}/.venv/bin/python missing (run uv sync there)")
    out = Path(a.out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    work = out / "work"
    work.mkdir(exist_ok=True)
    nuc = [n for n in NUC if not a.only or f"{n[0]}{n[2]}".lower() in a.only.lower().split(",")]
    meta = {k: subprocess.run(["git", "-C", str(v), "rev-parse", "HEAD"], capture_output=True,
                              text=True).stdout.strip() for k, v in repos.items()}
    meta.update(native_engine_loaded={k: subprocess.run(
        [str(v / ".venv/bin/python"), "-c", "from physics.hf import engine_c; print(engine_c.lib() is not None)"],
        cwd=v, capture_output=True, text=True).stdout.strip() for k, v in repos.items()})
    meta.update(cpu=a.cpu, load_before=os.getloadavg(), started=time.strftime("%F %T"), arms=arms,
                energies_mev=E_MEV)
    (out / "meta.json").write_text(json.dumps(meta, indent=1))
    log = open(out / "raw.jsonl", "a")

    def rec(r, **kw):
        r.update(kw, load=os.getloadavg()[0])
        log.write(json.dumps(r) + "\n")
        log.flush()
        print(f"{kw.get('nuclide', 'ALL'):7s} rep{kw['rep']} {kw['arm']:15s} cpu {r['cpu_s']:8.2f}s "
              f"wall {r['wall_s']:7.2f}s rc {r['rc']} {r.get('n_done', '')} {r['err'][-150:]}", flush=True)

    single = [x for x in arms if x == "talys" or split_arm(x)[1] in SINGLE_KINDS]
    for rep in range(a.repeats):
        for sym, z, A in nuc:
            name = f"{sym.capitalize()}-{A}"
            cc = out / f"cc_{z}_{A}_{rep}"
            shutil.rmtree(cc, ignore_errors=True)
            cc.mkdir()
            order = list(single) if rep % 2 == 0 else list(reversed(single))
            for arm in order:
                if arm == "talys":
                    r = run_talys(talys_bin, a.cpu, sym, z, A, work)
                else:
                    which, kind = split_arm(arm)
                    c = cc if kind == "warm" else (out / f"ccx_{z}_{A}_{rep}_{arm}")
                    if kind.startswith("cold"):
                        shutil.rmtree(c, ignore_errors=True)
                        c.mkdir()
                    if kind == "warm" and not any(cc.iterdir()):
                        _, o = run_engine(repos[which], a.cpu, f"{z}-{A}", work, cc, {})   # untimed fill
                        shutil.rmtree(o, ignore_errors=True)
                    r, o = run_engine(repos[which], a.cpu, f"{z}-{A}", work, c,
                                      FUSED if arm.endswith("_fused") else {})
                    shutil.rmtree(o, ignore_errors=True)
                rec(r, arm=arm, nuclide=name, rep=rep)
    only = ",".join(f"{z}-{A}" for _, z, A in nuc)
    batch = [x for x in arms if split_arm(x)[1].startswith("batch")]
    for rep in range(a.repeats):
        order = batch if rep % 2 == 0 else list(reversed(batch))
        for arm in order:
            which = split_arm(arm)[0]
            warm_cc = out / f"cc_batch_warm_{which}"
            env = {}
            if arm.endswith("_batch_gpu"):
                env = {"HF_CCGPU": "1", "ENGINE_PREFETCH": "1000"}
            if arm.endswith("_batch_fused"):
                env = dict(FUSED, ENGINE_PREFETCH="1000")
            if arm.endswith("_batch_warm"):
                if not warm_cc.is_dir():
                    warm_cc.mkdir()
                    _, o = run_engine(repos[which], a.cpu, only, work, warm_cc, {})
                    shutil.rmtree(o, ignore_errors=True)
                cc = warm_cc
            else:
                cc = Path(tempfile.mkdtemp(dir=work))
            r, o = run_engine(repos[which], a.cpu, only, work, cc, env)
            if rep == 0:   # keep the first repeat's batch outputs for an accuracy check
                dst = out / f"outputs_{arm}"
                shutil.rmtree(dst, ignore_errors=True)
                if (o / "o").exists():
                    shutil.move(str(o / "o"), dst)
            shutil.rmtree(o, ignore_errors=True)
            if cc != warm_cc:
                shutil.rmtree(cc, ignore_errors=True)
            rec(r, arm=arm, rep=rep, nuclide="ALL")
    report(out)


def report(out: Path, raw: Path | None = None, dest: Path | None = None):
    """Median CPU/wall per arm and the ratios to stock TALYS, from raw.jsonl (identical to SPEED50C's report)."""
    rs = [json.loads(line) for line in open(raw or out / "raw.jsonl")]
    med = {}
    for r in rs:
        med.setdefault((r["nuclide"], r["arm"]), []).append(r)
    arms_single = [a for a in dict.fromkeys(r["arm"] for r in rs if r["nuclide"] != "ALL")]
    known = ["talys", "base_cold", "new_cold", "new_cold_fused", "new_warm"]
    arms_single = [a for a in known if a in arms_single] + [a for a in arms_single if a not in known]
    L = ["| nuclide | " + " | ".join(f"{a} CPU-s" for a in arms_single) + " |",
         "|---" * (len(arms_single) + 1) + "|"]
    S = {a: 0.0 for a in arms_single}
    for n in dict.fromkeys(r["nuclide"] for r in rs if r["nuclide"] != "ALL"):
        row = []
        for a in arms_single:
            v = med.get((n, a))
            m = float(np.median([x["cpu_s"] for x in v])) if v else float("nan")
            S[a] += m if np.isfinite(m) else 0.0
            row.append(f"{m:.2f}")
        L.append(f"| {n} | " + " | ".join(row) + " |")
    L.append("| **sum** | " + " | ".join(f"**{S[a]:.1f}**" for a in arms_single) + " |")
    t = S.get("talys", float("nan"))
    L.append("")
    L.append("| arm | CPU-s (median) | wall-s (median) | TALYS sum / CPU | TALYS sum / wall | n |")
    L.append("|---|---|---|---|---|---|")
    for a in arms_single[1:]:
        L.append(f"| {a} (sum of per-nuclide processes) | {S[a]:.1f} | | {t / S[a]:.2f}x | | |")
    for (n, a), v in med.items():
        if n != "ALL":
            continue
        c = float(np.median([x["cpu_s"] for x in v]))
        w = float(np.median([x["wall_s"] for x in v]))
        L.append(f"| {a} | {c:.1f} | {w:.1f} | {t / c:.2f}x | {t / w:.2f}x | {v[0].get('n_done')} |")
    loads = [r["load"] for r in rs]
    L.append("")
    L.append(f"load (1-min) during runs: median {np.median(loads):.1f}, max {np.max(loads):.1f}")
    dest = dest or out / "REPORT.md"
    dest.write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "report":
        ap = argparse.ArgumentParser(prog="bench.py report")
        ap.add_argument("dir", type=Path, help="a bench output directory (reads DIR/raw.jsonl)")
        ap.add_argument("--raw", type=Path, default=None, help="read this raw.jsonl instead")
        ap.add_argument("--dest", type=Path, default=None, help="write the report here instead of DIR/REPORT.md")
        x = ap.parse_args(sys.argv[2:])
        report(x.dir, x.raw, x.dest)
    else:
        main()
