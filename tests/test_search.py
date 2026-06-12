from __future__ import annotations

from src.data.schemas import LocationRecord
from src.utils.search import record_matches_query, search_records


def test_search_across_relevant_fields(sample_records: list[LocationRecord]) -> None:
    anqing = sample_records[2]
    assert record_matches_query(anqing, "AQG")
    assert record_matches_query(anqing, "bomber")
    assert record_matches_query(anqing, "tianzhushan")
    assert not record_matches_query(anqing, "nope")


def test_search_ranking_prefers_exact_and_prefix_name(sample_records: list[LocationRecord]) -> None:
    results = search_records(sample_records, "Anqing")
    assert results[0].record.name == "Anqing Air Base"
    assert results[0].rank == 1

    exact = search_records(sample_records, "Alpha Air Base")
    assert exact[0].record.name == "Alpha Air Base"
    assert exact[0].rank == 0


def test_search_finds_metro_by_city_region_and_population(
    sample_records: list[LocationRecord],
) -> None:
    by_city = search_records(sample_records, "Chongqing")
    by_region = search_records(sample_records, "Chongqing")
    by_population = search_records(sample_records, "32,054,159")

    assert by_city[0].record.source_file == "metro_areas.csv"
    assert by_city[0].record.location_category == "Countervalue"
    assert by_region[0].record.name == "Chongqing"
    assert by_population[0].record.name == "Chongqing"


def test_search_finds_iran_by_name_and_notes(sample_records: list[LocationRecord]) -> None:
    by_name = search_records(sample_records, "Mehrabad")
    by_notes = search_records(sample_records, "F-14s")

    assert by_name[0].record.source_file == "iran_data.csv"
    assert by_name[0].record.country == "Iran"
    assert by_name[0].record.location_category == "Counterforce"
    assert by_notes[0].record.name == "Mehrabad International Airport"


def test_search_finds_dprk_by_name_and_category_source(
    sample_records: list[LocationRecord],
) -> None:
    by_name = search_records(sample_records, "Sakkanmol")
    by_source = search_records(sample_records, "Rocket launch site")

    assert by_name[0].record.source_file == "dprk_data.csv"
    assert by_name[0].record.country == "DPRK"
    assert by_name[0].record.location_category == "Counterforce"
    assert by_source[0].record.name == "Sakkanmol Missile Operating Base"
