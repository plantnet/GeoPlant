from __future__ import annotations

import csv
import importlib.util
import sys
from pathlib import Path


SCRIPT_PATH = Path(__file__).parents[2] / "metadata-preprocessing/create_pa_test_splits.py"
SPEC = importlib.util.spec_from_file_location("create_pa_test_splits", SCRIPT_PATH)
create_pa_test_splits_module = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules["create_pa_test_splits"] = create_pa_test_splits_module
SPEC.loader.exec_module(create_pa_test_splits_module)


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="") as file_handle:
        writer = csv.DictWriter(file_handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as file_handle:
        return list(csv.DictReader(file_handle))


def test_create_pa_test_splits_writes_iid_and_ood_files(tmp_path):
    common = {
        "lon": "1.0",
        "lat": "2.0",
        "year": "2024",
        "geoUncertaintyInM": "5.0",
        "areaInM2": "100.0",
        "region": "TEST",
        "country": "France",
    }
    write_csv(
        tmp_path / "PA_metadata_train.csv",
        [{**common, "speciesId": "10", "surveyId": "1", "county": "A", "district": "B"}],
    )
    write_csv(
        tmp_path / "GLC25_PA_metadata_train.csv",
        [{**common, "speciesId": "10.0", "surveyId": "1"}],
    )
    write_csv(
        tmp_path / "PA_metadata_test.csv",
        [{**common, "surveyId": "2", "county": "A", "district": "B"}],
    )
    write_csv(
        tmp_path / "GLC25_PA_metadata_test (1).csv",
        [
            {**common, "surveyId": "2"},
            {**common, "surveyId": "3"},
        ],
    )
    write_csv(tmp_path / "test_labels.csv", [{"surveyId": "2", "predictions": "10 11"}])
    write_csv(
        tmp_path / "GLC25_SOLUTION_FILE-v2 (2).csv",
        [
            {"surveyId": "2", "predictions": "11 10", "Usage": "Public"},
            {"surveyId": "3", "predictions": "12 13", "Usage": "Private"},
        ],
    )

    summary = create_pa_test_splits_module.create_pa_test_splits(tmp_path, overwrite=True)

    assert summary.iid_rows == 1
    assert summary.ood_rows == 1
    assert summary.combined_rows == 2
    assert "testSplit" not in read_csv(tmp_path / "PA_metadata_test_iid.csv")[0]
    assert "testSplit" not in read_csv(tmp_path / "PA_metadata_test_ood.csv")[0]
    assert "testSplit" not in read_csv(tmp_path / "PA_metadata_test_glc25.csv")[0]
    assert read_csv(tmp_path / "test_labels_iid.csv") == [{"surveyId": "2", "speciesIds": "10 11"}]
    assert read_csv(tmp_path / "test_labels_glc25.csv") == [
        {"surveyId": "2", "speciesIds": "11 10"},
        {"surveyId": "3", "speciesIds": "12 13"},
    ]
    assert read_csv(tmp_path / "test_labels_ood.csv") == [{"surveyId": "3", "speciesIds": "12 13"}]
