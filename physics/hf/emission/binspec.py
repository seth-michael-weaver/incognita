"""Binary (first-emission) emission spectra of every ejectile, and TALYS's full binary cross section.

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

TALYS routines ported here (file:line of the subroutine statement):
    binemission.f90:1 (binemission)     -- compound continuum emission spectrum `xsemis`, normalised by `binnorm`
    binaryspectra.f90:1 (binaryspectra) -- xsbinemis = xscomp + xspreeq + xsgr
    binary.f90:345-375                  -- binemissum (integrated continuum) and the discrete lines

XDHARD (Incognita extension, OUTPUT ONLY; SPECOUT took this file onto B78f without XDHARD's xsfeed hunk, so
`full_xsbinary` is recorded, never fed back): the port had no inclusive/binary emission spectra (spectra.f90,
binaryspectra.f90 not ported). `record` is called by `engine`/`engine_c` after `binary` when
`INCOGNITA_BINSPEC` is on; it reads the objects the cascade already holds and changes none of them, so every
cross section is bit-identical with it on or off. The spectra are appended to `LAST` (one dict per incident
energy) for the caller to save.

Spectrum convention (TALYS's): `egrid(nen)` is the channel (relative) kinetic energy Eo = Etotal - S - Ex of the
ejectile + residual pair; `xsbinemis` is mb/MeV on `egrid[ebegin..eend]`; the discrete residual levels add
lines `xsdisc(type, nex)` at `eoutdis(type, nex) = Etotal - S(0,0,type) - edis` (energies.f90:167).
`pe_ps`/`pe_ki` are the Kalbach pickup/stripping and knockout parts of `xspreeq` (preeqcomplex.f90),
`pe_ex` = xspreeq - pe_ps - pe_ki (exciton + breakup).

`full_xsbinary` is binary.f90's `xsbinary(type)` after the direct (binary.f90:215) and pre-equilibrium /
giant-resonance (binary.f90:259) addends -- what multiple.f90:950 adds to `xsfeed(0,0,type)`. The cascade
used to pass the compound-only value, so `xsparticle_mb` (totalxs.f90) lacked the binary direct + PE step
(Fe-56 14.1 MeV: d 1.52 vs (n,d) 3.45 mb). `xsfeed` feeds only `xsparticle`/`multiplicity`; no channel,
residual or fission cross section reads it.

Test: tests/hf/test_binspec.py

Task: T10 (physics/hf/CONTRACT.md §7; Incognita extension, output only). Acceptance test: NONE-PUBLIC.
"""

from __future__ import annotations

import os

import numpy as np

LAST: list[dict] = []


def enabled() -> bool:
    """`INCOGNITA_BINSPEC` (or SPECOUT's `INCOGNITA_SPECOUT`) = 1/y/yes/on records the binary spectra (output only;
    default off = no work).

    TALYS: (none -- Incognita extension, not a TALYS routine)
    Test: none in the public suite
    """
    return any(os.environ.get(k, "").strip().lower() in ("1", "y", "yes", "on")
               for k in ("INCOGNITA_BINSPEC", "INCOGNITA_SPECOUT"))


def _np(x) -> np.ndarray:
    if hasattr(x, "detach"):
        x = x.detach().cpu().numpy()
    return np.asarray(x, dtype=float)


def full_xsbinary(b2) -> list[float] | None:
    """binary.f90's `xsbinary(-1..6)` after the direct-discrete and pre-equilibrium/GR addends, from the
    `BinaryInputs` the cascade built (compound-only `xsbinary_mb`, `xsdirdisctot_mb`, `xspreeqtot_mb`,
    `xsgrtot_mb`). Same arithmetic as `emission.binary.binary`'s `xsbin` (racap is added downstream by
    `direct.racapcalc.add_to_results`, as in `binary`).

    TALYS: (none -- Incognita extension, not a TALYS routine)
    Test: none in the public suite
    """
    if b2.xsbinary_mb is None:
        return None
    out = [float(v) for v in _np(b2.xsbinary_mb)]
    for t in sorted(b2.grids):
        out[t + 1] = out[t + 1] + float(b2.xsdirdisctot_mb.get(t, 0.0))
        if b2.flagpreeq:
            out[t + 1] = out[t + 1] + float(b2.xspreeqtot_mb.get(t, 0.0)) + float(b2.xsgrtot_mb.get(t, 0.0))
    return out


def _edges(egrid: np.ndarray, maxen: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """grid.f90:164-176: Ebottom, Etop, deltaE on the emission grid."""
    eg = egrid
    n = len(eg)
    eb, et, de = np.zeros(n), np.zeros(n), np.zeros(n)
    for nen in range(2, maxen):
        de[nen] = 0.5 * (eg[nen + 1] - eg[nen - 1])
        et[nen] = 0.5 * (eg[nen] + eg[nen + 1])
        eb[nen] = 0.5 * (eg[nen] + eg[nen - 1])
    de[1] = eg[1] + 0.5 * (eg[2] - eg[1])
    et[1] = de[1]
    eb[1] = 0.0
    de[maxen] = 0.5 * (eg[maxen] - eg[maxen - 1])
    et[maxen] = eg[maxen]
    eb[maxen] = 0.5 * (eg[maxen] + eg[maxen - 1])
    return eb, et, de


def _pol1(x1, x2, y1, y2, x):
    if x1 == x2:
        return y1
    return y1 + (x - x1) * (y2 - y1) / (x2 - x1)


def _locate(xs: np.ndarray, ib: int, ie: int, x: float) -> int:
    """TALYS locate: the index j in [ib, ie-1] with xs[j] <= x < xs[j+1] (xs ascending or descending)."""
    if xs[ie] >= xs[ib]:
        j = int(np.searchsorted(xs[ib:ie + 1], x, side="right")) - 1 + ib
    else:
        j = int(np.searchsorted(-xs[ib:ie + 1], -x, side="right")) - 1 + ib
    return min(max(j, ib), ie - 1)


def binemission(pinp, t: int, contrib: np.ndarray, xscompcont: float, speceps: float = 1.0e-30, egn: int = 0):
    """binemission.f90 for one ejectile: (xsemis on egrid, binnorm). `contrib[nex]` is the compound
    population of the binary residual's continuum bin nex (comptarget.f90's `contrib`).

    TALYS: (none -- Incognita extension, not a TALYS routine)
    Test: none in the public suite
    """
    eg = np.asarray(pinp.egrid_mev, float)[:egn] if egn else np.asarray(pinp.egrid_mev, float)
    E = len(eg)
    xsemis = np.zeros(E)
    r = pinp.residuals[t]
    ib, ie = int(pinp.ebegin[t]), int(pinp.eend[t])
    if ib >= ie:
        return xsemis, 0.0
    nl, mx = int(r.nlast), int(r.maxex)
    if mx <= nl:
        return xsemis, 0.0
    exinc = float(pinp.etotal_mev)
    ss = float(r.sep_mev)
    eo = np.zeros(mx + 2)
    xsm = np.zeros(mx + 2)
    for nex in range(nl + 1, mx + 1):
        dex = float(r.dex_mev[nex])
        eo[nex] = exinc - ss - float(r.ex_mev[nex])
        xsm[nex] = float(contrib[nex]) / dex if dex > 0 else 0.0
    eo[nl] = exinc - ss - float(r.ex_mev[nl])
    xsm[nl] = xsm[nl + 1]
    xsm[mx + 1] = 0.0
    for nen in range(ib, ie + 1):
        eout = eg[nen]
        if eout >= eo[nl]:
            continue
        if eout <= eo[mx]:
            xsemis[nen] = xsm[mx] * eout / eo[mx] if eo[mx] != 0 else 0.0
            continue
        nexout = _locate(eo, nl, mx, eout)
        xs = _pol1(eo[nexout], eo[nexout + 1], xsm[nexout], xsm[nexout + 1], eout)
        xsemis[nen] = 0.0 if xs < speceps else xs
    return xsemis, nl


def record(e_inc_mev: float, pinp, b2, b, k0: int, ctx=None) -> dict | None:
    """Binary emission spectra of every ejectile at one incident energy (see module doc); appended to LAST.

    TALYS: (none -- Incognita extension, not a TALYS routine)
    Test: none in the public suite
    """
    if pinp is None:
        return None
    eg = np.asarray(pinp.egrid_mev, float)
    lens = [len(v) for v in pinp.xspreeq_mb.values()]
    if lens:  # the run grid's maxen+1 points (egrid_mev may carry the array's unused tail)
        eg = eg[: min(len(eg), min(lens))]
    maxen = len(eg) - 1
    eb, et, de = _edges(eg, maxen)
    exinc = float(pinp.etotal_mev)
    comp = getattr(b2, "xscompcont_mb", {}) or {}
    xseps = float(getattr(b2, "xseps_mb", 0.0) or 0.0)
    pres = _components(ctx, e_inc_mev)
    xsb = full_xsbinary(b2)
    out = dict(e_inc_mev=float(e_inc_mev), etotal_mev=exinc, egrid=eg.tolist(), ebottom=eb.tolist(),
               etop=et.tolist(), deltae=de.tolist(), xsbinary_full=xsb,
               xsbinary_comp=[float(v) for v in _np(b2.xsbinary_mb)] if b2.xsbinary_mb is not None else None,
               xsreacinc_mb=float(b2.xsreacinc_mb), xscompel_mb=float(_np(b.xscompel_mb)),
               xsnonel_mb=float(_np(b.xsnonel_mb)), types={})
    from physics.hf.preeq.exciton import c6fix_on
    c6 = c6fix_on()  # C6FIX: same boundary book as preeqcorrect, frac < 0 -> 0
    for t in sorted(pinp.residuals):
        if t not in b2.grids:
            continue
        r = pinp.residuals[t]
        ib, ie = int(pinp.ebegin[t]), int(pinp.eend[t])
        nl, mx = int(r.nlast), int(r.maxex)
        cpex = _np(b2.xspopex_mb[t])
        contrib = np.zeros(mx + 2)
        k = min(len(cpex), mx + 1)
        contrib[:k] = cpex[:k]
        cc = float(comp.get(t, 0.0))
        if cc < xseps:  # binary.f90:311
            cc = 0.0
        xsemis, _ = binemission(pinp, t, contrib, cc, egn=len(eg))
        # binemission.f90:157-170: emissum over ebegin..nendisc, the top bin cut at the last discrete line
        edis = np.asarray(r.ex_mev[: nl + 1], float)
        eoutdis = exinc - float(r.sep_mev) - edis
        nendisc = ie
        if nl >= 0 and eoutdis[nl] > 0:
            nendisc = max(ib, min(ie, int(np.searchsorted(eb[: ie + 1], eoutdis[nl], side="right")) - 1))
        emissum = float(np.sum(xsemis[ib:nendisc + 1] * de[ib:nendisc + 1])) if ie > ib else 0.0
        if ie > ib and nl >= 0 and eoutdis[nl] > 0:
            emissum -= xsemis[nendisc] * (max(et[nendisc] - eoutdis[nl], 0.0) if c6 else (et[nendisc] - eoutdis[nl]))
        binnorm = cc / emissum if emissum != 0.0 else 0.0
        xsemis = binnorm * xsemis
        xspre = np.asarray(pinp.xspreeq_mb.get(t, np.zeros(len(eg))), float)[: len(eg)]
        xsgr = (np.asarray(pinp.xsgr_mb.get(t, np.zeros(len(eg))), float)[: len(eg)]
                if pinp.flaggiant else np.zeros(len(eg)))
        if len(xsgr) < len(eg):
            xsgr = np.pad(xsgr, (0, len(eg) - len(xsgr)))
        sl = slice(ib, ie + 1) if ie >= ib else slice(0, 0)
        mask = np.zeros(len(eg), bool)
        mask[sl] = True
        xsbinemis = np.where(mask, xsemis + xspre + xsgr, 0.0)
        disc = _np(b.xsdisc_mb[t]) if t in b.xsdisc_mb else np.zeros(0)
        nd = min(len(disc), nl + 1)
        lines_e = eoutdis[:nd].tolist()
        lines_xs = disc[:nd].tolist()
        if t == k0 and nd > 0:
            lt = int(getattr(b2, "ltarget", 0))
            if lt < nd:
                lines_xs[lt] = 0.0  # compound + direct elastic is not an emission line (binary.f90:368)
        dd = _np(b2.xsdirdisc_mb[t])[:nd] if t in b2.xsdirdisc_mb else np.zeros(nd)
        ent = dict(ebegin=ib, eend=ie, nendisc=int(nendisc), nlast=nl, maxex=mx, sep_mev=float(r.sep_mev),
                   xsemis=np.where(mask, xsemis, 0.0).tolist(), xspreeq=np.where(mask, xspre, 0.0).tolist(),
                   xsgr=np.where(mask, xsgr, 0.0).tolist(), xsbinemis=xsbinemis.tolist(), binnorm=float(binnorm),
                   xscompcont=cc, xspreeqtot=float(pinp.xspreeqtot_mb.get(t, 0.0)),
                   lines_e=lines_e, lines_xs=lines_xs, lines_dir=dd.tolist(),
                   continuum_sum=float(np.sum(xsbinemis[ib:nendisc + 1] * de[ib:nendisc + 1])
                                       - (xsbinemis[nendisc] * (max(et[nendisc] - eoutdis[nl], 0.0) if c6 else (et[nendisc] - eoutdis[nl]))
                                          if (ie > ib and nl >= 0 and eoutdis[nl] > 0) else 0.0)))
        if pres is not None:
            for key, name in (("xspreeqps", "pe_ps"), ("xspreeqki", "pe_ki")):
                if key in pres:
                    v = np.asarray(pres[key][t], float)[: len(eg)]
                    if len(v) < len(eg):
                        v = np.pad(v, (0, len(eg) - len(v)))
                    ent[name] = np.where(mask, v, 0.0).tolist()
        out["types"][t] = ent
    LAST.append(out)
    return out


def _components(ctx, e_inc_mev: float):
    """The preequilibrium components (pickup/stripping, knockout) at this energy, from the same cached T8 run
    `pop_inputs_of` read (feed_reference._preeq_of, ctx = (target, declared, preeq_fit)); None when not available."""
    if ctx is None:
        return None
    try:
        from physics.hf.emission.feed_reference import _preeq_of

        target, declared, pfit = ctx
        pe, pres, _ = _preeq_of(target, declared, pfit) if pfit else _preeq_of(target, declared)
        i = pe.get(round(float(e_inc_mev), 6))
        if i is None:
            return None
        res = {}
        for key in ("xspreeqps", "xspreeqki"):
            if key in pres:
                res[key] = np.asarray(pres[key][i].detach().cpu().numpy() if hasattr(pres[key][i], "detach")
                                      else pres[key][i], float)
        return res
    except Exception:  # noqa: BLE001 -- components are diagnostic output only
        return None


def binspec_ctx(cas, target: str, declared):
    """(target, declared, preeq_fit) -- the key `feed_reference.pop_inputs_of` used for `_preeq_of`; None when off.

    TALYS: (none -- Incognita extension, not a TALYS routine)
    Test: none in the public suite
    """
    if not enabled():
        return None
    try:
        from physics.hf.compound.pop_reference import preeq_fit

        pfit = preeq_fit(cas.fit, cas.Zt, cas.At) if declared is not None else ()
    except Exception:  # noqa: BLE001
        pfit = ()
    return (target, declared, pfit)
