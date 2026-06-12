"""Root Dash layout."""

from __future__ import annotations

from typing import Any

from dash import dcc, html

from src.components.details_panel import render_details_panel
from src.components.legend import build_legend
from src.components.map_view import build_map
from src.components.sidebar import build_sidebar
from src.components.top_bar import build_top_bar
from src.config import AppSettings
from src.data.load_locations import LocationDataset
from src.utils.marker_styles import legend_payload


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
            html.Div(
                id="workspace",
                className="workspace",
                children=[
                    build_sidebar(dataset.records, quality),
                    html.Main(
                        className="map-stage",
                        children=[
                            build_map(dataset.records, settings),
                            html.Div(
                                className="map-control-group",
                                children=[
                                    html.Button(
                                        "Reset View",
                                        id="map-reset-view",
                                        className="map-control-button",
                                        type="button",
                                    ),
                                    html.Button(
                                        "Fit to Screen",
                                        id="map-fit-screen",
                                        className="map-control-button",
                                        type="button",
                                    ),
                                    html.Button(
                                        "Full Map",
                                        id="map-full-map-toggle",
                                        className="map-control-button",
                                        type="button",
                                    ),
                                    html.Button(
                                        "Collapse Sidebar",
                                        id="map-sidebar-toggle",
                                        className="map-control-button",
                                        type="button",
                                    ),
                                ],
                            ),
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
