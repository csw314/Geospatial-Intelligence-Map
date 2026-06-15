"""Robust CSV loading for global location data."""

from __future__ import annotations

from collections import Counter, defaultdict
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from src.config import CoordinateAuditMode
from src.data.coordinate_audit import audit_us_military_records
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
    required_columns: tuple[str, ...]
    optional_columns: tuple[str, ...]
    normalizer: Callable[[Mapping[str, Any], int], Any]
    alternative_file_names: tuple[str, ...] = ()
    dataset_type: str = "military"
    map_layer: str = "adversary_military"
    location_category: str = "Counterforce"
    required_nonempty_columns: tuple[str, ...] = ()
    expected_exact_rows: int | None = None
    expected_distinct_counts: Mapping[str, int] | None = None
    expected_value_counts: Mapping[str, Mapping[str, int]] | None = None


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


def _required_columns(
    expected_columns: tuple[str, ...],
    optional_columns: tuple[str, ...],
) -> tuple[str, ...]:
    optional_set = set(optional_columns)
    return tuple(column for column in expected_columns if column not in optional_set)


SOURCE_SPECS = (
    SourceSpec(
        file_name="russia_data.csv",
        dataset_type="military",
        map_layer="adversary_military",
        location_category="Counterforce",
        required_columns=_required_columns(RUSSIA_EXPECTED_COLUMNS, RUSSIA_OPTIONAL_COLUMNS),
        optional_columns=RUSSIA_OPTIONAL_COLUMNS,
        normalizer=normalize_russia_row,
    ),
    SourceSpec(
        file_name="china_data.csv",
        dataset_type="military",
        map_layer="adversary_military",
        location_category="Counterforce",
        required_columns=_required_columns(CHINA_EXPECTED_COLUMNS, CHINA_OPTIONAL_COLUMNS),
        optional_columns=CHINA_OPTIONAL_COLUMNS,
        normalizer=normalize_china_row,
    ),
    SourceSpec(
        file_name="iran_data.csv",
        dataset_type="military",
        map_layer="adversary_military",
        location_category="Counterforce",
        required_columns=_required_columns(IRAN_EXPECTED_COLUMNS, IRAN_OPTIONAL_COLUMNS),
        optional_columns=IRAN_OPTIONAL_COLUMNS,
        normalizer=normalize_iran_row,
    ),
    SourceSpec(
        file_name="dprk_data.csv",
        dataset_type="military",
        map_layer="adversary_military",
        location_category="Counterforce",
        required_columns=_required_columns(DPRK_EXPECTED_COLUMNS, DPRK_OPTIONAL_COLUMNS),
        optional_columns=DPRK_OPTIONAL_COLUMNS,
        normalizer=normalize_dprk_row,
    ),
    SourceSpec(
        file_name="global_cities_metros_100k.csv",
        alternative_file_names=("Global_Cities_Metros_100k_Locations_Core.csv",),
        dataset_type="metro_area",
        map_layer="global_metros",
        location_category="Non-Military",
        required_columns=_required_columns(
            GLOBAL_CITIES_EXPECTED_COLUMNS,
            GLOBAL_CITIES_OPTIONAL_COLUMNS,
        ),
        optional_columns=GLOBAL_CITIES_OPTIONAL_COLUMNS,
        normalizer=normalize_global_city_row,
        required_nonempty_columns=("Record_ID", "Latitude", "Longitude"),
        expected_exact_rows=7027,
        expected_distinct_counts={"Country": 180},
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
        required_columns=_required_columns(
            US_MILITARY_EXPECTED_COLUMNS,
            US_MILITARY_OPTIONAL_COLUMNS,
        ),
        optional_columns=US_MILITARY_OPTIONAL_COLUMNS,
        normalizer=normalize_us_military_row,
        required_nonempty_columns=("Record_ID", "Latitude", "Longitude"),
        expected_exact_rows=1626,
        expected_distinct_counts={"Host_Country": 40},
        expected_value_counts={
            "Service_Branch": {
                "Army": 623,
                "Air Force": 469,
                "Navy": 452,
                "Marine Corps": 80,
                "Washington Headquarters Services": 2,
            }
        },
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


def _validate_and_prepare_columns(
    frame: pd.DataFrame,
    required_columns: tuple[str, ...],
    optional_columns: tuple[str, ...],
    report: SourceQualityReport,
) -> pd.DataFrame:
    missing_required = [column for column in required_columns if column not in frame.columns]
    if missing_required:
        report.schema_validation_failed = True
        report.validation_errors.append(f"Missing required columns: {', '.join(missing_required)}")
        return frame

    missing_optional = [column for column in optional_columns if column not in frame.columns]
    if missing_optional:
        report.validation_warnings.append(
            f"Missing optional columns filled with blanks: {', '.join(missing_optional)}"
        )
        frame = frame.copy()
        for column in missing_optional:
            frame[column] = ""
    return frame


def _validate_source_frame(
    frame: pd.DataFrame,
    spec: SourceSpec,
    report: SourceQualityReport,
) -> None:
    if spec.expected_exact_rows is not None and len(frame) != spec.expected_exact_rows:
        report.expected_row_count_failed = True
        report.validation_warnings.append(
            f"Expected {spec.expected_exact_rows:,} rows but loaded {len(frame):,}"
        )

    for column in spec.required_nonempty_columns:
        if column not in frame.columns:
            continue
        blank_count = sum(1 for value in frame[column] if normalize_text(value) == "")
        if blank_count:
            report.schema_validation_failed = True
            report.validation_errors.append(
                f"Required column {column} contains {blank_count:,} blank values"
            )

    for column, expected_count in (spec.expected_distinct_counts or {}).items():
        if column not in frame.columns:
            continue
        actual_count = frame[column].nunique()
        if actual_count != expected_count:
            report.expected_row_count_failed = True
            report.validation_warnings.append(
                f"Expected {expected_count:,} distinct {column} values but found "
                f"{actual_count:,}"
            )

    for column, expected_counts in (spec.expected_value_counts or {}).items():
        if column not in frame.columns:
            continue
        actual_counts = Counter(str(value) for value in frame[column])
        for value, expected_count in expected_counts.items():
            actual_count = actual_counts.get(value, 0)
            if actual_count != expected_count:
                report.expected_row_count_failed = True
                report.validation_warnings.append(
                    f"Expected {expected_count:,} {column}={value} rows but found "
                    f"{actual_count:,}"
                )


def _coordinate_fields_needed_cleanup(row: Mapping[str, Any]) -> bool:
    for field_name in ("Latitude", "Longitude"):
        if field_name in row and str(row[field_name]) != normalize_text(row[field_name]):
            return True
    return False


def _load_source(
    data_dir: Path,
    spec: SourceSpec,
    audit_mode: CoordinateAuditMode,
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

    frame = _validate_and_prepare_columns(
        read_result.frame,
        spec.required_columns,
        spec.optional_columns,
        report,
    )
    report.encoding = read_result.encoding
    report.total_rows = len(frame) + read_result.bad_line_count
    report.parsing_warnings.extend(read_result.warnings)
    if report.schema_validation_failed:
        report.load_error = "source schema validation failed"
        return records, report

    _validate_source_frame(frame, spec, report)

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
    _validate_normalized_records(records, spec, report)
    if (
        audit_mode == "strict"
        and report.expected_row_count_failed
        and spec.file_name != "us_military_sites.csv"
    ):
        report.load_error = "source validation strict mode failed"
        report.plotted_rows = 0
        return [], report
    if spec.file_name == "us_military_sites.csv" and audit_mode != "off":
        records = _apply_coordinate_audit(records, report, audit_mode)
    if audit_mode == "strict" and report.expected_row_count_failed:
        report.load_error = report.load_error or "source validation strict mode failed"
        report.plotted_rows = 0
        return [], report
    return records, report


def _validate_normalized_records(
    records: list[LocationRecord],
    spec: SourceSpec,
    report: SourceQualityReport,
) -> None:
    if spec.expected_exact_rows is not None and len(records) != spec.expected_exact_rows:
        report.expected_row_count_failed = True
        report.validation_warnings.append(
            f"Expected {spec.expected_exact_rows:,} plotted records but normalized "
            f"{len(records):,}"
        )

    ids = [record.id for record in records]
    duplicate_ids = sorted(id_value for id_value, count in Counter(ids).items() if count > 1)
    if duplicate_ids:
        report.schema_validation_failed = True
        report.validation_errors.append(f"Duplicate normalized IDs: {', '.join(duplicate_ids[:5])}")


def _apply_coordinate_audit(
    records: list[LocationRecord],
    report: SourceQualityReport,
    audit_mode: CoordinateAuditMode,
) -> list[LocationRecord]:
    audit_results = audit_us_military_records(records)
    report.records_audited = len(audit_results)
    report.audit_passed = sum(1 for result in audit_results if result.audit_status == "pass")
    report.audit_warnings = sum(1 for result in audit_results if result.audit_status == "warning")
    report.audit_high_confidence_mismatches = sum(
        1 for result in audit_results if result.audit_status == "high_confidence_mismatch"
    )
    report.audit_unverified = sum(
        1 for result in audit_results if result.audit_status == "unverified"
    )
    report.audit_probable_coordinate_swaps = sum(
        1 for result in audit_results if result.audit_reason == "probable_lat_lon_swap"
    )
    report.audit_probable_longitude_sign_errors = sum(
        1 for result in audit_results if result.audit_reason == "probable_longitude_sign_error"
    )
    report.audit_probable_latitude_sign_errors = sum(
        1 for result in audit_results if result.audit_reason == "probable_latitude_sign_error"
    )

    result_by_source_record_id = {result.record_id: result for result in audit_results}
    audited_records = []
    for record in records:
        result = result_by_source_record_id.get(str(record.raw.get("Record_ID", "")))
        if result is None:
            audited_records.append(record)
            continue
        audited_records.append(
            record.model_copy(
                update={
                    "coordinate_audit_status": result.audit_status,
                    "coordinate_audit_severity": result.audit_severity,
                    "coordinate_audit_reason": result.audit_reason,
                    "coordinate_audit_detected_geography": result.detected_geography,
                    "coordinate_audit_possible_correction_type": result.possible_correction_type,
                    "coordinate_audit_distance_km": result.distance_from_expected_region_km,
                }
            )
        )

    if report.audit_high_confidence_mismatches:
        report.validation_warnings.append(
            f"Coordinate audit found {report.audit_high_confidence_mismatches:,} "
            "high-confidence geographic mismatches"
        )
    if audit_mode == "strict" and report.audit_high_confidence_mismatches:
        report.load_error = "coordinate audit strict mode failed"
        report.plotted_rows = 0
        return []
    return audited_records


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


def load_location_dataset(
    data_dir: Path,
    *,
    audit_mode: CoordinateAuditMode = "warn",
) -> LocationDataset:
    """Load all configured source CSVs."""

    records: list[LocationRecord] = []
    source_reports: list[SourceQualityReport] = []
    for spec in SOURCE_SPECS:
        source_records, source_report = _load_source(data_dir, spec, audit_mode)
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
