from __future__ import annotations

from typing import Any

from dash import html

from src.components.details_panel import render_details_panel
from src.data.schemas import LocationRecord


def _record_by_name(records: list[LocationRecord], name: str) -> LocationRecord:
    return next(record for record in records if record.name == name)


def _collect_text(node: Any) -> str:
    if node is None:
        return ""
    if isinstance(node, str):
        return node
    if isinstance(node, (int, float)):
        return str(node)
    children = getattr(node, "children", None)
    if isinstance(children, list):
        return " ".join(_collect_text(child) for child in children)
    return _collect_text(children)


def _collect_links(node: Any) -> list[Any]:
    links: list[Any] = []
    if isinstance(node, html.A):
        links.append(node)
    children = getattr(node, "children", None)
    if isinstance(children, list):
        for child in children:
            links.extend(_collect_links(child))
    elif children is not None:
        links.extend(_collect_links(children))
    return links


def test_global_city_details_use_grouped_sections_and_formatting(
    sample_records: list[LocationRecord],
) -> None:
    panel = render_details_panel(_record_by_name(sample_records, "Chongqing"))
    text = _collect_text(panel)

    assert "Identity and Geography" in text
    assert "Population" in text
    assert "Capital and Economy" in text
    assert "Sources and Research Links" in text
    assert "32,054,159" in text
    assert "$12,500" in text
    assert "Yes" in text
    links = _collect_links(panel)
    assert links
    assert all(link.target == "_blank" for link in links)
    assert all(link.rel == "noopener noreferrer" for link in links)


def test_us_site_details_use_grouped_sections_and_caveat(
    sample_records: list[LocationRecord],
) -> None:
    panel = render_details_panel(_record_by_name(sample_records, "Ramstein Air Base"))
    text = _collect_text(panel)

    assert "Site Identity" in text
    assert "Coordinates and Quality" in text
    assert "Facilities" in text
    assert "Sources and Notes" in text
    assert "United States" in text
    assert "Germany" in text
    assert "Representative point" in text
    assert "$2,500M" in text
    assert "unit of observation is a site" in text


def test_us_site_details_display_coordinate_audit_warning(
    sample_records: list[LocationRecord],
) -> None:
    record = _record_by_name(sample_records, "Ramstein Air Base").model_copy(
        update={
            "coordinate_audit_status": "high_confidence_mismatch",
            "coordinate_audit_severity": "high",
            "coordinate_audit_reason": "country_or_territory_mismatch",
            "coordinate_audit_detected_geography": "Spain",
            "coordinate_audit_possible_correction_type": "manual_review",
            "coordinate_audit_distance_km": 1000.0,
        }
    )

    text = _collect_text(render_details_panel(record))

    assert "Coordinate audit warning" in text
    assert "Coordinate-audit status" in text
    assert "country_or_territory_mismatch" in text
    assert "Spain" in text
