"""Map legend component."""

from __future__ import annotations

from typing import Any

from dash import html

from src.utils.display import display_country


def build_legend(legend: dict[str, Any]) -> Any:
    """Build a collapsible map legend."""

    category_items = [
        html.Div(
            className="legend-row",
            children=[
                html.Span(className="legend-dot", style={"--legend-color": color}),
                html.Span(category),
            ],
        )
        for category, color in legend.get("categories", {}).items()
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
            html.Div("Location Category", className="legend-heading"),
            html.Div(category_items, className="legend-group"),
            html.Div("Country", className="legend-heading"),
            html.Div(country_items, className="legend-group"),
            html.Div("Type", className="legend-heading"),
            html.Div(type_items, className="legend-group legend-type-list"),
        ],
    )
