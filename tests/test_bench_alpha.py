"""(n,a) / He-4 production derived the same way for every evaluated file (incognita/bench/alpha.py), and the REACTION-code
check of the benchmark rows (incognita/bench/reaction_check.py). Synthetic ENDF-6 sections; no library file needed."""
import numpy as np
import pytest

from incognita.bench import alpha as AL
from incognita.bench import score as S


def _num(x):
    if isinstance(x, int):
        return f'{x:11d}'
    m, e = f'{x:.6e}'.split('e')
    return f'{m}{int(e):+d}'.rjust(11)


def _lines(vals, mf, mt, mat=2631):
    out = []
    for i in range(0, len(vals), 6):
        row = ''.join(_num(v) if v is not None else ' ' * 11 for v in vals[i:i + 6]).ljust(66)
        out.append(f'{row}{mat:4d}{mf:2d}{mt:3d}')
    return out


def _cont(c1, c2, l1, l2, n1, n2, mf, mt):
    return _lines([c1, c2, l1, l2, n1, n2], mf, mt)


def _tab1(c1, c2, l1, l2, xy, mf, mt):
    return _cont(c1, c2, l1, l2, 1, len(xy), mf, mt) + _lines([len(xy), 2], mf, mt) + _lines([v for p in xy for v in p], mf, mt)


def _mf6_mt5():
    """MF6 MT5 of a Fe-56-like file: residual Cr-53 (LAW 0) yield 0 -> 0.5 from 10 to 20 MeV, alpha (LAW 1) yield 0 -> 0.6,
    neutron (LAW 7) in between, to check that every LAW block is skipped correctly."""
    L = _cont(26056.0, 55.45, 0, 2, 3, 0, 6, 5)
    L += _tab1(2004.0, 3.97, 0, 1, [(1e7, 0.0), (2e7, 0.6)], 6, 5)               # alpha, LAW 1
    L += _cont(0.0, 0.0, 1, 2, 1, 2, 6, 5) + _lines([2, 2], 6, 5)                 # TAB2: NE = 2
    for e in (1e7, 2e7):
        L += _cont(0.0, e, 0, 0, 4, 2, 6, 5) + _lines([0.0, 0.0, 1e6, 1e-6], 6, 5)  # LIST: NW = 4
    L += _tab1(1.0, 1.0, 0, 7, [(1e7, 1.0), (2e7, 1.0)], 6, 5)                    # neutron, LAW 7
    L += _cont(0.0, 0.0, 0, 0, 1, 1, 6, 5) + _lines([1, 2], 6, 5)                 # TAB2: NE = 1
    L += _cont(0.0, 1.5e7, 0, 0, 1, 2, 6, 5) + _lines([2, 2], 6, 5)               # TAB2: NMU = 2
    for mu in (-1.0, 1.0):
        L += _tab1(0.0, mu, 0, 0, [(0.0, 0.0), (1e6, 1e-6)], 6, 5)
    L += _tab1(24053.0, 52.5, 0, 0, [(1e7, 0.0), (2e7, 0.5)], 6, 5)              # residual Cr-53, LAW 0
    return '\n'.join(L)


def test_mt5_yields_and_parts():
    g = np.array([5e6, 1e7, 1.5e7, 2e7])
    y = AL.mt5_yields(_mf6_mt5(), (24053, 2004), g)
    assert np.allclose(y[24053], [0, 0, 0.25, 0.5]) and np.allclose(y[2004], [0, 0, 0.3, 0.6])
    s5 = np.array([0.0, 0.01, 0.1, 0.4])
    p = AL.mt5_alpha_parts(_mf6_mt5(), 26, 56, s5, g)
    assert np.allclose(p[AL.MT5_NA], s5 * [0, 0, 0.25, 0.5]) and np.allclose(p[AL.MT5_HE], s5 * [0, 0, 0.3, 0.6])
    # no MT 5 products in the file: defined only where sigma_5 = 0 everywhere
    assert AL.mt5_alpha_parts('', 26, 56, s5, g) == {}
    assert set(AL.mt5_alpha_parts('', 26, 56, np.zeros(4), g)) == {AL.MT5_NA, AL.MT5_HE}


def test_na_and_he_totals_and_completeness():
    n = len(S.G)
    c = {107: np.full(n, 0.004), 5: np.where(S.G > 1e7, 0.1, 0.0)}
    y, miss = AL.na_total(c)                       # MT 5 > 0, products not read: incomplete above 10 MeV only
    i5, i14 = np.searchsorted(S.G, 5e6), np.searchsorted(S.G, 1.4e7)
    assert not AL.is_incomplete(y[i5], miss[i5]) and AL.is_incomplete(y[i14], miss[i14])
    assert not AL.is_incomplete(1.0, 0.009) and AL.is_incomplete(1.0, 0.011)     # sigma_5 bound below 1 % is harmless
    c[AL.MT5_NA] = np.where(S.G > 1e7, 0.096, 0.0)
    y, miss = AL.na_total(c)
    assert miss is None and abs(y[i14] - 0.1) < 1e-12
    h = {22: np.full(n, 0.01), 108: np.full(n, 0.001), 107: np.full(n, 0.004)}
    y, miss = AL.he_total(h)                       # 0.01 + 2 x 0.001 + 0.004
    assert miss is None and np.allclose(y, 0.016)
    cur = S.Curves({(26, 56, k): v for k, v in c.items()}, S.G)
    assert abs(cur.value(26, 56, 'na', 1.4e7, '') - 0.1) < 1e-6
    assert abs(cur.alpha_value(26, 56, 'na', 1.4e7, '', old=True)[0] - 0.004) < 1e-9
    del cur.tab[(26, 56, AL.MT5_NA)]; cur._cache = {}
    assert cur.alpha_value(26, 56, 'na', 1.4e7)[1] == 'incomplete' and np.isnan(cur.value(26, 56, 'na', 1.4e7))


@pytest.mark.parametrize('rx,flags', [
    ('(26-FE-56(N,A)24-CR-53,,SIG)', []),
    ('(26-FE-54(N,A)24-CR-51,,SIG,,,DERIV)', ['SF9:DERIV']),
    ('(77-IR-191(N,2N)77-IR-190-G+M1,,SIG)', ['STATE-G+M1']),            # Ir-190 has a second long-lived isomer
    ('(49-IN-115(N,2N)49-IN-114-L,,SIG)', ['STATE-L']),
    ('((30-ZN-67(N,P)29-CU-67,,SIG)+(30-ZN-68(N,X)29-CU-67,,SIG,,RAB))', ['COMBO_SUM', 'SF8:RAB']),
    ('((28-NI-60(N,P)27-CO-60,,SIG)+(28-NI-60(N,N+P)27-CO-59,,SIG))', ['COMBO_SUM']),
    ('((46-PD-106(N,G)46-PD-107,,SIG)+(46-PD-108(N,G)46-PD-109,,SIG))', ['COMBO_SUM']),
    ('((46-PD-108(N,G)46-PD-109-G,,SIG)+(46-PD-108(N,G)46-PD-109-M,,SIG,,FCT))', []),   # Pd-109m: IT 100 %
    ('(81-TL-203(N,A)79-AU-200-G,M+,SIG)', ['SF5:M+', 'STATE-G']),       # Au-200m: IT 16 %
    ('(40-ZR-90(N,2N)40-ZR-89-G+M1,,SIG)', []),                          # only one long-lived isomer
])
def test_reaction_flags(rx, flags):
    pytest.importorskip('data.ingest.exfor_reactions')
    from incognita.bench.reaction_check import reaction_flags
    iso = {(77, 190): [100.0, 8.6], (46, 109): [100.0], (79, 200): [16.0], (40, 89): [93.77]}
    assert reaction_flags(rx, '12345', isomers=lambda z, a: iso.get((z, a), [])) == flags


def test_ingest_stages_mt5_alpha_parts(tmp_path):
    E = pytest.importorskip('data.ingest.endf')
    assert {23, 25, 29, 30, 108, 109, 113, 114} <= set(E.ALL_MTS) and E.MT5_ALPHA_MTS == (AL.MT5_NA, AL.MT5_HE)
    other = _cont(26056.0, 55.45, 0, 0, 0, 0, 3, 5)              # an MF3 MT5 HEAD: must not be picked up
    tape = tmp_path / 'tape20'
    tape.write_text('\n'.join(other + [_mf6_mt5()]) + '\n')
    lines = E._mt5_product_lines(tape)
    assert len(lines) == len(_mf6_mt5().splitlines()) and all(l[70:75] == ' 6  5' for l in lines)
    g = np.array([5e6, 1e7, 1.5e7, 2e7])
    p = AL.mt5_alpha_parts('\n'.join(lines), 26, 56, np.array([0.0, 0.01, 0.1, 0.4]), g)
    assert np.allclose(p[AL.MT5_NA], [0, 0, 0.025, 0.2])
