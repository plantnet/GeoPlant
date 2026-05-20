# GeoPlant Dataset Downloader

Download selected GeoPlant metadata, rasters, and pre-extracted modalities without fetching the full dataset archive.

## Install

```bash
uv sync
```

For tests:

```bash
uv sync --group dev
uv run pytest dataset/tests -q
```

## Usage

Run from the repository root:

```bash
python -m dataset.data_download --metadata --presence-absence --data ./data
```

Or use the Python API:

```python
from dataset import GeoPlant

gp = GeoPlant(root="data")
gp.download(metadata="pa")
gp.download(source="pa", variables="climate")
gp.download(source="pa", variables="climate", cubes=True, extract=True)
gp.download(rasters=True, variables="humanfootprint")
gp.download(rasters=True, variables="humanfootprint", legacy=True)
```

The downloader supports:

```text
Data types:
  --metadata
  --rasters
  --pre-extracted, --ready-to-use
  --cube               Download cube archives instead of CSV values when available
  --extract            Extract selected zip archives after all required files download
  --legacy            Download legacy raster/value files instead of the current default
```

```text
Data sources:
  --presence-only
  --presence-absence
```

If no source is selected for `--metadata`, both PO and PA metadata are downloaded.
PA metadata includes the train file plus the explicit IID, OOD, and combined
GLC25 test files. The test labels are carried by those split files, so the
downloader does not request separate `test_labels*.csv` files.

For `--pre-extracted`, you must also select one or more variables:

```text
Variables:
  --biogeographicalregions
  --climate
  --elevation
  --humanfootprint
  --landcover
  --soilgrids
  --satellitedata
  --satellitetimeseries
  --all-variables
```

`--satellitedata` resolves files under `SatelliteData/`: Sentinel-2 JPEG
archives, Sentinel-2 TIFF archives, and AlphaEarth Parquet files.
Use `--sentinel2-jpeg`, `--sentinel2-tiff`, or `--alphaearth` to limit
satellite downloads to one or more modalities.

## Examples

Download all metadata:

```bash
python -m dataset.data_download --metadata --data ./data
```

Download PA Bioclim time-series values:

```bash
python -m dataset.data_download \
  --pre-extracted \
  --presence-absence \
  --climate \
  --data ./data
```

Download PO Landsat time-series cubes:

```bash
python -m dataset.data_download \
  --ready-to-use \
  --presence-only \
  --satellitetimeseries \
  --cube \
  --data ./data
```

Download all raster layers that exist:

```bash
python -m dataset.data_download --rasters --all-variables --data ./data
```

Download PA AlphaEarth only:

```bash
python -m dataset.data_download \
  --ready-to-use \
  --presence-absence \
  --satellitedata \
  --alphaearth \
  --data ./data
```

## Notes

- The downloader talks directly to the GeoPlant Seafile host and preserves the published folder structure under your `--data` directory.
- Not every variable has both CSV and cube variants.
- Multipart archive datasets should be listed as nested file groups in `config.py`; extraction waits until every file in the group has downloaded.
- If any requested download fails, the command exits non-zero.
