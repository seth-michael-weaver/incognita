#!/usr/bin/env python3
"""Reproducible speed benchmark: the Incognita engine against stock TALYS-2, same machine.

What is timed, per nuclide (each run is a fresh process pinned to one CPU with `taskset`, one
thread, CPU time = user + sys from `os.wait4`):

  talys      stock TALYS, minimal default input (projectile, element, mass, energy file). No dump,
             debug or extra output keywords: those make TALYS several times slower and would
             inflate the ratio.
  nocache    the engine, coupled-channels disk cache off (`INCOGNITA_CC_CACHE` unset).
  cold       the engine with an empty cache directory (the first run of a sweep pays this).
  warm       the engine with a cache directory already filled by an earlier run of the same
             target and energies (what later runs of a parameter sweep or a rerun see).

Engine runs report two numbers: the whole process (Python start-up and imports included) and the
per-target compute alone (what a long-lived worker pays per target). Stock TALYS is always the
whole process. Repeats are interleaved: every repeat visits every nuclide, and the arm order
alternates (talys, nocache, cold, warm / warm, cold, nocache, talys) so drifting background load
hits all arms alike. Medians over repeats are reported.

Parity: the no-cache engine run and the TALYS run are compared at the benchmark energies on total,
elastic, nonelastic and capture (residual production of Z, A+1), with the same structure
database, as max and median |log10(engine / TALYS)|. The cache arms are also checked to agree
with the no-cache arm.

    uv run python scripts/bench_vs_talys.py --talys /path/to/talys/bin/talys \\
        --talys-structure /path/to/talys/structure --nuclides mix12 --energies grid64 \\
        --cpus 8 --repeats 3 --out out/bench

Writes `<out>/bench.json` (every run, provenance, summary) and `<out>/bench.md` (tables).
Needs a TALYS binary and its structure database, so it is not run in CI.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import re
import shutil
import statistics
import subprocess
import sys
import tempfile
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

ARMS = ("talys", "nocache", "cold", "warm")
OBSERVABLES = ("total", "elastic", "nonelastic", "capture")

# 3 spherical, 2 vibrational, 4 rotational, 3 actinide (collective type from TALYS's
# structure/deformation files: S, V, R)
NUCLIDE_PRESETS: dict[str, list[str]] = {
    "mix12": ["Ni-58", "Zr-90", "Sn-118", "Ge-74", "Cd-112", "Sm-152", "Gd-157", "Dy-163",
              "W-184", "Th-232", "U-235", "U-238"],
    "quick": ["Fe-56", "Dy-163"],
}
ENERGY_PRESETS = ("grid64", "grid16", "short")

SYMBOLS = (
    "n H He Li Be B C N O F Ne Na Mg Al Si P S Cl Ar K Ca Sc Ti V Cr Mn Fe Co Ni Cu Zn Ga Ge As "
    "Se Br Kr Rb Sr Y Zr Nb Mo Tc Ru Rh Pd Ag Cd In Sn Sb Te I Xe Cs Ba La Ce Pr Nd Pm Sm Eu Gd "
    "Tb Dy Ho Er Tm Yb Lu Hf Ta W Re Os Ir Pt Au Hg Tl Pb Bi Po At Rn Fr Ra Ac Th Pa U Np Pu Am "
    "Cm Bk Cf Es Fm Md No Lr Rf Db Sg Bh Hs Mt Ds Rg Cn"
).split()


# ----------------------------------------------------------------------------- pure helpers


def parse_nuclide(tok: str) -> tuple[int, int]:
    """'U-238', 'u238', '92-238' -> (92, 238)."""
    tok = tok.strip()
    m = re.fullmatch(r"(\d+)-(\d+)", tok)
    if m:
        return int(m.group(1)), int(m.group(2))
    m = re.fullmatch(r"([A-Za-z]{1,2})-?(\d+)", tok)
    if not m:
        raise ValueError(f"cannot parse nuclide {tok!r} (use e.g. U-238 or 92-238)")
    sym = m.group(1).capitalize()
    if sym not in SYMBOLS[1:]:
        raise ValueError(f"unknown element {m.group(1)!r}")
    return SYMBOLS.index(sym), int(m.group(2))


def parse_nuclides(spec: str) -> list[tuple[int, int]]:
    """A preset name or a comma-separated list."""
    if spec in NUCLIDE_PRESETS:
        return [parse_nuclide(t) for t in NUCLIDE_PRESETS[spec]]
    return [parse_nuclide(t) for t in spec.split(",") if t.strip()]


def label(Z: int, A: int) -> str:
    return f"{SYMBOLS[Z]}-{A}"


def energies_mev(preset: str) -> list[float]:
    """Incident energies in MeV. grid64 is the engine's standard 64-point grid (1 keV-20 MeV,
    log-spaced, float32-rounded as the engine driver does)."""
    import numpy as np

    n = {"grid64": 64, "grid16": 16}.get(preset)
    if n is not None:
        ev = np.logspace(3.0, np.log10(2e7), n)
        return [float(np.float32(e)) for e in ev / 1e6]
    if preset == "short":
        return [0.01, 0.1, 1.0, 5.0, 14.0]
    raise ValueError(f"unknown energy preset {preset!r}; choose from {ENERGY_PRESETS}")


def collective_type(structure: Path, Z: int, A: int) -> str:
    """TALYS's collective type (S/V/R/...) from structure/deformation/<Sym>.def; S if absent."""
    f = structure / "deformation" / f"{SYMBOLS[Z]}.def"
    if f.is_file():
        for ln in f.read_text(errors="replace").splitlines():
            t = ln.split()
            if len(t) >= 4 and t[0].isdigit() and t[1].isdigit() and int(t[0]) == Z \
                    and int(t[1]) == A:
                return t[3]
    return "S"


def nuclide_class(Z: int, colltype: str) -> str:
    if Z >= 89:
        return "actinide"
    return {"S": "spherical", "V": "vibrational", "R": "rotational"}.get(colltype, "other")


def arm_order(repeat: int) -> tuple[str, ...]:
    """ABBA: even repeats forward, odd repeats reversed."""
    return ARMS if repeat % 2 == 0 else tuple(reversed(ARMS))


def parity_stats(eng: dict[str, list[float]], tal: dict[str, list[float]],
                 floor_mb: float = 1e-6) -> dict:
    """max / median |log10(engine/TALYS)| per observable over points where both exceed floor_mb."""
    import math

    out = {}
    for obs in OBSERVABLES:
        a, b = eng.get(obs), tal.get(obs)
        if not a or not b or len(a) != len(b):
            out[obs] = None
            continue
        d = [abs(math.log10(x / y)) for x, y in zip(a, b, strict=True)
             if x > floor_mb and y > floor_mb]
        out[obs] = {"n": len(d), "skipped": len(a) - len(d),
                    "max": max(d) if d else None,
                    "median": statistics.median(d) if d else None}
    return out


def _fmt(x: float | None, nd: int = 2) -> str:
    return "-" if x is None else f"{x:.{nd}f}"


def markdown_tables(summary: dict) -> str:
    """The per-nuclide, per-class and parity tables as markdown."""
    rows = summary["nuclides"]
    lines = [
        "| nuclide | class | TALYS | engine no-cache (compute / process) | cold cache | warm cache "
        "| speed-up no-cache (compute / process) | speed-up warm (compute / process) |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for r in rows:
        m = r["median_cpu_s"]
        lines.append(
            f"| {r['nuclide']} | {r['class']} | {_fmt(m['talys'])} "
            f"| {_fmt(m['nocache_compute'])} / {_fmt(m['nocache'])} "
            f"| {_fmt(m['cold_compute'])} / {_fmt(m['cold'])} "
            f"| {_fmt(m['warm_compute'])} / {_fmt(m['warm'])} "
            f"| {_fmt(r['speedup']['nocache_compute'], 1)}x / {_fmt(r['speedup']['nocache'], 1)}x "
            f"| {_fmt(r['speedup']['warm_compute'], 1)}x / {_fmt(r['speedup']['warm'], 1)}x |")
    lines += ["", "| class | nuclides | TALYS CPU-s | no-cache compute | no-cache process "
              "| warm compute | warm process | speed-up no-cache (compute / process) "
              "| speed-up warm (compute / process) |", "|---|---|---|---|---|---|---|---|---|"]
    for cls, c in summary["classes"].items():
        s = c["sum_cpu_s"]
        lines.append(
            f"| {cls} | {c['n']} | {_fmt(s['talys'], 1)} | {_fmt(s['nocache_compute'], 1)} "
            f"| {_fmt(s['nocache'], 1)} | {_fmt(s['warm_compute'], 1)} | {_fmt(s['warm'], 1)} "
            f"| {_fmt(c['speedup']['nocache_compute'], 1)}x / {_fmt(c['speedup']['nocache'], 1)}x "
            f"| {_fmt(c['speedup']['warm_compute'], 1)}x / {_fmt(c['speedup']['warm'], 1)}x |")
    lines += ["", "| observable | points | max abs(log10(engine/TALYS)) | median |",
              "|---|---|---|---|"]
    for obs, p in summary["parity"].items():
        lines.append(f"| {obs} | {p['n']} | {_fmt(p['max'], 6)} | {_fmt(p['median'], 6)} |")
    return "\n".join(lines) + "\n"


def summarize(runs: list[dict], nuclides: list[dict]) -> dict:
    """Medians per (nuclide, arm), class and overall sums, speed-ups, pooled parity."""
    keys = ("talys", "nocache", "cold", "warm", "nocache_compute", "cold_compute", "warm_compute")
    per = []
    for nd in nuclides:
        rs = [r for r in runs if r["nuclide"] == nd["nuclide"] and r.get("ok")]
        med = {}
        for k in keys:
            arm, _, part = k.partition("_")
            v = [r["compute_cpu_s"] if part else r["cpu_s"] for r in rs if r["arm"] == arm]
            v = [x for x in v if x is not None]
            med[k] = statistics.median(v) if v else None
        spd = {k: (med["talys"] / med[k]) if med["talys"] and med[k] else None
               for k in keys if k != "talys"}
        per.append({**nd, "median_cpu_s": med, "speedup": spd,
                    "n_repeats": sum(1 for r in rs if r["arm"] == "talys")})

    def group(members: list[dict]) -> dict:
        s = {}
        for k in keys:
            v = [m["median_cpu_s"][k] for m in members]
            s[k] = sum(v) if v and all(x is not None for x in v) else None
        spd = {k: (s["talys"] / s[k]) if s["talys"] and s[k] else None
               for k in keys if k != "talys"}
        return {"n": len(members), "sum_cpu_s": s, "speedup": spd,
                "speedup_range": {k: [min(x), max(x)] if (x := [m["speedup"][k] for m in members
                                                                if m["speedup"][k]]) else None
                                  for k in ("nocache_compute", "nocache", "warm_compute", "warm")}}

    classes = {}
    for cls in ("spherical", "vibrational", "rotational", "actinide", "other"):
        mem = [p for p in per if p["class"] == cls]
        if mem:
            classes[cls] = group(mem)
    classes["all"] = group(per)

    pooled: dict[str, list[float]] = {o: [] for o in OBSERVABLES}
    for r in runs:
        if r["arm"] == "nocache" and r.get("parity_abs_log10"):
            for o in OBSERVABLES:
                pooled[o] += r["parity_abs_log10"].get(o, [])
    parity = {o: {"n": len(v), "max": max(v) if v else None,
                  "median": statistics.median(v) if v else None} for o, v in pooled.items()}
    return {"nuclides": per, "classes": classes, "parity": parity}


# ------------------------------------------------------------------------------ measurement


def _loadavg() -> float:
    try:
        return float(Path("/proc/loadavg").read_text().split()[0])
    except OSError:
        return float("nan")


def timed(cmd: list[str], cpu: str, cwd: Path, env: dict, stdin=None, stdout=None) -> dict:
    """`taskset -c cpu cmd`; CPU-s of that child (user + sys, children it waited for included)."""
    t0, l0 = time.perf_counter(), _loadavg()
    p = subprocess.Popen(["taskset", "-c", cpu, *cmd], cwd=cwd, env=env, stdin=stdin,
                         stdout=stdout or subprocess.DEVNULL, stderr=subprocess.STDOUT)
    _pid, status, ru = os.wait4(p.pid, 0)
    return {"cpu_s": ru.ru_utime + ru.ru_stime, "wall_s": time.perf_counter() - t0,
            "maxrss_mb": ru.ru_maxrss / 1024, "rc": os.waitstatus_to_exitcode(status),
            "loadavg": [l0, _loadavg()]}


def _clean_env(structure: Path) -> dict:
    env = {k: v for k, v in os.environ.items() if not k.startswith(("INCOGNITA_", "HF_"))}
    env.update(OMP_NUM_THREADS="1", MKL_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1",
               HF_NATIVE_QUIET="1", TALYS_DIR=str(structure.parent), PYTHONPATH=str(REPO))
    return env


def _read_tot(path: Path) -> dict[float, float]:
    out = {}
    if not path.is_file():
        return out
    for ln in path.read_text(errors="replace").splitlines():
        t = ln.split()
        if not t or ln.lstrip().startswith("#"):
            continue
        try:
            out[float(t[0])] = float(t[1])
        except (ValueError, IndexError):
            continue
    return out


def _on_grid(table: dict[float, float], energies: list[float]) -> list[float] | None:
    """TALYS writes energies to 7 significant digits; match each requested energy to 1e-5 rel."""
    if not table:
        return None
    ks = sorted(table)
    out = []
    for e in energies:
        k = min(ks, key=lambda x: abs(x - e))
        if abs(k - e) > 1e-5 * e:
            return None
        out.append(table[k])
    return out


def run_talys(talys: Path, structure: Path, Z: int, A: int, energies: list[float], cpu: str,
              work: Path) -> dict:
    wd = Path(tempfile.mkdtemp(prefix=f"talys-{Z}-{A}-", dir=work))
    inp = ["projectile n", f"element {SYMBOLS[Z].lower()}", f"mass {A}", "energy energies",
           f"strucpath {structure}/"]
    (wd / "talys.inp").write_text("\n".join(inp) + "\n")
    (wd / "energies").write_text("".join(f"{e:.7E}\n" for e in energies))
    with open(wd / "talys.inp") as fin, open(wd / "talys.out", "w") as fout:
        r = timed([str(talys)], cpu, wd, _clean_env(structure), stdin=fin, stdout=fout)
    text = (wd / "talys.out").read_text(errors="replace")
    r["ok"] = r["rc"] == 0 and "congratulates" in text
    xs = {"total": "total.tot", "elastic": "elastic.tot", "nonelastic": "nonelastic.tot",
          "capture": f"rp{Z:03d}{A + 1:03d}.tot"}
    r["xs_mb"] = {k: _on_grid(_read_tot(wd / f), energies) for k, f in xs.items()}
    if not r["ok"]:
        r["tail"] = text[-800:]
    shutil.rmtree(wd, ignore_errors=True)
    return r


def run_engine(Z: int, A: int, energies: list[float], cpu: str, structure: Path, work: Path,
               cache: Path | None) -> dict:
    env = _clean_env(structure)
    if cache is not None:
        env["INCOGNITA_CC_CACHE"] = str(cache)
    res = work / f"engine-{Z}-{A}-{os.getpid()}.json"
    cmd = [sys.executable, str(Path(__file__).resolve()), "--_engine-child",
           f"{Z},{A}", ",".join(repr(e) for e in energies), str(res)]
    r = timed(cmd, cpu, REPO, env)
    child = json.loads(res.read_text()) if res.is_file() else {}
    res.unlink(missing_ok=True)
    r["ok"] = r["rc"] == 0 and bool(child.get("ok"))
    r["compute_cpu_s"] = child.get("compute_cpu_s")
    r["xs_mb"] = child.get("xs_mb", {})
    if not r["ok"]:
        r["error"] = child.get("error", f"exit code {r['rc']}")
    return r


def engine_child(za: str, energies: str, out: str) -> None:
    """Runs inside the timed process: one target, one thread, the engine's C path."""
    Z, A = (int(x) for x in za.split(","))
    e_mev = tuple(float(x) for x in energies.split(","))
    rec: dict = {"ok": False}
    try:
        import torch

        torch.set_num_threads(1)
        from physics.hf import warmrun
        from physics.hf.engine import ChainedFull
        from physics.hf.engine_c import run as engine_run

        t0 = time.process_time()
        cas = warmrun.new_cascade(Z, A, e_mev)
        with torch.inference_mode():
            res = engine_run(injection=ChainedFull(Z=Z, A=A, declared_energies=e_mev,
                                                   cascade=cas))
        rec["compute_cpu_s"] = time.process_time() - t0

        def arr(t):
            return None if t is None else [float(x) for x in t.detach().cpu().numpy()]

        tot = res.totals_mb
        rec["xs_mb"] = {"total": arr(tot.get("total")), "elastic": arr(tot.get("elastic")),
                        "nonelastic": arr(tot.get("nonelastic")),
                        "capture": arr(res.residual_production_mb.get(f"rp{Z:03d}{A + 1:03d}"))}
        rec["ok"] = True
    except Exception as exc:  # noqa: BLE001 -- recorded, the parent reports it
        rec["error"] = f"{type(exc).__name__}: {exc}"
    Path(out).write_text(json.dumps(rec))


def provenance(talys: Path) -> dict:
    cpu = next((ln.split(":", 1)[1].strip() for ln in
                Path("/proc/cpuinfo").read_text().splitlines() if ln.startswith("model name")),
               platform.processor())
    sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO, capture_output=True,
                         text=True).stdout.strip()
    natives = sorted(p.name for p in (REPO / "physics/hf/native/lib").glob("*.so"))
    return {"cpu_model": cpu, "logical_cpus": os.cpu_count(), "kernel": platform.release(),
            "python": platform.python_version(), "git_sha": sha, "native_kernels": natives,
            "talys_sha256": hashlib.sha256(talys.read_bytes()).hexdigest(),
            "started": time.strftime("%Y-%m-%dT%H:%M:%S%z")}


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--talys", type=Path, help="stock TALYS executable")
    ap.add_argument("--talys-structure", type=Path,
                    help="TALYS structure directory (used by both codes)")
    ap.add_argument("--nuclides", default="mix12",
                    help=f"preset ({', '.join(NUCLIDE_PRESETS)}) or list, e.g. Fe-56,U-238")
    ap.add_argument("--energies", default="grid64", choices=ENERGY_PRESETS)
    ap.add_argument("--cpus", default="0",
                    help="CPU(s) to pin to; a comma list runs one stream per CPU, nuclides "
                         "split between streams, all arms of a nuclide on the same CPU")
    ap.add_argument("--repeats", type=int, default=3)
    ap.add_argument("--out", type=Path, default=Path("out/bench"))
    return ap


def _stream(items: list[dict], cpu: str, a, energies: list[float], work: Path,
            log) -> list[dict]:
    runs = []
    for rep in range(a.repeats):
        for nd in items:
            Z, A = nd["Z"], nd["A"]
            warm = work / f"warm-{Z}-{A}"
            if not warm.is_dir():  # fill the warm cache once, untimed
                warm.mkdir()
                run_engine(Z, A, energies, cpu, a.talys_structure, work, warm)
            per = {}
            for arm in arm_order(rep):
                if arm == "talys":
                    r = run_talys(a.talys, a.talys_structure, Z, A, energies, cpu, work)
                else:
                    cold = Path(tempfile.mkdtemp(prefix="cold-", dir=work)) if arm == "cold" \
                        else None
                    r = run_engine(Z, A, energies, cpu, a.talys_structure, work,
                                   {"nocache": None, "cold": cold, "warm": warm}[arm])
                    if cold is not None:
                        shutil.rmtree(cold, ignore_errors=True)
                r.update(nuclide=nd["nuclide"], arm=arm, repeat=rep, cpu=cpu)
                per[arm] = r
                log(f"rep {rep} {nd['nuclide']:>7} {arm:>7} cpu {r['cpu_s']:8.2f} s "
                    f"compute {_fmt(r.get('compute_cpu_s'))} ok={r['ok']}")
            talys_xs = per["talys"]["xs_mb"]
            base = per["nocache"]["xs_mb"]
            per["nocache"]["parity_abs_log10"] = _abs_log10(base, talys_xs)
            per["nocache"]["parity"] = parity_stats(base, talys_xs)
            for arm in ("cold", "warm"):
                d = _abs_log10(per[arm]["xs_mb"], base)
                per[arm]["max_abs_log10_vs_nocache"] = max(
                    (v for o in OBSERVABLES for v in d.get(o, [])), default=None)
            runs += per.values()
    return runs


def _abs_log10(a: dict, b: dict, floor_mb: float = 1e-6) -> dict[str, list[float]]:
    import math

    out = {}
    for o in OBSERVABLES:
        x, y = (a or {}).get(o), (b or {}).get(o)
        if x and y and len(x) == len(y):
            out[o] = [abs(math.log10(p / q)) for p, q in zip(x, y, strict=True)
                      if p > floor_mb and q > floor_mb]
    return out


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if argv and argv[0] == "--_engine-child":
        engine_child(*argv[1:4])
        return 0
    a = build_parser().parse_args(argv)
    if not a.talys or not a.talys_structure:
        build_parser().error("--talys and --talys-structure are required")
    a.talys, a.talys_structure = a.talys.resolve(), a.talys_structure.resolve()
    if shutil.which("taskset") is None:
        raise SystemExit("taskset (util-linux) is required to pin the runs")
    energies = energies_mev(a.energies)
    nuclides = []
    for Z, A in parse_nuclides(a.nuclides):
        ct = collective_type(a.talys_structure, Z, A)
        nuclides.append({"nuclide": label(Z, A), "Z": Z, "A": A, "colltype": ct,
                         "class": nuclide_class(Z, ct)})
    a.out.mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix="bench-", dir=a.out))
    logf = open(a.out / "bench.log", "a")

    def log(msg: str) -> None:
        line = f"{time.strftime('%H:%M:%S')} {msg}"
        print(line, flush=True)
        logf.write(line + "\n")
        logf.flush()

    cpus = [c.strip() for c in a.cpus.split(",") if c.strip()]
    streams = [nuclides[i::len(cpus)] for i in range(len(cpus))]
    meta = {"protocol": {"arms": ARMS, "repeats": a.repeats, "energies": a.energies,
                         "n_energies": len(energies), "cpus": cpus, "threads": 1,
                         "timer": "user+sys CPU seconds of the pinned child (os.wait4)"},
            "provenance": provenance(a.talys)}
    t0 = time.time()
    if len(cpus) == 1:
        runs = _stream(streams[0], cpus[0], a, energies, work, log)
    else:
        from concurrent.futures import ThreadPoolExecutor

        with ThreadPoolExecutor(len(cpus)) as ex:
            futs = [ex.submit(_stream, s, c, a, energies, work, log)
                    for s, c in zip(streams, cpus, strict=True)]
            runs = [r for f in futs for r in f.result()]
    shutil.rmtree(work, ignore_errors=True)
    meta["provenance"]["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    meta["provenance"]["wall_s"] = round(time.time() - t0, 1)
    loads = [x for r in runs for x in r["loadavg"]]
    meta["provenance"]["loadavg_1min"] = {"min": min(loads), "median": statistics.median(loads),
                                          "max": max(loads)}
    summary = summarize(runs, nuclides)
    for r in runs:
        r.pop("xs_mb", None)
        r.pop("parity_abs_log10", None)
    (a.out / "bench.json").write_text(json.dumps({**meta, "summary": summary, "runs": runs},
                                                 indent=1))
    (a.out / "bench.md").write_text(markdown_tables(summary))
    log(f"wrote {a.out / 'bench.json'} and {a.out / 'bench.md'}")
    print(markdown_tables(summary))
    return 0 if all(r["ok"] for r in runs) else 1


if __name__ == "__main__":
    raise SystemExit(main())
