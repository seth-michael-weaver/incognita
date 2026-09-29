"""COREX: the per-call speed paths of the shared utilities against the paths they stand in for.

Bit-identical where the operations did not change (the fixed-format readers, the grids, the
masses grid, the memos); to a stated relative tolerance where they did (numpy/float paths of
`particle_hole._sum_terms`, `ignatyuk`, `spincut`; the arm64 Numerov kernels).
"""

from __future__ import annotations

import os
import platform
import random
from pathlib import Path

import numpy as np
import pytest
import torch
from torch import Tensor

from physics.hf.core import grids as G
from physics.hf.structure import files as F

STRUCTURE = Path(os.environ.get("TALYS_DIR", Path.home() / "opt/talys-src")) / "structure"
needs_db = pytest.mark.skipif(not STRUCTURE.is_dir(), reason="TALYS structure database absent")
ARM64 = platform.machine().lower() in ("arm64", "aarch64")


# ------------------------------------------------------------------------------ fortran_read


def _fortran_read_c8035ee2(line: str, fmt: str) -> list:
    """`files.fortran_read` as it was at c8035ee2 (MACSPEED), the reference."""
    width, plan = F._read_plan(fmt)
    rec = line.rstrip("\n").ljust(width)
    vals: list = []
    for kind, a, b, d in plan:
        field = rec[a:b]
        if kind == "a":
            vals.append(field)
        elif kind == "i":
            s = field.replace(" ", "")
            vals.append(int(s) if s not in ("", "+", "-") else 0)
        else:
            s = field.replace(" ", "")
            if "." in s and s.isascii() and s.lstrip("+-").replace(".", "", 1).isdigit() \
                    and "+" not in s[1:] and "-" not in s[1:]:
                vals.append(float(s))
            else:
                vals.append(F._real(field, d))
    return vals


def _same(a, b) -> bool:
    if isinstance(a, float) and isinstance(b, float):
        return (a == b and np.signbit(a) == np.signbit(b)) or (a != a and b != b)
    return type(a) is type(b) and a == b


def _outcome(fn, line, fmt):
    try:
        return ("ok", fn(line, fmt))
    except (ValueError, IndexError) as exc:
        return ("err", type(exc).__name__)


def test_fortran_read_fuzz_matches_c8035ee2():
    rng = random.Random(20260914)
    alphabet = "0123456789  .+-eEdD_niNI\t\xa0"
    fmts = ["(f11.6)", "(e10.3)", "(i5)", "(es15.6)", "(f9.5)", "(i3)", "(f4.1)"]
    for _ in range(60000):
        fmt = rng.choice(fmts)
        width = F._read_plan(fmt)[0]
        k = rng.random()
        if k < 0.4:  # numbers as the structure files print them
            x = rng.uniform(-1e4, 1e4) * 10 ** rng.randint(-8, 3)
            s = rng.choice([f"{x:.6f}", f"{x:.3E}", f"{x:.4e}", f"{int(x)}", f"{x:.1f}"])
        else:
            s = "".join(rng.choice(alphabet) for _ in range(rng.randint(0, width)))
        line = s.rjust(width)[:width] if rng.random() < 0.7 else s[:width]
        got, ref = _outcome(F.fortran_read, line, fmt), _outcome(_fortran_read_c8035ee2, line, fmt)
        assert got[0] == ref[0], (line, fmt, got, ref)
        if got[0] == "ok":
            assert all(_same(a, b) for a, b in zip(got[1], ref[1], strict=True)), (line, fmt)


@needs_db
@pytest.mark.parametrize("sym", ["Ge", "Lu", "U", "Fe"])
def test_fortran_read_real_files_match_c8035ee2(sym):
    fmts = {"levels/final": ["(4x, i4, 2i5)", "(4x, f11.6, f6.1, 3x, i2, i3, 18x, e10.3, 3a1, a18)",
                             "(29x, i3, f10.6, e10.3, 5x, a1)"],
            "masses/hfb": ["(4x, i4, 2f12.6, 2f8.4, 20x, f4.1, i2)"]}
    ext = {"levels/final": "lev", "masses/hfb": "mass"}
    for sub, fl in fmts.items():
        path = STRUCTURE / sub / f"{sym}.{ext[sub]}"
        lines = F._lines(str(path))
        for line in lines[:: max(1, len(lines) // 4000)]:
            for fmt in fl:
                got = _outcome(F.fortran_read, line, fmt)
                ref = _outcome(_fortran_read_c8035ee2, line, fmt)
                assert got[0] == ref[0]
                if got[0] == "ok":
                    assert all(_same(a, b) for a, b in zip(got[1], ref[1], strict=True))


def test_psf_fields_match_the_blank_aware_read():
    from physics.hf.gamma.parameters import _fortran_fields

    full = f"{1.0:9.3f}" + "".join(f"{v:12.3E}" for v in (0.1234, 2.0, -2.5e-3))
    blank = f"{1.0:9.3f}" + f"{0.1234:12.3E}" + " " * 12 + f"{3.0:12.3E}"
    for line in [full, blank, full[:21], full[:33]]:
        ref = []
        for k in range(3):
            s = line[9 + 12 * k: 21 + 12 * k].strip()
            ref.append(float(s) if s else 0.0)
        assert _fortran_fields(line, 12, 9, 3) == ref


# ------------------------------------------------------------------------------------ grids


def _emission_end_loop(egrid, maxen, etotal_mev, s_type_mev, ebegin, parskip):
    f32, f64 = np.float32, np.float64
    eend, high, etot = {}, 0, f32(etotal_mev)
    for t in range(7):
        eend[t] = maxen - 1
        if parskip.get(t, False):
            continue
        lim = f64(etot) - f64(s_type_mev[t])
        for k in range(maxen + 1):
            if f64(f32(egrid[k])) > lim:
                eend[t] = k
                break
        if eend[t] > ebegin[t]:
            eend[t] = max(eend[t], ebegin[t] + 3)
        high = max(high, eend[t])
    return eend, high


def test_emission_end_and_eoutdis_match_the_loops():
    rng = np.random.default_rng(3)
    eg, maxen = G.egrid_values(35.0)
    for _ in range(200):
        et = float(rng.uniform(0.0, 40.0))
        s = {t: float(rng.uniform(-5.0, 15.0)) for t in range(7)}
        eb = {t: int(rng.integers(0, 40)) for t in range(7)}
        ps = {t: bool(rng.random() < 0.2) for t in range(7)}
        want = _emission_end_loop(eg, maxen, et, s, eb, ps)
        assert G.emission_end(eg, maxen, et, s, eb, ps) == want
        ed = {t: np.sort(rng.uniform(0.0, 6.0, 30)) for t in range(7)}
        eend, _ = G.emission_end(eg, maxen, et, s, eb, ps)
        _, eout = G.discrete_emission_begin(eg, et, s, ed, {t: 10 for t in range(7)}, eb, eend, ps)
        f32, f64 = np.float32, np.float64
        for t, v in eout.items():
            ref = np.array([f32(f64(f32(et)) - f64(s[t]) - f64(x))
                            for x in np.asarray(ed[t], dtype=f32)], f32).astype(f64)
            assert np.array_equal(v, ref)


def test_egrid_values_hands_out_copies():
    a, m = G.egrid_values(30.0)
    a[:] = -1.0
    b, m2 = G.egrid_values(30.0)
    assert m == m2 and b[1] == np.float32(0.001)


# ---------------------------------------------------------------------------- particle-hole


@pytest.mark.parametrize("seed", range(6))
def test_sum_terms_numpy_path_matches_torch(seed):
    from physics.hf.density import particle_hole as ph

    g = torch.Generator().manual_seed(seed)
    ee = torch.rand(4, 1, 7, 30, generator=g, dtype=torch.float64) * 40.0 - 2.0
    ew = torch.rand(9, 4, 21, 7, 1, generator=g, dtype=torch.float64) * 12.0 + 0.5
    h = torch.randint(0, 6, (1, 21, 1, 1), generator=g)
    nm1 = (torch.randint(-3, 11, (1, 21, 7, 1), generator=g)).to(torch.float64)
    hmax = int(h.max())
    ew_g = ew.clone().requires_grad_(True)  # a leaf asking for a graph takes the torch path
    ref_g = ph._sum_terms(ee, ew_g, h, nm1, hmax)
    assert ref_g.requires_grad
    ref = ref_g.detach()
    got = ph._sum_terms(ee, ew, h, nm1, hmax)  # no graph: the numpy path
    assert got.shape == ref.shape
    assert float((got - ref).abs().max()) <= 1e-12 * max(1.0, float(ref.abs().max()))


# ------------------------------------------------------------------------- level densities


@needs_db
@pytest.mark.parametrize("Z,A", [(32, 68), (71, 176), (92, 239), (26, 55)])
def test_ignatyuk_spincut_float_paths_match_tensor_paths(Z, A):
    from physics.hf.compound.dens_reference import _ld_of
    from physics.hf.density import parameters as P

    ld = _ld_of(Z, A, Z, A - 1, None, None)[0]
    for ibar in range(len(ld.delta_mev)):
        for e in (-1.0, 0.0, 0.3, 1.7, float(ld.Exmatch_mev[ibar]), 5.0, 12.5, 40.0):
            ref_a = P.ignatyuk(ld, torch.tensor([e], dtype=torch.float64), ibar)[0]
            ref_s = P.spincut(ld, ref_a.reshape(1), torch.tensor([e], dtype=torch.float64),
                              ibar)[0]
            with torch.inference_mode():
                got_a = P.ignatyuk(ld, torch.tensor(e, dtype=torch.float64), ibar)
                got_s = P.spincut(ld, got_a, e, ibar)
            assert got_a.dim() == 0 and got_s.dim() == 0
            for g_, r_ in ((got_a, ref_a), (got_s, ref_s)):
                assert abs(float(g_) - float(r_)) <= 1e-13 * max(1.0, abs(float(r_))), (e, ibar)


# ------------------------------------------------------------------------ structure memos


@needs_db
def test_masses_grid_matches_duflo_per_cell():
    from physics.hf.input.defaults import default_options
    from physics.hf.structure import masses as M

    o = default_options(40, 90)
    m = M.masses(o)
    dum = m.dumexc_mev.numpy()
    for Zix in range(o.maxZ + 5):
        for Nix in range(o.maxN + 5):
            Z, N = o.Zinit - Zix, o.Ninit - Nix
            want = M.duflo(N, Z) if (Z > 0 and N > 0 and m.flagduflo) else 0.0
            assert dum[Zix, Nix] == want


@needs_db
def test_levels_by_value_do_not_depend_on_the_target():
    from physics.hf.chartrun import drop_target_caches
    from physics.hf.input.defaults import default_options
    from physics.hf.structure import levels as L
    from physics.hf.structure.masses import masses

    o1, o2 = default_options(32, 68), default_options(32, 70)
    L._levels_of_values.cache_clear()
    L._LEVELS_CACHE.clear()
    a = L.discrete_levels(32, 67, o1, masses(o1))
    L._levels_of_values.cache_clear()
    b = L.discrete_levels(32, 67, o2, masses(o2))
    for f in ("e_mev", "spin", "parity", "half_life_s", "branch_to", "branch_ratio", "conversion",
              "all_e_mev", "all_spin", "all_parity", "all_half_life_s"):
        assert torch.equal(getattr(a, f), getattr(b, f)), f
    assert (a.nlev, a.nlevmax2, a.assign, a.Lisomer) == (b.nlev, b.nlevmax2, b.assign, b.Lisomer)
    drop_target_caches()
    assert L._levels_of_values.cache_info().currsize >= 1  # kept between targets


@needs_db
def test_level_block_is_the_raw_records_parsed():
    from physics.hf.structure import levels as L

    nnn, records = F.read_level_file(26, 56, 1)
    _, _, main, rest = L._level_block(26, 56, 1)
    pos = 0
    for lev in main:
        v = F.fortran_read(records[pos], L._LEVEL_FMT)
        assert lev[:4] == (L._f32(v[0]), L._f32(v[1]), v[2], L._f32(v[4]))
        pos += 1 + v[3]
        assert len(lev[8]) == v[3]
    assert len(rest[0]) == max(min(nnn, L.NUMLEV2) - min(nnn, L.NUMLEV), 0)


# --------------------------------------------------------------------------- arm64 kernels


@pytest.mark.skipif(not ARM64, reason="the NEON Numerov lanes are arm64 only (x86 keeps its bits)")
def test_numerov_inward_neon_matches_python_loop(monkeypatch):
    from physics.hf import native
    from physics.hf.omp import schrodinger as S

    if not native.available():
        pytest.skip("libhfnative not built")
    rng = np.random.default_rng(7)
    m = 37
    ee = rng.uniform(0.1, 30.0, m)
    ra = rng.uniform(5.0, 12.0, m)
    rb = ra + rng.uniform(200.0, 900.0, m)
    gb = rng.uniform(0.5, 1.5, m)
    gb1 = gb * rng.uniform(0.95, 1.05, m)
    n = np.where(np.arange(m) < 24, 4000, 1500).astype(np.int64)
    got = S._numerov_inward_many(ee, ra, rb, gb, gb1, n)
    monkeypatch.setattr(S._native, "available", lambda: False)
    ref = S._numerov_inward_many(ee, ra, rb, gb, gb1, n)
    for g_, r_ in zip(got, ref, strict=True):
        assert np.allclose(g_, r_, rtol=1e-9, atol=0.0)


@pytest.mark.skipif(not ARM64, reason="the interleaved DWBA rows are arm64 only")
@pytest.mark.parametrize("nk,nlj,n", [(1, 43, 356), (31, 55, 60), (3, 1, 40), (136, 57, 25)])
def test_dwba_numerov_arm64_matches_torch_loop(nk, nlj, n, monkeypatch):
    from physics.hf.ecis import dwba
    from physics.hf.native import speedw

    if not speedw.available():
        pytest.skip("libspeedw not built")
    g = torch.Generator().manual_seed(nk * 1000 + nlj * 10 + n)
    f = torch.complex(torch.randn(nlj, n + 1, generator=g, dtype=torch.float64) * 0.05 - 0.3,
                      torch.randn(nlj, n + 1, generator=g, dtype=torch.float64) * 0.02)
    kappa2 = torch.rand(nk, generator=g, dtype=torch.float64) * 2.0 - 0.3
    ls = torch.randint(0, 9, (nlj,), generator=g)
    h = 0.0666304755902749
    torch.set_num_threads(1)
    got = speedw.dwba_numerov(f, kappa2, ls, h, n)
    monkeypatch.setattr(speedw, "available", lambda: False)
    ref = dwba.distorted_waves(f, kappa2, ls, h, n)
    scale = ref.abs().clamp(min=1e-300)
    rel = ((got - ref).abs() / scale)[ref.abs() > 0]
    assert float(rel.max()) <= 1e-8


def test_mass10_many_matches_the_scalar_mass10():
    from physics.hf.structure import masses as M

    nx, nz = np.meshgrid(np.arange(1, 200), np.arange(1, 130), indexing="ij")
    nx, nz = nx.ravel(), nz.ravel()
    got = M._mass10_many(nx, nz)
    ref = np.array([M._mass10(int(a), int(b)) for a, b in zip(nx, nz, strict=True)], M._F)
    assert got.dtype == ref.dtype
    # Vectorised float32 maths may use different SIMD/FMA paths than the scalar loop depending on the
    # CPU (CI runners vary). ULP counts blow up for values near zero, so compare in absolute terms:
    # 1 keV is far below any physical use of these masses.
    bad = ~np.isclose(got, ref, rtol=1e-6, atol=1e-3)
    worst = np.argsort(-np.abs(got - ref))[:5]
    detail = "; ".join(f"N={nx[i]} Z={nz[i]} got={got[i]:.6g} ref={ref[i]:.6g}" for i in worst)
    assert not bad.any(), f"{int(bad.sum())} cells differ; worst: {detail}"


def _residual_exmax_loop(zcomp, ncomp, exmax0, exmax, sep_mev, parskip):
    from physics.hf.core.constants import PARN, PARZ

    f32, f64 = np.float32, np.float64
    e0, em = exmax0.astype(f32).copy(), exmax.astype(f32).copy()
    zdeep, ndeep = zcomp, ncomp
    for t in range(1, 7):
        if not parskip.get(t, False):
            zdeep, ndeep = max(zdeep, zcomp + PARZ[t]), max(ndeep, ncomp + PARN[t])
    for zix in range(zcomp, zdeep + 1):
        for nix in range(ndeep + 1):
            if (zix == zcomp and nix == ncomp) or em[zix, nix] != f32(0.0):
                continue
            for t in range(1, 7):
                zm, nm = zix - PARZ[t], nix - PARN[t]
                if parskip.get(t, False) or zm < 0 or nm < 0:
                    continue
                e0[zix, nix] = f32(f64(e0[zm, nm]) - f64(sep_mev[zm, nm, t]))
                em[zix, nix] = max(e0[zix, nix], f32(0.0))
    return e0, em


def test_residual_exmax_matches_the_loop():
    rng = np.random.default_rng(11)
    for _ in range(50):
        e0 = np.zeros((10, 12), np.float32)
        em = np.zeros((10, 12), np.float32)
        zc, nc = int(rng.integers(0, 4)), int(rng.integers(0, 4))
        e0[zc, nc] = em[zc, nc] = np.float32(rng.uniform(5, 30))
        em[rng.random((10, 12)) < 0.1] = np.float32(1.5)
        sep = rng.uniform(-3.0, 12.0, (10, 12, 7))
        ps = {t: bool(rng.random() < 0.2) for t in range(7)}
        got = G.residual_exmax(zc, nc, e0, em, sep, ps)
        ref = _residual_exmax_loop(zc, nc, e0, em, sep, ps)
        assert all(np.array_equal(g, r) and g.dtype == r.dtype
                   for g, r in zip(got, ref, strict=True))


def test_default_params_memo_hands_out_independent_copies():
    from physics.hf.input.defaults import _default_params_build, default_options, default_params

    o = default_options(26, 56)
    a = default_params(26, 56, o)
    for t in a.values.values():
        t.fill_(-7.0)
    b = default_params(26, 56, default_options(26, 56))
    ref = _default_params_build(26, 56, o, None, None)
    assert set(b.values) == set(ref)
    assert all(torch.equal(b.values[k], ref[k]) for k in ref)


@needs_db
def test_masses_memo_follows_the_param_grids():
    from physics.hf.input.defaults import default_options, default_params
    from physics.hf.structure import masses as M

    o = default_options(40, 90)
    p = default_params(40, 90, o)
    m1 = M.masses(o, p)
    assert M.masses(default_options(40, 90), default_params(40, 90, o)) is m1
    q = default_params(40, 90, o)
    q.values["beta2"][1, 1] = 0.123
    m2 = M.masses(o, q)
    assert m2 is not m1 and not torch.equal(m2.beta2, m1.beta2)


def _fixture_cases():
    z = np.load(Path(__file__).parent / "fixtures" / "finitewell_speed2.npz")
    for j in range(int(z["n"])):
        surf = z[f"c{j}_surf"]
        surf = bool(surf) if bool(z[f"c{j}_surf_is_bool"]) else torch.from_numpy(surf)
        yield (torch.from_numpy(z[f"c{j}_p"]), torch.from_numpy(z[f"c{j}_h"]),
               torch.from_numpy(z[f"c{j}_eex"]), torch.from_numpy(z[f"c{j}_ewell"]), surf)


def _close(got: Tensor, ref: Tensor, rel: float = 1e-12, floor: float = 1e-12) -> bool:
    got, ref = got.numpy(), ref.numpy()
    den = np.maximum(np.abs(ref), np.abs(got))
    return got.shape == ref.shape and bool(
        (np.abs(ref - got) <= rel * np.where(den > floor, den, 1.0)).all())


def test_finitewell_numpy_path_matches_torch_on_the_speed2_fixture():
    from physics.hf.density.particle_hole import finitewell

    for args in _fixture_cases():
        ref = finitewell(*args)  # grad mode on: the torch path
        with torch.inference_mode():
            got = finitewell(*args)
        assert _close(got, ref)


@pytest.mark.parametrize("seed", range(4))
def test_phdens2_numpy_path_matches_torch(seed):
    from physics.hf.density.particle_hole import phdens2

    g = torch.Generator().manual_seed(100 + seed)
    shp = (5, 7)
    ppi, hpi, pnu, hnu = (torch.randint(-1, 5, shp, generator=g) for _ in range(4))
    gsp = torch.rand(5, 1, generator=g, dtype=torch.float64) * 3 + 1
    gsn = torch.rand(5, 1, generator=g, dtype=torch.float64) * 3 + 1
    ex = torch.rand(5, 1, generator=g, dtype=torch.float64) * 60 - 2
    ew = torch.rand(5, 1, generator=g, dtype=torch.float64) * 40 + 1
    surf = torch.rand(shp, generator=g) < 0.5
    for kw in ({}, {"gsp_pauli": gsp * 1.1, "gsn_pauli": gsn * 0.9},
               {"ap2": torch.rand(shp, generator=g, dtype=torch.float64)}):
        for sw in (False, surf):
            ref = phdens2(ppi, hpi, pnu, hnu, gsp, gsn, ex, ew, sw, **kw)
            with torch.inference_mode():
                got = phdens2(ppi, hpi, pnu, hnu, gsp, gsn, ex, ew, sw, **kw)
            # inference_mode selects a different torch dispatch path for the same Python function
            # (no different physics); measured on this Mac (MACFIX2) up to 2.2e-11 relative at
            # seed=3, just over the old 1e-11 bound. Ordinary FP noise -- relaxed to the project
            # standard (project standard: no bit-identity anywhere, <=1e-6 relative).
            assert _close(got, ref, rel=1e-6, floor=1e-9)


def test_integrated_density_numpy_path_matches_torch():
    g = torch.Generator().manual_seed(5)
    r1, r2, r3 = (torch.rand(12, 41, generator=g, dtype=torch.float64) * 1e3 for _ in range(3))
    r2[0, :5] = 0.0
    r3[1, :3] = r2[1, :3]
    dex = torch.rand(12, 1, generator=g, dtype=torch.float64)
    ref = G.integrated_density(r1, r2, r3, dex)
    with torch.inference_mode():
        got = G.integrated_density(r1, r2, r3, dex)
    assert torch.allclose(got, ref, rtol=1e-14, atol=0.0)


def test_lazy_lines_are_the_split_lines(tmp_path):
    cases = [b"a\nb\n\nc", b"a\nb\n", b"", b"\n", b"x\r\ny\n", b"one\x85two\n", b"caf\xe9\nz"]
    for k, data in enumerate(cases):
        f = tmp_path / f"c{k}.txt"
        f.write_bytes(data)
        for enc in ("latin-1", "utf-8"):
            try:
                ref = tuple(data.decode(enc).splitlines())
            except UnicodeDecodeError:
                continue
            got = F.lazy_lines(str(f), encoding=enc)
            assert len(got) == len(ref) and tuple(got[i] for i in range(len(got))) == ref
            assert tuple(got[1:3]) == ref[1:3] and (not ref or got[-1] == ref[-1])


@needs_db
def test_level_file_blocks_unchanged_by_lazy_lines():
    for sym, Z in (("Ge", 32), ("U", 92)):
        lines = F._lines(str(STRUCTURE / "levels" / "final" / f"{sym}.lev"))
        lazy = F._lazy_lines(str(STRUCTURE / "levels" / "final" / f"{sym}.lev"))
        assert len(lazy) == len(lines)
        for A in (Z + 30, Z + 40, 2 * Z + 20, 250):
            assert F.read_level_file(Z, A, 1) == _read_level_file_split(lines, A)


def _read_level_file_split(lines, A):
    i = 0
    while i < len(lines):
        ia, nlevlines, nnn = F.fortran_read(lines[i], "(4x, i4, 2i5)")
        if ia == A:
            return nnn, lines[i + 1 : i + 1 + nlevlines]
        i += 1 + nlevlines
    return 0, ()
