"""Sidebar filter and data quality panel."""

from __future__ import annotations

from typing import Any

from dash import html

from src.components.filters import (
    build_country_filter,
    build_location_category_filter,
    build_search_box,
    build_source_filter,
    build_type_filter,
)
from src.data.schemas import LocationRecord


def render_quality_summary(quality: dict[str, Any]) -> Any:
    """Render the data quality summary."""

    source_rows = []
    for source in quality.get("sources", []):
        missing = source.get("missing_optional_fields", {})
        missing_text = ", ".join(f"{field}: {count}" for field, count in missing.items() if count)
        if not missing_text:
            missing_text = "None"
        source_rows.append(
            html.Div(
                className="quality-source",
                children=[
                    html.Div(
                        source.get("source_file", "Unknown source"),
                        className="quality-source-title",
                    ),
                    html.Div(f"Encoding: {source.get('encoding') or 'n/a'}"),
                    html.Div(f"Rows loaded: {source.get('total_rows', 0):,}"),
                    html.Div(f"Plotted: {source.get('plotted_rows', 0):,}"),
                    html.Div(
                        f"Coordinate fixes: {source.get('rows_with_cleaned_coordinates', 0):,}"
                    ),
                    html.Div(
                        f"Invalid coordinates: "
                        f"{source.get('rows_excluded_invalid_coordinates', 0):,}"
                    ),
                    html.Div(
                        f"Invalid/missing population: "
                        f"{source.get('rows_with_invalid_population', 0):,}"
                    ),
                    html.Div(
                        f"Duplicate coordinates: "
                        f"{source.get('duplicate_coordinate_count', 0):,}"
                    ),
                    html.Div(f"Missing optional: {missing_text}"),
                ],
            )
        )

    warnings = quality.get("warnings", [])
    warning_items = warnings[:5]
    return html.Div(
        className="quality-summary",
        children=[
            html.Div("Data Quality", className="section-heading"),
            html.Div(
                className="quality-kpis",
                children=[
                    html.Div(
                        [html.Span(f"{quality.get('total_rows', 0):,}"), html.Small("rows")],
                        className="quality-kpi",
                    ),
                    html.Div(
                        [
                            html.Span(f"{quality.get('plotted_rows', 0):,}"),
                            html.Small("plotted"),
                        ],
                        className="quality-kpi",
                    ),
                    html.Div(
                        [
                            html.Span(f"{quality.get('excluded_rows', 0):,}"),
                            html.Small("excluded"),
                        ],
                        className="quality-kpi",
                    ),
                    html.Div(
                        [
                            html.Span(f"{quality.get('counterforce_records', 0):,}"),
                            html.Small("counterforce"),
                        ],
                        className="quality-kpi",
                    ),
                    html.Div(
                        [
                            html.Span(f"{quality.get('countervalue_records', 0):,}"),
                            html.Small("countervalue"),
                        ],
                        className="quality-kpi",
                    ),
                ],
            ),
            html.Div(source_rows, className="quality-source-list"),
            html.Details(
                className="quality-warnings",
                children=[
                    html.Summary(f"Warnings ({len(warnings)})"),
                    (
                        html.Ul([html.Li(item) for item in warning_items])
                        if warning_items
                        else html.Div("None")
                    ),
                ],
            ),
        ],
    )


def build_sidebar(records: list[LocationRecord], quality: dict[str, Any]) -> Any:
    """Build the filter sidebar."""

    return html.Aside(
        className="sidebar",
        children=[
            html.Div(
                className="sidebar-scroll",
                children=[
                    html.Div("Filters", className="section-heading"),
                    html.Label("Country", className="control-label", htmlFor="country-filter"),
                    build_country_filter(records),
                    html.Label(
                        "Location Category",
                        className="control-label",
                        htmlFor="location-category-filter",
                    ),
                    build_location_category_filter(),
                    html.Label("Type", className="control-label", htmlFor="type-filter"),
                    build_type_filter(records),
                    html.Label("Source File", className="control-label", htmlFor="source-filter"),
                    build_source_filter(records),
                    html.Label("Search", className="control-label", htmlFor="search-input"),
                    build_search_box(),
                    html.Div(id="visible-count", className="visible-count"),
                    render_quality_summary(quality),
                ],
            )
        ],
    )
