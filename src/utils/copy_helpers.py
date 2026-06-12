"""Formatting helpers for coordinate display and copy actions."""

from __future__ import annotations


def format_decimal(value: float) -> str:
    """Format a coordinate without excessive trailing zeros."""

    return f"{value:.6f}".rstrip("0").rstrip(".")


def format_lat_lon(latitude: float, longitude: float) -> str:
    """Format a latitude/longitude pair for copy-ready display."""

    return f"{format_decimal(latitude)}, {format_decimal(longitude)}"
