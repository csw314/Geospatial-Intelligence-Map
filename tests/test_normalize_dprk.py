from __future__ import annotations

import pytest

from src.data.normalize_dprk import normalize_dprk_row


def test_normalize_dprk_row() -> None:
    normalized = normalize_dprk_row(
        {
            "Category Source": " Rocket launch site ",
            "Country": " DPRK ",
            "Name": " Sakkanmol Missile Operating Base ",
            "Type": " Missile operating base ",
            "Latitude": "38.584698",
            "Longitude": "126.107945",
            "Notes": " Tongch\u2019ang-dong note ",
        },
        2,
    )

    record = normalized.record
    assert record.id == "dprk_data.csv:2:sakkanmol-missile-operating-base"
    assert record.source_file == "dprk_data.csv"
    assert record.country == "DPRK"
    assert record.location_category == "Counterforce"
    assert record.dataset_type == "military"
    assert record.category_source == "Rocket launch site"
    assert record.notes == "Tongch\u2019ang-dong note"
    assert record.latitude == 38.584698
    assert record.longitude == 126.107945


def test_missing_dprk_coordinates_are_rejected() -> None:
    with pytest.raises(ValueError):
        normalize_dprk_row(
            {
                "Category Source": "Airfield",
                "Country": "DPRK",
                "Name": "Missing Coordinates",
                "Type": "Military airfield",
                "Latitude": "",
                "Longitude": "",
                "Notes": "",
            },
            3,
        )


def test_empty_dprk_notes_do_not_crash() -> None:
    normalized = normalize_dprk_row(
        {
            "Category Source": "Airfield",
            "Country": "DPRK",
            "Name": "Panghyon Airfield",
            "Type": "Military airfield",
            "Latitude": "39.9",
            "Longitude": "125.2",
            "Notes": "",
        },
        4,
    )

    assert normalized.record.notes is None
