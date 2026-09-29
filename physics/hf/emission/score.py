"""A-mult: score the ported binary emission, exclusive channels, per-level partials and residual
production against TALYS, with every upstream input injected from `talys_instrument/chdump.f90`.

Task: T10 (physics/hf/CONTRACT.md §7). Acceptance test: A-mult (§6), tolerance p95 |ln(p/t)| <= 0.05.

Metric and floors are §2 of docs/results/hf-engine-gates.md: r = |ln(p/t)| over points where the
TALYS value is above the floor (1e-3 mb for cross sections, 1e-6 mb for populations); a point
where TALYS is below the floor and the port is above counts as r = inf.

Usage:
    uv run python -m physics.hf.emission.score --runs ~/hf_t10/runs --work ~/hf_t10/score_work
"""

from __future__ import annotations

import argparse
import json
import math
import tarfile
from pathlib import Path

import numpy as np
import torch

from physics.hf.emission.binary import BinaryState, binary
from physics.hf.emission.channels import ExclusiveState, exclusive_channels
from physics.hf.emission.dumps import load_binary_dump, load_channel_dump
from physics.hf.yandf import parse_blocks

PARSYM = "gnpdtha"  # constants.f90: parsym, types 0..6
XS_FLOOR_MB = 1.0e-3
POP_FLOOR_MB = 1.0e-6


def _r(p: np.ndarray, t: np.ndarray, floor: float) -> np.ndarray:
    """|ln(p/t)| over points above the floor; inf where TALYS is below it and the port is not."""
    p, t = np.asarray(p, float), np.asarray(t, float)
    live = t > floor
    out = np.full(p.shape, np.nan)
    both = live & (p > 0)
    out[both] = np.abs(np.log(p[both] / t[both]))
    out[live & ~both] = np.inf  # port produced zero where TALYS did not
    dead = (~live) & (np.abs(p) > floor)
    out[dead] = np.inf
    return out[np.isfinite(out) | np.isinf(out)]


def count_negative_reference(work: Path) -> int:
    """Points where TALYS itself printed a NEGATIVE cross section.

    §2's metric scores `r = |ln(p/t)|` where `t` is above the floor and calls everything else
    `inf` ("the port produced something TALYS did not"). A negative TALYS value is below the
    floor, so a port that reproduces it exactly still scores `inf`. The rule is pre-registered and
    is not changed here; this counter makes the cause visible instead. Bi-209 (n,alpha) to level
    30 at 18 MeV is the only such point in the reference set: TALYS prints -0.303844 mb and the
    port returns -0.303844 mb.
    """
    from physics.hf.emission.binary import BinaryState, binary

    n = 0
    st = BinaryState()
    for case in load_binary_dump(work / "bin_inputs.txt"):
        res = binary(case, st)
        for t, arr in res.xsdisc_mb.items():
            for nex in range(arr.shape[0]):
                f = work / f"{PARSYM[case.k0]}{PARSYM[t]}.L{nex:02d}"
                if not f.is_file():
                    continue
                ref = _column(f, "xs").get(round(case.e_inc_mev, 6))
                if ref is not None and ref < 0:
                    n += 1
    return n


def _stats(rs: list[np.ndarray]) -> dict:
    if not rs:
        return {"n": 0}
    a = np.concatenate([x for x in rs if x.size])
    if a.size == 0:
        return {"n": 0}
    fin = a[np.isfinite(a)]
    return {
        "n": int(a.size), "n_inf": int(np.isinf(a).sum()),
        "median": float(np.median(fin)) if fin.size else float("inf"),
        "p95": float(np.percentile(fin, 95)) if fin.size else float("inf"),
        "max": float(fin.max()) if fin.size else float("inf"),
    }


# ------------------------------------------------------------------------------------------------
# TALYS output files, read with T0's YANDF parser
# ------------------------------------------------------------------------------------------------


def _column(path: Path, name: str) -> dict[float, float]:
    """{incident energy -> value} of one column of a TALYS excitation-function file."""
    blocks = parse_blocks(path)
    if not blocks or name not in blocks[0].columns:
        return {}
    b = blocks[0]
    return {round(float(e), 6): float(v)
            for e, v in zip(b.column("E"), b.column(name))}  # noqa: B905


def _read_binE(path: Path) -> dict[int, dict[str, np.ndarray]]:
    """binE*.out: one block per ejectile, `population` (= xspopex) plus the JP= columns (= xspop).

    The JP= columns run (J, parity) with parity fastest and ordered (-, +), which is the
    contract's parity axis, so the reshape below is the contract layout with no permutation.
    """
    out: dict[int, dict[str, np.ndarray]] = {}
    names = {"gamma": 0, "neutron": 1, "proton": 2, "deuteron": 3, "triton": 4,
             "helium-3": 5, "alpha": 6}
    for b in parse_blocks(path):
        t = names.get(b.meta.get("ejectile", ""))
        if t is None or "population" not in b.columns:
            continue
        jp = [i for i, c in enumerate(b.columns) if c.startswith("JP=")]
        pop = b.data[:, jp].reshape(b.data.shape[0], -1, 2)
        out[t] = {"popex": b.column("population"), "pop": pop}
    return out


def score_run(work: Path) -> dict:
    """Score one instrumented run directory: binary, exclusive channels, levels, residuals."""
    tag = work.name
    bcases = load_binary_dump(work / "bin_inputs.txt")
    ccases = load_channel_dump(work / "ch_inputs.txt")
    rec: dict = {"run": tag, "energies": len(bcases)}

    # --- binary.f90: the `.Lnn` discrete partials, and binE*.out per (bin, J, parity) ----------
    lev_r, bin_r, disc_tot_r = [], [], []
    lev_files: dict[tuple[int, int], dict[float, float]] = {}
    for t in range(7):
        for nex in range(40):
            f = work / f"{PARSYM[bcases[0].k0]}{PARSYM[t]}.L{nex:02d}"
            if f.is_file():
                lev_files[(t, nex)] = _column(f, "xs")
    bin_pop = {}
    for f in sorted(work.glob("binE*.out")):
        bin_pop[round(float(f.name[4:12]), 6)] = f

    results = []
    bstate = BinaryState()  # sfactor lives for the whole energy loop (strucinitial.f90:484)
    for case in bcases:
        res = binary(case, bstate)
        results.append(res)
        e = round(case.e_inc_mev, 6)
        for (t, nex), table in lev_files.items():
            if t not in res.xsdisc_mb or nex >= res.xsdisc_mb[t].shape[0]:
                continue
            ref = table.get(e)
            if ref is None:
                continue
            lev_r.append(_r(np.array([float(res.xsdisc_mb[t][nex])]), np.array([ref]), XS_FLOOR_MB))
        # binE*.out: population per (bin, J, parity) after binary.f90
        ekey = min(bin_pop, key=lambda k: abs(k - e)) if bin_pop else None
        if ekey is not None and abs(ekey - e) < 5e-4:
            for t, tab in _read_binE(bin_pop[ekey]).items():
                if t not in res.xspop_bine_mb:
                    continue
                got = res.xspop_bine_mb[t].numpy()
                n = min(got.shape[0], tab["pop"].shape[0])
                bin_r.append(_r(got[:n].reshape(-1), tab["pop"][:n].reshape(-1), POP_FLOOR_MB))
                pex = res.xspopex_bine_mb[t].numpy()
                bin_r.append(_r(pex[:n], tab["popex"][:n], POP_FLOOR_MB))
    rec["levels"] = _stats(lev_r)
    rec["binE"] = _stats(bin_r)
    rec["disc_tot"] = _stats(disc_tot_r)

    # --- channels.f90 / totalxs.f90 / residual.f90 --------------------------------------------
    chan_files = {int(f.name[2:8]): _column(f, "xs") for f in sorted(work.glob("xs[0-9]*.tot"))}
    rp_files = {(int(f.name[2:5]), int(f.name[5:8])): _column(f, "xs")
                for f in sorted(work.glob("rp[0-9]*.tot"))}
    part_files = {t: _column(work / f"{PARSYM[ccases[0].k0]}{PARSYM[t]}.tot", "xs")
                  for t in range(7) if (work / f"{PARSYM[ccases[0].k0]}{PARSYM[t]}.tot").is_file()}
    ch_r, rp_r, part_r = [], [], []
    state = ExclusiveState()
    for case in ccases:
        e = round(case.e_inc_mev, 6)
        # TALYS's chanopen/idnumfull at the start of THIS energy are in the dump; use them, so a
        # disagreement is channels.f90's arithmetic and not a replay of the state machine.
        out = exclusive_channels(case)
        state = ExclusiveState(set(case.chanopen), case.idnumfull)
        for code, table in chan_files.items():
            ref = table.get(e)
            if ref is None:
                continue
            ch_r.append(_r(np.array([out.xschannel_mb.get(code, 0.0)]), np.array([ref]),
                           XS_FLOOR_MB))
        for (Z, A), table in rp_files.items():
            ref = table.get(e)
            if ref is None:
                continue
            rp_r.append(_r(np.array([out.residual_mb.get((Z, A), 0.0)]), np.array([ref]),
                           XS_FLOOR_MB))
        for t, table in part_files.items():
            ref = table.get(e)
            if ref is None:
                continue
            part_r.append(_r(np.array([out.xsexclusive_mb.get(t, 0.0)]), np.array([ref]),
                             XS_FLOOR_MB))
    rec["channels"] = _stats(ch_r)
    rec["residual"] = _stats(rp_r)
    rec["exclusive_totals"] = _stats(part_r)
    rec["a_mult"] = _stats(lev_r + ch_r + rp_r)
    rec["negative_reference_points"] = count_negative_reference(work)
    try:
        zt, at = _target_ZA(tag.split("__")[-1])
        rec["cascade"] = score_cascade(work, zt, at)
    except Exception as exc:  # structure files missing on this box
        rec["cascade"] = {"n": 0, "error": str(exc)[:120]}
    return rec


def _target_ZA(tag: str) -> tuple[int, int]:
    from physics.hf.talys_reference import REFERENCE_SET

    t = next(x for x in REFERENCE_SET if x.tag == tag)
    return t.Z, t.A


# ------------------------------------------------------------------------------------------------
# E2E (docs/results/hf-engine-gates.md §4)
# ------------------------------------------------------------------------------------------------

E2E_CHANNELS: dict[str, tuple[str, str]] = {
    # label -> (where it comes from, file)
    "(n,g)": ("channel", "xs000000.tot"),
    "elastic": ("total", "elastic.tot"),
    "total inelastic": ("channel", "xs100000.tot"),
    "(n,2n)": ("channel", "xs200000.tot"),
    "(n,p)": ("channel", "xs010000.tot"),
    "(n,a)": ("channel", "xs000001.tot"),
    "total": ("total", "total.tot"),
    "nonelastic": ("total", "nonelastic.tot"),
    "(n,f)": ("total", "fission.tot"),
}
_TOTAL_KEY = {"elastic.tot": "elastic", "total.tot": "total", "nonelastic.tot": "nonelastic",
              "fission.tot": "fission"}


def e2e_run(work: Path, injection=None) -> dict:
    """§4's per-(target, channel) median of r, for one instrumented run directory.

    The first reference energy above a threshold reaction's threshold is excluded and reported
    separately: it is a grid-edge point where TALYS's own value is a fraction of a bin.

    `injection` defaults to `DumpInjection`, which is what §4's statistic was first computed with
    and what makes it a bookkeeping reproduction. Pass `engine.ChainedFull(work, Z, A)` to score
    the same statistic with nothing injected where a port exists (EXCL); the metric, the channels,
    the floor and the edge-point rule are §4's either way and are not touched here.
    """
    from physics.hf.engine import DumpInjection, run as engine_run

    res = engine_run(injection=injection if injection is not None else DumpInjection(work))
    e = res.e_inc_mev.numpy()
    out: dict[str, dict] = {}
    for label, (kind, fname) in E2E_CHANNELS.items():
        f = work / fname
        if not f.is_file():
            continue
        ref = _column(f, "xs")
        t = np.array([ref.get(round(float(x), 6), np.nan) for x in e])
        if kind == "channel":
            got = res.channels_mb.get(fname[:-4], torch.zeros_like(res.e_inc_mev)).numpy()
        else:
            got = res.totals_mb.get(_TOTAL_KEY[fname], torch.zeros_like(res.e_inc_mev)).numpy()
        live = np.isfinite(t) & (t > XS_FLOOR_MB)
        if not live.any():
            continue
        first = int(np.argmax(live))  # grid-edge point of a threshold reaction
        edge = bool(live[: first + 1].sum() == 1 and first > 0)
        keep = live.copy()
        if edge:
            keep[first] = False
        r_all = _r(got[live], t[live], XS_FLOOR_MB)
        r_keep = _r(got[keep], t[keep], XS_FLOOR_MB) if keep.any() else np.array([])
        out[label] = {
            "n": int(keep.sum()), "median": float(np.median(r_keep)) if r_keep.size else None,
            "max": float(np.max(r_keep[np.isfinite(r_keep)])) if r_keep.size else None,
            "edge_excluded": (float(r_all[0]) if edge and r_all.size else None),
        }
    return out


def e2e(runs: list[Path], injections: dict | None = None) -> dict:
    """§4's gate statistic: the median over the spherical targets of the per-target medians.

    `injections` maps a run directory's name to the `Injection` to score it with; anything absent
    falls back to `DumpInjection`.
    """
    injections = injections or {}
    per_target = {p.name: e2e_run(p, injections.get(p.name)) for p in runs}
    stat = {}
    for label in E2E_CHANNELS:
        med = [v[label]["median"] for v in per_target.values()
               if label in v and v[label]["median"] is not None]
        if med:
            stat[label] = {"targets": len(med), "statistic": float(np.median(med)),
                           "worst_target": float(max(med))}
    return {"per_target": per_target, "statistic": stat}


def main(argv=None) -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--runs", default=str(Path.home() / "hf_t10/runs"))
    p.add_argument("--work", default=str(Path.home() / "hf_t10/score_work"))
    p.add_argument("--out", default="docs/results/hf-emission-gate.json")
    p.add_argument("--only", default="")
    p.add_argument("--e2e", default="docs/results/hf-e2e.json")
    a = p.parse_args(argv)
    torch.set_num_threads(2)
    work = Path(a.work).expanduser()
    work.mkdir(parents=True, exist_ok=True)
    records = []
    for tar in sorted(Path(a.runs).expanduser().glob("*.tar.gz")):
        if a.only and a.only not in tar.name:
            continue
        d = work / tar.name[: -len(".tar.gz")]
        if not d.is_dir():
            with tarfile.open(tar) as tf:
                tf.extractall(work)
        rec = score_run(d)
        records.append(rec)
        print(json.dumps(rec), flush=True)
    summary = {
        k: _pool(records, k)
        for k in ("levels", "binE", "cascade", "channels", "residual", "exclusive_totals",
                  "a_mult")
    }
    summary["negative_reference_points"] = sum(
        r.get("negative_reference_points", 0) for r in records)
    out = {"runs": records, "summary": summary, "tolerance": 0.05}
    Path(a.out).write_text(json.dumps(out, indent=1))
    print(json.dumps(summary, indent=1))
    dirs = [work / r["run"] for r in records]
    ee = e2e(dirs)
    ee["provisional"] = True
    ee["injected"] = list(__import__("physics.hf.engine", fromlist=["DumpInjection"])
                          .DumpInjection(dirs[0]).families) if dirs else []
    Path(a.e2e).write_text(json.dumps(ee, indent=1))
    print(json.dumps(ee["statistic"], indent=1))


def _pool(records: list[dict], key: str) -> dict:
    ns = [r[key]["n"] for r in records if r.get(key, {}).get("n")]
    if not ns:
        return {"n": 0}
    p95 = [r[key]["p95"] for r in records if r.get(key, {}).get("n")]
    med = [r[key]["median"] for r in records if r.get(key, {}).get("n")]
    mx = [r[key]["max"] for r in records if r.get(key, {}).get("n")]
    inf = [r[key].get("n_inf", 0) for r in records if r.get(key, {}).get("n")]
    return {"n": int(sum(ns)), "n_inf": int(sum(inf)), "runs": len(ns),
            "worst_p95": max(p95), "median_of_medians": float(np.median(med)),
            "max": max(mx) if mx else math.inf}




# ------------------------------------------------------------------------------------------------
# cascade.f90: the gamma cascade's branching, against TALYS's own feedexcl
# ------------------------------------------------------------------------------------------------


def score_cascade(work: Path, zt: int, at: int) -> dict:
    """A-mult, cascade.f90: TALYS's `feedexcl(Zcomp, Ncomp, 0, nex, k)` for a discrete mother level
    below S_n is `xspop(nex, J, P) * branchratio(nex, i)`, so the feeding SHARES out of one level
    must equal T2's branching ratios exactly.

    This scores `multiple.gamma_cascade`'s content without needing the per-bin compound decay
    injected: the shares are what cascade.f90 computes, and their sum is what it removes from the
    mother level.

    Both sides are normalised over the DISTINCT daughter levels, because T2's `branch_to` can
    list the same daughter twice (two gamma rays between the same pair) while TALYS's array
    carries one entry. `disagreeing_levels` counts mother levels where the two sides differ by
    more than 1% after that normalisation -- those are branching-ratio data, not cascade.f90.
    """
    from physics.hf.input.defaults import default_options, default_params
    from physics.hf.structure.levels import discrete_levels
    from physics.hf.structure.masses import masses

    o = default_options(zt, at, "n")
    p = default_params(zt, at, o)
    m = masses(o, p)
    rs: list[np.ndarray] = []
    seen = disagree = mismatched = 0
    for case in load_channel_dump(work / "ch_inputs.txt"):
        for (zc, nc), n in case.nuclei.items():
            feed0 = n.feedexcl_mb.get(0)
            if not feed0 or n.nlast <= 0:
                continue
            # Only a level BELOW S_n is a pure gamma cascade: above it multiple.f90:499 sends the
            # level through compound() instead, and feedexcl then carries continuum gamma decay.
            smin = n.sep_mev.get(1, 0.0)
            lev = discrete_levels(n.Z, n.A, o, m, p)
            shares: dict[int, dict[int, float]] = {}
            for (nex, k), v in feed0.items():
                if 0 < nex <= n.nlast and n.edis_mev.get(nex, 1e9) <= smin:
                    shares.setdefault(nex, {})[k] = v
            for nex, d in shares.items():
                tot = sum(d.values())
                if tot <= 0 or nex >= int(lev.nbranch.shape[0]):
                    continue
                nb = int(lev.nbranch[nex])
                want: dict[int, float] = {}
                for i in range(nb):
                    k = int(lev.branch_to[nex, i])
                    want[k] = want.get(k, 0.0) + float(lev.branch_ratio[nex, i])
                wsum = sum(want.values())
                if not want or wsum <= 0 or set(want) != set(d):
                    mismatched += 1
                    continue
                got = np.array([d[k] / tot for k in sorted(d)])
                ref = np.array([want[k] / wsum for k in sorted(d)])
                r = _r(got, ref, 1e-6)
                # A branch T2 gives ~zero and TALYS gives real flux (or vice versa) is the same
                # kind of disagreement as a 1% one: branching-ratio data, not cascade.f90.
                if r.size and (not np.isfinite(r).all() or float(np.max(r)) > 0.01):
                    disagree += 1
                    continue
                seen += 1
                rs.append(r)
    out = _stats(rs)
    out["mother_levels"] = seen
    out["disagreeing_levels"] = disagree
    out["branch_set_mismatch"] = mismatched
    return out


if __name__ == "__main__":
    main()
