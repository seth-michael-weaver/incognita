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
"s_min_mev", "cpu_s", "wall_s", "err"}. The same work as a function: run(...) (used by warmpool.py, the warm pool).
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


def preload(full=False):
    """Import what every job needs (a warm worker calls this once, then forks one child per job).

    full=True also does the engine set-up that pprun.main does first in every fresh process (engine_pool._setup: one
    thread, the engine modules, the native library), in the order a fresh process does it, i.e. before any per-job
    environment is set; the child's own pprun.main repeats it as a no-op. warmpool.py uses full=True."""
    if EJ.INP + "/code" not in sys.path: sys.path.insert(0, EJ.INP + "/code")
    with contextlib.redirect_stdout(io.StringIO()):
        import numpy  # noqa: F401
        import prodrun  # noqa: F401
        if full:
            import engine_pool as EP
            EP._setup(EJ.ENG, [], "dircap,pespin")
        if EJ.ENG not in sys.path: sys.path.append(EJ.ENG)   # the engine repo, as pprun --repo uses it
        import physics.hf.jointcap  # noqa: F401


@contextlib.contextmanager
def _energy_subset(sub_ev):
    """Make pprun's engine run compute only the incident energies `sub_ev` (eV) of its declared grid.

    The engine's own subset mechanism (engine.ChainedFull(energies=..., trim_batches=False), used by the engine's
    physics.hf.pool for its bit-identical parallel runs): every run-scoped quantity still comes from the WHOLE declared
    grid -- the grid top (enincmax, hence the outgoing grid and the GRIDTOP pad), fisom's first-energy latch (the
    declared grid's first energy), the batched exciton / coupled-channels set-ups (trim_batches=False) -- and the
    run-scoped sfactor is carried by walking every declared energy below the highest requested one as far as binary.
    Energies above the highest requested one (e.g. the GRIDTOP pad energy) are not computed at all. sub_ev=None: no-op."""
    if sub_ev is None:
        yield; return
    import numpy as np
    import engine_pool as EP
    sub = tuple(float(np.float32(e)) for e in np.asarray(sorted(sub_ev), float) / 1e6)   # as engine_pool.run_item rounds the grid
    orig = EP._setup

    def setup(*a, **k):
        M, env = orig(*a, **k)
        CF = M["ChainedFull"]
        return dict(M, ChainedFull=lambda **kw: CF(energies=sub, trim_batches=False, **kw)), env
    EP._setup = setup
    try:
        yield
    finally:
        EP._setup = orig


@contextlib.contextmanager
def _hrule_cache(d):
    """Cache the library's per-item ISOHOLD h rule (r52pool.h_rule: three extra target builds per arm, ~0.4-1.3 s) on disk
    under `d`, keyed by everything it reads: engine, Z, A, the lines file's content, the deck lines (incl. the job's
    keywords), the item's own environment and the run's baseline NUCLIDO_* and INCOGNITA_* environment (INCOGNITA_*: an h that
    this repository's engine computed before engine_env mirrored the switches to it is not reused). NOT by the grid: h_rule builds its
    targets at the grid's first energy, but it reads only D0 and <Gamma_gamma> at S_n, and h came out bit-identical at
    1 keV, 1 MeV and 20 MeV (Fe-56, both arms, 2026-11-07); check_warm.py's 64-point checks run on an h cached by the
    1 MeV job. d=None: no-op. Used by the warm pool only (TW_HRULE_CACHE=0 turns it off there)."""
    if not d:
        yield; return
    import hashlib
    import r52pool as RP
    orig = RP.h_rule

    def h_rule(M, base_env, it):
        _, Z, A, lf, gj, extra, tag = it[:7]
        key = hashlib.sha256(json.dumps([EJ.ENG, int(Z), int(A), hashlib.sha256(open(lf, "rb").read()).hexdigest(), extra,
                                         sorted((it[7] or {}).items()) if len(it) > 7 else [],
                                         sorted((k, v) for k, v in base_env.items() if k.startswith(("NUCLIDO_", "INCOGNITA_", "TALYS", "CJ_", "RL_")))],
                                        default=str).encode()).hexdigest()[:24]
        f = os.path.join(d, key + ".json")
        try:
            c = json.load(open(f)); return c["row"], c["env"]
        except (OSError, ValueError, KeyError):
            pass
        row, env = orig(M, base_env, it)
        os.makedirs(d, exist_ok=True); tmp = f"{f}.{os.getpid()}.tmp"
        json.dump(dict(row=row, env=env), open(tmp, "w")); os.replace(tmp, f)
        return row, env
    RP.h_rule = h_rule
    try:
        yield
    finally:
        RP.h_rule = orig


def run(z, a, grid, comp="P", kw="", work="", gridtop=None, smin=None, keep=False, energies=None, skip_pad=False, parallel_arms=False,
        hrule_cache=None):
    """One engine run of the grid `grid` (+ the GRIDTOP pad). energies: compute and report only this subset of `grid`
    (the run-scoped quantities still come from the whole padded grid: see _energy_subset); skip_pad: do not compute the
    pad energy (same as energies=grid when a pad is added). Both give the full run's numbers at those energies.
    parallel_arms: a two-arm composition (JS) runs its second arm in a forked copy of this process, at the same time as
    the first (Linux; the warm pool uses it only when it has a free slot for it). Each arm's run starts from this
    process's state as it was before either arm ran. hrule_cache: a directory for _hrule_cache (warm pool)."""
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
    sub = None
    if energies is not None:
        want = {float(x) for x in energies}
        if not want <= set(es): raise ValueError("energies must be a subset of grid")
        sub = es = [e for e in es if e in want]
    elif skip_pad and len(g) > len(es):
        sub = list(es)
    if sub is not None: out["computed"] = len(sub)
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
                def one_arm(arm):
                    L = EJ.INP + ("/actjs_lines" if arm == "AJ" else "/lines")
                    PP.ALINES = L + "_A/V32_{:03d}_{:03d}.lines"; prodrun._PL = L + "_P"
                    pa = "A" if arm == "AJ" else arm
                    PP.DECK = {k: v + (";" + X if X else "") for k, v in base.items()}
                    sys.argv = ["pprun", "--repo", EJ.ENG, "--out", os.path.join(work, arm), "--grid", gfile, "--arm", pa, "--fewres", "off",
                                "--pewindow", "g", "--za", f"{z},{a}"]
                    with _energy_subset(sub), _hrule_cache(hrule_cache):
                        PP.main()

                try:
                    arms = EJ.ARMS[comp]; kid = None
                    if parallel_arms and len(arms) > 1 and hasattr(os, "fork"):
                        kid = os.fork()
                        if kid == 0:   # the second arm, in a copy of this process taken before the first arm ran
                            code = 1
                            try:
                                one_arm(arms[1]); code = 0
                            finally:
                                os._exit(code)
                    for arm in (arms[:1] if kid else arms):
                        one_arm(arm)
                    if kid: os.waitpid(kid, 0)
                    for arm in arms:
                        od = os.path.join(work, arm)
                        f = os.path.join(od, f"{z:03d}_{a:03d}.npz")
                        if not os.path.exists(f):
                            e = os.path.join(od, f"{z:03d}_{a:03d}.err")
                            raise RuntimeError(f"arm {arm}: " + (open(e).read().strip()[-300:] if os.path.exists(e) else "no output"))
                        q = np.load(f, allow_pickle=True); Q[arm] = {k: q[k] for k in q.files}
                        if sub is not None: Q[arm]["e_ev"] = np.asarray(es, float)   # the npz keeps the declared grid; arrays are the subset
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
                    ch["capture_P"] = arr(Q["P"], "capture_mb", n); ch["capture_A"] = arr(Q[EJ.ARMS[comp][1]], "capture_mb", n)
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
