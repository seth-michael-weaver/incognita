"""Pure-Python parts of scripts/bench_vs_talys.py (the timed runs need TALYS and are not tested)."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_PATH = Path(__file__).resolve().parents[1] / "scripts/bench_vs_talys.py"
_spec = importlib.util.spec_from_file_location("bench_vs_talys", _PATH)
bench = importlib.util.module_from_spec(_spec)
sys.modules["bench_vs_talys"] = bench
_spec.loader.exec_module(bench)


def test_parse_nuclides():
    assert bench.parse_nuclide("U-238") == (92, 238)
    assert bench.parse_nuclide("fe56") == (26, 56)
    assert bench.parse_nuclide("79-197") == (79, 197)
    assert bench.parse_nuclides("Fe-56, Dy-163") == [(26, 56), (66, 163)]
    mix = bench.parse_nuclides("mix12")
    assert len(mix) == 12 and (92, 238) in mix


def test_cli_defaults_and_arm_order():
    a = bench.build_parser().parse_args(["--talys", "t", "--talys-structure", "s", "--cpus", "3"])
    assert a.nuclides == "mix12" and a.energies == "grid64" and a.repeats == 3 and a.cpus == "3"
    assert bench.arm_order(0) == ("talys", "nocache", "cold", "warm")
    assert bench.arm_order(1) == ("warm", "cold", "nocache", "talys")


def test_energy_grid():
    e = bench.energies_mev("grid64")
    assert len(e) == 64 and abs(e[0] - 1e-3) < 1e-9 and abs(e[-1] - 20.0) < 1e-5
    assert all(b > a for a, b in zip(e, e[1:]))


def test_parity_and_tables():
    eng = {o: [1.0, 2.0, 1e-9] for o in bench.OBSERVABLES}
    tal = {o: [1.0, 2.0 * 10 ** 0.001, 1e-9] for o in bench.OBSERVABLES}
    p = bench.parity_stats(eng, tal)
    assert p["total"]["n"] == 2 and p["total"]["skipped"] == 1
    assert abs(p["total"]["max"] - 0.001) < 1e-12

    nd = [{"nuclide": "Fe-56", "Z": 26, "A": 56, "colltype": "S", "class": "spherical"}]
    runs = [{"nuclide": "Fe-56", "arm": "talys", "ok": True, "cpu_s": 10.0},
            {"nuclide": "Fe-56", "arm": "nocache", "ok": True, "cpu_s": 2.0, "compute_cpu_s": 1.0,
             "parity_abs_log10": {"total": [0.0, 0.001]}},
            {"nuclide": "Fe-56", "arm": "cold", "ok": True, "cpu_s": 2.0, "compute_cpu_s": 1.0},
            {"nuclide": "Fe-56", "arm": "warm", "ok": True, "cpu_s": 1.5, "compute_cpu_s": 0.5}]
    s = bench.summarize(runs, nd)
    assert s["classes"]["all"]["speedup"]["nocache_compute"] == 10.0
    assert s["classes"]["all"]["speedup"]["warm"] == 10.0 / 1.5
    md = bench.markdown_tables(s)
    assert "| Fe-56 | spherical | 10.00 |" in md and "10.0x / 5.0x" in md
