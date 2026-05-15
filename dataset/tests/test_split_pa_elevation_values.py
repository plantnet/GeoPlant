from __future__ import annotations

import csv
import importlib.util
import sys
from pathlib import Path


SCRIPT_PATH = Path(__file__).parents[2] / "metadata-preprocessing/split_pa_elevation_values.py"
SPEC = importlib.util.spec_from_file_location("split_pa_elevation_values", SCRIPT_PATH)
split_pa_elevation_values_module = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules["split_pa_elevation_values"] = split_pa_elevation_values_module
SPEC.loader.exec_module(split_pa_elevation_values_module)


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="") as file_handle:
        writer = csv.DictWriter(file_handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as file_handle:
        return list(csv.DictReader(file_handle))


def test_split_pa_elevation_values_uses_metadata_splits(tmp_path):
    values_dir = tmp_path / "values"
    metadata_dir = tmp_path / "metadata"
    values_dir.mkdir()
    metadata_dir.mkdir()
    write_csv(
        values_dir / "GLC25-PA-test-elevation.csv",
        [
            {"surveyId": "3", "Elevation": "30"},
            {"surveyId": "1", "Elevation": "10"},
            {"surveyId": "2", "Elevation": "20"},
            {"surveyId": "extra", "Elevation": "99"},
        ],
    )
    write_csv(metadata_dir / "PA_metadata_test_iid.csv", [{"surveyId": "1"}])
    write_csv(metadata_dir / "PA_metadata_test_ood.csv", [{"surveyId": "2"}, {"surveyId": "3"}])
    write_csv(
        metadata_dir / "PA_metadata_test_glc25.csv",
        [{"surveyId": "1"}, {"surveyId": "2"}, {"surveyId": "3"}],
    )

    summary = split_pa_elevation_values_module.split_pa_elevation_values(
        values_dir,
        metadata_dir,
        overwrite=True,
    )

    assert summary.iid_rows == 1
    assert summary.ood_rows == 2
    assert summary.combined_rows == 3
    assert summary.extra_input_rows == 1
    assert read_csv(values_dir / "PA-test-iid-elevation.csv") == [{"surveyId": "1", "Elevation": "10"}]
    assert read_csv(values_dir / "PA-test-ood-elevation.csv") == [
        {"surveyId": "2", "Elevation": "20"},
        {"surveyId": "3", "Elevation": "30"},
    ]
    assert read_csv(values_dir / "PA-test-glc25-elevation.csv") == [
        {"surveyId": "1", "Elevation": "10"},
        {"surveyId": "2", "Elevation": "20"},
        {"surveyId": "3", "Elevation": "30"},
    ]
