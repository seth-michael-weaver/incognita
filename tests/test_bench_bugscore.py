"""Scoring bug hunt 2026-11-07 (BUGSCORE): regression tests for the bench scorer. Synthetic ENDF-6 text; no library file needed."""
import numpy as np

from incognita.bench import alpha as AL
from incognita.bench import score as S
from tests.test_bench_alpha import _cont, _lines, _tab1


def test_he_total_uses_na_levels_when_mt107_absent():
    """A file that gives (n,a) only as its levels MT 800-849 (no MT 107) emits those alphas too: He-4 production must
    count them, as na_total already does (binavg / score: 'MT 107, else the sum of MT 800-849')."""
    lv = {800: np.array([0.0, 0.01, 0.02]), 801: np.array([0.0, 0.005, 0.01])}
    na, _ = AL.na_total(lv)
    he, miss = AL.he_total(lv)
    assert miss is None and np.allclose(na, [0.0, 0.015, 0.03])
    assert he is not None and np.allclose(he, na)
    # MT 107 present: the levels are its parts and are not added again
    both = {107: np.array([0.0, 0.015, 0.03]), **lv, 22: np.array([0.0, 0.001, 0.002])}
    he2, _ = AL.he_total(both)
    assert np.allclose(he2, [0.0, 0.016, 0.032])


def _endf(za, liso, sig102, mat):
    L = _lines([float(za), 55.0, 0, 0, 0, 0], 1, 451, mat)                     # HEAD: ZA AWR LRP=0
    L += _lines([0.0, 0.0, 0, liso, 0, 6], 1, 451, mat)                          # ELIS STA LIS LISO 0 NFOR=6
    L += _lines([float(za), 55.0, 0, 0, 0, 0], 3, 102, mat)                     # MF3 HEAD, then the TAB1
    L += [l[:66] + f'{mat:4d}{3:2d}{102:3d}' for l in _tab1(0.0, 0.0, 0, 0, [(1e-5, sig102), (2e7, sig102)], 3, 102)]
    return '\n'.join(L) + '\n'


def test_endf_library_keeps_ground_state_over_metastable_target(tmp_path):
    """--endf DIR on a full library: n-095_Am_242.endf and n-095_Am_242m1.endf carry the same ZA; the metastable target
    (LISO = 1) sorts after the ground state and used to overwrite it, so the ground-state rows were scored on the isomer."""
    (tmp_path / 'n-095_Am_242.endf').write_text(_endf(95242, 0, 2.0, 9546))
    (tmp_path / 'n-095_Am_242m1.endf').write_text(_endf(95242, 1, 7.0, 9547))
    cur = S.endf_library(sorted(tmp_path.iterdir()))
    v = cur.value(95, 242, 'capture', 1e5)
    assert np.isclose(v, 2.0), v
