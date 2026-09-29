"""Residual-production cross sections from a TALYS run, resolved by isomeric state.

A producer asks "how much 99mTc", not "how big is (p,2n)". Activation measurements report the
same thing: the production cross section of one nuclide, or of one of its long-lived states,
summed over every reaction channel that makes it. TALYS writes exactly that when
``fileresidual y`` is set:

* ``rpZZZAAA.tot``  -- production of the nuclide, all states;
* ``rpZZZAAA.Lnn``  -- production of level ``nn`` for each *isomer* TALYS tracks.

``nn`` is the LEVEL NUMBER in the discrete-level file, not the isomer index: 99mTc is
``rp043099.L02`` because the 142.7 keV isomer is level 2. The header carries ``isomer:`` (0 for
the ground state, 1 for the first isomer, ...) and the half-life, and those -- not the file
suffix -- decide the state label. Reading ``L01`` as "the isomer" would hand 99mTc's value to
whatever sits at level 1, which for Tc-99 is a 140.5 keV level with a picosecond lifetime.

State labels follow EXFOR's residual-state suffixes so the two sides join on a string:
``""`` (all states, the .tot file), ``"G"``, ``"M"``, ``"M2"``.
"""
from __future__ import annotations

import re
from pathlib import Path

import numpy as np

from physics.talys.runner import parse_yandf

_RP = re.compile(r"^rp(\d{3})(\d{3})\.(tot|L(\d{2}))$")


def _meta_block(path: Path) -> dict[str, str]:
    """Nested YANDF header keys flattened with their parent: ``level.isomer`` etc."""
    out: dict[str, str] = {}
    stack: list[tuple[int, str]] = []
    with open(path) as fh:
        for line in fh:
            if not line.startswith("#") or line.startswith("##"):
                if not line.startswith("#"):
                    break
                continue
            body = line[1:]
            indent = len(body) - len(body.lstrip(" "))
            s = body.strip()
            if ":" not in s:
                continue
            k, _, v = s.partition(":")
            k, v = k.strip(), v.strip()
            while stack and stack[-1][0] >= indent:
                stack.pop()
            if v:
                out[".".join([p for _, p in stack] + [k])] = v
            else:
                stack.append((indent, k))
    return out


def state_label(isomer: int) -> str:
    return "G" if isomer == 0 else ("M" if isomer == 1 else f"M{isomer}")


def read_residuals(workdir: str | Path) -> list[dict]:
    """Every residual-production table in a TALYS work directory.

    Returns dicts with ``product_z, product_a, state, level, half_life_s, E_mev, xs_mb``.
    ``state == ""`` is the all-states total. Tables that are identically zero are kept: a
    product the calculation says is not made is information, and dropping it would make a
    zero look like a missing run.
    """
    wd = Path(workdir)
    out: list[dict] = []
    for p in sorted(wd.glob("rp*")):
        m = _RP.match(p.name)
        if not m:
            continue
        z, a = int(m.group(1)), int(m.group(2))
        parsed = parse_yandf(p)
        d = parsed["data"]
        if d.size == 0:
            continue
        meta = _meta_block(p)
        if m.group(3) == "tot":
            state, level, hl = "", -1, float("nan")
        else:
            def pick(suffix: str) -> str | None:
                # `parameters:` is a sibling of `residual:` under `reaction:`, not its child,
                # so match on the tail rather than hard-coding the nesting.
                hits = [v for k, v in meta.items() if k.endswith(suffix)]
                return hits[0] if hits else None

            iso = pick("level.isomer")
            if iso is None:
                raise ValueError(f"{p}: no isomer number in header; refusing to guess the state")
            level = int(m.group(4))
            num = pick("level.number")
            if num is not None and int(num) != level:
                raise ValueError(f"{p}: file level {level} != header level {num}")
            state = state_label(int(iso))
            try:
                hl = float(pick("level.half-life [sec]") or "nan")
            except ValueError:
                hl = float("nan")
        out.append({
            "product_z": z, "product_a": a, "state": state, "level": level,
            "half_life_s": hl,
            "E_mev": np.asarray(d[:, 0], float),
            "xs_mb": np.asarray(d[:, 1], float),
        })
    return out
