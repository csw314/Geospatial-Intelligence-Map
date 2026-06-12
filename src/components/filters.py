"""Filter control builders."""

from __future__ import annotations

from typing import Any

import dash_bootstrap_components as dbc
from dash import dcc, html

from src.data.schemas import LocationRecord
from src.utils.display import canonical_country, display_country
from src.utils.marker_styles import all_types


def country_filter_options(records: list[LocationRecord]) -> list[dict[str, str]]:
    """Build Country filter options with source-specific aliases collapsed."""

    countries = sorted(
        {canonical_country(record.country) for record in records},
        key=lambda country: display_country(country).casefold(),
    )
    return [{"label": "All", "value": "All"}] + [
        {"label": display_country(country), "value": country} for country in countries
    ]


def build_country_filter(records: list[LocationRecord]) -> Any:
    """Build the country radio control."""

    return dbc.RadioItems(
        id="country-filter",
        className="filter-control",
        inputClassName="filter-input",
        labelClassName="filter-label",
        options=country_filter_options(records),
        value="All",
    )


def build_location_category_filter() -> Any:
    """Build the location-category radio control."""

    return dbc.RadioItems(
        id="location-category-filter",
        className="filter-control",
        inputClassName="filter-input",
        labelClassName="filter-label",
        options=[
            {"label": "All", "value": "All"},
            {"label": "Counterforce", "value": "Counterforce"},
            {"label": "Countervalue", "value": "Countervalue"},
        ],
        value="All",
    )


def build_type_filter(records: list[LocationRecord]) -> Any:
    """Build the dynamic type checklist."""

    types = all_types(records)
    return html.Div(
        children=[
            html.Div(
                className="type-actions",
                children=[
                    dbc.Button(
                        "Select All",
                        id="select-all-types",
                        size="sm",
                        color="secondary",
                        outline=True,
                    ),
                    dbc.Button(
                        "Clear All",
                        id="clear-all-types",
                        size="sm",
                        color="secondary",
                        outline=True,
                    ),
                ],
            ),
            dbc.Checklist(
                id="type-filter",
                className="type-checklist",
                inputClassName="filter-input",
                labelClassName="filter-label",
                options=[{"label": type_name, "value": type_name} for type_name in types],
                value=types,
            ),
        ]
    )


def build_source_filter(records: list[LocationRecord]) -> Any:
    """Build the source-file checklist."""

    sources = sorted({record.source_file for record in records})
    return dbc.Checklist(
        id="source-filter",
        className="filter-control",
        inputClassName="filter-input",
        labelClassName="filter-label",
        options=[{"label": source, "value": source} for source in sources],
        value=sources,
    )


def build_search_box() -> Any:
    """Build the search input and result container."""

    return html.Div(
        children=[
            dcc.Input(
                id="search-input",
                type="search",
                placeholder="Search locations",
                debounce=False,
                className="search-input",
                autoComplete="off",
            ),
            html.Div(id="search-results", className="search-results"),
        ]
    )
