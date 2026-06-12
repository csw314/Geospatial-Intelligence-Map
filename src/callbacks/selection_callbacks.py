"""Callbacks for selecting records and rendering details."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from dash import ALL, Input, Output, State, ctx, no_update

from src.components.details_panel import render_details_panel
from src.data.schemas import LocationRecord
from src.utils.marker_styles import all_types
from src.utils.search import filter_records

FILTER_TRIGGER_IDS = {
    "country-filter",
    "location-category-filter",
    "type-filter",
    "source-filter",
    "search-input",
}
CLEAR_SELECTION_TRIGGER_IDS = {"clear-selection", "close-details"}


def selected_id_from_click_data(click_data: dict[str, Any] | None) -> str | None:
    """Extract a record ID from Dash Leaflet GeoJSON click data."""

    if not click_data:
        return None
    properties = click_data.get("properties")
    if properties is None:
        feature = click_data.get("feature", {})
        if isinstance(feature, dict):
            properties = feature.get("properties")
    if isinstance(properties, dict):
        if properties.get("cluster"):
            return None
        record_id = properties.get("id")
        return str(record_id) if record_id else None
    return None


def selected_id_after_filter_change(
    records: list[LocationRecord],
    selected_id: str | None,
    *,
    country: str | None = "All",
    location_category: str | None = "All",
    types: Sequence[str] | None = None,
    source_files: Sequence[str] | None = None,
    query: str | None = None,
) -> str | None | Any:
    """Keep a selection only when the selected record remains visible."""

    if not selected_id:
        return no_update
    filtered = filter_records(
        records,
        country=country,
        location_category=location_category,
        types=types if types is not None else all_types(records),
        source_files=source_files,
        query=query,
    )
    if any(record.id == selected_id for record in filtered):
        return no_update
    return None


def resolve_selected_location(
    *,
    triggered_id: Any,
    click_data: dict[str, Any] | None,
    selected_id: str | None,
    record_by_id: Mapping[str, LocationRecord],
    records: list[LocationRecord],
    country: str | None = "All",
    location_category: str | None = "All",
    types: Sequence[str] | None = None,
    source_files: Sequence[str] | None = None,
    query: str | None = None,
) -> str | None | Any:
    """Resolve the next selected record ID for a Dash trigger."""

    if isinstance(triggered_id, Mapping) and triggered_id.get("type") == "search-result":
        record_id = str(triggered_id.get("id"))
        return record_id if record_id in record_by_id else no_update
    if isinstance(triggered_id, str):
        if triggered_id in CLEAR_SELECTION_TRIGGER_IDS:
            return None
        if triggered_id == "locations-layer":
            clicked_record_id = selected_id_from_click_data(click_data)
            return clicked_record_id if clicked_record_id in record_by_id else no_update
        if triggered_id in FILTER_TRIGGER_IDS:
            return selected_id_after_filter_change(
                records,
                selected_id,
                country=country,
                location_category=location_category,
                types=types,
                source_files=source_files,
                query=query,
            )
    return no_update


def register_selection_callbacks(app: Any, records: list[LocationRecord]) -> None:
    """Register selection and detail callbacks."""

    record_by_id = {record.id: record for record in records}

    @app.callback(
        Output("selected-location-id", "data"),
        Input("locations-layer", "clickData"),
        Input("locations-layer", "n_clicks"),
        Input({"type": "search-result", "id": ALL}, "n_clicks"),
        Input("clear-selection", "n_clicks"),
        Input("close-details", "n_clicks"),
        Input("country-filter", "value"),
        Input("location-category-filter", "value"),
        Input("type-filter", "value"),
        Input("source-filter", "value"),
        Input("search-input", "value"),
        State("selected-location-id", "data"),
        prevent_initial_call=True,
    )
    def update_selected_location(
        click_data: dict[str, Any] | None,
        _map_clicks: int | None,
        _search_clicks: list[int | None],
        _clear_clicks: int | None,
        _close_clicks: int | None,
        country: str | None,
        location_category: str | None,
        selected_types: list[str] | None,
        selected_sources: list[str] | None,
        query: str | None,
        selected_id: str | None,
    ) -> str | None | Any:
        return resolve_selected_location(
            triggered_id=ctx.triggered_id,
            click_data=click_data,
            selected_id=selected_id,
            record_by_id=record_by_id,
            records=records,
            country=country,
            location_category=location_category,
            types=selected_types,
            source_files=selected_sources,
            query=query,
        )

    @app.callback(
        Output("details-panel", "children"),
        Input("selected-location-id", "data"),
    )
    def update_details_panel(selected_id: str | None) -> Any:
        return render_details_panel(record_by_id.get(selected_id or ""))
