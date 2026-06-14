"""Callbacks for map viewport changes."""

from __future__ import annotations

from typing import Any

from dash import Input, Output, State, ctx, no_update

from src.config import INITIAL_CENTER, INITIAL_ZOOM, SELECTED_ZOOM
from src.data.schemas import LocationRecord


def resolve_map_view(
    *,
    triggered_id: Any,
    selected_id: str | None,
    record_by_id: dict[str, LocationRecord],
) -> tuple[list[float], int] | tuple[Any, Any]:
    """Resolve viewport changes for explicit map controls."""

    if triggered_id == "reset-view":
        return INITIAL_CENTER, INITIAL_ZOOM
    if triggered_id == "zoom-to-selected" and selected_id:
        record = record_by_id.get(selected_id)
        if record is None:
            return no_update, no_update
        return [record.latitude, record.longitude], SELECTED_ZOOM
    return no_update, no_update


def register_map_callbacks(app: Any, records: list[LocationRecord]) -> None:
    """Register map viewport callbacks."""

    record_by_id = {record.id: record for record in records}

    @app.callback(
        Output("map", "center"),
        Output("map", "zoom"),
        Input("reset-view", "n_clicks"),
        Input("zoom-to-selected", "n_clicks"),
        State("selected-location-id", "data"),
        prevent_initial_call=True,
    )
    def update_map_view(
        _reset_clicks: int | None,
        _zoom_clicks: int | None,
        selected_id: str | None,
    ) -> tuple[list[float], int] | tuple[Any, Any]:
        triggered = ctx.triggered_id
        return resolve_map_view(
            triggered_id=triggered,
            selected_id=selected_id,
            record_by_id=record_by_id,
        )
