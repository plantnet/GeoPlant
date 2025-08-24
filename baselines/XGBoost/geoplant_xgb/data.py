"""Data utilities: label building, alignment, species selection, and feature grouping."""
from __future__ import annotations

from typing import Dict, List, Tuple

import pandas as pd

from .config import ExperimentConfig


def build_wide_labels_from_long_metadata(
    train_metadata_long: pd.DataFrame,
    survey_id_column: str = "surveyId",
    species_id_column: str = "speciesId",
    species_prefix: str = "sp_",
) -> pd.DataFrame:
    """Convert long-format train metadata to a wide multi-hot label table.

    Each row of the input represents an occurrence (a species present at a plot).
    The function collapses duplicates and creates a single row per `surveyId`
    with binary columns `sp_<speciesId>`.

    Args:
        train_metadata_long: DataFrame containing at least `surveyId` and `speciesId`.
        survey_id_column: Column name of the survey key (default: 'surveyId').
        species_id_column: Column name of the species identifier (default: 'speciesId').
        species_prefix: Prefix used for the wide species columns (default: 'sp_').

    Returns:
        A DataFrame with columns: [`survey_id`, `sp_<id>` ...].
    """
    required = {survey_id_column, species_id_column}
    missing = required.difference(train_metadata_long.columns)
    if missing:
        raise ValueError(f"Required columns missing in train metadata: {missing}")

    pairs = (
        train_metadata_long[[survey_id_column, species_id_column]]
        .dropna(subset=[survey_id_column, species_id_column])
        .drop_duplicates()
    )

    crosstab = pd.crosstab(pairs[survey_id_column], pairs[species_id_column]).astype(
        "int8"
    )
    crosstab.columns = [f"{species_prefix}{int(c)}" for c in crosstab.columns]
    crosstab = crosstab.reset_index().rename(columns={survey_id_column: "survey_id"})
    return crosstab


def align_features_with_labels(
    features_table: pd.DataFrame,
    labels_wide_table: pd.DataFrame,
    survey_id_column: str = "survey_id",
) -> Tuple[pd.DataFrame, pd.DataFrame, List[str]]:
    """Inner-join features with labels and return aligned tables and species column names."""
    if survey_id_column not in features_table.columns:
        raise ValueError(f"`{survey_id_column}` missing in features_table")
    if survey_id_column not in labels_wide_table.columns:
        raise ValueError(f"`{survey_id_column}` missing in labels_wide_table")

    merged = features_table.merge(labels_wide_table, on=survey_id_column, how="inner")
    species_column_names = sorted([c for c in merged.columns if c.startswith("sp_")])
    feature_columns = [c for c in features_table.columns if c != survey_id_column]

    return (
        merged[[survey_id_column] + feature_columns],
        merged[[survey_id_column] + species_column_names],
        species_column_names,
    )


def select_top_species(
    labels_wide: pd.DataFrame, species_cols: List[str], cfg: ExperimentConfig
) -> List[str]:
    """Return the most frequent species columns filtered by `min_pos_per_species` and capped at `top_species_n`."""
    freq = labels_wide[species_cols].sum(axis=0).sort_values(ascending=False)
    freq = freq[freq >= int(cfg.min_pos_per_species)]
    return list(freq.head(int(cfg.top_species_n)).index)


def split_features_by_group(
    features_df: pd.DataFrame, cfg: ExperimentConfig
) -> Dict[str, List[str]]:
    """Map feature family name → list of feature columns using `cfg.group_prefixes`."""
    group_map: Dict[str, List[str]] = {}
    for name, prefixes in cfg.group_prefixes.items():
        cols = [
            c for c in features_df.columns if any(c.startswith(p) for p in prefixes)
        ]
        group_map[name] = sorted([c for c in cols if c != cfg.sample_id_col])
    return group_map
