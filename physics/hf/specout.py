"""SPECOUT: outgoing spectra (and, through `physics.hf.specang`, angular distributions and DDX) of the C path, OUTPUT ONLY.

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

TALYS routines ported here (file:line of the subroutine statement):
    compemission.f90:1 (compemission) -- the emission spectrum of every mother bin of a cascade nucleus from
                                         mcontrib(type, nex, nexout) and mpecontrib(type, nex, nexout)
    multiple.f90:693-713              -- xscomp / xsmpreeq accumulated over every cascade nucleus
    spectra.f90:1 (spectra)           -- xssumout = xspreeq + xsmpreeq + xscomp (+ xsgr and the discrete lines)

Switch: `INCOGNITA_SPECOUT` = 1/y/yes/on (default unset = nothing installed, no buffer, no call).

How it is fed (none of it reads back into the engine):
* C path: `native/engine_decay.c` `ce_set_specsink` registers `_SINK`; `walk_nucleus` then gives `nx_walk` two extra
  buffers (pp[153] mcontrib, pp[154] mpecontrib) that it only ever adds to, next to the very additions it makes to the
  daughters' populations, and hands them over with the nucleus's grids after a successful walk. `cascade_only` hands
  over its discrete gamma lines.
* Python walks (`emission.multiple`: numpy walk, tensor walk, `_apply_mpe`, `_apply_leftover`, gamma cascade) call
  `acc_*` with the same quantities; `multiple_native` (the Python-driven nx_walk) passes the same C buffers.
* Per incident energy, `engine_c.cases` (and `engine.ChainedFull`) call `begin_energy` / `begin_attempt` (a regrown or
  fallen-back cascade starts the walks over) / `end_energy`; `binspec.record` adds the binary spectra.

Spectrum convention (TALYS's): `egrid(nen)` is the ejectile's outgoing (channel) energy; spectra in mb/MeV on egrid;
discrete lines as (E, mb). `mcontrib` here is TALYS's: compound feeding + multiple pre-equilibrium (`fracmpe` splits it).

Test: tests/hf/test_specout.py

Task: T10 (physics/hf/CONTRACT.md §7; Incognita extension, output only). Acceptance test: NONE-PUBLIC.
"""

from __future__ import annotations

import ctypes
import os

import numpy as np

PARNAME = ("g", "n", "p", "d", "t", "h", "a")
PARZ = (0, 0, 1, 1, 1, 2, 2)
PARN = (0, 1, 0, 1, 2, 1, 2)

# finished energies of the current run (one dict per kept incident energy), and the energy being built
ENERGIES: list[dict] = []
_CUR: dict | None = None
RUN: dict | None = None  # the run's target: Zc, Ac (compound), k0, and the run-level angular results
_ACC: dict = {}  # Python walks: (zc, nc) -> {"mc": {t: {nex: vec}}, "mpe": {...}}


def enabled() -> bool:
    """Incognita extension.

    TALYS: (none -- Incognita extension, not a TALYS routine)
    Test: none in the public suite
    """
    return os.environ.get("INCOGNITA_SPECOUT", "").strip().lower() in ("1", "y", "yes", "on")


def active() -> bool:
    """An energy is being recorded (the switch is on and the engine is inside a kept energy).

    TALYS: (none -- Incognita extension, not a TALYS routine)
    Test: none in the public suite
    """
    return _CUR is not None


def reset() -> None:
    """Start a new run (one target): drop everything recorded.

    TALYS: (none -- Incognita extension, not a TALYS routine)
    Test: none in the public suite
    """
    global _CUR, RUN
    from physics.hf import specang

    specang._DWBA.clear()
    from physics.hf.ecis import angular

    angular._GEO.clear()
    ENERGIES.clear()
    _ACC.clear()
    _CUR = None
    RUN = None
    from physics.hf.emission import binspec

    binspec.LAST.clear()


# ---------------------------------------------------------------- C sink
_SINK_T = ctypes.CFUNCTYPE(None, ctypes.POINTER(ctypes.c_int64), ctypes.POINTER(ctypes.c_uint64))


def _arr(addr: int, n: int) -> np.ndarray:
    if not addr or n <= 0:
        return np.zeros(max(n, 0))
    return np.ctypeslib.as_array(ctypes.cast(addr, ctypes.POINTER(ctypes.c_double)), shape=(n,)).copy()


def _c_sink(iv, pv):
    try:
        zc, nc, xrows, maxex, nlast = (int(iv[k]) for k in range(5))
        rec = dict(zc=zc, nc=nc, maxex=maxex, nlast=nlast, ex=_arr(pv[0], xrows), dex=_arr(pv[1], xrows),
                   sep=_arr(pv[2], 7), types={}, lines_only=bool(iv[26]), src="c")
        for t in range(7):
            dr = int(iv[5 + t])
            if not dr:
                continue
            mc = _arr(pv[17 + t], xrows * dr).reshape(xrows, dr)
            mpe = _arr(pv[24 + t], xrows * dr).reshape(xrows, dr) if pv[24 + t] else np.zeros((xrows, dr))
            if t == 0:
                ex_d, dex_d, nl_d, mx_d = rec["ex"], rec["dex"], nlast, maxex
            else:
                ex_d, dex_d, nl_d, mx_d = _arr(pv[3 + t], dr), _arr(pv[10 + t], dr), int(iv[12 + t]), int(iv[19 + t])
            rec["types"][t] = dict(mc=mc, mpe=mpe, ex=ex_d, dex=dex_d, nlast=nl_d, maxex=mx_d)
        _put(rec)
    except Exception as exc:  # noqa: BLE001 -- output only: never let a recorder error reach the engine
        if _CUR is not None:
            _CUR.setdefault("errors", []).append(f"c_sink {type(exc).__name__}: {exc}")


_SINK = _SINK_T(_c_sink)


def sync_c(so) -> None:
    """Register (or clear) the C sink on libengdecay `so` per the switch; called once per run by engine_c.

    TALYS: (none -- Incognita extension, not a TALYS routine)
    Test: none in the public suite
    """
    if so is None or not hasattr(so, "ce_set_specsink"):
        return
    so.ce_set_specsink.argtypes = [ctypes.c_void_p]
    so.ce_set_specsink.restype = None
    so.ce_set_specsink(ctypes.cast(_SINK, ctypes.c_void_p) if enabled() else None)


def c_buffers(xrows: int, drows: dict[int, int]):
    """The pp[153..155] buffers `multiple_native._Walk` hands nx_walk: (keep-alive list, mc ptr array, mpe ptr array,
    strides, mc dict, mpe dict).

    TALYS: (none -- Incognita extension, not a TALYS routine)
    Test: none in the public suite
    """
    mc = {t: np.zeros((xrows, dr)) for t, dr in drows.items()}
    mpe = {t: np.zeros((xrows, dr)) for t, dr in drows.items() if t in (1, 2)}
    pm = np.zeros(7, np.uint64)
    pe = np.zeros(7, np.uint64)
    st = np.zeros(7, np.int64)
    for t, a in mc.items():
        pm[t] = a.ctypes.data
        st[t] = a.shape[1]
    for t, a in mpe.items():
        pe[t] = a.ctypes.data
    return [pm, pe, st, mc, mpe], pm, pe, st, mc, mpe


# ---------------------------------------------------------------- Python walks
def acc_mc(zc: int, nc: int, t: int, nex: int, vec, kind: str = "mc") -> None:
    """Add `vec` (daughter rows) to mcontrib (kind "mc") or mpecontrib (kind "mpe") of (zc, nc, t, nex).

    TALYS: (none -- Incognita extension, not a TALYS routine)
    Test: none in the public suite
    """
    v = np.asarray(vec.detach().cpu().numpy() if hasattr(vec, "detach") else vec, float).ravel()
    d = _ACC.setdefault((zc, nc), {"mc": {}, "mpe": {}})[kind].setdefault(t, {})
    cur = d.get(nex)
    if cur is None:
        d[nex] = v.copy()
    else:
        if len(cur) < len(v):
            cur = np.pad(cur, (0, len(v) - len(cur)))
        cur[: len(v)] += v
        d[nex] = cur


def acc_cell(zc: int, nc: int, t: int, nex: int, nexout: int, v: float, kind: str = "mc") -> None:
    """Incognita extension.

    TALYS: (none -- Incognita extension, not a TALYS routine)
    Test: none in the public suite
    """
    vec = np.zeros(nexout + 1)
    vec[nexout] = float(v)
    acc_mc(zc, nc, t, nex, vec, kind)


def acc_matrix(zc: int, nc: int, t: int, m: np.ndarray, kind: str = "mc") -> None:
    """Incognita extension.

    TALYS: (none -- Incognita extension, not a TALYS routine)
    Test: none in the public suite
    """
    for nex in np.flatnonzero(np.any(m != 0.0, axis=1)).tolist():
        acc_mc(zc, nc, t, nex, m[nex], kind)


def py_finish(nuc, daughters: dict) -> None:
    """End of one nucleus on a Python walk: turn its accumulators into a record (same layout as the C sink's).

    TALYS: (none -- Incognita extension, not a TALYS routine)
    Test: none in the public suite
    """
    a = _ACC.pop((nuc.zcomp, nuc.ncomp), None)
    if a is None:
        return
    def np_(x):
        return np.asarray(x.detach().cpu().numpy() if hasattr(x, "detach") else x, float)
    ex, dex = np_(nuc.ex_mev), np_(nuc.dex_mev)
    xrows = int(nuc.xspopex_mb.shape[0])
    sep = np.array([float(nuc.sep_mev.get(t, 0.0)) for t in range(7)])
    rec = dict(zc=nuc.zcomp, nc=nuc.ncomp, maxex=int(nuc.maxex), nlast=int(nuc.nlast), ex=ex[:xrows], dex=dex[:xrows],
               sep=sep, types={}, lines_only=False, src="py")
    for t in range(7):
        if t not in a["mc"] and t not in a["mpe"]:
            continue
        if t == 0:
            d, dr = nuc, xrows
        else:
            d = daughters.get(t)
            if d is None:
                continue
            dr = int(d.xspopex_mb.shape[0])
        mc, mpe = np.zeros((xrows, dr)), np.zeros((xrows, dr))
        for kind, M in (("mc", mc), ("mpe", mpe)):
            for nex, v in a[kind].get(t, {}).items():
                k = min(len(v), dr)
                M[nex, :k] += v[:k]
        rec["types"][t] = dict(mc=mc, mpe=mpe, ex=np_(d.ex_mev)[:dr], dex=np_(d.dex_mev)[:dr], nlast=int(d.nlast),
                               maxex=int(d.maxex))
    _put(rec)


def _put(rec: dict) -> None:
    if _CUR is None:
        return
    key = (rec["zc"], rec["nc"])
    old = _CUR["walks"].get(key)
    if old is None:
        _CUR["walks"][key] = rec
        return
    # the same nucleus reported twice in one attempt (python-driven nx_walk + leftover/mpe applied in Python):
    # add the matrices
    for t, e in rec["types"].items():
        o = old["types"].get(t)
        if o is None:
            old["types"][t] = e
            continue
        for k in ("mc", "mpe"):
            r = min(o[k].shape[0], e[k].shape[0]); c = min(o[k].shape[1], e[k].shape[1])
            o[k][:r, :c] += e[k][:r, :c]


# ---------------------------------------------------------------- per run
def begin_run(cas) -> None:
    """A new engine run on `cas` (engine_c.cases / engine.ChainedFull): the target context the angular/DDX output needs.

    TALYS: (none -- Incognita extension, not a TALYS routine)
    Test: none in the public suite
    """
    global RUN
    if not enabled():
        return
    k0 = int(cas.k0)
    RUN = dict(Z=int(cas.Zt), A=int(cas.At), k0=k0, Zc=int(cas.Zt) + PARZ[k0], Ac=int(cas.At) + PARZ[k0] + PARN[k0],
               flagfission=bool(getattr(cas.options, "flagfission", False)),
               cnubar=(float(getattr(cas.options, "cnubar1", 1.0)), float(getattr(cas.options, "cnubar2", 1.0))))


def end_run(cas) -> None:
    """End of the engine run: run-level angular distributions while the cascade is alive.

    TALYS: (none -- Incognita extension, not a TALYS routine)
    Test: none in the public suite
    """
    if RUN is None:
        return
    from physics.hf import specang

    specang.run_level(cas, [r["e_inc_mev"] for r in ENERGIES])


# ---------------------------------------------------------------- per energy
def begin_energy(e_inc_mev: float) -> None:
    """Incognita extension.

    TALYS: (none -- Incognita extension, not a TALYS routine)
    Test: none in the public suite
    """
    global _CUR
    if not enabled():
        _CUR = None
        return
    _CUR = dict(e_inc_mev=float(e_inc_mev), walks={}, attempts=0)
    _ACC.clear()
    from physics.hf import specang

    specang.sync_target(True)


def begin_attempt(path: str) -> None:
    """A (re)started cascade of the current energy: what earlier attempts recorded is void.

    TALYS: (none -- Incognita extension, not a TALYS routine)
    Test: none in the public suite
    """
    if _CUR is None:
        return
    _CUR["walks"] = {}
    _CUR["attempts"] += 1
    _CUR["path"] = path
    _ACC.clear()


def end_energy(pinp, k0: int, b2=None) -> None:
    """Close the current energy: compemission over every recorded nucleus + the binary spectra binspec recorded.

    TALYS: (none -- Incognita extension, not a TALYS routine)
    Test: none in the public suite
    """
    global _CUR
    if _CUR is None:
        return
    cur, _CUR = _CUR, None
    from physics.hf import specang

    specang.sync_target(False)
    try:
        from physics.hf.emission import binspec

        binrec = binspec.LAST.pop() if binspec.LAST and abs(binspec.LAST[-1]["e_inc_mev"] - cur["e_inc_mev"]) < 1e-9 \
            else None
        binspec.LAST.clear()
        cur["binary"] = binrec
        if pinp is None:
            ENERGIES.append(cur)
            return
        eg = np.asarray(pinp.egrid_mev, float)
        if binrec is not None:
            eg = eg[: len(binrec["egrid"])]
        maxen = len(eg) - 1
        eb, et, de = _edges(eg, maxen)
        etot = float(pinp.etotal_mev)
        if 1 in pinp.residuals:
            cur["S_n_cn"] = float(pinp.residuals[1].sep_mev)  # S(0, 0, 1), for nubarWahl
        eninccm = etot - float(pinp.residuals[k0].sep_mev) if k0 in pinp.residuals else cur["e_inc_mev"]
        xseps = float(getattr(b2, "xseps_mb", 1.0e-7) or 1.0e-7) if b2 is not None else 1.0e-7
        speceps = xseps / eninccm if eninccm > 0 else 0.0
        ebegin = {t: int(pinp.ebegin.get(t, 0)) for t in range(7)}
        eend = {t: int(pinp.eend.get(t, 0)) for t in range(7)}
        xsemis = np.zeros((7, len(eg)))
        xsmpe = np.zeros((7, len(eg)))
        glines = []
        per_nuc = {}
        for key in sorted(cur["walks"]):
            rec = cur["walks"][key]
            if rec["lines_only"]:
                glines += _gamma_lines(rec)
                continue
            ce, cm = compemission(rec, eg, eb, et, de, ebegin, eend, speceps)
            xsemis += ce
            xsmpe += cm
            glines += _gamma_lines(rec)
            per_nuc[key] = (ce, cm)
        cur.update(egrid=eg, ebottom=eb, etop=et, deltae=de, ebegin=ebegin, eend=eend, speceps=speceps,
                   eninccm=eninccm, xsemis_mul=xsemis, xsmpeemis=xsmpe, gamma_lines=glines, per_nucleus=per_nuc)
    except Exception as exc:  # noqa: BLE001 -- output only
        cur.setdefault("errors", []).append(f"end_energy {type(exc).__name__}: {exc}")
    ENERGIES.append(cur)


def _gamma_lines(rec: dict):
    """Discrete gamma transitions recorded on type 0 rows nex <= Nlast: (Z, N index, E_gamma, mb)."""
    e = rec["types"].get(0)
    if e is None:
        return []
    mc = e["mc"]
    out = []
    nl = rec["nlast"]
    ex = rec["ex"]
    for nex in range(1, min(nl, mc.shape[0] - 1) + 1):
        for k in np.flatnonzero(mc[nex, :nex]).tolist():
            out.append((rec["zc"], rec["nc"], nex, k, float(ex[nex] - ex[k]), float(mc[nex, k])))
    return out


def _edges(eg: np.ndarray, maxen: int):
    from physics.hf.emission.binspec import _edges as e

    return e(eg, maxen)


def _locate(xx: np.ndarray, ib: int, ie: int, x: float) -> int:
    """locate.f90 exactly (no clamping: ib - 1 below, ie above)."""
    if ib > ie:
        return 0
    jl, ju = ib - 1, ie + 1
    ascend = xx[ie] >= xx[ib]
    while ju - jl > 1:
        jm = (ju + jl) // 2
        if ascend == (x >= xx[jm]):
            jl = jm
        else:
            ju = jm
    if x == xx[ib]:
        return ib
    if x == xx[ie]:
        return ie - 1
    return jl


_SOLIB = None


def _solib():
    """native/lib/libspecout.so (scripts/build_specout_native.sh) or None; SPECOUT_PY=1 forces the Python version."""
    global _SOLIB
    if os.environ.get("SPECOUT_PY", "0") == "1":
        return None
    if _SOLIB is None:
        from pathlib import Path

        p = Path(__file__).resolve().parent / "native" / "lib" / "libspecout.so"
        try:
            so = ctypes.CDLL(str(p))
            if so.so_version() != 1:
                raise OSError("version")
            so.so_compemission.argtypes = [ctypes.c_void_p] * 3
            so.so_compemission.restype = ctypes.c_int
            _SOLIB = so
        except OSError:
            _SOLIB = False
    return _SOLIB or None


def compemission(rec: dict, eg, eb, et, de, ebegin: dict, eend: dict, speceps: float):
    """compemission.f90 for one cascade nucleus: (xsemis (7, E), xsmpeemis (7, E)) in mb/MeV on egrid.
    The compiled twin (native/specout.c) when built, else `compemission_py`.

    TALYS: (none -- Incognita extension, not a TALYS routine)
    Test: none in the public suite
    """
    so = _solib()
    if so is None:
        return compemission_py(rec, eg, eb, et, de, ebegin, eend, speceps)
    E = len(eg)
    T = rec["types"]
    xrows = len(rec["ex"])
    iv = np.zeros(39, np.int64)
    dv = np.zeros(8)
    pv = np.zeros(37, np.uint64)
    keep = []

    def P(a, dt=np.float64):
        a = np.ascontiguousarray(a, dtype=dt)
        keep.append(a)
        return a.ctypes.data

    iv[0], iv[1], iv[2], iv[3] = rec["maxex"], rec["nlast"], E, xrows
    dv[0] = speceps
    dv[1:8] = np.asarray(rec["sep"], float)[:7]
    pv[0], pv[1], pv[2], pv[3], pv[4], pv[5] = P(rec["ex"]), P(rec["dex"]), P(eg), P(eb), P(et), P(de)
    for t in range(7):
        iv[25 + t], iv[32 + t] = ebegin[t], eend[t]
        e = T.get(t)
        if e is None:
            continue
        mc = np.zeros((xrows, e["mc"].shape[1]))
        r = min(xrows, e["mc"].shape[0])
        mc[:r] = e["mc"][:r]
        mp = np.zeros_like(mc)
        mp[:r] = e["mpe"][:r]
        iv[4 + t], iv[11 + t], iv[18 + t] = mc.shape[1], e["maxex"], e["nlast"]
        exd = np.zeros(mc.shape[1]); dexd = np.zeros(mc.shape[1])
        exd[: min(len(e["ex"]), mc.shape[1])] = e["ex"][: mc.shape[1]]
        dexd[: min(len(e["dex"]), mc.shape[1])] = e["dex"][: mc.shape[1]]
        pv[6 + t], pv[13 + t], pv[20 + t] = P(exd), P(dexd), P(mc)
        pv[27 + t] = P(mp) if np.any(mp) else 0
    oc, om, w = np.zeros((7, E)), np.zeros((7, E)), np.zeros(E)
    pv[34], pv[35], pv[36] = oc.ctypes.data, om.ctypes.data, w.ctypes.data
    so.so_compemission(iv.ctypes.data, dv.ctypes.data, pv.ctypes.data)
    return oc, om


def compemission_py(rec: dict, eg, eb, et, de, ebegin: dict, eend: dict, speceps: float):
    """compemission.f90 for one cascade nucleus: (xsemis (7, E), xsmpeemis (7, E)) in mb/MeV on egrid (Python).

    TALYS: (none -- Incognita extension, not a TALYS routine)
    Test: none in the public suite
    """
    E = len(eg)
    out_c = np.zeros((7, E))
    out_m = np.zeros((7, E))
    ex, dex, sep = rec["ex"], rec["dex"], rec["sep"]
    maxex, nl0 = rec["maxex"], rec["nlast"]
    T = rec["types"]

    def mcv(t, a, b):
        e = T[t]
        M = e["mcx"]
        if a < 0 or b < 0 or a >= M.shape[0] or b >= M.shape[1]:
            return 0.0
        return float(M[a, b])

    for t, e in T.items():
        e["mcx"] = e["mc"] + e["mpe"]  # TALYS's mcontrib holds the multiple pre-equilibrium part too
    for nex in range(maxex, nl0, -1):
        exinc = float(ex[nex])
        dexinc = float(dex[nex])
        ex0plus = exinc + 0.5 * dexinc
        ex0min = exinc - 0.5 * dexinc
        nexmax = {}
        for t, e in T.items():
            if t == 0:
                continue
            exm = ex0plus - float(sep[t])
            if t > 1:
                exm -= float(eg[ebegin[t]])
            nexmax[t] = -1
            for nexout in range(e["maxex"], -1, -1):
                if nexout >= len(e["ex"]):
                    continue
                exmin = float(e["ex"][nexout]) - 0.5 * float(e["dex"][nexout])
                if exmin < exm:
                    nexmax[t] = nexout
                    break
        nexmax[0] = nex - 1
        for t, e in T.items():
            nxm = nexmax.get(t, -1)
            if nxm < 0 or ebegin[t] >= eend[t]:
                continue
            NL = int(e["nlast"])
            SS = float(sep[t])
            exd, dexd = e["ex"], e["dex"]
            xsgrid = np.zeros(E)
            xsmpegrid = np.zeros(E)
            for nexout in range(0, nxm + 1):
                if nexout == 0 and NL == 0:
                    continue
                xso00 = mcv(t, nex, nexout)
                if xso00 <= speceps:
                    continue
                exout = float(exd[nexout])
                dEx = float(dexd[nexout])
                if nexout > NL:
                    ex1min = exout - 0.5 * dEx
                    ex1plus = exout + 0.5 * dEx
                    if nexout == nxm and t >= 1:
                        ex1plus = ex0plus - SS
                        exout = 0.5 * (ex1plus + ex1min)
                    emin = max(ex0min - SS - ex1plus, 0.0)
                    emax = ex0plus - SS - ex1min
                    eout = 0.5 * (emin + emax)
                    exm = 0.0
                else:
                    exm = exout + SS
                    if ex0min < exm <= ex0plus:
                        eout = 0.5 * (ex0plus + exm) - SS - exout
                        emin = 0.0
                    else:
                        eout = exinc - SS - exout
                        emin = ex0min - SS - exout
                    emax = ex0plus - SS - exout
                nenbeg = max(_locate(eb, ebegin[t], eend[t], emin), 1)
                nenend = _locate(eb, ebegin[t], eend[t], emax)
                if nenend < nenbeg:
                    continue
                dE = emax - emin
                dEhalf = 0.5 * dE
                xsom0 = mcv(t, nex - 1, nexout)
                xsop0 = mcv(t, nex + 1, nexout)
                weight = np.zeros(E)
                if nexout > NL:
                    xso0m = mcv(t, nex, nexout - 1)
                    xsopm = mcv(t, nex + 1, nexout - 1)
                    xsomp = mcv(t, nex - 1, nexout + 1)
                    xso0p = mcv(t, nex, nexout + 1)
                    for nen in range(nenbeg, nenend + 1):
                        if eg[nen] <= eout:
                            edist = eout - eg[nen]
                            if emin <= 0.0001:
                                term = xso00 * (1.0 - edist / dEhalf)
                            else:
                                term1 = xso00 + 0.5 * edist / dE * (xsom0 - xso00)
                                term2 = xso0p + 0.5 * edist / dE * (xsomp - xso0p)
                                term = term1 + 0.5 * edist / dE * (term2 - term1)
                        else:
                            edist = eg[nen] - eout
                            if xsop0 == 0.0:
                                term1 = xso00 * (1.0 - 0.5 * edist / dEhalf)
                                term2 = 0.0
                            else:
                                term1 = xso00 + 0.5 * edist / dE * (xsop0 - xso00)
                                term2 = xso0m + 0.5 * edist / dE * (xsopm - xso0m)
                            term = term1 + 0.5 * edist / dE * (term2 - term1)
                        weight[nen] = max(term, 0.0) * de[nen]
                else:
                    inside = ex0min < exm <= ex0plus
                    for nen in range(nenbeg, nenend + 1):
                        if eg[nen] <= eout:
                            edist = eout - eg[nen]
                            term = xso00 * (1.0 - edist / dEhalf) if inside else xso00 + edist / dE * (xsom0 - xso00)
                        else:
                            edist = eg[nen] - eout
                            term = (xso00 * (1.0 - edist / dEhalf) if xsop0 == 0.0
                                    else xso00 + edist / dexinc * (xsop0 - xso00))
                        weight[nen] = max(term, 0.0) * de[nen]
                fracbot = (emin - eb[nenbeg]) / de[nenbeg]
                fractop = (et[nenend] - emax) / de[nenend]
                if nexout == NL + 1:
                    fractop = 0.0
                if nenend == nenbeg:
                    weight[nenbeg] *= 1.0 - fracbot - fractop
                else:
                    weight[nenbeg] *= 1.0 - fracbot
                    weight[nenend] *= 1.0 - fractop
                sumweight = float(np.sum(weight[nenbeg:nenend + 1]))
                if sumweight == 0.0:
                    continue
                fracmpe = float(e["mpe"][nex, nexout]) / xso00 if nexout < e["mpe"].shape[1] else 0.0
                factor = xso00 / sumweight
                sl = slice(nenbeg, nenend + 1)
                emisfac = factor * weight[sl] / de[sl]
                xsgrid[sl] += (1.0 - fracmpe) * emisfac
                xsmpegrid[sl] += fracmpe * emisfac
            sl = slice(ebegin[t], eend[t] + 1)
            out_c[t, sl] += xsgrid[sl]
            out_m[t, sl] += xsmpegrid[sl]
    for e in T.values():
        e.pop("mcx", None)
    return out_c, out_m


# ---------------------------------------------------------------- output
def pack(Z: int, A: int) -> dict:
    """Everything recorded for the run as flat numpy arrays (npz-ready). Spectra (mb/MeV, on egrid):
    so_<x>_comp = binary compound continuum + compemission compound part of every cascade nucleus (TALYS xscomp),
    so_<x>_pe = binary pre-equilibrium (xspreeq), so_<x>_mpe = multiple pre-equilibrium (xsmpreeq),
    so_<x>_gr = giant resonance (xsgr), so_<x>_cont = their sum (TALYS xssumout without the discrete lines),
    binary discrete lines so_<x>_lines_e / _lines_xs (ne, nlev) (NaN padded; elastic level zeroed),
    discrete gamma lines so_glines (rows: energy index, zc, nc, level from, level to, E_gamma, mb).

    TALYS: (none -- Incognita extension, not a TALYS routine)
    Test: none in the public suite
    """
    if not ENERGIES:
        return {}
    ne = len(ENERGIES)
    eg = next((r["egrid"] for r in ENERGIES if "egrid" in r), None)
    out = {"so_e_inc_mev": np.array([r["e_inc_mev"] for r in ENERGIES]), "so_version": np.array(1)}
    if eg is None:
        return out
    E = len(eg)
    out["so_egrid"] = np.asarray(eg, float)
    out["so_deltae"] = np.asarray(next(r["deltae"] for r in ENERGIES if "deltae" in r), float)
    comps = {k: np.zeros((ne, 7, E)) for k in ("bincomp", "mulcomp", "pe", "mpe", "gr")}
    nlev = 1
    for r in ENERGIES:
        b = r.get("binary")
        if b:
            for e in b["types"].values():
                nlev = max(nlev, len(e["lines_e"]))
    le = np.full((ne, 7, nlev), np.nan)
    lx = np.full((ne, 7, nlev), np.nan)
    eb_ = np.zeros((ne, 7), np.int64)
    ee_ = np.zeros((ne, 7), np.int64)
    gl, errs = [], []
    for i, r in enumerate(ENERGIES):
        errs += [f"{r['e_inc_mev']}: {x}" for x in r.get("errors", [])]
        if "xsemis_mul" in r:
            n = min(E, r["xsemis_mul"].shape[1])
            comps["mulcomp"][i, :, :n] = r["xsemis_mul"][:, :n]
            comps["mpe"][i, :, :n] = r["xsmpeemis"][:, :n]
            for t in range(7):
                eb_[i, t], ee_[i, t] = r["ebegin"][t], r["eend"][t]
            gl += [(i, *g) for g in r["gamma_lines"]]
        b = r.get("binary")
        if b:
            for t, e in b["types"].items():
                t = int(t)
                for k, name in (("xsemis", "bincomp"), ("xspreeq", "pe"), ("xsgr", "gr")):
                    v = np.asarray(e[k], float)[:E]
                    comps[name][i, t, : len(v)] = v
                le[i, t, : len(e["lines_e"])] = e["lines_e"]
                lx[i, t, : len(e["lines_xs"])] = e["lines_xs"]
    for t, x in enumerate(PARNAME):
        out[f"so_{x}_comp"] = comps["bincomp"][:, t] + comps["mulcomp"][:, t]
        out[f"so_{x}_bincomp"] = comps["bincomp"][:, t]
        out[f"so_{x}_pe"] = comps["pe"][:, t]
        out[f"so_{x}_mpe"] = comps["mpe"][:, t]
        out[f"so_{x}_gr"] = comps["gr"][:, t]
        out[f"so_{x}_cont"] = out[f"so_{x}_comp"] + comps["pe"][:, t] + comps["mpe"][:, t] + comps["gr"][:, t]
        out[f"so_{x}_lines_e"] = le[:, t]
        out[f"so_{x}_lines_xs"] = lx[:, t]
    out["so_ebegin"], out["so_eend"] = eb_, ee_
    out["so_glines"] = np.asarray(gl, float).reshape(-1, 7)
    out["so_errors"] = np.array("\n".join(errs))
    from physics.hf import specang

    out.update(specang.pack(ENERGIES, out))
    if os.environ.get("INCOGNITA_SPECOUT_F32", "1") != "0":  # storage: float32 for the big arrays (rel. 6e-8)
        keep64 = {"so_e_inc_mev", "so_egrid", "so_deltae"}
        for k, v in list(out.items()):
            if k not in keep64 and isinstance(v, np.ndarray) and v.dtype == np.float64 and v.size > 64:
                out[k] = v.astype(np.float32)
    return out
