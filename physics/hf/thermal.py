"""TALYS's incident energies below `eninclow` (thermal.f90) and its thermal cross sections (thermalxs.f90),
OUTPUT ONLY.

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

TALYS runs its nuclear models only at incident energies >= `eninclow` (`elow`, default 1e-6 MeV; with `endf y` D0).
When the grid starts below E1v = 0.2 eninclow, grid.f90 inserts E1v and eninclow into it; at the first computed
energy eninc(Ninclow+1) thermal.f90 fills every lower energy from that energy's cross sections:

    E <= E1v:              xs(E) = xs(eref) R sqrt(Etherm / E)                 (1/v through the thermal value)
    E1v < E < eninclow:    log-log between (E1v, xs(eref) Rres) and (eref, xs(eref))

with Etherm = 2.53e-8 MeV, R = xstherm / xs1, Rres = (sqrt(Etherm) xstherm / sqrt(E1v)) / xs1, xs1 = the compound
nucleus production (capture), (n,p) residual or (n,a) residual at eref; capture's R for every other channel, the (n,p)
and (n,a) ones for those channels when `xsptherm` / `xsalphatherm` are non-zero. The elastic, compound elastic and
direct capture stay at their eref value; the non-elastic is the sum of the filled channels; inelastic (the target
again) and the projectile's own binary/level columns are 0; fission is not filled (0). Below E1v an isomeric
branching ratio of a capture / (n,p) / (n,a) channel is the thermal table's (xscaptherm(i) / xscaptherm(-1)).

The ENGINE keeps its own numbers at those energies (it runs Hauser-Feshbach there; `lowepot` and the resonance-region fill in the published
library): `Results.thermal` carries TALYS's rows beside them and changes nothing else. `add_to_results` takes eref's
values from the run when eref is one of its energies, else from a one-energy run at eref (TALYS's own first energy).

TALYS routines ported here (file:line of the subroutine statement):
    thermalxs.f90:1 (thermalxs)     xscaptherm / xsptherm / xsalphatherm: structure/thermal table, deck, Kopecky
    thermal.f90:1 (thermal)         the fill below eninclow
    grid.f90:1 (grid)               E1v / eninclow insertion and Ninclow (core.grids.low_incident_energies)
Task: T10 (physics/hf/CONTRACT.md section 7; output only). Acceptance test: KW-B10
(tests/hf/test_kwcov_b10b.py, docs/hf/COVERAGE_PLAN.md).

TALYS quirks kept: (1) thermalxs.f90 reads the table AFTER the input, so a table row (isoR = -1 or an isomer) overwrites
a deck `xscaptherm` / `xsptherm` / `xsalphatherm` for that target; the deck value acts only where the table has none.
(2) The table is matched on A only (isoT not checked): the last row of that A wins. (3) Thresholds of channels that
open between the thermal energies and eref are not applied here (TALYS checks Ethrexcl / Ethresh; a channel open at
eref has a threshold below it, so only a threshold between the low energy and eref would differ).
"""

from __future__ import annotations

import math
import re
from dataclasses import replace

import numpy as np

__all__ = ["ETHERM_MEV", "thermal_table", "thermal_xs", "low_grid", "fill", "add_to_results"]

ETHERM_MEV = 2.53e-8  # thermal.f90:118
NUMISOM = 10  # A0_talys_mod.f90:44 numisom (isomer index 0..numisom)
_PARSYM = "gnpdtha"


def thermal_table(Z: int, A: int) -> dict | None:
    """structure/thermal/<El>.ther rows of mass A as {"cap"|"p"|"alpha": {isoR: mb}}; None without a file.
    Fixed format '(4x, 3i4, 3(es15.6, 15x))' (thermalxs.f90:62); every row with ia == A is applied in file order.

    TALYS: thermalxs.f90:1 (thermalxs)
    Test: tests/hf/test_kwcov_b10b.py
    """
    from physics.hf.core.constants import nuclide_symbol
    from physics.hf.structure.files import talys_structure_dir

    f = talys_structure_dir() / "thermal" / f"{nuclide_symbol(Z).capitalize()}.ther"
    if not f.is_file():
        return None
    out: dict = {"cap": {}, "p": {}, "alpha": {}}
    for line in f.read_text(errors="replace").splitlines()[1:]:
        try:
            ia, iso_r = int(line[4:8]), int(line[12:16])
        except ValueError:
            continue
        if ia != A:
            continue
        for key, a, b in (("cap", 16, 31), ("p", 46, 61), ("alpha", 76, 91)):
            s = line[a:b].strip()
            v = float(s) if s else 0.0
            if v != 0.0:
                out[key][iso_r] = v
    return out


def thermal_xs(Z: int, A: int, deck: dict | None = None, kopecky=None) -> dict:
    """xscaptherm / xsptherm / xsalphatherm over isomer index -1..numisom (mb), as thermalxs.f90 leaves them:
    the deck's (-1) values, overwritten by the table's rows of mass A; with a table, a (-1) still 0 becomes the sum over
    isomers; a capture (-1) still 0 becomes Kopecky's `kopecky()` (1.5e-3 (a (S - pair))^3.5, a callable so it is only
    evaluated when needed). `deck` = {"cap"|"p"|"alpha": value of the keyword} (0 = not given).

    TALYS: thermalxs.f90:1 (thermalxs)
    Test: tests/hf/test_kwcov_b10b.py
    """
    iso = range(-1, NUMISOM + 1)
    xs = {k: {i: 0.0 for i in iso} for k in ("cap", "p", "alpha")}
    for k, v in (deck or {}).items():
        xs[k][-1] = float(v)
    tab = thermal_table(Z, A)
    if tab is not None:
        for k in xs:
            for i, v in tab[k].items():
                if i in xs[k]:
                    xs[k][i] = v
        for k in xs:
            if xs[k][-1] == 0.0:
                xs[k][-1] = sum(xs[k][i] for i in range(0, NUMISOM + 1))
    if xs["cap"][-1] == 0.0 and kopecky is not None:
        xs["cap"][-1] = float(kopecky())
    return xs


def low_grid(declared_mev, eninclow_mev: float) -> dict:
    """grid.f90's incident grid with E1v / eninclow inserted: eninc, Ninclow, E1v, eninclow, eref = eninc(Ninclow+1)
    (None when every energy is below eninclow).

    TALYS: grid.f90:1 (grid) lines 221-252
    Test: tests/hf/test_kwcov_b10b.py
    """
    from physics.hf.core.grids import low_incident_energies

    g = low_incident_energies(sorted(float(e) for e in declared_mev), float(eninclow_mev), 0.0, 0.0)
    n = int(g["Ninclow"])
    g["eref"] = g["eninc"][n] if n < len(g["eninc"]) else None
    return g


def _ratios(ref: dict, therm: dict, e1v: float, Z: int, A: int) -> dict:
    """thermal.f90:118-160: (R, Rres) for capture-like, (n,p) and (n,a) quantities."""
    def rp(z, a):
        return float(ref.get(f"residual_production_mb/rp{z:03d}{a:03d}", 0.0))

    ctherm = math.sqrt(ETHERM_MEV) * therm["cap"][-1]
    xscapres = ctherm / math.sqrt(e1v)
    xscap1 = rp(Z, A + 1)
    if xscap1 > 0.0:
        cap = (therm["cap"][-1] / xscap1, xscapres / xscap1)
    else:
        cap = (1.0, 1.0)
    out = {"cap": cap, "p": cap, "alpha": cap}
    for key, (z, a) in (("p", (Z - 1, A)), ("alpha", (Z - 2, A - 3))):
        if therm[key][-1] != 0.0:
            res_ = math.sqrt(ETHERM_MEV) * therm[key][-1] / math.sqrt(e1v)
            x1 = rp(z, a)
            if x1 > 0.0:
                out[key] = (therm[key][-1] / x1, res_ / x1)
            else:
                out[key] = (1.0, cap[1])  # thermal.f90: ratiop = 1, ratioresp keeps capture's
    return out


def _value(xsa: float, e: float, rr: tuple, g: dict) -> float:
    """One filled number (thermal.f90's two branches; pol1 in ln E, ln xs)."""
    R, Rres = rr
    e1v, eref = g["E1v"], g["eref"]
    if e > e1v:
        xsres = xsa * Rres
        if xsres <= 0.0 or xsa <= 0.0:
            return 0.0
        x1, x2, y1, y2 = math.log(e1v), math.log(eref), math.log(xsres), math.log(xsa)
        return math.exp(y1 + (math.log(e) - x1) * (y2 - y1) / (x2 - x1))
    return xsa * R * math.sqrt(ETHERM_MEV) / math.sqrt(e)


_CHAN = re.compile(r"^channels_mb/xs(\d{6})$")
_CHANX = re.compile(r"^extras/xs(\d{6})\.(tot:gamma|L(\d\d)|L(\d\d):branch)$")
_RP = re.compile(r"^(?:residual_production_mb|extras)/rp(\d{3})(\d{3})(\.L(\d\d))?$")
_LEV = re.compile(r"^levels_mb/([gnpdtha])([gnpdtha])\.L(\d\d)$")
_BIN = re.compile(r"^extras/binary\.tot:([gnpdtha])$")
_EXC = re.compile(r"^extras/([gnpdtha])([gnpdtha])\.tot:(discrete|continuum)$")


def _kind_of_code(code: str) -> str:
    return "p" if code == "010000" else ("alpha" if code == "000001" else "cap")


def _kind_of_type(t: str) -> str:
    return "p" if t == "p" else ("alpha" if t == "a" else "cap")


def fill(ref: dict, g: dict, therm: dict, Z: int, A: int, k0: int = 1, xseps_mb: float = 1.0e-7) -> dict:
    """thermal.f90 for every energy of `g["eninc"]` below eninclow. `ref` = {result_arrays key: value at eref};
    returns {"E": [...], key: [...]} with the keys thermal.f90 fills (channels, isomeric channels and branches,
    gamma columns, residual production and isomers, discrete levels of other ejectiles, binary, exclusive
    discrete/continuum, totals). Pure function: no engine call.

    TALYS: thermal.f90:1 (thermal)
    Test: tests/hf/test_kwcov_b10b.py
    """
    n = int(g["Ninclow"])
    es = [float(e) for e in g["eninc"][:n]]
    rat = _ratios(ref, therm, float(g["E1v"]), Z, A)
    proj = _PARSYM[k0]
    out: dict = {"E": es}

    def put(key, kind, xsa, strict=False):
        if (xsa <= xseps_mb) if strict else (xsa < xseps_mb):
            out[key] = [0.0] * n
            return
        out[key] = [_value(xsa, e, rat[kind], g) for e in es]

    # channels (flagchannels): inelastic skipped (idchannel 100000), xsa <= xseps
    chan_keys = sorted(k for k in ref if _CHAN.match(k))
    for k in chan_keys:
        code = _CHAN.match(k).group(1)
        if code == "100000":
            out[k] = [0.0] * n
            continue
        put(k, _kind_of_code(code), float(ref[k]), strict=True)
    # isomeric channels, branches and gamma columns
    by_code: dict = {}
    for k in ref:
        m = _CHANX.match(k)
        if m and m.group(3) is not None:
            by_code.setdefault(m.group(1), []).append(int(m.group(3)))
    therm_of = {"000000": therm["cap"], "010000": therm["p"], "000001": therm["alpha"]}
    for k in sorted(ref):
        m = _CHANX.match(k)
        if not m:
            continue
        code, what = m.group(1), m.group(2)
        if code == "100000":
            out[k] = [0.0] * n
            continue
        kind = _kind_of_code(code)
        chan = float(ref.get(f"channels_mb/xs{code}", 0.0))
        if what == "tot:gamma":
            put(k, kind, float(ref[k]))
            continue
        lev = int(m.group(3) if m.group(3) is not None else m.group(4))
        nis = sorted(by_code.get(code, [])).index(lev) if lev in by_code.get(code, []) else -1
        # exclbranch at eref: the isomer file over its channel (= the `:branch` column, which a caller may not have)
        lv = ref.get(f"extras/xs{code}.L{lev:02d}")
        br0 = (float(lv) / chan if (lv is not None and chan > 0.0)
               else float(ref.get(f"extras/xs{code}.L{lev:02d}:branch", 0.0)))
        tt = therm_of.get(code)
        brres = 0.0
        if tt is not None and 0 <= nis <= NUMISOM and tt[-1] > 0.0:
            brres = tt[nis] / tt[-1]
        if chan <= xseps_mb:
            out[k] = [0.0] * n
            continue
        brs = [brres if (e <= g["E1v"] and brres > 0.0) else br0 for e in es]
        if what.endswith(":branch"):
            out[k] = brs
        else:
            out[k] = [_value(chan, e, rat[kind], g) * b for e, b in zip(es, brs)]
    # residual production and isomers (the target itself, Zcomp = 0 / Ncomp = 1, is skipped)
    Zc, Ac = Z, A + 1
    for k in sorted(ref):
        m = _RP.match(k)
        if not m:
            continue
        z, a = int(m.group(1)), int(m.group(2))
        zc, nc = Zc - z, (Ac - Zc) - (a - z)
        if (zc, nc) == (0, 1):
            out[k] = [0.0] * n
            continue
        kind = "p" if (zc, nc) == (1, 0) else ("alpha" if (zc, nc) == (2, 2) else "cap")
        put(k, kind, float(ref[k]))
    # discrete levels, binary, exclusive discrete / continuum (type k0 skipped)
    for k in sorted(ref):
        m = _LEV.match(k) or _BIN.match(k) or _EXC.match(k)
        if not m:
            continue
        t = m.group(2) if (_LEV.match(k) or _EXC.match(k)) else m.group(1)
        if t == proj:
            out[k] = [0.0] * n
            continue
        put(k, _kind_of_type(t), float(ref[k]))
    for t in _PARSYM:
        k = f"totals_mb/{proj}{t}"  # xsexclusive per ejectile
        if k in ref:
            if t == proj:
                out[k] = [0.0] * n
            else:
                put(k, _kind_of_type(t), float(ref[k]))
    # totals (thermal.f90:411-420): non-elastic = the filled channels (flagchannels) else the residual production
    if chan_keys:
        nonel = [sum(out[k][i] for k in chan_keys) for i in range(n)]
    else:
        rps = [k for k in out if k.startswith("residual_production_mb/rp") and "." not in k]
        nonel = [sum(out[k][i] for k in rps) for i in range(n)]
    el = float(ref.get("totals_mb/elastic", 0.0))
    ce = float(ref.get("totals_mb/compound_elastic", 0.0))
    out["totals_mb/nonelastic"] = nonel
    out["totals_mb/elastic"] = [el] * n
    out["totals_mb/total"] = [el + x for x in nonel]
    out["totals_mb/compound_elastic"] = [ce] * n
    out["totals_mb/reaction"] = [x + ce for x in nonel]
    if "totals_mb/fission" in ref:
        out["totals_mb/fission"] = [0.0] * n
    return out


def therm_of_run(cas) -> dict:
    """thermal_xs for a run's Cascade: deck values from its Params, Kopecky from its level densities.

    TALYS: thermalxs.f90:1 (thermalxs)
    Test: tests/hf/test_kwcov_b10b.py
    """
    deck = {}
    p = getattr(cas, "params", None)
    for key, name in (("cap", "xscaptherm"), ("p", "xsptherm"), ("alpha", "xsalphatherm")):
        try:
            if p is not None and name in p:
                deck[key] = float(p.at(name, -1))
        except (KeyError, TypeError, ValueError, IndexError):
            pass

    def kop():
        from physics.hf.urr import kopecky_mb

        return kopecky_mb(cas)

    return thermal_xs(int(cas.Zt), int(cas.At), deck, kop)


def add_to_results(res, injection):
    """Results.thermal: TALYS's rows below eninclow for an incident-neutron run whose energies go below it
    (empty and `res` unchanged otherwise). Nothing else in `res` moves.

    TALYS: thermal.f90:1 (thermal), talysreaction.f90:201 (the call at nin == Ninclow + 1)
    Test: tests/hf/test_kwcov_b10b.py
    """
    import torch

    from physics.hf import projectile

    if projectile.k0() != 1 or getattr(injection, "families", ()) or not hasattr(injection, "Z"):
        return res
    declared = getattr(injection, "declared_energies", None)
    if not declared:
        return res
    es = [float(e) for e in res.e_inc_mev.detach().cpu().numpy()]
    Z, A = int(injection.Z), int(injection.A)
    cas = getattr(injection, "cascade", None)
    if cas is not None:
        o = cas.options
    else:  # the run's own cached options (no new Cascade unless an energy is below eninclow)
        from physics.hf.compound.dens_reference import structure_of

        o = structure_of(Z, A)[0]
    elow = float(o.eninclow_mev)
    if not any(np.float32(e) < np.float32(elow) for e in es):
        return res
    if cas is None:
        from physics.hf import warmrun

        cas = warmrun.new_cascade(Z, A, tuple(float(x) for x in declared))
        o = cas.options
    if elow == 0.0:
        raise NotImplementedError("energies below eninclow with eninclow unresolved (endf y: grid.f90 takes D0): "
                                  "not ported; give `elow`")
    g = low_grid(declared, elow)
    if g["eref"] is None:
        raise NotImplementedError("every incident energy is below eninclow: TALYS computes none (thermal.f90 needs "
                                  "the first energy >= eninclow)")
    from physics.hf import warmrun

    eref = float(np.float32(g["eref"]))
    hit = [i for i, e in enumerate(es) if float(np.float32(e)) == eref]
    if hit:
        arr = warmrun.result_arrays(res)
        ref = {k: float(np.asarray(v).ravel()[hit[0]]) for k, v in arr.items() if np.asarray(v).shape == (len(es),)}
    else:  # eninclow was inserted by grid.f90: TALYS's first computed energy, run as the first energy of its own
        from physics.hf import engine_c
        from physics.hf.engine import ChainedFull

        above = tuple(e for e in g["eninc"] if np.float32(e) >= np.float32(elow))
        with torch.inference_mode():
            r = engine_c.run(ChainedFull(Z=Z, A=A, declared_energies=above, energies=(above[0],)), None)
        arr = warmrun.result_arrays(r)
        ref = {k: float(np.asarray(v).ravel()[0]) for k, v in arr.items()}
    th = therm_of_run(cas)
    t = fill(ref, g, th, Z, A, 1, float(np.float32(o.xseps_mb)))
    out = {k: np.asarray(v, dtype=np.float64) for k, v in t.items()}
    out["eninclow"] = np.asarray([g["eninclow"]])
    out["E1v"] = np.asarray([g["E1v"]])
    out["eref"] = np.asarray([g["eref"]])
    out["xscaptherm"] = np.asarray([th["cap"][i] for i in range(-1, NUMISOM + 1)])
    out["xsptherm"] = np.asarray([th["p"][i] for i in range(-1, NUMISOM + 1)])
    out["xsalphatherm"] = np.asarray([th["alpha"][i] for i in range(-1, NUMISOM + 1)])
    return replace(res, thermal=out)
