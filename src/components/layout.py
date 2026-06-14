"""Root Dash layout."""

from __future__ import annotations

from typing import Any

from dash import dcc, html

from src.components.details_panel import render_details_panel
from src.components.layer_toolbar import build_layer_toolbar
from src.components.legend import build_legend
from src.components.map_view import build_map
from src.components.sidebar import build_sidebar
from src.components.top_bar import build_top_bar
from src.config import AppSettings
from src.data.load_locations import LocationDataset
from src.utils.marker_styles import legend_payload


def build_warning_banner(quality: dict[str, Any]) -> Any:
    """Build a prominent application-level warning banner when needed."""

    warnings = quality.get("critical_warnings", [])
    if not warnings:
        return None
    return html.Div(
        id="quality-warning-banner",
        className="quality-warning-banner",
        children=[
            html.Div("Data requires review", className="quality-warning-title"),
            html.Ul([html.Li(warning) for warning in warnings], className="quality-warning-list"),
        ],
    )


def build_layout(dataset: LocationDataset, settings: AppSettings) -> Any:
    """Build the full application layout."""

    quality = dataset.quality_as_dict()
    return html.Div(
        id="app-shell",
        className="app-shell",
        children=[
            dcc.Store(id="selected-location-id", data=None),
            dcc.Store(
                id="layout-state",
                data={
                    "sidebar_collapsed": False,
                    "full_map": False,
                    "details_open": False,
                    "resize_nonce": 0,
                },
            ),
            html.Div(id="map-resize-sentinel", className="visually-hidden"),
            build_top_bar(dataset.quality_report.plotted_rows),
            build_warning_banner(quality),
            html.Div(
                id="workspace",
                className="workspace",
                children=[
                    build_sidebar(dataset.records, quality),
                    html.Main(
                        className="map-stage",
                        children=[
                            build_layer_toolbar(),
                            build_map(dataset.records, settings),
                            build_legend(legend_payload(dataset.records)),
                        ],
                    ),
                    html.Section(
                        id="details-panel",
                        className="details-panel is-collapsed",
                        children=render_details_panel(None),
                    ),
                ],
            ),
        ],
    )
