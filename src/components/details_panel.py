"""Selected location details panel."""

from __future__ import annotations

from typing import Any

import dash_bootstrap_components as dbc
from dash import dcc, html

from src.data.schemas import LocationRecord
from src.utils.copy_helpers import format_decimal, format_lat_lon
from src.utils.display import display_country


def _format_optional_int(value: int | None) -> str | None:
    if value is None:
        return None
    return f"{value:,}"


def _detail_row(label: str, value: Any) -> Any:
    if value is None or value == "":
        return None
    return html.Div(
        className="detail-row",
        children=[
            html.Div(label, className="detail-label"),
            html.Div(str(value), className="detail-value"),
        ],
    )


def render_details_panel(record: LocationRecord | None) -> Any:
    """Render the selected location details panel."""

    if record is None:
        return html.Div(
            className="details-empty",
            children=[
                html.Div("Location Details", className="section-heading"),
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
    rows = [
        _detail_row("Name", record.name),
        _detail_row("Country", display_country(record.country)),
        _detail_row("Type", record.type),
        _detail_row("Location category", record.location_category),
        _detail_row("Latitude", format_decimal(record.latitude)),
        _detail_row("Longitude", format_decimal(record.longitude)),
        _detail_row("Source file", record.source_file),
        _detail_row("Region", record.region),
        _detail_row("Category Source", record.category_source),
        _detail_row("Alternate names", record.alternate_names),
        _detail_row("IATA", record.iata),
        _detail_row("ICAO", record.icao),
        _detail_row("Use", record.use),
        _detail_row("Subordinate", record.subordinate),
        _detail_row("Runways", record.runways),
        _detail_row("Tenants", record.tenants),
        _detail_row("ISO2", record.iso2),
        _detail_row("Population", _format_optional_int(record.population)),
        _detail_row("Population Proper", _format_optional_int(record.population_proper)),
        _detail_row("Capital Status", record.capital_status),
        _detail_row("Source Country Name", record.source_country_name),
        _detail_row("Source URL", record.source_url),
        _detail_row("Notes", record.notes),
    ]
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
            html.Div([row for row in rows if row is not None], className="details-grid"),
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
