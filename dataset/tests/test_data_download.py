from __future__ import annotations

import pytest

from dataset.data_download import build_parser, collect_requested_files


def test_metadata_defaults_to_both_sources():
    args = build_parser().parse_args(["download", "metadata"])
    assert collect_requested_files(args) == [
        "PresenceOnlyOccurrences/PO_metadata_train.csv",
        "PresenceAbsenceSurveys/PA_metadata_train.csv",
        "PresenceAbsenceSurveys/PA_metadata_test_iid.csv",
        "PresenceAbsenceSurveys/PA_metadata_test_ood.csv",
        "PresenceAbsenceSurveys/PA_metadata_test_glc25.csv",
    ]


def test_environmental_values_defaults_to_all_variables_and_sources():
    args = build_parser().parse_args(["download", "environmental-values"])
    files = collect_requested_files(args)

    assert len(files) == 25
    assert files[:5] == [
        "EnvironmentalValues/Climate/PO-train-bioclimatic.csv",
        "EnvironmentalValues/Climate/PA-train-bioclimatic.csv",
        "EnvironmentalValues/Climate/PA-test-iid-bioclimatic.csv",
        "EnvironmentalValues/Climate/PA-test-ood-bioclimatic.csv",
        "EnvironmentalValues/Climate/PA-test-glc25-bioclimatic.csv",
    ]
    assert "EnvironmentalValues/SoilGrids/v2/PA-test-glc25-soilgrids.csv" in files


def test_environmental_values_can_filter_source_and_variables():
    args = build_parser().parse_args(["download", "environmental-values", "--source", "pa", "--variables", "climate"])
    assert collect_requested_files(args) == [
        "EnvironmentalValues/Climate/PA-train-bioclimatic.csv",
        "EnvironmentalValues/Climate/PA-test-iid-bioclimatic.csv",
        "EnvironmentalValues/Climate/PA-test-ood-bioclimatic.csv",
        "EnvironmentalValues/Climate/PA-test-glc25-bioclimatic.csv",
    ]


def test_bioclim_values_and_cubes_are_separate_categories():
    values = collect_requested_files(build_parser().parse_args(["download", "bioclim", "values", "--source", "po"]))
    cubes = collect_requested_files(build_parser().parse_args(["download", "bioclim", "cubes", "--source", "pa"]))
    assert values == ["TimeSeries/Bioclim/values/PO-train-bioclimatic_time_series.zip"]
    assert cubes == [
        "TimeSeries/Bioclim/cubes/PA-train-bioclimatic-monthly.zip",
        "TimeSeries/Bioclim/cubes/PA-test-iid-bioclimatic-monthly.zip",
        "TimeSeries/Bioclim/cubes/PA-test-ood-bioclimatic-monthly.zip",
        "TimeSeries/Bioclim/cubes/PA-test-glc25-bioclimatic-monthly.zip",
    ]


def test_landsat_values_and_cubes_are_separate_categories():
    values = collect_requested_files(build_parser().parse_args(["download", "landsat", "values", "--source", "both"]))
    cubes = collect_requested_files(build_parser().parse_args(["download", "landsat", "cubes", "--source", "both"]))
    assert values == [
        "TimeSeries/Landsat/values/PO-train-landsat-time-series.zip",
        "TimeSeries/Landsat/values/PA-train-landsat_time_series.zip",
        "TimeSeries/Landsat/values/PA-test-iid-landsat_time_series.zip",
        "TimeSeries/Landsat/values/PA-test-ood-landsat_time_series.zip",
        "TimeSeries/Landsat/values/PA-test-glc25-landsat_time_series.zip",
    ]
    assert cubes == [
        "TimeSeries/Landsat/cubes/PO-train-landsat-time-series.zip",
        "TimeSeries/Landsat/cubes/PA-train-landsat-time-series.zip",
        "TimeSeries/Landsat/cubes/PA-test-iid-landsat-time-series.zip",
        "TimeSeries/Landsat/cubes/PA-test-ood-landsat-time-series.zip",
        "TimeSeries/Landsat/cubes/PA-test-glc25-landsat-time-series.zip",
    ]


def test_satellite_data_can_filter_modalities():
    args = build_parser().parse_args(["download", "satellite-data", "--source", "pa", "--modalities", "alphaearth"])
    assert collect_requested_files(args) == [
        "SatelliteData/AlphaEarth/PA-train-alphaearth.parquet",
        "SatelliteData/AlphaEarth/PA-test-iid-alphaearth.parquet",
        "SatelliteData/AlphaEarth/PA-test-ood-alphaearth.parquet",
        "SatelliteData/AlphaEarth/PA-test-glc25-alphaearth.parquet",
    ]


def test_satellite_data_unknown_modality_lists_available_options():
    args = build_parser().parse_args(["download", "satellite-data", "--modalities", "tiff"])

    with pytest.raises(ValueError, match="Unknown satellite modality: 'tiff'.*sentinel2-tiff"):
        collect_requested_files(args)


def test_rasters_can_filter_variables():
    args = build_parser().parse_args(["download", "rasters", "--variables", "climate"])
    assert collect_requested_files(args) == [
        "EnvironmentalRasters/Climate/BioClimatic_Average_1981-2010.zip",
        "EnvironmentalRasters/Climate/Climatic_Monthly_1979-2019.zip",
    ]
