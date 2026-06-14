"""Normalization for U.S. military site rows."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Literal

from src.data.coordinate_utils import parse_latitude_longitude
from src.data.data_quality import NormalizedLocation
from src.data.normalization_utils import numeric_warning, parse_int, parse_number
from src.data.schemas import LocationRecord
from src.utils.text_cleaning import blank_to_none, normalize_mapping, slugify

SOURCE_FILE: Literal["us_military_sites.csv"] = "us_military_sites.csv"
EXPECTED_COLUMNS = (
    "Record_ID",
    "Site",
    "Component",
    "Service_Branch",
    "Component_Status",
    "Host_Country",
    "Admin_Area",
    "Location_Class",
    "Geographic_Scope",
    "Nearest_City",
    "Latitude",
    "Longitude",
    "Coordinate_Quality",
    "Buildings_Owned",
    "Buildings_Owned_SqFt",
    "Buildings_Leased",
    "Buildings_Leased_SqFt",
    "Buildings_Other",
    "Buildings_Other_SqFt",
    "Acres_Owned",
    "Total_Acres",
    "Plant_Replacement_Value_M",
    "Coordinate_Source_URL",
    "Dataset_Source_URL",
    "Notes",
)
OPTIONAL_COLUMNS = (
    "Component",
    "Service_Branch",
    "Component_Status",
    "Admin_Area",
    "Location_Class",
    "Geographic_Scope",
    "Nearest_City",
    "Coordinate_Quality",
    "Buildings_Owned",
    "Buildings_Owned_SqFt",
    "Buildings_Leased",
    "Buildings_Leased_SqFt",
    "Buildings_Other",
    "Buildings_Other_SqFt",
    "Acres_Owned",
    "Total_Acres",
    "Plant_Replacement_Value_M",
    "Coordinate_Source_URL",
    "Dataset_Source_URL",
    "Notes",
)


def normalize_us_military_row(row: Mapping[str, Any], row_number: int) -> NormalizedLocation:
    """Normalize one U.S. military-site CSV row into the shared schema."""

    raw = {str(key): "" if value is None else str(value) for key, value in row.items()}
    cleaned = normalize_mapping(row)
    coordinates = parse_latitude_longitude(cleaned.get("Latitude"), cleaned.get("Longitude"))
    if coordinates is None:
        raise ValueError("invalid U.S. military site latitude/longitude")

    int_fields = {
        "Buildings_Owned": parse_int(cleaned.get("Buildings_Owned")),
        "Buildings_Leased": parse_int(cleaned.get("Buildings_Leased")),
        "Buildings_Other": parse_int(cleaned.get("Buildings_Other")),
    }
    number_fields = {
        "Buildings_Owned_SqFt": parse_number(cleaned.get("Buildings_Owned_SqFt")),
        "Buildings_Leased_SqFt": parse_number(cleaned.get("Buildings_Leased_SqFt")),
        "Buildings_Other_SqFt": parse_number(cleaned.get("Buildings_Other_SqFt")),
        "Acres_Owned": parse_number(cleaned.get("Acres_Owned")),
        "Total_Acres": parse_number(cleaned.get("Total_Acres")),
        "Plant_Replacement_Value_M": parse_number(cleaned.get("Plant_Replacement_Value_M")),
    }

    warnings: list[str] = []
    invalid_numeric_count = 0
    for field_name, parsed_count in int_fields.items():
        warning = numeric_warning(field_name, cleaned.get(field_name), parsed_count)
        if warning:
            warnings.append(warning)
            invalid_numeric_count += 1
    for field_name, parsed_number in number_fields.items():
        warning = numeric_warning(field_name, cleaned.get(field_name), parsed_number)
        if warning:
            warnings.append(warning)
            invalid_numeric_count += 1

    record_id = cleaned.get("Record_ID") or str(row_number)
    name = cleaned.get("Site") or f"Unnamed U.S. military site {row_number}"
    service_branch = cleaned.get("Service_Branch") or "U.S. Military"
    latitude, longitude = coordinates
    record = LocationRecord(
        id=f"{SOURCE_FILE}:{record_id}:{slugify(name)}",
        source_file=SOURCE_FILE,
        map_layer="us_military",
        country=cleaned.get("Host_Country") or "Unknown",
        operator_country="United States",
        location_category="Military Site",
        dataset_type="military",
        name=name,
        type=service_branch,
        latitude=latitude,
        longitude=longitude,
        admin_area=blank_to_none(cleaned.get("Admin_Area")),
        component=blank_to_none(cleaned.get("Component")),
        service_branch=blank_to_none(cleaned.get("Service_Branch")),
        component_status=blank_to_none(cleaned.get("Component_Status")),
        location_class=blank_to_none(cleaned.get("Location_Class")),
        geographic_scope=blank_to_none(cleaned.get("Geographic_Scope")),
        nearest_city=blank_to_none(cleaned.get("Nearest_City")),
        coordinate_quality=blank_to_none(cleaned.get("Coordinate_Quality")),
        buildings_owned=int_fields["Buildings_Owned"],
        buildings_owned_sqft=number_fields["Buildings_Owned_SqFt"],
        buildings_leased=int_fields["Buildings_Leased"],
        buildings_leased_sqft=number_fields["Buildings_Leased_SqFt"],
        buildings_other=int_fields["Buildings_Other"],
        buildings_other_sqft=number_fields["Buildings_Other_SqFt"],
        acres_owned=number_fields["Acres_Owned"],
        total_acres=number_fields["Total_Acres"],
        plant_replacement_value_m=number_fields["Plant_Replacement_Value_M"],
        coordinate_source_url=blank_to_none(cleaned.get("Coordinate_Source_URL")),
        dataset_source_url=blank_to_none(cleaned.get("Dataset_Source_URL")),
        notes=blank_to_none(cleaned.get("Notes")),
        raw=raw,
    )
    return NormalizedLocation(
        record=record,
        invalid_numeric_count=invalid_numeric_count,
        warnings=tuple(warnings),
    )
