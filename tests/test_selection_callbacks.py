from __future__ import annotations

from dash import no_update

from src.callbacks.selection_callbacks import (
    resolve_selected_location,
    selected_id_after_filter_change,
    selected_id_from_click_data,
)
from src.data.schemas import LocationRecord


def _record_by_name(records: list[LocationRecord], name: str) -> LocationRecord:
    return next(record for record in records if record.name == name)


def _record_by_id(records: list[LocationRecord]) -> dict[str, LocationRecord]:
    return {record.id: record for record in records}


def test_geojson_feature_click_data_selects_record(
    sample_records: list[LocationRecord],
) -> None:
    record = sample_records[0]
    click_data = {"type": "Feature", "properties": {"id": record.id}}

    assert selected_id_from_click_data(click_data) == record.id
    assert (
        resolve_selected_location(
            triggered_id="locations-layer",
            click_data=click_data,
            selected_id=None,
            record_by_id=_record_by_id(sample_records),
            records=sample_records,
        )
        == record.id
    )


def test_nested_feature_click_data_remains_supported(
    sample_records: list[LocationRecord],
) -> None:
    record = sample_records[1]
    click_data = {"feature": {"properties": {"id": record.id}}}

    assert selected_id_from_click_data(click_data) == record.id


def test_cluster_and_malformed_click_data_are_ignored() -> None:
    cluster_click = {"type": "Feature", "properties": {"cluster": True, "id": "cluster-1"}}

    assert selected_id_from_click_data(cluster_click) is None
    assert selected_id_from_click_data({"type": "Feature", "properties": {"name": "No ID"}}) is None
    assert selected_id_from_click_data({"latlng": [38.0, 126.0]}) is None


def test_close_and_clear_selection_clear_selected_id(
    sample_records: list[LocationRecord],
) -> None:
    selected_id = sample_records[0].id

    for trigger_id in ("close-details", "clear-selection"):
        assert (
            resolve_selected_location(
                triggered_id=trigger_id,
                click_data=None,
                selected_id=selected_id,
                record_by_id=_record_by_id(sample_records),
                records=sample_records,
            )
            is None
        )


def test_search_result_trigger_selects_record(
    sample_records: list[LocationRecord],
) -> None:
    record = sample_records[0]

    assert (
        resolve_selected_location(
            triggered_id={"type": "search-result", "id": record.id},
            click_data=None,
            selected_id=None,
            record_by_id=_record_by_id(sample_records),
            records=sample_records,
        )
        == record.id
    )


def test_same_marker_can_be_reselected_after_close(
    sample_records: list[LocationRecord],
) -> None:
    record = sample_records[0]
    record_by_id = _record_by_id(sample_records)
    closed_id = resolve_selected_location(
        triggered_id="close-details",
        click_data=None,
        selected_id=record.id,
        record_by_id=record_by_id,
        records=sample_records,
    )
    reopened_id = resolve_selected_location(
        triggered_id="locations-layer",
        click_data={"type": "Feature", "properties": {"id": record.id}},
        selected_id=closed_id,
        record_by_id=record_by_id,
        records=sample_records,
    )

    assert closed_id is None
    assert reopened_id == record.id


def test_filter_change_clears_hidden_selection(
    sample_records: list[LocationRecord],
) -> None:
    russia_record = _record_by_name(sample_records, "Alpha Air Base")

    assert (
        selected_id_after_filter_change(
            sample_records,
            russia_record.id,
            country="China",
        )
        is None
    )
    assert (
        selected_id_after_filter_change(
            sample_records,
            russia_record.id,
            country="Russia",
        )
        is no_update
    )


def test_search_filter_change_clears_hidden_selection(
    sample_records: list[LocationRecord],
) -> None:
    russia_record = _record_by_name(sample_records, "Alpha Air Base")

    assert (
        selected_id_after_filter_change(
            sample_records,
            russia_record.id,
            query="Sakkanmol",
        )
        is None
    )


def test_layer_filter_change_preserves_selection_when_layer_remains_visible(
    sample_records: list[LocationRecord],
) -> None:
    city = _record_by_name(sample_records, "Chongqing")

    assert (
        selected_id_after_filter_change(
            sample_records,
            city.id,
            active_layers=["global_metros", "us_military"],
        )
        is no_update
    )


def test_layer_filter_change_clears_selection_when_layer_hidden(
    sample_records: list[LocationRecord],
) -> None:
    city = _record_by_name(sample_records, "Chongqing")

    assert (
        selected_id_after_filter_change(
            sample_records,
            city.id,
            active_layers=["adversary_military", "us_military"],
        )
        is None
    )
