"""Normalization for metro area and city rows."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Literal

from src.data.coordinate_utils import parse_latitude_longitude
from src.data.data_quality import NormalizedLocation
from src.data.schemas import LocationRecord
from src.utils.text_cleaning import blank_to_none, normalize_mapping, normalize_text, slugify

SOURCE_FILE: Literal["metro_areas.csv"] = "metro_areas.csv"
EXPECTED_COLUMNS = (
    "Country",
    "ISO2",
    "Metro Area / City",
    "Admin Region",
    "Longitude",
    "Latitude",
    "Population",
    "Population Proper",
    "Capital Status",
    "Source Country Name",
    "Source URL",
)
OPTIONAL_COLUMNS = (
    "ISO2",
    "Admin Region",
    "Population",
    "Population Proper",
    "Capital Status",
    "Source Country Name",
    "Source URL",
)


def parse_population(value: Any) -> int | None:
    """Parse a population string with separators into an integer."""

    text = normalize_text(value)
    if not text:
        return None
    compact = text.replace(",", "").replace("_", "").replace(" ", "")
    if not compact.isdigit():
        return None
    return int(compact)


def normalize_metro_area_row(row: Mapping[str, Any], row_number: int) -> NormalizedLocation:
    """Normalize one metro-area CSV row into the shared location schema."""

    raw = {str(key): "" if value is None else str(value) for key, value in row.items()}
    cleaned = normalize_mapping(row)
    coordinates = parse_latitude_longitude(cleaned.get("Latitude"), cleaned.get("Longitude"))
    if coordinates is None:
        raise ValueError("invalid metro-area latitude/longitude")

    warnings: list[str] = []
    invalid_population = False
    population = parse_population(cleaned.get("Population"))
    population_proper = parse_population(cleaned.get("Population Proper"))
    for field_name, parsed_value in (
        ("Population", population),
        ("Population Proper", population_proper),
    ):
        if parsed_value is None:
            invalid_population = True
            warnings.append(f"Missing or invalid {field_name} value")

    name = cleaned.get("Metro Area / City") or f"Unnamed metro area {row_number}"
    latitude, longitude = coordinates
    record = LocationRecord(
        id=f"{SOURCE_FILE}:{row_number}:{slugify(name)}",
        source_file=SOURCE_FILE,
        map_layer="global_metros",
        country=cleaned.get("Country") or "Unknown",
        location_category="Non-Military",
        dataset_type="metro_area",
        name=name,
        type="Metro Area",
        latitude=latitude,
        longitude=longitude,
        region=blank_to_none(cleaned.get("Admin Region")),
        iso2=blank_to_none(cleaned.get("ISO2")),
        population=population,
        population_proper=population_proper,
        capital_status=blank_to_none(cleaned.get("Capital Status")),
        source_country_name=blank_to_none(cleaned.get("Source Country Name")),
        source_url=blank_to_none(cleaned.get("Source URL")),
        raw=raw,
    )
    return NormalizedLocation(
        record=record,
        invalid_population_count=1 if invalid_population else 0,
        warnings=tuple(warnings),
    )
