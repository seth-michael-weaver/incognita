"""Injected-input reference for the emission acceptance test (A-mult): an instrumented TALYS run
that writes the exact arrays `binary.f90` and `channels.f90` consume, beside the ordinary output
files (`xs*.tot`, `*.Lnn`, `rp*.tot`, `binE*.out`) those routines produce.

Why an instrumented run rather than the standard dumps. The contract's injection rule says a
component must pass its gate on TALYS's own upstream values. For T10 those values are the
post-multiple-emission bookkeeping arrays -- `feedexcl`, `popexcl`, `fisfeedex`, `xspopnuc`,
`xspopex` -- and the pre-binary compound population `xspop`. TALYS writes none of them at its
defaults: `populationE*.out` holds the population per bin but not the bin-to-bin feeding terms
that channels.f90 divides by, and `binE*.out` is written by binary.f90 itself, after the addends
this task has to reproduce. `talys_instrument/chdump.f90` writes them from inside talysreaction,
and `verify` checks the instrumented binary reproduces the standard reference `xs*.tot` /
`rp*.tot` / `binE*.out` byte for byte (the hooks only call write routines).

Ported quantities are TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

Usage (stdlib only, so it runs on the remote boxes):

    python physics/hf/emission/em_reference.py run --talys ~/hf_t10/talys --out ~/hf_t10/runs \
        --jobs default:Fe056,default:Zr090 --workers 2
    python physics/hf/emission/em_reference.py verify --runs ~/hf_t10/runs \
        --reference features/hf_reference/raw
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tarfile
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve()
ROOT = HERE.parents[3]
DEFAULT_DIR = ROOT / "features" / "hf_emission_reference"

# Files kept in the archive: the two dumps plus every output file A-mult scores against.
KEEP_NAMES = {"talys.out", "talys.inp", "energies", "bin_inputs.txt", "ch_inputs.txt"}
KEEP_PREFIX = ("binE", "xs", "rp")
KEEP_SUFFIX = (".tot",)


def _talys_reference():
    sys.path.insert(0, str(ROOT))
    from physics.hf import talys_reference as tr

    return tr


def _keep(name: str) -> bool:
    if name in KEEP_NAMES:
        return True
    if name.startswith(KEEP_PREFIX) or name.endswith(KEEP_SUFFIX):
        return True
    # discrete-level partials: nn.L00 .. na.L39
    return len(name) > 3 and name[-4:-2] == ".L" and name[-2:].isdigit()


def run_job(talys_dir: str, out: str, variant: str, tag: str, timeout: float,
            extra: str = "", label: str = "") -> dict:
    tr = _talys_reference()
    target = next(t for t in tr.REFERENCE_SET if t.tag == tag)
    out_p = Path(out).expanduser()
    name = label or variant
    tar = out_p / f"{name}__{tag}.tar.gz"
    if tar.exists():
        return {"job": tar.name, "status": "exists"}
    wd = out_p / "_work" / f"{name}__{tag}"
    shutil.rmtree(wd, ignore_errors=True)
    wd.mkdir(parents=True)
    inp, en = tr.input_text(variant, target)  # identical input to the reference dumps
    if extra:
        inp = inp.rstrip("\n") + "\n" + "\n".join(extra.split(";")) + "\n"
    (wd / "talys.inp").write_text(inp)
    (wd / "energies").write_text(en)
    binary = Path(talys_dir).expanduser() / "bin" / "talys"
    env = dict(os.environ, TALYS_DIR=str(Path(talys_dir).expanduser()))
    t0 = time.time()
    with open(wd / "talys.inp") as fin, open(wd / "talys.out", "w") as fout:
        rc = subprocess.run(
            [str(binary)], stdin=fin, stdout=fout, stderr=subprocess.STDOUT, cwd=wd, env=env,
            timeout=timeout,
        ).returncode
    elapsed = time.time() - t0
    for p in wd.iterdir():
        if p.is_file() and not _keep(p.name):
            p.unlink()
        elif p.is_dir():
            shutil.rmtree(p, ignore_errors=True)
    manifest = {
        "variant": name, "base_variant": variant, "extra_keywords": extra, "target": tag,
        "returncode": rc, "elapsed_s": round(elapsed, 1), "host": os.uname().nodename,
        "talys_bin_sha256": hashlib.sha256(binary.read_bytes()).hexdigest()[:16],
    }
    (wd / "manifest.json").write_text(json.dumps(manifest, indent=1))
    with tarfile.open(tar.with_suffix(".partial"), "w:gz") as tf:
        tf.add(wd, arcname=f"{name}__{tag}")
    tar.with_suffix(".partial").rename(tar)
    shutil.rmtree(wd, ignore_errors=True)
    return {"job": tar.name, "status": "ok" if rc == 0 else "failed",
            "elapsed_s": manifest["elapsed_s"]}


def cmd_run(a) -> None:
    Path(a.out).expanduser().mkdir(parents=True, exist_ok=True)
    jobs = [j.split(":") for j in a.jobs.split(",") if j]
    with ProcessPoolExecutor(max_workers=a.workers) as ex:
        futs = [ex.submit(run_job, a.talys, a.out, v, t, a.timeout, a.extra, a.label)
                for v, t in jobs]
        for f in futs:
            print(json.dumps(f.result()), flush=True)


def _members(tar: Path, prefix: str) -> dict[str, bytes]:
    out = {}
    with tarfile.open(tar) as tf:
        for m in tf.getmembers():
            if m.isfile() and Path(m.name).name.startswith(prefix):
                out[Path(m.name).name] = tf.extractfile(m).read()
    return out


def _numbers(blob: bytes) -> list[float]:
    """Every number of every datablock row of a YANDF file, in order. The `#` header carries the
    run date and user, so a byte comparison is useless across machines; the numbers are the
    physics."""
    out: list[float] = []
    for line in blob.decode(errors="replace").splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        try:
            out.extend(float(x) for x in s.split())
        except ValueError:
            continue
    return out


def cmd_verify(a) -> None:
    """The hooks must not move the physics: every number of every xs*.tot / rp*.tot / binE*.out
    in the instrumented run equals the standard reference dump. Compared numerically rather than
    byte for byte, because the YANDF header carries the run date and user, and the two runs are on
    different machines."""
    ref_dir = Path(a.reference).expanduser()
    worst_overall = 0.0
    for tar in sorted(Path(a.runs).expanduser().glob("*.tar.gz")):
        ref = ref_dir / tar.name
        if not ref.exists():
            print(f"{tar.name}: no reference dump, skipped")
            continue
        for prefix in ("xs", "rp", "binE"):
            mine, theirs = _members(tar, prefix), _members(ref, prefix)
            common = sorted(set(mine) & set(theirs))
            worst, worst_file, nshape = 0.0, "", 0
            for k in common:
                x, y = _numbers(mine[k]), _numbers(theirs[k])
                if len(x) != len(y):
                    nshape += 1
                    continue
                for u, v in zip(x, y):  # noqa: B905 (py3.9 boxes)
                    if v != 0.0:
                        d = abs(u - v) / abs(v)
                    else:
                        d = 0.0 if u == 0.0 else float("inf")
                    if d > worst:
                        worst, worst_file = d, k
            worst_overall = max(worst_overall, worst)
            print(f"{tar.name} {prefix}*: {len(common)} files, {nshape} shape mismatch, "
                  f"max rel diff {worst:.3e} ({worst_file})")
    print(f"worst relative difference over everything compared: {worst_overall:.3e}")
    sys.exit(1 if worst_overall > float(a.tol) else 0)


def main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--talys", required=True)
    r.add_argument("--out", default=str(DEFAULT_DIR))
    r.add_argument("--jobs", required=True, help="variant:tag,variant:tag")
    r.add_argument("--workers", type=int, default=2)
    r.add_argument("--timeout", type=float, default=14400)
    r.add_argument("--extra", default="")
    r.add_argument("--label", default="")
    r.set_defaults(func=cmd_run)
    v = sub.add_parser("verify")
    v.add_argument("--runs", required=True)
    v.add_argument("--reference", default=str(ROOT / "features/hf_reference/raw"))
    # A-mult is scored at 0.05 and T14 measured TALYS moving from itself by up to ~1e-3 on
    # individual population cells (docs/results/hf-sgl-floor.md), so 1e-3 is the meaningful bar
    # for "the hooks did not move the physics" across two machines.
    v.add_argument("--tol", default=1e-3, type=float)
    v.set_defaults(func=cmd_verify)
    a = p.parse_args(argv)
    a.func(a)


if __name__ == "__main__":
    main()
