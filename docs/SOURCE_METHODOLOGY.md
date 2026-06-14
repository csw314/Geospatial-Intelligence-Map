# Source Methodology

This document summarizes the supporting workbook notes retained under `docs/source-data/`. The running application uses only CSV files from `data/raw/`.

## Global Cities And Metro Areas

Runtime file: `data/raw/global_cities_metros_100k.csv`.

Supporting workbook: `docs/source-data/global_cities_metros_100k_analysis.xlsx`.

Validation summary:

- 7,027 total records.
- 7,027 valid coordinates.
- 180 countries/territories.
- 602 records linked to the uploaded starting list.
- 184 national capitals and 4,276 records with some capital classification.
- 7,022 records with populated country GDP per-capita values.

Workbook source notes:

- Uploaded starting CSV: audited 604 supplied rows and retained source-specific population and capital fields. The workbook notes that the starting list covered four countries and had some damaged transliterations.
- Bamwor Global Cities Public: primary backbone for 5,979 qualifying records, updated March 12, 2026, CC BY 4.0. URL: `https://github.com/bamwor-dev/bamwor-open-data/tree/main/datasets/public/global_cities_public`.
- SimpleMaps-derived world-cities source: supplementary locations and metro-style population estimates. URLs: `https://simplemaps.com/data/world-cities` and `https://github.com/condwanaland/worldcities`.
- GeoNames: secondary identifiers, alternate names, feature codes, administrative codes, timezones, and elevation. URL: `https://download.geonames.org/export/dump/`.
- Bamwor Global Economy: country GDP PPP and GDP per-capita fields. URL: `https://github.com/bamwor-dev/bamwor-open-data/tree/main/datasets/public/global_economy`.
- CountryInfo and pycountry: ISO identifiers and descriptive country metadata. URLs: `https://pypi.org/project/countryinfo/` and `https://pypi.org/project/pycountry/`.
- GHSL Urban Centre Database 2025 is recommended for future polygon joins but is not embedded. URL: `https://data.jrc.ec.europa.eu/dataset/1a338be6-7eaf-480c-9664-3a8ade88cbcd`.

Methodology caveats:

- Each record has at least one source reporting 100,000 people or more.
- The selected `Population` is the maximum reported value across linked sources, not a harmonized metro statistic.
- Entity resolution used country-constrained normalized-name matching and coordinate-distance checks.
- Geospatial representation is an EPSG:4326 representative point; no metro or administrative polygon is implied.
- Qualifying populated-place subdivisions are retained and classified explicitly.
- Country GDP fields are national indicators, not city or metro measures.
- Wikimedia discovery URLs are included for research; licensing requires separate review.

## U.S. Military Sites

Runtime file: `data/raw/us_military_sites.csv`.

Supporting workbook: `docs/source-data/us_military_sites_worldwide_fy2024_geospatial.xlsx`.

Validation summary:

- 1,626 total site records.
- 1,626 valid point coordinates.
- 40 host countries/jurisdictions.
- Service totals: Army 623, Air Force 469, Navy 452, Marine Corps 80, Washington Headquarters Services 2.
- Geographic scope in the workbook summary: 1,028 CONUS, 407 OCONUS foreign, 191 OCONUS U.S. jurisdiction.
- Coordinate-quality summary in the workbook: 1,008 dataset geocode, 560 row-level source provided, 56 approximate.

Workbook source notes:

- Primary dataset: FY2024 DoD Base Structure Report records geocoded by the U.S. Base Project.
- Dataset page: `https://usbaseproject.com/data/`.
- Downloaded workbook: `https://usbaseproject.com/wp-content/uploads/2024/11/BSR-FY24_Lat-Long.xlsx`.
- Official DoD BSR library: `https://www.acq.osd.mil/eie/imr/rpid/library.html`.
- Dataset date: FY2024 inventory; source workbook published November 2024.

Methodology caveats:

- The unit of observation is a site: one specific geographic location containing real-property assets. Multiple sites may be assigned to one installation.
- Coverage is public acknowledged BSR site records. It is not guaranteed to list every classified, temporary, contingency, leased-access, or operational location.
- Coordinates are public point coordinates representing a site location or approximate centroid. They are not installation boundaries, entrances, or tactical coordinates.
- Coordinate reference system is WGS 84 / CRS84 longitude-latitude points.
- Closed, inactive, excess, or awaiting-disposal records can remain in BSR data. Presence in the file does not prove current operational status.
- The terms base, installation, and site are not interchangeable. Use `Record_ID` as the stable row key for this export.
