from __future__ import annotations

import pytest

from src.data.normalize_global_cities import normalize_global_city_row


def _row() -> dict[str, str]:
    return {
        "Record_ID": "G000003",
        "Location_Name": " Chongqing\u00a0",
        "Location_Type": "City / administrative seat",
        "Country": "China",
        "ISO2": "CN",
        "ISO3": "CHN",
        "Region": "East Asia",
        "Admin1_Name": "Chongqing",
        "Latitude": "29.55",
        "Longitude": "106.5069",
        "Timezone": "Asia/Shanghai",
        "Population": "32,054,159",
        "Population_Source": "Bamwor",
        "Population_Bamwor": "32,054,159",
        "Population_SimpleMaps": "32,000,000",
        "Population_Starting_List": "32,054,159",
        "Population_Size_Class": "10M+",
        "Capital_Classification": "admin",
        "Country_GDP_Per_Capita_USD": "$12,500",
        "Country_GDP_PPP_USD": "35,000,000,000,000",
        "OpenStreetMap_URL": "https://example.test/osm",
        "Wikipedia_Search_URL": "https://example.test/wiki",
        "Image_Research_URL": "https://example.test/images",
        "Primary_Source": "Bamwor",
        "Starting_List_Included": "Yes",
    }


def test_normalize_global_city_row_maps_required_fields() -> None:
    normalized = normalize_global_city_row(_row(), 2)
    record = normalized.record

    assert record.id == "global_cities_metros_100k.csv:G000003:chongqing"
    assert record.source_file == "global_cities_metros_100k.csv"
    assert record.map_layer == "global_metros"
    assert record.location_category == "Countervalue"
    assert record.dataset_type == "metro_area"
    assert record.name == "Chongqing"
    assert record.type == "City / administrative seat"
    assert record.country == "China"
    assert record.region == "East Asia"
    assert record.admin_area == "Chongqing"
    assert record.iso2 == "CN"
    assert record.iso3 == "CHN"
    assert record.timezone == "Asia/Shanghai"
    assert record.population == 32054159
    assert record.population_bamwor == 32054159
    assert record.population_simplemaps == 32000000
    assert record.population_starting_list == 32054159
    assert record.population_source == "Bamwor"
    assert record.population_size_class == "10M+"
    assert record.capital_classification == "admin"
    assert record.country_gdp_per_capita_usd == 12500
    assert record.country_gdp_ppp_usd == 35000000000000
    assert record.starting_list_included is True
    assert record.raw["Location_Name"] == " Chongqing\u00a0"
    assert normalized.invalid_population_count == 0


def test_global_city_invalid_numeric_values_are_reported_but_not_dropped() -> None:
    row = _row()
    row["Population"] = "unknown"
    row["Country_GDP_Per_Capita_USD"] = "not available"

    normalized = normalize_global_city_row(row, 2)

    assert normalized.record.population is None
    assert normalized.invalid_population_count == 1
    assert normalized.invalid_numeric_count == 2
    assert len(normalized.warnings) == 2


def test_global_city_invalid_coordinates_are_rejected() -> None:
    row = _row()
    row["Latitude"] = "91"

    with pytest.raises(ValueError):
        normalize_global_city_row(row, 2)
