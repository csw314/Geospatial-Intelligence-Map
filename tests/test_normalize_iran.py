from __future__ import annotations

import pytest

from src.data.normalize_iran import normalize_iran_row


def test_normalize_iran_row() -> None:
    normalized = normalize_iran_row(
        {
            "Country": " Iran ",
            "Type": " Air Base ",
            "Name": " Mehrabad International Airport ",
            "Latitude": "35.6886",
            "Longitude": "51.3128",
            "Notes": " F-14s located at this base ",
        },
        2,
    )

    record = normalized.record
    assert record.id == "iran_data.csv:2:mehrabad-international-airport"
    assert record.source_file == "iran_data.csv"
    assert record.country == "Iran"
    assert record.location_category == "Counterforce"
    assert record.dataset_type == "military"
    assert record.name == "Mehrabad International Airport"
    assert record.type == "Air Base"
    assert record.latitude == 35.6886
    assert record.longitude == 51.3128
    assert record.notes == "F-14s located at this base"


def test_empty_iran_notes_does_not_crash() -> None:
    normalized = normalize_iran_row(
        {
            "Country": "Iran",
            "Type": "Air Base",
            "Name": "Tabriz Air Base",
            "Latitude": "38.1289",
            "Longitude": "46.24",
            "Notes": "",
        },
        3,
    )

    assert normalized.record.notes is None


def test_invalid_iran_latitude_is_rejected() -> None:
    with pytest.raises(ValueError):
        normalize_iran_row(
            {
                "Country": "Iran",
                "Type": "Air Base",
                "Name": "Broken Latitude",
                "Latitude": "91",
                "Longitude": "46.24",
                "Notes": "",
            },
            4,
        )


def test_invalid_iran_longitude_is_rejected() -> None:
    with pytest.raises(ValueError):
        normalize_iran_row(
            {
                "Country": "Iran",
                "Type": "Air Base",
                "Name": "Broken Longitude",
                "Latitude": "38.1289",
                "Longitude": "181",
                "Notes": "",
            },
            5,
        )
