"""Above-map logical layer controls."""

from __future__ import annotations

from typing import Any

import dash_bootstrap_components as dbc
from dash import html

from src.utils.layers import ALL_MAP_LAYERS, MAP_LAYER_LABELS


def build_layer_toolbar() -> Any:
    """Build persistent additive map-layer switches."""

    return html.Div(
        id="layer-toolbar",
        className="layer-toolbar",
        children=[
            html.Div("Map Layers", className="layer-toolbar-title"),
            dbc.Checklist(
                id="active-layers",
                options=[
                    {"label": MAP_LAYER_LABELS[layer], "value": layer} for layer in ALL_MAP_LAYERS
                ],
                value=list(ALL_MAP_LAYERS),
                switch=True,
                inline=True,
                className="layer-switches",
                inputClassName="layer-switch-input",
                labelClassName="layer-switch-label",
            ),
        ],
    )
