"""Measured thermal capture sigma_gamma(0.0253 eV) for every target, by the PHASE0 anchor rule
(rl/phase0/code/x4_anchor.py + make_anchors.py, read-only imports; EXFOR snapshot entry_2026-10-14.zip).

Tier 1 = RRRTHERM's fixed rule (thermal point at 0.0253 eV stated, uncertainty given and <= 5 %, single-isotope target,
pre-2010 entries fitted, >= 2010 HELD), tier 2 only where tier 1 is empty (rel. unc. <= 10 %, or MXW of the rule's 1/v
targets without an energy column); capture = absorption - fission where no capture entry passes but both do.
Birge-scaled weighted mean. The six PHASE0 nuclides take anchors_all.json as published.

Deviation from the rule as written: a partial cross section to one isomeric state of the product ((N,G)...-M / -G)
is excluded, since it is not the total capture.

Writes docs/walkthrough/data/thermal.json (the explorer's diamond at 0.0253 eV) and the full table to the work dir.
usage (WSL): PYTHONDONTWRITEBYTECODE=1 ~/micromamba/envs/nucleus-phys/bin/python scripts/build_site_thermal.py
"""
import json, math, os, re, sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, "/home/seth/nucleus/research/rl/phase0/code")
import numpy as np  # noqa: E402
import x4_anchor as X  # noqa: E402
C = X.C

OUT = Path(os.path.expanduser(os.environ.get("PW_WORK", "~/koningov_data")))
SITE = Path(__file__).resolve().parent.parent / "docs" / "walkthrough" / "data"
JL = OUT / "x4_therm_all.jsonl"
P0 = "/home/seth/nucleus/research/rl/phase0/out/anchors_all.json"
_v0 = C._value
C._value = lambda rec: (lambda r: (None, None, None) if r[0] == 0 else r)(_v0(rec))  # a 0 value has no relative uncertainty: treat as "no DATA value"
X.pat = re.compile(r"\(\d+-[A-Z]+-\d+\(N,(G|ABS|F)\)")


def wmean(rows):
    v = np.array([r["value"] for r in rows]); s = np.array([r["unc"] for r in rows])
    w = 1 / s ** 2; mu = float(np.sum(w * v) / np.sum(w)); smu = float(1 / math.sqrt(np.sum(w)))
    R = math.sqrt(float(np.sum(((v - mu) / s) ** 2)) / (len(v) - 1)) if len(v) > 1 else 1.0
    return mu, smu * max(R, 1.0), R


def has_energy_col(rec):
    names = [str(x).strip() for x in (rec["data"][0] or []) + (rec["common"][0] or [])]
    return any(n.startswith(("EN", "KT")) for n in names)


def pick(rows, recs, t, q):
    fit = [r for r in rows if r["target"] == t and r["quantity"] == q and r["decision"] == "fit"]
    held = [r for r in rows if r["target"] == t and r["quantity"] == q and r["decision"] == "HELD"]
    tier = 1
    if not fit:
        tier = 2
        for r in rows:
            if r["target"] != t or r["quantity"] != q or r["decision"] != "excluded" or (r["year"] or 0) >= 2010:
                continue
            if r["value"] is None or not r["unc"] or r["unc"] <= 0 or r.get("npts", 1) > 3:
                continue
            w = r["why"]
            if w.startswith("relative uncertainty") and r["unc"] / abs(r["value"]) <= 0.10:
                fit.append(r)
            elif r["sf8"] == "MXW" and t in C.ONEOVERV and w == "no energy stated" and not has_energy_col(recs[r["sub"]]):
                fit.append(r)
    if not fit:
        return None
    mu, su, R = wmean(fit)
    return dict(value=mu, unc=su, birge=R, tier=tier, subs=[r["sub"] for r in fit], n=len(fit),
                held=[r["sub"] for r in held], years=[r["year"] for r in fit])


def main():
    if not JL.exists():
        print(X.extract(JL), "subentries", flush=True)
    recs = {}
    for l in open(JL):
        r = json.loads(l); recs[r["subent"]] = r
    targets = sorted({m.group(1) for r in recs.values()
                      for m in [re.match(r"^\((\d+-[A-Z]+-\d+)\(", "".join(r["bib"].get("REACTION", [])).replace(" ", ""))] if m})
    rows, _ = C.curate(str(JL), targets)
    for r in rows:  # a partial cross section to one isomeric state of the product is not the total capture
        if re.search(r"\(N,G\)[0-9A-Z-]*-(M[0-9]?|G),", r["reaction"]):
            r["decision"], r["why"] = "excluded", "partial: one isomeric state of the product"
    out = {}
    for t in targets:
        z, sym, a = t.split("-")
        if not a.isdigit() or int(a) == 0:
            continue
        cap = pick(rows, recs, t, "sig0:capture")
        if cap is None:
            ab, fi = pick(rows, recs, t, "sig0:absorption"), pick(rows, recs, t, "sig0:fission")
            if ab and fi and ab["value"] > fi["value"]:
                cap = dict(value=ab["value"] - fi["value"], unc=math.hypot(ab["unc"], fi["unc"]), tier=max(ab["tier"], fi["tier"]),
                           subs=ab["subs"] + fi["subs"], n=ab["n"] + fi["n"], held=[], note="absorption - fission")
        if cap:
            out[f"{int(z)}-{int(a)}"] = cap
    p0 = json.load(open(P0))
    for nuc, a in p0.items():
        m = re.match(r"([A-Z][a-z]?)(\d+)", nuc); sym, A = m.group(1), int(m.group(2))
        Z = {"Fe": 26, "Zr": 40, "Cl": 17, "Cu": 29, "Pu": 94, "U": 92}[sym]
        c = a.get("capture")
        if c:
            out[f"{Z}-{A}"] = dict(value=c["value"], unc=c["unc"], birge=c.get("birge", 1.0), tier=c["tier"], subs=c["subs"],
                                   n=len(c["subs"]), held=[h[0] for h in c.get("held", [])], note="PHASE0 anchors_all.json " + c.get("note", ""))
    json.dump(out, open(OUT / "thermal_capture.json", "w"), indent=0)
    def sg(v, n):
        return float(f"{v:.{n}g}")
    th = {k: [sg(v["value"], 5), sg(v["unc"], 3), v["n"], v["tier"], v["subs"]] + (["abs"] if "absorption" in v.get("note", "") else [])
          for k, v in sorted(out.items(), key=lambda kv: tuple(map(int, kv[0].split("-"))))}
    json.dump({"note": "Measured thermal capture sigma_gamma(0.0253 eV), b: [value, 1 sigma, number of EXFOR entries, tier, EXFOR subentries"
               "(, 'abs' = absorption - fission)]. Birge-scaled weighted mean by the PHASE0 rule (scripts/build_site_thermal.py).",
               "th": th}, open(SITE / "thermal.json", "w"), separators=(",", ":"))
    print(len(out), "targets with a measured thermal capture value;", sum(v["tier"] == 1 for v in out.values()), "tier 1")


if __name__ == "__main__":
    main()
