"""NPWINDOW: windowed target level-density factor on D0-unanchored targets (blind global rule; Incognita extension, not TALYS).

Card NPWINDOW (development notes; prereg 8c81704ef, result 9e82b62f6); promoted as an engine option by NPWPROMO.

Rule (one global form, no per-nucleus value):
- Class U: the TARGET X = (Z, A) of a neutron-induced run has no measured s-wave D0 of its own, i.e. the RIPL/TALYS resonance
  table lists no l = 0 D0 > 0 for compound (Z, A) (= (Z, A-1) + n). An input-availability flag only; the D0 values never enter.
  The flag list is `npwindow_d0anchored.csv` (parsed from talys structure/resonances/*.res; development notes).
- Change: the continuum level density of X itself (its (n,n') residual role; ground state, every LD consumer) is multiplied by
  exp(s(Ex)), s(Ex) = dc_X sqrt(S_n(X)) smoothstep(Ex - E_lo), E_lo = max(Ecut_X + 2, S_n(X) - 6) MeV, smoothstep rising over
  1 MeV as 3x^2 - 2x^3 (0 below E_lo). Every other nucleus, the discrete levels and anchored targets are unchanged.
- dc_X: the frozen MS2BLIND A3 global rule (development notes; coefficients below) on X's blind
  features: parity class, |beta2|, mass-table shell correction deltaW, magic proximity, X's production ctable field value;
  rounded to 1e-4 (as the NPWINDOW record, development notes).
- S_n, Ecut = edis[Nlast] of X's own ground-state LD record (as INGDUMP's ecut_mev / sn_mev).
- Engine form = the NPWINDOW record exactly: the shift s(Ex)/sqrt(Ex) as ENGADJ `eadj ctable Z A tal` hats (nodes every
  0.25 MeV on 0-31 MeV, least squares on a 0.02 MeV grid, development notes, `MX` arithmetic and text format), applied
  through the ENGADJ ctable hook (models._adjusted). While the rule applies, the run behaves as an ENGADJ run with those lines
  (native LD kernels off, stage-cache token carries the rule).

Switch: deck keyword `npwindow y|n` (Options.npwindow); `INCOGNITA_NPWINDOW` (y|n|1|0), when set, wins. Default y (ON, NPWPROMO);
`npwindow n` reproduces the previous engine bit for bit (every hook first asks `applies_run()`).

Test: tests/hf/test_npwindow.py
"""

from __future__ import annotations

import math
import os
from functools import lru_cache
from pathlib import Path

import numpy as np

ENV = "INCOGNITA_NPWINDOW"
EFF = "INCOGNITA_NPWINDOW_EFF"   # run-scoped state written at Cascade set-up: "Z,A" of an applying target, else "0"
DEFAULT = "y"  # NPWPROMO: default ON (production); `npwindow n` / INCOGNITA_NPWINDOW=0 = the previous engine bit for bit
_TABLE = Path(__file__).with_name("npwindow_d0anchored.csv")

#: MS2BLIND A3 (development notes: `dctable_coef`, lam 1, 960 nuclei)
_A3 = {"ee": 0.07241363822533907, "oz": 0.11760274706258989, "on": 0.11526472437347687,
       "oo": 0.09042571111548221, "beta2": -0.3709189148473279, "dW": 0.0038830265456475475,
       "mag": -0.1147370286425415, "cB": -0.7585562856027428}
_MAGIC = (2, 8, 20, 28, 50, 82, 126, 184)

# hat basis (development notes)
_H = 0.25
_NODES = np.arange(0.0, 31.0 + 1e-9, _H)
_HATS = [(n - _H, n + _H, n) for n in _NODES]
_G = np.arange(0.02, 30.5, 0.02)


def _yn(v, src: str) -> bool:
    s = str(v).strip().lower()
    if s in ("y", "yes", "1", "on", "true"):
        return True
    if s in ("n", "no", "0", "off", "false", ""):
        return False
    raise ValueError(f"{src}={v!r}: npwindow takes y or n")


def flag(keyword=DEFAULT) -> bool:
    """The run's switch: `INCOGNITA_NPWINDOW` when set, else the deck keyword `npwindow` (default n)."""
    e = os.environ.get(ENV, "").strip()
    return _yn(e, ENV) if e else _yn(keyword, "npwindow")


@lru_cache(maxsize=1)
def anchored() -> frozenset:
    """(Z, A) with a measured l = 0 D0 > 0 for compound (Z, A) in the resonance table."""
    out = set()
    for line in _TABLE.read_text().splitlines():
        if not line or line.startswith("#") or line.startswith("Z"):
            continue
        z, a = line.split(",")[:2]
        out.add((int(z), int(a)))
    return frozenset(out)


def in_class(Z: int, A: int) -> bool:
    """Class U: no measured s-wave D0 of (Z, A) itself."""
    return (int(Z), int(A)) not in anchored()


def _state(on: bool, Z: int, A: int, k0: int) -> str:
    return f"{int(Z)},{int(A)}" if (on and int(k0) == 1 and in_class(Z, A)) else "0"


def begin(Z: int, A: int, k0: int) -> None:
    """Cascade set-up (the run's target, before anything is built for it): write the run-scoped state from
    `INCOGNITA_NPWINDOW` or the run's deck keyword (fitlib cards), else the default. A state change in the same
    process drops the per-target caches (`chartrun.drop_target_caches`), as a change of ENGADJ cards does."""
    kw = DEFAULT
    from physics.hf.input import fitlib

    c = fitlib.active()
    if c is not None:
        kw = dict(c.options).get("npwindow", DEFAULT)
    new = _state(flag(kw), Z, A, k0)
    old = os.environ.get(EFF)
    os.environ[EFF] = new
    if old is not None and old != new:
        from physics.hf import chartrun

        chartrun.drop_target_caches()


def sync(options) -> None:
    """After the run's options are resolved (Cascade): they must agree with `begin` (deck keyword / env)."""
    new = _state(flag(getattr(options, "npwindow", DEFAULT)), options.Ztarget, options.Atarget, options.k0)
    if os.environ.get(EFF) != new:
        raise RuntimeError(f"NPWINDOW: run options give {new!r}, set-up gave {os.environ.get(EFF)!r}")


def target() -> tuple | None:
    """(Z, A) of the target the rule applies to in this run (set by `begin`), None when it does not (the default)."""
    v = os.environ.get(EFF, "0").strip()
    if v in ("", "0"):
        return None
    e = os.environ.get(ENV, "").strip()
    if e and not _yn(e, ENV):   # an explicit INCOGNITA_NPWINDOW=0 wins over a state left by an earlier run in this process
        return None
    z, a = v.split(",")
    return int(z), int(a)


def applies_run() -> bool:
    return target() is not None


def token() -> tuple:
    t = target()
    return () if t is None else (("npwindow", "MX1") + t,)


def dc_rule(Z: int, A: int, ctable0: float, deltaW: float, beta2: float) -> float:
    """MS2BLIND A3 dctable of (Z, A) (the NPWINDOW record's arithmetic), rounded to 1e-4 as the NPWINDOW record."""
    N = A - Z
    cls = ("ee", "on", "oz", "oo")[(Z % 2) * 2 + (N % 2)]
    mag = math.exp(-min(min(abs(Z - m) for m in _MAGIC), min(abs(N - m) for m in _MAGIC)) / 2)
    c0 = 0.0 if abs(ctable0) < 1e-10 else ctable0
    k = _A3
    d = k[cls] + k["beta2"] * abs(beta2) + k["dW"] * deltaW + k["mag"] * mag + k["cB"] * c0
    return float(f"{d:.4f}")


def _tal(e, ea, eb, em):  # eadj._shape (tal), verbatim arithmetic
    out = np.zeros_like(e)
    npow = 4
    lo = (e > ea) & (e <= em)
    hi = (e > em) & (e < eb)
    c = ea + 0.5 * (em - ea)
    x = (e[lo] - ea) ** npow
    out[lo] = (1.0 + 0.5**npow) * x / (x + (c - ea) ** npow)
    c = em + 0.5 * (eb - em)
    x = (eb - e[hi]) ** npow
    out[hi] = (1.0 + 0.5**npow) * x / (x + (c - eb) ** npow)
    return out


@lru_cache(maxsize=1)
def _basis() -> np.ndarray:
    return np.stack([_tal(_G, *hh) for hh in _HATS], 1)


def lines(Z: int, A: int, dc: float, ecut: float, sn: float) -> list[str]:
    """The rule's `eadj ctable` lines for X = (Z, A) (shapes.py MX: least squares, text format, zero hats dropped)."""
    x = np.clip(_G - max(ecut + 2.0, sn - 6.0), 0.0, 1.0)
    s = dc * np.sqrt(sn) * (x * x * (3.0 - 2.0 * x))
    tgt = s / np.sqrt(_G)
    amp = np.linalg.lstsq(_basis(), tgt, rcond=None)[0]
    amp[np.abs(amp) < 1e-12] = 0.0
    return [f"eadj ctable {Z} {A} tal {ea:.6f} {eb:.6f} {em:.6f} {1.0 + a:.10f}"
            for (ea, eb, em), a in zip(_HATS, amp) if a != 0.0]


def inputs(ld) -> tuple:
    """(dc, Ecut, S_n) of the nucleus of ground-state LD record `ld`."""
    def f(x):
        return float(x.detach().reshape(-1)[0]) if hasattr(x, "detach") else float(x)

    nlast = int(ld.Nlast[0])
    ecut = f(ld.edis_mev[min(nlast, len(ld.edis_mev) - 1)])
    sn = f(ld.S_mev)
    dc = dc_rule(int(ld.Z), int(ld.A), f(ld.ctable[0]), f(ld.deltaW_mev[0]), f(ld.beta2[0]))
    return dc, ecut, sn


_CACHE: dict = {}
_LDC: dict = {}   # id(ld) -> (ld, key): the record is held, so its id is not recycled while cached


def bumps(ld, ibar: int = 0) -> tuple:
    """The rule's ctable bumps for LD record `ld` (ground state of the applying target), () otherwise."""
    t = target()
    if t is None or ibar != 0 or (int(ld.Z), int(ld.A)) != t:
        return ()
    hit = _LDC.get(id(ld))
    if hit is not None and hit[0] is ld:
        key = hit[1]
    else:
        key = (t,) + inputs(ld)
        if len(_LDC) > 256:
            _LDC.clear()
        _LDC[id(ld)] = (ld, key)
    b = _CACHE.get(key)
    if b is None:
        from physics.hf import eadj

        b = tuple(eadj.parse_line(x) for x in lines(t[0], t[1], *key[1:]))
        _CACHE[key] = b
    return b
