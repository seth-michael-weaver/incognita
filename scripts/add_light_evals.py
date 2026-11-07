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


def apply(out=OUT, src=SRC):
    """Write every evaluation of `src` into its nuclide file under `out` and list them in index.json. An evaluation that
    is no longer in `src` (withdrawn) loses its "rm" block, so running this alone never leaves a stale curve behind.
    Files are read and written as UTF-8 (labels and caveats carry µ, χ², en dashes)."""
    idxf = os.path.join(out, "index.json")
    with open(idxf, encoding="utf-8") as fh:
        idx = json.load(fh)
    evals = {}
    for f in sorted(glob.glob(os.path.join(src, "*.json"))):
        with open(f, encoding="utf-8") as fh:
            ev = json.load(fh)
        Z, A = int(ev["Z"]), int(ev["A"])
        nf = os.path.join(out, "n", str(Z), f"{A}.json")
        rec = _read(nf)
        rec["rm"] = {k: ev[k] for k in KEEP if k in ev}
        rec["rm"]["report"] = REPO + os.path.basename(f)[:-5] + ".md"
        os.makedirs(os.path.dirname(nf), exist_ok=True)
        _write(nf, rec)
        evals[f"{Z}-{A}"] = ev["id"]
    for za in set(idx.get("light_evals") or {}) - set(evals):   # withdrawn since the last run
        Z, A = za.split("-")
        nf = os.path.join(out, "n", Z, f"{A}.json")
        rec = _read(nf)
        if rec.pop("rm", None) is not None:
            _write(nf, rec)
    idx["light_evals"] = evals
    _write(idxf, idx)
    print(f"light evaluations added: {evals or 'none'}")


def _read(path):
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _write(path, obj):
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, separators=(",", ":"))


if __name__ == "__main__":
    apply()
