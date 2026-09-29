"""Parse the A-mpe instrumentation dump and score `preeq.multi` against it.

Task: EXCL3 (physics/hf/CONTRACT.md §7). Acceptance test: A-mpe (§6).

`physics/hf/preeq/talys_instrument/` builds a private TALYS whose `multipreeq2.f90` calls
`mpdump_in` at entry and `mpdump_out` at the point where it is about to set `Dmulti` -- so every
record here is one `(Zcomp, Ncomp, nex)` call with TALYS's own inputs beside its own outputs, and
the gate measures `multipreeq2.f90` alone with nothing else in the loop.

Records that carry no `MPOU` block are calls TALYS abandoned at its own `sumfeed <= 1e-10` cut
(multipreeq2.f90:152); the port must abandon them too, which is checked rather than skipped.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import torch

from physics.hf.core.tensors import DTYPE
from physics.hf.preeq.multi import (
    MpeDaughter,
    MultiPreeqInputs,
    multiple_preequilibrium,
)

NUMJ = 40  # the port's (J, parity) grid, emission.multiple.NUMJ


def _f(x: str) -> float:
    return float(x)


def parse_mp_dump(path: Path) -> list[dict]:
    """Every `multipreeq2` call in one instrumented run, in call order."""
    recs: list[dict] = []
    cur: dict | None = None
    for line in Path(path).read_text().splitlines():
        tag, rest = line[:4], line[5:].split()
        if tag == "MPIN":
            cur = {
                "nin": int(rest[0]), "zcomp": int(rest[1]), "ncomp": int(rest[2]),
                "nex": int(rest[3]), "einc": _f(rest[4]), "exinc": _f(rest[5]),
                "dexinc": _f(rest[6]), "xspopex": _f(rest[7]), "sumfeed": _f(rest[8]),
                "pop": {}, "rnj": {}, "types": {}, "bins": {1: {}, 2: {}},
                "out": None, "mc": {}, "dm": {}, "dd": {},
            }
            recs.append(cur)
        elif cur is None:
            continue
        elif tag == "MPSC":
            cur.update(
                maxpar=int(rest[0]), numparx=int(rest[1]), mpreeqmode=int(rest[2]),
                flaggshell=rest[3] == "T", flag2comp=rest[4] == "T", gp=_f(rest[5]),
                gn=_f(rest[6]), alev=_f(rest[7]), damp=_f(rest[8]), efermi=_f(rest[9]),
                gp0=_f(rest[10]), gn0=_f(rest[11]))
        elif tag == "MPPH":
            cur["pop"][tuple(int(v) for v in rest[:4])] = _f(rest[4])
        elif tag == "MPRJ":
            cur["rnj"][int(rest[0])] = _f(rest[1])
            cur["rnjsum"] = _f(rest[2])
        elif tag == "MPTY":
            cur["types"][int(rest[0])] = {
                "zix": int(rest[1]), "nix": int(rest[2]), "nlast": int(rest[3]),
                "nexmax": int(rest[4]), "maxex": int(rest[5]), "parskip": rest[6] == "T",
                "s": _f(rest[7]), "gp": _f(rest[8]), "gn": _f(rest[9]), "alev": _f(rest[10])}
        elif tag == "MPBN":
            cur["bins"][int(rest[0])][int(rest[1])] = {
                "nen": int(rest[2]), "maxj": int(rest[3]), "ex": _f(rest[4]),
                "dex": _f(rest[5]), "eo": _f(rest[6]), "tswave": _f(rest[7]),
                "damp": _f(rest[8])}
        elif tag == "MPOU":
            cur["out"] = {"summpe": _f(rest[3]), "xspopex": _f(rest[4]),
                          "xsmpe": (_f(rest[5]), _f(rest[6]))}
        elif tag == "MPMC":
            cur["mc"][(int(rest[0]), int(rest[1]))] = _f(rest[2])
        elif tag == "MPDM":
            cur["dm"][tuple(int(v) for v in rest[:4])] = _f(rest[4])
        elif tag == "MPDD":
            cur["dd"][tuple(int(v) for v in rest[:6])] = _f(rest[6])
    return recs


def inputs_from(rec: dict) -> MultiPreeqInputs:
    """`MultiPreeqInputs` built entirely out of one dumped record."""
    t = lambda x: torch.tensor(float(x), dtype=DTYPE)  # noqa: E731
    nb = max(rec["types"][k]["maxex"] for k in (1, 2)) + 1
    daughters = []
    for k in (1, 2):
        ty = rec["types"][k]
        ex = np.zeros(nb)
        dex = np.zeros(nb)
        tsw = np.zeros(nb)
        dmp = np.zeros(nb)
        maxj = [0] * nb
        for nexout, b in rec["bins"][k].items():
            ex[nexout], dex[nexout] = b["ex"], b["dex"]
            tsw[nexout], dmp[nexout] = b["tswave"], b["damp"]
            maxj[nexout] = b["maxj"]
        daughters.append(MpeDaughter(
            type=k, zix=ty["zix"], nix=ty["nix"], nlast=ty["nlast"], nexmax=ty["nexmax"],
            parskip=ty["parskip"], s_mev=ty["s"], gp=t(ty["gp"]), gn=t(ty["gn"]),
            ex_mev=torch.as_tensor(ex, dtype=DTYPE), dex_mev=torch.as_tensor(dex, dtype=DTYPE),
            tswave=torch.as_tensor(tsw, dtype=DTYPE), maxj=tuple(maxj),
            damp=torch.as_tensor(dmp, dtype=DTYPE)))
    p = rec["maxpar"]
    pop = torch.zeros(p + 1, p + 1, p + 1, p + 1, dtype=DTYPE)
    for key, v in rec["pop"].items():
        if max(key) <= p:
            pop[key] = v
    rnj = torch.zeros(NUMJ + 1, dtype=DTYPE)
    for j, v in rec["rnj"].items():
        if j <= NUMJ:
            rnj[j] = v
    return MultiPreeqInputs(
        zcomp=rec["zcomp"], ncomp=rec["ncomp"], nex=rec["nex"], exinc_mev=t(rec["exinc"]),
        dexinc_mev=t(rec["dexinc"]), xspopex_mother_mb=t(rec["xspopex"]), xspopph2_mb=pop,
        gp_comp=t(rec["gp"]), gn_comp=t(rec["gn"]), gp_cn0=t(rec["gp0"]), gn_cn0=t(rec["gn0"]),
        daughters=tuple(daughters), rnj=rnj, rnjsum=t(rec["rnjsum"]), maxpar=p,
        flaggshell=rec["flaggshell"], damp_comp=t(rec["damp"]), efermi_mev=rec["efermi"],
        mpreeqmode=rec["mpreeqmode"], flag2comp=rec["flag2comp"])


def _resid(port: float, ref: float, floor: float) -> float | None:
    d = abs(port - ref)
    scale = max(abs(ref), floor)
    if scale == 0.0:
        return None if d == 0.0 else float("inf")
    return d / scale


class _Acc:
    def __init__(self) -> None:
        self.v: list[float] = []
        self.inf = 0
        self.worst: tuple | None = None

    def add(self, port, ref, floor, where) -> None:
        r = _resid(float(port), float(ref), floor)
        if r is None:
            return
        if not np.isfinite(r):
            self.inf += 1
            return
        self.v.append(r)
        if self.worst is None or r > self.worst[0]:
            self.worst = (r, where, float(port), float(ref))

    def stats(self) -> dict:
        if not self.v:
            return {"n": 0, "p95": 0.0, "median": 0.0, "max": 0.0, "n_inf": self.inf}
        a = np.asarray(self.v)
        return {"n": int(a.size), "p95": float(np.percentile(a, 95)),
                "median": float(np.median(a)), "max": float(a.max()), "n_inf": self.inf,
                "worst": None if self.worst is None else
                {"resid": self.worst[0], "where": str(self.worst[1]),
                 "port": self.worst[2], "talys": self.worst[3]}}


def score_dump(path: Path, floors: dict | None = None) -> dict:
    """Score `multiple_preequilibrium` against every call in one instrumented run.

    Quantities: `Dmulti`, `summpe`, `xsmpe(type, nex)`, `mpecontrib(type, nex, nexout)`, the
    mother's `xspopph2` leftover-flux transfers and the daughters' `xspopph2` additions.
    """
    # `xspopph2` is `real(sgl)` and these two quantities are *differences* of its entries, so
    # their absolute precision is float32 eps times the accumulator (O(1) mb here), not times
    # the difference. 1e-7 mb is that floor; below it a relative statistic measures TALYS's
    # storage rather than the port, and `*_abs_max_mb` reports the unscaled residual instead.
    f = {"term": 1.0e-12, "xsmpe": 1.0e-12, "summpe": 1.0e-12, "dmulti": 1.0e-12,
         "mother_ph": 1.0e-7, "daughter_ph": 1.0e-7}
    f.update(floors or {})
    acc = {k: _Acc() for k in f}
    calls = early = 0
    absmax = {"mother_ph": 0.0, "daughter_ph": 0.0}
    flux = [0.0, 0.0]
    for rec in parse_mp_dump(path):
        calls += 1
        res = multiple_preequilibrium(inputs_from(rec), numj=NUMJ)
        tag = (rec["zcomp"], rec["ncomp"], rec["nex"])
        if rec["out"] is None:  # TALYS's own sumfeed cut: the port must return nothing
            early += 1
            acc["summpe"].add(res.summpe_mb, 0.0, f["summpe"], tag)
            acc["dmulti"].add(res.dmulti, 0.0, f["dmulti"], tag)
            continue
        ref = rec["out"]
        acc["summpe"].add(res.summpe_mb, ref["summpe"], f["summpe"], tag)
        acc["dmulti"].add(res.dmulti, ref["summpe"] / ref["xspopex"], f["dmulti"], tag)
        for k in (1, 2):
            acc["xsmpe"].add(res.sumtype_mb[k - 1], ref["xsmpe"][k - 1], f["xsmpe"], (*tag, k))
        seen = set()
        for (ty, nexout), v in rec["mc"].items():
            seen.add((ty, nexout))
            port = res.term_mb[ty - 1, nexout] if nexout < res.term_mb.shape[1] else 0.0
            acc["term"].add(port, v, f["term"], (*tag, ty, nexout))
        for ty in (1, 2):
            for nexout in range(res.term_mb.shape[1]):
                if (ty, nexout) not in seen:
                    acc["term"].add(res.term_mb[ty - 1, nexout], 0.0, f["term"],
                                    (*tag, ty, nexout))
        dm = res.xspopph2_mother_mb - inputs_from(rec).xspopph2_mb
        keys = set(rec["dm"]) | {
            tuple(i.tolist()) for i in torch.nonzero(dm.abs() > 0)}
        for key in keys:
            ref_v = rec["dm"].get(key, 0.0)
            acc["mother_ph"].add(dm[key], ref_v, f["mother_ph"], (*tag, key))
            absmax["mother_ph"] = max(absmax["mother_ph"], abs(float(dm[key]) - ref_v))
        pk = {(ty, nexout, *rest): float(v[nexout])
              for (ty, *rest), v in res.xspopph2_daughter_mb.items()
              for nexout in range(v.shape[0]) if float(v[nexout]) != 0.0}
        for key in set(pk) | set(rec["dd"]):
            port_v, ref_v = pk.get(key, 0.0), rec["dd"].get(key, 0.0)
            acc["daughter_ph"].add(port_v, ref_v, f["daughter_ph"], (*tag, key))
            absmax["daughter_ph"] = max(absmax["daughter_ph"], abs(port_v - ref_v))
            flux[0] += port_v
            flux[1] += ref_v
    out = {k: a.stats() for k, a in acc.items()}
    for k, v in absmax.items():
        out[k]["abs_max_mb"] = v
    out["daughter_ph"]["total_flux_rel"] = (
        abs(flux[0] - flux[1]) / abs(flux[1]) if flux[1] else 0.0)
    out["calls"] = calls
    out["early_return_calls"] = early
    return out


def score_runs(runs: Path, tags, floors: dict | None = None) -> dict:
    """A-mpe over several instrumented runs: per target, and the pooled worst per quantity."""
    per = {}
    for tag in tags:
        f = Path(runs) / tag / "mp_inputs.txt"
        if f.is_file():
            per[tag] = score_dump(f, floors)
    keys = ("dmulti", "summpe", "xsmpe", "term", "mother_ph", "daughter_ph")
    worst = {
        k: {
            "p95": max((per[t][k]["p95"] for t in per), default=0.0),
            "max": max((per[t][k]["max"] for t in per), default=0.0),
            "n": sum(per[t][k]["n"] for t in per),
            "n_inf": sum(per[t][k]["n_inf"] for t in per),
        }
        for k in keys
    }
    for k in ("mother_ph", "daughter_ph"):
        worst[k]["abs_max_mb"] = max((per[t][k]["abs_max_mb"] for t in per), default=0.0)
    worst["daughter_ph"]["total_flux_rel"] = max(
        (per[t]["daughter_ph"]["total_flux_rel"] for t in per), default=0.0)
    return {
        "targets": sorted(per), "per_target": per, "worst": worst,
        "calls": sum(per[t]["calls"] for t in per),
        "early_return_calls": sum(per[t]["early_return_calls"] for t in per),
    }


def main(argv=None) -> None:
    """uv run python -m physics.hf.preeq.mpe_reference --runs ~/excl3/runs"""
    import argparse
    import json

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--runs", default=str(Path.home() / "excl3/runs"))
    ap.add_argument("--out", default="docs/results/hf-mpe-gate.json")
    ap.add_argument("--tol", type=float, default=2.0e-2)
    a = ap.parse_args(argv)
    torch.set_num_threads(2)
    runs = Path(a.runs).expanduser()
    tags = sorted(d.name for d in runs.iterdir() if (d / "mp_inputs.txt").is_file())
    res = score_runs(runs, tags)
    res["tolerance"] = a.tol
    res["verdict"] = (
        "PASS" if all(v["p95"] <= a.tol and v["n_inf"] == 0 for v in res["worst"].values())
        else "FAIL")
    Path(a.out).write_text(json.dumps(res, indent=1))
    print(res["verdict"], json.dumps(res["worst"], indent=1))


if __name__ == "__main__":
    main()
