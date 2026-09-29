"""NUBASE2020 parser (``nubase_4.mas20``): ground states and isomers with excitation energy,
half-life, spin-parity, decay modes and reference years. Blueprint §4.2.

Column positions are the ones documented in the file header (1-indexed, inclusive) and are
converted to 0-indexed slices below. Every raw string that carries evaluator markup
(half-life, spin-parity, decay modes) is kept next to its parsed form.
"""

from __future__ import annotations

import math
import re
from pathlib import Path

import numpy as np
import pandas as pd

__all__ = [
    "HALF_LIFE_UNIT_S",
    "NUBASE2016_FILE",
    "NUBASE_FILE",
    "SECONDS_PER_YEAR",
    "load_nubase",
    "parse_decay_modes",
    "parse_half_life",
    "parse_spin_parity",
]

REPO = Path(__file__).resolve().parents[2]
NUBASE_FILE = REPO / "raw" / "nubase2020" / "nubase_4.mas20.txt"
# NUBASE2016 (Audi et al., CPC 41 030001) -- fetched 2026-09-12 for the decay-data time split.
NUBASE2016_FILE = REPO / "raw" / "nubase2016" / "nubase2016.txt"

# NUBASE uses the tropical year: 1 y = 365.2422 d.
SECONDS_PER_YEAR = 365.2422 * 86400.0
_Y = SECONDS_PER_YEAR
HALF_LIFE_UNIT_S: dict[str, float] = {
    "ys": 1e-24, "zs": 1e-21, "as": 1e-18, "fs": 1e-15, "ps": 1e-12, "ns": 1e-9,
    "us": 1e-6, "ms": 1e-3, "s": 1.0, "m": 60.0, "h": 3600.0, "d": 86400.0,
    "y": _Y, "ky": 1e3 * _Y, "My": 1e6 * _Y, "Gy": 1e9 * _Y, "Ty": 1e12 * _Y,
    "Py": 1e15 * _Y, "Ey": 1e18 * _Y, "Zy": 1e21 * _Y, "Yy": 1e24 * _Y,
}  # fmt: skip

# 0-indexed slices from the header's 1-indexed inclusive columns.
_S = {
    "A": (0, 3),
    "Z": (4, 7),
    "iso": (7, 8),
    "a_el": (11, 16),
    "s_code": (16, 17),
    "mass_excess": (18, 31),
    "mass_excess_unc": (31, 42),
    "excitation": (42, 54),
    "excitation_unc": (54, 65),
    "exc_origin": (65, 67),
    "isomer_order_uncertain": (67, 68),
    "isomer_order_inverted": (68, 69),
    "half_life": (69, 78),
    "half_life_unit": (78, 80),
    "half_life_unc": (81, 88),
    "spin_parity": (88, 102),
    "ensdf_year": (102, 104),
    "discovery_year": (114, 118),
    "decay": (119, None),
}

# NUBASE2016 uses a narrower layout (no ordering flags, 2-char ENSDF year at 94-95,
# discovery year at 106-109, decay modes from 111). 0-indexed slices, same keys as ``_S``.
_S2016 = {
    "A": (0, 3),
    "Z": (4, 7),
    "iso": (7, 8),
    "a_el": (11, 16),
    "s_code": (16, 17),
    "mass_excess": (18, 29),
    "mass_excess_unc": (29, 38),
    "excitation": (38, 48),
    "excitation_unc": (48, 56),
    "exc_origin": (56, 58),
    "isomer_order_uncertain": (58, 59),
    "isomer_order_inverted": (59, 60),
    "half_life": (60, 69),
    "half_life_unit": (69, 71),
    "half_life_unc": (72, 79),
    "spin_parity": (79, 93),
    "ensdf_year": (93, 95),
    "discovery_year": (105, 109),
    "decay": (110, None),
}


def _num(field: str) -> tuple[float, bool]:
    s = field.strip()
    if not s or s == "*" or s == "non-exist":
        return math.nan, False
    if "#" in s:
        return float(s.replace("#", "")), True
    return float(s), False


_LIMIT_RE = re.compile(r"^([<>~])\s*([0-9.]+)\s*([A-Za-z]+)$")
_ASYM_RE = re.compile(r"^\+([0-9.eE+-]+)-([0-9.eE+-]+)$")


def parse_half_life(value: str, unit: str, unc: str) -> dict[str, object]:
    """Half-life fields -> seconds, log10 seconds, flags.

    ``value`` may be a number (``#`` = from systematics), ``stbl`` or ``p-unst``; ``unc`` may be
    a number in the same unit, an asymmetric ``+a-b`` or, when ``value`` is blank/``stbl``, a
    limit such as ``>300ns`` (kept as ``half_life_limit_kind`` / ``half_life_limit_s``).
    """
    v, u, du = value.strip(), unit.strip(), unc.strip()
    out: dict[str, object] = {
        "half_life_raw": " ".join(x for x in (v, u, du) if x),
        "half_life_s": math.nan,
        "half_life_unc_s": math.nan,
        "log10_half_life_s": math.nan,
        "log10_half_life_unc": math.nan,
        "half_life_extrapolated": False,
        "is_stable": False,
        "is_particle_unstable": False,
        "half_life_limit_kind": None,
        "half_life_limit_s": math.nan,
    }
    if v == "stbl":
        out["is_stable"] = True
    elif v.rstrip("#") == "p-unst":  # NUBASE2016 writes "p-unst#"
        out["is_particle_unstable"] = True
    elif v and v[0] in "<>":
        # a limit in the value field itself, e.g. '>100# ns' or '<1 us'
        val, ex = _num(v[1:])
        if u not in HALF_LIFE_UNIT_S:
            raise ValueError(f"unknown half-life unit {u!r} in {value!r} {unit!r}")
        out["half_life_limit_kind"] = v[0]
        out["half_life_limit_s"] = val * HALF_LIFE_UNIT_S[u]
        out["half_life_extrapolated"] = ex
    elif v:
        val, ex = _num(v.lstrip("~"))  # '~' = approximate; kept in half_life_raw
        if u not in HALF_LIFE_UNIT_S:
            raise ValueError(f"unknown half-life unit {u!r} in {value!r} {unit!r}")
        scale = HALF_LIFE_UNIT_S[u]
        t = val * scale
        out["half_life_s"] = t
        out["half_life_extrapolated"] = ex
        out["log10_half_life_s"] = math.log10(t) if t > 0 else math.nan
        if du:
            m = _ASYM_RE.match(du)
            if m:
                dt = max(float(m.group(1)), float(m.group(2))) * scale
            else:
                try:
                    dt = float(du.replace("#", "")) * scale
                except ValueError:
                    dt = math.nan
            out["half_life_unc_s"] = dt
            if t > 0 and not math.isnan(dt):
                out["log10_half_life_unc"] = dt / (t * math.log(10.0))
    m = _LIMIT_RE.match(du) if du else None
    if m:
        kind, num, lu = m.groups()
        if lu in HALF_LIFE_UNIT_S:
            out["half_life_limit_kind"] = kind
            out["half_life_limit_s"] = float(num) * HALF_LIFE_UNIT_S[lu]
    return out


_J_RE = re.compile(r"^(\d+(?:/2)?)([+-]?)$")


def _parse_j(tok: str) -> tuple[float | None, int | None]:
    m = _J_RE.match(tok)
    if not m:
        return None, None
    j = m.group(1)
    jv = float(j[:-2]) / 2 if j.endswith("/2") else float(j)
    p = {"+": 1, "-": -1, "": None}[m.group(2)]
    return jv, p


def parse_spin_parity(raw: str) -> dict[str, object]:
    """``'5/2+#'`` -> J=2.5, parity=+1, tentative; ``'(2+,3-)'`` -> J=None, parity=None.

    Rules: ``*`` = directly measured; ``#`` = from systematics (tentative); parentheses =
    tentative; comma-separated alternatives = ambiguous, J/parity kept only if all
    alternatives agree; a trailing parity after a group (``(3/2,5/2)+``) applies to all.
    ``T=...`` is the isospin and is returned separately.
    """
    s = raw.strip()
    out: dict[str, object] = {
        "spin_parity_raw": s or None,
        "spin": None,
        "parity": None,
        "spin_parity_tentative": False,
        "spin_parity_measured": False,
        "isospin": None,
    }
    if not s:
        return out
    m = re.search(r"T=(\S+)", s)
    if m:
        out["isospin"] = m.group(1)
        s = s[: m.start()].strip()
    s = s.replace("frg", "").strip()
    out["spin_parity_measured"] = "*" in s
    systematics = "#" in s
    s = s.replace("*", "").replace("#", "")
    tentative = systematics or "(" in s
    core = s.replace("(", "").replace(")", "").replace(" ", "")
    if not core:
        out["spin_parity_tentative"] = tentative
        return out
    parts = [p for p in core.split(",") if p]
    if len(parts) > 1:
        tentative = True
        # (3/2,5/2)+ style: propagate a trailing parity to alternatives lacking one
        last_p = parts[-1][-1] if parts[-1] and parts[-1][-1] in "+-" else ""
        if last_p and all(p[-1] not in "+-" for p in parts[:-1]):
            parts = [p + last_p for p in parts[:-1]] + [parts[-1]]
    parsed = [_parse_j(p) for p in parts]
    js = {j for j, _ in parsed}
    ps = {p for _, p in parsed}
    if len(js) == 1 and None not in js:
        out["spin"] = js.pop()
    if len(ps) == 1 and None not in ps:
        out["parity"] = ps.pop()
    elif len(parts) == 1 and core[-1] in "+-" and parsed[0][1] is None:
        # unparseable magnitude (e.g. '>3-') but a definite parity
        out["parity"] = 1 if core[-1] == "+" else -1
    out["spin_parity_tentative"] = tentative or (out["spin"] is None and len(parts) > 1)
    return out


_BR_RE = re.compile(
    r"^(?P<mode>[^=<>~?\s]+)\s*(?P<q>[=<>~])?\s*(?P<val>[-+]?[0-9][0-9.]*(?:[eE][-+]?\d+)?)?"
    r"(?:\s+(?P<unc>[^\s?]+))?\s*(?P<qq>\?)?$"
)


def _last_digit_sigma(val: str, unc: str) -> float:
    """NUBASE quotes uncertainties in units of the last digit of the value."""
    m = _ASYM_RE.match(unc)
    if m:
        unc = str(max(float(m.group(1)), float(m.group(2))))
    if "." in unc or "e" in unc.lower():
        return float(unc)
    mant, _, exp = val.lower().partition("e")
    decimals = len(mant.split(".")[1]) if "." in mant else 0
    scale = 10.0 ** (int(exp) if exp else 0)
    return float(unc) * 10.0 ** (-decimals) * scale


def parse_decay_modes(raw: str) -> list[dict[str, object]]:
    """``'B-=100;B-n=2.3 5;IT ?'`` -> list of {mode, qualifier, branching_pct, sigma_pct,
    extrapolated, raw}.

    Branchings are in percent as NUBASE quotes them. ``qualifier`` is one of ``= < > ~ ?``
    (``?`` when the mode is only suspected or the value is ``?``).
    """
    out = []
    items: list[str] = []
    for chunk in raw.strip().split(";"):
        # a few entries lack the ';' between suspected modes: 'B+p ? 2p ?'
        items.extend(re.split(r"(?<=\?)\s+(?=\S)", chunk.strip()))
    for item in items:
        item = item.strip()
        if not item:
            continue
        core = re.sub(r"\[.*?\]", "", item).strip()  # 'IT=100[gs=0,m=100]' annotations
        systematics = core.endswith("#")  # branching from systematics
        core = core.rstrip("#")
        m = _BR_RE.match(core)
        if not m:
            out.append(
                {
                    "mode": core,
                    "qualifier": "?",
                    "branching_pct": math.nan,
                    "sigma_pct": math.nan,
                    "extrapolated": systematics,
                    "raw": item,
                }
            )
            continue
        mode = m.group("mode").strip()
        q = m.group("q") or "="
        val = m.group("val")
        unc = m.group("unc")
        if m.group("qq") or val is None:
            q = "?" if (val is None or m.group("qq")) else q
        br = float(val) if val is not None else math.nan
        sig = math.nan
        if val is not None and unc is not None:
            try:
                sig = _last_digit_sigma(val, unc)
            except ValueError:
                sig = math.nan
        out.append(
            {
                "mode": mode,
                "qualifier": q,
                "branching_pct": br,
                "sigma_pct": sig,
                "extrapolated": systematics,
                "raw": item,
            }
        )
    return out


def _year(two_or_four: str) -> int | None:
    s = two_or_four.strip()
    if not s or not s.isdigit():
        return None
    v = int(s)
    if len(s) == 4:
        return v
    return 1900 + v if v >= 50 else 2000 + v


def _is_row(line: str) -> bool:
    return len(line) > 20 and line[0:3].strip().isdigit() and line[4:7].strip().isdigit()


def _masses_2016(line: str) -> tuple[float, bool, float, float, bool, float]:
    """NUBASE2016's mass/excitation block (columns 19-60) is not column-aligned: '5300#  200#'
    and '472.2074  0.0008' start at different offsets. Read it as whitespace tokens --
    mass excess, its uncertainty, then optionally excitation energy and its uncertainty,
    then an optional origin code (letters)."""
    nums = []
    for tok in line[18:60].split():
        try:
            nums.append(_num(tok))
        except ValueError:
            continue  # origin codes ('RQ', 'EU', ...) and 'non-exist'
    nums += [(math.nan, False)] * (4 - len(nums))
    (me, me_ex), (me_u, _), (ex, ex_ex), (ex_u, _) = nums[:4]
    return me, me_ex, me_u, ex, ex_ex, ex_u


def load_nubase(path: Path = NUBASE_FILE, edition: int | None = None) -> pd.DataFrame:
    """One row per NUBASE entry (ground states, isomers, levels, resonances, IAS).

    ``edition`` selects the column layout (2020 or 2016); by default it is read from the
    file name, so ``load_nubase(NUBASE2016_FILE)`` just works.
    """
    path = Path(path)
    if edition is None:
        edition = 2016 if "2016" in path.name else 2020
    fields = _S2016 if edition == 2016 else _S
    rows = []
    n_unparsed = 0
    with path.open() as fh:
        for line in fh:
            line = line.rstrip("\n")
            if line.startswith("#") or not _is_row(line):
                continue
            line = line.ljust(210)

            def g(k: str, _line: str = line) -> str:
                return _line[slice(*fields[k])]

            A = int(g("A"))
            Z = int(g("Z"))
            iso = int(g("iso"))
            a_el = g("a_el").strip()
            symbol = re.sub(r"^\d+", "", a_el).strip()
            if edition == 2016:
                me, me_ex, me_u, ex, ex_ex, ex_u = _masses_2016(line)
            else:
                me, me_ex = _num(g("mass_excess"))
                me_u, _ = _num(g("mass_excess_unc"))
                ex, ex_ex = _num(g("excitation"))
                ex_u, _ = _num(g("excitation_unc"))
            rec: dict[str, object] = {
                "A": A,
                "Z": Z,
                "N": A - Z,
                "iso": iso,
                "s_code": g("s_code").strip() or None,
                "symbol": symbol,
                # NUBASE lists a few isomers only to say they do not exist ("non-exist").
                "non_existent": "non-exist" in line[18:65],
                "mass_excess_kev": me,
                "mass_excess_unc_kev": me_u,
                "mass_excess_extrapolated": me_ex,
                "excitation_kev": ex,
                "excitation_unc_kev": ex_u,
                "excitation_extrapolated": ex_ex,
                "exc_origin": g("exc_origin").strip() or None,
                "isomer_order_uncertain": g("isomer_order_uncertain").strip() == "*",
                "isomer_order_inverted": g("isomer_order_inverted").strip() == "&",
            }
            try:
                rec.update(parse_half_life(g("half_life"), g("half_life_unit"), g("half_life_unc")))
            except ValueError:
                if edition == 2020:
                    raise
                # NUBASE2016 puts a few non-half-life notes in the field ('R=2.0~0.5' for
                # resonances): keep the raw string, parse nothing, never a label.
                rec.update(parse_half_life("", "", ""))
                rec["half_life_raw"] = " ".join(line[60:79].split())
                n_unparsed += 1
            rec.update(parse_spin_parity(g("spin_parity")))
            rec["ensdf_year"] = _year(g("ensdf_year"))
            rec["discovery_year"] = _year(g("discovery_year"))
            decay_raw = g("decay").strip()
            rec["decay_raw"] = decay_raw or None
            rec["decay_modes"] = parse_decay_modes(decay_raw)
            rows.append(rec)
    df = pd.DataFrame(rows)
    if df.empty:
        raise ValueError(f"{path}: no data rows recognised")
    dup = df.duplicated(["Z", "N", "iso"])
    if dup.any():
        dups = df[dup][["Z", "A", "iso"]].values.tolist()
        raise ValueError(f"{path}: duplicate (Z, N, iso): {dups}")
    for c in ("ensdf_year", "discovery_year"):
        df[c] = df[c].astype("Int64")
    df["spin"] = df["spin"].astype("Float64")
    df["parity"] = df["parity"].astype("Int64")
    df = df.sort_values(["Z", "N", "iso"]).reset_index(drop=True)
    df.attrs["source_version"] = f"NUBASE{edition}"
    df.attrs["half_life_unparsed"] = n_unparsed
    return df


def stable_count(df: pd.DataFrame) -> int:
    return int(np.sum(df["is_stable"] & (df["iso"] == 0)))
