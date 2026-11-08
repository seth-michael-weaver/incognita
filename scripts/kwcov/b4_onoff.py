#!/usr/bin/env python3
"""KWCOV B4: every Results array with the SPECOBS switches on vs off (output only), on any target.

    python scripts/kwcov/b4_onoff.py --z 92 --a 238 [--e 1,5,14] [--kw "outspectra y;ddxmode 3;outgamdis y"]
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))


def main():
    import b4_compare as B

    ap = argparse.ArgumentParser()
    ap.add_argument("--z", type=int, required=True)
    ap.add_argument("--a", type=int, required=True)
    ap.add_argument("--e", default="1,5,14")
    ap.add_argument("--kw", default="")
    a = ap.parse_args()
    E = [float(np.float32(float(x))) for x in a.e.split(",")]
    if not a.kw:
        os.environ["INCOGNITA_SPECOBS"] = "1"
    res, on = B.engine_run(a.z, a.a, E, a.kw or None)
    os.environ.pop("INCOGNITA_SPECOBS", None)
    _, off = B.engine_run(a.z, a.a, E, None)
    bad = [k for k in off if k not in on or not np.array_equal(off[k], on[k], equal_nan=True)]
    bad += [k for k in on if k not in off]
    worst = max((float(np.nanmax(np.abs(on[k] - off[k]) / np.maximum(np.abs(off[k]), 1e-300))) for k in bad
                 if k in on and k in off and on[k].shape == off[k].shape), default=0.0)
    print(f"on/off: {len(off)} arrays, {len(bad)} differ (worst rel {worst:.3g}): {bad[:10]}")
    print(f"spectra arrays: {len(res.spectra)}; e.g. {sorted(res.spectra)[:8]}")
    from physics.hf import specobs

    print("approx:", specobs.META.get("approx", [])[:10])


if __name__ == "__main__":
    main()
