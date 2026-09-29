#!/usr/bin/env python3
"""TALYS defaults echo runs: the reference for T3 (`physics/hf/input/defaults.py`).

Adopted into T0 from T3's session-scratchpad harness (T3 commit 1d625e04) so the defaults check
is reproducible after a reboot. TALYS prints every keyword it resolved -- explicit or default --
in the ``USER INPUT FILE + DEFAULTS`` table of talys.out, and with ``partable y`` writes every
per-nucleus parameter it used to ``parameters.dat``. ``tests/hf/test_defaults.py`` compares
`Options`/`Params` against both (parsers: ``defaults.parse_talys_echo``,
``defaults.parse_partable``).

    # on a compute box (stdlib only, Python >= 3.9)
    TALYS_BIN=~/opt/talys-src/bin/talys python3 physics/hf/talys_defaults_echo.py run \\
        --out ~/hf_reference/t3_echo --workers 3
    # then copy the directory to features/hf_reference/t3_echo on the laptop

Layout per case (what test_defaults.py reads): ``<case>/talys.inp``, ``talys_head.out``
(talys.out up to ``BASIC REACTION PARAMETERS``), ``parameters.dat``, ``done.json``.

Cases: the 24 reference targets at 1 MeV (full reaction, so energy-dependent switches are
echoed) and on a two-energy grid 1 keV / 30 MeV (``reaction n``: TALYS stops after the
defaults and structure setup), plus 22 explicit-keyword cases that exercise the cascades TALYS
applies when a keyword is present rather than absent (``ldmodel 1`` on U-238 and Th-232 flips
flagparity and the E1 wtable; ``strength 8``; ``widthmode 0``; p and alpha projectiles; ...).
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

# (symbol, Z, A) -- the same 24 targets as talys_reference.REFERENCE_SET, in T3's order
TARGETS = (
    ("Ca", 20, 40), ("Fe", 26, 56), ("Co", 27, 59), ("Ni", 28, 58), ("Zr", 40, 90),
    ("Nb", 41, 93), ("Mo", 42, 98), ("Sn", 50, 120), ("I", 53, 127), ("Ba", 56, 138),
    ("Ce", 58, 140), ("Au", 79, 197), ("Pb", 82, 208), ("Bi", 83, 209), ("Nd", 60, 150),
    ("Sm", 62, 152), ("Gd", 64, 157), ("Er", 68, 166), ("W", 74, 184), ("Th", 90, 232),
    ("U", 92, 235), ("U", 92, 238), ("Pu", 94, 239), ("Am", 95, 241),
)  # fmt: skip

GRID_MEV = (0.001, 30.0)

# (case, symbol, A, projectile, energy or grid, explicit keywords, full reaction?)
OVERRIDES = (
    ("ldmodel1__U238", "U", 238, "n", 1.0, {"ldmodel": "1"}, False),
    ("strength9__U238", "U", 238, "n", 1.0, {"strength": "9"}, False),
    ("widthmode0__Fe056", "Fe", 56, "n", 1.0, {"widthmode": "0"}, False),
    ("widthflucy__Fe056", "Fe", 56, "n", 1.0, {"widthfluc": "y"}, False),
    ("preeqn__Fe056", "Fe", 56, "n", 1.0, {"preequilibrium": "n"}, False),
    ("micro__Co059", "Co", 59, "n", 1.0, {"micro": "y"}, False),
    ("proton__Ni058", "Ni", 58, "p", 5.0, {}, False),
    ("alpha__Bi209", "Bi", 209, "a", 25.0, {}, False),
    ("endf__Fe056", "Fe", 56, "n", 1.0, {"endf": "y"}, False),
    ("soukho__Pu239", "Pu", 239, "n", 1.0, {"soukho": "y"}, False),
    ("strength8__Au197", "Au", 197, "n", 1.0, {"strength": "8"}, False),
    ("ldmodel2__Zr090", "Zr", 90, "n", 1.0, {"ldmodel": "2"}, True),
    ("ldmodel5__Sm152", "Sm", 152, "n", 1.0, {"ldmodel": "5"}, False),
    ("astro__Fe056", "Fe", 56, "n", 1.0, {"astro": "y"}, False),
    ("massdis__U235", "U", 235, "n", 1.0, {"massdis": "y"}, False),
    ("colenhancey__Fe056", "Fe", 56, "n", 1.0, {"colenhance": "y"}, False),
    ("gridendf__Fe056", "Fe", 56, "n", GRID_MEV, {"endf": "y"}, False),
    ("gridwidthflucy__Fe056", "Fe", 56, "n", GRID_MEV, {"widthfluc": "y"}, False),
    ("gridproton__Ni058", "Ni", 58, "p", (0.5, 30.0), {}, False),
    ("rvadjust__Fe056", "Fe", 56, "n", 1.0, {"rvadjust": "n 1.1", "avdadjust": "p 0.9"}, True),
    (
        "alphald__Fe056", "Fe", 56, "n", 1.0,
        {"alphald": "0.08", "cglobal": "2.", "pairconstant": "11."}, True,
    ),
    ("ldmodel1__Th232", "Th", 232, "n", 1.0, {"ldmodel": "1"}, True),
)  # fmt: skip


def cases() -> list[tuple]:
    out = []
    for sym, _z, a in TARGETS:
        out.append((f"default__{sym}{a:03d}", sym, a, "n", 1.0, {}, True))
        out.append((f"grid__{sym}{a:03d}", sym, a, "n", GRID_MEV, {}, False))
    return out + list(OVERRIDES)


def input_files(case: tuple) -> tuple[str, str | None]:
    """(talys.inp, energies file or None) exactly as the T3 runs wrote them."""
    name, sym, a, proj, e, kw, reaction = case
    if isinstance(e, tuple):
        energies = "".join(f"{x:.6E}\n" for x in e)
        estr = "energies"
    else:
        energies, estr = None, str(e)
    lines = [f"projectile {proj}", f"element {sym.lower()}", f"mass {a}", f"energy {estr}"]
    lines.append("partable y")
    lines += [f"{k} {v}" for k, v in kw.items()]
    if not reaction:
        lines.append("reaction n")
    return "\n".join(lines) + "\n", energies


def run_case(case: tuple, out: Path, timeout: float) -> tuple[str, str]:
    name = case[0]
    dst = out / name
    if (dst / "done.json").exists():
        return name, "exists"
    wd = out / "_work" / name
    shutil.rmtree(wd, ignore_errors=True)
    wd.mkdir(parents=True)
    inp, energies = input_files(case)
    (wd / "talys.inp").write_text(inp)
    if energies is not None:
        (wd / "energies").write_text(energies)
    t0 = time.time()
    with open(wd / "talys.inp") as fin, open(wd / "talys.out", "w") as fo:
        try:
            rc = subprocess.run(
                [os.environ["TALYS_BIN"]],
                stdin=fin,
                stdout=fo,
                stderr=subprocess.STDOUT,
                cwd=wd,
                timeout=timeout,
            ).returncode
        except subprocess.TimeoutExpired:
            rc = -9
    dst.mkdir(parents=True, exist_ok=True)
    txt = (wd / "talys.out").read_text(errors="replace")
    cut = txt.find("########## BASIC REACTION PARAMETERS")
    (dst / "talys_head.out").write_text(txt[: cut if cut > 0 else 200000])
    banner = "The TALYS team congratulates" in txt
    if (wd / "parameters.dat").exists():
        shutil.copy(wd / "parameters.dat", dst / "parameters.dat")
    (dst / "talys.inp").write_text(inp)
    done = {
        "rc": rc,
        "banner": banner,
        "elapsed_s": round(time.time() - t0, 1),
        "reaction": case[6],
    }
    (dst / "done.json").write_text(json.dumps(done))
    shutil.rmtree(wd, ignore_errors=True)
    return name, f"rc={rc} banner={banner} {time.time() - t0:.0f}s"  # fmt: skip


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--out", required=True)
    r.add_argument("--workers", type=int, default=3)
    r.add_argument("--timeout", type=float, default=3600.0)
    sub.add_parser("list")
    a = ap.parse_args(argv)
    if a.cmd == "list":
        for c in cases():
            print(c[0])
        return
    out = Path(a.out).expanduser()
    out.mkdir(parents=True, exist_ok=True)
    cs = sorted(cases(), key=lambda c: (c[6], c[2]))  # `reaction n` cases first, light to heavy
    with ThreadPoolExecutor(a.workers) as ex:
        for name, status in ex.map(lambda c: run_case(c, out, a.timeout), cs):
            print(name, status, flush=True)
    print("ECHO_DONE", flush=True)


if __name__ == "__main__":
    main()
