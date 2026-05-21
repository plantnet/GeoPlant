# GeoPlant Dataset Downloader

Download GeoPlant files by storage category without fetching the full dataset.

## Install

```bash
uv sync
```

For tests:

```bash
uv sync --group dev
uv run pytest dataset/tests -q
```

## CLI

Use one data category:

```text
geoplant download metadata
geoplant download environmental-values
geoplant download bioclim values
geoplant download bioclim cubes
geoplant download landsat values
geoplant download landsat cubes
geoplant download satellite-data
geoplant download rasters
```

Useful filters:

```text
--source po|pa|both          default: both
--variables elevation soilgrids
--modalities alphaearth sentinel2-tiff sentinel2-jpeg
--legacy
--extract
```

Category defaults download everything inside that category. Filters narrow it.

## Examples

All tabular `EnvironmentalValues`:

```bash
uv run geoplant download environmental-values \
  --source both \
  --data ./data
```

Only PA elevation values:

```bash
uv run geoplant download environmental-values \
  --source pa \
  --variables elevation \
  --data ./data
```

Bioclim time-series values:

```bash
uv run geoplant download bioclim values \
  --source both \
  --data ./data
```

Bioclim cubes, PA only, extracted after download:

```bash
uv run geoplant download bioclim cubes \
  --source pa \
  --extract \
  --data ./data
```

Landsat cubes, PO only:

```bash
uv run geoplant download landsat cubes \
  --source po \
  --data ./data
```

PA AlphaEarth only:

```bash
uv run geoplant download satellite-data \
  --source pa \
  --modalities alphaearth \
  --data ./data
```

Climate rasters only:

```bash
uv run geoplant download rasters \
  --variables climate \
  --data ./data
```

## Python API

```python
from dataset import GeoPlant

gp = GeoPlant(root="data")
gp.download(environmental_values=True, source="both")
gp.download(environmental_values=True, source="pa", variables="elevation")
gp.download(bioclim_cubes=True, source="pa", extract=True)
gp.download(satellite_data=True, source="pa", satellite_modalities="alphaearth")
gp.download(rasters=True, variables="climate")
```

## Notes

- Downloaded files keep the published Seafile folder structure under `--data`.
- `--environmental-values` means files under `EnvironmentalValues/`.
- Bioclim and Landsat time-series have their own categories.
- `--legacy` affects rasters and environmental values where legacy files exist.
