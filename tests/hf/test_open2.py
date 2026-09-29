"""OPEN2: Am-241's K = 5/2+ band head, the DWBA level that was returning exactly zero.

Gate: `docs/results/hf-open2.md` section 3. `weakcoupling.f90:44` never assigns `jcore`/`pcore`
to a level whose `leveltype` is 'R' or 'V', and `directecis.f90:211-212` then writes
`Plevel(2) = cparity(0)`, which `constants.f90:113` defines as a **blank**. ECIS reads the blank
as positive; the port read the 0 as a parity and its natural-parity test threw the level away.

The TALYS numbers pinned here come from a stock `TALYS-2.24` run of Am-241 at 0.5 MeV with
`outdirect y` (`directE0000.500.out`), and from `default__Am241`'s own `nn.L*` files.
"""

from __future__ import annotations

import numpy as np
import pytest
import torch

from tests._data import talys_structure_dir_or_missing

have_structure = pytest.mark.skipif(
    not (talys_structure_dir_or_missing() / "deformation").exists(),
    reason="TALYS structure database absent",
)

# directE0000.500.out, the `cross section` column, by level
TALYS_DIRECT_MB = {1: 109.0730, 2: 24.99940, 3: 3.522580, 4: 870.3540, 5: 1.371700,
                   7: 2.066420, 8: 0.9063030, 10: 0.08165080, 12: 0.05366800}


@have_structure
def test_am241_band_head_is_a_blank_parity_dwba_level():
    """Level 4 keeps `leveltype 'V'` and therefore has no core assigned, but it still carries
    `deform = 0.7` and still goes to ECIS -- as a lambda = 0 form factor with a blank parity."""
    from physics.hf.input.defaults import default_options
    from physics.hf.structure.deformation import deformation
    from physics.hf.structure.levels import discrete_levels
    from physics.hf.structure.masses import masses as get_masses

    o = default_options(95, 241)
    m = get_masses(o)
    lv = discrete_levels(95, 241, o, m)
    d = deformation(95, 241, o, lv, m)
    # deformpar.f90:178 demotes it locally (vibband 1 > maxband 0) but stores 'V'...
    assert d.leveltype[4] == "V"
    # ...and deformpar.f90:205-207's natural-parity branch still gives it the .def value.
    assert float(d.deform[4]) == pytest.approx(0.7, abs=1e-6)
    assert float(d.defpar[1]) == 0.0, "the band arrays stay empty, which is the whole point"


@have_structure
def test_unassigned_core_parity_reaches_ecis_as_positive():
    """`dwba_level_spins` must turn `pcore == 0` into ECIS's blank-read-as-plus, not into 0.

    With 0 the level's `pb != (-1) ** lam` test in `ecis.dwba` rejects it and the DWBA is zero.
    """
    from physics.hf.ecis.weakcore import dwba_level_spins

    class _S:
        Atarget = 241
        nlast = 30
        jdis = np.zeros(40)
        parlev = np.zeros(40)

    jcore = np.zeros(40)
    pcore = np.zeros(40)
    spin, par = dwba_level_spins(_S(), np.array([4]), jcore, pcore, nlev=30)
    assert float(spin[0]) == 0.0           # jcore(4), never assigned
    assert int(par[0]) == 1                # cparity(0) == ' ', and ECIS reads blank as '+'
    lam, pb = int(round(float(spin[0]))), int(par[0])
    assert pb == (-1) ** lam, "must survive ecis/dwba.py's natural-parity test"


@have_structure
def test_am241_direct_matches_talys_level_by_level():
    """The whole discrete direct block at 0.5 MeV, against stock TALYS. Level 4 is 870 of the
    1012 mb and used to be 0; nothing else may move."""
    from physics.hf.preeq.chain import chained_direct

    torch.set_num_threads(2)
    r, _grid = chained_direct(95, 241, (0.5,))[0.5]
    dd = np.asarray(r.xsdirdisc_mb.detach().numpy(), float)
    for i, t in TALYS_DIRECT_MB.items():
        assert dd[i] == pytest.approx(t, rel=2e-2), f"level {i}: {dd[i]} vs {t}"
    assert dd[4] > 800.0, "the band head is the defect; a zero here is the regression"
    assert dd.sum() == pytest.approx(1012.429, rel=2e-2)
