"""Build docs/walkthrough/data/q.json: reaction Q-values for the Data explorer's threshold plots.

For every nuclide in data/index.json it writes the Q-values (MeV) of (n,p), (n,alpha) and (n,2n), from the same mass
tables the engine reads (TALYS structure/masses: AME2020 where measured, else HFB-Skyrme). The page uses them to place the
plot window of a threshold reaction: the kinematic threshold, and for a charged particle out the Coulomb barrier it has
to tunnel through. A Q-value is null when a mass is in neither table; natural elements are not listed.

usage:  python scripts/build_site_q.py [TALYS structure dir, default $TALYS_DIR/structure or ~/opt/talys-src/structure]
"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs", "walkthrough", "data")
EXC_N, EXC_P, EXC_A = 8.0713181, 7.2889705, 2.42491565  # mass excesses (MeV) of the neutron, proton and alpha, AME2020


def read_table(sdir, table, sym):
    """{A: mass excess (MeV)} of one element, '(4x, i4, 2f12.6)' as in TALYS masses.f90."""
    path = os.path.join(sdir, "masses", table, f"{sym}.mass")
    if not os.path.isfile(path):
        return {}
    return {int(ln[4:8]): float(ln[20:32]) for ln in open(path) if ln[4:8].strip()}


def main():
    sdir = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        os.environ.get("TALYS_DIR") or os.path.expanduser("~/opt/talys-src"), "structure")
    idx = json.load(open(os.path.join(OUT, "index.json")))
    sym, rows = idx["sym"], idx["rows"]
    cache = {}

    def exc(Z, A):
        if Z < 1 or A < Z:
            return None
        if Z not in cache:
            cache[Z] = (read_table(sdir, "ame2020", sym[Z]), read_table(sdir, "hfb", sym[Z]))
        ame, hfb = cache[Z]
        return ame.get(A, hfb.get(A))

    def q(*terms):  # entrance minus exit mass excesses; None if any mass is missing
        return None if any(t is None for t in terms) else round(sum(terms), 3)

    out, nnull = {}, 0
    for r in rows:
        Z, A = r[0], r[1]
        if A <= 0:
            continue
        t, e_p, e_a, e_n = exc(Z, A), exc(Z - 1, A), exc(Z - 2, A - 3), exc(Z, A - 1)
        v = [q(EXC_N, t, -EXC_P, None if e_p is None else -e_p),
             q(EXC_N, t, -EXC_A, None if e_a is None else -e_a),
             q(t, None if e_n is None else -e_n, -EXC_N)]
        nnull += v.count(None)
        out[f"{Z}-{A}"] = v
    with open(os.path.join(OUT, "q.json"), "w") as f:
        json.dump({"cols": ["np", "na", "n2n"], "unit": "MeV", "masses": "AME2020, else HFB-Skyrme (TALYS structure)",
                   "q": out}, f, separators=(",", ":"))
    print(f"{len(out)} nuclides, {nnull} missing Q-values, {os.path.getsize(os.path.join(OUT, 'q.json')) / 1e3:.0f} kB")


if __name__ == "__main__":
    main()
