"""FISSB: a fissioning cascade nucleus on `compound.decay_fast`'s whole-nucleus path.

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

Task: FISSB (the speed work; no physics of its own). Acceptance test: A-mult / E2E through
`tests/hf/test_fission_batch.py`, which holds it to the per-bin `continuum.compound_decay`.

TALYS routines this computes, in the arrangement described below:
    compound.f90:1 (compound)       -- iloop 1's denominator with the fission width, fisfeed
    tfission.f90:1 (tfission)       -- through `fission.fission_batch_ladder`

`Cascade.decay` sent every mother bin of a fissioning nucleus down the per-bin path:
`densprepare`, the triple `bin_triples` builds with three `t1barrier` calls per barrier, and
`continuum._compound_decay_factored`. In compound.f90 fission is one more term of each
(J, parity) cell's denominator and one more output, `fisfeed = sum feed * fiswidth`; nothing
else of the decay sees it. So the fissioning nucleus is `decay_fast.NucleusWidths` with:

* the fission width of every (bin, J, parity) built for the whole ladder at once
  (`fission_batch_ladder.ladder_bin_widths`) and added to the six-exit denominator `dsum6`,
  which is also what the compiled photon kernel reads;
* compound.f90:222's closed-cell rule (a cell with no exit but alpha does not decay by alpha)
  taking the fission width into account: `zero6` also asks for a zero fission width;
* `fisfeed` formed from the bin's feed vector.

The particle exits, the lazy all-bins contraction and `multiple_emission`'s particle batch then
apply unchanged. Sums of non-negative terms are taken in a different order than the per-bin path
(`fiswidth + sum_t D_t` against `sum_{t<6} D_t + fiswidth + D_6`), so results move by rounding.
"""

from __future__ import annotations

import numpy as np

from physics.hf.compound import decay_native as dn
from physics.hf.compound.decay_fast import NucleusWidths

__all__ = ["FissionLadder", "FissionNucleusWidths"]


class FissionLadder:
    """One fissioning nucleus's fission transmission as `Cascade.decay` asks for it: the whole
    bin ladder at once (`widths`), or one bin's triple for the per-bin path (`triples`).

    TALYS: tfission.f90:1 (tfission), compound.f90:120-147 (compound)
    Test: tests/hf/test_fission_batch.py
    """

    __slots__ = ("chain", "Z", "A", "fnorm")

    def __init__(self, chain, Z: int, A: int, fnorm: float):
        self.chain, self.Z, self.A, self.fnorm = chain, int(Z), int(A), float(fnorm)

    def covered(self) -> bool:
        from physics.hf.fission.fission_batch_ladder import covered

        n = self.chain.nucleus(self.Z, self.A)
        return n is not None and covered(n.fp, self.chain.o)

    def triples(self, sp, nex: int) -> dict:
        return self.chain.bin_triples(self.Z, self.A, float(sp.ex_mev[nex]),
                                      float(sp.dex_mev[nex]), float(sp.exmax_mev),
                                      float(sp.ex_mev[sp.maxex]), fnorm=self.fnorm)

    def widths(self, sp, bins: np.ndarray) -> np.ndarray:
        """`continuum.fission_width` for mother bins `bins`, `(bins, J, 2)` with J at least the
        bins' largest `maxj` + 1 (the chain's `maxj` + 1 off the CENGFIS path)."""
        from physics.hf.fission.fis_ceng import ladder_widths
        from physics.hf.fission.fission_batch_ladder import ladder_bin_widths

        n = self.chain.nucleus(self.Z, self.A)
        # CENGFIS: C, no rhofis; the spins up to the bins' maxj, which is all `NucleusWidths` reads
        nj = int(np.asarray(sp.maxj, dtype=np.int64)[bins].max()) + 1 if len(bins) else 1
        got = ladder_widths(self.chain, n, np.asarray(sp.ex_mev, dtype=np.float64)[bins],
                            np.asarray(sp.dex_mev, dtype=np.float64)[bins], float(sp.exmax_mev),
                            float(sp.ex_mev[sp.maxex]), self.fnorm, nj)
        if got is not None:
            return got
        grid = self.chain._grid(n, float(sp.ex_mev[sp.maxex]))
        cache = n.__dict__.setdefault("_fissb_coef", {})
        return ladder_bin_widths(n.fp, grid, n.ld, np.asarray(sp.ex_mev, dtype=np.float64)[bins],
                                 np.asarray(sp.dex_mev, dtype=np.float64)[bins],
                                 float(sp.exmax_mev), self.chain.o, maxj=self.chain.maxj,
                                 fnorm=self.fnorm, cache=cache)

    def nucleus_widths(self, cas, st, sp, bins: list[int]) -> FissionNucleusWidths:
        return FissionNucleusWidths(cas, st, sp, bins, self)


class FissionNucleusWidths(NucleusWidths):
    """`decay_fast.NucleusWidths` of a fissioning nucleus: the fission width in every cell's
    denominator, and `fisfeed` in `feeding`'s third slot.

    TALYS: compound.f90:1 (compound)
    Test: tests/hf/test_fission_batch.py
    """

    def __init__(self, cas, st, sp, bins: list[int], ladder: FissionLadder):
        super().__init__(cas, st, sp, bins)
        fis = ladder.widths(sp, np.asarray(self.bins, dtype=np.int64))
        nj = self.nj
        if fis.shape[1] < nj:
            fis = np.concatenate([fis, np.zeros((fis.shape[0], nj - fis.shape[1], 2))], axis=1)
        self.fis = np.ascontiguousarray(fis[:, :nj])
        self.dsum6 = self.dsum6 + self.fis
        self.zero6 = self.zero6 & (self.fis == 0.0)
        if self._photon_bin is not None:
            self._photon_bin = dn.PhotonBin(self, self.exits[0])

    def feeding(self, nex: int, pop_mother: np.ndarray, popeps_a: float, dmulti: float = 0.0):
        """`NucleusWidths.feeding`, with compound.f90's `fisfeed = sum_(J, P) feed * fiswidth`.

        TALYS: compound.f90:1 (compound)
        Test: tests/hf/test_fission_batch.py
        """
        dp, mc, _, leftover = super().feeding(nex, pop_mother, popeps_a, dmulti)
        feed = self.pending[-1][1]
        fis = self.fis[self.row[nex], : feed.shape[0]]
        return dp, mc, float((feed * fis).sum()), leftover
