"""Experiment orchestration for MaxEnt ablations."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Dict

import numpy as np
import pandas as pd
from tqdm.auto import tqdm

from .config import ExperimentConfig
from .data import select_top_species, split_features_by_group
from .metrics import macro_auc, sample_f1_at_k, sample_recall_at_k
from .model import estimate_topk, predict_scores, train_ovr, train_richness_estimator


def _columns_for_groups(
    group_map: Dict[str, list[str]],
    selected_groups: Sequence[str],
) -> list[str]:
    columns: set[str] = set()
    for group_name in selected_groups:
        columns.update(group_map.get(group_name, []))
    return sorted(columns)


def _weighted_metrics_for_variable_topk(
    y_true: np.ndarray,
    y_scores: np.ndarray,
    topk_per_sample: np.ndarray,
) -> tuple[float, float]:
    f1_parts = []
    recall_parts = []
    weights = []
    for k_value in np.unique(topk_per_sample):
        sample_mask = topk_per_sample == k_value
        if sample_mask.sum() == 0:
            continue
        f1_parts.append(sample_f1_at_k(y_true[sample_mask], y_scores[sample_mask], int(k_value)))
        recall_parts.append(
            sample_recall_at_k(y_true[sample_mask], y_scores[sample_mask], int(k_value))
        )
        weights.append(int(sample_mask.sum()))
    if not weights:
        return float("nan"), float("nan")
    return float(np.average(f1_parts, weights=weights)), float(
        np.average(recall_parts, weights=weights)
    )


def run_one_ablation(
    experiment_config: ExperimentConfig,
    ablation_group_names: list[str],
    train_features: pd.DataFrame,
    train_labels: pd.DataFrame,
    test_features: pd.DataFrame,
    test_labels: pd.DataFrame,
    all_species_column_names: list[str],
) -> dict:
    """Run a single ablation configuration and return the resulting metrics row."""
    group_map = split_features_by_group(train_features, experiment_config)
    selected_feature_columns = _columns_for_groups(group_map, ablation_group_names)
    if not selected_feature_columns:
        raise ValueError(f"No feature columns found for groups {ablation_group_names}")

    top_species = select_top_species(train_labels, all_species_column_names, experiment_config)
    if not top_species:
        raise ValueError("No species passed the selection thresholds")

    train_feature_subset = train_features[selected_feature_columns]
    test_feature_subset = test_features[selected_feature_columns]
    train_label_subset = train_labels[
        [experiment_config.sample_id_col] + top_species
    ].set_index(experiment_config.sample_id_col)
    test_label_subset = test_labels[
        [experiment_config.sample_id_col] + top_species
    ].set_index(experiment_config.sample_id_col)

    models = train_ovr(
        train_feature_subset,
        train_label_subset,
        top_species,
        experiment_config,
    )
    scores_test = predict_scores(models, test_feature_subset, top_species)
    true_test = test_label_subset.values.astype(int)

    if experiment_config.use_richness_estimator:
        richness_clf, bin_edges, bin_to_mean = train_richness_estimator(
            train_feature_subset,
            train_label_subset,
            experiment_config,
        )
        topk_per_sample = estimate_topk(
            richness_clf,
            bin_edges,
            bin_to_mean,
            test_feature_subset,
            offset=experiment_config.richness_offset,
        )
        f1_score, recall_score = _weighted_metrics_for_variable_topk(
            true_test,
            scores_test,
            topk_per_sample,
        )
        topk_used = "per-sample"
    else:
        f1_score = sample_f1_at_k(true_test, scores_test, experiment_config.fixed_top_k)
        recall_score = sample_recall_at_k(true_test, scores_test, experiment_config.fixed_top_k)
        topk_used = experiment_config.fixed_top_k

    return {
        "groups": "+".join(ablation_group_names),
        "n_features": len(selected_feature_columns),
        "n_species": len(top_species),
        "AUC": macro_auc(true_test, scores_test),
        "Recall": recall_score,
        "Fs1": f1_score,
        "TopK": topk_used,
    }


def run_all(
    experiment_config: ExperimentConfig,
    train_features: pd.DataFrame,
    train_labels: pd.DataFrame,
    test_features: pd.DataFrame,
    test_labels: pd.DataFrame,
    species_column_names: list[str],
) -> pd.DataFrame:
    """Run all configured ablations and return a consolidated result table."""
    rows = []
    for ablation_group_names in tqdm(experiment_config.ablations, desc="Ablations"):
        rows.append(
            run_one_ablation(
                experiment_config,
                ablation_group_names,
                train_features,
                train_labels,
                test_features,
                test_labels,
                species_column_names,
            )
        )
    return pd.DataFrame(rows)
