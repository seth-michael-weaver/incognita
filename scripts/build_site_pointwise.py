"""DISPLAY-ONLY (like build_site_overlay.py): pointwise 0 K comparator curves below 1 keV for the site's Data explorer.

For each (library, nuclide) that the site's overlay already shows (~/siteoverlay_work/<lib>/<Z>_<A>.json), NJOY RECONR
reconstructs the ENDF-6 file at 0 K with err = errmax = 1e-4 (0.01 %; the production deck 1e-3 / errmax 10x was up to 1.8 % off pointwise in the resolved range); MT102 (and MT103 / MT107 where the overlay shows that channel)
between EMIN and 1 keV is thinned to at most NMAX points (5 per resonance peak, up to NMAX_DENSE, for dense nuclides) by greedy max-deviation refinement in log-log space and written
to ~/koningov_data/pw/<lib>/<Z>_<A>.json. Resumable.

Nothing in the engine, the library build, the benchmarks or the downloads reads these numbers.

usage (WSL, env with njoy):
  ~/micromamba/envs/nucleus-phys/bin/python scripts/build_site_pointwise.py run [--chans cap,np,na] [--only lib:Z:A,...] [--guard]
  ... jobs JOBS.json; then on any machine with the ENDF files: [NJOY=...] python build_site_pointwise.py farm --jobfile PART.json --wmax N
  ~/micromamba/envs/nucleus-phys/bin/python scripts/build_site_pointwise.py write
"""
import argparse, json, math, os, re, shutil, subprocess, sys, tempfile, time, zipfile

import numpy as np

RAW = os.path.expanduser(os.environ.get("PW_RAW", "~/nucleus/raw/endf"))
OVW = os.path.expanduser("~/siteoverlay_work")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.expanduser(os.environ.get("PW_WORK", "~/koningov_data") + "/pw_e4")
SCR = os.path.expanduser(os.environ.get("PW_WORK", "~/koningov_data") + "/scr")
NJOY = os.environ.get("NJOY") or os.path.expanduser("~/micromamba/envs/nucleus-phys/bin/njoy")
DIRS = {"endfb8.1": "endfb81", "jeff4.0": "jeff40", "tendl2025": "tendl2025"}
EMIN, EMAX, NMAX, TOL = 0.01, 1000.0, 500, 1e-4   # TOL: stop refining when the worst log10 deviation is below ~0.02 %
ERR = 1e-4  # RECONR err = errmax
NMAX_DENSE = 5000  # budget cap for nuclides with many resonances below 1 keV (see budget())
MTS = {"cap": 102, "np": 103, "na": 107}


def inputs():
    out = []
    for lib, d in DIRS.items():
        for fn in sorted(os.listdir(os.path.join(RAW, d, "n"))):
            m = re.match(r"n-(\d{3})_([A-Za-z]+)_(\d{3})\.endf$", fn) or re.match(r"n_(\d{3})-([A-Za-z]+)-(\d+)_\d+\.zip$", fn)
            if m:
                out.append((lib, int(m.group(1)), int(m.group(3)), os.path.join(RAW, d, "n", fn)))
    return out


def read_mf3(path, mts):
    """{mt: (E, sigma)} for MF3 sections of a PENDF, read by columns (fast, no full parse)."""
    want = {mt: [] for mt in mts}
    with open(path, encoding="latin-1") as f:
        for l in f:
            if len(l) < 75 or l[70:72] != " 3":
                continue
            mt = int(l[72:75]) if l[72:75].strip().isdigit() else -1
            if mt in want:
                want[mt].append(l[:66])
    res = {}
    for mt, ls in want.items():
        if len(ls) < 4:
            continue
        # HEAD, TAB1 CONT (NR NP), NR interpolation pairs, then NP pairs; last line is SEND-less (SEND has MT 0)
        nr, npt = int(ls[1][44:55]), int(ls[1][55:66])
        k = 2 + (2 * nr + 5) // 6
        vals = []
        for l in ls[k:]:
            for j in range(6):
                s = l[11 * j:11 * j + 11].strip()
                if s:
                    vals.append(float(re.sub(r"(?<=\d)([+-])(\d+)$", r"e\1\2", s)))
        v = np.array(vals[:2 * npt]).reshape(-1, 2)
        res[mt] = (v[:, 0], v[:, 1])
    return res


def thin(e, s, nmax=NMAX, tol=TOL):
    """Greedy max-deviation refinement (Douglas-Peucker with a point budget) on (log10 E, log10 sigma).
    Seeds: the ends and 0.0253 eV. Each step inserts the point of the largest vertical log deviation from the current
    polyline, so resonance peaks and interference dips are taken first. Returns indices into e."""
    m = (e >= EMIN * (1 - 1e-9)) & (e <= EMAX * (1 + 1e-9)) & (s > 0)
    idx_all = np.nonzero(m)[0]
    if len(idx_all) < 2:
        return idx_all
    x, y = np.log10(e[idx_all]), np.log10(s[idx_all])
    n = len(x)
    keep = {0, n - 1, int(np.argmin(np.abs(x - math.log10(0.0253))))}
    import heapq
    heap = []

    def push(a, b):
        if b - a < 2:
            return
        xs, ys = x[a + 1:b], y[a + 1:b]
        yl = y[a] + (y[b] - y[a]) * (xs - x[a]) / (x[b] - x[a]) if x[b] > x[a] else np.full_like(xs, y[a])
        d = np.abs(ys - yl); j = int(np.argmax(d))
        heapq.heappush(heap, (-float(d[j]), a, b, a + 1 + j))

    ks = sorted(keep)
    for a, b in zip(ks[:-1], ks[1:]):
        push(a, b)
    while heap and len(keep) < nmax:
        d, a, b, j = heapq.heappop(heap)
        if -d < tol:
            break
        keep.add(j); push(a, j); push(j, b)
    return idx_all[sorted(keep)]


ECUT = 2000.0


def fnum(v):
    """ENDF 11-column float"""
    m, e = f"{v:.6e}".split("e"); return f"{m}{int(e):+d}".rjust(11)

def cut_rrr(path):
    """Speed only: if the first resolved range of the file spans ECUT (2 keV), set its upper end EH to ECUT in MF2/MT151,
    so RECONR builds its grid only up to 2 keV. Every resonance stays in the list, so the cross section below 1 keV is
    unchanged (checked against the uncut run on U-238, Gd-157, Au-197). Returns 1 if cut, else 0."""
    L = open(path, encoding="latin-1").read().split(chr(10))
    st = [i for i, l in enumerate(L) if len(l) >= 75 and l[70:75] == " 2151"]
    if not st:
        return 0
    i = st[0] + 2  # HEAD, isotope CONT, then the first range CONT: EL EH LRU LRF NRO NAPS
    el, eh = (float(re.sub(r"(?<=\d)([+-])(\d+)$", r"e\1\2", L[i][k:k + 11].strip())) for k in (0, 11))
    if int(L[i][22:33]) != 1 or not (el < ECUT < eh):
        return 0
    L[i] = L[i][:11] + fnum(ECUT) + L[i][22:]
    open(path, "w", encoding="latin-1").write(chr(10).join(L))
    return 1





def is_done(dst):
    """an output exists, and is not one made with the old flat 500-point budget that already shows >= 90 resonance peaks
    in its thinned points (those may have more than 100 and are redone with budget())"""
    if not os.path.exists(dst):
        return False
    try:
        r = json.load(open(dst))
    except Exception:  # noqa: BLE001
        return False
    from scipy.signal import find_peaks
    for v in r.values():
        if isinstance(v, dict) and "e" in v and "npk" not in v and len(v["e"]) >= NMAX:
            s = np.log10(np.maximum(np.asarray(v["s"], float), 1e-30))
            if len(find_peaks(s, prominence=math.log10(2))[0]) >= 90:
                return False
    return True


def budget(e, s):
    """(number of resonance peaks, point budget). A peak is a local maximum at least 2x above the higher of its two
    flanking minima (scipy prominence >= log10 2 on log10 sigma), between EMIN and EMAX. The budget is NMAX (500), or
    5 points per peak for nuclides with more than 100 peaks, up to NMAX_DENSE (5000): checked against the full RECONR
    curve, 500 points kept every peak of Au-197 and Gd-155 within 10 %, but only 29 % (U-235) and 68 % (Pu-239)."""
    from scipy.signal import find_peaks
    m = (e >= EMIN) & (e <= EMAX) & (s > 0)
    if m.sum() < 3:
        return 0, NMAX
    npk = len(find_peaks(np.log10(s[m]), prominence=math.log10(2))[0])
    return npk, int(min(NMAX_DENSE, max(NMAX, 5 * npk)))


def sig(v, n):
    return 0 if v == 0 else float(f"{v:.{n}g}")


def one(job):
    lib, Z, A, path, chans = job
    dst = os.path.join(OUT, lib, f"{Z}_{A}.json")
    if is_done(dst):
        return dst, "cached", 0
    os.makedirs(os.path.dirname(dst), exist_ok=True); os.makedirs(SCR, exist_ok=True)
    d = tempfile.mkdtemp(dir=SCR); t0 = time.time()
    try:
        if path.endswith(".zip"):
            with zipfile.ZipFile(path) as z:
                open(os.path.join(d, "tape20"), "wb").write(z.read(z.namelist()[0]))
        else:
            shutil.copy(path, os.path.join(d, "tape20"))
        with open(os.path.join(d, "tape20"), encoding="latin-1") as f:
            f.readline(); mat = int(f.readline()[66:70])
        ncut = cut_rrr(os.path.join(d, "tape20"))
        inp = f"reconr\n20 22\n'koningov 0K pointwise'/\n{mat} 0 0/\n{ERR} 0. {ERR}/\n0/\nstop\n"
        r = subprocess.run([NJOY], input=inp, cwd=d, capture_output=True, text=True, timeout=7200)
        if r.returncode != 0 or not os.path.exists(os.path.join(d, "tape22")):
            return dst, f"fail njoy rc={r.returncode} {r.stdout[-300:]!r}", time.time() - t0
        tabs = read_mf3(os.path.join(d, "tape22"), [MTS[c] for c in chans])
        rec = {"lib": lib, "Z": Z, "A": A, "file": os.path.relpath(path, RAW), "err": ERR, "errmax": ERR, "T": 0, "emin": EMIN, "emax": EMAX, "rrr_cut": ncut}
        for c in chans:
            if MTS[c] not in tabs:
                continue
            e, s = tabs[MTS[c]]
            npk, nmax = budget(e, s)
            ii = thin(e, s, nmax=nmax)
            if len(ii) < 2:
                continue
            # thermal value: lin-lin from the full pointwise data
            rec[c] = {"n_full": int(np.sum((e >= EMIN) & (e <= EMAX))), "npk": npk, "nmax": nmax, "th": sig(float(np.interp(0.0253, e, s)), 5),
                      "e": [sig(float(v), 6) for v in e[ii]], "s": [sig(float(v), 4) for v in s[ii]]}
        json.dump(rec, open(dst + ".tmp", "w"), separators=(",", ":")); os.replace(dst + ".tmp", dst)
        return dst, "ok", time.time() - t0
    except Exception as ex:  # noqa: BLE001
        return dst, f"fail {ex!r}"[:300], time.time() - t0
    finally:
        shutil.rmtree(d, ignore_errors=True)


def compact(o):
    s = json.dumps(o, separators=(",", ":"), ensure_ascii=False)
    return re.sub(r"e([+-])0*(\d)", lambda m: "e" + ("-" if m.group(1) == "-" else "") + m.group(2), s)


def cmd_write():
    """data/lib/pw/<Z>/<A|nat>.json for every (nuclide, library, channel) that data/lib/<Z>.json shows, plus
    data/lib/pw/index.json (the nuclides that have a file). Budget gate: 150 MB total, 400 kB per file."""
    site = os.path.join(ROOT, "docs", "walkthrough", "data")
    dst = os.path.join(site, "lib", "pw")
    shutil.rmtree(dst, ignore_errors=True); os.makedirs(dst)
    keys, tot, big, ncurve, per_lib = [], 0, 0, 0, {}
    for fn in sorted(os.listdir(os.path.join(site, "lib")), key=lambda s: (len(s), s)):
        if not fn.endswith(".json"):
            continue
        lz = json.load(open(os.path.join(site, "lib", fn), encoding="utf-8")); Z = lz["Z"]
        for key, libs in lz["nuc"].items():
            A = 0 if key == "nat" else int(key); ent = {}
            for lib, v in libs.items():
                f = os.path.join(OUT, lib, f"{Z}_{A}.json")
                if not os.path.exists(f):
                    continue
                r = json.load(open(f)); e = {}
                for c in ("cap", "np", "na"):
                    if v.get(c) and r.get(c):  # only channels the overlay itself shows (np/na gate of build_site_overlay.py)
                        e[c] = {"e": r[c]["e"], "s": r[c]["s"], "th": r[c]["th"], "n_full": r[c]["n_full"], "nmax": r[c].get("nmax", NMAX)}
                        ncurve += 1; per_lib[(lib, c)] = per_lib.get((lib, c), 0) + 1
                if e:
                    ent[lib] = e
            if not ent:
                continue
            os.makedirs(os.path.join(dst, str(Z)), exist_ok=True)
            s = compact({"Z": Z, "A": A, "display_only": "Evaluated-library comparators for display; not used by INCOGNITA.",
                         "what": "pointwise, 0 K (NJOY RECONR, err = errmax = 1e-4), thinned by greedy max-deviation refinement in log-log space",
                         "emin_ev": EMIN, "emax_ev": EMAX, "nmax": NMAX, "units": {"e": "eV", "cap": "b", "np": "b", "na": "b"}, "libs": ent})
            open(os.path.join(dst, str(Z), f"{key}.json"), "w", encoding="utf-8").write(s)
            n = len(s.encode()); tot += n; big = max(big, n); keys.append(f"{Z}/{key}")
    open(os.path.join(dst, "index.json"), "w").write(compact({"nmax": NMAX, "emin_ev": EMIN, "emax_ev": EMAX, "keys": keys}))
    print(f"{len(keys)} nuclide files, {ncurve} curves {per_lib}, {tot / 1e6:.2f} MB, largest {big / 1e3:.1f} kB")
    if tot > 150e6 or big > 400e3:
        sys.exit("BUDGET GATE FAILED")


def all_jobs(chans):
    jobs = []
    for lib, Z, A, p in inputs():
        f = os.path.join(OVW, lib, f"{Z}_{A}.json")
        if not os.path.exists(f):
            continue
        r = json.load(open(f))
        ch = [c for c in chans if r.get(c)]
        if ch:
            jobs.append([lib, Z, A, os.path.relpath(p, RAW), ch, os.path.getsize(p)])
    order = list(DIRS)
    jobs.sort(key=lambda j: (order.index(j[0]), -j[5]))
    return jobs


def job_of(j):
    return (j[0], j[1], j[2], os.path.join(RAW, j[3]), j[4])


def free_cores():
    """cores not busy: ncpu minus the 1-minute load average (macOS sysctl or Linux /proc)"""
    try:
        if sys.platform == "darwin":
            n = int(subprocess.run(["sysctl", "-n", "hw.ncpu"], capture_output=True, text=True).stdout)
            la = float(subprocess.run(["sysctl", "-n", "vm.loadavg"], capture_output=True, text=True).stdout.strip("{} \n").split()[0])
        else:
            n, la = os.cpu_count(), os.getloadavg()[0]
        return n, la
    except Exception:  # noqa: BLE001
        return 1, 0.0


def farm(jobs, wmax):
    """Worker pool sized to the free cores, re-checked every minute: W = clamp(floor(ncpu - (load - own)), 1, wmax).
    Each job is a separate 'one' subprocess (nice is inherited), so the pool can shrink as other jobs' load rises."""
    todo = [j for j in jobs if not is_done(os.path.join(OUT, j[0], f"{j[1]}_{j[2]}.json"))]
    run, W, tchk, t0, done = [], 1, 0, time.time(), 0
    print(f"{len(todo)} to do of {len(jobs)}", flush=True)
    while todo or run:
        if time.time() - tchk > 60:
            n, la = free_cores(); W = max(1, min(wmax, int(n - max(0.0, la - len(run))))); tchk = time.time()
            print(f"{time.strftime('%H:%M:%S')} ncpu {n} load {la:.1f} mine {len(run)} -> W {W}; done {done}, left {len(todo)}", flush=True)
        for p in [p for p in run if p.poll() is not None]:
            run.remove(p); done += 1
        while todo and len(run) < W:
            j = todo.pop(0)
            run.append(subprocess.Popen([sys.executable, os.path.abspath(__file__), "one", json.dumps(j)]))
        time.sleep(0.5)
    print(f"DONE {done} jobs in {time.time() - t0:.0f} s", flush=True)
    open(os.path.join(os.path.dirname(OUT), "DONE"), "w").write(f"{done} {time.time() - t0:.0f}\n")


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("cmd"); ap.add_argument("arg", nargs="?"); ap.add_argument("--only", default="")
    ap.add_argument("--chans", default="cap"); ap.add_argument("--jobfile", default=""); ap.add_argument("--wmax", type=int, default=1)
    ap.add_argument("--guard", action="store_true", help="laptop: pause while Windows RAM < 3 GB or C: < 12 GB")
    a = ap.parse_args()
    if a.cmd == "write":
        return cmd_write()
    if a.cmd == "jobs":  # the job list, for farming out to other machines
        return json.dump(all_jobs(a.chans.split(",")), open(a.arg, "w"))
    if a.cmd == "one":
        dst, st, dt = one(job_of(json.loads(a.arg)))
        return print(f"{os.path.relpath(dst, OUT)} {st} {dt:.1f}s", flush=True)
    jobs = json.load(open(a.jobfile)) if a.jobfile else all_jobs(a.chans.split(","))
    if a.only:
        want = {tuple(x.split(":")) for x in a.only.split(",")}
        jobs = [j for j in jobs if (j[0], str(j[1]), str(j[2])) in want]
    if a.cmd == "farm":
        return farm(jobs, a.wmax)
    print(f"{len(jobs)} files", flush=True)
    # one NJOY at a time; with --guard, every 20 files the Windows host is checked (free RAM >= 3 GB, C: >= 12 GB), else wait
    for i, j in enumerate(jobs):
        while a.guard and i % 20 == 0:
            try:
                o = subprocess.run(["powershell.exe", "-NoProfile", "-c", "[math]::Round((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1MB,2); [math]::Round((Get-PSDrive C).Free/1GB,2)"],
                                   capture_output=True, text=True, timeout=120).stdout.split()
                ram, disk = float(o[0].replace(",", ".")), float(o[1].replace(",", "."))
            except Exception as ex:  # noqa: BLE001
                ram, disk = 99, 99; print("guard check failed", ex, flush=True)
            if ram >= 3 and disk >= 12:
                break
            print(f"PAUSE: RAM {ram} GB, C: {disk} GB", flush=True); time.sleep(120)
        dst, st, dt = one(job_of(j))
        if st != "cached":
            print(f"[{i + 1}/{len(jobs)}] {os.path.relpath(dst, OUT)} {st} {dt:.1f}s", flush=True)
    open(os.path.join(os.path.dirname(OUT), "DONE"), "w").write(f"{len(jobs)}\n")


if __name__ == "__main__":
    main()
