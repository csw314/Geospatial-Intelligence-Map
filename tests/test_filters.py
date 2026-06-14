from __future__ import annotations

from src.callbacks.filter_callbacks import (
    selected_id_visible_in_records,
    type_options_for_country,
    types_for_country,
)
from src.components.filters import country_filter_options
from src.data.schemas import LocationRecord
from src.utils.search import filter_records


def test_country_type_and_source_filtering(sample_records: list[LocationRecord]) -> None:
    filtered = filter_records(
        sample_records,
        country="Russia",
        types=["Air Base"],
        source_files=["russia_data.csv"],
    )

    assert [record.name for record in filtered] == ["Alpha Air Base"]


def test_clear_all_type_filter_returns_no_records(sample_records: list[LocationRecord]) -> None:
    assert filter_records(sample_records, types=[]) == []


def test_combined_search_and_filter_logic(sample_records: list[LocationRecord]) -> None:
    filtered = filter_records(
        sample_records,
        country="China",
        types=["Air Base"],
        source_files=["china_data.csv"],
        query="tianzhushan",
    )

    assert [record.name for record in filtered] == ["Anqing Air Base"]


def test_type_options_are_relevant_to_country(sample_records: list[LocationRecord]) -> None:
    assert types_for_country(sample_records, "Russia") == ["Air Base", "Air Defense"]
    assert types_for_country(sample_records, "China") == ["Air Base", "Metro Area"]
    assert types_for_country(sample_records, "DPRK") == [
        "Metro Area",
        "Missile operating base",
    ]
    assert type_options_for_country(
        sample_records,
        "China",
        active_layers=["adversary_military"],
    ) == [{"label": "Air Base", "value": "Air Base"}]
    assert type_options_for_country(
        sample_records,
        "China",
        active_layers=["global_metros"],
    ) == [{"label": "Metro Area", "value": "Metro Area"}]
    assert type_options_for_country(
        sample_records,
        "DPRK",
        active_layers=["adversary_military"],
    ) == [{"label": "Missile operating base", "value": "Missile operating base"}]
    assert type_options_for_country(
        sample_records,
        "DPRK",
        active_layers=["global_metros"],
    ) == [{"label": "Metro Area", "value": "Metro Area"}]


def test_all_layers_show_military_and_metro(
    sample_records: list[LocationRecord],
) -> None:
    filtered = filter_records(sample_records)

    assert {record.map_layer for record in filtered} == {
        "adversary_military",
        "global_metros",
        "us_military",
    }


def test_adversary_layer_excludes_metro_and_us_rows(
    sample_records: list[LocationRecord],
) -> None:
    filtered = filter_records(sample_records, active_layers=["adversary_military"])

    assert filtered
    assert all(record.map_layer == "adversary_military" for record in filtered)
    assert {record.dataset_type for record in filtered} == {"military"}
    assert {"Russia", "China", "Iran", "DPRK"}.issubset({record.country for record in filtered})


def test_global_metro_layer_excludes_military_rows(
    sample_records: list[LocationRecord],
) -> None:
    filtered = filter_records(sample_records, active_layers=["global_metros"])

    assert [record.name for record in filtered] == ["Chongqing", "Pyongyang"]
    assert {record.source_file for record in filtered} == {"global_cities_metros_100k.csv"}


def test_us_military_layer_excludes_adversary_and_metro_rows(
    sample_records: list[LocationRecord],
) -> None:
    filtered = filter_records(sample_records, active_layers=["us_military"])

    assert [record.name for record in filtered] == ["Ramstein Air Base"]
    assert {record.location_category for record in filtered} == {"Military Site"}
    assert {record.operator_country for record in filtered} == {"United States"}


def test_layer_filter_combines_with_country_and_type(
    sample_records: list[LocationRecord],
) -> None:
    filtered = filter_records(
        sample_records,
        country="China",
        active_layers=["global_metros"],
        types=["Metro Area"],
    )

    assert [record.name for record in filtered] == ["Chongqing"]


def test_country_filter_works_for_iran(sample_records: list[LocationRecord]) -> None:
    filtered = filter_records(
        sample_records,
        country="Iran",
        active_layers=["adversary_military"],
    )

    assert [record.name for record in filtered] == ["Mehrabad International Airport"]


def test_country_filter_works_for_dprk(sample_records: list[LocationRecord]) -> None:
    filtered = filter_records(
        sample_records,
        country="DPRK",
    )

    assert [record.name for record in filtered] == [
        "Pyongyang",
        "Sakkanmol Missile Operating Base",
    ]
    assert {record.country for record in filtered} == {"DPRK", "North Korea"}
    assert {record.source_file for record in filtered} == {
        "dprk_data.csv",
        "global_cities_metros_100k.csv",
    }


def test_country_filter_options_collapse_dprk_and_north_korea(
    sample_records: list[LocationRecord],
) -> None:
    options = country_filter_options(sample_records)
    labels = [option["label"] for option in options]
    values = [option["value"] for option in options]

    assert labels.count("DPRK / North Korea") == 1
    assert "DPRK" in values
    assert "North Korea" not in values


def test_type_options_include_iran_and_dprk_types(
    sample_records: list[LocationRecord],
) -> None:
    options = type_options_for_country(
        sample_records,
        "All",
        active_layers=["adversary_military"],
    )
    values = {option["value"] for option in options}

    assert "Air Base" in values
    assert "Missile operating base" in values


def test_hidden_selected_id_is_removed_from_filtered_geojson_context(
    sample_records: list[LocationRecord],
) -> None:
    russia_record = sample_records[0]
    china_records = filter_records(sample_records, country="China")

    assert selected_id_visible_in_records(china_records, russia_record.id) is None
    assert selected_id_visible_in_records([russia_record], russia_record.id) == russia_record.id


def test_all_military_layers_without_metros(sample_records: list[LocationRecord]) -> None:
    filtered = filter_records(
        sample_records,
        active_layers=["adversary_military", "us_military"],
    )

    assert {record.map_layer for record in filtered} == {"adversary_military", "us_military"}
    assert all(record.map_layer != "global_metros" for record in filtered)


def test_all_layers_disabled_returns_no_records(sample_records: list[LocationRecord]) -> None:
    assert filter_records(sample_records, active_layers=[]) == []


def test_us_layer_matches_host_country_not_operator_country(
    sample_records: list[LocationRecord],
) -> None:
    assert [record.name for record in filter_records(sample_records, country="Germany")] == [
        "Ramstein Air Base"
    ]
    assert filter_records(sample_records, country="United States") == []
