"""Data quality reporting structures."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class SourceQualityReport:
    """Quality metrics for one source CSV."""

    source_file: str
    dataset_type: str = "military"
    map_layer: str = "adversary_military"
    location_category: str = "Counterforce"
    encoding: str | None = None
    total_rows: int = 0
    plotted_rows: int = 0
    rows_with_text_cleanup: int = 0
    rows_with_cleaned_coordinates: int = 0
    rows_excluded_invalid_coordinates: int = 0
    rows_with_invalid_population: int = 0
    rows_with_numeric_parse_warnings: int = 0
    duplicate_coordinate_count: int = 0
    records_audited: int = 0
    audit_passed: int = 0
    audit_warnings: int = 0
    audit_high_confidence_mismatches: int = 0
    audit_probable_coordinate_swaps: int = 0
    audit_probable_longitude_sign_errors: int = 0
    audit_probable_latitude_sign_errors: int = 0
    audit_unverified: int = 0
    validation_errors: list[str] = field(default_factory=list)
    validation_warnings: list[str] = field(default_factory=list)
    expected_row_count_failed: bool = False
    schema_validation_failed: bool = False
    missing_optional_fields: dict[str, int] = field(default_factory=dict)
    parsing_warnings: list[str] = field(default_factory=list)
    load_error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Serialize the source report."""

        return asdict(self)


@dataclass
class DuplicateCoordinate:
    """One duplicate coordinate pair and the records at that location."""

    latitude: float
    longitude: float
    record_ids: list[str]
    names: list[str]

    def to_dict(self) -> dict[str, Any]:
        """Serialize the duplicate coordinate record."""

        return asdict(self)


@dataclass
class DataQualityReport:
    """Aggregate quality report for all loaded sources."""

    sources: list[SourceQualityReport] = field(default_factory=list)
    duplicate_coordinates: list[DuplicateCoordinate] = field(default_factory=list)

    @property
    def total_rows(self) -> int:
        """Total CSV rows seen across all sources."""

        return sum(source.total_rows for source in self.sources)

    @property
    def plotted_rows(self) -> int:
        """Total normalized records available for plotting."""

        return sum(source.plotted_rows for source in self.sources)

    @property
    def excluded_rows(self) -> int:
        """Total rows excluded because coordinates were invalid."""

        return sum(source.rows_excluded_invalid_coordinates for source in self.sources)

    @property
    def warnings(self) -> list[str]:
        """Flattened parsing warnings."""

        items: list[str] = []
        for source in self.sources:
            items.extend(
                f"{source.source_file}: {warning}" for warning in source.validation_warnings
            )
            items.extend(f"{source.source_file}: {error}" for error in source.validation_errors)
            items.extend(source.parsing_warnings)
            if source.load_error:
                items.append(f"{source.source_file}: {source.load_error}")
        return items

    @property
    def critical_warnings(self) -> list[str]:
        """Warnings that should be displayed prominently in the application shell."""

        items: list[str] = []
        for source in self.sources:
            if source.load_error:
                items.append(f"{source.source_file} failed to load: {source.load_error}")
            if source.schema_validation_failed:
                items.append(
                    f"{source.source_file} failed required schema validation; "
                    "the map may be incomplete."
                )
            if source.expected_row_count_failed:
                items.append(
                    f"{source.source_file} did not match expected source counts; "
                    "the dataset requires review."
                )
            if source.audit_high_confidence_mismatches:
                items.append(
                    f"{source.source_file} has "
                    f"{source.audit_high_confidence_mismatches:,} high-confidence "
                    "coordinate audit mismatches. The map displays source-provided "
                    "coordinates that require review."
                )
        return items

    @property
    def counterforce_records(self) -> int:
        """Total plotted Counterforce records."""

        return sum(
            source.plotted_rows
            for source in self.sources
            if source.location_category == "Counterforce"
        )

    @property
    def countervalue_records(self) -> int:
        """Total plotted Countervalue records."""

        return sum(
            source.plotted_rows
            for source in self.sources
            if source.location_category == "Countervalue"
        )

    @property
    def global_metro_records(self) -> int:
        """Total plotted records in the global metro layer."""

        return sum(
            source.plotted_rows for source in self.sources if source.map_layer == "global_metros"
        )

    @property
    def adversary_military_records(self) -> int:
        """Total plotted records in the adversary military layer."""

        return sum(
            source.plotted_rows
            for source in self.sources
            if source.map_layer == "adversary_military"
        )

    @property
    def us_military_records(self) -> int:
        """Total plotted records in the U.S. military layer."""

        return sum(
            source.plotted_rows for source in self.sources if source.map_layer == "us_military"
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialize the aggregate report."""

        return {
            "total_rows": self.total_rows,
            "plotted_rows": self.plotted_rows,
            "excluded_rows": self.excluded_rows,
            "counterforce_records": self.counterforce_records,
            "countervalue_records": self.countervalue_records,
            "global_metro_records": self.global_metro_records,
            "adversary_military_records": self.adversary_military_records,
            "us_military_records": self.us_military_records,
            "critical_warnings": self.critical_warnings,
            "sources": [source.to_dict() for source in self.sources],
            "duplicate_coordinates": [
                duplicate.to_dict() for duplicate in self.duplicate_coordinates
            ],
            "warnings": self.warnings,
        }


@dataclass(frozen=True)
class NormalizedLocation:
    """A normalized row plus row-level quality metadata."""

    record: Any
    coordinate_cleaned: bool = False
    invalid_population_count: int = 0
    invalid_numeric_count: int = 0
    warnings: tuple[str, ...] = ()
