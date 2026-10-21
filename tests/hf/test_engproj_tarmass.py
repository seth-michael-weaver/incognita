"""ENGPROJ3 TARMASSFIX: the incident kinematics use the TARGET mass nucmass(parZ(k0), parN(k0)) (nuclides.f90:239),
not the compound-minus-neutron mass_amu[0, 1]. Stock TALYS-2.25 prints Ecm = 18.973 MeV for t + Fe-56 at 20 MeV
(development notes); n and (by default) p/alpha keep [0, 1]."""
import pytest

from physics.hf.core.constants import PARN, PARZ
from physics.hf.projectile import target_mass_index


@pytest.fixture(autouse=True)
def _clear_projectile_keyed_caches():
    """TMFLEAK: dens_reference's lru_caches (_structure_of, run_grid, ...) are keyed on (Z, A) only and assume ONE projectile
    per process (projectile.py docstring). test_triton_fe56_ecm_matches_stock builds run_grid(26, 56) under INCOGNITA_CPINC=t; left
    cached, the k0=4 structure reached test_etablefix (neutron, same Fe-56) and shifted its global wtable (1.076 != 1.0)."""
    from physics.hf.compound import dens_reference as dr

    def clear():
        for v in vars(dr).values():
            if hasattr(v, "cache_clear"):
                v.cache_clear()

    clear()
    yield
    clear()


@pytest.mark.parametrize("sym,k", [("g", 0), ("d", 3), ("t", 4), ("h", 5)])
def test_engproj_projectiles_use_target(monkeypatch, sym, k):
    monkeypatch.setenv("INCOGNITA_CPINC", sym)
    monkeypatch.delenv("INCOGNITA_TARMASSFIX", raising=False)
    assert target_mass_index() == (PARZ[k], PARN[k])


@pytest.mark.parametrize("sym", ["n", "p", "a"])
def test_legacy_index_with_flag_off(monkeypatch, sym):
    monkeypatch.setenv("INCOGNITA_CPINC", sym)
    monkeypatch.setenv("INCOGNITA_TARMASSFIX", "0")
    assert target_mass_index() == (0, 1)


@pytest.mark.parametrize("flag", [None, "1"])  # default ON (TARMASSFIX_PROMO)
def test_default_fixes_p_alpha(monkeypatch, flag):
    if flag is None:
        monkeypatch.delenv("INCOGNITA_TARMASSFIX", raising=False)
    else:
        monkeypatch.setenv("INCOGNITA_TARMASSFIX", flag)
    for sym, k in (("p", 2), ("a", 6), ("n", 1)):
        monkeypatch.setenv("INCOGNITA_CPINC", sym)
        assert target_mass_index() == (PARZ[k], PARN[k])


def test_triton_fe56_ecm_matches_stock(monkeypatch):
    monkeypatch.setenv("INCOGNITA_CPINC", "t")
    from physics.hf.compound.dens_reference import run_grid
    from physics.hf.core.constants import talys_constants
    from physics.hf.core.grids import incident_kinematics

    from physics.hf.compound.dens_reference import _structure_of

    c = talys_constants()
    rg = run_grid(26, 56, 60.0)
    _structure_of.cache_clear()  # (Z, A)-keyed options of this default-env build must not reach later fitlib tests (ENGPORTPROMO gate T)
    ecm, _ = incident_kinematics(20.0, 4, float(rg.m.mass_amu[target_mass_index()]),
                                 float(rg.m.specmass[c["parZ"][4], c["parN"][4], 4]),
                                 float(rg.m.redumass_amu[c["parZ"][4], c["parN"][4], 4]), rg.options.flagrel)
    assert abs(float(ecm) - 18.973) < 5e-4
