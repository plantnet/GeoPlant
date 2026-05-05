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
    assert "PresenceAbsenceSurveys/PA_metadata_test.csv" in files
    assert "PresenceAbsenceSurveys/test_labels.csv" in files


def test_collect_requested_files_for_presence_absence_climate_csvs():
    parser = build_parser()
    args = parser.parse_args(["--pre-extracted", "--presence-absence", "--climate"])
    files = collect_requested_files(args)
    assert files == [
        "BioclimTimeSeries/values/PA-test-bioclimatic-average.csv",
        "BioclimTimeSeries/values/PA-test-bioclimatic-monthly.csv",
        "BioclimTimeSeries/values/PA-train-bioclimatic-average.csv",
        "BioclimTimeSeries/values/PA-train-bioclimatic-monthly.csv",
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
