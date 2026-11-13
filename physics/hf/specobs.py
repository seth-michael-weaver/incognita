"""Emission spectra, double-differential cross sections, discrete gamma-ray lines and the (k0,g<p>)
column on TALYS's keywords, OUTPUT ONLY.

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

What it gives (TALYS's file names without the incident energy, as Results.spectra keys; arrays (C, ...) on the run's
energies, NaN where TALYS writes no row at that energy):

    <x>spec.tot                    xssumout (C, M) mb/MeV on espec      spectraout.f90, the (k0,x<x>) spectrum file
    <x>spec.tot:E                  espec (C, M) MeV (egrid up to the last discrete line, then the fine discrete grid)
    <x>spec.tot:direct|:preeq|:multiple_preeq|:compound|:preeq_ratio      columns 3-7 of the file
    <x>spec.tot:breakup_ratio|:stripping|:knockout|:breakup               columns 8-11 (k0 > 2 or x in d t h a)
    Eaverage_<x>.out               average emission energy (C,) MeV     spectra.f90:268-281
    <x>ddx                         xssumoutad (C, M, nanglecont+1) mb/MeV/sr (+ :direct :preeq :multiple_preeq
                                   :compound), x in n p d t h a           ddxout.f90 (talys.out tables)
    <x>ddxA<aaa.a>.deg             fileddxa: DDX at one angle (C, M) (+ the same columns)   ddxout.f90, ddxmode 2 / 3
    <x>ddxE<eeee.e>.MeV            fileddxe: DDX at one emission energy (C, nanglecont+1)  ddxout.f90, ddxmode 1 / 3
    anglecont                      the continuum angle grid (nanglecont+1,) degrees
    gam<ZZZ><AAA>L<ii>L<jj>.tot    discrete gamma line i -> j of a residual (C,) mb (+ :E, gamma energy MeV)
    <k0><x>.tot:ngn                xsngn: the initial compound nucleus' own particle emission (the (n,gn) column of
                                   nn.tot / nn.con), mb                multiple.f90:945-949

Switches: the deck keywords (Options) `outspectra` (spectraout), `ddxmode` (ddxout; > 0 implies outspectra),
`fileddxa`, `fileddxe`, `anglescont`, `outgamdis` (gamdisout), `filespectrum`, `filegamdis`, `blockspectra`, `blockddx`,
`adddiscrete`, `addelastic`, `channelenergy`, `elwidth`, `segment`; the port switch `INCOGNITA_SPECOBS=1` (= outspectra y,
ddxmode 3, outgamdis y); `INCOGNITA_SPECOBS_DIR=<dir>` also writes the files (spec, ddx, gam, Eaverage). Default: none of
them, nothing is computed and every engine array is unchanged. Any of them turns the `specout` recorders on for the
run (specout.enabled); a DDX also turns angout's recorders on for every discrete level (the discrete peaks carry discad).

Where the numbers come from (none of it feeds back into the engine): the `specout` recorders (binary spectra of
`emission.binspec`, compemission of every cascade nucleus in `specout`, discrete gamma lines of the cascade) taken as
TALYS has them (the discrete-parent closing is undone: the raw binary parts and compemission alone are used); Kalbach systematics
(`specang.kalbach_a`) for the pre-equilibrium and multiple pre-equilibrium DDX; angout's discad for the discrete peaks.

TALYS routines ported here (file:line of the subroutine statement):
    spectra.f90:1 (spectra)        espec, the fine grid above the last discrete line, discrete peaks, xssumout, ratios,
                                   Eaverage, the DDX arrays on it
    binary.f90:345-375             Eaveragebin
    multiple.f90:693-713, :945-949 xscompad / xsmpreeqad, Eaveragemul, xsngn
    preeqang.f90:1 (preeqang)      xspreeqad = (xspreeq - xspreeqbu) kalbach
    spectraout.f90:1, ddxout.f90:1, gamdisout.f90:1   names, columns, interpolation to fileddxa / fileddxe
Approximation (recorded in META["approx"]): the giant-resonance and collective-continuum part of the DDX (xsgrad) is
isotropic (TALYS: grcollad / directad of the GR and deformed continuum levels).
Task: T10 (physics/hf/CONTRACT.md section 7; output only). Acceptance test: KW-B4
(tests/hf/test_specobs.py, scripts/kwcov/b4_compare.py, docs/hf/COVERAGE_PLAN.md).
"""

from __future__ import annotations

import datetime
import math
import os
from pathlib import Path

import numpy as np

ENV = "INCOGNITA_SPECOBS"
ENV_DIR = "INCOGNITA_SPECOBS_DIR"
PARSYM = "gnpdtha"
PARZ = (0, 0, 1, 1, 1, 2, 2)
PARN = (0, 1, 0, 1, 2, 1, 2)
PARA = (0, 1, 1, 2, 3, 3, 4)
NUMENDISC = 400  # A0_talys_mod.f90:71
SQRTTWOPI = math.sqrt(2.0 * math.pi)
COLS = ("direct", "preeq", "multiple_preeq", "compound")

_SET: dict | None = None
_DISCAD: dict = {}  # angout's discrete angular distributions of the run (take_discad)
META: dict = {}


def _on(v) -> bool:
    v = str(v).strip().lower()
    return v[:1] in ("1", "y", "t") or v == "on"


def _points(v) -> tuple:
    """fileddxa / fileddxe values: ((symbol, value), ...) from Options or a deck string `n 30 90 p 30`."""
    if isinstance(v, (tuple, list)):
        return tuple((str(a), float(b)) for a, b in v)
    out, sym = [], None
    for x in str(v).replace(",", " ").split():
        if x[:1].lower() in PARSYM and not x[:1].isdigit():
            sym = x[:1].lower()
        elif sym is not None:
            out.append((sym, float(x)))
    return tuple(out)


def settings(options=None) -> dict | None:
    """spectraout / ddxout / gamdisout switches for a run, or None when none of them runs (output.f90:63-67).

    TALYS: output.f90:1 (output) lines 63-67, input_output.f90:1, input_outfiles.f90:1, input_directpar.f90:1
    Test: tests/hf/test_specobs.py
    """
    env = _on(os.environ.get(ENV, "0"))
    if options is not None:
        o = options
        spec, ddxmode, gamdis = bool(o.flagspec), int(o.ddxmode), bool(o.flaggamdis)
        fs, dda, dde = tuple(o.filespectrum), _points(o.fileddxa), _points(o.fileddxe)
        blocks, blockd = bool(o.flagblockspectra), bool(o.flagblockddx)
        k0 = int(o.k0)
    else:  # before a Cascade exists: the active deck lines (fitlib) carry the same keywords
        from physics.hf.input import fitlib

        ov = {str(k).lower(): v for k, v in fitlib.option_overrides().items()}
        endf = _on(ov.get("endf", "n"))
        spec, gamdis = _on(ov.get("outspectra", endf)), _on(ov.get("outgamdis", "n"))
        ddxmode = int(ov.get("ddxmode", 0))
        fs, dda, dde, blocks, blockd, k0 = (), (), (), endf, endf, None
    if env:
        spec, gamdis, ddxmode = True, True, max(ddxmode, 3)
    if ddxmode > 0:
        spec = True  # input_output.f90:283-285
    if not (spec or gamdis):
        return None
    return dict(spec=spec, ddxmode=ddxmode, ddx=ddxmode > 0, gamdis=gamdis, filespectrum=set(fs) if fs else set(PARSYM),
                fileddxa=dda, fileddxe=dde, blockspectra=blocks, blockddx=blockd, k0=k0)


def ddx_wanted(options) -> bool:
    """The run writes double-differential cross sections (ddxmode > 0, or the port switch).

    TALYS: input_output.f90:279-288 (flagddx)
    Test: tests/hf/test_specobs.py
    """
    s = settings(options)
    return bool(s and s["ddx"])


def wanted() -> bool:
    """The run being set up asks for spectrum / DDX / gamma-line output (the `specout` recorders must be on).

    TALYS: (none -- a port switch)
    Test: tests/hf/test_specobs.py
    """
    return _SET is not None or settings() is not None


def active() -> bool:
    """A run with spectrum / DDX / gamma-line output is in progress (begin_run saw a switch).

    TALYS: (none -- a port switch)
    Test: tests/hf/test_specobs.py
    """
    return _SET is not None


def begin_run(cas) -> bool:
    """Called by specout.begin_run: fix the run's settings from its Options and Params.

    TALYS: (none -- a port switch)
    Test: tests/hf/test_specobs.py
    """
    global _SET
    _DISCAD.clear()
    s = settings(cas.options)
    if s is not None:
        o = cas.options
        try:
            elw = float(cas.params.at("elwidth"))
        except Exception:  # noqa: BLE001 -- Params without the key: TALYS's default
            elw = 0.5
        s.update(Z=int(cas.Zt), A=int(cas.At), k0=int(cas.k0), nangle=int(o.nangle), nanglecont=int(o.nanglecont),
                 elwidth=elw, segment=int(o.segment), flagendf=bool(o.flagendf), echannel=bool(o.flagEchannel),
                 eadd=float(o.eadd_mev), eaddel=float(o.eaddel_mev), flagelectron=bool(getattr(o, "flagelectron", True)),
                 cas=cas)
    _SET = s
    from physics.hf import exclspec  # sp*.tot needs outspectra + channels y

    exclspec.begin_run(cas)
    return s is not None


def end_run() -> None:
    """The run is over: the switches are read again for the next one.

    TALYS: (none -- a port switch)
    Test: tests/hf/test_specobs.py
    """
    global _SET
    _SET = None
    _DISCAD.clear()


def take_discad(arr: dict, nangle: int) -> None:
    """angout.add_to_results hands over the run's discrete angular distributions (discad on the `angles` grid).

    TALYS: angdis.f90:1 (angdis) -- discad
    Test: tests/hf/test_specobs.py
    """
    if _SET is None:
        return
    _DISCAD.clear()
    _DISCAD.update({k: np.asarray(v, float) for k, v in arr.items() if "ang.L" in k and ":" not in k})
    _DISCAD["_nangle"] = int(nangle)


def anglecont(nanglecont: int) -> np.ndarray:
    """anglecont(iang) = iang * (180 / nanglecont), single precision (grid.f90:266-269).

    TALYS: grid.f90:1 (grid)
    Test: tests/hf/test_specobs.py
    """
    f32 = np.float32
    d = f32(180.0) / f32(nanglecont)
    return np.array([f32(i) * d for i in range(nanglecont + 1)], dtype=np.float32).astype(float)


def _locate(xx, ib: int, ie: int, x: float) -> int:
    from physics.hf.specout import _locate as loc

    return loc(np.asarray(xx, float), ib, ie, x)


def _vec(v, n: int) -> np.ndarray:
    a = np.zeros(n)
    if v is None:
        return a
    v = np.asarray(v, float)[:n]
    a[: v.size] = v
    return a


# ------------------------------------------------------------------------------------------------ one incident energy
def energy_spectra(r: dict, s: dict, xselastot: float, row: int = 0) -> dict:
    """spectra.f90 for one recorded incident energy `r` (a specout.ENERGIES entry): per ejectile type the espec grid,
    the spectrum columns and (DDX) the angle-dependent ones, plus Eaverage and xsngn.

    TALYS: spectra.f90:1 (spectra), binary.f90:345-375, multiple.f90:693-713, :945-949, preeqang.f90:1
    Test: tests/hf/test_specobs.py
    """
    from physics.hf import specang

    k0, e_inc = int(s["k0"]), float(r["e_inc_mev"])
    eg, de = np.asarray(r["egrid"], float), np.asarray(r["deltae"], float)
    et = np.asarray(r["etop"], float)
    E = len(eg)
    b = r.get("binary") or {"types": {}}
    eninccm = float(r["eninccm"])
    flagadd = e_inc >= s["eadd"]  # energies.f90:210-219
    flagaddel = e_inc >= s["eaddel"]
    elw, seg = float(s["elwidth"]), int(s["segment"])
    fine = 2 if s["flagendf"] else 10
    Ainit = s["A"] + PARA[k0]
    Zc, Ac = s["Z"] + PARZ[k0], Ainit
    ddx = s["ddx"]
    th = anglecont(s["nanglecont"])
    nA = th.size
    nangle = int(_DISCAD.get("_nangle", s["nangle"]))
    iangdisc = [int(float(iang * nangle) / s["nanglecont"]) for iang in range(nA)]
    sm = specang.smyers(Zc, Ac) if ddx else None
    pertal = r.get("per_nucleus_talys", {})
    mulc = np.asarray(r.get("xsemis_mul_talys", np.zeros((7, E))), float)
    mulm = np.asarray(r.get("xsmpeemis_talys", np.zeros((7, E))), float)
    xsbin_full = b.get("xsbinary_full") or [0.0] * 8
    approx = []
    out = {"types": {}}
    # xsngn (multiple.f90:945-949): the initial compound nucleus' own emission before the binary step is added
    cn = r.get("walks", {}).get((0, 0))
    ngn = {}
    if cn is not None:
        for t, e in cn["types"].items():
            m = np.asarray(e["mc"], float) + np.asarray(e["mpe"], float)
            ngn[t] = float(m[int(cn["nlast"]) + 1:].sum()) if t == 0 else float(m.sum())
    out["ngn"] = ngn
    for t in range(7):
        ent = b["types"].get(t)
        if ent is None:
            continue
        raw = ent.get("raw") or ent
        bincomp = _vec(raw["xsemis"], E)
        pe = _vec(raw["xspreeq"], E)
        gr = _vec(raw["xsgr"], E)
        ps, ki, bu = _vec(ent.get("pe_ps"), E), _vec(ent.get("pe_ki"), E), np.zeros(E)
        comp = bincomp + mulc[t]
        mpe = mulm[t]
        ib, ie = int(ent["ebegin"]), int(ent["eend"])
        NL = int(ent["nlast"])
        lines_e = np.asarray(ent["lines_e"], float)
        lines_xs = np.asarray(ent["lines_xs"], float).copy()
        if t == k0 and lines_xs.size:
            lines_xs[0] = xselastot  # spectra.f90:139 xsdisc(k0, Ltarget) = xselastot
        # xsparticle(type) == 0: TALYS skips the ejectile (no line, no continuum anywhere)
        part = float(np.sum((comp + pe + mpe + gr)[ib:ie + 1] * de[ib:ie + 1])) + float(np.sum(lines_xs[1 if t == k0 else 0:]))
        if part <= 0.0 or ie < ib:
            continue
        eoutdis = lambda i: float(lines_e[i]) if i < lines_e.size else -1.0  # noqa: E731
        add = flagadd or t >= 2
        if add:
            elast = max(eoutdis(NL) - elw, 0.0)
            nend = _locate(eg, ib, ie, elast)
        else:
            nend = ie
        c1, c2, c3 = 1.0, 0.0, 0.0
        if s["echannel"]:  # spectra.f90:152-158
            c1 = (Ainit - PARA[t]) / Ainit
            c2 = PARA[t] / Ainit * PARA[k0] / Ainit * e_inc
            if c1 > 0.0 and c2 > 0.0:
                c3 = 2.0 * math.sqrt(c1 * c2)
        rows = list(range(ib, nend + 1))
        if add:
            f32 = np.float32  # spectra.f90:200-202 in single precision (U-238 5 MeV: int(10 * 2.9999998) = 29)
            ehigh = f32(eg[ie]) - f32(eg[nend])
            nhigh = min(int(f32(fine * seg) * ehigh), NUMENDISC - 8 * fine)
            eendout = nend + nhigh + 8 * fine
        else:
            eendout = ie
        M = eendout - ib + 1
        espec = np.zeros(M)
        col = {k: np.zeros(M) for k in ("disc", "pe", "ps", "ki", "bu", "mpe", "comp")}
        src = {"disc": gr, "pe": pe, "ps": ps, "ki": ki, "bu": bu, "mpe": mpe, "comp": comp}
        if ddx:
            ain = specang.kalbach_a(k0, t, e_inc, eg, sm)
            K = specang.kalbach_shape(ain, th)  # (E, A); 1 / (4 pi) for photons
            pead = np.where((pe != 0.0)[:, None], (pe - bu)[:, None] * K, 0.0)
            pead[: ib] = 0.0
            pead[ie + 1:] = 0.0
            mpead = mpe[:, None] * K
            compad = np.repeat(comp[:, None] / (4 * math.pi), nA, axis=1)
            grad = np.repeat(gr[:, None] / (4 * math.pi), nA, axis=1)  # approximation: TALYS grcollad / directad
            if np.any(gr != 0.0):
                approx.append(f"E={e_inc:g} {PARSYM[t]}: giant-resonance / collective-continuum DDX isotropic")
            srcad = {"disc": grad, "pe": pead, "mpe": mpead, "comp": compad}
            colad = {k: np.zeros((M, nA)) for k in srcad}
        for nen in rows:
            j = nen - ib
            espec[j] = c1 * eg[nen] + c2 + c3 * math.sqrt(max(eg[nen], 0.0))
            for k in col:
                col[k][j] = src[k][nen]
            if ddx:
                for k in colad:
                    colad[k][j] = srcad[k][nen]
        if add:
            levels = []
            for i in range(NL + 1):
                if i == 0 and t == k0 and k0 > 1:
                    continue
                if i == 0 and not flagaddel:
                    continue
                eo = eoutdis(i)
                if eo <= 0.0 or i >= lines_xs.size:
                    continue
                dw = elw * (eo / eninccm) ** 1.5
                da = None
                if ddx and lines_xs[i] != 0.0:
                    da = _DISCAD.get(f"{PARSYM[k0]}{PARSYM[t]}ang.L{i:02d}")
                    if da is None:
                        approx.append(f"E={e_inc:g} {PARSYM[t]} level {i}: no discad, isotropic peak")
                levels.append((i, eo, dw, da))
            ri = row
            for nenout in range(nend + 1, eendout + 1):
                j = nenout - ib
                eout = eg[nend] + (nenout - nend) / (seg * float(fine))
                espec[j] = c1 * eout + c2 + c3 * math.sqrt(max(eout, 0.0))
                nen = _locate(eg, nend, ie, eout)
                nen = min(nen, E - 2)
                ea = eout - eg[nen]
                eb_ = eg[nen + 1] - eg[nen]
                f = ea / eb_ if ea < eb_ else 1.0
                for k in col:
                    col[k][j] = src[k][nen] + f * (src[k][nen + 1] - src[k][nen])
                if ddx:
                    for k in colad:
                        colad[k][j] = srcad[k][nen] + f * (srcad[k][nen + 1] - srcad[k][nen])
                for i, eo, dw, da in levels:
                    g = 1.0 / (dw * SQRTTWOPI) * math.exp(-((eout - eo) ** 2) / (2.0 * dw * dw))
                    col["disc"][j] += g * lines_xs[i]
                    if ddx:
                        if da is not None:
                            colad["disc"][j] += g * da[ri, iangdisc]
                        else:
                            colad["disc"][j] += g * lines_xs[i] / (4 * math.pi)
        cont = col["pe"] + col["mpe"] + col["comp"]
        with np.errstate(divide="ignore", invalid="ignore"):
            pratio = np.where(cont != 0.0, (col["pe"] + col["mpe"]) / np.where(cont != 0.0, cont, 1.0), 0.0)
            bratio = (np.where(cont != 0.0, col["bu"] / np.where(cont != 0.0, cont, 1.0), 0.0) if (k0 > 2 or t > 2)
                      else np.zeros(M))
        res = dict(E=espec, total=cont + col["disc"], direct=col["disc"], preeq=col["pe"], multiple_preeq=col["mpe"],
                   compound=col["comp"], preeq_ratio=pratio, breakup_ratio=bratio, stripping=col["ps"],
                   knockout=col["ki"], breakup=col["bu"], ebegin=ib, eendout=eendout, deltae=de)
        if ddx:
            res["ad"] = dict(total=colad["disc"] + colad["pe"] + colad["mpe"] + colad["comp"], direct=colad["disc"],
                             preeq=colad["pe"], multiple_preeq=colad["mpe"], compound=colad["comp"])
        # Eaverage (spectra.f90:268-281, binary.f90:345-375, multiple.f90:711-714)
        nd = int(ent.get("nendisc", ie))
        xbe = bincomp + pe + gr
        bsum = float(np.sum(xbe[ib:nd + 1] * de[ib:nd + 1]))
        esum = float(np.sum(eg[ib:nd + 1] * xbe[ib:nd + 1] * de[ib:nd + 1]))
        if eoutdis(NL) > 0.0 and nd < E:
            frac = et[nd] - eoutdis(NL)
            bsum -= xbe[nd] * frac
            esum -= eg[nd] * xbe[nd] * frac
        xsb = bsum
        for i in range(min(NL + 1, lines_xs.size)):
            if t == k0 and i == 0:
                continue
            xsb += float(ent["lines_xs"][i])
            esum += float(ent["lines_xs"][i]) * eoutdis(i)
        ebin = esum / xsb if xsb > 0.0 else 0.0
        xsbt = float(xsbin_full[t + 1]) if len(xsbin_full) > t + 1 else 0.0
        xssum, easum = xsbt, ebin * xsbt
        walks = r.get("walks", {})
        for key, (ce, cm) in pertal.items():
            if key == (0, 0):
                continue
            em = (ce[t] + cm[t])
            emis = float(np.sum(em * de))
            if emis <= 0.0:
                continue
            emul = float(np.sum(eg * em * de)) / emis
            w = walks.get(key)
            feed = emis
            if w is not None and t in w["types"]:  # xsfeed: what the continuum bins emit (not the discrete cascade)
                m = np.asarray(w["types"][t]["mc"], float) + np.asarray(w["types"][t]["mpe"], float)
                feed = float(m[int(w["nlast"]) + 1:].sum()) if t == 0 else float(m.sum())
            xssum += feed
            easum += emul * feed
        res["Eaverage"] = easum / xssum if xssum > 0.0 else 0.0
        out["types"][t] = res
    out["approx"] = approx
    return out


# ------------------------------------------------------------------------------------------------ the run
def _ddx_name(x: str, kind: str, v: float) -> str:
    v32 = float(np.float32(v))
    if kind == "A":
        return f"{x}ddxA{int(v32):03d}{f'{v32:5.1f}'[3:]}.deg"
    return f"{x}ddxE{int(v32):04d}{f'{v32:6.1f}'[4:]}.MeV"


def build(res=None) -> dict[str, np.ndarray]:
    """The Results.spectra arrays of the recorded run (see module doc); fills META for `write_files`.

    TALYS: spectra.f90:1, spectraout.f90:1, ddxout.f90:1, gamdisout.f90:1
    Test: tests/hf/test_specobs.py
    """
    from physics.hf import specout

    s = _SET
    META.clear()
    if s is None or not specout.ENERGIES:
        return {}
    ens = specout.ENERGIES
    C = len(ens)
    k0 = int(s["k0"])
    e_inc = np.array([float(r["e_inc_mev"]) for r in ens])
    per = []
    approx = []
    el = None
    if res is not None and "elastic" in getattr(res, "totals_mb", {}):
        v = res.totals_mb["elastic"]
        el = np.asarray(v.detach().numpy() if hasattr(v, "detach") else v, float)
    for i, r in enumerate(ens):
        approx += [f"E={e_inc[i]:g}: {m}" for m in r.get("errors", []) if m.startswith(("end_energy", "c_sink"))]
        if "egrid" not in r or not r.get("binary"):
            per.append(None)
            continue
        a = r.get("ang") or {}
        xe = float(a["xselastot"]) if "xselastot" in a else (float(el[i]) if el is not None and i < el.size else 0.0)
        try:
            p = energy_spectra(r, s, xe, i)
        except Exception as exc:  # noqa: BLE001 -- output only
            approx.append(f"E={e_inc[i]:g}: spectra {type(exc).__name__}: {exc}")
            p = None
        per.append(p)
        if p:
            approx += p["approx"]
    out: dict[str, np.ndarray] = {}
    th = anglecont(s["nanglecont"])
    present: dict[str, np.ndarray] = {}
    if s["spec"]:
        for t in range(7):
            x = PARSYM[t]
            rows = [p["types"].get(t) if p else None for p in per]
            if not any(rows):
                continue
            M = max(rr["E"].size for rr in rows if rr)
            stem = f"{x}spec.tot"
            present[stem] = np.array([rr is not None for rr in rows])
            cols = ("total", "E", "direct", "preeq", "multiple_preeq", "compound", "preeq_ratio")
            if k0 > 2 or t > 2:
                cols += ("breakup_ratio", "stripping", "knockout", "breakup")
            for c in cols:
                arr = np.full((C, M), np.nan)
                for i, rr in enumerate(rows):
                    if rr:
                        arr[i, : rr[c].size] = rr[c]
                out[stem if c == "total" else f"{stem}:{c}"] = arr
            ea = np.full(C, np.nan)
            for i, rr in enumerate(rows):
                if rr:
                    ea[i] = rr["Eaverage"]
            out[f"Eaverage_{x}.out"] = ea
            if s["ddx"] and t >= 1:
                AD = {c: np.full((C, M, th.size), np.nan) for c in ("total",) + COLS}
                for i, rr in enumerate(rows):
                    if rr and "ad" in rr:
                        for c in AD:
                            AD[c][i, : rr["E"].size] = rr["ad"][c]
                for c, v in AD.items():
                    out[f"{x}ddx" if c == "total" else f"{x}ddx:{c}"] = v
                # fileddxa (ddxmode 2 / 3): spectrum at one angle, linear in angle (ddxout.f90:236-265)
                if s["ddxmode"] in (2, 3):
                    anginc = 180.0 / s["nanglecont"]
                    for sym, angf in s["fileddxa"]:
                        if sym != x:
                            continue
                        iang = _locate(th, 0, th.size - 1, angf)
                        iang = min(max(iang, 0), th.size - 2)
                        fac = (angf - th[iang]) / anginc
                        name = _ddx_name(x, "A", angf)
                        for c in ("total",) + COLS:
                            v = AD[c]
                            out[name if c == "total" else f"{name}:{c}"] = v[:, :, iang] + fac * (v[:, :, iang + 1] - v[:, :, iang])
                        present[name] = present[stem]
                # fileddxe (ddxmode 1 / 3): angular distribution at one emission energy (ddxout.f90:88-120)
                if s["ddxmode"] in (1, 3):
                    for sym, enf in s["fileddxe"]:
                        if sym != x:
                            continue
                        name = _ddx_name(x, "E", enf)
                        vals = {c: np.full((C, th.size), np.nan) for c in ("total",) + COLS}
                        for i, rr in enumerate(rows):
                            if not rr or "ad" not in rr:
                                continue
                            Eo = rr["E"]
                            n = _locate(Eo, 0, Eo.size - 1, enf)
                            n = min(max(n, 0), Eo.size - 2)
                            nen = n + rr["ebegin"]
                            dE = rr["deltae"][nen] if nen < len(rr["deltae"]) and rr["deltae"][nen] > 0 else Eo[n + 1] - Eo[n]
                            fac = (enf - Eo[n]) / dE
                            for c in vals:
                                v = rr["ad"][c]
                                vals[c][i] = v[n] + fac * (v[n + 1] - v[n])
                        for c, v in vals.items():
                            out[name if c == "total" else f"{name}:{c}"] = v
                        present[name] = present[stem]
        if s["ddx"]:
            out["anglecont"] = th
    # xsngn: the (k0,g<p>) column of <k0><p>.tot / .con
    for t in range(7):
        v = np.array([(p["ngn"].get(t, 0.0) if p else np.nan) for p in per])
        if np.any(np.nan_to_num(v) != 0.0):
            out[f"{PARSYM[k0]}{PARSYM[t]}.tot:ngn"] = v
    # discrete gamma lines (gamdisout.f90; cascade.f90:78-83: the intensity over 1 + the conversion coefficient)
    lines = {}
    if s["gamdis"]:
        Zc, Ac = s["Z"] + PARZ[k0], s["A"] + PARA[k0]
        convs: dict = {}
        for i, r in enumerate(ens):
            for zc, nc, n1, n2, eg_, mb in r.get("gamma_lines", []):
                Z, A = Zc - int(zc), Ac - int(zc) - int(nc)
                name = f"gam{Z:03d}{A:03d}L{int(n1):02d}L{int(n2):02d}.tot"
                d = lines.setdefault(name, [np.zeros(C), float(eg_), (Z, A, int(n1), int(n2))])
                cv = _conversion(s, int(zc), int(nc), int(n1), int(n2), convs, approx) if s["flagelectron"] else 0.0
                d[0][i] += float(mb) / (1.0 + cv)
        for name, (v, eg_, key) in sorted(lines.items()):
            out[name] = v
            out[name + ":E"] = np.full(C, eg_)
    META.update(Z=int(s["Z"]), A=int(s["A"]), k0=k0, e_inc_mev=e_inc, present=present, approx=sorted(set(approx)),
                lines={n: v[2] for n, v in lines.items()}, settings={k: v for k, v in s.items() if k != "cas"})
    return out


def _conversion(s: dict, zc: int, nc: int, n1: int, n2: int, cache: dict, approx: list) -> float:
    """conv(Zcomp, Ncomp, n1, branch to n2) of the levels the cascade used (Cascade._levels), 0 when not found.

    TALYS: cascade.f90:1 (cascade) lines 78-83, levels.f90:177-190
    Test: tests/hf/test_specobs.py
    """
    lv = cache.get((zc, nc))
    if lv is None:
        cas = s.get("cas")
        try:
            if hasattr(cas, "_levels"):
                lv = cas._levels(zc, nc)
            else:
                from physics.hf.structure.levels import discrete_levels

                lv = discrete_levels(s["Z"] + PARZ[s["k0"]] - zc, s["A"] + PARA[s["k0"]] - zc - nc, cas.options)
        except Exception as exc:  # noqa: BLE001 -- output only
            approx.append(f"gamma lines Zcomp={zc} Ncomp={nc}: no levels for the conversion ({type(exc).__name__})")
            lv = False
        cache[(zc, nc)] = lv
    if lv is False or n1 >= int(lv.branch_to.shape[0]):
        return 0.0
    bto = lv.branch_to[n1].tolist()
    if n2 not in bto:
        return 0.0
    return float(lv.conversion[n1, bto.index(n2)])


def add_to_results(res, injection):
    """End of engine.run / engine_c.run (after angout): Results.spectra from the recorded run (and the TALYS files with
    INCOGNITA_SPECOBS_DIR); the recorders the switches turned on are cleared. Unchanged when no switch is on.

    TALYS: spectraout.f90:1, ddxout.f90:1, gamdisout.f90:1
    Test: tests/hf/test_specobs.py
    """
    from physics.hf import recoil, specout

    if _SET is None:
        if recoil.active():  # `recoil y` with `outspectra n` (discrete recoils only, as TALYS)
            try:
                res = recoil.add_to_results(res, injection)
            finally:
                if not specout.env_enabled():
                    specout.clear_run()
        return res
    from dataclasses import replace

    import torch

    try:
        res = recoil.add_to_results(res, injection)  # before the recorders are cleared (no-op without recoil)
        arr = build(res)
        out_dir = os.environ.get(ENV_DIR, "").strip()
        if out_dir and arr:
            write_files(arr, META, out_dir)
        from physics.hf import exclspec  # exclusive channel spectra (outspectra + channels y)

        if exclspec.active():
            xarr, xmeta = exclspec.build([float(r["e_inc_mev"]) for r in specout.ENERGIES])
            META["exclspec"] = xmeta
            if out_dir and xarr:
                exclspec.write_files(xarr, xmeta, out_dir)
            arr = {**arr, **xarr}
        res = replace(res, spectra={k: torch.as_tensor(v, dtype=torch.float64) for k, v in arr.items()})
    finally:
        if not specout.env_enabled():
            specout.clear_run()
        end_run()
        from physics.hf import exclspec

        exclspec.end_run()
    return res


# ------------------------------------------------------------------------------------------------ TALYS files
def _efile(e: float) -> str:
    e32 = float(np.float32(e))
    return f"{int(e32):04d}{f'{e32:8.3f}'[4:]}"


def _header(f, title, Z, A, reaction, mf, mt, extra):
    from physics.hf.angout import _w_char, _w_real
    from physics.hf.core.constants import nuclide_symbol

    nuc = f"{nuclide_symbol(Z)}{A}"
    _w_char(f, 0, "header")
    _w_char(f, 2, "title", f"{nuc}{title}")
    _w_char(f, 2, "source", "INCOGNITA (TALYS-2.x port)")
    _w_char(f, 2, "user", "Unknown User")
    _w_char(f, 2, "date", datetime.date.today().isoformat())
    _w_char(f, 2, "format", "YANDF-0.4")
    _w_char(f, 0, "target")
    _w_char(f, 2, "Z", Z)
    _w_char(f, 2, "A", A)
    _w_char(f, 2, "nuclide", nuc)
    _w_char(f, 0, "reaction")
    _w_char(f, 2, "type", reaction)
    _w_char(f, 2, "ENDF_MF", mf)
    _w_char(f, 2, "ENDF_MT", mt)
    for k, v in extra:
        _w_real(f, 2, k, v)


def _rows(f, data):
    for row in zip(*data):  # noqa: B905
        f.write("".join(f"{float(np.float32(v)):15.6E}" for v in row) + "\n")


def write_files(arr: dict, meta: dict, out_dir) -> list[str]:
    """TALYS's spectrum, DDX, gamma-line and average-energy files of the run in `out_dir` (YANDF-0.4 names and columns).

    TALYS: spectraout.f90:1, ddxout.f90:1, gamdisout.f90:1, write_block.f90:1
    Test: tests/hf/test_specobs.py
    """
    from physics.hf.angout import _datablock, _w_char

    d = Path(out_dir)
    d.mkdir(parents=True, exist_ok=True)
    s = meta["settings"]
    Z, A, k0 = meta["Z"], meta["A"], meta["k0"]
    k = PARSYM[k0]
    E = meta["e_inc_mev"]
    written: list[str] = []
    opened: set[str] = set()

    def fopen(fn, block):
        mode = "a" if (block and fn in opened) else "w"
        opened.add(fn)
        written.append(fn)
        return open(d / fn, mode)

    for t, x in enumerate(PARSYM):
        stem = f"{x}spec.tot"
        if stem not in arr or x not in s["filespectrum"]:
            continue
        cols = ["E-out", "xs", "Direct", "Preequilibrium", "Multiple_preeq", "Compound", "Preeq_ratio"]
        keys = [":E", "", ":direct", ":preeq", ":multiple_preeq", ":compound", ":preeq_ratio"]
        if k0 > 2 or t > 2:
            cols += ["Break-up_ratio", "Stripping", "Knock-out", "Break-up"]
            keys += [":breakup_ratio", ":stripping", ":knockout", ":breakup"]
        un = ["MeV"] + ["mb/MeV"] * 5 + [""] + ([""] + ["mb/MeV"] * 3 if len(cols) > 7 else [])
        for i, e in enumerate(E):
            if not meta["present"][stem][i]:
                continue
            m = np.isfinite(arr[stem + ":E"][i])
            fn = f"{x}spec.tot" if s["blockspectra"] else f"{x}spec{_efile(e)}.tot"
            with fopen(fn, s["blockspectra"]) as f:
                _header(f, f"({k},x{x}) emission spectrum at {float(np.float32(e)):12.6E} MeV", Z, A, f"({k},x{x})", 6, 5, [])
                _w_char(f, 2, "parameters")
                from physics.hf.angout import _w_real

                _w_real(f, 4, "E-incident [MeV]", e)
                _w_real(f, 4, "E-average [MeV]", arr[f"Eaverage_{x}.out"][i])
                _w_char(f, 2, "quantity")
                _w_char(f, 4, "type", "emission spectrum")
                _datablock(f, 2, cols, un, int(m.sum()))
                _rows(f, [arr[stem + kk][i][m] for kk in keys])
        fn = f"Eaverage_{x}.out"
        with fopen(fn, False) as f:
            _header(f, f"({k},x{x}) average emission energy", Z, A, f"({k},x{x})", 0, 0, [])
            _w_char(f, 2, "quantity")
            _w_char(f, 4, "type", "emission energy")
            ok = np.isfinite(arr[fn])
            _datablock(f, 2, ["E", "E-average"], ["MeV", "MeV"], int(ok.sum()))
            _rows(f, [E[ok], arr[fn][ok]])
    for name in sorted(n for n in arr if "ddxA" in n or "ddxE" in n):
        if ":" in name:
            continue
        x = name[0]
        is_a = "ddxA" in name
        val = float(name[5:-4])
        for i, e in enumerate(E):
            if not meta["present"].get(name, np.zeros(len(E), bool))[i]:
                continue
            if is_a:
                fn = f"{x}ddx.deg" if s["blockddx"] else f"{x}ddxE{_efile(e)}{name[4:]}"
                m = np.isfinite(arr[f"{x}spec.tot:E"][i])
                first = arr[f"{x}spec.tot:E"][i][m]
                data = [first] + [arr[name if c == "" else f"{name}:{c}"][i][m] for c in ("",) + COLS]
                cols, un = ["E-out", "xs", "Direct", "Preequilibrium", "Multiple_preeq", "Compound"], ["MeV"] + ["mb/MeV/sr"] * 5
                extra = [("E-incident [MeV]", e), ("Angle [deg]", val)]
            else:
                fn = f"{x}ddx.MeV" if s["blockddx"] else f"{x}ddxE{_efile(e)}{name[4:]}"
                th = arr["anglecont"]
                data = [th] + [arr[name if c == "" else f"{name}:{c}"][i] for c in ("",) + COLS]
                cols, un = ["Angle", "xs", "Direct", "Preequilibrium", "Multiple_preeq", "Compound"], ["deg"] + ["mb/MeV/sr"] * 5
                extra = [("E-incident [MeV]", e), ("E-emission [MeV]", val)]
            with fopen(fn, s["blockddx"]) as f:
                _header(f, f"({k},x{x}) double-differential cross section at {float(np.float32(e)):12.6E} MeV", Z, A,
                        f"({k},x{x})", 6, 5, extra)
                _w_char(f, 2, "quantity")
                _w_char(f, 4, "type", "double-differential cross section")
                _datablock(f, 2, cols, un, len(data[0]))
                _rows(f, data)
    for name, (Zr, Ar, n1, n2) in sorted(meta.get("lines", {}).items()):
        with fopen(name, False) as f:
            _header(f, f"({k},xg_{n1}-{n2}) gamma-ray production cross section", Z, A, f"({k},xg_{n1}-{n2})", 0, 0,
                    [("gamma energy [MeV]", arr[name + ":E"][0])])
            _w_char(f, 2, "quantity")
            _w_char(f, 4, "type", "cross section")
            _datablock(f, 2, ["E", "xs"], ["MeV", "mb"], len(E))
            _rows(f, [E, arr[name]])
    return sorted(set(written))


__all__ = ["ENV", "ENV_DIR", "META", "active", "add_to_results", "anglecont", "begin_run", "build", "ddx_wanted",
           "end_run", "energy_spectra", "settings", "take_discad", "wanted", "write_files"]
