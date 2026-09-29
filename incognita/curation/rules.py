"""Curation rule v2, passes A and B and the ladder (docs/release/CURATION_RULE_v2.md §1-3).

Everything here is EXFOR against EXFOR (plus RIPL D0 and physics bounds). No evaluated-library value is read.
"""
from __future__ import annotations

import re
from collections import defaultdict

import numpy as np

from . import exfor_text, inputs
from .schema import DATA_DOWN, EXCLUDE_RULES, RECORD_DOWN

X15, X2, X3, X5 = (float(np.log10(v)) for v in (1.5, 2.0, 3.0, 5.0))
NOT_COMPARABLE = ("spa", "fis", "raw")
KT_LO, KT_HI, F_MIN, GAP, RATIO = 2e4, 4e4, 0.8, 3.0, 1.5
DUP_EXACT, DUP_SD = 3e-5, 0.004


def comparable(kind: str) -> bool:
    return not any(t in kind.split("/") for t in NOT_COMPARABLE)


def ri_kind(kind: str) -> bool:
    return kind.split("/")[0] == "ri"


class Engine:
    def __init__(self, cells, sid: dict[str, int], twins, findings: list[dict]):
        self.sid = sid
        self.findings = findings
        d0 = inputs.ripl_d0()
        recs = cells.to_dicts()
        for i, r in enumerate(recs):
            r["i"] = i
            r["series"] = sid.get(r["dataset_key"], -hash(r["entry"]) % 10**9 - 10**9)
            r["kind0"] = r["kind"].split("/")[0]
            z, a = r["target_z"], r["target_a"]
            if z and a:
                es, src = inputs.e_stat(int(z), int(a), d0)
            else:
                es, src = 1e5, "no Z/A"
            r["e_stat"], r["e_stat_src"] = es, src
            lo = 10 ** ((r["bin"] - 100) / 10)
            thermal = r["e_lo_ev"] >= 0.02 and r["e_hi_ev"] <= 0.03
            r["bin_lo"], r["bin_hi"] = lo, 10 ** ((r["bin"] - 99) / 10)
            r["in_region"] = (r["kind0"] != "sig") or thermal or lo >= es
            r["cmp"] = comparable(r["kind"])
            r["fired"], r["ev"] = set(), {}
        self.recs = recs
        self.by_ds = defaultdict(list)
        for r in recs:
            self.by_ds[r["dataset_key"]].append(r)
        self.twins = {t["superseded"]: t for t in twins.iter_rows(named=True)}
        self.renorm: dict[str, dict] = {}
        self.status_cache: dict[str, set[str]] = {}
        self.dup_cache: dict[tuple[str, str], bool] = {}
        self.dup_pairs: set[tuple[str, str]] = set()

    # ------------------------------------------------------------------ pass A
    def pass_a(self) -> None:
        for r in self.recs:
            k = r["dataset_key"]
            if k in self.twins:
                r["fired"].add("R3")
                r["ev"]["R3"] = self.twins[k]
            if r["cmp"] and r["kind0"] in ("sig", "av") and r["target_a"]:   # the bound is at the incident energy
                e_mev = np.sqrt(max(r["e_lo_ev"], 1e-5) * max(r["e_hi_ev"], 1e-5)) / 1e6
                lim = np.pi * (1.25 * r["target_a"] ** (1 / 3) + 4.55 / np.sqrt(e_mev)) ** 2 / 100.0
                r["ev"]["r7_limit_b"] = float(lim)
                if r["mean_b"] > lim:
                    r["fired"].add("R7")
        for f in self.findings:
            key = f"{f['entry']}/{f['subentry']}/{f.get('pointer') or ''}"
            cells = self.by_ds.get(key, [])
            if f["rule"] == "R4":
                self.renorm[key] = f
                for r in cells:
                    r["x"] += np.log10(f["renorm"]["factor"])
                    r["ev"]["renorm_factor"] = f["renorm"]["factor"]
                continue
            sc = f["scope"]
            for r in cells:
                if sc["kind"] == "points":
                    if not any(r["e_lo_ev"] * 0.9999 <= p["e_ev"] <= r["e_hi_ev"] * 1.0001 for p in sc["points"]):
                        continue
                elif sc["kind"] == "energy":
                    if r["e_lo_ev"] < sc["e_min_ev"]:
                        continue
                if f["rule"] == "R8" and not r["bin_hi"] > 3e6:
                    continue          # G4: R8 covers the cells whose 0.1-dex bin extends above 3 MeV
                r["fired"].add(f["rule"])
                r["ev"].setdefault("record_findings", []).append(f["id"])
        # reference pool: not excluded in pass A, not derived
        for r in self.recs:
            r["pool"] = r["gs"] and not (r["fired"] & {"R1", "R2x", "R3", "R7"}) and not r["derived"]
        self.cell_ix = defaultdict(list)       # (nuclide, kind, bin) -> pool cells
        self.bin_kind_ix = defaultdict(list)   # (kind, bin) -> pool cells
        self.elem_ix = defaultdict(list)       # (Z, kind, bin) -> pool cells
        self.ds_vals = defaultdict(dict)       # dataset -> {(kind, bin): x}
        for r in self.recs:
            self.ds_vals[r["dataset_key"]][(r["nuclide"], r["kind"], r["bin"])] = r["x"]
            if r["pool"] and r["cmp"] and r["in_region"]:
                self.cell_ix[(r["nuclide"], r["kind"], r["bin"])].append(r)
                self.bin_kind_ix[(r["kind"], r["bin"])].append(r)
                if r["target_z"]:
                    self.elem_ix[(r["target_z"], r["kind"], r["bin"])].append(r)

    # ------------------------------------------------------------------ R3d
    def _dup(self, d: dict, q: dict) -> bool:
        """q is a copy of datum d (exact value here, or a constant ratio over >= 2 shared cells)."""
        if abs(q["x"] - d["x"]) < DUP_EXACT:
            return True
        _cache = self.dup_cache
        key = (d["dataset_key"], q["dataset_key"])
        if key not in _cache:
            A, B = self.ds_vals[d["dataset_key"]], self.ds_vals[q["dataset_key"]]
            com = [c for c in A if c in B]
            dup = False
            if len(com) >= 2:
                lr = np.array([A[c] - B[c] for c in com])
                dup = lr.std() < DUP_SD and 10 ** abs(lr.mean()) <= 1.25
            _cache[key] = dup
        return _cache[key]

    def refs(self, r, bins, *, x=None):
        x = r["x"] if x is None else x
        out, dropped = defaultdict(list), []
        for b in bins:
            for q in self.cell_ix[(r["nuclide"], r["kind"], b)]:
                if q["series"] == r["series"] or q["entry"] == r["entry"]:
                    continue
                if self._dup(r, q):
                    dropped.append(q["dataset_key"])
                    self.dup_pairs.add(tuple(sorted((r["dataset_key"], q["dataset_key"]))))
                    continue
                out[q["series"]].append(q["x"])
        return {s: float(np.mean(v)) for s, v in out.items()}, sorted(set(dropped))

    def offset(self, r, widen=True):
        ref, dup = self.refs(r, [r["bin"]])
        wid = False
        if widen and len(ref) < 2:
            ref, dup2 = self.refs(r, [r["bin"] - 1, r["bin"], r["bin"] + 1])
            dup = sorted(set(dup) | set(dup2))
            wid = True
        if not ref:
            return dict(n_ref=0, widened=wid, dup_dropped=dup)
        v = np.array(list(ref.values()))
        return dict(d=float(r["x"] - np.median(v)), n_ref=len(v), spread=float(v.max() - v.min()), widened=wid,
                    ref_dex=[round(float(u - r["x"]), 3) for u in v], ref_series=sorted(ref), dup_dropped=dup)

    # ------------------------------------------------------------------ pass B
    def pass_b(self) -> None:
        s_cells = defaultdict(list)
        for r in self.recs:
            if r["cmp"] and r["in_region"] and r["pool"]:
                s_cells[r["series"]].append(r)
        s_off: dict[int, list] = {}

        def series_offsets(s):
            if s not in s_off:
                out = []
                for q in s_cells[s]:
                    o = self.offset(q, widen=False)
                    if o["n_ref"] >= 1:
                        out.append((q["i"], o["d"], o["ref_series"]))
                s_off[s] = out
            return s_off[s]

        for r in self.recs:
            if r["fired"] & {"R1", "R2x", "R3", "R7"}:
                continue                              # already excluded in pass A
            if not r["gs"]:
                r["ev"]["untested"] = "partial or isomeric-state quantity"
                continue
            if not (r["cmp"] and r["in_region"]):
                r["ev"]["untested"] = "kind not comparable" if not r["cmp"] else f"below statistical region ({r['e_stat']:.3g} eV, D0 {r['e_stat_src']})"
                continue
            ev, sx = r["ev"], r["sig_x"]
            o = self.offset(r)
            ev["r5"] = {k: v for k, v in o.items()}
            if o["dup_dropped"]:
                r["fired"].add("R3d")
            if o["n_ref"] >= 2:
                dd = -np.array(o["ref_dex"])
                if (np.all(dd > X2) or np.all(dd < -X2)) and abs(o["d"]) > 2 * sx:
                    r["fired"].add("R5x" if abs(o["d"]) > X3 and (o["n_ref"] >= 3 or o["spread"] <= X15) else "R5d")
            if o["n_ref"] >= 1:
                d0 = o["d"]
                others = [z for z in series_offsets(r["series"]) if z[0] != r["i"]]
                if others:
                    ds_ = np.array([z[1] for z in others])
                    same = [z for z in others if np.sign(z[1]) == np.sign(d0) and abs(z[1]) > X2]
                    nser = len({s for z in same for s in z[2]})
                    med = float(np.median(ds_))
                    ev["r6"] = dict(n_other=len(others), n_same=len(same), median=round(med, 3), ref_series=nser)
                    if len(same) >= 3 and abs(med - d0) <= X15 and nser >= 2:
                        if abs(d0) > X3 and abs(d0) > 2 * sx:
                            r["fired"].add("R6x")
                        elif abs(d0) > X2:
                            r["fired"].add("R6d")
            if o["n_ref"] <= 1:
                self._r10(r, o)
            if r["e_lo_ev"] >= 1.2e7 and r["target_a"]:
                self._r9(r)
        self._r11()

    def _r9(self, r) -> None:
        a = r["target_a"]
        per = defaultdict(list)
        for b in (r["bin"] - 1, r["bin"], r["bin"] + 1):
            for q in self.bin_kind_ix[(r["kind"], b)]:
                if q["nuclide"] != r["nuclide"] and q["series"] != r["series"] and q["target_a"] and abs(q["target_a"] - a) <= 30:
                    per[q["nuclide"]].append(q["x"])
        if len(per) >= 5:
            m9 = float(np.median([np.median(v) for v in per.values()]))
            r["ev"]["r9"] = dict(n_nuclides=len(per), d=round(r["x"] - m9, 3))
            if abs(r["x"] - m9) > X5:
                r["fired"].add("R9")

    def _r10(self, r, o) -> None:
        if r["kind0"] != "sig" or not (1e4 <= r["bin_lo"] < 1.2e7) or not r["target_z"]:
            return
        n = r["n_neut"]
        if n is None or inputs.near_magic(n):
            return
        per = defaultdict(list)
        for b in (r["bin"] - 1, r["bin"], r["bin"] + 1):
            for q in self.elem_ix[(r["target_z"], r["kind"], b)]:
                dn = q["n_neut"] - n
                if dn == 0 or abs(dn) > 4 or dn % 2 or inputs.near_magic(q["n_neut"]):
                    continue
                if q["series"] == r["series"] or q["entry"] == r["entry"]:
                    continue
                per[q["nuclide"]].append(q["x"])
        if len(per) < 2:
            return
        meds = {k: float(np.median(v)) for k, v in per.items()}
        m = np.array(list(meds.values()))
        ev = dict(n_nuclides=len(meds), nuclide_medians_dex={k: round(v - r["x"], 3) for k, v in meds.items()},
                  spread=round(float(m.max() - m.min()), 3))
        r["ev"]["r10"] = ev
        if m.max() - m.min() > X3:
            ev["note"] = "neighbours disagree (> x3): no test"
            return
        d10 = float(r["x"] - np.median(m))
        ev["d"] = round(d10, 3)
        if abs(d10) > X5 and abs(d10) > 2 * r["sig_x"]:
            one = o.get("n_ref") == 1 and np.sign(-o["ref_dex"][0]) == np.sign(d10) and abs(o["ref_dex"][0]) > X3
            r["fired"].add("R10x" if one else "R10d")

    # ------------------------------------------------------------------ R11 (MACSCHECK, adopted)
    @staticmethod
    def macs_over(e_lo, e_hi, e_mid, sig, kt):
        o = np.argsort(e_mid)
        e_lo, e_hi, e_mid, sig = e_lo[o], e_hi[o], e_mid[o], sig[o]
        cut = np.where(e_mid[1:] / e_mid[:-1] > GAP)[0] + 1
        num = den = 0.0
        for s in np.split(np.arange(len(e_mid)), cut):
            lo, hi = min(e_lo[s[0]], e_mid[s[0]]), max(e_hi[s[-1]], e_mid[s[-1]])
            g = np.geomspace(lo, hi, 600)
            ls = np.interp(np.log(g), np.log(e_mid[s]), np.log(sig[s]))
            w = g * np.exp(-g / kt) * g
            num += np.trapezoid(np.exp(ls) * w, np.log(g))
            den += np.trapezoid(w, np.log(g))
        return 2 / np.sqrt(np.pi) * num / den, den / kt ** 2

    @staticmethod
    def surname(a) -> str:
        return re.split(r"[.\s]+", (a or "").strip())[-1].lower()

    def _r11(self) -> None:
        ims = [r for r in self.recs if r["kind"] == "mxw" and r["pool"] and not r["is_compilation"]
               and KT_LO <= r["e_lo_ev"] <= KT_HI]
        im_by_nuc = defaultdict(list)
        for r in ims:
            im_by_nuc[r["nuclide"]].append(r)
        ser = defaultdict(list)
        for r in self.recs:
            if r["pool"] and r["kind"] in ("sig", "av"):
                ser[(r["nuclide"], r["series"])].append(r)
        self.r11_rows = []
        for (nuc, s), g in ser.items():
            if nuc not in im_by_nuc:
                continue
            bins = defaultdict(list)
            for r in g:
                bins[r["bin"]].append(r)
            bl = sorted(bins)
            e_lo = np.array([min(q["e_lo_ev"] for q in bins[b]) for b in bl])
            e_hi = np.array([max(q["e_hi_ev"] for q in bins[b]) for b in bl])
            sig = np.array([10 ** np.mean([q["x"] for q in bins[b]]) for b in bl])
            e_mid = np.sqrt(e_lo * e_hi)
            if int(((e_mid >= 3e3) & (e_mid <= 3e5)).sum()) < 2:
                continue
            own = {(self.surname(q["first_author"]), int(q["ds_year"])) for q in g if q["ds_year"] is not None}
            m = [q for q in im_by_nuc[nuc] if q["series"] != s and not any(
                q["ds_year"] is not None and self.surname(q["first_author"]) == a and abs(q["ds_year"] - y) <= 2
                for a, y in own)]
            if not m:
                continue
            par = list(range(len(m)))

            def f(i):
                while par[i] != i:
                    par[i] = par[par[i]]
                    i = par[i]
                return i
            for i in range(len(m)):
                for j in range(i):
                    if m[i]["series"] == m[j]["series"] or (
                            m[i]["first_author"] == m[j]["first_author"] and m[i]["ds_year"] == m[j]["ds_year"]):
                        par[f(i)] = f(j)
            groups = defaultdict(list)
            for i, q in enumerate(m):
                macs, cov = self.macs_over(e_lo, e_hi, e_mid, sig, q["e_lo_ev"])
                groups[f(i)].append(dict(im=q["dataset_key"], author=q["first_author"], year=q["ds_year"],
                                         kT_keV=q["e_lo_ev"] / 1e3, im_mb=10 ** q["x"] * 1e3,
                                         series_macs_mb=macs * 1e3, coverage=cov, R=macs / 10 ** q["x"]))
            gs = []
            for mem in groups.values():
                adm = [x for x in mem if x["coverage"] >= F_MIN]
                if adm:
                    Rs = [x["R"] for x in adm]
                    gs.append(dict(dir=1 if all(v > RATIO for v in Rs) else -1 if all(v < 1 / RATIO for v in Rs) else 0,
                                   mem=adm))
            if not gs:
                continue

            def cluster(dr):
                v = sorted(float(np.median([x["R"] for x in g_["mem"]])) for g_ in gs if g_["dir"] == dr)
                return max((sum(1 for u in v if a <= u <= a * RATIO) for a in v), default=0)
            nup, ndn = cluster(1), cluster(-1)
            nag = sum(g_["dir"] == 0 for g_ in gs)
            nagd = max(nup, ndn)
            flag = len(gs) >= 2 and nagd >= 2 and nagd > nag
            row = dict(nuclide=nuc, series=s, n_groups=len(gs), n_against=nagd, n_agree=nag,
                       direction=(1 if nup >= ndn else -1) if nagd else 0, flag=flag,
                       grade=("R11x" if nagd >= 3 else "R11d") if flag else "",
                       datasets=sorted({q["dataset_key"] for q in g}),
                       groups=[[{k: (round(v, 4) if isinstance(v, float) else v) for k, v in x.items()} for x in g_["mem"]] for g_ in gs])
            self.r11_rows.append(row)
            if flag:
                for k in row["datasets"]:
                    for r in self.by_ds[k]:
                        if r["nuclide"] == nuc:
                            r["fired"].add(row["grade"])
                            r["ev"]["r11"] = {kk: row[kk] for kk in ("n_groups", "n_against", "n_agree", "direction", "groups")}

    # ------------------------------------------------------------------ R12 + ladder
    def status(self, r) -> set[str]:
        k = r["dataset_key"]
        if k not in self.status_cache:
            try:
                self.status_cache[k] = exfor_text.status_codes(r["entry"], r["subentry"])
            except KeyError:
                self.status_cache[k] = set()
        return self.status_cache[k]

    def ladder(self) -> None:
        ds_no_unc = defaultdict(lambda: True)
        for r in self.recs:
            ds_no_unc[r["dataset_key"]] &= bool(r["no_unc"])
        for r in self.recs:
            f = r["fired"]
            if f & (DATA_DOWN | {"R5x", "R6x", "R10x", "R11x"}):
                st = self.status(r)
                flags = sorted(st & {"PRELM", "CURVE"})
                if flags or ds_no_unc[r["dataset_key"]]:
                    f.add("R12")
                    r["ev"]["r12"] = dict(status=flags, no_uncertainty=ds_no_unc[r["dataset_key"]])
            if f & EXCLUDE_RULES:
                r["decision"] = "exclude"
            elif (f & DATA_DOWN) and (f & RECORD_DOWN):
                r["decision"] = "exclude"
                r["ladder2"] = True
            elif f & (DATA_DOWN | {"R2d", "R8"}):
                r["decision"] = "downweight"
            else:
                r["decision"] = "keep"
