"""Score the ported gamma-strength machinery against TALYS: gate A-psf.

Reference: the `psf<ZZZ><AAA>.{E1,M1,E2,M2}` files of every reference dump (gamma.f90:30 writes
them for the compound nucleus at the first incident energy only), read through
`physics.hf.reference`. Quantities scored, all against the columns TALYS itself printed:

* ``f(E1)`` / ``f(M1)`` -- fstrength at Efs = 0, the call gammaout.f90 makes.
* ``T(E1) T(M1) T(E2) T(M2)`` -- Tjl(0, nen, irad, l) from tgamma, so E2/M2 are gated too.
  (The *f* column of psf*.E2/.M2 is NOT f(E2)/f(M2): gammaout.f90 hard-wires l = 1. See
  tests/hf/test_gamma.py::test_talys_psf_E2_M2_files_carry_the_l1_strength.)
* ``Gamma_gamma`` and ``S-wave strength function`` -- radwidtheory, with rho(Ex, J, pi) injected
  from the compound nucleus's ld*.gs tables (contract §5) until T6's density is wired in.

Metric (docs/results/hf-engine-gates.md §2): r = |ln(port/TALYS)| over points where TALYS is
above the floor; the gate is p95(r) <= 0.01 over all points of all reference targets.

    python -m physics.hf.gamma.score --out docs/results/hf-psf-gate.json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import torch
from scipy.interpolate import CubicSpline

from physics.hf import reference as ref
from physics.hf.gamma.parameters import gamma_parameters
from physics.hf.gamma.strength import fstrength_gp
from physics.hf.gamma.transmission import radwidtheory, tgamma
from physics.hf.input.defaults import default_options
from physics.hf.talys_reference import ENERGIES_MEV

TOL = 0.01  # A-psf
FLOOR = 1e-30
RADIATIONS = (("E1", 1, 1), ("M1", 0, 1), ("E2", 1, 2), ("M2", 0, 2))

# fstrength's tabulated E1 branch interpolates the SMLO tables in the nuclear temperature
# Tnuc = sqrt((Efs + Sn - delta - Egamma) / a) (fstrength.f90, the nTqrpa > 1 path), and
# radwidtheory integrates that f(E1). Both `a` and `delta` are injected from the ld*.gs header
# (contract §5) -- but densityout.f90 prints them only for the analytical level-density models.
# An ldmodel 7 nucleus (every actinide: input_densitymodel.f90:90 resolves ldmodelall to 7 for a
# neutron on A > fislim) therefore carries no reference value for them, so these four quantities
# are reported and NOT gated for such a case. See docs/results/hf-psf-gate.json "ungated".
T_DEPENDENT = frozenset({"f(E1)", "T(E1)", "Gamma_gamma", "S-wave"})
TEMPERATURE_KEYS = ("pairing energy [MeV]", "a(Sn) [MeV^-1]")


def has_temperature_inputs(ld_meta: dict) -> bool:
    return all(k in ld_meta for k in TEMPERATURE_KEYS)


def _frames():
    import pandas as pd

    d = ref.reference_dir()
    return (
        pd.read_parquet(d / "psf.parquet"),
        pd.read_parquet(d / "level_density.parquet"),
        pd.read_parquet(d / "raw_rows.parquet"),
    )


def _wide(df):
    return df.pivot_table(index="row", columns="column", values="value", observed=True)


def _meta(df) -> dict:
    return json.loads(df["meta"].iloc[0])


def cases(psf) -> list[tuple[str, str, int, int]]:
    """(target, variant, Z, A) of every compound nucleus with a psf*.E1 file."""
    out = []
    for (target, variant, file), _ in psf.groupby(["target", "variant", "file"], observed=True):
        if file.endswith(".E1"):
            tag = file[3:9]
            out.append((target, variant, int(tag[:3]), int(tag[3:])))
    return sorted(set(out))


def _levels(raw, target: str, variant: str, Z: int, A: int):
    """(E [MeV], J, parity) of the discrete levels TALYS printed for (Z, A)."""
    s = raw[
        (raw.target == target)
        & (raw.variant == variant)
        & (raw.file == f"levels{Z:03d}{A:03d}.out")
    ]
    out = []
    for line in s.sort_values(["block", "row"])["line"]:
        if "--->" in line:
            continue
        f = line.split()
        if len(f) < 4 or f[3] not in "+-":
            continue
        out.append((float(f[1]), float(f[2]), 1 if f[3] == "+" else -1))
    return out


def _density_from_dump(g):
    """rho(Ex, J, parity) [MeV^-1] off the ld*.gs per-parity tables, cubic in ln(rho).

    This interpolation is the injection (contract §5), not the port: radwidtheory integrates
    rho over Egamma on its own grid, so whatever error the interpolation makes lands on
    <Gamma_gamma>. Cubic rather than linear because linear dominates the residual -- Nb-93
    6.3e-4 -> 4.1e-5, Au-197 4.0e-4 -> 2.4e-5, W-184 2.8e-4 -> 3.0e-5, Ca-40 1.0e-5 -> 4.6e-6 --
    and a gate number should measure the port. It goes away when T6's analytical rho replaces
    the tabulated injection.
    """
    tabs: dict[int, tuple] = {}
    for _, gb in g.groupby("block", observed=True):
        m = _meta(gb)
        if "Parity" not in m or int(m["Parity"]) in tabs:
            continue
        w = _wide(gb)
        if "E" not in w:
            continue
        jc = [c for c in w.columns if str(c).startswith("rho(J)=")]
        tabs[int(m["Parity"])] = (
            w["E"].to_numpy(),
            np.array([float(str(c).split("=")[1]) for c in jc]),
            np.log(np.maximum(w[jc].to_numpy(), 1e-300)),
        )

    def density(ex, J, parity):
        E, js, lr = tabs[parity]
        idx = [int(np.argmin(np.abs(js - j))) for j in J.numpy()]
        x = ex.numpy()
        cols = [np.exp(CubicSpline(E, lr[:, k])(x)) for k in idx]
        return torch.tensor(np.stack(cols, -1), dtype=torch.float64)

    return density


def _r(port: np.ndarray, talys: np.ndarray) -> np.ndarray:
    msk = talys > FLOOR
    return np.abs(np.log(port[msk] / talys[msk]))


def score_case(frames, case: tuple[str, str, int, int]) -> dict:
    psf, ld, raw = frames
    target, variant, Z, A = case
    tag = f"{Z:03d}{A:03d}"
    sub = psf[(psf.target == target) & (psf.variant == variant)]
    g = ld[(ld.target == target) & (ld.variant == variant) & (ld.file == f"ld{tag}.gs")]
    m = _meta(g)
    hdr = {rad: _meta(sub[sub.file == f"psf{tag}.{rad}"]) for rad in ("E1", "M1", "E2", "M2")}
    tables = {rad: _wide(sub[sub.file == f"psf{tag}.{rad}"]) for rad in ("E1", "M1", "E2", "M2")}
    beta2 = float(hdr["M1"].get("pygmy tpr [mb]", 0.0)) / (1.0e-2 * A**0.9)
    have_T = has_temperature_inputs(m)

    gp = gamma_parameters(
        Z,
        A,
        default_options(Z, A - 1),
        S_k0_mev=float(m["separation energy [MeV]"]),
        delta_mev=float(m.get("pairing energy [MeV]", 0.0)),
        alev_per_mev=float(m.get("a(Sn) [MeV^-1]", 0.0)),
        beta2=beta2,
        flagcol=m.get("collective enhancement", "n") == "y",
    )

    rec: dict = {
        "target": target,
        "variant": variant,
        "Z": Z,
        "A": A,
        "strength": gp.strength,
        "strengthM1": gp.strengthM1,
        "ldmodel": m.get("ldmodel keyword"),
        "psf_model": hdr["E1"].get("PSF model", "").strip(),
        "temperature_inputs": have_T,
        "quantities": {},
        "ungated": [] if have_T else sorted(T_DEPENDENT),
    }

    # f(E1), f(M1) at the energies TALYS tabulated
    for rad, irad in (("E1", 1), ("M1", 0)):
        w = tables[rad]
        e = torch.tensor(w["E"].to_numpy(), dtype=torch.float64)
        port = fstrength_gp(gp, 0.0, e, irad, 1).numpy()
        rec["quantities"][f"f({rad})"] = _stats(_r(port, w[f"f({rad})"].to_numpy()))

    # T(XL): every multipolarity, at the first incident energy (the one gamma.f90 dumps)
    w = tables["E1"]
    n = int((w["T(E1)"] > 0).sum())  # TALYS pads the table with T = 0 beyond egrid
    e = torch.tensor(w["E"].to_numpy()[:n], dtype=torch.float64)
    tr = tgamma(gp, e, ENERGIES_MEV[0], Z, A - 1)
    for rad, irad, ell in RADIATIONS:
        talys = tables[rad][f"T({rad})"].to_numpy()[:n]
        rec["quantities"][f"T({rad})"] = _stats(_r(tr.tjl[:, irad, ell].numpy(), talys))

    # theoretical <Gamma_gamma> and the S-wave strength function
    lv = _levels(raw, target, variant, Z, A)
    tg = _levels(raw, target, variant, Z, A - 1)
    if lv and tg:
        rw = radwidtheory(
            gp,
            float(hdr["E1"]["average resonance energy [eV]"]) * 1.0e-6,
            float(m["separation energy [MeV]"]),
            torch.tensor([x[0] for x in lv]),
            torch.tensor([x[1] for x in lv]),
            torch.tensor([x[2] for x in lv]),
            tg[0][1],
            tg[0][2],
            _density_from_dump(g),
            float(m["theoretical D0 [eV]"]),
        )
        th = float(hdr["E1"]["theoretical Gamma_gamma [eV]"])
        sw = float(hdr["E1"]["theoretical S-wave strength function [e-4]"]) * 1.0e-4
        rec["quantities"]["Gamma_gamma"] = _stats(
            np.array([abs(np.log(float(rw.gamgamth0_ev) / th))])
        )
        rec["quantities"]["S-wave"] = _stats(np.array([abs(np.log(float(rw.swaveth) / sw))]))
        rec["gamgam_ev"] = {"port": float(rw.gamgamth0_ev), "talys": th}
    else:
        rec["quantities"]["Gamma_gamma"] = None
        rec["quantities"]["S-wave"] = None
    return rec


def _stats(r: np.ndarray) -> dict:
    if r.size == 0:
        return {"n": 0}
    return {
        "n": int(r.size),
        "p95": float(np.percentile(r, 95)),
        "median": float(np.median(r)),
        "max": float(r.max()),
    }


def summarise(records: list[dict]) -> dict:
    per_quantity: dict[str, list[float]] = {}
    worst: dict[str, tuple[float, str]] = {}
    for rec in records:
        ungated = set(rec.get("ungated") or ())
        for name, st in rec["quantities"].items():
            if not st or not st.get("n") or name in ungated:
                continue
            per_quantity.setdefault(name, []).append(st["p95"])
            tag = f"{rec['target']}-{rec['variant']}"
            if name not in worst or st["max"] > worst[name][0]:
                worst[name] = (st["max"], tag)
    overall = max((max(v) for v in per_quantity.values()), default=float("nan"))
    ungated_cases = [
        f"{r['target']}-{r['variant']}" for r in records if not r.get("temperature_inputs", True)
    ]
    return {
        "gate": "A-psf",
        "tolerance": TOL,
        "targets": len({r["target"] for r in records}),
        "cases": len(records),
        "ungated_quantities": sorted(T_DEPENDENT),
        "ungated_cases": ungated_cases,
        "ungated_reason": (
            "ld*.gs prints a(Sn) and the pairing energy only for the analytical level-density "
            "models; an ldmodel 7 nucleus has no reference value for the two inputs fstrength's "
            "temperature branch needs (needs T6 densitypar)"
        ),
        "worst_p95_per_quantity": {k: max(v) for k, v in per_quantity.items()},
        "worst_case_per_quantity": {k: {"max": v[0], "case": v[1]} for k, v in worst.items()},
        "worst_p95_overall": overall,
        "pass": bool(overall <= TOL),
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path, default=None, help="write the full report as JSON")
    ap.add_argument("--target", default=None, help="score one target only")
    a = ap.parse_args(argv)

    if not (ref.available("psf") and ref.available("level_density") and ref.available("raw_rows")):
        raise SystemExit("reference dumps not parsed (features/hf_reference)")
    frames = _frames()
    cs = [c for c in cases(frames[0]) if a.target is None or c[0] == a.target]
    if not cs:
        raise SystemExit("no psf cases in the reference dumps")

    records = [score_case(frames, c) for c in cs]
    names = list(records[0]["quantities"])
    head = f"{'target':>8} {'variant':>8} " + " ".join(f"{n:>11}" for n in names)
    print(head)
    print("-" * len(head))
    for rec in records:
        row = f"{rec['target']:>8} {rec['variant']:>8} "
        ungated = set(rec.get("ungated") or ())
        for n in names:
            st = rec["quantities"].get(n)
            if not st or not st.get("n"):
                row += f" {'-':>10}"
            elif n in ungated:
                row += f" {'(' + format(st['p95'], '.1e') + ')':>10}"
            else:
                row += f" {st['p95']:>10.2e}"
        print(row)
    s = summarise(records)
    print(
        f"\nA-psf: worst p95 {s['worst_p95_overall']:.3g} over {s['cases']} cases "
        f"({s['targets']} targets), tolerance {TOL} -> {'PASS' if s['pass'] else 'FAIL'}"
    )
    for n, w in s["worst_case_per_quantity"].items():
        print(f"  worst single point {n:>12}: {w['max']:.3g} ({w['case']})")
    if s["ungated_cases"]:
        print(
            f"\n  (...) = not gated, {len(s['ungated_cases'])} cases: {s['ungated_reason']}\n"
            f"        {', '.join(s['ungated_cases'])}"
        )
    if a.out:
        a.out.parent.mkdir(parents=True, exist_ok=True)
        a.out.write_text(json.dumps({"summary": s, "cases": records}, indent=2) + "\n")
        print(f"wrote {a.out}")
    return 0 if s["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
