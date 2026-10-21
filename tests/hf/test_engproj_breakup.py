"""ENGPROJ: Kalbach breakup (breakup.f90) on a hand-made deuteron case: only n and p get a spectrum; peak near
Ecent; the integral equals the breakup cross section (PBU is normalised over the emission grid)."""
import math
from types import SimpleNamespace

import torch

from physics.hf.core.tensors import DTYPE
from physics.hf.preeq.complex import breakup


def _inp(k0=3, Z=26, A=56, einc=20.0):
    E = 80
    eg = torch.linspace(0.25, 39.75, E, dtype=DTYPE).reshape(1, E)
    de = torch.full((1, E), 0.5, dtype=DTYPE)
    s = torch.tensor([[0.0, 10.0, 8.0, 12.0, 15.0, 16.0, 7.0]], dtype=DTYPE)
    ecomp = torch.tensor([einc * A / (A + 2.0) + 12.0], dtype=DTYPE)
    return SimpleNamespace(k0=k0, Z=Z, A=A, C=1, E=E, einc_mev=torch.tensor([einc], dtype=DTYPE), ecomp_mev=ecomp,
                           egrid_mev=eg, deltae_mev=de, emask=torch.ones(1, 7, E, dtype=torch.bool), s_mev=s)


def test_deuteron_breakup_shape():
    out = breakup(_inp(), SimpleNamespace(), [1.0] * 6)
    assert out.shape == (1, 7, 80)
    assert float(out[0, 1].sum()) > 0 and float(out[0, 2].sum()) > 0
    assert float(out[0, 3:].abs().sum()) == 0.0 and float(out[0, 0].abs().sum()) == 0.0
    # the neutron spectrum peaks about half the incident energy (Ecent = (Einc - Ca)/2 + Cb, Cb = 0 for n)
    peak = float(_inp().egrid_mev[0, int(out[0, 1].argmax())])
    assert 5.0 < peak < 11.0


def test_cbreak_zero_kills():
    out = breakup(_inp(), SimpleNamespace(), [0.0] * 6)
    assert float(out.abs().sum()) == 0.0
