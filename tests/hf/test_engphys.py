"""ENGPHYS: the four far-chart consistency switches (physics/hf/engphys.py), default OFF.

Each arm runs in its own interpreter (the direct / deformation / OMP caches are per process, and a worker sets its
environment before it imports anything, as engine_curves.py does). Pinned:
* OFF: n + Am-308 keeps stock TALYS's (n,2n) >> sigma_R (ENGDEFECT) -- nothing moves without a switch;
* ON (all four): (n,2n) <= sigma_R and the exclusive sum (+ fission) <= nonelastic (1e-3) on Am-308 (DWBA unitarity),
  U-248 at 1.38 MeV (DWBA on a Soukhovitskii actinide) and Tl-237 at 8.75 / 10.75 MeV (pre-equilibrium spin spread);
* the C chain (engine_c), the torch chain (engine.run) and the batch path (gpu_full.run_batch on CPU) agree under
  the switches.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]
TALYS_DIR = Path(os.environ.get("TALYS_DIR", Path.home() / "opt/talys-src"))
pytestmark = pytest.mark.skipif(not (TALYS_DIR / "structure").is_dir(), reason="no TALYS structure/")

CASES = {(95, 308): (0.3357390, 0.5380377, 1.0), (92, 248): (1.38, 1.62), (81, 237): (8.75, 10.75), (39, 90): (0.5, 1.0, 2.0)}
#: n + Am-308 (unbound target): the batch path already differs from the C chain with every switch OFF (nonelastic 0.005 vs
#: 1.238 mb at 0.1 MeV, 902 vs 912 mb at 0.287 MeV), so it is not a parity case for the switches; Y-90 (odd-odd, `oddodd`
#: moves it) is.
BATCH_SKIP = {(95, 308)}

PROBE = r"""
import json, sys, numpy as np, torch
torch.set_num_threads(1)
Z, A, path = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
E = tuple(float(np.float32(float(x))) for x in sys.argv[4].split(","))
from physics.hf import chartrun, warmrun
from physics.hf.engine import ChainedFull
out = {}
def pack(res):
    ch = {k: v.detach().cpu().numpy().astype(float).tolist() for k, v in res.channels_mb.items()}
    tot = {k: v.detach().cpu().numpy().astype(float).tolist() for k, v in res.totals_mb.items() if hasattr(v, "detach")}
    return {"ch": ch, "tot": tot}
cas = warmrun.new_cascade(Z, A, E)
with torch.inference_mode():
    if path == "c":
        from physics.hf.engine_c import run
        out = pack(run(injection=ChainedFull(Z=Z, A=A, declared_energies=E, cascade=cas)))
    elif path == "py":
        from physics.hf.engine import run
        out = pack(run(injection=ChainedFull(Z=Z, A=A, declared_energies=E, cascade=cas)))
    else:
        from physics.hf.gpu_full import run_batch
        from physics.hf.gpu_full_setup import setup_nuclide
        o = run_batch([(setup_nuclide(Z, A, E), i) for i in range(len(E))], torch.device("cpu"))
        out = {"tot": {k: v.cpu().numpy().astype(float).tolist() for k, v in o.items() if not k.startswith("_") and hasattr(v, "cpu")}}
print("JSON" + json.dumps(out))
"""


def _probe(Z, A, path, on):
    env = {k: v for k, v in os.environ.items() if not k.startswith("INCOGNITA_")}
    env.update(OMP_NUM_THREADS="1", MKL_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", PYTHONPATH=str(ROOT))
    if on:
        env["INCOGNITA_ENGPHYS"] = "all"
    e = ",".join(str(x) for x in CASES[(Z, A)])
    p = subprocess.run([sys.executable, "-c", PROBE, str(Z), str(A), path, e], cwd=ROOT, env=env,
                       capture_output=True, text=True, timeout=1800)
    assert p.returncode == 0, p.stderr[-3000:]
    line = [x for x in p.stdout.splitlines() if x.startswith("JSON")][-1]
    return json.loads(line[4:])


def _excl(r):
    s = sum(np.nan_to_num(np.asarray(v, float)) for k, v in r["ch"].items() if k.startswith("xs"))
    return s + np.clip(np.nan_to_num(np.asarray(r["tot"]["fission"], float)), 0, None)


@pytest.fixture(scope="module")
def runs():
    return {(za, path, on): _probe(*za, path, on) for za in CASES for path, on in
            (("c", False), ("c", True), ("py", True), ("gpu", True))}


def test_off_keeps_stock_talys_behaviour(runs):
    r = runs[((95, 308), "c", False)]
    assert r["ch"]["xs200000"][0] > 10 * r["tot"]["reaction"][0]


@pytest.mark.parametrize("za", list(CASES))
def test_on_is_unitary(runs, za):
    r = runs[(za, "c", True)]
    R, NE = np.asarray(r["tot"]["reaction"]), np.asarray(r["tot"]["nonelastic"])
    assert np.all(np.asarray(r["ch"].get("xs200000", np.zeros_like(R))) <= R * (1 + 1e-6))
    assert np.all(_excl(r) <= NE * (1 + 1e-3)), (_excl(r), NE)


@pytest.mark.parametrize("za", list(CASES))
def test_paths_agree_on(runs, za):
    c, py, g = runs[(za, "c", True)], runs[(za, "py", True)], runs[(za, "gpu", True)]
    for k in ("reaction", "nonelastic", "compound_elastic"):
        np.testing.assert_allclose(py["tot"][k], c["tot"][k], rtol=1e-6, atol=1e-6, err_msg=k)
    for k in ("xs200000", "xs100000", "xs000000", "xs300000"):
        if k in c["ch"]:
            np.testing.assert_allclose(py["ch"][k], c["ch"][k], rtol=1e-6, atol=1e-6, err_msg=k)
    if za not in BATCH_SKIP:
        np.testing.assert_allclose(g["tot"]["nonelastic"], c["tot"]["nonelastic"], rtol=1e-4, atol=1e-6)

