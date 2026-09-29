"""AME + NUBASE join -> validated Nuclide records -> feature table; mass-model baselines."""

import json
import math

import numpy as np
import pyarrow.parquet as pq
import pytest

from data.ingest.ame import AME_DIR, load_ame
from data.ingest.build_nuclides import build_feature_table, build_nuclide_records, summary
from data.ingest.nubase import NUBASE_FILE, load_nubase
from data.schema.nuclide import Nuclide
from physics.features import FEATURE_NAMES
from physics.massmodels import MODELS, baseline_rms, load_all
from physics.massmodels.dz import dz10_binding_mev, dz10_mass_excess_kev
from physics.massmodels.paths import BRUSLIB, DZ_DIR, RIPL_MASSES, WS4_DIR

pytestmark = pytest.mark.skipif(
    not (AME_DIR.exists() and NUBASE_FILE.exists()), reason="raw AME/NUBASE not downloaded"
)
needs_models = pytest.mark.skipif(
    not all(p.exists() for p in (RIPL_MASSES, BRUSLIB, WS4_DIR, DZ_DIR)),
    reason="raw mass-model tables not downloaded",
)


@pytest.fixture(scope="module")
def ame():
    return load_ame()


@pytest.fixture(scope="module")
def records(ame):
    return build_nuclide_records(ame, load_nubase())


@pytest.fixture(scope="module")
def models():
    return load_all()


def by_key(records, Z, N, iso=0):
    r = [x for x in records if x.key == (Z, N, iso)]
    assert len(r) == 1
    return r[0]


def test_records_validate_and_are_unique(records):
    assert all(isinstance(r, Nuclide) for r in records)
    keys = [r.key for r in records]
    assert len(keys) == len(set(keys))
    assert keys == sorted(keys)
    assert 5500 <= len(records) <= 6200


def test_ground_state_counts(records):
    gs = [r for r in records if r.iso == 0]
    assert 3400 <= len(gs) <= 3700
    with_mass = [r for r in gs if r.mass_excess_kev is not None]
    assert len(with_mass) == len(gs)  # every NUBASE ground state has an AME mass in 2020
    meas = [r for r in with_mass if not r.mass_excess_kev.extrapolated]
    assert 2400 <= len(meas) <= 2700
    assert 700 <= len(with_mass) - len(meas) <= 1100
    assert 240 <= sum(r.is_stable for r in gs) <= 300


def test_pb208_record(records):
    r = by_key(records, 82, 126)
    assert r.nuclide_id == "Z082N126M0" and r.A == 208 and r.symbol == "Pb"
    assert r.mass_excess_kev.value == pytest.approx(-21748.519, abs=0.001)
    assert r.mass_excess_kev.sigma == pytest.approx(1.148, abs=0.001)
    assert r.binding_energy_per_a_kev.value == pytest.approx(7867.453, abs=0.001)
    assert r.sn_kev.value == pytest.approx(7367.8686, abs=0.001)
    assert r.is_stable and r.log10_half_life_s is None
    assert r.spin == 0 and r.parity == 1
    assert r.discovery_year == 1927
    m = by_key(records, 82, 126, iso=1)
    assert m.excitation_energy_kev.value == pytest.approx(4895.23, abs=0.01)
    assert m.mass_excess_kev.value == pytest.approx(-16853.3, abs=0.1)
    assert [b.mode for b in m.decay_modes] == ["IT"]


def test_fe56_and_u235_records(records):
    fe = by_key(records, 26, 30)
    assert fe.mass_excess_kev.value == pytest.approx(-60607.163, abs=0.001)
    assert fe.is_stable
    u = by_key(records, 92, 143)
    assert u.mass_excess_kev.value == pytest.approx(40918.782, abs=0.001)
    assert u.sn_kev.value == pytest.approx(5297.4952, abs=0.001)
    assert u.sp_kev.value == pytest.approx(6709.0586, abs=0.001)
    assert u.spin == 3.5 and u.parity == -1
    assert u.log10_half_life_s.value == pytest.approx(
        math.log10(704e6 * 365.2422 * 86400), abs=1e-6
    )


def test_u238_and_co60_half_lives(records):
    y = 365.2422 * 86400
    u = by_key(records, 92, 146)
    assert 10**u.log10_half_life_s.value / y == pytest.approx(4.468e9, rel=0.01)
    co = by_key(records, 27, 33)
    assert 10**co.log10_half_life_s.value / y == pytest.approx(5.27, rel=0.001)
    assert co.decay_modes[0].mode == "B-" and co.decay_modes[0].branching == 1.0


def test_pn_from_delayed_neutron_branch(records):
    he8 = by_key(records, 2, 6)  # 8He: B-n=16 1
    assert he8.pn is not None and he8.pn.value == pytest.approx(0.16)
    assert he8.pn.sigma == pytest.approx(0.01)


def test_branchings_are_fractions(records):
    for r in records:
        for b in r.decay_modes:
            if b.branching is not None:
                assert 0.0 <= b.branching <= 1.0


def test_arrow_round_trip(records, tmp_path):
    path = Nuclide.write_parquet(records[:200], tmp_path / "n.parquet")
    back = Nuclide.read_parquet(path)
    assert back == records[:200]


@needs_models
def test_feature_table(records, models):
    t = build_feature_table(records, models)
    names = t.column_names
    assert names[0] == "nuclide_id"
    for f in FEATURE_NAMES:
        assert f in names
    for m in MODELS:
        assert f"me_{m}_kev" in names
    assert "beta2_frdm2012" in names and "beta2_ws4" in names
    assert "target_mass_excess_kev" in names and "target_is_extrapolated" in names
    n_gs = sum(r.iso == 0 and r.mass_excess_kev is not None for r in records)
    assert t.num_rows == n_gs
    sources = json.loads(t.schema.metadata[b"column_sources"])
    assert set(sources) == set(names)
    assert sources["me_frdm2012_kev"].endswith("mass-frdm12.dat")
    df = t.to_pandas().set_index("nuclide_id")
    pb = df.loc["Z082N126M0"]
    assert pb["me_frdm2012_kev"] == pytest.approx(-20920.0)
    assert pb["me_ws4_kev"] == pytest.approx(-21268.0, abs=1.0)
    assert pb["me_hfb24_kev"] == pytest.approx(-21940.0)
    assert pb["target_mass_excess_kev"] == pytest.approx(-21748.519, abs=0.001)
    assert not pb["target_is_extrapolated"]
    assert pb["Z_is_magic"] == 1 and pb["N_is_magic"] == 1
    # light nuclei fall outside every table -> NaN, not an error
    assert math.isnan(df.loc["Z001N000M0", "me_frdm2012_kev"])
    assert df["me_frdm2012_kev"].notna().sum() > 3000


@needs_models
def test_feature_parquet_round_trip(records, models, tmp_path):
    t = build_feature_table(records, models)
    pq.write_table(t, tmp_path / "f.parquet")
    back = pq.read_table(tmp_path / "f.parquet")
    assert back.num_rows == t.num_rows
    assert b"column_sources" in back.schema.metadata


@needs_models
def test_mass_model_baseline_rms(ame, models):
    rms = baseline_rms(ame, models).set_index("model")
    # BLUEPRINT §3.3: 300-600 keV for pure theory; the readmes in RIPL-4 quote the exact
    # numbers on the same 2457-nuclide set.
    assert rms.loc["ws4", "n"] >= 2300
    bounds = {
        "ws4": (250, 350),  # 295
        "frdm2012": (550, 660),  # 606
        "hfb24": (500, 620),  # 549 on AME2012
        "hfb27": (470, 570),  # 518
        "hfb31": (500, 650),  # 561 on AME2012
        "dz28": (330, 500),
        "dz10": (450, 700),  # 506 on 1810 masses (1996); ~610 on AME2020
        "ws4_rbf": (140, 250),
        "bskg3": (550, 700),  # 631
        "d1m": (700, 900),  # 798
    }
    for model, (lo, hi) in bounds.items():
        v = rms.loc[model, "rms_kev"]
        assert lo <= v <= hi, f"{model}: {v:.1f} keV outside [{lo}, {hi}]"
        assert abs(rms.loc[model, "mean_kev"]) < 150, model


def test_dz10_port_sanity(ame):
    # 208Pb: binding ~1636.4 MeV; the DZ10 formula should be within ~2 MeV.
    b = dz10_binding_mev(126, 82)
    assert b == pytest.approx(1636.43, abs=2.0)
    me = dz10_mass_excess_kev([82, 26], [126, 30])
    assert me[0] == pytest.approx(-21748.5, abs=2000)
    assert me[1] == pytest.approx(-60607.2, abs=2000)
    assert math.isnan(dz10_mass_excess_kev([1], [0])[0])
    # unbiased across the measured chart (a mis-ported term shows up as a large mean shift)
    meas = ame[(~ame["mass_excess_extrapolated"]) & (ame["Z"] >= 8) & (ame["N"] >= 8)]
    d = (
        dz10_mass_excess_kev(meas["Z"].to_numpy(), meas["N"].to_numpy())
        - meas["mass_excess_kev"].to_numpy()
    )
    assert abs(float(np.mean(d))) < 100
    assert float(np.sqrt(np.mean(d**2))) < 800


@needs_models
def test_summary_prints(records, models, ame):
    text = summary(records, build_feature_table(records, models), baseline_rms(ame, models))
    assert "ground states" in text and "frdm2012" in text
