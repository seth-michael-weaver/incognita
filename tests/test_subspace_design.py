"""D3: the sweep design restricted to the identifiable parameters.

The point of the restriction is that the recorded `p_<name>` columns must be what TALYS
actually ran -- which is where `omit_params` differs: it drops the keyword but leaves the
sampled value in the design, so the surrogate would see a column that looks like a knob and
moves nothing.
"""
from __future__ import annotations

import numpy as np

from physics.talys import params as P
from physics.talys import sweep as S

D3 = ["ld_a_factor", "gsf_norm", "gsf_width_factor"]


def test_naming_no_parameters_reproduces_the_old_design():
    """Every sweep in the repository's history must be unaffected, bit for bit."""
    for active in (None, []):
        assert np.array_equal(S.subspace_design(4, 6, 7, active), S.lhs_design(4, 6, 7))


def test_naming_every_parameter_reproduces_the_old_design():
    assert np.array_equal(S.subspace_design(3, 5, 1, list(P.PARAM_NAMES)),
                          S.lhs_design(3, 5, 1))


def test_inactive_dimensions_hold_the_talys_default():
    d = S.subspace_design(5, 8, 3, D3)
    default = P.default_coded_vector()
    active = [P.PARAM_INDEX[a] for a in D3]
    inactive = [i for i in range(P.N_PARAMS) if i not in active]
    assert np.allclose(d[:, inactive], default[inactive])
    # and the active ones actually move, over most of their range
    lo, hi = P.coded_bounds()
    spread = np.ptp(d[:, active], axis=0)
    assert (spread > 0.5 * (hi[active] - lo[active])).all(), spread


def test_decoded_defaults_are_the_physical_defaults():
    """A pinned dimension must decode to factor 1 / shift 0 / the default model."""
    row = P.decode(S.subspace_design(2, 3, 11, D3)[0])
    assert row["ldmodel"] == P.TALYS_DEFAULTS["ldmodel"]
    assert row["strength"] == P.TALYS_DEFAULTS["strength"]
    for name in ("omp_rv_factor", "omp_av_factor", "omp_w1_factor", "omp_v1_factor",
                 "ld_spincut_factor"):
        assert abs(row[name] - 1.0) < 1e-9, name
    for name in ("ld_pshift_mev", "gsf_eshift_mev"):
        assert abs(row[name]) < 1e-9, name


def test_unknown_parameter_is_an_error_not_a_silent_pin():
    import pytest
    with pytest.raises(ValueError, match="unknown parameter"):
        S.subspace_design(2, 2, 0, ["gsf_with_a_typo"])


def test_empty_design_keeps_its_shape():
    assert S.subspace_design(0, 0, 1, D3).shape == (0, P.N_PARAMS)
