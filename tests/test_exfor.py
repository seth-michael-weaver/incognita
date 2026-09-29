"""EXFOR ingestion (WP-09): reaction parser, standards scaffolding, a synthetic X4
entry parsed end to end, and one real datum from the capture subset when present."""

from __future__ import annotations

import textwrap
from collections import Counter
from pathlib import Path

import numpy as np
import pyarrow.parquet as pq
import pytest

from data.curate.standards import (
    STANDARDS_VERSION,
    load_standards,
    monitor_ratio,
    ratio_to_absolute,
    standard_for_reaction,
)
from data.ingest.exfor import ExforMeasurement, build_measurements, parse_entry
from data.ingest.exfor_reactions import (
    ReactionParseError,
    mt_for,
    parse_reaction,
    parse_target,
)
from data.schema.measurement import Measurement, QuantityType
from tests._data import STANDARDS

REPO = Path(__file__).resolve().parents[1]
CAPTURE = REPO / "staging" / "exfor_capture_Z26-92.parquet"

# ----------------------------------------------------------------------- reactions


def test_capture_reaction_decomposition() -> None:
    rx = parse_reaction("(26-FE-56(N,G)26-FE-57,,SIG)")
    assert (rx.target.z, rx.target.a, rx.target.iso) == (26, 56, 0)
    assert rx.projectile == "n"
    assert rx.mt == 102
    assert rx.quantity == QuantityType.CROSS_SECTION
    assert rx.sf.sf1 == "26-FE-56"
    assert rx.sf.sf2 == "N"
    assert rx.sf.sf3 == "G"
    assert rx.sf.sf4 == "26-FE-57"
    assert rx.sf.sf5 is None
    assert rx.sf.sf6 == "SIG"
    assert not rx.is_ratio


def test_fission_mt() -> None:
    rx = parse_reaction("(92-U-235(N,F),,SIG)")
    assert rx.mt == 18
    assert rx.target.a == 235
    assert rx.sf.sf4 is None


@pytest.mark.parametrize(
    ("sf3", "mt"),
    [
        ("TOT", 1),
        ("EL", 2),
        ("INL", 4),
        ("2N", 16),
        ("3N", 17),
        ("N+A", 22),
        ("N+P", 28),
        ("P+N", 28),  # order-insensitive
        ("G", 102),
        ("P", 103),
        ("A", 107),
        ("ABS", 27),
        ("X", None),
    ],
)
def test_mt_table(sf3: str, mt: int | None) -> None:
    assert mt_for("N", sf3) == mt


def test_no_mt_for_charged_particles() -> None:
    assert mt_for("P", "G") is None
    assert parse_reaction("(28-NI-58(P,X)27-CO-57,,SIG)").mt is None


def test_ratio_detection() -> None:
    rx = parse_reaction("((92-U-238(N,F),,SIG)/(92-U-235(N,F),,SIG))")
    assert rx.is_ratio
    assert rx.operator == "/"
    assert rx.quantity == QuantityType.RATIO
    assert rx.target.a == 238  # numerator
    assert rx.denominator is not None
    assert rx.denominator.target.a == 235
    # double slash (ratio of ratios) and product/sum combinations
    assert parse_reaction("((14-SI-0(N,X)0-G-0,PAR,DA)//(14-SI-0(N,X)0-G-0,PAR,DA))").is_ratio
    prod = parse_reaction("((26-FE-56(N,EL),,WID,,G)*(26-FE-56(N,G),,WID))")
    assert prod.operator == "*" and not prod.is_ratio


def test_quantity_classification() -> None:
    assert parse_reaction("(79-AU-197(N,G)79-AU-198,,SIG,,MXW)").quantity == QuantityType.INTEGRAL
    assert parse_reaction("(79-AU-197(N,G)79-AU-198,,RI)").quantity == QuantityType.INTEGRAL
    assert parse_reaction("(92-U-238(N,0),,EN)").quantity == QuantityType.RESONANCE_PARAMETER
    assert parse_reaction("(95-AM-243(N,G),,WID)").quantity == QuantityType.RESONANCE_PARAMETER
    assert (
        parse_reaction("(26-FE-56(N,EL)26-FE-56,,DA)").quantity == QuantityType.ANGULAR_DISTRIBUTION
    )
    assert parse_reaction("(26-FE-56(N,INL)26-FE-56,,DE)").quantity == QuantityType.SPECTRUM
    assert parse_reaction("(92-U-235(N,F),,NU)").quantity == QuantityType.OTHER


def test_targets_and_isomers() -> None:
    assert parse_target("26-FE-0").a == 0
    assert parse_target("49-IN-115-M").iso == 1
    assert parse_target("49-IN-115-M2").iso == 2
    assert parse_target("79-AU-197-G").iso == 0
    with pytest.raises(ReactionParseError):
        parse_target("40-ZR-ALY")
    with pytest.raises(ReactionParseError):
        parse_reaction("(garbage)")


# ----------------------------------------------------------------------- standards


@pytest.mark.needs_data(STANDARDS)
def test_standards_table_loads_the_six_standards() -> None:
    t = load_standards()
    names = {s.name for s in t.standards if s.is_standard}
    for want in ("1H(n,n)", "6Li(n,t)", "10B(n,a)", "197Au(n,g)", "235U(n,f)", "238U(n,f)"):
        assert want in names
    au = t.get(79, 197, "G")
    assert au is not None
    # thermal point and the plateau in the standard range
    assert t.evaluate(au, [0.0253])[0] == pytest.approx(98.659)
    assert t.evaluate(au, [2.5e5])[0] == pytest.approx(0.238)
    # outside coverage: nan, never extrapolated
    assert np.isnan(t.evaluate(au, [1.0e3])[0])
    assert np.isnan(t.evaluate(au, [5.0e6])[0])


@pytest.mark.needs_data(STANDARDS)
def test_standard_lookup_from_reaction_strings() -> None:
    assert standard_for_reaction("(92-U-235(N,F),,SIG)").name == "235U(n,f)"
    assert standard_for_reaction("(3-LI-6(N,T)2-HE-4,,SIG)").name == "6Li(n,t)"
    assert standard_for_reaction("(3-LI-6(N,A)1-H-3,,SIG)").name == "6Li(n,t)"
    assert standard_for_reaction("(1-H-1(N,EL)1-H-1,,SIG)").name == "1H(n,n)"
    assert standard_for_reaction("(5-B-10(N,A)3-LI-7,,SIG)").name == "10B(n,a)"
    assert standard_for_reaction("(79-AU-197(N,G)79-AU-198,,SIG)").name == "197Au(n,g)"
    # not standards: partial branches, Maxwellian averages, other nuclides
    assert standard_for_reaction("(5-B-10(N,A)3-LI-7,PAR,SIG)") is None
    assert standard_for_reaction("(79-AU-197(N,G)79-AU-198,,SIG,,MXW)") is None
    assert standard_for_reaction("(27-CO-59(N,G)27-CO-60,,SIG)") is None


@pytest.mark.needs_data(STANDARDS)
def test_ratio_and_monitor_conversion() -> None:
    res = ratio_to_absolute([0.5], [2.5e6], "(92-U-235(N,F),,SIG)")
    assert res is not None
    vals, std = res
    assert std.name == "235U(n,f)"
    assert vals[0] == pytest.approx(0.5 * 1.2615, rel=1e-6)  # lin-lin between 2.4 and 2.6 MeV
    assert ratio_to_absolute([0.5], [2.5e6], "(27-CO-59(N,G)27-CO-60,,SIG)") is None
    r = monitor_ratio("(79-AU-197(N,G)79-AU-198,,SIG)", [5.0e5], 0.13)
    assert r is not None
    assert r[0][0] == pytest.approx(0.137 / 0.13)


# ----------------------------------------------------------------------- synthetic X4

SYNTHETIC = textwrap.dedent(
    """\
    ENTRY            99999   20250101                             9999900000001
    SUBENT        99999001   20250101                             9999900100001
    BIB                  8         12                                 9999900100002
    TITLE      Synthetic test entry for the Incognita X4 parser       9999900100003
    AUTHOR     (A.Tester, B.Other)                                    9999900100004
    INSTITUTE  (1USABNL)                                              9999900100005
    REFERENCE  (J,NSE,100,1,201501)                                   9999900100006
               #doi:10.1000/test-doi                                  9999900100007
    FACILITY   (LINAC,1USARPI) test facility                          9999900100008
    DETECTOR   (SCIN) liquid scintillator                             9999900100009
    MONITOR    (79-AU-197(N,G)79-AU-198,,SIG)                         9999900100010
    STATUS     (APRVD)                                                9999900100011
    HISTORY    (20250101C)                                            9999900100012
    ENDBIB              12          0                                 9999900100013
    COMMON               1          3                                 9999900100014
    EN-RSL                                                            9999900100015
    PER-CENT                                                          9999900100016
     5.                                                               9999900100017
    ENDCOMMON            3          0                                 9999900100018
    ENDSUBENT           17          0                                 9999900199999
    SUBENT        99999002   20250101                             9999900200001
    BIB                  2          2                                 9999900200002
    REACTION   (26-FE-56(N,G)26-FE-57,,SIG)                           9999900200003
    STATUS     (TABLE) Table 1 of the paper                           9999900200004
    ENDBIB               2          0                                 9999900200005
    NOCOMMON             0          0                                 9999900200006
    DATA                 5          3                                 9999900200007
    EN         DATA       ERR-S      ERR-SYS    MONIT                 9999900200008
    KEV        MB         MB         PER-CENT   MB                    9999900200009
     250.       12.0       1.2        3.         240.                 9999900200010
     500.       8.0        0.8        3.         130.                 9999900200011
     1000.      5.0                   3.         80.                  9999900200012
    ENDDATA              5          0                                 9999900200013
    ENDSUBENT           12          0                                 9999900299999
    SUBENT        99999003   20250101                             9999900300001
    BIB                  2          3                                 9999900300002
    REACTION  1(92-U-238(N,0),,EN)                                    9999900300003
              2(92-U-238(N,G),,WID)                                   9999900300004
    STATUS     (SPSDD,99999004)                                       9999900300005
    ENDBIB               3          0                                 9999900300006
    NOCOMMON             0          0                                 9999900300007
    DATA                 4          2                                 9999900300008
    DATA      1DATA-ERR  1DATA      2DATA-ERR  2                      9999900300009
    EV         EV         MILLI-EV   MILLI-EV                         9999900300010
     6.67       0.01       23.0       0.5                             9999900300011
     20.9       0.02       22.0       0.6                             9999900300012
    ENDDATA              4          0                                 9999900300013
    ENDSUBENT           12          0                                 9999900399999
    SUBENT        99999004   20250101                             9999900400001
    BIB                  1          1                                 9999900400002
    REACTION   ((92-U-238(N,F),,SIG)/(92-U-235(N,F),,SIG))            9999900400003
    ENDBIB               1          0                                 9999900400004
    NOCOMMON             0          0                                 9999900400005
    DATA                 3          2                                 9999900400006
    EN         DATA       DATA-ERR                                    9999900400007
    MEV        NO-DIM     NO-DIM                                      9999900400008
     2.5    +00 4.3    -01 1.0    -02                                 9999900400009
     14.0       0.55       0.01                                       9999900400010
    ENDDATA              4          0                                 9999900400011
    ENDSUBENT           10          0                                 9999900499999
    ENDENTRY             4          0                                 9999999999999
    """
)


@pytest.mark.needs_data(STANDARDS)
def test_synthetic_entry_end_to_end() -> None:
    entry = parse_entry(SYNTHETIC)
    assert entry.entry == "99999"
    assert [s.accession for s in entry.subentries] == [
        "99999001",
        "99999002",
        "99999003",
        "99999004",
    ]
    stats: Counter = Counter()
    errors: list[dict] = []
    ms = build_measurements(entry, stats, errors)
    assert errors == []
    assert stats["subentries"] == 3
    assert stats["subentries_parsed"] == 3
    by_key = {(m.subentry, m.pointer): m for m in ms}
    assert set(by_key) == {
        ("99999002", None),
        ("99999003", "1"),
        ("99999003", "2"),
        ("99999004", None),
    }

    # --- capture table: units, errors, BIB inheritance from subentry 001, monitor renorm
    fe = by_key[("99999002", None)]
    assert fe.target_id == "Z026N030M0"
    assert fe.mt == 102
    assert fe.energy_ev == pytest.approx([250e3, 500e3, 1000e3])
    assert fe.energy_sigma_ev == pytest.approx([12.5e3, 25e3, 50e3])  # 5 % from COMMON of 001
    assert fe.original.units == "MB"
    assert fe.original.values == pytest.approx([12.0, 8.0, 5.0])
    assert fe.original.stat_sigma[:2] == pytest.approx([1.2, 0.8])
    assert np.isnan(fe.original.stat_sigma[2])  # missing σ is kept missing, not defaulted
    assert fe.original.sys_sigma == pytest.approx([0.36, 0.24, 0.15])  # 3 % of the value
    assert fe.monitor == "(79-AU-197(N,G)79-AU-198,,SIG)"
    assert fe.renormalized is not None
    assert fe.renormalized.units == "b"
    assert fe.renormalized.standards_version == STANDARDS_VERSION
    # Au(n,g) 2017 standard: 0.238 b at 250 keV, 0.137 b at 500 keV, 0.079 b at 1 MeV
    assert fe.renormalized.values == pytest.approx(
        [12e-3 * 0.238 / 0.240, 8e-3 * 0.137 / 0.130, 5e-3 * 0.079 / 0.080], rel=1e-6
    )
    assert fe.year == 2015
    assert fe.doi == "10.1000/test-doi"
    assert fe.first_author == "A.Tester"
    assert fe.facility == "LINAC"
    assert fe.detector == "SCIN"
    assert fe.reference == "(J,NSE,100,1,201501)"
    assert fe.outdated is False
    assert fe.exfor_version

    # --- resonance table: pointer 1 is the energy, pointer 2 the width; SPSDD -> outdated
    en = by_key[("99999003", "1")]
    wid = by_key[("99999003", "2")]
    assert en.quantity == QuantityType.RESONANCE_PARAMETER
    assert en.outdated is True and wid.outdated is True
    assert wid.energy_ev == pytest.approx([6.67, 20.9])
    assert wid.original.units == "MILLI-EV"
    assert wid.original.values == pytest.approx([23.0, 22.0])
    assert wid.renormalized is not None
    assert wid.renormalized.units == "eV"
    assert wid.renormalized.values == pytest.approx([0.023, 0.022])
    assert wid.renormalized.standards_version == "units-only"

    # --- ratio to the 235U(n,f) standard -> absolute barns (Fortran "4.3    -01" parsed)
    ra = by_key[("99999004", None)]
    assert ra.quantity == QuantityType.RATIO
    assert ra.original.values == pytest.approx([0.43, 0.55])
    assert ra.renormalized is not None
    assert ra.renormalized.standards_version == STANDARDS_VERSION
    assert ra.renormalized.values[0] == pytest.approx(0.43 * 1.2615, rel=1e-6)
    assert ra.renormalized.values[1] == pytest.approx(0.55 * 2.079, rel=1e-6)

    # --- Arrow round trip through the schema
    table = ExforMeasurement.to_arrow(ms)
    back = ExforMeasurement.from_arrow(table)
    assert [m.key for m in back] == [m.key for m in ms]


# ----------------------------------------------------------------------- real datum


@pytest.mark.skipif(not CAPTURE.exists(), reason="capture subset not built yet")
def test_real_au197_capture_near_30_kev() -> None:
    t = pq.read_table(
        CAPTURE,
        columns=["target_z", "target_a", "mt", "quantity", "energy_ev", "renormalized", "outdated"],
        filters=[("target_z", "=", 79), ("target_a", "=", 197), ("mt", "=", 102)],
    )
    vals = []
    for row in t.to_pylist():
        if row["quantity"] != "cross_section" or row["renormalized"] is None or row["outdated"]:
            continue
        if row["renormalized"]["units"] != "b":
            continue
        for e, v in zip(row["energy_ev"], row["renormalized"]["values"], strict=True):
            if 25e3 <= e <= 35e3 and v == v:
                vals.append(v)
    assert len(vals) > 10
    med = float(np.median(vals))
    assert 0.3 < med < 1.2  # ~0.6 b within a factor of 2


@pytest.mark.skipif(not CAPTURE.exists(), reason="capture subset not built yet")
def test_capture_subset_is_only_neutron_capture_z26_92() -> None:
    t = pq.read_table(CAPTURE, columns=["target_z", "projectile", "sf", "energy_ev"])
    z = t.column("target_z").to_numpy()
    assert z.min() >= 26 and z.max() <= 92
    assert set(t.column("projectile").to_pylist()) == {"n"}
    sf3 = {s["sf3"] for s in t.column("sf").to_pylist()}
    assert sf3 == {"G"}
    emax = max(max(e) for e in t.column("energy_ev").to_pylist() if e)
    assert emax <= 20e6


# ----------------------------------------------------------------------- MONIT renorm rules
#
# Minimal X4 snippets reproducing the artefacts the WP-12 curation pass found in the
# capture subset (2026-09-09): entry 40520 (Kononov 1977: a (MONIT)-flagged 197Au
# normalization constant at EN-NRM = 30 keV next to an unflagged 10B shape monitor)
# and entry 31790 (Wallner 2017: MONIT = 98.66 "MB" that is really barns), plus the
# cases that must keep working.


def _x4(*lines: str) -> str:
    """Join X4 lines; the parser only reads columns 1-66, so no right padding needed."""
    return "\n".join(lines) + "\n"


def _row(*fields: str) -> str:
    return "".join(f"{f:<11}" for f in fields)


def _entry_header(entry: str, bib_lines: list[str], common: list[str] | None = None) -> list[str]:
    n = len(bib_lines)
    out = [f"ENTRY            {entry}   20250101", f"SUBENT        {entry}001   20250101"]
    out.append(f"BIB                  {n}         {n}")
    out.extend(bib_lines)
    out.append("ENDBIB")
    if common:
        nf = len(common[0]) // 11
        out.append(f"COMMON               {nf}          3")
        out.extend(common)
        out.append("ENDCOMMON")
    else:
        out.append("NOCOMMON             0          0")
    out.append("ENDSUBENT")
    return out


def _subent(
    acc: str,
    reaction: str,
    headings: str,
    units: str,
    rows: list[str],
    common: list[str] | None = None,
) -> list[str]:
    out = [f"SUBENT        {acc}   20250101", "BIB                  1          1"]
    out.append(f"REACTION   {reaction}")
    out.append("ENDBIB")
    if common:
        nf = len(common[0]) // 11
        out.append(f"COMMON               {nf}          3")
        out.extend(common)
        out.append("ENDCOMMON")
    else:
        out.append("NOCOMMON             0          0")
    nf = len(headings) // 11
    out.append(f"DATA                 {nf}          {len(rows)}")
    out.append(headings)
    out.append(units)
    out.extend(rows)
    out.append("ENDDATA")
    out.append("ENDSUBENT")
    return out


def _measurements(text: str, **kw) -> tuple[dict, Counter]:
    stats: Counter = Counter()
    errors: list[dict] = []
    ms = build_measurements(parse_entry(text), stats, errors, **kw)
    assert errors == []
    return {m.subentry: m for m in ms}, stats


KONONOV_STYLE = _x4(
    *_entry_header(
        "40520",
        [
            "AUTHOR     (V.N.Kononov)",
            "REFERENCE  (R,YK-22,29,1977)",
            "MONITOR    (5-B-10(N,A)3-LI-7,,SIG) Energy dependence of",
            "            neutron flux measured using B-10(n,alpha gamma).",
            "           ((MONIT)79-AU-197(N,G)79-AU-198,,SIG)",
            "           Absolute normalization , 596.+-24.mb at 30 keV.",
            "MONIT-REF  (,B.A.Magurno+,R,BNL-NCS-50464,1975) Energy dependence",
            "           ((MONIT)21848002,W.P.Poenitz+,J,JNE,22,505,1968)",
        ],
        [
            _row("EN-NRM", "ERR-2", "MONIT", "MONIT-ERR"),
            _row("KEV", "PER-CENT", "MB", "MB"),
            _row("30.", "5.", "596.", "24."),
        ],
    ),
    *_subent(
        "40520002",
        "(79-AU-197(N,G)79-AU-198,,SIG)",
        _row("EN-MIN", "EN-MAX", "DATA", "ERR-T"),
        _row("KEV", "KEV", "MB", "MB"),
        [
            _row("5.", "6.", "2280.", "187."),
            _row("20.", "30.", "800.", "60."),
            _row("90.", "100.", "320.", "25."),
        ],
    ),
    # same layout but the normalization point lies inside the Au Standard's range
    *_subent(
        "40520003",
        "(49-IN-0(N,G),,SIG)",
        _row("EN-MIN", "EN-MAX", "DATA", "ERR-T"),
        _row("KEV", "KEV", "MB", "MB"),
        [
            _row("5.", "6.", "1690.", "170."),
            _row("20.", "30.", "700.", "50."),
            _row("90.", "100.", "300.", "20."),
        ],
        common=[_row("EN-NRM", "MONIT"), _row("KEV", "MB"), _row("500.", "130.")],
    ),
    "ENDENTRY",
)


@pytest.mark.needs_data(STANDARDS)
def test_kononov_style_monit_flag_and_en_nrm() -> None:
    """40520: the MONIT constant belongs to the (MONIT)-flagged 197Au item at EN-NRM,
    not to the 10B shape monitor at every data energy (that gave x3.5-4.6)."""
    by, stats = _measurements(KONONOV_STYLE)
    au = by["40520002"]
    assert au.monitor == "(5-B-10(N,A)3-LI-7,,SIG)"  # first MONITOR code, unchanged
    assert au.renorm_monitor == "(79-AU-197(N,G)79-AU-198,,SIG)"
    # Au Standard has no point-wise values at 30 keV -> nothing applied, nothing lost
    assert au.renorm_reason == "monitor_energy_out_of_range"
    assert au.renorm_factor is None and au.renorm_factor_rejected is None
    assert au.renormalized is not None
    assert au.renormalized.standards_version == "units-only"
    assert au.renormalized.values == pytest.approx([2.280, 0.800, 0.320])
    assert stats["renorm:monitor_energy_out_of_range"] == 1

    # EN-NRM = 500 keV, assumed 130 mb, Standard 137 mb: one factor for the whole table
    ind = by["40520003"]
    assert ind.renorm_reason == "monitor_to_standard"
    assert ind.renorm_monitor == "(79-AU-197(N,G)79-AU-198,,SIG)"
    assert ind.renorm_factor == pytest.approx(0.137 / 0.130, rel=1e-6)
    assert ind.renormalized is not None
    assert ind.renormalized.standards_version == STANDARDS_VERSION
    assert ind.renormalized.values == pytest.approx(
        [v * 1e-3 * 0.137 / 0.130 for v in (1690.0, 700.0, 300.0)], rel=1e-6
    )
    assert ind.renormalized.stat_sigma == pytest.approx(
        [v * 1e-3 * 0.137 / 0.130 for v in (170.0, 50.0, 20.0)], rel=1e-6
    )


@pytest.mark.needs_data(STANDARDS)
def test_band_is_configurable() -> None:
    by, stats = _measurements(KONONOV_STYLE, renorm_band=(0.95, 1.05))
    ind = by["40520003"]
    assert ind.renorm_reason.startswith("factor_out_of_band")
    assert ind.renorm_factor is None
    assert ind.renorm_factor_rejected == pytest.approx(0.137 / 0.130, rel=1e-6)
    assert ind.renormalized is not None
    assert ind.renormalized.standards_version == "units-only"
    assert ind.renormalized.values == pytest.approx([1.690, 0.700, 0.300])
    assert stats["renorm:factor_out_of_band"] == 1


WALLNER_STYLE = _x4(
    *_entry_header(
        "31790",
        [
            "AUTHOR     (A.Wallner)",
            "REFERENCE  (J,PR/C,96,025808,2017)",
            "MONITOR    (79-AU-197(N,G)79-AU-198,,SIG)",
            "            Thermal cross setio: 98.66+/-0.14 barn.",
        ],
    ),
    *_subent(
        "31790002",
        "(26-FE-54(N,G)26-FE-55,,SIG,,SPA)",
        _row("DATA", "ERR-T", "FLAG"),
        _row("B", "B", "NO-DIM"),
        [_row("2.36", "0.07", "1."), _row("2.29", "0.06", "2."), _row("2.31", "0.07", "3.")],
        common=[
            _row("EN-DUMMY", "MONIT", "MONIT-ERR"),
            _row("EV", "MB", "MB"),
            _row("0.0253", "98.66", "0.14"),
        ],
    ),
    "ENDENTRY",
)


@pytest.mark.needs_data(STANDARDS)
def test_wallner_style_monit_unit_slip_is_rejected_not_applied() -> None:
    """31790: MONIT 98.66 compiled as MB (the text says barn) -> x1000; record, don't apply."""
    by, stats = _measurements(WALLNER_STYLE)
    fe = by["31790002"]
    assert fe.renorm_monitor == "(79-AU-197(N,G)79-AU-198,,SIG)"
    assert fe.renorm_reason.startswith("factor_out_of_band")
    assert fe.renorm_reason.endswith(":unit_slip_1000^1")
    assert fe.renorm_factor is None
    assert fe.renorm_factor_rejected == pytest.approx(98.659 / 0.09866, rel=1e-6)
    assert fe.renormalized is not None
    assert fe.renormalized.standards_version == "units-only"
    assert fe.renormalized.values == pytest.approx([2.36, 2.29, 2.31])
    assert fe.original.values == pytest.approx([2.36, 2.29, 2.31])
    assert stats["renorm:factor_out_of_band"] == 1
    assert stats["renorm:monitor_to_standard"] == 0


CORRECT_AU_STYLE = _x4(
    *_entry_header(
        "11047",
        [
            "AUTHOR     (A.Tester)",
            "REFERENCE  (J,NSE,100,1,201501)",
            "MONITOR    (79-AU-197(N,G)79-AU-198,,SIG)",
        ],
        [_row("MONIT"), _row("B"), _row("95.")],
    ),
    # thermal Maxwellian value normalized to an old Au thermal value of 95 b
    *_subent(
        "11047002",
        "(26-FE-0(N,G),,SIG,,MXW)",
        _row("EN-DUMMY", "DATA", "DATA-ERR"),
        _row("EV", "B", "B"),
        [_row("0.0253", "2.50", "0.10")],
    ),
    # per-point MONIT column in DATA, every point inside the Au Standard's range
    *_subent(
        "11047003",
        "(27-CO-59(N,G)27-CO-60,,SIG)",
        _row("EN", "DATA", "MONIT"),
        _row("KEV", "MB", "MB"),
        [_row("250.", "12.0", "240."), _row("500.", "8.0", "130."), _row("1000.", "5.0", "80.")],
    ),
    # same, but the first point lies below the Au Standard's 200 keV lower edge
    *_subent(
        "11047004",
        "(27-CO-59(N,G)27-CO-60,,SIG)",
        _row("EN", "DATA", "MONIT"),
        _row("KEV", "MB", "MB"),
        [_row("100.", "20.0", "300."), _row("500.", "8.0", "130.")],
    ),
    "ENDENTRY",
)


@pytest.mark.needs_data(STANDARDS)
def test_correct_au_monitor_is_still_renormalized() -> None:
    by, stats = _measurements(CORRECT_AU_STYLE)
    th = by["11047002"]
    assert th.renorm_reason == "monitor_to_standard"
    assert th.renorm_monitor == "(79-AU-197(N,G)79-AU-198,,SIG)"
    assert th.renorm_factor == pytest.approx(98.659 / 95.0, rel=1e-6)
    assert th.renormalized is not None
    assert th.renormalized.standards_version == STANDARDS_VERSION
    assert th.renormalized.values == pytest.approx([2.50 * 98.659 / 95.0], rel=1e-6)

    co = by["11047003"]
    assert co.renorm_reason == "monitor_to_standard"
    assert co.renorm_factor == pytest.approx(
        np.median([0.238 / 0.240, 0.137 / 0.130, 0.079 / 0.080])
    )
    assert co.renormalized is not None
    assert co.renormalized.values == pytest.approx(
        [12e-3 * 0.238 / 0.240, 8e-3 * 0.137 / 0.130, 5e-3 * 0.079 / 0.080], rel=1e-6
    )

    # never half-renormalize a table
    part = by["11047004"]
    assert part.renorm_reason.startswith("monitor_energy_partial_coverage:1/2")
    assert part.renorm_factor is None
    assert part.renorm_factor_rejected == pytest.approx(0.137 / 0.130, rel=1e-6)
    assert part.renormalized is not None
    assert part.renormalized.standards_version == "units-only"
    assert part.renormalized.values == pytest.approx([20e-3, 8e-3])
    assert stats["renorm:monitor_to_standard"] == 2
    assert stats["renorm:monitor_energy_partial_coverage"] == 1


@pytest.mark.needs_data(STANDARDS)
def test_monitor_reference_and_monit_ref_flag_are_not_standards() -> None:
    text = _x4(
        *_entry_header(
            "20264",
            ["AUTHOR     (A.Fabry)", "REFERENCE  (J,NSE,100,1,196801)"],
            [_row("EN-DUMMY"), _row("MEV"), _row("1.0")],
        ),
        # 238U(n,g) is a *reference* cross section in the 2017 package, not a standard
        *_subent(
            "20264007",
            "(92-U-238(N,G)92-U-239,,SIG,,FIS)",
            _row("EN-NRM", "MONIT", "DATA", "DATA-ERR"),
            _row("EV", "B", "MB", "MB"),
            [_row("2.53E-02", "2.73", "85.", "8.")],
        ),
        "ENDENTRY",
    )
    # inject the subentry-level MONITOR keyword
    text = text.replace(
        "REACTION   (92-U-238(N,G)92-U-239,,SIG,,FIS)",
        "REACTION   (92-U-238(N,G)92-U-239,,SIG,,FIS)\nMONITOR    (92-U-238(N,G)92-U-239,,SIG)",
    )
    by, stats = _measurements(text)
    u = by["20264007"]
    assert u.renorm_reason == "monitor_not_standard"
    assert u.renorm_monitor == "(92-U-238(N,G)92-U-239,,SIG)"
    assert u.renormalized is not None and u.renormalized.standards_version == "units-only"

    # 40691: the (MONIT) flag lives only in MONIT-REF, so the MONIT column is not the
    # 235U(n,f) shape monitor's value
    text = _x4(
        *_entry_header(
            "40691",
            [
                "AUTHOR     (Yu.Ya.Stavisskii)",
                "REFERENCE  (J,SJA,19,905,1965)",
                "MONITOR    (92-U-235(N,F),,SIG) For energy dependence.",
                "MONIT-REF  ((MONIT)40691003,Yu.Ya.Stavisskii+,J,SJA,19,905,1965)",
            ],
            [
                _row("EN-NRM", "MONIT", "MONIT-ERR"),
                _row("KEV", "MB", "MB"),
                _row("600.", "325.", "60."),
            ],
        ),
        *_subent(
            "40691002",
            "(75-RE-0(N,G),,SIG)",
            _row("EN", "DATA"),
            _row("MEV", "B"),
            [_row("2.0E-02", "1.8"), _row("6.0E-01", "0.325")],
        ),
        "ENDENTRY",
    )
    by, stats = _measurements(text)
    re_ = by["40691002"]
    assert re_.renorm_reason.startswith("monitor_reaction_ambiguous")
    assert re_.renorm_factor is None
    assert re_.renormalized is not None and re_.renormalized.standards_version == "units-only"
    assert stats["renorm:monitor_reaction_ambiguous"] == 1


@pytest.mark.needs_data(STANDARDS)
def test_constant_monit_under_multi_energy_table_is_ambiguous() -> None:
    text = _x4(
        *_entry_header(
            "99998",
            [
                "AUTHOR     (A.Tester)",
                "REFERENCE  (J,NSE,100,1,201501)",
                "MONITOR    (79-AU-197(N,G)79-AU-198,,SIG)",
            ],
            [_row("MONIT"), _row("MB"), _row("130.")],
        ),
        *_subent(
            "99998002",
            "(27-CO-59(N,G)27-CO-60,,SIG)",
            _row("EN", "DATA"),
            _row("KEV", "MB"),
            [_row("250.", "12.0"), _row("500.", "8.0"), _row("1000.", "5.0")],
        ),
        "ENDENTRY",
    )
    by, _ = _measurements(text)
    m = by["99998002"]
    assert m.renorm_reason.startswith("monitor_energy_ambiguous")
    assert m.renorm_factor is None and m.renorm_factor_rejected is None
    assert m.renormalized is not None and m.renormalized.standards_version == "units-only"


@pytest.mark.needs_data(STANDARDS)
def test_extended_arrow_schema_round_trip() -> None:
    by, _ = _measurements(CORRECT_AU_STYLE)
    ms = list(by.values())
    table = ExforMeasurement.to_arrow(ms)
    assert (
        table.schema.names[: len(Measurement.ARROW_SCHEMA.names)] == Measurement.ARROW_SCHEMA.names
    )
    assert table.schema.names[-4:] == [
        "renorm_factor",
        "renorm_monitor",
        "renorm_reason",
        "renorm_factor_rejected",
    ]
    back = ExforMeasurement.from_arrow(table)
    assert [m.renorm_reason for m in back] == [m.renorm_reason for m in ms]
    assert back[0].renorm_factor == pytest.approx(ms[0].renorm_factor)
    # a plain-Measurement reader that selects columns by name still works
    plain = Measurement.from_arrow(table.select(Measurement.ARROW_SCHEMA.names))
    assert [m.key for m in plain] == [m.key for m in ms]


@pytest.mark.needs_data(STANDARDS)
def test_isomer_product_monitor_is_not_the_standard() -> None:
    au = "MONITOR    (79-AU-197(N,G)79-AU-198,,SIG)"
    assert au in CORRECT_AU_STYLE
    by, _ = _measurements(CORRECT_AU_STYLE.replace(au, au.replace("198,,SIG", "198-M,,SIG")))
    assert by["11047003"].renorm_reason == "monitor_not_standard:isomer product"
    assert by["11047003"].renormalized is not None
    assert by["11047003"].renormalized.standards_version == "units-only"
    by, _ = _measurements(CORRECT_AU_STYLE.replace(au, au.replace("198,,SIG", "198-G,,SIG")))
    assert by["11047003"].renorm_reason == "monitor_to_standard"
