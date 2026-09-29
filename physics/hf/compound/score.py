"""Score the ported comptarget against TALYS: gates A-cn1 (wfc_off) and A-cn2 (default).

Two references, both from the instrumented run (compound/cn_reference.py), whose binE*.out files
are verified identical to the standard reference dumps:

1. **binE*.out** (the pre-registered gate reference). It is the post-binary population, i.e.
   compound + direct to discrete levels + pre-equilibrium in the continuum (binary.f90:193-260),
   written before compound elastic is removed from the target state (binary.f90:509). Both
   addends are TALYS's own `xsdirdisc` / `preeqpopex`, taken from the same dump, so what is
   compared is still this module's number; the continuum addend additionally needs the compound
   spin shape `sfactor`, which IS this module's output. The (J, P) cells where TALYS instead
   falls back to the particle-hole spin distribution (`sfactor == 0`, or `xspopex <= popepsA`
   leaving `sfactor` stale) are not gated -- that shape is T8's and T6's, and those cells have
   zero compound population, so they say nothing about T9. They are counted and reported, and
   reference 2 below covers them anyway.
2. **the compound-only xspop** written at the end of comptarget (full double precision, every
   energy, every row). Reported beside the gate as a diagnostic; it isolates this module from
   binary.f90's bookkeeping.

Metric (gates doc §2): r = |ln(p/t)| over points with t >= 1e-6 mb; t below the floor but p above
it counts as r = inf. Statistic: p95 over all points of all spherical reference targets; median
and max beside it.

    python -m physics.hf.compound.score --runs features/hf_compound_reference --out docs/results/hf-compound-gates.json
"""

from __future__ import annotations

import argparse
import io
import json
import re
import tarfile
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import numpy as np
import torch

from physics.hf.compound.prepare import NUMJ, PARTICLES, load_cn_dump
from physics.hf.compound.target import compound_target_inputs

FLOOR_MB = 1.0e-6
SPHERICAL = {"Ca040", "Fe056", "Co059", "Ni058", "Zr090", "Nb093", "Mo098", "Sn120", "I127",
             "Ba138", "Ce140", "Au197", "Pb208", "Bi209"}
MAXJPH = 30  # preeqspindis.f90:48 maxJph: spins that receive pre-equilibrium population
BANDS = ((0.0, 0.1), (0.1, 1.0), (1.0, 5.0), (5.0, 12.0), (12.0, 21.0))


def _extract(tar: Path, dest: Path) -> Path:
    dest.mkdir(parents=True, exist_ok=True)
    with tarfile.open(tar) as tf:
        tf.extractall(dest, filter="data")
    return next(p for p in dest.iterdir() if p.is_dir())


def _preeq_flags(talys_out: Path) -> dict[float, bool]:
    flags, e = {}, None
    for line in talys_out.open(errors="replace"):
        m = re.match(r"\s*#+ RESULTS FOR E=\s*([0-9.Ee+-]+)", line)
        if m:
            e = float(m.group(1))
        elif e is not None and "Preequilibrium (flagpreeq)" in line:
            flags[round(e, 5)] = line.split(":")[-1].strip() == "y"
    return flags


def _read_binE(path: Path) -> dict[str, np.ndarray]:
    """ejectile -> (rows, 2 + 2 (numJ+1)) [bin, Ex, pop, JP columns (J=0: -, +; J=1: -, +; ...)]."""
    out, ej, rows = {}, None, []
    for line in path.open():
        if line.startswith("#"):
            if "ejectile:" in line:
                if ej is not None:
                    out[ej] = np.array(rows)
                ej, rows = line.split(":", 1)[1].strip(), []
            continue
        tok = line.split()
        if tok:
            rows.append([float(v) for v in tok])
    if ej is not None:
        out[ej] = np.array(rows)
    return out


def _read_direct(path: Path) -> list[tuple[int, float]]:
    rows = []
    if not path.exists():
        return rows
    for line in path.open():
        if line.startswith("#") or not line.strip():
            continue
        tok = line.split()
        if not tok[0].isdigit():
            continue  # giant-resonance rows (GMR, GQR, LEOR, HEOR) feed the continuum, not levels
        rows.append((int(tok[0]), float(tok[5])))  # level, cross section [mb] (J/P takes 2 tokens)
    return rows


def _r(p: np.ndarray, t: np.ndarray) -> np.ndarray:
    live = t >= FLOOR_MB
    r = np.full(p.shape, np.nan)
    r[live] = np.abs(np.log(np.maximum(p[live], 1e-300) / t[live]))
    r[(~live) & (p >= FLOOR_MB)] = np.inf
    return r[~np.isnan(r)]


def _preeq_addend(pp: np.ndarray, mask: np.ndarray, p: np.ndarray, c, t: int, r, n: int) -> None:
    """Add binary.f90's continuum pre-equilibrium population to `pp`, and clear `mask` on the
    cells whose addend this module cannot reconstruct.

    binary.f90:225-235. For every continuum bin TALYS builds a spin factor from the *compound*
    population, ``sfactor(J,P) = xspop(J,P) / xspopex``, and with ``pespinmodel 1`` spreads
    ``preeqpopex`` over (J, P) with it -- that part the port reproduces exactly, since the shape
    is its own xspop. Two cells fall outside it:

    * ``sfactor(J,P) == 0`` (binary.f90:234-237): TALYS instead uses the *particle-hole* spin
      distribution ``spindis(sc, J) * pardis``. Those are cells where the compound population is
      zero, so they carry no information about this module, and the shape belongs to T8
      (`preeqspindis.f90`) and T6 (`spincut`/`ignatyuk`). Not gated; counted.
    * ``xspopex <= popepsA`` (binary.f90:231): sfactor is not updated at all and keeps the value
      it had at an earlier incident energy (``strucinitial.f90:484`` zeroes it once per run), so
      the addend is not a function of this energy's dump. Not gated; counted.

    Cells with ``J > maxJph`` get no pre-equilibrium at all and stay gated -- they are pure
    compound and are the strongest rows in the comparison.
    """
    popeps_a = c.popeps_mb / max(5 * r.maxex, 1)  # binary.f90:228
    for nex in range(r.nlast + 1, n):
        e_pe = c.preeqpopex_mb.get((t, nex), 0.0)
        if e_pe == 0.0:
            continue
        tot = p[nex].sum()  # xspopex: continuum bins get no direct contribution
        if tot > popeps_a:
            sf = p[nex, :MAXJPH + 1] / tot
            pp[nex, :MAXJPH + 1] += sf * e_pe
            mask[nex, :MAXJPH + 1] &= sf > 0.0
        else:
            mask[nex, :MAXJPH + 1] = False


def score_run(tar: Path, work: Path) -> dict:
    d = _extract(tar, work / tar.stem.replace(".tar", ""))
    variant, target = d.name.split("__")
    cases = load_cn_dump(d / "cn_inputs.txt")
    pre = _preeq_flags(d / "talys.out")
    recs = []
    for c in cases:
        e = c.e_inc_mev
        t0 = time.time()
        bp = compound_target_inputs(c)
        dt = time.time() - t0
        pop = bp.pop_mb[0].numpy()
        tag = f"{e:08.3f}".replace(" ", "0")
        bin_path = d / f"binE{tag}.out"
        ref_bin = _read_binE(bin_path) if bin_path.exists() else {}
        preeq_on = pre.get(round(e, 5), False)
        for t, r in c.residuals.items():
            name = PARTICLES[t]
            n = r.maxex + 1
            p = pop[t, :n]
            # (a) compound-only xspop, every row
            ref = c.ref_pop_mb.get(t, np.zeros_like(p))
            rr = _r(p.reshape(-1), ref.reshape(-1))
            recs.append(dict(kind="xspop", variant=variant, target=target, e=e, type=name, r=rr.tolist()))
            # (b) binE gate: binE = compound + xsdirdisc (direct + pre-equilibrium to discrete
            # levels, binary.f90:196-206) + pre-equilibrium in the continuum, spread over (J, P)
            # by the COMPOUND spin shape sfactor (binary.f90:225-235, pespinmodel 1, the default
            # for k0 <= 1). Both addends are TALYS's own numbers from the instrumented dump; only
            # the spin shape is the port's. `mask` drops the (J, P) cells where that
            # reconstruction is not defined -- see _preeq_addend.
            if name not in ref_bin:
                continue
            tb = ref_bin[name]
            jp = tb[:, 3:3 + 2 * (NUMJ + 1)].reshape(-1, NUMJ + 1, 2)[:n].copy()
            pp = p.copy()
            have_xsdd = c.popeps_mb > 0  # dumps before the XSDD/PEPX extension lack them
            mask = np.ones(pp.shape, bool)
            if have_xsdd:
                for (tt, lev), xs in c.xsdirdisc_mb.items():
                    if tt == t and lev <= r.nlast:
                        pp[lev, r.jdis2[lev] // 2, 0 if r.parlev[lev] == -1 else 1] += xs
                if c.flagpreeq:
                    _preeq_addend(pp, mask, p, c, t, r, n)
            else:
                direct = dict(_read_direct(d / f"directE{tag}.out"))
                if t == c.k0:
                    for lev, xs in direct.items():
                        if lev <= r.nlast:
                            pp[lev, r.jdis2[lev] // 2, 0 if r.parlev[lev] == -1 else 1] += xs
                if preeq_on:
                    mask[r.nlast + 1:] = False
            live = jp >= FLOOR_MB
            rb = _r(pp[mask].reshape(-1), jp[mask].reshape(-1))
            recs.append(dict(kind="binE", variant=variant, target=target, e=e, type=name, r=rb.tolist(),
                             ungated_cells=int((~mask & live).sum()), gated_cells=int((mask & live).sum()),
                             seconds=dt))
    return {"variant": variant, "target": target, "records": recs}


def summarise(records: list[dict], kind: str, variant: str, spherical_only: bool = True) -> dict:
    sel = [x for x in records if x["kind"] == kind and x["variant"] == variant
           and (not spherical_only or x["target"] in SPHERICAL)]
    allr = np.concatenate([np.asarray(x["r"]) for x in sel]) if sel else np.zeros(0)

    def stats(a):
        a = np.asarray(a)
        if a.size == 0:
            return {"n": 0}
        fin = a[np.isfinite(a)]
        return {"n": int(a.size), "n_inf": int((~np.isfinite(a)).sum()),
                "p95": float(np.percentile(a, 95)) if np.isfinite(np.percentile(a, 95)) else float("inf"),
                "median": float(np.median(a)), "max": float(fin.max()) if fin.size else float("inf")}

    out = {"all": stats(allr), "by_type": {}, "by_band": {}, "by_target": {}}
    for t in PARTICLES:
        v = [np.asarray(x["r"]) for x in sel if x["type"] == t]
        if v:
            out["by_type"][t] = stats(np.concatenate(v))
    for lo, hi in BANDS:
        v = [np.asarray(x["r"]) for x in sel if lo <= x["e"] < hi]
        if v:
            out["by_band"][f"{lo}-{hi} MeV"] = stats(np.concatenate(v))
    for tg in sorted({x["target"] for x in sel}):
        out["by_target"][tg] = stats(np.concatenate([np.asarray(x["r"]) for x in sel if x["target"] == tg]))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", default="features/hf_compound_reference")
    ap.add_argument("--work", default=str(Path.home() / "t9cn" / "score_work"))
    ap.add_argument("--out", default="docs/results/hf-compound-gates.json")
    ap.add_argument("--workers", type=int, default=1,
                    help="score this many tarballs at once; each still runs on 2 torch threads. "
                         "GOE (widthmode 3) is ~200x Moldauer, so its nine targets want more "
                         "than one process.")
    a = ap.parse_args(argv)
    torch.set_num_threads(2)
    records = []
    tars = [t for t in sorted(Path(a.runs).glob("*.tar.gz")) if not t.name.startswith("multi")]
    if a.workers > 1:
        with ProcessPoolExecutor(a.workers) as ex:
            futs = {ex.submit(score_run, t, Path(a.work) / t.stem): t for t in tars}
            for f in as_completed(futs):
                records += f.result()["records"]
                print(futs[f].name, "scored", flush=True)
    else:
        for tar in tars:
            res = score_run(tar, Path(a.work))
            records += res["records"]
            print(tar.name, "scored", flush=True)
    result = {}
    variants = {x["variant"] for x in records}
    gates = [(v, g) for v, g in (("wfc_off", "A-cn1"), ("default", "A-cn2"),
                                 ("hrtw", "A-cn2-hrtw"), ("goe", "A-cn2-goe")) if v in variants]
    for kind in ("binE", "xspop"):
        for variant, gate in gates:
            s = summarise(records, kind, variant)
            tol = 0.01 if gate == "A-cn1" else 0.02
            s["gate"], s["tolerance_p95"] = gate, tol
            s["pass"] = bool(s["all"].get("n", 0) and s["all"]["p95"] <= tol)
            result[f"{gate}:{kind}"] = s
    worst = sorted(
        ((float(np.max(x["r"])) if len(x["r"]) else 0.0, x["kind"], x["variant"], x["target"], x["e"], x["type"])
         for x in records), reverse=True)[:25]
    result["worst"] = worst
    result["runtime_s_per_case"] = float(np.mean([x["seconds"] for x in records if "seconds" in x])) if records else None
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(json.dumps(result, indent=1))
    print(json.dumps({k: (v["all"], v.get("pass")) for k, v in result.items() if ":" in k}, indent=1))


def score_multi_run(tar: Path, work: Path) -> dict:
    """A-mult diagnostic for compound.f90: the daughter increments of every mother bin against
    TALYS's own (the DPOP rows of cn_multi.txt), inputs injected.

    This is the continuum half of T9. The pre-registered A-mult gate (contract §6) is on exclusive
    channels and residual production, which is T10's `emission`; what is scored here is the one
    routine T9 owns inside it, so it is reported as a component diagnostic at the same 5%.
    """
    from physics.hf.compound.continuum import compound_decay, load_cn_multi_dump

    d = _extract(tar, work / tar.stem.replace(".tar", ""))
    variant, target = d.name.split("__")
    recs = []
    for mi in load_cn_multi_dump(d / "cn_multi.txt"):
        t0 = time.time()
        f = compound_decay(mi)
        dt = time.time() - t0
        for t, got in f.dpop_mb.items():
            ref = mi.ref_dpop_mb.get(t)
            if ref is None:
                ref = np.zeros(tuple(got.shape))
            r = _r(got.numpy().reshape(-1), ref.reshape(-1))
            recs.append(dict(kind="dpop", variant=variant, target=target, e=mi.e_inc_mev,
                             type=PARTICLES[t], nex=mi.nex, r=r.tolist(), seconds=dt))
        # denomhf is dumped per (J2, parity) and is the single number the whole block divides by
        ref_d = np.array([mi.denomhf[k] for k in sorted(mi.denomhf)])
        got_d = np.array([float(f.denom[k]) for k in sorted(mi.denomhf) if k in f.denom])
        if ref_d.size and got_d.size == ref_d.size:
            recs.append(dict(kind="denomhf", variant=variant, target=target, e=mi.e_inc_mev,
                             type="all", nex=mi.nex, r=_r(got_d, ref_d).tolist()))
    return {"variant": variant, "target": target, "records": recs}


def main_multi(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", default="features/hf_compound_reference")
    ap.add_argument("--work", default=str(Path.home() / "t9cn" / "score_work"))
    ap.add_argument("--out", default="docs/results/hf-compound-multi.json")
    a = ap.parse_args(argv)
    torch.set_num_threads(2)
    records = []
    for tar in sorted(Path(a.runs).glob("multi*.tar.gz")):
        records += score_multi_run(tar, Path(a.work))["records"]
        print(tar.name, "scored", flush=True)
    result = {}
    for kind in ("dpop", "denomhf"):
        sel = [x for x in records if x["kind"] == kind]
        allr = np.concatenate([np.asarray(x["r"]) for x in sel]) if sel else np.zeros(0)
        stats = {"n": int(allr.size)}
        if allr.size:
            fin = allr[np.isfinite(allr)]
            stats.update(n_inf=int((~np.isfinite(allr)).sum()),
                         p95=float(np.percentile(allr, 95)),
                         median=float(np.median(allr)),
                         max=float(fin.max()) if fin.size else float("inf"))
        by_type = {}
        for t in PARTICLES:
            v = [np.asarray(x["r"]) for x in sel if x["type"] == t]
            if v:
                c = np.concatenate(v)
                by_type[t] = {"n": int(c.size), "p95": float(np.percentile(c, 95)),
                              "median": float(np.median(c)), "max": float(c[np.isfinite(c)].max())
                              if np.isfinite(c).any() else float("inf")}
        result[kind] = {"all": stats, "by_type": by_type, "tolerance_p95": 0.05,
                        "pass": bool(allr.size and np.percentile(allr, 95) <= 0.05)}
    result["runtime_s_per_mother_bin"] = float(np.mean(
        [x["seconds"] for x in records if "seconds" in x])) if records else None
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(json.dumps(result, indent=1))
    print(json.dumps({k: v for k, v in result.items() if k in ("dpop", "denomhf")},
                     indent=1)[:1200])


if __name__ == "__main__":
    import sys as _sys
    if "--multi" in _sys.argv:
        _sys.argv.remove("--multi")
        main_multi()
    else:
        main()
