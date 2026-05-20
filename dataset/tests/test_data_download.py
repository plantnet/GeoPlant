from __future__ import annotations

from dataset.data_download import build_parser, collect_requested_files, files_for_variable


def test_files_for_variable_uses_csvs_for_non_cube_downloads():
    structure = {
        "climate": {
            "csvs": ["a.csv", "b.csv"],
            "cubes": ["a.zip"],
        }
    }
    assert files_for_variable(structure, cubes=False, variable="climate") == ["a.csv", "b.csv"]
    assert files_for_variable(structure, cubes=True, variable="climate") == ["a.zip"]


def test_collect_requested_files_defaults_metadata_to_both_sources():
    parser = build_parser()
    args = parser.parse_args(["--metadata"])
    files = collect_requested_files(args)
    assert "PresenceOnlyOccurrences/PO_metadata_train.csv" in files
    assert "PresenceAbsenceSurveys/PA_metadata_train.csv" in files
    assert "PresenceAbsenceSurveys/PA_metadata_test_iid.csv" in files
    assert "PresenceAbsenceSurveys/PA_metadata_test_ood.csv" in files
    assert "PresenceAbsenceSurveys/PA_metadata_test_glc25.csv" in files
    assert "PresenceAbsenceSurveys/PA_metadata_test.csv" not in files
    assert "PresenceAbsenceSurveys/test_labels.csv" not in files
    assert "PresenceAbsenceSurveys/test_labels_iid.csv" not in files
    assert "PresenceAbsenceSurveys/test_labels_ood.csv" not in files
    assert "PresenceAbsenceSurveys/test_labels_glc25.csv" not in files


def test_collect_requested_files_for_climate_rasters():
    parser = build_parser()
    args = parser.parse_args(["--rasters", "--climate"])
    files = collect_requested_files(args)
    assert files == [
        "EnvironmentalRasters/Climate/BioClimatic_Average_1981-2010.zip",
        "EnvironmentalRasters/Climate/Climatic_Monthly_1979-2019.zip",
    ]


def test_collect_requested_files_for_all_rasters():
    parser = build_parser()
    args = parser.parse_args(["--rasters", "--all-variables"])
    files = collect_requested_files(args)
    assert files == [
        "EnvironmentalRasters/BiogeographicalRegions/Bioregions-Europe-2016-v1.geojson",
        "EnvironmentalRasters/Climate/BioClimatic_Average_1981-2010.zip",
        "EnvironmentalRasters/Climate/Climatic_Monthly_1979-2019.zip",
        "EnvironmentalRasters/Elevation/ASTER_Elevation.tif",
        "EnvironmentalRasters/HumanFootprint/v2/OSM_detailed.zip",
        "EnvironmentalRasters/LandCover/LandCover_MODIS_Terra-Aqua_500m.tif",
        "EnvironmentalRasters/Soilgrids/soilgrids.zip",
    ]


def test_collect_requested_files_can_select_legacy_rasters():
    parser = build_parser()
    args = parser.parse_args(["--rasters", "--humanfootprint", "--legacy"])
    files = collect_requested_files(args)
    assert files == [
        "EnvironmentalRasters/HumanFootprint/v1/summarized.zip",
        "EnvironmentalRasters/HumanFootprint/v1/detailed.zip",
    ]


def test_collect_requested_files_for_presence_absence_climate_csvs():
    parser = build_parser()
    args = parser.parse_args(["--pre-extracted", "--presence-absence", "--climate"])
    files = collect_requested_files(args)
    assert files == [
        "TimeSeries/Bioclim/values/PA-train-bioclimatic_time_series.zip",
        "TimeSeries/Bioclim/values/PA-test-iid-bioclimatic_time_series.zip",
        "TimeSeries/Bioclim/values/PA-test-ood-bioclimatic_time_series.zip",
        "TimeSeries/Bioclim/values/PA-test-glc25-bioclimatic_time_series.zip",
    ]


def test_collect_requested_files_for_presence_absence_elevation_values():
    parser = build_parser()
    args = parser.parse_args(["--pre-extracted", "--presence-absence", "--elevation"])
    files = collect_requested_files(args)
    assert files == [
        "EnvironmentalValues/Elevation/PA-train-elevation.csv",
        "EnvironmentalValues/Elevation/PA-test-iid-elevation.csv",
        "EnvironmentalValues/Elevation/PA-test-ood-elevation.csv",
        "EnvironmentalValues/Elevation/PA-test-glc25-elevation.csv",
    ]


def test_collect_requested_files_for_presence_absence_environmental_values_use_splits():
    parser = build_parser()
    args = parser.parse_args(
        ["--pre-extracted", "--presence-absence", "--humanfootprint", "--landcover", "--soilgrids"]
    )
    files = collect_requested_files(args)
    assert files == [
        "EnvironmentalValues/HumanFootprint/v2/PA-train-human_footprint.csv",
        "EnvironmentalValues/HumanFootprint/v2/PA-test-human_footprint.csv",
        "EnvironmentalValues/HumanFootprint/v2/PA-test-ood-human_footprint.csv",
        "EnvironmentalValues/HumanFootprint/v2/PA-test-glc25-human_footprint.csv",
        "EnvironmentalValues/LandCover/PA-train-landcover.csv",
        "EnvironmentalValues/LandCover/PA-test-iid-landcover.csv",
        "EnvironmentalValues/LandCover/PA-test-ood-landcover.csv",
        "EnvironmentalValues/LandCover/PA-test-glc25-landcover.csv",
        "EnvironmentalValues/SoilGrids/v2/PA-train-soilgrids.csv",
        "EnvironmentalValues/SoilGrids/v2/PA-test-iid-soilgrids.csv",
        "EnvironmentalValues/SoilGrids/v2/PA-test-ood-soilgrids.csv",
        "EnvironmentalValues/SoilGrids/v2/PA-test-glc25-soilgrids.csv",
    ]


def test_collect_requested_files_can_select_legacy_environmental_values():
    parser = build_parser()
    args = parser.parse_args(
        [
            "--pre-extracted",
            "--presence-absence",
            "--humanfootprint",
            "--soilgrids",
            "--legacy",
        ]
    )
    files = collect_requested_files(args)
    assert files == [
        "EnvironmentalValues/HumanFootprint/v1/PA-train-human-footprint.csv",
        "EnvironmentalValues/HumanFootprint/v1/PA-test-human-footprint.csv",
        "EnvironmentalValues/SoilGrids/v1/PA-train-soilgrids.csv",
        "EnvironmentalValues/SoilGrids/v1/PA-test-soilgrids.csv",
    ]


def test_collect_requested_files_for_presence_only_values_use_environmental_values():
    parser = build_parser()
    args = parser.parse_args(
        ["--pre-extracted", "--presence-only", "--elevation", "--humanfootprint", "--landcover", "--soilgrids"]
    )
    files = collect_requested_files(args)
    assert files == [
        "EnvironmentalValues/Elevation/PO-train-elevation.csv",
        "EnvironmentalValues/HumanFootprint/v2/PO-train-human_footprint.csv",
        "EnvironmentalValues/LandCover/PO-train-landcover.csv",
        "EnvironmentalValues/SoilGrids/v2/PO-train-soilgrids.csv",
    ]


def test_collect_requested_files_for_presence_only_satellite_data():
    parser = build_parser()
    args = parser.parse_args(["--pre-extracted", "--presence-only", "--satellitedata"])
    files = collect_requested_files(args)
    assert files[:2] == [
        "SatelliteData/Sentinel2Patches-jpeg/PO-Train-Sentinel2Patches-NIR.zip",
        "SatelliteData/Sentinel2Patches-jpeg/PO-Train-Sentinel2Patches-RGB.zip",
    ]
    assert files[2:26] == [
        f"SatelliteData/Sentinel2Patches-tiff/PO-Train-Sentinel2Patches-part-{part:02d}.zip"
        for part in range(24)
    ]
    assert files[26:] == ["SatelliteData/AlphaEarth/PO-train-alphaearth.parquet"]


def test_collect_requested_files_for_presence_absence_satellite_data_uses_split_tiff_tests():
    parser = build_parser()
    args = parser.parse_args(["--pre-extracted", "--presence-absence", "--satellitedata"])
    files = collect_requested_files(args)
    assert files[:2] == [
        "SatelliteData/Sentinel2Patches-jpeg/PA-Train-Sentinel2Patches-RGB+NIR.zip",
        "SatelliteData/Sentinel2Patches-jpeg/PA-Test-IID-Sentinel2Patches.zip",
    ]
    assert files[2:] == [
        "SatelliteData/Sentinel2Patches-tiff/PA-Train-Sentinel2Patches.zip",
        "SatelliteData/Sentinel2Patches-tiff/PA-Test-IID-Sentinel2Patches.zip",
        "SatelliteData/Sentinel2Patches-tiff/PA-Test-OOD-Sentinel2Patches.zip",
        "SatelliteData/Sentinel2Patches-tiff/PA-Test-GLC25-Sentinel2Patches.zip",
        "SatelliteData/AlphaEarth/PA-train-alphaearth.parquet",
        "SatelliteData/AlphaEarth/PA-test-iid-alphaearth.parquet",
        "SatelliteData/AlphaEarth/PA-test-ood-alphaearth.parquet",
        "SatelliteData/AlphaEarth/PA-test-glc25-alphaearth.parquet",
    ]


def test_collect_requested_files_can_select_presence_absence_alphaearth_only():
    parser = build_parser()
    args = parser.parse_args(["--ready-to-use", "--presence-absence", "--satellitedata", "--alphaearth"])
    files = collect_requested_files(args)
    assert files == [
        "SatelliteData/AlphaEarth/PA-train-alphaearth.parquet",
        "SatelliteData/AlphaEarth/PA-test-iid-alphaearth.parquet",
        "SatelliteData/AlphaEarth/PA-test-ood-alphaearth.parquet",
        "SatelliteData/AlphaEarth/PA-test-glc25-alphaearth.parquet",
    ]


def test_collect_requested_files_can_select_presence_only_alphaearth_only():
    parser = build_parser()
    args = parser.parse_args(["--pre-extracted", "--presence-only", "--satellitedata", "--alphaearth"])
    files = collect_requested_files(args)
    assert files == ["SatelliteData/AlphaEarth/PO-train-alphaearth.parquet"]


def test_collect_requested_files_can_select_satellite_modalities_together():
    parser = build_parser()
    args = parser.parse_args(
        ["--pre-extracted", "--presence-absence", "--satellitedata", "--sentinel2-tiff", "--alphaearth"]
    )
    files = collect_requested_files(args)
    assert files == [
        "SatelliteData/Sentinel2Patches-tiff/PA-Train-Sentinel2Patches.zip",
        "SatelliteData/Sentinel2Patches-tiff/PA-Test-IID-Sentinel2Patches.zip",
        "SatelliteData/Sentinel2Patches-tiff/PA-Test-OOD-Sentinel2Patches.zip",
        "SatelliteData/Sentinel2Patches-tiff/PA-Test-GLC25-Sentinel2Patches.zip",
        "SatelliteData/AlphaEarth/PA-train-alphaearth.parquet",
        "SatelliteData/AlphaEarth/PA-test-iid-alphaearth.parquet",
        "SatelliteData/AlphaEarth/PA-test-ood-alphaearth.parquet",
        "SatelliteData/AlphaEarth/PA-test-glc25-alphaearth.parquet",
    ]


def test_collect_requested_files_can_select_legacy_presence_only_values():
    parser = build_parser()
    args = parser.parse_args(
        ["--pre-extracted", "--presence-only", "--humanfootprint", "--soilgrids", "--legacy"]
    )
    files = collect_requested_files(args)
    assert files == [
        "EnvironmentalValues/HumanFootprint/v1/PO-train-human-footprint.csv",
        "EnvironmentalValues/SoilGrids/v1/PO-train-soilgrids.csv",
    ]


def test_collect_requested_files_for_presence_only_climate_monthly_uses_bioclim_time_series():
    parser = build_parser()
    args = parser.parse_args(["--pre-extracted", "--presence-only", "--climate"])
    files = collect_requested_files(args)
    assert files == [
        "TimeSeries/Bioclim/values/PO-train-bioclimatic_time_series.zip",
    ]


def test_collect_requested_files_for_presence_only_climate_cubes_uses_bioclim_time_series():
    parser = build_parser()
    args = parser.parse_args(["--pre-extracted", "--cube", "--presence-only", "--climate"])
    files = collect_requested_files(args)
    assert files == [
        "TimeSeries/Bioclim/cubes/PO-train-bioclimatic-monthly.zip",
    ]


def test_collect_requested_files_for_landsat_values_use_time_series_layout():
    parser = build_parser()
    args = parser.parse_args(["--pre-extracted", "--presence-only", "--presence-absence", "--satellitetimeseries"])
    files = collect_requested_files(args)
    assert files == [
        "TimeSeries/Landsat/values/PO-train-landsat-time-series.zip",
        "TimeSeries/Landsat/values/PA-train-landsat_time_series.zip",
        "TimeSeries/Landsat/values/PA-test-iid-landsat_time_series.zip",
        "TimeSeries/Landsat/values/PA-test-ood-landsat_time_series.zip",
        "TimeSeries/Landsat/values/PA-test-glc25-landsat_time_series.zip",
    ]


def test_collect_requested_files_for_landsat_cubes_use_time_series_layout():
    parser = build_parser()
    args = parser.parse_args(
        ["--pre-extracted", "--cube", "--presence-only", "--presence-absence", "--satellitetimeseries"]
    )
    files = collect_requested_files(args)
    assert files == [
        "TimeSeries/Landsat/cubes/PO-train-landsat-time-series.zip",
        "TimeSeries/Landsat/cubes/PA-train-landsat-time-series.zip",
        "TimeSeries/Landsat/cubes/PA-test-iid-landsat-time-series.zip",
        "TimeSeries/Landsat/cubes/PA-test-ood-landsat-time-series.zip",
        "TimeSeries/Landsat/cubes/PA-test-glc25-landsat-time-series.zip",
    ]


def test_collect_requested_files_requires_variable_for_pre_extracted():
    parser = build_parser()
    args = parser.parse_args(["--pre-extracted", "--presence-only"])
    try:
        collect_requested_files(args)
    except ValueError as exc:
        assert "requires at least one variable" in str(exc)
    else:
        raise AssertionError("Expected a ValueError when no variable is selected.")
