"""incognita.bench.score ENDF-6 reading (`--endf` scoring): isomer files and blank-in-exponent numbers."""
import numpy as np

from incognita.bench import alpha as AL
from incognita.bench import score as S


def _fld(v):
    return f"{v:11.6g}".rjust(11) if isinstance(v, float) else f"{v:11d}"


def _line(fields, mat, mf, mt):
    body = "".join(_fld(f) if not isinstance(f, str) else f.rjust(11) for f in fields).ljust(66)
    return f"{body}{mat:4d}{mf:2d}{mt:3d}{1:5d}"


def _tape(path, za, liso, sigma_b, mat=9547):
    """A minimal material: MF1/451 (ZA, LRP=0; LISO on line 2) and MF3/102 constant sigma, lin-lin, 1e-5 eV - 20 MeV."""
    lines = [_line([float(za), 240.0, 0, 0, 0, 0], mat, 1, 451),
             _line([0.0, 0.0, 0, liso, 0, 6], mat, 1, 451),
             _line([float(za), 240.0, 0, 0, 0, 0], mat, 3, 102),
             _line([0.0, 0.0, 0, 0, 1, 2], mat, 3, 102),
             _line([2, 2], mat, 3, 102),
             _line([1e-5, sigma_b, 2e7, sigma_b], mat, 3, 102)]
    path.write_text("\n".join(lines) + "\n")
    return path


def test_isomer_file_does_not_replace_the_ground_state(tmp_path):
    g = _tape(tmp_path / "n-095_Am_242.endf", 95242, 0, 1.0)
    m = _tape(tmp_path / "n-095_Am_242m1.endf", 95242, 1, 5.0)
    for order in ([g, m], [m, g]):
        cur = S.endf_library(order)
        x, y = cur.xy(95, 242, 102)
        assert np.allclose(y[(x > 1) & (x < 1e7)], 1.0), order


def test_blank_inside_exponent():
    # IRDFF-II Mn-55 / Tm-169 and BROND-3.1 O-18 / P-31 write "2.50550+ 4" (data/ingest/endf.endf_float)
    assert S._f(" 2.50550+ 4") == 25055.0
    assert AL._f(" 2.50550+ 4") == 25055.0
    assert S._f("-1.0-5") == -1e-5 and S._f("") == 0.0
