"""EXFOR reaction-string parser (SF1–SF9 decomposition, blueprint §4.2) and the
ENDF MT mapping for the common neutron channels.

Grammar (EXFOR Formats Manual, chapter 8)::

    (SF1(SF2,SF3)SF4,SF5,SF6,SF7,SF8,SF9)

with SF1 = target ``Z-SYM-A[-M|-G|-Mn|-L]``, SF2 = projectile, SF3 = process,
SF4 = product (optional), SF5 = branch, SF6 = parameter (``SIG``, ``DA``, ...),
SF7 = particle considered, SF8 = modifier (``MXW``, ``SPA``, ``RAW`` ...), SF9 =
data type. Combinations wrap several reaction codes in parentheses joined by an
operator, e.g. ``((92-U-238(N,F),,SIG)/(92-U-235(N,F),,SIG))``.

Only the outer structure is interpreted here; everything is kept verbatim in the
``ReactionSF`` block so WP-12 can revisit corner cases.
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field

from data.schema.measurement import QuantityType, ReactionSF

__all__ = [
    "MT_BY_CHANNEL",
    "ParsedReaction",
    "ReactionParseError",
    "Target",
    "classify_quantity",
    "mt_for",
    "parse_reaction",
    "parse_target",
    "split_top_level",
]


class ReactionParseError(ValueError):
    pass


# --------------------------------------------------------------------------- target


@dataclass(frozen=True)
class Target:
    z: int
    a: int  # 0 == natural abundance
    iso: int = 0  # 0 ground, 1 first isomer, ...
    symbol: str = ""
    raw: str = ""


_TARGET_RE = re.compile(
    r"^(?P<z>\d{1,3})-(?P<sym>[A-Z]{1,2})-(?P<a>\d{1,3})(?:-(?P<iso>G|M\d?|L\d?|T))?$"
)


def parse_target(code: str) -> Target:
    """``"26-FE-56"`` → ``Target(26, 56)``; ``"79-AU-197-M1"`` → iso 1; ``"26-FE-0"`` → natural."""
    code = code.strip().upper()
    m = _TARGET_RE.match(code)
    if m is None:
        raise ReactionParseError(f"unparseable target {code!r}")
    iso_code = m["iso"]
    if iso_code is None or iso_code == "G":
        iso = 0
    elif iso_code.startswith("M"):
        iso = int(iso_code[1:]) if len(iso_code) > 1 else 1
    else:  # L (level) / T (total): treat as ground state; the code stays in sf1
        iso = 0
    return Target(int(m["z"]), int(m["a"]), iso, m["sym"], code)


# --------------------------------------------------------------------------- projectile

_PROJECTILE = {
    "N": "n",
    "P": "p",
    "D": "d",
    "T": "t",
    "HE3": "h",
    "A": "a",
    "G": "g",
    "E": "e",
    "0": "0",  # target property / resonance parameter (no projectile)
}


def projectile_symbol(sf2: str) -> str:
    sf2 = sf2.strip().upper()
    if sf2 in _PROJECTILE:
        return _PROJECTILE[sf2]
    return sf2.lower()  # heavy ions ("6-C-12"), pions ("PIP"), etc.: keep the code


# --------------------------------------------------------------------------- MT map

_PARTICLE_ORDER = ("N", "P", "D", "T", "HE3", "A")


def _channel_key(sf3: str) -> frozenset[tuple[str, int]] | str:
    """``"2N+A"`` → frozenset({("N", 2), ("A", 1)}); non-particle codes returned verbatim."""
    sf3 = sf3.strip().upper()
    if sf3 in ("TOT", "EL", "NON", "INL", "F", "ABS", "X", "SCT", "THS", "0"):
        return sf3
    counts: Counter[str] = Counter()
    for tok in sf3.split("+"):
        m = re.match(r"^(\d*)(N|P|D|T|HE3|A)$", tok)
        if m is None:
            return sf3
        counts[m[2]] += int(m[1] or 1)
    return frozenset(counts.items())


def _k(spec: str) -> frozenset[tuple[str, int]] | str:
    return _channel_key(spec)


# Neutron-induced channels, ENDF-6 MT numbers (BNL-90365 App. B)
MT_BY_CHANNEL: dict[frozenset[tuple[str, int]] | str, int] = {
    "TOT": 1,
    "EL": 2,
    "NON": 3,
    "INL": 4,
    "F": 18,
    "ABS": 27,
    _k("2N"): 16,
    _k("3N"): 17,
    _k("N+A"): 22,
    _k("N+3A"): 23,
    _k("2N+A"): 24,
    _k("3N+A"): 25,
    _k("N+P"): 28,
    _k("N+2A"): 29,
    _k("2N+2A"): 30,
    _k("N+D"): 32,
    _k("N+T"): 33,
    _k("N+HE3"): 34,
    _k("N+D+2A"): 35,
    _k("N+T+2A"): 36,
    _k("4N"): 37,
    _k("2N+P"): 41,
    _k("3N+P"): 42,
    _k("N+2P"): 44,
    _k("N+P+A"): 45,
    _k("P"): 103,
    _k("D"): 104,
    _k("T"): 105,
    _k("HE3"): 106,
    _k("A"): 107,
    _k("2A"): 108,
    _k("3A"): 109,
    _k("2P"): 111,
    _k("P+A"): 112,
    _k("T+2A"): 113,
    _k("D+2A"): 114,
    _k("P+D"): 115,
    _k("P+T"): 116,
    _k("D+A"): 117,
    _k("5N"): 152,
    _k("6N"): 153,
    _k("7N"): 160,
    _k("8N"): 161,
    _k("4N+P"): 156,
    _k("3N+D"): 157,
    _k("2N+D"): 154,
    _k("2N+T"): 159,
    _k("2N+HE3"): 174,
    _k("N+2D"): 171,
    _k("3P"): 197,
}
# "G" is not a particle token in _channel_key; register explicitly
MT_BY_CHANNEL["G"] = 102


def mt_for(sf2: str, sf3: str) -> int | None:
    """ENDF MT for a neutron-induced channel; ``None`` for anything else / unknown."""
    if sf2.strip().upper() != "N":
        return None
    key = _channel_key(sf3)
    return MT_BY_CHANNEL.get(key)


# --------------------------------------------------------------------------- quantity

_RESONANCE_SF6 = {
    "WID",
    "WID/RED",
    "WID/STR",
    "EN",
    "ARE",
    "STF",
    "D",
    "J",
    "L",
    "AG",
    "RED",
    "AMP",
    "SRC",
    "LDP",
    "SCT",
    "PTY",
    "STR",
    "SPC",
}
_INTEGRAL_SF8 = {"MXW", "SPA", "FIS", "FST", "AV", "BRA", "BRS", "EPI", "MSC", "TTA", "TT"}
_SPECTRUM_SF6 = {"DE", "DA/DE", "DA/DE/DE", "DE/DE", "DE/DA", "DA/DA/DE", "DP"}
_ANGULAR_SF6 = {"DA", "DA/DA", "DA/DA/DA", "DA/DE/DA"}


def classify_quantity(sf: ReactionSF, *, is_ratio: bool = False) -> QuantityType:
    if is_ratio:
        return QuantityType.RATIO
    sf3 = (sf.sf3 or "").upper()
    sf6 = (sf.sf6 or "").upper()
    sf8 = (sf.sf8 or "").upper()
    if sf6 == "RI":
        return QuantityType.INTEGRAL
    if sf6 in _RESONANCE_SF6 or sf3 == "0":
        return QuantityType.RESONANCE_PARAMETER
    if sf6 in _ANGULAR_SF6:
        return QuantityType.ANGULAR_DISTRIBUTION
    if sf6 in _SPECTRUM_SF6:
        return QuantityType.SPECTRUM
    if sf6 == "SIG":
        for mod in sf8.split("/"):
            if mod in _INTEGRAL_SF8:
                return QuantityType.INTEGRAL
        return QuantityType.CROSS_SECTION
    return QuantityType.OTHER


# --------------------------------------------------------------------------- parsing


@dataclass
class ParsedReaction:
    raw: str
    sf: ReactionSF
    target: Target
    projectile: str
    mt: int | None
    quantity: QuantityType
    is_ratio: bool = False
    operator: str | None = None  # "/", "*", "+", "-", "=" for combinations
    components: list[ParsedReaction] = field(default_factory=list)

    @property
    def denominator(self) -> ParsedReaction | None:
        if self.operator in ("/", "//") and len(self.components) == 2:
            return self.components[1]
        return None


def split_top_level(s: str) -> tuple[list[str], list[str]]:
    """Split ``"(A)/(B)"`` into ``(["(A)", "(B)"], ["/"])`` at top-level operators."""
    parts: list[str] = []
    ops: list[str] = []
    depth = 0
    cur: list[str] = []
    for ch in s:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if depth == 0 and ch in "/*+-=":
            joined = "".join(cur).strip()
            if joined.endswith(")"):
                parts.append(joined)
                ops.append(ch)
                cur = []
                continue
            if not cur and ops:  # doubled operator such as "//" (ratio of ratios)
                ops[-1] += ch
                continue
        cur.append(ch)
    if cur:
        parts.append("".join(cur).strip())
    return parts, ops


_SIMPLE_RE = re.compile(
    r"^(?P<sf1>[^(),]+)\((?P<sf2>[^,()]+),(?P<sf3>[^()]*)\)(?P<sf4>[^,()]*)(?:,(?P<rest>.*))?$"
)


def _strip_outer(s: str) -> str:
    s = s.strip()
    if s.startswith("(") and s.endswith(")"):
        depth = 0
        for i, ch in enumerate(s):
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
                if depth == 0 and i != len(s) - 1:
                    return s  # closing paren before the end -> not a single group
        return s[1:-1]
    return s


def _parse_simple(code: str, raw: str) -> ParsedReaction:
    m = _SIMPLE_RE.match(code.strip())
    if m is None:
        raise ReactionParseError(f"unparseable reaction {raw!r}")
    rest = (m["rest"] or "").split(",")
    rest += [""] * (5 - len(rest))
    sf = ReactionSF(
        sf1=m["sf1"].strip() or None,
        sf2=m["sf2"].strip() or None,
        sf3=m["sf3"].strip() or None,
        sf4=m["sf4"].strip() or None,
        sf5=rest[0].strip() or None,
        sf6=rest[1].strip() or None,
        sf7=rest[2].strip() or None,
        sf8=rest[3].strip() or None,
        sf9=",".join(rest[4:]).strip() or None,
    )
    target = parse_target(sf.sf1 or "")
    return ParsedReaction(
        raw=raw,
        sf=sf,
        target=target,
        projectile=projectile_symbol(sf.sf2 or ""),
        mt=mt_for(sf.sf2 or "", sf.sf3 or ""),
        quantity=classify_quantity(sf),
    )


def parse_reaction(code: str) -> ParsedReaction:
    """Parse a full EXFOR REACTION code (with its outer parentheses).

    Combinations return the *first* component's decomposition as ``sf``/target,
    with ``is_ratio``/``operator``/``components`` describing the combination.
    """
    raw = code.strip()
    inner = _strip_outer(raw)
    parts, ops = split_top_level(inner)
    if len(parts) == 1 and not ops:
        if inner.startswith("(("):
            # doubly wrapped single reaction, e.g. "((...))"
            return parse_reaction(inner)
        return _parse_simple(inner, raw)
    if not ops:
        raise ReactionParseError(f"unparseable combination {raw!r}")
    comps = [parse_reaction(p) for p in parts]
    op = ops[0]
    first = comps[0]
    is_ratio = op.startswith("/") or (op == "=" and (comps[1].operator or "").startswith("/"))
    quantity = classify_quantity(first.sf, is_ratio=is_ratio)
    if op == "=" and not is_ratio:
        quantity = first.quantity
    return ParsedReaction(
        raw=raw,
        sf=first.sf,
        target=first.target,
        projectile=first.projectile,
        mt=first.mt,
        quantity=quantity,
        is_ratio=is_ratio,
        operator=op,
        components=comps,
    )
