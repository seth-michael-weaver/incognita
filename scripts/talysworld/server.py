#!/usr/bin/env python3
"""TALYSWORLD-style calculator for INCOGNITA's production engine (local service + web page).

Like IAEA TALYSWORLD: pick a target, incident energies and a few keywords; every incident energy runs as its own engine
job (energy grid [E], padded with a dummy top energy when the compound nucleus is unbound to some ejectile: see
engine_job.py, GRIDTOP pad; TW_GRIDTOP=0 turns the pad off), at most 3 at a time at nice 10, and each finished point is streamed to the page. Results are
cached by (inputs, energy) under ~/talysworld_data/cache, so a repeated point costs nothing.

Start (laptop WSL / Linux, system python3 with pandas + pyarrow for the library overlay):
    python3 scripts/talysworld/server.py            # then open http://localhost:8765/
Options: --port 8765 --workers 3 (hard cap 3) --nice 10.

API (JSON): GET /api/meta, GET /api/library?z=&a=, POST /api/run {z, a, energies_ev, comp, kw:{...}, extra},
GET /api/stream?run=ID (Server-Sent Events: one "point" event per finished energy, then "done"), GET /api/run?run=ID.
POST /api/gridrun {z, a, comp, kw, extra}: ONE wide-grid engine run (engine_grid.py) on the library grid (64 energies), the
way the library itself ran; about 100x cheaper than one job per energy. The run has one "point": {e_ev: [...], channels}.
The public site's calculator page (www.incognitanuclear.org/calculator.html) finds this service at http://localhost:8765
and offers live runs; CORS allows only the site's own origins and localhost, and the service listens on 127.0.0.1 only.
Never expose it publicly (no tunnels, no port forwarding).
Engine job: scripts/talysworld/engine_job.py (production engine engine-20261022-3, library v0.2 run environment).
Warm pool (default; --no-warm for the old fresh process per job): jobs go to warmpool.py, one preloaded daemon per service
port (socket ~/talysworld_data/warm-PORT.sock) that forks a child per job, at most --workers engine processes at once; a
one-energy point then costs ~1-3 s instead of ~11-15 s, with the same numbers (scripts/talysworld/check_warm.py).
"""
import argparse, hashlib, json, math, os, queue, re, subprocess, threading, time, uuid
from concurrent.futures import ThreadPoolExecutor
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

import warmpool as WP  # scripts/talysworld/warmpool.py (its client side imports no engine)

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SITE = os.path.join(ROOT, "docs", "walkthrough")
WEB = os.path.join(HERE, "web")   # the calculator page lives here (local only; not on the public site since 2026-11-07)
LIB = os.path.join(ROOT, "library", "v0.2.2")   # the library the site shows
H = os.path.expanduser("~")
ENG = os.environ.get("TW_ENG", f"{H}/fastgate_data/eng/16606b356d6e")
PY = os.path.join(ENG, ".venv", "bin", "python")
DATA = os.environ.get("TW_DATA", f"{H}/talysworld_data")
ENGINE_LABEL = "INCOGNITA production engine engine-20261022-3 (nucleus 16606b356d6e)"
GRIDTOP_NOTE = " + GRIDTOP pad (grid [E, E + |min S| + 1 MeV], only E reported)"
MAX_WORKERS = 3
GRIDTOP = os.environ.get("TW_GRIDTOP", "1").strip().lower() not in ("0", "n", "no", "off", "false")  # engine_job.py reads it too

# Exposed keywords (TALYS spelling). "" = the library deck's own value (per-nucleus deck lines + production deck).
KEYWORDS = {
    "localomp": dict(label="Optical model (neutron)", help="TALYS localomp: Koning-Delaroche local (y) or global (n) potential. "
                     "Checked 2026-11-07: 'n' gives the same numbers as the deck on Fe-56 and Pb-208 (no effect on this engine path)",
                     options=[["", "library deck (local KD03)"], ["y", "local Koning-Delaroche"], ["n", "global Koning-Delaroche (no effect seen)"]]),
    "rvadjust": dict(label="OMP radius scale (neutron)", help="TALYS rvadjust n: real volume radius x factor. The response "
                     "can be large (Pb-208 1 MeV total 4.80 b at 1 -> 8.08 b at 1.05); that is the optical model's own smooth response "
                     "to the radius, not a stale cache",
                     options=[["", "library deck (1)"], ["n 0.97", "0.97"], ["n 0.99", "0.99"], ["n 1.01", "1.01"], ["n 1.03", "1.03"]]),
    "ldmodel": dict(label="Level density model", help="TALYS ldmodel (engine default 1; 5 above A = 215 for neutrons)",
                    options=[["", "library deck"], ["1", "1 constant temperature + Fermi gas"], ["2", "2 back-shifted Fermi gas"],
                             ["3", "3 generalised superfluid"], ["4", "4 Goriely HFB tables"], ["5", "5 Hilaire-Goriely HFB tables"],
                             ["6", "6 Hilaire-Goriely T-dependent HFB"]]),
    "strength": dict(label="Gamma strength function (E1)", help="TALYS strength (library deck: per nucleus, mostly 8 or 9)",
                     options=[["", "library deck"], ["1", "1 Kopecky-Uhl"], ["2", "2 Brink-Axel"], ["3", "3 HFBCS + QRPA tables"],
                              ["4", "4 HFB + QRPA tables"], ["5", "5 Goriely hybrid"], ["6", "6 T-dependent HFB"],
                              ["7", "7 T-dependent RMF"], ["8", "8 Gogny D1M HFB + QRPA"], ["9", "9 SMLO (2019)"]]),
    "preequilibrium": dict(label="Pre-equilibrium", help="TALYS preequilibrium (library deck: y at every energy)",
                           options=[["", "library deck (on)"], ["y", "on"], ["n", "off"]]),
    "widthmode": dict(label="Width fluctuation", help="TALYS widthmode",
                      options=[["", "library deck"], ["0", "0 none (Hauser-Feshbach)"], ["1", "1 Moldauer"], ["2", "2 HRTW"], ["3", "3 GOE"]]),
    "spincutmodel": dict(label="Spin cut-off model", help="TALYS spincutmodel",
                         options=[["", "library deck"], ["1", "1"], ["2", "2"]]),
}
COMPS = [["library", "as the library (v0.2 composition for this nucleus)"], ["P", "P arm (field)"], ["A", "A arm (anchored)"],
         ["AJ", "AJ arm (actinide lines)"]]
ORIGINS = re.compile(r"^(https://(www\.)?incognitanuclear\.org|https://nucleus-incognita-woad\.vercel\.app|http://(localhost|127\.0\.0\.1)(:\d+)?)$")
EXTRA_OK = re.compile(r"^[A-Za-z0-9 .;_+\-]*$")

pool = None
NICE = 10
LIBRARY = {}           # (Z, A) -> dict
LIB_GRID = []
RUNS = {}              # run id -> dict(points=[...], n=int, q=[queues], done=bool)
INFLIGHT = {}          # (key, e) -> threading.Event + slot
LOCK = threading.Lock()


def inside(base, rel):
    """base/rel if it is a path strictly inside base (no '..' escape, not a sibling sharing base's name prefix), else None."""
    p = os.path.normpath(os.path.join(base, rel))
    return p if p.startswith(base + os.sep) else None


def load_library():
    global LIB_GRID
    import numpy as np, pandas as pd
    C = pd.read_parquet(os.path.join(LIB, "capture_v022.parquet"), columns=["nuclide_id", "Z", "A", "tier", "energy_ev", "sigma_b",
                                                                            "value_source", "engine_points_repaired"])
    X = pd.read_parquet(os.path.join(LIB, "channels_v022.parquet")).set_index("nuclide_id")
    for r in C.itertuples(index=False):
        vs = r.value_source; m = re.search(r"composed (.+?);", vs); f = re.search(r"blind curve x ([0-9.]+) \(measured MACS30 anchor", vs)  # v0.2.1+: "(... anchor; centre-of-mass ...)"
        d = dict(nuclide_id=r.nuclide_id, Z=int(r.Z), A=int(r.A), tier=r.tier, energy_ev=[float(x) for x in r.energy_ev],
                 capture_mb=[float(x) * 1e3 for x in r.sigma_b], comp=(m.group(1).strip() if m else ""),
                 carried_v01="v0.1 value carried" in vs, anchored_factor=float(f.group(1)) if f else None,
                 points_repaired=int(r.engine_points_repaired or 0), value_source=vs)
        if r.nuclide_id in X.index:
            x = X.loc[r.nuclide_id]
            if x.energy_ev is not None and len(x.energy_ev):
                for c in ("np", "n2n", "na"):
                    d[c + "_mb"] = [float(v) for v in x[f"sigma_{c}_mb"]]
        LIBRARY[(int(r.Z), int(r.A))] = d
    LIB_GRID = [float(x) for x in C.energy_ev.iloc[0]]


def resolve_comp(z, a, comp):
    if comp in ("P", "A", "AJ"): return comp
    d = LIBRARY.get((z, a))
    if d and d["comp"]: return d["comp"].replace(" [FEW->mean]", "")
    return "P"


def kw_string(kw, extra):
    parts = []
    for k in sorted(KEYWORDS):
        v = str((kw or {}).get(k, "") or "").strip()
        if v:
            if v not in [o[0] for o in KEYWORDS[k]["options"]]: raise ValueError(f"{k}: value {v!r} not offered")
            parts.append(f"{k} {v}")
    extra = (extra or "").strip().strip(";")
    if extra:
        if not EXTRA_OK.match(extra): raise ValueError("extra keywords: letters, digits, spaces, '.', '-', '_', '+', ';' only")
        parts += [p.strip() for p in extra.split(";") if p.strip()]
    return ";".join(parts)


def ekey(e):
    return f"{float(e):.6e}"


def engine_id():
    """The engine the jobs run (TW_ENG): its ENGINE_COMMIT (12 characters), else the install directory's name. The default
    install gives 16606b356d6e either way, so its existing cache stays valid."""
    try:
        with open(os.path.join(ENG, "ENGINE_COMMIT")) as f:
            c = f.read().strip()[:12]
        if c: return c
    except OSError:
        pass
    return os.path.basename(os.path.normpath(ENG))


def _flavour():
    """engine_env.flavour of TW_ENG ('repo' | 'production'); 'production' when it cannot tell (the cache key then stays as
    it always was)."""
    try:
        import engine_env
        return engine_env.flavour(ENG)
    except Exception:  # noqa: BLE001
        return "production"


def cache_key(z, a, comp, kws):
    tag = [engine_id(), "libv02-inputs", z, a, comp, kws]
    if GRIDTOP: tag.append("gridtop-pad1")   # padded jobs differ from the old one-point jobs: separate cache
    if _flavour() == "repo": tag.append("switches-mapped")   # SWNAMES6: results from before engine_env reached this engine
    return hashlib.sha256(json.dumps(tag).encode()).hexdigest()[:16]


def run_point(z, a, comp, kws, key, e):
    """One engine job (or the cached result) for one energy."""
    cdir = os.path.join(DATA, "cache", key); cf = os.path.join(cdir, ekey(e) + ".json")
    if os.path.exists(cf):
        try: return dict(json.load(open(cf)), cached=True)
        except (OSError, ValueError): pass
    with LOCK:
        ev = INFLIGHT.get((key, ekey(e)))
        mine = ev is None
        if mine: ev = INFLIGHT[(key, ekey(e))] = threading.Event()
    if not mine:
        ev.wait()
        if os.path.exists(cf): return dict(json.load(open(cf)), cached=True)
    try:
        work = os.path.join(DATA, "jobs", uuid.uuid4().hex[:12])
        res = warm_point(z, a, comp, kws, e, work)
        if res is None:   # no warm pool: one fresh engine process (the old way)
            cmd = ["nice", "-n", str(NICE), PY, os.path.join(HERE, "engine_job.py"), "--z", str(z), "--a", str(a), "--e", repr(float(e)),
                   "--comp", comp, "--kw", kws, "--work", work, "--cold"]
            try:
                p = subprocess.run(cmd, capture_output=True, text=True, timeout=3600, cwd=DATA)
                line = [ln for ln in p.stdout.splitlines() if ln.startswith("{")]
                res = json.loads(line[-1]) if line else dict(z=z, a=a, e_ev=e, err=f"engine job exit {p.returncode}: {p.stderr.strip()[-300:]}")
            except subprocess.TimeoutExpired:
                res = dict(z=z, a=a, e_ev=e, err="engine job timed out (1 h)")
        res["e_ev"] = float(e); res.pop("log_tail", None)
        if not res.get("err"):
            os.makedirs(cdir, exist_ok=True); json.dump(res, open(cf, "w"))
            mf = os.path.join(cdir, "inputs.json")
            if not os.path.exists(mf): json.dump(dict(z=z, a=a, comp=comp, kw=kws, engine=ENGINE_LABEL, gridtop=GRIDTOP), open(mf, "w"))
        return dict(res, cached=False)
    finally:
        if mine:
            with LOCK: INFLIGHT.pop((key, ekey(e)), None)
            ev.set()


# Energy grids for one-job-per-curve runs (POST /api/gridrun): points 16 / 32 (log-spaced 1 keV - 20 MeV), 64 (the library
# grid), 134 (the production grid, inputs/grid134.json); "low" adds the 15 points below 1 keV of library v0.2.2 (2 eV - 661 eV).
LOW15 = [2.0, 3.0266439158325404, 4.580286696623066, 6.931448431551464, 10.489513111631119, 15.874010519681994, 24.022488679628626,
         36.353759602677016, 55.014942659540594, 83.25532074018732, 125.99210498948727, 190.6666190046831, 288.5399811814427,
         436.6538892586245, 660.7979186246156]
POINTS = [16, 32, 64, 134]
BINS = [20, 40, 60, 100]   # the engine's continuum excitation bins (TALYS keyword bins; 40 = the TALYS default, not in the deck)
SMIN = {}                  # (z, a) -> min separation energy of the compound nucleus (MeV), for the GRIDTOP pad
WARM = dict(p=None, lock=threading.Lock())
WARM_SOCK = None           # set in main(): one pool socket per service port
# Curves with TW_CHUNK_MIN energies or more are split over the workers (energy subsets of one declared grid; equal to the
# one-run curve, check_warm.py). Default 0 = off: measured 2026-11-07, every slice repeats the run's set-up and walks all
# lower energies (sfactor), so 2-3 slices gave 0.6x-1.4x on the 64-point curve; a two-arm curve already runs its arms
# side by side.
CHUNK_MIN = int(os.environ.get("TW_CHUNK_MIN", "0"))


def grid_for(points, low):
    if points == 64: g = list(LIB_GRID)
    elif points == 134:
        g = json.load(open(os.path.join(os.environ.get("TW_INPUTS", f"{H}/libv02/inputs"), "grid134.json")))
    elif points in (16, 32): g = [10 ** (3 + i * (math.log10(2e7) - 3) / (points - 1)) for i in range(points)]
    else: raise ValueError(f"points: one of {POINTS}")
    return (LOW15 + g) if low else g


def warm_pool():
    """The warm engine pool (warmpool.py: one preloaded daemon, a forked child per job, at most `--workers` at once),
    started on first use; None if it cannot be started (callers then run a fresh process per job, as before)."""
    with WARM["lock"]:
        if WARM["p"] is not None and WARM["p"].alive(): return WARM["p"]
        if WARM.get("fails", 0) >= 3: return None
        try:
            P, proc = WP.ensure(WARM_SOCK, workers=pool._max_workers, nice=NICE, data=DATA, python=PY)
            WARM["p"], WARM["proc"] = P, proc; return P
        except (OSError, RuntimeError) as ex:
            WARM["fails"] = WARM.get("fails", 0) + 1
            print(f"talysworld: warm pool unavailable ({ex}); fresh processes", flush=True); return None


def smin_of(P, z, a):
    # rounded to 4 decimals, the value engine_grid.run pads with and reports (s_min_mev), which run_grid also caches here
    if (z, a) not in SMIN: SMIN[(z, a)] = round(float(min(P.smin(z, a))), 4)
    return SMIN[(z, a)]


def warm_point(z, a, comp, kws, e, work):
    """One energy through the warm pool, in engine_job.py's result format; None if the pool is unavailable."""
    P = warm_pool()
    if P is None: return None
    try:
        sm = smin_of(P, z, a) if GRIDTOP else None
        r = P.run(dict(z=z, a=a, grid=[float(e)], comp=comp, kw=kws, work=work, smin=sm, gridtop=GRIDTOP, skip_pad=True))
    except (OSError, RuntimeError, ValueError) as ex:
        return dict(z=z, a=a, e_ev=e, err=f"warm pool: {type(ex).__name__}: {ex}"[:300])
    out = {k: v for k, v in r.items() if k not in ("channels", "e_ev", "n_grid", "computed")}
    if r.get("channels"): out["channels"] = {c: v[0] for c, v in r["channels"].items()}
    if GRIDTOP and sm is not None: out["s_min_mev"] = round(sm, 4)
    if GRIDTOP and sm is not None and sm < 0: out["grid_ev"] = [float(e), float(e) + (-sm + 1.0) * 1e6]
    out["warm"] = True
    return out


def engine_call(args):
    """One curve: through the warm pool, its energies split over the pool's workers when the grid is wide (CHUNK_MIN
    points or more); or one fresh engine_grid.py process if the pool is unavailable."""
    P = warm_pool()
    if P is not None:
        try:
            sm = args.get("smin")
            if sm is None and GRIDTOP: sm = smin_of(P, args["z"], args["a"])
            n = len(args["grid"]); chunks = pool._max_workers if CHUNK_MIN and n >= CHUNK_MIN else 1
            res = P.run_grid(args["z"], args["a"], args["grid"], args["comp"], args["kw"], smin=sm, chunks=chunks, gridtop=GRIDTOP)
            res["warm"] = True; return res
        except (OSError, RuntimeError, ValueError) as ex:
            print(f"talysworld: warm pool call failed ({ex}); fresh process", flush=True)
    os.makedirs(os.path.dirname(args["work"]), exist_ok=True)
    gf = args["work"] + ".grid.json"; json.dump(args["grid"], open(gf, "w"))
    cmd = ["nice", "-n", str(NICE), PY, os.path.join(HERE, "engine_grid.py"), "--z", str(args["z"]), "--a", str(args["a"]), "--grid", gf,
           "--comp", args["comp"], "--kw", args["kw"], "--work", args["work"]] + (["--smin", repr(args["smin"])] if args.get("smin") is not None else [])
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=7200, cwd=DATA)
        line = [ln for ln in p.stdout.splitlines() if ln.startswith("{")]
        return json.loads(line[-1]) if line else dict(err=f"engine job exit {p.returncode}: {p.stderr.strip()[-300:]}")
    except subprocess.TimeoutExpired:
        return dict(err="engine job timed out (2 h)")
    finally:
        try: os.remove(gf)
        except OSError: pass


def run_grid(z, a, comp, kws, points=64, low=False):
    """One wide-grid engine job (or the cached result): the whole curve in one engine call."""
    gk = f"-grid{points}{'L' if low else ''}"
    key = cache_key(z, a, comp, kws) + gk; cf = os.path.join(DATA, "cache", key + ".json")
    if os.path.exists(cf):
        try: return dict(json.load(open(cf)), cached=True)
        except (OSError, ValueError): pass
    args = dict(z=z, a=a, grid=grid_for(points, low), comp=comp, kw=kws, work=os.path.join(DATA, "jobs", uuid.uuid4().hex[:12]),
                smin=SMIN.get((z, a)))
    res = engine_call(args)
    res.pop("log_tail", None)
    if res.get("s_min_mev") is not None: SMIN[(z, a)] = res["s_min_mev"]
    if not res.get("err"):
        os.makedirs(os.path.dirname(cf), exist_ok=True); json.dump(res, open(cf, "w"))
    return dict(res, cached=False)


def start_gridrun(body):
    z, a = int(body["z"]), int(body["a"])
    if not (1 <= z <= 118 and z <= a <= 300): raise ValueError("bad target")
    points = int(body.get("points", 64)); low = bool(body.get("low", False)); bins = int(body.get("bins", 40))
    if points not in POINTS: raise ValueError(f"points: one of {POINTS}")
    if bins not in BINS: raise ValueError(f"bins: one of {BINS}")
    comp = resolve_comp(z, a, body.get("comp", "library")); kws = kw_string(body.get("kw"), body.get("extra"))
    if bins != 40: kws = ";".join([x for x in (kws, f"bins {bins}") if x])
    rid = uuid.uuid4().hex[:10]
    R = RUNS[rid] = dict(id=rid, z=z, a=a, comp=comp, kw=kws, key=cache_key(z, a, comp, kws), n=1, points=[], q=[], done=False, t0=time.time())

    def one():
        try: res = run_grid(z, a, comp, kws, points, low)
        except Exception as ex:  # noqa: BLE001
            res = dict(z=z, a=a, err=f"service: {type(ex).__name__}: {ex}"[:300], cached=False)
        with LOCK:
            R["points"].append(res); R["done"] = True
            for q in R["q"]: q.put(("point", res)); q.put(("done", dict(n=1, wall_s=round(time.time() - R["t0"], 1))))
    pool.submit(one)
    return dict(run=rid, comp=comp, kw=kws, n=1)


def start_run(body):
    z, a = int(body["z"]), int(body["a"])
    es = sorted({float(x) for x in body.get("energies_ev", [])})
    if not es: raise ValueError("no energies")
    if len(es) > 400: raise ValueError("at most 400 energies per run")
    if min(es) < 1e-5 or max(es) > 2e8: raise ValueError("energies must be within 1e-5 eV .. 200 MeV")
    if not (1 <= z <= 118 and z <= a <= 300): raise ValueError("bad target")
    comp = resolve_comp(z, a, body.get("comp", "library")); kws = kw_string(body.get("kw"), body.get("extra"))
    key = cache_key(z, a, comp, kws); rid = uuid.uuid4().hex[:10]
    R = RUNS[rid] = dict(id=rid, z=z, a=a, comp=comp, kw=kws, key=key, n=len(es), points=[], q=[], done=False, t0=time.time())

    def one(e):
        try:
            res = run_point(z, a, comp, kws, key, e)
        except Exception as ex:  # noqa: BLE001  (never leave a run hanging)
            res = dict(z=z, a=a, e_ev=e, err=f"service: {type(ex).__name__}: {ex}"[:300], cached=False)
        with LOCK:
            R["points"].append(res)
            for q in R["q"]: q.put(("point", res))
            if len(R["points"]) == R["n"]:
                R["done"] = True
                for q in R["q"]: q.put(("done", dict(n=R["n"], wall_s=round(time.time() - R["t0"], 1))))
    # cached points are answered at once (not queued behind other runs' jobs); the rest go to the pool in energy order
    cached = [e for e in es if os.path.exists(os.path.join(DATA, "cache", key, ekey(e) + ".json"))]
    for e in cached: one(e)
    for e in [e for e in es if e not in set(cached)]:
        pool.submit(one, e)
    return dict(run=rid, comp=comp, kw=kws, key=key, n=len(es), cached=len(cached))


class Handler(BaseHTTPRequestHandler):
    server_version = "talysworld/1"

    def log_message(self, fmt, *args):  # quiet
        pass

    def _send(self, code, body, ctype="application/json; charset=utf-8"):
        b = body if isinstance(body, bytes) else (json.dumps(body) if not isinstance(body, str) else body).encode()
        self.send_response(code); self.send_header("Content-Type", ctype); self.send_header("Content-Length", str(len(b)))
        self.send_header("Cache-Control", "no-store"); self._cors(); self.end_headers(); self.wfile.write(b)

    def _cors(self):
        o = self.headers.get("Origin", "")
        if o and ORIGINS.match(o):
            self.send_header("Access-Control-Allow-Origin", o); self.send_header("Vary", "Origin")

    def do_OPTIONS(self):  # CORS / private-network preflight from the public site's calculator page
        self.send_response(204); self._cors()
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS"); self.send_header("Access-Control-Allow-Headers", "Content-Type")
        if self.headers.get("Access-Control-Request-Private-Network"): self.send_header("Access-Control-Allow-Private-Network", "true")
        self.send_header("Access-Control-Max-Age", "600"); self.send_header("Content-Length", "0"); self.end_headers()

    def _file(self, path):
        if not os.path.isfile(path): return self._send(404, {"error": "not found"})
        ext = os.path.splitext(path)[1].lower()
        ct = {".html": "text/html; charset=utf-8", ".js": "text/javascript", ".css": "text/css", ".json": "application/json",
              ".svg": "image/svg+xml", ".png": "image/png", ".csv": "text/csv"}.get(ext, "application/octet-stream")
        self._send(200, open(path, "rb").read(), ct)

    def do_GET(self):
        u = urlparse(self.path); q = {k: v[0] for k, v in parse_qs(u.query).items()}
        try:
            # "/" is the site's calculator page (one engine job per curve, live here); the older one-job-per-energy page is /classic
            if u.path in ("/", "/index.html", "/calculator", "/calculator.html"): return self._file(os.path.join(WEB, "calculator.html"))
            if u.path == "/classic": return self._file(os.path.join(HERE, "index.html"))
            if u.path.startswith("/site/"):
                p = inside(SITE, u.path[len("/site/"):])
                if p is None: return self._send(403, {"error": "forbidden"})
                return self._file(p)
            if u.path == "/api/meta":
                return self._send(200, dict(engine=ENGINE_LABEL + (GRIDTOP_NOTE if GRIDTOP else ""), keywords=KEYWORDS, comps=COMPS, library_grid_ev=LIB_GRID,
                                            library=os.path.basename(LIB), workers=pool._max_workers, gridrun=True, points=POINTS, bins=BINS, low_points=len(LOW15), nice=NICE, projectiles=["n"],
                                            nuclides=sorted([k[0], k[1]] for k in LIBRARY)))
            if u.path == "/api/library":
                d = LIBRARY.get((int(q["z"]), int(q["a"])))
                return self._send(200, d or {})
            if u.path == "/api/run":
                R = RUNS.get(q.get("run", ""))
                if not R: return self._send(404, {"error": "no such run"})
                return self._send(200, {k: v for k, v in R.items() if k != "q"})
            if u.path == "/api/stream":
                R = RUNS.get(q.get("run", ""))
                if not R: return self._send(404, {"error": "no such run"})
                qq = queue.Queue()
                with LOCK:
                    old = list(R["points"]); R["q"].append(qq); done = R["done"]
                self.send_response(200); self.send_header("Content-Type", "text/event-stream"); self.send_header("Cache-Control", "no-store")
                self._cors(); self.end_headers()
                try:
                    for p in old: self.wfile.write(f"event: point\ndata: {json.dumps(p)}\n\n".encode())
                    if done: self.wfile.write(f"event: done\ndata: {json.dumps(dict(n=R['n']))}\n\n".encode())
                    self.wfile.flush()
                    while not done:
                        try: ev, data = qq.get(timeout=15)
                        except queue.Empty:
                            self.wfile.write(b": keep-alive\n\n"); self.wfile.flush(); continue
                        self.wfile.write(f"event: {ev}\ndata: {json.dumps(data)}\n\n".encode()); self.wfile.flush()
                        done = ev == "done"
                except (BrokenPipeError, ConnectionResetError):
                    pass
                finally:
                    with LOCK:
                        if qq in R["q"]: R["q"].remove(qq)
                return
            if not u.path.startswith("/api/"):   # the calculator page's own files (web/ first), then the site's style, scripts and data
                for base in (WEB, SITE):
                    p = inside(base, u.path.lstrip("/"))
                    if p is not None and os.path.isfile(p): return self._file(p)
            return self._send(404, {"error": "not found"})
        except (KeyError, ValueError) as ex:
            return self._send(400, {"error": str(ex)})

    def do_POST(self):
        u = urlparse(self.path)
        try:
            body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
            if u.path == "/api/run": return self._send(200, start_run(body))
            if u.path == "/api/gridrun": return self._send(200, start_gridrun(body))
            return self._send(404, {"error": "not found"})
        except (KeyError, ValueError, TypeError) as ex:
            return self._send(400, {"error": str(ex)})


def main():
    global pool, NICE, WARM_SOCK
    ap = argparse.ArgumentParser(); ap.add_argument("--port", type=int, default=8765); ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--workers", type=int, default=3); ap.add_argument("--nice", type=int, default=10)
    ap.add_argument("--no-warm", action="store_true", help="a fresh engine process per job (no warm pool)")
    a = ap.parse_args(); NICE = max(10, a.nice)
    WARM_SOCK = os.path.join(DATA, f"warm-{a.port}.sock")
    if a.no_warm: WARM["fails"] = 99
    if a.host not in ("127.0.0.1", "localhost", "::1"): raise SystemExit("talysworld listens on this machine only (127.0.0.1); never expose it")
    pool = ThreadPoolExecutor(max_workers=max(1, min(MAX_WORKERS, a.workers)))
    os.makedirs(os.path.join(DATA, "cache"), exist_ok=True)
    if not os.path.isdir(os.path.join(DATA, "cc")):
        subprocess.run(["cp", "-a", f"{H}/fastgate_data/cc", os.path.join(DATA, "cc")], check=True)
    load_library()
    print(f"talysworld: {len(LIBRARY)} library nuclides; engine {ENG}; {pool._max_workers} workers at nice {NICE}; "
          f"http://localhost:{a.port}/", flush=True)
    ThreadingHTTPServer((a.host, a.port), Handler).serve_forever()


if __name__ == "__main__":
    main()
