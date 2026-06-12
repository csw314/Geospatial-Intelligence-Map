from __future__ import annotations

from src.utils.text_cleaning import blank_to_none, normalize_text, row_needed_text_cleanup, slugify


def test_text_normalization_replaces_non_breaking_spaces() -> None:
    assert normalize_text("  2,800\u00a0m  ") == "2,800 m"
    assert blank_to_none(" \u00a0 ") is None
    assert row_needed_text_cleanup({"Runways": "2,800\u00a0m"})
    assert slugify("Alpha Air Base") == "alpha-air-base"
