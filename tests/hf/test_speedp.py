"""SPEEDP: the scheduling machinery the dump-free arm uses to skip work it is not asked for.

None of it may change a number. What it CAN do wrong is serve a narrowed answer to a caller that
asked for the whole grid, so that is what these test.
"""

from __future__ import annotations

import pytest

from physics.hf.preeq import chain as PC

DECLARED = (0.001, 0.1, 1.0, 5.0, 14.0, 18.0, 20.0)


@pytest.fixture(autouse=True)
def _clean_registry():
    yield
    PC.set_energy_subset(26, 56, DECLARED, None)


def test_lazy_energy_map_computes_only_what_is_looked_up():
    seen = []
    m = PC._ByEnergy((1.0, 2.0, 3.0), lambda k: seen.append(k) or k * 10)
    assert len(m) == 3 and list(m) == [1.0, 2.0, 3.0] and seen == []
    assert m[2.0] == 20.0 and m[2.0] == 20.0  # memoised: one evaluation
    assert seen == [2.0]
    assert m.get(9.0) is None and seen == [2.0]
    with pytest.raises(KeyError):
        m[9.0]


def test_energy_subset_registers_and_deregisters():
    assert PC.energy_subset(26, 56, DECLARED) is None
    PC.set_energy_subset(26, 56, DECLARED, (5.0, 18.0))
    assert PC.energy_subset(26, 56, DECLARED) == (5.0, 18.0)
    PC.set_energy_subset(26, 56, DECLARED, None)
    assert PC.energy_subset(26, 56, DECLARED) is None


def test_a_subset_covering_the_whole_grid_is_not_a_subset():
    """The full-grid run E2E scores must neither trim nor drop a cache."""
    PC.set_energy_subset(26, 56, DECLARED, DECLARED)
    assert PC.energy_subset(26, 56, DECLARED) is None


def test_a_narrowed_subset_drops_the_caches_that_depend_on_it():
    from physics.hf.compound import pop_reference
    from physics.hf.emission import feed_reference

    PC.set_energy_subset(26, 56, DECLARED, (18.0,))
    pop_reference._preeq.cache_info()  # exists and is an lru_cache
    PC.set_energy_subset(26, 56, DECLARED, (5.0, 18.0))
    assert pop_reference._preeq.cache_info().currsize == 0
    assert feed_reference._preeq_of.cache_info().currsize == 0


def test_a_subset_narrows_the_exciton_model_and_nothing_else():
    """`_preeq`'s energy list follows the registered subset; the rows it keeps are the same rows."""
    from physics.hf.compound.pop_reference import _preeq

    full, res_full, _o = _preeq("Fe056", declared=DECLARED)
    assert full == PC.preeq_energies(26, 56, DECLARED)
    PC.set_energy_subset(26, 56, DECLARED, (18.0,))
    sub, res_sub, _o = _preeq("Fe056", declared=DECLARED)
    assert sub == [18.0]
    i = full.index(18.0)
    for key in ("xspreeqsum", "xspreeqdiscsum"):
        assert float(res_sub[key][0]) == float(res_full[key][i])


def test_a_subset_with_no_preequilibrium_energy_is_an_empty_result():
    """Every energy below `epreeq`: `preeq.f90` never runs, and the callers' None branch is taken."""
    from physics.hf.compound.pop_reference import _preeq

    PC.set_energy_subset(26, 56, DECLARED, (0.001,))
    energies, res, options = _preeq("Fe056", declared=DECLARED)
    assert energies == [] and dict(res) == {} and options is not None


def test_lend_cascade_refuses_a_cascade_carrying_overrides():
    from physics.hf.emission.feeding import Cascade

    cas = Cascade(26, 56, 20.0, energies=DECLARED)
    key = (26, 56, 20.0, 1)
    PC._LENT.pop(key, None)
    cas.diff_params = True
    PC.lend_cascade(cas)
    assert key not in PC._LENT
    cas.diff_params = False
    PC.lend_cascade(cas)
    assert PC._LENT[key]() is cas
    PC._LENT.pop(key, None)
