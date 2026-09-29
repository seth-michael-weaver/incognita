"""CHARTFIX: `Dmulti` reaches the compound decay of the bin multiple pre-equilibrium depleted.

`multipreeq2.f90:374` sets `Dmulti(nex) = summpe / xspopex(Zcomp, Ncomp, nex)` and
`compound.f90:402` then decays the SAME bin with `(1 - Dmulti) * xspop`, so the flux multiple
pre-equilibrium already emitted is not shared out a second time. The port's `multipreeq2` is
exact (`preeq.multi`, gate A-mpe) but both of `Cascade.decay`'s fast paths dropped the factor --
`decay_batch` was handed a literal `dmulti=0.0` and `decay_fast` had no parameter at all -- so at
20 MeV, the one energy of TALYS's default grid where `emulpre` lets multiple pre-equilibrium run,
every second-chance channel was high by the whole multiple pre-equilibrium cross section
(Fe-56 `(n,2n)` +0.63 %, `(n,np)` +0.69 %).

Two checks, on Fe-56's 20 MeV cascade:

* every `Dmulti` `Cascade.mpe` produced arrives at a `feeding` call, and
* `decay_fast` applies it the way `decay_batch` and `compound.f90:402` do.
"""

from __future__ import annotations

import numpy as np
import pytest
import torch

GRID = (1.0e-3, 1.0, 5.0, 14.0, 20.0)


def _rel(a, b) -> float:
    a, b = np.asarray(a, dtype=np.float64), np.asarray(b, dtype=np.float64)
    den = np.maximum(np.abs(a), np.abs(b))
    return float(np.max(np.where(den > 0, np.abs(a - b) / np.where(den > 0, den, 1.0), 0.0),
                        initial=0.0))


@pytest.fixture(scope="module")
def cascade20():
    """Fe-56 at 20 MeV, dump-free: the `Dmulti` of every mother bin multiple pre-equilibrium
    touched, the `dmulti` every `NucleusWidths.feeding` was given, and the widths themselves."""
    import physics.hf.compound.decay_fast as dfm
    import physics.hf.emission.feeding as fm
    from physics.hf.engine import ChainedFull

    mpe_d, feed_d, builds = [], [], []
    mpe0, feed0, init0 = fm.Cascade.mpe, dfm.NucleusWidths.feeding, dfm.NucleusWidths.__init__

    def mpe2(self, st, nuclei, zc, nc, nex, *, etotal_mev):
        r = mpe0(self, st, nuclei, zc, nc, nex, etotal_mev=etotal_mev)
        if r is not None and r.dmulti != 0.0:
            mpe_d.append(((zc, nc, nex), r.dmulti))
        return r

    def feed2(self, nex, pop, popeps_a, dmulti=0.0):
        feed_d.append((id(self), nex, dmulti, np.array(pop), popeps_a))
        return feed0(self, nex, pop, popeps_a, dmulti)

    def init2(self, cas, st, sp, bins):
        out = init0(self, cas, st, sp, bins)
        builds.append((self, cas, st, sp, list(bins)))
        return out

    import os

    from physics.hf.native import nativex

    torch.set_num_threads(1)
    fm.Cascade.mpe, dfm.NucleusWidths.feeding, dfm.NucleusWidths.__init__ = mpe2, feed2, init2
    # NATIVEX: these checks watch `decay_fast`'s numpy path; the compiled walk (held to it by
    # tests/hf/test_nativex.py) is switched off
    prev = os.environ.get("HF_NATIVEX")
    os.environ["HF_NATIVEX"] = "0"
    nativex.lib.cache_clear()
    try:
        ChainedFull(Z=26, A=56, declared_energies=GRID, energies=(20.0,)).cases()
    finally:
        if prev is None:
            os.environ.pop("HF_NATIVEX", None)
        else:
            os.environ["HF_NATIVEX"] = prev
        nativex.lib.cache_clear()
        fm.Cascade.mpe, dfm.NucleusWidths.feeding = mpe0, feed0
        dfm.NucleusWidths.__init__ = init0
    return mpe_d, feed_d, builds


def test_every_dmulti_reaches_the_compound_decay(cascade20):
    """multiple.f90:549-560: the bin multipreeq2 depleted is the next thing `compound` decays."""
    mpe_d, feed_d, _ = cascade20
    assert len(mpe_d) >= 20, len(mpe_d)
    want = sorted(d for _, d in mpe_d)
    got = sorted(d for _, _, d, _, _ in feed_d if d != 0.0)
    assert got == want
    # and nothing else was depleted: one decay per depleted bin, the rest at Dmulti = 0
    assert sum(1 for _, _, d, _, _ in feed_d if d == 0.0) > len(want)


def test_decay_fast_applies_dmulti_like_decay_batch(cascade20):
    """compound.f90:402 in `decay_fast`'s numpy path against `decay_batch`'s tensor path, on the
    bins multiple pre-equilibrium actually depleted."""
    from physics.hf.compound.decay_batch import NucleusDecay

    _mpe_d, feed_d, builds = cascade20
    ref = {}
    n_bins, worst_feed, worst_dp = 0, 0.0, 0.0
    for nwid, nex, dmulti, pop, popeps_a in feed_d:
        if dmulti == 0.0:
            continue
        nw = next(b[0] for b in builds if id(b[0]) == nwid)
        if id(nw) not in ref:
            _, cas, st, sp, bins = next(b for b in builds if id(b[0]) == nwid)
            ref[id(nw)] = NucleusDecay(cas, st, sp, bins)
        # `feed` is where (1 - Dmulti) enters: the same array, scaled
        base = nw.feeding(nex, pop, popeps_a)
        f0 = nw.pending.pop()[1]
        cut = nw.feeding(nex, pop, popeps_a, dmulti)
        f1 = nw.pending.pop()[1]
        worst_feed = max(worst_feed, _rel(f1, (1.0 - dmulti) * f0))
        assert _rel(f1, f0) > 0.0  # the factor is not a no-op on these bins
        dref, mref, _, _lo = ref[id(nw)].feeding(nex, torch.as_tensor(pop), popeps_a,
                                                 dmulti=dmulti)
        got, want = cut[0][0], dref[0].numpy()
        if got is not None:
            k = got.shape[1]
            worst_dp = max(worst_dp, _rel(got, want[: got.shape[0], :k]),
                           _rel(cut[1][0], mref[0].numpy()[: got.shape[0]]))
        del base
        n_bins += 1
    assert n_bins >= 20, n_bins
    assert worst_feed <= 1e-15, worst_feed
    assert worst_dp <= 1e-13, worst_dp
