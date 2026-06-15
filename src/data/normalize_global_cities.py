"""Normalization for global city and metro rows."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Literal

from src.data.coordinate_utils import parse_latitude_longitude
from src.data.data_quality import NormalizedLocation
from src.data.normalization_utils import (
    numeric_warning,
    parse_bool,
    parse_int,
    parse_number,
)
from src.data.schemas import LocationRecord
from src.utils.text_cleaning import blank_to_none, normalize_mapping, slugify

SOURCE_FILE: Literal["global_cities_metros_100k.csv"] = "global_cities_metros_100k.csv"
EXPECTED_COLUMNS = (
    "Record_ID",
    "Location_Name",
    "Location_Type",
    "Country",
    "ISO2",
    "ISO3",
    "Region",
    "Admin1_Name",
    "Latitude",
    "Longitude",
    "Timezone",
    "Population",
    "Population_Source",
    "Population_Bamwor",
    "Population_SimpleMaps",
    "Population_Starting_List",
    "Population_Size_Class",
    "Capital_Classification",
    "Country_GDP_Per_Capita_USD",
    "Country_GDP_PPP_USD",
    "OpenStreetMap_URL",
    "Wikipedia_Search_URL",
    "Image_Research_URL",
    "Primary_Source",
    "Starting_List_Included",
)
OPTIONAL_COLUMNS = (
    "ISO2",
    "ISO3",
    "Region",
    "Admin1_Name",
    "Timezone",
    "Population_Source",
    "Population_Bamwor",
    "Population_SimpleMaps",
    "Population_Starting_List",
    "Population_Size_Class",
    "Capital_Classification",
    "Country_GDP_Per_Capita_USD",
    "Country_GDP_PPP_USD",
    "OpenStreetMap_URL",
    "Wikipedia_Search_URL",
    "Image_Research_URL",
    "Primary_Source",
    "Starting_List_Included",
)


def normalize_global_city_row(row: Mapping[str, Any], row_number: int) -> NormalizedLocation:
    """Normalize one global city/metro CSV row into the shared schema."""

    raw = {str(key): "" if value is None else str(value) for key, value in row.items()}
    cleaned = normalize_mapping(row)
    coordinates = parse_latitude_longitude(cleaned.get("Latitude"), cleaned.get("Longitude"))
    if coordinates is None:
        raise ValueError("invalid global city latitude/longitude")

    warnings: list[str] = []
    invalid_numeric_count = 0
    invalid_population = False

    population_fields = {
        "Population": parse_int(cleaned.get("Population")),
        "Population_Bamwor": parse_int(cleaned.get("Population_Bamwor")),
        "Population_SimpleMaps": parse_int(cleaned.get("Population_SimpleMaps")),
        "Population_Starting_List": parse_int(cleaned.get("Population_Starting_List")),
    }
    for field_name, parsed_population in population_fields.items():
        warning = numeric_warning(field_name, cleaned.get(field_name), parsed_population)
        if warning:
            warnings.append(warning)
            invalid_numeric_count += 1
            invalid_population = True

    gdp_per_capita = parse_number(cleaned.get("Country_GDP_Per_Capita_USD"))
    gdp_ppp = parse_number(cleaned.get("Country_GDP_PPP_USD"))
    for field_name, parsed_gdp in (
        ("Country_GDP_Per_Capita_USD", gdp_per_capita),
        ("Country_GDP_PPP_USD", gdp_ppp),
    ):
        warning = numeric_warning(field_name, cleaned.get(field_name), parsed_gdp)
        if warning:
            warnings.append(warning)
            invalid_numeric_count += 1

    record_id = cleaned.get("Record_ID") or str(row_number)
    name = cleaned.get("Location_Name") or f"Unnamed global city {row_number}"
    location_type = cleaned.get("Location_Type") or "Metro Area"
    latitude, longitude = coordinates
    record = LocationRecord(
        id=f"{SOURCE_FILE}:{record_id}:{slugify(name)}",
        source_file=SOURCE_FILE,
        map_layer="global_metros",
        country=cleaned.get("Country") or "Unknown",
        location_category="Non-Military",
        dataset_type="metro_area",
        name=name,
        type=location_type,
        latitude=latitude,
        longitude=longitude,
        region=blank_to_none(cleaned.get("Region")),
        admin_area=blank_to_none(cleaned.get("Admin1_Name")),
        iso2=blank_to_none(cleaned.get("ISO2")),
        iso3=blank_to_none(cleaned.get("ISO3")),
        timezone=blank_to_none(cleaned.get("Timezone")),
        population=population_fields["Population"],
        population_source=blank_to_none(cleaned.get("Population_Source")),
        population_bamwor=population_fields["Population_Bamwor"],
        population_simplemaps=population_fields["Population_SimpleMaps"],
        population_starting_list=population_fields["Population_Starting_List"],
        population_size_class=blank_to_none(cleaned.get("Population_Size_Class")),
        capital_classification=blank_to_none(cleaned.get("Capital_Classification")),
        capital_status=blank_to_none(cleaned.get("Capital_Classification")),
        country_gdp_per_capita_usd=gdp_per_capita,
        country_gdp_ppp_usd=gdp_ppp,
        openstreetmap_url=blank_to_none(cleaned.get("OpenStreetMap_URL")),
        wikipedia_search_url=blank_to_none(cleaned.get("Wikipedia_Search_URL")),
        image_research_url=blank_to_none(cleaned.get("Image_Research_URL")),
        primary_source=blank_to_none(cleaned.get("Primary_Source")),
        starting_list_included=parse_bool(cleaned.get("Starting_List_Included")),
        raw=raw,
    )
    return NormalizedLocation(
        record=record,
        invalid_population_count=1 if invalid_population else 0,
        invalid_numeric_count=invalid_numeric_count,
        warnings=tuple(warnings),
    )
