"""Add INCOGNITA's light-nuclide R-matrix evaluations to the Every nuclide data (docs/walkthrough/data/).

Below Z 8 the page shows measurements only, unless an R-matrix evaluation of that nuclide has passed its pre-registered
gates. Each passing evaluation is one file data/light_evals/<ID>.json (written from the frozen fit by the research
card; every number in it comes from INCOGNITA's own R-matrix model, no evaluated-library content) with its public
report data/light_evals/<ID>.md. This script copies each one into the nuclide's file as "rm" and lists it in
index.json under "light_evals" ("<Z>-<A>": id). build_site_data.py calls it at the end; it can also run alone:

usage:  python scripts/add_light_evals.py
"""
import glob, json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "data", "light_evals")
OUT = os.path.join(ROOT, "docs", "walkthrough", "data")
REPO = "https://github.com/seth-michael-weaver/incognita/blob/main/data/light_evals/"
KEEP = ("id", "label", "reaction", "e_min_ev", "e_max_ev", "energy_ev", "sigma_b", "mubar_cm", "chi2_dof", "caveat", "checks")


def apply(out=OUT):
    idxf = os.path.join(out, "index.json")
    idx = json.load(open(idxf))
    evals = {}
    for f in sorted(glob.glob(os.path.join(SRC, "*.json"))):
        ev = json.load(open(f))
        Z, A = int(ev["Z"]), int(ev["A"])
        nf = os.path.join(out, "n", str(Z), f"{A}.json")
        rec = json.load(open(nf)) if os.path.exists(nf) else {}
        rec["rm"] = {k: ev[k] for k in KEEP if k in ev}
        rec["rm"]["report"] = REPO + os.path.basename(f)[:-5] + ".md"
        os.makedirs(os.path.dirname(nf), exist_ok=True)
        with open(nf, "w") as fh:
            json.dump(rec, fh, separators=(",", ":"))
        evals[f"{Z}-{A}"] = ev["id"]
    idx["light_evals"] = evals
    with open(idxf, "w") as fh:
        json.dump(idx, fh, separators=(",", ":"))
    print(f"light evaluations added: {evals or 'none'}")


if __name__ == "__main__":
    apply()
