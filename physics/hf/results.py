"""Result schema of the port: names and units match the TALYS output files they replace.

Task: T10 (physics/hf/CONTRACT.md §7). Acceptance test: E2E (§6).

Every cross section is millibarns (contract §4.1), keyed the way TALYS names its files so the
E2E test is a join on the name: exclusive channels by TALYS's six-digit channel code
(`xs000000` = (n,g), `xs100000` = (n,n'), `xs200000` = (n,2n), `xs010000` = (n,p),
`xs000001` = (n,a); code digits = number of n, p, d, t, h, a emitted), per-level partials by
`<ejectile><residual-level>` (`nn.L01`), residual production by `rpZZZAAA`, totals by
`total`, `elastic`, `nonelastic`, `reaction`, fission by `fission`.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import torch
from torch import Tensor

PARSYM = "gnpdtha"  # constants.f90: parsym, types 0..6


@dataclass(frozen=True)
class Results:
    e_inc_mev: Tensor  # (C,)
    channels_mb: dict[str, Tensor] = field(default_factory=dict)  # "xs000000" -> (C,)
    levels_mb: dict[str, Tensor] = field(default_factory=dict)  # "nn.L01" -> (C,)
    residual_production_mb: dict[str, Tensor] = field(default_factory=dict)  # "rp026056" -> (C,)
    totals_mb: dict[str, Tensor] = field(default_factory=dict)  # "total", "elastic", ...
    # what the engine injected rather than computed, per family: "fission", "direct", "ecis", ...
    injected: tuple[str, ...] = ()

    @property
    def n(self) -> int:
        return int(self.e_inc_mev.shape[0])


def channel_code(counts: tuple[int, int, int, int, int, int]) -> str:
    """TALYS's exclusive-channel file name from (n, p, d, t, h, a) emitted."""
    return "xs" + "".join(str(min(c, 9)) for c in counts)


def level_key(k0: int, ejectile: int, level: int) -> str:
    """The `.Lnn` file name of a discrete-level partial (discreteout.f90:179-181)."""
    return f"{PARSYM[k0]}{PARSYM[ejectile]}.L{level:02d}"


def residual_key(Z: int, A: int) -> str:
    """The `rpZZZAAA.tot` file name of a residual production cross section (finalout.f90:379)."""
    return f"rp{Z:03d}{A:03d}"


def stack(per_case: list[dict[str, float]], device=None) -> dict[str, Tensor]:
    """Turn one dict per case into the contract's name -> (C,) tensors, zero-filled where a case
    does not have that key (a channel that is closed at that energy)."""
    keys = sorted({k for d in per_case for k in d})
    return {k: torch.tensor([d.get(k, 0.0) for d in per_case], dtype=torch.float64, device=device)
            for k in keys}
