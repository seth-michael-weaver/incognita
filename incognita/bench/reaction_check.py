"""REACTION-code check of the benchmark's EXFOR rows: is a series a TOTAL cross section for its stated reaction?

This is the rule of the research repository's `scripts/channels/score_channels_fixed.py` (`reaction_flags`, the v5b data
fix registered 2026-09-23), which the light (Z 1-25) channel rows already pass (`scripts/build_light_channels.py`). The
benchmark rows of `ch-n2n`, `ch-np`, `ch-na` and `ch-sacs` were cut before it; on 2026-11-06 it was applied to them too
(`scripts/fix_bench_rows.py`). Every leaf of the full REACTION string is checked. A series is kept only if

  (a) no product state / level suffix on SF4 (-G, -M, -Mn, -L, -Ln) and no partial state sum (-M1+M2, -G+M2, ...);
  (b) SF5 empty, except '(M)' / 'M+' on a product WITHOUT a state suffix (isomer included = total);
  the rule's intent is "total cross section", so two state-labelled codes that ARE the total are kept when ``isomers``
  (from NUBASE2020: the residual's isomers with half-life >= 1 s and their IT branching) shows it:
      -G+M1 / -G+M      when the residual has at most one such isomer (ground + the only isomer = total);
      -G,M+             (ground state, isomer decay included) when every such isomer decays by IT >= 99 %;
      (-G)+(-M,FCT)     ground state plus the isomer term times its IT factor, under the same IT >= 99 % condition;
  without ``isomers`` both are flagged (the research rule);
  (c) SF7 and SF8 empty (REL, RAW, SFC, RAB, FCT, ...); with sacs=True (spectrum averages) SF8 must be FIS or SPA;
  (d) SF9 empty (DERIV, EVAL, RECOM, CALC are not measurements of this quantity as compiled);
  (e) no combination except a '+' sum over the states of ONE target / process / residual that includes the ground state
      (ratios, differences, products, '=', and sums with other targets or processes are dropped);
  (f) no V-entry (evaluated compilation).
"""
from __future__ import annotations

import re
from typing import Callable

STATE = re.compile(r"-(?:[GML]\d?)(?:\+[GML]\d?)*$")      # any state / level / partial state-sum suffix on SF4
GM_TOTAL = re.compile(r"-G\+M1?$")                         # ground + (first) isomer
_OPS = {"+": "SUM", "-": "DIFF", "*": "PROD", "=": "EQ", "/": "RATIO"}


def _leaves(p):
    return [q for c in p.components for q in _leaves(c)] if p.components else [p]


def _residual(sf4: str):
    """'77-IR-190-G+M1' -> (77, 190); None when SF4 is not a nuclide."""
    m = re.match(r"^(\d{1,3})-[A-Z]{1,2}-(\d{1,3})", sf4 or "")
    return (int(m.group(1)), int(m.group(2))) if m else None


def _fct_ok(leaf, isomers) -> bool:
    """An isomer leaf with SF8 = FCT inside a ground + isomer sum, e.g. ((46-PD-108(N,G)46-PD-109-G,,SIG)+
    (46-PD-108(N,G)46-PD-109-M,,SIG,,FCT)): the isomer term times a factor (its IT branching to the ground state). The sum
    is the total when every isomer of the residual (half-life >= 1 s) decays by IT >= 99 % (Pd-109m: IT 100 %)."""
    s4 = (leaf.sf.sf4 or "").strip()
    r = _residual(s4)
    if leaf.sf.sf8 != "FCT" or isomers is None or r is None or not re.search(r"-M\d?$", s4):
        return False
    iso = isomers(*r)
    return bool(iso) and all(x >= 99.0 for x in iso)


def reaction_flags(rx: str, entry: str = "", sacs: bool = False,
                   isomers: Callable[[int, int], list[float]] | None = None) -> list[str]:
    """Flags that make a REACTION code NOT a total cross section for its stated reaction (empty list = keep).

    isomers(Z, A) -> IT branching (%) of each isomer of the residual with half-life >= 1 s (NaN if unknown); see
    `nubase_isomers`. Without it, -G+M1 and -G,M+ are flagged (the research rule)."""
    from data.ingest.exfor_reactions import parse_reaction
    fl = []
    try:
        p = parse_reaction(str(rx))
    except Exception:
        return ["UNPARSEABLE"]
    lv = _leaves(p)
    if p.components:
        procs = {((l.sf.sf1 or ""), (l.sf.sf2 or ""), (l.sf.sf3 or "")) for l in lv}
        res = {STATE.sub("", (l.sf.sf4 or "").strip()) for l in lv}
        states = {(l.sf.sf4 or "").strip().rsplit("-", 1)[-1] for l in lv}
        isosum = (p.operator == "+" and len(procs) == 1 and len(res) == 1 and "G" in states
                  and all(not (l.sf.sf5 or l.sf.sf7 or (l.sf.sf8 and not _fct_ok(l, isomers)) or l.sf.sf9) for l in lv))
        if not isosum:
            fl.append("COMBO_" + _OPS.get(p.operator[0], p.operator))
    else:
        isosum = False
    for l in lv:
        s4 = (l.sf.sf4 or "").strip()
        m = STATE.search(s4)
        r = _residual(s4)
        iso = isomers(*r) if (isomers is not None and r is not None) else None
        total_gm = m is not None and iso is not None and GM_TOTAL.search(s4) is not None and len(iso) <= 1
        total_gmplus = (m is not None and iso is not None and s4.endswith("-G") and l.sf.sf5 == "M+"
                        and all(x >= 99.0 for x in iso))   # NaN >= 99 is False: unknown branching stays flagged
        if m and not isosum and not (total_gm or total_gmplus):
            fl.append("STATE" + m.group(0))
        if l.sf.sf5 and not (l.sf.sf5 in ("(M)", "M+") and not m) and not total_gmplus:
            fl.append("SF5:" + l.sf.sf5)
        if l.sf.sf7:
            fl.append("SF7:" + l.sf.sf7)
        if (l.sf.sf8 or "") not in (("FIS", "SPA") if sacs else ("",)) and not (isosum and _fct_ok(l, isomers)):
            fl.append("SF8:" + str(l.sf.sf8))
        if l.sf.sf9:
            fl.append("SF9:" + l.sf.sf9)
    if str(entry).upper().startswith("V"):
        fl.append("V_ENTRY")
    return sorted(set(fl))


MIN_ISOMER_HALF_LIFE_S = 1.0     # shorter isomers decay inside the measurement (prompt cascade): not a separate product


def nubase_isomers(nubase, min_half_life_s: float = MIN_ISOMER_HALF_LIFE_S) -> Callable[[int, int], list[float]]:
    """From a `data.ingest.nubase.load_nubase` frame: (Z, A) -> [IT branching % of each existing isomer (iso 1-4) with
    half-life >= min_half_life_s]; NaN where NUBASE gives no IT percentage (e.g. 'IT=?')."""
    import math
    x = nubase[nubase.iso.isin([1, 2, 3, 4]) & ~nubase.non_existent.astype(bool)
               & (nubase.half_life_s.astype(float) >= min_half_life_s)]
    out: dict[tuple[int, int], list[float]] = {}
    for r in x.itertuples():
        it = [d.get("branching_pct") for d in (r.decay_modes or []) if d.get("mode") == "IT"]
        v = float(it[0]) if it and it[0] is not None and d_ok(it[0]) else math.nan
        out.setdefault((int(r.Z), int(r.A)), []).append(v)
    return lambda z, a: out.get((int(z), int(a)), [])


def d_ok(v) -> bool:
    try:
        return v == v and float(v) >= 0
    except (TypeError, ValueError):
        return False
