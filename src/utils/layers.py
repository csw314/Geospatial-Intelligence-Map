"""Logical map-layer constants and labels."""

from __future__ import annotations

from collections.abc import Sequence

from src.data.schemas import MapLayer

GLOBAL_METROS: MapLayer = "global_metros"
ADVERSARY_MILITARY: MapLayer = "adversary_military"
US_MILITARY: MapLayer = "us_military"
ALL_MAP_LAYERS: tuple[MapLayer, ...] = (GLOBAL_METROS, ADVERSARY_MILITARY, US_MILITARY)
MAP_LAYER_LABELS: dict[MapLayer, str] = {
    GLOBAL_METROS: "Global Metro Areas / Non-Military",
    ADVERSARY_MILITARY: "Russia, China, Iran, and North Korea Military Sites",
    US_MILITARY: "U.S. Military Sites",
}
MAP_LAYER_SHORT_LABELS: dict[MapLayer, str] = {
    GLOBAL_METROS: "Global metros",
    ADVERSARY_MILITARY: "Adversary military",
    US_MILITARY: "U.S. military",
}


def normalize_active_layers(active_layers: Sequence[str] | None) -> set[MapLayer]:
    """Return valid active layer values; None means all layers are active."""

    if active_layers is None:
        return set(ALL_MAP_LAYERS)
    valid_values = set(ALL_MAP_LAYERS)
    return {layer for layer in active_layers if layer in valid_values}
