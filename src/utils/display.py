"""Display-label helpers."""

from __future__ import annotations

DPRK_COUNTRY_VALUE = "DPRK"
DPRK_COUNTRY_ALIASES = frozenset({"DPRK", "North Korea", "DPRK / North Korea"})
_DPRK_COUNTRY_ALIAS_KEYS = frozenset(alias.casefold() for alias in DPRK_COUNTRY_ALIASES)


def canonical_country(country: str | None) -> str:
    """Return the shared country value used by UI filters."""

    normalized = (country or "").strip()
    if normalized.casefold() in _DPRK_COUNTRY_ALIAS_KEYS:
        return DPRK_COUNTRY_VALUE
    return normalized


def display_country(country: str) -> str:
    """Return a clear UI label for a normalized country value."""

    if canonical_country(country) == DPRK_COUNTRY_VALUE:
        return "DPRK / North Korea"
    return country
