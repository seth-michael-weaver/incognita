"""Exclusive channel spectra `sp<nnnnnn>.tot` / `sp<nnnnnn>.fis`, OUTPUT ONLY.

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

What it gives (Results.spectra keys, TALYS's file names without the incident energy; arrays (C, M) on the run's
energies, NaN where TALYS writes no row at that energy, M = the egrid points ebegin(0)..eendhigh):

    sp<nnnnnn>.tot:E               egrid (C, M) MeV                                channelsout.f90, column 1
    sp<nnnnnn>.tot:<x>             xschannelsp(idc, x) mb/MeV, x in g n p d t h a  columns 2-8; for sp000000 the
                                   particle columns are xsngnspec (zero unless `endf y`, multiple.f90:719-723)
    sp<nnnnnn>.fis:E / :<x>        xsfischannelsp (fissile targets)                channelsout.f90, sp*.fis

A channel appears at an energy when TALYS writes its file there: chanopen and xschannel >= xseps (.tot), xsfischannel
> xseps (.fis). Switch: the deck's `outspectra y` (or anything that implies it: ddxmode > 0, endf y, recoil y,
INCOGNITA_SPECOBS=1) together with `channels y` (TALYS computes the exclusive spectra only inside channels.f90).
`INCOGNITA_SPECOBS_DIR=<dir>` also writes the files (sp100000E0014.000.tot, sp000000E0014.000.fis). Default: nothing
is computed and every engine array is unchanged; with the switch the C driver takes the Python channels (as
INCOGNITA_CHANOBS does), which give the same cross sections.

How (none of it feeds back into the engine): channels.f90's exclusive-channel loop is walked again on the energy's
channel inputs (the same `feedexcl` / `popexcl` / `xsexcl` recurrences as `emission.channels`), carrying `specexcl`
(channel, ejectile, residual bin, emission energy): the binary emission per residual bin (`binemis`, from the raw
binary parts `specout` recorded), the first term (the source channel's spectrum times feedexcl / popexcl) and the second
(specemission.f90's smearing of the last emitted particle over the mother and residual bins); the final spectra are the
ground state + isomer bins, the fission spectra the fisfeedex-weighted bins.

TALYS quirks kept: for the photon source (the channel itself), specemission's lower-bin feed `xsexcl(idorg, nex-1)`
is read while the channel is being built, so at nex - 1 = nexout it is the partial photon sum and below it zero;
`xsexcl(idorg, maxex+1)` of the initial compound state is zero (reset at idnum 0), so the upper feed of the CN's top
bin is zero; the discrete photon lines are not in the gamma spectra.

TALYS routines ported here (file:line of the subroutine statement):
    channels.f90:1 (channels)            specexcl, xschannelsp, xsfischannelsp (lines 330-475)
    specemission.f90:1 (specemission)    the spectrum of the last emitted particle per mother -> residual bin
    binemission.f90:1 (binemission)      binemis, the binary emission per residual continuum bin (lines 171-205)
    channelsout.f90:1 (channelsout)      file names, columns, the chanopen / xseps conditions
Task: T10 (physics/hf/CONTRACT.md section 7; output only). Acceptance test: KW-B4B
(tests/hf/test_kwcov_b4b.py, scripts/kwcov/b4b_compare.py, docs/hf/COVERAGE_PLAN.md).
"""

from __future__ import annotations

from pathlib import Path

import numpy as np

PARSYM = "gnpdtha"
PARZ = (0, 0, 1, 1, 1, 2, 2)
PARN = (0, 1, 0, 1, 2, 1, 2)

_ON: dict | None = None  # the run's settings while a run records
ENERGIES: list[dict] = []  # one per recorded incident energy
_STATE = None  # ExclusiveState of the Python driver (engine.py) across its energies


# ------------------------------------------------------------------------------------------------ switches
def wanted_for(options) -> bool:
    """True when the run's Options ask for the exclusive spectra: outspectra (or what implies it) and channels y.

    TALYS: channels.f90:1 (channels) -- `flagspec` inside the channels y loop
    Test: tests/hf/test_kwcov_b4b.py
    """
    from physics.hf import specobs

    try:
        s = specobs.settings(options)
    except Exception:  # noqa: BLE001
        return False
    return bool(s is not None and s["spec"] and bool(getattr(options, "flagchannels", False)))


def begin_run(cas) -> bool:
    """A new engine run: fix the switches (called by specobs.begin_run).

    TALYS: (none -- a port switch)
    Test: tests/hf/test_kwcov_b4b.py
    """
    global _ON, _STATE
    ENERGIES.clear()
    _STATE = None
    _ON = None
    if wanted_for(cas.options):
        o = cas.options
        _ON = dict(Z=int(cas.Zt), A=int(cas.At), k0=int(cas.k0), flagendf=bool(o.flagendf),
                   flagfission=bool(getattr(o, "flagfission", False)))
    return _ON is not None


def active() -> bool:
    """True while a run records exclusive spectra.

    TALYS: (none -- a port switch)
    Test: tests/hf/test_kwcov_b4b.py
    """
    return _ON is not None


def end_run() -> None:
    """Forget the run (after add_to_results).

    TALYS: (none -- a port switch)
    Test: tests/hf/test_kwcov_b4b.py
    """
    global _ON, _STATE
    _ON = None
    _STATE = None
    ENERGIES.clear()


# ------------------------------------------------------------------------------------------------ helpers
def _locate(xx, ib: int, ie: int, x: float) -> int:
    from physics.hf.specout import _locate as loc

    return loc(xx, ib, ie, x)


class _Grid:
    """The energy's emission grid (egrid, Ebottom, Etop, deltaE, ebegin, eend) as `specout` closed it."""

    def __init__(self, cur: dict):
        self.eg = np.asarray(cur["egrid"], float)
        self.eb = np.asarray(cur["ebottom"], float)
        self.et = np.asarray(cur["etop"], float)
        self.de = np.asarray(cur["deltae"], float)
        self.ebegin = {int(t): int(v) for t, v in cur["ebegin"].items()}
        self.eend = {int(t): int(v) for t, v in cur["eend"].items()}
        self.speceps = float(cur["speceps"])
        self.n = len(self.eg)
        self.eendhigh = min(max(self.eend.values()), self.n - 1)


def binemis(cur: dict, nuc_grid: dict, etotal: float, g: _Grid) -> dict:
    """binemis(type, nexout, nen) of binemission.f90:171-205 on the raw binary parts `specout` recorded:
    {type: (nr, M) array} for the binary residual of each ejectile (continuum bins only).

    TALYS: binemission.f90:1 (binemission)
    Test: tests/hf/test_kwcov_b4b.py
    """
    out = {}
    rec = cur.get("binary") or {}
    for t, ent in (rec.get("types") or {}).items():
        t = int(t)
        key = (PARZ[t], PARN[t])
        if key not in nuc_grid:
            continue
        ex, dex, nl, mx = nuc_grid[key]
        ib, ie = int(ent["ebegin"]), int(ent["eend"])
        if ib >= ie or mx <= nl:
            continue
        raw = ent.get("raw") or ent
        xb = (np.asarray(raw["xsemis"], float) + np.asarray(raw["xspreeq"], float) + np.asarray(raw["xsgr"], float))
        xb = np.pad(xb, (0, max(0, g.n - len(xb))))[: g.n]
        ss = float(ent["sep_mev"])
        eo_nl = etotal - ss - ex[nl]
        B = np.zeros((mx + 1, g.n))
        for nexout in range(nl + 1, mx + 1):
            d = dex[nexout]
            eo = etotal - ss - ex[nexout]
            emin, emax = eo - 0.5 * d, eo + 0.5 * d
            nb = _locate(g.eb, ib, ie, emin)
            ne = _locate(g.eb, ib, ie, emax)
            nb = max(nb, 1)
            if ne < nb:
                continue
            for nen in range(nb, ne + 1):
                if g.eg[nen] >= eo_nl:
                    continue
                B[nexout, nen] = xb[nen]
            fb = (emin - g.eb[nb]) / g.de[nb]
            ft = (g.et[ne] - emax) / g.de[ne]
            if nexout == nl + 1:
                ft = 0.0
            if ne == nb:
                B[nexout, nb] *= 1.0 - fb - ft
            else:
                B[nexout, nb] *= 1.0 - fb
                B[nexout, ne] *= 1.0 - ft
        out[t] = B
    return out


class _Geom:
    """specemission.f90's bin geometry per (mother, type, nex, nexout), shared by every channel that passes there."""

    def __init__(self, g: _Grid, nuc_grid: dict, sep: dict):
        self.g, self.ng, self.sep, self.cache, self.nexmax = g, nuc_grid, sep, {}, {}

    def of(self, mk, t: int, nex: int, nexout: int):
        key = (mk, t, nex, nexout)
        got = self.cache.get(key, 0)
        if got != 0:
            return got
        got = self.cache[key] = self._make(mk, t, nex, nexout)
        return got

    def _make(self, mk, t, nex, nexout):
        g = self.g
        ex_m, dex_m, _, _ = self.ng[mk]
        dk = (mk[0] + PARZ[t], mk[1] + PARN[t])
        if dk not in self.ng:
            return None
        ex_d, dex_d, NL, mx_d = self.ng[dk]
        exinc, dexinc = ex_m[nex], dex_m[nex]
        ex0p, ex0m = exinc + 0.5 * dexinc, exinc - 0.5 * dexinc
        SS = self.sep[mk].get(t, 0.0)
        exm = ex0p - SS
        if t > 1:
            exm -= g.eg[g.ebegin[t]]
        k = (mk, t, nex)
        nexmax = self.nexmax.get(k)
        if nexmax is None:
            nexmax = -1
            for n2 in range(mx_d, -1, -1):
                if ex_d[n2] - 0.5 * dex_d[n2] < exm:
                    nexmax = n2
                    break
            self.nexmax[k] = nexmax
        if nexmax < 0 or nexout > mx_d:
            return None
        exout, dex = ex_d[nexout], dex_d[nexout]
        cont = nexout > NL
        edge = False
        if cont:
            ex1min = exout - 0.5 * dex
            if nexout == nexmax and t >= 1:
                ex1plus = ex0p - SS
                exout = 0.5 * (ex1plus + ex1min)
            else:
                ex1plus = exout + 0.5 * dex
            emax = ex0p - SS - ex1min
            emin = max(ex0m - SS - ex1plus, 0.0)
            eout = 0.5 * (emin + emax)
        else:
            exm2 = exout + SS
            edge = exm2 <= ex0p and exm2 > ex0m
            if edge:
                eout = 0.5 * (ex0p + exm2) - SS - exout
                emin = 0.0
            else:
                eout = exinc - SS - exout
                emin = ex0m - SS - exout
            emax = ex0p - SS - exout
        ib, ie = g.ebegin[t], g.eend[t]
        nb = max(_locate(g.eb, ib, ie, emin), 1)
        ne = _locate(g.eb, ib, ie, emax)
        if ne < nb:
            return None
        sl = slice(nb, ne + 1)
        egs = g.eg[sl]
        fb = (emin - g.eb[nb]) / g.de[nb]
        ft = 0.0 if nexout == NL + 1 else (g.et[ne] - emax) / g.de[ne]
        corr = np.ones(ne - nb + 1)
        if ne == nb:
            corr[0] = 1.0 - fb - ft
        else:
            corr[0] = 1.0 - fb
            corr[-1] = 1.0 - ft
        low = egs <= eout
        edist = np.where(low, eout - egs, egs - eout)
        dE = emax - emin
        return dict(cont=cont, edge=edge, sl=sl, low=low, edist=edist, dE=dE, dEhalf=0.5 * dE, emin=emin,
                    dexinc=dexinc, wde=g.de[sl] * corr, de=g.de[sl])


def _specemission(geo, F, nex: int, nexout: int, f0: float, fm: float, fp: float):
    """specemission.f90 for one mother bin -> residual bin given the mother's dense feedexcl F (rows nex, columns
    nexout) and feed0 / feedm / feedp = xsexcl(idorg, nex + 0/-1/+1) / popexcl: (slice, spectrum) or None.

    `geo` is the cached geometry (_Geom.of)."""
    if geo is None:
        return None
    R, Cn = F.shape

    def f(a, b):
        return F[a, b] if (0 <= a < R and 0 <= b < Cn) else 0.0

    xso00 = f(nex, nexout) * f0
    if xso00 == 0.0:
        return None
    xsom0 = f(nex - 1, nexout) * fm
    xsop0 = f(nex + 1, nexout) * fp
    ed, low = geo["edist"], geo["low"]
    dE, dEh = geo["dE"], geo["dEhalf"]
    if geo["cont"]:
        xso0m = f(nex, nexout - 1) * f0
        xsopm = f(nex + 1, nexout - 1) * fp
        xsomp = f(nex - 1, nexout + 1) * fm
        xso0p = f(nex, nexout + 1) * f0
        with np.errstate(divide="ignore", invalid="ignore"):
            if geo["emin"] <= 0.0001:
                tlo = xso00 * (1.0 - ed / dEh)
            else:
                t1 = xso00 + 0.5 * ed / dE * (xsom0 - xso00)
                t2 = xso0p + 0.5 * ed / dE * (xsomp - xso0p)
                tlo = t1 + 0.5 * ed / dE * (t2 - t1)
            if xsop0 == 0.0:
                t1 = xso00 * (1.0 - 0.5 * ed / dEh)
                t2 = 0.0
            else:
                t1 = xso00 + 0.5 * ed / dE * (xsop0 - xso00)
                t2 = xso0m + 0.5 * ed / dE * (xsopm - xso0m)
            thi = t1 + 0.5 * ed / dE * (t2 - t1)
    else:
        with np.errstate(divide="ignore", invalid="ignore"):
            if geo["edge"]:
                tlo = xso00 * (1.0 - ed / dEh)
            else:
                tlo = xso00 + ed / geo["dexinc"] * (xsom0 - xso00)
            if xsop0 == 0.0:
                thi = xso00 * (1.0 - ed / dEh)
            else:
                thi = xso00 + ed / geo["dexinc"] * (xsop0 - xso00)
    term = np.maximum(np.where(low, tlo, thi), 0.0)
    w = term * geo["wde"]
    sw = float(w.sum())
    if sw == 0.0 or not np.isfinite(sw):
        return None
    return geo["sl"], xso00 / sw * w / geo["de"]


# ------------------------------------------------------------------------------------------------ the channel loop
def energy_spectra(cinp, nuc_grid: dict, cur: dict, state, flagendf: bool = False) -> dict:
    """channels.f90's loop with `flagspec`: {code: dict(xs, xsfis, sp (7, M), spfis (7, M))} of every channel TALYS
    would write at this energy (chanopen; xs >= xseps for .tot, xsfis > xseps for .fis), M = egrid points.

    `nuc_grid[(zc, nc)] = (Ex, deltaEx, Nlast, maxex)`; `cur` is the `specout` energy record (egrid, binary parts);
    `state` is the ExclusiveState before this energy (updated in place, as channels.f90 does).

    TALYS: channels.f90:1 (channels), specemission.f90:1 (specemission), channelsout.f90:1 (channelsout)
    Test: tests/hf/test_kwcov_b4b.py
    """
    from physics.hf.emission.channels import _channel_keys, _limits_of, caps, numchantot
    from physics.hf.emission.feed_table import dense_feed

    g = _Grid(cur)
    nuc = cinp.nuclei
    xseps = float(cinp.xseps_mb)
    root = nuc[(0, 0)]
    top0 = root.maxex + 1
    etotal = float((cur.get("binary") or {}).get("etotal_mev", 0.0))
    B = binemis(cur, nuc_grid, etotal, g)
    sep = {k: dict(n.sep_mev) for k, n in nuc.items()}
    geom = _Geom(g, nuc_grid, sep)
    M = g.n
    live = [t for t in range(7) if not cinp.parskip[t]]

    feeds: dict = {}

    def feed_of(mk, t):
        """(F dense (maxex+2, nr_daughter), pop (maxex+2,)) of mother mk, type t; F row top0 for (0,0)."""
        key = (mk, t)
        got = feeds.get(key)
        if got is None:
            m = nuc[mk]
            dk = (mk[0] + PARZ[t], mk[1] + PARN[t])
            nr = (nuc[dk].maxex + 1) if dk in nuc else 1
            fe = m.feedexcl_mb.get(t)
            rows = max(m.maxex + 2, top0 + 1 if mk == (0, 0) else 0)
            F = dense_feed(fe, rows, nr) if fe else np.zeros((rows, nr))
            pop = np.zeros(rows)
            for nex, v in m.popexcl_mb.items():
                if 0 <= nex < rows:
                    pop[nex] = v
            got = feeds[key] = (F, pop)
        return got

    xsexcl: dict[int, np.ndarray] = {}
    spx: dict[int, np.ndarray] = {}
    idchannel: dict[int, int] = {}
    slots: dict[int, list[int]] = {}
    xsch: dict[int, float] = {}
    xsfis: dict[int, float] = {}
    spsum: dict[int, np.ndarray] = {}
    spfis: dict[int, np.ndarray] = {}
    idnum = -1
    qex: dict[int, float] = {}
    q00 = root.sep_mev.get(cinp.k0, 0.0) + cinp.targete_mev  # Qexcl(0, 0)
    cap, nchtot = caps(), numchantot()
    from physics.hf.emission.channels import NUMNCHAN, NUMZCHAN

    zend = min(NUMZCHAN, cinp.maxz, cinp.zinit)
    nend = min(NUMNCHAN, cinp.maxn, cinp.ninit)
    st = state
    for zix in range(zend + 1):
        for nix in range(nend + 1):
            if (zix, nix) not in nuc:
                continue
            res = nuc[(zix, nix)]
            lim = _limits_of(zix, nix, tuple(cinp.parinclude), cinp.maxchannel, cap)
            for key in _channel_keys(zix, nix, lim, cinp.maxchannel):
                i_n, ip, idd_, it, ih, ia = key
                if key not in st.chanopen and st.idnumfull:
                    continue
                if idnum == nchtot:
                    continue
                npart = i_n + ip + idd_ + it + ih + ia
                ident = 100000 * i_n + 10000 * ip + 1000 * idd_ + 100 * it + 10 * ih + ia
                idnum += 1
                idchannel[idnum] = ident
                slots.setdefault(ident, []).append(idnum)
                identorg: dict[int, int] = {}
                q0 = q00 if idnum == 0 else 0.0  # Qexcl(idnum, 0), as emission.channels forms it
                for t in live:
                    idd = ident if t == 0 else ident - 10 ** (6 - t)
                    if idd < 0:
                        continue
                    for idorg in reversed(slots.get(idd, ())):
                        if idorg <= idnum and idchannel.get(idorg) == idd:
                            identorg[t] = idorg
                            break
                    else:
                        continue
                    mk = (zix - PARZ[t], nix - PARN[t])
                    if q0 == 0.0 and mk in nuc:
                        q0 = (q0 if identorg[t] == idnum else qex[identorg[t]]) - nuc[mk].sep_mev.get(t, 0.0)  # (a slot given back keeps a stale Q)
                    if min(res.nlast, len(res.edis_mev) - 1) >= 0:
                        q0 = q0 - res.edis_mev.get(0, 0.0)
                qex[idnum] = q0
                nr = res.maxex + 1
                xe = np.zeros(nr + 1)  # index nr (= maxex + 1) stays 0 (xsexcl(idnum, maxex+1) after the reset)
                S = np.zeros((7, nr, M))
                # sources other than the photon (completed channels): binary + first + second term
                for t in live:
                    if t == 0 or t not in identorg:
                        continue
                    mk = (zix - PARZ[t], nix - PARN[t])
                    if mk not in nuc:
                        continue
                    idorg = identorg[t]
                    F, pop = feed_of(mk, t)
                    k = min(F.shape[1], nr)
                    if mk == (0, 0):
                        xe[:k] += F[top0, :k]
                        if t in B:
                            kb = min(B[t].shape[0], nr)
                            S[t, :kb] += B[t][:kb]
                    mx = nuc[mk].maxex
                    xo = xsexcl[idorg]
                    so = spx[idorg]
                    for nex in range(mx, 0, -1):
                        if pop[nex] == 0.0:
                            continue
                        row = F[nex, :k]
                        nz = np.flatnonzero(row)
                        if nz.size == 0:
                            continue
                        r = row[nz] / pop[nex]
                        xe[nz] += r * xo[nex]
                        S[:, nz, :] += r[None, :, None] * so[:, nex, None, :]
                        f0 = xo[nex] / pop[nex]
                        fm = xo[nex - 1] / pop[nex - 1] if pop[nex - 1] != 0.0 else 0.0
                        fp = (xo[nex + 1] / pop[nex + 1]) if (nex + 1 < len(pop) and pop[nex + 1] != 0.0
                                                               and nex + 1 < len(xo)) else 0.0
                        if pop[nex] <= g.speceps:
                            continue
                        for nexout in nz.tolist():
                            got = _specemission(geom.of(mk, t, nex, nexout), F, nex, nexout, f0, fm, fp)
                            if got is not None:
                                S[t, nexout, got[0]] += got[1]
                # the photon source: the channel itself, walked down from its top bin (channels.f90:330, type 0 first)
                if 0 in identorg:
                    mk = (zix, nix)
                    F, pop = feed_of(mk, 0)
                    k = min(F.shape[1], nr)
                    NLc = res.nlast
                    top = F[top0, :k] if mk == (0, 0) else None
                    if top is not None and 0 in B:
                        kb = min(B[0].shape[0], nr)
                        S[0, :kb] += B[0][:kb]
                    part = xe.copy()  # the particle sources are in already; the photon pass adds per nexout
                    # TALYS processes type 0 before the particle types at every nexout, so the partial sum that
                    # specemission reads at nex - 1 == nexout holds the photon feeding only
                    for nexout in range(nr - 1, -1, -1):
                        partial = top[nexout] if (top is not None and nexout < k) else 0.0
                        for nex in range(res.maxex, nexout, -1):
                            fv = F[nex, nexout] if nexout < k else 0.0
                            if fv == 0.0 or pop[nex] == 0.0:
                                continue
                            r = fv / pop[nex]
                            term2 = r * xe[nex]
                            part[nexout] += term2
                            partial += term2
                            S[:, nexout, :] += r * S[:, nex, :]
                            if nex <= NLc or pop[nex] <= g.speceps:
                                continue
                            f0 = xe[nex] / pop[nex]
                            if nex - 1 > nexout:
                                xm = xe[nex - 1]
                            elif nex - 1 == nexout:
                                xm = partial
                            else:
                                xm = 0.0
                            fm = xm / pop[nex - 1] if pop[nex - 1] != 0.0 else 0.0
                            fp = xe[nex + 1] / pop[nex + 1] if (nex + 1 < len(pop) and pop[nex + 1] != 0.0) else 0.0
                            got = _specemission(geom.of(mk, 0, nex, nexout), F, nex, nexout, f0, fm, fp)
                            if got is not None:
                                S[0, nexout, got[0]] += got[1]
                        xe[nexout] = part[nexout]
                        if top is not None and nexout < k:
                            xe[nexout] += top[nexout]
                xsexcl[idnum] = xe
                spx[idnum] = S
                # total and per isomer (channels.f90:398-425)
                tot = 0.0
                sp = np.zeros((7, M))
                for nexout in range(min(res.maxex, res.nlast), -1, -1):
                    if res.tau_s.get(nexout, 0.0) != 0.0 or nexout == 0:
                        tot += float(xe[nexout])
                        sp += S[:, nexout, :]
                fis = 0.0
                spf = np.zeros((7, M))
                if cinp.flagfission:
                    if zix == 0 and nix == 0:
                        fis += root.fisfeedex_mb.get(top0, 0.0)
                    for nex in range(res.maxex, 0, -1):
                        p = res.popexcl_mb.get(nex, 0.0)
                        if p != 0.0:
                            term = res.fisfeedex_mb.get(nex, 0.0) / p
                            fis += term * float(xe[nex])
                            spf += term * S[:, nex, :]
                if q0 > 0.0 and tot <= xseps:  # non-threshold floor (channels.f90:435-445): file, zero spectra
                    tot = xseps
                xsch[idnum], xsfis[idnum] = tot, fis
                spsum[idnum], spfis[idnum] = sp, spf
                # idnum give-back (channels.f90:630-637)
                if (tot >= xseps and not st.idnumfull) or npart == 0:
                    st.chanopen.add(key)
                if tot < xseps and npart > 1 and key not in st.chanopen:
                    idnum -= 1
                if st.opennum == nchtot - 10:
                    st.idnumfull = True
    out = {}
    for i in range(idnum + 1):
        code = idchannel[i]
        d = [int(c) for c in f"{code:06d}"]
        if tuple(d) not in st.chanopen:
            continue
        ent = dict(xs=xsch[i], xsfis=xsfis[i])
        if xsch[i] >= xseps:
            sp = spsum[i].copy()
            if code == 0:  # channelsout.f90:669-671: the (k0,g x) columns are xsngnspec
                sp[1:] = 0.0
                if flagendf:
                    cn = (cur.get("per_nucleus_talys") or {}).get((0, 0))
                    if cn is not None:
                        v = np.asarray(cn[0], float) + np.asarray(cn[1], float)
                        sp[1:, : v.shape[1]] = v[1:, :M]
            ent["sp"] = sp
        if cinp.flagfission and xsfis[i] > xseps:
            ent["spfis"] = spfis[i]
        out[code] = ent
    return out


def nuclear_grids(cinp, st) -> dict:
    """(Ex, deltaEx, Nlast, maxex) of every channel nucleus from the cascade's NucleusSpec records.

    TALYS: (none -- Incognita extension, not a TALYS routine)
    Test: tests/hf/test_kwcov_b4b.py
    """
    out = {}
    for key, n in cinp.nuclei.items():
        sp = getattr(st, "spec", {}).get(key)
        if sp is None:
            continue
        mx = int(sp.maxex)
        ex = np.zeros(mx + 3)
        dex = np.zeros(mx + 3)
        k = min(len(sp.ex_mev), mx + 1)
        ex[:k] = np.asarray(sp.ex_mev, float)[:k]
        dex[:k] = np.asarray(sp.dex_mev, float)[:k]
        out[key] = (ex, dex, int(n.nlast), mx)
    return out


def record(cinp, st, state=None) -> None:
    """After specout.end_energy: the exclusive spectra of this energy (output only; errors are recorded, not raised).
    `state` = the ExclusiveState before this energy's channels (engine_c passes its snapshot); None = the module's own
    (engine.py's driver keeps one across its energies).

    TALYS: channels.f90:1 (channels)
    Test: tests/hf/test_kwcov_b4b.py
    """
    global _STATE
    if _ON is None:
        return
    from physics.hf import specout
    from physics.hf.emission.channels import ExclusiveState

    cur = specout.ENERGIES[-1] if specout.ENERGIES else None
    e = float(cinp.e_inc_mev)
    rec = dict(e_inc_mev=e)
    try:
        if cur is None or abs(float(cur["e_inc_mev"]) - e) > 1e-9 or "egrid" not in cur:
            raise RuntimeError("no specout record for this energy")
        if state is None:
            if _STATE is None:
                _STATE = ExclusiveState()
            state = _STATE
        rec["channels"] = energy_spectra(cinp, nuclear_grids(cinp, st), cur, state, bool(_ON["flagendf"]))
        g = _Grid(cur)
        rec["egrid"] = g.eg[g.ebegin.get(0, 0): g.eendhigh + 1]
        rec["sl"] = (g.ebegin.get(0, 0), g.eendhigh + 1)
    except Exception as exc:  # noqa: BLE001 -- output only
        rec["error"] = f"{type(exc).__name__}: {exc}"
    ENERGIES.append(rec)


def build(e_inc) -> tuple[dict, dict]:
    """Results.spectra arrays of the run on the energies `e_inc` (the `specout` order) and the file metadata.

    TALYS: channelsout.f90:1 (channelsout)
    Test: tests/hf/test_kwcov_b4b.py
    """
    if _ON is None:
        return {}, {}
    e_inc = [float(x) for x in e_inc]
    C = len(e_inc)
    byE = {round(r["e_inc_mev"], 6): r for r in ENERGIES}
    M = max([len(r.get("egrid", ())) for r in ENERGIES] + [0])
    names: dict[str, list] = {}
    errors = []
    for i, e in enumerate(e_inc):
        r = byE.get(round(e, 6))
        if r is None or "channels" not in r:
            if r is not None and "error" in r:
                errors.append(f"E={e:g}: {r['error']}")
            continue
        a, b = r["sl"]
        for code, ent in r["channels"].items():
            for kind, k in (("tot", "sp"), ("fis", "spfis")):
                if k in ent:
                    names.setdefault(f"sp{code:06d}.{kind}", []).append((i, r["egrid"], ent[k][:, a:b]))
    arr: dict[str, np.ndarray] = {}
    present = {}
    for name, rows in names.items():
        E = np.full((C, M), np.nan)
        V = np.full((7, C, M), np.nan)
        pres = np.zeros(C, bool)
        for i, eg, v in rows:
            E[i, : len(eg)] = eg
            V[:, i, : v.shape[1]] = v
            pres[i] = True
        arr[name + ":E"] = E
        for t in range(7):
            arr[f"{name}:{PARSYM[t]}"] = V[t]
        present[name] = pres
    meta = dict(present=present, e_inc_mev=np.array(e_inc), Z=_ON["Z"], A=_ON["A"], k0=_ON["k0"], errors=errors)
    return arr, meta


# ------------------------------------------------------------------------------------------------ TALYS files
def _reaction(code: int, k0: int, fis: bool) -> str:
    """channelsout.f90's reacstring / fisstring."""
    d = [int(c) for c in f"{code:06d}"]
    s = "(" + PARSYM[k0] + ","
    if sum(d) == 0:
        s += "g"
    for n, x in zip(d, "npdtha"):  # noqa: B905
        if n == 1:
            s += x
        elif n > 1:
            s += f"{n}{x}"
    if sum(d) == 1 and d[k0 - 1] == 1 and k0 >= 1:
        s += "'"
    return s + ("f)" if fis else ")")


def write_files(arr: dict, meta: dict, out_dir) -> list[str]:
    """sp<nnnnnn>E<eeee.eee>.tot / .fis (channelsout.f90's non-block names) in `out_dir`.

    TALYS: channelsout.f90:1 (channelsout)
    Test: tests/hf/test_kwcov_b4b.py
    """
    from physics.hf.angout import _datablock, _w_char, _w_real
    from physics.hf.specobs import _efile, _header, _rows

    d = Path(out_dir)
    d.mkdir(parents=True, exist_ok=True)
    written = []
    Z, A, k0 = meta["Z"], meta["A"], meta["k0"]
    cols = ["E-out", "gamma", "neutron", "proton", "deuteron", "triton", "helium-3", "alpha"]
    un = ["MeV"] + ["mb/MeV"] * 7
    for name, pres in sorted(meta["present"].items()):
        code, kind = int(name[2:8]), name[9:]
        for i, e in enumerate(meta["e_inc_mev"]):
            if not pres[i]:
                continue
            m = np.isfinite(arr[name + ":E"][i])
            fn = f"{name[:8]}E{_efile(e)}.{kind}"
            reac = _reaction(code, k0, kind == "fis")
            q = "fission emission spectrum" if kind == "fis" else "emission spectrum"
            with open(d / fn, "w") as f:
                _header(f, f"{reac} {q} at {float(np.float32(e)):12.6E} MeV", Z, A, reac, 6 if kind == "tot" else 0,
                        0, [])
                _w_real(f, 2, "E-incident [MeV]", e)
                _w_char(f, 2, "quantity")
                _w_char(f, 4, "type", q)
                _datablock(f, 2, cols, un, int(m.sum()))
                _rows(f, [arr[name + ":E"][i][m]] + [arr[f"{name}:{x}"][i][m] for x in PARSYM])
            written.append(fn)
    return written


__all__ = ["ENERGIES", "active", "begin_run", "binemis", "build", "end_run", "energy_spectra", "nuclear_grids",
           "record", "wanted_for", "write_files"]
