"""Charged-particle TALYS sweep that keeps every residual product and isomeric state (WP-25).

The neutron sweep (``physics.talys.sweep``) stores a fixed set of exclusive channels, because
its surrogate's output width is pinned to them. For a proton or alpha beam that is the wrong
object twice over: the exclusive-channel aliases invert (``xs100000`` is (p,n), not
inelastic), and what a producer or an activation experiment measures is the production of a
*nuclide in a state* summed over every channel that makes it. This sweep stores those
directly, one row per (run, product, state), from TALYS's ``rp*.tot`` / ``rp*.Lnn`` tables.

Parameter space -- eight knobs, all checked to be exact no-ops at their default value
(explicit default == keyword absent, to the last digit, on Mo-100+p and Bi-209+alpha; see
``tests/test_charged_medical.py`` and ``docs/results/wp25-medical-model.md``). That check exists
because of ``ldmodel 1`` (docs/results/wp24-fission-ldmodel-trap.md), which is *not* a no-op
and moved U-238 fission by 17x; ``ldmodel`` is deliberately absent here.

  m2constant       pre-equilibrium matrix-element scale        log-uniform [0.5, 2]
  rspincut         spin-cutoff scale (isomer ratios)           [0.5, 1.5]
  v1adjust_proj    entrance-channel OMP real depth             [0.9, 1.1]
  w1adjust_proj    entrance-channel OMP imaginary depth        [0.7, 1.3]
  rvadjust_proj    entrance-channel OMP real radius            [0.93, 1.07]
  v1adjust_n       neutron-emission OMP real depth             [0.9, 1.1]
  ld_a_factor      level-density a for the CN and its xn/pxn residual chain   [0.85, 1.15]
  cknock_a         alpha knock-out strength (alpha beams only; NaN = not applied) log [0.5, 2]

The design is SHARED across targets (every target sees the same parameter vectors), so a
global calibration can rank vectors by their pooled fit; sample 0 is the TALYS default.

    uv run python -m physics.charged.sweep run --config configs/charged_medical_sweep.yaml \
        shard_index=0 n_shards=2 workers=3
"""
from __future__ import annotations

import os
import shutil
import signal
import socket
import sys
import tempfile
import time
from concurrent.futures import FIRST_COMPLETED, ProcessPoolExecutor, wait
from pathlib import Path

import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq
from omegaconf import OmegaConf
from scipy.stats import qmc

from physics.charged.residual import read_residuals
from physics.talys.runner import TalysError, run_talys

REPO = Path(__file__).resolve().parents[2]

KNOBS: tuple[tuple[str, float, float, bool, float], ...] = (
    # name, lo, hi, log-scale, default
    ("m2constant", 0.5, 2.0, True, 1.0),
    ("rspincut", 0.5, 1.5, False, 1.0),
    ("v1adjust_proj", 0.9, 1.1, False, 1.0),
    ("w1adjust_proj", 0.7, 1.3, False, 1.0),
    ("rvadjust_proj", 0.93, 1.07, False, 1.0),
    ("v1adjust_n", 0.9, 1.1, False, 1.0),
    ("ld_a_factor", 0.85, 1.15, False, 1.0),
    ("cknock_a", 0.5, 2.0, True, 1.0),
)
KNOB_NAMES = tuple(k[0] for k in KNOBS)

BASE_KEYWORDS: dict[str, str] = {
    "fileresidual": "y",
    "outdiscrete": "n",
    "outspectra": "n",
    "outgamdis": "n",
    "bins": "20",
    "maxlevelstar": "20",
    "preequilibrium": "y",
}


def energy_grid(projectile: str) -> list[float]:
    """Incident energies in MeV. 1 MeV steps where excitation functions turn over."""
    if projectile == "p":
        e = np.r_[np.arange(2.0, 20.5, 1.0), np.arange(22.5, 40.1, 2.5), np.arange(45.0, 70.1, 5.0)]
    elif projectile == "a":
        e = np.r_[np.arange(8.0, 30.5, 1.0), np.arange(32.5, 50.1, 2.5), [55.0, 60.0]]
    elif projectile == "d":
        e = np.r_[np.arange(2.0, 20.5, 1.0), np.arange(22.5, 40.1, 2.5), [45.0, 50.0]]
    else:
        raise ValueError(f"no energy grid for projectile {projectile!r}")
    return [float(x) for x in e]


def design(n_samples: int, seed: int) -> np.ndarray:
    """(n_samples + 1, n_knobs) physical values; row 0 is the default vector."""
    out = np.empty((n_samples + 1, len(KNOBS)))
    out[0] = [k[4] for k in KNOBS]
    if n_samples:
        u = qmc.LatinHypercube(d=len(KNOBS), seed=int(seed), scramble=True).random(n_samples)
        for j, (_, lo, hi, logscale, _) in enumerate(KNOBS):
            out[1:, j] = (np.exp(np.log(lo) + u[:, j] * (np.log(hi) - np.log(lo))) if logscale
                          else lo + u[:, j] * (hi - lo))
    return out


def ld_chain(Z: int, A: int, projectile: str) -> list[tuple[int, int]]:
    """Compound nucleus plus the residuals its xn and pxn chains feed."""
    dz, da = {"p": (1, 1), "a": (2, 4), "d": (1, 2), "n": (0, 1)}[projectile]
    zc, ac = Z + dz, A + da
    chain = [(zc, ac - k) for k in range(0, 5)] + [(zc - 1, ac - 1 - k) for k in range(0, 3)]
    return chain


def to_keywords(values: np.ndarray, Z: int, A: int, projectile: str) -> tuple[dict, dict]:
    """Knob values -> (TALYS keywords, applied values with NaN for not-applied knobs).

    A knob at its default emits no keyword. That is safe only because every knob here was
    checked to be an exact no-op at its default; it is the opposite of safe for ``ldmodel``.
    """
    v = dict(zip(KNOB_NAMES, (float(x) for x in values), strict=True))
    applied = dict(v)
    kw: dict[str, str] = {}

    def differs(name: str) -> bool:
        return abs(v[name] - dict((k[0], k[4]) for k in KNOBS)[name]) > 1e-12

    if differs("m2constant"):
        kw["m2constant"] = f"{v['m2constant']:.6g}"
    if differs("rspincut"):
        kw["rspincut"] = f"{v['rspincut']:.6g}"
    for name, key, particle in (("v1adjust_proj", "v1adjust", projectile),
                                ("w1adjust_proj", "w1adjust", projectile),
                                ("rvadjust_proj", "rvadjust", projectile),
                                ("v1adjust_n", "v1adjust", "n")):
        if differs(name):
            # two v1adjust lines (projectile and neutron) need distinct dict keys
            kw[f"{key}#{particle}"] = f"{particle} {v[name]:.6g}"
    if differs("ld_a_factor"):
        for i, (z, a) in enumerate(ld_chain(Z, A, projectile)):
            kw[f"aadjust#{i}"] = f"{z} {a} {v['ld_a_factor']:.6g}"
    if projectile == "a":
        if differs("cknock_a"):
            kw["cknock"] = f"a {v['cknock_a']:.6g}"
    else:
        applied["cknock_a"] = float("nan")
    if projectile == "n":
        applied["v1adjust_proj"] = applied["w1adjust_proj"] = applied["rvadjust_proj"] = float("nan")
    return kw, applied


def _schema() -> pa.Schema:
    fields = [("Z", pa.int16()), ("A", pa.int16()), ("projectile", pa.string()),
              ("sample_id", pa.int32()), ("status", pa.string()), ("error", pa.string())]
    fields += [(f"p_{k}", pa.float64()) for k in KNOB_NAMES]
    fields += [("keywords", pa.string()), ("E_mev", pa.list_(pa.float64())),
               ("product_z", pa.int16()), ("product_a", pa.int16()), ("state", pa.string()),
               ("level", pa.int16()), ("half_life_s", pa.float64()),
               ("xs_mb", pa.list_(pa.float64())), ("talys_version", pa.string()),
               ("runtime_s", pa.float64()), ("hostname", pa.string()), ("timestamp", pa.string())]
    return pa.schema(fields)


def run_one(Z: int, A: int, projectile: str, sample_id: int, values: np.ndarray,
            timeout_s: float, work_root: str) -> list[dict]:
    """One TALYS run -> one row per residual product/state. Never raises."""
    E = energy_grid(projectile)
    kw, applied = to_keywords(values, Z, A, projectile)
    head = {"Z": Z, "A": A, "projectile": projectile, "sample_id": int(sample_id),
            "status": "ok", "error": "", **{f"p_{k}": applied[k] for k in KNOB_NAMES},
            "keywords": "\n".join(f"{k.split('#', 1)[0]} {v}" for k, v in kw.items()),
            "E_mev": E, "talys_version": "", "runtime_s": float("nan"),
            "hostname": socket.gethostname(), "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S")}
    wd = tempfile.mkdtemp(prefix=f"z{Z}a{A}{projectile}s{sample_id}_", dir=work_root)
    t0 = time.perf_counter()
    try:
        res = run_talys(Z, A, E, {**BASE_KEYWORDS, **kw}, workdir=wd, projectile=projectile,
                        timeout=timeout_s)
        prods = read_residuals(wd)
        head["runtime_s"] = float(res["elapsed"])
        head["talys_version"] = res.get("talys_version") or ""
    except (TalysError, ValueError, OSError) as exc:
        msg = str(exc)
        return [{**head, "status": "error", "runtime_s": time.perf_counter() - t0,
                 "error": msg if len(msg) <= 1500 else msg[:1100] + "\n...\n" + msg[-400:],
                 "product_z": -1, "product_a": -1, "state": "", "level": -1,
                 "half_life_s": float("nan"), "xs_mb": []}]
    finally:
        shutil.rmtree(wd, ignore_errors=True)
    rows = []
    for p in prods:
        # every table shares the input grid; align defensively by nearest energy
        xs = np.full(len(E), np.nan)
        for j, e in enumerate(E):
            k = int(np.argmin(np.abs(p["E_mev"] - e))) if p["E_mev"].size else -1
            if k >= 0 and abs(p["E_mev"][k] - e) <= 1e-4 * e:
                xs[j] = p["xs_mb"][k]
        rows.append({**head, "product_z": p["product_z"], "product_a": p["product_a"],
                     "state": p["state"], "level": p["level"],
                     "half_life_s": p["half_life_s"], "xs_mb": xs.tolist()})
    if not rows:
        rows = [{**head, "status": "error", "error": "no residual production tables written",
                 "product_z": -1, "product_a": -1, "state": "", "level": -1,
                 "half_life_s": float("nan"), "xs_mb": []}]
    return rows


def _worker(args):
    return run_one(*args)


def completed(out_dir: Path) -> set[tuple[int, int, str, int]]:
    keys = set()
    for s in sorted((out_dir / "shards").glob("*.parquet")):
        t = pq.read_table(s, columns=["Z", "A", "projectile", "sample_id", "status"]).to_pylist()
        keys |= {(r["Z"], r["A"], r["projectile"], r["sample_id"]) for r in t
                 if r["status"] == "ok"}
    return keys


def load(out_dir: str | Path):
    """All ok rows; the last successful copy of a (target, sample, product, state) wins."""
    import polars as pl

    shards = sorted(Path(out_dir).glob("shards/*.parquet"))
    if not shards:
        raise FileNotFoundError(f"no shards under {out_dir}")
    df = pl.concat([pl.read_parquet(s) for s in shards], how="vertical_relaxed")
    df = df.filter(pl.col("status") == "ok").sort("timestamp")
    return df.unique(subset=["Z", "A", "projectile", "sample_id", "product_z", "product_a",
                             "state"], keep="last", maintain_order=True)


def run(cfg) -> None:
    out_dir = REPO / cfg.out_dir
    (out_dir / "shards").mkdir(parents=True, exist_ok=True)
    work_root = str(out_dir / "_work")
    Path(work_root).mkdir(parents=True, exist_ok=True)
    X = design(int(cfg.n_samples), int(cfg.seed))
    targets = [(int(t[0]), int(t[1]), str(t[2])) for t in cfg.targets]
    tasks = [(z, a, pr, s) for s in range(X.shape[0]) for (z, a, pr) in targets]
    # shard_index may be a list: one machine taking several shards keeps the sample-major
    # order ACROSS them, where running them one after another would finish every design row
    # of the first shard before starting the second.
    K = int(cfg.n_shards)
    ks = ({int(x) for x in cfg.shard_index} if OmegaConf.is_list(cfg.shard_index)
          else {int(cfg.shard_index)})
    k = sorted(ks)
    tasks = [t for j, t in enumerate(tasks) if j % K in ks]
    done = completed(out_dir)
    todo = [t for t in tasks if t not in done]
    print(f"[charged-sweep] shard {k}/{K}: {len(tasks)} tasks, {len(todo)} to run, "
          f"workers={cfg.workers}", flush=True)
    deadline = time.time() + 60 * float(cfg.max_minutes) if cfg.get("max_minutes") else None
    buf: list[dict] = []
    n_done = n_err = 0
    tag = f"{socket.gethostname()}-{os.getpid()}"

    def flush(i: int) -> None:
        nonlocal buf
        if not buf:
            return
        path = out_dir / "shards" / f"{tag}-{i:05d}.parquet"
        tmp = path.with_suffix(".parquet.tmp")
        pq.write_table(pa.Table.from_pylist(buf, schema=_schema()), tmp)
        os.replace(tmp, path)
        buf = []

    stop = {"flag": False}
    signal.signal(signal.SIGTERM, lambda *_: stop.__setitem__("flag", True))
    shard_i = 0
    with ProcessPoolExecutor(int(cfg.workers)) as ex:
        pending = set()
        it = iter(todo)
        while True:
            while len(pending) < int(cfg.workers) and not stop["flag"] and (
                    deadline is None or time.time() < deadline):
                t = next(it, None)
                if t is None:
                    break
                z, a, pr, s = t
                pending.add(ex.submit(_worker, (z, a, pr, s, X[s], float(cfg.timeout_s),
                                                work_root)))
            if not pending:
                break
            fin, pending = wait(pending, return_when=FIRST_COMPLETED)
            for f in fin:
                rows = f.result()
                buf.extend(rows)
                n_done += 1
                if rows[0]["status"] != "ok":
                    n_err += 1
                    print(f"[charged-sweep] ERROR Z{rows[0]['Z']}A{rows[0]['A']}"
                          f"{rows[0]['projectile']} s{rows[0]['sample_id']}: "
                          f"{rows[0]['error'][:300]}", flush=True)
                if n_done % int(cfg.shard_size) == 0:
                    flush(shard_i)
                    shard_i += 1
                    print(f"[charged-sweep] {n_done}/{len(todo)} done, {n_err} errors",
                          flush=True)
    flush(shard_i)
    print(f"[charged-sweep] finished: {n_done} runs, {n_err} errors", flush=True)


def main(argv: list[str]) -> None:
    if not argv or argv[0] != "run":
        raise SystemExit(__doc__)
    args = argv[1:]
    path = None
    if len(args) >= 2 and args[0] == "--config":
        path, args = args[1], args[2:]
    cfg = OmegaConf.create({"out_dir": "features/charged_sweep", "seed": 20260912,
                            "n_samples": 12, "workers": 2, "shard_size": 10,
                            "timeout_s": 3600, "max_minutes": None, "shard_index": 0,
                            "n_shards": 1, "targets": []})
    if path:
        cfg = OmegaConf.merge(cfg, OmegaConf.load(path))
    if args:
        cfg = OmegaConf.merge(cfg, OmegaConf.from_dotlist(args))
    run(cfg)


if __name__ == "__main__":
    main(sys.argv[1:])
