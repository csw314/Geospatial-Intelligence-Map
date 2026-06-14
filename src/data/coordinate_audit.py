"""Offline coordinate plausibility checks for source-provided points."""

from __future__ import annotations

import json
import math
from collections import defaultdict
from collections.abc import Iterable, Sequence
from dataclasses import asdict, dataclass
from pathlib import Path
from statistics import median
from typing import Any, Literal

from src.config import PROJECT_ROOT
from src.data.schemas import LocationRecord
from src.utils.text_cleaning import normalize_text

AuditStatus = Literal["pass", "warning", "high_confidence_mismatch", "unverified"]
AuditSeverity = Literal["none", "low", "medium", "high"]

DEFAULT_REFERENCE_PATH = PROJECT_ROOT / "data" / "reference" / "geographic_envelopes.json"
BORDER_TOLERANCE_KM = 75.0
GROUP_OUTLIER_KM = 500.0


@dataclass(frozen=True)
class BoundingBox:
    """A simple latitude/longitude geographic envelope."""

    min_latitude: float
    min_longitude: float
    max_latitude: float
    max_longitude: float

    @classmethod
    def from_values(cls, values: Sequence[float]) -> BoundingBox:
        """Create a bounding box from [min_lat, min_lon, max_lat, max_lon]."""

        return cls(
            min_latitude=float(values[0]),
            min_longitude=float(values[1]),
            max_latitude=float(values[2]),
            max_longitude=float(values[3]),
        )

    def contains(self, latitude: float, longitude: float) -> bool:
        """Return True when the point falls inside the envelope."""

        return (
            self.min_latitude <= latitude <= self.max_latitude
            and self.min_longitude <= longitude <= self.max_longitude
        )

    def distance_km(self, latitude: float, longitude: float) -> float:
        """Approximate distance from the point to the envelope in kilometers."""

        if self.contains(latitude, longitude):
            return 0.0
        clamped_lat = min(max(latitude, self.min_latitude), self.max_latitude)
        clamped_lon = min(max(longitude, self.min_longitude), self.max_longitude)
        return haversine_km(latitude, longitude, clamped_lat, clamped_lon)


@dataclass(frozen=True)
class CoordinateAuditResult:
    """Row-level coordinate plausibility audit output."""

    record_id: str
    site: str
    host_country: str
    admin_area: str | None
    latitude: float
    longitude: float
    audit_status: AuditStatus
    audit_severity: AuditSeverity
    audit_reason: str
    detected_geography: str | None = None
    possible_correction_type: str | None = None
    distance_from_expected_region_km: float | None = None

    def to_dict(self) -> dict[str, Any]:
        """Serialize the audit result."""

        return asdict(self)


@dataclass(frozen=True)
class GeographyReference:
    """Offline geography envelopes for expected and detected regions."""

    countries: dict[str, list[BoundingBox]]
    admin_areas: dict[str, list[BoundingBox]]
    places: dict[str, list[BoundingBox]]


def _load_bbox_map(raw: MappingLike) -> dict[str, list[BoundingBox]]:
    return {
        str(key): [BoundingBox.from_values(values) for values in boxes]
        for key, boxes in raw.items()
    }


MappingLike = dict[str, Any]


def load_geography_reference(path: Path = DEFAULT_REFERENCE_PATH) -> GeographyReference:
    """Load local static envelope reference data."""

    raw = json.loads(path.read_text(encoding="utf-8"))
    return GeographyReference(
        countries=_load_bbox_map(raw.get("countries", {})),
        admin_areas=_load_bbox_map(raw.get("admin_areas", {})),
        places=_load_bbox_map(raw.get("places", {})),
    )


def haversine_km(
    latitude_a: float,
    longitude_a: float,
    latitude_b: float,
    longitude_b: float,
) -> float:
    """Return approximate great-circle distance in kilometers."""

    radius_km = 6371.0
    lat_a = math.radians(latitude_a)
    lat_b = math.radians(latitude_b)
    delta_lat = math.radians(latitude_b - latitude_a)
    delta_lon = math.radians(longitude_b - longitude_a)
    hav = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(lat_a) * math.cos(lat_b) * math.sin(delta_lon / 2) ** 2
    )
    return 2 * radius_km * math.asin(math.sqrt(hav))


def _key(*parts: str | None) -> str:
    return "|".join(normalize_text(part) for part in parts)


def _expected_boxes(
    record: LocationRecord,
    reference: GeographyReference,
) -> tuple[str | None, list[BoundingBox]]:
    place_key = _key(record.country, record.admin_area, record.nearest_city)
    if record.nearest_city and place_key in reference.places:
        return place_key, reference.places[place_key]

    admin_key = _key(record.country, record.admin_area)
    if record.admin_area and admin_key in reference.admin_areas:
        return admin_key, reference.admin_areas[admin_key]

    country = normalize_text(record.country)
    return country, reference.countries.get(country, [])


def _any_contains(boxes: Sequence[BoundingBox], latitude: float, longitude: float) -> bool:
    return any(box.contains(latitude, longitude) for box in boxes)


def _min_distance(
    boxes: Sequence[BoundingBox],
    latitude: float,
    longitude: float,
) -> float | None:
    if not boxes:
        return None
    return min(box.distance_km(latitude, longitude) for box in boxes)


def _detect_geography(
    latitude: float,
    longitude: float,
    reference: GeographyReference,
) -> str | None:
    for name, boxes in {**reference.admin_areas, **reference.countries}.items():
        if _any_contains(boxes, latitude, longitude):
            return name
    return None


def _transformed_candidate(
    record: LocationRecord,
    boxes: Sequence[BoundingBox],
) -> tuple[str, str] | None:
    latitude = record.latitude
    longitude = record.longitude
    candidates = (
        ("probable_lat_lon_swap", "latitude_longitude_swap", longitude, latitude),
        ("probable_longitude_sign_error", "longitude_sign_flip", latitude, -longitude),
        ("probable_latitude_sign_error", "latitude_sign_flip", -latitude, longitude),
    )
    for reason, correction, candidate_latitude, candidate_longitude in candidates:
        if (
            -90 <= candidate_latitude <= 90
            and -180 <= candidate_longitude <= 180
            and _any_contains(boxes, candidate_latitude, candidate_longitude)
        ):
            return reason, correction
    return None


def _rounded_placeholder_candidate(record: LocationRecord) -> bool:
    return float(record.latitude).is_integer() and float(record.longitude).is_integer()


def audit_record(
    record: LocationRecord,
    reference: GeographyReference,
    *,
    group_outlier_distance_km: float | None = None,
) -> CoordinateAuditResult:
    """Audit one U.S. military site record without modifying its coordinates."""

    expected_name, boxes = _expected_boxes(record, reference)
    detected = _detect_geography(record.latitude, record.longitude, reference)
    distance = _min_distance(boxes, record.latitude, record.longitude)

    if not boxes:
        return CoordinateAuditResult(
            record_id=record.raw.get("Record_ID", record.id),
            site=record.name,
            host_country=record.country,
            admin_area=record.admin_area,
            latitude=record.latitude,
            longitude=record.longitude,
            audit_status="unverified",
            audit_severity="low",
            audit_reason="unverified_geography",
            detected_geography=detected,
        )

    if _any_contains(boxes, record.latitude, record.longitude):
        return CoordinateAuditResult(
            record_id=record.raw.get("Record_ID", record.id),
            site=record.name,
            host_country=record.country,
            admin_area=record.admin_area,
            latitude=record.latitude,
            longitude=record.longitude,
            audit_status="pass",
            audit_severity="none",
            audit_reason="within_expected_geography",
            detected_geography=expected_name,
            distance_from_expected_region_km=0.0,
        )

    transformed = _transformed_candidate(record, boxes)
    if transformed:
        reason, correction = transformed
        return CoordinateAuditResult(
            record_id=record.raw.get("Record_ID", record.id),
            site=record.name,
            host_country=record.country,
            admin_area=record.admin_area,
            latitude=record.latitude,
            longitude=record.longitude,
            audit_status="high_confidence_mismatch",
            audit_severity="high",
            audit_reason=reason,
            detected_geography=detected,
            possible_correction_type=correction,
            distance_from_expected_region_km=round(distance or 0.0, 1),
        )

    if group_outlier_distance_km is not None and group_outlier_distance_km >= GROUP_OUTLIER_KM:
        return CoordinateAuditResult(
            record_id=record.raw.get("Record_ID", record.id),
            site=record.name,
            host_country=record.country,
            admin_area=record.admin_area,
            latitude=record.latitude,
            longitude=record.longitude,
            audit_status="warning",
            audit_severity="high",
            audit_reason="group_outlier",
            detected_geography=detected,
            possible_correction_type="cluster_outlier_review",
            distance_from_expected_region_km=round(group_outlier_distance_km, 1),
        )

    if normalize_text(record.nearest_city).casefold() == "iwo-jima":
        return CoordinateAuditResult(
            record_id=record.raw.get("Record_ID", record.id),
            site=record.name,
            host_country=record.country,
            admin_area=record.admin_area,
            latitude=record.latitude,
            longitude=record.longitude,
            audit_status="warning",
            audit_severity="high",
            audit_reason="named_place_mismatch_requires_review",
            detected_geography=detected,
            possible_correction_type="manual_review",
            distance_from_expected_region_km=round(distance or 0.0, 1),
        )

    if distance is not None and distance <= BORDER_TOLERANCE_KM:
        return CoordinateAuditResult(
            record_id=record.raw.get("Record_ID", record.id),
            site=record.name,
            host_country=record.country,
            admin_area=record.admin_area,
            latitude=record.latitude,
            longitude=record.longitude,
            audit_status="warning",
            audit_severity="low",
            audit_reason="near_expected_border_or_generalized_boundary",
            detected_geography=detected,
            distance_from_expected_region_km=round(distance, 1),
        )

    reason = (
        "suspicious_rounded_placeholder"
        if _rounded_placeholder_candidate(record)
        else "country_or_territory_mismatch"
    )
    return CoordinateAuditResult(
        record_id=record.raw.get("Record_ID", record.id),
        site=record.name,
        host_country=record.country,
        admin_area=record.admin_area,
        latitude=record.latitude,
        longitude=record.longitude,
        audit_status="high_confidence_mismatch",
        audit_severity="high",
        audit_reason=reason,
        detected_geography=detected,
        distance_from_expected_region_km=round(distance or 0.0, 1),
    )


def _group_outlier_distances(records: Sequence[LocationRecord]) -> dict[str, float]:
    groups: dict[tuple[str, str, str], list[LocationRecord]] = defaultdict(list)
    for record in records:
        if not record.nearest_city or normalize_text(record.nearest_city).casefold() == "unknown":
            continue
        groups[(record.country, record.admin_area or "", record.nearest_city)].append(record)

    distances: dict[str, float] = {}
    for group_records in groups.values():
        if len(group_records) < 4:
            continue
        median_latitude = median(record.latitude for record in group_records)
        median_longitude = median(record.longitude for record in group_records)
        for record in group_records:
            distance = haversine_km(
                record.latitude,
                record.longitude,
                median_latitude,
                median_longitude,
            )
            if distance >= GROUP_OUTLIER_KM:
                distances[record.id] = distance
    return distances


def audit_us_military_records(
    records: Iterable[LocationRecord],
    *,
    reference_path: Path = DEFAULT_REFERENCE_PATH,
) -> list[CoordinateAuditResult]:
    """Audit U.S. military site records against offline geographic references."""

    us_records = [record for record in records if record.source_file == "us_military_sites.csv"]
    reference = load_geography_reference(reference_path)
    group_distances = _group_outlier_distances(us_records)
    return [
        audit_record(
            record,
            reference,
            group_outlier_distance_km=group_distances.get(record.id),
        )
        for record in us_records
    ]


def summarize_audit_results(results: Sequence[CoordinateAuditResult]) -> dict[str, Any]:
    """Build a compact summary grouped by status, severity, and reason."""

    by_status: dict[str, int] = defaultdict(int)
    by_severity: dict[str, int] = defaultdict(int)
    by_reason: dict[str, int] = defaultdict(int)
    for result in results:
        by_status[result.audit_status] += 1
        by_severity[result.audit_severity] += 1
        by_reason[result.audit_reason] += 1
    return {
        "total": len(results),
        "by_status": dict(sorted(by_status.items())),
        "by_severity": dict(sorted(by_severity.items())),
        "by_reason": dict(sorted(by_reason.items())),
    }
