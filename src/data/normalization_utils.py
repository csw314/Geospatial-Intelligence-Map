"""Shared normalization helpers for source-specific CSV parsers."""

from __future__ import annotations

import re
from typing import Any

from src.utils.text_cleaning import normalize_text

NUMBER_CLEAN_RE = re.compile(r"[\s,$]")
TRUE_VALUES = {"1", "true", "yes", "y", "included"}
FALSE_VALUES = {"0", "false", "no", "n", "not included", "excluded"}


def parse_int(value: Any) -> int | None:
    """Parse an optional integer with common separators and currency symbols."""

    parsed = parse_number(value)
    if parsed is None:
        return None
    return int(parsed)


def parse_number(value: Any) -> float | None:
    """Parse an optional decimal number with commas, spaces, and currency symbols."""

    text = normalize_text(value)
    if not text:
        return None
    compact = NUMBER_CLEAN_RE.sub("", text)
    if compact.startswith("(") and compact.endswith(")"):
        compact = f"-{compact[1:-1]}"
    try:
        return float(compact)
    except ValueError:
        return None


def parse_bool(value: Any) -> bool | None:
    """Parse common source Boolean text into True/False when possible."""

    text = normalize_text(value).casefold()
    if not text:
        return None
    if text in TRUE_VALUES:
        return True
    if text in FALSE_VALUES:
        return False
    return None


def numeric_warning(
    field_name: str, raw_value: Any, parsed_value: int | float | None
) -> str | None:
    """Return a parse warning for non-empty numeric text that could not be parsed."""

    if normalize_text(raw_value) and parsed_value is None:
        return f"Could not parse numeric field {field_name}: {normalize_text(raw_value)}"
    return None
