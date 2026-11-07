"""PERFHF gate: the compound-nucleus speed work must not move a single bit of the production run.

Two parts:

* unit twins (always run): each compiled/memoised replacement against the code it replaced, on its own
  inputs, compared bit for bit (`np.array_equal`, NaN == NaN);
* the production gate (`slow`, `needs_data`): `scripts/talysworld/engine_grid.py` (the TALYSWORLD engine
  calculator: library v0.2 deck, environment, runner and inputs, P arm, GRIDTOP pad) on Fe-56, Zr-90, Au-197
  and U-238, at 14.1 MeV alone and on the 64-point library grid, against the golden channels written from
  origin/main 3aac5ab1 before the work started (`data/perfhf_gate.json`; rewritten at 3fe96822 + SWNAMES6, when
  engine_grid.py began to pass the library switches to this repository's engine under its INCOGNITA_* names: the
  earlier golden file was a run without them, capture off by up to 126 %). Every channel the calculator
  reports (total, elastic, nonelastic, capture, (n,p), (n,a), (n,2n), inelastic, fission) must match
  exactly: the JSON keeps each float's repr, which round-trips the double.

The production gate needs the laptop's library inputs (~/libv02/inputs, ~/talysworld_data/cc, the engine
venv); it is skipped without them.

    python tests/hf/test_perfhf_gate.py --write   # (re)write the golden file from THIS checkout
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]
GOLDEN = Path(__file__).with_name("data") / "perfhf_gate.json"
CASES = {  # (Z, A): min separation energy of the compound nucleus [MeV] (engine masses; GRIDTOP pad input)
    (26, 56): 0.0, (40, 90): 0.0, (79, 197): -0.5263641756976867, (92, 238): -4.13029517569769,
}
E1_EV = 14.1e6
GRID64 = [1000.0, 1170.2275477071134, 1369.4325134126043, 1602.5476519212207, 1875.3454087915627,
          2194.5808588339446, 2568.1589766782176, 3005.3303814001574, 3516.9204022755903, 4115.597137836078,
          4816.1851459603295, 5636.032532660582, 6595.440529492904, 7718.166196876587, 9032.010701366826,
          10569.507733924895, 12368.729115942298, 14474.22754160273, 16938.139800964524, 19821.477802002966,
          23195.639360168916, 27144.176165949066, 31764.862709208453, 37172.11739145014, 43499.83577807764,
          50904.706148241945, 59570.08944260839, 69710.55968511703, 81577.21730960486, 95463.90696098917,
          111714.49373749817, 130731.37804977443, 152985.45994355876, 179027.79962459597, 209503.26292609097,
          245166.48961063856, 286900.5799170185, 335738.96207204193, 392890.9822552964, 459771.85068085446,
          538037.6853270174, 629626.5210742472, 736806.2997280774, 862231.0292659404, 1009006.5029348617,
          1180767.2055499936, 1381766.3113637501, 1616981.0020515048, 1892235.7127197233, 2214346.3577798195,
          2591289.108038862, 3032397.8983004643, 3548595.556200364, 4152664.2755367034, 4859562.131612263,
          5686793.476206959, 6654842.383978494, 7787679.883380498, 9113357.532256398, 10664702.036350533,
          12480128.111025542, 14604589.71443603, 17090693.206793007, 20000000.000000004]
CHANNELS = ("total", "elastic", "nonelastic", "capture", "np", "na", "n2n", "inelastic", "fission")


# ---------------------------------------------------------------------------------------- unit twins

def _hump_cases():
    """Fission-path humps the way `exactfis_correction` cuts them, for the two fm6 paths the suite uses."""
    from physics.hf.fission import wkb as W

    out = []
    for Z, A in ((92, 239), (94, 240)):
        p = W.read_hfbpath(Z, A, 6)
        if p is None:
            continue
        beta = p.betafis.detach().numpy().astype(np.float64)
        v = p.vfis_mev.detach().numpy().astype(np.float64)
        mu = p.rmiufis.detach().numpy().astype(np.float64)
        ii = list(p.iiextr)
        nextr = min(p.nextr, 2 * W.NUMBAR - 1)
        for kb in range(1, nextr + 1, 2):
            a0, a1, a2 = ii[kb - 1], ii[kb], ii[kb + 1]
            lo = a0 + int(np.argmin(v[a0:a1 + 1]))
            hi = a1 + int(np.argmin(v[a1:a2 + 1]))
            if mu[lo] <= 0:
                lo += 1
            out.append((beta, v, mu, lo, hi))
    return out


def test_texact_c_is_numpy_bitwise():
    """native/nx2_texact.c's transfer loop == the numpy loop it replaced, bit for bit."""
    from physics.hf.fission import wkb as W

    if W._texact_kernel() is None:
        pytest.skip("libnx2 without nx2_fis_texact (scripts/build_nx2_native.sh)")
    cases = _hump_cases()
    if not cases:
        pytest.skip("no fm6 fission paths")
    es = np.arange(W.EXACTFIS_DE, 12.0, W.EXACTFIS_DE)
    n = 0
    for beta, v, mu, lo, hi in cases:
        ref = W._t_exact_vec_np(beta, v, mu, lo, hi, es, native=False)
        got = W._t_exact_vec_np(beta, v, mu, lo, hi, es, native=True)
        assert np.array_equal(ref, got, equal_nan=True)
        n += int(np.isfinite(ref).sum())
    assert n > 100  # the comparison saw real transmissions, not only NaN


def test_texact_memo_returns_fresh_equal_arrays():
    from physics.hf.fission import wkb as W

    cases = _hump_cases()
    if not cases:
        pytest.skip("no fm6 fission paths")
    beta, v, mu, lo, hi = cases[0]
    es = np.arange(W.EXACTFIS_DE, 9.0, W.EXACTFIS_DE)
    W._TEX_MEMO.clear()
    a = W._t_exact_vec(beta, v, mu, lo, hi, es)
    a[:] = -1.0  # a caller writing into its copy must not reach the memo
    b = W._t_exact_vec(beta, v, mu, lo, hi, es)
    ref = W._t_exact_vec_np(beta, v, mu, lo, hi, es)
    assert np.array_equal(b, ref, equal_nan=True)
    assert len(W._TEX_MEMO) == 1


# ---------------------------------------------------------------------------------------- production gate

def _python() -> str:
    eng = Path(os.environ.get("TW_ENG_PY", Path.home() / "fastgate_data/eng/16606b356d6e/.venv/bin/python"))
    return str(eng) if eng.exists() else sys.executable


def _have_inputs() -> bool:
    h = Path.home()
    return (h / "libv02/inputs/code/prodrun.py").exists() and (h / "talysworld_data/cc").is_dir()


def run_case(z: int, a: int, grid: list[float], work: Path) -> dict:
    """One engine_grid.py run of THIS checkout (TW_ENG = the repo root), as the calculator runs it."""
    gf = work / f"grid_{z}_{a}_{len(grid)}.json"
    work.mkdir(parents=True, exist_ok=True)
    gf.write_text(json.dumps(grid))
    env = {k: v for k, v in os.environ.items() if not k.startswith(("NUCLIDO_", "INCOGNITA_", "HF_"))}
    env["TW_ENG"] = str(ROOT)
    cmd = [_python(), str(ROOT / "scripts/talysworld/engine_grid.py"), "--z", str(z), "--a", str(a),
           "--grid", str(gf), "--comp", "P", "--work", str(work / f"w_{z}_{a}_{len(grid)}"),
           "--smin", repr(CASES[(z, a)])]
    p = subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=1800)
    line = [ln for ln in p.stdout.splitlines() if ln.startswith("{")]
    assert line, f"engine_grid failed: {p.stderr[-800:]}"
    out = json.loads(line[-1])
    assert not out["err"], out["err"]
    return {c: out["channels"][c] for c in CHANNELS}


def _all_cases():
    for (z, a) in CASES:
        yield z, a, "e14", [E1_EV]
        yield z, a, "g64", GRID64


@pytest.mark.slow
@pytest.mark.needs_data
@pytest.mark.parametrize("z,a,tag,grid", list(_all_cases()), ids=lambda x: str(x) if not isinstance(x, list) else "")
def test_production_channels_bit_identical(z, a, tag, grid, tmp_path):
    if not _have_inputs() or not GOLDEN.exists():
        pytest.skip("library inputs or golden file missing")
    gold = json.loads(GOLDEN.read_text())[f"{z}_{a}_{tag}"]
    got = run_case(z, a, grid, tmp_path)
    for c in CHANNELS:
        g, r = np.asarray(gold[c], dtype=np.float64), np.asarray(got[c], dtype=np.float64)
        assert np.array_equal(g, r), f"{z}-{a} {tag} {c}: max rel {np.max(np.abs(r / np.where(g == 0, 1, g) - 1)):.3e}"


if __name__ == "__main__" and "--write" in sys.argv:
    import tempfile

    sys.path.insert(0, str(ROOT))
    res = {}
    with tempfile.TemporaryDirectory() as td:
        for z, a, tag, grid in _all_cases():
            res[f"{z}_{a}_{tag}"] = run_case(z, a, grid, Path(td))
            print(z, a, tag, "capture", res[f"{z}_{a}_{tag}"]["capture"][:2], flush=True)
    GOLDEN.write_text(json.dumps(res, indent=0) + "\n")
    print("wrote", GOLDEN)
