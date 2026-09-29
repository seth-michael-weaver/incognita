"""Injected-input reference for the compound acceptance tests (A-cn1, A-cn2): an instrumented
TALYS run that writes the exact arrays `comptarget.f90` consumes, and the compound-only population
it produces, beside the ordinary output files.

Why an instrumented run rather than the standard dumps. The contract's injection rule says
`compound` must pass its gate with TALYS's own upstream values. Three of those values are not in
any file TALYS writes at its defaults: the bin-integrated level density `rho0` (exgrid.f90
integrates density() over each bin's edges and centre, not on the ld*.gs table grid), the
second-order interpolation of T_lj from the emission grid onto each residual level/bin
(`Tjlnex`, densprepare.f90), and the per-bin gamma transmission `Tgam` including `Fnorm(0)`.
Rebuilding them from ld*.gs/psf/transmission tables would be ports of T6/T7/T5 work and would
test those ports, not this one. So `talys_instrument/cndump.f90` writes them from inside
comptarget, and this script checks that the instrumented binary reproduces the standard
reference binE*.out to within the two reference machines' own agreement (`verify`; the hooks only
call write routines).

Ported quantities are TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

Usage (stdlib only for `run`, so it runs on the remote boxes):

    python physics/hf/compound/cn_reference.py run --talys ~/t9cn/talys --out ~/t9cn/runs \
        --jobs wfc_off:Fe056,default:Fe056 --workers 2
    python physics/hf/compound/cn_reference.py verify --runs <dir> --reference features/hf_reference/raw
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
DEFAULT_DIR = ROOT / "features" / "hf_compound_reference"


def _talys_reference():
    sys.path.insert(0, str(ROOT))
    from physics.hf import talys_reference as tr  # noqa: E402

    return tr


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
    # `extra` appends TALYS keywords (e.g. "widthmode 2"); anything but "" makes the run a
    # variant of the reference set, not a member of it, so it gets its own `label`.
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
    keep = {"talys.out", "talys.inp", "cn_inputs.txt", "energies"}
    for p in wd.iterdir():
        if p.name in keep or p.name.startswith(("binE", "directE", "initial_population")):
            continue
        p.unlink()
    manifest = {
        "variant": name,
        "base_variant": variant,
        "extra_keywords": extra,
        "target": tag,
        "returncode": rc,
        "elapsed_s": round(elapsed, 1),
        "host": os.uname().nodename,
        "talys_bin_sha256": hashlib.sha256(binary.read_bytes()).hexdigest()[:16],
    }
    (wd / "manifest.json").write_text(json.dumps(manifest, indent=1))
    with tarfile.open(tar.with_suffix(".partial"), "w:gz") as tf:
        tf.add(wd, arcname=f"{name}__{tag}")
    tar.with_suffix(".partial").rename(tar)
    shutil.rmtree(wd, ignore_errors=True)
    return {"job": tar.name, "status": "ok" if rc == 0 else "failed", "elapsed_s": manifest["elapsed_s"]}


def run_multi(talys_dir: str, out: str, tag: str, zn: str, energies: list[float],
              timeout: float) -> dict:
    """One `default` run restricted to a few incident energies, with the continuum-decay hooks
    armed for residual (Zcomp, Ncomp) = `zn`, so `cn_multi.txt` stays small.

    The keywords are the reference set's own `default` variant, so this is a TALYS run at its
    defaults; only the energy list is shortened (cn_multi.txt is ~50 MB per energy).
    """
    tr = _talys_reference()
    target = next(t for t in tr.REFERENCE_SET if t.tag == tag)
    out_p = Path(out).expanduser()
    zntag = zn.replace(" ", "")
    tar = out_p / f"multi{zntag}__{tag}.tar.gz"
    if tar.exists():
        return {"job": tar.name, "status": "exists"}
    wd = out_p / "_work" / f"multi{zntag}__{tag}"
    shutil.rmtree(wd, ignore_errors=True)
    wd.mkdir(parents=True)
    inp, _ = tr.input_text("default", target)
    (wd / "talys.inp").write_text(inp)
    (wd / "energies").write_text("".join(f"{e:.6E}\n" for e in sorted(energies)))
    binary = Path(talys_dir).expanduser() / "bin" / "talys"
    env = dict(os.environ, TALYS_DIR=str(Path(talys_dir).expanduser()), CNDUMP_ZN=zn)
    t0 = time.time()
    with open(wd / "talys.inp") as fin, open(wd / "talys.out", "w") as fout:
        rc = subprocess.run(
            [str(binary)], stdin=fin, stdout=fout, stderr=subprocess.STDOUT, cwd=wd, env=env,
            timeout=timeout,
        ).returncode
    elapsed = time.time() - t0
    keep = {"talys.out", "talys.inp", "cn_inputs.txt", "cn_multi.txt", "energies"}
    for f in wd.iterdir():
        if f.name in keep or f.name.startswith(("binE", "directE", "population")):
            continue
        f.unlink()
    (wd / "manifest.json").write_text(json.dumps({
        "variant": f"multi{zntag}", "target": tag, "cndump_zn": zn, "energies": sorted(energies),
        "returncode": rc, "elapsed_s": round(elapsed, 1), "host": os.uname().nodename,
        "talys_bin_sha256": hashlib.sha256(binary.read_bytes()).hexdigest()[:16],
    }, indent=1))
    with tarfile.open(tar.with_suffix(".partial"), "w:gz") as tf:
        tf.add(wd, arcname=f"multi{zntag}__{tag}")
    tar.with_suffix(".partial").rename(tar)
    shutil.rmtree(wd, ignore_errors=True)
    return {"job": tar.name, "status": "ok" if rc == 0 else "failed",
            "elapsed_s": round(elapsed, 1)}


def cmd_multi(a) -> None:
    Path(a.out).expanduser().mkdir(parents=True, exist_ok=True)
    en = [float(x) for x in a.energies.split(",")]
    with ProcessPoolExecutor(a.workers) as ex:
        futs = [ex.submit(run_multi, a.talys, a.out, t, a.zn, en, a.timeout)
                for t in a.targets.split(",")]
        for f in futs:
            print(json.dumps(f.result()), flush=True)


def cmd_run(a) -> None:
    jobs = [j.split(":") for j in a.jobs.split(",")]
    Path(a.out).expanduser().mkdir(parents=True, exist_ok=True)
    with ProcessPoolExecutor(a.workers) as ex:
        futs = [ex.submit(run_job, a.talys, a.out, v, t, a.timeout, a.extra, a.label)
                for v, t in jobs]
        for f in futs:
            print(json.dumps(f.result()), flush=True)


def _members(tar: Path, prefix: str) -> dict[str, bytes]:
    out = {}
    with tarfile.open(tar) as tf:
        for m in tf.getmembers():
            name = m.name.split("/", 1)[-1]
            if m.isfile() and name.startswith(prefix):
                out[name] = tf.extractfile(m).read()
    return out


def cmd_verify(a) -> None:
    """The instrumented binE*.out must equal the reference dump's binE*.out: the hooks write, they do
    not compute. Compared numerically (max relative difference over every printed number) rather
    than byte for byte, because the reference dumps come from two machines (x86-64 desktop,
    arm64 MacBook) whose binaries agree to the last printed digit only most of the time."""
    import numpy as np

    def nums(b: bytes) -> np.ndarray:
        rows = [ln.split() for ln in b.decode().splitlines() if ln and not ln.startswith("#")]
        return np.array([float(x) for r in rows for x in r])

    worst_all = 0.0
    for tar in sorted(Path(a.runs).glob("*.tar.gz")):
        ref = Path(a.reference) / tar.name
        if not ref.exists():
            print(f"{tar.name}: no reference tarball, skipped")
            continue
        mine, theirs = _members(tar, "binE"), _members(ref, "binE")
        worst, where = 0.0, ""
        for k in theirs:
            x, y = nums(mine.get(k, b"")), nums(theirs[k])
            if x.shape != y.shape:
                worst, where = float("inf"), k
                break
            d = np.abs(x - y) / np.maximum(np.abs(y), 1e-30)
            d[(np.abs(x) < 1e-12) & (np.abs(y) < 1e-12)] = 0.0
            if d.max() > worst:
                worst, where = float(d.max()), k
        print(f"{tar.name}: {len(theirs)} binE files, max relative difference {worst:.2e} ({where})")
        worst_all = max(worst_all, worst)
    sys.exit(0 if worst_all <= a.tol else 1)


def main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--talys", required=True)
    r.add_argument("--out", required=True)
    r.add_argument("--jobs", required=True, help="variant:tag,...")
    r.add_argument("--workers", type=int, default=2)
    r.add_argument("--timeout", type=float, default=7200.0)
    r.add_argument("--extra", default="", help="extra talys.inp keywords, ';'-separated")
    r.add_argument("--label", default="", help="output name when --extra changes the physics")
    r.set_defaults(fn=cmd_run)
    m = sub.add_parser("multi")
    m.add_argument("--talys", required=True)
    m.add_argument("--out", required=True)
    m.add_argument("--targets", required=True, help="tag,...")
    m.add_argument("--zn", default="0 1", help='CNDUMP_ZN, "Zcomp Ncomp" of the residual to dump')
    m.add_argument("--energies", default="14.0")
    m.add_argument("--workers", type=int, default=1)
    m.add_argument("--timeout", type=float, default=7200.0)
    m.set_defaults(fn=cmd_multi)
    v = sub.add_parser("verify")
    v.add_argument("--runs", required=True)
    v.add_argument("--reference", default=str(ROOT / "features" / "hf_reference" / "raw"))
    v.add_argument("--tol", type=float, default=1.0e-5)
    v.set_defaults(fn=cmd_verify)
    a = p.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
