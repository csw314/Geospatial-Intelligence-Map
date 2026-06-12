# Testing

Run:

```powershell
python -m pytest
python -m ruff check .
python -m black --check .
python -m mypy src
```

Browser smoke tests use Playwright. Install Chromium once before running the full suite:

```powershell
python -m playwright install chromium
```

Tests cover coordinate parsing, text normalization, source normalization, data quality reporting, filters, search ranking, app import, layout construction, GeoJSON marker generation, selection state, details-panel visibility, and browser-level map/search/filter smoke paths.
