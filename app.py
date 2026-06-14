"""Dash application entry point."""

from __future__ import annotations

import dash_bootstrap_components as dbc
from dash import Dash

from src.callbacks import register_callbacks
from src.components.layout import build_layout
from src.config import load_settings
from src.data.load_locations import load_location_dataset


def create_app() -> Dash:
    """Create and configure the Dash application."""

    settings = load_settings()
    dataset = load_location_dataset(settings.data_dir, audit_mode=settings.coordinate_audit_mode)
    dash_app = Dash(
        __name__,
        external_stylesheets=[dbc.themes.BOOTSTRAP],
        title="Global Location Map",
    )
    dash_app.layout = build_layout(dataset, settings)
    register_callbacks(dash_app, dataset.records)
    return dash_app


app = create_app()
server = app.server


if __name__ == "__main__":
    app.run(debug=load_settings().debug)
