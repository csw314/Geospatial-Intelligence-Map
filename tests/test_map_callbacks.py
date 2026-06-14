from __future__ import annotations

from dash import no_update

from src.callbacks.map_callbacks import resolve_map_view
from src.config import INITIAL_CENTER, INITIAL_ZOOM, SELECTED_ZOOM
from src.data.schemas import LocationRecord


def _record_by_id(records: list[LocationRecord]) -> dict[str, LocationRecord]:
    return {record.id: record for record in records}


def test_selection_change_does_not_auto_zoom(sample_records: list[LocationRecord]) -> None:
    assert resolve_map_view(
        triggered_id="selected-location-id",
        selected_id=sample_records[0].id,
        record_by_id=_record_by_id(sample_records),
    ) == (no_update, no_update)


def test_zoom_to_selected_centers_on_record(sample_records: list[LocationRecord]) -> None:
    record = sample_records[0]

    assert resolve_map_view(
        triggered_id="zoom-to-selected",
        selected_id=record.id,
        record_by_id=_record_by_id(sample_records),
    ) == ([record.latitude, record.longitude], SELECTED_ZOOM)


def test_reset_view_resets_only_viewport(sample_records: list[LocationRecord]) -> None:
    assert resolve_map_view(
        triggered_id="reset-view",
        selected_id=sample_records[0].id,
        record_by_id=_record_by_id(sample_records),
    ) == (INITIAL_CENTER, INITIAL_ZOOM)
