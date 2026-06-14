# Data Dictionary

## Normalized LocationRecord

- `id`: deterministic source row identifier. New CSVs use `source_file:Record_ID:slug`.
- `source_file`: active runtime CSV name.
- `map_layer`: `global_metros`, `adversary_military`, or `us_military`.
- `country`: geographic country used by the Country filter. For U.S. sites this is `Host_Country`.
- `operator_country`: military operator when applicable. U.S. sites use `United States`; metro records are null.
- `location_category`: `Counterforce`, `Countervalue`, or `Military Site`.
- `dataset_type`: `military` or `metro_area`.
- `name`: display name.
- `type`: source type, location type, or U.S. service branch.
- `latitude`, `longitude`: validated WGS84 decimal coordinates.
- `region`: source regional text.
- `admin_area`: global city `Admin1_Name` or U.S. site `Admin_Area`.
- `raw`: original source row values preserved for auditability.

## Adversary Military Fields

- `category_source`: DPRK category/source text.
- `alternate_names`, `iata`, `icao`, `use`, `subordinate`, `runways`, `tenants`: China source metadata.
- `notes`: Iran and DPRK notes where available.

## Global City Fields

Source file: `global_cities_metros_100k.csv`.

- `Record_ID` -> `id`
- `Location_Name` -> `name`
- `Location_Type` -> `type`
- `Country` -> `country`
- `ISO2` -> `iso2`
- `ISO3` -> `iso3`
- `Region` -> `region`
- `Admin1_Name` -> `admin_area`
- `Timezone` -> `timezone`
- `Population` -> `population`
- `Population_Source` -> `population_source`
- `Population_Bamwor` -> `population_bamwor`
- `Population_SimpleMaps` -> `population_simplemaps`
- `Population_Starting_List` -> `population_starting_list`
- `Population_Size_Class` -> `population_size_class`
- `Capital_Classification` -> `capital_classification` and legacy `capital_status`
- `Country_GDP_Per_Capita_USD` -> `country_gdp_per_capita_usd`
- `Country_GDP_PPP_USD` -> `country_gdp_ppp_usd`
- `OpenStreetMap_URL` -> `openstreetmap_url`
- `Wikipedia_Search_URL` -> `wikipedia_search_url`
- `Image_Research_URL` -> `image_research_url`
- `Primary_Source` -> `primary_source`
- `Starting_List_Included` -> `starting_list_included`

Population fields are parsed as integers when possible. GDP fields are parsed as optional numbers. `Starting_List_Included` is parsed as a Boolean when possible, while the raw original remains in `raw`.

## U.S. Military Site Fields

Source file: `us_military_sites.csv`.

- `Record_ID` -> `id`
- `Site` -> `name`
- `Component` -> `component`
- `Service_Branch` -> `service_branch` and `type`
- `Component_Status` -> `component_status`
- `Host_Country` -> `country`
- `Admin_Area` -> `admin_area`
- `Location_Class` -> `location_class`
- `Geographic_Scope` -> `geographic_scope`
- `Nearest_City` -> `nearest_city`
- `Coordinate_Quality` -> `coordinate_quality`
- `Buildings_Owned` -> `buildings_owned`
- `Buildings_Owned_SqFt` -> `buildings_owned_sqft`
- `Buildings_Leased` -> `buildings_leased`
- `Buildings_Leased_SqFt` -> `buildings_leased_sqft`
- `Buildings_Other` -> `buildings_other`
- `Buildings_Other_SqFt` -> `buildings_other_sqft`
- `Acres_Owned` -> `acres_owned`
- `Total_Acres` -> `total_acres`
- `Plant_Replacement_Value_M` -> `plant_replacement_value_m`
- `Coordinate_Source_URL` -> `coordinate_source_url`
- `Dataset_Source_URL` -> `dataset_source_url`
- `Notes` -> `notes`

Buildings are parsed as optional integers. Square footage, acreage, and plant replacement value are parsed as optional numbers. Non-empty invalid numerics are reported but do not drop the row.

## Quality Metrics

The aggregate report includes total rows, plotted rows, excluded rows, Counterforce and Countervalue totals, layer totals, source reports, duplicate-coordinate groups, and flattened warnings.

Each source report includes source encoding, loaded rows, plotted rows, coordinate cleanup counts, invalid-coordinate exclusions, invalid/missing population rows, numeric parse warnings, duplicate-coordinate record count, missing optional fields, parser warnings, and load errors.
