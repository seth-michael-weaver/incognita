"""SPEEDW: the compiled multipreeq2 loop (`preeq.mpe_fast`) against the torch loop (`preeq.multi`).

Every mother bin of Fe-56's 20 MeV cascade (the only incident energy of the harness grid where
multipreeq2 runs) goes through both, fed the SAME inputs. The kernel uses glibc `pow` and
left-to-right sums where the torch loop uses torch's SIMD pow and lane sums, so the check is rel
1e-14 on every output plus an exact match of the structure (the daughter particle-hole keys and
`mulpreZN`), not bits. The torch loop stays the path for anything on the autograd graph.
"""

from __future__ import annotations

import pytest
import torch

import physics.hf.preeq.mpe_fast as F
import physics.hf.preeq.multi as M

pytestmark = pytest.mark.skipif(not F.available(), reason="libmpenative.so not built "
                                "(scripts/build_mpe_native.sh)")

GRID = (1.0e-3, 1.0, 5.0, 14.0, 20.0)


def _rel(a, b) -> float:
    a = torch.as_tensor(a, dtype=torch.float64)
    b = torch.as_tensor(b, dtype=torch.float64)
    den = torch.maximum(a.abs(), b.abs())
    r = torch.where(den > 0, (a - b).abs() / torch.where(den > 0, den, 1.0), 0.0)
    return float(r.max()) if r.numel() else 0.0


def test_kernel_matches_torch_loop_on_every_mother_bin(monkeypatch):
    from physics.hf.engine import ChainedFull

    seen = {"n": 0, "worst": 0.0}
    torch_loop = M.multiple_preequilibrium
    kernel = F.multiple_preequilibrium_fast

    def both(inp, numj=40):
        ref = torch_loop(inp, numj=numj)
        got = kernel(inp, numj=numj)
        assert got.mulpre == ref.mulpre
        assert list(got.xspopph2_daughter_mb) == list(ref.xspopph2_daughter_mb)
        worst = max(_rel(getattr(ref, n), getattr(got, n)) for n in (
            "dmulti", "summpe_mb", "term_mb", "sumtype_mb", "xspop_add_mb", "xspopph2_mother_mb"))
        for k, v in ref.xspopph2_daughter_mb.items():
            worst = max(worst, _rel(v, got.xspopph2_daughter_mb[k]))
        seen["n"] += 1
        seen["worst"] = max(seen["worst"], worst)
        return ref

    monkeypatch.setattr(F, "multiple_preequilibrium_fast", both)
    # NATIVEX: multipreeq2 runs through `Cascade.mpe` (this kernel), not inside the compiled walk
    monkeypatch.setenv("HF_NATIVEX_MPE", "0")
    ChainedFull(Z=26, A=56, declared_energies=GRID, energies=(20.0,)).cases()
    assert seen["n"] > 100
    assert seen["worst"] <= 1e-14


def test_graph_inputs_take_the_torch_loop(monkeypatch):
    calls = []
    monkeypatch.setattr(F, "multiple_preequilibrium",
                        lambda inp, numj=40: calls.append(1) or "torch")
    inp = type("I", (), {"mpreeqmode": 2, "flag2comp": True, "flaggshell": False,
                         "daughters": (), "zcomp": 1, "ncomp": 0})()
    assert F.multiple_preequilibrium_fast(inp) == "torch"  # not two daughters: torch loop
    assert calls
