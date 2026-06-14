# Architecture

The app keeps CSV parsing and validation outside Dash callbacks. Runtime data is loaded once during `create_app()` by `load_location_dataset()`.

## Modules

- `src/data`: CSV loading, source-specific normalizers, Pydantic schemas, coordinate parsing, and quality reports.
- `src/utils`: pure filtering, search, display helpers, layer constants, and GeoJSON marker generation.
- `src/components`: Dash layout factories for the top bar, sidebar, layer toolbar, map, legend, and details drawer.
- `src/callbacks`: Dash callbacks for filtering, search result rendering, selection, details, map viewport, and layout state.

## Data Flow

`src/data/load_locations.py` registers one `SourceSpec` per active CSV:

- Russia, China, Iran, and DPRK normalizers emit `map_layer="adversary_military"`, `location_category="Counterforce"`, and `dataset_type="military"`.
- `normalize_global_cities.py` emits `map_layer="global_metros"`, `location_category="Countervalue"`, and `dataset_type="metro_area"`.
- `normalize_us_military.py` emits `map_layer="us_military"`, `location_category="Military Site"`, `dataset_type="military"`, `country=Host_Country`, and `operator_country="United States"`.

The legacy `normalize_metro_areas.py` module remains for direct regression tests and historical reference, but `metro_areas.csv` is archived and not registered as an active source.

Each normalizer preserves original row values in `record.raw`. The loader records source encoding, row counts, invalid-coordinate exclusions, numeric warnings, optional-field gaps, load errors, and duplicate-coordinate groups. Duplicate coordinates are reported globally but records are retained.

## Filtering And Search

The above-map toolbar owns logical layer visibility through the `active-layers` checklist. `filter_records()` applies active layers, country, type, source file, and query filters in deterministic order. Country matching uses canonical DPRK handling, while U.S. site country matching uses host country.

Type options are contextual to active layers, selected country, and selected source files. Search scans normalized fields plus `record.raw`, so source-specific metadata remains discoverable without exposing raw metadata in GeoJSON.

Selection is stored as `selected-location-id`. Filter or layer changes keep the selected ID only if the selected record remains visible. Search-result selection and marker selection both use the same selected-ID path.

## Map And GeoJSON

The map still uses Dash Leaflet and one clustered `dl.GeoJSON` layer. Active logical layers are unioned server-side before GeoJSON generation. This avoids multiple overlapping cluster engines and keeps global zoom performance predictable.

GeoJSON properties are minimal: record ID, name, display country, `map_layer`, type/service text, marker colors, type code, and selected state. Complete source metadata is rendered from the server-side record in the details drawer.

Marker styling is layer-aware:

- `global_metros`: green civilian marker with `MET`.
- `adversary_military`: country-colored military marker.
- `us_military`: distinct U.S. service marker family using service abbreviations.

## Layout Controls

The root app shell contains the top bar, workspace grid, sidebar, map stage, legend, and details drawer. The duplicate floating custom map utility group has been removed. Top-bar buttons remain the only custom controls for sidebar collapse, fit-to-screen, full-map mode, and reset view.

`src/callbacks/layout_callbacks.py` owns layout-only state:

- `sidebar_collapsed`
- `full_map`
- `details_open`
- `resize_nonce`

These flags update CSS classes and button labels. They do not reload CSV data, reset filters, clear search text, or change the selected record except through the normal details close/selection path.

The clientside resize callback dispatches browser resize events and attempts Leaflet `invalidateSize()` after sidebar, full-map, details, and fit-to-screen changes.
