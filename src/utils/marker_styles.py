"""Map marker style and GeoJSON generation utilities."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from html import escape
from typing import Any

from src.data.schemas import LocationRecord
from src.utils.copy_helpers import format_lat_lon
from src.utils.display import canonical_country, display_country

COUNTRY_COLORS = {
    "Russia": "#c2410c",
    "China": "#2563eb",
    "Iran": "#7c3aed",
    "DPRK": "#be123c",
}
CATEGORY_COLORS = {
    "Counterforce": "#334155",
    "Countervalue": "#15803d",
}
DEFAULT_MARKER_COLOR = "#4b5563"
METRO_MARKER_COLOR = "#15803d"

TYPE_PALETTE = (
    "#0f766e",
    "#7c3aed",
    "#be123c",
    "#b45309",
    "#047857",
    "#0369a1",
    "#a21caf",
    "#4d7c0f",
    "#dc2626",
    "#4338ca",
    "#0e7490",
    "#854d0e",
)


@dataclass(frozen=True)
class TypeStyle:
    """A derived style for one location type."""

    type_name: str
    color: str
    code: str

    def to_dict(self) -> dict[str, str]:
        """Serialize the type style."""

        return asdict(self)


def type_code(type_name: str) -> str:
    """Create a compact marker code from a dynamic type name."""

    words = [word for word in type_name.replace(",", " ").split() if word]
    if not words:
        return "?"
    if len(words) == 1:
        return words[0][:3].upper()
    return "".join(word[0] for word in words[:3]).upper()


def build_type_styles(types: list[str]) -> dict[str, TypeStyle]:
    """Build stable type styles from the currently loaded data types."""

    styles: dict[str, TypeStyle] = {}
    for index, type_name in enumerate(sorted(set(types), key=str.casefold)):
        styles[type_name] = TypeStyle(
            type_name=type_name,
            color=TYPE_PALETTE[index % len(TYPE_PALETTE)],
            code=type_code(type_name),
        )
    return styles


def all_types(records: list[LocationRecord]) -> list[str]:
    """Return all unique record types in display order."""

    return sorted({record.type for record in records}, key=str.casefold)


def _format_optional_int(value: int | None) -> str | None:
    if value is None:
        return None
    return f"{value:,}"


def _popup_html(record: LocationRecord) -> str:
    optional_fields = [
        ("Region", record.region),
        ("Category Source", record.category_source),
        ("Alternate names", record.alternate_names),
        ("IATA", record.iata),
        ("ICAO", record.icao),
        ("Use", record.use),
        ("Subordinate", record.subordinate),
        ("Runways", record.runways),
        ("Tenants", record.tenants),
        ("ISO2", record.iso2),
        ("Population", _format_optional_int(record.population)),
        ("Population Proper", _format_optional_int(record.population_proper)),
        ("Capital Status", record.capital_status),
        ("Source Country Name", record.source_country_name),
        ("Source URL", record.source_url),
        ("Notes", record.notes),
    ]
    rows = [
        ("Name", record.name),
        ("Country", display_country(record.country)),
        ("Type", record.type),
        ("Coordinates", format_lat_lon(record.latitude, record.longitude)),
        ("Source", record.source_file),
        ("Location category", record.location_category),
    ]
    rows.extend((label, value) for label, value in optional_fields if value)
    body = "".join(
        f"<div><strong>{escape(label)}:</strong> {escape(str(value))}</div>"
        for label, value in rows
    )
    return f'<div class="marker-popup">{body}</div>'


def record_to_feature(
    record: LocationRecord,
    *,
    type_styles: dict[str, TypeStyle],
    selected_id: str | None = None,
) -> dict[str, Any]:
    """Convert one record into a GeoJSON feature."""

    type_style = type_styles.get(record.type) or TypeStyle(
        type_name=record.type,
        color=DEFAULT_MARKER_COLOR,
        code=type_code(record.type),
    )
    marker_color = (
        METRO_MARKER_COLOR
        if record.dataset_type == "metro_area"
        else COUNTRY_COLORS.get(canonical_country(record.country), DEFAULT_MARKER_COLOR)
    )
    type_color = "#86efac" if record.dataset_type == "metro_area" else type_style.color
    type_code_value = "MET" if record.dataset_type == "metro_area" else type_style.code
    return {
        "type": "Feature",
        "geometry": {
            "type": "Point",
            "coordinates": [record.longitude, record.latitude],
        },
        "properties": {
            "id": record.id,
            "name": record.name,
            "country": record.country,
            "type": record.type,
            "source_file": record.source_file,
            "location_category": record.location_category,
            "dataset_type": record.dataset_type,
            "latitude": record.latitude,
            "longitude": record.longitude,
            "region": record.region,
            "marker_color": marker_color,
            "type_color": type_color,
            "type_code": type_code_value,
            "selected": record.id == selected_id,
            "popup_html": _popup_html(record),
        },
    }


def records_to_geojson(
    records: list[LocationRecord],
    *,
    selected_id: str | None = None,
) -> dict[str, Any]:
    """Convert records into a GeoJSON feature collection for Dash Leaflet."""

    type_styles = build_type_styles([record.type for record in records])
    return {
        "type": "FeatureCollection",
        "features": [
            record_to_feature(record, type_styles=type_styles, selected_id=selected_id)
            for record in records
        ],
    }


def legend_payload(records: list[LocationRecord]) -> dict[str, Any]:
    """Return country and dynamic type legend data."""

    type_styles = build_type_styles(all_types(records))
    return {
        "countries": COUNTRY_COLORS,
        "categories": CATEGORY_COLORS,
        "types": [style.to_dict() for style in type_styles.values()],
    }
