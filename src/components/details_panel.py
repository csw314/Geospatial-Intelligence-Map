"""Selected location details panel."""

from __future__ import annotations

from typing import Any

import dash_bootstrap_components as dbc
from dash import dcc, html

from src.data.schemas import LocationRecord
from src.utils.copy_helpers import format_decimal, format_lat_lon
from src.utils.display import display_country


def _is_missing(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return value.strip() == "" or value.strip().casefold() == "nan"
    return False


def _format_optional_int(value: int | None) -> str | None:
    if value is None:
        return None
    return f"{value:,}"


def _format_optional_number(value: float | None, suffix: str = "") -> str | None:
    if value is None:
        return None
    if float(value).is_integer():
        return f"{value:,.0f}{suffix}"
    return f"{value:,.2f}{suffix}"


def _format_currency(value: float | None, suffix: str = "") -> str | None:
    if value is None:
        return None
    if float(value).is_integer():
        return f"${value:,.0f}{suffix}"
    return f"${value:,.2f}{suffix}"


def _format_bool(value: bool | None) -> str | None:
    if value is None:
        return None
    return "Yes" if value else "No"


def _detail_row(label: str, value: Any) -> Any:
    if _is_missing(value):
        return None
    return html.Div(
        className="detail-row",
        children=[
            html.Div(label, className="detail-label"),
            html.Div(value, className="detail-value"),
        ],
    )


def _link_row(label: str, url: str | None, text: str) -> Any:
    if _is_missing(url):
        return None
    return _detail_row(
        label,
        html.A(text, href=url, target="_blank", rel="noopener noreferrer"),
    )


def _detail_section(title: str, rows: list[Any]) -> Any:
    visible_rows = [row for row in rows if row is not None]
    if not visible_rows:
        return None
    return html.Section(
        className="detail-section",
        children=[
            html.Div(title, className="detail-section-title"),
            html.Div(visible_rows, className="details-grid"),
        ],
    )


def _global_city_sections(record: LocationRecord) -> list[Any]:
    return [
        _detail_section(
            "Identity and Geography",
            [
                _detail_row("Location name", record.name),
                _detail_row("Location type", record.type),
                _detail_row("Country", display_country(record.country)),
                _detail_row("ISO2", record.iso2),
                _detail_row("ISO3", record.iso3),
                _detail_row("Region", record.region),
                _detail_row("Admin1", record.admin_area),
                _detail_row("Timezone", record.timezone),
                _detail_row("Latitude", format_decimal(record.latitude)),
                _detail_row("Longitude", format_decimal(record.longitude)),
            ],
        ),
        _detail_section(
            "Population",
            [
                _detail_row("Selected population", _format_optional_int(record.population)),
                _detail_row("Population source", record.population_source),
                _detail_row("Bamwor population", _format_optional_int(record.population_bamwor)),
                _detail_row(
                    "SimpleMaps population",
                    _format_optional_int(record.population_simplemaps),
                ),
                _detail_row(
                    "Starting-list population",
                    _format_optional_int(record.population_starting_list),
                ),
                _detail_row("Population size class", record.population_size_class),
            ],
        ),
        _detail_section(
            "Capital and Economy",
            [
                _detail_row("Capital classification", record.capital_classification),
                _detail_row(
                    "GDP per capita",
                    _format_currency(record.country_gdp_per_capita_usd),
                ),
                _detail_row("GDP PPP", _format_currency(record.country_gdp_ppp_usd)),
            ],
        ),
        _detail_section(
            "Sources and Research Links",
            [
                _detail_row("Primary source", record.primary_source),
                _detail_row("Starting-list included", _format_bool(record.starting_list_included)),
                _link_row("OpenStreetMap", record.openstreetmap_url, "Open map source"),
                _link_row("Wikipedia search", record.wikipedia_search_url, "Search Wikipedia"),
                _link_row("Image research", record.image_research_url, "Search imagery"),
            ],
        ),
    ]


def _us_military_sections(record: LocationRecord) -> list[Any]:
    return [
        _detail_section(
            "Site Identity",
            [
                _detail_row("Site", record.name),
                _detail_row("Component", record.component),
                _detail_row("Service branch", record.service_branch),
                _detail_row("Component status", record.component_status),
                _detail_row("U.S. operator", record.operator_country),
                _detail_row("Host country", display_country(record.country)),
                _detail_row("Administrative area", record.admin_area),
                _detail_row("Location class", record.location_class),
                _detail_row("Geographic scope", record.geographic_scope),
                _detail_row("Nearest city", record.nearest_city),
            ],
        ),
        _detail_section(
            "Coordinates and Quality",
            [
                _detail_row("Latitude", format_decimal(record.latitude)),
                _detail_row("Longitude", format_decimal(record.longitude)),
                _detail_row("Coordinate quality", record.coordinate_quality),
                _link_row(
                    "Coordinate source", record.coordinate_source_url, "Open coordinate source"
                ),
            ],
        ),
        _detail_section(
            "Facilities",
            [
                _detail_row("Buildings owned", _format_optional_int(record.buildings_owned)),
                _detail_row(
                    "Owned square feet", _format_optional_number(record.buildings_owned_sqft)
                ),
                _detail_row("Buildings leased", _format_optional_int(record.buildings_leased)),
                _detail_row(
                    "Leased square feet", _format_optional_number(record.buildings_leased_sqft)
                ),
                _detail_row("Buildings other", _format_optional_int(record.buildings_other)),
                _detail_row(
                    "Other square feet", _format_optional_number(record.buildings_other_sqft)
                ),
                _detail_row("Acres owned", _format_optional_number(record.acres_owned)),
                _detail_row("Total acres", _format_optional_number(record.total_acres)),
                _detail_row(
                    "Plant replacement value",
                    _format_currency(record.plant_replacement_value_m, "M"),
                ),
            ],
        ),
        _detail_section(
            "Sources and Notes",
            [
                _link_row("Dataset source", record.dataset_source_url, "Open dataset source"),
                _detail_row("Notes", record.notes),
                _detail_row(
                    "Unit caveat",
                    (
                        "The source unit of observation is a site, not necessarily an entire "
                        "installation. Coordinates are public representative points or "
                        "approximate centroids."
                    ),
                ),
            ],
        ),
    ]


def _adversary_sections(record: LocationRecord) -> list[Any]:
    return [
        _detail_section(
            "Identity and Location",
            [
                _detail_row("Name", record.name),
                _detail_row("Country", display_country(record.country)),
                _detail_row("Operator", record.operator_country),
                _detail_row("Type", record.type),
                _detail_row("Location category", record.location_category),
                _detail_row("Latitude", format_decimal(record.latitude)),
                _detail_row("Longitude", format_decimal(record.longitude)),
                _detail_row("Source file", record.source_file),
                _detail_row("Region", record.region),
            ],
        ),
        _detail_section(
            "Military Details",
            [
                _detail_row("Category Source", record.category_source),
                _detail_row("Alternate names", record.alternate_names),
                _detail_row("IATA", record.iata),
                _detail_row("ICAO", record.icao),
                _detail_row("Use", record.use),
                _detail_row("Subordinate", record.subordinate),
                _detail_row("Runways", record.runways),
                _detail_row("Tenants", record.tenants),
                _detail_row("Notes", record.notes),
                _link_row("Source URL", record.source_url, "Open source"),
            ],
        ),
    ]


def _detail_sections(record: LocationRecord) -> list[Any]:
    if record.map_layer == "global_metros":
        sections = _global_city_sections(record)
    elif record.map_layer == "us_military":
        sections = _us_military_sections(record)
    else:
        sections = _adversary_sections(record)
    return [section for section in sections if section is not None]


def render_details_panel(record: LocationRecord | None) -> Any:
    """Render the selected location details panel."""

    if record is None:
        return html.Div(
            className="details-empty",
            children=[
                html.Div(
                    className="details-header",
                    children=[
                        html.Div("Location Details", className="section-heading"),
                        dbc.Button(
                            "Close",
                            id="close-details",
                            color="secondary",
                            size="sm",
                            outline=True,
                            disabled=True,
                        ),
                    ],
                ),
                html.Div("No location selected", className="empty-state"),
                html.Div(
                    className="detail-actions",
                    children=[
                        dbc.Button(
                            "Zoom to Location",
                            id="zoom-to-selected",
                            color="primary",
                            size="sm",
                            disabled=True,
                        ),
                        dbc.Button(
                            "Clear Selection",
                            id="clear-selection",
                            color="secondary",
                            size="sm",
                            outline=True,
                            disabled=True,
                        ),
                    ],
                ),
            ],
        )

    coordinate_text = format_lat_lon(record.latitude, record.longitude)
    return html.Div(
        className="details-card",
        children=[
            html.Div(
                className="details-header",
                children=[
                    html.Div("Location Details", className="section-heading"),
                    dbc.Button(
                        "Close",
                        id="close-details",
                        color="secondary",
                        size="sm",
                        outline=True,
                    ),
                ],
            ),
            html.H2(record.name, className="details-title"),
            html.Div(_detail_sections(record), className="details-sections"),
            html.Div(
                className="coordinate-copy",
                children=[
                    html.Div("Copy Coordinates", className="coordinate-label"),
                    html.Code(coordinate_text, id="coordinate-copy-text"),
                    dcc.Clipboard(
                        target_id="coordinate-copy-text",
                        title="Copy coordinates",
                        className="clipboard-button",
                    ),
                ],
            ),
            html.Div(
                className="detail-actions",
                children=[
                    dbc.Button(
                        "Zoom to Location",
                        id="zoom-to-selected",
                        color="primary",
                        size="sm",
                    ),
                    dbc.Button(
                        "Clear Selection",
                        id="clear-selection",
                        color="secondary",
                        size="sm",
                        outline=True,
                    ),
                ],
            ),
        ],
    )
