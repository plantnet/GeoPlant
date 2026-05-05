"""Solution parsing and wide conversion utilities."""

from __future__ import annotations

import pandas as pd


def parse_solution(solution_csv_path: str) -> pd.DataFrame:
    """Read a solution-like CSV with survey and species-list columns."""
    dataframe = pd.read_csv(solution_csv_path)
    prediction_column = None
    for column in dataframe.columns:
        normalized = column.lower()
        if normalized.startswith("pred") or normalized.startswith("species"):
            prediction_column = column
            break
    if prediction_column is None:
        raise ValueError("No predictions/species column found in solution file.")
    return dataframe.rename(columns={prediction_column: "speciesList"})


def lists_to_wide(
    solution_df: pd.DataFrame,
    species_prefix: str = "sp_",
) -> tuple[pd.DataFrame, list[str]]:
    """Expand space-separated species IDs into a wide binary table."""
    all_ids: set[int] = set()
    for species_list in solution_df["speciesList"].astype(str):
        all_ids.update(int(token) for token in species_list.split() if token)

    species_columns = [f"{species_prefix}{species_id}" for species_id in sorted(all_ids)]
    wide = pd.DataFrame({"survey_id": solution_df["surveyId"].values})
    for species_column in species_columns:
        wide[species_column] = 0
    for row_index, species_list in enumerate(solution_df["speciesList"].astype(str)):
        for token in species_list.split():
            wide.at[row_index, f"{species_prefix}{int(token)}"] = 1
    return wide, species_columns
