"""Direct radiative capture. OFF by default (flagracap = .false., input_gammamodel.f90:61).

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

Task: T12 (physics/hf/CONTRACT.md §7). Acceptance test: A-mult (§6).

TALYS routines ported here (file:line of the subroutine/function statement):
    racap.f90:1 (racap)
    racapinit.f90:1 (racapinit)

Scope, stated plainly
---------------------
The kernel of direct capture is `racapcalc.f`, 2,015 lines of Fortran-77 that solve the bound
and scattering states and integrate the E1/E2/M1 overlaps, driven by the JLMB folding potential
(`mom`) and by particle-hole level-density tables (`phdensitytablejp`). That is a solver on the
scale of T13's ECIS and is **not** ported here; like ECIS, it is the injection seam. What is
ported is everything TALYS does around it:

* `racapinit.f90:416-479` -- how many final states are "experimental" (`nlevexpracap`), and the
  spectroscopic factor of every one of them: the two global defaults (`sfexpall` = 0.347, or 1
  for an odd-A target; `sfthall` = 1, input_gammapar.f90:162-164) overridden level by level from
  `structure/levels/spectn/<Sym>.spect<n|p>` when the energy, spin and parity all match;
* `racap.f90:180-210` -- the barn-to-millibarn conversion, the split of the capture strength into
  a discrete part (`xsracapedisc`) and a continuum part (`xsracapecont`), and the binning of the
  continuum states into the excitation-energy bins, giving `xsracappopex` and `xsracappop(J, pi)`;
* `binary.f90:273-306` and `binary.f90:320` -- the addends the capture channel and the compound
  flux receive when the flag is on.

`racapcalc`'s per-state cross sections are the argument `xspex_b`; the reference runs T12 made
(`reference_runs.py`, variant `t12racap`) write them, and `racap.out` is what the gate reads.
Nothing here runs unless `options.flagracap` is true, so the default path of the port is
unchanged.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import torch
from torch import Tensor

from physics.hf.core.constants import nuclide_symbol
from physics.hf.core.tensors import DTYPE
from physics.hf.structure.files import fortran_read, talys_structure_dir

__all__ = [
    "RacapPopulation",
    "ISPECT",
    "spectroscopic_factors",
    "n_experimental_levels",
    "racap_populations",
    "racap_binary_addends",
]

# racapinit.f90:418. TALYS hard-codes it: experimental levels first, theoretical ones above.
ISPECT = 3
PARSYM = ("g", "n", "p", "d", "t", "h", "a")


@dataclass(frozen=True)
class RacapPopulation:
    """What `racap` hands to `binary`, in mb (racap.f90:186-210).

    `popex` is indexed by the excitation index `nex` of the compound nucleus (levels below
    `nlevexpracap`, bins above); `pop` is (nex, J, parity) with parity ordered (-1, +1) (§4.2).
    """

    xsracape_mb: Tensor  # scalar, total direct capture
    xsracapedisc_mb: Tensor  # scalar
    xsracapecont_mb: Tensor  # scalar
    popex_mb: Tensor  # (nex,)
    pop_mb: Tensor  # (nex, numJph+1, 2)


def n_experimental_levels(nlast: int) -> int:
    """`nlevexpracap` = Nlast(0,0,0) + 1, or 1 when only theoretical levels are used.

    TALYS: racapinit.f90:1 (racapinit)
    Test: A-mult (the `experimental levels` line of racap.out)
    """
    return 1 if ISPECT == 2 else int(nlast) + 1


def _read_spect_file(k0: int, Z: int, A: int) -> list[tuple]:
    """The `<Sym>.spect<p>` block for mass `A`: (index, E, spin, parity, factor) per level.

    `racapinit.f90:452-477` reads `i, ka, jlev` free-format, then `jlev` records with
    `(2x, i3, f8.4, f6.2, 2x, i2, f10.5)`, and only uses the block whose `ka` is the compound
    nucleus mass. Blank lines separate the blocks in the file and TALYS's list-directed read
    walks straight past them, so they are dropped here before the blocks are counted -- keeping
    them would put every block after the first at the wrong offset (which silently costs Fe-57
    and every other non-leading block its file factors).
    """
    path = (
        talys_structure_dir()
        / "levels"
        / f"spect{PARSYM[k0]}"
        / f"{nuclide_symbol(Z).strip()}.spect{PARSYM[k0]}"
    )
    if not path.is_file():
        return []
    lines = [ln for ln in path.read_text(errors="replace").splitlines() if ln.strip()]
    i = 0
    while i < len(lines):
        head = lines[i].split()
        if len(head) < 3:
            break
        ka, jlev = int(head[1]), int(head[2])
        if ka == A:
            out = []
            for ln in lines[i + 1 : i + 1 + jlev]:
                j, e, spinf, parity, sf = fortran_read(ln, "(2x, i3, f8.4, f6.2, 2x, i2, f10.5)")
                out.append((int(j), float(e), float(spinf), int(parity), float(sf)))
            return out
        i += jlev + 1
    return []


def spectroscopic_factors(
    Z: int,
    A: int,
    options,
    params,
    edis_mev: np.ndarray,
    jdis: np.ndarray,
    parlev: np.ndarray,
    nlast: int,
    numex: int,
) -> np.ndarray:
    """`spectfac(0, 0, nex)` for the compound nucleus (Z, A), 0..numex.

    Below `nlevexpracap` a level takes the experimental factor (`sfexp`, default 0.347, or 1 for
    an odd-A target -- input_gammapar.f90:163-164); above it every bin takes the theoretical one
    (`sfth`, default 1). The per-level file then overrides any level up to `Nlast` whose energy
    is within 0.1 MeV and whose spin and parity match exactly (racapinit.f90:463-469); the first
    match wins and the file record is not reused.

    TALYS: racapinit.f90:1 (racapinit)
    Test: A-mult (the `Spectroscopic factors` block of racap.out)
    """
    nexp = n_experimental_levels(nlast)
    sfth = float(params["sfth"][0, 0]) if "sfth" in params else 1.0
    out = np.empty(numex + 1)
    for nex in range(numex + 1):
        if nex <= nexp - 1 and "sfexp" in params and nex < params["sfexp"].shape[2]:
            out[nex] = float(params["sfexp"][0, 0, nex])
        elif nex <= nexp - 1:
            out[nex] = 1.0 if A % 2 != 0 else 0.347
        else:
            out[nex] = sfth
    if ISPECT == 2:
        return out
    for _j, e, spinf, parity, sf in _read_spect_file(options.k0, Z, A):
        for nex in range(0, min(nlast, numex) + 1):
            if (
                abs(float(edis_mev[nex]) - e) < 1.0e-1
                and float(jdis[nex]) == spinf
                and int(parlev[nex]) == parity
            ):
                out[nex] = sf
                break
    return out


def racap_populations(
    xspex_b: Tensor,
    xsp_b: Tensor,
    exfin_mev: np.ndarray,
    nlevracap: int,
    nlevexpracap: int,
    ex_mev: np.ndarray,
    deltaex_mev: np.ndarray,
    maxex: int,
    numjph: int = 30,
) -> RacapPopulation:
    """Turn `racapcalc`'s per-state capture cross sections into the arrays `binary` consumes.

    `xspex_b[i]` and `xsp_b[i, J, parity]` are state `i = 1..nlevracap` in barns, as
    `racapcalc` returns them; everything here is the factor 1000 (racap.f90:186), the split at
    `nlevexpracap` and, for a state above it, the search for the excitation bin whose
    half-width brackets `exfin[i]` (racap.f90:199-201). A continuum state outside every bin is
    dropped -- TALYS's loop simply never matches it -- so `xsracapecont` can exceed the sum of
    what lands in `popex`.

    TALYS: racap.f90:1 (racap)
    Test: A-mult (the per-level table of racap.out)
    """
    xspex = torch.as_tensor(xspex_b, dtype=DTYPE).reshape(-1)
    xsp = torch.as_tensor(xsp_b, dtype=DTYPE)
    mb = torch.as_tensor(1000.0, dtype=DTYPE)
    popex = torch.zeros(maxex + 1, dtype=DTYPE)
    pop = torch.zeros(maxex + 1, numjph + 1, 2, dtype=DTYPE)
    disc = torch.zeros((), dtype=DTYPE)
    cont = torch.zeros((), dtype=DTYPE)
    for i in range(1, int(nlevracap) + 1):
        term = xspex[i - 1] * mb
        if i <= nlevexpracap:
            disc = disc + term
            if i - 1 <= maxex:
                popex = popex.index_put((torch.tensor(i - 1),), term, accumulate=True)
                pop[i - 1] = pop[i - 1] + xsp[i - 1] * mb
        else:
            cont = cont + term
            for nex in range(nlevexpracap, maxex + 1):
                lo = ex_mev[nex] - deltaex_mev[nex] / 2.0
                hi = ex_mev[nex] + deltaex_mev[nex] / 2.0
                if lo <= exfin_mev[i - 1] < hi:
                    popex = popex.index_put((torch.tensor(nex),), term, accumulate=True)
                    pop[nex] = pop[nex] + xsp[i - 1] * mb
    return RacapPopulation(disc + cont, disc, cont, popex, pop)


def racap_binary_addends(
    rp: RacapPopulation,
    xsdisctot_mb: Tensor,
    xsdircont_mb: Tensor,
    xspopnuc_mb: Tensor,
    xsbinary_mb: Tensor,
) -> dict[str, Tensor]:
    """The five totals `binary.f90:273-278` moves when `racap y` is set, plus the flux term.

    `xscompall` (binary.f90:320) loses the whole of `xsracape`, so direct capture takes flux out
    of the compound nucleus rather than adding to it. Returns a dict of the updated scalars; the
    per-level and per-bin populations are `rp.popex_mb` and `rp.pop_mb`, which binary.f90:279-305
    adds into `xspop`/`xspopex` at each level's own (J, parity).

    TALYS: racap.f90:1 (racap)
    Test: A-mult
    """
    return {
        "xsdisctot_mb": xsdisctot_mb + rp.xsracapedisc_mb,
        "xsdircont_mb": xsdircont_mb + rp.xsracapecont_mb,
        "xspopnuc_mb": xspopnuc_mb + rp.xsracape_mb,
        "xsbinary_mb": xsbinary_mb + rp.xsracape_mb,
        "xscompall_subtract_mb": rp.xsracape_mb,
    }
