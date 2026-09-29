"""A-pe: score the ported pre-equilibrium against TALYS's `exciton*.out` and `preeq*.out`.

Task: T8 (physics/hf/CONTRACT.md §6/§7). Gate: A-pe, p95 |ln(port/TALYS)| <= 0.02.

    uv run python -m physics.hf.preeq.score              # all 24 targets, default variant
    uv run python -m physics.hf.preeq.score --target Fe056 --json out.json

Metric and floors are `docs/results/hf-engine-gates.md` §2: cross sections are gated above
1e-3 mb, and a point where TALYS is below the floor but the port is above it counts as
`r = inf`. The `exciton*.out` quantities (matrix elements, emission rates, escape and damping
widths, transition rates, lifetimes) have no cross-section floor, so every point TALYS printed
non-zero is scored.
"""

from __future__ import annotations

import argparse
import json

import numpy as np
import torch

from physics.hf import reference as ref
from physics.hf.core.constants import talys_constants
from physics.hf.input.nuclides import coulomb_barriers
from physics.hf.preeq.exciton import preequilibrium
from physics.hf.preeq.prepare import energies_for, prepare

XS_FLOOR_MB = 1.0e-3
TOLERANCE = 0.02
# TALYS writes exciton*.out in real(sgl): a width or lifetime below the float32 smallest
# normal (1.18e-38) underflows to 0.000000E+00 on the `* hbar` multiply even though the
# emission rate it came from prints fine. Those points are TALYS's own underflow, not a
# disagreement, so they sit below the floor (contract §4.1, gates doc §2).
SGL_FLOOR = 1.0e-37
FLOORS = {
    "escape width": SGL_FLOOR,
    "damping width": SGL_FLOOR,
    "total width": SGL_FLOOR,
    "lifetime": SGL_FLOOR,
    "emission rate": SGL_FLOOR,
    "internal transition rate": SGL_FLOOR,
}
PARNAME = ("gamma", "neutron", "proton", "deuteron", "triton", "helium-3", "alpha")
SPHERICAL_SKIP = ("Am241", "Pu239", "Th232", "U235", "U238", "Au197", "Ca040")


def _r(port: np.ndarray, talys: np.ndarray, floor: float = 0.0) -> np.ndarray:
    """|ln(port/TALYS)| where TALYS is above `floor`, plus inf where only the port is."""
    live = talys > floor
    out = np.full(port.shape, np.nan)
    with np.errstate(divide="ignore", invalid="ignore"):
        out[live] = np.abs(np.log(np.maximum(port[live], 1e-300) / talys[live]))
    extra = (~live) & (np.abs(port) > floor)
    out[extra] = np.inf
    return out[live | extra]


def _stats(r: np.ndarray) -> dict:
    if r.size == 0:
        return {"n": 0}
    finite = np.isfinite(r)
    # np.percentile sorts, so the inf points sit at the top: p95 stays finite as long as
    # fewer than 5% of the points are ones TALYS never produced.
    return {
        "n": int(r.size),
        "n_extra": int((~finite).sum()),
        "median": float(np.median(r[finite])) if finite.any() else float("inf"),
        "p95": float(np.percentile(r, 95)),
        "max": float(r.max()),
    }


def score_target(target: str, variant: str = "default") -> dict:
    """Every A-pe quantity for one target, at every dumped incident energy."""
    inp, hdr = prepare(target, variant)
    options, params = hdr["options"], hdr["params"]
    energies = hdr["energies"]
    cb = coulomb_barriers(options)
    inc = ref.incident_scalars(target, variant)
    reac = {round(float(r.e_inc_mev), 6): float(r.sigma_reac_omp_mb) for _, r in inc.iterrows()}
    xsreacinc = torch.tensor([reac[round(e, 6)] for e in energies], dtype=torch.float64)
    res = preequilibrium(
        inp, options, params, hdr["discrete"], coulbar_mev=cb, xsreacinc_mb=xsreacinc
    )
    hbar = talys_constants()["hbar"]
    acc: dict[str, list] = {}
    add = lambda k, r: acc.setdefault(k, []).append(r)  # noqa: E731

    for ei, e in enumerate(energies):
        # --- exciton*.out
        for _b, (meta, w) in ref.blocks(
            "exciton", target, f"exciton{e:08.3f}.out", variant
        ).items():
            q = meta["type"]
            if q == "matrix element":
                port = torch.stack(
                    [res[k][ei] for k in ("M2pipi", "M2nunu", "M2pinu", "M2nupi")], 1
                )
                tal = w[["M2pipi", "M2nunu", "M2pinu", "M2nupi"]].to_numpy()
            elif q in ("emission rate", "escape width"):
                cols = list(PARNAME) + ["Total"]
                tal = w[cols].to_numpy()
                port = torch.cat([res["wemispart2"][ei], res["wemistot2"][ei : ei + 1].T], 1)
                if q == "escape width":
                    port = port * hbar
            elif q in ("internal transition rate", "damping width"):
                ks = ["lambdapiplus", "lambdanuplus", "lambdapinu", "lambdanupi"]
                cols = (
                    ks
                    if q == "internal transition rate"
                    else ["gammapiplus", "gammanuplus", "gammapinu", "gammanupi"]
                )
                tal = w[cols].to_numpy()
                port = torch.stack([res[k][ei] for k in ks], 1)
                if q == "damping width":
                    port = port * hbar
            elif q == "total width":
                tal = w[["gammatot"]].to_numpy()
                port = (
                    (
                        res["lambdapiplus"]
                        + res["lambdanuplus"]
                        + res["lambdapinu"]
                        + res["lambdanupi"]
                        + res["wemistot2"]
                    )[ei]
                    * hbar
                ).reshape(-1, 1)
            elif q == "lifetime":
                tal = w[["Strength"]].to_numpy()
                port = res["Spre"][ei].reshape(-1, 1)
            else:
                continue
            add(q, _r(port.detach().numpy(), tal, FLOORS.get(q, 0.0)))

        # --- preeq*.out spectra
        eg = inp.egrid_mev[ei].numpy()
        blocks = ref.blocks("preequilibrium", target, f"preeq{e:08.3f}.out", variant)
        for _b, (meta, w) in blocks.items():
            if meta.get("type") != "emission spectrum":
                continue
            # preeqout.f90 writes a block only for the open channels, so the block index is
            # not the particle type: read the type off the block's own `particle` field.
            t = PARNAME.index(str(meta["particle"]).strip())
            eo = w["E-out"].to_numpy()
            idx = np.array([int(np.argmin(np.abs(eg - x))) for x in eo])
            for col, key in (
                ("Total", "xspreeq"),
                ("Pickup/strip", "xspreeqps"),
                ("Knockout", "xspreeqki"),
                ("Breakup", "xspreeqbu"),
            ):
                if col not in w:
                    continue
                add(
                    f"spectrum {col}",
                    _r(res[key][ei, t].detach().numpy()[idx], w[col].to_numpy(), XS_FLOOR_MB),
                )
            exciton_only = res["xsstep"][ei, t, 1:].sum(0).detach().numpy()[idx]
            add(
                "spectrum Exciton model",
                _r(exciton_only, w["Exciton model"].to_numpy(), XS_FLOOR_MB),
            )
            for p in range(1, res["xsstep"].shape[2]):
                if f"p={p}" not in w:
                    continue
                add(
                    "spectrum per stage",
                    _r(
                        res["xsstep"][ei, t, p].detach().numpy()[idx],
                        w[f"p={p}"].to_numpy(),
                        XS_FLOOR_MB,
                    ),
                )
        tot = float(str(blocks[1][0].get("Pre-equilibrium cross section [mb]", "nan")).split()[0])
        if np.isfinite(tot) and tot > XS_FLOOR_MB:
            add(
                "total cross section",
                _r(np.array([float(res["xspreeqsum"][ei])]), np.array([tot]), XS_FLOOR_MB),
            )

    quantities = {k: _stats(np.concatenate(v)) for k, v in acc.items()}
    return {
        "target": target,
        "variant": variant,
        "energies": energies,
        "quantities": quantities,
        "worst_p95": max((q["p95"] for q in quantities.values() if q.get("n")), default=0.0),
    }


def summarise(records: list[dict]) -> dict:
    per_q: dict[str, list] = {}
    for rec in records:
        for k, v in rec["quantities"].items():
            if v.get("n"):
                per_q.setdefault(k, []).append((rec["target"], v["p95"], v["max"]))
    out = {}
    for k, rows in per_q.items():
        worst = max(rows, key=lambda r: r[1])
        out[k] = {
            "targets": len(rows),
            "worst_target": worst[0],
            "worst_p95": worst[1],
            "worst_max": max(r[2] for r in rows),
        }
    return {
        "tolerance": TOLERANCE,
        "per_quantity": out,
        "pass": all(v["worst_p95"] <= TOLERANCE for v in out.values()),
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description="A-pe gate (pre-equilibrium)")
    ap.add_argument("--target", action="append")
    ap.add_argument("--variant", default="default")
    ap.add_argument("--json")
    args = ap.parse_args(argv)
    if not ref.available("exciton"):
        raise SystemExit("reference dumps not parsed (features/hf_reference/exciton.parquet)")
    targets = args.target or sorted(ref._family("exciton")["target"].unique())
    records = []
    for t in targets:
        if not energies_for(t, args.variant):
            continue
        try:
            rec = score_target(t, args.variant)
        except Exception as exc:  # noqa: BLE001
            print(f"{t}: FAILED {type(exc).__name__}: {exc}")
            records.append(
                {"target": t, "variant": args.variant, "error": str(exc), "quantities": {}}
            )
            continue
        records.append(rec)
        print(f"{t}: worst p95 {rec['worst_p95']:.3e}")
    summary = summarise(records)
    print(json.dumps(summary["per_quantity"], indent=2, sort_keys=True))
    print("A-pe", "PASS" if summary["pass"] else "FAIL", f"(tolerance {TOLERANCE})")
    if args.json:
        with open(args.json, "w") as fh:
            json.dump({"summary": summary, "records": records}, fh, indent=2)
    return 0 if summary["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
