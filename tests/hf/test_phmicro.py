"""PHMICRO: tabulated microscopic particle-hole densities (TALYS phmodel 2, structure/density/ph/<El>.ph).

Checks the reader (header labels, 5-point smoothing, phdens2.f90 interpolation) against a hand computation from the
file, and that the override is the identity when the switch is off.
"""

import numpy as np
import pytest
import torch

from physics.hf.density import particle_hole as P


def _have_tables():
    try:
        return P.ph_table2(82, 208) is not None
    except FileNotFoundError:
        return False


pytestmark = pytest.mark.skipif(not _have_tables(), reason="no structure/density/ph tables")


def test_edens_grid():
    e = P.ph_edens()
    assert e[0] == 0.0 and e[1] == 0.25 and e[20] == 5.0 and e[30] == 10.0 and e[40] == 20.0
    assert e[41:44].tolist() == [22.5, 25.0, 30.0] and e[60] == 200.0


def test_table_reader_and_smoothing():
    blk = P._ph_file_blocks(82)[208]
    c2, raw = blk[0], blk[1]
    assert len(c2) == 72 and c2[0] == (0, 0, 1, 0) and c2[3] == (0, 0, 2, 0)
    ex, tab = P.ph_table2(82, 208)
    k = c2.index((0, 1, 1, 0))
    e = P.ph_edens()
    nex = 20  # 5 MeV: the 5-point energy-weighted mean of phdensitytable.f90
    s = sum(raw[j - 1, k] * 0.5 * (e[min(j + 1, 60)] - e[max(j - 1, 1)]) for j in range(nex - 2, nex + 3))
    assert tab[0, 1, 1, 0, nex] == pytest.approx(s / (e[nex + 2] - e[nex - 2]), rel=1e-14)
    assert ex[0, 1, 1, 0] and not ex[4, 4, 4, 4]


def test_interp_log_linear():
    _, tab = P.ph_table2(82, 208)
    row = tab[0, 0, 1, 1]
    e = P.ph_edens()
    x = 0.5 * (e[30] + e[31])  # 10.5 MeV, both ends > 1
    want = np.exp(0.5 * (np.log(row[30]) + np.log(row[31])))
    assert P._ph_interp(row[None, :], np.array([x]))[0] == pytest.approx(want, rel=1e-12)
    assert P._ph_interp(row[None, :], np.array([0.0]))[0] == 0.0


def test_override_off_is_identity_and_on_replaces():
    d = torch.tensor([[1.0, 2.0]], dtype=torch.float64)
    i = torch.tensor([[0, 0]])
    assert P.ph_override(d, i, i + 1, i + 1, i, torch.tensor(5.0), 0, 0, None) is d
    # Pb-208 + n: CN (Z0, N0) = (82, 127); residual of (n,p) is (Zix, Nix) = (1, 0) = Tl-208
    on = P.ph_override(d, i, i + 1, i + 1, i, torch.tensor(5.0, dtype=torch.float64), 1, 0, (82, 127))
    ex, tab = P.ph_table2(81, 208)
    want = P._ph_interp(tab[0, 1, 1, 0][None, :], np.array([5.0]))[0]
    assert torch.allclose(on, torch.full_like(d, want))
    # a configuration outside the table keeps the analytic value
    big = torch.tensor([[5, 5]])
    assert torch.equal(P.ph_override(d, big, big, big, big, torch.tensor(5.0), 0, 0, (82, 127)), d)


def test_phnorm_refdeg_and_switch(monkeypatch):
    """PHMICRO3: INCOGNITA_PHNORM=1 divides the tabulated density by 2 per odd species of the table nucleus; OFF untouched."""
    import numpy as np
    from physics.hf.density import particle_hole as PH

    assert [PH.ph_refdeg(z, n) for z, n in ((50, 66), (50, 67), (49, 66), (49, 67))] == [1.0, 2.0, 2.0, 4.0]
    dens = np.full(3, 7.0)
    args = (np.array(1), np.array(1), np.array(1), np.array(0), np.array([10.0, 15.0, 20.0]))
    monkeypatch.delenv("INCOGNITA_PHNORM", raising=False)
    for zix, nix, d in ((0, 0, 4.0), (0, 1, 2.0), (1, 0, 2.0), (1, 1, 1.0)):  # CN Z0=79, N0=119 (Au-197 + n): odd-odd
        off = PH.ph_override(dens, *args, np.array(zix), np.array(nix), (79, 119))
        monkeypatch.setenv("INCOGNITA_PHNORM", "1")
        on = PH.ph_override(dens, *args, np.array(zix), np.array(nix), (79, 119))
        monkeypatch.delenv("INCOGNITA_PHNORM")
        assert np.all(off > 1.0) and np.allclose(on * d, off)
    assert PH.ph_override(dens, *args, np.array(0), np.array(0), None) is dens
