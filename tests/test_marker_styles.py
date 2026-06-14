from __future__ import annotations

from src.data.schemas import LocationRecord
from src.utils.marker_styles import (
    COUNTRY_COLORS,
    US_SERVICE_STYLES,
    build_type_styles,
    legend_payload,
    records_to_geojson,
    type_code,
)


def test_type_style_generation_is_dynamic(sample_records: list[LocationRecord]) -> None:
    styles = build_type_styles([record.type for record in sample_records])

    assert set(styles) == {
        "Air Base",
        "Air Defense",
        "Air Force",
        "Metro Area",
        "Missile operating base",
    }
    assert type_code("Army, Army CORP, Fleet HQ") == "AAC"


def test_records_to_geojson_marks_selected_record(sample_records: list[LocationRecord]) -> None:
    selected_id = sample_records[0].id
    geojson = records_to_geojson(sample_records, selected_id=selected_id)

    assert geojson["type"] == "FeatureCollection"
    assert len(geojson["features"]) == 8
    selected = [feature for feature in geojson["features"] if feature["properties"]["selected"]]
    assert len(selected) == 1
    assert selected[0]["properties"]["id"] == selected_id


def test_metro_geojson_has_distinct_marker_properties(
    sample_records: list[LocationRecord],
) -> None:
    geojson = records_to_geojson(sample_records)
    metro_feature = next(
        feature
        for feature in geojson["features"]
        if feature["properties"]["map_layer"] == "global_metros"
    )

    assert metro_feature["properties"]["type_code"] == "MET"
    assert metro_feature["properties"]["type"] == "Metro Area"
    assert "popup_html" not in metro_feature["properties"]
    assert "raw" not in metro_feature["properties"]


def test_us_military_geojson_has_service_marker_properties(
    sample_records: list[LocationRecord],
) -> None:
    geojson = records_to_geojson(sample_records)
    us_feature = next(
        feature
        for feature in geojson["features"]
        if feature["properties"]["map_layer"] == "us_military"
    )

    assert us_feature["properties"]["type_code"] == "AF"
    assert us_feature["properties"]["type"] == "Air Force"
    assert us_feature["properties"]["marker_color"] == US_SERVICE_STYLES["Air Force"]["color"]


def test_legend_includes_iran_and_dprk(sample_records: list[LocationRecord]) -> None:
    payload = legend_payload(sample_records)

    assert "Iran" in COUNTRY_COLORS
    assert "DPRK" in COUNTRY_COLORS
    assert payload["countries"]["Iran"]
    assert payload["countries"]["DPRK"]
    assert payload["layers"]["global_metros"]
    assert payload["layers"]["us_military"]
    assert payload["us_services"]["Air Force"]["code"] == "AF"
