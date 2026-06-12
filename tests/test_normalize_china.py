from __future__ import annotations

import pytest

from src.data.normalize_china import normalize_china_row


def test_normalize_china_row_with_optional_fields() -> None:
    normalized = normalize_china_row(
        {
            "Name": " Anqing Air Base ",
            "Alternate names": "Anqing\u00a0Tianzhushan Airport",
            "IATA": "AQG",
            "ICAO": "ZSAQ",
            "Use": "Dual",
            "Subordinate": "ETCAF",
            "Coordinates": "30.58333N 117.05000E",
            "Latitude": "30.58333",
            "Longitude": "117.05",
            "Runways": "06/24: 2,800\u00a0m",
            "Tenants": "",
            "Type": "Air Base",
        },
        2,
    )

    record = normalized.record
    assert record.id == "china_data.csv:2:anqing-air-base"
    assert record.alternate_names == "Anqing Tianzhushan Airport"
    assert record.runways == "06/24: 2,800 m"
    assert record.tenants is None
    assert not normalized.coordinate_cleaned


def test_normalize_china_recovers_from_coordinates_field() -> None:
    normalized = normalize_china_row(
        {
            "Name": "Recovered Base",
            "Alternate names": "",
            "IATA": "",
            "ICAO": "",
            "Use": "",
            "Subordinate": "",
            "Coordinates": "30.5N 117.25E",
            "Latitude": "bad",
            "Longitude": "bad",
            "Runways": "",
            "Tenants": "",
            "Type": "Air Base",
        },
        4,
    )

    assert normalized.record.latitude == 30.5
    assert normalized.record.longitude == 117.25
    assert normalized.coordinate_cleaned
    assert normalized.warnings == ("Recovered coordinates from Coordinates field",)


def test_normalize_china_rejects_unrecoverable_coordinates() -> None:
    with pytest.raises(ValueError):
        normalize_china_row(
            {
                "Name": "Broken",
                "Coordinates": "unknown",
                "Latitude": "bad",
                "Longitude": "bad",
                "Type": "Air Base",
            },
            5,
        )
