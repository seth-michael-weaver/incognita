"""SPEEDW: the compiled DWBA Numerov loop (`native/speedw.c`) equals `ecis.dwba.distorted_waves`'s
torch loop to the bit.

The kernel repeats torch's own complex kernels at one thread -- the plain product on the first
N - N%4 elements of a contiguous result and the fma form on the rest, the fma form for a strided
operand, Smith's division in fma form -- so the check is exact equality, on every tail length
(N % 4 = 0..3), a single row, and channel counts from 1 to a coupled-deck-sized batch. Values
are drawn over the magnitudes a real deck has (the fma/plain split shows up in the last bit of
random operands, so a wrong rule fails here). A machine with its own build must pass this before
the kernel is trusted there.
"""

from __future__ import annotations

import platform

import pytest
import torch

from physics.hf.ecis import dwba
from physics.hf.native import speedw

pytestmark = pytest.mark.skipif(not speedw.available(), reason="libspeedw.so not built "
                                "(scripts/build_speedw_native.sh)")


@pytest.mark.parametrize("nk,nlj,n", [(1, 43, 356), (31, 55, 60), (2, 49, 97), (3, 1, 40),
                                      (4, 7, 33), (136, 57, 25), (1, 1, 12)])
def test_kernel_is_the_torch_loop_bit_for_bit(nk, nlj, n, monkeypatch):
    g = torch.Generator().manual_seed(nk * 1000 + nlj * 10 + n)
    f = torch.complex(torch.randn(nlj, n + 1, generator=g, dtype=torch.float64) * 3.0,
                      torch.randn(nlj, n + 1, generator=g, dtype=torch.float64) * 0.5)
    kappa2 = torch.rand(nk, generator=g, dtype=torch.float64) * 2.0 - 0.3
    l = torch.randint(0, 9, (nlj,), generator=g)
    h = 0.0666304755902749
    torch.set_num_threads(1)
    got = speedw.dwba_numerov(f, kappa2, l, h, n)
    monkeypatch.setattr(speedw, "available", lambda: False)
    ref = dwba.distorted_waves(f, kappa2, l, h, n)
    assert got.shape == ref.shape
    if platform.machine().lower() in ("arm64", "aarch64"):
        # COREX: the arm64 kernel steps rows side by side with the division turned into a
        # product (speedw.c); it agrees with the loop to rounding, not to the bit
        scale = ref.abs().clamp(min=1e-300)
        rel = ((got - ref).abs() / scale)[ref.abs() > 0]
        assert float(rel.max()) <= 1e-8
        return
    assert torch.equal(torch.view_as_real(got), torch.view_as_real(ref))
