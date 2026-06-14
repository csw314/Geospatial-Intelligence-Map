"""Robust CSV loading for global location data."""

from __future__ import annotations

from collections import Counter, defaultdict
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from src.data.data_quality import DataQualityReport, DuplicateCoordinate, SourceQualityReport
from src.data.normalize_china import (
    EXPECTED_COLUMNS as CHINA_EXPECTED_COLUMNS,
)
from src.data.normalize_china import (
    OPTIONAL_COLUMNS as CHINA_OPTIONAL_COLUMNS,
)
from src.data.normalize_china import normalize_china_row
from src.data.normalize_dprk import (
    EXPECTED_COLUMNS as DPRK_EXPECTED_COLUMNS,
)
from src.data.normalize_dprk import (
    OPTIONAL_COLUMNS as DPRK_OPTIONAL_COLUMNS,
)
from src.data.normalize_dprk import normalize_dprk_row
from src.data.normalize_global_cities import (
    EXPECTED_COLUMNS as GLOBAL_CITIES_EXPECTED_COLUMNS,
)
from src.data.normalize_global_cities import (
    OPTIONAL_COLUMNS as GLOBAL_CITIES_OPTIONAL_COLUMNS,
)
from src.data.normalize_global_cities import normalize_global_city_row
from src.data.normalize_iran import (
    EXPECTED_COLUMNS as IRAN_EXPECTED_COLUMNS,
)
from src.data.normalize_iran import (
    OPTIONAL_COLUMNS as IRAN_OPTIONAL_COLUMNS,
)
from src.data.normalize_iran import normalize_iran_row
from src.data.normalize_russia import (
    EXPECTED_COLUMNS as RUSSIA_EXPECTED_COLUMNS,
)
from src.data.normalize_russia import (
    OPTIONAL_COLUMNS as RUSSIA_OPTIONAL_COLUMNS,
)
from src.data.normalize_russia import normalize_russia_row
from src.data.normalize_us_military import (
    EXPECTED_COLUMNS as US_MILITARY_EXPECTED_COLUMNS,
)
from src.data.normalize_us_military import (
    OPTIONAL_COLUMNS as US_MILITARY_OPTIONAL_COLUMNS,
)
from src.data.normalize_us_military import normalize_us_military_row
from src.data.schemas import LocationRecord
from src.utils.text_cleaning import normalize_text, row_needed_text_cleanup

ENCODINGS = ("utf-8", "utf-8-sig", "cp1252", "latin1")


@dataclass(frozen=True)
class SourceSpec:
    """Metadata needed to load and normalize one source file."""

    file_name: str
    expected_columns: tuple[str, ...]
    optional_columns: tuple[str, ...]
    normalizer: Callable[[Mapping[str, Any], int], Any]
    alternative_file_names: tuple[str, ...] = ()
    dataset_type: str = "military"
    map_layer: str = "adversary_military"
    location_category: str = "Counterforce"


@dataclass(frozen=True)
class CsvReadResult:
    """A loaded CSV and parsing metadata."""

    frame: pd.DataFrame
    encoding: str
    warnings: list[str]
    bad_line_count: int


@dataclass(frozen=True)
class LocationDataset:
    """All normalized records and their quality report."""

    records: list[LocationRecord]
    quality_report: DataQualityReport

    def records_as_dicts(self) -> list[dict[str, Any]]:
        """Serialize records for Dash stores."""

        return [record.model_dump() for record in self.records]

    def quality_as_dict(self) -> dict[str, Any]:
        """Serialize the data quality report for Dash stores."""

        return self.quality_report.to_dict()


SOURCE_SPECS = (
    SourceSpec(
        file_name="russia_data.csv",
        dataset_type="military",
        map_layer="adversary_military",
        location_category="Counterforce",
        expected_columns=RUSSIA_EXPECTED_COLUMNS,
        optional_columns=RUSSIA_OPTIONAL_COLUMNS,
        normalizer=normalize_russia_row,
    ),
    SourceSpec(
        file_name="china_data.csv",
        dataset_type="military",
        map_layer="adversary_military",
        location_category="Counterforce",
        expected_columns=CHINA_EXPECTED_COLUMNS,
        optional_columns=CHINA_OPTIONAL_COLUMNS,
        normalizer=normalize_china_row,
    ),
    SourceSpec(
        file_name="iran_data.csv",
        dataset_type="military",
        map_layer="adversary_military",
        location_category="Counterforce",
        expected_columns=IRAN_EXPECTED_COLUMNS,
        optional_columns=IRAN_OPTIONAL_COLUMNS,
        normalizer=normalize_iran_row,
    ),
    SourceSpec(
        file_name="dprk_data.csv",
        dataset_type="military",
        map_layer="adversary_military",
        location_category="Counterforce",
        expected_columns=DPRK_EXPECTED_COLUMNS,
        optional_columns=DPRK_OPTIONAL_COLUMNS,
        normalizer=normalize_dprk_row,
    ),
    SourceSpec(
        file_name="global_cities_metros_100k.csv",
        alternative_file_names=("Global_Cities_Metros_100k_Locations_Core.csv",),
        dataset_type="metro_area",
        map_layer="global_metros",
        location_category="Countervalue",
        expected_columns=GLOBAL_CITIES_EXPECTED_COLUMNS,
        optional_columns=GLOBAL_CITIES_OPTIONAL_COLUMNS,
        normalizer=normalize_global_city_row,
    ),
    SourceSpec(
        file_name="us_military_sites.csv",
        alternative_file_names=(
            "US_Military_Site.csv",
            "US_Military_Sites_Worldwide_FY2024_Geospatial.csv",
        ),
        dataset_type="military",
        map_layer="us_military",
        location_category="Military Site",
        expected_columns=US_MILITARY_EXPECTED_COLUMNS,
        optional_columns=US_MILITARY_OPTIONAL_COLUMNS,
        normalizer=normalize_us_military_row,
    ),
)


def _make_bad_line_collector(bad_lines: list[list[str]]) -> Callable[[list[str]], None]:
    def collect_bad_line(fields: list[str]) -> None:
        bad_lines.append(fields)
        return None

    return collect_bad_line


def read_csv_robust(path: Path) -> CsvReadResult:
    """Read a CSV using the configured encoding fallback strategy."""

    if not path.exists():
        raise FileNotFoundError(f"{path} does not exist")

    decode_errors: list[str] = []
    for encoding in ENCODINGS:
        bad_lines: list[list[str]] = []
        collect_bad_line = _make_bad_line_collector(bad_lines)

        try:
            frame = pd.read_csv(
                path,
                dtype=str,
                keep_default_na=False,
                na_filter=False,
                encoding=encoding,
                engine="python",
                on_bad_lines=collect_bad_line,
            )
        except UnicodeDecodeError as exc:
            decode_errors.append(f"{encoding}: {exc}")
            continue
        warnings = [f"Skipped malformed CSV line with fields: {line}" for line in bad_lines]
        if decode_errors:
            warnings.insert(0, f"Encoding fallback used after: {'; '.join(decode_errors)}")
        return CsvReadResult(
            frame=frame,
            encoding=encoding,
            warnings=warnings,
            bad_line_count=len(bad_lines),
        )

    raise UnicodeDecodeError("csv", b"", 0, 1, "unable to decode with configured encodings")


def _ensure_expected_columns(
    frame: pd.DataFrame,
    expected_columns: tuple[str, ...],
    report: SourceQualityReport,
) -> pd.DataFrame:
    missing_columns = [column for column in expected_columns if column not in frame.columns]
    if missing_columns:
        report.parsing_warnings.append(
            f"Missing expected columns filled with blanks: {', '.join(missing_columns)}"
        )
        frame = frame.copy()
        for column in missing_columns:
            frame[column] = ""
    return frame


def _coordinate_fields_needed_cleanup(row: Mapping[str, Any]) -> bool:
    for field_name in ("Latitude", "Longitude"):
        if field_name in row and str(row[field_name]) != normalize_text(row[field_name]):
            return True
    return False


def _load_source(
    data_dir: Path,
    spec: SourceSpec,
) -> tuple[list[LocationRecord], SourceQualityReport]:
    report = SourceQualityReport(
        source_file=spec.file_name,
        dataset_type=spec.dataset_type,
        map_layer=spec.map_layer,
        location_category=spec.location_category,
    )
    records: list[LocationRecord] = []

    try:
        source_path = next(
            path
            for path in (
                data_dir / spec.file_name,
                *(data_dir / name for name in spec.alternative_file_names),
            )
            if path.exists()
        )
        read_result = read_csv_robust(source_path)
    except Exception as exc:  # noqa: BLE001 - one source failing should not crash the app.
        report.load_error = str(exc)
        return records, report
    if source_path.name != spec.file_name:
        report.parsing_warnings.append(
            f"Loaded alternate filename {source_path.name}; normalized as {spec.file_name}"
        )

    frame = _ensure_expected_columns(read_result.frame, spec.expected_columns, report)
    report.encoding = read_result.encoding
    report.total_rows = len(frame) + read_result.bad_line_count
    report.parsing_warnings.extend(read_result.warnings)

    missing_optional_fields: Counter[str] = Counter()
    for index, row in frame.iterrows():
        row_number = int(index) + 2
        row_dict = {column: row.get(column, "") for column in frame.columns}
        if row_needed_text_cleanup(row_dict):
            report.rows_with_text_cleanup += 1
        for column in spec.optional_columns:
            if normalize_text(row_dict.get(column)) == "":
                missing_optional_fields[column] += 1

        try:
            normalized = spec.normalizer(row_dict, row_number)
        except ValueError as exc:
            report.rows_excluded_invalid_coordinates += 1
            report.parsing_warnings.append(f"Row {row_number}: {exc}")
            continue

        if normalized.coordinate_cleaned or _coordinate_fields_needed_cleanup(row_dict):
            report.rows_with_cleaned_coordinates += 1
        report.rows_with_invalid_population += normalized.invalid_population_count
        report.rows_with_numeric_parse_warnings += normalized.invalid_numeric_count
        for warning in normalized.warnings:
            report.parsing_warnings.append(f"Row {row_number}: {warning}")
        records.append(normalized.record)

    report.plotted_rows = len(records)
    report.missing_optional_fields = dict(missing_optional_fields)
    return records, report


def _find_duplicates(records: list[LocationRecord]) -> list[DuplicateCoordinate]:
    grouped: dict[tuple[float, float], list[LocationRecord]] = defaultdict(list)
    for record in records:
        grouped[(round(record.latitude, 6), round(record.longitude, 6))].append(record)

    duplicates: list[DuplicateCoordinate] = []
    for (latitude, longitude), items in sorted(grouped.items()):
        if len(items) < 2:
            continue
        duplicates.append(
            DuplicateCoordinate(
                latitude=latitude,
                longitude=longitude,
                record_ids=[item.id for item in items],
                names=[item.name for item in items],
            )
        )
    return duplicates


def load_location_dataset(data_dir: Path) -> LocationDataset:
    """Load all configured source CSVs."""

    records: list[LocationRecord] = []
    source_reports: list[SourceQualityReport] = []
    for spec in SOURCE_SPECS:
        source_records, source_report = _load_source(data_dir, spec)
        records.extend(source_records)
        source_reports.append(source_report)

    duplicates = _find_duplicates(records)
    duplicate_ids = {record_id for duplicate in duplicates for record_id in duplicate.record_ids}
    for source_report in source_reports:
        source_report.duplicate_coordinate_count = sum(
            1
            for record in records
            if record.source_file == source_report.source_file and record.id in duplicate_ids
        )

    quality_report = DataQualityReport(
        sources=source_reports,
        duplicate_coordinates=duplicates,
    )
    return LocationDataset(records=records, quality_report=quality_report)
