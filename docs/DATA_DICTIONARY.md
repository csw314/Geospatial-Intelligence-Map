# Data Dictionary

## Normalized LocationRecord

- `id`: deterministic source row identifier
- `source_file`: `russia_data.csv`, `china_data.csv`, `iran_data.csv`, `dprk_data.csv`, or `metro_areas.csv`
- `country`: source country name
- `location_category`: `Counterforce` for Russia, China, Iran, and DPRK military rows; `Countervalue` for metro-area rows
- `dataset_type`: `military` or `metro_area`
- `name`: display name
- `type`: dynamic location type from the source CSV
- `latitude`, `longitude`: validated decimal coordinates
- `region`: Russia oblast or regional text when available
- `category_source`: DPRK category/source text when available
- `alternate_names`, `iata`, `icao`, `use`, `subordinate`, `runways`, `tenants`: China metadata when available
- `iso2`: metro-area ISO2 code when available
- `population`, `population_proper`: parsed metro population integers when available
- `capital_status`: metro capital status
- `source_country_name`: source file country label for metro rows
- `source_url`: source URL for metro rows
- `notes`: Iran and DPRK notes when available
- `raw`: source row values; metro rows preserve original values for auditability

## Quality Metrics

The data quality report includes source encoding, loaded rows, plotted rows, counterforce/countervalue totals, coordinate fixes, invalid-coordinate exclusions, invalid/missing metro population rows, duplicate coordinates, optional-field gaps, and parsing warnings.
