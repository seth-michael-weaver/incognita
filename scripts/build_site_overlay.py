"""DISPLAY-ONLY. Build the "overlay evaluated libraries" comparison data of the website's Data explorer.

    ** These numbers are comparators for the web page and nothing else. Nothing in the engine, the library build, the
    ** benchmarks or the downloads reads them; do not import this script or its output from model-side code.

Libraries shipped (redistribution confirmed): ENDF/B-VIII.1 (US public domain), JEFF-4.0 (CC BY 4.0), TENDL-2025
(CC BY 4.0). JENDL-5 is HELD until its terms for derived tables are confirmed.

For each incident-neutron ENDF-6 file of those libraries (held offline in ~/nucleus/raw/endf, licences in
~/nucleus/raw/MANIFEST.json) and each nuclide the site shows, NJOY RECONR (0 K, 0.5 % tolerance, via openmc.data.njoy)
reconstructs pointwise MT102 (capture), MT16 (n,2n), MT103 (n,p) and MT107 (n,alpha); if MT103/MT107 are absent their
partials MT600-649 / MT800-849 are summed (RECONR does this itself) -- but only when the SOURCE file has MT103/107 or the
continuum member MT649/849; otherwise part of the channel sits in MT5 and the channel is omitted for that library
(checked at "write" time) rather than shown too low. They are reduced to:
  - log-energy bin averages on the site's 64-point grid (data/index.json grid_ev, 1 keV - 20 MeV): bin edges at the
    geometric midpoints between grid points (first/last half-bins mirrored, top clipped at 20 MeV); the average is
    (1/ln(b/a)) * integral sigma(E) dE/E, exact for the lin-lin pointwise data;
  - MACS at the site's 12 kT values: (2/sqrt(pi)) / (kT)^2 * integral sigma(E) E exp(-E/kT) dE (exact on lin-lin).
Rounded to 4 significant digits. Capture in b, everything else in mb.

Output docs/walkthrough/data/lib/<Z>.json, loaded by js/data.js only when the reader ticks the overlay box; never part of
the INCOGNITA CSV/JSON downloads. Input SHA256 (first 16 hex) per file: scripts/build_site_overlay.sources.json.
The build fails if the total exceeds 10 MB or any file exceeds 400 kB.

usage (WSL, env with openmc + njoy):
  ~/micromamba/envs/nucleus-phys/bin/python scripts/build_site_overlay.py reduce [--jobs 4] [--only endfb81:79:197,...]
  ~/micromamba/envs/nucleus-phys/bin/python scripts/build_site_overlay.py write
"""
import argparse, hashlib, io, json, math, os, re, shutil, sys, tempfile, zipfile
from multiprocessing import Pool

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "docs", "walkthrough", "data")
OUT = os.path.join(SITE, "lib")
SRCJ = os.path.join(ROOT, "scripts", "build_site_overlay.sources.json")
RAW = os.path.expanduser("~/nucleus/raw/endf")
WORK = os.path.expanduser("~/siteoverlay_work")  # per-file reduced results (resumable) + NJOY scratch
MAX_TOTAL, MAX_FILE = 10_000_000, 400_000

LIBS = {  # key: (label, directory, licence, citation)
    "endfb8.1": ("ENDF/B-VIII.1", "endfb81", "US public domain",
                 "G. P. A. Nobre et al., Nucl. Data Sheets 202 (2025) 1 (CSEWG, NNDC/BNL)"),
    "jeff4.0": ("JEFF-4.0", "jeff40", "CC BY 4.0",
                "JEFF-4.0 Evaluated Data: neutron data, OECD/NEA (2025), doi:10.82555/e9ajn-a3p20"),
    "tendl2025": ("TENDL-2025", "tendl2025", "CC BY 4.0",
                  "A. J. Koning, D. Rochman, J.-Ch. Sublet et al., Nucl. Data Sheets 155 (2019) 1; TENDL-2025, tendl.web.psi.ch"),
}
# HELD: "jendl5" (JENDL-5, JAEA, "open, attribution") -- redistribution of derived tables not yet confirmed.
REACT = {"cap": (102, range(0, 0), 1.0), "n2n": (16, range(0, 0), 1e3), "np": (103, range(600, 650), 1e3), "na": (107, range(800, 850), 1e3)}


def sig(v, n=4):
    if v is None or not math.isfinite(v):
        return None
    return 0 if v == 0 else float(f"{v:.{n}g}")


def site_keys():
    idx = json.load(open(os.path.join(SITE, "index.json")))
    keys = {(r[0], r[1]) for r in idx["rows"]} | {(z, 0) for z in idx["natural"]}
    return idx["grid_ev"], idx["kT_keV"], keys


def inputs():
    """[(lib, Z, A, path)] for ground-state targets of the shipped libraries."""
    out = []
    for lib, (_, d, _, _) in LIBS.items():
        for fn in sorted(os.listdir(os.path.join(RAW, d, "n"))):
            m = re.match(r"n-(\d{3})_([A-Za-z]+)_(\d{3})\.endf$", fn) or re.match(r"n_(\d{3})-([A-Za-z]+)-(\d+)_\d+\.zip$", fn)
            if m:  # metastable targets (…m1.endf, …-116M_…zip) do not match and are skipped
                out.append((lib, int(m.group(1)), int(m.group(3)), os.path.join(RAW, d, "n", fn)))
    return out


def sha16(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()[:16]


def raw_mf3(path):
    """set of MF3 MTs in the source ENDF-6 file (zip or plain), read from the MF/MT columns."""
    if path.endswith(".zip"):
        with zipfile.ZipFile(path) as z:
            lines = z.read(z.namelist()[0]).decode("latin-1").splitlines()
    else:
        lines = open(path, encoding="latin-1").read().splitlines()
    return {int(l[72:75]) for l in lines if len(l) >= 75 and l[70:72] == " 3" and l[72:75].strip().isdigit()}


def tab1(ev, mt):
    from openmc.data import endf
    f = io.StringIO(ev.section[3, mt]); endf.get_head_record(f); _, xs = endf.get_tab1_record(f)
    return np.asarray(xs.x, float), np.asarray(xs.y, float)


def binavg(e, s, edges):
    """(1/ln(b/a)) ∫ σ dE/E per bin, exact for lin-lin σ(E); σ = 0 outside the tabulated range."""
    out = []
    for a, b in zip(edges[:-1], edges[1:]):
        lo, hi = max(a, e[0]), min(b, e[-1])
        if hi <= lo:
            out.append(0.0); continue
        i0, i1 = np.searchsorted(e, lo, "right"), np.searchsorted(e, hi, "left")
        x = np.concatenate(([lo], e[i0:i1], [hi])); y = np.interp(x, e, s)
        x0, x1, y0, y1 = x[:-1], x[1:], y[:-1], y[1:]
        ok = x1 > x0
        k = np.where(ok, (y1 - y0) / np.where(ok, x1 - x0, 1), 0)
        I = np.sum(np.where(ok, (y0 - k * x0) * np.log(np.where(ok, x1 / x0, 1)) + k * (x1 - x0), 0))
        out.append(I / math.log(b / a))
    return out


def macs(e, s, kts_ev):
    """(2/√π)/(kT)² ∫ σ E e^(−E/kT) dE, exact on lin-lin segments."""
    x0, x1, y0, y1 = e[:-1], e[1:], s[:-1], s[1:]
    ok = x1 > x0
    b = np.where(ok, (y1 - y0) / np.where(ok, x1 - x0, 1), 0); a = y0 - b * x0
    res = []
    for T in kts_ev:
        F1 = lambda x: -T * np.exp(-x / T) * (x + T)
        F2 = lambda x: -T * np.exp(-x / T) * (x * x + 2 * T * x + 2 * T * T)
        I = np.sum(np.where(ok, a * (F1(x1) - F1(x0)) + b * (F2(x1) - F2(x0)), 0))
        res.append(2 / math.sqrt(math.pi) * I / T ** 2)
    return res


def reduce_one(job):
    lib, Z, A, path, edges, kts = job
    dst = os.path.join(WORK, lib, f"{Z}_{A}.json")
    if os.path.exists(dst):
        return dst, "cached"
    import openmc.data
    from openmc.data import endf
    os.environ["PATH"] = os.path.dirname(sys.executable) + os.pathsep + os.environ.get("PATH", "")  # njoy lives beside python in the env
    os.makedirs(os.path.dirname(dst), exist_ok=True); os.makedirs(os.path.join(WORK, "scr"), exist_ok=True)
    d = tempfile.mkdtemp(dir=os.path.join(WORK, "scr")); cwd = os.getcwd()
    try:
        src = path
        if path.endswith(".zip"):
            with zipfile.ZipFile(path) as z:
                nm = z.namelist()[0]; src = os.path.join(d, "tape"); open(src, "wb").write(z.read(nm))
        os.chdir(d)
        openmc.data.njoy.make_pendf(src, "pendf", error=0.005, stdout=False)
        os.chdir(cwd)
        ev = endf.Evaluation(os.path.join(d, "pendf"))
        have = {mt for (mf, mt) in ev.section if mf == 3}
        rec = {"lib": lib, "Z": Z, "A": A, "sha16": sha16(path), "file": os.path.relpath(path, RAW), "mts": {}}
        for k, (mt, parts, scale) in REACT.items():
            if mt in have:
                e, s = tab1(ev, mt); rec["mts"][k] = mt
            else:
                pm = [p for p in parts if p in have]
                if not pm:
                    continue
                tabs = [tab1(ev, p) for p in pm]
                e = np.unique(np.concatenate([t[0] for t in tabs]))
                s = sum(np.interp(e, t[0], t[1], left=0, right=0) for t in tabs); rec["mts"][k] = f"sum MT{pm[0]}-{pm[-1]}"
            m = e <= 2.0e7 * (1 + 1e-9)
            e, s = e[m], s[m]
            if len(e) < 2 or not np.any(s > 0):
                continue
            rec[k] = [sig(v * scale) for v in binavg(e, s, edges)]
            if k == "cap":
                rec["macs"] = [sig(v * 1e3) for v in macs(e, s, kts)]
        json.dump(rec, open(dst, "w"))
        return dst, "ok"
    except Exception as ex:  # noqa: BLE001
        os.chdir(cwd)
        return dst, f"fail {ex!r}"[:300]
    finally:
        shutil.rmtree(d, ignore_errors=True)


def edges_of(grid):
    g = np.asarray(grid, float); mid = np.sqrt(g[:-1] * g[1:])
    e = np.concatenate(([g[0] ** 2 / mid[0]], mid, [g[-1] ** 2 / mid[-1]]))
    e[-1] = min(e[-1], 2.0e7)
    return e


def cmd_reduce(a):
    grid, kt, keys = site_keys()
    edges, kts = edges_of(grid), [k * 1e3 for k in kt]
    jobs = [(lib, Z, A, p, edges, kts) for lib, Z, A, p in inputs() if (Z, A) in keys]
    if a.only:
        want = {tuple(x.split(":")) for x in a.only.split(",")}
        jobs = [j for j in jobs if (j[0], str(j[1]), str(j[2])) in want]
    jobs.sort(key=lambda j: -os.path.getsize(j[3]))  # big files first, so the tail is short
    print(f"{len(jobs)} files to reduce", flush=True)
    with Pool(a.jobs) as pool:
        for i, (dst, st) in enumerate(pool.imap_unordered(reduce_one, jobs, chunksize=1)):
            if st != "cached":
                print(f"[{i + 1}/{len(jobs)}] {os.path.relpath(dst, WORK)} {st}", flush=True)


def compact(o):
    s = json.dumps(o, separators=(",", ":"), ensure_ascii=False)
    return re.sub(r"e([+-])0*(\d)", lambda m: "e" + ("-" if m.group(1) == "-" else "") + m.group(2), s)


def cmd_write(a):
    grid, kt, keys = site_keys()
    byz, src, fails = {}, {}, []
    for lib in LIBS:
        dd = os.path.join(WORK, lib)
        for fn in sorted(os.listdir(dd)) if os.path.isdir(dd) else []:
            r = json.load(open(os.path.join(dd, fn)))
            Z, A = r["Z"], r["A"]
            if (Z, A) not in keys:
                continue
            if r.get("np") or r.get("na"):  # (n,p)/(n,alpha) only when the source file gives the sum or the continuum partial
                raw = raw_mf3(os.path.join(RAW, r["file"]))
                for k, (mt, parts, _) in REACT.items():
                    if r.get(k) and parts and mt not in raw and parts[-1] not in raw:
                        r.pop(k); r["mts"][k] = f"omitted: MT{mt} and MT{parts[-1]} absent from the file (rest in MT5)"
            ent = {k: r[k] for k in ("cap", "n2n", "np", "na", "macs") if r.get(k)}
            if ent:
                byz.setdefault(Z, {}).setdefault(str(A) if A else "nat", {})[lib] = ent
            src[f"{lib}/{Z}/{A}"] = [r["file"], r["sha16"], r["mts"]]
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    tot, big, nl = 0, 0, 0
    for Z, nuc in sorted(byz.items()):
        used = sorted({l for v in nuc.values() for l in v}, key=list(LIBS).index)
        libs = {l: {"label": LIBS[l][0], "lic": LIBS[l][2], "cite": LIBS[l][3]} for l in used}
        s = compact({"Z": Z, "display_only": "Evaluated-library comparators for display; not used by INCOGNITA.",
                     "units": {"cap": "b", "n2n": "mb", "np": "mb", "na": "mb", "macs": "mb"}, "libs": libs, "nuc": nuc})
        open(os.path.join(OUT, f"{Z}.json"), "w", encoding="utf-8").write(s)
        n = len(s.encode()); tot += n; big = max(big, n); nl += sum(len(v) for v in nuc.values())
        if n > MAX_FILE:
            fails.append(f"lib/{Z}.json is {n} bytes > {MAX_FILE}")
    if tot > MAX_TOTAL:
        fails.append(f"total {tot} bytes > {MAX_TOTAL}")
    json.dump({"note": "DISPLAY-ONLY overlay inputs (scripts/build_site_overlay.py): lib/Z/A -> [file under ~/nucleus/raw/endf, sha256[:16], MTs used]",
               "held": {"jendl5": "JENDL-5: redistribution of derived tables not yet confirmed"}, "files": src},
              open(SRCJ, "w"), separators=(",", ":"))
    print(f"{nl} nuclide-libraries, {len(byz)} element files, {tot / 1e6:.2f} MB total, largest {big / 1e3:.0f} kB")
    if fails:
        sys.exit("BUDGET GATE FAILED: " + "; ".join(fails))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd", required=True)
    r = sp.add_parser("reduce"); r.add_argument("--jobs", type=int, default=4); r.add_argument("--only", default="")
    sp.add_parser("write")
    a = ap.parse_args()
    (cmd_reduce if a.cmd == "reduce" else cmd_write)(a)
