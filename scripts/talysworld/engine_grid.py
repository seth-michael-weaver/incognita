#!/usr/bin/env python3
"""Engine calculator, wide-grid job: ONE target, the WHOLE energy grid in ONE engine run (production engine).

Same engine, environment, runner, deck and inputs as engine_job.py (it imports them from there); the only difference is
that all incident energies go into one run, as the library runs did, instead of one job per energy. That is about 100x
cheaper for the same physics, and it is the library's own way of running (run-scoped quantities such as the spin-shape
sfactor carry over between energies exactly as in the library).

GRIDTOP pad (default on; TW_GRIDTOP=0 or --no-gridtop to turn off): when the compound nucleus is unbound to an ejectile
(min S < 0) one dummy energy max(E) + |min S| + 1 MeV is appended so the outgoing grid reaches every exit; only the
requested energies are reported. See engine_job.py for the reason.

usage: engine_grid.py --z Z --a A --grid GRID.json --comp COMP [--kw "ldmodel 2;strength 9"] --work DIR [--report E1,E2,...]
Prints one JSON line: {"e_ev": [...], "channels": {total, elastic, nonelastic, capture, np, na, n2n, inelastic, fission: [mb]},
"cpu_s", "wall_s", "err"}. --report keeps only the grid energies within 1e-6 (relative) of the listed ones.
"""
import argparse, contextlib, io, json, os, shutil, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import engine_job as EJ  # noqa: E402  (sets the library run environment on import)


def arr(q, k, n):
    import numpy as np
    if k == "capture_mb" and k not in q: k = "ch_xs000000"
    if k not in q: return [0.0] * n
    v = np.asarray(q[k], float).ravel()
    return [float(x) for x in v[:n]]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--z", type=int, required=True); ap.add_argument("--a", type=int, required=True)
    ap.add_argument("--grid", required=True); ap.add_argument("--comp", default="P"); ap.add_argument("--kw", default="")
    ap.add_argument("--work", required=True); ap.add_argument("--keep", action="store_true"); ap.add_argument("--report", default="")
    ap.add_argument("--no-gridtop", action="store_true")
    a = ap.parse_args(); t0 = time.process_time(); w0 = time.time()
    comp = a.comp.replace(" [FEW->mean]", "").strip()
    es = sorted(float(x) for x in json.load(open(a.grid))); a.work = os.path.abspath(a.work)
    os.makedirs(a.work, exist_ok=True); grid = os.path.join(a.work, "grid.json")
    out = dict(z=a.z, a=a.a, comp=comp, kw=a.kw, arms=EJ.ARMS[comp], err="")
    gridtop = not a.no_gridtop and os.environ.get("TW_GRIDTOP", "1").strip().lower() not in ("0", "n", "no", "off", "false")
    g = list(es)
    if gridtop:
        try:
            smin = min(EJ.cn_separation_mev(a.z, a.a)); out["s_min_mev"] = round(smin, 4)
            if smin < 0: g.append(max(es) + (-smin + 1.0) * 1e6)
        except Exception as ex:  # noqa: BLE001
            out["err"] = f"GRIDTOP pad: separation energies unavailable: {type(ex).__name__}: {ex}"[:400]
    out["gridtop"] = gridtop; out["n_grid"] = len(g)
    n = len(es)
    if not out["err"]:
        json.dump(g, open(grid, "w"))
        sys.path.insert(0, EJ.INP + "/code")
        log = io.StringIO()
        try:
            with contextlib.redirect_stdout(log):
                import numpy as np
                import prodrun
                PP = prodrun.PP
                X = a.kw.strip().strip(";"); base = dict(PP.DECK); Q = {}
                for arm in EJ.ARMS[comp]:
                    L = EJ.INP + ("/actjs_lines" if arm == "AJ" else "/lines")
                    PP.ALINES = L + "_A/V32_{:03d}_{:03d}.lines"; prodrun._PL = L + "_P"
                    pa = "A" if arm == "AJ" else arm
                    PP.DECK = {k: v + (";" + X if X else "") for k, v in base.items()}
                    od = os.path.join(a.work, arm)
                    sys.argv = ["pprun", "--repo", EJ.ENG, "--out", od, "--grid", grid, "--arm", pa, "--fewres", "off", "--pewindow", "g",
                                "--za", f"{a.z},{a.a}"]
                    PP.main()
                    f = os.path.join(od, f"{a.z:03d}_{a.a:03d}.npz")
                    if not os.path.exists(f):
                        e = os.path.join(od, f"{a.z:03d}_{a.a:03d}.err")
                        raise RuntimeError(f"arm {arm}: " + (open(e).read().strip()[-300:] if os.path.exists(e) else "no output"))
                    q = np.load(f, allow_pickle=True); Q[arm] = {k: q[k] for k in q.files}
                first = Q[EJ.ARMS[comp][0]] if comp not in ("A(rotor)", "ACTJS A(rotor)") else Q[EJ.ARMS[comp][-1]]
                ch = {c: arr(first, k, n) for c, k in EJ.CH.items()}
                if comp in ("JS(P,A)", "ACTJS JS(P,A)"):
                    from physics.hf import jointcap as J

                    class _Q(dict):
                        files = property(lambda s: list(s.keys()))
                    c = J.combine(_Q(Q["P"]), _Q(Q[EJ.ARMS[comp][1]]))
                    ch["capture"] = [float(x) for x in np.asarray(c["capture_mb"], float).ravel()[:n]]
                out["channels"] = ch
        except Exception as ex:  # noqa: BLE001
            out["err"] = f"{type(ex).__name__}: {ex}"[:400]; out["log_tail"] = log.getvalue()[-400:]
    keep = list(range(n))
    if a.report:
        want = [float(x) for x in a.report.split(",")]
        keep = [i for i, e in enumerate(es) if any(abs(e / w - 1) < 1e-6 for w in want)]
        seen, k2 = set(), []
        for i in keep:   # a grid may repeat an energy (20 MeV twice in grid134): keep the first
            key = round(es[i], 3)
            if key not in seen: seen.add(key); k2.append(i)
        keep = k2
    out["e_ev"] = [es[i] for i in keep]
    if "channels" in out: out["channels"] = {c: [v[i] for i in keep] for c, v in out["channels"].items()}
    out["cpu_s"] = round(time.process_time() - t0, 2); out["wall_s"] = round(time.time() - w0, 2)
    if not a.keep: shutil.rmtree(a.work, ignore_errors=True)
    sys.stdout.write(json.dumps(out) + "\n"); sys.stdout.flush()


if __name__ == "__main__":
    main()
