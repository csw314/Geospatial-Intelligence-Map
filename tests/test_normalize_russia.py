from __future__ import annotations

import pytest

from src.data.normalize_russia import normalize_russia_row


def test_normalize_russia_row() -> None:
    normalized = normalize_russia_row(
        {
            "Oblast": " Moscow\u00a0Oblast ",
            "Name": " Alpha Air Base ",
            "Latitude": "55.0",
            "Longitude": "37.0",
            "Country": "Russia",
            "Type": " Air Base ",
        },
        2,
    )

    record = normalized.record
    assert record.id == "russia_data.csv:2:alpha-air-base"
    assert record.country == "Russia"
    assert record.region == "Moscow Oblast"
    assert record.type == "Air Base"
    assert record.latitude == 55.0
    assert record.longitude == 37.0


def test_normalize_russia_rejects_invalid_coordinates() -> None:
    with pytest.raises(ValueError):
        normalize_russia_row(
            {
                "Oblast": "",
                "Name": "Broken",
                "Latitude": "91",
                "Longitude": "37.0",
                "Country": "Russia",
                "Type": "Air Base",
            },
            2,
        )
