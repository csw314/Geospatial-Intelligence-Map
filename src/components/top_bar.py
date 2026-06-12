"""Top application bar."""

from __future__ import annotations

from typing import Any

import dash_bootstrap_components as dbc
from dash import html


def build_top_bar(total_plotted: int) -> Any:
    """Build the top app bar."""

    return html.Header(
        className="app-top-bar",
        children=[
            html.Div(
                className="brand-block",
                children=[
                    html.H1("Global Location Map", className="app-title"),
                    html.Div(
                        f"{total_plotted:,} plotted locations",
                        id="status-line",
                        className="status-line",
                    ),
                ],
            ),
            html.Div(
                className="top-bar-actions",
                children=[
                    dbc.Button(
                        "Collapse Sidebar",
                        id="sidebar-toggle",
                        color="light",
                        outline=True,
                        size="sm",
                    ),
                    dbc.Button(
                        "Fit to Screen",
                        id="fit-screen",
                        color="light",
                        outline=True,
                        size="sm",
                    ),
                    dbc.Button(
                        "Full Map",
                        id="full-map-toggle",
                        color="light",
                        outline=True,
                        size="sm",
                    ),
                    dbc.Button(
                        "Reset View",
                        id="reset-view",
                        color="primary",
                        size="sm",
                        className="reset-button",
                    ),
                ],
            ),
        ],
    )
