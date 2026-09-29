"""Unit normalization (data/curate/units.py): round trips and the EXFOR unit vocabulary."""

from __future__ import annotations

import math

import pytest

from data.curate.units import (
    canonical_unit,
    convert,
    from_barn,
    from_ev,
    is_energy_unit,
    is_xs_unit,
    parse_unit,
    to_barn,
    to_ev,
)


@pytest.mark.parametrize(
    ("code", "value", "ev"),
    [
        ("EV", 1.0, 1.0),
        ("KEV", 30.0, 30_000.0),
        ("MEV", 14.1, 14.1e6),
        ("MILLI-EV", 25.3, 0.0253),
        ("MICRO-EV", 1.0, 1e-6),
        ("GEV", 1.0, 1e9),
    ],
)
def test_energy_to_ev(code: str, value: float, ev: float) -> None:
    assert to_ev(value, code) == pytest.approx(ev)
    assert from_ev(to_ev(value, code), code) == pytest.approx(value)
    assert is_energy_unit(code)


@pytest.mark.parametrize(
    ("code", "value", "barn"),
    [
        ("B", 2.0, 2.0),
        ("MB", 600.0, 0.6),
        ("MICRO-B", 1.0, 1e-6),
        ("MU-B", 1.0, 1e-6),
        ("NB", 1.0, 1e-9),
        ("PB", 1.0, 1e-12),
        ("KB", 1.0, 1e3),
        ("MILLI-BARNS", 250.0, 0.25),
        ("BARNS", 1.5, 1.5),
        ("millibarn", 10.0, 0.01),
    ],
)
def test_xs_to_barn(code: str, value: float, barn: float) -> None:
    assert to_barn(value, code) == pytest.approx(barn)
    assert from_barn(to_barn(value, code), code) == pytest.approx(value)
    assert is_xs_unit(code)


def test_lower_case_and_whitespace_are_tolerated() -> None:
    assert parse_unit(" mb ").canonical == "b"
    assert parse_unit(" kev").factor == 1e3


@pytest.mark.parametrize(
    ("code", "canonical", "factor"),
    [
        ("MB/SR", "b/sr", 1e-3),
        ("B/SR", "b/sr", 1.0),
        ("MU-B/SR", "b/sr", 1e-6),
        ("MB/SR/MEV", "b/sr/eV", 1e-9),
        ("MB/MEV", "b/eV", 1e-9),
        ("B*EV", "b*eV", 1.0),
        ("MB*KEV", "b*eV", 1.0),
        ("NO-DIM", "1", 1.0),
        ("PER-CENT", "%", 1.0),
        ("ADEG", "deg", 1.0),
        ("ARB-UNITS", "arb", 1.0),
    ],
)
def test_compound_units(code: str, canonical: str, factor: float) -> None:
    info = parse_unit(code)
    assert info.known
    assert info.canonical == canonical
    assert info.factor == pytest.approx(factor)
    assert canonical_unit(code) == canonical


def test_unknown_unit_is_flagged_not_guessed() -> None:
    info = parse_unit("P/IN/MEVSR")
    assert not info.known
    assert info.canonical == "?"
    assert math.isnan(info.factor)
    with pytest.raises(ValueError):
        convert([1.0], "P/IN/MEVSR")


def test_arbitrary_units_are_not_convertible() -> None:
    info = parse_unit("ARB-UNITS")
    assert info.known and not info.convertible
    with pytest.raises(ValueError):
        convert([1.0], "ARB-UNITS")


def test_convert_vector_round_trip() -> None:
    vals = [1.0, 250.0, 1e4]
    out, info = convert(vals, "MB")
    assert info.canonical == "b"
    assert out == pytest.approx([1e-3, 0.25, 10.0])
    back = [v / info.factor for v in out]
    assert back == pytest.approx(vals)


def test_energy_and_xs_are_not_confused() -> None:
    with pytest.raises(ValueError):
        to_ev(1.0, "MB")
    with pytest.raises(ValueError):
        to_barn(1.0, "KEV")
