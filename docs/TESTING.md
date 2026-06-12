# Testing

Run:

```powershell
python -m pytest
python -m ruff check .
python -m black --check .
python -m mypy src
```

Tests cover coordinate parsing, text normalization, source normalization, data quality reporting, filters, search ranking, app import, layout construction, and GeoJSON marker generation.

