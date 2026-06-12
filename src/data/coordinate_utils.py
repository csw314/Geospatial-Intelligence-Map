"""Coordinate parsing and validation helpers."""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from typing import Any

from src.utils.text_cleaning import normalize_text

COORDINATE_TOKEN_RE = re.compile(
    r"(?P<prefix>[NSEW])?\s*(?P<number>[+-]?\d+(?:\.\d+)?)\s*(?:°|º|deg)?\s*(?P<suffix>[NSEW])?",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class ParsedCoordinate:
    """A parsed decimal coordinate token."""

    value: float
    direction: str | None = None


def _parse_compact_dms(number_text: str, direction: str) -> float | None:
    digits = number_text.strip().lstrip("+")
    if "." in digits or not digits.isdigit():
        return None

    degree_digits = 2 if direction in {"N", "S"} else 3
    if len(digits) <= degree_digits:
        return None

    degrees = int(digits[:degree_digits])
    remainder = digits[degree_digits:]
    if len(remainder) <= 2:
        minutes = int(remainder)
        seconds = 0
        if minutes > 59 and remainder.endswith("0"):
            minutes = int(remainder[:-1])
    elif len(remainder) == 3:
        minutes = int(remainder[:2])
        seconds = int(remainder[2:])
    else:
        minutes = int(remainder[:2])
        seconds = int(remainder[2:4])

    if minutes > 59 or seconds > 59:
        return None
    decimal = degrees + minutes / 60 + seconds / 3600
    return _apply_direction(decimal, direction)


def parse_float(value: Any) -> float | None:
    """Parse a decimal float from a cell value."""

    text = normalize_text(value)
    if not text:
        return None
    text = text.replace(",", "")
    try:
        parsed = float(text)
    except ValueError:
        return None
    if not math.isfinite(parsed):
        return None
    return parsed


def is_valid_latitude(value: float | None) -> bool:
    """Return True when value is a valid latitude."""

    return value is not None and -90 <= value <= 90


def is_valid_longitude(value: float | None) -> bool:
    """Return True when value is a valid longitude."""

    return value is not None and -180 <= value <= 180


def parse_latitude_longitude(latitude: Any, longitude: Any) -> tuple[float, float] | None:
    """Parse and validate a latitude/longitude field pair."""

    parsed_latitude = parse_float(latitude)
    parsed_longitude = parse_float(longitude)
    if parsed_latitude is None or parsed_longitude is None:
        return None
    if is_valid_latitude(parsed_latitude) and is_valid_longitude(parsed_longitude):
        return parsed_latitude, parsed_longitude
    return None


def _apply_direction(value: float, direction: str | None) -> float:
    if direction is None:
        return value
    if direction.upper() in {"S", "W"}:
        return -abs(value)
    return abs(value)


def _extract_coordinate_tokens(value: Any) -> list[ParsedCoordinate]:
    text = normalize_text(value)
    tokens: list[ParsedCoordinate] = []
    for match in COORDINATE_TOKEN_RE.finditer(text):
        prefix = match.group("prefix")
        suffix = match.group("suffix")
        direction = (prefix or suffix).upper() if prefix or suffix else None
        number_text = match.group("number")
        number = (
            _parse_compact_dms(number_text, direction)
            if direction is not None
            else parse_float(number_text)
        )
        if number is None:
            number = parse_float(number_text)
            if number is not None:
                number = _apply_direction(number, direction)
        if number is None:
            continue
        tokens.append(ParsedCoordinate(number, direction))
    return tokens


def parse_coordinate_pair(value: Any) -> tuple[float, float] | None:
    """Parse a decimal coordinate pair from a free-form coordinate string."""

    tokens = _extract_coordinate_tokens(value)
    if len(tokens) < 2:
        return None

    latitude: float | None = None
    longitude: float | None = None
    undirected: list[float] = []

    for token in tokens:
        if token.direction in {"N", "S"} and latitude is None:
            latitude = token.value
        elif token.direction in {"E", "W"} and longitude is None:
            longitude = token.value
        elif token.direction is None:
            undirected.append(token.value)

    if latitude is None and undirected:
        latitude = undirected.pop(0)
    if longitude is None and undirected:
        longitude = undirected.pop(0)

    if latitude is None or longitude is None:
        return None
    if is_valid_latitude(latitude) and is_valid_longitude(longitude):
        return latitude, longitude
    return None
