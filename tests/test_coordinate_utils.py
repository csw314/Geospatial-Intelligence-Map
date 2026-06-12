from __future__ import annotations

import pytest

from src.data.coordinate_utils import (
    is_valid_latitude,
    is_valid_longitude,
    parse_coordinate_pair,
    parse_latitude_longitude,
)


def test_latitude_longitude_validation() -> None:
    assert is_valid_latitude(90)
    assert is_valid_latitude(-90)
    assert not is_valid_latitude(91)
    assert is_valid_longitude(180)
    assert is_valid_longitude(-180)
    assert not is_valid_longitude(181)


def test_parse_latitude_longitude_fields() -> None:
    assert parse_latitude_longitude(" 30.5 ", "\u00a0117.25 ") == (30.5, 117.25)
    assert parse_latitude_longitude("bad", "117.25") is None
    assert parse_latitude_longitude("95", "117.25") is None


def test_parse_coordinate_pair_with_cardinals() -> None:
    assert parse_coordinate_pair("30.58333N 117.05000E") == (30.58333, 117.05)
    assert parse_coordinate_pair("41.1 S, 122.8 W") == (-41.1, -122.8)
    assert parse_coordinate_pair("30.5, 117.25") == (30.5, 117.25)
    assert parse_coordinate_pair("no coordinates here") is None


def test_parse_compact_dms_coordinate_pair() -> None:
    assert parse_coordinate_pair("304219N 1035701E") == pytest.approx(
        (
            30.705277777777777,
            103.95027777777777,
        )
    )
    assert parse_coordinate_pair("24320N 11870E") == pytest.approx(
        (
            24.533333333333335,
            118.11666666666666,
        )
    )
