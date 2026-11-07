#!/usr/bin/env python3
"""Pack the engine calculator's precomputed model variations into small JSON files for the site.

Input: a directory of wide-grid engine runs, <RUNS>/<Name>/<variant>.json, each the output line of
scripts/talysworld/engine_grid.py (one engine run per nuclide and variant, the library v0.2.1 energy grid, 64 points
1 keV - 20 MeV, production engine engine-20261022-3 with the library deck + one keyword).
Output: docs/walkthrough/data/calc/index.json (grid, variants, nuclides) and data/calc/<Z>/<A>.json (per variant, per
channel, cross sections in mb with 4 significant digits; channels that are zero at every energy are left out).
A variant whose numbers equal the library-settings run (base) to 1e-6 is listed in "same" (the keyword is the deck's own
value for that nucleus).

usage: python3 scripts/build_site_calc.py RUNS_DIR [--items items.json]
"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs", "walkthrough", "data", "calc")
VARIANTS = [("base", "")] + [(f"ld{k}", f"ldmodel {k}") for k in range(1, 7)] + [("pe0", "preequilibrium n")] + \
           [(f"gs{k}", f"strength {k}") for k in (1, 2, 8, 9)]
CH = ["capture", "elastic", "inelastic", "np", "na", "n2n", "fission", "total"]


def sig(v):
    return float(f"{v:.4g}") if v else 0


def main():
    runs = sys.argv[1]
    items = json.load(open(sys.argv[sys.argv.index("--items") + 1])) if "--items" in sys.argv else None
    names = [it["name"] for it in items] if items else sorted(os.listdir(runs))
    os.makedirs(OUT, exist_ok=True)
    grid, nucl, total, nvar, cpu, fails = None, [], 0, 0, 0.0, []
    for nm in names:
        d = os.path.join(runs, nm)
        if not os.path.isdir(d): continue
        V, same, z = {}, [], None
        for v, kw in VARIANTS:
            f = os.path.join(d, v + ".json")
            if not os.path.exists(f):
                if os.path.exists(os.path.join(d, v + ".err.json")): fails.append(f"{nm} {v}: " + json.load(open(os.path.join(d, v + ".err.json"))).get("err", "")[:120])
                continue
            r = json.load(open(f))
            if r.get("err") or "channels" not in r: fails.append(f"{nm} {v}: {r.get('err', '')[:120]}"); continue
            z, a, comp = r["z"], r["a"], r["comp"]; cpu += r.get("cpu_s", 0)
            if grid is None: grid = [round(e, 1) for e in r["e_ev"]]
            V[v] = {c: [sig(x) for x in r["channels"][c]] for c in CH if c in r["channels"] and any(r["channels"][c])}
        if "base" not in V: continue
        b = V["base"]
        for v in V:
            if v != "base" and set(V[v]) == set(b) and all(
                    all(abs(x - y) <= 1e-6 * max(abs(x), abs(y), 1e-30) for x, y in zip(V[v][c], b[c])) for c in b):
                same.append(v)
        rec = dict(name=nm, z=z, a=a, comp=comp, v=V, same=same)
        os.makedirs(os.path.join(OUT, str(z)), exist_ok=True)
        s = json.dumps(rec, separators=(",", ":"))
        open(os.path.join(OUT, str(z), f"{a}.json"), "w").write(s); total += len(s)
        nucl.append([z, a, nm, sorted(V)]); nvar += len(V)
    idx = dict(grid_ev=grid, engine="INCOGNITA production engine engine-20261022-3 (nucleus 16606b356d6e), library v0.2 deck and inputs",
               method="one wide-grid engine run per nuclide and variant on the library v0.2.1 grid (64 energies, 1 keV - 20 MeV); "
                      "library deck + one keyword; GRIDTOP pad when the compound nucleus is unbound to an ejectile",
               variants={v: kw for v, kw in VARIANTS}, channels=CH, unit="mb", nuclides=nucl, runs=nvar, cpu_s=round(cpu))
    s = json.dumps(idx, separators=(",", ":")); open(os.path.join(OUT, "index.json"), "w").write(s); total += len(s)
    print(f"{len(nucl)} nuclides, {nvar} runs, {total/1e6:.2f} MB, engine cpu {cpu/3600:.2f} h; {len(fails)} failed")
    for f in fails: print("  FAIL", f)


if __name__ == "__main__":
    main()
