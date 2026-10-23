"""PEPHOTFIX: `pewindow g` (and a/l/p/q) on a photon entrance (k0 = 0).

engine-2026-10-19 raised `KeyError: 0` in `pepauli_onsets` (the Kalbach-pickup onsets read gscomp[k0] for k0 <= 2, k0 = 0
included) on every photon run with the production `PEWINDOW g`. A photon entrance has no discrete PE collapse (preeq.f90:134:
preeqcorrect only for k0 > 0), so the window has nothing to correct: the photon run must be the PEWINDOW n run, bit for bit.
The run happens in a subprocess: in-memory (Z, A) caches assume one projectile per process (physics/hf/projectile.py).
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CODE = r"""
import json, os, sys, hashlib
import numpy as np, torch
torch.set_num_threads(1)
from physics.hf.engine import run, ChainedFull
from physics.hf.warmrun import result_arrays
with torch.inference_mode():
    res = run(injection=ChainedFull(Z=79, A=197, declared_energies=(30.0,), energies=None))
arr = result_arrays(res)
h = {k: hashlib.sha256(np.ascontiguousarray(np.asarray(v)).tobytes()).hexdigest() for k, v in arr.items()}
print("PEPHOTFIX_JSON" + json.dumps({"h": h, "n": len(h)}))
"""


def _photon_run(window: str) -> dict:
    env = {k: v for k, v in os.environ.items() if not k.startswith("INCOGNITA_")}
    env.update(INCOGNITA_CPINC="g", INCOGNITA_PEUNITS="y", INCOGNITA_PEWINDOW=window, OMP_NUM_THREADS="1", MKL_NUM_THREADS="1",
               OPENBLAS_NUM_THREADS="1")
    p = subprocess.run([sys.executable, "-c", CODE], cwd=ROOT, env=env, capture_output=True, text=True, timeout=1800)
    assert p.returncode == 0, p.stderr[-3000:]
    line = [s for s in p.stdout.splitlines() if s.startswith("PEPHOTFIX_JSON")][-1]
    return json.loads(line[len("PEPHOTFIX_JSON"):])


def test_photon_pewindow_is_the_n_run():
    ref = _photon_run("n")
    assert ref["n"] > 10
    for w in ("g", "a"):
        got = _photon_run(w)  # g raised KeyError 0 before PEPHOTFIX
        assert got["h"] == ref["h"], sorted(k for k in ref["h"] if got["h"].get(k) != ref["h"][k])[:10]
