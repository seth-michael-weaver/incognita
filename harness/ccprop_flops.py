"""CCPROP gate 1: FLOPs of the current `cc_block_*` kernel against a log-derivative / R-matrix
propagator, on the real (J, parity) blocks of the 112 CC targets.

    uv run python harness/ccprop_flops.py --targets 92-238,60-150 --json out.json
    uv run python harness/ccprop_flops.py --all --json docs/results/hf-ccprop/flops.json

Nothing here is a wall clock. Every kernel call the chart path makes is logged with its exact
(N, energies, matching indices, deformed-spin-orbit flag), and the FLOPs are then counted from the
LAPACK/BLAS calls that `physics/hf/native/ccfast.c` issues at those dimensions, in the order it
issues them, with the standard complex counts registered in `docs/results/hf-ccprop.md`:

    complex N x N x N product  8 N^3        complex LU (zgetrf)             (8/3) N^3
    complex triangular solve   4 N^3 each   complex QR (zgeqrf) and zungqr  (16/3) N^3 each
    complex inverse            8 N^3        ztrsm (right, N x N by N x N)   4 N^3

`lu_solve_small` (N <= 12 on x86) is the same elimination written out, so it counts as
zgetrf + zgetrs. Terms below O(N^3) -- `build_m`, the Numerov combination, the Simpson weights --
are counted separately as `n2` and are ~1 % of the total at the N of a real block.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

# --------------------------------------------------------------------------- flop counts, N^3 units
LU = 8.0 / 3.0          # zgetrf
TRS = 4.0               # one triangular solve with N right-hand sides
SOLVE = LU + 2 * TRS    # zgetrf + zgetrs, and `lu_solve_small`
GEMM = 8.0              # zgemm
QR = 16.0 / 3.0         # zgeqrf
UNGQR = 16.0 / 3.0
TRSM = 4.0
INV = 8.0               # zgetrf + zgetri


def cur_w(nm: int, stab: int) -> float:
    """`ccfast.c::cc_block_w`, one energy: the W-form renormalised Numerov. One `mm` before the
    loop, then one `solve_n` per step and a stabilisation (QR + 3 ztrsm + zungqr) every `stab`."""
    f = GEMM
    for i in range(nm + 1):
        f += SOLVE
        if i == nm:
            break
        if i % stab == stab - 1:
            f += QR + 3 * TRSM + UNGQR
    return f


def cur_d(nm: int, stab: int) -> float:
    """`ccfast.c::cc_block_d`, one energy: the same step with the derivative coupling. Per step
    `mm(M_i u_i)`, the three `mm(nh3_k, v3_k)` (k = 2 skipped at i = 0), one `solve_n`, `mm(M_p
    u_p)` again after every stabilisation, and two more `mm` at the matching point. The
    stabilisation carries `nhist - 1` companions (up to 5)."""
    f = 0.0
    nhist, have_mu_p = 1, False
    for i in range(nm + 1):
        f += GEMM                                   # mm(Mc, uc)
        if i != 0 and not have_mu_p:
            f += GEMM                               # mm(Mp, up)
        f += GEMM * (3 if i != 0 else 2)            # mm(nh3_k, v3_k)
        f += SOLVE
        if i == nm:
            f += 2 * GEMM                           # the two s3 products
            break
        if nhist < 6:
            nhist += 1
        have_mu_p = True
        if i % stab == stab - 1:
            f += QR + (nhist - 1) * TRSM + UNGQR
            have_mu_p = False
    return f


def prop_w(nm: int, variant: str) -> float:
    """A log-derivative propagator over the same grid, one energy.

    The fused kick-and-drift of Johnson's method is
        Y <- (1/h) I - (1/h^2) (Y + Q_i + (1/h) I)^-1,
    i.e. exactly one complex inverse per half-sector, and the half-sector is one ECIS step
    (`gate 3`: the potential is sampled where ECIS samples it). Simpson's rule needs the modified
    matrix U (I + h^2 U / 6)^-1 at the panel midpoints, which is every second grid point:

    `exact`   -- the modification as a right-hand-side solve (zgetrf + zgetrs);
    `neumann` -- its leading term U - (h^2/6) U^2, one product; this is what makes the method
                 fourth order, so it cannot be dropped at equal accuracy;
    `floor`   -- the modification dropped altogether. Second order, NOT equal accuracy: it is the
                 unreachable lower bound of any propagator that does one dense O(N^3) operation
                 per ECIS step, quoted so that gate 1 is decided against the best case and not
                 against one implementation.
    """
    per_mid = {"exact": SOLVE, "neumann": GEMM, "floor": 0.0}[variant]
    steps = nm + 1
    return steps * INV + (steps // 2) * per_mid


def prop_d(nm: int, variant: str) -> float:
    """The same for the derivative-coupling equation u'' = M u + N u'. Its Riccati form is
    Y' = M + N Y - Y^2, so the sector picks up one product (Y <- (I + w N) Y) on top of the
    inverse: the N u' term cannot be folded into a diagonal reference."""
    per_mid = {"exact": SOLVE, "neumann": GEMM, "floor": 0.0}[variant]
    steps = nm + 1
    return steps * (INV + GEMM) + (steps // 2) * per_mid


# --------------------------------------------------------------------------------- the block log
_LOG: list[dict] = []


def _hook():
    """Record every `cc_block_w` / `cc_block_d` call the chart path makes."""
    from physics.hf.ecis import ccnative

    real = ccnative._keep_raw

    def spy(ch, ff, kin, h_fm, nmatch, r_fm, stab=ccnative.STABILISE_EVERY):
        _LOG.append({
            "n": int(ch.level.numel()),
            "nmatch": [int(v) for v in nmatch.tolist()],
            "deformed": bool(ch.so_deriv_coef is not None and ff.so_r2 is not None),
            "stab": int(stab),
        })
        return real(ch, ff, kin, h_fm, nmatch, r_fm, stab)

    ccnative._keep_raw = spy


def run_target(Z: int, A: int, grid) -> None:
    import torch

    from physics.hf.core.tensors import DTYPE
    from physics.hf.ecis import incident as inc_mod
    from physics.hf.ecis.incident import incident_coupled
    from physics.hf.ecis.reference import coupled_band

    band = coupled_band(Z, A)
    inc_mod._SOLVED.clear()
    incident_coupled(None, Z, A, torch.tensor(list(grid), dtype=DTYPE), band)
    inc_mod._SOLVED.clear()


def totals(log: list[dict]) -> dict:
    out: dict[str, float] = {}
    counts = {"calls_w": 0, "calls_d": 0, "steps_w": 0, "steps_d": 0}
    for rec in log:
        n3 = float(rec["n"]) ** 3
        deformed = rec["deformed"]
        counts["calls_d" if deformed else "calls_w"] += 1
        for nm in rec["nmatch"]:
            counts["steps_d" if deformed else "steps_w"] += nm + 1
            if deformed:
                out["cur"] = out.get("cur", 0.0) + cur_d(nm, rec["stab"]) * n3
                out["cur_d"] = out.get("cur_d", 0.0) + cur_d(nm, rec["stab"]) * n3
                for v in ("exact", "neumann", "floor"):
                    out[f"prop_{v}"] = out.get(f"prop_{v}", 0.0) + prop_d(nm, v) * n3
                    out[f"prop_{v}_d"] = out.get(f"prop_{v}_d", 0.0) + prop_d(nm, v) * n3
            else:
                out["cur"] = out.get("cur", 0.0) + cur_w(nm, rec["stab"]) * n3
                out["cur_w"] = out.get("cur_w", 0.0) + cur_w(nm, rec["stab"]) * n3
                for v in ("exact", "neumann", "floor"):
                    out[f"prop_{v}"] = out.get(f"prop_{v}", 0.0) + prop_w(nm, v) * n3
                    out[f"prop_{v}_w"] = out.get(f"prop_{v}_w", 0.0) + prop_w(nm, v) * n3
    out.update(counts)
    return out


def main(argv) -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--targets", default="")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--json", default="")
    a = ap.parse_args(argv)

    import numpy as np
    import torch

    torch.set_num_threads(2)
    design = json.loads((REPO / "features" / "talys_sweep_broad" / "design.json")
                        .read_text().replace("NaN", "null"))
    grid = tuple(float(np.float32(float(f"{float(x):.6E}"))) for x in design["energies_mev"])
    if a.all:
        from physics.hf.ecis.reference import coupled_band
        picks = []
        for x in design["nuclides"]:
            Z, A_ = int(x["Z"]), int(x["A"])
            try:
                b = coupled_band(Z, A_)
            except Exception:  # noqa: BLE001
                continue
            if b["colltype"] in ("R", "V") and int(b["spin"].numel()) > 1:
                picks.append((Z, A_))
    else:
        picks = [tuple(int(v) for v in t.split("-")) for t in a.targets.split(",") if t]

    _hook()
    per: dict[str, dict] = {}
    for Z, A_ in picks:
        start = len(_LOG)
        try:
            run_target(Z, A_, grid)
        except Exception as exc:  # noqa: BLE001
            print(f"{Z}-{A_}: {type(exc).__name__}: {exc}", file=sys.stderr)
            continue
        per[f"{Z}-{A_}"] = totals(_LOG[start:])
        t = per[f"{Z}-{A_}"]
        print(f"{Z}-{A_:<4} cur {t['cur']:.4e}  exact/cur {t['prop_exact']/t['cur']:.3f}  "
              f"neumann/cur {t['prop_neumann']/t['cur']:.3f}  floor/cur {t['prop_floor']/t['cur']:.3f}",
              flush=True)
    agg = totals(_LOG)
    res = {"targets": len(per), "grid_points": len(grid), "aggregate": agg, "per_target": per,
           "ratios": {k: agg[f"prop_{k}"] / agg["cur"] for k in ("exact", "neumann", "floor")}}
    for path in ("w", "d"):
        if f"cur_{path}" in agg:
            res["ratios"][f"{path}_share_of_cur"] = agg[f"cur_{path}"] / agg["cur"]
            for k in ("exact", "neumann", "floor"):
                res["ratios"][f"{k}_over_cur_{path}"] = agg[f"prop_{k}_{path}"] / agg[f"cur_{path}"]
    txt = json.dumps(res, indent=1)
    if a.json:
        Path(a.json).parent.mkdir(parents=True, exist_ok=True)
        Path(a.json).write_text(txt)
    print(json.dumps({"aggregate": agg, "ratios": res["ratios"]}, indent=1))


if __name__ == "__main__":
    main(sys.argv[1:])
