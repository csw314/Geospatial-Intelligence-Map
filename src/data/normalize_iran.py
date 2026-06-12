"""Normalization for Iran location rows."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Literal

from src.data.coordinate_utils import parse_latitude_longitude
from src.data.data_quality import NormalizedLocation
from src.data.schemas import LocationRecord
from src.utils.text_cleaning import blank_to_none, normalize_mapping, slugify

SOURCE_FILE: Literal["iran_data.csv"] = "iran_data.csv"
EXPECTED_COLUMNS = ("Country", "Type", "Name", "Latitude", "Longitude", "Notes")
OPTIONAL_COLUMNS = ("Notes",)


def normalize_iran_row(row: Mapping[str, Any], row_number: int) -> NormalizedLocation:
    """Normalize one Iran CSV row into the shared location schema."""

    raw = {str(key): "" if value is None else str(value) for key, value in row.items()}
    cleaned = normalize_mapping(row)
    coordinates = parse_latitude_longitude(cleaned.get("Latitude"), cleaned.get("Longitude"))
    if coordinates is None:
        raise ValueError("invalid Iran latitude/longitude")

    name = cleaned.get("Name") or f"Unnamed Iran location {row_number}"
    location_type = cleaned.get("Type") or "Unknown"
    latitude, longitude = coordinates
    record = LocationRecord(
        id=f"{SOURCE_FILE}:{row_number}:{slugify(name)}",
        source_file=SOURCE_FILE,
        country=cleaned.get("Country") or "Iran",
        location_category="Counterforce",
        dataset_type="military",
        name=name,
        type=location_type,
        latitude=latitude,
        longitude=longitude,
        notes=blank_to_none(cleaned.get("Notes")),
        raw=raw,
    )
    return NormalizedLocation(record=record)
