"""Filtering and search helpers for normalized records."""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from typing import Any

from src.data.schemas import LocationRecord
from src.utils.display import canonical_country
from src.utils.layers import normalize_active_layers
from src.utils.text_cleaning import normalize_text

SEARCHABLE_FIELDS = (
    "name",
    "alternate_names",
    "region",
    "category_source",
    "type",
    "notes",
    "iata",
    "icao",
    "use",
    "subordinate",
    "tenants",
    "source_file",
    "map_layer",
    "country",
    "operator_country",
    "location_category",
    "dataset_type",
    "iso2",
    "iso3",
    "admin_area",
    "timezone",
    "population",
    "population_proper",
    "population_source",
    "population_bamwor",
    "population_simplemaps",
    "population_starting_list",
    "population_size_class",
    "capital_status",
    "capital_classification",
    "country_gdp_per_capita_usd",
    "country_gdp_ppp_usd",
    "primary_source",
    "source_country_name",
    "component",
    "service_branch",
    "component_status",
    "location_class",
    "geographic_scope",
    "nearest_city",
    "coordinate_quality",
)
SearchIndex = dict[str, str]


@dataclass(frozen=True)
class SearchResult:
    """A ranked search hit."""

    record: LocationRecord
    rank: int
    label: str


def _normalized_query(query: str | None) -> str:
    return normalize_text(query).casefold()


def _record_values(record: LocationRecord) -> list[str]:
    values: list[str] = []
    for field_name in SEARCHABLE_FIELDS:
        value = getattr(record, field_name)
        if value:
            values.append(str(value))
    for value in record.raw.values():
        if value:
            values.append(str(value))
    return values


def build_search_document(record: LocationRecord) -> str:
    """Build one normalized search document for a record."""

    return " ".join(normalize_text(value).casefold() for value in _record_values(record))


def build_search_index(records: Sequence[LocationRecord]) -> SearchIndex:
    """Build immutable normalized search text for startup-time records."""

    return {record.id: build_search_document(record) for record in records}


def record_matches_query(
    record: LocationRecord,
    query: str | None,
    *,
    search_index: SearchIndex | None = None,
) -> bool:
    """Return True when the record matches a case-insensitive query."""

    normalized_query = _normalized_query(query)
    if not normalized_query:
        return True
    document = search_index.get(record.id) if search_index is not None else None
    if document is None:
        document = build_search_document(record)
    return normalized_query in document


def _rank_record(
    record: LocationRecord,
    query: str,
    *,
    search_index: SearchIndex | None = None,
) -> int | None:
    normalized_query = _normalized_query(query)
    if not normalized_query:
        return 0

    name = normalize_text(record.name).casefold()
    identifiers = [
        normalize_text(value).casefold()
        for value in (record.iata, record.icao)
        if value is not None
    ]
    document = search_index.get(record.id) if search_index is not None else None
    if document is None:
        document = build_search_document(record)

    if name == normalized_query:
        return 0
    if name.startswith(normalized_query):
        return 1
    if normalized_query in identifiers:
        return 2
    if any(value.startswith(normalized_query) for value in identifiers):
        return 3
    if document.startswith(normalized_query) or f" {normalized_query}" in document:
        return 4
    if normalized_query in document:
        return 5
    return None


def search_records(
    records: Sequence[LocationRecord],
    query: str | None,
    *,
    limit: int = 25,
    search_index: SearchIndex | None = None,
) -> list[SearchResult]:
    """Search records and return deterministic ranked results."""

    normalized_query = _normalized_query(query)
    if not normalized_query:
        return []

    results: list[SearchResult] = []
    for record in records:
        rank = _rank_record(record, normalized_query, search_index=search_index)
        if rank is None:
            continue
        label_bits = [record.name, record.country, record.type]
        if record.iata:
            label_bits.append(record.iata)
        results.append(SearchResult(record=record, rank=rank, label=" | ".join(label_bits)))

    results.sort(key=lambda result: (result.rank, result.record.name.casefold(), result.record.id))
    return results[:limit]


def filter_records(
    records: Iterable[LocationRecord],
    *,
    country: str | None = "All",
    active_layers: Sequence[str] | None = None,
    location_category: str | None = None,
    types: Sequence[str] | None = None,
    source_files: Sequence[str] | None = None,
    query: str | None = None,
    search_index: SearchIndex | None = None,
) -> list[LocationRecord]:
    """Apply country, type, source, and text filters."""

    type_set = set(types) if types is not None else None
    source_set = set(source_files) if source_files is not None else None
    layer_set = normalize_active_layers(active_layers)
    country_filter = canonical_country(country)
    if type_set == set() or source_set == set() or layer_set == set():
        return []

    filtered: list[LocationRecord] = []
    for record in records:
        if (
            country_filter
            and country_filter != "All"
            and canonical_country(record.country) != country_filter
        ):
            continue
        if (
            location_category
            and location_category != "All"
            and record.location_category != location_category
        ):
            continue
        if record.map_layer not in layer_set:
            continue
        if type_set is not None and record.type not in type_set:
            continue
        if source_set is not None and record.source_file not in source_set:
            continue
        if not record_matches_query(record, query, search_index=search_index):
            continue
        filtered.append(record)
    return filtered


def records_from_dicts(items: Sequence[dict[str, Any]]) -> list[LocationRecord]:
    """Rehydrate LocationRecord objects from Dash-store dictionaries."""

    return [LocationRecord.model_validate(item) for item in items]
