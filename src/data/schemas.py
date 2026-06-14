"""Pydantic schemas for normalized location data."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

SourceFile = Literal[
    "russia_data.csv",
    "china_data.csv",
    "iran_data.csv",
    "dprk_data.csv",
    "global_cities_metros_100k.csv",
    "us_military_sites.csv",
    "metro_areas.csv",
]
MapLayer = Literal["global_metros", "adversary_military", "us_military"]
LocationCategory = Literal["Counterforce", "Countervalue", "Military Site"]
DatasetType = Literal["military", "metro_area"]


class LocationRecord(BaseModel):
    """Normalized internal location schema used by the map and detail UI."""

    model_config = ConfigDict(frozen=True)

    id: str
    source_file: SourceFile
    map_layer: MapLayer
    country: str
    operator_country: str | None = None
    location_category: LocationCategory
    dataset_type: DatasetType
    name: str
    type: str = Field(alias="type")
    latitude: float
    longitude: float
    region: str | None = None
    category_source: str | None = None
    alternate_names: str | None = None
    iata: str | None = None
    icao: str | None = None
    use: str | None = None
    subordinate: str | None = None
    runways: str | None = None
    tenants: str | None = None
    iso2: str | None = None
    iso3: str | None = None
    admin_area: str | None = None
    timezone: str | None = None
    population: int | None = None
    population_proper: int | None = None
    population_source: str | None = None
    population_bamwor: int | None = None
    population_simplemaps: int | None = None
    population_starting_list: int | None = None
    population_size_class: str | None = None
    capital_status: str | None = None
    capital_classification: str | None = None
    country_gdp_per_capita_usd: float | None = None
    country_gdp_ppp_usd: float | None = None
    openstreetmap_url: str | None = None
    wikipedia_search_url: str | None = None
    image_research_url: str | None = None
    primary_source: str | None = None
    starting_list_included: bool | None = None
    source_country_name: str | None = None
    source_url: str | None = None
    component: str | None = None
    service_branch: str | None = None
    component_status: str | None = None
    location_class: str | None = None
    geographic_scope: str | None = None
    nearest_city: str | None = None
    coordinate_quality: str | None = None
    buildings_owned: int | None = None
    buildings_owned_sqft: float | None = None
    buildings_leased: int | None = None
    buildings_leased_sqft: float | None = None
    buildings_other: int | None = None
    buildings_other_sqft: float | None = None
    acres_owned: float | None = None
    total_acres: float | None = None
    plant_replacement_value_m: float | None = None
    coordinate_source_url: str | None = None
    dataset_source_url: str | None = None
    coordinate_audit_status: str | None = None
    coordinate_audit_severity: str | None = None
    coordinate_audit_reason: str | None = None
    coordinate_audit_detected_geography: str | None = None
    coordinate_audit_possible_correction_type: str | None = None
    coordinate_audit_distance_km: float | None = None
    notes: str | None = None
    raw: dict[str, Any]

    @field_validator("latitude")
    @classmethod
    def validate_latitude(cls, value: float) -> float:
        """Validate latitude bounds."""

        if not -90 <= value <= 90:
            raise ValueError("latitude must be between -90 and 90")
        return value

    @field_validator("longitude")
    @classmethod
    def validate_longitude(cls, value: float) -> float:
        """Validate longitude bounds."""

        if not -180 <= value <= 180:
            raise ValueError("longitude must be between -180 and 180")
        return value
