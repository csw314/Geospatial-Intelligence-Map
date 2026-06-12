from __future__ import annotations

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
