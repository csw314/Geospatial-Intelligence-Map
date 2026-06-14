from __future__ import annotations

import pytest

from src.data.normalize_us_military import normalize_us_military_row


def _row() -> dict[str, str]:
    return {
        "Record_ID": "US0001",
        "Site": " Ramstein Air Base ",
        "Component": "Active",
        "Service_Branch": "Air Force",
        "Component_Status": "Active",
        "Host_Country": "Germany",
        "Admin_Area": "Rhineland-Palatinate",
        "Location_Class": "Installation",
        "Geographic_Scope": "Overseas",
        "Nearest_City": "Ramstein-Miesenbach",
        "Latitude": "49.4369",
        "Longitude": "7.6003",
        "Coordinate_Quality": "Representative point",
        "Buildings_Owned": "100",
        "Buildings_Owned_SqFt": "1,234,567",
        "Buildings_Leased": "2",
        "Buildings_Leased_SqFt": "50,000",
        "Buildings_Other": "0",
        "Buildings_Other_SqFt": "0",
        "Acres_Owned": "1,200.5",
        "Total_Acres": "1,400.25",
        "Plant_Replacement_Value_M": "$2,500.75",
        "Coordinate_Source_URL": "https://example.test/coordinate",
        "Dataset_Source_URL": "https://example.test/dataset",
        "Notes": " Public representative point. ",
    }


def test_normalize_us_military_row_maps_required_fields() -> None:
    normalized = normalize_us_military_row(_row(), 2)
    record = normalized.record

    assert record.id == "us_military_sites.csv:US0001:ramstein-air-base"
    assert record.source_file == "us_military_sites.csv"
    assert record.map_layer == "us_military"
    assert record.location_category == "Military Site"
    assert record.dataset_type == "military"
    assert record.name == "Ramstein Air Base"
    assert record.type == "Air Force"
    assert record.country == "Germany"
    assert record.operator_country == "United States"
    assert record.component == "Active"
    assert record.service_branch == "Air Force"
    assert record.component_status == "Active"
    assert record.admin_area == "Rhineland-Palatinate"
    assert record.location_class == "Installation"
    assert record.geographic_scope == "Overseas"
    assert record.nearest_city == "Ramstein-Miesenbach"
    assert record.coordinate_quality == "Representative point"
    assert record.buildings_owned == 100
    assert record.buildings_owned_sqft == 1234567
    assert record.buildings_leased == 2
    assert record.buildings_leased_sqft == 50000
    assert record.acres_owned == 1200.5
    assert record.total_acres == 1400.25
    assert record.plant_replacement_value_m == 2500.75
    assert record.coordinate_source_url == "https://example.test/coordinate"
    assert record.dataset_source_url == "https://example.test/dataset"
    assert record.raw["Site"] == " Ramstein Air Base "


def test_us_military_invalid_numeric_values_are_reported_but_not_dropped() -> None:
    row = _row()
    row["Buildings_Owned"] = "many"
    row["Total_Acres"] = "unknown"

    normalized = normalize_us_military_row(row, 2)

    assert normalized.record.buildings_owned is None
    assert normalized.record.total_acres is None
    assert normalized.invalid_numeric_count == 2
    assert len(normalized.warnings) == 2


def test_us_military_invalid_coordinates_are_rejected() -> None:
    row = _row()
    row["Longitude"] = "181"

    with pytest.raises(ValueError):
        normalize_us_military_row(row, 2)
