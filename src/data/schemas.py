"""Pydantic schemas for normalized location data."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

SourceFile = Literal[
    "russia_data.csv",
    "china_data.csv",
    "iran_data.csv",
    "dprk_data.csv",
    "metro_areas.csv",
]
LocationCategory = Literal["Counterforce", "Countervalue"]
DatasetType = Literal["military", "metro_area"]


class LocationRecord(BaseModel):
    """Normalized internal location schema used by the map and detail UI."""

    model_config = ConfigDict(frozen=True)

    id: str
    source_file: SourceFile
    country: str
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
    population: int | None = None
    population_proper: int | None = None
    capital_status: str | None = None
    source_country_name: str | None = None
    source_url: str | None = None
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
