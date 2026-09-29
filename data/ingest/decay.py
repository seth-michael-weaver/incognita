"""Ground-state decay labels for the decay-data model: half-lives, partial half-lives per
mode and beta-delayed neutron emission probabilities, from three editions.

* **NUBASE2016** and **NUBASE2020** through :func:`data.ingest.nubase.load_nubase`.
* **ENSDF 2026-09-01** adopted-levels ground states, parsed here, because the snapshot
  carries evaluations dated after NUBASE2020's literature cutoff.

A label is only a label when it was measured. NUBASE's ``#`` (systematics) values, half-life
limits, ``?`` branchings and ENSDF ``SY``/``CA``/``AP``/limit qualifiers are all excluded --
they are somebody else's model, and training on them would score us against it.

Partial half-life of mode m = T1/2 / BR_m. Only branchings quoted as a number (``=`` or ``~``
in NUBASE, ``=`` in ENSDF) of at least ``MIN_BRANCH_PCT`` are turned into partials; below
that a partial is dominated by the branching uncertainty, not by the decay physics.

The three splits (:func:`time_split`):

* ``C_disc2003`` -- NUBASE2020 labels; train on ground states discovered <= 2003, test on
  those discovered later. The powered split: a nuclide's half-life cannot predate its
  discovery.
* ``A_2016_2020`` -- train on NUBASE2016 labels, test on labels that NUBASE2020 has and
  NUBASE2016 did not (first measurements published 2016-2020). The powered split.
* ``B_2020_2026`` -- train on NUBASE2020, test on labels an ENSDF evaluation dated 2021 or
  later has and NUBASE2020 did not. Honest but thin: ENSDF lags new measurements.
"""

from __future__ import annotations

import math
import re
from pathlib import Path

import numpy as np
import pandas as pd

from data.ingest import ensdf as E
from data.ingest.nubase import NUBASE2016_FILE, NUBASE_FILE, load_nubase

__all__ = [
    "C_CUTOFF",
    "EDITION_CUTOFF",
    "INNER",
    "discovery_split",
    "MIN_BRANCH_PCT",
    "SPLITS",
    "TARGETS",
    "ensdf_ground_states",
    "labels_from_ensdf",
    "labels_from_nubase",
    "parse_ensdf_branchings",
    "time_split",
]

REPO = Path(__file__).resolve().parents[2]
MIN_BRANCH_PCT = 1.0
TARGETS = ("log_t", "log_t_bm", "log_t_bp", "log_t_a", "pn")
"""log10 total T1/2 [s]; log10 partial beta-minus, beta-plus/EC, alpha T1/2 [s]; P1n [%]."""

_BETA_PLUS = ("B+", "EC", "e+", "EC+B+", "B+EC")


def _branch(modes: list[dict], names: tuple[str, ...]) -> float:
    """Summed measured branching [%] over ``names``; NaN if any listed one is not measured."""
    tot, seen = 0.0, False
    for m in modes:
        if m["mode"] not in names:
            continue
        seen = True
        if m.get("extrapolated") or m["qualifier"] not in ("=", "~"):
            return math.nan
        br = m.get("branching_pct", m.get("branching"))
        if br is None or not np.isfinite(br):
            return math.nan
        sig = m.get("sigma_pct", m.get("sigma"))
        if sig is not None and np.isfinite(sig) and sig >= br:
            # consistent with zero at 1 sigma (48Ca: ENSDF %B-=22 +30-22 beside %2B-=78)
            return math.nan
        tot += float(br)
    return tot if seen else math.nan


def _partials(log_t: float, modes: list[dict], out: dict) -> None:
    for key, names in (("log_t_bm", ("B-",)), ("log_t_bp", _BETA_PLUS), ("log_t_a", ("A",))):
        br = _branch(modes, names)
        out[key] = (log_t - math.log10(br / 100.0)
                    if np.isfinite(log_t) and np.isfinite(br) and br >= MIN_BRANCH_PCT
                    else math.nan)
    pn = _branch(modes, ("B-n",))
    bm = _branch(modes, ("B-",))
    # P1n is quoted per decay; only meaningful when beta-minus is essentially the only mode
    out["pn"] = pn if np.isfinite(pn) and np.isfinite(bm) and bm >= 50.0 else math.nan


def labels_from_nubase(edition: int = 2020) -> pd.DataFrame:
    """One row per ground state with measured labels (NaN where not measured)."""
    nb = load_nubase(NUBASE2016_FILE if edition == 2016 else NUBASE_FILE, edition=edition)
    gs = nb[(nb["iso"] == 0) & ~nb["non_existent"]].copy()
    rows = []
    for r in gs.itertuples(index=False):
        measured_t = (np.isfinite(r.log10_half_life_s) and not r.half_life_extrapolated
                      and not r.is_stable and not isinstance(r.half_life_limit_kind, str)
                      and not str(r.half_life_raw).lstrip().startswith("~"))
        log_t = float(r.log10_half_life_s) if measured_t else math.nan
        out = {"Z": int(r.Z), "N": int(r.N), "A": int(r.A), "log_t": log_t,
               "log_t_sigma": float(r.log10_half_life_unc) if measured_t else math.nan,
               "is_stable": bool(r.is_stable),
               "mass_excess_kev": float(r.mass_excess_kev),
               "mass_extrapolated": bool(r.mass_excess_extrapolated),
               "discovery_year": r.discovery_year, "decay_raw": r.decay_raw}
        _partials(log_t, list(r.decay_modes), out)
        rows.append(out)
    df = pd.DataFrame(rows)
    df.attrs["source"] = f"NUBASE{edition}"
    return df


# ------------------------------------------------------------------------------- ENSDF

_BR_TOKEN = re.compile(
    r"%(?P<mode>[A-Z0-9+\-]+(?:\+%[A-Z0-9+\-]+)?)\s*"
    r"(?P<op>=|<=|>=|<|>|\s+AP\s+|\s+LT\s+|\s+GT\s+|\s+LE\s+|\s+GE\s+)\s*"
    r"(?P<val>[0-9.]+(?:E[+-]?[0-9]+)?|\?)?"
    r"(?:\s+(?P<unc>\+\d+-\d+|\d+)(?=\s|\$|$))?"
)
_ENSDF_MODE = {"B-": "B-", "B-N": "B-n", "B-2N": "B-2n", "A": "A", "EC+%B+": "B+",
               "B+": "B+", "EC": "EC", "SF": "SF", "P": "p", "IT": "IT", "N": "n"}


def parse_ensdf_branchings(text: str) -> list[dict]:
    """``'%B-=100$ %B-N=2.2 17'`` -> NUBASE-shaped mode dicts (branching in %)."""
    out = []
    for m in _BR_TOKEN.finditer(text.upper()):
        mode = _ENSDF_MODE.get(m["mode"])
        if mode is None:
            continue
        op = m["op"].strip()
        val = m["val"]
        q = {"=": "=", "AP": "~"}.get(op, "<" if op in ("<", "<=", "LT", "LE") else ">")
        if val in (None, "?"):
            q = "?"
        sig = math.nan
        if val not in (None, "?") and m["unc"]:
            digits = [int(x) for x in re.findall(r"\d+", m["unc"])]
            sig = E._digits_sigma(val, str(max(digits))) or math.nan
        out.append({"mode": mode, "qualifier": q,
                    "branching_pct": float(val) if val not in (None, "?") else math.nan,
                    "sigma_pct": sig, "extrapolated": False})
    return out


def ensdf_ground_states(zip_path: Path = E.ENSDF_ZIP) -> pd.DataFrame:
    """Ground-state record of every adopted-levels dataset: half-life, qualifiers, the
    evaluation date (YYYYMM) and the level's continuation text (branchings live there)."""
    rows = []
    for nucid, dsid, lines in E.iter_adopted_datasets(zip_path):
        key = E._nucid(nucid)
        if key is None or "NOT OBSERVED" in dsid or "INFERRED" in dsid:
            continue
        Z, A = key
        first, cont = None, []
        for line in lines[1:]:
            c6, c7, c8 = line[5:6], line[6:7], line[7:8]
            if c7 != " " or c8 != "L":
                continue
            if c6 == " " and not any(ch in line[9:21] for ch in "$="):
                if first is not None:
                    break
                first = line
            elif first is not None:
                cont.append(line[9:].strip())
        if first is None:
            continue
        e_field = first[9:19].strip()
        try:
            is_gs = float(e_field) == 0.0
        except ValueError:
            is_gs = False  # '0+X', 'X', 'SP': an offset band, not the ground state
        if not is_gs:
            continue
        hl = E.parse_half_life(first[39:49], first[49:55])
        rows.append({"Z": Z, "N": A - Z, "A": A, "dsid": dsid, "date": lines[0][74:80].strip(),
                     "half_life_s": hl["half_life_s"], "half_life_sigma_s": hl["half_life_sigma_s"],
                     "half_life_qualifier": hl["half_life_qualifier"],
                     "width_ev": hl["width_ev"], "is_stable": hl["is_stable"],
                     "half_life_raw": first[39:55].strip(), "continuation": "$".join(cont)})
    df = pd.DataFrame(rows)
    # a nuclide can have several adopted datasets (e.g. ':TENTATIVE'); keep the newest
    df = df.sort_values("date").drop_duplicates(["Z", "N"], keep="last").reset_index(drop=True)
    return df


def labels_from_ensdf(gs: pd.DataFrame | None = None) -> pd.DataFrame:
    gs = ensdf_ground_states() if gs is None else gs
    rows = []
    for r in gs.itertuples(index=False):
        ok = (pd.notna(r.half_life_s) and r.half_life_s > 0 and pd.isna(r.half_life_qualifier)
              and pd.isna(r.width_ev) and not r.is_stable)
        log_t = math.log10(r.half_life_s) if ok else math.nan
        sig = (r.half_life_sigma_s / (r.half_life_s * math.log(10))
               if ok and pd.notna(r.half_life_sigma_s) else math.nan)
        out = {"Z": int(r.Z), "N": int(r.N), "A": int(r.A), "log_t": log_t, "log_t_sigma": sig,
               "date": r.date, "year": int(r.date[:4]) if str(r.date)[:4].isdigit() else None,
               "half_life_raw": r.half_life_raw}
        _partials(log_t, parse_ensdf_branchings(r.continuation or ""), out)
        rows.append(out)
    df = pd.DataFrame(rows)
    df.attrs["source"] = "ENSDF 2026-09-01"
    return df


def _revised(new: pd.Series, old: pd.Series, dex: float) -> pd.Series:
    return new.notna() & old.notna() & ((new - old).abs() > dex)


def time_split(name: str) -> dict[str, pd.DataFrame]:
    """``{"train": labels, "test_new": labels, "test_revised": labels}``; test tables carry
    the target columns filled only where that label is new (or revised) in the later edition.

    ``test_revised`` uses 0.3 dex for half-lives and 5 percentage points for P1n.
    """
    if name == "C_disc2003":
        return discovery_split(2020, C_CUTOFF)
    if name.startswith("inner:"):  # model selection and conformal calibration only
        return discovery_split(**INNER[name.removeprefix("inner:")])
    if name == "A_2016_2020":
        old, new = labels_from_nubase(2016), labels_from_nubase(2020)
        new_meta = new
    elif name == "B_2020_2026":
        old, new = labels_from_nubase(2020), labels_from_ensdf()
        new = new[new["year"].fillna(0) >= 2021]
        new_meta = new
    else:
        raise KeyError(name)
    j = new_meta.merge(old[["Z", "N", *TARGETS]], on=["Z", "N"], how="left", suffixes=("", "_old"))
    test_new = j[["Z", "N", "A"]].copy()
    test_rev = j[["Z", "N", "A"]].copy()
    for t in TARGETS:
        test_new[t] = j[t].where(j[t].notna() & j[f"{t}_old"].isna())
        test_rev[t] = j[t].where(_revised(j[t], j[f"{t}_old"], 5.0 if t == "pn" else 0.3))
    keep = lambda d: d[d[list(TARGETS)].notna().any(axis=1)].reset_index(drop=True)  # noqa: E731
    return {"train": old, "test_new": keep(test_new), "test_revised": keep(test_rev)}


# ------------------------------------------------------------------ split C (discovery year)

C_CUTOFF = 2003


def discovery_split(edition: int = 2020, cutoff: int = C_CUTOFF,
                    until: int | None = None) -> dict[str, pd.DataFrame]:
    """Train on ground states discovered <= ``cutoff``, test on those discovered after (and
    <= ``until`` if given), labels from one NUBASE edition on both sides. Nuclides without a
    discovery year are in neither set."""
    lab = labels_from_nubase(edition)
    yr = pd.to_numeric(lab["discovery_year"], errors="coerce")
    train = lab[yr <= cutoff].reset_index(drop=True)
    later = (yr > cutoff) & ((yr <= until) if until is not None else True)
    test = lab[later][["Z", "N", "A", *TARGETS]]
    test = test[test[list(TARGETS)].notna().any(axis=1)].reset_index(drop=True)
    train.attrs["source"] = f"NUBASE{edition} discovered <= {cutoff}"
    return {"train": train, "test_new": test, "test_revised": test.iloc[0:0]}


INNER = {  # model selection + conformal calibration, strictly before each split's cutoff
    "C_disc2003": dict(edition=2020, cutoff=1990, until=C_CUTOFF),
    "A_2016_2020": dict(edition=2016, cutoff=2006, until=2016),
    "B_2020_2026": dict(edition=2020, cutoff=2010, until=2020),
}
EDITION_CUTOFF = {  # (label edition, discovery cutoff for experimental masses)
    "C_disc2003": (2020, C_CUTOFF), "A_2016_2020": (2016, None), "B_2020_2026": (2020, None),
}


SPLITS = ("C_disc2003", "A_2016_2020", "B_2020_2026")
