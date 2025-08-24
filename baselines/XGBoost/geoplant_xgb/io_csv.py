"""CSV loaders and feature construction for separate train/test predictor files."""
from __future__ import annotations

from typing import Dict, Tuple

import pandas as pd

from .config import ExperimentConfig, PredictorPairSpec
from .encoding import one_hot, to_numeric

# Metadata schema known to the encoder
META_CATEGORICAL = ["country", "region", "taxonRank", "county", "disctrict"]
META_NUMERIC = ["geoUncertaintyInM", "areaInM2", "year"]
META_GEO = ["lat", "lon"]  # elevation handled via predictors if present


def load_metadata_csv(csv_path: str, sample_id_col: str = "surveyId") -> pd.DataFrame:
    """Load a metadata CSV and assert that it includes the survey key column.

    Args:
        csv_path: Path to CSV file.
        sample_id_col: Name of the survey key in the file (usually 'surveyId').

    Returns:
        The raw metadata DataFrame.

    Raises:
        ValueError: If the required key column is missing.
    """
    df = pd.read_csv(csv_path)
    if sample_id_col not in df.columns:
        raise ValueError(f"{sample_id_col} missing in {csv_path}")
    return df


def load_predictor_pairs(
    pairs: list[PredictorPairSpec],
) -> Tuple[Dict[str, pd.DataFrame], Dict[str, pd.DataFrame]]:
    """Load per-family TRAIN/TEST predictor CSVs and prefix numeric columns.

    For each :class:`PredictorPairSpec`, reads the train and test CSVs, keeps
    `surveyId` and all **numeric** columns, and renames numeric columns with
    the family `prefix`.

    Returns:
        Two dictionaries keyed by predictor name:
        - train_predictors_by_name[name] -> DataFrame
        - test_predictors_by_name[name]  -> DataFrame
    """

    def _prepare(df: pd.DataFrame, prefix: str) -> pd.DataFrame:
        if "surveyId" not in df.columns:
            raise ValueError("predictor CSV missing 'surveyId'")
        numeric_cols = [
            c
            for c in df.columns
            if c != "surveyId" and pd.api.types.is_numeric_dtype(df[c])
        ]
        out = df[["surveyId"] + numeric_cols].copy()
        out.rename(columns={c: f"{prefix}{c}" for c in numeric_cols}, inplace=True)
        return out

    train_map, test_map = {}, {}
    for spec in pairs:
        train_map[spec.name] = _prepare(pd.read_csv(spec.train_path), spec.prefix)
        test_map[spec.name] = _prepare(pd.read_csv(spec.test_path), spec.prefix)
    return train_map, test_map


def build_features_from_meta_and_predictors_pair(
    experiment_config: ExperimentConfig,
    train_metadata: pd.DataFrame,
    test_metadata: pd.DataFrame,
    train_predictors_by_name: Dict[str, pd.DataFrame],
    test_predictors_by_name: Dict[str, pd.DataFrame],
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Encode metadata and merge predictor families into TRAIN/TEST feature tables.

    Metadata encodings:
      - **location**: lat, lon + basic numeric meta (prefixed as 'loc_').
      - **meta**: one-hot encoded categoricals (prefixed as 'meta_').

    The output uses `experiment_config.sample_id_col` (default 'survey_id') as the
    primary key; input CSVs keep their `surveyId` which is normalized here.

    Args:
        experiment_config: Full configuration with `sample_id_col` and group prefixes.
        train_metadata: Train metadata frame containing `surveyId` (and features to encode).
        test_metadata: Test metadata frame containing `surveyId`.
        train_predictors_by_name: Dict[name -> DataFrame] with `surveyId` and prefixed numeric columns.
        test_predictors_by_name: Dict[name -> DataFrame] with `surveyId` and prefixed numeric columns.

    Returns:
        (train_features, test_features) with first column `experiment_config.sample_id_col`.
    """
    key_out = experiment_config.sample_id_col

    def _prep_meta(df: pd.DataFrame) -> pd.DataFrame:
        if "surveyId" not in df.columns:
            raise ValueError("metadata missing 'surveyId'")
        out = df.copy()
        out[key_out] = out["surveyId"]
        return out

    train_meta = _prep_meta(train_metadata)
    test_meta = _prep_meta(test_metadata)

    # Metadata encodings
    train_geo = to_numeric(train_meta, META_GEO, None)
    test_geo = to_numeric(test_meta, META_GEO, None)
    train_num = to_numeric(train_meta, META_NUMERIC, "loc_")
    test_num = to_numeric(test_meta, META_NUMERIC, "loc_")
    train_cat = one_hot(train_meta, META_CATEGORICAL, "meta_")
    test_cat = one_hot(test_meta, META_CATEGORICAL, "meta_")

    train_features = pd.concat(
        [train_meta[[key_out]], train_geo, train_num, train_cat], axis=1
    )
    test_features = pd.concat(
        [test_meta[[key_out]], test_geo, test_num, test_cat], axis=1
    )

    # Merge predictors by survey key
    for df in train_predictors_by_name.values():
        train_features = train_features.merge(
            df.rename(columns={"surveyId": key_out}), on=key_out, how="left"
        )
    for df in test_predictors_by_name.values():
        test_features = test_features.merge(
            df.rename(columns={"surveyId": key_out}), on=key_out, how="left"
        )

    return train_features, test_features
