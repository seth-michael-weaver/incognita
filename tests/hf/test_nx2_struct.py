"""NATIVEX2 lever `struct`: the structure set-up paths against the forms they replace, bit for bit --
the compiled level-block reader against the Python format readers (and its fallback on every
non-plain field form), the shared default-parameter templates against a fresh build, the dense
mass-table gather and the per-cell Duflo memo against the per-element loop and the scalar
formula, and `lazy_lines`' control-byte check against `str.splitlines`."""

from __future__ import annotations

import os
from pathlib import Path

import numpy as np
import pytest
import torch

from physics.hf.structure import files as F

STRUCTURE = Path(os.environ.get("TALYS_DIR", Path.home() / "opt/talys-src")) / "structure"
needs_db = pytest.mark.skipif(not STRUCTURE.is_dir(), reason="TALYS structure database absent")


def _same(a, b) -> bool:
    if type(a) is not type(b):
        return False
    if isinstance(a, np.ndarray):
        return a.dtype == b.dtype and a.shape == b.shape and a.tobytes() == b.tobytes()
    if isinstance(a, (tuple, list)):
        return len(a) == len(b) and all(_same(x, y) for x, y in zip(a, b, strict=True))
    if isinstance(a, float):
        return np.float64(a).tobytes() == np.float64(b).tobytes()
    return a == b


def _nx2_built() -> bool:
    from physics.hf.native import nx2

    # not `nx2.kernel` with a signature of its own: that would rebind the shared ctypes function
    so = nx2.lib()
    return (so is not None and hasattr(so, "nx2_struct_levels")
            and os.environ.get("HF_NX2_STRUCT", "1") != "0")


# ---------------------------------------------------------------------------- level blocks


@needs_db
@pytest.mark.parametrize("d", [1, 2, 3])
def test_compiled_level_blocks_are_the_python_reads(d):
    """Every block of a spread of element files, isomers and actinides included."""
    if not _nx2_built():
        pytest.skip("no libnx2 build")
    from physics.hf.core.constants import nuclide_symbol
    from physics.hf.structure import levels as L

    n = 0
    for Z in (1, 8, 20, 26, 40, 50, 63, 72, 77, 82, 90, 92, 95, 100):
        path = STRUCTURE / "levels" / {1: "final", 2: "exp", 3: "hfb"}[d] / f"{nuclide_symbol(Z)}.lev"
        if not path.is_file():
            continue
        for A in sorted(F._level_headers(str(path))):
            nnn, recs = F.level_records(Z, A, d)
            if not (nnn or recs):
                continue
            got = L._level_block_nx2(nnn, recs)
            assert got is not None, (Z, A, d)
            assert _same(got, L._level_block_py(nnn, recs)), (Z, A, d)
            n += 1
    assert n > 100


def _records(tmp_path, lines: list[str]):
    f = tmp_path / "x.lev"
    f.write_bytes(("\n".join(lines) + "\n").encode("latin-1"))
    lz = F.lazy_lines(str(f))
    assert isinstance(lz, F.LazyLines)
    return F.LevelRecords(lz, 0, len(lz))


_LEV0 = "   0   0.000000   0.0    1  0                   2.500E-03 JP             HFB  "
_LEV1 = "   1   1.812362   1.5   -1  1                            EJP   level density  "
_BR = "                               0  1.000000 0.000E+00     B"
_LEV2 = "   2   2.124690   2.5    1  0"


def test_compiled_level_block_plain_synthetic_and_fallbacks(tmp_path):
    if not _nx2_built():
        pytest.skip("no libnx2 build")
    from physics.hf.structure import levels as L

    plain = [_LEV0, _LEV1, _BR, _LEV2]
    recs = _records(tmp_path, plain)
    got = L._level_block_nx2(2, recs)
    assert got is not None and _same(got, L._level_block_py(2, recs))
    # short records read blanks; exponents with and without a sign; signs on the mantissa
    variants = [
        [_LEV0[:30], _LEV1, _BR[:42], _LEV2],
        [_LEV0.replace("2.500E-03", "  2.500e3"), _LEV1.replace("1.812362", "+1.81236"), _BR, _LEV2],
        [_LEV0.replace("0.000000", "  -0.000"), _LEV1, _BR.replace("1.000000", "    .5  "), _LEV2],
    ]
    for lines in variants:
        recs = _records(tmp_path, lines)
        got = L._level_block_nx2(2, recs)
        assert got is not None and _same(got, L._level_block_py(2, recs)), lines
    # every non-plain form falls back to the Python readers
    fallbacks = [
        _LEV1.replace("1.812362", "  1812362"),  # implied decimals
        _LEV1.replace("1.812362", "1.81 2362"),  # inner blank
        _LEV1.replace("   1.5", "  1D+0"),  # D exponent
        _LEV1.replace("1.812362", "1.8123-2"),  # signed exponent without a letter
        _LEV1.replace("1.812362", "     1.8E"),  # exponent without digits
        _LEV1.replace("   -1", "   +-"),  # parity not an integer
        _LEV1.replace("-1  1", "-1 -1"),  # negative branch count
    ]
    for bad in fallbacks:
        recs = _records(tmp_path, [_LEV0, bad, _BR, _LEV2])
        assert L._level_block_nx2(2, recs) is None, bad
    # a block that runs out of records: the Python read raises, the kernel declines
    recs = _records(tmp_path, [_LEV0, _LEV1])
    assert L._level_block_nx2(2, recs) is None
    with pytest.raises(IndexError):
        L._level_block_py(2, recs)


def test_lazy_lines_control_bytes(tmp_path):
    cases = [b"a\tb\nc\x1fd\n", b"a\x0bb\n", b"a\x0cb", b"a\x1cb\nc", b"a\x1db", b"a\x1eb",
             b"a\rb", b"a\x85b\n", b"\x00a\nb\x07\n", b"plain\nlines\n"]
    for k, data in enumerate(cases):
        f = tmp_path / f"c{k}.txt"
        f.write_bytes(data)
        for enc in ("latin-1", "utf-8"):
            try:
                ref = tuple(data.decode(enc).splitlines())
            except UnicodeDecodeError:
                continue
            got = F.lazy_lines(str(f), encoding=enc)
            assert tuple(got[i] for i in range(len(got))) == ref, (data, enc)


# ---------------------------------------------------------------------- default parameters


_TARGETS = [(26, 56), (26, 55), (40, 90), (50, 120), (50, 119), (82, 208), (83, 209), (92, 238),
            (94, 239), (95, 241), (3, 6), (8, 16), (29, 63), (71, 175)]


def test_default_params_templates_are_fresh_builds():
    from physics.hf.input import defaults as D

    D._PARAMS_TEMPLATES.clear()
    for Z, A in _TARGETS + _TARGETS[::-1]:  # the second pass takes every tensor from a template
        o = D.default_options(Z, A)
        D._default_params_values.cache_clear()
        got = D._default_params_values(Z, A, o)
        ref = D._default_params_build(Z, A, o, None, None)
        assert set(got) == set(ref)
        for k in ref:
            assert got[k].dtype == ref[k].dtype and torch.equal(got[k], ref[k]), (Z, A, k)


# ---------------------------------------------------------------------------------- masses


@needs_db
def test_masses_table_gather_is_the_element_loop():
    from physics.hf.input.defaults import default_options
    from physics.hf.structure import masses as M

    M._DENSE.clear()
    for Z, A in _TARGETS:
        o = default_options(Z, A)
        m = M.masses(o)
        Zinit, Ninit, maxZ, maxN = o.Zinit, o.Ninit, o.maxZ, o.maxN
        nz, nn = maxZ + 5, maxN + 5
        A_g = Zinit + Ninit - np.arange(nz)[:, None] - np.arange(nn)[None, :]
        expmass = np.zeros((nz, nn))
        beta2 = np.zeros((nz, nn))
        beta4 = np.zeros((nz, nn))
        gsspin = np.where(A_g % 2 == 0, 0.0, 0.5)
        gsparity = np.ones((nz, nn))
        sdir = str(F.talys_structure_dir())
        theo = {1: "frdm", 0: "hfb", 2: "hfb", 3: "hfbd1m"}[o.massmodel]
        for Zix in range(nz):  # masses.f90's loop, as `_masses_of` had it
            Zc = Zinit - Zix
            if Zc <= 0:
                continue
            Abegin, Aend = Zc + Ninit - maxN - 4, Zc + Ninit
            ia, cols = M._mass_table(sdir, Zc, "ame2020")
            sel = (ia >= Abegin) & (ia <= Aend)
            expmass[Zix, Ninit - (ia[sel] - Zc)] = cols[sel, 0]
            ia, cols = M._mass_table(sdir, Zc, theo)
            sel = (ia >= Abegin) & (ia <= Aend)
            Nix = Ninit - (ia[sel] - Zc)
            cols = cols[sel]
            b2 = beta2[Zix, Nix]
            beta2[Zix, Nix] = np.where(b2 == 0.0, cols[:, 2].astype(np.float32).astype(float), b2)
            beta4[Zix, Nix] = cols[:, 3].astype(np.float32)
            gsspin[Zix, Nix] = cols[:, 4].astype(np.float32)
            gsparity[Zix, Nix] = cols[:, 5]
        for name, ref in (("expmass_amu", expmass), ("beta2", beta2), ("beta4", beta4),
                          ("gsspin", gsspin), ("gsparity", gsparity)):
            assert getattr(m, name).numpy().tobytes() == ref.tobytes(), (Z, A, name)


@needs_db
def test_duflo_cells_are_the_scalar_formula_whatever_grid_asked_first():
    from physics.hf.structure import masses as M

    M._DUFLO_HAVE[:] = False
    for Zinit, Ninit in ((93, 147), (27, 30), (51, 70), (93, 146)):
        M._duflo_grid.cache_clear()
        exc, live = M._duflo_grid(Zinit, Ninit, 17, 39)
        for Zix in range(0, 17, 3):
            for Nix in range(0, 39, 4):
                Z, N = Zinit - Zix, Ninit - Nix
                want = M.duflo(N, Z) if (Z > 0 and N > 0) else 0.0
                assert exc[Zix, Nix] == want and bool(live[Zix, Nix]) == (Z > 0 and N > 0)
