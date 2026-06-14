"""Normalization for China location rows."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Literal

from src.data.coordinate_utils import parse_coordinate_pair, parse_latitude_longitude
from src.data.data_quality import NormalizedLocation
from src.data.schemas import LocationRecord
from src.utils.text_cleaning import blank_to_none, normalize_mapping, slugify

SOURCE_FILE: Literal["china_data.csv"] = "china_data.csv"
EXPECTED_COLUMNS = (
    "Name",
    "Alternate names",
    "IATA",
    "ICAO",
    "Use",
    "Subordinate",
    "Coordinates",
    "Latitude",
    "Longitude",
    "Runways",
    "Tenants",
    "Type",
)
OPTIONAL_COLUMNS = (
    "Alternate names",
    "IATA",
    "ICAO",
    "Use",
    "Subordinate",
    "Runways",
    "Tenants",
)


def normalize_china_row(row: Mapping[str, Any], row_number: int) -> NormalizedLocation:
    """Normalize one China CSV row into the shared location schema."""

    cleaned = normalize_mapping(row)
    coordinates = parse_latitude_longitude(cleaned.get("Latitude"), cleaned.get("Longitude"))
    coordinate_cleaned = False
    warnings: list[str] = []

    if coordinates is None:
        coordinates = parse_coordinate_pair(cleaned.get("Coordinates"))
        coordinate_cleaned = coordinates is not None
        if coordinates is not None:
            warnings.append("Recovered coordinates from Coordinates field")

    if coordinates is None:
        raise ValueError("invalid China latitude/longitude and Coordinates field")

    name = cleaned.get("Name") or f"Unnamed China location {row_number}"
    location_type = cleaned.get("Type") or "Unknown"
    latitude, longitude = coordinates
    record = LocationRecord(
        id=f"{SOURCE_FILE}:{row_number}:{slugify(name)}",
        source_file=SOURCE_FILE,
        map_layer="adversary_military",
        country="China",
        operator_country="China",
        location_category="Counterforce",
        dataset_type="military",
        name=name,
        type=location_type,
        latitude=latitude,
        longitude=longitude,
        alternate_names=blank_to_none(cleaned.get("Alternate names")),
        iata=blank_to_none(cleaned.get("IATA")),
        icao=blank_to_none(cleaned.get("ICAO")),
        use=blank_to_none(cleaned.get("Use")),
        subordinate=blank_to_none(cleaned.get("Subordinate")),
        runways=blank_to_none(cleaned.get("Runways")),
        tenants=blank_to_none(cleaned.get("Tenants")),
        raw=cleaned,
    )
    return NormalizedLocation(
        record=record,
        coordinate_cleaned=coordinate_cleaned,
        warnings=tuple(warnings),
    )
