"""G-2PH: the two-phonon (`ecis1(2:2) = 'T'`) incident coupled channels against TALYS.

No dump in `features/hf_reference/raw` is a two-phonon target -- that is why
`ecis.incident` raised on one until TWOPH -- so this scorer reads the three runs
`scripts/hf_twophonon_reference.py` makes (Zn-64, Cd-114, Te-124, the full 23-energy reference
grid) instead of the reference parquet.

Metric of contract §6 and of `ecis.score`: `r = |ln(port/TALYS)|` over points above the floor,
p95 gated at the A-inc tolerance of `docs/results/hf-engine-gates.md` (1e-2), median and max
reported. Four quantity groups:

    * the six A-inc scalars per incident energy, from `talys.out`,
    * the direct inelastic cross section to each COUPLED level per energy, from `directE*.out` --
      the quantity that only exists because the levels are coupled, and the one the second-order
      terms move most,
    * `Tjlinc(l, j)` and the spin-averaged `T_l`, from `transmission_inc.out` (TALYS overwrites
      it, so it holds the last incident energy only),
    * the S-matrix-derived `S0`, `S1` and `R'`, which are inside the six scalars.

Two arms, as `ecis.score` has: `--chained` uses T4's own OMP (the engine's arm) and the default
injects the 20 OMP numbers TALYS prints per incident energy, which isolates the coupled-channels
solve from T4 but carries the `f6.2/f6.3` print floor of `incidentecis.f90:347`, about 1e-4.

Usage:
    uv run python -m physics.hf.ecis.score_twophonon                # injected OMP
    uv run python -m physics.hf.ecis.score_twophonon --chained      # T4's OMP

Task: TWOPH (physics/hf/CONTRACT.md §7). Acceptance test: G-2PH.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import tarfile
import time
from pathlib import Path

import numpy as np
import torch

from physics.hf.core.tensors import DTYPE
from physics.hf.ecis.incident import incident_coupled
from physics.hf.ecis.reference import COLUMNS, InjectedOMP, _HEAD, _split_fixed

TOL = 1.0e-2  # A-inc, docs/results/hf-engine-gates.md §3
RAW = Path(os.environ.get("HF_TWOPH_RAW", Path.home() / "twoph_ref"))
CACHE = Path(os.environ.get("HF_TWOPH_CACHE", Path.home() / ".cache" / "incognita" / "hf_twoph"))
OUT = Path(__file__).resolve().parents[3] / "docs" / "results" / "hf-ecis-twophonon-gate.json"
VARIANT = "twophonon"

# (tag, Z, A): the three gate targets of docs/results/hf-ecis-twophonon.md §5.
TARGETS: tuple[tuple[str, int, int], ...] = (("Zn064", 30, 64), ("Cd114", 48, 114),
                                             ("Te124", 52, 124))
FIELDS = {
    "sigma_tot_omp_mb": "sigma_tot_mb",
    "sigma_reac_omp_mb": "sigma_reac_mb",
    "sigma_el_omp_mb": "sigma_shape_el_mb",
    "s0": "s0",
    "s1": "s1",
    "r_prime_fm": "r_prime_fm",
}


def run_dir(tag: str) -> Path:
    """The extracted run, unpacked into the cache on first use."""
    d = CACHE / f"{VARIANT}__{tag}"
    if not (d / "talys.out").is_file():
        src = RAW / f"{VARIANT}__{tag}.tar.gz"
        if not src.is_file():
            raise FileNotFoundError(
                f"{src} -- make it with `python3 scripts/hf_twophonon_reference.py`"
            )
        CACHE.mkdir(parents=True, exist_ok=True)
        with tarfile.open(src) as tf:
            tf.extractall(CACHE, filter="data")
    return d


def injected_omp(tag: str):
    """The 20 OMP numbers TALYS prints for the incident channel at every energy."""
    lines = (run_dir(tag) / "talys.out").read_text(errors="replace").splitlines()
    rows: list[list[float]] = []
    for i, ln in enumerate(lines):
        if _HEAD not in ln:
            continue
        for j in range(i + 1, min(i + 10, len(lines))):
            vals = _split_fixed(lines[j])
            if len(vals) == 21:
                rows.append(vals)
                break
    a = torch.tensor(rows, dtype=DTYPE)
    return InjectedOMP(a[:, 0].contiguous(),
                       **{n: a[:, k + 1].contiguous() for k, n in enumerate(COLUMNS)})


def talys_scalars(tag: str) -> dict[float, dict]:
    """The A-inc scalars per incident energy, keyed by energy."""
    from physics.hf.talys_reference import parse_talys_out

    return {round(r["e_inc_mev"], 6): r for r in parse_talys_out(run_dir(tag) / "talys.out")}


def talys_direct(tag: str) -> dict[float, dict[int, float]]:
    """`directE*.out` -> {incident energy: {level index: direct cross section in mb}}. The level
    index is TALYS's own discrete-level number, which for the coupled levels is 1..ncoll-1."""
    out: dict[float, dict[int, float]] = {}
    for p in sorted(run_dir(tag).glob("directE*.out")):
        e, rows = None, {}
        for ln in p.read_text(errors="replace").splitlines():
            m = re.match(r"#\s+E-incident \[MeV\]:\s+(\S+)", ln)
            if m:
                e = float(m.group(1))
            if ln.startswith("#"):
                continue
            f = ln.split()
            # level, energy, E-out, J, parity, cross section, def. type, def. par.
            if len(f) >= 6 and f[0].isdigit():
                rows[int(f[0])] = float(f[5])
        if e is not None:
            out[round(e, 6)] = rows
    return out


def talys_tjlinc(tag: str) -> tuple[float, np.ndarray]:
    """`(incident energy, (L, 3) array of T(l-1/2), T(l+1/2), T_l)` -- TALYS overwrites
    `transmission_inc.out` at every energy, so this is the last one."""
    p = run_dir(tag) / "transmission_inc.out"
    e, rows = float("nan"), []
    for ln in p.read_text(errors="replace").splitlines():
        m = re.match(r"#\s+E-incident \[MeV\]:\s+(\S+)", ln)
        if m:
            e = float(m.group(1))
        if ln.startswith("#"):
            continue
        f = ln.split()
        if len(f) == 4 and f[0].isdigit():
            rows.append([float(x) for x in f[1:]])
    return e, np.array(rows, dtype=float)


def _r(port: float, talys: float) -> float | None:
    if not (np.isfinite(port) and np.isfinite(talys)) or talys <= 0 or port <= 0:
        return None
    return abs(math.log(port / talys))


def score_target(tag: str, Z: int, A: int, chained: bool = False) -> dict:
    """Every G-2PH quantity of one target."""
    from physics.hf.ecis.reference import coupled_band

    band = coupled_band(Z, A)
    src = injected_omp(tag)
    e = src.e_inc_mev
    if chained:
        from physics.hf.input.defaults import default_params
        from physics.hf.omp.parameters import omp_parameters

        o = band["options"]
        p = omp_parameters(Z, A - Z, 1, e, default_params(Z, A, o), o)
    else:
        p = src
    t0 = time.time()
    inc, res = incident_coupled(p, Z, A, e, band, options=band["options"])
    dt = time.time() - t0

    rows: list[dict] = []

    def add(quantity, e_mev, port, talys, extra=None):
        v = _r(float(port), float(talys))
        if v is None:
            return
        rows.append({"target": tag, "quantity": quantity, "e_inc_mev": float(e_mev),
                     "port": float(port), "talys": float(talys), "r": v, **(extra or {})})

    ref = talys_scalars(tag)
    for i in range(e.numel()):
        key = round(float(e[i]), 6)
        if key not in ref:
            continue
        for q, field in FIELDS.items():
            if ref[key].get(q) is None:
                continue
            add(q, e[i], getattr(inc, field)[i], ref[key][q])

    direct = talys_direct(tag)
    n_lev = int(band["spin"].numel())
    for i in range(e.numel()):
        got = direct.get(round(float(e[i]), 6))
        if not got:
            continue
        for lev in range(1, n_lev):
            if lev in got:
                add("direct_inelastic_mb", e[i], res.sigma_direct_mb[i, lev], got[lev],
                    {"level": lev})

    e_t, tj = talys_tjlinc(tag)
    idx = int(np.argmin(np.abs(e.numpy() - e_t)))
    if abs(float(e[idx]) - e_t) < 1.0e-6:
        got = inc.tjl_inc[idx].detach().numpy()
        tl = inc.t_l[idx].detach().numpy()
        for L in range(min(tj.shape[0], got.shape[0])):
            add("tjlinc_minus", e_t, got[L, 0], tj[L, 0], {"l": L})
            add("tjlinc_plus", e_t, got[L, 1], tj[L, 1], {"l": L})
            add("t_l", e_t, tl[L], tj[L, 2], {"l": L})
    return {"rows": rows, "seconds": dt, "n_j": res.n_j, "ncoll": n_lev,
            "codes": list(_scheme_codes(band)), "e_tjl_mev": e_t}


def _scheme_codes(band) -> tuple[int, ...]:
    from physics.hf.ecis.vibm import scheme_from_band

    return scheme_from_band(band)[0].codes


def summarise(rows: list[dict]) -> dict:
    r = np.array([x["r"] for x in rows])
    return {"n": int(r.size), "median": float(np.median(r)), "p95": float(np.percentile(r, 95)),
            "max": float(r.max()), "pass": bool(np.percentile(r, 95) <= TOL)}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--chained", action="store_true")
    ap.add_argument("--targets", default="")
    ap.add_argument("--out", default=str(OUT))
    a = ap.parse_args(argv)
    want = set(a.targets.split(",")) if a.targets else None
    per, rows = {}, []
    for tag, Z, A in TARGETS:
        if want and tag not in want:
            continue
        got = score_target(tag, Z, A, chained=a.chained)
        rows += got["rows"]
        per[tag] = {**{k: v for k, v in got.items() if k != "rows"},
                    "summary": summarise(got["rows"])}
        print(f"{tag}: {per[tag]['summary']} in {got['seconds']:.1f}s", flush=True)
    by_q = {q: summarise([x for x in rows if x["quantity"] == q])
            for q in sorted({x["quantity"] for x in rows})}
    res = {"arm": "chained" if a.chained else "injected", "tol": TOL,
           "overall": summarise(rows), "per_quantity": by_q, "per_target": per,
           "rows": rows}
    Path(a.out).write_text(json.dumps(res, indent=1))
    print(json.dumps({"arm": res["arm"], "overall": res["overall"],
                      "per_quantity": by_q}, indent=1))
    return 0 if res["overall"]["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
