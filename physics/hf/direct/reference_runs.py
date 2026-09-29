"""T12's own TALYS reference runs: the two output blocks the standard dumps do not contain.

The 54 archives T0 parsed (`features/hf_reference/`) carry `directE*.out` with the discrete
direct cross sections and the giant-resonance parameters, which is enough to gate
`directread.f90` and `sumrules.f90`. They do NOT carry:

* the **giant resonance spectra** datablock of `directE*.out` -- `directout.f90:233` writes it
  only `if (flagspec)`, and `outspectra` is not in T0's `OUTPUT_KEYWORDS`. That block holds
  `xsgr`, `xsgrstate` and `xscollcont`, i.e. everything `giant.f90` computes;
* anything from **direct radiative capture**, which is off by default
  (`input_gammamodel.f90:61`, `flagracap = .false.`) and writes `racap.tot`/`racap.out`.

So T12 runs TALYS twice more, with the same projectile, energies and output keywords T0 used
plus one extra keyword each. `variant` names are prefixed `t12` so they can never collide with
T0's published variants, and the archives land in `features/hf_direct_reference/`, not in
`features/hf_reference/`.

    python -m physics.hf.direct.reference_runs run --variants t12spec,t12racap --workers 2

Run it detached; a full variant is ~1 h with 2 workers. Nothing here is part of the port.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import tarfile
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from physics.hf.talys_reference import (
    ENERGIES_MEV,
    FISSION_OUTPUT_KEYWORDS,
    OUTPUT_KEYWORDS,
    REFERENCE_SET,
    Target,
)

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_OUT = ROOT / "features" / "hf_direct_reference"

# Spherical set = T9's nine, minus the three whose `default` run is slowest, plus the two
# deformed targets the gate reports separately (contract §6: deformed is not in the A-mult set).
SPHERICAL = ("Ca040", "Fe056", "Ni058", "Zr090", "Nb093", "Sn120", "Pb208")
DEFORMED = ("W184", "Gd157")

VARIANTS: dict[str, dict] = {
    # flagspec on: adds the "Giant resonance spectra" datablock to directE*.out
    # (directout.f90:233-252) and the binary spectra to talys.out. No model keyword.
    "t12spec": {
        "keywords": {},
        "output": {**OUTPUT_KEYWORDS, "outspectra": "y"},
        "targets": SPHERICAL + DEFORMED,
    },
    # Direct radiative capture on (racap.f90). This IS a model keyword: it adds xsracape to the
    # capture channel, so it is a separate variant and is never mixed into a gate of the
    # default physics.
    "t12racap": {
        "keywords": {"racap": "y"},
        "output": {**OUTPUT_KEYWORDS, "outspectra": "y"},
        "targets": ("Fe056", "Ni058", "Zr090", "Sn120"),
    },
}


def jobs(variants: list[str]) -> list[tuple[str, Target]]:
    out = []
    for v in variants:
        spec = VARIANTS[v]
        for t in REFERENCE_SET:
            if t.tag in spec["targets"]:
                out.append((v, t))
    return out


def input_text(variant: str, t: Target) -> tuple[str, str]:
    """(talys.inp, energies file). Mirrors talys_reference.input_text so the runs are
    comparable to T0's archives keyword for keyword."""
    spec = VARIANTS[variant]
    energies = spec.get("energies", ENERGIES_MEV)
    lines = ["projectile n", f"element {t.symbol.lower()}", f"mass {t.A}", "energy energies"]
    lines += [f"{k} {v}" for k, v in spec["keywords"].items()]
    output = dict(spec["output"])
    if t.A > 150:
        output.update(FISSION_OUTPUT_KEYWORDS)
    lines += [f"{k} {v}" for k, v in output.items()]
    return "\n".join(lines) + "\n", "".join(f"{e:.6E}\n" for e in energies)


def _talys_bin() -> Path:
    if os.environ.get("TALYS_BIN"):
        return Path(os.environ["TALYS_BIN"])
    return Path(os.environ.get("TALYS_DIR", Path.home() / "opt/talys-src")) / "bin" / "talys"


def run_one(variant: str, t: Target, out: Path, timeout: float = 7200.0) -> dict:
    tar = out / f"{variant}__{t.tag}.tar.gz"
    if tar.exists():
        return {"job": tar.name, "status": "exists"}
    wd = out / "_work" / f"{variant}__{t.tag}"
    shutil.rmtree(wd, ignore_errors=True)
    wd.mkdir(parents=True)
    inp, en = input_text(variant, t)
    (wd / "talys.inp").write_text(inp)
    (wd / "energies").write_text(en)
    env = dict(os.environ)
    env.setdefault("TALYS_DIR", str(_talys_bin().resolve().parent.parent))
    t0 = time.time()
    with open(wd / "talys.inp") as fin, open(wd / "talys.out", "w") as fout:
        try:
            rc = subprocess.run(
                [str(_talys_bin())],
                stdin=fin,
                stdout=fout,
                stderr=subprocess.STDOUT,
                cwd=wd,
                env=env,
                timeout=timeout,
            ).returncode
        except subprocess.TimeoutExpired:
            rc = "timeout"
    elapsed = time.time() - t0
    text = (wd / "talys.out").read_text(errors="replace")
    ok = rc == 0 and "The TALYS team congratulates" in text
    lines = text.splitlines()
    fatal = [
        ln
        for i, ln in enumerate(lines)
        if "TALYS-error" in ln and not any("Continuing" in w for w in lines[i : i + 6])
    ]
    manifest = {
        "variant": variant,
        "target": t.tag,
        "Z": t.Z,
        "A": t.A,
        "shape": t.shape,
        "returncode": rc,
        "completed_banner": "The TALYS team congratulates" in text,
        "fatal_errors": fatal[:5],
        "elapsed_s": round(elapsed, 1),
        "host": os.uname().nodename,
        "talys_bin": str(_talys_bin()),
        "talys_bin_sha256": hashlib.sha256(_talys_bin().read_bytes()).hexdigest()[:16],
        "input": inp,
        "n_files": len(list(wd.iterdir())),
    }
    (wd / "manifest.json").write_text(json.dumps(manifest, indent=1))
    # Keep only what T12 reads; a full archive is ~1 GB with outspectra on.
    keep = {"manifest.json", "talys.inp", "energies", "racap.tot", "racap.out"}
    for p in sorted(wd.iterdir()):
        if p.name in keep or p.name.startswith("directE"):
            continue
        if p.is_dir():
            shutil.rmtree(p, ignore_errors=True)
        else:
            p.unlink()
    status = "ok" if ok and not fatal else "failed"
    tmp = tar.with_suffix(".partial")
    with tarfile.open(tmp, "w:gz") as tf:
        tf.add(wd, arcname=f"{variant}__{t.tag}")
    tmp.rename(tar if status == "ok" else out / f"FAILED__{variant}__{t.tag}.tar.gz")
    shutil.rmtree(wd, ignore_errors=True)
    return {"job": tar.name, "status": status, "elapsed_s": manifest["elapsed_s"]}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("cmd", choices=("run", "list"))
    ap.add_argument("--variants", default="t12spec,t12racap")
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    a = ap.parse_args(argv)
    js = jobs(a.variants.split(","))
    if a.cmd == "list":
        for v, t in js:
            print(v, t.tag)
        return 0
    out = Path(a.out).expanduser()
    out.mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(max_workers=max(1, a.workers)) as ex:
        for r in ex.map(lambda vt: run_one(vt[0], vt[1], out), js):
            print(json.dumps(r), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
