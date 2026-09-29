"""Round-trip tests: Pydantic -> Arrow -> Parquet -> Pydantic for all five records,
plus the canonical nuclide key and the common energy grid."""

from __future__ import annotations

import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq
import pytest
from pydantic import ValidationError

from data.schema import (
    RECORD_TYPES,
    DataBlock,
    Datum,
    DecayBranch,
    EvaluatedXS,
    FissionBarrier,
    Lorentzian,
    Measurement,
    NamedParam,
    Nuclide,
    NuclideKey,
    Param,
    QuantityType,
    ReactionSF,
    Source,
    SplitKind,
    SplitManifest,
    SplitRole,
    StructureParams,
    from_arrow,
    nuclide_id,
    nuclide_id_from_za,
    parse_nuclide_id,
    read_parquet,
    to_arrow,
    write_parquet,
)
from physics import grid

# --------------------------------------------------------------------------- fixtures


def make_nuclides() -> list[Nuclide]:
    fe56 = Nuclide(
        Z=26,
        N=30,
        symbol="Fe",
        mass_excess_kev=Datum(value=-60605.4, sigma=0.3),
        binding_energy_per_a_kev=Datum(value=8790.36, sigma=0.01),
        sn_kev=Datum(value=11197.1, sigma=0.3),
        s2n_kev=Datum(value=20496.7, sigma=0.4),
        sp_kev=Datum(value=10183.6, sigma=0.4),
        s2p_kev=Datum(value=18262.9, sigma=0.5),
        spin=0.0,
        parity=1,
        is_stable=True,
        decay_modes=[DecayBranch(mode="IS", branching=0.91754, sigma=0.00036)],
        charge_radius_fm=Datum(value=3.7377, sigma=0.0016),
        beta2=Datum(value=0.239, sigma=0.011),
        source_version="AME2020+NUBASE2020",
    )
    # A far-from-stability, extrapolated nuclide with a beta-delayed neutron branch.
    sn132ish = Nuclide(
        Z=50,
        N=90,
        mass_excess_kev=Datum(value=-40000.0, sigma=500.0, extrapolated=True),
        spin=None,
        parity=None,
        spin_parity_tentative=True,
        log10_half_life_s=Datum(value=-1.2, sigma=0.3),
        decay_modes=[
            DecayBranch(mode="B-", branching=1.0),
            DecayBranch(mode="B-n", branching=0.3, sigma=0.1, qualifier="~"),
        ],
        pn=Datum(value=0.3, sigma=0.1),
        p2n=Datum(value=0.01, sigma=0.005),
    )
    # An isomer.
    am242m = Nuclide(
        Z=95,
        N=147,
        iso=1,
        excitation_energy_kev=Datum(value=48.60, sigma=0.05),
        spin=5.0,
        parity=-1,
        log10_half_life_s=Datum(value=9.65, sigma=0.01),
        decay_modes=[
            DecayBranch(mode="IT", branching=0.9955),
            DecayBranch(mode="A", branching=0.0045),
        ],
    )
    return [fe56, sn132ish, am242m]


def make_structure() -> list[StructureParams]:
    m = Source.MEASURED
    s = Source.SYSTEMATICS
    full = StructureParams(
        Z=92,
        N=146,
        ld_model="BSFG",
        ld_a=Param(value=27.4, sigma=1.1, source=m),
        ld_delta_mev=Param(value=0.55, sigma=0.2, source=s),
        ld_spin_cutoff=Param(value=6.1, source=s),
        n_discrete_levels=40,
        level_cutoff_mev=1.2,
        d0_ev=Param(value=20.3, sigma=0.4, source=m),
        d1_ev=Param(value=6.9, sigma=0.8, source=m),
        s0=Param(value=1.08e-4, sigma=0.1e-4, source=m),
        s1=Param(value=1.7e-4, sigma=0.3e-4, source=s),
        gamma_gamma_mev=Param(value=23.4, sigma=0.8, source=m),
        gsf_model="GLO",
        gdr=[
            Lorentzian(
                energy_mev=Param(value=10.9, sigma=0.1, source=m),
                width_mev=Param(value=2.3, sigma=0.2, source=m),
                sigma_mb=Param(value=290.0, sigma=15.0, source=m),
            ),
            Lorentzian(
                energy_mev=Param(value=14.0, sigma=0.1, source=m),
                width_mev=Param(value=4.5, sigma=0.3, source=m),
                sigma_mb=Param(value=360.0, sigma=20.0, source=m),
            ),
        ],
        upbend_c=Param(value=1e-8, source=s),
        omp_form="KD03",
        omp=[
            NamedParam(name="rv", value=1.26, sigma=0.01, source=s),
            NamedParam(name="av", value=0.62, source=s),
            NamedParam(name="v1", value=51.0, sigma=0.5, source=m),
        ],
        fission_barriers=[
            FissionBarrier(
                index=1,
                height_mev=Param(value=6.0, sigma=0.2, source=m),
                curvature_mev=Param(value=0.9, source=s),
            ),
            FissionBarrier(index=2, height_mev=Param(value=5.5, sigma=0.3, source=m)),
        ],
        source_version="RIPL-3",
    )
    sparse = StructureParams(Z=26, N=31, d0_ev=Param(value=25000.0, sigma=3000.0, source=m))
    return [full, sparse]


def make_measurements() -> list[Measurement]:
    e = np.logspace(3, 6, 12)
    xs = 0.1 / np.sqrt(e / 1e3)
    abs_meas = Measurement(
        entry="10047",
        subentry="10047002",
        target_z=92,
        target_a=235,
        projectile="n",
        reaction="(92-U-235(N,F),,SIG)",
        sf=ReactionSF(sf1="92-U-235", sf2="N", sf3="F", sf6="SIG", sf9="EXP"),
        mt=18,
        quantity=QuantityType.CROSS_SECTION,
        energy_ev=e,
        energy_sigma_ev=0.02 * e,
        original=DataBlock(values=xs, stat_sigma=0.03 * xs, sys_sigma=0.02 * xs, units="b"),
        year=1971,
        facility="LINAC",
        detector="FISCH",
        first_author="R.Gwin",
        doi="10.13182/NSE71-A19047",
        exfor_version="2025-06-01",
    )
    ratio = Measurement(
        entry="12345",
        subentry="12345003",
        pointer="1",
        target_z=79,
        target_a=197,
        projectile="n",
        reaction="((79-AU-197(N,G)79-AU-198,,SIG)/(92-U-235(N,F),,SIG))",
        sf=ReactionSF(sf1="79-AU-197", sf2="N", sf3="G", sf4="79-AU-198", sf6="SIG"),
        mt=102,
        quantity=QuantityType.RATIO,
        energy_ev=[1e4, 3e4, 1e5],
        original=DataBlock(values=[0.5, 0.4, 0.3], stat_sigma=[0.02, 0.02, 0.02], units="NO-DIM"),
        renormalized=DataBlock(
            values=[0.6, 0.48, 0.36],
            stat_sigma=[0.024, 0.024, 0.024],
            sys_sigma=[0.01, 0.01, 0.01],
            units="b",
            standards_version="IAEA Neutron Standards 2017",
        ),
        monitor="(92-U-235(N,F),,SIG)",
        year=1985,
        outdated=True,
    )
    natural = Measurement(
        entry="20001",
        subentry="20001005",
        target_z=26,
        target_a=0,
        projectile="n",
        reaction="(26-FE-0(N,TOT),,SIG)",
        mt=1,
        energy_ev=[1e6, 2e6],
        original=DataBlock(values=[3.1, 3.4]),
    )
    return [abs_meas, ratio, natural]


def make_evaluated() -> list[EvaluatedXS]:
    e = grid.ENERGY_GRID_EV
    capture = EvaluatedXS(
        library="ENDF/B-VIII.1",
        Z=79,
        N=118,
        mt=102,
        values_b=98.7 * np.sqrt(0.0253 / e),
        resolved_upper_ev=5e3,
        unresolved_upper_ev=2e5,
        resonance_ref="staging/resonances.parquet#ENDF/B-VIII.1/Z079N118M0",
        covariance_ref="staging/cov.zarr/ENDF-B-VIII.1/Z079N118M0/MT102",
    )
    n2n = EvaluatedXS(
        library="TENDL-2023",
        library_version="2023-12",
        Z=79,
        N=118,
        mt=16,
        temperature_k=293.6,
        values_b=np.where(e > 8.1e6, 2.0, 0.0),
        threshold_ev=8.1e6,
    )
    return [capture, n2n]


def make_splits() -> list[SplitManifest]:
    return [
        SplitManifest(
            name="nuclide-holdout-v1",
            kind=SplitKind.NUCLIDE,
            role=SplitRole.TEST,
            seed=42,
            members=[nuclide_id(26, 30), nuclide_id(50, 82), nuclide_id(92, 146)],
            params={"fraction": "0.1", "stratify": "mass_region"},
            version="v0.1",
        ),
        SplitManifest(
            name="time-2012",
            kind=SplitKind.TIME,
            role=SplitRole.TRAIN,
            members=["10047002", "12345003"],
            params={"year": "2012"},
            description="train on measurements published before 2012",
        ),
        SplitManifest(name="icsbep", kind=SplitKind.INTEGRAL, role=SplitRole.TEST),
    ]


FACTORIES = {
    Nuclide: make_nuclides,
    StructureParams: make_structure,
    Measurement: make_measurements,
    EvaluatedXS: make_evaluated,
    SplitManifest: make_splits,
}


# --------------------------------------------------------------------------- round trips


@pytest.mark.parametrize("record_type", RECORD_TYPES, ids=lambda t: t.__name__)
def test_roundtrip_pydantic_arrow_parquet(record_type, tmp_path):
    records = FACTORIES[record_type]()
    assert records, "factory must produce at least one record"

    table = record_type.to_arrow(records)
    assert isinstance(table, pa.Table)
    assert table.schema.equals(record_type.ARROW_SCHEMA)
    assert table.num_rows == len(records)

    path = tmp_path / f"{record_type.__name__}.parquet"
    pq.write_table(table, path)
    back = record_type.from_arrow(pq.read_table(path))

    assert back == records
    # A second pass through Arrow must be byte-identical: no drift from filled-in defaults.
    assert record_type.to_arrow(back).equals(table)


@pytest.mark.parametrize("record_type", RECORD_TYPES, ids=lambda t: t.__name__)
def test_module_level_helpers(record_type, tmp_path):
    records = FACTORIES[record_type]()
    table = to_arrow(records)
    assert from_arrow(table, record_type) == records
    path = write_parquet(records, tmp_path / "sub" / "t.parquet")
    assert read_parquet(path, record_type) == records
    assert record_type.read_parquet(path) == records


def test_schema_columns_match_fields():
    for record_type in RECORD_TYPES:
        assert list(record_type.ARROW_SCHEMA.names) == list(record_type.model_fields)


def test_empty_table_roundtrip():
    for record_type in RECORD_TYPES:
        table = record_type.to_arrow([])
        assert table.num_rows == 0
        assert table.schema.equals(record_type.ARROW_SCHEMA)
        assert record_type.from_arrow(table) == []


def test_from_arrow_rejects_extra_columns():
    table = SplitManifest.to_arrow(make_splits()).append_column("junk", pa.array([1, 2, 3]))
    with pytest.raises(ValueError, match="unexpected columns"):
        SplitManifest.from_arrow(table)


def test_to_arrow_rejects_wrong_type():
    with pytest.raises(TypeError):
        Nuclide.to_arrow(make_splits())


# --------------------------------------------------------------------------- record semantics


def test_nuclide_derived_keys_and_validation():
    n = Nuclide(Z=26, N=30)
    assert (n.A, n.nuclide_id, n.key) == (56, "Z026N030M0", (26, 30, 0))
    assert Nuclide(Z=26, N=30, A=56, nuclide_id="Z026N030M0") == n
    with pytest.raises(ValidationError):
        Nuclide(Z=26, N=30, A=57)
    with pytest.raises(ValidationError):
        Nuclide(Z=26, N=30, nuclide_id="Z026N031M0")
    with pytest.raises(ValidationError):
        Nuclide(Z=0, N=0)
    with pytest.raises(ValidationError):
        Nuclide(Z=26, N=30, spin=0.3)
    with pytest.raises(ValidationError):
        Nuclide(Z=26, N=30, parity=2)
    with pytest.raises(ValidationError):
        Nuclide(Z=26, N=30, is_stable=True, log10_half_life_s=Datum(value=1.0))
    with pytest.raises(ValidationError):
        Nuclide(Z=26, N=30, pn=Datum(value=1.5))
    with pytest.raises(ValidationError):
        DecayBranch(mode="B-", branching=50.0)  # percent, not fraction
    with pytest.raises(ValidationError):
        DecayBranch(mode="nonsense")
    with pytest.raises(ValidationError):
        Datum(value=1.0, sigma=-1.0)


def test_structure_validation():
    lor = Lorentzian(
        energy_mev=Param(value=15.0), width_mev=Param(value=5.0), sigma_mb=Param(value=300.0)
    )
    with pytest.raises(ValidationError):
        StructureParams(Z=26, N=30, gdr=[lor, lor, lor])
    with pytest.raises(ValidationError):
        StructureParams(
            Z=92,
            N=146,
            fission_barriers=[
                FissionBarrier(index=1, height_mev=Param(value=6.0)),
                FissionBarrier(index=1, height_mev=Param(value=5.0)),
            ],
        )
    with pytest.raises(ValidationError):
        Param(value=1.0, source="guess")
    assert StructureParams(Z=26, N=30).key == (26, 30, 0)


def test_measurement_validation():
    base = dict(entry="1", subentry="1001", target_z=26, target_a=56, projectile="n", reaction="x")
    m = Measurement(**base, energy_ev=[1.0, 2.0], original=DataBlock(values=[1.0, 2.0]))
    assert m.target_id == nuclide_id_from_za(26, 56) == "Z026N030M0"
    assert m.n_points == 2 and m.quantity == "cross_section"
    with pytest.raises(ValidationError):
        Measurement(**base, energy_ev=[1.0, 2.0], original=DataBlock(values=[1.0]))
    with pytest.raises(ValidationError):
        Measurement(
            **base, energy_ev=[1.0], energy_sigma_ev=[1.0, 2.0], original=DataBlock(values=[1.0])
        )
    with pytest.raises(ValidationError):
        DataBlock(values=[1.0, 2.0], stat_sigma=[0.1])
    with pytest.raises(ValidationError):  # renormalized data must name its standards
        Measurement(
            **base,
            energy_ev=[1.0],
            original=DataBlock(values=[1.0]),
            renormalized=DataBlock(values=[1.1]),
        )
    with pytest.raises(ValidationError):  # A < Z
        Measurement(
            entry="1",
            subentry="1",
            target_z=26,
            target_a=20,
            projectile="n",
            reaction="x",
            energy_ev=[1.0],
            original=DataBlock(values=[1.0]),
        )
    assert (
        Measurement(
            **{**base, "target_a": 0}, energy_ev=[1.0], original=DataBlock(values=[1.0])
        ).target_id
        is None
    )


def test_evaluated_validation():
    with pytest.raises(ValidationError, match="3000 points"):
        EvaluatedXS(library="L", Z=1, N=0, mt=1, values_b=[1.0, 2.0])
    with pytest.raises(ValidationError, match="negative"):
        EvaluatedXS(library="L", Z=1, N=0, mt=1, values_b=-np.ones(grid.N_POINTS))
    ok = EvaluatedXS(library="L", Z=1, N=0, mt=1, values_b=np.ones(grid.N_POINTS))
    assert ok.grid_id == grid.GRID_ID
    assert ok.energy_ev is grid.ENERGY_GRID_EV
    assert ok.values().shape == (grid.N_POINTS,)
    # A custom grid is allowed if labelled as such.
    custom = EvaluatedXS(library="L", Z=1, N=0, mt=1, grid_id="custom-3pt", values_b=[1, 2, 3])
    with pytest.raises(ValueError):
        _ = custom.energy_ev


def test_split_validation():
    with pytest.raises(ValidationError):
        SplitManifest(name="s", kind="nuclide", role="test", members=["a", "a"])
    with pytest.raises(ValidationError):
        SplitManifest(name="s", kind="integral", role="train")
    with pytest.raises(ValidationError):
        SplitManifest(name="s", kind="random", role="test")


# --------------------------------------------------------------------------- keys


def test_nuclide_id_convention():
    assert nuclide_id(26, 30) == "Z026N030M0"
    assert nuclide_id(95, 147, 1) == "Z095N147M1"
    assert nuclide_id_from_za(92, 235) == nuclide_id(92, 143)
    assert parse_nuclide_id("Z095N147M1") == NuclideKey(95, 147, 1)
    assert parse_nuclide_id(nuclide_id(1, 0)) == (1, 0, 0)
    k = NuclideKey(26, 30)
    assert (k.A, k.id) == (56, "Z026N030M0")
    # Keys sort by Z, then N, then isomer.
    ids = [nuclide_id(26, 30), nuclide_id(26, 29), nuclide_id(8, 8), nuclide_id(26, 30, 1)]
    assert sorted(ids) == [
        nuclide_id(8, 8),
        nuclide_id(26, 29),
        nuclide_id(26, 30),
        nuclide_id(26, 30, 1),
    ]
    for bad in [(0, 0, 0), (-1, 5, 0), (5, 5, -1), (1000, 0, 0)]:
        with pytest.raises(ValueError):
            nuclide_id(*bad)
    for bad_key in ["Fe56", "Z26N30M0", "Z026N030", ""]:
        with pytest.raises(ValueError):
            parse_nuclide_id(bad_key)


# --------------------------------------------------------------------------- grid


def test_grid_endpoints_and_shape():
    g = grid.ENERGY_GRID_EV
    assert g.shape == (3000,) and g.dtype == np.float64
    assert g[0] == 1e-5
    assert g[-1] == 20e6
    assert np.all(np.diff(g) > 0)
    # Log-spaced: constant ratio between neighbours.
    ratios = g[1:] / g[:-1]
    assert np.allclose(ratios, ratios[0], rtol=1e-9)
    assert np.array_equal(grid.energy_grid(), g)
    assert not g.flags.writeable
    assert grid.N_POINTS == 3000 and grid.E_MIN_EV == 1e-5 and grid.E_MAX_EV == 20e6
    assert np.allclose(grid.LOG10_ENERGY_GRID, np.log10(g))


def test_grid_function_arguments():
    g = grid.energy_grid(11, 1.0, 1e10)
    assert g.shape == (11,) and g[0] == 1.0 and g[-1] == 1e10
    assert np.allclose(g, 10.0 ** np.arange(11))
    with pytest.raises(ValueError):
        grid.energy_grid(1)
    with pytest.raises(ValueError):
        grid.energy_grid(10, 5.0, 1.0)


def test_grid_nearest_index_and_interp():
    assert grid.nearest_index(1e-5) == 0
    assert grid.nearest_index(20e6) == grid.N_POINTS - 1
    assert grid.nearest_index(grid.ENERGY_GRID_EV[1234]) == 1234
    assert grid.nearest_index([1e-5, 20e6]).tolist() == [0, grid.N_POINTS - 1]
    # 1/v interpolated in log-log is exact on the grid.
    e = np.array([1e-3, 1.0, 1e3, 1e7, 3e7])
    y = np.sqrt(0.0253 / e)
    out = grid.interp_to_grid(e, y, log_y=True)
    inside = (grid.ENERGY_GRID_EV >= e[0]) & (grid.ENERGY_GRID_EV <= e[-1])
    assert np.allclose(out[inside], np.sqrt(0.0253 / grid.ENERGY_GRID_EV[inside]), rtol=1e-10)
    assert np.all(out[~inside] == 0.0)
    # Threshold reaction: zero below threshold via fill_value.
    out2 = grid.interp_to_grid(np.array([9e6, 20e6]), np.array([1.0, 2.0]))
    assert out2[0] == 0.0 and out2[-1] == 2.0


# ---------------------------------------------------------------------------------------------
# Conformance of the files the pipeline actually wrote, not of synthetic round-trips.
#
# The round-trip tests above write records and read them back, so they agree with the schema by
# construction and cannot notice drift. What they miss is an ingest that quietly stops emitting a
# column, or emits it with a different type: the synthetic test still passes and every consumer
# that reads with polars instead of ``Model.read_parquet`` sails past it. These check the real
# staging tables against the declared schema, and skip when the data is absent so a checkout
# without it still runs.
#
# Extra columns in the file are allowed on purpose -- ``exfor_capture_Z26-92.parquet`` carries
# four ``renorm_*`` columns the schema does not declare, and ``pq.read_table(schema=...)``
# selects by name, so extras are harmless. A MISSING or RETYPED column is not.

STAGED = [
    ("Nuclide", "staging/nuclides.parquet"),
    ("StructureParams", "staging/structure_params.parquet"),
    ("Measurement", "staging/exfor_capture_Z26-92.parquet"),
    ("Measurement", "staging/exfor_n2n_Z26-92.parquet"),
]


def _norm(t: object) -> str:
    """Arrow type as a string, with the list child's field name normalised away.

    ``pa.list_(pa.float64())`` names its child ``item``; polars writes ``element``. The types are
    identical and interoperable, and comparing ``str(type)`` naively reports every list column in
    the project as a mismatch.
    """
    return str(t).replace("item:", "element:")


@pytest.mark.parametrize("model_name,rel", STAGED)
def test_staged_file_matches_declared_schema(model_name, rel):
    import pathlib

    import data.schema as schema_mod

    repo = pathlib.Path(__file__).resolve().parents[1]
    path = repo / rel
    if not path.exists():
        pytest.skip(f"{rel} not present in this checkout")
    model = getattr(schema_mod, model_name)
    on_disk = {f.name: f.type for f in pq.ParquetFile(path).schema_arrow}
    missing, retyped = [], []
    for field in model.ARROW_SCHEMA:
        if field.name not in on_disk:
            missing.append(field.name)
        elif _norm(on_disk[field.name]) != _norm(field.type):
            retyped.append(f"{field.name}: declared {field.type}, on disk {on_disk[field.name]}")
    assert not missing, f"{rel} is missing declared columns: {missing}"
    assert not retyped, f"{rel} has retyped columns: {retyped}"
