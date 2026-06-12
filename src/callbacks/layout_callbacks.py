"""Callbacks and helpers for responsive layout controls."""

from __future__ import annotations

from typing import Any, Literal, SupportsInt, TypedDict, cast

from dash import Input, Output, State, ctx, no_update


class LayoutState(TypedDict):
    """Persistent UI layout state."""

    sidebar_collapsed: bool
    full_map: bool
    details_open: bool
    resize_nonce: int


DEFAULT_LAYOUT_STATE: LayoutState = {
    "sidebar_collapsed": False,
    "full_map": False,
    "details_open": False,
    "resize_nonce": 0,
}

LayoutAction = Literal[
    "toggle_sidebar",
    "toggle_full_map",
    "fit_to_screen",
    "close_details",
    "open_details",
]


def normalize_layout_state(state: dict[str, Any] | None) -> LayoutState:
    """Return a complete layout state with defaults filled in."""

    merged = dict(DEFAULT_LAYOUT_STATE)
    if state:
        merged.update(state)
    resize_nonce = cast(SupportsInt, merged["resize_nonce"])
    return LayoutState(
        sidebar_collapsed=bool(merged["sidebar_collapsed"]),
        full_map=bool(merged["full_map"]),
        details_open=bool(merged["details_open"]),
        resize_nonce=int(resize_nonce),
    )


def reduce_layout_state(
    state: dict[str, Any] | None,
    action: LayoutAction,
) -> LayoutState:
    """Apply one layout action without touching data/filter state."""

    next_state = normalize_layout_state(state)
    if action == "toggle_sidebar":
        next_state["sidebar_collapsed"] = not next_state["sidebar_collapsed"]
    elif action == "toggle_full_map":
        next_state["full_map"] = not next_state["full_map"]
    elif action == "close_details":
        next_state["details_open"] = False
    elif action == "open_details":
        next_state["details_open"] = True
    next_state["resize_nonce"] += 1
    return next_state


def app_shell_class(state: dict[str, Any] | None) -> str:
    """Build the root app shell class name."""

    normalized = normalize_layout_state(state)
    classes = ["app-shell"]
    if normalized["full_map"]:
        classes.append("is-full-map")
    if normalized["sidebar_collapsed"]:
        classes.append("is-sidebar-collapsed")
    if not normalized["details_open"]:
        classes.append("is-details-collapsed")
    return " ".join(classes)


def full_map_label(state: dict[str, Any] | None) -> str:
    """Return the correct full-map toggle label."""

    return "Exit Full Map" if normalize_layout_state(state)["full_map"] else "Full Map"


def sidebar_label(state: dict[str, Any] | None) -> str:
    """Return the correct sidebar toggle label."""

    return (
        "Show Sidebar" if normalize_layout_state(state)["sidebar_collapsed"] else "Collapse Sidebar"
    )


def details_panel_class(state: dict[str, Any] | None) -> str:
    """Build the details panel class name."""

    normalized = normalize_layout_state(state)
    classes = ["details-panel"]
    if not normalized["details_open"]:
        classes.append("is-collapsed")
    return " ".join(classes)


def layout_state_for_trigger(
    triggered_id: Any,
    selected_id: str | None,
    state: dict[str, Any] | None,
) -> LayoutState | Any:
    """Resolve the next layout state for a Dash trigger."""

    if triggered_id in {"sidebar-toggle", "map-sidebar-toggle"}:
        return reduce_layout_state(state, "toggle_sidebar")
    if triggered_id in {"full-map-toggle", "map-full-map-toggle"}:
        return reduce_layout_state(state, "toggle_full_map")
    if triggered_id in {"fit-screen", "map-fit-screen"}:
        return reduce_layout_state(state, "fit_to_screen")
    if triggered_id == "close-details":
        return reduce_layout_state(state, "close_details")
    if triggered_id == "selected-location-id":
        return reduce_layout_state(state, "open_details" if selected_id else "close_details")
    return no_update


def register_layout_callbacks(app: Any) -> None:
    """Register layout state and Leaflet resize callbacks."""

    @app.callback(
        Output("layout-state", "data"),
        Input("sidebar-toggle", "n_clicks"),
        Input("map-sidebar-toggle", "n_clicks"),
        Input("full-map-toggle", "n_clicks"),
        Input("map-full-map-toggle", "n_clicks"),
        Input("fit-screen", "n_clicks"),
        Input("map-fit-screen", "n_clicks"),
        Input("selected-location-id", "data"),
        State("layout-state", "data"),
        prevent_initial_call=True,
    )
    def update_layout_state(
        _sidebar_clicks: int | None,
        _map_sidebar_clicks: int | None,
        _full_map_clicks: int | None,
        _map_full_map_clicks: int | None,
        _fit_clicks: int | None,
        _map_fit_clicks: int | None,
        selected_id: str | None,
        state: dict[str, Any] | None,
    ) -> LayoutState | Any:
        return layout_state_for_trigger(ctx.triggered_id, selected_id, state)

    @app.callback(
        Output("app-shell", "className"),
        Output("details-panel", "className"),
        Output("full-map-toggle", "children"),
        Output("map-full-map-toggle", "children"),
        Output("sidebar-toggle", "children"),
        Output("map-sidebar-toggle", "children"),
        Input("layout-state", "data"),
    )
    def update_layout_classes(
        state: dict[str, Any] | None,
    ) -> tuple[str, str, str, str, str, str]:
        shell_class = app_shell_class(state)
        panel_class = details_panel_class(state)
        full_label = full_map_label(state)
        side_label = sidebar_label(state)
        return shell_class, panel_class, full_label, full_label, side_label, side_label

    app.clientside_callback(
        """
        function(layoutState) {
            const resizeMap = () => {
                const mapElement = document.getElementById("map");
                if (!mapElement) {
                    return window.dash_clientside.no_update;
                }
                window.dispatchEvent(new Event("resize"));
                if (mapElement._leaflet_map) {
                    mapElement._leaflet_map.invalidateSize({pan: false});
                    return layoutState ? layoutState.resize_nonce : 0;
                }
                const candidates = Object.values(window).filter((value) => {
                    return value && value.invalidateSize && value.getContainer;
                });
                const map = candidates.find((candidate) => candidate.getContainer() === mapElement);
                if (map) {
                    map.invalidateSize({pan: false});
                }
                return layoutState ? layoutState.resize_nonce : 0;
            };
            window.setTimeout(resizeMap, 40);
            window.setTimeout(resizeMap, 180);
            window.setTimeout(resizeMap, 420);
            return layoutState ? layoutState.resize_nonce : 0;
        }
        """,
        Output("map-resize-sentinel", "children"),
        Input("layout-state", "data"),
    )
