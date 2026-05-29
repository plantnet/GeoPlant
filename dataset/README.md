# GeoPlant Dataset Downloader

GeoPlant is large and multimodal. 
This downloader is therefore meant for partial, repeatable downloads.
The data are structured  as follows:

```text
GeoPlantData/
  PresenceAbsenceSurveys/
  PresenceOnlyOccurrences/
  EnvironmentalValues/
  EnvironmentalRasters/
  TimeSeries/
  SatelliteData/
```

If you download `EnvironmentalValues/Climate/PA-train-bioclimatic.csv` with
`root="GeoPlantData"` or `--data ./GeoPlantData`, it is saved as:

```text
GeoPlantData/EnvironmentalValues/Climate/PA-train-bioclimatic.csv
```

## Mental Model

Downloads should follow three steps.

1. Choose the observation source:
```text
po   --> Presence-only training observations
pa   --> Presence-absence train and test surveys
both --> PO + PA, default
```

2. Choose the data family:

| Data family | Folder | Use it for | Python helper | CLI command |
| --- | --- | --- | --- | --- |
| Metadata | `PresenceOnlyOccurrences/`, `PresenceAbsenceSurveys/` | survey IDs, species lists, coordinates, split metadata | `download_metadata()` | `metadata` |
| Environmental values | `EnvironmentalValues/` | tabular CSV predictors for XGBoost, MaxEnt, MLPs, quick experiments | `download_environmental_values()` | `environmental-values` |
| Environmental rasters | `EnvironmentalRasters/` | spatial raster layers and custom extraction | `download_rasters()` | `rasters` |
| Bioclim time series | `TimeSeries/Bioclim/` | monthly climate values or cube tensors | `download_bioclim(...)` | `bioclim values`, `bioclim cubes` |
| Landsat time series | `TimeSeries/Landsat/` | Landsat values or cube tensors | `download_landsat(...)` | `landsat values`, `landsat cubes` |
| Satellite data | `SatelliteData/` | Sentinel-2 patches and AlphaEarth embeddings | `download_satellite_data()` | `satellite-data` |

3. Narrow the request if needed:

| Filter | Values | Applies to |
| --- | --- | --- |
| `source` / `--source` | `po`, `pa`, `both` | metadata, environmental-values, bioclim, landsat, satellite-data |
| `variables` / `--variables` | predictor names | environmental-values, rasters |
| `modalities` / `--modalities` | satellite modality names | satellite-data |
| `legacy` / `--legacy` | boolean or flag | environmental-values, rasters |
| `extract` / `--extract` | boolean or flag | zip archives |

## Important Distinction

Climate appears in two places because it is used in two different ways:

```text
EnvironmentalValues/Climate    static tabular bioclimatic CSV predictors
TimeSeries/Bioclim             monthly Bioclim time-series values and cubes
```

Use `environmental-values` for static tabular climate CSVs. Use
`bioclim values` or `bioclim cubes` for time-series data.

## Available Filters

Environmental value variables:

```text
climate
elevation
humanfootprint
landcover
soilgrids
```

Raster variables:

```text
biogeographicalregions
climate
elevation
humanfootprint
landcover
soilgrids
```

Satellite modalities:

```text
alphaearth
sentinel2-jpeg
sentinel2-tiff
```

Use the full Sentinel-2 modality names: `sentinel2-tiff`, not `tiff`;
`sentinel2-jpeg`, not `jpeg`. If a modality is unknown, the downloader prints
the available options.

## Install

From the repository root:

```bash
uv sync
```

For tests:

```bash
uv sync --group dev
uv run pytest dataset/tests -q
```

## Notebook Workflow

Start with one local dataset root:

```python
from dataset import GeoPlant

gp = GeoPlant(root="GeoPlantData")
```

Preview selected files before downloading:

```python
gp.files(environmental_values=True, variables="climate")
gp.files(satellite_data=True, source="po", satellite_modalities="sentinel2-tiff")
```

Download metadata:

```python
gp.download_metadata()
gp.download_metadata(source="pa")
```

Download tabular EnvironmentalValues:

```python
# all current EnvironmentalValues CSVs, PO + PA
gp.download_environmental_values()

# climate CSVs only
gp.download_climate_values()

# PA only
gp.download_environmental_values(source="pa")

# variable subset
gp.download_environmental_values(
    source="both",
    variables=["climate", "elevation", "soilgrids"],
)

# legacy files where available
gp.download_environmental_values(
    source="both",
    variables=["climate", "humanfootprint", "soilgrids"],
    legacy=True,
)
```

Download Bioclim time series:

```python
gp.download_bioclim("values", source="both")
gp.download_bioclim("cubes", source="pa", extract=True)
```

Download Landsat time series:

```python
gp.download_landsat("values", source="both")
gp.download_landsat("cubes", source="pa", extract=True)
```

Download SatelliteData:

```python
gp.download_satellite_data()
gp.download_satellite_data(source="pa", modalities="alphaearth")
gp.download_satellite_data(source="po", modalities="sentinel2-tiff", extract=True)
```

Download rasters:

```python
gp.download_rasters()
gp.download_rasters(variables="climate")
gp.download_rasters(variables=["climate", "elevation", "landcover"])
gp.download_rasters(variables="humanfootprint", legacy=True)
```

The lower-level API is also available if you prefer explicit flags:

```python
gp.download(environmental_values=True, source="pa", variables="climate")
gp.download(bioclim_cubes=True, source="pa", extract=True)
gp.download(satellite_data=True, source="po", satellite_modalities="sentinel2-tiff")
```

## CLI Workflow

Every command follows the same shape:

```bash
uv run geoplant download <family> [subcategory] --data ./GeoPlantData
```

Available commands:

```text
metadata
environmental-values
rasters
bioclim values
bioclim cubes
landsat values
landsat cubes
satellite-data
```

Metadata:

```bash
uv run geoplant download metadata --data ./GeoPlantData
uv run geoplant download metadata --source pa --data ./GeoPlantData
```

All tabular EnvironmentalValues:

```bash
uv run geoplant download environmental-values \
  --source both \
  --data ./GeoPlantData
```

Only PA climate and soil CSVs:

```bash
uv run geoplant download environmental-values \
  --source pa \
  --variables climate soilgrids \
  --data ./GeoPlantData
```

Bioclim time-series values and cubes:

```bash
uv run geoplant download bioclim values \
  --source both \
  --data ./GeoPlantData

uv run geoplant download bioclim cubes \
  --source pa \
  --data ./GeoPlantData \
  --extract
```

Landsat values and cubes:

```bash
uv run geoplant download landsat values \
  --source both \
  --data ./GeoPlantData

uv run geoplant download landsat cubes \
  --source po \
  --data ./GeoPlantData \
  --extract
```

Satellite data:

```bash
uv run geoplant download satellite-data \
  --source pa \
  --modalities alphaearth \
  --data ./GeoPlantData

uv run geoplant download satellite-data \
  --source po \
  --modalities sentinel2-tiff \
  --data ./GeoPlantData \
  --extract
```

Rasters:

```bash
uv run geoplant download rasters \
  --variables climate elevation landcover \
  --data ./GeoPlantData
```

## Extraction And Resume

Downloads are safe to rerun. Complete files with the expected size are skipped.

Extract already downloaded archives from Python:

```python
gp.extract(bioclim_cubes=True, source="both")
gp.extract(landsat_cubes=True, source="pa")
gp.extract(satellite_data=True, source="po", satellite_modalities="sentinel2-tiff")
```

Multipart archives use a completion marker:

```text
.geoplant_extract_complete
```

If extraction failed midway and the output folder exists without this marker,
rerun the same `gp.extract(...)` call. The downloader treats the folder as
incomplete and extracts into it again.

Force extraction into an existing folder:

```python
gp.extract(
    satellite_data=True,
    source="po",
    satellite_modalities="sentinel2-tiff",
    overwrite=True,
)
```

## Troubleshooting

### `GeoPlant` Has No New Method In Notebook

The notebook kernel may be using an older editable install. Check:

```python
import dataset
from dataset import GeoPlant
import inspect

print(dataset.__file__)
print(inspect.getsourcefile(GeoPlant))
```

Then reinstall from the repo and restart the kernel:

```python
%pip install -e /Users/lukaspicek/Documents/Projects/INRIA/GLC/GeoPlant
```

### `Unknown satellite modality: 'tiff'`

Use the full modality name:

```python
gp.download_satellite_data(modalities="sentinel2-tiff")
```

Valid values:

```text
alphaearth
sentinel2-jpeg
sentinel2-tiff
```

### Climate Values Missing

Use `download_environmental_values(...)` for static tabular climate CSVs:

```python
gp.download_environmental_values(variables="climate")
```

Use `download_bioclim(...)` only for Bioclim time-series archives:

```python
gp.download_bioclim("values")
gp.download_bioclim("cubes")
```

### Extraction Skips Existing Folder

If grouped extraction completed, the output folder contains
`.geoplant_extract_complete` and reruns skip it. To extract again:

```python
gp.extract(
    satellite_data=True,
    source="po",
    satellite_modalities="sentinel2-tiff",
    overwrite=True,
)
```
