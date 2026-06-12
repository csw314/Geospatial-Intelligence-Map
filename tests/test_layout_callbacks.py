from __future__ import annotations

from typing import Any

from src.callbacks.layout_callbacks import (
    DEFAULT_LAYOUT_STATE,
    app_shell_class,
    details_panel_class,
    full_map_label,
    layout_state_for_trigger,
    reduce_layout_state,
    sidebar_label,
)
from src.components.layout import build_layout
from src.config import load_settings
from src.data.load_locations import load_location_dataset


def _collect_component_ids(component: Any) -> set[str]:
    found: set[str] = set()

    def walk(node: Any) -> None:
        if node is None:
            return
        node_id = getattr(node, "id", None)
        if isinstance(node_id, str):
            found.add(node_id)
        children = getattr(node, "children", None)
        if isinstance(children, list):
            for child in children:
                walk(child)
        else:
            walk(children)

    walk(component)
    return found


def test_sidebar_collapse_state_changes() -> None:
    state = reduce_layout_state(DEFAULT_LAYOUT_STATE, "toggle_sidebar")

    assert state["sidebar_collapsed"]
    assert "is-sidebar-collapsed" in app_shell_class(state)
    assert sidebar_label(state) == "Show Sidebar"


def test_full_map_state_changes() -> None:
    state = reduce_layout_state(DEFAULT_LAYOUT_STATE, "toggle_full_map")

    assert state["full_map"]
    assert "is-full-map" in app_shell_class(state)
    assert full_map_label(state) == "Exit Full Map"


def test_fit_to_screen_only_increments_resize_nonce() -> None:
    state = reduce_layout_state(DEFAULT_LAYOUT_STATE, "fit_to_screen")

    assert state["resize_nonce"] == DEFAULT_LAYOUT_STATE["resize_nonce"] + 1
    assert state["sidebar_collapsed"] == DEFAULT_LAYOUT_STATE["sidebar_collapsed"]
    assert state["full_map"] == DEFAULT_LAYOUT_STATE["full_map"]
    assert state["details_open"] == DEFAULT_LAYOUT_STATE["details_open"]


def test_details_panel_open_close_state() -> None:
    opened = reduce_layout_state(DEFAULT_LAYOUT_STATE, "open_details")
    closed = reduce_layout_state(opened, "close_details")

    assert opened["details_open"]
    assert details_panel_class(opened) == "details-panel"
    assert not closed["details_open"]
    assert "is-collapsed" in details_panel_class(closed)


def test_selected_location_state_controls_details_panel_visibility() -> None:
    opened = layout_state_for_trigger("selected-location-id", "abc", DEFAULT_LAYOUT_STATE)
    closed = layout_state_for_trigger("selected-location-id", None, opened)

    assert opened["details_open"]
    assert not closed["details_open"]
    assert "is-collapsed" in details_panel_class(closed)


def test_layout_contains_responsive_map_controls() -> None:
    settings = load_settings()
    dataset = load_location_dataset(settings.data_dir)
    layout = build_layout(dataset, settings)
    ids = _collect_component_ids(layout)

    assert "layout-state" in ids
    assert "map" in ids
    assert "sidebar-toggle" in ids
    assert "full-map-toggle" in ids
    assert "fit-screen" in ids
    assert "map-sidebar-toggle" in ids
    assert "map-full-map-toggle" in ids
    assert "map-fit-screen" in ids
    assert "map-reset-view" in ids
    assert "close-details" in ids
