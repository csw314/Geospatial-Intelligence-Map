from __future__ import annotations

import pytest

from src.data.normalize_metro_areas import normalize_metro_area_row, parse_population


def test_parse_population_with_commas() -> None:
    assert parse_population("32,054,159") == 32054159
    assert parse_population(" 1 234 ") == 1234
    assert parse_population("") is None
    assert parse_population("unknown") is None


def test_normalize_metro_area_row() -> None:
    normalized = normalize_metro_area_row(
        {
            "Country": " China ",
            "ISO2": " CN ",
            "Metro Area / City": " Chongqing\u00a0",
            "Admin Region": " Chongqing ",
            "Longitude": "106.5069",
            "Latitude": "29.55",
            "Population": "32,054,159",
            "Population Proper": "32,054,159",
            "Capital Status": "admin",
            "Source Country Name": "China",
            "Source URL": "https://example.test/cn.csv",
        },
        2,
    )

    record = normalized.record
    assert record.id == "metro_areas.csv:2:chongqing"
    assert record.source_file == "metro_areas.csv"
    assert record.map_layer == "global_metros"
    assert record.location_category == "Non-Military"
    assert record.dataset_type == "metro_area"
    assert record.type == "Metro Area"
    assert record.country == "China"
    assert record.region == "Chongqing"
    assert record.population == 32054159
    assert record.population_proper == 32054159
    assert record.raw["Metro Area / City"] == " Chongqing\u00a0"


def test_missing_population_does_not_drop_metro_row() -> None:
    normalized = normalize_metro_area_row(
        {
            "Country": "China",
            "ISO2": "CN",
            "Metro Area / City": "Small City",
            "Admin Region": "Region",
            "Longitude": "100",
            "Latitude": "20",
            "Population": "",
            "Population Proper": "not available",
            "Capital Status": "",
            "Source Country Name": "China",
            "Source URL": "",
        },
        5,
    )

    assert normalized.record.population is None
    assert normalized.record.population_proper is None
    assert normalized.invalid_population_count == 1
    assert len(normalized.warnings) == 2


def test_invalid_metro_coordinates_are_rejected() -> None:
    with pytest.raises(ValueError):
        normalize_metro_area_row(
            {
                "Country": "China",
                "Metro Area / City": "Broken City",
                "Longitude": "181",
                "Latitude": "20",
                "Population": "1,000",
                "Population Proper": "1,000",
            },
            6,
        )
