"""The 4-column noise control has to match the block it controls for, or it controls nothing.

`noise_control` (F0) was three columns of uniform hash and was read against blocks of three
and of four columns, the four-column one by multiplying the effect by 4/3. F1 then measured
the same physics by another route and its 95% interval excluded that extrapolation
(docs/results/power/noise-control-verdict.md). `noise_control4` removes the extrapolation by
being the same width as `inelastic_threshold`; these tests pin the properties that claim rests
on, because a control that quietly stopped matching would still produce a number.
"""
import numpy as np
import pytest

from models.stage_c_data import inelastic_features, noise_control4_features

# a fixed, ordinary set of targets -- two dozen is enough to pin structure and keeps the
# staging/levels.parquet read cheap
IDS = [f"Z{z:03d}N{n:03d}M0" for z, n in
       [(26, 30), (26, 32), (28, 30), (28, 32), (40, 50), (40, 51), (42, 56), (47, 60),
        (50, 62), (50, 70), (53, 74), (56, 82), (60, 82), (64, 93), (68, 98), (74, 110),
        (79, 118), (82, 126), (83, 126), (90, 142), (92, 143), (92, 146), (94, 145), (95, 146)]]

# the level scheme and ground states are main-checkout data, not shipped in the public tree
pytestmark = pytest.mark.needs_main("staging/levels.parquet", "staging/nuclides.parquet")


@pytest.fixture(scope="module")
def blocks():
    return inelastic_features(IDS), noise_control4_features(IDS)


def test_same_width(blocks):
    real, noise = blocks
    assert real.shape == noise.shape == (len(IDS), 4)


def test_same_marginal_in_every_column(blocks):
    """A derangement permutes rows, so each column holds exactly the same multiset of values.

    This is the property a moment-matched uniform would not have, and column 1 (R42) is why:
    a few nuclides with a very low first 2+ put it in the hundreds, so a uniform carrying its
    standard deviation would hand every covered row a value the real block gives to three.
    """
    real, noise = blocks
    assert np.array_equal(np.sort(real, axis=0), np.sort(noise, axis=0))


def test_same_sparsity(blocks):
    """Same coverage, column by column: the flags travel with the value they flag."""
    real, noise = blocks
    assert np.array_equal((real != 0).sum(axis=0), (noise != 0).sum(axis=0))
    for value, flag in ((0, 2), (1, 3)):
        assert np.array_equal(noise[:, value] != 0, noise[:, flag] != 0)


def test_carries_no_information_about_its_own_nuclide(blocks):
    """No row keeps its own values, and the two blocks are uncorrelated column by column."""
    real, noise = blocks
    assert not any((real[i] == noise[i]).all() and real[i].any() for i in range(len(IDS)))
    for c in range(4):
        if real[:, c].std() > 0 and noise[:, c].std() > 0:
            assert abs(np.corrcoef(real[:, c], noise[:, c])[0, 1]) < 0.6


def test_fixed_across_calls_and_independent_of_id_order():
    """Both arms and every seed must see the same control, whatever order the ids arrive in."""
    a = noise_control4_features(IDS)
    assert np.array_equal(a, noise_control4_features(IDS))
    b = noise_control4_features(list(reversed(IDS)))[::-1]
    assert np.array_equal(a, b)


def test_reaches_the_bundle_as_four_columns():
    """A block that is not wired through reports a null that is a bug -- see ab_power's guard."""
    from models.stage_c_data import assemble_embedding
    base = np.zeros((len(IDS), 3), np.float32)
    assert assemble_embedding(IDS, base).shape[1] == 3
    assert assemble_embedding(IDS, base, noise_control4=True).shape[1] == 7
