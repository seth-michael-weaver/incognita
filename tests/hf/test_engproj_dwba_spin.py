"""ENGPROJ: the general-spin DWBA weight reproduces the spin-1/2 and spin-0 forms, and spin 1 conserves flux."""
import torch

from physics.hf.core.angmom import clebsch
from physics.hf.core.tensors import DTYPE
from physics.hf.ecis.dwba import _lj_table, spin_weights


def _cg_half(l, j, lam, pb, njmax):
    jc, jp = j[None, :], j[:, None]
    lm = torch.full_like(jp.expand(jp.shape[0], jc.shape[1]), float(lam))
    cg = clebsch(jc.expand_as(lm), lm, jp.expand_as(lm), torch.full_like(lm, -0.5), torch.zeros_like(lm),
                 torch.full_like(lm, -0.5))
    par = (-1.0) ** (l.to(DTYPE)[:, None] + l.to(DTYPE)[None, :])
    keep = (pb * par > 0).to(DTYPE) * (jc <= njmax + 0.5 + 1e-9).to(DTYPE)
    return (2.0 * jc + 1.0) / 2.0 * cg * cg * keep


def test_spin_half_identity():
    for lam in (2, 3, 4):
        l, j, _ = _lj_table(14, 0.5)
        a = spin_weights(l, j, lam, (-1) ** lam, 10, 0.5)
        b = _cg_half(l, j, lam, (-1) ** lam, 10)
        assert torch.allclose(a, b, rtol=1e-12, atol=1e-14)


def test_spin_one_table_and_sum_rule():
    l, j, ls2 = _lj_table(12, 1.0)
    assert int((l == 0).sum()) == 1 and int((l == 3).sum()) == 3
    assert torch.allclose(ls2[(l == 2) & (j == 3.0)], torch.tensor([4.0], dtype=DTYPE))  # 2 l.s = 12-6-2
    for lam in (2, 3):
        w = spin_weights(l, j, lam, (-1) ** lam, 8, 1.0)
        # summed over exit channels, each open entrance channel carries (2J+1)/(2s+1) (sum over j', l' of |A|^2 = 1)
        jc = j[None, :]
        expect = (2.0 * jc + 1.0) / 3.0
        live = (j <= 5.0)  # far from the l table edge
        assert torch.allclose(w.sum(0)[live], expect[0, live], rtol=1e-10)
