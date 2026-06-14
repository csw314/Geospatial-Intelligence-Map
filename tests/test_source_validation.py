from __future__ import annotations

from pathlib import Path

from src.data.load_locations import load_location_dataset


def _write(path: Path, text: str) -> None:
    path.write_text(text, encoding="cp1252")


def test_missing_required_column_fails_source_validation(tmp_path: Path) -> None:
    _write(
        tmp_path / "us_military_sites.csv",
        (
            "Record_ID,Site,Component,Service_Branch,Component_Status,Host_Country,"
            "Admin_Area,Location_Class,Geographic_Scope,Nearest_City,Latitude,"
            "Coordinate_Quality,Buildings_Owned\n"
            "1,Site,Active,Army,Active,United States,Texas,Site,CONUS,Austin,30,Quality,1\n"
        ),
    )

    report = load_location_dataset(tmp_path).quality_report
    us_report = next(
        source for source in report.sources if source.source_file == "us_military_sites.csv"
    )

    assert us_report.schema_validation_failed
    assert "Missing required columns" in us_report.validation_errors[0]
    assert us_report.plotted_rows == 0
    assert report.critical_warnings


def test_optional_missing_column_is_permitted_and_reported(tmp_path: Path) -> None:
    _write(
        tmp_path / "us_military_sites.csv",
        ("Record_ID,Site,Latitude,Longitude,Host_Country\n" "1,Site,30,-97,United States\n"),
    )

    report = load_location_dataset(tmp_path).quality_report
    us_report = next(
        source for source in report.sources if source.source_file == "us_military_sites.csv"
    )

    assert not us_report.schema_validation_failed
    assert us_report.plotted_rows == 1
    assert us_report.validation_warnings


def test_strict_audit_mode_prevents_suspect_us_records_from_plotting(tmp_path: Path) -> None:
    _write(
        tmp_path / "us_military_sites.csv",
        (
            "Record_ID,Site,Latitude,Longitude,Host_Country,Admin_Area,Nearest_City,"
            "Service_Branch\n"
            "1,Bad Point,5,115,United States,South Carolina,Beaufort,Navy\n"
        ),
    )

    report = load_location_dataset(tmp_path, audit_mode="strict").quality_report
    us_report = next(
        source for source in report.sources if source.source_file == "us_military_sites.csv"
    )

    assert us_report.load_error == "coordinate audit strict mode failed"
    assert us_report.audit_high_confidence_mismatches == 1
    assert us_report.plotted_rows == 0


def test_strict_mode_prevents_row_count_mismatch_when_audit_passes(tmp_path: Path) -> None:
    _write(
        tmp_path / "us_military_sites.csv",
        (
            "Record_ID,Site,Latitude,Longitude,Host_Country,Admin_Area,Nearest_City,"
            "Service_Branch\n"
            "1,Good Point,30,-97,United States,Texas,Austin,Army\n"
        ),
    )

    report = load_location_dataset(tmp_path, audit_mode="strict").quality_report
    us_report = next(
        source for source in report.sources if source.source_file == "us_military_sites.csv"
    )

    assert us_report.load_error == "source validation strict mode failed"
    assert us_report.audit_high_confidence_mismatches == 0
    assert us_report.plotted_rows == 0
