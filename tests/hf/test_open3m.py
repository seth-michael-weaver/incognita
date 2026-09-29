"""OPEN3M defect A2: discrete levels whose 2J parity their mass number forbids.

Gate: `docs/results/hf-open3m.md` section 1. TALYS resolves an ENSDF spin range to a spin with the
wrong 2J parity (Nb-95 level 6, `(5/2:13/2)+`, becomes J = 3.0). compprepare.f90/comptarget.f90
then enumerate `jj2'` with the wrong parity, `l2'` comes out odd and `lprime = l2prime / 2`
truncates. The port parameterised the loop by integer l' and gave such a level exactly zero.
"""

from __future__ import annotations

import itertools

import pytest
import torch

from physics.hf.compound.prepare import PARSPIN2, SPIN2, anomalous_exit_mask
from physics.hf.compound.target_batch import _mask_for


def _fortran_channels(J2: int, Irspin2: int, t: int, l2maxhf: int) -> set[tuple[int, int]]:
    """compprepare.f90's exit loops, transcribed literally: the (lprime, updown2) it reads."""
    parspin2o, pspin2o = PARSPIN2[t], SPIN2[t]
    out = set()
    for jj2prime in range(abs(J2 - Irspin2), J2 + Irspin2 + 1, 2):
        l2primebeg = abs(jj2prime - parspin2o)
        if t == 0:
            l2primebeg = max(l2primebeg, 2)
        l2primeend = min(jj2prime + parspin2o, l2maxhf)
        for l2prime in range(l2primebeg, l2primeend + 1, 2):
            lprime = l2prime // 2
            updown2 = 0 if t == 0 else int((jj2prime - l2prime) / pspin2o)  # Fortran truncation
            out.add((lprime, updown2))
    return out


@pytest.mark.parametrize("t", range(7))
def test_mask_is_compprepare_for_every_spin_parity(t):
    """Every (J2, Irspin2) pair, both 2J parities of the level, against the Fortran loops, with
    the `l2' <= l2maxhf` cap the callers apply."""
    L, lmaxhf = 9, 6
    lp = torch.arange(L)
    for J2, Irspin2 in itertools.product(range(0, 16), range(0, 16)):
        lo, hi = torch.tensor([abs(J2 - Irspin2)]), torch.tensor([J2 + Irspin2])
        anom = (lo + PARSPIN2[t]) % 2
        m = anomalous_exit_mask(lo, hi, anom, PARSPIN2[t], SPIN2[t], L, t == 0)[0]
        m = m & (2 * lp + anom <= 2 * lmaxhf)[:, None]
        got = {(int(a), int(b) - 1) for a, b in torch.nonzero(m).tolist()}
        assert got == _fortran_channels(J2, Irspin2, t, 2 * lmaxhf), (J2, Irspin2)


@pytest.mark.parametrize("t", range(7))
def test_plain_spins_keep_the_old_mask_bitwise(t):
    """With no anomalous level `_mask_for` takes its original branch; the new rule agrees there."""
    L = 9
    j2 = torch.arange(1, 30, 2)
    irs2 = (2 * torch.arange(12) + (1 + PARSPIN2[t]) % 2)[None, :].expand(len(j2), -1)
    old = _mask_for(j2, irs2, PARSPIN2[t], SPIN2[t], L, t == 0)
    lo, hi = (j2[:, None] - irs2).abs(), j2[:, None] + irs2
    new = anomalous_exit_mask(lo, hi, (lo + PARSPIN2[t]) % 2, PARSPIN2[t], SPIN2[t], L, t == 0)
    assert torch.equal(old, new.to(old.dtype))


def test_nb95_level_6_is_reached():
    """Nb-96's integer compound spins against Nb-95 L6's J = 3.0: the old rule has no channel at
    all, TALYS's truncation has the ones `_fortran_channels` lists."""
    t, L = 1, 10
    j2 = torch.arange(0, 14, 2)
    irs2 = torch.full((len(j2), 1), 6)
    m = _mask_for(j2, irs2, PARSPIN2[t], SPIN2[t], L, False)
    assert m.sum() > 0
    for k, J2 in enumerate(j2.tolist()):
        got = {(int(a), int(b) - 1) for a, b in torch.nonzero(m[k, 0]).tolist()}
        want = {c for c in _fortran_channels(J2, 6, t, 4 * L) if c[0] < L}  # uncapped
        assert got == want


def test_gpu_photon_mask_is_the_same_rule():
    """`capture_gpu._photon_exit_mask` (l' = 1, 2, l2maxhf = 2 gammax = 4) against the shared rule,
    both 2J parities. Runs on the CPU device; the whole kernel was checked there on Ba-138, whose
    compound nucleus Ba-139 has L15 J = 3.0 and L30 J = 5.0 (docs/results/hf-open3m.md)."""
    from physics.hf.capture_gpu import L, _photon_exit_mask

    j2 = torch.arange(0, 20)[:, None].expand(20, 20)
    irs2 = torch.arange(0, 20)[None, :].expand(20, 20)
    got = _photon_exit_mask(j2, irs2)
    lo, hi = (j2 - irs2).abs(), j2 + irs2
    ref = anomalous_exit_mask(lo, hi, lo % 2, 0, 1, L, True)[..., 1]
    ref = ref & (2 * torch.arange(L) + (lo % 2)[..., None] <= 2 * (L - 1))
    assert torch.equal(got.bool(), ref[..., 1:])
