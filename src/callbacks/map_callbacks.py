"""Callbacks for map viewport changes."""

from __future__ import annotations

from typing import Any

from dash import Input, Output, ctx, no_update

from src.config import INITIAL_CENTER, INITIAL_ZOOM, SELECTED_ZOOM
from src.data.schemas import LocationRecord


def register_map_callbacks(app: Any, records: list[LocationRecord]) -> None:
    """Register map viewport callbacks."""

    record_by_id = {record.id: record for record in records}

    @app.callback(
        Output("map", "center"),
        Output("map", "zoom"),
        Input("reset-view", "n_clicks"),
        Input("selected-location-id", "data"),
        Input("zoom-to-selected", "n_clicks"),
        prevent_initial_call=True,
    )
    def update_map_view(
        _reset_clicks: int | None,
        selected_id: str | None,
        _zoom_clicks: int | None,
    ) -> tuple[list[float], int] | tuple[Any, Any]:
        triggered = ctx.triggered_id
        if triggered == "reset-view":
            return INITIAL_CENTER, INITIAL_ZOOM
        if triggered in {"selected-location-id", "zoom-to-selected"} and selected_id:
            record = record_by_id.get(selected_id)
            if record is None:
                return no_update, no_update
            return [record.latitude, record.longitude], SELECTED_ZOOM
        return no_update, no_update
