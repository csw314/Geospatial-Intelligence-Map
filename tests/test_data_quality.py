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
        tmp_path / "global_cities_metros_100k.csv",
        (
            "Record_ID,Location_Name,Location_Type,Country,ISO2,ISO3,Region,Admin1_Name,"
            "Latitude,Longitude,Timezone,Population,Population_Source,Population_Bamwor,"
            "Population_SimpleMaps,Population_Starting_List,Population_Size_Class,"
            "Capital_Classification,Country_GDP_Per_Capita_USD,Country_GDP_PPP_USD,"
            "OpenStreetMap_URL,Wikipedia_Search_URL,Image_Research_URL,Primary_Source,"
            "Starting_List_Included\n"
            "G1,Chongqing,Metro Area,China,CN,CHN,East Asia,Chongqing,29.55,106.5069,"
            'Asia/Shanghai,"32,054,159",Bamwor,"32,054,159",32000000,,10M+,admin,'
            "12500,35000000000000,https://example.test/osm,https://example.test/wiki,"
            "https://example.test/images,Bamwor,Yes\n"
            "G2,Broken City,City,China,CN,CHN,East Asia,Region,20,181,Asia/Shanghai,"
            "1000,Bamwor,1000,1000,,Under 1M,,12500,35000000000000,,,,Bamwor,No\n"
            "G3,Missing Population,City,China,CN,CHN,East Asia,Region,20,100,"
            "Asia/Shanghai,unknown,Bamwor,,,,Under 1M,minor,12500,35000000000000,"
            ",,,Bamwor,\n"
        ),
    )
    _write_cp1252(
        tmp_path / "us_military_sites.csv",
        (
            "Record_ID,Site,Component,Service_Branch,Component_Status,Host_Country,"
            "Admin_Area,Location_Class,Geographic_Scope,Nearest_City,Latitude,Longitude,"
            "Coordinate_Quality,Buildings_Owned,Buildings_Owned_SqFt,Buildings_Leased,"
            "Buildings_Leased_SqFt,Buildings_Other,Buildings_Other_SqFt,Acres_Owned,"
            "Total_Acres,Plant_Replacement_Value_M,Coordinate_Source_URL,Dataset_Source_URL,"
            "Notes\n"
            "U1,Alpha Site,Active,Army,Active,Germany,Bavaria,Site,Overseas,Nuremberg,"
            "49,11,Representative point,1,1000,0,0,0,0,10,10,100,"
            "https://example.test/coord,https://example.test/data,One site\n"
            "U2,Bravo Site,Active,Air Force,Active,Germany,Bavaria,Site,Overseas,Nuremberg,"
            "49,11,Representative point,2,2000,0,0,0,0,20,20,200,"
            "https://example.test/coord,https://example.test/data,Colocated site\n"
            "U3,Charlie Site,Reserve,Navy,Active,Japan,Okinawa,Site,Overseas,Naha,"
            "26.2,127.7,Approximate centroid,3,3000,1,500,0,0,30,31,300,"
            "https://example.test/coord,https://example.test/data,\n"
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

    assert report.total_rows == 12
    assert report.plotted_rows == 9
    assert report.counterforce_records == 4
    assert report.non_military_records == 2
    assert report.global_metro_records == 2
    assert report.adversary_military_records == 4
    assert report.us_military_records == 3
    assert len(report.duplicate_coordinates) == 2
    china_report = next(
        source for source in report.sources if source.source_file == "china_data.csv"
    )
    russia_report = next(
        source for source in report.sources if source.source_file == "russia_data.csv"
    )
    assert china_report.rows_with_cleaned_coordinates == 1
    assert russia_report.rows_with_text_cleanup == 1
    assert china_report.missing_optional_fields["Tenants"] == 1
    global_report = next(
        source for source in report.sources if source.source_file == "global_cities_metros_100k.csv"
    )
    assert global_report.total_rows == 3
    assert global_report.plotted_rows == 2
    assert global_report.rows_excluded_invalid_coordinates == 1
    assert global_report.rows_with_invalid_population == 1
    us_report = next(
        source for source in report.sources if source.source_file == "us_military_sites.csv"
    )
    assert us_report.total_rows == 3
    assert us_report.plotted_rows == 3
    assert us_report.duplicate_coordinate_count == 2
    iran_report = next(source for source in report.sources if source.source_file == "iran_data.csv")
    dprk_report = next(source for source in report.sources if source.source_file == "dprk_data.csv")
    assert iran_report.total_rows == 2
    assert iran_report.plotted_rows == 1
    assert iran_report.rows_excluded_invalid_coordinates == 1
    assert dprk_report.total_rows == 2
    assert dprk_report.plotted_rows == 1
    assert dprk_report.rows_excluded_invalid_coordinates == 1
