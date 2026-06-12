from __future__ import annotations

from pathlib import Path

from src.data.load_locations import load_location_dataset


def _write_cp1252(path: Path, text: str) -> None:
    path.write_bytes(text.encode("cp1252"))


def test_data_quality_report_generation(tmp_path: Path) -> None:
    _write_cp1252(
        tmp_path / "russia_data.csv",
        (
            "Oblast,Name,Latitude,Longitude,Country,Type\n"
            ",Alpha\u00a0Base,30.5,117.25,Russia,Air Base\n"
        ),
    )
    _write_cp1252(
        tmp_path / "china_data.csv",
        (
            "Name,Alternate names,IATA,ICAO,Use,Subordinate,Coordinates,Latitude,"
            "Longitude,Runways,Tenants,Type\n"
            "Recovered Base,,,,,,30.5N 117.25E,bad,bad,,,Air Base\n"
        ),
    )
    _write_cp1252(
        tmp_path / "metro_areas.csv",
        (
            "Country,ISO2,Metro Area / City,Admin Region,Longitude,Latitude,Population,"
            "Population Proper,Capital Status,Source Country Name,Source URL\n"
            'China,CN,Chongqing,Chongqing,106.5069,29.55,"32,054,159",'
            '"32,054,159",admin,China,https://example.test/cn.csv\n'
            "China,CN,Broken City,Region,181,20,1000,1000,,China,\n"
            "China,CN,Missing Population,Region,100,20,unknown,,minor,China,\n"
        ),
    )
    _write_cp1252(
        tmp_path / "iran_data.csv",
        (
            "Country,Type,Name,Latitude,Longitude,Notes\n"
            "Iran,Air Base,Mehrabad International Airport,35.6886,51.3128,F-14s\n"
            "Iran,Air Base,Broken Latitude,91,51.3128,\n"
        ),
    )
    _write_cp1252(
        tmp_path / "dprk_data.csv",
        (
            "Category Source,Country,Name,Type,Latitude,Longitude,Notes\n"
            "Rocket launch site,DPRK,Sakkanmol Missile Operating Base,"
            "Missile operating base,38.584698,126.107945,cp1252 smart quote ’\n"
            "Airfield,DPRK,Missing Coordinates,Military airfield,,,\n"
        ),
    )

    dataset = load_location_dataset(tmp_path)
    report = dataset.quality_report

    assert report.total_rows == 9
    assert report.plotted_rows == 6
    assert report.counterforce_records == 4
    assert report.countervalue_records == 2
    assert len(report.duplicate_coordinates) == 1
    china_report = next(
        source for source in report.sources if source.source_file == "china_data.csv"
    )
    russia_report = next(
        source for source in report.sources if source.source_file == "russia_data.csv"
    )
    assert china_report.rows_with_cleaned_coordinates == 1
    assert russia_report.rows_with_text_cleanup == 1
    assert china_report.missing_optional_fields["Tenants"] == 1
    metro_report = next(
        source for source in report.sources if source.source_file == "metro_areas.csv"
    )
    assert metro_report.total_rows == 3
    assert metro_report.plotted_rows == 2
    assert metro_report.rows_excluded_invalid_coordinates == 1
    assert metro_report.rows_with_invalid_population == 1
    iran_report = next(source for source in report.sources if source.source_file == "iran_data.csv")
    dprk_report = next(source for source in report.sources if source.source_file == "dprk_data.csv")
    assert iran_report.total_rows == 2
    assert iran_report.plotted_rows == 1
    assert iran_report.rows_excluded_invalid_coordinates == 1
    assert dprk_report.total_rows == 2
    assert dprk_report.plotted_rows == 1
    assert dprk_report.rows_excluded_invalid_coordinates == 1
