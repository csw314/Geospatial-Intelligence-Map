"""Text normalization helpers."""

from __future__ import annotations

import re
import unicodedata
from collections.abc import Mapping
from typing import Any

WHITESPACE_RE = re.compile(r"\s+")
SLUG_RE = re.compile(r"[^a-z0-9]+")


def normalize_text(value: Any) -> str:
    """Return a normalized string value safe for search and display."""

    if value is None:
        return ""
    text = str(value).replace("\u00a0", " ")
    text = unicodedata.normalize("NFKC", text)
    return WHITESPACE_RE.sub(" ", text).strip()


def blank_to_none(value: Any) -> str | None:
    """Normalize a value and convert blanks to None."""

    normalized = normalize_text(value)
    return normalized if normalized else None


def normalize_mapping(row: Mapping[str, Any]) -> dict[str, str]:
    """Normalize every value in a CSV row mapping."""

    return {str(key): normalize_text(value) for key, value in row.items()}


def row_needed_text_cleanup(row: Mapping[str, Any]) -> bool:
    """Return True when a row contains text that changes during normalization."""

    for value in row.values():
        original = "" if value is None else str(value)
        if original != normalize_text(value):
            return True
    return False


def slugify(value: str) -> str:
    """Create a compact deterministic slug for record IDs."""

    normalized = normalize_text(value).lower()
    slug = SLUG_RE.sub("-", normalized).strip("-")
    return slug or "unnamed"
