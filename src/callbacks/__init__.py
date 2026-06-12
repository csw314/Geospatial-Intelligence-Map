"""Dash callback registration."""

from __future__ import annotations

from typing import Any

from src.callbacks.filter_callbacks import register_filter_callbacks
from src.callbacks.layout_callbacks import register_layout_callbacks
from src.callbacks.map_callbacks import register_map_callbacks
from src.callbacks.selection_callbacks import register_selection_callbacks
from src.data.schemas import LocationRecord


def register_callbacks(app: Any, records: list[LocationRecord]) -> None:
    """Register all Dash callbacks."""

    register_filter_callbacks(app, records)
    register_selection_callbacks(app, records)
    register_map_callbacks(app, records)
    register_layout_callbacks(app)
