"""Experiment orchestration: single ablations or grids with metrics collection.

Public functions
----------------
run_one_ablation(...):
    Execute one ablation, training OVR models on the selected feature families,
    then evaluate Fs1/Recall@K/Macro-AUC either with a fixed Top‑K or with the
    per-sample richness estimator.

run_all(...):
    Loop over all ablation configurations listed in `ExperimentConfig.ablations`
    and return a consolidated result table.
"""
from __future__ import annotations

from typing import Dict, List, Sequence

import numpy as np
import pandas as pd
from tqdm.auto import tqdm

from .config import ExperimentConfig
from .data import select_top_species, split_features_by_group
from .metrics import macro_auc, sample_f1_at_k, sample_recall_at_k
from .model import (estimate_topk, predict_scores, train_ovr,
                    train_richness_estimator)


def _columns_for_groups(
    group_map: Dict[str, List[str]], selected_groups: Sequence[str]
) -> List[str]:
    """Return a sorted, deduplicated list of feature columns for the specified groups."""
    columns: set[str] = set()
    for group_name in selected_groups:
        columns.update(group_map.get(group_name, []))
    return sorted(columns)


def run_one_ablation(
    experiment_config: ExperimentConfig,
    ablation_group_names: List[str],
    train_features: pd.DataFrame,
    train_labels: pd.DataFrame,
    test_features: pd.DataFrame,
    test_labels: pd.DataFrame,
    all_species_column_names: List[str],
) -> Dict:
    """Run a **single** ablation configuration and return a metrics row.

    Steps:
        1) Select feature columns from `ablation_group_names`.
        2) Select most frequent species (>= min positives, top N).
        3) Train OVR models.
        4) Score the test set.
        5) Compute Fs1/Recall@K/AUC (fixed K or per-sample K).

    Args:
        experiment_config: Full configuration (schema, groups, model params).
        ablation_group_names: List of feature family names to include.
        train_features: Training feature table.
        train_labels: Training labels in wide format (`survey_id` + `sp_*` columns).
        test_features: Test feature table.
        test_labels: Test labels in wide format (or placeholder zeros).
        all_species_column_names: All species columns available (e.g., from training labels).

    Returns:
        A dictionary with keys: groups, n_features, n_species, AUC, Recall, Fs1, TopK.
    """
    feature_groups = split_features_by_group(train_features, experiment_config)
    selected_feature_columns = _columns_for_groups(feature_groups, ablation_group_names)

    train_features_subset = train_features[selected_feature_columns]
    test_features_subset = test_features[selected_feature_columns]

    top_species = select_top_species(
        train_labels, all_species_column_names, experiment_config
    )
    train_labels_top = train_labels[
        [experiment_config.sample_id_col] + top_species
    ].set_index(experiment_config.sample_id_col)
    test_labels_top = test_labels[
        [experiment_config.sample_id_col] + top_species
    ].set_index(experiment_config.sample_id_col)

    models = train_ovr(
        train_features_subset, train_labels_top, top_species, experiment_config
    )
    scores_test = predict_scores(models, test_features_subset, top_species)

    if experiment_config.use_richness_estimator:
        richness_clf, bin_edges, bin_to_mean = train_richness_estimator(
            train_features_subset, train_labels_top, experiment_config, nbins=15
        )
        topk_per_sample = estimate_topk(
            richness_clf,
            bin_edges,
            bin_to_mean,
            test_features_subset,
            offset=experiment_config.richness_offset,
        )

        true_test = test_labels_top.values.astype(int)
        f1_parts, recall_parts, weights = [], [], []
        for k_value in np.unique(topk_per_sample):
            mask = topk_per_sample == k_value
            if mask.sum() == 0:
                continue
            f1_parts.append(
                sample_f1_at_k(true_test[mask], scores_test[mask], int(k_value))
            )
            recall_parts.append(
                sample_recall_at_k(true_test[mask], scores_test[mask], int(k_value))
            )
            weights.append(int(mask.sum()))
        f1_score = (
            float(np.average(f1_parts, weights=weights)) if f1_parts else float("nan")
        )
        recall_score = (
            float(np.average(recall_parts, weights=weights))
            if recall_parts
            else float("nan")
        )
        topk_used = "per-sample"
    else:
        f1_score = sample_f1_at_k(
            test_labels_top.values.astype(int),
            scores_test,
            experiment_config.fixed_top_k,
        )
        recall_score = sample_recall_at_k(
            test_labels_top.values.astype(int),
            scores_test,
            experiment_config.fixed_top_k,
        )
        topk_used = experiment_config.fixed_top_k

    auc_score = macro_auc(test_labels_top.values.astype(int), scores_test)

    return {
        "groups": "+".join(ablation_group_names),
        "n_features": len(selected_feature_columns),
        "n_species": len(top_species),
        "AUC": auc_score,
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
    species_column_names: List[str],
) -> pd.DataFrame:
    """Run all ablations configured in `experiment_config.ablations`.

    Returns a DataFrame with one row per ablation."""
    results_rows = []
    for group_set in tqdm(experiment_config.ablations, desc="Ablations"):
        row = run_one_ablation(
            experiment_config,
            group_set,
            train_features,
            train_labels,
            test_features,
            test_labels,
            species_column_names,
        )
        results_rows.append(row)
    return pd.DataFrame(results_rows)
