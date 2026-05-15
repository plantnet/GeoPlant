from __future__ import annotations

import csv
import importlib.util
import sys
from pathlib import Path


SCRIPT_PATH = Path(__file__).parents[2] / "metadata-preprocessing/split_pa_environmental_values.py"
SPEC = importlib.util.spec_from_file_location("split_pa_environmental_values", SCRIPT_PATH)
split_pa_environmental_values_module = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules["split_pa_environmental_values"] = split_pa_environmental_values_module
SPEC.loader.exec_module(split_pa_environmental_values_module)


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as file_handle:
        writer = csv.DictWriter(file_handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as file_handle:
        return list(csv.DictReader(file_handle))


def test_split_one_variable_uses_metadata_order_and_drops_unnamed_columns(tmp_path):
    values_root = tmp_path / "values"
    metadata_dir = tmp_path / "metadata"
    write_csv(
        values_root / "Landcover/GLC25-PA-test-landcover.csv",
        [
            {"": "0", "surveyId": "3", "LandCover-1": "30"},
            {"": "1", "surveyId": "1", "LandCover-1": "10"},
            {"": "2", "surveyId": "2", "LandCover-1": "20"},
            {"": "3", "surveyId": "extra", "LandCover-1": "99"},
        ],
    )
    write_csv(metadata_dir / "PA_metadata_test_iid.csv", [{"surveyId": "1"}])
    write_csv(metadata_dir / "PA_metadata_test_ood.csv", [{"surveyId": "2"}, {"surveyId": "3"}])
    write_csv(
        metadata_dir / "PA_metadata_test_glc25.csv",
        [{"surveyId": "1"}, {"surveyId": "2"}, {"surveyId": "3"}],
    )

    summary = split_pa_environmental_values_module.split_one_variable(
        values_root,
        metadata_dir,
        "landcover",
        overwrite=True,
    )

    assert summary.iid_rows == 1
    assert summary.ood_rows == 2
    assert summary.combined_rows == 3
    assert summary.extra_input_rows == 1
    assert read_csv(values_root / "Landcover/PA-test-iid-landcover.csv") == [
        {"surveyId": "1", "LandCover-1": "10"}
    ]
    assert read_csv(values_root / "Landcover/PA-test-ood-landcover.csv") == [
        {"surveyId": "2", "LandCover-1": "20"},
        {"surveyId": "3", "LandCover-1": "30"},
    ]
    assert read_csv(values_root / "Landcover/PA-test-glc25-landcover.csv") == [
        {"surveyId": "1", "LandCover-1": "10"},
        {"surveyId": "2", "LandCover-1": "20"},
        {"surveyId": "3", "LandCover-1": "30"},
    ]
