# Global Location Map

Production-style Dash application for visualizing provided military/location CSVs and metro-area/city CSVs in one interactive global map.

<img src="assets/Screenshot 2026-06-12 170319.png" alt="App Screenshot" width="500">

## Tech Stack

- Python 3.11+
- Dash, Dash Leaflet, dash-bootstrap-components
- pandas and Pydantic
- pytest, Ruff, Black, mypy

## Folder Structure

```text
app.py
assets/styles.css
data/raw/russia_data.csv
data/raw/china_data.csv
data/raw/iran_data.csv
data/raw/dprk_data.csv
data/raw/metro_areas.csv
src/data/
src/components/
src/callbacks/
src/utils/
tests/
docs/
```

## Data Sources

The app reads:

- `data/raw/russia_data.csv`
- `data/raw/china_data.csv`
- `data/raw/iran_data.csv`
- `data/raw/dprk_data.csv`
- `data/raw/metro_areas.csv`

Expected Russia columns: `Oblast`, `Name`, `Latitude`, `Longitude`, `Country`, `Type`.

Expected China columns: `Name`, `Alternate names`, `IATA`, `ICAO`, `Use`, `Subordinate`, `Coordinates`, `Latitude`, `Longitude`, `Runways`, `Tenants`, `Type`.

Expected Iran columns: `Country`, `Type`, `Name`, `Latitude`, `Longitude`, `Notes`.

Expected DPRK columns: `Category Source`, `Country`, `Name`, `Type`, `Latitude`, `Longitude`, `Notes`.

Expected metro columns: `Country`, `ISO2`, `Metro Area / City`, `Admin Region`, `Longitude`, `Latitude`, `Population`, `Population Proper`, `Capital Status`, `Source Country Name`, `Source URL`.

Russia, China, Iran, and DPRK records are loaded as `Counterforce` / `military`. Metro-area records are loaded as `Countervalue` / `metro_area` and use a distinct civilian marker style.

## Cleaning And Validation

CSV loading tries `utf-8`, `utf-8-sig`, `cp1252`, then `latin1`. Text fields are trimmed and non-breaking spaces are normalized. Latitude must be between `-90` and `90`; longitude must be between `-180` and `180`. China rows with invalid direct latitude or longitude attempt recovery from the `Coordinates` field. Iran and DPRK rows with invalid or missing coordinates are excluded and reported. Metro population strings such as `32,054,159` are parsed into integers; rows with missing or invalid population values remain plotted and are reported in data quality.

The UI shows total rows, plotted rows, counterforce/countervalue counts, coordinate fixes, excluded invalid-coordinate rows, invalid/missing population rows, duplicate coordinate counts, missing optional fields, and parsing warnings.

## Filters

The `Location Category` filter appears under `Country`:

- `All`: shows military/counterforce records and metro/countervalue records.
- `Counterforce`: shows only `russia_data.csv`, `china_data.csv`, `iran_data.csv`, and `dprk_data.csv`.
- `Countervalue`: shows only `metro_areas.csv`.

The `Country` options are generated from loaded data and include Russia, China, Iran, DPRK, and countries present in `metro_areas.csv`. The `Type` options update from the active Country, Location Category, and Source File filters. Search respects the active filters and can find Iran/DPRK rows by name, country, type, notes, and DPRK category source; metro rows can be found by city, country, ISO2, admin region, population text, capital status, and source country name.

## Layout Controls

The dashboard is designed as a full-height geospatial workspace. The top bar and map overlay both include controls for layout and viewport management:

- `Full Map`: toggles a focused map mode with a compact top bar and overlay panels.
- `Fit to Screen`: preserves filters, search text, selected markers, center, and zoom while forcing the map container to recalculate its size.
- `Collapse Sidebar`: hides the filter/search/data-quality sidebar to give the map more width; use `Show Sidebar` to restore it.
- `Reset View`: returns the map to the initial Eurasian/global view.

The details panel opens as a drawer when a location is selected. Closing the details panel clears the active selection, while `Clear Selection` does the same from inside the panel. On narrower screens, filters become a drawer and details become a bottom sheet.

Known browser-resize note: Leaflet sometimes needs an explicit resize after parent layout changes. The app sends a small clientside resize signal after Full Map, Fit to Screen, sidebar collapse, and details drawer changes so tiles and clustered markers repaint correctly.

## Local Setup

```powershell
python -m venv .venv
.\.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m playwright install chromium
python app.py
```

Open `http://127.0.0.1:8050/`.

## Basemap

The default basemap is CARTO Voyager raster tiles, which provide English/Latin-friendly labels for the primary map view and require no API key for local development. Override the tile URL, attribution, or layer name with `GLOBAL_LOCATION_TILE_URL`, `GLOBAL_LOCATION_TILE_ATTRIBUTION`, and `GLOBAL_LOCATION_TILE_LAYER_NAME`.

## Quality Gates

```powershell
python -m pytest
python -m ruff check .
python -m black --check .
python -m mypy src
```

Browser smoke tests use Playwright with Chromium. Install the browser once with:

```powershell
python -m playwright install chromium
```

## Adding A Country Or Metro CSV

Add a new normalizer in `src/data/`, define expected and optional columns, add a `SourceSpec` in `src/data/load_locations.py`, and map source-specific fields into `LocationRecord`. For future military/counterforce datasets, follow `src/data/normalize_iran.py` or `src/data/normalize_dprk.py`, set `location_category` to `Counterforce`, set `dataset_type` to `military`, and preserve source notes in `notes` when available. For future metro/city datasets, follow `src/data/normalize_metro_areas.py`, set `location_category` to `Countervalue`, set `dataset_type` to `metro_area`, and preserve original source values in `raw`.

## Adding Marker Types

Types are derived dynamically from loaded data. To adjust styling, update `TYPE_PALETTE` or `type_code()` in `src/utils/marker_styles.py`.

## Known Data Quality Issues

Some CSVs use cp1252-compatible bytes and contain non-breaking spaces or Windows-style punctuation. Optional metadata fields are missing in some rows, especially Russia `Oblast`, China `Tenants`, and Iran `Notes`. DPRK currently contains rows with missing coordinates; those rows are excluded and counted in the data-quality report. Metro rows with invalid coordinates are excluded; metro rows with missing or invalid population values remain visible and are counted in the data-quality report.

## Limitations And Non-Goals

This is a neutral geospatial visualization tool. It does not provide scoring, targeting, routing, prioritization, vulnerability assessment, military recommendations, or operational analysis.
