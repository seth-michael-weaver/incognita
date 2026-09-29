"""Stage-B parameter space: keyword existence in the TALYS source, coding round-trips."""

from __future__ import annotations

import numpy as np
import pytest

from physics.talys import params as P


def test_every_keyword_exists_in_talys_source():
    src = P.talys_source_dir()
    if src is None:
        pytest.skip("TALYS source tree not available")
    missing = P.verify_keywords()
    assert missing == [], f"keywords absent from TALYS {src}: {missing}"
    # a made-up keyword must be rejected by the same index
    assert P.keyword_exists_in_source("deltaadjust") is False
    assert P.keyword_exists_in_source("notarealkeyword") is False


def test_default_vector_gives_plain_defaults():
    x = P.default_coded_vector()
    v = P.decode(x)
    assert v["ldmodel"] == 1 and v["strength"] == 9
    for name in P.CONTINUOUS_NAMES:
        if name.endswith("_mev"):
            assert v[name] == 0.0
        else:
            assert v[name] == pytest.approx(1.0)
    kw = P.to_keywords(x, 26, 56)
    assert kw == {"ldmodel": "1", "strength": "9"}


def test_encode_decode_roundtrip_and_bounds():
    rng = np.random.default_rng(0)
    lo, hi = P.coded_bounds()
    x = rng.uniform(lo, hi)
    v = P.decode(x)
    assert v["ldmodel"] in P.LD_MODELS and v["strength"] in P.STRENGTH_MODELS
    assert 0.5 <= v["ld_a_factor"] <= 2.0 and 0.95 <= v["omp_rv_factor"] <= 1.05
    assert -1.0 <= v["ld_pshift_mev"] <= 1.0
    x2 = P.encode(v)
    v2 = P.decode(x2)
    for k in P.PARAM_NAMES:
        assert v2[k] == pytest.approx(v[k], rel=1e-9)


def test_keyword_routing_by_model():
    v = {n: 1.0 for n in P.CONTINUOUS_NAMES}
    v.update({"ld_pshift_mev": 0.3, "gsf_eshift_mev": -0.5, "gsf_norm": 1.5, "ld_a_factor": 0.8})
    # analytic strength + phenomenological LD -> *gradjust / pshiftadjust + legacy y
    kw = P.to_keywords(P.encode({**v, "ldmodel": 3, "strength": 2}), 79, 197)
    lines = P.keyword_lines(kw)
    assert "legacy y" in lines
    assert "sgradjust 79 198 1.5 E1" in lines
    assert any(ln.startswith("egradjust 79 198 ") and ln.endswith(" E1") for ln in lines)
    assert "pshiftadjust 79 198 0.3" in lines and "pshiftadjust 79 197 0.3" in lines
    assert "aadjust 79 198 0.8" in lines and "aadjust 79 197 0.8" in lines
    # tabulated strength + microscopic LD -> ftable/etable + ptableadjust, no legacy
    kw = P.to_keywords(P.encode({**v, "ldmodel": 5, "strength": 9}), 79, 197)
    lines = P.keyword_lines(kw)
    assert "legacy y" not in lines
    assert "ftable 79 198 1.5 E1" in lines and "etable 79 198 -0.5 E1" in lines
    assert "ptableadjust 79 198 0.3" in lines
    # ldmodel 4/6 and strength <= 7 need legacy y
    assert "legacy" in P.to_keywords(P.encode({"ldmodel": 4}), 26, 56)
    assert "legacy" in P.to_keywords(P.encode({"strength": 1}), 26, 56)
    assert P.gamgam_keywords(79, 197, 0.128) == {"gnorm": "y", "gamgam": "79 198 0.128"}
