"""COLLRULE (Incognita extension, not TALYS; default OFF): the incident-channel coupling scheme of the TARGET chosen by a global
rule on its measured low-lying structure instead of the header letter of `deformation/<Sym>.def`.

Keyword `collrule n|strict|trans|sv|y` (y = strict; sv = strict restricted to its S -> V class, the component that passed
COLLRULE's gates; n = TALYS, the default) or env `INCOGNITA_COLLRULE` (same values, used when the
keyword is off). The decisions are a table written by development notes from ENSDF 2026-09-01 adopted levels only
(R4/2 = E(4+_1)/E(2+_1), B(E2; 2+_1 -> 0+), ENSDF ground-state band flags); no reaction datum enters it:
  even-even   rotor R4/2 >= 3.0 -> R | vibrator [2.0, 2.4) -> V | spherical < 2.0 -> S | transitional [2.4, 3.0) -> letter kept
              (strict) or V (trans);
  odd-A/odd-odd  core R4/2 >= 3.0 and an ENSDF g.s. band -> R | core < 2.4 -> S | transitional core -> kept (strict) or S (trans).
Only rows whose letter changes are in the table; every other nucleus, and every residual nucleus of a run, is untouched.
How a new letter is realised (the TALYS machinery in each case):
  S  the target's block is read as `spherical y` reads it, for the target only (deformpar.f90:136-137);
  V  the block becomes g.s. + the 2+_1 level as a one-phonon lambda-2 vibration with the MEASURED beta2 (Raman convention,
     R0 = 1.2 A^1/3; a deformation length beta2 R0 when the file block is deftype D); the file's D rows are kept;
  R  TALYS's `autorot` band construction (deformpar.f90:241-262: ground band up to maxrot from the discrete levels, beta2/beta4
     from the mass table), without autorot's A > 150 / 8-from-magic test. If the band is incomplete in the level file the
     target stays S, exactly as autorot leaves it.
The OMP's colltype (omppar.f90:217/267: W_D d1 x 0.85 for a non-S target) follows the realised letter, as TALYS's does.

WEAKCPL (`collrule svw` / `svwa`, = sv plus weak-coupling CC; development notes): an odd-A target whose even-even
core(s) are STRICT vibrators (table weakcpl_table.csv from development notes, ENSDF only) is run as a V target in the
de-Shalit core-excitation (weak-coupling) picture: g.s. I (no phonon) + the multiplet |2+_core x I; J>, |I-2| <= J <= I+2,
each member a one-phonon lambda-2 level of its own band with beta_J = beta_core sqrt((2J+1)/5) (then
sum_J B(E2; I -> J) = B(E2; 0+ -> 2+)_core in ECIS's reduced-matrix-element convention, t^2/(2I+1)). Members are found by
weakcoupling.f90's spin/energy search around the core's E(2+_1), with the parity of the g.s. required (a 2+ phonon keeps it).
beta_core / E(2+_1) = the qualifying core's, or the mean of the A-1 and A+1 cores when both qualify. svw: file letter S
targets only (arm WS); svwa: also the file letter R ones (arm WA: Mn-55, Rh-103, Ag-107/109, Eu-151). The core 2+_1 is
then NOT also spread over the target's D levels by the DWBA weak coupling (no double counting)."""
from __future__ import annotations

import csv
import math
import os
from functools import lru_cache
from pathlib import Path

ENV = "INCOGNITA_COLLRULE"
_TABLE = Path(__file__).with_name("collrule_table.csv")
_WTABLE = Path(__file__).with_name("weakcpl_table.csv")
MAGIC = (2, 8, 20, 28, 50, 82, 126)


def mode(options=None) -> str:
    """'strict', 'trans' or '' (off)."""
    v = str(getattr(options, "collrule", "n") or "n").strip().lower()
    if v in ("n", "0", ""):
        v = os.environ.get(ENV, "").strip().lower()
    if v in ("y", "strict"):
        return "strict"
    if v == "trans":
        return "trans"
    if v in ("sv", "svw", "svwa"):
        return v
    if v in ("", "n", "0"):
        return ""
    raise ValueError(f"collrule: unknown value {v!r} (n|strict|trans|sv|svw|svwa|y)")


@lru_cache(maxsize=1)
def _table() -> dict:
    out = {}
    with open(_TABLE) as fh:
        for r in csv.DictReader(fh):
            b = float(r["beta2_be2"]) if r["beta2_be2"] not in ("", "nan") else math.nan
            out[(int(r["Z"]), int(r["A"]))] = dict(letter=r["letter"], strict=r["strict"], trans=r["trans"], beta2=b)
    return out


@lru_cache(maxsize=1)
def _wtable() -> dict:
    out = {}
    with open(_WTABLE) as fh:
        for r in csv.DictReader(fh):
            out[(int(r["Z"]), int(r["A"]))] = dict(arm=r["arm"], beta2=float(r["beta2"]), e2=float(r["e2_keV"]) / 1000.0)
    return out


def is_target(Z: int, A: int, options) -> bool:
    """(Z, A) is the target of a neutron-incident run."""
    return options.k0 == 1 and Z == options.Zinit and A - Z == options.Ninit - 1


def target_letter(Z: int, A: int, options) -> str | None:
    """The rule's new letter for the target (Z, A), or None (off / not the target / no change)."""
    m = mode(options)
    if not m or not is_target(Z, A, options):
        return None
    r = _table().get((int(Z), int(A)))
    if m in ("svw", "svwa") and int(A) % 2 == 1:  # WEAKCPL: odd-A weak-coupling CC ('W' = V realised by weak_block)
        w = _wtable().get((int(Z), int(A)))
        return "W" if w is not None and (w["arm"] == "WS" or m == "svwa") else None
    if m in ("sv", "svw", "svwa"):  # COLLRULE's registered component: the STRICT rule's S -> V class only (measured-B(E2) vibrators)
        return "V" if r is not None and r["letter"] == "S" and r["strict"] == "V" else None
    if r is None or r[m] == r["letter"]:
        return None
    return r[m]


def beta2(Z: int, A: int) -> float:
    return _table()[(int(Z), int(A))]["beta2"]


def band_complete(jdis, parlev, A: int, maxrot: int, nmax: int) -> bool:
    """deformpar.f90:245-259: the ground band J0 + dspin (i - 1), i = 2 .. maxrot + 1, same parity as the g.s.; TALYS keeps the
    rotor iff the LAST member (indexcc(ndef)) is found among levels 1 .. nmax."""
    dspin = 2.0 if A % 2 == 0 else 1.0
    ndef = maxrot + 1
    spin = float(jdis[0]) + dspin * (ndef - 1)
    return any(float(jdis[n]) == spin and int(parlev[n]) == int(parlev[0]) for n in range(1, nmax + 1))


def autorot_region(Z: int, A: int) -> bool:
    """deformpar.f90:241: A > 150 and at least 8 nucleons from every magic number (the TALYS autorot test)."""
    N = A - Z
    return A > 150 and min(min(abs(N - m), abs(Z - m)) for m in (2, 8, 20, 28, 50, 82, 126)) >= 8


def vib_block(Z: int, A: int, block, jdis, parlev, nmax: int):
    """The target's `.def` block rebuilt for a V scheme: g.s. (V, band 0), the first 2+ level as a one-phonon lambda-2 member of
    vibband 1 with the measured beta2 (length beta2 1.2 A^1/3 fm when the block is deftype D), and the file's D rows except the
    2+_1's own. None when the level file has no 2+ (the target keeps its letter)."""
    n2 = next((n for n in range(1, nmax + 1) if float(jdis[n]) == 2.0 and int(parlev[n]) == 1), None)
    if n2 is None:
        return None
    deftype = block[1] if block is not None else "B"
    b = beta2(Z, A)
    val = round(b * 1.2 * A ** (1.0 / 3.0), 5) if deftype == "D" else round(b, 5)
    rows = [(0, "V", 0, 0, 0, 0, (0.0, 0.0, 0.0, 0.0)), (n2, "V", 1, 2, 0, 1, (val, 0.0, 0.0, 0.0))]
    if block is not None:
        rows += [r for r in block[2] if r[1] == "D" and r[0] not in (0, n2)]
    rows = [rows[0]] + sorted(rows[1:], key=lambda r: r[0])
    return ("V", deftype, rows)


def weak_block(Z: int, A: int, block, jdis, parlev, edis, nmax: int):
    """WEAKCPL: the odd target's `.def` block rebuilt as a weak-coupling V scheme: g.s. (V, band 0) + one row per multiplet
    member J (V, band k, lambda 2, one phonon, beta_core sqrt((2J+1)/5); a length beta 1.2 A^1/3 fm when the block is deftype
    D) + the file's D rows except the members' and the g.s.'s. Members: weakcoupling.f90's search (j = int|I-2| .. int(I+2);
    outward from `middle` = (first level above the core E(2+_1)) + 1, upward first; first free level with int(J) == j), plus
    parity == g.s. parity. None when no member is found (the target keeps its letter)."""
    w = _wtable()[(int(Z), int(A))]
    b, ec = w["beta2"], w["e2"]
    j0 = float(jdis[0])
    middle = 0
    for i2 in range(1, len(edis)):
        if edis[i2] > ec:
            middle = i2 + 1
            break
    taken, members = set(), []
    for j in range(int(abs(j0 - 2.0)), int(j0 + 2.0) + 1):
        for i3 in range(0, len(edis)):
            hit = None
            for i4 in (1, -1):
                if i3 == 0 and i4 == -1:
                    break
                i5 = middle + i4 * i3
                if i5 < 1 or i5 > nmax or i5 in taken:
                    continue
                if int(jdis[i5]) == j and int(parlev[i5]) == int(parlev[0]):
                    hit = i5
                    break
            if hit is not None:
                taken.add(hit)
                members.append(hit)
                break
    if not members:
        return None
    deftype = block[1] if block is not None else "B"
    rows = [(0, "V", 0, 0, 0, 0, (0.0, 0.0, 0.0, 0.0))]
    for k, n in enumerate(sorted(members), 1):
        bj = b * math.sqrt((2.0 * float(jdis[n]) + 1.0) / 5.0)
        val = round(bj * 1.2 * A ** (1.0 / 3.0), 5) if deftype == "D" else round(bj, 5)
        rows.append((n, "V", k, 2, 0, 1, (val, 0.0, 0.0, 0.0)))
    if block is not None:
        rows += [r for r in block[2] if r[1] == "D" and r[0] != 0 and r[0] not in taken]
    rows = [rows[0]] + sorted(rows[1:], key=lambda r: r[0])
    return ("V", deftype, rows)


def core_skip(target, core_levels) -> int | None:
    """WEAKCPL: the index of the core's 2+_1 when the target is a weak-coupling CC target (its multiplet is in the CC set), so
    the DWBA weak coupling (weakcoupling.f90) does not spread the same 2+ over other D levels; None otherwise."""
    if not getattr(target, "weakcc", False):
        return None
    sp = core_levels.all_spin.numpy()
    pa = core_levels.all_parity.numpy()
    return next((i for i in range(1, core_levels.nlevmax2 + 1) if float(sp[i]) == 2.0 and int(pa[i]) == 1), None)
