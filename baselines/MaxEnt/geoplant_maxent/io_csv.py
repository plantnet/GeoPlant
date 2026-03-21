"""CSV loaders and feature construction for separate train/test predictor files."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Dict

import pandas as pd

from .config import ExperimentConfig, PredictorPairSpec
from .encoding import align_one_hot, to_numeric


def _rename_alias_columns(dataframe: pd.DataFrame, aliases: dict[str, str]) -> pd.DataFrame:
    renamed = {
        source: target
        for source, target in aliases.items()
        if source in dataframe.columns and target not in dataframe.columns
    }
    return dataframe.rename(columns=renamed) if renamed else dataframe


def _require_column(dataframe: pd.DataFrame, column_name: str, csv_path: str) -> None:
    if column_name not in dataframe.columns:
        raise ValueError(f"Required column `{column_name}` missing in {csv_path}")


def _ensure_unique_ids(dataframe: pd.DataFrame, id_column: str, dataset_name: str) -> None:
    duplicated = dataframe[id_column].duplicated(keep=False)
    if duplicated.any():
        duplicate_ids = dataframe.loc[duplicated, id_column].head(5).tolist()
        raise ValueError(
            f"{dataset_name} contains duplicated `{id_column}` values: {duplicate_ids}"
        )


def _collapse_metadata_rows(
    metadata: pd.DataFrame,
    cfg: ExperimentConfig,
    dataset_name: str,
) -> pd.DataFrame:
    _require_column(metadata, cfg.source_sample_id_col, dataset_name)
    collapsed = _rename_alias_columns(metadata.copy(), cfg.metadata_aliases)
    non_label_columns = [column for column in collapsed.columns if column != cfg.species_id_col]
    collapsed = collapsed[non_label_columns].groupby(cfg.source_sample_id_col, as_index=False).first()
    _ensure_unique_ids(collapsed, cfg.source_sample_id_col, dataset_name)
    collapsed[cfg.sample_id_col] = collapsed[cfg.source_sample_id_col]
    return collapsed


def load_metadata_csv(
    csv_path: str,
    sample_id_col: str = "surveyId",
) -> pd.DataFrame:
    """Load a metadata CSV and assert that it includes the survey key column."""
    dataframe = pd.read_csv(csv_path)
    _require_column(dataframe, sample_id_col, csv_path)
    return dataframe


def _select_numeric_predictors(dataframe: pd.DataFrame, spec: PredictorPairSpec) -> pd.DataFrame:
    _require_column(dataframe, "surveyId", spec.train_path)
    numeric_columns = [
        column
        for column in dataframe.columns
        if column != "surveyId" and pd.api.types.is_numeric_dtype(dataframe[column])
    ]
    if not numeric_columns:
        raise ValueError(f"Predictor file `{spec.name}` does not contain numeric columns")
    selected = dataframe[["surveyId"] + sorted(numeric_columns)].copy()
    selected.rename(
        columns={column: f"{spec.prefix}{column}" for column in numeric_columns},
        inplace=True,
    )
    _ensure_unique_ids(selected, "surveyId", spec.name)
    return selected


def load_predictor_pairs(
    pairs: Iterable[PredictorPairSpec],
) -> tuple[Dict[str, pd.DataFrame], Dict[str, pd.DataFrame]]:
    """Load train/test predictor CSVs and prefix their numeric feature columns."""
    train_map: Dict[str, pd.DataFrame] = {}
    test_map: Dict[str, pd.DataFrame] = {}
    for spec in pairs:
        train_map[spec.name] = _select_numeric_predictors(pd.read_csv(spec.train_path), spec)
        test_map[spec.name] = _select_numeric_predictors(
            pd.read_csv(spec.test_path),
            PredictorPairSpec(
                name=spec.name,
                group=spec.group,
                prefix=spec.prefix,
                train_path=spec.test_path,
                test_path=spec.test_path,
            ),
        )
    return train_map, test_map


def build_features_from_meta_and_predictors_pair(
    experiment_config: ExperimentConfig,
    train_metadata: pd.DataFrame,
    test_metadata: pd.DataFrame,
    train_predictors_by_name: Dict[str, pd.DataFrame],
    test_predictors_by_name: Dict[str, pd.DataFrame],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Encode metadata and merge predictor families into train/test feature tables."""
    train_meta = _collapse_metadata_rows(train_metadata, experiment_config, "train metadata")
    test_meta = _collapse_metadata_rows(test_metadata, experiment_config, "test metadata")

    train_geo = to_numeric(train_meta, experiment_config.metadata_geo_columns)
    test_geo = to_numeric(test_meta, experiment_config.metadata_geo_columns)
    train_num = to_numeric(train_meta, experiment_config.metadata_numeric_columns, add_prefix="loc_")
    test_num = to_numeric(test_meta, experiment_config.metadata_numeric_columns, add_prefix="loc_")
    train_cat, test_cat = align_one_hot(
        train_meta,
        test_meta,
        experiment_config.metadata_categorical_columns,
        prefix="meta_",
    )

    train_features = pd.concat(
        [train_meta[[experiment_config.sample_id_col]], train_geo, train_num, train_cat],
        axis=1,
    )
    test_features = pd.concat(
        [test_meta[[experiment_config.sample_id_col]], test_geo, test_num, test_cat],
        axis=1,
    )

    for pair_name, train_predictors in train_predictors_by_name.items():
        if pair_name not in test_predictors_by_name:
            raise ValueError(f"Missing test predictors for `{pair_name}`")
        train_features = train_features.merge(
            train_predictors.rename(columns={"surveyId": experiment_config.sample_id_col}),
            on=experiment_config.sample_id_col,
            how="left",
        )
        test_features = test_features.merge(
            test_predictors_by_name[pair_name].rename(
                columns={"surveyId": experiment_config.sample_id_col}
            ),
            on=experiment_config.sample_id_col,
            how="left",
        )
    return train_features, test_features
