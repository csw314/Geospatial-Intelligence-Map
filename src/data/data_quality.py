"""Data quality reporting structures."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class SourceQualityReport:
    """Quality metrics for one source CSV."""

    source_file: str
    dataset_type: str = "military"
    encoding: str | None = None
    total_rows: int = 0
    plotted_rows: int = 0
    rows_with_text_cleanup: int = 0
    rows_with_cleaned_coordinates: int = 0
    rows_excluded_invalid_coordinates: int = 0
    rows_with_invalid_population: int = 0
    duplicate_coordinate_count: int = 0
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
            items.extend(source.parsing_warnings)
            if source.load_error:
                items.append(f"{source.source_file}: {source.load_error}")
        return items

    @property
    def counterforce_records(self) -> int:
        """Total plotted Counterforce records."""

        return sum(
            source.plotted_rows for source in self.sources if source.dataset_type == "military"
        )

    @property
    def countervalue_records(self) -> int:
        """Total plotted Countervalue records."""

        return sum(
            source.plotted_rows for source in self.sources if source.dataset_type == "metro_area"
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialize the aggregate report."""

        return {
            "total_rows": self.total_rows,
            "plotted_rows": self.plotted_rows,
            "excluded_rows": self.excluded_rows,
            "counterforce_records": self.counterforce_records,
            "countervalue_records": self.countervalue_records,
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
    warnings: tuple[str, ...] = ()
