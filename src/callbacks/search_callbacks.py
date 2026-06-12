"""Search result rendering helpers."""

from __future__ import annotations

from typing import Any

import dash_bootstrap_components as dbc
from dash import html

from src.utils.display import display_country
from src.utils.search import SearchResult


def render_search_results(results: list[SearchResult], query: str | None) -> Any:
    """Render clickable search results."""

    if not query:
        return html.Div()
    if not results:
        return html.Div("No matches", className="empty-state search-empty")

    return dbc.ListGroup(
        [
            dbc.ListGroupItem(
                id={"type": "search-result", "id": result.record.id},
                action=True,
                className="search-result-item",
                children=[
                    html.Div(result.record.name, className="search-result-name"),
                    html.Div(
                        (
                            f"{display_country(result.record.country)} | "
                            f"{result.record.type} | {result.record.source_file}"
                        ),
                        className="search-result-meta",
                    ),
                ],
            )
            for result in results
        ],
        flush=True,
        className="search-result-list",
    )
