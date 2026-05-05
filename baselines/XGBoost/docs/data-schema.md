
# Data Schema

## Metadata (train/test)
Required:
- `surveyId` (key)

Optional numeric:
- `lat`, `lon`
- `geoUncertaintyInM`, `areaInM2`, `year`

Optional categorical:
- `country`, `region`, `taxonRank`, `county`, `disctrict`

## Predictors (per family)
- TRAIN and TEST CSVs, each with `surveyId` and **numeric** columns.
- Columns are prefixed on load (e.g., `clim_*`, `soil_*`, `lc_*`, `hfp_*`).

## Labels (train only)
- Provided **inside train metadata** as **long format** (`surveyId`, `speciesId`).
- Convert to wide 0/1 with `build_wide_labels_from_long_metadata`.
