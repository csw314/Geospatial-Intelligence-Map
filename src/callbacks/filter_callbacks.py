"""Callbacks for filtering records and updating map data."""

from __future__ import annotations

from collections import Counter
from typing import Any

from dash import Input, Output, State, ctx

from src.callbacks.search_callbacks import render_search_results
from src.data.schemas import LocationRecord
from src.utils.display import canonical_country
from src.utils.layers import ALL_MAP_LAYERS
from src.utils.marker_styles import all_types, records_to_geojson
from src.utils.search import filter_records, search_records


def types_for_filter_context(
    records: list[LocationRecord],
    country: str | None,
    active_layers: list[str] | None = None,
    location_category: str | None = None,
    source_files: list[str] | None = None,
) -> list[str]:
    """Return dynamic type names relevant to the selected filters."""

    source_set = set(source_files) if source_files is not None else None
    layer_set = set(active_layers) if active_layers is not None else set(ALL_MAP_LAYERS)
    country_filter = canonical_country(country)
    return sorted(
        {
            record.type
            for record in records
            if (
                not country_filter
                or country_filter == "All"
                or canonical_country(record.country) == country_filter
            )
            and record.map_layer in layer_set
            and (
                not location_category
                or location_category == "All"
                or record.location_category == location_category
            )
            and (source_set is None or record.source_file in source_set)
        },
        key=str.casefold,
    )


def types_for_country(records: list[LocationRecord], country: str | None) -> list[str]:
    """Return dynamic type names relevant to the selected country."""

    return types_for_filter_context(records, country)


def type_options_for_country(
    records: list[LocationRecord],
    country: str | None,
    active_layers: list[str] | None = None,
    location_category: str | None = None,
    source_files: list[str] | None = None,
) -> list[dict[str, str]]:
    """Build Dash checklist options for the selected filter context."""

    return [
        {"label": type_name, "value": type_name}
        for type_name in types_for_filter_context(
            records,
            country,
            active_layers,
            location_category,
            source_files,
        )
    ]


def _option_values(options: list[dict[str, Any]] | None) -> list[str]:
    if not options:
        return []
    return [str(option["value"]) for option in options]


def selected_id_visible_in_records(
    records: list[LocationRecord],
    selected_id: str | None,
) -> str | None:
    """Return selected_id only when it exists in the visible record set."""

    if selected_id and any(record.id == selected_id for record in records):
        return selected_id
    return None


def register_filter_callbacks(app: Any, records: list[LocationRecord]) -> None:
    """Register filter and search callbacks."""

    @app.callback(
        Output("type-filter", "options"),
        Output("type-filter", "value"),
        Input("country-filter", "value"),
        Input("active-layers", "value"),
        Input("source-filter", "value"),
        Input("select-all-types", "n_clicks"),
        Input("clear-all-types", "n_clicks"),
        State("type-filter", "value"),
        prevent_initial_call=True,
    )
    def update_type_selection(
        country: str | None,
        active_layers: list[str] | None,
        selected_sources: list[str] | None,
        _select_clicks: int | None,
        _clear_clicks: int | None,
        _selected_types: list[str] | None,
    ) -> tuple[list[dict[str, str]], list[str]]:
        options = type_options_for_country(
            records,
            country=country,
            active_layers=active_layers,
            source_files=selected_sources,
        )
        available_types = _option_values(options)
        triggered = ctx.triggered_id
        if triggered == "clear-all-types":
            return options, []
        return options, available_types

    @app.callback(
        Output("locations-layer", "data"),
        Output("visible-count", "children"),
        Output("search-results", "children"),
        Input("country-filter", "value"),
        Input("active-layers", "value"),
        Input("type-filter", "value"),
        Input("source-filter", "value"),
        Input("search-input", "value"),
        Input("selected-location-id", "data"),
    )
    def update_filtered_records(
        country: str | None,
        active_layers: list[str] | None,
        selected_types: list[str] | None,
        selected_sources: list[str] | None,
        query: str | None,
        selected_id: str | None,
    ) -> tuple[dict[str, Any], str, Any]:
        filtered = filter_records(
            records,
            country=country,
            active_layers=active_layers,
            types=selected_types if selected_types is not None else all_types(records),
            source_files=selected_sources,
            query=query,
        )
        search_base = filter_records(
            records,
            country=country,
            active_layers=active_layers,
            types=selected_types if selected_types is not None else all_types(records),
            source_files=selected_sources,
            query=None,
        )
        search_results = search_records(search_base, query, limit=20)
        layer_counts = Counter(record.map_layer for record in filtered)
        count_text = (
            f"{len(filtered):,} visible of {len(records):,} plotted | "
            f"Global metros: {layer_counts.get('global_metros', 0):,} | "
            f"Adversary military: {layer_counts.get('adversary_military', 0):,} | "
            f"U.S. military: {layer_counts.get('us_military', 0):,}"
        )
        return (
            records_to_geojson(
                filtered,
                selected_id=selected_id_visible_in_records(filtered, selected_id),
            ),
            count_text,
            render_search_results(search_results, query),
        )
