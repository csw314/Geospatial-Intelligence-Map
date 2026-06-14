from __future__ import annotations

from collections import Counter

from dash import Dash

from app import create_app
from src.components.layout import build_layout
from src.config import load_settings
from src.data.load_locations import load_location_dataset


def test_app_imports_and_layout_builds() -> None:
    dash_app = create_app()
    assert isinstance(dash_app, Dash)
    assert dash_app.layout is not None


def test_layout_builds_from_real_dataset() -> None:
    settings = load_settings()
    dataset = load_location_dataset(settings.data_dir)
    layout = build_layout(dataset, settings)

    assert layout is not None
    assert dataset.quality_report.plotted_rows > 0
    counts = Counter(record.map_layer for record in dataset.records)
    assert counts["global_metros"] == 7027
    assert counts["us_military"] == 1626
    assert counts["adversary_military"] > 0
