"""Map marker style and GeoJSON generation utilities."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from src.data.schemas import LocationRecord
from src.utils.display import canonical_country, display_country

COUNTRY_COLORS = {
    "Russia": "#c2410c",
    "China": "#2563eb",
    "Iran": "#7c3aed",
    "DPRK": "#be123c",
}
DEFAULT_MARKER_COLOR = "#4b5563"
METRO_MARKER_COLOR = "#15803d"
US_MARKER_COLOR = "#1f2937"
US_MARKER_BORDER = "#f59e0b"
LAYER_COLORS = {
    "global_metros": METRO_MARKER_COLOR,
    "adversary_military": DEFAULT_MARKER_COLOR,
    "us_military": US_MARKER_COLOR,
}
US_SERVICE_STYLES = {
    "Army": {"color": "#365314", "border": "#bef264", "code": "ARM"},
    "Air Force": {"color": "#075985", "border": "#7dd3fc", "code": "AF"},
    "Navy": {"color": "#1e3a8a", "border": "#bfdbfe", "code": "NAV"},
    "Marine Corps": {"color": "#7f1d1d", "border": "#fecaca", "code": "MC"},
    "Washington Headquarters Services": {
        "color": "#3f3f46",
        "border": "#e4e4e7",
        "code": "WHS",
    },
}

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
    if record.map_layer == "global_metros":
        marker_color = METRO_MARKER_COLOR
        type_color = "#86efac"
        type_code_value = "MET"
    elif record.map_layer == "us_military":
        service_style = US_SERVICE_STYLES.get(record.service_branch or record.type, {})
        marker_color = service_style.get("color", US_MARKER_COLOR)
        type_color = service_style.get("border", US_MARKER_BORDER)
        type_code_value = service_style.get("code", type_style.code)
    else:
        marker_color = COUNTRY_COLORS.get(canonical_country(record.country), DEFAULT_MARKER_COLOR)
        type_color = type_style.color
        type_code_value = type_style.code
    return {
        "type": "Feature",
        "geometry": {
            "type": "Point",
            "coordinates": [record.longitude, record.latitude],
        },
        "properties": {
            "id": record.id,
            "name": record.name,
            "country": display_country(record.country),
            "map_layer": record.map_layer,
            "type": record.type,
            "marker_color": marker_color,
            "type_color": type_color,
            "type_code": type_code_value,
            "selected": record.id == selected_id,
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
        "layers": LAYER_COLORS,
        "countries": COUNTRY_COLORS,
        "us_services": US_SERVICE_STYLES,
        "types": [style.to_dict() for style in type_styles.values()],
    }
