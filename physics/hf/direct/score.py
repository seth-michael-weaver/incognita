"""A-mult gate for the direct/giant-resonance subsystem, and the precision floor it is read at.

    uv run python -m physics.hf.direct.score          # gate -> docs/results/hf-direct-gate.json
    uv run python -m physics.hf.direct.score --floor  # TALYS-sgl vs TALYS-dbl, direct family

What is scored, and what is injected (contract §5). The per-level DWBA cross sections come out
of ECIS, which is T13's port; until it lands they are injected from `directE*.out` and their
own ratio is 1 by construction. Everything around them is ported here and is scored:

    levels   the set of collective levels TALYS ran a DWBA for (directecis.f90:197-202) --
             exact set comparison, not a ratio
    gr       Egrcoll, Ggrcoll, betagr of GMR/GQR/LEOR/HEOR (sumrules.f90) and eoutgr (giant.f90:98)
    totals   xsdirdisctot and xscollconttot -- the split of the injected cross sections at
             `Nlast` (directread.f90:189-201), and xsgrtot (giant.f90:122-131). These are the
             addends binary.f90:214-216 and compnorm.f90:165-169 consume.
    spectra  xsgrstate, xscollcont and their sum xsgr on the emission grid (giant.f90), from
             T12's own `t12spec` runs (`outspectra y`), which are the only ones that write them.

The metric is the contract's `r = |ln(p/t)|` over points above a floor, and the gate bounds its
95th percentile at the A-mult tolerance 0.05, widened by T14's rule to `max(tol, 2 delta)` if
the measured single/double-precision spread of the family demands it.
"""

from __future__ import annotations

import argparse
import json
import tarfile
import time
from pathlib import Path

import numpy as np
import torch

from physics.hf.core.tensors import DTYPE
from physics.hf.direct import dwba as D
from physics.hf.direct import prepare as P
from physics.hf.direct import reference as dref

ROOT = Path(__file__).resolve().parents[3]
OUT_JSON = ROOT / "docs" / "results" / "hf-direct-gate.json"
TOL_AMULT = 0.05  # contract §6
XS_FLOOR_MB = 1.0e-6  # below this TALYS's own es15.6 print carries no information
SPEC_FLOOR_FRAC = 1.0e-6  # spectra points below this fraction of the column peak are ignored

SHAPE = {
    t.tag: t.shape
    for t in __import__("physics.hf.talys_reference", fromlist=["REFERENCE_SET"]).REFERENCE_SET
}


def _r(p, t, floor: float) -> np.ndarray:
    p = np.asarray(p, float).reshape(-1)
    t = np.asarray(t, float).reshape(-1)
    live = (t > floor) & (p > 0)
    return np.abs(np.log(p[live] / t[live]))


def _stats(r: np.ndarray) -> dict:
    if r.size == 0:
        return {"n": 0}
    return {
        "n": int(r.size),
        "median": float(np.median(r)),
        "p95": float(np.percentile(r, 95)),
        "max": float(r.max()),
        "n_inf": int((~np.isfinite(r)).sum()),
    }


def _case_records(target: str, e: float, variant: str, dump) -> list[dict]:
    """Score one (target, incident energy) against one dumped `directE*.out`."""
    cs = P.case(target, e)
    k0 = cs.options.k0
    gr = D.giant_resonance_parameters(cs.struct, cs.params)
    lv = D.direct_levels(cs.struct, cs.eninccm_mev, cs.eoutdis_mev, e, k0)
    xs, xscc, xsgrcoll = P.injected_cross_sections(cs, lv, dump)
    res = D.direct(
        cs.struct,
        gr,
        lv,
        xs,
        xsgrcoll,
        cs.eoutdis_mev,
        cs.eninccm_mev,
        torch.as_tensor(cs.egrid_mev, dtype=DTYPE),
        torch.as_tensor(cs.deltae_mev, dtype=DTYPE),
        cs.grid_mask,
        xscc,
        flaggiant=dump.has_giant,
        elwidth_mev=float(cs.params.at("elwidth")),
    )
    xsdirdisc, disctot, collconttot = res.xsdirdisc_mb, res.xsdirdisctot_mb, res.xscollconttot_mb
    xsgrstate, cc, xsgr, eoutgr = (
        res.xsgrstate_mb,
        res.xscollcont_mb,
        res.xsgr_mb,
        res.eoutgr_mev,
    )
    common = dict(target=target, variant=variant, e=e, shape=SHAPE.get(target, "?"))
    out: list[dict] = []

    # `directout.f90:110` writes a row only where `xsdirdisc /= 0`, so the comparable set is
    # the levels the port gives a non-zero cross section, DWBA and coupled-channels together.
    nz = xsdirdisc.detach().numpy()
    port_set = {int(i) for i in np.nonzero(nz)[0]}
    dwba_set = set(lv.index.tolist())
    dump_set = set(dump.level.tolist())
    out.append(
        dict(
            common,
            kind="levels",
            n_dump=len(dump_set),
            n_port=len(port_set),
            missing=sorted(dump_set - port_set),
            extra=sorted(port_set - dump_set),
            # the part the port decides on its own (directecis.f90), with the coupled-channels
            # levels removed from the reference because their selection is ECIS's, not ours
            dwba_missing=sorted((dump_set - set(int(i) for i in cs.struct.cc_levels)) - dwba_set),
            dwba_extra=sorted({i for i in dwba_set if nz[i] != 0.0} - dump_set),
        )
    )

    if dump.has_giant:
        out.append(
            dict(
                common,
                kind="gr_levels",
                n_dump=int((dump.xsgrcoll_mb != 0).sum()),
                missing=sorted(
                    set(np.nonzero(dump.xsgrcoll_mb)[0].tolist())
                    - set(D.giant_levels(gr, cs.eninccm_mev, k0).tolist())
                ),
                extra=sorted(
                    {
                        int(k)
                        for k in D.giant_levels(gr, cs.eninccm_mev, k0)
                        if dump.xsgrcoll_mb[k] == 0.0
                    }
                ),
            )
        )
        out.append(
            dict(
                common,
                kind="gr",
                r=np.concatenate(
                    [
                        _r(gr.e_mev.detach().numpy(), dump.egrcoll_mev, 0.0),
                        _r(gr.width_mev.detach().numpy(), dump.ggrcoll_mev, 0.0),
                        _r(gr.beta.detach().numpy(), dump.betagr, 0.0),
                        _r(np.abs(eoutgr.detach().numpy()), np.abs(dump.eoutgr_mev), 1e-9),
                    ]
                ).tolist(),
            )
        )
    out.append(
        dict(
            common,
            kind="totals",
            r=np.concatenate(
                [
                    _r([float(disctot)], [dump.xsdirdisctot_mb], XS_FLOOR_MB),
                    _r([float(collconttot)], [dump.xscollconttot_mb], XS_FLOOR_MB),
                    _r(
                        [float(xsgrcoll.sum())] if dump.has_giant else [],
                        [dump.xsgrtot_mb] if dump.has_giant else [],
                        XS_FLOOR_MB,
                    ),
                ]
            ).tolist(),
        )
    )
    if dump.has_spectra:
        sl = slice(cs.ebegin, min(cs.eend, cs.maxen) + 1)
        n = len(dump.spec_eout_mev)
        rs = []
        for k in range(4):
            ref_col = dump.spec_state_mb[k]
            if ref_col.max() <= 0:
                continue
            rs.append(
                _r(xsgrstate[k].detach().numpy()[sl][:n], ref_col, ref_col.max() * SPEC_FLOOR_FRAC)
            )
        for got, want in ((cc, dump.spec_collective_mb), (xsgr, dump.spec_total_mb)):
            w = np.asarray(want)
            if w.max() > 0:
                rs.append(_r(got.detach().numpy()[sl][:n], w, w.max() * SPEC_FLOOR_FRAC))
        out.append(dict(common, kind="spectra", r=np.concatenate(rs).tolist() if rs else []))
    return out


def gate(targets: list[str] | None = None, variants=("default", "wfc_off")) -> dict:
    """Run the gate over T0's archives plus every T12 `t12spec` run available."""
    recs: list[dict] = []
    t0 = time.time()
    tags = targets or sorted({t for t, _ in [(k, 0) for k in SHAPE]})
    for target in tags:
        for variant in variants:
            try:
                energies = dref.energies_with_direct(target, variant)
            except Exception:
                continue
            for e in energies:
                try:
                    dump = dref.dump(target, e, variant)
                except KeyError:
                    continue
                recs.extend(_case_records(target, e, variant, dump))
    for target in dref.t12_available("t12spec"):
        for e in dref.t12_energies(target, "t12spec"):
            dump = dref.t12_dump(target, e, "t12spec")
            recs.extend(_case_records(target, e, "t12spec", dump))
    return {"records": recs, "elapsed_s": round(time.time() - t0, 1)}


def summarise(recs: list[dict]) -> dict:
    kinds = sorted({r["kind"] for r in recs})
    out: dict = {"by_kind": {}, "by_kind_shape": {}, "by_target": {}}
    lev = [r for r in recs if r["kind"] == "levels"]
    grl = [r for r in recs if r["kind"] == "gr_levels"]
    out["levels"] = {
        "n_cases": len(lev),
        "n_exact": sum(1 for r in lev if not r["missing"] and not r["extra"]),
        "n_missing_total": sum(len(r["missing"]) for r in lev),
        "n_extra_total": sum(len(r["extra"]) for r in lev),
        "n_exact_dwba": sum(1 for r in lev if not r["dwba_missing"] and not r["dwba_extra"]),
        "n_dwba_missing_total": sum(len(r["dwba_missing"]) for r in lev),
        "n_dwba_extra_total": sum(len(r["dwba_extra"]) for r in lev),
        "worst": [
            {k: r[k] for k in ("target", "variant", "e", "missing", "extra")}
            for r in lev
            if r["missing"] or r["extra"]
        ][:20],
    }
    out["gr_levels"] = {
        "n_cases": len(grl),
        "n_exact": sum(1 for r in grl if not r["missing"] and not r["extra"]),
        "worst": [
            {k: r[k] for k in ("target", "variant", "e", "missing", "extra")}
            for r in grl
            if r["missing"] or r["extra"]
        ][:20],
    }
    for kind in kinds:
        if kind in ("levels", "gr_levels"):
            continue
        rs = np.concatenate(
            [np.asarray(r["r"]) for r in recs if r["kind"] == kind] or [np.zeros(0)]
        )
        out["by_kind"][kind] = _stats(rs)
        for shape in ("spherical", "deformed", "actinide"):
            sub = [np.asarray(r["r"]) for r in recs if r["kind"] == kind and r["shape"] == shape]
            out["by_kind_shape"][f"{kind}/{shape}"] = _stats(np.concatenate(sub or [np.zeros(0)]))
    for target in sorted({r["target"] for r in recs}):
        sub = [
            np.asarray(r["r"])
            for r in recs
            if r["target"] == target and r["kind"] not in ("levels", "gr_levels")
        ]
        out["by_target"][target] = _stats(np.concatenate(sub or [np.zeros(0)]))
    worst = []
    for r in recs:
        if r["kind"] in ("levels", "gr_levels") or not r.get("r"):
            continue
        worst.append((max(r["r"]), r["target"], r["variant"], r["e"], r["kind"]))
    worst.sort(reverse=True)
    out["worst_cases"] = [
        dict(r=w[0], target=w[1], variant=w[2], e=w[3], kind=w[4]) for w in worst[:15]
    ]
    return out


# --- precision floor for the `direct` family (T14's rule, T14's archives) ---------------------


def _directs_from_archive(tar: Path) -> dict[str, str]:
    out = {}
    with tarfile.open(tar) as tf:
        for m in tf.getmembers():
            if m.isfile() and Path(m.name).name.startswith("directE"):
                f = tf.extractfile(m)
                if f is not None:
                    out[Path(m.name).name] = f.read().decode("utf-8", "replace")
    return out


def floor(sgl_dir: Path, dbl_dir: Path) -> dict:
    """Measure delta for the `direct` family: TALYS-float32 against TALYS-float64.

    `docs/results/hf-sgl-floor.json` records `direct` with `n: 0` because T0's loader produces
    no numeric rows for the family (see `physics.hf.direct.reference`), so T14 had nothing to
    compare. The archives are still on disk, and this reads them with T12's own parser.
    """
    per: dict[str, list] = {"rows": [], "gr": [], "meta": []}
    jobs = []
    for p in sorted(sgl_dir.glob("*.tar.gz")):
        q = dbl_dir / p.name
        if not q.exists() or p.name.startswith("FAILED"):
            continue
        jobs.append(p.name)
        a, b = _directs_from_archive(p), _directs_from_archive(q)
        for name in sorted(set(a) & set(b)):
            e = float(name[7:-4])
            da = dref._from_text(e, a[name])
            db = dref._from_text(e, b[name])
            if list(da.level) == list(db.level):
                per["rows"].append(_r(da.xs_mb, db.xs_mb, XS_FLOOR_MB))
            if da.has_giant and db.has_giant:
                per["gr"].append(
                    np.concatenate(
                        [
                            _r(da.xsgrcoll_mb, db.xsgrcoll_mb, XS_FLOOR_MB),
                            _r(da.egrcoll_mev, db.egrcoll_mev, 0.0),
                            _r(da.ggrcoll_mev, db.ggrcoll_mev, 0.0),
                            _r(da.betagr, db.betagr, 0.0),
                        ]
                    )
                )
            per["meta"].append(
                _r(
                    [da.xsdirdisctot_mb, da.xscollconttot_mb, da.xsgrtot_mb],
                    [db.xsdirdisctot_mb, db.xscollconttot_mb, db.xsgrtot_mb],
                    XS_FLOOR_MB,
                )
            )
    res = {k: _stats(np.concatenate(v or [np.zeros(0)])) for k, v in per.items()}
    allr = np.concatenate([x for v in per.values() for x in v] or [np.zeros(0)])
    res["all"] = _stats(allr)
    res["jobs"] = jobs
    d = res["all"].get("p95", 0.0)
    res["two_delta"] = 2.0 * d
    res["effective_tolerance"] = max(TOL_AMULT, 2.0 * d)
    return res


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--targets", default="")
    ap.add_argument("--variants", default="default,wfc_off")
    ap.add_argument("--floor", action="store_true")
    ap.add_argument(
        "--floor-dirs",
        default=str(Path.home() / "hf_sglfloor/desk_sgl")
        + ","
        + str(Path.home() / "hf_sglfloor/desk_dbl"),
    )
    ap.add_argument("--out", default=str(OUT_JSON))
    a = ap.parse_args(argv)
    doc: dict = {"tolerance": TOL_AMULT, "generated_by": "physics.hf.direct.score"}
    if a.floor:
        s, d = (Path(x).expanduser() for x in a.floor_dirs.split(","))
        doc["floor"] = floor(s, d)
        print(json.dumps(doc["floor"], indent=1))
    else:
        g = gate([t for t in a.targets.split(",") if t] or None, tuple(a.variants.split(",")))
        doc["elapsed_s"] = g["elapsed_s"]
        doc["summary"] = summarise(g["records"])
        doc["n_records"] = len(g["records"])
        print(json.dumps(doc["summary"], indent=1, default=float))
    p = Path(a.out)
    old = json.loads(p.read_text()) if p.exists() else {}
    old.update(doc)
    p.write_text(json.dumps(old, indent=1, default=float) + "\n")
    print(f"-> {p}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
