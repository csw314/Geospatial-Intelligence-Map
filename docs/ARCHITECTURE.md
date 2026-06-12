# Architecture

The app keeps CSV parsing and validation outside Dash callbacks.

- `src/data`: reads CSV files, normalizes military and metro rows, validates coordinates, parses metro population values, and builds quality reports.
- `src/utils`: pure filtering, search, coordinate formatting, and GeoJSON generation.
- `src/components`: Dash layout factories.
- `src/callbacks`: Dash callback registration for filters, search, selection, details, map viewport, and responsive layout state.

The central loader registers one `SourceSpec` per dataset. Russia, China, Iran, and DPRK normalizers emit `Counterforce` / `military` records. The metro normalizer emits `Countervalue` / `metro_area` records from `metro_areas.csv` and falls back to `metro_area.csv` if only the singular filename exists.

Country-specific normalizers live in:

- `src/data/normalize_russia.py`
- `src/data/normalize_china.py`
- `src/data/normalize_iran.py`
- `src/data/normalize_dprk.py`
- `src/data/normalize_metro_areas.py`

Iran maps `Notes` into `notes`. DPRK maps `Category Source` into `category_source` and `Notes` into `notes`. Rows with invalid or missing coordinates raise a row-level validation error, are excluded from plotted records, and are reported in the per-source data-quality warnings.

The map layer is rendered as clustered GeoJSON using Dash Leaflet. Filter changes rebuild the server-side GeoJSON payload so clusters reflect the current visible record set. Marker styling branches on `dataset_type`, keeping military markers intact while rendering metro areas with a distinct civilian marker.

Search and filtering are pure utilities. The Dash callbacks combine Country, Location Category, Source File, Type, and text search filters before rebuilding map data and search results. Search covers common normalized fields plus country-specific notes/category-source fields and metro population/source fields.

## Layout Flow

The root layout uses a full-height app shell with a top bar, collapsible sidebar, map stage, overlay legend, and overlay details drawer. The map keeps the available space because details no longer permanently occupy a grid column.

`src/callbacks/layout_callbacks.py` owns layout-only state:

- `sidebar_collapsed`
- `full_map`
- `details_open`
- `resize_nonce`

These flags only update CSS classes and button labels. They do not reload CSV data, reset filters, clear search text, or alter selected markers. Selecting a marker opens the details drawer; closing the drawer does not clear the selected marker.

The same module registers a clientside callback that responds to layout state changes by dispatching browser resize events and attempting Leaflet `invalidateSize` when a map instance is available. This is needed because Leaflet maps may render stale tiles after parent containers change size.
