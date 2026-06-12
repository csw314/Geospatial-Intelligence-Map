"""Normalization for Russia location rows."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Literal

from src.data.coordinate_utils import parse_latitude_longitude
from src.data.data_quality import NormalizedLocation
from src.data.schemas import LocationRecord
from src.utils.text_cleaning import blank_to_none, normalize_mapping, slugify

SOURCE_FILE: Literal["russia_data.csv"] = "russia_data.csv"
EXPECTED_COLUMNS = ("Oblast", "Name", "Latitude", "Longitude", "Country", "Type")
OPTIONAL_COLUMNS = ("Oblast",)


def normalize_russia_row(row: Mapping[str, Any], row_number: int) -> NormalizedLocation:
    """Normalize one Russia CSV row into the shared location schema."""

    cleaned = normalize_mapping(row)
    coordinates = parse_latitude_longitude(cleaned.get("Latitude"), cleaned.get("Longitude"))
    if coordinates is None:
        raise ValueError("invalid Russia latitude/longitude")

    name = cleaned.get("Name") or f"Unnamed Russia location {row_number}"
    location_type = cleaned.get("Type") or "Unknown"
    latitude, longitude = coordinates
    record = LocationRecord(
        id=f"{SOURCE_FILE}:{row_number}:{slugify(name)}",
        source_file=SOURCE_FILE,
        country="Russia",
        location_category="Counterforce",
        dataset_type="military",
        name=name,
        type=location_type,
        latitude=latitude,
        longitude=longitude,
        region=blank_to_none(cleaned.get("Oblast")),
        raw=cleaned,
    )
    return NormalizedLocation(record=record)
