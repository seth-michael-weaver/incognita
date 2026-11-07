#!/usr/bin/env python3
"""Engine calculator, wide-grid job: ONE target, the WHOLE energy grid in ONE engine run (production engine).

Same engine, environment, runner, deck and inputs as engine_job.py (it imports them from there); the only difference is
that all incident energies go into one run, as the library runs did, instead of one job per energy. The engine spends
about 5-6 s per job on start-up and a whole 64-point curve costs 8-13 s in one run, so this is about 100x cheaper than
one job per energy for the same physics, and it is the library's own way of running (run-scoped quantities such as the
spin-shape sfactor carry over between energies exactly as in the library).

GRIDTOP pad (default on; TW_GRIDTOP=0 or --no-gridtop to turn off): when the compound nucleus is unbound to an ejectile
(min S < 0) one dummy energy max(E) + |min S| + 1 MeV is appended so the outgoing grid reaches every exit; only the
requested energies are reported. See engine_job.py for the reason. --smin S skips the separation-energy lookup (a separate
process, ~5 s) when S is already known (the service caches it per nuclide).

usage: engine_grid.py --z Z --a A --grid GRID.json --comp COMP [--kw "ldmodel 2;bins 60"] --work DIR [--smin S]
Prints one JSON line: {"e_ev": [...], "channels": {total, elastic, nonelastic, capture, np, na, n2n, inelastic, fission: [mb]},
"s_min_mev", "cpu_s", "wall_s", "err"}. The same work as a function: run(...) (used by engine_warm.py).
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


def preload():
    """Import what every job needs (a warm worker calls this once, then forks one child per job)."""
    if EJ.INP + "/code" not in sys.path: sys.path.insert(0, EJ.INP + "/code")
    with contextlib.redirect_stdout(io.StringIO()):
        import numpy  # noqa: F401
        import prodrun  # noqa: F401
        if EJ.ENG not in sys.path: sys.path.append(EJ.ENG)   # the engine repo, as pprun --repo uses it
        import physics.hf.jointcap  # noqa: F401


def run(z, a, grid, comp="P", kw="", work="", gridtop=None, smin=None, keep=False):
    t0 = time.process_time(); w0 = time.time()
    comp = comp.replace(" [FEW->mean]", "").strip()
    es = sorted(float(x) for x in grid); work = os.path.abspath(work)
    os.makedirs(work, exist_ok=True); gfile = os.path.join(work, "grid.json")
    out = dict(z=z, a=a, comp=comp, kw=kw, arms=EJ.ARMS[comp], err="")
    if gridtop is None: gridtop = os.environ.get("TW_GRIDTOP", "1").strip().lower() not in ("0", "n", "no", "off", "false")
    g = list(es)
    if gridtop:
        try:
            if smin is None: smin = min(EJ.cn_separation_mev(z, a))
            # the service caches the returned (rounded) value and passes it back on later runs of this nucleus: pad with the
            # rounded value every time, so the first run and the later ones get the same grid
            smin = round(float(smin), 4)
            out["s_min_mev"] = smin
            if smin < 0: g.append(max(es) + (-smin + 1.0) * 1e6)
        except Exception as ex:  # noqa: BLE001
            out["err"] = f"GRIDTOP pad: separation energies unavailable: {type(ex).__name__}: {ex}"[:400]
    out["gridtop"] = gridtop; out["n_grid"] = len(g)
    n = len(es)
    if not out["err"]:
        json.dump(g, open(gfile, "w"))
        if EJ.INP + "/code" not in sys.path: sys.path.insert(0, EJ.INP + "/code")
        log = io.StringIO()
        try:
            with contextlib.redirect_stdout(log):
                import numpy as np
                import prodrun
                PP = prodrun.PP
                X = kw.strip().strip(";"); base = dict(PP.DECK); Q = {}
                try:
                    for arm in EJ.ARMS[comp]:
                        L = EJ.INP + ("/actjs_lines" if arm == "AJ" else "/lines")
                        PP.ALINES = L + "_A/V32_{:03d}_{:03d}.lines"; prodrun._PL = L + "_P"
                        pa = "A" if arm == "AJ" else arm
                        PP.DECK = {k: v + (";" + X if X else "") for k, v in base.items()}
                        od = os.path.join(work, arm)
                        sys.argv = ["pprun", "--repo", EJ.ENG, "--out", od, "--grid", gfile, "--arm", pa, "--fewres", "off", "--pewindow", "g",
                                    "--za", f"{z},{a}"]
                        PP.main()
                        f = os.path.join(od, f"{z:03d}_{a:03d}.npz")
                        if not os.path.exists(f):
                            e = os.path.join(od, f"{z:03d}_{a:03d}.err")
                            raise RuntimeError(f"arm {arm}: " + (open(e).read().strip()[-300:] if os.path.exists(e) else "no output"))
                        q = np.load(f, allow_pickle=True); Q[arm] = {k: q[k] for k in q.files}
                finally:
                    PP.DECK = base
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
    out["e_ev"] = es
    out["cpu_s"] = round(time.process_time() - t0, 2); out["wall_s"] = round(time.time() - w0, 2)
    if not keep: shutil.rmtree(work, ignore_errors=True)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--z", type=int, required=True); ap.add_argument("--a", type=int, required=True)
    ap.add_argument("--grid", required=True); ap.add_argument("--comp", default="P"); ap.add_argument("--kw", default="")
    ap.add_argument("--work", required=True); ap.add_argument("--keep", action="store_true"); ap.add_argument("--smin", type=float)
    ap.add_argument("--no-gridtop", action="store_true")
    a = ap.parse_args()
    out = run(a.z, a.a, json.load(open(a.grid)), a.comp, a.kw, a.work, gridtop=False if a.no_gridtop else None, smin=a.smin, keep=a.keep)
    sys.stdout.write(json.dumps(out) + "\n"); sys.stdout.flush()


if __name__ == "__main__":
    main()
