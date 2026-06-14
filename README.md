# Global Location Map

Dash and Dash Leaflet application for viewing three additive global map layers:

- Global Metro Areas / Countervalue
- Russia, China, Iran, and North Korea Military Sites
- U.S. Military Sites

The app is a neutral public-data visualization tool. It does not provide scoring, targeting, routing, prioritization, vulnerability assessment, military recommendations, or operational analysis.

## Tech Stack

- Python 3.11+
- Dash, Dash Leaflet, dash-bootstrap-components
- pandas and Pydantic
- pytest, Ruff, Black, mypy, Playwright

## Active Runtime Data

Runtime loading is CSV-only. The app reads these files once at startup from `data/raw/`:

- `russia_data.csv`
- `china_data.csv`
- `iran_data.csv`
- `dprk_data.csv`
- `global_cities_metros_100k.csv` - 7,027 rows, 7,027 valid coordinates, 180 countries
- `us_military_sites.csv` - 1,626 rows, 1,626 valid coordinates, 40 host countries/jurisdictions

The legacy `metro_areas.csv` file was archived to `data/archive/metro_areas_legacy.csv` and is not loaded. Supporting workbooks are retained under `docs/source-data/`; the application does not read XLSX files.

Expected global-city columns:

`Record_ID`, `Location_Name`, `Location_Type`, `Country`, `ISO2`, `ISO3`, `Region`, `Admin1_Name`, `Latitude`, `Longitude`, `Timezone`, `Population`, `Population_Source`, `Population_Bamwor`, `Population_SimpleMaps`, `Population_Starting_List`, `Population_Size_Class`, `Capital_Classification`, `Country_GDP_Per_Capita_USD`, `Country_GDP_PPP_USD`, `OpenStreetMap_URL`, `Wikipedia_Search_URL`, `Image_Research_URL`, `Primary_Source`, `Starting_List_Included`.

Expected U.S. military-site columns:

`Record_ID`, `Site`, `Component`, `Service_Branch`, `Component_Status`, `Host_Country`, `Admin_Area`, `Location_Class`, `Geographic_Scope`, `Nearest_City`, `Latitude`, `Longitude`, `Coordinate_Quality`, `Buildings_Owned`, `Buildings_Owned_SqFt`, `Buildings_Leased`, `Buildings_Leased_SqFt`, `Buildings_Other`, `Buildings_Other_SqFt`, `Acres_Owned`, `Total_Acres`, `Plant_Replacement_Value_M`, `Coordinate_Source_URL`, `Dataset_Source_URL`, `Notes`.

Expected U.S. service totals:

- Army: 623
- Air Force: 469
- Navy: 452
- Marine Corps: 80
- Washington Headquarters Services: 2

## Normalization Model

Every CSV row is normalized to a Pydantic `LocationRecord`. The key visibility field is `map_layer`:

- `global_metros`: global city and metro records, `Countervalue`, `metro_area`
- `adversary_military`: Russia, China, Iran, and DPRK records, `Counterforce`, `military`
- `us_military`: U.S.-operated site records, `Military Site`, `military`

For U.S. records, `country` is the host country so geographic filtering works. `operator_country` is `United States`. U.S. sites are not classified as Counterforce.

Global city population values are not a single harmonized metro statistic. The details drawer shows the selected `Population`, `Population_Source`, and individual Bamwor, SimpleMaps, and starting-list values where available.

U.S. records are site-level observations. Multiple sites can belong to one installation, and colocated records are retained. Coordinates are public representative points or approximate centroids, not boundaries, entrances, or tactical coordinates. `Coordinate_Quality` is displayed and searchable.

## Cleaning, Validation, And Coordinate Audit

CSV loading tries `utf-8`, `utf-8-sig`, `cp1252`, then `latin1`. Text is normalized, latitude must be between `-90` and `90`, and longitude must be between `-180` and `180`. China rows can recover coordinates from a combined `Coordinates` field. Invalid coordinate rows are excluded and reported.

Comma-formatted population, square-footage, acreage, GDP, and replacement-value fields are parsed into numeric values when possible. Non-empty numeric values that fail parsing are reported as warnings. Original source columns are preserved in `record.raw` for auditability.

Source validation distinguishes required columns, optional columns, required non-empty fields, row-count expectations, distinct-count expectations, duplicate normalized IDs, and source-specific value counts. Missing required columns fail that source explicitly. Optional missing columns may be filled with blanks and reported. Expected row-count or service-total mismatches are surfaced in the data-quality panel and warning banner.

U.S. site coordinates also run through an offline plausibility audit using static geographic envelopes in `data/reference/geographic_envelopes.json`. The audit checks host country, territories, U.S. states, selected named places, candidate latitude/longitude swaps, sign errors, group outliers, and suspicious rounded points. It does not call external geocoders and does not modify source coordinates.

Audit mode is configured with `COORDINATE_AUDIT_MODE`:

- `off`: skip plausibility auditing.
- `warn`: default; load and plot source coordinates while reporting anomalies.
- `strict`: prevent high-confidence suspect U.S. site coordinates from entering the dataset.

Run the audit manually with:

```powershell
python scripts/audit_us_military_coordinates.py --input data/raw/us_military_sites.csv --output artifacts/us_military_coordinate_audit.csv
```

Generated audit artifacts are gitignored under `artifacts/`.

The data-quality panel reports total rows, plotted rows, excluded rows, per-layer counts, per-source loaded/plotted counts, invalid coordinate exclusions, numeric parsing warnings, missing optional fields, duplicate-coordinate groups, source encoding, validation warnings, coordinate-audit totals, and load errors. Critical load, validation, expected-count, and coordinate-audit problems appear in a prominent banner.

## Filters And Search

The layer toolbar sits above the map and uses independent switches. Any combination is valid: metro-only, adversary-only, U.S.-only, metros plus adversary, all military without metros, all three layers, or no layers.

The sidebar includes:

- Searchable Country dropdown with `All` and canonical `DPRK / North Korea` display.
- Searchable multi-select Type dropdown. Options update from active layers, country, and source files.
- Source File checklist as an advanced filter.
- Debounced text search.

Search covers normalized fields and source-specific raw metadata. Global-city search includes names, type, country, ISO codes, region, admin area, timezone, population fields, population source, size class, capital classification, and primary source. U.S. search includes site, component, service branch, status, host country, admin area, location class, geographic scope, nearest city, coordinate quality, and notes.

Search text is indexed once at startup as server-side normalized search documents. Callbacks do not reread CSV files or place search documents in GeoJSON. Type selections preserve the user's previous intersection when layer, country, or source context changes; Select All and Clear All remain explicit commands.

The visible-count text reports total visible records plus visible global metros, adversary military sites, and U.S. military sites. Reset View only resets the viewport; it does not clear filters, layers, search text, details state, or selection.

## Markers, Legend, And Details

The map uses one clustered GeoJSON layer populated from the union of active logical layers. GeoJSON properties are intentionally small: id, name, country, layer, type/service, marker style fields, and selected state.

Marker families:

- Global metros: green civilian marker with `MET`.
- Adversary military: existing country-colored military markers for Russia, China, Iran, and DPRK.
- U.S. military: distinct diamond marker with service codes such as `ARM`, `AF`, `NAV`, `MC`, and `WHS`.

The legend explains map layers, adversary country colors, U.S. service styling, and type codes. Selecting a marker or search result opens a source-aware details drawer and highlights the marker without automatically zooming. Use `Zoom to Location` to deliberately center and zoom to the selected record. URLs render as descriptive links that open in a new tab. Missing values are omitted.

Top-bar controls:

- `Collapse Sidebar` / `Show Sidebar`
- `Fit to Screen`
- `Full Map` / `Exit Full Map`
- `Reset View`

The duplicate floating map utility group has been removed. Standard Leaflet zoom, scale, fullscreen, and basemap controls remain.

## Local Setup

```powershell
python -m venv .venv
.\.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements-lock.txt
python -m playwright install chromium
python app.py
```

Open `http://127.0.0.1:8050/`.

The default basemap is CARTO Voyager. Override it with `GLOBAL_LOCATION_TILE_URL`, `GLOBAL_LOCATION_TILE_ATTRIBUTION`, and `GLOBAL_LOCATION_TILE_LAYER_NAME`. Copy `.env.example` to `.env` to customize basemap or coordinate-audit mode.

## Quality Gates

```powershell
python -m pytest
python -m pytest -m browser
python -m ruff check .
python -m black --check .
python -m mypy src
```

Browser smoke tests use Playwright with Chromium:

```powershell
python -m playwright install chromium
python -m pytest -m browser
```

Dependencies are maintained in `requirements.in` and pinned in `requirements-lock.txt`. Update the lock with the project's chosen resolver, then rerun all quality gates before committing. CI installs from `requirements-lock.txt`.

## Adding A Source

Add a normalizer in `src/data/`, define expected and optional columns, add a `SourceSpec` in `src/data/load_locations.py`, and map source-specific fields into `LocationRecord`. Set `map_layer` explicitly. Preserve source provenance and raw values. Do not add runtime Excel dependencies.

## Limitations

The city layer is point-based and does not include metro polygons or harmonized urban-area boundaries. Country GDP fields are national indicators, not city metrics. U.S. site records are public BSR site records and are not a complete inventory of classified, temporary, contingency, or access locations.

Coordinate auditing is designed to detect gross inconsistencies, not prove exact installation locations. It uses generalized envelopes, so coastlines, borders, small islands, and territory metadata can produce false positives or false negatives. The application never silently changes, swaps, negates, relocates, deletes, or excludes source coordinates in warn mode.
