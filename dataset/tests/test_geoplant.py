from __future__ import annotations

from pathlib import Path
import zipfile

import pytest

from dataset import GeoPlant
from dataset.data_download import DownloadResult


def test_geoplant_selects_metadata_source():
    geoplant = GeoPlant(root="data")

    assert geoplant.files(metadata=True, source="pa") == [
        "PresenceAbsenceSurveys/PA_metadata_train.csv",
        "PresenceAbsenceSurveys/PA_metadata_test_iid.csv",
        "PresenceAbsenceSurveys/PA_metadata_test_ood.csv",
        "PresenceAbsenceSurveys/PA_metadata_test_glc25.csv",
    ]


def test_geoplant_selects_environmental_values_with_filters():
    geoplant = GeoPlant(root="data")

    assert geoplant.files(environmental_values=True, source="pa", variables="soilgrids", legacy=True) == [
        "EnvironmentalValues/SoilGrids/v1/PA-train-soilgrids.csv",
        "EnvironmentalValues/SoilGrids/v1/PA-test-soilgrids.csv",
    ]


def test_geoplant_selects_bioclim_values_and_cubes():
    geoplant = GeoPlant(root="data")

    assert geoplant.files(bioclim_values=True, source="po") == [
        "TimeSeries/Bioclim/values/PO-train-bioclimatic_time_series.zip",
    ]
    assert geoplant.files(bioclim_cubes=True, source="pa") == [
        "TimeSeries/Bioclim/cubes/PA-train-bioclimatic-monthly.zip",
        "TimeSeries/Bioclim/cubes/PA-test-iid-bioclimatic-monthly.zip",
        "TimeSeries/Bioclim/cubes/PA-test-ood-bioclimatic-monthly.zip",
        "TimeSeries/Bioclim/cubes/PA-test-glc25-bioclimatic-monthly.zip",
    ]


def test_geoplant_selects_rasters_with_filters():
    geoplant = GeoPlant(root="data")

    assert geoplant.files(rasters=True, variables="climate") == [
        "EnvironmentalRasters/Climate/BioClimatic_Average_1981-2010.zip",
        "EnvironmentalRasters/Climate/Climatic_Monthly_1979-2019.zip",
    ]


def test_geoplant_can_select_satellite_modalities():
    geoplant = GeoPlant(root="data")

    assert geoplant.files(satellite_data=True, source="pa", satellite_modalities="alphaearth") == [
        "SatelliteData/AlphaEarth/PA-train-alphaearth.parquet",
        "SatelliteData/AlphaEarth/PA-test-iid-alphaearth.parquet",
        "SatelliteData/AlphaEarth/PA-test-ood-alphaearth.parquet",
        "SatelliteData/AlphaEarth/PA-test-glc25-alphaearth.parquet",
    ]


def test_geoplant_unknown_satellite_modality_lists_available_options():
    geoplant = GeoPlant(root="data")

    with pytest.raises(ValueError, match="Unknown satellite modality: 'tiff'.*sentinel2-tiff"):
        geoplant.files(satellite_data=True, satellite_modalities="tiff")


def test_geoplant_path_resolves_under_root():
    geoplant = GeoPlant(root=Path("data"))

    assert geoplant.path("PresenceAbsenceSurveys/PA_metadata_test_iid.csv") == Path(
        "data/PresenceAbsenceSurveys/PA_metadata_test_iid.csv"
    )


def test_geoplant_download_uses_selected_files_and_root(monkeypatch):
    calls = []

    def fake_download_files(file_paths, output_dir):
        calls.append((file_paths, output_dir))
        return [DownloadResult(file_path=file_paths[0], success=True)]

    monkeypatch.setattr("dataset.geoplant.download_files", fake_download_files)
    geoplant = GeoPlant(root=Path("data"))

    results = geoplant.download(environmental_values=True, source="pa", variables="elevation")

    assert calls == [
        (
            [
                "EnvironmentalValues/Elevation/PA-train-elevation.csv",
                "EnvironmentalValues/Elevation/PA-test-iid-elevation.csv",
                "EnvironmentalValues/Elevation/PA-test-ood-elevation.csv",
                "EnvironmentalValues/Elevation/PA-test-glc25-elevation.csv",
            ],
            Path("data"),
        )
    ]
    assert results == [DownloadResult(file_path="EnvironmentalValues/Elevation/PA-train-elevation.csv", success=True)]


def test_geoplant_extract_selected_zip_files(tmp_path):
    archive_path = tmp_path / "TimeSeries/Bioclim/cubes/PA-test-iid-bioclimatic-monthly.zip"
    archive_path.parent.mkdir(parents=True)
    with zipfile.ZipFile(archive_path, "w") as archive:
        archive.writestr("sample.txt", "ok")

    geoplant = GeoPlant(root=tmp_path)
    results = geoplant.extract(bioclim_cubes=True, source="pa")

    selected = [result for result in results if result.archive_path == str(archive_path)]
    assert selected
    assert selected[0].success
    assert (archive_path.with_suffix("") / "sample.txt").read_text() == "ok"


def test_geoplant_download_extract_uses_group_completion(monkeypatch):
    calls = []

    def fake_download_files(file_paths, output_dir):
        return [
            DownloadResult(file_path=file_paths[0], success=True),
            DownloadResult(file_path=file_paths[1], success=False, error="missing"),
        ]

    def fake_extract_groups(file_groups, output_dir, successful_files, overwrite=False):
        calls.append((file_groups, output_dir, successful_files, overwrite))
        return []

    monkeypatch.setattr(GeoPlant, "file_groups", lambda self, **kwargs: [["a.zip", "b.zip"]])
    monkeypatch.setattr("dataset.geoplant.download_files", fake_download_files)
    monkeypatch.setattr("dataset.geoplant.extract_downloaded_file_groups", fake_extract_groups)

    geoplant = GeoPlant(root=Path("data"))
    geoplant.download(satellite_data=True, source="po", extract=True, overwrite=True)

    assert calls == [([["a.zip", "b.zip"]], Path("data"), {"a.zip"}, True)]
