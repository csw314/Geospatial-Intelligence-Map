"""Map legend component."""

from __future__ import annotations

from typing import Any

from dash import html

from src.utils.display import display_country
from src.utils.layers import MAP_LAYER_SHORT_LABELS


def build_legend(legend: dict[str, Any]) -> Any:
    """Build a collapsible map legend."""

    layer_items = [
        html.Div(
            className="legend-row",
            children=[
                html.Span(className="legend-dot", style={"--legend-color": color}),
                html.Span(MAP_LAYER_SHORT_LABELS.get(layer, layer)),
            ],
        )
        for layer, color in legend.get("layers", {}).items()
    ]
    country_items = [
        html.Div(
            className="legend-row",
            children=[
                html.Span(className="legend-dot", style={"--legend-color": color}),
                html.Span(display_country(country)),
            ],
        )
        for country, color in legend.get("countries", {}).items()
    ]
    service_items = [
        html.Div(
            className="legend-row",
            children=[
                html.Span(
                    service_item.get("code", "?"),
                    className="legend-type-code",
                    style={
                        "--legend-color": service_item.get("color", "#1f2937"),
                        "--legend-border": service_item.get("border", "#f59e0b"),
                    },
                ),
                html.Span(service_name),
            ],
        )
        for service_name, service_item in legend.get("us_services", {}).items()
    ]
    type_items = [
        html.Div(
            className="legend-row",
            children=[
                html.Span(
                    type_item.get("code", "?"),
                    className="legend-type-code",
                    style={"--legend-color": type_item.get("color", "#4b5563")},
                ),
                html.Span(type_item.get("type_name", "Unknown")),
            ],
        )
        for type_item in legend.get("types", [])
    ]
    return html.Details(
        className="map-legend",
        open=False,
        children=[
            html.Summary("Legend"),
            html.Div("Map Layers", className="legend-heading"),
            html.Div(layer_items, className="legend-group"),
            html.Div("Adversary Country", className="legend-heading"),
            html.Div(country_items, className="legend-group"),
            html.Div("U.S. Service", className="legend-heading"),
            html.Div(service_items, className="legend-group"),
            html.Div("Type Codes", className="legend-heading"),
            html.Div(type_items, className="legend-group legend-type-list"),
        ],
    )
