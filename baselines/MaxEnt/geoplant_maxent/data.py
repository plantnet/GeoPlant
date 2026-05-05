"""Data utilities: label building, alignment, species selection, and feature grouping."""

from __future__ import annotations

from typing import Dict

import pandas as pd

from .config import ExperimentConfig


def build_wide_labels_from_long_metadata(
    train_metadata_long: pd.DataFrame,
    survey_id_column: str = "surveyId",
    species_id_column: str = "speciesId",
    species_prefix: str = "sp_",
) -> pd.DataFrame:
    """Convert long-format train metadata to a wide multi-hot label table."""
    required = {survey_id_column, species_id_column}
    missing = required.difference(train_metadata_long.columns)
    if missing:
        raise ValueError(f"Required columns missing in train metadata: {sorted(missing)}")
    pairs = (
        train_metadata_long[[survey_id_column, species_id_column]]
        .dropna(subset=[survey_id_column, species_id_column])
        .drop_duplicates()
    )
    crosstab = pd.crosstab(pairs[survey_id_column], pairs[species_id_column]).astype("int8")
    crosstab.columns = [f"{species_prefix}{int(column)}" for column in crosstab.columns]
    return crosstab.reset_index().rename(columns={survey_id_column: "survey_id"})


def align_features_with_labels(
    features_table: pd.DataFrame,
    labels_wide_table: pd.DataFrame,
    survey_id_column: str = "survey_id",
) -> tuple[pd.DataFrame, pd.DataFrame, list[str]]:
    """Inner-join features with labels and return aligned tables and species columns."""
    if survey_id_column not in features_table.columns:
        raise ValueError(f"`{survey_id_column}` missing in features_table")
    if survey_id_column not in labels_wide_table.columns:
        raise ValueError(f"`{survey_id_column}` missing in labels_wide_table")
    if features_table[survey_id_column].duplicated().any():
        raise ValueError("Feature rows must be unique per survey")
    if labels_wide_table[survey_id_column].duplicated().any():
        raise ValueError("Label rows must be unique per survey")

    merged = features_table.merge(labels_wide_table, on=survey_id_column, how="inner")
    species_column_names = sorted(column for column in merged.columns if column.startswith("sp_"))
    feature_columns = [column for column in features_table.columns if column != survey_id_column]
    return (
        merged[[survey_id_column] + feature_columns],
        merged[[survey_id_column] + species_column_names],
        species_column_names,
    )


def select_top_species(
    labels_wide: pd.DataFrame,
    species_cols: list[str],
    cfg: ExperimentConfig,
) -> list[str]:
    """Return frequent species filtered by the experiment thresholds."""
    frequency = labels_wide[species_cols].sum(axis=0).sort_values(ascending=False)
    frequency = frequency[frequency >= int(cfg.min_pos_per_species)]
    return list(frequency.head(int(cfg.top_species_n)).index)


def split_features_by_group(
    features_df: pd.DataFrame,
    cfg: ExperimentConfig,
) -> Dict[str, list[str]]:
    """Map feature family name to feature columns using configured prefixes."""
    group_map: Dict[str, list[str]] = {}
    for group_name, prefixes in cfg.group_prefixes.items():
        columns = [
            column
            for column in features_df.columns
            if column != cfg.sample_id_col and any(column.startswith(prefix) for prefix in prefixes)
        ]
        group_map[group_name] = sorted(columns)
    return group_map
