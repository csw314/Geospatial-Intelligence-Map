# Testing

Run the default quality gates:

```powershell
python -m pytest
python -m ruff check .
python -m black --check .
python -m mypy src
```

Browser smoke tests use Playwright. Install Chromium once before running the browser suite:

```powershell
python -m playwright install chromium
python -m pytest -m browser
```

## Coverage Areas

Unit tests cover:

- Coordinate parsing and text normalization.
- Russia, China, Iran, DPRK, legacy metro, global-city, and U.S. military-site normalizers.
- cp1252-compatible loading, encoding fallback, expected source counts, and invalid-coordinate reporting.
- Global city parsing for population, GDP, Booleans, raw preservation, and stable IDs.
- U.S. site parsing for service/status values, numeric facility fields, coordinate quality, host country versus operator country, raw preservation, and stable IDs.
- Layer filtering for metro-only, adversary-only, U.S.-only, metro plus adversary, all military, all layers, and no layers.
- Filter interactions with country, type, source file, and text search.
- Selection retention and clearing as layer/filter visibility changes.
- Search-result and marker selection behavior, including cluster clicks ignored as selections.
- Source-aware details sections, numeric formatting, link rendering, missing-field omission, and U.S. site caveats.
- Marker/legend payloads, service codes, selected-state flags, and minimal GeoJSON properties.
- Layout state, top-bar controls, layer toolbar presence, and absence of duplicate floating map utility controls.

Browser smoke tests cover:

- Application load and visible Leaflet map.
- Layer toolbar visibility above the map.
- Absence of the removed floating custom utility group.
- Metro-only, U.S.-only, metro plus adversary, and all-military layer combinations.
- Search and details drawer behavior for a global city and a U.S. military site.
- Top-bar Reset View, Fit to Screen, Full Map, and Collapse Sidebar controls.
- Mobile viewport usability with the layer toolbar and details drawer.
