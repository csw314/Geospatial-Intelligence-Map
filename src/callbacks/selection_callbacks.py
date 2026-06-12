"""Callbacks for selecting records and rendering details."""

from __future__ import annotations

from typing import Any

from dash import ALL, Input, Output, ctx, no_update

from src.components.details_panel import render_details_panel
from src.data.schemas import LocationRecord


def _selected_id_from_click_data(click_data: dict[str, Any] | None) -> str | None:
    if not click_data:
        return None
    properties = click_data.get("properties")
    if properties is None:
        feature = click_data.get("feature", {})
        if isinstance(feature, dict):
            properties = feature.get("properties")
    if isinstance(properties, dict):
        record_id = properties.get("id")
        return str(record_id) if record_id else None
    return None


def register_selection_callbacks(app: Any, records: list[LocationRecord]) -> None:
    """Register selection and detail callbacks."""

    record_by_id = {record.id: record for record in records}

    @app.callback(
        Output("selected-location-id", "data"),
        Input("locations-layer", "clickData"),
        Input({"type": "search-result", "id": ALL}, "n_clicks"),
        Input("clear-selection", "n_clicks"),
        prevent_initial_call=True,
    )
    def update_selected_location(
        click_data: dict[str, Any] | None,
        _search_clicks: list[int | None],
        _clear_clicks: int | None,
    ) -> str | None | Any:
        triggered = ctx.triggered_id
        if triggered == "clear-selection":
            return None
        if triggered == "locations-layer":
            record_id = _selected_id_from_click_data(click_data)
            return record_id if record_id in record_by_id else no_update
        if isinstance(triggered, dict) and triggered.get("type") == "search-result":
            record_id = str(triggered.get("id"))
            return record_id if record_id in record_by_id else no_update
        return no_update

    @app.callback(
        Output("details-panel", "children"),
        Input("selected-location-id", "data"),
    )
    def update_details_panel(selected_id: str | None) -> Any:
        return render_details_panel(record_by_id.get(selected_id or ""))
