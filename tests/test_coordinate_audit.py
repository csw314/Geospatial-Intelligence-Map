from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.data.coordinate_audit import audit_us_military_records
from src.data.load_locations import load_location_dataset
from src.data.schemas import LocationRecord


def _us_record(
    *,
    record_id: str,
    name: str,
    host_country: str,
    admin_area: str,
    nearest_city: str,
    latitude: float,
    longitude: float,
) -> LocationRecord:
    return LocationRecord(
        id=f"us_military_sites.csv:{record_id}:{name.lower().replace(' ', '-')}",
        source_file="us_military_sites.csv",
        map_layer="us_military",
        country=host_country,
        operator_country="United States",
        location_category="Military Site",
        dataset_type="military",
        name=name,
        type="Army",
        latitude=latitude,
        longitude=longitude,
        admin_area=admin_area,
        service_branch="Army",
        nearest_city=nearest_city,
        raw={"Record_ID": record_id, "Site": name},
    )


def test_coordinate_audit_passes_host_country_and_territory_records() -> None:
    records = [
        _us_record(
            record_id="T1",
            name="Michigan Site",
            host_country="United States",
            admin_area="Michigan",
            nearest_city="Battle Creek",
            latitude=44.0,
            longitude=-85.0,
        ),
        _us_record(
            record_id="T2",
            name="Guam Site",
            host_country="United States",
            admin_area="Guam",
            nearest_city="Agana",
            latitude=13.47,
            longitude=144.76,
        ),
        _us_record(
            record_id="T3",
            name="Puerto Rico Site",
            host_country="United States",
            admin_area="Puerto Rico",
            nearest_city="San Juan",
            latitude=18.45,
            longitude=-66.2,
        ),
    ]

    results = audit_us_military_records(records)

    assert {result.record_id: result.audit_status for result in results} == {
        "T1": "pass",
        "T2": "pass",
        "T3": "pass",
    }


def test_coordinate_audit_detects_transform_candidates_and_mismatches() -> None:
    records = [
        _us_record(
            record_id="SWAP",
            name="Kuwait Swap",
            host_country="Kuwait",
            admin_area="Kuwait",
            nearest_city="Unknown",
            latitude=47.42,
            longitude=29.69,
        ),
        _us_record(
            record_id="SIGN",
            name="Michigan Sign",
            host_country="United States",
            admin_area="Michigan",
            nearest_city="Battle Creek",
            latitude=44.0,
            longitude=85.0,
        ),
        _us_record(
            record_id="MISS",
            name="South Carolina Mismatch",
            host_country="United States",
            admin_area="South Carolina",
            nearest_city="Beaufort",
            latitude=5.35,
            longitude=115.74,
        ),
    ]

    by_id = {result.record_id: result for result in audit_us_military_records(records)}

    assert by_id["SWAP"].audit_reason == "probable_lat_lon_swap"
    assert by_id["SWAP"].possible_correction_type == "latitude_longitude_swap"
    assert by_id["SIGN"].audit_reason == "probable_longitude_sign_error"
    assert by_id["SIGN"].possible_correction_type == "longitude_sign_flip"
    assert by_id["MISS"].audit_status == "high_confidence_mismatch"
    assert by_id["MISS"].audit_reason == "country_or_territory_mismatch"


def test_coordinate_audit_detects_group_outlier_and_unverified_geography() -> None:
    records = [
        _us_record(
            record_id="L1",
            name="Lajes A",
            host_country="Portugal",
            admin_area="Portugal",
            nearest_city="Lajes",
            latitude=38.7,
            longitude=-27.1,
        ),
        _us_record(
            record_id="L2",
            name="Lajes B",
            host_country="Portugal",
            admin_area="Portugal",
            nearest_city="Lajes",
            latitude=38.73,
            longitude=-27.05,
        ),
        _us_record(
            record_id="L3",
            name="Lajes C",
            host_country="Portugal",
            admin_area="Portugal",
            nearest_city="Lajes",
            latitude=38.76,
            longitude=-27.08,
        ),
        _us_record(
            record_id="L4",
            name="Lajes Outlier",
            host_country="Portugal",
            admin_area="Portugal",
            nearest_city="Lajes",
            latitude=39.0,
            longitude=8.0,
        ),
        _us_record(
            record_id="UNK",
            name="Unknown Geography",
            host_country="Atlantis",
            admin_area="Atlantis",
            nearest_city="Unknown",
            latitude=0.0,
            longitude=0.0,
        ),
    ]

    by_id = {result.record_id: result for result in audit_us_military_records(records)}

    assert by_id["L4"].audit_status == "warning"
    assert by_id["L4"].audit_reason == "group_outlier"
    assert by_id["UNK"].audit_status == "unverified"


def test_known_active_us_coordinate_audit_cases_are_flagged() -> None:
    dataset = load_location_dataset(Path("data/raw"))
    us_records = [
        record for record in dataset.records if record.source_file == "us_military_sites.csv"
    ]
    by_id = {result.record_id: result for result in audit_us_military_records(us_records)}

    assert by_id["837"].audit_status == "high_confidence_mismatch"
    assert by_id["837"].audit_reason == "country_or_territory_mismatch"
    assert by_id["888"].audit_reason == "probable_lat_lon_swap"
    assert by_id["982"].audit_reason == "probable_longitude_sign_error"
    assert by_id["1022"].audit_reason == "probable_longitude_sign_error"
    assert by_id["1298"].audit_reason == "group_outlier"
    assert by_id["1303"].audit_reason == "group_outlier"
    assert by_id["1363"].audit_status == "high_confidence_mismatch"
    assert by_id["757"].audit_reason == "named_place_mismatch_requires_review"


def test_coordinate_audit_does_not_modify_source_coordinates() -> None:
    path = Path("data/raw/us_military_sites.csv")
    before = pd.read_csv(path, dtype=str, keep_default_na=False, na_filter=False, encoding="cp1252")
    load_location_dataset(Path("data/raw"))
    after = pd.read_csv(path, dtype=str, keep_default_na=False, na_filter=False, encoding="cp1252")

    assert before[["Record_ID", "Latitude", "Longitude"]].equals(
        after[["Record_ID", "Latitude", "Longitude"]]
    )
